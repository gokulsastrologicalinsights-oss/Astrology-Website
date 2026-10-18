"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  Compass,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  ChevronRight,
  Layers,
  Calendar,
  Grid3X3,
  FileText,
  Clock,
  Sparkle,
} from "lucide-react";

export default function AstrologyToolsPage() {
  const router = useRouter();
  const { language, t } = useLanguage();
  const { user, isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !user)) {
      router.replace("/login");
    }
  }, [isAuthenticated, user, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-[calc(100vh-14rem)] flex items-center justify-center bg-[#E8EEF7]">
        <div className="w-8 h-8 border-4 border-[#3478F6] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-8">
      {/* Breadcrumb Navigation */}
      <Breadcrumbs
        items={[
          {
            label: language === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools",
          },
        ]}
      />

      {/* Page Header */}
      <div className="text-center max-w-3xl mx-auto space-y-3">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
          <Compass className="w-3.5 h-3.5 text-[#B8862B]" />
          <span>{language === "ta" ? "கருவிகள் அடைவு" : "Master Tools Directory"}</span>
        </div>

        <h1 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-bold text-[#102A4C] tracking-tight">
          Astrology Tools | ஜோதிடக் கருவிகள்
        </h1>

        <p className="text-sm sm:text-base text-[#52667E] leading-relaxed">
          {t.toolsSubtitle ||
            "Access your horoscope calculations, KP astrology analysis, and numerology tools from one place."}
        </p>
      </div>

      {/* Primary Category Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-4 gap-6 max-w-7xl mx-auto pt-4">
        {/* Section Card 1: Horoscope / KP System */}
        <Link
          href="/tools/horoscope"
          className="group flex flex-col justify-between rounded-2xl sm:rounded-3xl border border-[#DDE5F0] bg-white p-6 sm:p-8 shadow-sm hover:shadow-xl hover:border-[#B8862B] transition-all relative overflow-hidden"
          aria-label="Navigate to Horoscope and KP System Tools"
        >
          {/* Subtle accent highlight */}
          <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-[#B8862B] to-[#E5B558]" />

          <div className="space-y-5">
            <div className="flex items-center justify-between">
              <div className="w-16 h-16 rounded-2xl bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center text-[#B8862B] shadow-2xs group-hover:scale-105 transition-transform">
                <Compass className="w-8 h-8 transition-transform group-hover:rotate-45" />
              </div>
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
                Vedic &amp; KP
              </span>
            </div>

            <div>
              <h2 className="font-serif text-2xl font-bold text-[#102A4C] group-hover:text-[#B8862B] transition-colors">
                Horoscope / KP System
              </h2>
              <p className="text-xs sm:text-sm font-tamil text-[#B8862B] font-semibold mt-1">
                ஜாதகம் மற்றும் கே.பி. ஜோதிடம்
              </p>
            </div>

            <p className="text-xs sm:text-sm text-[#52667E] leading-relaxed">
              Create and manage horoscopes, examine planetary positions, explore KP astrology calculations, and access Dasa-Bhukti timelines.
            </p>

            {/* Quick feature highlights inside card */}
            <div className="pt-2 flex flex-wrap gap-1.5 text-[11px] text-[#52667E]">
              <span className="px-2.5 py-1 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                Create Horoscope
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                Saved Horoscopes
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                Placidus Sub-Lords
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                5-Level Dasa Hierarchy
              </span>
            </div>
          </div>

          <div className="mt-8 pt-5 border-t border-[#F1F5F9] flex items-center justify-between">
            <span className="inline-flex items-center gap-2 text-xs sm:text-sm font-bold text-[#B8862B] group-hover:translate-x-0.5 transition-transform">
              <span>{t.sectionHoroscopeCta || "Open Horoscope Tools"}</span>
              <ArrowRight className="w-4 h-4" />
            </span>
            <span className="text-xs text-[#94A3B8] font-medium hidden sm:inline">
              6 Modules
            </span>
          </div>
        </Link>

        {/* Section Card 2: Numerology */}
        <Link
          href="/tools/numerology"
          className="group flex flex-col justify-between rounded-2xl sm:rounded-3xl border border-[#DDE5F0] bg-white p-6 sm:p-8 shadow-sm hover:shadow-xl hover:border-[#3478F6] transition-all relative overflow-hidden"
          aria-label="Navigate to Numerology Tools"
        >
          {/* Subtle accent highlight */}
          <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-[#3478F6] to-[#60A5FA]" />

          <div className="space-y-5">
            <div className="flex items-center justify-between">
              <div className="w-16 h-16 rounded-2xl bg-[#EBF2FE] border border-[#BFDBFE] flex items-center justify-center text-[#3478F6] shadow-2xs group-hover:scale-105 transition-transform">
                <Sparkles className="w-8 h-8 transition-transform group-hover:rotate-12" />
              </div>
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-[#EBF2FE] text-[#2563EB] border border-[#BFDBFE]">
                Vibrational Science
              </span>
            </div>

            <div>
              <h2 className="font-serif text-2xl font-bold text-[#102A4C] group-hover:text-[#3478F6] transition-colors">
                Numerology
              </h2>
              <p className="text-xs sm:text-sm font-tamil text-[#3478F6] font-semibold mt-1">
                எண் கணிதம்
              </p>
            </div>

            <p className="text-xs sm:text-sm text-[#52667E] leading-relaxed">
              Calculate numerology values, analyze names and birth dates, compare alternative spellings, and access supported numerology reports.
            </p>

            {/* Quick feature highlights inside card */}
            <div className="pt-2 flex flex-wrap gap-1.5 text-[11px] text-[#52667E]">
              <span className="px-2.5 py-1 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                Core Calculator
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                Name Spelling Compare
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                Driver &amp; Destiny
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                Destiny Matrix &amp; Lo Shu
              </span>
            </div>
          </div>

          <div className="mt-8 pt-5 border-t border-[#F1F5F9] flex items-center justify-between">
            <span className="inline-flex items-center gap-2 text-xs sm:text-sm font-bold text-[#3478F6] group-hover:translate-x-0.5 transition-transform">
              <span>{t.sectionNumerologyCta || "Open Numerology Tools"}</span>
              <ArrowRight className="w-4 h-4" />
            </span>
            <span className="text-xs text-[#94A3B8] font-medium hidden sm:inline">
              6 Modules
            </span>
          </div>
        </Link>

        {/* Section Card 3: Muhurta */}
        <Link
          href="/muhurta"
          className="group flex flex-col justify-between rounded-2xl sm:rounded-3xl border border-[#DDE5F0] bg-white p-6 sm:p-8 shadow-sm hover:shadow-xl hover:border-emerald-500 transition-all relative overflow-hidden"
          aria-label="Navigate to Vedic Muhurta Tools"
        >
          {/* Subtle accent highlight */}
          <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-emerald-600 to-teal-400" />

          <div className="space-y-5">
            <div className="flex items-center justify-between">
              <div className="w-16 h-16 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600 shadow-2xs group-hover:scale-105 transition-transform">
                <Calendar className="w-8 h-8 transition-transform group-hover:rotate-6" />
              </div>
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                Panchanga Timing
              </span>
            </div>

            <div>
              <h2 className="font-serif text-2xl font-bold text-[#102A4C] group-hover:text-emerald-700 transition-colors">
                Muhurta Finder
              </h2>
              <p className="text-xs sm:text-sm font-tamil text-emerald-700 font-semibold mt-1">
                சுப முகூர்த்தம் &amp; பஞ்சாங்கம்
              </p>
            </div>

            <p className="text-xs sm:text-sm text-[#52667E] leading-relaxed">
              Find, evaluate, compare, save, and print auspicious date-time windows for weddings, housewarmings, business openings, and vehicle deliveries.
            </p>

            {/* Quick feature highlights inside card */}
            <div className="pt-2 flex flex-wrap gap-1.5 text-[11px] text-[#52667E]">
              <span className="px-2.5 py-1 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                Auspicious Window Search
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                Daily Panchangam
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                Lagna &amp; Ashtama Shuddhi
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                Navatara Compatibility
              </span>
            </div>
          </div>

          <div className="mt-8 pt-5 border-t border-[#F1F5F9] flex items-center justify-between">
            <span className="inline-flex items-center gap-2 text-xs sm:text-sm font-bold text-emerald-700 group-hover:translate-x-0.5 transition-transform">
              <span>{language === "ta" ? "முகூர்த்தம் திறக்க" : "Open Muhurta Finder"}</span>
              <ArrowRight className="w-4 h-4" />
            </span>
            <span className="text-xs text-[#94A3B8] font-medium hidden sm:inline">
              8 Modules
            </span>
          </div>
        </Link>

        {/* Section Card 4: Advanced KP System */}
        <Link
          href="/tools/advanced-kp"
          className="group flex flex-col justify-between rounded-2xl sm:rounded-3xl border border-[#DDE5F0] bg-white p-6 sm:p-8 shadow-sm hover:shadow-xl hover:border-[#B8862B] transition-all relative overflow-hidden"
          aria-label="Navigate to Advanced KP System"
        >
          {/* Subtle accent highlight */}
          <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-[#B8862B] via-[#E5B558] to-[#102A4C]" />

          <div className="space-y-5">
            <div className="flex items-center justify-between">
              <div className="w-16 h-16 rounded-2xl bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center text-[#B8862B] shadow-2xs group-hover:scale-105 transition-transform">
                <Compass className="w-8 h-8 transition-transform group-hover:rotate-45" />
              </div>
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
                Krishnamurti Core
              </span>
            </div>

            <div>
              <h2 className="font-serif text-2xl font-bold text-[#102A4C] group-hover:text-[#B8862B] transition-colors">
                Advanced KP
              </h2>
              <p className="text-xs sm:text-sm font-tamil text-[#B8862B] font-semibold mt-1">
                உயர்நிலை கே.பி. முறை
              </p>
            </div>

            <p className="text-xs sm:text-sm text-[#52667E] leading-relaxed">
              Explore 249 sub-division tables, 4-tier significators (A, B, C, D), Placidus cuspal arbiter analysis, authentic 1-249 Horary Prashna, and 5-level Vimshottari timelines.
            </p>

            {/* Quick feature highlights inside card */}
            <div className="pt-2 flex flex-wrap gap-1.5 text-[11px] text-[#52667E]">
              <span className="px-2.5 py-1 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                Horary 1-249
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                Cuspal Sub-Lords
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                4-Tier Significators
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                5-Level Dasa
              </span>
            </div>
          </div>

          <div className="mt-8 pt-5 border-t border-[#F1F5F9] flex items-center justify-between">
            <span className="inline-flex items-center gap-2 text-xs sm:text-sm font-bold text-[#B8862B] group-hover:translate-x-0.5 transition-transform">
              <span>{language === "ta" ? "KP திறக்க" : "Open Advanced KP"}</span>
              <ArrowRight className="w-4 h-4" />
            </span>
            <span className="text-xs text-[#94A3B8] font-medium hidden sm:inline">
              6 Modules
            </span>
          </div>
        </Link>
      </div>

      {/* Engine & Rigor Disclaimer */}
      <div className="max-w-5xl mx-auto p-4 rounded-2xl bg-white border border-[#DDE5F0] flex items-center gap-3 text-xs text-[#52667E] shadow-2xs">
        <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0" />
        <p className="leading-relaxed">
          <strong>Deterministic Rigor:</strong> All tools in both sections operate on validated mathematical ephemeris formulas (JPL/Swiss Ephemeris standard) and verified classical numerology algorithms without conversational AI dependencies.
        </p>
      </div>
    </div>
  );
}
