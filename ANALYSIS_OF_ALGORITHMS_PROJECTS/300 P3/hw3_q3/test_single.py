import os
import random

# Read graph
def read_graph(filepath):
    with open(filepath, "r") as f:
        lines = f.read().split()
    if not lines:
        return 0, []
    n = int(lines[0])
    m = int(lines[1])
    edges = []
    edge_data = list(map(int, lines[2:]))
    for i in range(0, len(edge_data), 2):
        edges.append((edge_data[i], edge_data[i+1]))
    return n, edges

# Test on smallest graph
g_path = "graphs/G_1.txt"
n, edges = read_graph(g_path)
print(f"Testing on graph with {n} nodes and {len(edges)} edges")

# Build adjacency list
adj = {i: set() for i in range(n)}
for u, v in edges:
    adj[u].add(v)
    adj[v].add(u)

best_coloring = None
best_conflicts = float('inf')

# Try many attempts
for attempt in range(10000):
    nodes = list(range(n))
    random.shuffle(nodes)
    coloring = [-1] * n
    
    for v in nodes:
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
    
    conflicts = sum(1 for u, v in edges if coloring[u] == coloring[v])
    if conflicts < best_conflicts:
        best_conflicts = conflicts
        best_coloring = coloring
        print(f"Attempt {attempt}: Found coloring with {conflicts} conflicts")
        if best_conflicts == 0:
            print("Found zero-conflict coloring!")
            break
    
    if (attempt + 1) % 1000 == 0:
        print(f"Tried {attempt + 1} attempts, best so far: {best_conflicts} conflicts")

print(f"\nBest coloring found: {best_conflicts} conflicts")
