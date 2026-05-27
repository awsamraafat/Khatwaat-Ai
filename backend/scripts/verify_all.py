import os
import time
import sys
# Inject current folder and parent directory to resolve packages
base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_path)
sys.path.insert(0, os.path.dirname(base_path))

def verify_all():
    print("--- 1. Testing Data Simulation ---")
    try:
        from simulate_data import simulate_student_responses
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bank_path = os.path.join(BASE_DIR, "data", "processed", "cleaned_question_bank.json")
        out_path = os.path.join(BASE_DIR, "data", "raw", "simulated_student_responses.csv")
        # Run with a small number to make it fast
        simulate_student_responses(bank_path, out_path, num_students=20)
        print("Data Simulation PASSED.\n")
    except Exception as e:
        print(f"Data Simulation FAILED: {e}")
        return False

    print("--- 2. Testing Item Calibration ---")
    try:
        from calibrate_items import calibrate_and_update_bank
        calib_out_path = os.path.join(BASE_DIR, "data", "processed", "calibrated_question_bank.json")
        calibrate_and_update_bank(out_path, bank_path, calib_out_path)
        print("Item Calibration PASSED.\n")
    except Exception as e:
        print(f"Item Calibration FAILED: {e}")
        return False

    print("--- 3. Testing Exam Session (CAT Engine integration) ---")
    try:
        from session_manager import ExamSession
        # Test Session Manager
        session = ExamSession(student_id="VERIFY_101", bank_path=calib_out_path, subject="MATH", max_time_per_question=30)
        session.start_exam()
        
        for i in range(3):
            q = session.get_next_question()
            if not q:
                break
            
            # Simulate answering correctly
            correct_ans = q['content']['correct_answer']
            session.submit_answer(q["question_id"], correct_ans)
            
        receipt = session.finish_exam()
        if receipt["final_metrics"]["correct_answers"] != 3:
            raise ValueError("Correct answers mismatch in receipt.")
            
        print("Exam Session PASSED.\n")
    except Exception as e:
        print(f"Exam Session FAILED: {e}")
        return False

    print("ALL TESTS PASSED 100% SUCCESSFULLY.")
    return True

if __name__ == "__main__":
    verify_all()
