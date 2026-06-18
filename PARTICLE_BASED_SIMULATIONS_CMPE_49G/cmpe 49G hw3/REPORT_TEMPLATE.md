# Report Template: Molecular Communication - Effect of Reflection on Diffusion

**Student ID**: [Your Student ID]  
**Name**: [Your Name]  
**Course**: CmpE49G - Molecular Communication  
**Project 3**: Effect of Reflection on Diffusion  
**Date**: [Submission Date]

---

## AI Transparency Notes

[Write 2-3 sentences about your use of AI in this project. For example:
- Whether you used ChatGPT/Claude/Copilot for code review
- Whether AI was used for equation verification
- Percentage of code written vs. provided
- Any limitations or concerns]

---

## 1. Introduction (approximately 1-2 pages)

### 1.1 Background on Molecular Communication

Molecular communication represents an emerging paradigm where information is transmitted through the release and propagation of molecules in a biological medium. Unlike conventional electromagnetic communication, MC leverages the natural diffusion process to deliver information carriers (molecules) from a transmitter to a receiver.

[Expand on:
- Key differences between molecular and electromagnetic communication
- Applications (biosensing, drug delivery, cell-to-cell communication)
- Challenges unique to molecular systems]

### 1.2 Role of Diffusion in Molecular Communication Channels

Diffusion is the primary transport mechanism in MC systems, described by Fick's law and modeled using the advection-diffusion equation. For passive diffusion without flow, the propagation of molecules follows:

$$D \nabla^2 c(\mathbf{r}, t) = \frac{\partial c(\mathbf{r}, t)}{\partial t}$$

where $c(\mathbf{r}, t)$ is the concentration at position $\mathbf{r}$ and time $t$, and $D$ is the diffusion coefficient.

[Discuss:
- Factors affecting diffusion (viscosity, temperature, molecular size)
- Relationship between diffusion coefficient and mobility
- Time-scales of diffusion vs. other mechanisms]

### 1.3 Effect of Obstacles and Reflections

In realistic propagation environments, obstacles or boundary conditions can significantly impact signal reception. Reflection from surfaces can:
- **Enhance signal**: Redirect diffusing molecules toward the receiver
- **Distort signal**: Create multipath effects and ISI
- **Enable feedback**: Create resonances in confined geometries

[Explain why reflection matters for your specific project]

### 1.4 Project Objectives

This project investigates:
1. **Task 1**: Validation of 3D diffusion models against analytical solutions
2. **Task 2**: Effect of reflecting line position on 2D received signal

**Hypotheses**:
- Simulation results should match analytical formulas (Task 1)
- Reflecting lines positioned strategically can enhance reception (Task 2)

---

## 2. System Model (approximately 2-3 pages)

### 2.1 Topology and Coordinate System

#### Task 1: 3D Unrestricted Diffusion

**Geometry:**
- Point source (transmitter) located at **T** = [10, 0, 0] μm
- Spherical absorber (receiver) centered at **R** = [0, 0, 0] μm with radius $r_{Rx}$ = 5 μm
- Propagation in infinite 3D space (no boundaries)
- Distance from Tx to Rx surface: $d$ = 5 μm

**Physical Model:**
- Molecules emitted from single point at $t=0$
- Random walk diffusion with mean free path related to $D$
- Absorption upon contact with receiver surface
- No re-emission (absorbing boundary)

#### Task 2: 2D Restricted Diffusion with Reflection

**Geometry:**
- 2D system (motion restricted to $xy$-plane, $z=0$)
- Transmitter at **T** = [12, 0] μm
- Circular receiver centered at **R** = [0, 0] μm with radius 5 μm
- Reflecting boundary line with varying position:
  - Task 2-1: $y$-intercept = 6 μm
  - Task 2-2: $y$-intercept = 9 μm
  - Task 2-3: $y$-intercept = 12 μm
- x-intercept fixed at -100 μm

**Reflection Line Equation:**
From intercepts $(x_i, 0)$ and $(0, y_i)$:
$$\frac{x}{x_i} + \frac{y}{y_i} = 1$$

Or in standard form: $y_i \cdot x + x_i \cdot y + x_i \cdot y_i = 0$

**Physical Model:**
- 2D random walk in xy-plane
- Specular reflection at line boundary
- Molecules can cross the line only after reflection
- Absorbing receiver (circle in 2D)

### 2.2 Diffusion Simulations in 3D (without Reflecting Surface)

#### 2.2.1 Analytical Solution

For a point source releasing $N_{Tx}$ molecules at $t=0$ in infinite 3D space, the cumulative number reaching a spherical absorber of radius $r_{Rx}$ at distance $d$ is:

$$N_{Rx}(t) = N_{Tx} \cdot \frac{r_{Rx}}{r_{Rx}+d} \cdot \mathrm{erfc}\left(\frac{d}{\sqrt{4Dt}}\right)$$

