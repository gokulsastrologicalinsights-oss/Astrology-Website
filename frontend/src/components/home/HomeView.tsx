"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { formatSerialNumber } from "@/lib/formatters";
import { SavedHoroscopeItem } from "@/lib/types";
import {
  Compass,
  Sparkles,
  ArrowRight,
  Database,
  Calendar,
  Layers,
  Clock,
  ShieldCheck,
  Grid3X3,
  FileText,
  Heart,
  ChevronRight,
  User,
  PlusCircle,
  ExternalLink,
} from "lucide-react";

export function HomeView() {
  const { language, t } = useLanguage();
  const { user } = useAuth();
  const [recentHoroscopes, setRecentHoroscopes] = useState<SavedHoroscopeItem[]>([]);
  const [isLoadingRecent, setIsLoadingRecent] = useState(true);

  // Time-of-day greeting
  const [greeting, setGreeting] = useState("Welcome");

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) {
      setGreeting(language === "ta" ? "இனிய காலை வணக்கம்" : "Good morning");
    } else if (hour < 17) {
      setGreeting(language === "ta" ? "இனிய பிற்பகல் வணக்கம்" : "Good afternoon");
    } else {
      setGreeting(language === "ta" ? "இனிய மாலை வணக்கம்" : "Good evening");
    }
  }, [language]);

  // Load recent horoscopes from Supabase API
  useEffect(() => {
    let isMounted = true;
    fetch("/api/horoscopes?page=1&limit=3", { cache: "no-store" })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (isMounted && data?.horoscopes) {
          setRecentHoroscopes(data.horoscopes);
        }
      })
      .catch((err) => {
        console.warn("Could not fetch recent horoscopes for Home page:", err);
      })
      .finally(() => {
        if (isMounted) setIsLoadingRecent(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-10">
      {/* 1. Personalized Welcome Hero */}
      <div className="relative rounded-3xl bg-gradient-to-br from-[#102A4C] via-[#16355F] to-[#1E4378] text-white p-6 sm:p-10 shadow-lg border border-[#3478F6]/20 overflow-hidden">
        {/* Subtle decorative glow */}
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-[#3478F6]/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-80 h-80 bg-[#B8862B]/15 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/15 text-xs text-[#FAF2DE] font-semibold">
            <Sparkles className="w-3.5 h-3.5 text-[#B8862B]" />
            <span>
              {language === "ta"
                ? "கோகுலின் ஜோதிட நுண்ணறிவுகள்"
                : "Gokul’s Astrological Insights"}
            </span>
          </div>

          <h1 className="font-serif text-2xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-white leading-tight">
            {greeting}, {user?.displayName || user?.username || "Aspirant"}!
          </h1>

          <p className="text-xs sm:text-sm text-slate-200 leading-relaxed max-w-2xl">
            {language === "ta"
              ? "துல்லியமான வேத மற்றும் கே.பி வானியல் முறை மற்றும் எண் கணிதத் தளம். எஃபிமெரிஸ் கணித முறையுடன் உங்கள் ஜாதகங்கள் மற்றும் எண் வரைபடங்களை அணுகுங்கள்."
              : "Welcome to your precision astrological hub. Access deterministic sidereal Vedic charts, KP sub-lord significators, hierarchical Dasa timelines, and vibration numerology."}
          </p>

          <div className="pt-3 flex flex-wrap gap-3">
            <Link
              href="/tools"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold text-[#102A4C] bg-white hover:bg-slate-100 shadow-md transition-all group"
            >
              <span>{language === "ta" ? "ஜோதிடக் கருவிகளைத் திறக்க" : "Explore Astrology Tools"}</span>
              <ArrowRight className="w-3.5 h-3.5 text-[#3478F6] group-hover:translate-x-0.5 transition-transform" />
            </Link>

            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-white/10 hover:bg-white/20 border border-white/20 backdrop-blur-xs transition-colors"
            >
              <span>{t.navDashboard}</span>
            </Link>
          </div>
        </div>
      </div>

      {/* 2. The Two Primary Category Feature Cards */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg sm:text-xl font-bold text-[#102A4C] tracking-tight">
              {language === "ta" ? "முக்கிய கருவிகள் பிரிவுகள்" : "Astrology Tools Sections"}
            </h2>
            <p className="text-xs text-[#52667E]">
              {language === "ta"
                ? "இரு முதன்மை பிரிவுகள் வழியாக அனைத்து ஜோதிட மற்றும் எண் கணித அம்சங்களை அணுகலாம்."
                : "Choose between precision Horoscope / KP System calculations or Numerology tools."}
            </p>
          </div>
          <Link
            href="/tools"
            className="text-xs font-semibold text-[#3478F6] hover:underline hidden sm:inline-flex items-center gap-1"
          >
            <span>{language === "ta" ? "அனைத்து கருவிகள்" : "View Directory"}</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Category Card 1: Horoscope / KP System */}
          <Link
            href="/tools/horoscope"
            className="group block p-6 sm:p-8 rounded-2xl bg-white border border-[#DDE5F0] hover:border-[#B8862B] shadow-xs hover:shadow-lg transition-all"
          >
            <div className="flex items-start justify-between">
              <div className="w-14 h-14 rounded-2xl bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center text-[#B8862B] group-hover:scale-105 transition-transform shadow-2xs">
                <Compass className="w-7 h-7" />
              </div>
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-[11px] font-semibold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
                Vedic &amp; KP
              </span>
            </div>

            <div className="mt-6 space-y-2">
              <h3 className="font-serif text-xl sm:text-2xl font-bold text-[#102A4C] group-hover:text-[#B8862B] transition-colors">
                Horoscope / KP System
              </h3>
              <p className="text-xs font-tamil text-[#B8862B] font-medium">
                ஜாதகம் மற்றும் கே.பி. ஜோதிடம்
              </p>
              <p className="text-xs sm:text-sm text-[#52667E] leading-relaxed pt-1">
                {t.sectionHoroscopeDesc ||
                  "Create and manage horoscopes, examine planetary positions, explore KP astrology calculations, and access Dasa-Bhukti timelines."}
              </p>
            </div>

            <div className="mt-6 pt-4 border-t border-[#F1F5F9] flex items-center justify-between text-xs font-bold text-[#B8862B]">
              <span>{t.sectionHoroscopeCta || "Open Horoscope Tools"}</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>

          {/* Category Card 2: Numerology */}
          <Link
            href="/tools/numerology"
            className="group block p-6 sm:p-8 rounded-2xl bg-white border border-[#DDE5F0] hover:border-[#3478F6] shadow-xs hover:shadow-lg transition-all"
          >
            <div className="flex items-start justify-between">
              <div className="w-14 h-14 rounded-2xl bg-[#EBF2FE] border border-[#BFDBFE] flex items-center justify-center text-[#3478F6] group-hover:scale-105 transition-transform shadow-2xs">
                <Sparkles className="w-7 h-7" />
              </div>
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-[11px] font-semibold bg-[#EBF2FE] text-[#2563EB] border border-[#BFDBFE]">
                Pythagorean &amp; Arcana
              </span>
            </div>

            <div className="mt-6 space-y-2">
              <h3 className="font-serif text-xl sm:text-2xl font-bold text-[#102A4C] group-hover:text-[#3478F6] transition-colors">
                Numerology
              </h3>
              <p className="text-xs font-tamil text-[#3478F6] font-medium">
                எண் கணிதம்
              </p>
              <p className="text-xs sm:text-sm text-[#52667E] leading-relaxed pt-1">
                {t.sectionNumerologyDesc ||
                  "Calculate numerology values, analyze names and birth dates, compare alternative spellings, and access supported numerology reports."}
              </p>
            </div>

            <div className="mt-6 pt-4 border-t border-[#F1F5F9] flex items-center justify-between text-xs font-bold text-[#3478F6]">
              <span>{t.sectionNumerologyCta || "Open Numerology Tools"}</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>
        </div>
      </div>

      {/* 3. Frequently Used Quick Access Tools */}
      <div className="rounded-2xl border border-[#DDE5F0] bg-white p-6 shadow-xs space-y-4">
        <h3 className="font-serif text-base sm:text-lg font-bold text-[#102A4C]">
          {t.homeQuickAccess || "Frequently Used Tools"}
        </h3>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <Link
            href="/horoscope"
            className="p-3.5 rounded-xl border border-[#DDE5F0] hover:border-[#B8862B] bg-[#F8FAFC] hover:bg-[#FAF2DE]/40 transition-all text-center flex flex-col items-center justify-center gap-2 group"
          >
            <div className="w-9 h-9 rounded-lg bg-[#FAF2DE] text-[#B8862B] flex items-center justify-center">
              <Compass className="w-5 h-5 group-hover:rotate-12 transition-transform" />
            </div>
            <span className="text-xs font-semibold text-[#102A4C]">
              {language === "ta" ? "புதிய ஜாதகம்" : "New Chart"}
            </span>
          </Link>

          <Link
            href="/tools/horoscope?tab=saved"
            className="p-3.5 rounded-xl border border-[#DDE5F0] hover:border-[#B8862B] bg-[#F8FAFC] hover:bg-[#FAF2DE]/40 transition-all text-center flex flex-col items-center justify-center gap-2 group"
          >
            <div className="w-9 h-9 rounded-lg bg-[#FAF2DE] text-[#B8862B] flex items-center justify-center">
              <Database className="w-5 h-5 group-hover:scale-105 transition-transform" />
            </div>
            <span className="text-xs font-semibold text-[#102A4C]">
              {language === "ta" ? "சேமித்த ஜாதகம்" : "Saved Charts"}
            </span>
          </Link>

          <Link
            href="/numerology/traditional"
            className="p-3.5 rounded-xl border border-[#DDE5F0] hover:border-[#3478F6] bg-[#F8FAFC] hover:bg-[#EBF2FE]/40 transition-all text-center flex flex-col items-center justify-center gap-2 group"
          >
            <div className="w-9 h-9 rounded-lg bg-[#EBF2FE] text-[#3478F6] flex items-center justify-center">
              <Sparkles className="w-5 h-5 group-hover:scale-105 transition-transform" />
            </div>
            <span className="text-xs font-semibold text-[#102A4C]">
              {language === "ta" ? "எண் கால்குலேட்டர்" : "Numerology"}
            </span>
          </Link>

          <Link
            href="/tools/numerology?tab=name"
            className="p-3.5 rounded-xl border border-[#DDE5F0] hover:border-[#3478F6] bg-[#F8FAFC] hover:bg-[#EBF2FE]/40 transition-all text-center flex flex-col items-center justify-center gap-2 group"
          >
            <div className="w-9 h-9 rounded-lg bg-[#EBF2FE] text-[#3478F6] flex items-center justify-center">
              <FileText className="w-5 h-5 group-hover:scale-105 transition-transform" />
            </div>
            <span className="text-xs font-semibold text-[#102A4C]">
              {language === "ta" ? "பெயர் ஒப்பீடு" : "Name Compare"}
            </span>
          </Link>

          <Link
            href="/numerology/destiny-matrix"
            className="p-3.5 rounded-xl border border-[#DDE5F0] hover:border-[#3478F6] bg-[#F8FAFC] hover:bg-[#EBF2FE]/40 transition-all text-center flex flex-col items-center justify-center gap-2 group"
          >
            <div className="w-9 h-9 rounded-lg bg-[#EBF2FE] text-[#3478F6] flex items-center justify-center">
              <Layers className="w-5 h-5 group-hover:scale-105 transition-transform" />
            </div>
            <span className="text-xs font-semibold text-[#102A4C]">
              {language === "ta" ? "விதி அணி (22)" : "Destiny Matrix"}
            </span>
          </Link>

          <Link
            href="/numerology/advanced"
            className="p-3.5 rounded-xl border border-[#DDE5F0] hover:border-[#3478F6] bg-[#F8FAFC] hover:bg-[#EBF2FE]/40 transition-all text-center flex flex-col items-center justify-center gap-2 group"
          >
            <div className="w-9 h-9 rounded-lg bg-[#EBF2FE] text-[#3478F6] flex items-center justify-center">
              <Grid3X3 className="w-5 h-5 group-hover:scale-105 transition-transform" />
            </div>
            <span className="text-xs font-semibold text-[#102A4C]">
              {language === "ta" ? "லோ-ஷூ கட்டம்" : "Lo Shu Grid"}
            </span>
          </Link>
        </div>
      </div>

      {/* 4. Recent Saved Horoscopes Preview */}
      <div className="rounded-2xl border border-[#DDE5F0] bg-white p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-[#F1F5F9]">
          <div className="flex items-center gap-2">
            <Database className="w-5 h-5 text-[#B8862B]" />
            <h3 className="font-serif text-base sm:text-lg font-bold text-[#102A4C]">
              {t.homeRecentCharts || "Recent Saved Horoscopes"}
            </h3>
          </div>
          <Link
            href="/dashboard"
            className="text-xs font-semibold text-[#3478F6] hover:underline inline-flex items-center gap-1"
          >
            <span>{language === "ta" ? "அனைத்தையும் காண்க" : "View All on Dashboard"}</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {isLoadingRecent ? (
          <div className="py-8 text-center text-xs text-[#52667E]">
            <div className="inline-block animate-spin w-5 h-5 border-2 border-[#B8862B] border-t-transparent rounded-full mb-2" />
            <p>{t.loading}</p>
          </div>
        ) : recentHoroscopes.length === 0 ? (
          <div className="py-8 px-4 text-center rounded-xl border border-dashed border-[#DDE5F0] bg-[#F8FAFC]">
            <Compass className="w-8 h-8 text-[#94A3B8] mx-auto mb-2" />
            <p className="text-xs text-[#52667E]">
              {language === "ta"
                ? "இதுவரை ஜாதகங்கள் எதுவும் சேமிக்கப்படவில்லை. புதிய ஜாதகத்தைக் கணக்கிடுங்கள்."
                : "No saved horoscopes found. Generate your first precision chart to see it here."}
            </p>
            <div className="mt-3">
              <Link
                href="/horoscope"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white bg-[#102A4C] hover:bg-[#1E3A61]"
              >
                <PlusCircle className="w-3.5 h-3.5" />
                <span>{language === "ta" ? "புதிய ஜாதகம் கணிக்க" : "Create Horoscope"}</span>
              </Link>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {recentHoroscopes.map((item) => (
              <div
                key={item.id}
                className="p-4 rounded-xl border border-[#DDE5F0] hover:border-[#B8862B] bg-[#FAFBFD] hover:bg-white shadow-2xs hover:shadow-xs transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-[#FAF2DE] text-[#B8862B] border border-[#D8BD80]">
                      #{formatSerialNumber(item.display_number)}
                    </span>
                    <span className="text-[10px] text-[#94A3B8]">
                      {new Date(item.created_at).toLocaleDateString()}
                    </span>
                  </div>

                  <h4 className="font-bold text-sm text-[#102A4C] truncate">
                    {item.person_name}
                  </h4>

                  <div className="mt-2 space-y-1 text-xs text-[#52667E]">
                    <div className="flex items-center gap-1.5 truncate">
                      <Calendar className="w-3.5 h-3.5 text-[#94A3B8] shrink-0" />
                      <span>{item.birth_date}</span>
                    </div>
                    <div className="flex items-center gap-1.5 truncate">
                      <Clock className="w-3.5 h-3.5 text-[#94A3B8] shrink-0" />
                      <span>{item.birth_time}</span>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-[#F1F5F9] flex items-center justify-end">
                  <Link
                    href={`/horoscope/results?id=${item.id}`}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-[#3478F6] hover:underline"
                  >
                    <span>{t.actionOpenHoroscope || "Open"}</span>
                    <ExternalLink className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 5. Engine & Data Integrity Notice */}
      <div className="p-4 rounded-2xl bg-white border border-[#DDE5F0] flex items-center gap-3 shadow-2xs text-xs text-[#52667E]">
        <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0" />
        <p className="leading-relaxed">
          <strong>Deterministic Ephemeris:</strong> All planetary coordinates, KP cusp sub-lords, and Dasa periods are calculated through verified algorithms. Saved horoscopes and numerology reports are stored in your secure Supabase account with sequential numbering.
        </p>
      </div>
    </div>
  );
}
