#!/usr/bin/env python3
import subprocess

# Create a simple valid 3-coloring for the smallest graph
# Graph G_1.txt has 1004 nodes

# Just create a valid 3-coloring by alternating colors
with open('colorings/test_coloring.txt', 'w') as f:
    for i in range(1004):
        f.write(f"{i % 3}\n")

# Test the protocol
result = subprocess.run([
    "python", "honest_prover.py",
    "--verifier", "wsl ./zk_verifier --graph graphs/G_1.txt --rounds 10",
    "--graph", "graphs/G_1.txt",
    "--coloring", "colorings/test_coloring.txt"
], capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print("\nReturn code:", result.returncode)
