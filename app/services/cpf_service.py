# app/services/cpf_service.py
import asyncio
import threading
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

import httpx

from app.config.settings import settings
from app.utils.selenium_engine import iniciar_driver_com_perfil, finalizar
from app.utils.cpf_automation import realizar_consulta_receita, clicar_capturar, extrair_resultado

# Executor global para reutilização
_EXECUTOR = ThreadPoolExecutor(max_workers=2)

DEFAULT_TIMEOUT = 60  # segundos

# ----------------------------
# Fonte 1: Selenium (thread)
# ----------------------------
def consultar_com_selenium(cpf: str, data_nascimento: str, stop_evt: threading.Event) -> Dict[str, Any]:
    driver = None
    try:
        if stop_evt.is_set():
            return {"status": "falha", "mensagem": "Cancelado antes de iniciar"}

        driver = iniciar_driver_com_perfil(remote=True, perfil="cpf")
        driver.get(settings.URL_CONSULTA_CPF)

        if stop_evt.is_set():
            return {"status": "falha", "mensagem": "Cancelado"}

        realizar_consulta_receita(driver, cpf, data_nascimento)

        # Pontos de checagem de cancelamento entre passos
        if stop_evt.is_set():
            return {"status": "falha", "mensagem": "Cancelado"}

        clicar_capturar(driver)

        if stop_evt.is_set():
            return {"status": "falha", "mensagem": "Cancelado"}

        resultado = extrair_resultado(driver)

        if isinstance(resultado, dict):
            return resultado
        elif isinstance(resultado, str):
            return {"status": "sucesso", "nome": resultado}
        else:
            return {"status": "falha", "mensagem": "Formato de retorno inesperado"}

    except Exception as e:
        return {"status": "falha", "mensagem": f"Erro Selenium: {e}"}
    finally:
        if driver:
            try:
                finalizar(driver)
            except Exception:
                pass

# ----------------------------
# Fonte 2: Portal Transparência (HTTP async)
# ----------------------------
async def consultar_portal_transparencia(cpf: str) -> Dict[str, Any]:
    headers = {
        "chave-api-dados": settings.API_PORTAL_KEY,
        "Accept": "application/json",
    }
    params = {"cpf": cpf}

    timeout = httpx.Timeout(5.0)  # timeout curto só para essa fonte
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            resp = await client.get(settings.API_PORTAL_URL, headers=headers, params=params)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and data and isinstance(data[0], dict) and "nome" in data[0]:
                    return {"status": "sucesso", "nome": data[0]["nome"]}
                if isinstance(data, dict) and "nome" in data:
                    return {"status": "sucesso", "nome": data["nome"]}
                return {"status": "falha", "mensagem": "Resposta sem campo 'nome'"}
            else:
                return {"status": "falha", "mensagem": f"HTTP {resp.status_code} no Portal"}
        except httpx.RequestError as e:
            return {"status": "falha", "mensagem": f"Erro de rede: {e}"}
        except Exception as e:
            return {"status": "falha", "mensagem": f"Erro Portal: {e}"}

# ----------------------------
# Orquestração: corrida com fallback
# ----------------------------
async def processar_consulta(cpf: str, data_nascimento: str, timeout_total: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """
    Disputa entre Portal (async) e Selenium (thread):
      - Retorna o primeiro 'sucesso'
      - Se o primeiro concluir com falha, tenta a outra fonte dentro de 'timeout_total'
      - Cancela o Selenium cooperativamente via stop_evt
      - Nunca levanta HTTPException (o controller decide)
    """
    loop = asyncio.get_running_loop()
    stop_evt = threading.Event()

    # Cria as tarefas
    t_portal = asyncio.create_task(consultar_portal_transparencia(cpf))
    fut_selenium = loop.run_in_executor(_EXECUTOR, consultar_com_selenium, cpf, data_nascimento, stop_evt)

    # Empacota o future do executor em Task para tratamento uniforme
    t_selenium = asyncio.create_task(asyncio.wrap_future(asyncio.ensure_future(fut_selenium)))

    try:
        done, pending = await asyncio.wait(
            {t_portal, t_selenium},
            timeout=timeout_total,
            return_when=asyncio.FIRST_COMPLETED,
        )

        if not done:
            # Ninguém terminou no tempo
            stop_evt.set()
            for t in pending:
                t.cancel()
            return {"status": "falha", "mensagem": "Tempo excedido na consulta"}

        # Primeiro que terminou
        first = next(iter(done))
        try:
            first_result = await _safe_result(first)
        except asyncio.CancelledError:
            first_result = {"status": "falha", "mensagem": "Cancelado"}

        if first_result.get("status") == "sucesso":
            # Cancela a outra fonte
            stop_evt.set()
            for t in pending:
                t.cancel()
            return first_result

        # Não teve sucesso — tenta a outra se ainda estiver pendente
        other = next(iter(pending), None)
        if other:
            stop_evt.set()  # sinaliza Selenium parar cedo se ele for o "other"
            try:
                other_result = await asyncio.wait_for(_safe_result(other), timeout=timeout_total)
            except asyncio.TimeoutError:
                return {"status": "falha", "mensagem": "Tempo excedido aguardando método alternativo"}
            except asyncio.CancelledError:
                return {"status": "falha", "mensagem": "Consulta cancelada"}

            if other_result.get("status") == "sucesso":
                return other_result
            return other_result  # falha padronizada da segunda fonte

        # Só o primeiro concluiu (com falha)
        return first_result

    finally:
        stop_evt.set()
        for t in (t_portal, t_selenium):
            if not t.done():
                t.cancel()

async def _safe_result(task: asyncio.Task) -> Dict[str, Any]:
    try:
        result = await task
        # Garante dict padrão
        if not isinstance(result, dict):
            return {"status": "falha", "mensagem": "Retorno inesperado"}
        return result
    except Exception as e:
        return {"status": "falha", "mensagem": f"Erro: {e}"}
