#include "hash_parallelization_v3.h"
#include <stdio.h>
int main(void) {
    init(100, 50, 4, 10, 42);
    array_allocation();
    parallel_h_1();
    int count = 0;
    for (int i = 0; i < 100; i++) if (hash_array[i] != NULL) count++;
    printf("✓ Parallel h_1: %d/50 entries placed\n", count);
    for (int i = 0; i < 100; i++) hash_array[i] = NULL;
    parallel_h_2();
    count = 0;
    for (int i = 0; i < 100; i++) if (hash_array[i] != NULL) count++;
    printf("✓ Parallel h_2: %d/50 entries placed\n", count);
    array_deallocation();
    return 0;
}
