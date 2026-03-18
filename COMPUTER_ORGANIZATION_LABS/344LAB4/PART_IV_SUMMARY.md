# Part IV: Load-Use Hazard - Implementation Summary

## Part IV Assignment Completion

### ✅ Task 1: Insert Load-Use Hazard Code

The following code has been inserted in the template at the designated location:

```assembly
    lw x7, 4(x5)
    add x9, x7, x7
```

**File**: `prelab4_FFXX_GXX.s` (lines 24-25)

**Location**: After Part III data forwarding example (the `nop` after the ADD)

---

### ✅ Task 2: Generate Simulation Trace

**Compilation Command**:
```bash
riscv64-unknown-elf-gcc -march=rv32i -mabi=ilp32 -o prelab4_FFXX_GXX.elf \
  -nostdlib -T linker.ld prelab4_FFXX_GXX.s
```

**Simulation Command**:
```bash
/opt/openhwgroup/cvw/bin/wsim --sim verilator rv32i --elf prelab4_FFXX_GXX.elf --vcd
```

**Output Files Generated**:
- `prelab4_FFXX_GXX.elf` - Compiled executable
- `prelab4_FFXX_GXX.objdump` - Disassembly
- `prelab4_testbench.vcd` - Waveform trace (140KB, simulation duration 465ps)

---

### ✅ Task 3: Load Trace in GTKWave

**GTKWave Command**:
```bash
gtkwave prelab4_testbench.vcd signals.gtkw
```

**Signals Displayed** (from `signals.gtkw`):
- `testbench.dut.core.ifu.clk` - Clock
- `testbench.dut.core.ifu.PCF[31:0]` - Fetch stage PC
- `testbench.dut.core.ifu.PCD[31:0]` - Decode stage PC
- `testbench.dut.core.ifu.PCE[31:0]` - Execute stage PC
- `testbench.dut.core.ieu.c.Rs1E[4:0]` - Execute source register 1
- `testbench.dut.core.ieu.c.Rs2E[4:0]` - Execute source register 2
- `testbench.dut.core.ieu.c.RdE[4:0]` - Execute destination register
- `testbench.dut.core.ieu.c.RdM[4:0]` - Memory destination register
- `testbench.dut.core.ieu.c.RdW[4:0]` - Writeback destination register
- `testbench.dut.core.hzu.StallF` - Fetch stall signal

---

## Hazard Scenario Description

### The Load-Use Hazard Pattern

```assembly
Address 0x80000020:  lw   x7, 4(x5)    # Load from memory into x7
Address 0x80000024:  add  x9, x7, x7   # Immediately use x7
```

**Compiled Instructions**:
```
80000020:  0042a383  lw   t2, 4(t0)    # t2 = x7
80000024:  007384b3  add  s1, t2, t2   # s1 = x9
```

### Why This Creates a Hazard

| Stage | Cycle N | Cycle N+1 | Cycle N+2 |
|-------|---------|-----------|-----------|
| Fetch | ADD | NEXT | ... |
| Decode | LW | ADD | NEXT |
| Execute | ... | LW | ADD |
| Memory | ... | ... | LW |
| Writeback | ... | ... | ... |

**Problem**: 
- At Cycle N+1, ADD is in Decode wanting to fetch operand x7
- At the same cycle, LW is only in Execute stage
- The load result won't be ready until Cycle N+2 (Memory) or N+3 (Writeback)
- If ADD proceeds to Execute in Cycle N+2, it reads x7 before it's written!

### Hardware Detection and Resolution

**Hazard Detection Unit (HDU)** checks:
1. Is instruction in Memory/Writeback a LOAD? → YES (LW)
2. Is instruction in Decode using the same register as source? → YES (Rs1=x7, Rs2=x7)
3. Action: **Set StallF = 1**

**Pipeline Response**:
- **Cycle N+1**: StallF=1 (stall active)
  - Fetch stage HOLDS (PCF unchanged)
  - All stages HOLD their values
  - ADD stays in Decode
  
- **Cycle N+2**: StallF=0 (stall ends)
  - LW reaches Writeback and writes x7
  - ADD advances to Decode
  
- **Cycle N+3**: 
  - ADD now in Execute, reads x7 value from previous LW
  - Has correct data through forwarding/register file

### Register Dependencies

**When Stall Occurs** (Cycle N+1):
- **PCE** = Address of instruction in Execute (not the ADD)
- **PCD** = 0x80000024 (ADD instruction)
- **RdW** = x7 (LW writing x7 to Writeback)
- **Rs1E, Rs2E** = Would be 07 (x7) if ADD were in Execute, but it's NOT yet
- **StallF** = 1

