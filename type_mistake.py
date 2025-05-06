# Type safe by design
from dataclasses import dataclass

import nest_asyncio
from pydantic_ai import Agent, RunContext

nest_asyncio.apply()


@dataclass
class User:
    name: str


agent = Agent(
    "test",
    deps_type=User,
    output_type=bool,
)


@agent.system_prompt
def add_user_name(ctx: RunContext[str]) -> str:
    return f"The user's name is {ctx.deps}."


def foobar(x: bytes) -> None:
    pass


result = agent.run_sync("Does their name start with 'A'?", deps=User("Anne"))
foobar(result.output)
print(result.output)
