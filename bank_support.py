# Building support agent for a bank
# import logfire
import nest_asyncio
from dataclasses import dataclass
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

nest_asyncio.apply()

# logfire.configure()
# logfire.instrument_asyncpg()


class DatabaseConn:
    """This is a fake database for example purposes
    In reality, you'd be connecting to an external database to get information about customers
    """

    @classmethod
    async def customer_name(cls, *, id: int) -> str | None:
        if id == 123:
            return "Abdul"

    @classmethod
    async def customer_balance(cls, *, id: int, include_pending: bool) -> float:
        if id == 123:
            return 123.45
        else:
            raise ValueError("Customer not found")


# The @dataclass decorator automatically generates special methods like __init__() and __repr__()
# for the class, making it easier to define classes that primarily store data
@dataclass
class SupportDependencies:
    """Dependencies required for the bank support agent.

    Attributes:
        customer_id: Unique identifier for the customer being served
        db: Database connection instance to fetch customer information
    """

    customer_id: int
    db: DatabaseConn


class SupportOutput(BaseModel):
    support_advice: str = Field(description="Advice returned to the customer")
    block_card: bool = Field(description="Whether to block the customer's card")
    risk: int = Field(description="Risk level of query", ge=0, le=10)


support_agent = Agent(
    "google-gla:gemini-1.5-flash",
    deps_type=SupportDependencies,
    output_type=SupportOutput,
    system_prompt=(
        "You are a support agent in our bank, give the customer support and judge the risk level of their query"
    ),
    # instrument=True,
)


@support_agent.system_prompt
async def add_customer_name(ctx: RunContext[SupportDependencies]) -> str:
    """Adds the customer's name to the system prompt.

    Args:
        ctx: Run context containing dependencies like customer ID and database connection.
            The ctx (context) parameter provides access to dependencies needed by this function,
            including the database connection and customer ID. Using a context object allows for:
            - Dependency injection for easier testing
            - Consistent access to shared resources
            - Type safety through the RunContext generic type
            - Clean separation of concerns

    Returns:
        str: A string containing the customer's name to be added to the system prompt.
        Returns "The customer's name is {name}" if found, or None if not found.

    This function fetches the customer's name from the database using the customer ID
    and formats it into a string that can be added to the agent's system prompt.
    """
    customer_name = await ctx.deps.db.customer_name(id=ctx.deps.customer_id)
    return f"The customer's name is {customer_name}"


@support_agent.tool
async def customer_balance(
    ctx: RunContext[SupportDependencies], include_pending: bool
) -> float:
    """Returns the customer's current account balance"""
    balance = await ctx.deps.db.customer_balance(
        id=ctx.deps.customer_id,
        include_pending=include_pending,
    )
    return f"Kshs {balance:.2f}"


if __name__ == "__main__":
    deps = SupportDependencies(customer_id=123, db=DatabaseConn())
    result = support_agent.run_sync("What is my balance?", deps=deps)
    print(result.output)

    result = support_agent.run_sync("I just lost my card", deps=deps)
    print(result.output)

    result = support_agent.run_sync("I want to block my card", deps=deps)
    print(result.output)
