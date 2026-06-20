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
from horarios import extrair_horarios
from atualizarAulaPorGrade_60 import atualizar_aula_grade_60
from atualizarAulaPorGrade_80 import atualizar_aula_grade_80
import re
import os
import time
import traceback

def acessar_editar(browser, modulo, data_aula, grade, bach_ou_lic, timeout=10, nova_aba=False):
    try:
        texto = WebDriverWait(browser, timeout).until( EC.presence_of_element_located( ( By.XPATH, "//span[contains(@class,'tex2jax_ignore') and contains(., 'Webconferências') and contains(., 'Aulas ao vivo')]")))
        container = texto.find_element( By.XPATH, "./ancestor::tr[contains(@data-atmid, '')][1]")
        ActionChains(browser).move_to_element(container).perform()
        editar_link = container.find_element( By.CSS_SELECTOR, "a[title='Alterar']")
        WebDriverWait(browser, timeout).until( lambda d: editar_link.is_displayed())
        if nova_aba:
            handles_antes = browser.window_handles
            url = editar_link.get_attribute("href")
            if url.startswith("/"):
                url = "https://www.unoeste.br" + url
            browser.execute_script( f"window.open('{url}', '_blank');")
            WebDriverWait(browser, timeout).until( lambda d: len(d.window_handles) > len(handles_antes))
            nova_aba_handle = [ w for w in browser.window_handles if w not in handles_antes ][0]
            browser.switch_to.window(nova_aba_handle)
            fonte_btn = WebDriverWait(browser, 10).until( EC.element_to_be_clickable((By.ID, "cke_28")))
            browser.execute_script( "arguments[0].click();", fonte_btn)
            
            data_formatada = extrair_horarios(browser, grade,data_aula, bach_ou_lic)[0]
            hora_inicio = extrair_horarios(browser, grade, data_aula, bach_ou_lic)[1]
            hora_final = extrair_horarios(browser, grade, data_aula, bach_ou_lic)[2]
            numero_modulo = int(re.search(r"\d+", modulo).group())
            if grade == [80, 40]:
                atualizar_aula_grade_80(browser, numero_modulo, data_formatada, hora_inicio, hora_final)
            else:
                atualizar_aula_grade_60(browser, modulo, data_formatada, hora_inicio, hora_final)

            fonte_btn = WebDriverWait(browser, 10).until( EC.element_to_be_clickable((By.ID, "cke_28")))
            browser.execute_script( "arguments[0].click();", fonte_btn)
            salvar = WebDriverWait(browser, 10).until( EC.element_to_be_clickable((By.ID, "cphLayoutPrincipal_bSalvarTextoBreve")))
            salvar.click()
            WebDriverWait(browser, timeout).until( lambda d: d.execute_script( "return document.readyState") == "complete")
            
            return nova_aba_handle
        else:
            browser.execute_script( "arguments[0].click();", editar_link)
            return browser.current_window_handle

    except Exception as e:
        print("Erro ao acessar editar:", e)
        return None