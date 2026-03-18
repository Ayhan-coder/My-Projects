# Fibonacci Program Analysis - Parts 1 & 2

## Program Overview

Your fibonacci.s program computes the first 12 Fibonacci numbers (0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89) and stores them in array `V`.

---

## Part 1: Tracking the Instructions (with Fibonacci)

### Program Structure

```
_start:                          # PC 0x80000000
  la  t0, V                      # PC 0x80000000-0x80000004
  li  t1, N-2 (10)               # PC 0x80000008
  li  t2, 0                      # PC 0x8000000c
  li  t3, 1                      # PC 0x80000010
  sw  t2, 0(t0)                  # PC 0x80000014 - Store 0
  addi t0, t0, 4                 # PC 0x80000018
  sw  t3, 0(t0)                  # PC 0x8000001c - Store 1

LOOP:                            # PC 0x80000020
  beqz t1, DONE                  # PC 0x80000020 - Branch if done
  add  t4, t3, t2                # PC 0x80000024 - Add: t4 = t3 + t2
  addi t0, t0, 4                 # PC 0x80000028 - Increment pointer
  sw   t4, 0(t0)                 # PC 0x8000002c - Store result
  mv   t2, t3                    # PC 0x80000030 - t2 = t3
  mv   t3, t4                    # PC 0x80000034 - t3 = t4
  addi t1, t1, -1                # PC 0x80000038 - Decrement counter
  j    LOOP                      # PC 0x8000003c - Jump back

DONE:                            # PC 0x80000040
  j    DONE                      # PC 0x80000040 - Infinite loop (halt)
```

### What to Do in GTKWave

#### Step 1: Open GTKWave with Fibonacci VCD
```bash
& "C:\iverilog\gtkwave\bin\gtkwave.exe" fibonacci_testbench.vcd
```

#### Step 2: Add Key Signals
Navigate and add:
- testbench → dut → core → ifu → clk
- testbench → dut → core → ifu → PCF (Program Counter Fetch)
- testbench → dut → core → ifu → PCD (Program Counter Decode)  
- testbench → dut → core → ifu → PCE (Program Counter Execute)
- testbench → dut → core → ifu → InstrD (Instruction Decode - hex)

#### Step 3: Find Instruction Fetch/Decode Events

Pick a cycle around **t=300ps to t=400ps** and observe:
- **PCF**: Address of instruction being fetched (should increment by 4)
- **InstrD**: Hex encoding of instruction in decode stage
- **PCD**: Should equal previous cycle's PCF (1-cycle delay)

#### Step 4: Verify Against Objdump

For any cycle you pick, verify:
- If PCF = 0x80000020, then InstrD should = 0x02030063 (beqz instruction)
- If PCF = 0x80000024, then InstrD should = 0x007e0eb3 (add instruction)
- And so on...

### Key Observations for Part 1

**Sequential Execution Example:**
```
Cycle N:   PCF=80000000, InstrD=?, PCD=?
Cycle N+1: PCF=80000004, InstrD=0x00010297, PCD=80000000
Cycle N+2: PCF=80000008, InstrD=0x00028293, PCD=80000004
Cycle N+3: PCF=8000000c, InstrD=0x00a00313, PCD=80000008
...
Cycle M:   PCF=80000020, InstrD=0x02030063 (beqz - branch to LOOP)
```

**Pipeline Delay:**
- Notice that PCD lags behind PCF by 1 cycle
- This is the fetch → decode pipeline stage

### Answer for Part 1

**Q: Are the instructions being fetched the same as shown in the disassembly?**

**A: YES**

The hex encoding shown in `InstrD` at any cycle matches exactly with the instruction at that PC address in `fibonacci.objdump`. For example:
- At PC 0x80000020, the instruction is `beqz t1, 80000040` which encodes to `02030063`
- When PCF=0x80000020 (fetch stage), one cycle later PCD=0x80000020 (decode stage), and InstrD will show `0x02030063`

This confirms that the RTL simulator is correctly implementing instruction fetch and decode, and the pipelining introduces a predictable 1-cycle delay between stages.

---

## Part 2: Unexpected Instructions (Control Hazards)

### Program Control Flow

The fibonacci program has several control flow changes:

1. **Beqz instruction** (PC=0x80000020): Branch if counter equals zero
   - Loop condition: if t1==0, jump to DONE (PC=0x80000040)
   - Otherwise, continue to next instruction (PC=0x80000024)

2. **Jump instruction** (PC=0x8000003c): Unconditional jump back to LOOP
   - Always jumps to PC=0x80000020

3. **Infinite loop** (PC=0x80000040): Jump to itself (halt)
   - j 80000040 → always jumps to 80000040

### What to Do in GTKWave for Part 2

#### Step 1: Add FlushD Signal
- In left panel: testbench → dut → core → ifu → **FlushD**
- Double-click to add to waveform

#### Step 2: Find Branch/Jump Events

Look for when **FlushD = 1** (goes high):

**Event 1: The Loop Jump (most important)**
- Instruction at PC=0x8000003c: `j 80000020` (unconditional jump back to loop)
- This happens multiple times (once per loop iteration)
- Each time, FlushD should pulse

**Event 2: Exit from Loop**
- When counter reaches 0, `beqz t1, DONE` takes the branch
- Jump target is PC=0x80000040
- This causes a FlushD pulse

