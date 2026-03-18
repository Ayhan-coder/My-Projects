#include "hash_parallelization_v3.h"
#include <stdio.h>

int main(void) {
    // Test with 100 million entries
    int n_ = 160000000; // hash array size
    int m_ = 100000000; // 100 million entries to place
    int t_ = 8;         // number of threads
    int k_ = 1000;      // window size for h_2
    int seed = 42;

    printf("Ultra test (100 million entries): n=%d, m=%d, t=%d, k=%d\n", n_, m_, t_, k_);

    init(n_, m_, t_, k_, seed);
    array_allocation();
    
    speedup_comparison_h_1();
    
    int placed = 0;
    for (int i = 0; i < n; i++) {
        if (hash_array[i] != NULL) placed++;
    }
    
    printf("Entries placed: %d/%d\n", placed, m);
    printf("Speedup: %.4f\n", h_1_speedup);
    
    array_deallocation();
    return 0;
}
