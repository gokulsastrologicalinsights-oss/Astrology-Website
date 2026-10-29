"use client";

import React, { useState, useEffect, useMemo, useCallback, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  UnifiedMarriageRequest,
  UnifiedMarriageResponse,
  SavedHoroscopeItem,
} from "@/lib/types";
import { predictMarriageEvent, ApiError } from "@/lib/api";
import {
  Heart,
  Compass,
  Calendar,
  Clock,
  MapPin,
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Sliders,
  ChevronDown,
  ChevronUp,
  Info,
  Layers,
  ArrowRight,
  Database,
  Search,
  X,
  User,
} from "lucide-react";

function getUserDefaultTimezone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Kolkata";
  } catch {
    return "Asia/Kolkata";
  }
}

const COMMON_TIMEZONES = [
  { label: "India (IST)", value: "Asia/Kolkata" },
  { label: "US East (EST/EDT)", value: "America/New_York" },
  { label: "US West (PST/PDT)", value: "America/Los_Angeles" },
  { label: "UK (GMT/BST)", value: "Europe/London" },
  { label: "UAE (GST)", value: "Asia/Dubai" },
  { label: "Singapore (SGT)", value: "Asia/Singapore" },
  { label: "Australia (AEST)", value: "Australia/Sydney" },
];

const UNCERTAINTY_PRESETS = [
  { label: "Exact (0s)", value: 0 },
  { label: "±1 min (60s)", value: 60 },
  { label: "±2 mins (120s)", value: 120 },
  { label: "±5 mins (300s)", value: 300 },
  { label: "±15 mins (900s)", value: 900 },
];

