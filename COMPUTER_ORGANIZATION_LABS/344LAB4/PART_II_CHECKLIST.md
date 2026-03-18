# Part II Checklist

## Steps to Complete Part II:

### □ Step 1: Add FlushD Signal to GTKWave
1. In GTKWave, look at the left panel (Signal Hierarchy)
2. Navigate: `testbench` → `dut` → `core` → `ifu`
3. Find signal named `FlushD`
4. Double-click to add it to waveform view

### □ Step 2: Locate a Flush Event
Look for where FlushD goes HIGH (= 1):
- Scan through the waveform
- FlushD will show brief pulses (1 clock cycle)
- This typically happens around jump/branch instructions
- For your program, look around PC = 80000028 (the `j END` instruction)

### □ Step 3: Analyze the Flush Event
When you find FlushD = 1, observe:
- **Before:** What instruction is in InstrD? What is PCF?
- **During:** FlushD = 1
- **After (next cycle):** InstrD becomes NOP, PCF redirects to correct address

### □ Step 4: Take Screenshot
Capture the waveform showing:
- ✓ clk
- ✓ PCF  
- ✓ PCD
- ✓ InstrD
- ✓ FlushD ← **MUST be visible and showing the pulse!**

### □ Step 5: Answer the Questions

Write answers for:

**Q1: Explain the unexpected instruction behavior and why it's provided**
Key points to cover:
- Speculative execution / sequential fetching
- Control hazards from branches/jumps
- Performance optimization (avoid stalling on every branch)
- Flush penalty only when prediction wrong

**Q2: What happens right after FlushD is high?**
Key points:
- Instruction in Decode → converted to NOP
- PCF redirected to correct target
- Execute receives bubble
- Pipeline refills with correct instructions

---

## Quick Reference - Your Program's Jump:

```assembly
80000028:  j 8000002c <END>    ← Jump instruction
                                   
After this jump, processor will:
1. Fetch 8000002c (correct)
2. Fetch 80000030 (correct - target of jump)  
3. But may have ALREADY fetched 8000002c before jump decoded
4. FlushD will trigger to invalidate wrong fetch
```

---

## GTKWave Tips:

**Zoom controls:**
- Scroll wheel to zoom in/out
- Click and drag in the time ruler to zoom to specific region

**Signal display format:**
- Right-click signal name → Data Format → Hexadecimal

**Finding specific time:**
- Look for the jump instruction InstrD = 0040006f
- FlushD pulse should be nearby

**Signal values:**
- FlushD = 0 (low) = normal operation
- FlushD = 1 (high) = flush happening!

---

## Expected Observations:

Around the jump at PC=80000028, you should see:

```
Cycle N:   PCF=80000028, InstrD=(previous), FlushD=0
Cycle N+1: PCF=8000002c, InstrD=0040006f (jump decoded), FlushD=0  
Cycle N+2: PCF=80000030, InstrD=(wrong?), FlushD=1 ← FLUSH!
Cycle N+3: PCF=8000002c, InstrD=00000013 (NOP), FlushD=0 ← Corrected
```

(Note: Exact timing may vary - this is conceptual)

---

All set! Open GTKWave, add the FlushD signal, and start exploring! 🔍
