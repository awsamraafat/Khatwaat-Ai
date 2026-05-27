"""
Recommendation Engine (Nezam El Masarat & University College Placement)

Generates personalized academic track recommendations for High School (Short-Term)
and matching University Colleges (Long-Term) based on student performance (theta scores).
"""
import numpy as np
from typing import Dict, List
from ai.track_classifier import get_track_prediction, TRACK_PROFILES

# Flat weights for General Track profile
GENERAL_TRACK_PROFILE = {
    "MATH": 0.20,
    "SCIENCE": 0.20,
    "ENGLISH": 0.20,
    "ARABIC": 0.20,
    "IQ": 0.20
}

# Short-term High School educational tracks
EDUCATIONAL_TRACKS = {
    "مسار الهندسة وعلوم الحاسب (Engineering & CS)": {
        "profile": TRACK_PROFILES["Engineering & Computer Science"],
        "icon": "💻",
        "description": "يناسب الطلاب الشغوفين بالتقنية والابتكار والبرمجيات؛ يعتمد بقوة على مهاراتك المتميزة في الرياضيات المتقدمة والتفكير المنطقي والتحليلي."
    },
    "مسار الصحة والحياة (Health & Life Sciences)": {
        "profile": TRACK_PROFILES["Medicine & Life Sciences"],
        "icon": "🔬",
        "description": "يناسب الطلاب المهتمين بالطب، الرعاية الصحية، وعلوم الأحياء والكيمياء؛ يعتمد على تميزك في التفكير العلمي والمهارات العملية."
    },
    "مسار إدارة الأعمال (Business Administration)": {
        "profile": TRACK_PROFILES["Business"],
        "icon": "📈",
        "description": "يناسب الطلاب المهتمين بريادة الأعمال، التمويل، والتسويق والإدارة؛ يركز على مهاراتك اللغوية (الإنجليزية) والرياضيات التطبيقية."
    },
    "مسار العلوم الإنسانية والآداب (Arts & Humanities)": {
        "profile": TRACK_PROFILES["Arts & Humanities"],
        "icon": "⚖️",
        "description": "يناسب الطلاب المهتمين بالقانون، الإعلام، الترجمة والآداب؛ يركز على مهارات التعبير واللغات والتفكير النقدي والفلسفي."
    },
    "المسار العام (General Track)": {
        "profile": GENERAL_TRACK_PROFILE,
        "icon": "🌐",
        "description": "مسار متوازن ومرن يجمع بين شتى العلوم والمعارف بشكل متكافئ ويفتح لك خيارات متعددة ومتنوعة في القبول الجامعي العام."
    }
}