function MarriagePredictionContent() {
  const searchParams = useSearchParams();
  const savedIdParam = searchParams.get("saved_id") || "";

  const { language } = useLanguage();
  const { session, isAuthenticated } = useAuth();

  // Mode: "manual" or "saved"
  const [inputMode, setInputMode] = useState<"manual" | "saved">(
    savedIdParam ? "saved" : "manual"
  );
  const [savedHoroscopes, setSavedHoroscopes] = useState<SavedHoroscopeItem[]>([]);
  const [selectedSavedId, setSelectedSavedId] = useState<string>(savedIdParam);
  const [loadingSavedList, setLoadingSavedList] = useState<boolean>(false);
  const [chartSearchQuery, setChartSearchQuery] = useState<string>("");

  // Form Fields
  const [birthDate, setBirthDate] = useState<string>("1995-10-24");
  const [birthTime, setBirthTime] = useState<string>("14:30:00");
  const [timezone, setTimezone] = useState<string>(getUserDefaultTimezone());
  const [latitude, setLatitude] = useState<string>("13.0827");
  const [longitude, setLongitude] = useState<string>("80.2707");
  const [locationName, setLocationName] = useState<string>("Chennai, India");
  const [uncertaintySeconds, setUncertaintySeconds] = useState<number>(120);
  const [startYear, setStartYear] = useState<string>("2024");
  const [endYear, setEndYear] = useState<string>("2032");
  const [forceTimingScan, setForceTimingScan] = useState<boolean>(false);

  // Form Validation State
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  // Execution & Response State
  const [loading, setLoading] = useState<boolean>(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [apiErrorStatus, setApiErrorStatus] = useState<number | null>(null);
  const [response, setResponse] = useState<UnifiedMarriageResponse | null>(null);

  // Section Accordion Toggles
  const [showMetadata, setShowMetadata] = useState<boolean>(false);
  const [showDisclaimers, setShowDisclaimers] = useState<boolean>(true);

  const populateFromSaved = (item: SavedHoroscopeItem) => {
    setBirthDate(item.birth_date);
    setBirthTime(item.birth_time);
    setTimezone(item.timezone || "Asia/Kolkata");
    setLatitude(String(item.latitude));
    setLongitude(String(item.longitude));
    setLocationName(item.birthplace || item.person_name || "Saved Chart");
    setSelectedSavedId(item.id);
  };

  // Load all saved horoscopes list with multi-page support if user is authenticated
  const fetchSavedHoroscopes = useCallback(async () => {
    setLoadingSavedList(true);
    try {
      const headers: Record<string, string> = {
        Accept: "application/json",
      };
      if (session?.access_token) {
        headers["Authorization"] = `Bearer ${session.access_token}`;
      }

      let allItems: SavedHoroscopeItem[] = [];
      let page = 1;
      const pageSize = 1000;
      let hasMore = true;

      while (hasMore) {
        const queryParams = new URLSearchParams({
          page: String(page),
          limit: String(pageSize),
        });

        const resp = await fetch(`/api/horoscopes?${queryParams.toString()}`, {
          headers,
          cache: "no-store",
          credentials: "include",
        });

        if (!resp.ok) break;

        const data = await resp.json();
        const items: SavedHoroscopeItem[] = data.horoscopes || [];
        allItems = allItems.concat(items);

        if (items.length < pageSize || allItems.length >= (data.totalCount || 0)) {
          hasMore = false;
        } else {
          page++;
          if (page > 10) break; // Safety threshold (up to 10,000 horoscopes)
        }
      }

      setSavedHoroscopes(allItems);
      if (allItems.length > 0 && savedIdParam) {
        const matched = allItems.find((h) => h.id === savedIdParam);
        if (matched) {
          populateFromSaved(matched);
        }
      }
    } catch (err) {
      console.warn("Failed to load saved horoscopes:", err);
    } finally {
      setLoadingSavedList(false);
    }
  }, [session?.access_token, savedIdParam]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchSavedHoroscopes();
    }
  }, [isAuthenticated, fetchSavedHoroscopes]);

  // Instant client-side search filtering across customer name, date of birth, time, birthplace, or chart #
  const filteredSavedHoroscopes = useMemo(() => {
    const q = chartSearchQuery.trim().toLowerCase();
    if (!q) return savedHoroscopes;

    return savedHoroscopes.filter((item) => {
      const name = (item.person_name || "").toLowerCase();
      const birthDate = (item.birth_date || "").toLowerCase();
      const birthTime = (item.birth_time || "").toLowerCase();
      const place = (item.birthplace || "").toLowerCase();
      const dispNum = item.display_number ? String(item.display_number) : "";

      return (
        name.includes(q) ||
        birthDate.includes(q) ||
        birthTime.includes(q) ||
        place.includes(q) ||
        dispNum === q ||
        `#${dispNum}` === q
      );
    });
  }, [savedHoroscopes, chartSearchQuery]);

  // Selected horoscope details for active confirmation card
  const selectedHoroscope = useMemo(() => {
    return savedHoroscopes.find((h) => h.id === selectedSavedId) || null;
  }, [savedHoroscopes, selectedSavedId]);

  // Validate form fields
  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    // 1. Date of birth
    if (!birthDate.trim()) {
      errors.birthDate = "Birth date is required.";
    } else if (!/^\d{4}-\d{2}-\d{2}$/.test(birthDate.trim())) {
      errors.birthDate = "Format must be YYYY-MM-DD.";
    } else {
      const d = new Date(birthDate);
      if (isNaN(d.getTime())) {
        errors.birthDate = "Invalid calendar date.";
      }
    }

    // 2. Time of birth
    if (!birthTime.trim()) {
      errors.birthTime = "Birth time is required.";
    } else if (!/^\d{2}:\d{2}(:\d{2})?$/.test(birthTime.trim())) {
      errors.birthTime = "Format must be HH:MM or HH:MM:SS (24-hour clock).";
    }

    // 3. Timezone
    if (!timezone.trim()) {
      errors.timezone = "IANA timezone is required.";
    } else {
      try {
        Intl.DateTimeFormat(undefined, { timeZone: timezone.trim() });
      } catch {
        errors.timezone = "Invalid IANA timezone (e.g. 'Asia/Kolkata', 'America/New_York').";
      }
    }

    // 4. Coordinates
    const latNum = parseFloat(latitude);
    if (isNaN(latNum) || latNum < -90.0 || latNum > 90.0) {
      errors.latitude = "Latitude must be a valid number between -90.0 and +90.0.";
    }

    const lonNum = parseFloat(longitude);
    if (isNaN(lonNum) || lonNum < -180.0 || lonNum > 180.0) {
      errors.longitude = "Longitude must be a valid number between -180.0 and +180.0.";
    }

    // 5. Uncertainty
    if (isNaN(uncertaintySeconds) || uncertaintySeconds < 0.0 || uncertaintySeconds > 1800.0) {
      errors.uncertaintySeconds = "Uncertainty must be between 0 and 1800 seconds (max 30 mins).";
    }

    // 6. Year range
    if (startYear.trim() && endYear.trim()) {
      const sY = parseInt(startYear, 10);
      const eY = parseInt(endYear, 10);
      if (isNaN(sY) || isNaN(eY)) {
        errors.years = "Start and End years must be valid integers.";
      } else if (eY < sY) {
        errors.years = "End year cannot be earlier than Start year.";
      }
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e?: React.FormEvent, forceScanOverride?: boolean) => {
    if (e) e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    setApiError(null);
    setApiErrorStatus(null);

    // Format birth time to HH:MM:SS
    const formattedTime = birthTime.trim().length === 5 ? `${birthTime.trim()}:00` : birthTime.trim();
    const isForce = forceScanOverride !== undefined ? forceScanOverride : forceTimingScan;

    const payload: UnifiedMarriageRequest = {
      birth: {
        birth_date: birthDate.trim(),
        birth_time: formattedTime,
        timezone: timezone.trim(),
        latitude: parseFloat(latitude),
        longitude: parseFloat(longitude),
      },
      birth_time_uncertainty_seconds: Number(uncertaintySeconds),
      start_year: startYear.trim() ? parseInt(startYear, 10) : undefined,
      end_year: endYear.trim() ? parseInt(endYear, 10) : undefined,
      force_timing_scan: isForce,
    };

    try {
      const token = session?.access_token;
      const data = await predictMarriageEvent(payload, token);
      setResponse(data);

      // Smooth scroll down to results
      setTimeout(() => {
        document.getElementById("results-section")?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setApiErrorStatus(err.statusCode);
        if (err.statusCode === 401) {
          setApiError(
            "Authentication required: You must be logged in with a valid account to execute unified marriage event predictions. Please sign in and retry."
          );
        } else if (err.statusCode === 422) {
          setApiError(
            `Validation error (HTTP 422): ${err.message || "Please check your birth data and parameter bounds."}`
          );
        } else {
          setApiError(err.message || "An unexpected error occurred during calculation.");
        }
      } else if (err instanceof Error) {
        setApiError(err.message);
      } else {
        setApiError("Calculation request failed. Please verify your connection.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResponse(null);
    setApiError(null);
    setApiErrorStatus(null);
    setValidationErrors({});
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-[#F8F9FA] pb-24 text-slate-800 antialiased overflow-x-hidden">
      {/* Top Header Banner */}
      <div className="border-b border-slate-200 bg-white">
        <div className="w-full px-4 py-6 sm:px-6 lg:px-8 2xl:px-10">
          <Breadcrumbs
            items={[
              { label: language === "ta" ? "முகப்பு" : "Home", href: "/" },
              { label: language === "ta" ? "கருவிகள்" : "Tools", href: "/tools" },
              {
                label: language === "ta" ? "திருமண கணிப்பு" : "Marriage Prediction",
                href: "/tools/marriage-prediction",
              },
            ]}
          />

          <div className="mt-4 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <div className="flex items-center gap-2.5">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[#FAF2DE] text-[#B4872B] shadow-sm">
                  <Heart className="h-6 w-6 fill-[#B4872B]/20" />
                </div>
                <div>
                  <h1 className="text-xl font-bold tracking-tight text-[#153F6B] sm:text-2xl md:text-3xl break-words">
                    {language === "ta"
                      ? "ஒருங்கிணைந்த கே.பி + வேத திருமண நிகழ்வு கணிப்பு"
                      : "Unified KP + Vedic Marriage Prediction Engine"}
                  </h1>
                  <p className="mt-0.5 text-xs text-slate-500 sm:text-sm">
                    {language === "ta"
                      ? "கே.பி உப-அதிபதி தத்துவம் மற்றும் பராசர வேத ஜோதிட விதிமுறைகளின் ஒருங்கிணைந்த கணக்கீடு"
                      : "Deterministic synthesis of Krishnamurti Paddhati (KP) cuspal sub-lords and Parashari Vedic principles"}
                  </p>
                </div>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-[#153F6B] ring-1 ring-inset ring-blue-700/10">
                Engine: XALEN 0.6.0
              </span>
              <span className="inline-flex items-center rounded-full bg-amber-50 px-3 py-1 text-xs font-medium text-amber-800 ring-1 ring-inset ring-amber-600/20">
                Rule: UNI-MARR-REC-001
              </span>
            </div>
          </div>
        </div>
      </div>

      <main className="w-full px-4 pt-6 sm:pt-8 sm:px-6 lg:px-8 2xl:px-10 min-w-0">
        {/* Epistemological & Scientific Disclaimer */}
        {showDisclaimers && (
          <div className="mb-8 rounded-xl border border-amber-200 bg-amber-50/70 p-4 text-sm text-amber-900 shadow-sm">
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-start gap-3">
                <Info className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />
                <div className="space-y-1">
                  <p className="font-semibold text-amber-950">
                    Epistemological & Rule-Based Boundary Notice
                  </p>
                  <p className="text-xs leading-relaxed text-amber-900/90 sm:text-sm">
                    This analysis is an algorithmic, deterministic implementation of classical
                    astrological rules (KP sub-lord significations, D1/D9 placements, and Vimshottari
                    Dasha/transits). It represents a <strong>symbolic rule evaluation</strong> and not a
                    fatalistic, guaranteed, or scientifically proven real-world outcome. Results must be
                    interpreted holistically by a qualified astrologer.
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setShowDisclaimers(false)}
                className="text-xs text-amber-700 hover:text-amber-950"
                aria-label="Dismiss notice"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        {/* Input Form Section */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8 overflow-hidden max-w-full">
          <div className="mb-6 flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-5">
            <div>
              <h2 className="text-lg font-bold text-[#153F6B] sm:text-xl">
                {language === "ta" ? "பிறப்பு விவரங்கள்" : "Birth Chart Details & Parameters"}
              </h2>
              <p className="mt-1 text-xs text-slate-500 sm:text-sm">
                Enter precise birth time, geographic coordinates, and uncertainty bounds.
              </p>
            </div>

            {/* Mode Toggle: Saved vs Manual */}
            {isAuthenticated && (
              <div className="inline-flex rounded-lg border border-slate-200 bg-slate-50 p-1">
                <button
                  type="button"
                  onClick={() => setInputMode("manual")}
                  className={`rounded-md px-3 py-1.5 text-xs font-semibold transition ${
                    inputMode === "manual"
                      ? "bg-white text-[#153F6B] shadow-sm"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  {language === "ta" ? "நேரடி பதிவு" : "Manual Entry"}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setInputMode("saved");
                    if (savedHoroscopes.length === 0) {
                      fetchSavedHoroscopes();
                    }
                  }}
                  className={`rounded-md px-3 py-1.5 text-xs font-semibold transition flex items-center gap-1.5 ${
                    inputMode === "saved"
                      ? "bg-white text-[#153F6B] shadow-sm"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  <Database className="w-3.5 h-3.5 text-[#B4872B]" />
                  <span>
                    {language === "ta" ? "சேமிக்கப்பட்ட ஜாதகங்கள்" : "Saved Customer Charts"}
                  </span>
                  <span className="rounded-full bg-slate-200/80 px-1.5 py-0.2 text-[10px] text-slate-700">
                    {loadingSavedList ? "..." : savedHoroscopes.length}
                  </span>
                </button>
              </div>
            )}
          </div>

          {/* Saved Charts Selector */}
          {inputMode === "saved" && isAuthenticated && (
            <div className="mb-6 rounded-xl border border-blue-100 bg-blue-50/50 p-4 space-y-3.5">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <label
                  htmlFor="saved-chart-search"
                  className="text-xs font-bold text-[#153F6B] flex items-center gap-1.5"
                >
                  <Database className="w-4 h-4 text-[#B4872B]" />
                  <span>
                    {language === "ta"
                      ? "சேமிக்கப்பட்ட வாடிக்கையாளர் ஜாதகத்தை தேர்ந்தெடுக்கவும்:"
                      : "Select from Saved Customer Horoscopes:"}
                  </span>
                  <span className="text-[11px] font-normal text-slate-500">
                    ({loadingSavedList ? (
                      <span className="inline-flex items-center gap-1 text-[#153F6B]">
                        <RefreshCw className="w-3 h-3 animate-spin" />
                        {language === "ta" ? "ஏற்றுகிறது..." : "Loading..."}
                      </span>
                    ) : (
                      `${savedHoroscopes.length} ${language === "ta" ? "மொத்த ஜாதகங்கள்" : "charts total"}`
                    )})
                  </span>
                </label>

                <button
                  type="button"
                  onClick={() => fetchSavedHoroscopes()}
                  disabled={loadingSavedList}
                  className="self-start sm:self-auto inline-flex items-center gap-1 text-xs text-[#153F6B] hover:text-[#1E4E8C] font-semibold py-1 px-2.5 rounded-lg border border-blue-200 bg-white hover:bg-blue-50 transition shadow-2xs"
                  title={language === "ta" ? "மீண்டும் புதுப்பிக்க" : "Refresh list"}
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${loadingSavedList ? "animate-spin" : ""}`} />
                  <span>{language === "ta" ? "புதுப்பி" : "Refresh"}</span>
                </button>
              </div>

              {/* Search Option Input */}
              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  id="saved-chart-search"
                  type="text"
                  value={chartSearchQuery}
                  onChange={(e) => setChartSearchQuery(e.target.value)}
                  placeholder={
                    language === "ta"
                      ? "வாடிக்கையாளர் பெயர், பிறந்த தேதி (YYYY-MM-DD), இடம் அல்லது ஜாதக எண் மூலம் தேடுக..."
                      : "Search saved charts by customer name, birth date (YYYY-MM-DD), place, or chart #..."
                  }
                  className="w-full pl-9 pr-9 py-2 text-xs sm:text-sm rounded-lg border border-slate-300 bg-white text-slate-800 placeholder:text-slate-400 focus:border-[#153F6B] focus:ring-1 focus:ring-[#153F6B] shadow-2xs"
                />
                {chartSearchQuery && (
                  <button
                    type="button"
                    onClick={() => setChartSearchQuery("")}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-1"
                    title={language === "ta" ? "தேடலை நீக்கு" : "Clear search"}
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>

              {chartSearchQuery && (
                <div className="flex items-center justify-between text-xs text-slate-600 px-0.5">
                  <span>
                    {language === "ta"
                      ? `"${chartSearchQuery}" க்கான முடிவுகள்: ${filteredSavedHoroscopes.length} ஜாதகம்(கள்)`
                      : `Results for "${chartSearchQuery}": ${filteredSavedHoroscopes.length} chart(s)`}
                  </span>
                  {filteredSavedHoroscopes.length === 0 && (
                    <button
                      type="button"
                      onClick={() => setChartSearchQuery("")}
                      className="text-blue-700 hover:underline font-semibold"
                    >
                      {language === "ta" ? "அனைத்தையும் காட்டு" : "Show all charts"}
                    </button>
                  )}
                </div>
              )}

              {loadingSavedList ? (
                <div className="py-4 flex items-center justify-center gap-2 text-slate-500 text-xs">
                  <RefreshCw className="w-4 h-4 animate-spin text-[#153F6B]" />
                  <span>
                    {language === "ta" ? "சேமிக்கப்பட்ட ஜாதகங்கள் ஏற்றப்படுகின்றன..." : "Loading saved customer horoscopes..."}
                  </span>
                </div>
              ) : savedHoroscopes.length === 0 ? (
                <div className="p-4 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 text-xs">
                  <p className="font-semibold">
                    {language === "ta"
                      ? "சேமிக்கப்பட்ட ஜாதகங்கள் எதுவும் இல்லை."
                      : "No saved customer horoscopes found in this account."}
                  </p>
                  <p className="mt-1 text-slate-600">
                    {language === "ta"
                      ? "ஜாதக கணிப்பு பக்கத்தில் புதிய ஜாதகங்களை உருவாக்கி சேமிக்கலாம்."
                      : "Generate and save charts using the Horoscope tool, or switch to Manual Entry."}
                  </p>
                </div>
              ) : (
                <>

                  {/* Dropdown Chart Selection */}
                  <div>
                    <select
                      id="saved-chart-select"
                      value={selectedSavedId}
                      onChange={(e) => {
                        const id = e.target.value;
                        setSelectedSavedId(id);
                        const matched = savedHoroscopes.find((h) => h.id === id);
                        if (matched) populateFromSaved(matched);
                      }}
                      className="w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-800 shadow-sm focus:border-[#153F6B] focus:outline-none focus:ring-1 focus:ring-[#153F6B]"
                    >
                      <option value="">
                        {filteredSavedHoroscopes.length === 0
                          ? language === "ta" ? "-- பொருத்தமான ஜாதகங்கள் இல்லை --" : "-- No matching charts found --"
                          : language === "ta" ? `-- ஜாதகத்தை தேர்ந்தெடுக்கவும் (${filteredSavedHoroscopes.length} கிடைத்துள்ளன) --` : `-- Choose a saved chart (${filteredSavedHoroscopes.length} available) --`}
                      </option>
                      {filteredSavedHoroscopes.map((h) => (
                        <option key={h.id} value={h.id}>
                          {h.display_number ? `#${h.display_number} - ` : ""}{h.person_name} ({h.birth_date} {h.birth_time}) - {h.birthplace || "Location"}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Active Selected Horoscope Details Preview Card */}
                  {selectedHoroscope && (
                    <div className="rounded-lg border border-emerald-200 bg-emerald-50/70 p-3 text-xs text-emerald-950 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                      <div className="flex items-start gap-2.5">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
                        <div>
                          <div className="font-bold text-emerald-900 text-sm flex items-center gap-2">
                            <span>{selectedHoroscope.person_name}</span>
                            {selectedHoroscope.display_number && (
                              <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-emerald-200/80 text-emerald-800">
                                #{selectedHoroscope.display_number}
                              </span>
                            )}
                          </div>
                          <div className="text-emerald-800 text-xs mt-0.5 flex flex-wrap gap-x-3 gap-y-1">
                            <span>📅 {selectedHoroscope.birth_date}</span>
                            <span>⏰ {selectedHoroscope.birth_time}</span>
                            <span>📍 {selectedHoroscope.birthplace || "Coordinates"} ({Number(selectedHoroscope.latitude).toFixed(2)}°, {Number(selectedHoroscope.longitude).toFixed(2)}°)</span>
                            <span>🌐 {selectedHoroscope.timezone}</span>
                          </div>
                        </div>
                      </div>
                      <div className="self-end sm:self-center shrink-0">
                        <span className="text-[11px] font-semibold text-emerald-700 bg-white/90 px-2.5 py-1 rounded-md border border-emerald-300 shadow-2xs">
                          ✓ {language === "ta" ? "விவரங்கள் நிரப்பப்பட்டன" : "Fields Populated"}
                        </span>
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate>
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
              {/* Date of Birth */}
              <div>
                <label
                  htmlFor="birth-date"
                  className="mb-1.5 block text-xs font-bold uppercase tracking-wider text-slate-600"
                >
                  Date of Birth <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                    <Calendar className="h-4 w-4" />
                  </div>
                  <input
                    id="birth-date"
                    type="date"
                    value={birthDate}
                    onChange={(e) => {
                      setBirthDate(e.target.value);
                      if (validationErrors.birthDate) {
                        setValidationErrors((prev) => ({ ...prev, birthDate: "" }));
                      }
                    }}
                    className={`w-full rounded-lg border py-2.5 pl-10 pr-3.5 text-sm transition focus:outline-none focus:ring-1 ${
                      validationErrors.birthDate
                        ? "border-red-500 bg-red-50/20 text-red-900 focus:border-red-500 focus:ring-red-500"
                        : "border-slate-300 bg-white text-slate-800 focus:border-[#153F6B] focus:ring-[#153F6B]"
                    }`}
                    required
                  />
                </div>
                {validationErrors.birthDate && (
                  <p className="mt-1 text-xs text-red-600">{validationErrors.birthDate}</p>
                )}
              </div>

              {/* Time of Birth */}
              <div>
                <label
                  htmlFor="birth-time"
                  className="mb-1.5 block text-xs font-bold uppercase tracking-wider text-slate-600"
                >
                  Time of Birth (Local Civil) <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                    <Clock className="h-4 w-4" />
                  </div>
                  <input
                    id="birth-time"
                    type="text"
                    value={birthTime}
                    placeholder="HH:MM:SS (24-hour)"
                    onChange={(e) => {
                      setBirthTime(e.target.value);
                      if (validationErrors.birthTime) {
                        setValidationErrors((prev) => ({ ...prev, birthTime: "" }));
                      }
                    }}
                    className={`w-full rounded-lg border py-2.5 pl-10 pr-3.5 text-sm transition focus:outline-none focus:ring-1 ${
                      validationErrors.birthTime
                        ? "border-red-500 bg-red-50/20 text-red-900 focus:border-red-500 focus:ring-red-500"
                        : "border-slate-300 bg-white text-slate-800 focus:border-[#153F6B] focus:ring-[#153F6B]"
                    }`}
                    required
                  />
                </div>
                <p className="mt-1 text-[11px] text-slate-500">
                  Local clock time. Do not convert to UTC or solar time.
                </p>
                {validationErrors.birthTime && (
                  <p className="mt-0.5 text-xs text-red-600">{validationErrors.birthTime}</p>
                )}
              </div>

              {/* Timezone */}
              <div>
                <label
                  htmlFor="birth-timezone"
                  className="mb-1.5 block text-xs font-bold uppercase tracking-wider text-slate-600"
                >
                  IANA Timezone <span className="text-red-500">*</span>
                </label>
                <input
                  id="birth-timezone"
                  type="text"
                  value={timezone}
                  onChange={(e) => {
                    setTimezone(e.target.value);
                    if (validationErrors.timezone) {
                      setValidationErrors((prev) => ({ ...prev, timezone: "" }));
                    }
                  }}
                  className={`w-full rounded-lg border px-3.5 py-2.5 text-sm transition focus:outline-none focus:ring-1 ${
                    validationErrors.timezone
                      ? "border-red-500 bg-red-50/20 text-red-900 focus:border-red-500 focus:ring-red-500"
                      : "border-slate-300 bg-white text-slate-800 focus:border-[#153F6B] focus:ring-[#153F6B]"
                  }`}
                  placeholder="e.g. Asia/Kolkata"
                  required
                />
                <div className="mt-1.5 flex flex-wrap gap-1">
                  {COMMON_TIMEZONES.slice(0, 4).map((tz) => (
                    <button
                      key={tz.value}
                      type="button"
                      onClick={() => setTimezone(tz.value)}
                      className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] text-slate-600 hover:bg-slate-200"
                    >
                      {tz.label}
                    </button>
                  ))}
                </div>
                {validationErrors.timezone && (
                  <p className="mt-1 text-xs text-red-600">{validationErrors.timezone}</p>
                )}
              </div>

              {/* Latitude */}
              <div>
                <label
                  htmlFor="birth-lat"
                  className="mb-1.5 block text-xs font-bold uppercase tracking-wider text-slate-600"
                >
                  Latitude (°N / -S) <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                    <MapPin className="h-4 w-4" />
                  </div>
                  <input
                    id="birth-lat"
                    type="number"
                    step="0.0001"
                    min="-90"
                    max="90"
                    value={latitude}
                    onChange={(e) => {
                      setLatitude(e.target.value);
                      if (validationErrors.latitude) {
                        setValidationErrors((prev) => ({ ...prev, latitude: "" }));
                      }
                    }}
                    className={`w-full rounded-lg border py-2.5 pl-10 pr-3.5 text-sm transition focus:outline-none focus:ring-1 ${
                      validationErrors.latitude
                        ? "border-red-500 bg-red-50/20 text-red-900 focus:border-red-500 focus:ring-red-500"
                        : "border-slate-300 bg-white text-slate-800 focus:border-[#153F6B] focus:ring-[#153F6B]"
                    }`}
                    placeholder="13.0827"
                    required
                  />
                </div>
                {validationErrors.latitude && (
                  <p className="mt-1 text-xs text-red-600">{validationErrors.latitude}</p>
                )}
              </div>

              {/* Longitude */}
              <div>
                <label
                  htmlFor="birth-lon"
                  className="mb-1.5 block text-xs font-bold uppercase tracking-wider text-slate-600"
                >
                  Longitude (°E / -W) <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                    <Compass className="h-4 w-4" />
                  </div>
                  <input
                    id="birth-lon"
                    type="number"
                    step="0.0001"
                    min="-180"
                    max="180"
                    value={longitude}
                    onChange={(e) => {
                      setLongitude(e.target.value);
                      if (validationErrors.longitude) {
                        setValidationErrors((prev) => ({ ...prev, longitude: "" }));
                      }
                    }}
                    className={`w-full rounded-lg border py-2.5 pl-10 pr-3.5 text-sm transition focus:outline-none focus:ring-1 ${
                      validationErrors.longitude
                        ? "border-red-500 bg-red-50/20 text-red-900 focus:border-red-500 focus:ring-red-500"
                        : "border-slate-300 bg-white text-slate-800 focus:border-[#153F6B] focus:ring-[#153F6B]"
                    }`}
                    placeholder="80.2707"
                    required
                  />
                </div>
                {validationErrors.longitude && (
                  <p className="mt-1 text-xs text-red-600">{validationErrors.longitude}</p>
                )}
              </div>

              {/* Location Name (Label only) */}
              <div>
                <label
                  htmlFor="birth-place"
                  className="mb-1.5 block text-xs font-bold uppercase tracking-wider text-slate-600"
                >
                  Location Label (Optional)
                </label>
                <input
                  id="birth-place"
                  type="text"
                  value={locationName}
                  onChange={(e) => setLocationName(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-800 transition focus:border-[#153F6B] focus:outline-none focus:ring-1 focus:ring-[#153F6B]"
                  placeholder="e.g. Chennai, India"
                />
                <p className="mt-1 text-[11px] text-slate-500">
                  Label only. Exact coordinates above drive calculations.
                </p>
              </div>
            </div>

            {/* Advanced Sensitivity & Timing Parameters */}
            <div className="mt-6 rounded-xl border border-slate-200 bg-slate-50/70 p-5">
              <div className="flex items-center gap-2 font-semibold text-slate-800">
                <Sliders className="h-4 w-4 text-[#B4872B]" />
                <span className="text-sm">Birth-Time Sensitivity & Timing Window Bounds</span>
              </div>

              <div className="mt-4 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {/* Birth Time Uncertainty */}
                <div>
                  <div className="flex items-center justify-between">
                    <label
                      htmlFor="uncertainty-input"
                      className="text-xs font-bold uppercase tracking-wider text-slate-600"
                    >
                      Uncertainty (±Seconds)
                    </label>
                    <span className="font-mono text-xs font-bold text-[#153F6B]">
                      ±{uncertaintySeconds}s ({(uncertaintySeconds / 60).toFixed(1)}m)
                    </span>
                  </div>
                  <input
                    id="uncertainty-input"
                    type="range"
                    min="0"
                    max="1800"
                    step="15"
                    value={uncertaintySeconds}
                    onChange={(e) => setUncertaintySeconds(parseFloat(e.target.value))}
                    className="mt-2 h-2 w-full cursor-pointer appearance-none rounded-lg bg-slate-200 accent-[#153F6B]"
                  />
                  <div className="mt-2 flex flex-wrap gap-1">
                    {UNCERTAINTY_PRESETS.map((p) => (
                      <button
                        key={p.value}
                        type="button"
                        onClick={() => setUncertaintySeconds(p.value)}
                        className={`rounded px-1.5 py-0.5 text-[10px] transition ${
                          uncertaintySeconds === p.value
                            ? "bg-[#153F6B] text-white"
                            : "bg-white text-slate-600 hover:bg-slate-200"
                        }`}
                      >
                        {p.label}
                      </button>
                    ))}
                  </div>
                  {validationErrors.uncertaintySeconds && (
                    <p className="mt-1 text-xs text-red-600">
                      {validationErrors.uncertaintySeconds}
                    </p>
                  )}
                </div>

                {/* Search Start Year */}
                <div>
                  <label
                    htmlFor="start-year"
                    className="mb-1.5 block text-xs font-bold uppercase tracking-wider text-slate-600"
                  >
                    Timing Scan: Start Year
                  </label>
                  <input
                    id="start-year"
                    type="number"
                    min="1900"
                    max="2100"
                    value={startYear}
                    onChange={(e) => setStartYear(e.target.value)}
                    className="w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-sm text-slate-800 transition focus:border-[#153F6B] focus:outline-none focus:ring-1 focus:ring-[#153F6B]"
                    placeholder="2024"
                  />
                  <p className="mt-1 text-[11px] text-slate-500">
                    Defaults to age 18 if unspecified.
                  </p>
                </div>

                {/* Search End Year */}
                <div>
                  <label
                    htmlFor="end-year"
                    className="mb-1.5 block text-xs font-bold uppercase tracking-wider text-slate-600"
                  >
                    Timing Scan: End Year
                  </label>
                  <input
                    id="end-year"
                    type="number"
                    min="1900"
                    max="2100"
                    value={endYear}
                    onChange={(e) => setEndYear(e.target.value)}
                    className="w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-sm text-slate-800 transition focus:border-[#153F6B] focus:outline-none focus:ring-1 focus:ring-[#153F6B]"
                    placeholder="2032"
                  />
                  <p className="mt-1 text-[11px] text-slate-500">
                    Must be ≥ Start Year (defaults to Start + 10).
                  </p>
                </div>

                {/* Force Timing Scan Option */}
                <div className="flex items-start gap-2.5 pt-3 sm:col-span-2 lg:col-span-3 border-t border-slate-200/60 mt-1">
                  <input
                    type="checkbox"
                    id="force-timing-checkbox"
                    checked={forceTimingScan}
                    onChange={(e) => setForceTimingScan(e.target.checked)}
                    className="mt-0.5 h-4 w-4 rounded border-slate-300 text-[#153F6B] focus:ring-[#153F6B] cursor-pointer"
                  />
                  <div>
                    <label htmlFor="force-timing-checkbox" className="text-xs font-semibold text-slate-800 cursor-pointer">
                      Enable Exploratory Timing Scan
                    </label>
                    <p className="text-[11px] text-slate-500">
                      Evaluates Vimshottari Dasa-Bhukti and Jupiter-Saturn double transit confluence windows even if marriage promise is INDETERMINATE or delayed.
                    </p>
                  </div>
                </div>
              </div>
              {validationErrors.years && (
                <p className="mt-2 text-xs text-red-600">{validationErrors.years}</p>
              )}
            </div>

            {/* Error Banner */}
            {apiError && (
              <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-900 shadow-sm">
                <div className="flex items-start gap-3">
                  <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-600" />
                  <div className="flex-1">
                    <p className="font-semibold text-red-950">Calculation Request Error</p>
                    <p className="mt-1 text-xs text-red-800 sm:text-sm">{apiError}</p>
                    {apiErrorStatus === 401 && (
                      <div className="mt-3">
                        <Link
                          href="/login"
                          className="inline-flex items-center gap-1.5 rounded-lg bg-[#153F6B] px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-[#1a4b7f]"
                        >
                          Go to Sign In <ArrowRight className="h-3.5 w-3.5" />
                        </Link>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="mt-8 flex flex-col items-center justify-end gap-3 sm:flex-row">
              {response && (
                <button
                  type="button"
                  onClick={handleReset}
                  className="w-full rounded-xl border border-slate-300 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 shadow-sm hover:bg-slate-50 sm:w-auto"
                >
                  Clear / Reset
                </button>
              )}

              <button
                type="submit"
                disabled={loading}
                className="flex w-full items-center justify-center gap-2 rounded-xl bg-[#153F6B] px-7 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-[#1a4b7f] disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
              >
                {loading ? (
                  <>
                    <RefreshCw className="h-4 w-4 animate-spin" />
                    <span>Evaluating Rules & Ephemeris...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4 text-[#FAF2DE]" />
                    <span>Run Unified Prediction Analysis</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Results Section */}
        {response && (
          <div id="results-section" className="mt-12 space-y-8 max-w-full min-w-0">
            <div className="flex items-center justify-between border-b border-slate-200 pb-4">
              <div>
                <h2 className="text-xl font-bold text-[#153F6B] sm:text-2xl">
                  Astrological Evaluation Dashboard
                </h2>
                <p className="text-xs text-slate-500 sm:text-sm">
                  Evaluated with continuous Placidus sensitivity mesh and Vimshottari dasha timing.
                </p>
              </div>
              <button
                type="button"
                onClick={handleReset}
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#153F6B] hover:underline"
              >
                <RefreshCw className="h-3.5 w-3.5" /> Run Another Analysis
              </button>
            </div>

            {/* ------------------------------------------------------------- */}
            {/* Section A: Overall Event Verdict                              */}
            {/* ------------------------------------------------------------- */}
            <div
              className={`rounded-2xl border p-6 shadow-sm sm:p-8 overflow-hidden max-w-full ${
                response.final_verdict === "EVENT_INDICATED"
                  ? "border-emerald-200 bg-emerald-50/50"
                  : response.final_verdict === "EVENT_NOT_INDICATED"
                  ? "border-rose-200 bg-rose-50/50"
                  : "border-amber-200 bg-amber-50/50"
              }`}
            >
              <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div className="flex items-start gap-4">
                  <div
                    className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl shadow-sm ${
                      response.final_verdict === "EVENT_INDICATED"
                        ? "bg-emerald-600 text-white"
                        : response.final_verdict === "EVENT_NOT_INDICATED"
                        ? "bg-rose-600 text-white"
                        : "bg-amber-600 text-white"
                    }`}
                  >
                    {response.final_verdict === "EVENT_INDICATED" && (
                      <CheckCircle2 className="h-7 w-7" />
                    )}
                    {response.final_verdict === "EVENT_NOT_INDICATED" && (
                      <AlertCircle className="h-7 w-7" />
                    )}
                    {response.final_verdict === "INDETERMINATE" && (
                      <AlertTriangle className="h-7 w-7" />
                    )}
                  </div>
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                        Master Reconciliation Verdict
                      </span>
                      <span className="rounded bg-white/80 px-2 py-0.5 text-[10px] font-mono text-slate-600 shadow-xs">
                        {response.reconciliation_rule_id}
                      </span>
                    </div>

                    <h3
                      className={`mt-1 text-2xl font-extrabold tracking-tight sm:text-3xl ${
                        response.final_verdict === "EVENT_INDICATED"
                          ? "text-emerald-950"
                          : response.final_verdict === "EVENT_NOT_INDICATED"
                          ? "text-rose-950"
                          : "text-amber-950"
                      }`}
                    >
                      {response.final_verdict === "EVENT_INDICATED" && "EVENT INDICATED — MARRIAGE PROMISED"}
                      {response.final_verdict === "EVENT_NOT_INDICATED" && "EVENT NOT INDICATED — MARRIAGE DENIED"}
                      {response.final_verdict === "INDETERMINATE" && "INDETERMINATE — UNRESOLVED VERDICT"}
                    </h3>

                    <p className="mt-1 text-xs text-slate-700 sm:text-sm">
                      {response.final_verdict === "EVENT_INDICATED" &&
                        "Both KP cuspal sub-lord significations and Vedic Parashari conditions concordantly support marriage fruition."}
                      {response.final_verdict === "EVENT_NOT_INDICATED" &&
                        "Both KP and Vedic systems concordantly indicate denial under the deterministic rulebook."}
                      {response.final_verdict === "INDETERMINATE" &&
                        "The analysis yields an indeterminate outcome due to inter-tradition conflict, birth-time sensitivity, or calculation error."}
                    </p>
                  </div>
                </div>

                <div className="rounded-xl border border-white/60 bg-white/80 p-3 text-right text-xs shadow-xs md:max-w-xs">
                  <p className="font-semibold text-slate-800">Rule Provenance</p>
                  <p className="font-mono text-[11px] text-slate-600">
                    {response.reconciliation_provenance}
                  </p>
                  <p className="mt-1 text-[10px] text-slate-500">
                    Deterministic inter-tradition synthesis policy
                  </p>
                </div>
              </div>

              {/* Sensitivity Warning Banner if chart is sensitive */}
              {response.birth_time_sensitivity.is_sensitive && (
                <div className="mt-5 rounded-xl border border-amber-300 bg-white/90 p-3.5 text-xs text-amber-900 shadow-xs">
                  <div className="flex items-start gap-2.5">
                    <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
                    <div>
                      <p className="font-bold text-amber-950">
                        Birth-Time Sensitivity Discontinuity Warning
                      </p>
                      <p className="mt-0.5 text-amber-900/90 leading-relaxed">
                        The Placidus 7th cuspal sub-lord traverses an analytical boundary within your
                        entered uncertainty window (±{response.birth_time_sensitivity.uncertainty_seconds}s).
                        The resulting natal verdict is sensitive to birth-time precision. See the
                        sensitivity scan section below for exact crossing timings.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* ------------------------------------------------------------- */}
            {/* Section B & C: Dual Tradition Comparison (KP + Vedic)         */}
            {/* ------------------------------------------------------------- */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              {/* KP Analysis Card */}
              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm overflow-hidden max-w-full">
                <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                  <div className="flex items-center gap-2.5">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#FAF2DE] text-[#B4872B]">
                      <Compass className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="font-bold text-[#153F6B]">Krishnamurti Paddhati (KP)</h3>
                      <p className="text-[11px] text-slate-500">Placidus Cusps + Krishnamurti Ayanamsa</p>
                    </div>
                  </div>
                  <span
                    className={`rounded-full px-2.5 py-1 text-xs font-bold ${
                      response.kp_promise.verdict === "PROMISED"
                        ? "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-600/20"
                        : response.kp_promise.verdict === "DENIED"
                        ? "bg-rose-50 text-rose-700 ring-1 ring-rose-600/20"
                        : "bg-amber-50 text-amber-700 ring-1 ring-amber-600/20"
                    }`}
                  >
                    {response.kp_promise.verdict}
                  </span>
                </div>

                <div className="mt-4 space-y-4 text-xs">
                  {/* CSL and Star Lord */}
                  <div className="grid grid-cols-2 gap-3 rounded-xl bg-slate-50 p-3.5">
                    <div>
                      <p className="text-[11px] font-medium text-slate-500">7th Cusp Sub-Lord (CSL)</p>
                      <div className="mt-1 flex items-center gap-1.5">
                        <span className="font-bold text-slate-900 sm:text-sm">
                          {response.kp_promise.cuspal_sub_lord_7}
                        </span>
                        {response.kp_promise.is_csl_retrograde && (
                          <span className="rounded bg-red-100 px-1 text-[10px] font-semibold text-red-700">
                            (R)
                          </span>
                        )}
                      </div>
                    </div>
                    <div>
                      <p className="text-[11px] font-medium text-slate-500">Star-Lord of 7th CSL</p>
                      <div className="mt-1 flex items-center gap-1.5">
                        <span className="font-bold text-slate-900 sm:text-sm">
                          {response.kp_promise.star_lord_of_csl}
                        </span>
                        {response.kp_promise.is_star_lord_retrograde && (
                          <span className="rounded bg-red-100 px-1 text-[10px] font-semibold text-red-700">
                            (R)
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Significations */}
                  <div className="space-y-2">
                    <div>
                      <span className="text-[11px] font-medium text-slate-500">
                        Star-Lord Significations (Primary Promise Vector):
                      </span>
                      <div className="mt-1 flex flex-wrap gap-1.5">
                        {response.kp_promise.star_lord_significations.length === 0 ? (
                          <span className="text-slate-400 italic">None signified</span>
                        ) : (
                          response.kp_promise.star_lord_significations.map((h) => (
                            <span
                              key={h}
                              className={`rounded px-2 py-0.5 font-mono text-[11px] font-bold ${
                                [2, 7, 11].includes(h)
                                  ? "bg-emerald-100 text-emerald-800"
                                  : [1, 6, 10].includes(h)
                                  ? "bg-rose-100 text-rose-800"
                                  : "bg-slate-100 text-slate-700"
                              }`}
                            >
                              H{h}
                            </span>
                          ))
                        )}
                      </div>
                    </div>

                    <div>
                      <span className="text-[11px] font-medium text-slate-500">
                        Sub-Lord Significations (Fruition / Denial Gate):
                      </span>
                      <div className="mt-1 flex flex-wrap gap-1.5">
                        {response.kp_promise.sub_lord_significations.length === 0 ? (
                          <span className="text-slate-400 italic">None signified</span>
                        ) : (
                          response.kp_promise.sub_lord_significations.map((h) => (
                            <span
                              key={h}
                              className={`rounded px-2 py-0.5 font-mono text-[11px] font-bold ${
                                [2, 7, 11].includes(h)
                                  ? "bg-emerald-100 text-emerald-800"
                                  : [1, 6, 10].includes(h)
                                  ? "bg-rose-100 text-rose-800"
                                  : "bg-slate-100 text-slate-700"
                              }`}
                            >
                              H{h}
                            </span>
                          ))
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Rule & Explanation */}
                  <div className="rounded-xl border border-slate-100 bg-slate-50/50 p-3">
                    <div className="flex items-center justify-between text-[11px] text-slate-500">
                      <span>
                        Rule: <strong className="text-slate-700">{response.kp_promise.rule_id}</strong>
                      </span>
                      <span className="font-mono text-[10px]">
                        [{response.kp_promise.rule_provenance}]
                      </span>
                    </div>
                    <p className="mt-1.5 leading-relaxed text-slate-700">
                      {response.kp_promise.explanation}
                    </p>
                    <div className="mt-2 text-[10px] text-slate-500">
                      Internal Modifier:{" "}
                      <span className="font-mono font-medium text-[#153F6B]">
                        {response.kp_promise.internal_modifier}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Vedic Analysis Card */}
              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm overflow-hidden max-w-full">
                <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                  <div className="flex items-center gap-2.5">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50 text-[#153F6B]">
                      <Layers className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="font-bold text-[#153F6B]">Parashari Vedic Astrology</h3>
                      <p className="text-[11px] text-slate-500">D1 Rasi + D9 Navamsa (Whole Sign, Lahiri)</p>
                    </div>
                  </div>
                  <span
                    className={`rounded-full px-2.5 py-1 text-xs font-bold ${
                      response.vedic_promise.verdict === "PROMISED"
                        ? "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-600/20"
                        : response.vedic_promise.verdict === "DENIED"
                        ? "bg-rose-50 text-rose-700 ring-1 ring-rose-600/20"
                        : "bg-amber-50 text-amber-700 ring-1 ring-amber-600/20"
                    }`}
                  >
                    {response.vedic_promise.verdict}
                  </span>
                </div>

                <div className="mt-4 space-y-4 text-xs">
                  {/* 7th Lord D1 & Venus */}
                  <div className="grid grid-cols-2 gap-3 rounded-xl bg-slate-50 p-3.5">
                    <div>
                      <p className="text-[11px] font-medium text-slate-500">7th Lord (D1 Rasi)</p>
                      <p className="mt-1 font-bold text-slate-900 sm:text-sm">
                        {response.vedic_promise.seventh_lord_d1}{" "}
                        <span className="text-xs font-normal text-slate-500">
                          (in H{response.vedic_promise.seventh_lord_house_d1},{" "}
                          {response.vedic_promise.seventh_house_sign_d1})
                        </span>
                      </p>
                    </div>
                    <div>
                      <p className="text-[11px] font-medium text-slate-500">Kuja Dosha Status</p>
                      <div className="mt-1">
                        {response.vedic_promise.kuja_dosha_present ? (
                          response.vedic_promise.kuja_dosha_cancelled ? (
                            <span className="rounded bg-emerald-100 px-1.5 py-0.5 text-[11px] font-semibold text-emerald-800">
                              Active (Cancelled)
                            </span>
                          ) : (
                            <span className="rounded bg-rose-100 px-1.5 py-0.5 text-[11px] font-semibold text-rose-800">
                              Active (Uncancelled)
                            </span>
                          )
                        ) : (
                          <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[11px] font-medium text-slate-700">
                            Absent
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Venus Affliction Metrics */}
                  <div>
                    <span className="text-[11px] font-medium text-slate-500">
                      Karaka (Venus) Dignity & Placements:
                    </span>
                    <div className="mt-1.5 grid grid-cols-3 gap-2">
                      <div className="rounded-lg border border-slate-100 bg-slate-50/50 p-2 text-center">
                        <span className="block text-[10px] text-slate-500">Combustion</span>
                        <span
                          className={`mt-0.5 block font-semibold ${
                            response.vedic_promise.venus_combustion
                              ? "text-rose-600"
                              : "text-emerald-700"
                          }`}
                        >
                          {response.vedic_promise.venus_combustion ? "Combust" : "Clear"}
                        </span>
                      </div>
                      <div className="rounded-lg border border-slate-100 bg-slate-50/50 p-2 text-center">
                        <span className="block text-[10px] text-slate-500">Debilitation</span>
                        <span
                          className={`mt-0.5 block font-semibold ${
                            response.vedic_promise.venus_debilitation
                              ? "text-rose-600"
                              : "text-emerald-700"
                          }`}
                        >
                          {response.vedic_promise.venus_debilitation ? "Debilitated" : "Dignified"}
                        </span>
                      </div>
                      <div className="rounded-lg border border-slate-100 bg-slate-50/50 p-2 text-center">
                        <span className="block text-[10px] text-slate-500">Dusthana</span>
                        <span
                          className={`mt-0.5 block font-semibold ${
                            response.vedic_promise.venus_dusthana
                              ? "text-rose-600"
                              : "text-emerald-700"
                          }`}
                        >
                          {response.vedic_promise.venus_dusthana ? "6/8/12" : "Favorable"}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* D9 Navamsa Indicators */}
                  <div className="rounded-xl border border-slate-100 bg-slate-50/50 p-3">
                    <div className="flex items-center justify-between text-[11px] text-slate-600">
                      <span>
                        D9 7th Sign: <strong>{response.vedic_promise.d9_seventh_sign}</strong>
                      </span>
                      <span>
                        D9 7th Lord: <strong>{response.vedic_promise.d9_seventh_lord}</strong>
                      </span>
                      <span>
                        D9 Venus: <strong>{response.vedic_promise.d9_venus_sign}</strong>
                      </span>
                    </div>
                    <div className="mt-2 flex items-center justify-between text-[11px]">
                      <span className="text-slate-500">
                        Compound Denial Gates Met:{" "}
                        <strong className="text-slate-800">
                          {response.vedic_promise.compound_denial_gates_met} / 3
                        </strong>
                      </span>
                      <span
                        className={`font-semibold ${
                          response.vedic_promise.d9_afflicted
                            ? "text-amber-700"
                            : "text-emerald-700"
                        }`}
                      >
                        {response.vedic_promise.d9_afflicted ? "D9 Afflicted" : "D9 Unafflicted"}
                      </span>
                    </div>
                  </div>

                  {/* Rule & Explanation */}
                  <div className="rounded-xl border border-slate-100 bg-slate-50/50 p-3">
                    <div className="flex items-center justify-between text-[11px] text-slate-500">
                      <span>
                        Rule: <strong className="text-slate-700">{response.vedic_promise.rule_id}</strong>
                      </span>
                      <span className="font-mono text-[10px]">
                        [{response.vedic_promise.rule_provenance}]
                      </span>
                    </div>
                    <p className="mt-1.5 leading-relaxed text-slate-700">
                      {response.vedic_promise.explanation}
                    </p>
                    <div className="mt-2 text-[10px] text-slate-500">
                      Internal Modifier:{" "}
                      <span className="font-mono font-medium text-[#153F6B]">
                        {response.vedic_promise.internal_modifier}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* ------------------------------------------------------------- */}
            {/* Section D: Birth-Time Sensitivity Diagnostics                 */}
            {/* ------------------------------------------------------------- */}
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm overflow-hidden max-w-full">
              <div className="flex flex-col gap-2 border-b border-slate-100 pb-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 text-indigo-700">
                    <Clock className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-[#153F6B]">
                      Continuous Placidus Cusp Birth-Time Sensitivity Scan
                    </h3>
                    <p className="text-[11px] text-slate-500">
                      Adaptive subdivision mesh across [τ₀ - Δt, τ₀ + Δt] uncertainty interval
                    </p>
                  </div>
                </div>

                <span
                  className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-bold ${
                    response.birth_time_sensitivity.scan_status === "STABLE"
                      ? "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-600/20"
                      : response.birth_time_sensitivity.scan_status === "BOUNDARY_CROSSING_DETECTED"
                      ? "bg-amber-50 text-amber-700 ring-1 ring-amber-600/20"
                      : "bg-rose-50 text-rose-700 ring-1 ring-rose-600/20"
                  }`}
                >
                  Status: {response.birth_time_sensitivity.scan_status}
                </span>
              </div>

              <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <div className="rounded-xl bg-slate-50 p-3.5 text-xs">
                  <span className="text-[11px] text-slate-500">Nominal 7th CSL</span>
                  <p className="mt-1 font-bold text-slate-900 sm:text-base">
                    {response.birth_time_sensitivity.nominal_sub_lord}
                  </p>
                </div>
                <div className="rounded-xl bg-slate-50 p-3.5 text-xs">
                  <span className="text-[11px] text-slate-500">Nominal 7th Cusp Longitude</span>
                  <p className="mt-1 font-mono font-bold text-slate-900 sm:text-base">
                    {response.birth_time_sensitivity.nominal_cusp_degree.toFixed(4)}°
                  </p>
                </div>
                <div className="rounded-xl bg-slate-50 p-3.5 text-xs">
                  <span className="text-[11px] text-slate-500">Uncertainty Evaluated</span>
                  <p className="mt-1 font-bold text-[#153F6B] sm:text-base">
                    ±{response.birth_time_sensitivity.uncertainty_seconds}s (
                    {(response.birth_time_sensitivity.uncertainty_seconds / 60).toFixed(1)}m)
                  </p>
                </div>
                <div className="rounded-xl bg-slate-50 p-3.5 text-xs">
                  <span className="text-[11px] text-slate-500">Crossings Detected</span>
                  <p
                    className={`mt-1 font-bold sm:text-base ${
                      response.birth_time_sensitivity.crossings.length > 0
                        ? "text-amber-700"
                        : "text-emerald-700"
                    }`}
                  >
                    {response.birth_time_sensitivity.crossings.length} Transition
                    {response.birth_time_sensitivity.crossings.length === 1 ? "" : "s"}
                  </p>
                </div>
              </div>

              {/* Crossings List / Table */}
              <div className="mt-6">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600">
                  Detected Sub-Lord Boundary Crossings
                </h4>
                {response.birth_time_sensitivity.crossings.length === 0 ? (
                  <div className="mt-2 rounded-xl border border-slate-100 bg-slate-50/50 p-4 text-xs text-slate-600">
                    <p className="leading-relaxed">
                      ✓ No sub-lord transitions occur within the evaluated ±
                      {response.birth_time_sensitivity.uncertainty_seconds}s uncertainty window. The 7th
                      cuspal sub-lord remains stably identified as{" "}
                      <strong>{response.birth_time_sensitivity.nominal_sub_lord}</strong>.
                    </p>
                  </div>
                ) : (
                  <div className="mt-2 w-full max-w-full overflow-x-auto rounded-xl border border-slate-200">
                    <table className="w-full min-w-[500px] text-left text-xs">
                      <thead className="border-b border-slate-200 bg-slate-50 text-[11px] font-semibold text-slate-600">
                        <tr>
                          <th className="px-3.5 py-2.5">Time Offset (Δt)</th>
                          <th className="px-3.5 py-2.5">Transition Timestamp (UTC)</th>
                          <th className="px-3.5 py-2.5">Boundary Longitude</th>
                          <th className="px-3.5 py-2.5">Sub-Lord Shift</th>
                          <th className="px-3.5 py-2.5">Verdict Impact</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 text-slate-700">
                        {response.birth_time_sensitivity.crossings.map((c, idx) => (
                          <tr key={idx} className="hover:bg-slate-50/80">
                            <td className="px-3.5 py-2.5 font-mono font-bold text-[#153F6B]">
                              {c.delta_seconds >= 0 ? `+${c.delta_seconds.toFixed(1)}s` : `${c.delta_seconds.toFixed(1)}s`}
                            </td>
                            <td className="px-3.5 py-2.5 font-mono text-slate-600">
                              {c.crossing_time_iso}
                            </td>
                            <td className="px-3.5 py-2.5 font-mono">
                              {c.boundary_longitude_deg.toFixed(4)}°
                            </td>
                            <td className="px-3.5 py-2.5 font-medium">
                              {c.from_sub_lord} → <strong className="text-slate-900">{c.to_sub_lord}</strong>
                            </td>
                            <td className="px-3.5 py-2.5">
                              <span
                                className={`rounded px-2 py-0.5 text-[10px] font-bold ${
                                  c.verdict_impact === "VERDICT_PRESERVED"
                                    ? "bg-emerald-100 text-emerald-800"
                                    : c.verdict_impact === "VERDICT_FLIPPED"
                                    ? "bg-rose-100 text-rose-800"
                                    : "bg-slate-100 text-slate-800"
                                }`}
                              >
                                {c.verdict_impact}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              {/* Scientific Disclaimer & Tolerances */}
              <div className="mt-4 rounded-xl border border-slate-100 bg-slate-50/60 p-3.5 text-[11px] text-slate-500">
                <p>
                  <strong>Numerical Scan Guarantee:</strong> Root bracketing time tolerance:{" "}
                  {response.birth_time_sensitivity.tolerance_guarantee.time_tolerance_seconds}s,
                  longitude tolerance:{" "}
                  {response.birth_time_sensitivity.tolerance_guarantee.longitude_tolerance_deg}°.{" "}
                  {response.birth_time_sensitivity.tolerance_guarantee.disclaimer}
                </p>
                <p className="mt-1 text-slate-400">
                  Note: The scan detects mathematical KP sub-lord boundary transitions under Placidus semi-arc
                  motion, but cannot guarantee detection of all unmodeled real-world observational variations.
                </p>
              </div>
            </div>

            {/* ------------------------------------------------------------- */}
            {/* Section E: Vimshottari Dasha & Transit Timing Windows         */}
            {/* ------------------------------------------------------------- */}
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm overflow-hidden max-w-full">
              <div className="flex flex-col gap-2 border-b border-slate-100 pb-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-amber-50 text-amber-700">
                    <Calendar className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-[#153F6B]">
                      Vimshottari Dasha & Transit Timing Evaluation
                    </h3>
                    <p className="text-[11px] text-slate-500">
                      Evaluated for Mahadasha/Antardasha lords and Jupiter-Saturn double transit confluence
                    </p>
                  </div>
                </div>

                <span
                  className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-bold ${
                    response.timing_status === "WINDOW_FOUND"
                      ? "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-600/20"
                      : response.timing_status === "NO_WINDOW_IN_RANGE"
                      ? "bg-amber-50 text-amber-700 ring-1 ring-amber-600/20"
                      : "bg-slate-100 text-slate-700 ring-1 ring-slate-600/20"
                  }`}
                >
                  Timing Status: {response.timing_status}
                </span>
              </div>

              <div className="mt-5">
                {/* Case 1: Window Found */}
                {response.timing_status === "WINDOW_FOUND" && response.timing?.best_window && (
                  <div className="rounded-xl border border-emerald-200 bg-emerald-50/40 p-5">
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-900">
                          Prime Confluence Timing Window
                        </span>
                        <h4 className="mt-0.5 text-xl font-extrabold text-emerald-950 sm:text-2xl">
                          {response.timing.best_window.start_date} to{" "}
                          {response.timing.best_window.end_date}
                        </h4>
                        <p className="mt-1 text-xs text-emerald-800">
                          Evaluated period between {response.timing.search_start_date} and{" "}
                          {response.timing.search_end_date}.
                        </p>
                      </div>

                      {/* Astrological Confluence Score / Timing Alignment Index */}
                      <div className="rounded-xl border border-emerald-200 bg-white p-4 shadow-xs sm:w-72">
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-bold text-slate-700">
                            Astrological Confluence Score
                          </span>
                          <span className="font-mono font-bold text-[#153F6B]">
                            {response.timing.best_window.confidence_score.toFixed(2)} / 1.00
                          </span>
                        </div>
                        {/* Meter */}
                        <div className="mt-2 h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
                          <div
                            className="h-full rounded-full bg-[#153F6B] transition-all"
                            style={{
                              width: `${Math.round(
                                response.timing.best_window.confidence_score * 100
                              )}%`,
                            }}
                          />
                        </div>
                        <p className="mt-2 text-[10px] leading-tight text-slate-500">
                          This score represents agreement between the configured astrological timing
                          factors. It is not a statistically validated probability of marriage.
                        </p>
                      </div>
                    </div>

                    {/* Dasha and Transit Details */}
                    <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-3">
                      <div className="rounded-lg bg-white p-3 text-xs shadow-xs">
                        <span className="text-[11px] text-slate-500">Dasha Periods</span>
                        <p className="mt-0.5 font-bold text-slate-900">
                          {response.timing.best_window.mahadasha} -{" "}
                          {response.timing.best_window.antardasha}
                          {response.timing.best_window.pratyantardasha &&
                            ` - ${response.timing.best_window.pratyantardasha}`}
                        </p>
                      </div>

                      <div className="rounded-lg bg-white p-3 text-xs shadow-xs">
                        <span className="text-[11px] text-slate-500">Double Transit Active</span>
                        <p
                          className={`mt-0.5 font-bold ${
                            response.timing.best_window.double_transit_active
                              ? "text-emerald-700"
                              : "text-slate-600"
                          }`}
                        >
                          {response.timing.best_window.double_transit_active
                            ? "✓ Jupiter & Saturn Simultaneous Aspect"
                            : "No Simultaneous Alignment"}
                        </p>
                      </div>

                      <div className="rounded-lg bg-white p-3 text-xs shadow-xs">
                        <span className="text-[11px] text-slate-500">KP Level A/B Confluence</span>
                        <p
                          className={`mt-0.5 font-bold ${
                            response.timing.best_window.kp_significator_confluence
                              ? "text-emerald-700"
                              : "text-slate-600"
                          }`}
                        >
                          {response.timing.best_window.kp_significator_confluence
                            ? "✓ Primary Significators Active"
                            : "Partial Significator Support"}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Case 2: No Window Found in Range */}
                {response.timing_status === "NO_WINDOW_IN_RANGE" && (
                  <div className="rounded-xl border border-amber-200 bg-amber-50/50 p-4 text-xs text-amber-900">
                    <p className="font-semibold text-amber-950">
                      No Qualified Window Found in Scanned Range ({startYear} – {endYear})
                    </p>
                    <p className="mt-1 leading-relaxed text-amber-900/90">
                      Neither the Dasha lord alignment nor the Jupiter-Saturn double transit met the
                      confluence threshold within the scanned years. <strong>Important:</strong> An
                      absent timing window does not denote marriage denial; the event may fructify outside
                      the evaluated interval. You may widen the start and end year parameters above to
                      scan other decades.
                    </p>
                  </div>
                )}

                {/* Case 3: Timing Not Determinable */}
                {response.timing_status === "TIMING_NOT_DETERMINABLE" && (
                  <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs text-slate-700">
                    <p className="font-semibold text-slate-900">Timing Calculation Incomplete</p>
                    <p className="mt-1 leading-relaxed text-slate-600">
                      Timing could not be determined due to computational constraints or missing
                      astronomical parameters. <strong>Notice:</strong> Natal marriage promise
                      indications remain fully valid; decoupled timing failures do not invalidate natal
                      concordance.
                    </p>
                  </div>
                )}

                {/* Case 4: Not Evaluated */}
                {response.timing_status === "NOT_EVALUATED" && (
                  <div className="rounded-xl border border-amber-200 bg-amber-50/60 p-5 text-xs text-slate-700">
                    <div className="flex items-start gap-3">
                      <AlertTriangle className="h-5 w-5 text-amber-600 shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <p className="font-bold text-sm text-amber-900">Timing Scan Not Evaluated (Gatekeeper Active)</p>
                        <p className="mt-1 leading-relaxed text-slate-600">
                          By default, the timing scan is triggered exclusively when both KP and Vedic traditions concordantly
                          support marriage promise (<span className="font-semibold text-emerald-800">EVENT_INDICATED</span>).
                          For charts marked <span className="font-semibold text-amber-800">INDETERMINATE</span> (such as mixed significations, 8th lord influences, or delay indicators),
                          timing computation is intentionally bypassed to avoid false temporal projections.
                        </p>
                        <div className="mt-4 flex flex-wrap items-center gap-3">
                          <button
                            type="button"
                            onClick={() => {
                              setForceTimingScan(true);
                              handleSubmit(undefined, true);
                            }}
                            className="inline-flex items-center gap-2 rounded-lg bg-[#153F6B] px-4 py-2 text-xs font-bold text-white shadow-sm hover:bg-[#102e4e] transition-colors cursor-pointer"
                          >
                            <Sparkles className="h-3.5 w-3.5" />
                            Run Exploratory Timing Scan Anyway
                          </button>
                          <span className="text-[11px] text-slate-500">
                            Evaluates Dasha-Bhukti and Jupiter-Saturn double transit confluence across your selected year range.
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* ------------------------------------------------------------- */}
            {/* Section F: Calculation Metadata & Ephemeris Audit             */}
            {/* ------------------------------------------------------------- */}
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm overflow-hidden max-w-full">
              <button
                type="button"
                onClick={() => setShowMetadata(!showMetadata)}
                className="flex w-full items-center justify-between text-left"
              >
                <div className="flex items-center gap-2.5">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-100 text-slate-600">
                    <Database className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-[#153F6B]">
                      Calculation Metadata & Ayanamsa Audit
                    </h3>
                    <p className="text-[11px] text-slate-500">
                      Astronomical coordinates, Julian Day UT1, and dual ayanamsa provenance
                    </p>
                  </div>
                </div>
                <div className="text-slate-400">
                  {showMetadata ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
                </div>
              </button>

              {showMetadata && (
                <div className="mt-6 space-y-4 border-t border-slate-100 pt-5 text-xs">
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    <div className="rounded-lg bg-slate-50 p-3">
                      <span className="text-[11px] text-slate-500">Birth Datetime (UTC)</span>
                      <p className="mt-0.5 font-mono font-bold text-slate-800">
                        {response.metadata.birth_utc_iso || "N/A"}
                      </p>
                    </div>

                    <div className="rounded-lg bg-slate-50 p-3">
                      <span className="text-[11px] text-slate-500">Julian Day UT1</span>
                      <p className="mt-0.5 font-mono font-bold text-slate-800">
                        {response.metadata.julian_day_ut1.toFixed(6)}
                      </p>
                    </div>

                    <div className="rounded-lg bg-slate-50 p-3">
                      <span className="text-[11px] text-slate-500">Local Timezone & Offset</span>
                      <p className="mt-0.5 font-bold text-slate-800">
                        {response.metadata.local_timezone} (UTC{" "}
                        {(response.metadata.utc_offset_hours || 0) >= 0 ? "+" : ""}
                        {response.metadata.utc_offset_hours}h)
                      </p>
                    </div>

                    {/* Dual Ayanamsa Display */}
                    <div className="rounded-lg border border-amber-200 bg-amber-50/50 p-3">
                      <span className="text-[11px] font-semibold text-amber-900">
                        KP Krishnamurti Ayanamsa (ID: 1)
                      </span>
                      <p className="mt-0.5 font-mono font-bold text-amber-950 sm:text-sm">
                        {response.metadata.ayanamsa_deg.toFixed(6)}°
                      </p>
                      <span className="text-[10px] text-amber-700">
                        Applied to KP Placidus house cusps and planetary star-lords.
                      </span>
                    </div>

                    <div className="rounded-lg border border-blue-200 bg-blue-50/50 p-3">
                      <span className="text-[11px] font-semibold text-blue-900">
                        Vedic Chitrapaksha Lahiri Ayanamsa (ID: 0)
                      </span>
                      <p className="mt-0.5 font-mono font-bold text-blue-950 sm:text-sm">
                        {(() => {
                          const note = response.metadata.notes?.find((n) =>
                            n.includes("Vedic Chitrapaksha Lahiri ayanamsa:")
                          );
                          if (note) {
                            const match = note.match(/([\d.]+)°/);
                            return match ? `${match[1]}°` : note;
                          }
                          return "Documented in engine notes";
                        })()}
                      </p>
                      <span className="text-[10px] text-blue-700">
                        Applied to Parashari Whole Sign D1/D9 chart generation.
                      </span>
                    </div>

                    <div className="rounded-lg bg-slate-50 p-3">
                      <span className="text-[11px] text-slate-500">House Systems Applied</span>
                      <p className="mt-0.5 font-semibold text-slate-800">
                        Placidus (KP) + Whole Sign (Vedic)
                      </p>
                      <span className="text-[10px] text-slate-500">
                        Engine: {response.metadata.engine}
                      </span>
                    </div>
                  </div>

                  {/* Engine Notes */}
                  {response.metadata.notes && response.metadata.notes.length > 0 && (
                    <div className="rounded-lg border border-slate-100 bg-slate-50/50 p-3">
                      <span className="font-semibold text-slate-700">Calculation Notes:</span>
                      <ul className="mt-1.5 list-inside list-disc space-y-0.5 text-[11px] text-slate-600">
                        {response.metadata.notes.map((n, i) => (
                          <li key={i}>{n}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default function MarriagePredictionPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-[#F8F9FA]">
          <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <RefreshCw className="h-6 w-6 animate-spin text-[#153F6B]" />
            <span className="text-sm font-semibold text-slate-700">
              Loading Marriage Prediction Tool...
            </span>
          </div>
        </div>
      }
    >
      <MarriagePredictionContent />
    </Suspense>
  );
}
