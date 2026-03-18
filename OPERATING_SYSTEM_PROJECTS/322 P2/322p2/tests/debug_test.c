/*
 * Debug test to identify the issue
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
    
    printf("Testing Hash Parallelization - DEBUG\n");
    printf("n=%d, m=%d, t=%d, k=%d, seed=%d\n\n", n_, m_, t_, k_, seed);
    
    // Initialize
    init(n_, m_, t_, k_, seed);
    
    // Allocate arrays
    array_allocation();
    
    // Test parallel h_1
    printf("Testing parallel_h_1...\n");
    parallel_h_1();
    
    int placed_count = 0;
    printf("\nChecking which entries were placed:\n");
    for (int i = 0; i < m; i++) {
        int found = 0;
        for (int j = 0; j < n; j++) {
            if (hash_array[j] != NULL && hash_array[j]->value == i) {
                found = 1;
                placed_count++;
                break;
            }
        }
        if (!found) {
            printf("Entry %d NOT FOUND in hash array!\n", i);
        }
    }
    
    printf("\nTotal placed: %d/%d\n", placed_count, m);
    
    // Check for duplicates or corruption
    printf("\nChecking for issues in hash array:\n");
    for (int i = 0; i < n; i++) {
        if (hash_array[i] != NULL) {
            // Verify it points to valid entry
            int value = hash_array[i]->value;
            if (value < 0 || value >= m) {
                printf("Position %d has invalid value: %d\n", i, value);
            }
        }
    }
    
    array_deallocation();
    
    return 0;
}
