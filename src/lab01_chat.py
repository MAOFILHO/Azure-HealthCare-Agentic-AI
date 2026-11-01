"""Lab 1 - First generative call to the Northfield Foundry project."""
import os

PROMPT = "In two sentences, explain what a hospital care coordinator does."


def ask(openai_client, model, prompt=PROMPT):
    """Ask the model one question (one stateless "response") and print the reply."""
    response = openai_client.responses.create(model=model, input=prompt)
    print(response.output_text)


def main():
    from dotenv import load_dotenv
    from azure.identity import DefaultAzureCredential
    from azure.ai.projects import AIProjectClient

    load_dotenv()  # reads the dotenv file from the folder you run the script in

    # 1. Connect to the Foundry project (auth comes from your `az login`)
    project = AIProjectClient(
        endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    # 2. Get an OpenAI-compatible client that routes through the project
    openai_client = project.get_openai_client()

    # 3. Ask the model a question
    ask(openai_client, os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"])


if __name__ == "__main__":
    main()
