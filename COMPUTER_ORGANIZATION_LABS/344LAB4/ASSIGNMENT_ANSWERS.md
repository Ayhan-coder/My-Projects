# Assignment Answers Summary

## Part I: Tracking the Instructions

### Question: Are the instructions the same?
**Answer:** YES, the instruction encoding shown in `InstrD` at a given cycle exactly matches the instruction encoding shown in `prelab4_FFXX_GXX.objdump` at the corresponding PC address.

### Explanation:
The `PCF` signal shows the address of the instruction being fetched from memory. One clock cycle later, this instruction appears in the Decode stage and its encoding is displayed in `InstrD`. Due to pipelining, separate PC registers exist for each stage:
- **PCF** = PC for Fetch stage
- **PCD** = PC for Decode stage (value of PCF from previous cycle)
- **PCE** = PC for Execute stage (value of PCD from previous cycle)

This 1-cycle delay is a natural consequence of pipelining, where registers are inserted between stages to allow multiple instructions to be processed simultaneously.

---

## Part II: Unexpected Instructions

### Question 1: Explain this behavior and why this functionality is provided

**Behavior:**
When examining the instruction trace in `InstrD`, we observe instructions that should not be executed according to program logic. For example, after a jump instruction, we may see sequential instructions that follow the jump in memory even though control should transfer to the jump target.

**Explanation:**
This occurs because of **speculative execution** and **control hazards**:

1. **Sequential Fetching:** The Instruction Fetch Unit (IFU) continuously fetches instructions sequentially (PC + 4) before knowing whether the current instruction is a branch or jump.

2. **Control Hazard:** When a jump or branch instruction is fetched, the processor doesn't immediately know:
   - That it's a control-flow instruction
   - What the target address is
   
3. **Pipeline Delay:** By the time the jump is decoded and the target is calculated, the fetch unit has already fetched one or more wrong instructions from the sequential path.

4. **Flush Mechanism:** These incorrectly fetched instructions must be invalidated (flushed) to maintain program correctness.

**Why This Functionality Is Provided:**

This is a **performance optimization** technique:

- **Alternative (Always Stall):** The processor could stall (wait) every time it encounters a potential branch/jump until the instruction is fully decoded and the target is calculated. This would waste 1-2 cycles on EVERY control instruction.

- **Better Approach (Speculative Fetch + Flush):** The processor optimistically assumes sequential execution and continues fetching. If the assumption is wrong, it flushes the incorrect instructions and redirects. Since most program execution is sequential (not jumping), this approach is much faster on average.

- **Trade-off:** We pay a 1-cycle penalty only when we're wrong (when a branch is taken or a jump occurs), rather than stalling on every potential control instruction.

This is the foundation of **branch prediction** in modern processors, where sophisticated algorithms predict whether branches will be taken to minimize flush penalties even further.

---

### Question 2: What happens at the clock cycle right after FlushD is high?

**Answer:**

When `FlushD = 1` (high), it signals that the instruction currently in the Decode stage must be invalidated. In the **next clock cycle** (immediately after FlushD is high), the following happens:

1. **Decode Stage:**
   - The invalid instruction is **converted to a NOP (No Operation)**
   - The instruction encoding in `InstrD` typically becomes `00000013` (the RISC-V NOP encoding)
   - This NOP will not modify any registers, memory, or processor state

2. **Execute Stage:**
   - Instead of receiving the flushed instruction, the Execute stage receives a **bubble** (essentially a NOP)
   - One cycle of execution time is "wasted" but correctness is preserved

3. **Fetch Stage:**
   - The Program Counter for Fetch (`PCF`) is **redirected** to the correct target address
   - The fetch unit begins fetching instructions from the correct path

4. **Pipeline Recovery:**
   - Over the next 1-2 cycles, the pipeline refills with instructions from the correct execution path
   - Normal execution resumes without any architectural state being corrupted

**Visual Example:**
```
Cycle N:   FlushD = 1, InstrD = 0040006f (wrong instruction)
Cycle N+1: FlushD = 0, InstrD = 00000013 (NOP/bubble), PCF redirected
Cycle N+2: Pipeline continues with correct instructions
```

The flush mechanism ensures **correctness** (wrong instructions never execute) at the cost of **one bubble cycle** (temporary performance loss).

---

## Part III: Data Hazard

### Question: How can a register whose value is about to change in the Writeback stage be used in Execute stage?

**Answer: Data Forwarding (Bypassing)**

This seeming contradiction is resolved through a fundamental pipeline optimization called **data forwarding** or **bypassing**.

**The Problem:**
```
Instruction A: add x6, x1, x2    # Writes to x6
Instruction B: add x8, x6, x6    # Reads x6 immediately after
```

