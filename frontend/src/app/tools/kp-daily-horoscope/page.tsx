"use client";

import React, { useState, useEffect, useCallback, useMemo } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  getKpDailyHoroscope,
  KpDailyHoroscopeResponse,
  RashiDailyPrediction,
  KpAspectPrediction,
  MoonSubLordWindow,
} from "@/lib/api";
import {
  Compass,
  Calendar,
  Clock,
  Sparkles,
  Search,
  CheckCircle2,
  AlertTriangle,
  Star,
  Zap,
  Briefcase,
  Coins,
  Heart,
  Activity,
  Plane,
  ShieldCheck,
  RefreshCw,
  Sun,
  Moon,
  TrendingUp,
  Award,
  Info,
  ChevronRight,
  Flame,
} from "lucide-react";

const RASHI_SYMBOLS: Record<number, string> = {
  1: "♈",
  2: "♉",
  3: "♊",
  4: "♋",
  5: "♌",
  6: "♍",
  7: "♎",
  8: "♏",
  9: "♐",
  10: "♑",
  11: "♒",
  12: "♓",
};

export default function KpDailyHoroscopePage() {
  const { language } = useLanguage();
  const isTa = language === "ta";

  // Date selection state
  const [todayStr, setTodayStr] = useState<string>("");
  const [selectedDate, setSelectedDate] = useState<string>("");
  const [activeRashiId, setActiveRashiId] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [horoscopeData, setHoroscopeData] = useState<KpDailyHoroscopeResponse | null>(null);

  // Initialize date on mount
  useEffect(() => {
    const today = new Date().toISOString().split("T")[0];
    setTodayStr(today);
    setSelectedDate(today);
  }, []);

  const handleTomorrow = () => {
    const d = new Date();
    d.setDate(d.getDate() + 1);
    setSelectedDate(d.toISOString().split("T")[0]);
  };

  // Fetch horoscope data
  const loadData = useCallback(async (targetDate: string) => {
    if (!targetDate) return;
    try {
      setLoading(true);
      setError(null);
      const res = await getKpDailyHoroscope({ date: targetDate, rashi: "all", ayanamsa: 1 });
      setHoroscopeData(res);
    } catch (err: any) {
      console.error("Failed to load daily KP horoscope:", err);
      setError(err?.message || "Failed to calculate daily KP horoscope");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (selectedDate) {
      loadData(selectedDate);
    }
  }, [selectedDate, loadData]);

  // Current active prediction
  const activePrediction = useMemo<RashiDailyPrediction | null>(() => {
    if (!horoscopeData || !horoscopeData.predictions) return null;
    return horoscopeData.predictions.find((p) => p.rashi_id === activeRashiId) || horoscopeData.predictions[0];
  }, [horoscopeData, activeRashiId]);

  const getAspectIcon = (code: string) => {
    switch (code) {
      case "career":
        return <Briefcase className="w-5 h-5 text-blue-500" />;
      case "finance":
        return <Coins className="w-5 h-5 text-emerald-500" />;
      case "love":
        return <Heart className="w-5 h-5 text-rose-500" />;
      case "health":
        return <Activity className="w-5 h-5 text-amber-500" />;
      case "travel":
        return <Plane className="w-5 h-5 text-indigo-500" />;
      default:
        return <Sparkles className="w-5 h-5 text-purple-500" />;
    }
  };

  const getSentimentBadge = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case "excellent":
        return "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800";
      case "favorable":
        return "bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300 border-blue-300 dark:border-blue-800";
      case "mixed":
        return "bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300 border-amber-300 dark:border-amber-800";
      default:
        return "bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300 border-rose-300 dark:border-rose-800";
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
      {/* Top Breadcrumb & Hero */}
      <div className="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Breadcrumbs
            items={[
              { label: isTa ? "முகப்பு" : "Home", href: "/" },
              { label: isTa ? "ஜோதிடக் கருவிகள்" : "Tools", href: "/tools" },
              { label: isTa ? "கே.பி. தினசரி ராசிபலன்" : "KP Daily Horoscope", href: "/tools/kp-daily-horoscope" },
            ]}
          />

          <div className="mt-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300 border border-purple-300 dark:border-purple-800">
                  {isTa ? "கே.பி. 249 உப-அதிபதி முறை" : "KP 249 Sub-Lord System"}
                </span>
                <span className="text-xs text-slate-500 flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  {isTa ? "நிகழ்நேர கோச்சாரம்" : "Real-time Transits"}
                </span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold mt-1 text-slate-900 dark:text-white">
                {isTa ? "தினசரி கே.பி. ராசிபலன்" : "KP Daily Transit Horoscope"}
              </h1>
              <p className="text-sm text-slate-600 dark:text-slate-400 mt-1 max-w-2xl">
                {isTa
                  ? "சந்திரனின் 249 உப-அதிபதி கோச்சாரம் மற்றும் பாவ காரகத்துவங்களின் அடிப்படையில் துல்லியமான தினசரி வழிகாட்டுதல்."
                  : "Accurate daily predictive forecast for all 12 Rashis based on real-time Moon sub-lord ingress and KP cuspal house significations."}
              </p>
            </div>

            {/* Date Quick Switcher */}
            <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800/80 p-1.5 rounded-xl border border-slate-200 dark:border-slate-700">
              <button
                type="button"
                onClick={() => setSelectedDate(todayStr)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                  selectedDate === todayStr
                    ? "bg-purple-600 text-white shadow-sm"
                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                }`}
              >
                {isTa ? "இன்று" : "Today"}
              </button>
              <button
                type="button"
                onClick={handleTomorrow}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                  selectedDate && selectedDate !== todayStr
                    ? "bg-purple-600 text-white shadow-sm"
                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                }`}
              >
                {isTa ? "நாளை" : "Tomorrow"}
              </button>
              <div className="flex items-center gap-1.5 pl-2 border-l border-slate-300 dark:border-slate-700">
                <Calendar className="w-4 h-4 text-slate-400" />
                <input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="bg-transparent text-xs font-medium focus:outline-none text-slate-800 dark:text-slate-200 cursor-pointer"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Planetary Overview Banner */}
        {horoscopeData && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-white dark:bg-slate-900 rounded-2xl p-4 border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400">
                <Sun className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs text-slate-500">{isTa ? "கிழமை அதிபதி" : "Day Lord"}</p>
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                  {horoscopeData.day_lord} ({isTa ? horoscopeData.day_of_week_ta : horoscopeData.day_of_week})
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-blue-100 dark:bg-blue-950/60 text-blue-700 dark:text-blue-400">
                <Moon className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs text-slate-500">{isTa ? "சந்திரன் ராசி" : "Moon Sign"}</p>
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                  {horoscopeData.moon_sign_at_noon}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-indigo-100 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-400">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs text-slate-500">{isTa ? "சந்திரன் நட்சத்திரம்" : "Moon Star"}</p>
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                  {horoscopeData.moon_star_at_noon}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-purple-100 dark:bg-purple-950/60 text-purple-700 dark:text-purple-400">
                <Award className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs text-slate-500">{isTa ? "மதிய உப-அதிபதி" : "Midday Sub-Lord"}</p>
                <p className="text-sm font-semibold text-purple-600 dark:text-purple-400">
                  {horoscopeData.moon_sub_lord_at_noon}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* 12 Rashis Selector Carousel / Grid */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-bold flex items-center gap-2">
              <Compass className="w-4 h-4 text-purple-600" />
              {isTa ? "ராசியைத் தேர்ந்தெடுக்கவும்" : "Select Your Rashi (Moon / Lagna Sign)"}
            </h2>
            <span className="text-xs text-slate-500">
              {isTa ? "12 ராசிகளின் கே.பி. கணிப்பு" : "12 Signs Available"}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-12 gap-2">
            {horoscopeData?.predictions.map((p) => {
              const isActive = p.rashi_id === activeRashiId;
              return (
                <button
                  key={p.rashi_id}
                  type="button"
                  onClick={() => setActiveRashiId(p.rashi_id)}
                  className={`flex flex-col items-center justify-center p-3 rounded-2xl border transition-all ${
                    isActive
                      ? "bg-purple-600 text-white border-purple-500 shadow-md shadow-purple-500/20 scale-[1.03]"
                      : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-purple-300 dark:hover:border-purple-800 text-slate-700 dark:text-slate-300"
                  }`}
                >
                  <span className="text-xl mb-1">{RASHI_SYMBOLS[p.rashi_id]}</span>
                  <span className="text-xs font-bold leading-tight">
                    {isTa ? p.rashi_name_ta : p.rashi_name_en}
                  </span>
                  <span
                    className={`mt-1 text-[10px] px-1.5 py-0.5 rounded-full font-semibold ${
                      isActive
                        ? "bg-purple-500/80 text-white"
                        : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                    }`}
                  >
                    {p.daily_score}%
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Loading / Error States */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-20 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800">
            <RefreshCw className="w-8 h-8 text-purple-600 animate-spin mb-3" />
            <p className="text-sm font-medium text-slate-600 dark:text-slate-400">
              {isTa ? "கே.பி. உப-அதிபதி கோச்சாரம் கணக்கிடப்படுகிறது..." : "Calculating KP 249 sub-lord transits..."}
            </p>
          </div>
        )}

        {error && (
          <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900 text-rose-800 dark:text-rose-300 flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
            <p className="text-sm font-medium">{error}</p>
          </div>
        )}

        {/* Active Prediction Main View */}
        {!loading && activePrediction && (
          <div className="space-y-8">
            {/* 1. Daily Executive Brief Statement Hero Card */}
            <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-purple-900 via-indigo-900 to-slate-950 text-white p-6 sm:p-8 shadow-xl">
              <div className="relative z-10 space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-5">
                  <div className="flex items-center gap-3">
                    <span className="text-4xl">{RASHI_SYMBOLS[activePrediction.rashi_id]}</span>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="text-2xl font-bold tracking-tight">
                          {isTa ? activePrediction.rashi_name_ta : activePrediction.rashi_name_en}
                        </h3>
                        <span className="text-xs px-2.5 py-0.5 rounded-full bg-white/15 text-purple-200 font-medium">
                          {isTa ? `ராசி நாதன்: ${activePrediction.sign_lord}` : `Lord: ${activePrediction.sign_lord}`}
                        </span>
                      </div>
                      <p className="text-xs text-purple-200 mt-0.5">
                        {isTa ? "இன்றைய தினசரி கே.பி. வழிகாட்டல்" : "Today's KP Executive Brief"}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 bg-white/10 backdrop-blur-md px-4 py-2.5 rounded-2xl border border-white/15">
                    <div>
                      <p className="text-[11px] text-purple-200 uppercase font-semibold">
                        {isTa ? "சாதக நிலை" : "Day Favorability"}
                      </p>
                      <div className="flex items-center gap-2">
                        <span className="text-2xl font-extrabold text-amber-300">
                          {activePrediction.daily_score}%
                        </span>
                        <div className="flex items-center text-amber-300 text-sm">
                          <Star className="w-4 h-4 fill-amber-300" />
                          <span className="ml-1 text-xs font-bold text-white">{activePrediction.daily_rating_stars}</span>
                        </div>
                      </div>
                    </div>
                    <span className="px-3 py-1 rounded-xl text-xs font-bold uppercase bg-white/20 text-white">
                      {activePrediction.day_sentiment}
                    </span>
                  </div>
                </div>

                {/* The Brief Statement */}
                <div className="bg-white/10 backdrop-blur-md p-5 rounded-2xl border border-white/15 space-y-2">
                  <p className="text-xs font-bold uppercase tracking-wider text-amber-300 flex items-center gap-1.5">
                    <Flame className="w-4 h-4 text-amber-300" />
                    {isTa ? "இன்றைய முக்கிய தாரக மந்திரம் / ஒரு வரி சுருக்கம்" : "Core Daily Punchline"}
                  </p>
                  <p className="text-base sm:text-lg font-semibold leading-relaxed text-slate-100">
                    "{isTa ? activePrediction.brief_statement_ta : activePrediction.brief_statement_en}"
                  </p>
                </div>

                {/* Highlight & Caution Pillars */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-emerald-950/40 border border-emerald-500/30 p-4 rounded-2xl flex items-start gap-3">
                    <div className="p-2 rounded-xl bg-emerald-500/20 text-emerald-300 flex-shrink-0 mt-0.5">
                      <Sparkles className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-300">
                        {isTa ? "வெற்றி வாய்ப்பு (சிறப்பான அம்சம்)" : "Peak Opportunity (Where You Win)"}
                      </h4>
                      <p className="text-xs text-slate-200 mt-1 leading-relaxed">
                        {isTa ? activePrediction.peak_highlight_ta : activePrediction.peak_highlight_en}
                      </p>
                    </div>
                  </div>

                  <div className="bg-rose-950/40 border border-rose-500/30 p-4 rounded-2xl flex items-start gap-3">
                    <div className="p-2 rounded-xl bg-rose-500/20 text-rose-300 flex-shrink-0 mt-0.5">
                      <AlertTriangle className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-xs font-bold uppercase tracking-wider text-rose-300">
                        {isTa ? "கவனிக்க வேண்டிய பகுதி (தவிர்க்க வேண்டியவை)" : "Watch Out / Caution Trap"}
                      </h4>
                      <p className="text-xs text-slate-200 mt-1 leading-relaxed">
                        {isTa ? activePrediction.caution_trap_ta : activePrediction.caution_trap_en}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Auspicious Slots & Lucky Attributes */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
                  <div className="bg-white/5 border border-white/10 p-3 rounded-xl">
                    <p className="text-[11px] text-purple-200">{isTa ? "பொன்னான நேரம்" : "Golden Hours"}</p>
                    <p className="text-xs font-bold text-amber-300 mt-0.5">{activePrediction.golden_hour_window}</p>
                  </div>
                  <div className="bg-white/5 border border-white/10 p-3 rounded-xl">
                    <p className="text-[11px] text-purple-200">{isTa ? "கவன நேரம்" : "Caution Hours"}</p>
                    <p className="text-xs font-bold text-rose-300 mt-0.5">{activePrediction.caution_hour_window}</p>
                  </div>
                  <div className="bg-white/5 border border-white/10 p-3 rounded-xl">
                    <p className="text-[11px] text-purple-200">{isTa ? "அதிர்ஷ்ட நிறம் & எண்" : "Lucky Color & No."}</p>
                    <p className="text-xs font-bold text-slate-100 mt-0.5">
                      {isTa ? activePrediction.lucky_color_ta : activePrediction.lucky_color_en} (#{activePrediction.lucky_number})
                    </p>
                  </div>
                  <div className="bg-white/5 border border-white/10 p-3 rounded-xl">
                    <p className="text-[11px] text-purple-200">{isTa ? "அதிர்ஷ்ட திசை" : "Lucky Direction"}</p>
                    <p className="text-xs font-bold text-slate-100 mt-0.5">
                      {isTa ? activePrediction.lucky_direction_ta : activePrediction.lucky_direction_en}
                    </p>
                  </div>
                </div>

                {/* KP Daily Remedy */}
                <div className="bg-purple-950/60 border border-purple-500/30 p-3.5 rounded-2xl flex items-center gap-3">
                  <ShieldCheck className="w-5 h-5 text-purple-300 flex-shrink-0" />
                  <p className="text-xs text-purple-200">
                    <span className="font-bold text-white mr-1.5">{isTa ? "கே.பி. பரிகார வழிகாட்டல்:" : "KP Daily Action:"}</span>
                    {isTa ? activePrediction.daily_remedy_ta : activePrediction.daily_remedy_en}
                  </p>
                </div>
              </div>
            </div>

            {/* 2. All 5 Life Aspects Detailed Analysis */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-purple-600" />
                  {isTa ? "அனைத்து அம்சங்களின் விரிவான பலன்கள்" : "In-Depth Life Aspects Analysis"}
                </h3>
                <span className="text-xs text-slate-500">
                  {isTa ? "காரகத்துவ பாவகங்கள் அடிப்படையில்" : "Cuspal Significations Breakdown"}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {activePrediction.aspects.map((aspect) => (
                  <div
                    key={aspect.aspect_code}
                    className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm space-y-4 hover:border-purple-300 dark:hover:border-purple-800 transition"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2.5">
                        <div className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800">
                          {getAspectIcon(aspect.aspect_code)}
                        </div>
                        <div>
                          <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                            {isTa ? aspect.aspect_name_tamil : aspect.aspect_name}
                          </h4>
                          <span className="text-[11px] text-slate-500">
                            {isTa ? "பாவகங்கள்: " : "Houses: "}
                            {aspect.signified_houses.join(", ")}
                          </span>
                        </div>
                      </div>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-semibold border ${getSentimentBadge(aspect.status)}`}>
                        {aspect.status}
                      </span>
                    </div>

                    {/* Score Bar */}
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-slate-500">{isTa ? "மதிப்பெண்" : "Score"}</span>
                        <span className="font-bold text-slate-800 dark:text-slate-200">{aspect.score}%</span>
                      </div>
                      <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-purple-500 to-indigo-600 rounded-full transition-all duration-500"
                          style={{ width: `${aspect.score}%` }}
                        />
                      </div>
                    </div>

                    {/* Insight */}
                    <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                      {isTa ? aspect.insight_ta : aspect.insight_en}
                    </p>

                    {/* Recommendation */}
                    <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                      <p className="text-[11px] text-slate-700 dark:text-slate-300 font-medium leading-normal">
                        {isTa ? aspect.key_recommendation_ta : aspect.key_recommendation_en}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 3. Moon Sub-Lord Hourly Transit Windows */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold flex items-center gap-2">
                    <Clock className="w-5 h-5 text-purple-600" />
                    {isTa ? "சந்திரனின் மணி நேர உப-அதிபதி கால அட்டவணை" : "Moon's Hourly KP Sub-Lord Schedule"}
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {isTa
                      ? "ஒவ்வொரு மணி நேரத்திலும் சந்திரனின் உப-அதிபதி மாற்றத்தால் ஏற்படும் நன்மை / எச்சரிக்கை நேரங்கள்."
                      : "Hourly shifts in the Moon's sub-lord triggering specific house combinations for your sign."}
                  </p>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-medium">
                    <span className="w-2 h-2 rounded-full bg-emerald-500" />
                    {isTa ? "பொன்னான நேரம்" : "Golden"}
                  </span>
                  <span className="flex items-center gap-1 text-rose-600 dark:text-rose-400 font-medium">
                    <span className="w-2 h-2 rounded-full bg-rose-500" />
                    {isTa ? "கவன நேரம்" : "Caution"}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {activePrediction.moon_sub_windows.map((win, idx) => {
                  const isGolden = win.sentiment === "golden";
                  const isCaution = win.sentiment === "caution";
                  return (
                    <div
                      key={idx}
                      className={`p-4 rounded-2xl border transition-all ${
                        isGolden
                          ? "bg-emerald-50/60 dark:bg-emerald-950/30 border-emerald-300 dark:border-emerald-800"
                          : isCaution
                          ? "bg-rose-50/60 dark:bg-rose-950/30 border-rose-300 dark:border-rose-800"
                          : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                          <Clock className="w-3.5 h-3.5 text-purple-500" />
                          {win.start_time} - {win.end_time}
                        </span>
                        <span
                          className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                            isGolden
                              ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
                              : isCaution
                              ? "bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300"
                              : "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300"
                          }`}
                        >
                          {win.sentiment}
                        </span>
                      </div>

                      <div className="text-xs text-slate-600 dark:text-slate-400 mb-2">
                        <span className="font-semibold text-slate-900 dark:text-white">
                          {win.sub_lord} Sub
                        </span>{" "}
                        ({win.star_name} - {win.star_lord} Star)
                        {win.activated_houses.length > 0 && (
                          <span className="ml-1 text-slate-500">
                            • {isTa ? "பாவகங்கள்: " : "Houses: "}
                            {win.activated_houses.join(", ")}
                          </span>
                        )}
                      </div>

                      <p className="text-xs text-slate-700 dark:text-slate-300 font-medium">
                        {isTa ? win.advice_ta : win.advice_en}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
