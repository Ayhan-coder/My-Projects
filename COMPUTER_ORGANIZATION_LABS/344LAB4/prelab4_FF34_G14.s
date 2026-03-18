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

    # Load-Use Hazard Implementation
    # Load a value from memory into x7
    lw x7, 4(x5)
    # Immediately use x7 in the next instruction - this creates a load-use hazard
    # The add instruction needs x7's value, but lw hasn't completed the memory access yet
    add x9, x7, x7

# DO NOT EDIT BELOW THIS LINE.
################################################################################# 
    j END

END:    
    li   a7, 10       
    j .
