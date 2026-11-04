"""Lab 4 - Ground CareCompanion in the hospital's policy documents."""
import os
import time
from pathlib import Path

import openai
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FileSearchTool, PromptAgentDefinition

load_dotenv()
POLICY_DIR = Path(__file__).resolve().parent.parent / "data" / "policies"
POLL_SECONDS = 2
POLL_TIMEOUT_SECONDS = 60
RETRY_TRIES = 6
CALL_TIMEOUT_SECONDS = 60  # SDK default is 600; QA saw calls hang 10 to 66 min
SDK_RETRIES = 3

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
# A stuck call raises openai.APITimeoutError and the SDK resends it.
openai_client = project.get_openai_client(
    timeout=CALL_TIMEOUT_SECONDS, max_retries=SDK_RETRIES
)


def retry_not_found(call, tries=RETRY_TRIES):
    """Run call, retrying openai.NotFoundError and openai.APITimeoutError.
    The service answers 404 on the file and vector store routes for a short
    time, about 1 call in 6, and some calls hang. After the last try the last
    error is raised."""
    for attempt in range(tries):
        try:
            return call()
        except (openai.NotFoundError, openai.APITimeoutError):
            if attempt == tries - 1:
                raise
            time.sleep(POLL_SECONDS)


def wait_until_indexed(client, vector_store_id, file_id):
    """Poll until the file is indexed. Each poll goes through retry_not_found."""
    deadline = time.monotonic() + POLL_TIMEOUT_SECONDS
    while True:
        status = retry_not_found(lambda: client.vector_stores.files.retrieve(
            file_id, vector_store_id=vector_store_id
        ))
        if status.status == "completed":
            return
        if status.status in ("failed", "cancelled"):
            raise RuntimeError(f"File {file_id} {status.status}: {status.last_error}")
        if time.monotonic() >= deadline:
            raise TimeoutError(
                f"File {file_id} not indexed after {POLL_TIMEOUT_SECONDS} seconds"
            )
        time.sleep(POLL_SECONDS)


# 1. Create a vector store and index every policy file into it
vector_store = retry_not_found(
    lambda: openai_client.vector_stores.create(name="northfield-policies")
)
for policy_file in sorted(POLICY_DIR.glob("*.md")):
    # A path, not an open file: the SDK reads it to bytes it can resend on a retry.
    uploaded = retry_not_found(lambda: openai_client.files.create(
        file=policy_file, purpose="assistants",
    ))
    retry_not_found(lambda: openai_client.vector_stores.files.create(
        vector_store_id=vector_store.id, file_id=uploaded.id,
    ))
    wait_until_indexed(openai_client, vector_store.id, uploaded.id)
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
