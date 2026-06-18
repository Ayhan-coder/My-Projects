"""
Main runner for molecular diffusion simulations.
Runs Task 1 (3D) and Task 2 (2D) simulations with specified parameters.
"""
import sys
import os
import time
import numpy as np
import json
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from simulation_3d import Simulation3D
from simulation_2d_fast import Simulation2D_Fast as Simulation2D
from analytical import channel_response_3d
from plotting import plot_3d_results, plot_2d_comparison, plot_2d_single


def run_simulation_multiple_times(sim_class, sim_params, num_runs=3):
    """
    Run a simulation multiple times and collect results.
    
    Parameters:
    -----------
    sim_class : class
        Simulation class (Simulation3D or Simulation2D)
    sim_params : dict
        Simulation parameters
    num_runs : int
        Number of times to run the simulation
        
    Returns:
    --------
    results_list : list of dict
        List of results from each run
    """
    results_list = []
    
    for run_idx in range(num_runs):
        print(f"  Run {run_idx + 1}/{num_runs}...", end=' ', flush=True)
        run_start = time.time()
        sim = sim_class(sim_params)
        cumulative, time_axis = sim.run()
        run_elapsed = time.time() - run_start
        results = sim.get_results()
        results_list.append(results)
        print(f"Completed in {run_elapsed:.1f}s. Absorbed: {cumulative[-1]} molecules")
    
    return results_list


def task1_3d():
    """Run Task 1: 3D diffusion simulations."""
    task1_start = time.time()
    print("\n" + "="*70)
    print("TASK 1: 3D Diffusion with Spherical Absorber (No Reflection)")
    print("="*70)
    
    # Task 1-1: D = 75
    print("\nTask 1-1: D = 75 μm²/s")
    print("-" * 70)
    
    sim_params_1_1 = {
        'rx_center': [0, 0, 0],
        'rx_r_inMicroMeters': 5,
        'rx_tx_distance': 5,
        'tx_emission_pt': [10, 0, 0],
        'D_inMicroMeterSqrPerSecond': 75,
        'tend': 0.4,
        'delta_t': 0.0001,
        'num_molecules': 50000
    }
    
    results_1_1 = run_simulation_multiple_times(Simulation3D, sim_params_1_1, num_runs=3)
    
    # Compute analytical response
    r_rx = sim_params_1_1['rx_r_inMicroMeters']
    d = sim_params_1_1['rx_tx_distance']
    D = sim_params_1_1['D_inMicroMeterSqrPerSecond']
    N_tx = sim_params_1_1['num_molecules']
    time_axis = results_1_1[0]['time']
    analytical_1_1 = channel_response_3d(time_axis, r_rx, d, D, N_tx)
    
    # Plot
    plot_3d_results(results_1_1, analytical_1_1, sim_params_1_1,
                    'Task 1-1: 3D Diffusion (D=75 μm²/s)',
                    'plots/task1_1_results.png')
    
    # Save results
    results_1_1_avg = {
        'time': time_axis.tolist(),
        'cumulative_avg': np.mean([r['cumulative'] for r in results_1_1], axis=0).tolist(),
        'cumulative_std': np.std([r['cumulative'] for r in results_1_1], axis=0).tolist(),
        'analytical': analytical_1_1.tolist(),
        'parameters': sim_params_1_1
    }
    
    with open('results/task1_1_results.json', 'w') as f:
        json.dump(results_1_1_avg, f, indent=2)
    
    # Task 1-2: D = 200
    print("\n\nTask 1-2: D = 200 μm²/s")
    print("-" * 70)
    
    sim_params_1_2 = sim_params_1_1.copy()
    sim_params_1_2['D_inMicroMeterSqrPerSecond'] = 200
    
    results_1_2 = run_simulation_multiple_times(Simulation3D, sim_params_1_2, num_runs=3)
    
    # Compute analytical response
    D = sim_params_1_2['D_inMicroMeterSqrPerSecond']
    analytical_1_2 = channel_response_3d(time_axis, r_rx, d, D, N_tx)
    
    # Plot
    plot_3d_results(results_1_2, analytical_1_2, sim_params_1_2,
                    'Task 1-2: 3D Diffusion (D=200 μm²/s)',
                    'plots/task1_2_results.png')
    
    # Save results
    results_1_2_avg = {
        'time': time_axis.tolist(),
        'cumulative_avg': np.mean([r['cumulative'] for r in results_1_2], axis=0).tolist(),
        'cumulative_std': np.std([r['cumulative'] for r in results_1_2], axis=0).tolist(),
        'analytical': analytical_1_2.tolist(),
        'parameters': sim_params_1_2
    }
    
    with open('results/task1_2_results.json', 'w') as f:
        json.dump(results_1_2_avg, f, indent=2)
    
    task1_elapsed = time.time() - task1_start
    print(f"\nTask 1 complete in {task1_elapsed:.1f}s. Results saved.")
    return sim_params_1_1, sim_params_1_2


