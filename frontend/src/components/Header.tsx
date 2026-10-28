"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ChevronDown, ChevronRight, Menu, X } from "lucide-react";

export default function Header() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [intelligenceOpen, setIntelligenceOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 60) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <>
      {/* ─────────────────────────────────────────────────────────────
          1. HERO INLINE HEADER (100% Transparent Background - Screenshot 1)
          ───────────────────────────────────────────────────────────── */}
      <header
        className={`w-full absolute top-0 left-0 right-0 z-40 px-6 sm:px-12 pt-8 sm:pt-10 transition-opacity duration-300 bg-transparent ${
          isScrolled ? "opacity-0 pointer-events-none" : "opacity-100"
        }`}
        aria-hidden={isScrolled}
      >
        <div className="max-w-[1400px] mx-auto flex items-start justify-between bg-transparent">
          
          {/* Top-Left: Exactly 4 Stacked Links (Screenshot 1) */}
          <nav className="hidden sm:flex flex-col gap-1 text-[13px] font-normal text-white/80 bg-transparent">
            <div
              className="relative bg-transparent"
              onMouseEnter={() => setIntelligenceOpen(true)}
              onMouseLeave={() => setIntelligenceOpen(false)}
            >
              <button
                type="button"
                onClick={() => setIntelligenceOpen(!intelligenceOpen)}
                className="flex items-center gap-1.5 hover:text-white transition-colors cursor-pointer py-0.5 bg-transparent"
              >
                <span>Intelligence</span>
                <ChevronDown className="w-3 h-3 text-white/60" />
              </button>

              {/* Minimal Dropdown */}
              {intelligenceOpen && (
                <div className="absolute left-0 top-full pt-1.5 z-50 w-56 animate-in fade-in duration-150">
                  <div className="bg-[#121318]/95 backdrop-blur-xl border border-white/10 rounded-xl p-2 shadow-2xl space-y-1">
                    <a
                      href="#intelligence"
                      onClick={() => setIntelligenceOpen(false)}
                      className="block px-3 py-1.5 text-[12.5px] text-white/80 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                    >
                      Realm Environments
                    </a>
                    <a
                      href="#intelligence"
                      onClick={() => setIntelligenceOpen(false)}
                      className="block px-3 py-1.5 text-[12.5px] text-white/80 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                    >
                      Cortex Telemetry
                    </a>
                    <a
                      href="#benchmarks"
                      onClick={() => setIntelligenceOpen(false)}
                      className="block px-3 py-1.5 text-[12.5px] text-white/80 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                    >
                      Model Evaluations
                    </a>
                  </div>
                </div>
              )}
            </div>

            <a href="#benchmarks" className="hover:text-white transition-colors py-0.5">
              Research
            </a>
            <a href="#telemetry" className="hover:text-white transition-colors py-0.5">
              Expert opportunities
            </a>
            <a href="#faq" className="hover:text-white transition-colors py-0.5">
              Data partnerships
            </a>
          </nav>

          {/* Mobile hamburger */}
          <button
            type="button"
            onClick={() => setMobileOpen(true)}
            className="sm:hidden text-white/80 p-1.5 bg-transparent"
            aria-label="Open menu"
          >
            <Menu className="w-6 h-6" />
          </button>

          {/* Top-Center: Clean Logo (Screenshot 1) */}
          <div className="text-center pt-0.5 bg-transparent">
            <Link
              href="/"
              className="text-white font-bold text-[22px] sm:text-[24px] tracking-tight hover:opacity-90 transition-opacity bg-transparent"
            >
              next-hour<span className="text-white">.</span>
            </Link>
          </div>

          {/* Top-Right: Button with rounded-[10px] & dark square [>] (Screenshot 1) */}
          <div className="bg-transparent">
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

        </div>
      </header>

      {/* ─────────────────────────────────────────────────────────────
          2. FLOATING NAVBAR (Appears smoothly on scroll - Screenshot 2)
          ───────────────────────────────────────────────────────────── */}
      <div
        className={`fixed top-4 left-0 right-0 z-50 flex justify-center px-4 transition-all duration-300 pointer-events-none ${
          isScrolled
            ? "opacity-100 translate-y-0"
            : "opacity-0 -translate-y-4"
        }`}
      >
        <nav
          className="pointer-events-auto bg-[#131418]/65 backdrop-blur-xl border border-white/10 rounded-2xl px-5 py-2 flex items-center justify-between gap-6 shadow-2xl max-w-fit mx-auto"
          aria-label="Floating Navigation"
        >
          {/* Logo */}
          <Link
            href="/"
            className="text-white font-bold text-[18px] tracking-tight shrink-0 pr-1"
          >
            nh<span className="text-white">.</span>
          </Link>

          {/* Center Links (Screenshot 2) */}
          <ul className="hidden md:flex items-center gap-6 text-[13px] text-white/80" role="list">
            <li>
              <a href="#intelligence" className="hover:text-white transition-colors">
                Intelligence
              </a>
            </li>
            <li>
              <a href="#benchmarks" className="hover:text-white transition-colors">
                Research
              </a>
            </li>
            <li>
              <a href="#telemetry" className="hover:text-white transition-colors">
                Expert opportunities
              </a>
            </li>
            <li>
              <a href="#faq" className="hover:text-white transition-colors">
                Data partnerships
              </a>
            </li>
          </ul>

          {/* Right Button (Screenshot 2: rounded-[10px] with [>]) */}
          <div className="flex items-center gap-2">
            <a
              href="#telemetry"
              className="
                group inline-flex items-center gap-2
                bg-white hover:bg-white/90 text-black
                text-[12.5px] font-medium
                pl-3.5 pr-1.5 py-1 rounded-[10px]
                transition-all duration-150 shrink-0
              "
            >
              <span>Get in touch</span>
              <span className="w-5 h-5 rounded-[5px] bg-[#0c0d10] text-white flex items-center justify-center text-[10px] group-hover:translate-x-0.5 transition-transform">
                <ChevronRight className="w-3 h-3 stroke-[2.5]" />
              </span>
            </a>

            <button
              type="button"
              onClick={() => setMobileOpen(true)}
              className="md:hidden text-white/80 p-1"
              aria-label="Open mobile menu"
            >
              <Menu className="w-5 h-5" />
            </button>
          </div>
        </nav>
      </div>

      {/* ─────────────────────────────────────────────────────────────
          3. MOBILE DRAWER
          ───────────────────────────────────────────────────────────── */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 flex flex-col justify-between bg-black/95 backdrop-blur-2xl p-6">
          <div className="flex items-center justify-between pb-6 border-b border-white/10">
            <span className="text-white font-bold text-[20px]">
              next-hour<span className="text-white">.</span>
            </span>
            <button
              type="button"
              onClick={() => setMobileOpen(false)}
              className="text-white/80 p-2"
              aria-label="Close menu"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          <nav className="flex flex-col gap-4 text-lg text-white/85">
            <a href="#intelligence" onClick={() => setMobileOpen(false)}>Intelligence</a>
            <a href="#benchmarks" onClick={() => setMobileOpen(false)}>Research</a>
            <a href="#telemetry" onClick={() => setMobileOpen(false)}>Expert opportunities</a>
            <a href="#faq" onClick={() => setMobileOpen(false)}>Data partnerships</a>
          </nav>

          <a
            href="#telemetry"
            onClick={() => setMobileOpen(false)}
            className="w-full flex items-center justify-center gap-2 bg-white text-black font-medium py-3 rounded-[10px]"
          >
            <span>Get in touch</span>
            <ChevronRight className="w-4 h-4" />
          </a>
        </div>
      )}
    </>
  );
}
