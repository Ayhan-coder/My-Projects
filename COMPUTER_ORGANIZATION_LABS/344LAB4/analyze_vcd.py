#!/usr/bin/env python3
"""
Simple VCD analyzer for Part I of the assignment
Extracts PCF and InstrD values at different time points
"""

def parse_vcd_simple(filename):
    """Parse VCD file and extract signal values"""
    signals = {}
    signal_map = {}
    current_time = 0
    timeline = {}
    
    with open(filename, 'r') as f:
        in_definitions = True
        
        for line in f:
            line = line.strip()
            
            # Parse signal definitions
            if '$var' in line and in_definitions:
                parts = line.split()
                if len(parts) >= 5:
                    signal_name = parts[4]
                    signal_code = parts[3]
                    if signal_name in ['PCF', 'InstrD', 'PCD', 'PCE', 'clk']:
                        signal_map[signal_code] = signal_name
                        signals[signal_name] = '0'
            
            # End of definitions
            if '$enddefinitions' in line:
                in_definitions = False
                continue
            
            # Parse time stamps
            if line.startswith('#') and not in_definitions:
                current_time = int(line[1:])
                if current_time not in timeline:
                    timeline[current_time] = signals.copy()
            
            # Parse signal changes
            elif not in_definitions and line:
                if line[0] in ['0', '1'] and len(line) > 1:
                    # Single bit signal
                    value = line[0]
                    code = line[1:]
                    if code in signal_map:
                        signals[signal_map[code]] = value
                        if current_time in timeline:
                            timeline[current_time][signal_map[code]] = value
                            
                elif line[0] == 'b' and ' ' in line:
                    # Multi-bit signal
                    parts = line.split()
                    value = parts[0][1:]  # Remove 'b' prefix
                    code = parts[1]
                    if code in signal_map:
                        # Convert binary to hex
                        try:
                            hex_value = hex(int(value, 2))[2:].upper().zfill(8)
                            signals[signal_map[code]] = hex_value
                            if current_time in timeline:
                                timeline[current_time][signal_map[code]] = hex_value
                        except:
                            signals[signal_map[code]] = value
                            if current_time in timeline:
                                timeline[current_time][signal_map[code]] = value
    
    return timeline

def main():
    print("=" * 80)
    print("VCD WAVEFORM ANALYSIS - Part I: Tracking Instructions")
    print("=" * 80)
    
    timeline = parse_vcd_simple('testbench.vcd')
    
    # Sort times
    times = sorted(timeline.keys())
    
    print("\nTime | clk | PCF        | PCD        | PCE        | InstrD")
    print("-" * 80)
    
    for t in times[::10]:  # Show every 10th timestamp to keep it manageable
        data = timeline[t]
        clk = data.get('clk', '?')
        pcf = data.get('PCF', '????????')
        pcd = data.get('PCD', '????????')
        pce = data.get('PCE', '????????')
        instrd = data.get('InstrD', '????????')
        
        print(f"{t:4d} |  {clk}  | 0x{pcf} | 0x{pcd} | 0x{pce} | 0x{instrd}")
    
    print("\n" + "=" * 80)
    print("KEY OBSERVATIONS FOR PART I:")
    print("=" * 80)
    print("""
1. Pick a cycle (e.g., between t=310ps and t=320ps)
2. Note the value of PCF (Program Counter Fetch)
3. Note the value of InstrD (Instruction Decoded)
4. Compare InstrD with the objdump file at the PC address
5. Observe that PCD = PCF from previous cycle (1-cycle pipeline delay)
    """)
    
    # Show specific interesting cycles
    print("\nDETAILED VIEW OF KEY CYCLES:")
    print("-" * 80)
    for t in range(260, 420, 10):
        if t in timeline:
            data = timeline[t]
            clk = data.get('clk', '?')
            pcf = data.get('PCF', '????????')
            instrd = data.get('InstrD', '????????')
            print(f"t={t}ps: clk={clk} PCF=0x{pcf} InstrD=0x{instrd}")

if __name__ == "__main__":
    main()
