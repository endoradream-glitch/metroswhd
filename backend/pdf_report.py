"""
Utility for generating commander brief reports as PDF documents.

Using reportlab's high-level platypus API we construct a
structured PDF summarising patrol activities and incident reports
over a specified time window. This module is designed to be
imported and invoked from the reports router.
"""

from datetime import datetime
from typing import List

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors

from .models import Incident, Patrol


def generate_commander_brief(
    file_path: str, start: datetime, end: datetime, incidents: List[Incident], patrols: List[Patrol]
) -> None:
    """Generate a PDF summarising incidents and patrol statuses.

    Args:
        file_path: Path on disk where the PDF should be saved.
        start: Start of the reporting period.
        end: End of the reporting period.
        incidents: List of incidents within the period.
        patrols: List of patrols for status summary.
    """
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    Story = []

    # Title
    title_text = f"Commander Brief ({start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')})"
    Story.append(Paragraph(title_text, styles['Title']))
    Story.append(Spacer(1, 12))

    # Section: Patrol Statuses
    Story.append(Paragraph("Patrol Statuses", styles['Heading2']))
    if patrols:
        data = [["ID", "Unit", "Route", "Last Update", "On Track"]]
        for p in patrols:
            data.append([
                p.id,
                p.unit,
                p.route_name,
                p.last_update.strftime('%Y-%m-%d %H:%M') if p.last_update else "N/A",
                "Yes" if p.on_track else "No",
            ])
        table = Table(data, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        Story.append(table)
    else:
        Story.append(Paragraph("No patrols recorded in this period.", styles['Normal']))
    Story.append(Spacer(1, 12))

    # Section: Incidents
    Story.append(Paragraph("Incident Reports", styles['Heading2']))
    if incidents:
        for inc in incidents:
            Story.append(Paragraph(f"<b>Incident ID:</b> {inc.id}", styles['Heading4']))
            Story.append(Paragraph(f"<b>Camp:</b> {inc.camp}", styles['Normal']))
            Story.append(Paragraph(f"<b>DTG:</b> {inc.dtg.strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
            Story.append(Paragraph(f"<b>Subject:</b> {inc.subject}", styles['Normal']))
            Story.append(Paragraph(f"<b>Location:</b> {inc.location[0]}, {inc.location[1]}", styles['Normal']))
            Story.append(Paragraph("<b>Details:</b>", styles['Normal']))
            for line in inc.incident_in_brief:
                Story.append(Paragraph(f" - {line}", styles['Normal']))
            if inc.follow_up:
                Story.append(Paragraph(f"<b>Follow-up:</b> {inc.follow_up}", styles['Normal']))
            Story.append(Paragraph(f"<b>Reporter:</b> {inc.reporter}", styles['Normal']))
            Story.append(Spacer(1, 12))
    else:
        Story.append(Paragraph("No incidents reported in this period.", styles['Normal']))

    doc.build(Story)