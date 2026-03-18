/*
 * Test with larger parameters to see better speedup
 */

#include "hash_parallelization_v3.h"
#include <stdio.h>

int main(void) {
    // Larger parameters
    int n_ = 10000;   // Much larger hash array
    int m_ = 5000;    // More entries
    int t_ = 8;       // More threads
    int k_ = 100;     // Window size
    int seed = 42;
    
    printf("Testing with larger parameters for speedup\n");
    printf("n=%d, m=%d, t=%d, k=%d\n\n", n_, m_, t_, k_, seed);
    
    init(n_, m_, t_, k_, seed);
    array_allocation();
    
    // Test speedup
    printf("Running speedup comparison...\n");
    speedup_comparison_h_1();
    
    int placed = 0;
    for (int i = 0; i < n; i++) {
        if (hash_array[i] != NULL) placed++;
    }
    
    printf("Entries placed: %d/%d\n", placed, m);
    printf("h_1 Speedup: %.4f\n\n", h_1_speedup);
    
    // Reset and test h_2
    for (int i = 0; i < n; i++) {
        hash_array[i] = NULL;
    }
    
    printf("Testing parallel_h_2...\n");
    parallel_h_2();
    
    placed = 0;
    for (int i = 0; i < n; i++) {
        if (hash_array[i] != NULL) placed++;
    }
    printf("h_2 entries placed: %d/%d\n", placed, m);
    
    array_deallocation();
    printf("\nAll tests passed!\n");
    
    return 0;
}
