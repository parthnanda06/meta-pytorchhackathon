"""
LLM client — wraps OpenAI API calls for structured startup analysis generation.

All calls use temperature=0 for deterministic, reproducible output.
Prompts are brutally honest — no buzzwords, no fake positivity.
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict

from openai import OpenAI

# ---------------------------------------------------------------------------
# System prompts (brutal, role-specific)
# ---------------------------------------------------------------------------

SYSTEM_PROMPTS: Dict[str, str] = {
    "problem": (
        "You are a brutally honest startup analyst.\n\n"
        "Strict rules:\n"
        "- Avoid generic phrases like 'underserved market' or 'leverages technology'\n"
        "- Do not assume the problem is valid — challenge it\n"
        "- Highlight any ambiguity or missing clarity\n\n"
        "Tone: Direct, critical, and realistic.\n"
        "Do NOT make the problem sound better than it is.\n"
        "Respond in plain paragraphs only (no headings, no bullet points, no markdown)."
    ),
    "solution": (
        "You are a critical product evaluator.\n\n"
        "Strict rules:\n"
        "- Avoid buzzwords and vague statements\n"
        "- Be skeptical — assume execution is hard\n"
        "- If the solution sounds like a rebranded existing product, say it\n\n"
        "Tone: Harsh, practical, no hype.\n"
        "Respond in plain paragraphs only (no headings, no bullet points, no markdown)."
    ),
    "market": (
        "You are a skeptical market analyst.\n\n"
        "Strict rules:\n"
        "- Do NOT assume a large market without justification\n"
        "- Penalize crowded or saturated markets\n"
        "- If this is a copy of an existing idea, call it out clearly\n\n"
        "Tone: Realistic and critical.\n"
        "Respond in plain paragraphs only (no headings, no bullet points, no markdown)."
    ),
}

# ---------------------------------------------------------------------------
# Analysis prompts (brutal, verdict-style)
# ---------------------------------------------------------------------------

ANALYSIS_PROMPTS: Dict[str, str] = {
    "problem": (
        "Analyze the core problem this startup idea is trying to solve.\n\n"
        "Startup idea: {idea}\n\n"
        "Clearly identify:\n"
        "1. Exact target users (be specific, not broad categories)\n"
        "2. The real pain they face (concrete, not abstract)\n"
        "3. Why existing solutions fail or are insufficient\n\n"
        "If the problem is weak, unnecessary, or already well-solved, say it clearly.\n\n"
        "End with exactly one of these lines:\n"
        '"Verdict: Strong problem" OR "Verdict: Weak problem"'
    ),
    "solution": (
        "Evaluate the proposed solution for this startup idea.\n\n"
        "Startup idea: {idea}\n\n"
        "Previous problem analysis:\n{problem_analysis}\n\n"
        "Instructions:\n"
        "1. Explain how the solution actually works in practice\n"
        "2. Check if it truly solves the stated problem\n"
        "3. Identify technical, operational, or adoption challenges\n"
        "4. Call out if the solution is overengineered, unrealistic, or unnecessary\n\n"
        "End with exactly one of these lines:\n"
        '"Verdict: Strong solution" OR "Verdict: Weak solution"'
    ),
    "market": (
        "Evaluate the market viability of this startup idea.\n\n"
        "Startup idea: {idea}\n\n"
        "Previous analysis:\n- Problem: {problem_analysis}\n- Solution: {solution_analysis}\n\n"
        "Instructions:\n"
        "1. Identify who will actually pay for this product\n"
        "2. Assess willingness to pay realistically\n"
        "3. Mention direct competitors or substitutes\n"
        "4. Highlight at least one major risk (competition, behavior, pricing, etc.)\n\n"
        "If this is a copy of an existing idea, call it out clearly.\n\n"
        "End with exactly one of these lines:\n"
        '"Verdict: Strong market" OR "Verdict: Weak market"'
    ),
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_analysis(
    idea: str,
    analysis_type: str,
    current_state: Dict[str, Any],
    model: str = "gpt-4o-mini",
) -> str:
    """
    Call the OpenAI API to produce a brutally honest analysis with a verdict.

    Parameters
    ----------
    idea : str
        The startup idea being evaluated.
    analysis_type : str
        One of ``"problem"``, ``"solution"``, ``"market"``.
    current_state : dict
        The current environment state (used to inject prior analyses into
        the prompt for context continuity).
    model : str
        The OpenAI model to use. Defaults to ``gpt-4o-mini``.

    Returns
    -------
    str
        The generated analysis text (ending with a verdict line).
    """
    try:
        api_base_url = os.getenv("API_BASE_URL") or os.getenv("OPENAI_API_BASE") or "https://api.openai.com/v1"
        model_name = os.getenv("MODEL_NAME") or os.getenv("LLM_MODEL") or model
        api_key = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY")

        if not api_key:
            # Fallback to a dummy key if running in an environment that expects requests but hasn't provided a key yet
            api_key = "dummy-key-for-proxy"

        client = OpenAI(
            base_url=api_base_url,
            api_key=api_key
        )

        template = ANALYSIS_PROMPTS[analysis_type]
        analysis = current_state.get("analysis", {})

        prompt = template.format(
            idea=idea,
            problem_analysis=analysis.get("problem", "N/A"),
            solution_analysis=analysis.get("solution", "N/A"),
        )

        system_prompt = SYSTEM_PROMPTS[analysis_type]

        response = client.chat.completions.create(
            model=model_name,
            temperature=0,
            max_tokens=600,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error connecting to LLM: {str(e)}\n\nVerdict: Weak {analysis_type}"


def grade_analysis_with_llm(
    idea: str,
    analysis: Dict[str, str],
    model: str = "gpt-4o-mini",
) -> Dict[str, Any]:
    """
    Use the LLM to produce a strict, structured score for the analysis.

    Returns a dict with breakdown and final score:
        {
            "problem": float,
            "solution": float,
            "market": float,
            "final": float,
            "raw": str,
        }
    """
    try:
        api_base_url = os.getenv("API_BASE_URL") or os.getenv("OPENAI_API_BASE") or "https://api.openai.com/v1"
        model_name = os.getenv("MODEL_NAME") or os.getenv("LLM_MODEL") or model
        api_key = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY")

        if not api_key:
            # Fallback to a dummy key if running in an environment that expects requests but hasn't provided a key yet
            api_key = "dummy-key-for-proxy"

        client = OpenAI(
            base_url=api_base_url,
            api_key=api_key
        )

        analysis_text = (
            f"Problem analysis: {analysis.get('problem', 'MISSING')}\n\n"
            f"Solution analysis: {analysis.get('solution', 'MISSING')}\n\n"
            f"Market analysis: {analysis.get('market', 'MISSING')}"
        )

        grading_prompt = (
            "You are a strict and skeptical startup evaluator.\n\n"
            "Evaluate the overall startup analysis and assign a score "
            "between 0.0 and 1.0.\n\n"
            f"Startup idea: {idea}\n\n"
            f"{analysis_text}\n\n"
            "Scoring criteria:\n"
            "- Problem clarity (0.0-0.3)\n"
            "- Solution feasibility (0.0-0.3)\n"
            "- Market viability (0.0-0.4)\n\n"
            "Strict evaluation rules:\n"
            "- Be harsh — do NOT give high scores easily\n"
            "- Penalize vague or generic analysis\n"
            "- Penalize unrealistic solutions\n"
            "- Penalize crowded or undifferentiated markets\n"
            "- If any section is weak, reduce score significantly\n"
            "- If the idea feels like a copy of an existing product, penalize heavily\n\n"
            "Output format (STRICT — follow exactly):\n"
            "Problem: X/0.3\n"
            "Solution: Y/0.3\n"
            "Market: Z/0.4\n"
            "Final: TOTAL\n\n"
            "Return ONLY this format. No explanation."
        )

        response = client.chat.completions.create(
            model=model_name,
            temperature=0,
            max_tokens=50,
            messages=[
                {"role": "system", "content": "You are a strict scoring system. Follow the output format exactly. No text beyond the four score lines."},
                {"role": "user", "content": grading_prompt},
            ],
        )

        raw = response.choices[0].message.content.strip()
        return _parse_structured_score(raw)
    except Exception as e:
        return _parse_structured_score("")


def _parse_structured_score(raw: str) -> Dict[str, Any]:
    """
    Parse the structured grading output:
        Problem: 0.2/0.3
        Solution: 0.15/0.3
        Market: 0.25/0.4
        Final: 0.6
    """
    result = {
        "problem": 0.0,
        "solution": 0.0,
        "market": 0.0,
        "final": 0.0,
        "raw": raw,
    }

    for line in raw.strip().splitlines():
        line = line.strip()
        # Match patterns like "Problem: 0.2/0.3" or "Final: 0.6"
        match = re.match(r"(Problem|Solution|Market|Final):\s*([\d.]+)", line, re.IGNORECASE)
        if match:
            key = match.group(1).lower()
            value = float(match.group(2))
            result[key] = value

    # Ensure final is within strict bounds (strictly between 0 and 1)
    result["final"] = max(0.01, min(0.99, result["final"]))

    return result
