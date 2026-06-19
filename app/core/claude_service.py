from groq import Groq
from app.core.config import GROQ_API_KEY, GROQ_MODEL
from app.db.database import get_schema_context

client = Groq(api_key=GROQ_API_KEY)

# ── System prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert SQL data analyst assistant.

Your job:
1. Convert the user's plain-English question into a valid SQL SELECT query.
2. Return ONLY the SQL query — no explanation, no markdown fences, no comments.
3. The query must be read-only (SELECT only). Never generate INSERT, UPDATE, DELETE, DROP, etc.
4. Use table and column names exactly as shown in the schema.
5. Add a LIMIT clause when the result could be large (default LIMIT 100).
6. If the question cannot be answered from the schema, return exactly: CANNOT_ANSWER

{schema}
"""

EXPLAIN_PROMPT = """You are a helpful data analyst.

Given this SQL query, explain what it does in 2-3 simple sentences for a non-technical business user.
Focus on: what data is being retrieved, any filters applied, and how results are sorted/grouped.

SQL:
{sql}
"""


def question_to_sql(user_question: str, retry_error: str = "") -> str:
    """Convert a natural language question to SQL using Groq (Llama 3.3)."""
    schema = get_schema_context()
    system = SYSTEM_PROMPT.format(schema=schema)

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_question},
    ]

    # If retrying after an error, append the error context
    if retry_error:
        messages.append({
            "role": "assistant",
            "content": "(previous SQL had an error)"
        })
        messages.append({
            "role": "user",
            "content": (
                f"That SQL caused this error: {retry_error}\n"
                "Please fix the SQL and return only the corrected query."
            )
        })

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        max_tokens=512,
        temperature=0,
        messages=messages,
    )
    return response.choices[0].message.content.strip()


def explain_sql(sql: str) -> str:
    """Ask Groq to explain a SQL query in plain English."""
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        max_tokens=256,
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a helpful data analyst who explains SQL in plain English."},
            {"role": "user", "content": EXPLAIN_PROMPT.format(sql=sql)},
        ],
    )
    return response.choices[0].message.content.strip()
