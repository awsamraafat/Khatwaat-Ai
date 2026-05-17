import time
import json
import os
from datetime import datetime
from cat_engine import CATEngine

class ExamSession:
    def __init__(self, student_id, bank_path, subject=None, max_time_per_question=60):
        """
        Initializes an Exam Session Manager.
        """
        self.student_id = student_id
        self.subject = subject
        self.max_time_per_question = max_time_per_question
        
        # Initialize CAT engine
        self.engine = CATEngine(bank_path, subject)
        
        # Session State
        self.session_id = f"SESSION_{student_id}_{int(time.time())}"
        self.start_time = None
        self.end_time = None
        self.current_question = None
        self.current_question_start_time = None
        
        # Detailed Tracking
        self.responses_log = []

    def start_exam(self):
        """Starts the exam session timer."""
        self.start_time = time.time()
        print(f"Exam Session {self.session_id} started for {self.student_id}.")

    def get_next_question(self):
        """
        Retrieves the next adaptive question and starts its timer.
        """
        if self.start_time is None:
            raise RuntimeError("Exam has not been started. Call start_exam() first.")
            
        q = self.engine.get_next_question()
        if q:
            self.current_question = q
            self.current_question_start_time = time.time()
        else:
            self.current_question = None
            self.current_question_start_time = None
            
        return self.current_question

    def submit_answer(self, question_id, user_answer):
        """
        Records the answer, calculates time spent, checks correctness, 
        and updates the CAT engine. Handles timeouts if applicable.
        """
        if self.current_question is None or self.current_question["question_id"] != question_id:
            raise ValueError("Invalid question submission.")
            
        end_time = time.time()
        time_spent = end_time - self.current_question_start_time
        
        correct_answer = self.current_question['content']['correct_answer']
        
        # Enforce time limit
        is_timeout = False
        if self.max_time_per_question > 0 and time_spent > self.max_time_per_question:
            is_timeout = True
            is_correct = False
        else:
            is_correct = (user_answer.strip().upper() == correct_answer.strip().upper())
            
        # Update underlying CAT Engine
        updated_theta = self.engine.submit_answer(question_id, is_correct)
        
        # Log detailed data
        log_entry = {
            "question_id": question_id,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "is_timeout": is_timeout,
            "time_spent_seconds": round(time_spent, 2),
            "irt_difficulty_b": self.current_question['irt_parameters']['b'],
            "irt_discrimination_a": self.current_question['irt_parameters']['a'],
            "new_theta_estimate": round(updated_theta, 4),
            "current_se": round(self.engine.get_standard_error(), 4)
        }
        self.responses_log.append(log_entry)
        
        self.current_question = None
        self.current_question_start_time = None
        
        return is_correct, is_timeout, updated_theta

    def is_finished(self, max_questions=15, target_se=0.3):
        """Wrapper for CAT engine's stopping criteria."""
        return self.engine.is_finished(max_questions, target_se)

    def finish_exam(self, export_dir="data/sessions"):
        """
        Ends the exam session, calculates total duration, and exports a JSON receipt.
        """
        self.end_time = time.time()
        total_duration = self.end_time - self.start_time
        
        # Prevent zero division and ensure sensible metrics
        total_questions = len(self.responses_log)
        correct_count = sum(1 for r in self.responses_log if r["is_correct"])
        
        receipt = {
            "session_id": self.session_id,
            "student_id": self.student_id,
            "subject": self.subject,
            "start_time_iso": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time_iso": datetime.fromtimestamp(self.end_time).isoformat(),
            "total_duration_seconds": round(total_duration, 2),
            "max_time_per_question_enforced": self.max_time_per_question,
            "final_metrics": {
                "total_questions_answered": total_questions,
                "correct_answers": correct_count,
                "raw_percentage": round((correct_count / total_questions * 100) if total_questions > 0 else 0, 2),
                "final_theta": round(self.engine.theta, 4),
                "final_standard_error": round(self.engine.get_standard_error(), 4)
            },
            "responses": self.responses_log
        }
        
        # Ensure directory exists
        base_path = os.path.dirname(os.path.abspath(__file__))
        target_dir = os.path.join(os.path.dirname(base_path), export_dir)
        os.makedirs(target_dir, exist_ok=True)
        
        file_path = os.path.join(target_dir, f"{self.session_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(receipt, f, ensure_ascii=False, indent=4)
            
        print(f"Exam Session completed. Receipt saved to: {file_path}")
        return receipt
