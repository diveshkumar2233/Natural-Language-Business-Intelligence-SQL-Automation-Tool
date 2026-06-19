from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import GROQ_MODEL, ACTIVE_DB_URL
from app.schemas.query import HealthResponse

app = FastAPI(
    title="Text-to-SQL Engine",
    description="Convert plain-English questions to SQL using Claude AI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        db=ACTIVE_DB_URL.split("://")[0],
        model=GROQ_MODEL,
    )
