import time
import numpy as np
import pulp
def generate_transportation_instance(supply_nodes, demand_nodes, max_cost, max_supply_demand):
    """
    Generates a random transportation problem instance including supply nodes,
    demand nodes, costs, and aligns the total supply with total demand.

    :param supply_nodes: Number of supply nodes.
    :type supply_nodes: int
    :param demand_nodes: Number of demand nodes.
    :type demand_nodes: int
    :param max_cost: Maximum cost for transportation between nodes.
    :type max_cost: int
    :param max_supply_demand: Maximum supply or demand at a single node.
    :type max_supply_demand: int
    :return: A tuple consisting of supply array, demand array, and cost matrix.
    :type return: tuple
    """
    np.random.seed(0)  # For reproducibility
    supply = np.random.randint(1, max_supply_demand, size=supply_nodes)
    demand = np.random.randint(1, max_supply_demand, size=demand_nodes)

    # Adjust supply and demand to make them equal
    total_supply = sum(supply)
    total_demand = sum(demand)
    if total_supply > total_demand:
        demand[-1] += total_supply - total_demand
    elif total_demand > total_supply:
        supply[-1] += total_demand - total_supply

    cost = np.random.randint(1, max_cost, size=(supply_nodes, demand_nodes))
    return supply, demand, cost



supply, demand, cost = generate_transportation_instance(3, 3, 10, 20)





def solve_transportation_problem(supply, demand, cost):
    """
    Solves the transportation problem to find the optimal allocation of supply to meet
    demand at minimum cost. The function uses linear programming to minimize the cost
    while satisfying the supply and demand constraints for each supply and demand node.

    :param supply: List representing the supply available at each source node
    :type supply: List[float]
    :param demand: List representing the demand required at each destination node
    :type demand: List[float]
    :param cost: 2D list where cost[i][j] represents the cost of transporting one unit
                 from supply node i to demand node j
    :type cost: List[List[float]]
    :return: A tuple containing:
             - `prob`: The optimized problem instance, which includes information about
               the solution and its status.
             - A 2D list representing the transportation solution, where the value at
               index [i][j] indicates the quantity transported from supply node i to
               demand node j.
    :rtype: Tuple[pulp.LpProblem, List[List[float]]]
    """
    supply_nodes = len(supply)
    demand_nodes = len(demand)

    # Create the problem
    prob = pulp.LpProblem("Transportation_Problem", pulp.LpMinimize)

    # Decision variables
    x = [[pulp.LpVariable(f"x_{i}_{j}", lowBound=0) for j in range(demand_nodes)] for i in range(supply_nodes)]

    # Objective function
    prob += pulp.lpSum(cost[i][j] * x[i][j] for i in range(supply_nodes) for j in range(demand_nodes))

    # Constraints
    for i in range(supply_nodes):
        prob += pulp.lpSum(x[i][j] for j in range(demand_nodes)) == supply[i]
    for j in range(demand_nodes):
        prob += pulp.lpSum(x[i][j] for i in range(supply_nodes)) == demand[j]

    # Solve the problem
    prob.solve()
    return prob, [[x[i][j].varValue for j in range(demand_nodes)] for i in range(supply_nodes)]


def revised_simplex_solver(c, A, b):
    """
    Solves a linear programming problem in standard form using the Revised Simplex
    Method. The function assumes the problem is given by a cost vector, constraint
    matrix, and constraint bounds. It iteratively computes solutions and adjusts the
    basis until the optimal solution is found or a termination condition is met.

    :param c: Coefficient vector of the objective function, with size (n,).
    :param A: Constraint matrix with size (m, n), where m is the number of
               constraints, and n is the number of variables.
    :param b: Vector of constraint bounds with size (m,).
    :return: A tuple containing:
        - The optimal solution vector of size (n,).
        - The optimal value of the objective function.
    """
    m, n = A.shape  # m = number of constraints, n = number of variables

    # Step 1: Initialize the basis
    B_indices = list(range(n - m, n))  # Indices of the basis variables
    N_indices = list(range(n - m))    # Indices of the non-basis variables

    B = A[:, B_indices]
    N = A[:, N_indices]
    c_B = c[B_indices]
    c_N = c[N_indices]

    while True:
        # Step 2: Compute the basic solution
        B_inv = safe_inverse(B)  # Use safe inverse to handle singularity

