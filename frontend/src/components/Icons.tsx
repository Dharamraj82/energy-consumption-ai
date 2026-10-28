import React from "react";

/* ============================================================
   LockBox Brand Logo Mark (white caret + box outline)
   ============================================================ */
export function LockBoxLogo({ className = "w-7 h-7" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 36 36"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden="true"
    >
      {/* Rounded rect body */}
      <rect x="2" y="2" width="32" height="32" rx="8" fill="white" />
      {/* Bold left-pointing caret / chevron */}
      <path
        d="M21.5 11L14.5 18L21.5 25"
        stroke="#0254EC"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

/* ============================================================
   Apple Logo Icon
   ============================================================ */
export function AppleIcon({ className = "w-4 h-4" }: { className?: string }) {
  return (
    <svg viewBox="0 0 814 1000" fill="currentColor" xmlns="http://www.w3.org/2000/svg" className={className} aria-hidden="true">
      <path d="M788.1 340.9c-5.8 4.5-108.2 62.2-108.2 190.5 0 148.4 130.3 200.9 134.2 202.2-.6 3.2-20.7 71.9-68.7 141.9-42.8 61.6-87.5 123.1-155.5 123.1s-85.5-39.5-164-39.5c-76 0-103.7 40.8-165.9 40.8s-105-37.3-155.5-127.4C46.7 790.7 0 663 0 541.8c0-194.3 125.4-297.5 248.8-297.5 66.1 0 121.2 43.4 162.7 43.4 39.5 0 101.1-46 176.3-46 28.5 0 130.9 2.6 198.3 99.2zm-234-181.5c31.1-36.9 53.1-88.1 53.1-139.3 0-7.1-.6-14.3-1.9-20.1-50.6 1.9-110.8 33.7-147.1 75.8-28.5 32.4-55.1 83.6-55.1 135.5 0 7.8 1.3 15.6 1.9 18.1 3.2.6 8.4 1.3 13.6 1.3 45.4 0 102.5-30.4 135.5-71.3z"/>
    </svg>
  );
}

/* ============================================================
   Isometric 3D Folder / App Icon (next to "Manage" in headline)
   Matches the small app screenshot sticker in the design
   ============================================================ */
export function AppSticker({ className = "w-14 h-14" }: { className?: string }) {
  return (
    <span
      className={`inline-flex items-center justify-center ${className} rounded-2xl bg-white border border-slate-200 shadow-lg overflow-hidden`}
      style={{ boxShadow: "0 8px 24px -4px rgba(0,0,0,0.12), 0 2px 6px -1px rgba(0,0,0,0.06)" }}
    >
      <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full p-0.5">
        {/* Browser window chrome bar */}
        <rect x="4" y="4" width="56" height="56" rx="12" fill="#F1F5F9" />
        {/* Top bar */}
        <rect x="4" y="4" width="56" height="16" rx="12" fill="#334155" />
        <rect x="4" y="12" width="56" height="8" fill="#334155" />
        {/* Window dots */}
        <circle cx="14" cy="12" r="2.5" fill="#EF4444" />
        <circle cx="22" cy="12" r="2.5" fill="#F59E0B" />
        <circle cx="30" cy="12" r="2.5" fill="#10B981" />
        {/* Screen / content area */}
        <rect x="8" y="22" width="48" height="34" rx="4" fill="#FFFFFF" />
        {/* Blue header strip inside screen */}
        <rect x="8" y="22" width="48" height="11" rx="4" fill="#0254EC" />
        <rect x="8" y="29" width="48" height="4" fill="#0254EC" />
        {/* Content lines */}
        <rect x="12" y="38" width="20" height="2.5" rx="1.25" fill="#CBD5E1" />
        <rect x="12" y="43" width="36" height="2.5" rx="1.25" fill="#E2E8F0" />
        <rect x="12" y="48" width="28" height="2.5" rx="1.25" fill="#E2E8F0" />
        {/* Yellow accent pill */}
        <rect x="12" y="53" width="14" height="4" rx="2" fill="#FEAC1F" />
      </svg>
    </span>
  );
}

/* ============================================================
   Google Drive Multicolor Logo
   ============================================================ */
export function GoogleDriveIcon({ className = "w-8 h-8" }: { className?: string }) {
  return (
    <svg viewBox="0 0 87.3 78" xmlns="http://www.w3.org/2000/svg" className={className} aria-label="Google Drive">
      <path d="m6.6 66.85 3.85 6.65c.8 1.4 1.95 2.5 3.3 3.3l13.75-23.8h-27.5c0 1.55.4 3.1 1.2 4.5z" fill="#0066da"/>
      <path d="m43.65 25-13.75-23.8c-1.35.8-2.5 1.9-3.3 3.3l-25.4 44c-.8 1.4-1.2 2.95-1.2 4.5h27.5z" fill="#00ac47"/>
      <path d="m73.55 76.8c1.35-.8 2.5-1.9 3.3-3.3l1.6-2.75 7.65-13.25c.8-1.4 1.2-2.95 1.2-4.5h-27.502l5.852 11.5z" fill="#ea4335"/>
      <path d="m43.65 25 13.75-23.8c-1.35-.8-2.9-1.2-4.5-1.2h-18.5c-1.6 0-3.15.45-4.5 1.2z" fill="#00832d"/>
      <path d="m59.8 53h-32.3l-13.75 23.8c1.35.8 2.9 1.2 4.5 1.2h50.8c1.6 0 3.15-.45 4.5-1.2z" fill="#2684fc"/>
      <path d="m73.4 26.5-12.7-22c-.8-1.4-1.95-2.5-3.3-3.3l-13.75 23.8 16.15 28h27.45c0-1.55-.4-3.1-1.2-4.5z" fill="#ffba00"/>
    </svg>
  );
}

/* ============================================================
   Zoom Blue Icon
   ============================================================ */
export function ZoomIcon({ className = "w-8 h-8" }: { className?: string }) {
  return (
    <span className={`inline-flex items-center justify-center bg-[#2D8CFF] rounded-xl ${className}`} aria-label="Zoom">
      <svg viewBox="0 0 24 24" fill="white" className="w-3/5 h-3/5">
        <path d="M4 8a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8zm14 2.5 3-2.25v7.5l-3-2.25v-3z" />
      </svg>
    </span>
  );
}

/* ============================================================
   Google Calendar Icon
   ============================================================ */
export function GoogleCalendarIcon({ className = "w-8 h-8" }: { className?: string }) {
  return (
    <span className={`inline-flex flex-col items-center justify-start overflow-hidden bg-white border-2 border-slate-200 rounded-xl ${className}`} aria-label="Google Calendar">
      <span className="w-full bg-[#1A73E8] h-2.5" />
      <span className="text-[13px] font-bold text-[#1A73E8] pt-0.5 leading-none">31</span>
    </span>
  );
}

/* ============================================================
   Google Meet Icon (for phone mockup)
   ============================================================ */
export function GoogleMeetIcon({ className = "w-8 h-8" }: { className?: string }) {
  return (
    <span className={`inline-flex items-center justify-center bg-white rounded-xl border border-slate-200 shadow-sm ${className}`} aria-label="Google Meet">
      <svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" className="w-3/4 h-3/4">
        <path fill="#00832d" d="M23.987 24L6 36V12z"/>
        <path fill="#00832d" d="M6 12h17.987v24H6z"/>
        <path fill="#00ac47" d="M23.987 24l18-12H6z"/>
        <path fill="#ea4335" d="M42 12H23.987v12L42 36z"/>
        <path fill="#0277bd" d="M23.987 24v12H42z"/>
        <path fill="#f4b400" d="M42 24v12l-18-12z"/>
      </svg>
    </span>
  );
}

/* ============================================================
   Full-Size 3D Padlock (hero section right visual)
   Matches the bold illustration in the design
   ============================================================ */
export function HeroPadlock({ className = "" }: { className?: string }) {
  return (
    <div className={`relative ${className}`} aria-hidden="true">
      <svg
        viewBox="0 0 200 250"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full"
        style={{ filter: "drop-shadow(0 28px 44px rgba(8,32,233,0.45)) drop-shadow(0 8px 16px rgba(8,32,233,0.20))" }}
      >
        {/* === Shackle (arch) === */}
        {/* Outer thick stroke */}
        <path
          d="M55 115V62C55 38.804 73.804 20 97 20H103C126.196 20 145 38.804 145 62V115"
          stroke="#05209C"
          strokeWidth="30"
          strokeLinecap="round"
        />
        {/* Inner bright stroke */}
        <path
          d="M55 115V62C55 38.804 73.804 20 97 20H103C126.196 20 145 38.804 145 62V115"
          stroke="#0254EC"
          strokeWidth="22"
          strokeLinecap="round"
        />
        {/* Shackle top highlight */}
        <path
          d="M70 64C70 46.327 84.327 32 102 32"
          stroke="rgba(255,255,255,0.35)"
          strokeWidth="5"
          strokeLinecap="round"
        />

        {/* === Body === */}
        <rect x="20" y="100" width="160" height="138" rx="28" fill="url(#bodyGrad)" />
        {/* Inner bevel border */}
        <rect x="22" y="102" width="156" height="134" rx="26" stroke="rgba(255,255,255,0.18)" strokeWidth="2" />
        {/* Top edge lighter highlight */}
        <ellipse cx="100" cy="102" rx="60" ry="5" fill="rgba(255,255,255,0.12)" />

        {/* === Keyhole === */}
        {/* Keyhole upper circle */}
        <circle cx="100" cy="152" r="14" fill="white" />
        {/* Keyhole slot */}
        <rect x="91.5" y="154" width="17" height="26" rx="4" fill="white" />
        {/* Keyhole inner circle shadow */}
        <circle cx="100" cy="152" r="8" fill="rgba(0,0,0,0.12)" />

        <defs>
          <linearGradient id="bodyGrad" x1="20" y1="100" x2="180" y2="238" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#1E6AFF" />
            <stop offset="45%" stopColor="#0254EC" />
            <stop offset="100%" stopColor="#0820E9" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
}

/* ============================================================
   Security Padlock in a Glass Dome (Key Features section)
   ============================================================ */
export function SecurityDomePadlock({ className = "" }: { className?: string }) {
  return (
    <div className={`relative flex items-end justify-center ${className}`} aria-hidden="true">
      <svg viewBox="0 0 280 300" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
        {/* Glass dome / cylinder base */}
        <ellipse cx="140" cy="268" rx="90" ry="14" fill="#FB6908" opacity="0.7" />
        <ellipse cx="140" cy="265" rx="90" ry="11" fill="#EA580C" opacity="0.5" />

        {/* Cylinder body */}
        <path
          d="M50 268 Q50 130 140 100 Q230 130 230 268"
          fill="url(#domeGrad)"
          opacity="0.22"
          stroke="#CFDCFE"
          strokeWidth="2"
        />

        {/* Dome glass ellipse top */}
        <ellipse cx="140" cy="98" rx="90" ry="28" fill="rgba(207,220,254,0.3)" stroke="#CFDCFE" strokeWidth="2" />

        {/* Inner padlock inside dome */}
        {/* Shackle */}
        <path
          d="M108 155V128C108 114.745 118.745 104 132 104H148C161.255 104 172 114.745 172 128V155"
          stroke="#05209C"
          strokeWidth="20"
          strokeLinecap="round"
        />
        <path
          d="M108 155V128C108 114.745 118.745 104 132 104H148C161.255 104 172 114.745 172 128V155"
          stroke="#FB6908"
          strokeWidth="14"
          strokeLinecap="round"
        />
        {/* Body */}
        <rect x="88" y="148" width="104" height="88" rx="18" fill="#FB6908" />
        <rect x="90" y="150" width="100" height="84" rx="16" stroke="rgba(255,255,255,0.15)" strokeWidth="2" />
        {/* Keyhole */}
        <circle cx="140" cy="185" r="9" fill="white" />
        <rect x="135" y="187" width="10" height="16" rx="3" fill="white" />
        <circle cx="140" cy="185" r="5" fill="rgba(0,0,0,0.15)" />

        <defs>
          <linearGradient id="domeGrad" x1="50" y1="200" x2="230" y2="268" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#CFDCFE" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#0254EC" stopOpacity="0.2" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
}
