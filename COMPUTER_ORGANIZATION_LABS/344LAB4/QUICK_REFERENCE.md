# Quick Reference: Fibonacci Instruction Values

## All Instructions with Hex Encodings

```
PC Address | Hex Encoding | Assembly Instruction         | Expected in InstrD (1 cycle later)
-----------|--------------|------------------------------|-----------------------------------
0x80000000 | 0x00010297   | auipc t0,0x10                | After PC=0x80000000 fetches
0x80000004 | 0x00028293   | mv t0,t0                     | After PC=0x80000004 fetches
0x80000008 | 0x00a00313   | li t1,10                     | After PC=0x80000008 fetches
0x8000000c | 0x00000393   | li t2,0                      | After PC=0x8000000c fetches
0x80000010 | 0x00100e13   | li t3,1                      | After PC=0x80000010 fetches
0x80000014 | 0x0072a023   | sw t2,0(t0)                  | After PC=0x80000014 fetches
0x80000018 | 0x00428293   | addi t0,t0,4                 | After PC=0x80000018 fetches
0x8000001c | 0x01c2a023   | sw t3,0(t0)                  | After PC=0x8000001c fetches

0x80000020 | 0x02030063   | beqz t1,80000040 (LOOP)      | After PC=0x80000020 fetches ← LOOP START
0x80000024 | 0x007e0eb3   | add t4,t3,t2                 | After PC=0x80000024 fetches
0x80000028 | 0x00428293   | addi t0,t0,4                 | After PC=0x80000028 fetches
0x8000002c | 0x01d2a023   | sw t4,0(t0)                  | After PC=0x8000002c fetches
0x80000030 | 0x000e0393   | mv t2,t3                     | After PC=0x80000030 fetches
0x80000034 | 0x000e8e13   | mv t3,t4                     | After PC=0x80000034 fetches
0x80000038 | 0xfff30313   | addi t1,t1,-1                | After PC=0x80000038 fetches
0x8000003c | 0xfe5ff06f   | j 80000020 (jump to LOOP)    | After PC=0x8000003c fetches ← JUMP!

0x80000040 | 0x0000006f   | j 80000040 (infinite loop)   | After PC=0x80000040 fetches ← DONE/HALT
```

---

## How to Use This Table in GTKWave:

### Method 1: Direct Match
```
1. Look at PCF value in GTKWave (e.g., 0x80000024)
2. Find that address in column 1 above
3. Look at expected InstrD (column 3)
4. BUT: InstrD shows instruction from PREVIOUS fetch
5. So if PCF=0x80000024 now, InstrD should show 0x80000020's instruction
   → InstrD should be 0x02030063
```

### Method 2: Account for Pipeline Delay

```
If at time T:
  PCF = 0x80000028    (currently fetching addi t0,t0,4)
  
Then InstrD should show:
  = instruction that was fetched last cycle
  = instruction at PC=0x80000024 (from previous cycle)
  = 0x007e0eb3 (add t4,t3,t2)
```

---

## Pipeline Timing Example

```
Cycle  | PCF       | InstrD      | Description
-------|-----------|-------------|---------------------------------------
1      | 0x80000000| 0x????????  | Fetch _start, decode old/invalid
2      | 0x80000004| 0x00010297  | Fetch mv, decode auipc ← MATCH PC from cycle 1
3      | 0x80000008| 0x00028293  | Fetch li t1, decode mv ← MATCH PC from cycle 2
4      | 0x8000000c| 0x00a00313  | Fetch li t2, decode li t1 ← MATCH PC from cycle 3
...
N      | 0x80000020| 0x01c2a023  | Fetch beqz, decode sw t3 ← MATCH PC from cycle N-1
N+1    | 0x80000024| 0x02030063  | Fetch add, decode beqz ← MATCH PC from cycle N
N+2    | 0x80000028| 0x007e0eb3  | Fetch addi, decode add ← MATCH PC from cycle N+1
N+3    | 0x8000002c| 0x00428293  | Fetch sw, decode addi ← MATCH PC from cycle N+2
```

**KEY INSIGHT:** InstrD at cycle N = Instruction at (PCF from cycle N-1)

---

## Common Hex Values to Look For

These are the KEY instruction encodings in your fibonacci program:

| Instruction | Hex Value  | When It Appears       |
|------------|-----------|----------------------|
| auipc t0   | 0x00010297| Initial setup         |
| mv t0      | 0x00028293| Initial setup         |
| li t1,10   | 0x00a00313| Initialize counter    |
| li t2,0    | 0x00000393| Initialize fib(0)     |
| li t3,1    | 0x00100e13| Initialize fib(1)     |
| sw (store) | 0x0072a023| Store V[0]            |
| addi t0    | 0x00428293| Pointer increment     |
| sw t3      | 0x01c2a023| Store V[1]            |
| **beqz**   | **0x02030063**| **LOOP condition** ← Most common in loop|
| **add t4** | **0x007e0eb3**| **Add fibs** ← Most common in loop    |
| **j 80000020** | **0xfe5ff06f**| **Jump back** ← Causes FlushD! |
| j 80000040 | 0x0000006f| Halt loop              |

---

## What Values Are NOT Expected

If you see these, something is wrong:
- InstrD > 0xffffffff (shouldn't happen, it's 32-bit)
- InstrD = 0x00000000 for many cycles (unless at halt)
- InstrD = 0xxxxxxxxx (completely random, suggests corruption)

---

## Debug Script for You:

Pick a time in GTKWave (e.g., t=350ps) and fill this out:

```
Time: t=_____ps

PCF value (what address is being fetched):  0x________

InstrD value (what instruction is in decode): 0x________

What instruction should be at PCF address (from objdump):
  → Assembly: ___________________________
  → Expected Hex: 0x________

Does InstrD match instruction from PCF - 4 cycles ago?
  YES / NO

Additional notes:
  ________________________________________________________________________________
```

Once you fill this out and share, I can tell you exactly what's wrong! 

---

## If Still Stuck:

1. **Take a screenshot** of GTKWave showing:
   - clk signal
   - PCF value
   - InstrD value
   - The timeline/address

2. **Tell me the time** you're looking at

3. **Tell me what values** you see

4. **I'll help identify** the exact issue!

