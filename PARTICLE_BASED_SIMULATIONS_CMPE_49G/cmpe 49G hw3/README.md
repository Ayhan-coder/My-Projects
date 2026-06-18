# Molecular Diffusion Simulation - CMPE49G Project 3

## Project Overview

This project simulates the effect of reflection on molecular diffusion in communication channels.

**Task 1**: 3D molecular diffusion with a spherical absorber (point source, no reflection)
**Task 2**: 2D molecular diffusion with a reflecting line

## Directory Structure

```
cmpe 49G hw3/
├── src/                          # Source code modules
│   ├── analytical.py             # Analytical formula for 3D channel response
│   ├── simulation_3d.py           # 3D diffusion simulation
│   ├── simulation_2d.py           # 2D diffusion with reflection
│   ├── utils.py                   # Utility functions (geometry, reflection)
│   └── plotting.py                # Plotting utilities
├── results/                       # Simulation results (JSON files)
├── plots/                         # Output plots (PNG files)
├── main.py                        # Main runner script
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. **Clone/extract the project to your working directory**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Simulations

### Full Project (All Tasks)

To run all simulations (Task 1-1, Task 1-2, and Task 2-1 through 2-3):

```bash
python main.py
```

This will:
- Run 3 independent simulations for each parameter set
- Average results to reduce fluctuations
- Generate comparison plots
- Save results and plots to `results/` and `plots/` directories

**Estimated Runtime**: 30-60 minutes (depending on your machine)

### Individual Task Simulations

You can also run individual simulations by importing and using the classes directly:

```python
from src.simulation_3d import Simulation3D
from src.simulation_2d import Simulation2D

# Example: Run a single Task 1-1 simulation
sim_params = {
    'rx_center': [0, 0, 0],
    'rx_r_inMicroMeters': 5,
    'rx_tx_distance': 5,
    'tx_emission_pt': [10, 0, 0],
    'D_inMicroMeterSqrPerSecond': 75,
    'tend': 0.4,
    'delta_t': 0.0001,
    'num_molecules': 50000
}

