# x -> $s0, y -> $s1, z -> $s2
.text
.globl main
main:  
          lui     $s0, 0x7FFF
          ori     $s0, $s0, 0xFFFF
          lui     $s1, 0x0004
          ori     $s1, $s1, 0x93E0
          sll      $t0, $t1, 2
          sub   $s2, $s0, $t0