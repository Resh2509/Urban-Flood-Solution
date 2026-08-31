from fastapi import APIRouter
from app.data.scenario import (
    RAINFALL_MM_HR,
    RAINFALL_LOCATION,
    RAINFALL_INTENSITY
)

router = APIRouter(prefix="/api")


@router.get("/rainfall")
def get_rainfall():
    return {
        "location": RAINFALL_LOCATION,
        "rainfall_mm": RAINFALL_MM_HR,
        "intensity": RAINFALL_INTENSITY
    }