import runpy
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

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


@pytest.fixture
def lab04(monkeypatch):
    """Run lab04 with every Azure dependency mocked, so there is no network."""
    openai_client = MagicMock(name="openai_client")
    openai_client.vector_stores.create.return_value.id = "vs-test"
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

    runpy.run_path(str(LAB04))
    return types.SimpleNamespace(openai_client=openai_client, project=project)


def test_all_three_policy_files_are_uploaded(lab04):
    expected = sorted(p.name for p in POLICY_DIR.glob("*.md"))
    assert len(expected) == 3

    uploads = lab04.openai_client.vector_stores.files.upload_and_poll.call_args_list
    assert len(uploads) == 3
    assert sorted(Path(c.kwargs["file"].name).name for c in uploads) == expected
    assert {c.kwargs["vector_store_id"] for c in uploads} == {"vs-test"}


def test_agent_has_file_search_tool_attached(lab04):
    kwargs = lab04.project.agents.create_version.call_args.kwargs
    (tool,) = kwargs["definition"].tools
    assert isinstance(tool, FakeFileSearchTool)
    assert tool.vector_store_ids == ["vs-test"]
