from dataclasses import dataclass

@dataclass
class DrainageNode:
    node_id: str
    location_name: str
    latitude: float
    longitude: float
    node_type: str
    elevation: float = 0.0
    slope: float = 0.0
    flow_accum: float = 0.0
    is_low_area: bool = False
    
    # Dynamic state tracking
    surface_inflow_rate: float = 0.0
    pipe_inflow_rate: float = 0.0
    total_inflow: float = 0.0
    outflow_rate: float = 0.0
    stored_volume: float = 0.0
    accumulation_rate: float = 0.0
    water_depth_cm: float = 0.0

    def update_balance(self, surface_in: float, pipe_in: float, outflow: float, dt_minutes: float = 15.0):
        self.surface_inflow_rate = surface_in
        self.pipe_inflow_rate = pipe_in
        self.total_inflow = surface_in + pipe_in
        self.outflow_rate = outflow
        
        self.accumulation_rate = self.total_inflow - self.outflow_rate
        volume_change = self.accumulation_rate * dt_minutes
        self.stored_volume = max(0.0, self.stored_volume + volume_change)
        
        # 10m x 10m nodal surface ponding approximation
        catchment_m2 = 100.0
        self.water_depth_cm = (self.stored_volume / (catchment_m2 * 1000.0)) * 100.0
        
        return {
            "node_id": self.node_id,
            "total_inflow_L_min": round(self.total_inflow, 2),
            "outflow_L_min": round(self.outflow_rate, 2),
            "accumulation_rate_L_min": round(self.accumulation_rate, 2),
            "stored_volume_L": round(self.stored_volume, 2),
            "estimated_depth_cm": round(self.water_depth_cm, 2),
            "status": "Abnormal Accumulation" if self.accumulation_rate > 50.0 else "Normal"
        }