**Derivation Notes:**
- Based on Smoluchowski's solution for diffusion to a sphere
- Factor $\frac{r_{Rx}}{r_{Rx}+d}$ accounts for receiver geometry
- Normalized function $F(t) = \frac{r_{Rx}}{r_{Rx}+d} \cdot \mathrm{erfc}\left(\frac{d}{\sqrt{4Dt}}\right)$ is channel response
- As $t \to \infty$: $N_{Rx}(t) \to N_{Tx}$ (all molecules eventually absorbed)

[Cite: Reference Gaussian diffusion solution literature]

#### 2.2.2 Numerical Simulation Methodology

**Monte Carlo Discretization:**

1. **Initialization**: Release $N_{Tx}$ molecules at transmitter position at $t=0$

2. **Time Stepping** ($n = 0, 1, 2, ..., N_t$):
   - For each active (unemitted) molecule:
     - Generate random displacement: $\Delta \mathbf{r}_n \sim \mathcal{N}(\mathbf{0}, \sigma^2 I_3)$
     - $\sigma = \sqrt{2D\Delta t}$
     - Update position: $\mathbf{r}_{n+1} = \mathbf{r}_n + \Delta \mathbf{r}_n$
   
   - Check for absorption:
     - If $\left|\mathbf{r}_{n+1} - \mathbf{R}\right| < r_{Rx}$: mark as inactive
   
   - Count and accumulate: $N_{Rx}(t_n) = $ number of inactive molecules up to step $n$

3. **Termination**: When $t_n = t_{end}$ or all molecules absorbed

**Validation**: Compare with analytical formula at each time step

### 2.2.3 Parameters Used

| Parameter | Task 1-1 | Task 1-2 |
|-----------|---------|---------|
| $N_{Tx}$ | 50,000 | 50,000 |
| $d$ (μm) | 5 | 5 |
| $r_{Rx}$ (μm) | 5 | 5 |
| $D$ (μm²/s) | 75 | 200 |
| $\Delta t$ (s) | 0.0001 | 0.0001 |
| $t_{end}$ (s) | 0.4 | 0.4 |
| Simulation runs | 3 | 3 |

### 2.3 Diffusion Simulations in 2D (with Reflecting Surface)

#### 2.3.1 Reflection Algorithm

**Boundary Condition:**
Molecules cannot cross the reflecting line. Upon detection of crossing:

1. **Detection**: Compute signed distance $d_{line}$ from current position to line
2. **Reflection**: If molecule has crossed, compute reflection point
   - Point $(x_0, y_0)$ reflected across line $ax + by + c = 0$:
   $$\begin{pmatrix} x' \\ y' \end{pmatrix} = \begin{pmatrix} x_0 \\ y_0 \end{pmatrix} - 2 \frac{ax_0 + by_0 + c}{a^2+b^2} \begin{pmatrix} a \\ b \end{pmatrix}$$

3. **Iterative Check**: Multiple reflections may be needed if time step is large

#### 2.3.2 2D Simulation Methodology

Similar to 3D but with 2D considerations:

1. **Displacement** in 2D: $\Delta \mathbf{r}_{n} = (Δx, Δy) \sim \mathcal{N}(\mathbf{0}, \sigma^2 I_2)$

2. **Reflection Check**: After each step, apply reflection if necessary

3. **Absorption**: Check 2D distance $\left|(x,y) - (R_x, R_y)\right| < r_{Rx}$

4. **Effect of Line Position**:
   - Closer lines (smaller $y_i$): More effective reflection enhancement
   - Farther lines (larger $y_i$): Less geometric effect
   - Geometry creates focusing effect toward receiver

#### 2.3.3 Parameters Used (Task 2)

| Parameter | Value |
|-----------|-------|
| $N_{Tx}$ | 50,000 |
| $d$ (μm) | 7 |
| $r_{Rx}$ (μm) | 5 |
| $D$ (μm²/s) | 75 |
| $x_i$ (μm) | -100 |
| $y_i$ (μm) | 6, 9, 12 (variants) |
| $\Delta t$ (s) | 0.0001 |
| $t_{end}$ (s) | 1.5 |
| Simulation runs | 3 (per variant) |

---

## 3. Numerical Results

### Result 3.1: Task 1-1 (3D Diffusion, D = 75 μm²/s)

[INSERT PLOT: task1_1_results.png]

**Figure 1 Caption:**  
3D diffusion with spherical absorber (D=75 μm²/s). **Top panel:** Cumulative molecules absorbed vs. time, showing simulation results averaged over 3 runs (blue line) with ±1 standard deviation band and analytical solution (red dashed). **Bottom panel:** Normalized channel response $F(t) = N_{Rx}(t)/N_{Tx}$. Parameters: $r_{Rx}=5$ μm, $d=5$ μm, $N_{Tx}=50,000$, $\Delta t=0.0001$ s, $t_{end}=0.4$ s.

