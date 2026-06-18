#!/usr/bin/env python3
"""
Verify the assembly code output by examining the ELF file's data sections.
We'll use objdump to extract the final state.
"""

import subprocess
import struct

def run_objdump(elf_file, section):
    """Run objdump to get section contents."""
    try:
        result = subprocess.run(
            ['/opt/riscv/bin/riscv64-unknown-elf-objdump', '-s', '-j', section, elf_file],
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception as e:
        print(f"Error running objdump: {e}")
        return ""

def parse_hex_dump(dump_output):
    """Parse objdump hex output into bytes."""
    data = []
    for line in dump_output.split('\n'):
        # Skip header lines
        if 'Contents of section' in line or 'file format' in line or not line.strip():
            continue
        # Parse hex dump lines like: " 80010000 00004e20 28420000 e0030000 ..."
        parts = line.split()
        if len(parts) < 2:
            continue
        # Skip the address part
        hex_values = parts[1:]
        for hex_val in hex_values:
            # Each hex_val is 4 bytes in hex (8 characters)
            if len(hex_val) == 8:
                try:
                    # Convert to bytes (little-endian)
                    bytes_data = bytes.fromhex(hex_val)
                    data.extend(bytes_data)
                except:
                    pass
    return bytes(data)

print("=== Verifying Assembly Code Output ===")
print()

# First, let's see what sections are available
print("Available sections in 1.elf:")
result = subprocess.run(
    ['/opt/riscv/bin/riscv64-unknown-elf-objdump', '-h', '1.elf'],
    capture_output=True,
    text=True
)
print(result.stdout)

print("\n=== Attempting to extract runtime data ===")
print("Note: Without running the program, we can only see initial data values.")
print("The assembly code needs to be executed to see final results.")
print()

# Try to dump the .data section (initial values)
data_dump = run_objdump('1.elf', '.data')
if data_dump:
    print("Initial .data section:")
    print(data_dump)

# Try to dump the .bss section
bss_dump = run_objdump('1.elf', '.bss')
if bss_dump:
    print("\nInitial .bss section:")
    print(bss_dump)

print("\n" + "="*60)
print("CONCLUSION:")
print("="*60)
print("To verify the assembly code produces the same result,")
print("we need to either:")
print("1. Add debug output to the assembly (print statements)")
print("2. Use a debugger to examine memory after execution")
print("3. Modify the code to write results to a file")
print("4. Use spike's interactive debugger")
print()
print("Let's try running with spike's debug mode...")
