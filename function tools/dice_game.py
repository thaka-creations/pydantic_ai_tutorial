import nest_asyncio
import random
from pydantic_ai import Agent, RunContext

nest_asyncio.apply()

agent = Agent(
    "google-gla:gemini-1.5-flash",
    deps_type=str,
    system_prompt=(
        "You're a dice game, you should roll the die and see if the number "
        "you get back matches the user's guess. If so, tell them they're a winner."
        "Use the player's name in the response."
    ),
)


@agent.tool_plain
def roll_die() -> str:
    """Roll a six-sided die and return the result"""
    return str(random.randint(1, 6))


@agent.tool
def get_player_name(ctx: RunContext[str]) -> str:
    """Get the player's name"""
    return ctx.deps


dice_result = agent.run_sync("My guess is 4", deps="Abdul")
print(dice_result.output)

# you can print messages from that game to see what happened
print(dice_result.all_messages())
