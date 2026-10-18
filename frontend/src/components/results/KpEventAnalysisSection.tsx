"use client";

import React, { useState, useEffect, useMemo, useCallback } from "react";
import {
  KpResponse,
  DasaResponse,
  HoroscopeResponse,
  KpEventAnalysisResponse,
  PeriodAnalysisResult,
  EventGradingDetail,
  SavedHoroscopeItem,
} from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { getLordName } from "@/lib/translations";
import { analyzeKpEvents, analyzeSavedHoroscopeKpEvents } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import {
  Sparkles,
  Calendar,
  Clock,
  Filter,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Search,
  FileText,
  SlidersHorizontal,
  Bookmark,
  Compass,
  ArrowRight,
  Info,
  ShieldCheck,
  RotateCcw,
} from "lucide-react";

interface KpEventAnalysisSectionProps {
  kp?: KpResponse;
  dasa?: DasaResponse;
  horoscope?: HoroscopeResponse;
  savedHoroscopeId?: string;
  onSelectSavedHoroscope?: (id: string) => void;
}

export function KpEventAnalysisSection({
  kp,
  dasa,
  horoscope,
  savedHoroscopeId,
  onSelectSavedHoroscope,
}: KpEventAnalysisSectionProps) {
  const { language, t } = useLanguage();
  const { session, isAuthenticated } = useAuth();

  // Calculation state
  const [analysisResult, setAnalysisResult] = useState<KpEventAnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Saved horoscopes list for Workflow A
  const [savedList, setSavedList] = useState<SavedHoroscopeItem[]>([]);
  const [selectedSavedId, setSelectedSavedId] = useState<string>(savedHoroscopeId || "");
  const [isLoadingSavedList, setIsLoadingSavedList] = useState<boolean>(false);

  // Filters
  const [periodFilter, setPeriodFilter] = useState<"all" | "running">("all");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [gradeFilter, setGradeFilter] = useState<string>("all");
  const [eventSearch, setEventSearch] = useState<string>("");
  const [startDateFilter, setStartDateFilter] = useState<string>("");
  const [endDateFilter, setEndDateFilter] = useState<string>("");

  // UI View: "cards" | "report"
  const [viewMode, setViewMode] = useState<"cards" | "report">("cards");
  const [expandedPeriodKeys, setExpandedPeriodKeys] = useState<Record<string, boolean>>({});
  const [copiedReport, setCopiedReport] = useState<boolean>(false);

  // Fetch list of saved horoscopes if user is authenticated
  useEffect(() => {
    if (isAuthenticated) {
      setIsLoadingSavedList(true);
      fetch("/api/horoscopes?limit=50")
        .then((res) => (res.ok ? res.json() : Promise.reject("Failed to fetch")))
        .then((data) => {
          if (data?.horoscopes) {
            setSavedList(data.horoscopes);
          }
        })
        .catch((err) => {
          console.warn("Could not load saved horoscopes list:", err);
        })
        .finally(() => {
          setIsLoadingSavedList(false);
        });
    }
  }, [isAuthenticated]);

  // Construct request payload from current kp, dasa, and horoscope objects
  const runDirectAnalysis = useCallback(async () => {
    if (!kp && !dasa && !horoscope) {
      return;
    }
    setIsLoading(true);
    setErrorMsg(null);

    try {
      // 1. Extract Lagna
      const lagnaName = horoscope?.ascendant?.sign_name || "Aries";

      // 2. Extract Significators
      // KpResponse provides house_significators (4 tiers A, B, C, D)
      const rawHouseSigs = kp?.house_significators || [];

      // 3. Extract CSL map
      const cslMap: Record<string, string> = {};
      if (kp?.cuspal_analysis) {
        for (const cusp of kp.cuspal_analysis) {
          if (cusp.house && cusp.sub_lord) {
            cslMap[String(cusp.house)] = cusp.sub_lord;
          }
        }
      }

      // 4. Extract Retrograde status
      const retroMap: Record<string, boolean> = {
        Rahu: true,
        Ketu: true,
      };
      if (horoscope?.planets) {
        for (const p of horoscope.planets) {
          retroMap[p.name] = Boolean(p.is_retrograde);
        }
      }

      // 5. Extract Dasha-Bhukti periods from dasa_tree or kp dasa_hierarchy
      const periods: Array<{
        mahadasha_lord: string;
        bhukti_lord: string;
        antara_lord?: string;
        start_date: string;
        end_date: string;
      }> = [];

      if (dasa?.dasa_tree && dasa.dasa_tree.length > 0) {
        for (const md of dasa.dasa_tree) {
          if (md.sub_periods && md.sub_periods.length > 0) {
            for (const bd of md.sub_periods) {
              periods.push({
                mahadasha_lord: md.lord,
                bhukti_lord: bd.lord,
                start_date: (bd.start_date_iso || "").split("T")[0],
                end_date: (bd.end_date_iso || "").split("T")[0],
              });
            }
          } else {
            periods.push({
              mahadasha_lord: md.lord,
              bhukti_lord: md.lord,
              start_date: (md.start_date_iso || "").split("T")[0],
              end_date: (md.end_date_iso || "").split("T")[0],
            });
          }
        }
      } else if (kp?.dasa_hierarchy?.mahadashas) {
        for (const md of kp.dasa_hierarchy.mahadashas) {
          periods.push({
            mahadasha_lord: md.lord,
            bhukti_lord: md.lord,
            start_date: md.start_date.split("T")[0],
            end_date: md.end_date.split("T")[0],
          });
        }
      }

      if (periods.length === 0) {
        throw new Error("No Dasha periods found to analyze.");
      }

      const token = session?.access_token;
      const res = await analyzeKpEvents(
        {
          lagna: lagnaName,
          periods,
          significations: rawHouseSigs,
          csl_significations: cslMap,
          retrograde_status: retroMap,
          timezone: horoscope?.metadata?.local_timezone || "Asia/Kolkata",
          save_horoscope_id: savedHoroscopeId,
        },
        token
      );

      setAnalysisResult(res);
    } catch (err: unknown) {
      console.error("KP Event Analysis failed:", err);
      setErrorMsg((err as Error)?.message || "Failed to calculate KP event predictions.");
    } finally {
      setIsLoading(false);
    }
  }, [kp, dasa, horoscope, savedHoroscopeId, session]);

  // Workflow A: Run analysis for a selected saved horoscope
  const runSavedAnalysis = useCallback(
    async (id: string, forceRegen = false) => {
      if (!id || !session?.access_token) return;
      setIsLoading(true);
      setErrorMsg(null);

      try {
        const res = await analyzeSavedHoroscopeKpEvents(session.access_token, id, {
          regenerate: forceRegen,
        });
        setAnalysisResult(res);
        if (onSelectSavedHoroscope) {
          onSelectSavedHoroscope(id);
        }
      } catch (err: unknown) {
        console.error("Failed to analyze saved horoscope:", err);
        setErrorMsg((err as Error)?.message || "Could not analyze the selected saved horoscope.");
      } finally {
        setIsLoading(false);
      }
    },
    [session, onSelectSavedHoroscope]
  );

  // Trigger analysis when inputs are ready
  useEffect(() => {
    if (selectedSavedId && session?.access_token) {
      runSavedAnalysis(selectedSavedId);
    } else if (kp && (dasa || kp.dasa_hierarchy)) {
      runDirectAnalysis();
    }
  }, [selectedSavedId, kp, dasa, session?.access_token, runSavedAnalysis, runDirectAnalysis]);

  // Handle saved horoscope dropdown selection
  const handleSavedSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newId = e.target.value;
    setSelectedSavedId(newId);
    if (newId) {
      runSavedAnalysis(newId);
    }
  };

  // Toggle period expansion
  const togglePeriodExpanded = (key: string) => {
    setExpandedPeriodKeys((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  // Copy human-readable report to clipboard
  const handleCopyReport = () => {
    if (!analysisResult?.human_readable_report) return;
    navigator.clipboard.writeText(analysisResult.human_readable_report);
    setCopiedReport(true);
    setTimeout(() => setCopiedReport(false), 2000);
  };

  // Filter periods based on user criteria
  const filteredPeriods = useMemo(() => {
    if (!analysisResult?.periods) return [];

    return analysisResult.periods.filter((p) => {
      // 1. Running filter
      if (periodFilter === "running" && !p.running) {
        return false;
      }

      // 2. Date range filter
      if (startDateFilter && p.end < startDateFilter) {
        return false;
      }
      if (endDateFilter && p.start > endDateFilter) {
        return false;
      }

      // 3. Event / Grade / Category search
      if (categoryFilter !== "all" || gradeFilter !== "all" || eventSearch.trim() !== "") {
        const matchingEvents = p.events.filter((e) => {
          if (gradeFilter !== "all" && e.color.toLowerCase() !== gradeFilter.toLowerCase()) {
            return false;
          }
          if (eventSearch.trim() !== "") {
            const q = eventSearch.toLowerCase().trim();
            if (!e.event.toLowerCase().includes(q)) {
              return false;
            }
          }
          return true;
        });

        if (matchingEvents.length === 0) {
          return false;
        }
      }

      return true;
    });
  }, [
    analysisResult,
    periodFilter,
    categoryFilter,
    gradeFilter,
    eventSearch,
    startDateFilter,
    endDateFilter,
  ]);

  return (
    <div className="space-y-6">
      {/* 1. Header & Saved Horoscope Workflow A Selector */}
      <div className="p-4 sm:p-5 rounded-2xl border border-[#E2DCD5] bg-gradient-to-br from-white via-[#FCFAF7] to-[#F9F5EC] shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-[#FAF2DE] border border-[#D8BD80] text-[#784E0E]">
                <Sparkles className="w-4 h-4 text-[#B8860B]" />
              </span>
              <h3 className="font-serif text-lg font-bold text-[#0F172A]">
                {language === "ta" ? "KP தசா–புக்தி நிகழ்வு கணிப்பு எஞ்சின்" : "KP Dasha–Bhukti Event Prediction Engine"}
              </h3>
              <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
                Rule-Based KP
              </span>
            </div>
            <p className="text-xs text-[#64748B]">
              {language === "ta"
                ? "32 பாரம்பரிய KP நிகழ்வுகளுக்கான பாவக காரகத்துவங்கள் (L1-L4), CSL ஆய்வு மற்றும் தசா கால ஆதரவு முடிவுகள்."
                : "Deterministic rule-based analysis across 32 KP events using L1-L4 significator strengths, CSL arbiters, and delay factors."}
            </p>
          </div>

          {/* Workflow A: Saved Horoscope Selector */}
          {savedList.length > 0 && (
            <div className="flex items-center gap-2 bg-white px-3 py-2 rounded-xl border border-[#E2DCD5] shadow-2xs">
              <Bookmark className="w-4 h-4 text-[#B8860B] shrink-0" />
              <div className="flex flex-col">
                <span className="text-[10px] font-semibold text-[#64748B] uppercase tracking-wider">
                  {language === "ta" ? "சேமித்த ஜாதகம்" : "Saved Horoscope"}
                </span>
                <select
                  value={selectedSavedId}
                  onChange={handleSavedSelectChange}
                  disabled={isLoading}
                  className="text-xs font-bold text-[#0F172A] bg-transparent outline-none cursor-pointer max-w-[200px] truncate"
                >
                  <option value="">{language === "ta" ? "— தற்போதைய ஜாதகம் —" : "— Current Chart —"}</option>
                  {savedList.map((item) => (
                    <option key={item.id} value={item.id}>
                      #{item.display_number} - {item.person_name} ({item.birth_date})
                    </option>
                  ))}
                </select>
              </div>
              {selectedSavedId && (
                <button
                  type="button"
                  title="Recalculate analysis"
                  onClick={() => runSavedAnalysis(selectedSavedId, true)}
                  disabled={isLoading}
                  className="p-1 text-[#64748B] hover:text-[#0F172A] rounded transition-colors"
                >
                  <RotateCcw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
                </button>
              )}
            </div>
          )}
        </div>

        {/* Persistence Notice / Warning Banner */}
        {(analysisResult?.persistence_warning || analysisResult?.overall_summary?.persistence_warning) && (
          <div className="mt-3 p-3 rounded-xl bg-amber-50/90 border border-amber-200 flex items-start gap-2.5 text-xs text-amber-900 shadow-2xs">
            <span className="text-amber-700 text-sm">⚠️</span>
            <div className="flex-1">
              <span className="font-semibold block">{language === "ta" ? "தற்காலிக சேமிப்பு அறிவிப்பு" : "Storage Notice"}</span>
              <span className="text-amber-800 text-[11px] leading-relaxed">
                {analysisResult.persistence_warning || analysisResult?.overall_summary?.persistence_warning}
              </span>
            </div>
          </div>
        )}

        {/* 2. Compact Summary Statistics Cards */}
        {analysisResult?.overall_summary && (
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5 mt-4 pt-4 border-t border-[#E8DEC8]">
            <div className="p-2.5 rounded-xl bg-white border border-[#E2DCD5] shadow-2xs">
              <span className="text-[10px] font-semibold text-[#64748B] uppercase tracking-wider block">
                {language === "ta" ? "காலங்கள்" : "Total Periods"}
              </span>
              <span className="text-base font-bold text-[#0F172A] font-mono">
                {analysisResult.overall_summary.total_periods}
              </span>
            </div>

            <div className="p-2.5 rounded-xl bg-emerald-50/70 border border-emerald-200 shadow-2xs">
              <span className="text-[10px] font-bold text-emerald-800 uppercase tracking-wider flex items-center gap-1">
                <span>🟢</span>
                <span>{language === "ta" ? "வலுவானது" : "Strong"}</span>
              </span>
              <span className="text-base font-extrabold text-emerald-900 font-mono">
                {analysisResult.overall_summary.green_count}
              </span>
            </div>

            <div className="p-2.5 rounded-xl bg-amber-50/70 border border-amber-200 shadow-2xs">
              <span className="text-[10px] font-bold text-amber-800 uppercase tracking-wider flex items-center gap-1">
                <span>🟠</span>
                <span>{language === "ta" ? "மிதமானது" : "Moderate"}</span>
              </span>
              <span className="text-base font-extrabold text-amber-900 font-mono">
                {analysisResult.overall_summary.orange_count}
              </span>
            </div>

            <div className="p-2.5 rounded-xl bg-rose-50/70 border border-rose-200 shadow-2xs">
              <span className="text-[10px] font-bold text-rose-800 uppercase tracking-wider flex items-center gap-1">
                <span>🔴</span>
                <span>{language === "ta" ? "பலவீனமானது" : "Weak"}</span>
              </span>
              <span className="text-base font-extrabold text-rose-900 font-mono">
                {analysisResult.overall_summary.red_count}
              </span>
            </div>

            <div className="p-2.5 rounded-xl bg-indigo-50/70 border border-indigo-200 shadow-2xs col-span-2 sm:col-span-1">
              <span className="text-[10px] font-bold text-indigo-800 uppercase tracking-wider block truncate">
                {language === "ta" ? "நடப்பு தசா-புக்தி" : "Running Period"}
              </span>
              <span className="text-xs font-bold text-indigo-900 truncate block mt-0.5">
                {analysisResult.overall_summary.running_period || "—"}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* 3. Filter Bar & View Mode Toggle */}
      <div className="p-4 rounded-xl bg-white border border-[#E2DCD5] shadow-2xs space-y-3">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
          {/* Quick Period Toggle */}
          <div className="flex items-center gap-1.5 bg-[#F1EFEA] p-1 rounded-lg">
            <button
              type="button"
              onClick={() => setPeriodFilter("all")}
              className={`px-3 py-1 text-xs font-bold rounded-md transition-all ${
                periodFilter === "all"
                  ? "bg-white text-[#0F172A] shadow-2xs"
                  : "text-[#64748B] hover:text-[#0F172A]"
              }`}
            >
              {language === "ta" ? "அனைத்து காலங்கள்" : "All Periods"}
            </button>
            <button
              type="button"
              onClick={() => setPeriodFilter("running")}
              className={`px-3 py-1 text-xs font-bold rounded-md transition-all flex items-center gap-1.5 ${
                periodFilter === "running"
                  ? "bg-emerald-600 text-white shadow-2xs"
                  : "text-[#64748B] hover:text-[#0F172A]"
              }`}
            >
              <Clock className="w-3 h-3" />
              <span>{language === "ta" ? "நடப்பு காலம் மட்டும்" : "Running Period"}</span>
            </button>
          </div>

          {/* View Mode Toggle & Copy */}
          <div className="flex items-center gap-2">
            <div className="flex items-center bg-[#F1EFEA] p-1 rounded-lg">
              <button
                type="button"
                onClick={() => setViewMode("cards")}
                className={`px-3 py-1 text-xs font-bold rounded-md transition-all ${
                  viewMode === "cards"
                    ? "bg-white text-[#0F172A] shadow-2xs"
                    : "text-[#64748B] hover:text-[#0F172A]"
                }`}
              >
                {language === "ta" ? "அட்டவணை / கார்டுகள்" : "Cards View"}
              </button>
              <button
                type="button"
                onClick={() => setViewMode("report")}
                className={`px-3 py-1 text-xs font-bold rounded-md transition-all flex items-center gap-1 ${
                  viewMode === "report"
                    ? "bg-white text-[#0F172A] shadow-2xs"
                    : "text-[#64748B] hover:text-[#0F172A]"
                }`}
              >
                <FileText className="w-3.5 h-3.5" />
                <span>{language === "ta" ? "அறிக்கை உரை" : "Human Report"}</span>
              </button>
            </div>

            {viewMode === "report" && (
              <button
                type="button"
                onClick={handleCopyReport}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#D8BD80] bg-[#FAF2DE] text-xs font-bold text-[#784E0E] hover:bg-[#FAF6EC] shadow-2xs cursor-pointer"
              >
                {copiedReport ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedReport ? (language === "ta" ? "நகலெடுக்கப்பட்டது!" : "Copied!") : (language === "ta" ? "நகலெடு" : "Copy Report")}</span>
              </button>
            )}
          </div>
        </div>

        {/* Detailed Secondary Filters */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5 pt-2 border-t border-[#F1EFEA] text-xs">
          {/* Grade filter */}
          <div>
            <label className="text-[10px] font-bold text-[#64748B] uppercase block mb-1">
              {language === "ta" ? "தரம் (Grade)" : "Filter by Grade"}
            </label>
            <select
              value={gradeFilter}
              onChange={(e) => setGradeFilter(e.target.value)}
              className="w-full px-2.5 py-1.5 rounded-lg border border-[#E2DCD5] bg-white text-xs font-medium text-[#0F172A] focus:outline-hidden focus:ring-1 focus:ring-[#B8860B]"
            >
              <option value="all">{language === "ta" ? "அனைத்து தரங்கள்" : "All Grades"}</option>
              <option value="green">🟢 Strong (Green)</option>
              <option value="orange">🟠 Moderate (Orange)</option>
              <option value="red">🔴 Weak (Red)</option>
            </select>
          </div>

          {/* Event Search */}
          <div>
            <label className="text-[10px] font-bold text-[#64748B] uppercase block mb-1">
              {language === "ta" ? "நிகழ்வு தேடல்" : "Search Event"}
            </label>
            <div className="relative">
              <input
                type="text"
                placeholder={language === "ta" ? "எ.கா. Marriage, Job..." : "e.g. Marriage, Job..."}
                value={eventSearch}
                onChange={(e) => setEventSearch(e.target.value)}
                className="w-full pl-7 pr-2.5 py-1.5 rounded-lg border border-[#E2DCD5] bg-white text-xs text-[#0F172A] focus:outline-hidden focus:ring-1 focus:ring-[#B8860B]"
              />
              <Search className="w-3.5 h-3.5 text-[#94A3B8] absolute left-2 top-2" />
            </div>
          </div>

          {/* Start Date */}
          <div>
            <label className="text-[10px] font-bold text-[#64748B] uppercase block mb-1">
              {language === "ta" ? "ஆரம்ப தேதி" : "From Date"}
            </label>
            <input
              type="date"
              value={startDateFilter}
              onChange={(e) => setStartDateFilter(e.target.value)}
              className="w-full px-2.5 py-1.5 rounded-lg border border-[#E2DCD5] bg-white text-xs text-[#0F172A] focus:outline-hidden focus:ring-1 focus:ring-[#B8860B]"
            />
          </div>

          {/* End Date */}
          <div>
            <label className="text-[10px] font-bold text-[#64748B] uppercase block mb-1">
              {language === "ta" ? "முடிவு தேதி" : "To Date"}
            </label>
            <input
              type="date"
              value={endDateFilter}
              onChange={(e) => setEndDateFilter(e.target.value)}
              className="w-full px-2.5 py-1.5 rounded-lg border border-[#E2DCD5] bg-white text-xs text-[#0F172A] focus:outline-hidden focus:ring-1 focus:ring-[#B8860B]"
            />
          </div>
        </div>
      </div>

      {/* 4. Loading & Error States */}
      {isLoading && (
        <div className="p-12 text-center bg-white rounded-xl border border-[#E2DCD5] space-y-3">
          <RefreshCw className="w-7 h-7 text-[#B8860B] animate-spin mx-auto" />
          <p className="text-sm font-semibold text-[#0F172A]">
            {language === "ta" ? "KP நிகழ்வு விதிகள் கணக்கிடப்படுகின்றன…" : "Evaluating KP Event Significations & Predictions…"}
          </p>
        </div>
      )}

      {errorMsg && !isLoading && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-900 text-xs flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0" />
          <div>
            <span className="font-bold">{language === "ta" ? "பிழை ஏற்பட்டது:" : "Calculation Error:"}</span>
            <p className="mt-0.5">{errorMsg}</p>
          </div>
        </div>
      )}

      {/* 5. Main Content: Cards View vs Report View */}
      {!isLoading && !errorMsg && analysisResult && (
        <>
          {viewMode === "report" ? (
            /* Human-Readable Monospace / Text View */
            <div className="p-5 rounded-2xl bg-[#0F172A] text-slate-100 font-mono text-xs shadow-md border border-slate-800 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800 text-slate-400">
                <span>Rule-Set Version: {analysisResult.rule_set_version}</span>
                <span>Current Date Context: {analysisResult.current_date}</span>
              </div>
              <pre className="whitespace-pre-wrap leading-relaxed overflow-x-auto text-[11px] sm:text-xs text-slate-200">
                {analysisResult.human_readable_report}
              </pre>
            </div>
          ) : (
            /* Cards View */
            <div className="space-y-4">
              {filteredPeriods.length === 0 ? (
                <div className="p-8 text-center bg-white rounded-xl border border-[#E2DCD5] text-[#64748B]">
                  <p className="font-medium">
                    {language === "ta"
                      ? "தேர்ந்தெடுக்கப்பட்ட வடிகட்டிகளுக்கு பொருந்தும் காலங்கள் எதுவும் இல்லை."
                      : "No periods matched the selected filters."}
                  </p>
                </div>
              ) : (
                filteredPeriods.map((period) => {
                  const isExpanded = Boolean(expandedPeriodKeys[period.period]);
                  const mdName = getLordName(period.mahadasha_lord, language);
                  const bdName = getLordName(period.bhukti_lord, language);

                  return (
                    <div
                      key={period.period}
                      className={`rounded-2xl border transition-all ${
                        period.running
                          ? "border-emerald-500 bg-white shadow-md ring-2 ring-emerald-500/20"
                          : "border-[#E2DCD5] bg-white hover:border-[#D8BD80] shadow-2xs"
                      }`}
                    >
                      {/* Period Header */}
                      <div className="px-4 py-3 sm:px-5 sm:py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#F1EFEA] bg-[#FAF8F5]/60 rounded-t-2xl">
                        <div className="flex items-center gap-2.5">
                          <span className="w-2.5 h-2.5 rounded-full bg-[#B8860B]" />
                          <div className="flex items-center gap-2">
                            <span className="font-serif text-sm sm:text-base font-bold text-[#0F172A]">
                              {mdName} — {bdName}
                            </span>
                            {period.antara_lord && (
                              <span className="text-xs text-[#64748B] font-mono">
                                ({period.antara_lord})
                              </span>
                            )}
                          </div>

                          {period.running && (
                            <span className="px-2 py-0.5 rounded-full bg-emerald-600 text-white font-bold text-[10px] tracking-wider uppercase animate-pulse flex items-center gap-1">
                              <span className="w-1.5 h-1.5 rounded-full bg-white animate-ping" />
                              <span>{language === "ta" ? "நடப்பு காலம்" : "Running Now"}</span>
                            </span>
                          )}
                        </div>

                        <div className="flex items-center gap-3 text-xs text-[#64748B] font-mono">
                          <Calendar className="w-3.5 h-3.5 text-[#B8860B]" />
                          <span>
                            {period.start} to {period.end}
                          </span>
                        </div>
                      </div>

                      {/* Period Events List */}
                      <div className="p-4 sm:p-5 space-y-3">
                        {period.status === "missing_data" ? (
                          <div className="p-3 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 text-xs">
                            <span className="font-bold">Data missing:</span>{" "}
                            {period.missing_fields?.join(", ") || "Required planetary significations missing."}
                          </div>
                        ) : period.events.length === 0 ? (
                          <p className="text-xs text-[#94A3B8] italic">
                            {language === "ta" ? "பொருந்தக்கூடிய நிகழ்வுகள் இல்லை." : "No qualifying events found for this period."}
                          </p>
                        ) : (
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            {period.events.map((ev) => {
                              const isGreen = ev.color === "green";
                              const isOrange = ev.color === "orange";

                              const cardBorderClass = isGreen
                                ? "border-emerald-200 bg-emerald-50/30"
                                : isOrange
                                ? "border-amber-200 bg-amber-50/30"
                                : "border-rose-200 bg-rose-50/20";

                              const badgeBgClass = isGreen
                                ? "bg-emerald-100 text-emerald-900 border-emerald-300"
                                : isOrange
                                ? "bg-amber-100 text-amber-900 border-amber-300"
                                : "bg-rose-100 text-rose-900 border-rose-300";

                              const emoji = isGreen ? "🟢" : isOrange ? "🟠" : "🔴";

                              return (
                                <div
                                  key={ev.event}
                                  className={`p-3.5 rounded-xl border ${cardBorderClass} shadow-2xs space-y-2`}
                                >
                                  {/* Event title & grade pill */}
                                  <div className="flex items-center justify-between gap-2">
                                    <div className="flex items-center gap-1.5">
                                      <span>{emoji}</span>
                                      <span className="font-bold text-xs sm:text-sm text-[#0F172A]">
                                        {ev.event}
                                      </span>
                                    </div>
                                    <span
                                      className={`px-2 py-0.5 text-[10px] font-extrabold uppercase rounded-md border tracking-wider ${badgeBgClass}`}
                                    >
                                      {ev.grade}
                                    </span>
                                  </div>

                                  {/* Supporting & Denying Houses */}
                                  <div className="space-y-1 text-[11px] font-mono">
                                    <div className="flex items-start gap-1">
                                      <span className="text-[#64748B] shrink-0 font-sans">Supporting:</span>
                                      <span className="font-semibold text-emerald-900">
                                        {ev.supporting.length > 0
                                          ? ev.supporting.map((h) => `${h.house}(${h.level})`).join(", ")
                                          : "none"}
                                      </span>
                                    </div>

                                    <div className="flex items-start gap-1">
                                      <span className="text-[#64748B] shrink-0 font-sans">Denying:</span>
                                      <span className="font-semibold text-rose-900">
                                        {ev.denying.length > 0
                                          ? ev.denying.map((h) => `${h.house}(${h.level})`).join(", ")
                                          : "none"}
                                      </span>
                                    </div>
                                  </div>

                                  {/* Hint (<= 20 words) */}
                                  <div className="p-2 rounded-lg bg-white/80 border border-[#E2DCD5]/60 text-[11px] text-[#334155] leading-relaxed">
                                    <span className="font-bold text-[#0F172A] font-sans">Hint: </span>
                                    {ev.hint}
                                  </div>

                                  {/* Badges: Retrograde delay, CSL adjustment, Denied */}
                                  <div className="flex flex-wrap items-center gap-1.5 pt-1">
                                    {ev.retrograde_note && (
                                      <span className="px-1.5 py-0.5 text-[10px] rounded font-semibold bg-amber-100 text-amber-800 border border-amber-200 flex items-center gap-1">
                                        <AlertTriangle className="w-2.5 h-2.5" />
                                        <span>Delay possible</span>
                                      </span>
                                    )}
                                    {ev.csl_adjustment && (
                                      <span
                                        className="px-1.5 py-0.5 text-[10px] rounded font-semibold bg-indigo-50 text-indigo-800 border border-indigo-200 flex items-center gap-1"
                                        title={ev.csl_adjustment}
                                      >
                                        <ShieldCheck className="w-2.5 h-2.5 text-indigo-600" />
                                        <span>CSL Adjusted</span>
                                      </span>
                                    )}
                                    {ev.denied && (
                                      <span className="px-1.5 py-0.5 text-[10px] rounded font-bold bg-rose-100 text-rose-800 border border-rose-200">
                                        🚫 Denied
                                      </span>
                                    )}
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        )}

                        {/* Optional View All Evaluated Events Drawer */}
                        {period.all_events && period.all_events.length > period.events.length && (
                          <div className="pt-2 border-t border-[#F1EFEA]">
                            <button
                              type="button"
                              onClick={() => togglePeriodExpanded(period.period)}
                              className="text-[11px] font-bold text-[#B8860B] hover:text-[#784E0E] flex items-center gap-1 cursor-pointer"
                            >
                              <span>
                                {isExpanded
                                  ? (language === "ta" ? "சுருக்குக" : "Hide remaining events")
                                  : (language === "ta"
                                      ? `மேலும் ${period.all_events.length - period.events.length} நிகழ்வுகளைக் காண்க`
                                      : `View all ${period.all_events.length} evaluated events for this period`)}
                              </span>
                              {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                            </button>

                            {isExpanded && (
                              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 mt-3 pt-3 border-t border-dashed border-[#E2DCD5]">
                                {period.all_events.slice(period.events.length).map((extraEv) => (
                                  <div
                                    key={extraEv.event}
                                    className="p-2 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5] text-[11px] space-y-1"
                                  >
                                    <div className="flex items-center justify-between">
                                      <span className="font-semibold text-[#0F172A] truncate">
                                        {extraEv.event}
                                      </span>
                                      <span
                                        className={`px-1.5 py-0.2 rounded text-[9px] font-extrabold uppercase ${
                                          extraEv.color === "green"
                                            ? "bg-emerald-100 text-emerald-800"
                                            : extraEv.color === "orange"
                                            ? "bg-amber-100 text-amber-800"
                                            : "bg-rose-100 text-rose-800"
                                        }`}
                                      >
                                        {extraEv.grade}
                                      </span>
                                    </div>
                                    <div className="text-[10px] text-[#64748B]">
                                      Supp: {extraEv.support_score} | Den: {extraEv.denial_score} | Cov:{" "}
                                      {(extraEv.coverage * 100).toFixed(0)}%
                                    </div>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          )}

          {/* Mandatory Final Disclaimer Line (Section 9) */}
          <div className="p-3.5 rounded-xl bg-[#FAF2DE] border border-[#D8BD80] text-center text-xs font-semibold text-[#784E0E] shadow-2xs">
            Indicative KP hint, confirm with CSL and transit before decisions.
          </div>

          {/* 6. Color Legend */}
          <div className="p-4 rounded-xl bg-white border border-[#E2DCD5] shadow-2xs space-y-2">
            <span className="text-xs font-bold text-[#0F172A] uppercase tracking-wider block">
              {language === "ta" ? "KP கணிப்பு தரம் மற்றும் வண்ண விளக்கம்" : "KP Prediction Grading & Color Legend"}
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
              <div className="flex items-start gap-2">
                <span className="text-base leading-none">🟢</span>
                <div>
                  <span className="font-bold text-emerald-950 block">STRONG (Green)</span>
                  <span className="text-[11px] text-[#64748B]">
                    Full coverage (100%), support &gt; 2× denial, both lords support, house 11 present for gain-type events.
                  </span>
                </div>
              </div>

              <div className="flex items-start gap-2">
                <span className="text-base leading-none">🟠</span>
                <div>
                  <span className="font-bold text-amber-950 block">MODERATE (Orange)</span>
                  <span className="text-[11px] text-[#64748B]">
                    Coverage &ge; 60%, support &gt; denial, at least 2 distinct supporting houses signified.
                  </span>
                </div>
              </div>

              <div className="flex items-start gap-2">
                <span className="text-base leading-none">🔴</span>
                <div>
                  <span className="font-bold text-rose-950 block">WEAK (Red)</span>
                  <span className="text-[11px] text-[#64748B]">
                    Coverage &lt; 60% or denial &ge; support. Denied when denial &gt; 1.5× support.
                  </span>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
