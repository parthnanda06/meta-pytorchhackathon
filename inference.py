import os
from environment import StartupEnv
from grader import grade

def main():
    # Priority to IDEA env var if provided by validator
    idea = os.getenv("IDEA") or "AI fitness startup"

    print("[START]")

    # CRITICAL: enabling LLM for Meta proxy validation
    env = StartupEnv(idea=idea, use_llm=True)
    state = env.reset()

    # Explicitly walk through the required analytical steps
    for action in ["analyze_problem", "analyze_solution", "analyze_market"]:
        print(f"[STEP] {action}")
        state, _, _ = env.step(action)

    score = grade(state)

    # STRICT clamp to (0, 1) exclusively
    if score <= 0:
        score = 0.01
    elif score >= 1:
        score = 0.99

    print(f"SCORE: {score:.4f}")
    print("[END]")

if __name__ == "__main__":
    main()
