from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.database import initialize_database
from app.api.teacher_routes import router as teacher_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="TutorIA API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check():
    return {"status": "ok", "database": "sqlite"}

app.include_router(
    teacher_router
)