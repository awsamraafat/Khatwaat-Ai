"use client";

import { motion } from "framer-motion";
import { ArrowRight, Brain, Zap, Shield, Target } from "lucide-react";
import Link from "next/link";

export default function Home() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring" as const,
        stiffness: 100,
      },
    },
  };

  return (
    <main className="min-h-screen relative overflow-hidden flex flex-col items-center justify-center p-6 pt-24 md:p-24">
      {/* Background decoration elements */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-[128px] -z-10" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-[128px] -z-10" />

      <motion.div
        className="max-w-5xl mx-auto w-full z-10 flex flex-col items-center text-center"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div variants={itemVariants} className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-8 text-sm text-primary-foreground/80 font-medium">
          <Brain className="w-4 h-4 text-primary" />
          <span>Powered by 3PL Item Response Theory</span>
        </motion.div>

        <motion.h1
          variants={itemVariants}
          className="font-outfit text-5xl md:text-7xl font-bold tracking-tight mb-6 bg-gradient-to-br from-white to-white/60 bg-clip-text text-transparent"
        >
          Adaptive AI <br className="hidden md:block" />
          Assessment Platform
        </motion.h1>

        <motion.p
          variants={itemVariants}
          className="text-lg md:text-xl text-muted-foreground max-w-2xl mb-12"
        >
          Next-generation testing that adapts to your true ability in real-time. 
          Discover your strengths, get personalized career tracks, and learn faster.
        </motion.p>

        <motion.div variants={itemVariants} className="flex flex-col sm:flex-row gap-4 w-full justify-center">
          <Link
            href="/login"
            className="group relative inline-flex h-14 items-center justify-center overflow-hidden rounded-full bg-primary px-8 font-medium text-primary-foreground transition-transform hover:scale-105 active:scale-95"
          >
            <span className="mr-2">Start Assessment</span>
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </Link>
          <Link
            href="/admin"
            className="group inline-flex h-14 items-center justify-center rounded-full glass px-8 font-medium text-foreground transition-all hover:bg-white/10"
          >
            Admin Dashboard
          </Link>
        </motion.div>

        {/* Features Grid */}
        <motion.div
          variants={containerVariants}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-24 w-full"
        >
          <FeatureCard
            icon={<Target className="w-6 h-6 text-blue-400" />}
            title="Precision Targeting"
            description="Our CAT engine hones in on your exact ability level using advanced mathematical models, cutting exam time in half."
          />
          <FeatureCard
            icon={<Zap className="w-6 h-6 text-purple-400" />}
            title="Real-Time Analytics"
            description="Watch your Theta score update dynamically as you answer questions. Instantly discover your strengths and weaknesses."
          />
          <FeatureCard
            icon={<Shield className="w-6 h-6 text-emerald-400" />}
            title="AI Proctoring"
            description="Advanced behavioral analysis detects suspicious patterns and safeguards exam integrity seamlessly in the background."
          />
        </motion.div>
      </motion.div>
    </main>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <motion.div
      variants={{
        hidden: { y: 20, opacity: 0 },
        visible: { y: 0, opacity: 1 },
      }}
      className="glass p-8 rounded-3xl flex flex-col items-start text-left hover-lift border-t border-white/20"
    >
      <div className="p-3 bg-white/5 rounded-2xl mb-6 ring-1 ring-white/10">
        {icon}
      </div>
      <h3 className="font-outfit text-xl font-semibold mb-3 text-white">{title}</h3>
      <p className="text-muted-foreground leading-relaxed">{description}</p>
    </motion.div>
  );
}
