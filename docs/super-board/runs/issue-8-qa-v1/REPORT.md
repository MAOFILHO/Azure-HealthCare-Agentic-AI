# issue-8 QA v1
$ python -m pytest tests/test_lab01.py tests/test_hospital_tools.py -q
........                                                                 [100%]
8 passed in 0.01s

mutation: lab01_chat.main() env read replaced by literal -> test_main_reads_the_deployment_name_from_the_environment FAILED (red)
mutation: print(response.output_text) replaced by pass -> 2 failed (red)
restored -> green. SDK not installed in this venv, only pytest: runs offline.
pr-security-review: 0 findings
