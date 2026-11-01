# QA v2 · issue 41 · PR 47 · head c89caed

Local tests: /Users/marco/K21/Azure-HealthCare-Agentic-AI/.venv/bin/python -m pytest -q

| AC | Result | Proof |
|---|---|---|
| 1 `az bicep build` on `infra/budget.bicep` | pass | exit 0; all 5 templates in `infra/` build |
| 2 75% alert, no email in committed files | pass | `actual75` threshold 75 Actual; `contactEmail` has no default; scan of infra, tests, README, RUNBOOK, .github finds no address |
| 3 test covers both, `pytest` passes | pass | `tests/test_infra_budget.py` 8 tests; full suite 83 passed |
| 4 README or runbook names the step | pass | `docs/RUNBOOK.md` one line; README counts 5 templates |

Mutation check (changes reverted): giving `contactEmail` a default fails 2 tests; threshold 75 to 70 fails 3 tests.

Security pass: `$budget_email` is quoted in `deploy.sh`; no secrets; template never deployed.

Note (not a failure): `--what-if` combined with `--budget-email` previews main.bicep only, so the budget is not previewed.
