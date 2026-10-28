"use client";

import React from "react";
import { ChevronRight } from "lucide-react";

export default function DeviceSecuritySection() {
  return (
    <section id="telemetry" className="w-full bg-black py-20 sm:py-28 px-6 sm:px-12 border-t border-white/8 select-none">
      <div className="max-w-5xl mx-auto">
        
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-14 items-center">
          
          {/* Left: Clean Obsidian Phone Widget */}
          <div className="lg:col-span-5 flex justify-center">
            <div className="w-full max-w-[320px] bg-[#121318] border border-white/15 rounded-2xl p-5 shadow-2xl">
              <div className="flex items-center justify-between text-[11px] text-white/50 pb-3 border-b border-white/10">
                <span className="font-mono">17:24</span>
                <span className="text-emerald-400 font-semibold flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  LIVE
                </span>
              </div>

              <div className="py-4">
                <span className="text-[11px] text-white/40 block font-mono">Meter #01 • Forecast</span>
                <div className="flex items-baseline gap-2 mt-1">
                  <span className="text-3xl font-bold font-mono text-white">4.21</span>
                  <span className="text-sm font-mono text-white/60">kW</span>
                </div>
              </div>

              {/* 4 Telemetry pills */}
              <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
                <div className="bg-black/40 border border-white/8 rounded-xl p-2.5">
                  <span className="text-white/40 block">Voltage</span>
                  <span className="text-white font-semibold">234.8 V</span>
                </div>
                <div className="bg-black/40 border border-white/8 rounded-xl p-2.5">
                  <span className="text-white/40 block">Intensity</span>
                  <span className="text-white font-semibold">18.4 A</span>
                </div>
                <div className="bg-black/40 border border-white/8 rounded-xl p-2.5">
                  <span className="text-white/40 block">Reactive</span>
                  <span className="text-white font-semibold">0.41 kvar</span>
                </div>
                <div className="bg-black/40 border border-white/8 rounded-xl p-2.5">
                  <span className="text-white/40 block">Interval</span>
                  <span className="text-emerald-400 font-semibold">1-Minute</span>
                </div>
              </div>
            </div>
          </div>

          {/* Right: Very Less Text */}
          <div className="lg:col-span-7 flex flex-col justify-center">
            <h3 className="text-white font-bold text-2xl sm:text-3xl tracking-tight mb-4">
              Take Control of Energy Peaks
            </h3>
            <p className="text-white/70 text-[15px] sm:text-[16px] leading-[1.65] mb-6 font-normal">
              Our machine learning models analyze previous active power and clock time intervals
              to forecast electrical demand and eliminate utility spikes.
            </p>

            <div>
              <a
                href="#intelligence"
                className="
                  group inline-flex items-center gap-2
                  bg-white hover:bg-white/90 text-black
                  text-[13px] font-medium
                  pl-4 pr-1.5 py-1.5 rounded-[10px]
                  transition-all duration-150
                "
              >
                <span>Inspect feature logic</span>
                <span className="w-6 h-6 rounded-[6px] bg-[#0c0d10] text-white flex items-center justify-center text-[12px] group-hover:translate-x-0.5 transition-transform">
                  <ChevronRight className="w-3.5 h-3.5 stroke-[2.5]" />
                </span>
              </a>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
