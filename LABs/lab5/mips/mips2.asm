
.text
.globl main

main:
         # x = 1
         addi $s0, $zero,1
         
         #t0 = 2*x
         add $t0, $s0, $s0
         
         #t0 = 4*x
         add $t0, $t0, $t0
         
         #t0 = 5*x
         add $t0, $t0, $s0
         
         #y = 15
         addi $s1, $zero, 15
         
         #y = 5*x + 15
         add $s1, $s1, $t0
         