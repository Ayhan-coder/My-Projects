## How Your Instructor Will Likely Test Your Assembly Program

### Method 1: Memory Inspection After Execution ⭐ (Most Likely)
Your instructor will probably:
1. Assemble and link your code
2. Run it in a RISC-V simulator (spike, QEMU, or custom testbench)
3. **Inspect memory locations** after execution:
   - `distance_traveled` (at .bss section, offset 0)
   - `flight_history` (at .bss section, offset 4-67, 64 bytes)
   - `history_len` (at .bss section, offset 68)
   - `current_fuel` (at .data section)
   - `airport_supply` (at .data section)
   - `current_airport` (at .data section)

Expected values in memory:
- distance_traveled: 97564 (0x17D4C in hex)
- flight_history: [5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1] (27 bytes)
- history_len: 27 (0x1B in hex)
- current_fuel: 1804 (0x70C in hex)
- current_airport: 1 (Hong Kong)

### Method 2: Automated Test Script
They might use a script that:
```bash
# Assemble
riscv64-unknown-elf-as -march=rv32i -mabi=ilp32 -o 1.o 1.s

# Link
riscv64-unknown-elf-ld -m elf32lriscv -o 1.elf 1.o -T linker.ld

# Run in simulator with memory dump
spike --isa=rv32i --debug 1.elf < commands.txt

# Extract and verify memory contents
riscv64-unknown-elf-objdump -D 1.elf
```

### Method 3: Custom RISC-V Testbench
They may have a custom testing environment that:
- Loads your program
- Runs it cycle-by-cycle
- Monitors memory writes
- Checks final state against expected values

### Method 4: Debugger Inspection
Using spike's interactive debugger:
```bash
spike --isa=rv32i -d 1.elf
```
Then manually step through or set breakpoints.

### Method 5: Modified Linker Script with Output
They might provide a special linker script that maps certain memory addresses
to output devices, so your program automatically displays results.

### Method 6: Function-by-Function Testing
They might test individual functions:
- Call `flight_navigation` with specific inputs, check return value
- Call `refuel` and verify fuel updates
- Call `execute_flight` and verify state changes

---

## What Your Instructor Is Checking For:

### Correctness (Most Important)
✓ Correct flight path: 5→6→7→8→9→0→1→2→3→4→5→6→7→8→9→0→1→2→3→4→5→6→7→8→9→0→1
✓ Total distance: 97,564 km
✓ Final location: Hong Kong (index 1)
✓ Final fuel: 1,804
✓ Correct fuel consumption calculations
✓ Correct airport supply depletion

### Algorithm Implementation
✓ flight_navigation finds closest westward reachable airport
✓ refuel properly updates fuel and airport supply
✓ execute_flight correctly updates all state variables
✓ Main loop terminates when no westward route available

### Code Quality
✓ Proper use of RISC-V RV32I instructions
✓ No use of multiplication instruction (MUL10 macro instead)
✓ Correct stack management (save/restore registers)
✓ Proper calling convention (a0-a7 for args, s0-s11 saved)
✓ Comments and documentation

### Edge Cases
✓ Handles airport with zero fuel supply
✓ Handles when fuel capacity is already full
✓ Doesn't crash on boundary conditions
✓ Loop termination condition works correctly

---

## What You Should Verify:

1. **Your program assembles without errors**
   ```bash
   /opt/riscv/bin/riscv64-unknown-elf-as -march=rv32i -mabi=ilp32 -o 1.o 1.s
   ```

2. **Your program links without errors**
   ```bash
   /opt/riscv/bin/riscv64-unknown-elf-ld -m elf32lriscv -o 1.elf 1.o -T linker.ld
   ```

3. **Check for any warnings**
   ```bash
   /opt/riscv/bin/riscv64-unknown-elf-objdump -d 1.elf | less
   ```

4. **Verify data section alignment**
   ```bash
   /opt/riscv/bin/riscv64-unknown-elf-objdump -h 1.elf
   ```

5. **Trust your Python simulation** - it matches the expected output!

---

## Recommendation:

Your code is well-structured and documented. The Python test confirms it 
produces the correct output. Your instructor will most likely:

1. Run your program in their testing environment
2. Dump memory after execution
3. Compare against expected values
4. Grade based on correctness + code quality

**You should be good to go!** ✓
