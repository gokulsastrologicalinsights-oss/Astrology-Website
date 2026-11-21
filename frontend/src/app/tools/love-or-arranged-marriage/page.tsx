"use client";

import React, { useState, useEffect, useMemo, useCallback, Suspense } from "react";import { DateInputDMY } from "@/components/common/DateInputDMY";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  LoveOrArrangedRequest,
  LoveOrArrangedResponse,
  SavedHoroscopeItem,
} from "@/lib/types";
import { predictLoveOrArranged } from "@/lib/api";
import {
  Heart,
  Sparkles,
  Calendar,
  Clock,
  MapPin,
  User,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Search,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  Printer,
  Compass,
  ArrowRight,
  Database,
  Flame,
  Award,
  Layers,
  Info,
} from "lucide-react";

const COMMON_TIMEZONES = [
  { label: "India (IST)", value: "Asia/Kolkata" },
  { label: "US East (EST/EDT)", value: "America/New_York" },
  { label: "US West (PST/PDT)", value: "America/Los_Angeles" },
  { label: "UK (GMT/BST)", value: "Europe/London" },
  { label: "UAE (GST)", value: "Asia/Dubai" },
  { label: "Singapore (SGT)", value: "Asia/Singapore" },
  { label: "Australia (AEST)", value: "Australia/Sydney" },
];

