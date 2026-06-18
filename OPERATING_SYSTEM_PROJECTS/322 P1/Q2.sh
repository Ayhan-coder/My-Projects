#!/bin/bash

# Q2 Solver - Write strings to dev/proc as instructed
# Run this AFTER Q1.sh completes successfully

cd ~/Downloads/PROJECT1_UPDATE2/PROJECT1

# Compile helpers if needed
[ ! -f write_dev ] && gcc -o write_dev write_dev.c
[ ! -f write_proc ] && gcc -o write_proc write_proc.c

# Send START to begin Q2
./write_dev START

for i in {1..100}; do
    # Read current instruction from /dev/cmachine
    output=$(cat /dev/cmachine 2>/dev/null)
    echo "[$i] $output"

    # Check for completion of Q2
    if echo "$output" | grep -qi "Question 2 is done\|Q2 done\|Question 3\|phase 2 completed\|congrat"; then
        echo "=== Q2 COMPLETE ==="
        break
    fi

    # Handle "Write START" prompts (transition between questions)
    if echo "$output" | grep -q "Write START"; then
        echo "    -> Sending START"
        ./write_dev START
        sleep 0.2
        continue
    fi

    # Extract the string to write (between double quotes)
    str=$(echo "$output" | sed -n 's/.*"\([^"]*\)".*/\1/p')
    
    if [ -z "$str" ]; then
        sleep 0.2
        continue
    fi

    # Determine where to write based on what the output says
    if echo "$output" | grep -q "/proc/cmachine"; then
        echo "    -> Writing '$str' to /proc/cmachine"
        ./write_proc "$str"
    elif echo "$output" | grep -q "/dev/cmachine"; then
        echo "    -> Writing '$str' to /dev/cmachine"
        ./write_dev "$str"
    fi
    
    sleep 0.1
done
