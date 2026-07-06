"""Simple, deterministic skill comparison helpers.

We store skills as comma-separated strings. This module normalizes them,
splits them, and computes matching/missing skills using plain Python sets.
No LLM required for this comparison — the LLM only produces natural language.
"""

from typing import Iterable, List


def parse_skills(raw: str | None) -> List[str]:
    """Split a comma-separated skill string into a clean lowercased list."""
    if not raw:
        return []
    parts = [item.strip().lower() for item in raw.split(",")]
    # Deduplicate while preserving order.
    seen: set[str] = set()
    result: List[str] = []
    for item in parts:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def compare_skills(
    user_skills: Iterable[str], job_skills: Iterable[str]
) -> tuple[List[str], List[str]]:
    """Return (matching, missing) skills based on set membership."""
    user_set = {s.lower() for s in user_skills if s}
    job_list = [s for s in job_skills if s]
    matching = [s for s in job_list if s.lower() in user_set]
    missing = [s for s in job_list if s.lower() not in user_set]
    return matching, missing
