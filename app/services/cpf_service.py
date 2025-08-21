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

    # se você usar cancelamento cooperativo, crie o stop_evt aqui e passe ao Selenium
    # stop_evt = threading.Event()

    # 1) Portal como Task (ok)
    tarefa_portal = asyncio.create_task(consultar_portal_transparencia(cpf))

    # 2) Selenium via executor (retorna concurrent.futures.Future)
    fut_selenium = loop.run_in_executor(None, consultar_com_selenium, cpf, data_nascimento)

    # 3) NÃO faça create_task de um Future. Use wrap_future OU passe direto no wait:
    # t_selenium = asyncio.wrap_future(fut_selenium)  # opção A
    # done, pending = await asyncio.wait({tarefa_portal, t_selenium}, return_when=asyncio.FIRST_COMPLETED)

    # ...ou simplesmente:
    done, pending = await asyncio.wait(
        {tarefa_portal, fut_selenium},  # opção B (direto)
        return_when=asyncio.FIRST_COMPLETED
    )

    for task in done:
        resultado = task.result()
        if resultado and isinstance(resultado, dict) and resultado.get("status") == "sucesso":
            for t in pending:
                # t.cancel() não mata a thread; se tiver stop_evt, sinalize aqui
                t.cancel()
            return resultado

    for task in pending:
        try:
            return await task  # aqui pode ser a Task async OU o Future do executor
        except asyncio.CancelledError:
            pass

    raise HTTPException(status_code=500, detail="Erro na consulta CPF")

