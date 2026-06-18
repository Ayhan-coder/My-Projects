# Lab 4 - Complete Assignment Guide

## 🎉 Status: READY FOR ANALYSIS

All files compiled and simulated. GTKWave open and ready to explore!

---

## 📚 Two Programs to Analyze

### Program 1: fibonacci.s (For Assignment Parts 1 & 2)

**Status:** ✅ READY
- Simulates computing first 12 Fibonacci numbers
- Has multiple control flow changes (loops, branches, jumps)
- Perfect for observing pipeline behavior and control hazards

**Files:**
- `fibonacci.elf` - Compiled executable
- `fibonacci.objdump` - Disassembly reference
- `fibonacci_testbench.vcd` - Waveform (open in GTKWave)

**Guide:** See `FIBONACCI_COMPLETE_GUIDE.md` and `FIBONACCI_ANALYSIS.md`

---

### Program 2: prelab4_FFXX_GXX.s (For Assignment Parts 3 & 4)

**Status:** ✅ READY
- Simple program with load-use hazard implemented
- Demonstrates data forwarding and stall mechanisms
- Perfect for observing hazard detection

**Files:**
- `prelab4_FFXX_GXX.elf` - Compiled executable  
- `prelab4_FFXX_GXX.objdump` - Disassembly reference
- `testbench.vcd` - Waveform (from previous run)

**Guide:** See `PART_III_IV_GUIDE.md` and `ASSIGNMENT_ANSWERS.md`

---

## 📋 Assignment Structure

### PART 1 & 2: Fibonacci Program

**What to Do:**
1. Open `fibonacci_testbench.vcd` in GTKWave
2. Add signals: clk, PCF, InstrD, PCD (Part 1)
3. Find and analyze instruction cycles
4. Verify InstrD matches fibonacci.objdump
5. Add FlushD signal (Part 2)
6. Find FlushD pulses at jumps/branches
7. Take 2 screenshots

**Key Concepts:**
- **Part 1:** Instruction fetch/decode pipeline stages
- **Part 2:** Control hazards and speculative execution

**Answers:** In `FIBONACCI_COMPLETE_GUIDE.md`

---

### PART 3 & 4: Prelab4 Program

**What to Do:**
1. Open `testbench.vcd` in GTKWave (or run new simulation)
2. Understand data forwarding (Part 3)
3. Find and analyze load-use hazard (Part 4)
4. Look for StallF=1 signal
5. Take 1 screenshot

**Key Concepts:**
- **Part 3:** Data forwarding (bypassing) mechanism
- **Part 4:** Load-use hazard requiring pipeline stall

**Answers:** In `ASSIGNMENT_ANSWERS.md`

---

## 🎯 Quick Start

### Open GTKWave - Fibonacci
```bash
& "C:\iverilog\gtkwave\bin\gtkwave.exe" fibonacci_testbench.vcd
```

### Open GTKWave - Prelab4
```bash
& "C:\iverilog\gtkwave\bin\gtkwave.exe" testbench.vcd
```

---

## 📖 Reading Materials (Guides)

| File | Purpose |
|------|---------|
| `FIBONACCI_COMPLETE_GUIDE.md` | **START HERE** for Parts 1 & 2 |
| `FIBONACCI_ANALYSIS.md` | Detailed fibonacci analysis |
| `PART_III_IV_GUIDE.md` | Detailed guide for Parts 3 & 4 |
| `ASSIGNMENT_ANSWERS.md` | **All answers written out** |
| `COMPLETE_SUMMARY.md` | Overall summary |

---

## 📝 Answer Files

All answers are pre-written in these documents:

### For Parts 1 & 2 (Fibonacci):
→ See `FIBONACCI_COMPLETE_GUIDE.md` - Answers section

### For Part 3 (Data Forwarding):
→ See `ASSIGNMENT_ANSWERS.md` - Part III section

### For Part 4 (Load-Use Hazard):
→ See `ASSIGNMENT_ANSWERS.md` - Part IV section

---

