"""Lab 7 - Delete the cloud objects the labs created."""
import os
import time

import openai
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Names the labs create (Lab 2 and 4 agent, Lab 4 vector store).
# Anything else in the project is not ours and is left alone.
LAB_AGENT_NAMES = {"carecompanion-agent"}
LAB_VECTOR_STORE_NAMES = {"northfield-policies"}

DELETE_TRIES = 5
DELETE_WAIT_SECONDS = 3


def delete_vector_store(openai_client, store_id):
    # The service sometimes answers 404 for a store it just created, so a
    # NotFoundError is retried. After the last try, warn and go on.
    for attempt in range(1, DELETE_TRIES + 1):
        try:
            openai_client.vector_stores.delete(vector_store_id=store_id)
            return
        except openai.NotFoundError:
            if attempt == DELETE_TRIES:
                print(f"Warning: could not delete vector store {store_id} (404 after {DELETE_TRIES} tries)")
            else:
                time.sleep(DELETE_WAIT_SECONDS)


def cleanup(project, openai_client):
    # Read both lists to the end first: deleting while paging breaks the
    # "after" cursor (it points at the item just deleted).
    stores = list(openai_client.vector_stores.list())
    agents = list(project.agents.list())

    # Vector stores from Lab 4 (every full re-run created a new one)
    for store in stores:
        if store.name in LAB_VECTOR_STORE_NAMES:
            print(f"Deleting vector store: {store.name} ({store.id})")
            delete_vector_store(openai_client, store.id)

    for agent in agents:
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
