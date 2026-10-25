"use client";

import React, { useState, useEffect, useMemo, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  PanchaPakshiResponse,
  AntaraSlot,
  YamamSlot,
  BirdItem,
} from "@/lib/types";
import { calculatePanchaPakshi, getPanchaPakshiBirds } from "@/lib/api";
import {
  Sparkles,
  Clock,
  Calendar,
  Compass,
  MapPin,
  RefreshCw,
  AlertCircle,
  ShieldAlert,
  ShieldCheck,
  ChevronLeft,
  ChevronRight,
  Flame,
  CheckCircle2,
  XCircle,
  Info,
  Timer,
  Zap,
  Award,
  Sun,
  Moon,
  ArrowRight,
  HelpCircle,
} from "lucide-react";

interface CityPreset {
  name_en: string;
  name_ta: string;
  lat: number;
  lon: number;
  tz: string;
}

const CITY_PRESETS: CityPreset[] = [
  { name_en: "Chennai", name_ta: "சென்னை", lat: 13.0827, lon: 80.2707, tz: "Asia/Kolkata" },
  { name_en: "Madurai", name_ta: "மதுரை", lat: 9.9252, lon: 78.1198, tz: "Asia/Kolkata" },
  { name_en: "Coimbatore", name_ta: "கோயம்புத்தூர்", lat: 11.0168, lon: 76.9558, tz: "Asia/Kolkata" },
  { name_en: "Tiruchirappalli", name_ta: "திருச்சி", lat: 10.7905, lon: 78.7047, tz: "Asia/Kolkata" },
  { name_en: "Bengaluru", name_ta: "பெங்களூரு", lat: 12.9716, lon: 77.5946, tz: "Asia/Kolkata" },
  { name_en: "Mumbai", name_ta: "மும்பை", lat: 19.0760, lon: 72.8777, tz: "Asia/Kolkata" },
  { name_en: "New Delhi", name_ta: "புது தில்லி", lat: 28.6139, lon: 77.2090, tz: "Asia/Kolkata" },
  { name_en: "Singapore", name_ta: "சிங்கப்பூர்", lat: 1.3521, lon: 103.8198, tz: "Asia/Singapore" },
  { name_en: "London", name_ta: "லண்டன்", lat: 51.5074, lon: -0.1278, tz: "Europe/London" },
  { name_en: "New York", name_ta: "நியூயார்க்", lat: 40.7128, lon: -74.0060, tz: "America/New_York" },
];

const NAKSHATRAS = [
  { index: 1, name_en: "Ashwini", name_ta: "அசுவினி" },
  { index: 2, name_en: "Bharani", name_ta: "பரணி" },
  { index: 3, name_en: "Krittika", name_ta: "கார்த்திகை" },
  { index: 4, name_en: "Rohini", name_ta: "ரோகிணி" },
  { index: 5, name_en: "Mrigashira", name_ta: "மிருகசீரிஷம்" },
  { index: 6, name_en: "Ardra", name_ta: "திருவாதிரை" },
  { index: 7, name_en: "Punarvasu", name_ta: "புனர்பூசம்" },
  { index: 8, name_en: "Pushya", name_ta: "பூசம்" },
  { index: 9, name_en: "Ashlesha", name_ta: "ஆயில்யம்" },
  { index: 10, name_en: "Magha", name_ta: "மகம்" },
  { index: 11, name_en: "Purva Phalguni", name_ta: "பூரம்" },
  { index: 12, name_en: "Uttara Phalguni", name_ta: "உத்திரம்" },
  { index: 13, name_en: "Hasta", name_ta: "அஸ்தம்" },
  { index: 14, name_en: "Chitra", name_ta: "சித்திரை" },
  { index: 15, name_en: "Swati", name_ta: "சுவாதி" },
  { index: 16, name_en: "Vishakha", name_ta: "விசாகம்" },
  { index: 17, name_en: "Anuradha", name_ta: "அனுஷம்" },
  { index: 18, name_en: "Jyeshtha", name_ta: "கேட்டை" },
  { index: 19, name_en: "Moola", name_ta: "மூலம்" },
  { index: 20, name_en: "Purva Ashadha", name_ta: "பூராடம்" },
  { index: 21, name_en: "Uttara Ashadha", name_ta: "உத்திராடம்" },
  { index: 22, name_en: "Shravana", name_ta: "திருவோணம்" },
  { index: 23, name_en: "Dhanishta", name_ta: "அவிட்டம்" },
  { index: 24, name_en: "Shatabhisha", name_ta: "சதயம்" },
  { index: 25, name_en: "Purva Bhadrapada", name_ta: "பூரட்டாதி" },
  { index: 26, name_en: "Uttara Bhadrapada", name_ta: "உத்திரட்டாதி" },
  { index: 27, name_en: "Revati", name_ta: "ரேவதி" },
];

