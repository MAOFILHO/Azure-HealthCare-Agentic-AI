# QA v1 - issue 41 (budget alert) @ 8977733

| AC | Result | Proof |
|---|---|---|
| az bicep build passes | pass | `az bicep build --file infra/budget.bicep` exit 0 |
| 75% alert, no email in committed files | pass | `tests/test_infra_budget.py` (alerts, no-default, no-email scan); mutation 75 to 76 turned the test red, restored green |
| test covers both, pytest passes | pass | 82 passed |
| README or runbook names the step | pass | `docs/RUNBOOK.md` optional budget step |

Also: `bash -n infra/deploy.sh` clean. pr-security-review: 0 findings (email is a CLI parameter, never written or echoed).
Local tests: python -m pytest -q
