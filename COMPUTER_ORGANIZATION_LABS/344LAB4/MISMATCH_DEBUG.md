# Fibonacci Objdump vs GTKWave Mismatch Analysis

## Reference: fibonacci.objdump

```
Address  | Hex Code  | Assembly         | t1(counter) | t2(fib-2) | t3(fib-1) | t4(result)
---------|-----------|------------------|-------------|-----------|-----------|----------
80000000 | 00010297  | auipc t0,0x10    | -           | -         | -         | -
80000004 | 00028293  | mv t0,t0         | -           | -         | -         | -
80000008 | 00a00313  | li t1,10         | 10          | -         | -         | -
8000000c | 00000393  | li t2,0          | 10          | 0         | -         | -
80000010 | 00100e13  | li t3,1          | 10          | 0         | 1         | -
80000014 | 0072a023  | sw t2,0(t0)      | 10          | 0         | 1         | -         V[0]=0
80000018 | 00428293  | addi t0,t0,4     | 10          | 0         | 1         | -         ptr++
8000001c | 01c2a023  | sw t3,0(t0)      | 10          | 0         | 1         | -         V[1]=1

LOOP:
80000020 | 02030063  | beqz t1,DONE     | if t1==0→jump, else continue
80000024 | 007e0eb3  | add t4,t3,t2     | t4 = t3+t2
80000028 | 00428293  | addi t0,t0,4     | ptr++
8000002c | 01d2a023  | sw t4,0(t0)      | V[i] = t4
80000030 | 000e0393  | mv t2,t3         | t2 = t3 (shift)
80000034 | 000e8e13  | mv t3,t4         | t3 = t4 (shift)
80000038 | fff30313  | addi t1,t1,-1    | t1-- (counter--)
8000003c | fe5ff06f  | j 80000020       | Jump back to LOOP

DONE:
80000040 | 0000006f  | j 80000040       | Infinite loop (halt)
```

## Expected GTKWave Values

### Instruction Encoding Check

For any cycle in GTKWave, verify:
1. **PCF value** (address being fetched)
2. **InstrD value** (hex encoding in decode stage)
3. **Compare** with objdump at that address

### Example Verifications:

**If PCF = 0x80000020:**
- Expected InstrD = **0x02030063** (beqz t1,80000040)
- Check in GTKWave: Does InstrD match?

**If PCF = 0x80000024:**
- Expected InstrD = **0x007e0eb3** (add t4,t3,t2)
- Check in GTKWave: Does InstrD match?

**If PCF = 0x8000003c:**
- Expected InstrD = **0xfe5ff06f** (j 80000020)
- Check in GTKWave: Does InstrD match?

---

## Troubleshooting Mismatch Issues

### Possible Causes:

1. **Pipeline Delay (EXPECTED):**
   - InstrD lags PCF by 1 cycle
   - PCF shows what's being FETCHED now
   - InstrD shows what was fetched LAST cycle
   - So InstrD = previous cycle's PCF value instruction
   
   **Example:**
   ```
   Cycle N:   PCF=0x80000024, InstrD=0x02030063 (from prev fetch)
   Cycle N+1: PCF=0x80000028, InstrD=0x007e0eb3 (from cycle N fetch)
   ```

2. **Byte Swapping:**
   - RISC-V uses little-endian encoding
   - 0xfe5ff06f in hex is displayed as-is
   - But may appear different depending on display format

3. **Data Format Setting:**
   - Right-click on InstrD in GTKWave
   - Select "Data Format" → "Hexadecimal"
   - Make sure it's set to display as HEX, not binary or decimal

4. **Signal Not Selected Correctly:**
   - Verify you're looking at `InstrD` from `testbench.dut.core.ifu`
   - NOT other signals with similar names

---

## Step-by-Step Debug:

### Step 1: Verify Signal Selection in GTKWave

Check that you have the correct signal:
- Full path should be: `testbench.dut.core.ifu.InstrD[31:0]`
- Right-click → Properties to confirm

### Step 2: Check Data Format

- Right-click on InstrD signal name
- Click "Data Format"
- Select "Hexadecimal"
- Apply

### Step 3: Document Your Observation

Pick a specific time (e.g., t=350ps) and write down:
- **Time:** t=350ps
- **PCF value:** 0x________
- **InstrD value:** 0x________
- **PCD value (optional):** 0x________

Then look up what instruction should be at PCF address in objdump.

### Step 4: Check Pipeline Stages

Remember: There's a **1-cycle delay** between pipeline stages:
- Cycle N: PCF fetches address X
- Cycle N+1: InstrD shows instruction from address X
- Cycle N+2: Execute stage processes that instruction

### Step 5: Share Observations

If values still don't match:
1. Tell me the TIME in GTKWave (e.g., t=350ps)
2. Tell me the **PCF value** you see
3. Tell me the **InstrD value** you see
4. Tell me what address/instruction you EXPECT

Then I can help diagnose the issue!

---

## Common Mismatches Explained:

### Scenario 1: PCF=0x80000020, but InstrD≠0x02030063

**Likely cause:** Pipeline delay
- InstrD shows instruction from PREVIOUS fetch
- Check what PCF was one cycle earlier
- That's what InstrD should match

### Scenario 2: Values in wrong format

**Solution:** 
- Right-click InstrD → Data Format → Hexadecimal
- Ensure it's showing HEX not binary

### Scenario 3: Seeing different instruction entirely

**Possible causes:**
- Wrong signal selected (check full path in left panel)
- Waveform file corrupted (unlikely but possible)
- Simulation didn't complete properly

### Scenario 4: Address incrementing strangely

**Normal behavior:**
- PCF increments by 4 each cycle (RISC-V 32-bit instructions)
- 0x80000000 → 0x80000004 → 0x80000008 → ...
- May occasionally jump (branches/jumps) or stall (hazards)

---

## What to Report

If mismatch persists, tell me:

1. **Time point:** What time in GTKWave did you check?
2. **PCF value:** What address is being fetched?
3. **InstrD value:** What hex does GTKWave show?
4. **Expected:** What should it be from objdump?
5. **Screenshot:** Can you take a screenshot showing both?

---

## Quick Verification Checklist:

- [ ] InstrD signal added from `ifu` module
- [ ] Data format set to Hexadecimal
- [ ] Checked instruction at PCF-4 (previous cycle) to account for delay
- [ ] Verified objdump is reading correct file (fibonacci.objdump)
- [ ] Simulation completed successfully (program ended)
- [ ] VCD file loaded completely (check file size: should be ~140KB)

---

Let me know which specific cycle has the mismatch and I can help debug! 🔍
