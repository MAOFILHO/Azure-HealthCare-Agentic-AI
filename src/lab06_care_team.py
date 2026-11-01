"""Lab 6 - A coordinator agent that consults specialist agents."""
import asyncio
import os

from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient

from hospital_tools import book_appointment, find_patient, get_appointments

load_dotenv()


def make_client() -> FoundryChatClient:
    return FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"],
        credential=AzureCliCredential(),
    )


records = Agent(
    client=make_client(),
    name="RecordsSpecialist",
    description="Looks up patient records by name in the registry.",
    instructions=(
        "You look up Northfield General patient records with your tool "
        "and report exactly what you find. Never invent data."
    ),
    tools=[find_patient],
)

scheduler = Agent(
    client=make_client(),
    name="SchedulingSpecialist",
    description="Checks and books appointments for a known patient ID.",
    instructions=(
        "You handle appointment lookups and bookings for Northfield "
        "General using your tools. Require a patient ID; never invent "
        "appointments."
    ),
    tools=[get_appointments, book_appointment],
)

coordinator = Agent(
    client=make_client(),
    name="CareCoordinator",
    instructions=(
        "You are Northfield General's care coordinator. Break each "
        "request into steps, use the records specialist to identify "
        "patients and the scheduling specialist for appointments, then "
        "give the caller one clear, complete answer. Never give medical "
        "advice."
    ),
    tools=[
        records.as_tool(
            name="records_specialist",
            description="Look up a patient's record by name.",
        ),
        scheduler.as_tool(
            name="scheduling_specialist",
            description="Check or book appointments for a patient ID.",
        ),
    ],
)


async def main() -> None:
    task = (
        "Maria Rivera was discharged on July 15 after a cardiac "
        "procedure. Check whether she already has a cardiology "
        "follow-up on the books; her discharge papers say she needs "
        "one within two weeks. If she doesn't, book cardiology for "
        "2026-07-28."
    )
    result = await coordinator.run(task)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
