"use client";

import React from "react";
import MountainHeroBackground from "./MountainHeroBackground";

export default function HeroSection() {
  return (
    <section
      id="overview"
      className="relative w-full min-h-screen flex items-center justify-center px-6 sm:px-10 overflow-hidden bg-black select-none"
    >
      {/* ── Mountain Dusk Backdrop matching Screenshot 1 ── */}
      <MountainHeroBackground />

      {/* ── Center Text: approx 6xl on md+ screens with exact line breaks ── */}
      <div className="relative z-10 max-w-5xl mx-auto w-full flex flex-col items-center text-center mt-12 sm:mt-16">
        <h1 className="font-bold text-white tracking-[-0.025em] text-3xl sm:text-5xl md:text-6xl leading-[1.12] text-center">
          <span className="block">Data lab to train</span>
          <span className="block">frontier models &</span>
          <span className="block">evaluate agents</span>
        </h1>
      </div>
    </section>
  );
}
