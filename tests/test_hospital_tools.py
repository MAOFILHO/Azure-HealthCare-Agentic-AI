import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from hospital_tools import book_appointment, find_patient, get_appointments


def test_find_patient_finds_maria_rivera():
    result = json.loads(find_patient("Rivera"))
    assert [p["name"] for p in result] == ["Maria Rivera"]
    assert result[0]["id"] == "PAT-1001"


def test_find_patient_unknown_name_returns_nothing():
    assert find_patient("Nobody Atall") == "No matching patient found."


def test_get_appointments_lists_cardiology_follow_up():
    result = json.loads(get_appointments("PAT-1001"))
    assert len(result) == 1
    assert result[0]["department"] == "Cardiology"
    assert result[0]["datetime"].startswith("2026-07-29")


def test_get_appointments_unknown_patient_returns_nothing():
    assert get_appointments("PAT-0000") == (
        "No upcoming appointments for this patient."
    )


def test_book_appointment_returns_confirmation_code_and_status():
    result = json.loads(book_appointment("PAT-1001", "Cardiology", "2026-09-01"))
    assert result["status"] == "confirmed"
    assert result["confirmationCode"] == "NGH-1001-20260901"
