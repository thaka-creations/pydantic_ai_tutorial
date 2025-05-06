import random

import nest_asyncio
from pydantic_ai import Agent, RunContext

nest_asyncio.apply()

system_prompt = """
You're a dice game, you should roll the die and see if the number
you get back matches the user's guess. If so, tell them they're a winner.
Use the player's name in the response.
"""


def roll_die() -> str:
    """Roll a six-sided die and return the result"""
    return str(random.randint(1, 6))


def get_player_name(ctx: RunContext[str]) -> str:
    """Get the player's name"""
    return ctx.deps


agent = Agent(
    "google-gla:gemini-1.5-flash",
    deps_type=str,
    system_prompt=system_prompt,
    tools=[roll_die, get_player_name],
)

dice_result = {}
dice_result["a"] = agent.run_sync("My guess is 4", deps="Yashar")
dice_result["b"] = agent.run_sync("My guess is 6", deps="Anne")
print(dice_result["a"].output)
print(dice_result["b"].output)
