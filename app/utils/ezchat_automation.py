from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from app.utils.selenium_engine import acessar_url, selecionar_opcao_autocomplete, preencher_campo_xpath, clicar_xpath
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from app.config.settings import settings

def login_ezchat(driver, usuario, senha):
    acessar_url(driver, settings.EZCHAT_LOGIN_URL)

    # Aguarda o campo de username ficar clicável e preenche
    preencher_campo_xpath(driver, '//input[@name="username"]', usuario)

    # Aguarda o campo de senha ficar clicável e preenche
    preencher_campo_xpath(driver, '//input[@name="password"]', senha)

    # Aguarda e clica no botão de login
    clicar_xpath(driver, '//button[span[text()="Log in"]]')

def acessar_pagina_cadastro(driver):
    acessar_url(driver, settings.EZCHAT_CADASTRO_USUARIO_URL )
    time.sleep(4)


def cadastrar_usuario(driver, emails, setores):
    clicar_xpath(driver, '//button[span[text()="Invite agent"]]')

    email_str = ", ".join(emails)
    preencher_campo_xpath(driver, '//input[@name="emails"]', email_str)
   
    for setor in setores:
        selecionar_opcao_autocomplete(
            driver,
            '//input[@name="categories"]',
            setor,
            setor
        )
        time.sleep(0.3)  # pequeno delay entre seleções
      
    clicar_xpath(driver, '//button[span[text()="Create"]]')
    time.sleep(2)

def extrair_resultado_ezchat(driver, emails):
    encontrados = []
    nao_encontrados = []

    try:
        # Coleta todos os e-mails visíveis na tabela
        linhas = driver.find_elements(By.XPATH, '//tr[contains(@class, "MuiTableRow-root")]')
        emails_tabela = []
        for linha in linhas:
            colunas = linha.find_elements(By.TAG_NAME, 'td')
            if colunas:
                email_tabela = colunas[0].text.strip()
                if email_tabela:
                    emails_tabela.append(email_tabela.lower())

        # Verifica se cada e-mail enviado está na tabela
        for email in emails:
            if email.lower() in emails_tabela:
                encontrados.append(email)
            else:
                nao_encontrados.append(email)

    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Erro ao verificar e-mails na tabela: {e}",
            "encontrados": [],
            "nao_encontrados": [],
            "http_status": 500
        }

    if encontrados and nao_encontrados:
        return {
            "status": "parcial",
            "mensagem": "Alguns usuários foram encontrados, outros não.",
            "encontrados": encontrados,
            "nao_encontrados": nao_encontrados,
            "http_status": 207
        }

    elif encontrados:
        return {
            "status": "sucesso",
            "mensagem": "Todos os usuários foram encontrados.",
            "encontrados": encontrados,
            "nao_encontrados": [],
            "http_status": 200
        }

    else:
        return {
            "status": "erro",
            "mensagem": "Nenhum dos e-mails foi encontrado.",
            "encontrados": [],
            "nao_encontrados": emails,
            "http_status": 400
        }
    
