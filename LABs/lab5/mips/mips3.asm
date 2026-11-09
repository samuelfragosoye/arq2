.text
.globl main
main:
    addi $s0, $zero, 3      # x = 3
    addi $s1, $zero, 4      # y = 4

    # 15*x = 8*x + 4*x + 2*x + x
    add $t0, $s0, $s0       # 2*x
    add $t1, $t0, $t0       # 4*x
    add $t2, $t1, $t1       # 8*x
    add $t3, $t2, $t1       # 12*x
    add $t3, $t3, $t0       # 14*x
    add $t3, $t3, $s0       # 15*x

    # 67*y = 64*y + 2*y + y
    add $t4, $s1, $s1       # 2*y
    add $t5, $t4, $t4       # 4*y
    add $t5, $t5, $t5       # 8*y
    add $t5, $t5, $t5       # 16*y
    add $t5, $t5, $t5       # 32*y
    add $t5, $t5, $t5       # 64*y
    add $t5, $t5, $t4       # 66*y
    add $t5, $t5, $s1       # 67*y

    # z = (15*x + 67*y)*4
    add $s2, $t3, $t5       # 15*x + 67*y
    add $s2, $s2, $s2       # *2
    add $s2, $s2, $s2       # *4