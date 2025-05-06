# Getting started with PydanticAI
A python agent framework designed to make it less painful to build production grade applications
with generative AI.


## Why use PydanticAI
- **Built by the Pydantic Team**: Team behind validation layer of the OpenAI SDK and many others
- **Model_agnostic**: Supports variety of models
- **Pydantic logfire integration**: Seamlessly integrates with Pydantic Logfire for real-time
debugging, perfomance monitoring and behavior tracking of your LLM-powered applications.
- **Type-safe**: Designed to make type checking as powerful and informative as possible for you.
- **Python-centric Design**: Leverages python's familiar control flow and agent composition to 
build your AI-driven projects, making it easy to apply standard python best practices you'd use in any 
other (non-AI) project.
- **Structured Responses**: Harnesses the power of pydantic to validate and structure model output,
ensuring responses are consistent across runs.
- **Dependency injection system**: Offers an optional dependency injection system to provide data and 
services to your agent's system prompts, tools and output validators. This is useful for testing
and eval-driven iterative development.
- **Streamed responses**: Provides the ability to stream LLM responses continously, with immediate validation,
ensuring real time access to validated outputs.
- **Graph support**: Pydantic graph provides a powerful way to define graphs using typing hints, this is 
useful in complex applications where standard control flow can degrade to spagheti code.


## Agents
### Introduction
Agents are PydanticAI's primary interface for interacting with LLMs.
In some use cases a single agent will control an entire application or component, but multiple agents can also interact
to embody more complex workflows
The agent class has full API documentation, but conceptually you can think of an agent as a container for:

| Component | Description |
|-----------|-------------|
| System Prompt(s) | A set of instructions for the LLM written by the developer|
| Function tool(s) | Functions that the LLM may call to get information while generating a response |
| Structured output type| The structured datatype that the LLM must return at the end of a run, if specified |
| Dependency type contraint | System prompt functions, tools, and output validators may all use dependencies when they're run|
| LLM model | Optional default LLM model associated with the agent. Can also be specified when running the agent |
| Model Settings | Optional default model settings to help fine tune requests. Can also be specified when running the agent |

### Running Agents
There are four ways to run an agent
1. **agent.run()** - a coroutine which returns a RunResult containing a completed response.
2. **agent.run_sync()** - a plain, synchronous function which return a RunResult containing a completed response
3. **agent.run_stream()** - a corouting which returns a StreamedRunResult, which contains methods to stream a response as an
async iterable
4. **agent.iter()** - a context manager which returns an AgentRun, an async-iterable over the nodes of the agent's underlying
Graph


### Iterating over an agent's graph
Under the hood, each agent in pydanticAI uses pydantic-graph to manage its execution flow.
Pydantic-graph is a generic, type-centric library for building and running finite state machines in python.
It doesn't actually depend on PydantiAI - you can use it standalone for workflows that have nothing to do with GenAI
- but pydanticAI makes use of it to orchestrate the handling of model requests and model responses in an agent's run.

In many scenarios, you don't need to worry about pydantic-graph at all; calling agent.run()
simply traverses the underlying graph from start to finish. However, if you need deeper insight or
control - for example to capture each tool invocation, or to inject your own logic at specific stages - 
PydanticAI exposes the lower-level iteration process via Agent.iter. This method returns an AgentRun,
which you can async-iterate over, or manually drive node-by-node via the next method. Once the agent's graph returns an End,
you have the final result along with a detailed history of all steps.


### Accessing usage and the final output
You can retrieve usage statistics (tokens, requests etc) at any time from the AgentRun object via agent_run.usage()
This methods returns a Usage object containing the usage data.
Once the run finishes, agent_run.result becomes a AgentRunResult object containing the final output (and the related metadata)

### Additional Configuration
#### Usage Limits
PydanticAI offers a UsageLimits structure to help you limit your usage on model runs
You can apply these settings by passing the **usage_limits**argument to the run{_sync,_stream}
functions.

