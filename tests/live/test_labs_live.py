"""Opt-in live smoke test: runs every lab against the deployed Azure project.

Skipped unless RUN_LIVE=1. Environment variables (FOUNDRY_PROJECT_ENDPOINT,
FOUNDRY_MODEL_DEPLOYMENT_NAME, FOUNDRY_RESOURCE_ENDPOINT) come from the caller.
Lab 7 cleanup is excluded: it deletes the agent.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src"
TIMEOUT = 180

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(os.environ.get("RUN_LIVE") != "1", reason="set RUN_LIVE=1 to run against Azure"),
]

# (script, stdin, expected phrase). Order matters: lab02_create_agent publishes the agent lab02_chat talks to.
LABS = [
    ("lab01_chat.py", None, "care"),
    ("lab02_create_agent.py", None, "is now at version"),
    ("lab02_chat.py", "Hello\nquit\n", "CareCompanion:"),
    ("lab04_knowledge.py", None, "file search attached"),
    ("lab05_extract.py", None, "Saved extracted markdown"),
    ("lab05_structured.py", None, "patient_name"),
    ("lab03_tools.py", "Does Maria Rivera have appointments?\nquit\n", "Assistant:"),
    ("lab06_care_team.py", None, "cardiology"),
    ("lab06_pipeline.py", None, "555-0100"),
    ("lab07_mcp.py", None, "endpoint"),
]


@pytest.mark.parametrize("script,stdin,phrase", LABS, ids=[lab[0] for lab in LABS])
def test_lab_runs_live(script, stdin, phrase):
    result = subprocess.run(
        [sys.executable, str(SRC / script)],
        input=stdin,
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        cwd=SRC.parent,
    )
    assert result.returncode == 0, result.stderr[-2000:]
    assert phrase.lower() in result.stdout.lower()
