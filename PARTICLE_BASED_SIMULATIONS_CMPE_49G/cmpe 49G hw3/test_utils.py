"""
Utilities for quick testing and result analysis.
Useful for parameter tuning and understanding simulation behavior.
"""
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from simulation_3d import Simulation3D
from simulation_2d import Simulation2D
from analytical import channel_response_3d


def quick_test_3d():
    """Quick test of 3D simulation with reduced parameters."""
    print("Quick Test: 3D Simulation (reduced scale for fast execution)")
    print("-" * 60)
    
    sim_params = {
        'rx_center': [0, 0, 0],
        'rx_r_inMicroMeters': 5,
        'rx_tx_distance': 5,
        'tx_emission_pt': [10, 0, 0],
        'D_inMicroMeterSqrPerSecond': 75,
        'tend': 0.1,  # Reduced from 0.4 for testing
        'delta_t': 0.0001,
        'num_molecules': 10000  # Reduced from 50000 for testing
    }
    
    sim = Simulation3D(sim_params)
    cumulative, time_axis = sim.run()
    results = sim.get_results()
    
    print(f"Simulation completed in {time_axis[-1]:.3f} seconds")
    print(f"Final absorbed molecules: {cumulative[-1]} / {sim_params['num_molecules']}")
    print(f"Absorption efficiency: {100*cumulative[-1]/sim_params['num_molecules']:.1f}%")
    
    # Compare with analytical
    r_rx = sim_params['rx_r_inMicroMeters']
    d = sim_params['rx_tx_distance']
    D = sim_params['D_inMicroMeterSqrPerSecond']
    N_tx = sim_params['num_molecules']
    analytical = channel_response_3d(time_axis, r_rx, d, D, N_tx)
    
    # Compute error metrics
    mse = np.mean((cumulative - analytical)**2)
    mae = np.mean(np.abs(cumulative - analytical))
    
    print(f"Mean square error vs analytical: {mse:.2f}")
    print(f"Mean absolute error vs analytical: {mae:.2f}")
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(time_axis, cumulative, 'b-', linewidth=2, label='Simulation')
    ax.plot(time_axis, analytical, 'r--', linewidth=2, label='Analytical')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Cumulative Received Molecules')
    ax.set_title('Quick Test: 3D Diffusion')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('quick_test_3d.png', dpi=150)
    print("\nPlot saved to quick_test_3d.png")
    plt.close()


def quick_test_2d():
    """Quick test of 2D simulation with reduced parameters."""
    print("\nQuick Test: 2D Simulation with Reflection (reduced scale for fast execution)")
    print("-" * 60)
    
    sim_params = {
        'rx_center': [0, 0, 0],
        'rx_r_inMicroMeters': 5,
        'rx_tx_distance': 7,
        'tx_emission_pt': [12, 0, 0],
        'D_inMicroMeterSqrPerSecond': 75,
        'reflecting_line_x_intercept': -100,
        'reflecting_line_y_intercept': 6,
        'tend': 0.3,  # Reduced for testing
        'delta_t': 0.0001,
        'num_molecules': 10000  # Reduced for testing
    }
    
    sim = Simulation2D(sim_params)
    cumulative, time_axis = sim.run()
    results = sim.get_results()
    
    print(f"Simulation completed in {time_axis[-1]:.3f} seconds")
    print(f"Final absorbed molecules: {cumulative[-1]} / {sim_params['num_molecules']}")
    print(f"Absorption efficiency: {100*cumulative[-1]/sim_params['num_molecules']:.1f}%")
    print(f"Total reflections: {results['reflection_count']}")
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(time_axis, cumulative, 'b-', linewidth=2, label='Cumulative')
    ax.fill_between(time_axis, 0, cumulative, alpha=0.2)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Cumulative Received Molecules')
    ax.set_title('Quick Test: 2D Diffusion with Reflection')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('quick_test_2d.png', dpi=150)
    print("Plot saved to quick_test_2d.png")
    plt.close()


