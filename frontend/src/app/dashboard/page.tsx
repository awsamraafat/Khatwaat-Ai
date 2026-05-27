"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { PlayCircle, Award, TrendingUp, Clock, Brain, AlertTriangle, CheckCircle2, Sparkles } from "lucide-react";
import { useRouter } from "next/navigation";
import { ApiClient } from "@/lib/api";

export default function DashboardOverview() {
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await ApiClient.getStudentAnalytics();
        setAnalytics(data);
      } catch (e) {
        console.error("Failed to load analytics", e);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const startExam = async (subject: string) => {
    try {
      const res = await ApiClient.startExam(subject, 15);
      localStorage.setItem("currentQuestion", JSON.stringify(res.first_question));
      router.push(`/exam/${res.session_id}`);
    } catch (e) {
      alert("Failed to start exam. " + (e as Error).message);
    }
  };

  if (loading) {
    return (
      <div className="p-8 h-full flex flex-col items-center justify-center space-y-4">
        <div className="w-10 h-10 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
        <p className="text-muted-foreground animate-pulse">Loading your dashboard...</p>
      </div>
    );
  }

  const subjects = [
    { name: "MATH", icon: "📐", color: "from-purple-500 to-indigo-600" },
    { name: "SCIENCE", icon: "🔬", color: "from-emerald-400 to-teal-500" },
    { name: "ENGLISH", icon: "🌍", color: "from-blue-400 to-cyan-500" },
    { name: "ARABIC", icon: "📖", color: "from-rose-400 to-red-500" },
    { name: "IQ", icon: "🧠", color: "from-amber-400 to-orange-500" },
  ];

  return (
    <div className="p-6 md:p-10 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold font-outfit text-white mb-2">
            Welcome back! 👋
          </h1>
          <p className="text-muted-foreground text-lg">
            Ready to challenge yourself today?
          </p>
        </div>
        <div className="glass px-6 py-3 rounded-2xl flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center text-primary">
            <Award size={24} />
          </div>
          <div>
            <p className="text-sm text-zinc-400 font-medium">Overall Theta</p>
            <p className="text-2xl font-bold text-white">
              {analytics?.overall_theta !== null ? analytics?.overall_theta.toFixed(2) : "0.00"}
            </p>
          </div>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard 
          icon={<TrendingUp className="text-emerald-400" />} 
          label="Total Exams Taken" 
          value={analytics?.total_exams || 0} 
        />
        <StatCard 
          icon={<Brain className="text-purple-400" />} 
          label="Top Strength" 
          value={analytics?.strengths?.[0] || "None yet"} 
        />
        <StatCard 
          icon={<AlertTriangle className="text-amber-400" />} 
          label="Focus Area" 
          value={analytics?.weaknesses?.[0] || "None yet"} 
        />
      </div>

      {/* Subjects Grid */}
      <div>
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-4">
          <h2 className="text-2xl font-bold font-outfit text-white">Available Assessments</h2>
          
          {analytics?.subjects?.length >= 5 && (
            <motion.button
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              onClick={() => router.push("/dashboard/final-results")}
              className="bg-gradient-to-r from-primary to-purple-500 hover:from-primary/90 hover:to-purple-500/90 text-white px-6 py-3 rounded-xl font-bold flex items-center gap-2 shadow-lg shadow-primary/20 transition-all hover:scale-105 active:scale-95"
            >
              <Sparkles className="w-5 h-5" /> View Final AI Results
            </motion.button>
          )}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {subjects.map((subject, idx) => {
            // Find student's data for this subject if it exists
            const sData = analytics?.subjects?.find((s: any) => s.subject === subject.name);
            
            return (
              <motion.div
                key={subject.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="glass rounded-3xl overflow-hidden border border-white/10 flex flex-col hover-lift group"
              >
                <div className={`h-24 bg-gradient-to-br ${subject.color} p-6 relative overflow-hidden`}>
                  <div className="absolute -right-4 -bottom-4 text-8xl opacity-20 transform group-hover:scale-110 transition-transform duration-500">
                    {subject.icon}
                  </div>
                  <h3 className="text-2xl font-bold font-outfit text-white relative z-10">{subject.name}</h3>
                </div>
                
                <div className="p-6 flex-1 flex flex-col justify-between bg-card/50">
                  <div className="space-y-4 mb-6">
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-zinc-400">Current Ability (θ)</span>
                      <span className="font-semibold text-white px-2 py-1 bg-white/10 rounded-md">
                        {sData ? sData.latest_theta.toFixed(2) : "0.00"}
                      </span>
                    </div>
                    <div className="w-full bg-zinc-800 rounded-full h-2 overflow-hidden">
                      {/* Visual bar for theta (-3 to 3 mapped to 0-100%) */}
                      <div 
                        className={`h-full bg-gradient-to-r ${subject.color}`} 
                        style={{ width: `${Math.max(0, Math.min(100, ((sData?.latest_theta || 0) + 3) / 6 * 100))}%` }}
                      />
                    </div>
                  </div>
                  
                  {sData ? (
                    <button
                      disabled
                      className="w-full py-3 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium flex items-center justify-center gap-2 cursor-not-allowed opacity-80"
                    >
                      <CheckCircle2 size={18} /> Completed
                    </button>
                  ) : (
                    <button
                      onClick={() => startExam(subject.name)}
                      className="w-full py-3 rounded-xl bg-white/10 hover:bg-white/20 text-white font-medium transition-colors flex items-center justify-center gap-2"
                    >
                      <PlayCircle size={18} /> Start Exam
                    </button>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string | number }) {
  return (
    <div className="glass p-6 rounded-3xl flex items-center gap-5 border border-white/10">
      <div className="p-4 bg-zinc-800/50 rounded-2xl ring-1 ring-white/5">
        {icon}
      </div>
      <div>
        <p className="text-sm text-zinc-400 mb-1">{label}</p>
        <p className="text-2xl font-bold font-outfit text-white">{value}</p>
      </div>
    </div>
  );
}
