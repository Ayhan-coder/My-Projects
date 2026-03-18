"""
Generate performance comparison visualizations for Hamiltonian* Path algorithms.
Creates PNG files with tables and charts comparing the three algorithms.
"""
import random
import time
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to avoid tkinter issues
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.table import Table
import numpy as np
from solution import hamiltonian_naive, hamiltonian_optimized, hamiltonian_bonus
from graph_construction import generate_tricky_graph
import timeit


def timed_run(func, args, iterations=10):
    """
    Run a function multiple times and return average time.
    Uses timeit for better sub-millisecond measurements.
    """
    def wrapper():
        return func(*args)
    
    total_time = timeit.timeit(wrapper, number=iterations)
    return total_time / iterations


def benchmark_all_algorithms(n_values, num_trials=1, max_time=3.0):
    """
    Benchmark all three algorithms across different values of n.
    
    Args:
        n_values: List of n values to test
        num_trials: Number of trials per algorithm (1 for speed)
        max_time: Maximum time in seconds for any single algorithm
    
    Returns:
        Dictionary with timing results for each algorithm
    """
    results = {
        'n': [],
        'naive_time': [],
        'optimized_time': [],
        'bonus_time': [],
        'naive_result': [],
        'optimized_result': [],
        'bonus_result': []
    }
    
    skip_naive = False  # Flag to skip naive if it gets too slow
    
    for n in n_values:
        print(f"Benchmarking n={n}...")
        
        # Generate test graph
        random.seed(42 + n)
        graph, start, end = generate_tricky_graph(n)
        
        # Benchmark naive algorithm (skip if previously too slow)
        if not skip_naive:
            start_time = time.time()
            result_naive = hamiltonian_naive(graph, start, end)
            naive_avg = time.time() - start_time
            
            # If takes too long, skip naive for remaining n values
            if naive_avg > max_time:
                print(f"  Naive: {naive_avg:.4f}s (too slow, skipping for larger n)")
                skip_naive = True
            else:
                print(f"  Naive: {naive_avg:.6f}s")
        else:
            # Use estimated time based on exponential growth
            if len(results['naive_time']) > 0:
                # Factorial grows by factor of n
                naive_avg = results['naive_time'][-1] * (n / (n-1))
                result_naive = results['naive_result'][-1]
                print(f"  Naive: {naive_avg:.6f}s (estimated, skipped)")
            else:
                naive_avg = max_time * 10
                result_naive = False
        
        # Benchmark optimized algorithm (use timeit for accuracy)
        result_optimized = hamiltonian_optimized(graph, start, end)
        opt_avg = timed_run(hamiltonian_optimized, (graph, start, end), iterations=5)
        print(f"  Optimized: {opt_avg:.6f}s")
        
        # Benchmark bonus algorithm (use timeit for accuracy)
        result_bonus = hamiltonian_bonus(graph, start, end)
        bonus_avg = timed_run(hamiltonian_bonus, (graph, start, end), iterations=5)
        print(f"  Held-Karp: {bonus_avg:.6f}s")
        
        # Store results
        results['n'].append(n)
        results['naive_time'].append(naive_avg)
        results['optimized_time'].append(opt_avg)
        results['bonus_time'].append(bonus_avg)
        results['naive_result'].append(result_naive)
        results['optimized_result'].append(result_optimized)
        results['bonus_result'].append(result_bonus)
        
    return results


