"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  Compass,
  Sparkles,
  Layers,
  Calendar,
  Flame,
  Database,
  User,
  Settings,
  Cake,
  Phone,
  BookOpen,
  GraduationCap,
  Activity,
  HeartHandshake,
  Heart,
  ShieldCheck,
  Search,
  Hash,
  Briefcase,
  Grid,
  Zap,
} from "lucide-react";
import { BirthdayReminderModal } from "@/components/birthday/BirthdayReminderModal";
import { HelpModal } from "@/components/layout/HelpModal";

export default function AstrologyToolsPage() {
  const router = useRouter();
  const { language, t } = useLanguage();
  const { user, isAuthenticated, isLoading } = useAuth();
  const [isBirthdayOpen, setIsBirthdayOpen] = useState(false);
  const [isHelpOpen, setIsHelpOpen] = useState(false);

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
      id: "ashtakavarga",
      titleTa: "அஷ்டகவர்க்கம் & கக்ஷா கோச்சாரம்",
      titleEn: "Ashtakavarga & Kakshya Studio",
      href: "/tools/ashtakavarga",
      icon: Grid,
      color: "text-indigo-600 border-indigo-300 bg-indigo-50",
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
      id: "remedies",
      titleTa: "பரிகாரங்கள் & ஆலயங்கள்",
      titleEn: "Remedies & Pariharam",
      href: "/remedies",
      icon: Flame,
      color: "text-amber-700 border-amber-300 bg-amber-50",
    },
  ];

  // Section 2: Workspace / Practice Cards
  const workspaceTools = [
    {
      id: "profile",
      titleTa: "எனது சுயவிவரம்",
      titleEn: "My Profile",
      href: "/dashboard",
      icon: User,
      color: "text-[#153F6B] border-[#153F6B]/30 bg-[#EBF2FE]",
    },
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
      id: "contacts",
      titleTa: "வாடிக்கையாளர் தொடர்புகள்",
      titleEn: "Customer Contacts",
      href: "/horoscopes",
      icon: Phone,
      color: "text-emerald-600 border-emerald-300 bg-emerald-50",
    },
    {
      id: "settings",
      titleTa: "அமைப்புகள்",
      titleEn: "Account & Settings",
      href: "/dashboard",
      icon: Settings,
      color: "text-[#8190A6] border-slate-300 bg-slate-50",
    },
  ];

  // Section 3: Resources
  const resourceTools = [
    {
      id: "remedies-guide",
      titleTa: "நவகிரக ஆலயங்கள் & மந்திரங்கள்",
      titleEn: "Temples & Mantras",
      href: "/remedies",
      icon: Flame,
      color: "text-amber-600 border-amber-300 bg-amber-50",
    },
    {
      id: "ephemeris",
      titleTa: "எஃபிமெரிஸ் கணித முறை",
      titleEn: "XALEN Ephemeris Engine",
      href: "/dashboard",
      icon: Activity,
      color: "text-emerald-600 border-emerald-300 bg-emerald-50",
    },
    {
      id: "platform-guide",
      titleTa: "தள வழிகாட்டி & ஆவணங்கள்",
      titleEn: "Help & User Guide",
      action: () => setIsHelpOpen(true),
      icon: GraduationCap,
      color: "text-indigo-600 border-indigo-300 bg-indigo-50",
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

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 sm:gap-4">
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
                className="h-32 sm:h-36 rounded-2xl bg-white border border-[#D9DEE7] hover:border-[#B4872B] p-3 sm:p-4 flex flex-col items-center justify-center text-center shadow-xs hover:shadow-md transition-all group"
              >
                <div
                  className={`w-11 h-11 sm:w-12 sm:h-12 rounded-full border flex items-center justify-center mb-2.5 group-hover:scale-105 transition-transform ${card.color}`}
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

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 sm:gap-4">
          {workspaceTools.map((card) => {
            const Icon = card.icon;
            if (card.action) {
              return (
                <button
                  key={card.id}
                  type="button"
                  onClick={card.action}
                  className="h-32 sm:h-36 rounded-2xl bg-white border border-[#D9DEE7] hover:border-[#B4872B] p-3 sm:p-4 flex flex-col items-center justify-center text-center shadow-xs hover:shadow-md transition-all group cursor-pointer"
                >
                  <div
                    className={`w-11 h-11 sm:w-12 sm:h-12 rounded-full border flex items-center justify-center mb-2.5 group-hover:scale-105 transition-transform ${card.color}`}
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
                className="h-32 sm:h-36 rounded-2xl bg-white border border-[#D9DEE7] hover:border-[#B4872B] p-3 sm:p-4 flex flex-col items-center justify-center text-center shadow-xs hover:shadow-md transition-all group"
              >
                <div
                  className={`w-11 h-11 sm:w-12 sm:h-12 rounded-full border flex items-center justify-center mb-2.5 group-hover:scale-105 transition-transform ${card.color}`}
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

      {/* Section 3: ஆதாரங்கள் (Resources) */}
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 shrink-0">
            <BookOpen className="w-5 h-5 text-[#B4872B]" />
            <h2 className="text-base sm:text-lg font-bold text-[#183047]">
              {language === "ta" ? "ஆதாரங்கள்" : "Resources"}
            </h2>
          </div>
          <div className="flex-1 h-px bg-[#D9DEE7]" />
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 sm:gap-4">
          {resourceTools.map((card) => {
            const Icon = card.icon;
            if (card.action) {
              return (
                <button
                  key={card.id}
                  type="button"
                  onClick={card.action}
                  className="h-32 sm:h-36 rounded-2xl bg-white border border-[#D9DEE7] hover:border-[#B4872B] p-3 sm:p-4 flex flex-col items-center justify-center text-center shadow-xs hover:shadow-md transition-all group cursor-pointer"
                >
                  <div
                    className={`w-11 h-11 sm:w-12 sm:h-12 rounded-full border flex items-center justify-center mb-2.5 group-hover:scale-105 transition-transform ${card.color}`}
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
                className="h-32 sm:h-36 rounded-2xl bg-white border border-[#D9DEE7] hover:border-[#B4872B] p-3 sm:p-4 flex flex-col items-center justify-center text-center shadow-xs hover:shadow-md transition-all group"
              >
                <div
                  className={`w-11 h-11 sm:w-12 sm:h-12 rounded-full border flex items-center justify-center mb-2.5 group-hover:scale-105 transition-transform ${card.color}`}
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
      <HelpModal isOpen={isHelpOpen} onClose={() => setIsHelpOpen(false)} />
    </div>
  );
}
