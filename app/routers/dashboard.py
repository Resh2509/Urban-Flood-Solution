from fastapi import APIRouter
from app.data.hydraulic_data import HYDRAULIC_DATA

router = APIRouter(prefix="/api")


@router.get("/dashboard")
def get_dashboard():

    blocked_nodes = [
        node for node in HYDRAULIC_DATA
        if node["blockage_probability"] >= 1
    ]

    surcharged_nodes = [
        node for node in HYDRAULIC_DATA
        if node["surcharge_status"] == "Surcharged"
    ]

    return {
        "rainfall": {
            "rainfall_mm_hr": 75,
            "location": "Velachery"
        },

        "flood_status": {
            "status": "Warning",
            "risk_level": "High"
        },

        "prediction": {
            "prediction_window": "0-3 hours",
            "predicted_flood_depth_cm": 25,
            "risk_level": "High"
        },

        "drainage": {
            "total_nodes": len(HYDRAULIC_DATA),
            "blocked_nodes": len(blocked_nodes),
            "surcharged_nodes": len(surcharged_nodes),
            "network_status": "Partially Critical"
        },

        "blockages": {
            "total_blockages": len(blocked_nodes),
            "critical_blockages": len(blocked_nodes)
        },

        "workers": {
            "available_workers": 12,
            "assigned_workers": 5,
            "available_vehicles": 4
        },

        "high_risk_nodes": [
            {
                "node_id": node["node_id"],
                "location_name": node["location_name"],
                "blockage_status": node["blockage_status"],
                "surcharge_status": node["surcharge_status"],
                "backflow_risk": node["backflow_risk"]
            }
            for node in blocked_nodes
        ]
    }