"use client";

import React, { useState, useMemo, useEffect } from "react";
import {
  DasaResponse,
  DasaPeriodNode,
  HoroscopeResponse,
  KpResponse,
  KpEventAnalysisResponse,
  BirthDasaBalance,
  DasaPeriodAgeDict,
} from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { getLordName, getGrahaShort } from "@/lib/translations";
import { analyzeKpEvents } from "@/lib/api";
import {
  jdToCalendarDateTime,
  calculateCalendarAge,
  formatCalendarAge,
  findActiveHierarchy,
  generateChildSubPeriods,
  VIMSHOTTARI_YEARS,
} from "@/lib/dasa-helpers";
import {
  buildPlanetContexts,
  calculateBenefitBhavas,
  PlanetContext,
} from "@/lib/benefit-bhavas";
import {
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

function formatDateStr(
  isoStr?: string,
  jd?: number,
  offsetHours: number = 0
): string {
  if (isoStr) {
    const parts = isoStr.split("T");
    if (parts[0]) {
      const [y, m, d] = parts[0].split("-");
      return `${d}/${m}/${y}`;
    }
  }
  if (jd) {
    const dt = jdToCalendarDateTime(jd, offsetHours);
    if (dt) {
      const d = String(dt.day).padStart(2, "0");
      const m = String(dt.month).padStart(2, "0");
      return `${d}/${m}/${dt.year}`;
    }
  }
  return "—";
}

/**
 * Format short planetary abbreviation matching the reference screenshot.
 * In Tamil:
 * Sun -> சூ, Moon -> சந், Mars -> செ, Mercury -> பு, Jupiter -> குரு,
 * Venus -> சுக், Saturn -> சனி, Rahu -> ராகு, Ketu -> கேது
 */
function getPeriodPlanetShort(lordEn: string, lang: "en" | "ta"): string {
  const norm = lordEn.trim().toLowerCase();
  if (lang === "ta") {
    switch (norm) {
      case "sun":
      case "surya":
        return "சூ";
      case "moon":
      case "chandra":
        return "சந்";
      case "mars":
      case "mangal":
      case "mangala":
      case "sevvai":
        return "செ";
      case "mercury":
      case "budh":
      case "budha":
        return "பு";
      case "jupiter":
      case "guru":
        return "குரு";
      case "venus":
      case "sukra":
      case "shukra":
        return "சுக்";
      case "saturn":
      case "shani":
        return "சனி";
      case "rahu":
        return "ராகு";
      case "ketu":
        return "கேது";
      default:
        return getLordName(lordEn, lang);
    }
  }
  switch (norm) {
    case "sun":
      return "Sun";
    case "moon":
      return "Moo";
    case "mars":
      return "Mar";
    case "mercury":
      return "Mer";
    case "jupiter":
      return "Jup";
    case "venus":
      return "Ven";
    case "saturn":
      return "Sat";
    case "rahu":
      return "Rah";
    case "ketu":
      return "Ket";
    default:
      return lordEn.slice(0, 3);
  }
}

/**
 * Format Star Lord short label in parentheses matching the screenshot.
 * e.g. (சு) for Venus, (சூ) for Sun, (ராகு) for Rahu, etc.
 */
function getStarLordShort(starLordEn: string, lang: "en" | "ta", parentLordEn?: string): string {
  const norm = starLordEn.trim().toLowerCase();
  if (lang === "ta") {
    switch (norm) {
      case "sun":
      case "surya":
        return "சூ";
      case "moon":
      case "chandra":
        return "சந்";
      case "mars":
      case "mangal":
      case "mangala":
      case "sevvai":
        return "செ";
      case "mercury":
      case "budh":
      case "budha":
        return "பு";
      case "jupiter":
      case "guru":
        return "குரு";
      case "venus":
      case "sukra":
      case "shukra": {
        // In the reference screenshot:
        // When parent is Sun "சூ (சு)" or Mercury "பு (சு)", Venus star lord is shortened to "சு".
        // When parent is Rahu/Saturn "சனி (சுக்)", it shows "சுக்".
        const pNorm = (parentLordEn || "").trim().toLowerCase();
        if (pNorm === "sun" || pNorm === "surya" || pNorm === "mercury" || pNorm === "budh") {
          return "சு";
        }
        return "சுக்";
      }
      case "saturn":
      case "shani":
        return "சனி";
      case "rahu":
        return "ராகு";
      case "ketu":
        return "கேது";
      default:
        return getGrahaShort(starLordEn, lang);
    }
  }
  switch (norm) {
    case "sun":
      return "Sun";
    case "moon":
      return "Moo";
    case "mars":
      return "Mar";
    case "mercury":
      return "Mer";
    case "jupiter":
      return "Jup";
    case "venus":
      return "Ven";
    case "saturn":
      return "Sat";
    case "rahu":
      return "Rah";
    case "ketu":
      return "Ket";
    default:
      return starLordEn.slice(0, 3);
  }
}

function calculateVedicDifference(
  sY: number,
  sM: number,
  sD: number,
  eY: number,
  eM: number,
  eD: number
): { years: number; months: number; days: number } | null {
  if (eY < sY || (eY === sY && eM < sM) || (eY === sY && eM === sM && eD < sD)) {
    return null;
  }
  let d = eD - sD;
  let m = eM - sM;
  let y = eY - sY;

  if (d < 0) {
    d += 30; // standard 30-day Vedic month
    m -= 1;
  }
  if (m < 0) {
    m += 12;
    y -= 1;
  }
  return { years: y, months: m, days: d };
}

/**
 * Format Duration as Years.Months.Days (Y.M.D) matching the reference screenshot.
 * e.g. 0.6.18, 2.10.0, 0.10.6, 1.5.0, 0.4.27, 1.2.0, 0.2.0, 0.0.18, etc.
 */
function formatYmdDuration(
  node: DasaPeriodNode,
  parentFullYears?: number
): string {
  // If active at birth and dates exist, use 30-day Vedic calendar difference
  if (node.is_active_at_birth && node.start_date_iso && node.end_date_iso) {
    const sParts = node.start_date_iso.split("T")[0].split("-").map(Number);
    const eParts = node.end_date_iso.split("T")[0].split("-").map(Number);
    if (sParts.length === 3 && eParts.length === 3) {
      const vDiff = calculateVedicDifference(
        sParts[0],
        sParts[1],
        sParts[2],
        eParts[0],
        eParts[1],
        eParts[2]
      );
      if (vDiff) {
        return `${vDiff.years}.${vDiff.months}.${vDiff.days}`;
      }
    }
  }

  // Canonical Vimshottari arithmetic: (parentYears * lordYears) / 120
  let yearsFloat: number | null = null;
  if (parentFullYears && VIMSHOTTARI_YEARS[node.lord]) {
    yearsFloat = (parentFullYears * VIMSHOTTARI_YEARS[node.lord]) / 120.0;
  } else if (node.duration_years && node.duration_years > 0) {
    yearsFloat = node.duration_years;
  } else if (node.duration_days && node.duration_days > 0) {
    yearsFloat = node.duration_days / 365.25;
  }

  if (yearsFloat === null || isNaN(yearsFloat)) {
    return "0.0.0";
  }

  let y = Math.floor(yearsFloat + 1e-6);
  let remMonths = (yearsFloat - y) * 12;
  let m = Math.floor(remMonths + 1e-6);
  let remDays = (remMonths - m) * 30;
  let d = Math.round(remDays);
  if (d >= 30) {
    m += 1;
    d = 0;
  }
  if (m >= 12) {
    y += 1;
    m = 0;
  }
  return `${y}.${m}.${d}`;
}

/**
 * Format native's calendar age at the period's end date:
 * e.g. "0Y 6M", "3Y 4M", "14Y 1M", "46Y 1M" matching the screenshot.
 */
function getPeriodAgeStr(
  endIso?: string,
  endJd?: number,
  birthDate?: string,
  utcOffsetHours: number = 0
): string | null {
  if (!birthDate) return null;
  const [bY, bM, bD] = birthDate.split("-").map(Number);
  if (!bY || !bM || !bD) return null;

  let tY: number | undefined;
  let tM: number | undefined;
  let tD: number | undefined;

  if (endIso) {
    const parts = endIso.split("T")[0].split("-").map(Number);
    if (parts.length === 3 && parts[0] && parts[1] && parts[2]) {
      tY = parts[0];
      tM = parts[1];
      tD = parts[2];
    }
  }

  if (tY === undefined && endJd) {
    const dt = jdToCalendarDateTime(endJd, utcOffsetHours);
    if (dt) {
      tY = dt.year;
      tM = dt.month;
      tD = dt.day;
    }
  }

  if (tY === undefined || tM === undefined || tD === undefined) return null;

  const age = calculateCalendarAge(bY, bM, bD, tY, tM, tD);
  if (!age) return null;

  return `${age.years}Y ${age.months}M`;
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

  // State 1: Expand/collapse state for each Mahadasha chart card
  // By default, all Mahadasha cards are open so charts are shown side by side
  const [expandedMahaKeys, setExpandedMahaKeys] = useState<Record<number, boolean>>(() => {
    const map: Record<number, boolean> = {};
    if (dasa?.dasa_tree) {
      dasa.dasa_tree.forEach((_, idx) => {
        map[idx] = true;
      });
    }
    return map;
  });

  // State 2: Expand/collapse state for Bhukti and deeper rows
  // By default, expand the currently active Bhukti row to reveal nested Pratyantardasa rows (as in screenshot)
  const [expandedRowKeys, setExpandedRowKeys] = useState<Record<string, boolean>>(() => {
    const map: Record<string, boolean> = {};
    if (dasa?.dasa_tree) {
      const tJd = defaultTargetDate ? dateToJd(defaultTargetDate) : 0;
      dasa.dasa_tree.forEach((m, mIdx) => {
        if (tJd >= m.start_jd && tJd < m.end_jd) {
          const bList =
            m.sub_periods && m.sub_periods.length > 0
              ? m.sub_periods
              : generateChildSubPeriods(m, utcOffsetHours, resolvedBirthDate);
          bList.forEach((b, bIdx) => {
            if (tJd >= b.start_jd && tJd < b.end_jd) {
              map[`${mIdx}-${bIdx}`] = true;
            }
          });
        }
      });
    }
    return map;
  });

  const toggleMaha = (idx: number) => {
    setExpandedMahaKeys((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  const toggleRow = (key: string) => {
    setExpandedRowKeys((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const expandAllMahadashas = () => {
    if (!dasa?.dasa_tree) return;
    const map: Record<number, boolean> = {};
    dasa.dasa_tree.forEach((_, idx) => {
      map[idx] = true;
    });
    setExpandedMahaKeys(map);
    setExpandedRowKeys({});
  };

  const expandToAntharam = () => {
    if (!dasa?.dasa_tree) return;
    const mahaMap: Record<number, boolean> = {};
    const rowMap: Record<string, boolean> = {};
    dasa.dasa_tree.forEach((m, mIdx) => {
      mahaMap[mIdx] = true;
      const bChildren =
        m.sub_periods && m.sub_periods.length > 0
          ? m.sub_periods
          : generateChildSubPeriods(m, utcOffsetHours, resolvedBirthDate);
      bChildren.forEach((_, bIdx) => {
        rowMap[`${mIdx}-${bIdx}`] = true;
      });
    });
    setExpandedMahaKeys(mahaMap);
    setExpandedRowKeys(rowMap);
  };

  const expandAllFiveLevels = () => {
    if (!dasa?.dasa_tree) return;
    const mahaMap: Record<number, boolean> = {};
    const rowMap: Record<string, boolean> = {};

    const recurse = (nodes: DasaPeriodNode[], prefix: string, currDepth: number) => {
      nodes.forEach((n, idx) => {
        const k = prefix ? `${prefix}-${idx}` : `${idx}`;
        rowMap[k] = true;
        if (currDepth < 5) {
          const ch =
            n.sub_periods && n.sub_periods.length > 0
              ? n.sub_periods
              : generateChildSubPeriods(n, utcOffsetHours, resolvedBirthDate);
          if (ch.length > 0) {
            recurse(ch, k, currDepth + 1);
          }
        }
      });
    };

    dasa.dasa_tree.forEach((m, mIdx) => {
      mahaMap[mIdx] = true;
      const bList =
        m.sub_periods && m.sub_periods.length > 0
          ? m.sub_periods
          : generateChildSubPeriods(m, utcOffsetHours, resolvedBirthDate);
      recurse(bList, `${mIdx}`, 2);
    });

    setExpandedMahaKeys(mahaMap);
    setExpandedRowKeys(rowMap);
  };

  const collapseAll = () => {
    setExpandedRowKeys({});
  };

  const expandActivePath = () => {
    if (!dasa?.dasa_tree) return;
    const mahaMap: Record<number, boolean> = {};
    const rowMap: Record<string, boolean> = {};

    dasa.dasa_tree.forEach((m, mIdx) => {
      if (targetJd >= m.start_jd && targetJd < m.end_jd) {
        mahaMap[mIdx] = true;
        const recurseActive = (
          nodes: DasaPeriodNode[],
          prefix: string,
          currDepth: number
        ) => {
          nodes.forEach((n, idx) => {
            const k = `${prefix}-${idx}`;
            if (targetJd >= n.start_jd && targetJd < n.end_jd) {
              rowMap[k] = true;
              if (currDepth < 5) {
                const ch =
                  n.sub_periods && n.sub_periods.length > 0
                    ? n.sub_periods
                    : generateChildSubPeriods(n, utcOffsetHours, resolvedBirthDate);
                if (ch.length > 0) {
                  recurseActive(ch, k, currDepth + 1);
                }
              }
            }
          });
        };
        const bList =
          m.sub_periods && m.sub_periods.length > 0
            ? m.sub_periods
            : generateChildSubPeriods(m, utcOffsetHours, resolvedBirthDate);
        recurseActive(bList, `${mIdx}`, 2);
      }
    });

    setExpandedMahaKeys((prev) => ({ ...prev, ...mahaMap }));
    setExpandedRowKeys((prev) => ({ ...prev, ...rowMap }));
  };

  // Derive or extract authoritative Birth Dasa Balance
  const birthBalance = useMemo(() => {
    if (dasa?.birth_dasa_balance) {
      return dasa.birth_dasa_balance;
    }
    if (!dasa?.dasa_tree || dasa.dasa_tree.length === 0) return null;
    const firstMaha = dasa.dasa_tree[0];
    const firstBhukti =
      firstMaha.sub_periods && firstMaha.sub_periods.length > 0
        ? firstMaha.sub_periods[0]
        : null;

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
            formatted: formatYmdDuration(firstBhukti),
          }
        : undefined,
      next_dasa_transition_date: formatDateStr(
        firstMaha.end_date_iso,
        firstMaha.end_jd,
        utcOffsetHours
      ),
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
      {/* 1. Birth-Time Dasa Balance (தசா இருப்பு) Section */}
      {/* ========================================================================= */}
      {birthBalance && (
        <div className="rounded-2xl border-2 border-[#D8BD80] bg-[#FAF6EC] shadow-sm overflow-hidden">
          {/* Section Header */}
          <div className="px-5 py-3.5 bg-[#FAF2DE] border-b border-[#D8BD80] flex flex-col sm:flex-row sm:items-center justify-between gap-2">
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

          {/* Section Grid: 7 Essential Facts */}
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
                {language === "ta" ? "நிரயண முறை (Sidereal)" : "Sidereal Zodiac"}
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
                <strong>{birthBalance.mahadasha_full_duration.formatted}</strong>
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
                {birthBalance.elapsed_duration.total_days.toFixed(1)} {language === "ta" ? "நாட்கள்" : "Days"}
              </div>
            </div>

            {/* Card 5: Remaining Dasa Balance at Birth */}
            <div className="p-3 rounded-xl bg-[#FAF2DE] border border-[#D8BD80] space-y-1 shadow-2xs sm:col-span-2 lg:col-span-1">
              <div className="text-[11px] font-bold text-[#8C6D23] flex items-center justify-between">
                <span>{language === "ta" ? "பிறப்பில் தசா இருப்பு (மீதம்)" : "Remaining Dasa Balance at Birth"}</span>
                <CheckCircle2 className="w-4 h-4 text-[#B4872B]" />
              </div>
              <div className="font-bold text-base text-[#153F6B]">
                {birthBalance.remaining_balance.formatted}
              </div>
              <div className="text-[10px] font-mono text-[#8C6D23]">
                {birthBalance.remaining_balance.total_days.toFixed(1)} {language === "ta" ? "நாட்கள்" : "Days"}
              </div>
            </div>

            {/* Card 6: Starting Bhukti */}
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
                  ? "விம்சோத்தரி தசா-புக்தி அட்டவணை"
                  : "Vimshottari Dasa–Bhukti Schedule"}
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
                {selectedDateAge && (
                  <span>• {language === "ta" ? "வயது:" : "Age:"} {selectedDateAge}</span>
                )}
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
              onClick={expandAllMahadashas}
              className="px-2.5 py-1 rounded-lg border border-[#D9DEE7] bg-white hover:bg-[#F2F3F5] text-[#183047] font-medium transition-colors cursor-pointer"
            >
              {language === "ta" ? "மகாதசை" : "Dasa"}
            </button>

            <button
              type="button"
              onClick={expandToAntharam}
              className="px-2.5 py-1 rounded-lg border border-[#D9DEE7] bg-white hover:bg-[#F2F3F5] text-[#183047] font-medium transition-colors cursor-pointer"
            >
              {language === "ta" ? "அந்தரம் வரை" : "Antharam"}
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
                showLegend
                  ? "bg-[#153F6B] text-white border-[#153F6B]"
                  : "bg-white text-[#8190A6] border-[#D9DEE7] hover:text-[#183047]"
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
              <span>
                {language === "ta"
                  ? "பயன் தரும் பாவங்கள் (Benefit Bhavas) 4 அடுக்கு வரிசை:"
                  : "Benefit Bhavas Four-Category Logical Order:"}
              </span>
            </div>
            <div className="font-mono text-[11px] bg-white p-2 rounded-lg border border-[#E2E8F0] space-y-0.5">
              <div>
                <strong>[1] Star-lord house:</strong> நின்ற நட்சத்திர அதிபதி நின்ற பாவம்
              </div>
              <div>
                <strong>[2] Star lord's own house:</strong> நின்ற நட்சத்திர அதிபதியின் சொந்த வீடுகள்
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
      {/* 3. Side-by-Side Dasa Charts Grid (Reference Screenshot Layout) */}
      {/* ========================================================================= */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-5 items-start">
        {dasa.dasa_tree.map((mahaNode, mahaIdx) => (
          <MahadashaCard
            key={`maha-${mahaIdx}`}
            mahaNode={mahaNode}
            mahaIdx={mahaIdx}
            isExpanded={Boolean(expandedMahaKeys[mahaIdx])}
            onToggleMaha={toggleMaha}
            expandedRowKeys={expandedRowKeys}
            onToggleRow={toggleRow}
            targetJd={targetJd}
            utcOffsetHours={utcOffsetHours}
            planetContexts={planetContexts}
            language={language}
            birthDate={resolvedBirthDate}
          />
        ))}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Mahadasha Card Component (Independent Responsive Chart Box)
// ---------------------------------------------------------------------------

interface MahadashaCardProps {
  mahaNode: DasaPeriodNode;
  mahaIdx: number;
  isExpanded: boolean;
  onToggleMaha: (idx: number) => void;
  expandedRowKeys: Record<string, boolean>;
  onToggleRow: (key: string) => void;
  targetJd: number;
  utcOffsetHours: number;
  planetContexts: Record<string, PlanetContext> | null;
  language: "en" | "ta";
  birthDate?: string;
}

function MahadashaCard({
  mahaNode,
  mahaIdx,
  isExpanded,
  onToggleMaha,
  expandedRowKeys,
  onToggleRow,
  targetJd,
  utcOffsetHours,
  planetContexts,
  language,
  birthDate,
}: MahadashaCardProps) {
  // Check if this Mahadasha is the currently active one
  const isMahaActive = targetJd >= mahaNode.start_jd && targetJd < mahaNode.end_jd;

  // Resolve star lord for the Mahadasha
  const mahaStarLord = useMemo(() => {
    if (planetContexts && mahaNode.lord) {
      return calculateBenefitBhavas(mahaNode.lord, planetContexts).starLord;
    }
    return mahaNode.star_lord || mahaNode.lord;
  }, [mahaNode.lord, mahaNode.star_lord, planetContexts]);

  const pShort = getPeriodPlanetShort(mahaNode.lord, language);
  const sShort = getStarLordShort(mahaStarLord, language, mahaNode.lord);

  const startDateStr = formatDateStr(mahaNode.start_date_iso, mahaNode.start_jd, utcOffsetHours);
  const endDateStr = formatDateStr(mahaNode.end_date_iso, mahaNode.end_jd, utcOffsetHours);

  // Subperiods (Bhuktis)
  const bhuktis = useMemo(() => {
    if (mahaNode.sub_periods && mahaNode.sub_periods.length > 0) {
      return mahaNode.sub_periods;
    }
    return generateChildSubPeriods(mahaNode, utcOffsetHours, birthDate);
  }, [mahaNode, utcOffsetHours, birthDate]);

  const mahaFullYears = VIMSHOTTARI_YEARS[mahaNode.lord] || Math.round(mahaNode.duration_years) || 120;

  return (
    <div
      className={`bg-white rounded-xl border overflow-hidden shadow-xs transition-shadow hover:shadow-md ${
        isMahaActive
          ? "border-[#103A60] ring-1 ring-[#103A60]/30"
          : "border-[#D9DEE7]"
      }`}
    >
      {/* Mahadasha Header Bar */}
      <div
        onClick={() => onToggleMaha(mahaIdx)}
        className={`px-3.5 py-2.5 flex items-center justify-between cursor-pointer select-none transition-colors ${
          isMahaActive
            ? "bg-[#103A60] text-white"
            : "bg-[#EEF2F6] hover:bg-[#E5EBF2] text-[#183047]"
        }`}
      >
        {/* Left: Circle button with minus/plus and Planet + Star Lord */}
        <div className="flex items-center gap-2.5">
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onToggleMaha(mahaIdx);
            }}
            aria-label={isExpanded ? "Collapse Mahadasha" : "Expand Mahadasha"}
            className={`w-4.5 h-4.5 rounded-full flex items-center justify-center shrink-0 cursor-pointer transition-colors ${
              isMahaActive
                ? "bg-white/20 text-white hover:bg-white/30"
                : "bg-[#CBD5E1] text-[#334155] hover:bg-[#94A3B8] hover:text-white"
            }`}
          >
            {isExpanded ? (
              <Minus className="w-2.5 h-2.5 stroke-[3]" />
            ) : (
              <Plus className="w-2.5 h-2.5 stroke-[3]" />
            )}
          </button>

          <div className="font-bold text-xs sm:text-sm flex items-center gap-1">
            <span>{pShort}</span>
            <span
              className={`font-semibold ${
                isMahaActive ? "text-sky-300" : "text-[#0284C7]"
              }`}
            >
              ({sShort})
            </span>
          </div>
        </div>

        {/* Right: Date Range */}
        <div
          className={`font-mono text-[11px] sm:text-xs font-medium tracking-tight ${
            isMahaActive ? "text-sky-100" : "text-[#52667E]"
          }`}
        >
          {startDateStr} - {endDateStr}
        </div>
      </div>

      {/* Table of Bhuktis (Nested Hierarchy) */}
      {isExpanded && (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-[#FAF2DE] text-[#183047] font-bold border-b border-[#D8BD80]/80">
              <tr>
                <th className="py-2 px-2.5 text-left font-bold w-[28%] sm:w-[26%]">
                  Bukthi
                </th>
                <th className="py-2 px-2 text-left font-bold w-[18%] sm:w-[17%]">
                  From
                </th>
                <th className="py-2 px-2 text-left font-bold w-[26%] sm:w-[27%]">
                  To
                </th>
                <th className="py-2 px-2 text-left font-bold w-[14%] sm:w-[13%]">
                  Duration
                </th>
                <th className="py-2 px-2 text-left font-bold w-[14%] sm:w-[17%]">
                  Benefit Bhavas
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E2E8F0]">
              {bhuktis.map((bhuktiNode, bIdx) => {
                const rowKey = `${mahaIdx}-${bIdx}`;
                return (
                  <DasaTableRow
                    key={rowKey}
                    node={bhuktiNode}
                    rowKey={rowKey}
                    depth={2}
                    expandedRowKeys={expandedRowKeys}
                    onToggleRow={onToggleRow}
                    targetJd={targetJd}
                    utcOffsetHours={utcOffsetHours}
                    planetContexts={planetContexts}
                    language={language}
                    birthDate={birthDate}
                    parentFullYears={mahaFullYears}
                  />
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
// Dasa Table Row Component (Recursive for Nested Sub-Periods)
// ---------------------------------------------------------------------------

interface DasaTableRowProps {
  node: DasaPeriodNode;
  rowKey: string;
  depth: number;
  expandedRowKeys: Record<string, boolean>;
  onToggleRow: (key: string) => void;
  targetJd: number;
  utcOffsetHours: number;
  planetContexts: Record<string, PlanetContext> | null;
  language: "en" | "ta";
  birthDate?: string;
  parentFullYears?: number;
}

function DasaTableRow({
  node,
  rowKey,
  depth,
  expandedRowKeys,
  onToggleRow,
  targetJd,
  utcOffsetHours,
  planetContexts,
  language,
  birthDate,
  parentFullYears,
}: DasaTableRowProps) {
  const isExpanded = Boolean(expandedRowKeys[rowKey]);

  // Active status detection
  const isCurrentlyActive = targetJd >= node.start_jd && targetJd < node.end_jd;

  // Resolve star lord and Benefit Bhavas
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

  const pShort = getPeriodPlanetShort(node.lord, language);
  const sShort = getStarLordShort(starLordName, language, node.lord);

  const sDateStr = formatDateStr(node.start_date_iso, node.start_jd, utcOffsetHours);
  const eDateStr = formatDateStr(node.end_date_iso, node.end_jd, utcOffsetHours);

  // Age string in the "To" column (e.g. "46Y 1M")
  const ageStr = useMemo(() => {
    return getPeriodAgeStr(node.end_date_iso, node.end_jd, birthDate, utcOffsetHours);
  }, [node.end_date_iso, node.end_jd, birthDate, utcOffsetHours]);

  // Duration in Y.M.D format matching the screenshot (e.g. 0.4.27, 1.2.0, 0.2.0)
  const durationStr = useMemo(() => {
    return formatYmdDuration(node, parentFullYears);
  }, [node, parentFullYears]);

  // Resolve child sub-periods if depth < 5
  const canHaveChildren = depth < 5;
  const subPeriods = useMemo(() => {
    if (!canHaveChildren) return [];
    if (node.sub_periods && node.sub_periods.length > 0) {
      return node.sub_periods;
    }
    return generateChildSubPeriods(node, utcOffsetHours, birthDate);
  }, [node, canHaveChildren, utcOffsetHours, birthDate]);

  const hasChildren = subPeriods.length > 0;

  // Calculate full theoretical duration in years for child proportion calculations
  const thisNodeFullYears = useMemo(() => {
    if (parentFullYears && VIMSHOTTARI_YEARS[node.lord]) {
      return (parentFullYears * VIMSHOTTARI_YEARS[node.lord]) / 120.0;
    }
    return node.duration_years || (node.duration_days ? node.duration_days / 365.25 : undefined);
  }, [parentFullYears, node.lord, node.duration_years, node.duration_days]);

  // Row styling
  // In the screenshot:
  // Active Bhukti row has a dark slate-grey background (#717A8A / #64748B) with white text.
  // Inactive rows alternate between white and very light grey-blue (#F8FAFC).
  // Child rows have left indentation on the first column.
  const isDepth2 = depth === 2;
  const isHighlightActive = isCurrentlyActive && isDepth2;

  return (
    <>
      <tr
        onClick={() => hasChildren && onToggleRow(rowKey)}
        className={`transition-colors text-xs select-none ${
          hasChildren ? "cursor-pointer" : ""
        } ${
          isHighlightActive
            ? "bg-[#717A8A] text-white font-bold"
            : depth % 2 === 0
            ? "bg-white hover:bg-[#F2F4F8]"
            : "bg-[#F8FAFC] hover:bg-[#F2F4F8]"
        }`}
      >
        {/* Col 1: Bukthi Name + Star Lord + Expand/Collapse Square Button */}
        <td className="py-1.5 px-2.5 whitespace-nowrap">
          <div
            className={`flex items-center gap-1.5 ${
              depth === 3 ? "pl-5 sm:pl-6" : depth === 4 ? "pl-9 sm:pl-10" : depth === 5 ? "pl-12 sm:pl-14" : ""
            }`}
          >
            {hasChildren ? (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onToggleRow(rowKey);
                }}
                aria-label={isExpanded ? "Collapse" : "Expand"}
                className={`w-3.5 h-3.5 sm:w-4 sm:h-4 rounded-xs sm:rounded-sm flex items-center justify-center shrink-0 cursor-pointer shadow-2xs transition-colors ${
                  isHighlightActive
                    ? "bg-[#0F2942] text-white border border-white/30 hover:bg-[#081B2E]"
                    : "bg-[#153F6B] hover:bg-[#0D2F4E] text-white"
                }`}
              >
                {isExpanded ? (
                  <Minus className="w-2.5 h-2.5 stroke-[3]" />
                ) : (
                  <Plus className="w-2.5 h-2.5 stroke-[3]" />
                )}
              </button>
            ) : (
              <span className="w-3.5 sm:w-4 inline-block shrink-0" />
            )}

            <div className="flex items-center gap-1">
              <span
                className={`font-semibold ${
                  isHighlightActive ? "text-white font-bold" : "text-[#183047]"
                }`}
              >
                {pShort}
              </span>
              <span
                className={`text-[11px] font-medium ${
                  isHighlightActive ? "text-sky-200" : "text-[#0284C7]"
                }`}
              >
                ({sShort})
              </span>
            </div>
          </div>
        </td>

        {/* Col 2: From Date */}
        <td
          className={`py-1.5 px-2 font-mono text-[11px] whitespace-nowrap ${
            isHighlightActive ? "text-white" : "text-[#334155]"
          }`}
        >
          {sDateStr}
        </td>

        {/* Col 3: To Date + Age (e.g. 09/04/1994 (14Y 1M)) */}
        <td className="py-1.5 px-2 font-mono text-[11px] whitespace-nowrap">
          <span className={isHighlightActive ? "text-white" : "text-[#334155]"}>
            {eDateStr}
          </span>
          {ageStr && (
            <span
              className={`text-[10px] sm:text-[11px] ml-1 font-medium ${
                isHighlightActive ? "text-amber-200 font-bold" : "text-[#D97706]"
              }`}
            >
              ({ageStr})
            </span>
          )}
        </td>

        {/* Col 4: Duration (e.g. 0.4.27, 1.2.0, 0.2.0) */}
        <td
          className={`py-1.5 px-2 font-mono text-[11px] whitespace-nowrap ${
            isHighlightActive ? "text-white font-bold" : "text-[#183047] font-medium"
          }`}
        >
          {durationStr}
        </td>

        {/* Col 5: Benefit Bhavas (e.g. 7 | 6 | 7 | 3, 8) */}
        <td
          className={`py-1.5 px-2 font-mono text-[11px] whitespace-nowrap ${
            isHighlightActive ? "text-white font-bold" : "text-[#183047] font-semibold"
          }`}
          title={`Benefit Bhavas: ${benefitBhavas}`}
        >
          {benefitBhavas}
        </td>
      </tr>

      {/* Recursive Children (Pratyantardasa / Sookshmadasha / Pranadasha) */}
      {isExpanded &&
        hasChildren &&
        subPeriods.map((subNode, sIdx) => {
          const subKey = `${rowKey}-${sIdx}`;
          return (
            <DasaTableRow
              key={subKey}
              node={subNode}
              rowKey={subKey}
              depth={depth + 1}
              expandedRowKeys={expandedRowKeys}
              onToggleRow={onToggleRow}
              targetJd={targetJd}
              utcOffsetHours={utcOffsetHours}
              planetContexts={planetContexts}
              language={language}
              birthDate={birthDate}
              parentFullYears={thisNodeFullYears}
            />
          );
        })}
    </>
  );
}
