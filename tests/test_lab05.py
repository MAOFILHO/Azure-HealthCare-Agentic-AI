import json
import re
import runpy
import sys
import types
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent.parent / "src"
NOTE_MD = Path(__file__).resolve().parent.parent / "data" / "discharge_note.md"

EXPECTED_FIELDS = [
    "patient_name",
    "discharge_date",
    "diagnosis",
    "medications",
    "follow_up",
    "warning_signs",
]

RECORD = {
    "patient_name": "Maria Rivera",
    "discharge_date": "2026-07-15",
    "diagnosis": "Coronary artery disease",
    "medications": [{"name": "Aspirin", "dose": "81 mg", "schedule": "once daily"}],
    "follow_up": {"department": "Cardiology", "timeframe": "2 weeks"},
    "warning_signs": ["Chest pain or pressure"],
}


def stub_module(monkeypatch, name, **attrs):
    module = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    monkeypatch.setitem(sys.modules, name, module)
    return module


@pytest.fixture
def azure_env(monkeypatch):
    monkeypatch.setenv("FOUNDRY_RESOURCE_ENDPOINT", "https://example.invalid/")
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example.invalid/proj")
    monkeypatch.setenv("FOUNDRY_MODEL_DEPLOYMENT_NAME", "demo-model")
    stub_module(monkeypatch, "dotenv", load_dotenv=lambda *a, **k: None)
    stub_module(
        monkeypatch, "azure.identity", DefaultAzureCredential=lambda: object()
    )
    stub_module(monkeypatch, "azure")
    stub_module(monkeypatch, "azure.ai")


def test_extract_writes_discharge_note_md(monkeypatch, azure_env, capsys):
    markdown = "# DISCHARGE SUMMARY\n\nPatient: Maria Rivera\n"
    calls = {}

    class FakeClient:
        def __init__(self, endpoint, credential):
            calls["endpoint"] = endpoint

        def begin_analyze_binary(self, analyzer_id, binary_input):
            calls["analyzer_id"] = analyzer_id
            calls["binary_input"] = binary_input
            content = types.SimpleNamespace(markdown=markdown)
            result = types.SimpleNamespace(contents=[content])
            return types.SimpleNamespace(result=lambda: result)

    stub_module(
        monkeypatch,
        "azure.ai.contentunderstanding",
        ContentUnderstandingClient=FakeClient,
    )
    written = {}
    monkeypatch.setattr(
        Path,
        "write_text",
        lambda self, data, encoding=None: written.update({self.name: data}),
    )

    runpy.run_path(str(SRC / "lab05_extract.py"), run_name="__main__")

    assert written == {"discharge_note.md": markdown}
    assert calls["analyzer_id"] == "prebuilt-layout"
    assert calls["binary_input"].startswith(b"%PDF")
    assert "Saved extracted markdown" in capsys.readouterr().out


def test_structured_prompt_asks_for_the_defined_fields(monkeypatch, azure_env):
    namespace = run_structured(monkeypatch, json.dumps(RECORD))["namespace"]
    asked = re.findall(r"^- (\w+)", namespace["PROMPT"], flags=re.MULTILINE)
    assert asked == EXPECTED_FIELDS


def test_structured_json_has_the_defined_fields(monkeypatch, azure_env, capsys):
    run_structured(monkeypatch, json.dumps(RECORD))
    printed = json.loads(capsys.readouterr().out)
    assert list(printed) == EXPECTED_FIELDS
    assert printed["patient_name"] == "Maria Rivera"


def test_structured_sends_note_markdown_to_configured_model(monkeypatch, azure_env):
    sent = run_structured(monkeypatch, json.dumps(RECORD))["sent"]
    assert sent["model"] == "demo-model"
    assert sent["input"].endswith(NOTE_MD.read_text(encoding="utf-8"))


def test_structured_rejects_non_json_reply(monkeypatch, azure_env):
    with pytest.raises(json.JSONDecodeError):
        run_structured(monkeypatch, "Sure! Here is the JSON:")


def run_structured(monkeypatch, reply):
    sent = {}

    class FakeResponses:
        def create(self, model, input):
            sent.update(model=model, input=input)
            return types.SimpleNamespace(output_text=reply)

    class FakeProject:
        def __init__(self, endpoint, credential):
            pass

        def get_openai_client(self):
            return types.SimpleNamespace(responses=FakeResponses())

    stub_module(monkeypatch, "azure.ai.projects", AIProjectClient=FakeProject)
    namespace = runpy.run_path(str(SRC / "lab05_structured.py"), run_name="__main__")
    return {"namespace": namespace, "sent": sent}
