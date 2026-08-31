from fastapi import APIRouter
from app.data.hydraulic_data import HYDRAULIC_DATA

router = APIRouter(prefix="/api")


@router.get("/predictions")
def get_predictions():

    max_water_depth = max(
        node["water_depth_cm"]
        for node in HYDRAULIC_DATA
    )

    if max_water_depth >= 10:
        risk_level = "Critical"
    elif max_water_depth >= 5:
        risk_level = "High"
    elif max_water_depth >= 2:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "prediction_window": "0-3 hours",
        "predicted_flood_depth_cm": max_water_depth,
        "risk_level": risk_level
    }