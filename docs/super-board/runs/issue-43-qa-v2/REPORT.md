# QA v2 issue 43 (head bbcc07a)
- R1 re-check: verify_commands[1] resolves the repo venv via git-common-dir; pytest ran from the issue worktree with VIRTUAL_ENV unset: 74 passed
- compileall -q src: exit 0
- az bicep build infra/main.bicep --stdout: exit 0 (upgrade notice only)
- config JSON parses; super-board-verification-ready.py exit 0
- security pass: config-only diff, static shell strings, no input interpolation, no findings
Local tests: python3 -m pytest -q
