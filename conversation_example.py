import nest_asyncio
from pydantic_ai import Agent

nest_asyncio.apply()

agent = Agent("google-gla:gemini-1.5-flash")

# First run
result1 = agent.run_sync("Who was Albert Einstein?")
print(result1.output)

# Second run
result2 = agent.run_sync(
    "What was his most famous equation?", message_history=result1.new_messages()
)
print(result2.output)
