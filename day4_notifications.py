import os
import pandas as pd

def run_day4():
    print("\n--- [Day 4] Generating Automated Worker Emergency Notifications ---")
    assignments_df = pd.read_csv("data/assignments.csv")
    routes_df = pd.read_csv("output/route_output.csv")
    tasks_df = pd.read_csv("data/tasks.csv")

    # Drop duplicate columns in routes_df before merging to avoid _x/_y suffix collision
    routes_clean = routes_df.drop(columns=["worker_name"], errors="ignore")
    
    # Merge assignments with routes
    merged = assignments_df.merge(routes_clean, on=["worker_id", "task_id"], how="inner")

    # Merge task inundation depth if not already present
    if "estimated_water_depth_cm" not in merged.columns:
        merged = merged.merge(tasks_df[["task_id", "estimated_water_depth_cm"]], on="task_id", how="left")

    notifications = []
    for _, row in merged.iterrows():
        depth = row.get("estimated_water_depth_cm", row.get("max_flood_depth_cm", 0.0))
        msg = (
            f"🚨 URGENT MUNICIPAL DISPATCH [{str(row['urgency']).upper()} PRIORITY: {row['priority_score']}/100] 🚨\n"
            f"Dear {row['worker_name']} ({row['worker_role']}),\n"
            f"Task: {row['task_type']}\n"
            f"Location: {row['location_name']} ({row['target_node']})\n"
            f"Predicted Water Inundation: {depth} cm\n"
            f"Safe Navigation Route: {row['safe_path']}\n"
            f"Total Distance: {row['safe_distance_m']} m | Status: {row['route_status']}"
        )
        notifications.append({
            "worker_id": row["worker_id"],
            "worker_name": row["worker_name"],
            "phone": row["phone"],
            "urgency": row["urgency"],
            "priority_score": row["priority_score"],
            "target_location": row["location_name"],
            "target_node": row["target_node"],
            "safe_path": row["safe_path"],
            "safe_distance_m": row["safe_distance_m"],
            "sms_payload": msg
        })

    df_notif = pd.DataFrame(notifications)
    os.makedirs("output", exist_ok=True)
    df_notif.to_csv("output/notification_output.csv", index=False)

    print(f"[OK] Created {len(df_notif)} SMS/Push Notifications.")
    print("\n--- Sample Emergency Dispatch Notification ---")
    print("-" * 75)
    print(df_notif.iloc[0]["sms_payload"])
    print("-" * 75)
    return df_notif

if __name__ == "__main__":
    run_day4()