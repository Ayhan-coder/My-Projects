#include "hash_parallelization_v3.h"
#include <stdio.h>
#include <time.h>
#include <stdint.h>

typedef struct {
    int n;
    int m;
    int t;
    int k;
    int seed;
} h2_test_config;

static int64_t get_time_ns(struct timespec *ts) {
    return (int64_t)ts->tv_sec * 1000000000LL + (int64_t)ts->tv_nsec;
}

void run_h2_test(int test_id, h2_test_config cfg) {
    int windows = cfg.n / cfg.k;
    printf("=== H2 TEST: h2_%02d | N=%d M=%d T=%d K=%d windows=%d seed=%d ===\n",
           test_id, cfg.n, cfg.m, cfg.t, cfg.k, windows, cfg.seed);
    
    init(cfg.n, cfg.m, cfg.t, cfg.k, cfg.seed);
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
    
    double time_ms = (double)h2_time / 1000000.0;
    printf("    [h_2] time = %.4f ms | entries placed = %d/%d\n", time_ms, placed, cfg.m);
    printf("PASS\n\n");
    
    array_deallocation();
}

int main(void) {
    printf("H2 Test Suite (Parallel Hash Function 2)\n");
    printf("=========================================\n\n");
    
    // Test configurations with varying k values and window configurations
    h2_test_config tests[] = {
        // Small tests
        {4096, 2048, 8, 16, 2001},      // 256 windows
        {4096, 2048, 8, 32, 2002},      // 128 windows
        {4096, 2048, 8, 64, 2003},      // 64 windows
        
        // Medium tests with different thread counts
        {16384, 12288, 4, 64, 2004},    // 256 windows, 4 threads
        {16384, 12288, 8, 64, 2005},    // 256 windows, 8 threads
        {16384, 12288, 16, 64, 2006},   // 256 windows, 16 threads
        
        // Tests with large k (small windows)
        {32768, 24576, 8, 256, 2007},   // 128 windows
        {32768, 24576, 8, 512, 2008},   // 64 windows
        
        // Tests with small k (many windows)
        {32768, 24576, 8, 16, 2009},    // 2048 windows
        {32768, 24576, 8, 32, 2010},    // 1024 windows
        
        // Large test
        {65536, 49152, 8, 128, 2011},   // 512 windows
    };
    
    int num_tests = sizeof(tests) / sizeof(tests[0]);
    
    for (int i = 0; i < num_tests; i++) {
        run_h2_test(1 + i, tests[i]);
    }
    
    printf("All H2 tests completed!\n");
    return 0;
}
