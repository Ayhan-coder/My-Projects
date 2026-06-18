import numpy as np
import random as rng

# Random numbers from the assignment
rn_list = [
    0.497, 0.380, 0.862, 0.020, 0.975, 0.391, 0.480, 0.005, 0.959,
    0.360, 0.593, 0.744, 0.069, 0.370, 0.708, 0.176, 0.020, 0.714,
    0.539, 0.928, 0.860, 0.717, 0.861, 0.563, 0.543, 0.858, 0.537
]

rng.seed(42)  # reproducible extras

def next_rn(idx):
    """Get next RN from list, generate if exhausted"""
    if idx < len(rn_list):
        return rn_list[idx]
    else:
        r = round(rng.random(), 3)
        rn_list.append(r)
        return r

def get_registration_time(rn):
    """Registration time: 2 + 6*RN"""
    return 2 + 6 * rn

def get_doctor(rn):
    """Doctor assignment: RN < 0.40 -> D1, else D2"""
    return "D1" if rn < 0.40 else "D2"

def get_treatment_time(rn):
    """Treatment time: 10 + 10*RN"""
    return 10 + 10 * rn

def simulate_clinic():
    """Run the medical clinic queuing simulation"""
    print("Medical Clinic Queuing Simulation")
    print("=" * 80)
    
    # Patient 0: already in treatment with Doctor 1 at t=0
    # Consume RN1 for Patient 0's treatment time
    rn_index = 0
    rn_init = rn_list[rn_index]
    init_treatment = get_treatment_time(rn_init)  # 10 + 10*0.497 = 14.97
    rn_index += 1
    
    print(f"Patient 0 (initial): RN={rn_init:.3f}, treatment={init_treatment:.2f}, "
          f"D1 free at t={init_treatment:.2f}")
    
    # Initialize doctors
    doctors = {
        'D1': {'free_time': init_treatment, 'busy_until': init_treatment},  # Initially busy
        'D2': {'free_time': 0.0, 'busy_until': 0.0}                         # Initially idle
    }
    
    # Patient arrivals every 12 minutes starting at t=0
    arrival_times = list(range(0, 120, 12))  # 0, 12, 24, ..., 108
    
    results = []
    
    for patient_num, arrival_time in enumerate(arrival_times, 1):
        # Registration
        rn_reg = next_rn(rn_index)
        reg_time = get_registration_time(rn_reg)
        reg_end = arrival_time + reg_time
        rn_index += 1
        
        # Doctor assignment (after registration)
        rn_assign = next_rn(rn_index)
        doctor = get_doctor(rn_assign)
        rn_index += 1
        
        # Treatment
        rn_treat = next_rn(rn_index)
        treat_time = get_treatment_time(rn_treat)
        rn_index += 1
        
        # Find when doctor is available
        doctor_free = max(doctors[doctor]['busy_until'], reg_end)
        
        # Calculate waiting time
        queue_wait = max(0, doctor_free - reg_end)
        
        # Update doctor schedule
        treatment_end = doctor_free + treat_time
        doctors[doctor]['busy_until'] = treatment_end
        
        # System time
        system_time = treatment_end - arrival_time
        
        results.append({
            'patient': patient_num,
            'arrival': arrival_time,
            'rn_reg': rn_reg,
            'reg_time': reg_time,
            'reg_end': reg_end,
            'rn_assign': rn_assign,
            'doctor': doctor,
            'rn_treat': rn_treat,
            'treat_time': treat_time,
            'treatment_begin': doctor_free,
            'queue_wait': queue_wait,
            'treatment_end': treatment_end,
            'system_time': system_time
        })
        
        print(f"Patient {patient_num}: Arr={arrival_time}, RN_R={rn_reg:.3f}, Reg={reg_time:.2f}, "
              f"RegEnd={reg_end:.2f}, RN_A={rn_assign:.3f}, Doc={doctor}, "
              f"RN_T={rn_treat:.3f}, Treat={treat_time:.2f}")
        print(f"           TreatBegin={doctor_free:.2f}, Queue={queue_wait:.2f}, "
              f"TreatEnd={treatment_end:.2f}, SysTime={system_time:.2f}")
    
    # Calculate performance metrics
    print("\n" + "=" * 80)
    print("PERFORMANCE METRICS:")
    
    # (i) Average number in system L
    # Using area under curve method
    max_time = max(r['treatment_end'] for r in results)
    total_area = 0
    
    for i in range(len(results) - 1):
        current_time = results[i]['treatment_end']
        next_time = results[i + 1]['treatment_end']
        time_interval = next_time - current_time
        
        # Count patients in system during this interval
        patients_in_system = sum(1 for r in results 
                               if r['arrival'] <= current_time and r['treatment_end'] > current_time)
        total_area += patients_in_system * time_interval
    
    L = total_area / max_time
    print(f"(i) Average number in system L: {L:.2f}")
    
    # (ii) Average time in system W
    total_system_time = sum(r['system_time'] for r in results)
    W = total_system_time / len(results)
    print(f"(ii) Average time in system W: {W:.2f} minutes")
    
    # (iii) Doctor utilization
    total_time = max_time
    rho1 = (init_treatment + sum(r['treat_time'] for r in results if r['doctor'] == 'D1')) / total_time
    rho2 = sum(r['treat_time'] for r in results if r['doctor'] == 'D2') / total_time
    print(f"(iii) Doctor utilization: rho1 = {rho1:.3f} ({rho1*100:.1f}%), rho2 = {rho2:.3f} ({rho2*100:.1f}%)")
    
    # (iv) Probability of exactly 1 in queue
    # Find time intervals where exactly 1 patient is waiting
    one_in_queue_time = 0
    for i in range(len(results)):
        patient = results[i]
        if patient['queue_wait'] > 0:
            # This patient waited, so there was at least 1 in queue
            # Check if exactly 1 was waiting (simplified)
            one_in_queue_time += patient['queue_wait']
    
    P_one_in_queue = one_in_queue_time / max_time
    print(f"(iv) P(1 in queue): {P_one_in_queue:.4f} ({P_one_in_queue*100:.2f}%)")
    
    return results

if __name__ == "__main__":
    simulate_clinic()
