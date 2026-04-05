#!/usr/bin/env python3
"""
run.py — Entry point for the Startup Idea Validator environment.

Usage:
    python run.py --difficulty easy
    python run.py --difficulty medium
    python run.py --difficulty hard
    python run.py --difficulty hard --no-llm          # offline mode
    python run.py --difficulty hard --llm-grade        # include LLM grading
    python run.py --idea "My custom startup idea"
"""

from __future__ import annotations

import argparse
import io
import json
import sys

# Ensure UTF-8 output on Windows terminals
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()  # loads OPENAI_API_KEY from .env

from env.environment import StartupEnv
from agent.agent import Agent
from grader.grader import grade, grade_with_llm
from tasks.tasks import get_task


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

DEFAULT_IDEA = (
    "An AI-powered platform that helps early-stage founders validate their "
    "startup ideas by analysing market data, competitor landscape, and customer "
    "pain points in real-time."
)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Startup Idea Validator environment."
    )
    parser.add_argument(
        "--difficulty",
        type=str,
        choices=["easy", "medium", "hard"],
        default="hard",
        help="Task difficulty level (default: hard).",
    )
    parser.add_argument(
        "--idea",
        type=str,
        default=DEFAULT_IDEA,
        help="The startup idea to evaluate.",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM calls and use deterministic placeholders.",
    )
    parser.add_argument(
        "--llm-grade",
        action="store_true",
        help="Also run LLM-based grading (requires OPENAI_API_KEY).",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    args = parse_args()

    # 1. Load task ----------------------------------------------------------
    task = get_task(args.difficulty)
    print("=" * 72)
    print(f"  STARTUP IDEA VALIDATOR  --  Difficulty: {args.difficulty.upper()}")
    print("=" * 72)
    print(f"\n[IDEA]   {args.idea}")
    print(f"[TASK]   {task['description']}")
    print(f"[TARGET] Max reward: {task['max_reward']}")
    print(f"[MODE]   LLM: {'enabled' if not args.no_llm else 'disabled (placeholders)'}")
    print()

    # 2. Initialise environment & agent ------------------------------------
    env = StartupEnv(idea=args.idea, use_llm=not args.no_llm)
    agent = Agent(allowed_actions=task["actions"])

    # 3. Run episode -------------------------------------------------------
    state = env.reset()
    total_reward = 0.0
    step_num = 0

    while True:
        action = agent.act(state)
        if action is None:
            break

        step_num += 1
        print(f"--- Step {step_num}: {action} ---")
        state, reward, done = env.step(action)
        total_reward += reward
        print(f"  [OK] Reward: +{reward}  |  Cumulative: {total_reward}")

        # Show a snippet of the analysis
        key = action.replace("analyze_", "")
        snippet = state["analysis"][key][:120].replace("\n", " ")
        print(f"  [{key.upper()}] {snippet}...")
        print()

        if done:
            break

    # 4. Grade --------------------------------------------------------------
    print("=" * 72)
    print("  RESULTS")
    print("=" * 72)

    rule_score = grade(state)
    print(f"\n[SCORE]  Rule-based : {rule_score:.4f}")
    print(f"[REWARD] Cumulative : {total_reward}")

    if args.llm_grade:
        print("\n[LLM]   Running LLM-based grading...")
        llm_result = grade_with_llm(state)
        print(f"[SCORE]  Problem  : {llm_result['problem']}/0.3")
        print(f"[SCORE]  Solution : {llm_result['solution']}/0.3")
        print(f"[SCORE]  Market   : {llm_result['market']}/0.4")
        print(f"[SCORE]  Final    : {llm_result['final']}")

    # 5. Full state dump ----------------------------------------------------
    print("\n" + "-" * 72)
    print("  FINAL STATE")
    print("-" * 72)
    print(json.dumps(state, indent=2, ensure_ascii=False))
    print()


if __name__ == "__main__":
    main()
