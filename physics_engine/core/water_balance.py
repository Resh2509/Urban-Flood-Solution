import os
import glob
import pandas as pd
from typing import Dict, List
from physics_engine.models.drainage_node import DrainageNode

class WaterBalanceEngine:
    def __init__(self, data_dir: str = "hydro_twin_Data"):
        self.data_dir = data_dir
        self.nodes: Dict[str, DrainageNode] = {}
        self.network_edges: List[dict] = []
        self._load_datasets()

    def _resolve_file(self, keyword: str) -> str:
        """Finds CSV file matching a keyword inside data_dir regardless of copy suffixes."""
        matched = glob.glob(os.path.join(self.data_dir, f"*{keyword}*.csv"))
        if not matched:
            for f in os.listdir(self.data_dir):
                if keyword.lower() in f.lower() and f.endswith(".csv"):
                    return os.path.join(self.data_dir, f)
            raise FileNotFoundError(f"Could not find any CSV containing '{keyword}' in '{self.data_dir}'")
        return matched[0]

    def _clean_dataframe(self, path: str) -> pd.DataFrame:
        """Reads CSV files directly line-by-line to avoid Excel quotation/delimiter errors."""
        with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines:
            return pd.DataFrame()

        # Parse header
        raw_header = lines[0].strip().strip('"').strip("'")
        header = [c.strip().strip('"').strip("'") for c in raw_header.split(',')]

        data_rows = []
        for line in lines[1:]:
            clean_line = line.strip().strip('"').strip("'")
            if not clean_line:
                continue
            parts = [c.strip().strip('"').strip("'") for c in clean_line.split(',')]
            if len(parts) == len(header):
                data_rows.append(parts)
            elif len(parts) > len(header):
                data_rows.append(parts[:len(header)])
            else:
                parts.extend([""] * (len(header) - len(parts)))
                data_rows.append(parts)

        df = pd.DataFrame(data_rows, columns=header)
        df.columns = [str(c).replace('\ufeff', '').strip().lower() for c in df.columns]
        return df

    def _load_datasets(self):
        df_nodes = self._clean_dataframe(self._resolve_file("nodes"))
        df_edges = self._clean_dataframe(self._resolve_file("drainage"))
        df_terrain = self._clean_dataframe(self._resolve_file("terrain"))

        # Find and standardize the node id column across node & terrain dfs
        for df in [df_nodes, df_terrain]:
            for col in df.columns:
                if "node" in col:
                    df.rename(columns={col: "node_id"}, inplace=True)
                    break

        df_nodes["node_id"] = df_nodes["node_id"].astype(str).str.strip()
        df_terrain["node_id"] = df_terrain["node_id"].astype(str).str.strip()

        # Merge nodes with terrain features
        merged_nodes = df_nodes.merge(df_terrain, on="node_id", how="left")

        for _, row in merged_nodes.iterrows():
            nid = str(row.get("node_id", "")).strip()
            if not nid or nid.lower() == "nan":
                continue

            # Read elevation
            elevation = 0.0
            for col in ["elevation_m", "elevation", "elevation_m_msl"]:
                if col in row and row[col] != "":
                    try:
                        elevation = float(row[col])
                        break
                    except (ValueError, TypeError):
                        pass

            # Read slope
            slope = 0.0
            for col in ["slope_perc", "slope_percentage", "slope"]:
                if col in row and row[col] != "":
                    try:
                        slope = float(row[col])
                        break
                    except (ValueError, TypeError):
                        pass

            # Read flow accumulation
            flow_accum = 0.0
            for col in ["flow_accum", "flow_accumulation"]:
                if col in row and row[col] != "":
                    try:
                        flow_accum = float(row[col])
                        break
                    except (ValueError, TypeError):
                        pass

            # Read low area flag
            low_area = False
            for col in ["low_area_f", "low_area_flag", "low_area"]:
                if col in row and row[col] != "":
                    try:
                        low_area = bool(int(float(row[col])))
                        break
                    except (ValueError, TypeError):
                        pass

            lat = 0.0
            lon = 0.0
            try:
                lat = float(row.get("latitude", 0.0))
                lon = float(row.get("longitude", 0.0))
            except (ValueError, TypeError):
                pass

            self.nodes[nid] = DrainageNode(
                node_id=nid,
                location_name=str(row.get("location_name", nid)).strip(),
                latitude=lat,
                longitude=lon,
                node_type=str(row.get("node_type", "drainage_node")).strip(),
                elevation=elevation,
                slope=slope,
                flow_accum=flow_accum,
                is_low_area=low_area
            )

        self.network_edges = df_edges.to_dict(orient="records")

    def run_timestep_balance(self, rainfall_mm_hr: float = 45.0, runoff_coeff: float = 0.85):
        results = []
        catchment_area_m2 = 500.0
        base_surface_inflow = catchment_area_m2 * (rainfall_mm_hr / 60.0) * runoff_coeff

        for node_id, node in self.nodes.items():
            # Apply micro-topography factor (slope and depression flag)
            terrain_factor = 1.3 if node.is_low_area else (1.0 + (node.slope / 10.0))
            node_surface_in = base_surface_inflow * terrain_factor

            # Calculate outgoing pipe capacity
            out_edges = [
                e for e in self.network_edges 
                if str(e.get("source_node", "")).strip() == node_id
            ]
            
            max_outflow_capacity = 0.0
            for e in out_edges:
                cap_val = e.get("pipe_capacity") or e.get("pipe_capacity_l_min") or 400.0
                try:
                    max_outflow_capacity += float(cap_val)
                except (ValueError, TypeError):
                    max_outflow_capacity += 400.0
            
            if not out_edges:
                max_outflow_capacity = 200.0

            potential_outflow = node_surface_in + (node.stored_volume / 15.0)
            actual_outflow = min(potential_outflow, max_outflow_capacity)

            res = node.update_balance(
                surface_in=node_surface_in,
                pipe_in=0.0,
                outflow=actual_outflow,
                dt_minutes=15.0
            )
            res["location_name"] = node.location_name
            res["elevation"] = node.elevation
            results.append(res)

        return pd.DataFrame(results)