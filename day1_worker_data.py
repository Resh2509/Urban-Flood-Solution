import os
import pandas as pd

def run_day1():
    print("\n--- [Day 1] Loading Municipal Worker Fleet & Tasks ---")
    workers_df = pd.read_csv("data/workers.csv")
    tasks_df = pd.read_csv("data/tasks.csv")
    
    print(f"[OK] {len(workers_df)} Municipal Workers Active.")
    print(f"[OK] {len(tasks_df)} Emergency Flood Tasks Registered.")
    print("\nWorker Fleet Overview:")
    print(workers_df[["worker_id", "name", "role", "current_node", "availability"]].to_string(index=False))
    return workers_df, tasks_df

if __name__ == "__main__":
    run_day1()