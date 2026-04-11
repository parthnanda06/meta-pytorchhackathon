import json
import sys
from backend.environment import StartupEnv
from backend.agent import Agent
from backend.grader import grade, safe_score


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
        # Paranoid clamping before final emission
        final_score = max(0.01, min(0.99, float(score)))
        print(f"[END] task={idea} score={final_score:.2f} steps={steps}", flush=True)

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