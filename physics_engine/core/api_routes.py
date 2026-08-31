from fastapi import APIRouter, Query
from typing import Optional, List
from physics_engine.core.surcharge_backflow import SurchargeBackflowEngine
from physics_engine.core.hydraulic_engine import HydraulicCapacityEngine
from physics_engine.core.blockage_detector import BlockageDetectionEngine

router = APIRouter(prefix="/api/v1/physics", tags=["Physics & Hydraulics Engine"])

# Initialize engines
surcharge_engine = SurchargeBackflowEngine()
hydraulic_engine = HydraulicCapacityEngine()
blockage_engine = BlockageDetectionEngine()

@router.get("/hydraulic-analysis")
def get_hydraulic_analysis(rainfall_mm_hr: float = Query(75.0, description="Rainfall intensity in mm/hr")):
    """
    Computes real-time mass balance, Manning capacity, surcharge status, and backflow risk across all nodes.
    """
    df_results = surcharge_engine.run_full_physics_pipeline(rainfall_mm_hr=rainfall_mm_hr)
    return {
        "status": "success",
        "rainfall_mm_hr": rainfall_mm_hr,
        "total_nodes": len(df_results),
        "data": df_results.to_dict(orient="records")
    }

@router.get("/blockage-risk")
def get_blockage_risk(node_id: Optional[str] = Query(None, description="Optional specific Node ID (e.g. N007)")):
    """
    Returns real-time ML blockage probabilities, blockage classifications, and flow-to-capacity metrics.
    """
    df_results = surcharge_engine.run_full_physics_pipeline(rainfall_mm_hr=75.0)
    
    if node_id:
        filtered = df_results[df_results["node_id"] == node_id.strip()]
        records = filtered.to_dict(orient="records")
    else:
        # Return all nodes with blockage details
        records = df_results[[
            "node_id", "location_name", "inflow_lps", "outflow_lps", 
            "capacity_lps", "blockage_probability", "blockage_status", "surcharge_status"
        ]].to_dict(orient="records")
        
    return {
        "status": "success",
        "node_filter": node_id if node_id else "ALL",
        "high_risk_count": sum(1 for r in records if r["blockage_status"] != "Normal"),
        "data": records
    }