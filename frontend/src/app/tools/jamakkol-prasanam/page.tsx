"use client";

import React, { useState, useEffect, useMemo, Suspense } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  JamakkolPrasanamResponse,
  JamakkolPrasanamRequest,
  HousePlacementItem,
} from "@/lib/types";
import { calculateJamakkolPrasanam } from "@/lib/api";
import {
  Compass,
  Clock,
  Calendar,
  Sparkles,
  MapPin,
  RefreshCw,
  AlertCircle,
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Info,
  Timer,
  Zap,
  Sun,
  Moon,
  ChevronRight,
  HelpCircle,
  Flame,
  Award,
  Navigation,
  Layers,
  ArrowRight,
  Eye,
  TrendingUp,
  TrendingDown,
  XCircle,
  BookOpen,
  Users,
  Landmark,
  Plane,
  Scale,
  Banknote,
  Sprout,
  Coins,
  Droplets,
  Briefcase,
  Heart,
  CloudLightning,
  Skull,
  Table,
  Shield,
  Activity,
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
  { name_en: "Salem", name_ta: "சேலம்", lat: 11.6643, lon: 78.1460, tz: "Asia/Kolkata" },
  { name_en: "Tirunelveli", name_ta: "திருநெல்வேலி", lat: 8.7139, lon: 77.7567, tz: "Asia/Kolkata" },
  { name_en: "Bengaluru", name_ta: "பெங்களூரு", lat: 12.9716, lon: 77.5946, tz: "Asia/Kolkata" },
  { name_en: "Hyderabad", name_ta: "ஹைதராபாத்", lat: 17.3850, lon: 78.4867, tz: "Asia/Kolkata" },
  { name_en: "Mumbai", name_ta: "மும்பை", lat: 19.0760, lon: 72.8777, tz: "Asia/Kolkata" },
  { name_en: "New Delhi", name_ta: "புது தில்லி", lat: 28.6139, lon: 77.2090, tz: "Asia/Kolkata" },
  { name_en: "Singapore", name_ta: "சிங்கப்பூர்", lat: 1.3521, lon: 103.8198, tz: "Asia/Singapore" },
  { name_en: "Kuala Lumpur", name_ta: "கோலாலம்பூர்", lat: 3.1390, lon: 101.6869, tz: "Asia/Kuala_Lumpur" },
  { name_en: "London", name_ta: "லண்டன்", lat: 51.5074, lon: -0.1278, tz: "Europe/London" },
  { name_en: "New York", name_ta: "நியூயார்க்", lat: 40.7128, lon: -74.0060, tz: "America/New_York" },
];

const QUERY_CATEGORIES = [
  { id: "general", name_en: "General Query (பொதுவான வினா)", name_ta: "பொதுவான வினா" },
  { id: "business_finance", name_en: "Business & Finance (தொழில், முதலீடு & வர்த்தகம்)", name_ta: "தொழில் & வர்த்தகம்" },
  { id: "career_job", name_en: "Career & Employment (வேலை வாய்ப்பு, பதவி உயர்வு)", name_ta: "உத்தியோகம் & வேலை" },
  { id: "health_illness", name_en: "Health & Recovery (உடல் நலம், நோய் குணமாகுமா?)", name_ta: "உடல் நலம் & சிகிச்சை" },
  { id: "lost_property", name_en: "Lost Articles & Recovery (பொருள் மீட்பு, திருட்டு)", name_ta: "காணாமல் போன பொருள்" },
  { id: "litigation_dispute", name_en: "Litigation & Property Disputes (வழக்கு, பூமி விவாதம்)", name_ta: "வழக்கு & பூமி விவாதம்" },
  { id: "relationship_marriage", name_en: "Marriage & Relationships (திருமணம், நல்லுறவு)", name_ta: "திருமணம் & உறவுகள்" },
  { id: "travel_journey", name_en: "Travel & Relocation (பயணம், இடமாற்றம்)", name_ta: "பயணம் & இடமாற்றம்" },
];

