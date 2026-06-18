**IE 306 — Systems Simulation**  
**Assignment 2: Coordinated Traffic Corridor Simulation**  
(Group Assignment — Teams of 3)

Spring 2026 | Due Date: April 7th, 2026

**Overview**

In this assignment you will build a discrete-event simulation of a two-intersection traffic corridor using SimPy. The corridor runs south-to-north (S→N); one-way cross-streets run west-to-east (W→E) at each intersection. Your model must faithfully represent signal phasing, turning movements, downstream blocking, transit signal priority for buses, and emergency-vehicle preemption. You will then design and run experiments comparing uncoordinated vs. coordinated signal control and analyze the impact of emergency-vehicle preemptions.

Choosing the right SimPy constructs for each aspect of the system is part of the assignment. Your report should justify your design decisions.

**1 System Description**

The corridor consists of two signalised intersections, A (upstream/south) and B (downstream/north), connected by a single directional link of length L = 300 m. Vehicles enter the system from the south at Intersection A and, if travelling through, proceed northward to Intersection B and exit north. Cross-street (W→E) traffic arrives from the west independently at each intersection.

**1.1 Corridor Geometry**

The corridor consists of two signalised intersections, A (upstream/south) and B (downstream/north), connected by a single directional link of length L = 300 m. Vehicles enter the system from the south at Intersection A and, if travelling through, proceed northward to Intersection B and exit north. Cross-street (W→E) traffic arrives from the west independently at each intersection.

**1.2 Signal Control**

Each intersection operates a two-phase fixed-time signal cycle:

**Table 1: Signal timing parameters.**

Parameter                  | Intersection A | Intersection B
---------------------------|----------------|---------------
Cycle length, C            | 90 s           | 90 s
N/S green, gNS             | 45 s           | 45 s
Amber / all-red clearance  | 4 s            | 4 s
W/E green, gWE             | 37 s           | 37 s

The phases cycle as: N/S green → amber → W/E green → amber → repeat. The amber interval (4 s) is an all-red clearance phase: it represents the real-world yellow-plus-all-red period during which the previous phase’s traffic clears the intersection before the next phase begins. During this interval no vehicles may enter the intersection from any direction. A vehicle that is already crossing (i.e. currently being served) finishes normally, but no new service may start.

**Coordination.** In the coordinated scenario, Intersection B’s N/S green phase starts with an offset ϕ relative to A’s N/S green start. Set ϕ equal to the free-flow travel time on the link:

ϕ = L / vf = 300 / 15 = 20 s

where vf = 15 m/s (54 km/h) is the free-flow speed.

In the uncoordinated scenario, both intersections start their cycles at time t = 0 with no offset (ϕ = 0).

**1.3 Vehicle Types and Arrivals**

Vehicles enter the corridor from the south approach of Intersection A. The combined arrival process is Poisson with rate λ = 900 veh/h. Each arrival is classified by Poisson splitting:

**Table 2: Vehicle type mix (southbound entry at A).**

Type       | Proportion | Notes
-----------|------------|--------------------------------------------
Car        | 85%        | Standard traffic
Bus        | 10%        | Non-preemptive queue priority (see §1.6)
Emergency  | 5%         | Preempts current signal phase (see §1.7)

W→E cross-traffic arrives from the west as an independent Poisson process at each intersection with rate λWE = 400 veh/h (all regular cars, normal priority).

**1.4 Turning Movements**

At each intersection, a northbound vehicle may turn off the corridor. Turning decisions are made independently upon arrival at the intersection according to the following proportions:

**Table 3: Turning proportions for northbound vehicles.**

Intersection | Straight (N) | Turn E
-------------|--------------|-------
A            | 0.70         | 0.30
B            | 0.80         | 0.20

Vehicles that turn E leave the corridor and do not need further modeling after exiting the intersection. Note that the demand arriving at Intersection B on the N/S corridor is not a fixed input—it depends on the turning proportions at A and the green time available there.

**1.5 Link Model and Downstream Blocking**

The link between A and B is modeled as a point queue with finite storage capacity. The capacity is derived from a jam density assumption:

• Link length: L = 300 m  
• Jam density: kj = 133 veh/km  
• Link capacity: Nmax = kj × L = 133 × 0.3 = 40 vehicles

Travel time on the link for a vehicle depends on the current occupancy n of the link. Use the following simple model:

ttravel(n) = (L / vf) × 1 / (1 − (n/Nmax)) = 20 × 1 / (1 − n/40) (seconds)

At n = 0 the travel time equals the free-flow time (20 s). As n approaches Nmax, travel time increases sharply, reflecting congestion.

**Downstream blocking rule.** A vehicle at Intersection A may only proceed northward onto the link when both conditions are satisfied simultaneously:

1. The N/S signal at A is green, and  
2. The current link occupancy n < Nmax.

If either condition is not met, the vehicle waits at Intersection A.

**1.6 Transit Signal Priority (Buses)**

Buses approaching an intersection are served before regular cars in the queue. Bus priority is non-preemptive: a bus moves ahead of waiting cars but does not interrupt a vehicle that is already being served (crossing the intersection).

