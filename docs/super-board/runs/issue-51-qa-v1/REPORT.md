# issue-51 QA v1 (head cc47bb0)

$ python3 -m compileall -q src  -> exit 0
$ az bicep build --file infra/main.bicep --stdout -> exit 0
$ pytest -q
........................................................................ [ 85%]
............                                                             [100%]
84 passed in 12.94s

## Mutation check: filterwarnings line replaced by pass
=========================== short test summary info ============================
FAILED tests/test_lab07.py::test_lab07_hides_only_the_mcp_ping_deprecation_warning
1 failed, 7 passed in 1.06s
## Restored
8 passed in 0.75s

## Cause
agent_framework/_mcp.py:657 await self._client.send_ping() (library); mcp/client/client.py:527 emits the warning. src/lab07_mcp.py has no ping call.
pr-security-review: 0 findings (one regex-scoped warnings filter, no input/auth/data path)
