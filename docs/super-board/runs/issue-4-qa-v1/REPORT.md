# QA v1 issue #4 (non-visual, no screenshots)

$ az bicep build --file infra/main.bicep --stdout  -> exit 0
$ python3 -m unittest tests.test_infra_bicep -v  -> 10 tests OK
$ python3 -m compileall -q src  -> exit 0
pr-security-review: 0 findings (IaC only, no secrets, no network/identity changes)
