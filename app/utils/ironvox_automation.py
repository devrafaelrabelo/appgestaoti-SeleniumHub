from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, NoAlertPresentException
import re
import unicodedata
import time

def normalizar(s: str) -> str:
    """Remove acentos, pontuação e normaliza espaços/letras para comparar textos."""
    if not s:
        return ""
    # remove acentos
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    # caixa baixa
    s = s.lower()
    # troca qualquer coisa não alfanumérica por espaço
    s = re.sub(r"[^a-z0-9]+", " ", s)
    # trim/colapsa espaços
    s = " ".join(s.split())
    return s

def atualizar_ramal(driver, wait, ramal, nome_usuario, setor):
    try:
        campo_busca = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[ng-model="q"]')))
        campo_busca.clear()
        campo_busca.send_keys(ramal)

        xpath_ramal = f'//tr[td[2][normalize-space(text())="{ramal}"]]'
        wait.until(EC.visibility_of_element_located((By.XPATH, xpath_ramal)))
        driver.find_element(By.XPATH, f'{xpath_ramal}//a[@ng-click="updateData(e)"]').click()

        novo_callerid = f"{ramal} {nome_usuario} {setor} HS"
        campo_callerid = wait.until(EC.visibility_of_element_located((By.ID, "callerid")))
        campo_callerid.clear()
        campo_callerid.send_keys(novo_callerid)

        # Seleciona grupo do setor
        select = Select(wait.until(EC.presence_of_element_located((By.NAME, "pickupgroup"))))
        for option in select.options:
            if setor.upper() in option.text.upper():
                select.select_by_visible_text(option.text)
                break

        # Avançar etapas
        for _ in range(3):
            wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "PRÓXIMO")]'))).click()

        # Remover filas existentes
        start = time.time()
        while time.time() - start < 10:  # timeout de 10s
            filas = driver.find_elements(By.CSS_SELECTOR, "span.agentSelected")
            if not filas:
                break
            driver.execute_script("arguments[0].click();", filas[0])

        # Salvar
        wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@ng-click="insertData(ramal)"]'))).click()

         # ⬇️ 1) Se aparecer um alert(), aceite-o:
        try:
            alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
            msg = alert.text
            alert.accept()
            print(f"[IRONVOX] Alerta após salvar: {msg}")
        except TimeoutException:
            pass  # sem alert, segue

        wait.until(EC.invisibility_of_element_located((By.ID, "addExten")))

        return {"status": "sucesso"}

    except Exception as e:
        return {"status": "falha", "mensagem": str(e)}


def atualizar_agente(driver, wait, ramal, nome_usuario, setor):
    try:
        campo_busca = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[ng-model="q"]')))
        campo_busca.clear()
        campo_busca.send_keys(ramal)

        xpath = f'//tr[td[2][normalize-space(text())="{ramal}"]]'
        wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
        driver.find_element(By.XPATH, f'{xpath}//a[@ng-click="updateData(a)"]').click()

        campo_nome = wait.until(EC.visibility_of_element_located((By.NAME, "agentName")))
        campo_nome.clear()
        campo_nome.send_keys(f"{ramal} {nome_usuario}")

        # Avançar etapas
        for _ in range(2):
            wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@ng-click="next()"]'))).click()

        # Remover filas existentes
        for span in driver.find_elements(By.CSS_SELECTOR, "span.agentSelected"):
            driver.execute_script("arguments[0].click();", span)

        # Selecionar setor
        setor_normalizado = normalizar(setor)
        for span in driver.find_elements(By.XPATH, "//li[contains(@class, 'list-group-item')]/span[@class='ng-binding']"):
            if normalizar(span.text) == setor_normalizado:
                driver.execute_script("arguments[0].click();", span)
                break

        # Ajustar prioridade do setor selecionado
        for item in driver.find_elements(By.CSS_SELECTOR, "li.list-group-item"):
            try:
                span = item.find_element(By.CSS_SELECTOR, "span.agentSelected")
                if normalizar(span.text) == setor_normalizado:
                    select = Select(item.find_element(By.NAME, "agentPriority"))
                    if select.first_selected_option.get_attribute("value") != "1":
                        select.select_by_value("1")
                    break
            except:
                continue

        # Salvar
        wait.until(EC.element_to_be_clickable((
            By.XPATH, "//button[@type='submit' and contains(., 'Atualizar Agente')]"
        ))).click()

         # ⬇️ 1) Se aparecer um alert(), aceite-o:
        try:
            alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
            msg = alert.text
            alert.accept()
            print(f"[IRONVOX] Alerta após salvar: {msg}")
        except TimeoutException:
            pass  # sem alert, segue

        # ⬇️ 2) Aguarde a modal/loader sumir (ajuste o seletor conforme sua tela)
        wait.until(EC.invisibility_of_element_located((By.ID, "addExten")))

        return {"status": "sucesso"}

    except Exception as e:
        return {"status": "falha", "mensagem": str(e)}


def close_alert_if_any(driver, timeout=5):
    """Fecha o alert se existir e retorna a mensagem."""
    try:
        alert = WebDriverWait(driver, timeout).until(EC.alert_is_present())
        msg = alert.text
        alert.accept()
        print(f"[IRONVOX] Alert fechado: {msg}")
        return msg
    except (TimeoutException, NoAlertPresentException):
        return None

