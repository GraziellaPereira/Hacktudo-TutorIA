from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import initialize_database
from app.api.teacher_routes import router as teacher_router
from app.api.student_routes import router as student_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="TutorIA API",
    version="0.1.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        # depois vamos trocar pela URL do Render
        "https://SEU-FRONTEND.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "database": "sqlite"
    }

app.include_router(
    teacher_router
)

app.include_router(
    student_router
)