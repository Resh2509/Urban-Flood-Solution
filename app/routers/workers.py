from fastapi import APIRouter
from app.data.hydraulic_data import HYDRAULIC_DATA

router = APIRouter(prefix="/api")


@router.get("/workers")
def get_workers():

    high_risk_nodes = [
        node for node in HYDRAULIC_DATA
        if node["blockage_probability"] >= 1
    ]

    return {
        "available_workers": 12,
        "assigned_workers": 5,
        "available_vehicles": 4,
        "high_risk_locations": len(high_risk_nodes)
    }