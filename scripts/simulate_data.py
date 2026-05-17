import json
import numpy as np
import pandas as pd
import os
from irt_engine import IRTEngine2PL

def simulate_student_responses(question_bank_path, output_csv_path, num_students=200):
    """
    Simulates student responses based on the item parameters in the question bank
    and true hidden student abilities.
    """
    print(f"Loading questions from {question_bank_path}")
    with open(question_bank_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    questions = data.get("questions", [])
    num_items = len(questions)
    
    if num_items == 0:
        print("No questions found in the bank.")
        return

    # Extract true item parameters
    true_a = np.array([q["irt_parameters"]["a"] for q in questions])
    true_b = np.array([q["irt_parameters"]["b"] for q in questions])
    question_ids = [q["question_id"] for q in questions]

    # Generate true student abilities (normal distribution, mean 0, std 1)
    np.random.seed(42) # For reproducibility
    true_thetas = np.random.normal(0, 1, num_students)
    
    response_matrix = np.zeros((num_students, num_items))
    
    print(f"Simulating responses for {num_students} students and {num_items} items...")
    
    for i in range(num_students):
        for j in range(num_items):
            prob = IRTEngine2PL.probability(true_thetas[i], true_a[j], true_b[j])
            # Simulate a 1 or 0 based on the probability
            response = np.random.binomial(1, prob)
            response_matrix[i, j] = response

    # Save to a CSV simulating real-world data collection
    df = pd.DataFrame(response_matrix, columns=question_ids)
    df.insert(0, "student_id", [f"STU_{i+1:04d}" for i in range(num_students)])
    
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df.to_csv(output_csv_path, index=False)
    print(f"Simulated responses saved to {output_csv_path}")
    
if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bank_path = os.path.join(BASE_DIR, "data", "processed", "cleaned_question_bank.json")
    out_path = os.path.join(BASE_DIR, "data", "raw", "simulated_student_responses.csv")
    simulate_student_responses(bank_path, out_path)
