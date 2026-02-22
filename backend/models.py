"""
Pydantic models and data structures representing domain entities for the
True Enterprise edition of Patrol Tracker.

These models act as a contract for API request and response bodies and
provide type hints throughout the backend.
"""

from datetime import datetime
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field

from .roles import Role


class User(BaseModel):
    username: str
    role: Role


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PatrolBase(BaseModel):
    unit: str
    route_name: str
    # route as list of coordinate pairs (lat, lon)
    route: List[Tuple[float, float]] = Field(default_factory=list)


class PatrolCreate(PatrolBase):
    pass


class Patrol(PatrolBase):
    id: int
    current_location: Optional[Tuple[float, float]] = None
    last_update: Optional[datetime] = None
    on_track: bool = True

    class Config:
        orm_mode = True


class PatrolUpdate(BaseModel):
    latitude: float
    longitude: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class IncidentReport(BaseModel):
    camp: str
    dtg: datetime
    subject: str
    location: Tuple[float, float]
    incident_in_brief: List[str] = Field(default_factory=list, description="List of numbered incident details")
    follow_up: Optional[str] = None
    reporter: str


class Incident(IncidentReport):
    id: int


class Geofence(BaseModel):
    name: str
    points: List[Tuple[float, float]]
    # Optionally define a bounding box for quick checks
    class Config:
        orm_mode = True


class PDFRequest(BaseModel):
    start_date: datetime
    end_date: datetime
