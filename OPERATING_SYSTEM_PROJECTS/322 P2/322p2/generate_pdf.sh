#!/bin/bash

# PDF Generation Instructions for CMPE322 Project 2 Report

echo "════════════════════════════════════════════════════════════"
echo "  REPORT PDF GENERATION OPTIONS"
echo "════════════════════════════════════════════════════════════"
echo ""

cd /home/vboxuser/Downloads/322p2

echo "Option 1: Install LaTeX and compile"
echo "─────────────────────────────────────"
echo "If you're root or have sudo:"
echo "  apt-get install texlive-latex-base texlive-latex-extra"
echo "  pdflatex report.tex"
echo ""

echo "Option 2: Use online LaTeX compiler"
echo "────────────────────────────────────"
echo "1. Go to https://www.overleaf.com/"
echo "2. Create a new project (blank)"
echo "3. Upload report.tex and gpt_queries.tex"
echo "4. Click 'Recompile'"
echo "5. Download report.pdf"
echo ""

echo "Option 3: Use LaTeX.Online"
echo "──────────────────────────"
echo "Visit: https://latexonline.cc/"
echo "Upload: report.tex and gpt_queries.tex"
echo "Download the generated PDF"
echo ""

echo "Option 4: Check if pdflatex is already available"
echo "─────────────────────────────────────────────────"
if command -v pdflatex &> /dev/null; then
    echo "✓ pdflatex is installed!"
    echo "Generating PDF..."
    pdflatex report.tex
    if [ -f "report.pdf" ]; then
        echo "✓ report.pdf generated successfully!"
        pdfinfo report.pdf 2>/dev/null || echo "PDF created: $(ls -lh report.pdf)"
    fi
else
    echo "✗ pdflatex not found"
fi
echo ""

echo "Files needed for LaTeX compilation:"
echo "  - report.tex (main document)"
echo "  - gpt_queries.tex (GPT query log - auto-included)"
echo ""

echo "════════════════════════════════════════════════════════════"
