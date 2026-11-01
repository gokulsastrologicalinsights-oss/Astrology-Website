"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  DoubleTransitRequest,
  DoubleTransitResponse,
  DoubleTransitWindow,
} from "@/lib/types";
import { calculateDoubleTransit } from "@/lib/api";
import {
  Compass,
  Sparkles,
  Calendar,
  Clock,
  Heart,
  Briefcase,
  Baby,
  Coins,
  Home,
  Plane,
  Activity,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  ArrowRight,
  TrendingUp,
  Layers,
  Award,
  Search,
  Database,
  User,
} from "lucide-react";

const DOMAINS_LIST = [
  {
    id: "marriage",
    labelEn: "Marriage & Sacred Union",
    labelTa: "திருமணம்",
    house: 7,
    icon: Heart,
    color: "from-rose-500 to-pink-600",
    border: "border-rose-200",
    bg: "bg-rose-50",
    text: "text-rose-700",
  },
  {
    id: "career",
    labelEn: "Career Milestone & Promotion",
    labelTa: "தொழில் உயர்வு & வெற்றி",
    house: 10,
    icon: Briefcase,
    color: "from-blue-600 to-indigo-700",
    border: "border-blue-200",
    bg: "bg-blue-50",
    text: "text-blue-700",
  },
  {
    id: "childbirth",
    labelEn: "Childbirth & Progeny Blessing",
    labelTa: "குழந்தைப் பேறு",
    house: 5,
    icon: Baby,
    color: "from-amber-500 to-orange-600",
    border: "border-amber-200",
    bg: "bg-amber-50",
    text: "text-amber-800",
  },
  {
    id: "wealth",
    labelEn: "Wealth & Financial Windfall",
    labelTa: "தன யோகம் & பெருஞ்செல்வம்",
    house: 2,
    icon: Coins,
    color: "from-emerald-500 to-teal-700",
    border: "border-emerald-200",
    bg: "bg-emerald-50",
    text: "text-emerald-800",
  },
  {
    id: "property",
    labelEn: "Property & Real Estate",
    labelTa: "சொத்து & வீடு வாங்குதல்",
    house: 4,
    icon: Home,
    color: "from-purple-500 to-indigo-600",
    border: "border-purple-200",
    bg: "bg-purple-50",
    text: "text-purple-800",
  },
  {
    id: "foreign",
    labelEn: "Foreign Travel & Relocation",
    labelTa: "வெளிநாட்டுப் பயணம்",
    house: 12,
    icon: Plane,
    color: "from-sky-500 to-cyan-600",
    border: "border-sky-200",
    bg: "bg-sky-50",
    text: "text-sky-800",
  },
  {
    id: "health",
    labelEn: "Health Recovery & Vitality",
    labelTa: "ஆரோக்கிய மீட்சி",
    house: 1,
    icon: Activity,
    color: "from-emerald-600 to-green-700",
    border: "border-green-200",
    bg: "bg-green-50",
    text: "text-green-800",
  },
];

