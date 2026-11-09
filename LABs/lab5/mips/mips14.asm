.data
A: .word 7

.text
.globl main
main:
lui  $t0, 0x1001
lw   $t1, 0($t0)          # A
andi $t2, $t1, 1          # bit menos significativo
beq  $t2, $zero, par
addi $t3, $zero, 1        # ímpar -> 1
j    fim
par:
add  $t3, $zero, $zero    # par -> 0
fim:
sw   $t3, 8($t0)          # 2ª posição livre