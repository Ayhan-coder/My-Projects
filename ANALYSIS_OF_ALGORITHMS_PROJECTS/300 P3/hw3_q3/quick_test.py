#!/usr/bin/env python3
"""Quick test to verify acceptance rate on a single graph."""
import subprocess
import os

# Generate a small graph
print("Generating graph...")
subprocess.run(["wsl", "./gen_graph", "--size", "10"], 
               stdout=open("test_g.txt", "w"), check=True)

# Read graph
with open("test_g.txt", "r") as f:
    tokens = f.read().split()
n = int(tokens[0])
edges = []
for i in range(2, len(tokens), 2):
    edges.append((int(tokens[i]), int(tokens[i+1])))

print(f"Graph: {n} vertices, {len(edges)} edges")

# Build adjacency
adj = {i: set() for i in range(n)}
for u, v in edges:
    adj[u].add(v)
    adj[v].add(u)

# Simple coloring: node 0 = 0, neighbors of 0 = 1, rest greedy
coloring = [-1] * n
coloring[0] = 0
for neighbor in adj[0]:
    coloring[neighbor] = 1

for v in range(n):
    if coloring[v] == -1:
        used = set()
        for neighbor in adj[v]:
            if coloring[neighbor] != -1:
                used.add(coloring[neighbor])
        for c in [0, 1, 2]:
            if c not in used:
                coloring[v] = c
                break
        if coloring[v] == -1:
            coloring[v] = 0

# Write coloring
with open("test_c.txt", "w") as f:
    for c in coloring:
        f.write(f"{c}\n")

conflicts = sum(1 for u, v in edges if coloring[u] == coloring[v])
print(f"Conflicts: {conflicts}/{len(edges)} = {100*conflicts/len(edges):.1f}%")

# Count node 0 conflicts
node0_conf = sum(1 for neighbor in adj[0] if coloring[neighbor] == 0)
print(f"Node 0 conflicts: {node0_conf}")

# Test acceptance
print("\nTesting acceptance (10 trials, 50 rounds each)...")
accepts = 0
for trial in range(10):
    result = subprocess.run([
        "python", "honest_prover.py",
        "--verifier", "wsl ./zk_verifier --graph test_g.txt --rounds 50",
        "--graph", "test_g.txt",
        "--coloring", "test_c.txt"
    ], capture_output=True, text=True)
    
    if "ACCEPT" in result.stdout:
        accepts += 1
        print(f"Trial {trial+1}: ACCEPT")
    else:
        print(f"Trial {trial+1}: {result.stdout.strip()[:40]}")

print(f"\nAcceptance rate: {accepts}/10 = {accepts*10}%")
