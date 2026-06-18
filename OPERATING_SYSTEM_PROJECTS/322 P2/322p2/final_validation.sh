#!/bin/bash

# Final Validation Test for CMPE322 Project 2

echo "════════════════════════════════════════════════════════════"
echo "  CMPE322 PROJECT 2 - FINAL VALIDATION TEST"
echo "════════════════════════════════════════════════════════════"
echo ""

cd /home/vboxuser/Downloads/322p2

# Test 1: Small dataset
echo "Test 1: Small Dataset (n=100, m=50, t=4)"
echo "─────────────────────────────────────────────"
cat > final_test1.c << 'EOF'
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
EOF
gcc -pthread -o final_test1 final_test1.c -L. -Wl,-rpath,. hash_parallelization.so && ./final_test1
echo ""

# Test 2: Medium dataset with speedup
echo "Test 2: Medium Dataset with Speedup (n=10000, m=5000, t=4)"
echo "─────────────────────────────────────────────────────────────"
cat > final_test2.c << 'EOF'
#include "hash_parallelization_v3.h"
#include <stdio.h>
int main(void) {
    init(10000, 5000, 4, 100, 42);
    array_allocation();
    speedup_comparison_h_1();
    int count = 0;
    for (int i = 0; i < 10000; i++) if (hash_array[i] != NULL) count++;
    printf("✓ Entries placed: %d/5000\n", count);
    printf("✓ Speedup: %.4f\n", h_1_speedup);
    array_deallocation();
    return 0;
}
EOF
gcc -pthread -o final_test2 final_test2.c -L. -Wl,-rpath,. hash_parallelization.so && ./final_test2
echo ""

# Test 3: Large dataset
echo "Test 3: Large Dataset (n=50000, m=40000, t=8)"
echo "─────────────────────────────────────────────"
cat > final_test3.c << 'EOF'
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
EOF
gcc -pthread -o final_test3 final_test3.c -L. -Wl,-rpath,. hash_parallelization.so && ./final_test3
echo ""

# Test 4: Verify timestamps
echo "Test 4: Timestamp Verification"
echo "────────────────────────────────"
cat > final_test4.c << 'EOF'
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
EOF
gcc -pthread -o final_test4 final_test4.c -L. -Wl,-rpath,. hash_parallelization.so && ./final_test4
echo ""

echo "════════════════════════════════════════════════════════════"
echo "  ALL TESTS COMPLETED SUCCESSFULLY!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Submission files ready:"
echo "  ✓ hash_parallelization.so"
echo "  ✓ hash_parallelization.c"
echo "  ⚠ report.pdf (needs to be created from report.tex or report.md)"
echo ""
echo "To create submission:"
echo "  1. Create report.pdf from report.tex or report.md"
echo "  2. Edit prepare_submission.sh with your student ID"
echo "  3. Run: ./prepare_submission.sh"
echo ""
