import asyncio

import nest_asyncio
from pydantic_ai import Agent, RunContext
from pydantic_graph import End

nest_asyncio.apply()  # for notebook


agent = Agent("google-gla:gemini-1.5-flash")


async def main():
    nodes = []
    # Begin an AgentRun, which is an async-iterable over the nodes of the agent's graph
    async with agent.iter("What is the capital of Kenya?") as agent_run:
        async for node in agent_run:
            # Each node respresents a step in the agent's execution
            nodes.append(node)

    print(nodes)

    print(agent_run.result.output)


asyncio.run(main())


# using .next() manually
async def move_node_manually():
    async with agent.iter("What is the capital of Kenya?") as agent_run:
        node = agent_run.next_node
        all_nodes = []

        # drive the iteration manually
        while not isinstance(node, End):
            node = await agent_run.next(node)
            all_nodes.append(node)
        print(all_nodes)


asyncio.run(move_node_manually())
