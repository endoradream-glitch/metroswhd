"""
Geofence management routes.

These endpoints allow HQ staff to define geofences and retrieve existing
geofences. Patrol location updates can be checked against these
geofences to detect incursions or deviations.
"""

from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies import role_required
from ..models import Geofence
from ..roles import Role


router = APIRouter(prefix="/geofences", tags=["geofences"])

# In-memory geofence store
geofence_db: Dict[str, Geofence] = {}


@router.post("/create", response_model=Geofence, status_code=status.HTTP_201_CREATED)
async def create_geofence(geofence: Geofence, user=Depends(role_required(Role.HQ_OPS))):
    """Create or update a named geofence."""
    geofence_db[geofence.name] = geofence
    return geofence


@router.get("/", response_model=List[Geofence])
async def list_geofences(user=Depends(role_required(Role.PATROL_MEMBER))):
    """List all configured geofences."""
    return list(geofence_db.values())