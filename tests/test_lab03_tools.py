import asyncio
import importlib
import json
import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import hospital_tools


class FakeAgent:
    """Stands in for agent_framework.Agent: records what lab03 wires up."""

    instances = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        FakeAgent.instances.append(self)

    def create_session(self):
        return object()


@pytest.fixture
def lab03(monkeypatch):
    """Import lab03_tools with the Azure and Agent Framework pieces faked."""
    def module(name, **attrs):
        mod = types.ModuleType(name)
        mod.__dict__.update(attrs)
        monkeypatch.setitem(sys.modules, name, mod)

    module("dotenv", load_dotenv=lambda: None)
    module("azure")
    module("azure.identity", AzureCliCredential=lambda: object())
    module("agent_framework", Agent=FakeAgent)
    module("agent_framework.foundry", FoundryChatClient=lambda **kw: object())
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example.invalid")
    monkeypatch.setenv("FOUNDRY_MODEL_DEPLOYMENT_NAME", "demo-model")
    FakeAgent.instances.clear()
    sys.modules.pop("lab03_tools", None)
    yield importlib.import_module("lab03_tools")
    sys.modules.pop("lab03_tools", None)


def build_agent(lab03, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _prompt="": "quit")
    asyncio.run(lab03.main())
    return FakeAgent.instances[-1]


def test_agent_registers_the_three_tool_names(lab03, monkeypatch):
    agent = build_agent(lab03, monkeypatch)
    names = [tool.__name__ for tool in agent.kwargs["tools"]]
    assert names == ["find_patient", "get_appointments", "book_appointment"]


def test_book_appointment_call_reaches_hospital_tools(lab03, monkeypatch):
    calls = []

    def spy(patient_id, department, preferred_day):
        calls.append((patient_id, department, preferred_day))
        return json.dumps({"status": "confirmed"})

    monkeypatch.setattr(hospital_tools, "book_appointment", spy)
    sys.modules.pop("lab03_tools", None)
    lab03 = importlib.import_module("lab03_tools")

    agent = build_agent(lab03, monkeypatch)
    book = next(t for t in agent.kwargs["tools"] if t.__name__ == "spy")
    result = book("PAT-1001", "Cardiology", "2026-12-01")

    assert calls == [("PAT-1001", "Cardiology", "2026-12-01")]
    assert json.loads(result)["status"] == "confirmed"
