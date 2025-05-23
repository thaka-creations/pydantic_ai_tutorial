import asyncio
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Union

import logfire
from openai import AsyncOpenAI
from pydantic_ai import Agent, BinaryContent, RunContext
from pymilvus import MilvusClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from . import model, schema

logfire.configure(send_to_logfire="if-token-present")
openai = AsyncOpenAI()
milvus_client = MilvusClient(uri="./milvus_demo.db")
COLLECTION_NAME = "my_rag_collection"  # Constant name in uppercase

# Create SQLAlchemy engine and sessionx
engine = create_engine("postgresql://postgres:@localhost:5432/exam_db")
Session = sessionmaker(bind=engine)


@dataclass
class Deps:
    """Dependencies container for agents."""

    openai: AsyncOpenAI


extract_agent = Agent[BinaryContent, Union[model.Questions, model.Failed]](
    model="openai:gpt-4o",  # Using latest stable model
    deps_type=Deps,
    instrument=True,
    output_type=Union[model.Questions, model.Failed],
    system_prompt=(
        """You are an expert at extracting questions from documents.
        Your task is to read through documents and identify any questions that are asked.
        Extract both explicit questions (ending with ?) and implicit questions that are phrased as statements.

        For each question:
        1. Identify the question number (e.g. "1", "17")
        2. Break down into parts if present (e.g. "(a)", "(b)") and ensure related parts are grouped together
        3. Extract any marks allocated
        4. Preserve any mathematical equations
        5. Group related questions and their parts together (e.g. if question 1.a and 1.b are about the same topic or build on each other)
        6. Pay special attention to questions with marks allocated and maintain their relationships
        7. When parts of a question reference each other or build on previous parts, keep them grouped as a single unit

        Return the questions structured according to the provided model schema."""
    ),
)

retrieval_agent = Agent[str, model.RetrievedQuestions](
    model="openai:gpt-4o",  # Using latest stable model
    deps_type=Deps,
    instrument=True,
    output_type=model.RetrievedQuestions,
    system_prompt=(
        """
        You are an intelligent assistant helping to refine or relay user queries based on retrieved information. You will be given a list of relevant questions retrieved from a vector database.
        Your task is:
        - To decide whether the retrieved questions need to be rephrased, or modified for clarity, context, or improved relevance.
        - Or, if they are already appropriate, to return them as-is without unnecessary changes.
        - Respond with your best judgment—only modify if it adds value. If no modifications are necessary, just return the original questions unchanged.
        - When possible, group related questions together in your response
        - Highlight questions that have marks allocated
        """
    ),
)


@retrieval_agent.tool
async def retrieve(
    context: RunContext[Deps], search_query: str
) -> model.RetrievedQuestions:
    """Retrieve relevant questions based on search query.

    Args:
        context: The run context containing dependencies
        search_query: Query string to search for

    Returns:
        model.RetrievedQuestions: Retrieved questions
    """
    session = Session()
    try:
        res = await search_milvus(
            search_query, context.deps.openai, COLLECTION_NAME, session
        )
        return res
    finally:
        session.close()


def get_pdf_bytes(file_name: str) -> bytes:
    """Read and return binary content of a PDF file.

    Args:
        file_name: Path to the PDF file

    Returns:
        bytes: Binary content of the PDF file

    Raises:
        ValueError: If file cannot be read or is not found
    """
    try:
        return Path(file_name).read_bytes()
    except Exception as e:
        raise ValueError(f"Failed to read PDF file {file_name}: {str(e)}")


async def create_embedding(question: str, openai: AsyncOpenAI) -> list[float]:
    """Generate embeddings for a question using OpenAI's API.

    Args:
        question: The question text to embed
        openai: AsyncOpenAI client instance

    Returns:
        list[float]: The embedding vector

    Raises:
        AssertionError: If unexpected number of embeddings returned
    """
    embedding = await openai.embeddings.create(
        input=question,
        model="text-embedding-3-small",
    )
    assert len(embedding.data) == 1, (
        f"Expected 1 embedding, got {len(embedding.data)}, question: {question}"
    )
    return embedding.data[0].embedding


