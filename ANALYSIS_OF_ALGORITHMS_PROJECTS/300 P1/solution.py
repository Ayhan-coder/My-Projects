import itertools
import time
import random

def hamiltonian_naive(graph, start, end):
    N = len(graph)
    n = N // 3
    vertices = list(range(N))
    
    # Try all subsets of size n that contain both start and end
    for subset in itertools.combinations(vertices, n):
        # Check if subset contains both start and end
        contains_start = False
        contains_end = False
        for vertex in subset:
            if vertex == start:  contains_start = True
            if vertex == end:   contains_end = True
        
        if not contains_start or not contains_end:
            continue
        
        # Build subgraph H for this subset
        subset_list = list(subset)
        H = []
        for i in range(n):
            row = []
            for j in range(n):
                vertex_i = subset_list[i]
                vertex_j = subset_list[j]
                row.append(graph[vertex_i][vertex_j])
            H.append(row)
        
        # Find indices of start and end in subset
        s = -1
        t = -1
        for i in range(len(subset_list)):
            if subset_list[i] == start:
                s = i
            if subset_list[i] == end:
                t = i
        
        # Try all permutations starting at s and ending at t
        if all_permutations(H, s, t):
            return True
    
    return False


def all_permutations(H, s, t):
    """
    Check all permutations that start at index s and end at index t.
    """
    n = len(H)
    
    # Build list of all indices
    indices = []
    for i in range(n):
        indices.append(i)
    
    # Remove s and t from middle positions
    middle_indices = []
    for i in indices:
        if i != s and i != t:
            middle_indices.append(i)
    
    # Try all permutations of middle indices
    for middle_perm in itertools.permutations(middle_indices):
        # Build full permutation: start with s, then middle nodes, then t
        perm = [s]
        for node in middle_perm:
            perm.append(node)
        perm.append(t)
        
        if hamiltonian_check(H, perm):
            return True
    
    return False


def hamiltonian_check(H, perm):
    """
    Check if the given permutation forms a valid path.
    Basic operation happens here: checking H[perm[i]][perm[i+1]]
    """
    n = len(H)
    for i in range(n - 1):
        if H[perm[i]][perm[i + 1]] == 0:
            return False  # Early exit on first missing edge
    return True


def hamiltonian_optimized(graph, start, end):
    N = len(graph)
    n = N // 3
    
    # Find connected component containing start using BFS/DFS
    component_start = find_component(graph, start)
    component_end = find_component(graph, end)
    
    # Check if start and end are in the same component
    # Two sets are equal if they have the same elements
    if component_start != component_end:
        return False
    
    # Get the component containing both start and end
    component = component_start
    
    # If component size != n, no Hamiltonian* path of length n exists
    component_size = len(component)
    if component_size != n:
        return False
    
    # Build subgraph H for this component
    component_list = list(component)
    H = []
    for i in range(n):
        row = []
        for j in range(n):
            vertex_i = component_list[i]
            vertex_j = component_list[j]
            edge_value = graph[vertex_i][vertex_j]
            row.append(edge_value)
        H.append(row)
    
    # Find indices of start and end in component
    s = -1
    t = -1
    for i in range(len(component_list)):
        if component_list[i] == start:
            s = i
        if component_list[i] == end:
            t = i
    
    # Check all permutations in this component only
    return all_permutations(H, s, t)


def find_component(graph, start_node):
    """
    Find all nodes in the connected component containing start_node using BFS.
    """
    N = len(graph)
    visited = set()
    queue = []
    
    # Start with the start_node
    queue.append(start_node)
    visited.add(start_node)
    
    # Process all nodes in the queue
    while len(queue) > 0:
        # Remove first node from queue
        node = queue[0]
        queue = queue[1:]
        
        # Check all possible neighbors
        for neighbor in range(N):
            # Check if there's an edge and neighbor not visited
            has_edge = (graph[node][neighbor] == 1)
            is_visited = (neighbor in visited)
            
            if has_edge and not is_visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return visited


def hamiltonian_bonus(graph, start, end):
    N = len(graph)
    n = N // 3   # each component has size n by construction

    # 1) Find the connected component containing 'start'
    component = find_component(graph, start)

    # 2) Check that 'end' is in the same component and size is exactly n
    if end not in component or len(component) != n:
        return False

    # 3) Compress the component vertices to indices 0..n-1
    component_list = list(component)  # some ordering of the vertices in this component
    index_of = {v: i for i, v in enumerate(component_list)}

    s_idx = index_of[start]
    t_idx = index_of[end]

    # 4) Build adjacency matrix for this n-vertex component
    #    adj[i][j] = 1 if there's an edge between component_list[i] and component_list[j]
    adj = [[0] * n for _ in range(n)]
    for i, vi in enumerate(component_list):
        gi = graph[vi]
        for j, vj in enumerate(component_list):
            adj[i][j] = gi[vj]

    # 5) Held–Karp DP:
    #    dp[mask][v] = True if there exists a simple path that
    #      - starts at s_idx,
    #      - visits exactly the vertices in 'mask' (bitmask over {0..n-1}),
    #      - ends at vertex v.
    #
    #    We ensure that s_idx is always included in the mask.

    FULL_MASK = (1 << n) - 1
    dp = [[False] * n for _ in range(1 << n)]

    # Base case: path of length 1, only 'start' visited
    dp[1 << s_idx][s_idx] = True

    # Transitions: extend paths by adding new vertices
    for mask in range(1 << n):
        # We only care about masks that include the start vertex
        if not (mask & (1 << s_idx)):
            continue

        for v in range(n):
            # v must be in the current mask and be a valid endpoint
            if not (mask & (1 << v)):
                continue
            if not dp[mask][v]:
                continue

            # Try to extend path ending at v by going to a new vertex w
            for w in range(n):
                if mask & (1 << w):
                    continue  # w already used, skip
                if adj[v][w] == 0:
                    continue  # no edge v-w, skip

                next_mask = mask | (1 << w)
                dp[next_mask][w] = True

    # 6) Check if there is a path that:
    #    - visits all n vertices in this component (mask == FULL_MASK),
    #    - starts at s_idx (enforced by construction),
    #    - ends at t_idx.
    return dp[FULL_MASK][t_idx]