function PanchaPakshiStudioInner() {
  const { language } = useLanguage();
  const searchParams = useSearchParams();

  // Inputs state
  const [dateStr, setDateStr] = useState<string>(() => {
    return new Date().toISOString().split("T")[0];
  });
  const [selectedCity, setSelectedCity] = useState<CityPreset>(CITY_PRESETS[0]);
  const [latitude, setLatitude] = useState<number>(CITY_PRESETS[0].lat);
  const [longitude, setLongitude] = useState<number>(CITY_PRESETS[0].lon);
  const [timezoneStr, setTimezoneStr] = useState<string>(CITY_PRESETS[0].tz);

  const [birthNakshatra, setBirthNakshatra] = useState<number>(4); // Rohini default
  const [birthPaksha, setBirthPaksha] = useState<"shukla" | "krishna">("shukla");

  // View state
  const [activeTab, setActiveTab] = useState<"timeline" | "golden" | "padupakshi" | "lore">("timeline");
  const [timelineFilter, setTimelineFilter] = useState<"all" | "day" | "night">("all");
  const [selectedAntaraModal, setSelectedAntaraModal] = useState<AntaraSlot | null>(null);

  // Data state
  const [data, setData] = useState<PanchaPakshiResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Live ticking clock
  const [nowTime, setNowTime] = useState<Date>(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setNowTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const handleSelectCity = (city: CityPreset) => {
    setSelectedCity(city);
    setLatitude(city.lat);
    setLongitude(city.lon);
    setTimezoneStr(city.tz);
  };

  const shiftDate = (days: number) => {
    const d = new Date(dateStr);
    d.setDate(d.getDate() + days);
    setDateStr(d.toISOString().split("T")[0]);
  };

  const resetToToday = () => {
    setDateStr(new Date().toISOString().split("T")[0]);
  };

  const fetchBioRhythms = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await calculatePanchaPakshi({
        target_date: dateStr,
        latitude,
        longitude,
        timezone: timezoneStr,
        birth_nakshatra: birthNakshatra,
        birth_paksha: birthPaksha,
      });
      setData(res);
    } catch (err: any) {
      setError(err?.message || "Failed to calculate Pancha Pakshi bio-rhythms.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBioRhythms();
  }, [dateStr, latitude, longitude, timezoneStr, birthNakshatra, birthPaksha]);

  // Current active sub-period (Antara)
  const currentActiveAntara = useMemo(() => {
    if (!data?.all_antaras || data.all_antaras.length === 0) return null;
    const nowMs = nowTime.getTime();

    for (let i = 0; i < data.all_antaras.length; i++) {
      const slot = data.all_antaras[i];
      const startMs = new Date(slot.start_time_utc).getTime();
      const endMs = new Date(slot.end_time_utc).getTime();

      if (nowMs >= startMs && nowMs < endMs) {
        const totalMs = endMs - startMs;
        const elapsedMs = Math.max(0, nowMs - startMs);
        const remainingMs = Math.max(0, endMs - nowMs);
        const progressPercent = Math.min(100, Math.round((elapsedMs / totalMs) * 100));

        const remMins = Math.floor(remainingMs / 60000);
        const remSecs = Math.floor((remainingMs % 60000) / 1000);

        const nextSlot = i + 1 < data.all_antaras.length ? data.all_antaras[i + 1] : null;

        return {
          slot,
          progressPercent,
          remainingMinutes: remMins,
          remainingSeconds: remSecs,
          nextSlot,
          isToday: dateStr === new Date().toISOString().split("T")[0],
        };
      }
    }
    return null;
  }, [data, nowTime, dateStr]);

  // Filtered Antaras for Timeline Tab
  const filteredAntaras = useMemo(() => {
    if (!data?.all_antaras) return [];
    if (timelineFilter === "day") {
      return data.all_antaras.filter((a) => a.period_type === "day");
    }
    if (timelineFilter === "night") {
      return data.all_antaras.filter((a) => a.period_type === "night");
    }
    return data.all_antaras;
  }, [data, timelineFilter]);

  return (
    <div className="min-h-screen bg-[#F4F6F9] text-[#102A4C]">
      {/* Top Sticky Header & Breadcrumbs */}
      <div className="bg-white border-b border-[#DDE5F0] sticky top-0 z-20 shadow-2xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4">
          <Breadcrumbs
            items={[
              { label: language === "ta" ? "முகப்பு" : "Home", href: "/" },
              { label: language === "ta" ? "கருவிகள்" : "Tools", href: "/tools" },
              {
                label:
                  language === "ta"
                    ? "பஞ்ச பட்சி சாஸ்திரம் & பயோ-ரிதம் அரங்கம்"
                    : "Pancha Pakshi Bio-Rhythms Studio",
              },
            ]}
          />

          <div className="mt-3 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold uppercase tracking-wider mb-1">
                <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
                <span>{language === "ta" ? "அகத்தியர் சித்த முறை பஞ்ச பட்சி சாஸ்திரம்" : "Sage Agastya's Pancha Pakshi Siddha System"}</span>
              </div>
              <h1 className="font-serif text-2xl sm:text-3xl font-bold text-[#102A4C]">
                {language === "ta"
                  ? "பஞ்ச பட்சி சாஸ்திரம் & பயோ-ரிதம் அரங்கம்"
                  : "Pancha Pakshi Shastra (Five Birds Bio-Rhythms Studio)"}
              </h1>
              <p className="text-xs sm:text-sm text-[#52667E] mt-0.5">
                {language === "ta"
                  ? "வல்லூறு, ஆந்தை, காகம், கோழி, மயில் ஐந்து பட்சிகளின் அரசு, ஊண், நடை, துயில், சாவு அந்தர கால அட்டவணை."
                  : "Daily bio-rhythmic energy transitions across Ruling, Eating, Walking, Sleeping, and Dying phases."}
              </p>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={fetchBioRhythms}
                disabled={loading}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#102A4C] hover:bg-[#16365C] text-white text-xs font-semibold shadow-xs transition-all cursor-pointer"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-amber-300" : ""}`} />
                <span>{loading ? (language === "ta" ? "கணக்கிடுகிறது..." : "Calculating...") : (language === "ta" ? "புதுப்பி" : "Refresh Rhythms")}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-8">
        {/* INPUTS & BIRTH BIRD SELECTOR BAR */}
        <div className="p-6 rounded-3xl bg-white border border-[#DDE5F0] shadow-xs space-y-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
            {/* Birth Nakshatra */}
            <div>
              <label className="block text-[11px] font-bold text-[#52667E] uppercase tracking-wider mb-1">
                {language === "ta" ? "பிறந்த நட்சத்திரம் (Janma Star)" : "Birth Star (Janma Nakshatra)"}
              </label>
              <select
                value={birthNakshatra}
                onChange={(e) => setBirthNakshatra(parseInt(e.target.value) || 1)}
                className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] bg-white font-medium text-[#102A4C]"
              >
                {NAKSHATRAS.map((nak) => (
                  <option key={nak.index} value={nak.index}>
                    #{nak.index} {nak.name_en} ({nak.name_ta})
                  </option>
                ))}
              </select>
            </div>

            {/* Birth Paksha Toggle */}
            <div>
              <label className="block text-[11px] font-bold text-[#52667E] uppercase tracking-wider mb-1">
                {language === "ta" ? "பிறந்த பக்ஷம் (Birth Paksha)" : "Birth Paksha"}
              </label>
              <div className="grid grid-cols-2 gap-1.5 p-1 rounded-xl bg-[#F1F5F9] border border-[#E2E8F0]">
                <button
                  type="button"
                  onClick={() => setBirthPaksha("shukla")}
                  className={`py-1.5 rounded-lg font-bold text-xs transition-all cursor-pointer ${
                    birthPaksha === "shukla"
                      ? "bg-white text-[#102A4C] shadow-2xs"
                      : "text-[#52667E] hover:text-[#102A4C]"
                  }`}
                >
                  {language === "ta" ? "வளர்பிறை (சுக்ல)" : "Waxing (Shukla)"}
                </button>
                <button
                  type="button"
                  onClick={() => setBirthPaksha("krishna")}
                  className={`py-1.5 rounded-lg font-bold text-xs transition-all cursor-pointer ${
                    birthPaksha === "krishna"
                      ? "bg-white text-[#102A4C] shadow-2xs"
                      : "text-[#52667E] hover:text-[#102A4C]"
                  }`}
                >
                  {language === "ta" ? "தேய்பிறை (கிருஷ்ண)" : "Waning (Krishna)"}
                </button>
              </div>
            </div>

            {/* Target Date */}
            <div>
              <label className="block text-[11px] font-bold text-[#52667E] uppercase tracking-wider mb-1">
                {language === "ta" ? "கணிப்பு தேதி / Target Date" : "Target Date"}
              </label>
              <div className="flex items-center gap-1.5">
                <button
                  type="button"
                  onClick={() => shiftDate(-1)}
                  className="p-2 rounded-xl border border-[#DDE5F0] hover:bg-[#F8FAFC] text-[#102A4C]"
                  title="Previous Day"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <input
                  type="date"
                  value={dateStr}
                  onChange={(e) => setDateStr(e.target.value)}
                  className="w-full px-3 py-1.5 rounded-xl border border-[#DDE5F0] bg-white text-xs font-semibold text-[#102A4C]"
                />
                <button
                  type="button"
                  onClick={() => shiftDate(1)}
                  className="p-2 rounded-xl border border-[#DDE5F0] hover:bg-[#F8FAFC] text-[#102A4C]"
                  title="Next Day"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* City Preset */}
            <div>
              <label className="block text-[11px] font-bold text-[#52667E] uppercase tracking-wider mb-1">
                {language === "ta" ? "நகரம் / Location" : "Location"}
              </label>
              <select
                value={selectedCity.name_en}
                onChange={(e) => {
                  const found = CITY_PRESETS.find((c) => c.name_en === e.target.value);
                  if (found) handleSelectCity(found);
                }}
                className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] bg-white font-medium text-[#102A4C]"
              >
                {CITY_PRESETS.map((c) => (
                  <option key={c.name_en} value={c.name_en}>
                    {language === "ta" ? c.name_ta : c.name_en} ({c.name_en})
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Error Notification */}
        {error && (
          <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-3">
            <AlertCircle className="w-5 h-5 shrink-0 text-rose-600" />
            <div>
              <strong className="font-bold">Error: </strong>
              <span>{error}</span>
            </div>
          </div>
        )}

        {/* Loading Spinner */}
        {loading && (
          <div className="p-16 text-center space-y-3">
            <div className="w-10 h-10 border-4 border-[#3478F6] border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-xs font-semibold text-[#52667E]">
              {language === "ta"
                ? "அகத்தியர் முறைப்படி ஜாமங்கள் மற்றும் அந்தரங்கள் கணக்கிடப்படுகின்றன..."
                : "Calculating Agastya Yamams and Antara bio-rhythms..."}
            </p>
          </div>
        )}

        {!loading && data && (
          <div className="space-y-8">
            {/* 1. REAL-TIME ACTIVE BIO-RHYTHM HERO GAUGE */}
            {currentActiveAntara && currentActiveAntara.isToday && (
              <div className="p-6 sm:p-8 rounded-3xl bg-linear-to-r from-[#102A4C] via-[#16365C] to-[#1E4574] text-white shadow-xl relative overflow-hidden">
                <div className="absolute right-0 top-0 bottom-0 opacity-10 pointer-events-none flex items-center pr-8">
                  <span className="text-9xl">{data.birth_bird.symbol}</span>
                </div>

                <div className="relative z-10 space-y-6">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-white/15">
                    <div className="flex items-center gap-4">
                      <div className="w-14 h-14 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 flex items-center justify-center text-3xl shadow-inner">
                        {data.birth_bird.symbol}
                      </div>

                      <div>
                        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/20 border border-emerald-400/40 text-emerald-300 text-[10px] font-bold uppercase tracking-wider mb-1">
                          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                          <span>{language === "ta" ? "தற்போதைய நிகழ்நேர இயக்கம்" : "ACTIVE REAL-TIME STATE"}</span>
                        </div>
                        <h2 className="text-2xl sm:text-3xl font-serif font-bold text-white flex items-center gap-2">
                          <span>{data.birth_bird.name_en}</span>
                          <span className="text-amber-300 text-lg font-tamil">
                            ({data.birth_bird.name_ta})
                          </span>
                        </h2>
                        <div className="text-xs text-white/70">
                          {language === "ta" ? "பூதம்:" : "Element:"} {data.birth_bird.element_ta} ({data.birth_bird.element_en}) • {data.birth_bird.ruling_planet_ta} ({data.birth_bird.ruling_planet})
                        </div>
                      </div>
                    </div>

                    {/* Live Countdown Clock */}
                    <div className="flex items-center gap-4 bg-black/25 px-5 py-3 rounded-2xl border border-white/10 backdrop-blur-md">
                      <Timer className="w-7 h-7 text-amber-300 shrink-0" />
                      <div>
                        <div className="text-[10px] uppercase font-bold text-white/70 tracking-wider">
                          {language === "ta" ? "அந்தர நேரம் முடிவடைய" : "Time Remaining in this Antara"}
                        </div>
                        <div className="text-2xl font-mono font-bold text-amber-300">
                          {currentActiveAntara.remainingMinutes}m {currentActiveAntara.remainingSeconds < 10 ? `0${currentActiveAntara.remainingSeconds}` : currentActiveAntara.remainingSeconds}s
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Active Activity & Power Bar */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs sm:text-sm font-bold">
                      <div className="flex items-center gap-2">
                        <span className="text-white/70">{language === "ta" ? "செயல்பாடு:" : "Activity:"}</span>
                        <span className="text-amber-300 font-serif text-base sm:text-lg">
                          {currentActiveAntara.slot.major_activity_ta}ல் {currentActiveAntara.slot.sub_activity_ta} ({currentActiveAntara.slot.sub_activity_en} in {currentActiveAntara.slot.major_activity_en})
                        </span>
                      </div>
                      <div className="text-amber-300 font-mono text-base font-bold">
                        {currentActiveAntara.slot.power_score}% {language === "ta" ? "ஆற்றல்" : "Power"}
                      </div>
                    </div>

                    <div className="w-full h-3 rounded-full bg-white/10 overflow-hidden">
                      <div
                        className="h-full bg-linear-to-r from-amber-400 to-emerald-400 transition-all duration-1000 rounded-full"
                        style={{ width: `${currentActiveAntara.slot.power_score}%` }}
                      />
                    </div>

                    <div className="flex justify-between text-[11px] text-white/70 font-mono">
                      <span>{currentActiveAntara.slot.start_time_local}</span>
                      <span>{currentActiveAntara.progressPercent}% elapsed</span>
                      <span>{currentActiveAntara.slot.end_time_local}</span>
                    </div>
                  </div>

                  {/* Action Advisory Pills */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs pt-1">
                    <div className="p-4 rounded-2xl bg-white/10 border border-white/15 backdrop-blur-xs space-y-1.5">
                      <div className="flex items-center gap-1.5 text-emerald-300 font-bold uppercase tracking-wider text-[11px]">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                        <span>{language === "ta" ? "இப்போது செய்ய வேண்டியவை / Good To Do" : "Favorable Activities Right Now"}</span>
                      </div>
                      <p className="text-white/90 leading-relaxed">
                        {currentActiveAntara.slot.power_score >= 50
                          ? (language === "ta" ? currentActiveAntara.slot.recommended_ta.join(", ") : currentActiveAntara.slot.recommended_en.join(", "))
                          : (language === "ta" ? "முக்கிய முடிவுகள் எடுக்காமல் அமைதி காக்கவும், தியானம் செய்யலாம்." : "Maintain calm, avoid major signatures or conflicts.")}
                      </p>
                    </div>

                    <div className="p-4 rounded-2xl bg-white/10 border border-white/15 backdrop-blur-xs space-y-1.5">
                      <div className="flex items-center gap-1.5 text-rose-300 font-bold uppercase tracking-wider text-[11px]">
                        <XCircle className="w-4 h-4 text-rose-400" />
                        <span>{language === "ta" ? "இப்போது தவிர்க்க வேண்டியவை / Avoid" : "Activities to Avoid Right Now"}</span>
                      </div>
                      <p className="text-white/90 leading-relaxed">
                        {currentActiveAntara.slot.avoid_ta.length > 0
                          ? (language === "ta" ? currentActiveAntara.slot.avoid_ta.join(", ") : currentActiveAntara.slot.avoid_en.join(", "))
                          : (language === "ta" ? "தவறான பேச்சுவார்த்தைகளைத் தவிர்க்கவும்." : "Avoid unnecessary arguments.")}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Birth Bird Summary Metadata Card */}
            <div className="p-6 rounded-3xl bg-white border border-[#DDE5F0] shadow-xs space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-3 border-b border-[#F1F5F9]">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{data.birth_bird.symbol}</span>
                  <div>
                    <h3 className="font-serif text-lg font-bold text-[#102A4C]">
                      {data.birth_bird.name_en} ({data.birth_bird.name_ta})
                    </h3>
                    <p className="text-xs text-[#52667E]">
                      {language === "ta" ? "உங்களது உயிர் பட்சி (Janma Pakshi)" : "Your Native Birth Bird"} • {data.astronomical.target_paksha_ta} ({data.astronomical.target_paksha.toUpperCase()})
                    </p>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-2 text-xs">
                  <span className="px-3 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 font-bold">
                    {data.total_golden_windows} {language === "ta" ? "தங்கத் தருணங்கள்" : "Golden Windows"}
                  </span>
                  <span className="px-3 py-1 rounded-full bg-rose-50 text-rose-800 border border-rose-200 font-bold">
                    {data.total_padupakshi_windows} {language === "ta" ? "படுபட்சி காலங்கள்" : "Padupakshi Hours"}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3 text-xs">
                <div className="p-3 rounded-xl bg-[#FAF8F5] border border-[#E2E8F0]">
                  <span className="text-[10px] text-[#8C6D23] font-bold uppercase block">பூதம் (Element)</span>
                  <strong className="text-sm text-[#102A4C] block mt-0.5">{data.birth_bird.element_ta}</strong>
                  <span className="text-[10px] text-[#52667E]">{data.birth_bird.element_en}</span>
                </div>

                <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                  <span className="text-[10px] text-[#52667E] font-bold uppercase block">கிரகம் (Graha)</span>
                  <strong className="text-sm text-[#102A4C] block mt-0.5">{data.birth_bird.ruling_planet_ta}</strong>
                  <span className="text-[10px] text-[#52667E]">{data.birth_bird.ruling_planet}</span>
                </div>

                <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                  <span className="text-[10px] text-[#52667E] font-bold uppercase block">திசை (Direction)</span>
                  <strong className="text-sm text-[#102A4C] block mt-0.5">{data.birth_bird.lucky_direction_ta}</strong>
                  <span className="text-[10px] text-[#52667E]">{data.birth_bird.lucky_direction}</span>
                </div>

                <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                  <span className="text-[10px] text-[#52667E] font-bold uppercase block">வண்ணம் (Color)</span>
                  <strong className="text-sm text-[#102A4C] block mt-0.5">{data.birth_bird.lucky_color_ta}</strong>
                  <span className="text-[10px] text-[#52667E]">{data.birth_bird.lucky_color}</span>
                </div>

                <div className="p-3 rounded-xl bg-emerald-50/50 border border-emerald-200">
                  <span className="text-[10px] text-emerald-800 font-bold uppercase block">நட்பு பட்சி (Friend)</span>
                  <strong className="text-sm text-emerald-950 block mt-0.5">{data.birth_bird.friendly_birds_ta.join(", ")}</strong>
                  <span className="text-[10px] text-emerald-700">{data.birth_bird.friendly_birds.join(", ")}</span>
                </div>

                <div className="p-3 rounded-xl bg-rose-50/50 border border-rose-200">
                  <span className="text-[10px] text-rose-800 font-bold uppercase block">பகை பட்சி (Enemy)</span>
                  <strong className="text-sm text-rose-950 block mt-0.5">{data.birth_bird.inimical_birds_ta.join(", ")}</strong>
                  <span className="text-[10px] text-rose-700">{data.birth_bird.inimical_birds.join(", ")}</span>
                </div>
              </div>
            </div>

            {/* Navigation Studio Tabs */}
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-[#DDE5F0] pb-3">
              <div className="flex items-center gap-2">
                {[
                  { id: "timeline", en: "50-Interval Bio-Rhythm Timeline", ta: "முழு நாள் 50 அந்தர கால அட்டவணை", icon: Clock },
                  { id: "golden", en: `Golden Windows (${data.total_golden_windows})`, ta: `தங்க வெற்றித் தருணங்கள் (${data.total_golden_windows})`, icon: Zap },
                  { id: "padupakshi", en: `Padupakshi Hours (${data.total_padupakshi_windows})`, ta: `படுபட்சி எச்சரிக்கை (${data.total_padupakshi_windows})`, icon: ShieldAlert },
                  { id: "lore", en: "Agastya Pancha Pakshi Lore", ta: "அகத்தியர் பட்சி தத்துவங்கள்", icon: Info },
                ].map((tab) => {
                  const Icon = tab.icon;
                  const isActive = activeTab === tab.id;
                  return (
                    <button
                      key={tab.id}
                      type="button"
                      onClick={() => setActiveTab(tab.id as any)}
                      className={`inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all cursor-pointer ${
                        isActive
                          ? "bg-[#102A4C] text-white shadow-xs"
                          : "bg-white text-[#52667E] hover:bg-[#F1F5F9] border border-[#DDE5F0]"
                      }`}
                    >
                      <Icon className={`w-4 h-4 ${isActive ? "text-amber-300" : "text-[#52667E]"}`} />
                      <span>{language === "ta" ? tab.ta : tab.en}</span>
                    </button>
                  );
                })}
              </div>

              {/* Filter for Timeline Tab */}
              {activeTab === "timeline" && (
                <div className="flex items-center gap-1 text-xs">
                  <span className="font-bold text-[#52667E] mr-1">{language === "ta" ? "காட்சி:" : "Filter:"}</span>
                  <button
                    type="button"
                    onClick={() => setTimelineFilter("all")}
                    className={`px-2.5 py-1 rounded-lg font-medium transition-all cursor-pointer ${
                      timelineFilter === "all" ? "bg-[#102A4C] text-white" : "bg-white border text-[#52667E]"
                    }`}
                  >
                    All (50)
                  </button>
                  <button
                    type="button"
                    onClick={() => setTimelineFilter("day")}
                    className={`px-2.5 py-1 rounded-lg font-medium transition-all cursor-pointer ${
                      timelineFilter === "day" ? "bg-amber-600 text-white" : "bg-white border text-amber-700"
                    }`}
                  >
                    Day (25)
                  </button>
                  <button
                    type="button"
                    onClick={() => setTimelineFilter("night")}
                    className={`px-2.5 py-1 rounded-lg font-medium transition-all cursor-pointer ${
                      timelineFilter === "night" ? "bg-indigo-600 text-white" : "bg-white border text-indigo-700"
                    }`}
                  >
                    Night (25)
                  </button>
                </div>
              )}
            </div>

            {/* TAB 1: 50-INTERVAL BIO-RHYTHM TIMELINE */}
            {activeTab === "timeline" && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-3.5">
                  {filteredAntaras.map((antara) => {
                    const isCurrent =
                      currentActiveAntara?.isToday &&
                      currentActiveAntara.slot.global_sub_index === antara.global_sub_index &&
                      currentActiveAntara.slot.period_type === antara.period_type;

                    const isGolden = antara.power_score >= 80;
                    const isDanger = antara.power_score <= 25;

                    return (
                      <div
                        key={`${antara.period_type}-${antara.global_sub_index}`}
                        onClick={() => setSelectedAntaraModal(antara)}
                        className={`p-4 rounded-2xl border transition-all cursor-pointer relative overflow-hidden group hover:shadow-md space-y-2 ${
                          isCurrent
                            ? "bg-amber-50/90 border-amber-400 ring-2 ring-amber-400 shadow-md"
                            : isGolden
                            ? "bg-emerald-50/40 border-emerald-300 hover:border-emerald-400"
                            : isDanger
                            ? "bg-rose-50/40 border-rose-300 hover:border-rose-400"
                            : "bg-white border-[#DDE5F0] hover:border-[#3478F6]/40"
                        }`}
                      >
                        {isCurrent && (
                          <div className="absolute top-0 right-0 bg-amber-500 text-white text-[9px] uppercase font-bold px-2 py-0.5 rounded-bl-lg">
                            ACTIVE
                          </div>
                        )}

                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-mono text-[#52667E]">
                            #{antara.global_sub_index} • {antara.period_type === "day" ? "Day" : "Night"}
                          </span>
                          <span
                            className="text-xs font-bold px-2 py-0.5 rounded-full font-mono"
                            style={{
                              backgroundColor: `${antara.color}15`,
                              color: antara.color,
                            }}
                          >
                            {antara.power_score}%
                          </span>
                        </div>

                        <div>
                          <h4 className="font-serif font-bold text-sm text-[#102A4C] group-hover:text-[#3478F6] transition-colors">
                            {antara.sub_activity_ta} ({antara.sub_activity_en})
                          </h4>
                          <div className="text-[11px] text-[#52667E]">
                            {antara.major_activity_ta}ல் {antara.sub_activity_ta}
                          </div>
                        </div>

                        <div className="pt-2 border-t border-[#F1F5F9] flex items-center justify-between text-[11px] font-mono text-[#102A4C] font-semibold">
                          <span>{antara.start_time_local.slice(0, 5)}</span>
                          <span>—</span>
                          <span>{antara.end_time_local.slice(0, 5)}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* TAB 2: GOLDEN ACTION WINDOWS */}
            {activeTab === "golden" && (
              <div className="p-6 sm:p-8 rounded-3xl bg-white border border-[#DDE5F0] space-y-6">
                <div>
                  <h3 className="font-serif text-xl font-bold text-[#102A4C] flex items-center gap-2">
                    <Zap className="w-5 h-5 text-amber-500" />
                    <span>{language === "ta" ? "தங்க வெற்றித் தருணங்கள் (Golden Victory Windows)" : "Golden Action Windows"}</span>
                  </h3>
                  <p className="text-xs text-[#52667E] mt-0.5">
                    {language === "ta"
                      ? "80% முதல் 100% பிராண சக்தி வாய்ந்த நேரங்கள். முக்கிய ஒப்பந்தங்கள், புதிய துவக்கம் மற்றும் அரச காரியங்களுக்கு உத்தமம்."
                      : "Peak bio-rhythm windows (80% to 100% vitality). Optimal for contracts, major financial moves, and leadership."}
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {data.golden_windows.map((win) => (
                    <div
                      key={`${win.period_type}-${win.global_sub_index}`}
                      className="p-5 rounded-2xl bg-emerald-50/60 border border-emerald-300 space-y-3"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-serif text-base font-bold text-emerald-950">
                          {win.sub_activity_ta} ({win.sub_activity_en})
                        </span>
                        <span className="px-2.5 py-0.5 rounded-full bg-emerald-600 text-white font-mono font-bold text-xs">
                          {win.power_score}%
                        </span>
                      </div>

                      <div className="font-mono text-xs font-bold text-[#102A4C] bg-white/70 p-2 rounded-xl border border-emerald-200">
                        {win.start_time_local} — {win.end_time_local} ({win.duration_minutes} mins)
                      </div>

                      <div className="text-xs text-emerald-900 space-y-1">
                        <div className="font-bold text-[11px] uppercase tracking-wider text-emerald-800">
                          {language === "ta" ? "உத்தம பலன்கள்:" : "Favorable for:"}
                        </div>
                        <ul className="space-y-0.5 pl-2">
                          {(language === "ta" ? win.recommended_ta : win.recommended_en).map((rec, i) => (
                            <li key={i} className="flex items-center gap-1.5">
                              <span className="text-emerald-600 font-bold">✓</span>
                              <span>{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB 3: PADUPAKSHI CAUTION ALERT */}
            {activeTab === "padupakshi" && (
              <div className="p-6 sm:p-8 rounded-3xl bg-white border border-[#DDE5F0] space-y-6">
                <div>
                  <h3 className="font-serif text-xl font-bold text-rose-900 flex items-center gap-2">
                    <ShieldAlert className="w-5 h-5 text-rose-600" />
                    <span>{language === "ta" ? "படுபட்சி எச்சரிக்கை காலங்கள் (Padupakshi Caution Hours)" : "Padupakshi Warning Periods"}</span>
                  </h3>
                  <p className="text-xs text-[#52667E] mt-0.5">
                    {language === "ta"
                      ? "பிராண சக்தி குறைந்த நேரங்கள் (0% முதல் 25%). புதிய காரியங்கள், அறுவை சிகிச்சை, கடன் கொடுத்தல் மற்றும் விவாதங்களைத் தவிர்க்கவும்."
                      : "Critical low-vitality windows (0% to 25% energy). Strictly avoid starting new ventures, high-stakes decisions, or surgery."}
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {data.padupakshi_windows.map((win) => (
                    <div
                      key={`${win.period_type}-${win.global_sub_index}`}
                      className="p-5 rounded-2xl bg-rose-50/60 border border-rose-300 space-y-3"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-serif text-base font-bold text-rose-950">
                          {win.sub_activity_ta} ({win.sub_activity_en})
                        </span>
                        <span className="px-2.5 py-0.5 rounded-full bg-rose-600 text-white font-mono font-bold text-xs">
                          {win.power_score}%
                        </span>
                      </div>

                      <div className="font-mono text-xs font-bold text-[#102A4C] bg-white/70 p-2 rounded-xl border border-rose-200">
                        {win.start_time_local} — {win.end_time_local} ({win.duration_minutes} mins)
                      </div>

                      <div className="text-xs text-rose-900 space-y-1">
                        <div className="font-bold text-[11px] uppercase tracking-wider text-rose-800">
                          {language === "ta" ? "கட்டாயம் தவிர்க்கவும்:" : "Strictly Avoid:"}
                        </div>
                        <p className="text-[11px] text-rose-800 leading-relaxed">
                          {language === "ta"
                            ? "முக்கிய ஆவணக் கையெழுத்து, மருத்துவ சிகிச்சை, பயணம், வாக்குவாதங்கள் தவிர்க்கப்பட வேண்டும்."
                            : "Contract signings, travel, contentious debates, and aggressive confrontations."}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB 4: AGASTYA LORE & PRINCIPLES */}
            {activeTab === "lore" && (
              <div className="p-6 sm:p-8 rounded-3xl bg-white border border-[#DDE5F0] space-y-6">
                <div>
                  <h3 className="font-serif text-xl font-bold text-[#102A4C]">
                    {language === "ta" ? "அகத்தியர் பஞ்ச பட்சி சாஸ்திர தத்துவங்கள்" : "Sage Agastya's Pancha Pakshi Siddha Philosophy"}
                  </h3>
                  <p className="text-xs text-[#52667E] mt-0.5">
                    {language === "ta"
                      ? "ஐந்து பட்சிகள், பஞ்ச பூதங்கள் மற்றும் அன்றாட வாழ்வியல் வழிகாட்டுதல்கள்."
                      : "The biological correspondence between the 5 cosmic birds, 5 elements, and dynamic human energy."}
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs text-[#52667E] leading-relaxed">
                  <div className="p-5 rounded-2xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-3">
                    <h4 className="font-serif font-bold text-sm text-[#102A4C]">
                      {language === "ta" ? "1. பஞ்ச பட்சி சாஸ்திரம் என்றால் என்ன?" : "1. What is Pancha Pakshi Shastra?"}
                    </h4>
                    <p>
                      Conceived by the venerated Tamil Siddha <strong>Sage Agastya</strong>, Pancha Pakshi Shastra assigns every human being one of five sacred birds (Vulture, Owl, Crow, Cock, Peacock) based on the Janma Nakshatra and the Moon&apos;s lunar phase (Shukla / Krishna Paksha).
                    </p>
                    <p>
                      Each bird embodies one of the Five Great Elements (Pancha Bhutas):
                    </p>
                    <ul className="list-disc pl-4 space-y-1">
                      <li><strong>Vulture (வல்லூறு)</strong> — Ether / Space (ஆகாயம்)</li>
                      <li><strong>Owl (ஆந்தை)</strong> — Air (காற்று)</li>
                      <li><strong>Crow (காகம்)</strong> — Fire (நெருப்பு)</li>
                      <li><strong>Cock (கோழி)</strong> — Water (நீர்)</li>
                      <li><strong>Peacock (மயில்)</strong> — Earth (நிலம்)</li>
                    </ul>
                  </div>

                  <div className="p-5 rounded-2xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-3">
                    <h4 className="font-serif font-bold text-sm text-[#102A4C]">
                      {language === "ta" ? "2. ஐந்து தொழில்களின் ஆற்றல் படிநிலை" : "2. Hierarchical Order of the 5 Activities"}
                    </h4>
                    <div className="space-y-2">
                      <div className="p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-between text-emerald-950 font-bold">
                        <span>1. அரசு (Ruling / Arasu)</span>
                        <span>100% Power (Supreme Victory)</span>
                      </div>
                      <div className="p-2.5 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-between text-blue-950 font-bold">
                        <span>2. ஊண் (Eating / Oon)</span>
                        <span>80% Power (Prosperity & Joy)</span>
                      </div>
                      <div className="p-2.5 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-between text-amber-950 font-bold">
                        <span>3. நடை (Walking / Nadai)</span>
                        <span>50% Power (Movement & Commute)</span>
                      </div>
                      <div className="p-2.5 rounded-xl bg-purple-50 border border-purple-200 flex items-center justify-between text-purple-950 font-bold">
                        <span>4. துயில் (Sleeping / Thuyil)</span>
                        <span>20% Power (Rest & Reflection)</span>
                      </div>
                      <div className="p-2.5 rounded-xl bg-rose-50 border border-rose-200 flex items-center justify-between text-rose-950 font-bold">
                        <span>5. சாவு (Dying / Saavu)</span>
                        <span>0% Power (Padupakshi / Prohibited)</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* DETAIL MODAL FOR CLICKED ANTARA SLOT */}
      {selectedAntaraModal && (
        <div
          className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4"
          onClick={() => setSelectedAntaraModal(null)}
        >
          <div
            className="w-full max-w-lg bg-white rounded-3xl p-6 sm:p-8 space-y-5 shadow-2xl border border-[#DDE5F0]"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between pb-4 border-b border-[#F1F5F9]">
              <div>
                <span className="text-[10px] uppercase font-bold text-[#52667E] tracking-wider">
                  Antara #{selectedAntaraModal.global_sub_index} • {selectedAntaraModal.period_type === "day" ? "Daytime" : "Nighttime"}
                </span>
                <h3 className="text-xl font-serif font-bold text-[#102A4C]">
                  {selectedAntaraModal.major_activity_ta}ல் {selectedAntaraModal.sub_activity_ta} ({selectedAntaraModal.sub_activity_en})
                </h3>
              </div>

              <button
                type="button"
                onClick={() => setSelectedAntaraModal(null)}
                className="w-8 h-8 rounded-xl bg-[#F1F5F9] hover:bg-[#E2E8F0] text-[#52667E] flex items-center justify-center font-bold cursor-pointer"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] flex items-center justify-between font-medium">
                <span>{language === "ta" ? "நேர அளவு:" : "Time Window:"}</span>
                <span className="font-mono font-bold text-[#102A4C]">
                  {selectedAntaraModal.start_time_local} — {selectedAntaraModal.end_time_local} ({selectedAntaraModal.duration_minutes} min)
                </span>
              </div>

              <div className="p-3 rounded-xl bg-[#FAF8F5] border border-[#E2E8F0] flex items-center justify-between font-medium">
                <span>{language === "ta" ? "ஆற்றல் நிலை:" : "Vitality Score:"}</span>
                <span className="font-mono font-bold text-base text-amber-700">
                  {selectedAntaraModal.power_score}% ({selectedAntaraModal.rating_label_ta})
                </span>
              </div>

              {selectedAntaraModal.recommended_ta.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-bold text-emerald-800 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    <span>{language === "ta" ? "உத்தம காரியங்கள்" : "Recommended Activities"}</span>
                  </h4>
                  <ul className="space-y-1 pl-2 text-[#52667E]">
                    {(language === "ta" ? selectedAntaraModal.recommended_ta : selectedAntaraModal.recommended_en).map((item, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-emerald-500 font-bold">✓</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {selectedAntaraModal.avoid_ta.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-bold text-rose-800 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                    <XCircle className="w-4 h-4 text-rose-600" />
                    <span>{language === "ta" ? "தவிர்க்க வேண்டியவை" : "Avoid"}</span>
                  </h4>
                  <ul className="space-y-1 pl-2 text-[#52667E]">
                    {(language === "ta" ? selectedAntaraModal.avoid_ta : selectedAntaraModal.avoid_en).map((item, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-rose-500 font-bold">✗</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div className="pt-2">
              <button
                type="button"
                onClick={() => setSelectedAntaraModal(null)}
                className="w-full py-2.5 rounded-xl bg-[#102A4C] hover:bg-[#16365C] text-white font-bold text-xs transition-colors cursor-pointer"
              >
                {language === "ta" ? "மூடு" : "Close"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function PanchaPakshiPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-[#F4F6F9]">
          <div className="w-8 h-8 border-4 border-[#3478F6] border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <PanchaPakshiStudioInner />
    </Suspense>
  );
}
