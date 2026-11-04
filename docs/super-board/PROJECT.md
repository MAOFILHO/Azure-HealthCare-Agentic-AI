# CareCompanion

Healthcare assistant built on Azure and Microsoft Foundry. Demo data only.

## Layout
- `src/` lab scripts `lab01` to `lab07` plus `hospital_tools.py` (agent tools).
- `data/` demo patients, appointments, discharge note, and 3 policy files (billing, discharge, visiting hours).
- `docs/` 3 PDFs: Architecture Overview, Project Overview, User Guide.

## Run
Python 3.12. Install with `pip install -r requirements.txt`. Each lab runs as `python src/labNN_*.py`. Azure sign-in comes from the environment, never from files in the repo.

## Checks
No test suite yet. A ticket that adds tests must say how to run them.