**Event 3: Infinite Loop**
- At PC=0x80000040: `j 80000040` (jump to itself)
- May or may not cause flush depending on implementation

#### Step 3: Trace Unexpected Instructions

Before a flush happens, you'll see instructions fetched that don't match the correct program flow:

**Example: At the end of first loop iteration**
```
Cycle A:   PCF=8000003c, InstrD=?, PCD=80000038
           (Fetching jump instruction)

Cycle A+1: PCF=80000040, InstrD=fe5ff06f (the jump), PCD=8000003c
           (Jump decoded, but fetch already moved to 80000040)
           (This is WRONG - should fetch 80000020)

Cycle A+2: PCF=80000044?, InstrD=0000006f, PCD=80000040
           **FlushD=1** ← Flush detected!
           (Instruction at 80000044 is unexpected)

Cycle A+3: PCF=80000020, InstrD=00000013?, PCD=80000040
           (PC corrected to 80000020, decode flush shows as NOP)
```

#### Step 4: Take Screenshot

Show:
- ✓ clk (clock signal)
- ✓ PCF (shows speculative fetch, then redirect)
- ✓ PCD (shows the unexpected instruction)
- ✓ InstrD (shows what was fetched before flush)
- ✓ **FlushD = 1** ← Critical signal showing the flush event

Zoom to show **4-5 clock cycles around a FlushD pulse**

### Answer for Part 2

**Q1: Explain the unexpected instruction behavior and why this functionality is provided**

**A1:**

The processor exhibits speculative execution: when fetching the jump instruction at PC=0x8000003c, it doesn't immediately know this is a jump. The Fetch Unit continues sequentially, fetching from PC=0x80000040 (and possibly beyond). However, the jump target is PC=0x80000020, so the instructions fetched from 0x80000040+ are on the wrong path.

**Why:** This is a **performance optimization**. Rather than stall every time a branch/jump is encountered (waiting for decode → execute → jump target calculation), the processor optimistically continues fetching sequentially. Only when wrong, it flushes and redirects.

**Example timeline for fibonacci loop jump:**
```
Fetch 8000003c: j 80000020 (jump instruction)
Fetch 80000040: (wrong - should jump to 80000020)
Fetch 80000044: (more wrong instructions)
Decode 8000003c: Jump! Target = 80000020
Flush! Invalidate 80000040, 80000044, etc.
Redirect PCF to 80000020
```

**Q2: What happens right after FlushD is high?**

**A2:**

In the clock cycle immediately after FlushD=1:

1. **Decode Stage:** The instruction in decode (which was from the wrong path) is **converted to a NOP** (no operation). The instruction encoding becomes 0x00000013 (RISC-V NOP).

2. **Fetch Stage:** The Program Counter (PCF) is **redirected** to the correct target address. For the loop jump, PCF redirects from 0x80000040 to 0x80000020.

3. **Execute Stage:** A **bubble/NOP** is inserted. One cycle of execution time is wasted but correctness is preserved.

4. **Pipeline Refill:** Over the next few cycles, the pipeline fills with instructions from the correct path (starting from the jump target at 0x80000020).

**Result:** The processor recovers from the mispredicted path with only a 1-cycle penalty, maintaining correctness while providing reasonable performance.

---

## Expected Waveform Behavior

### Fibonacci Loop Iterations

The fibonacci program executes the loop 10 times (N-2 where N=12):

```
Iteration 1: V[0]=0, V[1]=1, V[2]=1
Iteration 2: V[0]=0, V[1]=1, V[2]=1, V[3]=2
Iteration 3: V[0]=0, V[1]=1, V[2]=1, V[3]=2, V[4]=3
...
Iteration 10: V[0-11] contains all 12 Fibonacci numbers
```

Each loop iteration:
1. Adds t3 + t2 → stores in V[i]
2. Shifts registers (t2=t3, t3=t4)
3. Decrements counter (t1--)
4. Jumps back to LOOP (causes flush event)

### FlushD Pulse Pattern

You should see approximately **10 FlushD pulses** (one per loop iteration), where each pulse corresponds to the jump instruction redirecting back to LOOP.

Plus potentially:
- 1 FlushD when exiting loop (beqz takes branch)
- Possibly 1 more at infinite loop (depending on implementation)

---

## Navigation Tips for Fibonacci VCD

1. **Finding the main loop:** Look for repeating patterns in PCF (~every 40-50 cycles)
2. **Finding first FlushD:** Scan through and look for signal transitions on FlushD (0→1)
3. **Loop jump location:** PC=0x8000003c (fe5ff06f instruction)
4. **Branch instruction:** PC=0x80000020 (02030063 - beqz)
5. **Total execution:** Program runs for much longer than prelab4 (due to loop iterations)

---

## Files Available

- `fibonacci.elf` - Compiled program
- `fibonacci.objdump` - Disassembly (reference)
- `fibonacci_testbench.vcd` - Waveform trace (open in GTKWave)
- `fibonacci.s` - Source code

Open GTKWave with:
```bash
& "C:\iverilog\gtkwave\bin\gtkwave.exe" fibonacci_testbench.vcd
```

---

Good luck analyzing the fibonacci waveforms! The control flow is much more interesting than the prelab4 program. 🧬
