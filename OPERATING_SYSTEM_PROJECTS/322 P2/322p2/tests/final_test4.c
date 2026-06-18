#include "hash_parallelization_v3.h"
#include <stdio.h>
int main(void) {
    init(100, 20, 2, 10, 42);
    array_allocation();
    parallel_h_1();
    int zero_timestamps = 0;
    for (int i = 0; i < 100; i++) {
        if (hash_array[i] != NULL && hash_array[i]->timestamp == 0) {
            zero_timestamps++;
        }
    }
    if (zero_timestamps == 0) {
        printf("✓ All timestamps recorded correctly\n");
    } else {
        printf("✗ WARNING: %d entries have zero timestamps\n", zero_timestamps);
    }
    array_deallocation();
    return 0;
}
