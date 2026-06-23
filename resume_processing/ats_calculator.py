"""
resume_processing/ats_calculator.py
Calculates the ATS (Applicant Tracking System) score and skill gap
by comparing skills found in a resume against the skills required for a role.
"""


def calculate_ats_score(matched_skills: list[str], required_skills: list[str]) -> float:
    """
    ATS score = (matched skills / total required skills) * 100.
    Returns a float rounded to 1 decimal place, e.g. 72.7
    """
    if not required_skills:
        return 0.0
    score = (len(matched_skills) / len(required_skills)) * 100
    return round(score, 1)


def get_skill_gap(matched_skills: list[str], required_skills: list[str]) -> list[str]:
    """Returns the list of required skills NOT found in the resume."""
    matched_set = set(matched_skills)
    return [skill for skill in required_skills if skill not in matched_set]


def analyze_resume_for_role(resume_skills: list[str], required_skills: list[str]) -> dict:
    """
    Convenience function: given skills found in a resume and skills required
    for a role, returns a full analysis dict ready to display or save.
    """
    matched = [skill for skill in required_skills if skill in resume_skills]
    missing = get_skill_gap(matched, required_skills)
    score = calculate_ats_score(matched, required_skills)

    return {
        "ats_score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "total_required": len(required_skills),
        "total_matched": len(matched),
    }