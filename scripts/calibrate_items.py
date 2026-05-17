import json
import pandas as pd
import numpy as np
import os
from irt_engine import IRTEngine2PL

def calibrate_and_update_bank(responses_csv_path, bank_path, output_bank_path):
    """
    Reads student responses, calibrates items using JMLE, and saves a calibrated question bank.
    """
    print(f"Loading student responses from {responses_csv_path}...")
    df = pd.read_csv(responses_csv_path)
    
    # Drop student_id column to get the pure response matrix
    response_matrix = df.drop(columns=['student_id']).values
    question_ids = df.drop(columns=['student_id']).columns.tolist()
    
    print(f"Starting Item Calibration for {len(question_ids)} items and {len(df)} students...")
    print("This might take a few moments depending on the data size.")
    
    # Calibrate
    estimated_thetas, estimated_a, estimated_b = IRTEngine2PL.calibrate_bank(
        response_matrix, 
        max_iter=10, # Keep iteration low for performance during demonstration
        tol=1e-2
    )
    
    print("Calibration complete.")
    
    # Load existing question bank
    print(f"Loading question bank from {bank_path}...")
    with open(bank_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    questions = data.get("questions", [])
    
    # Update items with new parameters
    # We create a dictionary to map question IDs to their new parameters easily
    param_dict = {qid: {"a": a, "b": b} for qid, a, b in zip(question_ids, estimated_a, estimated_b)}
    
    updated_count = 0
    for q in questions:
        qid = q["question_id"]
        if qid in param_dict:
            q["irt_parameters"]["a"] = float(param_dict[qid]["a"])
            q["irt_parameters"]["b"] = float(param_dict[qid]["b"])
            q["metadata"]["calibrated"] = True
            updated_count += 1
            
    print(f"Updated parameters for {updated_count} questions.")
    
    # Save the calibrated bank
    os.makedirs(os.path.dirname(output_bank_path), exist_ok=True)
    with open(output_bank_path, 'w', encoding='utf-8') as f:
        json.dump({"questions": questions}, f, ensure_ascii=False, indent=4)
        
    print(f"Calibrated Question Bank saved to: {output_bank_path}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(BASE_DIR, "data", "raw", "simulated_student_responses.csv")
    input_bank = os.path.join(BASE_DIR, "data", "processed", "cleaned_question_bank.json")
    output_bank = os.path.join(BASE_DIR, "data", "processed", "calibrated_question_bank.json")
    
    calibrate_and_update_bank(csv_path, input_bank, output_bank)
