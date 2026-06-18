# Full test runner - runs all patterns with all test cases

import subprocess
import sys
import os
from pathlib import Path

# Test configs
# P1: 2+ procs (1 manager + workers)
# P2: exactly 5 procs
# P3: 1 + 4k procs
# P4: 1 + 2k procs

TEST_CONFIGS = [
    # Pattern 1 tests - using 3 processes (1 manager + 2 workers)
    {"pattern": 1, "processes": 3, "test_cases": [1, 2, 3, 4, 5]},
    
    # Pattern 2 tests - requires exactly 5 processes
    {"pattern": 2, "processes": 5, "test_cases": [1, 2, 3, 4, 5]},
    
    # Pattern 3 tests - using 5 processes (1 manager + 1 pipeline of 4 workers)
    {"pattern": 3, "processes": 5, "test_cases": [1, 2, 3, 4, 5]},
    
    # Pattern 4 tests - using 5 processes (1 manager + 4 workers = 2 pairs)
    {"pattern": 4, "processes": 5, "test_cases": [1, 2, 3, 4, 5]},
]

def run_mpi_test(pattern, num_processes, test_case):
    # Construct file paths
    text_file = f"test_cases/text_{test_case}.txt"
    vocab_file = f"test_cases/vocab_{test_case}.txt"
    stopwords_file = f"test_cases/stopwords_{test_case}.txt"
    
    # Check if files exist
    if not all(os.path.exists(f) for f in [text_file, vocab_file, stopwords_file]):
        return False, "", f"Missing test files for test case {test_case}"
    
    # Construct mpiexec command
    cmd = [
        "mpiexec",
        "-n", str(num_processes),
        "python", "solution.py",
        "--text", text_file,
        "--vocab", vocab_file,
        "--stopwords", stopwords_file,
        "--pattern", str(pattern)
    ]
    
    print(f"  Running: {' '.join(cmd)}")
    
    try:
        # Run the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        if result.returncode == 0:
            return True, result.stdout, result.stderr
        else:
            return False, result.stdout, result.stderr
            
    except subprocess.TimeoutExpired:
        return False, "", "Test timed out after 30 seconds"
    except Exception as e:
        return False, "", f"Error running test: {str(e)}"

def main():
    print("=" * 80)
    print("MPI-Based Parallel NLP System - Comprehensive Test Suite")
    print("=" * 80)
    print()
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    # Run all test configurations
    for config in TEST_CONFIGS:
        pattern = config["pattern"]
        processes = config["processes"]
        test_cases = config["test_cases"]
        
        print(f"\n{'=' * 80}")
        print(f"PATTERN {pattern} - Testing with {processes} processes")
        print(f"{'=' * 80}")
        
        for test_case in test_cases:
            total_tests += 1
            print(f"\n[Test {total_tests}] Pattern {pattern}, Test Case {test_case}")
            print("-" * 80)
            
            success, stdout, stderr = run_mpi_test(pattern, processes, test_case)
            
            if success:
                passed_tests += 1
                print(f"✓ PASSED")
                print("\nOutput:")
                print(stdout)
                if stderr:
                    print("\nWarnings/Info:")
                    print(stderr)
            else:
                failed_tests += 1
                print(f"✗ FAILED")
                if stdout:
                    print("\nStdout:")
                    print(stdout)
                if stderr:
                    print("\nError:")
                    print(stderr)
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests:  {total_tests}")
    print(f"Passed:       {passed_tests} ({100*passed_tests//total_tests if total_tests > 0 else 0}%)")
    print(f"Failed:       {failed_tests} ({100*failed_tests//total_tests if total_tests > 0 else 0}%)")
    print("=" * 80)
    
    # Exit with appropriate code
    sys.exit(0 if failed_tests == 0 else 1)

if __name__ == "__main__":
    main()
