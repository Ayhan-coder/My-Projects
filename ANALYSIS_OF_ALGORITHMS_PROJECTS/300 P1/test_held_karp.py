"""
Quick test to verify Held-Karp algorithm implementation
"""
from solution import hamiltonian_bonus, hamiltonian_optimized, hamiltonian_naive
from graph_construction import generate_tricky_graph
import time

print("=" * 70)
print("HELD-KARP ALGORITHM VERIFICATION")
print("=" * 70)

# Test 1: Small graph
print("\nTest 1: Small graph (n=3)")
graph, start, end = generate_tricky_graph(3)
result_bonus = hamiltonian_bonus(graph, start, end)
result_opt = hamiltonian_optimized(graph, start, end)
print(f"  Held-Karp result: {result_bonus}")
print(f"  Optimized result: {result_opt}")
print(f"  ✓ Match: {result_bonus == result_opt}")

# Test 2: Medium graph
print("\nTest 2: Medium graph (n=5)")
graph, start, end = generate_tricky_graph(5)
result_bonus = hamiltonian_bonus(graph, start, end)
result_opt = hamiltonian_optimized(graph, start, end)
print(f"  Held-Karp result: {result_bonus}")
print(f"  Optimized result: {result_opt}")
print(f"  ✓ Match: {result_bonus == result_opt}")

# Test 3: Performance comparison (n=8)
print("\nTest 3: Performance comparison (n=8)")
graph, start, end = generate_tricky_graph(8)

start_time = time.time()
result_opt = hamiltonian_optimized(graph, start, end)
opt_time = time.time() - start_time

start_time = time.time()
result_bonus = hamiltonian_bonus(graph, start, end)
bonus_time = time.time() - start_time

print(f"  Optimized (n!):     {opt_time:.4f}s (result={result_opt})")
print(f"  Held-Karp (2^n):    {bonus_time:.4f}s (result={result_bonus})")
if opt_time > 0 and bonus_time > 0:
    speedup = opt_time / bonus_time
    print(f"  Speedup factor:     {speedup:.2f}x")
print(f"  ✓ Results match: {result_opt == result_bonus}")

# Test 4: Larger graph where Held-Karp should shine (n=10)
print("\nTest 4: Larger graph (n=10) - Held-Karp advantage")
graph, start, end = generate_tricky_graph(10)

print("  Running Held-Karp (O(n² × 2^n))...")
start_time = time.time()
result_bonus = hamiltonian_bonus(graph, start, end)
bonus_time = time.time() - start_time
print(f"    Held-Karp: {bonus_time:.4f}s (result={result_bonus})")

print("  Running Optimized (O(n!))...")
start_time = time.time()
result_opt = hamiltonian_optimized(graph, start, end)
opt_time = time.time() - start_time
print(f"    Optimized: {opt_time:.4f}s (result={result_opt})")

if opt_time > 0 and bonus_time > 0:
    speedup = opt_time / bonus_time
    print(f"  Held-Karp is {speedup:.2f}x faster!")
print(f"  ✓ Results match: {result_opt == result_bonus}")

# Test 5: Multiple random graphs
print("\nTest 5: Consistency check (10 random graphs, n=6)")
all_match = True
for i in range(10):
    graph, start, end = generate_tricky_graph(6)
    result_bonus = hamiltonian_bonus(graph, start, end)
    result_opt = hamiltonian_optimized(graph, start, end)
    if result_bonus != result_opt:
        all_match = False
        print(f"  ✗ Mismatch in graph {i+1}")
        
if all_match:
    print(f"  ✓ All 10 graphs: Held-Karp and Optimized agree")

print("\n" + "=" * 70)
print("HELD-KARP VERIFICATION COMPLETE")
print("=" * 70)

# Complexity comparison table
print("\nComplexity Comparison:")
print("┌─────────────┬──────────────────────┬─────────────────────┐")
print("│ Algorithm   │ Time Complexity      │ For n=20            │")
print("├─────────────┼──────────────────────┼─────────────────────┤")
print("│ Naive       │ O(C(3n,n) × n!)      │ Astronomical        │")
print("│ Optimized   │ O(n!)                │ ~2.4 × 10¹⁸         │")
print("│ Held-Karp   │ O(n² × 2ⁿ)           │ ~4.2 × 10⁸          │")
print("└─────────────┴──────────────────────┴─────────────────────┘")
print("\nHeld-Karp provides ~10¹⁰ speedup over factorial algorithms!")
