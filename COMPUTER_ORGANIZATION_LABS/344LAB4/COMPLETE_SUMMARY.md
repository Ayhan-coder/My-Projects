# Complete Assignment Summary - All Parts

## 📋 Assignment Status

### ✅ Completed:
1. ✅ Docker setup and compilation
2. ✅ Assembly program with load-use hazard
3. ✅ Verilator simulation (VCD generated)
4. ✅ GTKWave opened with signals
5. ✅ All answer documentation

### 📝 What You Need to Do:
1. Explore GTKWave waveforms
2. Take 3 screenshots (Part I, II, IV)
3. Copy answers from `ASSIGNMENT_ANSWERS.md` to your lab report

---

## 🎯 Quick Reference - What to Find in GTKWave

### Part I: Tracking Instructions
**Find:** Any cycle around t=310ps
**Look for:** 
- PCF value (e.g., 80000014)
- InstrD value (e.g., 0002a303)
**Verify:** InstrD matches objdump at that PC address
**Screenshot:** clk, PCF, InstrD

### Part II: Unexpected Instructions & FlushD
**Find:** Cycles around jump instruction (PC=80000028)
**Look for:** 
- FlushD = 1 (brief pulse)
- InstrD becomes NOP after flush
**Screenshot:** clk, PCF, PCD, InstrD, FlushD (showing pulse)

### Part III: Data Hazard (Forwarding)
**Find:** Around t=290ps to t=320ps
**Look for:**
- PCE = 8000001C (add instruction)
- Rs1E = Rs2E = 06 (reading x6)
- RdW = 06 (writing x6)
**No screenshot needed** - just understand and write answer

### Part IV: Load-Use Hazard
**Find:** Around PC=80000020 (your lw instruction)
**Look for:**
- StallF = 1 (the key signal!)
- RdM = 07 (load destination)
- Rs1E = Rs2E = 07 (add sources)
- PC not advancing during stall
**Screenshot:** clk, PCF/PCD/PCE, Rs1E/Rs2E, RdM, StallF=1

---

## 📁 Files in Your Directory

### Generated Files:
- `prelab4_FFXX_GXX.elf` - Compiled executable
- `prelab4_FFXX_GXX.objdump` - Disassembly for reference
- `testbench.vcd` - Waveform data (140KB)

### Guide Documents I Created:
- `ASSIGNMENT_ANSWERS.md` ← **Complete written answers for all parts**
- `PART_I_INSTRUCTIONS.md` - Part I detailed guide
- `PART_II_GUIDE.md` - Part II detailed explanation
- `PART_II_CHECKLIST.md` - Part II step-by-step
- `PART_III_IV_GUIDE.md` - Parts III & IV complete guide
- `analyze_vcd.py` - Python script (if you want to analyze VCD programmatically)

### Original Files:
- `prelab4_FFXX_GXX.s` - Your assembly (with load-use hazard)
- `linker.ld` - Linker script
- `signals.gtkw` - GTKWave signal configuration

---

## 🔍 Your Program's Key Instructions

```assembly
Address    | Hex      | Assembly          | Notes
-----------|----------|-------------------|---------------------------
80000000   | 00010297 | auipc t0,0x10     | Start - setup
80000004   | 00028293 | mv    t0,t0       | 
80000008   | 00000013 | nop               |
8000000c   | 00000013 | nop               |
80000010   | 00000013 | nop               |
80000014   | 0002a303 | lw    t1,0(t0)    | Original load
80000018   | 00000013 | nop               | 
8000001c   | 00630433 | add   s0,t1,t1    | Part III observation point
80000020   | 0042a383 | lw    t2,4(t0)    | YOUR LOAD (Part IV) ←
80000024   | 007384b3 | add   s1,t2,t2    | DEPENDENT ADD (causes stall) ←
80000028   | 0040006f | j     8000002c    | Jump (Part II flush point)
8000002c   | 00a00893 | li    a7,10       | END label
80000030   | 0000006f | j     80000030    | Infinite loop (halt)
```

