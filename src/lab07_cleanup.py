"""Lab 7 - Delete the cloud objects the labs created."""
import os

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

project = AIProjectClient(
    endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
openai_client = project.get_openai_client()

# Vector stores from Lab 4 (every full re-run created a new one)
for store in openai_client.vector_stores.list():
    print(f"Deleting vector store: {store.name} ({store.id})")
    openai_client.vector_stores.delete(vector_store_id=store.id)

print("Vector stores cleared.")
print("Now delete the agent in the portal (Build > Agents), then run:")
print("  az group delete --name rg-northfield-ai --yes")
