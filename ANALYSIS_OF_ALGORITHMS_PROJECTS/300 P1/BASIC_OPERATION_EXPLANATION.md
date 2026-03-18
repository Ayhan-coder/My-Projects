# Basic Operation Analysis for Hamiltonian* Path Algorithms

## What is a Basic Operation?

In algorithm complexity analysis, a **basic operation** is:
- The operation that contributes **most** to the total running time
- Usually executed in the **innermost loop** of the algorithm
- A **constant-time O(1)** operation
- Can be clearly identified and counted

## Our Basic Operation

### Definition

**The basic operation is: Checking if an edge exists between two consecutive vertices in a candidate Hamiltonian* path**

### In Code

```python
# This is the basic operation:
if H[perm[i]][perm[i+1]] == 0:
    return False

# Or equivalently:
if graph[current][neighbor] == 1:
    # edge exists
```

### Why This Operation?

1. **Innermost Loop**: This check happens in the deepest nested structure
2. **Most Frequent**: Executed for every edge in every permutation/path
3. **Dominates Runtime**: Total time is proportional to how many edge checks we perform
4. **O(1) Constant Time**: Simple array access and integer comparison

---

## Operations We COUNT as Basic

### ✅ In `hamiltonian_check(H, perm)`:
```python
for i in range(n - 1):
    if H[perm[i]][perm[i + 1]] == 0:  # ← BASIC OPERATION (counted)
        return False
```
**Count per call**: n - 1 basic operations (worst case)

### ✅ In `backtrack_hamiltonian()`:
```python
for neighbor in range(N):
    if graph[current][neighbor] == 1:  # ← BASIC OPERATION (counted)
        # ... recursive exploration
```
**Count**: Multiple edge checks per recursive call

### ✅ In final edge check (backtracking):
```python
if graph[current][end] == 1:  # ← BASIC OPERATION (counted)
    return True
```

---

## Operations We DO NOT Count as Basic

### ❌ Preprocessing Operations

#### Building subgraph H:
```python
# NOT a basic operation (preprocessing)
H = []
for i in range(n):
    row = []
    for j in range(n):
        vertex_i = subset_list[i]
        vertex_j = subset_list[j]
        row.append(graph[vertex_i][vertex_j])  # Edge lookup, but preprocessing
    H.append(row)
```
**Why not?**: This is O(n²) preprocessing, done once per subset, not in the innermost loop.

#### Component detection (BFS):
```python
# NOT the basic operation (preprocessing)
def find_component(graph, start_node):
    for neighbor in range(N):
        has_edge = (graph[node][neighbor] == 1)  # Edge check, but preprocessing
        if has_edge and not is_visited:
            visited.add(neighbor)
            queue.append(neighbor)
```
**Why not?**: This is a one-time preprocessing step to find components, not part of the path validation loop.

### ❌ Control Flow Operations

```python
# NOT basic operations
for i in range(n - 1):           # Loop control
if not contains_start:            # Boolean check (not innermost)
while len(queue) > 0:             # Loop condition
```

### ❌ Data Structure Operations

```python
# NOT basic operations
visited.add(neighbor)             # Set insertion
path.append(neighbor)             # List append
perm = [s] + list(middle_perm)    # List construction
```

### ❌ Function Calls

```python
# NOT basic operations
for subset in itertools.combinations(vertices, n):  # Iterator operation
for middle_perm in itertools.permutations(...):     # Permutation generation
```

---

## Complexity Analysis Using Basic Operations

### Naive Algorithm

**Structure**:
```
For each of C(3n-2, n-2) subsets:
    Build H (O(n²) edge lookups - preprocessing)
    For each of (n-2)! permutations:
        Check n-1 edges  ← COUNT BASIC OPERATIONS HERE
```

**Basic Operation Count**:
- **Best case**: First permutation works → **O(n)** basic operations (after O(n²) preprocessing)
- **Worst case**: C(3n-2, n-2) × (n-2)! × **(n-1)** basic operations
- **Average case**: Similar to worst case

### Optimized Algorithm

**Structure**:
```
Find component (O(n) edge checks - preprocessing)
Build H for component (O(n²) - preprocessing)
For each of (n-2)! permutations:
    Check n-1 edges  ← COUNT BASIC OPERATIONS HERE
```

**Basic Operation Count**:
- **Best case**: First permutation works → **n-1** basic operations (after O(n²) preprocessing)
- **Worst case**: **(n-2)! × (n-1)** basic operations
- **Average case**: Approximately (n-2)! × (n-1) / 2 basic operations

**Time Complexity**: (n-2)! × (n-1) + O(n²) = **(n-2)! × n** (since (n-1) ≈ n asymptotically)

### Bonus (Held-Karp Dynamic Programming) Algorithm

**Structure**:
```
Find component (preprocessing)
Build induced subgraph H (preprocessing)
Initialize DP table: dp[2^n][n]
For each subset mask (2^n total):
    For each vertex u in mask:
        For each vertex v not in mask:
            Check if edge (u,v) exists  ← COUNT BASIC OPERATIONS HERE
            Update dp[mask | v][v]
Return dp[full_mask][end]
```

**Basic Operation Count**:
- **Best case**: O(n² × 2ⁿ) (DP must explore all states)
- **Worst case**: O(n² × 2ⁿ) edge checks
- **Average case**: O(n² × 2ⁿ) (deterministic algorithm)

**Note**: Held-Karp provides **exponentially better** complexity than the optimized algorithm:
- Optimized: (n-2)! × n ≈ O(n!)
- Held-Karp: O(n² × 2ⁿ)
- For n=20: 2²⁰ ≈ 1 million vs 20! ≈ 2.4 × 10¹⁸ (factor of ~10¹² improvement!)

---

## Summary Table

| Operation | Basic Operation? | Reason |
|-----------|-----------------|----------|
| `H[perm[i]][perm[i+1]] == 0` | ✅ **YES** | Innermost loop, most frequent, O(1) |
| `H[u][v] == 1` (in DP transitions) | ✅ **YES** | Edge check during state transitions |
| Building subgraph H | ❌ No | Preprocessing (O(n²), outside main loop) |
| BFS component detection | ❌ No | Preprocessing (one-time setup) |
| Generating permutations | ❌ No | Library call (not what we analyze) |
| Bitmask operations | ❌ No | Data structure management |
| DP table updates | ❌ No | State bookkeeping |
| Array indexing `perm[i]` | ❌ No | Part of computing basic operation |
| Loop counter `i < n` | ❌ No | Loop overhead |

---

## Visual Representation

```
NAIVE ALGORITHM:
┌─────────────────────────────────────────┐
│ For C(3n-2,n-2) subsets:               │  Outer structure
│  ┌────────────────────────────────────┐ │
│  │ Build H (preprocessing)            │ │  O(n²) not counted
│  │ For (n-2)! permutations:           │ │
│  │  ┌───────────────────────────────┐ │ │
│  │  │ For i in range(n-1):          │ │ │
│  │  │   if H[perm[i]][perm[i+1]]==0 │ │ │  ← BASIC OPERATION
│  │  │      return False              │ │ │     (counted here)
│  │  └───────────────────────────────┘ │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘

Total basic operations (worst): C(3n-2,n-2) × (n-2)! × (n-1)
```

---

## References in Code

All basic operations in `solution.py` are now marked with explicit comments:
- `hamiltonian_check()`: Main basic operation location
- `backtrack_hamiltonian()`: Basic operations in DFS exploration
- `find_component()`: Clarified as preprocessing (NOT basic operations)

Look for comments like:
```python
# BASIC OPERATION: ...
```

in the code to identify where we count operations for complexity analysis.
