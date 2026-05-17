import json
import numpy as np
import random
from irt_engine import IRTEngine2PL

class CATEngine:
    def __init__(self, question_bank_path, subject=None):
        """
        Initialize the CAT Engine with a calibrated question bank.
        Optionally filter by subject.
        """
        with open(question_bank_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Filter for calibrated questions, and optionally by subject
        self.all_questions = []
        for q in data.get("questions", []):
            if not q.get("metadata", {}).get("calibrated", False):
                continue
            if subject and q.get("metadata", {}).get("subject") != subject:
                continue
            self.all_questions.append(q)
            
        if len(self.all_questions) == 0:
            raise ValueError(f"No calibrated questions found for subject '{subject}'.")

        self.reset()

    def reset(self):
        """Resets the exam state for a new student."""
        self.theta = 0.0  # Initial assumed ability
        self.history_questions = [] # List of question_ids asked
        self.history_responses = [] # List of 0s and 1s
        self.history_a = [] # List of discrimination params for asked questions
        self.history_b = [] # List of difficulty params for asked questions
        self.unasked_questions = {q["question_id"]: q for q in self.all_questions}

    def item_information(self, theta, a, b):
        """
        Calculate Fisher Information for a 2PL model.
        I(theta) = a^2 * P(theta) * (1 - P(theta))
        """
        p = IRTEngine2PL.probability(theta, a, b)
        return (a ** 2) * p * (1 - p)

    def get_next_question(self, exposure_pool_size=5):
        """
        Selects the next best question based on Maximum Fisher Information at current theta.
        Applies basic exposure control by selecting randomly from the top `exposure_pool_size` items.
        """
        if not self.unasked_questions:
            return None # No more questions

        info_scores = []
        for qid, q in self.unasked_questions.items():
            a = q["irt_parameters"]["a"]
            b = q["irt_parameters"]["b"]
            info = self.item_information(self.theta, a, b)
            info_scores.append((info, qid))

        # Sort by information descending
        info_scores.sort(key=lambda x: x[0], reverse=True)
        
        # Exposure control: take top N and pick one randomly
        top_candidates = info_scores[:min(exposure_pool_size, len(info_scores))]
        selected_info, selected_qid = random.choice(top_candidates)
        
        return self.unasked_questions[selected_qid]

    def submit_answer(self, question_id, is_correct):
        """
        Records the answer and updates the student's ability estimate (theta).
        """
        if question_id not in self.unasked_questions:
            raise ValueError("Question ID is invalid or already asked.")
            
        q = self.unasked_questions.pop(question_id)
        a = q["irt_parameters"]["a"]
        b = q["irt_parameters"]["b"]
        
        self.history_questions.append(question_id)
        self.history_responses.append(1 if is_correct else 0)
        self.history_a.append(a)
        self.history_b.append(b)
        
        # Update Theta using Maximum Likelihood Estimation
        # We need at least one correct and one incorrect answer for stable MLE,
        # but our estimate_ability function handles edge cases gracefully.
        self.theta = IRTEngine2PL.estimate_ability(
            np.array(self.history_responses),
            np.array(self.history_a),
            np.array(self.history_b),
            initial_theta=self.theta
        )
        
        return self.theta

    def get_standard_error(self):
        """
        Calculates the Standard Error (SE) of the current theta estimate.
        SE = 1 / sqrt(Total Information)
        """
        total_info = sum(self.item_information(self.theta, a, b) 
                         for a, b in zip(self.history_a, self.history_b))
        
        if total_info <= 0:
            return float('inf')
        return 1.0 / np.sqrt(total_info)

    def is_finished(self, max_questions=20, target_se=0.3):
        """
        Checks if stopping criteria are met.
        """
        num_asked = len(self.history_questions)
        if num_asked >= max_questions:
            return True, "Max questions reached"
            
        se = self.get_standard_error()
        if num_asked >= 5 and se <= target_se: # Ensure a minimum of 5 questions are asked
            return True, f"Target precision reached (SE: {se:.3f})"
            
        if len(self.unasked_questions) == 0:
            return True, "Bank exhausted"
            
        return False, "Continue"
