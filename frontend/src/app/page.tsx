import React from "react";
import Header from "@/components/Header";
import HeroSection from "@/components/HeroSection";
import IntelligenceStickySection from "@/components/IntelligenceStickySection";
import KeyFeaturesSection from "@/components/KeyFeaturesSection";
import DeviceSecuritySection from "@/components/DeviceSecuritySection";
import BenefitSection from "@/components/BenefitSection";
import FAQSection from "@/components/FAQSection";
import CTAFooterSection from "@/components/CTAFooterSection";

export default function Home() {
  return (
    <div className="min-h-screen bg-black text-[#f8fafc] selection:bg-white/20 selection:text-white">
      {/* ─── Accessible Skip Link ─── */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      {/* ─── Header: Hero top navigation + Floating Pill on scroll ─── */}
      <Header />

      <main id="main-content">
        {/* ─── 1. Hero: Mountain dusk backdrop + big centered headline ─── */}
        <HeroSection />

        {/* ─── 2. Intelligence: Sticky 3D Showcase (Micro1 style) ─── */}
        <IntelligenceStickySection />

        {/* ─── 3. Machine Learning Pipeline & Benchmarks ─── */}
        <KeyFeaturesSection />

        {/* ─── 4. Live Telemetry: Phone interface + kilowatt analysis ─── */}
        <DeviceSecuritySection />

        {/* ─── 5. Core Benefits: For Households & Facility Teams ─── */}
        <BenefitSection />

        {/* ─── 6. FAQ: Quick Answers, Clear Solutions ─── */}
        <FAQSection />

        {/* ─── 7. CTA Banner & Minimalist Footer ─── */}
        <CTAFooterSection />
      </main>
    </div>
  );
}