```
from pydantic_ai.exceptions import UsageLimitExceeded
from pydantic_ai.usage import UsageLimits

result_sync = agent.run_sync(
    "What is the capital of Kenya? Answer with just the city.",
    usage_limits=UsageLimits(response_tokens_limit=10)
)

result_sync.usage()
"""
Usage(requests=1, request_tokens=62, response_tokens=1, total_tokens=63, details=None)
"""

try:
    result_sync = agent.run_sync(
        "What is the capital of Kenya? Answer with a paragraph.",
        usage_limits=UsageLimits(response_tokens_limit=10)
    )
except UsageLimitExceeded as e:
    print(e)
 ```

 Restricting the number of requests can be useful in preventing infinite loops or excessive tool calling:

 ```
 from typing_extensions import TypedDict
 from pydantic_ai import Agent, ModelRetry
 from pydantic_ai.exceptions import UsageLimitExceeded
 from pydantic_ai.usage import UsageLimits

 class NeverOutputTpe(TypeDict):
    """
    Never ever coerce data to this type
    :::
    never_use_this: str

agent = Agent(
    "anthropic:claude-3-5-sonnet-latest',
    retries=3,
    output_type=NeverOutputType,
    system_prompt="Any time you get a response, call the 'infinite_retry_tool' to produce a response"
)

@agent.tool_plain(retries=5)
def infinite_retry_tool()->int:
    raise ModelRetry("Please try again")

try:
    result_sync = agent.run_sync(
        "Begin infinite retry loop!", usage_limits=UsageLimits(request_limit=3)
    )
except UsageLimitExceeded as e:
    print(e)

```
N/B: Relevant if you've registered many tools. The request_limit can be used to prevent the model from calling them in a loop
too many times

#### Model(Run) Settings
Pydantic offers a settings.ModelSettings structure to help you fine tune your requests.
This structure allows you to configure common parameters that influence the model's behavior, such as temperature, max_tokens,
timeout and more.
There are two ways to apply these settings: 
1.Passing to run{_sync,_stream} functions via the model_settings argument. This allows for fine-tuning on a per-request basis.
2. Setting during Agent initialization via the model_settings argument. These settings will be applied by default to all subsequent
run calls using said agent. However, model_settings provided during a specific run call will override the agent's default settings.

For example, if you'd like to set the temperature setting to 0.0 to ensure less random behavior, you can do the following

```
from pydantic_ai import Agent

agent = Agent("open:gpt-4o")
result_sync = agent.run_sync(
    "what is the capital of Kenya?", model_settings={"temperature": 0.0}
)
print(result_sync.output)
```

####
Model specific settings, like [GeminiModelSettings](model_settings.py), associated with your model of choice
    

### Runs Vs Conversations
An agent run might represent an entire conversation - there's no limit to how many messages can be exchanged in a single run.
However, a conversation might also be comprised of multiple runs, especially if you need to maintain state between separate interactions or API calls.

```
import nest_asyncio
from pydantic_ai import Agent

nest_asyncio.apply()

agent = Agent("google-gla:gemini-1.5-flash")

# First run
result1 = agent.run_sync("Who was Albert Einstein?")
print(result1.output)

# Second run
result2 = agent.run_sync(
    "What was his most famous equation?", message_history=result1.new_messages()
)
print(result2.output)
```

### Type safe by design
PydanticAI is designed to work well with static type checkers, like **mypy** and **pyright**.
In particular, agents are generic in both the type of their dependencies and the type
of the outputs they return, so you can use the type hints to ensure you're using the right
types.

```
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext

@dataclass
class User:
    name: str

agent = Agent(
    'test',
    deps_type=User,
    output_type=bool,
)

@agent.system_prompt
def add_user_name(ctx:RunContext[str])->str:
    return f"The user's name is {ctx.deps}."

def foobar(x:bytes)-> None:
    pass

result = agent.run_sync("Does their name start with 'A'?" , deps=User("Anne"))
foobar(result.output)
```

