import asyncio

import nest_asyncio
from pydantic_ai import Agent

nest_asyncio.apply()

agent = Agent("google-gla:gemini-1.5-flash")


async def main():
    async with agent.run_stream("Where does 'hello world' come from?") as result:
        async for message in result.stream_text(delta=True):
            print(message)


asyncio.run(main())
