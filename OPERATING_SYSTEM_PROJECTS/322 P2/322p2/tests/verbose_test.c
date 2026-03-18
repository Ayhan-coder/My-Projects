/*
 * Verbose debug test
 */

#include "hash_parallelization_v3.h"
#include <stdio.h>

int main(void) {
    // Initialize parameters
    int n_ = 20;    // Smaller for easier debugging
    int m_ = 10;    // Smaller number of entries
    int t_ = 2;     // Fewer threads
    int k_ = 5;     // Window size for h_2
    int seed = 42;  // Random seed
    
    printf("DEBUG Test - Small parameters\n");
    printf("n=%d, m=%d, t=%d, k=%d\n\n", n_, m_, t_, k_, seed);
    
    // Initialize
    init(n_, m_, t_, k_, seed);
    
    // Allocate arrays
    array_allocation();
    
    printf("Entry distribution:\n");
    int entries_per_thread = m / t;
    for (int i = 0; i < t; i++) {
        int start = i * entries_per_thread;
        int end = (i + 1) * entries_per_thread;
        printf("Thread %d: entries [%d ... %d)\n", i, start, end);
    }
    printf("\n");
    
    // Test parallel h_1
    printf("Running parallel_h_1...\n");
    parallel_h_1();
    
    printf("\nHash array contents:\n");
    for (int i = 0; i < n; i++) {
        if (hash_array[i] != NULL) {
            printf("hash_array[%d] = entry with value %d\n", i, hash_array[i]->value);
        }
    }
    
    printf("\nChecking all entries:\n");
    for (int i = 0; i < m; i++) {
        int found = 0;
        for (int j = 0; j < n; j++) {
            if (hash_array[j] != NULL && hash_array[j]->value == i) {
                found = 1;
                printf("Entry %d: FOUND at position %d\n", i, j);
                break;
            }
        }
        if (!found) {
            printf("Entry %d: NOT FOUND!\n", i);
        }
    }
    
    array_deallocation();
    
    return 0;
}
