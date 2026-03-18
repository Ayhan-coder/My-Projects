#include "hash_parallelization_v3.h"
#include <stdio.h>

int main(void) {
    // Test with parameters greater than 1,000,000
    int n_ = 2000000;   // hash array size
    int m_ = 1200000;   // number of entries to place
    int t_ = 8;         // number of threads
    int k_ = 1000;      // window size for h_2
    int seed = 42;

    printf("Extreme test (big): n=%d, m=%d, t=%d, k=%d\n", n_, m_, t_, k_);

    init(n_, m_, t_, k_, seed);
    array_allocation();
    
    speedup_comparison_h_1();
    
    int placed = 0;
    for (int i = 0; i < n; i++) {
        if (hash_array[i] != NULL) placed++;
    }
    
    printf("Entries: %d/%d\n", placed, m);
    printf("Speedup: %.4f\n", h_1_speedup);
    
    array_deallocation();
    return 0;
}
