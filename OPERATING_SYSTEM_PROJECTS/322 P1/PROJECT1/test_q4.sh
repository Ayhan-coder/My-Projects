#!/bin/bash
DEV="/dev/cmachine"

echo "Testing single write with space..."
printf "14 56\x00" > "$DEV"
cat "$DEV"
echo ""

echo "Testing single write with newline..."
printf "14\n56\x00" > "$DEV"
cat "$DEV"
echo ""

echo "Testing keep open..."
(
  echo "14"
  sleep 0.1
  echo "56"
  sleep 0.1
) > "$DEV"
cat "$DEV"
echo ""

echo "Testing sum (70)..."
printf "70\x00" > "$DEV"
cat "$DEV"
echo ""

echo "Testing count (2)..."
printf "2\x00" > "$DEV"
cat "$DEV"
echo ""
