from app.config.settings import settings
from selenium.webdriver.support.ui import WebDriverWait
from app.utils.selenium_engine import iniciar_driver_com_perfil, finalizar
from app.utils.ironvox_automation import atualizar_ramal, atualizar_agente
from app.utils.conexao import testar_conexao_url
from app.schemas.ironvox_schema import IronvoxRamalItem, IronvoxAgenteItem
from selenium.webdriver.common.by import By
from typing import Iterable, List
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
        wait = WebDriverWait(driver, 20)
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
            resultado = atualizar_ramal(driver, wait, item.ramal, item.nome_usuario, item.setor)
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
        wait = WebDriverWait(driver, 20)
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
            resultado = atualizar_agente(driver, wait,  item.ramal, item.nome_usuario, item.setor)
            resultados.append({"ramal": item.ramal, **resultado})

    except Exception as e:
        print("❌ Erro ao processar agentes:", str(e))
        resultados.append({"status": "falha", "mensagem": str(e)})
    finally:
        if driver:
            finalizar(driver)

    return resultados


def _normalizar_lista_numeros(numeros: Iterable[str | int]) -> List[str]:
    """Converte para strings, remove espaços e descarta vazios/None."""
    out: List[str] = []
    for n in numeros:
        if n is None:
            continue
        s = str(n).strip()
        if s:
            out.append(s)
    return out


def liberar_ramais_para_livre_hs(numeros: Iterable[str | int]) -> list[dict]:
    """
    Ex.: ['611', '612'] -> ['611 LIVRE HS', '612 LIVRE HS']
    """
    nums = _normalizar_lista_numeros(numeros)
    itens = [IronvoxRamalItem(ramal=n, nome_usuario="LIVRE", setor="HS") for n in nums]
    return processar_lista_ramais(itens)


def liberar_agentes_para_livre(numeros: Iterable[str | int]) -> list[dict]:
    """
    Ex.: ['611', '612'] -> ['611 LIVRE', '612 LIVRE']
    """
    nums = _normalizar_lista_numeros(numeros)
    itens = [IronvoxAgenteItem(ramal=n, nome_usuario="LIVRE", setor=None) for n in nums]
    return processar_lista_agentes(itens)


# --------------------------------------------------

from typing import Iterable, List
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time

from app.config.settings import settings
from app.utils.selenium_engine import iniciar_driver_com_perfil, finalizar
from app.utils.conexao import testar_conexao_url

# ⚠️ Importa as NOVAS funções (não as antigas)
from app.utils.ironvox_automation import set_ramal_livre_hs, set_agente_livre

def _norm_lista(numeros: Iterable[str | int]) -> List[str]:
    out: List[str] = []
    for n in numeros:
        if n is None:
            continue
        s = str(n).strip()
        if s:
            out.append(s)
    return out

def processar_lista_ramais_livre_hs(numeros: Iterable[str | int]) -> list[dict]:
    resultados: list[dict] = []
    driver = None
    url = settings.IRONVOX_URL_RAMAL

    if not testar_conexao_url(url):
        return [{"status": "falha", "mensagem": f"Não foi possível acessar o site: {url}"}]

    try:
        driver = iniciar_driver_com_perfil(remote=True, perfil="default")
        wait = WebDriverWait(driver, 20)
        driver.username = settings.IRONVOX_USER
        driver.password = settings.IRONVOX_PASSWORD

        driver.get(url)
        driver.maximize_window()
        time.sleep(2)

        # Login
        driver.find_element(By.ID, "usuario").send_keys(driver.username)
        driver.find_element(By.ID, "senha").send_keys(driver.password)
        driver.find_element(By.XPATH, '//input[@type="submit" and @value="Login"]').click()
        time.sleep(2)

        for numero in _norm_lista(numeros):
            try:
                r = set_ramal_livre_hs(driver, wait, numero, setor_padrao="HS", selecionar_pickup=True)
                resultados.append({"ramal": numero, **r})
            except Exception as e:
                resultados.append({"ramal": numero, "status": "falha", "mensagem": str(e)})

    except Exception as e:
        resultados.append({"status": "falha", "mensagem": str(e)})
    finally:
        if driver:
            finalizar(driver)

    return resultados

def processar_lista_agentes_livre(numeros: Iterable[str | int]) -> list[dict]:
    resultados: list[dict] = []
    driver = None
    url = settings.IRONVOX_URL_AGENT

    if not testar_conexao_url(url):
        return [{"status": "falha", "mensagem": f"Não foi possível acessar o site: {url}"}]

    try:
        driver = iniciar_driver_com_perfil(remote=True, perfil="default")
        wait = WebDriverWait(driver, 20)
        driver.username = settings.IRONVOX_USER
        driver.password = settings.IRONVOX_PASSWORD

        driver.get(url)
        driver.maximize_window()
        time.sleep(2)

        # Login
        driver.find_element(By.ID, "usuario").send_keys(driver.username)
        driver.find_element(By.ID, "senha").send_keys(driver.password)
        driver.find_element(By.XPATH, '//input[@type="submit" and @value="Login"]').click()
        time.sleep(2)

        for numero in _norm_lista(numeros):
            try:
                r = set_agente_livre(driver, wait, numero)
                resultados.append({"ramal": numero, **r})
            except Exception as e:
                resultados.append({"ramal": numero, "status": "falha", "mensagem": str(e)})

    except Exception as e:
        resultados.append({"status": "falha", "mensagem": str(e)})
    finally:
        if driver:
            finalizar(driver)

    return resultados
