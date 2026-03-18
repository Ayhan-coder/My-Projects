# Part I: Tracking Instructions - Guide

## What You Should See in GTKWave

GTKWave is now open with your waveform. The signals from `signals.gtkw` should already be loaded:

### Signals Displayed:
1. **clk** - System clock (toggles 0/1)
2. **PCF** - Program Counter Fetch (address of instruction being fetched)
3. **PCD** - Program Counter Decode (address of instruction being decoded)
4. **PCE** - Program Counter Execute (address of instruction being executed)
5. **Rs1E, Rs2E** - Source registers in Execute stage
6. **RdE, RdM, RdW** - Destination registers in Execute/Memory/Writeback
7. **StallF** - Stall signal (1 when hazard detected)

---

## Part I Tasks:

### Step 1: Navigate the Waveform
- Use the zoom buttons or scroll to see different time periods
- The time scale is in picoseconds (ps)
- Look for cycles around t=290ps to t=330ps

### Step 2: Pick a Clock Cycle
**Example: Look at the cycle between t=310ps and t=320ps**

At this cycle, observe:
- **PCF** value (e.g., 80000000, 80000004, etc.)
- **InstrD** value (the hex instruction code)

### Step 3: Compare with objdump

Open `prelab4_FFXX_GXX.objdump` and find the instruction at the PCF address.

**Example from your objdump:**
```
80000000:	00010297          	auipc	t0,0x10
80000004:	00028293          	mv	t0,t0
80000008:	00000013          	nop
8000000c:	00000013          	nop
80000010:	00000013          	nop
80000014:	0002a303          	lw	t1,0(t0)
80000018:	00000013          	nop
8000001c:	00630433          	add	s0,t1,t1
80000020:	0042a383          	lw	t2,4(t0)
80000024:	007384b3          	add	s1,t2,t2
80000028:	0040006f          	j	8000002c
```

### Step 4: Verify Pipeline Behavior

**Key Observation:**
- At time T, if PCF = 80000014, the fetch is getting the `lw` instruction
- At time T+1 cycle, PCD should = 80000014 (instruction moves to decode)
- At time T+2 cycles, PCE should = 80000014 (instruction moves to execute)

This demonstrates the **1-cycle delay** between pipeline stages.

---

## Screenshot Requirements for Part I:

Take a screenshot showing:
1. ✅ The clock signal (clk)
2. ✅ PCF showing the fetch address
3. ✅ InstrD showing the decoded instruction in hex
4. ✅ A specific clock cycle highlighted (e.g., t=310-320ps)

**Answer the question:**
- Does the InstrD value match the instruction encoding at the PCF address in the objdump?
- YES! They should match exactly.

---

## Your Load-Use Hazard (for Part IV later)

Looking at your objdump, you have:
```
80000020:	0042a383          	lw	t2,4(t0)      # Load into x7 (t2)
80000024:	007384b3          	add	s1,t2,t2      # Use x7 immediately
```

When you look at cycles around this instruction:
- **StallF** should go HIGH (=1) when the `add` is decoded
- This demonstrates the load-use hazard!

---

## Next Steps:

1. Explore the waveform in GTKWave
2. Take your screenshot for Part I
3. Verify the instruction match
4. Note the pipeline delays (PCD vs PCF vs PCE)

**Tip:** Right-click on signals to change display format (hex, decimal, binary)
