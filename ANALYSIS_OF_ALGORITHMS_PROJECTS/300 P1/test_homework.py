"""
Test script to verify that the Hamiltonian* path homework is working correctly.
"""
import random
from graph_construction import generate_tricky_graph
from solution import (
    hamiltonian_naive,
    hamiltonian_optimized, 
    hamiltonian_bonus
)

def test_basic_functionality():
    """Test that all algorithms produce consistent results."""
    print("=" * 60)
    print("TEST 1: Basic Functionality Test")
    print("=" * 60)
    
    # Test with small n to ensure all algorithms can run
    n = 4
    random.seed(42)  # For reproducibility
    
    graph, start, end = generate_tricky_graph(n)
    
    print(f"\nTesting with n={n} (graph size = {len(graph)})")
    print(f"Start vertex: {start}, End vertex: {end}")
    
    # Test naive algorithm
    print("\nRunning naive algorithm...")
    try:
        result_naive = hamiltonian_naive(graph, start, end)
        print(f"✓ Naive result: {result_naive}")
    except Exception as e:
        print(f"✗ Naive failed with error: {e}")
        return False
    
    # Test optimized algorithm
    print("\nRunning optimized algorithm...")
    try:
        result_optimized = hamiltonian_optimized(graph, start, end)
        print(f"✓ Optimized result: {result_optimized}")
    except Exception as e:
        print(f"✗ Optimized failed with error: {e}")
        return False
    
    # Test bonus algorithm
    print("\nRunning bonus (backtracking) algorithm...")
    try:
        result_bonus = hamiltonian_bonus(graph, start, end)
        print(f"✓ Bonus result: {result_bonus}")
    except Exception as e:
        print(f"✗ Bonus failed with error: {e}")
        return False
    
    # Check consistency
    if result_naive == result_optimized == result_bonus:
        print(f"\n✓ SUCCESS: All algorithms agree on result: {result_naive}")
        return True
    else:
        print(f"\n✗ FAILURE: Algorithms disagree!")
        print(f"  Naive: {result_naive}, Optimized: {result_optimized}, Bonus: {result_bonus}")
        return False


def test_graph_structure():
    """Test that the graph has the expected structure (3 disconnected components)."""
    print("\n" + "=" * 60)
    print("TEST 2: Graph Structure Test")
    print("=" * 60)
    
    n = 5
    random.seed(123)
    
    graph, start, end = generate_tricky_graph(n)
    N = len(graph)
    
    print(f"\nGraph has {N} vertices (expected: {3*n})")
    
    # Find all components using BFS
    def find_all_components(graph):
        N = len(graph)
        visited = set()
        components = []
        
        for start_node in range(N):
            if start_node not in visited:
                component = set()
                queue = [start_node]
                component.add(start_node)
                visited.add(start_node)
                
                while queue:
                    node = queue.pop(0)
                    for neighbor in range(N):
                        if graph[node][neighbor] == 1 and neighbor not in visited:
                            visited.add(neighbor)
                            component.add(neighbor)
                            queue.append(neighbor)
                
                components.append(component)
        
        return components
    
    components = find_all_components(graph)
    
    print(f"Number of components: {len(components)} (expected: 3)")
    print(f"Component sizes: {[len(c) for c in components]} (expected: all size {n})")
    
    # Check if all components have size n
    if len(components) == 3 and all(len(c) == n for c in components):
        print("✓ Graph structure is correct!")
        return True
    else:
        print("✗ Graph structure is incorrect!")
        return False


def test_multiple_runs():
    """Test multiple random graphs to ensure consistency."""
    print("\n" + "=" * 60)
    print("TEST 3: Multiple Random Graphs Test")
    print("=" * 60)
    
    n = 4
    num_tests = 5
    
    print(f"\nTesting {num_tests} random graphs with n={n}...")
    
    all_passed = True
    for i in range(num_tests):
        random.seed(i)
        graph, start, end = generate_tricky_graph(n)
        
        result_naive = hamiltonian_naive(graph, start, end)
        result_optimized = hamiltonian_optimized(graph, start, end)
        result_bonus = hamiltonian_bonus(graph, start, end)
        
        if result_naive == result_optimized == result_bonus:
            print(f"  Test {i+1}: ✓ All agree (result={result_naive})")
        else:
            print(f"  Test {i+1}: ✗ Disagreement! Naive={result_naive}, Opt={result_optimized}, Bonus={result_bonus}")
            all_passed = False
    
    if all_passed:
        print("\n✓ All tests passed!")
        return True
    else:
        print("\n✗ Some tests failed!")
        return False


