from datetime import datetime, timedelta

def extrair_horarios(browser, grade, data_original, bach_ou_lic):
    data = datetime.strptime(data_original,"%d/%m/%Y, %H:%M:%S")
    data = data.replace( month=data.month - 1) #Esse daqui só serve para teste
    data = data.replace( day=data.day + 20) #Esse daqui só serve para teste
    if (grade in [80, 40]) or ((bach_ou_lic.strip()=="BACH") and (grade == 60)):
        H = 1
        M = 40
    elif grade == 60:
        H = 1
        M = 0
    else:
        H = 0
        M = 0
    if grade in [80, 40]:
        duracao = timedelta(hours=H, minutes=M)
    elif grade == 60:
        duracao = timedelta(hours=H, minutes=M)
    else:
        duracao = timedelta()
    hora_inicio = data.strftime("%H:%M")
    hora_final = (data + duracao).strftime("%H:%M")
    data_formatada = data.strftime("%d/%m")
    data_final_googlemeet = (data + duracao).strftime("%Y-%m-%dT%H:%M")
    
    return data_formatada, hora_inicio, hora_final, data_final_googlemeet, data