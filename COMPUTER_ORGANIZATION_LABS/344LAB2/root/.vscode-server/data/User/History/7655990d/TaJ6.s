.global _start

.equ NUM_AIRPORTS, 10               # Total number of airports
.equ FUEL_CAPACITY, 20000           # Maximum fuel capacity of the airplane
.equ FUEL_CONSUMPTION_RATE, 2       # Fuel consumption rate of the plane (fuel per distance unit)

.section .rodata
# Distance matrix [NUM_AIRPORTS x NUM_AIRPORTS]
# Each row corresponds to an airport, and each column corresponds to the distance to another airport
# Self-distance is 0

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

current_fuel:     .word 20000
airport_supply:   .word 17000, 18000, 16000, 17000, 27500, 36500, 15500, 26000, 27000, 40000
current_airport:  .word 5            # Starting at Brussels
flight_state:     .word 1            # 1 = journey ongoing, -1 = journey ended

.section .bss

distance_traveled: .space 4          # Total distance traveled (word)
flight_history:    .space 64         # History of visited airport indices (bytes)
history_len:       .space 4          # Length of flight_history (word)


.section .text
# -------------------------------------------------------------
# Helper: rd = rs * 10  (no MUL; RV32I-safe)
# Args:
#   rd = destination register
#   rs = source register (index value)
# Clobbers: t0, t1 (internal scratch)
# Note: result = rs * 10, computed as (rs << 3) + (rs << 1)
# -------------------------------------------------------------
.macro MUL10 rd, rs
    slli    t0, \rs, 3        # t0 = rs * 8
    slli    t1, \rs, 1        # t1 = rs * 2
    add     \rd, t0, t1       # rd = t0 + t1 = rs*10
.endm

# -------------------------------------------------------------
# flight_navigation(current_idx, &distances, &directions, current_fuel)
# Args:
#   a0 = current_idx (0..NUM_AIRPORTS-1)
#   a1 = &distances (word matrix NUMxNUM)
#   a2 = &directions (byte matrix NUMxNUM)
#   a3 = current_fuel (value)
# Returns:
#   a0 = index of closest reachable westward (dir==2 or 3), or -1 if none
# Clobbers: t0-t6, a4-a7
# Preserves: s0-s1
# -------------------------------------------------------------
.global flight_navigation
flight_navigation:
    addi    sp, sp, -16
    sw      ra, 12(sp)
    sw      s0, 8(sp)
    sw      s1, 4(sp)

    mv      s0, a0              # s0 = current_idx
    li      s1, -1              # best_index = -1

    li      t5, 0x7fffffff      # best_distance = big

    # Compute row bases: for distances and directions
    # row_off = current_idx * 10
    MUL10   t0, s0              # t0 = row_off (elements)

    # dist_row_addr = a1 + (row_off * 4)
    slli    t1, t0, 2           # t1 = row_off * 4
    add     t2, a1, t1          # t2 = dist_row_addr

    # dir_row_addr = a2 + (row_off * 1)
    add     t3, a2, t0          # t3 = dir_row_addr

    li      t4, 0               # j = 0

.fn_loop_j:
    li      t1, NUM_AIRPORTS
    bge     t4, t1, .fn_done

    # Skip self (j == current_idx)
    beq     t4, s0, .fn_next_j

    # Load direction byte: dir = dir_row_addr[j]
    add     t6, t3, t4
    lbu     a4, 0(t6)           # a4 = dir byte

    # Check westward (2 or 3)
    li      a5, 2
    beq     a4, a5, .fn_check_reach
    li      a5, 3
    bne     a4, a5, .fn_next_j

.fn_check_reach:
    # Load distance word: dist = dist_row_addr[j]
    slli    a6, t4, 2
    add     a6, t2, a6
    lw      a6, 0(a6)           # a6 = distance

    # fuel_needed = dist * FUEL_CONSUMPTION_RATE (=2)
    slli    a7, a6, 1           # a7 = fuel_needed

    # reachable ? current_fuel (a3) >= fuel_needed
    blt     a3, a7, .fn_next_j

    # If reachable and closer than best, update best
    bge     a6, t5, .fn_next_j

    mv      t5, a6              # best_distance = dist
    mv      s1, t4              # best_index = j

.fn_next_j:
    addi    t4, t4, 1
    j       .fn_loop_j

.fn_done:
    mv      a0, s1              # return best_index (or -1)

    lw      s1, 4(sp)
    lw      s0, 8(sp)
    lw      ra, 12(sp)
    addi    sp, sp, 16
    ret


