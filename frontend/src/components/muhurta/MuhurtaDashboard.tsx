"use client";

import React, { useState, useEffect } from "react";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { getOccasions, listSavedMuhurtas, getDailyPanchang } from "@/lib/api";
import { SavedMuhurtaItem, OccasionItem } from "@/lib/types";
import {
  Sparkles,
  Calendar,
  Clock,
  MapPin,
  Bookmark,
  Sun,
  Moon,
  Compass,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Heart,
  Home,
  Briefcase,
  Car,
  GraduationCap,
  Sparkle,
} from "lucide-react";

interface MuhurtaDashboardProps {
  onTabChange: (tab: string, occasionCode?: string) => void;
}

export function MuhurtaDashboard({ onTabChange }: MuhurtaDashboardProps) {
  const { language } = useLanguage();
  const { session } = useAuth();

  const [occasions, setOccasions] = useState<OccasionItem[]>([]);
  const [savedCount, setSavedCount] = useState<number>(0);
  const [recentSaved, setRecentSaved] = useState<SavedMuhurtaItem[]>([]);
  const [todayPanchang, setTodayPanchang] = useState<Record<string, any> | null>(null);
  const [loading, setLoading] = useState(true);

  const todayStr = new Date().toISOString().split("T")[0];

  useEffect(() => {
    const token = session?.access_token || "cookie";

    Promise.allSettled([
      getOccasions(),
      listSavedMuhurtas(token, 5, 0),
      getDailyPanchang({
        date: todayStr,
        latitude: 13.0827,
        longitude: 80.2707,
        timezone: "Asia/Kolkata",
        ayanamsa_id: 0,
      }),
    ]).then(([occRes, savedRes, panRes]) => {
      if (occRes.status === "fulfilled" && occRes.value?.occasions) {
        setOccasions(occRes.value.occasions);
      }
      if (savedRes.status === "fulfilled" && savedRes.value) {
        setSavedCount(savedRes.value.count || 0);
        setRecentSaved(savedRes.value.items || []);
      }
      if (panRes.status === "fulfilled" && panRes.value) {
        setTodayPanchang(panRes.value);
      }
      setLoading(false);
    });
  }, [session, todayStr]);

  const categories = [
    {
      id: "marriage_relationships",
      code: "marriage",
      en: "Marriage & Relationships",
      ta: "திருமணம் / நிச்சயதார்த்தம்",
      icon: Heart,
      color: "from-rose-500 to-pink-600",
    },
    {
      id: "home_property",
      code: "griha_pravesham",
      en: "Housewarming & Property",
      ta: "கிரகப்பிரவேசம் / பூமி பூஜை",
      icon: Home,
      color: "from-amber-500 to-orange-600",
    },
    {
      id: "business_professional",
      code: "shop_opening",
      en: "Business & Ventures",
      ta: "தொழில் தொடக்கம் / திறப்பு விழா",
      icon: Briefcase,
      color: "from-blue-500 to-indigo-600",
    },
    {
      id: "family_ceremonies",
      code: "namakaranam",
      en: "Family Ceremonies",
      ta: "பெயரிடுதல் / அன்னப்பிராசனம்",
      icon: Sparkles,
      color: "from-purple-500 to-violet-600",
    },
    {
      id: "travel_vehicles",
      code: "vehicle_purchase",
      en: "Vehicles & Travel",
      ta: "வாகனம் வாங்குதல் / பயணம்",
      icon: Car,
      color: "from-emerald-500 to-teal-600",
    },
    {
      id: "education_spiritual",
      code: "vidyarambham",
      en: "Education & Vidyarambham",
      ta: "வித்யாரம்பம் / கல்வி தொடக்கம்",
      icon: GraduationCap,
      color: "from-cyan-500 to-blue-600",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Hero Welcome Banner */}
      <div className="bg-gradient-to-r from-[#201538] via-[#2F1E4E] to-[#1F1735] text-white p-7 sm:p-10 rounded-3xl shadow-xl border border-amber-500/20 relative overflow-hidden">
        <div className="absolute top-0 right-0 -mr-20 -mt-20 w-80 h-80 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-amber-400/20 text-amber-300 border border-amber-400/30">
            <Sparkles className="w-4 h-4 text-amber-300" />
            <span>
              {language === "ta"
                ? "கோகுலின் ஜோதிட நுண்ணறிவு • முகூர்த்த கணித அமைப்பு"
                : "Gokul's Astrological Insights • Vedic Muhurta Module"}
            </span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-white leading-tight">
            {language === "ta"
              ? "துல்லியமான சுப முகூர்த்தம் & பஞ்சாங்கக் கணிப்பான்"
              : "Vedic Muhurta & Panchangam Calculation Engine"}
          </h1>

          <p className="text-sm sm:text-base text-purple-200/90 leading-relaxed">
            {language === "ta"
              ? "சுவிஸ் எபிமெரிஸ் கணித முறைப்படி, ராகு காலம், எமகண்டம், வர்ஜியம் தவிர்ந்து, தாரா பலம், சந்திர பலம் மற்றும் சுப லக்ன சுத்தியுடன் கூடிய உன்னத முகூர்த்தங்களை கண்டறிந்து அச்சிடலாம்."
              : "Discover, filter, rank, save, and print auspicious time windows for all major life ceremonies using astronomical Meeus/NOAA calculations and classical Panchanga rules."}
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <button
              type="button"
              onClick={() => onTabChange("find")}
              className="px-6 py-3 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-950 font-extrabold rounded-2xl shadow-lg transition-all text-xs sm:text-sm flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              <span>{language === "ta" ? "சுப முகூர்த்தம் தேடு" : "Find Auspicious Dates"}</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              type="button"
              onClick={() => onTabChange("panchang")}
              className="px-5 py-3 bg-white/10 hover:bg-white/15 border border-white/20 text-white font-bold rounded-2xl text-xs sm:text-sm flex items-center gap-2 transition-colors backdrop-blur-sm"
            >
              <Sun className="w-4 h-4 text-amber-300" />
              <span>{language === "ta" ? "இன்றைய பஞ்சாங்கம்" : "Today's Panchangam"}</span>
            </button>

            <button
              type="button"
              onClick={() => onTabChange("saved")}
              className="px-5 py-3 bg-white/10 hover:bg-white/15 border border-white/20 text-white font-bold rounded-2xl text-xs sm:text-sm flex items-center gap-2 transition-colors backdrop-blur-sm"
            >
              <Bookmark className="w-4 h-4 text-amber-300" />
              <span>{language === "ta" ? "சேமிக்கப்பட்டவை" : "Saved Muhurtas"}</span>
            </button>
          </div>
        </div>
      </div>

      {/* 4 KPI Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* KPI 1: Supported Occasions */}
        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-700 flex items-center justify-center flex-shrink-0 border border-amber-100">
            <Sparkle className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-black text-slate-900">
              {occasions.length > 0 ? occasions.length : "18+"}
            </div>
            <div className="text-xs font-semibold text-slate-500 mt-0.5">
              {language === "ta" ? "சுப நிகழ்வு வகைகள்" : "Ceremony Categories"}
            </div>
          </div>
        </div>

        {/* KPI 2: Saved Muhurtas */}
        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-purple-50 text-purple-700 flex items-center justify-center flex-shrink-0 border border-purple-100">
            <Bookmark className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-black text-slate-900">{savedCount}</div>
            <div className="text-xs font-semibold text-slate-500 mt-0.5">
              {language === "ta" ? "சேமிக்கப்பட்ட முகூர்த்தங்கள்" : "Saved Muhurta Records"}
            </div>
          </div>
        </div>

        {/* KPI 3: Today's Nakshatra */}
        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center flex-shrink-0 border border-emerald-100">
            <Sun className="w-6 h-6" />
          </div>
          <div>
            <div className="text-base font-extrabold text-slate-900 truncate">
              {todayPanchang?.nakshatra?.name || "Loading..."}
            </div>
            <div className="text-xs font-semibold text-slate-500 mt-0.5">
              {todayPanchang?.tithi?.name || "Today's Panchang"}
            </div>
          </div>
        </div>

        {/* KPI 4: Ephemeris Engine */}
        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-700 flex items-center justify-center flex-shrink-0 border border-blue-100">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="text-base font-extrabold text-slate-900">Swiss Ephemeris</div>
            <div className="text-xs font-semibold text-slate-500 mt-0.5">
              Sub-second NOAA / Meeus
            </div>
          </div>
        </div>
      </div>

      {/* Today's Daylight Panchanga & Auspicious Periods Banner */}
      {todayPanchang && (
        <div className="bg-white rounded-3xl p-6 sm:p-7 border border-slate-200 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
            <div>
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Sun className="w-4 h-4 text-amber-600" />
                <span>{language === "ta" ? "இன்றைய பஞ்சாங்கக் காலங்கள்" : "Today's Astronomical Periods"}</span>
              </h3>
              <div className="text-xs text-slate-500 mt-0.5">
                📍 {todayPanchang.location?.city_name || "Chennai, India"} • {todayStr} ({todayPanchang.vara?.name})
              </div>
            </div>

            <button
              type="button"
              onClick={() => onTabChange("panchang")}
              className="text-xs font-bold text-amber-700 hover:text-amber-800 flex items-center gap-1"
            >
              <span>{language === "ta" ? "முழு பஞ்சாங்கம் காண்க" : "View Full Panchangam"}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Quick Limbs Pills */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100">
              <span className="text-[10px] text-slate-400 block font-bold uppercase">
                {language === "ta" ? "திதி" : "Tithi"}
              </span>
              <div className="font-extrabold text-slate-900 mt-0.5">
                {todayPanchang.tithi?.name}
              </div>
              <div className="text-slate-500 text-[11px]">
                {todayPanchang.tithi?.paksha}
              </div>
            </div>

            <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100">
              <span className="text-[10px] text-slate-400 block font-bold uppercase">
                {language === "ta" ? "நட்சத்திரம்" : "Nakshatra"}
              </span>
              <div className="font-extrabold text-slate-900 mt-0.5">
                {todayPanchang.nakshatra?.name}
              </div>
              <div className="text-slate-500 text-[11px]">
                Lord: {todayPanchang.nakshatra?.lord}
              </div>
            </div>

            <div className="p-3 rounded-2xl bg-rose-50/70 border border-rose-100">
              <span className="text-[10px] text-rose-500 block font-bold uppercase">
                {language === "ta" ? "ராகு காலம்" : "Rahu Kalam"}
              </span>
              <div className="font-extrabold text-rose-900 mt-0.5">
                {todayPanchang.inauspicious_periods?.rahu_kalam?.start} – {todayPanchang.inauspicious_periods?.rahu_kalam?.end}
              </div>
              <div className="text-rose-600 text-[11px]">
                🚫 Inauspicious
              </div>
            </div>

            <div className="p-3 rounded-2xl bg-emerald-50/70 border border-emerald-100">
              <span className="text-[10px] text-emerald-600 block font-bold uppercase">
                {language === "ta" ? "அபிஜித் முகூர்த்தம்" : "Abhijit Muhurta"}
              </span>
              <div className="font-extrabold text-emerald-900 mt-0.5">
                {todayPanchang.auspicious_periods?.abhijit?.start} – {todayPanchang.auspicious_periods?.abhijit?.end}
              </div>
              <div className="text-emerald-700 text-[11px]">
                ✓ Highly Auspicious
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Occasion Quick Launchers */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Sparkle className="w-4 h-4 text-amber-600" />
            <span>{language === "ta" ? "சுப நிகழ்வுகள் வகைப்பாடு" : "Ceremony Categories"}</span>
          </h3>
          <button
            type="button"
            onClick={() => onTabChange("find")}
            className="text-xs font-bold text-amber-700 hover:text-amber-800 flex items-center gap-1"
          >
            <span>{language === "ta" ? "அனைத்து முகூர்த்தங்கள்" : "Browse All"}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {categories.map((cat) => {
            const Icon = cat.icon;
            return (
              <button
                key={cat.id}
                type="button"
                onClick={() => onTabChange("find", cat.code)}
                className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm hover:shadow-md hover:border-amber-300 text-left transition-all group flex items-start justify-between"
              >
                <div>
                  <div
                    className={`w-10 h-10 rounded-2xl bg-gradient-to-tr ${cat.color} text-white flex items-center justify-center shadow-md mb-3`}
                  >
                    <Icon className="w-5 h-5" />
                  </div>
                  <h4 className="text-sm font-extrabold text-slate-900 group-hover:text-amber-700 transition-colors">
                    {cat.en}
                  </h4>
                  <div className="text-xs text-amber-700 font-tamil font-semibold mt-0.5">
                    {cat.ta}
                  </div>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-300 group-hover:text-amber-600 group-hover:translate-x-1 transition-all mt-2" />
              </button>
            );
          })}
        </div>
      </div>

      {/* Recent Saved Muhurtas */}
      {recentSaved.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Bookmark className="w-4 h-4 text-amber-600" />
              <span>{language === "ta" ? "அண்மையில் சேமிக்கப்பட்டவை" : "Recently Saved Muhurtas"}</span>
            </h3>
            <button
              type="button"
              onClick={() => onTabChange("saved")}
              className="text-xs font-bold text-amber-700 hover:text-amber-800 flex items-center gap-1"
            >
              <span>{language === "ta" ? "அனைத்தும் காண்க" : "View All Saved"}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {recentSaved.slice(0, 3).map((item) => (
              <div
                key={item.id}
                className="bg-white rounded-3xl p-5 border border-slate-200 shadow-sm hover:shadow-md transition-shadow space-y-3"
              >
                <div className="flex items-center justify-between">
                  <span className="w-7 h-7 rounded-xl bg-amber-100 text-amber-900 font-extrabold text-xs flex items-center justify-center font-mono">
                    #{item.display_number}
                  </span>
                  <span className="text-xs font-bold text-amber-800">{item.score}/100</span>
                </div>

                <div>
                  <h4 className="text-sm font-extrabold text-slate-900 truncate">
                    {item.title}
                  </h4>
                  <div className="text-xs text-slate-500 flex items-center gap-1 mt-1">
                    <Calendar className="w-3.5 h-3.5 text-slate-400" />
                    <span>{item.event_date} ({item.local_start_time} - {item.local_end_time})</span>
                  </div>
                </div>

                <div className="text-[11px] text-slate-600 pt-2 border-t border-slate-100 flex items-center justify-between">
                  <span>Lagna: <b>{item.lagna_summary?.sign_name || "N/A"}</b></span>
                  <span className="truncate max-w-[120px] text-slate-400">{item.location_name}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