def task2_2d():
    """Run Task 2: 2D diffusion simulations with reflection."""
    task2_start = time.time()
    print("\n" + "="*70)
    print("TASK 2: 2D Diffusion with Reflecting Line")
    print("="*70)
    
    # Base parameters for all Task 2 simulations
    base_params = {
        'rx_center': [0, 0, 0],
        'rx_r_inMicroMeters': 5,
        'rx_tx_distance': 7,
        'tx_emission_pt': [12, 0, 0],
        'D_inMicroMeterSqrPerSecond': 75,
        'reflecting_line_x_intercept': -100,
        'tend': 1.5,
        'delta_t': 0.0001,
        'num_molecules': 50000
    }
    
    task2_configs = {
        'Task 2-1 (y_int=6)': 6,
        'Task 2-2 (y_int=9)': 9,
        'Task 2-3 (y_int=12)': 12
    }
    
    all_results = {}
    all_params = {}
    comparison_data = {}
    
    for config_name, y_intercept in task2_configs.items():
        config_start = time.time()
        print(f"\n{config_name}")
        print("-" * 70)
        
        sim_params = base_params.copy()
        sim_params['reflecting_line_y_intercept'] = y_intercept
        
        results = run_simulation_multiple_times(Simulation2D, sim_params, num_runs=3)
        
        all_results[config_name] = results
        all_params[config_name] = sim_params
        
        # Get average metrics
        cumulative_counts = [r['cumulative'][-1] for r in results]
        avg_absorbed = np.mean(cumulative_counts)
        std_absorbed = np.std(cumulative_counts)
        
        config_elapsed = time.time() - config_start
        print(f"Average total absorbed: {avg_absorbed:.0f} ± {std_absorbed:.0f} molecules")
        print(f"Config completed in {config_elapsed:.1f}s")
        
        # Save individual results
        config_id = config_name.split('(')[1].strip(')')
        time_axis = results[0]['time']
        results_avg = {
            'time': time_axis.tolist(),
            'cumulative_avg': np.mean([r['cumulative'] for r in results], axis=0).tolist(),
            'cumulative_std': np.std([r['cumulative'] for r in results], axis=0).tolist(),
            'parameters': sim_params
        }
        
        with open(f'results/task2_{config_id}_results.json', 'w') as f:
            json.dump(results_avg, f, indent=2)
    
    # Create comparison plot
    plot_2d_comparison(all_results, all_params,
                      'Task 2: 2D Diffusion with Reflection - Effect of Reflecting Line Position',
                      'plots/task2_comparison.png')
    
    task2_elapsed = time.time() - task2_start
    print(f"\n\nTask 2 complete in {task2_elapsed:.1f}s. Results saved.")
    return all_params


if __name__ == '__main__':
    # Create output directories if they don't exist
    Path('results').mkdir(exist_ok=True)
    Path('plots').mkdir(exist_ok=True)
    
    print("\n" + "="*70)
    print("MOLECULAR DIFFUSION SIMULATION - CMPE49G Project 3")
    print("="*70)
    
    overall_start = time.time()
    
    # Run simulations
    task1_params = task1_3d()
    task2_params = task2_2d()
    
    overall_elapsed = time.time() - overall_start
    
    print("\n" + "="*70)
    print("ALL SIMULATIONS COMPLETED SUCCESSFULLY")
    print("="*70)
    print(f"\nTotal elapsed time: {overall_elapsed:.1f}s ({overall_elapsed/60:.1f} min)")
    print("\nOutput files saved:")
    print("  Plots: plots/*.png")
    print("  Results: results/*.json")
    print("\nParameters saved for report generation.")
