import runpy
import sys
import time
import types
from pathlib import Path
from unittest.mock import DEFAULT, MagicMock

import httpx
import openai
import pytest

LAB04 = Path(__file__).resolve().parent.parent / "src" / "lab04_knowledge.py"
POLICY_DIR = LAB04.parent.parent / "data" / "policies"


class FakeFileSearchTool:
    def __init__(self, vector_store_ids):
        self.vector_store_ids = vector_store_ids


class FakePromptAgentDefinition:
    def __init__(self, model, instructions, tools):
        self.model = model
        self.instructions = instructions
        self.tools = tools


def not_found():
    request = httpx.Request("GET", "https://example.test")
    return openai.NotFoundError(
        "404", response=httpx.Response(404, request=request), body=None
    )


def timed_out():
    return openai.APITimeoutError(request=httpx.Request("POST", "https://example.test"))


def completed():
    return types.SimpleNamespace(status="completed", last_error=None)


def make_fail_once(client, path, error=not_found):
    """The call at path (e.g. "files.create") raises error once, then works."""
    mock = client
    for part in path.split("."):
        mock = getattr(mock, part)
    then = mock.side_effect
    seen = []

    def effect(*args, **kwargs):
        seen.append(1)
        if len(seen) == 1:
            raise error()
        return then(*args, **kwargs) if then else DEFAULT

    mock.side_effect = effect


@pytest.fixture
def run_lab04(monkeypatch):
    """Run lab04 with every Azure dependency mocked, so there is no network."""

    def run(retrieve_side_effect=None, attach_side_effect=None, fail_once=None,
            fail_with=not_found):
        openai_client = MagicMock(name="openai_client")
        openai_client.vector_stores.create.return_value.id = "vs-test"
        files = openai_client.vector_stores.files
        files.retrieve.side_effect = retrieve_side_effect or (lambda *a, **k: completed())
        files.create.side_effect = attach_side_effect
        if fail_once:
            make_fail_once(openai_client, fail_once, fail_with)
        project = MagicMock(name="project")
        project.get_openai_client.return_value = openai_client

        modules = {
            "dotenv": types.SimpleNamespace(load_dotenv=lambda *a, **k: None),
            "azure": types.ModuleType("azure"),
            "azure.identity": types.SimpleNamespace(DefaultAzureCredential=MagicMock()),
            "azure.ai": types.ModuleType("azure.ai"),
            "azure.ai.projects": types.SimpleNamespace(
                AIProjectClient=MagicMock(return_value=project)
            ),
            "azure.ai.projects.models": types.SimpleNamespace(
                FileSearchTool=FakeFileSearchTool,
                PromptAgentDefinition=FakePromptAgentDefinition,
            ),
        }
        for name, module in modules.items():
            monkeypatch.setitem(sys.modules, name, module)
        monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example.test")
        monkeypatch.setenv("FOUNDRY_MODEL_DEPLOYMENT_NAME", "test-model")

        clock = {"now": 0.0}
        monkeypatch.setattr(time, "monotonic", lambda: clock["now"])
        monkeypatch.setattr(time, "sleep", lambda s: clock.update(now=clock["now"] + s))

        runpy.run_path(str(LAB04))
        return types.SimpleNamespace(openai_client=openai_client, project=project)

    return run


@pytest.fixture
def lab04(run_lab04):
    return run_lab04()


def test_all_three_policy_files_are_uploaded(lab04):
    expected = sorted(p.name for p in POLICY_DIR.glob("*.md"))
    assert len(expected) == 3

    client = lab04.openai_client
    assert not client.vector_stores.files.upload_and_poll.called

    uploads = client.files.create.call_args_list
    assert len(uploads) == 3
    assert {c.kwargs["purpose"] for c in uploads} == {"assistants"}
    assert sorted(Path(c.kwargs["file"].name).name for c in uploads) == expected

    attached = client.vector_stores.files.create.call_args_list
    assert len(attached) == 3
    assert {c.kwargs["vector_store_id"] for c in attached} == {"vs-test"}


def test_not_found_on_first_poll_is_retried(run_lab04):
    calls = []

    def retrieve(*args, **kwargs):
        calls.append(1)
        if len(calls) == 1:
            raise not_found()
        return completed()

    lab = run_lab04(retrieve)
    assert len(calls) == 4  # 1 miss then ok for file 1, then ok for files 2 and 3
    assert lab.project.agents.create_version.called


def test_failed_file_raises_clear_error(run_lab04):
    failed = types.SimpleNamespace(status="failed", last_error="bad file")
    with pytest.raises(RuntimeError, match="failed"):
        run_lab04(lambda *a, **k: failed)


def test_never_ready_times_out(run_lab04):
    in_progress = types.SimpleNamespace(status="in_progress", last_error=None)
    with pytest.raises(TimeoutError, match="60"):
        run_lab04(lambda *a, **k: in_progress)


def test_poll_always_not_found_raises_after_6_tries(run_lab04):
    calls = []

    def retrieve(*args, **kwargs):
        calls.append(1)
        raise not_found()

    with pytest.raises(openai.NotFoundError):
        run_lab04(retrieve)
    assert len(calls) == 6


@pytest.mark.parametrize("call", [
    "vector_stores.create",
    "files.create",
    "vector_stores.files.create",
    "vector_stores.files.retrieve",
])
def test_every_file_and_vector_store_call_retries_404(run_lab04, call):
    lab = run_lab04(fail_once=call)
    assert lab.project.agents.create_version.called


def test_timed_out_upload_is_retried(run_lab04):
    lab = run_lab04(fail_once="files.create", fail_with=timed_out)
    assert lab.openai_client.files.create.call_count == 4  # 1 timeout, then 3 files
    assert lab.project.agents.create_version.called


def test_upload_sends_the_path_so_the_sdk_can_resend_it(lab04):
    for call in lab04.openai_client.files.create.call_args_list:
        assert isinstance(call.kwargs["file"], Path)


def test_client_has_a_bounded_timeout_and_retries(lab04):
    kwargs = lab04.project.get_openai_client.call_args.kwargs
    assert kwargs["timeout"] == 60
    assert kwargs["max_retries"] == 3


def test_not_found_on_attach_is_retried(run_lab04):
    calls = []

    def attach(*args, **kwargs):
        calls.append(1)
        if len(calls) == 1:
            raise not_found()

    lab = run_lab04(attach_side_effect=attach)
    assert len(calls) == 4  # 1 miss then ok for file 1, then ok for files 2 and 3
    assert lab.project.agents.create_version.called


def test_attach_never_found_raises_after_6_tries_2_seconds_apart(run_lab04):
    calls = []

    def attach(*args, **kwargs):
        calls.append(time.monotonic())
        raise not_found()

    with pytest.raises(openai.NotFoundError):
        run_lab04(attach_side_effect=attach)
    assert len(calls) == 6
    assert calls[-1] - calls[0] == 10


def test_agent_has_file_search_tool_attached(lab04):
    kwargs = lab04.project.agents.create_version.call_args.kwargs
    (tool,) = kwargs["definition"].tools
    assert isinstance(tool, FakeFileSearchTool)
    assert tool.vector_store_ids == ["vs-test"]


AGENT_REFERENCE = {"name": "carecompanion-agent", "type": "agent_reference"}


def test_client_is_not_agent_bound(lab04):
    for call in lab04.project.get_openai_client.call_args_list:
        assert "agent_name" not in call.kwargs


def test_agent_response_sends_agent_reference(lab04):
    kwargs = lab04.openai_client.responses.create.call_args.kwargs
    assert kwargs["extra_body"] == {"agent_reference": AGENT_REFERENCE}
