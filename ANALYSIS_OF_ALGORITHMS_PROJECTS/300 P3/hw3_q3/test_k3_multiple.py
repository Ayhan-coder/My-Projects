#!/usr/bin/env python3
import subprocess

# Test the protocol multiple times
print("Running 10 trials on K3 with valid 3-coloring...")
accepts = 0

for trial in range(10):
    result = subprocess.run([
        "python", "honest_prover.py",
        "--verifier", "wsl ./zk_verifier --graph test_graph.txt --rounds 20",
        "--graph", "test_graph.txt",
        "--coloring", "test_coloring.txt"
    ], capture_output=True, text=True, timeout=10)
    
    if "ACCEPT" in result.stdout:
        accepts += 1
        print(f"Trial {trial+1}: ACCEPT")
    else:
        print(f"Trial {trial+1}: REJECT - {result.stdout.strip()}")

print(f"\nAcceptance rate: {accepts}/10 = {accepts*10}%")
