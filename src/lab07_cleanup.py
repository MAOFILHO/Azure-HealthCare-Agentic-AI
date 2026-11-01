"""Lab 7 - Delete the cloud objects the labs created."""
import os

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Names the labs create (Lab 2 and 4 agent, Lab 4 vector store).
# Anything else in the project is not ours and is left alone.
LAB_AGENT_NAMES = {"carecompanion-agent"}
LAB_VECTOR_STORE_NAMES = {"northfield-policies"}


def cleanup(project, openai_client):
    # Vector stores from Lab 4 (every full re-run created a new one)
    for store in openai_client.vector_stores.list():
        if store.name in LAB_VECTOR_STORE_NAMES:
            print(f"Deleting vector store: {store.name} ({store.id})")
            openai_client.vector_stores.delete(vector_store_id=store.id)

    for agent in project.agents.list():
        if agent.name in LAB_AGENT_NAMES:
            print(f"Deleting agent: {agent.name}")
            project.agents.delete(agent.name)


def main():
    load_dotenv()
    project = AIProjectClient(
        endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )
    cleanup(project, project.get_openai_client())
    print("Lab agents and vector stores cleared. To remove everything else, run:")
    print("  az group delete --name K21-project-rg --yes")


if __name__ == "__main__":
    main()
