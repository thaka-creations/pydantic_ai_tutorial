import asyncio
from datetime import date

import nest_asyncio
from pydantic_ai import Agent
from typing_extensions import TypedDict

nest_asyncio.apply()


class UserProfile(TypedDict, total=False):
    name: str
    dob: date
    bio: str


agent = Agent(
    model="openai:gpt-4o",
    output_type=UserProfile,
    instructions="Extract a user profile from the input",
)


async def main():
    user_input = "My name is Ben, I was born on January 28th 1990, I like the chain the dog and the pyramid."
    async with agent.run_stream(user_input) as result:
        async for profile in result.stream():
            print(profile)


asyncio.run(main())
