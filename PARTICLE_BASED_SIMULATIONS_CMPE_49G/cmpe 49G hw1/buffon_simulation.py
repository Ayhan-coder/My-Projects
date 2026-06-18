"""
CmpE 49G - Project 1: Monte Carlo Simulation for Buffon's Needle
Comprehensive implementation of classic and concentric circle variants.

@Author: Ali Ayhan Günder 2021400219
@Date: 26 February 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import argparse


# ============================================================================
# PROBLEM 1: CLASSIC BUFFON'S NEEDLE (PARALLEL LINES)
# ============================================================================

def analytical_probability_classic(L, D):
    """
    Analytical solution for Buffon's Needle with parallel lines.
    
    Derivation:
    - Needle center at distance x ~ U(0, D/2) from nearest line
    - Angle θ ~ U(0, π/2) with horizontal
    - Crosses if x <= (L/2)*sin(θ)
    - P(cross) = ∫₀^(π/2) (2/πD) * (L/2)*sin(θ) dθ = 2L/(πD)
    
    Parameters:
        L: Needle length
        D: Distance between parallel lines (L < D required)
    
    Returns:
        Theoretical crossing probability
    """
    assert L < D, "Needle length must be less than line spacing"
    return 2.0 * L / (np.pi * D)


def simulate_buffon_classic(L, D, N, seed=42):
    """
    Monte Carlo simulation of Buffon's Needle on parallel lines.
    
    Parameters:
        L: Needle length
        D: Distance between parallel lines
        N: Number of needles to simulate
        seed: Random seed for reproducibility
    
    Returns:
        Estimated crossing probability
    """
    np.random.seed(seed)
    
    # Sample needle center distance from nearest line: x ~ U(0, D/2)
    x = np.random.uniform(0, D / 2, N)
    
    # Sample needle angle: θ ~ U(0, π/2)
    theta = np.random.uniform(0, np.pi / 2, N)
    
    # Needle crosses if x <= (L/2)*sin(θ)
    # This is the projection of half-needle perpendicular to lines
    crosses = x <= (L / 2) * np.sin(theta)
    
    # Estimate probability as fraction of crossings
    p_estimated = np.sum(crosses) / N
    
    return p_estimated


def run_problem1_convergence(L_values, D_values, N_values, seed=42):
    """
    Run convergence analysis for Problem 1 across multiple (L, D) pairs and N values.
    
    Parameters:
        L_values: List of needle lengths
        D_values: List of line spacings
        N_values: List of sample sizes
        seed: Random seed
    
    Returns:
        Dictionary with results indexed by (L, D)
    """
    results = {}
    
    for L, D in zip(L_values, D_values):
        p_analytical = analytical_probability_classic(L, D)
        estimates = []
        errors = []
        
        for N in N_values:
            p_est = simulate_buffon_classic(L, D, N, seed=seed)
            error = abs(p_est - p_analytical)
            estimates.append(p_est)
            errors.append(error)
        
        results[(L, D)] = {
            'estimates': np.array(estimates),
            'analytical': p_analytical,
            'errors': np.array(errors)
        }
    
    return results


# ============================================================================
# PROBLEM 2: CONCENTRIC CIRCLES
# ============================================================================

def analytical_probability_concentric(L, D):
    """
    Analytical solution for Buffon's Needle with concentric circles.
    
    Surprising Result: Despite the different geometry, the probability is also 2L/(πD)!
    This follows from a beautiful symmetry: as circles get larger, their density decreases
    in such a way that the total probability remains constant.
    
    Parameters:
        L: Needle length
        D: Base circle radius (L < D required)
    
    Returns:
        Theoretical crossing probability
    """
    assert L < D, "Needle length must be less than base circle radius"
    return 2.0 * L / (np.pi * D)


def check_line_segment_circle_intersection_vectorized(x1, y1, x2, y2, radius):
    """
    Vectorized check: does line segment from (x1,y1) to (x2,y2) cross the circle
    centered at origin with given radius?
    
    Uses quadratic formula: find t in [0,1] such that ||(x1,y1) + t*(dx,dy)|| = radius.
    The segment crosses the circle if at least one solution t lies in [0, 1].
    Note: a segment entirely inside the circle does NOT cross it.
    
    Parameters:
        x1, y1: Starting points (arrays)
        x2, y2: Ending points (arrays)
        radius: Circle radius (scalar)
    
    Returns:
        Boolean array indicating crossing for each segment
    """
    dx = x2 - x1
    dy = y2 - y1
    
    # Quadratic coefficients: ||P0 + t*D||^2 = r^2
    # Expands to: a*t^2 + b*t + c = 0
    a = dx**2 + dy**2
    b = 2.0 * (x1 * dx + y1 * dy)
    c = x1**2 + y1**2 - radius**2
    
    # Discriminant
    discriminant = b**2 - 4.0 * a * c
    
    # Initialize result
    crosses = np.zeros(len(x1), dtype=bool)
    
    # Only check where discriminant >= 0 (real solutions exist)
    valid = discriminant >= 0
    
    if np.any(valid):
        sqrt_disc = np.sqrt(discriminant[valid])
        a_valid = a[valid]
        b_valid = b[valid]
        
        # Two intersection parameter values
        t1 = (-b_valid - sqrt_disc) / (2.0 * a_valid)
        t2 = (-b_valid + sqrt_disc) / (2.0 * a_valid)
        
        # The segment crosses the circle if at least one root is in [0, 1].
        # This ensures the segment actually touches the circle boundary,
        # excluding cases where the segment is entirely inside the circle
        # (where t1 < 0 and t2 > 1, so no root is in [0,1]).
        t1_in_range = (t1 >= 0.0) & (t1 <= 1.0)
        t2_in_range = (t2 >= 0.0) & (t2 <= 1.0)
        crosses[valid] = t1_in_range | t2_in_range
    
    return crosses


def simulate_buffon_concentric(L, D, N, square_size=None, seed=42):
    """
    Monte Carlo simulation of Buffon's Needle with concentric circles.
    
    Sampling strategy:
    - Needle center (cx, cy) uniform in a large square
    - Angle θ ~ U(0, 2π)
    - For each needle, check intersection only with the nearest circles
      (those within L/2 of the needle center's radial distance)
    
    Parameters:
        L: Needle length
        D: Base circle radius (distance between consecutive circles)
        N: Number of needles to simulate
        square_size: Side length of sampling region (default: 200*D)
        seed: Random seed for reproducibility
    
    Returns:
        Estimated crossing probability
    """
    if square_size is None:
        square_size = 200.0 * D
    
    np.random.seed(seed)
    
    # Sample needle centers uniformly in square
    cx = np.random.uniform(-square_size / 2, square_size / 2, N)
    cy = np.random.uniform(-square_size / 2, square_size / 2, N)
    
    # Sample needle angle: θ ~ U(0, 2π)
    theta = np.random.uniform(0, 2 * np.pi, N)
    
    # Calculate needle endpoints
    x1 = cx - (L / 2) * np.cos(theta)
    y1 = cy - (L / 2) * np.sin(theta)
    x2 = cx + (L / 2) * np.cos(theta)
    y2 = cy + (L / 2) * np.sin(theta)
    
    # Distance of each needle center from origin
    r_center = np.sqrt(cx**2 + cy**2)
    
    # For each needle, determine candidate circle indices.
    # The needle extends at most L/2 from its center, so it can only
    # cross circles with radius within [r_center - L/2, r_center + L/2].
    # Circle k has radius k*D, so relevant k values are:
    #   k_min = max(1, floor((r_center - L/2) / D))
    #   k_max = ceil((r_center + L/2) / D) + 1
    k_min_arr = np.maximum(1, np.floor((r_center - L / 2) / D).astype(int))
    k_max_arr = np.ceil((r_center + L / 2) / D).astype(int) + 1
    
    # Track which needles cross any circle
    crosses_any = np.zeros(N, dtype=bool)
    
    # Find the global range of k values we need to check
    global_k_min = int(np.min(k_min_arr))
    global_k_max = int(np.max(k_max_arr))
    
    # Check each circle, but only for needles that could possibly intersect it
    for k in range(global_k_min, global_k_max + 1):
        radius = k * D
        # Only check needles whose center is within L/2 + some margin of this circle
        candidate_mask = (k_min_arr <= k) & (k_max_arr >= k)
        
        if not np.any(candidate_mask):
            continue
        
        # Extract candidate needles
        idx = np.where(candidate_mask)[0]
        crosses_k = check_line_segment_circle_intersection_vectorized(
            x1[idx], y1[idx], x2[idx], y2[idx], radius
        )
        crosses_any[idx] |= crosses_k
    
    # Estimate probability
    p_estimated = np.sum(crosses_any) / N
    
    return p_estimated


def run_problem2_convergence(L_values, D_values, N_values, seed=42):
    """
    Run convergence analysis for Problem 2 across multiple (L, D) pairs and N values.
    
    Parameters:
        L_values: List of needle lengths
        D_values: List of base circle radii
        N_values: List of sample sizes
        seed: Random seed
    
    Returns:
        Dictionary with results indexed by (L, D)
    """
    results = {}
    
    for L, D in zip(L_values, D_values):
        p_analytical = analytical_probability_concentric(L, D)
        estimates = []
        errors = []
        for N in N_values:
            p_est = simulate_buffon_concentric(L, D, N, seed=seed)
            error = abs(p_est - p_analytical)
            estimates.append(p_est)
            errors.append(error)
        results[(L, D)] = {
            'estimates': np.array(estimates),
            'analytical': p_analytical,
            'errors': np.array(errors)
        }
    return results


# ============================================================================
# PLOTTING AND VISUALIZATION
# ============================================================================

def create_convergence_plots(results, N_values, problem_id, output_dir='plots'):
    """
    Create convergence plots for estimated probability vs. log10(N).
    
    Parameters:
        results: Dictionary from run_problem*_convergence()
        N_values: Array of sample sizes (must be same as used in results)
        problem_id: 1 (classic) or 2 (concentric)
        output_dir: Directory to save plots
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    log_N = np.log10(N_values)
    
    # Create figure with subplots for each (L, D) pair
    fig, axes = plt.subplots(len(results), 1, figsize=(10, 4 * len(results)))
    if len(results) == 1:
        axes = [axes]
    
    for idx, (L, D) in enumerate(sorted(results.keys())):
        data = results[(L, D)]
        estimates = data['estimates']
        analytical = data['analytical']
        
        axes[idx].plot(log_N, estimates, 'bo-', linewidth=2, markersize=8, 
                       label='Monte Carlo Estimate', alpha=0.7)
        axes[idx].axhline(y=analytical, color='r', linestyle='--', linewidth=2, 
                         label=f'Analytical: {analytical:.6f}')
        axes[idx].set_xlabel('log10(Number of Needles)', fontsize=11, fontweight='bold')
        axes[idx].set_ylabel('Crossing Probability', fontsize=11, fontweight='bold')
        axes[idx].set_title(f'Problem {problem_id}: L={L}, D={D} | Theoretical P = 2L/(pi*D)', 
                           fontsize=12, fontweight='bold')
        axes[idx].grid(True, alpha=0.3, linestyle='--')
        axes[idx].legend(fontsize=10, loc='best')
        axes[idx].set_ylim([0, 1.1 * max(np.max(estimates), analytical)])
    
    plt.tight_layout()
    filename = f'{output_dir}/problem{problem_id}_convergence.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"[OK] Saved convergence plot: {filename}")
    plt.close()


def create_error_plots(results, N_values, problem_id, output_dir='plots'):
    """
    Create error (|estimate - analytical|) vs log10(N) plots.
    
    Parameters:
        results: Dictionary from run_problem*_convergence()
        N_values: Array of sample sizes
        problem_id: 1 (classic) or 2 (concentric)
        output_dir: Directory to save plots
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    log_N = np.log10(N_values)
    
    fig, axes = plt.subplots(len(results), 1, figsize=(10, 4 * len(results)))
    if len(results) == 1:
        axes = [axes]
    
    for idx, (L, D) in enumerate(sorted(results.keys())):
        data = results[(L, D)]
        errors = data['errors']
        
        axes[idx].semilogy(log_N, errors, 'go-', linewidth=2, markersize=8, alpha=0.7, 
                          label='Absolute Error')
        axes[idx].set_xlabel('log10(Number of Needles)', fontsize=11, fontweight='bold')
        axes[idx].set_ylabel('Absolute Error', fontsize=11, fontweight='bold')
        axes[idx].set_title(f'Problem {problem_id}: Absolute Error | L={L}, D={D}', 
                           fontsize=12, fontweight='bold')
        axes[idx].grid(True, alpha=0.3, linestyle='--', which='both')
        axes[idx].legend(fontsize=10, loc='best')
    
    plt.tight_layout()
    filename = f'{output_dir}/problem{problem_id}_error.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"[OK] Saved error plot: {filename}")
    plt.close()


def print_results_table(results, N_values, problem_id):
    """
    Print convergence results as formatted table.
    
    Parameters:
        results: Dictionary from run_problem*_convergence()
        N_values: Array of sample sizes
        problem_id: 1 (classic) or 2 (concentric)
    """
    print(f"\n{'=' * 90}")
    print(f"PROBLEM {problem_id} - CONVERGENCE ANALYSIS")
    print(f"{'=' * 90}\n")
    
    for L, D in sorted(results.keys()):
        print(f"Case: L={L}, D={D}")
        print(f"Analytical Probability: {results[(L, D)]['analytical']:.8f}")
        print(f"{'N':<12} {'Estimated P':<18} {'Analytical P':<18} {'Abs Error':<15}")
        print("-" * 63)
        
        for i, N in enumerate(N_values):
            est = results[(L, D)]['estimates'][i]
            ana = results[(L, D)]['analytical']
            err = results[(L, D)]['errors'][i]
            print(f"{N:<12} {est:<18.8f} {ana:<18.8f} {err:<15.8f}")
        print()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Buffon\'s Needle Monte Carlo Simulation (Classic & Concentric Circles)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run both problems with default parameters
  python buffon_simulation.py

  # Run only Problem 1 with custom parameters
  python buffon_simulation.py --problem_id 1 --L 1.5 --D 2.5 --seed 42

  # Run Problem 2 with specific parameters
  python buffon_simulation.py --problem_id 2 --L 2.0 --D 3.0 --seed 42
        """
    )
    
    parser.add_argument('--problem_id', type=int, choices=[0, 1, 2], default=0,
                       help='0: both problems (default), 1: classic only, 2: concentric only')
    parser.add_argument('--L', type=float, default=1.0,
                       help='Needle length (default: run convergence for multiple values)')
    parser.add_argument('--D', type=float, default=2.0,
                       help='Line spacing or base circle radius (default: run convergence)')
    parser.add_argument('--N', type=int, default=None,
                       help='Sample size (default: run convergence analysis)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility (default: 42)')
    
    args = parser.parse_args()
    
    # Define standard test cases
    L_values = [1.0, 2.0, 3.0]
    D_values = [2.0, 3.0, 5.0]
    N_values = [100, 1_000, 10_000, 100_000, 1_000_000]
    
    print("\n" + "=" * 90)
    print("BUFFON'S NEEDLE - MONTE CARLO SIMULATION")
    print("=" * 90)
    print(f"Seed: {args.seed}")
    print(f"Test cases: {list(zip(L_values, D_values))}")
    print()
    
    # Problem 1: Classic Buffon's Needle
    if args.problem_id in [0, 1]:
        results_p1 = run_problem1_convergence(L_values, D_values, N_values, seed=args.seed)
        print_results_table(results_p1, N_values, problem_id=1)
        create_convergence_plots(results_p1, N_values, problem_id=1)
        create_error_plots(results_p1, N_values, problem_id=1)
    
    # Problem 2: Concentric Circles
    if args.problem_id in [0, 2]:
        results_p2 = run_problem2_convergence(L_values, D_values, N_values, seed=args.seed)
        print_results_table(results_p2, N_values, problem_id=2)
        create_convergence_plots(results_p2, N_values, problem_id=2)
        create_error_plots(results_p2, N_values, problem_id=2)
    
    print("=" * 90)
    print("Simulation complete! Check the 'plots/' directory for figures.")
    print("=" * 90 + "\n")


if __name__ == '__main__':
    main()
