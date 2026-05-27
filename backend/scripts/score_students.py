import sys
import os
import json
import pandas as pd
import numpy as np
# Inject parent directory (/backend) to resolve the "ai" package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai.irt_engine import IRTEngine2PL

def score_students(responses_csv_path, bank_path):
    """
    Scores students (estimates their theta ability) based on a calibrated question bank.
    """
    print(f"Loading calibrated question bank from {bank_path}...")
    with open(bank_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    questions = data.get("questions", [])
    
    # Create a fast lookup for parameters
    param_dict = {q["question_id"]: q["irt_parameters"] for q in questions if q["metadata"].get("calibrated", False)}
    
    print(f"Loaded {len(param_dict)} calibrated questions.")
    
    print(f"Loading student responses from {responses_csv_path}...")
    df = pd.read_csv(responses_csv_path)
    
    student_ids = df['student_id'].tolist()
    question_ids = df.columns.drop('student_id').tolist()
    
    results = []
    
    print("Estimating abilities (theta)...")
    for index, row in df.iterrows():
        student_id = row['student_id']
        
        # Collect responses and corresponding parameters
        student_responses = []
        a_params = []
        b_params = []
        
        for qid in question_ids:
            response = row[qid]
            # If the student answered this question and it's calibrated
            if not pd.isna(response) and qid in param_dict:
                student_responses.append(response)
                a_params.append(param_dict[qid]["a"])
                b_params.append(param_dict[qid]["b"])
                
        if len(student_responses) > 0:
            theta = IRTEngine2PL.estimate_ability(
                np.array(student_responses),
                np.array(a_params),
                np.array(b_params)
            )
            
            # Simple Classical Test Theory (CTT) score for comparison
            raw_score = sum(student_responses)
            total_answered = len(student_responses)
            
            results.append({
                "student_id": student_id,
                "raw_score": raw_score,
                "total_answered": total_answered,
                "percentage": (raw_score / total_answered) * 100,
                "theta_ability": theta
            })
            
    results_df = pd.DataFrame(results)
    
    print("\n--- Scoring Complete ---")
    print("Sample Results (Top 5 and Bottom 5 by Theta):")
    results_df = results_df.sort_values(by='theta_ability', ascending=False)
    print("\nTop 5 Students:")
    print(results_df.head(5).to_string(index=False))
    print("\nBottom 5 Students:")
    print(results_df.tail(5).to_string(index=False))
    
    return results_df

if __name__ == "__main__":
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(BASE_DIR, "data", "raw", "simulated_student_responses.csv")
    bank_path = os.path.join(BASE_DIR, "data", "processed", "calibrated_question_bank.json")
    
    # Note: We are using the simulated responses here to test the scoring, 
    # but in reality, you would use NEW test responses against the calibrated bank.
    score_students(csv_path, bank_path)
