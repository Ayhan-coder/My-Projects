.global _start

.equ NUM_AIRPORTS, 10               # Total number of airports
.equ FUEL_CAPACITY, 20000           # Maximum fuel capacity of the airplane
.equ FUEL_CONSUMPTION_RATE, 2       # Fuel consumption rate of the plane

.section .rodata
# Distance matrix [NUM_AIRPORTS x NUM_AIRPORTS]
# Each row corresponds to an airport, and each column corresponds to the distance to another airport
# Self-distance is omitted (0)

distances:

    .word  0,     2962,  5357,  7979,  8979,  9591,  8823,  10830,  8754,  6136    # 0: Tokyo
    .word  2962,  0,     2564,  5920,  8006,  9631,  9710,  12970, 11664,  8947    # 1: Hong Kong
    .word  5357,  2564,  0,     5845,   8678, 10881, 11552, 15339, 14101, 10789    # 2: Singapore
    .word  7979,  5920,  5845,  0,     3028,  5497,  6919,  11001, 13400, 13712    # 3: Dubai
    .word  8979,  8006,  8678,  3028,  0,     2488,  4114,  8027,  11002, 13021    # 4: Istanbul
    .word  9591,  9631,  10881, 5497,  2488,  0,     1895,  5540,  8760,  11628    # 5: Brussels
    .word  8823,  9710,  11552, 6919,  4114,  1895,  0,     4163,  6926,  9777     # 6: Reykjavik
    .word 10830, 12970,  15339, 11001,  8027, 5540,  4163,  0,     3974,  8007     # 7: New York
    .word  8754, 11664,  14101, 13400, 11002,  8760, 6926,  3974,  0,     4108     # 8: Los Angeles
    .word  6136,  8947,  10789, 13712, 13021, 11628, 9777,  8007,  4108,  0        # 9: Honolulu

# Direction matrix [NUM_AIRPORTS x NUM_AIRPORTS]
# SE=0, NE=1, SW=2, NW=3, self=-1

directions:

    .byte -1,  2,  2,  3,  3,  3,  3,  1,  1,  1    # 0: Tokyo
    .byte  1, -1,  2,  3,  3,  3,  3,  1,  1,  1    # 1: Hong Kong
    .byte  1,  1, -1,  3,  3,  3,  3,  3,  1,  1    # 2: Singapore
    .byte  0,  0,  0, -1,  3,  3,  3,  3,  3,  1    # 3: Dubai
    .byte  0,  0,  0,  0, -1,  3,  3,  3,  3,  1    # 4: Istanbul
    .byte  0,  0,  0,  0,  0, -1,  3,  3,  3,  3    # 5: Brussels
    .byte  0,  0,  0,  0,  0,  0, -1,  2,  3,  3    # 6: Reykjavik
    .byte  2,  2,  0,  0,  0,  0,  1, -1,  3,  3    # 7: New York
    .byte  2,  2,  2,  0,  0,  0,  0,  0, -1,  2    # 8: Los Angeles
    .byte  2,  2,  2,  2,  2,  0,  0,  0,  1, -1    # 9: Honolulu

.section .data

current_fuel: .word 20000
airport_supply: .word 17000, 18000, 16000, 17000, 27500, 36500, 15500, 26000, 27000, 40000
current_airport: .word 5            # Starting at Brussels
flight_state: .word 1               # 1 = journey ongoing, -1 = journey ended


.section .bss

distance_traveled: .space 4         # Total distance traveled
flight_history: .space 64           # Keep history of flight with airport indices (store as bytes)
history_len: .space 4               # Length of flight history



.section .text

# -------------------------------------------------------------
# Helper macro: rd = rs * 10 
# -------------------------------------------------------------
.macro MUL10 rd, rs
    slli    t0, \rs, 3              # t0 = rs * 8
    slli    t1, \rs, 1              # t1 = rs * 2
    add     \rd, t0, t1             # rd = t0 + t1 = rs*10
