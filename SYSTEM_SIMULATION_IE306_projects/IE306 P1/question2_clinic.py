"""
IE 306 Assignment 1 - Question 2
Medical Clinic Queuing Simulation (120 minutes)

System:
  - Deterministic interarrival = 12 min -> arrivals at t=0, 12, 24, ..., 108
  - Registration (receptionist): Uniform(2, 8) min
  - 40% -> Doctor 1, 60% -> Doctor 2
  - Treatment: Uniform(10, 20) min for both doctors
  - Doctor 1 is BUSY initially, Doctor 2 is IDLE
  - Simulate for 120 minutes

RN consumption per patient: RN1=registration, RN2=assignment, RN3=treatment
For Doctor 1's initial patient we consume one RN for remaining treatment time.
Extra RNs generated where the provided 27 are exhausted.
"""

import random as rng

# -- Given random numbers (extended if needed) -------------------------
random_numbers = [
    0.497, 0.380, 0.862, 0.020, 0.975, 0.391, 0.480,
    0.005, 0.959, 0.360, 0.593, 0.744, 0.069, 0.370,
    0.708, 0.176, 0.020, 0.714, 0.539, 0.928, 0.860,
    0.717, 0.861, 0.563, 0.543, 0.858, 0.537
]

rng.seed(42)  # reproducible extras
rn_idx = 0

def next_rn():
    global rn_idx
    if rn_idx < len(random_numbers):
        r = random_numbers[rn_idx]
    else:
        r = round(rng.random(), 3)
        random_numbers.append(r)  # track for display
    rn_idx += 1
    return r

# -- Distribution helpers ----------------------------------------------
def registration_time(rn):
    return 2 + 6 * rn          # Uniform(2, 8)

def treatment_time(rn):
    return 10 + 10 * rn        # Uniform(10, 20)

def assign_doctor(rn):
    return 1 if rn < 0.40 else 2

# -- Parameters --------------------------------------------------------
SIM_TIME = 120
INTERARRIVAL = 12

# -- Initial conditions ------------------------------------------------
receptionist_free_at = 0.0

# Doctor 1 is busy -> consume one RN for remaining treatment of initial patient
rn_init = next_rn()
init_trt = treatment_time(rn_init)
doctor_free_at = {1: init_trt, 2: 0.0}

print(f"Doctor 1 initially busy -> RN={rn_init:.3f}, treatment={init_trt:.2f}, "
      f"finishes at t={init_trt:.2f}")
print(f"Doctor 2 initially idle -> free at t=0.00\n")

# -- Generate arrivals ------------------------------------------------
arrival_times = [i * INTERARRIVAL for i in range(100) if i * INTERARRIVAL < SIM_TIME]
# arrivals: 0, 12, 24, 36, 48, 60, 72, 84, 96, 108 -> 10 patients

# -- Print header ------------------------------------------------------
hdr = (f"{'Pat':>3} | {'Arr':>6} | {'RN_R':>5} | {'RegDur':>6} | {'RegEnd':>6} | "
       f"{'RN_A':>5} | {'Doc':>3} | {'RN_T':>5} | {'TrtDur':>6} | "
       f"{'TrtBeg':>6} | {'QWait':>6} | {'TrtEnd':>6} | {'SysTime':>7}")
print(hdr)
print("-" * len(hdr))

patients = []