**1.7 Emergency Vehicle Preemption**

When an emergency vehicle arrives at an intersection:

1. If the N/S phase is already green, the emergency vehicle proceeds with highest priority (ahead of all queued vehicles).  
2. If the N/S phase is not green (i.e. W/E green or amber), the emergency vehicle preempts the current phase:  
   • The current phase is immediately interrupted.  
   • A 4 s all-red clearance interval is inserted.  
   • N/S green is then activated for at least 10 s (the emergency service time) to allow the emergency vehicle (and any other N/S vehicles that can proceed) through.  
   • After the emergency vehicle clears, the signal returns to its regular cycle, resuming from the point in the cycle where it was interrupted.  
3. Emergency vehicles are not subject to downstream blocking — they always proceed onto the link regardless of occupancy (but still occupy a slot on the link).

**1.8 Intersection Service Time**

Each vehicle requires a short time to cross the intersection (start-up delay + clearing the intersection). Model this as an exponential random variable with mean µs = 2 s per vehicle. Only one vehicle per approach can cross at a time (i.e. the intersection approach acts as a single server).

**2 Simulation Requirements**

**2.1 Random Number Streams**

Use numpy.random.default_rng() with separate seeds for each random source (arrival process, vehicle classification, turning decisions, service times, link travel time noise, etc.). Document your seed assignments clearly.

**2.2 Warm-up and Run Length**

• Simulated duration: 2 hours (7 200 s) per replication.  
• Discard the first 15 minutes (900 s) as warm-up.  
• Number of replications: 20.  
• Report point estimates and 95% confidence intervals for all KPIs.

**3 Experiments**

Run the following three scenarios:

**Table 4: Experimental scenarios.**

Scenario | Description                        | Offset ϕ | Emergency Vehicles
---------|------------------------------------|----------|-------------------
1        | Uncoordinated, no emergencies      | 0 s      | Disabled
2        | Coordinated, no emergencies        | 20 s     | Disabled
3        | Coordinated, with emergencies      | 20 s     | Enabled

For each scenario, collect and report the following Key Performance Indicators (KPIs):

1. Average delay per vehicle (seconds)—separately for through-traffic (S→N) and W/E traffic.  
2. Maximum and average queue length at each approach (N/S at A, N/S at B, W/E at A, W/E at B).  
3. Throughput: vehicles per hour exiting northbound at B.  
4. Average link occupancy between A and B.  
5. Downstream blocking frequency: fraction of cycles in which at least one N/S vehicle at A was blocked due to link full.  
6. (Scenario 3 only) Number of preemption events, and average recovery time (time from end of emergency service until the signal controller returns to its regular cycle point).

**4 Deliverables**

1. Jupyter Notebook (.ipynb)—containing all simulation code, clearly structured and documented. Your code should be runnable end-to-end.

2. Report (PDF, max 10 pages excluding code appendix):  
   a. A brief description of your model logic and any assumptions you made beyond what is specified here.  
   b. A conceptual model diagram (activity diagram, flowchart, or similar) showing the lifecycle of a vehicle and the signal controller logic.  
   c. Results tables and/or figures for all three scenarios.  
   d. A comparative discussion: What is the effect of coordination? How do emergency preemptions degrade corridor performance? Which KPI is most affected?  
   e. A short paragraph on verification and validation: What sanity checks did you perform to convince yourselves the model is correct?

**5 Grading Rubric**

Component                                              | Points
-------------------------------------------------------|-------
Model correctness (signal logic, preemption, priority, blocking) | 35
Experimental design (seeds, warm-up, replications, CIs) | 15
Code quality (readability, structure, documentation)   | 15
Results and analysis (tables, figures, comparative discussion) | 25
Verification and validation discussion                 | 10
**Total**                                              | **100**

**Parameter Summary**

**Table 5: Complete parameter set.**

Parameter                  | Symbol | Value
---------------------------|--------|----------------------
Link length                | L      | 300 m
Free-flow speed            | vf     | 15 m/s (54 km/h)
Free-flow travel time      | L/vf   | 20 s
Jam density                | kj     | 133 veh/km
Link capacity              | Nmax   | 40 vehicles
Cycle length               | C      | 90 s
N/S green                  | gNS    | 45 s
Amber (clearance)          |        | 4 s
W/E green                  | gWE    | 37 s
Coordination offset        | ϕ      | 0 s or 20 s
S entry arrival rate       | λ      | 900 veh/h
W/E arrival rate           | λWE    | 400 veh/h (per intersection)
Car proportion             |        | 0.85
Bus proportion             |        | 0.10
Emergency proportion       |        | 0.05
Turning straight (A)       |        | 0.70
Turn E (A)                 |        | 0.30
Turning straight (B)       |        | 0.80
Turn E (B)                 |        | 0.20
Intersection service       | µs     | Exp(mean = 2 s)
Emergency service time     |        | 10 s (min green)
Emergency clearance        |        | 4 s (all-red)
Warm-up                    |        | 900 s
Run length                 |        | 7 200 s
Replications               |        | 20

Good luck!
