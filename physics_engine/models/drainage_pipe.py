import math
from dataclasses import dataclass

@dataclass
class DrainagePipe:
    pipe_id: str
    source_node: str
    target_node: str
    length_m: float
    diameter_m: float
    slope: float
    roughness: float = 0.013  # Concrete Manning's n

    def calculate_manning_capacity_lps(self) -> float:
        """
        Calculates theoretical full-flow capacity using Manning's Equation:
        Q = (1 / n) * A * (R_h)^(2/3) * S^(1/2)
        Returns discharge in Litres per Second (L/s).
        """
        s = max(self.slope, 0.001)
        radius = self.diameter_m / 2.0
        area = math.pi * (radius ** 2)
        wetted_perimeter = math.pi * self.diameter_m
        hydraulic_radius = area / wetted_perimeter

        velocity = (1.0 / self.roughness) * (hydraulic_radius ** (2.0 / 3.0)) * (math.sqrt(s))
        flow_m3_s = area * velocity
        return flow_m3_s * 1000.0

    @staticmethod
    def classify_flow_state(flow_in_lps: float, capacity_lps: float) -> dict:
        fcr = flow_in_lps / capacity_lps if capacity_lps > 0 else 999.0

        if fcr < 0.60:
            status = "Normal"
        elif fcr < 0.85:
            status = "High Load"
        elif fcr <= 1.00:
            status = "Near Capacity"
        elif fcr <= 1.25:
            status = "Overcapacity"
        else:
            status = "Surcharge Risk"

        return {
            "flow_capacity_ratio": round(fcr, 3),
            "hydraulic_status": status,
            "surcharge_risk": status in ["Overcapacity", "Surcharge Risk"]
        }