## System Prompts
System prompts might seem simple at first glance since they're just strings (or sequences of strings that are concatenated),
but crafting the right system prompt is key to getting the model to behave as you want.

### Tip
For most use cases, you should use instructions instead of system prompts
If you know what you are doing though and want to preserve system prompt message history sent to the LLM in subsequent completions requests,
you can achieve this using the system_prompt argument/decorator.

Generally, system prompts fall into two categories:
1. Static system prompts: These are known when writing the code and can be defined via the system_prompy paramater of the Agent constructor.
2. Dynamic system promprs: These depend in some way on context that isn't known until runtime, and should be defined via functions decorated with
@agent.system_prompt.

You can add both to a single agent; they're appended in the order they're defined at runtime.

```
from  datetime import date
from pydantic_ai import Agent, RunContext

agent = Agent(
    "openai:gpt-4o",
    deps_type=str,
    system_prompt="Use the customer's name while replying to them"
)

@agent.system_prompt
def add_the_users_name(ctx: RunContext[str])-> str:
    return f"The user's name is {ctx.deps}"

@agent.system_prompt
def add_the_date()->str:
    return f"The date is {date.today()}"

result = agent.run_sync("What is the date?", deps="Frank")
print(result.output)
```

## Instructions
Are similar to system prompts. The main difference is that when an explicit **message_history** is provided in a call to 
*Agent.run** and similar methods, instructions from any existing messages in the history are not included in the request to the
model - only the instructions of the current agent are included.

You should use:
- **instructions** when you want your request to the model to only include system prompts for the current agent
- **system_prompt** when you want your request to the model to the model to retain the system prompts used in previous requests 
(possibly made using other agents)

In general, we recommend using **instructions** instead of **system_prompt** unless you have a specific reason to use **system_prompt**

```
from pydantic_ai import Agent
agent = Agent(
    "openai:gpt:4o",
    instructions="You are a helpful assistant that can answer questions and help with tasks"
)
result = agent.run_sync("What is the capital of France?")
print(result.output)
```

## Reflection and self-correction
Validation errors from both function tool parameter validation and structured output validation can be passed back to the model with a request to retry.
You can also raise **ModelRetry** from within a tool or output validator function to tell the model it should retry generating a response
The default retry count is 1 but can be altered for the entire agent, a specific tool or an output validator
You can access the current retry count from within a tool or output validator via ctx.retry

```
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext, ModelRetry
from fake_database import DatabaseConn

class ChatResult(BaseModel):
    user_id: int
    message: str

agent = Agent(
    "openai:gpt-4o",
    deps_type=DatabaseConn,
    output_type=ChatResult
)

@agent.tool(retries=2)
def get_user_by_name(ctx: RunContext[DatabaseConn], name: str)->int:
    """Get a user's ID from their full name"""
    print(name)
    user_id = ctx.deps.users.get(name=name)
    if user_id is None:
        raise ModelRetry(f"No user found with name {name!r}, remember to provide their full name")
    return user_id

result = agent.run_sync("Send a message to John Doe asking for coffee next week", deps=DatabaseConn())
print(result.output)

```

## Model Errors
If models behave unexpectedly (eg the retry limit is exceeded, or their API returns 503), agent runs will raise **UnexpectedModelBehavior**
In these cases, capture_run_messages can be used to access the messages exchanged during the run to help diagnose the issue.

```
from pydantic_ai import Agent, ModelRetry, UnexpectedModelBehavior, capture_run_messages

agent = Agent("openai:gpt-4o")

@agent.tool_plain  # A decorator for tools that don't need access to dependencies or retry context
def calc_volume(size: int) -> int:
    if size == 42:
        return size**3
    else:
        raise ModelRetry("Please try again")

with capture_run_messages() as messages:
    try:
        result = agent.run_sync("Please get me the volume of a box with size")
    except UnexpectedModelBehavior as e:
        print("An error occurred", e)
    else:
        print(result.output)

```