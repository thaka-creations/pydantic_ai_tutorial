# Message and chat history
PydanticAI provides access to messaeges exchanged during an agent run. These messages can
be used both to continue a coherent conversation, and to understand how an agent performed.

## Accessing messages from results
After running an agent, you can access the messages exchanged during that run from the result object.
Both RunResult (returned by Agent.run, Agent.run_sync) and StreamedRunResult returned by Agent.run_stream
have the following methods.
- all_messages(): returns all messages, including messages from prior runs. There's also a variant that 
returns JSON bytes, all_messages_json(),
- new_messages(): returns only the messages from the current run. There's also a variant that returns 
JSON bytes, new_messages_json().

See example `messages_and_chat_history/run_result_messages.py`

## Usimg Messages as Input for Further Agent Runs
The primary use of message histories in PydanticAI is to maintain context across multiple agent runs.
To use existing messages in a run, pass them to the **message_history** parameter of **Agent.run**,
**Agent.run_sync** or **Agent.run_stream**
If message_history is set and not empty, a new system prompt is not generated - we assume the existing
message history includes a system prompt.

```python
from pydantic_ai import Agent

agent = Agent("openai:gpt-4o", system_prompt="Be a helpful assistant")
result1 = agent.run_sync("Tell me a joke")
print(result1.output)

result2 = agent.run_sync("Explain?", message_history=result1.new_messages())
print(result2.output)

print(result2.all_messages())
```

## Storing and loading messages (to JSON)
While maintaining conversation state in memory is enough for many applications, often
times you may want to store the mesaages history of an agent run on disk or in a database. This might be
for evals, for sharing data betweek python and JS/TS or any number of other use cases.
The intended way to do this is using a TypeAdapter.
We export **ModelMessagesTypeAdapter** that can be used for this, or you can create your own.

```python
from pydantic_core import to_jsonable_python

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessagesTypeAdapter  

agent = Agent('openai:gpt-4o', system_prompt='Be a helpful assistant.')

result1 = agent.run_sync('Tell me a joke.')
history_step_1 = result1.all_messages()
as_python_objects = to_jsonable_python(history_step_1)  
same_history_as_step_1 = ModelMessagesTypeAdapter.validate_python(as_python_objects)

result2 = agent.run_sync(  
    'Tell me a different joke.', message_history=same_history_as_step_1
)
```
