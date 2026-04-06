#!/usr/bin/env python3
"""
inference.py — Hackathon compliant entry point.
"""
from __future__ import annotations
import argparse
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# We need to import from the backend module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from env.environment import StartupEnv
from agent.agent import Agent
from tasks.tasks import get_task
from grader.grader import grade

DEFAULT_IDEA = "A startup idea."

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--difficulty", type=str, default="hard")
    parser.add_argument("--idea", type=str, default=DEFAULT_IDEA)
    parser.add_argument("--no-llm", action="store_true")
    return parser.parse_args()

def main() -> None:
    try:
        args = parse_args()
        task = get_task(args.difficulty)
        
        env = StartupEnv(idea=args.idea, use_llm=not args.no_llm)
        agent = Agent(allowed_actions=task["actions"])
        
        state = env.reset()
        
        print("[START]")
        while True:
            action = agent.act(state)
            if action is None:
                break
            
            print(f"[STEP] {action}")
            state, reward, done = env.step(action)
            if done:
                break
                
        score = grade(state)
        print(f"SCORE: {score:.4f}")
        print("[END]")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        print("[END]")
        sys.exit(1)

if __name__ == "__main__":
    main()
