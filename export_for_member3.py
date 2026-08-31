import os
import glob
import pandas as pd

def _resolve_file(data_dir: str, keyword: str) -> str:
    matched = glob.glob(os.path.join(data_dir, f"*{keyword}*.csv"))
    if not matched:
        for f in os.listdir(data_dir):
            if keyword.lower() in f.lower() and f.endswith(".csv"):
                return os.path.join(data_dir, f)
        raise FileNotFoundError(f"Missing CSV containing '{keyword}' in '{data_dir}'")
    return matched[0]

def generate_member3_dataset(data_dir="hydro_twin_Data"):
    physics_file = os.path.join(data_dir, "member2_physics_unified_output.csv")
    network_file = _resolve_file(data_dir, "drainage")

    df_physics = pd.read_csv(physics_file)
    df_network = pd.read_csv(network_file)

    # Clean headers
    df_physics.columns = df_physics.columns.str.strip()
    df_network.columns = df_network.columns.str.strip()

    # Clean join keys
    df_physics["node_id"] = df_physics["node_id"].astype(str).str.strip()
    df_network["source_node"] = df_network["source_node"].astype(str).str.strip()

    # Merge edge network with source node physics
    df_merged = df_network.merge(
        df_physics, 
        left_on="source_node", 
        right_on="node_id", 
        how="left"
    )

    # Format exactly as Member 3 requested
    df_member3 = pd.DataFrame({
        "drainage_id": df_merged["pipe_id"],
        "from_node": df_merged["source_node"],
        "to_node": df_merged["target_node"],
        "flow_rate_lps": df_merged["inflow_lps"],
        "capacity_lps": df_merged["capacity_lps"],
        "water_level_cm": df_merged["water_depth_cm"],
        "blockage_probability": df_merged["blockage_probability"],
        "blockage_status": df_merged["blockage_status"],
        "overflow_risk": df_merged["surcharge_status"].apply(lambda x: "High" if str(x).strip() == "Surcharged" else "Low"),
        "backflow_risk": df_merged["backflow_risk"]
    })

    output_path = os.path.join(data_dir, "member3_drainage_visualization.csv")
    df_member3.to_csv(output_path, index=False)
    print(f"[OK] Member 3 Dataset Generated: {output_path}")
    return df_member3

if __name__ == "__main__":
    df = generate_member3_dataset()
    print("\n--- Member 3 Drainage Network Output Preview ---")
    print(df.to_string(index=False))