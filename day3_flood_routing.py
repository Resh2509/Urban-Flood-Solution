import os
import pandas as pd
from routing.road_network import build_velachery_road_network
from routing.flood_cost import update_flood_costs
from routing.astar_router import find_flood_aware_route

def run_day3():
    print("\n--- [Day 3] Generating Flood-Aware A* Safe Routes ---")
    assignments_df = pd.read_csv("data/assignments.csv")
    tasks_df = pd.read_csv("data/tasks.csv")

    # Build node flood dictionary from high priority task water depths
    node_flood_depths = {row["node_id"]: float(row["estimated_water_depth_cm"]) for _, row in tasks_df.iterrows()}

    # Initialize Graph & dynamic flood weights
    G = build_velachery_road_network()
    G = update_flood_costs(G, node_flood_depths)

    routes = []
    for _, row in assignments_df.iterrows():
        start = row["start_node"]
        target = row["target_node"]
        route_data = find_flood_aware_route(G, start, target)
        route_data["worker_id"] = row["worker_id"]
        route_data["worker_name"] = row["worker_name"]
        route_data["task_id"] = row["task_id"]
        routes.append(route_data)

    df_routes = pd.DataFrame(routes)
    os.makedirs("output", exist_ok=True)
    df_routes.to_csv("output/route_output.csv", index=False)

    print(f"[OK] Flood-aware routes mapped for {len(df_routes)} assignments.")
    print(df_routes[["worker_id", "source", "target", "safe_path", "safe_distance_m", "route_status"]].to_string(index=False))
    return df_routes

if __name__ == "__main__":
    run_day3()