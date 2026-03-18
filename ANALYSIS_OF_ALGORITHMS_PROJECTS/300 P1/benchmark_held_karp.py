"""
Performance benchmark: Held-Karp vs Permutation-based algorithms
"""
from solution import hamiltonian_bonus, hamiltonian_optimized
from graph_construction import generate_tricky_graph
import time

print("=" * 70)
print("PERFORMANCE BENCHMARK: Held-Karp vs O(n!) Algorithms")
print("=" * 70)

# Test with increasing n values
n_values = [5, 7, 9, 11, 13, 15]

print("\n{:<6} {:<15} {:<15} {:<12}".format("n", "Optimized(n!)", "Held-Karp(2^n)", "Speedup"))
print("-" * 70)

for n in n_values:
    graph, start, end = generate_tricky_graph(n)
    
    # Benchmark Optimized (factorial)
    start_time = time.time()
    result_opt = hamiltonian_optimized(graph, start, end)
    opt_time = time.time() - start_time
    
    # Benchmark Held-Karp (exponential but better)
    start_time = time.time()
    result_hk = hamiltonian_bonus(graph, start, end)
    hk_time = time.time() - start_time
    
    # Calculate speedup
    if hk_time > 0:
        speedup = opt_time / hk_time
    else:
        speedup = float('inf')
    
    # Verify results match
    match = "✓" if result_opt == result_hk else "✗"
    
    print("{:<6} {:<15.6f}s {:<15.6f}s {:<8.2f}x {}".format(
        n, opt_time, hk_time, speedup, match
    ))
    
    # Stop if optimized takes too long
    if opt_time > 5.0:
        print("\n⚠️  Stopping benchmark: Optimized algorithm taking too long")
        print(f"   (For larger n, factorial growth makes it impractical)")
        break

print("\n" + "=" * 70)
print("THEORETICAL COMPLEXITY GROWTH:")
print("=" * 70)
print("\nFor reference, here's how the operations grow:")
print("\n{:<6} {:<20} {:<20}".format("n", "n! (approx)", "n² × 2^n"))
print("-" * 70)

import math
for n in [10, 15, 20, 25, 30]:
    factorial = math.factorial(n)
    exponential = n * n * (2 ** n)
    
    # Format with scientific notation if too large
    if factorial > 1e10:
        fact_str = f"{factorial:.2e}"
    else:
        fact_str = f"{factorial:,}"
    
    if exponential > 1e10:
        exp_str = f"{exponential:.2e}"
    else:
        exp_str = f"{exponential:,}"
    
    print("{:<6} {:<20} {:<20}".format(n, fact_str, exp_str))

print("\n" + "=" * 70)
print("KEY INSIGHT:")
print("=" * 70)
print("While both are exponential, 2^n grows MUCH slower than n!")
print("For n=20: Held-Karp is ~10 billion times faster!")
print("This makes Held-Karp practical for n ≤ 25, while n! becomes")
print("infeasible around n=15.")
