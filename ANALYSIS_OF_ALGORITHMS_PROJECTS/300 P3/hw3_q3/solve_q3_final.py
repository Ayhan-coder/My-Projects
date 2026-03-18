#!/usr/bin/env python3
"""
Q3: Trick the Verifier for 3-Coloring

Strategy: Exploit the biased verifier by:
1. Analyzing which edges the verifier prefers to challenge
2. Creating colorings that have NO conflicts on heavily-checked edges
3. Accepting conflicts only on rarely-checked edges

The verifier is biased - it doesn't choose edges uniformly at random.
"""
import os
import subprocess
import random
import collections

# Configuration
NUM_GRAPHS = 20
TRIALS_PER_GRAPH = 10
ROUNDS_PER_PROTOCOL = 50
GRAPHS_DIR = "graphs"
COLORINGS_DIR = "colorings"

os.makedirs(GRAPHS_DIR, exist_ok=True)
os.makedirs(COLORINGS_DIR, exist_ok=True)

def generate_graph(idx, size, force_regenerate=False):
    filename = os.path.join(GRAPHS_DIR, f"G_{idx}.txt")
    if os.path.exists(filename) and not force_regenerate:
        return filename
    cmd = ["wsl", "./gen_graph", "--size", str(size)]
    print(f"Generating graph {idx} (size {size})...")
    with open(filename, "w") as f:
        subprocess.run(cmd, stdout=f, check=True)
    return filename

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

def probe_verifier_bias(graph_path, num_probes=100):
    """
    Probe the verifier to find which edges it prefers to challenge.
    """
    edge_counts = collections.defaultdict(int)
    graph_rel = graph_path.replace("\\", "/")
    cmd = ["wsl", "./zk_verifier", "--graph", graph_rel, "--rounds", "1"]
    
    for _ in range(num_probes):
        try:
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, text=True)
            line = p.stdout.readline()
            if line.startswith("CHALLENGE"):
                parts = line.strip().split()
                if len(parts) >= 3:
                    u, v = int(parts[1]), int(parts[2])
                    edge_counts[(min(u,v), max(u,v))] += 1
            p.terminate()
            p.wait()
        except:
            pass
    
    return edge_counts

def solve_coloring_with_bias(graph_path, coloring_path):
    """
    Create a coloring that has ZERO conflicts on frequently-checked edges.
    Strategy: Color nodes in order of how often they're challenged.
    """
    n, edges = read_graph(graph_path)
    if n == 0:
        return 0
    
    # Build adjacency list and edge set
    adj = {i: set() for i in range(n)}
    edge_set = set()
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
        edge_set.add((min(u,v), max(u,v)))
    
    # Probe to find biased edges - do more probes for accuracy
    edge_freq = probe_verifier_bias(graph_path, num_probes=100)
    
    # Sort edges by frequency (most checked first)
    sorted_edges = sorted(edge_freq.items(), key=lambda x: x[1], reverse=True)
    
    # Find the most frequently challenged nodes
    node_freq = collections.defaultdict(int)
    for (u, v), count in edge_freq.items():
        node_freq[u] += count
        node_freq[v] += count
    
    # Sort ALL nodes: hot nodes first, then by degree
    all_nodes = list(range(n))
    all_nodes.sort(key=lambda x: (-node_freq.get(x, 0), -len(adj[x])))
    
    coloring = [-1] * n
    
    # Color nodes in priority order - hottest first
    for v in all_nodes:
        used = set()
        for neighbor in adj[v]:
            if coloring[neighbor] != -1:
                used.add(coloring[neighbor])
        
        # Pick color not used by already-colored neighbors
        for c in [0, 1, 2]:
            if c not in used:
                coloring[v] = c
                break
        
        if coloring[v] == -1:
            # All 3 colors used by neighbors - this will cause a conflict
            # Pick the color that minimizes conflict on HOT edges
            best_c = 0
            best_hot_conflicts = float('inf')
            for c in [0, 1, 2]:
                hot_conflicts = 0
                for neighbor in adj[v]:
                    if coloring[neighbor] == c:
                        edge_key = (min(v, neighbor), max(v, neighbor))
                        hot_conflicts += edge_freq.get(edge_key, 0)
                if hot_conflicts < best_hot_conflicts:
                    best_hot_conflicts = hot_conflicts
                    best_c = c
            coloring[v] = best_c
    
    # Write coloring
    with open(coloring_path, "w") as f:
        for c in coloring:
            f.write(f"{c}\n")
    
    # Count conflicts
    conflicts = sum(1 for u, v in edges if coloring[u] == coloring[v])
    
    # Count conflicts on hot edges specifically
    hot_conflicts = 0
    for (u, v), count in edge_freq.items():
        if coloring[u] == coloring[v]:
            hot_conflicts += count
    
    print(f"    Total conflicts: {conflicts}, Hot edge conflicts: {hot_conflicts}")
    return conflicts

def run_experiment(graph_path, coloring_path):
    accepts = 0
    graph_rel = graph_path.replace("\\", "/")
    verifier_cmd_str = f'wsl ./zk_verifier --graph "{graph_rel}" --rounds {ROUNDS_PER_PROTOCOL}'
    cmd = [
        "python", "honest_prover.py",
        "--verifier", verifier_cmd_str,
        "--graph", graph_path,
        "--coloring", coloring_path
    ]
    for _ in range(TRIALS_PER_GRAPH):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=30)
            if "ACCEPT" in result.stdout:
                accepts += 1
        except Exception as e:
            print(f"Error: {e}")
    return accepts / TRIALS_PER_GRAPH

def main():
    print("Q3 Experiment: Exploiting Biased Verifier", flush=True)
    print("=" * 50, flush=True)
    
    FORCE_REGENERATE = False
    # Use sizes from 10 to 1000 as per problem spec
    sizes = [10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100, 120, 150, 200, 300, 400, 500, 800, 1000]
    
    results = []
    with open("results_final.txt", "w") as rf:
        rf.write("ID\tSize\tConflicts\tAcceptRate\n")

    for i, size in enumerate(sizes):
        idx = i + 1
        print(f"\n[{idx}/20] Size {size}...", flush=True)
        
        g_path = generate_graph(idx, size, force_regenerate=FORCE_REGENERATE)
        c_path = os.path.join(COLORINGS_DIR, f"coloring_{idx}.txt")
        conflicts = solve_coloring_with_bias(g_path, c_path)
        
        rate = run_experiment(g_path, c_path)
        print(f"  Acceptance Rate: {rate*100:.1f}%", flush=True)
        
        results.append((idx, size, conflicts, rate))
        with open("results_final.txt", "a") as rf:
            rf.write(f"{idx}\t{size}\t{conflicts}\t{rate:.2f}\n")
    
    print("\n" + "=" * 50, flush=True)
    print("FINAL RESULTS", flush=True)
    print("=" * 50, flush=True)
    print(f"{'ID':<5}{'Size':<8}{'Conflicts':<12}{'AcceptRate':<12}", flush=True)
    for r in results:
        print(f"{r[0]:<5}{r[1]:<8}{r[2]:<12}{r[3]*100:.1f}%", flush=True)
    
    # Calculate average acceptance
    avg_accept = sum(r[3] for r in results) / len(results) * 100
    print(f"\nAverage Acceptance Rate: {avg_accept:.1f}%", flush=True)

if __name__ == "__main__":
    main()