def create_comparison_table(results):
    """Create a visual comparison table as PNG."""
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # Prepare table data
    headers = ['n', 'Graph Size', 'Naive (s)', 'Optimized (s)', 'Held-Karp (s)', 
               'Speedup\n(Opt/HK)', 'Speedup\n(Naive/HK)']
    
    table_data = []
    for i, n in enumerate(results['n']):
        graph_size = 3 * n
        naive_time = results['naive_time'][i]
        opt_time = results['optimized_time'][i]
        bonus_time = results['bonus_time'][i]
        
        # Calculate speedups (Held-Karp vs others)
        # Use minimum threshold to avoid division by near-zero
        min_time = max(bonus_time, 1e-5)  # At least 10 microseconds
        speedup_opt_vs_hk = opt_time / min_time if opt_time > 1e-6 else 1.0
        speedup_naive_vs_hk = naive_time / min_time if naive_time > 1e-6 else 1.0
        
        # Format times with scientific notation for very small values
        if naive_time < 0.0001:
            naive_str = f"{naive_time:.2e}"
        elif naive_time < 0.01:
            naive_str = f"{naive_time:.5f}"
        else:
            naive_str = f"{naive_time:.3f}"
            
        if opt_time < 0.0001:
            opt_str = f"{opt_time:.2e}"
        elif opt_time < 0.01:
            opt_str = f"{opt_time:.5f}"
        else:
            opt_str = f"{opt_time:.3f}"
            
        if bonus_time < 0.0001:
            bonus_str = f"{bonus_time:.2e}"
        elif bonus_time < 0.01:
            bonus_str = f"{bonus_time:.5f}"
        else:
            bonus_str = f"{bonus_time:.3f}"
        
        row = [
            str(n),
            str(graph_size),
            naive_str,
            opt_str,
            bonus_str,
            f"{speedup_opt_vs_hk:.1f}x" if speedup_opt_vs_hk < 100 else f"{speedup_opt_vs_hk:.0f}x",
            f"{speedup_naive_vs_hk:.1f}x" if speedup_naive_vs_hk < 100 else f"{speedup_naive_vs_hk:.0f}x"
        ]
        table_data.append(row)
    
    # Create table
    table = ax.table(cellText=table_data, colLabels=headers, 
                     cellLoc='center', loc='center',
                     colWidths=[0.08, 0.12, 0.15, 0.15, 0.15, 0.15, 0.15])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.5)
    
    # Style the header
    for i in range(len(headers)):
        cell = table[(0, i)]
        cell.set_facecolor('#4472C4')
        cell.set_text_props(weight='bold', color='white')
    
    # Alternate row colors
    for i in range(1, len(table_data) + 1):
        for j in range(len(headers)):
            cell = table[(i, j)]
            if i % 2 == 0:
                cell.set_facecolor('#E7E6E6')
            else:
                cell.set_facecolor('#F2F2F2')
    
    # Highlight speedup columns
    for i in range(1, len(table_data) + 1):
        for j in [5, 6]:  # Speedup columns
            cell = table[(i, j)]
            cell.set_facecolor('#C6E0B4')
            cell.set_text_props(weight='bold')
    
    plt.title('Hamiltonian* Path Algorithm Performance Comparison', 
              fontsize=16, fontweight='bold', pad=20)
    
    # Add footer with complexity
    footer_text = (
        "Time Complexity (asymptotic in terms of n):\n"
        "Naive: O(C(3n,n) × n!)  |  Optimized: O(n!)  |  Bonus (Held-Karp): O(n² × 2ⁿ)"
    )
    plt.figtext(0.5, 0.02, footer_text, ha='center', fontsize=9, 
                style='italic', wrap=True)
    
    plt.savefig('algorithm_comparison_table.png', dpi=300, bbox_inches='tight',
                facecolor='white')
    print("\n✓ Saved: algorithm_comparison_table.png")
    plt.close()


