import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from lab01_chat import ask


def fake_client(reply="A coordinator schedules care."):
    client = MagicMock()
    client.responses.create.return_value.output_text = reply
    return client


def test_request_uses_the_deployment_name():
    client = fake_client()
    ask(client, "demo-deployment")
    assert client.responses.create.call_args.kwargs["model"] == "demo-deployment"


def test_reply_is_printed(capsys):
    ask(fake_client("A coordinator schedules care."), "demo-deployment")
    assert capsys.readouterr().out == "A coordinator schedules care.\n"