.endm

   
flight_navigation:
    # Finds next airport to fly to based on distance and fuel towards west
    # Args:
    #   a0 = current_idx (0..NUM_AIRPORTS-1)
    #   a1 = &distances (word matrix)
    #   a2 = &directions (byte matrix)
    #   a3 = current_fuel (value)
    # Returns:
    #   a0 = index of closest reachable westward airport, or -1 if none
    
    addi    sp, sp, -16                 # Allocate stack frame
    sw      ra, 12(sp)                  # Save return address
    sw      s0, 8(sp)                   # Save s0 (current_idx)
    sw      s1, 4(sp)                   # Save s1 (best_index)

    mv      s0, a0                      # s0 = current_idx
    li      s1, -1                      # best_index = -1 (no destination found yet)
    li      t5, 0x7fffffff              # best_distance = MAX_INT

    # Compute row offset: row_off = current_idx * 10
    MUL10   t0, s0                      # t0 = row_off (in elements)

    # Calculate distance row address: dist_row_addr = distances + (row_off * 4)
    slli    t1, t0, 2                   # t1 = row_off * 4 (word size)
    add     t2, a1, t1                  # t2 = dist_row_addr

    # Calculate direction row address: dir_row_addr = directions + row_off
    add     t3, a2, t0                  # t3 = dir_row_addr

    li      t4, 0                       # j = 0 (loop counter)

.fn_loop_j:
    li      t1, NUM_AIRPORTS            # Load NUM_AIRPORTS constant
    bge     t4, t1, .fn_done            # if j >= NUM_AIRPORTS, exit loop

    beq     t4, s0, .fn_next_j          # Skip if j == current_idx (self)

    # Load direction: dir = dir_row_addr[j]
    add     t6, t3, t4                  # t6 = &dir_row_addr[j]
    lbu     a4, 0(t6)                   # a4 = direction value

    # Check if westward: dir == 2 (SW) or dir == 3 (NW)
    li      a5, 2                       # Check for SW
    beq     a4, a5, .fn_check_reach     # If SW, check reachability
    li      a5, 3                       # Check for NW
    bne     a4, a5, .fn_next_j          # If not NW, skip to next

.fn_check_reach:
    # Load distance: dist = dist_row_addr[j]
    slli    a6, t4, 2                   # a6 = j * 4 (word offset)
    add     a6, t2, a6                  # a6 = &dist_row_addr[j]
    lw      a6, 0(a6)                   # a6 = distance value

    # Calculate fuel needed: fuel_needed = dist * FUEL_CONSUMPTION_RATE (=2)
    slli    a7, a6, 1                   # a7 = dist * 2

    # Check if reachable: current_fuel >= fuel_needed
    blt     a3, a7, .fn_next_j          # If insufficient fuel, skip

    # Check if this is the closest so far
    bge     a6, t5, .fn_next_j          # If not closer, skip

    # Update best destination
    mv      t5, a6                      # best_distance = dist
    mv      s1, t4                      # best_index = j

.fn_next_j:
    addi    t4, t4, 1                   # j++
    j       .fn_loop_j                  # Continue loop

.fn_done:
    mv      a0, s1                      # Return best_index (or -1 if none)

    lw      s1, 4(sp)                   # Restore s1
    lw      s0, 8(sp)                   # Restore s0
    lw      ra, 12(sp)                  # Restore return address
    addi    sp, sp, 16                  # Deallocate stack frame

    # a0 = closest westward airport index
    ret


refuel:
    # Refuel the airplane at the current airport
    # Args:
    #   a0 = airport_idx
    #   a1 = &airport_supply (word array)
    #   a2 = current_fuel (value)
    # Returns:
    #   a0 = updated current_fuel after refuel
    
    addi    sp, sp, -16                 # Allocate stack frame
    sw      ra, 12(sp)                  # Save return address
    sw      s0, 8(sp)                   # Save s0 (airport_idx)
    sw      s1, 4(sp)                   # Save s1 (current_fuel)

    mv      s0, a0                      # s0 = airport_idx
    mv      s1, a2                      # s1 = current_fuel

    # Calculate fuel needed: need = FUEL_CAPACITY - current_fuel
    li      t0, FUEL_CAPACITY           # t0 = FUEL_CAPACITY
    sub     t0, t0, s1                  # t0 = need
    bge     x0, t0, .rf_done_ret_cur    # If need <= 0, already full

    # Load airport supply: supply = airport_supply[idx]
    slli    t1, s0, 2                   # t1 = idx * 4 (word offset)
    add     t2, a1, t1                  # t2 = &airport_supply[idx]
    lw      t3, 0(t2)                   # t3 = supply

    beqz    t3, .rf_done_ret_cur        # If supply == 0, no refuel possible

    # Calculate amount to take: take = min(need, supply)
    blt     t0, t3, .rf_take_need       # If need < supply, take = need
    mv      t4, t3                      # Otherwise, take = supply
    j       .rf_apply
