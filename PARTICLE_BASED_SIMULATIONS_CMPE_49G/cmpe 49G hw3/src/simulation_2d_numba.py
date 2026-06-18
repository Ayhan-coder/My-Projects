"""
Numba-accelerated 2D molecular diffusion with reflection.
Uses JIT compilation for fast CPU execution (Numba can also use GPU).
"""
import numpy as np
import numba as nb

# Fast reflection kernel (JIT-compiled)
@nb.njit(parallel=True)
def update_molecules_numba(positions, active_mask, rx_center, rx_r, tx_pt, 
                           sigma, line_x_int, line_y_int, D, delta_t):
    """
    Numba-accelerated kernel for molecule updates.
    
    Using numba.njit with parallel=True for multi-threaded execution.
    """
    n_active = np.sum(active_mask)
    absorbed_indices = np.empty(n_active, dtype=np.int32)
    n_absorbed = 0
    reflections = 0
    
    # Line parameters
    b = line_y_int
    m = -b / line_x_int
    a = m
    b_coeff = -1.0
    c = b
    denom = np.sqrt(a**2 + b_coeff**2)
    
    # Transmitter side
    tx_side_num = a * tx_pt[0] + b_coeff * tx_pt[1] + c
    tx_side = 1.0 if tx_side_num > 0 else (-1.0 if tx_side_num < 0 else 0.0)
    
    # Process molecules in parallel
    for i in nb.prange(len(positions)):
        if active_mask[i]:
            # Brownian motion (random walk)
            rand1 = np.random.randn()
            rand2 = np.random.randn()
            positions[i, 0] += rand1 * sigma
            positions[i, 1] += rand2 * sigma
            
            # Reflection check
            for _ in range(5):
                numerator = a * positions[i, 0] + b_coeff * positions[i, 1] + c
                dist = numerator / denom
                current_side = 1.0 if dist > 0 else (-1.0 if dist < 0 else 0.0)
                
                if (current_side * tx_side) < 0:
                    # Reflect
                    denom2 = a**2 + b_coeff**2
                    x0, y0 = positions[i, 0], positions[i, 1]
                    positions[i, 0] = x0 - 2 * a * numerator / denom2
                    positions[i, 1] = y0 - 2 * b_coeff * numerator / denom2
                    reflections += 1
                else:
                    break
            
            # Absorption check
            dx = positions[i, 0] - rx_center[0]
            dy = positions[i, 1] - rx_center[1]
            dist_sq = dx*dx + dy*dy
            
            if dist_sq < rx_r * rx_r:
                absorbed_indices[n_absorbed] = i
                n_absorbed += 1
    
    return absorbed_indices[:n_absorbed], reflections


class Simulation2D_Numba:
    """Numba-accelerated 2D molecular diffusion simulation."""
    
    def __init__(self, sim_params):
        """Initialize Numba simulation."""
        rx_center = np.array(sim_params['rx_center'], dtype=np.float64)
        self.rx_center = rx_center[:2]
        
        self.rx_r = float(sim_params['rx_r_inMicroMeters'])
        
        tx_pt = np.array(sim_params['tx_emission_pt'], dtype=np.float64)
        self.tx_pt = tx_pt[:2]
        
        self.D = float(sim_params['D_inMicroMeterSqrPerSecond'])
        self.delta_t = float(sim_params['delta_t'])
        self.tend = float(sim_params['tend'])
        self.num_molecules = int(sim_params['num_molecules'])
        
        self.line_x_int = float(sim_params['reflecting_line_x_intercept'])
        self.line_y_int = float(sim_params['reflecting_line_y_intercept'])
        
        self.steps = int(self.tend / self.delta_t) + 1
        self.time_axis = np.linspace(0, self.tend, self.steps)
        
        self.sigma = np.sqrt(2 * self.D * self.delta_t)
        
        self.absorbed_count = np.zeros(self.steps, dtype=np.int32)
        self.molecule_positions = None
        self.molecule_active = None
        self.reflection_count = 0
    
    def run(self):
        """Execute Numba-accelerated simulation."""
        # Initialize molecules
        self.molecule_positions = np.tile(self.tx_pt, (self.num_molecules, 1)).astype(np.float64)
        self.molecule_active = np.ones(self.num_molecules, dtype=np.bool_)
        
        # Set random seed for reproducibility
        np.random.seed(42)
        
        # Main simulation loop
        for step in range(1, self.steps):
            num_active = np.sum(self.molecule_active)
            
            if num_active == 0:
                break
            
            # Numba-accelerated update
            absorbed_indices, reflections = update_molecules_numba(
                self.molecule_positions,
                self.molecule_active,
                self.rx_center,
                self.rx_r,
                self.tx_pt,
                float(self.sigma),
                float(self.line_x_int),
                float(self.line_y_int),
                self.D,
                self.delta_t
            )
            
            # Mark absorbed molecules
            for idx in absorbed_indices:
                self.molecule_active[idx] = False
            
            self.reflection_count += reflections
            
            # Count cumulative
            self.absorbed_count[step] = np.sum(~self.molecule_active)
        
        return self.absorbed_count, self.time_axis
    
    def get_results(self):
        """Return results."""
        cumulative = self.absorbed_count.copy()
        instantaneous = np.diff(cumulative, prepend=0)
        
        return {
            'time': self.time_axis,
            'cumulative': cumulative,
            'instantaneous': instantaneous,
            'num_molecules': self.num_molecules,
            'reflection_count': self.reflection_count,
            'gpu_used': False  # Numba uses multi-threaded CPU by default
        }
