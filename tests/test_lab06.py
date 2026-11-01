import asyncio
import json
import re
import runpy
import sys
import types
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))

import hospital_tools  # noqa: E402

CONTACT = "555-0100"


class FakeAgentTool:
    def __init__(self, agent, name):
        self.agent = agent
        self.name = name


class FakeAgent:
    """Stands in for agent_framework.Agent; run() is scripted per agent name."""

    scripts = {}

    def __init__(self, client=None, name="", instructions="", tools=None, **_):
        self.name = name
        self.instructions = instructions
        self.tools = tools or []
        self.tasks = []

    def as_tool(self, name, description=""):
        return FakeAgentTool(self, name)

    async def run(self, task):
        self.tasks.append(task)
        return await self.scripts[self.name](self, task)


@pytest.fixture
def stub_azure(monkeypatch):
    class FakeSequentialBuilder:
        def __init__(self, participants):
            self.participants = participants

        def build(self):
            return FakeWorkflow(self.participants)

    class FakeWorkflow:
        def __init__(self, participants):
            self.participants = participants

        async def run(self, text):
            for agent in self.participants:
                text = await agent.run(text)
            return types.SimpleNamespace(get_outputs=lambda: [text])

    modules = {
        "dotenv": types.SimpleNamespace(load_dotenv=lambda *a, **k: None),
        "azure": types.ModuleType("azure"),
        "azure.identity": types.SimpleNamespace(AzureCliCredential=lambda: None),
        "agent_framework": types.SimpleNamespace(Agent=FakeAgent),
        "agent_framework.foundry": types.SimpleNamespace(
            FoundryChatClient=lambda **kw: None
        ),
        "agent_framework.orchestrations": types.SimpleNamespace(
            SequentialBuilder=FakeSequentialBuilder
        ),
    }
    for name, module in modules.items():
        monkeypatch.setitem(sys.modules, name, module)
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example.test")
    monkeypatch.setenv("FOUNDRY_MODEL_DEPLOYMENT_NAME", "test-model")


def _tool_named(agent, fn_name):
    return next(t for t in agent.tools if t.__name__ == fn_name)


@pytest.fixture
def care_team(stub_azure, monkeypatch):
    booked = []
    real_book = hospital_tools.book_appointment

    def spy_book(patient_id, department, date):
        booked.append((patient_id, department, date))
        return real_book(patient_id, department, date)

    spy_book.__name__ = "book_appointment"
    monkeypatch.setattr(hospital_tools, "book_appointment", spy_book)

    async def records(agent, task):
        patient = json.loads(_tool_named(agent, "find_patient")("Rivera"))[0]
        return patient["id"]

    async def scheduler(agent, task):
        patient_id = "PAT-1001"
        existing = _tool_named(agent, "get_appointments")(patient_id)
        if existing.startswith("No upcoming"):
            _tool_named(agent, "book_appointment")(patient_id, "Cardiology", "2026-07-28")
        return existing

    async def coordinator(agent, task):
        # The coordinator delegates through its tools: records first, then scheduling.
        out = []
        for tool in agent.tools:
            out.append(await tool.agent.run(task))
        return " | ".join(out)

    FakeAgent.scripts = {
        "RecordsSpecialist": records,
        "SchedulingSpecialist": scheduler,
        "CareCoordinator": coordinator,
    }
    ns = runpy.run_path(str(SRC / "lab06_care_team.py"))
    asyncio.run(ns["main"]())
    return types.SimpleNamespace(ns=ns, booked=booked)


def test_coordinator_calls_both_specialists(care_team):
    coordinator = care_team.ns["coordinator"]
    assert [t.name for t in coordinator.tools] == [
        "records_specialist",
        "scheduling_specialist",
    ]
    assert [t.agent for t in coordinator.tools] == [
        care_team.ns["records"],
        care_team.ns["scheduler"],
    ]
    assert len(care_team.ns["records"].tasks) == 1
    assert len(care_team.ns["scheduler"].tasks) == 1


def test_no_new_booking_for_maria_rivera(care_team):
    assert care_team.booked == []


@pytest.fixture
def pipeline(stub_azure, capsys):
    async def extractor(agent, task):
        return "- Diagnosis: demo\n- Follow-up: cardiology"

    async def writer(agent, task):
        closing = re.search(r"End with: '(.+)'", agent.instructions).group(1)
        return "Here is your summary.\n\n" + closing

    FakeAgent.scripts = {"NoteExtractor": extractor, "PatientWriter": writer}
    ns = runpy.run_path(str(SRC / "lab06_pipeline.py"))
    asyncio.run(ns["main"]())
    return types.SimpleNamespace(ns=ns, out=capsys.readouterr().out.rstrip())


def test_summary_ends_with_the_contact_number(pipeline):
    assert pipeline.out.endswith(f"Call your care team at {CONTACT}.")


def test_writer_adds_no_advice_and_runs_after_extractor(pipeline):
    ns = pipeline.ns
    assert "add no medical advice" in ns["writer"].instructions
    assert ns["workflow"].participants == [ns["extractor"], ns["writer"]]
    assert "Maria Rivera" in ns["extractor"].tasks[0]
