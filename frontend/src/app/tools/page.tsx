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
  Clock,
  Home,
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
      titleTa: "திருமணப் பொருத்தம்",
      titleEn: "Porutham & Match",
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
      titleTa: "தினசரி பஞ்சாங்கம்",
      titleEn: "Daily Panchangam",
      href: "/muhurta",
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
      id: "transit-watch",
      titleTa: "கோச்சார ஜாதகம்",
      titleEn: "KP Transit Watch",
      href: "/tools/transit-watch",
      icon: Clock,
      color: "text-teal-600 border-teal-300 bg-teal-50",
    },
    {
      id: "d1-d9",
      titleTa: "வர்க்க சக்கரங்கள் (D1 - D60)",
      titleEn: "Divisional Charts (D1 - D60)",
      href: "/tools/d1-d9",
      icon: Compass,
      color: "text-[#153F6B] border-[#153F6B]/30 bg-[#EBF2FE]",
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
      titleTa: "சுப முகூர்த்தம்",
      titleEn: "Muhurta Finder",
      href: "/muhurta",
      icon: Calendar,
      color: "text-emerald-600 border-emerald-300 bg-emerald-50",
    },
    {
      id: "vastu",
      titleTa: "வாஸ்து சாஸ்திரம்",
      titleEn: "Vastu Shastra Assessment",
      href: "/vastu",
      icon: Home,
      color: "text-cyan-600 border-cyan-300 bg-cyan-50",
    },
    {
      id: "remedies",
      titleTa: "பரிகாரங்கள் & ஆலயங்கள்",
      titleEn: "Remedies & Pariharam",
      href: "/remedies",
      icon: Flame,
      color: "text-amber-700 border-amber-300 bg-amber-50",
    },
    {
      id: "destiny-card",
      titleTa: "விதி அட்டை",
      titleEn: "Destiny Card Snapshot",
      href: "/tools/horoscope?tab=destiny-card",
      icon: Sparkles,
      color: "text-purple-600 border-purple-300 bg-purple-50",
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
      id: "vastu-guide",
      titleTa: "வாஸ்து சாஸ்திர விதிகள்",
      titleEn: "Vastu Shastra Principles",
      href: "/vastu",
      icon: Home,
      color: "text-blue-600 border-blue-300 bg-blue-50",
    },
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
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-8">
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
