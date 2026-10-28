"use client";

import React, { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

const FAQS = [
  {
    question: "What does this AI model actually predict?",
    answer:
      "It predicts active power (measured in kilowatts, kW) for upcoming intervals by analyzing recent power load and cyclic clock time.",
  },
  {
    question: "What features and sensors are used for training?",
    answer:
      "Input features include lagged active power, hour, minute, and day of week, alongside voltage, global intensity, and circuit sub-metering.",
  },
  {
    question: "How do you prevent data leakage in time-series forecasting?",
    answer:
      "We strictly use chronological train, validation, and test splits (60% / 20% / 20%) without shuffling so future data never leaks into models.",
  },
  {
    question: "Which machine learning models are benchmarked?",
    answer:
      "Random Forest regressors, Decision Trees, and Linear Regression are evaluated against persistence baselines using MAE and RMSE.",
  },
  {
    question: "How can I integrate the prediction API?",
    answer:
      "A fast Python FastAPI service provides GET /health, GET /model-info, and POST /predict for smart meter and IoT telemetry payloads.",
  },
];

export default function FAQSection() {
  const [openIndex, setOpenIndex] = useState<number>(0);

  return (
    <section id="faq" className="w-full bg-black py-20 sm:py-28 px-6 sm:px-12 border-t border-white/8 select-none">
      <div className="max-w-3xl mx-auto">
        
        {/* Header */}
        <div className="text-center mb-12 sm:mb-14">
          <h2 className="text-white font-bold text-3xl sm:text-4xl tracking-tight">
            Frequently Asked Questions
          </h2>
        </div>

        {/* Accordion list with rounded-2xl */}
        <div className="flex flex-col gap-3">
          {FAQS.map((faq, i) => {
            const isOpen = openIndex === i;
            return (
              <div
                key={faq.question}
                className={`border rounded-2xl transition-all duration-200 overflow-hidden ${
                  isOpen
                    ? "bg-[#14151a] border-white/20 p-5 sm:p-6"
                    : "bg-[#0f1014] border-white/8 hover:border-white/15 p-4 sm:p-5"
                }`}
              >
                <button
                  type="button"
                  onClick={() => setOpenIndex(isOpen ? -1 : i)}
                  className="w-full flex items-center justify-between gap-4 text-left cursor-pointer"
                  aria-expanded={isOpen}
                >
                  <span className="text-[15px] sm:text-[16px] font-medium text-white">
                    {faq.question}
                  </span>
                  <span className="text-white/60 shrink-0">
                    {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </span>
                </button>

                {isOpen && (
                  <p className="mt-3 pt-3 border-t border-white/8 text-white/60 text-[14px] leading-[1.6]">
                    {faq.answer}
                  </p>
                )}
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
}
