from fastapi import FastAPI

from app.routers import predictions
from app.routers import rainfall
from app.routers import flood
from app.routers import drainage
from app.routers import blockages
from app.routers import workers
from app.routers import ai
from app.routers import hydraulic
from app.routers import physics
from app.routers import dashboard


app = FastAPI(
    title="HydroGraph-Twin API",
    description="Backend API for Urban Flood Nowcasting and Intelligent Response",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "HydroGraph-Twin Backend is running!"
    }


app.include_router(predictions.router)
app.include_router(rainfall.router)
app.include_router(flood.router)
app.include_router(drainage.router)
app.include_router(blockages.router)
app.include_router(workers.router)
app.include_router(ai.router)
app.include_router(hydraulic.router)
app.include_router(physics.router)
app.include_router(dashboard.router)