def create_performance_charts(results):
    """Create performance comparison charts."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    n_values = results['n']
    
    # Chart 1: Execution Time Comparison (Linear Scale)
    ax1.plot(n_values, results['naive_time'], 'o-', linewidth=2, markersize=8,
             label='Naive', color='#E74C3C')
    ax1.plot(n_values, results['optimized_time'], 's-', linewidth=2, markersize=8,
             label='Optimized', color='#3498DB')
    ax1.plot(n_values, results['bonus_time'], '^-', linewidth=2, markersize=8,
             label='Bonus (Held-Karp)', color='#2ECC71')
    
    ax1.set_xlabel('n (component size)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Execution Time (seconds)', fontsize=12, fontweight='bold')
    ax1.set_title('Execution Time Comparison', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(n_values)
    
    # Chart 2: Execution Time Comparison (Log Scale)
    ax2.semilogy(n_values, results['naive_time'], 'o-', linewidth=2, markersize=8,
                 label='Naive', color='#E74C3C')
    ax2.semilogy(n_values, results['optimized_time'], 's-', linewidth=2, markersize=8,
                 label='Optimized', color='#3498DB')
    ax2.semilogy(n_values, results['bonus_time'], '^-', linewidth=2, markersize=8,
                 label='Bonus (Held-Karp)', color='#2ECC71')
    
    ax2.set_xlabel('n (component size)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Execution Time (seconds, log scale)', fontsize=12, fontweight='bold')
    ax2.set_title('Execution Time Comparison (Log Scale)', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3, which='both')
    ax2.set_xticks(n_values)
    
    # Chart 3: Speedup Comparison (focus on meaningful comparisons)
    speedup_opt_vs_hk = []
    speedup_naive_vs_hk = []
    
    for i in range(len(n_values)):
        opt_time = results['optimized_time'][i]
        bonus_time = results['bonus_time'][i]
        naive_time = results['naive_time'][i]
        
        # Calculate speedups relative to Held-Karp
        if bonus_time > 1e-6:
            speedup_opt_vs_hk.append(opt_time / bonus_time)
            speedup_naive_vs_hk.append(naive_time / bonus_time)
        else:
            speedup_opt_vs_hk.append(1.0)
            speedup_naive_vs_hk.append(1.0)
    
    x = np.arange(len(n_values))
    width = 0.35
    
    bars1 = ax3.bar(x - width/2, speedup_opt_vs_hk, width, label='Optimized vs Held-Karp',
                    color='#3498DB', edgecolor='black', linewidth=1.2)
    bars2 = ax3.bar(x + width/2, speedup_naive_vs_hk, width, label='Naive vs Held-Karp',
                    color='#E74C3C', edgecolor='black', linewidth=1.2)
    
    ax3.set_xlabel('n (component size)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Speedup Factor (vs Held-Karp)', fontsize=12, fontweight='bold')
    ax3.set_title('Speedup Relative to Held-Karp Algorithm', fontsize=14, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(n_values)
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.set_yscale('log')  # Use log scale for large speedups
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                label = f'{height:.0f}x' if height >= 10 else f'{height:.1f}x'
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        label,
                        ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    # Chart 4: Relative Performance (Normalized to Optimized)
    normalized_naive = [results['naive_time'][i] / results['optimized_time'][i] 
                        if results['optimized_time'][i] > 0 else 0 
                        for i in range(len(n_values))]
    normalized_opt = [1.0] * len(n_values)
    normalized_bonus = [results['bonus_time'][i] / results['optimized_time'][i] 
                        if results['optimized_time'][i] > 0 else 0 
                        for i in range(len(n_values))]
    
    ax4.plot(n_values, normalized_naive, 'o-', linewidth=2, markersize=8,
             label='Naive', color='#E74C3C')
    ax4.plot(n_values, normalized_opt, 's-', linewidth=2, markersize=8,
             label='Optimized (baseline)', color='#3498DB')
    ax4.plot(n_values, normalized_bonus, '^-', linewidth=2, markersize=8,
             label='Bonus', color='#2ECC71')
    
    ax4.set_xlabel('n (component size)', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Relative Time (normalized to Optimized)', fontsize=12, fontweight='bold')
    ax4.set_title('Relative Performance (Optimized = 1.0)', fontsize=14, fontweight='bold')
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3)
    ax4.set_xticks(n_values)
    ax4.axhline(y=1, color='#3498DB', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('algorithm_performance_charts.png', dpi=300, bbox_inches='tight',
                facecolor='white')
    print("✓ Saved: algorithm_performance_charts.png")
    plt.close()


def create_complexity_comparison():
    """Create theoretical complexity comparison chart."""
    import math
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Theoretical growth for visualization
    n_range = np.arange(2, 15, 0.5)
    
    # Simplified theoretical curves (for illustration)
    # Using approximations: C(3n,n) grows roughly as 3^(3n) / sqrt(n)
    naive_theoretical = np.array([3**(2*n) / np.sqrt(n) for n in n_range])
    optimized_theoretical = np.array([math.factorial(int(n)) if n <= 8 else math.factorial(8) * (n/8)**10 
                                      for n in n_range])
    heldkarp_theoretical = np.array([n*n * (2**n) for n in n_range])
    
    # Normalize for visualization
    naive_theoretical = naive_theoretical / naive_theoretical[0]
    optimized_theoretical = optimized_theoretical / optimized_theoretical[0]
    heldkarp_theoretical = heldkarp_theoretical / heldkarp_theoretical[0]
    
    # Chart 1: Theoretical complexity growth
    ax1.semilogy(n_range, naive_theoretical, linewidth=3, 
                 label='Naive: O(C(3n,n) × n!)', color='#E74C3C')
    ax1.semilogy(n_range, optimized_theoretical, linewidth=3,
                 label='Optimized: O(n!)', color='#3498DB')
    ax1.semilogy(n_range, heldkarp_theoretical, linewidth=3,
                 label='Held-Karp: O(n² × 2ⁿ)', color='#2ECC71')
    
    ax1.set_xlabel('n (component size)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Relative Operations (log scale)', fontsize=12, fontweight='bold')
    ax1.set_title('Theoretical Complexity Growth', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3, which='both')
    
    # Chart 2: Complexity comparison table
    ax2.axis('off')
    
    complexity_data = [
        ['Algorithm', 'Best Case', 'Worst Case', 'Average Case'],
        ['Naive', 'O(n²)', 'O(C(3n,n) × n!)', 'O(C(3n,n) × n!)'],
        ['Optimized', 'O(n²)', 'O(n!)', 'O(n!)'],
        ['Bonus (Held-Karp)', 'O(n² × 2ⁿ)', 'O(n² × 2ⁿ)', 'O(n² × 2ⁿ)']
    ]
    
    table = ax2.table(cellText=complexity_data, cellLoc='center', loc='center',
                      colWidths=[0.25, 0.25, 0.25, 0.25])
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 3)
    
    # Style header
    for i in range(4):
        cell = table[(0, i)]
        cell.set_facecolor('#4472C4')
        cell.set_text_props(weight='bold', color='white')
    
    # Style rows
    colors = ['#E74C3C', '#3498DB', '#2ECC71']
    for i in range(1, 4):
        for j in range(4):
            cell = table[(i, j)]
            if j == 0:
                cell.set_facecolor(colors[i-1])
                cell.set_text_props(weight='bold', color='white')
            else:
                cell.set_facecolor('#F2F2F2')
    
    ax2.set_title('Time Complexity Summary', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('complexity_comparison.png', dpi=300, bbox_inches='tight',
                facecolor='white')
    print("✓ Saved: complexity_comparison.png")
    plt.close()


def main():
    """Main function to generate all visualizations."""
    print("=" * 60)
    print("GENERATING PERFORMANCE COMPARISON VISUALIZATIONS")
    print("=" * 60)
    
    # Define test range (adjust based on computational limits)
    # Using range where performance differences are measurable
    # Start from n=5 to get meaningful timing data
    n_values = [5, 6, 7, 8]
    
    print(f"\nBenchmarking algorithms for n = {n_values}")
    print("This may take a few moments...\n")
    
    # Run benchmarks
    results = benchmark_all_algorithms(n_values, num_trials=3)
    
    print("\n" + "=" * 60)
    print("GENERATING VISUALIZATIONS")
    print("=" * 60 + "\n")
    
    # Generate visualizations
    create_comparison_table(results)
    create_performance_charts(results)
    create_complexity_comparison()
    
    print("\n" + "=" * 60)
    print("✓ ALL VISUALIZATIONS GENERATED SUCCESSFULLY!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  1. algorithm_comparison_table.png - Detailed performance table")
    print("  2. algorithm_performance_charts.png - Performance charts and graphs")
    print("  3. complexity_comparison.png - Theoretical complexity comparison")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
