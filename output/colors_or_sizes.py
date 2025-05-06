# Example of a union return type which registers multiple tools,
# and wraps non object schemas in an object

from typing import Union
from pydantic_ai import Agent

agent: Agent[None, Union[list[str], list[int]]] = Agent(
    "google-gla:gemini-1.5-flash",
    output_type=Union[list[str], list[int]],
    system_prompt=("Extract either colors or sizes from the shapes provided"),
)

result = agent.run_sync("red square, blue circle, green triangle")
print(result.output)

result = agent.run_sync("square size 10, circle size 20, triangle size 30")
print(result.output)
