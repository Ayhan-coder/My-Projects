# Lab 3 Quick Start Guide

## Overview
This lab involves benchmarking CPU performance using CoreMark with different compiler optimizations and documenting the results along with RISC-V ISA extension information.

## Files in This Directory

1. **LAB3_SETUP_INSTRUCTIONS.md** - Detailed setup instructions for installing prerequisites and running CoreMark
2. **LAB3_REPORT.md** - Your main report template (FILL THIS IN with your results)
3. **DATA_COLLECTION.md** - Simple data collection sheet for recording benchmark results
4. **run_benchmarks.ps1** - Automated PowerShell script to run all benchmarks (use after setup)
5. **README.md** - This file

## Quick Start Steps

### Step 1: Install Prerequisites (REQUIRED)
You need Git and a C compiler. Follow instructions in **LAB3_SETUP_INSTRUCTIONS.md**

Recommended:
- **Git for Windows:** https://git-scm.com/download/win
- **MSYS2 (includes MinGW-w64):** https://www.msys2.org/

### Step 2: Clone CoreMark
```powershell
cd c:\Users\gunde\Desktop\344Labs\344LAB3
git clone https://github.com/eembc/coremark.git
cd coremark
```

### Step 3: Option A - Manual Benchmarking
Follow the detailed instructions in **LAB3_SETUP_INSTRUCTIONS.md** and record results in **DATA_COLLECTION.md**

### Step 3: Option B - Automated Benchmarking
```powershell
cd c:\Users\gunde\Desktop\344Labs\344LAB3
.\run_benchmarks.ps1
```

Note: If you get "execution policy" error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 4: Fill in Your Report
Open **LAB3_REPORT.md** and fill in:
- Your benchmark results
- CPU information
- Analysis of results
- The algorithm and ISA extension descriptions are already provided as reference

## What's Already Done for You

The **LAB3_REPORT.md** file includes:

✅ **Complete explanations of CoreMark algorithms:**
- List Processing
- Matrix Manipulation
- State Machine
- CRC

✅ **Detailed descriptions of RISC-V ISA extensions:**
- RV32I
- RV32IM
- RV32IMC
- RV32GC
- RV64I

✅ **Formatted tables** ready for your benchmark data

## What You Need to Do

1. ⬜ Install Git and a C compiler
2. ⬜ Clone and build CoreMark
3. ⬜ Run benchmarks with different optimization flags
4. ⬜ Collect CPU information
5. ⬜ Fill in the benchmark results tables in LAB3_REPORT.md
6. ⬜ Write your analysis of the results
7. ⬜ Add your name and course information
8. ⬜ Review and customize the algorithm/ISA descriptions if needed

## Tips for Success

- **Close other applications** when running benchmarks for consistent results
- **Run each configuration 5 times** and take the average
- **Keep your laptop plugged in** to prevent CPU throttling
- **Wait for system to be idle** before running benchmarks
- **Document your compiler version** and CPU model

## Need Help?

- Check **LAB3_SETUP_INSTRUCTIONS.md** for detailed setup help
- Read the CoreMark README.md generated after each run
- Visit https://github.com/eembc/coremark for official documentation

## After Completion

Submit **LAB3_REPORT.md** with all sections completed.

Good luck! 🚀
