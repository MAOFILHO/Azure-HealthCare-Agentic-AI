# issue-78 QA v2 live run

Head: ea9c0cd
Command: RUN_LIVE=1 pytest tests/live -m live -v (FOUNDRY_* exported from the k21-healthcare deployment, values not recorded)

10 passed in 140.00s: lab01_chat, lab02_create_agent, lab02_chat, lab04_knowledge, lab05_extract, lab05_structured, lab03_tools, lab06_care_team, lab06_pipeline, lab07_mcp.

Offline: pytest 107 passed, 10 skipped. pytest -W error 107 passed, 10 skipped. pytest -m live without RUN_LIVE: 10 skipped.
Side effect: lab05_extract rewrote data/discharge_note.md; restored, not committed.
