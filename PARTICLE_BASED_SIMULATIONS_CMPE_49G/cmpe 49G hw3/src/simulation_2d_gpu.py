"""
GPU-accelerated 2D molecular diffusion simulation with reflection (using CuPy).
"""
import numpy as np

try:
    import cupy as cp
    HAS_GPU = True
except ImportError:
    HAS_GPU = False
    cp = np

from utils import is_inside_circle_2d, reflect_point_across_line, distance_to_line_2d


class Simulation2D_GPU:
    """GPU-accelerated 2D molecular diffusion with absorber and reflecting line."""
    
    def __init__(self, sim_params):
        """Initialize 2D GPU simulation."""
        rx_center = np.array(sim_params['rx_center'], dtype=np.float32)
        self.rx_center = cp.asarray(rx_center[:2])
        
        self.rx_r = np.float32(sim_params['rx_r_inMicroMeters'])
        
        tx_pt = np.array(sim_params['tx_emission_pt'], dtype=np.float32)
        self.tx_pt = cp.asarray(tx_pt[:2])
        
        self.D = np.float32(sim_params['D_inMicroMeterSqrPerSecond'])
        self.delta_t = np.float32(sim_params['delta_t'])
        self.tend = sim_params['tend']
        self.num_molecules = sim_params['num_molecules']
        
        # Reflecting line parameters
        self.line_x_int = np.float32(sim_params['reflecting_line_x_intercept'])
        self.line_y_int = np.float32(sim_params['reflecting_line_y_intercept'])
        
        # Derived parameters
        self.steps = int(self.tend / self.delta_t) + 1
        self.time_axis = np.linspace(0, self.tend, self.steps)
        
        # Standard deviation for GPU
        self.sigma = np.float32(np.sqrt(2 * self.D * self.delta_t))
        
        # Initialize tracking
        self.absorbed_count = np.zeros(self.steps, dtype=np.int32)
        self.molecule_positions = None
        self.molecule_active = None
        self.reflection_count = 0
        
        self.gpu_available = HAS_GPU
        if not HAS_GPU:
            print("WARNING: CuPy not available, falling back to CPU")
    
    def _check_and_reflect_gpu(self, positions, active_mask):
        """
        GPU-accelerated reflection check and application.
        
        Parameters:
        -----------
        positions : cupy array (N, 2)
            Current positions of molecules
        active_mask : cupy array (N,) bool
            Which molecules are active
            
        Returns:
        --------
        positions : cupy array (N, 2)
            Updated positions after reflection
        num_reflections : int
            Total reflections applied
        """
        # Compute line parameters
        b = self.line_y_int
        m = -b / self.line_x_int
        a = m
        b_coeff = np.float32(-1.0)
        c = b
        
        # Determine correct side
        tx_side_num = a * self.tx_pt[0] + b_coeff * self.tx_pt[1] + c
        tx_side = cp.sign(tx_side_num)
        
        # Compute distances for all active molecules
        denom = cp.sqrt(a**2 + b_coeff**2)
        
        num_reflections = 0
        max_iterations = 5
        
        for iteration in range(max_iterations):
            active_indices = cp.where(active_mask)[0]
            
            if len(active_indices) == 0:
                break
            
            active_pos = positions[active_indices]
            
            # Compute signed distances
            numerator = a * active_pos[:, 0] + b_coeff * active_pos[:, 1] + c
            distances = numerator / denom
            current_side = cp.sign(distances)
            
            # Find molecules on wrong side
            wrong_side = (current_side * tx_side) < 0
            
            if not cp.any(wrong_side):
                break
            
            # Reflect wrong-side molecules
            wrong_indices = active_indices[cp.where(wrong_side)[0]]
            
            for idx in cp.asnumpy(wrong_indices):
                x0, y0 = positions[idx, 0], positions[idx, 1]
                numerator_val = float(a * x0 + b_coeff * y0 + c)
                denom_val = float(denom)
                
                x_reflected = float(x0) - 2 * a * numerator_val / (denom_val**2)
                y_reflected = float(y0) - 2 * b_coeff * numerator_val / (denom_val**2)
                
                positions[idx, 0] = np.float32(x_reflected)
                positions[idx, 1] = np.float32(y_reflected)
                num_reflections += 1
        
        return positions, num_reflections
    
    def run(self):
        """Execute the GPU-accelerated simulation."""
        if not self.gpu_available:
            return self._run_cpu()
        
        # Initialize molecules on GPU
        self.molecule_positions = cp.tile(cp.asarray(self.tx_pt), (self.num_molecules, 1))
        self.molecule_active = cp.ones(self.num_molecules, dtype=bool)
        
        # Simulation loop
        for step in range(1, self.steps):
            active_mask = self.molecule_active
            num_active = cp.sum(active_mask)
            
            if num_active == 0:
                break
            
            # GPU random number generation
            random_disp = cp.random.randn(int(num_active), 2, dtype=np.float32) * self.sigma
            self.molecule_positions[active_mask] += random_disp
            
            # Apply reflection (partially on GPU)
            self.molecule_positions, num_refl = self._check_and_reflect_gpu(
                self.molecule_positions, active_mask
            )
            self.reflection_count += num_refl
            
            # Check absorption on GPU
            active_indices = cp.where(active_mask)[0]
            distances = cp.linalg.norm(
                self.molecule_positions[active_indices] - self.rx_center,
                axis=1
            )
            
            absorbed_mask_local = distances < self.rx_r
            
            # Update inactive molecules
            absorbed_indices = active_indices[cp.where(absorbed_mask_local)[0]]
            self.molecule_active[absorbed_indices] = False
            
            # Count cumulative absorbed
            self.absorbed_count[step] = int(cp.sum(~self.molecule_active))
        
        # Copy results back to CPU
        self.absorbed_count = cp.asnumpy(self.absorbed_count)
        
        return self.absorbed_count, self.time_axis
    
    def _run_cpu(self):
        """Fallback to CPU implementation."""
        from simulation_2d import Simulation2D
        sim_cpu = Simulation2D({
            'rx_center': cp.asnumpy(self.rx_center),
            'rx_r_inMicroMeters': float(self.rx_r),
            'rx_tx_distance': 7,
            'tx_emission_pt': cp.asnumpy(self.tx_pt),
            'D_inMicroMeterSqrPerSecond': float(self.D),
            'reflecting_line_x_intercept': float(self.line_x_int),
            'reflecting_line_y_intercept': float(self.line_y_int),
            'tend': self.tend,
            'delta_t': float(self.delta_t),
            'num_molecules': self.num_molecules
        })
        return sim_cpu.run()
    
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
            'gpu_used': self.gpu_available
        }
