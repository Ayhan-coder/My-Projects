# Part III & IV - Step-by-Step Guide

## Part III: Data Hazard (Understanding Forwarding)

### Background:
The observation in Part III shows that at t=290ps (or similar cycle):
- Instruction at PC=8000001C is `add x8, x6, x6` (in Execute stage)
- This instruction uses x6 as source: `Rs1E=06`, `Rs2E=06`
- But x6 is also being written in Writeback: `RdW=06`

**Question:** How can x6 be used (read) and written at the same time?

---

### What to Do in GTKWave for Part III:

#### □ Step 1: Find the Observation Point
Navigate to around **t=290ps to t=320ps** in the waveform:
- The signals should already be visible from `signals.gtkw`
- You should see: PCF, PCD, PCE, Rs1E, Rs2E, RdE, RdM, RdW, StallF

#### □ Step 2: Identify the Specific Cycle
Look for when:
- `PCE = 8000001C` (the add instruction is executing)
- `Rs1E = 06` and `Rs2E = 06` (reading x6)
- `RdW = 06` (writing to x6 in Writeback)
- This is around the 3rd clock cycle shown

#### □ Step 3: Observe the Signals
Note the values:
```
PCE = 8000001C  → add x8, x6, x6 in Execute
Rs1E = 06       → needs x6
Rs2E = 06       → needs x6
RdW = 06        → x6 being written in Writeback
```

#### □ Step 4: Take Screenshot (Optional)
If required, capture showing the simultaneous read/write dependency

---

### Answer to Write:

**Question: How can a register whose value is about to change in Writeback be used in Execute?**

**Answer: Data Forwarding (Bypassing)**

The processor uses **data forwarding** (also called **bypassing**), a hardware mechanism that allows the result of an instruction to be used by a subsequent instruction before it's written back to the register file.

**How It Works:**

1. **Bypass Paths:** 
   - Physical wires (multiplexers) route values from later pipeline stages back to the ALU inputs in the Execute stage
   - Memory→Execute forwarding: `RdM` value forwarded
   - Writeback→Execute forwarding: `RdW` value forwarded

2. **Hazard Detection:**
   - The Hazard Unit compares source registers (`Rs1E`, `Rs2E`) with destination registers (`RdM`, `RdW`)
   - If `Rs1E == RdW == 0x06`, forwarding is activated

3. **Value Selection:**
   - Multiplexers select the forwarded value instead of the stale register file value
   - The ALU receives the correct (most recent) value

4. **Result:**
   - Even though x6 hasn't been written to the register file yet, the `add` instruction gets the correct value
   - No stall needed - execution continues at full speed!

**Why This Matters:**
- Without forwarding: would need 2 NOPs after every data-producing instruction (30-40% slower)
- With forwarding: most data hazards resolved with zero stall penalty
- Essential for pipeline performance

**Exception:** Load instructions (covered in Part IV) still need 1-cycle stall because memory data arrives too late even for forwarding.

---

## Part IV: Load-Use Hazard Implementation

### What I Implemented:

In your `prelab4_FFXX_GXX.s`, I added:
```assembly
lw  x7, 4(x5)      # Load from memory into x7
add x9, x7, x7     # Immediately use x7 - HAZARD!
```

From the objdump:
```
80000020:  0042a383    lw   t2,4(t0)     # x7 = t2
80000024:  007384b3    add  s1,t2,t2     # x9 = s1
```

---

### What to Do in GTKWave for Part IV:

#### □ Step 1: Find the Load-Use Hazard Location

In GTKWave, scroll to find where:
- `PCF = 80000020` or `PCD = 80000020` or `PCE = 80000020`
- This is your `lw x7, 4(x5)` instruction
- The dependent `add` follows immediately

**Estimated time:** Around t=350ps to t=400ps (may vary)

#### □ Step 2: Observe the Stall Signal

Watch for **`StallF`** signal to go HIGH (= 1):
- This happens when the `add` instruction is **decoded**
- The hazard unit detects: "previous instruction is a load, current instruction uses the loaded register"
- `StallF = 1` triggers a pipeline stall

#### □ Step 3: Track the Timeline

Observe the cycle-by-cycle behavior:

**Cycle 1: Load in Execute**
```
PCE = 80000020     (lw executing - calculating address)
PCD = 80000024     (add in decode)
Rs1E, Rs2E = ?     (previous instruction)
StallF = 0
```

**Cycle 2: Hazard Detected, Stall Begins**
```
PCE = 80000024?    (trying to execute add)
PCD = 80000024     (add STAYS in decode - stalled!)
RdM = 07           (lw is in Memory, will write to x7)
Rs1E = 07, Rs2E = 07 (add needs x7)
StallF = 1         ← STALL DETECTED!
```

