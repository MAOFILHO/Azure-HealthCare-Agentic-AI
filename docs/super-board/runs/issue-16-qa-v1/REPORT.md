# QA v1 - issue #16 runbook

Head tested: `3a77495`. Non-visual card: no screenshots.

| AC | Result | Proof |
|---|---|---|
| Runbook lists every lab in the guide's order | pass | `tests/test_runbook.py::test_labs_appear_in_the_guides_order`; swapping Lab 1 and Lab 3 turns it red |
| Contains no secrets or endpoints | pass | `test_contains_no_secrets_or_endpoints`; adding a `*.azure.com` URL turns it red; manual grep for key, secret, token, password finds none |
| README links the runbook | pass | `test_readme_links_the_runbook`; renaming the link turns it red |

Runbook claims checked against the code: deploy message `infra/deploy.sh:54`, destroy message `infra/destroy.sh:15`, group name `K21-project-rg`, agent version line `src/lab02_create_agent.py:49`, `Indexed` line `src/lab04_knowledge.py:45`, cleanup lines `src/lab07_cleanup.py:18,23,34`, lab05 output `data/discharge_note.md` from `with_suffix(".md")`. All match.

Local tests: `python3 -m unittest tests.test_runbook` (6 pass). `python3 -m compileall -q src` clean.
Full suite on this Mac: 6 import errors from missing local packages (pytest, azure.ai.projects), none in files this PR touches. CI installs them.

pr-security-review: 0 findings (docs, one offline test, no runtime code).

Test gaps (not written):
- Medium: no test ties the quoted deploy and destroy messages to the scripts; a reworded script message would leave the runbook stale.
- Low: `src/lab07_cleanup.py:35` prints `rg-northfield-ai`, while the runbook and `infra/destroy.sh` use `K21-project-rg`. Outside this card.
