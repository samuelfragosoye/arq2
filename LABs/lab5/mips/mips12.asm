.data 
k: .word 10
.text 
.globl main 
main: 
           lui $s0, 0x1001
           ori $t0, $s0, 0x0000
           ori $t1, $s0, 0x0004
           ori $t2, $s0, 0x0008
           ori $t3, $s0, 0x000C
           sw $t0, 0($t1)
           sw $t1, 0($t2)
           sw $t2, 0($t3)
           
           add $s1, $t3, $zero
           
           lw $t4, 0($s1)
           lw $t5, 0($t4)
           lw $t6, 0($t5)
           lw $t7, 0($t6)
           sll $t7, $t7, 1
           sw $t7, 0($t6)
           