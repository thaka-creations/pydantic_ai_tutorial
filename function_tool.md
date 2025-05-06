# Function Tools
Function tools provide a mechanism for models to retrieve extra information to help them generate a response
They're useful when it is impractical or impossible to pull all the context an agen might need into the system prompt,
or when you want agents' behavior more deterministic or reliable by deferring some of the logic required to generate a 
response to another (not necessary AI-powered) tool

## Function tools vs RAG
Function tools are basically the "R" of RAG (retrieval-augmented generation) - they augment what the model can
do by letting it request extra information.
The main semantic difference between PydanticAI tools and RAG is synonymous with vector-search, while pydantic tools
are more general purpose. 

There are a number of ways to register tools with an agent:
- via the @agent.tool decorator - for tools that need access to the agent context
- via the @agent.tool_plain decorator - for tools that do not need access to the agent context
- via the tools keyword argument to Agent which can take either plain functions, or instances of Tool

## Registering function tools via Decorator
@agent.tool is considered the default decorator since in the majority of cases tools will need access to the 
agent context. See the example in `function_tools/dice_game.py`.

## Registering function tools via agent argument
As well as using the decorators, we can register tools via the tools argument to the Agent constructor.
This is useful when you want to reuse tools, and can also give more fine-grained control over the tools.
See example in `function_tools/dice_game_tool_kwarg.py`

## Function Tool Output
Tools can return anything that pydantic can serialize to JSON, as well as audio, video, image or
document content depending on the types of multi-modal input the model supports:

