"use client";

import React, { useState, useEffect, useCallback, Suspense, useMemo } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  LifeDomainInfo,
  LifeRoadmapRequest,
  LifeRoadmapResponse,
  DomainScorecard,
  RoadmapPeriodItem,
  ScoredMilestone,
  SavedHoroscopeItem,
} from "@/lib/types";
import { getLifeRoadmapDomains, generateLifeRoadmap } from "@/lib/api";
import {
  Sparkles,
  Calendar,
  Clock,
  Compass,
  Briefcase,
  Heart,
  Coins,
  Plane,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  AlertCircle,
  Search,
  Filter,
  Layers,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  RefreshCw,
  Printer,
  Download,
  ArrowRight,
  User,
  Info,
  Zap,
  Bookmark,
  Share2,
} from "lucide-react";

function getTodayIsoDate(): string {
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, "0");
  const d = String(now.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

const DOMAIN_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  career: Briefcase,
  relationships: Heart,
  finance: Coins,
  travel: Plane,
  health: ShieldAlert,
};

function LifeRoadmapContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialHoroscopeId = searchParams.get("id") || "";

  const { language } = useLanguage();
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
  const [manualDate, setManualDate] = useState<string>("1995-10-25");
  const [manualTime, setManualTime] = useState<string>("14:30:00");
  const [manualPlace, setManualPlace] = useState<string>("Chennai, India");
  const [manualLat, setManualLat] = useState<string>("13.0827");
  const [manualLon, setManualLon] = useState<string>("80.2707");
  const [manualTz, setManualTz] = useState<string>("Asia/Kolkata");

  // Horizon & Filter controls
  const [horizonYears, setHorizonYears] = useState<number>(3);
  const [startDate, setStartDate] = useState<string>(getTodayIsoDate());
  const [activeDomainFilter, setActiveDomainFilter] = useState<string>("all");
  const [activeProbFilter, setActiveProbFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Domain metadata
  const [domains, setDomains] = useState<LifeDomainInfo[]>([]);

  // Calculation state
  const [calculating, setCalculating] = useState<boolean>(false);
  const [roadmapData, setRoadmapData] = useState<LifeRoadmapResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // UI state
  const [copiedReport, setCopiedReport] = useState<boolean>(false);
  const [expandedPeriodKey, setExpandedPeriodKey] = useState<string | null>(null);
  const [selectedMilestone, setSelectedMilestone] = useState<ScoredMilestone | null>(null);
  const [viewTab, setViewTab] = useState<"roadmap" | "scorecards" | "milestones" | "report">("roadmap");

  // Load domain metadata
  useEffect(() => {
    getLifeRoadmapDomains()
      .then((dList) => setDomains(dList || []))
      .catch((err) => console.warn("Failed to load life domains:", err));
  }, []);

  // Fetch saved horoscopes
  const loadSavedHoroscopes = useCallback(async () => {
    if (authLoading) return;
    if (!isAuthenticated || !session?.access_token) return;
    setLoadingHoroscopes(true);
    setHoroscopesError(null);
    try {
      const res = await fetch("/api/horoscopes?page=1&limit=1000", {
        cache: "no-store",
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });
      if (res.ok) {
        const data = await res.json();
        const items: SavedHoroscopeItem[] = data.horoscopes || [];
        setSavedHoroscopes(items);
        if (items.length > 0 && !selectedHoroscopeId) {
          setSelectedHoroscopeId(items[0].id);
        }
      } else {
        const errData = await res.json().catch(() => ({}));
        setHoroscopesError(errData?.error || `Failed to load horoscopes (HTTP ${res.status})`);
      }
    } catch (err: any) {
      setHoroscopesError(
        err instanceof Error ? err.message : "Could not connect to server."
      );
    } finally {
      setLoadingHoroscopes(false);
    }
  }, [authLoading, isAuthenticated, session?.access_token, selectedHoroscopeId]);

  useEffect(() => {
    loadSavedHoroscopes();
  }, [loadSavedHoroscopes]);

  // Handle roadmap calculation
  const handleGenerateRoadmap = async () => {
    setErrorMsg(null);
    setCalculating(true);

    try {
      const payload: LifeRoadmapRequest = {
        horizon_years: horizonYears,
        start_date: startDate || getTodayIsoDate(),
        filter_domain: activeDomainFilter === "all" ? undefined : activeDomainFilter,
      };

      if (chartMode === "saved") {
        if (!selectedHoroscopeId) {
          setErrorMsg("Please select a saved horoscope.");
          setCalculating(false);
          return;
        }
        payload.horoscope_id = selectedHoroscopeId;
      } else {
        if (!manualDate || !manualTime) {
          setErrorMsg("Please provide birth date and birth time.");
          setCalculating(false);
          return;
        }
        payload.birth_date = manualDate;
        payload.birth_time = manualTime;
        payload.timezone = manualTz;
        payload.latitude = parseFloat(manualLat) || 13.0827;
        payload.longitude = parseFloat(manualLon) || 80.2707;
        payload.place_name = manualPlace;
        payload.customer_name = manualName;
      }

      const res = await generateLifeRoadmap(payload, session?.access_token);
      setRoadmapData(res);
      // Auto-expand running period if found
      if (res.running_period_key) {
        setExpandedPeriodKey(res.running_period_key);
      } else if (res.chronological_periods.length > 0) {
        setExpandedPeriodKey(res.chronological_periods[0].period_key);
      }
    } catch (err: any) {
      console.error("Life roadmap generation failed:", err);
      setErrorMsg(
        err?.message ||
          "Failed to generate Life Roadmap. Please verify input details and try again."
      );
    } finally {
      setCalculating(false);
    }
  };

  // Filtered periods
  const filteredPeriods = useMemo(() => {
    if (!roadmapData) return [];
    return roadmapData.chronological_periods
      .map((p) => {
        let milestones = p.all_milestones;

        // Domain filter
        if (activeDomainFilter !== "all") {
          milestones = milestones.filter((m) => m.domain_id === activeDomainFilter);
        }

        // Probability filter
        if (activeProbFilter === "high") {
          milestones = milestones.filter((m) => m.probability_level === "HIGH" || m.probability_level === "CAUTION");
        } else if (activeProbFilter === "moderate") {
          milestones = milestones.filter((m) => m.probability_level === "MODERATE");
        } else if (activeProbFilter === "caution") {
          milestones = milestones.filter((m) => m.is_caution_type && m.probability_level === "CAUTION");
        }

        // Search query
        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase();
          milestones = milestones.filter(
            (m) =>
              m.event_name.toLowerCase().includes(q) ||
              m.domain_name.toLowerCase().includes(q) ||
              m.hint.toLowerCase().includes(q) ||
              p.period_key.toLowerCase().includes(q)
          );
        }

        return {
          ...p,
          top_milestones: milestones.slice(0, 4),
          all_milestones: milestones,
        };
      })
      .filter((p) => {
        // If filters applied, only show periods having matching milestones or matches search
        if (activeDomainFilter !== "all" || activeProbFilter !== "all" || searchQuery.trim()) {
          return p.all_milestones.length > 0;
        }
        return true;
      });
  }, [roadmapData, activeDomainFilter, activeProbFilter, searchQuery]);

  // Copy report
  const handleCopyMarkdown = () => {
    if (!roadmapData?.executive_roadmap_markdown) return;
    navigator.clipboard.writeText(roadmapData.executive_roadmap_markdown);
    setCopiedReport(true);
    setTimeout(() => setCopiedReport(false), 2500);
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-800 pb-20">
      {/* Top Banner / Breadcrumb */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Breadcrumbs
            items={[
              { label: "Home", href: "/" },
              { label: "Astrology Tools", href: "/tools" },
              { label: "Life Roadmap", href: "/tools/life-roadmap" },
            ]}
          />

          <div className="mt-3 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300">
                  <Sparkles className="w-3.5 h-3.5 mr-1" /> Feature 1: Multi-Year Life Roadmap
                </span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-50 text-amber-800 border border-amber-200">
                  32-Event KP Engine
                </span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight mt-1">
                Automated Multi-Year Life Timeline Predictor
              </h1>
              <p className="text-sm text-slate-600 mt-1 max-w-3xl">
                Instead of scanning just one event at a time, this engine evaluates your birth chart across the next 1, 3, or 5 years across all 5 major life domains simultaneously using Dasha-Bhukti-Antara (DBA) periods.
              </p>
            </div>

            {/* Quick cross-link to single-event scanner */}
            <div className="flex items-center gap-2">
              <Link
                href="/tools/kp-events-prediction"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-lg hover:bg-indigo-100 transition-colors"
              >
                <Layers className="w-3.5 h-3.5" />
                Single-Event KP Scanner
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Input Configuration Card */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 sm:p-6">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-5">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-amber-50 border border-amber-200 text-amber-800">
                <Compass className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-slate-900">
                  1. Chart Selection & Strategic Horizon
                </h2>
                <p className="text-xs text-slate-500">
                  Select a saved client horoscope or enter birth details directly.
                </p>
              </div>
            </div>

            {/* Mode Toggle */}
            <div className="flex items-center bg-slate-100 p-1 rounded-xl">
              <button
                type="button"
                onClick={() => setChartMode("saved")}
                className={`px-3 py-1 text-xs font-medium rounded-lg transition-all ${
                  chartMode === "saved"
                    ? "bg-white text-slate-900 shadow-xs font-semibold"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                Saved Horoscope
              </button>
              <button
                type="button"
                onClick={() => setChartMode("manual")}
                className={`px-3 py-1 text-xs font-medium rounded-lg transition-all ${
                  chartMode === "manual"
                    ? "bg-white text-slate-900 shadow-xs font-semibold"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                Direct Birth Input
              </button>
            </div>
          </div>

          {/* Saved Chart Mode */}
          {chartMode === "saved" ? (
            <div className="space-y-4">
              {loadingHoroscopes ? (
                <div className="flex items-center gap-2 text-xs text-slate-500 py-4">
                  <RefreshCw className="w-4 h-4 animate-spin text-amber-600" />
                  Loading your saved customer horoscopes...
                </div>
              ) : horoscopesError ? (
                <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-700">
                  {horoscopesError}. Please ensure you are logged in or switch to Direct Birth Input.
                </div>
              ) : savedHoroscopes.length === 0 ? (
                <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-800 flex items-center justify-between">
                  <span>No saved horoscopes found. Please add one or use Direct Birth Input.</span>
                  <button
                    type="button"
                    onClick={() => setChartMode("manual")}
                    className="font-semibold underline ml-2 hover:text-amber-900"
                  >
                    Switch to Direct Input &rarr;
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-700 mb-1">
                      Choose Customer Chart
                    </label>
                    <select
                      value={selectedHoroscopeId}
                      onChange={(e) => setSelectedHoroscopeId(e.target.value)}
                      className="w-full text-sm rounded-xl border-slate-300 bg-white px-3 py-2 border focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                    >
                      {savedHoroscopes.map((h) => (
                        <option key={h.id} value={h.id}>
                          {h.person_name} — {h.birth_date} {h.birth_time || ""} ({h.birthplace || h.timezone})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-700 mb-1">
                      Selected Chart Summary
                    </label>
                    {(() => {
                      const sel = savedHoroscopes.find((h) => h.id === selectedHoroscopeId);
                      return sel ? (
                        <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 space-y-0.5">
                          <div>
                            <span className="font-semibold text-slate-900">{sel.person_name}</span> | Born: {sel.birth_date} at {sel.birth_time || "12:00"}
                          </div>
                          <div className="text-slate-500 text-[11px]">
                            {sel.birthplace || "Coordinates"} ({sel.latitude}&deg;N, {sel.longitude}&deg;E) | TZ: {sel.timezone}
                          </div>
                        </div>
                      ) : null;
                    })()}
                  </div>
                </div>
              )}
            </div>
          ) : (
            /* Manual Chart Entry */
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Native Name</label>
                <input
                  type="text"
                  value={manualName}
                  onChange={(e) => setManualName(e.target.value)}
                  className="w-full text-xs rounded-xl border-slate-300 px-3 py-2 border focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                  placeholder="e.g. John Doe"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Birth Date</label>
                <input
                  type="date"
                  value={manualDate}
                  onChange={(e) => setManualDate(e.target.value)}
                  className="w-full text-xs rounded-xl border-slate-300 px-3 py-2 border focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Birth Time (24h)</label>
                <input
                  type="time"
                  step="1"
                  value={manualTime}
                  onChange={(e) => setManualTime(e.target.value)}
                  className="w-full text-xs rounded-xl border-slate-300 px-3 py-2 border focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Birth Place / City</label>
                <input
                  type="text"
                  value={manualPlace}
                  onChange={(e) => setManualPlace(e.target.value)}
                  className="w-full text-xs rounded-xl border-slate-300 px-3 py-2 border focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Latitude</label>
                <input
                  type="text"
                  value={manualLat}
                  onChange={(e) => setManualLat(e.target.value)}
                  className="w-full text-xs rounded-xl border-slate-300 px-3 py-2 border focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Longitude</label>
                <input
                  type="text"
                  value={manualLon}
                  onChange={(e) => setManualLon(e.target.value)}
                  className="w-full text-xs rounded-xl border-slate-300 px-3 py-2 border focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Timezone</label>
                <input
                  type="text"
                  value={manualTz}
                  onChange={(e) => setManualTz(e.target.value)}
                  className="w-full text-xs rounded-xl border-slate-300 px-3 py-2 border focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                />
              </div>
            </div>
          )}

          {/* Horizon Selection & Action Bar */}
          <div className="mt-5 pt-4 border-t border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-3">
              <span className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
                Life Horizon:
              </span>

              {/* 1 Year, 3 Years, 5 Years Buttons */}
              <div className="flex items-center gap-1.5 bg-slate-100 p-1 rounded-xl">
                {[
                  { yr: 1, label: "1 Year", desc: "Immediate Outlook" },
                  { yr: 3, label: "3 Years", desc: "Strategic Roadmap" },
                  { yr: 5, label: "5 Years", desc: "Long-Range Vision" },
                ].map((item) => (
                  <button
                    key={item.yr}
                    type="button"
                    onClick={() => setHorizonYears(item.yr)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      horizonYears === item.yr
                        ? "bg-amber-500 text-white shadow-xs"
                        : "text-slate-700 hover:text-slate-900 hover:bg-slate-200"
                    }`}
                    title={item.desc}
                  >
                    {item.label}
                  </button>
                ))}
              </div>

              {/* Start Date */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500">Starting from:</span>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="text-xs rounded-lg border-slate-300 px-2.5 py-1 border bg-white focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                />
              </div>
            </div>

            <button
              type="button"
              onClick={handleGenerateRoadmap}
              disabled={calculating}
              className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-700 hover:to-amber-800 text-white rounded-xl text-sm font-semibold shadow-sm transition-all disabled:opacity-50"
            >
              {calculating ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Evaluating Multi-Year Chart...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Generate Life Roadmap
                </>
              )}
            </button>
          </div>

          {errorMsg && (
            <div className="mt-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}
        </div>

        {/* RESULTS SECTION */}
        {roadmapData && (
          <div className="space-y-6">
            {/* Native & Chart Overview Card */}
            <div className="bg-gradient-to-br from-slate-900 to-slate-800 text-white rounded-2xl p-6 shadow-md">
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 text-xs font-medium text-amber-300">
                    <User className="w-4 h-4" />
                    <span>{roadmapData.customer_name || "Native"}</span>
                    <span>&bull;</span>
                    <span>Lagna: {roadmapData.lagna}</span>
                    <span>&bull;</span>
                    <span>Moon: {roadmapData.moon_sign} ({roadmapData.nakshatra})</span>
                  </div>
                  <h2 className="text-2xl font-bold tracking-tight mt-1 text-white">
                    {roadmapData.horizon_years}-Year Life Roadmap ({roadmapData.start_date} to {roadmapData.end_date})
                  </h2>
                  <p className="text-sm text-slate-300 mt-1 max-w-3xl">
                    {roadmapData.overall_summary.executive_verdict}
                  </p>
                </div>

                {roadmapData.running_period_key && (
                  <div className="shrink-0 bg-white/10 backdrop-blur-xs border border-white/20 rounded-xl p-3 text-right">
                    <span className="text-[11px] uppercase tracking-wider text-amber-300 font-semibold block">
                      Active Running Dasha
                    </span>
                    <span className="text-base font-bold text-white tracking-wide">
                      {roadmapData.running_period_key}
                    </span>
                    <span className="inline-block mt-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
                      RUNNING NOW
                    </span>
                  </div>
                )}
              </div>

              {/* 4 Stat Badges */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6 pt-5 border-t border-white/10">
                <div className="bg-white/5 rounded-xl p-3 border border-white/5">
                  <span className="text-[11px] text-slate-400 block font-medium">DBA Periods</span>
                  <span className="text-xl font-bold text-white mt-0.5 block">
                    {roadmapData.overall_summary.total_dba_periods}
                  </span>
                </div>
                <div className="bg-white/5 rounded-xl p-3 border border-white/5">
                  <span className="text-[11px] text-emerald-400 block font-medium">🟢 High Probability Windows</span>
                  <span className="text-xl font-bold text-emerald-300 mt-0.5 block">
                    {roadmapData.overall_summary.high_probability_count}
                  </span>
                </div>
                <div className="bg-white/5 rounded-xl p-3 border border-white/5">
                  <span className="text-[11px] text-amber-400 block font-medium">🟡 Moderate / Delays</span>
                  <span className="text-xl font-bold text-amber-300 mt-0.5 block">
                    {roadmapData.overall_summary.moderate_count}
                  </span>
                </div>
                <div className="bg-white/5 rounded-xl p-3 border border-white/5">
                  <span className="text-[11px] text-rose-400 block font-medium">🔴 Caution Alerts</span>
                  <span className="text-xl font-bold text-rose-300 mt-0.5 block">
                    {roadmapData.overall_summary.caution_alerts_count}
                  </span>
                </div>
              </div>
            </div>

            {/* View Navigation Tabs */}
            <div className="flex items-center justify-between border-b border-slate-200">
              <div className="flex items-center gap-1 sm:gap-2">
                {[
                  { key: "roadmap", label: "Timeline Roadmap", icon: Layers },
                  { key: "scorecards", label: "5 Life Domains", icon: Compass },
                  { key: "milestones", label: "Key Milestones", icon: Sparkles },
                  { key: "report", label: "Executive Report", icon: Printer },
                ].map((t) => {
                  const Icon = t.icon;
                  const isActive = viewTab === t.key;
                  return (
                    <button
                      key={t.key}
                      type="button"
                      onClick={() => setViewTab(t.key as any)}
                      className={`inline-flex items-center gap-1.5 px-3 sm:px-4 py-2.5 text-xs sm:text-sm font-semibold border-b-2 transition-all ${
                        isActive
                          ? "border-amber-600 text-amber-800 bg-amber-50/50"
                          : "border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300"
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      {t.label}
                    </button>
                  );
                })}
              </div>

              {/* Action buttons */}
              <div className="flex items-center gap-2 pb-1">
                <button
                  type="button"
                  onClick={handleCopyMarkdown}
                  className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 shadow-2xs"
                >
                  {copiedReport ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                  {copiedReport ? "Copied" : "Copy Report"}
                </button>
              </div>
            </div>

            {/* TAB 1: TIMELINE ROADMAP */}
            {viewTab === "roadmap" && (
              <div className="space-y-5">
                {/* Filter Toolbar */}
                <div className="bg-white rounded-xl border border-slate-200 p-3.5 flex flex-col md:flex-row md:items-center justify-between gap-3 shadow-2xs">
                  {/* Domain Filters */}
                  <div className="flex flex-wrap items-center gap-1.5">
                    <span className="text-xs font-semibold text-slate-500 uppercase mr-1">Domain:</span>
                    <button
                      type="button"
                      onClick={() => setActiveDomainFilter("all")}
                      className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-all ${
                        activeDomainFilter === "all"
                          ? "bg-slate-900 text-white"
                          : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                      }`}
                    >
                      All Domains
                    </button>
                    {domains.map((d) => {
                      const Icon = DOMAIN_ICONS[d.id] || Compass;
                      const isSel = activeDomainFilter === d.id;
                      return (
                        <button
                          key={d.id}
                          type="button"
                          onClick={() => setActiveDomainFilter(d.id)}
                          className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold transition-all ${
                            isSel
                              ? "bg-amber-600 text-white shadow-2xs"
                              : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                          }`}
                        >
                          <Icon className="w-3 h-3" />
                          {d.name.split(" ")[0]}
                        </button>
                      );
                    })}
                  </div>

                  {/* Probability Filter & Search */}
                  <div className="flex items-center gap-2">
                    <select
                      value={activeProbFilter}
                      onChange={(e) => setActiveProbFilter(e.target.value)}
                      className="text-xs rounded-lg border-slate-300 bg-white px-2.5 py-1.5 border focus:ring-2 focus:ring-amber-500 focus:outline-hidden"
                    >
                      <option value="all">All Probabilities</option>
                      <option value="high">🟢 High / Favorable Only</option>
                      <option value="moderate">🟡 Moderate / Delays</option>
                      <option value="caution">🔴 Caution Alerts Only</option>
                    </select>

                    <div className="relative">
                      <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
                      <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search event or Dasha..."
                        className="text-xs rounded-lg border-slate-300 pl-8 pr-2.5 py-1.5 border bg-white focus:ring-2 focus:ring-amber-500 focus:outline-hidden w-36 sm:w-44"
                      />
                    </div>
                  </div>
                </div>

                {/* Chronological Timeline Cards */}
                {filteredPeriods.length === 0 ? (
                  <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center text-slate-500">
                    <AlertCircle className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                    <p className="text-sm font-medium">No periods match the current filters.</p>
                    <button
                      type="button"
                      onClick={() => {
                        setActiveDomainFilter("all");
                        setActiveProbFilter("all");
                        setSearchQuery("");
                      }}
                      className="mt-3 text-xs font-semibold text-amber-700 hover:underline"
                    >
                      Reset all filters
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {filteredPeriods.map((period, pIdx) => {
                      const isExpanded = expandedPeriodKey === period.period_key;
                      const hasHigh = period.all_milestones.some((m) => m.probability_level === "HIGH");
                      const hasCaution = period.all_milestones.some((m) => m.probability_level === "CAUTION");

                      return (
                        <div
                          key={period.period_key}
                          className={`bg-white rounded-2xl border transition-all ${
                            period.is_running
                              ? "border-amber-400 ring-2 ring-amber-400/20 shadow-md"
                              : "border-slate-200 hover:border-slate-300 shadow-2xs"
                          }`}
                        >
                          {/* Period Header */}
                          <div
                            onClick={() =>
                              setExpandedPeriodKey(isExpanded ? null : period.period_key)
                            }
                            className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 cursor-pointer select-none"
                          >
                            <div className="flex items-start sm:items-center gap-3">
                              <div
                                className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 font-bold text-xs ${
                                  period.is_running
                                    ? "bg-amber-500 text-white"
                                    : hasCaution
                                    ? "bg-rose-100 text-rose-800"
                                    : hasHigh
                                    ? "bg-emerald-100 text-emerald-800"
                                    : "bg-slate-100 text-slate-700"
                                }`}
                              >
                                {pIdx + 1}
                              </div>

                              <div>
                                <div className="flex flex-wrap items-center gap-2">
                                  <h3 className="text-base font-bold text-slate-900 tracking-tight">
                                    {period.period_key}
                                  </h3>

                                  {period.is_running && (
                                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-300 animate-pulse">
                                      RUNNING NOW
                                    </span>
                                  )}

                                  {hasCaution && (
                                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800 border border-rose-300">
                                      <AlertTriangle className="w-3 h-3 mr-1" /> Caution Flag
                                    </span>
                                  )}

                                  {hasHigh && (
                                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                                      <Sparkles className="w-3 h-3 mr-1" /> Key Breakthrough
                                    </span>
                                  )}
                                </div>

                                <div className="flex items-center gap-2 text-xs text-slate-500 mt-0.5">
                                  <Calendar className="w-3.5 h-3.5" />
                                  <span>
                                    {period.start_display} &ndash; {period.end_display}
                                  </span>
                                  <span>&bull;</span>
                                  <span>{period.duration_days} days</span>
                                </div>
                              </div>
                            </div>

                            {/* Right summary badges & toggle */}
                            <div className="flex items-center justify-between sm:justify-end gap-3 w-full sm:w-auto">
                              {/* Domain pills */}
                              <div className="flex items-center gap-1.5 flex-wrap">
                                {Object.entries(period.domain_highlights).map(([dId, dColor]) => {
                                  const Icon = DOMAIN_ICONS[dId] || Compass;
                                  return (
                                    <span
                                      key={dId}
                                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-medium ${
                                        dColor === "green"
                                          ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                                          : dColor === "orange"
                                          ? "bg-amber-50 text-amber-800 border border-amber-200"
                                          : "bg-slate-100 text-slate-600"
                                      }`}
                                      title={`Active in ${dId}`}
                                    >
                                      <Icon className="w-2.5 h-2.5" />
                                      {dId.slice(0, 4)}
                                    </span>
                                  );
                                })}
                              </div>

                              <div className="text-slate-400">
                                {isExpanded ? (
                                  <ChevronUp className="w-5 h-5" />
                                ) : (
                                  <ChevronDown className="w-5 h-5" />
                                )}
                              </div>
                            </div>
                          </div>

                          {/* Period Body: Milestones */}
                          {isExpanded && (
                            <div className="px-4 pb-5 sm:px-6 pt-2 border-t border-slate-100">
                              <div className="space-y-3">
                                {period.all_milestones.length === 0 ? (
                                  <p className="text-xs text-slate-500 italic py-2">
                                    No prominent events flagged under active filters.
                                  </p>
                                ) : (
                                  period.all_milestones.map((m, mIdx) => {
                                    const isCaution = m.is_caution_type;
                                    const isSelected = selectedMilestone?.event_name === m.event_name;

                                    return (
                                      <div
                                        key={mIdx}
                                        onClick={() =>
                                          setSelectedMilestone(isSelected ? null : m)
                                        }
                                        className={`p-3 sm:p-4 rounded-xl border transition-all cursor-pointer ${
                                          m.color === "green"
                                            ? "bg-emerald-50/60 border-emerald-200 hover:border-emerald-300"
                                            : m.color === "red"
                                            ? "bg-rose-50/60 border-rose-200 hover:border-rose-300"
                                            : "bg-amber-50/40 border-amber-200 hover:border-amber-300"
                                        }`}
                                      >
                                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                                          <div className="flex items-center gap-2">
                                            <span
                                              className={`w-2.5 h-2.5 rounded-full shrink-0 ${
                                                m.color === "green"
                                                  ? "bg-emerald-500"
                                                  : m.color === "red"
                                                  ? "bg-rose-500"
                                                  : "bg-amber-500"
                                              }`}
                                            />
                                            <h4 className="text-sm font-bold text-slate-900">
                                              {m.event_name}
                                            </h4>
                                            <span className="text-xs text-slate-500">
                                              &bull; {m.domain_name}
                                            </span>
                                          </div>

                                          <div className="flex items-center gap-2">
                                            <span
                                              className={`px-2 py-0.5 rounded-full text-[11px] font-semibold ${
                                                m.color === "green"
                                                  ? "bg-emerald-100 text-emerald-800"
                                                  : m.color === "red"
                                                  ? "bg-rose-100 text-rose-800"
                                                  : "bg-amber-100 text-amber-800"
                                              }`}
                                            >
                                              {m.status_label}
                                            </span>
                                          </div>
                                        </div>

                                        <p className="text-xs text-slate-700 mt-2 font-medium">
                                          {m.hint}
                                        </p>

                                        {/* Evidence Chips */}
                                        <div className="flex flex-wrap items-center gap-2 mt-2 pt-2 border-t border-slate-200/50 text-[11px] text-slate-600">
                                          <span>
                                            <strong>Supporting Houses:</strong>{" "}
                                            {m.supporting_houses.length > 0
                                              ? m.supporting_houses
                                                  .map((h) => `${h.house}(${h.level})`)
                                                  .join(", ")
                                              : "None"}
                                          </span>
                                          {m.denying_houses.length > 0 && (
                                            <>
                                              <span>&bull;</span>
                                              <span className="text-rose-700">
                                                <strong>Denying Houses:</strong>{" "}
                                                {m.denying_houses
                                                  .map((h) => `${h.house}(${h.level})`)
                                                  .join(", ")}
                                              </span>
                                            </>
                                          )}
                                          <span>&bull;</span>
                                          <span>
                                            Coverage: {(m.coverage * 100).toFixed(0)}%
                                          </span>
                                        </div>

                                        {/* Deep Astrological Details (Expand on click) */}
                                        {isSelected && (
                                          <div className="mt-3 pt-3 border-t border-slate-200/80 text-xs bg-white/70 p-3 rounded-lg space-y-1.5">
                                            <div className="font-semibold text-slate-900">
                                              Astrological Computation Mechanics:
                                            </div>
                                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
                                              <div>
                                                Support Score: <strong>{m.support_score}</strong>
                                              </div>
                                              <div>
                                                Denial Score: <strong>{m.denial_score}</strong>
                                              </div>
                                              <div>
                                                Coverage Ratio: <strong>{m.coverage}</strong>
                                              </div>
                                              <div>
                                                Denied Flag: <strong>{m.denied ? "YES" : "NO"}</strong>
                                              </div>
                                            </div>
                                            {m.csl_adjustment && (
                                              <div className="text-amber-800 text-[11px]">
                                                CSL Arbiter: {m.csl_adjustment}
                                              </div>
                                            )}
                                            {m.retrograde_note && (
                                              <div className="text-indigo-800 text-[11px]">
                                                Planetary Motion: {m.retrograde_note}
                                              </div>
                                            )}
                                          </div>
                                        )}
                                      </div>
                                    );
                                  })
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {/* TAB 2: 5 LIFE DOMAINS SCORECARDS */}
            {viewTab === "scorecards" && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                  {roadmapData.domain_scorecards.map((sc) => {
                    const Icon = DOMAIN_ICONS[sc.domain_id] || Compass;

                    return (
                      <div
                        key={sc.domain_id}
                        className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs hover:shadow-md transition-all flex flex-col justify-between"
                      >
                        <div>
                          <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-3">
                            <div className="flex items-center gap-2.5">
                              <div className="p-2 rounded-xl bg-amber-50 text-amber-800 border border-amber-200">
                                <Icon className="w-5 h-5" />
                              </div>
                              <div>
                                <h3 className="text-base font-bold text-slate-900 tracking-tight">
                                  {sc.domain_name}
                                </h3>
                                <p className="text-[11px] text-slate-500">{sc.domain_name_ta}</p>
                              </div>
                            </div>

                            <span
                              className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                                sc.status_color === "green"
                                  ? "bg-emerald-100 text-emerald-800"
                                  : sc.status_color === "red"
                                  ? "bg-rose-100 text-rose-800"
                                  : "bg-amber-100 text-amber-800"
                              }`}
                            >
                              {sc.summary_label}
                            </span>
                          </div>

                          <p className="text-xs text-slate-600 mb-4">{sc.summary_text}</p>

                          {/* Counters */}
                          <div className="grid grid-cols-3 gap-2 bg-slate-50 p-2.5 rounded-xl border border-slate-100 text-center text-xs mb-4">
                            <div>
                              <span className="text-[10px] text-emerald-700 block font-semibold">🟢 High</span>
                              <span className="font-bold text-slate-900">{sc.green_count}</span>
                            </div>
                            <div>
                              <span className="text-[10px] text-amber-700 block font-semibold">🟡 Moderate</span>
                              <span className="font-bold text-slate-900">{sc.orange_count}</span>
                            </div>
                            <div>
                              <span className="text-[10px] text-rose-700 block font-semibold">🔴 Caution</span>
                              <span className="font-bold text-slate-900">{sc.caution_alert_count}</span>
                            </div>
                          </div>

                          {/* Peak Window Highlight */}
                          {sc.peak_window_event && (
                            <div className="p-3 rounded-xl bg-amber-50/70 border border-amber-200 text-xs text-amber-900 space-y-1">
                              <span className="text-[10px] font-bold uppercase tracking-wider text-amber-800 block">
                                Prime Manifestation Window:
                              </span>
                              <div className="font-semibold">{sc.peak_window_event}</div>
                              <div className="text-[11px] text-amber-700">{sc.peak_window_dates}</div>
                              <div className="text-[10px] text-amber-800 font-mono">Dasha: {sc.peak_window_period}</div>
                            </div>
                          )}
                        </div>

                        {/* Filter by this domain button */}
                        <div className="mt-4 pt-3 border-t border-slate-100">
                          <button
                            type="button"
                            onClick={() => {
                              setActiveDomainFilter(sc.domain_id);
                              setViewTab("roadmap");
                            }}
                            className="w-full py-1.5 px-3 rounded-lg text-xs font-semibold text-amber-800 bg-amber-50 hover:bg-amber-100 transition-colors flex items-center justify-center gap-1.5"
                          >
                            View {sc.domain_name} in Timeline
                            <ArrowRight className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* TAB 3: KEY MILESTONES SUMMARY */}
            {viewTab === "milestones" && (
              <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <div>
                    <h3 className="text-base font-bold text-slate-900">
                      Key Milestone Highlights Across {roadmapData.horizon_years} Years
                    </h3>
                    <p className="text-xs text-slate-500">
                      Top high-probability breakthroughs and active caution alerts across all domains.
                    </p>
                  </div>
                </div>

                <div className="divide-y divide-slate-100">
                  {roadmapData.upcoming_key_milestones.length === 0 ? (
                    <p className="text-xs text-slate-500 py-4 text-center">
                      No extreme peaks flagged. The multi-year cycle is balanced.
                    </p>
                  ) : (
                    roadmapData.upcoming_key_milestones.map((m, idx) => {
                      const Icon = DOMAIN_ICONS[m.domain_id] || Compass;
                      return (
                        <div key={idx} className="py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                          <div className="flex items-start gap-3">
                            <div
                              className={`p-2 rounded-xl mt-0.5 shrink-0 ${
                                m.color === "green"
                                  ? "bg-emerald-100 text-emerald-800"
                                  : m.color === "red"
                                  ? "bg-rose-100 text-rose-800"
                                  : "bg-amber-100 text-amber-800"
                              }`}
                            >
                              <Icon className="w-4 h-4" />
                            </div>

                            <div>
                              <div className="flex items-center gap-2">
                                <span className="text-sm font-bold text-slate-900">{m.event_name}</span>
                                <span className="text-xs text-slate-500">&bull; {m.domain_name}</span>
                              </div>
                              <p className="text-xs text-slate-600 mt-0.5">{m.hint}</p>
                            </div>
                          </div>

                          <div className="shrink-0 flex items-center gap-2 sm:self-center">
                            <span
                              className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                                m.color === "green"
                                  ? "bg-emerald-100 text-emerald-800 border border-emerald-200"
                                  : m.color === "red"
                                  ? "bg-rose-100 text-rose-800 border border-rose-200"
                                  : "bg-amber-100 text-amber-800 border border-amber-200"
                              }`}
                            >
                              {m.status_label}
                            </span>
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            )}

            {/* TAB 4: EXECUTIVE REPORT MARKDOWN */}
            {viewTab === "report" && (
              <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <div>
                    <h3 className="text-base font-bold text-slate-900">
                      Life Roadmap Executive Astrological Report
                    </h3>
                    <p className="text-xs text-slate-500">
                      Standardized markdown document ready for client delivery and records.
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={handleCopyMarkdown}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-slate-900 rounded-lg hover:bg-slate-800"
                  >
                    {copiedReport ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                    {copiedReport ? "Copied" : "Copy to Clipboard"}
                  </button>
                </div>

                <div className="bg-slate-50 rounded-xl p-4 sm:p-6 border border-slate-200 font-mono text-xs text-slate-800 whitespace-pre-wrap leading-relaxed overflow-x-auto max-h-[600px] overflow-y-auto">
                  {roadmapData.executive_roadmap_markdown}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default function LifeRoadmapPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-[#F8FAFC]">
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <RefreshCw className="w-4 h-4 animate-spin text-amber-600" />
            Loading Life Roadmap...
          </div>
        </div>
      }
    >
      <LifeRoadmapContent />
    </Suspense>
  );
}
