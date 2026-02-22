"""
Reporting endpoints for exporting commander briefs.

This router provides an endpoint for generating PDF reports summarising
patrol statuses and incidents over a given time window. Access is
restricted to HQ OPS and above.
"""

import os
from datetime import datetime
from tempfile import NamedTemporaryFile
from typing import List

from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import FileResponse

from ..dependencies import role_required
from ..models import Incident, Patrol
from ..roles import Role
from ..pdf_report import generate_commander_brief
from .incidents import incidents_db
from .patrols import patrols_db


router = APIRouter(prefix="/reports", tags=["reports"])


def _parse_datetime(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid datetime: {value}")


@router.get("/commander-brief")
async def commander_brief(
    start: str = Query(..., description="Start of reporting period (ISO8601)"),
    end: str = Query(..., description="End of reporting period (ISO8601)"),
    user=Depends(role_required(Role.HQ_OPS)),
):
    """Generate a commander brief PDF for the specified date range."""
    start_dt = _parse_datetime(start)
    end_dt = _parse_datetime(end)
    if end_dt < start_dt:
        raise HTTPException(status_code=400, detail="End must be after start")

    # Filter incidents
    incident_list: List[Incident] = []
    for inc in incidents_db.values():
        if start_dt <= inc.dtg <= end_dt:
            incident_list.append(inc)

    # All patrols included
    patrol_list: List[Patrol] = list(patrols_db.values())

    # Generate PDF in a temporary file
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp_path = tmp.name
    generate_commander_brief(tmp_path, start_dt, end_dt, incident_list, patrol_list)

    filename = f"commander_brief_{start_dt.date()}_{end_dt.date()}.pdf"
    return FileResponse(tmp_path, filename=filename, media_type="application/pdf")