.text
.globl main
main:
lui  $s0, 0x0018
ori  $s0, $s0, 0x6A00     # x = 1600000
lui  $s1, 0x0001
ori  $s1, $s1, 0x3880     # y = 80000
lui  $s2, 0x0006
ori  $s2, $s2, 0x1A80     # z = 400000
div  $s0, $s2             # x / z
mflo $t0                  # 4
mult $t0, $s1             # 4 * y
mflo $s3                  # resultado