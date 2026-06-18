#!/usr/bin/env bash
set -u

DEV="/dev/cmachine"

if [ ! -e "$DEV" ]; then
    echo "$DEV does not exist."
    exit 1
fi

echo "Sending START..."
printf 'START\x00' > "$DEV"

echo "Brute-forcing syscall numbers 0..350..."

for i in {0..350}; do
    # Write the number
    # We use printf to ensure no newline if that matters, but usually echo is fine if we handle nulls
    # The previous scripts used printf '%s\x00' "$num"
    
    printf '%s\x00' "$i" > "$DEV"
    
    # Read response
    RESP=$(cat "$DEV")
    
    # Check if response is interesting
    if [[ "$RESP" != *"Wrong syscall number is entered"* ]]; then
        echo "HIT at syscall $i! Response: $RESP"
    fi
    
    if echo "$RESP" | grep -qi "success\|congratulations\|hash"; then
        echo "SUCCESS at syscall $i!"
        echo "Response: $RESP"
        exit 0
    fi
    
    # Optional: print progress every 10
    if (( i % 10 == 0 )); then
        echo "Tried $i... Last response: $RESP"
    fi
done

echo "Finished loop. Final check:"
cat "$DEV"