def analyze_results_json(json_file):
    """
    Analyze and display statistics from a saved results JSON file.
    
    Parameters:
    -----------
    json_file : str
        Path to the JSON results file
    """
    print(f"\nAnalyzing results file: {json_file}")
    print("-" * 60)
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    cumulative_avg = np.array(data['cumulative_avg'])
    cumulative_std = np.array(data['cumulative_std'])
    time_axis = np.array(data['time'])
    
    print(f"Time range: {time_axis[0]:.4f} to {time_axis[-1]:.4f} s")
    print(f"Time steps: {len(time_axis)}")
    print(f"Final cumulative (avg): {cumulative_avg[-1]:.1f}")
    print(f"Final cumulative (std): {cumulative_std[-1]:.1f}")
    print(f"Peak rate of absorption: {np.max(np.diff(cumulative_avg)):.1f} molecules/step")
    
    if 'analytical' in data:
        analytical = np.array(data['analytical'])
        error = cumulative_avg - analytical
        mse = np.mean(error**2)
        print(f"Mean square error vs analytical: {mse:.2f}")
        print(f"Max error vs analytical: {np.max(np.abs(error)):.1f}")


def compare_configurations(config_1, config_2):
    """
    Compare results from two simulation configurations.
    
    Parameters:
    -----------
    config_1, config_2 : str
        Paths to JSON result files
    """
    print(f"\nComparing configurations:")
    print(f"  Config 1: {config_1}")
    print(f"  Config 2: {config_2}")
    print("-" * 60)
    
    with open(config_1, 'r') as f:
        data1 = json.load(f)
    with open(config_2, 'r') as f:
        data2 = json.load(f)
    
    cum1 = np.array(data1['cumulative_avg'])
    cum2 = np.array(data2['cumulative_avg'])
    time = np.array(data1['time'])
    
    diff = cum1 - cum2
    ratio = cum1 / np.maximum(cum2, 1)  # Avoid division by zero
    
    print(f"Final count Config 1: {cum1[-1]:.1f}")
    print(f"Final count Config 2: {cum2[-1]:.1f}")
    print(f"Difference: {diff[-1]:.1f}")
    print(f"Ratio (Config1/Config2): {ratio[-1]:.2f}x")
    
    # Plot comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    ax1.plot(time, cum1, 'b-', label='Config 1', linewidth=2)
    ax1.plot(time, cum2, 'r-', label='Config 2', linewidth=2)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Cumulative Molecules')
    ax1.set_title('Cumulative Comparison')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(time, diff, 'g-', linewidth=2)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Difference (Config1 - Config2)')
    ax2.set_title('Difference Over Time')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('config_comparison.png', dpi=150)
    print("Comparison plot saved to config_comparison.png")
    plt.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Utilities for simulation testing and analysis')
    parser.add_argument('--test-3d', action='store_true', help='Quick test of 3D simulation')
    parser.add_argument('--test-2d', action='store_true', help='Quick test of 2D simulation')
    parser.add_argument('--analyze', type=str, help='Analyze JSON results file')
    parser.add_argument('--compare', nargs=2, help='Compare two JSON result files')
    
    args = parser.parse_args()
    
    if args.test_3d:
        quick_test_3d()
    elif args.test_2d:
        quick_test_2d()
    elif args.analyze:
        analyze_results_json(args.analyze)
    elif args.compare:
        compare_configurations(args.compare[0], args.compare[1])
    else:
        print("Utilities for simulation testing and analysis")
        print("\nUsage:")
        print("  python test_utils.py --test-3d      : Quick test of 3D simulation")
        print("  python test_utils.py --test-2d      : Quick test of 2D simulation")
        print("  python test_utils.py --analyze FILE : Analyze results JSON file")
        print("  python test_utils.py --compare F1 F2: Compare two results")
