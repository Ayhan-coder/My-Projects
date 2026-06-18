"""
IE 306 Assignment 1 – Question 1
Inventory System Simulation (10 days)
"""

# ── Given random numbers ──────────────────────────────────────────────
random_numbers = [
    0.497, 0.380, 0.862, 0.020, 0.975, 0.391, 0.480,
    0.005, 0.959, 0.360, 0.593, 0.744, 0.069, 0.370,
    0.708, 0.176, 0.020, 0.714, 0.539, 0.928, 0.860,
    0.717, 0.861, 0.563, 0.543, 0.858, 0.537
]

# ── Demand distribution ──────────────────────────────────────────────
# Demand:      2     3     4     5     6     7
# Prob:       0.10  0.18  0.20  0.22  0.20  0.10
# CDF:        0.10  0.28  0.48  0.70  0.90  1.00
def demand_from_rn(rn):
    """Map a random number to a demand value using inverse-transform."""
    if rn < 0.10:
        return 2
    elif rn < 0.28:
        return 3
    elif rn < 0.48:
        return 4
    elif rn < 0.70:
        return 5
    elif rn < 0.90:
        return 6
    else:
        return 7

# ── Lead-time distribution (discrete uniform 0-5) ────────────────────
# Values: 0, 1, 2, 3, 4, 5  each with prob 1/6
# CDF:    0.1667  0.3333  0.5000  0.6667  0.8333  1.0000
def lead_time_from_rn(rn):
    """Map a random number to a lead time (0–5 days)."""
    if rn < 1/6:
        return 0
    elif rn < 2/6:
        return 1
    elif rn < 3/6:
        return 2
    elif rn < 4/6:
        return 3
    elif rn < 5/6:
        return 4
    else:
        return 5

# ── Simulation parameters ────────────────────────────────────────────
REORDER_POINT = 10
TARGET_LEVEL  = 20
INITIAL_INV   = 18
SIM_DAYS      = 10

# ── Run the simulation ───────────────────────────────────────────────
rn_idx = 0          # index into random_numbers list

inventory       = INITIAL_INV
order_pending    = False    # is there an outstanding order?
order_arrival_day = None    # the day the pending order arrives (morning)
order_qty        = 0

total_lost_sales = 0
total_ending_inv = 0

header = (f"{'Day':>3} | {'Beg Inv':>7} | {'RN(D)':>7} | {'Demand':>6} | "
          f"{'End Inv':>7} | {'Lost':>4} | {'Order?':>6} | "
          f"{'RN(LT)':>7} | {'LT':>3} | {'Ord Qty':>7} | {'Arrive':>6}")
print(header)
print("-" * len(header))

for day in range(1, SIM_DAYS + 1):

    # ── Morning: receive order if it arrives today ────────────────
    if order_pending and order_arrival_day == day:
        inventory += order_qty
        order_pending = False
        order_arrival_day = None
        received = order_qty
        order_qty = 0
    else:
        received = 0

    beginning_inv = inventory

    # ── During the day: generate demand ───────────────────────────
    rn_demand = random_numbers[rn_idx]; rn_idx += 1
    demand = demand_from_rn(rn_demand)

    # ── Satisfy demand ────────────────────────────────────────────
    if inventory >= demand:
        inventory -= demand
        lost = 0
    else:
        lost = demand - inventory
        inventory = 0

    ending_inv = inventory
    total_lost_sales += lost
    total_ending_inv += ending_inv

    # ── End of day: check reorder policy ──────────────────────────
    order_placed = False
    rn_lt_str = ""
    lt_str = ""
    oq_str = ""
    arrive_str = ""

    if ending_inv <= REORDER_POINT and not order_pending:
        order_placed = True
        order_qty = TARGET_LEVEL - ending_inv

        rn_lt = random_numbers[rn_idx]; rn_idx += 1
        lt = lead_time_from_rn(rn_lt)

        order_pending = True
        # Order placed at close of day  →  arrives morning of (day + lt + 1)
        # If LT=0 → available morning of next day  (day+1)
        order_arrival_day = day + lt + 1

        rn_lt_str = f"{rn_lt:.3f}"
        lt_str = str(lt)
        oq_str = str(order_qty)
        arrive_str = f"Day {order_arrival_day}"

    recv_note = f" (+{received})" if received else ""

    print(f"{day:>3} | {beginning_inv:>7}{recv_note:>0} | {rn_demand:>7.3f} | {demand:>6} | "
          f"{ending_inv:>7} | {lost:>4} | {'Yes' if order_placed else 'No':>6} | "
          f"{rn_lt_str:>7} | {lt_str:>3} | {oq_str:>7} | {arrive_str:>6}")

print("-" * len(header))

avg_lost = total_lost_sales / SIM_DAYS
avg_inv  = total_ending_inv / SIM_DAYS

print(f"\n=== RESULTS ===")
print(f"Total lost sales over {SIM_DAYS} days : {total_lost_sales}")
print(f"Average lost sales per day          : {avg_lost:.2f}")
print(f"Sum of ending inventories           : {total_ending_inv}")
print(f"Average ending inventory level      : {avg_inv:.2f}")
