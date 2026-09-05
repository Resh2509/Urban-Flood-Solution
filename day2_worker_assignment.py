import os
import pandas as pd
from ortools.linear_solver import pywraplp
from routing.road_network import haversine_distance

def run_day2():
    print("\n--- [Day 2] Running Google OR-Tools Worker Dispatch Optimization ---")
    workers_df = pd.read_csv("data/workers.csv")
    tasks_df = pd.read_csv("data/tasks.csv")

    num_workers = len(workers_df)
    num_tasks = len(tasks_df)

    # Compute Distance Matrix (meters)
    dist_matrix = []
    for _, w in workers_df.iterrows():
        row = []
        for _, t in tasks_df.iterrows():
            d = haversine_distance(
                float(w["latitude"]), float(w["longitude"]),
                float(t["latitude"]), float(t["longitude"])
            )
            row.append(float(d))
        dist_matrix.append(row)

    # Mixed Integer Linear Programming (MIP) Solver using SCIP (or CBC fallback)
    solver = pywraplp.Solver.CreateSolver("SCIP") or pywraplp.Solver.CreateSolver("CBC")
    if not solver:
        raise RuntimeError("OR-Tools SCIP/CBC solver not found.")

    x = {}
    for i in range(num_workers):
        for j in range(num_tasks):
            x[i, j] = solver.IntVar(0, 1, f"x_{i}_{j}")

    # Constraint 1: Each emergency task assigned to exactly 1 worker
    for j in range(num_tasks):
        solver.Add(solver.Sum([x[i, j] for i in range(num_workers)]) == 1)

    # Constraint 2: Each worker handles at most 1 task
    for i in range(num_workers):
        solver.Add(solver.Sum([x[i, j] for j in range(num_tasks)]) <= 1)

    # Objective: Minimize cost = Distance - (Priority Score * 30.0)
    objective = solver.Objective()
    for i in range(num_workers):
        for j in range(num_tasks):
            priority = float(tasks_df.iloc[j]["priority_score"])
            cost = float(dist_matrix[i][j]) - (priority * 30.0)
            # Explicit float conversion prevents the SWIG C++ double TypeError
            objective.SetCoefficient(x[i, j], float(cost))
    objective.SetMinimization()

    status = solver.Solve()

    assignments = []
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        for i in range(num_workers):
            for j in range(num_tasks):
                if x[i, j].solution_value() > 0.5:
                    w = workers_df.iloc[i]
                    t = tasks_df.iloc[j]
                    assignments.append({
                        "worker_id": str(w["worker_id"]),
                        "worker_name": str(w["name"]),
                        "worker_role": str(w["role"]),
                        "phone": str(w["phone"]),
                        "start_node": str(w["current_node"]),
                        "task_id": str(t["task_id"]),
                        "target_node": str(t["node_id"]),
                        "location_name": str(t["location_name"]),
                        "task_type": str(t["task_type"]),
                        "priority_score": int(t["priority_score"]),
                        "urgency": str(t["urgency"]),
                        "distance_m": round(float(dist_matrix[i][j]), 2)
                    })

    df_assign = pd.DataFrame(assignments)
    os.makedirs("output", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    df_assign.to_csv("output/worker_assignment_output.csv", index=False)
    df_assign.to_csv("data/assignments.csv", index=False)

    print(f"[OK] Generated {len(df_assign)} optimized assignments.")
    print(df_assign[["worker_id", "worker_name", "task_id", "target_node", "location_name", "priority_score", "distance_m"]].to_string(index=False))
    return df_assign

if __name__ == "__main__":
    run_day2()