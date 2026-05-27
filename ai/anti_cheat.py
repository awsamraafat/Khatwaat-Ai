"""
Anti-Cheat AI — Backend Analysis Module

Provides server-side analysis of student behavior during exams:
- Timing anomaly detection
- Answer similarity detection between students
- Risk score aggregation
"""
import numpy as np
from typing import List, Dict
from datetime import datetime


def detect_timing_anomalies(answers: List[dict], time_per_question: int = 60) -> List[dict]:
    """
    Detect abnormal timing patterns in a student's answers.
    
    Flags:
    - Too fast (< 2s): likely random clicking
    - Suspiciously consistent timing: possible bot
    - Too slow but correct: possible looking up answers
    """
    anomalies = []
    times = [a.get("time_spent_seconds", 0) for a in answers]
    
    if not times:
        return anomalies
    
    avg_time = np.mean(times)
    std_time = np.std(times) if len(times) > 1 else 0
    
    for i, answer in enumerate(answers):
        t = answer.get("time_spent_seconds", 0)
        
        # Too fast (< 2 seconds)
        if t < 2.0:
            anomalies.append({
                "type": "too_fast",
                "question_id": answer.get("question_id"),
                "time": t,
                "risk": 30,
                "detail": f"Answered in {t:.1f}s (suspiciously fast)"
            })
        
        # Very slow but correct (possible lookup)
        if t > time_per_question * 0.9 and answer.get("is_correct", False):
            anomalies.append({
                "type": "slow_correct",
                "question_id": answer.get("question_id"),
                "time": t,
                "risk": 15,
                "detail": f"Answered correctly after {t:.1f}s (near timeout)"
            })
    
    # Check for suspiciously consistent timing (low std dev)
    if len(times) >= 5 and std_time < 1.0 and avg_time > 3.0:
        anomalies.append({
            "type": "consistent_timing",
            "risk": 25,
            "detail": f"Suspiciously consistent timing (avg={avg_time:.1f}s, std={std_time:.2f}s)"
        })
    
    return anomalies


def detect_answer_similarity(session_answers: List[dict], other_sessions: List[List[dict]], threshold: float = 0.9) -> List[dict]:
    """
    Compare a student's answer pattern against other concurrent sessions
    to detect potential answer copying.
    
    Args:
        session_answers: The current student's answers.
        other_sessions: List of other students' answer lists.
        threshold: Minimum similarity ratio to flag (0-1).
    
    Returns:
        List of similarity alerts.
    """
    alerts = []
    
    if not session_answers or not other_sessions:
        return alerts
    
    # Create answer vector for current student
    current_answers = {a["question_id"]: a["user_answer"] for a in session_answers}
    
    for i, other in enumerate(other_sessions):
        other_answers = {a["question_id"]: a["user_answer"] for a in other}
        
        # Find common questions
        common = set(current_answers.keys()) & set(other_answers.keys())
        
        if len(common) < 5:  # Need at least 5 common questions
            continue
        
        # Calculate similarity
        matches = sum(1 for q in common if current_answers[q] == other_answers[q])
        similarity = matches / len(common)
        
        if similarity >= threshold:
            alerts.append({
                "type": "answer_similarity",
                "other_session_index": i,
                "common_questions": len(common),
                "matching_answers": matches,
                "similarity": round(similarity, 4),
                "risk": min(int(similarity * 60), 50),
                "detail": f"Answer similarity {similarity:.0%} with another student ({matches}/{len(common)} matching)"
            })
    
    return alerts


def calculate_session_risk(
    timing_anomalies: List[dict],
    similarity_alerts: List[dict],
    frontend_events: List[dict]
) -> dict:
    """
    Aggregate all anti-cheat signals into a final risk assessment.
    
    Returns:
        {
            "total_risk": 0-100,
            "risk_level": "low" | "medium" | "high" | "critical",
            "breakdown": {...}
        }
    """
    timing_risk = sum(a.get("risk", 0) for a in timing_anomalies)
    similarity_risk = sum(a.get("risk", 0) for a in similarity_alerts)
    frontend_risk = sum(e.get("risk_score", 0) for e in frontend_events)
    
    total_risk = min(timing_risk + similarity_risk + frontend_risk, 100)
    
    if total_risk >= 80:
        level = "critical"
    elif total_risk >= 50:
        level = "high"
    elif total_risk >= 25:
        level = "medium"
    else:
        level = "low"
    
    return {
        "total_risk": total_risk,
        "risk_level": level,
        "breakdown": {
            "timing_risk": min(timing_risk, 40),
            "similarity_risk": min(similarity_risk, 50),
            "frontend_risk": min(frontend_risk, 40),
            "timing_anomalies": len(timing_anomalies),
            "similarity_alerts": len(similarity_alerts),
            "frontend_events": len(frontend_events)
        },
        "is_suspicious": total_risk > 50,
        "requires_review": total_risk > 70
    }
