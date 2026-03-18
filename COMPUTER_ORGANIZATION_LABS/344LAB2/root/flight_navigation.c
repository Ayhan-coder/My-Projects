#include <stdint.h>
#include <string.h>

// Constants
#define NUM_AIRPORTS 10
#define FUEL_CAPACITY 20000
#define FUEL_CONSUMPTION_RATE 2

// Distance matrix [NUM_AIRPORTS x NUM_AIRPORTS]
int32_t distances[NUM_AIRPORTS][NUM_AIRPORTS] = {
    {0,     2962,  5357,  7979,  8979,  9591,  8823,  10830,  8754,  6136},   // 0: Tokyo
    {2962,  0,     2564,  5920,  8006,  9631,  9710,  12970, 11664,  8947},   // 1: Hong Kong
    {5357,  2564,  0,     5845,  8678, 10881, 11552, 15339, 14101, 10789},   // 2: Singapore
    {7979,  5920,  5845,  0,     3028,  5497,  6919,  11001, 13400, 13712},   // 3: Dubai
    {8979,  8006,  8678,  3028,  0,     2488,  4114,  8027,  11002, 13021},   // 4: Istanbul
    {9591,  9631, 10881,  5497,  2488,  0,     1895,  5540,  8760,  11628},   // 5: Brussels
    {8823,  9710, 11552,  6919,  4114,  1895,  0,     4163,  6926,  9777},    // 6: Reykjavik
    {10830, 12970, 15339, 11001,  8027,  5540,  4163,  0,     3974,  8007},   // 7: New York
    {8754, 11664, 14101, 13400, 11002,  8760,  6926,  3974,  0,     4108},    // 8: Los Angeles
    {6136,  8947, 10789, 13712, 13021, 11628,  9777,  8007,  4108,  0}        // 9: Honolulu
};

// Direction matrix [NUM_AIRPORTS x NUM_AIRPORTS]
// SE=0, NE=1, SW=2, NW=3, self=-1
int8_t directions[NUM_AIRPORTS][NUM_AIRPORTS] = {
    {-1,  2,  2,  3,  3,  3,  3,  1,  1,  1},    // 0: Tokyo
    {1, -1,  2,  3,  3,  3,  3,  1,  1,  1},     // 1: Hong Kong
    {1,  1, -1,  3,  3,  3,  3,  3,  1,  1},     // 2: Singapore
    {0,  0,  0, -1,  3,  3,  3,  3,  3,  1},     // 3: Dubai
    {0,  0,  0,  0, -1,  3,  3,  3,  3,  1},     // 4: Istanbul
    {0,  0,  0,  0,  0, -1,  3,  3,  3,  3},     // 5: Brussels
    {0,  0,  0,  0,  0,  0, -1,  2,  3,  3},     // 6: Reykjavik
    {2,  2,  0,  0,  0,  0,  1, -1,  3,  3},     // 7: New York
    {2,  2,  2,  0,  0,  0,  0,  0, -1,  2},     // 8: Los Angeles
    {2,  2,  2,  2,  2,  0,  0,  0,  1, -1}      // 9: Honolulu
};

// Global state variables
int32_t current_fuel = FUEL_CAPACITY;
int32_t airport_supply[NUM_AIRPORTS] = {17000, 18000, 16000, 17000, 27500, 36500, 15500, 26000, 27000, 40000};
int32_t current_airport = 5;  // Starting at Brussels
int32_t flight_state = 1;     // 1 = journey ongoing, -1 = journey ended

// Output variables
int32_t distance_traveled = 0;
uint8_t flight_history[64] = {0};  // Keep history of flight with airport indices (store as bytes)
int32_t history_len = 0;

// Airport names for display
const char* airport_names[NUM_AIRPORTS] = {
    "Tokyo", "Hong Kong", "Singapore", "Dubai", "Istanbul",
    "Brussels", "Reykjavik", "New York", "Los Angeles", "Honolulu"
};

/**
 * flight_navigation - Find next airport to fly to based on distance and fuel towards west
 * @current_idx: Current airport index (0..NUM_AIRPORTS-1)
 * @fuel: Current fuel amount
 * 
 * Returns: Index of closest reachable westward airport, or -1 if none
 */
