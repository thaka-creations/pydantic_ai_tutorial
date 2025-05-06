import nest_asyncio

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.models.test import TestModel
import json

nest_asyncio.apply()

agent = Agent()


@agent.tool_plain(docstring_format="google", require_parameter_descriptions=True)
def foobar(a: int, b: str, c: dict[str, list[float]]) -> str:
    """Get me foobar.

    Args:
        a: apple pie
        b: banana cake
        c: carrot smoothie
    """
    return f"{a} {b} {c}"


def print_schema(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    tool = info.function_tools[0]
    print(tool.description)
    print(json.dumps(tool.parameters_json_schema, indent=2))
    return ModelResponse(parts=[TextPart("foobar")])


agent.run_sync("hello", model=FunctionModel(print_schema))
