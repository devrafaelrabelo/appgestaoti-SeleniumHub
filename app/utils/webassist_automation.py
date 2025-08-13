from app.utils.selenium_engine import preencher_campo_xpath, clicar_xpath, selecionar_combo_xpath
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException, TimeoutException, NoSuchElementException, InvalidSessionIdException

from app.config.settings import settings
import time
import random
from selenium.webdriver.common.action_chains import ActionChains

def digitar_como_humano(elemento, texto, delay=0.3):
    for letra in texto:
        elemento.send_keys(letra)
        time.sleep(random.uniform(delay * 0.8, delay * 1.2))

# def realizar_login_webassist(driver):
    try:
        print("👤 Preenchendo usuário e senha como humano...")

        campo_login = driver.find_element(By.XPATH, '//*[@id="edtLogin"]')
        campo_senha = driver.find_element(By.XPATH, '//*[@id="edtSenha"]')

        digitar_como_humano(campo_login, settings.WEBASSIST_USER)
        time.sleep(0.5)
        digitar_como_humano(campo_senha, settings.WEBASSIST_PASSWORD)

        print("➡️ Clicando no botão de login com simulação humana...")
        botao_login = driver.find_element(By.XPATH, '//*[@class="btn btn-logon btn-block"]')

        actions = ActionChains(driver)
        actions.move_to_element_with_offset(botao_login, random.randint(-2, 2), random.randint(-2, 2))
        actions.pause(random.uniform(0.3, 0.7))
        actions.click()
        actions.perform()

        print("⏳ Verificando se alerta aparece...")
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            print(f"⚠️ Alerta encontrado: {alert.text}")
            alert.accept()
            print("✅ Alerta fechado com sucesso.")
        except NoAlertPresentException:
            print("✅ Nenhum alerta detectado.")
        except InvalidSessionIdException:
            print("❌ Sessão foi perdida ou navegador foi fechado.")
            return False
        except Exception as e:
            print(f"⚠️ Erro ao tratar alerta: {e}")

        print("✅ Conectado com sucesso")
        time.sleep(30)

    except (NoSuchElementException, TimeoutException) as e:
        print(f"❌ Erro ao localizar elemento na página: {e}")
    except InvalidSessionIdException:
        print("❌ Sessão do navegador inválida. Reabra o driver.")
    except Exception as e:
        print(f"❌ Erro inesperado durante login: {e}")

def realizar_login_webassist(driver):
    try:
        print("🔎 Aguardando campos de login estarem prontos...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "edtLogin")))

        campo_login = driver.find_element(By.ID, "edtLogin")
        campo_senha = driver.find_element(By.ID, "edtSenha")

        print("👤 Digitando login de forma humana...")
        digitar_como_humano(campo_login, settings.WEBASSIST_USER, delay=0.25)
        time.sleep(random.uniform(0.5, 1.2))
        digitar_como_humano(campo_senha, settings.WEBASSIST_PASSWORD, delay=0.25)

        print("🖱️ Clicando no botão de login com movimento natural...")
        botao_login = driver.find_element(By.CLASS_NAME, "btn-logon")

        actions = ActionChains(driver)
        actions.move_to_element_with_offset(botao_login, random.randint(-3, 3), random.randint(-2, 2))
        actions.pause(random.uniform(0.3, 0.8))
        actions.click()
        actions.perform()

        print("⏳ Aguardando possível alerta...")
        try:
            WebDriverWait(driver, 4).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            print(f"⚠️ Alerta detectado: {alert.text}")
            alert.accept()
            print("✅ Alerta fechado.")
        except NoAlertPresentException:
            print("✅ Nenhum alerta visível.")
        except InvalidSessionIdException:
            print("❌ Sessão perdida. Driver foi fechado.")
            return False
        except Exception as e:
            print(f"⚠️ Erro ao lidar com alerta: {e}")

        print("✅ Login finalizado. Aguardando interação/captcha manual...")
        time.sleep(30)

    except (NoSuchElementException, TimeoutException) as e:
        print(f"❌ Erro ao encontrar elemento: {e}")
    except InvalidSessionIdException:
        print("❌ Sessão do navegador inválida.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def navegar_para_cadastro_webassist(driver):
    driver.get(settings.WEBASSIST_URL_CADASTRO)
    time.sleep(2)
    print("🧭 Navegando até o menu de cadastro de usuários...")

def cadastrar_usuario_webassist(driver, nome: str, email: str, login: str, situacao: str, cliente: str, perfil: str):
    print(f"📝 Cadastrando usuário: {login}")

    wait = WebDriverWait(driver, 15)

    preencher_campo_xpath(driver, '//*[@id="edtNome"]', nome)
    preencher_campo_xpath(driver, '//*[@id="edtEmail"]', email)
    preencher_campo_xpath(driver, '//*[@id="edtLogin"]', login)

    # Seleciona cliente no select2 "cmbCliente"
    try:
        combo_cliente = wait.until(EC.presence_of_element_located((By.ID, "cmbCliente")))
        Select(combo_cliente).select_by_visible_text(cliente)
        print(f"🏢 Cliente selecionado: {cliente}")
    except Exception as e:
        raise Exception(f"Erro ao selecionar cliente '{cliente}': {e}")

    # Aguarda carregamento do perfil após o cliente
    try:
        wait.until(lambda d: len(Select(d.find_element(By.ID, "cmbPerfil")).options) > 1)
    except:
        raise Exception("Perfis não carregados após seleção do cliente.")

    # Seleciona perfil
    try:
        combo_perfil = driver.find_element(By.ID, "cmbPerfil")
        Select(combo_perfil).select_by_visible_text(perfil)
        print(f"👤 Perfil selecionado: {perfil}")
    except Exception as e:
        raise Exception(f"Erro ao selecionar perfil '{perfil}': {e}")

    # Situação: Ativo / Inativo
    try:
        combo_situacao = driver.find_element(By.ID, "cmbSituacao")
        Select(combo_situacao).select_by_value(situacao)  # 'A' ou 'I'
        print(f"📌 Situação definida: {situacao}")
    except Exception as e:
        raise Exception(f"Erro ao selecionar situação '{situacao}': {e}")

    # Salvar
    # clicar_xpath(driver, '//*[@id="btnSalvar"]', delay=2)
    time.sleep(30)
    print(f"✅ Usuário {login} cadastrado com sucesso.")
