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
See example in `function_tools/function_tool_output.py`.

## Function Tools vs Structuted Outputs
As the name suggests, function tools use the model's tools or functions API to let the model
know what is available to call. Tools or functions are also used to define the schema(s) for
structured responses, thus a model might have access to many tools, some of which call function tools
while others end the run and produce a final output.

### Function tools and schema
Function parameters are extracted from the function signature, and all parameters except **RunContext** are used 
to build the schema for that tool call.
Even better, PydanticAI extracts the docstring from functions and (thanks to griffe) extracts parameter descriptions
from the docstring and adds them to the schema.
PydanticAI will infer format to use based on the docstring, but you can explicitly set it using **docstring_format**.
You can also enforce parameter requirements by setting **require_parameter_descriptions=True**.
This will raise a **UserError** if a parameter description is missing.
To demostrate a tool's schema, here we use **FunctionModel** to print the schema a modal would receive:
See example in `function_tools/tool_schema.py` and `function_tools/single_parameter_tool.py`

## Dynamic Function tools
Tools can optionally be defined with another function: **prepare**, which is called at each step of a run
to customize the definition of the tool passed to the model, or omit the tool completely from that step.
A prepare method can be registered via the prepare kwarg to any of the tool registration mechanisms:
- @agent.tool decorator
- @agent.tool_plain decorator
- Tool dataclass

The prepare method, should be of type **ToolPrepareFunc**, a function which takes **RunContext** and a pre-built
**ToolDefinition**, and should either return that **ToolDefinition** with or without modifying it, return a new
**ToolDefinition**, or return None to indicate this tools should not be registered for that step.
