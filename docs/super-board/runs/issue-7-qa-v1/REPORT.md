# QA v1 issue 7

Head tested: 812e055
Command: python3 -m pytest tests

```
============================= test session starts ==============================
platform darwin -- Python 3.14.7, pytest-9.2.0, pluggy-1.7.0 -- /private/tmp/claude-501/-Users-marco-K21-Azure-HealthCare-Agentic-AI/36feb72c-a43f-43b6-8956-1d81be3676f7/scratchpad/venv/bin/python
rootdir: ~/K21/Azure-HealthCare-Agentic-AI/.claude/worktrees/issue-7-qa
collecting ... collected 5 items

tests/test_hospital_tools.py::test_find_patient_finds_maria_rivera PASSED [ 20%]
tests/test_hospital_tools.py::test_find_patient_unknown_name_returns_nothing PASSED [ 40%]
tests/test_hospital_tools.py::test_get_appointments_lists_cardiology_follow_up PASSED [ 60%]
tests/test_hospital_tools.py::test_get_appointments_unknown_patient_returns_nothing PASSED [ 80%]
tests/test_hospital_tools.py::test_book_appointment_returns_confirmation_code_and_status PASSED [100%]

============================== 5 passed in 0.01s ===============================
```

Mutation check: book_appointment status confirmed -> pending turned test_book_appointment_returns_confirmation_code_and_status red; restored, green.
Non-visual ACs: no screenshots by design.
