"""
2D molecular diffusion simulation with circular absorber and reflecting line.
"""
import numpy as np
from utils import (
    is_inside_circle_2d,
    reflect_point_across_line,
    distance_to_line_2d
)


class Simulation2D:
    """Simulates 2D molecular diffusion with absorber and reflecting line."""
    
    def __init__(self, sim_params):
        """
        Initialize 2D simulation.
        
        Parameters:
        -----------
        sim_params : dict
            Dictionary containing simulation parameters:
            - rx_center : array-like (2 or 3,), receiver center position
            - rx_r_inMicroMeters : float, receiver radius
            - tx_emission_pt : array-like (2 or 3,), transmission point
            - D_inMicroMeterSqrPerSecond : float, diffusion coefficient
            - delta_t : float, time step
            - tend : float, end simulation time
            - num_molecules : int, number of molecules to emit
            - reflecting_line_x_intercept : float, x-intercept of reflecting line
            - reflecting_line_y_intercept : float, y-intercept of reflecting line
        """
        rx_center = np.array(sim_params['rx_center'], dtype=float)
        self.rx_center = rx_center[:2]  # Use only x, y
        
        self.rx_r = sim_params['rx_r_inMicroMeters']
        
        tx_pt = np.array(sim_params['tx_emission_pt'], dtype=float)
        self.tx_pt = tx_pt[:2]  # Use only x, y
        
        self.D = sim_params['D_inMicroMeterSqrPerSecond']
        self.delta_t = sim_params['delta_t']
        self.tend = sim_params['tend']
        self.num_molecules = sim_params['num_molecules']
        
        # Reflecting line parameters
        self.line_x_int = sim_params['reflecting_line_x_intercept']
        self.line_y_int = sim_params['reflecting_line_y_intercept']
        
        # Derived parameters
        self.steps = int(self.tend / self.delta_t) + 1
        self.time_axis = np.linspace(0, self.tend, self.steps)
        
        # Standard deviation of diffusion step
        self.sigma = np.sqrt(2 * self.D * self.delta_t)
        
        # Initialize tracking
        self.absorbed_count = np.zeros(self.steps, dtype=int)
        self.molecule_positions = None
        self.molecule_active = None
        self.reflection_count = 0
    
    def _check_and_reflect(self, position):
        """
        Check if molecule crossed the reflecting line and reflect if necessary.
        
        Parameters:
        -----------
        position : array-like (2,)
            Current position [x, y]
            
        Returns:
        --------
        position : ndarray (2,)
            Position after reflection (if needed)
        num_reflections : int
            Number of reflections applied
        """
        num_reflections = 0
        pos = np.array(position, dtype=float)
        
        # Check if molecule is on the wrong side of the line
        # We need to define which side is "wrong"
        # Determine the correct side by checking the transmitter position
        tx_side = distance_to_line_2d(self.tx_pt, self.line_x_int, self.line_y_int)
        
        # If transmitter is on positive side, molecules should stay on positive side
        max_iterations = 5  # Prevent infinite loops
        iterations = 0
        
        while iterations < max_iterations:
            current_side = distance_to_line_2d(pos, self.line_x_int, self.line_y_int)
            
            # If on wrong side, reflect
            if (tx_side > 0 and current_side < 0) or (tx_side < 0 and current_side > 0):
                pos = reflect_point_across_line(pos, self.line_x_int, self.line_y_int)
                num_reflections += 1
                iterations += 1
            else:
                break
        
        return pos, num_reflections
    
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
            random_disp = np.random.randn(num_active, 2) * self.sigma
            self.molecule_positions[active_mask] += random_disp
            
            # Apply reflection boundary
            for i in np.where(active_mask)[0]:
                self.molecule_positions[i], reflections = self._check_and_reflect(
                    self.molecule_positions[i]
                )
                self.reflection_count += reflections
            
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
            'num_molecules': self.num_molecules,
            'reflection_count': self.reflection_count
        }
