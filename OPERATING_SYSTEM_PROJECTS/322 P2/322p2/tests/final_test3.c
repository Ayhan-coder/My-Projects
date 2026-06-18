#include "hash_parallelization_v3.h"
#include <stdio.h>
int main(void) {
    init(50000, 40000, 8, 500, 42);
    array_allocation();
    speedup_comparison_h_1();
    int count = 0;
    for (int i = 0; i < 50000; i++) if (hash_array[i] != NULL) count++;
    printf("✓ Entries placed: %d/40000\n", count);
    printf("✓ Speedup: %.4f\n", h_1_speedup);
    array_deallocation();
    return 0;
}
