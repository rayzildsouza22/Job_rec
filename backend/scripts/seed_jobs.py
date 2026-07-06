"""Seed a handful of sample jobs and embed them in Qdrant.

Run from the backend/ folder with the venv active:

    python -m scripts.seed_jobs
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running as `python -m scripts.seed_jobs` from backend/
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models.jobs import Job  # noqa: E402
from app.routers.jobs import _job_to_embedding_text  # noqa: E402
from app.utils.vector_store import upsert_job  # noqa: E402

SAMPLE_JOBS = [
    {
        "company": "Northwind Labs",
        "title": "Junior Backend Engineer (Python)",
        "description": (
            "Build REST APIs with FastAPI, work with PostgreSQL, "
            "write tests, and collaborate on a small microservice team."
        ),
        "required_skills": "Python, FastAPI, PostgreSQL, Git, REST",
        "location": "Bengaluru, India",
        "experience": "0-2 years",
        "salary": "6-10 LPA",
    },
    {
        "company": "BrightStack",
        "title": "Frontend Developer (React)",
        "description": (
            "Build responsive dashboards with React and TypeScript, "
            "consume REST APIs with Axios, and ship features weekly."
        ),
        "required_skills": "React, TypeScript, CSS, Axios, HTML",
        "location": "Remote (India)",
        "experience": "1-3 years",
        "salary": "8-14 LPA",
    },
    {
        "company": "DataForge",
        "title": "Data Analyst",
        "description": (
            "Analyse product KPIs with SQL and Python, build dashboards, "
            "and communicate findings to product managers."
        ),
        "required_skills": "SQL, Python, Pandas, Excel, Data Visualization",
        "location": "Hyderabad, India",
        "experience": "0-2 years",
        "salary": "5-9 LPA",
    },
    {
        "company": "Modelry",
        "title": "ML Engineer (NLP)",
        "description": (
            "Work on NLP pipelines, fine-tune transformer models, "
            "build retrieval systems with vector databases."
        ),
        "required_skills": "Python, PyTorch, NLP, Transformers, Vector Databases",
        "location": "Bengaluru, India",
        "experience": "1-3 years",
        "salary": "12-20 LPA",
    },
    {
        "company": "CloudNimbus",
        "title": "DevOps Engineer",
        "description": (
            "Own CI/CD pipelines, manage Kubernetes clusters, "
            "and improve observability across services."
        ),
        "required_skills": "Docker, Kubernetes, AWS, Terraform, CI/CD",
        "location": "Pune, India",
        "experience": "2-4 years",
        "salary": "14-22 LPA",
    },
    {
        "company": "PayLoop",
        "title": "Full Stack Developer",
        "description": (
            "Ship features end-to-end: React on the frontend, "
            "FastAPI/Node on the backend, PostgreSQL for storage."
        ),
        "required_skills": "React, TypeScript, Node.js, PostgreSQL, REST",
        "location": "Remote",
        "experience": "1-3 years",
        "salary": "10-16 LPA",
    },
]


def main() -> None:
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        created = 0
        for data in SAMPLE_JOBS:
            existing = (
                session.query(Job)
                .filter(Job.company == data["company"], Job.title == data["title"])
                .first()
            )
            if existing:
                continue
            job = Job(**data)
            session.add(job)
            session.flush()  # get id
            try:
                upsert_job(job.id, _job_to_embedding_text(job))
            except Exception as exc:  # noqa: BLE001
                print(f"[seed] Qdrant upsert failed for {data['title']}: {exc}")
            created += 1
        session.commit()
        print(f"Seeded {created} new jobs.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
