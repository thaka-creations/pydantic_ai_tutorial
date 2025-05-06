from typing import Union

from fake_database import DatabaseConn, QueryError
from pydantic import BaseModel

from pydantic_ai import Agent, RunContext, ModelRetry


class Success(BaseModel):
    sql_query: str


class InvalidRequest(BaseModel):
    error_message: str


Output = Union[Success, InvalidRequest]
agent: Agent[DatabaseConn, Output] = Agent(
    "google-gla:gemini-1.5-flash",
    output_type=Output,  # type: ignore
    deps_type=DatabaseConn,
    system_prompt="Generate PostgreSQL flavored SQL queries based on user input.",
)


@agent.output_validator
async def validate_sql(ctx: RunContext[DatabaseConn], output: Output) -> Output:
    if isinstance(output, InvalidRequest):
        return output
    try:
        await ctx.deps.execute(f"EXPLAIN {output.sql_query}")
    except QueryError as e:
        raise ModelRetry(f"Invalid query: {e}") from e
    else:
        return output


result = agent.run_sync(
    "get me users who were last active yesterday.", deps=DatabaseConn()
)
print(result.output)
