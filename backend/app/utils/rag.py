"""LangChain + Groq RAG helper.

Kept intentionally simple:
1. We already retrieved top jobs from Qdrant + PostgreSQL.
2. We build a short grounded prompt with the resume text and job details.
3. We call the Groq LLM via LangChain's ChatGroq wrapper.
4. We parse the JSON response into a plain dict.

No agents, no chains-of-chains — a single prompt + a single LLM call.
"""

from __future__ import annotations

import json
import os
from typing import List

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

_llm: ChatGroq | None = None


def _get_llm() -> ChatGroq:
    global _llm
    if _llm is None:
        if not GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY missing. Set it in backend/.env before "
                "generating recommendations."
            )
        _llm = ChatGroq(
            model=GROQ_MODEL,
            api_key=GROQ_API_KEY,
            temperature=0.2,
            max_tokens=400,
        )
    return _llm


SYSTEM_PROMPT = (
    "You are a helpful career assistant. You will receive a candidate's "
    "resume/profile summary and a single job description. "
    "Produce a short, grounded explanation of why the job might match, "
    "based ONLY on the information provided. Do not invent facts."
)


def explain_match(
    resume_text: str,
    job_title: str,
    job_company: str,
    job_description: str,
    matching_skills: List[str],
    missing_skills: List[str],
) -> str:
    """Return a short natural-language explanation for one job match."""
    llm = _get_llm()

    user_prompt = (
        f"Candidate resume/profile summary (may be truncated):\n"
        f"----\n{resume_text[:2000]}\n----\n\n"
        f"Job: {job_title} at {job_company}\n"
        f"Description (truncated):\n----\n{job_description[:1500]}\n----\n\n"
        f"Matching skills already found deterministically: "
        f"{', '.join(matching_skills) if matching_skills else 'none'}\n"
        f"Missing skills already found deterministically: "
        f"{', '.join(missing_skills) if missing_skills else 'none'}\n\n"
        "Reply in 3-4 sentences: why this role might match the candidate, "
        "what strengths line up, and one concrete next skill to learn."
    )

    response = llm.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
    )
    return str(response.content).strip()


def skill_gap_suggestions(
    resume_text: str,
    job_title: str,
    job_description: str,
    missing_skills: List[str],
) -> str:
    """Return a short study/upskilling plan for missing skills."""
    if not missing_skills:
        return "You already cover the listed required skills for this role."

    llm = _get_llm()
    user_prompt = (
        f"Candidate resume/profile summary (truncated):\n"
        f"----\n{resume_text[:1500]}\n----\n\n"
        f"Target role: {job_title}\n"
        f"Job description (truncated):\n----\n{job_description[:1000]}\n----\n\n"
        f"Missing skills: {', '.join(missing_skills)}\n\n"
        "Give a short, practical study plan (max 4 bullet points) that would "
        "help the candidate close these skill gaps for this role."
    )
    response = llm.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
    )
    return str(response.content).strip()
