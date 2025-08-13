import asyncio
import requests
from concurrent.futures import ThreadPoolExecutor
from fastapi import HTTPException
from time import sleep

from app.config.settings import settings
from app.utils.selenium_engine import iniciar_driver_com_perfil, finalizar
from app.utils.cpf_automation import realizar_consulta_receita, clicar_capturar, extrair_resultado


def consultar_com_selenium(cpf: str, data_nascimento: str) -> dict:
    driver = None
    try:
        driver = iniciar_driver_com_perfil(remote=True, perfil="cpf")
        driver.get(settings.URL_CONSULTA_CPF)

        realizar_consulta_receita(driver, cpf, data_nascimento)
        sleep(2)
        clicar_capturar(driver)
        resultado = extrair_resultado(driver)

        if isinstance(resultado, dict):
            return resultado
        elif isinstance(resultado, str):
            return {"status": "sucesso", "nome": resultado}
        else:
            return {"status": "falha", "mensagem": "Formato de retorno inesperado"}

    except Exception as e:
        return {"status": "falha", "mensagem": str(e)}
    finally:
        if driver:
            finalizar(driver)


async def consultar_portal_transparencia(cpf: str) -> dict:
    try:
        headers = {
            "chave-api-dados": settings.API_PORTAL_KEY,
            "Accept": "application/json"
        }
        params = {"cpf": cpf}
        response = requests.get(settings.API_PORTAL_URL, headers=headers, params=params, timeout=5)

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0 and "nome" in data[0]:
                return {"status": "sucesso", "nome": data[0]["nome"]}
            elif isinstance(data, dict) and "nome" in data:
                return {"status": "sucesso", "nome": data["nome"]}
    except Exception:
        pass
    return None


async def processar_consulta(cpf: str, data_nascimento: str) -> dict:
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        tarefa_selenium = loop.run_in_executor(executor, consultar_com_selenium, cpf, data_nascimento)
        tarefa_portal = asyncio.create_task(consultar_portal_transparencia(cpf)) 

        done, pending = await asyncio.wait(
            [tarefa_portal, tarefa_selenium],
            return_when=asyncio.FIRST_COMPLETED)

        for task in done:
            resultado = task.result()
            if resultado and resultado.get("status") == "sucesso":
                for t in pending:
                    t.cancel()
                return resultado

        for task in pending:
            try:
                return await task
            except asyncio.CancelledError:
                pass

    raise HTTPException(status_code=500, detail="Erro na consulta CPF")
