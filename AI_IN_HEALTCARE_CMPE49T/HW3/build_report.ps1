# PowerShell build script to compile the LaTeX report
# Run from project directory
# Usage: .\build_report.ps1

# Check for pdflatex
if (-not (Get-Command pdflatex -ErrorAction SilentlyContinue)) {
    Write-Host "pdflatex not found in PATH. Install MiKTeX or TeX Live and add pdflatex to PATH." -ForegroundColor Yellow
    exit 1
}

pdflatex hw3_report.tex
pdflatex hw3_report.tex
Write-Host "hw3_report.pdf generated." -ForegroundColor Green
