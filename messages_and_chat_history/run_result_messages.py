import nest_asyncio
import json
from pydantic_ai import Agent

nest_asyncio.apply()


agent = Agent(
    model="google-gla:gemini-1.5-flash",
    system_prompt="Be a helpful assistant",
)

result = agent.run_sync("Tell me a joke")

print(result.all_messages())

print(result.all_messages_json())
