"""Lab 7 - An agent that uses the Microsoft Learn MCP server."""
import asyncio
import os

from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.foundry import FoundryChatClient

load_dotenv()


async def main() -> None:
    # The MCP tool manages a live connection, so it is used as an
    # async context manager: connect, discover tools, disconnect.
    async with MCPStreamableHTTPTool(
        name="microsoft-learn",
        url="https://learn.microsoft.com/api/mcp",
    ) as learn_docs:
        agent = Agent(
            client=FoundryChatClient(
                project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
                model=os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"],
                credential=AzureCliCredential(),
            ),
            name="ITHelpdeskAgent",
            instructions=(
                "You help Northfield General's IT team with Azure and "
                "Microsoft Foundry questions. Always search the "
                "Microsoft Learn documentation with your tools before "
                "answering, and name the page your answer came from."
            ),
            tools=[learn_docs],
        )
        result = await agent.run(
            "What is a Foundry project endpoint, and where do I find "
            "it in the portal?"
        )
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
