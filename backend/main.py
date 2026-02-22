"""
Entry point for the Patrol Tracker True Enterprise backend.

This module initialises the FastAPI application, configures CORS and
mounts all routers. To run locally, execute ``uvicorn main:app`` from
within the backend directory.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import users, patrols, incidents, reports, geofence, streaming


app = FastAPI(title="Patrol Tracker V3 True Enterprise Edition")

# Allow all origins for demonstration; restrict in production
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(patrols.router)
app.include_router(incidents.router)
app.include_router(geofence.router)
app.include_router(reports.router)
app.include_router(streaming.router)


@app.get("/health")
def read_health() -> dict:
    """Simple health check endpoint."""
    return {"status": "ok"}