# Long-term University College Placement mapped to Tracks
COLLEGE_PLACEMENTS = [
    {
        "role": "كلية الحاسبات وتقنية المعلومات (College of Computers & IT)",
        "track": "Engineering & Computer Science",
        "track_key": "مسار الهندسة وعلوم الحاسب (Engineering & CS)",
        "icon": "💻",
        "reason": "بناءً على تفوقك الرياضي المتميز وقدرتك التحليلية العالية في الذكاء المنطقي؛ خيار ممتاز للتخصص في علوم الحاسب والأمن السيبراني والذكاء الاصطناعي."
    },
    {
        "role": "كلية الهندسة (College of Engineering)",
        "track": "Engineering & Computer Science",
        "track_key": "مسار الهندسة وعلوم الحاسب (Engineering & CS)",
        "icon": "🏗️",
        "reason": "تأهلك مهاراتك المتقدمة في الرياضيات وحل المشكلات الهندسية المعقدة لدراسة مجالات الهندسة الكهربائية والميكانيكية والبرمجيات بكفاءة."
    },
    {
        "role": "كلية الذكاء الاصطناعي والبيانات (College of AI & Data Science)",
        "track": "Engineering & Computer Science",
        "track_key": "مسار الهندسة وعلوم الحاسب (Engineering & CS)",
        "icon": "🤖",
        "reason": "تعد القدرة العالية على التفكير المنطقي والرياضيات حجر الأساس للتميز في هندسة البيانات وبناء نماذج الذكاء الاصطناعي وتعلم الآلة."
    },
    {
        "role": "كلية الطب البشري وطب الأسنان (College of Medicine & Dentistry)",
        "track": "Medicine & Life Sciences",
        "track_key": "مسار الصحة والحياة (Health & Life Sciences)",
        "icon": "🩺",
        "reason": "تفوقك العلمي المتميز في مواد العلوم العامة يجعلك مرشحاً رائعاً لدراسة الطب البشري أو جراحة الفم والأسنان ورعاية المرضى وعلاجهم."
    },
    {
        "role": "كلية الصيدلة (College of Pharmacy)",
        "track": "Medicine & Life Sciences",
        "track_key": "مسار الصحة والحياة (Health & Life Sciences)",
        "icon": "💊",
        "reason": "تمكنك المميز في الكيمياء وعلوم الحياة يؤهلك بقوة لدراسة علم الأدوية، التفاعلات الدوائية، والصيدلة الإكلينيكية وأبحاث العلاج."
    },
    {
        "role": "كلية العلوم الطبية التطبيقية (College of Applied Medical Sciences)",
        "track": "Medicine & Life Sciences",
        "track_key": "مسار الصحة والحياة (Health & Life Sciences)",
        "icon": "🔬",
        "reason": "تتوافق قدراتك في التفكير العلمي والعلوم الطبية التطبيقية للتميز في تخصصات المختبرات الطبية، الأشعة، والعلاج الطبيعي."
    },
    {
        "role": "كلية إدارة الأعمال والمالية (College of Business & Finance)",
        "track": "Business",
        "track_key": "مسار إدارة الأعمال (Business Administration)",
        "icon": "📊",
        "reason": "توافق رائع بين مهارات الإنجليزية المتقدمة والرياضيات التطبيقية يمهد لك الطريق لدراسة التمويل والاستثمار، المحاسبة، والتسويق الرقمي."
    },
    {
        "role": "كلية نظم المعلومات الإدارية (College of MIS)",
        "track": "Business",
        "track_key": "مسار إدارة الأعمال (Business Administration)",
        "icon": "💻",
        "reason": "الدمج بين التفكير التقني والمهارات الإدارية واللغوية يؤهلك لإدارة وتصميم النظم الرقمية والتحول التكنولوجي في الشركات والمؤسسات."
    },
    {
        "role": "كلية الحقوق والأنظمة (College of Law)",
        "track": "Arts & Humanities",
        "track_key": "مسار العلوم الإنسانية والآداب (Arts & Humanities)",
        "icon": "⚖️",
        "reason": "قوة مهارات اللغة والتفكير النقدي والمحاججة اللفظية تؤهلك للتميز الباهر في دراسة الأنظمة والقوانين، والمحاماة، والاستشارات الشرعية."
    },
    {
        "role": "كلية اللغات والترجمة (College of Languages & Translation)",
        "track": "Arts & Humanities",
        "track_key": "مسار العلوم الإنسانية والآداب (Arts & Humanities)",
        "icon": "🗣️",
        "reason": "تميزك اللغوي الواضح في اللغتين العربية والإنجليزية يفتح أمامك آفاقاً واسعة في مجالات الترجمة التحريرية والفورية وعلم اللغويات والاتصال الدولي."
    },
    {
        "role": "كلية الإعلام والاتصال (College of Media & Communication)",
        "track": "Arts & Humanities",
        "track_key": "مسار العلوم الإنسانية والآداب (Arts & Humanities)",
        "icon": "🎙️",
        "reason": "التمكن اللغوي والقدرة التعبيرية العالية تتيح لك التميز في العمل الإعلامي الرقمي، العلاقات العامة، وتصميم المحتوى الجماهيري."
    },
    {
        "role": "كلية العلوم الأساسية (College of Sciences)",
        "track": "General",
        "track_key": "المسار العام (General Track)",
        "icon": "🌐",
        "reason": "يفتح أمامك تفوقك المتوازن في شتى المواد فرصة لدراسة العلوم الطبيعية مثل الفيزياء أو الكيمياء العامة أو الرياضيات بالجامعة."
    },
    {
        "role": "كلية التربية (College of Education)",
        "track": "General",
        "track_key": "المسار العام (General Track)",
        "icon": "🏫",
        "reason": "امتلاكك لمهارات معرفية شاملة ومتوازنة يؤهلك للتميز في قطاع التعليم وتدريس المناهج الدراسية وإدارة المنشآت التعليمية."
    }
]


def calculate_match_score(subject_thetas: Dict[str, float], profile: Dict[str, float]) -> float:
    """Calculate the AI match score for a profile using sigmoid transform on theta scores."""
    score = 0.0
    total_weight = 0.0
    
    for subject, weight in profile.items():
        theta = subject_thetas.get(subject, 0.0)
        # Sigmoid maps (-inf, inf) to (0.0, 1.0)
        # theta of 0 maps to 0.5 (average)
        # theta of +1.5 maps to 0.82
        # theta of -1.5 maps to 0.18
        normalized = 1.0 / (1.0 + np.exp(-theta))
        score += weight * normalized
        total_weight += weight
        
    return score / total_weight if total_weight > 0 else 0.5


def get_short_term_recommendations(subject_thetas: Dict[str, float]) -> List[dict]:
    """
    Generate short-term High School track recommendations (Nezam El Masarat).
    All tracks are returned with their AI match score percentages.
    """
    recommendations = []
    
    for track_name, info in EDUCATIONAL_TRACKS.items():
        match_val = calculate_match_score(subject_thetas, info["profile"])
        
        recommendations.append({
            "path": track_name,
            "match_score": round(match_val, 4),
            "reason": info["description"],
            "icon": info["icon"]
        })
        
    # Sort tracks by match score descending
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    return recommendations


def get_long_term_recommendations(subject_thetas: Dict[str, float]) -> List[dict]:
    """
    Generate long-term University College Placement recommendations.
    All suitable colleges are returned with their match scores matching the corresponding track.
    """
    # Pre-calculate track scores
    track_scores = {}
    for track_name, info in EDUCATIONAL_TRACKS.items():
        track_scores[track_name] = calculate_match_score(subject_thetas, info["profile"])
        
    recommendations = []
    
    for college in COLLEGE_PLACEMENTS:
        track_key = college["track_key"]
        match_val = track_scores.get(track_key, 0.5)
        
        recommendations.append({
            "role": college["role"],
            "match_score": round(match_val, 4),
            "reason": college["reason"],
            "icon": college["icon"],
            "track": track_key
        })
        
    # Sort colleges by match score descending
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    return recommendations


def get_all_recommendations(subject_thetas: Dict[str, float]) -> dict:
    """Get complete AI recommendation package."""
    track = get_track_prediction(subject_thetas)
    
    return {
        "short_term": get_short_term_recommendations(subject_thetas),
        "long_term": get_long_term_recommendations(subject_thetas),
        "predicted_track": track.get("predicted_track"),
        "track_confidence": track.get("confidence"),
        "track_details": track
    }
