"use client";

import React, { useState, useMemo, useEffect } from "react";
import {
  DasaResponse,
  DasaPeriodNode,
  HoroscopeResponse,
  KpResponse,
  KpEventAnalysisResponse,
  PeriodAnalysisResult,
  BirthDasaBalance,
} from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { getLordName, getGrahaShort, TranslationDictionary } from "@/lib/translations";
import { analyzeKpEvents } from "@/lib/api";
import {
  jdToCalendarDateTime,
  calculateCalendarAge,
  formatCalendarAge,
  findActiveHierarchy,
  ActiveHierarchy,
  generateChildSubPeriods,
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
  ChevronsDown,
  Plus,
  Minus,
  Info,
  Compass,
  Layers,
  CheckCircle2,
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

function formatMoonLon(deg: number): string {
  const norm = ((deg % 360) + 360) % 360;
  const d = Math.floor(norm);
  const m = Math.floor((norm - d) * 60);
  const s = Math.round(((norm - d) * 60 - m) * 60);
  return `${d}° ${String(m).padStart(2, "0")}' ${String(s).padStart(2, "0")}" (${norm.toFixed(4)}°)`;
}

function formatDateStr(isoStr?: string, jd?: number, offsetHours: number = 0, isSubDaily: boolean = false): string {
  if (isoStr) {
    const parts = isoStr.split("T");
    if (parts[0]) {
      const [y, m, d] = parts[0].split("-");
      const dmy = `${d}/${m}/${y}`;
      if (isSubDaily && parts[1]) {
        return `${dmy} ${parts[1].slice(0, 8)}`;
      }
      return dmy;
    }
  }
  if (jd) {
    const dt = jdToCalendarDateTime(jd, offsetHours);
    if (dt) {
      const d = String(dt.day).padStart(2, "0");
      const m = String(dt.month).padStart(2, "0");
      const dmy = `${d}/${m}/${dt.year}`;
      if (isSubDaily) {
        const h = String(dt.hour).padStart(2, "0");
        const min = String(dt.minute).padStart(2, "0");
        const s = String(dt.second).padStart(2, "0");
        return `${dmy} ${h}:${min}:${s}`;
      }
      return dmy;
    }
  }
  return "—";
}

function formatDurationShort(node: DasaPeriodNode): string {
  if (node.duration_years >= 1.0) {
    const y = Math.floor(node.duration_years);
    const remDays = (node.duration_years - y) * 365.25;
    const m = Math.floor(remDays / 30.4375);
    const d = Math.round(remDays - m * 30.4375);
    return `${y}y ${m}m ${d}d`;
  }
  if (node.duration_days >= 30.0) {
    const m = Math.floor(node.duration_days / 30.4375);
    const d = Math.round(node.duration_days - m * 30.4375);
    return `${m}m ${d}d`;
  }
  if (node.duration_days >= 1.0) {
    return `${node.duration_days.toFixed(1)}d`;
  }
  const hrs = node.duration_days * 24.0;
  if (hrs >= 1.0) {
    return `${hrs.toFixed(1)}h`;
  }
  const mins = hrs * 60.0;
  return `${mins.toFixed(0)}m`;
}

interface LevelConfig {
  name: string;
  nameTamil: string;
  badgeLabel: string;
  badgeLabelTamil: string;
  badgeColor: string;
  rowIndent: string;
  levelNumber: number;
}

function getLevelConfig(level: string): LevelConfig {
  const norm = level.toLowerCase();
  if (norm.includes("maha")) {
    return {
      name: "Dasa",
      nameTamil: "மகாதசை",
      badgeLabel: "Dasa",
      badgeLabelTamil: "தசை",
      badgeColor: "bg-amber-100 text-amber-900 border-amber-300",
      rowIndent: "pl-2 sm:pl-3",
      levelNumber: 1,
    };
  }
  if (norm.includes("antar") && !norm.includes("praty")) {
    return {
      name: "Bhukti",
      nameTamil: "புக்தி",
      badgeLabel: "Bhukti",
      badgeLabelTamil: "புக்தி",
      badgeColor: "bg-blue-100 text-blue-900 border-blue-300",
      rowIndent: "pl-6 sm:pl-8",
      levelNumber: 2,
    };
  }
  if (norm.includes("praty")) {
    return {
      name: "Antharam",
      nameTamil: "அந்தரம்",
      badgeLabel: "Antharam",
      badgeLabelTamil: "அந்தரம்",
      badgeColor: "bg-emerald-100 text-emerald-900 border-emerald-300",
      rowIndent: "pl-10 sm:pl-14",
      levelNumber: 3,
    };
  }
  if (norm.includes("sookshma")) {
    return {
      name: "Sookshamam",
      nameTamil: "சூட்சுமம்",
      badgeLabel: "Sookshamam",
      badgeLabelTamil: "சூட்சுமம்",
      badgeColor: "bg-purple-100 text-purple-900 border-purple-300",
      rowIndent: "pl-14 sm:pl-20",
      levelNumber: 4,
    };
  }
  return {
    name: "Pranam",
    nameTamil: "பிராணம்",
    badgeLabel: "Pranam",
    badgeLabelTamil: "பிராணம்",
    badgeColor: "bg-rose-100 text-rose-900 border-rose-300",
    rowIndent: "pl-18 sm:pl-26",
    levelNumber: 5,
  };
}

export function DasaTimeline({
  dasa,
  birthDate: propBirthDate,
  birthTime: propBirthTime,
  timezone: propTimezone,
  horoscope,
  kp,
  kpEventAnalysis,
}: DasaTimelineProps) {
  const { language, t } = useLanguage();

  // KP Event Predictions Integration state
  const [internalKpAnalysis, setInternalKpAnalysis] = useState<KpEventAnalysisResponse | null>(null);

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

  const planetContexts = useMemo(() => {
    if (!horoscope?.planets || !horoscope?.ascendant) return null;
    return buildPlanetContexts(horoscope.planets, horoscope.ascendant, horoscope.houses);
  }, [horoscope]);

  // Resolve birth date & time from props or dasa metadata or first node
  const resolvedBirthDate = useMemo(() => {
    if (propBirthDate) return propBirthDate;
    if (dasa?.birth_dasa_balance?.birth_date) return dasa.birth_dasa_balance.birth_date;
    if (dasa?.metadata?.birth_utc_iso) {
      return dasa.metadata.birth_utc_iso.split("T")[0];
    }
    if (dasa?.dasa_tree && dasa.dasa_tree.length > 0) {
      const dt = jdToCalendarDateTime(dasa.dasa_tree[0].start_jd);
      if (dt) return dt.dateStr;
    }
    return "";
  }, [propBirthDate, dasa]);

  const resolvedBirthTime = useMemo(() => {
    if (propBirthTime) return propBirthTime;
    if (dasa?.birth_dasa_balance?.birth_time) return dasa.birth_dasa_balance.birth_time;
    if (dasa?.metadata?.birth_utc_iso) {
      const parts = dasa.metadata.birth_utc_iso.split("T");
      if (parts[1]) return parts[1].slice(0, 8);
    }
    return "—";
  }, [propBirthTime, dasa]);

  const resolvedTimezone = useMemo(() => {
    return propTimezone || dasa?.metadata?.local_timezone || "Asia/Kolkata";
  }, [propTimezone, dasa]);

  const utcOffsetHours = dasa?.metadata?.utc_offset_hours || 0;

  // Selected date for active period detection (defaults to target_date or today)
  const defaultTargetDate = useMemo(() => {
    if (dasa?.active_period?.target_date_iso) {
      return dasa.active_period.target_date_iso;
    }
    return new Date().toISOString().split("T")[0];
  }, [dasa]);

  const [selectedDate, setSelectedDate] = useState<string>(defaultTargetDate);
  const [showLegend, setShowLegend] = useState<boolean>(false);

  // Expanded nodes mapping
  const [expandedKeys, setExpandedKeys] = useState<Record<string, boolean>>(() => {
    // By default expand first Mahadasha (balance dasha)
    return { "node-0": true };
  });

  // Compute active hierarchy and person's age on selected date
  const { activeHierarchy, selectedDateAge, targetJd } = useMemo(() => {
    if (!dasa?.dasa_tree || dasa.dasa_tree.length === 0 || !selectedDate) {
      return { activeHierarchy: null, selectedDateAge: null, targetJd: 0 };
    }

    const tJd = dateToJd(selectedDate);
    const tree = dasa.dasa_tree;
    const startJd = tree[0].start_jd;
    const endJd = tree[tree.length - 1].end_jd;

    if (tJd < startJd || tJd >= endJd) {
      return { activeHierarchy: null, selectedDateAge: null, targetJd: tJd };
    }

    const hierarchy = findActiveHierarchy(tree, tJd);

    let ageStr: string | null = null;
    if (resolvedBirthDate) {
      const [by, bm, bd] = resolvedBirthDate.split("-").map(Number);
      const [ty, tm, td] = selectedDate.split("-").map(Number);
      const ageObj = calculateCalendarAge(by, bm, bd, ty, tm, td);
      ageStr = formatCalendarAge(ageObj, language);
    }

    return { activeHierarchy: hierarchy, selectedDateAge: ageStr, targetJd: tJd };
  }, [dasa, selectedDate, resolvedBirthDate, language]);

  const toggleExpand = (key: string) => {
    setExpandedKeys((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const expandAllLevel1 = () => {
    if (!dasa?.dasa_tree) return;
    const map: Record<string, boolean> = {};
    dasa.dasa_tree.forEach((_, idx) => {
      map[`node-${idx}`] = true;
    });
    setExpandedKeys(map);
  };

  const expandToLevel2 = () => {
    if (!dasa?.dasa_tree) return;
    const map: Record<string, boolean> = {};
    dasa.dasa_tree.forEach((m, mIdx) => {
      map[`node-${mIdx}`] = true;
    });
    setExpandedKeys(map);
  };

  const expandToLevel3 = () => {
    if (!dasa?.dasa_tree) return;
    const map: Record<string, boolean> = {};
    dasa.dasa_tree.forEach((m, mIdx) => {
      map[`node-${mIdx}`] = true;
      const bChildren = m.sub_periods && m.sub_periods.length > 0
        ? m.sub_periods
        : generateChildSubPeriods(m, utcOffsetHours, resolvedBirthDate);
      bChildren.forEach((_, bIdx) => {
        map[`node-${mIdx}-${bIdx}`] = true;
      });
    });
    setExpandedKeys(map);
  };

  const expandToLevel4 = () => {
    if (!dasa?.dasa_tree) return;
    const map: Record<string, boolean> = {};
    dasa.dasa_tree.forEach((m, mIdx) => {
      map[`node-${mIdx}`] = true;
      const bChildren = m.sub_periods && m.sub_periods.length > 0
        ? m.sub_periods
        : generateChildSubPeriods(m, utcOffsetHours, resolvedBirthDate);
      bChildren.forEach((b, bIdx) => {
        map[`node-${mIdx}-${bIdx}`] = true;
        const pChildren = b.sub_periods && b.sub_periods.length > 0
          ? b.sub_periods
          : generateChildSubPeriods(b, utcOffsetHours, resolvedBirthDate);
        pChildren.forEach((_, pIdx) => {
          map[`node-${mIdx}-${bIdx}-${pIdx}`] = true;
        });
      });
    });
    setExpandedKeys(map);
  };

  const expandAllFiveLevels = () => {
    if (!dasa?.dasa_tree) return;
    const map: Record<string, boolean> = {};
    const recurse = (nodes: DasaPeriodNode[], prefix: string, currDepth: number) => {
      nodes.forEach((n, idx) => {
        const k = prefix ? `${prefix}-${idx}` : `node-${idx}`;
        map[k] = true;
        if (currDepth < 5) {
          const ch = n.sub_periods && n.sub_periods.length > 0
            ? n.sub_periods
            : generateChildSubPeriods(n, utcOffsetHours, resolvedBirthDate);
          if (ch.length > 0) {
            recurse(ch, k, currDepth + 1);
          }
        }
      });
    };
    recurse(dasa.dasa_tree, "", 1);
    setExpandedKeys(map);
  };

  const collapseAll = () => {
    setExpandedKeys({});
  };

  const expandActivePath = () => {
    if (!dasa?.dasa_tree) return;
    const map: Record<string, boolean> = {};
    const recurseActive = (nodes: DasaPeriodNode[], prefix: string, currDepth: number) => {
      nodes.forEach((n, idx) => {
        const k = prefix ? `${prefix}-${idx}` : `node-${idx}`;
        if (targetJd >= n.start_jd && targetJd < n.end_jd) {
          map[k] = true;
          if (currDepth < 5) {
            const ch = n.sub_periods && n.sub_periods.length > 0
              ? n.sub_periods
              : generateChildSubPeriods(n, utcOffsetHours, resolvedBirthDate);
            if (ch.length > 0) {
              recurseActive(ch, k, currDepth + 1);
            }
          }
        }
      });
    };
    recurseActive(dasa.dasa_tree, "", 1);
    setExpandedKeys((prev) => ({ ...prev, ...map }));
  };

  // Derive or extract authoritative Birth Dasa Balance
  const birthBalance = useMemo(() => {
    if (dasa?.birth_dasa_balance) {
      return dasa.birth_dasa_balance;
    }
    // Fallback: reconstruct from dasa properties
    if (!dasa?.dasa_tree || dasa.dasa_tree.length === 0) return null;
    const firstMaha = dasa.dasa_tree[0];
    const firstBhukti = firstMaha.sub_periods && firstMaha.sub_periods.length > 0 ? firstMaha.sub_periods[0] : null;

    const fullYears = 6.0; // conservative fallback
    const remDays = firstMaha.duration_days;
    const fullDays = firstMaha.duration_years * 365.25;

    return {
      birth_date: resolvedBirthDate,
      birth_time: resolvedBirthTime,
      moon_sidereal_deg: dasa.moon_sidereal_deg,
      nakshatra_name: dasa.nakshatra?.name || "—",
      nakshatra_pada: dasa.nakshatra?.pada || 1,
      nakshatra_lord: dasa.nakshatra?.lord || firstMaha.lord,
      starting_mahadasha_lord: firstMaha.lord,
      mahadasha_full_duration: {
        years: Math.round(firstMaha.duration_years),
        months: 0,
        days: 0,
        total_days: fullDays,
        total_years: firstMaha.duration_years,
        formatted: `${firstMaha.duration_years.toFixed(2)} Years`,
      },
      elapsed_duration: {
        years: 0,
        months: 0,
        days: 0,
        total_days: 0,
        total_years: 0,
        formatted: "—",
      },
      remaining_balance: {
        years: Math.floor(firstMaha.duration_years),
        months: Math.floor(((firstMaha.duration_years % 1) * 365.25) / 30.4375),
        days: Math.round(((firstMaha.duration_years % 1) * 365.25) % 30.4375),
        total_days: remDays,
        total_years: firstMaha.duration_years,
        formatted: dasa.birth_balance_formatted,
      },
      starting_bhukti_lord: firstBhukti?.lord,
      starting_bhukti_remaining: firstBhukti
        ? {
            years: Math.floor(firstBhukti.duration_years),
            months: Math.floor(((firstBhukti.duration_years % 1) * 365.25) / 30.4375),
            days: Math.round(((firstBhukti.duration_years % 1) * 365.25) % 30.4375),
            total_days: firstBhukti.duration_days,
            total_years: firstBhukti.duration_years,
            formatted: formatDurationShort(firstBhukti),
          }
        : undefined,
      next_dasa_transition_date: formatDateStr(firstMaha.end_date_iso, firstMaha.end_jd, utcOffsetHours),
      next_dasa_transition_jd: firstMaha.end_jd,
    } as BirthDasaBalance;
  }, [dasa, resolvedBirthDate, resolvedBirthTime, utcOffsetHours]);

  if (!dasa || !dasa.dasa_tree || dasa.dasa_tree.length === 0) {
    return (
      <div className="p-8 text-center bg-white rounded-2xl border border-[#D9DEE7] text-xs text-[#8190A6]">
        {t.dasaNoPeriodsAvailable || "No Dasa periods available."}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ========================================================================= */}
      {/* 1. Birth-Time Dasa Balance (தசா இருப்பு) Section - Mandatory Specification */}
      {/* ========================================================================= */}
      {birthBalance && (
        <div className="rounded-2xl border-2 border-[#D8BD80] bg-[#FAF6EC] shadow-sm overflow-hidden">
          {/* Section Header */}
          <div className="px-5 py-4 bg-[#FAF2DE] border-b border-[#D8BD80] flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="space-y-0.5">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-[#B4872B]" />
                <h2 className="text-base sm:text-lg font-bold font-serif text-[#183047]">
                  {language === "ta" ? "தசா இருப்பு" : "Vimshottari Dasa Balance at Birth"}
                </h2>
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-[#153F6B] text-white">
                  {language === "ta" ? "பிறப்பு இருப்பு" : "At Birth"}
                </span>
              </div>
              <p className="text-xs text-[#8C6D23] font-medium">
                {language === "ta"
                  ? "விம்சோத்தரி தசா-புக்தி இருப்பு கால அளவு (Vimshottari Dasa Balance at Birth)"
                  : "Authoritative Vimshottari Dasa-Bhukti duration remaining at the exact moment of birth"}
              </p>
            </div>

            <div className="text-xs text-[#153F6B] font-mono bg-white/70 px-3 py-1.5 rounded-lg border border-[#D8BD80]/60 flex items-center gap-2 self-start sm:self-auto">
              <Clock className="w-3.5 h-3.5 text-[#B4872B]" />
              <span>
                {birthBalance.birth_date} • {birthBalance.birth_time} ({resolvedTimezone})
              </span>
            </div>
          </div>

          {/* Section Grid: 9 Essential Authoritative Facts */}
          <div className="p-4 sm:p-5 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5 text-xs">
            {/* Card 1: Moon Sidereal Longitude */}
            <div className="p-3 rounded-xl bg-white border border-[#D9DEE7] space-y-1 shadow-2xs">
              <div className="text-[11px] font-semibold text-[#8190A6] flex items-center justify-between">
                <span>{language === "ta" ? "பிறப்பு சந்திரன் பாகை" : "Birth Moon's Longitude"}</span>
                <Compass className="w-3.5 h-3.5 text-[#153F6B]" />
              </div>
              <div className="font-mono font-bold text-sm text-[#183047]">
                {formatMoonLon(birthBalance.moon_sidereal_deg)}
              </div>
              <div className="text-[10px] text-[#52667E]">
                {language === "ta" ? "நிரயண சயன முறை (Sidereal)" : "Sidereal Zodiac"}
              </div>
            </div>

            {/* Card 2: Birth Nakshatra & Pada */}
            <div className="p-3 rounded-xl bg-white border border-[#D9DEE7] space-y-1 shadow-2xs">
              <div className="text-[11px] font-semibold text-[#8190A6] flex items-center justify-between">
                <span>{language === "ta" ? "பிறப்பு நட்சத்திரம் & பாதம்" : "Birth Nakshatra & Pada"}</span>
                <Sparkles className="w-3.5 h-3.5 text-[#B4872B]" />
              </div>
              <div className="font-bold text-sm text-[#183047]">
                {birthBalance.nakshatra_name}{" "}
                <span className="text-[#153F6B]">
                  • {language === "ta" ? "பாதம்" : "Pada"} {birthBalance.nakshatra_pada}
                </span>
              </div>
              <div className="text-[10px] text-[#52667E]">
                {language === "ta" ? "நட்சத்திர அதிபதி:" : "Star Lord:"}{" "}
                <strong>{getLordName(birthBalance.nakshatra_lord, language)}</strong>
              </div>
            </div>

            {/* Card 3: Starting Mahadasha Lord */}
            <div className="p-3 rounded-xl bg-white border border-[#D9DEE7] space-y-1 shadow-2xs">
              <div className="text-[11px] font-semibold text-[#8190A6] flex items-center justify-between">
                <span>{language === "ta" ? "ஆரம்ப மகாதசா அதிபதி" : "Starting Mahadasha Lord"}</span>
                <Layers className="w-3.5 h-3.5 text-[#153F6B]" />
              </div>
              <div className="font-bold text-sm text-[#153F6B]">
                {getLordName(birthBalance.starting_mahadasha_lord, language)} (
                {birthBalance.starting_mahadasha_lord})
              </div>
              <div className="text-[10px] text-[#52667E]">
                {language === "ta" ? "முழு கால அளவு:" : "Full Duration:"}{" "}
                <strong>{birthBalance.mahadasha_full_duration.formatted}</strong> (
                {birthBalance.mahadasha_full_duration.total_days.toFixed(1)}d)
              </div>
            </div>

            {/* Card 4: Elapsed Mahadasha at Birth */}
            <div className="p-3 rounded-xl bg-white border border-[#D9DEE7] space-y-1 shadow-2xs">
              <div className="text-[11px] font-semibold text-[#8190A6]">
                {language === "ta" ? "பிறப்பில் சென்ற தசா காலம்" : "Elapsed Dasa Duration at Birth"}
              </div>
              <div className="font-bold text-sm text-[#52667E]">
                {birthBalance.elapsed_duration.formatted}
              </div>
              <div className="text-[10px] font-mono text-[#8190A6]">
                {birthBalance.elapsed_duration.total_days.toFixed(2)} {language === "ta" ? "நாட்கள்" : "Days"} (
                {birthBalance.elapsed_duration.total_years.toFixed(4)}y)
              </div>
            </div>

            {/* Card 5: Remaining Dasa Balance at Birth (The Core Balance) */}
            <div className="p-3 rounded-xl bg-[#FAF2DE] border border-[#D8BD80] space-y-1 shadow-2xs sm:col-span-2 lg:col-span-1">
              <div className="text-[11px] font-bold text-[#8C6D23] flex items-center justify-between">
                <span>{language === "ta" ? "பிறப்பில் தசா இருப்பு (மீதம்)" : "Remaining Dasa Balance at Birth"}</span>
                <CheckCircle2 className="w-4 h-4 text-[#B4872B]" />
              </div>
              <div className="font-bold text-base text-[#153F6B]">
                {birthBalance.remaining_balance.formatted}
              </div>
              <div className="text-[10px] font-mono text-[#8C6D23]">
                {birthBalance.remaining_balance.total_days.toFixed(2)} {language === "ta" ? "நாட்கள்" : "Days"} (
                {birthBalance.remaining_balance.total_years.toFixed(6)}y)
              </div>
            </div>

            {/* Card 6: Starting Bhukti & Remaining */}
            <div className="p-3 rounded-xl bg-white border border-[#D9DEE7] space-y-1 shadow-2xs">
              <div className="text-[11px] font-semibold text-[#8190A6]">
                {language === "ta" ? "பிறப்பில் நடப்பு புக்தி இருப்பு" : "Starting Bhukti & Balance at Birth"}
              </div>
              <div className="font-bold text-sm text-[#183047]">
                {birthBalance.starting_bhukti_lord
                  ? getLordName(birthBalance.starting_bhukti_lord, language)
                  : "—"}
              </div>
              <div className="text-[10px] text-[#52667E]">
                {birthBalance.starting_bhukti_remaining
                  ? `${birthBalance.starting_bhukti_remaining.formatted} (${birthBalance.starting_bhukti_remaining.total_days.toFixed(1)}d)`
                  : "—"}
              </div>
            </div>

            {/* Card 7: Next Dasa Transition Date */}
            <div className="p-3 rounded-xl bg-white border border-[#D9DEE7] space-y-1 shadow-2xs sm:col-span-2 lg:col-span-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <div className="text-[11px] font-bold text-[#153F6B]">
                    {language === "ta"
                      ? "அடுத்த மகாதசை துவங்கும் தேதி (Next Dasa Transition Date):"
                      : "Next Dasa Transition Date:"}
                  </div>
                  <div className="text-xs text-[#52667E]">
                    {language === "ta"
                      ? "பிறப்பு தசா இருப்பின்படி முதல் தசை நிறைவுறும் சரியான நாள்"
                      : "Exact date calculated from birth balance when opening Mahadasha transitions to subsequent Dasa"}
                  </div>
                </div>
                <div className="font-mono font-bold text-sm text-[#153F6B] bg-[#EBF2FE] px-3 py-1.5 rounded-lg border border-[#BFDBFE] self-start sm:self-auto">
                  {birthBalance.next_dasa_transition_date}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* 2. Dasa-Bhukti Schedule Header & Quick Controls */}
      {/* ========================================================================= */}
      <div className="bg-white rounded-2xl border border-[#D9DEE7] p-4 sm:p-5 shadow-xs space-y-3">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          {/* Left: Active Period Summary */}
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-[#153F6B]" />
              <h3 className="font-bold text-sm sm:text-base text-[#183047]">
                {language === "ta"
                  ? "முழு 5-அடுக்கு விம்சோத்தரி தசா-புக்தி அட்டவணை"
                  : "Complete 5-Level Vimshottari Dasa–Bhukti Table"}
              </h3>
            </div>
            {activeHierarchy?.mahadasha && (
              <div className="text-xs text-[#52667E] flex items-center gap-2 flex-wrap">
                <span>
                  {language === "ta" ? "நடப்பு தசா:" : "Active Dasa:"}{" "}
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
                {activeHierarchy.pratyantardasha && (
                  <span>
                    / அந்தரம்:{" "}
                    <strong className="text-emerald-700">
                      {getLordName(activeHierarchy.pratyantardasha.lord, language)}
                    </strong>
                  </span>
                )}
                {selectedDateAge && <span>• {language === "ta" ? "வயது:" : "Age:"} {selectedDateAge}</span>}
              </div>
            )}
          </div>

          {/* Right: Expand / Collapse Actions & Date Picker */}
          <div className="flex items-center gap-1.5 flex-wrap text-xs">
            {/* Target Date Picker */}
            <div className="flex items-center gap-1 bg-[#F2F3F5] px-2 py-1 rounded-lg border border-[#D9DEE7]">
              <Calendar className="w-3.5 h-3.5 text-[#8190A6]" />
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="bg-transparent text-xs text-[#183047] font-semibold outline-none cursor-pointer"
                title={language === "ta" ? "தேதி தேர்வு செய்க" : "Select target date"}
              />
            </div>

            <button
              type="button"
              onClick={expandActivePath}
              className="px-2.5 py-1 rounded-lg border border-[#B4872B] bg-[#FAF2DE] text-[#8C6D23] font-bold inline-flex items-center gap-1 transition-colors cursor-pointer hover:bg-[#F2E5C5]"
            >
              <Sparkles className="w-3 h-3 text-[#B4872B]" />
              <span>{language === "ta" ? "நடப்பு பாதை" : "Active Path"}</span>
            </button>

            <button
              type="button"
              onClick={expandAllLevel1}
              className="px-2.5 py-1 rounded-lg border border-[#D9DEE7] bg-white hover:bg-[#F2F3F5] text-[#183047] font-medium transition-colors cursor-pointer"
            >
              {language === "ta" ? "மகாதசை" : "Dasa"}
            </button>

            <button
              type="button"
              onClick={expandToLevel2}
              className="px-2.5 py-1 rounded-lg border border-[#D9DEE7] bg-white hover:bg-[#F2F3F5] text-[#183047] font-medium transition-colors cursor-pointer"
            >
              {language === "ta" ? "புக்தி வரை" : "Bhukti"}
            </button>

            <button
              type="button"
              onClick={expandToLevel3}
              className="px-2.5 py-1 rounded-lg border border-[#D9DEE7] bg-white hover:bg-[#F2F3F5] text-[#183047] font-medium transition-colors cursor-pointer hidden sm:inline-block"
            >
              {language === "ta" ? "அந்தரம் வரை" : "Antharam"}
            </button>

            <button
              type="button"
              onClick={expandToLevel4}
              className="px-2.5 py-1 rounded-lg border border-[#D9DEE7] bg-white hover:bg-[#F2F3F5] text-[#183047] font-medium transition-colors cursor-pointer hidden md:inline-block"
            >
              {language === "ta" ? "சூட்சுமம் வரை" : "Sookshamam"}
            </button>

            <button
              type="button"
              onClick={expandAllFiveLevels}
              className="px-2.5 py-1 rounded-lg border border-[#153F6B] bg-[#EBF2FE] text-[#153F6B] font-bold transition-colors cursor-pointer hover:bg-[#DBEAFE]"
            >
              <ChevronsDown className="w-3.5 h-3.5 inline mr-0.5" />
              <span>{language === "ta" ? "அனைத்தும் (5)" : "Expand (5)"}</span>
            </button>

            <button
              type="button"
              onClick={collapseAll}
              className="px-2.5 py-1 rounded-lg border border-[#D9DEE7] bg-white hover:bg-[#F2F3F5] text-[#8190A6] hover:text-[#183047] font-medium transition-colors cursor-pointer"
              title="Collapse all"
            >
              <ChevronsUp className="w-3.5 h-3.5 inline mr-0.5" />
              <span>{language === "ta" ? "சுருக்குக" : "Collapse"}</span>
            </button>

            <button
              type="button"
              onClick={() => setShowLegend(!showLegend)}
              className={`p-1 rounded-lg border transition-colors cursor-pointer ${
                showLegend ? "bg-[#153F6B] text-white border-[#153F6B]" : "bg-white text-[#8190A6] border-[#D9DEE7] hover:text-[#183047]"
              }`}
              title={language === "ta" ? "பயன் தரும் பாவங்கள் விளக்கம்" : "Benefit Bhavas Legend"}
            >
              <Info className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Benefit Bhavas Legend & Guide */}
        {showLegend && (
          <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#CBD5E1] text-xs text-[#334155] space-y-1.5 transition-all">
            <div className="font-bold text-[#153F6B] flex items-center gap-1.5">
              <Info className="w-3.5 h-3.5 text-[#153F6B]" />
              <span>{language === "ta" ? "பயன் தரும் பாவங்கள் (Benefit Bhavas) 4 அடுக்கு வரிசை:" : "Benefit Bhavas Four-Category Logical Order:"}</span>
            </div>
            <div className="font-mono text-[11px] bg-white p-2 rounded-lg border border-[#E2E8F0] space-y-0.5">
              <div>
                <strong>[1] Star-lord house:</strong> நின்ற நட்சத்திர அதிபதி நின்ற பாவம்
              </div>
              <div>
                <strong>[2] Star lord's own house:</strong> நின்ற நட்சத்திர அதிபதியின் சொந்த வீடுகள் (ராசி ஆதிப்பத்தியம்)
              </div>
              <div>
                <strong>[3] Planet's placement house:</strong> தசா/புக்தி/அந்தர அதிபதி நின்ற பாவம்
              </div>
              <div>
                <strong>[4] Planet-owned houses:</strong> தசா/புக்தி/அந்தர அதிபதியின் சொந்த வீடுகள்
              </div>
              <div className="text-[10px] text-[#B4872B] pt-1 italic">
                * ராகு / கேதுவுக்கு சொந்த வீடுகள் கிடையாது என்பதால், 2-வது அல்லது 4-வது அடுக்கு விடுபடும்.
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ========================================================================= */}
      {/* 3. The 5-Level Vimshottari Table with Indentation & Benefit Bhavas */}
      {/* ========================================================================= */}
      <div className="bg-white rounded-2xl border border-[#D9DEE7] shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-[#FAF2DE] text-[#183047] font-bold border-b border-[#D8BD80]">
              <tr>
                <th className="py-2.5 px-3 text-left w-36">
                  {language === "ta" ? "நிலை" : "Level"}
                </th>
                <th className="py-2.5 px-3 text-left">
                  {language === "ta" ? "கிரகம் / அதிபதி" : "Planet"}
                </th>
                <th className="py-2.5 px-3 text-left">
                  {language === "ta" ? "தொடக்க தேதி" : "Start Date"}
                </th>
                <th className="py-2.5 px-3 text-left">
                  {language === "ta" ? "முடிவு தேதி" : "End Date"}
                </th>
                <th className="py-2.5 px-3 text-left">
                  {language === "ta" ? "கால அளவு" : "Duration"}
                </th>
                <th className="py-2.5 px-3 text-left">
                  <div className="flex items-center gap-1">
                    <span>{language === "ta" ? "பயன் தரும் பாவங்கள்" : "Benefit Bhavas"}</span>
                    <span className="text-[10px] text-[#8C6D23] font-normal hidden lg:inline">
                      (SL Occ | SL Own | PL Occ | PL Own)
                    </span>
                  </div>
                </th>
                <th className="py-2.5 px-3 text-right">
                  {language === "ta" ? "நிலை" : "Status"}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E2E8F0]">
              {dasa.dasa_tree.map((node, idx) => (
                <HierarchicalDasaRow
                  key={`node-${idx}`}
                  node={node}
                  rowKey={`node-${idx}`}
                  depth={1}
                  expandedKeys={expandedKeys}
                  onToggleExpand={toggleExpand}
                  targetJd={targetJd}
                  utcOffsetHours={utcOffsetHours}
                  planetContexts={planetContexts}
                  language={language}
                  birthDate={resolvedBirthDate}
                />
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Hierarchical Recursive Row Component for All 5 Levels
// ---------------------------------------------------------------------------

interface HierarchicalDasaRowProps {
  node: DasaPeriodNode;
  rowKey: string;
  depth: number;
  expandedKeys: Record<string, boolean>;
  onToggleExpand: (key: string) => void;
  targetJd: number;
  utcOffsetHours: number;
  planetContexts: Record<string, PlanetContext> | null;
  language: "en" | "ta";
  birthDate?: string;
}

function HierarchicalDasaRow({
  node,
  rowKey,
  depth,
  expandedKeys,
  onToggleExpand,
  targetJd,
  utcOffsetHours,
  planetContexts,
  language,
  birthDate,
}: HierarchicalDasaRowProps) {
  const isExpanded = !!expandedKeys[rowKey];

  const cfg = getLevelConfig(node.level);
  const depthLevel = cfg.levelNumber;
  const canHaveChildren = depthLevel < 5;

  // Resolve children: use pre-existing sub_periods or generate dynamically with canonical Vimshottari math
  const subPeriods = useMemo(() => {
    if (node.sub_periods && node.sub_periods.length > 0) {
      return node.sub_periods;
    }
    if (canHaveChildren) {
      return generateChildSubPeriods(node, utcOffsetHours, birthDate);
    }
    return [];
  }, [node, canHaveChildren, utcOffsetHours, birthDate]);

  const hasChildren = subPeriods.length > 0;

  const isSubDaily = depth >= 4;

  const sDateStr = formatDateStr(node.start_date_iso, node.start_jd, utcOffsetHours, isSubDaily);
  const eDateStr = formatDateStr(node.end_date_iso, node.end_jd, utcOffsetHours, isSubDaily);
  const durationStr = formatDurationShort(node);

  // Active status detection
  const isCurrentlyActive = targetJd >= node.start_jd && targetJd < node.end_jd;
  const isAtBirth = Boolean(node.is_active_at_birth);
  const isCompleted = targetJd >= node.end_jd;

  // Benefit Bhavas resolution
  const { starLordName, benefitBhavas } = useMemo(() => {
    if (planetContexts && node.lord) {
      const res = calculateBenefitBhavas(node.lord, planetContexts);
      return {
        starLordName: res.starLord,
        benefitBhavas: res.formatted,
      };
    }
    return {
      starLordName: node.star_lord || node.lord,
      benefitBhavas: node.benefit_bhavas || "—",
    };
  }, [node.lord, node.star_lord, node.benefit_bhavas, planetContexts]);

  // Planet display label with star lord in parentheses
  const planetLabel = useMemo(() => {
    const lName = getLordName(node.lord, language);
    const sName = getLordName(starLordName, language);
    if (language === "ta") {
      const lShort = getGrahaShort(node.lord, "ta");
      const sShort = getGrahaShort(starLordName, "ta");
      return `${lName} (${sShort})`;
    }
    return `${node.lord} (${starLordName?.slice(0, 3) || "Star"})`;
  }, [node.lord, starLordName, language]);

  return (
    <>
      <tr
        onClick={() => hasChildren && onToggleExpand(rowKey)}
        className={`transition-colors text-xs select-none ${
          hasChildren ? "cursor-pointer" : ""
        } ${
          isCurrentlyActive
            ? "bg-[#FAF2DE]/70 font-bold border-l-4 border-l-[#B4872B]"
            : isAtBirth
            ? "bg-[#EBF2FE]/40"
            : depth % 2 === 0
            ? "bg-[#F8FAFC]/50 hover:bg-[#F2F3F5]"
            : "bg-white hover:bg-[#F2F3F5]"
        }`}
      >
        {/* Col 1: Level Badge + Indentation */}
        <td className="py-2 px-3 whitespace-nowrap">
          <div className={`flex items-center gap-1.5 ${cfg.rowIndent}`}>
            {hasChildren ? (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onToggleExpand(rowKey);
                }}
                className="w-4 h-4 rounded flex items-center justify-center border border-slate-300 bg-white hover:bg-slate-100 text-slate-700 cursor-pointer shadow-2xs"
              >
                {isExpanded ? <Minus className="w-2.5 h-2.5" /> : <Plus className="w-2.5 h-2.5" />}
              </button>
            ) : (
              <span className="w-4 inline-block" />
            )}
            <span
              className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full border ${cfg.badgeColor}`}
            >
              {language === "ta" ? cfg.badgeLabelTamil : cfg.badgeLabel}
            </span>
          </div>
        </td>

        {/* Col 2: Planet Name + Star Lord */}
        <td className="py-2 px-3 font-semibold text-[#183047] whitespace-nowrap">
          <div className="flex items-center gap-1.5">
            <span>{planetLabel}</span>
            {isCurrentlyActive && (
              <span className="w-2 h-2 rounded-full bg-[#B4872B] inline-block shrink-0 animate-pulse" />
            )}
          </div>
        </td>

        {/* Col 3: Start Date */}
        <td className="py-2 px-3 font-mono text-[11px] text-[#52667E] whitespace-nowrap">
          {sDateStr}
        </td>

        {/* Col 4: End Date */}
        <td className="py-2 px-3 font-mono text-[11px] text-[#52667E] whitespace-nowrap">
          {eDateStr}
        </td>

        {/* Col 5: Duration */}
        <td className="py-2 px-3 font-mono text-[11px] font-semibold text-[#183047] whitespace-nowrap">
          {durationStr}
        </td>

        {/* Col 6: Benefit Bhavas */}
        <td className="py-2 px-3 font-mono text-[11px] font-bold text-[#153F6B] whitespace-nowrap">
          <span
            className="px-2 py-0.5 rounded bg-slate-100/80 border border-slate-200 inline-block hover:bg-amber-50 hover:border-amber-300 transition-colors"
            title={`Star Lord Occupied | Star Lord Owned | Planet Occupied | Planet Owned: ${benefitBhavas}`}
          >
            {benefitBhavas}
          </span>
        </td>

        {/* Col 7: Status */}
        <td className="py-2 px-3 text-right whitespace-nowrap">
          {isCurrentlyActive ? (
            <span className="px-2 py-0.5 rounded-full bg-[#B4872B] text-white text-[10px] font-bold">
              {language === "ta" ? "நடப்பு" : "Active"}
            </span>
          ) : isAtBirth ? (
            <span className="px-2 py-0.5 rounded-full bg-[#153F6B] text-white text-[10px] font-semibold">
              {language === "ta" ? "பிறப்பில்" : "At Birth"}
            </span>
          ) : isCompleted ? (
            <span className="text-[10px] text-[#8190A6]">
              {language === "ta" ? "முடிந்தது" : "Past"}
            </span>
          ) : (
            <span className="text-[10px] text-[#52667E]">
              {language === "ta" ? "வருவது" : "Upcoming"}
            </span>
          )}
        </td>
      </tr>

      {/* Recursive Children Rows */}
      {isExpanded &&
        hasChildren &&
        subPeriods.map((sub, sIdx) => (
          <HierarchicalDasaRow
            key={`${rowKey}-${sIdx}`}
            node={sub}
            rowKey={`${rowKey}-${sIdx}`}
            depth={depth + 1}
            expandedKeys={expandedKeys}
            onToggleExpand={onToggleExpand}
            targetJd={targetJd}
            utcOffsetHours={utcOffsetHours}
            planetContexts={planetContexts}
            language={language}
            birthDate={birthDate}
          />
        ))}
    </>
  );
}
