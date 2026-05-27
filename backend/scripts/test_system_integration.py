import urllib.request
import urllib.error
import json
import time

BASE_URL = "http://localhost:8000"

def make_request(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    if data is not None:
        data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err_data = json.loads(e.read().decode("utf-8"))
        except Exception:
            err_data = e.reason
        return e.code, err_data
    except Exception as e:
        return 500, str(e)

def run_integration_test():
    print("============================================================")
    print("🧪 Starting End-to-End AI Assessment Integration Test 🧪")
    print("============================================================")
    
    # 1. Test Auth: Student Registration/Login
    print("\n[Step 1/5] Testing Authentication...")
    test_user = {
        "email": "e2e_student_test@khatwaat.com",
        "password": "Password123!",
        "full_name": "E2E Integration Test Student"
    }
    
    # Try register
    status, reg_res = make_request(f"{BASE_URL}/auth/register", method="POST", data=test_user)
    if status in [200, 201]:
        token = reg_res["access_token"]
        print("   ✅ Student Registration: SUCCESS!")
    else:
        # User already exists, try logging in
        status, login_res = make_request(f"{BASE_URL}/auth/login", method="POST", data={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        if status == 200:
            token = login_res["access_token"]
            print("   ✅ Student Login: SUCCESS!")
        else:
            print(f"   ❌ Authentication FAILED: {login_res}")
            return False
            
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # 2. Check Initial Analytics
    print("\n[Step 2/5] Checking Student Analytics Pre-Exam...")
    status, init_analytics = make_request(f"{BASE_URL}/analytics/student", headers=headers)
    if status != 200:
        print(f"   ❌ Analytics Check FAILED: {init_analytics}")
        return False
    
    print(f"   ✅ Initialized successfully. Total completed subjects: {len(init_analytics.get('subjects', []))}")

    # 3. Start Adaptive Exam for subject 'MATH'
    print("\n[Step 3/5] Starting Adaptive Exam for 'MATH'...")
    start_payload = {
        "subject": "MATH",
        "max_questions": 5,
        "target_se": 0.3
    }
    status, start_data = make_request(f"{BASE_URL}/exam/start", method="POST", data=start_payload, headers=headers)
    if status != 200:
        print(f"   ❌ Start Exam FAILED: {start_data}")
        return False
        
    session_id = start_data["session_id"]
    current_q = start_data["first_question"]
    print(f"   ✅ Exam Session Created: {session_id}")
    print(f"   ✅ First adaptive question loaded: {current_q['question_id']} | Difficulty: {current_q['difficulty_label']} (b: {current_q['irt_b']})")

    # 4. Simulate Student Exam Performance (5 Answering loops)
    print("\n[Step 4/5] Simulating Adaptive Exam Run...")
    for i in range(1, 6):
        print(f"   👉 Answering Question {i} ({current_q['question_id']})...")
        answer_payload = {
            "session_id": session_id,
            "question_id": current_q["question_id"],
            "user_answer": "A"  # Answer "A"
        }
        
        status, ans_res = make_request(f"{BASE_URL}/exam/answer", method="POST", data=answer_payload, headers=headers)
        if status != 200:
            print(f"      ❌ Answering FAILED on question {i}: {ans_res}")
            return False
            
        print(f"      Result: Correct={ans_res['is_correct']} | New Ability (Theta)={ans_res['new_theta']:.4f} | finished={ans_res['is_finished']}")
        
        if ans_res["is_finished"]:
            print(f"   ✅ Exam finished successfully on question {i}! Reason: {ans_res['finish_reason']}")
            break
            
        current_q = ans_res["next_question"]
        if not current_q:
            print("      ❌ Next question not served but exam is not completed!")
            return False
            
    # 5. Verify Database Finalization & AI Recommendation
    print("\n[Step 5/5] Verifying AI Recommendation & Database Locks...")
    
    # Check that subject 'MATH' is locked/marked completed in Student Analytics
    status, final_analytics = make_request(f"{BASE_URL}/analytics/student", headers=headers)
    if status != 200:
        print(f"   ❌ Analytics Check FAILED: {final_analytics}")
        return False
        
    math_completed = [s for s in final_analytics.get("subjects", []) if s["subject"] == "MATH"]
    if math_completed:
        print(f"   ✅ Database Lock verified: 'MATH' is locked as completed in Analytics. Ability: {math_completed[0]['latest_theta']:.4f}")
    else:
        print("   ❌ Database Lock FAILED: 'MATH' did not register as completed in Analytics.")
        return False
        
    # Get recommendations to check the AI tracks & college placement
    status, rec_res = make_request(f"{BASE_URL}/recommendations/", headers=headers)
    if status != 200:
        print(f"   ❌ AI Recommendation FAILED: {rec_res}")
        return False
        
    print("\n============================================================")
    print("🎉 SYSTEM STATUS: ALL ENGINES FULLY WORKING! 🎉")
    print("============================================================")
    print(f"📊 Predicted High School Track: {rec_res.get('predicted_track')}")
    print(f"🎯 AI Prediction Confidence: {rec_res.get('track_confidence') * 100:.1f}%")
    print("\n💡 Recommended Short-Term Tracks (Nezam El Masarat):")
    for track in rec_res.get("short_term", [])[:3]:
        print(f"   - {track['icon']} {track['path']} | Match: {track['match_score']*100:.1f}%")
        
    print("\n💡 Recommended Long-Term University Colleges:")
    for college in rec_res.get("long_term", [])[:3]:
        print(f"   - {college['icon']} {college['role']} | Match: {college['match_score']*100:.1f}%")
    print("============================================================")
    return True

if __name__ == "__main__":
    run_integration_test()