.rf_take_need:
    mv      t4, t0                      # take = need

.rf_apply:
    add     s1, s1, t4                  # current_fuel += take
    sub     t3, t3, t4                  # supply -= take
    sw      t3, 0(t2)                   # Store updated supply back

.rf_done_ret_cur:
    mv      a0, s1                      # Return updated fuel

    lw      s1, 4(sp)                   # Restore s1
    lw      s0, 8(sp)                   # Restore s0
    lw      ra, 12(sp)                  # Restore return address
    addi    sp, sp, 16                  # Deallocate stack frame

    ret

execute_flight:
    # Execute flight to next airport
    # Change current_airport, update current_fuel, distance_traveled
    # Args:
    #   a0 = src_idx
    #   a1 = dst_idx
    #   a2 = &distances
    #   a3 = &current_fuel (address)
    #   a4 = &distance_traveled (address)
    #   a5 = &current_airport (address)
    #   a6 = &flight_history (address)
    #   a7 = &history_len (address)
    # Returns:
    #   a0 = 0 on success, -1 on failure
    
    addi    sp, sp, -24                 # Allocate stack frame
    sw      ra, 20(sp)                  # Save return address
    sw      s0, 16(sp)                  # Save s0 (src_idx)
    sw      s1, 12(sp)                  # Save s1 (dst_idx)

    mv      s0, a0                      # s0 = src_idx
    mv      s1, a1                      # s1 = dst_idx

    # Get distance: distance = distances[src*10 + dst]
    MUL10   t0, s0                      # t0 = src * 10
    add     t0, t0, s1                  # t0 = src*10 + dst (element index)
    slli    t1, t0, 2                   # t1 = (src*10 + dst) * 4 (word offset)
    add     t1, a2, t1                  # t1 = &distances[src*10 + dst]
    lw      t2, 0(t1)                   # t2 = distance

    # Calculate fuel needed: fuel_needed = distance * FUEL_CONSUMPTION_RATE (=2)
    slli    t3, t2, 1                   # t3 = distance * 2

    # Load current fuel
    lw      t4, 0(a3)                   # t4 = current_fuel

    # Check if reachable (defensive check)
    blt     t4, t3, .xf_fail            # If insufficient fuel, fail

    # Deduct fuel: current_fuel -= fuel_needed
    sub     t4, t4, t3                  # t4 = current_fuel - fuel_needed
    sw      t4, 0(a3)                   # Store updated current_fuel

    # Update distance traveled: distance_traveled += distance
    lw      t5, 0(a4)                   # t5 = distance_traveled
    add     t5, t5, t2                  # t5 += distance
    sw      t5, 0(a4)                   # Store updated distance_traveled

    # Update current airport: current_airport = dst_idx
    sw      s1, 0(a5)                   # current_airport = dst_idx

    # Append to flight history: flight_history[history_len] = dst_idx (byte)
    lw      t6, 0(a7)                   # t6 = history_len
    li      t0, 64                      # Max history size
    bge     t6, t0, .xf_skip_hist       # If history full, skip

    add     t5, a6, t6                  # t5 = &flight_history[history_len]
    andi    t4, s1, 0xFF                # t4 = dst_idx as byte
    sb      t4, 0(t5)                   # Store dst_idx in history
    addi    t6, t6, 1                   # history_len++
    sw      t6, 0(a7)                   # Store updated history_len

.xf_skip_hist:
    li      a0, 0                       # Return success
    j       .xf_done