def test_performance():
    """Test performance of algorithms (with small n to avoid timeout)."""
    print("\n" + "=" * 60)
    print("TEST 4: Performance Comparison")
    print("=" * 60)
    
    import time
    
    n_values = [3, 4, 5]
    
    for n in n_values:
        random.seed(42)
        graph, start, end = generate_tricky_graph(n)
        
        print(f"\nn={n} (graph size = {3*n}):")
        
        # Naive
        start_time = time.time()
        result_naive = hamiltonian_naive(graph, start, end)
        naive_time = time.time() - start_time
        print(f"  Naive:      {naive_time:.4f}s (result={result_naive})")
        
        # Optimized
        start_time = time.time()
        result_optimized = hamiltonian_optimized(graph, start, end)
        opt_time = time.time() - start_time
        print(f"  Optimized:  {opt_time:.4f}s (result={result_optimized})")
        
        # Bonus
        start_time = time.time()
        result_bonus = hamiltonian_bonus(graph, start, end)
        bonus_time = time.time() - start_time
        print(f"  Bonus:      {bonus_time:.4f}s (result={result_bonus})")
        
        if opt_time < naive_time:
            speedup = naive_time / opt_time
            print(f"  ✓ Optimized is {speedup:.2f}x faster than naive")
    
    return True


def test_edge_cases():
    """Test edge cases like small graphs and specific scenarios."""
    print("\n" + "=" * 60)
    print("TEST 5: Edge Cases")
    print("=" * 60)
    
    all_passed = True
    
    # Test with n=2 (smallest meaningful case)
    print("\nTesting with n=2 (6 vertices total)...")
    random.seed(999)
    graph, start, end = generate_tricky_graph(2)
    
    result_naive = hamiltonian_naive(graph, start, end)
    result_optimized = hamiltonian_optimized(graph, start, end)
    result_bonus = hamiltonian_bonus(graph, start, end)
    
    if result_naive == result_optimized == result_bonus:
        print(f"  ✓ n=2: All algorithms agree (result={result_naive})")
    else:
        print(f"  ✗ n=2: Disagreement! Naive={result_naive}, Opt={result_optimized}, Bonus={result_bonus}")
        all_passed = False
    
    # Test with n=3
    print("\nTesting with n=3 (9 vertices total)...")
    random.seed(888)
    graph, start, end = generate_tricky_graph(3)
    
    result_naive = hamiltonian_naive(graph, start, end)
    result_optimized = hamiltonian_optimized(graph, start, end)
    result_bonus = hamiltonian_bonus(graph, start, end)
    
    if result_naive == result_optimized == result_bonus:
        print(f"  ✓ n=3: All algorithms agree (result={result_naive})")
    else:
        print(f"  ✗ n=3: Disagreement! Naive={result_naive}, Opt={result_optimized}, Bonus={result_bonus}")
        all_passed = False
    
    if all_passed:
        print("\n✓ All edge cases passed!")
        return True
    else:
        print("\n✗ Some edge cases failed!")
        return False


def test_same_component():
    """Test cases where start and end are in the same component."""
    print("\n" + "=" * 60)
    print("TEST 6: Same Component Scenarios")
    print("=" * 60)
    
    all_passed = True
    
    print("\nGenerating 10 graphs and checking same-component behavior...")
    
    for seed in range(100, 110):
        random.seed(seed)
        n = 4
        graph, start, end = generate_tricky_graph(n)
        
        # Find which component start is in
        from solution import find_component
        component_start = find_component(graph, start)
        component_end = find_component(graph, end)
        
        same_component = (component_start == component_end)
        
        result_naive = hamiltonian_naive(graph, start, end)
        result_optimized = hamiltonian_optimized(graph, start, end)
        result_bonus = hamiltonian_bonus(graph, start, end)
        
        # All three should agree
        if result_naive == result_optimized == result_bonus:
            status = "same" if same_component else "diff"
            print(f"  Seed {seed}: ✓ {status} component, result={result_naive}")
        else:
            print(f"  Seed {seed}: ✗ Disagreement! Naive={result_naive}, Opt={result_optimized}, Bonus={result_bonus}")
            all_passed = False
    
    if all_passed:
        print("\n✓ All same-component tests passed!")
        return True
    else:
        print("\n✗ Some same-component tests failed!")
        return False


