"""Lab 4 - Ground CareCompanion in the hospital's policy documents."""
import os
from pathlib import Path

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FileSearchTool, PromptAgentDefinition

load_dotenv()
POLICY_DIR = Path(__file__).resolve().parent.parent / "data" / "policies"

INSTRUCTIONS = """You are CareCompanion, the virtual patient-services
assistant for Northfield General Hospital.

Scope: hospital logistics only - visiting hours, appointments, billing,
directions, parking, and discharge paperwork.

Hard rules, in priority order:
1. EMERGENCIES FIRST. Anything that sounds like an emergency: tell the
   caller to hang up and call 911 immediately.
2. NO MEDICAL ADVICE. Refer clinical questions to the nurse advice
   line: 555-0142.
3. POLICY ANSWERS COME FROM DOCUMENTS. For any question about hospital
   policy (hours, billing, discharge), search your files and answer
   only from what you find, quoting the specific rule. If the documents
   do not cover it, say so and offer Patient Services at 555-0100.

Style: warm, plain language, short answers.
"""

project = AIProjectClient(
    endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
openai_client = project.get_openai_client()

# 1. Create a vector store and index every policy file into it
vector_store = openai_client.vector_stores.create(name="northfield-policies")
for policy_file in sorted(POLICY_DIR.glob("*.md")):
    with policy_file.open("rb") as fh:
        openai_client.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store.id, file=fh,
        )
    print(f"Indexed {policy_file.name}")

# 2. Publish a new agent version with the file search tool attached
agent = project.agents.create_version(
    agent_name="carecompanion-agent",
    definition=PromptAgentDefinition(
        model=os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"],
        instructions=INSTRUCTIONS,
        tools=[FileSearchTool(vector_store_ids=[vector_store.id])],
    ),
)
print(f"{agent.name} is now version {agent.version} (file search attached)")

# 3. Ask a question only the documents can answer
conversation = openai_client.conversations.create()
response = openai_client.responses.create(
    conversation=conversation.id,
    input="Can my brother visit me in the ICU at 9 pm tonight?",
    extra_body={"agent_reference": {"name": "carecompanion-agent", "type": "agent_reference"}},
)
print("\n" + response.output_text)
