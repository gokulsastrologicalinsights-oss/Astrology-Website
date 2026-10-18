"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { SavedHoroscopesList } from "@/components/saved/SavedHoroscopesList";
import {
  Compass,
  Database,
  Layers,
  Clock,
  Sparkles,
  ArrowLeft,
  ArrowRight,
  ShieldCheck,
  Calendar,
  Eye,
  Sliders,
  CheckCircle2,
  ListFilter,
  FileText,
} from "lucide-react";

function HoroscopeToolsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialTab = searchParams.get("tab") === "saved" ? "saved" : "cards";

  const { language, t } = useLanguage();
  const { user, isAuthenticated, isLoading } = useAuth();
  const [activeTab, setActiveTab] = useState<"cards" | "saved">(initialTab);

  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !user)) {
      router.replace("/login");
    }
  }, [isAuthenticated, user, isLoading, router]);

  useEffect(() => {
    const tabParam = searchParams.get("tab");
    if (tabParam === "saved") {
      setActiveTab("saved");
    }
  }, [searchParams]);

  if (isLoading) {
    return (
      <div className="min-h-[calc(100vh-14rem)] flex items-center justify-center bg-[#E8EEF7]">
        <div className="w-8 h-8 border-4 border-[#B8862B] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  const astrologyCards = [
    {
      id: "card-create",
      titleEn: "Create Horoscope",
      titleTa: "ஜாதகம் உருவாக்குதல்",
      descEn:
        "Open the full precision horoscope input form. Enter birth name, date, time, and coordinates to compute astronomical positions. Auto-saved with sequential serial numbers.",
      descTa:
        "முழு துல்லியமான ஜாதகக் கணக்கீட்டு படிவத்தைத் திறந்து, பிறந்த பெயர், தேதி, நேரம் மற்றும் இடத்தை உள்ளிட்டு கணக்கிடுங்கள். தானாக சேமிக்கப்படும்.",
      icon: Compass,
      href: "/horoscope",
      ctaEn: "Open Creation Form",
      ctaTa: "படிவத்தைத் திறக்க",
      badge: "Form & Ephemeris",
      color: "text-[#B8862B] bg-[#FAF2DE] border-[#D8BD80]",
    },
    {
      id: "card-saved",
      titleEn: "Saved Horoscopes",
      titleTa: "சேமிக்கப்பட்ட ஜாதகங்கள்",
      descEn:
        "Display saved horoscope records from Supabase. View permanent serial numbers, inspect stored calculations without recalculation, search, edit, or paginate.",
      descTa:
        "Supabase தரவுத்தளத்தில் சேமிக்கப்பட்ட ஜாதகங்களை வரிசை எண்களுடன் பார்க்கவும், தேடவும், திருத்தவும் அல்லது திறக்கவும்.",
      icon: Database,
      action: () => setActiveTab("saved"),
      ctaEn: "Browse Saved Horoscopes",
      ctaTa: "ஜாதகங்களை ஆராய்க",
      badge: "Supabase DB",
      color: "text-[#B8862B] bg-[#FAF2DE] border-[#D8BD80]",
    },
    {
      id: "card-kp",
      titleEn: "KP Astrology System",
      titleTa: "கே.பி. ஜோதிட முறை",
      descEn:
        "Open the Krishnamurti Paddhati module. Examine Placidus house cusps, cusp sub-lords, planetary significators (Levels A, B, C, D), and KP planetary rulers.",
      descTa:
        "கிருஷ்ணமூர்த்தி பத்தாதி (KP) முறையை ஆராயுங்கள். பிளாசிடஸ் பாவ முனைகள், உப-அதிபதிகள் மற்றும் கிரக காரகத்துவங்களை அணுகுங்கள்.",
      icon: Layers,
      href: "/horoscope/results?tab=kp",
      ctaEn: "Open KP Module",
      ctaTa: "கே.பி. முறையைத் திறக்க",
      badge: "Sub-Lord Precision",
      color: "text-[#B8862B] bg-[#FAF2DE] border-[#D8BD80]",
    },
    {
      id: "card-dasa",
      titleEn: "Vimshottari Dasa Timeline",
      titleTa: "விம்சோத்தரி தசா-புக்தி",
      descEn:
        "Open the hierarchical Dasa-Bhukti timeline. Displays complete 5-level progression: Mahadasha, Bhukti / Antardasha, Pratyantardasha, Sookshma, and Pranadasha.",
      descTa:
        "சந்திரனின் பாகையிலிருந்து கணக்கிடப்படும் 5-நிலை முழுமையான விம்சோத்தரி தசா காலவரிசையை (மகா தசை, புக்தி, அந்தரம், சூட்சுமம், பிராணன்) ஆராயுங்கள்.",
      icon: Clock,
      href: "/horoscope/results?tab=dasa",
      ctaEn: "View Dasa Timeline",
      ctaTa: "தசா காலவரிசையைக் காண்க",
      badge: "5-Level Hierarchy",
      color: "text-[#B8862B] bg-[#FAF2DE] border-[#D8BD80]",
    },
    {
      id: "card-analysis",
      titleEn: "Horoscope Planetary Analysis",
      titleTa: "ஜாதக கிரக நிலை பகுப்பாய்வு",
      descEn:
        "Detailed planetary positions in sidereal coordinates (degrees, minutes, seconds, nakshatras, padas, retrogrades), Bhava cusps, and South & North Indian chart layouts.",
      descTa:
        "துல்லியமான கிரக நிலைகள் (பாகை, கலை, விகலை, நட்சத்திர பாதம்), பாவ நிலைகள் மற்றும் தென்னிந்திய/வடஇந்திய கட்டங்களை அணுகுங்கள்.",
      icon: FileText,
      href: "/horoscope/results?tab=planets",
      ctaEn: "Inspect Planetary Analysis",
      ctaTa: "கிரக நிலைகளை ஆராய்க",
      badge: "Sidereal Vedic",
      color: "text-[#B8862B] bg-[#FAF2DE] border-[#D8BD80]",
    },
    {
      id: "card-tools",
      titleEn: "Panchang & Additional Tools",
      titleTa: "பஞ்சாங்கம் & கூடுதல் கருவிகள்",
      descEn:
        "Explore real-time Panchang calculations (Tithi, Nakshatra, Yoga, Karana, Vara), Ayanamsa comparative settings (Lahiri, KP, Raman), and chart format preferences.",
      descTa:
        "பஞ்சாங்க உறுப்புகள் (திதி, நட்சத்திரம், யோகம், கரணம், வாரம்) மற்றும் அயனாம்ச ஒப்பீட்டு அமைப்புகளை அணுகுங்கள்.",
      icon: Sliders,
      href: "/horoscope/results?tab=panchang",
      ctaEn: "Open Panchang & Tools",
      ctaTa: "பஞ்சாங்கம் & கருவிகள்",
      badge: "Ephemeris Tools",
      color: "text-[#B8862B] bg-[#FAF2DE] border-[#D8BD80]",
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-8">
      {/* 1. Breadcrumb Navigation & Back Action */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <Breadcrumbs
          items={[
            {
              label: language === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools",
              href: "/tools",
            },
            {
              label: language === "ta" ? "ஜாதகம் மற்றும் கே.பி. ஜோதிடம்" : "Horoscope / KP System",
            },
          ]}
        />

        <Link
          href="/tools"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#52667E] hover:text-[#102A4C] transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>
            {language === "ta" ? "ஜோதிடக் கருவிகள் முதன்மைப் பக்கம்" : "Back to Astrology Tools"}
          </span>
        </Link>
      </div>

      {/* 2. Page Title Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-[#DDE5F0]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2 h-2 rounded-full bg-[#B8862B]" />
            <span className="text-xs font-bold uppercase tracking-wider text-[#B8862B]">
              Vedic &amp; KP Astrological Engine
            </span>
          </div>
          <h1 className="font-serif text-2xl sm:text-3xl lg:text-4xl font-bold text-[#102A4C]">
            Horoscope / KP System | ஜாதகம் மற்றும் கே.பி. ஜோதிடம்
          </h1>
          <p className="mt-1 text-xs sm:text-sm text-[#52667E]">
            {language === "ta"
              ? "முழுமையான வானியல் எஃபிமெரிஸ் அடிப்படையிலான ஜாதகக் கணிப்பு, கே.பி. உப-அதிபதிகள் மற்றும் தசா காலவரிசை கருவிகள்."
              : "Access precision sidereal calculations, KP Krishnamurti Paddhati cuspal analysis, and complete 5-level Dasa timelines."}
          </p>
        </div>

        {/* Local Internal Tabs */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-white border border-[#DDE5F0] shadow-2xs shrink-0">
          <button
            type="button"
            onClick={() => setActiveTab("cards")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              activeTab === "cards"
                ? "bg-[#102A4C] text-white shadow-xs"
                : "text-[#52667E] hover:text-[#102A4C]"
            }`}
          >
            {language === "ta" ? "கருவிகள் அடைவு" : "Feature Directory"}
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("saved")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              activeTab === "saved"
                ? "bg-[#102A4C] text-white shadow-xs"
                : "text-[#52667E] hover:text-[#102A4C]"
            }`}
          >
            {language === "ta" ? "சேமித்த ஜாதகங்கள்" : "Saved Horoscopes"}
          </button>
        </div>
      </div>

      {/* 3. Tab Content */}
      {activeTab === "cards" ? (
        <div className="space-y-8">
          {/* 6 Feature Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {astrologyCards.map((card) => {
              const Icon = card.icon;

              const content = (
                <div className="flex flex-col justify-between h-full space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div
                        className={`w-12 h-12 rounded-xl flex items-center justify-center shadow-2xs border ${card.color}`}
                      >
                        <Icon className="w-6 h-6" />
                      </div>
                      <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-[#F8FAFC] text-[#52667E] border border-[#E2E8F0]">
                        {card.badge}
                      </span>
                    </div>

                    <div>
                      <h3 className="font-serif text-lg font-bold text-[#102A4C] group-hover:text-[#B8862B] transition-colors">
                        {language === "ta" ? card.titleTa : card.titleEn}
                      </h3>
                      <p className="text-[11px] font-tamil text-[#B8862B] font-medium">
                        {language === "ta" ? card.titleEn : card.titleTa}
                      </p>
                    </div>

                    <p className="text-xs text-[#52667E] leading-relaxed">
                      {language === "ta" ? card.descTa : card.descEn}
                    </p>
                  </div>

                  <div className="pt-4 border-t border-[#F1F5F9] flex items-center justify-between text-xs font-bold text-[#B8862B]">
                    <span>{language === "ta" ? card.ctaTa : card.ctaEn}</span>
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              );

              if (card.href) {
                return (
                  <Link
                    key={card.id}
                    href={card.href}
                    className="p-6 rounded-2xl bg-white border border-[#DDE5F0] hover:border-[#B8862B] shadow-xs hover:shadow-md transition-all group block"
                  >
                    {content}
                  </Link>
                );
              }

              return (
                <button
                  key={card.id}
                  type="button"
                  onClick={card.action}
                  className="p-6 rounded-2xl bg-white border border-[#DDE5F0] hover:border-[#B8862B] shadow-xs hover:shadow-md transition-all group block text-left w-full cursor-pointer"
                >
                  {content}
                </button>
              );
            })}
          </div>

          {/* Quick Info Banner */}
          <div className="p-4 rounded-2xl bg-white border border-[#DDE5F0] flex items-center gap-3 text-xs text-[#52667E] shadow-2xs">
            <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0" />
            <p className="leading-relaxed">
              <strong>Calculation Integrity:</strong> Every calculation uses sidereal positions derived from the XALEN astronomical engine. Saved records in Supabase preserve exact calculation snapshots for instant, deterministic reopening.
            </p>
          </div>
        </div>
      ) : (
        /* Saved Horoscopes Inline Tab */
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-[#102A4C]">
                {language === "ta" ? "சேமிக்கப்பட்ட ஜாதகங்கள் பட்டியல்" : "Saved Horoscopes Directory"}
              </h2>
              <p className="text-xs text-[#52667E]">
                {language === "ta"
                  ? "தேடல், பக்கமாக்கல் மற்றும் நேரடி ஜாதகப் பார்வை வசதியுடன் கூடிய பட்டியல்."
                  : "Search, paginate, edit birth metadata, or view stored calculation snapshots."}
              </p>
            </div>
            <Link
              href="/horoscope"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white bg-[#102A4C] hover:bg-[#1E3A61] shadow-xs transition-colors"
            >
              <Compass className="w-3.5 h-3.5" />
              <span>{language === "ta" ? "புதிய ஜாதகம் கணிக்க" : "New Horoscope"}</span>
            </Link>
          </div>

          <div className="rounded-2xl border border-[#DDE5F0] bg-white p-6 shadow-xs">
            <SavedHoroscopesList />
          </div>
        </div>
      )}
    </div>
  );
}

export default function HoroscopeToolsPage() {
  return (
    <React.Suspense
      fallback={
        <div className="min-h-[calc(100vh-14rem)] flex items-center justify-center bg-[#E8EEF7]">
          <div className="w-8 h-8 border-4 border-[#B8862B] border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <HoroscopeToolsContent />
    </React.Suspense>
  );
}

