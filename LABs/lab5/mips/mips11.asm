.data 
x: .word 100000
z: .word 200000
y: .word 0

.text
.globl main
main:
           lui $t0, 0x1001
           lw $s0, 0($t0)
           lw $s1, 4($t0)
           sub $t1, $s0, $s1
           lui $t2, 0x0004
           ori $t2, $t2, 0x93E0
           add $t1, $t1, $t2
           sw $t1, 8($t0)