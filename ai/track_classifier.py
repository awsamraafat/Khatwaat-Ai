"""
Track Classification Engine

Predicts which academic/career track best fits a student based on their
performance across subjects using their IRT theta scores.

Tracks:
1. Engineering & Computer Science
2. Medicine & Life Sciences  
3. Business
4. Arts & Humanities
"""
import numpy as np
from typing import Dict, List, Tuple


# Track definitions with subject weight profiles
# Each track has weights for how important each subject is
TRACK_PROFILES = {
    "Engineering & Computer Science": {
        "MATH": 0.35,
        "SCIENCE": 0.25,
        "IQ": 0.25,
        "ENGLISH": 0.10,
        "ARABIC": 0.05
    },
    "Medicine & Life Sciences": {
        "SCIENCE": 0.40,
        "MATH": 0.20,
        "IQ": 0.15,
        "ENGLISH": 0.15,
        "ARABIC": 0.10
    },
    "Business": {
        "MATH": 0.25,
        "ENGLISH": 0.25,
        "IQ": 0.25,
        "ARABIC": 0.15,
        "SCIENCE": 0.10
    },
    "Arts & Humanities": {
        "ARABIC": 0.35,
        "ENGLISH": 0.30,
        "IQ": 0.20,
        "MATH": 0.05,
        "SCIENCE": 0.10
    }
}


def classify_track(subject_thetas: Dict[str, float]) -> List[Tuple[str, float]]:
    """
    Classify a student into tracks based on their subject theta scores.
    
    Args:
        subject_thetas: Dict mapping subject name -> theta score.
            e.g., {"MATH": 1.5, "SCIENCE": 0.8, "IQ": 1.2, "ENGLISH": -0.3, "ARABIC": 0.5}
    
    Returns:
        List of (track_name, confidence_score) tuples, sorted by confidence descending.
        Confidence is normalized to [0, 1].
    """
    if not subject_thetas:
        return []
    
    track_scores = {}
    
    for track_name, weights in TRACK_PROFILES.items():
        score = 0.0
        total_weight = 0.0
        
        for subject, weight in weights.items():
            if subject in subject_thetas:
                # Normalize theta to [0, 1] range using sigmoid-like transform
                theta = subject_thetas[subject]
                normalized = 1.0 / (1.0 + np.exp(-theta))  # Maps (-inf, inf) to (0, 1)
                score += weight * normalized
                total_weight += weight
        
        if total_weight > 0:
            track_scores[track_name] = score / total_weight
        else:
            track_scores[track_name] = 0.5  # Neutral if no data
    
    # Normalize scores to sum to 1 (confidence distribution)
    total = sum(track_scores.values())
    if total > 0:
        track_scores = {k: v / total for k, v in track_scores.items()}
    
    # Sort by score descending
    sorted_tracks = sorted(track_scores.items(), key=lambda x: x[1], reverse=True)
    
    return sorted_tracks


def get_track_prediction(subject_thetas: Dict[str, float]) -> dict:
    """
    Get the full track prediction with reasoning.
    
    Returns:
        {
            "predicted_track": "Engineering & Computer Science",
            "confidence": 0.85,
            "all_tracks": [...],
            "reasoning": "..."
        }
    """
    tracks = classify_track(subject_thetas)
    
    if not tracks:
        return {
            "predicted_track": None,
            "confidence": 0,
            "all_tracks": [],
            "reasoning": "Insufficient data for prediction"
        }
    
    predicted_track, confidence = tracks[0]
    
    # Generate reasoning based on strongest subjects
    sorted_subjects = sorted(subject_thetas.items(), key=lambda x: x[1], reverse=True)
    strong_subjects = [s for s, t in sorted_subjects if t > 0.5]
    weak_subjects = [s for s, t in sorted_subjects if t < -0.5]
    
    reasoning_parts = []
    if strong_subjects:
        reasoning_parts.append(f"Strong performance in: {', '.join(strong_subjects)}")
    if weak_subjects:
        reasoning_parts.append(f"Needs improvement in: {', '.join(weak_subjects)}")
    reasoning_parts.append(f"Best fit: {predicted_track} (confidence: {confidence:.0%})")
    
    return {
        "predicted_track": predicted_track,
        "confidence": round(confidence, 4),
        "all_tracks": [{"track": t, "confidence": round(c, 4)} for t, c in tracks],
        "reasoning": ". ".join(reasoning_parts)
    }
