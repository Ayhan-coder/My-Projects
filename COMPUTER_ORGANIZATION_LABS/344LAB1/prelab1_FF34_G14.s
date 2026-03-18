.data
    secret_code: .word 517, 1863, 4174, 1705, 456, 2025, 0
    key:         .word 17

.text

.globl _start

_start:
    # Load addresses and values to registers
    la t0, secret_code         
    la t1, key
    lw t1, 0(t1)               # t1 = 17
    
# DO NOT EDIT ABOVE THIS LINE.         


    li      t2, 0                 
    li      t6, 0                

loop:
    slli    t3, t2, 2             
    add     t4, t0, t3            
    lw      t5, 0(t4)             
    beq     t5, x0, done         

  
    li      a2, 10
    li      a3, 0                 
    mv      a0, t5                 

check_pair:
    blt     a0, a2, check_done     
    rem     a1, a0, a2
    div     a4, a0, a2
    rem     a5, a4, a2
    li      a6, 10
    mul     a5, a5, a6
    add     a5, a5, a1

    beq     a5, t1, found_match   

    mv      a0, a4                 
    j       check_pair

found_match:
    li      a3, 1                 

check_done:
    beq     a3, x0, no_transform   
    mul     t5, t5, t2
    sw      t5, 0(t4)              

no_transform:
    add     t6, t6, t5             
    addi    t2, t2, 1            
    j       loop


done:
    j       end



# DO NOT EDIT BELOW THIS LINE.      

end: 
    # t6 should have the final decoded value
    li a7, 10
    ecall

