import type { Metadata } from "next";
import { Plus_Jakarta_Sans, Inter } from "next/font/google";
import "./globals.css";

const plusJakartaSans = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["500", "600", "700", "800"],
  variable: "--font-heading",
  display: "swap",
});

const inter = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-sans",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Next-Hour – AI Energy Consumption Prediction & Analytics",
  description:
    "Data lab to train frontier models, predict next-hour power usage, spot peak demand spikes, and evaluate energy efficiency with real-time machine learning.",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`dark ${plusJakartaSans.variable} ${inter.variable}`}>
      <body className="min-h-screen bg-black text-[#f8fafc] antialiased selection:bg-white/20 selection:text-white">
        {children}
      </body>
    </html>
  );
}
