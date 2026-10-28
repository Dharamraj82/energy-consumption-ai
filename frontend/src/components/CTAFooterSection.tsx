"use client";

import React from "react";
import Link from "next/link";
import { ChevronRight } from "lucide-react";

const FOOTER_NAV = [
  { label: "Intelligence", href: "#intelligence" },
  { label: "Research", href: "#benchmarks" },
  { label: "Expert opportunities", href: "#telemetry" },
  { label: "Data partnerships", href: "#faq" },
];

export default function CTAFooterSection() {
  return (
    <section className="w-full bg-black px-6 sm:px-12 pt-10 pb-10 border-t border-white/8 select-none">
      <div className="max-w-5xl mx-auto flex flex-col gap-10">
        
        {/* Minimal CTA Banner with rounded-2xl */}
        <div className="relative bg-[#121318] border border-white/10 rounded-2xl p-8 sm:p-14 text-center overflow-hidden">
          <h2 className="text-white font-bold text-2xl sm:text-4xl tracking-tight mb-3">
            Start Predicting Energy Demand
          </h2>
          <p className="text-white/60 text-[15px] max-w-md mx-auto mb-6">
            Integrate Next-Hour models into your smart meters and building management systems.
          </p>
          <a
            href="#telemetry"
            className="
              group inline-flex items-center gap-2.5
              bg-white hover:bg-white/90 text-black
              text-[13px] font-medium
              pl-4 pr-1.5 py-1.5 rounded-[10px]
              transition-all duration-150
            "
          >
            <span>Get in touch</span>
            <span className="w-6 h-6 rounded-[6px] bg-[#0c0d10] text-white flex items-center justify-center text-[12px] group-hover:translate-x-0.5 transition-transform">
              <ChevronRight className="w-3.5 h-3.5 stroke-[2.5]" />
            </span>
          </a>
        </div>

        {/* Minimal Footer matching micro1 */}
        <footer className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 text-[12px] text-white/50">
          <div className="flex items-center gap-2">
            <span className="text-white font-bold text-base">next-hour<span className="text-white">.</span></span>
            <span>© 2026 Next-Hour AI Lab</span>
          </div>

          <nav className="flex items-center gap-6">
            {FOOTER_NAV.map((item) => (
              <a
                key={item.label}
                href={item.href}
                className="hover:text-white transition-colors"
              >
                {item.label}
              </a>
            ))}
          </nav>
        </footer>

      </div>
    </section>
  );
}
