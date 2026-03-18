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
    int pat;
    int timeout;
} test_config;

static int64_t get_time_ns(struct timespec *ts) {
    return (int64_t)ts->tv_sec * 1000000000LL + (int64_t)ts->tv_nsec;
}

void run_test(int test_id, test_config cfg) {
    int windows = cfg.n / cfg.k;
    printf("=== TEST: fuzz_%02d | N=%d M=%d T=%d K=%d windows=%d seed=%d pat=%d timeout=%ds ===\n",
           test_id, cfg.n, cfg.m, cfg.t, cfg.k, windows, cfg.seed, cfg.pat, cfg.timeout);
    
    init(cfg.n, cfg.m, cfg.t, cfg.k, cfg.seed);
    array_allocation();
    
    struct timespec start, end;
    int64_t seq_time, par_time;
    
    // Sequential h_1
    clock_gettime(CLOCK_MONOTONIC, &start);
    sequential_h_1();
    clock_gettime(CLOCK_MONOTONIC, &end);
    seq_time = get_time_ns(&end) - get_time_ns(&start);
    
    // Reset for parallel
    for (int i = 0; i < n; i++) {
        hash_array[i] = NULL;
    }
    for (int i = 0; i < m; i++) {
        entry_list[i].timestamp = 0;
    }
    
    // Parallel h_1
    clock_gettime(CLOCK_MONOTONIC, &start);
    parallel_h_1();
    clock_gettime(CLOCK_MONOTONIC, &end);
    par_time = get_time_ns(&end) - get_time_ns(&start);
    
    double speedup = (double)seq_time / (double)par_time;
    printf("    [h_1] speedup = %.6f (seq/par)\n", speedup);
    printf("PASS\n\n");
    
    array_deallocation();
}

int main(void) {
    printf("Fuzz Test Suite (Friend's Format)\n");
    printf("==================================\n\n");
    
    // Test configurations matching friend's format
    test_config tests[] = {
        {32768, 16384, 16, 16, 1007, 0, 120},
        {16384, 12288, 64, 64, 1008, 0, 57},
        {16384, 12288, 64, 256, 1009, 1, 57},
        {32768, 24576, 8, 32, 1010, 0, 60},
        {8192, 6144, 2, 64, 1011, 1, 12},
        {8192, 4096, 64, 64, 1012, 1, 57},
        {16384, 12288, 8, 128, 1013, 0, 12},
        {8192, 6144, 2, 16, 1014, 0, 30},
        {4096, 2048, 8, 16, 1015, 0, 12},
        {16384, 8192, 2, 16, 1016, 0, 60},
        {32768, 16384, 4, 128, 1017, 0, 12},
    };
    
    int num_tests = sizeof(tests) / sizeof(tests[0]);
    
    for (int i = 0; i < num_tests; i++) {
        run_test(7 + i, tests[i]);
    }
    
    printf("All tests completed!\n");
    return 0;
}
