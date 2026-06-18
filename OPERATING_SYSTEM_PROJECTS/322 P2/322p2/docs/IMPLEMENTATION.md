# CMPE322 Project 2 - Hash Parallelization Implementation

## Files Included
- `hash_parallelization_v3.h` - Header file (DO NOT MODIFY)
- `hash_parallelization.c` - Implementation of all required functions
- `Makefile` - Build automation
- `test_hash.c` - Optional test program

## Compilation Instructions

### To create the shared object library (required for submission):
```bash
gcc -shared -fPIC -pthread -o hash_parallelization.so hash_parallelization.c -lrt
```

Or using make:
```bash
make
```

### To compile and test (optional):
```bash
gcc -pthread -o test_hash test_hash.c hash_parallelization.c -lrt
./test_hash
```

Or using make:
```bash
make test
make run_test
```

## Implementation Details

### Implemented Functions:

1. **array_allocation()** - Allocates and initializes:
   - hash_array (n pointers to entry_struct)
   - entry_list (m entry_struct items)
   - lock_list (n pthread mutexes)

2. **array_deallocation()** - Cleans up:
   - Destroys all mutex locks
   - Frees all allocated memory

3. **sequential_h_1()** - Sequential hash implementation:
   - Uses h_1(i) = (i + c) mod n
   - Linear probing for collision resolution
   - Updates timestamps using clock_gettime()

4. **parallel_h_1()** - Parallel hash implementation:
   - Divides m entries among t threads
   - Uses trylock to avoid blocking
   - Implements speedup-focused design

5. **parallel_h_2()** - Parallel hash with windows:
   - Divides hash array into n/k windows
   - Acquires all window locks before checking
   - Releases all locks on failure (deadlock prevention)
   - Uses get_random_val() for window selection

6. **speedup_comparison_h_1()** - Measures performance:
   - Runs sequential_h_1 and measures time
   - Runs parallel_h_1 and measures time
   - Calculates speedup = sequential_time / parallel_time
   - Stores result in h_1_speedup

## Key Implementation Features

### Thread Safety
- Uses pthread_mutex_trylock() for non-blocking lock acquisition
- Proper lock release in all code paths
- Deadlock prevention in h_2 by releasing all locks on failure

### Timestamp Accuracy
- Uses clock_gettime(CLOCK_MONOTONIC, ...) for nanosecond precision
- Timestamps recorded immediately after successful placement
- Stored as int64_t in nanoseconds

### Collision Handling
- h_1: Linear probing with increment
- h_2: Window-based with random starting point

### Thread Distribution
- Each thread processes m/t consecutive entries
- Thread i processes indices [i*(m/t), (i+1)*(m/t))

## Testing

The test program verifies:
- Array allocation/deallocation
- Sequential h_1 correctness
- Parallel h_1 correctness
- Speedup measurement
- Parallel h_2 correctness and deadlock-free operation

## Notes

- All hash array entries initialized to NULL
- Entry values are set to their indices (0 to m-1)
- Random seed controls get_random_val() behavior
- No timing mechanisms or sleeps used for deadlock handling
- Timestamps enable verification of execution order
