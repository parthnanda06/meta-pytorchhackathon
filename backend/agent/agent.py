"""
Deterministic agent for the StartupEnv.

The agent inspects the current state and selects the next required action
in a fixed order:  problem → solution → market.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


# Fixed action ordering — deterministic pipeline.
ACTION_SEQUENCE: List[str] = [
    "analyze_problem",
    "analyze_solution",
    "analyze_market",
]

ANALYSIS_KEY_MAP: Dict[str, str] = {
    "analyze_problem": "problem",
    "analyze_solution": "solution",
    "analyze_market": "market",
}


class Agent:
    """
    A deterministic agent that selects the next action based on missing
    parts of the environment state.

    The action order is always: ``analyze_problem`` → ``analyze_solution``
    → ``analyze_market``.
    """

    def __init__(self, allowed_actions: Optional[List[str]] = None) -> None:
        """
        Parameters
        ----------
        allowed_actions : list[str] | None
            Subset of actions the agent is allowed to take (set by the task).
            If ``None``, all actions are allowed.
        """
        if allowed_actions is not None:
            self._sequence = [a for a in ACTION_SEQUENCE if a in allowed_actions]
        else:
            self._sequence = list(ACTION_SEQUENCE)

    def act(self, state: Dict[str, Any]) -> Optional[str]:
        """
        Given the current environment state, return the next action to take.

        Returns ``None`` if all allowed analyses are already complete.
        """
        analysis = state.get("analysis", {})
        for action in self._sequence:
            key = ANALYSIS_KEY_MAP[action]
            if not analysis.get(key):  # empty string or missing
                return action
        return None

    def run_episode(self, env) -> Dict[str, Any]:
        """
        Convenience method: run a full episode from reset to done.

        Returns
        -------
        dict
            ``{"final_state": ..., "cumulative_reward": ..., "steps": ...}``
        """
        state = env.reset()
        total_reward = 0.0
        steps = 0

        while True:
            action = self.act(state)
            if action is None:
                break
            state, reward, done = env.step(action)
            total_reward += reward
            steps += 1
            if done:
                break

        return {
            "final_state": state,
            "cumulative_reward": total_reward,
            "steps": steps,
        }
