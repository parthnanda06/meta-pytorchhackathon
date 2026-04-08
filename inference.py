from environment import StartupEnv
from agent import Agent
from grader import grade

def safe_score(score):
    score = float(score)
    if score <= 0.0:
        return 0.01
    if score >= 1.0:
        return 0.99
    return score


def main():
    tasks = [
        {"idea": "AI fitness startup"},
        {"idea": "Food delivery platform"},
        {"idea": "Edtech app for students"}
    ]

    results = []

    for t in tasks:
        env = StartupEnv(idea=t["idea"], use_llm=False)
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
            state, _, done = env.step(action)
            if done:
                break

        score = grade(state)
        score = safe_score(score)

        results.append({
            "task": t["idea"],
            "score": score
        })

    print(results)

if __name__ == "__main__":
    main()
