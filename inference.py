import json
from backend.environment import StartupEnv
from backend.agent import Agent
from backend.grader import grade


def safe_score(score):
    try:
        score = float(score)
    except:
        return 0.5
    if score <= 0.0:
        return 0.05
    if score >= 1.0:
        return 0.95
    return max(0.05, min(0.95, score))


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

    while True:
        action = agent.act(state)
        if action is None:
            break

        print(f"[STEP] {action}")
        state, _, done = env.step(action)

        if done:
            break

    score = grade(state)
    score = safe_score(score)

    print(f"SCORE: {score:.4f}")
    print("[END]")

    return score


def main():
    tasks = [
        "AI fitness startup",
        "Food delivery platform",
        "Edtech app for students"
    ]

    results = []

    for idea in tasks:
        score = run_single_task(idea)
        results.append({
            "task": idea,
            "score": score
        })

    # Keep the JSON summary at the very end as well, just in case.
    # print(json.dumps(results))


if __name__ == "__main__":
    main()