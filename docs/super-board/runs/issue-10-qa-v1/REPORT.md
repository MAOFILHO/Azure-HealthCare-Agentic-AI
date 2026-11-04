# QA v1 for issue 10 (head 73772e7)

## pytest (python3.12, full suite)
............                                                             [100%]
12 passed in 3.25s

## pytest with sockets denied (connect, create_connection, getaddrinfo)
12 passed

## mutation checks (reverted after)
- drop book_appointment from tools: 2 failed
- replace book_appointment with a lambda that skips hospital_tools: 2 failed

## security pass
Test-only diff (tests/test_lab03_tools.py). Endpoint is example.invalid, model name is a placeholder, no secrets, no dotenv read. No findings.
