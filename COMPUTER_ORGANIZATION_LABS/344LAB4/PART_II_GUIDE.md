# Part II: Unexpected Instructions & FlushD

## Overview
In Part II, you'll investigate **control hazards** - what happens when the processor encounters branches/jumps and has already fetched wrong instructions.

---

## The Phenomenon: Unexpected Instructions

### What to Look For in GTKWave:

1. **Add the FlushD signal** (if not already visible):
   - Navigate to: `testbench -> dut -> core -> ifu`
   - Find and double-click on **FlushD**
   - This signal will show when instructions are being flushed/invalidated

2. **Observe the instruction flow:**
   - Watch the `InstrD` values as you step through time
   - Compare them to your objdump file sequentially
   - You'll notice some instructions appear that shouldn't execute!

---

## Your Program's Control Flow

Looking at `prelab4_FFXX_GXX.objdump`:

```assembly
80000000:  auipc  t0,0x10          # Start
80000004:  mv     t0,t0
80000008:  nop
8000000c:  nop
80000010:  nop
80000014:  lw     t1,0(t0)
80000018:  nop
8000001c:  add    s0,t1,t1
80000020:  lw     t2,4(t0)         # Your hazard
80000024:  add    s1,t2,t2         # Dependent instruction
80000028:  j      8000002c <END>   # ← JUMP to END
8000002c <END>:
8000002c:  li     a7,10
80000030:  j      80000030         # ← Infinite loop (halt)
```

### Expected Execution Order:
```
80000000 → 80000004 → ... → 80000028 (jump) → 8000002c → 80000030 → 80000030 ...
```

### What Actually Gets Fetched:
The processor **speculatively fetches** sequential instructions:
```
80000028 (j instruction)
8000002c (jump target) ← Should execute
80000030 (infinite loop) ← Should execute
BUT ALSO:
80000034 (whatever is there) ← WRONG! Never should fetch this
80000038 (whatever is there) ← WRONG! Never should fetch this
```

**Why?** The processor doesn't know about the jump at `80000028` until it's **decoded**. By then, the fetch unit has already started fetching `8000002c`, `80000030`, etc.

---

## Control Hazard Explained

### Timeline of a Jump:

**Cycle 1:**
- **Fetch:** Fetches jump instruction at `80000028`
- **PC increments** to `8000002c` for next fetch

**Cycle 2:**
- **Fetch:** Fetches instruction at `8000002c` (wrong path!)
- **Decode:** Jump instruction decoded, target calculated = `8000002c`
- **Problem detected:** We just fetched the wrong next instruction!

**Cycle 3:**
- **FlushD = 1:** Invalidate the wrongly fetched instruction in decode
- **Redirect PC:** Set PCF to correct target
- **Insert bubble:** Execute stage gets a NOP

**Cycle 4+:**
- Continue from correct path

---

## Why This Functionality Is Needed

### Performance Trade-off:

**Option 1 - Always Stall on Branches (Slow):**
- Every time you see a branch/jump, wait until it's fully decoded
- Pipeline stalls for 1-2 cycles on EVERY control instruction
- Very slow!

**Option 2 - Speculative Fetch + Flush (Fast):**
- Assume sequential execution, keep fetching
- If wrong, flush and redirect (only pay penalty when wrong)
- Much faster on average!

### Branch Prediction:
Modern processors go even further:
- Predict whether branches are taken or not taken
- Only flush when prediction is wrong
- Your simple Wally design: always predicts "sequential" (not taken)

---

## What Happens After FlushD = 1

**The cycle right after FlushD goes high:**

1. **Decode Stage:**
   - The invalid instruction is converted to a NOP (no operation)
   - It won't modify any registers or memory

2. **Execute Stage:**
   - Receives a bubble/NOP instead of a real instruction
   - One cycle is "wasted" but correctness is maintained

3. **Fetch Stage:**
   - PCF is redirected to the correct target address
   - Starts fetching from the correct path

4. **Next Cycles:**
   - Pipeline fills with correct instructions
   - Normal execution resumes

---

## What to Do in GTKWave for Part II:

### Step 1: Add FlushD Signal
- In GTKWave left panel: `testbench -> dut -> core -> ifu -> FlushD`
- Double-click to add it to the waveform

### Step 2: Find a Flush Event
- Look for where `FlushD = 1` (goes high)
- This typically happens around jumps/branches
- For your program, look around the `j END` instruction

### Step 3: Observe the Cycle
**Before FlushD = 1:**
- Note the value of `InstrD` (the instruction being flushed)
- Note the value of `PCF` (where fetch is pointing)

**When FlushD = 1:**
- This is the cycle the flush is detected

**After FlushD = 1 (next cycle):**
- `InstrD` becomes 00000000 or 00000013 (NOP)
- `PCF` redirects to correct target

### Step 4: Take Screenshot
Show:
- `clk`
- `PCF`
- `PCD`
- `InstrD`
- `FlushD` ← Make sure this is visible and showing the high pulse

---

## Expected Timeline Example:

```
Time  | clk | PCF      | InstrD   | FlushD | Explanation
------|-----|----------|----------|--------|---------------------------
350ps |  1  | 80000028 | 00630433 |   0    | Fetching jump instruction
360ps |  0  | 8000002c | 0040006f |   0    | Jump now in decode
370ps |  1  | 80000030 | 00a00893 |   1    | FlushD! Wrong path detected
380ps |  0  | 8000002c | 00000013 |   0    | Flushed to NOP, PC corrected
390ps |  1  | 80000030 | 00a00893 |   0    | Correct execution
```

(Note: Actual addresses/values may differ - check your waveform!)

---

## Questions to Answer for Part II:

### 1. Explain this behavior (unexpected instructions)
**Answer:**
The processor uses **speculative execution** - it continues fetching instructions sequentially while a branch/jump is being decoded. When the jump target is calculated, if the already-fetched instruction is from the wrong path, it must be discarded (flushed). This is a **control hazard**.

### 2. Why is this functionality provided?
**Answer:**
This is a **performance optimization**. Stalling the pipeline on every branch/jump would waste many cycles. Instead, the processor optimistically continues fetching, and only pays a penalty (1 cycle flush) when it guesses wrong. Since most execution is sequential, this significantly improves average performance.

### 3. What happens the cycle right after FlushD is high?
**Answer:**
- The invalid instruction in the Decode stage is **converted to a NOP** (neutralized)
- The Program Counter (PCF) is **redirected** to the correct target address
- The Execute stage receives a **bubble/NOP** (one wasted cycle)
- Subsequent cycles fetch from the **correct path** and execution continues normally

---

## Tips:

- **Zoom in** around the jump instruction (PC = 80000028) to see the flush clearly
- FlushD will be a **short pulse** (high for 1 cycle)
- You might see multiple flush events if there are multiple jumps/branches
- The infinite loop `j 80000030` will NOT cause flushes (jumps to itself, no redirect needed)

---

Good luck! Let me know if you see anything unexpected in the waveform.
