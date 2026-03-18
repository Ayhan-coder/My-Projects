#!/bin/bash
# Test script for the RISC-V assembly flight navigation program

set -e  # Exit on error

echo "=== RISC-V Flight Navigation Program Test ==="
echo ""

# Step 1: Assemble the code
echo "[1/3] Assembling 1.s..."
/opt/riscv/bin/riscv64-unknown-elf-as -march=rv32i -mabi=ilp32 -o 1.o 1.s
echo "✓ Assembly successful"

# Step 2: Link the object file
echo "[2/3] Linking object file..."
/opt/riscv/bin/riscv64-unknown-elf-ld -m elf32lriscv -o 1.elf 1.o -T linker.ld
echo "✓ Linking successful"

# Step 3: Run the program in spike simulator (bare metal mode)
echo "[3/3] Running program in Spike simulator..."
echo ""
spike --isa=rv32i /opt/riscv/riscv32-unknown-elf/bin/pk 1.elf
EXIT_CODE=$?

echo ""
echo "=== Program exited with code: $EXIT_CODE ==="

# Step 4: Display file info
echo ""
echo "=== Binary Information ==="
/opt/riscv/bin/riscv64-unknown-elf-objdump -h 1.elf | head -20

echo ""
echo "=== Test Complete ==="