from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ============ AUTH ============
class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=6)
    full_name: str
    role: str = "student"

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    user_id: str
    email: str
    role: str
    full_name: Optional[str] = None


# ============ EXAM ============
class StartExamRequest(BaseModel):
    subject: str
    max_questions: int = 20
    target_se: float = 0.3

class SubmitAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    user_answer: str

class QuestionResponse(BaseModel):
    question_id: str
    question_text: str
    question_type: str
    options: List[dict]
    difficulty_label: str
    irt_b: float
    subject: str

class ExamStartResponse(BaseModel):
    session_id: str
    subject: str
    first_question: QuestionResponse
    total_available: int

class AnswerResponse(BaseModel):
    is_correct: bool
    is_timeout: bool
    new_theta: float
    current_se: float
    is_finished: bool
    finish_reason: Optional[str] = None
    next_question: Optional[QuestionResponse] = None

class ExamResultResponse(BaseModel):
    session_id: str
    subject: str
    total_questions: int
    correct_answers: int
    raw_percentage: float
    final_theta: float
    final_se: float
    start_time: str
    end_time: str
    duration_seconds: float
    responses: List[dict]


# ============ ANALYTICS ============
class StudentAnalyticsResponse(BaseModel):
    user_id: str
    subjects: List[dict]
    overall_theta: Optional[float] = None
    total_exams: int = 0
    strengths: List[str] = []
    weaknesses: List[str] = []

class AdminAnalyticsResponse(BaseModel):
    total_students: int
    total_exams: int
    total_questions: int
    hardest_questions: List[dict]
    easiest_questions: List[dict]
    top_students: List[dict]
    cheating_alerts: List[dict]


# ============ ANTI-CHEAT ============
class AntiCheatEvent(BaseModel):
    session_id: str
    event_type: str  # tab_switch, copy_paste, fullscreen_exit, etc.
    event_data: dict = {}


# ============ RECOMMENDATIONS ============
class RecommendationResponse(BaseModel):
    short_term: List[dict]
    long_term: List[dict]
    predicted_track: Optional[str] = None
    track_confidence: Optional[float] = None
