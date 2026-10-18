"use client";

import React, { useState, useMemo, useEffect } from "react";
import {
  DasaResponse,
  DasaPeriodNode,
  HoroscopeResponse,
  KpResponse,
  KpEventAnalysisResponse,
  PeriodAnalysisResult,
  EventGradingDetail,
  HouseSignificationDetail,
} from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { getLordName, GRAHAS, TranslationDictionary } from "@/lib/translations";
import { analyzeKpEvents } from "@/lib/api";
import {
  jdToCalendarDateTime,
  calculateCalendarAge,
  formatCalendarAge,
  formatPeriodDuration,
  findActiveHierarchy,
  getLevelMetadata,
  ActiveHierarchy,
} from "@/lib/dasa-helpers";
import {
  buildPlanetContexts,
  calculateBenefitBhavas,
  PlanetContext,
} from "@/lib/benefit-bhavas";
import {
  ChevronDown,
  ChevronRight,
  Clock,
  Calendar,
  Sparkles,
  ChevronsDown,
  ChevronsUp,
  SlidersHorizontal,
  Compass,
  Tag,
  ShieldCheck,
  AlertTriangle,
  Filter,
} from "lucide-react";

interface DasaTimelineProps {
  dasa?: DasaResponse;
  birthDate?: string;
  birthTime?: string;
  timezone?: string;
  horoscope?: HoroscopeResponse;
  kp?: KpResponse;
  kpEventAnalysis?: KpEventAnalysisResponse | null;
}

/**
 * Standard Fliegel-Van Flandern Julian Day from Gregorian date (noon UTC)
 */
function dateToJd(isoDateStr: string): number {
  const [y, m, d] = isoDateStr.split("-").map(Number);
  const a = Math.floor((14 - m) / 12);
  const yAdjusted = y + 4800 - a;
  const mAdjusted = m + 12 * a - 3;
  return (
    d +
    Math.floor((153 * mAdjusted + 2) / 5) +
    365 * yAdjusted +
    Math.floor(yAdjusted / 4) -
    Math.floor(yAdjusted / 100) +
    Math.floor(yAdjusted / 400) -
    32045 +
    0.5 // 12:00 UTC
  );
}

