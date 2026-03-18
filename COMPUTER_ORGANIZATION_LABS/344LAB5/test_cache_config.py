#!/usr/bin/env python3
"""
Unit test for Wally Cache Configuration Parameters
Tests the cache parameters extracted from config.vh
"""

import re
import sys

def parse_config_file(filepath):
    """Parse Verilog config file and extract cache parameters"""
    params = {}
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Extract cache parameters using regex
    param_names = [
        'DCACHE_NUMWAYS',
        'DCACHE_WAYSIZEINBYTES',
        'DCACHE_LINELENINBITS',
        'ICACHE_NUMWAYS',
        'ICACHE_WAYSIZEINBYTES',
        'ICACHE_LINELENINBITS',
        'CACHE_SRAMLEN',
        'XLEN'
    ]
    
    for param in param_names:
        # Look for localparam or parameter definitions
        pattern = rf'{param}\s*=\s*32\'d(\d+)'
        match = re.search(pattern, content)
        if match:
            params[param] = int(match.group(1))
    
    return params

def test_cache_parameters():
    """Test cache parameter values and relationships"""
    print("=" * 70)
    print("WALLY CACHE CONFIGURATION TEST")
    print("=" * 70)
    
    # Parse the config file
    config_file = '/root/Wally_sources/config.vh'
    params = parse_config_file(config_file)
    
    print(f"\n[✓] Successfully parsed config file: {config_file}")
    print(f"\nExtracted Parameters:")
    print("-" * 70)
    for param, value in sorted(params.items()):
        print(f"  {param:30s} = {value:10d}")
    
    # Validation tests
    print("\n" + "=" * 70)
    print("VALIDATION TESTS")
    print("=" * 70)
    
    test_results = []
    
    # Test 1: DCACHE configuration exists
    if all(p in params for p in ['DCACHE_NUMWAYS', 'DCACHE_WAYSIZEINBYTES', 'DCACHE_LINELENINBITS']):
        print("\n[✓] TEST 1: D$ (Data Cache) parameters found")
        test_results.append(True)
    else:
        print("\n[✗] TEST 1: D$ parameters missing")
        test_results.append(False)
    
    # Test 2: ICACHE configuration exists
    if all(p in params for p in ['ICACHE_NUMWAYS', 'ICACHE_WAYSIZEINBYTES', 'ICACHE_LINELENINBITS']):
        print("[✓] TEST 2: I$ (Instruction Cache) parameters found")
        test_results.append(True)
    else:
        print("[✗] TEST 2: I$ parameters missing")
        test_results.append(False)
    
    # Test 3: Cache size calculations
    if 'DCACHE_NUMWAYS' in params and 'DCACHE_WAYSIZEINBYTES' in params:
        d_cache_size = params['DCACHE_NUMWAYS'] * params['DCACHE_WAYSIZEINBYTES']
        print(f"[✓] TEST 3: D$ total size = {params['DCACHE_NUMWAYS']} ways × {params['DCACHE_WAYSIZEINBYTES']} bytes = {d_cache_size} bytes ({d_cache_size//1024} KB)")
        test_results.append(True)
    else:
        print("[✗] TEST 3: Cannot calculate D$ size")
        test_results.append(False)
    
    # Test 4: I$ cache size calculations
    if 'ICACHE_NUMWAYS' in params and 'ICACHE_WAYSIZEINBYTES' in params:
        i_cache_size = params['ICACHE_NUMWAYS'] * params['ICACHE_WAYSIZEINBYTES']
        print(f"[✓] TEST 4: I$ total size = {params['ICACHE_NUMWAYS']} ways × {params['ICACHE_WAYSIZEINBYTES']} bytes = {i_cache_size} bytes ({i_cache_size//1024} KB)")
        test_results.append(True)
    else:
        print("[✗] TEST 4: Cannot calculate I$ size")
        test_results.append(False)
    
    # Test 5: Cache line size
    if 'DCACHE_LINELENINBITS' in params:
        line_size_bytes = params['DCACHE_LINELENINBITS'] // 8
        line_size_words = line_size_bytes // 4  # 32-bit words
        print(f"[✓] TEST 5: D$ cache line = {params['DCACHE_LINELENINBITS']} bits = {line_size_bytes} bytes = {line_size_words} 32-bit words")
        test_results.append(True)
    else:
        print("[✗] TEST 5: Cannot determine cache line size")
        test_results.append(False)
    
    # Test 6: SRAM configuration
    if 'CACHE_SRAMLEN' in params:
        print(f"[✓] TEST 6: SRAM word length = {params['CACHE_SRAMLEN']} bits")
        test_results.append(True)
    else:
        print("[✗] TEST 6: SRAM configuration missing")
        test_results.append(False)
    
    # Test 7: Verify power-of-2 values (good cache design practice)
    print("\n" + "=" * 70)
    print("POWER-OF-2 VALIDATION (Best Practice Check)")
    print("=" * 70)
    
    def is_power_of_2(n):
        return n > 0 and (n & (n - 1)) == 0
    
    critical_params = [
        'DCACHE_NUMWAYS', 'DCACHE_WAYSIZEINBYTES', 'DCACHE_LINELENINBITS',
        'ICACHE_NUMWAYS', 'ICACHE_WAYSIZEINBYTES', 'ICACHE_LINELENINBITS'
    ]
    
    pow2_ok = True
    for param in critical_params:
        if param in params:
            value = params[param]
            is_pow2 = is_power_of_2(value)
            status = "✓" if is_pow2 else "✗"
            print(f"  [{status}] {param:30s} = {value:6d} {'(power of 2)' if is_pow2 else '(NOT power of 2 - ERROR!)'}")
            if not is_pow2:
                pow2_ok = False
    
    test_results.append(pow2_ok)
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(test_results)
    total = len(test_results)
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n[✓✓✓] ALL TESTS PASSED ✓✓✓\n")
        return 0
    else:
        print(f"\n[✗✗✗] {total - passed} TESTS FAILED ✗✗✗\n")
        return 1

if __name__ == '__main__':
    sys.exit(test_cache_parameters())
