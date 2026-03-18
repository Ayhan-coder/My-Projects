#!/bin/bash

# Q3 Solver - Execute 16 sleep_ten processes within 15 seconds
# They must run in parallel (background) to complete in time

cd ~/Downloads/PROJECT1_UPDATE2/PROJECT1

# Compile helpers if needed
[ ! -f write_dev ] && gcc -o write_dev write_dev.c

# Send START to begin Q3
./write_dev START &

echo "Launching 16 sleep_ten processes in parallel..."

# Launch all 16 processes in background simultaneously
for i in {1..16}; do
    ./sleep_ten &
done

echo "All 16 processes launched. Waiting for completion..."

# Wait for all background processes to finish
wait

echo "All processes completed. Checking result..."
cat /dev/cmachine
