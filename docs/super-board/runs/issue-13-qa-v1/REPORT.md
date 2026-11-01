# issue 13 QA v1 (non-visual, no screenshots)

$ python -m pytest tests -q
..............                                                           [100%]
14 passed in 2.91s

$ socket.connect disabled, python -m pytest tests/test_lab06.py
....                                                                     [100%]
4 passed in 0.02s

Mutants (each reverted after run):
- drop scheduler tool from coordinator -> test_coordinator_calls_both_specialists FAILED
- contact number 555-0100 -> 555-0199 -> test_summary_ends_with_the_contact_number FAILED
- writer instruction 'add no medical advice' -> 'add medical advice' -> test_writer_adds_no_advice FAILED
- swap workflow order -> 2 FAILED
- remove PAT-1001 appointments from data (forces a booking) -> test_no_new_booking_for_maria_rivera FAILED (assertion, after spy recursion fix)

pr-security-review: 0 findings (tests-only diff, no network, no secrets, no dotenv read)
