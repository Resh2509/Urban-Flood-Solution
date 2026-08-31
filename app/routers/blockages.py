from fastapi import APIRouter
from app.data.hydraulic_data import HYDRAULIC_DATA

router = APIRouter(prefix="/api")


@router.get("/blockages")
def get_blockages():

    blocked_nodes = [
        node for node in HYDRAULIC_DATA
        if node["blockage_status"] != "Normal"
    ]

    critical_blockages = [
        node for node in HYDRAULIC_DATA
        if node["blockage_status"] == "Severe_Blockage"
    ]

    return {
        "total_blockages": len(blocked_nodes),
        "critical_blockages": len(critical_blockages),
        "locations": [
            node["location_name"]
            for node in blocked_nodes
        ]
    }