.xf_fail:
    li      a0, -1                      # Return failure

.xf_done:
    lw      s1, 12(sp)                  # Restore s1
    lw      s0, 16(sp)                  # Restore s0
    lw      ra, 20(sp)                  # Restore return address
    addi    sp, sp, 24                  # Deallocate stack frame

    ret


check_flight_state:
    # Check if flight can continue or end
    # Args:
    #   a0 = current_idx
    #   a1 = &distances
    #   a2 = &directions
    #   a3 = current_fuel (value)
    #   a4 = &flight_state (address)
    # Returns:
    #   a0 = flight_state (1 = continue, -1 = ended)
    
    addi    sp, sp, -16                 # Allocate stack frame
    sw      ra, 12(sp)                  # Save return address
    sw      s0, 8(sp)                   # Save s0 (flight_state pointer)

    mv      s0, a4                      # s0 = &flight_state (preserve across call)

    # Call flight_navigation to check if any westward destination is reachable
    call    flight_navigation           # a0 = next_idx or -1

    # Check result
    li      t0, -1                      # Load -1 for comparison
    beq     a0, t0, .cfs_end            # If no destination found, end journey

    # Reachable destination found -> continue journey
    li      t1, 1                       # flight_state = 1 (continue)
    sw      t1, 0(s0)                   # Store flight_state
    mv      a0, t1                      # Return 1
    j       .cfs_done

.cfs_end:
    li      t1, -1                      # flight_state = -1 (ended)
    sw      t1, 0(s0)                   # Store flight_state
    mv      a0, t1                      # Return -1

.cfs_done:
    lw      s0, 8(sp)                   # Restore s0
    lw      ra, 12(sp)                  # Restore return address
    addi    sp, sp, 16                  # Deallocate stack frame

    ret


_start:
    # Initialize and implement flight logic
    
    # Zero out distance_traveled
    li      t0, 0                       # t0 = 0
    la      t1, distance_traveled       # t1 = &distance_traveled
    sw      t0, 0(t1)                   # distance_traveled = 0
    
    # Zero out history_len
    la      t2, history_len             # t2 = &history_len
    sw      t0, 0(t2)                   # history_len = 0

    # Record starting airport in flight history
    la      t3, current_airport         # t3 = &current_airport
    lw      t4, 0(t3)                   # t4 = starting airport index
    la      t5, flight_history          # t5 = &flight_history
    lw      t6, 0(t2)                   # t6 = history_len (currently 0)
    add     t1, t5, t6                  # t1 = &flight_history[0]
    andi    t4, t4, 0xFF                # Mask to byte
    sb      t4, 0(t1)                   # flight_history[0] = starting airport
    addi    t6, t6, 1                   # history_len++
    sw      t6, 0(t2)                   # Store updated history_len

    # Save all pointers on stack for main loop
    # Stack layout:
    # sp+0:  &distances
    # sp+4:  &directions
    # sp+8:  &current_fuel
    # sp+12: &distance_traveled
    # sp+16: &current_airport
    # sp+20: &flight_history
    # sp+24: &history_len
    # sp+28: &flight_state
    # sp+32: &airport_supply
    # sp+36: loop_counter
    # sp+40-47: padding (for alignment)
    
    addi    sp, sp, -48                 # Allocate stack space
    
    la      t0, distances
    sw      t0, 0(sp)
    la      t0, directions
    sw      t0, 4(sp)
    la      t0, current_fuel
    sw      t0, 8(sp)
    la      t0, distance_traveled
    sw      t0, 12(sp)
    la      t0, current_airport
    sw      t0, 16(sp)
    la      t0, flight_history
    sw      t0, 20(sp)
    la      t0, history_len
    sw      t0, 24(sp)
    la      t0, flight_state
    sw      t0, 28(sp)
    la      t0, airport_supply
    sw      t0, 32(sp)
    li      t0, 0
    sw      t0, 36(sp)                  # loop_counter = 0

