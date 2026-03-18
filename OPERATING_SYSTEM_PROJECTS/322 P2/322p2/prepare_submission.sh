#!/bin/bash

# CMPE322 Project 2 Submission Preparation Script

STUDENT_ID="XXXXXXXXX"  # Replace with your actual student ID

echo "CMPE322 Project 2 - Submission Preparation"
echo "=========================================="
echo ""

# Check if student ID was updated
if [ "$STUDENT_ID" = "XXXXXXXXX" ]; then
    echo "ERROR: Please edit this script and set your STUDENT_ID"
    exit 1
fi

echo "Student ID: $STUDENT_ID"
echo ""

# Step 1: Compile the shared object
echo "Step 1: Compiling hash_parallelization.so..."
gcc -shared -fPIC -pthread -o hash_parallelization.so hash_parallelization.c -lrt

if [ $? -ne 0 ]; then
    echo "ERROR: Compilation failed!"
    exit 1
fi
echo "✓ Compilation successful"
echo ""

# Step 2: Check required files
echo "Step 2: Checking required files..."
MISSING=0

if [ ! -f "hash_parallelization.so" ]; then
    echo "✗ hash_parallelization.so is missing"
    MISSING=1
else
    echo "✓ hash_parallelization.so found"
fi

if [ ! -f "hash_parallelization.c" ]; then
    echo "✗ hash_parallelization.c is missing"
    MISSING=1
else
    echo "✓ hash_parallelization.c found"
fi

if [ ! -f "report.pdf" ]; then
    echo "✗ report.pdf is missing"
    echo "  NOTE: You need to compile report.tex to create report.pdf"
    echo "  Run: pdflatex report.tex"
    MISSING=1
else
    echo "✓ report.pdf found"
fi

if [ $MISSING -eq 1 ]; then
    echo ""
    echo "ERROR: Some required files are missing!"
    exit 1
fi
echo ""

# Step 3: Create submission zip
echo "Step 3: Creating submission zip..."
ZIP_NAME="${STUDENT_ID}.zip"

# Remove old zip if exists
if [ -f "$ZIP_NAME" ]; then
    rm "$ZIP_NAME"
fi

# Create zip with only required files
zip "$ZIP_NAME" hash_parallelization.so hash_parallelization.c report.pdf

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create zip file!"
    exit 1
fi

echo "✓ Created $ZIP_NAME"
echo ""

# Step 4: Verify zip contents
echo "Step 4: Verifying zip contents..."
unzip -l "$ZIP_NAME"
echo ""

# Final check
echo "=========================================="
echo "Submission preparation complete!"
echo ""
echo "Your submission file: $ZIP_NAME"
echo ""
echo "IMPORTANT: Verify that:"
echo "1. The zip contains exactly 3 files (no folders)"
echo "2. Files are directly in the zip root"
echo "3. hash_parallelization.c has no test code"
echo "4. report.pdf is maximum 2 pages"
echo "=========================================="
