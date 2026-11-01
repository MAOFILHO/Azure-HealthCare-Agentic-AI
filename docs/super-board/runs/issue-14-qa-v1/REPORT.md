# QA v1 · issue #14 · head 7fc2c08

Non-visual: no screenshots (tests only, no UI).

| AC | Proof |
|---|---|
| MCP URL checked | `tests/test_lab07.py::test_learn_tool_points_at_microsoft_learn_mcp_server`; mutation (URL changed) turns it red |
| Cleanup scope | `test_cleanup_deletes_only_the_lab_vector_store_and_agent`, `..._every_rerun_copy...`, `..._nothing_when_only_foreign...`; mutation (drop either name filter) turns 2 tests red |
| No network | full suite, 15 passed, with socket connect and getaddrinfo patched to raise |

Names match the labs: `carecompanion-agent` (lab02, lab04), `northfield-policies` (lab04).
Security: pr-security-review, 0 findings (deletion scope narrowed, no input or secrets).
Local tests: `.venv/bin/python -m pytest -q`
