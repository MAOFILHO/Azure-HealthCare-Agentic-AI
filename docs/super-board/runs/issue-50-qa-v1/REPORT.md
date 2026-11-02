# QA report · issue 50 · v1

Head under test: `874e1df`. Docs-only change, no screenshots (no UI).

| AC | Check | Result |
|---|---|---|
| 1 | `docs/agents/factory-lessons.md` has 4 `## N.` sections, each with one Symptom, Cause and Fix line (awk count 3,3,3,3) | pass |
| 2 | `docs/agents/issue-tracker.md` line 5 links `factory-lessons.md`; target file exists | pass |
| 3 | grep for URLs, GUIDs, subscription, key, secret, token, password, long base64 in both added texts: 0 hits | pass |

Verify commands (all from `verify_commands`): `compileall` exit 0 · `pytest -q` 83 passed · `az bicep build` exit 0.

Test-gap check: docs only, no code branch to cover. `n/a`.
pr-security-review: no code in diff, 0 findings.
