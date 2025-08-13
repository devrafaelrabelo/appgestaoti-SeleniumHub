from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from app.utils.selenium_engine import preencher_campo_xpath, clicar_xpath


def realizar_consulta_receita(driver, cpf, data_nascimento):
    preencher_campo_xpath(driver, '//*[@id="txtCPF"]', cpf)
    preencher_campo_xpath(driver, '//*[@id="txtDataNascimento"]', data_nascimento)
    clicar_xpath(driver, '//*[@id="fieldForm"]', delay=2.5)


def clicar_capturar(driver):
    clicar_xpath(driver, '//*[@id="id_submit"]', delay=2)


def extrair_resultado(driver):
    try:
        if driver.find_elements(By.XPATH, "//h4[contains(text(), 'CPF incorreto')]"):
            return {"status": "falha", "mensagem": "CPF inválido"}

        if driver.find_elements(
            By.XPATH,
            "//div[contains(@class, 'clConteudoCentro')]"
            "//span[contains(@class, 'clConteudoCompBold')]"
            "/h4/b[contains(text(), 'Data de nascimento informada')]"
        ):
            return {"status": "falha", "mensagem": "Data de nascimento divergente"}

        nome = driver.find_element(By.XPATH, "//span[contains(text(), 'Nome:')]/b").text
        return nome  # apenas nome puro, tratado no service
    except NoSuchElementException:
        return {"status": "falha", "mensagem": "Elemento não encontrado"}
    except Exception as e:
        return {"status": "falha", "mensagem": f"Erro inesperado: {str(e)}"}
