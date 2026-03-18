CMPE 49T — HW3 (Diagnosis Model Evaluation)

This folder contains code, notebooks, and a LaTeX report for CMPE 49T Homework 3.

Files:
- `00_generate_predictions.ipynb` — Notebook to prepare dataset and train logistic regression.
- `hw3.py` — End-to-end Python script that performs training and evaluation (saves figures/arrays).
- `hw3_report.tex` — LaTeX source for the final report (includes figures saved by `hw3.py`).
- `weights_000000.npy`, `bias_000000.npy`, `X_test_000000.npy`, `y_test_000000.npy` — Saved outputs (student ID=000000 for this workspace; replace with your own seed and re-run).
- Figures: `training_loss.png`, `roc_curve.png`, `pr_curve.png`, `total_cost.png`.

Setup & Reproducibility
------------------------
1. Install Python packages (virtual environment recommended):

```powershell
python -m venv venv; .\venv\Scripts\Activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

2. Generate model outputs (train + evaluation):

```powershell
# Optional: update student_id inside hw3.py and in the notebook to your own ID as a string
python .\hw3.py
```

The script will save produced figures and arrays in `outdir` path used in the script. If you want outputs in the working directory, update the `outdir` variable accordingly.

3. Compile the LaTeX report to PDF (Windows PowerShell). You must have a LaTeX engine installed (MiKTeX or TeX Live). Then run:

```powershell
pdflatex hw3_report.tex
pdflatex hw3_report.tex  # run twice for table-of-contents
```

Optional build script (PowerShell) for convenience: `build_report.ps1`.

Notes & Tips
-----------
- Replace the `student_id` in `hw3.py` and `00_generate_predictions.ipynb` with your actual student number.
- Ensure `hw3.py` is run before compiling the report so that the latest figures are available for inclusion.
- If LaTeX compilation fails due to missing packages, install the missing package via your LaTeX manager (MiKTeX's package manager or TeX Live).
