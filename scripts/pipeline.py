import pandas as pd
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(BASE_DIR, "data", "raw", "QuestionBank.csv")
output_path = os.path.join(BASE_DIR, "data", "processed", "cleaned_question_bank.json")

def clean_and_process():
    print("Loading data...")
    df = pd.read_csv(csv_path)
    
    initial_count = len(df)
    
    # Drop full duplicates
    df = df.drop_duplicates()
    
    # Drop duplicates by QuestionText
    df = df.drop_duplicates(subset=['QuestionText'], keep='first')
    
    final_count = len(df)
    print(f"Removed {initial_count - final_count} duplicate questions.")
    
    # We will map Subject to topics and skills as placeholders
    subject_topics = {
        'ARABIC': 'النصوص والبلاغة',
        'ENGLISH': 'Grammar and Reading',
        'SCIENCE': 'General Science',
        'MATH': 'Algebra and Geometry',
        'IQ': 'Logical Reasoning'
    }
    
    subject_skills = {
        'ARABIC': 'التحليل والاستنتاج',
        'ENGLISH': 'Comprehension',
        'SCIENCE': 'Scientific Method',
        'MATH': 'Problem Solving',
        'IQ': 'Critical Thinking'
    }

    questions = []
    
    for _, row in df.iterrows():
        subject = str(row.get('Subject', 'UNKNOWN')).strip()
        topic = subject_topics.get(subject, 'General Topic')
        skill = subject_skills.get(subject, 'General Skill')
        difficulty = 'Medium'  # Default placeholder
        
        q_obj = {
            "question_id": str(row.get('QuestionID')),
            "metadata": {
                "subject": subject,
                "topic": topic,
                "skill": skill,
                "difficulty": difficulty,
                "calibrated": False
            },
            "content": {
                "question_text": str(row.get('QuestionText')),
                "question_type": "MCQ",
                "options": [
                    {"id": "A", "text": str(row.get('OptionA'))},
                    {"id": "B", "text": str(row.get('OptionB'))},
                    {"id": "C", "text": str(row.get('OptionC'))},
                    {"id": "D", "text": str(row.get('OptionD'))}
                ],
                "correct_answer": str(row.get('CorrectAnswer'))
            },
            "irt_parameters": {
                "a": 1.0,
                "b": 0.0,
                "c": 0.25
            }
        }
        questions.append(q_obj)
        
    print(f"Processed {len(questions)} unique questions.")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({"questions": questions}, f, ensure_ascii=False, indent=4)
        
    print(f"Data successfully saved to:\n{output_path}")

if __name__ == "__main__":
    clean_and_process()