# -------------------------------------------------------------
# refuel(airport_idx, &airport_supply, current_fuel)
# Args:
#   a0 = airport_idx
#   a1 = &airport_supply (word array)
#   a2 = current_fuel (value)
# Returns:
#   a0 = updated current_fuel after refuel (value)
# Side effects:
#   airport_supply[airport_idx] decreased by amount taken
# Notes: Plane fills up to FUEL_CAPACITY; if supply is 0, no refuel.
# -------------------------------------------------------------
.global refuel
refuel:
    addi    sp, sp, -16
    sw      ra, 12(sp)
    sw      s0, 8(sp)
    sw      s1, 4(sp)

    mv      s0, a0              # s0 = airport_idx
    mv      s1, a2              # s1 = current_fuel

    # need = FUEL_CAPACITY - current_fuel
    li      t0, FUEL_CAPACITY
    sub     t0, t0, s1
    bge     x0, t0, .rf_done_ret_cur    # need <= 0? already full

    # load supply = airport_supply[idx]
    slli    t1, s0, 2
    add     t2, a1, t1
    lw      t3, 0(t2)           # t3 = supply

    beqz    t3, .rf_done_ret_cur

    # take = min(need, supply)
    blt     t0, t3, .rf_take_need
    mv      t4, t3              # take = supply
    j       .rf_apply
.rf_take_need:
    mv      t4, t0              # take = need

.rf_apply:
    add     s1, s1, t4          # current_fuel += take
    sub     t3, t3, t4          # supply -= take
    sw      t3, 0(t2)           # store back supply

.rf_done_ret_cur:
    mv      a0, s1              # return updated fuel

    lw      s1, 4(sp)
    lw      s0, 8(sp)
    lw      ra, 12(sp)
    addi    sp, sp, 16
    ret


# -------------------------------------------------------------
# execute_flight(src_idx, dst_idx, &distances, &current_fuel,
#                &distance_traveled, &current_airport,
#                &flight_history, &history_len)
# Args:
#   a0 = src_idx
#   a1 = dst_idx
#   a2 = &distances
#   a3 = &current_fuel (word)
#   a4 = &distance_traveled (word)
#   a5 = &current_airport (word)
#   a6 = &flight_history (bytes)
#   a7 = &history_len (word)
# Returns:
#   a0 = 0 on success, -1 on failure (insufficient fuel)
# Side effects:
#   Updates current_fuel, distance_traveled, current_airport
#   Appends dst_idx to flight_history and increments history_len
# -------------------------------------------------------------
.global execute_flight
execute_flight:
    addi    sp, sp, -24
    sw      ra, 20(sp)
    sw      s0, 16(sp)
    sw      s1, 12(sp)

    mv      s0, a0              # s0 = src_idx
    mv      s1, a1              # s1 = dst_idx

    # distance = distances[src*10 + dst]
    MUL10   t0, s0              # t0 = src*10
    add     t0, t0, s1          # t0 = src*10 + dst (element index)
    slli    t1, t0, 2           # *4 (word size)
    add     t1, a2, t1          # address
    lw      t2, 0(t1)           # t2 = distance

    # fuel_needed = distance * 2
    slli    t3, t2, 1

    # load current_fuel
    lw      t4, 0(a3)

    # Check reachability (defensive)
    blt     t4, t3, .xf_fail

    # current_fuel -= fuel_needed
    sub     t4, t4, t3
    sw      t4, 0(a3)

    # distance_traveled += distance
    lw      t5, 0(a4)
    add     t5, t5, t2
    sw      t5, 0(a4)

    # current_airport = dst_idx
    sw      s1, 0(a5)

    # Append to history: flight_history[history_len] = dst_idx (byte)
    # Only write if within bounds (max 64 bytes)
    lw      t6, 0(a7)           # t6 = history_len
    li      t0, 64
    bge     t6, t0, .xf_skip_hist
    
    add     t5, a6, t6          # address of slot
    andi    t4, s1, 0xFF
    sb      t4, 0(t5)
    addi    t6, t6, 1
    sw      t6, 0(a7)

.xf_skip_hist:

    li      a0, 0               # success
    j       .xf_done

.xf_fail:
    li      a0, -1

.xf_done:
    lw      s1, 12(sp)
    lw      s0, 16(sp)
    lw      ra, 20(sp)
    addi    sp, sp, 24
    ret


# -------------------------------------------------------------
# check_flight_state(current_idx, &distances, &directions, current_fuel, &flight_state)
# Args:
#   a0 = current_idx
#   a1 = &distances
#   a2 = &directions
#   a3 = current_fuel (value)
#   a4 = &flight_state
# Returns:
#   a0 = flight_state (1 = continue, -1 = ended)
# Preserves: s0
# -------------------------------------------------------------
.global check_flight_state
check_flight_state:
    addi    sp, sp, -16
    sw      ra, 12(sp)
    sw      s0, 8(sp)

    # Preserve the flight_state pointer (a4) across the call
    mv      s0, a4

    # Call flight_navigation to see if any westward reachable
    call    flight_navigation

    # a0 = next_idx or -1
    li      t0, -1
    beq     a0, t0, .cfs_end

    # reachable -> flight_state = 1
    li      t1, 1
    sw      t1, 0(s0)          # store via preserved pointer
    mv      a0, t1
    j       .cfs_done

.cfs_end:
    li      t1, -1
    sw      t1, 0(s0)          # store via preserved pointer
    mv      a0, t1

