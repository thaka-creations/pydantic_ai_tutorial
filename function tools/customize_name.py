from __future__ import annotations

from typing import Literal

import nest_asyncio
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.test import TestModel
from pydantic_ai.tools import Tool, ToolDefinition

nest_asyncio.apply()


def greet(name: str) -> str:
    return f"Hello {name}"


async def prepare_greet(
    context: RunContext[Literal["human", "machine"]],
    tool_def: ToolDefinition,
) -> ToolDefinition | None:
    d = f"Name of the {context.deps} to greet"
    tool_def.parameters_json_schema["properties"]["name"]["description"] = d
    return tool_def


greet_tool = Tool(greet, prepare=prepare_greet)
test_model = TestModel()
agent = Agent(test_model, tools=[greet_tool], deps_type=Literal["human", "machine"])

result = agent.run_sync("testing...", deps="machine")
print(result.output)
print(test_model.last_model_request_parameters.function_tools)