function LoveOrArrangedToolContent() {
  const { language } = useLanguage();
  const { session, isAuthenticated } = useAuth();
  const searchParams = useSearchParams();
  const savedIdParam = searchParams.get("saved_id");

  // Inputs
  const [name, setName] = useState("Native");
  const [gender, setGender] = useState<"male" | "female">("male");
  const [birthDate, setBirthDate] = useState("1995-10-24");
  const [birthTime, setBirthTime] = useState("14:30:00");
  const [latitude, setLatitude] = useState(13.0827); // Chennai
  const [longitude, setLongitude] = useState(80.2707);
  const [timezone, setTimezone] = useState("Asia/Kolkata");
  const [showCoordinateSettings, setShowCoordinateSettings] = useState(false);

  // Saved Horoscopes
  const [savedHoroscopes, setSavedHoroscopes] = useState<SavedHoroscopeItem[]>([]);
  const [loadingSavedList, setLoadingSavedList] = useState(false);
  const [selectedSavedId, setSelectedSavedId] = useState<string>("");
  const [chartSearchQuery, setChartSearchQuery] = useState("");
  const [showSavedPicker, setShowSavedPicker] = useState(false);

  // States
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<LoveOrArrangedResponse | null>(null);
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);

  // Populate from saved horoscope
  const populateFromSaved = (item: SavedHoroscopeItem) => {
    setName(item.person_name || "Native");
    const rawGender = (item.calculation_result as any)?.gender || (item as any).gender;
    if (rawGender === "female" || rawGender === "male") {
      setGender(rawGender);
    }
    setBirthDate(item.birth_date || "1995-10-24");
    setBirthTime(item.birth_time || "14:30:00");
    setLatitude(Number(item.latitude) || 13.0827);
    setLongitude(Number(item.longitude) || 80.2707);
    setTimezone(item.timezone || "Asia/Kolkata");
    setSelectedSavedId(item.id);
    setShowSavedPicker(false);
  };

  // Fetch saved horoscopes
  const fetchSavedHoroscopes = useCallback(async () => {
    setLoadingSavedList(true);
    try {
      const headers: Record<string, string> = { Accept: "application/json" };
      if (session?.access_token) {
        headers["Authorization"] = `Bearer ${session.access_token}`;
      }

      const resp = await fetch("/api/horoscopes?page=1&limit=500", {
        headers,
        cache: "no-store",
        credentials: "include",
      });

      if (resp.ok) {
        const data = await resp.json();
        const items: SavedHoroscopeItem[] = data.horoscopes || [];
        setSavedHoroscopes(items);
        if (items.length > 0 && savedIdParam) {
          const matched = items.find((h) => h.id === savedIdParam);
          if (matched) {
            populateFromSaved(matched);
          }
        }
      }
    } catch {
      // silently handle
    } finally {
      setLoadingSavedList(false);
    }
  }, [session, savedIdParam]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchSavedHoroscopes();
    }
  }, [isAuthenticated, fetchSavedHoroscopes]);

  const filteredSavedHoroscopes = useMemo(() => {
    const q = chartSearchQuery.trim().toLowerCase();
    if (!q) return savedHoroscopes;
    return savedHoroscopes.filter(
      (h) =>
        (h.person_name && h.person_name.toLowerCase().includes(q)) ||
        (h.birthplace && h.birthplace.toLowerCase().includes(q)) ||
        (h.location_name && h.location_name.toLowerCase().includes(q))
    );
  }, [savedHoroscopes, chartSearchQuery]);

  // Handle calculation
  const handleCalculate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setIsLoading(true);
    setError(null);

    const req: LoveOrArrangedRequest = {
      birth: {
        birth_date: birthDate,
        birth_time: birthTime.length === 5 ? `${birthTime}:00` : birthTime,
        timezone: timezone || "Asia/Kolkata",
        latitude: Number(latitude),
        longitude: Number(longitude),
      },
      name: name.trim() || undefined,
      gender: gender,
      chart_id: selectedSavedId || undefined,
    };

    try {
      const resp = await predictLoveOrArranged(req, session?.access_token);
      setResult(resp);
    } catch (err: any) {
      setError(
        err?.message ||
          (language === "ta"
            ? "கணிப்பு செய்வதில் பிழை ஏற்பட்டது. தயவுசெய்து விவரங்களை சரிபார்க்கவும்."
            : "Failed to evaluate horoscope. Please verify inputs.")
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Sample Preset Loader
  const loadSample = (type: "sample1" | "sample2") => {
    if (type === "sample1") {
      setName("Sample (Traditional)");
      setGender("male");
      setBirthDate("1995-10-24");
      setBirthTime("14:30:00");
      setLatitude(13.0827);
      setLongitude(80.2707);
      setTimezone("Asia/Kolkata");
    } else {
      setName("Sample (Romantic)");
      setGender("female");
      setBirthDate("1998-05-15");
      setBirthTime("21:15:00");
      setLatitude(13.0827);
      setLongitude(80.2707);
      setTimezone("Asia/Kolkata");
    }
  };

  return (
    <div className="min-h-screen bg-[#F4F6F9] py-6 px-3 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Navigation Breadcrumbs */}
        <Breadcrumbs
          items={[
            { label: language === "ta" ? "முகப்பு" : "Home", href: "/dashboard" },
            { label: language === "ta" ? "ஜோதிட கருவிகள்" : "Astrology Tools", href: "/tools" },
            {
              label:
                language === "ta"
                  ? "காதல் அல்லது நிச்சயிக்கப்பட்ட திருமணம்"
                  : "Love or Arranged Marriage",
            },
          ]}
        />

        {/* Page Header */}
        <div className="bg-gradient-to-r from-[#1B365D] via-[#24477D] to-[#392E5C] text-white p-6 sm:p-8 rounded-2xl shadow-lg relative overflow-hidden">
          <div className="absolute right-0 top-0 translate-x-8 -translate-y-8 opacity-10 pointer-events-none">
            <Heart className="w-64 h-64 text-white" />
          </div>

          <div className="relative z-10 space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-sm text-xs sm:text-sm font-medium border border-white/20">
              <Sparkles className="w-4 h-4 text-pink-300" />
              <span>
                {language === "ta"
                  ? "எளிய & துல்லியமான திருமண வகை கணிப்பு"
                  : "Dedicated Marriage Pathway Evaluator"}
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
              {language === "ta"
                ? "காதல் அல்லது நிச்சயிக்கப்பட்ட திருமணம்? (Love or Arranged Marriage)"
                : "Love vs. Arranged Marriage Predictor"}
            </h1>

            <p className="text-sm sm:text-base text-blue-100 max-w-2xl leading-relaxed">
              {language === "ta"
                ? "ஜாதகத்தில் 5 & 7-ஆம் பாவக தொடர்புகள், சுக்கிரன், குரு மற்றும் கே.பி உப-அதிபதி விதிகளின்படி சொந்த விருப்பத்திலான காதல் திருமணமா அல்லது பெற்றோரால் நிச்சயிக்கப்படும் மரபு வழி திருமணமா என்பதை மிக எளிய முறையில் அறியும் நேரடி கருவி."
                : "Enter birth details to get a direct, simple verdict on whether the horoscope indicates Love Marriage, Arranged Marriage, or Love-cum-Arranged with family blessings."}
            </p>
          </div>
        </div>

        {/* Main Content Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Input Form Column */}
          <div className="lg:col-span-5 space-y-4">
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-5 sm:p-6 space-y-5">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <h2 className="text-base font-bold text-slate-800 flex items-center gap-2">
                  <User className="w-5 h-5 text-[#1B365D]" />
                  <span>{language === "ta" ? "ஜாதக விவரங்கள்" : "Horoscope Details"}</span>
                </h2>

                <div className="flex items-center gap-2 text-xs">
                  <button
                    type="button"
                    onClick={() => loadSample("sample1")}
                    className="px-2 py-1 bg-slate-100 text-slate-700 rounded hover:bg-slate-200 transition"
                  >
                    {language === "ta" ? "மாதிரி 1" : "Sample 1"}
                  </button>
                  <button
                    type="button"
                    onClick={() => loadSample("sample2")}
                    className="px-2 py-1 bg-slate-100 text-slate-700 rounded hover:bg-slate-200 transition"
                  >
                    {language === "ta" ? "மாதிரி 2" : "Sample 2"}
                  </button>
                </div>
              </div>

              {/* Saved Horoscopes Quick Picker */}
              {savedHoroscopes.length > 0 && (
                <div className="bg-blue-50/70 border border-blue-200 rounded-xl p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold text-blue-900 flex items-center gap-1.5">
                      <Database className="w-3.5 h-3.5" />
                      {language === "ta"
                        ? "சேமிக்கப்பட்ட ஜாதகங்களிலிருந்து தேர்வு"
                        : "Pick from Saved Horoscopes"}
                    </span>
                    <button
                      type="button"
                      onClick={() => setShowSavedPicker(!showSavedPicker)}
                      className="text-xs font-medium text-blue-700 hover:text-blue-900 flex items-center gap-1"
                    >
                      {showSavedPicker
                        ? language === "ta"
                          ? "மறை"
                          : "Hide"
                        : language === "ta"
                        ? "தேர்வு செய்"
                        : "Browse"}
                      {showSavedPicker ? (
                        <ChevronUp className="w-3.5 h-3.5" />
                      ) : (
                        <ChevronDown className="w-3.5 h-3.5" />
                      )}
                    </button>
                  </div>

                  {showSavedPicker && (
                    <div className="space-y-2 mt-2">
                      <div className="relative">
                        <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-400" />
                        <input
                          type="text"
                          placeholder={
                            language === "ta"
                              ? "பெயர் மூலம் தேட..."
                              : "Search by name or place..."
                          }
                          value={chartSearchQuery}
                          onChange={(e) => setChartSearchQuery(e.target.value)}
                          className="w-full text-xs pl-8 pr-3 py-1.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white"
                        />
                      </div>
                      <div className="max-h-40 overflow-y-auto space-y-1 pr-1">
                        {filteredSavedHoroscopes.slice(0, 15).map((item) => (
                          <button
                            key={item.id}
                            type="button"
                            onClick={() => populateFromSaved(item)}
                            className={`w-full text-left px-2.5 py-1.5 rounded text-xs transition flex items-center justify-between ${
                              selectedSavedId === item.id
                                ? "bg-blue-600 text-white font-medium"
                                : "bg-white hover:bg-blue-100 text-slate-800 border border-slate-200"
                            }`}
                          >
                            <span className="truncate">{item.person_name}</span>
                            <span className="text-[10px] opacity-75 ml-2 shrink-0">
                              {item.birth_date}
                            </span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Form Fields */}
              <form onSubmit={handleCalculate} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    {language === "ta" ? "பெயர் (விருப்பத்தேர்வு)" : "Name (Optional)"}
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Enter name"
                    className="w-full text-sm px-3 py-2 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#1B365D] focus:outline-none bg-white"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    {language === "ta" ? "பாலினம்" : "Gender"}
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      onClick={() => setGender("male")}
                      className={`py-2 rounded-xl text-xs font-semibold border transition ${
                        gender === "male"
                          ? "bg-[#1B365D] text-white border-[#1B365D]"
                          : "bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100"
                      }`}
                    >
                      {language === "ta" ? "ஆண் (Male)" : "Male"}
                    </button>
                    <button
                      type="button"
                      onClick={() => setGender("female")}
                      className={`py-2 rounded-xl text-xs font-semibold border transition ${
                        gender === "female"
                          ? "bg-pink-700 text-white border-pink-700"
                          : "bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100"
                      }`}
                    >
                      {language === "ta" ? "பெண் (Female)" : "Female"}
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5 text-slate-500" />
                      {language === "ta" ? "பிறந்த தேதி" : "Birth Date"}
                    </label>
                    <DateInputDMY
                      value={birthDate}
                      onChange={(e) => setBirthDate(e.target.value)}
                      required
                      className="w-full text-sm px-3 py-2 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#1B365D] focus:outline-none bg-white"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5 text-slate-500" />
                      {language === "ta" ? "பிறந்த நேரம்" : "Birth Time"}
                    </label>
                    <input
                      type="time"
                      step="1"
                      value={birthTime}
                      onChange={(e) => setBirthTime(e.target.value)}
                      required
                      className="w-full text-sm px-3 py-2 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#1B365D] focus:outline-none bg-white"
                    />
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="text-xs font-semibold text-slate-700 flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-slate-500" />
                      {language === "ta" ? "பிறந்த இடம் & நேர மண்டலம்" : "Place & Coordinates"}
                    </label>
                    <button
                      type="button"
                      onClick={() => setShowCoordinateSettings(!showCoordinateSettings)}
                      className="text-[11px] text-blue-600 hover:underline"
                    >
                      {showCoordinateSettings
                        ? language === "ta"
                          ? "மறை"
                          : "Hide coordinates"
                        : language === "ta"
                        ? "அட்சரேகை மாற்ற"
                        : "Edit Lat/Long"}
                    </button>
                  </div>

                  {showCoordinateSettings ? (
                    <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-2 mt-2">
                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <span className="text-[10px] text-slate-500">Latitude</span>
                          <input
                            type="number"
                            step="0.0001"
                            value={latitude}
                            onChange={(e) => setLatitude(parseFloat(e.target.value) || 0)}
                            className="w-full text-xs p-1.5 rounded border border-slate-300 bg-white"
                          />
                        </div>
                        <div>
                          <span className="text-[10px] text-slate-500">Longitude</span>
                          <input
                            type="number"
                            step="0.0001"
                            value={longitude}
                            onChange={(e) => setLongitude(parseFloat(e.target.value) || 0)}
                            className="w-full text-xs p-1.5 rounded border border-slate-300 bg-white"
                          />
                        </div>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-500">Timezone</span>
                        <select
                          value={timezone}
                          onChange={(e) => setTimezone(e.target.value)}
                          className="w-full text-xs p-1.5 rounded border border-slate-300 bg-white"
                        >
                          {COMMON_TIMEZONES.map((tz) => (
                            <option key={tz.value} value={tz.value}>
                              {tz.label} ({tz.value})
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  ) : (
                    <div className="text-xs text-slate-600 bg-slate-50 px-3 py-2 rounded-xl border border-slate-200 flex items-center justify-between">
                      <span>Chennai, India (13.08°N, 80.27°E)</span>
                      <span className="text-[11px] text-slate-400">IST (+05:30)</span>
                    </div>
                  )}
                </div>

                {error && (
                  <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-start gap-2">
                    <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
                    <span>{error}</span>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-[#1B365D] to-[#2B4C7E] hover:from-[#152C4D] hover:to-[#223E68] text-white font-semibold text-sm shadow-md hover:shadow-lg transition flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {isLoading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>{language === "ta" ? "கணக்கிடப்படுகிறது..." : "Analyzing Horoscope..."}</span>
                    </>
                  ) : (
                    <>
                      <Heart className="w-4 h-4 text-pink-300" />
                      <span>{language === "ta" ? "காதல் அல்லது நிச்சயிக்கப்பட்ட திருமண பலன் காண்க" : "Predict Marriage Type"}</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>

          {/* Result Output Column */}
          <div className="lg:col-span-7">
            {result ? (
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-5 sm:p-7 space-y-6">
                {/* Header Action Bar */}
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <div>
                    <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                      {language === "ta" ? "திருமண வகை தீர்ப்பு" : "Marriage Outcome Verdict"}
                    </h3>
                    <p className="text-xs text-slate-400">
                      {result.native_name || "Native"} • {result.birth_summary}
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={() => window.print()}
                    className="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition"
                    title={language === "ta" ? "அச்சிடுக" : "Print"}
                  >
                    <Printer className="w-4 h-4" />
                  </button>
                </div>

                {/* Hero Verdict Box */}
                <div
                  className={`p-6 rounded-2xl border text-center space-y-4 shadow-sm relative overflow-hidden ${
                    result.verdict_badge === "LOVE"
                      ? "bg-gradient-to-b from-rose-50 via-pink-50/50 to-white border-rose-200"
                      : result.verdict_badge === "LOVE_ARRANGED"
                      ? "bg-gradient-to-b from-purple-50 via-indigo-50/40 to-white border-purple-200"
                      : "bg-gradient-to-b from-blue-50 via-sky-50/40 to-white border-blue-200"
                  }`}
                >
                  <div className="inline-flex p-3 rounded-full bg-white shadow-sm ring-4 ring-white/50 mx-auto">
                    {result.verdict_badge === "LOVE" ? (
                      <Heart className="w-8 h-8 text-rose-500 fill-rose-500 animate-pulse" />
                    ) : result.verdict_badge === "LOVE_ARRANGED" ? (
                      <Sparkles className="w-8 h-8 text-purple-600" />
                    ) : (
                      <ShieldCheck className="w-8 h-8 text-blue-600" />
                    )}
                  </div>

                  <div>
                    <span
                      className={`inline-block px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mb-2 ${
                        result.verdict_badge === "LOVE"
                          ? "bg-rose-100 text-rose-800"
                          : result.verdict_badge === "LOVE_ARRANGED"
                          ? "bg-purple-100 text-purple-800"
                          : "bg-blue-100 text-blue-800"
                      }`}
                    >
                      {result.verdict_badge === "LOVE"
                        ? language === "ta"
                          ? "காதல் திருமணம் யோகம்"
                          : "Love Marriage"
                        : result.verdict_badge === "LOVE_ARRANGED"
                        ? language === "ta"
                          ? "பெற்றோர் சம்மதத்துடன் காதல்"
                          : "Love with Family Blessings"
                        : language === "ta"
                        ? "நிச்சயிக்கப்பட்ட திருமணம்"
                        : "Arranged Marriage"}
                    </span>

                    <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                      {language === "ta" ? result.verdict_ta : result.verdict}
                    </h2>

                    <p className="text-xs sm:text-sm text-slate-600 max-w-lg mx-auto mt-2 leading-relaxed font-medium">
                      {language === "ta" ? result.summary_ta : result.summary_en}
                    </p>
                  </div>

                  {/* Probability Meter */}
                  <div className="pt-2 max-w-md mx-auto space-y-2">
                    <div className="flex justify-between text-xs font-bold">
                      <span className="text-rose-600 flex items-center gap-1">
                        <Heart className="w-3.5 h-3.5" />
                        {language === "ta" ? "காதல் வாய்ப்பு:" : "Love Probability:"} {result.love_percentage}%
                      </span>
                      <span className="text-blue-700 flex items-center gap-1">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        {language === "ta" ? "நிச்சயிக்கப்பட்ட வாய்ப்பு:" : "Arranged Probability:"}{" "}
                        {result.arranged_percentage}%
                      </span>
                    </div>

                    <div className="h-3.5 w-full bg-slate-100 rounded-full overflow-hidden flex p-0.5 border border-slate-200">
                      <div
                        style={{ width: `${result.love_percentage}%` }}
                        className="bg-gradient-to-r from-rose-500 to-pink-500 rounded-l-full transition-all duration-1000"
                        title={`Love Marriage: ${result.love_percentage}%`}
                      />
                      <div
                        style={{ width: `${result.arranged_percentage}%` }}
                        className="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-r-full transition-all duration-1000"
                        title={`Arranged Marriage: ${result.arranged_percentage}%`}
                      />
                    </div>
                  </div>
                </div>

                {/* Family Approval & Parental Consent Card */}
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-white border border-slate-200 shrink-0 text-amber-600">
                    <Award className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                      {language === "ta" ? "பெற்றோர் & குடும்பத்தார் ஆதரவு" : "Parental & Family Approval"}
                    </h4>
                    <p className="text-sm font-semibold text-slate-900 mt-0.5">
                      {language === "ta" ? result.family_support_ta : result.family_support}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">
                      {language === "ta"
                        ? "குருவின் பார்வை மற்றும் 9-ஆம் பாவக பலத்தின்படி குடும்பப் பெரியோர்களின் ஆசி வெளிப்படும் விதம்."
                        : "Assessed via Jupiter's protective drishti on the 7th/9th houses and dharma lord alignment."}
                    </p>
                  </div>
                </div>

                {/* Key Deciding Factors */}
                <div className="space-y-3">
                  <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                    <Compass className="w-4 h-4 text-[#1B365D]" />
                    <span>
                      {language === "ta"
                        ? "முக்கிய ஜோதிட காரணிகள் (Key Deciding Factors)"
                        : "Primary Astrological Indicators"}
                    </span>
                  </h4>

                  <div className="grid grid-cols-1 gap-2.5">
                    {result.key_factors.map((factor, idx) => (
                      <div
                        key={idx}
                        className={`p-3.5 rounded-xl border transition ${
                          factor.influence === "LOVE"
                            ? "bg-rose-50/40 border-rose-100"
                            : factor.influence === "ARRANGED"
                            ? "bg-blue-50/40 border-blue-100"
                            : "bg-slate-50 border-slate-200"
                        }`}
                      >
                        <div className="flex items-center justify-between gap-2 mb-1">
                          <span className="text-xs font-bold text-slate-900">
                            {language === "ta" ? factor.title_ta : factor.title_en}
                          </span>

                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold shrink-0 ${
                              factor.influence === "LOVE"
                                ? "bg-rose-100 text-rose-700"
                                : factor.influence === "ARRANGED"
                                ? "bg-blue-100 text-blue-700"
                                : "bg-slate-200 text-slate-700"
                            }`}
                          >
                            {factor.influence === "LOVE"
                              ? language === "ta"
                                ? "காதல் சாதகம்"
                                : "Love Indicator"
                              : factor.influence === "ARRANGED"
                              ? language === "ta"
                                ? "மரபு சாதகம்"
                                : "Arranged Indicator"
                              : "Neutral"}
                          </span>
                        </div>

                        <p className="text-xs text-slate-600 leading-relaxed">
                          {language === "ta" ? factor.description_ta : factor.description_en}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Collapsible Technical Astrological Signatures */}
                <div className="border border-slate-200 rounded-xl overflow-hidden">
                  <button
                    type="button"
                    onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
                    className="w-full p-3 bg-slate-50 hover:bg-slate-100 flex items-center justify-between text-xs font-semibold text-slate-700 transition"
                  >
                    <span className="flex items-center gap-1.5">
                      <Layers className="w-3.5 h-3.5 text-slate-500" />
                      {language === "ta"
                        ? "நுட்பமான கிரக அமைப்புகள் (Technical Planetary Positions)"
                        : "Planetary Positions & KP Sub-Lord Reference"}
                    </span>
                    {showTechnicalDetails ? (
                      <ChevronUp className="w-4 h-4 text-slate-400" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-slate-400" />
                    )}
                  </button>

                  {showTechnicalDetails && (
                    <div className="p-4 bg-white text-xs space-y-2 border-t border-slate-200">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-slate-600">
                        <div className="p-2 bg-slate-50 rounded">
                          <span className="font-semibold text-slate-800">5th House (Romance):</span>{" "}
                          {result.fifth_house_summary}
                        </div>
                        <div className="p-2 bg-slate-50 rounded">
                          <span className="font-semibold text-slate-800">7th House (Marriage):</span>{" "}
                          {result.seventh_house_summary}
                        </div>
                        <div className="p-2 bg-slate-50 rounded">
                          <span className="font-semibold text-slate-800">Venus Placement:</span>{" "}
                          {result.venus_summary}
                        </div>
                        {result.kp_sublord_summary && (
                          <div className="p-2 bg-slate-50 rounded">
                            <span className="font-semibold text-slate-800">KP Cuspal Rule:</span>{" "}
                            {result.kp_sublord_summary}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* Calculate Again */}
                <div className="text-center pt-2">
                  <button
                    type="button"
                    onClick={() => {
                      setResult(null);
                      window.scrollTo({ top: 0, behavior: "smooth" });
                    }}
                    className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition inline-flex items-center gap-1.5"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    <span>{language === "ta" ? "மற்றொரு ஜாதகத்தை கணக்கிடுக" : "Calculate Another Horoscope"}</span>
                  </button>
                </div>
              </div>
            ) : (
              /* Empty Placeholder State */
              <div className="h-full min-h-[380px] bg-white rounded-2xl border border-dashed border-slate-300 p-8 flex flex-col items-center justify-center text-center space-y-4">
                <div className="p-4 rounded-full bg-pink-50 border border-pink-100 text-pink-600">
                  <Heart className="w-10 h-10" />
                </div>
                <div className="max-w-sm space-y-1">
                  <h3 className="text-base font-bold text-slate-800">
                    {language === "ta"
                      ? "கணிப்பு இன்னும் செய்யப்படவில்லை"
                      : "Awaiting Horoscope Calculation"}
                  </h3>
                  <p className="text-xs text-slate-500 leading-relaxed">
                    {language === "ta"
                      ? "இடதுபுறம் உள்ள படிவத்தில் பிறந்த தேதி, நேரம் உள்ளிட்டு 'பலன் காண்க' பொத்தானை அழுத்தவும் அல்லது சேமிக்கப்பட்ட ஜாதகத்தைத் தேர்ந்தெடுக்கவும்."
                      : "Enter birth particulars on the left or select a saved chart, then click 'Predict Marriage Type' to see your simple love vs. arranged verdict."}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function LoveOrArrangedToolPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-[#F4F6F9]">
          <div className="w-8 h-8 border-4 border-[#1B365D] border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <LoveOrArrangedToolContent />
    </Suspense>
  );
}
