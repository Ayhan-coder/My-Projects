#!/usr/bin/env python3
"""
Test if we can create a graph and a valid 3-coloring that passes the protocol.
"""
import os
import subprocess

# Create a simple 3-colorable test graph: a triangle (K3)
test_graph = """3 3
0 1
1 2
0 2
"""

with open("test_graph.txt", "w") as f:
    f.write(test_graph)

# Create a valid 3-coloring for this triangle
test_coloring = """0
1
2
"""

with open("test_coloring.txt", "w") as f:
    f.write(test_coloring)

# Test the protocol
print("Testing protocol on a simple triangle (K3) with a valid 3-coloring...")
result = subprocess.run([
    "python", "honest_prover.py",
    "--verifier", "wsl ./zk_verifier --graph test_graph.txt --rounds 5",
    "--graph", "test_graph.txt",
    "--coloring", "test_coloring.txt"
], capture_output=True, text=True, timeout=10)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print("\nReturn code:", result.returncode)

# Check if it passed
if "ACCEPT" in result.stdout:
    print("\n✓ Protocol ACCEPTED!")
else:
    print("\n✗ Protocol REJECTED")
