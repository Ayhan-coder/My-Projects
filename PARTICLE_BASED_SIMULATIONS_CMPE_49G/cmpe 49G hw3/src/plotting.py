"""
Plotting utilities for simulation results.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Set publication quality plot parameters
rcParams['font.size'] = 11
rcParams['lines.linewidth'] = 1.5
rcParams['axes.grid'] = True
rcParams['grid.alpha'] = 0.3


def plot_3d_results(results_list, analytical, sim_params, title, output_file):
    """
    Plot 3D simulation results with analytical comparison.
    
    Parameters:
    -----------
    results_list : list of dict
        List of simulation results from multiple runs
    analytical : ndarray
        Analytical channel response
    sim_params : dict
        Simulation parameters
    title : str
        Plot title
    output_file : str
        Output file path for saving plot
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Average results from multiple runs
    time_axis = results_list[0]['time']
    cumulative_avg = np.mean([r['cumulative'] for r in results_list], axis=0)
    cumulative_std = np.std([r['cumulative'] for r in results_list], axis=0)
    
    # Get normalization factor
    N_tx = results_list[0]['num_molecules']
    
    # Plot cumulative
    ax1.plot(time_axis, cumulative_avg, 'b-', linewidth=2, label='Simulation (averaged)')
    ax1.fill_between(time_axis, 
                     cumulative_avg - cumulative_std,
                     cumulative_avg + cumulative_std,
                     alpha=0.2, color='blue', label='±1 std dev')
    ax1.plot(time_axis, analytical, 'r--', linewidth=2, label='Analytical')
    
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Cumulative Received Molecules')
    ax1.set_title(f'{title} - Cumulative Response')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    # Plot normalized cumulative for comparison
    cumulative_normalized = cumulative_avg / N_tx
    analytical_normalized = analytical / N_tx
    
    ax2.plot(time_axis, cumulative_normalized, 'b-', linewidth=2, label='Simulation (averaged)')
    ax2.fill_between(time_axis,
                     (cumulative_avg - cumulative_std) / N_tx,
                     (cumulative_avg + cumulative_std) / N_tx,
                     alpha=0.2, color='blue', label='±1 std dev')
    ax2.plot(time_axis, analytical_normalized, 'r--', linewidth=2, label='Analytical')
    
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Normalized Cumulative Response F(t)')
    ax2.set_title(f'{title} - Normalized Cumulative Response (F(t))')
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    
    # Add parameter caption
    param_text = (
        f"rx_center={sim_params['rx_center']}, "
        f"rx_r={sim_params['rx_r_inMicroMeters']} μm, "
        f"tx_pt={sim_params['tx_emission_pt']}, "
        f"D={sim_params['D_inMicroMeterSqrPerSecond']} μm²/s, "
        f"Δt={sim_params['delta_t']} s, "
        f"tend={sim_params['tend']} s, "
        f"N_molecules={sim_params['num_molecules']}"
    )
    fig.text(0.5, 0.01, param_text, ha='center', fontsize=9, wrap=True)
    
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved plot to {output_file}")
    plt.close()


