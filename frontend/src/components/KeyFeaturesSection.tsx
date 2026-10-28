"use client";

import React from "react";
import { Database, LineChart, Code, ChevronRight } from "lucide-react";

export default function KeyFeaturesSection() {
  return (
    <section id="benchmarks" className="w-full bg-black py-20 sm:py-28 px-6 sm:px-12 border-t border-white/8 select-none">
      <div className="max-w-5xl mx-auto">
        
        {/* Header: Short, minimal */}
        <div className="text-center mb-14 sm:mb-16">
          <h2 className="text-white font-bold text-3xl sm:text-4xl tracking-tight">
            Benchmarked on Real Telemetry
          </h2>
          <p className="mt-3 text-white/60 text-[15px] max-w-lg mx-auto font-normal">
            Evaluated against chronological test windows with MAE and RMSE error metrics.
          </p>
        </div>

        {/* 3 cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Card 1 */}
          <div className="bg-[#121318] border border-white/10 rounded-2xl p-6 flex flex-col justify-between">
            <div>
              <div className="w-8 h-8 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center text-white mb-4">
                <Database className="w-4 h-4" />
              </div>
              <h3 className="text-white font-bold text-lg tracking-tight mb-2">
                Feature Engineering
              </h3>
              <p className="text-white/60 text-[13.5px] leading-[1.6]">
                Hour, minute, and day-of-week cyclic signals alongside lagged active power readings with zero forward leakage.
              </p>
            </div>
            <div className="pt-6 border-t border-white/8 mt-6 flex justify-between text-[11px] font-mono text-white/50">
              <span>Chrono Split</span>
              <span className="text-white">60/20/20</span>
            </div>
          </div>

          {/* Card 2 */}
          <div className="bg-[#121318] border border-white/10 rounded-2xl p-6 flex flex-col justify-between">
            <div>
              <div className="w-8 h-8 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center text-white mb-4">
                <LineChart className="w-4 h-4" />
              </div>
              <h3 className="text-white font-bold text-lg tracking-tight mb-2">
                Tree Regressors
              </h3>
              <p className="text-white/60 text-[13.5px] leading-[1.6]">
                Comparing Random Forests, Decision Trees, and Linear Regressors against persistence baseline models.
              </p>
            </div>
            <div className="pt-6 border-t border-white/8 mt-6 flex justify-between text-[11px] font-mono text-white/50">
              <span>Best MAE</span>
              <span className="text-emerald-400 font-semibold">0.16 kW</span>
            </div>
          </div>

          {/* Card 3 */}
          <div className="bg-[#121318] border border-white/10 rounded-2xl p-6 flex flex-col justify-between">
            <div>
              <div className="w-8 h-8 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center text-white mb-4">
                <Code className="w-4 h-4" />
              </div>
              <h3 className="text-white font-bold text-lg tracking-tight mb-2">
                FastAPI Serving
              </h3>
              <p className="text-white/60 text-[13.5px] leading-[1.6]">
                Sub-50ms inference endpoints, liveness diagnostics, and Pydantic-guarded interfaces for smart meters.
              </p>
            </div>
            <div className="pt-6 border-t border-white/8 mt-6 flex justify-between text-[11px] font-mono text-white/50">
              <span>Latency</span>
              <span className="text-sky-400 font-semibold">11.4 ms</span>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
