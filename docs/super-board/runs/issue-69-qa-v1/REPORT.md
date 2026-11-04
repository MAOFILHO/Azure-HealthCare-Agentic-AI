# QA v1 - issue 69 (lab02 agent_reference)

Non-visual change, no screenshots.

| AC | Check | Result |
|---|---|---|
| 1 | `grep agent_name src/lab02_chat.py` has no match; line 36 is `project.get_openai_client()` | pass |
| 2 | `test_every_response_targets_the_agent_via_agent_reference` asserts both turns send the reference | pass |
| 3 | `pytest -q` | 89 passed |
| 4 | `git diff --name-only origin/staging...HEAD` | src/lab02_chat.py, tests/test_lab02.py |

Mutation check: deleting `extra_body=AGENT_REFERENCE,` turned the new test red (1 failed, 3 passed). Restored, green (4 passed). The mutation was not committed.

Security pass: pr-security-review on the 2-file diff, 0 findings. No keys, no endpoint literals; the endpoint still comes from `FOUNDRY_PROJECT_ENDPOINT`.

Test gaps (not written): `main()` is not unit-tested, so AC1 is checked by grep, not by a test. Low.
