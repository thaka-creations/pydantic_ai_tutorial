import asyncio
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Union

import logfire
from openai import AsyncOpenAI
from pydantic_ai import Agent, BinaryContent, RunContext
from pymilvus import MilvusClient
from tqdm import tqdm

from . import model

logfire.configure(send_to_logfire="if-token-present")
openai = AsyncOpenAI()
milvus_client = MilvusClient(uri="./milvus_demo.db")
collection_name = "my_rag_collection"


@dataclass
class Deps:
    openai: AsyncOpenAI


extract_agent = Agent[BinaryContent, Union[model.Questions, model.Failed]](
    model="openai:gpt-4o",  # Fixed model name
    deps_type=Deps,
    instrument=True,
    output_type=Union[model.Questions, model.Failed],
    system_prompt=(
        """You are an expert at extracting questions from documents.
        Your task is to read through documents and identify any questions that are asked.
        Extract both explicit questions (ending with ?) and implicit questions that are phrased as statements.

        For each question:
        1. Identify the question number (e.g. "1", "17")
        2. Break down into parts if present (e.g. "(a)", "(b)")
        3. Extract any marks allocated
        4. Preserve any mathematical equations

        Return the questions structured according to the provided model schema."""
    ),
)

retrieval_agent = Agent[str, str](
    model="openai:gpt-4o",
    deps_type=Deps,
    instrument=True,
    output_type=str,
    system_prompt=(
        """
        You are an intelligent assistant helping to refine or relay user queries based on retrieved information. You will be given a list of relevant questions retrieved from a vector database.
        Your task is:
        - To decide whether the retrieved questions need to be rephrased, or modified for clarity, context, or improved relevance.
        - Or, if they are already appropriate, to return them as-is without unnecessary changes.
        - Respond with your best judgment—only modify if it adds value. If no modifications are necessary, just return the original questions unchanged.
        """
    ),
)


@retrieval_agent.tool
async def retrieve(context: RunContext[Deps], search_query: str) -> str:
    res = await search_milvus(search_query, context.deps.openai, collection_name)
    return res


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


async def load_data_into_milvus(questions: list[str], openai: AsyncOpenAI) -> None:
    """Load question embeddings into Milvus vector database.

    Args:
        questions: List of question texts to embed
        openai: AsyncOpenAI client instance
    """
    collection_name = "my_rag_collection"

    if milvus_client.has_collection(collection_name):
        milvus_client.drop_collection(collection_name)

    milvus_client.create_collection(
        collection_name=collection_name,
        dimension=1536,  # text-embedding-3-small has 1536 dimensions
        metric_type="IP",  # Inner product distance
        consistency_level="Strong",  # Strong consistency level
    )

    data = []
    for i, question in enumerate(tqdm(questions, desc="Creating embeddings")):
        data.append(
            {
                "id": i,
                "vector": await create_embedding(question, openai),
                "text": question,
            }
        )

    milvus_client.insert(collection_name=collection_name, data=data)


async def search_milvus(
    question: str,
    openai: AsyncOpenAI,
    collection_name: str,
) -> list[str]:
    search_res = milvus_client.search(
        collection_name=collection_name,
        data=[await create_embedding(question, openai)],
        limit=3,
        search_params={"metric_type": "IP", "params": {}},
        output_fields=["text"],
    )

    return [res["entity"]["text"] for res in search_res[0]]


async def extract_questions(path: str) -> None:
    """Extract questions from a PDF document using an LLM agent.

    Args:
        path: Path to the PDF document to analyze
    """
    logfire.instrument_openai(openai)

    logfire.info("Extracting questions from {path}", path=path)

    result = await extract_agent.run(
        [
            BinaryContent(data=get_pdf_bytes(path), media_type="application/pdf"),
        ],
        deps=Deps(openai=openai),  # Fixed deps parameter to pass OpenAI client
    )
    if isinstance(result.output, model.Questions):
        questions = [part.content for q in result.output.questions for part in q.parts]
        await load_data_into_milvus(questions, openai)
    print(result.output)


async def retrieve_questions(query: str) -> str:
    result = await retrieval_agent.run(query, deps=Deps(openai=openai))
    print(result.output)
    return result.output


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else None
    if action == "extract":
        asyncio.run(extract_questions("cre.pdf"))
    elif action == "retrieve":
        asyncio.run(retrieve_questions("Give seven difference"))
    else:
        print(
            "Usage: python question_extractor.py extract|retrieve",
            file=sys.stderr,
        )
