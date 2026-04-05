# 🚀 Startup Idea Validator (OpenEnv AI Environment)

An OpenEnv-compliant AI environment for step-based evaluation of startup ideas using structured reasoning and automated grading.

---

## 🧠 Overview

This project simulates a real-world startup evaluation pipeline where an AI agent analyzes a given idea across three key dimensions:

* Problem Clarity
* Solution Feasibility
* Market Viability

The system follows an **RL-inspired environment design** using step-based interactions, reward signals, and deterministic evaluation.

---

## ⚙️ Key Features

* ✅ OpenEnv-compliant environment (`reset`, `step`, `state`)
* ✅ Step-based execution (Problem → Solution → Market)
* ✅ Deterministic agent behavior
* ✅ Automated grading system (0.0 – 1.0 score)
* ✅ Difficulty levels (Easy / Medium / Hard)
* ✅ Structured logging (machine-readable)
* ✅ Reproducible inference pipeline

---

## 🧩 Environment Design

### 🔹 Actions

* `analyze_problem`
* `analyze_solution`
* `analyze_market`

### 🔹 Observations (State)

```json
{
  "idea": "string",
  "analysis": {
    "problem": "string",
    "solution": "string",
    "market": "string"
  }
}
```

---

## 🎯 Reward Function

| Step              | Max Reward |
| ----------------- | ---------- |
| Problem Analysis  | 0.3        |
| Solution Analysis | 0.3        |
| Market Analysis   | 0.4        |

* Rewards are **incremental and cumulative**
* Total reward ranges from **0.0 to 1.0**

---

## 📊 Difficulty Levels

| Level  | Behavior                                      |
| ------ | --------------------------------------------- |
| Easy   | Analyze only problem                          |
| Medium | Analyze problem + solution                    |
| Hard   | Full evaluation (problem + solution + market) |

---

## 🔎 Logging Format

The system outputs **strict machine-readable logs**:

```text
START
STEP: analyze_problem
STEP: analyze_solution
STEP: analyze_market
END
SCORE: 0.72
```

* `START` → beginning of evaluation
* `STEP` → each agent action
* `END` → completion of steps
* `SCORE` → final evaluation result

---

## 🧪 Hackathon Inference Entry

Run using the required inference script:

```bash
python inference.py --difficulty hard --idea "AI startup validator for founders"
```

---

## ⚙️ Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 2. Set environment variables

Create a `.env` file:

```bash
OPENAI_API_KEY=your_api_key_here
API_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini
```

---

## 🐳 Docker Support

```bash
docker build -t startup-validator .
docker run startup-validator
```

---

## 📦 Project Structure

```bash
startup-env/
│
├── backend/
│   ├── env/
│   ├── agent/
│   ├── grader/
│   ├── tasks/
│   └── llm/
│
├── inference.py
├── openenv.yaml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## ⚠️ Important Notes

* This is NOT a chatbot
* Uses structured step-based reasoning
* Fully deterministic (`temperature = 0`)
* Designed for automated evaluation systems

---

## 🚀 Example Use Cases

* Startup validation tools
* Investor decision systems
* Product idea screening
* AI-based evaluation pipelines

---

## 👨‍💻 Author

Parth Bhanushali
Computer Science (AI Specialization)
