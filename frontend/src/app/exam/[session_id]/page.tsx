"use client";

import { useEffect, useState, use } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Clock, Shield, AlertTriangle, ArrowRight, CheckCircle2 } from "lucide-react";
import { ApiClient } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function ExamPage({ params }: { params: Promise<{ session_id: string }> }) {
  const router = useRouter();
  const resolvedParams = use(params);
  
  const [question, setQuestion] = useState<any>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [timeLeft, setTimeLeft] = useState(60);
  const [theta, setTheta] = useState(0);
  const [se, setSe] = useState(0);
  const [isCompleted, setIsCompleted] = useState(false);

  useEffect(() => {
    // Load the first question from localStorage
    const cached = localStorage.getItem("currentQuestion");
    if (cached) {
      setQuestion(JSON.parse(cached));
    } else {
      alert("No active question found. Please start the exam again.");
      router.push("/dashboard");
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    if (timeLeft <= 0) {
      handleSubmit(true);
      return;
    }
    const timer = setInterval(() => setTimeLeft((prev) => prev - 1), 1000);
    return () => clearInterval(timer);
  }, [timeLeft]);

  async function handleSubmit(isTimeout = false) {
    if (!selectedAnswer && !isTimeout) return;
    setSubmitting(true);
    
    try {
      // Connect to the real backend
      const res = await ApiClient.submitAnswer(
        resolvedParams.session_id, 
        question.question_id, 
        selectedAnswer
      );
      
      setTheta(res.new_theta);
      setSe(res.current_se);
      
      if (res.is_finished) {
        setIsCompleted(true);
        localStorage.removeItem("currentQuestion");
        return;
      }

      setQuestion(res.next_question);
      localStorage.setItem("currentQuestion", JSON.stringify(res.next_question));
      setSelectedAnswer("");
      setTimeLeft(60);
      
    } catch (e) {
      alert("Error submitting answer: " + (e as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <div className="min-h-screen bg-background flex justify-center items-center">Loading exam...</div>;

  if (isCompleted) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center p-6 relative overflow-hidden">
        {/* Neon blur background */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-emerald-500/5 rounded-full blur-[120px] -z-10" />
        
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-lg glass p-10 md:p-12 rounded-[2.5rem] border border-emerald-500/20 text-center space-y-8 shadow-2xl shadow-emerald-950/20 animate-fade-in"
        >
          {/* Animated Glow Circle */}
          <div className="mx-auto w-24 h-24 rounded-full bg-emerald-500/10 flex items-center justify-center border border-emerald-500/30 shadow-[0_0_40px_rgba(16,185,129,0.2)]">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200, damping: 15 }}
            >
              <CheckCircle2 className="w-12 h-12 text-emerald-400" />
            </motion.div>
          </div>

          <div className="space-y-3">
            <h1 className="text-3xl md:text-4xl font-bold font-outfit text-white">
              Assessment Completed!
            </h1>
            <p className="text-zinc-400 text-lg leading-relaxed">
              Fantastic job completing your <span className="text-emerald-400 font-semibold">{question?.subject || "Subject"}</span> exam! Your performance has been analyzed by our adaptive AI engine.
            </p>
          </div>

          <div className="glass bg-zinc-900/40 p-6 rounded-2xl border border-white/5 space-y-4">
            <div className="flex justify-between items-center text-sm border-b border-white/5 pb-3">
              <span className="text-zinc-500 font-medium">Subject</span>
              <span className="text-white font-bold">{question?.subject || "N/A"}</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-zinc-500 font-medium">Estimated Ability (θ)</span>
              <span className="text-emerald-400 font-extrabold text-2xl">{theta.toFixed(2)}</span>
            </div>
          </div>

          <button
            onClick={() => router.push("/dashboard")}
            className="w-full py-4 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white font-bold rounded-2xl transition-all shadow-lg shadow-emerald-900/30 hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-2 text-lg"
          >
            Return to Dashboard <ArrowRight className="w-5 h-5" />
          </button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Top Bar */}
      <header className="h-16 border-b border-border glass-panel sticky top-0 z-50 flex items-center justify-between px-6">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-emerald-400 text-sm font-medium bg-emerald-500/10 px-3 py-1.5 rounded-full border border-emerald-500/20">
            <Shield className="w-4 h-4" /> AI Proctoring Active
          </div>
          <span className="text-zinc-500 text-sm">Session ID: {resolvedParams.session_id.substring(0,8)}</span>
        </div>
        
        <div className="flex items-center gap-6">
          <div className="flex flex-col items-end">
            <span className="text-xs text-zinc-400 uppercase font-bold tracking-wider">Current Ability (θ)</span>
            <span className="text-primary font-bold">{theta.toFixed(2)} ±{se.toFixed(2)}</span>
          </div>
          <div className={`flex items-center gap-2 text-lg font-bold font-outfit px-4 py-1.5 rounded-xl border ${
            timeLeft < 15 ? "text-red-400 bg-red-500/10 border-red-500/20 animate-pulse" : "text-white bg-white/5 border-white/10"
          }`}>
            <Clock className="w-5 h-5" />
            00:{timeLeft.toString().padStart(2, '0')}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center p-6 relative overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/5 rounded-full blur-[120px] -z-10" />

        <div className="w-full max-w-3xl">
          <div className="flex justify-between items-center mb-6">
            <span className="text-sm font-medium text-primary px-3 py-1 bg-primary/10 rounded-lg border border-primary/20">
              {question.subject}
            </span>
            <span className={`text-sm font-medium px-3 py-1 rounded-lg border ${
              question.difficulty_label === "Easy" ? "text-emerald-400 bg-emerald-500/10 border-emerald-500/20" :
              question.difficulty_label === "Medium" ? "text-amber-400 bg-amber-500/10 border-amber-500/20" :
              "text-rose-400 bg-rose-500/10 border-rose-500/20"
            }`}>
              {question.difficulty_label}
            </span>
          </div>

          <AnimatePresence mode="wait">
            <motion.div
              key={question.question_id}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="glass p-8 md:p-12 rounded-[2rem] border border-white/10 shadow-2xl"
            >
              <h2 className="text-2xl md:text-3xl font-medium text-white mb-10 leading-relaxed">
                {question.question_text}
              </h2>

              <div className="space-y-4">
                {question.options.map((opt: any) => (
                  <button
                    key={opt.id}
                    onClick={() => setSelectedAnswer(opt.id)}
                    className={`w-full flex items-center gap-4 p-5 rounded-2xl border text-left transition-all ${
                      selectedAnswer === opt.id
                        ? "bg-primary/20 border-primary text-white shadow-[0_0_20px_rgba(59,130,246,0.15)] ring-1 ring-primary/50"
                        : "bg-white/5 border-white/10 text-zinc-300 hover:bg-white/10 hover:text-white"
                    }`}
                  >
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm transition-colors ${
                      selectedAnswer === opt.id ? "bg-primary text-white" : "bg-zinc-800 text-zinc-400"
                    }`}>
                      {opt.id}
                    </div>
                    <span className="text-lg">{opt.text}</span>
                  </button>
                ))}
              </div>

              <div className="mt-10 flex justify-end">
                <button
                  onClick={() => handleSubmit(false)}
                  disabled={!selectedAnswer || submitting}
                  className="bg-white text-black hover:bg-zinc-200 px-8 py-4 rounded-xl font-bold flex items-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
                >
                  {submitting ? (
                    <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                  ) : (
                    <>Submit Answer <ArrowRight className="w-5 h-5" /></>
                  )}
                </button>
              </div>
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}