export default function DoubleTransitPage() {
  const { language } = useLanguage();
  const { session, isAuthenticated } = useAuth();

  // Mode: Saved chart vs manual entry
  const [inputMode, setInputMode] = useState<"saved" | "manual">("manual");
  const [savedHoroscopes, setSavedHoroscopes] = useState<any[]>([]);
  const [chartSearchQuery, setChartSearchQuery] = useState<string>("");
  const [selectedHoroscopeId, setSelectedHoroscopeId] = useState<string>("");

  // Form State
  const [birthDate, setBirthDate] = useState<string>("1995-10-24");
  const [birthTime, setBirthTime] = useState<string>("14:30:00");
  const [timezone, setTimezone] = useState<string>("Asia/Kolkata");
  const [latitude, setLatitude] = useState<number>(13.0827);
  const [longitude, setLongitude] = useState<number>(80.2707);

  // Radar Settings
  const [selectedDomain, setSelectedDomain] = useState<string>("marriage");
  const [forecastYears, setForecastYears] = useState<number>(3);
  const [includeRahu, setIncludeRahu] = useState<boolean>(true);

  // Results State
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DoubleTransitResponse | null>(null);
  const [filterPeakOnly, setFilterPeakOnly] = useState<boolean>(false);

  useEffect(() => {
    async function fetchSavedList() {
      if (!session?.access_token) return;
      try {
        const resp = await fetch("/api/horoscopes?limit=1000", {
          headers: { Authorization: `Bearer ${session.access_token}` },
        });
        if (resp.ok) {
          const data = await resp.json();
          const items = data.horoscopes || [];
          setSavedHoroscopes(items);
          if (items.length > 0 && !selectedHoroscopeId) {
            setInputMode("saved");
            setSelectedHoroscopeId(items[0].id);
            setBirthDate(items[0].birth_date);
            setBirthTime(items[0].birth_time);
            setTimezone(items[0].timezone || "Asia/Kolkata");
            setLatitude(items[0].latitude);
            setLongitude(items[0].longitude);
          }
        }
      } catch (err) {
        console.warn("Could not load saved horoscopes:", err);
      }
    }
    if (isAuthenticated) fetchSavedList();
  }, [isAuthenticated, session?.access_token]);

  const handleSelectSavedChart = (id: string) => {
    setSelectedHoroscopeId(id);
    const found = savedHoroscopes.find((h) => h.id === id);
    if (found) {
      setBirthDate(found.birth_date);
      setBirthTime(found.birth_time);
      setTimezone(found.timezone || "Asia/Kolkata");
      setLatitude(found.latitude);
      setLongitude(found.longitude);
    }
  };

  const handleScanRadar = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload: DoubleTransitRequest = {
        birth_date: birthDate,
        birth_time: birthTime,
        timezone,
        latitude: Number(latitude),
        longitude: Number(longitude),
        domain: selectedDomain,
        forecast_years: Number(forecastYears),
        include_rahu: includeRahu,
        ayanamsa: 1,
      };

      const res = await calculateDoubleTransit(payload);
      setResult(res);
    } catch (err: any) {
      setError(err?.detail || err?.message || "Double transit calculation failed.");
    } finally {
      setLoading(false);
    }
  };

  const activeDomainMeta = DOMAINS_LIST.find((d) => d.id === selectedDomain) || DOMAINS_LIST[0];
  const displayedWindows = result
    ? filterPeakOnly
      ? result.peak_windows
      : result.windows
    : [];

  return (
    <div className="min-h-screen bg-[#F8FAFC] pb-24 text-[#0F172A]">
      {/* Header Banner */}
      <div className="bg-linear-to-r from-[#102A4C] via-[#153F6B] to-[#1E4E8C] text-white py-10 px-4 sm:px-6 lg:px-8 border-b border-[#254F7F]">
        <div className="max-w-7xl mx-auto space-y-4">
          <Breadcrumbs
            items={[
              { label: language === "ta" ? "முகப்பு" : "Home", href: "/" },
              { label: language === "ta" ? "கருவிகள்" : "Tools", href: "/tools" },
              { label: language === "ta" ? "குரு-சனி இரட்டை கோச்சார ராடார்" : "Double Transit Radar" },
            ]}
          />

          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pt-2">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-400/20 border border-amber-300/30 text-amber-200 text-xs font-semibold mb-3">
                <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                <span>Vedic Astrology Gold Standard • Parashari & KP Engine</span>
              </div>
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-serif font-bold text-white tracking-tight">
                {language === "ta"
                  ? "குரு-சனி இரட்டை கோச்சார நிகழ்வு கால ராடார்"
                  : 'Double Transit ("Guru-Shani") Event Timing Radar'}
              </h1>
              <p className="text-sm sm:text-base text-slate-200 mt-2 max-w-3xl leading-relaxed">
                {language === "ta"
                  ? "வேத ஜோதிடத்தில் ஒரு முக்கிய நிகழ்வு நடப்பதற்கு குரு மற்றும் சனி ஆகிய இரண்டு பெரும் கிரகங்களும் ஒரே நேரத்தில் சம்பந்தப்பட்ட வீட்டை அல்லது வீட்டின் அதிபதியைப் பார்க்க வேண்டும் (Double Transit Principle). அடுத்த 5 ஆண்டுகளில் எந்தெந்த காலங்களில் மகாதிசை + கோச்சாரம் இணைகிறது என்பதை உடனே கண்டறியுங்கள்."
                  : "Vedic astrology's gold standard for pinpointing major life milestones is the Double Transit principle (both Jupiter and Saturn simultaneously aspecting or occupying the concerned house/lord, confirmed by Dasa). Scans upcoming calendar windows where Gochara and Dasa align."}
              </p>
            </div>

            <div className="flex items-center gap-3">
              <Link
                href="/tools/birth-time-rectification"
                className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-xs font-medium text-white transition-all flex items-center gap-2"
              >
                <span>BTR Assistant</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
              <Link
                href="/tools/kaksha-transit"
                className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-xs font-medium text-white transition-all flex items-center gap-2"
              >
                <span>Kaksha Alerts</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Form & Domain Selection */}
          <div className="lg:col-span-5 space-y-6">
            {/* Domain Picker Card */}
            <div className="bg-white rounded-2xl p-6 shadow-xs border border-[#E2E8F0] space-y-4">
              <div className="flex items-center gap-2 pb-3 border-b border-[#F1F5F9]">
                <Compass className="w-5 h-5 text-[#102A4C]" />
                <h3 className="font-serif font-bold text-base text-[#102A4C]">
                  {language === "ta" ? "கணிக்க வேண்டிய வாழ்க்கை நிகழ்வு" : "Target Life Event Domain"}
                </h3>
              </div>

              <div className="grid grid-cols-1 gap-2">
                {DOMAINS_LIST.map((dom) => {
                  const Icon = dom.icon;
                  const isSelected = selectedDomain === dom.id;
                  return (
                    <button
                      key={dom.id}
                      type="button"
                      onClick={() => setSelectedDomain(dom.id)}
                      className={`w-full p-3 rounded-xl border text-left flex items-center justify-between transition-all ${
                        isSelected
                          ? "bg-[#FAF7F0] border-[#B4872B] shadow-xs"
                          : "bg-white hover:bg-slate-50 border-[#E2E8F0]"
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-9 h-9 rounded-lg flex items-center justify-center ${
                            isSelected ? "bg-[#102A4C] text-amber-300" : "bg-slate-100 text-slate-600"
                          }`}
                        >
                          <Icon className="w-4 h-4" />
                        </div>
                        <div>
                          <span className={`text-xs font-bold block ${isSelected ? "text-[#102A4C]" : "text-[#334155]"}`}>
                            {language === "ta" ? dom.labelTa : dom.labelEn}
                          </span>
                          <span className="text-[11px] text-[#64748B]">
                            Primary House {dom.house}
                          </span>
                        </div>
                      </div>
                      {isSelected && <CheckCircle2 className="w-4 h-4 text-[#B4872B]" />}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Saved Horoscope Search & Selector */}
            {savedHoroscopes.length > 0 && (
              <div className="bg-white rounded-2xl p-5 shadow-xs border border-[#E2E8F0] space-y-3">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold text-[#102A4C]">
                    {language === "ta" ? "ஜாதகரைத் தேர்ந்தெடுக்கவும்" : "Select Saved Client Chart"}
                  </label>
                  <span className="text-[11px] font-mono text-[#64748B]">
                    {savedHoroscopes.length} saved
                  </span>
                </div>

                <div className="relative">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                  <input
                    type="text"
                    value={chartSearchQuery}
                    onChange={(e) => setChartSearchQuery(e.target.value)}
                    placeholder="Search by client name, place, date..."
                    className="w-full text-xs pl-9 pr-3 py-2 border border-[#CBD5E1] rounded-xl outline-none focus:ring-2 focus:ring-[#102A4C] bg-[#F8FAFC]"
                  />
                </div>

                <div className="max-h-40 overflow-y-auto space-y-1.5 pt-1">
                  {savedHoroscopes
                    .filter((h) => {
                      if (!chartSearchQuery) return true;
                      const q = chartSearchQuery.toLowerCase();
                      return (
                        (h.person_name && h.person_name.toLowerCase().includes(q)) ||
                        (h.location_name && h.location_name.toLowerCase().includes(q)) ||
                        (h.birth_date && h.birth_date.includes(q))
                      );
                    })
                    .map((h) => {
                      const isSel = h.id === selectedHoroscopeId;
                      return (
                        <div
                          key={h.id}
                          onClick={() => handleSelectSavedChart(h.id)}
                          className={`p-2.5 rounded-xl border text-left cursor-pointer transition-all flex items-center justify-between ${
                            isSel
                              ? "bg-[#FAF7F0] border-[#B4872B] ring-1 ring-[#B4872B]/30"
                              : "hover:bg-slate-50 border-[#E2E8F0]"
                          }`}
                        >
                          <div>
                            <strong className="text-xs text-[#102A4C] block">
                              {h.person_name || "Unnamed"}
                            </strong>
                            <span className="text-[10px] font-mono text-[#64748B]">
                              {h.birth_date} @ {h.birth_time} • {h.location_name || `${h.latitude}, ${h.longitude}`}
                            </span>
                          </div>
                          {isSel && <CheckCircle2 className="w-4 h-4 text-[#B4872B] shrink-0" />}
                        </div>
                      );
                    })}
                </div>
              </div>
            )}

            {/* Birth Details Card */}
            <div className="bg-white rounded-2xl p-6 shadow-xs border border-[#E2E8F0] space-y-4">
              <div className="flex items-center gap-2 pb-3 border-b border-[#F1F5F9]">
                <Clock className="w-5 h-5 text-[#102A4C]" />
                <h3 className="font-serif font-bold text-base text-[#102A4C]">
                  {language === "ta" ? "ஜாதகரின் பிறந்த விவரங்கள்" : "Birth Information"}
                </h3>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-[#475569] mb-1">
                    {language === "ta" ? "பிறந்த தேதி" : "Birth Date"}
                  </label>
                  <input
                    type="date"
                    value={birthDate}
                    onChange={(e) => setBirthDate(e.target.value)}
                    className="w-full text-xs font-mono px-3 py-2 border border-[#CBD5E1] rounded-lg outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-[#475569] mb-1">
                    {language === "ta" ? "பிறந்த நேரம்" : "Birth Time"}
                  </label>
                  <input
                    type="time"
                    step="1"
                    value={birthTime}
                    onChange={(e) => setBirthTime(e.target.value)}
                    className="w-full text-xs font-mono px-3 py-2 border border-[#CBD5E1] rounded-lg outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-[11px] font-semibold text-[#475569] mb-1">Timezone</label>
                  <input
                    type="text"
                    value={timezone}
                    onChange={(e) => setTimezone(e.target.value)}
                    className="w-full text-xs font-mono px-2 py-1.5 border border-[#CBD5E1] rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-[#475569] mb-1">Latitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={latitude}
                    onChange={(e) => setLatitude(parseFloat(e.target.value))}
                    className="w-full text-xs font-mono px-2 py-1.5 border border-[#CBD5E1] rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-[#475569] mb-1">Longitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={longitude}
                    onChange={(e) => setLongitude(parseFloat(e.target.value))}
                    className="w-full text-xs font-mono px-2 py-1.5 border border-[#CBD5E1] rounded-lg"
                  />
                </div>
              </div>

              {/* Forecast Horizon */}
              <div className="pt-3 border-t border-[#F1F5F9] space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-[#334155]">
                    Scan Horizon: {forecastYears} Years
                  </span>
                  <div className="flex items-center gap-1">
                    {[1, 2, 3, 5].map((yr) => (
                      <button
                        key={yr}
                        type="button"
                        onClick={() => setForecastYears(yr)}
                        className={`px-2.5 py-1 text-xs font-mono rounded-md transition-colors ${
                          forecastYears === yr
                            ? "bg-[#102A4C] text-white font-bold"
                            : "bg-slate-100 hover:bg-slate-200 text-[#475569]"
                        }`}
                      >
                        {yr}Y
                      </button>
                    ))}
                  </div>
                </div>

                <label className="flex items-center gap-2 cursor-pointer text-xs text-[#334155] pt-1">
                  <input
                    type="checkbox"
                    checked={includeRahu}
                    onChange={(e) => setIncludeRahu(e.target.checked)}
                    className="rounded accent-[#102A4C]"
                  />
                  <span>Include Rahu catalytic trine aspect (5th & 9th)</span>
                </label>
              </div>

              {/* Error Box */}
              {error && (
                <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              {/* Submit Button */}
              <button
                type="button"
                onClick={handleScanRadar}
                disabled={loading}
                className="w-full py-3.5 px-4 rounded-xl bg-linear-to-r from-[#102A4C] to-[#153F6B] hover:from-[#0B1E38] hover:to-[#102A4C] text-white font-serif font-bold text-sm tracking-wide shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin text-amber-300" />
                    <span>Scanning Next {forecastYears} Years of Planetary Gochara...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-amber-300" />
                    <span>Scan Double Transit Radar</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Right Column: Radar Results Dashboard */}
          <div className="lg:col-span-7 space-y-6">
            {!result ? (
              <div className="bg-white rounded-2xl p-12 text-center border border-[#E2E8F0] shadow-xs space-y-4">
                <div className="w-16 h-16 rounded-2xl bg-amber-50 border border-amber-200 text-[#8C6D23] flex items-center justify-center mx-auto">
                  <Compass className="w-8 h-8" />
                </div>
                <div className="max-w-md mx-auto space-y-2">
                  <h3 className="font-serif font-bold text-lg text-[#102A4C]">
                    {language === "ta" ? "இரட்டை கோச்சார ராடார் தயார்" : "Double Transit Radar Ready"}
                  </h3>
                  <p className="text-xs text-[#64748B] leading-relaxed">
                    {language === "ta"
                      ? "வாழ்க்கை நிகழ்வைத் தேர்ந்தெடுத்து (திருமணம், வேலை உயர்வு, குழந்தை, சொத்து) ராடாரை இயக்கவும். சனி மற்றும் குரு இரண்டும் ஒரே நேரத்தில் உங்கள் இலக்கு வீட்டைப் பார்க்கும் நாட்காட்டி சாளரங்களை இது வரைபடமாகக் காட்டும்."
                      : "Choose a target life milestone on the left (Marriage, Career, Childbirth, Wealth, Property) and trigger the scan. The radar will trace the multi-year orbits of Saturn and Jupiter and highlight every fruition window confirmed by Dasa."}
                  </p>
                </div>
              </div>
            ) : (
              <>
                {/* Hero Summary Card */}
                <div className="bg-linear-to-br from-[#102A4C] via-[#153F6B] to-[#1A365D] rounded-2xl p-6 sm:p-8 text-white shadow-lg border border-amber-400/30 space-y-6">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-5">
                    <div>
                      <span className="text-[11px] font-mono uppercase tracking-wider text-amber-300 font-semibold block">
                        Double Transit Alignment Radar
                      </span>
                      <h2 className="text-xl sm:text-2xl font-serif font-bold text-white mt-1">
                        {language === "ta" ? result.domain.name_ta : result.domain.name_en}
                      </h2>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="px-3 py-1 rounded-full bg-amber-400/20 border border-amber-300/30 text-amber-200 font-mono text-xs font-bold">
                        House {result.target_house} • Lord: {result.target_house_lord}
                      </span>
                    </div>
                  </div>

                  {/* Slow Planets Current Transit Bar */}
                  <div className="grid grid-cols-3 gap-3 p-3.5 rounded-xl bg-white/5 border border-white/10 text-center">
                    <div>
                      <span className="text-[10px] text-slate-300 uppercase block">Saturn (Shani)</span>
                      <span className="text-xs sm:text-sm font-bold text-amber-300">
                        {result.current_transits.saturn_sign} ({result.current_transits.saturn_degree}°)
                      </span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-300 uppercase block">Jupiter (Guru)</span>
                      <span className="text-xs sm:text-sm font-bold text-emerald-300">
                        {result.current_transits.jupiter_sign} ({result.current_transits.jupiter_degree}°)
                      </span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-300 uppercase block">Rahu (North Node)</span>
                      <span className="text-xs sm:text-sm font-bold text-indigo-300">
                        {result.current_transits.rahu_sign} ({result.current_transits.rahu_degree}°)
                      </span>
                    </div>
                  </div>

                  {/* Summary Verdict */}
                  <p className="text-xs sm:text-sm text-slate-200 leading-relaxed font-sans bg-white/5 p-4 rounded-xl border border-white/10">
                    {language === "ta" ? result.summary_verdict_ta : result.summary_verdict}
                  </p>
                </div>

                {/* Peak Event Timing Windows */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Award className="w-5 h-5 text-amber-600" />
                      <h3 className="font-serif font-bold text-base text-[#102A4C]">
                        {language === "ta" ? "கைகூடும் முக்கிய கால சாளரங்கள்" : "Fruition Calendar Windows"}
                      </h3>
                    </div>
                    <label className="flex items-center gap-2 cursor-pointer text-xs text-[#64748B]">
                      <input
                        type="checkbox"
                        checked={filterPeakOnly}
                        onChange={(e) => setFilterPeakOnly(e.target.checked)}
                        className="rounded accent-[#102A4C]"
                      />
                      <span>Peak Windows Only ({result.peak_windows.length})</span>
                    </label>
                  </div>

                  <div className="space-y-4">
                    {displayedWindows.length === 0 ? (
                      <div className="p-8 text-center bg-white rounded-2xl border border-[#E2E8F0] text-[#64748B] text-xs">
                        No windows found matching the current filter.
                      </div>
                    ) : (
                      displayedWindows.map((win, idx) => {
                        const isPeak = win.probability_percentage >= 85;
                        const isHigh = win.probability_percentage >= 70;
                        return (
                          <div
                            key={idx}
                            className={`p-6 rounded-2xl bg-white border transition-all space-y-4 shadow-xs ${
                              isPeak
                                ? "border-amber-300 ring-2 ring-amber-300/30"
                                : isHigh
                                ? "border-blue-200"
                                : "border-[#E2E8F0]"
                            }`}
                          >
                            {/* Window Header */}
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#F1F5F9] pb-3">
                              <div className="flex items-center gap-3">
                                <span
                                  className={`w-8 h-8 rounded-full flex items-center justify-center font-mono font-bold text-xs ${
                                    isPeak
                                      ? "bg-amber-100 text-amber-900"
                                      : "bg-slate-100 text-slate-700"
                                  }`}
                                >
                                  #{idx + 1}
                                </span>
                                <div>
                                  <div className="text-sm sm:text-base font-bold text-[#102A4C] flex items-center gap-2">
                                    <span>{win.start_date} – {win.end_date}</span>
                                    <span className="text-xs font-mono font-normal text-[#64748B]">
                                      ({win.duration_months} mos)
                                    </span>
                                  </div>
                                  <span className="text-xs font-semibold text-amber-700">
                                    {win.alignment_level}
                                  </span>
                                </div>
                              </div>

                              <div className="flex items-center gap-2">
                                <div className="text-right">
                                  <span className="text-[10px] text-[#64748B] uppercase block">Probability</span>
                                  <span
                                    className={`text-base font-mono font-extrabold ${
                                      isPeak
                                        ? "text-emerald-700"
                                        : isHigh
                                        ? "text-blue-700"
                                        : "text-slate-600"
                                    }`}
                                  >
                                    {win.probability_percentage}%
                                  </span>
                                </div>
                              </div>
                            </div>

                            {/* Planetary Confluence Badges */}
                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                              <div className="p-3 rounded-xl bg-[#FAF7F0] border border-[#E8DEC8]">
                                <span className="text-[10px] text-[#8C6D23] uppercase font-bold block mb-1">
                                  Saturn (Shani) Gochara
                                </span>
                                <div className="font-bold text-[#102A4C]">
                                  In {win.saturn_transit_sign}
                                </div>
                                <span className="text-[11px] text-slate-600 block mt-0.5">
                                  {win.saturn_aspect_type}
                                </span>
                              </div>

                              <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200">
                                <span className="text-[10px] text-emerald-800 uppercase font-bold block mb-1">
                                  Jupiter (Guru) Gochara
                                </span>
                                <div className="font-bold text-[#102A4C]">
                                  In {win.jupiter_transit_sign}
                                </div>
                                <span className="text-[11px] text-slate-600 block mt-0.5">
                                  {win.jupiter_aspect_type}
                                </span>
                              </div>

                              <div className="p-3 rounded-xl bg-indigo-50 border border-indigo-200">
                                <span className="text-[10px] text-indigo-800 uppercase font-bold block mb-1">
                                  Vimshottari Dasa
                                </span>
                                <div className="font-bold text-[#102A4C]">
                                  {win.running_mahadasha} – {win.running_antardasha}
                                </div>
                                <span className="text-[11px] text-slate-600 block mt-0.5 truncate" title={win.dasa_connection_details}>
                                  {win.dasa_confirms_event ? "Confirms House" : "Neutral Period"}
                                </span>
                              </div>
                            </div>

                            {/* Astrological Rationale */}
                            <p className="text-xs text-[#334155] leading-relaxed bg-[#F8FAFC] p-3 rounded-xl border border-[#E2E8F0]">
                              {language === "ta" ? win.astrological_rationale_ta : win.astrological_rationale}
                            </p>
                          </div>
                        );
                      })
                    )}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
