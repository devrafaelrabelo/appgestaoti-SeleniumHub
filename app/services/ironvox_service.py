from app.config.settings import settings
from selenium.webdriver.support.ui import WebDriverWait
from app.utils.selenium_engine import iniciar_driver_com_perfil, finalizar
from app.utils.ironvox_automation import atualizar_ramal, atualizar_agente
from app.utils.conexao import testar_conexao_url
from app.schemas.ironvox_schema import IronvoxRamalItem, IronvoxAgenteItem
from selenium.webdriver.common.by import By
import time

def processar_lista_ramais(lista: list[IronvoxRamalItem]) -> list[dict]:
    resultados = []
    driver = None

    url = settings.IRONVOX_URL_RAMAL

    if not testar_conexao_url(url):
        return [{"status": "falha", "mensagem": f"Não foi possível acessar o site: {url}"}]

    try:
        print("🚀 Iniciando driver Selenium para RAMAIS...")
        driver = iniciar_driver_com_perfil(remote=True, perfil="default")
        driver.username = settings.IRONVOX_USER
        driver.password = settings.IRONVOX_PASSWORD        


        print(f"🌐 Acessando URL: {settings.IRONVOX_URL_RAMAL}")
        driver.get(settings.IRONVOX_URL_RAMAL)
        driver.maximize_window()
        time.sleep(2)

        # Login
        driver.find_element(By.ID, "usuario").send_keys(driver.username)
        driver.find_element(By.ID, "senha").send_keys(driver.password)
        driver.find_element(By.XPATH, '//input[@type="submit" and @value="Login"]').click()
        time.sleep(2)

        for item in lista:
            print(f"📞 Atualizando RAMAL {item.ramal}")
            resultado = atualizar_ramal(driver, driver, item.ramal, item.nome_usuario, item.setor)
            resultados.append({"ramal": item.ramal, **resultado})

    except Exception as e:
        print("❌ Erro ao processar ramais:", str(e))
        resultados.append({"status": "falha", "mensagem": str(e)})
    finally:
        if driver:
            finalizar(driver)

    return resultados


def processar_lista_agentes(lista: list[IronvoxAgenteItem]) -> list[dict]:
    resultados = []
    driver = None

    url = settings.IRONVOX_URL_AGENT

    if not testar_conexao_url(url):
        return [{"status": "falha", "mensagem": f"Não foi possível acessar o site: {url}"}]

    try:
        print("🚀 Iniciando driver Selenium para AGENTES...")
        driver = iniciar_driver_com_perfil(remote=True, perfil="default")
        driver.username = settings.IRONVOX_USER
        driver.password = settings.IRONVOX_PASSWORD

        print(f"🌐 Acessando URL: {settings.IRONVOX_URL_AGENT}")
        driver.get(settings.IRONVOX_URL_AGENT)
        driver.maximize_window()
        time.sleep(2)

        # Login
        driver.find_element(By.ID, "usuario").send_keys(driver.username)
        driver.find_element(By.ID, "senha").send_keys(driver.password)
        driver.find_element(By.XPATH, '//input[@type="submit" and @value="Login"]').click()
        time.sleep(2)

        for item in lista:
            print(f"👤 Atualizando AGENTE {item.ramal}")
            resultado = atualizar_agente(driver, driver, item.ramal, item.nome_usuario, item.setor)
            resultados.append({"ramal": item.ramal, **resultado})

    except Exception as e:
        print("❌ Erro ao processar agentes:", str(e))
        resultados.append({"status": "falha", "mensagem": str(e)})
    finally:
        if driver:
            finalizar(driver)

    return resultados
