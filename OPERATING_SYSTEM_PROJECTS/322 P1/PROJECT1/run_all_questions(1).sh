#!/usr/bin/env bash
set -euo pipefail

# run_all_questions.sh
# Runs Q1, Q2, and Q3 in sequence

DEV="/dev/cmachine"
PROC="/proc/cmachine"

echo "=== Q1 START ==="
./Q1.sh 2>&1 | tail -3

echo ""
echo "=== Transitioning to Q2 ==="
cat "$DEV"
cat "$DEV"
printf 'START\x00' > "$DEV"
sleep 0.2

echo ""
echo "=== Q2 START ==="
./Q2.sh 2>&1 | tail -5

echo ""
echo "=== Transitioning to Q3 ==="
cat "$DEV"
printf 'START\x00' > "$DEV"
sleep 0.2
cat "$DEV"

echo ""
echo "=== Q3 START ==="
./Q3.sh
