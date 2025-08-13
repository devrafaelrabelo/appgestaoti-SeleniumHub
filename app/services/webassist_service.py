from app.utils.selenium_engine import iniciar_driver_com_perfil, finalizar
from app.config.settings import settings
from app.utils.conexao import testar_conexao_url
from app.utils.webassist_automation import (
    realizar_login_webassist,
    navegar_para_cadastro_webassist,
    cadastrar_usuario_webassist
)
from app.schemas.webassist_schema import WebAssistUser
from fastapi import HTTPException
import time


def cadastrar_usuarios_webassist(lista: list[WebAssistUser]) -> dict:
    driver = iniciar_driver_com_perfil(remote=True, perfil="webassit")

    try:
        url = settings.WEBASSIST_URL_LOGIN

        if not testar_conexao_url(url):
            raise HTTPException(
                status_code=503,
                detail=f"Não foi possível acessar o site: {url}"
            )
        

        print("🌐 Acessando WebAssist...")
        driver.get(url)
        time.sleep(1)
        

        print("🌐 Realizando Login WebAssist...")
        realizar_login_webassist(driver)
        time.sleep(1)


        print("🌐 Acessando tela de Cadastro WebAssist...")
        navegar_para_cadastro_webassist(driver)
        time.sleep(1)

        resultados = []
        # for usuario in lista:
        #     try:
        #         cadastrar_usuario_webassist(
        #             driver,
        #             nome=usuario.nome,
        #             email=usuario.email,
        #             login=usuario.login,
        #             situacao=usuario.situacao,
        #             cliente=usuario.cliente,
        #             perfil=usuario.perfil
        #         )
        #         resultados.append({"login": usuario.login, "status": "sucesso"})
        #         time.sleep(2)
        #     except Exception as e:
        #         resultados.append({"login": usuario.login, "status": "erro", "mensagem": str(e)})

        return {"resultado": resultados}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro inesperado ao cadastrar usuários no WebAssist: {str(e)}"
        )
    finally:
        finalizar(driver)
