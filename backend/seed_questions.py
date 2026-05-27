"""
Seed script to import questions from Google Sheets CSV into Supabase.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from models.database import get_supabase_admin

GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1ANWBSbpuf5Z1QP_nxvvfiu-3Rmc-bdinPbIErtoGkvI/export?format=csv"

# Subject metadata mapping
SUBJECT_TOPICS = {
    'ARABIC': 'النصوص والبلاغة',
    'ENGLISH': 'Grammar and Reading',
    'SCIENCE': 'General Science',
    'MATH': 'Algebra and Geometry',
    'IQ': 'Logical Reasoning'
}

SUBJECT_SKILLS = {
    'ARABIC': 'التحليل والاستنتاج',
    'ENGLISH': 'Comprehension',
    'SCIENCE': 'Scientific Method',
    'MATH': 'Problem Solving',
    'IQ': 'Critical Thinking'
}


def seed_questions():
    print("Fetching questions from Google Sheet...")
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL)
    
    initial = len(df)
    df = df.drop_duplicates()
    df = df.drop_duplicates(subset=['QuestionText'], keep='first')
    print(f"Loaded {len(df)} unique questions (removed {initial - len(df)} duplicates)")
    
    supabase = get_supabase_admin()
    
    # Batch insert
    batch = []
    for _, row in df.iterrows():
        subject = str(row.get('Subject', 'UNKNOWN')).strip()
        
        # Allow configuring IRT parameters directly from the spreadsheet if the columns exist,
        # otherwise fallback to the default mathematical values.
        irt_a = float(row['irt_a']) if 'irt_a' in row and pd.notna(row['irt_a']) else 1.0
        irt_b = float(row['irt_b']) if 'irt_b' in row and pd.notna(row['irt_b']) else 0.0
        irt_c = float(row['irt_c']) if 'irt_c' in row and pd.notna(row['irt_c']) else 0.25

        batch.append({
            "question_id": str(row['QuestionID']),
            "subject_name": subject,
            "question_text": str(row['QuestionText']),
            "question_type": "MCQ",
            "option_a": str(row['OptionA']),
            "option_b": str(row['OptionB']),
            "option_c": str(row['OptionC']),
            "option_d": str(row['OptionD']),
            "correct_answer": str(row['CorrectAnswer']),
            "topic": SUBJECT_TOPICS.get(subject, 'General'),
            "skill": SUBJECT_SKILLS.get(subject, 'General'),
            "difficulty": "Medium",
            "irt_a": irt_a,
            "irt_b": irt_b,
            "irt_c": irt_c,
            "calibrated": False
        })
    
    # Insert in chunks of 50
    chunk_size = 50
    inserted = 0
    for i in range(0, len(batch), chunk_size):
        chunk = batch[i:i+chunk_size]
        try:
            supabase.table("questions").upsert(chunk, on_conflict="question_id").execute()
            inserted += len(chunk)
            print(f"  Inserted {inserted}/{len(batch)} questions...")
        except Exception as e:
            print(f"  Error inserting chunk: {e}")
    
    print(f"\nSeeding complete! {inserted} questions in database.")
    
    # Print summary
    for subject in ['ARABIC', 'ENGLISH', 'SCIENCE', 'MATH', 'IQ']:
        count = len([q for q in batch if q['subject_name'] == subject])
        print(f"  {subject}: {count} questions")


if __name__ == "__main__":
    seed_questions()
