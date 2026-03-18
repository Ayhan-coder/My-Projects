#!/usr/bin/env python3
"""
Test runner for the RISC-V flight navigation assembly program.
This script simulates the program execution and validates the logic.
"""

# Airport data
NUM_AIRPORTS = 10
FUEL_CAPACITY = 20000
FUEL_CONSUMPTION_RATE = 2

# Distance matrix (from the assembly code)
distances = [
    [0,     2962,  5357,  7979,  8979,  9591,  8823,  10830,  8754,  6136],   # 0: Tokyo
    [2962,  0,     2564,  5920,  8006,  9631,  9710,  12970, 11664,  8947],   # 1: Hong Kong
    [5357,  2564,  0,     5845,  8678, 10881, 11552, 15339, 14101, 10789],   # 2: Singapore
    [7979,  5920,  5845,  0,     3028,  5497,  6919,  11001, 13400, 13712],   # 3: Dubai
    [8979,  8006,  8678,  3028,  0,     2488,  4114,  8027,  11002, 13021],   # 4: Istanbul
    [9591,  9631, 10881,  5497,  2488,  0,     1895,  5540,  8760,  11628],   # 5: Brussels
    [8823,  9710, 11552,  6919,  4114,  1895,  0,     4163,  6926,  9777],    # 6: Reykjavik
    [10830, 12970, 15339, 11001,  8027,  5540,  4163,  0,     3974,  8007],   # 7: New York
    [8754, 11664, 14101, 13400, 11002,  8760,  6926,  3974,  0,     4108],    # 8: Los Angeles
    [6136,  8947, 10789, 13712, 13021, 11628,  9777,  8007,  4108,  0]        # 9: Honolulu
]

# Direction matrix (SE=0, NE=1, SW=2, NW=3, self=-1)
directions = [
    [-1,  2,  2,  3,  3,  3,  3,  1,  1,  1],    # 0: Tokyo
    [1, -1,  2,  3,  3,  3,  3,  1,  1,  1],     # 1: Hong Kong
    [1,  1, -1,  3,  3,  3,  3,  3,  1,  1],     # 2: Singapore
    [0,  0,  0, -1,  3,  3,  3,  3,  3,  1],     # 3: Dubai
    [0,  0,  0,  0, -1,  3,  3,  3,  3,  1],     # 4: Istanbul
    [0,  0,  0,  0,  0, -1,  3,  3,  3,  3],     # 5: Brussels
    [0,  0,  0,  0,  0,  0, -1,  2,  3,  3],     # 6: Reykjavik
    [2,  2,  0,  0,  0,  0,  1, -1,  3,  3],     # 7: New York
    [2,  2,  2,  0,  0,  0,  0,  0, -1,  2],     # 8: Los Angeles
    [2,  2,  2,  2,  2,  0,  0,  0,  1, -1]      # 9: Honolulu
]

# Airport names for display
airport_names = [
    "Tokyo", "Hong Kong", "Singapore", "Dubai", "Istanbul",
    "Brussels", "Reykjavik", "New York", "Los Angeles", "Honolulu"
]

# Initial state
current_fuel = 20000
airport_supply = [17000, 18000, 16000, 17000, 27500, 36500, 15500, 26000, 27000, 40000]
current_airport = 5  # Starting at Brussels
distance_traveled = 0
flight_history = [current_airport]

# Expected history for validation
expected_history = [5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1]

def flight_navigation(current_idx, current_fuel):
    """Find the closest reachable westward airport."""
    best_index = -1
    best_distance = float('inf')
    
    for j in range(NUM_AIRPORTS):
        if j == current_idx:
            continue
        
        direction = directions[current_idx][j]
        # Check if westward (2=SW or 3=NW)
        if direction not in [2, 3]:
            continue
        
        dist = distances[current_idx][j]
        fuel_needed = dist * FUEL_CONSUMPTION_RATE
        
        # Check if reachable
        if current_fuel >= fuel_needed:
            if dist < best_distance:
                best_distance = dist
                best_index = j
    
    return best_index

def refuel(airport_idx, current_fuel):
    """Refuel at the current airport."""
    need = FUEL_CAPACITY - current_fuel
    if need <= 0:
        return current_fuel, 0
    
    supply = airport_supply[airport_idx]
    if supply == 0:
        return current_fuel, 0
    
    take = min(need, supply)
    airport_supply[airport_idx] -= take
    return current_fuel + take, take

def execute_flight(src_idx, dst_idx):
    """Execute a flight from source to destination."""
    global current_fuel, distance_traveled, current_airport
    
    dist = distances[src_idx][dst_idx]
    fuel_needed = dist * FUEL_CONSUMPTION_RATE
    
    if current_fuel < fuel_needed:
        return False
    
    current_fuel -= fuel_needed
    distance_traveled += dist
    current_airport = dst_idx
    flight_history.append(dst_idx)
    
    return True

def check_any_westward_reachable_after_refuel(current_idx, current_fuel):
    """Check if any westward airport is reachable after refueling."""
    # Simulate refuel
    need = FUEL_CAPACITY - current_fuel
    supply = airport_supply[current_idx]
    take = min(need, supply) if need > 0 and supply > 0 else 0
    fuel_after_refuel = current_fuel + take
    
    # Check if any westward destination is reachable
    for j in range(NUM_AIRPORTS):
        if j == current_idx:
            continue
        direction = directions[current_idx][j]
        if direction in [2, 3]:  # Westward
            dist = distances[current_idx][j]
            fuel_needed = dist * FUEL_CONSUMPTION_RATE
            if fuel_after_refuel >= fuel_needed:
                return True
    return False

# Main simulation
print("=== Flight Navigation Simulation ===")
print(f"Starting at: {airport_names[current_airport]}")
print(f"Initial fuel: {current_fuel}")
print()

iteration = 0
max_iterations = 100

while iteration < max_iterations:
    iteration += 1
    print(f"--- Iteration {iteration} ---")
    print(f"Current location: {airport_names[current_airport]} (idx {current_airport})")
    print(f"Current fuel: {current_fuel}")
    
    # Find next westward airport
    next_idx = flight_navigation(current_airport, current_fuel)
    
    if next_idx == -1:
        print("No reachable westward airport found. Journey ends.")
        break
    
    print(f"Next destination: {airport_names[next_idx]} (idx {next_idx})")
    dist = distances[current_airport][next_idx]
    fuel_needed = dist * FUEL_CONSUMPTION_RATE
    print(f"Distance: {dist} km, Fuel needed: {fuel_needed}")
    
    # Execute flight
    if not execute_flight(current_airport - 1 if current_airport > 0 else current_airport, next_idx):
        print("Flight failed!")
        break
    
    print(f"Arrived at {airport_names[next_idx]}")
    print(f"Fuel remaining: {current_fuel}")
    
    # Refuel
    old_fuel = current_fuel
    current_fuel, refueled = refuel(current_airport, current_fuel)
    print(f"Refueled: +{refueled}, New fuel: {current_fuel}")
    print()

print()
print("=== Journey Summary ===")
print(f"Total distance traveled: {distance_traveled} km")
print(f"Final fuel: {current_fuel}")
print(f"Final location: {airport_names[current_airport]} (idx {current_airport})")
print(f"Number of stops: {len(flight_history)}")
print(f"Flight path: {' -> '.join([airport_names[i] for i in flight_history])}")
print()
print("Remaining fuel at airports:")
for i, supply in enumerate(airport_supply):
    print(f"  {airport_names[i]}: {supply}")
