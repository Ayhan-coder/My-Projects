# Hamiltonian* Path - Theoretical Analysis

## Part 1: Naive Algorithm Analysis (50 pt)

### Basic Operation (5 pt)

**The basic operation is: checking if an edge exists between two consecutive vertices in a permutation**

Specifically, in Algorithm 5 (Hamiltonian*Check), line 3:
```
if H[perm(i)][perm(i + 1)] = 0

```

This operation:
- Is executed in the innermost loop
- Determines the algorithm's running time
- Is a simple array access/comparison (O(1) operation)

### Time Complexity Analysis (20 pt)

#### Worst Case Complexity

**Steps in the algorithm:**

1. **Subset Generation**: C(3n, n) subsets of size n from 3n vertices
   - Only subsets containing both start and end are processed
   - Worst case: approximately C(3n-2, n-2) valid subsets

2. **For each valid subset**:
   - Build subgraph H: O(n²) operations
   - Find s and t indices: O(n) operations
   - Call AllPermutations: checks (n-2)! permutations
   
3. **For each permutation** (n-2)! permutations:
   - Hamiltonian*Check: checks n-1 edges in worst case
   - Basic operation executed: (n-1) times per permutation

**Total worst case complexity:**
```
T_worst(n) = C(3n-2, n-2) × [(n²) + n + (n-2)! × (n-1)]
          ≈ C(3n-2, n-2) × (n-2)! × n
```

Using Stirling's approximation for C(3n-2, n-2):
```
C(3n-2, n-2) ≈ 3^(3n) / (sqrt(2πn) × 2^n)
```

**Therefore: T_worst(n) = O(C(3n, n) × n!)**

This grows extremely fast - faster than exponential!

#### Best Case Complexity

**Best case occurs when:**
- The first subset tried contains a valid Hamiltonian* path
- The first permutation checked is the valid path

**Steps:**
1. Generate first subset: O(n)
2. Build H: O(n²)
3. First permutation of AllPermutations
4. Hamiltonian*Check finds valid path on first edge check: O(1) if path exists, or finds invalid edge and returns immediately

**T_best(n) = O(n²)**

However, more realistically, if we must check all n-1 edges:
**T_best(n) = O(n²)** for building H + O(n) for checking = **O(n²)**

#### Average Case Complexity

**Assumptions for average case:**
- Graph structure means roughly 1/3 of random subsets will have valid components
- On average, we check about half of all permutations before finding a path (if it exists)
- Early termination in Hamiltonian*Check: on average, check n/2 edges for invalid paths

**Average case:**
```
T_avg(n) ≈ [C(3n-2, n-2) / 2] × [(n-2)! / 2] × [n/2]
         = O(C(3n, n) × n!)
```

**Summary:**
- Best case: **O(n²)**
- Worst case: **O(C(3n, n) × n!)**
- Average case: **O(C(3n, n) × n!)**

---

## Part 2: Optimized Algorithm Analysis (50 pt)

### Key Optimization

**Insight:** The graph has 3 disconnected components of size n each. Since a Hamiltonian* path must visit n nodes and components are disconnected:
- **start and end must be in the same component**
- **That component must have exactly n nodes**

### Algorithm Steps

1. Find component containing start: O(3n) = O(n) using BFS/DFS
2. Check if end is in same component: O(1)
3. If yes, check only permutations within that component of size n

### Time Complexity Analysis

#### Worst Case

**Steps:**
1. Component detection: O(n) using BFS
2. Build subgraph H for n nodes: O(n²)
3. Check all (n-2)! permutations: (n-2)! × (n-1)

**T_worst_optimized(n) = O(n) + O(n²) + (n-2)! × n**
**= O(n!)**

Compare to naive: O(C(3n, n) × n!)

**Improvement factor:**
```
C(3n, n) = (3n)! / (n! × (2n)!)

For n=10: C(30,10) ≈ 3 × 10^13
```

**The optimized version is exponentially faster!**

#### Best Case

Same as naive:
- First permutation is valid path
- **T_best(n) = O(n²)** (component detection + building H + first check)

#### Average Case

**T_avg_optimized(n) = O(n) + O(n²) + O(n!)**
**= O(n!)**

This is drastically better than O(C(3n, n) × n!)

### Comparison Table

| Algorithm | Best Case | Worst Case | Average Case |
|-----------|-----------|------------|--------------|
| Naive | O(n²) | O(C(3n,n) × n!) | O(C(3n,n) × n!) |
| Optimized | O(n²) | O(n!) | O(n!) |
| **Improvement** | Same | **C(3n,n) times faster** | **C(3n,n) times faster** |

---

## Bonus: Superior Algorithm (20 pt)

### Backtracking Approach

Instead of generating all permutations, use DFS with intelligent pruning:

**Key improvements:**
1. Build path incrementally (don't generate all permutations upfront)
2. Prune branches early when they can't lead to solution
3. Stop immediately when solution found
4. Don't explore paths that go to 'end' too early

### Time Complexity

**Worst case:** Still O(n!) - must explore entire search tree
**Average/Best case:** Much better due to:
- Early termination when path found
- Pruning of invalid branches before full exploration
- Typical complexity: O(b^d) where b = branching factor (< n) and d = depth (= n)

### Practical Performance

The backtracking algorithm typically performs much better than O(n!) because:
1. **Pruning**: Many branches eliminated early
2. **Early termination**: Stops at first valid path
3. **Connected graph structure**: Limits branching factor

**Expected performance: O(n^k)** for some k < n in practice

### Discussion: Polynomial Time Algorithms?

**Question:** Can we solve Hamiltonian* Path in polynomial time?

**Answer:** The general Hamiltonian Path problem is NP-complete. However:

1. **Our specific case** with 3 disconnected components of size n:
   - We reduced it to finding Hamiltonian path in ONE component of size n
   - Still NP-complete for general graphs

2. **Special graph structures** where polynomial solutions exist:
   - Trees: O(n)
   - Directed Acyclic Graphs: O(n)
   - Complete graphs: O(n) (any permutation works)

3. **Our graphs** are not special enough - they're general random graphs within each component

**Conclusion:** For this problem, no polynomial-time algorithm is known. The best we can do is:
- Exploit structure (component detection)
- Use intelligent search (backtracking with pruning)
- Typical performance better than theoretical worst case
- Still exponential in worst case: **Ω(n!)**

### Lower Bound

The problem requires checking connectivity between n nodes in some order:
- At minimum, we need to examine Ω(n²) edges
- For finding the specific order: Ω(n!) in worst case
- **Best possible: Ω(n²)** (linear in input size)
- **Worst case: Ω(2^n)** (exponential, typical for NP-complete problems)
