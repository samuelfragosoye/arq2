.data
x1:      .word 15
x2:      .word 25
x3:      .word 13
x4:      .word 17
soma: .word -1

.text
.globl main
main:
           lui $t0, 0x1001
           lw $t1, 0($t0)
           lw $t2, 4($t0)
           lw $t3, 8($t0)
           lw $t4, 12($t0)
           add $t5, $t1, $t2
           add $t5, $t5, $t3
           add $t5, $t5, $t4
           sw $t5, 15($t0)