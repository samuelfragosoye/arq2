
.text
.globl main

main:
    # Inicializacao
    addi $s0, $zero, 2  # a = 2
    addi $s1, $zero, 3  # b = 3
    addi $s2, $zero, 4  # c = 4
    addi $s3, $zero, 5  # d = 5

    # x = (a+b) - (c+d)
    add $s4, $s0, $s1
    add $s5, $s2, $s3
    sub $s6, $s4, $s5

    # y = a-b+x
    sub $s7, $s0, $s1
    add $s7, $s7, $s6

    # b = x-y
    sub $s1, $s6, $s7
