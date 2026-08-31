import os
import glob
import pandas as pd
from typing import Dict
from physics_engine.models.drainage_pipe import DrainagePipe

class HydraulicCapacityEngine:
    def __init__(self, data_dir: str = "hydro_twin_Data"):
        self.data_dir = data_dir
        self.pipes: Dict[str, DrainagePipe] = {}
        self._load_network()

    def _resolve_file(self, keyword: str) -> str:
        matched = glob.glob(os.path.join(self.data_dir, f"*{keyword}*.csv"))
        if not matched:
            for f in os.listdir(self.data_dir):
                if keyword.lower() in f.lower() and f.endswith(".csv"):
                    return os.path.join(self.data_dir, f)
            raise FileNotFoundError(f"Missing CSV containing '{keyword}' in '{self.data_dir}'")
        return matched[0]

    def _load_network(self):
        pipe_path = self._resolve_file("drainage")
        with open(pipe_path, "r", encoding="utf-8-sig", errors="ignore") as f:
            lines = [l.strip() for l in f if l.strip()]

        raw_header = lines[0].strip().strip('"').strip("'")
        header = [c.strip().strip('"').strip("'").lower() for c in raw_header.split(',')]

        for line in lines[1:]:
            parts = [c.strip().strip('"').strip("'") for c in line.split(',')]
            row = dict(zip(header, parts))
            pid = row.get("pipe_id", "").strip()
            if not pid:
                continue

            try:
                length = float(row.get("pipe_length_m", 1000.0))
                diameter = float(row.get("pipe_diameter_m", 0.6))
                slope = float(row.get("pipe_slope", 0.004))
                roughness = float(row.get("roughness_coefficient", 0.013))
            except (ValueError, TypeError):
                length, diameter, slope, roughness = 1000.0, 0.6, 0.004, 0.013

            self.pipes[pid] = DrainagePipe(
                pipe_id=pid,
                source_node=row.get("source_node", "").strip(),
                target_node=row.get("target_node", "").strip(),
                length_m=length,
                diameter_m=diameter,
                slope=slope,
                roughness=roughness
            )

    def evaluate_network(self, node_inflows_lps: Dict[str, float]) -> pd.DataFrame:
        results = []
        for pid, pipe in self.pipes.items():
            theoretical_cap = pipe.calculate_manning_capacity_lps()
            inflow = node_inflows_lps.get(pipe.source_node, 50.0)
            state = pipe.classify_flow_state(inflow, theoretical_cap)

            results.append({
                "pipe_id": pipe.pipe_id,
                "source_node": pipe.source_node,
                "target_node": pipe.target_node,
                "pipe_diameter_m": pipe.diameter_m,
                "manning_capacity_lps": round(theoretical_cap, 2),
                "actual_flow_in_lps": round(inflow, 2),
                "flow_capacity_ratio": state["flow_capacity_ratio"],
                "hydraulic_status": state["hydraulic_status"],
                "surcharge_risk": state["surcharge_risk"]
            })

        return pd.DataFrame(results)