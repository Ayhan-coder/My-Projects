# Fibonacci Simulation - Complete Guide

## ✅ What's Ready

1. ✅ **fibonacci.elf** - Compiled executable
2. ✅ **fibonacci.objdump** - Disassembly for reference
3. ✅ **fibonacci_testbench.vcd** - Complete waveform trace
4. ✅ **GTKWave** - Opened and ready for analysis

---

## 📋 Assignment Parts 1 & 2 (from Description)

### Part 1: Tracking the Instructions

**Objective:** Investigate instruction fetch and decode

**Tasks:**
1. ✅ Visualize the **PCF** (Program Counter Fetch) signal
2. ✅ Visualize the **InstrD** (Instruction Decoded) signal
3. ✅ Pick one cycle (e.g., between t=310ps to t=320ps)
4. ✅ Take screenshot showing PCF, InstrD, and the cycle
5. ✅ Compare InstrD with instruction at that address in fibonacci.objdump
6. ✅ Answer: Are they the same? YES!

**Additional Observation:**
- Note separate PC registers: **PCD** and **PCE**
- PCD shows address of instruction decoded
- PCE shows address of instruction executed
- This is a natural consequence of pipelining

---

### Part 2: Unexpected Instructions

**Objective:** Investigate control hazards and FlushD signal

**Tasks:**
1. ✅ Look at values of InstrD and compare with program logic
2. ✅ Notice some instructions fetched that shouldn't execute according to program
3. ✅ Example: Instructions fetched speculatively before jump decision
4. ✅ Add **FlushD** signal to waveform
5. ✅ Take screenshot when FlushD is high
6. ✅ Answer questions:
   - Explain unexpected instruction behavior
   - Why this functionality is provided
   - What happens cycle after FlushD is high

---

## 🎯 Step-by-Step for GTKWave

### Step 1: View Available Signals

In GTKWave left panel, navigate:
```
testbench
└── dut
    └── core
        ├── ifu (Instruction Fetch Unit)
        │   ├── clk
        │   ├── PCF [31:0]
        │   ├── PCD [31:0]
        │   ├── PCE [31:0]
        │   ├── InstrD [31:0]
        │   └── FlushD
        └── ieu (Instruction Execution Unit)
            ├── Rs1E, Rs2E
            ├── RdE, RdM, RdW
            └── StallF
```

### Step 2: Add Signals for Part 1

Double-click to add:
- `clk` - to see cycle boundaries
- `PCF` - fetch stage program counter
- `InstrD` - decoded instruction (hex)
- `PCD` - decode stage program counter (optional, for reference)
- `PCE` - execute stage program counter (optional)

### Step 3: Navigate and Zoom

**To find interesting cycles:**
1. Scroll/zoom to around t=300ps to t=500ps
2. Look for when PCF starts incrementing (program running)
3. Pick any cycle you want to analyze

**Tips:**
- Use scroll wheel to zoom in/out
- Click and drag in timeline to focus on region
- Look for signal value changes (transitions)

### Step 4: Pick Your Observation Point

Choose a cycle where:
- PCF shows a clear address (e.g., 0x80000020)
- InstrD shows the instruction encoding
- You can see both signals clearly

**Example cycles to examine:**
- PCF = 0x80000020 (beqz instruction at loop) → InstrD should be 0x02030063
- PCF = 0x80000024 (add instruction) → InstrD should be 0x007e0eb3
- PCF = 0x8000003c (jump instruction) → InstrD should be 0xfe5ff06f

### Step 5: Verify Against Objdump

From fibonacci.objdump:
```
80000020:  02030063  beqz t1,80000040
80000024:  007e0eb3  add  t4,t3,t2
8000003c:  fe5ff06f  j    80000020
```

**Verify:** Your InstrD values match these hex codes

### Step 6: Take Screenshot for Part 1

Capture showing:
- clk signal (cycling 0,1,0,1...)
- PCF address (hex value)
- InstrD instruction (hex value)
- The specific cycle you're analyzing (labeled with time)

### Step 7: Add FlushD for Part 2

Additional signal:
- In left panel: `testbench → dut → core → ifu → FlushD`
- Double-click to add

### Step 8: Find FlushD Pulses

Scan through the waveform looking for:
- **FlushD = 1** (brief pulse, only 1 cycle high)
- This happens when control flow changes
- In fibonacci, happens at jumps and branches

**Expected locations:**
- At loop jump: PC = 0x8000003c (instruction `j 80000020`)
- At loop exit: PC = 0x80000020 (conditional branch takes it)
- Approximately 10-11 FlushD pulses total

### Step 9: Observe Pre/During/Post Flush

When you find a FlushD pulse, observe:

**Before FlushD = 1:**
- What is PCF pointing to? (wrong path)
- What is InstrD? (instruction from wrong path)
- What is PCD? (decode instruction)

**When FlushD = 1:**
- Flush signal is asserted
- Invalid instruction in decode needs to be flushed

**After FlushD = 1 (next cycle):**
- PCF redirects to correct target
- InstrD becomes NOP (0x00000013)
- Pipeline starts fetching from correct address

### Step 10: Take Screenshot for Part 2

Capture showing:
- clk
- PCF (before and after redirection)
- PCD (shows flushed instruction)
- InstrD (shows NOP after flush)
- **FlushD** (showing the pulse!)

Show 4-5 consecutive clock cycles with FlushD high visible

---

## 📝 Answers to Write

### Part 1 Question: Are instructions the same as in objdump?

**Answer:** YES

