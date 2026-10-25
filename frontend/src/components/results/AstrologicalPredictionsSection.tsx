"use client";

import React, { useState, useEffect, useMemo, useCallback } from "react";
import {
  FullHoroscopeResult,
  PredictionCategoryGroup,
  PredictionSubcategory,
  EvaluatedPredictionRule,
} from "@/lib/types";
import {
  getPredictionCategories,
  evaluatePredictionRules,
  ApiError,
} from "@/lib/api";
import {
  Compass,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Sparkles,
  BookOpen,
  Filter,
  Search,
  RefreshCw,
  Layers,
  ChevronDown,
  ChevronUp,
  Info,
  ShieldAlert,
  ArrowRight,
  SlidersHorizontal,
  ExternalLink,
} from "lucide-react";

interface AstrologicalPredictionsSectionProps {
  horoscopeResult: FullHoroscopeResult;
  language: "en" | "ta";
}

export function AstrologicalPredictionsSection({
  horoscopeResult,
  language,
}: AstrologicalPredictionsSectionProps) {
  // Categories state
  const [categoryGroups, setCategoryGroups] = useState<PredictionCategoryGroup[]>([]);
  const [isLoadingCategories, setIsLoadingCategories] = useState<boolean>(true);
  const [categoriesError, setCategoriesError] = useState<string | null>(null);

  // Filter & Selection state
  const [selectedGroupCode, setSelectedGroupCode] = useState<string>("all");
  const [selectedCategorySlug, setSelectedCategorySlug] = useState<string>("marriage_prospects");
  const [selectedSubcategory, setSelectedSubcategory] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [chartScope, setChartScope] = useState<"d1" | "d9" | "both">("both");
  const [astrologySystem, setAstrologySystem] = useState<"all" | "vedic" | "kp">("all");
  const [showOnlyMatched, setShowOnlyMatched] = useState<boolean>(true);

  // Evaluation state
  const [isEvaluating, setIsEvaluating] = useState<boolean>(false);
  const [evaluationError, setEvaluationError] = useState<string | null>(null);
  const [evaluationResults, setEvaluationResults] = useState<EvaluatedPredictionRule[] | null>(null);
  const [evaluatedAt, setEvaluatedAt] = useState<string | null>(null);
  const [lastEvaluatedChartKey, setLastEvaluatedChartKey] = useState<string | null>(null);

  // Expanded rule card IDs for detailed rationale
  const [expandedRuleIds, setExpandedRuleIds] = useState<Set<string>>(new Set());

  // Generate unique chart signature for cache/re-evaluation detection
  const chartIdentityKey = useMemo(() => {
    const hid = horoscopeResult.savedId || "adhoc";
    const dt = horoscopeResult.clientInputs?.birthDate || horoscopeResult.horoscope?.metadata?.birth_utc_iso || "";
    const tm = horoscopeResult.clientInputs?.birthTime || "";
    const aya = horoscopeResult.horoscope?.metadata?.ayanamsa_id ?? 0;
    return `${hid}-${dt}-${tm}-aya${aya}`;
  }, [horoscopeResult]);

  // Load category library on mount
  useEffect(() => {
    let isMounted = true;
    async function loadCategories() {
      setIsLoadingCategories(true);
      setCategoriesError(null);
      try {
        const groups = await getPredictionCategories();
        if (isMounted) {
          setCategoryGroups(groups);
          // Default to first subcategory if available
          if (groups.length > 0 && groups[0].subcategories.length > 0) {
            setSelectedCategorySlug(groups[0].subcategories[0].slug);
          }
        }
      } catch (err: unknown) {
        if (isMounted) {
          const msg = err instanceof Error ? err.message : String(err);
          setCategoriesError(msg);
        }
      } finally {
        if (isMounted) setIsLoadingCategories(false);
      }
    }
    loadCategories();
    return () => {
      isMounted = false;
    };
  }, []);

  // Filtered subcategories based on selected group & search query
  const availableSubcategories = useMemo(() => {
    let list: (PredictionSubcategory & { group_code: string; group_name: string })[] = [];
    categoryGroups.forEach((g) => {
      if (selectedGroupCode === "all" || g.group_code === selectedGroupCode) {
        g.subcategories.forEach((sub) => {
          list.push({
            ...sub,
            group_code: g.group_code,
            group_name: language === "ta" ? g.group_name_ta : g.group_name_en,
          });
        });
      }
    });

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      list = list.filter(
        (item) =>
          item.name_en.toLowerCase().includes(q) ||
          item.name_ta.toLowerCase().includes(q) ||
          item.description_en.toLowerCase().includes(q) ||
          item.description_ta.toLowerCase().includes(q)
      );
    }
    return list;
  }, [categoryGroups, selectedGroupCode, searchQuery, language]);

  // Evaluator execution
  const executeEvaluation = useCallback(
    async (evaluateAll: boolean = false) => {
      setIsEvaluating(true);
      setEvaluationError(null);

      try {
        const categoryToQuery = evaluateAll ? undefined : selectedCategorySlug;
        const subcatToQuery = evaluateAll ? undefined : selectedSubcategory || undefined;

        const payload = {
          horoscope: horoscopeResult.horoscope,
          saved_horoscope_id: horoscopeResult.savedId,
          category_slug: categoryToQuery,
          subcategory: subcatToQuery,
          chart_scope: chartScope,
          astrology_system: astrologySystem,
          language: language,
          dasa: horoscopeResult.dasa as any,
          kp: horoscopeResult.kp as any,
        };

        const resp = await evaluatePredictionRules(payload);
        setEvaluationResults(resp.results);
        setEvaluatedAt(new Date().toLocaleTimeString());
        setLastEvaluatedChartKey(chartIdentityKey);

        // Auto-expand matched rules
        const matchedIds = new Set<string>();
        resp.results.forEach((r) => {
          if (r.matched) matchedIds.add(r.rule_id);
        });
        setExpandedRuleIds(matchedIds);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        setEvaluationError(msg);
      } finally {
        setIsEvaluating(false);
      }
    },
    [
      horoscopeResult,
      selectedCategorySlug,
      selectedSubcategory,
      chartScope,
      astrologySystem,
      language,
      chartIdentityKey,
    ]
  );

  // Auto re-evaluate when chart identity changes if previously evaluated
  useEffect(() => {
    if (lastEvaluatedChartKey && lastEvaluatedChartKey !== chartIdentityKey) {
      executeEvaluation(false);
    }
  }, [chartIdentityKey, lastEvaluatedChartKey, executeEvaluation]);

  // Toggle card expansion
  const toggleExpand = (ruleId: string) => {
    setExpandedRuleIds((prev) => {
      const next = new Set(prev);
      if (next.has(ruleId)) {
        next.delete(ruleId);
      } else {
        next.add(ruleId);
      }
      return next;
    });
  };

  // Filtered displayed rules
  const displayedRules = useMemo(() => {
    if (!evaluationResults) return [];
    if (showOnlyMatched) {
      return evaluationResults.filter((r) => r.matched);
    }
    return evaluationResults;
  }, [evaluationResults, showOnlyMatched]);

  const matchedCount = useMemo(() => {
    return evaluationResults ? evaluationResults.filter((r) => r.matched).length : 0;
  }, [evaluationResults]);

  const unevaluableCount = useMemo(() => {
    return evaluationResults ? evaluationResults.filter((r) => r.unevaluable).length : 0;
  }, [evaluationResults]);

  return (
    <section className="bg-white rounded-xl border border-[#D9DEE7] p-4 sm:p-6 shadow-2xs space-y-6">
      {/* 1. Header with Badge & Overview */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#F2F3F5] pb-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center text-[#B4872B] shrink-0">
              <Compass className="w-4 h-4" />
            </div>
            <h3 className="font-serif text-base sm:text-lg font-bold text-[#183047]">
              {language === "ta"
                ? "ஜோதிட விதிகள் மற்றும் கணிப்புகள்"
                : "Astrological Conditions & Predictions"}
            </h3>
            <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-[#FAF8F2] text-[#8C6D23] border border-[#D8BD80]/60">
              {language === "ta" ? "விதிமுறை இயந்திரம்" : "Rule Engine v1"}
            </span>
          </div>
          <p className="text-xs text-[#52667E] max-w-2xl">
            {language === "ta"
              ? "பாரம்பரிய வேத (பராசர) மற்றும் கே.பி விதிமுறைகளின்படி தற்போதைய ஜாதக அமைப்புகளை ஆராய்ந்து, சரியான சான்றுகளுடன் கூடிய கணிப்புகளை வழங்கும் பகுதி."
              : "Deterministic rule-based evaluation of the active horoscope against classical Parashari, Vedic, and KP canons with traceable evidence."}
          </p>
        </div>

        {/* Global Action Button */}
        <div className="flex items-center gap-2 self-start md:self-center flex-wrap">
          <button
            type="button"
            onClick={() => executeEvaluation(false)}
            disabled={isEvaluating}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-[#B4872B] hover:bg-[#8C6D23] text-white font-bold text-xs shadow-2xs transition-colors cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isEvaluating ? "animate-spin" : ""}`} />
            <span>
              {language === "ta" ? "தேர்ந்தெடுத்ததை கணி" : "Evaluate Selected"}
            </span>
          </button>

          <button
            type="button"
            onClick={() => executeEvaluation(true)}
            disabled={isEvaluating}
            title={language === "ta" ? "அனைத்து விதிகளையும் கணக்கிடு" : "Evaluate all categories"}
            className="inline-flex items-center gap-1 px-3 py-2 rounded-lg bg-[#F2F3F5] hover:bg-[#E2E8F0] border border-[#D9DEE7] text-xs font-semibold text-[#153F6B] transition-colors cursor-pointer disabled:opacity-50"
          >
            <span>{language === "ta" ? "அனைத்தும்" : "Evaluate All"}</span>
          </button>
        </div>
      </div>

      {/* 2. Control Filters & Selectors */}
      <div className="space-y-4 bg-[#F8FAFC] rounded-lg p-3.5 sm:p-4 border border-[#E2E8F0]">
        {/* Row A: Category Groups & Search */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 items-center">
          {/* Group Filter Dropdown */}
          <div className="space-y-1">
            <label className="text-[11px] font-bold text-[#52667E] uppercase tracking-wider">
              {language === "ta" ? "பிரிவுத் தொகுப்பு" : "Category Group"}
            </label>
            <select
              value={selectedGroupCode}
              onChange={(e) => {
                setSelectedGroupCode(e.target.value);
                setSelectedSubcategory("");
              }}
              className="w-full text-xs rounded-lg border border-[#D9DEE7] bg-white p-2 text-[#183047] font-medium focus:ring-1 focus:ring-[#B4872B] focus:border-[#B4872B]"
            >
              <option value="all">
                {language === "ta" ? "அனைத்து பிரிவுகள் (8 தொகுப்புகள்)" : "All Groups (8 Groups)"}
              </option>
              {categoryGroups.map((g) => (
                <option key={g.group_code} value={g.group_code}>
                  {language === "ta" ? g.group_name_ta : g.group_name_en}
                </option>
              ))}
            </select>
          </div>

          {/* Search Category Filter */}
          <div className="space-y-1 md:col-span-2">
            <label className="text-[11px] font-bold text-[#52667E] uppercase tracking-wider">
              {language === "ta" ? "விதிகள் அல்லது தலைப்பை தேடு" : "Search Categories & Rules"}
            </label>
            <div className="relative">
              <input
                type="text"
                placeholder={
                  language === "ta"
                    ? "திருமணம், வேலை, யோகம், நட்சத்திரம்..."
                    : "Search marriage, career, lagna, wealth, intimacy..."
                }
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg border border-[#D9DEE7] bg-white text-[#183047] placeholder-[#8190A6] focus:ring-1 focus:ring-[#B4872B] focus:border-[#B4872B]"
              />
              <Search className="w-3.5 h-3.5 text-[#8190A6] absolute left-2.5 top-2.5" />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery("")}
                  className="absolute right-2.5 top-2 text-[10px] text-[#8190A6] hover:text-[#183047]"
                >
                  Clear
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Row B: Subcategory Pills Carousel */}
        <div className="space-y-1.5">
          <label className="text-[11px] font-bold text-[#52667E] uppercase tracking-wider flex items-center justify-between">
            <span>{language === "ta" ? "துணைப் பிரிவு" : "Subcategory"}</span>
            <span className="text-[10px] font-mono text-[#8190A6]">
              {availableSubcategories.length} {language === "ta" ? "கிடைக்கின்றன" : "available"}
            </span>
          </label>
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
            {availableSubcategories.slice(0, 15).map((sub) => {
              const isSelected = selectedCategorySlug === sub.slug;
              return (
                <button
                  key={sub.slug}
                  type="button"
                  onClick={() => {
                    setSelectedCategorySlug(sub.slug);
                    setSelectedSubcategory(sub.slug);
                  }}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors cursor-pointer border ${
                    isSelected
                      ? "bg-[#153F6B] text-white border-[#153F6B] shadow-2xs"
                      : "bg-white text-[#52667E] border-[#D9DEE7] hover:bg-[#F2F3F5]"
                  }`}
                >
                  {language === "ta" ? sub.name_ta : sub.name_en}
                </button>
              );
            })}
          </div>
        </div>

        {/* Row C: Chart Scope & Astrology System Settings */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-[#E2E8F0] text-xs">
          <div className="flex items-center gap-4 flex-wrap">
            {/* Scope Selection */}
            <div className="flex items-center gap-1.5">
              <span className="text-[#8190A6] font-medium">
                {language === "ta" ? "சக்கரம்:" : "Scope:"}
              </span>
              <div className="inline-flex rounded-lg bg-white border border-[#D9DEE7] p-0.5">
                {(["both", "d1", "d9"] as const).map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => setChartScope(s)}
                    className={`px-2.5 py-1 rounded text-[11px] font-semibold uppercase ${
                      chartScope === s
                        ? "bg-[#FAF2DE] text-[#8C6D23] font-bold"
                        : "text-[#52667E] hover:text-[#183047]"
                    }`}
                  >
                    {s === "both" ? "D1 + D9" : s}
                  </button>
                ))}
              </div>
            </div>

            {/* Astrology System Selection */}
            <div className="flex items-center gap-1.5">
              <span className="text-[#8190A6] font-medium">
                {language === "ta" ? "முறைமை:" : "System:"}
              </span>
              <div className="inline-flex rounded-lg bg-white border border-[#D9DEE7] p-0.5">
                {(["all", "vedic", "kp"] as const).map((sys) => (
                  <button
                    key={sys}
                    type="button"
                    onClick={() => setAstrologySystem(sys)}
                    className={`px-2.5 py-1 rounded text-[11px] font-semibold capitalize ${
                      astrologySystem === sys
                        ? "bg-[#153F6B] text-white"
                        : "text-[#52667E] hover:text-[#183047]"
                    }`}
                  >
                    {sys === "all" ? (language === "ta" ? "அனைத்தும்" : "All") : sys}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Matched Only Toggle */}
          <div className="flex items-center gap-2">
            <label className="inline-flex items-center gap-1.5 text-xs text-[#183047] cursor-pointer">
              <input
                type="checkbox"
                checked={showOnlyMatched}
                onChange={(e) => setShowOnlyMatched(e.target.checked)}
                className="rounded border-[#D9DEE7] text-[#B4872B] focus:ring-[#B4872B]"
              />
              <span className="font-medium">
                {language === "ta" ? "பொருந்தியவை மட்டும்" : "Show matched only"}
              </span>
            </label>
          </div>
        </div>
      </div>

      {/* 3. Evaluation Status, Counts & Error Banner */}
      {evaluationError && (
        <div className="p-3.5 rounded-lg border border-rose-300 bg-rose-50 flex items-start gap-3 text-xs text-rose-800">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold">Evaluation Error</span>
            <p>{evaluationError}</p>
          </div>
        </div>
      )}

      {evaluationResults && !isEvaluating && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-3 rounded-lg bg-[#FAF8F2] border border-[#D8BD80]/50 text-xs text-[#8C6D23]">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span className="font-bold">
              {matchedCount} {language === "ta" ? "விதிகள் பொருந்தியுள்ளன" : "Matching Rules Found"}
            </span>
            <span className="text-[#8190A6]">
              ({evaluationResults.length} {language === "ta" ? "ஆராயப்பட்டது" : "evaluated"})
            </span>
            {unevaluableCount > 0 && (
              <span className="px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 text-[10px] font-mono">
                {unevaluableCount} unevaluable (data missing)
              </span>
            )}
          </div>
          {evaluatedAt && (
            <span className="text-[#8190A6] text-[11px] font-mono">
              {language === "ta" ? "கணிக்கப்பட்ட நேரம்:" : "Evaluated at:"} {evaluatedAt}
            </span>
          )}
        </div>
      )}

      {/* 4. Results Display List / Empty States */}
      {isEvaluating ? (
        <div className="py-12 flex flex-col items-center justify-center space-y-3 text-center">
          <RefreshCw className="w-7 h-7 text-[#B4872B] animate-spin" />
          <p className="text-xs font-semibold text-[#183047]">
            {language === "ta"
              ? "ஜாதக தரவுகள் சோதிக்கப்படுகின்றன..."
              : "Evaluating astrological conditions against chart evidence..."}
          </p>
        </div>
      ) : !evaluationResults ? (
        <div className="py-10 text-center space-y-3 bg-[#FAF8F2]/40 rounded-xl border border-dashed border-[#D8BD80]/70 p-6">
          <div className="w-10 h-10 rounded-full bg-[#FAF2DE] text-[#B4872B] mx-auto flex items-center justify-center">
            <Sparkles className="w-5 h-5" />
          </div>
          <div className="space-y-1">
            <h4 className="font-bold text-sm text-[#183047]">
              {language === "ta" ? "கணிப்புகளைத் தொடங்கவும்" : "Ready to Evaluate Predictions"}
            </h4>
            <p className="text-xs text-[#52667E] max-w-md mx-auto">
              {language === "ta"
                ? "ஒரு பிரிவை தேர்ந்தெடுத்து 'தேர்ந்தெடுத்ததை கணி' பொத்தானை அழுத்தவும். லக்னம், நவாம்சம் மற்றும் கிரக சேர்க்கைகள் ஆராயப்படும்."
                : "Select a category above and click 'Evaluate Selected' to verify planetary placements, aspects, and lordships."}
            </p>
          </div>
          <button
            type="button"
            onClick={() => executeEvaluation(false)}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-[#B4872B] hover:bg-[#8C6D23] text-white font-bold text-xs shadow-2xs transition-colors cursor-pointer"
          >
            <Compass className="w-3.5 h-3.5" />
            <span>{language === "ta" ? "இப்போதே கணி" : "Evaluate Predictions"}</span>
          </button>
        </div>
      ) : displayedRules.length === 0 ? (
        <div className="py-10 text-center space-y-2 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0] p-6">
          <Info className="w-6 h-6 text-[#8190A6] mx-auto" />
          <h4 className="font-bold text-xs sm:text-sm text-[#183047]">
            {language === "ta"
              ? "இந்த பிரிவில் விதிகள் பொருந்தவில்லை"
              : "No Rules Matched for This Selection"}
          </h4>
          <p className="text-xs text-[#8190A6] max-w-md mx-auto">
            {language === "ta"
              ? "தற்போதைய ஜாதக அமைப்புகளுக்குரிய குறிப்பிட்ட நிபந்தனைகள் இதில் பூர்த்தியாகவில்லை."
              : "The planetary configurations in this horoscope do not meet the classical criteria for the selected category."}
          </p>
          {showOnlyMatched && evaluationResults.length > 0 && (
            <button
              type="button"
              onClick={() => setShowOnlyMatched(false)}
              className="text-xs font-semibold text-[#153F6B] hover:underline cursor-pointer pt-2"
            >
              {language === "ta"
                ? "பொருந்தாத விதிகளையும் காரணங்களுடன் காண்க"
                : "Show non-matching rules to review reasons"}
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {displayedRules.map((rule) => {
            const isExpanded = expandedRuleIds.has(rule.rule_id);
            const severityColor =
              rule.severity === "favorable"
                ? "bg-emerald-50 text-emerald-800 border-emerald-300"
                : rule.severity === "unfavorable"
                ? "bg-rose-50 text-rose-800 border-rose-300"
                : rule.severity === "mixed"
                ? "bg-purple-50 text-purple-800 border-purple-300"
                : "bg-blue-50 text-blue-800 border-blue-300";

            return (
              <div
                key={rule.rule_id}
                className={`rounded-xl border transition-all ${
                  rule.matched
                    ? "bg-white border-[#D9DEE7] shadow-2xs hover:border-[#B4872B]"
                    : "bg-[#F8FAFC] border-[#E2E8F0] opacity-80"
                }`}
              >
                {/* Rule Card Header */}
                <div
                  onClick={() => toggleExpand(rule.rule_id)}
                  className="p-3.5 sm:p-4 flex items-start justify-between gap-3 cursor-pointer select-none"
                >
                  <div className="space-y-1.5 flex-1">
                    {/* Badges Row */}
                    <div className="flex items-center gap-2 flex-wrap text-[10px]">
                      <span className="font-mono font-bold text-[#8190A6]">
                        {rule.rule_id} v{rule.version}
                      </span>
                      <span className="px-2 py-0.5 rounded font-semibold bg-[#F2F3F5] text-[#153F6B] border border-[#D9DEE7]">
                        {rule.astrology_system.toUpperCase()}
                      </span>
                      <span className="px-2 py-0.5 rounded font-semibold bg-[#F2F3F5] text-[#52667E] border border-[#D9DEE7] uppercase">
                        {rule.chart_scope}
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded font-bold border ${severityColor}`}
                      >
                        {rule.severity.toUpperCase()}
                      </span>

                      {rule.matched ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold border border-emerald-300">
                          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                          <span>{language === "ta" ? "பொருந்தியது" : "Matched"}</span>
                        </span>
                      ) : rule.unevaluable ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 font-bold border border-amber-300">
                          <AlertCircle className="w-3 h-3 text-amber-600" />
                          <span>{language === "ta" ? "தரவு இல்லை" : "Unevaluable"}</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-gray-100 text-gray-700 font-medium">
                          <span>{language === "ta" ? "பொருந்தவில்லை" : "Not Matched"}</span>
                        </span>
                      )}
                    </div>

                    {/* Title */}
                    <h4 className="text-xs sm:text-sm font-bold text-[#183047]">
                      {language === "ta" && rule.name_ta ? rule.name_ta : rule.name_en}
                    </h4>

                    {/* Primary Interpretation Preview */}
                    <p className="text-xs text-[#52667E] leading-relaxed">
                      {language === "ta" && rule.interpretation_ta
                        ? rule.interpretation_ta
                        : rule.interpretation_en}
                    </p>
                  </div>

                  {/* Expand / Collapse Chevron */}
                  <div className="pt-1 text-[#8190A6]">
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4" />
                    ) : (
                      <ChevronDown className="w-4 h-4" />
                    )}
                  </div>
                </div>

                {/* Collapsible Details Drawer */}
                {isExpanded && (
                  <div className="p-3.5 sm:p-4 border-t border-[#F2F3F5] bg-[#FAF8F2]/30 space-y-3.5 text-xs">
                    {/* 1. Exact Chart Evidence */}
                    <div className="space-y-1.5 bg-white p-3 rounded-lg border border-[#D9DEE7]">
                      <div className="flex items-center gap-1.5 text-[11px] font-bold text-[#153F6B] uppercase tracking-wider">
                        <CheckCircle2 className="w-3.5 h-3.5 text-[#B4872B]" />
                        <span>{language === "ta" ? "ஜாதக சான்றுகள்" : "Exact Chart Evidence"}</span>
                      </div>
                      {rule.chart_evidence.length > 0 ? (
                        <ul className="space-y-1 pl-4 list-disc text-xs text-[#183047] font-medium">
                          {rule.chart_evidence.map((ev, idx) => (
                            <li key={idx} className="font-mono text-[11px]">
                              {ev}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-[#8190A6] italic text-[11px]">
                          {rule.unevaluable_reason || "No matching chart evidence found."}
                        </p>
                      )}
                    </div>

                    {/* 2. Astrological Principle & Reasoning */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div className="space-y-1 bg-white p-3 rounded-lg border border-[#D9DEE7]">
                        <span className="text-[11px] font-bold text-[#52667E] uppercase tracking-wider block">
                          {language === "ta" ? "ஜோதிட தத்துவம்" : "Astrological Principle"}
                        </span>
                        <p className="text-xs text-[#52667E] leading-relaxed">
                          {language === "ta" && rule.astrological_principle_ta
                            ? rule.astrological_principle_ta
                            : rule.astrological_principle_en}
                        </p>
                      </div>

                      <div className="space-y-1 bg-white p-3 rounded-lg border border-[#D9DEE7]">
                        <span className="text-[11px] font-bold text-[#52667E] uppercase tracking-wider block">
                          {language === "ta" ? "காரணம் மற்றும் தர்க்கம்" : "Match Reasoning"}
                        </span>
                        <ul className="space-y-1 text-xs text-[#52667E]">
                          {rule.match_reasons.map((r, i) => (
                            <li key={i} className="flex items-start gap-1.5">
                              <span className="text-[#B4872B] mt-0.5">•</span>
                              <span>{r}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    {/* 3. Source Reference & Limitations */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pt-2 border-t border-[#D9DEE7]/70 text-[11px] text-[#8190A6]">
                      {rule.source_reference && (
                        <div className="flex items-center gap-1">
                          <BookOpen className="w-3.5 h-3.5 text-[#B4872B] shrink-0" />
                          <span>
                            <strong className="text-[#52667E]">Source:</strong>{" "}
                            {rule.source_reference}
                          </span>
                        </div>
                      )}
                      {(rule.limitations_en || rule.limitations_ta) && (
                        <div className="flex items-center gap-1 text-[#8C6D23]">
                          <ShieldAlert className="w-3.5 h-3.5 shrink-0" />
                          <span>
                            <strong className="text-[#8C6D23]">Caveat:</strong>{" "}
                            {language === "ta" && rule.limitations_ta
                              ? rule.limitations_ta
                              : rule.limitations_en}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