def plot_2d_comparison(results_dict, sim_params_dict, title, output_file):
    """
    Plot 2D simulation results for multiple reflecting line configurations.
    
    Parameters:
    -----------
    results_dict : dict
        Dictionary mapping configuration name to list of results
    sim_params_dict : dict
        Dictionary mapping configuration name to sim_params
    title : str
        Plot title
    output_file : str
        Output file path
    """
    fig, ax = plt.subplots(figsize=(12, 7))
    
    colors = ['b', 'g', 'r', 'm', 'c']
    
    for idx, (config_name, results_list) in enumerate(results_dict.items()):
        # Average results
        time_axis = results_list[0]['time']
        cumulative_avg = np.mean([r['cumulative'] for r in results_list], axis=0)
        cumulative_std = np.std([r['cumulative'] for r in results_list], axis=0)
        N_tx = results_list[0]['num_molecules']
        
        color = colors[idx % len(colors)]
        label = config_name
        
        # Normalized plot
        cumulative_norm = cumulative_avg / N_tx
        cumulative_std_norm = cumulative_std / N_tx
        
        ax.plot(time_axis, cumulative_norm, color=color, linewidth=2, label=label)
        ax.fill_between(time_axis,
                       cumulative_norm - cumulative_std_norm,
                       cumulative_norm + cumulative_std_norm,
                       alpha=0.15, color=color)
    
    ax.set_xlabel('Time (s)', fontsize=12)
    ax.set_ylabel('Normalized Cumulative Response F(t)', fontsize=12)
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.legend(loc='best', fontsize=11)
    ax.grid(True, alpha=0.3)
    
    # Add detailed parameters in caption
    param_texts = []
    for config_name, sim_params in sim_params_dict.items():
        param_text = (
            f"{config_name}: rx_r={sim_params['rx_r_inMicroMeters']} μm, "
            f"y_intercept={sim_params['reflecting_line_y_intercept']} μm, "
            f"D={sim_params['D_inMicroMeterSqrPerSecond']} μm²/s"
        )
        param_texts.append(param_text)
    
    caption = (
        f"Common parameters: rx_center={sim_params_dict[list(sim_params_dict.keys())[0]]['rx_center']}, "
        f"tx_pt={sim_params_dict[list(sim_params_dict.keys())[0]]['tx_emission_pt']}, "
        f"x_intercept={sim_params_dict[list(sim_params_dict.keys())[0]]['reflecting_line_x_intercept']} μm, "
        f"Δt={sim_params_dict[list(sim_params_dict.keys())[0]]['delta_t']} s, "
        f"tend={sim_params_dict[list(sim_params_dict.keys())[0]]['tend']} s\n"
        + "\n".join(param_texts)
    )
    
    fig.text(0.5, -0.01, caption, ha='center', fontsize=9, wrap=True)
    
    plt.tight_layout(rect=[0, 0.08, 1, 1])
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved plot to {output_file}")
    plt.close()


def plot_2d_single(results_list, sim_params, title, output_file):
    """Plot a single 2D simulation result."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    time_axis = results_list[0]['time']
    cumulative_avg = np.mean([r['cumulative'] for r in results_list], axis=0)
    cumulative_std = np.std([r['cumulative'] for r in results_list], axis=0)
    N_tx = results_list[0]['num_molecules']
    
    cumulative_norm = cumulative_avg / N_tx
    cumulative_std_norm = cumulative_std / N_tx
    
    ax.plot(time_axis, cumulative_norm, 'b-', linewidth=2, label='Simulation (averaged)')
    ax.fill_between(time_axis,
                   cumulative_norm - cumulative_std_norm,
                   cumulative_norm + cumulative_std_norm,
                   alpha=0.2, color='blue', label='±1 std dev')
    
    ax.set_xlabel('Time (s)', fontsize=12)
    ax.set_ylabel('Normalized Cumulative Response F(t)', fontsize=12)
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.legend(loc='best', fontsize=11)
    ax.grid(True, alpha=0.3)
    
    # Add parameter caption
    param_text = (
        f"rx_center={sim_params['rx_center']}, rx_r={sim_params['rx_r_inMicroMeters']} μm, "
        f"tx_pt={sim_params['tx_emission_pt']}, D={sim_params['D_inMicroMeterSqrPerSecond']} μm²/s, "
        f"x_intercept={sim_params['reflecting_line_x_intercept']} μm, "
        f"y_intercept={sim_params['reflecting_line_y_intercept']} μm, "
        f"Δt={sim_params['delta_t']} s, tend={sim_params['tend']} s, "
        f"N_molecules={sim_params['num_molecules']}"
    )
    fig.text(0.5, 0.01, param_text, ha='center', fontsize=9, wrap=True)
    
    plt.tight_layout(rect=[0, 0.08, 1, 1])
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved plot to {output_file}")
    plt.close()
