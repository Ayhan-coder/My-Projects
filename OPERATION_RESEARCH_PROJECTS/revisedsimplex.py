import numpy as np
from pulp import LpMaximize, LpProblem, LpVariable, PULP_CBC_CMD


def revised_simplex_solver(c, A, b):

    m, n = A.shape
    basis_indices = find_initial_basis(A)  # Find initial basis
    if basis_indices is None:
        return None, None, "infeasible"

    nonbasic_indices = [i for i in range(n) if i not in basis_indices]
    x = np.zeros(n)
    x[basis_indices] = np.linalg.solve(A[:, basis_indices], b)
    obj = np.dot(c, x)
    B_inv = np.linalg.inv(A[:, basis_indices])

    while True:
        y = np.dot(c[basis_indices], B_inv)
        reduced_costs = c[nonbasic_indices] - np.dot(y, A[:, nonbasic_indices])

        if all(rc <= 1e-10 for rc in reduced_costs):
            return x, obj, "optimal"

        enter_index = nonbasic_indices[np.argmax(reduced_costs)]
        pbar = np.dot(B_inv, A[:, enter_index])

        if all(p <= 1e-10 for p in pbar):
            return x, obj, "unbounded"

        ratios = [(x[basis_indices[i]] / pbar[i], i) if pbar[i] > 1e-10 else (np.inf, i) for i in range(m)]
        exit_index_basis = min(ratios)[1]
        exit_index = basis_indices[exit_index_basis]

        basis_indices[exit_index_basis] = enter_index
        nonbasic_indices = [i for i in range(n) if i not in basis_indices]
        theta = min(ratios)[0]

        x[enter_index] = theta
        for i in range(m):
            if i != exit_index_basis:
                x[basis_indices[i]] -= pbar[i] * theta
        x[exit_index] = 0.0

        eta = np.eye(m)
        eta[:, exit_index_basis] = -pbar / pbar[exit_index_basis]
        eta[exit_index_basis, exit_index_basis] = 1.0 / pbar[exit_index_basis]
        B_inv = np.dot(eta, B_inv)

        obj = np.dot(c, x)


def find_initial_basis(A):
    m, n = A.shape
    potential_basis = A[:, n - m:]
    if np.linalg.matrix_rank(potential_basis) == m:
        return list(range(n - m, n))
    else:
        return None


def pulp_solver(c, A, b):

    m, n = A.shape
    prob = LpProblem("LP_Problem", LpMaximize)

    # Variables
    x = [LpVariable(f"x{i}", lowBound=0) for i in range(n)]

    # Objective Function
    prob += sum(c[i] * x[i] for i in range(n))

    # Constraints
    for i in range(m):
        prob += sum(A[i][j] * x[j] for j in range(n)) <= b[i]

    # Solve Problem
    prob.solve(PULP_CBC_CMD(msg=False))

    solution = [var.value() for var in x]
    objective = prob.objective.value()
    return solution, objective


def test_lp_solvers():
    test_cases = [
        {
            "name": "Basic Feasible Solution",
            "c": np.array([3, 2]),
            "A": np.array([[1, 1], [2, 1]]),
            "b": np.array([4, 6]),
            "expected_status": "optimal",
        },
        {
            "name": "Unbounded Solution",
            "c": np.array([3, 2]),
            "A": np.array([[-1, -1], [-2, -1]]),
            "b": np.array([-4, -6]),
            "expected_status": "unbounded",
        },
        {
            "name": "Infeasible Problem",
            "c": np.array([1, 1]),
            "A": np.array([[1, 0], [-1, 0]]),
            "b": np.array([1, -2]),
            "expected_status": "infeasible",
        },
        {
            "name": "Degenerate Problem",
            "c": np.array([4, 5]),
            "A": np.array([[1, 1], [2, 0], [0, 2]]),
            "b": np.array([5, 8, 8]),
            "expected_status": "optimal",
        },
    ]

    for case in test_cases:
        print(f"Running test case: {case['name']}")
        c = case["c"]
        A = case["A"]
        b = case["b"]

        # Test Revised Simplex Solver
        manual_solution, manual_obj, manual_status = revised_simplex_solver(c, A, b)

        # Test PuLP Solver
        pulp_solution, pulp_obj = pulp_solver(c, A, b)

        # Compare results
        print("Revised Simplex Solver:")
        print(f"  Status: {manual_status}")
        if manual_status == "optimal":
            print(f"  Solution: {manual_solution}")
            print(f"  Objective Value: {manual_obj}")

        print("PuLP Solver:")
        print(f"  Solution: {pulp_solution}")
        print(f"  Objective Value: {pulp_obj}")

        if manual_status == "optimal" and case["expected_status"] == "optimal":
            diff = abs(manual_obj - pulp_obj)
            assert diff < 1e-5, f"Objective values differ too much: {diff}"
            print(f"  Objective values are consistent with a difference of {diff:.5e}.")
        elif manual_status != case["expected_status"]:
            print(f"  Unexpected status from Revised Simplex Solver: {manual_status}.")
        else:
            print(f"  Both solvers agree on problem status ({case['expected_status']}).")

        print("\n" + "-" * 50 + "\n")


# Run tests
test_lp_solvers()