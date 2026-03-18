# Quick Reference: Your CoreMark Results

## System Tested
**Intel Core i7-11375H @ 3.30GHz** (4 cores, 8 threads)  
**Compiler:** GCC 15.2.0 (MSYS2)

## Benchmark Results (Iterations/Second)

```
┌─────────────────┬──────────────┬────────────┐
│ Optimization    │ Performance  │ vs Default │
├─────────────────┼──────────────┼────────────┤
│ -O0             │   5,278 ⬇⬇⬇  │  -74.49%   │
│ -O1             │  19,150 ⬇    │   -7.44%   │
│ -O2 (default)   │  20,688 ━    │    0.00%   │
│ -O3             │  21,501 ⬆    │   +3.93%   │
│ -Ofast ★        │  21,612 ⬆⬆   │   +4.46%   │
│ -march=native   │  20,017 ⬇    │   -3.24%   │
└─────────────────┴──────────────┴────────────┘

★ Best Performance
```

## Key Takeaways

1. **292% performance gain** from -O0 to -O2
2. **Only 4.46% additional gain** from -O2 to -Ofast
3. **-march=native unexpectedly slower** than generic -O2
4. **All runs validated correctly** (CRC checksums matched)

## To Run More Tests

```powershell
cd c:\Users\gunde\Desktop\344Labs\344LAB3\coremark

# Set PATH (if needed in new terminal)
$env:Path = "C:\Program Files\Git\bin;C:\msys64\mingw64\bin;" + $env:Path

# Compile with specific optimization
mingw32-make PORT_DIR=simple XCFLAGS="-O3" compile

# Run benchmark
.\coremark.exe 0x0 0x0 0x66 0 7 1 2000
```

## Files to Submit

📄 **LAB3_REPORT.md** - Your complete lab report (ready!)

## What's Included in Report

✅ All benchmark data (30 runs)  
✅ CPU specifications  
✅ Performance analysis  
✅ CoreMark algorithm descriptions  
✅ RISC-V ISA extension documentation  
✅ Professional conclusions

---

**Report Location:**  
`c:\Users\gunde\Desktop\344Labs\344LAB3\LAB3_REPORT.md`

Open it, add your name, and you're ready to submit! 🚀
