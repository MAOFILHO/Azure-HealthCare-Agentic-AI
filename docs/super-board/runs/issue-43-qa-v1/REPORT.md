# QA v1 issue 43
- compileall: exit 0
- pytest -q: 74 passed
- az bicep build infra/main.bicep: exit 0 (upgrade notice only)
- config JSON parses; super-board-verification-ready.py exit 0
- security pass: config-only diff, no findings
Local tests: python3 -m pytest -q
