from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import os
import time
import traceback

def atualizar_aula_grade_80(browser, modulo, data_formatada, hora_inicio, hora_final, timeout=10):
    textarea = WebDriverWait(browser, 10).until( EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.cke_source")))
    html = textarea.get_attribute("value")
    soup = BeautifulSoup(html, "html.parser")
    if hora_inicio.endswith(":00"):
        hora_inicio_html = hora_inicio.replace(":00", "h")
    else:
        hora_inicio_html = hora_inicio.replace(":", "h")
    if hora_final.endswith(":00"):
        hora_final_html = hora_final.replace(":00", "h")
    else:
        hora_final_html = hora_final.replace(":", "h")
    novo_horario = f"{data_formatada} das {hora_inicio_html} às {hora_final_html}"
    texto_modulo = f"{modulo}ª Aula ao vivo"
    linhas = soup.find_all("tr")
    encontrou = False
    for linha in linhas:
        texto_linha = linha.get_text(" ", strip=True)
        if texto_modulo in texto_linha:
            colunas = linha.find_all("td")
            if len(colunas) >= 2:
                b_horario = colunas[1].find("b")
                if b_horario:
                    b_horario.string = novo_horario
                    encontrou = True
                    print(f"✅ Atualizado módulo {modulo}: {novo_horario}")
                    break
    if not encontrou:
        print(f"❌ Módulo {modulo} não encontrado na tabela")

    novo_html = str(soup)
    browser.execute_script(""" arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true })); arguments[0].dispatchEvent(new Event('change', { bubbles: true })); """, textarea, novo_html)