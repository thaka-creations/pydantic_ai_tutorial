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