def test_different_sizes():
    """Test with various values of n to ensure scalability."""
    print("\n" + "=" * 60)
    print("TEST 7: Different Graph Sizes")
    print("=" * 60)
    
    n_values = [2, 3, 4, 5, 6]
    all_passed = True
    
    for n in n_values:
        random.seed(42 + n)
        graph, start, end = generate_tricky_graph(n)
        
        print(f"\nTesting n={n} (graph size = {3*n})...")
        
        try:
            result_naive = hamiltonian_naive(graph, start, end)
            result_optimized = hamiltonian_optimized(graph, start, end)
            result_bonus = hamiltonian_bonus(graph, start, end)
            
            if result_naive == result_optimized == result_bonus:
                print(f"  ✓ All algorithms agree (result={result_naive})")
            else:
                print(f"  ✗ Disagreement! Naive={result_naive}, Opt={result_optimized}, Bonus={result_bonus}")
                all_passed = False
        except Exception as e:
            print(f"  ✗ Error occurred: {e}")
            all_passed = False
    
    if all_passed:
        print("\n✓ All size tests passed!")
        return True
    else:
        print("\n✗ Some size tests failed!")
        return False


def test_algorithm_correctness():
    """Test that algorithms correctly identify when no path exists."""
    print("\n" + "=" * 60)
    print("TEST 8: No-Path Detection")
    print("=" * 60)
    
    all_passed = True
    found_no_path = False
    found_path = False
    
    print("\nSearching for graphs with and without Hamiltonian* paths...")
    
    for seed in range(200, 250):
        random.seed(seed)
        n = 4
        graph, start, end = generate_tricky_graph(n)
        
        result = hamiltonian_optimized(graph, start, end)
        
        if result:
            found_path = True
        else:
            found_no_path = True
        
        # Verify all three agree
        result_naive = hamiltonian_naive(graph, start, end)
        result_bonus = hamiltonian_bonus(graph, start, end)
        
        if not (result == result_naive == result_bonus):
            print(f"  ✗ Seed {seed}: Disagreement! Naive={result_naive}, Opt={result}, Bonus={result_bonus}")
            all_passed = False
        
        if found_no_path and found_path:
            break
    
    if found_path:
        print(f"  ✓ Found graphs WITH Hamiltonian* paths")
    else:
        print(f"  ⚠ Warning: No graphs with Hamiltonian* paths found")
    
    if found_no_path:
        print(f"  ✓ Found graphs WITHOUT Hamiltonian* paths")
    else:
        print(f"  ⚠ Warning: All tested graphs had Hamiltonian* paths")
    
    if all_passed:
        print("\n✓ No-path detection test passed!")
        return True
    else:
        print("\n✗ No-path detection test failed!")
        return False


def test_determinism():
    """Test that algorithms are deterministic with same input."""
    print("\n" + "=" * 60)
    print("TEST 9: Determinism Test")
    print("=" * 60)
    
    all_passed = True
    
    print("\nRunning same graph through each algorithm multiple times...")
    
    random.seed(12345)
    n = 4
    graph, start, end = generate_tricky_graph(n)
    
    # Run each algorithm 5 times
    for algo_name, algo_func in [("Naive", hamiltonian_naive), 
                                   ("Optimized", hamiltonian_optimized), 
                                   ("Bonus", hamiltonian_bonus)]:
        results = []
        for run in range(5):
            result = algo_func(graph, start, end)
            results.append(result)
        
        if len(set(results)) == 1:
            print(f"  ✓ {algo_name}: Deterministic (result={results[0]})")
        else:
            print(f"  ✗ {algo_name}: Non-deterministic! Results: {results}")
            all_passed = False
    
    if all_passed:
        print("\n✓ Determinism test passed!")
        return True
    else:
        print("\n✗ Determinism test failed!")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("HAMILTONIAN* PATH HOMEWORK VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Graph Structure", test_graph_structure),
        ("Multiple Random Graphs", test_multiple_runs),
        ("Performance", test_performance),
        ("Edge Cases", test_edge_cases),
        ("Same Component Scenarios", test_same_component),
        ("Different Graph Sizes", test_different_sizes),
        ("No-Path Detection", test_algorithm_correctness),
        ("Determinism", test_determinism)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ {test_name} crashed with error: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Your homework is working well!")
    else:
        print("⚠️  SOME TESTS FAILED. Please review the errors above.")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    main()
