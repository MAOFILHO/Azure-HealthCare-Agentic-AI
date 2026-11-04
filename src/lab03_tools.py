"""Lab 3 - A tool-using scheduling assistant (Microsoft Agent Framework)."""
import asyncio
import os

from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient

from hospital_tools import book_appointment, find_patient, get_appointments

load_dotenv()  # the Agent Framework does not load .env on its own


def setup_tracing() -> None:
    """Print spans for model and tool calls to the console when asked to."""
    if os.environ.get("ENABLE_CONSOLE_EXPORTERS", "").lower() == "true":
        from agent_framework.observability import configure_otel_providers

        configure_otel_providers()


async def main() -> None:
    setup_tracing()
    agent = Agent(
        client=FoundryChatClient(
            project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
            model=os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"],
            credential=AzureCliCredential(),
        ),
        name="SchedulingAssistant",
        instructions=(
            "You are the scheduling assistant for Northfield General "
            "Hospital. Always use your tools to look up patients and "
            "appointments before answering; never invent records. "
            "Confirm the patient's identity (name -> patient ID) before "
            "booking anything. Never give medical advice. "
            "Today's date is 2026-07-20 (demo date)."
        ),
        tools=[find_patient, get_appointments, book_appointment],
    )

    session = agent.create_session()  # keeps multi-turn context
    print("Scheduling assistant ready. Type 'quit' to exit.")
    while True:
        user_text = input("\nYou: ").strip()
        if user_text.lower() in ("quit", "exit"):
            break
        result = await agent.run(user_text, session=session)
        print(f"\nAssistant: {result}")


if __name__ == "__main__":
    asyncio.run(main())
