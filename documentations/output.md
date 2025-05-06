# Output
Output refers to the final value returned from running an agent these can be either plain text
or structured data.
The output is wrapped in **AgentRunResult** or **StreamedRunResult** so you can access other data
like usage of the run and message history.
Both AgentRunResult and StreamedRunResult are generic in the data they wrap, so typing information about
the data returned by the agent is preserved.

```python
from pydantic import BaseModel
from pydantic_ai import Agent

class CityLocation(BaseModel):
    city: str
    country: str

agent = Agent("google-gla:gemini-1.5-flash", output_type=CityLocation)
result = agent.run_sync("Where were the olympics held in 2012?")
print(result.output)
print(result.usage()
```

## Output data
When the output type is str, or a union including str, plain text responses are enabled on the model,
and the raw text response from the model is used as the response data.
If the output type is a union with multiple members (after removing str from the members),
each member is registered as a separate tool with the model in order to reduce the complexity of the 
tool schemas and maximise the chances a model will respond correctly.
If the output type schema is not of type object, the output type is wrapped in a single element object,
so the schema of all tools registered with the model are object schemas.
Structured outputs (like tools) use pydantic to build the JSON schema used for the tool, and to validate
the data returned by the model.
See example in `output/colors_or_sizes.py`

## Output validator functions
Some validation is inconvenient or impossible to do in pydantic validators, in particular
when the validation requires IO and is asynchronous. PydanticAI provides a way to add validation functions
via the **agent.output_validator** decorator
See example See example in `output/sql_gen.py`

## Streamed Results
There are two main challenges with streamed results:
1. Validating structured responses before they're complete, this is achieved by "partial validation"
which was recently added to Pydantic
2. When receiving a response, we don't know if it's the final response without starting to stream it and 
peeking at the content. PydanticAI streams just enough of the response to sniff out if it's a tool call or an
output, then streams the whole thing and calls tools, or returns the stream as a StreamedRunResult.

### Streaming Text
See example `output/streamed_hello_world.py`

### Streaming Structured Output
Not all types are supported with partial validation in pydantic, generally for model-like structures it's currently
best to use **TypeDict**






