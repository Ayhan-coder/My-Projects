# Lab 3: CoreMark Benchmark Report

**Name:** [Your Name]  
**Partner:** [Partner Name]  
**Date:** October 31, 2025  
**Course:** [Course Number]

---

## System Information

**CPU Model:** 11th Gen Intel(R) Core(TM) i7-11375H @ 3.30GHz  
**Base Clock Frequency:** 3300 MHz  
**Max Clock Frequency:** 3302 MHz  
**Number of Cores:** 4  
**Number of Logical Processors:** 8  
**Operating System:** Windows  
**Compiler:** GCC version 15.2.0 (MSYS2 MinGW-w64)

---

## Benchmark Results

### Default Build Performance

| Run # | Iterations/Sec |
|-------|----------------|
| 1     | 19290.12       |
| 2     | 19227.07       |
| 3     | 19342.36       |
| 4     | 19753.74       |
| 5     | 19490.64       |
| **Average** | **19420.79** |

### Compiler Optimization Comparison

| Optimization Flag | Run 1 | Run 2 | Run 3 | Run 4 | Run 5 | **Average** | **% Change vs Default** |
|-------------------|-------|-------|-------|-------|-------|-------------|-------------------------|
| -O0               | 4607.23 | 4617.87 | 4605.82 | 4631.06 | 4926.11 | **4677.62** | **-75.91%** |
| -O1               | 18389.11 | 18310.55 | 18392.50 | 18426.39 | 18374.47 | **18378.60** | **-5.37%** |
| -O2 (Default)     | 19290.12 | 19227.07 | 19342.36 | 19753.74 | 19490.64 | **19420.79** | **0%** |
| -O3               | 20458.27 | 20578.95 | 20529.67 | 20604.40 | 20567.67 | **20547.79** | **+5.80%** |
| -Ofast            | 17572.63 | 19228.30 | 20207.46 | 20326.58 | 20348.64 | **19536.72** | **+0.60%** |
| -march=native     | 19021.05 | 19146.08 | 19211.07 | 19133.87 | 19196.31 | **19141.68** | **-1.44%** |

**Formula for % Change:** `((New Value - Default Value) / Default Value) × 100`

---

## Analysis of Results

### Performance Observations

**1. Impact of Optimization Levels:**

The benchmark results clearly demonstrate the significant impact of compiler optimization on CPU performance. The progression from `-O0` (no optimization) to `-Ofast` shows dramatic performance improvements:

- **-O0 (No Optimization)**: At 4,678 iterations/sec, this represents a 75.91% performance **decrease** compared to the default -O2 setting. Without optimization, the compiler generates straightforward but inefficient machine code, resulting in excessive memory operations, redundant calculations, and poor instruction scheduling.

- **-O1 (Basic Optimization)**: Performance jumps to 18,379 iterations/sec, recovering most of the ground but still 5.37% slower than -O2. This level enables fundamental optimizations like common subexpression elimination and dead code removal without aggressive transformations.

- **-O2 (Default)**: At 19,421 iterations/sec, this is GCC's recommended optimization level for production code, balancing performance with compilation time and code size. It includes loop optimizations, vectorization, and instruction scheduling.

- **-O3 (Aggressive Optimization)**: Shows a 5.80% improvement over -O2 (20,548 iterations/sec), enabling more aggressive loop unrolling, function inlining, and other transformations that may increase code size but improve execution speed. This achieved the best overall performance among all tested configurations.

- **-Ofast (Maximum Speed)**: Achieves 19,537 iterations/sec (+0.60% over -O2). While this level relaxes strict standards compliance (e.g., IEEE 754 floating-point) for additional speed, in this benchmark it only marginally outperformed -O2, showing that the aggressive optimizations don't always translate to significant gains depending on the workload.

The key finding is that going from -O0 to -O2 provides a **315% performance increase**, while -O2 to -O3 adds another 5.80%. This demonstrates that most performance gains come from basic optimizations, with diminishing returns at higher levels.

**2. Performance Variations:**

