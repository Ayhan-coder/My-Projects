"""
3D molecular diffusion simulation with spherical absorber (no reflection).
"""
import numpy as np
from utils import compute_distance_to_sphere, is_inside_sphere


class Simulation3D:
    """Simulates 3D molecular diffusion with point source and spherical absorber."""
    
    def __init__(self, sim_params):
        """
        Initialize 3D simulation.
        
        Parameters:
        -----------
        sim_params : dict
            Dictionary containing simulation parameters:
            - rx_center : array-like (3,), receiver center position
            - rx_r_inMicroMeters : float, receiver radius in micrometers
            - tx_emission_pt : array-like (3,), transmission point
            - D_inMicroMeterSqrPerSecond : float, diffusion coefficient
            - delta_t : float, time step
            - tend : float, end simulation time
            - num_molecules : int, number of molecules to emit
        """
        self.rx_center = np.array(sim_params['rx_center'], dtype=float)
        self.rx_r = sim_params['rx_r_inMicroMeters']
        self.tx_pt = np.array(sim_params['tx_emission_pt'], dtype=float)
        self.D = sim_params['D_inMicroMeterSqrPerSecond']
        self.delta_t = sim_params['delta_t']
        self.tend = sim_params['tend']
        self.num_molecules = sim_params['num_molecules']
        
        # Derived parameters
        self.steps = int(self.tend / self.delta_t) + 1
        self.time_axis = np.linspace(0, self.tend, self.steps)
        
        # Standard deviation of diffusion step
        self.sigma = np.sqrt(2 * self.D * self.delta_t)
        
        # Initialize tracking
        self.absorbed_count = np.zeros(self.steps, dtype=int)
        self.molecule_positions = None
        self.molecule_active = None
    
    def run(self):
        """Execute the entire simulation."""
        # Initialize molecules at transmission point
        self.molecule_positions = np.tile(self.tx_pt, (self.num_molecules, 1))
        self.molecule_active = np.ones(self.num_molecules, dtype=bool)
        
        # Run simulation loop
        for step in range(1, self.steps):
            # Diffusion step: add random Gaussian displacement
            active_mask = self.molecule_active
            num_active = np.sum(active_mask)
            
            if num_active == 0:
                break
            
            # Add Brownian motion to active molecules
            random_disp = np.random.randn(num_active, 3) * self.sigma
            self.molecule_positions[active_mask] += random_disp
            
            # Check for absorption
            distances = np.linalg.norm(
                self.molecule_positions[active_mask] - self.rx_center,
                axis=1
            )
            
            absorbed_mask = distances < self.rx_r
            
            # Mark absorbed molecules as inactive
            active_indices = np.where(active_mask)[0]
            self.molecule_active[active_indices[absorbed_mask]] = False
            
            # Count cumulative absorbed molecules
            self.absorbed_count[step] = np.sum(~self.molecule_active)
        
        return self.absorbed_count, self.time_axis
    
    def get_results(self):
        """Return cumulative and instantaneous results."""
        cumulative = self.absorbed_count.copy()
        instantaneous = np.diff(cumulative, prepend=0)
        
        return {
            'time': self.time_axis,
            'cumulative': cumulative,
            'instantaneous': instantaneous,
            'num_molecules': self.num_molecules
        }
