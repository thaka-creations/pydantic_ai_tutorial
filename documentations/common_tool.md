# Common Tools
PydanticAi ships with native tools that can be used to enhance your agent's capabilities.

## DuckDuckGo Search Tool
Allows you to search the web for information. It is built on top of the **DuckDuckGo API**

### Installation
To use **duckduckgo_search_tool**, you need to install **pydantic-ai-slim** with the duckduckgo 
optional grop:

```python
pip install pydantic-ai-slim[duckduckgo]
```

### Usage
```python
from pydantic_ai import Agent
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool

agent = Agent(
    'openai:o3-mini',
    tools=[duckduckgo_search_tool()],
    system_prompt='Search DuckDuckGo for the given query and return the results.',
)

result = agent.run_sync(
    'Can you list the top five highest-grossing animated films of 2025?'
)
print(result.output)
```

## Tavity Search Tool
The Tavity search tool allows you to search the web for information, It is built on top
of the Tavity API.

### Installation
To use **tavity_search_tool**, you need to install **pydantic-ai-slim** with the tavity optional
group:

```python
pip install pydantic-ai-slim[tavity]
```

### Usage
```python
import os

from pydantic_ai.agent import Agent
from pydantic_ai.common_tools.tavily import tavily_search_tool

api_key = os.getenv('TAVILY_API_KEY')
assert api_key is not None

agent = Agent(
    'openai:o3-mini',
    tools=[tavily_search_tool(api_key)],
    system_prompt='Search Tavily for the given query and return the results.',
)

result = agent.run_sync('Tell me the top news in the GenAI world, give me links.')
print(result.output)
```
