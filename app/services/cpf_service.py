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
async def processar_consulta(cpf: str, data_nascimento: str) -> dict:
    loop = asyncio.get_running_loop()
    stop_evt = threading.Event()  # <- evento para cancelamento cooperativo

    tarefa_portal = asyncio.create_task(consultar_portal_transparencia(cpf))

    # PASSA o stop_evt aqui 👇
    fut_selenium = loop.run_in_executor(
        None, consultar_com_selenium, cpf, data_nascimento, stop_evt
    )

    done, pending = await asyncio.wait(
        {tarefa_portal, fut_selenium},
        return_when=asyncio.FIRST_COMPLETED
    )

    for task in done:
        resultado = task.result()
        if resultado and isinstance(resultado, dict) and resultado.get("status") == "sucesso":
            # sinaliza a outra fonte para encerrar cedo
            stop_evt.set()
            for t in pending:
                # cancelar task async; a thread vai respeitar o stop_evt
                try:
                    t.cancel()
                except Exception:
                    pass
            return resultado

    # se o primeiro não foi sucesso, tenta a outra
    for task in pending:
        try:
            stop_evt.set()  # já podemos pedir para Selenium encerrar
            return await task
        except asyncio.CancelledError:
            pass

    raise HTTPException(status_code=500, detail="Erro na consulta CPF")