for i, arr in enumerate(arrival_times):
    pid = i + 1

    # Registration
    rn_r = next_rn()
    reg_dur = registration_time(rn_r)
    reg_start = max(arr, receptionist_free_at)
    reg_end = reg_start + reg_dur
    receptionist_free_at = reg_end

    # Doctor assignment
    rn_a = next_rn()
    doc = assign_doctor(rn_a)

    # Treatment
    rn_t = next_rn()
    trt_dur = treatment_time(rn_t)
    trt_start = max(reg_end, doctor_free_at[doc])
    q_wait = trt_start - reg_end    # time waiting in doctor queue
    trt_end = trt_start + trt_dur
    doctor_free_at[doc] = trt_end

    sys_time = trt_end - arr

    patients.append(dict(
        pid=pid, arr=arr, rn_r=rn_r, reg_dur=reg_dur, reg_end=reg_end,
        rn_a=rn_a, doc=doc, rn_t=rn_t, trt_dur=trt_dur,
        trt_start=trt_start, q_wait=q_wait, trt_end=trt_end, sys_time=sys_time
    ))

    print(f"{pid:>3} | {arr:>6.1f} | {rn_r:>5.3f} | {reg_dur:>6.2f} | {reg_end:>6.2f} | "
          f"{rn_a:>5.3f} | {'D'+str(doc):>3} | {rn_t:>5.3f} | {trt_dur:>6.2f} | "
          f"{trt_start:>6.2f} | {q_wait:>6.2f} | {trt_end:>6.2f} | {sys_time:>7.2f}")

print("-" * len(hdr))
print(f"Random numbers used: {rn_idx} (given: 27, generated: {max(0, rn_idx-27)})\n")

# -- Performance metrics ----------------------------------------------

# --- (i) Average number of patients in the clinic (L) ---
# Area-under-the-curve method: track number in system over time
events = []
# Initial patient with Doctor 1 (enters at t<0, departs at init_trt)
events.append((0.0, +1, 'init_enter'))
events.append((init_trt, -1, 'init_leave'))
for p in patients:
    events.append((p['arr'], +1, f"p{p['pid']}_arr"))
    events.append((p['trt_end'], -1, f"p{p['pid']}_dep"))

events.sort(key=lambda x: (x[0], x[1]))

T_end = max(SIM_TIME, max(e[0] for e in events))

n_in_sys = 0
last_t = 0.0
area_sys = 0.0

for t, delta, label in events:
    area_sys += n_in_sys * (t - last_t)
    n_in_sys += delta
    last_t = t
area_sys += n_in_sys * (T_end - last_t)

L = area_sys / T_end

# --- (ii) Average time spent in clinic (W) ---
W = sum(p['sys_time'] for p in patients) / len(patients)

# --- (iii) Utilization of each doctor ---
doc1_busy = init_trt   # initial patient
doc2_busy = 0.0
for p in patients:
    if p['doc'] == 1:
        doc1_busy += p['trt_dur']
    else:
        doc2_busy += p['trt_dur']

util1 = doc1_busy / T_end
util2 = doc2_busy / T_end

# --- (iv) Probability of 1 patient in the (doctor) queue ---
q_events = []
for p in patients:
    if p['q_wait'] > 0:
        q_events.append((p['reg_end'], +1))
        q_events.append((p['trt_start'], -1))
q_events.sort(key=lambda x: (x[0], x[1]))

q_len = 0
last_t = 0.0
time_q1 = 0.0

for t, delta in q_events:
    if q_len == 1:
        time_q1 += (t - last_t)
    q_len += delta
    last_t = t
if q_len == 1:
    time_q1 += (T_end - last_t)

prob_q1 = time_q1 / T_end

# -- Print results -----------------------------------------------------
print("=" * 50)
print("RESULTS")
print("=" * 50)
print(f"Observation period: 0 - {T_end:.2f} min")
print()
print(f"i)   Avg # patients in clinic (L)    : {L:.4f}")
print(f"ii)  Avg time in clinic (W)           : {W:.2f} min")
print(f"iii) Doctor 1 utilization             : {util1:.4f}  ({util1*100:.1f}%)")
print(f"     Doctor 2 utilization             : {util2:.4f}  ({util2*100:.1f}%)")
print(f"iv)  P(1 patient in queue)            : {prob_q1:.4f}  ({prob_q1*100:.1f}%)")
print(f"     (Time with queue=1: {time_q1:.2f} min)")
