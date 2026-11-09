.text
.globl main
main:
lui  $s0, 0x1001          # base do vetor
add  $t3, $s0, $zero      # ponteiro
add  $t0, $zero, $zero    # i = 0
addi $t1, $zero, 100      # limite
add  $t2, $zero, $zero    # soma = 0
loop:
beq  $t0, $t1, fim
sll  $t4, $t0, 1          # 2i
addi $t4, $t4, 1          # 2i + 1
sw   $t4, 0($t3)          # vetor[i]
add  $t2, $t2, $t4        # soma += vetor[i]
addi $t3, $t3, 4
addi $t0, $t0, 1
j    loop
fim:
sw   $t2, 0($t3)          # logo após a última posição (base + 400)