async def load_data_into_milvus(
    questions: list[model.ExamQuestion], openai: AsyncOpenAI, postgres_session
) -> None:
    """Load question embeddings into Milvus vector database.

    Args:
        questions: List of question texts to embed
        openai: AsyncOpenAI client instance
    """
    if milvus_client.has_collection(COLLECTION_NAME):
        milvus_client.drop_collection(COLLECTION_NAME)

    milvus_client.create_collection(
        collection_name=COLLECTION_NAME,
        dimension=1536,  # text-embedding-3-small has 1536 dimensions
        metric_type="IP",  # Inner product distance
        consistency_level="Strong",  # Strong consistency level
    )

    data = []
    for question in tqdm(questions, desc="Creating embeddings"):
        question_parts = question.parts
        for part in question_parts:
            # save to postgres
            db_question = schema.ExamQuestion(
                exam_name="KCSE",
                subject="CRE",
                year="2024",
                question_number=question.question_number,
                part_label=part.part_label,
                content=part.content,
                marks=part.marks,
            )
            postgres_session.add(db_question)
            postgres_session.flush()

            data.append(
                {
                    "id": db_question.id,
                    "vector": await create_embedding(part.content, openai),
                    "question_number": question.question_number,
                    "question_part": part.part_label,
                    "question": part.content,
                    "marks": part.marks,
                }
            )

    postgres_session.commit()
    milvus_client.insert(collection_name=COLLECTION_NAME, data=data)


async def search_milvus(
    question: str,
    openai: AsyncOpenAI,
    collection_name: str,
    postgres_session,
) -> list[model.RetrievedQuestion]:
    """Search for similar questions in Milvus database.

    Args:
        question: Query string to search for
        openai: AsyncOpenAI client instance
        collection_name: Name of Milvus collection to search

    Returns:
        list[model.RetrievedQuestion]: List of retrieved questions
    """
    search_res = milvus_client.search(
        collection_name=collection_name,
        data=[await create_embedding(question, openai)],
        limit=5,
        search_params={"metric_type": "IP", "params": {}},
        output_fields=["question_number", "question_part", "question", "marks"],
    )
    ids = [hit["id"] for hit in search_res[0]]
    db_questions = (
        postgres_session.query(schema.ExamQuestion)
        .filter(schema.ExamQuestion.id.in_(ids))
        .all()
    )
    return [
        model.RetrievedQuestion(
            id=db_question.id,
            question_number=db_question.question_number,
            question_part=db_question.part_label,
            question=db_question.content,
            marks=db_question.marks,
        )
        for db_question in db_questions
    ]


async def extract_questions(path: str) -> None:
    """Extract questions from a PDF document using an LLM agent.

    Args:
        path: Path to the PDF document to analyze
    """
    logfire.instrument_openai(openai)
    logfire.info("Extracting questions from {path}", path=path)

    result = await extract_agent.run(
        [BinaryContent(data=get_pdf_bytes(path), media_type="application/pdf")],
        deps=Deps(openai=openai),
    )

    if isinstance(result.output, model.Questions):
        session = Session()
        try:
            await load_data_into_milvus(result.output.questions, openai, session)
        finally:
            session.close()


async def retrieve_questions(query: str) -> model.RetrievedQuestions:
    """Retrieve and process questions based on query.

    Args:
        query: Search query string

    Returns:
        model.RetrievedQuestions: Retrieved and processed questions
    """
    result = await retrieval_agent.run(query, deps=Deps(openai=openai))
    print(result.output)
    return result.output


async def add_tables_to_exam_db():
    """Add tables to the exam database."""
    Session = sessionmaker(bind=engine)
    session = Session()
    session.execute(
        text(
            """
            CREATE TABLE exam_questions (
                id SERIAL PRIMARY KEY,
                exam_name VARCHAR(255),
                subject VARCHAR(255),
                year VARCHAR(255),
                question_number VARCHAR(255),
                part_label VARCHAR(255),
                content TEXT,
                marks INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )
    session.commit()
    session.close()


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else None
    if action == "extract":
        asyncio.run(extract_questions("cre.pdf"))
    elif action == "retrieve":
        asyncio.run(retrieve_questions("Outline six attributes of God"))
    elif action == "add_tables_to_exam_db":
        asyncio.run(add_tables_to_exam_db())
    else:
        print(
            "Usage: python question_extractor.py extract|retrieve",
            file=sys.stderr,
        )
        sys.exit(1)
