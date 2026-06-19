from fastapi import APIRouter, HTTPException
from app.schemas.query import QueryRequest, QueryResponse, SchemaResponse
from app.core.claude_service import question_to_sql, explain_sql
from app.db.database import run_query, get_schema_context
from app.core.config import MAX_ROWS

router = APIRouter(prefix="/query", tags=["Query"])


@router.post("/", response_model=QueryResponse)
def run_text_to_sql(request: QueryRequest):
    """
    Main endpoint:
    1. Send user question → Claude → SQL
    2. Execute SQL on DB
    3. If error, retry once with error context
    4. Return rows + plain-English explanation
    """
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Step 1: Generate SQL
    sql = question_to_sql(question)

    if sql == "CANNOT_ANSWER":
        raise HTTPException(
            status_code=422,
            detail="This question cannot be answered from the available database schema."
        )

    # Step 2: Execute — retry once on failure
    try:
        rows = run_query(sql)
    except Exception as e:
        # Auto-correct loop: send error back to Claude
        sql = question_to_sql(question, retry_error=str(e))
        try:
            rows = run_query(sql)
        except Exception as e2:
            raise HTTPException(status_code=500, detail=f"SQL execution failed: {e2}")

    # Step 3: Trim to MAX_ROWS
    rows = rows[:MAX_ROWS]
    columns = list(rows[0].keys()) if rows else []

    # Step 4: Explain SQL
    explanation = explain_sql(sql)

    return QueryResponse(
        question=question,
        sql=sql,
        explanation=explanation,
        rows=rows,
        row_count=len(rows),
        columns=columns,
    )


@router.get("/schema", response_model=SchemaResponse)
def get_schema():
    """Return the current database schema as text."""
    return SchemaResponse(schema_text=get_schema_context())
