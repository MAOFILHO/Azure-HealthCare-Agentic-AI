import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from lab02_chat import chat
from lab02_create_agent import create_agent


def test_create_agent_uses_name_model_and_safety_instructions():
    project = MagicMock()

    create_agent(project, "demo-model")

    kwargs = project.agents.create_version.call_args.kwargs
    assert kwargs["agent_name"] == "carecompanion-agent"
    assert kwargs["definition"].model == "demo-model"
    instructions = kwargs["definition"].instructions
    assert "911" in instructions
    assert "NO MEDICAL ADVICE" in instructions
    assert "NO GUESSING" in instructions


class FakeOpenAI:
    """Keeps history per conversation id, like the server-side conversation."""

    def __init__(self):
        self.histories = {}
        self.extra_bodies = []
        self.conversations = SimpleNamespace(create=self._create)
        self.responses = SimpleNamespace(create=self._respond)

    def _create(self):
        self.histories["conv-1"] = []
        return SimpleNamespace(id="conv-1")

    def _respond(self, conversation, input, extra_body=None):
        self.extra_bodies.append(extra_body)
        history = self.histories[conversation]
        seen = list(history)
        history.append(input)
        return SimpleNamespace(output_text=f"seen={seen}")


def run_chat(client, lines):
    feed = iter(lines)
    out = []
    chat(client, read_input=lambda _prompt: next(feed), write=out.append)
    return "\n".join(out)


def test_second_turn_keeps_first_turn_context():
    client = FakeOpenAI()

    output = run_chat(client, ["my name is Maria", "what is my name?", "quit"])

    assert "seen=['my name is Maria']" in output
    assert client.histories["conv-1"] == ["my name is Maria", "what is my name?"]


def test_quit_ends_chat_without_calling_the_agent():
    client = FakeOpenAI()

    run_chat(client, ["QUIT"])

    assert client.histories["conv-1"] == []


def test_every_response_targets_the_agent_via_agent_reference():
    client = FakeOpenAI()

    run_chat(client, ["hello", "again", "quit"])

    expected = {"agent_reference": {"name": "carecompanion-agent", "type": "agent_reference"}}
    assert client.extra_bodies == [expected, expected]
