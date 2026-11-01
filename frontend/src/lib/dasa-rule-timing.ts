import { DasaPeriodNode, EvaluatedPredictionRule, HouseInfo } from "@/lib/types";

// Classical Vedic Planet Names & Translations
export const PLANET_DETAILS: Record<string, { en: string; ta: string; color: string }> = {
  Sun: { en: "Sun", ta: "சூரியன்", color: "#E05A1B" },
  Moon: { en: "Moon", ta: "சந்திரன்", color: "#3B82F6" },
  Mars: { en: "Mars", ta: "செவ்வாய்", color: "#DC2626" },
  Mercury: { en: "Mercury", ta: "புதன்", color: "#16A34A" },
  Jupiter: { en: "Jupiter", ta: "குரு", color: "#D97706" },
  Venus: { en: "Venus", ta: "சுக்கிரன்", color: "#9333EA" },
  Saturn: { en: "Saturn", ta: "சனி", color: "#475569" },
  Rahu: { en: "Rahu", ta: "ராகு", color: "#4F46E5" },
  Ketu: { en: "Ketu", ta: "கேது", color: "#78350F" },
};

// Sign Lord Mapping for 12 Signs (1 = Aries .. 12 = Pisces)
export const SIGN_LORDS: Record<number, string> = {
  1: "Mars",
  2: "Venus",
  3: "Mercury",
  4: "Moon",
  5: "Sun",
  6: "Mercury",
  7: "Venus",
  8: "Mars",
  9: "Jupiter",
  10: "Saturn",
  11: "Saturn",
  12: "Jupiter",
};

export interface RuleDasaTimingPeriod {
  maha_en: string;
  maha_ta: string;
  bhukti_en: string;
  bhukti_ta: string;
  start_date: string; // DD/MM/YYYY
  end_date: string;   // DD/MM/YYYY
  start_iso: string;
  end_iso: string;
  status: "active" | "upcoming" | "past";
  is_mahadasha_same: boolean;
}

export interface RuleDasaTimingAnalysis {
  planets: Array<{
    name_en: string;
    name_ta: string;
    role_en: string;
    role_ta: string;
  }>;
  activePeriod: RuleDasaTimingPeriod | null;
  nextUpcomingPeriod: RuleDasaTimingPeriod | null;
  allPeriods: RuleDasaTimingPeriod[];
  summary_en: string;
  summary_ta: string;
}

function formatDateStr(isoStr?: string): string {
  if (!isoStr) return "—";
  const datePart = isoStr.split("T")[0];
  if (!datePart) return "—";
  const parts = datePart.split("-");
  if (parts.length === 3) {
    const [y, m, d] = parts;
    return `${d}/${m}/${y}`;
  }
  return datePart;
}

