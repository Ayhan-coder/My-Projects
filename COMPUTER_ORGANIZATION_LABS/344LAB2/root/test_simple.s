.global _start

# Simple test - just set some values and exit
_start:
    li      a0, 42          # Set exit code to 42
    li      a7, 93          # SYS_exit syscall number
    ecall                   # Exit
