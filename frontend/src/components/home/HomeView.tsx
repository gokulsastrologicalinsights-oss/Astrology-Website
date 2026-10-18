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
  ChevronRight,
  User,
  PlusCircle,
  ExternalLink,
  HeartHandshake,
  Hash,
  Home as HomeIcon,
  Flame,
  Briefcase,
  Settings,
  Cake,
  Phone,
  Eye,
  CalendarCheck,
} from "lucide-react";
import { BirthdayReminderModal } from "@/components/birthday/BirthdayReminderModal";

export function HomeView() {
  const { language, t } = useLanguage();
  const { user } = useAuth();
  const [recentHoroscopes, setRecentHoroscopes] = useState<SavedHoroscopeItem[]>([]);
  const [isLoadingRecent, setIsLoadingRecent] = useState(true);
  const [isBirthdayOpen, setIsBirthdayOpen] = useState(false);

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

  // Section 1: Astrology Tools Cards (matching Screenshot 1)
  const astrologyTools = [
    {
      id: "horoscope",
      titleTa: "ஜாதகம் (வேத & கே.பி)",
      titleEn: "Horoscope (Vedic & KP)",
      href: "/tools/horoscope",
      icon: Compass,
      color: "text-[#B4872B] border-[#B4872B]/40 bg-[#FAF2DE]/50",
    },
    {
      id: "marriage",
      titleTa: "திருமணப் பொருத்தம்",
      titleEn: "Porutham & Match",
      href: "/tools/horoscope",
      icon: HeartHandshake,
      color: "text-[#153F6B] border-[#153F6B]/30 bg-[#EBF2FE]",
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
      titleTa: "D1/D9 சக்கரங்கள்",
      titleEn: "D1 Rasi & D9 Navamsa",
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
      icon: CalendarCheck,
      color: "text-emerald-600 border-emerald-300 bg-emerald-50",
    },
    {
      id: "vastu",
      titleTa: "வாஸ்து சாஸ்திரம்",
      titleEn: "Vastu Shastra Assessment",
      href: "/vastu",
      icon: HomeIcon,
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

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-8">
      {/* 1. Personalized Welcome Header */}
      <div className="rounded-2xl bg-white border border-[#D9DEE7] p-5 sm:p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#B4872B]" />
            <span className="text-xs font-bold uppercase tracking-wider text-[#B4872B]">
              Gokul’s Astrological Insights
            </span>
          </div>
          <h1 className="font-serif text-xl sm:text-2xl lg:text-3xl font-bold text-[#183047] tracking-tight">
            {greeting}, {user?.displayName || user?.username || "Aspirant"}!
          </h1>
          <p className="text-xs sm:text-sm text-[#8190A6] max-w-2xl">
            {language === "ta"
              ? "துல்லியமான வேத மற்றும் கே.பி வானியல் எஃபிமெரிஸ் தளம். உங்கள் ஜாதகங்கள் மற்றும் பகுப்பாய்வுகளை அணுகுங்கள்."
              : "Welcome to precision Vedic and KP Krishnamurti Paddhati astrology powered by the XALEN astronomical engine."}
          </p>
        </div>

        <div className="flex items-center gap-2.5 flex-wrap">
          <Link
            href="/horoscope"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white bg-[#153F6B] hover:bg-[#0F3155] shadow-xs transition-colors"
          >
            <Compass className="w-3.5 h-3.5 text-[#B4872B]" />
            <span>{language === "ta" ? "+ ஜாதகம் உருவாக்கு" : "+ Create Horoscope"}</span>
          </Link>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-[#183047] bg-white hover:bg-[#F2F3F5] border border-[#D9DEE7] shadow-2xs transition-colors"
          >
            <span>{t.navDashboard}</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* 2. Section 1: ஜோதிடக் கருவிகள் (Astrology Tools Cards) */}
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

      {/* 3. Section 2: என் பயிற்சி (Workspace / Practice Cards) */}
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

      {/* 4. Recent Saved Horoscopes Preview (Screenshot 2 3-column card style) */}
      <div className="rounded-2xl border border-[#D9DEE7] bg-white p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-[#D9DEE7]">
          <div className="flex items-center gap-2">
            <Database className="w-5 h-5 text-[#B4872B]" />
            <h3 className="font-serif text-base sm:text-lg font-bold text-[#183047]">
              {t.homeRecentCharts || "Recent Saved Horoscopes"}
            </h3>
          </div>
          <Link
            href="/horoscopes"
            className="text-xs font-semibold text-[#153F6B] hover:underline inline-flex items-center gap-1"
          >
            <span>{language === "ta" ? "அனைத்தையும் காண்க" : "View All"}</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {isLoadingRecent ? (
          <div className="py-8 text-center text-xs text-[#8190A6]">
            <div className="inline-block animate-spin w-5 h-5 border-2 border-[#B4872B] border-t-transparent rounded-full mb-2" />
            <p>{t.loading}</p>
          </div>
        ) : recentHoroscopes.length === 0 ? (
          <div className="py-8 px-4 text-center rounded-xl border border-dashed border-[#D9DEE7] bg-[#F2F3F5]">
            <Compass className="w-8 h-8 text-[#8190A6] mx-auto mb-2" />
            <p className="text-xs text-[#8190A6]">
              {language === "ta"
                ? "இதுவரை ஜாதகங்கள் எதுவும் சேமிக்கப்படவில்லை. புதிய ஜாதகத்தைக் கணக்கிடுங்கள்."
                : "No saved horoscopes found. Generate your first precision chart to see it here."}
            </p>
            <div className="mt-3">
              <Link
                href="/horoscope"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white bg-[#153F6B] hover:bg-[#0F3155]"
              >
                <PlusCircle className="w-3.5 h-3.5 text-[#B4872B]" />
                <span>{language === "ta" ? "புதிய ஜாதகம் கணிக்க" : "Create Horoscope"}</span>
              </Link>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {recentHoroscopes.map((item) => {
              const initial = item.person_name?.trim()?.charAt(0)?.toUpperCase() || "H";
              return (
                <div
                  key={item.id}
                  className="p-4 rounded-xl border border-[#D9DEE7] hover:border-[#B4872B] bg-white shadow-2xs hover:shadow-xs transition-all flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-start justify-between gap-3 mb-3">
                      <div className="flex items-center gap-2.5 min-w-0">
                        <div className="w-10 h-10 rounded-full bg-[#153F6B] text-white flex items-center justify-center font-bold text-sm shrink-0 border border-[#B4872B]/30">
                          {initial}
                        </div>
                        <div className="min-w-0">
                          <div className="flex items-center gap-1.5">
                            <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-[#FAF2DE] text-[#B4872B] border border-[#D8BD80]">
                              {formatSerialNumber(item.display_number)}
                            </span>
                            <h4 className="font-bold text-sm text-[#183047] truncate">
                              {item.person_name}
                            </h4>
                          </div>
                          <div className="text-[11px] text-[#8190A6] flex items-center gap-1 mt-0.5">
                            <Calendar className="w-3 h-3 text-[#8190A6] shrink-0" />
                            <span>{item.birth_date} {item.birth_time}</span>
                          </div>
                        </div>
                      </div>

                      <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-[#F2F3F5] text-[#8190A6] border border-[#D9DEE7] shrink-0">
                        TA
                      </span>
                    </div>

                    <div className="text-xs text-[#8190A6] flex items-center gap-1.5 truncate">
                      <span>📍 {item.birthplace || "India"}</span>
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-[#F2F3F5] flex items-center justify-between">
                    <span className="text-[10px] text-[#8190A6]">
                      {new Date(item.created_at).toLocaleDateString()}
                    </span>

                    <Link
                      href={`/horoscope/results?id=${item.id}`}
                      className="inline-flex items-center gap-1 px-3 py-1 rounded-lg border border-[#D9DEE7] hover:border-[#153F6B] text-xs font-semibold text-[#153F6B] hover:bg-[#EBF2FE] transition-colors"
                    >
                      <Eye className="w-3 h-3 text-[#153F6B]" />
                      <span>{language === "ta" ? "காண்க" : "View"}</span>
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* 5. Engine & Data Integrity Notice */}
      <div className="p-4 rounded-2xl bg-white border border-[#D9DEE7] flex items-center gap-3 shadow-2xs text-xs text-[#52667E]">
        <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0" />
        <p className="leading-relaxed">
          <strong>Deterministic Ephemeris:</strong> All planetary coordinates, KP cusp sub-lords, and Dasa periods are calculated through verified algorithms. Saved horoscopes and numerology reports are stored in your secure Supabase account with sequential numbering.
        </p>
      </div>

      {/* Birthday Reminder Modal */}
      <BirthdayReminderModal
        isOpen={isBirthdayOpen}
        onClose={() => setIsBirthdayOpen(false)}
      />
    </div>
  );
}
