#x -> $s0, y -> $s1, z -> $s2
.text
.globl main
main:
          addi $s0, $zero, 3
          addi $1, $zero, 4
          sll $t0, $s0, 4
          sub $t0, $t0, $s0
          sll $t1, $s1, 6
          sll $t2, $s1, 1
          add $t1, $t1, $t2
          add $t1, $t1, $s1
          add $t0, $t0, $t1
          sll $s2, $t0, 2
          