"""
Full Test Suite for MPI-Based Parallel NLP System
Tests all 4 patterns with all 5 test cases
"""

import subprocess
import sys
import os
from datetime import datetime

# Full test matrix
FULL_TESTS = []

# Pattern 1: End-to-End (3 processes: 1 manager + 2 workers)
for tc in [1, 2, 3, 4, 5]:
    FULL_TESTS.append({
        "pattern": 1, "processes": 3, "test_case": tc,
        "name": f"Pattern 1 (End-to-End) - Test Case {tc}"
    })

# Pattern 2: Linear Pipeline (exactly 5 processes)
for tc in [1, 2, 3, 4, 5]:
    FULL_TESTS.append({
        "pattern": 2, "processes": 5, "test_case": tc,
        "name": f"Pattern 2 (Linear Pipeline) - Test Case {tc}"
    })

# Pattern 3: Parallel Pipelines (5 processes: 1 manager + 1 pipeline)
for tc in [1, 2, 3, 4, 5]:
    FULL_TESTS.append({
        "pattern": 3, "processes": 5, "test_case": tc,
        "name": f"Pattern 3 (Parallel Pipelines) - Test Case {tc}"
    })

# Pattern 4: Task Parallelism (5 processes: 1 manager + 4 workers)
for tc in [1, 2, 3, 4, 5]:
    FULL_TESTS.append({
        "pattern": 4, "processes": 5, "test_case": tc,
        "name": f"Pattern 4 (Task Parallelism) - Test Case {tc}"
    })

def run_test(config):
    """Run a single test configuration"""
    pattern = config["pattern"]
    processes = config["processes"]
    test_case = config["test_case"]
    
    text_file = f"test_cases/text_{test_case}.txt"
    vocab_file = f"test_cases/vocab_{test_case}.txt"
    stopwords_file = f"test_cases/stopwords_{test_case}.txt"
    
    cmd = [
        "mpiexec", "-n", str(processes),
        "python", "solution.py",
        "--text", text_file,
        "--vocab", vocab_file,
        "--stopwords", stopwords_file,
        "--pattern", str(pattern)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": "TIMEOUT", "returncode": -1}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}

def main():
    output_file = "full_test_results.txt"
    
    print("=" * 80)
    print("MPI-Based Parallel NLP System - Full Test Suite")
    print(f"Total Tests: {len(FULL_TESTS)}")
    print("=" * 80)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("MPI-Based Parallel NLP System - Full Test Results\n")
        f.write(f"Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Tests: {len(FULL_TESTS)}\n")
        f.write("=" * 80 + "\n\n")
        
        passed = 0
        failed = 0
        failed_tests = []
        
        for i, config in enumerate(FULL_TESTS, 1):
            test_name = config['name']
            print(f"[{i}/{len(FULL_TESTS)}] {test_name}...", end=" ", flush=True)
            
            f.write(f"\n{'=' * 80}\n")
            f.write(f"Test {i}/{len(FULL_TESTS)}: {test_name}\n")
            f.write(f"{'=' * 80}\n")
            f.write(f"Pattern: {config['pattern']}, Processes: {config['processes']}, Test Case: {config['test_case']}\n\n")
            
            result = run_test(config)
            
            if result["success"]:
                passed += 1
                f.write("STATUS: PASSED\n\n")
                f.write("OUTPUT:\n")
                f.write(result["stdout"])
                f.write("\n")
                print("PASSED")
            else:
                failed += 1
                failed_tests.append(test_name)
                f.write("STATUS: FAILED\n\n")
                if result["stdout"]:
                    f.write("STDOUT:\n")
                    f.write(result["stdout"])
                    f.write("\n")
                if result["stderr"]:
                    f.write("STDERR:\n")
                    f.write(result["stderr"])
                    f.write("\n")
                print("✗ FAILED")
        
        # Write summary
        f.write("\n" + "=" * 80 + "\n")
        f.write("FINAL SUMMARY\n")
        f.write("=" * 80 + "\n")
        f.write(f"Total Tests:  {len(FULL_TESTS)}\n")
        f.write(f"Passed:       {passed} ({100*passed//len(FULL_TESTS)}%)\n")
        f.write(f"Failed:       {failed} ({100*failed//len(FULL_TESTS)}%)\n")
        
        if failed_tests:
            f.write("\nFailed Tests:\n")
            for test in failed_tests:
                f.write(f"  - {test}\n")
        
        f.write("=" * 80 + "\n")
    
    # Print summary to console
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"Total Tests:  {len(FULL_TESTS)}")
    print(f"Passed:       {passed} ({100*passed//len(FULL_TESTS)}%)")
    print(f"Failed:       {failed} ({100*failed//len(FULL_TESTS)}%)")
    
    if failed_tests:
        print("\nFailed Tests:")
        for test in failed_tests:
            print(f"  - {test}")
    
    print("=" * 80)
    print(f"\nDetailed results saved to: {output_file}")
    print("=" * 80)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
