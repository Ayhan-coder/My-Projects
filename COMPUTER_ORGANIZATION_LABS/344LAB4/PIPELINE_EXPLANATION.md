# Understanding the Objdump vs GTKWave Mismatch

## The Most Important Thing to Understand: PIPELINE DELAY

The Wally processor is a **5-stage pipeline**:
1. **Fetch (F):** Get instruction from memory
2. **Decode (D):** Decode instruction  
3. **Execute (E):** Execute ALU operation
4. **Memory (M):** Load/Store memory
5. **Writeback (W):** Write result back

---

## How Signals Relate to Pipeline Stages

```
Stage       | Signal Name | What It Means
------------|-------------|-----------------------------------------------
Fetch       | PCF         | Address of instruction CURRENTLY being fetched
Decode      | PCD, InstrD | Address/Encoding of instruction CURRENTLY decoded
Execute     | PCE         | Address of instruction CURRENTLY executing
Memory      | (stored)    | Address of instruction in memory stage
Writeback   | RdW, RdM    | Register being written BACK now
```

---

## The Key Insight: InstrD LAGS PCF by ONE CYCLE

### What This Means:

When you look at GTKWave at time T:

**PCF** = Address being FETCHED RIGHT NOW (at time T)
**InstrD** = Instruction that was FETCHED LAST CYCLE (from time T-1)

### Example:

```
Time T-1 cycle:  PCF = 0x80000024  (fetching "add t4,t3,t2")
                 Instruction 0x007e0eb3 gets fetched

Time T cycle:    PCF = 0x80000028  (fetching "addi t0,t0,4")
                 InstrD = 0x007e0eb3  (the instruction from T-1!)
```

**So InstrD should match the INSTRUCTION AT (PCF - 4), not PCF itself!**

---

## Step-by-Step Verification:

### At time T in GTKWave:

1. **Read PCF value** (let's say PCF = 0x80000028)

2. **Read InstrD value** (let's say InstrD = 0x007e0eb3)

3. **Go back one instruction in objdump:**
   - PCF = 0x80000028 → previous instruction at 0x80000024
   - Look up 0x80000024 in objdump
   - Should see: `add t4,t3,t2` with encoding `0x007e0eb3`

4. **Compare:**
   - InstrD from GTKWave = 0x007e0eb3 ✓ MATCHES!

---

## Why This Happens (Technical):

```
The processor needs time to fetch and decode an instruction:

Cycle N:
  - Fetch stage: Reads instruction from memory at address PCF
  - Output: 32-bit instruction word
  - This goes into a PIPELINE REGISTER

Cycle N+1:
  - Decode stage: Reads from pipeline register (still has old data)
  - Fetch stage: Has already moved on to fetch NEXT instruction at PCF+4
  - Output: InstrD shows what decode is currently working on (from cycle N)

Result: InstrD is ALWAYS one cycle behind PCF!
```

---

## The OBJDUMP Should ALWAYS Match

The question in Part 1 asks: **"Are the instructions the same?"**

**Answer: YES, they are the same!**

Because:
1. InstrD is the actual instruction being decoded
2. It came from memory at some earlier address
3. That address and instruction are in objdump
4. When you account for the 1-cycle delay, they match perfectly

---

## If You See a Mismatch:

### Scenario A: InstrD doesn't match instruction at (PCF - 4)

**Possible causes:**
1. Waveform corrupted - re-run simulation
2. Wrong signal selected - verify full path in GTKWave
3. Display format wrong - right-click → Data Format → Hexadecimal

### Scenario B: Pattern doesn't make sense

**Check these:**
1. Is PCF incrementing by 4 each cycle? (Normal sequential)
2. Does PCF sometimes NOT increment? (Could be a stall from hazard)
3. Does PCF jump around? (Branches/jumps causing FlushD)
4. Is simulation complete? (File size should be ~140KB)

### Scenario C: Seeing mostly zeros

**Likely issue:**
- You're looking at the END of the program where it's halted
- Navigate to earlier times (t=300ps to t=600ps) to see activity
- Or scroll LEFT in GTKWave timeline

---

## The Bottom Line

✅ **InstrD and Objdump WILL match when you account for pipeline delay**

The pipeline delay is **EXPECTED** and **CORRECT**.

If you're seeing a mismatch:
1. Double-check you're comparing the right instruction (PCF-4, not PCF)
2. Verify data format is Hexadecimal
3. Confirm you're looking at the right signal (from ifu module)
4. Re-run simulation if still stuck

---

## Quick Checklist for Debugging:

- [ ] PCF shows address in hex (0x80000000 format)
- [ ] InstrD shows instruction in hex (0x007e0eb3 format)
- [ ] InstrD matches objdump at address (PCF - 4)
- [ ] PCF increments by 4 between cycles (most of the time)
- [ ] Signal data format is set to Hexadecimal
- [ ] Full signal path is: testbench.dut.core.ifu.InstrD
- [ ] Waveform file is complete (~140KB)

---

## If You're Still Stuck:

Tell me:
1. **What time in GTKWave** (e.g., t=350ps)
2. **What PCF shows** (e.g., 0x80000028)
3. **What InstrD shows** (e.g., 0x00428293)
4. **What you EXPECTED** (based on objdump)

Then I can immediately tell you what's happening! 🔍

