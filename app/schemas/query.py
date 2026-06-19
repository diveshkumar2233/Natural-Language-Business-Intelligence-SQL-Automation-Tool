from pydantic import BaseModel
from typing import Any


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question: str
    sql: str
    explanation: str
    rows: list[dict[str, Any]]
    row_count: int
    columns: list[str]


class SchemaResponse(BaseModel):
    schema_text: str


class HealthResponse(BaseModel):
    status: str
    db: str
    model: str
