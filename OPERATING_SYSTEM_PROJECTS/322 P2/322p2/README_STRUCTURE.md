# CMPE322 Project 2 - Directory Structure

## Organization

```
322p2/
├── src/                          # Core implementation files
│   ├── hash_parallelization.c    # Main implementation
│   ├── hash_parallelization_v3.h # Header file
│   └── hash_parallelization.so   # Compiled shared library
├── tests/                        # All test files
│   ├── test_hash.c              # Basic test
│   ├── extreme_test.c           # 1.2M entries (h_1)
│   ├── mega_test.c              # 1.5M entries (h_1)
│   ├── giga_test.c              # 10M entries (h_1)
│   ├── ultra_test.c             # 100M entries (h_1)
│   ├── fuzz_test.c              # 11 different configurations (h_1)
│   ├── h2_test.c                # H2 test suite
│   ├── h2_mega_test.c           # 1M entries (h_2)
│   ├── final_test1-4.c          # Final validation tests
│   └── [compiled executables]
├── docs/                         # Documentation
│   ├── report.tex               # LaTeX report
│   ├── report.md                # Markdown report
│   ├── README.txt               # Original readme
│   ├── IMPLEMENTATION.md        # Implementation notes
│   ├── COMPLETE_GUIDE.md        # Complete guide
│   ├── QUICK_REFERENCE.txt      # Quick reference
│   └── FINAL_CHECKLIST.txt      # Final checklist
├── Makefile                      # Build system
├── generate_pdf.sh              # PDF generation script
├── prepare_submission.sh        # Submission preparation
├── final_validation.sh          # Validation script
└── PROJECT2_v2.pdf              # Project specification

```

## Building

### Build shared library:
```bash
make all
```

### Build and run specific tests:
```bash
make run_giga      # 10M entries (h_1)
make run_ultra     # 100M entries (h_1)
make run_fuzz      # Fuzz test suite
make run_h2        # H2 test suite
make run_h2_mega   # 1M entries (h_2)
```

### Clean build artifacts:
```bash
make clean
```

## Test Results Summary

### H_1 Tests (8 threads):
- extreme_test: 1.2M entries → 0.147s, 3.71x speedup
- mega_test: 1.5M entries → 0.148s, 3.69x speedup
- giga_test: 10M entries → 0.839s, 4.25x speedup
- ultra_test: 100M entries → ~8-10s, 4.71x speedup

### H_2 Tests:
- h2_mega: 1M entries (K=1000) → 7.37s
- Note: H1 is ~1000x faster than H2 for same workload

## System Requirements
- GCC compiler with pthread support
- POSIX-compliant system (Linux/WSL)
- Minimum 16GB RAM recommended for ultra tests
