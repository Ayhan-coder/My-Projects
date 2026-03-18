/*
 * Test file for hash_parallelization implementation
 * Compile with: gcc -pthread -o test_hash test_hash.c hash_parallelization.c -lrt
 * Or create shared library: gcc -shared -fPIC -pthread -o hash_parallelization.so hash_parallelization.c -lrt
 */

#include "hash_parallelization_v3.h"
#include <stdio.h>

int main(void) {
    // Initialize parameters
    int n_ = 100;   // Hash array size
    int m_ = 50;    // Number of entries
    int t_ = 4;     // Number of threads
    int k_ = 10;    // Window size for h_2
    int seed = 42;  // Random seed
    
    printf("Testing Hash Parallelization\n");
    printf("n=%d, m=%d, t=%d, k=%d, seed=%d\n\n", n_, m_, t_, k_, seed);
    
    // Initialize
    init(n_, m_, t_, k_, seed);
    
    // Allocate arrays
    printf("Allocating arrays...\n");
    if (array_allocation() != 0) {
        printf("Error: Array allocation failed\n");
        return 1;
    }
    printf("Arrays allocated successfully\n\n");
    
    // Test sequential h_1
    printf("Testing sequential_h_1...\n");
    sequential_h_1();
    
    // Verify all entries were placed
    int placed_count = 0;
    for (int i = 0; i < n; i++) {
        if (hash_array[i] != NULL) {
            placed_count++;
        }
    }
    printf("Sequential h_1: Placed %d/%d entries\n", placed_count, m);
    
    // Reset for parallel test
    for (int i = 0; i < n; i++) {
        hash_array[i] = NULL;
    }
    for (int i = 0; i < m; i++) {
        entry_list[i].timestamp = 0;
    }
    
    // Test parallel h_1
    printf("\nTesting parallel_h_1...\n");
    parallel_h_1();
    
    placed_count = 0;
    for (int i = 0; i < n; i++) {
        if (hash_array[i] != NULL) {
            placed_count++;
        }
    }
    printf("Parallel h_1: Placed %d/%d entries\n", placed_count, m);
    
    // Reset for speedup comparison
    for (int i = 0; i < n; i++) {
        hash_array[i] = NULL;
    }
    for (int i = 0; i < m; i++) {
        entry_list[i].timestamp = 0;
    }
    
    // Test speedup comparison
    printf("\nTesting speedup_comparison_h_1...\n");
    speedup_comparison_h_1();
    printf("h_1 Speedup: %.4f\n", h_1_speedup);
    
    // Reset for h_2 test
    for (int i = 0; i < n; i++) {
        hash_array[i] = NULL;
    }
    for (int i = 0; i < m; i++) {
        entry_list[i].timestamp = 0;
    }
    
    // Test parallel h_2
    printf("\nTesting parallel_h_2...\n");
    parallel_h_2();
    
    placed_count = 0;
    for (int i = 0; i < n; i++) {
        if (hash_array[i] != NULL) {
            placed_count++;
        }
    }
    printf("Parallel h_2: Placed %d/%d entries\n", placed_count, m);
    
    // Clean up
    printf("\nDeallocating arrays...\n");
    array_deallocation();
    printf("Test completed successfully!\n");
    
    return 0;
}