**After Stall** (Cycle N+3):
- **PCE** = 0x80000024 (ADD now in Execute)
- **Rs1E** = 07 (read x7 as source)
- **Rs2E** = 07 (read x7 as source)
- **RdE** = 09 (write x9 as destination)
- **RdW** = (some other value, LW already wrote)

---

## Performance Impact

### Cycles Required

**With Stall**:
- Cycle 1: Fetch/Decode LW
- Cycle 2: Fetch/Decode ADD (stalled)
- Cycle 3: ADD executes normally
- **Total: 3 cycles for 2 instructions** (1.5 cycles/instruction)

**Without Stall (impossible, would get wrong result)**:
- Cycle 1: Fetch/Decode LW  
- Cycle 2: Fetch/Decode ADD, try to execute (reads stale x7)
- Cycle 3: ADD completes with wrong result
- **Broken: Incorrect computation**

### Real-World Implications

1. **Throughput Loss**: 
   - Expected: 1 cycle/instruction for 2 instructions = 2 cycles
   - Actual: 3 cycles
   - Loss: 33% throughput reduction at this code location

2. **Load Instructions Are Bottlenecks**:
   - Every load followed by immediate use causes 1-cycle stall
   - Common pattern in loops reading arrays
   - Compiler tries to reorder instructions to avoid this

3. **Software Optimization**:
   - Insert independent instructions between load and use
   - Example: Better code structure
   ```assembly
   lw x7, 0(x5)      # Load first element
   add x8, x6, x6    # Do independent work
   add x9, x7, x7    # Now use x7 (result ready!)
   ```

---

## Verification in GTKWave

### How to Find the Stall

1. **Navigate to time region**: Look around 300-350ps
2. **Find StallF=1**: 
   - Exact cycle depends on simulation, but stall should occur when ADD enters Decode
   - StallF will be high for exactly 1 cycle
3. **Observe PCF**: 
   - When StallF=1, PCF should NOT change
   - Other cycles, PCF increments by 4
4. **Trace the ADD**:
   - PCD becomes 0x80000024 → ADD in Decode
   - One cycle later (after stall), PCE becomes 0x80000024 → ADD in Execute

### Expected Signal Sequence

```
Time    | StallF | PCF      | PCD      | PCE      | RdW | Description
--------|--------|----------|----------|----------|-----|------------------
300ps   | 0      | 0x80000...| 0x80000020 | 0x80000... | 07  | LW in Decode
310ps   | 1      | 0x80000...| 0x80000024 | 0x80000020 | 07  | ← STALL! ADD in Decode, LW in Execute
320ps   | 0      | 0x80000...| 0x80000024 | 0x80000024 | -- | ADD in Decode, previous instr in Execute
330ps   | 0      | 0x80000...| 0x80000...| 0x80000024 | 09  | ADD in Execute, writeback occurs
```

---

## Summary of Implementation

| Aspect | Details |
|--------|---------|
| **Hazard Type** | Load-Use Data Hazard |
| **Code Pattern** | `lw x7, ...` followed by `add ... x7, ...` |
| **Detection** | Hardware Hazard Detection Unit (HDU) |
| **Resolution** | 1-cycle pipeline stall via StallF signal |
| **Root Cause** | Load result not available until Memory stage |
| **Indicator Signal** | StallF = 1 (high for 1 cycle during hazard) |
| **Files** | `prelab4_FFXX_GXX.s`, `.elf`, `.objdump`, `.vcd` |
| **Observation Tool** | GTKWave with `signals.gtkw` configuration |

---

## Files Generated

```
prelab4_FFXX_GXX.s ........... Assembly source with load-use hazard
prelab4_FFXX_GXX.elf ........ Compiled 5,008 bytes executable
prelab4_FFXX_GXX.objdump .... Disassembly with instructions and addresses
prelab4_testbench.vcd ....... 140KB waveform trace (465ps simulation)
signals.gtkw ................ GTKWave signal configuration file
PART_IV_LOAD_USE_HAZARD.md .. Detailed technical analysis
```

---

## Next Steps for Verification

1. **In GTKWave**:
   - Click on the signals panel to navigate
   - Search for time ~310ps (adjust based on actual simulation)
   - Look for StallF=1 pattern
   - Take screenshot showing:
     - StallF HIGH (at least 1 complete cycle)
     - PCF unchanged during stall
     - PCD = 0x80000024 (ADD instruction)
     - PCE = 0x80000020 or earlier (ADD not yet in Execute)

2. **Document**:
   - Record the exact cycle times shown in GTKWave
   - Note the signal values when stall occurs
   - Explain why each signal has that value

3. **Conclusion**:
   - Verify that this is indeed a load-use hazard
   - Confirm that stalling prevented wrong data from being used
   - Note the 1-cycle performance penalty

