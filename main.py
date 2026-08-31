import os
import pandas as pd
from physics_engine.core.water_balance import WaterBalanceEngine
from physics_engine.core.hydraulic_engine import HydraulicCapacityEngine
from physics_engine.core.blockage_detector import BlockageDetectionEngine
from physics_engine.core.surcharge_backflow import SurchargeBackflowEngine

def main():
    print("=" * 80)
    print("HydroGraph-Twin — Member 2: Complete Physics & Hydraulic Engine (Days 1–4)")
    print("=" * 80)

    data_folder = "hydro_twin_Data"

    # 1. Train Blockage Model
    print("\n[STEP 1] Validating Blockage ML Classifier...")
    blockage_engine = BlockageDetectionEngine(data_dir=data_folder)
    train_res = blockage_engine.train_model()
    print(f" -> ML Model ready with {train_res['accuracy']}% accuracy.")

    # 2. Run Unified Physics Pipeline (Monsoon Downpour: 85 mm/h)
    print("\n[STEP 2] Running Coupled Physics + Hydraulic + Surcharge + Backflow Pipeline...")
    pipeline = SurchargeBackflowEngine(data_dir=data_folder)
    df_final_physics = pipeline.run_full_physics_pipeline(rainfall_mm_hr=85.0)

    # 3. Export for Member 1 (AI GNN Input) and Member 5 (FastAPI Backend)
    output_path = os.path.join(data_folder, "member2_physics_unified_output.csv")
    df_final_physics.to_csv(output_path, index=False)

    print("\n--- Member 2 Deliverable: Unified Physics & Hydraulic Stream ---")
    cols_to_print = [
        "node_id", "location_name", "inflow_lps", "capacity_lps", 
        "accumulation_rate_lps", "blockage_probability", "surcharge_status", "backflow_risk"
    ]
    print(df_final_physics[cols_to_print].to_string(index=False))

    print(f"\n[SUCCESS] Member 2 Deliverables Completed!")
    print(f"[EXPORT] Ready for Member 1 (PG-STGNN) & Member 5 (API): {output_path}")

if __name__ == "__main__":
    main()