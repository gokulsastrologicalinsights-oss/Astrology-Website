"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  Compass,
  Clock,
  Sparkles,
  Layers,
  Calendar,
  Database,
  Cake,
  BookOpen,
  HeartHandshake,
  Heart,
  ShieldCheck,
  Hash,
  Briefcase,
  Zap,
  ShieldAlert,
  Flame,
} from "lucide-react";
import { BirthdayReminderModal } from "@/components/birthday/BirthdayReminderModal";
import { DasaCautionReminderModal } from "@/components/caution/DasaCautionReminderModal";

export default function AstrologyToolsPage() {
  const router = useRouter();
  const { language, t } = useLanguage();
  const { user, isAuthenticated, isLoading } = useAuth();
  const [isBirthdayOpen, setIsBirthdayOpen] = useState(false);
  const [isCautionOpen, setIsCautionOpen] = useState(false);

  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !user)) {
      router.replace("/login");
    }
  }, [isAuthenticated, user, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-[calc(100vh-14rem)] flex items-center justify-center bg-[#F2F3F5]">
        <div className="w-8 h-8 border-4 border-[#153F6B] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null;
  }

interface AstrologyToolCard {
  id: string;
  titleTa: string;
  titleEn: string;
  descriptionTa?: string;
  descriptionEn?: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}

  // Section 1: Astrology Tools Cards (matching Screenshot 1)
  const astrologyTools: AstrologyToolCard[] = [
    {
      id: "instant-revelation",
      titleTa: "வாடிக்கையாளர் நேரடி வாக்கு பலகை (உடனடி பலன்)",
      titleEn: "Instant Customer Revelation Teleprompter",
      descriptionTa: "வாடிக்கையாளர் வந்தவுடன் எவ்வித கிரகக் கணக்கீடும் இன்றி வருகை நோக்கம், 3 கடந்த கால உண்மைகள், மற்றும் எதிர்காலத்தை நேரடியாகப் பேசும் வாக்கு பலகை.",
      descriptionEn: "Zero-analysis cold-reading teleprompter: instant arrival mind-reading, 3 verifiable past shock hits, Vastu markers, and future timing windows.",
      href: "/tools/instant-revelation",
      icon: Zap,
      color: "text-rose-700 border-rose-300 bg-rose-50/70 ring-2 ring-rose-400/40",
    },
    {
      id: "kp-monthly-predictions",
      titleTa: "KP நடப்பு காலக்கட்ட பலன் & நிகழ்வு கணிப்பான்",
      titleEn: "KP Monthly & Period Predictive Event Timing",
      descriptionTa: "தசா-புத்தி-அந்தரம், பாவ உப-நட்சத்திர நாதன் (CSL) மற்றும் கோச்சார சூரியன் இணைவு மூலம் நடப்பு மாதம் (நவம்பர்/டிசம்பர்) எது கண்டிப்பாக நடந்து தீரும் என்ற 100% உறுதியான கணிப்பு.",
      descriptionEn: "High-certainty monthly prediction forecaster evaluating running D-B-A-S, Cuspal Sub-Lord promise, and transit Sun triggers to pinpoint guaranteed events.",
      href: "/tools/kp-monthly-predictions",
      icon: Sparkles,
      color: "text-amber-700 border-amber-400 bg-amber-50/90 ring-2 ring-amber-500/40",
    },
    {
      id: "life-roadmap",
      titleTa: "வாழ்க்கை காலவரிசை கணிப்பு (Life Roadmap)",
      titleEn: "Multi-Year Life Roadmap (1-5 Years)",
      descriptionTa: "அனைத்து 5 முக்கிய வாழ்க்கை துறைகளிலும் (தொழில், திருமணம், தனம், பயணம், ஆரோக்கியம்) அடுத்த 1, 3, அல்லது 5 ஆண்டுகளுக்கான முழு காலவரிசை வரைபடம்.",
      descriptionEn: "Automated multi-year timeline evaluating Career, Relationships, Finance, Relocation, and Health simultaneously across DBA periods.",
      href: "/tools/life-roadmap",
      icon: Sparkles,
      color: "text-emerald-700 border-emerald-300 bg-emerald-50/80 ring-2 ring-emerald-400/30",
    },
    {
      id: "kp-horary-predictor",
      titleTa: "கே.பி. உடனடி பிரஸ்னம் (1-249 நிகழ்வு கணிப்பாளர்)",
      titleEn: "Instant KP Horary / Prashna Predictor (1–249)",
      descriptionTa: "விசா அனுமதி, வேலை நேர்காணல், நீதிமன்ற வழக்கு வெற்றி, திருமணம், சொத்து சேர்க்கை கேள்விகளுக்கு உடனடி தீர்ப்பு & காரிய சித்தி கால அட்டவணை.",
      descriptionEn: "Instant automated event predictor for real-time queries (Visa, Job Interview, Court Case, Marriage, Property): Verdict Card, CSL analysis, and Dasha/Moon transit timing.",
      href: "/tools/kp-horary-predictor",
      icon: Sparkles,
      color: "text-[#B8862B] border-[#D8BD80] bg-[#FAF2DE]/80 ring-2 ring-[#B8862B]/30",
    },
    {
      id: "horoscope",
      titleTa: "ஜாதகம் (வேத & கே.பி)",
      titleEn: "Horoscope (Vedic & KP)",
      href: "/tools/horoscope",
      icon: Compass,
      color: "text-[#B4872B] border-[#B4872B]/40 bg-[#FAF2DE]/50",
    },
    {
      id: "horoscope-writing",
      titleTa: "பாரம்பரிய தமிழ் ஜாதகக் குறிப்பு",
      titleEn: "Horoscope Writing",
      descriptionTa: "பாரம்பரிய 6-பக்க தமிழ் ஜாதக ஏடு, தினசுத்தி, உடுமகா திசை மற்றும் அர்ச்சனை சீட்டு.",
      descriptionEn: "Traditional 6-page Tamil horoscope booklet, eras, Vimshottari Dasa, and archana slip.",
      href: "/tools/horoscope-writing",
      icon: BookOpen,
      color: "text-[#8B6914] border-[#B4872B]/40 bg-[#FAF2DE]/50",
    },
    {
      id: "kp-narrative",
      titleTa: "கே.பி. கணிப்பு உரை அறிக்கை (Predictive Narrative)",
      titleEn: "Automated KP Predictive Narrative Engine",
      descriptionTa: "ஜாதக வாக்குறுதி, தற்போதைய தசா-புத்தி பலன்கள், 12-24 மாத மைல்கற்கள் மற்றும் பரிகாரங்களை எளிய நடையில் வழங்கும் கணிப்பு இயந்திரம்.",
      descriptionEn: "Structured, plain-language predictive report evaluating Natal Event Promise, running Dasha-Bhukti, 12-24 month milestone windows, and remedial advice.",
      href: "/tools/kp-predictive-narrative",
      icon: Sparkles,
      color: "text-[#153F6B] border-[#153F6B]/30 bg-[#EBF2FE] ring-2 ring-[#153F6B]/20",
    },
    {
      id: "marriage",
      titleTa: "திருமணப் பொருத்தம் (36 அஷ்டகூடம்)",
      titleEn: "Kundli Matching & 36 Ashta Kuta",
      href: "/tools/marriage-compatibility",
      icon: HeartHandshake,
      color: "text-[#153F6B] border-[#153F6B]/30 bg-[#EBF2FE]",
    },
    {
      id: "marriage-prediction",
      titleTa: "திருமண கணிப்பு",
      titleEn: "Marriage Prediction",
      descriptionTa: "கே.பி மற்றும் வேத ஜோதிட முறையில் திருமண வாய்ப்புகள் மற்றும் கால நிர்ணயம்.",
      descriptionEn: "Analyze marriage prospects and timing using KP and Vedic astrology.",
      href: "/tools/marriage-prediction",
      icon: Heart,
      color: "text-rose-600 border-rose-300 bg-rose-50",
    },
    {
      id: "panchang",
      titleTa: "தினசரி பஞ்சாங்கம் & 24-கிரக ஹோரை",
      titleEn: "Daily Panchangam & 24-Planetary Horas",
      descriptionTa: "சூரிய உதயம், திதி, நட்சத்திரம், யோகம், கரணம், இராகு காலம் மற்றும் நேரடி 24-மணி நேர கிரக ஹோரை வழிகாட்டி.",
      descriptionEn: "Astronomical 5-limbs, Rahu/Yama/Gulika octants, and live 24-Hora timing advisor with real-time countdown.",
      href: "/tools/panchang",
      icon: Calendar,
      color: "text-amber-600 border-amber-300 bg-amber-50",
    },
    {
      id: "birth-time-rectification",
      titleTa: "பிறந்த நேர திருத்தம் (BTR)",
      titleEn: "Birth Time Rectification (BTR)",
      descriptionTa: "வாழ்க்கை நிகழ்வுகளைக் கொண்டு கே.பி உப-அதிபதி, D9 நவாம்சம் & D60 ஷஷ்டியாம்சம் முறையில் வினாடித் துல்லியத்தில் நேரத் திருத்தம்.",
      descriptionEn: "Rectify birth time down to the second using past life events, KP sub-lords, D9 Navamsha, and D60 Shashtiamsha shifts.",
      href: "/tools/birth-time-rectification",
      icon: Clock,
      color: "text-amber-700 border-amber-300 bg-amber-50",
    },
    {
      id: "advanced-kp",
      titleTa: "உயர்நிலை கே.பி",
      titleEn: "Advanced KP System",
      href: "/tools/advanced-kp",
      icon: Layers,
      color: "text-indigo-600 border-indigo-300 bg-indigo-50",
    },
    {
      id: "kp-events",
      titleTa: "கே.பி. நிகழ்வு கணிப்பு",
      titleEn: "KP Events & Prediction",
      href: "/tools/kp-events-prediction",
      icon: Sparkles,
      color: "text-[#B4872B] border-[#B4872B]/40 bg-[#FAF2DE]/50",
    },
    {
      id: "numerology",
      titleTa: "எண் கணிதம்",
      titleEn: "Numerology System",
      href: "/tools/numerology",
      icon: Hash,
      color: "text-blue-600 border-blue-300 bg-blue-50",
    },
    {
      id: "muhurta",
      titleTa: "சுப முகூர்த்த அரங்கம்",
      titleEn: "Muhurta Event Matching Studio",
      descriptionTa: "திருமணம், கிரகப்பிரவேசம், வர்த்தகத் துவக்கம் மற்றும் வாகன முகூர்த்தங்களுக்கான சாஸ்திர தேர்வு இயந்திரம்.",
      descriptionEn: "Multi-criteria candidate search and scoring engine for Marriage, Griha Pravesha, Business Launch, and Vehicle Purchase.",
      href: "/tools/muhurta",
      icon: Sparkles,
      color: "text-emerald-600 border-emerald-300 bg-emerald-50",
    },
    {
      id: "jamakkol-prasanam",
      titleTa: "ஜாமக்கோள் பிரசன்னம்",
      titleEn: "Jamakkol Prasanam Horary",
      descriptionTa: "உதயம், ஆருடம், கவிப்பு மற்றும் 8 வெளிவட்ட ஜாமக் கோள்களைக் கொண்ட அதிவேக 16-ஜாம பிரசன்ன சக்கரம் & காரிய சித்தி தீர்ப்பு.",
      descriptionEn: "Classical 16-Jamam horary astrology engine with Udhayam, Aarudham, Kavippu, and 8 outer Jama Grahas in a dual-ring South Indian chart.",
      href: "/tools/jamakkol-prasanam",
      icon: Compass,
      color: "text-amber-600 border-amber-300 bg-amber-50",
    },
    {
      id: "pancha-pakshi",
      titleTa: "பஞ்ச பட்சி சாஸ்திரம்",
      titleEn: "Pancha Pakshi Shastra",
      descriptionTa: "அகத்தியர் சித்த முறைப்படி வல்லூறு, ஆந்தை, காகம், கோழி, மயில் ஐந்து பட்சிகளின் அரசு, ஊண், நடை, துயில், சாவு அந்தர கால வழிகாட்டி.",
      descriptionEn: "Sage Agastya's five-bird bio-rhythm predictive system across Ruling, Eating, Walking, Sleeping, and Dying phases.",
      href: "/tools/pancha-pakshi",
      icon: Zap,
      color: "text-teal-600 border-teal-300 bg-teal-50",
    },
    {
      id: "daily-sastra",
      titleTa: "தினசரி சாஸ்திர வழிகாட்டி",
      titleEn: "Daily Dharma & Sastra Guide",
      descriptionTa: "நாள்விழிப்பு, கௌரி பஞ்சாங்கம், வாரசூலம் பரிகாரம், 22 நோய் தீர்க்கும் தெய்வங்கள், வாஸ்து புருஷன் விழிப்பு மற்றும் சுபமுகூர்த்த நியதிகள்.",
      descriptionEn: "Classical daily do's and don'ts, Gowri Panchangam, Soolam remedies, medical deity healing, and Vastu Purusha awakening.",
      href: "/tools/daily-sastra",
      icon: ShieldCheck,
      color: "text-indigo-700 border-indigo-300 bg-indigo-50",
    },
    {
      id: "kuladeivam-finder",
      titleTa: "குலதெய்வம் கண்டறியும் ஆய்வு அரங்கம்",
      titleEn: "Kuladeivam (Family Deity) Finder",
      descriptionTa: "5 & 9-ஆம் பாவகங்கள், நவாம்சம் மற்றும் ஜாமக்கோள் பிரசன்ன ஆருட வழி வம்சக் குலதெய்வம், கோவில் திசை, மற்றும் பரிகார வழிகாட்டி.",
      descriptionEn: "Classical Vedic & Horary engine to find ancestral deity, gender, worship category, temple direction, and discovery protocol.",
      href: "/tools/kuladeivam-finder",
      icon: Sparkles,
      color: "text-amber-800 border-amber-400 bg-amber-50",
    },
    {
      id: "remedies",
      titleTa: "சாஸ்திர பரிகாரங்கள் & நவகிரக திருத்தலங்கள்",
      titleEn: "Shastric Remedies & Navagraha Temples",
      descriptionTa: "தோஷ நிவர்த்தி பரிகாரங்கள், நவகிரக பரிகாரத் தலங்கள், சன்னூ சடங்குகள் மற்றும் ருக்யா ஆன்மீக வழிகாட்டி.",
      descriptionEn: "Classical Vedic dosha remedies, 9 planetary temples, Sannu rituals, and Islamic Ruqyah spiritual healing guide.",
      href: "/remedies",
      icon: Sparkles,
      color: "text-amber-700 border-amber-300 bg-amber-50",
    },
  ];

  // Section 2: Workspace / Practice Cards
  const workspaceTools = [
    {
      id: "saved-charts",
      titleTa: "சேமிக்கப்பட்ட ஜாதகங்கள்",
      titleEn: "Saved Horoscopes",
      href: "/horoscopes",
      icon: Database,
      color: "text-[#B4872B] border-[#B4872B]/40 bg-[#FAF2DE]/50",
    },
    {
      id: "birthdays",
      titleTa: "பிறந்தநாள் நினைவூட்டல்",
      titleEn: "Birthday Reminders",
      action: () => setIsBirthdayOpen(true),
      icon: Cake,
      color: "text-amber-600 border-amber-300 bg-amber-50",
    },
    {
      id: "caution-alerts",
      titleTa: "கண்ட கால எச்சரிக்கை",
      titleEn: "Dasa Caution Alerts",
      action: () => setIsCautionOpen(true),
      icon: ShieldAlert,
      color: "text-rose-600 border-rose-300 bg-rose-50",
    },
    {
      id: "instant-revelation",
      titleTa: "நேரடி வாக்கு பலகை",
      titleEn: "Instant Revelation",
      href: "/tools/instant-revelation",
      icon: Flame,
      color: "text-rose-700 border-rose-300 bg-rose-50/70",
    },
  ];

  return (
    <div className="w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 sm:py-8 space-y-8">
      {/* Breadcrumb Navigation */}
      <Breadcrumbs
        items={[
          {
            label: language === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools",
          },
        ]}
      />

      {/* Section 1: ஜோதிடக் கருவிகள் (Astrology Tools) */}
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 shrink-0">
            <Layers className="w-5 h-5 text-[#B4872B]" />
            <h2 className="text-base sm:text-lg font-bold text-[#183047]">
              {language === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools"}
            </h2>
          </div>
          <div className="flex-1 h-px bg-[#D9DEE7]" />
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-3 sm:gap-4">
          {astrologyTools.map((card) => {
            const Icon = card.icon;
            return (
              <Link
                key={card.id}
                href={card.href}
                title={
                  (language === "ta" ? card.descriptionTa : card.descriptionEn) ||
                  (language === "ta" ? card.titleTa : card.titleEn)
                }
                className="h-28 sm:h-32 rounded-xl bg-white border border-[#D9DEE7] hover:border-[#B4872B] p-2.5 sm:p-3 flex flex-col items-center justify-center text-center shadow-xs hover:shadow-md transition-all group"
              >
                <div
                  className={`w-10 h-10 sm:w-11 sm:h-11 rounded-full border flex items-center justify-center mb-2 group-hover:scale-105 transition-transform ${card.color}`}
                >
                  <Icon className="w-5 h-5 sm:w-6 sm:h-6" />
                </div>
                <div className="text-xs sm:text-sm font-semibold text-[#183047] group-hover:text-[#153F6B] leading-tight line-clamp-2">
                  {language === "ta" ? card.titleTa : card.titleEn}
                </div>
                <div className="text-[10px] text-[#8190A6] mt-0.5 truncate hidden sm:block">
                  {language === "ta" ? card.titleEn : card.titleTa}
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Section 2: என் பயிற்சி (My Workspace / Practice) */}
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 shrink-0">
            <Briefcase className="w-5 h-5 text-[#B4872B]" />
            <h2 className="text-base sm:text-lg font-bold text-[#183047]">
              {language === "ta" ? "என் பயிற்சி" : "My Practice"}
            </h2>
          </div>
          <div className="flex-1 h-px bg-[#D9DEE7]" />
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-4 gap-3 sm:gap-4">
          {workspaceTools.map((card) => {
            const Icon = card.icon;
            if (card.action) {
              return (
                <button
                  key={card.id}
                  type="button"
                  onClick={card.action}
                  className="h-28 sm:h-32 rounded-xl bg-white border border-[#D9DEE7] hover:border-[#B4872B] p-2.5 sm:p-3 flex flex-col items-center justify-center text-center shadow-xs hover:shadow-md transition-all group cursor-pointer"
                >
                  <div
                    className={`w-10 h-10 sm:w-11 sm:h-11 rounded-full border flex items-center justify-center mb-2 group-hover:scale-105 transition-transform ${card.color}`}
                  >
                    <Icon className="w-5 h-5 sm:w-6 sm:h-6" />
                  </div>
                  <div className="text-xs sm:text-sm font-semibold text-[#183047] group-hover:text-[#153F6B] leading-tight line-clamp-2">
                    {language === "ta" ? card.titleTa : card.titleEn}
                  </div>
                  <div className="text-[10px] text-[#8190A6] mt-0.5 truncate hidden sm:block">
                    {language === "ta" ? card.titleEn : card.titleTa}
                  </div>
                </button>
              );
            }

            return (
              <Link
                key={card.id}
                href={card.href!}
                className="h-28 sm:h-32 rounded-xl bg-white border border-[#D9DEE7] hover:border-[#B4872B] p-2.5 sm:p-3 flex flex-col items-center justify-center text-center shadow-xs hover:shadow-md transition-all group"
              >
                <div
                  className={`w-10 h-10 sm:w-11 sm:h-11 rounded-full border flex items-center justify-center mb-2 group-hover:scale-105 transition-transform ${card.color}`}
                >
                  <Icon className="w-5 h-5 sm:w-6 sm:h-6" />
                </div>
                <div className="text-xs sm:text-sm font-semibold text-[#183047] group-hover:text-[#153F6B] leading-tight line-clamp-2">
                  {language === "ta" ? card.titleTa : card.titleEn}
                </div>
                <div className="text-[10px] text-[#8190A6] mt-0.5 truncate hidden sm:block">
                  {language === "ta" ? card.titleEn : card.titleTa}
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Engine & Calculation Integrity Banner */}
      <div className="p-4 rounded-2xl bg-white border border-[#D9DEE7] flex items-center gap-3 text-xs text-[#52667E] shadow-2xs">
        <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0" />
        <p className="leading-relaxed">
          <strong>{language === "ta" ? "துல்லியமான எஃபிமெரிஸ் கணிதம்:" : "Deterministic Ephemeris:"}</strong>{" "}
          {language === "ta"
            ? "அனைத்து கிரக நிலைகள், கே.பி. உப-அதிபதிகள் மற்றும் தசா காலங்கள் சுவிஸ் எஃபிமெரிஸ் மற்றும் XALEN வானியல் முறையின் மூலம் நேரடியாகக் கணக்கிடப்படுகின்றன."
            : "All planetary positions, KP cusps, and Dasa periods operate on verified astronomical formulas powered by the XALEN computational core."}
        </p>
      </div>

      {/* Modals */}
      <BirthdayReminderModal isOpen={isBirthdayOpen} onClose={() => setIsBirthdayOpen(false)} />
      <DasaCautionReminderModal isOpen={isCautionOpen} onClose={() => setIsCautionOpen(false)} />
    </div>
  );
}
