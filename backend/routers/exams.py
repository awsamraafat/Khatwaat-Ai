from fastapi import APIRouter, Depends, HTTPException
from models.schemas import (
    StartExamRequest, SubmitAnswerRequest, QuestionResponse,
    ExamStartResponse, AnswerResponse, ExamResultResponse
)
from middleware.auth_middleware import get_current_user
from services.exam_service import ExamService

router = APIRouter(prefix="/exam", tags=["Exams"])


def _format_question(q: dict) -> QuestionResponse:
    """Format a question dict for API response (strips correct_answer for security)."""
    if q is None:
        return None
    
    difficulty_b = q["irt_parameters"]["b"]
    if difficulty_b < -1:
        label = "Easy"
    elif difficulty_b < 1:
        label = "Medium"
    else:
        label = "Hard"
    
    return QuestionResponse(
        question_id=q["question_id"],
        question_text=q["content"]["question_text"],
        question_type=q["content"]["question_type"],
        options=q["content"]["options"],
        difficulty_label=label,
        irt_b=round(difficulty_b, 2),
        subject=q["metadata"]["subject"]
    )


@router.post("/start", response_model=ExamStartResponse)
async def start_exam(req: StartExamRequest, user: dict = Depends(get_current_user)):
    """Start a new adaptive exam session."""
    try:
        session_id, first_q, total = ExamService.start_exam(
            user_id=user["id"],
            subject=req.subject.upper(),
            max_questions=req.max_questions,
            target_se=req.target_se
        )
        
        return ExamStartResponse(
            session_id=session_id,
            subject=req.subject.upper(),
            first_question=_format_question(first_q),
            total_available=total
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer", response_model=AnswerResponse)
async def submit_answer(req: SubmitAnswerRequest, user: dict = Depends(get_current_user)):
    """Submit an answer to the current question."""
    try:
        result = ExamService.submit_answer(
            session_id=req.session_id,
            question_id=req.question_id,
            user_answer=req.user_answer
        )
        
        next_q = _format_question(result["next_question"]) if result["next_question"] else None
        
        return AnswerResponse(
            is_correct=result["is_correct"],
            is_timeout=result["is_timeout"],
            new_theta=round(result["new_theta"], 4),
            current_se=round(result["current_se"], 4),
            is_finished=result["is_finished"],
            finish_reason=result.get("finish_reason"),
            next_question=next_q
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result/{session_id}")
async def get_result(session_id: str, user: dict = Depends(get_current_user)):
    """Get exam results. If session is active, finishes it first."""
    try:
        # Try to finish active session
        if session_id in ExamService._active_sessions:
            result = ExamService.finish_exam(session_id)
            return result
        
        # Otherwise fetch from DB
        from models.database import get_supabase_admin
        supabase = get_supabase_admin()
        
        session = supabase.table("exam_sessions").select("*").eq(
            "session_id", session_id
        ).single().execute()
        
        if not session.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        answers = supabase.table("answers").select("*").eq(
            "session_id", session.data["id"]
        ).order("question_order").execute()
        
        return {
            "session_id": session.data["session_id"],
            "subject": session.data["subject_name"],
            "total_questions": session.data["total_questions"],
            "correct_answers": session.data["correct_answers"],
            "raw_percentage": session.data["raw_percentage"],
            "final_theta": session.data["final_theta"],
            "final_se": session.data["final_se"],
            "start_time": session.data["start_time"],
            "end_time": session.data["end_time"],
            "responses": answers.data or []
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
