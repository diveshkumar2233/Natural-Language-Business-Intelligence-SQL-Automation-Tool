from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError
from app.core.config import ACTIVE_DB_URL

engine = create_engine(ACTIVE_DB_URL, pool_pre_ping=True)


def get_connection():
    return engine.connect()


def get_schema_context() -> str:
    """
    Introspect the database and return a plain-text schema description
    that will be injected into the Claude prompt.
    """
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    lines = ["DATABASE SCHEMA:\n"]
    for table in tables:
        cols = inspector.get_columns(table)
        fks  = inspector.get_foreign_keys(table)

        col_defs = ", ".join(
            f"{c['name']} {str(c['type'])}" + (" PK" if c.get("primary_key") else "")
            for c in cols
        )
        lines.append(f"Table: {table} ({col_defs})")

        for fk in fks:
            lines.append(
                f"  FK: {table}.{fk['constrained_columns']} → "
                f"{fk['referred_table']}.{fk['referred_columns']}"
            )

    return "\n".join(lines)


def run_query(sql: str) -> list[dict]:
    """
    Execute a read-only SQL query and return rows as list of dicts.
    Raises ValueError for non-SELECT statements (safety guard).
    """
    clean = sql.strip().upper()
    if not clean.startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed.")

    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
    return rows
