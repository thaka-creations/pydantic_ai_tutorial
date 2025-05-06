import asyncio
from datetime import date
import nest_asyncio
from pydantic_ai import Agent, RunContext
from dataclasses import dataclass
from pydantic_ai.messages import (
    PartStartEvent,
    PartDeltaEvent,
    ToolCallPartDelta,
    TextPartDelta,
    FinalResultEvent,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
)

nest_asyncio.apply()


@dataclass
class WeatherService:
    async def get_forecast(self, location: str, forecast_date: date) -> str:
        # in real code, call weather API, DB queries etc
        return f"The forecast in {location} on {forecast_date} is sunny with a high of 25C and a low of 15C"

    async def get_historic_weather(self, location: str, forecast_date: date) -> str:
        # In real code: call a historical weather API or DB
        return f"The weather in {location} on {forecast_date} was cloudy with a high of 20C and a low of 10C"


weather_agent = Agent[WeatherService, str](
    model="openai:gpt-4.1-mini",
    deps_type=WeatherService,
    output_type=str,
    system_prompt="Providing a weather forecast at the location the user provides",
)


@weather_agent.tool
async def weather_forecast(
    ctx: RunContext[WeatherService], location: str, forecast_date: date
) -> str:
    if forecast_date >= date.today():
        return await ctx.deps.get_forecast(location, forecast_date)
    else:
        return await ctx.deps.get_historic_weather(location, forecast_date)


output_messages: list[str] = []


async def main():
    user_prompt = "What will the weather be like in Nairobi on Tuesday?"

    async with weather_agent.iter(user_prompt, deps=WeatherService()) as run:
        async for node in run:
            if Agent.is_user_prompt_node(node):
                output_messages.append(f"=== UserPromptNode: {node.user_prompt} ===")
            elif Agent.is_model_request_node(node):
                output_messages.append(
                    "=== ModelRequestNode: streaming partial request tokens ==="
                )
                async with node.stream(run.ctx) as request_stream:
                    async for event in request_stream:
                        if isinstance(event, PartStartEvent):
                            output_messages.append(
                                f"[Request] Starting part {event.index}: {event.part!r}"
                            )
                        elif isinstance(event, PartDeltaEvent):
                            if isinstance(event.delta, TextPartDelta):
                                output_messages.append(
                                    f"[Request] Delta part {event.index} text delta: {event.delta.content_delta!r}"
                                )
                            elif isinstance(event.delta, ToolCallPartDelta):
                                output_messages.append(
                                    f"[Request] Part {event.index} args_delta={event.delta.args_delta}"
                                )
                        elif isinstance(event, FinalResultEvent):
                            output_messages.append(
                                f"[Result] The model produced a final output (tool_name={event.tool_name})"
                            )
            elif Agent.is_call_tools_node(node):
                # A handle-response node => The model returned some data, potentially calls a tool
                output_messages.append(
                    "=== CallToolsNode: streaming partial response & tool usage ==="
                )
                async with node.stream(run.ctx) as handle_stream:
                    async for event in handle_stream:
                        if isinstance(event, FunctionToolCallEvent):
                            output_messages.append(
                                f"[Tools] The LLM calls tool={event.part.tool_name!r} with args={event.part.args} (tool_call_id={event.part.tool_call_id!r})"
                            )
                        elif isinstance(event, FunctionToolResultEvent):
                            output_messages.append(
                                f"[Tools] Tool call {event.tool_call_id!r} returned => {event.result.content}"
                            )
            elif Agent.is_end_node(node):
                assert run.result.output == node.data.output
                # Once an End node is reached, the agent run is complete
                output_messages.append(
                    f"=== Final Agent Output: {run.result.output} ==="
                )


if __name__ == "__main__":
    asyncio.run(main())

    print("\n".join(output_messages))
