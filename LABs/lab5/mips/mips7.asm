.text
.globl main
main:
          ori   $8, $0, 0x01
          sll    $8, $8, 31
          sra  $8, $8, 31