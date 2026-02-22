"""
Incident reporting routes.

This router allows patrol members to submit structured incident reports and
higher roles to view them. The incident format follows a high-level
Bangladesh Army style, storing details such as camp, DTG, subject and
structured incident details. Reports are stored in-memory for this
demonstration.
"""

from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies import role_required, get_current_user
from ..models import Incident, IncidentReport
from ..roles import Role


router = APIRouter(prefix="/incidents", tags=["incidents"])

# In-memory incident store
incidents_db: Dict[int, Incident] = {}
incident_id_counter = 1


@router.post("/report", response_model=Incident, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident_data: IncidentReport,
    current_user = Depends(role_required(Role.PATROL_MEMBER)),
):
    """Submit a new incident report. Members and above may report."""
    global incident_id_counter
    new_id = incident_id_counter
    incident_id_counter += 1
    incident = Incident(
        id=new_id,
        camp=incident_data.camp,
        dtg=incident_data.dtg,
        subject=incident_data.subject,
        location=incident_data.location,
        incident_in_brief=incident_data.incident_in_brief,
        follow_up=incident_data.follow_up,
        reporter=current_user.username,
    )
    incidents_db[new_id] = incident
    return incident


@router.get("/", response_model=List[Incident])
async def list_incidents(current_user=Depends(role_required(Role.PATROL_MEMBER))):
    """Return all incident reports."""
    return list(incidents_db.values())