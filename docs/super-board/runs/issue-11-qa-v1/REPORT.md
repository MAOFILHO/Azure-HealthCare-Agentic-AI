# issue-11 QA v1 @ 5668262
$ python -m pytest -q  (only pytest installed; azure/dotenv absent -> proves no network/SDK)
............                                                             [100%]
12 passed in 2.84s

mutation 1: tools=[] -> test_agent_has_file_search_tool_attached FAILED (caught)
mutation 2: glob limited to visiting*.md -> test_all_three_policy_files_are_uploaded FAILED (caught)
security pass: diff is one test file, no secrets/network/dotenv; 0 findings
