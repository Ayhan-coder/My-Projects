import json
import numpy as np
import os
import glob

results_dir = "results"
json_files = glob.glob(os.path.join(results_dir, "*.json"))

for file in sorted(json_files):
    print(f"\n--- {os.path.basename(file)} ---")
    with open(file, 'r') as f:
        data = json.load(f)
    
    print(f"Parameters:")
    if "parameters" in data:
        for k, v in data["parameters"].items():
            print(f"  {k}: {v}")
    
    # Calculate MAE if theoretical is available
    if "analytical" in data and "cumulative_avg" in data:
        theo = np.array(data["analytical"])
        mean_rx = np.array(data["cumulative_avg"])
        
        valid_idx = ~np.isnan(theo) & ~np.isnan(mean_rx)
        if np.any(valid_idx):
            mae = np.mean(np.abs(theo[valid_idx] - mean_rx[valid_idx]))
            print(f"MAE: {mae:.2f}")
    
    if "cumulative_avg" in data and len(data["cumulative_avg"]) > 0:
        mean_rx = np.array(data["cumulative_avg"])
        final_val = np.nanmax(mean_rx)
        print(f"Final Max Value: {final_val:.2f}")
        
        if "time" in data:
            times = np.array(data["time"])
            idx = np.where(mean_rx >= 0.9 * final_val)[0]
            if len(idx) > 0:
                sat_time = times[idx[0]]
                print(f"90% Saturation Time: {sat_time:.4f} s")
            else:
                print("Did not reach 90% saturation.")
