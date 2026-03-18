# CMPE 49T — HW 1 Environment Setup

This repo contains a minimal, clean environment to complete **Part II** (NumPy-only) and organize **Part I** (manual) work.

## 1) Create a virtual environment


**Windows (PowerShell)**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2) Launch Jupyter
```bash
jupyter notebook
```
Then open `hw1_cnn_manual.ipynb`.

## 3) Files
- `hw1_cnn_manual.ipynb` — Notebook template with function stubs and the given matrices.
- `hw1_cnn_manual.py` — Python script with the same stubs if you prefer .py.
- `requirements.txt` — Minimal deps (NumPy + Jupyter).

## 4) Tips
- Do **not** use high-level DL libs (torch/keras). NumPy only.
- After each major stage, print the matrix and its shape.
- Keep floating results to ~3 decimals where needed.
