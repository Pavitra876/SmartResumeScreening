"""
recommendation/career_advisor.py
Turns ATS analysis results into actionable career recommendations.
"""

from recommendation.learning_resources import get_resources_for_skill


def get_priority_skills(missing_skills: list[str], limit: int = 3) -> list[str]:
    return missing_skills[:limit]


def build_recommendation(ats_score: float, missing_skills: list[str]) -> dict:
    if ats_score >= 75:
        verdict = "You're a strong match for this role. Focus on polishing your remaining gaps."
    elif ats_score >= 50:
        verdict = "You're a reasonable match. A few targeted skills would meaningfully boost your fit."
    elif ats_score >= 25:
        verdict = "There's a noticeable skill gap for this role. Prioritize the skills below before applying."
    else:
        verdict = "This role may not be the best fit yet. Consider building these foundational skills first, or explore a closer-matching role."

    priority_skills = get_priority_skills(missing_skills)
    roadmap = []
    for skill in priority_skills:
        resources = get_resources_for_skill(skill)
        roadmap.append({"skill": skill, "resources": resources})

    return {"verdict": verdict, "roadmap": roadmap}


def suggest_alternative_roles(all_roles_with_scores: list[dict], current_role: str, threshold: float = 50.0) -> list[dict]:
    alternatives = [
        r for r in all_roles_with_scores
        if r["role_name"] != current_role and r["score"] >= threshold
    ]
    alternatives.sort(key=lambda r: r["score"], reverse=True)
    return alternatives