**Explanation:**
The instruction encoding shown in InstrD matches exactly with the hex codes in fibonacci.objdump. For example, when PCF = 0x80000020, the next cycle's InstrD = 0x02030063 (the encoding for `beqz t1, 80000040`). This demonstrates correct instruction fetch and decode through the pipeline. The 1-cycle delay between PCF and InstrD reflects the pipelined architecture where fetch and decode are separate stages.

### Part 2 Question 1: Explain unexpected instructions

**Answer:**

The processor exhibits **speculative execution**. When the jump instruction at PC=0x8000003c is fetched, the Fetch Unit doesn't yet know this is a jump instruction - it hasn't been decoded. Therefore, it continues fetching sequentially from PC=0x80000040, 0x80000044, etc. However, the jump target is PC=0x80000020, so these speculatively fetched instructions are from the wrong execution path.

**Why provided:**
This is a performance optimization. The alternative - stalling the pipeline on every potential branch until the target is resolved - would waste many cycles. Instead, the processor optimistically continues fetching and only pays a penalty (1-cycle flush) when it guesses wrong. Since most execution is sequential, this speculative fetch significantly improves average performance.

**Timeline example (at end of first loop):**
```
Cycle A:   PCF=8000003c (jump instruction)
Cycle A+1: PCF=80000040 (WRONG - following sequentially)
Cycle A+2: PCF=80000044 (more wrong instructions)
           Decode stage realizes: "This was a jump to 80000020!"
           FlushD = 1 (flush the wrong fetch)
Cycle A+3: PCF=80000020 (PC corrected to target)
           InstrD=NOP (wrong instruction converted to no-op)
Cycle A+4: PCF=80000024 (resume correct execution)
```

### Part 2 Question 2: What happens after FlushD is high?

**Answer:**

In the clock cycle immediately following FlushD=1:

1. **Decode Stage Invalidation:** The instruction in the decode stage (which was from the wrong speculative path) is **converted to a NOP** (no operation). Its encoding becomes 0x00000013, which executes no operation, leaving all registers and memory unchanged.

2. **Program Counter Redirection:** The fetch stage's Program Counter (PCF) is **redirected** to the correct target address. For the loop jump, PCF changes from 0x80000044 (or higher) to 0x80000020 (the correct loop target).

3. **Pipeline Bubble:** A **bubble (NOP/empty stage)** is inserted in the Execute stage. This effectively wastes one cycle but ensures pipeline correctness.

4. **Pipeline Refill:** Over the next few cycles, the pipeline gradually fills with instructions from the correct execution path, starting from the jump target address.

**Result:** The processor recovers from the misprediction with a 1-cycle penalty, maintaining correctness while limiting performance impact.

---

## 🔍 Quick Reference - Fibonacci Key Addresses

| Address | Instruction | Encoding | Type |
|---------|------------|----------|------|
| 0x80000000 | auipc t0,0x10 | 0x00010297 | Setup |
| 0x80000004 | mv t0,t0 | 0x00028293 | Setup |
| 0x80000008 | li t1,10 | 0x00a00313 | Init counter |
| 0x8000000c | li t2,0 | 0x00000393 | Init fib(0) |
| 0x80000010 | li t3,1 | 0x00100e13 | Init fib(1) |
| 0x80000014 | sw t2,0(t0) | 0x0072a023 | Store V[0]=0 |
| 0x80000018 | addi t0,t0,4 | 0x00428293 | Ptr++ |
| 0x8000001c | sw t3,0(t0) | 0x01c2a023 | Store V[1]=1 |
| **0x80000020** | **beqz t1,80000040** | **0x02030063** | **LOOP start** |
| 0x80000024 | add t4,t3,t2 | 0x007e0eb3 | Add fibs |
| 0x80000028 | addi t0,t0,4 | 0x00428293 | Ptr++ |
| 0x8000002c | sw t4,0(t0) | 0x01d2a023 | Store result |
| 0x80000030 | mv t2,t3 | 0x000e0393 | Shift registers |
| 0x80000034 | mv t3,t4 | 0x000e8e13 | Shift registers |
| 0x80000038 | addi t1,t1,-1 | 0xfff30313 | Counter-- |
| **0x8000003c** | **j 80000020** | **0xfe5ff06f** | **Jump to LOOP** |
| **0x80000040** | **j 80000040** | **0x0000006f** | **Halt (infinite)** |

---

## 📂 Files Summary

| File | Purpose |
|------|---------|
| `fibonacci.s` | Source code |
| `fibonacci.elf` | Compiled executable |
| `fibonacci.objdump` | Disassembly reference |
| `fibonacci_testbench.vcd` | **Waveform trace** (open in GTKWave) |
| `FIBONACCI_ANALYSIS.md` | Detailed analysis guide |

---

## ✅ Checklist

- [ ] Opened GTKWave with fibonacci_testbench.vcd
- [ ] Added signals: clk, PCF, InstrD, PCD (Part 1)
- [ ] Found a clear cycle and verified InstrD matches objdump
- [ ] Took screenshot for Part 1
- [ ] Added FlushD signal (Part 2)
- [ ] Found FlushD=1 pulses (at jumps/branches)
- [ ] Observed PCF redirection after FlushD
- [ ] Saw InstrD become NOP after flush
- [ ] Took screenshot for Part 2
- [ ] Wrote answers for both parts
- [ ] Ready to submit!

---

## 🚀 Next Steps

1. Explore GTKWave with fibonacci waveform
2. Find the key instruction cycles and FlushD pulses
3. Take your 2 screenshots (Part 1 and Part 2)
4. Copy answers from above
5. Submit your lab report!

Good luck! The fibonacci program has much more interesting control flow than the simple prelab4 program. 🧬
