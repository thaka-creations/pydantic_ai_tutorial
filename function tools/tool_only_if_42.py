import nest_asyncio
from typing import Union
from pydantic_ai import Agent, RunContext
from pydantic_ai.tools import ToolDefinition

nest_asyncio.apply()

agent = Agent("test")


async def only_if_42(
    context: RunContext,
    tool_def: ToolDefinition,
) -> Union[ToolDefinition, None]:
    """Prepare function that only allows the tool to be used when context.deps equals 42.

    Args:
        context: The run context containing dependencies and state
        tool_def: The tool definition to potentially return

    Returns:
        The tool definition if context.deps is 42, None otherwise
    """
    if context.deps == 42:
        return tool_def


@agent.tool(prepare=only_if_42)
def hitchhiker(context: RunContext[int], answer: str) -> str:
    return f"{context.deps} {answer}"


result = agent.run_sync("testing...", deps=41)
print(result.output)

result = agent.run_sync("testing...", deps=42)
print(result.output)
