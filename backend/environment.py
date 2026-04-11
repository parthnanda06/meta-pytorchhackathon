"""
StartupEnv — an OpenEnv-compliant environment for step-based startup idea validation.

Actions:
    "analyze_problem"   →  fills state["analysis"]["problem"]   →  reward +0.3
    "analyze_solution"  →  fills state["analysis"]["solution"]  →  reward +0.3
    "analyze_market"    →  fills state["analysis"]["market"]    →  reward +0.4

Total cumulative reward across a complete episode: 1.0
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional, Tuple

from .client import generate_analysis

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_ACTIONS = ("analyze_problem", "analyze_solution", "analyze_market")

REWARD_MAP: Dict[str, float] = {
    "analyze_problem": 0.33,
    "analyze_solution": 0.33,
    "analyze_market": 0.34,
}

ANALYSIS_KEY_MAP: Dict[str, str] = {
    "analyze_problem": "problem",
    "analyze_solution": "solution",
    "analyze_market": "market",
}


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------


class StartupEnv:
    """OpenEnv-compliant environment for evaluating startup ideas."""

    def __init__(self, idea: str, use_llm: bool = True) -> None:
        """
        Parameters
        ----------
        idea : str
            The startup idea to evaluate.
        use_llm : bool
            If *True* (default), use the OpenAI API to generate rich analysis
            text.  If *False*, use deterministic placeholder text (useful for
            offline testing / CI).
        """
        self._idea = idea
        self._use_llm = use_llm
        self._state: Dict[str, Any] = {}
        self._cumulative_reward: float = 0.0
        self._done: bool = False
        self._steps_taken: int = 0
        self._completed_actions: list[str] = []

    # ------------------------------------------------------------------
    # OpenEnv interface
    # ------------------------------------------------------------------

    def reset(self) -> Dict[str, Any]:
        """Reset the environment to its initial state and return it."""
        self._state = {
            "idea": self._idea,
            "analysis": {
                "problem": "",
                "solution": "",
                "market": "",
            },
        }
        self._cumulative_reward = 0.0
        self._done = False
        self._steps_taken = 0
        self._completed_actions = []
        return copy.deepcopy(self._state)

    def step(self, action: str) -> Tuple[Dict[str, Any], float, bool]:
        """
        Execute *action* in the environment.

        Returns
        -------
        state : dict
            The updated environment state.
        reward : float
            The incremental reward earned by this action.
        done : bool
            Whether the episode is complete (all analyses filled).
        """
        if not self._state:
            raise RuntimeError("Environment not initialised. Call reset() first.")
        if self._done:
            raise RuntimeError("Episode is already done. Call reset() to start a new episode.")
        if action not in VALID_ACTIONS:
            raise ValueError(
                f"Invalid action '{action}'. Valid actions: {VALID_ACTIONS}"
            )
        if action in self._completed_actions:
            raise ValueError(f"Action '{action}' has already been performed in this episode.")

        # Generate analysis content ----------------------------------------
        analysis_key = ANALYSIS_KEY_MAP[action]
        if self._use_llm:
            content = generate_analysis(
                idea=self._idea,
                analysis_type=analysis_key,
                current_state=self._state,
            )
        else:
            content = self._placeholder(analysis_key)

        # Update state ------------------------------------------------------
        self._state["analysis"][analysis_key] = content
        self._steps_taken += 1
        self._completed_actions.append(action)

        # Compute reward ----------------------------------------------------
        reward = REWARD_MAP.get(action, 0.0)
        self._cumulative_reward += reward

        # Check termination -------------------------------------------------
        analysis = self._state["analysis"]
        self._done = all(
            analysis[k] != "" for k in ("problem", "solution", "market")
        )

        return copy.deepcopy(self._state), reward, self._done

    def state(self) -> Dict[str, Any]:
        """Return a deep copy of the current state."""
        if not self._state:
            raise RuntimeError("Environment not initialised. Call reset() first.")
        return copy.deepcopy(self._state)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def cumulative_reward(self) -> float:
        return self._cumulative_reward

    @property
    def completed_actions(self) -> list[str]:
        return list(self._completed_actions)

    @staticmethod
    def _placeholder(analysis_key: str) -> str:
        """Deterministic fallback used when LLM is disabled."""
        placeholders = {
            "problem": (
                "The target users are early-stage startup founders (pre-seed to seed stage) "
                "who lack access to structured market validation. Their specific pain is spending "
                "weeks manually researching competitors, customer segments, and market sizing "
                "using fragmented tools like Google Trends, Crunchbase, and LinkedIn, often "
                "reaching unreliable conclusions. Current alternatives like consulting firms "
                "charge $5K-50K, which most bootstrapped founders cannot afford. Free tools "
                "provide raw data but no synthesis or actionable insight. The problem is real "
                "but the severity depends on how many founders actually change course based "
                "on validation data versus gut instinct. Most founders rely on intuition "
                "regardless of data, which weakens the case for a dedicated validation tool.\n\n"
                "Verdict: Weak problem"
            ),
            "solution": (
                "The solution aggregates publicly available data sources (competitor databases, "
                "job postings, patent filings, funding records) and runs them through a "
                "structured analysis pipeline that outputs a validation report. The practical "
                "limitation is that the quality of the output depends entirely on the quality "
                "of the input idea description. Vague one-line ideas will produce vague analysis. "
                "A real risk is that founders may treat automated output as authoritative when "
                "it should only be a starting point. The solution does address the stated problem "
                "of reducing manual research time, but whether the output is accurate enough to "
                "replace human judgment is unproven. This is essentially a wrapper around existing "
                "LLM capabilities that anyone can replicate with a well-crafted ChatGPT prompt.\n\n"
                "Verdict: Weak solution"
            ),
            "market": (
                "The paying customers would be startup founders and small teams in the idea "
                "validation phase. Globally, roughly 300 million people attempt to start "
                "businesses each year, but only a fraction (estimated 5-10%) would pay for "
                "validation tooling, and even fewer would pay more than $20-50/month. Direct "
                "competitors include Validator AI, IdeaBuddy, and general-purpose tools like "
                "ChatGPT which can perform similar analysis for free. The key risk is customer "
                "retention: founders validate once and leave. There is no recurring need, which "
                "makes a subscription model difficult to sustain. The market exists but is "
                "crowded with free alternatives that are good enough for most users.\n\n"
                "Verdict: Weak market"
            ),
        }
        return placeholders.get(analysis_key, "Analysis complete.")
