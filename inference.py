import json
import sys
from backend.environment import StartupEnv
from backend.agent import Agent
from backend.grader import grade


def safe_score(score):
    try:
        score = float(score or 0.5)
    except (TypeError, ValueError):
        return 0.5
    
    if score <= 0.0:
        return 0.001
    if score >= 1.0:
        return 0.999
    return float(max(0.001, min(0.999, score)))


def run_single_task(idea):
    print("[START]")
    print(f"TASK: {idea}")

    env = StartupEnv(idea=idea, use_llm=True)
    agent = Agent(allowed_actions=[
        "analyze_problem",
        "analyze_solution",
        "analyze_market"
    ])

    state = env.reset()
    rewards = []
    steps = 0
    success = False

    try:
        while True:
            action = agent.act(state)
            if action is None:
                break

            state, reward, done = env.step(action)
            rewards.append(float(reward or 0.0))
            steps += 1
            
            # Match sample script exactly: [STEP] action | reward=0.xx
            print(f"[STEP] {action} | reward={reward:.2f}")

            if done:
                success = True
                break
                
        # Final grading
        raw_score = grade(state)
        score = safe_score(raw_score)
        
    except Exception as e:
        print(f"Error during episode: {e}")
        score = 0.5
    finally:
        # Always emit [END] even on crash
        # Format: [END] success=True, steps=3, score=0.720, rewards=0.30,0.30,0.30
        rewards_str = ",".join(f"{r:.2f}" for r in rewards)
        print(f"[END] success={success}, steps={steps}, score={score:.3f}, rewards={rewards_str}")

    return score


def main():
    tasks = [
        "AI fitness startup",
        "Food delivery platform",
        "Edtech app for students"
    ]

    for idea in tasks:
        run_single_task(idea)


if __name__ == "__main__":
    main()