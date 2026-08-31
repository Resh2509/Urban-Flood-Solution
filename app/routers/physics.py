
from fastapi import APIRouter, HTTPException
from app.data.hydraulic_data import HYDRAULIC_DATA
from app.data.scenario import RAINFALL_MM_HR

router = APIRouter(
    prefix="/api/v1/physics",
    tags=["Physics"]
)


@router.get("/hydraulic-analysis")
def hydraulic_analysis():
    return {
        "status": "success",
        "rainfall_mm_hr": RAINFALL_MM_HR,
        "total_nodes": len(HYDRAULIC_DATA),
        "data": HYDRAULIC_DATA
    }


@router.get("/blockage-risk")
def blockage_risk(node_id: str | None = None):

    if node_id:
        filtered_nodes = [
            node for node in HYDRAULIC_DATA
            if node["node_id"].upper() == node_id.upper()
        ]

        if not filtered_nodes:
            raise HTTPException(
                status_code=404,
                detail=f"Node {node_id} not found"
            )
    else:
        filtered_nodes = HYDRAULIC_DATA

    high_risk_nodes = [
        node for node in filtered_nodes
        if node["blockage_probability"] >= 1
    ]

    return {
        "status": "success",
        "node_filter": node_id.upper() if node_id else "ALL",
        "high_risk_count": len(high_risk_nodes),
        "data": [
            {
                "node_id": node["node_id"],
                "location_name": node["location_name"],
                "inflow_lps": node["inflow_lps"],
                "outflow_lps": node["outflow_lps"],
                "capacity_lps": node["capacity_lps"],
                "blockage_probability": node["blockage_probability"],
                "blockage_status": node["blockage_status"],
                "surcharge_status": node["surcharge_status"]
            }
            for node in filtered_nodes
        ]
    }