export function DasaTimeline({
  dasa,
  birthDate: propBirthDate,
  timezone: propTimezone,
  horoscope,
  kp,
  kpEventAnalysis,
}: DasaTimelineProps) {
  const { language, t } = useLanguage();

  // KP Event Predictions Integration state
  const [internalKpAnalysis, setInternalKpAnalysis] = useState<KpEventAnalysisResponse | null>(null);
  const [showKpEvents, setShowKpEvents] = useState<boolean>(true);
  const [selectedEventFilter, setSelectedEventFilter] = useState<string>("all");

  // Auto-load KP event predictions if kp is present and kpEventAnalysis is not provided
  useEffect(() => {
    if (kpEventAnalysis) {
      setInternalKpAnalysis(kpEventAnalysis);
      return;
    }
    if (!kp || !dasa?.dasa_tree || dasa.dasa_tree.length === 0) return;

    let isMounted = true;
    const periods: Array<{
      mahadasha_lord: string;
      bhukti_lord: string;
      start_date: string;
      end_date: string;
    }> = [];

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

    const rawHouseSigs = kp.house_significators || [];
    const cslMap: Record<string, string> = {};
    if (kp.cuspal_analysis) {
      for (const cusp of kp.cuspal_analysis) {
        if (cusp.house && cusp.sub_lord) {
          cslMap[String(cusp.house)] = cusp.sub_lord;
        }
      }
    }
    const retroMap: Record<string, boolean> = { Rahu: true, Ketu: true };
    if (horoscope?.planets) {
      for (const p of horoscope.planets) {
        retroMap[p.name] = Boolean(p.is_retrograde);
      }
    }

    analyzeKpEvents({
      lagna: horoscope?.ascendant?.sign_name || "Aries",
      periods,
      significations: rawHouseSigs,
      csl_significations: cslMap,
      retrograde_status: retroMap,
      timezone: propTimezone || "Asia/Kolkata",
    })
      .then((res) => {
        if (isMounted) setInternalKpAnalysis(res);
      })
      .catch((err) => {
        console.warn("Dasa KP analysis auto-load failed:", err);
      });

    return () => {
      isMounted = false;
    };
  }, [kp, dasa, horoscope, propTimezone, kpEventAnalysis]);

  const effectiveKpAnalysis = kpEventAnalysis || internalKpAnalysis;

  // Build key -> PeriodAnalysisResult map
  const eventPredictionsMap = useMemo(() => {
    const map: Record<string, PeriodAnalysisResult> = {};
    if (!effectiveKpAnalysis?.periods) return map;
    for (const p of effectiveKpAnalysis.periods) {
      const key = p.period.toLowerCase();
      map[key] = p;
      const parts = p.period.split("-");
      if (parts.length >= 2) {
        map[`${parts[0]}-${parts[1]}`.toLowerCase()] = p;
      }
    }
    return map;
  }, [effectiveKpAnalysis]);

  // Extract distinct event names for filter
  const allDistinctEventNames = useMemo(() => {
    const set = new Set<string>();
    if (effectiveKpAnalysis?.periods) {
      for (const p of effectiveKpAnalysis.periods) {
        for (const ev of p.events) {
          set.add(ev.event);
        }
      }
    }
    return Array.from(set).sort();
  }, [effectiveKpAnalysis]);

  const planetContexts = useMemo(() => {
    if (!horoscope?.planets || !horoscope?.ascendant) return null;
    return buildPlanetContexts(horoscope.planets, horoscope.ascendant, horoscope.houses);
  }, [horoscope]);

  // Resolve birth date from props or dasa metadata or first node
  const resolvedBirthDate = useMemo(() => {
    if (propBirthDate) return propBirthDate;
    if (dasa?.metadata?.birth_utc_iso) {
      return dasa.metadata.birth_utc_iso.split("T")[0];
    }
    if (dasa?.dasa_tree && dasa.dasa_tree.length > 0) {
      const dt = jdToCalendarDateTime(dasa.dasa_tree[0].start_jd);
      if (dt) return dt.dateStr;
    }
    return "";
  }, [propBirthDate, dasa]);

  const utcOffsetHours = dasa?.metadata?.utc_offset_hours || 0;

  // Selected date for active period detection (defaults to target_date or today)
  const defaultTargetDate = useMemo(() => {
    if (dasa?.active_period?.target_date_iso) {
      return dasa.active_period.target_date_iso;
    }
    return new Date().toISOString().split("T")[0];
  }, [dasa]);

  const [selectedDate, setSelectedDate] = useState<string>(defaultTargetDate);

  // Set of expanded node path keys, e.g. "maha-Sun", "antar-Sun-Moon", etc.
  const [expandedKeys, setExpandedKeys] = useState<Record<string, boolean>>({});

  // Compute active hierarchy and person's age on selected date
  const { activeHierarchy, selectedDateAge, isDateOutOfRange } = useMemo(() => {
    if (!dasa?.dasa_tree || dasa.dasa_tree.length === 0 || !selectedDate) {
      return { activeHierarchy: null, selectedDateAge: null, isDateOutOfRange: false };
    }

    const targetJd = dateToJd(selectedDate);
    const tree = dasa.dasa_tree;
    const startJd = tree[0].start_jd;
    const endJd = tree[tree.length - 1].end_jd;

    if (targetJd < startJd || targetJd >= endJd) {
      return { activeHierarchy: null, selectedDateAge: null, isDateOutOfRange: true };
    }

    const hierarchy = findActiveHierarchy(tree, targetJd);

    let ageStr: string | null = null;
    if (resolvedBirthDate) {
      const [by, bm, bd] = resolvedBirthDate.split("-").map(Number);
      const [ty, tm, td] = selectedDate.split("-").map(Number);
      const ageObj = calculateCalendarAge(by, bm, bd, ty, tm, td);
      ageStr = formatCalendarAge(ageObj, language);
    }

    return {
      activeHierarchy: hierarchy,
      selectedDateAge: ageStr,
      isDateOutOfRange: false,
    };
  }, [dasa, selectedDate, resolvedBirthDate, language]);

  if (!dasa || !dasa.dasa_tree || dasa.dasa_tree.length === 0) {
    return (
      <div className="p-8 text-center bg-white rounded-lg border border-[#E2DCD5] text-[#64748B]">
        <Compass className="w-8 h-8 text-[#B8860B] mx-auto mb-2 opacity-60" />
        <p className="font-medium">{t.dasaNoPeriodsAvailable}</p>
      </div>
    );
  }

  const toggleExpand = (nodeKey: string) => {
    setExpandedKeys((prev) => ({
      ...prev,
      [nodeKey]: !prev[nodeKey],
    }));
  };

  // Quick expansion controls
  const expandAllMaha = () => {
    const next: Record<string, boolean> = {};
    dasa.dasa_tree.forEach((m) => {
      next[`maha-${m.lord}`] = true;
    });
    setExpandedKeys(next);
  };

  const expandToAntaram = () => {
    const next: Record<string, boolean> = {};
    dasa.dasa_tree.forEach((m) => {
      next[`maha-${m.lord}`] = true;
      m.sub_periods?.forEach((a) => {
        next[`antar-${m.lord}-${a.lord}`] = true;
      });
    });
    setExpandedKeys(next);
  };

  const collapseAll = () => {
    setExpandedKeys({});
  };

  const expandActivePath = () => {
    if (!activeHierarchy) return;
    const next: Record<string, boolean> = { ...expandedKeys };
    const { mahadasha, antardasha, pratyantardasha, sookshmadasha } = activeHierarchy;

    if (mahadasha) {
      next[`maha-${mahadasha.lord}`] = true;
    }
    if (mahadasha && antardasha) {
      next[`antar-${mahadasha.lord}-${antardasha.lord}`] = true;
    }
    if (mahadasha && antardasha && pratyantardasha) {
      next[`pratyantar-${mahadasha.lord}-${antardasha.lord}-${pratyantardasha.lord}`] = true;
    }
    if (mahadasha && antardasha && pratyantardasha && sookshmadasha) {
      next[`sookshma-${mahadasha.lord}-${antardasha.lord}-${pratyantardasha.lord}-${sookshmadasha.lord}`] = true;
    }

    setExpandedKeys(next);
  };

  return (
    <div className="space-y-6">
      {/* 1. Header Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Birth Balance Card */}
        <div className="bg-[#FAF7F0] p-4 rounded-xl border border-[#D8BD80]/80 shadow-2xs">
          <div className="flex items-center gap-2 text-xs uppercase tracking-wider font-bold text-[#8C6D23]">
            <Clock className="w-4 h-4 text-[#B8860B]" />
            <span>{t.dasaBalanceAtBirth}</span>
          </div>
          <div className="mt-2 text-xl font-bold text-[#0F172A]">
            {dasa.birth_balance_formatted}
          </div>
          <div className="mt-1 flex items-center justify-between text-xs text-[#64748B]">
            <div>
              {language === "ta" ? "பிறந்த நட்சத்திர அதிபதி" : "Birth Star Lord"}:{" "}
              <span className="font-semibold text-[#1E293B]">
                {getLordName(dasa.birth_dasa_lord, language)}
              </span>
            </div>
            {resolvedBirthDate && (
              <div className="font-mono text-[11px] text-[#475569]">
                DOB: {resolvedBirthDate}
              </div>
            )}
          </div>
        </div>

        {/* Active Period / Target Date Inspector Card */}
        <div className="bg-[#FAF7F0] p-4 rounded-xl border border-[#D8BD80]/80 shadow-2xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2 text-xs uppercase tracking-wider font-bold text-[#8C6D23]">
                <Calendar className="w-4 h-4 text-[#B8860B]" />
                <span>{t.dasaActivePeriod}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <label htmlFor="target-date-input" className="text-[11px] text-[#64748B]">
                  {t.dasaSelectedDate}:
                </label>
                <input
                  id="target-date-input"
                  type="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="px-2 py-0.5 text-xs font-mono rounded border border-[#D8BD80] bg-white text-[#0F172A] focus:outline-hidden focus:ring-1 focus:ring-[#B8860B]"
                />
              </div>
            </div>

            {/* Active Hierarchy Breadcrumb */}
            {isDateOutOfRange ? (
              <div className="mt-2 text-xs text-amber-800 bg-amber-50 p-2 rounded border border-amber-200">
                {t.dasaPeriodOutsideRange} ({selectedDate})
              </div>
            ) : activeHierarchy?.mahadasha ? (
              <div className="mt-2">
                <div className="flex flex-wrap items-center gap-1.5 text-xs sm:text-sm font-bold text-[#784E0E]">
                  <span className="px-1.5 py-0.5 rounded bg-amber-200/60 text-amber-900">
                    {getLordName(activeHierarchy.mahadasha.lord, language)}
                  </span>
                  {activeHierarchy.antardasha && (
                    <>
                      <span className="text-[#94A3B8]">/</span>
                      <span className="px-1.5 py-0.5 rounded bg-indigo-100 text-indigo-900 font-medium">
                        {getLordName(activeHierarchy.antardasha.lord, language)}
                      </span>
                    </>
                  )}
                  {activeHierarchy.pratyantardasha && (
                    <>
                      <span className="text-[#94A3B8]">/</span>
                      <span className="px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-900 font-medium">
                        {getLordName(activeHierarchy.pratyantardasha.lord, language)}
                      </span>
                    </>
                  )}
                  {activeHierarchy.sookshmadasha && (
                    <>
                      <span className="text-[#94A3B8]">/</span>
                      <span className="px-1.5 py-0.5 rounded bg-purple-100 text-purple-900 font-medium">
                        {getLordName(activeHierarchy.sookshmadasha.lord, language)}
                      </span>
                    </>
                  )}
                  {activeHierarchy.pranadasha && (
                    <>
                      <span className="text-[#94A3B8]">/</span>
                      <span className="px-1.5 py-0.5 rounded bg-rose-100 text-rose-900 font-medium">
                        {getLordName(activeHierarchy.pranadasha.lord, language)}
                      </span>
                    </>
                  )}
                </div>

                {selectedDateAge && (
                  <div className="mt-1 text-xs text-[#475569]">
                    <span className="text-[#64748B]">
                      {language === "ta" ? "தேர்ந்தெடுக்கப்பட்ட நாளில் வயது" : "Age on selected date"}:{" "}
                    </span>
                    <span className="font-semibold text-[#0F172A]">{selectedDateAge}</span>
                  </div>
                )}
              </div>
            ) : (
              <div className="mt-2 text-xs text-[#64748B]">
                {t.dasaNoPeriodsAvailable}
              </div>
            )}
          </div>

          {activeHierarchy && (
            <div className="mt-2 pt-2 border-t border-[#E8DEC8] flex items-center justify-end">
              <button
                type="button"
                onClick={expandActivePath}
                className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#8C6D23] hover:text-[#0F172A] underline"
              >
                <Sparkles className="w-3 h-3 text-[#B8860B]" />
                <span>{t.dasaExpandActivePath}</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* 2. Dasa Tree Header & Toolbar */}
      <div className="bg-white rounded-xl border border-[#E2DCD5] shadow-xs overflow-hidden">
        <div className="px-4 py-3 bg-[#FAF7F0] border-b border-[#E2DCD5] flex flex-wrap items-center justify-between gap-3">
          <div>
            <h4 className="text-sm font-bold text-[#0F172A] uppercase tracking-wider flex items-center gap-2">
              <span>
                {language === "ta"
                  ? "விம்சோத்தரி 5-நிலை தசா கால அட்டவணை"
                  : "Vimshottari 5-Level Dasa Hierarchy"}
              </span>
            </h4>
            <div className="text-[11px] text-[#64748B] font-mono mt-0.5">
              Maha → Bhukti → Antaram → Sookshma → Prana (120Y Cycle)
            </div>
          </div>

          {/* Quick hierarchy expansion controls */}
          <div className="flex flex-wrap items-center gap-1.5 text-xs">
            {/* KP Event Predictions Toggle */}
            {effectiveKpAnalysis && (
              <button
                type="button"
                onClick={() => setShowKpEvents(!showKpEvents)}
                className={`px-2.5 py-1 rounded border font-semibold inline-flex items-center gap-1 transition-colors ${
                  showKpEvents
                    ? "bg-emerald-50 text-emerald-800 border-emerald-300"
                    : "bg-white text-[#64748B] border-[#E2DCD5] hover:text-[#0F172A]"
                }`}
                title="Toggle KP Dasha Event Indicators"
              >
                <span>✨</span>
                <span>{language === "ta" ? "KP கணிப்புகள்" : "KP Events"}</span>
              </button>
            )}

            {/* KP Event Filter Dropdown */}
            {effectiveKpAnalysis && showKpEvents && allDistinctEventNames.length > 0 && (
              <div className="flex items-center gap-1 bg-white border border-[#D8BD80] rounded px-2 py-0.5">
                <Filter className="w-3 h-3 text-[#B8860B]" />
                <select
                  value={selectedEventFilter}
                  onChange={(e) => setSelectedEventFilter(e.target.value)}
                  className="bg-transparent text-[11px] font-bold text-[#0F172A] outline-none cursor-pointer"
                >
                  <option value="all">{language === "ta" ? "அனைத்து நிகழ்வுகள்" : "All Events"}</option>
                  {allDistinctEventNames.map((name) => (
                    <option key={name} value={name}>
                      {name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <button
              type="button"
              onClick={expandAllMaha}
              className="px-2.5 py-1 rounded border border-[#D8BD80] bg-white text-[#784E0E] hover:bg-[#FAF6EC] font-medium transition-colors"
              title="Expand all Mahadashas"
            >
              {language === "ta" ? "மகா தசை" : "Maha"}
            </button>
            <button
              type="button"
              onClick={expandToAntaram}
              className="px-2.5 py-1 rounded border border-[#D8BD80] bg-white text-[#784E0E] hover:bg-[#FAF6EC] font-medium transition-colors"
              title="Expand to Bhukti and Antaram"
            >
              {language === "ta" ? "அந்தரம் வரை" : "To Antaram"}
            </button>
            <button
              type="button"
              onClick={expandActivePath}
              className="px-2.5 py-1 rounded border border-[#B8860B] bg-[#FAF2DE] text-[#784E0E] hover:bg-[#FAF6EC] font-bold inline-flex items-center gap-1 transition-colors"
            >
              <Sparkles className="w-3 h-3" />
              <span>{language === "ta" ? "நடப்பு" : "Active"}</span>
            </button>
            <button
              type="button"
              onClick={collapseAll}
              className="px-2.5 py-1 rounded border border-[#E2DCD5] bg-white text-[#64748B] hover:text-[#0F172A] font-medium transition-colors"
              title={t.dasaCollapseAll}
            >
              <ChevronsUp className="w-3.5 h-3.5 inline mr-0.5" />
              <span>{t.dasaCollapseAll}</span>
            </button>
          </div>
        </div>

        {/* KP Event Legend Bar */}
        {effectiveKpAnalysis && showKpEvents && (
          <div className="px-4 py-2 bg-gradient-to-r from-emerald-50/50 via-amber-50/50 to-rose-50/50 border-b border-[#E2DCD5] flex flex-wrap items-center justify-between gap-2 text-[11px] text-[#475569]">
            <div className="flex items-center gap-3 flex-wrap">
              <span className="font-bold text-[#0F172A] uppercase tracking-wider text-[10px]">
                {language === "ta" ? "KP நிகழ்வு தரங்கள்:" : "KP Event Indicators:"}
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                <span className="font-semibold text-emerald-900">STRONG (Green)</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-amber-500" />
                <span className="font-semibold text-amber-900">MODERATE (Orange)</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-rose-500" />
                <span className="font-semibold text-rose-900">WEAK (Red)</span>
              </span>
            </div>
            <span className="text-[10px] text-[#64748B] italic">
              Indicative KP hint, confirm with CSL and transit before decisions.
            </span>
          </div>
        )}

        {/* 3. The 5-Level Dasa Tree Rows */}
        <div className="divide-y divide-[#F1EBE4]">
          {dasa.dasa_tree.map((maha) => (
            <DasaNodeRow
              key={`maha-${maha.lord}`}
              node={maha}
              path={[maha.lord]}
              nodeKey={`maha-${maha.lord}`}
              expandedKeys={expandedKeys}
              onToggleExpand={toggleExpand}
              activeHierarchy={activeHierarchy}
              resolvedBirthDate={resolvedBirthDate}
              utcOffsetHours={utcOffsetHours}
              planetContexts={planetContexts}
              language={language}
              t={t}
              eventPredictionsMap={eventPredictionsMap}
              showKpEvents={showKpEvents}
              selectedEventFilter={selectedEventFilter}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Recursive Row Component supporting all 5 levels
// ---------------------------------------------------------------------------

interface DasaNodeRowProps {
  node: DasaPeriodNode;
  path: string[];
  nodeKey: string;
  expandedKeys: Record<string, boolean>;
  onToggleExpand: (key: string) => void;
  activeHierarchy: ActiveHierarchy | null;
  resolvedBirthDate: string;
  utcOffsetHours: number;
  planetContexts: Record<string, PlanetContext> | null;
  language: "en" | "ta";
  t: TranslationDictionary;
  eventPredictionsMap?: Record<string, PeriodAnalysisResult>;
  showKpEvents?: boolean;
  selectedEventFilter?: string;
}

function DasaNodeRow({
  node,
  path,
  nodeKey,
  expandedKeys,
  onToggleExpand,
  activeHierarchy,
  resolvedBirthDate,
  utcOffsetHours,
  planetContexts,
  language,
  t,
  eventPredictionsMap,
  showKpEvents = true,
  selectedEventFilter = "all",
}: DasaNodeRowProps) {
  const isExpanded = !!expandedKeys[nodeKey];
  const hasSubPeriods = !!(node.sub_periods && node.sub_periods.length > 0);
  const meta = getLevelMetadata(node.level);
  const [isKpDetailOpen, setIsKpDetailOpen] = useState<boolean>(false);

  // Derive period prediction for looking up KP event predictions
  const periodPrediction = useMemo(() => {
    if (!eventPredictionsMap) return undefined;
    if (meta.levelNumber === 1) {
      return eventPredictionsMap[`${node.lord.toLowerCase()}-${node.lord.toLowerCase()}`];
    } else if (meta.levelNumber === 2 && path.length >= 1) {
      return eventPredictionsMap[`${path[0].toLowerCase()}-${node.lord.toLowerCase()}`];
    } else if (meta.levelNumber === 3 && path.length >= 2) {
      return (
        eventPredictionsMap[`${path[0].toLowerCase()}-${path[1].toLowerCase()}-${node.lord.toLowerCase()}`] ||
        eventPredictionsMap[`${path[0].toLowerCase()}-${path[1].toLowerCase()}`]
      );
    }
    return undefined;
  }, [meta.levelNumber, path, node.lord, eventPredictionsMap]);

  // Mahadasha summary count across all its Bhuktis
  const mahaSummary = useMemo(() => {
    if (meta.levelNumber !== 1 || !eventPredictionsMap) return null;
    const prefix = `${node.lord.toLowerCase()}-`;
    let greenCount = 0;
    let orangeCount = 0;
    for (const [k, p] of Object.entries(eventPredictionsMap)) {
      if (k.startsWith(prefix) && p.events) {
        for (const ev of p.events) {
          if (ev.color === "green") greenCount++;
          else if (ev.color === "orange") orangeCount++;
        }
      }
    }
    return { greenCount, orangeCount };
  }, [meta.levelNumber, node.lord, eventPredictionsMap]);

  // Check if this period matches the selected event filter with GREEN or ORANGE grade
  const matchingEvent = useMemo(() => {
    if (!periodPrediction?.events || !selectedEventFilter || selectedEventFilter === "all") return null;
    return periodPrediction.events.find(
      (e) => e.event.toLowerCase() === selectedEventFilter.toLowerCase() && (e.color === "green" || e.color === "orange")
    );
  }, [periodPrediction, selectedEventFilter]);

  const mahaHasMatchingEvent = useMemo(() => {
    if (meta.levelNumber !== 1 || !eventPredictionsMap || !selectedEventFilter || selectedEventFilter === "all") {
      return false;
    }
    const prefix = `${node.lord.toLowerCase()}-`;
    for (const [k, p] of Object.entries(eventPredictionsMap)) {
      if (k.startsWith(prefix) && p.events) {
        if (p.events.some((e) => e.event.toLowerCase() === selectedEventFilter.toLowerCase() && (e.color === "green" || e.color === "orange"))) {
          return true;
        }
      }
    }
    return false;
  }, [meta.levelNumber, node.lord, eventPredictionsMap, selectedEventFilter]);

  // Check if this node is active in the hierarchy
  const isActive = useMemo(() => {
    if (!activeHierarchy) return false;
    const { mahadasha, antardasha, pratyantardasha, sookshmadasha, pranadasha } = activeHierarchy;
    switch (meta.levelNumber) {
      case 1:
        return mahadasha?.lord.toLowerCase() === node.lord.toLowerCase();
      case 2:
        return (
          path[0]?.toLowerCase() === mahadasha?.lord.toLowerCase() &&
          antardasha?.lord.toLowerCase() === node.lord.toLowerCase()
        );
      case 3:
        return (
          path[0]?.toLowerCase() === mahadasha?.lord.toLowerCase() &&
          path[1]?.toLowerCase() === antardasha?.lord.toLowerCase() &&
          pratyantardasha?.lord.toLowerCase() === node.lord.toLowerCase()
        );
      case 4:
        return (
          path[0]?.toLowerCase() === mahadasha?.lord.toLowerCase() &&
          path[1]?.toLowerCase() === antardasha?.lord.toLowerCase() &&
          path[2]?.toLowerCase() === pratyantardasha?.lord.toLowerCase() &&
          sookshmadasha?.lord.toLowerCase() === node.lord.toLowerCase()
        );
      case 5:
        return (
          path[0]?.toLowerCase() === mahadasha?.lord.toLowerCase() &&
          path[1]?.toLowerCase() === antardasha?.lord.toLowerCase() &&
          path[2]?.toLowerCase() === pratyantardasha?.lord.toLowerCase() &&
          path[3]?.toLowerCase() === sookshmadasha?.lord.toLowerCase() &&
          pranadasha?.lord.toLowerCase() === node.lord.toLowerCase()
        );
      default:
        return false;
    }
  }, [activeHierarchy, node.lord, meta.levelNumber, path]);

  // Start & End Dates with time for Sookshma/Prana
  const { startFormatted, endFormatted } = useMemo(() => {
    const showTime = meta.levelNumber >= 4;
    const sDt = jdToCalendarDateTime(node.start_jd, utcOffsetHours);
    const eDt = jdToCalendarDateTime(node.end_jd, utcOffsetHours);

    const sStr = sDt ? (showTime ? `${sDt.dateStr} ${sDt.timeStr}` : sDt.dateStr) : "—";
    const eStr = eDt ? (showTime ? `${eDt.dateStr} ${eDt.timeStr}` : eDt.dateStr) : "—";
    return { startFormatted: sStr, endFormatted: eStr };
  }, [node.start_jd, node.end_jd, utcOffsetHours, meta.levelNumber]);

  // Exact Start Age & End Age
  const { startAgeText, endAgeText } = useMemo(() => {
    // 1. If backend dictionary provided, format for current language
    if (node.start_age_dict && node.end_age_dict) {
      return {
        startAgeText: formatCalendarAge(node.start_age_dict, language),
        endAgeText: formatCalendarAge(node.end_age_dict, language),
      };
    }

    // 2. Client-side exact calendar age calculation from birth date
    if (resolvedBirthDate) {
      const [by, bm, bd] = resolvedBirthDate.split("-").map(Number);
      const sDt = jdToCalendarDateTime(node.start_jd, utcOffsetHours);
      const eDt = jdToCalendarDateTime(node.end_jd, utcOffsetHours);

      const sAge = sDt ? calculateCalendarAge(by, bm, bd, sDt.year, sDt.month, sDt.day) : null;
      const eAge = eDt ? calculateCalendarAge(by, bm, bd, eDt.year, eDt.month, eDt.day) : null;

      return {
        startAgeText: formatCalendarAge(sAge, language),
        endAgeText: formatCalendarAge(eAge, language),
      };
    }

    // 3. Fallback to preformatted string from backend if any
    return {
      startAgeText: node.start_age || t.dasaAgeUnavailable,
      endAgeText: node.end_age || t.dasaAgeUnavailable,
    };
  }, [node, resolvedBirthDate, utcOffsetHours, language, t.dasaAgeUnavailable]);

  // Formatted duration separated from age
  const durationText = useMemo(() => {
    return formatPeriodDuration(node.duration_years, node.duration_days, language);
  }, [node.duration_years, node.duration_days, language]);

  // Resolve Benefit Bhavas, Period Lord Occupancy, and Star Lord for this period
  const { starLordName, benefitBhavas, periodLordOcc, starLordOcc, periodLordOwn, starLordOwn } = useMemo(() => {
    let sl = node.star_lord;
    let bb = node.benefit_bhavas;
    let plOcc = node.period_lord_occupied;
    let slOcc = node.star_lord_occupied;
    let plOwn = node.period_lord_owned;
    let slOwn = node.star_lord_owned;

    // Authoritatively calculate Benefit Bhavas whenever planetContexts is available,
    // ensuring previously saved horoscopes with stale or Placidus-distorted snapshots
    // are auto-healed to display the true canonical Vedic house occupancy.
    if (planetContexts && node.lord) {
      const res = calculateBenefitBhavas(node.lord, planetContexts);
      sl = res.starLord;
      bb = res.formatted;
      plOcc = res.periodLordOccupied;
      slOcc = res.starLordOccupied;
      plOwn = res.periodLordOwned;
      slOwn = res.starLordOwned;
    }

    return {
      starLordName: sl || null,
      benefitBhavas: bb || null,
      periodLordOcc: plOcc ?? null,
      starLordOcc: slOcc ?? null,
      periodLordOwn: plOwn || [],
      starLordOwn: slOwn || [],
    };
  }, [node, planetContexts]);

  // Star lord display label (e.g. "Sun's star" or "சூரியன் சாரம்")
  const starLordDisplay = useMemo(() => {
    if (!starLordName || starLordName === "Unknown") return null;
    if (language === "ta") {
      const slTa = getLordName(starLordName, "ta");
      return `${slTa} சாரம்`;
    }
    return `${starLordName}'s star`;
  }, [starLordName, language]);

  // Exact period duration in Y.M.D format (e.g. 2.10.0)
  const durationYmd = useMemo(() => {
    const sDt = jdToCalendarDateTime(node.start_jd, utcOffsetHours);
    const eDt = jdToCalendarDateTime(node.end_jd, utcOffsetHours);
    if (!sDt || !eDt) return null;
    const diff = calculateCalendarAge(sDt.year, sDt.month, sDt.day, eDt.year, eDt.month, eDt.day);
    if (!diff) return null;
    return `${diff.years}.${diff.months}.${diff.days}`;
  }, [node.start_jd, node.end_jd, utcOffsetHours]);

  // Dates formatted in DD/MM/YYYY (with time for Sookshma/Prana)
  const { sDateFormatted, eDateFormatted } = useMemo(() => {
    const showTime = meta.levelNumber >= 4;
    const sDt = jdToCalendarDateTime(node.start_jd, utcOffsetHours);
    const eDt = jdToCalendarDateTime(node.end_jd, utcOffsetHours);
    const sStr = sDt
      ? showTime
        ? `${String(sDt.day).padStart(2, "0")}/${String(sDt.month).padStart(2, "0")}/${sDt.year} ${sDt.timeStr}`
        : `${String(sDt.day).padStart(2, "0")}/${String(sDt.month).padStart(2, "0")}/${sDt.year}`
      : startFormatted;
    const eStr = eDt
      ? showTime
        ? `${String(eDt.day).padStart(2, "0")}/${String(eDt.month).padStart(2, "0")}/${eDt.year} ${eDt.timeStr}`
        : `${String(eDt.day).padStart(2, "0")}/${String(eDt.month).padStart(2, "0")}/${eDt.year}`
      : endFormatted;
    return { sDateFormatted: sStr, eDateFormatted: eStr };
  }, [node.start_jd, node.end_jd, utcOffsetHours, meta.levelNumber, startFormatted, endFormatted]);

  const lordLabel = getLordName(node.lord, language);
  const grahaInfo = GRAHAS[node.lord];
  const levelTitle = language === "ta" ? meta.nameTamil : meta.name;
  const badgeShort = language === "ta" ? meta.badgeShortTamil : meta.badgeShort;

  // Background styling based on level, active status, and event filter highlight
  const rowBgClass = useMemo(() => {
    if (showKpEvents && selectedEventFilter && selectedEventFilter !== "all") {
      if (meta.levelNumber === 1) {
        if (mahaHasMatchingEvent) {
          return "bg-emerald-50/50 border-l-4 border-l-emerald-500 hover:bg-emerald-50/80";
        }
        return "bg-white opacity-60 hover:opacity-100";
      } else if (matchingEvent?.color === "green") {
        return "bg-emerald-50/80 border-l-4 border-l-emerald-500 hover:bg-emerald-100/60";
      } else if (matchingEvent?.color === "orange") {
        return "bg-amber-50/80 border-l-4 border-l-amber-500 hover:bg-amber-100/60";
      } else if (periodPrediction && meta.levelNumber >= 2) {
        return "bg-slate-50/40 opacity-50 hover:opacity-100";
      }
    }
    if (isActive) return "bg-[#FAF2DE]/80 border-l-4 border-l-[#B8860B]";
    switch (meta.levelNumber) {
      case 1:
        return "bg-white hover:bg-[#FAF8F5]";
      case 2:
        return "bg-[#FCFAF7] hover:bg-[#F8F4ED] border-l-2 border-l-indigo-300";
      case 3:
        return "bg-[#FAF7F2] hover:bg-[#F5F0E8] border-l-2 border-l-emerald-300";
      case 4:
        return "bg-[#F7F4EE] hover:bg-[#F2ECE2] border-l-2 border-l-purple-300";
      case 5:
        return "bg-[#F4F1EA] hover:bg-[#EFE8DC] border-l-2 border-l-rose-300";
      default:
        return "bg-white";
    }
  }, [isActive, meta.levelNumber, showKpEvents, selectedEventFilter, matchingEvent, mahaHasMatchingEvent, periodPrediction]);

  return (
    <div className={`transition-colors ${meta.indentClass}`}>
      {/* Node Row */}
      <div
        onClick={() => hasSubPeriods && onToggleExpand(nodeKey)}
        className={`px-3 py-2.5 sm:px-4 sm:py-3 flex flex-col md:flex-row md:items-center justify-between gap-2.5 cursor-pointer ${rowBgClass}`}
      >
        {/* Left: Expander, Level Badge, Lord Symbol & Name, Star Lord, Benefit Bhavas */}
        <div className="flex items-start sm:items-center gap-2.5 min-w-0">
          {hasSubPeriods ? (
            <button
              type="button"
              aria-expanded={isExpanded}
              aria-label={`Toggle ${levelTitle} for ${node.lord}`}
              onClick={(e) => {
                e.stopPropagation();
                onToggleExpand(nodeKey);
              }}
              className="mt-0.5 sm:mt-0 p-1 rounded hover:bg-black/5 text-[#8C6D23] focus:outline-hidden focus:ring-1 focus:ring-[#B8860B]"
            >
              {isExpanded ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
            </button>
          ) : (
            <span className="w-6 inline-block" />
          )}

          {/* Level Badge */}
          <span
            className={`px-1.5 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase border shrink-0 ${meta.badgeClass}`}
            title={levelTitle}
          >
            {badgeShort}
          </span>

          {/* Lord Badge / Symbol & Name */}
          <div className="flex items-center gap-2 flex-wrap">
            <span
              className="w-2.5 h-2.5 rounded-full inline-block shrink-0"
              style={{ backgroundColor: grahaInfo?.color || "#B8860B" }}
            />
            <span className={`text-[#0F172A] ${meta.levelNumber === 1 ? "font-bold text-sm sm:text-base" : "font-semibold text-xs sm:text-sm"}`}>
              {lordLabel}
            </span>

            {/* Star Lord Tag (e.g. Sukran (Sun's star)) */}
            {starLordDisplay && (
              <span className="text-[11px] font-medium text-[#784E0E] bg-[#FAF2DE] border border-[#E8DEC8] px-1.5 py-0.5 rounded">
                ({starLordDisplay})
              </span>
            )}

            <span className="text-[11px] text-[#64748B]">
              ({levelTitle})
            </span>

            {/* Active Period Badge */}
            {isActive && (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#B8860B] text-white tracking-wide shadow-2xs">
                {language === "ta" ? "தற்போது" : "Active"}
              </span>
            )}

            {/* Benefit Bhavas Compact Badge */}
            {benefitBhavas && (
              <div
                className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#FAF5E6] border border-[#D8BD80] text-xs font-mono shadow-2xs text-[#0F172A]"
                title={
                  language === "ta"
                    ? `சார நாதன் அமர்வு: ${starLordOcc ?? "—"} | சார நாதன் ஆட்சி: ${starLordOwn.length > 0 ? starLordOwn.join(", ") : "—"} | தசா நாதன் அமர்வு: ${periodLordOcc ?? "—"} | தசா நாதன் ஆட்சி: ${periodLordOwn.length > 0 ? periodLordOwn.join(", ") : "—"}`
                    : `Star Lord Occ: ${starLordOcc ?? "—"} | Star Lord Own: ${starLordOwn.length > 0 ? starLordOwn.join(", ") : "—"} | Period Lord Occ: ${periodLordOcc ?? "—"} | Period Lord Own: ${periodLordOwn.length > 0 ? periodLordOwn.join(", ") : "—"}`
                }
              >
                <span className="text-[10px] uppercase font-bold text-[#8C6D23] tracking-wider">
                  {t.dasaBenefitBhavas}:
                </span>
                <span className="font-bold tracking-wider text-[#0F172A]">
                  {benefitBhavas}
                </span>
              </div>
            )}

            {/* KP Event Badges on Row */}
            {showKpEvents && (periodPrediction || (meta.levelNumber === 1 && (mahaSummary?.greenCount || mahaSummary?.orangeCount))) && (
              <div className="flex items-center gap-1.5 flex-wrap">
                {meta.levelNumber === 1 && mahaSummary && (mahaSummary.greenCount > 0 || mahaSummary.orangeCount > 0) ? (
                  <span
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleExpand(nodeKey);
                    }}
                    className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-amber-50 text-amber-900 border border-amber-200 hover:bg-amber-100 cursor-pointer shadow-2xs"
                    title="Mahadasha contains strong or moderate events in its Bhuktis. Click to expand."
                  >
                    <span>✨</span>
                    {mahaSummary.greenCount > 0 && (
                      <span className="font-bold text-emerald-800">
                        {mahaSummary.greenCount} {language === "ta" ? "வலுவான" : "Strong"}
                      </span>
                    )}
                    {mahaSummary.greenCount > 0 && mahaSummary.orangeCount > 0 && <span>•</span>}
                    {mahaSummary.orangeCount > 0 && (
                      <span className="font-semibold text-amber-800">
                        {mahaSummary.orangeCount} {language === "ta" ? "மிதமான" : "Mod"}
                      </span>
                    )}
                  </span>
                ) : periodPrediction ? (
                  <>
                    {/* If filtered by specific event */}
                    {selectedEventFilter !== "all" && matchingEvent ? (
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setIsKpDetailOpen(!isKpDetailOpen);
                        }}
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-bold border transition-colors shadow-2xs ${
                          matchingEvent.color === "green"
                            ? "bg-emerald-100 text-emerald-900 border-emerald-300 hover:bg-emerald-200"
                            : "bg-amber-100 text-amber-900 border-amber-300 hover:bg-amber-200"
                        }`}
                      >
                        <span>{matchingEvent.color === "green" ? "🟢" : "🟡"}</span>
                        <span>{matchingEvent.event}</span>
                        <span className="uppercase text-[9px] px-1 rounded bg-white/70">
                          {matchingEvent.grade}
                        </span>
                      </button>
                    ) : (
                      /* Top 1-2 event indicators */
                      periodPrediction.events.slice(0, 2).map((ev, i) => (
                        <button
                          key={i}
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            setIsKpDetailOpen(!isKpDetailOpen);
                          }}
                          className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold border transition-colors ${
                            ev.color === "green"
                              ? "bg-emerald-50 text-emerald-800 border-emerald-300 hover:bg-emerald-100"
                              : ev.color === "orange"
                              ? "bg-amber-50 text-amber-800 border-amber-300 hover:bg-amber-100"
                              : "bg-rose-50 text-rose-700 border-rose-200 hover:bg-rose-100"
                          }`}
                          title={`${ev.event}: ${ev.grade} - ${ev.hint}`}
                        >
                          <span
                            className={`w-1.5 h-1.5 rounded-full ${
                              ev.color === "green"
                                ? "bg-emerald-500"
                                : ev.color === "orange"
                                ? "bg-amber-500"
                                : "bg-rose-500"
                            }`}
                          />
                          <span>{ev.event}</span>
                        </button>
                      ))
                    )}

                    {/* Toggle Details Button */}
                    {periodPrediction.events.length > 0 && (
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setIsKpDetailOpen(!isKpDetailOpen);
                        }}
                        className={`text-[10px] font-semibold px-1.5 py-0.5 rounded border transition-colors ${
                          isKpDetailOpen
                            ? "bg-[#8C6D23] text-white border-[#8C6D23]"
                            : "bg-white text-[#784E0E] border-[#D8BD80] hover:bg-[#FAF2DE]"
                        }`}
                      >
                        {isKpDetailOpen
                          ? language === "ta" ? "மறை" : "Hide Details"
                          : periodPrediction.events.length > 2
                          ? `+${periodPrediction.events.length - 2} more`
                          : language === "ta" ? "விவரம்" : "Details"}
                      </button>
                    )}
                  </>
                ) : null}
              </div>
            )}
          </div>
        </div>

        {/* Right: Dates, Ages, Duration */}
        <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-6 text-xs text-[#1E293B] pl-8 md:pl-0 shrink-0">
          {/* Period Boundaries */}
          <div className="space-y-0.5 text-left md:text-right">
            <div className="font-mono text-[#0F172A] font-semibold text-[11px] sm:text-xs">
              <span>{sDateFormatted}</span>
              <span className="mx-1.5 text-[#94A3B8]">→</span>
              <span>{eDateFormatted}</span>
            </div>
            <div className="text-[11px] text-[#64748B] flex items-center md:justify-end gap-1 font-mono">
              <span className="text-[#8C6D23] font-medium">{t.dasaDuration}:</span>
              {durationYmd ? (
                <span className="font-bold text-[#0F172A] bg-slate-100 px-1 py-0.2 rounded border border-slate-200">
                  {durationYmd}
                </span>
              ) : null}
              <span className="text-[#64748B] text-[10px]">({durationText})</span>
            </div>
          </div>

          {/* Person's Age at Start and End of Period */}
          <div className="bg-white/80 p-1.5 sm:p-2 rounded border border-[#E8DEC8] text-[11px] sm:text-xs min-w-[210px] space-y-0.5 shadow-2xs">
            <div className="flex items-center justify-between gap-2">
              <span className="text-[#64748B] text-[10px] uppercase font-semibold">
                {t.dasaAgeAtStart}:
              </span>
              <span className="font-semibold text-[#0F172A] text-right font-mono">
                {startAgeText}
              </span>
            </div>
            <div className="flex items-center justify-between gap-2 border-t border-[#F1EBE4] pt-0.5">
              <span className="text-[#64748B] text-[10px] uppercase font-semibold">
                {t.dasaAgeAtEnd}:
              </span>
              <span className="font-semibold text-[#0F172A] text-right font-mono">
                {endAgeText}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Inline KP Event Details Drawer */}
      {showKpEvents && isKpDetailOpen && periodPrediction && (
        <div
          onClick={(e) => e.stopPropagation()}
          className="px-4 py-3 bg-[#FAF8F3] border-t border-b border-[#E8DEC8] space-y-3 text-xs"
        >
          {/* Drawer Header */}
          <div className="flex items-center justify-between border-b border-[#EADFCB] pb-2">
            <div className="flex items-center gap-2">
              <span className="font-bold text-[#784E0E] flex items-center gap-1.5 text-xs sm:text-sm">
                <span>✨</span>
                <span>
                  {language === "ta" ? "KP நிகழ்வு பகுப்பாய்வு" : "KP Event Analysis"}:{" "}
                  <span className="text-[#0F172A]">{periodPrediction.period}</span>
                </span>
              </span>
              {Boolean(periodPrediction.running || periodPrediction.is_running) && (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#B8860B] text-white">
                  {language === "ta" ? "நடப்பு காலம்" : "Running Period"}
                </span>
              )}
            </div>
            <button
              type="button"
              onClick={() => setIsKpDetailOpen(false)}
              className="text-[#64748B] hover:text-[#0F172A] text-xs font-semibold px-2 py-0.5 rounded hover:bg-black/5"
            >
              ✕ {language === "ta" ? "மூடு" : "Close"}
            </button>
          </div>

          {/* Evaluated Events List */}
          {periodPrediction.status === "missing_data" ? (
            <div className="p-3 bg-amber-50 border border-amber-200 text-amber-800 rounded">
              {language === "ta" ? "தரவு இல்லை:" : "Missing significator data:"}{" "}
              {periodPrediction.missing_fields?.join(", ") || "Mahadasha/Bhukti lords"}
            </div>
          ) : periodPrediction.events.length === 0 ? (
            <div className="text-gray-500 italic py-2">
              {language === "ta" ? "குறிப்பிடத்தக்க நிகழ்வுகள் இல்லை" : "No prominent events scored for this period."}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
              {periodPrediction.events.map((ev, idx) => {
                const isGreen = ev.color === "green";
                const isOrange = ev.color === "orange";
                const borderClass = isGreen
                  ? "border-emerald-300 bg-emerald-50/60"
                  : isOrange
                  ? "border-amber-300 bg-amber-50/60"
                  : "border-rose-200 bg-rose-50/40";
                const badgeClass = isGreen
                  ? "bg-emerald-600 text-white"
                  : isOrange
                  ? "bg-amber-600 text-white"
                  : "bg-rose-600 text-white";

                const suppList = ev.supporting || ev.supporting_houses_covered || [];
                const denList = ev.denying || ev.denying_houses_present || [];
                const missingList = (ev.scoring_metadata?.missing_supporting as number[] | undefined) || ev.missing_supporting_houses || [];
                const retroNote = ev.retrograde_note || (ev.retrograde_delay ? "Retrograde lord involved: delay possible." : null);

                return (
                  <div
                    key={`${ev.event}-${idx}`}
                    className={`p-2.5 rounded-lg border ${borderClass} space-y-1.5`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-bold text-[#0F172A] text-xs sm:text-sm">
                        {ev.event}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${badgeClass}`}>
                        {ev.grade}
                      </span>
                    </div>

                    {/* Hint text */}
                    <p className="text-[11px] text-[#334155] italic">
                      &ldquo;{ev.hint}&rdquo;
                    </p>

                    {/* Score & Coverage */}
                    <div className="flex items-center justify-between text-[11px] text-[#475569] font-mono bg-white/70 px-2 py-1 rounded border border-[#E8DEC8]">
                      <span>
                        Supp: <strong>{ev.support_score}</strong> | Den: <strong>{ev.denial_score}</strong>
                      </span>
                      <span>
                        Cov: <strong>{Math.round(ev.coverage * 100)}%</strong>
                      </span>
                    </div>

                    {/* House breakdown */}
                    <div className="space-y-0.5 text-[10px]">
                      <div className="text-emerald-800">
                        <span className="font-bold">Supp Houses:</span>{" "}
                        {suppList.length > 0
                          ? suppList.map((h: HouseSignificationDetail) => `H${h.house}(${h.level})`).join(", ")
                          : "None"}
                      </div>
                      {missingList.length > 0 && (
                        <div className="text-slate-600">
                          <span className="font-bold">Missing Supp:</span>{" "}
                          {missingList.map((h: number) => `H${h}`).join(", ")}
                        </div>
                      )}
                      {denList.length > 0 && (
                        <div className="text-rose-700">
                          <span className="font-bold">Denying Houses:</span>{" "}
                          {denList.map((h: HouseSignificationDetail) => `H${h.house}(${h.level})`).join(", ") || "None"}
                        </div>
                      )}
                    </div>

                    {/* Retrograde / CSL notes */}
                    {retroNote && (
                      <div className="text-[10px] font-medium text-amber-800 bg-amber-100/70 px-1.5 py-0.5 rounded">
                        ⚠️ {retroNote}
                      </div>
                    )}
                    {ev.csl_adjustment && (
                      <div className="text-[10px] font-medium text-indigo-800 bg-indigo-50 px-1.5 py-0.5 rounded">
                        ℹ️ CSL: {ev.csl_adjustment}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {/* Section 9 / 12 Disclaimer */}
          <div className="pt-1.5 border-t border-[#EADFCB] text-[10px] text-[#64748B] italic text-right">
            Indicative KP hint, confirm with CSL and transit before decisions.
          </div>
        </div>
      )}

      {/* Sub-Periods Container (Recursively renders immediate children when expanded) */}
      {isExpanded && hasSubPeriods && (
        <div className="border-t border-[#E8DEC8] divide-y divide-[#EFEAE2]">
          {node.sub_periods!.map((subNode) => {
            const subKey = `${getLevelPrefix(subNode.level)}-${[...path, subNode.lord].join("-")}`;
            return (
              <DasaNodeRow
                key={subKey}
                node={subNode}
                path={[...path, subNode.lord]}
                nodeKey={subKey}
                expandedKeys={expandedKeys}
                onToggleExpand={onToggleExpand}
                activeHierarchy={activeHierarchy}
                resolvedBirthDate={resolvedBirthDate}
                utcOffsetHours={utcOffsetHours}
                planetContexts={planetContexts}
                language={language}
                t={t}
                eventPredictionsMap={eventPredictionsMap}
                showKpEvents={showKpEvents}
                selectedEventFilter={selectedEventFilter}
              />
            );
          })}
        </div>
      )}
    </div>
  );
}

function getLevelPrefix(level: string): string {
  const norm = level.toLowerCase();
  if (norm.includes("maha")) return "maha";
  if (norm.includes("praty")) return "pratyantar";
  if (norm.includes("antar")) return "antar";
  if (norm.includes("sookshma")) return "sookshma";
  return "prana";
}
