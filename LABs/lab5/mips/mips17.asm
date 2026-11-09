.data
x: .word 6
y: .word 7
k: .word 0

.text
.globl main
main:
lui  $t0, 0x1001
lw   $s0, 0($t0)          # x
lw   $s1, 4($t0)          # y (contador)
add  $s2, $zero, $zero    # k = 0
loop:
beq  $s1, $zero, fim
add  $s2, $s2, $s0        # k += x
addi $s1, $s1, -1
j    loop
fim:
sw   $s2, 8($t0)          # 3ª posição