int32_t flight_navigation(int32_t current_idx, int32_t fuel)
{
    int32_t best_index = -1;
    int32_t best_distance = 0x7fffffff;  // MAX_INT

    for (int32_t j = 0; j < NUM_AIRPORTS; j++) {
        if (j == current_idx)
            continue;

        int8_t direction = directions[current_idx][j];
        
        // Check if westward (2=SW or 3=NW)
        if (direction != 2 && direction != 3)
            continue;

        int32_t dist = distances[current_idx][j];
        int32_t fuel_needed = dist * FUEL_CONSUMPTION_RATE;

        // Check if reachable
        if (fuel < fuel_needed)
            continue;

        // Check if this is the closest so far
        if (dist >= best_distance)
            continue;

        // Update best destination
        best_distance = dist;
        best_index = j;
    }

    return best_index;
}

/**
 * refuel - Refuel the airplane at the current airport
 * @airport_idx: Airport index
 * 
 * Returns: Updated current_fuel after refuel
 */
int32_t refuel(int32_t airport_idx)
{
    int32_t need = FUEL_CAPACITY - current_fuel;
    
    if (need <= 0)
        return current_fuel;

    int32_t supply = airport_supply[airport_idx];
    
    if (supply == 0)
        return current_fuel;

    int32_t take = (need < supply) ? need : supply;
    
    airport_supply[airport_idx] -= take;
    current_fuel += take;
    
    return current_fuel;
}

/**
 * execute_flight - Execute flight to next airport
 * @src_idx: Source airport index
 * @dst_idx: Destination airport index
 * 
 * Returns: 0 on success, -1 on failure
 */
int32_t execute_flight(int32_t src_idx, int32_t dst_idx)
{
    int32_t dist = distances[src_idx][dst_idx];
    int32_t fuel_needed = dist * FUEL_CONSUMPTION_RATE;

    // Check if reachable
    if (current_fuel < fuel_needed)
        return -1;

    // Deduct fuel
    current_fuel -= fuel_needed;

    // Update distance traveled
    distance_traveled += dist;

    // Update current airport
    current_airport = dst_idx;

    // Append to flight history
    if (history_len < 64) {
        flight_history[history_len] = (uint8_t)dst_idx;
        history_len++;
    }

    return 0;
}

/**
 * check_flight_state - Check if flight can continue or end
 * 
 * Returns: flight_state (1 = continue, -1 = ended)
 */
int32_t check_flight_state(void)
{
    // Call flight_navigation to check if any westward destination is reachable
    int32_t next_idx = flight_navigation(current_airport, current_fuel);

    if (next_idx == -1) {
        // No destination found -> end journey
        flight_state = -1;
        return -1;
    }

    // Reachable destination found -> continue journey
    flight_state = 1;
    return 1;
}

/**
 * main - Execute flight logic
 * 
 * Simulates the airplane journey, finding westward routes and refueling
 * until no more westward routes are available.
 */
int main(void)
{
    // Initialize distance_traveled and history_len
    distance_traveled = 0;
    history_len = 0;

    // Record starting airport in flight history
    flight_history[0] = (uint8_t)current_airport;  // Starting at Brussels (idx 5)
    history_len = 1;

    int32_t loop_count = 0;
    const int32_t MAX_ITERATIONS = 100;

    // Main simulation loop
    while (loop_count < MAX_ITERATIONS) {
        loop_count++;

        // Find next westward airport
        int32_t next_idx = flight_navigation(current_airport, current_fuel);

        if (next_idx == -1) {
            // No route found - exit
            break;
        }

        // Execute flight to next airport
        if (execute_flight(current_airport, next_idx) != 0) {
            // Flight failed - exit
            break;
        }

        // Refuel at new airport
        current_fuel = refuel(current_airport);

        // Check if journey can continue
        if (check_flight_state() == -1) {
            // Journey ended
            break;
        }
    }

    // Program end - all results are stored in:
    // - distance_traveled: Total distance traveled
    // - flight_history[]: Array of airport indices visited
    // - history_len: Number of stops made
    // - current_fuel: Remaining fuel
    // - current_airport: Final airport location

    return 0;
}
