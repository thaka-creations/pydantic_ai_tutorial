"""If a tool has a single parameter that can be represented as an object in JSON schema (e.g dataclass, TypedDict, pydantic model),
the schema for the tool is simplified to be just that object
"""

import nest_asyncio
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

nest_asyncio.apply()

agent = Agent()


class Foobar(BaseModel):
    x: int
    y: str
    z: float = 3.14


@agent.tool_plain
def foobar_v2(f: Foobar) -> str:
    return str(f)


test_model = TestModel()
result = agent.run_sync("hello", model=test_model)
print(result.output)
print(test_model.last_model_request_parameters.function_tools)
