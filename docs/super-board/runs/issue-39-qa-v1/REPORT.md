# QA v1 · issue #39 · head 6609ac1

| AC | Proof |
|---|---|
| cleanup() lists agents and stores before any delete | `src/lab07_cleanup.py:15-16` reads both lists with `list()`; loops at :18 and :23 iterate the copies |
| A test fails if a delete happens while a list is still being read | `tests/test_lab07.py::test_cleanup_reads_every_list_to_the_end_before_deleting` goes red on the pre-fix `cleanup()` (AssertionError at test_lab07.py:105, "deleted while a list was still being read"), green on the fix |
| pytest passes | `.venv/bin/python -m pytest -q` → 74 passed |

Mutation check: pre-fix `src/lab07_cleanup.py` (from 5d0eec4) restored → 1 failed, 6 passed in test_lab07.py; fix restored → 74 passed. The mutation was not committed.
pr-security-review: 0 findings (call order change only, no new input, I/O or secrets).
Non-visual change: no screenshots, intentionally.
Not run: live Foundry cleanup (no cloud access in this lane).
