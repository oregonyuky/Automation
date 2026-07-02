from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from pyfiglet import Figlet
from colorama import Fore, Style, init
from getpass import getpass
import sys
import os
import time
import re

options = Options()
options.add_argument("--log-level=3")
options.add_argument("--disable-logging")
options.add_argument("--disable-gpu")
options.add_argument("--disable-features=VoiceTranscription")
options.add_experimental_option("excludeSwitches", ["enable-logging"])
service = Service(log_output="NUL")  # Windows

def executar(ra, senha, count):
    print(Fore.YELLOW + f"\n=== Buscar Aluno {count} ===")
    print(Style.RESET_ALL)
    print("• Informe o RA ou o nome completo do aluno")
    print("• Digite 'sair' para encerrar")
    while True:
        raAluno = input("\nRA ou nome: ").strip()
        if raAluno == "":
            continue  
        if raAluno.lower() == "sair":
            sys.exit()
        break
    if raAluno.lower() == "sair":
        sys.exit()
    if not any(c.isalpha() for c in raAluno):
        raAluno = raAluno.replace(".", "").replace("-", "").replace(" ", "")
    
    browser = webdriver.Chrome(service=service, options=options)
    try:
        browser.get("https://www.unoeste.br/Academico/EAD/Login.aspx")
        browser.maximize_window()
        wait = WebDriverWait(browser, 20)
        campo_ra = wait.until(EC.presence_of_element_located( (By.ID, "cphLayoutPrincipal_txbMatricula")))
        campo_senha = wait.until( EC.presence_of_element_located( (By.ID, "cphLayoutPrincipal_txbSenha")))
        botao_login = wait.until( EC.element_to_be_clickable( (By.ID, "cphLayoutPrincipal_btnEntrar")))
        campo_ra.clear()
        campo_ra.send_keys(ra)
        campo_senha.clear()
        campo_senha.send_keys(senha)
        botao_login.click()
        wait.until( EC.presence_of_element_located( (By.TAG_NAME, "body")))
        pesquisa = wait.until( EC.presence_of_element_located( (By.CLASS_NAME, "lkPesquisa")))
        browser.execute_script( "arguments[0].click();", pesquisa)
        campo_busca = wait.until(EC.element_to_be_clickable( (By.CLASS_NAME, "inpBuscaAluno")))

        campo_busca.click()
        campo_busca.send_keys(Keys.CONTROL, "a")
        campo_busca.send_keys(Keys.DELETE)

        browser.execute_script("""
        arguments[0].value = arguments[1];
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('keyup', { bubbles: true }));
        """, campo_busca, raAluno)


        botao_busca = wait.until( EC.element_to_be_clickable((By.ID, "btnBuscarAluno")))

        browser.execute_script( "arguments[0].click();", botao_busca)
        if browser.find_elements( By.XPATH, "//td[contains(normalize-space(), 'Nenhum Registro')]"):
            print("Nenhum aluno foi encontrado.")
        else:
            checkbox = browser.find_element(By.ID, "cphLayoutPrincipal_ckMesmaPagina")

            if not checkbox.is_selected():
                checkbox.click()
                print("Visualizar aluno na mesma tela - Alterada")
            
            perfis = browser.find_elements( By.XPATH, "//*[starts-with(@id,'cphLayoutPrincipal_gvAluno_linkPerfil_')]")
            ra_aluno_text = None
            encontrou = False
            for i in range(len(perfis)):

                # recarrega a lista porque a página muda após abrir/fechar perfil
                perfis = browser.find_elements( By.XPATH, "//*[starts-with(@id,'cphLayoutPrincipal_gvAluno_linkPerfil_')]")

                url_antes = browser.current_url

                # Primeira tentativa: clique real via ActionChains (mais respeitado pelo fancybox)
                try:
                    ActionChains(browser).move_to_element(perfis[i]).click().perform()
                except WebDriverException:
                    pass

                time.sleep(0.5)

                if browser.current_url != url_antes:
                    print("href foi seguido em vez do modal abrir, voltando e tentando via JS...")
                    browser.back()
                    wait.until(EC.presence_of_element_located((By.XPATH, "//*[starts-with(@id,'cphLayoutPrincipal_gvAluno_linkPerfil_')]")))

                    # recarrega a lista de novo após o back()
                    perfis = browser.find_elements(By.XPATH, "//*[starts-with(@id,'cphLayoutPrincipal_gvAluno_linkPerfil_')]")

                    browser.execute_script("arguments[0].click();", perfis[i])

                iframes = browser.find_elements(By.TAG_NAME, "iframe")

                for iframe in iframes:
                    browser.switch_to.default_content()
                    browser.switch_to.frame(iframe)
                    try:
                        situacao = browser.find_element( By.XPATH, "//th[contains(text(),'Situação Acadêmica:')]/following-sibling::td[1]").text.strip()
                        if situacao.upper() == "CURSANDO" or situacao.upper() == "SEM REMATRICULA":
                            ra_aluno = browser.find_element( By.XPATH, "//th[contains(text(),'R.A.:')]/following-sibling::td[1]" ) 
                            print("RA:", ra_aluno.text.strip())
                            ra_aluno_text = ra_aluno.text.strip()
                            nome = browser.find_element( By.CLASS_NAME, "nomeAluno").text.strip()
                            print("Nome:", nome)
                            curso = browser.find_element( By.XPATH, "//th[contains(text(),'Curso:')]/following-sibling::td[1]" ) 
                            print("Curso:", curso.text.strip())
                            encontrou = True
                            break
                    except:
                        pass

                if encontrou:
                    break
                browser.switch_to.default_content()
                try:
                    fechar = wait.until( EC.element_to_be_clickable((By.CLASS_NAME, "modal-close-custom")))
                    browser.execute_script("arguments[0].click();", fechar)
                except:
                    pass

            if not encontrou:
                print("Nenhum aluno com situação CURSANDO foi encontrado.")
            else:
                elementos = browser.find_elements(By.ID, "btnEnviarAcesso")
                try:
                    acesso = WebDriverWait(browser, 2).until(
                        EC.element_to_be_clickable((By.ID, "btnEnviarAcesso"))
                    )
                    browser.execute_script("arguments[0].click();", acesso)
                except TimeoutException:
                    print("btnEnviarAcesso não encontrado, seguindo...")

                while True:
                    try:
                        senha = WebDriverWait(browser, 1, poll_frequency=0.1).until(
                            EC.visibility_of_element_located(
                                (By.XPATH, "//table[contains(@class,'senhaTemp')]//tbody/tr[1]/td[4]")
                            )
                        ).text.strip()

                        if senha:
                            print("Senha temporária:", senha)
                            break

                    except TimeoutException:
                        pass

                    try:
                        botao = browser.find_element(By.ID, "btnGerarSenhaTemporaria")
                        browser.execute_script("arguments[0].click();", botao)

                    except Exception:
                        print("Botão btnGerarSenhaTemporaria não encontrado.")
                        break

                browser.execute_script("window.open('');")
                browser.switch_to.window(browser.window_handles[-1])
                browser.get("https://www.unoeste.br/site/ava/")

                wait = WebDriverWait(browser, 20)
                campo_ra = wait.until(EC.presence_of_element_located( (By.ID, "tbLogin")))
                campo_senha = wait.until( EC.presence_of_element_located( (By.ID, "tbSenha")))
                botao_login = wait.until( EC.element_to_be_clickable( (By.ID, "bAutenticar")))
                campo_ra.clear()
                campo_ra.send_keys(ra_aluno_text)
                campo_senha.clear()
                campo_senha.send_keys(senha)

                botao_login.click()

        input("Pressione ENTER para fazer outra consulta...")
    except WebDriverException:
        print("Navegador foi fechado. Voltando para o início...")
    finally:
        try:
            pass
        except:
            pass

def buscarAlunoExecutar():
    os.system("cls" if os.name == "nt" else "clear")
    f = Figlet(font="Slant")
    print(f.renderText("Buscar Aluno"))

    ra = input("RA: ").strip()
    senha = getpass("SENHA: ").strip()
    count = 1
    while True:
        executar(ra, senha, count)
        count += 1