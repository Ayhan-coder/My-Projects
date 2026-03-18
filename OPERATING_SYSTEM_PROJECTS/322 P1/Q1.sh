#!/bin/bash

# Q1 Solver - Uses write_dev C program for reliable writes

cd ~/Downloads/PROJECT1_UPDATE2/PROJECT1

# Compile write_dev if not exists
if [ ! -f write_dev ]; then
    gcc -o write_dev write_dev.c
fi

# Send START using the C program
echo "Sending START..."
./write_dev START

# Follow the /dev vs /proc trail
current="/proc/cmachine"  # First instruction says read proc

for i in {1..50}; do
    output=$(cat "$current" 2>/dev/null)
    echo "[$i] $current: $output"

    # Check for completion
    if echo "$output" | grep -qi "hash\|complete\|congrat\|Question 2\|Q1 Done"; then
        echo "=== Q1 COMPLETE ==="
        break
    fi

    # Follow the instruction - read what it says
    if echo "$output" | grep -q "/proc/cmachine"; then
        current="/proc/cmachine"
    elif echo "$output" | grep -q "/dev/cmachine"; then
        current="/dev/cmachine"
    fi
    
    sleep 0.1
done