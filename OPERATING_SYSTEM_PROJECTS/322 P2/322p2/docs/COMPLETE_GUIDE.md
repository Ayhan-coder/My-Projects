# CMPE322 Project 2 - Complete Implementation Guide

## Project Overview
This project implements parallel hashing algorithms using POSIX threads (pthread library). Two hash functions are implemented: h_1 (optimized for speedup) and h_2 (prone to deadlocks, requiring careful lock management).

## Files Created

### Required for Submission:
1. **hash_parallelization.c** - Main implementation file
2. **hash_parallelization.so** - Shared object library (compiled from .c file)
3. **report.pdf** - Project report (compile from report.tex)

### Supporting Files:
- **hash_parallelization_v3.h** - Header file (provided, DO NOT MODIFY)
- **Makefile** - Build automation
- **test_hash.c** - Test program for validation
- **report.tex** - LaTeX source for report
- **prepare_submission.sh** - Submission preparation script

## Compilation Instructions

### Option 1: Using GCC directly
```bash
# Create shared object library (required for submission)
gcc -shared -fPIC -pthread -o hash_parallelization.so hash_parallelization.c -lrt

# Compile test program (optional)
gcc -pthread -o test_hash test_hash.c hash_parallelization.c -lrt
```

### Option 2: Using Makefile
```bash
# Build shared library
make

# Build and run test
make test
make run_test

# Clean build artifacts
make clean
```

### Create Report PDF
```bash
pdflatex report.tex
```

## Implementation Details

### 1. array_allocation()
Allocates three main data structures:
- **hash_array**: Array of n pointers to entry_struct (initialized to NULL)
- **entry_list**: Array of m entry_struct items (values set to indices)
- **lock_list**: Array of n pthread mutexes (initialized)

### 2. array_deallocation()
Cleanup function:
- Destroys all n mutex locks
- Frees hash_array, entry_list, and lock_list

### 3. sequential_h_1()
Sequential implementation of h_1 hash function:
- Hash function: h_1(i) = (i + c) mod n
- Linear probing for collision resolution
- Timestamps recorded using clock_gettime(CLOCK_MONOTONIC)
- No locking required (single-threaded)

### 4. parallel_h_1()
Parallel implementation optimized for speedup:
- Creates t threads
- Each thread processes m/t consecutive entries
- Uses pthread_mutex_trylock() for non-blocking lock attempts
- If lock acquisition fails, tries next position (no blocking)
- Records timestamps in nanoseconds

Algorithm per thread:
```
For each entry i in thread's range:
    c = 0
    while true:
        pos = (i + c) mod n
        if trylock(pos) succeeds:
            if hash_array[pos] is NULL:
                place entry
                record timestamp
                unlock and break
            else:
                unlock
                c++
        else:
            retry (implicit by continuing loop)
```

### 5. parallel_h_2()
Parallel implementation with window-based hashing:
- Divides hash array into n/k windows of size k
- Each window: [0...k-1], [k...2k-1], ..., [(n/k-1)*k...n-1]
- Hash function: h_2(i) = ((i + c) mod k) + z*k, for any z in [0, n/k-1]

Deadlock Prevention Strategy:
- Attempts to acquire ALL window locks before checking
- If ANY lock acquisition fails, releases ALL acquired locks immediately
- Uses random starting window to reduce contention
- No sleep/wait mechanisms - just release and retry

Algorithm per thread:
```
For each entry i in thread's range:
    c = 0
    while true:
        rand_val = get_random_val()
        Try to acquire all n/k locks (one per window at position ((i+c) mod k))
        If all locks acquired successfully:
            Check all positions for empty slot
            If empty slot found:
                place entry
                record timestamp
                release all locks and break
            else:
                release all locks
                c++
        else:
            release all acquired locks (deadlock prevention)
            retry
```

### 6. speedup_comparison_h_1()
Measures performance comparison:
1. Runs sequential_h_1() and measures execution time
2. Resets hash_array and timestamps
3. Runs parallel_h_1() and measures execution time
4. Calculates: h_1_speedup = sequential_time / parallel_time

Time measurement using clock_gettime():
```c
struct timespec start, end;
clock_gettime(CLOCK_MONOTONIC, &start);
// ... work ...
clock_gettime(CLOCK_MONOTONIC, &end);
time_ns = (end.tv_sec - start.tv_sec) * 1000000000LL + 
          (end.tv_nsec - start.tv_nsec);
```

