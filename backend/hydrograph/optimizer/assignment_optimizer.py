import sys
import json
import math

from ortools.graph.python import linear_sum_assignment


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the straight-line distance between
    two latitude/longitude points in kilometers.
    """

    R = 6371.0

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c


def severity_penalty(severity):

    severity = str(severity).lower()

    if severity == "critical":
        return 0

    if severity == "high":
        return 10

    if severity == "medium":
        return 20

    return 30


def calculate_cost(worker, task):

    distance = haversine_distance(
        float(worker["latitude"]),
        float(worker["longitude"]),
        float(task["latitude"]),
        float(task["longitude"])
    )

    priority = float(task["priority_score"])
    deadline = float(task["deadline_minutes"])
    severity = task["severity"]

    priority_cost = 100 - priority
    deadline_cost = min(deadline, 120) / 10
    severity_cost = severity_penalty(severity)

    cost = (
        distance * 100
        + priority_cost * 2
        + deadline_cost
        + severity_cost
    )

    return int(round(cost))


def solve_assignment(workers, tasks):

    if not workers:
        raise ValueError("No available workers found.")

    if not tasks:
        raise ValueError("No tasks found.")

    assignment = linear_sum_assignment.SimpleLinearSumAssignment()

    for worker_index, worker in enumerate(workers):

        for task_index, task in enumerate(tasks):

            cost = calculate_cost(worker, task)

            assignment.add_arc_with_cost(
                worker_index,
                task_index,
                cost
            )

    status = assignment.solve()

    if status != assignment.OPTIMAL:
        raise RuntimeError("No optimal assignment found.")

    results = []

    for worker_index in range(len(workers)):

        task_index = assignment.right_mate(worker_index)

        if task_index >= 0:

            worker = workers[worker_index]
            task = tasks[task_index]

            cost = assignment.assignment_cost(worker_index)

            results.append({
                "worker_id": worker["worker_id"],
                "task_id": task["task_id"],
                "cost": cost
            })

    return results


def main():

    try:

        input_data = sys.stdin.read()

        data = json.loads(input_data)

        workers = data.get("workers", [])
        tasks = data.get("tasks", [])

        results = solve_assignment(
            workers,
            tasks
        )

        print(json.dumps({
            "success": True,
            "assignments": results
        }))

    except Exception as error:

        print(json.dumps({
            "success": False,
            "error": str(error)
        }))

        sys.exit(1)


if __name__ == "__main__":
    main()
    