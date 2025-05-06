# Import Agent and RunContext from pydantic_ai
# Agent: Main class for creating LLM agents with system prompts, tools and structured outputs
# RunContext: Provides typed access to dependencies and context during agent execution
import nest_asyncio
from pydantic_ai import Agent, RunContext

nest_asyncio.apply()  # for notebook

roulette_agent = Agent(
    model="google-gla:gemini-1.5-flash",
    deps_type=int,
    output_type=bool,
    system_prompt=(
        "Use the 'roulette_wheel' function to see if the customer has won based on the number they provide"
    ),
)


@roulette_agent.tool
async def rolette_wheel(ctx: RunContext[int], square: int) -> str:
    """Check if the square is a winner"""
    return "winner" if square == ctx.deps else "loser"


# Run the agent
success_number = 18
result = roulette_agent.run_sync("Put my money on square eighteen", deps=success_number)
print(result.output)

result = roulette_agent.run_sync("I bet five is the winner", deps=success_number)
print(result.output)
