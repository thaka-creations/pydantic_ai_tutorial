from datetime import datetime

import nest_asyncio
from pydantic import BaseModel
from pydantic_ai import Agent, DocumentUrl, ImageUrl
from pydantic_ai.models.openai import OpenAIResponsesModel

nest_asyncio.apply()


class User(BaseModel):
    name: str
    age: int


agent = Agent(model=OpenAIResponsesModel("gpt-4o"))


@agent.tool_plain
def get_current_time() -> str:
    """Get the current time"""
    return datetime.now()


@agent.tool_plain
def get_user() -> User:
    return User(name="John", age=30)


@agent.tool_plain
def get_company_logo() -> ImageUrl:
    return ImageUrl(url="https://iili.io/3Hs4FMg.png")


@agent.tool_plain
def get_document() -> DocumentUrl:
    return DocumentUrl(
        url="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    )


result = agent.run_sync("What time is it?")
print(result.output)

result = agent.run_sync("What is the user's name?")
print(result.output)

result = agent.run_sync("What is the company name in the logo?")
print(result.output)

result = agent.run_sync("What is the main content of the document?")
print(result.output)