---

## 📝 Answer Template (Copy from ASSIGNMENT_ANSWERS.md)

### Part I: Are instructions the same?
**Answer:** YES
**Explanation:** [See ASSIGNMENT_ANSWERS.md]

### Part II Question 1: Explain unexpected instructions
**Answer:** Speculative execution causes control hazards...
[See ASSIGNMENT_ANSWERS.md for full answer]

### Part II Question 2: What happens after FlushD is high?
**Answer:** Invalid instruction converted to NOP, PCF redirected...
[See ASSIGNMENT_ANSWERS.md for full answer]

### Part III: How can RdW be used in Execute?
**Answer:** Data Forwarding (Bypassing)...
[See ASSIGNMENT_ANSWERS.md for full answer]

### Part IV: Describe hazard scenario
**Answer:** Load-Use Data Hazard between lw x7,4(x5) and add x9,x7,x7...
[See ASSIGNMENT_ANSWERS.md for full answer]

---

## 🖼️ Screenshot Requirements Summary

### Screenshot 1 (Part I):
**Signals:** clk, PCF, InstrD
**Time:** Any cycle (e.g., t=310ps)
**Show:** Instruction fetch/decode working

### Screenshot 2 (Part II):
**Signals:** clk, PCF, PCD, InstrD, FlushD
**Time:** When FlushD = 1
**Show:** Control hazard flush happening

### Screenshot 3 (Part IV):
**Signals:** clk, PCF/PCD/PCE, Rs1E, Rs2E, RdM, StallF
**Time:** When StallF = 1 (around PC=80000020)
**Show:** Load-use hazard causing stall

---

## 🎓 Key Concepts Summary

### Pipeline Stages (5-stage):
1. **Fetch (F):** Fetch instruction from memory
2. **Decode (D):** Decode instruction, read registers
3. **Execute (E):** ALU operations
4. **Memory (M):** Load/store memory access
5. **Writeback (W):** Write result to register file

### Hazard Types:
1. **Structural:** Resource conflict (not in this lab)
2. **Data Hazard:** Register dependency
   - Solution: Forwarding (for most cases)
   - Exception: Load-use needs 1 stall
3. **Control Hazard:** Branch/jump causes wrong fetch
   - Solution: Flush + redirect

### Signals:
- **PC_:** Program Counter for each stage (F/D/E)
- **Instr_:** Instruction word
- **Rs1_, Rs2_:** Source registers
- **Rd_:** Destination register
- **StallF:** Pipeline stall indicator
- **FlushD:** Instruction flush indicator

---

## 💡 Tips for GTKWave

### Navigation:
- **Scroll wheel:** Zoom in/out
- **Click+drag timeline:** Zoom to region
- **Arrow keys:** Move through time
- **Ctrl+F:** Search signals

### Signal Format:
- Right-click signal name
- "Data Format" → Choose Hexadecimal/Binary/Decimal

### Finding Events:
- Look for signal transitions (0→1 or value changes)
- StallF=1 and FlushD=1 are brief pulses (1 cycle)
- PC values are hex addresses matching your objdump

### Best View:
- Zoom so 5-10 clock cycles fit on screen
- Each cycle should be readable
- Signal values should be visible

---

## ✅ Final Checklist

Before submitting:

- [ ] Opened GTKWave and explored waveforms
- [ ] Found and understood Part I (instruction tracking)
- [ ] Found FlushD pulse for Part II
- [ ] Understood forwarding concept for Part III
- [ ] Found StallF=1 for Part IV (load-use hazard)
- [ ] Took all 3 required screenshots
- [ ] Copied answers from ASSIGNMENT_ANSWERS.md
- [ ] Verified answers match your observations
- [ ] Reviewed objdump to understand instruction flow
- [ ] Ready to submit!

---

**Everything is ready!** GTKWave is open, all answers are written, you just need to:
1. Explore the waveforms
2. Take screenshots
3. Copy the answers to your lab report format

Good luck with your submission! 🎉
