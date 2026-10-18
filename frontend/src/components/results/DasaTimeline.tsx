"use client";

import React, { useState, useMemo, useEffect } from "react";
import {
  DasaResponse,
  DasaPeriodNode,
  HoroscopeResponse,
  KpResponse,
  KpEventAnalysisResponse,
  PeriodAnalysisResult,
} from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { getLordName, getGrahaShort, GRAHAS, TranslationDictionary } from "@/lib/translations";
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
  ChevronsUp,
  Filter,
  Plus,
  Minus,
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
    0.5
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

  // Expanded nodes mapping
  const [expandedKeys, setExpandedKeys] = useState<Record<string, boolean>>(() => {
    // By default expand first two Mahadashas and active Mahadasha
    return { "maha-0": true, "maha-1": true };
  });

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

    return { activeHierarchy: hierarchy, selectedDateAge: ageStr, isDateOutOfRange: false };
  }, [dasa, selectedDate, resolvedBirthDate, language]);

  // Keep active Mahadasha auto-expanded
  useEffect(() => {
    if (activeHierarchy?.mahadasha && dasa?.dasa_tree) {
      const activeIdx = dasa.dasa_tree.findIndex(
        (m) => m.lord.toLowerCase() === activeHierarchy.mahadasha?.lord.toLowerCase()
      );
      if (activeIdx !== -1) {
        setExpandedKeys((prev) => ({
          ...prev,
          [`maha-${activeIdx}`]: true,
        }));
      }
    }
  }, [activeHierarchy, dasa]);

  const toggleExpand = (key: string) => {
    setExpandedKeys((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const expandAllMaha = () => {
    if (!dasa?.dasa_tree) return;
    const map: Record<string, boolean> = {};
    dasa.dasa_tree.forEach((_, idx) => {
      map[`maha-${idx}`] = true;
    });
    setExpandedKeys(map);
  };

  const expandToAntaram = () => {
    if (!dasa?.dasa_tree) return;
    const map: Record<string, boolean> = {};
    dasa.dasa_tree.forEach((m, mIdx) => {
      map[`maha-${mIdx}`] = true;
      m.sub_periods?.forEach((b, bIdx) => {
        map[`maha-${mIdx}-bhukti-${bIdx}`] = true;
      });
    });
    setExpandedKeys(map);
  };

  const collapseAll = () => {
    setExpandedKeys({});
  };

  const expandActivePath = () => {
    if (!activeHierarchy || !dasa?.dasa_tree) return;
    const map: Record<string, boolean> = {};
    const { mahadasha, antardasha, pratyantardasha } = activeHierarchy;

    dasa.dasa_tree.forEach((m, mIdx) => {
      if (mahadasha && m.lord.toLowerCase() === mahadasha.lord.toLowerCase()) {
        map[`maha-${mIdx}`] = true;
        m.sub_periods?.forEach((b, bIdx) => {
          if (antardasha && b.lord.toLowerCase() === antardasha.lord.toLowerCase()) {
            map[`maha-${mIdx}-bhukti-${bIdx}`] = true;
            b.sub_periods?.forEach((p, pIdx) => {
              if (pratyantardasha && p.lord.toLowerCase() === pratyantardasha.lord.toLowerCase()) {
                map[`maha-${mIdx}-bhukti-${bIdx}-antar-${pIdx}`] = true;
              }
            });
          }
        });
      }
    });
    setExpandedKeys((prev) => ({ ...prev, ...map }));
  };

  if (!dasa || !dasa.dasa_tree || dasa.dasa_tree.length === 0) {
    return (
      <div className="p-8 text-center bg-white rounded-2xl border border-[#D9DEE7] text-xs text-[#8190A6]">
        {t.dasaNoPeriodsAvailable || "No Dasa periods available."}
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {/* 1. Header Toolbar & Quick Controls */}
      <div className="bg-white rounded-2xl border border-[#D9DEE7] p-4 sm:p-5 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Left: Active Period Overview */}
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#153F6B]" />
            <h3 className="font-bold text-sm text-[#183047]">
              {language === "ta" ? "விம்சோத்தரி தசா-புக்தி அட்டவணை" : "Vimshottari Dasa-Bhukti Schedule"}
            </h3>
          </div>
          {activeHierarchy?.mahadasha && (
            <div className="text-xs text-[#8190A6] flex items-center gap-2 flex-wrap">
              <span>
                {language === "ta" ? "நடப்பு தசா:" : "Current Dasa:"}{" "}
                <strong className="text-[#153F6B]">
                  {getLordName(activeHierarchy.mahadasha.lord, language)}
                </strong>
              </span>
              {activeHierarchy.antardasha && (
                <span>
                  / புக்தி:{" "}
                  <strong className="text-[#B4872B]">
                    {getLordName(activeHierarchy.antardasha.lord, language)}
                  </strong>
                </span>
              )}
              {selectedDateAge && <span>• வயது: {selectedDateAge}</span>}
            </div>
          )}
        </div>

        {/* Right: Expand / Collapse Actions & Filter */}
        <div className="flex items-center gap-1.5 flex-wrap text-xs">
          {/* Target Date Picker */}
          <div className="flex items-center gap-1 bg-[#F2F3F5] px-2 py-1 rounded-lg border border-[#D9DEE7]">
            <Calendar className="w-3.5 h-3.5 text-[#8190A6]" />
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="bg-transparent text-xs text-[#183047] font-semibold outline-none cursor-pointer"
            />
          </div>

          <button
            type="button"
            onClick={expandAllMaha}
            className="px-2.5 py-1 rounded-lg border border-[#D9DEE7] bg-white hover:bg-[#F2F3F5] text-[#183047] font-medium transition-colors cursor-pointer"
          >
            {language === "ta" ? "அனைத்து தசா" : "All Maha"}
          </button>

          <button
            type="button"
            onClick={expandActivePath}
            className="px-2.5 py-1 rounded-lg border border-[#B4872B] bg-[#FAF2DE] text-[#8C6D23] font-bold inline-flex items-center gap-1 transition-colors cursor-pointer"
          >
            <Sparkles className="w-3 h-3 text-[#B4872B]" />
            <span>{language === "ta" ? "நடப்பு தசை" : "Active Dasa"}</span>
          </button>

          <button
            type="button"
            onClick={collapseAll}
            className="px-2.5 py-1 rounded-lg border border-[#D9DEE7] bg-white hover:bg-[#F2F3F5] text-[#8190A6] hover:text-[#183047] font-medium transition-colors cursor-pointer"
            title={t.dasaCollapseAll}
          >
            <ChevronsUp className="w-3.5 h-3.5 inline mr-0.5" />
            <span>{language === "ta" ? "சுருக்குக" : "Collapse"}</span>
          </button>
        </div>
      </div>

      {/* 2. Responsive 2-Column Grid of Mahadasha Cards matching Screenshot 4 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {dasa.dasa_tree.map((maha, mIdx) => {
          const mKey = `maha-${mIdx}`;
          const isMahaExpanded = !!expandedKeys[mKey];
          const isMahaActive =
            activeHierarchy?.mahadasha?.lord.toLowerCase() === maha.lord.toLowerCase();

          return (
            <MahadashaCard
              key={mKey}
              maha={maha}
              mIdx={mIdx}
              isExpanded={isMahaExpanded}
              isActive={isMahaActive}
              onToggleMaha={() => toggleExpand(mKey)}
              expandedKeys={expandedKeys}
              onToggleKey={toggleExpand}
              activeHierarchy={activeHierarchy}
              resolvedBirthDate={resolvedBirthDate}
              utcOffsetHours={utcOffsetHours}
              planetContexts={planetContexts}
              language={language}
              t={t}
            />
          );
        })}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Mahadasha Card Component matching Screenshot 4
// ---------------------------------------------------------------------------

interface MahadashaCardProps {
  maha: DasaPeriodNode;
  mIdx: number;
  isExpanded: boolean;
  isActive: boolean;
  onToggleMaha: () => void;
  expandedKeys: Record<string, boolean>;
  onToggleKey: (key: string) => void;
  activeHierarchy: ActiveHierarchy | null;
  resolvedBirthDate: string;
  utcOffsetHours: number;
  planetContexts: Record<string, PlanetContext> | null;
  language: "en" | "ta";
  t: TranslationDictionary;
}

function MahadashaCard({
  maha,
  mIdx,
  isExpanded,
  isActive,
  onToggleMaha,
  expandedKeys,
  onToggleKey,
  activeHierarchy,
  resolvedBirthDate,
  utcOffsetHours,
  planetContexts,
  language,
  t,
}: MahadashaCardProps) {
  // Dates in DD/MM/YYYY
  const sDt = jdToCalendarDateTime(maha.start_jd, utcOffsetHours);
  const eDt = jdToCalendarDateTime(maha.end_jd, utcOffsetHours);
  const sDateStr = sDt
    ? `${String(sDt.day).padStart(2, "0")}/${String(sDt.month).padStart(2, "0")}/${sDt.year}`
    : "—";
  const eDateStr = eDt
    ? `${String(eDt.day).padStart(2, "0")}/${String(eDt.month).padStart(2, "0")}/${eDt.year}`
    : "—";

  // Label: Lord name with Star Lord in parentheses (e.g. சந் (சந்), குரு (சந்), செ (பு))
  const starLordName = useMemo(() => {
    if (planetContexts && maha.lord) {
      return calculateBenefitBhavas(maha.lord, planetContexts).starLord;
    }
    return maha.star_lord || maha.lord;
  }, [maha.lord, maha.star_lord, planetContexts]);

  const mahaTitle = useMemo(() => {
    if (language === "ta") {
      const lShort = getGrahaShort(maha.lord, "ta");
      const sShort = getGrahaShort(starLordName, "ta");
      return `${lShort} (${sShort})`;
    }
    return `${maha.lord} (${starLordName?.slice(0, 3) || "Star"})`;
  }, [maha.lord, starLordName, language]);

  return (
    <div className="rounded-xl border border-[#D9DEE7] bg-white shadow-2xs overflow-hidden flex flex-col justify-start">
      {/* Mahadasha Card Header matching Screenshot 4 */}
      <div
        onClick={onToggleMaha}
        className={`px-3.5 py-2.5 flex items-center justify-between text-xs sm:text-sm font-bold transition-colors cursor-pointer select-none ${
          isActive
            ? "bg-[#153F6B] text-white"
            : "bg-[#E2E8F0] text-[#183047] hover:bg-[#D9DEE7]"
        }`}
      >
        <div className="flex items-center gap-2">
          {/* Toggle Button [-] / [+] */}
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onToggleMaha();
            }}
            className={`w-4 h-4 rounded-full flex items-center justify-center font-bold text-xs border ${
              isActive
                ? "border-white/50 text-white bg-white/20"
                : "border-[#183047]/40 text-[#183047] bg-white"
            }`}
          >
            {isExpanded ? <Minus className="w-2.5 h-2.5" /> : <Plus className="w-2.5 h-2.5" />}
          </button>
          <span>{mahaTitle}</span>
        </div>

        {/* Date Range: DD/MM/YYYY - DD/MM/YYYY */}
        <div className={`font-mono text-xs ${isActive ? "text-white" : "text-[#52667E]"}`}>
          {sDateStr} - {eDateStr}
        </div>
      </div>

      {/* Inner Bhukti Table matching Screenshot 4 */}
      {isExpanded && maha.sub_periods && maha.sub_periods.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-[#FAF2DE] text-[#183047] font-bold border-b border-[#D8BD80]">
              <tr>
                <th className="py-2 px-3 text-left">Bukthi</th>
                <th className="py-2 px-3 text-left">From</th>
                <th className="py-2 px-3 text-left">To</th>
                <th className="py-2 px-3 text-left">Duration</th>
                <th className="py-2 px-3 text-left">Benefit Bhavas</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F2F3F5] text-[#183047]">
              {maha.sub_periods.map((bhukti, bIdx) => {
                const bKey = `maha-${mIdx}-bhukti-${bIdx}`;
                const isBhuktiExpanded = !!expandedKeys[bKey];
                const isBhuktiActive =
                  isActive &&
                  activeHierarchy?.antardasha?.lord.toLowerCase() === bhukti.lord.toLowerCase();

                return (
                  <React.Fragment key={bKey}>
                    <BhuktiRow
                      bhukti={bhukti}
                      mIdx={mIdx}
                      bIdx={bIdx}
                      bKey={bKey}
                      isExpanded={isBhuktiExpanded}
                      isActive={isBhuktiActive}
                      onToggle={() => onToggleKey(bKey)}
                      resolvedBirthDate={resolvedBirthDate}
                      utcOffsetHours={utcOffsetHours}
                      planetContexts={planetContexts}
                      language={language}
                      t={t}
                    />

                    {/* Sub-Periods: Antardashas when expanded */}
                    {isBhuktiExpanded && bhukti.sub_periods && bhukti.sub_periods.length > 0 && (
                      <tr className="bg-[#F8FAFC]">
                        <td colSpan={5} className="p-2 sm:p-3">
                          <div className="pl-4 border-l-2 border-[#153F6B]/30 space-y-1">
                            <div className="text-[11px] font-bold text-[#153F6B] uppercase tracking-wider mb-1">
                              {language === "ta" ? "அந்தர காலங்கள்" : "Antardasha Periods"}
                            </div>
                            <div className="divide-y divide-[#E2E8F0] bg-white rounded-lg border border-[#D9DEE7] overflow-hidden">
                              {bhukti.sub_periods.map((antar, aIdx) => {
                                const aKey = `${bKey}-antar-${aIdx}`;
                                const isAntarExpanded = !!expandedKeys[aKey];
                                const isAntarActive =
                                  isBhuktiActive &&
                                  activeHierarchy?.pratyantardasha?.lord.toLowerCase() ===
                                    antar.lord.toLowerCase();

                                return (
                                  <AntardashaRow
                                    key={aKey}
                                    antar={antar}
                                    aKey={aKey}
                                    isExpanded={isAntarExpanded}
                                    isActive={isAntarActive}
                                    onToggle={() => onToggleKey(aKey)}
                                    resolvedBirthDate={resolvedBirthDate}
                                    utcOffsetHours={utcOffsetHours}
                                    planetContexts={planetContexts}
                                    language={language}
                                    t={t}
                                  />
                                );
                              })}
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Bhukti Row Component matching Screenshot 4
// ---------------------------------------------------------------------------

interface BhuktiRowProps {
  bhukti: DasaPeriodNode;
  mIdx: number;
  bIdx: number;
  bKey: string;
  isExpanded: boolean;
  isActive: boolean;
  onToggle: () => void;
  resolvedBirthDate: string;
  utcOffsetHours: number;
  planetContexts: Record<string, PlanetContext> | null;
  language: "en" | "ta";
  t: TranslationDictionary;
}

function BhuktiRow({
  bhukti,
  bKey,
  isExpanded,
  isActive,
  onToggle,
  resolvedBirthDate,
  utcOffsetHours,
  planetContexts,
  language,
}: BhuktiRowProps) {
  // Start & End Dates
  const sDt = jdToCalendarDateTime(bhukti.start_jd, utcOffsetHours);
  const eDt = jdToCalendarDateTime(bhukti.end_jd, utcOffsetHours);
  const sDateStr = sDt
    ? `${String(sDt.day).padStart(2, "0")}/${String(sDt.month).padStart(2, "0")}/${sDt.year}`
    : "—";
  const eDateStr = eDt
    ? `${String(eDt.day).padStart(2, "0")}/${String(eDt.month).padStart(2, "0")}/${eDt.year}`
    : "—";

  // Duration decimal (Y.M.D)
  const durationYmd = useMemo(() => {
    if (!sDt || !eDt) return "—";
    const diff = calculateCalendarAge(sDt.year, sDt.month, sDt.day, eDt.year, eDt.month, eDt.day);
    if (!diff) return "—";
    return `${diff.years}.${diff.months}.${diff.days}`;
  }, [sDt, eDt]);

  // Age duration in period e.g. (0Y 4M) or (1Y 10M)
  const periodAgeStr = useMemo(() => {
    if (!resolvedBirthDate || !sDt || !eDt) return "";
    const [by, bm, bd] = resolvedBirthDate.split("-").map(Number);
    const ageAtStart = calculateCalendarAge(by, bm, bd, sDt.year, sDt.month, sDt.day);
    if (!ageAtStart) return "";
    return `(${ageAtStart.years}Y ${ageAtStart.months}M)`;
  }, [resolvedBirthDate, sDt, eDt]);

  // Benefit Bhavas
  const { starLordName, benefitBhavas } = useMemo(() => {
    if (planetContexts && bhukti.lord) {
      const res = calculateBenefitBhavas(bhukti.lord, planetContexts);
      return {
        starLordName: res.starLord,
        benefitBhavas: res.formatted,
      };
    }
    return {
      starLordName: bhukti.star_lord || bhukti.lord,
      benefitBhavas: bhukti.benefit_bhavas || "—",
    };
  }, [bhukti.lord, bhukti.star_lord, bhukti.benefit_bhavas, planetContexts]);

  // Label: e.g. சுக் (பு)
  const bhuktiLabel = useMemo(() => {
    if (language === "ta") {
      const lShort = getGrahaShort(bhukti.lord, "ta");
      const sShort = getGrahaShort(starLordName, "ta");
      return `${lShort} (${sShort})`;
    }
    return `${bhukti.lord?.slice(0, 3)} (${starLordName?.slice(0, 3)})`;
  }, [bhukti.lord, starLordName, language]);

  const hasSub = bhukti.sub_periods && bhukti.sub_periods.length > 0;

  return (
    <tr className={`hover:bg-[#F2F3F5] transition-colors ${isActive ? "bg-[#FAF2DE]/50 font-bold" : ""}`}>
      {/* Col 1: Bukthi */}
      <td className="py-2 px-3 font-semibold text-[#183047]">
        <div className="flex items-center gap-1.5">
          {hasSub ? (
            <button
              type="button"
              onClick={onToggle}
              className="w-3.5 h-3.5 rounded bg-slate-100 hover:bg-slate-200 border border-slate-300 flex items-center justify-center text-[10px] text-slate-700 cursor-pointer"
            >
              {isExpanded ? <Minus className="w-2 h-2" /> : <Plus className="w-2 h-2" />}
            </button>
          ) : (
            <span className="w-3.5 inline-block" />
          )}
          <span>{bhuktiLabel}</span>
          {isActive && (
            <span className="w-1.5 h-1.5 rounded-full bg-[#B4872B] inline-block shrink-0" />
          )}
        </div>
      </td>

      {/* Col 2: From */}
      <td className="py-2 px-3 font-mono text-[11px] text-[#52667E] whitespace-nowrap">
        {sDateStr}
      </td>

      {/* Col 3: To */}
      <td className="py-2 px-3 font-mono text-[11px] text-[#52667E] whitespace-nowrap">
        <span>{eDateStr}</span>
        {periodAgeStr && (
          <span className="text-amber-700 ml-1 text-[10px] font-sans font-normal">
            {periodAgeStr}
          </span>
        )}
      </td>

      {/* Col 4: Duration */}
      <td className="py-2 px-3 font-mono text-[11px] text-[#183047] whitespace-nowrap">
        {durationYmd}
      </td>

      {/* Col 5: Benefit Bhavas */}
      <td className="py-2 px-3 font-mono text-[11px] font-semibold text-[#183047]">
        {benefitBhavas}
      </td>
    </tr>
  );
}

// ---------------------------------------------------------------------------
// Antardasha Row Component (for level 3 hierarchy inside Bhukti)
// ---------------------------------------------------------------------------

interface AntardashaRowProps {
  antar: DasaPeriodNode;
  aKey: string;
  isExpanded: boolean;
  isActive: boolean;
  onToggle: () => void;
  resolvedBirthDate: string;
  utcOffsetHours: number;
  planetContexts: Record<string, PlanetContext> | null;
  language: "en" | "ta";
  t: TranslationDictionary;
}

function AntardashaRow({
  antar,
  isExpanded,
  isActive,
  onToggle,
  utcOffsetHours,
  planetContexts,
  language,
}: AntardashaRowProps) {
  const sDt = jdToCalendarDateTime(antar.start_jd, utcOffsetHours);
  const eDt = jdToCalendarDateTime(antar.end_jd, utcOffsetHours);
  const sDateStr = sDt
    ? `${String(sDt.day).padStart(2, "0")}/${String(sDt.month).padStart(2, "0")}/${sDt.year}`
    : "—";
  const eDateStr = eDt
    ? `${String(eDt.day).padStart(2, "0")}/${String(eDt.month).padStart(2, "0")}/${eDt.year}`
    : "—";

  const durationYmd = useMemo(() => {
    if (!sDt || !eDt) return "—";
    const diff = calculateCalendarAge(sDt.year, sDt.month, sDt.day, eDt.year, eDt.month, eDt.day);
    if (!diff) return "—";
    return `${diff.years}.${diff.months}.${diff.days}`;
  }, [sDt, eDt]);

  const starLordName = useMemo(() => {
    if (planetContexts && antar.lord) {
      return calculateBenefitBhavas(antar.lord, planetContexts).starLord;
    }
    return antar.star_lord || antar.lord;
  }, [antar.lord, antar.star_lord, planetContexts]);

  const antarLabel = useMemo(() => {
    if (language === "ta") {
      const lShort = getGrahaShort(antar.lord, "ta");
      const sShort = getGrahaShort(starLordName, "ta");
      return `${lShort} (${sShort})`;
    }
    return `${antar.lord?.slice(0, 3)} (${starLordName?.slice(0, 3)})`;
  }, [antar.lord, starLordName, language]);

  return (
    <div className={`p-2 flex items-center justify-between text-[11px] hover:bg-slate-50 ${isActive ? "bg-amber-50 font-bold" : ""}`}>
      <div className="flex items-center gap-2">
        <span className="px-1.5 py-0.2 rounded text-[9px] bg-slate-100 font-bold text-slate-700">
          Antar
        </span>
        <span className="font-semibold text-[#183047]">{antarLabel}</span>
      </div>

      <div className="flex items-center gap-3 font-mono text-[10px] text-[#52667E]">
        <span>{sDateStr} → {eDateStr}</span>
        <span className="font-bold text-[#183047]">{durationYmd}</span>
      </div>
    </div>
  );
}
