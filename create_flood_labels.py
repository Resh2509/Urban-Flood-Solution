import csv
import os

# ============================================================
# 1. FILE PATHS CONFIGURATION
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "hydro_twin_Data")

INPUT_FILE = os.path.join(DATA_DIR, "05_hydraulic_observations.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "06_flood_blockage_labels.csv")

print("\nProcessing hydraulic observations...")
print(f"Reading: {INPUT_FILE}")

if not os.path.exists(INPUT_FILE):
    print(f"\n[ERROR] File not found: {INPUT_FILE}")
    print("Ensure 05_hydraulic_observations.csv is placed inside hydro_twin_Data.")
    exit()

# ============================================================
# 2. PROCESS HYDRAULIC RECORDS & COMPUTE TARGET LABELS
# ============================================================
labeled_rows = []

with open(INPUT_FILE, "r", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)
    
    # Strip whitespace from headers
    if not reader.fieldnames:
        print("\n[ERROR] The input CSV file has no header row.")
        exit()
        
    reader.fieldnames = [h.strip() for h in reader.fieldnames]

    for row in reader:
        timestamp = row.get("timestamp", "").strip()
        node_id = row.get("node_id", "").strip()
        
        try:
            flow_in = float(row.get("flow_in_lps", 0.0))
            flow_out = float(row.get("flow_out_lps", 1.0))
            water_depth = float(row.get("water_depth_cm", 0.0))
            accum_rate = float(row.get("water_accumulation_lps", flow_in - flow_out))
        except (ValueError, TypeError):
            continue

        # 1. Hydraulic Ratio: Inflow vs Discharge
        ratio = round(flow_in / max(flow_out, 0.001), 2)

        # 2. Blockage State & Quantitative Probability Index
        if ratio <= 1.05 and water_depth <= 5.0:
            status = "Normal"
            blockage_risk = round(min(ratio * 0.15, 0.20), 2)
        elif ratio <= 1.30 and water_depth <= 20.0:
            status = "Moderate_Load"
            blockage_risk = round(0.25 + (ratio - 1.0) * 0.20, 2)
        elif ratio <= 1.80 or water_depth <= 40.0:
            status = "Partial_Blockage"
            blockage_risk = round(0.50 + (ratio - 1.3) * 0.25, 2)
        else:
            status = "Severe_Blockage_Surcharge"
            blockage_risk = round(min(0.80 + (water_depth / 100.0) * 0.20, 0.99), 2)

        # 3. Surface Inundation Hazard Rating
        if water_depth < 10.0:
            severity = "Low"
        elif water_depth < 25.0:
            severity = "Medium"
        elif water_depth < 50.0:
            severity = "High"
        else:
            severity = "Critical"

        labeled_rows.append({
            "timestamp": timestamp,
            "node_id": node_id,
            "water_depth_cm": round(water_depth, 2),
            "flow_capacity_ratio": ratio,
            "accumulation_rate": round(accum_rate, 2),
            "blockage_status": status,
            "blockage_risk": blockage_risk,
            "flood_severity": severity
        })

print(f"Parsed {len(labeled_rows)} hydraulic observation records.")

# ============================================================
# 3. WRITE 06_flood_blockage_labels.csv
# ============================================================
fieldnames = [
    "timestamp",
    "node_id",
    "water_depth_cm",
    "flow_capacity_ratio",
    "accumulation_rate",
    "blockage_status",
    "blockage_risk",
    "flood_severity"
]

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(labeled_rows)

print("\n" + "=" * 55)
print("SUCCESS: 06_flood_blockage_labels.csv created!")
print(f"Saved to: {OUTPUT_FILE}")
print("=" * 55)