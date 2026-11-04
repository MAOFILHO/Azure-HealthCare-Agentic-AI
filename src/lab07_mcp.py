"""Lab 7 - An agent that uses the Microsoft Learn MCP server."""
import asyncio
import os
import warnings

from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.foundry import FoundryChatClient

MCP_URL = "https://learn.microsoft.com/api/mcp"

# agent_framework's MCP tool calls the SDK's ping on connect. The mcp 2.x
# SDK warns that ping is removed as of 2026-07-28; the call still works and
# this lab does not make it, so hide only that one message.
warnings.filterwarnings("ignore", message="ping is removed as of")


def learn_tool():
    return MCPStreamableHTTPTool(name="microsoft-learn", url=MCP_URL)


def create_agent(client, learn_docs):
    return Agent(
        client=client,
        name="ITHelpdeskAgent",
        instructions=(
            "You help Northfield General's IT team with Azure and "
            "Microsoft Foundry questions. Always search the "
            "Microsoft Learn documentation with your tools before "
            "answering, and name the page your answer came from."
        ),
        tools=[learn_docs],
    )


async def main() -> None:
    load_dotenv()
    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"],
        credential=AzureCliCredential(),
    )
    # The MCP tool manages a live connection, so it is used as an
    # async context manager: connect, discover tools, disconnect.
    async with learn_tool() as learn_docs:
        agent = create_agent(client, learn_docs)
        result = await agent.run(
            "What is a Foundry project endpoint, and where do I find "
            "it in the portal?"
        )
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
