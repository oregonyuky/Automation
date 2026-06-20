from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
from editar import acessar_editar
from adicionarRecurso import abrir_adicionar_recurso
from gravarExcel import gravar_sem_email_excel
import os
import time
import re

def agendamentoaulaaovivo():
    load_dotenv()
    browser = webdriver.Chrome()
    browser.get("https://www.unoeste.br/AVA")
    browser.maximize_window()
    ra = os.getenv("UNOESTE_RA")
    senha = os.getenv("UNOESTE_SENHA")
    wait = WebDriverWait(browser, 20)
    campo_ra = wait.until(EC.presence_of_element_located( (By.ID, "tbLogin")))
    campo_senha = wait.until( EC.presence_of_element_located( (By.ID, "tbSenha")))
    botao_login = wait.until( EC.element_to_be_clickable( (By.ID, "bAutenticar")))
    campo_ra.clear()
    campo_ra.send_keys(ra)
    campo_senha.clear()
    campo_senha.send_keys(senha)
    botao_login.click()
    wait.until( EC.presence_of_element_located( (By.TAG_NAME, "body")))
    browser.get( "https://www.unoeste.br/sistemas/agendamentoaulaaovivo/agendamentos#")
    wait.until( lambda driver: driver.execute_script("return document.readyState") == "complete")
    input_periodo = wait.until( EC.element_to_be_clickable( (By.ID, "inputPeriodo")))
    input_periodo.click()
    input_periodo.send_keys(Keys.CONTROL, "a")
    input_periodo.send_keys(Keys.DELETE)
    browser.execute_script("""
    arguments[0].value = arguments[1];
    arguments[0].dispatchEvent(new Event('input', {bubbles:true}));
    arguments[0].dispatchEvent(new Event('change', {bubbles:true}));
    """, input_periodo, "01/06/2026 - 31/12/2026")

    body = wait.until( EC.presence_of_element_located( (By.TAG_NAME, "body")))
    body.click()
    exibir = wait.until( EC.presence_of_element_located( (By.CLASS_NAME, "form-check-input")))
    if exibir.is_selected():
        browser.execute_script( "arguments[0].click();", exibir )
    filtrar = wait.until( EC.element_to_be_clickable( (By.CLASS_NAME, "btn.btn-primary.btn-sm")))
    filtrar.click()
    tbody = wait.until( EC.presence_of_element_located((By.TAG_NAME, "tbody")))
    total_linhas = len(tbody.find_elements(By.TAG_NAME, "tr"))
    print(f"Total de linhas: {total_linhas}\n")
    for i in range(total_linhas):
        if i == 4:
            break
        body = wait.until( EC.presence_of_element_located( (By.TAG_NAME, "body")))
        body.click()
        tbody = WebDriverWait(browser, 10).until( EC.presence_of_element_located((By.TAG_NAME, "tbody")))
        rows = tbody.find_elements(By.TAG_NAME, "tr")
        row = rows[i]
        tds = row.find_elements(By.TAG_NAME, "td")
        icon = tds[0].find_element(By.TAG_NAME, "i")
        color = icon.get_attribute("style")  
        data = tds[1].text.strip()
        professor = tds[2].text.strip()
        disciplina_texto = tds[3].text.strip()
        codigo = disciplina_texto.split(" - ")[0]
        nome_disciplina = disciplina_texto.split(" - ")[1].strip()
        modulo = tds[4].text.strip()
        data_aula = tds[5].text.strip()
        email = tds[6].text.strip()
        print(f"Linha: {i}, Data: {data}, Professor: {professor}, Disciplina: {codigo}, Módulo: {modulo}, Data da Aula: {data_aula}, Email: {email}")
        if email == "[Não encontrado]":
            print(f"⚠️     Professor {professor} não tem email institucional cadastrado. Pulando...")
            gravar_sem_email_excel( caminho_excel="conflitos_horario.xlsx", professor=professor, codigo=codigo, nome_disciplina=nome_disciplina, data_aula=data_aula, modulo=modulo)
            print("-----------------------------------------------------------------------------------------------------------------------------------------------------------------")
            continue
        try:
            icon = row.find_element(By.CSS_SELECTOR, "td i")
            color = icon.get_attribute("style")
            #if "red" not in color: 
                #continue 
            button = row.find_element(By.CSS_SELECTOR, "button.btn.btn-default.btn-sm")
            browser.execute_script("arguments[0].click();", button)
            WebDriverWait(row, 5).until( lambda r: r.find_element( By.CSS_SELECTOR, "ul.dropdown-menu.show"))
            link_element = row.find_element( By.XPATH, ".//a[contains(., 'Acessar disciplina no Aprender')]")
            url = link_element.get_attribute("href")
            main = browser.current_window_handle
            browser.execute_script(f"window.open('{url}', '_blank');")
            wait.until(lambda d: len(d.window_handles) > 1)
            new_tab = [w for w in browser.window_handles if w != main][0]
            browser.switch_to.window(new_tab)
            wait.until( EC.presence_of_element_located((By.TAG_NAME, "h1")))
            h1 = browser.find_element(By.TAG_NAME, "h1").text.strip()
            wait.until(EC.presence_of_element_located((By.ID, "lblNomeCurso")))
            modalidade = browser.find_element(By.ID, "lblNomeCurso").text
            match = re.search(r'\((BACH|LIC)-', modalidade)
            if match:
                bach_ou_lic = match.group(1)
            else:
                bach_ou_lic = "Desconhecida"

            print(f"Modalidade: {bach_ou_lic}")
            print(f"1️⃣   Grade/Horário: {h1}")
            match = re.search(r"\((\d+)h\)", h1)
            if match:
                grade = int(match.group(1))
                print(f"2️⃣   Grade capturada: {grade}")
            handles_antes = browser.window_handles
            nova_aba = acessar_editar(browser, modulo, data_aula, grade, bach_ou_lic, nova_aba=True)
            if nova_aba:
                print("3️⃣   Edição terminada")
            browser.close()
            browser.switch_to.window(new_tab)

            url_modulos = browser.current_url
            abrir_adicionar_recurso(browser, modulo, grade, email, data_aula, professor, bach_ou_lic, codigo, nome_disciplina)
            browser.get(url_modulos)
            browser.close()
            browser.switch_to.window(main)
            print("-----------------------------------------------------------------------------------------------------------------------------------------------------------------")
        except Exception as e:
            print("Erro:", e)
    time.sleep(1000)