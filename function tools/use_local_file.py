from pathlib import Path
from typing import List, Optional

import nest_asyncio
from pydantic import BaseModel, Field
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.openai import OpenAIResponsesModel


nest_asyncio.apply()


class QuestionPart(BaseModel):
    """Represents a sub-part of a question (e.g., (a), (b))"""

    part_label: Optional[str] = Field(description="E.g., '(a)', '(b)'", default=None)
    content: str = Field(description="The question text, including any math equations")
    marks: Optional[int] = Field(
        description="Marks allocated (if specified)", default=None
    )


class ExamQuestion(BaseModel):
    """Represents a full question (e.g., Q1, Q2) with its parts."""

    question_number: str = Field(description="E.g., '1', '17'")
    parts: List[QuestionPart] = Field(description="List of sub-questions")


class Questions(BaseModel):
    """Top-level model for any exam paper (CRE or Math)."""

    questions: List[ExamQuestion] = Field(description="All questions")


agent = Agent(model=OpenAIResponsesModel("gpt-4.1-nano"))

pdf_path = Path("cre.pdf")

result = agent.run_sync(
    [
        "Extract questions from this document?",
        BinaryContent(data=pdf_path.read_bytes(), media_type="application/pdf"),
    ],
    output_type=Questions,
)

print(result.output)
