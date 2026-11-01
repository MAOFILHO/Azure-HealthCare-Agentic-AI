# issue 3 QA v1 (non-visual, no screenshots)
$ az bicep build --file infra/main.bicep --stdout  -> exit 0, 0 errors
$ python3 -m unittest tests.test_infra_bicep -v
test_builds_with_no_errors (tests.test_infra_bicep.MainBicepTest.test_builds_with_no_errors) ... ok
test_defaults_match_guide (tests.test_infra_bicep.MainBicepTest.test_defaults_match_guide) ... ok
test_module_endpoint_values_are_not_openai_v1 (tests.test_infra_bicep.MainBicepTest.test_module_endpoint_values_are_not_openai_v1) ... ok
test_outputs_endpoints_without_openai_v1_suffix (tests.test_infra_bicep.MainBicepTest.test_outputs_endpoints_without_openai_v1_suffix) ... ok
test_subscription_scope (tests.test_infra_bicep.MainBicepTest.test_subscription_scope) ... ok

----------------------------------------------------------------------
Ran 5 tests in 2.806s

OK
$ python3 -m compileall -q src -> exit 0
mutation: foundry.bicep api/projects -> openai/v1/projects: new test FAILED; restored: OK
pr-security-review: 0 findings
