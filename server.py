import os
import pandas as pd
import uvicorn
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="HydroGraph-Twin — Member 6 Response & Routing API",
    description="OR-Tools Worker Assignment, Flood-Aware A* Routing, and Automated Alert Dispatch",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/response/assignments")
def get_assignments():
    if os.path.exists("output/worker_assignment_output.csv"):
        df = pd.read_csv("output/worker_assignment_output.csv")
        return {"status": "success", "count": len(df), "data": df.to_dict(orient="records")}
    return {"status": "error", "message": "Assignments not generated yet."}

@app.get("/api/v1/response/routes")
def get_routes(worker_id: str = Query(None)):
    if os.path.exists("output/route_output.csv"):
        df = pd.read_csv("output/route_output.csv")
        if worker_id:
            df = df[df["worker_id"] == worker_id.strip()]
        return {"status": "success", "data": df.to_dict(orient="records")}
    return {"status": "error", "message": "Routes not generated yet."}

@app.get("/api/v1/response/notifications")
def get_notifications(worker_id: str = Query(None)):
    if os.path.exists("output/notification_output.csv"):
        df = pd.read_csv("output/notification_output.csv")
        if worker_id:
            df = df[df["worker_id"] == worker_id.strip()]
        return {"status": "success", "data": df.to_dict(orient="records")}
    return {"status": "error", "message": "Notifications not generated yet."}

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8001, reload=True)