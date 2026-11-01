import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from lab01_chat import ask, main


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


def test_main_reads_the_deployment_name_from_the_environment(monkeypatch, capsys):
    client = fake_client("A coordinator schedules care.")
    project_cls = MagicMock()
    project_cls.return_value.get_openai_client.return_value = client
    for name, attr, value in [
        ("dotenv", "load_dotenv", MagicMock()),
        ("azure.identity", "DefaultAzureCredential", MagicMock()),
        ("azure.ai.projects", "AIProjectClient", project_cls),
    ]:
        monkeypatch.setitem(sys.modules, name, MagicMock(**{attr: value}))
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://demo.invalid")
    monkeypatch.setenv("FOUNDRY_MODEL_DEPLOYMENT_NAME", "env-deployment")

    main()

    assert client.responses.create.call_args.kwargs["model"] == "env-deployment"
    assert capsys.readouterr().out == "A coordinator schedules care.\n"
