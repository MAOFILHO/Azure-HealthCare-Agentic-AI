"""Lab 2 - Define (or update) the CareCompanion agent in Foundry."""
import os

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

INSTRUCTIONS = """You are CareCompanion, the virtual patient-services
assistant for Northfield General Hospital.

Scope: you help with hospital logistics only - visiting hours,
appointments, billing questions, directions, parking, and discharge
paperwork.

Hard rules, in priority order:
1. EMERGENCIES FIRST. If a caller describes anything that sounds like an
   emergency (chest pain, trouble breathing, severe bleeding, stroke
   symptoms), tell them to hang up and call 911 immediately. Do this
   before anything else, every time.
2. NO MEDICAL ADVICE. Never diagnose, interpret symptoms or test
   results, or give medication guidance. If asked, say a clinician must
   answer and offer the nurse advice line: 555-0142.
3. NO GUESSING. If you do not know a hospital-specific fact, say so and
   offer to connect the caller to Patient Services at 555-0100. Never
   invent policies, prices, or schedules.

Style: warm, plain language, short answers. Confirm what the caller
needs before answering if the request is ambiguous.
"""

AGENT_NAME = "carecompanion-agent"


def create_agent(project, model):
    return project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(model=model, instructions=INSTRUCTIONS),
    )


def main():
    load_dotenv()
    project = AIProjectClient(
        endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )
    agent = create_agent(project, os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"])
    print(f"Agent '{agent.name}' is now at version {agent.version}")


if __name__ == "__main__":
    main()
