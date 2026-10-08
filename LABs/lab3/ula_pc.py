#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EP03 - ULA 4 bits + Arduino | Programa do PC

O que este programa faz:
1) Le o arquivo fonte "testeula.ula".
2) Converte as instrucoes para tres digitos hexadecimais XYS.
3) Detecta erros de sintaxe e valores invalidos.
4) Grava as instrucoes validas no arquivo "testeula.hex".
"""

import re

ARQ_ULA = "testeula.ula"               # arquivo fonte (entrada)
ARQ_HEX = "testeula.hex"               # arquivo gerado (saida)

# Figura 2: mnemonico -> codigo hexadecimal da instrucao (S)
MNEMONICOS = {
    "nA": 0x0,    "AoBn": 0x1,  "nAeB": 0x2,  "zeroL": 0x3,
    "AeBn": 0x4,  "nB": 0x5,    "AxB": 0x6,   "AenB": 0x7,
    "nAoB": 0x8,  "AxBn": 0x9,  "copiaB": 0xA, "AeB": 0xB,
    "umL": 0xC,   "AonB": 0xD,  "AoB": 0xE,   "copiaA": 0xF,
}

# Expressoes regulares das linhas validas
RE_INICIO = re.compile(r"^inicio\s*:$")
RE_FIM    = re.compile(r"^fim\s*\.$")
RE_XY     = re.compile(r"^([XY])\s*=\s*(\d+)\s*;$")        # X=12;  Y=6;
RE_W      = re.compile(r"^W\s*=\s*([A-Za-z]+)\s*;$")        # W=AeB;


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

    print("\nConversao concluida.")
    print("Use as instrucoes geradas para testar o Arduino no Tinkercad.")


if __name__ == "__main__":
    main()