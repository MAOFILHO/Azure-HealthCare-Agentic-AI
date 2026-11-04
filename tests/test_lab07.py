import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import openai

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import lab07_cleanup
from lab07_cleanup import cleanup
from lab07_mcp import create_agent, learn_tool


def test_learn_tool_points_at_microsoft_learn_mcp_server():
    tool = learn_tool()

    assert tool.url == "https://learn.microsoft.com/api/mcp"


def test_create_agent_attaches_the_learn_tool():
    tool = learn_tool()

    agent = create_agent(MagicMock(), tool)

    assert agent.mcp_tools == [tool]
    assert "Microsoft Learn" in agent.default_options["instructions"]


def fake_clients(agent_names, stores):
    project = MagicMock()
    project.agents.list.return_value = [SimpleNamespace(name=n) for n in agent_names]
    openai_client = MagicMock()
    openai_client.vector_stores.list.return_value = [
        SimpleNamespace(id=i, name=n) for i, n in stores
    ]
    return project, openai_client


def test_cleanup_deletes_only_the_lab_vector_store_and_agent():
    project, openai_client = fake_clients(
        ["carecompanion-agent", "someone-elses-agent"],
        [("vs_lab", "northfield-policies"), ("vs_other", "team-docs")],
    )

    cleanup(project, openai_client)

    project.agents.delete.assert_called_once_with("carecompanion-agent")
    openai_client.vector_stores.delete.assert_called_once_with(
        vector_store_id="vs_lab"
    )


def test_cleanup_deletes_every_rerun_copy_of_the_lab_vector_store():
    project, openai_client = fake_clients(
        [], [("vs_1", "northfield-policies"), ("vs_2", "northfield-policies")]
    )

    cleanup(project, openai_client)

    deleted = [c.kwargs["vector_store_id"]
               for c in openai_client.vector_stores.delete.call_args_list]
    assert deleted == ["vs_1", "vs_2"]


def test_cleanup_deletes_nothing_when_only_foreign_resources_exist():
    project, openai_client = fake_clients(
        ["other-agent"], [("vs_other", "team-docs")]
    )

    cleanup(project, openai_client)

    project.agents.delete.assert_not_called()
    openai_client.vector_stores.delete.assert_not_called()


def test_cleanup_prints_the_group_name_that_destroy_sh_deletes(monkeypatch, capsys):
    import lab07_cleanup

    destroy = (Path(__file__).resolve().parent.parent / "infra" / "destroy.sh").read_text()
    group = next(
        line.split("=", 1)[1].strip('"')
        for line in destroy.splitlines()
        if line.startswith("group=")
    )
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example.test")
    monkeypatch.setattr(lab07_cleanup, "load_dotenv", lambda: None)
    monkeypatch.setattr(lab07_cleanup, "DefaultAzureCredential", MagicMock())
    project = MagicMock()
    project.agents.list.return_value = []
    project.get_openai_client.return_value.vector_stores.list.return_value = []
    monkeypatch.setattr(lab07_cleanup, "AIProjectClient", MagicMock(return_value=project))

    lab07_cleanup.main()

    assert f"--name {group} " in capsys.readouterr().out


def test_cleanup_reads_every_list_to_the_end_before_deleting():
    state = {"reading": 0}

    def paged(items):
        state["reading"] += 1
        yield from items
        state["reading"] -= 1

    def delete_guard(*args, **kwargs):
        assert state["reading"] == 0, "deleted while a list was still being read"

    project, openai_client = MagicMock(), MagicMock()
    project.agents.list.side_effect = lambda: paged(
        [SimpleNamespace(name="carecompanion-agent"), SimpleNamespace(name="x")]
    )
    openai_client.vector_stores.list.side_effect = lambda: paged(
        [SimpleNamespace(id="vs_1", name="northfield-policies"),
         SimpleNamespace(id="vs_2", name="northfield-policies")]
    )
    project.agents.delete.side_effect = delete_guard
    openai_client.vector_stores.delete.side_effect = delete_guard

    cleanup(project, openai_client)

    project.agents.delete.assert_called_once_with("carecompanion-agent")
    assert openai_client.vector_stores.delete.call_count == 2


def test_lab07_hides_only_the_mcp_ping_deprecation_warning():
    import importlib
    import warnings

    import lab07_mcp
    from mcp import MCPDeprecationWarning

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        importlib.reload(lab07_mcp)
        warnings.warn(
            "ping is removed as of 2026-07-28; the method only works under "
            "mode='legacy'.",
            MCPDeprecationWarning,
        )
        warnings.warn(
            "The logging capability is deprecated as of 2026-07-28.",
            MCPDeprecationWarning,
        )

    assert [str(w.message) for w in caught] == [
        "The logging capability is deprecated as of 2026-07-28."
    ]


def not_found():
    response = MagicMock(status_code=404, headers={})
    return openai.NotFoundError("Subdomain does not map to a resource", response=response, body=None)


def test_cleanup_retries_a_transient_404_on_vector_store_delete(monkeypatch):
    monkeypatch.setattr(lab07_cleanup.time, "sleep", MagicMock())
    project, openai_client = fake_clients([], [("vs_1", "northfield-policies")])
    openai_client.vector_stores.delete.side_effect = [not_found(), not_found(), None]

    cleanup(project, openai_client)

    assert openai_client.vector_stores.delete.call_count == 3


def test_cleanup_warns_and_still_deletes_the_agent_on_a_permanent_404(monkeypatch, capsys):
    sleep = MagicMock()
    monkeypatch.setattr(lab07_cleanup.time, "sleep", sleep)
    project, openai_client = fake_clients(
        ["carecompanion-agent"],
        [("vs_1", "northfield-policies"), ("vs_2", "northfield-policies")],
    )
    openai_client.vector_stores.delete.side_effect = lambda vector_store_id: (
        (_ for _ in ()).throw(not_found()) if vector_store_id == "vs_1" else None
    )

    cleanup(project, openai_client)

    out = capsys.readouterr().out
    warnings = [line for line in out.splitlines() if "vs_1" in line and "warn" in line.lower()]
    assert len(warnings) == 1
    assert openai_client.vector_stores.delete.call_count == 5 + 1
    sleep.assert_called_with(3)
    project.agents.delete.assert_called_once_with("carecompanion-agent")
