from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time

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
