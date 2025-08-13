def atualizar_ramal(driver, wait, ramal, nome_usuario, setor):
    try:
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[ng-model="q"]'))).clear()
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[ng-model="q"]'))).send_keys(ramal)
        xpath_ramal = f'//tr[td[2][normalize-space(text())="{ramal}"]]'
        wait.until(EC.visibility_of_element_located((By.XPATH, xpath_ramal)))
        driver.find_element(By.XPATH, f'{xpath_ramal}//a[@ng-click="updateData(e)"]').click()

        novo_callerid = f"{ramal} {nome_usuario} {setor} HS"
        wait.until(EC.visibility_of_element_located((By.ID, "callerid"))).clear()
        driver.find_element(By.ID, "callerid").send_keys(novo_callerid)

        select = Select(driver.find_element(By.NAME, "pickupgroup"))
        for option in select.options:
            if setor.upper() in option.text.upper():
                select.select_by_visible_text(option.text)
                break

        for _ in range(3):
            wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "PRÓXIMO")]'))).click()
            time.sleep(0.5)

        while True:
            filas = driver.find_elements(By.CSS_SELECTOR, "span.agentSelected")
            if not filas:
                break
            driver.execute_script("arguments[0].click();", filas[0])
            time.sleep(0.2)
            driver.execute_script("arguments[0].click();", filas[0])

        driver.find_element(By.XPATH, '//button[@ng-click="insertData(ramal)"]').click()
        wait.until(EC.invisibility_of_element_located((By.ID, "addExten")))

        return {"status": "sucesso"}

    except Exception as e:
        return {"status": "falha", "mensagem": str(e)}


def atualizar_agente(driver, wait, ramal, nome_usuario, setor):
    try:
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[ng-model="q"]'))).clear()
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[ng-model="q"]'))).send_keys(ramal)
        xpath = f'//tr[td[2][normalize-space(text())="{ramal}"]]'
        wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
        driver.find_element(By.XPATH, f'{xpath}//a[@ng-click="updateData(a)"]').click()

        wait.until(EC.visibility_of_element_located((By.NAME, "agentName"))).clear()
        driver.find_element(By.NAME, "agentName").send_keys(f"{ramal} {nome_usuario}")

        for _ in range(2):
            wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@ng-click="next()"]'))).click()
            time.sleep(0.2)

        for span in driver.find_elements(By.CSS_SELECTOR, "span.agentSelected"):
            driver.execute_script("arguments[0].click();", span)
            time.sleep(0.2)
            driver.execute_script("arguments[0].click();", span)

        setor_normalizado = normalizar(setor)
        for span in driver.find_elements(By.XPATH, "//li[contains(@class, 'list-group-item')]/span[@class='ng-binding']"):
            if normalizar(span.text) == setor_normalizado:
                driver.execute_script("arguments[0].click();", span)
                break

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

        wait.until(EC.element_to_be_clickable((
            By.XPATH, "//button[@type='submit' and contains(., 'Atualizar Agente')]"
        ))).click()

        return {"status": "sucesso"}

    except Exception as e:
        return {"status": "falha", "mensagem": str(e)}
