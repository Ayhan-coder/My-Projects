#!/usr/bin/env bash
set -euo pipefail

# Q4.sh
# Solves Question 4 using the identified syscall numbers.

DEV="/dev/cmachine"

# Ensure device exists
if [ ! -e "$DEV" ]; then
  echo "Error: $DEV not found. Run Insert.sh first." >&2
  exit 1
fi

# Send START to begin Q4
printf 'START\x00' > "$DEV"
echo "Q4 started. Sending known syscall numbers..."

# The correct syscall numbers identified
SYSCALLS="3 9 11 14 56 257 258"

for num in $SYSCALLS; do
  echo "Writing syscall number: $num"
  printf '%s\x00' "$num" > "$DEV"
  
  response=$(cat "$DEV")
  echo "Response: $response"
  
  if echo "$response" | grep -qi "success\|congratulations\|hash"; then
    echo "Q4 SOLVED!"
    echo "Final message: $response"
    
    # Check kernel log for the hash
    echo "Checking kernel log for hash..."
    # The hash is a long string of uppercase letters, likely without spaces
    sudo dmesg | tail -20 | grep -E "[A-Z]{20,}" | tail -1
    exit 0
  fi
done

echo "Finished sending numbers."
echo "Final device message: $(cat "$DEV")"
