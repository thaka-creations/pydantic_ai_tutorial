import nest_asyncio
from pydantic_ai import Agent, UnexpectedModelBehavior
from pydantic_ai.models.gemini import GeminiModelSettings

nest_asyncio.apply()

agent = Agent("openai:gpt-4.1-mini")
result_sync = agent.run_sync(
    "what is the capital of Kenya?", model_settings={"temperature": 0.0}
)
print(result_sync.output)


# model specific settings
agent = Agent(
    "google-gla:gemini-1.5-flash",
    output_type=str,
    system_prompt="You are a helpful assistant that can answer questions about the world.",
)
try:
    result = agent.run_sync(
        "Write a list of 5 very rude things that I might say to the universe after stubbing my toe in the dark:",
        model_settings=GeminiModelSettings(
            temperature=0.0,
            gemini_safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_LOW_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_LOW_AND_ABOVE",
                },
            ],
        ),
    )
except UnexpectedModelBehavior as e:
    print(e)

print(result.output)
