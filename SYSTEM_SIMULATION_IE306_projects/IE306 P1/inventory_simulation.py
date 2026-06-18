import numpy as np

# Random numbers from the assignment
rn_list = [
    0.497, 0.380, 0.862, 0.020, 0.975, 0.391, 0.480, 0.005, 0.959,
    0.360, 0.593, 0.744, 0.069, 0.370, 0.708, 0.176, 0.020, 0.714,
    0.539, 0.928, 0.860, 0.717, 0.861, 0.563, 0.543, 0.858, 0.537
]

def get_demand(rn):
    """Get demand from random number using CDF mapping"""
    if rn < 0.10: return 2
    elif rn < 0.28: return 3
    elif rn < 0.48: return 4
    elif rn < 0.70: return 5
    elif rn < 0.90: return 6
    else: return 7

def get_lead_time(rn):
    """Get lead time from random number (discrete uniform 0-5)"""
    return int(6 * rn)

def simulate_inventory():
    """Run the 10-day inventory simulation"""
    print("Inventory System Simulation")
    print("=" * 80)
    
    # Initialize
    inventory = 18
    reorder_point = 10
    target_level = 20
    horizon = 10
    
    # Track orders: (arrival_day, quantity)
    outstanding_orders = []
    
    # Results tracking
    results = []
    rn_index = 0
    
    for day in range(1, horizon + 1):
        # Check for arrivals (morning)
        arrivals = [order for order in outstanding_orders if order[0] == day]
        for arrival_day, quantity in arrivals:
            inventory += quantity
            print(f"Day {day}: Order of {quantity} units arrived")
        outstanding_orders = [order for order in outstanding_orders if order[0] != day]
        
        # Demand
        rn_demand = rn_list[rn_index % len(rn_list)]
        demand = get_demand(rn_demand)
        rn_index += 1
        
        # Process demand
        beginning_inventory = inventory
        lost_sales = max(0, demand - inventory)
        inventory = max(0, inventory - demand)
        ending_inventory = inventory
        
        # Check for reorder (end of day)
        order_placed = "No"
        order_qty = 0
        lead_time = 0
        arrival_day = "--"
        
        if ending_inventory <= reorder_point and not outstanding_orders:
            order_qty = target_level - ending_inventory
            rn_lt = rn_list[rn_index % len(rn_list)]
            lead_time = get_lead_time(rn_lt)
            arrival_day = f"Day {day + lead_time + 1}"
            outstanding_orders.append((day + lead_time + 1, order_qty))
            order_placed = "Yes"
            rn_index += 1
        
        results.append({
            'day': day,
            'beginning': beginning_inventory,
            'rn_demand': rn_demand,
            'demand': demand,
            'ending': ending_inventory,
            'lost': lost_sales,
            'order_placed': order_placed,
            'order_qty': order_qty,
            'lead_time': lead_time,
            'arrival_day': arrival_day
        })
        
        print(f"Day {day}: Begin={beginning_inventory}, RN={rn_demand:.3f}, Demand={demand}, "
              f"End={ending_inventory}, Lost={lost_sales}, Order={order_placed}")
        if order_placed == "Yes":
            print(f"        Order: {order_qty} units, LT={lead_time}, Arrives {arrival_day}")
    
    # Calculate results
    total_lost = sum(r['lost'] for r in results)
    avg_lost = total_lost / horizon
    avg_ending = sum(r['ending'] for r in results) / horizon
    
    print("\n" + "=" * 80)
    print("RESULTS:")
    print(f"Total lost sales: {total_lost} units")
    print(f"Average lost sales per day: {avg_lost:.2f} units/day")
    print(f"Average ending inventory: {avg_ending:.2f} units")
    
    return results

if __name__ == "__main__":
    simulate_inventory()
