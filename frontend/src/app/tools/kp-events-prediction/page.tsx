"use client";

import React, { useState, useEffect, useCallback, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  KpPredictionScanRequest,
  KpPredictionResponse,
  SupportedKpEventItem,
  SavedHoroscopeItem,
} from "@/lib/types";
import { getSupportedKpEvents, scanKpPrediction } from "@/lib/api";
import {
  Compass,
  Calendar,
  Clock,
  Sparkles,
  Search,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  FileText,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  ShieldCheck,
  ArrowRight,
  Layers,
  SlidersHorizontal,
  Bookmark,
  Info,
  Download,
  User,
  Heart,
  Briefcase,
  GraduationCap,
  Home,
  Plane,
  Coins,
  Activity,
  Award,
} from "lucide-react";

function getTodayIsoDate(): string {
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, "0");
  const d = String(now.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function getOffsetIsoDate(days: number): string {
  const now = new Date();
  now.setDate(now.getDate() + days);
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, "0");
  const d = String(now.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function getUserTimezone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Kolkata";
  } catch {
    return "Asia/Kolkata";
  }
}

function KpEventsPredictionContent() {
  const router = useRouter();
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
  const [horoscopesError, setHoroscopesError] = useState<string | null>(null);

  // Manual chart input state
  const [manualName, setManualName] = useState<string>("Client Chart");
  const [manualDate, setManualDate] = useState<string>("1990-05-15");
  const [manualTime, setManualTime] = useState<string>("14:30:00");
  const [manualPlace, setManualPlace] = useState<string>("Chennai, India");
  const [manualLat, setManualLat] = useState<string>("13.0827");
  const [manualLon, setManualLon] = useState<string>("80.2707");
  const [manualTz, setManualTz] = useState<string>("Asia/Kolkata");

  // Supported event list
  const [supportedEvents, setSupportedEvents] = useState<SupportedKpEventItem[]>([]);
  const [selectedEventName, setSelectedEventName] = useState<string>("Marriage");

  // Scanner parameters
  const [startDate, setStartDate] = useState<string>(getTodayIsoDate());
  const [endDate, setEndDate] = useState<string>(getOffsetIsoDate(60));
  const [scanResMin, setScanResMin] = useState<number>(5);
  const [maxCandidates, setMaxCandidates] = useState<number>(25);
  const [includeRulingPlanets, setIncludeRulingPlanets] = useState<boolean>(true);
  const [scanMode, setScanMode] = useState<"standard" | "deep">("standard");
  const [deepTarget, setDeepTarget] = useState<"sub_lord" | "sub_sub_lord">("sub_lord");
  const [deepMaxRefine, setDeepMaxRefine] = useState<number>(15);

  // Prediction calculation state
  const [calculating, setCalculating] = useState<boolean>(false);
  const [predictionData, setPredictionData] = useState<KpPredictionResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // UI state
  const [copiedReport, setCopiedReport] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<"summary" | "promise" | "dasha" | "windows" | "report">("summary");

  // Fetch supported events on load
  useEffect(() => {
    getSupportedKpEvents()
      .then((res) => {
        if (res && res.events) {
          setSupportedEvents(res.events);
          if (res.events.length > 0 && !res.events.some((e) => e.name === selectedEventName)) {
            setSelectedEventName(res.events[0].name);
          }
        }
      })
      .catch((err) => {
        console.warn("Could not load supported events:", err);
      });
  }, []);

  // Fetch saved horoscopes
  const loadSavedHoroscopes = useCallback(async () => {
    if (authLoading) return; // Wait for auth to resolve before fetching
    if (!isAuthenticated || !session?.access_token) return;
    setLoadingHoroscopes(true);
    setHoroscopesError(null);
    try {
      const res = await fetch("/api/horoscopes?page=1&limit=50", {
        cache: "no-store",
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });
      if (res.ok) {
        const data = await res.json();
        // API returns { horoscopes: [...], totalCount, ... } — NOT data.data
        const items: SavedHoroscopeItem[] = data.horoscopes || [];
        setSavedHoroscopes(items);
        if (items.length > 0 && !selectedHoroscopeId) {
          setSelectedHoroscopeId(items[0].id);
        }
      } else {
        // Distinguish real errors (401, 500) from empty list
        const errData = await res.json().catch(() => ({}));
        const msg = errData?.error || `Failed to load horoscopes (HTTP ${res.status})`;
        setHoroscopesError(msg);
      }
    } catch (err: any) {
      console.error("Failed to load saved horoscopes:", err);
      setHoroscopesError(
        err instanceof Error ? err.message : "Could not connect to server. Is the application running?"
      );
    } finally {
      setLoadingHoroscopes(false);
    }
  }, [authLoading, isAuthenticated, session?.access_token, selectedHoroscopeId]);

  useEffect(() => {
    loadSavedHoroscopes();
  }, [loadSavedHoroscopes]);

  // Selected saved horoscope item
  const selectedHoroscope = savedHoroscopes.find((h) => h.id === selectedHoroscopeId);

  // Handle Scan Trigger
  const handleRunScan = async () => {
    setErrorMsg(null);
    setCalculating(true);

    try {
      const payload: KpPredictionScanRequest = {
        event_name: selectedEventName,
        start_date: startDate,
        end_date: endDate,
        scan_resolution_minutes: Number(scanResMin),
        max_candidates: Number(maxCandidates),
        include_ruling_planets: includeRulingPlanets,
        scan_mode: scanMode,
        deep_refinement_target: deepTarget,
        deep_max_intervals_to_refine: Number(deepMaxRefine),
      };

      if (chartMode === "saved") {
        if (!selectedHoroscopeId) {
          throw new Error(
            language === "ta"
              ? "தயவுசெய்து ஒரு சேமிக்கப்பட்ட ஜாதகத்தைத் தேர்ந்தெடுக்கவும்."
              : "Please select a saved horoscope."
          );
        }
        payload.horoscope_id = selectedHoroscopeId;
      } else {
        const latNum = parseFloat(manualLat);
        const lonNum = parseFloat(manualLon);
        if (isNaN(latNum) || isNaN(lonNum)) {
          throw new Error("Latitude and longitude must be valid decimal numbers.");
        }
        payload.birth_date = manualDate;
        payload.birth_time = manualTime;
        payload.timezone = manualTz;
        payload.latitude = latNum;
        payload.longitude = lonNum;
        payload.place_name = manualPlace;
        payload.customer_name = manualName;
      }

      const res = await scanKpPrediction(payload, session?.access_token);
      setPredictionData(res);
      setActiveTab("summary");
    } catch (err: any) {
      console.error("Scan error:", err);
      if (err.data?.validation_errors && Array.isArray(err.data.validation_errors)) {
        const details = err.data.validation_errors
          .map((v: any) => `${v.field ? v.field.replace(/^body -> /, "") : "Field"}: ${v.message}`)
          .join(" | ");
        setErrorMsg(`Validation error: ${details}`);
      } else {
        setErrorMsg(err.message || "Failed to calculate KP event prediction.");
      }
    } finally {
      setCalculating(false);
    }
  };

  const handleCopyReport = () => {
    if (!predictionData?.report_markdown) return;
    navigator.clipboard.writeText(predictionData.report_markdown);
    setCopiedReport(true);
    setTimeout(() => setCopiedReport(false), 2500);
  };

  const handleDownloadReport = () => {
    if (!predictionData?.report_markdown) return;
    const blob = new Blob([predictionData.report_markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `KP_Prediction_${selectedEventName.replace(/\s+/g, "_")}_${startDate}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Group events by category
  const categoriesMap: Record<string, SupportedKpEventItem[]> = {};
  supportedEvents.forEach((ev) => {
    const cat = ev.category || "General";
    if (!categoriesMap[cat]) categoriesMap[cat] = [];
    categoriesMap[cat].push(ev);
  });

  const getCategoryIcon = (cat: string) => {
    const c = cat.toLowerCase();
    if (c.includes("relation")) return <Heart className="w-4 h-4 text-rose-500" />;
    if (c.includes("career") || c.includes("profess")) return <Briefcase className="w-4 h-4 text-blue-600" />;
    if (c.includes("educat")) return <GraduationCap className="w-4 h-4 text-purple-600" />;
    if (c.includes("propert") || c.includes("vehic")) return <Home className="w-4 h-4 text-amber-600" />;
    if (c.includes("travel") || c.includes("foreign")) return <Plane className="w-4 h-4 text-cyan-600" />;
    if (c.includes("financ")) return <Coins className="w-4 h-4 text-emerald-600" />;
    if (c.includes("health")) return <Activity className="w-4 h-4 text-red-500" />;
    return <Sparkles className="w-4 h-4 text-[#B8862B]" />;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-8">
      {/* Breadcrumb Navigation */}
      <Breadcrumbs
        items={[
          { label: language === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools", href: "/tools" },
          { label: language === "ta" ? "KP நிகழ்வுகள் & கணிப்பு" : "KP Events & Prediction" },
        ]}
      />

      {/* Page Header */}
      <div className="rounded-3xl bg-gradient-to-br from-[#102A4C] via-[#1E3A5F] to-[#0A1A2F] text-white p-6 sm:p-10 shadow-xl relative overflow-hidden border border-[#D8BD80]/30">
        <div className="absolute top-0 right-0 w-96 h-96 bg-[#B8862B]/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-3 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-[#FAF2DE]/20 text-[#FAF2DE] border border-[#FAF2DE]/30 backdrop-blur-xs">
              <Compass className="w-3.5 h-3.5 text-[#E5B558]" />
              <span>{language === "ta" ? "நவீன KP நிகழ்வு கணிப்பு எஞ்சின்" : "Advanced KP Event Timing Engine"}</span>
            </div>

            <h1 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-white">
              KP Events &amp; Prediction
            </h1>
            <p className="font-tamil text-sm sm:text-base text-[#D8BD80]">
              கே.பி. நிகழ்வு ஆய்வு &amp; கோட்சார காலம் கணித்தல்
            </p>

            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              {language === "ta"
                ? "ஜாதகத்தின் நிகழ்வு உறுதிப்பாடு (CSL), தசா-புக்தி ஆதரவு மற்றும் துல்லியமான கோட்சார சந்திரன் & லக்ன கால அட்டவணையை கணக்கிடுங்கள்."
                : "Evaluate natal event promise (CSL), supporting Dasha-Bhukti-Antara periods, and scan candidate Moon transit dates and Ascendant time windows."}
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <Link
              href="/tools/advanced-kp"
              className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold bg-white/10 hover:bg-white/20 text-white border border-white/20 transition-colors"
            >
              <Compass className="w-4 h-4 text-[#E5B558]" />
              <span>Advanced KP</span>
            </Link>
            <Link
              href="/tools/transit-watch"
              className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold bg-white/10 hover:bg-white/20 text-white border border-white/20 transition-colors"
            >
              <Clock className="w-4 h-4 text-cyan-300" />
              <span>Transit Watch</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Main Workspace Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Form Controls (4 cols) */}
        <div className="lg:col-span-4 space-y-6">
          {/* Section A: Horoscope Selection */}
          <div className="rounded-2xl border border-[#DDE5F0] bg-white p-5 sm:p-6 shadow-xs space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-[#F1F5F9]">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center text-[#B8862B]">
                  <User className="w-4 h-4" />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-[#102A4C]">
                    {language === "ta" ? "1. ஜாதகம் தேர்வு" : "1. Horoscope Selection"}
                  </h2>
                  <p className="text-[11px] text-[#52667E]">
                    {language === "ta" ? "வாடிக்கையாளர் ஜாதகத்தை தேர்ந்தெடுக்கவும்" : "Saved customer chart or manual"}
                  </p>
                </div>
              </div>

              {/* Mode Toggle */}
              <div className="inline-flex p-0.5 rounded-lg bg-[#F1F5F9] border border-[#E2E8F0] text-xs font-semibold">
                <button
                  type="button"
                  onClick={() => setChartMode("saved")}
                  className={`px-2.5 py-1 rounded-md transition-all ${
                    chartMode === "saved" ? "bg-white text-[#102A4C] shadow-2xs" : "text-[#64748B] hover:text-[#102A4C]"
                  }`}
                >
                  {language === "ta" ? "சேமிக்கப்பட்டது" : "Saved"}
                </button>
                <button
                  type="button"
                  onClick={() => setChartMode("manual")}
                  className={`px-2.5 py-1 rounded-md transition-all ${
                    chartMode === "manual" ? "bg-white text-[#102A4C] shadow-2xs" : "text-[#64748B] hover:text-[#102A4C]"
                  }`}
                >
                  {language === "ta" ? "புதியது" : "New"}
                </button>
              </div>
            </div>

            {chartMode === "saved" ? (
              <div className="space-y-4">
                {loadingHoroscopes ? (
                  <div className="py-6 flex flex-col items-center justify-center text-[#64748B] gap-2">
                    <RefreshCw className="w-5 h-5 animate-spin text-[#B8862B]" />
                    <span className="text-xs">Loading saved horoscopes...</span>
                  </div>
                ) : horoscopesError ? (
                  <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs space-y-2">
                    <p className="font-semibold flex items-center gap-1.5"><AlertCircle className="w-3.5 h-3.5" /> Failed to load saved horoscopes</p>
                    <p>{horoscopesError}</p>
                    <button
                      type="button"
                      onClick={loadSavedHoroscopes}
                      className="underline text-red-700 hover:text-red-900 font-semibold"
                    >
                      Retry
                    </button>
                  </div>
                ) : savedHoroscopes.length === 0 ? (
                  <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-xs space-y-2">
                    <p className="font-semibold">No saved horoscopes found.</p>
                    <p>Switch to &quot;New&quot; mode to enter birth details, or create a horoscope first.</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <label className="block text-xs font-semibold text-[#102A4C]">
                      Select Saved Horoscope
                    </label>
                    <select
                      value={selectedHoroscopeId}
                      onChange={(e) => setSelectedHoroscopeId(e.target.value)}
                      className="w-full px-3 py-2 text-xs rounded-xl border border-[#CBD5E1] bg-white focus:outline-hidden focus:ring-2 focus:ring-[#B8862B]"
                    >
                      {savedHoroscopes.map((h) => (
                        <option key={h.id} value={h.id}>
                          {h.person_name} — {h.birth_date} ({h.birthplace || "Unknown"})
                        </option>
                      ))}
                    </select>

                    {selectedHoroscope && (
                      <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-1.5 text-xs text-[#334155]">
                        <div className="flex justify-between">
                          <span className="text-[#64748B]">Customer Name:</span>
                          <span className="font-bold text-[#102A4C]">{selectedHoroscope.person_name}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-[#64748B]">Birth Date &amp; Time:</span>
                          <span className="font-medium">{selectedHoroscope.birth_date} @ {selectedHoroscope.birth_time}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-[#64748B]">Place / Coordinates:</span>
                          <span className="font-medium">{selectedHoroscope.birthplace || "Coords"} ({selectedHoroscope.latitude.toFixed(2)}°, {selectedHoroscope.longitude.toFixed(2)}°)</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-[#64748B]">Timezone:</span>
                          <span className="font-medium">{selectedHoroscope.timezone}</span>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-3 text-xs">
                <div>
                  <label className="block font-semibold text-[#102A4C] mb-1">Name / Label</label>
                  <input
                    type="text"
                    value={manualName}
                    onChange={(e) => setManualName(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] focus:ring-2 focus:ring-[#B8862B]"
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block font-semibold text-[#102A4C] mb-1">Birth Date</label>
                    <input
                      type="date"
                      value={manualDate}
                      onChange={(e) => setManualDate(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] focus:ring-2 focus:ring-[#B8862B]"
                    />
                  </div>
                  <div>
                    <label className="block font-semibold text-[#102A4C] mb-1">Birth Time</label>
                    <input
                      type="time"
                      step="1"
                      value={manualTime}
                      onChange={(e) => setManualTime(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] focus:ring-2 focus:ring-[#B8862B]"
                    />
                  </div>
                </div>
                <div>
                  <label className="block font-semibold text-[#102A4C] mb-1">Birthplace Name</label>
                  <input
                    type="text"
                    value={manualPlace}
                    onChange={(e) => setManualPlace(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] focus:ring-2 focus:ring-[#B8862B]"
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block font-semibold text-[#102A4C] mb-1">Latitude</label>
                    <input
                      type="number"
                      step="0.0001"
                      value={manualLat}
                      onChange={(e) => setManualLat(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] focus:ring-2 focus:ring-[#B8862B]"
                    />
                  </div>
                  <div>
                    <label className="block font-semibold text-[#102A4C] mb-1">Longitude</label>
                    <input
                      type="number"
                      step="0.0001"
                      value={manualLon}
                      onChange={(e) => setManualLon(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] focus:ring-2 focus:ring-[#B8862B]"
                    />
                  </div>
                </div>
                <div>
                  <label className="block font-semibold text-[#102A4C] mb-1">Timezone</label>
                  <input
                    type="text"
                    value={manualTz}
                    onChange={(e) => setManualTz(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] focus:ring-2 focus:ring-[#B8862B]"
                  />
                </div>
              </div>
            )}

            {/* Birth-time Accuracy Notice */}
            <div className="p-3 rounded-xl bg-blue-50/70 border border-blue-200 text-blue-900 text-[11px] flex gap-2">
              <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
              <p>
                <strong>Birth-time accuracy:</strong> KP Cuspal Sub-Lords shift in 2–4 minutes. Ensure accurate birth records.
              </p>
            </div>
          </div>

          {/* Section B: Event Selection */}
          <div className="rounded-2xl border border-[#DDE5F0] bg-white p-5 sm:p-6 shadow-xs space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b border-[#F1F5F9]">
              <div className="w-8 h-8 rounded-lg bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center text-[#B8862B]">
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <h2 className="text-sm font-bold text-[#102A4C]">
                  {language === "ta" ? "2. நிகழ்வு தேர்வு" : "2. Event Selection"}
                </h2>
                <p className="text-[11px] text-[#52667E]">
                  {language === "ta" ? "ஆராய வேண்டிய நிகழ்வை தேர்ந்தெடுக்கவும்" : "Select supported event category"}
                </p>
              </div>
            </div>

            <div className="space-y-3">
              <label className="block text-xs font-semibold text-[#102A4C]">
                Select Event Category
              </label>
              <select
                value={selectedEventName}
                onChange={(e) => setSelectedEventName(e.target.value)}
                className="w-full px-3 py-2.5 text-xs font-semibold rounded-xl border border-[#CBD5E1] bg-white focus:outline-hidden focus:ring-2 focus:ring-[#B8862B]"
              >
                {Object.entries(categoriesMap).map(([cat, evList]) => (
                  <optgroup key={cat} label={`─── ${cat} ───`}>
                    {evList.map((e) => (
                      <option key={e.name} value={e.name}>
                        {e.name} (Cusp {e.primary_cusp})
                      </option>
                    ))}
                  </optgroup>
                ))}
              </select>

              {/* Event details pill */}
              {(() => {
                const activeEv = supportedEvents.find((e) => e.name === selectedEventName);
                if (!activeEv) return null;
                return (
                  <div className="p-3.5 rounded-xl bg-[#FAF2DE]/50 border border-[#D8BD80]/50 space-y-2 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-[#102A4C] flex items-center gap-1.5">
                        {getCategoryIcon(activeEv.category)}
                        {activeEv.name}
                      </span>
                      <span className="px-2 py-0.5 rounded-full bg-[#102A4C] text-white text-[10px] font-bold">
                        Primary Cusp: {activeEv.primary_cusp}
                      </span>
                    </div>
                    <p className="text-[11px] text-[#52667E] leading-relaxed">
                      {activeEv.description}
                    </p>
                    <div className="flex flex-wrap gap-1.5 pt-1 text-[11px]">
                      <span className="px-2 py-0.5 rounded-md bg-emerald-100 text-emerald-800 font-medium">
                        Supporting: {activeEv.supporting_houses.join(", ")}
                      </span>
                      <span className="px-2 py-0.5 rounded-md bg-rose-100 text-rose-800 font-medium">
                        Denying: {activeEv.denying_houses.join(", ")}
                      </span>
                    </div>
                  </div>
                );
              })()}
            </div>
          </div>

          {/* Section E: Scanner Configuration */}
          <div className="rounded-2xl border border-[#DDE5F0] bg-white p-5 sm:p-6 shadow-xs space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b border-[#F1F5F9]">
              <div className="w-8 h-8 rounded-lg bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center text-[#B8862B]">
                <Clock className="w-4 h-4" />
              </div>
              <div>
                <h2 className="text-sm font-bold text-[#102A4C]">
                  {language === "ta" ? "3. ஸ்கேனர் அமைப்புகள்" : "3. Scanner Parameters"}
                </h2>
                <p className="text-[11px] text-[#52667E]">
                  {language === "ta" ? "தேதி வரம்பு மற்றும் துல்லியத்தை அமைக்கவும்" : "Date range & transit resolution"}
                </p>
              </div>
            </div>

            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-semibold text-[#102A4C] mb-1">Start Date</label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] focus:ring-2 focus:ring-[#B8862B]"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-[#102A4C] mb-1">End Date</label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] focus:ring-2 focus:ring-[#B8862B]"
                  />
                </div>
              </div>

              {/* Quick Preset Buttons */}
              <div className="flex gap-1.5 pt-1">
                <button
                  type="button"
                  onClick={() => setEndDate(getOffsetIsoDate(30))}
                  className="px-2.5 py-1 rounded-lg bg-[#F1F5F9] hover:bg-[#E2E8F0] text-[11px] font-semibold text-[#334155]"
                >
                  +30 Days
                </button>
                <button
                  type="button"
                  onClick={() => setEndDate(getOffsetIsoDate(60))}
                  className="px-2.5 py-1 rounded-lg bg-[#F1F5F9] hover:bg-[#E2E8F0] text-[11px] font-semibold text-[#334155]"
                >
                  +60 Days
                </button>
                <button
                  type="button"
                  onClick={() => setEndDate(getOffsetIsoDate(90))}
                  className="px-2.5 py-1 rounded-lg bg-[#F1F5F9] hover:bg-[#E2E8F0] text-[11px] font-semibold text-[#334155]"
                >
                  +90 Days
                </button>
              </div>

              <div className="grid grid-cols-2 gap-2 pt-2">
                <div>
                  <label className="block font-semibold text-[#102A4C] mb-1">Lagna Step (min)</label>
                  <select
                    value={scanResMin}
                    onChange={(e) => setScanResMin(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] bg-white focus:ring-2 focus:ring-[#B8862B]"
                  >
                    <option value={5}>5 minutes</option>
                    <option value={10}>10 minutes</option>
                    <option value={15}>15 minutes</option>
                    <option value={30}>30 minutes</option>
                  </select>
                </div>
                <div>
                  <label className="block font-semibold text-[#102A4C] mb-1">Max Windows</label>
                  <select
                    value={maxCandidates}
                    onChange={(e) => setMaxCandidates(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] bg-white focus:ring-2 focus:ring-[#B8862B]"
                  >
                    <option value={15}>15 candidates</option>
                    <option value={25}>25 candidates</option>
                    <option value={50}>50 candidates</option>
                  </select>
                </div>
              </div>

              <div className="pt-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeRulingPlanets}
                    onChange={(e) => setIncludeRulingPlanets(e.target.checked)}
                    className="rounded-sm border-gray-300 text-[#B8862B] focus:ring-[#B8862B]"
                  />
                  <span className="font-semibold text-[#102A4C]">Filter / Score with Ruling Planets (RP)</span>
                </label>
              </div>

              {/* Scan Mode Selection: Standard vs Deep Scan */}
              <div className="pt-3 border-t border-[#F1F5F9] space-y-2">
                <label className="block font-semibold text-[#102A4C]">
                  {language === "ta" ? "கணக்கீட்டு முறை (Scan Mode)" : "Calculation Scan Mode"}
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setScanMode("standard")}
                    className={`py-2 px-3 rounded-xl border text-left text-xs transition-all ${
                      scanMode === "standard"
                        ? "border-[#B8862B] bg-[#FAF2DE] text-[#102A4C] font-bold shadow-2xs"
                        : "border-[#CBD5E1] bg-white text-[#52667E] hover:border-gray-400"
                    }`}
                  >
                    <span className="block font-bold">Standard Scan</span>
                    <span className="text-[10px] text-[#64748B]">Coarse 5-min intervals</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setScanMode("deep")}
                    className={`py-2 px-3 rounded-xl border text-left text-xs transition-all ${
                      scanMode === "deep"
                        ? "border-[#B8862B] bg-[#FAF2DE] text-[#102A4C] font-bold shadow-2xs"
                        : "border-[#CBD5E1] bg-white text-[#52667E] hover:border-gray-400"
                    }`}
                  >
                    <span className="block font-bold flex items-center gap-1">
                      <Sparkles className="w-3.5 h-3.5 text-[#B8862B]" />
                      Deep Scan
                    </span>
                    <span className="text-[10px] text-[#64748B]">Adaptive ±0.5s bisection</span>
                  </button>
                </div>

                {scanMode === "deep" && (
                  <div className="p-3.5 rounded-xl bg-[#FAF2DE]/50 border border-[#D8BD80]/50 space-y-2.5 text-xs animate-in fade-in">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-[#102A4C]">Refinement Level</span>
                      <select
                        value={deepTarget}
                        onChange={(e) => setDeepTarget(e.target.value as "sub_lord" | "sub_sub_lord")}
                        className="px-2 py-1 rounded-lg border border-[#CBD5E1] bg-white text-xs font-medium text-[#102A4C]"
                      >
                        <option value="sub_lord">KP Sub-Lord (Default)</option>
                        <option value="sub_sub_lord">KP Sub-Sub-Lord</option>
                      </select>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-[#102A4C]">Refined Windows Cap</span>
                      <select
                        value={deepMaxRefine}
                        onChange={(e) => setDeepMaxRefine(Number(e.target.value))}
                        className="px-2 py-1 rounded-lg border border-[#CBD5E1] bg-white text-xs font-medium text-[#102A4C]"
                      >
                        <option value={10}>Top 10 candidates</option>
                        <option value={15}>Top 15 candidates</option>
                        <option value={25}>Top 25 candidates</option>
                      </select>
                    </div>
                    <p className="text-[10.5px] text-[#785E1A] leading-relaxed">
                      Deep Scan bisects exact Moon &amp; Ascendant ingress/egress boundaries down to the second using XALEN ephemeris root-finding.
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Error Message */}
            {errorMsg && (
              <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex gap-2">
                <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* Primary Action Button */}
            <button
              type="button"
              onClick={handleRunScan}
              disabled={calculating}
              className="w-full py-3.5 px-4 rounded-xl bg-gradient-to-r from-[#B8862B] to-[#996D1E] hover:from-[#A47623] hover:to-[#855D17] text-white font-bold text-sm shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {calculating ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin text-white" />
                  <span>Scanning Astrological Windows...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-[#FAF2DE]" />
                  <span>{language === "ta" ? "நிகழ்வு & காலத்தை கணக்கிடு" : "Scan Event Promise & Dates"}</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: Results & Interactive Report (8 cols) */}
        <div className="lg:col-span-8 space-y-6">
          {!predictionData ? (
            <div className="rounded-3xl border-2 border-dashed border-[#DDE5F0] bg-white p-12 text-center space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center text-[#B8862B] mx-auto shadow-xs">
                <Compass className="w-8 h-8" />
              </div>
              <div className="max-w-md mx-auto space-y-2">
                <h3 className="font-serif text-xl font-bold text-[#102A4C]">
                  {language === "ta" ? "KP கணிப்பு தொடங்குங்கள்" : "Ready to Analyze KP Event"}
                </h3>
                <p className="text-xs sm:text-sm text-[#52667E] leading-relaxed">
                  {language === "ta"
                    ? "இடதுபுறத்தில் உள்ள ஜாதகத்தை மற்றும் நிகழ்வை தேர்வு செய்து 'Scan Event Promise & Dates' பொத்தானை அழுத்தவும்."
                    : "Select a horoscope and event category on the left, then click 'Scan Event Promise & Dates' to evaluate the natal promise and candidate transit time windows."}
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Results Navigation Tabs */}
              <div className="flex border-b border-[#DDE5F0] gap-2 overflow-x-auto pb-1 text-xs sm:text-sm font-semibold">
                <button
                  type="button"
                  onClick={() => setActiveTab("summary")}
                  className={`px-4 py-2.5 rounded-t-xl transition-all border-b-2 flex items-center gap-1.5 whitespace-nowrap ${
                    activeTab === "summary"
                      ? "border-[#B8862B] text-[#B8862B] bg-[#FAF2DE]/20 font-bold"
                      : "border-transparent text-[#64748B] hover:text-[#102A4C]"
                  }`}
                >
                  <Award className="w-4 h-4" />
                  <span>Overview &amp; Promise</span>
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab("windows")}
                  className={`px-4 py-2.5 rounded-t-xl transition-all border-b-2 flex items-center gap-1.5 whitespace-nowrap ${
                    activeTab === "windows"
                      ? "border-[#B8862B] text-[#B8862B] bg-[#FAF2DE]/20 font-bold"
                      : "border-transparent text-[#64748B] hover:text-[#102A4C]"
                  }`}
                >
                  <Clock className="w-4 h-4" />
                  <span>Candidate Windows ({predictionData.total_windows_found})</span>
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab("dasha")}
                  className={`px-4 py-2.5 rounded-t-xl transition-all border-b-2 flex items-center gap-1.5 whitespace-nowrap ${
                    activeTab === "dasha"
                      ? "border-[#B8862B] text-[#B8862B] bg-[#FAF2DE]/20 font-bold"
                      : "border-transparent text-[#64748B] hover:text-[#102A4C]"
                  }`}
                >
                  <Layers className="w-4 h-4" />
                  <span>Dasha Periods</span>
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab("report")}
                  className={`px-4 py-2.5 rounded-t-xl transition-all border-b-2 flex items-center gap-1.5 whitespace-nowrap ${
                    activeTab === "report"
                      ? "border-[#B8862B] text-[#B8862B] bg-[#FAF2DE]/20 font-bold"
                      : "border-transparent text-[#64748B] hover:text-[#102A4C]"
                  }`}
                >
                  <FileText className="w-4 h-4" />
                  <span>Full Report</span>
                </button>
              </div>

              {/* Tab 1: Overview & Promise */}
              {activeTab === "summary" && (
                <div className="space-y-6">
                  {/* Promise Banner */}
                  <div className="rounded-2xl border border-[#DDE5F0] bg-white p-6 shadow-xs space-y-5">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#F1F5F9]">
                      <div>
                        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
                          Natal Cuspal Sub-Lord Assessment
                        </div>
                        <h3 className="font-serif text-2xl font-bold text-[#102A4C] mt-1">
                          {predictionData.event_promise.event_name}
                        </h3>
                        <p className="text-xs text-[#52667E]">
                          Client: <strong>{predictionData.customer_name}</strong> | Birth: {predictionData.birth_details.birth_date} @ {predictionData.birth_details.birth_time}
                        </p>
                      </div>

                      <div className="text-left sm:text-right">
                        <span
                          className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs sm:text-sm font-bold ${
                            predictionData.event_promise.promise_status === "Promised"
                              ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                              : predictionData.event_promise.promise_status === "Delayed / Mixed"
                              ? "bg-amber-100 text-amber-800 border border-amber-300"
                              : "bg-rose-100 text-rose-800 border border-rose-300"
                          }`}
                        >
                          {predictionData.event_promise.promise_status === "Promised" && <CheckCircle2 className="w-4 h-4" />}
                          {predictionData.event_promise.promise_status === "Delayed / Mixed" && <AlertTriangle className="w-4 h-4" />}
                          {predictionData.event_promise.promise_status === "Denied / Weak" && <AlertCircle className="w-4 h-4" />}
                          Promise: {predictionData.event_promise.promise_status}
                        </span>
                      </div>
                    </div>

                    {/* Promise Breakdown Grid */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
                      <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-1">
                        <span className="text-[#64748B] block font-medium">Primary House Cusp:</span>
                        <span className="font-bold text-[#102A4C] text-sm">
                          {predictionData.event_promise.primary_cusp}th House ({predictionData.event_promise.cusp_sign})
                        </span>
                        <p className="text-[11px] text-[#52667E]">
                          Degree: {predictionData.event_promise.cusp_degree}°
                        </p>
                      </div>

                      <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-1">
                        <span className="text-[#64748B] block font-medium">Cuspal Sub-Lord (CSL):</span>
                        <span className="font-bold text-[#B8862B] text-sm">
                          {predictionData.event_promise.cusp_sub_lord}
                        </span>
                        <p className="text-[11px] text-[#52667E]">
                          Star Lord: {predictionData.event_promise.cusp_star_lord}
                          {predictionData.event_promise.is_csl_retrograde && " (Retrograde)"}
                        </p>
                      </div>

                      <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-1">
                        <span className="text-[#64748B] block font-medium">CSL Signified Houses:</span>
                        <span className="font-bold text-[#102A4C] text-sm">
                          [{predictionData.event_promise.csl_significations.join(", ")}]
                        </span>
                        <p className="text-[11px] text-emerald-700 font-medium">
                          Supporting: [{predictionData.event_promise.supporting_hits.join(", ") || "None"}]
                        </p>
                      </div>
                    </div>

                    {/* Astrological Explanation */}
                    <div className="p-4 rounded-xl bg-[#FAF2DE]/50 border border-[#D8BD80]/50 space-y-2">
                      <h4 className="text-xs font-bold text-[#102A4C] flex items-center gap-1.5">
                        <Info className="w-3.5 h-3.5 text-[#B8862B]" />
                        Astrological Promise Rule Rationale
                      </h4>
                      <p className="text-xs text-[#334155] leading-relaxed">
                        {predictionData.event_promise.rule_explanation}
                      </p>
                    </div>

                    {/* Ruling Planets Overview */}
                    {predictionData.ruling_planets && (
                      <div className="pt-2 border-t border-[#F1F5F9] space-y-3">
                        <div className="flex items-center justify-between">
                          <h4 className="text-xs font-bold text-[#102A4C]">
                            Ruling Planets (RP) at Judgement Moment
                          </h4>
                          <span className="text-[11px] text-[#64748B]">
                            {predictionData.ruling_planets.judgement_time}
                          </span>
                        </div>
                        <div className="flex flex-wrap gap-2 text-xs">
                          {predictionData.ruling_planets.active_ruling_planets.map((rp) => (
                            <span
                              key={rp}
                              className="px-3 py-1 rounded-full bg-[#102A4C] text-white font-semibold text-xs shadow-2xs"
                            >
                              {rp}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Tab 2: Candidate Windows */}
              {activeTab === "windows" && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between text-xs text-[#64748B]">
                    <span>
                      Showing <strong>{predictionData.candidate_windows.length}</strong> candidate timing windows for <strong>{predictionData.event_promise.event_name}</strong>
                    </span>
                    <span className="text-[11px]">Ranked by Composite Astrological Evidence</span>
                  </div>

                  {predictionData.candidate_windows.length === 0 ? (
                    <div className="rounded-2xl border border-amber-200 bg-amber-50/60 p-8 text-center space-y-2 text-amber-900 text-xs">
                      <AlertTriangle className="w-8 h-8 mx-auto text-amber-600" />
                      <p className="font-bold text-sm">No Qualifying Transit Windows Found</p>
                      <p className="max-w-md mx-auto text-[#52667E]">
                        No candidate windows satisfied the dual transit criteria within the scanned range ({predictionData.scan_parameters.start_date} to {predictionData.scan_parameters.end_date}).
                        Try extending the date range or adjusting the scan resolution.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {predictionData.candidate_windows.map((w, idx) => (
                        <div
                          key={w.id || idx}
                          className="rounded-2xl border border-[#DDE5F0] bg-white p-5 shadow-xs hover:border-[#B8862B] transition-all space-y-3"
                        >
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#F1F5F9]">
                            <div className="flex items-center gap-3">
                              <span
                                className={`w-9 h-9 rounded-xl flex items-center justify-center font-bold text-sm shrink-0 shadow-2xs ${
                                  w.evidence_grade === "A"
                                    ? "bg-emerald-500 text-white"
                                    : w.evidence_grade === "B"
                                    ? "bg-amber-500 text-white"
                                    : "bg-slate-400 text-white"
                                }`}
                              >
                                {w.evidence_grade}
                              </span>
                              <div>
                                <div className="flex items-center gap-2">
                                  <h4 className="text-sm font-bold text-[#102A4C]">
                                    {w.date} &bull; {w.start_time} – {w.end_time}
                                  </h4>
                                  {w.scan_mode === "deep" && (
                                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
                                      <Sparkles className="w-3 h-3 text-[#B8862B]" />
                                      Deep Scan (±0.5s)
                                    </span>
                                  )}
                                </div>
                                <p className="text-[11px] text-[#64748B]">
                                  Timezone: {w.timezone} | Dasha: <span className="font-semibold text-[#102A4C]">{w.dasha_chain}</span>
                                  {w.refinement_resolution && ` | Res: ${w.refinement_resolution}`}
                                </p>
                              </div>
                            </div>

                            <div className="flex items-center gap-2">
                              <span className="text-xs font-semibold text-[#64748B]">Score:</span>
                              <span className="px-2.5 py-1 rounded-lg bg-[#FAF2DE] text-[#8C6D23] font-bold text-xs border border-[#D8BD80]">
                                {w.composite_score} / 100
                              </span>
                            </div>
                          </div>

                          {/* Transit Breakdown Pills */}
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                            <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-1">
                              <span className="text-[11px] font-bold text-[#64748B] block">Transit Moon (Date Determinant):</span>
                              <p className="text-[#102A4C]">
                                <strong>{w.moon_transit.sign}</strong> ({w.moon_transit.star} / Sub: <span className="font-bold text-[#B8862B]">{w.moon_transit.sub_lord}</span>)
                              </p>
                            </div>

                            <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-1">
                              <span className="text-[11px] font-bold text-[#64748B] block">Transit Lagna (Time Window):</span>
                              <p className="text-[#102A4C]">
                                <strong>{w.lagna_transit.sign}</strong> (Sub: <span className="font-bold text-[#B8862B]">{w.lagna_transit.sub_lord}</span>, Sub-Sub: {w.lagna_transit.sub_sub_lord})
                              </p>
                            </div>
                          </div>

                          {/* Deep Scan Exact Transitions Pill */}
                          {w.transit_transitions && (
                            <div className="p-3.5 rounded-xl bg-[#FAF2DE]/30 border border-[#D8BD80]/50 space-y-2 text-xs">
                              <span className="text-[11px] font-bold text-[#8C6D23] flex items-center gap-1.5">
                                <Clock className="w-3.5 h-3.5 text-[#B8862B]" />
                                Exact Astronomical Ingress / Egress ({w.transit_transitions.refinement_level || "sub_lord"})
                              </span>
                              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px] text-[#334155]">
                                <div>
                                  <span className="text-[#64748B] block">Lagna Ingress:</span>
                                  <strong>{w.transit_transitions.lagna_ingress_time}</strong> ({w.transit_transitions.lagna_ingress_degree}°)
                                </div>
                                <div>
                                  <span className="text-[#64748B] block">Lagna Egress:</span>
                                  <strong>{w.transit_transitions.lagna_egress_time}</strong> ({w.transit_transitions.lagna_egress_degree}°)
                                </div>
                                <div>
                                  <span className="text-[#64748B] block">Moon Sub Ingress:</span>
                                  <strong>
                                    {w.transit_transitions.moon_sub_lord_ingress_in_window
                                      ? `${w.transit_transitions.moon_from_sub_lord} → ${w.transit_transitions.moon_to_sub_lord} @ ${w.transit_transitions.moon_crossing_time}`
                                      : `${w.moon_transit.sub_lord} (Continuous)`}
                                  </strong>
                                </div>
                                <div>
                                  <span className="text-[#64748B] block">Precision:</span>
                                  <strong className="text-emerald-700">±{w.transit_transitions.astronomical_precision_seconds}s (XALEN)</strong>
                                </div>
                              </div>
                              <p className="text-[10px] text-[#785E1A] italic pt-0.5">
                                Note: Calculated transit boundaries denote astronomical coordinate entry/exit. Event fruition requires overall karmic and chart concurrence.
                              </p>
                            </div>
                          )}

                          <p className="text-xs text-[#334155] leading-relaxed">
                            {w.explanation}
                          </p>

                          {/* Matched Ruling Planets */}
                          {w.ruling_planets_matched.length > 0 && (
                            <div className="flex flex-wrap items-center gap-1.5 text-[11px] pt-1">
                              <span className="text-[#64748B]">RP Resonance:</span>
                              {w.ruling_planets_matched.map((rp) => (
                                <span
                                  key={rp}
                                  className="px-2 py-0.5 rounded-md bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80] font-semibold"
                                >
                                  {rp}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Tab 3: Dasha Periods */}
              {activeTab === "dasha" && (
                <div className="rounded-2xl border border-[#DDE5F0] bg-white p-6 shadow-xs space-y-4">
                  <h3 className="font-serif text-lg font-bold text-[#102A4C]">
                    Vimshottari Dasha Periods &amp; Significations
                  </h3>
                  <p className="text-xs text-[#52667E]">
                    Showing candidate Maha Dasha, Bhukti, and Antara periods active across the scan window.
                  </p>

                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left">
                      <thead>
                        <tr className="bg-[#F8FAFC] text-[#64748B] border-b border-[#E2E8F0]">
                          <th className="p-2.5 font-semibold">Level</th>
                          <th className="p-2.5 font-semibold">Lords</th>
                          <th className="p-2.5 font-semibold">Period Dates</th>
                          <th className="p-2.5 font-semibold">Signified Houses</th>
                          <th className="p-2.5 font-semibold">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#F1F5F9]">
                        {predictionData.candidate_dasha_periods.map((dp, i) => (
                          <tr key={i} className="hover:bg-[#F8FAFC]">
                            <td className="p-2.5 font-bold text-[#102A4C]">Level {dp.level}</td>
                            <td className="p-2.5 font-semibold text-[#102A4C]">
                              {dp.mahadasha_lord}
                              {dp.bhukti_lord && ` > ${dp.bhukti_lord}`}
                              {dp.antara_lord && ` > ${dp.antara_lord}`}
                            </td>
                            <td className="p-2.5 text-[#64748B]">
                              {dp.start_date} to {dp.end_date}
                              {dp.is_running && (
                                <span className="ml-1.5 px-1.5 py-0.5 rounded-xs bg-emerald-100 text-emerald-800 text-[10px] font-bold">
                                  Running
                                </span>
                              )}
                            </td>
                            <td className="p-2.5 font-mono text-[#334155]">
                              [{dp.signified_houses.join(", ")}]
                            </td>
                            <td className="p-2.5">
                              <span
                                className={`px-2 py-0.5 rounded-md text-[11px] font-bold ${
                                  dp.support_status.includes("Strong")
                                    ? "bg-emerald-100 text-emerald-800"
                                    : dp.support_status.includes("Support")
                                    ? "bg-blue-100 text-blue-800"
                                    : dp.support_status.includes("Unfavorable")
                                    ? "bg-rose-100 text-rose-800"
                                    : "bg-slate-100 text-slate-800"
                                }`}
                              >
                                {dp.support_status}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Tab 4: Markdown Report */}
              {activeTab === "report" && (
                <div className="rounded-2xl border border-[#DDE5F0] bg-white p-6 shadow-xs space-y-4">
                  <div className="flex items-center justify-between pb-3 border-b border-[#F1F5F9]">
                    <h3 className="font-serif text-lg font-bold text-[#102A4C]">
                      Astrological Analysis Report
                    </h3>
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={handleCopyReport}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#CBD5E1] bg-white hover:bg-[#F8FAFC] text-xs font-semibold text-[#334155] transition-colors"
                      >
                        {copiedReport ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                        <span>{copiedReport ? "Copied!" : "Copy Report"}</span>
                      </button>
                      <button
                        type="button"
                        onClick={handleDownloadReport}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#CBD5E1] bg-white hover:bg-[#F8FAFC] text-xs font-semibold text-[#334155] transition-colors"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>Download (.md)</span>
                      </button>
                    </div>
                  </div>

                  <pre className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] text-xs text-[#334155] font-mono whitespace-pre-wrap overflow-x-auto leading-relaxed max-h-[500px]">
                    {predictionData.report_markdown}
                  </pre>
                </div>
              )}

              {/* Disclaimer Notice */}
              <div className="p-4 rounded-2xl bg-amber-50/50 border border-amber-200/60 text-xs text-amber-900 space-y-1">
                <p className="font-bold flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-amber-700" />
                  Transparency &amp; Astrological Evidence Disclaimer
                </p>
                <p className="text-[11px] leading-relaxed text-[#52667E]">
                  {predictionData.limitations_disclaimer}
                </p>
                <p className="text-[11px] text-[#64748B] pt-1">
                  Engine: {predictionData.calculation_convention}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function KpEventsPredictionPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-[50vh] flex items-center justify-center">
          <RefreshCw className="w-8 h-8 text-[#B8862B] animate-spin" />
        </div>
      }
    >
      <KpEventsPredictionContent />
    </Suspense>
  );
}