function JamakkolPrasanamInner() {
  const { language } = useLanguage();

  const getCurrentMoment = () => {
    const now = new Date();
    const pad = (n: number) => n.toString().padStart(2, "0");
    const dateStr = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
    const timeStr = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
    return { dateStr, timeStr };
  };

  const [dateInput, setDateInput] = useState<string>(() => getCurrentMoment().dateStr);
  const [timeInput, setTimeInput] = useState<string>(() => getCurrentMoment().timeStr);
  const [selectedCity, setSelectedCity] = useState<CityPreset>(CITY_PRESETS[0]);
  const [queryText, setQueryText] = useState<string>("");
  const [queryCategory, setQueryCategory] = useState<string>("general");
  const [querentSeed, setQuerentSeed] = useState<string>("");

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<JamakkolPrasanamResponse | null>(null);
  const [activeTab, setActiveTab] = useState<"verdict" | "rules" | "domains" | "pillars" | "direction" | "houses">("verdict");
  const [domainFilter, setDomainFilter] = useState<string>("all");

  const handleNowClick = () => {
    const { dateStr, timeStr } = getCurrentMoment();
    setDateInput(dateStr);
    setTimeInput(timeStr);
  };

  const handleCalculate = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const fullIsoString = `${dateInput}T${timeInput}`;
      const payload: JamakkolPrasanamRequest = {
        query_datetime: fullIsoString,
        latitude: selectedCity.lat,
        longitude: selectedCity.lon,
        timezone: selectedCity.tz,
        ayanamsa_id: 0,
        query_text: queryText.trim() ? queryText.trim() : undefined,
        query_category: queryCategory,
        querent_seed: querentSeed && !isNaN(parseInt(querentSeed)) ? parseInt(querentSeed) : undefined,
      };

      const res = await calculateJamakkolPrasanam(payload);
      setResult(res);
    } catch (err: any) {
      console.error("Jamakkol calculation failed:", err);
      setError(
        err?.message ||
          (language === "ta"
            ? "ஜாமக்கோள் பிரசன்னம் கணக்கிடுவதில் பிழை ஏற்பட்டது. தயவுசெய்து மீண்டும் முயற்சிக்கவும்."
            : "Failed to calculate Jamakkol Prasanam. Please check parameters and try again.")
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    handleCalculate();
  }, []);

  const houseMap = useMemo(() => {
    if (!result?.house_placements) return new Map<number, HousePlacementItem>();
    const map = new Map<number, HousePlacementItem>();
    result.house_placements.forEach((h) => map.set(h.sign_index, h));
    return map;
  }, [result]);

  return (
    <div className="min-h-screen bg-[#F8FAFC] pb-16 text-slate-800">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-[#153F6B] via-[#1E4D82] to-[#0D2845] text-white py-8 px-4 sm:px-6 lg:px-8 2xl:px-10 shadow-md border-b border-amber-500/20">
        <div className="w-full max-w-7xl 2xl:max-w-screen-2xl mx-auto">
          <Breadcrumbs
            items={[
              { label: language === "ta" ? "முகப்பு" : "Home", href: "/" },
              { label: language === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools", href: "/tools" },
              {
                label: language === "ta" ? "ஜாமக்கோள் பிரசன்னம்" : "Jamakkol Prasanam",
                href: "/tools/jamakkol-prasanam",
              },
            ]}
          />

          <div className="mt-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-400/20 border border-amber-300/30 text-amber-300 text-xs font-semibold mb-2">
                <Compass className="w-3.5 h-3.5 animate-spin-slow" />
                <span>{language === "ta" ? "பாரம்பரிய தமிழ் பிரசன்ன சாஸ்திரம் & வைர விதிகள்" : "Classical Tamil Horary Shastra & Diamond Rules"}</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white flex items-center gap-2">
                <span>{language === "ta" ? "ஜாமக்கோள் பிரசன்னம்" : "Jamakkol Prasanam Studio"}</span>
                <span className="text-amber-400 text-sm font-medium border border-amber-400/40 rounded px-2 py-0.5">
                  16 Jamams Dual-Ring
                </span>
              </h1>
              <p className="mt-1 text-slate-300 text-sm sm:text-base max-w-2xl">
                {language === "ta"
                  ? "உதயம் (1 மணி நேரம்), ஆருடம் (5 நிமிடம்), கவிப்பு, 8 இடஞ்சுழி ஜாமக் கோள்கள் மற்றும் கடிகார நேர உடனடி பலன் சூத்திரங்கள்."
                  : "Udayam (1 hour), Arudam (5 min), Kavippu, 8 Anti-Clockwise Jama Grahas, and Snapshot Watch Time Shastra Rules."}
              </p>
            </div>

            {/* Quick Now Button */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  handleNowClick();
                  setTimeout(handleCalculate, 50);
                }}
                disabled={isLoading}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-900 font-bold shadow-lg shadow-amber-500/20 active:scale-95 transition-all text-sm"
              >
                <Zap className="w-4 h-4 fill-current text-slate-900 animate-pulse" />
                <span>{language === "ta" ? "இந்த நொடி பிரசன்னம்" : "Cast Current Moment (Now)"}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="w-full max-w-7xl 2xl:max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 2xl:px-10 mt-6 space-y-6">
        {/* Controls Card */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-5 sm:p-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-blue-600" />
                <span>{language === "ta" ? "தேதி" : "Query Date"}</span>
              </label>
              <input
                type="date"
                value={dateInput}
                onChange={(e) => setDateInput(e.target.value)}
                className="w-full text-sm rounded-xl border border-slate-300 px-3 py-2 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#153F6B] focus:border-transparent font-medium"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-blue-600" />
                <span>{language === "ta" ? "நேரம் (துல்லிய வினாடி)" : "Exact Query Time"}</span>
              </label>
              <div className="flex gap-2">
                <input
                  type="time"
                  step="1"
                  value={timeInput}
                  onChange={(e) => setTimeInput(e.target.value)}
                  className="w-full text-sm rounded-xl border border-slate-300 px-3 py-2 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#153F6B] focus:border-transparent font-medium"
                />
                <button
                  type="button"
                  onClick={handleNowClick}
                  title={language === "ta" ? "தற்போதைய நேரம்" : "Current Time"}
                  className="px-2.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold flex items-center transition"
                >
                  <Timer className="w-4 h-4 text-amber-600" />
                </button>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-blue-600" />
                <span>{language === "ta" ? "பிரசன்ன இடம் (நகரம்)" : "Location / City"}</span>
              </label>
              <select
                value={selectedCity.name_en}
                onChange={(e) => {
                  const city = CITY_PRESETS.find((c) => c.name_en === e.target.value);
                  if (city) setSelectedCity(city);
                }}
                className="w-full text-sm rounded-xl border border-slate-300 px-3 py-2 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#153F6B] focus:border-transparent font-medium"
              >
                {CITY_PRESETS.map((c) => (
                  <option key={c.name_en} value={c.name_en}>
                    {language === "ta" ? c.name_ta : c.name_en} ({c.tz.split("/")[1]})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                <span>{language === "ta" ? "கேள்வியின் பிரிவு" : "Query Classification"}</span>
              </label>
              <select
                value={queryCategory}
                onChange={(e) => setQueryCategory(e.target.value)}
                className="w-full text-sm rounded-xl border border-slate-300 px-3 py-2 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#153F6B] focus:border-transparent font-medium"
              >
                {QUERY_CATEGORIES.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {language === "ta" ? cat.name_ta : cat.name_en}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="mt-4 pt-4 border-t border-slate-100 grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-slate-600 mb-1">
                {language === "ta" ? "குறிப்பிட்ட வினா (விரும்பினால்)" : "Specific Question / Query Text (Optional)"}
              </label>
              <input
                type="text"
                placeholder={
                  language === "ta"
                    ? "எ.கா: தொழில் கூட்டு ஒப்பந்தம் வெற்றி பெறுமா? பொருள் எங்கே?"
                    : "e.g., Will my property contract be signed? Where is the lost object?"
                }
                value={queryText}
                onChange={(e) => setQueryText(e.target.value)}
                className="w-full text-sm rounded-xl border border-slate-300 px-3 py-2 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#153F6B] focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1 flex items-center justify-between">
                <span>{language === "ta" ? "கேள்வியாளர் எண் (1-108)" : "Querent Seed (1-108 / 249)"}</span>
                <span className="text-[10px] text-slate-400 font-normal">
                  {language === "ta" ? "ஆருட மாற்று" : "Optional override"}
                </span>
              </label>
              <div className="flex gap-2">
                <input
                  type="number"
                  min="1"
                  max="249"
                  placeholder={language === "ta" ? "நேர ஆருடம் (Default)" : "Time-based (Default)"}
                  value={querentSeed}
                  onChange={(e) => setQuerentSeed(e.target.value)}
                  className="w-full text-sm rounded-xl border border-slate-300 px-3 py-2 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#153F6B] focus:border-transparent"
                />
                <button
                  type="button"
                  onClick={handleCalculate}
                  disabled={isLoading}
                  className="px-5 py-2 rounded-xl bg-[#153F6B] hover:bg-[#1E4D82] text-white font-bold text-sm shadow flex items-center gap-1.5 transition whitespace-nowrap"
                >
                  {isLoading ? (
                    <RefreshCw className="w-4 h-4 animate-spin text-amber-300" />
                  ) : (
                    <Compass className="w-4 h-4 text-amber-300" />
                  )}
                  <span>{language === "ta" ? "கணிக்கவும்" : "Cast Chart"}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 text-rose-700 text-sm flex items-center gap-2">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {result && (
          <div className="space-y-6">
            {/* Snapshot Watch Time Prediction Alert Banner */}
            <div
              className={`rounded-2xl p-4 sm:p-5 border-2 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
                result.classical_rules.watch_time_relation.result === "Success"
                  ? "bg-emerald-50/90 border-emerald-400 text-emerald-950"
                  : result.classical_rules.watch_time_relation.result === "Delay and Failure"
                  ? "bg-amber-50/90 border-amber-400 text-amber-950"
                  : "bg-rose-50/90 border-rose-400 text-rose-950"
              }`}
            >
              <div className="flex items-start sm:items-center gap-3">
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold text-white shadow-xs flex-shrink-0 ${
                    result.classical_rules.watch_time_relation.result === "Success"
                      ? "bg-emerald-600"
                      : result.classical_rules.watch_time_relation.result === "Delay and Failure"
                      ? "bg-amber-600"
                      : "bg-rose-600"
                  }`}
                >
                  <Timer className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-xs font-bold uppercase tracking-wider opacity-80">
                    {language === "ta" ? "கடிகார நேர உடனடி பலன் (Snapshot Watch Time)" : "Snapshot Watch Time Prediction"}
                  </div>
                  <div className="text-base sm:text-lg font-extrabold flex items-center gap-2">
                    <span>
                      {language === "ta" ? "உதயம் - ஆருடம் தொடர்பு:" : "Udayam - Arudham:"}{" "}
                      {result.classical_rules.watch_time_relation.relation_type}
                    </span>
                    <span
                      className={`text-xs px-2.5 py-0.5 rounded-full font-extrabold ${
                        result.classical_rules.watch_time_relation.result === "Success"
                          ? "bg-emerald-600 text-white"
                          : result.classical_rules.watch_time_relation.result === "Delay and Failure"
                          ? "bg-amber-600 text-white"
                          : "bg-rose-600 text-white"
                      }`}
                    >
                      {language === "ta"
                        ? result.classical_rules.watch_time_relation.result === "Success"
                          ? "வெற்றி (Success)"
                          : result.classical_rules.watch_time_relation.result === "Delay and Failure"
                          ? "தாமதம் & தோல்வி"
                          : "தோல்வி (Failure)"
                        : result.classical_rules.watch_time_relation.result}
                    </span>
                  </div>
                  <div className="text-xs sm:text-sm font-medium mt-0.5">
                    {language === "ta"
                      ? result.classical_rules.watch_time_relation.description_ta
                      : result.classical_rules.watch_time_relation.description_en}
                  </div>
                </div>
              </div>

              {/* Debilitated in Udayam Warning */}
              {result.classical_rules.exalted_debilitated_audit.debilitated_in_udayam && (
                <div className="bg-rose-600 text-white px-3 py-2 rounded-xl text-xs font-bold flex items-center gap-2 shadow-sm animate-pulse">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  <span>
                    {language === "ta"
                      ? "உதயத்தில் நீச கிரகம்: செய்ய முடியாத கேள்வி / வீண் பேச்சு!"
                      : "Debilitated in Udayam: Querent incapable / talking nonsense!"}
                  </span>
                </div>
              )}
            </div>

            {/* Solar & Active Jamam Summary Ribbon */}
            <div className="bg-gradient-to-r from-slate-900 to-[#153F6B] text-white rounded-2xl p-5 shadow-sm border border-slate-700">
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 text-center sm:text-left">
                <div className="bg-white/5 rounded-xl p-3 border border-white/10">
                  <div className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider flex items-center gap-1 justify-center sm:justify-start">
                    {result.solar_info.is_day ? (
                      <Sun className="w-3.5 h-3.5 text-amber-400" />
                    ) : (
                      <Moon className="w-3.5 h-3.5 text-indigo-300" />
                    )}
                    <span>{language === "ta" ? "பொழுது" : "Period"}</span>
                  </div>
                  <div className="text-base font-bold text-white mt-1">
                    {result.solar_info.is_day
                      ? language === "ta"
                        ? "பகல் பொழுது"
                        : "Daytime"
                      : language === "ta"
                      ? "இரவுப் பொழுது"
                      : "Nighttime"}
                  </div>
                  <div className="text-[11px] text-slate-300 mt-0.5">
                    {result.solar_info.sunrise_local} - {result.solar_info.sunset_local}
                  </div>
                </div>

                <div className="bg-white/5 rounded-xl p-3 border border-white/10">
                  <div className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider flex items-center gap-1 justify-center sm:justify-start">
                    <Timer className="w-3.5 h-3.5 text-emerald-400" />
                    <span>{language === "ta" ? "ஜாம எண்" : "Active Jamam"}</span>
                  </div>
                  <div className="text-base font-bold text-amber-300 mt-1">
                    {language === "ta"
                      ? `${result.jamam_info.jamam_number}-ம் ஜாமம்`
                      : `Jamam #${result.jamam_info.jamam_number}`}
                  </div>
                  <div className="text-[11px] text-slate-300 mt-0.5">
                    {result.jamam_info.jamam_start_local} - {result.jamam_info.jamam_end_local}
                  </div>
                </div>

                <div className="bg-white/5 rounded-xl p-3 border border-white/10">
                  <div className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider flex items-center gap-1 justify-center sm:justify-start">
                    <Flame className="w-3.5 h-3.5 text-amber-400" />
                    <span>{language === "ta" ? "ஜாம நாதன்" : "Jamam Lord"}</span>
                  </div>
                  <div className="text-base font-bold text-white mt-1 flex items-center gap-1.5 justify-center sm:justify-start">
                    <span>{result.jamam_info.jamam_ruler_symbol}</span>
                    <span>
                      {language === "ta"
                        ? result.jamam_info.jamam_ruler_ta
                        : result.jamam_info.jamam_ruler_en}
                    </span>
                  </div>
                  <div className="text-[11px] text-emerald-300 mt-0.5 font-medium">
                    {result.jamam_info.is_benefic_ruler
                      ? language === "ta"
                        ? "சுப கிரகம்"
                        : "Benefic Lord"
                      : language === "ta"
                      ? "அசுப கிரகம்"
                      : "Dynamic / Krura"}
                  </div>
                </div>

                <div className="bg-white/5 rounded-xl p-3 border border-white/10">
                  <div className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider flex items-center gap-1 justify-center sm:justify-start">
                    <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                    <span>{language === "ta" ? "கிழமை நாதன்" : "Day Lord"}</span>
                  </div>
                  <div className="text-base font-bold text-white mt-1">
                    {language === "ta"
                      ? result.jamam_info.weekday_lord_ta
                      : result.jamam_info.weekday_lord_en}
                  </div>
                  <div className="text-[11px] text-slate-300 mt-0.5">
                    {result.solar_info.dinamana_ghatikas} {language === "ta" ? "நாழிகை" : "Ghatikas"}
                  </div>
                </div>

                <div className="bg-white/5 rounded-xl p-3 border border-white/10">
                  <div className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider flex items-center gap-1 justify-center sm:justify-start">
                    <Navigation className="w-3.5 h-3.5 text-cyan-400" />
                    <span>{language === "ta" ? "சூரிய வீதி" : "Surya Veethi"}</span>
                  </div>
                  <div className="text-base font-bold text-cyan-300 mt-1">
                    {language === "ta"
                      ? result.solar_info.surya_veethi
                      : result.solar_info.surya_veethi_en}
                  </div>
                  <div className="text-[11px] text-slate-300 mt-0.5">
                    {language === "ta" ? "கவிப்பு அளவுகோல்" : "Anchor Path"}
                  </div>
                </div>

                <div className="bg-white/5 rounded-xl p-3 border border-white/10">
                  <div className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider flex items-center gap-1 justify-center sm:justify-start">
                    <Clock className="w-3.5 h-3.5 text-amber-400" />
                    <span>{language === "ta" ? "ஜாம முன்னேற்றம்" : "Progress"}</span>
                  </div>
                  <div className="text-base font-bold text-amber-400 mt-1">
                    {result.jamam_info.progress_percent}%
                  </div>
                  <div className="w-full bg-slate-700 h-1.5 rounded-full mt-1.5 overflow-hidden">
                    <div
                      className="bg-amber-400 h-full rounded-full transition-all duration-500"
                      style={{ width: `${result.jamam_info.progress_percent}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* The 3 Core Pillars (முப்புள்ளி) Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              {/* Udhayam */}
              <div className="bg-white rounded-2xl p-5 border-2 border-blue-500/30 shadow-sm relative overflow-hidden">
                <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/5 rounded-bl-full pointer-events-none" />
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-0.5 rounded-md bg-blue-100 text-blue-800 text-xs font-bold uppercase tracking-wider">
                    {language === "ta" ? "உதயம் (Udayam)" : "Udayam (Lagna)"}
                  </span>
                  <span className="text-xs text-slate-500 font-medium">
                    {language === "ta" ? "1 மணி நேரத்திற்கு மாறும்" : "Changes in 1 hour"}
                  </span>
                </div>
                <div className="mt-3">
                  <div className="text-2xl font-extrabold text-[#153F6B]">
                    {language === "ta"
                      ? result.three_pillars.udhayam.sign_name_ta
                      : result.three_pillars.udhayam.sign_name_en}
                  </div>
                  <div className="text-sm font-semibold text-slate-600 mt-0.5">
                    {result.three_pillars.udhayam.dms} ({result.three_pillars.udhayam.nature_ta} /{" "}
                    {result.three_pillars.udhayam.direction_ta})
                  </div>
                </div>
                <div className="mt-4 pt-3 border-t border-slate-100 text-xs text-slate-600 space-y-1">
                  <div className="flex justify-between">
                    <span className="text-slate-500">{language === "ta" ? "ராசி நாதன்:" : "Sign Lord:"}</span>
                    <span className="font-semibold text-slate-800">
                      {language === "ta"
                        ? result.three_pillars.udhayam.lord_ta
                        : result.three_pillars.udhayam.lord_en}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">{language === "ta" ? "நட்சத்திரம்:" : "Nakshatra:"}</span>
                    <span className="font-semibold text-slate-800">
                      {result.three_pillars.udhayam.nakshatra_name} ({language === "ta" ? "பாதம்" : "Pada"}{" "}
                      {result.three_pillars.udhayam.pada})
                    </span>
                  </div>
                </div>
              </div>

              {/* Aarudham */}
              <div className="bg-white rounded-2xl p-5 border-2 border-emerald-500/30 shadow-sm relative overflow-hidden">
                <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-bl-full pointer-events-none" />
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-0.5 rounded-md bg-emerald-100 text-emerald-800 text-xs font-bold uppercase tracking-wider">
                    {language === "ta" ? "ஆருடம் (Arudam)" : "Aarudham"}
                  </span>
                  <span className="text-xs text-slate-500 font-medium">
                    {language === "ta" ? "5 நிமிடத்திற்கு மாறும்" : "Changes in 5 mins"}
                  </span>
                </div>
                <div className="mt-3">
                  <div className="text-2xl font-extrabold text-emerald-700">
                    {language === "ta"
                      ? result.three_pillars.aarudham.sign_name_ta
                      : result.three_pillars.aarudham.sign_name_en}
                  </div>
                  <div className="text-sm font-semibold text-slate-600 mt-0.5">
                    {result.three_pillars.aarudham.dms} ({result.three_pillars.aarudham.nature_ta} /{" "}
                    {result.three_pillars.aarudham.direction_ta})
                  </div>
                </div>
                <div className="mt-4 pt-3 border-t border-slate-100 text-xs text-slate-600 space-y-1">
                  <div className="flex justify-between">
                    <span className="text-slate-500">{language === "ta" ? "ராசி நாதன்:" : "Sign Lord:"}</span>
                    <span className="font-semibold text-slate-800">
                      {language === "ta"
                        ? result.three_pillars.aarudham.lord_ta
                        : result.three_pillars.aarudham.lord_en}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">{language === "ta" ? "உதயத்திலிருந்து பாவம்:" : "Bhava from Udayam:"}</span>
                    <span className="font-bold text-emerald-800">
                      {result.classical_rules.watch_time_relation.house_from_udayam}-ம் பாவம் ({result.classical_rules.watch_time_relation.relation_type})
                    </span>
                  </div>
                </div>
              </div>

              {/* Kavippu */}
              <div className="bg-white rounded-2xl p-5 border-2 border-rose-500/30 shadow-sm relative overflow-hidden">
                <div className="absolute top-0 right-0 w-24 h-24 bg-rose-500/5 rounded-bl-full pointer-events-none" />
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-0.5 rounded-md bg-rose-100 text-rose-800 text-xs font-bold uppercase tracking-wider">
                    {language === "ta" ? "கவிப்பு (Kavippu)" : "Kavippu (Shield)"}
                  </span>
                  <span className="text-xs text-slate-500 font-medium">
                    {language === "ta" ? "தடை & ரகசிய கண்டம்" : "Consequence / Obstacle"}
                  </span>
                </div>
                <div className="mt-3">
                  <div className="text-2xl font-extrabold text-rose-700">
                    {language === "ta"
                      ? result.three_pillars.kavippu.sign_name_ta
                      : result.three_pillars.kavippu.sign_name_en}
                  </div>
                  <div className="text-sm font-semibold text-slate-600 mt-0.5">
                    {result.three_pillars.kavippu.dms} ({result.three_pillars.kavippu.nature_ta} /{" "}
                    {result.three_pillars.kavippu.direction_ta})
                  </div>
                </div>
                <div className="mt-4 pt-3 border-t border-slate-100 text-xs text-slate-600 space-y-1">
                  <div className="flex justify-between">
                    <span className="text-slate-500">{language === "ta" ? "உதயத்திலிருந்து பாவம்:" : "Bhava from Udayam:"}</span>
                    <span className="font-bold text-rose-800">
                      {result.classical_rules.kavippu_afflictions.kavippu_bhava_from_udayam}-ம் பாவம்
                      {result.classical_rules.kavippu_afflictions.kavippu_in_2nd && " (2-ல் கவிப்பு - தன நஷ்டம்!)"}
                      {result.classical_rules.kavippu_afflictions.kavippu_in_11th && " (11-ல் கவிப்பு - லாபத் தடை!)"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">{language === "ta" ? "வீதி அளவுகோல்:" : "Veethi:"}</span>
                    <span className="font-semibold text-slate-800">
                      {language === "ta"
                        ? result.three_pillars.kavippu.surya_veethi
                        : result.three_pillars.kavippu.surya_veethi_en}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* South Indian Dual-Ring Chart */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-5 sm:p-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-2">
                <div>
                  <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                    <Compass className="w-5 h-5 text-amber-600" />
                    <span>{language === "ta" ? "ஜாமக்கோள் பிரசன்ன சக்கரம் (Dual-Ring)" : "Jamakkol Horary Dual-Ring Chart"}</span>
                  </h2>
                  <p className="text-xs text-slate-500">
                    {language === "ta"
                      ? "உள்வட்டம்: கோச்சாரக் கோள்கள் (வேர் - அதிக பலம்) | வெளிவட்டம்: 8 இடஞ்சுழி ஜாமக் கோள்கள் (கிளைகள்)"
                      : "Inner Ring: Actual Transit Planets (Root - More Powerful) | Outer Ring: 8 Anti-Clockwise Jama Grahas (Branches)"}
                  </p>
                </div>

                <div className="flex items-center gap-3 text-xs">
                  <div className="flex items-center gap-1.5">
                    <span className="w-3 h-3 rounded-full bg-blue-500 inline-block" />
                    <span className="font-medium text-slate-700">{language === "ta" ? "உதயம்" : "Udayam"}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="w-3 h-3 rounded-full bg-emerald-500 inline-block" />
                    <span className="font-medium text-slate-700">{language === "ta" ? "ஆருடம்" : "Arudam"}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="w-3 h-3 rounded-full bg-rose-500 inline-block" />
                    <span className="font-medium text-slate-700">{language === "ta" ? "கவிப்பு" : "Kavippu"}</span>
                  </div>
                </div>
              </div>

              {/* 4x4 Grid */}
              <div className="mt-5 grid grid-cols-4 gap-2 sm:gap-3 bg-slate-100 p-2 sm:p-3 rounded-2xl border border-slate-300">
                {[12, 1, 2, 3].map((signIdx) => (
                  <ChartCell key={signIdx} signIdx={signIdx} houseMap={houseMap} language={language} />
                ))}

                <ChartCell signIdx={11} houseMap={houseMap} language={language} />
                <div className="col-span-2 row-span-2 bg-gradient-to-br from-[#0E294A] to-[#153F6B] rounded-xl p-4 text-white flex flex-col justify-between shadow-inner border border-amber-500/30">
                  <div>
                    <div className="flex items-center justify-between text-xs text-amber-300 font-semibold border-b border-white/10 pb-2">
                      <span>{language === "ta" ? "பிரசன்ன விவரம்" : "Prasanam Digest"}</span>
                      <span>{result.query_datetime.replace("T", " ").substring(0, 19)}</span>
                    </div>

                    <div className="mt-3 space-y-1.5 text-xs">
                      <div className="flex justify-between">
                        <span className="text-slate-300">{language === "ta" ? "உதய தொடர்பு (Watch Time):" : "Watch Time Relation:"}</span>
                        <span className="font-bold text-amber-300">
                          {result.classical_rules.watch_time_relation.relation_type} ({result.classical_rules.watch_time_relation.result})
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-300">{language === "ta" ? "ஜாம நாதன்:" : "Jamam Ruler:"}</span>
                        <span className="font-bold text-amber-400">
                          {language === "ta"
                            ? result.jamam_info.jamam_ruler_ta
                            : result.jamam_info.jamam_ruler_en}{" "}
                          ({result.jamam_info.jamam_number}-ம் ஜாமம்)
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-300">{language === "ta" ? "10-ம் அதிபதி இருப்பு:" : "10th Lord in Bhava:"}</span>
                        <span className="font-bold text-cyan-300">
                          {result.classical_rules.lord_connections.tenth_lord_bhava}-ம் பாவம் ({result.classical_rules.lord_connections.tenth_lord})
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-300">{language === "ta" ? "கவிப்பு பாவம்:" : "Kavippu Bhava:"}</span>
                        <span className="font-bold text-rose-300">
                          {result.classical_rules.kavippu_afflictions.kavippu_bhava_from_udayam}-ம் பாவம்
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="mt-3 pt-2 border-t border-white/10 flex items-center justify-between">
                    <span className="text-[11px] text-slate-300">
                      {language === "ta" ? "காரிய முடிவு:" : "Verdict:"}
                    </span>
                    <span
                      className={`text-xs font-bold px-2.5 py-0.5 rounded-full ${
                        result.prediction_verdict.status === "favorable"
                          ? "bg-emerald-500/20 text-emerald-300 border border-emerald-400/40"
                          : result.prediction_verdict.status === "delayed_success"
                          ? "bg-amber-500/20 text-amber-300 border border-amber-400/40"
                          : "bg-rose-500/20 text-rose-300 border border-rose-400/40"
                      }`}
                    >
                      {language === "ta"
                        ? result.prediction_verdict.verdict_title_ta.split("-")[0]
                        : result.prediction_verdict.status.toUpperCase()}
                    </span>
                  </div>
                </div>
                <ChartCell signIdx={4} houseMap={houseMap} language={language} />

                <ChartCell signIdx={10} houseMap={houseMap} language={language} />
                <ChartCell signIdx={5} houseMap={houseMap} language={language} />

                {[9, 8, 7, 6].map((signIdx) => (
                  <ChartCell key={signIdx} signIdx={signIdx} houseMap={houseMap} language={language} />
                ))}
              </div>
            </div>

            {/* Analysis Tabs */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
              <div className="flex border-b border-slate-200 bg-slate-50 px-4 sm:px-6 gap-2 overflow-x-auto">
                <button
                  onClick={() => setActiveTab("verdict")}
                  className={`py-3.5 px-4 font-semibold text-sm border-b-2 flex items-center gap-2 whitespace-nowrap transition-all ${
                    activeTab === "verdict"
                      ? "border-[#153F6B] text-[#153F6B] bg-white"
                      : "border-transparent text-slate-500 hover:text-slate-800"
                  }`}
                >
                  <Award className="w-4 h-4 text-amber-600" />
                  <span>{language === "ta" ? "காரிய சித்தி தீர்ப்பு" : "Verdict & Synthesis"}</span>
                </button>

                <button
                  onClick={() => setActiveTab("rules")}
                  className={`py-3.5 px-4 font-semibold text-sm border-b-2 flex items-center gap-2 whitespace-nowrap transition-all ${
                    activeTab === "rules"
                      ? "border-[#153F6B] text-[#153F6B] bg-white"
                      : "border-transparent text-slate-500 hover:text-slate-800"
                  }`}
                >
                  <BookOpen className="w-4 h-4 text-purple-600" />
                  <span>{language === "ta" ? "சாஸ்திர விதிகள் (Classical Rules)" : "Classical Rules Audit"}</span>
                </button>

                <button
                  onClick={() => setActiveTab("domains")}
                  className={`py-3.5 px-4 font-semibold text-sm border-b-2 flex items-center gap-2 whitespace-nowrap transition-all ${
                    activeTab === "domains"
                      ? "border-[#153F6B] text-[#153F6B] bg-white"
                      : "border-transparent text-slate-500 hover:text-slate-800"
                  }`}
                >
                  <Sparkles className="w-4 h-4 text-amber-500" />
                  <span>{language === "ta" ? "துறைசார் ஆய்வுகள் (Domain Rules)" : "Domain Shastra Rules"}</span>
                </button>

                <button
                  onClick={() => setActiveTab("pillars")}
                  className={`py-3.5 px-4 font-semibold text-sm border-b-2 flex items-center gap-2 whitespace-nowrap transition-all ${
                    activeTab === "pillars"
                      ? "border-[#153F6B] text-[#153F6B] bg-white"
                      : "border-transparent text-slate-500 hover:text-slate-800"
                  }`}
                >
                  <Layers className="w-4 h-4 text-blue-600" />
                  <span>{language === "ta" ? "முப்புள்ளி & கோள்கள்" : "Pillars & Grahas"}</span>
                </button>

                <button
                  onClick={() => setActiveTab("direction")}
                  className={`py-3.5 px-4 font-semibold text-sm border-b-2 flex items-center gap-2 whitespace-nowrap transition-all ${
                    activeTab === "direction"
                      ? "border-[#153F6B] text-[#153F6B] bg-white"
                      : "border-transparent text-slate-500 hover:text-slate-800"
                  }`}
                >
                  <Navigation className="w-4 h-4 text-emerald-600" />
                  <span>{language === "ta" ? "திசை & சம்பவ காலம்" : "Direction & Timing"}</span>
                </button>

                <button
                  onClick={() => setActiveTab("houses")}
                  className={`py-3.5 px-4 font-semibold text-sm border-b-2 flex items-center gap-2 whitespace-nowrap transition-all ${
                    activeTab === "houses"
                      ? "border-[#153F6B] text-[#153F6B] bg-white"
                      : "border-transparent text-slate-500 hover:text-slate-800"
                  }`}
                >
                  <Compass className="w-4 h-4 text-indigo-600" />
                  <span>{language === "ta" ? "12 பாவ நிலைகள்" : "12 Bhavas Table"}</span>
                </button>
              </div>

              <div className="p-5 sm:p-6">
                {/* 1. Verdict Tab */}
                {activeTab === "verdict" && (
                  <div className="space-y-6">
                    <div
                      className={`rounded-2xl p-6 border-2 ${
                        result.prediction_verdict.status === "favorable"
                          ? "bg-emerald-50/70 border-emerald-400 text-emerald-950"
                          : result.prediction_verdict.status === "delayed_success"
                          ? "bg-amber-50/70 border-amber-400 text-amber-950"
                          : "bg-rose-50/70 border-rose-400 text-rose-950"
                      }`}
                    >
                      <div className="flex items-start gap-4">
                        <div
                          className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm ${
                            result.prediction_verdict.status === "favorable"
                              ? "bg-emerald-600 text-white"
                              : result.prediction_verdict.status === "delayed_success"
                              ? "bg-amber-600 text-white"
                              : "bg-rose-600 text-white"
                          }`}
                        >
                          {result.prediction_verdict.status === "favorable" ? (
                            <CheckCircle2 className="w-7 h-7" />
                          ) : result.prediction_verdict.status === "delayed_success" ? (
                            <AlertTriangle className="w-7 h-7" />
                          ) : (
                            <ShieldAlert className="w-7 h-7" />
                          )}
                        </div>

                        <div className="flex-1">
                          <h3 className="text-xl font-extrabold tracking-tight">
                            {language === "ta"
                              ? result.prediction_verdict.verdict_title_ta
                              : result.prediction_verdict.verdict_title_en}
                          </h3>
                          <p className="mt-2 text-sm sm:text-base leading-relaxed font-medium">
                            {language === "ta"
                              ? result.prediction_verdict.verdict_summary_ta
                              : result.prediction_verdict.verdict_summary_en}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Query Verification Box (10th Lord & Arudam Bhava) */}
                    <div className="bg-slate-50 rounded-2xl p-5 border border-slate-200">
                      <h4 className="text-sm font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2 mb-3">
                        <Eye className="w-4 h-4 text-blue-600" />
                        <span>{language === "ta" ? "கேள்வி சரிபார்த்தல் (Query Verification)" : "Query Verification via 10th Lord & Arudam"}</span>
                      </h4>
                      <div className="space-y-2 text-sm text-slate-700">
                        <div className="p-3 bg-white rounded-xl border border-slate-200">
                          <span className="font-bold text-[#153F6B]">
                            {language === "ta" ? "10-ம் அதிபதி வழியே:" : "Through 10th Lord:"}
                          </span>{" "}
                          <span>
                            {language === "ta"
                              ? result.classical_rules.lord_connections.tenth_lord_query_signification_ta
                              : result.classical_rules.lord_connections.tenth_lord_query_signification_en}
                          </span>
                        </div>
                        <div className="p-3 bg-white rounded-xl border border-slate-200">
                          <span className="font-bold text-emerald-700">
                            {language === "ta" ? "ஆருட பாவம் வழியே:" : "Through Arudam Bhava:"}
                          </span>{" "}
                          <span>
                            {language === "ta"
                              ? `ஆருடம் உதயத்திற்கு ${result.classical_rules.watch_time_relation.house_from_udayam}-ம் பாவத்தில் நிற்பதால், கேள்வி அப்பாவக விஷயம் தொடர்புடையது.`
                              : `Arudam is in the ${result.classical_rules.watch_time_relation.house_from_udayam}th house from Udayam; question corresponds to that bhava.`}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Category-Specific Insights */}
                    {result.prediction_verdict.category_specific_insights_en.length > 0 && (
                      <div className="bg-slate-50 rounded-2xl p-5 border border-slate-200">
                        <h4 className="text-sm font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2 mb-3">
                          <Sparkles className="w-4 h-4 text-blue-600" />
                          <span>
                            {language === "ta"
                              ? "கேள்விப் பிரிவு சார்ந்த சிறப்பு வழிகாட்டல்"
                              : "Category-Specific Astrological Insights"}
                          </span>
                        </h4>
                        <ul className="space-y-2">
                          {(language === "ta"
                            ? result.prediction_verdict.category_specific_insights_ta
                            : result.prediction_verdict.category_specific_insights_en
                          ).map((insight, idx) => (
                            <li key={idx} className="flex items-start gap-2.5 text-sm text-slate-700">
                              <span className="w-1.5 h-1.5 rounded-full bg-blue-600 mt-2 flex-shrink-0" />
                              <span>{insight}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Classical Remedies */}
                    <div className="bg-amber-50/50 rounded-2xl p-5 border border-amber-200">
                      <h4 className="text-sm font-bold text-amber-900 uppercase tracking-wider flex items-center gap-2 mb-3">
                        <Flame className="w-4 h-4 text-amber-600" />
                        <span>{language === "ta" ? "சாஸ்திர பரிகாரங்கள் & அனுகூல வழிமுறைகள்" : "Classical Remedies & Pariharam"}</span>
                      </h4>
                      <ul className="space-y-2.5">
                        {(language === "ta"
                          ? result.prediction_verdict.remedial_measures_ta
                          : result.prediction_verdict.remedial_measures_en
                        ).map((rem, idx) => (
                          <li key={idx} className="flex items-start gap-2.5 text-sm text-slate-700">
                            <span className="w-5 h-5 rounded-full bg-amber-200 text-amber-800 text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                              {idx + 1}
                            </span>
                            <span>{rem}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {/* 2. Classical Rules Audit Tab */}
                {activeTab === "rules" && (
                  <div className="space-y-6">
                    {/* Grid of Key Classical Shastra Rules */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Rule 1: Watch Time Relation */}
                      <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-xs">
                        <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                          1. {language === "ta" ? "உதயம் - ஆருடம் தொடர்பு" : "Watch Time Relation"}
                        </div>
                        <div className="text-base font-extrabold text-[#153F6B] mt-1 flex items-center justify-between">
                          <span>{result.classical_rules.watch_time_relation.relation_type}</span>
                          <span
                            className={`text-xs px-2 py-0.5 rounded font-bold ${
                              result.classical_rules.watch_time_relation.result === "Success"
                                ? "bg-emerald-100 text-emerald-800"
                                : result.classical_rules.watch_time_relation.result === "Delay and Failure"
                                ? "bg-amber-100 text-amber-800"
                                : "bg-rose-100 text-rose-800"
                            }`}
                          >
                            {result.classical_rules.watch_time_relation.result}
                          </span>
                        </div>
                        <p className="text-xs text-slate-600 mt-1.5">
                          {language === "ta"
                            ? result.classical_rules.watch_time_relation.description_ta
                            : result.classical_rules.watch_time_relation.description_en}
                        </p>
                      </div>

                      {/* Rule 2: Facing Direction */}
                      <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-xs">
                        <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                          2. {language === "ta" ? "நோக்கு நிலை (Facing from Sun)" : "Facing Direction (From Sun)"}
                        </div>
                        <div className="text-base font-extrabold text-[#153F6B] mt-1 flex items-center justify-between">
                          <span>
                            {language === "ta"
                              ? result.classical_rules.facing_direction.facing_name_ta
                              : result.classical_rules.facing_direction.facing_type}
                          </span>
                          <span
                            className={`text-xs px-2 py-0.5 rounded font-bold ${
                              result.classical_rules.facing_direction.result === "Success"
                                ? "bg-emerald-100 text-emerald-800"
                                : result.classical_rules.facing_direction.result === "Success after Failure"
                                ? "bg-amber-100 text-amber-800"
                                : "bg-slate-100 text-slate-700"
                            }`}
                          >
                            {result.classical_rules.facing_direction.result}
                          </span>
                        </div>
                        <p className="text-xs text-slate-600 mt-1.5">
                          {language === "ta"
                            ? result.classical_rules.facing_direction.description_ta
                            : result.classical_rules.facing_direction.description_en}
                        </p>
                      </div>

                      {/* Rule 3: Rising Nature */}
                      <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-xs">
                        <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                          3. {language === "ta" ? "உதய ராசி தன்மை" : "Rising Nature (Siro/Pristo)"}
                        </div>
                        <div className="text-base font-extrabold text-[#153F6B] mt-1 flex items-center justify-between">
                          <span>
                            {language === "ta"
                              ? result.classical_rules.rising_nature.nature_name_ta
                              : result.classical_rules.rising_nature.nature_type}
                          </span>
                          <span
                            className={`text-xs px-2 py-0.5 rounded font-bold ${
                              result.classical_rules.rising_nature.result === "Success"
                                ? "bg-emerald-100 text-emerald-800"
                                : result.classical_rules.rising_nature.result === "Success after delay"
                                ? "bg-amber-100 text-amber-800"
                                : "bg-slate-100 text-slate-700"
                            }`}
                          >
                            {result.classical_rules.rising_nature.result}
                          </span>
                        </div>
                        <p className="text-xs text-slate-600 mt-1.5">
                          {language === "ta"
                            ? result.classical_rules.rising_nature.description_ta
                            : result.classical_rules.rising_nature.description_en}
                        </p>
                      </div>

                      {/* Rule 4: Subh Udayam & Subh Arudam Balance */}
                      <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-xs">
                        <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                          4. {language === "ta" ? "சுப உதயம் & சுப ஆருடம்" : "Subh Udayam & Subh Arudam"}
                        </div>
                        <div className="text-base font-extrabold text-[#153F6B] mt-1 flex items-center justify-between">
                          <span>{result.classical_rules.subh_balance.result}</span>
                          <span className="text-xs px-2 py-0.5 rounded font-bold bg-indigo-50 text-indigo-700">
                            {result.classical_rules.subh_balance.is_subh_udayam ? "U: Subh" : "U: Asubh"} |{" "}
                            {result.classical_rules.subh_balance.is_subh_arudam ? "A: Subh" : "A: Asubh"}
                          </span>
                        </div>
                        <p className="text-xs text-slate-600 mt-1.5">
                          {language === "ta"
                            ? result.classical_rules.subh_balance.description_ta
                            : result.classical_rules.subh_balance.description_en}
                        </p>
                      </div>

                      {/* Rule 5: 10th and 11th Lord Connection */}
                      <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-xs">
                        <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                          5. {language === "ta" ? "10 மற்றும் 11-ம் அதிபதிகள் தொடர்பு" : "10th & 11th Lord Connection"}
                        </div>
                        <div className="mt-1.5 space-y-1 text-xs">
                          <div className="flex justify-between items-center">
                            <span>{language === "ta" ? "10-ம் அதிபதி தொடர்பு (வெற்றி):" : "10th Lord Connection:"}</span>
                            <span className="font-bold">
                              {result.classical_rules.lord_connections.tenth_lord_connected ? (
                                <span className="text-emerald-600">
                                  {result.classical_rules.lord_connections.tenth_lord_connection_type}
                                </span>
                              ) : (
                                <span className="text-slate-400">None</span>
                              )}
                            </span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span>{language === "ta" ? "11-ம் அதிபதி தொடர்பு (லாபம்):" : "11th Lord Connection:"}</span>
                            <span className="font-bold">
                              {result.classical_rules.lord_connections.eleventh_lord_connected ? (
                                <span className="text-emerald-600">
                                  {result.classical_rules.lord_connections.eleventh_lord_connection_type}
                                </span>
                              ) : (
                                <span className="text-slate-400">None</span>
                              )}
                            </span>
                          </div>
                          {result.classical_rules.lord_connections.parivartana_udayam_10th && (
                            <div className="text-emerald-600 font-bold">
                              ★ Parivartana Yoga between Udayam and 10th Lord!
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Rule 6: Kavippu in 2nd / 11th Impact */}
                      <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-xs">
                        <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                          6. {language === "ta" ? "கவிப்பு பாவம் & தோஷங்கள்" : "Kavippu Placement & Afflictions"}
                        </div>
                        <div className="text-sm font-bold text-rose-700 mt-1">
                          {language === "ta"
                            ? result.classical_rules.kavippu_afflictions.afflicted_bhava_meaning_ta
                            : result.classical_rules.kavippu_afflictions.afflicted_bhava_meaning_en}
                        </div>
                        {result.classical_rules.kavippu_afflictions.afflicted_transit_planets.length > 0 && (
                          <div className="text-xs text-rose-600 font-semibold mt-1">
                            Afflicted Planets: {result.classical_rules.kavippu_afflictions.afflicted_transit_planets.join(", ")} (Lose all power!)
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Approaching vs Crossed Planets Table */}
                    <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
                      <h4 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-3 flex items-center gap-2">
                        <Clock className="w-4 h-4 text-blue-600" />
                        <span>
                          {language === "ta"
                            ? "உதயத்தை நெருங்கும் / கடந்த கோள்கள் (நிகழ்காலம், எதிர்காலம் & இறந்தகாலம்)"
                            : "Planets Approaching vs Crossed Udayam (Present, Future & Past Events)"}
                        </span>
                      </h4>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Approaching */}
                        <div className="bg-blue-50/50 rounded-xl p-3.5 border border-blue-200">
                          <div className="text-xs font-bold text-blue-900 flex items-center gap-1.5 mb-2">
                            <TrendingUp className="w-3.5 h-3.5 text-blue-600" />
                            <span>
                              {language === "ta" ? "உதயத்தை நெருங்கும் கோள்கள் (நிகழ்காலம் & எதிர்காலம்)" : "Approaching Udayam (Present & Future)"}
                            </span>
                          </div>
                          {result.classical_rules.approaching_planets.length > 0 ? (
                            <div className="space-y-2">
                              {result.classical_rules.approaching_planets.map((p, idx) => (
                                <div key={idx} className="bg-white p-2.5 rounded-lg border border-blue-100 text-xs">
                                  <div className="font-bold text-blue-900 flex justify-between">
                                    <span>{language === "ta" ? p.name_ta : p.name_en}</span>
                                    <span className="text-[10px] text-blue-600 font-medium">{p.location}</span>
                                  </div>
                                  <div className="text-slate-600 mt-1">
                                    <span className="font-semibold text-slate-700">
                                      {language === "ta" ? "காரகத்துவம்:" : "Signifies:"}
                                    </span>{" "}
                                    {language === "ta" ? p.karakatwa_ta : p.karakatwa_en}
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <div className="text-xs text-slate-400 italic">No planets immediately approaching Udayam</div>
                          )}
                        </div>

                        {/* Crossed */}
                        <div className="bg-amber-50/50 rounded-xl p-3.5 border border-amber-200">
                          <div className="text-xs font-bold text-amber-900 flex items-center gap-1.5 mb-2">
                            <TrendingDown className="w-3.5 h-3.5 text-amber-600" />
                            <span>
                              {language === "ta" ? "உதயத்தைக் கடந்த கோள்கள் (இறந்த காலம்)" : "Crossed Udayam (Past Events)"}
                            </span>
                          </div>
                          {result.classical_rules.crossed_planets.length > 0 ? (
                            <div className="space-y-2">
                              {result.classical_rules.crossed_planets.map((p, idx) => (
                                <div key={idx} className="bg-white p-2.5 rounded-lg border border-amber-100 text-xs">
                                  <div className="font-bold text-amber-900 flex justify-between">
                                    <span>{language === "ta" ? p.name_ta : p.name_en}</span>
                                    <span className="text-[10px] text-amber-600 font-medium">{p.location}</span>
                                  </div>
                                  <div className="text-slate-600 mt-1">
                                    <span className="font-semibold text-slate-700">
                                      {language === "ta" ? "கடந்த நிகழ்வு:" : "Past Matter:"}
                                    </span>{" "}
                                    {language === "ta" ? p.karakatwa_ta : p.karakatwa_en}
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <div className="text-xs text-slate-400 italic">No planets recently crossed Udayam</div>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Classical Bhava Impacts: Kavippu 1-12 & Udayam Lord Thought */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Kavippu Bhava Effect */}
                      {result.classical_rules.kavippu_bhava_effect && (
                        <div className="bg-rose-50/80 rounded-2xl p-5 border border-rose-200 shadow-xs">
                          <div className="flex items-center gap-2 text-rose-900 font-bold text-sm mb-2">
                            <ShieldAlert className="w-4 h-4 text-rose-600" />
                            <span>
                              {language === "ta"
                                ? "உதயத்திற்கு கவிப்பு அமர்ந்த பாவகத்தின் தாக்கம்"
                                : "Kavippu Bhava Effect on Querent"}
                            </span>
                          </div>
                          <p className="text-xs leading-relaxed font-semibold text-rose-950">
                            {language === "ta"
                              ? result.classical_rules.kavippu_bhava_effect.ta
                              : result.classical_rules.kavippu_bhava_effect.en}
                          </p>
                        </div>
                      )}

                      {/* Udayam Lord Thought */}
                      {result.classical_rules.udayam_lord_thought && (
                        <div className="bg-indigo-50/80 rounded-2xl p-5 border border-indigo-200 shadow-xs">
                          <div className="flex items-center gap-2 text-indigo-900 font-bold text-sm mb-2">
                            <Eye className="w-4 h-4 text-indigo-600" />
                            <span>
                              {language === "ta"
                                ? "உதயாதிபதி அமர்ந்த பாவம் (கேள்வியாளரின் சிந்தனை)"
                                : "Udayam Lord Placement (Querent's Mind & Focus)"}
                            </span>
                          </div>
                          <p className="text-xs leading-relaxed font-semibold text-indigo-950">
                            {language === "ta"
                              ? result.classical_rules.udayam_lord_thought.ta
                              : result.classical_rules.udayam_lord_thought.en}
                          </p>
                        </div>
                      )}
                    </div>

                    {/* Conjoined & Parivartana Diamond Alerts */}
                    {((result.classical_rules.conjoined_inner_outer_planets && result.classical_rules.conjoined_inner_outer_planets.length > 0) ||
                      (result.classical_rules.parivartana_exchanges && result.classical_rules.parivartana_exchanges.length > 0) ||
                      result.classical_rules.eighth_lord_in_udayam?.is_in_udayam ||
                      result.classical_rules.snake_udayam_analysis?.snake_approaching) && (
                      <div className="space-y-3">
                        <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                          {language === "ta" ? "வைர விதிகள் & விசேஷ யோகங்கள்" : "Diamond Shastra Yogas & Alerts"}
                        </h4>

                        {/* Conjoined Planets (Double Impact) */}
                        {result.classical_rules.conjoined_inner_outer_planets?.map((c, idx) => (
                          <div key={idx} className="bg-amber-50 rounded-xl p-3.5 border border-amber-300 flex items-start gap-3">
                            <Sparkles className="w-4 h-4 text-amber-600 mt-0.5 shrink-0" />
                            <div className="text-xs text-amber-950">
                              <span className="font-extrabold text-amber-800">
                                {language === "ta" ? "இரட்டிப்பு பலன் (Double Impact): " : "Twofold Magnification: "}
                              </span>
                              {language === "ta" ? c.effect_ta : c.effect_en}
                            </div>
                          </div>
                        ))}

                        {/* Parivartana Exchanges */}
                        {result.classical_rules.parivartana_exchanges?.map((pv, idx) => (
                          <div key={idx} className="bg-purple-50 rounded-xl p-3.5 border border-purple-300 flex items-start gap-3">
                            <RefreshCw className="w-4 h-4 text-purple-600 mt-0.5 shrink-0" />
                            <div className="text-xs text-purple-950">
                              <span className="font-extrabold text-purple-800">
                                {language === "ta" ? "பரிவர்த்தனை யோகம் (Sign Exchange): " : "Parivartana Yoga: "}
                              </span>
                              {language === "ta" ? pv.description_ta : pv.description_en}
                            </div>
                          </div>
                        ))}

                        {/* 8th Lord in Udayam */}
                        {result.classical_rules.eighth_lord_in_udayam?.is_in_udayam && (
                          <div className="bg-rose-50 rounded-xl p-3.5 border border-rose-300 flex items-start gap-3">
                            <AlertCircle className="w-4 h-4 text-rose-600 mt-0.5 shrink-0" />
                            <div className="text-xs text-rose-950">
                              <span className="font-extrabold text-rose-800">
                                {language === "ta" ? "8-ம் அதிபதி உதயம் தோஷம்: " : "8th Lord in Udayam Warning: "}
                              </span>
                              {language === "ta"
                                ? result.classical_rules.eighth_lord_in_udayam.warning_ta
                                : result.classical_rules.eighth_lord_in_udayam.warning_en}
                            </div>
                          </div>
                        )}

                        {/* Snake Approaching / In Udayam */}
                        {result.classical_rules.snake_udayam_analysis && (result.classical_rules.snake_udayam_analysis.snake_approaching || result.classical_rules.snake_udayam_analysis.snake_in_udayam) && (
                          <div className="bg-teal-50 rounded-xl p-3.5 border border-teal-300 flex items-start gap-3">
                            <Flame className="w-4 h-4 text-teal-700 mt-0.5 shrink-0" />
                            <div className="text-xs text-teal-950">
                              <span className="font-extrabold text-teal-800">
                                {language === "ta" ? "பாம்பு கிரகம் (ராகு) தாக்கம்: " : "Snake (Rahu) Influence: "}
                              </span>
                              {language === "ta"
                                ? result.classical_rules.snake_udayam_analysis.effect_ta
                                : result.classical_rules.snake_udayam_analysis.effect_en}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {/* 2.5 Domain Specific Rules Tab */}
                {activeTab === "domains" && (
                  <div className="space-y-6">
                    {/* Domain Category Filter Badges */}
                    <div className="flex flex-wrap gap-2 pb-2 border-b border-slate-200">
                      {[
                        { id: "all", name_en: "All Domains", name_ta: "அனைத்தும்", icon: Sparkles },
                        { id: "relationships", name_en: "Relationships", name_ta: "உறவுமுறை", icon: Users },
                        { id: "muhurta", name_en: "Muhurata Studio", name_ta: "சுப முகூர்த்தம்", icon: Calendar },
                        { id: "occult", name_en: "Evil Spirits & Black Magic", name_ta: "பில்லி சூனியம்", icon: Skull },
                        { id: "disaster", name_en: "Disaster & Death", name_ta: "பேரிடர் & ஆயுள்", icon: CloudLightning },
                        { id: "attributes", name_en: "Planet Attributes & Rays", name_ta: "கிரக கதிர்கள் & பண்பு", icon: Table },
                        { id: "politics", name_en: "Politics & Govt", name_ta: "அரசியல் & பதவி", icon: Landmark },
                        { id: "travel", name_en: "Foreign & Visa", name_ta: "வெளிநாடு & விசா", icon: Plane },
                        { id: "court", name_en: "Court Cases", name_ta: "நீதிமன்ற வழக்கு", icon: Scale },
                        { id: "loans", name_en: "Loans & Debt", name_ta: "கடன் & நிதி", icon: Banknote },
                        { id: "agri", name_en: "Agri & Borewell", name_ta: "விவசாயம் & போர்", icon: Sprout },
                        { id: "shares", name_en: "Share Market", name_ta: "பங்கு & கமாடிட்டி", icon: Coins },
                      ].map((item) => {
                        const IconComponent = item.icon;
                        const isSelected = domainFilter === item.id;
                        return (
                          <button
                            key={item.id}
                            onClick={() => setDomainFilter(item.id)}
                            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                              isSelected
                                ? "bg-[#153F6B] text-white shadow-xs"
                                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                            }`}
                          >
                            <IconComponent className="w-3.5 h-3.5" />
                            <span>{language === "ta" ? item.name_ta : item.name_en}</span>
                          </button>
                        );
                      })}
                    </div>

                    {/* Section 1: Relationships Prasanam */}
                    {(domainFilter === "all" || domainFilter === "relationships") && result.classical_rules.relationship_analysis && (
                      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-4">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
                          <div className="flex items-center gap-2">
                            <Users className="w-5 h-5 text-pink-600" />
                            <div>
                              <h3 className="font-extrabold text-slate-900 text-sm sm:text-base">
                                {language === "ta" ? "உறவுமுறை பிரசன்னம் (Relationship Analysis)" : "Classical Relationship Prasanam"}
                              </h3>
                              <p className="text-xs text-slate-500">
                                {language === "ta"
                                  ? "காரக கிரகம் உச்சம் + கவிப்பு தாக்கமின்மை = 100% உதவி; உச்சம் + கவிப்பு = வசதியிருந்தும் உதவ மாட்டார்; நீசம்/கவிப்பு = முடக்கம்."
                                  : "Exalted + free from Kavippu = 100% Help; Exalted with Kavippu = Has wealth but won't care; Debilitated/Kavippu = Obstruction."}
                              </p>
                            </div>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                          {Object.entries(result.classical_rules.relationship_analysis).map(([key, rel]) => (
                            <div
                              key={key}
                              className={`rounded-xl p-3 border text-xs flex flex-col justify-between ${
                                rel.verdict.includes("100% Yes")
                                  ? "bg-emerald-50/70 border-emerald-300"
                                  : rel.verdict.includes("Capable but Unwilling")
                                  ? "bg-amber-50/70 border-amber-300"
                                  : rel.verdict.includes("Unfavorable")
                                  ? "bg-rose-50/70 border-rose-300"
                                  : "bg-slate-50 border-slate-200"
                              }`}
                            >
                              <div>
                                <div className="flex justify-between items-start gap-1 mb-1">
                                  <span className="font-extrabold text-slate-900">
                                    {language === "ta" ? rel.title_ta : rel.title_en}
                                  </span>
                                  <span className="text-[10px] font-semibold text-slate-500">
                                    {rel.planet} ({rel.karak_bhava}th Bhava)
                                  </span>
                                </div>
                                <div
                                  className={`inline-block px-2 py-0.5 rounded text-[10px] font-extrabold uppercase mb-2 ${
                                    rel.verdict.includes("100% Yes")
                                      ? "bg-emerald-200 text-emerald-950"
                                      : rel.verdict.includes("Capable but Unwilling")
                                      ? "bg-amber-200 text-amber-950"
                                      : rel.verdict.includes("Unfavorable")
                                      ? "bg-rose-200 text-rose-950"
                                      : "bg-slate-200 text-slate-800"
                                  }`}
                                >
                                  {language === "ta" ? rel.verdict_ta : rel.verdict}
                                </div>
                              </div>
                              <p className="text-[11px] text-slate-600 mt-1">
                                {language === "ta" ? rel.description_ta : rel.description_en}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Section 2: Politics & Government Posts */}
                    {(domainFilter === "all" || domainFilter === "politics") && result.classical_rules.politics_govt_analysis && (
                      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-4">
                        <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
                          <Landmark className="w-5 h-5 text-indigo-600" />
                          <div>
                            <h3 className="font-extrabold text-slate-900 text-sm sm:text-base">
                              {language === "ta" ? "அரசியல் & அரசு பதவி பிரசன்னம்" : "Politics & Government Appointments"}
                            </h3>
                            <p className="text-xs text-slate-500">
                              {language === "ta"
                                ? "5-ம் பாவம் அரசியல் காரக பாவம் (கவிப்பு இருந்தால் இல்லை); குரு அரசியல் அனுமதி சீட்டு (நீசமாயின் அனுமதி மறுப்பு)."
                                : "5th House is Politics Karaka (Kavippu = No); Jupiter is politics entry ticket (Debilitated = No ticket)."}
                            </p>
                          </div>
                        </div>

                        {/* Top Key Pillars in Politics */}
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                          <div className={`p-3 rounded-xl border text-xs ${result.classical_rules.politics_govt_analysis.kavippu_in_5th_house ? "bg-rose-50 border-rose-200 text-rose-950" : "bg-emerald-50 border-emerald-200 text-emerald-950"}`}>
                            <div className="text-[10px] uppercase font-bold text-slate-500 mb-0.5">5th House Karaka</div>
                            <div className="font-bold">{result.classical_rules.politics_govt_analysis.kavippu_in_5th_house ? "Afflicted by Kavippu (No)" : "Clean & Favorable"}</div>
                          </div>
                          <div className={`p-3 rounded-xl border text-xs ${result.classical_rules.politics_govt_analysis.central_govt_ticket_eligible ? "bg-emerald-50 border-emerald-200 text-emerald-950" : "bg-rose-50 border-rose-200 text-rose-950"}`}>
                            <div className="text-[10px] uppercase font-bold text-slate-500 mb-0.5">Central Entry Ticket</div>
                            <div className="font-bold">{result.classical_rules.politics_govt_analysis.central_govt_ticket_eligible ? "Approved (Jupiter Strong)" : "Denied (Jupiter Weak)"}</div>
                          </div>
                          <div className={`p-3 rounded-xl border text-xs ${result.classical_rules.politics_govt_analysis.powerful_post_eligible ? "bg-emerald-50 border-emerald-200 text-emerald-950" : "bg-amber-50 border-amber-200 text-amber-950"}`}>
                            <div className="text-[10px] uppercase font-bold text-slate-500 mb-0.5">High Power Role</div>
                            <div className="font-bold">{result.classical_rules.politics_govt_analysis.powerful_post_eligible ? "Eligible (UD/Sun Exalted)" : "Moderate Prospects"}</div>
                          </div>
                          <div className={`p-3 rounded-xl border text-xs ${result.classical_rules.politics_govt_analysis.panchayat_election_favorable ? "bg-emerald-50 border-emerald-200 text-emerald-950" : "bg-slate-50 border-slate-200 text-slate-800"}`}>
                            <div className="text-[10px] uppercase font-bold text-slate-500 mb-0.5">Local / Panchayat</div>
                            <div className="font-bold">{result.classical_rules.politics_govt_analysis.panchayat_election_favorable ? "Victory (Saturn Exalted)" : "Challenging"}</div>
                          </div>
                        </div>

                        {/* Posts Breakdown Grid */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
                          {Object.entries(result.classical_rules.politics_govt_analysis.posts_breakdown).map(([k, p]) => (
                            <div key={k} className="p-2.5 rounded-lg border border-slate-200 bg-slate-50/60 flex justify-between items-center text-xs">
                              <div>
                                <div className="font-bold text-slate-900">{language === "ta" ? p.post_ta : p.post_en}</div>
                                <div className="text-[10px] text-slate-500">{language === "ta" ? p.reasons_ta : p.reasons_en}</div>
                              </div>
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${p.status === "Favorable" ? "bg-emerald-100 text-emerald-800" : "bg-rose-100 text-rose-800"}`}>
                                {language === "ta" ? p.status_ta : p.status}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Section 3: Foreign Travel & Citizenship */}
                    {(domainFilter === "all" || domainFilter === "travel") && result.classical_rules.foreign_travel_analysis && (
                      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-4">
                        <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
                          <Plane className="w-5 h-5 text-sky-600" />
                          <div>
                            <h3 className="font-extrabold text-slate-900 text-sm sm:text-base">
                              {language === "ta" ? "வெளிநாட்டுப் பயணம், குடியுரிமை & விசா" : "Foreign Travel, Visa & Citizenship"}
                            </h3>
                            <p className="text-xs text-slate-500">
                              {language === "ta"
                                ? "பாம்பு (ராகு) உதயத்தை அணுகினால் 100% பயணம்; உதயாதிபதி உச்சம் ஆயின் பயணம் உண்டு; 9/11/12-ல் கவிப்பு வரக்கூடாது."
                                : "Snake approaching Udayam = 100% Travel; Udayam Lord exalted = Travel confirmed; 9/11/12 must be free from Kavippu."}
                            </p>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className={`p-4 rounded-xl border ${result.classical_rules.foreign_travel_analysis.can_travel ? "bg-sky-50 border-sky-300 text-sky-950" : "bg-rose-50 border-rose-300 text-rose-950"}`}>
                            <div className="text-xs uppercase font-extrabold tracking-wider mb-1">
                              {language === "ta" ? "பயண வாய்ப்பு தீர்ப்பு" : "Travel Prospects"}
                            </div>
                            <div className="text-sm font-bold">
                              {language === "ta" ? result.classical_rules.foreign_travel_analysis.verdict_ta : result.classical_rules.foreign_travel_analysis.verdict_en}
                            </div>
                            <div className="text-xs text-slate-600 mt-2">
                              <span className="font-bold">{language === "ta" ? "பயண நோக்கம் (ஆருட நிலை): " : "Purpose of Travel: "}</span>
                              {language === "ta" ? result.classical_rules.foreign_travel_analysis.travel_purpose_ta : result.classical_rules.foreign_travel_analysis.travel_purpose_en}
                            </div>
                          </div>

                          <div className={`p-4 rounded-xl border ${result.classical_rules.foreign_travel_analysis.citizenship_green_card_favorable ? "bg-emerald-50 border-emerald-300 text-emerald-950" : "bg-amber-50 border-amber-300 text-amber-950"}`}>
                            <div className="text-xs uppercase font-extrabold tracking-wider mb-1">
                              {language === "ta" ? "கிரீன் கார்டு / நிரந்தர குடியுரிமை" : "Green Card & Citizenship"}
                            </div>
                            <div className="text-sm font-bold">
                              {result.classical_rules.foreign_travel_analysis.citizenship_green_card_favorable
                                ? (language === "ta" ? "குடியுரிமை / விசா ஒப்புதல் சாதகமாக அமையும் (9 & 12 பலம்)" : "Citizenship / Green Card Favorable (9th & 12th lords pure)")
                                : (language === "ta" ? "தாயகம் திரும்ப வேண்டிய நிலை / விசா சிக்கல் (9 அல்லது 12-ல் கவிப்பு)" : "Has to return back / Visa delays (Kavippu in 9th/12th houses)")}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Section 4: Court Cases & Litigation */}
                    {(domainFilter === "all" || domainFilter === "court") && result.classical_rules.court_case_analysis && (
                      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-4">
                        <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
                          <Scale className="w-5 h-5 text-amber-700" />
                          <div>
                            <h3 className="font-extrabold text-slate-900 text-sm sm:text-base">
                              {language === "ta" ? "நீதிமன்ற வழக்கு & பஞ்சாயத்து பிரசன்னம்" : "Court Cases, Disputes & Settlement"}
                            </h3>
                            <p className="text-xs text-slate-500">
                              {language === "ta"
                                ? "7-ல் கவிப்பு அல்லது 7-ம் அதிபதியுடன் கவிப்பு = எதிரி தோல்வி, கேள்வியாளருக்கு வெற்றி! 11-ல் கவிப்பு = தோல்வி; உதயாதிபதி 3/11-ல் உச்சம் = உறுதியான வெற்றி."
                                : "Kavippu in 7th / with 7th Lord = Opponent defeated, Querent WINS! Kavippu in 11th = Defeat; UD lord in 3/11 exalted = Sure Victory."}
                            </p>
                          </div>
                        </div>

                        <div className="p-4 rounded-xl border bg-amber-50/50 border-amber-300">
                          <div className="text-sm font-extrabold text-slate-900">
                            {language === "ta" ? result.classical_rules.court_case_analysis.verdict_ta : result.classical_rules.court_case_analysis.verdict_en}
                          </div>
                        </div>

                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
                          <div className="p-2.5 rounded-lg border border-slate-200 bg-slate-50">
                            <span className="text-[10px] text-slate-500 font-bold block">7th Bhava / Opponent</span>
                            <span className="font-bold">{result.classical_rules.court_case_analysis.kavippu_in_7th_house || result.classical_rules.court_case_analysis.seventh_lord_has_kavippu ? "Afflicted by Kavippu (You Win!)" : "Opponent Active"}</span>
                          </div>
                          <div className="p-2.5 rounded-lg border border-slate-200 bg-slate-50">
                            <span className="text-[10px] text-slate-500 font-bold block">11th Bhava / Victory</span>
                            <span className="font-bold">{result.classical_rules.court_case_analysis.kavippu_in_11th_house ? "Kavippu Blocks Win" : "Clear Path"}</span>
                          </div>
                          <div className="p-2.5 rounded-lg border border-slate-200 bg-slate-50">
                            <span className="text-[10px] text-slate-500 font-bold block">Arguments / Mercury</span>
                            <span className="font-bold">{result.classical_rules.court_case_analysis.mercury_debilitated ? "Debilitated (Weak arguments)" : "Sharp arguments"}</span>
                          </div>
                          <div className="p-2.5 rounded-lg border border-slate-200 bg-slate-50">
                            <span className="text-[10px] text-slate-500 font-bold block">Resolution Mode</span>
                            <span className="font-bold">
                              {result.classical_rules.court_case_analysis.moon_in_udayam_fast_verdict ? "Fast Verdict (Moon)" :
                               result.classical_rules.court_case_analysis.venus_in_udayam_money_victory ? "Money Power (Venus)" :
                               result.classical_rules.court_case_analysis.jupiter_in_udayam_settlement ? "Lok Adalat Mediation (Jupiter)" :
                               result.classical_rules.court_case_analysis.snake_in_udayam_crisis ? "High Tension / Crisis" : "Standard Legal Battle"}
                            </span>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Section 5: Loans & Financial Debt */}
                    {(domainFilter === "all" || domainFilter === "loans") && result.classical_rules.loans_analysis && (
                      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-4">
                        <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
                          <Banknote className="w-5 h-5 text-emerald-600" />
                          <div>
                            <h3 className="font-extrabold text-slate-900 text-sm sm:text-base">
                              {language === "ta" ? "கடன், வங்கி நிதி & காசோலை ஒப்புதல்" : "Loans, Bank Sanctions & Debt Approvals"}
                            </h3>
                            <p className="text-xs text-slate-500">
                              {language === "ta"
                                ? "6-ம் பாவம் கடன் காரகம் (நீசம்/கவிப்பு இருந்தால் கடன் கிடைக்காது); உதயாதிபதி அல்லது குரு உச்சம் பெற்றால் கடன் உடனே ஒப்புதல்."
                                : "6th House is Loan Karaka (Kavippu/Debilitation = No loan); UD Lord or Jupiter exalted = Fast Loan Approval."}
                            </p>
                          </div>
                        </div>

                        <div className={`p-4 rounded-xl border ${result.classical_rules.loans_analysis.loan_approved ? "bg-emerald-50 border-emerald-300 text-emerald-950" : "bg-rose-50 border-rose-300 text-rose-950"}`}>
                          <div className="text-sm font-bold">
                            {language === "ta" ? result.classical_rules.loans_analysis.verdict_ta : result.classical_rules.loans_analysis.verdict_en}
                          </div>
                          {result.classical_rules.loans_analysis.scale_indicators_en.length > 0 && (
                            <ul className="mt-2 list-disc list-inside text-xs space-y-0.5 text-slate-700">
                              {(language === "ta" ? result.classical_rules.loans_analysis.scale_indicators_ta : result.classical_rules.loans_analysis.scale_indicators_en).map((s, idx) => (
                                <li key={idx}>{s}</li>
                              ))}
                            </ul>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Section 6: Agriculture, Rain & Borewell */}
                    {(domainFilter === "all" || domainFilter === "agri") && result.classical_rules.agriculture_borewell_rain_analysis && (
                      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-4">
                        <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
                          <Sprout className="w-5 h-5 text-green-600" />
                          <div>
                            <h3 className="font-extrabold text-slate-900 text-sm sm:text-base">
                              {language === "ta" ? "விவசாயம், மழை & போர்வெல் தண்ணீர் கணிப்பு" : "Agriculture, Rain & Borewell Water Discovery"}
                            </h3>
                            <p className="text-xs text-slate-500">
                              {language === "ta"
                                ? "உதயத்தை அணுகும் கிரகம் பயிரை குறிக்கும்; 4/11-ல் அல்லது சந்திரன்/சுக்கிரனுடன் கவிப்பு இருந்தால் தண்ணீர் இல்லை."
                                : "Approaching planet denotes crop type; Kavippu in 4/11 or with Moon/Venus = Dry borewell."}
                            </p>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                          {/* Crop */}
                          <div className="p-3 rounded-xl border border-green-200 bg-green-50/70">
                            <div className="font-bold text-green-900 uppercase text-[10px] mb-1">Crop Forecast</div>
                            <div className="font-semibold text-slate-800">
                              {language === "ta" ? result.classical_rules.agriculture_borewell_rain_analysis.crop_indicated_ta : result.classical_rules.agriculture_borewell_rain_analysis.crop_indicated_en}
                            </div>
                          </div>

                          {/* Rain */}
                          <div className={`p-3 rounded-xl border ${result.classical_rules.agriculture_borewell_rain_analysis.rain_expected ? "bg-sky-50 border-sky-200 text-sky-950" : "bg-slate-50 border-slate-200 text-slate-800"}`}>
                            <div className="font-bold text-[10px] uppercase mb-1 flex items-center gap-1">
                              <Droplets className="w-3.5 h-3.5 text-sky-600" />
                              Rain Forecast
                            </div>
                            <div className="font-semibold">
                              {language === "ta" ? result.classical_rules.agriculture_borewell_rain_analysis.rain_verdict_ta : result.classical_rules.agriculture_borewell_rain_analysis.rain_verdict_en}
                            </div>
                          </div>

                          {/* Borewell */}
                          <div className={`p-3 rounded-xl border ${result.classical_rules.agriculture_borewell_rain_analysis.borewell_water_available ? "bg-teal-50 border-teal-200 text-teal-950" : "bg-rose-50 border-rose-200 text-rose-950"}`}>
                            <div className="font-bold text-[10px] uppercase mb-1">Borewell Water & Depth</div>
                            <div className="font-semibold">
                              {language === "ta" ? result.classical_rules.agriculture_borewell_rain_analysis.water_depth_ta : result.classical_rules.agriculture_borewell_rain_analysis.water_depth_en}
                            </div>
                            <div className="text-[10px] text-teal-800 mt-1 font-bold">
                              {language === "ta" ? result.classical_rules.agriculture_borewell_rain_analysis.water_direction_ta : result.classical_rules.agriculture_borewell_rain_analysis.water_direction_en}
                            </div>
                          </div>
                        </div>

                        {result.classical_rules.agriculture_borewell_rain_analysis.borewell_drilling_bit_warning && (
                          <div className="p-3 rounded-xl bg-rose-50 border border-rose-300 text-xs font-bold text-rose-900 flex items-center gap-2">
                            <AlertTriangle className="w-4 h-4 text-rose-600" />
                            <span>
                              {language === "ta"
                                ? "எச்சரிக்கை: பாம்பு கவிப்புடன் உள்ளதால் போர்வெல் ட்ரில்லிங் பிட் (Drilling bit) உடையும் அபாயம் உள்ளது!"
                                : "Warning: Snake conjunct Kavippu indicates danger of drilling bit breakage / obstruction!"}
                            </span>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Section 7: Share Market & Commodities */}
                    {(domainFilter === "all" || domainFilter === "shares") && result.classical_rules.share_market_analysis && (
                      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-4">
                        <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
                          <Coins className="w-5 h-5 text-amber-600" />
                          <div>
                            <h3 className="font-extrabold text-slate-900 text-sm sm:text-base">
                              {language === "ta" ? "பங்குச்சந்தை & 7 வகை பொருட்கள் விலை நகர்வு" : "Share Market & Commodity Trends"}
                            </h3>
                            <p className="text-xs text-slate-500">
                              {language === "ta"
                                ? "5-ம் பாவத்தில் கவிப்பு = பங்கு வாங்கக்கூடாது; கிரக உச்சம் = விலை உயரும் (Bullish); நீசம்/கவிப்பு = விலை இறங்கும் (Bearish)."
                                : "Kavippu in 5th = Do NOT buy shares; Exalted = Price rises (Bullish); Debilitated/Kavippu = Price falls (Bearish)."}
                            </p>
                          </div>
                        </div>

                        <div className={`p-4 rounded-xl border ${result.classical_rules.share_market_analysis.can_buy_shares ? "bg-emerald-50 border-emerald-300 text-emerald-950" : "bg-rose-50 border-rose-300 text-rose-950"}`}>
                          <div className="text-sm font-bold">
                            {language === "ta" ? result.classical_rules.share_market_analysis.verdict_ta : result.classical_rules.share_market_analysis.verdict_en}
                          </div>
                        </div>

                        {/* Commodities Breakdown Grid */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
                          {Object.entries(result.classical_rules.share_market_analysis.commodities).map(([k, c]) => (
                            <div key={k} className="p-3 rounded-xl border border-slate-200 bg-slate-50/70 flex justify-between items-center text-xs">
                              <div>
                                <div className="font-bold text-slate-900">{language === "ta" ? c.commodity_ta : c.commodity_en}</div>
                                <div className="text-[10px] text-slate-500">{c.planet} Karaka</div>
                              </div>
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                c.trend_type === "bullish" ? "bg-emerald-100 text-emerald-800" :
                                c.trend_type === "bearish" ? "bg-rose-100 text-rose-800" : "bg-slate-100 text-slate-700"
                              }`}>
                                {c.trend}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Section 8: Muhurata Studio & Approaching Hour Guidance */}
                    {(domainFilter === "all" || domainFilter === "muhurta") && result.classical_rules.muhurta_analysis && (
                      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-5">
                        <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
                          <Calendar className="w-5 h-5 text-indigo-600" />
                          <div>
                            <h3 className="font-extrabold text-slate-900 text-sm sm:text-base">
                              {language === "ta" ? "ஜாமக்கோள் முகூர்த்த ஆய்வு & மணிநேர வழிகாட்டி" : "Jamakkol Muhurata Studio & Hourly Guidance"}
                            </h3>
                            <p className="text-xs text-slate-500">
                              {language === "ta"
                                ? "உதயம் (ஆண்), ஆருடம் (பெண்); 7-ம் பாவகங்கள் சுபமாக இருக்க வேண்டும்; உதயத்தை நெருங்கும் கோள்கள் காட்டும் சுப காரியங்கள்."
                                : "Udayam is Groom (Male), Arudam is Bride (Female); 7th houses must be pure; Auspicious actions for approaching planet."}
                            </p>
                          </div>
                        </div>

                        {/* Current Approaching Planet Signification Banner */}
                        {result.classical_rules.muhurta_analysis.current_approaching_signification && (
                          <div className="p-4 rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 text-xs">
                            <div className="flex items-center gap-2 font-extrabold text-blue-900 text-sm mb-1">
                              <Sparkles className="w-4 h-4 text-blue-600" />
                              <span>
                                {language === "ta"
                                  ? `உதயத்தை நெருங்கும் கிரகம்: ${result.classical_rules.muhurta_analysis.current_approaching_signification.planet} (இந்த மணிநேரத்திற்கு உகந்த காரியங்கள்)`
                                  : `Planet Approaching Udayam: ${result.classical_rules.muhurta_analysis.current_approaching_signification.planet} (Favorable Actions for This Hour)`}
                              </span>
                            </div>
                            <p className="text-slate-700 leading-relaxed font-medium">
                              {language === "ta"
                                ? result.classical_rules.muhurta_analysis.current_approaching_signification.advice_ta
                                : result.classical_rules.muhurta_analysis.current_approaching_signification.advice_en}
                            </p>
                            <div className="flex flex-wrap gap-1.5 mt-2">
                              {result.classical_rules.muhurta_analysis.current_approaching_signification.auspicious_activities.map((act, idx) => (
                                <span key={idx} className="px-2 py-0.5 rounded bg-blue-200/60 text-blue-950 font-bold text-[10px]">
                                  ✓ {act}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Marriage Muhurta & Couple Reunion */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {/* Marriage Muhurta */}
                          <div className={`p-4 rounded-xl border ${result.classical_rules.muhurta_analysis.marriage_muhurta.is_auspicious ? "bg-emerald-50 border-emerald-300 text-emerald-950" : "bg-rose-50 border-rose-300 text-rose-950"}`}>
                            <div className="text-xs font-bold uppercase tracking-wider mb-1 flex items-center justify-between">
                              <span>{language === "ta" ? "திருமண முகூர்த்த தகுதி" : "Marriage Muhurta Status"}</span>
                              <span className="text-[10px] px-2 py-0.5 rounded font-extrabold bg-white/70">
                                {result.classical_rules.muhurta_analysis.marriage_muhurta.is_auspicious ? "AUSPICIOUS" : "INAUSPICIOUS"}
                              </span>
                            </div>
                            <div className="text-xs font-bold mt-1">
                              {language === "ta" ? result.classical_rules.muhurta_analysis.marriage_muhurta.verdict_ta : result.classical_rules.muhurta_analysis.marriage_muhurta.verdict_en}
                            </div>
                            <div className="mt-2 text-[11px] text-slate-600 space-y-0.5">
                              <div>• Groom (Udayam): {result.classical_rules.muhurta_analysis.marriage_muhurta.udayam_groom_sign}</div>
                              <div>• Bride (Arudam): {result.classical_rules.muhurta_analysis.marriage_muhurta.arudam_bride_sign} (House {result.classical_rules.muhurta_analysis.marriage_muhurta.u_a_distance})</div>
                              <div>• Lords Debilitated: {result.classical_rules.muhurta_analysis.marriage_muhurta.lords_debilitated ? "Yes (Blemish)" : "No (Pure)"}</div>
                              <div>• 7th Houses Afflicted by Kavippu: {result.classical_rules.muhurta_analysis.marriage_muhurta.sevenths_afflicted ? "Yes (Avoid)" : "No (Protected)"}</div>
                            </div>
                          </div>

                          {/* Couple Reunion after Separation */}
                          <div className={`p-4 rounded-xl border ${result.classical_rules.muhurta_analysis.couple_reunion.is_golden_hour ? "bg-amber-50 border-amber-300 text-amber-950" : "bg-slate-50 border-slate-200 text-slate-800"}`}>
                            <div className="text-xs font-bold uppercase tracking-wider mb-1 flex items-center gap-1.5 text-pink-700">
                              <Heart className="w-4 h-4 fill-pink-600 text-pink-600" />
                              <span>{language === "ta" ? "பிரிந்த தம்பதியர் மீண்டும் சேர்தல்" : "Couple Reunion After Separation"}</span>
                            </div>
                            {result.classical_rules.muhurta_analysis.couple_reunion.is_golden_hour && (
                              <div className="text-xs font-extrabold text-amber-800 mb-1">
                                ★ {language === "ta" ? "ரிஷப/துலாம் உதயம் & சுக்கிரன் உச்சம்: சமரசம் பேச பொன்னான நேரம்!" : "Taurus/Libra Udayam & Venus Exalted: Golden Hour to negotiate reconciliation!"}
                              </div>
                            )}
                            <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                              {language === "ta"
                                ? result.classical_rules.muhurta_analysis.couple_reunion.mediator_advice_ta
                                : result.classical_rules.muhurta_analysis.couple_reunion.mediator_advice_en}
                            </p>
                          </div>
                        </div>

                        {/* Quick Action Muhurta Cards */}
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
                          <div className={`p-2.5 rounded-lg border ${result.classical_rules.muhurta_analysis.business_startup_muhurta.is_auspicious ? "bg-emerald-50 border-emerald-200 text-emerald-950" : "bg-slate-50 border-slate-200 text-slate-700"}`}>
                            <span className="font-extrabold block text-[10px] uppercase text-slate-500">Business Launch</span>
                            <span className="font-bold">{result.classical_rules.muhurta_analysis.business_startup_muhurta.is_auspicious ? "Favorable" : "Postpone"}</span>
                          </div>
                          <div className={`p-2.5 rounded-lg border ${result.classical_rules.muhurta_analysis.construction_muhurta.is_auspicious ? "bg-emerald-50 border-emerald-200 text-emerald-950" : "bg-slate-50 border-slate-200 text-slate-700"}`}>
                            <span className="font-extrabold block text-[10px] uppercase text-slate-500">New Construction</span>
                            <span className="font-bold">{result.classical_rules.muhurta_analysis.construction_muhurta.is_auspicious ? "Favorable" : "Inauspicious"}</span>
                          </div>
                          <div className={`p-2.5 rounded-lg border ${result.classical_rules.muhurta_analysis.documentation_call_muhurta.is_auspicious ? "bg-emerald-50 border-emerald-200 text-emerald-950" : "bg-rose-50 border-rose-200 text-rose-950"}`}>
                            <span className="font-extrabold block text-[10px] uppercase text-slate-500">Agreements & Calls</span>
                            <span className="font-bold">{result.classical_rules.muhurta_analysis.documentation_call_muhurta.is_auspicious ? "Success" : "Failure Risk"}</span>
                          </div>
                          <div className={`p-2.5 rounded-lg border ${result.classical_rules.muhurta_analysis.loan_application_muhurta.is_auspicious ? "bg-emerald-50 border-emerald-200 text-emerald-950" : "bg-slate-50 border-slate-200 text-slate-700"}`}>
                            <span className="font-extrabold block text-[10px] uppercase text-slate-500">Apply for Loan</span>
                            <span className="font-bold">{result.classical_rules.muhurta_analysis.loan_application_muhurta.is_auspicious ? "Apply Now" : "Do Not Apply"}</span>
                          </div>
                        </div>

                        {/* Travel Delay Warning */}
                        {result.classical_rules.muhurta_analysis.travel_muhurta.saturn_approaching_delay && (
                          <div className="p-3 rounded-xl bg-amber-50 border border-amber-300 text-xs text-amber-950 flex items-center gap-2">
                            <Clock className="w-4 h-4 text-amber-700 shrink-0" />
                            <span>
                              {language === "ta"
                                ? result.classical_rules.muhurta_analysis.travel_muhurta.verdict_ta
                                : result.classical_rules.muhurta_analysis.travel_muhurta.verdict_en}
                            </span>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Section 9: Evil Spirits, Black Magic & Haunted Residence */}
                    {(domainFilter === "all" || domainFilter === "occult") && result.classical_rules.evil_spirits_black_magic_analysis && (
                      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-4">
                        <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
                          <Skull className="w-5 h-5 text-rose-600" />
                          <div>
                            <h3 className="font-extrabold text-slate-900 text-sm sm:text-base">
                              {language === "ta" ? "பில்லி, சூனியம் & துஷ்ட சக்தி பிரசன்னம்" : "Prasanam for Evil Spirits & Black Magic"}
                            </h3>
                            <p className="text-xs text-slate-500">
                              {language === "ta"
                                ? "உதயாதிபதி மாந்தியுடன் இருந்தால் துஷ்ட சக்தி தாக்கம்; மாந்தியுடன் உள்ள கிரகத்தின் ஜீவ காரகருக்கு செய்வினை; பாம்பு உதயத்தை அணுகினால் பில்லி உண்டு."
                                : "UD Lord with Mandi = Under evil spirits; Planet with Mandi = Black magic on that Jeeva Karaka; Snake approaching = Yes."}
                            </p>
                          </div>
                        </div>

                        {/* Immunity Banner or Warning */}
                        <div className={`p-4 rounded-xl border ${result.classical_rules.evil_spirits_black_magic_analysis.black_magic_cannot_harm_querent ? "bg-emerald-50 border-emerald-300 text-emerald-950" : (result.classical_rules.evil_spirits_black_magic_analysis.black_magic_present || result.classical_rules.evil_spirits_black_magic_analysis.querent_under_evil_spirits ? "bg-rose-50 border-rose-300 text-rose-950" : "bg-slate-50 border-slate-200 text-slate-800")}`}>
                          <div className="text-xs uppercase font-extrabold tracking-wider mb-1 flex items-center gap-2">
                            <Shield className="w-4 h-4 text-emerald-600" />
                            <span>{language === "ta" ? "மாந்திரீக தற்காப்பு & பாதுகாப்பு நிலை" : "Protection & Immunity Verdict"}</span>
                          </div>
                          <div className="text-sm font-bold">
                            {language === "ta" ? result.classical_rules.evil_spirits_black_magic_analysis.summary_ta : result.classical_rules.evil_spirits_black_magic_analysis.summary_en}
                          </div>
                        </div>

                        {/* Perpetrator & Haunted Residence */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                          {/* Perpetrator Identity */}
                          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50">
                            <div className="text-[10px] uppercase font-bold text-slate-500 mb-1">
                              {language === "ta" ? "செய்வினை செய்தவரின் அடையாளம் (கவிப்பு நின்ற கிரகம்)" : "Perpetrator Profile (Planet with Kavippu)"}
                            </div>
                            <div className="font-extrabold text-slate-900 text-sm">
                              {result.classical_rules.evil_spirits_black_magic_analysis.perpetrator_profile.planet} Karaka
                            </div>
                            <p className="text-slate-600 mt-1">
                              {language === "ta"
                                ? result.classical_rules.evil_spirits_black_magic_analysis.perpetrator_profile.description_ta
                                : result.classical_rules.evil_spirits_black_magic_analysis.perpetrator_profile.description_en}
                            </p>
                          </div>

                          {/* Haunted Residence Check */}
                          <div className={`p-4 rounded-xl border ${result.classical_rules.evil_spirits_black_magic_analysis.haunted_residence_mandi_in_4th ? "bg-rose-50 border-rose-300 text-rose-950" : "bg-slate-50 border-slate-200 text-slate-800"}`}>
                            <div className="text-[10px] uppercase font-bold text-slate-500 mb-1">
                              {language === "ta" ? "வீட்டு வாசஸ்தலம் (மாந்தி 4-ம் பாவம்)" : "Living Residence (Mandi in 4th Bhava)"}
                            </div>
                            <div className="font-bold text-sm">
                              {result.classical_rules.evil_spirits_black_magic_analysis.haunted_residence_mandi_in_4th
                                ? (language === "ta" ? "வீட்டில் அமானுஷ்ய சக்தி / வாஸ்து தோஷம் உண்டு (Mandi in 4th)" : "The house querent is living in is haunted / afflicted by negative spirits!")
                                : (language === "ta" ? "வாசஸ்தலம் சுத்தமாக உள்ளது (மாந்தி 4-ல் இல்லை)" : "Residence is clear of subterranean spirit affliction.")}
                            </div>
                          </div>
                        </div>

                        {/* Afflicted Jeeva Karakas (Planets with Mandi) */}
                        {result.classical_rules.evil_spirits_black_magic_analysis.afflicted_jeeva_karakas.length > 0 && (
                          <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-xs">
                            <div className="font-extrabold text-amber-900 mb-1">
                              {language === "ta" ? "மாந்தியுடன் இணைந்து பாதிக்கப்பட்ட ஜீவ காரக உறவினர்கள்:" : "Jeeva Karakas Influenced by Mandi / Black Magic:"}
                            </div>
                            <div className="flex flex-wrap gap-2 mt-1">
                              {result.classical_rules.evil_spirits_black_magic_analysis.afflicted_jeeva_karakas.map((j, idx) => (
                                <span key={idx} className="px-2.5 py-1 rounded-md bg-white border border-amber-300 text-amber-950 font-bold">
                                  {j.planet}: {language === "ta" ? j.person_ta : j.person_en}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Section 10: Natural vs Unnatural Death & Disaster */}
                    {(domainFilter === "all" || domainFilter === "disaster") && (
                      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-4">
                        <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
                          <CloudLightning className="w-5 h-5 text-amber-600" />
                          <div>
                            <h3 className="font-extrabold text-slate-900 text-sm sm:text-base">
                              {language === "ta" ? "இயற்கை பேரிடர், புயல் பாதுகாப்பு & ஆயுள் முடிவு" : "Natural Disaster, Cyclone Shield & Longevity Transition"}
                            </h3>
                            <p className="text-xs text-slate-500">
                              {language === "ta"
                                ? "சனி உதயம் அணுகுதல் / 3-ல் சனி / உதயாதிபதி நீசம் = புயல் பாதிப்பில்லை; குரு பார்வை = இயற்கை மரணம்; மாந்தி = துர்மரணம்."
                                : "Saturn approaching / in 3rd / UD lord debilitated = Cyclone protection; Jupiter = Natural death; Mandi = Unnatural death."}
                            </p>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {/* Cyclone Protection */}
                          {result.classical_rules.rain_disaster_catastrophe_analysis && (
                            <div className={`p-4 rounded-xl border ${result.classical_rules.rain_disaster_catastrophe_analysis.cyclone_protection_active ? "bg-teal-50 border-teal-300 text-teal-950" : "bg-slate-50 border-slate-200 text-slate-800"}`}>
                              <div className="text-xs font-bold uppercase tracking-wider mb-1 text-teal-800 flex items-center gap-1.5">
                                <ShieldCheck className="w-4 h-4 text-teal-600" />
                                <span>{language === "ta" ? "புயல் பாதுகாப்பு விதி (Cyclone Protection)" : "Cyclone Protection Shastra Rule"}</span>
                              </div>
                              <div className="text-xs font-semibold leading-relaxed mt-1">
                                {language === "ta" ? result.classical_rules.rain_disaster_catastrophe_analysis.cyclone_verdict_ta : result.classical_rules.rain_disaster_catastrophe_analysis.cyclone_verdict_en}
                              </div>
                            </div>
                          )}

                          {/* Natural vs Unnatural Death */}
                          {result.classical_rules.natural_unnatural_death_analysis && (
                            <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 text-xs">
                              <div className="text-[10px] uppercase font-bold text-slate-500 mb-1">
                                {language === "ta" ? "இயற்கை மரணம் vs துர்மரணம் (குரு vs மாந்தி)" : "Nature of Death (Jupiter vs Mandi Influence)"}
                              </div>
                              <div className="font-extrabold text-slate-900 text-sm">
                                {language === "ta" ? result.classical_rules.natural_unnatural_death_analysis.death_nature_ta : result.classical_rules.natural_unnatural_death_analysis.death_nature}
                              </div>
                              <div className="mt-2 text-slate-600 text-[11px] space-y-0.5">
                                <div>• Jupiter Influence on Udayam: {result.classical_rules.natural_unnatural_death_analysis.jupiter_influences_udayam ? "Yes (Auspicious Grace)" : "No"}</div>
                                <div>• Mandi Influence on Udayam: {result.classical_rules.natural_unnatural_death_analysis.mandi_influences_udayam ? "Yes (Trauma / Shock Indicator)" : "No"}</div>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Section 11: Planet Attributes, Rays & Places Matrix */}
                    {(domainFilter === "all" || domainFilter === "attributes") && result.classical_rules.planet_attributes_table && (
                      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-4">
                        <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
                          <Table className="w-5 h-5 text-blue-600" />
                          <div>
                            <h3 className="font-extrabold text-slate-900 text-sm sm:text-base">
                              {language === "ta" ? "கிரகங்களின் கதிர்கள், வயது, உயரம், இடங்கள் & திசைகள்" : "Planetary Attributes: Rays, Age, Height, Places & Directions"}
                            </h3>
                            <p className="text-xs text-slate-500">
                              {language === "ta"
                                ? "சூரியன் முதல் பாம்பு வரை பாரம்பரிய சாஸ்திரத்தில் வரையறுக்கப்பட்ட கதிர்கள், தோற்றம் மற்றும் வாழிட அமைப்புகள்."
                                : "Canonical Jamakkol table of planetary rays, age categories, stature, places, and spatial bearings."}
                            </p>
                          </div>
                        </div>

                        <div className="overflow-x-auto">
                          <table className="w-full text-left text-xs border-collapse">
                            <thead>
                              <tr className="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                                <th className="py-2.5 px-3">{language === "ta" ? "கிரகம்" : "Planet"}</th>
                                <th className="py-2.5 px-3">{language === "ta" ? "திசை (Direction)" : "Direction"}</th>
                                <th className="py-2.5 px-3">{language === "ta" ? "கதிர்கள் (Rays)" : "Rays"}</th>
                                <th className="py-2.5 px-3">{language === "ta" ? "வயது (Age)" : "Age"}</th>
                                <th className="py-2.5 px-3">{language === "ta" ? "உயரம் (Height)" : "Height"}</th>
                                <th className="py-2.5 px-3">{language === "ta" ? "இடங்கள் (Places)" : "Places"}</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                              {Object.entries(result.classical_rules.planet_attributes_table).map(([p_name, attrs]) => (
                                <tr key={p_name} className="hover:bg-slate-50/70">
                                  <td className="py-2.5 px-3 font-extrabold text-[#153F6B] whitespace-nowrap">{p_name}</td>
                                  <td className="py-2.5 px-3 font-semibold text-slate-800 whitespace-nowrap">
                                    {language === "ta" ? attrs.direction_ta : attrs.direction_en}
                                  </td>
                                  <td className="py-2.5 px-3 font-black text-amber-700">{attrs.rays}</td>
                                  <td className="py-2.5 px-3 text-slate-600 whitespace-nowrap">{attrs.age}</td>
                                  <td className="py-2.5 px-3 text-slate-600 whitespace-nowrap">{attrs.height}</td>
                                  <td className="py-2.5 px-3 text-slate-600">
                                    {language === "ta" ? attrs.places_ta : attrs.places_en}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* 3. Pillars & Grahas Tab */}
                {activeTab === "pillars" && (
                  <div className="space-y-5">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Exalted planets */}
                      <div className="bg-emerald-50 rounded-xl p-4 border border-emerald-200">
                        <div className="text-xs font-bold text-emerald-800 uppercase tracking-wider mb-1">
                          {language === "ta" ? "உச்சக் கோள்கள் (Exalted Planets)" : "Exalted Planets (Prosperity)"}
                        </div>
                        <div className="text-sm font-semibold text-emerald-900">
                          {result.classical_rules.exalted_debilitated_audit.exalted_planets.length > 0
                            ? result.classical_rules.exalted_debilitated_audit.exalted_planets.join(", ")
                            : "None"}
                        </div>
                        <div className="text-xs text-slate-500 mt-1">
                          {language === "ta"
                            ? "உச்சம் பெற்ற கோள்களின் காரகத்துவம் செழிக்கும் (கவிப்பு தாக்கத்தைப் பார்க்கவும்)."
                            : "Indicates prosperity of concerned karakatwa (observe Kavippu)."}
                        </div>
                      </div>

                      {/* Debilitated planets */}
                      <div className="bg-rose-50 rounded-xl p-4 border border-rose-200">
                        <div className="text-xs font-bold text-rose-800 uppercase tracking-wider mb-1">
                          {language === "ta" ? "நீசக் கோள்கள் (Debilitated Planets)" : "Debilitated Planets"}
                        </div>
                        <div className="text-sm font-semibold text-rose-900">
                          {result.classical_rules.exalted_debilitated_audit.debilitated_planets.length > 0
                            ? result.classical_rules.exalted_debilitated_audit.debilitated_planets.join(", ")
                            : "None"}
                        </div>
                        <div className="text-xs text-slate-500 mt-1">
                          {language === "ta"
                            ? "செயல் திறனின்மை, வீண் வார்த்தைகள் அல்லது இயலாமையைக் காட்டும்."
                            : "Incapable of performing, talks nonsense or non-actionable."}
                        </div>
                      </div>
                    </div>

                    {/* Outer Jama Grahas */}
                    <div className="mt-4">
                      <h4 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-3">
                        {language === "ta" ? "8 ஜாமக் கோள்களின் அமர்வு (வெளிவட்டம்)" : "8 Jama Grahas Sign Placements (Outer Ring)"}
                      </h4>
                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                        {result.jama_grahas.map((g) => (
                          <div
                            key={g.id}
                            className="bg-white rounded-xl p-3 border border-slate-200 shadow-sm flex items-center gap-3"
                          >
                            <div
                              className="w-10 h-10 rounded-xl flex items-center justify-center font-bold text-base text-white shadow-sm flex-shrink-0"
                              style={{ backgroundColor: g.color }}
                            >
                              {g.symbol}
                            </div>
                            <div className="min-w-0 flex-1">
                              <div className="text-sm font-bold text-slate-800 truncate">
                                {language === "ta" ? g.name_ta : g.name_en} ({g.classical_name_ta})
                              </div>
                              <div className="text-xs text-slate-500">
                                {language === "ta" ? g.sign_name_ta : g.sign_name_en} ({g.dms})
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* 4. Direction & Timing Tab */}
                {activeTab === "direction" && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div className="bg-slate-50 rounded-2xl p-5 border border-slate-200 flex flex-col justify-between">
                      <div>
                        <div className="flex items-center gap-2 text-emerald-800 font-bold text-sm mb-3">
                          <Navigation className="w-5 h-5 text-emerald-600" />
                          <span>{language === "ta" ? "அஷ்ட திக்கு வழிகாட்டல்" : "Ashta Dikku Directional Alignment"}</span>
                        </div>
                        <p className="text-sm text-slate-700 leading-relaxed font-medium">
                          {language === "ta"
                            ? result.prediction_verdict.directional_guidance_ta
                            : result.prediction_verdict.directional_guidance_en}
                        </p>
                      </div>

                      <div className="mt-4 pt-4 border-t border-slate-200/60 text-xs text-slate-500">
                        {language === "ta"
                          ? "காணாமல் போன பொருள், உதவி புரியும் நபர் அல்லது சுபச் செய்தி இத்திசையிலிருந்து அமைய வாய்ப்புண்டு."
                          : "Primary orientation for tracing lost items, allies, or communication."}
                      </div>
                    </div>

                    <div className="bg-slate-50 rounded-2xl p-5 border border-slate-200 flex flex-col justify-between">
                      <div>
                        <div className="flex items-center gap-2 text-blue-800 font-bold text-sm mb-3">
                          <Timer className="w-5 h-5 text-blue-600" />
                          <span>{language === "ta" ? "சம்பவ காலம் (கால நிர்ணயம்)" : "Timing of Manifestation"}</span>
                        </div>
                        <p className="text-sm text-slate-700 leading-relaxed font-medium">
                          {language === "ta"
                            ? result.prediction_verdict.timing_of_event_ta
                            : result.prediction_verdict.timing_of_event_en}
                        </p>
                      </div>

                      <div className="mt-4 pt-4 border-t border-slate-200/60 text-xs text-slate-500">
                        {language === "ta"
                          ? "உதய ராசியின் சரம் / ஸ்திரம் / உபய தன்மை மற்றும் பாகை இடைவெளியின் அடிப்படையில் கணிக்கப்பட்டது."
                          : "Derived from Udhayam's Chara/Sthira/Ubhaya modality and angular degree spans."}
                      </div>
                    </div>
                  </div>
                )}

                {/* 5. 12 Bhavas Table */}
                {activeTab === "houses" && (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead>
                        <tr className="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                          <th className="py-2.5 px-3">{language === "ta" ? "பாவம்" : "House from Lagna"}</th>
                          <th className="py-2.5 px-3">{language === "ta" ? "ராசி" : "Sign (Rasi)"}</th>
                          <th className="py-2.5 px-3">{language === "ta" ? "அதிபதி" : "Lord"}</th>
                          <th className="py-2.5 px-3">{language === "ta" ? "முப்புள்ளி" : "Key Pillars"}</th>
                          <th className="py-2.5 px-3">{language === "ta" ? "ஜாமக் கோள்கள் (வெளி)" : "Jama Grahas"}</th>
                          <th className="py-2.5 px-3">{language === "ta" ? "கோச்சாரக் கிரகங்கள் (உள்)" : "Transit Planets"}</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {result.house_placements
                          .slice()
                          .sort((a, b) => a.house_from_udhayam - b.house_from_udhayam)
                          .map((h) => (
                            <tr key={h.sign_index} className="hover:bg-slate-50/70">
                              <td className="py-2 px-3 font-extrabold text-[#153F6B]">
                                {h.house_from_udhayam}
                                {h.house_from_udhayam === 1 && (
                                  <span className="ml-1 text-[10px] text-amber-600 uppercase font-bold">
                                    ({language === "ta" ? "லக்னம்" : "Lagna"})
                                  </span>
                                )}
                              </td>
                              <td className="py-2 px-3 font-semibold text-slate-800">
                                {language === "ta" ? h.sign_name_ta : h.sign_name_en} ({h.nature_ta})
                              </td>
                              <td className="py-2 px-3 text-slate-600">
                                {language === "ta" ? h.lord_ta : h.lord_en}
                              </td>
                              <td className="py-2 px-3">
                                <div className="flex flex-wrap gap-1">
                                  {h.is_udhayam && (
                                    <span className="px-1.5 py-0.5 rounded bg-blue-100 text-blue-800 text-[10px] font-bold">
                                      {language === "ta" ? "உதயம்" : "Udayam"}
                                    </span>
                                  )}
                                  {h.is_aarudham && (
                                    <span className="px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px] font-bold">
                                      {language === "ta" ? "ஆருடம்" : "Arudam"}
                                    </span>
                                  )}
                                  {h.is_kavippu && (
                                    <span className="px-1.5 py-0.5 rounded bg-rose-100 text-rose-800 text-[10px] font-bold">
                                      {language === "ta" ? "கவிப்பு" : "Kavippu"}
                                    </span>
                                  )}
                                </div>
                              </td>
                              <td className="py-2 px-3">
                                {h.jama_grahas.length > 0 ? (
                                  <div className="flex flex-wrap gap-1">
                                    {h.jama_grahas.map((g) => (
                                      <span
                                        key={g.id}
                                        className="px-1.5 py-0.5 rounded text-[10px] font-bold border"
                                        style={{
                                          borderColor: g.color,
                                          color: g.color,
                                          backgroundColor: `${g.color}15`,
                                        }}
                                      >
                                        {language === "ta" ? g.name_ta : g.name_en}
                                      </span>
                                    ))}
                                  </div>
                                ) : (
                                  <span className="text-slate-300">-</span>
                                )}
                              </td>
                              <td className="py-2 px-3">
                                {h.transit_planets.length > 0 ? (
                                  <div className="flex flex-wrap gap-1">
                                    {h.transit_planets.map((p, idx) => (
                                      <span
                                        key={idx}
                                        className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 text-[10px] font-medium"
                                      >
                                        {language === "ta" ? p.name_ta : p.name_en} ({p.dms})
                                        {p.is_retrograde ? " (R)" : ""}
                                      </span>
                                    ))}
                                  </div>
                                ) : (
                                  <span className="text-slate-300">-</span>
                                )}
                              </td>
                            </tr>
                          ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function ChartCell({
  signIdx,
  houseMap,
  language,
}: {
  signIdx: number;
  houseMap: Map<number, HousePlacementItem>;
  language: string;
}) {
  const house = houseMap.get(signIdx);
  if (!house) return <div className="bg-white rounded-xl p-2 border border-slate-200" />;

  const isUdhayam = house.is_udhayam;
  const isAarudham = house.is_aarudham;
  const isKavippu = house.is_kavippu;

  return (
    <div
      className={`rounded-xl p-2.5 sm:p-3 min-h-[110px] sm:min-h-[130px] flex flex-col justify-between transition-all relative ${
        isUdhayam
          ? "bg-blue-50/80 border-2 border-blue-500 shadow-sm"
          : isAarudham
          ? "bg-emerald-50/80 border-2 border-emerald-500 shadow-sm"
          : isKavippu
          ? "bg-rose-50/80 border-2 border-rose-400 shadow-sm"
          : "bg-white border border-slate-200 hover:border-slate-300"
      }`}
    >
      <div className="flex items-start justify-between gap-1">
        <div>
          <div className="text-xs font-bold text-slate-800">
            {language === "ta" ? house.sign_name_ta : house.sign_name_en}
          </div>
          <div className="text-[10px] text-slate-400 font-medium">
            {house.house_from_udhayam}-ம் பாவம் ({house.house_from_udhayam}H)
          </div>
        </div>

        <div className="flex flex-col items-end gap-1">
          {isUdhayam && (
            <span className="px-1.5 py-0.2 rounded bg-blue-600 text-white font-extrabold text-[9px] uppercase tracking-wide">
              {language === "ta" ? "உதயம்" : "Udayam"}
            </span>
          )}
          {isAarudham && (
            <span className="px-1.5 py-0.2 rounded bg-emerald-600 text-white font-extrabold text-[9px] uppercase tracking-wide">
              {language === "ta" ? "ஆருடம்" : "Arudam"}
            </span>
          )}
          {isKavippu && (
            <span className="px-1.5 py-0.2 rounded bg-rose-600 text-white font-extrabold text-[9px] uppercase tracking-wide">
              {language === "ta" ? "கவிப்பு" : "Kavippu"}
            </span>
          )}
        </div>
      </div>

      <div className="my-1.5 space-y-1">
        {house.jama_grahas.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {house.jama_grahas.map((g) => (
              <span
                key={g.id}
                className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-extrabold border shadow-xs"
                style={{
                  backgroundColor: `${g.color}20`,
                  color: g.color,
                  borderColor: `${g.color}60`,
                }}
              >
                <span>{g.symbol}</span>
                <span>{language === "ta" ? g.classical_name_ta : g.name_en}</span>
              </span>
            ))}
          </div>
        )}

        {house.transit_planets.length > 0 && (
          <div className="flex flex-wrap gap-1 pt-1 border-t border-slate-100">
            {house.transit_planets.map((p, idx) => (
              <span
                key={idx}
                className="text-[10px] font-medium text-slate-700 bg-slate-100/80 px-1 rounded flex items-center gap-0.5"
                title={`${p.name_en} (${p.dms})`}
              >
                <span>{language === "ta" ? p.name_ta.substring(0, 3) : p.name_en.substring(0, 2)}</span>
                {p.is_retrograde && <span className="text-red-500 font-bold text-[8px]">R</span>}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="text-[9px] text-slate-400 font-medium truncate pt-1 border-t border-slate-100 flex justify-between">
        <span>{language === "ta" ? house.lord_ta : house.lord_en}</span>
        <span>{house.direction_ta}</span>
      </div>
    </div>
  );
}

export default function JamakkolPrasanamPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-slate-50">
          <RefreshCw className="w-8 h-8 animate-spin text-[#153F6B]" />
        </div>
      }
    >
      <JamakkolPrasanamInner />
    </Suspense>
  );
}
