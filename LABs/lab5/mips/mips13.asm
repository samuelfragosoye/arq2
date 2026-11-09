.data
A: .word -25

.text
.globl main
main:
           lui $t0, 0x1001
           lw $t1, 0($t0)
           slt $t2, $t1, $zero
           beq $t2, $zero, fim
           sub $t1, $zero, $t1
           fim:
           sw $t1, 0($t0)