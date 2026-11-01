# QA v1 · issue 35 · head 2459e4a

Fresh venv, `pip install -r requirements.txt` (Python 3.14.x, arm64).

- AC1: requirements.txt lines 8-9 are `mcp>=2,<3` and `tenacity` -> pass
- AC2: installed mcp 2.3.0, tenacity 9.2.1; `python -c "from mcp import Client"` prints `ok` -> pass
- AC3: `python -m pytest -q` -> 72 passed in 12.22s -> pass

Test-gap check: diff is two dependency lines, no code path; no test to add.
pr-security-review: 0 findings (unpinned `tenacity` noted as Low, not a failure).
