from typing import List, Optional

from pydantic import BaseModel, Field


class Failed(BaseModel):
    """Unable to find a suitable question in the document."""


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


class RetrievedQuestion(BaseModel):
    """Represents a question retrieved from the database."""

    id: int = Field(description="The id of the question")
    question_number: str = Field(description="E.g., '1', '17'")
    question_part: Optional[str] = Field(description="E.g., '(a)', '(b)'", default=None)
    question: str = Field(description="The question text, including any math equations")
    marks: Optional[int] = Field(
        description="Marks allocated (if specified)", default=None
    )


class RetrievedQuestions(BaseModel):
    """Represents a list of questions retrieved from the database."""

    questions: List[RetrievedQuestion] = Field(
        description="List of retrieved questions"
    )
