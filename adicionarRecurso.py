from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from datetime import datetime
from horarios import extrair_horarios
from selenium.common.exceptions import TimeoutException
from gravarExcel import gravar_conflitos_excel, gravar_sem_email_excel
import time
import re 

def abrir_adicionar_recurso(browser, modulo, grade, email, data_aula, professor, bach_ou_lic, numero_disciplina, nome_disciplina, timeout=10):
    match = re.search(r"\d+", modulo)
    if not match:
        raise ValueError(f"Módulo inválido: {modulo}")
    numero = match.group()
    nome_modulo = f"{numero}º Módulo"
    modulo_elemento = WebDriverWait(browser, timeout).until(
        EC.presence_of_element_located((
            By.XPATH,
            f"""
            //div[contains(@class,'divDisciplinaModulos')]
            [.//div[contains(@class,'divDisciplinaModulosTitulo')
            and contains(normalize-space(.), '{nome_modulo}')]]
            """
        ))
    )
    botao = modulo_elemento.find_element( By.XPATH, ".//div[contains(@onclick,'modalRec') and contains(., 'Adicionar novo recurso')]")
    onclick = botao.get_attribute("onclick")
    modal_id = re.search(r"#(modalRec-\d+)", onclick).group(1)
    browser.execute_script("arguments[0].click();", botao)
    print(f"4️⃣   Botão do adicionar recurso do módulo '{nome_modulo}' apertado.")
    modal = WebDriverWait(browser, timeout).until( EC.visibility_of_element_located((By.ID, modal_id)))
    link_meet = modal.find_element( By.XPATH, ".//a[contains(@href, 'ModuloRecursosAulaAoVivoMeet') or contains(., 'Aula ao vivo')]")
    href = link_meet.get_attribute("href")
    browser.get(href)
    Acesse_aula_ao_vivo = WebDriverWait(browser, timeout).until( EC.presence_of_element_located( (By.ID, "cphLayoutPrincipal_tbAtmTitulo")))
    data_f = extrair_horarios(browser, grade, data_aula, bach_ou_lic)[0]
    Aula_Data = f"Acesse a aula ao vivo - {data_f}"
    Acesse_aula_ao_vivo.clear()
    Acesse_aula_ao_vivo.send_keys(Aula_Data)
    print("5️⃣   Título preenchido.")
    emailW = WebDriverWait(browser, timeout).until( EC.presence_of_element_located( (By.ID, "respReuniao"))) #Email
    if email is not None:
        emailW.clear()
        emailW.send_keys(email)
    select_mostrar = WebDriverWait(browser, timeout).until( EC.presence_of_element_located( (By.ID, "cphLayoutPrincipal_ddlMostrar")))
    Select(select_mostrar).select_by_value("N")
    print("🔴   Campo 'Mostrar' definido como Não.")
    inserir_data_Inicio = WebDriverWait(browser, timeout).until( EC.presence_of_element_located( (By.ID, "tbAtmDtInicio")))
    data_inicio = datetime.strptime( data_aula, "%d/%m/%Y, %H:%M:%S")
    data_inicio = extrair_horarios(browser, grade, data_aula, bach_ou_lic)[4]
    data_formatada = data_inicio.strftime("%d-%m-00%Y%H:%M")
    inserir_data_Inicio.clear()
    inserir_data_Inicio.send_keys(data_formatada)
    print("6️    Data Inicio registrado")
    WebDriverWait(browser, 10).until(
        lambda d: d.find_element(By.ID, "tbAtmDtFim").get_attribute("value") != ""
    )
    #Inserir Data final
    data_final_formatada = extrair_horarios(browser, grade, data_aula, bach_ou_lic)[3]
    inserir_data_Final = WebDriverWait(browser, timeout).until( EC.element_to_be_clickable( (By.ID, "tbAtmDtFim")))
    browser.execute_script(""" arguments[0].value = ''; """, inserir_data_Final) 
    browser.execute_script(""" arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input')); arguments[0].dispatchEvent(new Event('change')); arguments[0].dispatchEvent(new Event('blur')); """, inserir_data_Final, data_final_formatada) 
    print("7️    Data Final registrado")
    checkbox = WebDriverWait(browser, timeout).until( EC.presence_of_element_located( (By.ID, "ckRegPart")))
    if not checkbox.is_selected():
        browser.execute_script( "arguments[0].click();", checkbox)
        print("8️    Checkbox 'Permitir registro de presença' ativado.")
        if grade == 60:
            checkboxFreq = WebDriverWait(browser, timeout).until( EC.presence_of_element_located( (By.ID, "ckRegFreq")))
            browser.execute_script( "arguments[0].click();", checkboxFreq)
            print("9️⃣    Checkbox 'Permitir registro de frequência' ativado.")
    # clica no botão Fonte
    fonte_btn = WebDriverWait(browser, 10).until( EC.element_to_be_clickable((By.ID, "cke_30"))) 
    browser.execute_script( "arguments[0].click();", fonte_btn)
    textarea = WebDriverWait(browser, 10).until( EC.presence_of_element_located( (By.CSS_SELECTOR, "textarea.cke_source")))
    html = """<pre> &nbsp;</pre> <style type="text/css">/* CSS para alinhar o texto à esquerda e aumentar a fonte do título */ body { text-align: left; } h1 { font-size: 24px; } /* CSS para adicionar um fundo cinza claro à div principal */ .main-div { background-color: #f2f2f2; padding: 20px; margin: 0 auto; max-width: 800px; } /* CSS para alinhar o texto à esquerda e adicionar um espaçamento entre as linhas */ p { text-align: left; line-height: 1.5em; margin-bottom: 10px; } /* CSS para destacar as instruções com negrito e uma linha inferior */ .instructions { font-weight: bold; border-bottom: 1px solid #000; margin-bottom: 20px; } /* CSS para adicionar um espaçamento extra antes e depois dos títulos secundários */ h2 { margin-top: 30px; margin-bottom: 20px; } /* CSS para alinhar o texto ao centro */ .center { text-align: center; } /* CSS para destacar a observação em itálico e com uma borda */ .observation { font-style: italic; border: 1px solid #000; padding: 10px; margin: 20px 0; } /* CSS para definir o tamanho da imagem */ img { width: 50px; height: 41px; } </style> <div class="main-div"><!-- Instruções --> <div class="instructions"> <h1>Instru&ccedil;&otilde;es</h1> </div> <!-- Conteúdo --> <p>1) Acesse &agrave; sala de webconfer&ecirc;ncia, pelo link acima.</p> <div class="center"><img alt="Sala de webconferência" src="https://www.unoeste.br/Site/AVA/_design/imagem/ico_googlemeet.png" /></div> <h2>Observa&ccedil;&otilde;es:</h2> <!-- Observações --> <div class="observation"> <p>Voc&ecirc; deve possuir navegador Internet Explorer 9 ou superior, Google Chrome ou Mozilla Firefox atualizados.</p> <p>&Eacute; importante que disponha de &aacute;udio (microfone e fones de ouvido) para participar da aula. Recomendamos que possua webcam, pois, eventualmente, pode ser solicitado a voc&ecirc; que ative-a.</p> <p>Sugerimos que acesse a sala com anteced&ecirc;ncia de pelo menos 5 min, para poss&iacute;veis ajustes de &aacute;udio, caso necess&aacute;rio.</p> </div> <br /> <br /> <!-- Desejo de uma excelente aula --> <div class="center"><strong>Desejamos a voc&ecirc; uma excelente aula!</strong></div> </div>"""
    textarea.clear()
    textarea.send_keys(html)
    fonte_btn = WebDriverWait(browser, 10).until( EC.element_to_be_clickable((By.ID, "cke_30")))
    browser.execute_script( "arguments[0].click();", fonte_btn)
    print("🔟   TextArea inserido.")
    notificar_participantes = WebDriverWait(browser, timeout).until( EC.presence_of_element_located( (By.ID, "ddlNotificar")))
    Select(notificar_participantes).select_by_value("não")
    print("🔴   Campo 'Notificar Participantes' definido como Não.")
    checkboxWhats = WebDriverWait(browser, timeout).until( EC.presence_of_element_located( (By.ID, "ckLembretePorSMS")))
    checkbox30min = WebDriverWait(browser, timeout).until( EC.presence_of_element_located( (By.ID, "cphLayoutPrincipal_ckCalLembrTempo30M")))
    checkbox1dia = WebDriverWait(browser, timeout).until( EC.presence_of_element_located( (By.ID, "cphLayoutPrincipal_ckCalLembrTempo1D")))
    if not checkboxWhats.is_selected():
        browser.execute_script( "arguments[0].click();", checkboxWhats)
    if not checkbox30min.is_selected():
        browser.execute_script( "arguments[0].click();", checkbox30min)
    if not checkbox1dia.is_selected():
        browser.execute_script( "arguments[0].click();", checkbox1dia)
    print("🆗   Lembretes por WhatsApp, 30 minutos e 1 dia antes ativados.")
    salvar = WebDriverWait(browser, timeout).until( EC.element_to_be_clickable( (By.ID, "cphLayoutPrincipal_btnSalvar")))
    browser.execute_script( "arguments[0].click();", salvar)
    WebDriverWait(browser, timeout).until( lambda d: d.execute_script( "return document.readyState") == "complete") 
    try:
        div_conflito = WebDriverWait(browser, 3).until( EC.presence_of_element_located((By.ID, "divConflito")))
        itens = div_conflito.find_elements(By.TAG_NAME, "li")
        conflitos = []
        for item in itens:
            texto = item.text.strip()
            if " - " in texto:
                nome, disciplina_conflito = texto.split(" - ", 1)
            else:
                nome = texto
                disciplina_conflito = ""
            conflitos.append({
                "nome": nome.strip(),
                "disciplina_conflito": disciplina_conflito.strip()
            })
        data_inicio = extrair_horarios(browser, grade, data_aula, bach_ou_lic)[4]
        print(f"⚠️  Conflito encontrado. {len(conflitos)} registro(s) gravado(s) no Excel.")
        gravar_conflitos_excel(
            caminho_excel="conflitos_horario.xlsx",
            numero_disciplina=numero_disciplina,
            nome_disciplina=nome_disciplina,
            data=data_inicio,
            modulo=modulo,
            conflitos=conflitos
        )
    except TimeoutException:
        print("✅   Nenhum conflito encontrado.")