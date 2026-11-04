import asyncio, os, sys
sys.path.insert(0, "src")
from agent_framework import (Agent, BaseChatClient, ChatMiddlewareLayer, FunctionInvocationLayer,
    ChatResponse, Message, Content)
from agent_framework.observability import ChatTelemetryLayer
import lab03_tools
from hospital_tools import find_patient

class Fake(FunctionInvocationLayer, ChatMiddlewareLayer, ChatTelemetryLayer, BaseChatClient):
    n = 0
    def _inner_get_response(self, *, messages, stream, options, **kw):
        async def go():
            Fake.n += 1
            if Fake.n == 1:
                return ChatResponse(messages=[Message(role="assistant", contents=[
                    Content.from_function_call(call_id="c1", name="find_patient", arguments='{"name":"Demo"}')])])
            return ChatResponse(messages=[Message(role="assistant", contents=["done"])])
        return go()

async def main():
    lab03_tools.setup_tracing()
    agent = Agent(client=Fake(), name="t", instructions="x", tools=[find_patient])
    r = await agent.run("find Demo")
    print("RESULT", r.text)
asyncio.run(main())
