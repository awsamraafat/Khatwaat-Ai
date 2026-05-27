/**
 * API Client for connecting Next.js frontend to FastAPI backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiClient {
  static async request(endpoint: string, options: RequestInit = {}) {
    const token = typeof window !== "undefined" ? localStorage.getItem("khatwaat_token") : null;
    
    const headers = {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      if (response.status === 401 && typeof window !== "undefined") {
        localStorage.removeItem("khatwaat_token");
        localStorage.removeItem("khatwaat_user");
        window.location.href = "/login";
        return;
      }
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `API Request failed with status ${response.status}`);
    }

    return response.json();
  }

  // --- Auth ---
  static async login(data: any) {
    const res = await this.request("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });
    if (res.access_token && typeof window !== "undefined") {
      localStorage.setItem("khatwaat_token", res.access_token);
      localStorage.setItem("khatwaat_user", JSON.stringify(res));
    }
    return res;
  }

  static async register(data: any) {
    const res = await this.request("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
    if (res.access_token && typeof window !== "undefined") {
      localStorage.setItem("khatwaat_token", res.access_token);
      localStorage.setItem("khatwaat_user", JSON.stringify(res));
    }
    return res;
  }

  static logout() {
    if (typeof window !== "undefined") {
      localStorage.removeItem("khatwaat_token");
      localStorage.removeItem("khatwaat_user");
    }
  }

  // --- Exams ---
  static async startExam(subject: string, max_questions: number = 20) {
    return this.request("/exam/start", {
      method: "POST",
      body: JSON.stringify({ subject, max_questions, target_se: 0.3 }),
    });
  }

  static async submitAnswer(sessionId: string, questionId: string, answer: string) {
    return this.request("/exam/answer", {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        question_id: questionId,
        user_answer: answer,
      }),
    });
  }

  static async getExamResult(sessionId: string) {
    return this.request(`/exam/result/${sessionId}`);
  }

  // --- Analytics ---
  static async getStudentAnalytics() {
    return this.request("/analytics/student");
  }

  static async getAdminAnalytics() {
    return this.request("/analytics/admin");
  }

  // --- Recommendations ---
  static async getRecommendations() {
    return this.request("/recommendations/");
  }

  // --- Anti-Cheat ---
  static async logAntiCheatEvent(sessionId: string, eventType: string, eventData: any = {}) {
    return this.request("/anti-cheat/event", {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        event_type: eventType,
        event_data: eventData,
      }),
    });
  }
}