def run_with_alert_guard(driver, fn, *args, **kwargs):
    """Executa uma ação e, se aparecer UnexpectedAlert, fecha o alert e tenta 1 vez de novo."""
    try:
        return fn(*args, **kwargs)
    except UnexpectedAlertPresentException:
        close_alert_if_any(driver, timeout=5)
        return fn(*args, **kwargs)
    

# ---------------------------------------------

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.common.exceptions import TimeoutException, NoAlertPresentException
import re, unicodedata, time

# Helpers locais (sem alterar os existentes)
def _normalizar(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())

def _click_js(driver, elem):
    driver.execute_script("arguments[0].click();", elem)

def _close_alert_if_any(driver, timeout=5):
    try:
        alert = WebDriverWait(driver, timeout).until(EC.alert_is_present())
        msg = alert.text
        alert.accept()
        return msg
    except (TimeoutException, NoAlertPresentException):
        return None

def _wait_back_to_list(wait, locator=(By.CSS_SELECTOR, 'input[ng-model="q"]'), timeout=20):
    WebDriverWait(wait._driver, timeout).until(EC.visibility_of_element_located(locator))

# ==========================
# RAMAL → "LIVRE HS"
# ==========================
def set_ramal_livre_hs(driver, wait: WebDriverWait, ramal: str, setor_padrao: str = "HS", selecionar_pickup: bool = True):
    """
    NÃO altera a função original.
    Atualiza o ramal para: "<ramal> LIVRE HS"
    Remove filas e (opcional) seleciona pickup group do setor.
    """
    # 1) Buscar e editar
    campo_busca = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[ng-model="q"]')))
    campo_busca.clear()
    campo_busca.send_keys(ramal)

    xpath_ramal = f'//tr[td[2][normalize-space(text())="{ramal}"]]'
    row = wait.until(EC.visibility_of_element_located((By.XPATH, xpath_ramal)))
    editar = row.find_element(By.XPATH, './/a[@ng-click="updateData(e)"]')
    _click_js(driver, editar)

    # 2) CallerID: "<ramal> LIVRE HS"
    callerid = f"{ramal} LIVRE {setor_padrao}".strip()
    callerid = re.sub(r"\b(HS)(\s+\1)+\b", r"\1", callerid, flags=re.IGNORECASE)

    campo_callerid = wait.until(EC.visibility_of_element_located((By.ID, "callerid")))
    campo_callerid.clear()
    campo_callerid.send_keys(callerid)

    # 3) (Opcional) selecionar pickup group do setor
    if selecionar_pickup and setor_padrao:
        try:
            select = Select(wait.until(EC.presence_of_element_located((By.NAME, "pickupgroup"))))
            alvo = setor_padrao.upper()
            for opt in select.options:
                if alvo in opt.text.upper():
                    select.select_by_visible_text(opt.text)
                    break
        except Exception:
            pass  # se não encontrar, segue o jogo

    # 4) Avançar etapas (3x)
    for _ in range(3):
        btn = wait.until(EC.element_to_be_clickable((
            By.XPATH, '//button[contains(translate(., "óÔÕÔÓ", "oOOOO"), "PROXIMO")]'
        )))
        _click_js(driver, btn)

    # 5) Remover filas existentes (timeout ~12s)
    start = time.time()
    while time.time() - start < 12:
        filas = driver.find_elements(By.CSS_SELECTOR, "span.agentSelected")
        if not filas:
            break
        _click_js(driver, filas[0])

    # 6) Salvar
    btn_salvar = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@ng-click="insertData(ramal)"]')))
    _click_js(driver, btn_salvar)
    _close_alert_if_any(driver, timeout=5)

    # 7) Voltar à lista
    _wait_back_to_list(wait)

    return {"status": "sucesso", "novo_callerid": callerid}

# ==========================
# AGENTE → "LIVRE"
# ==========================
def set_agente_livre(driver, wait: WebDriverWait, ramal: str):
    """
    NÃO altera a função original.
    Atualiza o agente para: "<ramal> LIVRE"
    Remove filas e NÃO adiciona setor/queue.
    """
    # 1) Buscar e editar
    campo_busca = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[ng-model="q"]')))
    campo_busca.clear()
    campo_busca.send_keys(ramal)

    xpath = f'//tr[td[2][normalize-space(text())="{ramal}"]]'
    row = wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
    editar = row.find_element(By.XPATH, './/a[@ng-click="updateData(a)"]')
    _click_js(driver, editar)

    # 2) Nome do agente: "<ramal> LIVRE"
    nome_final = f"{ramal} LIVRE"
    campo_nome = wait.until(EC.visibility_of_element_located((By.NAME, "agentName")))
    campo_nome.clear()
    campo_nome.send_keys(nome_final)

    # 3) Avançar etapas (2x)
    for _ in range(2):
        btn_next = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@ng-click="next()"]')))
        _click_js(driver, btn_next)

    # 4) Remover filas existentes (sem adicionar nenhuma)
    start = time.time()
    while time.time() - start < 12:
        spans = driver.find_elements(By.CSS_SELECTOR, "span.agentSelected")
        if not spans:
            break
        _click_js(driver, spans[0])

    # 5) Salvar
    save_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//button[@type='submit' and contains(., 'Atualizar Agente')]"
    )))
    _click_js(driver, save_btn)
    _close_alert_if_any(driver, timeout=5)

    # 6) Voltar à lista
    _wait_back_to_list(wait)

    return {"status": "sucesso", "novo_nome": nome_final}
