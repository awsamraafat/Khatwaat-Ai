from fastapi import APIRouter, Depends, HTTPException
from models.schemas import AntiCheatEvent
from middleware.auth_middleware import get_current_user
from models.database import get_supabase_admin

router = APIRouter(prefix="/anti-cheat", tags=["Anti-Cheat"])


@router.post("/event")
async def log_anti_cheat_event(event: AntiCheatEvent, user: dict = Depends(get_current_user)):
    """Log an anti-cheat event from the frontend."""
    try:
        supabase = get_supabase_admin()
        
        # Find the session
        session = supabase.table("exam_sessions").select("id").eq(
            "session_id", event.session_id
        ).single().execute()
        
        if not session.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Calculate risk score based on event type
        risk_scores = {
            "tab_switch": 15,
            "copy_paste": 25,
            "fullscreen_exit": 20,
            "right_click": 5,
            "devtools_open": 40,
            "abnormal_timing": 30,
            "webcam_face_missing": 35,
            "webcam_multiple_faces": 45,
            "answer_similarity": 50
        }
        
        risk = risk_scores.get(event.event_type, 10)
        
        # Insert log
        supabase.table("anti_cheat_logs").insert({
            "session_id": session.data["id"],
            "event_type": event.event_type,
            "event_data": event.event_data,
            "risk_score": risk
        }).execute()
        
        # Calculate cumulative risk for this session
        all_logs = supabase.table("anti_cheat_logs").select("risk_score").eq(
            "session_id", session.data["id"]
        ).execute()
        
        total_risk = sum(log["risk_score"] for log in (all_logs.data or []))
        cumulative_risk = min(total_risk, 100)  # Cap at 100
        
        return {
            "logged": True,
            "event_risk": risk,
            "cumulative_risk": cumulative_risk,
            "alert": cumulative_risk > 70
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}")
async def get_session_risk(session_id: str, user: dict = Depends(get_current_user)):
    """Get anti-cheat risk summary for a session."""
    try:
        supabase = get_supabase_admin()
        
        session = supabase.table("exam_sessions").select("id").eq(
            "session_id", session_id
        ).single().execute()
        
        if not session.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        logs = supabase.table("anti_cheat_logs").select("*").eq(
            "session_id", session.data["id"]
        ).order("timestamp").execute()
        
        events = logs.data or []
        total_risk = sum(e["risk_score"] for e in events)
        
        # Group by event type
        event_counts = {}
        for e in events:
            t = e["event_type"]
            event_counts[t] = event_counts.get(t, 0) + 1
        
        return {
            "session_id": session_id,
            "total_events": len(events),
            "cumulative_risk": min(total_risk, 100),
            "event_breakdown": event_counts,
            "events": events,
            "is_suspicious": total_risk > 50
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
