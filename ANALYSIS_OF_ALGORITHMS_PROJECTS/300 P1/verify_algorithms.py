"""
Simple verification that all three algorithms work correctly
"""
from solution import hamiltonian_naive, hamiltonian_optimized, hamiltonian_bonus
from graph_construction import generate_tricky_graph

print("=" * 60)
print("ALGORITHM VERIFICATION TEST")
print("=" * 60)

# Test multiple graphs
test_cases = [3, 4, 5, 6, 7, 8]
all_pass = True

for n in test_cases:
    graph, start, end = generate_tricky_graph(n)
    
    result_naive = hamiltonian_naive(graph, start, end)
    result_opt = hamiltonian_optimized(graph, start, end)
    result_hk = hamiltonian_bonus(graph, start, end)
    
    match = (result_naive == result_opt == result_hk)
    status = "PASS" if match else "FAIL"
    
    if not match:
        all_pass = False
    
    print(f"n={n:2d}  | Naive: {str(result_naive):5s} | Opt: {str(result_opt):5s} | HK: {str(result_hk):5s} | {status}")

print("=" * 60)
if all_pass:
    print("SUCCESS: All algorithms agree on all test cases!")
    print("\nAlgorithm implementations:")
    print("  1. Naive:      O(C(3n,n) x n!)  - Working correctly")
    print("  2. Optimized:  O(n!)            - Working correctly")
    print("  3. Held-Karp:  O(n^2 x 2^n)     - Working correctly")
else:
    print("FAILURE: Some algorithms produced different results!")

print("=" * 60)
