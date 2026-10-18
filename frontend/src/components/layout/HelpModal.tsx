"use client";

import React from "react";
import { useLanguage } from "@/lib/i18n";
import {
  X,
  Compass,
  Sparkles,
  Layers,
  HelpCircle,
  Database,
  ShieldCheck,
  CheckCircle2,
} from "lucide-react";

interface HelpModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function HelpModal({ isOpen, onClose }: HelpModalProps) {
  const { language } = useLanguage();

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in duration-200"
    >
      <div
        className="fixed inset-0"
        onClick={onClose}
        aria-hidden="true"
      />

      <div className="relative w-full max-w-2xl bg-white rounded-2xl shadow-2xl border border-[#DDE5F0] overflow-hidden z-10 my-8">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 bg-[#F8FAFC] border-b border-[#DDE5F0]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#EBF2FE] border border-[#BFDBFE] flex items-center justify-center text-[#3478F6]">
              <HelpCircle className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-[#102A4C]">
                {language === "ta"
                  ? "வழிகாட்டி & உதவி மையம்"
                  : "Platform Guide & Help Center"}
              </h3>
              <p className="text-xs text-[#52667E]">
                {language === "ta"
                  ? "கோகுலின் ஜோதிட நுண்ணறிவுகள் — அமைப்பு விளக்கம்"
                  : "Gokul’s Astrological Insights Navigation & Features"}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 text-[#64748B] hover:text-[#102A4C] hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6 max-h-[75vh] overflow-y-auto text-xs sm:text-sm text-[#334155]">
          {/* Main Navigation Architecture */}
          <div className="space-y-2.5">
            <h4 className="font-bold text-[#102A4C] text-sm flex items-center gap-2">
              <Layers className="w-4 h-4 text-[#3478F6]" />
              <span>
                {language === "ta"
                  ? "மூன்று முக்கிய வழிசெலுத்தல் பிரிவுகள்"
                  : "Three-Item Main Navigation"}
              </span>
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="p-3 rounded-xl border border-[#DDE5F0] bg-[#F8FAFC]">
                <strong className="block text-[#102A4C] font-semibold">1. Home</strong>
                <p className="text-xs text-[#52667E] mt-1">
                  {language === "ta"
                    ? "தனிப்பயனாக்கப்பட்ட முகப்பு, விரைவு இணைப்புகள் மற்றும் சமீபத்திய ஜாதகங்கள்."
                    : "Personalized welcome page with quick-access tools and recent charts."}
                </p>
              </div>

              <div className="p-3 rounded-xl border border-[#DDE5F0] bg-[#F8FAFC]">
                <strong className="block text-[#102A4C] font-semibold">2. Dashboard</strong>
                <p className="text-xs text-[#52667E] mt-1">
                  {language === "ta"
                    ? "சேமிக்கப்பட்ட ஜாதகங்கள், பயன்பாட்டு புள்ளிவிவரங்கள் மற்றும் அறிக்கைகள்."
                    : "Database-backed metrics, saved charts management, and user history."}
                </p>
              </div>

              <div className="p-3 rounded-xl border border-[#DDE5F0] bg-[#F8FAFC]">
                <strong className="block text-[#102A4C] font-semibold">3. Astrology Tools</strong>
                <p className="text-xs text-[#52667E] mt-1">
                  {language === "ta"
                    ? "ஜாதகம்/KP முறை மற்றும் எண் கணிதம் ஆகிய இரு முக்கிய பிரிவுகள்."
                    : "Interactive directory leading to Horoscope/KP System and Numerology."}
                </p>
              </div>
            </div>
          </div>

          {/* Section 1: Horoscope / KP System */}
          <div className="p-4 rounded-xl border border-[#DDE5F0] bg-white space-y-2">
            <div className="flex items-center gap-2 text-[#B8862B] font-bold text-xs uppercase tracking-wider">
              <Compass className="w-4 h-4" />
              <span>Horoscope / KP System (ஜாதகம் & கே.பி. ஜோதிடம்)</span>
            </div>
            <ul className="space-y-1.5 text-xs text-[#52667E]">
              <li className="flex items-start gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 mt-0.5 shrink-0" />
                <span>
                  <strong>Create Horoscope:</strong> Precision astronomical calculation with JPL ephemeris models.
                </span>
              </li>
              <li className="flex items-start gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 mt-0.5 shrink-0" />
                <span>
                  <strong>Saved Horoscopes:</strong> Auto-saved in Supabase with sequential serial numbers (#0001).
                </span>
              </li>
              <li className="flex items-start gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 mt-0.5 shrink-0" />
                <span>
                  <strong>KP Astrology:</strong> Placidus cuspal sub-lords and planetary significators (Levels A, B, C, D).
                </span>
              </li>
              <li className="flex items-start gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 mt-0.5 shrink-0" />
                <span>
                  <strong>Dasa-Bhukti:</strong> Full 5-level hierarchy (Mahadasha through Pranadasha).
                </span>
              </li>
            </ul>
          </div>

          {/* Section 2: Numerology */}
          <div className="p-4 rounded-xl border border-[#DDE5F0] bg-white space-y-2">
            <div className="flex items-center gap-2 text-[#3478F6] font-bold text-xs uppercase tracking-wider">
              <Sparkles className="w-4 h-4" />
              <span>Numerology (எண் கணிதம்)</span>
            </div>
            <ul className="space-y-1.5 text-xs text-[#52667E]">
              <li className="flex items-start gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 mt-0.5 shrink-0" />
                <span>
                  <strong>Core Calculations:</strong> Life Path, Driver/Moolank, Destiny/Bhagyank, Soul Urge & Personality.
                </span>
              </li>
              <li className="flex items-start gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 mt-0.5 shrink-0" />
                <span>
                  <strong>Name Spelling Comparator:</strong> Compare alternative names side-by-side (Pythagorean & Chaldean).
                </span>
              </li>
              <li className="flex items-start gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 mt-0.5 shrink-0" />
                <span>
                  <strong>Couples Compatibility:</strong> Synthesis of vibrational relationship purpose and shared dynamics.
                </span>
              </li>
              <li className="flex items-start gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 mt-0.5 shrink-0" />
                <span>
                  <strong>Destiny Matrix & Lo Shu Grid:</strong> 22 Major Arcana octagram and 3x3 Magic Square with 8 Arrows.
                </span>
              </li>
            </ul>
          </div>

          {/* Engine & Rigor */}
          <div className="p-3.5 rounded-xl bg-[#F0FDF4] border border-[#BBF7D0] text-emerald-900 text-xs flex items-center gap-3">
            <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0" />
            <p className="leading-relaxed">
              <strong>Astronomical Precision:</strong> Calculations are strictly deterministic and powered by classical astronomical algorithms. Zero conversational AI hallucinations or invented claims.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 bg-[#F8FAFC] border-t border-[#DDE5F0] flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-bold text-white bg-[#102A4C] hover:bg-[#1E3A61] transition-colors"
          >
            {language === "ta" ? "சரி, புரிந்தது" : "Got It"}
          </button>
        </div>
      </div>
    </div>
  );
}
