# QA v1 issue 15

Head tested: aefb261
Local tests: python -m pytest -q  (14 passed)

| AC | Check | Result |
|---|---|---|
| Workflow runs on PRs to staging | `on: pull_request: branches: [staging]` in ci.yml, pinned by `test_runs_on_pull_requests_to_staging` | pass |
| Fails if a Bicep file does not build | `az bicep build` over `infra/*.bicep` under `set -e`; real build of both files exit 0, a broken file exit 1 | pass |
| Fails if a test fails | `python -m pytest` as its own step, no `continue-on-error`, no `\|\| true` | pass |

Security pass: workflow has `permissions: contents: read`, no secrets, no untrusted input interpolated. No findings.
Not run: the workflow on GitHub Actions itself (needs the PR to run; shown on the PR checks).
