"""
Grading module — scores the completeness and quality of a startup analysis.

Two grading strategies:
    1. ``grade()``            — deterministic, rule-based scoring.
    2. ``grade_with_llm()``   — optional LLM-based quality scoring.
"""

from __future__ import annotations

from typing import Any, Dict

from llm.client import grade_analysis_with_llm


# ---------------------------------------------------------------------------
# Rule-based grading
# ---------------------------------------------------------------------------

# Minimum character thresholds for "adequate" analysis depth.
MIN_LENGTH_GOOD = 300
MIN_LENGTH_ACCEPTABLE = 150

# Weight per section (must sum to 1.0).
SECTION_WEIGHTS: Dict[str, float] = {
    "problem": 0.3,
    "solution": 0.3,
    "market": 0.39,
}

# Quality keywords per section (presence → bonus).
QUALITY_KEYWORDS: Dict[str, list[str]] = {
    "problem": ["target user", "pain", "existing solution", "insufficient", "weak", "verdict"],
    "solution": ["works", "risk", "challenge", "overengineered", "solves", "verdict"],
    "market": ["pay", "competitor", "risk", "saturated", "willingness", "verdict"],
}


def grade(state: Dict[str, Any]) -> float:
    """
    Rule-based grading: returns a score between 0.0 and 1.0.

    Scoring per section:
        - Present and ≥ MIN_LENGTH_GOOD chars  →  base 0.7
        - Present and ≥ MIN_LENGTH_ACCEPTABLE   →  base 0.4
        - Present but short                     →  base 0.2
        - Empty / missing                       →  0.0
        + keyword bonus up to 0.3 per section

    Final score = weighted sum across sections.
    """
    idea = str(state.get("idea", ""))
    alpha_chars = sum(c.isalpha() for c in idea)
    if alpha_chars < 15:
        # Penalize if the input idea is largely just symbols or empty
        return 0.01

    analysis: Dict[str, str] = state.get("analysis", {})
    total = 0.0

    for section, weight in SECTION_WEIGHTS.items():
        text = analysis.get(section, "")
        if not text:
            continue

        # Length-based base score -------------------------------------------
        length = len(text)
        if length >= MIN_LENGTH_GOOD:
            base = 0.7
        elif length >= MIN_LENGTH_ACCEPTABLE:
            base = 0.4
        else:
            base = 0.2

        # Keyword bonus (up to 0.3) ----------------------------------------
        keywords = QUALITY_KEYWORDS.get(section, [])
        if keywords:
            hits = sum(1 for kw in keywords if kw.lower() in text.lower())
            # Require more hits to get the full bonus point
            keyword_score = min(0.3, (hits / max(1, len(keywords) - 2)) * 0.3)
        else:
            keyword_score = 0.0

        section_score = min(0.99, base + keyword_score)
        total += section_score * weight

    final_score = round(total, 4)
    if final_score <= 0.0:
        return 0.01
    elif final_score >= 1.0:
        return 0.99
    return final_score


# ---------------------------------------------------------------------------
# LLM-based grading (optional)
# ---------------------------------------------------------------------------


def grade_with_llm(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use an LLM to produce a strict, structured score breakdown.

    Returns a dict:
        {
            "problem": float,   # out of 0.3
            "solution": float,  # out of 0.3
            "market": float,    # out of 0.4
            "final": float,     # total 0.0-1.0
            "raw": str,         # raw LLM output
        }

    Requires ``OPENAI_API_KEY`` to be set.
    """
    idea = state.get("idea", "")
    analysis = state.get("analysis", {})
    return grade_analysis_with_llm(idea=idea, analysis=analysis)

def grade_with_llm_score(state: Dict[str, Any]) -> float:
    """
    OpenEnv-compliant wrapper for LLM-based grading.
    Returns just the float final score.
    """
    result = grade_with_llm(state)
    score = result.get("final", 0.01)
    if score >= 1.0: return 0.99
    if score <= 0.0: return 0.01
    return float(score)