## 📸 Screenshots Needed

### Part 1: Instruction Tracking
- **Program:** Fibonacci
- **Show:** clk, PCF, InstrD at a specific cycle
- **Verify:** InstrD matches fibonacci.objdump

### Part 2: Control Hazards & FlushD
- **Program:** Fibonacci
- **Show:** clk, PCF, PCD, InstrD, FlushD=1
- **Show:** 4-5 cycles around a FlushD pulse

### Part 4: Load-Use Hazard
- **Program:** Prelab4
- **Show:** clk, PCF/PCD/PCE, Rs1E, Rs2E, RdM, StallF=1
- **Show:** 4-5 cycles around the stall

---

## 🔍 Signal Navigation in GTKWave

### For Fibonacci (Parts 1 & 2):

**Part 1 Signals:**
```
testbench → dut → core → ifu
├── clk
├── PCF [31:0]
├── PCD [31:0]  (optional)
└── InstrD [31:0]
```

**Part 2 Additional Signal:**
```
testbench → dut → core → ifu
└── FlushD
```

### For Prelab4 (Part 4):

**Signals:**
```
testbench → dut → core
├── ifu
│   ├── PCF [31:0]
│   └── clk
├── ieu
│   ├── c
│   │   ├── Rs1E [4:0]
│   │   ├── Rs2E [4:0]
│   │   ├── RdE [4:0]
│   │   └── RdM [4:0]
│   └── c.RdW [4:0]
└── hzu
    └── StallF
```

---

## ✅ Checklist for Submission

- [ ] **Part 1:**
  - [ ] Opened fibonacci_testbench.vcd in GTKWave
  - [ ] Added clk, PCF, InstrD signals
  - [ ] Found a clear instruction cycle
  - [ ] Verified InstrD matches fibonacci.objdump
  - [ ] Took screenshot
  - [ ] Wrote answer: "Are instructions the same?"

- [ ] **Part 2:**
  - [ ] Added FlushD signal
  - [ ] Found FlushD=1 pulse (at jump)
  - [ ] Observed PCF redirection
  - [ ] Took screenshot showing FlushD pulse
  - [ ] Answered Q1: Explain unexpected instructions
  - [ ] Answered Q2: What happens after FlushD?

- [ ] **Part 3:**
  - [ ] Opened testbench.vcd in GTKWave
  - [ ] Understood data forwarding mechanism
  - [ ] Copied answer from ASSIGNMENT_ANSWERS.md

- [ ] **Part 4:**
  - [ ] Found load instruction (PC=80000020)
  - [ ] Found StallF=1 signal
  - [ ] Observed register dependency (Rs1E=Rs2E=RdM=07)
  - [ ] Took screenshot showing stall
  - [ ] Copied answer describing hazard

- [ ] Ready to submit!

---

## 💡 Key Insights

### Pipelining Benefits & Challenges

**Pipeline Stages:** Fetch → Decode → Execute → Memory → Writeback

**Hazards Observed:**

1. **Control Hazard** (Part 2 - Fibonacci)
   - Problem: Don't know branch target until decode complete
   - Solution: Speculative fetch, flush if wrong
   - Penalty: 1 cycle for incorrect prediction

2. **Data Hazard with Forwarding** (Part 3 - Prelab4)
   - Problem: Instruction B needs result from Instruction A
   - Solution: Forward result directly (bypass register file)
   - Penalty: 0 cycles for most cases

3. **Load-Use Hazard** (Part 4 - Prelab4)
   - Problem: Load result not available for next instruction
   - Solution: Stall pipeline for 1 cycle
   - Penalty: 1 mandatory cycle

---

## 🚀 You're All Set!

Everything is compiled, simulated, and ready for analysis. The guides provide:
- ✅ Complete explanations
- ✅ Step-by-step instructions
- ✅ All answers written out
- ✅ Signal navigation help
- ✅ Screenshot requirements

**Next Step:** Open GTKWave and start exploring! 🔍

Good luck with your submission! 🎓
