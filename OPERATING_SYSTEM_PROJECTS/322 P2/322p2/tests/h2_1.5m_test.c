#include "hash_parallelization_v3.h"
#include <stdio.h>
#include <time.h>
#include <stdint.h>

static int64_t get_time_ns(struct timespec *ts) {
    return (int64_t)ts->tv_sec * 1000000000LL + (int64_t)ts->tv_nsec;
}

int main(void) {
    // H2 test with 1.5 million entries
    int n_ = 2400000;   // hash array size
    int m_ = 1500000;   // 1.5 million entries to place
    int t_ = 8;         // number of threads
    int k_ = 1000;      // window size for h_2
    int seed = 42;

    printf("H2 test (1.5 million entries): n=%d, m=%d, t=%d, k=%d\n", n_, m_, t_, k_);

    init(n_, m_, t_, k_, seed);
    array_allocation();
    
    struct timespec start, end;
    int64_t h2_time;
    
    // Measure parallel_h_2 time
    clock_gettime(CLOCK_MONOTONIC, &start);
    parallel_h_2();
    clock_gettime(CLOCK_MONOTONIC, &end);
    h2_time = get_time_ns(&end) - get_time_ns(&start);
    
    int placed = 0;
    for (int i = 0; i < n; i++) {
        if (hash_array[i] != NULL) placed++;
    }
    
    double time_sec = (double)h2_time / 1000000000.0;
    double time_ms = (double)h2_time / 1000000.0;
    printf("Entries placed: %d/%d\n", placed, m);
    printf("H2 time: %.4f ms (%.4f seconds)\n", time_ms, time_sec);
    
    array_deallocation();
    return 0;
}
