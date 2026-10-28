"use client";

import React from "react";

export default function MountainHeroBackground() {
  return (
    <div
      className="absolute inset-0 w-full h-full overflow-hidden pointer-events-none select-none z-0"
      aria-hidden="true"
    >
      {/* Sky twilight gradient: clean, natural dusky tone extending to the very top with NO dark overlay */}
      <div
        className="absolute inset-0 w-full h-full"
        style={{
          background: `
            radial-gradient(ellipse 100% 70% at 50% 45%, rgba(142, 120, 116, 0.4) 0%, rgba(98, 83, 86, 0.25) 50%, rgba(35, 30, 34, 0.1) 80%, rgba(10, 10, 12, 0.8) 100%),
            linear-gradient(180deg, #534c4f 0%, #63585b 25%, #7a6b6d 45%, #504246 65%, #181418 80%, #000000 100%)
          `,
        }}
      />

      {/* Atmospheric subtle grain */}
      <div className="absolute inset-0 opacity-[0.03] bg-[radial-gradient(#fff_1px,transparent_1px)] [background-size:16px_16px]" />

      {/* Vector Mountain Silhouette Layers matching Screenshot 1 */}
      <svg
        viewBox="0 0 1440 900"
        preserveAspectRatio="xMidYMax slice"
        className="absolute inset-0 w-full h-full object-cover"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="skyHaze" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#8d6e68" stopOpacity="0.35" />
            <stop offset="60%" stopColor="#4e3e42" stopOpacity="0.15" />
            <stop offset="100%" stopColor="#0a0a0d" stopOpacity="0" />
          </linearGradient>

          <linearGradient id="distantRidge" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#3d3337" />
            <stop offset="60%" stopColor="#251f24" />
            <stop offset="100%" stopColor="#120f14" />
          </linearGradient>

          <linearGradient id="midRidge" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#282227" />
            <stop offset="50%" stopColor="#1a161b" />
            <stop offset="100%" stopColor="#0a090b" />
          </linearGradient>

          <linearGradient id="foregroundRidge" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#1d191d" />
            <stop offset="40%" stopColor="#110f13" />
            <stop offset="100%" stopColor="#000000" />
          </linearGradient>

          <linearGradient id="cragHighlight" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="rgba(195, 160, 150, 0.22)" />
            <stop offset="100%" stopColor="rgba(0, 0, 0, 0)" />
          </linearGradient>
        </defs>

        {/* Ambient horizon haze band */}
        <rect x="0" y="320" width="1440" height="260" fill="url(#skyHaze)" />

        {/* Layer 1: Distant mountain ridge */}
        <path
          d="M0,580 
             L110,555 L240,568 L380,530 L490,545 L620,510 L730,525 L880,490 
             L980,515 L1090,485 L1210,510 L1340,490 L1440,515 
             L1440,900 L0,900 Z"
          fill="url(#distantRidge)"
          opacity="0.65"
        />

        {/* Mist layer 1 */}
        <path
          d="M0,610 Q360,570 720,600 T1440,580 L1440,680 L0,680 Z"
          fill="#47393d"
          opacity="0.18"
        />

        {/* Layer 2: Mid-range mountain peaks with sharp crags */}
        <path
          d="M0,640 
             L80,615 L170,630 L280,590 L390,620 L480,570 L510,560 L570,595 
             L680,550 L710,520 L760,545 L840,580 L920,535 L1020,570 
             L1130,530 L1240,575 L1350,540 L1440,585 
             L1440,900 L0,900 Z"
          fill="url(#midRidge)"
          opacity="0.85"
        />

        {/* Layer 3: Central Primary Mountain Peak (Screenshot 1) */}
        <path
          d="M340,680 
             L410,630 L470,610 L515,550 L535,530 L555,548 L580,575 
             L640,620 L710,650 L780,680 Z"
          fill="url(#cragHighlight)"
        />

        {/* Layer 4: Foreground dark jagged mountain ridge */}
        <path
          d="M0,690 
             L60,670 L130,685 L210,650 L270,665 L350,620 L420,645 
             L490,590 L520,545 L545,550 L580,610 L630,635 L700,595 
             L750,620 L830,580 L880,605 L950,570 L1040,610 L1120,580 
             L1210,625 L1290,590 L1380,635 L1440,615 
             L1440,900 L0,900 Z"
          fill="url(#foregroundRidge)"
        />

        {/* Mountain textured slopes / dark ridges */}
        <path
          d="M490,590 L520,545 L545,550 L560,590 L530,630 L490,590 Z"
          fill="#1f1a20"
          opacity="0.7"
        />
        <path
          d="M700,595 L725,570 L750,620 L715,640 Z"
          fill="#1c181d"
          opacity="0.6"
        />
        <path
          d="M830,580 L860,555 L880,605 L845,620 Z"
          fill="#1c181d"
          opacity="0.6"
        />

        {/* Lower foreground dark hill slope covering base */}
        <path
          d="M0,740 
             Q320,700 680,720 
             Q1080,740 1440,710 
             L1440,900 L0,900 Z"
          fill="#0a090c"
        />
      </svg>

      {/* Bottom fade to pure black */}
      <div
        className="absolute bottom-0 left-0 right-0 h-[320px] pointer-events-none"
        style={{
          background: "linear-gradient(to bottom, rgba(0,0,0,0) 0%, rgba(0,0,0,0.6) 50%, #000000 100%)",
        }}
      />
    </div>
  );
}
