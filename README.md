# 🧠 AI-Powered Adaptive Assessment Engine (CAT + IRT)

A state-of-the-art, production-ready **AI-Driven Computerized Adaptive Testing (CAT)** engine powered by **Item Response Theory (IRT)** under the 2-Parameter Logistic (2PL) model. 

This system acts as a probabilistic AI agent that models student cognitive ability ($\theta$) dynamically in real-time, executing optimal question selection using concepts equivalent to **Active Learning** (Information Maximization) to reduce test length by up to 50% while maintaining absolute measurement precision.

---

## 🌟 Key Architecture & AI Concepts

The system mathematically treats adaptive testing as an active search and estimation problem across two primary phases:

### 1. The Probabilistic IRT Core (`irt_engine.py`)
This is the machine learning and parameter estimation layer of the system:
* **The 2PL Probabilistic Model**: Computes the probability of a correct response based on student ability ($\theta$), item difficulty ($b$), and item discrimination ($a$):
  $$P(\theta) = \frac{1}{1 + e^{-a(\theta - b)}}$$
* **State Estimation (MLE)**: Solves for the student's true latent ability ($\theta$) in real-time using **Maximum Likelihood Estimation** via non-linear optimization (`scipy.optimize` with BFGS solver).
* **Model Training / Calibration (JMLE)**: Learns both item difficulty and discrimination parameters simultaneously from student response matrices using iterative **Joint Maximum Likelihood Estimation (JMLE)**, recentering difficulty parameters to solve the scale identifiability problem.

### 2. Active Learning CAT Engine (`cat_engine.py`)
This is the decision-making agent that guides the live adaptive test session:
* **Fisher Information Maximization**: Implements an **Active Learning** query strategy. It calculates the Fisher Information for all unasked items at the current estimated $\theta$ and queries the item that maximizes the information gain:
  $$I(\theta) = a^2 \cdot P(\theta) \cdot (1 - P(\theta))$$
* **Exposure Control**: Implements a "Randomesque" exposure control policy to introduce stochasticity into the item selection pool, preventing exam security leaks.
* **Stop Criteria Precision Enforcer**: Evaluates measurement Standard Error ($SE = 1/\sqrt{\text{Total Info}}$) to stop the test early once a target confidence interval is achieved.

### 3. Session State Manager (`session_manager.py`)
The state controller wrapping the AI engine. It tracks start times, per-question thinking durations, enforces timeout bounds, manages session states, and exports comprehensive, secure **JSON Exam Receipts**.

---

## 📁 Repository & File Structure

```bash
├── data/
│   ├── raw/                       # Raw input CSV question banks & simulated response datasets
│   ├── processed/                 # Preprocessed & calibrated JSON question banks
│   └── sessions/                  # Secure JSON adaptive test session receipts
│
├── scripts/
│   ├── irt_engine.py              # Mathematical optimization models (MLE, JMLE)
│   ├── cat_engine.py              # Active Learning Fisher Information selection logic
│   ├── session_manager.py         # Stateful exam controller & JSON receipt generator
│   │
│   ├── pipeline.py                # Preprocesses, cleans, and deduplicates raw CSV items
│   ├── simulate_data.py           # Simulates response matrices for model training
│   ├── calibrate_items.py         # Trains the 2PL IRT model parameters using JMLE
│   ├── score_students.py          # Estimates ability rankings for response matrices
│   │
│   ├── run_cat_simulation.py      # Interactive terminal simulator (Live Demo Client)
│   ├── run_session_test.py        # Automated backend integration testing script
│   ├── verify_all.py              # End-to-end system testing verification suite
│   └── analyze.py                 # Primary data analysis script
│
├── requirements.txt               # Scientific Python libraries (numpy, scipy, pandas)
└── .gitignore                     # Git configuration ignoring temporary outputs
```

---

## ⚙️ Quick Start & Demonstrations

### 1. Install Dependencies
Ensure you have the required optimization and data manipulation packages installed:
```bash
pip install -r requirements.txt
```

### 2. Run the Full E2E Verification Suite
Run the automated pipeline, simulator, calibrator, and session tester in one click to verify everything is 100% operational:
```bash
python scripts/verify_all.py
```

### 3. Take a Live Interactive Adaptive Exam (Presentation Demo 🚀)
Demonstrate the AI's real-time adaptability to your examiners:
```bash
python scripts/run_cat_simulation.py
```
* **How to demonstrate**: Choose a subject (e.g., `MATH`, `ARABIC`). Answer a few questions correctly, and point out how the AI increases the estimated ability ($\theta$) and serves **harder** questions. Then, intentionally answer incorrectly, and watch the AI seamlessly adapt by providing **easier** questions.

---

## 🔌 API Integration & Production Readiness

This engine is strictly decoupled from framework dependencies. It can be easily integrated into any web API (FastAPI, Flask, Django, Node.js, etc.) to power high-concurrency production platforms:

```python
from scripts.session_manager import ExamSession

# 1. Initialize session when student begins the exam
session = ExamSession(student_id="STUDENT_99", bank_path="data/processed/calibrated_question_bank.json", subject="MATH")
session.start_exam()

# 2. Retrieve the optimal active-learning question to send to the UI
question = session.get_next_question()

# 3. Submit user answer, calculate response speed, and update theta dynamically
is_correct, is_timeout, new_theta = session.submit_answer(question_id="M015", user_answer="C")

# 4. Check stopping criteria in real-time
finished, reason = session.is_finished(max_questions=15, target_se=0.3)
if finished:
    receipt = session.finish_exam()
    # Save the receipt JSON to your primary database!
```
