from fastapi import APIRouter

router = APIRouter(prefix="/api")


@router.get("/forecast")
def get_forecast():
    return {
        "message": "AI forecast connection will be added here"
    }