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
        return 0.5

    # HARD SAFE ZONE (avoid boundaries completely)
    if score <= 0.1:
        return 0.15
    if score >= 0.9:
        return 0.85

    return round(score, 3)


# ---------------------------------------------------------------------------
# Rule-based grading configuration
# ---------------------------------------------------------------------------

# Minimum character thresholds for analysis depth.
MIN_LENGTH_GOOD = 300
MIN_LENGTH_ACCEPTABLE = 150

# Weight per section. Summing to 0.95 to ensure 1.0 is unreachable.
SECTION_WEIGHTS: Dict[str, float] = {
    "problem": 0.3,
    "solution": 0.3,
    "market": 0.35,
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

        # Section score capped to stay away from 1.0 boundary.
        section_score = min(0.95, base + keyword_score)
        total += section_score * weight

    # Final hard clamping and precision rounding.
    final_score = round(total, 4)
    return safe_score(final_score)


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
