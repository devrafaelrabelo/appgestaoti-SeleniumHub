from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.utils.selenium_engine import acessar_url, preencher_campo_id, clicar_id, enviar_enter_por_id
from app.config.settings import settings

DEFAULT_TIMEOUT = 10


def login_intranet(driver, usuario, senha):
    acessar_url(driver, settings.INTRANET_LOGIN_URL)
    preencher_campo_id(driver, 'user_login', usuario)
    preencher_campo_id(driver, 'user_pass', senha)
    enviar_enter_por_id(driver, 'user_pass')


def acessar_pagina_cadastro(driver):
    acessar_url(driver, settings.INTRANET_CADASTRO_USUARIO_URL)
    WebDriverWait(driver, DEFAULT_TIMEOUT).until(
        EC.presence_of_element_located((By.ID, "createusersub"))
    )


def cadastrar_usuario(driver, nome, sobrenome, email):
    preencher_campo_id(driver, "user_login", email)
    preencher_campo_id(driver, "email", email)
    preencher_campo_id(driver, "first_name", nome)
    preencher_campo_id(driver, "last_name", sobrenome)
    clicar_id(driver, 'createusersub')


def extrair_resultado_intranet(driver):
    try:
        sucesso_div = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "message"))
        )
        if "Novo usuário criado" in sucesso_div.text:
            return {"status": "sucesso", "mensagem": "Usuário criado com sucesso."}
    except TimeoutException:
        pass

    try:
        erro_div = driver.find_element(By.CLASS_NAME, "notice.error")
        return {"status": "falha", "mensagem": erro_div.text.strip()}
    except NoSuchElementException:
        pass

    return {"status": "falha", "mensagem": "Não foi possível confirmar o resultado do cadastro."}


def marcar_checkbox_usuario(driver, email):
    try:
        email_element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((
                By.XPATH,
                f"//td[@class='email column-email' and a[text()='{email}']]"
            ))
        )
        linha_usuario = email_element.find_element(By.XPATH, "./ancestor::tr")
        checkbox = linha_usuario.find_element(By.XPATH, ".//input[@type='checkbox']")
        driver.execute_script("arguments[0].checked = true;", checkbox)
        return True
    except TimeoutException:
        return False


def acessar_pagina_usuarios(driver):
    acessar_url(driver, settings.INTRANET_LISTA_USUARIOS_URL)
    WebDriverWait(driver, DEFAULT_TIMEOUT).until(
        EC.presence_of_element_located((By.ID, "bulk-action-selector-top"))
    )


def aplicar_exclusao(driver):
    try:
        # Seleciona "Excluir"
        seletor = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "bulk-action-selector-top"))
        )
        for option in seletor.find_elements(By.TAG_NAME, "option"):
            if option.get_attribute("value") == "delete":
                option.click()
                break
        else:
            raise Exception("Opção 'Excluir' não encontrada.")

        # Clica em "Aplicar"
        aplicar_btn = driver.find_element(By.ID, "doaction")
        aplicar_btn.click()

        # Confirma exclusão, se necessário
        try:
            confirmar_btn = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.ID, "submit"))
            )
            confirmar_btn.click()
        except TimeoutException:
            pass  # Já foi direto sem tela de confirmação

    except Exception as e:
        raise Exception(f"Erro durante exclusão: {str(e)}")
