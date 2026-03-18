#!/bin/bash

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║             WALLY CACHE ARCHITECTURE - COMPREHENSIVE TEST SUITE              ║"
echo "║                          Running All Tests...                                ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Array to store test results
declare -a test_results
declare -a test_names

# Test 1: Cache Configuration Analysis
echo "Running Test 1: Cache Configuration Analysis..."
python3 /root/test_wally_cache.py > /tmp/test1.log 2>&1
test_results+=($?)
test_names+=("Cache Configuration Analysis")

# Test 2: LSU Module Validation
echo "Running Test 2: LSU Module Validation..."
python3 /root/test_lsu_modules.py > /tmp/test2.log 2>&1
test_results+=($?)
test_names+=("LSU Module Validation")

# Test 3: Report Validation
echo "Running Test 3: Report Validation..."
python3 /root/test_report.py > /tmp/test3.log 2>&1
test_results+=($?)
test_names+=("Report Validation")

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                            TEST RESULTS SUMMARY                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

passed=0
failed=0

for i in "${!test_names[@]}"; do
    name="${test_names[$i]}"
    result="${test_results[$i]}"
    
    if [ "$result" -eq 0 ]; then
        echo "  [✓ PASS] ${name}"
        ((passed++))
    else
        echo "  [✗ FAIL] ${name}"
        ((failed++))
    fi
done

echo ""
echo "────────────────────────────────────────────────────────────────────────────────"
echo "Total: $((passed + failed)) tests | Passed: $passed | Failed: $failed"
echo "────────────────────────────────────────────────────────────────────────────────"
echo ""

if [ "$failed" -eq 0 ]; then
    echo "✓✓✓ ALL TESTS PASSED SUCCESSFULLY ✓✓✓"
    echo ""
    exit 0
else
    echo "✗✗✗ SOME TESTS FAILED ✗✗✗"
    echo ""
    echo "Detailed Test Output:"
    echo ""
    
    for i in "${!test_names[@]}"; do
        if [ "${test_results[$i]}" -ne 0 ]; then
            echo "═══════════════════════════════════════════════════════════════════════════════"
            echo "TEST: ${test_names[$i]} (FAILED)"
            echo "═══════════════════════════════════════════════════════════════════════════════"
            cat /tmp/test$((i+1)).log
            echo ""
        fi
    done
    
    exit 1
fi