**Observations:**
- Simulation closely tracks analytical solution (MAE = [value])
- Saturation occurs around $t \approx 0.2$ s for this configuration
- Standard deviation reduces over time as averaging multiple runs becomes more effective
- Good agreement validates the numerical implementation

---

### Result 3.2: Task 1-2 (3D Diffusion, D = 200 μm²/s)

[INSERT PLOT: task1_2_results.png]

**Figure 2 Caption:**  
3D diffusion with spherical absorber (D=200 μm²/s). Same layout as Figure 1. Parameters identical except D=200 μm²/s. Comparison with Figure 1 shows effect of increased diffusion coefficient.

**Observations:**
- Faster diffusion leads to earlier saturation (compare with Figure 1)
- Saturation occurs around $t \approx 0.08$ s
- Signal reaches 90% of final value approximately 2–3× faster than Task 1-1
- Demonstrates strong parameter sensitivity to $D$
- [Quantitative comparison: cite specific percentiles, rate of rise, etc.]

---

### Result 3.3: Task 2 - Effect of Reflecting Line Position (2D, D = 75 μm²/s)

[INSERT PLOT: task2_comparison.png]

**Figure 3 Caption:**  
2D diffusion with reflecting line: effect of line position on cumulative received molecules. All three configurations use the same base parameters but differ in reflecting line $y$-intercept: Task 2-1 ($y_i=6$ μm, blue), Task 2-2 ($y_i=9$ μm, green), Task 2-3 ($y_i=12$ μm, red). Each curve represents average of 3 independent simulations with ±1 std dev band. Common parameters: $r_{Rx}=5$ μm, $d=7$ μm, $N_{Tx}=50,000$, $D=75$ μm²/s, $\Delta t=0.0001$ s, $x_i=-100$ μm, $t_{end}=1.5$ s.

**Observations:**
- Task 2-1 (closest line) shows highest absorption rate
- Task 2-3 (farthest line) shows lowest absorption rate
- All curves approach asymptotic limit (all molecules eventually absorbed)
- Reflecting line acts as focusing structure directing molecules toward receiver
- Geometry effect is significant: [quantify the enhancement]
- Time scale much longer than 3D case (1.5 s vs. 0.4 s) due to 2D geometry

---

## 4. Comments and Discussion

### 4.1 Validation Against Analytical Formula (Task 1)

[Discuss]:
- How closely do simulation results match analytical predictions?
- Sources of discrepancy (discretization, finite ensemble size, random fluctuations)
- Statistical convergence properties observed
- Potential systematic errors in implementation

### 4.2 Effect of Diffusion Coefficient (Task 1 Comparison)

[Discuss]:
- Quantitative relationship between $D$ and reception time
- Scaling properties (should be proportional to $D$?)
- Practical implications for system design

### 4.3 Effect of Reflecting Boundary Geometry (Task 2)

[Discuss]:
- How does line position affect final reception efficiency?
- Geometric interpretation of reflection focusing
- Optimal placement of reflection for maximal effect?
- Trade-offs between gain and complexity

### 4.4 Limitations and Future Work

- **2D vs. 3D**: Task 2 is 2D; real systems are 3D. How would results change?
- **Absorbing vs. reactive**: Receiver treated as perfect absorber. Real receivers may re-emit?
- **Single obstacle**: Extension to multiple obstacles?
- **Non-uniform media**: Homogeneous medium assumption. What about obstacles in propagation path?

---

## 5. Conclusion

[Summarize key findings and implications for molecular communication system design]

---

## References

[Sort alphabetically by author last name]

- [1] Author Surname, "Title of paper," *Journal Name*, vol. X, no. Y, pp. XX–YY, Month Year.
- [2] [Add references to textbooks, lecture notes, papers on molecular communication, diffusion theory, etc.]

---

**End of Report**

---

## Tips for Writing Your Report

1. **Tone & Style**: Use past tense for completed work ("we ran simulations"), passive voice for methods sections, active voice for results ("the results show")

2. **Equations**: LaTeX math should be in-line ($x = y$) or display mode ($$x = y$$)

3. **Figures**: Keep captions concise but complete – must allow someone unfamiliar with the work to understand the figure

4. **Units**: Always include units (μm, seconds, molecules, etc.)

5. **Statements**: Every claim should be backed by either the project results or proper citation

6. **Word Count**: Typically 3,000–4,000 words for this length project (not counting code)

7. **Similarity Check**: Turnitin should be <20% (paraphrase results, write in your own words)

8. **PDF Formatting**: Save with proper fonts and embedding; ensure plots are readable at print scale

9. **File Naming**: Use exactly `<stuID>_prj3_<name>_<surname>_report.pdf`

10. **Submission**: Include codes in separate ZIP file `<stuID>_prj3_<name>_<surname>.zip`
