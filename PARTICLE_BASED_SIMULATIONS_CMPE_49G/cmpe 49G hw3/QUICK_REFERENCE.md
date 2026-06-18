# 🚀 QUICK REFERENCE CARD

## Essential Commands

### Run Everything
```bash
python main.py
```
**Takes**: 30-60 minutes | **Generates**: 3 plots + 5 JSON files

### Quick Validation (Before Full Run)
```bash
python test_utils.py --test-3d    # 30 sec
python test_utils.py --test-2d    # 45 sec
```
**Verifies**: Code works correctly before committing to hour-long run

### Analyze After Completion
```bash
python test_utils.py --analyze results/task1_1_results.json
python test_utils.py --compare results/task1_1_results.json results/task1_2_results.json
```

---

## 📁 Key Files & Locations

### FOR YOUR REPORT
| What | Where | Usage |
|-----|-------|-------|
| Task 1-1 plot | `plots/task1_1_results.png` | Copy to report as Figure 1 |
| Task 1-2 plot | `plots/task1_2_results.png` | Copy to report as Figure 2 |
| Task 2 plot | `plots/task2_comparison.png` | Copy to report as Figure 3 |

### FOR WRITING
| What | Where | Usage |
|-----|-------|-------|
| Report template | `REPORT_TEMPLATE.md` | Fill in sections, then convert to PDF |
| Execution guide | `EXECUTION_GUIDE.md` | Reference while running |
| Data for numbers | `results/*.json` | Citation of specific values |

### FOR CODING
| What | Where | Usage |
|------|-------|-------|
| 3D simulation | `src/simulation_3d.py` | Read to understand implementation |
| 2D simulation | `src/simulation_2d.py` | Read to understand reflection |
| Analytical | `src/analytical.py` | 3D formula implementation |
| Utils | `src/utils.py` | Geometry and reflection math |
| Plotting | `src/plotting.py` | How plots are generated |

---

## 📊 What You'll Get

### After Running `python main.py`:

**Plots folder** (`plots/`) will contain:
```
task1_1_results.png       ← 3D, D=75, simulation vs analytical
task1_2_results.png       ← 3D, D=200, comparison
task2_comparison.png      ← 2D, all three reflection configs overlaid
```

**Results folder** (`results/`) will contain:
```
task1_1_results.json      ← Time series + parameters
task1_2_results.json      ← Time series + parameters  
task2_task2-1_results.json ← Time series + parameters
task2_task2-2_results.json ← Time series + parameters
task2_task2-3_results.json ← Time series + parameters
```

---

## ⏰ Timeline

| Task | Duration | Start | Expected End |
|------|----------|-------|--------------|
| Run quick test | 1 min | Now | Now+1min |
| Run full sims | 45 min | 10:00 | 10:45 |
| Analyze plots | 10 min | 10:45 | 10:55 |
| Write report | 2-3 hrs | 11:00 | 2:00-3:00 PM |
| **TOTAL** | **3-4 hrs** | | |

---

## 🎯 Before Submission

- [ ] Run `python main.py` successfully
- [ ] Verify 3 PNG files in `plots/` folder
- [ ] Verify 5 JSON files in `results/` folder
- [ ] Use REPORT_TEMPLATE.md to write report
- [ ] Insert 3 plots into report (Figures 1-3)
- [ ] Convert to PDF: `<stuID>_prj3_name_surname_report.pdf`
- [ ] Create ZIP with code: `<stuID>_prj3_name_surname.zip`
- [ ] Submit PDF via course portal
- [ ] Email code ZIP to instructor

---

## 📌 Plot Captions (Already Included)

Every plot automatically includes:
✓ Parameter values (rx_center, rx_r, tx_pt, D, etc.)
✓ Time settings (Δt, tend)
✓ Molecule count (50,000)
✓ Configuration-specific values (y-intercepts for Task 2)

**No need to manually add** - they're in the PNG files!

---

## 💡 What Each Task Shows

**Task 1-1 (D=75)**
- Slower diffusion
- Saturation around 0.2 seconds
- Good match with red theoretical curve

**Task 1-2 (D=200)**
- Faster diffusion (2.7× larger D)
- Saturation around 0.08 seconds (much earlier!)
- Demonstrates D sensitivity

**Task 2-1,2,3 (Reflection)**
- Task 2-1 (green, y=6): Highest absorption
- Task 2-2 (blue, y=9): Medium absorption
- Task 2-3 (red, y=12): Lowest absorption
- Shows reflection geometry effects

---

## 🔧 If You Want to Modify Things

### Change number of molecules:
Edit `main.py`, find `'num_molecules': 50000`, change to `25000`

### Change diffusion coefficient:
Edit `main.py`, find `'D_inMicroMeterSqrPerSecond': 75`

### Change simulation time:
Edit `main.py`, find `'tend': 0.4` or `'tend': 1.5`

### Use only 1 run instead of 3 (faster):
In `main.py`, change `run_simulation_multiple_times(..., num_runs=3)` to `num_runs=1`

**Note**: More runs = smoother curves but longer execution time

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Code won't run | Run `python test_utils.py --test-3d` to verify setup |
| Too slow | Reduce `num_molecules` to 25000 in main.py |
| Plots missing | Check `plots/` folder exists |
| Import errors | Reinstall: `pip install -r requirements.txt` |
| Wrong file format | Plots are PNG, convert to your format if needed |

---

## 📧 Submission Details

**PDF Report:**
```
<stuID>_prj3_<firstname>_<lastname>_report.pdf
```
Send via: Course portal (check assignment page)

**Code ZIP:**
```
<stuID>_prj3_<firstname>_<lastname>.zip
```
Send via: Email to instructor  
Subject: "CMPE49G Project 3 - Codes - <stuID>"

---

## ✅ Pre-Run Checklist

- [ ] Python 3.7+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Virtual environment activated
- [ ] You understand you'll wait 30-60 minutes
- [ ] You have report template ready
- [ ] You're in the project directory

**When ready**, type:
```bash
python main.py
```

---

## 📱 One-Page Summary

| Component | Detail |
|-----------|--------|
| **What** | Molecular diffusion simulations (3D + 2D) |
| **Required** | Run `python main.py` |
| **Time** | 30-60 minutes |
| **Gets you** | 3 plots + data for report |
| **Then** | Write report using template |
| **Finally** | Submit PDF + ZIP |

---

**You're ready!** → Execute `python main.py`
