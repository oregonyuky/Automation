import re
from datetime import datetime
from bs4 import BeautifulSoup, Tag
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def formatar_hora(hora):
    h, m = hora.split(":")
    if m == "00":
        return f"{h}h"
    return f"{h}h{m}"


def pegar_data_do_texto(texto):
    match = re.search(r"(\d{2}/\d{2})", texto)
    if not match:
        return None
    return datetime.strptime(match.group(1), "%d/%m")

def atualizar_aula_grade_60(browser, modulo, data_formatada, hora_inicio, hora_final, timeout=10):
    numero_modulo = int(re.search(r"\d+", modulo).group())
    aula_1 = ((numero_modulo - 1) * 2) + 1
    aula_2 = aula_1 + 1

    # Novo horário formatado
    novo_horario = f"{data_formatada} das {formatar_hora(hora_inicio)} às {formatar_hora(hora_final)}"
    nova_data = datetime.strptime(data_formatada, "%d/%m")

    # Pega o HTML do CKEditor
    textarea = WebDriverWait(browser, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.cke_source"))
    )
    html = textarea.get_attribute("value")
    soup = BeautifulSoup(html, "html.parser")
    linhas = soup.find_all("tr")

    # Localiza as duas aulas
    linha_aula_1 = None
    linha_aula_2 = None
    for linha in linhas:
        texto_linha = linha.get_text(" ", strip=True)
        if f"{aula_1}ª Aula ao vivo" in texto_linha:
            linha_aula_1 = linha
        if f"{aula_2}ª Aula ao vivo" in texto_linha:
            linha_aula_2 = linha

    if not linha_aula_1 or not linha_aula_2:
        print(f"❌  Não encontrou as aulas {aula_1} e {aula_2}")
        return

    # Pega os td de horário (segunda coluna)
    td1 = linha_aula_1.find_all("td")[1]
    td2 = linha_aula_2.find_all("td")[1]

    # Função interna para atualizar horário mantendo estilo
    def atualizar_td(td, texto):
        td.clear()
        td.append(BeautifulSoup(f"""
            <span style="font-size:14px;">
                <span style="color:#e67e22;">
                    <span style="font-family:Trebuchet MS,Helvetica,sans-serif;">
                        <b>{texto}</b>
                    </span>
                </span>
            </span>
        """, "html.parser"))

    # Pega textos atuais
    texto1 = td1.get_text(" ", strip=True)
    texto2 = td2.get_text(" ", strip=True)

    if novo_horario in texto1 or novo_horario in texto2:
        print(f"⏭️ Já existe essa data e horário: {novo_horario}. Não fez alteração.")
        return
        
    data1 = pegar_data_do_texto(texto1)
    data2 = pegar_data_do_texto(texto2)

    vazio1 = "XX/XX" in texto1
    vazio2 = "XX/XX" in texto2

    if vazio1 and vazio2:
        atualizar_td(td1, novo_horario)
        print(f"📝  Inseriu na {aula_1}ª aula.")

    elif not vazio1 and vazio2:
        if nova_data < data1:
            atualizar_td(td1, novo_horario)
            atualizar_td(td2, texto1)
            print(f"📝  Inseriu na {aula_1}ª e moveu a antiga para {aula_2}ª.")
        else:
            atualizar_td(td2, novo_horario)
            print(f"📝  Inseriu na {aula_2}ª aula.")

    elif vazio1 and not vazio2:
        if nova_data < data2:
            atualizar_td(td1, novo_horario)
            print(f"📝  Inseriu na {aula_1}ª aula.")
        else:
            atualizar_td(td1, texto2)
            atualizar_td(td2, novo_horario)
            print(f"📝  Moveu antiga para {aula_1}ª e inseriu nova na {aula_2}ª.")

    else:
        if nova_data < data1:
            atualizar_td(td1, novo_horario)
            atualizar_td(td2, texto1)
            print(f"📝  Nova data menor. Inseriu na {aula_1}ª e moveu antiga para {aula_2}ª.")

        elif nova_data > data2:
            atualizar_td(td2, novo_horario)
            print(f"📝  Nova data maior. Inseriu na {aula_2}ª.")

        else:
            atualizar_td(td2, novo_horario)
            print(f"📝  Nova data entre as duas. Inseriu na {aula_2}ª.")

    # Atualiza o HTML do CKEditor
    novo_html = str(soup)
    browser.execute_script("""
        arguments[0].value = arguments[1];
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
    """, textarea, novo_html)