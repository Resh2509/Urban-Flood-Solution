from fastapi import APIRouter

router = APIRouter(prefix="/api")


@router.get("/hydraulic-analysis")
def get_hydraulic_analysis():
    return {
        "message": "Hydraulic analysis connection will be added here"
    }


@router.get("/blockage-risk")
def get_blockage_risk():
    return {
        "message": "Blockage risk connection will be added here"
    }