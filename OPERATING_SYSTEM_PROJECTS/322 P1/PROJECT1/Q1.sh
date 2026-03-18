#!/usr/bin/env bash
set -euo pipefail

# Q1.sh
# Solves Question 1 by sending START command and following the alternating
# read sequence between /dev/cmachine and /proc/cmachine until completion.

DEV="/dev/cmachine"
PROC="/proc/cmachine"

# Ensure device exists
if [ ! -e "$DEV" ]; then
  echo "Error: $DEV not found. Run Insert.sh first." >&2
  exit 1
fi

# Send START command (with null terminator) to begin Q1
printf 'START\x00' > "$DEV"

echo "Q1 started. Following the read sequence..."

# Read the initial instruction
response=$(cat "$DEV")
echo "Initial: $response"

# Track which file to read next based on the response
max_iterations=50
count=0

while [ $count -lt $max_iterations ]; do
  count=$((count + 1))
  
  # Check response to determine next action
  if echo "$response" | grep -q "next file you should read is: /dev/cmachine"; then
    response=$(cat "$DEV")
    echo "[$count] Read $DEV: $response"
  elif echo "$response" | grep -q "next file you should read is: /proc/cmachine"; then
    response=$(cat "$PROC")
    echo "[$count] Read $PROC: $response"
  elif echo "$response" | grep -q "Wrong choice"; then
    echo "[$count] Wrong choice detected. Restarting..."
    printf 'START\x00' > "$DEV"
    response=$(cat "$DEV")
    echo "[$count] Restarted: $response"
  elif echo "$response" | grep -q "Start the problem"; then
    # Need to read from proc first
    response=$(cat "$PROC")
    echo "[$count] Read $PROC: $response"
  elif echo "$response" | grep -qi "completed\|finished\|congratulations\|done\|solved\|hash\|END"; then
    echo "[$count] Q1 SOLVED!"
    echo "Final response: $response"
    break
  else
    # Unknown response - print and try reading from dev
    echo "[$count] Unknown response: $response"
    echo "[$count] Trying to continue by reading $DEV..."
    response=$(cat "$DEV")
  fi
done

if [ $count -ge $max_iterations ]; then
  echo "Reached max iterations ($max_iterations). Last response: $response"
fi

echo ""
echo "=== Kernel log (last 30 lines with MACHINE) ==="
sudo dmesg | grep -i "MACHINE\|Q1\|question\|hash" | tail -30 || true

echo ""
echo "Q1.sh completed"
