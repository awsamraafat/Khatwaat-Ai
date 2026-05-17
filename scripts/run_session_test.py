import time
import os
from session_manager import ExamSession

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_test_session():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bank_path = os.path.join(BASE_DIR, "data", "processed", "calibrated_question_bank.json")
    student_id = "STU_1001"
    subject = "ARABIC"
    
    print(f"Initializing Session Manager for Student {student_id} on {subject}...")
    try:
        # Enforce 30 seconds max per question for this test
        session = ExamSession(student_id, bank_path, subject, max_time_per_question=30)
    except Exception as e:
        print(f"Error: {e}")
        return

    print("\n--- Starting Exam ---")
    session.start_exam()
    
    question_count = 1
    
    while True:
        finished, reason = session.is_finished(max_questions=5) # Stop after 5 questions for a quick test
        if finished:
            print("\n--- Exam Over ---")
            print(f"Reason: {reason}")
            break
            
        q = session.get_next_question()
        if not q:
            break
            
        print(f"\n[Question {question_count}] Difficulty (b): {q['irt_parameters']['b']:+.2f}")
        # Question text omitted to avoid console encoding issues on Windows
        # print(f"Q: {q['content']['question_text']}")
        print("(Options omitted for test script)")
        
        # Simulate time passing (e.g. reading the question)
        simulated_delay = 2.5 # Simulate 2.5 seconds thinking time
        print(f"   (Simulating student thinking for {simulated_delay} seconds...)")
        time.sleep(simulated_delay)
        
        # For testing, just submit the correct answer for the first few, then wrong
        correct_answer = q['content']['correct_answer']
        user_ans = correct_answer if question_count <= 3 else "WRONG_ANS"
        
        print(f"   Student answered: {user_ans}")
        is_correct, is_timeout, new_theta = session.submit_answer(q["question_id"], user_ans)
        
        print(f"   Result: Correct={is_correct}, Timeout={is_timeout}, New Theta={new_theta:+.3f}")
        
        question_count += 1
        
    print("\n--- Generating Final Receipt ---")
    receipt = session.finish_exam()
    print("Test Complete.")

if __name__ == "__main__":
    run_test_session()
