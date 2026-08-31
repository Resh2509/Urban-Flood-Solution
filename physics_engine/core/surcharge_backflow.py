import os
import joblib
import pandas as pd
from typing import Dict, List
from physics_engine.core.water_balance import WaterBalanceEngine
from physics_engine.core.hydraulic_engine import HydraulicCapacityEngine

class SurchargeBackflowEngine:
    def __init__(self, data_dir: str = "hydro_twin_Data"):
        self.data_dir = data_dir
        self.wb_engine = WaterBalanceEngine(data_dir=data_dir)
        self.hyd_engine = HydraulicCapacityEngine(data_dir=data_dir)
        self._load_blockage_model()

    def _load_blockage_model(self):
        model_path = os.path.join(self.data_dir, "blockage_classifier_day3.joblib")
        if os.path.exists(model_path):
            artifact = joblib.load(model_path)
            self.model = artifact["model"]
            self.encoder = artifact["encoder"]
            self.feature_cols = artifact["features"]
        else:
            self.model = None

    def run_full_physics_pipeline(self, rainfall_mm_hr: float = 75.0, simulated_blocked_nodes: List[str] = ["N007", "N012"]) -> pd.DataFrame:
        """
        Runs the complete Day 1–4 integrated physics pipeline:
        Continuity Equation -> Manning Capacity -> ML Blockage Inference -> Surcharge & Backflow.
        """
        # 1. Day 1 Water Balance
        df_nodes = self.wb_engine.run_timestep_balance(rainfall_mm_hr=rainfall_mm_hr)

        # 2. Day 2 Hydraulic Capacity
        node_inflows_lps = {
            row["node_id"]: float(row["total_inflow_L_min"]) / 60.0
            for _, row in df_nodes.iterrows()
        }
        df_pipes = self.hyd_engine.evaluate_network(node_inflows_lps)

        # 3. Map downstream pipe capacity per node
        node_pipe_map: Dict[str, dict] = {}
        for _, pipe in df_pipes.iterrows():
            src = pipe["source_node"]
            node_pipe_map[src] = {
                "pipe_id": pipe["pipe_id"],
                "target_node": pipe["target_node"],
                "capacity_lps": pipe["manning_capacity_lps"],
                "fcr": pipe["flow_capacity_ratio"],
                "pipe_status": pipe["hydraulic_status"],
                "is_surcharged": pipe["surcharge_risk"]
            }

        final_records = []
        normal_idx = list(self.encoder.classes_).index("Normal") if self.model and "Normal" in self.encoder.classes_ else 0

        for _, node in df_nodes.iterrows():
            nid = node["node_id"]
            inflow_lps = node["total_inflow_L_min"] / 60.0
            outflow_lps = node["outflow_L_min"] / 60.0
            accum_lps = node["accumulation_rate_L_min"] / 60.0
            water_depth = node["estimated_depth_cm"]
            
            p_info = node_pipe_map.get(nid, {
                "pipe_id": "NONE",
                "target_node": "OUTLET",
                "capacity_lps": 400.0,
                "fcr": 0.02,
                "pipe_status": "Normal",
                "is_surcharged": False
            })

            # Handle simulated local blockages (e.g. debris/silt accumulation in Velachery)
            is_locally_blocked = nid in simulated_blocked_nodes
            effective_fcr = 0.45 if is_locally_blocked else max(1.10, round(inflow_lps / max(outflow_lps, 1.0), 3))

            # Machine Learning Blockage Inference
            blockage_prob = 0.0
            blockage_status = "Normal"
            if self.model:
                feat_df = pd.DataFrame([{
                    "rainfall_mm": rainfall_mm_hr / 4.0,
                    "flow_in_lps": inflow_lps,
                    "flow_out_lps": outflow_lps * 0.4 if is_locally_blocked else outflow_lps,
                    "water_level_cm": (water_depth + 15.0) if is_locally_blocked else max(5.0, water_depth + 2.0),
                    "water_accumulation_lps": accum_lps + (4.5 if is_locally_blocked else 0.0),
                    "flow_capacity_ratio": effective_fcr
                }])
                probs = self.model.predict_proba(feat_df[self.feature_cols])[0]
                pred_cls = self.model.predict(feat_df[self.feature_cols])[0]
                blockage_prob = round(1.0 - probs[normal_idx], 3)
                blockage_status = self.encoder.inverse_transform([pred_cls])[0]

            # Physical Surcharge & Backflow Rules
            is_surcharged = p_info["is_surcharged"] or blockage_status != "Normal" or water_depth > 10.0
            surcharge_status = "Surcharged" if is_surcharged else "Normal"

            backflow_risk = False
            if is_surcharged and p_info["target_node"] in self.wb_engine.nodes:
                downstream_node = self.wb_engine.nodes[p_info["target_node"]]
                if node["elevation"] <= (downstream_node.elevation + 1.2):
                    backflow_risk = True

            final_records.append({
                "node_id": nid,
                "location_name": node["location_name"],
                "elevation_m": node["elevation"],
                "inflow_lps": round(inflow_lps, 2),
                "outflow_lps": round(outflow_lps, 2),
                "capacity_lps": round(p_info["capacity_lps"], 2),
                "accumulation_rate_lps": round(accum_lps, 2),
                "water_depth_cm": round(water_depth, 2),
                "blockage_probability": blockage_prob,
                "blockage_status": blockage_status,
                "surcharge_status": surcharge_status,
                "backflow_risk": backflow_risk
            })

        return pd.DataFrame(final_records)