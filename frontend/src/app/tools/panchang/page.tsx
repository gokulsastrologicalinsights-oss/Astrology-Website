"use client";

import React, { useState, useEffect, useMemo, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  PanchangResponse,
  HoraSlotItem,
  DailyHoraResponse,
} from "@/lib/types";
import { getDailyPanchang } from "@/lib/api";
import {
  Sun,
  Moon,
  Compass,
  Clock,
  Calendar,
  Sparkles,
  MapPin,
  RefreshCw,
  AlertCircle,
  ShieldCheck,
  ShieldAlert,
  ChevronLeft,
  ChevronRight,
  Flame,
  CheckCircle2,
  XCircle,
  Info,
  Layers,
  ArrowRight,
  Timer,
  Check,
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

function PanchangStudioInner() {
  const { language } = useLanguage();
  const searchParams = useSearchParams();

  const [dateStr, setDateStr] = useState<string>(() => {
    return new Date().toISOString().split("T")[0];
  });
  const [selectedCity, setSelectedCity] = useState<CityPreset>(CITY_PRESETS[0]);
  const [latitude, setLatitude] = useState<number>(CITY_PRESETS[0].lat);
  const [longitude, setLongitude] = useState<number>(CITY_PRESETS[0].lon);
  const [timezoneStr, setTimezoneStr] = useState<string>(CITY_PRESETS[0].tz);
  const [showCoordInputs, setShowCoordInputs] = useState<boolean>(false);

  const [activeTab, setActiveTab] = useState<"horas" | "limbs" | "muhurtas" | "guide">("horas");
  const [horaPeriodFilter, setHoraPeriodFilter] = useState<"all" | "day" | "night">("all");
  const [selectedHoraModal, setSelectedHoraModal] = useState<HoraSlotItem | null>(null);

  const [data, setData] = useState<PanchangResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Live timer tick for current time and remaining hora countdown
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

  const fetchPanchang = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getDailyPanchang({
        date: dateStr,
        latitude,
        longitude,
        timezone: timezoneStr,
        ayanamsa_id: 0,
      });
      setData(res);
    } catch (err: any) {
      setError(err?.message || "Failed to calculate daily Panchangam and Horas.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPanchang();
  }, [dateStr, latitude, longitude, timezoneStr]);

  // Determine current active Hora from live time
  const currentHoraInfo = useMemo(() => {
    if (!data?.horas?.all_horas || data.horas.all_horas.length === 0) return null;

    const nowIso = nowTime.toISOString();
    const nowMs = nowTime.getTime();

    // Check if any slot encompasses current time
    for (let i = 0; i < data.horas.all_horas.length; i++) {
      const slot = data.horas.all_horas[i];
      const startMs = new Date(slot.start_time_utc).getTime();
      const endMs = new Date(slot.end_time_utc).getTime();

      if (nowMs >= startMs && nowMs < endMs) {
        const totalMs = endMs - startMs;
        const elapsedMs = Math.max(0, nowMs - startMs);
        const remainingMs = Math.max(0, endMs - nowMs);
        const progressPercent = Math.min(100, Math.round((elapsedMs / totalMs) * 100));

        const remMins = Math.floor(remainingMs / 60000);
        const remSecs = Math.floor((remainingMs % 60000) / 1000);

        const nextSlot =
          i + 1 < data.horas.all_horas.length
            ? data.horas.all_horas[i + 1]
            : null;

        return {
          currentSlot: slot,
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

  // Filtered Horas for Tab 1
  const filteredHoras = useMemo(() => {
    if (!data?.horas) return [];
    if (horaPeriodFilter === "day") return data.horas.day_horas;
    if (horaPeriodFilter === "night") return data.horas.night_horas;
    return data.horas.all_horas;
  }, [data, horaPeriodFilter]);

  return (
    <div className="min-h-screen bg-[#F4F6F9] text-[#102A4C]">
      {/* Top Header & Breadcrumbs */}
      <div className="bg-white border-b border-[#DDE5F0] sticky top-0 z-20 shadow-2xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4">
          <Breadcrumbs
            items={[
              { label: language === "ta" ? "முகப்பு" : "Home", href: "/" },
              { label: language === "ta" ? "கருவிகள்" : "Tools", href: "/tools" },
              {
                label:
                  language === "ta"
                    ? "தினசரி பஞ்சாங்கம் & ஹோரை"
                    : "Daily Panchang & Hora Studio",
              },
            ]}
          />

          <div className="mt-3 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-amber-50 border border-amber-200 text-amber-800 text-xs font-semibold uppercase tracking-wider mb-1">
                <Sun className="w-3.5 h-3.5 text-amber-600 animate-spin-slow" />
                <span>{language === "ta" ? "அக்யூரேட் எபிமெரிஸ் பஞ்சாங்கம்" : "High-Precision Astronomical Engine"}</span>
              </div>
              <h1 className="font-serif text-2xl sm:text-3xl font-bold text-[#102A4C]">
                {language === "ta"
                  ? "தினசரி பஞ்சாங்கம் & 24-கிரக ஹோரை அரங்கம்"
                  : "Daily Panchanga & 24-Planetary Hora Studio"}
              </h1>
              <p className="text-xs sm:text-sm text-[#52667E] mt-0.5">
                {language === "ta"
                  ? "திதி, வாரம், நட்சத்திரம், யோகம், கரணம், இராகு/எமகண்டம் மற்றும் நிகழ்நேர 24 மணி நேர கிரக ஹோரை வழிகாட்டி."
                  : "5 limbs of Panchangam, Muhurta octants, and real-time 24-Hora timing advisor with live countdown."}
              </p>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={fetchPanchang}
                disabled={loading}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white border border-[#DDE5F0] hover:bg-[#F8FAFC] text-xs font-semibold text-[#102A4C] shadow-2xs transition-all cursor-pointer"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-[#3478F6]" : ""}`} />
                <span>{loading ? (language === "ta" ? "கணக்கிடுகிறது..." : "Calculating...") : (language === "ta" ? "புதுப்பி" : "Refresh")}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-8">
        {/* Date & Location Controls Bar */}
        <div className="p-5 sm:p-6 rounded-3xl bg-white border border-[#DDE5F0] shadow-xs space-y-5">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
            {/* Date Navigator */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => shiftDate(-1)}
                className="p-2 rounded-xl border border-[#DDE5F0] hover:bg-[#F8FAFC] text-[#102A4C] cursor-pointer transition-colors"
                title={language === "ta" ? "முந்தைய நாள்" : "Previous Day"}
              >
                <ChevronLeft className="w-4 h-4" />
              </button>

              <input
                type="date"
                value={dateStr}
                onChange={(e) => setDateStr(e.target.value)}
                className="px-3.5 py-2 rounded-xl border border-[#DDE5F0] bg-white text-[#102A4C] font-semibold text-xs sm:text-sm focus:outline-hidden focus:border-[#3478F6] shadow-2xs"
              />

              <button
                type="button"
                onClick={() => shiftDate(1)}
                className="p-2 rounded-xl border border-[#DDE5F0] hover:bg-[#F8FAFC] text-[#102A4C] cursor-pointer transition-colors"
                title={language === "ta" ? "அடுத்த நாள்" : "Next Day"}
              >
                <ChevronRight className="w-4 h-4" />
              </button>

              <button
                type="button"
                onClick={resetToToday}
                className="px-3 py-2 rounded-xl border border-amber-200 bg-amber-50/70 hover:bg-amber-100/70 text-amber-900 font-bold text-xs cursor-pointer transition-colors"
              >
                {language === "ta" ? "இன்று" : "Today"}
              </button>
            </div>

            {/* City Preset Pills */}
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="text-[11px] font-bold text-[#52667E] uppercase tracking-wider mr-1">
                {language === "ta" ? "நகரம்:" : "City:"}
              </span>
              {CITY_PRESETS.slice(0, 7).map((city) => {
                const isSelected = selectedCity.name_en === city.name_en;
                return (
                  <button
                    key={city.name_en}
                    type="button"
                    onClick={() => handleSelectCity(city)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                      isSelected
                        ? "bg-[#102A4C] text-white shadow-2xs"
                        : "bg-[#F1F5F9] text-[#52667E] hover:bg-[#E2E8F0] hover:text-[#102A4C]"
                    }`}
                  >
                    {language === "ta" ? city.name_ta : city.name_en}
                  </button>
                );
              })}

              <button
                type="button"
                onClick={() => setShowCoordInputs(!showCoordInputs)}
                className="px-2.5 py-1 rounded-lg text-xs font-semibold text-[#3478F6] hover:bg-blue-50 transition-colors cursor-pointer"
              >
                {showCoordInputs
                  ? (language === "ta" ? "சுருக்கு" : "Hide Details")
                  : (language === "ta" ? "பிற நாடுகள் / ஒருங்கிணைப்புகள்" : "+ More / Lat-Lon")}
              </button>
            </div>
          </div>

          {/* Coordinate Drawer */}
          {showCoordInputs && (
            <div className="p-4 rounded-2xl bg-[#F8FAFC] border border-[#E2E8F0] grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
              <div>
                <label className="block text-[11px] font-bold text-[#52667E] mb-1">
                  {language === "ta" ? "அனைத்து நகரங்கள்" : "Preset Cities"}
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
                      {c.name_en} ({c.name_ta})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-[#52667E] mb-1">
                  {language === "ta" ? "அட்சரேகை (Latitude)" : "Latitude"}
                </label>
                <input
                  type="number"
                  step="0.0001"
                  value={latitude}
                  onChange={(e) => setLatitude(parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] bg-white font-medium text-[#102A4C]"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-[#52667E] mb-1">
                  {language === "ta" ? "தீர்க்கரேகை (Longitude)" : "Longitude"}
                </label>
                <input
                  type="number"
                  step="0.0001"
                  value={longitude}
                  onChange={(e) => setLongitude(parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] bg-white font-medium text-[#102A4C]"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-[#52667E] mb-1">
                  {language === "ta" ? "நேர மண்டலம் (Timezone)" : "Timezone"}
                </label>
                <input
                  type="text"
                  value={timezoneStr}
                  onChange={(e) => setTimezoneStr(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] bg-white font-medium text-[#102A4C]"
                />
              </div>
            </div>
          )}
        </div>

        {/* Error Notification */}
        {error && (
          <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-3">
            <AlertCircle className="w-5 h-5 shrink-0 text-rose-600" />
            <div>
              <strong className="font-bold">Calculation Error: </strong>
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
                ? "துல்லியமான வானியல் கணிப்புகள் மற்றும் கிரக ஹோரைகள் பெறப்படுகின்றன..."
                : "Computing high-precision astronomical limbs and 24-Hora planetary rulers..."}
            </p>
          </div>
        )}

        {!loading && data && (
          <div className="space-y-8">
            {/* LIVE REAL-TIME HORA BANNER (Active only for today's date) */}
            {currentHoraInfo && currentHoraInfo.isToday && (
              <div className="p-6 sm:p-8 rounded-3xl bg-linear-to-r from-[#102A4C] via-[#16365C] to-[#1E4574] text-white shadow-xl relative overflow-hidden">
                <div className="absolute right-0 top-0 bottom-0 opacity-10 pointer-events-none flex items-center pr-8">
                  <span className="text-9xl font-serif font-black">{currentHoraInfo.currentSlot.symbol}</span>
                </div>

                <div className="relative z-10 space-y-6">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-white/15">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 flex items-center justify-center text-2xl font-serif text-amber-300 shadow-inner">
                        {currentHoraInfo.currentSlot.symbol}
                      </div>
                      <div>
                        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/20 border border-emerald-400/40 text-emerald-300 text-[10px] font-bold uppercase tracking-wider mb-0.5">
                          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                          <span>{language === "ta" ? "தற்போதைய இயங்கும் ஹோரை" : "ACTIVE REAL-TIME HORA"}</span>
                        </div>
                        <h2 className="text-2xl sm:text-3xl font-serif font-bold tracking-tight text-white flex items-center gap-2">
                          <span>{currentHoraInfo.currentSlot.lord} Hora</span>
                          <span className="text-amber-300 text-lg font-tamil">
                            ({currentHoraInfo.currentSlot.lord_ta} ஹோரை)
                          </span>
                        </h2>
                      </div>
                    </div>

                    {/* Countdown Timer */}
                    <div className="flex items-center gap-4 bg-black/25 px-5 py-3 rounded-2xl border border-white/10 backdrop-blur-md">
                      <Timer className="w-6 h-6 text-amber-300 shrink-0" />
                      <div>
                        <div className="text-[10px] uppercase font-bold text-white/70 tracking-wider">
                          {language === "ta" ? "முடிவடைய எஞ்சியுள்ள நேரம்" : "Time Remaining in this Hora"}
                        </div>
                        <div className="text-xl sm:text-2xl font-mono font-bold text-amber-300">
                          {currentHoraInfo.remainingMinutes}m {currentHoraInfo.remainingSeconds < 10 ? `0${currentHoraInfo.remainingSeconds}` : currentHoraInfo.remainingSeconds}s
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-xs text-white/80 font-medium">
                      <span>{currentHoraInfo.currentSlot.start_time_local}</span>
                      <span>
                        {currentHoraInfo.progressPercent}% {language === "ta" ? "முடிந்தது" : "elapsed"} ({currentHoraInfo.currentSlot.duration_minutes} min total)
                      </span>
                      <span>{currentHoraInfo.currentSlot.end_time_local}</span>
                    </div>
                    <div className="w-full h-2.5 rounded-full bg-white/10 overflow-hidden">
                      <div
                        className="h-full bg-linear-to-r from-amber-400 to-amber-200 transition-all duration-1000 rounded-full"
                        style={{ width: `${currentHoraInfo.progressPercent}%` }}
                      />
                    </div>
                  </div>

                  {/* Recommendations & Prohibitions Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs pt-1">
                    <div className="p-4 rounded-2xl bg-white/10 border border-white/15 backdrop-blur-xs space-y-2">
                      <div className="flex items-center gap-1.5 text-emerald-300 font-bold uppercase tracking-wider text-[11px]">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                        <span>{language === "ta" ? "இப்போது செய்ய வேண்டியவை / Good To Do" : "Favorable Activities Right Now"}</span>
                      </div>
                      <ul className="space-y-1 text-white/90">
                        {(language === "ta"
                          ? currentHoraInfo.currentSlot.good_for_ta
                          : currentHoraInfo.currentSlot.good_for_en
                        ).slice(0, 3).map((act, idx) => (
                          <li key={idx} className="flex items-start gap-1.5">
                            <span className="text-emerald-400 font-bold">✓</span>
                            <span>{act}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="p-4 rounded-2xl bg-white/10 border border-white/15 backdrop-blur-xs space-y-2">
                      <div className="flex items-center gap-1.5 text-rose-300 font-bold uppercase tracking-wider text-[11px]">
                        <XCircle className="w-4 h-4 text-rose-400" />
                        <span>{language === "ta" ? "இப்போது தவிர்க்க வேண்டியவை / Avoid" : "Activities to Avoid Right Now"}</span>
                      </div>
                      <ul className="space-y-1 text-white/90">
                        {(language === "ta"
                          ? currentHoraInfo.currentSlot.avoid_ta
                          : currentHoraInfo.currentSlot.avoid_en
                        ).slice(0, 3).map((act, idx) => (
                          <li key={idx} className="flex items-start gap-1.5">
                            <span className="text-rose-400 font-bold">✗</span>
                            <span>{act}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Next Up Preview */}
                  {currentHoraInfo.nextSlot && (
                    <div className="flex items-center justify-between text-xs text-white/80 pt-2 border-t border-white/10">
                      <div className="flex items-center gap-2">
                        <span className="text-white/60 uppercase text-[10px] tracking-wider font-bold">
                          {language === "ta" ? "அடுத்த ஹோரை:" : "Next Upcoming Hora:"}
                        </span>
                        <strong className="text-white font-bold">
                          {currentHoraInfo.nextSlot.lord} ({currentHoraInfo.nextSlot.lord_ta})
                        </strong>
                      </div>
                      <span className="font-mono text-amber-200">
                        {language === "ta" ? "தொடங்கும் நேரம்:" : "Starts at:"} {currentHoraInfo.nextSlot.start_time_local}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Navigation Tabs */}
            <div className="flex flex-wrap items-center gap-2 border-b border-[#DDE5F0] pb-3">
              {[
                { id: "horas", en: "24-Planetary Hora Schedule", ta: "24-கிரக ஹோரை கால அட்டவணை", icon: Clock },
                { id: "limbs", en: "Panchanga 5-Limbs & Signs", ta: "பஞ்ச அங்கங்கள் & ராசிகள்", icon: Sun },
                { id: "muhurtas", en: "Auspicious & Prohibited Windows", ta: "சுப / அசுப கால அளவுகள்", icon: ShieldAlert },
                { id: "guide", en: "Hora Rules & Principles Guide", ta: "ஹோரை தத்துவ வழிகாட்டி", icon: Info },
              ].map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    type="button"
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs sm:text-sm transition-all cursor-pointer ${
                      isActive
                        ? "bg-[#102A4C] text-white shadow-xs"
                        : "bg-white text-[#52667E] hover:bg-[#F1F5F9] hover:text-[#102A4C] border border-[#DDE5F0]"
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${isActive ? "text-amber-400" : "text-[#52667E]"}`} />
                    <span>{language === "ta" ? tab.ta : tab.en}</span>
                  </button>
                );
              })}
            </div>

            {/* TAB 1: 24-PLANETARY HORA SCHEDULE */}
            {activeTab === "horas" && (
              <div className="space-y-6">
                {/* Hora Filters & Metadata Summary */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 sm:p-5 rounded-2xl bg-white border border-[#DDE5F0]">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-[#52667E] uppercase tracking-wider">
                      {language === "ta" ? "காட்சி:" : "Filter:"}
                    </span>
                    <div className="inline-flex rounded-xl bg-[#F1F5F9] p-1 border border-[#E2E8F0] text-xs font-semibold">
                      {[
                        { id: "all", en: "All 24 Horas", ta: "அனைத்தும் (24)" },
                        { id: "day", en: "12 Daytime Horas", ta: "பகல் ஹோரை (12)" },
                        { id: "night", en: "12 Nighttime Horas", ta: "இரவு ஹோரை (12)" },
                      ].map((f) => (
                        <button
                          key={f.id}
                          type="button"
                          onClick={() => setHoraPeriodFilter(f.id as any)}
                          className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer ${
                            horaPeriodFilter === f.id
                              ? "bg-white text-[#102A4C] shadow-2xs font-bold"
                              : "text-[#52667E] hover:text-[#102A4C]"
                          }`}
                        >
                          {language === "ta" ? f.ta : f.en}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center gap-3 text-xs text-[#52667E]">
                    <div>
                      {language === "ta" ? "பகல் ஹோரை அளவு:" : "Day Hora Duration:"}{" "}
                      <strong className="text-[#102A4C]">{data.horas.daytime_hora_duration_minutes} min</strong>
                    </div>
                    <span>•</span>
                    <div>
                      {language === "ta" ? "இரவு ஹோரை அளவு:" : "Night Hora Duration:"}{" "}
                      <strong className="text-[#102A4C]">{data.horas.nighttime_hora_duration_minutes} min</strong>
                    </div>
                  </div>
                </div>

                {/* Horas Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                  {filteredHoras.map((hora) => {
                    const isCurrent =
                      currentHoraInfo?.isToday &&
                      currentHoraInfo.currentSlot.index === hora.index;

                    const isBenefic = hora.nature === "benefic";
                    const isMalefic = hora.nature === "malefic";

                    return (
                      <div
                        key={hora.index}
                        onClick={() => setSelectedHoraModal(hora)}
                        className={`p-5 rounded-2xl border transition-all cursor-pointer relative overflow-hidden group hover:shadow-md ${
                          isCurrent
                            ? "bg-amber-50/90 border-amber-400 ring-2 ring-amber-400 shadow-md"
                            : "bg-white border-[#DDE5F0] hover:border-[#3478F6]/40"
                        }`}
                      >
                        {/* Current Active Ribbon */}
                        {isCurrent && (
                          <div className="absolute top-0 right-0 bg-amber-500 text-white font-bold text-[9px] uppercase px-3 py-0.5 rounded-bl-xl tracking-wider shadow-xs">
                            {language === "ta" ? "தற்போது இயங்குகிறது" : "RUNNING NOW"}
                          </div>
                        )}

                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-2.5">
                            <div
                              className="w-10 h-10 rounded-xl flex items-center justify-center text-xl font-serif font-bold text-white shadow-xs"
                              style={{ backgroundColor: hora.color }}
                            >
                              {hora.symbol}
                            </div>
                            <div>
                              <div className="flex items-center gap-1.5">
                                <span className="text-[10px] font-bold uppercase tracking-wider text-[#52667E]">
                                  #{hora.index} • {hora.period === "day" ? (language === "ta" ? "பகல்" : "Day") : (language === "ta" ? "இரவு" : "Night")}
                                </span>
                              </div>
                              <h3 className="font-serif text-lg font-bold text-[#102A4C] group-hover:text-[#3478F6] transition-colors">
                                {hora.lord}
                              </h3>
                            </div>
                          </div>

                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                              isBenefic
                                ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                                : isMalefic
                                ? "bg-rose-50 text-rose-700 border border-rose-200"
                                : "bg-amber-50 text-amber-700 border border-amber-200"
                            }`}
                          >
                            {language === "ta"
                              ? isBenefic
                                ? "சுப ஹோரை"
                                : isMalefic
                                ? "அசுப ஹோரை"
                                : "கலப்பு ஹோரை"
                              : hora.nature.toUpperCase()}
                          </span>
                        </div>

                        <div className="mt-4 pt-3 border-t border-[#F1F5F9] space-y-2">
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-[#52667E] font-medium">
                              {language === "ta" ? "கால அளவு:" : "Time Window:"}
                            </span>
                            <span className="font-mono font-bold text-[#102A4C]">
                              {hora.start_time_local} — {hora.end_time_local}
                            </span>
                          </div>

                          <div className="text-[11px] text-[#52667E] line-clamp-2">
                            <strong className="text-[#102A4C]">
                              {language === "ta" ? "நன்மை:" : "Good for:"}{" "}
                            </strong>
                            {(language === "ta" ? hora.good_for_ta : hora.good_for_en)[0]}
                          </div>
                        </div>

                        <div className="mt-3 flex items-center justify-between text-[11px] font-bold text-[#3478F6] group-hover:translate-x-0.5 transition-transform">
                          <span>{language === "ta" ? "முழு வழிகாட்டல் பார்க்க" : "View full activities"}</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* TAB 2: PANCHANGA 5-LIMBS & SIGNS */}
            {activeTab === "limbs" && (
              <div className="space-y-6">
                {/* 4 Solar Astronomical Cards */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="p-5 rounded-2xl bg-amber-50/70 border border-amber-200 text-[#102A4C] space-y-1">
                    <div className="flex items-center gap-2 text-amber-700 text-xs font-bold uppercase">
                      <Sun className="w-4 h-4 text-amber-600" />
                      <span>சூரிய உதயம் / Sunrise</span>
                    </div>
                    <div className="text-2xl font-serif font-bold text-[#102A4C]">
                      {data.astronomical.sunrise_local}
                    </div>
                    <div className="text-[11px] text-[#52667E]">Center of Solar Disk + Refraction</div>
                  </div>

                  <div className="p-5 rounded-2xl bg-orange-50/70 border border-orange-200 text-[#102A4C] space-y-1">
                    <div className="flex items-center gap-2 text-orange-700 text-xs font-bold uppercase">
                      <Sun className="w-4 h-4 text-orange-600" />
                      <span>சூரிய அஸ்தமனம் / Sunset</span>
                    </div>
                    <div className="text-2xl font-serif font-bold text-[#102A4C]">
                      {data.astronomical.sunset_local}
                    </div>
                    <div className="text-[11px] text-[#52667E]">
                      Daylight duration: {data.astronomical.day_length_hours} hrs
                    </div>
                  </div>

                  <div className="p-5 rounded-2xl bg-indigo-50/70 border border-indigo-200 text-[#102A4C] space-y-1">
                    <div className="flex items-center gap-2 text-indigo-700 text-xs font-bold uppercase">
                      <Compass className="w-4 h-4 text-indigo-600" />
                      <span>நண்பகல் உச்சி / Solar Noon</span>
                    </div>
                    <div className="text-2xl font-serif font-bold text-[#102A4C]">
                      {data.astronomical.solar_noon_local}
                    </div>
                    <div className="text-[11px] text-[#52667E]">Exact Meridian Crossing</div>
                  </div>

                  <div className="p-5 rounded-2xl bg-[#FAF8F5] border border-[#DDE5F0] text-[#102A4C] space-y-1">
                    <div className="flex items-center gap-2 text-[#8C6D23] text-xs font-bold uppercase">
                      <Calendar className="w-4 h-4 text-[#B8862B]" />
                      <span>வாரம் / Weekday Lord</span>
                    </div>
                    <div className="text-2xl font-serif font-bold text-[#102A4C]">
                      {data.vara.name_en}
                    </div>
                    <div className="text-[11px] text-[#52667E]">
                      {data.vara.name_ta} • Lord: {data.horas.day_lord.name_en} ({data.horas.day_lord.name_ta})
                    </div>
                  </div>
                </div>

                {/* Five Limbs Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                  {/* 1. Tithi */}
                  <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-3">
                    <div className="flex items-center justify-between pb-3 border-b border-[#F1F5F9]">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center font-bold">
                          1
                        </div>
                        <div>
                          <span className="text-[10px] font-bold uppercase tracking-wider text-amber-700">Limb 1</span>
                          <h3 className="font-serif text-base font-bold text-[#102A4C]">திதி / Tithi</h3>
                        </div>
                      </div>
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-50 text-amber-800 border border-amber-200">
                        {data.tithi.paksha} Paksha
                      </span>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-[#102A4C]">
                        {data.tithi.name}{" "}
                        {data.tithi.name_ta && (
                          <span className="text-xs font-tamil text-[#52667E]">({data.tithi.name_ta})</span>
                        )}
                      </div>
                      <div className="mt-2 text-xs text-[#52667E] space-y-1">
                        <div>Starts: <strong className="text-[#102A4C]">{data.tithi.start_time_local}</strong></div>
                        <div>Ends: <strong className="text-[#102A4C]">{data.tithi.end_time_local}</strong></div>
                      </div>
                    </div>
                  </div>

                  {/* 2. Nakshatra */}
                  <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-3">
                    <div className="flex items-center justify-between pb-3 border-b border-[#F1F5F9]">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-blue-50 text-[#3478F6] flex items-center justify-center font-bold">
                          2
                        </div>
                        <div>
                          <span className="text-[10px] font-bold uppercase tracking-wider text-[#3478F6]">Limb 2</span>
                          <h3 className="font-serif text-base font-bold text-[#102A4C]">நட்சத்திரம் / Nakshatra</h3>
                        </div>
                      </div>
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-50 text-[#3478F6] border border-blue-200">
                        Pada {data.nakshatra.pada}
                      </span>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-[#102A4C]">
                        {data.nakshatra.name}{" "}
                        {data.nakshatra.name_ta && (
                          <span className="text-xs font-tamil text-[#52667E]">({data.nakshatra.name_ta})</span>
                        )}
                      </div>
                      <div className="mt-2 text-xs text-[#52667E] space-y-1">
                        <div>Lord: <strong className="text-[#102A4C]">{data.nakshatra.lord}</strong></div>
                        <div>Ends: <strong className="text-[#102A4C]">{data.nakshatra.end_time_local}</strong></div>
                      </div>
                    </div>
                  </div>

                  {/* 3. Yoga */}
                  <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-3">
                    <div className="flex items-center justify-between pb-3 border-b border-[#F1F5F9]">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold">
                          3
                        </div>
                        <div>
                          <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-700">Limb 3</span>
                          <h3 className="font-serif text-base font-bold text-[#102A4C]">யோகம் / Yoga</h3>
                        </div>
                      </div>
                      <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-indigo-50 text-indigo-800 border border-indigo-200">
                        #{data.yoga.number} of 27
                      </span>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-[#102A4C]">
                        {data.yoga.name}{" "}
                        {data.yoga.name_ta && (
                          <span className="text-xs font-tamil text-[#52667E]">({data.yoga.name_ta})</span>
                        )}
                      </div>
                      <div className="mt-2 text-xs text-[#52667E]">
                        Combined Sun + Moon Longitude in 13° 20&apos; increments
                      </div>
                    </div>
                  </div>

                  {/* 4. Karana */}
                  <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-3">
                    <div className="flex items-center justify-between pb-3 border-b border-[#F1F5F9]">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
                          4
                        </div>
                        <div>
                          <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-700">Limb 4</span>
                          <h3 className="font-serif text-base font-bold text-[#102A4C]">கரணம் / Karana</h3>
                        </div>
                      </div>
                      <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                        Half-Tithi
                      </span>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-[#102A4C]">
                        {data.karana.name}{" "}
                        {data.karana.name_ta && (
                          <span className="text-xs font-tamil text-[#52667E]">({data.karana.name_ta})</span>
                        )}
                      </div>
                      <div className="mt-2 text-xs text-[#52667E]">
                        6° Moon-Sun longitudinal separation window
                      </div>
                    </div>
                  </div>

                  {/* 5. Surya Rashi (Sun Sign) */}
                  <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-3">
                    <div className="flex items-center justify-between pb-3 border-b border-[#F1F5F9]">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-orange-50 text-orange-600 flex items-center justify-center font-bold">
                          ☉
                        </div>
                        <div>
                          <span className="text-[10px] font-bold uppercase tracking-wider text-orange-700">Solar Rashi</span>
                          <h3 className="font-serif text-base font-bold text-[#102A4C]">சூரிய ராசி / Sun Sign</h3>
                        </div>
                      </div>
                      <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-orange-50 text-orange-800 border border-orange-200">
                        {data.sun_sign.degree_in_sign}°
                      </span>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-[#102A4C]">
                        {data.sun_sign.name_en}{" "}
                        <span className="text-xs font-tamil text-[#52667E]">({data.sun_sign.name_ta})</span>
                      </div>
                      <div className="mt-2 text-xs text-[#52667E]">
                        Zodiac Sign occupied by Sun at local sunrise
                      </div>
                    </div>
                  </div>

                  {/* 6. Chandra Rashi (Moon Sign) */}
                  <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-3">
                    <div className="flex items-center justify-between pb-3 border-b border-[#F1F5F9]">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-sky-50 text-sky-600 flex items-center justify-center font-bold">
                          ☽
                        </div>
                        <div>
                          <span className="text-[10px] font-bold uppercase tracking-wider text-sky-700">Lunar Rashi</span>
                          <h3 className="font-serif text-base font-bold text-[#102A4C]">சந்திர ராசி / Moon Sign</h3>
                        </div>
                      </div>
                      <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-sky-50 text-sky-800 border border-sky-200">
                        {data.moon_sign.degree_in_sign}°
                      </span>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-[#102A4C]">
                        {data.moon_sign.name_en}{" "}
                        <span className="text-xs font-tamil text-[#52667E]">({data.moon_sign.name_ta})</span>
                      </div>
                      <div className="mt-2 text-xs text-[#52667E]">
                        Governs daily Chandra-Bala and personal transit favorability
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 3: AUSPICIOUS & INAUSPICIOUS WINDOWS */}
            {activeTab === "muhurtas" && (
              <div className="space-y-6">
                <div className="p-6 sm:p-8 rounded-3xl bg-white border border-[#DDE5F0] shadow-xs space-y-6">
                  <div>
                    <h3 className="font-serif text-xl font-bold text-[#102A4C]">
                      {language === "ta" ? "சுப மற்றும் அசுப கால அளவுகள்" : "Daytime Auspicious & Prohibited Windows"}
                    </h3>
                    <p className="text-xs text-[#52667E] mt-0.5">
                      {language === "ta"
                        ? "அனைத்து கால அளவுகளும் சூரிய உதய-அஸ்தமன விகிதாசாரத்தின் அடிப்படையில் துல்லியமாக கணக்கிடப்பட்டுள்ளன."
                        : "All timings are strictly computed in proportion to local daylight lengths."}
                    </p>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                    {/* Rahu Kalam */}
                    <div className="p-5 rounded-2xl bg-rose-50/70 border border-rose-200 space-y-2">
                      <div className="flex items-center justify-between text-rose-800 font-bold text-xs">
                        <span>இராகு காலம் / Rahu Kalam</span>
                        <span className="px-2 py-0.5 rounded-full bg-rose-100 text-[10px] uppercase font-bold text-rose-700">
                          Strictly Avoid
                        </span>
                      </div>
                      <div className="text-xl font-bold text-rose-950 font-serif">
                        {new Date(data.inauspicious_periods.rahu_kalam.start_utc).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}{" "}
                        —{" "}
                        {new Date(data.inauspicious_periods.rahu_kalam.end_utc).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </div>
                      <div className="text-xs text-rose-700">
                        Octant #{data.inauspicious_periods.rahu_kalam.part} ({data.inauspicious_periods.rahu_kalam.duration_minutes} min). Do not initiate auspicious journeys, signings, or ceremonies.
                      </div>
                    </div>

                    {/* Yamagandam */}
                    <div className="p-5 rounded-2xl bg-orange-50/70 border border-orange-200 space-y-2">
                      <div className="flex items-center justify-between text-orange-800 font-bold text-xs">
                        <span>எமகண்டம் / Yamagandam</span>
                        <span className="px-2 py-0.5 rounded-full bg-orange-100 text-[10px] uppercase font-bold text-orange-700">
                          Avoid
                        </span>
                      </div>
                      <div className="text-xl font-bold text-orange-950 font-serif">
                        {new Date(data.inauspicious_periods.yamagandam.start_utc).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}{" "}
                        —{" "}
                        {new Date(data.inauspicious_periods.yamagandam.end_utc).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </div>
                      <div className="text-xs text-orange-700">
                        Octant #{data.inauspicious_periods.yamagandam.part} ({data.inauspicious_periods.yamagandam.duration_minutes} min). Ruled by Yama; prohibited for new business and travel.
                      </div>
                    </div>

                    {/* Gulika Kalam */}
                    <div className="p-5 rounded-2xl bg-indigo-50/70 border border-indigo-200 space-y-2">
                      <div className="flex items-center justify-between text-indigo-800 font-bold text-xs">
                        <span>குளிகை காலம் / Gulika Kalam</span>
                        <span className="px-2 py-0.5 rounded-full bg-indigo-100 text-[10px] uppercase font-bold text-indigo-700">
                          Action Repeats
                        </span>
                      </div>
                      <div className="text-xl font-bold text-indigo-950 font-serif">
                        {new Date(data.inauspicious_periods.gulikai.start_utc).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}{" "}
                        —{" "}
                        {new Date(data.inauspicious_periods.gulikai.end_utc).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </div>
                      <div className="text-xs text-indigo-700">
                        Octant #{data.inauspicious_periods.gulikai.part} ({data.inauspicious_periods.gulikai.duration_minutes} min). Good deeds repeat; bad deeds also repeat. Avoid funerals and borrowings.
                      </div>
                    </div>

                    {/* Varjyam (Tyajyam) */}
                    <div className="p-5 rounded-2xl bg-red-50/70 border border-red-200 space-y-2">
                      <div className="flex items-center justify-between text-red-800 font-bold text-xs">
                        <span>வர்ஜியம் / Tyajyam</span>
                        <span className="px-2 py-0.5 rounded-full bg-red-100 text-[10px] uppercase font-bold text-red-700">
                          4 Ghatikas Toxic
                        </span>
                      </div>
                      <div className="text-xl font-bold text-red-950 font-serif">
                        {new Date(data.varjyam.start_utc).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}{" "}
                        —{" "}
                        {new Date(data.varjyam.end_utc).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </div>
                      <div className="text-xs text-red-700">
                        Starts from {data.varjyam.start_ghatika}th Ghatika of {data.nakshatra.name}. Strictly avoided for Muhurtas.
                      </div>
                    </div>

                    {/* Abhijit Muhurta */}
                    <div className="p-5 rounded-2xl bg-emerald-50/70 border border-emerald-200 space-y-2">
                      <div className="flex items-center justify-between text-emerald-800 font-bold text-xs">
                        <span>அபிஜித் முகூர்த்தம் / Abhijit</span>
                        <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-[10px] uppercase font-bold text-emerald-700">
                          Highly Auspicious
                        </span>
                      </div>
                      <div className="text-xl font-bold text-emerald-950 font-serif">
                        {new Date(data.auspicious_periods.abhijit.start_utc).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}{" "}
                        —{" "}
                        {new Date(data.auspicious_periods.abhijit.end_utc).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </div>
                      <div className="text-xs text-emerald-700">
                        {data.auspicious_periods.abhijit.is_dur_muhurta_clash
                          ? "Warning: Clashes with Wednesday Dur Muhurta."
                          : "8th Muhurta of daylight. Potent mid-day interval that destroys negative astrological doshas."}
                      </div>
                    </div>

                    {/* Amrita Kalam */}
                    <div className="p-5 rounded-2xl bg-teal-50/70 border border-teal-200 space-y-2">
                      <div className="flex items-center justify-between text-teal-800 font-bold text-xs">
                        <span>அமிர்த காலம் / Amrita Kalam</span>
                        <span className="px-2 py-0.5 rounded-full bg-teal-100 text-[10px] uppercase font-bold text-teal-700">
                          Nectar Window
                        </span>
                      </div>
                      <div className="text-xl font-bold text-teal-950 font-serif">
                        {new Date(data.auspicious_periods.amrita_kalam.start_utc).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}{" "}
                        —{" "}
                        {new Date(data.auspicious_periods.amrita_kalam.end_utc).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </div>
                      <div className="text-xs text-teal-700">
                        Auspicious 4-ghatika period based on Nakshatra amrita-start ghatika. Excellent for starting treatments and ventures.
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 4: HORA RULES & PRINCIPLES GUIDE */}
            {activeTab === "guide" && (
              <div className="p-6 sm:p-8 rounded-3xl bg-white border border-[#DDE5F0] shadow-xs space-y-6">
                <div>
                  <h3 className="font-serif text-xl font-bold text-[#102A4C]">
                    {language === "ta" ? "வேத கிரக ஹோரை தத்துவ வழிகாட்டி" : "Classical Vedic Hora Principles & Rulership Guide"}
                  </h3>
                  <p className="text-xs text-[#52667E] mt-0.5">
                    {language === "ta"
                      ? "ஹோரை கால அளவுகள், கிரகங்களின் இயல்பு மற்றும் செயல்பாட்டு வழிகாட்டல்."
                      : "Understand how Horas are calculated from Sunrise and their classical applications."}
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs text-[#52667E] leading-relaxed">
                  <div className="space-y-3 p-5 rounded-2xl bg-[#F8FAFC] border border-[#E2E8F0]">
                    <h4 className="font-serif font-bold text-sm text-[#102A4C]">
                      {language === "ta" ? "1. ஹோரை என்றால் என்ன?" : "1. What is a Hora?"}
                    </h4>
                    <p>
                      The word <strong>Hora</strong> is derived from the Sanskrit word <em>Ahoratra</em> (A-ho-ra-tra), where &apos;Aho&apos; signifies day and &apos;Ratra&apos; signifies night. By dropping the first and last syllables, &apos;Hora&apos; was born, meaning an astrological hour.
                    </p>
                    <p>
                      A solar day (from sunrise to next sunrise) is divided into <strong>24 Horas</strong>:
                    </p>
                    <ul className="list-disc pl-4 space-y-1">
                      <li><strong>12 Daytime Horas (பகல் ஹோரை)</strong>: Total daylight (Sunset − Sunrise) divided by 12.</li>
                      <li><strong>12 Nighttime Horas (இரவு ஹோரை)</strong>: Total night duration (Next Sunrise − Sunset) divided by 12.</li>
                    </ul>
                  </div>

                  <div className="space-y-3 p-5 rounded-2xl bg-[#F8FAFC] border border-[#E2E8F0]">
                    <h4 className="font-serif font-bold text-sm text-[#102A4C]">
                      {language === "ta" ? "2. சால்டியன் வரிசை (Chaldean Order)" : "2. The Chaldean Speed Order"}
                    </h4>
                    <p>
                      The 1st Hora of daytime is always ruled by the <strong>Lord of the Weekday</strong> (Sunday = Sun, Monday = Moon, Tuesday = Mars, etc.). Subsequent Horas follow the descending astronomical orbital speed order:
                    </p>
                    <div className="p-3 rounded-xl bg-white border border-[#DDE5F0] font-mono font-bold text-[#102A4C] text-center">
                      Sun → Venus → Mercury → Moon → Saturn → Jupiter → Mars
                    </div>
                    <p>
                      Because 24 mod 7 = 3, after 24 Horas, the 25th Hora naturally lands on the Lord of the next day, maintaining an unbroken cosmic cycle!
                    </p>
                  </div>
                </div>

                {/* 7 Planets Table */}
                <div className="overflow-x-auto rounded-2xl border border-[#DDE5F0]">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-[#FAF8F5] text-[#102A4C] border-b border-[#DDE5F0]">
                      <tr>
                        <th className="p-3.5 font-bold">{language === "ta" ? "கிரகம்" : "Planet"}</th>
                        <th className="p-3.5 font-bold">{language === "ta" ? "இயல்பு" : "Nature"}</th>
                        <th className="p-3.5 font-bold">{language === "ta" ? "நன்மை பயக்கும் பணிகள்" : "Recommended Activities"}</th>
                        <th className="p-3.5 font-bold">{language === "ta" ? "தவிர்க்க வேண்டியவை" : "Avoid"}</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#F1F5F9]">
                      {["Jupiter", "Venus", "Mercury", "Moon", "Sun", "Mars", "Saturn"].map((pName) => {
                        const hMeta = data.horas.all_horas.find((h) => h.lord === pName);
                        if (!hMeta) return null;

                        return (
                          <tr key={pName} className="hover:bg-[#F8FAFC]">
                            <td className="p-3.5 font-bold text-[#102A4C] whitespace-nowrap">
                              <span className="mr-2 text-base">{hMeta.symbol}</span>
                              {hMeta.lord} ({hMeta.lord_ta})
                            </td>
                            <td className="p-3.5">
                              <span
                                className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                                  hMeta.nature === "benefic"
                                    ? "bg-emerald-50 text-emerald-700"
                                    : hMeta.nature === "malefic"
                                    ? "bg-rose-50 text-rose-700"
                                    : "bg-amber-50 text-amber-700"
                                }`}
                              >
                                {hMeta.benefic_type}
                              </span>
                            </td>
                            <td className="p-3.5 text-[#52667E]">
                              {(language === "ta" ? hMeta.good_for_ta : hMeta.good_for_en).slice(0, 2).join("; ")}
                            </td>
                            <td className="p-3.5 text-rose-700">
                              {(language === "ta" ? hMeta.avoid_ta : hMeta.avoid_en).slice(0, 2).join("; ")}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* DETAIL MODAL FOR CLICKED HORA CARD */}
      {selectedHoraModal && (
        <div
          className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4"
          onClick={() => setSelectedHoraModal(null)}
        >
          <div
            className="w-full max-w-lg bg-white rounded-3xl p-6 sm:p-8 space-y-6 shadow-2xl border border-[#DDE5F0]"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between pb-4 border-b border-[#F1F5F9]">
              <div className="flex items-center gap-3">
                <div
                  className="w-12 h-12 rounded-2xl flex items-center justify-center text-2xl font-serif font-bold text-white shadow-xs"
                  style={{ backgroundColor: selectedHoraModal.color }}
                >
                  {selectedHoraModal.symbol}
                </div>
                <div>
                  <div className="text-[10px] uppercase font-bold text-[#52667E] tracking-wider">
                    Hora #{selectedHoraModal.index} • {selectedHoraModal.period === "day" ? "Daytime" : "Nighttime"}
                  </div>
                  <h3 className="text-xl font-serif font-bold text-[#102A4C]">
                    {selectedHoraModal.lord} Hora ({selectedHoraModal.lord_ta})
                  </h3>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setSelectedHoraModal(null)}
                className="w-8 h-8 rounded-xl bg-[#F1F5F9] hover:bg-[#E2E8F0] text-[#52667E] flex items-center justify-center font-bold cursor-pointer"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] flex items-center justify-between font-medium">
                <span>{language === "ta" ? "நேர அளவு:" : "Time Slot:"}</span>
                <span className="font-mono font-bold text-[#102A4C]">
                  {selectedHoraModal.start_time_local} — {selectedHoraModal.end_time_local} ({selectedHoraModal.duration_minutes} min)
                </span>
              </div>

              <div className="space-y-2">
                <h4 className="font-bold text-emerald-800 flex items-center gap-1.5 uppercase tracking-wider text-[11px]">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>{language === "ta" ? "நன்மை பயக்கும் பணிகள்" : "Favorable & Recommended Actions"}</span>
                </h4>
                <ul className="space-y-1.5 pl-2 text-[#52667E]">
                  {(language === "ta" ? selectedHoraModal.good_for_ta : selectedHoraModal.good_for_en).map((item, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-emerald-500 font-bold">✓</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="space-y-2">
                <h4 className="font-bold text-rose-800 flex items-center gap-1.5 uppercase tracking-wider text-[11px]">
                  <XCircle className="w-4 h-4 text-rose-600" />
                  <span>{language === "ta" ? "தவிர்க்க வேண்டியவை" : "Actions to Strictly Avoid"}</span>
                </h4>
                <ul className="space-y-1.5 pl-2 text-[#52667E]">
                  {(language === "ta" ? selectedHoraModal.avoid_ta : selectedHoraModal.avoid_en).map((item, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-rose-500 font-bold">✗</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="pt-2">
              <button
                type="button"
                onClick={() => setSelectedHoraModal(null)}
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

export default function PanchangStudioPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-[#F4F6F9]">
          <div className="w-8 h-8 border-4 border-[#3478F6] border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <PanchangStudioInner />
    </Suspense>
  );
}
