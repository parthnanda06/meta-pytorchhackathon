"""
Task definitions for the StartupEnv.

Difficulty levels control which analysis actions the agent must perform:

    - easy:   problem only                  (max reward 0.3)
    - medium: problem + solution            (max reward 0.6)
    - hard:   problem + solution + market   (max reward 1.0)
"""

from __future__ import annotations

from typing import Any, Dict, List


TASK_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "easy": {
        "description": "Analyze the problem space only.",
        "actions": ["analyze_problem"],
        "max_reward": 0.3,
        "graders": ["rule_based"],
    },
    "medium": {
        "description": "Analyze the problem space and proposed solution.",
        "actions": ["analyze_problem", "analyze_solution"],
        "max_reward": 0.6,
        "graders": ["rule_based"],
    },
    "hard": {
        "description": "Full pipeline: problem, solution, and market analysis.",
        "actions": ["analyze_problem", "analyze_solution", "analyze_market"],
        "max_reward": 0.9,
        "graders": ["rule_based"],
    },
}


def get_task(difficulty: str) -> Dict[str, Any]:
    """
    Return the task definition for the given difficulty level.

    Parameters
    ----------
    difficulty : str
        One of ``"easy"``, ``"medium"``, ``"hard"``.

    Returns
    -------
    dict
        Keys: ``description``, ``actions`` (list[str]), ``max_reward`` (float).

    Raises
    ------
    ValueError
        If *difficulty* is not a recognised level.
    """
    difficulty = difficulty.lower().strip()
    if difficulty not in TASK_DEFINITIONS:
        valid = ", ".join(TASK_DEFINITIONS.keys())
        raise ValueError(f"Unknown difficulty '{difficulty}'. Choose from: {valid}")
    return TASK_DEFINITIONS[difficulty]

def get_all_tasks() -> List[Dict[str, Any]]:
    """
    Return a list of diverse startup ideas as required for the evaluation pipeline.
    """
    return [
        {
            "id": "easy",
            "idea": "An AI-powered SaaS platform that helps local bakeries predict daily demand for perishable goods using weather and local event data.",
            "difficulty": "easy"
        },
        {
            "id": "medium",
            "idea": "A mobile application that tracks user's carbon footprint based on their bank transactions and offers marketplace rewards for sustainable purchases.",
            "difficulty": "medium"
        },
        {
            "id": "hard",
            "idea": "A hardware startup building autonomous micro-drones for evaluating roof damage after severe storms, marketed directly to local insurance claim adjusters.",
            "difficulty": "hard"
        }
    ]
