import nest_asyncio
from typing import Union
from pydantic import BaseModel
from pydantic_ai import Agent

nest_asyncio.apply()


class Box(BaseModel):
    width: int
    height: int
    depth: int
    unit: str


agent: Agent[None, Union[Box, str]] = Agent(
    "google-gla:gemini-1.5-flash",
    output_type=Union[Box, str],
    system_prompt=(
        "Extract me the dimensions of a box,"
        "if you can't extract all data, ask the user to try again."
    ),
)

result = agent.run_sync("The box is 10*20*30")
print(result.output)

result = agent.run_sync("The box is 10*20")
print(result.output)

result = agent.run_sync("The box is 10*20*30 cm")
print(result.output)