sim = Simulation3D(sim_params)
cumulative, time_axis = sim.run()
results = sim.get_results()
```

## Simulation Parameters

### Task 1-1: 3D, D=75 μm²/s
- Receiver center: [0, 0, 0] μm
- Receiver radius: 5 μm
- Distance (Tx to Rx surface): 5 μm
- Transmission point: [10, 0, 0] μm
- Diffusion coefficient: 75 μm²/s
- Time step: 0.0001 s
- End time: 0.4 s
- Number of molecules: 50,000

### Task 1-2: 3D, D=200 μm²/s
Same as Task 1-1, but with D=200 μm²/s

### Task 2 (2D with Reflection)
- Receiver center: [0, 0, 0] μm
- Receiver radius: 5 μm
- Distance (Tx to Rx surface): 7 μm
- Transmission point: [12, 0, 0] μm
- Diffusion coefficient: 75 μm²/s
- Reflecting line x-intercept: -100 μm
- Time step: 0.0001 s
- End time: 1.5 s
- Number of molecules: 50,000

**Variations**:
- Task 2-1: y-intercept = 6 μm
- Task 2-2: y-intercept = 9 μm
- Task 2-3: y-intercept = 12 μm

## Output Files

### Plots
- `task1_1_results.png`: Task 1-1 cumulative and normalized response
- `task1_2_results.png`: Task 1-2 cumulative and normalized response
- `task2_comparison.png`: Task 2 all three configurations compared

### Results (JSON format)
- `task1_1_results.json`: Averaged results, parameters, and analytical comparison
- `task1_2_results.json`: Averaged results, parameters, and analytical comparison
- `task2_{config}_results.json`: Results for each Task 2 configuration

## Key Formulas

### 3D Analytical Channel Response
$$N_{Rx}(t) = N_{Tx} \cdot \frac{r_{Rx}}{r_{Rx} + d} \cdot \mathrm{erfc}\left(\frac{d}{\sqrt{4Dt}}\right)$$

Where:
- $N_{Rx}(t)$ = cumulative received molecules at time t
- $N_{Tx}$ = transmitted molecules
- $r_{Rx}$ = receiver radius
- $d$ = distance from emission point to receiver surface
- $D$ = diffusion coefficient
- $\mathrm{erfc}$ = complementary error function

### 2D Reflection
Molecules reflected across a line with equation: $y = mx + b$
Uses the standard point reflection formula with respect to a line.

## Code Modules

### `src/analytical.py`
- `channel_response_3d()`: Computes analytical 3D response
- `channel_response_3d_impulse()`: Computes impulse response

### `src/simulation_3d.py`
- `Simulation3D`: Main 3D simulation class
  - `run()`: Execute simulation
  - `get_results()`: Return formatted results

### `src/simulation_2d.py`
- `Simulation2D`: Main 2D simulation with reflection
  - `run()`: Execute simulation
  - `get_results()`: Return formatted results
  - `_check_and_reflect()`: Handle reflection boundary

### `src/utils.py`
- `compute_distance_to_sphere()`: Distance to sphere surface
- `is_inside_sphere()`: Check if point is inside sphere
- `reflect_point_across_line()`: 2D line reflection
- `distance_to_line_2d()`: Signed distance to line
- `is_inside_circle_2d()`: Check if point is inside circle

### `src/plotting.py`
- `plot_3d_results()`: Plot 3D simulation results with analytical comparison
- `plot_2d_comparison()`: Compare multiple 2D configurations
- `plot_2d_single()`: Plot single 2D result

## Report Generation

The generated plots include:
1. **Title and configuration information**
2. **Full parameter captions** (as required)
3. **Comparison with analytical solutions** (Task 1)
4. **Standard deviation bands** (from averaging multiple runs)
5. **Normalized responses F(t)** where applicable

**Plot 1 (Task 1-1)**: 3D diffusion with D=75 μm²/s
- Cumulative at actual scale
- Normalized cumulative F(t)
- Comparison with analytical formula

**Plot 2 (Task 1-2)**: 3D diffusion with D=200 μm²/s
- Same as Plot 1

**Plot 3 (Task 2)**: 2D diffusion with reflection - all three y-intercept configurations
- Single normalized cumulative plot
- All three configurations overlaid
- Clear demonstration of reflection effect

## Notes on Implementation

1. **Brownian Motion**: Implemented using random Gaussian displacement with σ = √(2Dt₀)

2. **Absorption Check**: Molecules are absorbed when their distance to receiver center < receiver radius

3. **Reflection Strategy**: 
   - Distance to line is computed at each step
   - If molecule crosses to wrong side, it's instantly reflected
   - Multiple reflections handled if needed (max 5 iterations)

4. **Averaging**: Multiple independent runs (typically 3) are averaged to reduce stochastic noise

5. **Numerical Precision**: 
   - Uses double precision (float64)
   - Handles erfc() complementary error function from scipy

## Troubleshooting

### Slow performance
- Reduce `num_molecules` parameter (but results may be noisier)
- Increase `delta_t` for faster simulation (but lower resolution)
- Run on a faster machine

### Memory issues
- Reduce `num_molecules`
- Check available RAM

### Import errors
- Verify all files are in `src/` directory
- Check `main.py` path configuration
- Reinstall requirements: `pip install -r requirements.txt`

## References

- Molecular Communication, point source diffusion
- Channel response in diffusion-based communication
- Composite analytical/numerical approach for validation

## Author Notes

This implementation combines:
- **Monte Carlo simulation** for stochastic molecular dynamics
- **Analytical solutions** for validation (3D case)
- **Reflection boundary conditions** for obstacle effects (2D case)

The numerical results should closely match the analytical formula in Task 1.
The Task 2 results demonstrate how reflecting boundaries enhance molecular reception by redirecting molecules toward the receiver.

---

For questions or issues, refer to the project assignment document or contact the course instructor.
