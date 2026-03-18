# Quick test runner - runs one test per pattern to verify everything works

import subprocess
import sys
import os
from datetime import datetime

# Test configs - one per pattern
QUICK_TESTS = [
    {"pattern": 1, "processes": 3, "test_case": 1, "name": "Pattern 1: End-to-End (2 workers)"},
    {"pattern": 2, "processes": 5, "test_case": 1, "name": "Pattern 2: Linear Pipeline"},
    {"pattern": 3, "processes": 5, "test_case": 1, "name": "Pattern 3: Parallel Pipelines"},
    {"pattern": 4, "processes": 5, "test_case": 1, "name": "Pattern 4: Task Parallelism"},
]

def run_test(config):
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
    output_file = "test_results.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("MPI-Based Parallel NLP System - Test Results\n")
        f.write(f"Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        passed = 0
        failed = 0
        
        for i, config in enumerate(QUICK_TESTS, 1):
            print(f"Running test {i}/{len(QUICK_TESTS)}: {config['name']}...")
            
            f.write(f"\nTest {i}: {config['name']}\n")
            f.write("-" * 80 + "\n")
            f.write(f"Pattern: {config['pattern']}, Processes: {config['processes']}, Test Case: {config['test_case']}\n\n")
            
            result = run_test(config)
            
            if result["success"]:
                passed += 1
                f.write("STATUS: ✓ PASSED\n\n")
                f.write("OUTPUT:\n")
                f.write(result["stdout"])
                f.write("\n")
                print(f"  ✓ PASSED")
            else:
                failed += 1
                f.write("STATUS: ✗ FAILED\n\n")
                if result["stdout"]:
                    f.write("STDOUT:\n")
                    f.write(result["stdout"])
                    f.write("\n")
                if result["stderr"]:
                    f.write("STDERR:\n")
                    f.write(result["stderr"])
                    f.write("\n")
                print(f"  ✗ FAILED")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("SUMMARY\n")
        f.write("=" * 80 + "\n")
        f.write(f"Total:  {len(QUICK_TESTS)}\n")
        f.write(f"Passed: {passed}\n")
        f.write(f"Failed: {failed}\n")
        f.write("=" * 80 + "\n")
    
    print(f"\n{'=' * 60}")
    print(f"Test Summary: {passed}/{len(QUICK_TESTS)} passed")
    print(f"Results saved to: {output_file}")
    print(f"{'=' * 60}")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
