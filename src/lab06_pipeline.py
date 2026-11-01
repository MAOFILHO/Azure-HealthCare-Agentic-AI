"""Lab 6 - Sequential workflow: discharge note -> after-visit summary."""
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework.orchestrations import SequentialBuilder

load_dotenv()
NOTE_MD = Path(__file__).resolve().parent.parent / "data" / "discharge_note.md"


def make_client() -> FoundryChatClient:
    return FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"],
        credential=AzureCliCredential(),
    )


extractor = Agent(
    client=make_client(),
    name="NoteExtractor",
    instructions=(
        "From the discharge note you are given, produce a terse bullet "
        "list of: diagnosis, each medication with dose and schedule, "
        "follow-up appointments, activity limits, and warning signs. "
        "Facts only - no interpretation, no advice."
    ),
)

writer = Agent(
    client=make_client(),
    name="PatientWriter",
    instructions=(
        "Rewrite the extracted facts as a warm after-visit summary a "
        "patient can read at a sixth-grade level. Keep every fact, "
        "change none, add no medical advice. End with: 'Questions? "
        "Call your care team at 555-0100.'"
    ),
)

workflow = SequentialBuilder(participants=[extractor, writer]).build()


async def main() -> None:
    note = NOTE_MD.read_text(encoding="utf-8")
    result = await workflow.run(
        "Create the after-visit summary for this note:\n\n" + note
    )
    for output in result.get_outputs():
        print(output)


if __name__ == "__main__":
    asyncio.run(main())
