# Lab 3: CoreMark Benchmark Setup Instructions

## Prerequisites

### 1. Install Git
You need to install Git for Windows:
- Download from: https://git-scm.com/download/win
- Run the installer and follow the default installation steps
- After installation, restart VS Code or open a new terminal

### 2. Install a C Compiler
You need a C compiler. Choose one of these options:

#### Option A: MinGW-w64 (Recommended for Windows)
1. Download from: https://www.mingw-w64.org/downloads/
2. Or use MSYS2: https://www.msys2.org/
3. Add the bin directory to your PATH

#### Option B: Visual Studio Build Tools
1. Download Visual Studio Build Tools
2. Install "Desktop development with C++" workload

#### Option C: WSL (Windows Subsystem for Linux)
1. Install WSL2: `wsl --install` in PowerShell (as Administrator)
2. This provides a Linux environment with gcc

## Setup Steps

Once Git and a C compiler are installed:

### 1. Clone CoreMark
```powershell
cd c:\Users\gunde\Desktop\344Labs\344LAB3
git clone https://github.com/eembc/coremark.git
cd coremark
```

### 2. Build and Run CoreMark (Default Settings)
```powershell
make
```

**Note the "Iterations/Sec" value from the output.**

### 3. Run Multiple Times for Average
Run the benchmark at least 5 times:
```powershell
# Run 1
make

# Run 2
make

# Run 3
make

# Run 4
make

# Run 5
make
```

Record each "Iterations/Sec" value and calculate the average.

### 4. Test Different Compiler Optimizations

For each optimization level, clean and rebuild:

#### No Optimization (-O0)
```powershell
make clean
make XCFLAGS="-O0"
# Run 5 times and record results
```

#### Optimization Level 1 (-O1)
```powershell
make clean
make XCFLAGS="-O1"
# Run 5 times and record results
```

#### Optimization Level 2 (-O2)
```powershell
make clean
make XCFLAGS="-O2"
# Run 5 times and record results
```

#### Optimization Level 3 (-O3)
```powershell
make clean
make XCFLAGS="-O3"
# Run 5 times and record results
```

#### Fast Optimization (-Ofast)
```powershell
make clean
make XCFLAGS="-Ofast"
# Run 5 times and record results
```

#### Native Architecture (-march=native)
```powershell
make clean
make XCFLAGS="-march=native"
# Run 5 times and record results
```

### 5. Get CPU Information

To get your CPU information:

```powershell
# In PowerShell
Get-WmiObject Win32_Processor | Select-Object Name, MaxClockSpeed, NumberOfCores, NumberOfLogicalProcessors
```

Or if using WSL:
```bash
lscpu
```

### 6. Review README.md
After each run, a `README.md` file is generated in the coremark directory. Review it to understand the algorithms being tested.

## Tips for Consistent Results

1. **Close other applications** to minimize background processes
2. **Disable CPU frequency scaling** if possible (may require BIOS settings)
3. **Keep your laptop plugged in** to prevent power-saving throttling
4. **Run benchmarks when system is idle**
5. **Take the average** of multiple runs to account for variability

## Next Steps

After completing the benchmarks, fill in the results in `LAB3_REPORT.md`.
