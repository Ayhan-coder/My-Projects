.globl _start

#.section .bss

.section .data
    arr: .word 1111, 2222, 3333, 4444, 5555, 6666
.section .text

_start:
    la x5, arr
    nop
    nop
    nop
    lw x6, 0(x5)
    nop
    add x8, x6, x6

################################################################################# 
# DO NOT EDIT ABOVE THIS LINE.

 
    lw x7, 4(x5)
    add x9, x7, x7

# DO NOT EDIT BELOW THIS LINE.
################################################################################# 
    j END

END:    
    li   a7, 10       
    j .
