# CareCompanion starter files

Companion bundle to "Building CareCompanion - AI-103 Healthcare Lab Guide".
Every file here matches the guide exactly; the guide explains each one.

## Setup (Lab 1 walks through all of this)
1. Copy this folder somewhere as your working project.
2. Rename `env.sample` to `.env` and paste in your own endpoints and
   deployment name.
3. Rename `gitignore` to `.gitignore`.
4. Create the virtual environment and install packages:
   python -m venv .venv  ->  activate it  ->  pip install -r requirements.txt

## Contents
- requirements.txt, env.sample, gitignore  - project config (Lab 1)
- src/                                     - all lab scripts (Labs 1-7)
- data/patients.json, appointments.json    - mock EHR data (Lab 3)
- data/policies/*.md                       - policy documents for RAG (Lab 4)
- data/discharge_note.pdf                  - synthetic note for Lab 5
  (discharge_note_source.txt is the same text if you prefer to make
  your own PDF, as the guide describes)

All data is synthetic. Never use real patient data in a lab environment.
