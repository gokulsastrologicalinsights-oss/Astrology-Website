"use client";

import React, { useState, useEffect, useCallback, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  KpMonthlyPredictionResponse,
  AvailableMonthItem,
  SavedHoroscopeItem,
  KpMonthlyEventItem,
} from "@/lib/types";
import { getAvailableKpMonths, getKpMonthlyPrediction } from "@/lib/api";
import {
  Compass,
  Calendar,
  Clock,
  Sparkles,
  Search,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  ShieldCheck,
  ArrowRight,
  Bookmark,
  Briefcase,
  Coins,
  Heart,
  Home,
  Car,
  Plane,
  GraduationCap,
  Baby,
  Scale,
  Activity,
  Flame,
  Star,
  Zap,
} from "lucide-react";

function getCategoryIcon(iconName: string) {
  switch (iconName) {
    case "Briefcase":
      return <Briefcase className="w-5 h-5 text-indigo-400" />;
    case "Coins":
      return <Coins className="w-5 h-5 text-amber-400" />;
    case "Heart":
      return <Heart className="w-5 h-5 text-pink-400" />;
    case "Home":
      return <Home className="w-5 h-5 text-emerald-400" />;
    case "Car":
      return <Car className="w-5 h-5 text-blue-400" />;
    case "Plane":
      return <Plane className="w-5 h-5 text-cyan-400" />;
    case "GraduationCap":
      return <GraduationCap className="w-5 h-5 text-purple-400" />;
    case "Baby":
      return <Baby className="w-5 h-5 text-rose-400" />;
    case "Scale":
      return <Scale className="w-5 h-5 text-teal-400" />;
    case "Activity":
      return <Activity className="w-5 h-5 text-emerald-400" />;
    case "AlertTriangle":
      return <AlertTriangle className="w-5 h-5 text-red-400" />;
    default:
      return <Sparkles className="w-5 h-5 text-amber-400" />;
  }
}