.main_loop:
    # Load all pointers from stack
    lw      s0, 0(sp)                   # s0 = &distances
    lw      s1, 4(sp)                   # s1 = &directions
    lw      s2, 8(sp)                   # s2 = &current_fuel
    lw      s3, 12(sp)                  # s3 = &distance_traveled
    lw      s4, 16(sp)                  # s4 = &current_airport
    lw      s5, 20(sp)                  # s5 = &flight_history
    lw      s6, 24(sp)                  # s6 = &history_len
    lw      s7, 28(sp)                  # s7 = &flight_state
    lw      s8, 32(sp)                  # s8 = &airport_supply
    
    # Get current state
    lw      a0, 0(s4)                   # a0 = current_idx
    mv      a1, s0                      # a1 = &distances
    mv      a2, s1                      # a2 = &directions
    lw      a3, 0(s2)                   # a3 = current_fuel (value)

    # Find next westward reachable airport
    call    flight_navigation           # a0 = next_idx or -1

    li      t1, -1
    beq     a0, t1, .no_route           # If no route found, exit

    # Route found - execute flight
    # Reload pointers
    lw      s0, 0(sp)                   # s0 = &distances
    lw      s2, 8(sp)                   # s2 = &current_fuel
    lw      s3, 12(sp)                  # s3 = &distance_traveled
    lw      s4, 16(sp)                  # s4 = &current_airport
    lw      s5, 20(sp)                  # s5 = &flight_history
    lw      s6, 24(sp)                  # s6 = &history_len
    
    mv      a1, a0                      # a1 = dst_idx (from flight_navigation)
    lw      a0, 0(s4)                   # a0 = src_idx (current_airport)
    mv      a2, s0                      # a2 = &distances
    mv      a3, s2                      # a3 = &current_fuel
    mv      a4, s3                      # a4 = &distance_traveled
    mv      a5, s4                      # a5 = &current_airport
    mv      a6, s5                      # a6 = &flight_history
    mv      a7, s6                      # a7 = &history_len

    call    execute_flight              # a0 = 0 on success

    li      t2, 0
    bne     a0, t2, .no_route           # If flight failed, exit

    # Flight successful - refuel at new airport
    # Reload pointers
    lw      s2, 8(sp)                   # s2 = &current_fuel
    lw      s4, 16(sp)                  # s4 = &current_airport
    lw      s8, 32(sp)                  # s8 = &airport_supply
    
    lw      a0, 0(s4)                   # a0 = current airport_idx
    mv      a1, s8                      # a1 = &airport_supply
    lw      a2, 0(s2)                   # a2 = current_fuel (value)
    call    refuel                      # a0 = updated fuel
    sw      a0, 0(s2)                   # Store updated fuel

    # Check if journey can continue
    # Reload pointers
    lw      s0, 0(sp)                   # s0 = &distances
    lw      s1, 4(sp)                   # s1 = &directions
    lw      s2, 8(sp)                   # s2 = &current_fuel
    lw      s4, 16(sp)                  # s4 = &current_airport
    lw      s7, 28(sp)                  # s7 = &flight_state
    
    lw      a0, 0(s4)                   # a0 = current_idx
    mv      a1, s0                      # a1 = &distances
    mv      a2, s1                      # a2 = &directions
    lw      a3, 0(s2)                   # a3 = current_fuel (value)
    mv      a4, s7                      # a4 = &flight_state
    call    check_flight_state          # a0 = flight_state

    li      t3, -1
    beq     a0, t3, .end                # If journey ended, exit

    # Safety check: prevent infinite loops
    lw      t4, 36(sp)                  # t4 = loop_counter
    addi    t4, t4, 1                   # loop_counter++
    sw      t4, 36(sp)                  # Store loop_counter
    li      t5, 100                     # Max iterations
    blt     t4, t5, .main_loop          # If counter < max, continue
    j       .end                        # Otherwise, exit

.no_route:
    # No westward route available - set flight_state = -1
    lw      s7, 28(sp)                  # s7 = &flight_state
    li      t5, -1                      # t5 = -1
    sw      t5, 0(s7)                   # flight_state = -1

.end:
    addi    sp, sp, 48                  # Restore stack pointer

    # Exit
    li a7, 10
    ecall