.cfs_done:
    lw      s0, 8(sp)
    lw      ra, 12(sp)
    addi    sp, sp, 16
    ret


# -------------------------------------------------------------
# Program entry / main loop
# NOTE: _start is the ELF entry point (no caller). Using s0–s8 here is OK
# without saving/restoring because there is no caller frame to preserve.
# All *procedures* below follow the standard RISC-V calling convention
# (callee-saved s* registers saved/restored inside each procedure).
# -------------------------------------------------------------
# Program entry / main loop
# -------------------------------------------------------------
_start:
    # Zero counters
    li      t0, 0
    la      t1, distance_traveled
    sw      t0, 0(t1)
    la      t2, history_len
    sw      t0, 0(t2)

    # Record starting airport into history
    la      t3, current_airport
    lw      t4, 0(t3)                   # t4 = start_idx
    la      t5, flight_history
    lw      t6, 0(t2)                   # history_len (0)
    add     t1, t5, t6
    andi    t4, t4, 0xFF
    sb      t4, 0(t1)
    addi    t6, t6, 1
    sw      t6, 0(t2)

    # Save all pointers on stack for safe access throughout main loop
    # Stack layout (from sp):
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
    # sp+40-47: padding (for 16-byte stack alignment)
    
    addi    sp, sp, -48
    
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
    sw      t0, 36(sp)          # loop_counter = 0

.main_loop:
    # Load pointers from stack
    lw      s0, 0(sp)           # &distances
    lw      s1, 4(sp)           # &directions
    lw      s2, 8(sp)           # &current_fuel
    lw      s3, 12(sp)          # &distance_traveled
    lw      s4, 16(sp)          # &current_airport
    lw      s5, 20(sp)          # &flight_history
    lw      s6, 24(sp)          # &history_len
    lw      s7, 28(sp)          # &flight_state
    lw      s8, 32(sp)          # &airport_supply
    
    # Load current state
    lw      a0, 0(s4)           # a0 = current_idx
    mv      a1, s0              # a1 = &distances
    mv      a2, s1              # a2 = &directions
    lw      a3, 0(s2)           # a3 = current_fuel value

    # Determine next airport (closest westward & reachable)
    call    flight_navigation    # a0 = next_idx or -1

    li      t1, -1
    beq     a0, t1, .no_route

    # Have a route: execute flight
    # Reload pointers (safe, but these are unchanged anyway)
    lw      s0, 0(sp)           # &distances
    lw      s2, 8(sp)           # &current_fuel
    lw      s3, 12(sp)          # &distance_traveled
    lw      s4, 16(sp)          # &current_airport
    lw      s5, 20(sp)          # &flight_history
    lw      s6, 24(sp)          # &history_len
    
    mv      a1, a0              # dst_idx (result from flight_navigation)
    lw      a0, 0(s4)           # src_idx
    mv      a2, s0              # &distances
    mv      a3, s2              # &current_fuel (addr)
    mv      a4, s3              # &distance_traveled
    mv      a5, s4              # &current_airport
    mv      a6, s5              # &flight_history
    mv      a7, s6              # &history_len

    call    execute_flight      # a0 = 0 on success

    li      t2, 0
    bne     a0, t2, .no_route   # if failed for any reason, end

    # On landing, refuel at the new current_airport
    # Reload pointers after execute_flight
    lw      s2, 8(sp)           # &current_fuel
    lw      s4, 16(sp)          # &current_airport
    lw      s8, 32(sp)          # &airport_supply
    
    lw      a0, 0(s4)           # airport_idx
    mv      a1, s8              # &airport_supply
    lw      a2, 0(s2)           # current_fuel value
    call    refuel
    sw      a0, 0(s2)           # store updated fuel

    # Update flight_state (1 = continue)
    # Reload all pointers after refuel
    lw      s0, 0(sp)           # &distances
    lw      s1, 4(sp)           # &directions
    lw      s2, 8(sp)           # &current_fuel
    lw      s4, 16(sp)          # &current_airport
    lw      s7, 28(sp)          # &flight_state
    
    lw      a0, 0(s4)           # current_idx
    mv      a1, s0              # &distances
    mv      a2, s1              # &directions
    lw      a3, 0(s2)           # current_fuel value
    mv      a4, s7              # &flight_state
    call    check_flight_state  # a0 = flight_state

    li      t3, -1
    beq     a0, t3, .end

    # Safety cap: avoid infinite loops
    lw      t4, 36(sp)          # load loop_counter
    addi    t4, t4, 1
    sw      t4, 36(sp)          # save loop_counter
    li      t5, 100
    blt     t4, t5, .main_loop
    j       .end

.no_route:
    # No reachable westward route -> set flight_state = -1 and end
    lw      s7, 28(sp)          # &flight_state
    li      t5, -1
    sw      t5, 0(s7)

.end:
    addi    sp, sp, 48          # restore stack (must match -48)
    li      a0, 0               # exit code
    li      a7, 93              # SYS_exit
    ecall
