import sys
import os
import json

from environment import StartupEnv
from agent import Agent
from grader import grade, grade_easy, grade_medium, grade_hard
from tasks import get_all_tasks
from tasks import get_task

def main():
    tasks_list = get_all_tasks()
    results = []

    for task_data in tasks_list:
        idea = task_data['idea']
        
        # Run environment offline (deterministically) 
        env = StartupEnv(idea=idea, use_llm=False)
        state = env.reset()
        
        task_def = get_task(task_data['difficulty'])
        
        # Agent automates the evaluation pipeline based on difficulty constraints
        agent = Agent(allowed_actions=task_def.get("actions"))
        
        while True:
            action = agent.act(state)
            if not action:
                break
            state, reward, done = env.step(action)
            if done:
                break
                
        # Call the specific grader for the task
        if task_data['id'] == "easy":
            score = grade_easy(state)
        elif task_data['id'] == "medium":
            score = grade_medium(state)
        else:
            score = grade_hard(state)
        
        # Strictly clamp between (0, 1) exclusively
        score = max(0.01, min(0.99, score))
        
        results.append({
            "task": task_data['id'],
            "score": round(score, 4)
        })

    # Exactly output pure JSON formatted array for platform regex parsers
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
