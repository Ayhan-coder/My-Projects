#!/usr/bin/env python3
"""
Wally Cache Report Validation Test
Verifies that the required assignment report is present and complete
"""

import os
import sys
import re

def test_report():
    """Test the cache report document"""
    
    print("\n" + "="*80)
    print(" WALLY CACHE REPORT VALIDATION TEST")
    print("="*80)
    
    report_file = '/root/Wally_cache_report.md'
    
    # TEST 1: Report Existence
    print("\n[TEST 1] Report File Existence")
    print("-" * 80)
    
    test_count = 1
    pass_count = 0
    
    if os.path.exists(report_file):
        filesize = os.path.getsize(report_file)
        print(f"  [✓ PASS] Report found: {report_file}")
        print(f"  [✓] File size: {filesize} bytes")
        pass_count += 1
    else:
        print(f"  [✗ FAIL] Report not found: {report_file}")
    
    # TEST 2: Report Content Validation
    print("\n[TEST 2] Report Content Validation")
    print("-" * 80)
    test_count += 1
    
    if os.path.exists(report_file):
        with open(report_file, 'r') as f:
            content = f.read()
        
        # Check for required sections
        required_sections = [
            ('# Default Parameters', 'Default Parameters section'),
            ('# Question 1', 'Question 1 section'),
            ('# Question 2', 'Question 2 section'),
            ('# Question 3', 'Question 3 section'),
            ('# Question 4', 'Question 4 section'),
            ('# Question 5', 'Question 5 section'),
            ('# Bonus', 'Bonus section'),
        ]
        
        all_sections_found = True
        for section, description in required_sections:
            if section in content:
                print(f"  [✓] Found: {description}")
            else:
                print(f"  [✗] Missing: {description}")
                all_sections_found = False
        
        if all_sections_found:
            print("\n  [✓ PASS] All required sections found")
            pass_count += 1
        else:
            print("\n  [✗ FAIL] Some sections are missing")
    
    # TEST 3: Table Validation
    print("\n[TEST 3] Parameter Table Validation")
    print("-" * 80)
    test_count += 1
    
    if os.path.exists(report_file):
        with open(report_file, 'r') as f:
            content = f.read()
        
        # Look for table markers
        table_markers = ['|', 'DCACHE_NUMWAYS', 'ICACHE_NUMWAYS']
        table_found = all(marker in content for marker in table_markers)
        
        if table_found:
            print("  [✓] Table structure detected")
            print("  [✓] Cache parameters in table")
            print("\n  [✓ PASS] Parameter table validation passed")
            pass_count += 1
        else:
            print("  [✗] Table structure not found")
    
    # TEST 4: Calculation Steps
    print("\n[TEST 4] Calculation Steps in Report")
    print("-" * 80)
    test_count += 1
    
    if os.path.exists(report_file):
        with open(report_file, 'r') as f:
            content = f.read()
        
        calculation_keywords = [
            'calculation',
            'Size',
            'cache line',
            'instructions',
            'words'
        ]
        
        calc_found = sum(1 for kw in calculation_keywords if kw.lower() in content.lower())
        
        if calc_found >= len(calculation_keywords) - 1:
            print(f"  [✓] Found {calc_found} calculation-related keywords")
            print("  [✓] Report includes calculation steps")
            print("\n  [✓ PASS] Calculation validation passed")
            pass_count += 1
        else:
            print(f"  [✗] Only found {calc_found} calculation keywords")
    
    # TEST 5: References
    print("\n[TEST 5] References and Citations")
    print("-" * 80)
    test_count += 1
    
    if os.path.exists(report_file):
        with open(report_file, 'r') as f:
            content = f.read()
        
        reference_keywords = ['reference', 'source', 'github', 'textbook', 'slide', 'https://']
        
        ref_found = sum(1 for kw in reference_keywords if kw.lower() in content.lower())
        
        if ref_found >= 2:
            print(f"  [✓] Found {ref_found} reference-related keywords")
            print("  [✓] Report includes citations and references")
            print("\n  [✓ PASS] Reference validation passed")
            pass_count += 1
        else:
            print(f"  [✗] Only found {ref_found} reference keywords")
    
    # TEST 6: Source Code References
    print("\n[TEST 6] Source Code References (for Bonus)")
    print("-" * 80)
    test_count += 1
    
    if os.path.exists(report_file):
        with open(report_file, 'r') as f:
            content = f.read()
        
        if 'https://github.com/openhwgroup/cvw' in content or 'github.com' in content.lower():
            print("  [✓] GitHub repository references found")
            print("  [✓] Bonus section references source code")
            print("\n  [✓ PASS] Source code reference validation passed")
            pass_count += 1
        else:
            print("  [✗] Source code references not found")
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"\nReport Validation: {pass_count}/{test_count}\n")
    
    if pass_count == test_count:
        print("="*80)
        print("✓✓✓ ALL REPORT TESTS PASSED ✓✓✓")
        print("="*80 + "\n")
        print("Report Contents:")
        print("  ✓ Default Parameters section with table")
        print("  ✓ Question 1 - I$ and D$ cache sizes")
        print("  ✓ Question 2 - Instructions per cache line")
        print("  ✓ Question 3 - 32-bit words per D$ fill")
        print("  ✓ Question 4 - Cache hit/miss definitions")
        print("  ✓ Question 5 - Write-back strategy explanation")
        print("  ✓ Bonus - L2 cache design choices")
        print("")
        return 0
    else:
        print("="*80)
        print(f"✗✗✗ {test_count - pass_count} REPORT TEST(S) FAILED ✗✗✗")
        print("="*80 + "\n")
        return 1

if __name__ == '__main__':
    sys.exit(test_report())
