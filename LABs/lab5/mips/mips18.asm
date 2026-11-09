.data
x: .word 3
y: .word 4
k: .word 0

.text
.globl main
main:
lui  $t0, 0x1001
lw   $s0, 0($t0)          # x
lw   $s1, 4($t0)          # y (expoente)
addi $s2, $zero, 1        # k = 1
outer:
beq  $s1, $zero, fim
add  $t1, $zero, $zero    # acumulador
add  $t2, $s0, $zero      # contador = x
inner:                    # t1 = k * x por somas
beq  $t2, $zero, fim_inner
add  $t1, $t1, $s2
addi $t2, $t2, -1
j    inner
fim_inner:
add  $s2, $t1, $zero      # k = k * x
addi $s1, $s1, -1
j    outer
fim:
sw   $s2, 8($t0)