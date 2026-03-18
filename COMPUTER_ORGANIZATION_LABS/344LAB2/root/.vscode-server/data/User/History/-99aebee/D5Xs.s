# This script is designed to test the assembly code in `1.s`.
# It assumes that you have a RISC-V toolchain installed (e.g., `riscv64-unknown-elf-gcc` and `spike` for simulation).

# Step 1: Assemble the code
riscv64-unknown-elf-as -o 1.o 1.s

# Step 2: Link the object file
riscv64-unknown-elf-ld -o 1.elf 1.o -T linker.ld

# Step 3: Run the program in a RISC-V simulator (e.g., Spike)
spike pk 1.elf

# Step 4: Check the output
# You can use `spike`'s debug features or add print statements in the assembly code to verify behavior.

# Note: Ensure that the `linker.ld` file is correctly configured for your environment.