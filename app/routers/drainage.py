from fastapi import APIRouter
from app.data.hydraulic_data import HYDRAULIC_DATA

router = APIRouter(prefix="/api")


@router.get("/drainage")
def get_drainage():

    blocked_nodes = len([
        node for node in HYDRAULIC_DATA
        if node["blockage_probability"] >= 1
    ])

    surcharged_nodes = len([
        node for node in HYDRAULIC_DATA
        if node["surcharge_status"] == "Surcharged"
    ])

    if surcharged_nodes > 0:
        network_status = "Partially Critical"
    else:
        network_status = "Normal"

    return {
        "total_nodes": len(HYDRAULIC_DATA),
        "blocked_nodes": blocked_nodes,
        "surcharged_nodes": surcharged_nodes,
        "network_status": network_status
    }