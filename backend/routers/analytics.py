from fastapi import APIRouter, Depends, HTTPException
from middleware.auth_middleware import get_current_user, require_admin
from models.database import get_supabase_admin

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/student")
async def get_student_analytics(user: dict = Depends(get_current_user)):
    """Get analytics for the current student."""
    try:
        supabase = get_supabase_admin()
        
        # Get per-subject analytics
        analytics = supabase.table("analytics").select("*").eq(
            "user_id", user["id"]
        ).execute()
        
        # Get recent exam sessions
        sessions = supabase.table("exam_sessions").select("*").eq(
            "user_id", user["id"]
        ).eq("status", "completed").order(
            "created_at", desc=True
        ).limit(20).execute()
        
        # Compute strengths and weaknesses
        subjects_data = []
        strengths = []
        weaknesses = []
        total_exams = 0
        theta_sum = 0
        
        for record in (analytics.data or []):
            subject = record["subject_name"]
            theta = record.get("latest_theta", 0)
            total_exams += record.get("total_exams", 0)
            theta_sum += theta
            
            accuracy = 0
            if record.get("total_questions_answered", 0) > 0:
                accuracy = round(record["total_correct"] / record["total_questions_answered"] * 100, 1)
            
            subjects_data.append({
                "subject": subject,
                "latest_theta": round(theta, 4),
                "total_exams": record.get("total_exams", 0),
                "total_questions": record.get("total_questions_answered", 0),
                "total_correct": record.get("total_correct", 0),
                "accuracy": accuracy
            })
            
            if theta > 0.5:
                strengths.append(subject)
            elif theta < -0.5:
                weaknesses.append(subject)
        
        overall_theta = round(theta_sum / len(analytics.data), 4) if analytics.data else None
        
        return {
            "user_id": user["id"],
            "subjects": subjects_data,
            "overall_theta": overall_theta,
            "total_exams": total_exams,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recent_sessions": sessions.data or []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin")
async def get_admin_analytics(user: dict = Depends(require_admin)):
    """Get system-wide analytics for admin."""
    try:
        supabase = get_supabase_admin()
        
        # Total counts
        students = supabase.table("profiles").select("id", count="exact").eq("role", "student").execute()
        exams = supabase.table("exam_sessions").select("id", count="exact").eq("status", "completed").execute()
        questions = supabase.table("questions").select("id", count="exact").execute()
        
        # Hardest questions (highest b)
        hardest = supabase.table("questions").select(
            "question_id, question_text, subject_name, irt_b, irt_a"
        ).eq("calibrated", True).order("irt_b", desc=True).limit(10).execute()
        
        # Easiest questions (lowest b)
        easiest = supabase.table("questions").select(
            "question_id, question_text, subject_name, irt_b, irt_a"
        ).eq("calibrated", True).order("irt_b").limit(10).execute()
        
        # Top students (highest theta)
        top_students = supabase.table("exam_sessions").select(
            "user_id, subject_name, final_theta, correct_answers, total_questions"
        ).eq("status", "completed").order("final_theta", desc=True).limit(10).execute()
        
        # Recent cheating alerts
        alerts = supabase.table("anti_cheat_logs").select(
            "*, exam_sessions(session_id, user_id, subject_name)"
        ).gt("risk_score", 50).order("timestamp", desc=True).limit(20).execute()
        
        return {
            "total_students": students.count or 0,
            "total_exams": exams.count or 0,
            "total_questions": questions.count or 0,
            "hardest_questions": hardest.data or [],
            "easiest_questions": easiest.data or [],
            "top_students": top_students.data or [],
            "cheating_alerts": alerts.data or []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