function KpMonthlyPredictionsContent() {
  const searchParams = useSearchParams();
  const initialHoroscopeId = searchParams.get("id") || "";

  const { language, t } = useLanguage();
  const { session, isAuthenticated, isLoading: authLoading } = useAuth();

  // Mode: "saved" (select saved customer chart) or "manual" (direct birth inputs)
  const [chartMode, setChartMode] = useState<"saved" | "manual">(
    initialHoroscopeId ? "saved" : "saved"
  );

  // Saved horoscopes list
  const [savedHoroscopes, setSavedHoroscopes] = useState<SavedHoroscopeItem[]>([]);
  const [selectedHoroscopeId, setSelectedHoroscopeId] = useState<string>(initialHoroscopeId);
  const [loadingHoroscopes, setLoadingHoroscopes] = useState<boolean>(false);

  // Manual chart input state
  const [manualName, setManualName] = useState<string>("Client Chart");
  const [manualDate, setManualDate] = useState<string>("1990-05-15");
  const [manualTime, setManualTime] = useState<string>("14:30:00");
  const [manualLat, setManualLat] = useState<string>("13.0827");
  const [manualLon, setManualLon] = useState<string>("80.2707");
  const [manualTz, setManualTz] = useState<string>("Asia/Kolkata");

  // Available candidate months
  const [availableMonths, setAvailableMonths] = useState<AvailableMonthItem[]>([]);
  const [selectedYear, setSelectedYear] = useState<number>(2026);
  const [selectedMonth, setSelectedMonth] = useState<number>(11);

  // Results state
  const [calculating, setCalculating] = useState<boolean>(false);
  const [predictionData, setPredictionData] = useState<KpMonthlyPredictionResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [copiedReport, setCopiedReport] = useState<boolean>(false);
  const [expandedEvents, setExpandedEvents] = useState<Record<string, boolean>>({});

  // Active view tab
  const [activeTab, setActiveTab] = useState<"guaranteed" | "favorable" | "caution" | "all">("guaranteed");

  // Load available months
  useEffect(() => {
    getAvailableKpMonths()
      .then((res) => {
        if (res && res.months && res.months.length > 0) {
          setAvailableMonths(res.months);
          const current = res.months.find((m) => m.is_current) || res.months[0];
          setSelectedYear(current.year);
          setSelectedMonth(current.month);
        }
      })
      .catch((err) => {
        console.warn("Could not load available months:", err);
      });
  }, []);

  // Fetch saved horoscopes
  const loadSavedHoroscopes = useCallback(async () => {
    if (authLoading) return;
    if (!isAuthenticated || !session?.access_token) return;
    setLoadingHoroscopes(true);
    try {
      const res = await fetch("/api/horoscopes?page=1&limit=1000", {
        cache: "no-store",
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });
      if (res.ok) {
        const data = await res.json();
        const items = data.items || [];
        setSavedHoroscopes(items);
        if (items.length > 0 && !selectedHoroscopeId) {
          setSelectedHoroscopeId(items[0].id);
        }
      }
    } catch (err) {
      console.warn("Failed to fetch saved horoscopes:", err);
    } finally {
      setLoadingHoroscopes(false);
    }
  }, [authLoading, isAuthenticated, session, selectedHoroscopeId]);

  useEffect(() => {
    loadSavedHoroscopes();
  }, [loadSavedHoroscopes]);

  // Execute prediction
  const handleCalculate = async () => {
    setErrorMsg(null);
    setCalculating(true);
    try {
      const token = session?.access_token;
      let reqBody: any = {
        year: selectedYear,
        month: selectedMonth,
        ayanamsa_id: 1, // KP
      };

      if (chartMode === "saved") {
        if (!selectedHoroscopeId) {
          throw new Error("தயவுசெய்து ஒரு ஜாதகத்தைத் தேர்ந்தெடுக்கவும்.");
        }
        reqBody.saved_horoscope_id = selectedHoroscopeId;
      } else {
        reqBody.birth = {
          birth_date: manualDate,
          birth_time: manualTime,
          latitude: parseFloat(manualLat),
          longitude: parseFloat(manualLon),
          timezone: manualTz,
          name: manualName,
        };
      }

      const res = await getKpMonthlyPrediction(reqBody, token);
      setPredictionData(res);
      // Auto switch to guaranteed if available, else favorable
      if (res.guaranteed_events && res.guaranteed_events.length > 0) {
        setActiveTab("guaranteed");
      } else {
        setActiveTab("favorable");
      }
    } catch (err: any) {
      setErrorMsg(err.message || "கணிப்பதில் பிழை ஏற்பட்டது. மீண்டும் முயற்சிக்கவும்.");
    } finally {
      setCalculating(false);
    }
  };

  const toggleExpand = (id: string) => {
    setExpandedEvents((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const copyToClipboard = () => {
    if (!predictionData) return;
    const text = `
KP நடப்பு காலக்கட்ட பலன்கள் (${predictionData.month_label_ta})
ஜாதகர்: ${predictionData.native_name}
நடப்பு தசா: ${predictionData.dasha_hierarchy.mahadasha_ta} | புத்தி: ${predictionData.dasha_hierarchy.antardasha_ta} | அந்தரம்: ${predictionData.dasha_hierarchy.pratyantardasha_ta}

${predictionData.overall_month_summary_ta}

🌟 கண்டிப்பாக நடந்து தீரும் நிகழ்வுகள் (${predictionData.guaranteed_events.length}):
${predictionData.guaranteed_events.map((e) => `• ${e.title_ta}\n  காலம்: ${e.trigger_window_dates}\n  முடிவு: ${e.summary_verdict_ta}`).join("\n\n")}

🚀 சாதகமான வாய்ப்புகள் (${predictionData.favorable_events.length}):
${predictionData.favorable_events.map((e) => `• ${e.title_ta}\n  காலம்: ${e.trigger_window_dates}\n  முடிவு: ${e.summary_verdict_ta}`).join("\n\n")}
    `.trim();

    navigator.clipboard.writeText(text);
    setCopiedReport(true);
    setTimeout(() => setCopiedReport(false), 2500);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-4 md:p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <Breadcrumbs
          items={[
            { label: language === "ta" ? "கருவிகள்" : "Tools", href: "/tools" },
            {
              label:
                language === "ta"
                  ? "KP நடப்பு காலக்கட்ட நிகழ்வு கணிப்பான்"
                  : "KP Period Event Timing",
            },
          ]}
        />

        {/* Hero Banner */}
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-amber-950/40 via-purple-950/30 to-slate-900 border border-amber-500/20 p-6 md:p-8 shadow-2xl">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="space-y-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-semibold">
                <Sparkles className="w-3.5 h-3.5" />
                <span>உயர் துல்லிய KP சிஸ்டம் (Krishnamurti Paddhati)</span>
              </div>
              <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-amber-200 via-white to-purple-200 bg-clip-text text-transparent">
                KP நடப்பு காலக்கட்ட பலன் & நிகழ்வு நிர்ணயிப்பான்
              </h1>
              <p className="text-slate-400 text-sm max-w-2xl">
                தசா-புத்தி-அந்தரம், பாவ உப-நட்சத்திர நாதன் (Cuspal Sub-Lord) மற்றும் கோச்சார சூரியனின் நட்சத்திர/உப-நட்சத்திர சஞ்சாரத்தை இணைத்து — 
                <strong> &quot;இந்த குறிப்பிட்ட மாதத்தில் எது கண்டிப்பாக நடந்து தீரும்&quot; </strong> 
                என்பதை அசைக்க முடியாத உறுதியுடன் கணிக்கிறது.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div className="p-3 bg-amber-500/10 rounded-xl border border-amber-500/20 text-amber-400">
                <Compass className="w-8 h-8" />
              </div>
            </div>
          </div>
        </div>

        {/* Control Panel: Month Selector & Chart Input */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          {/* 1. Month Selector Pills */}
          <div>
            <label className="text-xs font-semibold text-amber-300 uppercase tracking-wider block mb-3">
              📅 கணிக்க வேண்டிய காலக்கட்டம் / மாதம் (Target Month)
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
              {availableMonths.map((m) => {
                const isSelected = selectedYear === m.year && selectedMonth === m.month;
                return (
                  <button
                    key={`${m.year}-${m.month}`}
                    onClick={() => {
                      setSelectedYear(m.year);
                      setSelectedMonth(m.month);
                    }}
                    className={`p-3 rounded-xl text-left border transition-all flex flex-col justify-between ${
                      isSelected
                        ? "bg-amber-500/20 border-amber-400 text-amber-200 shadow-lg shadow-amber-500/10"
                        : "bg-slate-950/50 border-slate-800 hover:border-slate-700 text-slate-300"
                    }`}
                  >
                    <div className="text-xs font-medium text-slate-400">
                      {m.tag_ta ? (
                        <span className="inline-block px-1.5 py-0.5 rounded text-[10px] bg-amber-500/20 text-amber-300 font-semibold mb-1">
                          {m.tag_ta}
                        </span>
                      ) : (
                        <span>{m.year}</span>
                      )}
                    </div>
                    <div className="font-bold text-sm">{m.label_ta}</div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* 2. Chart Mode: Saved vs Manual */}
          <div className="border-t border-slate-800 pt-6">
            <div className="flex items-center gap-4 mb-4">
              <button
                onClick={() => setChartMode("saved")}
                className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                  chartMode === "saved"
                    ? "bg-amber-500 text-slate-950 shadow-md font-bold"
                    : "bg-slate-800 text-slate-400 hover:text-white"
                }`}
              >
                வாடிக்கையாளர் ஜாதகங்கள் (Saved Horoscopes)
              </button>
              <button
                onClick={() => setChartMode("manual")}
                className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                  chartMode === "manual"
                    ? "bg-amber-500 text-slate-950 shadow-md font-bold"
                    : "bg-slate-800 text-slate-400 hover:text-white"
                }`}
              >
                நேரடி விவரங்கள் (Manual Birth Input)
              </button>
            </div>

            {chartMode === "saved" ? (
              <div className="space-y-3">
                <label className="text-xs font-medium text-slate-400">
                  ஜாதகத்தைத் தேர்ந்தெடுக்கவும்:
                </label>
                {savedHoroscopes.length > 0 ? (
                  <select
                    value={selectedHoroscopeId}
                    onChange={(e) => setSelectedHoroscopeId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-slate-100 text-sm focus:border-amber-400 focus:outline-none"
                  >
                    {savedHoroscopes.map((h) => (
                      <option key={h.id} value={h.id}>
                        {h.person_name} — {h.birth_date} ({h.birthplace || "India"})
                      </option>
                    ))}
                  </select>
                ) : (
                  <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl text-sm text-slate-400 flex items-center justify-between">
                    <span>சேமிக்கப்பட்ட ஜாதகங்கள் இல்லை. நேரடி விவரங்களைப் பயன்படுத்தவும்.</span>
                    <button
                      onClick={() => setChartMode("manual")}
                      className="text-amber-400 hover:underline text-xs"
                    >
                      விவரங்களை உள்ளிடவும் →
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <label className="text-xs text-slate-400 block mb-1">பெயர் (Name)</label>
                  <input
                    type="text"
                    value={manualName}
                    onChange={(e) => setManualName(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-400 block mb-1">பிறந்த தேதி (Date)</label>
                  <input
                    type="date"
                    value={manualDate}
                    onChange={(e) => setManualDate(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-400 block mb-1">பிறந்த நேரம் (Time)</label>
                  <input
                    type="time"
                    step="1"
                    value={manualTime}
                    onChange={(e) => setManualTime(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Calculate Button */}
          <div className="flex justify-end pt-2">
            <button
              onClick={handleCalculate}
              disabled={calculating}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-sm flex items-center gap-2 shadow-lg shadow-amber-500/20 transition-all disabled:opacity-50"
            >
              {calculating ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>KP தசா & கோச்சாரத்தை ஆய்வு செய்கிறது...</span>
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 fill-slate-950" />
                  <span>KP காலக்கட்ட பலன்களைக் கணித்திடுக</span>
                </>
              )}
            </button>
          </div>

          {errorMsg && (
            <div className="p-4 bg-red-950/40 border border-red-500/30 rounded-xl text-red-300 text-sm flex items-center gap-2">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}
        </div>

        {/* Prediction Results Display */}
        {predictionData && (
          <div className="space-y-6">
            {/* 1. Dasha & Transit Sun Highlights Card */}
            <div className="bg-gradient-to-br from-slate-900 to-slate-950 border border-amber-500/30 rounded-2xl p-6 shadow-xl space-y-4">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-800 pb-4">
                <div>
                  <div className="text-xs text-amber-400 font-semibold tracking-wider uppercase">
                    KP காலக்கட்ட சுருக்கம் — {predictionData.native_name}
                  </div>
                  <h2 className="text-xl md:text-2xl font-bold text-white">
                    {predictionData.month_label_ta} மாத KP நிகழ்வு முடிவுகள்
                  </h2>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={copyToClipboard}
                    className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 flex items-center gap-1.5 transition-all"
                  >
                    {copiedReport ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                        <span>நகலெடுக்கப்பட்டது!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5 text-slate-400" />
                        <span>அறிக்கையை நகலெடு</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* D-B-A Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
                <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-[11px] text-slate-400">மகா தசா (Mahadasha)</div>
                  <div className="font-bold text-amber-300 text-base">
                    {predictionData.dasha_hierarchy.mahadasha_ta}
                  </div>
                  <div className="text-[10px] text-slate-500">அனுமதி தரும் அதிபதி</div>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-[11px] text-slate-400">புத்தி (Bhukti)</div>
                  <div className="font-bold text-emerald-300 text-base">
                    {predictionData.dasha_hierarchy.antardasha_ta}
                  </div>
                  <div className="text-[10px] text-slate-500">காலத்தை நிர்ணயிப்பவர்</div>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-[11px] text-slate-400">அந்தரம் (Antara)</div>
                  <div className="font-bold text-cyan-300 text-base">
                    {predictionData.dasha_hierarchy.pratyantardasha_ta}
                  </div>
                  <div className="text-[10px] text-slate-500">வாரங்களை நிர்ணயிப்பவர்</div>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl">
                  <div className="text-[11px] text-slate-400">சூரியன் கோச்சாரம் (Sun Transit)</div>
                  <div className="font-bold text-purple-300 text-base">
                    {predictionData.transit_sun.start_sign_ta} → {predictionData.transit_sun.end_sign_ta}
                  </div>
                  <div className="text-[10px] text-slate-500">மாதாந்திர தூண்டுதல்</div>
                </div>
              </div>

              {/* Overall Month Summary Callout */}
              <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-200 text-sm leading-relaxed">
                <span className="font-bold">✨ KP பொதுப்பலன்: </span>
                {predictionData.overall_month_summary_ta}
              </div>
            </div>

            {/* Category Navigation Tabs */}
            <div className="flex flex-wrap items-center gap-2 border-b border-slate-800 pb-2">
              <button
                onClick={() => setActiveTab("guaranteed")}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
                  activeTab === "guaranteed"
                    ? "bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/20"
                    : "bg-slate-900 text-slate-300 hover:bg-slate-800"
                }`}
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>கண்டிப்பாக நடப்பவை ({predictionData.guaranteed_events.length})</span>
              </button>
              <button
                onClick={() => setActiveTab("favorable")}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
                  activeTab === "favorable"
                    ? "bg-cyan-500 text-slate-950 shadow-lg shadow-cyan-500/20"
                    : "bg-slate-900 text-slate-300 hover:bg-slate-800"
                }`}
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>சாதகமான வாய்ப்புகள் ({predictionData.favorable_events.length})</span>
              </button>
              <button
                onClick={() => setActiveTab("caution")}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
                  activeTab === "caution"
                    ? "bg-rose-500 text-white shadow-lg shadow-rose-500/20"
                    : "bg-slate-900 text-slate-300 hover:bg-slate-800"
                }`}
              >
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>எச்சரிக்கை / விரயம் ({predictionData.caution_events.length})</span>
              </button>
              <button
                onClick={() => setActiveTab("all")}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
                  activeTab === "all"
                    ? "bg-purple-500 text-white shadow-lg shadow-purple-500/20"
                    : "bg-slate-900 text-slate-300 hover:bg-slate-800"
                }`}
              >
                <span>அனைத்து 11 துறைகளும் ({predictionData.all_events.length})</span>
              </button>
            </div>

            {/* Event List Rendering */}
            <div className="space-y-4">
              {(() => {
                let displayEvents: KpMonthlyEventItem[] = [];
                if (activeTab === "guaranteed") displayEvents = predictionData.guaranteed_events;
                else if (activeTab === "favorable") displayEvents = predictionData.favorable_events;
                else if (activeTab === "caution") displayEvents = predictionData.caution_events;
                else displayEvents = predictionData.all_events;

                if (displayEvents.length === 0) {
                  return (
                    <div className="p-8 text-center bg-slate-900/50 rounded-2xl border border-slate-800 text-slate-400">
                      இந்த பிரிவில் நிகழ்வுகள் எதுவும் இல்லை.
                    </div>
                  );
                }

                return displayEvents.map((ev) => {
                  const isExpanded = !!expandedEvents[ev.event_id];
                  const isGuaranteed = ev.status === "GUARANTEED";
                  const isFavorable = ev.status === "HIGHLY_FAVORABLE";
                  const isCaution = ev.status === "CAUTION";

                  return (
                    <div
                      key={ev.event_id}
                      className={`rounded-2xl border transition-all ${
                        isGuaranteed
                          ? "bg-gradient-to-r from-emerald-950/30 via-slate-900 to-slate-900 border-emerald-500/40 shadow-xl shadow-emerald-500/5"
                          : isFavorable
                          ? "bg-gradient-to-r from-cyan-950/20 via-slate-900 to-slate-900 border-cyan-500/30"
                          : isCaution
                          ? "bg-gradient-to-r from-rose-950/25 via-slate-900 to-slate-900 border-rose-500/30"
                          : "bg-slate-900/60 border-slate-800"
                      }`}
                    >
                      {/* Card Header */}
                      <div className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div className="flex items-start gap-3.5">
                          <div className="p-2.5 rounded-xl bg-slate-800/80 border border-slate-700">
                            {getCategoryIcon(ev.icon)}
                          </div>
                          <div>
                            <div className="flex items-center gap-2 mb-1 flex-wrap">
                              <span
                                className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${
                                  isGuaranteed
                                    ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                                    : isFavorable
                                    ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/40"
                                    : isCaution
                                    ? "bg-rose-500/20 text-rose-300 border-rose-500/40"
                                    : "bg-amber-500/20 text-amber-300 border-amber-500/40"
                                }`}
                              >
                                {ev.status_label_ta}
                              </span>
                              <span className="text-xs text-slate-400 font-medium">
                                காரிய ஸ்தானங்கள்: {ev.primary_houses.join(", ")}
                              </span>
                            </div>
                            <h3 className="text-lg font-bold text-white">{ev.title_ta}</h3>
                            <p className="text-xs text-amber-300/90 font-medium mt-1">
                              🎯 நிகழ்வு நடக்கும் உத்தேச காலம்: <strong>{ev.trigger_window_dates}</strong>
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center gap-3 self-end md:self-center">
                          <button
                            onClick={() => toggleExpand(ev.event_id)}
                            className="text-xs font-semibold px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center gap-1 transition-all"
                          >
                            <span>KP ஜோதிட ஆய்வு</span>
                            {isExpanded ? (
                              <ChevronUp className="w-3.5 h-3.5" />
                            ) : (
                              <ChevronDown className="w-3.5 h-3.5" />
                            )}
                          </button>
                        </div>
                      </div>

                      {/* Summary Verdict Callout */}
                      <div className="px-5 pb-4">
                        <div
                          className={`p-3.5 rounded-xl text-sm leading-relaxed border ${
                            isGuaranteed
                              ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-200"
                              : isFavorable
                              ? "bg-cyan-500/10 border-cyan-500/20 text-cyan-200"
                              : isCaution
                              ? "bg-rose-500/10 border-rose-500/20 text-rose-200"
                              : "bg-slate-800/60 border-slate-700/60 text-slate-300"
                          }`}
                        >
                          <strong>தீர்ப்பு: </strong>
                          {ev.summary_verdict_ta}
                        </div>
                      </div>

                      {/* Detailed Accordion with KP Evidence */}
                      {isExpanded && (
                        <div className="px-5 pb-5 pt-2 border-t border-slate-800/80 space-y-3 bg-slate-950/40 rounded-b-2xl">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                            <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl space-y-1">
                              <span className="font-semibold text-amber-300">
                                1. பாவ உப-நட்சத்திர நாதன் (விதி):
                              </span>
                              <p className="text-slate-300 leading-relaxed">{ev.cuspal_promise_ta}</p>
                            </div>
                            <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl space-y-1">
                              <span className="font-semibold text-emerald-300">
                                2. நடப்பு தசா-புத்தி இயக்கம்:
                              </span>
                              <p className="text-slate-300 leading-relaxed">{ev.dasha_bhukti_role_ta}</p>
                            </div>
                            <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl space-y-1">
                              <span className="font-semibold text-purple-300">
                                3. கோச்சார சூரியன் ட்ரிகர்:
                              </span>
                              <p className="text-slate-300 leading-relaxed">{ev.transit_trigger_ta}</p>
                            </div>
                            <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl space-y-1">
                              <span className="font-semibold text-cyan-300">
                                4. காரிய சித்தி வழிகாட்டல்:
                              </span>
                              <p className="text-slate-300 leading-relaxed">{ev.actionable_remedy_ta}</p>
                            </div>
                          </div>
                          <div className="text-[11px] text-slate-400 bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
                            <strong>காரக கிரகங்கள்: </strong>
                            {ev.significator_planets.join(", ") || "குரு, சந்திரன்"} |{" "}
                            <strong>துணை பாவங்கள்: </strong>
                            {ev.supporting_houses.join(", ")}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                });
              })()}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function KpMonthlyPredictionsPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
          <div className="flex items-center gap-3 text-amber-400">
            <RefreshCw className="w-6 h-6 animate-spin" />
            <span>ஏற்றுகிறது...</span>
          </div>
        </div>
      }
    >
      <KpMonthlyPredictionsContent />
    </Suspense>
  );
}