function getTodayIso(): string {
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, "0");
  const d = String(now.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

/**
 * Extracts relevant planets from an evaluated rule and its chart evidence.
 */
export function extractRelevantPlanetsFromRule(
  rule: EvaluatedPredictionRule,
  houses?: HouseInfo[]
): Array<{ name_en: string; name_ta: string; role_en: string; role_ta: string }> {
  const result: Array<{ name_en: string; name_ta: string; role_en: string; role_ta: string }> = [];
  const seenPlanets = new Set<string>();

  const addPlanet = (p: string, roleEn: string, roleTa: string) => {
    const cleanP = p.charAt(0).toUpperCase() + p.slice(1).toLowerCase();
    if (!PLANET_DETAILS[cleanP] || seenPlanets.has(cleanP)) return;
    seenPlanets.add(cleanP);
    result.push({
      name_en: cleanP,
      name_ta: PLANET_DETAILS[cleanP]?.ta || cleanP,
      role_en: roleEn,
      role_ta: roleTa,
    });
  };

  // 1. Check chart evidence strings (e.g. "D1 7th Lord (Moon) is placed in House 2", "Dispositor ... (Jupiter)")
  if (rule.chart_evidence && Array.isArray(rule.chart_evidence)) {
    for (const ev of rule.chart_evidence) {
      // Check for house lord mentions like "7th Lord (Moon)" or "2nd Lord (Saturn)"
      const matchLord = ev.match(/([0-9]{1,2})(?:st|nd|rd|th)\s+Lord\s*\(([A-Za-z]+)\)/i);
      if (matchLord && matchLord[1] && matchLord[2]) {
        const hNum = matchLord[1];
        const pName = matchLord[2];
        addPlanet(pName, `${hNum}th Lord (${pName})`, `${hNum}-ஆம் அதிபதி (${PLANET_DETAILS[pName]?.ta || pName})`);
      }

      // Check for dispositor mentions like "Dispositor of 7th Lord ... is (Saturn)"
      const matchDisp = ev.match(/Dispositor.*?is\s*\(([A-Za-z]+)\)/i);
      if (matchDisp && matchDisp[1]) {
        const pName = matchDisp[1];
        addPlanet(pName, `Dispositor (${pName})`, `வீட்டு அதிபதி / டிஸ்போஸிடர் (${PLANET_DETAILS[pName]?.ta || pName})`);
      }

      // Check for direct planet placement mentions like "Venus placed in Kendra", "Jupiter in 10th"
      for (const pName of Object.keys(PLANET_DETAILS)) {
        const reg = new RegExp(`\\b${pName}\\b`, "i");
        if (reg.test(ev)) {
          addPlanet(pName, `${pName} in Chart`, `ஜாதகத்தில் ${PLANET_DETAILS[pName].ta}`);
        }
      }
    }
  }

  // 2. If no lord matched from evidence, parse rule name and find lord via houses
  if (result.length === 0 && houses && houses.length >= 12) {
    const nameStr = `${rule.name_en || ""} ${rule.name_ta || ""} ${rule.rule_id || ""}`;
    const matchHouse = nameStr.match(/([0-9]{1,2})(?:st|nd|rd|th)\s+Lord/i) || nameStr.match(/([0-9]{1,2})-ஆம் அதிபதி/);
    if (matchHouse && matchHouse[1]) {
      const hNum = parseInt(matchHouse[1], 10);
      if (hNum >= 1 && hNum <= 12) {
        const hInfo = houses[hNum - 1];
        if (hInfo) {
          const signIdx = hInfo.sign_index;
          const lord = SIGN_LORDS[signIdx];
          if (lord) {
            addPlanet(lord, `${hNum}th Lord (${lord})`, `${hNum}-ஆம் அதிபதி (${PLANET_DETAILS[lord]?.ta || lord})`);
          }
        }
      }
    }
  }

  // 3. Fallback: Check rule name for direct classical planets (Venus, Jupiter, Saturn, etc.)
  if (result.length === 0) {
    const textToScan = `${rule.name_en || ""} ${rule.name_ta || ""}`;
    for (const [pName, details] of Object.entries(PLANET_DETAILS)) {
      const regEn = new RegExp(`\\b${pName}\\b`, "i");
      const regTa = new RegExp(details.ta, "i");
      if (regEn.test(textToScan) || regTa.test(textToScan)) {
        addPlanet(pName, `Significator (${pName})`, `காரக கிரகம் (${details.ta})`);
      }
    }
  }

  return result;
}

/**
 * Analyzes Dasa-Bhukti periods for the planets extracted from a rule.
 */
export function analyzeRuleDasaTiming(
  rule: EvaluatedPredictionRule,
  dasaTree: DasaPeriodNode[] | undefined,
  houses: HouseInfo[] | undefined
): RuleDasaTimingAnalysis | null {
  if (!dasaTree || !Array.isArray(dasaTree) || dasaTree.length === 0) {
    return null;
  }

  const relevantPlanets = extractRelevantPlanetsFromRule(rule, houses);
  if (relevantPlanets.length === 0) {
    return null;
  }

  const targetPlanetNames = new Set(relevantPlanets.map((p) => p.name_en.toLowerCase()));
  const todayIso = getTodayIso();

  const allPeriods: RuleDasaTimingPeriod[] = [];

  for (const mahaNode of dasaTree) {
    const mahaLord = mahaNode.lord.trim();
    const mahaLordClean = mahaLord.charAt(0).toUpperCase() + mahaLord.slice(1).toLowerCase();
    const mahaTa = PLANET_DETAILS[mahaLordClean]?.ta || mahaLord;

    // A. Check if the Mahadasha itself belongs to one of the target planets
    if (targetPlanetNames.has(mahaLord.toLowerCase())) {
      const startIso = (mahaNode.start_date_iso || "").split("T")[0];
      const endIso = (mahaNode.end_date_iso || "").split("T")[0];
      const status: "active" | "upcoming" | "past" =
        todayIso >= startIso && todayIso <= endIso
          ? "active"
          : todayIso < startIso
          ? "upcoming"
          : "past";

      allPeriods.push({
        maha_en: mahaLordClean,
        maha_ta: mahaTa,
        bhukti_en: `${mahaLordClean} Mahadasha (Full 10-20 Yr Period)`,
        bhukti_ta: `${mahaTa} மகா தசை (முழு காலம்)`,
        start_date: formatDateStr(startIso),
        end_date: formatDateStr(endIso),
        start_iso: startIso,
        end_iso: endIso,
        status,
        is_mahadasha_same: true,
      });
    }

    // B. Check Sub-Periods (Bhuktis / Antardashas)
    if (mahaNode.sub_periods && Array.isArray(mahaNode.sub_periods)) {
      for (const bhuktiNode of mahaNode.sub_periods) {
        const bhuktiLord = bhuktiNode.lord.trim();
        const bhuktiLordClean = bhuktiLord.charAt(0).toUpperCase() + bhuktiLord.slice(1).toLowerCase();
        const bhuktiTa = PLANET_DETAILS[bhuktiLordClean]?.ta || bhuktiLord;

        if (targetPlanetNames.has(bhuktiLord.toLowerCase())) {
          const startIso = (bhuktiNode.start_date_iso || "").split("T")[0];
          const endIso = (bhuktiNode.end_date_iso || "").split("T")[0];
          const status: "active" | "upcoming" | "past" =
            todayIso >= startIso && todayIso <= endIso
              ? "active"
              : todayIso < startIso
              ? "upcoming"
              : "past";

          allPeriods.push({
            maha_en: mahaLordClean,
            maha_ta: mahaTa,
            bhukti_en: bhuktiLordClean,
            bhukti_ta: bhuktiTa,
            start_date: formatDateStr(startIso),
            end_date: formatDateStr(endIso),
            start_iso: startIso,
            end_iso: endIso,
            status,
            is_mahadasha_same: mahaLordClean === bhuktiLordClean,
          });
        }
      }
    }
  }

  if (allPeriods.length === 0) {
    return null;
  }

  // Sort chronologically by start_iso
  allPeriods.sort((a, b) => a.start_iso.localeCompare(b.start_iso));

  // Find currently active period
  const activePeriod = allPeriods.find((p) => p.status === "active") || null;

  // Find next upcoming period
  const nextUpcomingPeriod = allPeriods.find((p) => p.status === "upcoming") || null;

  // Construct readable summaries
  let summary_ta = "";
  let summary_en = "";

  if (activePeriod) {
    summary_ta = `தற்போது நடப்பில் உள்ள காலம்: ${activePeriod.maha_ta} தசை – ${activePeriod.bhukti_ta} புக்தி (${activePeriod.start_date} முதல் ${activePeriod.end_date} வரை) இந்த விதியின் நற்பலன்களைத் தரும் முக்கிய யோகக் காலமாகும்.`;
    summary_en = `Currently Active Period: ${activePeriod.maha_en} Dasa – ${activePeriod.bhukti_en} Bhukti (${activePeriod.start_date} to ${activePeriod.end_date}) is actively triggering this rule's fructification.`;
  } else if (nextUpcomingPeriod) {
    summary_ta = `அடுத்த முக்கிய காலகட்டம்: ${nextUpcomingPeriod.maha_ta} தசை – ${nextUpcomingPeriod.bhukti_ta} புக்தி (${nextUpcomingPeriod.start_date} முதல் ${nextUpcomingPeriod.end_date} வரை) இந்த விதி நனவாகும் முதன்மைத் தருணமாகும்.`;
    summary_en = `Next Key Manifestation Window: ${nextUpcomingPeriod.maha_en} Dasa – ${nextUpcomingPeriod.bhukti_en} Bhukti (${nextUpcomingPeriod.start_date} to ${nextUpcomingPeriod.end_date}) is the primary window for this event.`;
  } else {
    summary_ta = `இந்த விதியோடு தொடர்புடைய தசா-புத்திக் காலங்கள் விம்சோத்தரி தசா அமைப்பில் ஆய்வு செய்யப்பட்டுள்ளன.`;
    summary_en = `Dasa-Bhukti periods associated with this rule's key significators have been mapped from the native's Vimshottari chart.`;
  }

  return {
    planets: relevantPlanets,
    activePeriod,
    nextUpcomingPeriod,
    allPeriods,
    summary_en,
    summary_ta,
  };
}
