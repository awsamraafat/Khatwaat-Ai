import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException
from middleware.auth_middleware import get_current_user
from models.database import get_supabase_admin
from ai.recommendations import get_all_recommendations
from ai.track_classifier import get_track_prediction

# Trigger uvicorn reload to load updated AI recommendations
router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/")
async def get_recommendations(user: dict = Depends(get_current_user)):
    """Get personalized recommendations based on student performance."""
    try:
        supabase = get_supabase_admin()
        
        # Get student's theta scores per subject
        analytics = supabase.table("analytics").select("*").eq(
            "user_id", user["id"]
        ).execute()
        
        if not analytics.data:
            return {
                "short_term": [],
                "long_term": [],
                "predicted_track": None,
                "track_confidence": None,
                "message": "Take exams in multiple subjects to get personalized recommendations."
            }
        
        # Build subject_thetas dict
        subject_thetas = {}
        for record in analytics.data:
            subject_thetas[record["subject_name"]] = record.get("latest_theta", 0.0)
        
        # Generate recommendations
        result = get_all_recommendations(subject_thetas)
        
        # Save recommendations to DB
        track = result.get("predicted_track")
        if track:
            supabase.table("recommendations").upsert({
                "user_id": user["id"],
                "recommendation_type": "long_term",
                "track": track,
                "confidence": result.get("track_confidence", 0),
                "reasoning": result.get("track_details", {}).get("reasoning", "")
            }, on_conflict="user_id,recommendation_type").execute()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/track")
async def get_track(user: dict = Depends(get_current_user)):
    """Get track classification prediction."""
    try:
        supabase = get_supabase_admin()
        
        analytics = supabase.table("analytics").select("*").eq(
            "user_id", user["id"]
        ).execute()
        
        if not analytics.data:
            return {"predicted_track": None, "message": "Insufficient data"}
        
        subject_thetas = {r["subject_name"]: r.get("latest_theta", 0.0) for r in analytics.data}
        return get_track_prediction(subject_thetas)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
