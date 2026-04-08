import os
from environment import StartupEnv
from agent import Agent
from grader import grade

def main():
    # If the validator passes an idea via env var or similar, prioritize it
    idea = os.getenv("IDEA") or "AI fitness startup"

    print("[START]")

    # CRITICAL: use_llm=True is required for proxy validation
    env = StartupEnv(idea=idea, use_llm=True)
    agent = Agent(allowed_actions=[
        "analyze_problem",
        "analyze_solution",
        "analyze_market"
    ])

    state = env.reset()

    while True:
        action = agent.act(state)
        if action is None:
            break

        print(f"[STEP] {action}")
        state, _, done = env.step(action)

        if done:
            break

    score = grade(state)

    # STRICT clamp to strictly (0, 1) exclusively
    if score <= 0:
        score = 0.01
    elif score >= 1:
        score = 0.99

    print(f"SCORE: {score:.4f}")
    print("[END]")

if __name__ == "__main__":
    main()
