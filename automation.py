from pyfiglet import Figlet
import subprocess
from colorama import Fore, Style, init
from buscarAluno import buscarAlunoExecutar
import sys
import os

while True:
    os.system("cls" if os.name == "nt" else "clear")
    f = Figlet(font="Slant")
    print(f.renderText("Suporte Tecnologico"))

    init()
    print(Fore.CYAN + "╔══════════════════════════════╗")
    print("║         AUTOMATION           ║")
    print("╚══════════════════════════════╝")
    print(Fore.GREEN + "[1] Buscar Aluno")
    print(Fore.RED + "[0] Sair")
    print(Style.RESET_ALL)

    opcao = input("-> ")

    match opcao:
        case "1":
            buscarAlunoExecutar()
        case "0":
            print("Encerrando...")
            break
        case _:
            print("Opção inválida!")