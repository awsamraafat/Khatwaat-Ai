import sys
import os
import time
import numpy as np
from datetime import datetime, timezone

# Add the scripts directory to the path so we can import the AI engines
# __file__ is in backend/services/, so dirname x2 gets us to the backend directory
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(root_dir, "scripts"))

from irt_engine import IRTEngine2PL
from models.database import get_supabase_admin


class ExamService:
    """
    Service that bridges FastAPI with the IRT/CAT AI engines.
    Uses Supabase as the persistence layer instead of JSON files.
    """
    
    # In-memory session cache for active exams (maps session_id -> engine state)
    _active_sessions = {}
    
    @staticmethod
    def _load_questions_from_db(subject: str) -> list:
        """Load questions from Supabase for a given subject."""
        supabase = get_supabase_admin()
        # Removed .eq("calibrated", True) so we can use our freshly seeded questions
        result = supabase.table("questions").select("*").eq(
            "subject_name", subject
        ).execute()
        
        if not result.data:
            raise ValueError(f"No questions found for subject '{subject}'")
        
        # Convert DB format to engine format
        questions = []
        for q in result.data:
            questions.append({
                "question_id": q["question_id"],
                "metadata": {
                    "subject": q["subject_name"],
                    "topic": q.get("topic", ""),
                    "skill": q.get("skill", ""),
                    "difficulty": q.get("difficulty", "Medium"),
                    "calibrated": True
                },
                "content": {
                    "question_text": q["question_text"],
                    "question_type": q["question_type"],
                    "options": [
                        {"id": "A", "text": q["option_a"]},
                        {"id": "B", "text": q["option_b"]},
                        {"id": "C", "text": q["option_c"]},
                        {"id": "D", "text": q["option_d"]}
                    ],
                    "correct_answer": q["correct_answer"]
                },
                "irt_parameters": {
                    "a": q["irt_a"],
                    "b": q["irt_b"],
                    "c": q.get("irt_c", 0.25)
                }
            })
        return questions
    
    @classmethod
    def start_exam(cls, user_id: str, subject: str, max_questions: int = 20, target_se: float = 0.3):
        """Initialize a new adaptive exam session."""
        questions = cls._load_questions_from_db(subject)
        
        session_id = f"SESSION_{user_id[:8]}_{int(time.time())}"
        
        # Initialize engine state (in-memory for performance)
        engine_state = {
            "theta": 0.0,
            "questions": {q["question_id"]: q for q in questions},
            "unasked": {q["question_id"]: q for q in questions},
            "history_questions": [],
            "history_responses": [],
            "history_a": [],
            "history_b": [],
            "history_c": [],
            "max_questions": max_questions,
            "target_se": target_se,
            "start_time": time.time(),
            "current_question": None,
            "current_question_start": None,
            "subject": subject,
            "user_id": user_id
        }
        
        cls._active_sessions[session_id] = engine_state
        
        # Save session to DB
        supabase = get_supabase_admin()
        supabase.table("exam_sessions").insert({
            "session_id": session_id,
            "user_id": user_id,
            "subject_name": subject,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "status": "in_progress"
        }).execute()
        
        # Get first question
        first_q = cls._select_next_question(engine_state)
        engine_state["current_question"] = first_q
        engine_state["current_question_start"] = time.time()
        
        return session_id, first_q, len(questions)
    
    @classmethod
    def _select_next_question(cls, state: dict, exposure_pool_size: int = 5):
        """Select the next question using Fisher Information maximization."""
        if not state["unasked"]:
            return None
        
        theta = state["theta"]
        info_scores = []
        
        for qid, q in state["unasked"].items():
            a = q["irt_parameters"]["a"]
            b = q["irt_parameters"]["b"]
            c = q["irt_parameters"].get("c", 0.0)
            p = IRTEngine2PL.probability(theta, a, b, c)
            q_val = 1.0 - p
            
            if c > 0:
                p_star = (p - c) / (1.0 - c)
                info = (a ** 2) * (p_star ** 2) * q_val / max(p, 1e-10)
            else:
                info = (a ** 2) * p * q_val
            
            info_scores.append((info, qid))
        
        info_scores.sort(key=lambda x: x[0], reverse=True)
        
        import random
        top = info_scores[:min(exposure_pool_size, len(info_scores))]
        _, selected_qid = random.choice(top)
        
        return state["unasked"][selected_qid]
    
    @classmethod
    def submit_answer(cls, session_id: str, question_id: str, user_answer: str, time_per_question: int = 60):
        """Submit an answer and update theta."""
        if session_id not in cls._active_sessions:
            raise ValueError("Session not found or expired")
        
        state = cls._active_sessions[session_id]
        
        if state["current_question"] is None or state["current_question"]["question_id"] != question_id:
            raise ValueError("Invalid question submission")
        
        q = state["current_question"]
        a = q["irt_parameters"]["a"]
        b = q["irt_parameters"]["b"]
        c = q["irt_parameters"].get("c", 0.0)
        correct_answer = q["content"]["correct_answer"]
        
        end_time = time.time()
        time_spent = end_time - state["current_question_start"]
        
        # Timeout check
        is_timeout = False
        if time_per_question > 0 and time_spent > time_per_question:
            is_timeout = True
            is_correct = False
        else:
            is_correct = user_answer.strip().upper() == correct_answer.strip().upper()
        
        # Update state
        state["unasked"].pop(question_id, None)
        state["history_questions"].append(question_id)
        state["history_responses"].append(1 if is_correct else 0)
        state["history_a"].append(a)
        state["history_b"].append(b)
        state["history_c"].append(c)
        
        # Update theta
        state["theta"] = float(IRTEngine2PL.estimate_ability(
            np.array(state["history_responses"]),
            np.array(state["history_a"]),
            np.array(state["history_b"]),
            np.array(state["history_c"]),
            initial_theta=state["theta"]
        ))
        
        # Calculate SE
        total_info = sum(
            cls._item_info(state["theta"], aa, bb, cc)
            for aa, bb, cc in zip(state["history_a"], state["history_b"], state["history_c"])
        )
        current_se = 1.0 / np.sqrt(total_info) if total_info > 0 else float('inf')
        
        # Save answer to DB
        supabase = get_supabase_admin()
        db_session = supabase.table("exam_sessions").select("id").eq("session_id", session_id).single().execute()
        
        supabase.table("answers").insert({
            "session_id": db_session.data["id"],
            "question_id": question_id,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "is_timeout": is_timeout,
            "time_spent_seconds": round(time_spent, 2),
            "irt_a": a,
            "irt_b": b,
            "irt_c": c,
            "theta_at_time": round(state["theta"], 4),
            "se_at_time": round(current_se, 4),
            "question_order": len(state["history_questions"])
        }).execute()
        
        # Check if finished
        num_asked = len(state["history_questions"])
        is_finished = False
        finish_reason = None
        
        if num_asked >= state["max_questions"]:
            is_finished = True
            finish_reason = "Max questions reached"
        elif num_asked >= 5 and current_se <= state["target_se"]:
            is_finished = True
            finish_reason = f"Target precision reached (SE: {current_se:.3f})"
        elif not state["unasked"]:
            is_finished = True
            finish_reason = "Bank exhausted"
        
        # Get next question if not finished
        next_question = None
        if not is_finished:
            next_question = cls._select_next_question(state)
            state["current_question"] = next_question
            state["current_question_start"] = time.time()
        else:
            state["current_question"] = None
            try:
                cls.finish_exam(session_id)
            except Exception as e:
                print(f"Error finalizing session {session_id} in submit_answer: {e}")
        
        return {
            "is_correct": is_correct,
            "is_timeout": is_timeout,
            "new_theta": state["theta"],
            "current_se": current_se,
            "is_finished": is_finished,
            "finish_reason": finish_reason,
            "next_question": next_question
        }
    
    @classmethod
    def finish_exam(cls, session_id: str):
        """Finalize an exam session and generate results."""
        if session_id not in cls._active_sessions:
            raise ValueError("Session not found")
        
        state = cls._active_sessions[session_id]
        end_time = time.time()
        
        total_q = len(state["history_questions"])
        correct = sum(state["history_responses"])
        
        total_info = sum(
            cls._item_info(state["theta"], a, b, c)
            for a, b, c in zip(state["history_a"], state["history_b"], state["history_c"])
        )
        final_se = 1.0 / np.sqrt(total_info) if total_info > 0 else float('inf')
        
        # Update DB
        supabase = get_supabase_admin()
        supabase.table("exam_sessions").update({
            "end_time": datetime.now(timezone.utc).isoformat(),
            "final_theta": round(state["theta"], 4),
            "final_se": round(final_se, 4),
            "total_questions": total_q,
            "correct_answers": correct,
            "raw_percentage": round((correct / total_q * 100) if total_q > 0 else 0, 2),
            "status": "completed"
        }).eq("session_id", session_id).execute()
        
        # Update analytics
        cls._update_analytics(state["user_id"], state["subject"], state["theta"], total_q, correct)
        
        result = {
            "session_id": session_id,
            "subject": state["subject"],
            "total_questions": total_q,
            "correct_answers": correct,
            "raw_percentage": round((correct / total_q * 100) if total_q > 0 else 0, 2),
            "final_theta": round(state["theta"], 4),
            "final_se": round(final_se, 4),
            "start_time": datetime.fromtimestamp(state["start_time"], tz=timezone.utc).isoformat(),
            "end_time": datetime.fromtimestamp(end_time, tz=timezone.utc).isoformat(),
            "duration_seconds": round(end_time - state["start_time"], 2)
        }
        
        # Clean up in-memory state
        del cls._active_sessions[session_id]
        
        return result
    
    @staticmethod
    def _item_info(theta, a, b, c=0.0):
        """Calculate Fisher Information for a single item."""
        p = IRTEngine2PL.probability(theta, a, b, c)
        q = 1.0 - p
        if c > 0:
            p_star = (p - c) / (1.0 - c)
            return (a ** 2) * (p_star ** 2) * q / max(p, 1e-10)
        return (a ** 2) * p * q
    
    @staticmethod
    def _update_analytics(user_id: str, subject: str, theta: float, total_q: int, correct: int):
        """Update running analytics for a user's subject performance."""
        try:
            supabase = get_supabase_admin()
            
            # Try to get existing analytics
            existing = supabase.table("analytics").select("*").eq(
                "user_id", user_id
            ).eq("subject_name", subject).execute()
            
            if existing.data:
                record = existing.data[0]
                supabase.table("analytics").update({
                    "latest_theta": round(theta, 4),
                    "total_exams": record["total_exams"] + 1,
                    "total_questions_answered": record["total_questions_answered"] + total_q,
                    "total_correct": record["total_correct"] + correct,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }).eq("id", record["id"]).execute()
            else:
                supabase.table("analytics").insert({
                    "user_id": user_id,
                    "subject_name": subject,
                    "latest_theta": round(theta, 4),
                    "total_exams": 1,
                    "total_questions_answered": total_q,
                    "total_correct": correct
                }).execute()
        except Exception as e:
            print(f"Warning: Failed to update analytics: {e}")
