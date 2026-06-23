"""
resume_processing/skill_extractor.py
Detects which known skills appear in a resume's extracted text.

Approach: rather than relying purely on spaCy's general NLP entities (which
aren't trained to recognize "Power BI" or "TensorFlow" as skills), we match
against the project's own skills master list -- the same approach real ATS
tools use. spaCy is used here to clean/normalize the text (lowercasing,
lemmatizing) so matches aren't missed due to casing or simple variations.
"""

import re
import spacy

# Load the small English model once when this module is imported.
# (Run `python -m spacy download en_core_web_sm` once before using this.)
_nlp = spacy.load("en_core_web_sm")


def _normalize(text: str) -> str:
    """Lowercase and clean text for reliable substring matching."""
    return text.lower()


def extract_skills_from_text(resume_text: str, known_skills: list[str]) -> list[str]:
    """
    Given the resume's raw text and a list of known skill names (e.g. from
    the database), return the subset of skills that appear in the resume.

    Uses word-boundary regex matching so "R" doesn't match inside "Marketing",
    and "Java" doesn't falsely match inside "JavaScript" (handled as a
    separate skill if needed).
    """
    normalized_text = _normalize(resume_text)
    found_skills = []

    for skill in known_skills:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, normalized_text):
            found_skills.append(skill)

    return found_skills


def clean_text_with_spacy(text: str) -> str:
    """
    Optional helper: runs text through spaCy to strip out punctuation/stopwords
    noise, useful if you want a cleaner version of the resume text to display
    or analyze further.
    """
    doc = _nlp(text)
    tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    return " ".join(tokens)