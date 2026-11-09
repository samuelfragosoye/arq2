#x -> $s0, y -> $s1, z -> $s2
.text
.globl main
main:
          lui     $s0, 0x0001
          ori     $s0, $s0, 0x86A0
          lui     $s1, 0x0003
          ori     $s1, $s1, 0x0D40
          add   $s2, $s0, $s1