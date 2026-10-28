"use client";

import React from "react";
import { Home, Building2, ChevronRight } from "lucide-react";

export default function BenefitSection() {
  return (
    <section id="benefits" className="w-full bg-black py-20 sm:py-28 px-6 sm:px-12 border-t border-white/8 select-none">
      <div className="max-w-5xl mx-auto">
        
        {/* Header: Short, minimal */}
        <div className="text-center mb-14 sm:mb-16">
          <h2 className="text-white font-bold text-3xl sm:text-4xl tracking-tight">
            Why Energy Intelligence Matters
          </h2>
          <p className="mt-3 text-white/60 text-[15px] max-w-lg mx-auto font-normal">
            Real-time machine learning predictions tailored for cost reduction and grid optimization.
          </p>
        </div>

        {/* Two cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Card 1 */}
          <div className="bg-[#121318] border border-white/10 rounded-2xl p-7 flex flex-col justify-between min-h-[300px]">
            <div>
              <div className="w-9 h-9 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center text-white mb-5">
                <Home className="w-4 h-4" />
              </div>
              <h3 className="text-white font-bold text-xl tracking-tight mb-2">
                For Households
              </h3>
              <p className="text-white/60 text-[14px] leading-[1.6]">
                Understand power consumption as it happens. Receive alerts before peak tariff
                hours and reduce everyday electricity bills.
              </p>
            </div>
            <div className="pt-6">
              <a
                href="#telemetry"
                className="inline-flex items-center gap-1.5 text-[13px] font-medium text-white hover:text-white/80 transition-colors"
              >
                <span>Explore household tools</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>

          {/* Card 2 */}
          <div className="bg-[#121318] border border-white/10 rounded-2xl p-7 flex flex-col justify-between min-h-[300px]">
            <div>
              <div className="w-9 h-9 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center text-white mb-5">
                <Building2 className="w-4 h-4" />
              </div>
              <h3 className="text-white font-bold text-xl tracking-tight mb-2">
                For Energy Teams
              </h3>
              <p className="text-white/60 text-[14px] leading-[1.6]">
                Monitor multi-circuit sub-metering, predict load surges, and integrate automated
                dispatch rules into your building management systems.
              </p>
            </div>
            <div className="pt-6">
              <a
                href="#telemetry"
                className="inline-flex items-center gap-1.5 text-[13px] font-medium text-white hover:text-white/80 transition-colors"
              >
                <span>Inspect API integration</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