def safe_inverse(matrix):
    """
    Computes the result of a linear programming optimization problem using the Simplex
    method. This process involves iteratively improving the solution until an
    optimal result is achieved. It begins with a basic feasible solution and step-by-step
    updates the basis and non-basis variables to move toward optimality.

    Steps involve:
    1. Calculating initial conditions and testing matrix invertibility.
    2. Solving iterations for reduced costs and optimality check.
    3. Handling unbounded solutions.
    4. Updating basis variables as required.

    :param matrix: A square matrix representing the coefficient matrix
                   to be inverted or factorized during computations.
                   It is expected to be non-singular for the inversion
                   process.
    :type matrix: numpy.ndarray

    :return: Optimal solution vector and optimal value if the linear
             program has an optimal solution. If no solution exists
             due to singularity, an exception is thrown to indicate
             the termination of the algorithm.

    :rtype: tuple[numpy.ndarray, float]

    :raises ValueError: If the matrix is determined to be singular
                        and cannot be inverted or if the linear
                        program is found to be unbounded or infeasible.
    """
    try:
        return np.linalg.inv(matrix)
    except np.linalg.LinAlgError:
        raise ValueError("Matrix is singular and cannot be inverted.")
        x_B = B_inv @ b
        lambda_ = c_B @ B_inv

        # Step 3: Compute reduced costs
        reduced_costs = c_N - lambda_ @ N

        # Check for optimality
        if all(reduced_costs >= 0):
            solution = np.zeros(n)
            solution[B_indices] = x_B
            optimal_value = c @ solution
            return solution, optimal_value

        # Step 4: Determine entering variable
        entering_idx = np.argmin(reduced_costs)
        entering_var = N_indices[entering_idx]

        # Step 5: Determine direction of movement
        d = B_inv @ A[:, entering_var]
        if all(d <= 0):
            raise ValueError("The linear program is unbounded.")

        # Step 6: Determine leaving variable
        ratios = np.where(d > 1e-10, x_B / d, np.inf)
        leaving_idx = np.argmin(ratios)
        leaving_var = B_indices[leaving_idx]

        # Step 7: Update basis
        B_indices[leaving_idx] = entering_var
        N_indices[entering_idx] = leaving_var

        B = A[:, B_indices]
        N = A[:, N_indices]
        c_B = c[B_indices]
        c_N = c[N_indices]




def run_experiments():
    """
    Runs experiments to evaluate different solvers on transportation problem instances
    with various problem sizes. The function generates random instances of transportation
    problems with given supply, demand, and cost matrices, and then solves them using
    an LP solver (via the PuLP library) and a custom Revised Simplex Algorithm implementation.
    It records the performance metrics and outcomes for each solver and problem size.

    :returns: A list of dictionaries containing results for each tested problem size,
              including computation times, solution values, solver statuses, and other
              relevant details.
    :rtype: list of dict
    """
    # Problem sizes to test (equal supply and demand nodes)
    problem_sizes = [5, 10, 20, 50]
    max_cost = 50
    max_supply_demand = 100

    results = []

    for size in problem_sizes:
        print(f"Running experiments for size: {size}x{size}")

        # Generate a transportation problem instance
        supply, demand, cost = generate_transportation_instance(size, size, max_cost, max_supply_demand)

        # Solve using LP solver (PuLP)
        start_time = time.time()
        lp_prob, lp_result = solve_transportation_problem(supply, demand, cost)
        lp_time = time.time() - start_time

        # Solve using Revised Simplex Algorithm
        c = cost.flatten()
        A = create_constraint_matrix(supply, demand)
        b = np.concatenate([supply, demand])  # Combine supply and demand constraints
        start_time = time.time()
        try:
            simplex_solution, simplex_value = revised_simplex_solver(c, A, b)
            simplex_time = time.time() - start_time
            simplex_status = "Optimal"
        except Exception as e:
            simplex_solution = None
            simplex_value = None
            simplex_time = None
            simplex_status = f"Failed: {str(e)}"

        # Record the results
        results.append({
            "size": size,
            "lp_time": lp_time,
            "simplex_time": simplex_time,
            "lp_solution": lp_result,
            "simplex_solution": simplex_solution,
            "lp_value": pulp.value(lp_prob.objective),
            "simplex_value": simplex_value,
            "simplex_status": simplex_status
        })

    return results


def create_constraint_matrix(supply, demand):
    """
    Creates and returns the constraint matrix required for a transportation
    problem. The matrix represents the constraints for supply and demand
    in a transportation problem. Each row in the matrix corresponds to either
    a supply point or a demand point.

    :param supply: A list representing the capacities of supply nodes.
    :param demand: A list representing the requirements of demand nodes.
    :return: A 2D numpy array representing the constraint matrix for the
        transportation problem.
    """
    supply_nodes = len(supply)
    demand_nodes = len(demand)

    # Create the constraint matrix
    A = []

    # Supply constraints (row for each supply node)
    for i in range(supply_nodes):
        row = [0] * (supply_nodes * demand_nodes)
        for j in range(demand_nodes):
            row[i * demand_nodes + j] = 1
        A.append(row)

    # Demand constraints (row for each demand node)
    for j in range(demand_nodes):
        row = [0] * (supply_nodes * demand_nodes)
        for i in range(supply_nodes):
            row[i * demand_nodes + j] = 1
        A.append(row)

    return np.array(A)

results = run_experiments()

for res in results:
    print(f"Problem Size: {res['size']}x{res['size']}")
    print(f"LP Solver Time: {res['lp_time']:.4f}s, Objective Value: {res['lp_value']}")
    if res['simplex_time'] is not None and res['simplex_value'] is not None:
        print(f"Revised Simplex Time: {res['simplex_time']:.4f}s, Objective Value: {res['simplex_value']}")
    else:
        print(f"Revised Simplex: {res['simplex_status']}\n")
