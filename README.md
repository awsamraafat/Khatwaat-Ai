# Question Bank & Adaptive Exam System (CAT + IRT)

A production-ready, highly modular Computerized Adaptive Testing (CAT) engine powered by Item Response Theory (IRT) under the 2-Parameter Logistic (2PL) model.

## Overview

This repository provides a complete pipeline to convert raw exam questions into a calibrated, adaptive testing platform. It uses sophisticated mathematical models to measure a student's true ability ($\theta$) dynamically, adapting the difficulty of the questions in real-time to minimize exam duration and maximize precision.

### Key Components

1. **IRT Engine (`irt_engine.py`)**: The mathematical core. Uses Maximum Likelihood Estimation (MLE) to estimate student ability, and Joint Maximum Likelihood Estimation (JMLE) via `scipy.optimize` to calibrate question difficulty ($b$) and discrimination ($a$).
2. **CAT Engine (`cat_engine.py`)**: The adaptive logic. Uses Maximum Fisher Information to select the optimal next question for a student. Implements "Randomesque" exposure control to prevent the exact same sequence of questions from appearing for every student.
3. **Session Manager (`session_manager.py`)**: The exam controller. Wraps the CAT engine to manage exam state, track per-question time spent, enforce hard timeouts, and generate a detailed JSON receipt upon exam completion.

## Is this Production-Ready?

**Yes.** The system is highly modular and strictly decoupled. It does not force you into a specific web framework or database. 

If you are a backend developer (using Django, FastAPI, Flask, Node.js via child processes, etc.), you can simply import the `ExamSession` manager to power your backend endpoints:

```python
from scripts.session_manager import ExamSession

# 1. Initialize session when student clicks "Start Exam"
session = ExamSession(student_id="USER_123", bank_path="data/processed/calibrated_question_bank.json", subject="MATH")
session.start_exam()

# 2. Get the first question to send to the frontend
question = session.get_next_question()

# 3. When frontend submits an answer
is_correct, is_timeout, new_theta = session.submit_answer(question_id="Q_55", user_answer="A")

# 4. Check if exam should end
finished, reason = session.is_finished(max_questions=15, target_se=0.3)
if finished:
    receipt = session.finish_exam()
    # Save 'receipt' JSON to your database!
```

## Quick Start & Testing

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Interactive CAT Simulator**:
   Take a test as a student in your terminal to see the adaptive logic in action.
   ```bash
   python scripts/run_cat_simulation.py
   ```

3. **Run the Automated Session Test**:
   Simulates a full exam session in the background and generates a JSON receipt in the `data/sessions/` folder.
   ```bash
   python scripts/run_session_test.py
   ```

## Repository Structure

- `data/raw/`: Store raw CSV question banks here.
- `data/processed/`: The cleaned and calibrated JSON question banks.
- `data/sessions/`: Auto-generated exam receipts will be saved here.
- `scripts/`: All core engine scripts and testing simulators.
