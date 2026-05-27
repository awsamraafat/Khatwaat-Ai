"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Users, FileQuestion, Activity, AlertTriangle, LogOut, TrendingDown } from "lucide-react";
import { useRouter } from "next/navigation";
import { ApiClient } from "@/lib/api";

export default function AdminDashboard() {
  const router = useRouter();
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    // Basic auth check
    const userData = localStorage.getItem("khatwaat_user");
    if (!userData) {
      router.push("/login");
      return;
    }
    const user = JSON.parse(userData);
    if (user.role !== "admin") {
      router.push("/dashboard");
      return;
    }

    // Load admin stats
    ApiClient.getAdminAnalytics().then(setStats).catch(console.error);
  }, [router]);

  const handleLogout = () => {
    ApiClient.logout();
    router.push("/login");
  };

  return (
    <div className="min-h-screen bg-background flex">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border glass-panel hidden md:flex flex-col relative z-20">
        <div className="p-6">
          <h2 className="text-2xl font-bold font-outfit text-white mb-2">Khatwaat</h2>
          <p className="text-xs text-red-400 uppercase tracking-wider font-semibold">Admin Panel</p>
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-4">
          <NavItem icon={<Activity size={20} />} label="System Overview" active />
          <NavItem icon={<Users size={20} />} label="Students" />
          <NavItem icon={<FileQuestion size={20} />} label="Question Bank" />
          <NavItem icon={<AlertTriangle size={20} />} label="Anti-Cheat Logs" />
        </nav>

        <div className="p-4 mt-auto border-t border-border">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors"
          >
            <LogOut size={16} /> Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8 overflow-y-auto">
        <h1 className="text-3xl font-bold font-outfit text-white mb-8">System Overview</h1>

        {/* Top Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <StatCard title="Total Students" value={stats?.total_students || 0} icon={<Users className="text-blue-400" />} />
          <StatCard title="Exams Completed" value={stats?.total_exams || 0} icon={<Activity className="text-emerald-400" />} />
          <StatCard title="Active Questions" value={stats?.total_questions || 0} icon={<FileQuestion className="text-purple-400" />} />
          <StatCard title="Cheating Alerts" value={stats?.cheating_alerts?.length || 0} icon={<AlertTriangle className="text-red-400" />} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Hardest Questions */}
          <div className="glass p-6 rounded-3xl border border-white/10">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
              <TrendingDown className="text-rose-400" /> Hardest Questions
            </h2>
            <div className="space-y-4">
              {(stats?.hardest_questions || []).slice(0, 5).map((q: any, i: number) => (
                <div key={i} className="bg-white/5 p-4 rounded-xl flex justify-between items-center">
                  <div className="max-w-[70%]">
                    <span className="text-xs text-primary mb-1 block">{q.subject_name}</span>
                    <p className="text-sm text-zinc-300 truncate">{q.question_text}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-zinc-500 block">Difficulty (b)</span>
                    <span className="font-bold text-rose-400">{q.irt_b.toFixed(2)}</span>
                  </div>
                </div>
              ))}
              {(!stats?.hardest_questions || stats.hardest_questions.length === 0) && (
                <p className="text-zinc-500 text-sm">No data available yet.</p>
              )}
            </div>
          </div>

          {/* Top Students */}
          <div className="glass p-6 rounded-3xl border border-white/10">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
              <Users className="text-emerald-400" /> Top Performing Students
            </h2>
            <div className="space-y-4">
              {(stats?.top_students || []).slice(0, 5).map((s: any, i: number) => (
                <div key={i} className="bg-white/5 p-4 rounded-xl flex justify-between items-center">
                  <div>
                    <span className="text-xs text-primary mb-1 block">{s.subject_name}</span>
                    <p className="text-sm text-zinc-300">User ID: {s.user_id.substring(0, 8)}...</p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-zinc-500 block">Theta Score</span>
                    <span className="font-bold text-emerald-400">+{s.final_theta.toFixed(2)}</span>
                  </div>
                </div>
              ))}
              {(!stats?.top_students || stats.top_students.length === 0) && (
                <p className="text-zinc-500 text-sm">No data available yet.</p>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function NavItem({ icon, label, active = false }: { icon: React.ReactNode; label: string; active?: boolean }) {
  return (
    <a href="#" className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${active ? "bg-red-500/10 text-red-400 font-medium" : "text-zinc-400 hover:text-white hover:bg-white/5"}`}>
      {icon}
      <span>{label}</span>
    </a>
  );
}

function StatCard({ title, value, icon }: { title: string; value: string | number; icon: React.ReactNode }) {
  return (
    <div className="glass p-6 rounded-2xl border border-white/10 flex items-center gap-4">
      <div className="p-4 bg-zinc-800/50 rounded-xl ring-1 ring-white/5">
        {icon}
      </div>
      <div>
        <p className="text-sm text-zinc-400">{title}</p>
        <p className="text-3xl font-bold text-white">{value}</p>
      </div>
    </div>
  );
}
