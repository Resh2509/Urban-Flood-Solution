from fastapi import APIRouter
from app.data.hydraulic_data import HYDRAULIC_DATA

router = APIRouter(prefix="/api")


@router.get("/flood-status")
def get_flood_status():

    high_risk_nodes = [
        node for node in HYDRAULIC_DATA
        if node["blockage_probability"] >= 1
    ]

    flooded_roads = len([
        node for node in HYDRAULIC_DATA
        if node["water_depth_cm"] >= 5
    ])

    if len(high_risk_nodes) >= 2:
        risk_level = "High"
        status = "Warning"
    elif len(high_risk_nodes) == 1:
        risk_level = "Medium"
        status = "Watch"
    else:
        risk_level = "Low"
        status = "Normal"

    return {
        "status": status,
        "flooded_roads": flooded_roads,
        "risk_level": risk_level,
        "high_risk_nodes": len(high_risk_nodes)
    }