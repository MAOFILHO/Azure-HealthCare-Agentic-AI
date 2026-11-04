# QA report, issue 58, v1

Head tested: 42fb58a (docs only, no UI, no screenshots).

| AC | Result | Proof |
|---|---|---|
| 1 soft-deleted account and FlagMustBeSetForRestore | pass | README.md line 152; infra/destroy.sh runs `az group delete` only |
| 2 20 USD budget, --budget-email, RUNBOOK link | pass | README.md line 188; infra/budget.bicep `amount int = 20`; infra/deploy.sh line 22 |
| 3 thresholds match | pass | infra/budget.bicep thresholds 75 and 100, both Actual |
| 4 no email, endpoint, subscription id | pass | regex grep of README.md found no match |
| 5 only README.md changes | pass | `git diff --name-only origin/staging...HEAD` lists README.md only |
| 6 offline pytest | pass | 84 passed; compileall src ok |

Security pass: pr-security-review on a 3-line docs diff, 0 findings.
Test gaps (not written): none; no code changed.
