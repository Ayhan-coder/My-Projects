#!/bin/bash

# Q4 Solver - Brute force syscall numbers

cd ~/Downloads/PROJECT1_UPDATE2/PROJECT1

# Compile helpers if needed
[ ! -f write_dev ] && gcc -o write_dev write_dev.c

# Send START to begin Q4
./write_dev START
sleep 0.3

echo "Brute forcing syscall numbers..."

for num in {0..450}; do
    # Write the number
    ./write_dev "$num" 2>/dev/null
    
    # Check result
    result=$(cat /dev/cmachine 2>/dev/null)
    
    # If not "Wrong syscall", it was accepted
    if ! echo "$result" | grep -q "Wrong syscall"; then
        echo "[$num] ACCEPTED: $result"
        
        # Check if Q4 is done
        if echo "$result" | grep -qi "done\|complete\|Question 5"; then
            echo "=== Q4 COMPLETE ==="
            break
        fi
    fi
done

echo "Final state:"
cat /dev/cmachine