**Cycle 3: Stall Continues, Load Completes**
```
PCE = (bubble)     (NOP inserted in Execute)
PCD = 80000024     (add still in decode)
RdW = 07           (lw in Writeback now)
PCF = 80000024     (fetch stalled - same address)
StallF = 0         (stall releasing)
```

**Cycle 4: Stall Released, Add Executes**
```
PCE = 80000024     (add finally executes!)
Rs1E = 07, Rs2E = 07 (now x7 value can be forwarded from Writeback)
RdW = 07           (lw completed, value available)
```

#### □ Step 4: Identify Key Signals

**Signals that prove the hazard:**

1. **`StallF = 1`** ← Main indicator
2. **`RdM = 07`** (load writing to x7 in Memory stage)
3. **`Rs1E = 07` and `Rs2E = 07`** (add needs x7 in Execute)
4. **`PCF` doesn't advance** during stall (stays at same address)
5. **`PCD` doesn't advance** during stall

#### □ Step 5: Take Screenshot

Capture the waveform showing:
- ✓ `clk` - to show cycle boundaries
- ✓ `PCF`, `PCD`, `PCE` - to show stall (PC not advancing)
- ✓ `Rs1E`, `Rs2E` - showing dependency (both = 07)
- ✓ `RdM` or `RdW` - showing load destination (= 07)
- ✓ **`StallF = 1`** ← CRITICAL - must show the stall!

**Time window:** Show 4-5 clock cycles around the stall event

---

### Answer to Write for Part IV:

**Describe the hazard scenario implemented:**

**Load-Use Data Hazard**

I implemented a **load-use hazard** by placing a load instruction immediately followed by an instruction that depends on the loaded value:

```assembly
lw  x7, 4(x5)      # Load word from memory address (x5+4) into x7
add x9, x7, x7     # Use x7 immediately (x9 = x7 + x7)
```

**Why This Creates a Hazard:**

Load instructions require memory access, which takes multiple cycles:
1. **Execute stage:** Calculate memory address (x5 + 4)
2. **Memory stage:** Read data from memory → data becomes available at END of stage
3. **Writeback stage:** Write data to register file

The dependent `add` instruction needs x7's value when it reaches the Execute stage. However:
- When `add` is in Execute, `lw` is only in Memory stage
- The load data hasn't arrived yet!
- **Even with data forwarding**, the value is not available in time

**Resolution:**

The Hazard Unit detects this condition:
- Load instruction in Execute stage with destination = x7
- Next instruction in Decode uses x7 as source
- Cannot forward (data not ready yet)

**Action taken:**
1. Assert `StallF = 1` - stall the pipeline
2. Hold Fetch and Decode stages (instructions don't advance)
3. Insert bubble/NOP in Execute stage
4. Wait 1 cycle for load to complete
5. Load data now available in Writeback, can be forwarded
6. Release stall, `add` executes with correct value

**Observable in Waveform:**
- `StallF = 1` for one clock cycle
- `PCF` and `PCD` don't advance during stall
- `RdM = 0x07` (load destination) matches `Rs1E = Rs2E = 0x07` (add sources)
- One bubble cycle inserted, then execution resumes

This demonstrates the **limit of data forwarding** - load instructions still require a mandatory 1-cycle stall when the next instruction immediately depends on the loaded data.

---

## Quick GTKWave Navigation Tips:

**Finding the load-use hazard cycles:**
1. Use Ctrl+F or Search function in GTKWave
2. Look for signal `PCF` or `PCD` with value `80000020` (the load)
3. Or scan for `StallF = 1` (easier!)

**Zoom to the right level:**
- You want to see 4-5 clock cycles clearly
- Each cycle should be wide enough to read signal values
- Use zoom buttons or scroll wheel

**Signal format:**
- Right-click signal → Data Format → Hexadecimal (for addresses/registers)
- Right-click signal → Data Format → Binary (for StallF if needed)

---

## Summary Checklist:

### Part III (Forwarding):
- [ ] Understand the observation at t=290ps
- [ ] Write answer explaining data forwarding mechanism
- [ ] Explain why forwarding is needed (performance)
- [ ] Mention exception: load-use hazards

### Part IV (Load-Use Hazard):
- [ ] Find the load instruction cycles (PC=80000020)
- [ ] Observe `StallF = 1` when hazard detected
- [ ] Note register dependency (Rs1E/Rs2E = RdM = 07)
- [ ] See PC not advancing during stall
- [ ] Take screenshot showing stall
- [ ] Write hazard description explaining:
  - What instructions you used
  - Why it creates a hazard
  - How the processor resolves it
  - What happens in the pipeline

---

You're almost done! The hard part (compilation, simulation) is complete. Now it's just analyzing the waveforms and writing up your observations. Good luck! 🚀
