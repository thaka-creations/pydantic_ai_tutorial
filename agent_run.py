import asyncio
import nest_asyncio
from pydantic_ai import Agent, RunContext

nest_asyncio.apply()  # for notebook

agent = Agent("google-gla:gemini-1.5-flash")
result_sync = agent.run_sync("What is the capital of Kenya?")
print(result_sync.output)


async def main():
    result = await agent.run("What is the capital of Tanzania?")
    print(result.output)

    async with agent.run_stream("What is the capital of Uganda?") as response:
        print(await response.get_output())


asyncio.run(main())
