# Part IV: Load-Use Hazard Analysis

## Overview
This document describes the load-use hazard implementation in `prelab4_FFXX_GXX.s` for Lab 4 Part IV, where we observe pipeline stalling due to data dependency between a load instruction and an immediately following instruction that uses the loaded value.

---

## Hazard Scenario Implemented

### Code Implementation

```assembly
    lw x7, 4(x5)        # Load x7 from memory [Address: 0x80000020]
    add x9, x7, x7      # Immediately use x7 [Address: 0x80000024]
```

### Why This Creates a Hazard

**Load-use hazard** occurs when:
1. A **load instruction** writes a value to register x7
2. The **very next instruction** immediately reads that same register x7

This creates a **data dependency** because:
- The load instruction needs **2 cycles** to produce its result:
  - Cycle N: Execute stage (address calculation)
  - Cycle N+1: Memory stage (value retrieval from memory)
  - Cycle N+2: Writeback stage (register written)
- The ADD instruction needs the result **immediately**
- If the ADD tries to read x7 before the load completes, it will get stale data

### Hardware Solution: Stalling

The Wally processor implements a **stall mechanism**:
1. When the hazard is detected, the **StallF signal goes HIGH**
2. This prevents the Fetch stage from fetching a new instruction
3. All pipeline stages are held in place for 1 cycle
4. This delays the ADD instruction by 1 cycle, giving the load result time to be written

---

## Instruction Sequence with Addresses

From the disassembly (`prelab4_FFXX_GXX.objdump`):

```
80000020:	0042a383          	lw	t2,4(t0)      # t2 = x7 (register number 7)
80000024:	007384b3          	add	s1,t2,t2      # s1 = x9, uses t2 (x7) immediately
```

- **LW** at **0x80000020**: Loads into **x7** (register number 7, called t2 by ABI)
- **ADD** at **0x80000024**: Uses **x7** as both source operands (Rs1E=7, Rs2E=7), produces **x9** (register number 9, called s1 by ABI)

### Register Mapping (RISC-V ABI)

| Hardware Register | ABI Name | Our Usage |
|-------------------|----------|-----------|
| x5                | t0       | Array base address |
| x7                | t2       | Load destination / Source for ADD |
| x8                | s0       | (used in Part III) |
| x9                | s1       | ADD result destination |

---

## Pipeline Timeline During Hazard

### Normal Execution (Without Stall)

| Cycle | Fetch | Decode | Execute | Memory | Writeback |
|-------|-------|--------|---------|--------|-----------|
| N     | ADD   | LW     | ...     | ...    | ...       |
| N+1   | NEXT  | ADD    | LW      | ...    | ...       |
| N+2   | ...   | NEXT   | ADD     | LW     | ...       |

**Problem**: At cycle N+1, ADD enters Execute while LW is still in Memory. ADD tries to read x7 but the value isn't ready yet!

### With Stall (What Wally Does)

| Cycle | Fetch | Decode | Execute | Memory | Writeback | StallF |
|-------|-------|--------|---------|--------|-----------|--------|
| N     | ADD   | LW     | ...     | ...    | ...       | 0      |
| N+1   | (STALL)| ADD   | LW      | ...    | ...       | 1      |
| N+2   | NEXT  | (STALL)| ADD     | LW     | ...       | 0      |
| N+3   | ...   | NEXT   | ADD     | LW     | ...       | 0      |

**Solution**: At cycle N+1, when the hazard is detected:
- StallF = 1 (Fetch stage stalled)
- ADD remains in Decode for one extra cycle
- LW advances through Memory
- By cycle N+2, LW reaches Writeback and x7 is written
- ADD can now safely execute in cycle N+3 and read the correct x7 value

---

## GTKWave Signal Observations

When analyzing the waveform in GTKWave, look for:

### Key Timing Points

**Cycle when LW is in Memory and ADD is in Decode:**
- **PCE** = Address of some other instruction (in Execute)
- **PCD** = 0x80000024 (ADD in Decode stage)
- **PCF** = Should NOT advance (because StallF=1)

### Stall Signal Evidence

**When StallF = 1:**
- **Fetch stage is held** - no new instruction fetched
- **All other stages are held** in place
- This creates a 1-cycle delay for the ADD instruction

**Signal Pattern to Identify:**
```
    |--- LW in Memory ---|--- LW in Writeback ---|
    |      StallF=1      |      StallF=0         |
    |--- ADD in Decode --|--- ADD in Execute ----|
```

### Register Signals During Hazard

When ADD is in Execute (after the stall):
- **Rs1E** = 07 (register 7, which is x7)
- **Rs2E** = 07 (register 7, which is x7)
- **RdE** = 09 (register 9, which is x9 - destination)
- **RdW** = 07 (register 7 is being written in Writeback from the LW)

This configuration shows:
- The ADD needs to read x7 (Rs1E=7, Rs2E=7)
- The LW is writing x7 (RdW=7) in the same cycle
- Data forwarding then routes the Writeback value to the ADD's ALU inputs

---

## Why This Matters

This is the **most severe type of data hazard** because:

1. **Cannot be solved by forwarding alone**: 
   - Forwarding can solve WR→RD hazards when the result is available in Execute/Memory
   - But a load's result comes FROM memory, so it's not available until Memory stage
   - With a dependent instruction in the next cycle, there's no earlier stage to forward from

2. **Requires hardware stalling**:
   - The processor must detect this specific pattern (Load followed by dependent instruction)
   - Hazard detection unit (HDU) stops the pipeline
   - 1-cycle stall is mandatory

3. **Real-world impact**:
   - Reduces pipeline throughput
   - Load instructions naturally create this bottleneck
   - Software techniques (instruction reordering) can help avoid load-use hazards

---

## Implementation Details

### How Wally Detects This Hazard

The hazard detection unit checks:
1. Is the instruction in Memory or Writeback a **load** (LW, LH, LB)?
2. Is the instruction in Decode using the **same register** as a source operand?
3. If both true → **set StallF = 1**

### What Gets Stalled

When StallF=1:
- **Fetch stage**: PCF does not change
- **All other stages**: Hold their current values
- **No new instruction** enters the pipeline

This creates a bubble in the pipeline for exactly 1 cycle.

---

## Verification Checklist

When viewing in GTKWave, verify:

- [ ] LW instruction is at address 0x80000020
- [ ] ADD instruction is at address 0x80000024
- [ ] Find the cycle where PCD = 0x80000024 (ADD in Decode)
- [ ] Confirm StallF = 1 in that same cycle
- [ ] Check that PCF remains constant (no new fetch)
- [ ] Observe that in the next cycle, StallF = 0 and PCF changes
- [ ] Take screenshot showing StallF=1 and pipeline registers

---

## Summary

**Hazard Type**: Load-Use Hazard (Write-Read after Load)

**Trigger**: 
```
lw  x7, 4(x5)       # Write x7
add x9, x7, x7      # Read x7 immediately
```

**Resolution**: Pipeline stall for 1 cycle (StallF=1)

**Root Cause**: Load result not available until Memory/Writeback stage; dependent instruction in Decode needs to wait

**Performance Impact**: 1 cycle delay per load-use pair

---

## Files and References

- **Assembly**: `prelab4_FFXX_GXX.s`
- **Compiled**: `prelab4_FFXX_GXX.elf`
- **Disassembly**: `prelab4_FFXX_GXX.objdump`
- **Waveform**: `prelab4_testbench.vcd`
- **Signal Config**: `signals.gtkw`
