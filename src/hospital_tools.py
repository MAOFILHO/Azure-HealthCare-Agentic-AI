"""Function tools over Northfield General's (mock) hospital systems.

Each function is written to be readable by a language model: the
docstring says what it does, and every argument carries a description.
"""
import json
from pathlib import Path
from typing import Annotated

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load(filename: str) -> list[dict]:
    return json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))


def find_patient(
    name: Annotated[str, "Full or partial patient name, e.g. 'Rivera'"],
) -> str:
    """Look up patient records by name in the hospital registry."""
    matches = [
        p for p in _load("patients.json")
        if name.lower() in p["name"].lower()
    ]
    if not matches:
        return "No matching patient found."
    return json.dumps(matches)


def get_appointments(
    patient_id: Annotated[str, "Patient identifier, e.g. 'PAT-1001'"],
) -> str:
    """Return all upcoming appointments for a patient ID."""
    appts = [
        a for a in _load("appointments.json")
        if a["patientId"] == patient_id
    ]
    if not appts:
        return "No upcoming appointments for this patient."
    return json.dumps(appts)


def book_appointment(
    patient_id: Annotated[str, "Patient identifier, e.g. 'PAT-1001'"],
    department: Annotated[str, "Department, e.g. 'Cardiology'"],
    preferred_day: Annotated[str, "Preferred date, format YYYY-MM-DD"],
) -> str:
    """Book a new appointment and return the confirmation details.

    This mock does not persist anything; a real implementation would
    POST to the scheduling system's API instead.
    """
    confirmation = f"NGH-{patient_id[-4:]}-{preferred_day.replace('-', '')}"
    return json.dumps({
        "status": "confirmed",
        "confirmationCode": confirmation,
        "patientId": patient_id,
        "department": department,
        "date": preferred_day,
        "instructions": "Arrive 15 minutes early with photo ID and "
                        "insurance card.",
    })