Across all optimization levels, results showed reasonable consistency between runs, with variations typically under 5%. Some notable observations:

- The -O0 runs showed moderate variation (from 4,605 to 4,926 iterations/sec), likely due to longer execution times making system variability more apparent.
- Higher optimization levels (-O2, -O3) showed relatively tight clustering of results, indicating more predictable performance.
- The -Ofast configuration showed higher variance, with Run 1 at 17,573 significantly lower than Runs 3-5 (20,207-20,349), suggesting initial cold-start effects or CPU ramping behavior.

The variations can be attributed to factors such as CPU thermal throttling, turbo boost behavior, background processes, and operating system scheduling decisions. Running multiple iterations and calculating averages helps mitigate these effects.

**3. Architecture-Specific Optimizations:**

The `-march=native` flag, which tells the compiler to optimize for the specific CPU architecture (11th Gen Intel Core i7-11375H), surprisingly performed **worse** than -O2 by 1.44%, achieving only 19,142 iterations/sec. This unexpected result can be explained by several factors:

- **Instruction Mix Trade-offs**: While `-march=native` enables advanced instructions specific to the Tiger Lake architecture (AVX-512, enhanced SSE), CoreMark's workload may not benefit from these specialized instructions. The benchmark focuses on integer operations, pointer chasing, and branching rather than vectorizable floating-point operations.

- **Code Size Impact**: Architecture-specific optimizations can increase code size, potentially leading to more instruction cache misses, which would harm performance on CoreMark's relatively small but frequently-executed loops.

- **Interaction with Other Flags**: When `-march=native` is used without other optimization flags, it defaults to -O0, which may explain the lower performance in our test configuration.

This result highlights an important lesson for embedded system development: **blindly enabling all optimizations doesn't guarantee better performance**. The effectiveness of optimizations depends heavily on the workload characteristics, and benchmark-driven validation is essential when selecting processor designs and compiler settings for production systems.

---

## CoreMark Algorithm Explanation

CoreMark exercises several key computational workloads that are representative of embedded and general-purpose processing tasks:

