import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (ensures all models register with Base)
from app.database import Base, engine
from app.routers import (
    auth,
    jobs,
    profiles,
    recommendations,
    resumes,
    saved_jobs,
    users,
)

load_dotenv()

# Create tables on startup. Simple + student-friendly (no Alembic yet).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Job Recommendation Assistant API",
    description=(
        "Full-stack AI job-recommendation API. "
        "PostgreSQL + Qdrant + LangChain + Groq."
    ),
    version="2.0.0",
)

# CORS: allow the local Vite dev server by default. In production, set
# FRONTEND_URL to the deployed frontend origin.
allowed_origins = [os.getenv("FRONTEND_URL", "http://localhost:5173")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(profiles.router)
app.include_router(jobs.router)
app.include_router(resumes.router)
app.include_router(saved_jobs.router)
app.include_router(recommendations.router)


@app.get("/")
def health_check():
    return {"message": "AI Job Recommendation Assistant API is running"}

