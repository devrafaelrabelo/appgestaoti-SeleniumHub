from app.utils.selenium_engine import iniciar_driver_com_perfil, finalizar
from app.utils.ezchat_automation import login_ezchat, acessar_pagina_cadastro, cadastrar_usuario, extrair_resultado_ezchat, desativar_usuario

from fastapi import HTTPException
import time

# Configurações do usuário fixo da intranet
USUARIO = "rafaelrabelo@bemprotege.com.br"
SENHA = "Uzumymu7+++"

def cadastrar_user_ezchat(emails: list[str], setores: list[str]) -> dict:
    driver = iniciar_driver_com_perfil(remote=True, perfil="default")

    try:
        login_ezchat(driver, USUARIO, SENHA)
        time.sleep(1)

        acessar_pagina_cadastro(driver)
        cadastrar_usuario(driver, emails, setores)
        time.sleep(2)

        resultado = extrair_resultado_ezchat(driver, emails)

        # Opcional: lança HTTPException se status indicar erro
        if resultado.get("http_status", 500) >= 400:
            raise HTTPException(
                status_code=resultado.get("http_status", 500),
                detail=resultado.get("mensagem", "Erro desconhecido no EZChat")
            )

        return resultado

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Exceção inesperada ao cadastrar no EZChat: {str(e)}"
        )

    finally:
        finalizar(driver)


def desativar_users_ezchat(emails: list[str]) -> tuple[dict, int]:
    driver = iniciar_driver_com_perfil(remote=True, perfil="default")

    alterados_com_arroba = []
    alterados_sem_arroba = []
    erros = {}

    try:
        login_ezchat(driver, USUARIO, SENHA)
        time.sleep(1)
        acessar_pagina_cadastro(driver)

        for email in emails:
            try:
                resultado = desativar_usuario(driver, email)

                if resultado["status"] == "sucesso":
                    if resultado["tipo"] == "com_arroba":
                        alterados_com_arroba.append(email)
                    else:
                        alterados_sem_arroba.append(email)
                else:
                    erros[email] = resultado.get("mensagem", "Erro desconhecido")
            except Exception as e:
                erros[email] = str(e)

        status_code = 207 if erros else 200

        return {
            "status": "parcial" if status_code == 207 else "sucesso",
            "resumo": {
                "encerrarChat": alterados_com_arroba,
                "encerradosCompletos": alterados_sem_arroba,
                "erros": erros
            },
            "total_processado": len(emails),
            "total_sucesso": len(alterados_com_arroba) + len(alterados_sem_arroba),
            "total_erros": len(erros)
        }, status_code

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro geral ao desativar usuários: {str(e)}")

    finally:
        finalizar(driver)