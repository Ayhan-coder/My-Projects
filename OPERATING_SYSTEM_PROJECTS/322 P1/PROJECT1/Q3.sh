#!/usr/bin/env bash
set -euo pipefail

# Q3.sh
# Solves Question 3: Execute 16 "sleep_ten" processes in 15 seconds.

DEV="/dev/cmachine"
SLEEP_TEN="./amd64/sleep_ten"

# Ensure device exists
if [ ! -e "$DEV" ]; then
  echo "Error: $DEV not found. Run Insert.sh first." >&2
  exit 1
fi

if [ ! -x "$SLEEP_TEN" ]; then
  echo "Error: $SLEEP_TEN not found or not executable." >&2
  exit 1
fi

# Send START to begin Q3 with null terminator
printf 'START\x00' > "$DEV" &

# Wait a tiny bit to ensure kernel registers the start time
sleep 0.1

echo "Q3 started: Running 16 sleep_ten processes in parallel (target: complete in 10-15 seconds)..."

# Start 16 sleep_ten processes immediately in background
# They each sleep for 10 seconds, so running in parallel should complete in ~10 seconds total
START_TIME=$(date +%s)
for i in {1..16}; do
  "$SLEEP_TEN" >/dev/null 2>&1 &
  # Add a tiny stagger to avoid race conditions if any
  sleep 0.01
done

echo "All 16 processes started in background. Waiting for completion..."

# Wait for all background jobs to complete
wait

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo "All 16 processes completed in $ELAPSED seconds!"

# Wait a moment then check device for result
sleep 1
response=$(cat "$DEV")
echo ""
echo "Response: $response"

if echo "$response" | grep -qi "question 3 is done\|success"; then
  echo "✓ Q3 SOLVED!"
fi

echo ""
echo "Q3.sh completed"