def desativar_usuario(driver, email: str):
    resultado = {
        "email": email,
        "status": "erro",
        "novo_nome": None,
        "tipo": None,
        "mensagem": ""
    }

    try:
        username = email.split('@')[0]

        # 1. Preencher campo de busca
        input_xpath = '//input[@id="search" and @type="search"]'
        input_element = driver.find_element(By.XPATH, input_xpath)
        input_element.click()
        input_element.clear()
        input_element.send_keys(email)
        time.sleep(0.5)

        # 2. Clicar em "Search"
        try:
            botao_search_xpath = '//button[span[text()="Search"]]'
            driver.find_element(By.XPATH, botao_search_xpath).click()
        except Exception:
            resultado["mensagem"] = "Botão Search não encontrado"
            return resultado

        time.sleep(2)

        # 3. Encontrar linha do usuário
        linha_xpath = f'//tr[.//strong[text()="{email}"]]'
        try:
            linha_element = driver.find_element(By.XPATH, linha_xpath)
        except Exception:
            resultado["mensagem"] = "Email não encontrado"
            return resultado

        colunas = linha_element.find_elements(By.TAG_NAME, "td")
        if len(colunas) < 5:
            resultado["mensagem"] = "Linha com menos de 5 colunas"
            return resultado

        valor_coluna = colunas[4].text.strip()
        valor_vinculo = int(valor_coluna) if valor_coluna.isdigit() else 0

        # 4. Editar
        botao_editar_xpath = linha_xpath + '//button[@title="Edit"]'
        driver.find_element(By.XPATH, botao_editar_xpath).click()
        time.sleep(1)

        # 5. Alterar nome
        campo_nome_xpath = '//input[@name="name"]'
        campo_nome = driver.find_element(By.XPATH, campo_nome_xpath)
        novo_nome = f"@zINATIVO - {username}" if valor_vinculo > 0 else f"zINATIVO - {username}"

        campo_nome.click()
        campo_nome.send_keys(Keys.CONTROL, 'a')
        campo_nome.send_keys(Keys.BACKSPACE)
        campo_nome.send_keys(novo_nome)
        time.sleep(0.5)

        resultado["novo_nome"] = novo_nome
        resultado["tipo"] = "com_arroba" if "@" in novo_nome else "sem_arroba"

        # 6. Clear se necessário
        if valor_vinculo == 0:
            try:
                campo_autocomplete_xpath = '//input[@name="categories"]'
                try:
                    campo_autocomplete = driver.find_element(By.XPATH, campo_autocomplete_xpath)
                    campo_autocomplete.click()
                except NoSuchElementException:
                    pass
                botao_clear_xpath = '//button[@aria-label="Clear" or @title="Clear"]'
                for botao in driver.find_elements(By.XPATH, botao_clear_xpath):
                    if botao.is_displayed():
                        botao.click()
                        time.sleep(0.5)
                        break
            except:
                pass

        # 7. Tentar salvar ou clicar fora do modal
        botoes_update = driver.find_elements(By.XPATH, '//button[span[text()="Update"]]')
        for botao in botoes_update:
            if botao.is_displayed() and botao.is_enabled():
                botao.click()
                resultado["status"] = "sucesso"
                resultado["mensagem"] = "Salvo com sucesso"
                time.sleep(1)
                return resultado

        # Clique fora se não salvou
        try:
            ActionChains(driver).move_by_offset(10, 10).click().perform()
            resultado["status"] = "sucesso"
            resultado["mensagem"] = "Modal fechado sem salvar"
            time.sleep(0.5)
            return resultado
        except:
            resultado["mensagem"] = "Erro ao fechar modal"
            return resultado

    except Exception as e:
        resultado["mensagem"] = f"Erro geral: {str(e)}"
        return resultado
    

def encerrar_em_lote(driver, lista_emails):
    alterados_com_arroba = []
    alterados_sem_arroba = []
    nao_encontrados = []

    for email in lista_emails:
        resultado = desativar_usuario(driver, email)

        if resultado["status"] == "sucesso":
            if resultado["tipo"] == "com_arroba":
                alterados_com_arroba.append((email, resultado["novo_nome"]))
            else:
                alterados_sem_arroba.append((email, resultado["novo_nome"]))
        else:
            nao_encontrados.append((email, resultado["mensagem"]))

    # Exibir resumo final
    print("\n✅ Encerramento concluído!\n")

    print("📛 Com '@zINATIVO':")
    for email, nome in alterados_com_arroba:
        print(f" - {email} => {nome}")

    print("\n🧾 Com 'zINATIVO' (sem @):")
    for email, nome in alterados_sem_arroba:
        print(f" - {email} => {nome}")

    print("\n❌ Não encontrados ou com erro:")
    for email, msg in nao_encontrados:
        print(f" - {email}: {msg}")
