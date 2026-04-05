"""
app.py — Flask web server for the Startup Idea Validator.

Provides a rich browser UI to interact with the OpenEnv environment.
"""

from __future__ import annotations

import json
import os
from flask import Flask, render_template, request, jsonify

from dotenv import load_dotenv
load_dotenv()

from env.environment import StartupEnv
from agent.agent import Agent
from grader.grader import grade, grade_with_llm
from tasks.tasks import get_task

app = Flask(__name__, template_folder='../frontend', static_folder='../frontend')

# Store active sessions in memory (for simplicity)
sessions: dict = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/start", methods=["POST"])
def start_session():
    """Initialize a new environment session."""
    data = request.get_json()
    idea = data.get("idea", "").strip()
    difficulty = data.get("difficulty", "hard").lower()
    use_llm = data.get("use_llm", False)

    if not idea:
        return jsonify({"error": "Please provide a startup idea."}), 400

    try:
        task = get_task(difficulty)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Check if LLM is available
    has_api_key = bool(os.environ.get("OPENAI_API_KEY"))
    if use_llm and not has_api_key:
        use_llm = False

    env = StartupEnv(idea=idea, use_llm=use_llm)
    state = env.reset()
    agent = Agent(allowed_actions=task["actions"])

    session_id = str(id(env))
    sessions[session_id] = {
        "env": env,
        "agent": agent,
        "task": task,
        "steps": [],
        "total_reward": 0.0,
        "use_llm": use_llm,
    }

    return jsonify({
        "session_id": session_id,
        "state": state,
        "task": {
            "description": task["description"],
            "actions": task["actions"],
            "max_reward": task["max_reward"],
        },
        "has_api_key": has_api_key,
        "use_llm": use_llm,
        "next_action": agent.act(state),
    })


@app.route("/api/step", methods=["POST"])
def run_step():
    """Execute the next action in the environment."""
    data = request.get_json()
    session_id = data.get("session_id")

    if session_id not in sessions:
        return jsonify({"error": "Session not found. Please start a new session."}), 404

    session = sessions[session_id]
    env = session["env"]
    agent = session["agent"]

    action = agent.act(env.state())
    if action is None:
        return jsonify({"error": "All steps are already complete."}), 400

    try:
        state, reward, done = env.step(action)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    session["total_reward"] += reward
    step_info = {
        "action": action,
        "reward": reward,
        "cumulative_reward": session["total_reward"],
        "analysis_key": action.replace("analyze_", ""),
        "analysis_text": state["analysis"][action.replace("analyze_", "")],
    }
    session["steps"].append(step_info)

    next_action = agent.act(state)

    result = {
        "step": step_info,
        "state": state,
        "done": done,
        "next_action": next_action,
        "total_reward": session["total_reward"],
    }

    # If done, compute grades
    if done or next_action is None:
        result["rule_score"] = grade(state)
        result["done"] = True

    return jsonify(result)


@app.route("/api/grade_llm", methods=["POST"])
def run_llm_grade():
    """Run optional LLM-based grading."""
    data = request.get_json()
    session_id = data.get("session_id")

    if session_id not in sessions:
        return jsonify({"error": "Session not found."}), 404

    session = sessions[session_id]
    env = session["env"]

    try:
        result = grade_with_llm(env.state())
        return jsonify({"llm_grade": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
