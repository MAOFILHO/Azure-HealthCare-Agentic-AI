"""Lab 2 - Multi-turn conversation with the CareCompanion agent."""
import os

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


def chat(openai_client, read_input=input, write=print):
    # A conversation = server-side message history for THIS exchange
    conversation = openai_client.conversations.create()
    write("CareCompanion is on the line. Type 'quit' to hang up.")

    while True:
        user_text = read_input("\nYou: ").strip()
        if user_text.lower() in ("quit", "exit"):
            break
        response = openai_client.responses.create(
            conversation=conversation.id,
            input=user_text,
        )
        write(f"\nCareCompanion: {response.output_text}")


def main():
    load_dotenv()
    project = AIProjectClient(
        endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )
    # The OpenAI client is pre-bound to the agent: every response uses its
    # instructions and model automatically.
    chat(project.get_openai_client(agent_name="carecompanion-agent"))


if __name__ == "__main__":
    main()
