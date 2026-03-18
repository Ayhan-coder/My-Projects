import subprocess
import collections
import os
import time

def probe_graph(graph_path, num_probes=500):
    """
    Runs the verifier against the graph multiple times to see which edges it picks.
    Returns a frequency map of edges (u, v) -> count.
    """
    counts = collections.defaultdict(int)
    
    # We only need 1 round to see the first challenge. 
    # The verifier prints CHALLENGE u v immediately.
    # We just allow it to timeout or kill it.
    
    graph_rel = graph_path.replace("\\", "/")
    cmd = ["wsl", "./zk_verifier", "--graph", graph_rel, "--rounds", "1"]
    
    print(f"Probing {graph_path} with {num_probes} samples...", flush=True)
    
    for _ in range(num_probes):
        try:
            # We communicate via pipes
            p = subprocess.Popen(
                cmd, 
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Read stdout line by line
            # It should print CHALLENGE <seed> u v
            # Wait, looking at honest_prover: line.startswith("CHALLENGE") -> _, us, vs = line.split()
            # It seems CHALLENGE line has 3 parts? "CHALLENGE u v"?
            # honest_prover says: _, us, vs = line.split() => So "CHALLENGE u v" (3 tokens total)
            
            try:
                # We expect immediate output
                line = p.stdout.readline()
                if line.startswith("CHALLENGE"):
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        u, v = int(parts[1]), int(parts[2])
                        # Canonicalize edge
                        if u > v: u, v = v, u
                        counts[(u, v)] += 1
            except Exception:
                pass
            
            # Kill process
            p.terminate()
            p.wait()
            
        except Exception as e:
            print(f"Probe error: {e}")
            
    return counts

def main():
    # Let's test on the existing G_1.txt (Size 14) first, then maybe generate a bigger one.
    # We assume G_1.txt exists from previous run or we regenerate it.
    
    if not os.path.exists("graphs/G_2.txt"):
        # Generate one if missing (Size 100)
        subprocess.run(["wsl", "./gen_graph", "--size", "100"], stdout=open("graphs/G_2.txt", "w"))

    # Choose a graph to probe
    target_graph = "graphs/G_2.txt" # Use a fresh one
    
    # Generate it properly
    subprocess.run(["wsl", "./gen_graph", "--size", "50"], stdout=open("graphs/test_probe.txt", "w"))
    target_graph = "graphs/test_probe.txt"
    
    edge_counts = probe_graph(target_graph, num_probes=50)
    
    # Read the graph to know TOTAL edges
    with open(target_graph, "r") as f:
        lines = f.read().split()
        n = int(lines[0])
        total_edges = []
        raw_edges = list(map(int, lines[2:]))
        for i in range(0, len(raw_edges), 2):
            u, v = raw_edges[i], raw_edges[i+1]
            if u > v: u, v = v, u
            total_edges.append((u, v))
            
    print(f"\nAnalysis for {target_graph} (N={n}, Total Edges={len(total_edges)})")
    print(f"Unique edges challenged: {len(edge_counts)} out of {len(total_edges)}")
    
    # Sort edges by frequency
    sorted_edges = sorted(edge_counts.items(), key=lambda x: x[1], reverse=True)
    
    print("\nTop 10 Most Challenged Edges:")
    for e, count in sorted_edges[:10]:
        print(f"Edge {e}: {count} times")
        
    # Find edges NEVER challenged (in our sample)
    challenged_set = set(edge_counts.keys())
    unchallenged = [e for e in total_edges if e not in challenged_set]
    
    print(f"\nUnchallenged Edges (in sample): {len(unchallenged)}")
    if unchallenged:
        print("Examples:", unchallenged[:10])
        
    # Check if unchallenged edges share common nodes (e.g. high index?)
    if unchallenged:
        high_node_counts = collections.defaultdict(int)
        for u, v in unchallenged:
            high_node_counts[u] += 1
            high_node_counts[v] += 1
        print("Most common nodes in unchallenged edges:", 
              sorted(high_node_counts.items(), key=lambda x: x[1], reverse=True)[:5])

if __name__ == "__main__":
    main()
