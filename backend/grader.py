"""
Grading module — scores the completeness and quality of a startup analysis.

Deterministic, rule-based scoring with strict boundary safety [0.001, 0.999].
"""

from __future__ import annotations

from typing import Any, Dict



def safe_score(score):
    try:
        score = float(score)
    except:
        return 0.500

    # Round to 3 decimal places
    score = round(score, 3)

    # HARD BOUNDARIES: [0.01, 0.99] inclusive
    # 0.0 -> 0.01, 1.0 -> 0.99. Other values like 0.73, 0.99 remain.
    if score <= 0.0:
        return 0.01
    if score >= 1.0:
        return 0.99

    return score


# ---------------------------------------------------------------------------
# Rule-based grading configuration
# ---------------------------------------------------------------------------

# Minimum character thresholds for analysis depth.
MIN_LENGTH_GOOD = 300
MIN_LENGTH_ACCEPTABLE = 150

# Weights summing to 1.0 to allow full scoring potential.
SECTION_WEIGHTS: Dict[str, float] = {
    "problem": 0.33,
    "solution": 0.33,
    "market": 0.34,
}

# Quality keywords per section (presence improves score).
QUALITY_KEYWORDS: Dict[str, list[str]] = {
    "problem": ["target user", "pain", "existing solution", "insufficient", "weak", "verdict"],
    "solution": ["works", "risk", "challenge", "overengineered", "solves", "verdict"],
    "market": ["pay", "competitor", "risk", "saturated", "willingness", "verdict"],
}


def grade(state: Dict[str, Any]) -> float:
    """
    Primary rule-based grader.
    Ensures final score is always in (0.05, 0.95) for ANY input.
    """
    idea = str(state.get("idea", ""))
    analysis: Dict[str, str] = state.get("analysis", {})
    total = 0.0

    for section, weight in SECTION_WEIGHTS.items():
        text = analysis.get(section, "")
        
        if not text:
            # Prevent zero-score state by providing a tiny floor for each section.
            total += 0.05 * weight
            continue

        # Length-based base score components.
        length = len(text)
        if length >= MIN_LENGTH_GOOD:
            base = 0.65
        elif length >= MIN_LENGTH_ACCEPTABLE:
            base = 0.4
        else:
            base = 0.2

        # Keyword bonus scoring (up to 0.3).
        keywords = QUALITY_KEYWORDS.get(section, [])
        hits = sum(1 for kw in keywords if kw.lower() in text.lower()) if keywords else 0
        keyword_score = min(0.3, (hits / max(1, len(keywords) - 2)) * 0.3) if keywords else 0

        # Section score
        section_score = base + keyword_score
        total += section_score * weight

    return safe_score(total)


# ---------------------------------------------------------------------------
# Grading wrappers
# ---------------------------------------------------------------------------

def grade_with_llm_score(state):
    return 0.5

# Optional difficulty-specific entry points if required by YAML.
def grade_easy(state: Dict[str, Any]) -> float:
    return grade(state)

def grade_medium(state: Dict[str, Any]) -> float:
    return grade(state)

def grade_hard(state: Dict[str, Any]) -> float:
    return grade(state)
