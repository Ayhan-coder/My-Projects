# Molecular Diffusion Simulation - Project Execution Guide

## Quick Start

Your simulation project is now ready to run. Here's what you need to do:

### Step 1: Run the Full Simulations (30-60 minutes)

Execute the main simulation runner:

```bash
cd "c:\Users\Slayer\Desktop\cmpe 49G hw3"
python main.py
```

This will:
- Run all 5 simulations (Task 1-1, Task 1-2, Task 2-1, 2-2, 2-3)
- Average results from 3 independent runs each
- Generate plots comparing simulations with analytical solutions
- Save all results to `results/` (JSON format) and `plots/` (PNG format)

**Expected Output:**
- `plots/task1_1_results.png` - 3D with D=75
- `plots/task1_2_results.png` - 3D with D=200
- `plots/task2_comparison.png` - 2D with three reflection configurations
- `results/task1_1_results.json` - Numerical results Task 1-1
- `results/task1_2_results.json` - Numerical results Task 1-2
- `results/task2_*.json` - Results for Task 2 variants

### Step 2: Extract Key Data for Report

All results automatically include:
- Time-series data (cumulative molecules vs time)
- Standard deviations from multiple runs
- All simulation parameters in plot captions
- Comparison with analytical formula (Task 1)

### Step 3: Analyze Results

Use the analysis tool to generate statistics:

```bash
python test_utils.py --analyze results/task1_1_results.json
python test_utils.py --analyze results/task1_2_results.json
python test_utils.py --analyze results/task2_task2-1_results.json
```

## Project Structure

```
c:\Users\Slayer\Desktop\cmpe 49G hw3\
├── src/
│   ├── analytical.py         # 3D analytical formula: N_Rx(t) = ...
│   ├── simulation_3d.py       # Monte Carlo 3D diffusion
│   ├── simulation_2d.py       # Monte Carlo 2D diffusion + reflection
│   ├── utils.py               # Geometry and reflection utilities
│   └── plotting.py            # Plot generation (all captions included)
├── main.py                    # Run all simulations (use this!)
├── test_utils.py              # Quick tests and analysis
├── results/                   # JSON output files
├── plots/                     # PNG plot files
└── README.md                  # Technical documentation
```

## Key Simulation Parameters

### Task 1: 3D Diffusion (No Reflection)
- **Task 1-1**: D = 75 μm²/s
- **Task 1-2**: D = 200 μm²/s
- Common: N = 50,000 molecules, tend = 0.4 s, 3 runs averaged

### Task 2: 2D Diffusion (With Reflection)
- **Task 2-1**: y-intercept = 6 μm (reflection closest to Tx)
- **Task 2-2**: y-intercept = 9 μm 
- **Task 2-3**: y-intercept = 12 μm (reflection farthest from Tx)
- Common: N = 50,000 molecules, tend = 1.5 s, 3 runs averaged

## Understanding the Results

### Plot 1 & 2 (Task 1): 3D Validation
Each plot shows two panels:
1. **Top**: Absolute cumulative molecules with ±1 std dev band
2. **Bottom**: Normalized response F(t) = N_Rx(t)/N_Tx

**What to look for:**
- Simulation should closely match analytical formula (red dashed line)
- D=200 should reach saturation faster than D=75 (faster diffusion)
- Error bands should shrink as time increases (averaging reduces noise)

**Analytical formula**: $N_{Rx}(t) = N_{Tx} \cdot \frac{r_{Rx}}{r_{Rx}+d} \cdot \mathrm{erfc}\left(\frac{d}{\sqrt{4Dt}}\right)$

### Plot 3 (Task 2): Reflection Effect
Single plot showing all three configurations overlaid:

**What to look for:**
- y-intercept = 6 (closest): Highest absorption (reflection redirects molecules)
- y-intercept = 9: Medium absorption
- y-intercept = 12 (farthest): Lowest absorption (fewer reflections)
- All approach asymptote as t → ∞

**Interpretation**: Reflecting lines closer to Tx enhance signal by redirecting molecules.

## Report Structure

Your PDF report should include:

### 1. AI Transparency Notes (1 paragraph)
Briefly describe your use of AI in this project.

