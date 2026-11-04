# QA report - issue 9 - v1

Head: 5e1fcc8 (issue-9-lab02-tests). Python 3.12 venv, SDK mocked.

| AC | Result | Proof |
|---|---|---|
| Agent name carecompanion-agent and safety instructions | pass | `tests/test_lab02.py::test_create_agent_uses_name_model_and_safety_instructions`; mutation: name changed to "x" and "NO MEDICAL ADVICE" removed, test fails both times |
| Second turn keeps first turn context | pass | `tests/test_lab02.py::test_second_turn_keeps_first_turn_context`; mutation: new conversation per turn, test fails |
| pytest passes with no network | pass | `pytest -q` 13 passed; `tests/test_lab02.py` 3 passed with socket.connect and getaddrinfo patched to raise |

Verify command `python3 -m compileall -q src`: ok.
Security pass on the PR diff (3 files, refactor plus tests): 0 findings. No secrets, no new network or identity calls, call shapes to the SDK unchanged.

Test gaps (not written, Low): `main()` wiring is not exercised; `exit` keyword is not tested separately from `quit`.

Local tests: pytest -q
