import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from physics_engine.core.api_routes import router as physics_router

app = FastAPI(
    title="HydroGraph-Twin — Physics & Hydraulics API",
    description="Physics-Guided Urban Flood Nowcasting: Mass balance, Manning capacity, blockage AI, surcharge & backflow engine.",
    version="1.0.0"
)

# Enable CORS for Member 3's GIS Dashboard frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register physics endpoints
app.include_router(physics_router)

@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "HydroGraph-Twin Physics Engine (Member 2)",
        "endpoints": [
            "/api/v1/physics/hydraulic-analysis",
            "/api/v1/physics/blockage-risk",
            "/docs"
        ]
    }

if __name__ == "__main__":
    print("=" * 70)
    print("Launching HydroGraph-Twin Physics API on http://127.0.0.1:8000")
    print("Swagger Documentation available at: http://127.0.0.1:8000/docs")
    print("=" * 70)
    uvicorn.run("server.py:app", host="127.0.0.1", port=8000, reload=True)