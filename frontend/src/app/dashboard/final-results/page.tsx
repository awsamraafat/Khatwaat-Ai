"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Sparkles, GraduationCap, Briefcase, ChevronRight, CheckCircle2, AlertTriangle, ArrowLeft, TrendingUp } from "lucide-react";
import { ApiClient } from "@/lib/api";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function FinalResultsPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const router = useRouter();

  useEffect(() => {
    async function fetchResults() {
      try {
        const res = await ApiClient.getRecommendations();
        setData(res);
      } catch (e: any) {
        setError(e.message || "Failed to load final results.");
      } finally {
        setLoading(false);
      }
    }
    fetchResults();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center space-y-4">
        <div className="w-12 h-12 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
        <p className="text-muted-foreground animate-pulse font-medium">Analyzing your full assessment profile...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen p-8 flex flex-col items-center justify-center">
        <div className="glass p-8 rounded-3xl max-w-md text-center">
          <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-white mb-2">Results Unavailable</h2>
          <p className="text-zinc-400 mb-6">{error || "No data returned."}</p>
          <button onClick={() => router.push("/dashboard")} className="bg-white/10 hover:bg-white/20 px-6 py-2 rounded-xl text-white">
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6 md:p-10 max-w-5xl mx-auto space-y-12">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-4"
      >
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-tr from-primary to-purple-500 mb-4 shadow-[0_0_40px_rgba(59,130,246,0.3)]">
          <Sparkles className="w-10 h-10 text-white" />
        </div>
        <h1 className="text-4xl md:text-5xl font-bold font-outfit text-white">Your AI Assessment Results</h1>
        <p className="text-lg text-zinc-400 max-w-2xl mx-auto">
          We've analyzed your performance across all subjects. Based on your cognitive profile and strengths, here is your personalized academic and career trajectory.
        </p>
      </motion.div>

      {/* Main Track Prediction */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
        className="glass rounded-[2rem] p-8 md:p-12 border border-primary/20 relative overflow-hidden"
      >
        <div className="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-primary/10 to-transparent pointer-events-none" />
        
        <div className="flex items-center gap-3 text-primary font-bold tracking-wider uppercase text-sm mb-4">
          <GraduationCap className="w-5 h-5" /> Predicted Academic Track
        </div>
        
        <h2 className="text-4xl md:text-5xl font-extrabold text-white mb-4">
          {data.predicted_track || "General Studies"}
        </h2>
        
        <div className="flex items-center gap-4 mb-8">
          <div className="bg-primary/20 text-primary border border-primary/30 px-4 py-1 rounded-full font-medium">
            {(data.track_confidence || 0) * 100}% Match
          </div>
          <p className="text-emerald-400 text-sm flex items-center gap-1"><CheckCircle2 className="w-4 h-4" /> Highly Confident</p>
        </div>
        
        <div className="bg-black/20 p-6 rounded-2xl border border-white/5">
          <h3 className="text-sm text-zinc-500 uppercase tracking-wider font-bold mb-2">AI Reasoning</h3>
          <p className="text-zinc-300 leading-relaxed text-lg">
            {data.track_details?.reasoning || "Based on your balanced performance, this track offers the highest probability of success."}
          </p>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Short Term */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="space-y-6"
        >
          <div className="flex items-center gap-3 text-2xl font-bold font-outfit text-white">
            <Briefcase className="w-6 h-6 text-purple-400" /> المسارات التعليمية للثانوية (Educational Tracks)
          </div>
          
          <div className="space-y-4">
            {data.short_term?.map((rec: any, idx: number) => (
              <div key={idx} className="glass p-6 rounded-2xl border border-white/5 hover:border-white/10 transition-colors">
                <div className="flex justify-between items-start gap-4 mb-2">
                  <h3 className="text-xl font-bold text-white flex items-center gap-2.5">
                    <span className="text-2xl filter drop-shadow-[0_0_10px_rgba(255,255,255,0.15)]">{rec.icon}</span>
                    <span>{rec.role || rec.path}</span>
                  </h3>
                  <span className="text-sm font-bold text-purple-400 bg-purple-500/10 px-3 py-1 rounded-full whitespace-nowrap">
                    {Math.round(rec.match_score * 100)}% Match
                  </span>
                </div>
                <p className="text-zinc-300 text-sm leading-relaxed">{rec.reason}</p>
              </div>
            ))}
            {(!data.short_term || data.short_term.length === 0) && (
              <div className="glass p-6 rounded-2xl text-zinc-500 text-center">No short-term data available.</div>
            )}
          </div>
        </motion.div>

        {/* Long Term */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="space-y-6"
        >
          <div className="flex items-center gap-3 text-2xl font-bold font-outfit text-white">
            <TrendingUp className="w-6 h-6 text-emerald-400" /> الكليات والاتجاهات الجامعية (University Placement)
          </div>
          
          <div className="space-y-4">
            {data.long_term?.map((rec: any, idx: number) => (
              <div key={idx} className="glass p-6 rounded-2xl border border-white/5 hover:border-white/10 transition-colors">
                <div className="flex justify-between items-start gap-4 mb-2">
                  <h3 className="text-xl font-bold text-white flex items-center gap-2.5">
                    <span className="text-2xl filter drop-shadow-[0_0_10px_rgba(255,255,255,0.15)]">{rec.icon}</span>
                    <span>{rec.role || rec.path}</span>
                  </h3>
                  <span className="text-sm font-bold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full whitespace-nowrap">
                    {Math.round(rec.match_score * 100)}% Match
                  </span>
                </div>
                <p className="text-zinc-300 text-sm leading-relaxed">{rec.reason}</p>
              </div>
            ))}
             {(!data.long_term || data.long_term.length === 0) && (
              <div className="glass p-6 rounded-2xl text-zinc-500 text-center">No long-term data available.</div>
            )}
          </div>
        </motion.div>
      </div>

      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="flex justify-center pt-8"
      >
        <Link href="/dashboard" className="text-zinc-400 hover:text-white flex items-center gap-2 transition-colors px-6 py-3 rounded-full hover:bg-white/5">
          <ArrowLeft className="w-4 h-4" /> Return to Dashboard
        </Link>
      </motion.div>
    </div>
  );
}