## Key Design Decisions

### Thread Distribution
- Entries divided evenly among threads
- Thread i processes: entry_list[i*(m/t) ... (i+1)*(m/t)-1]
- Simple, deterministic distribution

### Lock Management
- **h_1**: Single lock per position, trylock for non-blocking
- **h_2**: Multiple locks (all windows), trylock all before checking

### Deadlock Prevention (h_2)
- Release-all-on-failure strategy
- No timeouts or complex detection
- Random window starting point reduces likelihood

### Timestamp Precision
- Using CLOCK_MONOTONIC for consistency
- Nanosecond precision (int64_t)
- Recorded immediately after successful placement

## Testing Strategy

### Unit Testing
Run test_hash to verify:
- Memory allocation/deallocation
- Sequential correctness
- Parallel correctness
- All entries placed
- Speedup measurement

### Validation Checklist
- [ ] All m entries placed in hash_array
- [ ] No NULL entries in wrong positions
- [ ] All timestamps > 0
- [ ] No deadlocks in h_2
- [ ] Speedup > 1.0 for h_1 (typically)

## Common Issues and Solutions

### Issue 1: Compilation Errors
**Problem**: Undefined references to pthread functions
**Solution**: Add `-pthread` flag and `-lrt` for clock_gettime

### Issue 2: Deadlock in h_2
**Problem**: Program hangs during parallel_h_2
**Solution**: Verify all code paths release ALL acquired locks

### Issue 3: Missing Entries
**Problem**: Not all m entries placed
**Solution**: Check thread index calculation and loop boundaries

### Issue 4: Incorrect Timestamps
**Problem**: Timestamps are 0 or incorrect
**Solution**: Call clock_gettime() AFTER successful placement

### Issue 5: Speedup < 1.0
**Problem**: Parallel version slower than sequential
**Solution**: Normal for small datasets; test with larger m and n

## Submission Preparation

### Step 1: Compile Report
```bash
pdflatex report.tex
# This creates report.pdf
```

### Step 2: Update Student ID
Edit prepare_submission.sh and replace XXXXXXXXX with your student ID

### Step 3: Run Submission Script
```bash
./prepare_submission.sh
```

### Step 4: Verify
Check that STUDENTID.zip contains exactly:
- hash_parallelization.so
- hash_parallelization.c  
- report.pdf

Files should be directly in zip root (no folders).

### Manual Submission (if script fails)
```bash
zip STUDENTID.zip hash_parallelization.so hash_parallelization.c report.pdf
```

## Performance Expectations

### h_1 Speedup
- 2 threads: 1.5x - 2.0x
- 4 threads: 2.0x - 3.5x
- 8 threads: 2.5x - 4.0x

(Varies based on contention and system)

### h_2 Performance
- Slower than h_1 due to lock overhead
- More uniform distribution in hash array
- Should complete without deadlock

## Report Requirements

### Content (Max 2 pages):
1. Manual page links for all functions used
2. GPT/AI usage links (if applicable)
3. Comparison of h_1 vs h_2 (1 paragraph, 3 sentences)

### Format:
- 12pt Times New Roman
- English, formal style
- Use provided report.tex template

### h_1 vs h_2 Comparison Points:
- Speed: h_1 faster due to optimistic locking
- Deadlock: h_2 requires careful lock management
- Distribution: h_2 may have better hash distribution

## Additional Notes

### Thread Safety
- All shared memory access protected by locks
- trylock prevents indefinite blocking
- No race conditions in timestamp assignment

### Memory Management
- All malloc() calls checked for NULL
- Proper cleanup in array_deallocation()
- No memory leaks

### Portability
- Standard POSIX threads
- Works on Linux systems
- Requires libpthread and librt

### Code Style
- Clear variable names
- Comments for complex sections
- Error checking on system calls

## Troubleshooting

### GCC Not Found
Install build tools:
```bash
sudo apt-get install build-essential
```

### Missing pthread.h
Install development libraries:
```bash
sudo apt-get install libc6-dev
```

### pdflatex Not Found
Install LaTeX:
```bash
sudo apt-get install texlive-latex-base
```

## Contact and Support

For questions about the project:
- Check project PDF specification
- Review manual pages for functions
- Test with provided test_hash.c

Remember: NO modifications to hash_parallelization_v3.h allowed!
