#!/usr/bin/env bash
set -euo pipefail

# Q2.sh
# Solves Question 2. Assumes Q1 is already completed.
# Reads transition prompts then enters Q2 write sequence.

DEV="/dev/cmachine"
PROC="/proc/cmachine"

# Ensure device exists
if [ ! -e "$DEV" ]; then
  echo "Error: $DEV not found. Run Insert.sh first." >&2
  exit 1
fi

echo "Q2 starting..."

# Read the current state (Q1 completion message)
response=$(cat "$DEV")
echo "Initial: $response"

# Skip transition messages
for skip in {1..5}; do
  if echo "$response" | grep -q 'Write "'; then
    break
  fi
  echo "Skipping transition message #$skip"
  response=$(cat "$DEV")
done

echo "Entered Q2 write sequence"
echo ""

# Now run the write sequence loop
for i in {1..50}; do
  if echo "$response" | grep -q 'Write "'; then
    # Extract quoted string
    str=$(echo "$response" | sed -n 's/.*Write "\([^"]*\)".*/\1/p')
    
    if echo "$response" | grep -q "/proc/cmachine"; then
      printf '%s\x00' "$str" > "$PROC"
      response=$(cat "$PROC")
      echo "[$i] Wrote '$str' to /proc/cmachine"
    elif echo "$response" | grep -q "/dev/cmachine"; then
      printf '%s\x00' "$str" > "$DEV"
      response=$(cat "$DEV")
      echo "[$i] Wrote '$str' to /dev/cmachine"
    fi
  elif echo "$response" | grep -qi "question 2 is done"; then
    echo ""
    echo "Q2 SOLVED!"
    break
  else
    echo "[$i] Unexpected response: $response"
    break
  fi
done

echo ""
echo "Q2.sh completed"