In a naive pipeline:
- When B is in Execute stage, A is in Writeback stage
- B needs to read x6, but A hasn't written the new value to the register file yet
- B would read the OLD (stale) value of x6 → WRONG!

**The Solution - Data Forwarding:**

The processor adds **bypass paths** (multiplexers) that route computed values directly from later pipeline stages back to earlier stages:

1. **Forwarding Paths:**
   - **Memory → Execute:** Forward data from Memory stage to Execute stage inputs
   - **Writeback → Execute:** Forward data from Writeback stage to Execute stage inputs

2. **Hazard Detection:**
   - The **Hazard Unit** compares source registers in Execute (`Rs1E`, `Rs2E`) with destination registers in later stages (`RdM`, `RdW`)
   - If there's a match (e.g., `Rs1E == RdW == 0x06`), it activates forwarding

3. **Bypass Operation:**
   - Instead of reading the stale value from the register file, multiplexers select the forwarded value
   - The ALU receives the correct (new) value even though it hasn't been written to the register file yet

4. **Transparent to Software:**
   - The programmer doesn't need to worry about this
   - Hardware automatically detects dependencies and forwards values
   - Instructions execute as if they had access to the latest values

**Why This Matters:**
- **Without forwarding:** Would need to insert 2 NOPs after every instruction that writes a register (massive performance loss)
- **With forwarding:** Most data hazards are resolved with zero stall cycles
- **Performance gain:** Typical programs run 30-40% faster with forwarding

**Exception - Load-Use Hazard:**
Load instructions are special because they read from memory, and the data isn't available until the **Memory stage** completes. Even with forwarding, if the very next instruction needs that data in Execute stage, there's not enough time. This requires a **1-cycle stall** (which you'll observe in Part IV with the `StallF` signal).

**Key Signals in Wally:**
- `RdE`, `RdM`, `RdW`: Destination register in Execute/Memory/Writeback stages
- `Rs1E`, `Rs2E`: Source registers in Execute stage
- When `Rs1E == RdM` or `Rs1E == RdW`, forwarding is activated
- Multiplexers in the datapath select forwarded values instead of register file outputs

---

## Part IV: Load-Use Hazard

### Hazard Scenario Implemented:

In the template code, I inserted the following instructions:

```assembly
lw  x7, 4(x5)      # Load word from memory into register x7
add x9, x7, x7     # Immediately use x7 in the next instruction
```

**Corresponding addresses from objdump:**
```
80000020:  0042a383    lw   t2,4(t0)      # t2 = x7
80000024:  007384b3    add  s1,t2,t2      # s1 = x9
```

### Why This Creates a Hazard:

This is a **load-use data hazard** - the most common type of hazard that cannot be resolved by forwarding alone:

**Timeline:**
```
Cycle 1: lw is in Execute  → calculates address (x5 + 4)
Cycle 2: lw is in Memory   → reads from memory, data becomes available
         add is in Execute → needs x7 value NOW!
```

**The Problem:**
- The `add` instruction needs the value of `x7` when it's in the Execute stage
- But the `lw` instruction only produces that value at the END of the Memory stage
- Even with forwarding, the data arrives one cycle too late!

**Solution - Pipeline Stall:**
The Hazard Unit detects this situation and:
1. Asserts `StallF = 1` when the dependent `add` instruction is decoded
2. Stalls the pipeline for 1 cycle:
   - Fetch stage: holds (doesn't fetch new instruction)
   - Decode stage: holds (doesn't advance)
   - Execute stage: inserts a bubble (NOP)
3. After the stall, the load data is available and can be forwarded
4. The `add` executes with the correct value

### Observable Behavior in GTKWave:

**Look for these signals around PC = 80000020-80000024:**

1. **StallF = 1:** Goes high for one cycle when the hazard is detected
2. **PCF doesn't advance:** Stays at the same address during the stall
3. **Register dependencies visible:**
   - `RdM = 07` (lw is writing to x7 in Memory stage)
   - `Rs1E = 07` and `Rs2E = 07` (add needs x7 in Execute stage)
4. **Bubble insertion:** A NOP appears in the pipeline

**Screenshot should show:**
- Clock cycles around t=XXXps (when this instruction executes)
- `StallF = 1` for one cycle
- `PCF`, `PCD`, `PCE` showing the stall
- `Rs1E`, `Rs2E`, `RdM` showing the register dependency

---

### Summary:
The load-use hazard demonstrates the **limit of data forwarding**. While forwarding eliminates stalls for most data dependencies, load instructions require memory access, and the next instruction cannot proceed until that data is available. The 1-cycle stall is the minimum penalty required to maintain correctness.

---

**END OF ANSWERS**
