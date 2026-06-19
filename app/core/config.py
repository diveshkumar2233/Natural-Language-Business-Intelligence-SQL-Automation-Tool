from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL     = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
DATABASE_URL   = os.getenv("DATABASE_URL", "")
SQLITE_URL     = os.getenv("SQLITE_URL", "sqlite:///./text2sql.db")
MAX_ROWS       = int(os.getenv("MAX_ROWS", 200))
QUERY_TIMEOUT  = int(os.getenv("QUERY_TIMEOUT_SECONDS", 10))

# Use SQLite if no PostgreSQL URL provided
ACTIVE_DB_URL = DATABASE_URL if DATABASE_URL else SQLITE_URL
