"use client";

import React, { useState, useEffect, useRef } from "react";
import { ChevronRight, Check } from "lucide-react";

export default function IntelligenceStickySection() {
  const [activeTab, setActiveTab] = useState<"realm" | "cortex">("realm");
  const realmRef = useRef<HTMLDivElement>(null);
  const cortexRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleScroll = () => {
      if (!cortexRef.current) return;
      const cortexRect = cortexRef.current.getBoundingClientRect();
      // If cortex top is in upper-mid viewport, switch to cortex
      if (cortexRect.top <= window.innerHeight * 0.5) {
        setActiveTab("cortex");
      } else {
        setActiveTab("realm");
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <section id="intelligence" className="relative w-full bg-black py-24 sm:py-36 px-6 sm:px-12 select-none">
      
      {/* ── Section Title: Centered, Minimal, Exactly as in Screenshot 2 ── */}
      <div className="max-w-4xl mx-auto text-center mb-24 sm:mb-32">
        <h2
          className="text-white font-bold tracking-tight leading-[1.12]"
          style={{ fontSize: "clamp(34px, 5vw, 62px)" }}
        >
          next-hour Intelligence
        </h2>
        <p className="mt-4 sm:mt-5 text-white/70 text-[15px] sm:text-[17px] leading-[1.6] max-w-2xl mx-auto font-normal">
          We&apos;re building the infrastructure for advancing intelligence through expert human data,
          real-world training environments, and contextual evaluations
        </p>
      </div>

      {/* ── Sticky Split: Left text scrolls, Right 3D card stays stuck ── */}
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-start">
          
          {/* ────── Left Column: Very Less Text (Screenshot 2 & 3) ────── */}
          <div className="lg:col-span-5 flex flex-col gap-40 sm:gap-56 py-6">
            
            {/* 1. Realm > */}
            <div
              ref={realmRef}
              onClick={() => setActiveTab("realm")}
              className={`cursor-pointer transition-opacity duration-300 ${
                activeTab === "realm" ? "opacity-100" : "opacity-35 hover:opacity-60"
              }`}
            >
              <div className="flex items-center gap-1.5 mb-3 group">
                <h3 className="text-white font-bold text-2xl sm:text-3xl tracking-tight">
                  Realm
                </h3>
                <ChevronRight className="w-6 h-6 text-white/70 stroke-[2] group-hover:translate-x-1 transition-transform" />
              </div>
              <p className="text-white/70 text-[15px] sm:text-[16px] leading-[1.65] font-normal max-w-sm">
                RL environments that mirror real-world scenarios to generate world-class human data
                for agentic actions and elevate model reasoning
              </p>
            </div>

            {/* 2. Cortex > */}
            <div
              ref={cortexRef}
              onClick={() => setActiveTab("cortex")}
              className={`cursor-pointer transition-opacity duration-300 ${
                activeTab === "cortex" ? "opacity-100" : "opacity-35 hover:opacity-60"
              }`}
            >
              <div className="flex items-center gap-1.5 mb-3 group">
                <h3 className="text-white font-bold text-2xl sm:text-3xl tracking-tight">
                  Cortex
                </h3>
                <ChevronRight className="w-6 h-6 text-white/70 stroke-[2] group-hover:translate-x-1 transition-transform" />
              </div>
              <p className="text-white/70 text-[15px] sm:text-[16px] leading-[1.65] font-normal max-w-sm">
                Continuous real-world sensor telemetry and contextual evaluation environments
                to validate runtime agent actions without chronological leakage
              </p>
            </div>

          </div>

          {/* ────── Right Column: STICKY 3D Metallic Device (Screenshot 2 & 3) ────── */}
          <div className="lg:col-span-7 sticky top-28 sm:top-32 z-20">
            <div className="relative w-full max-w-[500px] mx-auto">
              
              {/* 3D Isometric Tilt wrapper */}
              <div
                className="transition-all duration-500 ease-out"
                style={{
                  transform: "perspective(1000px) rotateX(18deg) rotateY(-12deg) rotateZ(4deg)",
                  transformStyle: "preserve-3d",
                }}
              >
                
                {/* ── CARD 1: Realm Visual (Matches Screenshot 2) ── */}
                {activeTab === "realm" && (
                  <div className="bg-[#18191f] border border-white/15 rounded-2xl p-4 sm:p-5 shadow-[-20px_30px_60px_rgba(0,0,0,0.85)] animate-in fade-in duration-300">
                    {/* Top bar inside card */}
                    <div className="flex items-center justify-between pb-3 mb-3 border-b border-white/10 text-[11px] font-medium text-white/70">
                      <span>next-hour RL environment</span>
                      <span className="flex items-center gap-1 text-white">
                        29.9% <ChevronRight className="w-3 h-3 text-white/50" />
                      </span>
                    </div>

                    {/* 3 Model Inset Rows (Screenshot 2) */}
                    <div className="space-y-2">
                      {/* GPT-5.5 / Model 1 */}
                      <div className="bg-[#24262f] border border-white/10 rounded-xl px-3.5 py-2.5 flex items-center justify-between">
                        <div className="flex items-center gap-2.5">
                          <div className="w-6 h-6 rounded-full bg-white/10 flex items-center justify-center text-[11px]">
                            ⚡
                          </div>
                          <span className="text-[13px] font-medium text-white">GPT-5.5</span>
                        </div>
                        <span className="flex items-center gap-1 text-[12px] text-white/80 font-mono">
                          27.02% <ChevronRight className="w-3 h-3 text-white/40" />
                        </span>
                      </div>

                      {/* Claude Opus 4.7 / Model 2 */}
                      <div className="bg-[#24262f] border border-white/10 rounded-xl px-3.5 py-2.5 flex items-center justify-between">
                        <div className="flex items-center gap-2.5">
                          <div className="w-6 h-6 rounded-full bg-[#d97706]/20 text-[#fb923c] flex items-center justify-center text-[11px]">
                            ✳
                          </div>
                          <span className="text-[13px] font-medium text-white">Claude Opus 4.7</span>
                        </div>
                        <span className="flex items-center gap-1 text-[12px] text-white/80 font-mono">
                          26.8% <ChevronRight className="w-3 h-3 text-white/40" />
                        </span>
                      </div>

                      {/* Gemini 3.1 Pro / Model 3 */}
                      <div className="bg-[#24262f] border border-white/10 rounded-xl px-3.5 py-2.5 flex items-center justify-between">
                        <div className="flex items-center gap-2.5">
                          <div className="w-6 h-6 rounded-full bg-sky-500/20 text-sky-400 flex items-center justify-center text-[11px]">
                            ✦
                          </div>
                          <span className="text-[13px] font-medium text-white">Gemini 3.1 Pro</span>
                        </div>
                        <span className="flex items-center gap-1 text-[12px] text-white/80 font-mono">
                          24.5% <ChevronRight className="w-3 h-3 text-white/40" />
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* ── CARD 2: Cortex Visual (Matches Screenshot 3) ── */}
                {activeTab === "cortex" && (
                  <div className="bg-[#18191f] border border-white/15 rounded-2xl p-4 sm:p-5 shadow-[-20px_30px_60px_rgba(0,0,0,0.85)] animate-in fade-in duration-300">
                    {/* Header: Run details (Screenshot 3) */}
                    <div className="pb-3 mb-3 border-b border-white/10">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-[13px] font-bold text-white tracking-tight">Run details</span>
                        <span className="text-[10px] text-white/50 font-mono">#cortex-0129</span>
                      </div>
                      
                      {/* Pill tags */}
                      <div className="flex flex-wrap items-center gap-1.5 text-[10px] text-white/70">
                        <span className="bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-md border border-emerald-500/30">
                          Screenshot
                        </span>
                        <span className="bg-white/5 px-2 py-0.5 rounded-md border border-white/10">
                          Result: 26.8%
                        </span>
                        <span className="bg-white/5 px-2 py-0.5 rounded-md border border-white/10">
                          Agent: opencode
                        </span>
                        <span className="bg-white/5 px-2 py-0.5 rounded-md border border-white/10 truncate max-w-[130px]">
                          google/gemini-3.1-pro
                        </span>
                      </div>
                    </div>

                    {/* Metrics bar */}
                    <div className="bg-[#24262f] border border-white/10 rounded-xl p-3 mb-2.5 grid grid-cols-3 gap-2 text-[10px] text-white/60">
                      <div>
                        <span className="block text-white/40">Result</span>
                        <span className="text-[13px] font-bold text-white">26.8%</span>
                      </div>
                      <div>
                        <span className="block text-white/40">Duration</span>
                        <span className="text-[13px] font-bold text-white">9 min 20s</span>
                      </div>
                      <div>
                        <span className="block text-white/40">Tool calls</span>
                        <span className="text-[13px] font-bold text-white">58</span>
                      </div>
                    </div>

                    {/* Status pill: Completed with 12 tasks (Screenshot 3) */}
                    <div className="bg-emerald-950/40 border border-emerald-500/30 text-emerald-400 text-[11px] font-medium px-3 py-1.5 rounded-lg flex items-center justify-between mb-2.5">
                      <span>Completed with 12 tasks</span>
                      <Check className="w-3.5 h-3.5" />
                    </div>

                    {/* Bottom verification pill (Screenshot 3) */}
                    <div className="bg-[#101115] border border-white/10 rounded-lg px-3 py-1.5 flex items-center justify-between text-[10px] text-white/50 font-mono">
                      <span className="text-emerald-400 font-semibold">10 passed • 0 fail</span>
                      <span>19 Criteria</span>
                    </div>
                  </div>
                )}

              </div>

            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