### 2. Introduction (1-2 pages)
- Molecular communication background
- Role of diffusion in MC
- Effect of obstacles/reflections
- Project objectives

### 3. System Model (2-3 pages)

**Subsection 3.1: Topology**
- Describe point source and receiver geometry
- Show coordinate system diagrams
- Define all distances and radii

**Subsection 3.2: 3D Diffusion (without reflection)**
- State the analytical formula
- Explain derivation/source
- Note parameter ranges tested

**Subsection 3.3: 2D Diffusion (with reflection)**
- Describe reflection line geometry
- Explain reflection algorithm
- State boundary conditions

### 4. Numerical Results (3-4 pages)

**Figure 1**: Task 1-1 plot (3D, D=75)
- Full caption with all parameters
- Brief analysis of fit quality

**Figure 2**: Task 1-2 plot (3D, D=200)
- Full caption with all parameters
- Comparison with Task 1-1

**Figure 3**: Task 2 comparison plot (all y-intercepts)
- Full caption with all parameters for each configuration
- Analysis of reflection effects

### 5. Comments and Observations (1-2 pages)
- Agreement between simulation and analytical (Task 1)
- Effect of D (faster diffusion → faster saturation)
- Effect of reflection geometry (Task 2)
- Any unexpected results or limitations

## Estimated Execution Timeline

- **Simulation 3D Task1-1** (3 runs): ~5-10 min
- **Simulation 3D Task1-2** (3 runs): ~5-10 min
- **Simulation 2D Task2-1-3** (9 runs): ~15-30 min
- **Data analysis & plotting**: ~5 min
- **Total runtime**: 30-60 minutes on typical machine

Speed depends on your CPU. Simulations are CPU-intensive but not GPU-dependent.

## File Names for Submission

Based on assignment requirements:
- **Student ID**: Your student ID (replace throughout)
- **Report PDF**: `<stuID_prj3_name_surname_report.pdf`
- **Code ZIP**: `<stuID_prj3_name_surname.zip` containing all source code

Example with placeholder:
- `12345_prj3_john_smith_report.pdf`
- `12345_prj3_john_smith.zip`

## Troubleshooting

### Simulation runs too slow
- Reduce `num_molecules` (but results will be noisier)
- Increase `delta_t` (but coarser time resolution)
- Results are still valid for analysis

### Memory errors
- Run on a machine with more RAM
- Reduce `num_molecules` to 25,000

### Plots look wrong
- Check that results JSON files have symmetric columns (time aligns)
- Verify analytical formula implementation, parameters

### Code errors
- Run quick tests first: `python test_utils.py --test-3d`
- Check Python version ≥3.7
- Verify scipy/numpy/matplotlib are installed

## Key Formulas for Report

### 3D Channel Response (Analytical)
$$N_{Rx}(t) = N_{Tx} \cdot \frac{r_{Rx}}{r_{Rx}+d} \cdot \mathrm{erfc}\left(\frac{d}{\sqrt{4Dt}}\right)$$

where:
- $d$ = distance from Tx emission point to Rx surface
- $r_{Rx}$ = receiver radius
- $D$ = diffusion coefficient
- $\mathrm{erfc}$ = complementary error function

### Brownian Motion (Simulation)
Each molecule undergoes random walk with:
$$\Delta \mathbf{r} \sim \mathcal{N}(0, \sigma^2 I)$$
$$\sigma = \sqrt{2D\Delta t}$$

### Line Reflection (2D)
Point $(x_0, y_0)$ reflected across line $ax + by + c = 0$:
$$\begin{pmatrix} x' \\ y' \end{pmatrix} = \begin{pmatrix} x_0 \\ y_0 \end{pmatrix} - 2 \frac{ax_0 + by_0 + c}{a^2+b^2} \begin{pmatrix} a \\ b \end{pmatrix}$$

## Next Steps

1. ✓ Code is ready and tested
2. → Run `python main.py` to generate results
3. → Extract plots for your report
4. → Write report sections based on plots
5. → Format and submit PDF + code ZIP

**Good luck!** The simulations should take 30-60 minutes to run. Use that time to draft your report introduction and system model sections.