### 1. **List Processing (Linked Lists)**
[Explain what list processing tests and why it's important]

- **Operations tested:** 
  - Finding and removing elements
  - Sorting
  - Traversal
- **Why it matters:** Tests pointer chasing, cache performance, and branch prediction
- **Relevance:** Common in embedded systems for task scheduling, memory management

### 2. **Matrix Manipulation**
[Explain matrix operations tested]

- **Operations tested:**
  - Matrix multiplication
  - Addition
  - Integer operations
- **Why it matters:** Tests computational throughput and data locality
- **Relevance:** Signal processing, graphics, control systems

### 3. **State Machine**
[Explain state machine testing]

- **Operations tested:**
  - State transitions
  - String parsing
  - Pattern matching
- **Why it matters:** Tests branch prediction and control flow
- **Relevance:** Protocol handlers, parsers, control logic in embedded systems

### 4. **CRC (Cyclic Redundancy Check)**
[Explain CRC operations]

- **Operations tested:**
  - Bit manipulation
  - Checksum calculation
- **Why it matters:** Tests bit-level operations and integer arithmetic
- **Relevance:** Data integrity verification, communications

### Key Characteristics of CoreMark

- **No I/O operations:** Focuses purely on CPU performance
- **Minimal memory footprint:** Designed for embedded systems
- **Deterministic:** Same input always produces same output
- **Portable:** Runs on any system with a C compiler
- **Self-validating:** Checks correctness of results

---

## RISC-V ISA Extension Sets

### RV32I - Base Integer Instruction Set (32-bit)

**Description:**  
RV32I is the base integer instruction set for 32-bit RISC-V processors. It is the foundation upon which all other RISC-V extensions are built.

**Key Features:**
- **32 general-purpose registers** (x0-x31), each 32 bits wide
  - x0 is hardwired to zero
  - x1-x31 are general-purpose registers
- **32-bit address space** (4 GB addressable memory)
- **Integer arithmetic and logical operations**
  - ADD, SUB, AND, OR, XOR, shifts
- **Load/Store architecture**
  - LW (load word), SW (store word)
  - LH/LHU (load halfword), SH (store halfword)
  - LB/LBU (load byte), SB (store byte)
- **Control transfer instructions**
  - Conditional branches: BEQ, BNE, BLT, BGE, BLTU, BGEU
  - Unconditional jumps: JAL, JALR
- **41 instructions total** (minimal, RISC design)

**Use Cases:**  
Suitable for simple embedded systems, educational purposes, and as a base for more complex configurations. Can run basic software but lacks hardware multiplication/division.

---

### RV32IM - Base + Multiply/Divide Extension

**Description:**  
RV32IM adds the "M" (Multiply/Divide) standard extension to the base RV32I instruction set, providing hardware support for multiplication and division operations.

**Additional Features (M Extension):**
- **Multiplication instructions:**
  - MUL: Multiply (lower 32 bits of result)
  - MULH: Multiply high (signed × signed, upper 32 bits)
  - MULHSU: Multiply high (signed × unsigned)
  - MULHU: Multiply high (unsigned × unsigned)
- **Division instructions:**
  - DIV: Signed division
  - DIVU: Unsigned division
  - REM: Signed remainder
  - REMU: Unsigned remainder

**Performance Impact:**  
Without hardware multiply/divide, these operations must be implemented in software (much slower). The M extension provides significant performance improvements for:
- Mathematical computations
- Array indexing and address calculation
- Cryptographic operations
- Signal processing algorithms

**Use Cases:**  
General-purpose embedded systems requiring efficient arithmetic operations. Standard for most practical applications.

---

### RV32IMC - Base + Multiply/Divide + Compressed Instructions

**Description:**  
RV32IMC adds the "C" (Compressed) standard extension to RV32IM, providing 16-bit compressed instruction encodings alongside standard 32-bit instructions.

**Additional Features (C Extension):**
- **16-bit instruction formats** for common operations
  - Reduces code size by ~25-30%
  - All compressed instructions have 32-bit equivalents
- **Compressed instruction examples:**
  - C.LWSP / C.SWSP: Load/store word from/to stack pointer
  - C.LW / C.SW: Load/store word
  - C.J / C.JAL: Compressed jumps
  - C.BEQZ / C.BNEZ: Compressed branches
  - C.MV / C.ADD: Register operations
  - C.LI: Load immediate
  - C.ADDI4SPN: Add immediate to SP

**Benefits:**
1. **Reduced code size:** Critical for systems with limited instruction memory
2. **Improved instruction cache utilization:** More instructions fit in cache
3. **Lower memory bandwidth:** Fewer instruction fetches required
4. **No performance penalty:** Decompressed internally by the CPU

**Use Cases:**  
Cost-sensitive embedded systems with limited memory. Provides better code density without sacrificing performance. Common in microcontrollers and IoT devices.

---

### RV32GC - General-Purpose Configuration

**Description:**  
RV32GC represents a "General-purpose" configuration that combines multiple standard extensions, making it suitable for full-featured embedded and application processors.

**Components (G = IMAFD):**
- **I:** Base integer instructions (RV32I)
- **M:** Integer multiply/divide
- **A:** Atomic instructions
- **F:** Single-precision floating-point
- **D:** Double-precision floating-point
- **C:** Compressed instructions (added to make "GC")

**Atomic Extension (A):**
- **Load-reserved/store-conditional:** LR.W, SC.W
- **Atomic memory operations (AMO):**
  - AMOSWAP: Atomic swap
  - AMOADD: Atomic add
  - AMOAND, AMOOR, AMOXOR: Atomic logical ops
  - AMOMIN, AMOMAX: Atomic min/max (signed/unsigned)
- **Use case:** Synchronization primitives, lock-free data structures, multi-core systems

**Floating-Point Extensions (F & D):**
- **32 floating-point registers** (f0-f31)
- **F extension:** 32-bit IEEE 754 single-precision operations
  - FADD.S, FSUB.S, FMUL.S, FDIV.S, FSQRT.S
  - FLW, FSW (load/store)
- **D extension:** 64-bit IEEE 754 double-precision operations
  - FADD.D, FSUB.D, FMUL.D, FDIV.D, FSQRT.D
  - FLD, FSD (load/store)
- **Fused multiply-add:** FMADD, FMSUB, FNMADD, FNMSUB

**Use Cases:**  
Full-featured embedded systems, application processors, systems requiring floating-point computation (scientific applications, graphics, DSP), multi-threaded applications requiring synchronization.

---

### RV64I - Base Integer Instruction Set (64-bit)

**Description:**  
RV64I is the 64-bit version of the base integer instruction set. It extends RV32I to support 64-bit address spaces and 64-bit integer operations.

**Key Differences from RV32I:**
- **64-bit general-purpose registers** (x0-x31), each 64 bits wide
- **64-bit address space** (16 exabytes addressable memory)
- **Additional 64-bit operations:**
  - LD (load doubleword), SD (store doubleword)
  - ADDIW, SLLIW, SRLIW, SRAIW (32-bit word operations on 64-bit registers)
  - ADDW, SUBW, SLLW, SRLW, SRAW (32-bit word arithmetic)

**Word Operations (W suffix):**
- Operate on the lower 32 bits of 64-bit registers
- Sign-extend results to 64 bits
- Allows efficient 32-bit arithmetic in 64-bit mode
- Maintains compatibility with 32-bit code

**64-bit Specific Instructions:**
- All RV32I instructions work on full 64-bit values
- New instructions for 32-bit operations in 64-bit mode
- Expanded immediate ranges for some instructions

**Use Cases:**
- **Large address spaces:** Applications requiring >4GB memory
- **High-performance computing:** Scientific computing, database systems
- **Servers and workstations:** General-purpose computing with large datasets
- **Future-proofing:** As memory requirements grow beyond 32-bit limits

**Extensions:**  
Like RV32, RV64 can be combined with extensions:
- **RV64IM:** With multiply/divide
- **RV64IMC:** With multiply/divide and compressed instructions
- **RV64GC:** Full general-purpose configuration (IMAFDC)

---

## Comparison: Why Different Extension Sets Matter

| Feature | RV32I | RV32IM | RV32IMC | RV32GC | RV64I |
|---------|-------|--------|---------|--------|-------|
| Multiply/Divide | Software | Hardware | Hardware | Hardware | Software (or +M) |
| Code Size | Baseline | Baseline | ~70-75% | ~70-75% | Larger (64-bit) |
| Floating-Point | Software | Software | Software | Hardware | Software (or +FD) |
| Atomics | No | No | No | Yes | No (or +A) |
| Address Space | 32-bit (4GB) | 32-bit (4GB) | 32-bit (4GB) | 32-bit (4GB) | 64-bit (16EB) |
| Typical Use | Education, minimal systems | Embedded controllers | Memory-constrained embedded | Full-featured embedded/apps | High-performance, servers |

---

## Conclusions

This laboratory exercise provided valuable hands-on experience with processor benchmarking and demonstrated several key principles relevant to embedded systems development:

**1. Compiler Optimizations are Critical:** The 315% performance difference between unoptimized (-O0) and default optimized code (-O2) underscores that compiler optimization is not optional for performance-critical embedded applications. The results show that -O3 provided the best performance with a 5.80% gain over -O2, while -Ofast offered minimal improvement, suggesting that -O2 or -O3 represent the sweet spot for most production code.

**2. Benchmarking Enables Informed Decisions:** For the IoT startup scenario, having quantitative performance data allows evidence-based processor selection rather than relying on marketing claims or assumptions. Understanding that a given workload achieves ~20,548 iterations/sec on an Intel Core i7-11375H with GCC 15.2.0 provides a baseline for comparing RISC-V and other processor architectures in future labs.

**3. Algorithm Understanding Matters:** CoreMark's focus on four key computational patterns (list processing, matrix operations, state machines, and CRC calculations) provides a representative workload for embedded systems. Recognizing which algorithms stress which processor features (branch prediction for state machines, cache performance for list traversal, arithmetic throughput for matrix operations) helps in matching processor capabilities to application requirements.

**4. RISC-V Configurability Trades Off Complexity vs. Performance:** The detailed examination of RISC-V ISA extensions (from minimal RV32I to full-featured RV32GC) illustrates the design philosophy of building up capability through modular extensions. For the IoT devices, selecting the right extension set (e.g., RV32IMC for code density vs. RV32GC for floating-point capability) will directly impact chip cost, power consumption, and application performance.

**5. Architecture-Specific Optimizations Require Validation:** The counterintuitive result that `-march=native` performed worse than generic -O2 optimization (by 1.44%) demonstrates that assumptions about performance must be tested. In selecting a processor design for manufacturing thousands of devices, similar validation of RISC-V configurations will be essential to avoid costly mistakes.

This benchmark establishes a methodology and baseline for the upcoming Lab 3 exercises, where we will compare these x86-64 results against various RISC-V processor configurations to determine the optimal design for production deployment.

---

## References

1. CoreMark Official Repository: https://github.com/eembc/coremark
2. EEMBC CoreMark Documentation: https://www.eembc.org/coremark/
3. RISC-V ISA Specifications: https://riscv.org/technical/specifications/
4. GCC Optimization Options: https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html

---

## Appendix

### Sample CoreMark Output
```
2K performance run parameters for coremark.
CoreMark Size    : 666
Total ticks      : 14538
Total time (secs): 14.538000
Iterations/Sec   : 20635.575733
Iterations       : 300000
Compiler version : GCC15.2.0
Compiler flags   : -O2
Memory location  : STACK
seedcrc          : 0xe9f5
[0]crclist       : 0xe714
[0]crcmatrix     : 0x1fd7
[0]crcstate      : 0x8e3a
[0]crcfinal      : 0xcc42
Correct operation validated. See README.md for run and reporting rules.
CoreMark 1.0 : 20635.575733 / GCC15.2.0 -O2 / STACK
```

### Build Commands Used
```powershell
# Set up PATH for gcc and make (if needed in new terminal)
$env:Path = "C:\Program Files\Git\bin;C:\msys64\mingw64\bin;" + $env:Path

# Navigate to CoreMark directory
cd c:\Users\gunde\Desktop\344Labs\344LAB3\coremark

# Build with different optimization levels
mingw32-make PORT_DIR=simple XCFLAGS="-O0" compile
mingw32-make PORT_DIR=simple XCFLAGS="-O1" compile
mingw32-make PORT_DIR=simple XCFLAGS="-O2" compile
mingw32-make PORT_DIR=simple XCFLAGS="-O3" compile
mingw32-make PORT_DIR=simple XCFLAGS="-Ofast" compile
mingw32-make PORT_DIR=simple XCFLAGS="-march=native" compile

# Run benchmark (example for -O2)
.\coremark.exe 0x0 0x0 0x66 0 7 1 2000

# Clean before rebuilding
mingw32-make PORT_DIR=simple clean
```

### CPU Information Output
```powershell
PS C:\Users\gunde\Desktop\344Labs\344LAB3> Get-WmiObject Win32_Processor | Select-Object Name, MaxClockSpeed, NumberOfCores, NumberOfLogicalProcessors | Format-List

Name                      : 11th Gen Intel(R) Core(TM) i7-11375H @ 3.30GHz
MaxClockSpeed             : 3302
NumberOfCores             : 4
NumberOfLogicalProcessors : 8
```

### GCC Version Information
```
gcc.exe (Rev8, Built by MSYS2 project) 15.2.0
Copyright (C) 2025 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

### Complete Benchmark Run Example (-O3 Optimization)
```
=== Testing -O3 ===
Run 1 : 20458.265139
Run 2 : 20578.954589
Run 3 : 20529.665366
Run 4 : 20604.395604
Run 5 : 20567.667626
Average: 20547.79 Iterations/Sec
```
