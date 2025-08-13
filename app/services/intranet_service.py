from fastapi import HTTPException
from app.utils.selenium_engine import iniciar_driver_com_perfil, finalizar
from app.utils.intranet_automation import (
    login_intranet, acessar_pagina_cadastro, cadastrar_usuario,
    extrair_resultado_intranet, acessar_pagina_usuarios,
    marcar_checkbox_usuario, aplicar_exclusao
)
import time

USUARIO = "rafaelrabelo@bemprotege.com.br"
SENHA = "Uzumymu7+++"

def dividir_nome(nome_completo: str) -> tuple[str, str]:
    partes = nome_completo.strip().split()
    primeiro_nome = partes[0]
    sobrenome = " ".join(partes[1:]) if len(partes) > 1 else ""
    return primeiro_nome, sobrenome


def cadastrar_usuario_intranet_simples(nome_completo: str, email: str) -> dict:
    primeiro_nome, sobrenome = dividir_nome(nome_completo)
    driver = iniciar_driver_com_perfil(remote=True, perfil="default")

    try:
        login_intranet(driver, USUARIO, SENHA)
        acessar_pagina_cadastro(driver)
        cadastrar_usuario(driver, primeiro_nome, sobrenome, email)
        resultado = extrair_resultado_intranet(driver)

        if resultado.get("status") != "sucesso":
            raise HTTPException(status_code=500, detail=resultado.get("mensagem", "Erro ao cadastrar na Intranet"))

        return resultado

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado na criação: {str(e)}")

    finally:
        finalizar(driver)


def apagar_usuarios_intranet_multiplos(lista_emails: list[str]) -> dict:
    driver = iniciar_driver_com_perfil(remote=True)
    log = []
    encontrou_alguem = False

    try:
        login_intranet(driver, USUARIO, SENHA)
        acessar_pagina_usuarios(driver)
        time.sleep(2)

        for email in lista_emails:
            if not isinstance(email, str):
                log.append({"email": email, "status": "inválido"})
                continue

            marcado = marcar_checkbox_usuario(driver, email)
            if marcado:
                encontrou_alguem = True
                log.append({"email": email, "status": "selecionado"})
            else:
                log.append({"email": email, "status": "não encontrado"})

        if encontrou_alguem:
            try:
                aplicar_exclusao(driver)
                log.append({"status": "exclusão realizada"})
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Erro ao excluir usuários: {str(e)}")
        else:
            log.append({"status": "nenhum usuário selecionado para exclusão"})

        return {"status": "concluído", "log": log}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro inesperado na exclusão: {str(e)}"
        )

    finally:
        finalizar(driver)
