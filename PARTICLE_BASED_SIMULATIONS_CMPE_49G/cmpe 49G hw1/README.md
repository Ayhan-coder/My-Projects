# CmpE 49G - Project 1: Monte Carlo Simulation for Buffon's Needle

**Ali Ayhan Günder — 2021400219**  
CmpE 49G · Spring 2026

## Quick Start

```bash
pip install -r requirements.txt
python buffon_simulation.py          # runs both problems (~2-3 min)
```

Plots are saved to `plots/`. Use `--problem_id 1` or `--problem_id 2` to run a single problem, or pass `--L`, `--D`, `--N`, `--seed` for a custom single run. Run `python buffon_simulation.py --help` for details.

## Overview

Monte Carlo estimation of the crossing probability $P = 2L/(\pi D)$ for:

1. **Classic Buffon (parallel lines)** — needle length $L$, line spacing $D$
2. **Concentric circles variant** — circles with radii $kD$, same analytical $P$

Each geometry is tested with $(L,D) \in \{(1,2),(2,3),(3,5)\}$ and $N \in \{10^2, 10^3, 10^4, 10^5, 10^6\}$, seed 42.

## Output

| File | Description |
|------|-------------|
| `plots/problem{1,2}_convergence.png` | $\hat P$ vs $\log_{10} N$ |
| `plots/problem{1,2}_error.png` | Absolute error vs $N$ (log-log) |

## Files

```
buffon_simulation.py   Main simulation script
Report.pdf             PDF report
requirements.txt       Python dependencies (NumPy, Matplotlib)
plots/                 Generated figures
```

