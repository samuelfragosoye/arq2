#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EP03 - ULA 4 bits + Arduino  |  Programa do PC

O que este programa faz:
  1) Le o arquivo fonte "testeula.ula" (X=..; Y=..; W=mnemonico;).
  2) Converte cada instrucao W=... em 3 digitos hexadecimais "XYS"
     (X = valor de X, Y = valor de Y, S = codigo da instrucao da ULA)
     e grava o resultado em "testeula.hex".
  3) Detecta erros (sintaxe errada e linhas em branco): mostra o erro,
     IGNORA a linha e CONTINUA a conversao normalmente.
  4) Envia o .hex ao Arduino pela porta serial (todas as linhas de uma vez,
     so depois o Arduino pergunta se deve executar).

Uso:  python ula_pc.py [PORTA]      ex.: python ula_pc.py COM3
      (precisa de:  pip install pyserial   -- so para o envio serial)
"""

import re
import sys
import time
import threading

try:
    import serial                      # pyserial
    import serial.tools.list_ports
except ImportError:                    # sem pyserial so gera o .hex
    serial = None

ARQ_ULA = "testeula.ula"               # arquivo fonte (entrada)
ARQ_HEX = "testeula.hex"               # arquivo gerado (saida)
BAUD = 9600                            # mesma velocidade do Serial.begin() do Arduino

# Figura 2: mnemonico -> codigo hexadecimal da instrucao (S)
MNEMONICOS = {
    "nA": 0x0,    "AoBn": 0x1,  "nAeB": 0x2,  "zeroL": 0x3,
    "AeBn": 0x4,  "nB": 0x5,    "AxB": 0x6,   "AenB": 0x7,
    "nAoB": 0x8,  "AxBn": 0x9,  "copiaB": 0xA, "AeB": 0xB,
    "umL": 0xC,   "AonB": 0xD,  "AoB": 0xE,   "copiaA": 0xF,
}

# Expressoes regulares das linhas validas
RE_INICIO = re.compile(r"^inicio\s*:$")
RE_FIM = re.compile(r"^fim\s*\.$")
RE_XY = re.compile(r"^([XY])\s*=\s*(\d+)\s*;$")        # X=12;  Y=6;
RE_W = re.compile(r"^W\s*=\s*([A-Za-z]+)\s*;$")        # W=AeB;


def converter(arquivo):
    """Le o .ula e devolve (lista_de_instrucoes_hex, lista_de_erros)."""
    with open(arquivo, "r", encoding="utf-8-sig") as f:
        linhas = f.read().splitlines()

    hexs, erros = [], []
    x = y = 0                          # valores atuais de X e Y (persistem entre linhas)
    achou_fim = False

    for n, bruta in enumerate(linhas, start=1):
        linha = bruta.strip()

        # ERRO 1: linha em branco (informa e continua)
        if linha == "":
            erros.append(f"linha {n}: linha em branco")
            continue

        if RE_INICIO.match(linha):     # marcador de inicio: nada a gerar
            continue
        if RE_FIM.match(linha):        # marcador de fim: encerra a leitura
            achou_fim = True
            break

        m = RE_XY.match(linha)
        if m:                          # atribuicao a X ou Y
            valor = int(m.group(2))
            if valor > 15:             # so cabem 4 bits (0..15)
                erros.append(f"linha {n}: valor {valor} fora de 0..15 -> '{linha}'")
                continue
            if m.group(1) == "X":
                x = valor
            else:
                y = valor
            continue

        m = RE_W.match(linha)
        if m:                          # instrucao W=mnemonico;
            mnem = m.group(1)
            if mnem not in MNEMONICOS:
                erros.append(f"linha {n}: mnemonico desconhecido '{mnem}' -> '{linha}'")
                continue
            # monta XYS: tres digitos hexadecimais
            hexs.append(f"{x:X}{y:X}{MNEMONICOS[mnem]:X}")
            continue

        # ERRO 2: sintaxe errada (nenhum formato valido)
        erros.append(f"linha {n}: sintaxe invalida -> '{linha}'")

    if not achou_fim:
        erros.append("aviso: marcador 'fim.' nao encontrado")
    return hexs, erros


def escolher_porta():
    """Lista as portas seriais e deixa o usuario escolher."""
    portas = list(serial.tools.list_ports.comports())
    if not portas:
        return None
    for i, p in enumerate(portas):
        print(f"  [{i}] {p.device} - {p.description}")
    r = input("Numero da porta (ENTER cancela): ").strip()
    return portas[int(r)].device if r.isdigit() and int(r) < len(portas) else None


def enviar_serial(hexs, porta):
    """Envia todas as instrucoes ao Arduino e acompanha a execucao."""
    ser = serial.Serial(porta, BAUD, timeout=0.2)
    time.sleep(2)                      # o Arduino reinicia ao abrir a porta
    ser.reset_input_buffer()

    pergunta = threading.Event()       # Arduino perguntou "Executar? (s/n)"
    fim = threading.Event()            # Arduino terminou/cancelou

    def leitor():
        """Thread que imprime tudo o que o Arduino escreve."""
        while not fim.is_set():
            lin = ser.readline().decode("utf-8", errors="replace").rstrip()
            if not lin:
                continue
            print("[Arduino]", lin)
            if "Executar programa" in lin:
                pergunta.set()
            if "finalizada" in lin or "cancelada" in lin:
                fim.set()

    t = threading.Thread(target=leitor, daemon=True)
    t.start()

    print("\nEnviando programa (carga do vetor)...")
    for h in hexs:                     # carga completa ANTES de executar
        ser.write((h + "\n").encode())
        time.sleep(0.05)

    if not pergunta.wait(timeout=10):
        print("O Arduino nao respondeu com a pergunta de execucao.")
        fim.set()
        ser.close()
        return

    resp = input("Executar programa? (s/n): ").strip().lower()
    ser.write((("s" if resp == "s" else "n") + "\n").encode())
    fim.wait()                         # espera o fim da execucao
    time.sleep(0.5)
    ser.close()


def main():
    try:
        hexs, erros = converter(ARQ_ULA)
    except FileNotFoundError:
        print(f"Arquivo '{ARQ_ULA}' nao encontrado.")
        return

    # Mostra os erros e segue normalmente (nao interrompe a carga)
    for e in erros:
        print("[ERRO]", e)

    # Grava o .hex com as instrucoes validas
    with open(ARQ_HEX, "w", encoding="utf-8") as f:
        f.write("\n".join(hexs) + ("\n" if hexs else ""))
    print(f"\n{len(hexs)} instrucao(oes) gravada(s) em '{ARQ_HEX}':")
    for h in hexs:
        print("  ", h)

    if serial is None:
        print("\npyserial nao instalado (pip install pyserial): envio serial desativado.")
        return
    if input("\nEnviar ao Arduino? (s/n): ").strip().lower() != "s":
        return
    porta = sys.argv[1] if len(sys.argv) > 1 else escolher_porta()
    if not porta:
        print("Nenhuma porta selecionada.")
        return
    enviar_serial(hexs, porta)


if __name__ == "__main__":
    main()
