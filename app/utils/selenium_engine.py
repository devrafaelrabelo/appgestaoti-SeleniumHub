import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.config.settings import settings


def iniciar_driver_com_perfil(remote=True, perfil="default"):
    chrome_options = Options()

    if perfil == "cpf":
        chrome_options.add_argument('--user-data-dir=/home/seluser/chrome-profile')
        chrome_options.add_argument('--profile-directory=Default')

    if perfil == "webassit":
        chrome_options.add_argument('--user-data-dir=/home/seluser/chrome-profile')
        chrome_options.add_argument('--profile-directory=Zerado')
        chrome_options.add_argument('--lang=pt-BR')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--no-default-browser-check')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument("--password-store=basic")
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')

        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        # chrome_options.add_argument("--disable-extensions")
        # chrome_options.add_argument("--headless=new")
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--disable-dev-shm-usage')
        # chrome_options.add_argument('--window-size=800x600')
        # chrome_options.add_argument('--disable-background-networking')
        # chrome_options.add_argument('--disable-sync')
        # chrome_options.add_argument('--disable-default-apps')
        # chrome_options.add_argument('--disable-notifications')
        # chrome_options.add_argument('--disable-popup-blocking')
        # chrome_options.add_argument('--mute-audio')
        # chrome_options.add_argument('--disable-translate')
        # chrome_options.add_argument('--disable-infobars')
        # chrome_options.add_argument('--disable-features=TranslateUI')
        # chrome_options.add_argument('--disable-software-rasterizer')
        # chrome_options.add_argument('--disable-background-timer-throttling')
        # chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        # chrome_options.add_argument('--no-first-run')
        # chrome_options.add_argument('--no-default-browser-check')
        # chrome_options.add_argument('--disk-cache-size=0')
        # chrome_options.add_argument('--media-cache-size=0')
        # chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        # chrome_options.add_argument('--remote-debugging-port=9222')
        # chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        # chrome_options.add_argument('--single-process')
        # chrome_options.add_argument('--no-zygote')
        # chrome_options.add_argument("--incognito")
        

    if remote:
        return webdriver.Remote(command_executor=settings.REMOTE_SELENIUM_URL, options=chrome_options, keep_alive=True)
    else:
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def acessar_url(driver, url):
    driver.get(url)
    WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')

def preencher_campo_xpath(driver, xpath, valor, delay=0.7):
    try:
        campo = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        campo.click()
        time.sleep(delay)
        campo.send_keys(valor)
    except (NoSuchElementException, TimeoutException):
        raise Exception(f"[ERRO] Campo não encontrado ou não interagível: {xpath}")

def preencher_campo_id(driver, campo_id, valor, delay=0.4):
    try:
        campo = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, campo_id)))
        campo.click()
        time.sleep(delay)
        campo.send_keys(valor)
    except NoSuchElementException:
        raise Exception(f"Campo não encontrado: {campo_id}")

def clicar_xpath(driver, xpath, delay=0.7):
    try:
        botao = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        botao.click()
        time.sleep(delay)
    except (NoSuchElementException, TimeoutException):
        raise Exception(f"[ERRO] Botão não encontrado ou não clicável: {xpath}")

def clicar_id(driver, id_, delay=0.7):
    try:
        botao = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, id_)))
        botao.click()
        time.sleep(delay)
    except NoSuchElementException:
        raise Exception(f"Botão não encontrado: {id_}")

def enviar_enter_por_id(driver, id_):
    try:
        campo = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, id_)))
        campo.send_keys(Keys.ENTER)
    except NoSuchElementException:
        raise Exception(f"Campo não encontrado para ENTER: {id_}")
    
def selecionar_opcao_autocomplete(driver, campo_xpath, texto_digitado, texto_opcao):
    # 1. Localiza e digita no campo
    campo = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, campo_xpath))
    )
    campo.click()
    campo.clear()
    campo.send_keys(texto_digitado)

    # 2. Aguarda a lista aparecer e seleciona pelo texto da opção
    xpath_opcao = f'//li[contains(@id, "-option-") and normalize-space()="{texto_opcao}"]'
    opcao = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, xpath_opcao))
    )
    opcao.click()
    time.sleep(0.5)

def finalizar(driver):
    try:
        driver.quit()
    except Exception as e:
        print(f"Erro ao finalizar o driver: {e}")

def selecionar_combo_xpath(driver, xpath: str, valor_visivel: str):
    """Seleciona uma opção em um <select> usando o texto visível"""
    select_element = driver.find_element(By.XPATH, xpath)
    select = Select(select_element)
    select.select_by_visible_text(valor_visivel)