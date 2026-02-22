"""
Patrol management routes.

This router defines endpoints for creating patrols, updating their
locations and retrieving a list of active patrols. Patrol data is
kept in-memory for simplicity. Each update triggers a broadcast to
connected WebSocket clients via the streaming manager.
"""

from datetime import datetime
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies import role_required
from ..models import Patrol, PatrolCreate, PatrolUpdate
from ..roles import Role
from .. import geofence
from .streaming import manager  # WebSocket manager for broadcast


router = APIRouter(prefix="/patrols", tags=["patrols"])

# In-memory store of patrols
patrols_db: Dict[int, Patrol] = {}
patrol_id_counter = 1


@router.post("/create", response_model=Patrol, status_code=status.HTTP_201_CREATED)
async def create_patrol(patrol_data: PatrolCreate, user=Depends(role_required(Role.PATROL_COMD))):
    """Create a new patrol. Only command-level or higher may create."""
    global patrol_id_counter
    new_id = patrol_id_counter
    patrol_id_counter += 1
    patrol = Patrol(
        id=new_id,
        unit=patrol_data.unit,
        route_name=patrol_data.route_name,
        route=patrol_data.route,
        current_location=None,
        last_update=None,
        on_track=True,
    )
    patrols_db[new_id] = patrol
    return patrol


@router.get("/", response_model=List[Patrol])
async def list_patrols(user=Depends(role_required(Role.PATROL_MEMBER))):
    """Return all patrols visible to the user. Members may see their own; higher roles see all."""
    # For simplicity, return all patrols
    return list(patrols_db.values())


@router.post("/{patrol_id}/update", response_model=Patrol)
async def update_patrol(
    patrol_id: int,
    update: PatrolUpdate,
    user=Depends(role_required(Role.PATROL_MEMBER)),
):
    """Update patrol location and check route adherence. Broadcast update via WebSocket."""
    patrol = patrols_db.get(patrol_id)
    if not patrol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patrol not found")
    # Update location
    patrol.current_location = (update.latitude, update.longitude)
    patrol.last_update = update.timestamp
    # Check if on track
    patrol.on_track = geofence.is_on_route(patrol.current_location, patrol.route)
    # Broadcast update to clients
    message = {
        "type": "location_update",
        "patrol_id": patrol.id,
        "unit": patrol.unit,
        "location": patrol.current_location,
        "timestamp": patrol.last_update.isoformat(),
        "on_track": patrol.on_track,
    }
    await manager.broadcast(message)
    return patrol