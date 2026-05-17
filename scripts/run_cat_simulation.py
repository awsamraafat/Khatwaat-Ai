import os
from cat_engine import CATEngine

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(subject, question_num, theta, se):
    print("="*60)
    print(f"  Adaptive Exam Simulator: {subject}")
    print(f"  Question: {question_num} | Est. Theta: {theta:+.3f} | SE: {se:.3f}")
    print("="*60)

def run_simulation(bank_path, subject):
    print(f"Initializing CAT Engine for subject: {subject}...")
    try:
        engine = CATEngine(bank_path, subject=subject)
    except ValueError as e:
        print(f"Error: {e}")
        return

    print("Engine Ready. Press Enter to start...")
    input()
    
    question_count = 1
    
    while True:
        clear_screen()
        
        # Check if we should stop
        finished, reason = engine.is_finished(max_questions=15, target_se=0.3)
        if finished:
            print("="*60)
            print("  EXAM FINISHED")
            print(f"  Reason: {reason}")
            print(f"  Final Estimated Ability (Theta): {engine.theta:+.3f}")
            print(f"  Final Standard Error (SE): {engine.get_standard_error():.3f}")
            print(f"  Questions Asked: {len(engine.history_questions)}")
            print("="*60)
            break

        # Get the next best question
        q = engine.get_next_question()
        if not q:
            break
            
        print_header(subject, question_count, engine.theta, engine.get_standard_error())
        print(f"\n[Difficulty (b): {q['irt_parameters']['b']:+.2f}]")
        print(f"Q: {q['content']['question_text']}")
        print("\nOptions:")
        for opt in q['content']['options']:
            print(f"  {opt['id']}) {opt['text']}")
            
        correct_answer = q['content']['correct_answer']
        
        print("\n(For testing, the correct answer is hidden. Choose A, B, C, or D)")
        user_ans = input("Your Answer: ").strip().upper()
        
        is_correct = (user_ans == correct_answer)
        
        if is_correct:
            print("Correct! -> Difficulty will increase.")
        else:
            print(f"Wrong! (Correct was {correct_answer}) -> Difficulty will decrease.")
            
        # Submit answer to engine and update theta
        engine.submit_answer(q["question_id"], is_correct)
        question_count += 1
        
        input("\nPress Enter for next question...")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bank = os.path.join(BASE_DIR, "data", "processed", "calibrated_question_bank.json")
    subject_choice = input("Enter Subject (e.g. ARABIC, MATH, SCIENCE): ").strip().upper()
    run_simulation(bank, subject_choice)
