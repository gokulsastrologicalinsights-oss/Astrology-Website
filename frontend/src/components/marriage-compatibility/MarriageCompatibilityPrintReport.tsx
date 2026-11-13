"use client";

import React from "react";
import { MarriageCompatibilityResponse } from "@/lib/types";

interface MarriageCompatibilityPrintReportProps {
  response: MarriageCompatibilityResponse;
}

const SIGN_NAME_TO_IDX: Record<string, number> = {
  Aries: 1,
  Taurus: 2,
  Gemini: 3,
  Cancer: 4,
  Leo: 5,
  Virgo: 6,
  Libra: 7,
  Scorpio: 8,
  Sagittarius: 9,
  Capricorn: 10,
  Aquarius: 11,
  Pisces: 12,
};

const SIGN_NAMES_TA: Record<number, string> = {
  1: "மேஷம்",
  2: "ரிஷபம்",
  3: "மிதுனம்",
  4: "கடகம்",
  5: "சிம்மம்",
  6: "கன்னி",
  7: "துலாம்",
  8: "விருச்சிகம்",
  9: "தனுசு",
  10: "மகரம்",
  11: "கும்பம்",
  12: "மீனம்",
};

const SIGN_LORD_TA: Record<number, string> = {
  1: "செவ்வாய்",
  2: "சுக்கிரன்",
  3: "புதன்",
  4: "சந்திரன்",
  5: "சூரியன்",
  6: "புதன்",
  7: "சுக்கிரன்",
  8: "செவ்வாய்",
  9: "குரு",
  10: "சனி",
  11: "சனி",
  12: "குரு",
};

const PLANET_NAME_TO_TA: Record<string, string> = {
  Sun: "சூரியன்",
  Moon: "சந்திரன்",
  Mars: "செவ்வாய்",
  Mercury: "புதன்",
  Jupiter: "குரு",
  Venus: "சுக்கிரன்",
  Saturn: "சனி",
  Rahu: "ராகு",
  Ketu: "கேது",
};

const PLANET_CHART_ABBR_TA: Record<string, string> = {
  Sun: "சூ",
  Moon: "சந்",
  Mars: "செ",
  Mercury: "பு",
  Jupiter: "குரு",
  Venus: "சுக்",
  Saturn: "சனி",
  Rahu: "ரா",
  Ketu: "கே",
  Ascendant: "ல",
  Lagna: "ல",
};

const GANA_TA: Record<string, string> = {
  Deva: "தேவம்",
  Manushya: "மனுஷம்",
  Rakshasa: "ராட்சஸம்",
};

const RAJJU_TA: Record<string, string> = {
  Shiro: "தலை",
  Kantha: "கழுத்து",
  Udara: "வயிறு",
  Kati: "இடை",
  Pada: "பாதம்",
};

const RAJJU_DIR_TA: Record<string, string> = {
  Arohana: "(ஏறு)",
  Avarohana: "(இறங்கு)",
  Central: "",
};

const RAJJU_DIRECTION_BY_NAK_IDX: Record<number, string> = {
  0: "Arohana", 9: "Arohana", 18: "Arohana",
  8: "Avarohana", 17: "Avarohana", 26: "Avarohana",
  1: "Arohana", 10: "Arohana", 19: "Arohana",
  7: "Avarohana", 16: "Avarohana", 25: "Avarohana",
  2: "Arohana", 11: "Arohana", 20: "Arohana",
  6: "Avarohana", 15: "Avarohana", 24: "Avarohana",
  3: "Arohana", 12: "Arohana", 21: "Arohana",
  5: "Avarohana", 14: "Avarohana", 23: "Avarohana",
  4: "Central", 13: "Central", 22: "Central",
};

const NAKSHATRA_NAMES_TA: string[] = [
  "அசுவினி", "பரணி", "கிருத்திகை", "ரோகிணி", "மிருகசீரிஷம்", "திருவாதிரை",
  "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்",
  "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை",
  "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்",
  "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி",
];

// Tamil Yoni Animal + Gender per 0-indexed Nakshatra
const YONI_BY_NAK_IDX_TA: Record<number, string> = {
  0: "ஆண் குதிரை",
  1: "ஆண் யானை",
  2: "பெண் ஆடு",
  3: "ஆண் பாம்பு",
  4: "பெண் பாம்பு",
  5: "ஆண் நாய்",
  6: "பெண் பூனை",
  7: "ஆண் ஆடு",
  8: "ஆண் பூனை",
  9: "ஆண் எலி",
  10: "பெண் எலி",
  11: "ஆண் பசு",
  12: "பெண் எருமை",
  13: "பெண் புலி",
  14: "ஆண் எருமை",
  15: "ஆண் புலி",
  16: "பெண் மான்",
  17: "ஆண் மான்",
  18: "பெண் நாய்",
  19: "ஆண் குரங்கு",
  20: "ஆண் கீரி",
  21: "பெண் குரங்கு",
  22: "பெண் சிம்மம்",
  23: "பெண் குதிரை",
  24: "ஆண் சிம்மம்",
  25: "பெண் பசு",
  26: "பெண் யானை",
};

const ANIMAL_TA: Record<string, string> = {
  Horse: "குதிரை",
  Elephant: "யானை",
  Sheep: "ஆடு",
  Serpent: "பாம்பு",
  Dog: "நாய்",
  Cat: "பூனை",
  Rat: "எலி",
  Cow: "பசு",
  Buffalo: "எருமை",
  Tiger: "புலி",
  Deer: "மான்",
  Monkey: "குரங்கு",
  Mongoose: "கீரி",
  Lion: "சிம்மம்",
};

const NADI_TA: Record<string, string> = {
  Adi: "வாதம்",
  Aadi: "வாதம்",
  Vata: "வாதம்",
  Madhya: "பித்தம்",
  Pitta: "பித்தம்",
  Antya: "சிலேத்துமம்",
  Kapha: "சிலேத்துமம்",
};

const ASHTAKOOTA_META_PRINT: Array<[string, string, number, string]> = [
  ["varna", "வர்ணம் (Varna)", 1, "ஆன்ம சுபாவம் & மனோபாவம்"],
  ["vashya", "வசியம் (Vashya)", 2, "பரஸ்பர ஈர்ப்பு & ஒற்றுமை"],
  ["tara", "தாரா (Tara)", 3, "நவதாரை அதிர்ஷ்டம் & ஆயுள்"],
  ["yoni", "யோனி (Yoni)", 4, "தாம்பத்திய இணக்கம்"],
  ["graha_maitri", "கிரக மைத்ரி (Maitri)", 5, "ராசிநாதர்களின் நட்பு"],
  ["gana", "கணம் (Gana)", 6, "குண நலன் & கருத்துப் பரிமாற்றம்"],
  ["bhakoot", "பகுட் (Bhakoot)", 7, "வம்ச விருத்தி & பொருள் நலம்"],
  ["nadi", "நாடி (Nadi)", 8, "மரபணு & சந்ததி ஆரோக்கியம்"],
];

const KP_VERDICT_TA: Record<string, string> = {
  FAVORABLE: "சாதகம்",
  POSITIVE: "சாதகம்",
  MIXED: "மிதமானது",
  UNFAVORABLE: "சாதகமற்றது",
  NEGATIVE: "சாதகமற்றது",
  STRONG: "வலுவான ஒற்றுமை",
  MODERATE: "மிதமான ஒற்றுமை",
  WEAK: "குறைவான ஒற்றுமை",
};

const PAPASAMYA_VERDICT_TA: Record<string, string> = {
  FAVORABLE: "சாதகமான சமநிலை",
  TOLERABLE: "ஏற்கத்தக்க சமநிலை",
  UNFAVORABLE: "கவனம் தேவை (பாப வேறுபாடு)",
};

function fmtPts(val: any): string {
  const n = Number(val ?? 0);
  if (Number.isNaN(n)) return "0";
  return Number.isInteger(n) ? String(n) : n.toFixed(1).replace(/\.0$/, "");
}

const DASA_COLORS: Record<string, { bg: string; lightBg: string; text: string }> = {
  Sun: { bg: "#F59E0B", lightBg: "#FDE68A", text: "#1E293B" },
  Moon: { bg: "#D1D5DB", lightBg: "#E5E7EB", text: "#1E293B" },
  Mars: { bg: "#EF4444", lightBg: "#FCA5A5", text: "#FFFFFF" },
  Rahu: { bg: "#374151", lightBg: "#6B7280", text: "#FFFFFF" },
  Jupiter: { bg: "#FACC15", lightBg: "#FEF08A", text: "#1E293B" },
  Saturn: { bg: "#3B5998", lightBg: "#93C5FD", text: "#FFFFFF" },
  Mercury: { bg: "#22C55E", lightBg: "#86EFAC", text: "#FFFFFF" },
  Ketu: { bg: "#6B7280", lightBg: "#9CA3AF", text: "#FFFFFF" },
  Venus: { bg: "#EC4899", lightBg: "#F9A8D4", text: "#FFFFFF" },
};

const VIMSHOTTARI_ORDER = [
  "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
];
const VIMSHOTTARI_YEARS: Record<string, number> = {
  Ketu: 7,
  Venus: 20,
  Sun: 6,
  Moon: 10,
  Mars: 7,
  Rahu: 18,
  Jupiter: 16,
  Saturn: 19,
  Mercury: 17,
};

const OWN_SIGNS_MAP: Record<string, number[]> = {
  Sun: [5], Moon: [4], Mars: [1, 8], Mercury: [3, 6],
  Jupiter: [9, 12], Venus: [2, 7], Saturn: [10, 11],
};
const EXALTATION_SIGNS_MAP: Record<string, number> = {
  Sun: 1, Moon: 2, Mars: 10, Mercury: 6, Jupiter: 4, Venus: 12, Saturn: 7,
};
const DEBILITATION_SIGNS_MAP: Record<string, number> = {
  Sun: 7, Moon: 8, Mars: 4, Mercury: 12, Jupiter: 10, Venus: 6, Saturn: 1,
};
const SIGN_LORDS_MAP: Record<number, string> = {
  1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 5: "Sun", 6: "Mercury",
  7: "Venus", 8: "Mars", 9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter",
};

interface EvaluatedDoshaCell {
  status: "NONE" | "MITIGATED" | "PRESENT";
  severity_percent?: number;
  reasons_ta?: string[];
}

function deriveDoshaAuditFromChartAndVedic(
  chart: any,
  vedic: any,
  partnerChart: any
): Record<string, EvaluatedDoshaCell> {
  const ascRaw = chart?.ascendant || {};
  const ascSignIdx: number =
    ascRaw.sign_index ||
    SIGN_NAME_TO_IDX[ascRaw.sign_name] ||
    1;

  const planetsList: any[] = Array.isArray(chart?.planets)
    ? chart.planets
    : chart?.planets
    ? Object.values(chart.planets)
    : [];

  const grahas: Record<string, { sign_index: number; house: number; is_combust: boolean; is_retrograde: boolean }> = {};
  for (const p of planetsList) {
    if (!p || !p.name) continue;
    const sIdx = Number(p.sign_index || SIGN_NAME_TO_IDX[p.sign_name] || 1);
    const house = ((sIdx - ascSignIdx + 12) % 12) + 1;
    grahas[p.name] = {
      sign_index: sIdx,
      house,
      is_combust: Boolean(p.is_combust),
      is_retrograde: Boolean(p.is_retrograde),
    };
  }

  // Cross-reference combustion and affliction from houses_analysis if present
  const housesAnalysis: Record<string, any> = vedic?.houses_analysis || {};
  for (const hData of Object.values(housesAnalysis)) {
    const lName = (hData as any)?.lord_name;
    if (lName && grahas[lName]) {
      const confl: string[] = (hData as any)?.conflicting_influences || [];
      if (confl.some((c) => typeof c === "string" && c.toLowerCase().includes("combust"))) {
        grahas[lName].is_combust = true;
      }
    }
  }

  const jupP = grahas["Jupiter"];
  const jupStrong = Boolean(jupP && (jupP.house === 1 || jupP.house === 4 || jupP.house === 7 || jupP.house === 10 || jupP.house === 5 || jupP.house === 9));

  const hasAspectOnHouse = (pName: string, targetHouse: number): boolean => {
    const p = grahas[pName];
    if (!p) return false;
    const dist = ((targetHouse - p.house + 12) % 12) + 1;
    if (dist === 7) return true;
    if (pName === "Mars" && (dist === 4 || dist === 8)) return true;
    if (pName === "Jupiter" && (dist === 5 || dist === 9)) return true;
    if (pName === "Saturn" && (dist === 3 || dist === 10)) return true;
    return false;
  };

  const hasAspectOnGraha = (p1: string, p2: string): boolean => {
    const target = grahas[p2];
    return target ? hasAspectOnHouse(p1, target.house) : false;
  };

  const audit: Record<string, EvaluatedDoshaCell> = {};

  // 1. செவ்வாய் தோஷம் (Kuja Dosha)
  const kuja = vedic?.kuja_dosha;
  if (!kuja || !kuja.is_present) {
    audit["kuja_dosha"] = { status: "NONE", severity_percent: 0, reasons_ta: [] };
  } else if (kuja.is_cancelled) {
    const reasons: string[] = [];
    const marsP = grahas["Mars"];
    if (marsP) {
      if (OWN_SIGNS_MAP["Mars"]?.includes(marsP.sign_index)) {
        reasons.push("தோஷ நிவர்த்தி: செவ்வாய் ஆட்சி பெற்றுள்ளது.");
      } else if (EXALTATION_SIGNS_MAP["Mars"] === marsP.sign_index) {
        reasons.push("தோஷ நிவர்த்தி: செவ்வாய் உச்சம் பெற்றுள்ளது.");
      }
      if (jupP && (jupP.sign_index === marsP.sign_index || hasAspectOnGraha("Jupiter", "Mars"))) {
        reasons.push("தோஷ நிவர்த்தி: செவ்வாய் குருவுடன் சேர்க்கை / பார்வை பெற்றுள்ளது.");
      }
    }
    const cList: string[] = Array.isArray(kuja.cancellations_applied) ? kuja.cancellations_applied : [];
    for (const c of cList) {
      if (typeof c === "string") {
        if (c.includes("Jupiter") && !reasons.some((r) => r.includes("குரு"))) {
          reasons.push("தோஷ நிவர்த்தி: செவ்வாய் குருவின் சுப பார்வை பெற்றுள்ளது.");
        } else if (c.includes("Saturn") && !reasons.some((r) => r.includes("சனி"))) {
          reasons.push("தோஷ நிவர்த்தி: செவ்வாய் சனியின் பார்வை பெற்றுள்ளது.");
        } else if ((c.includes("Mercury") || c.includes("Virgo")) && !reasons.some((r) => r.includes("ராசிநாதனுடன்"))) {
          reasons.push("தோஷம் நிவர்த்தி: செவ்வாய் ராசிநாதனுடன் சேர்க்கை பெற்றுள்ளார். (பு)");
        }
      }
    }
    if (reasons.length === 0) {
      reasons.push("தோஷ நிவர்த்தி: சாஸ்திர விதிவிலக்குகளால் செவ்வாய் தோஷம் நீங்கியுள்ளது.");
    }
    audit["kuja_dosha"] = { status: "MITIGATED", severity_percent: 0, reasons_ta: reasons.slice(0, 2) };
  } else {
    const sev = Math.min(100, Math.max(25, Math.round(Number(kuja.effective_intensity_percent ?? 45))));
    const defaultReason = kuja.mars_house_from_lagna
      ? `செவ்வாய் லக்னத்திலிருந்து ${kuja.mars_house_from_lagna}-ஆம் வீட்டிலும், சந்திரனிலிருந்து ${kuja.mars_house_from_moon ?? "-"}-ஆம் வீட்டிலும் உள்ளார்.`
      : "செவ்வாய் தோஷம் உள்ளது.";
    audit["kuja_dosha"] = {
      status: "PRESENT",
      severity_percent: sev,
      reasons_ta: [kuja.explanation_ta || defaultReason],
    };
  }

  // 2. நாக தோஷம் (Naga Dosha)
  const nagaTriggers: string[] = [];
  for (const nodeName of ["Rahu", "Ketu"]) {
    const np = grahas[nodeName];
    if (np && (np.house === 1 || np.house === 2 || np.house === 7 || np.house === 8)) {
      nagaTriggers.push(`${PLANET_NAME_TO_TA[nodeName]} ${np.house}-ஆம் வீட்டில் உள்ளார்.`);
    }
  }
  if (nagaTriggers.length === 0) {
    audit["naga_dosha"] = { status: "NONE", severity_percent: 0, reasons_ta: [] };
  } else {
    const mitigations: string[] = [];
    if (jupP && (hasAspectOnHouse("Jupiter", 1) || hasAspectOnHouse("Jupiter", 7))) {
      mitigations.push("தோஷ நிவர்த்தி: குரு பார்வை லக்னம் / 7-ஆம் வீட்டின் மீது உள்ளது.");
    }
    if (jupStrong && nagaTriggers.length === 1) {
      mitigations.push("பாதுகாப்பு: குரு கேந்திர/திரிகோணத்தில் வலுவாக உள்ளதால் நாக தோஷம் தணிக்கப்படுகிறது.");
    }
    if (mitigations.length > 0) {
      audit["naga_dosha"] = { status: "MITIGATED", severity_percent: 0, reasons_ta: mitigations };
    } else {
      audit["naga_dosha"] = {
        status: "PRESENT",
        severity_percent: Math.min(75, 30 * nagaTriggers.length),
        reasons_ta: nagaTriggers,
      };
    }
  }

  // 3. புத்ர தோஷம் (Putra Dosha)
  const h5 = housesAnalysis["5"] || housesAnalysis[5];
  const putraAff: string[] = [];
  if (h5) {
    const occs: string[] = Array.isArray(h5.occupants) ? h5.occupants : [];
    for (const occ of occs) {
      if (occ === "Rahu" || occ === "Ketu" || occ === "Saturn" || occ === "Mars") {
        putraAff.push(`${PLANET_NAME_TO_TA[occ] || occ} 5-ஆம் வீட்டில் உள்ளார்.`);
      }
    }
    if (h5.lord_house === 6 || h5.lord_house === 8 || h5.lord_house === 12) {
      putraAff.push(`5-ஆம் அதிபதி ${h5.lord_house}-ஆம் வீட்டில் (ஒரு துர்ஸ்தானம்) உள்ளார்.`);
    }
    if (h5.lord_dignity === "Debilitated") {
      putraAff.push("5-ஆம் அதிபதி நீசமடைந்துள்ளார்.");
    }
  }
  if (jupP && DEBILITATION_SIGNS_MAP["Jupiter"] === jupP.sign_index) {
    putraAff.push("குரு (புத்திர காரகன்) நீசமடைந்துள்ளார்.");
  }
  if (putraAff.length === 0) {
    audit["putra_dosha"] = { status: "NONE", severity_percent: 0, reasons_ta: [] };
  } else {
    const protections: string[] = [];
    if (jupStrong && putraAff.length <= 1 && (!h5 || !((h5.occupants || []).includes("Rahu") || (h5.occupants || []).includes("Ketu")))) {
      protections.push("வலுவான பாதுகாப்பு அமைப்புகளால், குறிப்பிடத்தக்க புத்திர தோஷம் இல்லை.");
      protections.push("பாதுகாப்பு: குரு கேந்திர/திரிகோணத்தில் நல்ல நிலையில் உள்ளார்.");
    } else if (hasAspectOnHouse("Jupiter", 5) && putraAff.length === 1) {
      protections.push("பாதுகாப்பு: குரு பகவான் 5-ஆம் வீட்டைப் பார்வையிடுவதால் தோஷ நிவர்த்தி ஏற்படுகிறது.");
    }
    if (protections.length > 0) {
      audit["putra_dosha"] = { status: "MITIGATED", severity_percent: 0, reasons_ta: protections };
    } else {
      const sev = putraAff.length >= 2 ? 55 : 30;
      audit["putra_dosha"] = {
        status: "PRESENT",
        severity_percent: Math.min(90, sev),
        reasons_ta: ["கண்டறியப்பட்ட பாதிப்புகள்:", ...putraAff],
      };
    }
  }

  // 4. பஞ்சணை தோஷம் (12th House Sayana Sukha)
  const h12 = housesAnalysis["12"] || housesAnalysis[12];
  const h12Aff: string[] = [];
  if (h12) {
    const occs: string[] = Array.isArray(h12.occupants) ? h12.occupants : [];
    for (const occ of occs) {
      if (occ === "Saturn" || occ === "Rahu" || occ === "Ketu" || occ === "Mars") {
        h12Aff.push(`பாவ கிரகம் ${PLANET_NAME_TO_TA[occ] || occ} 12-ஆம் வீட்டில் உள்ளார்.`);
      }
    }
    if (h12.lord_dignity === "Debilitated") {
      h12Aff.push("12-ஆம் அதிபதி நீசமடைந்துள்ளார்.");
    }
  }
  if (h12Aff.length === 0) {
    audit["panchanai_dosha"] = { status: "NONE", severity_percent: 0, reasons_ta: [] };
  } else {
    if (hasAspectOnHouse("Jupiter", 12) || (h12?.occupants || []).includes("Venus")) {
      audit["panchanai_dosha"] = {
        status: "MITIGATED",
        severity_percent: 0,
        reasons_ta: ["தோஷ நிவர்த்தி: சுப கிரக பார்வை/சேர்க்கையால் படுக்கை சுகம் பாதுகாக்கப்படுகிறது."],
      };
    } else {
      audit["panchanai_dosha"] = {
        status: "PRESENT",
        severity_percent: Math.min(75, 30 * h12Aff.length),
        reasons_ta: h12Aff,
      };
    }
  }

  // 5. சூரிய தோஷம் (Surya Dosha)
  const sunP = grahas["Sun"];
  const sunAff: string[] = [];
  if (sunP) {
    if (sunP.house === 1 || sunP.house === 7 || sunP.house === 8) {
      sunAff.push(`சூரிய தோஷம்: லக்னத்திலிருந்து ${sunP.house}-ல் சூரியன் (கூட்டுறவில் அகந்தை/ஆதிக்கம்).`);
    }
    if (DEBILITATION_SIGNS_MAP["Sun"] === sunP.sign_index) {
      sunAff.push("சூரியன் நீசமடைந்துள்ளார்.");
    }
  }
  if (sunAff.length === 0) {
    audit["surya_dosha"] = { status: "NONE", severity_percent: 0, reasons_ta: [] };
  } else {
    const mit: string[] = [];
    if (sunP && (sunP.sign_index === 1 || sunP.sign_index === 5)) {
      mit.push("தோஷ நிவர்த்தி: சூரியன் ஆட்சி/உச்ச பலத்துடன் உள்ளார்.");
    }
    if (jupP && hasAspectOnGraha("Jupiter", "Sun")) {
      mit.push("பாதுகாப்பு: குரு பகவான் சூரியனைப் பார்வையிடுகிறார்.");
    }
    if (mit.length > 0 && sunAff.length === 1) {
      audit["surya_dosha"] = { status: "MITIGATED", severity_percent: 0, reasons_ta: mit };
    } else {
      audit["surya_dosha"] = {
        status: "PRESENT",
        severity_percent: 35,
        reasons_ta: sunAff,
      };
    }
  }

  // 6. சுக்ர தோஷம் (Shukra Dosha)
  const venusP = grahas["Venus"];
  const vAff: string[] = [];
  if (venusP) {
    if (DEBILITATION_SIGNS_MAP["Venus"] === venusP.sign_index) {
      vAff.push("சுக்கிர தோஷம்: சுக்கிரன் நீசமடைந்துள்ளார்.");
    }
    if (venusP.house === 6 || venusP.house === 8 || venusP.house === 12) {
      vAff.push(`சுக்கிர தோஷம்: சுக்கிரன் துர்ஸ்தானமான ${venusP.house}-ஆம் வீட்டில் உள்ளார்.`);
    }
    if (venusP.is_combust) {
      vAff.push("சுக்கிர தோஷம்: சுக்கிரன் அஸ்தமனம் அடைந்துள்ளார்.");
    }
    for (const mName of ["Sun", "Rahu", "Ketu", "Saturn", "Mars"]) {
      const mp = grahas[mName];
      if (mp && mp.sign_index === venusP.sign_index && mName !== "Venus") {
        vAff.push(`சுக்கிர தோஷம்: சுக்கிரன் ${PLANET_NAME_TO_TA[mName]}-உடன் இணைந்துள்ளார்.`);
      }
    }
  }
  if (vAff.length === 0) {
    audit["shukra_dosha"] = { status: "NONE", severity_percent: 0, reasons_ta: [] };
  } else {
    const sev = vAff.length === 1 ? 25 : 30;
    audit["shukra_dosha"] = {
      status: "PRESENT",
      severity_percent: sev,
      reasons_ta: ["காணப்படும் பாதிப்புகள்:", ...vAff],
    };
  }

  // 7. 7 ஆம் வீடு தோஷம் (7th House Affliction)
  const h7 = housesAnalysis["7"] || housesAnalysis[7];
  const h7Aff: string[] = [];
  if (h7) {
    const occs: string[] = Array.isArray(h7.occupants) ? h7.occupants : [];
    for (const occ of occs) {
      if (occ === "Saturn" || occ === "Rahu" || occ === "Ketu" || occ === "Mars" || occ === "Sun") {
        h7Aff.push(`7-ஆம் இட தோஷம்: ${PLANET_NAME_TO_TA[occ] || occ} 7-ஆம் வீட்டில் உள்ளார்.`);
      }
    }
  }
  if (h7Aff.length === 0) {
    audit["seventh_house_dosha"] = { status: "NONE", severity_percent: 0, reasons_ta: [] };
  } else {
    if (h7 && (hasAspectOnHouse("Jupiter", 7) || (h7.occupants || []).includes("Jupiter"))) {
      audit["seventh_house_dosha"] = {
        status: "MITIGATED",
        severity_percent: 0,
        reasons_ta: ["தோஷ நிவர்த்தி: குரு பார்வை/சேர்க்கை 7-ஆம் வீட்டைப் பாதுகாக்கிறது."],
      };
    } else {
      audit["seventh_house_dosha"] = {
        status: "PRESENT",
        severity_percent: 25,
        reasons_ta: h7Aff,
      };
    }
  }

  // 8. 7 ஆம் அதிபதி தோஷம் (7th Lord Affliction)
  const h7LordAff: string[] = [];
  if (h7) {
    if (h7.lord_house === 6 || h7.lord_house === 8 || h7.lord_house === 12) {
      h7LordAff.push(`7-ஆம் அதிபதி தோஷம்: 7-ஆம் அதிபதி துர்ஸ்தானமான ${h7.lord_house}-ஆம் வீட்டில் உள்ளார்.`);
    }
    if (h7.lord_dignity === "Debilitated") {
      h7LordAff.push("7-ஆம் அதிபதி தோஷம்: 7-ஆம் அதிபதி நீசமடைந்துள்ளார்.");
    }
    const lordP = grahas[h7.lord_name];
    if (lordP && lordP.is_combust) {
      h7LordAff.push("7-ஆம் அதிபதி தோஷம்: 7-ஆம் அதிபதி அஸ்தமனம் அடைந்துள்ளார்.");
    }
  }
  if (h7LordAff.length === 0) {
    audit["seventh_lord_dosha"] = { status: "NONE", severity_percent: 0, reasons_ta: [] };
  } else {
    const sev = h7LordAff.length > 1 ? 50 : 25;
    audit["seventh_lord_dosha"] = {
      status: "PRESENT",
      severity_percent: sev,
      reasons_ta: h7LordAff,
    };
  }

  // 9. தீய கிரக சேர்க்கைகள் (Malefic Conjunctions)
  const malConj: string[] = [];
  if (venusP) {
    for (const mName of ["Sun", "Saturn", "Rahu", "Ketu", "Mars"]) {
      const mp = grahas[mName];
      if (mp && mp.sign_index === venusP.sign_index && mName !== "Venus") {
        malConj.push(`பாப கிரக சேர்க்கை: சுக்கிரன் பாவியான ${PLANET_NAME_TO_TA[mName]}-உடன் இணைந்துள்ளார்.`);
      }
    }
  }
  if (malConj.length === 0) {
    audit["malefic_conjunctions"] = { status: "NONE", severity_percent: 0, reasons_ta: [] };
  } else {
    audit["malefic_conjunctions"] = {
      status: "PRESENT",
      severity_percent: 30,
      reasons_ta: malConj,
    };
  }

  // 10. வதை வைநாசிகம் (Vadha Vainashika)
  const partnerAscIdx = partnerChart?.ascendant?.sign_index || 1;
  const partnerPlanets: any[] = Array.isArray(partnerChart?.planets) ? partnerChart.planets : [];
  const partnerMoon = partnerPlanets.find((p: any) => p && p.name === "Moon");
  const myMoon = planetsList.find((p: any) => p && p.name === "Moon");
  audit["vadha_vainashika"] = { status: "NONE", severity_percent: 0, reasons_ta: [] };

  return audit;
}

function formatBirthDateWithAge(dateStr?: string): string {
  if (!dateStr) return "-";
  const parsed = new Date(`${dateStr.slice(0, 10)}T00:00:00`);
  if (isNaN(parsed.getTime())) return dateStr;
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const dd = String(parsed.getDate()).padStart(2, "0");
  const mmm = months[parsed.getMonth()];
  const yyyy = parsed.getFullYear();

  const today = new Date();
  let age = today.getFullYear() - yyyy;
  const mDiff = today.getMonth() - parsed.getMonth();
  if (mDiff < 0 || (mDiff === 0 && today.getDate() < parsed.getDate())) {
    age--;
  }
  return `${dd}-${mmm}-${yyyy} (${Math.max(0, age)} Yrs)`;
}

function getSignTa(signEn?: string, signTa?: string): string {
  if (signTa && signTa.trim()) return signTa;
  if (!signEn) return "-";
  const idx = SIGN_NAME_TO_IDX[signEn];
  return idx ? SIGN_NAMES_TA[idx] : signEn;
}

function getNakIndexFromName(nakEn?: string): number | undefined {
  if (!nakEn) return undefined;
  const idxMap: Record<string, number> = {
    Ashwini: 0, Aswini: 0, Bharani: 1, Krittika: 2, Rohini: 3, Mrigashira: 4, Mrigashirsha: 4,
    Ardra: 5, Punarvasu: 6, Pushya: 7, Ashlesha: 8, Magha: 9, "Purva Phalguni": 10,
    "Uttara Phalguni": 11, Hasta: 12, Chitra: 13, Swati: 14, Vishakha: 15, Anuradha: 16,
    Jyeshtha: 17, Mula: 18, Moola: 18, "Purva Ashadha": 19, "Uttara Ashadha": 20,
    Shravana: 21, Dhanishta: 22, Shatabhisha: 23, "Purva Bhadrapada": 24,
    "Uttara Bhadrapada": 25, Revati: 26,
  };
  return idxMap[nakEn];
}

// Frontend fallback Vimshottari Mahadasha + transition builder for older saved reports
function computeClientDasaSequence(moonDegree: number, birthDateStr: string) {
  const norm = ((moonDegree % 360) + 360) % 360;
  const starSpan = 360 / 27;
  const starIdx = Math.floor(norm / starSpan);
  const remFraction = ((starIdx + 1) * starSpan - norm) / starSpan;
  const startLordIdx = starIdx % 9;
  const startLord = VIMSHOTTARI_ORDER[startLordIdx];

  const bDate = new Date(`${birthDateStr.slice(0, 10)}T00:00:00`);
  const birthYearDec = isNaN(bDate.getTime())
    ? 1995.0
    : bDate.getFullYear() + bDate.getMonth() / 12 + bDate.getDate() / 365.25;

  const mahadashas: Array<{
    lord_en: string;
    lord_ta: string;
    start_year: number;
    end_year: number;
    start_cal_year: number;
    end_cal_year: number;
    bhuktis: Array<{ lord_en: string; short_ta: string; start_year: number; end_year: number }>;
  }> = [];

  let cursorYear = birthYearDec;
  for (let i = 0; i < 9; i++) {
    const lord = VIMSHOTTARI_ORDER[(startLordIdx + i) % 9];
    const fullYears = VIMSHOTTARI_YEARS[lord];
    const durYears = i === 0 ? fullYears * remFraction : fullYears;
    const theoStart = i === 0 ? birthYearDec - fullYears * (1 - remFraction) : cursorYear;
    const endYear = cursorYear + durYears;

    const bhuktis: Array<{ lord_en: string; short_ta: string; start_year: number; end_year: number }> = [];
    const mdStartIdx = VIMSHOTTARI_ORDER.indexOf(lord);
    let bCursor = theoStart;
    for (let j = 0; j < 9; j++) {
      const bLord = VIMSHOTTARI_ORDER[(mdStartIdx + j) % 9];
      const bDur = fullYears * (VIMSHOTTARI_YEARS[bLord] / 120);
      const bEnd = bCursor + bDur;
      if (bEnd > cursorYear) {
        bhuktis.push({
          lord_en: bLord,
          short_ta: PLANET_CHART_ABBR_TA[bLord] || bLord.slice(0, 2),
          start_year: Math.max(cursorYear, bCursor),
          end_year: bEnd,
        });
      }
      bCursor = bEnd;
    }

    mahadashas.push({
      lord_en: lord,
      lord_ta: PLANET_NAME_TO_TA[lord] || lord,
      start_year: Number(cursorYear.toFixed(4)),
      end_year: Number(endYear.toFixed(4)),
      start_cal_year: Math.round(cursorYear),
      end_cal_year: Math.round(endYear),
      bhuktis,
    });
    cursorYear = endYear;
  }
  return mahadashas;
}

function SouthIndianPrintChart({
  chartData,
  fallbackAscSign,
  title,
  centerLabel,
}: {
  chartData: any;
  fallbackAscSign?: string;
  title: string;
  centerLabel: string;
}) {
  const ascRaw = chartData?.ascendant || {};
  const ascSignIdx: number =
    ascRaw.sign_index ||
    SIGN_NAME_TO_IDX[ascRaw.sign_name] ||
    (fallbackAscSign ? SIGN_NAME_TO_IDX[fallbackAscSign] : 1) ||
    1;

  const bySign: Record<number, string[]> = {};
  for (let i = 1; i <= 12; i++) bySign[i] = [];

  if (ascSignIdx >= 1 && ascSignIdx <= 12) {
    bySign[ascSignIdx].push("ல");
  }

  const planetsList = Array.isArray(chartData?.planets)
    ? chartData.planets
    : chartData?.planets
    ? Object.values(chartData.planets)
    : [];

  for (const p of planetsList as any[]) {
    if (!p || !p.name) continue;
    const abbr = PLANET_CHART_ABBR_TA[p.name];
    if (!abbr) continue; // Keep classic 9 grahas cleanly
    const sIdx = Number(p.sign_index || SIGN_NAME_TO_IDX[p.sign_name] || 0);
    if (sIdx >= 1 && sIdx <= 12) {
      const retroSuffix = p.is_retrograde && p.name !== "Rahu" && p.name !== "Ketu" ? "(வ)" : "";
      bySign[sIdx].push(`${abbr}${retroSuffix}`);
    }
  }

  const renderCell = (signIdx: number) => {
    const items = bySign[signIdx] || [];
    return (
      <td
        key={signIdx}
        className="border border-slate-900 align-middle text-center p-1 w-1/4 h-[68px]"
      >
        <div className="flex flex-col items-center justify-center leading-[1.25] text-[11px] font-bold text-slate-900 font-tamil">
          {items.map((txt, idx) => (
            <span key={idx} className="font-tamil whitespace-nowrap">
              {txt.normalize("NFC")}
            </span>
          ))}
        </div>
      </td>
    );
  };

  return (
    <div className="flex flex-col items-center font-tamil">
      <div className="text-[13px] font-bold text-slate-900 mb-1.5 text-center font-tamil">{title}</div>
      <table className="w-full max-w-[300px] border-collapse border-2 border-slate-900 table-fixed bg-white font-tamil">
        <tbody>
          <tr>{[12, 1, 2, 3].map(renderCell)}</tr>
          <tr>
            {renderCell(11)}
            <td
              colSpan={2}
              rowSpan={2}
              className="border border-slate-900 align-middle text-center font-bold text-[13px] text-slate-900 bg-white font-tamil"
            >
              {centerLabel}
            </td>
            {renderCell(4)}
          </tr>
          <tr>
            {renderCell(10)}
            {renderCell(5)}
          </tr>
          <tr>{[9, 8, 7, 6].map(renderCell)}</tr>
        </tbody>
      </table>
    </div>
  );
}

function renderDoshaCell(cell: { status?: string; severity_percent?: number; reasons_ta?: string[] } | undefined) {
  if (!cell || cell.status === "NONE") {
    return <span className="text-slate-700 font-medium">இல்லை</span>;
  }

  const isMitigated = cell.status === "MITIGATED";
  const textColor = isMitigated ? "text-emerald-700" : "text-rose-700";
  const headerText = isMitigated
    ? "தோஷ நிவர்த்தி"
    : `தோஷம் உள்ளது (Effective Dosha Severity: ${cell.severity_percent ?? 40}%)`;

  return (
    <div className={`${textColor} space-y-0.5 leading-snug text-[10.5px]`}>
      <div className="font-bold">{headerText}</div>
      {cell.reasons_ta && cell.reasons_ta.length > 0 && (
        <>
          <div className="font-semibold">காரணங்கள்:</div>
          {cell.reasons_ta.map((r, i) => (
            <div key={i} className="pl-1">
              {r}
            </div>
          ))}
        </>
      )}
    </div>
  );
}

export function MarriageCompatibilityPrintReport({ response }: MarriageCompatibilityPrintReportProps) {
  const gp = response.groom_profile;
  const bp = response.bride_profile;
  const poruthams = response.tamil_porutham?.poruthams || {};
  const kootas = response.ashtakoota?.kootas || {};

  // Build 11-row table matching the exact reference PDF layout
  const nadiKoota = kootas["nadi"];
  const nadiPassed = Boolean(nadiKoota && nadiKoota.earned_points > 0);

  const gNakIdx = poruthams["dina"]?.groom_input?.nakshatra_index ?? getNakIndexFromName(gp.moon_nakshatra);
  const bNakIdx = poruthams["dina"]?.bride_input?.nakshatra_index ?? getNakIndexFromName(bp.moon_nakshatra);

  const gNakTa = gp.moon_nakshatra_tamil || (gNakIdx !== undefined ? NAKSHATRA_NAMES_TA[gNakIdx] : gp.moon_nakshatra);
  const bNakTa = bp.moon_nakshatra_tamil || (bNakIdx !== undefined ? NAKSHATRA_NAMES_TA[bNakIdx] : bp.moon_nakshatra);

  const gRasiTa = getSignTa(gp.moon_sign, gp.moon_sign_tamil);
  const bRasiTa = getSignTa(bp.moon_sign, bp.moon_sign_tamil);
  const gLagnaTa = getSignTa(gp.ascendant_sign, gp.ascendant_sign_tamil);
  const bLagnaTa = getSignTa(bp.ascendant_sign, bp.ascendant_sign_tamil);

  const gMoonSignIdx = poruthams["rasi"]?.groom_input?.moon_sign_index || SIGN_NAME_TO_IDX[gp.moon_sign] || 1;
  const bMoonSignIdx = poruthams["rasi"]?.bride_input?.moon_sign_index || SIGN_NAME_TO_IDX[bp.moon_sign] || 1;

  const gGanaRaw = poruthams["gana"]?.groom_input?.gana || "";
  const bGanaRaw = poruthams["gana"]?.bride_input?.gana || "";

  const gYoniTa =
    (gNakIdx !== undefined && YONI_BY_NAK_IDX_TA[gNakIdx]) ||
    ANIMAL_TA[poruthams["yoni"]?.groom_input?.yoni_animal] ||
    "-";
  const bYoniTa =
    (bNakIdx !== undefined && YONI_BY_NAK_IDX_TA[bNakIdx]) ||
    ANIMAL_TA[poruthams["yoni"]?.bride_input?.yoni_animal] ||
    "-";

  const gRajjuRaw = poruthams["rajju"]?.groom_input?.rajju || "";
  const bRajjuRaw = poruthams["rajju"]?.bride_input?.rajju || "";
  const gRajjuDir = gNakIdx !== undefined ? RAJJU_DIR_TA[RAJJU_DIRECTION_BY_NAK_IDX[gNakIdx] || ""] || "" : "";
  const bRajjuDir = bNakIdx !== undefined ? RAJJU_DIR_TA[RAJJU_DIRECTION_BY_NAK_IDX[bNakIdx] || ""] || "" : "";

  const gRajjuTa = `${RAJJU_TA[gRajjuRaw] || gRajjuRaw}${gRajjuDir ? ` ${gRajjuDir}` : ""}`.trim() || "-";
  const bRajjuTa = `${RAJJU_TA[bRajjuRaw] || bRajjuRaw}${bRajjuDir ? ` ${bRajjuDir}` : ""}`.trim() || "-";

  const gNadiTa = NADI_TA[nadiKoota?.groom_input?.nadi] || nadiKoota?.groom_input?.nadi || "-";
  const bNadiTa = NADI_TA[nadiKoota?.bride_input?.nadi] || nadiKoota?.bride_input?.nadi || "-";

  const matchingRows = [
    {
      label: "தினம்",
      desc: "நீண்ட ஆயுளும் ஆரோக்கியமும்",
      groomVal: gNakTa,
      brideVal: bNakTa,
      pass: Boolean(poruthams["dina"]?.is_favorable),
    },
    {
      label: "கணம்",
      desc: "கருத்துப் பரிமாற்றமும் மகிழ்ச்சியும்",
      groomVal: GANA_TA[gGanaRaw] || gGanaRaw || "-",
      brideVal: GANA_TA[bGanaRaw] || bGanaRaw || "-",
      pass: Boolean(poruthams["gana"]?.is_favorable),
    },
    {
      label: "மகேந்திரம்",
      desc: "வாரிசுகளும் குழந்தைகளும் வளர்வது",
      groomVal: gNakTa,
      brideVal: bNakTa,
      pass: Boolean(poruthams["mahendra"]?.is_favorable),
    },
    {
      label: "ஸ்திரீ தீர்க்கம்",
      desc: "மனைவியின் ஆயுள், ஆரோக்கியம் மற்றும் ஐஸ்வர்யம்.",
      groomVal: gNakTa,
      brideVal: bNakTa,
      pass: Boolean(poruthams["sthree_deergha"]?.is_favorable),
    },
    {
      label: "யோனி",
      desc: "அன்பான மற்றும் பரஸ்பர மகிழ்ச்சி",
      groomVal: gYoniTa,
      brideVal: bYoniTa,
      pass: Boolean(poruthams["yoni"]?.is_favorable),
    },
    {
      label: "ராசி",
      desc: "வம்சத்தின் வளர்ச்சி",
      groomVal: gRasiTa,
      brideVal: bRasiTa,
      pass: Boolean(poruthams["rasi"]?.is_favorable),
    },
    {
      label: "ராசி அதிபதி",
      desc: "வாரிசுகளின் வளர்ச்சி",
      groomVal: SIGN_LORD_TA[gMoonSignIdx] || "-",
      brideVal: SIGN_LORD_TA[bMoonSignIdx] || "-",
      pass: Boolean(poruthams["rasi_adhipathi"]?.is_favorable),
    },
    {
      label: "வசியம்",
      desc: "பரஸ்பர நட்பு",
      groomVal: gRasiTa,
      brideVal: bRasiTa,
      pass: Boolean(poruthams["vasya"]?.is_favorable),
    },
    {
      label: "ரஜ்ஜு",
      desc: "திருமண அதிர்ஷ்டமும் மங்களமும் வளர்வது",
      groomVal: gRajjuTa,
      brideVal: bRajjuTa,
      pass: Boolean(poruthams["rajju"]?.is_favorable),
    },
    {
      label: "நாடி",
      desc: "நல்ல ஆரோக்கியம்",
      groomVal: gNadiTa,
      brideVal: bNadiTa,
      pass: nadiPassed,
    },
    {
      label: "வேதை",
      desc: "நட்பும் ஒற்றுமையும்",
      groomVal: gNakTa,
      brideVal: bNakTa,
      pass: Boolean(poruthams["vedha"]?.is_favorable),
    },
  ];

  const passedCount11 = matchingRows.filter((r) => r.pass).length;
  const ashtakootaPts = response.ashtakoota?.total_points ?? 0;

  // Print report structured data (from backend, or lightweight deterministic fallback for historical snapshots)
  const prd = response.print_report_data || {};

  // Kuja balance summary
  const samadoshamStatus = response.dosha_analysis?.samadosham_status;
  const kujaSummaryTa =
    prd.kuja_summary_ta ||
    (samadoshamStatus === "NOT_MUTUALLY_MATCHED"
      ? "செவ்வாய் தோஷம் கவனிக்கப்பட வேண்டும்"
      : samadoshamStatus === "MUTUALLY_MATCHED" || samadoshamStatus === "MITIGATED"
      ? "செவ்வாய் தோஷ சமநிலை உள்ளது"
      : "செவ்வாய் தோஷம் இல்லை");

  const outcome = response.composite_assessment?.overall_outcome;
  const isUnfavorable = outcome === "UNFAVOURABLE_UNDER_SELECTED_RULES";
  const isFavorable = outcome === "FAVOURABLE_UNDER_SELECTED_RULES" || (passedCount11 >= 8 && !isUnfavorable);

  const bannerHeaderBg = isUnfavorable
    ? "bg-rose-700"
    : isFavorable
    ? "bg-[#15803D]"
    : "bg-amber-700";
  const bannerBodyBg = isUnfavorable
    ? "bg-rose-50 border-rose-300"
    : isFavorable
    ? "bg-[#DCFCE7] border-emerald-400"
    : "bg-amber-50 border-amber-300";
  const bannerTitle = isUnfavorable
    ? "பொருத்தம் கவனிக்கத்தக்கது"
    : isFavorable
    ? "பொருத்தம் சிறப்பானது"
    : "பொருத்தம் நன்று (நிபந்தனைகளுடன்)";

  // Page 3: 10-row Dosha Audit
  const derivedGroomAudit = deriveDoshaAuditFromChartAndVedic(
    response.groom_chart,
    response.groom_vedic,
    response.bride_chart
  );
  const derivedBrideAudit = deriveDoshaAuditFromChartAndVedic(
    response.bride_chart,
    response.bride_vedic,
    response.groom_chart
  );

  const fallbackDoshaRows = [
    {
      id: "kuja_dosha",
      label_ta: "செவ்வாய் தோஷம்",
      groom: derivedGroomAudit["kuja_dosha"] || { status: "NONE", reasons_ta: [] },
      bride: derivedBrideAudit["kuja_dosha"] || { status: "NONE", reasons_ta: [] },
    },
    {
      id: "naga_dosha",
      label_ta: "நாக தோஷம்",
      groom: derivedGroomAudit["naga_dosha"] || { status: "NONE", reasons_ta: [] },
      bride: derivedBrideAudit["naga_dosha"] || { status: "NONE", reasons_ta: [] },
    },
    {
      id: "putra_dosha",
      label_ta: "புத்ர தோஷம்",
      groom: derivedGroomAudit["putra_dosha"] || { status: "NONE", reasons_ta: [] },
      bride: derivedBrideAudit["putra_dosha"] || { status: "NONE", reasons_ta: [] },
    },
    {
      id: "panchanai_dosha",
      label_ta: "பஞ்சணை தோஷம் (படுக்கை வசதிகள்)",
      groom: derivedGroomAudit["panchanai_dosha"] || { status: "NONE", reasons_ta: [] },
      bride: derivedBrideAudit["panchanai_dosha"] || { status: "NONE", reasons_ta: [] },
    },
    {
      id: "surya_dosha",
      label_ta: "சூரிய தோஷம் (அகங்காரம் / ஆதிக்கம்)",
      groom: derivedGroomAudit["surya_dosha"] || { status: "NONE", reasons_ta: [] },
      bride: derivedBrideAudit["surya_dosha"] || { status: "NONE", reasons_ta: [] },
    },
    {
      id: "shukra_dosha",
      label_ta: "சுக்ர தோஷம் (வெள்ளி கிரகப் பிறழ்வு)",
      groom: derivedGroomAudit["shukra_dosha"] || { status: "NONE", reasons_ta: [] },
      bride: derivedBrideAudit["shukra_dosha"] || { status: "NONE", reasons_ta: [] },
    },
    {
      id: "seventh_house_dosha",
      label_ta: "7 ஆம் வீடு தோஷம்",
      groom: derivedGroomAudit["seventh_house_dosha"] || { status: "NONE", reasons_ta: [] },
      bride: derivedBrideAudit["seventh_house_dosha"] || { status: "NONE", reasons_ta: [] },
    },
    {
      id: "seventh_lord_dosha",
      label_ta: "7 ஆம் அதிபதி தோஷம்",
      groom: derivedGroomAudit["seventh_lord_dosha"] || { status: "NONE", reasons_ta: [] },
      bride: derivedBrideAudit["seventh_lord_dosha"] || { status: "NONE", reasons_ta: [] },
    },
    {
      id: "malefic_conjunctions",
      label_ta: "தீய கிரக சேர்க்கைகள்",
      groom: derivedGroomAudit["malefic_conjunctions"] || { status: "NONE", reasons_ta: [] },
      bride: derivedBrideAudit["malefic_conjunctions"] || { status: "NONE", reasons_ta: [] },
    },
    {
      id: "vadha_vainashika",
      label_ta: "வதை வைநாசிகம்",
      groom: derivedGroomAudit["vadha_vainashika"] || { status: "NONE", reasons_ta: [] },
      bride: derivedBrideAudit["vadha_vainashika"] || { status: "NONE", reasons_ta: [] },
    },
  ];
  const doshaAuditRows = Array.isArray(prd.dosha_audit) && prd.dosha_audit.length > 0 ? prd.dosha_audit : fallbackDoshaRows;

  // Page 4: Dasa Bhukti Sequence Timeline
  const currentYearNum = new Date().getFullYear() + new Date().getMonth() / 12;
  let groomMds = prd.dasa_bhukti_sequence?.groom_mahadashas;
  let brideMds = prd.dasa_bhukti_sequence?.bride_mahadashas;
  let transitions = prd.dasa_bhukti_sequence?.transitions;

  if (!Array.isArray(groomMds) || !Array.isArray(brideMds)) {
    const gSeq = computeClientDasaSequence(gp.moon_degree, gp.birth_date);
    const bSeq = computeClientDasaSequence(bp.moon_degree, bp.birth_date);
    groomMds = gSeq;
    brideMds = bSeq;
    const calcTrans: Array<{ year: number; side: string; label_ta: string }> = [];
    const lookupB = (seq: typeof gSeq, yr: number) => {
      for (const m of seq) {
        if (m.start_year <= yr && yr <= m.end_year) {
          const found = m.bhuktis.find((b) => b.start_year <= yr && yr <= b.end_year) || m.bhuktis[0];
          return found ? `${found.short_ta} Bukthi` : "";
        }
      }
      return "";
    };
    const wMin = currentYearNum - 16;
    const wMax = currentYearNum + 95;
    for (let i = 0; i < gSeq.length - 1; i++) {
      const y = gSeq[i].end_year;
      if (y >= wMin && y <= wMax) {
        const lbl = lookupB(bSeq, y);
        if (lbl) calcTrans.push({ year: y, side: "groom", label_ta: lbl });
      }
    }
    for (let i = 0; i < bSeq.length - 1; i++) {
      const y = bSeq[i].end_year;
      if (y >= wMin && y <= wMax) {
        const lbl = lookupB(gSeq, y);
        if (lbl) calcTrans.push({ year: y, side: "bride", label_ta: lbl });
      }
    }
    calcTrans.sort((a, b) => a.year - b.year);
    transitions = calcTrans;
  }

  // Visible window for Page 4 timeline: start from the earlier active Mahadasha start across partners
  const findActiveOrLatestStart = (mds: any[]) => {
    const active = mds.find((m) => m.start_year <= currentYearNum && currentYearNum <= m.end_year);
    return active ? active.start_year : mds[0]?.start_year ?? currentYearNum - 5;
  };
  const gActiveStart = findActiveOrLatestStart(groomMds);
  const bActiveStart = findActiveOrLatestStart(brideMds);
  const minVisibleYear = Math.min(gActiveStart, bActiveStart, currentYearNum - 3);
  const maxVisibleYear = Math.max(minVisibleYear + 98, currentYearNum + 97);

  const svgWidth = 680;
  const svgHeight = 850;
  const topPad = 14;
  const botPad = 18;
  const usableH = svgHeight - topPad - botPad;
  const yForYear = (yr: number) => {
    const clamped = Math.max(minVisibleYear, Math.min(maxVisibleYear, yr));
    return topPad + ((clamped - minVisibleYear) / (maxVisibleYear - minVisibleYear)) * usableH;
  };

  // De-collide future transition arrow Y positions so labels remain legible
  const renderedTransitions: Array<{ y: number; side: string; label_ta: string }> = [];
  for (const t of transitions || []) {
    if (t.year < Math.max(currentYearNum - 0.05, Math.max(gActiveStart, bActiveStart)) || t.year > maxVisibleYear - 0.5) {
      continue;
    }
    let yPos = yForYear(t.year);
    for (const prev of renderedTransitions) {
      if (Math.abs(yPos - prev.y) < 14) {
        yPos = prev.y + 14;
      }
    }
    renderedTransitions.push({ y: yPos, side: t.side, label_ta: t.label_ta });
  }

  const nowY = yForYear(currentYearNum);
  const gVisibleMds = groomMds.filter((md: any) => md.end_year > gActiveStart + 0.01 && md.start_year < maxVisibleYear);
  const bVisibleMds = brideMds.filter((md: any) => md.end_year > bActiveStart + 0.01 && md.start_year < maxVisibleYear);
  const nowCollidesWithGStart = gVisibleMds.some(
    (md: any) => Math.abs(yForYear(md.start_year) + 4 - (nowY - 4)) < 11
  );

  // Page 5 data
  const dasaSandhi = prd.dasa_sandhi || {
    has_sandhi: response.sivadasan_ravi_insights?.dasa_porutham?.verdict === "AFFLICTED",
    summary_ta:
      response.sivadasan_ravi_insights?.dasa_porutham?.findings_ta?.[0] ||
      "தசா சந்தி அமைப்பு சரிபார்க்கப்பட்டது.",
    note_ta:
      "குறிப்பு: தசா சந்தி என்பது, தம்பதியர் இருவரும் ஒரு வருட காலத்திற்குள் புதிய மகா தசைக்குள் நுழைவதைக் குறிக்கிறது. பாரம்பரியமாக, இது தம்பதியருக்கு ஒரு நிலையற்ற காலமாகக் கருதப்படுகிறது.",
  };

  const harmoniousConns: Array<{ groom_planet_ta: string; bride_planet_ta: string; description_ta: string }> =
    prd.planetary_analysis?.harmonious_connections || [];
  const incompatibleCombs: Array<{ groom_planet_ta: string; bride_planet_ta: string; description_ta: string }> =
    prd.planetary_analysis?.incompatible_combinations || [];

  const sageVerdictTa =
    prd.sage_verdict?.summary_ta ||
    `பொருத்தம் மதிப்பெண் ${passedCount11}/11 ஆகும். அஷ்டகூட மதிப்பெண்: ${ashtakootaPts}/36. ${kujaSummaryTa}. மேலும் மதிப்பாய்வு மற்றும் முடிவெடுப்பதற்கு விரிவான தோஷ பகுப்பாய்வு அட்டவணையை தயவுசெய்து சரிபார்க்கவும்.`;

  // Page 6 computed sections (Ashtakoota 36, Papasamya, KP 7th CSL, Guru Balam, Nandi Yogam, In-Laws, Navamsa, Remedies)
  const ashSummary = response.ashtakoota;
  const ashThreshold = ashSummary?.minimum_threshold ?? 18;
  const ashThresholdMet = ashSummary?.is_threshold_met ?? ashtakootaPts >= ashThreshold;
  const ashtakootaRows = ASHTAKOOTA_META_PRINT.map(([kId, labelTa, maxDef, sigTa]) => {
    const kObj = kootas?.[kId];
    const maxPts = Number(kObj?.max_points ?? maxDef) || maxDef;
    const earnedPts = Number(kObj?.earned_points ?? 0) || 0;
    const isCancelled = Boolean(kObj?.is_cancelled);
    const cancelReason = String(kObj?.cancellation_reason || "").trim();
    let statusTa = "தோஷம்";
    let statusCls = "text-rose-700 font-bold";
    if (isCancelled) {
      statusTa = "தோஷ நிவர்த்தி";
      statusCls = "text-emerald-700 font-bold";
    } else if (earnedPts >= maxPts * 0.5) {
      statusTa = "சாதகம்";
      statusCls = "text-emerald-700 font-bold";
    } else if (earnedPts > 0) {
      statusTa = "பகுதி";
      statusCls = "text-amber-700 font-bold";
    }
    return {
      id: kId,
      labelTa,
      sigTa,
      earnedStr: fmtPts(earnedPts),
      maxStr: fmtPts(maxPts),
      statusTa,
      statusCls,
      cancelReason,
    };
  });

  const doshaAny: Record<string, any> = response.dosha_analysis || {};
  const gPapa = doshaAny.groom_papasamya || {};
  const bPapa = doshaAny.bride_papasamya || {};
  const papaVerdict = String(doshaAny.papasamya_verdict || "TOLERABLE").toUpperCase();
  const papaVerdictTa = PAPASAMYA_VERDICT_TA[papaVerdict] || papaVerdict;
  const papaToneCls =
    papaVerdict === "FAVORABLE"
      ? "text-emerald-700 font-bold"
      : papaVerdict === "UNFAVORABLE"
      ? "text-rose-700 font-bold"
      : "text-amber-700 font-bold";
  const papaDiffStr =
    doshaAny.papasamya_diff_percent !== undefined && doshaAny.papasamya_diff_percent !== null
      ? `${Number(doshaAny.papasamya_diff_percent).toFixed(1)}%`
      : "-";

  const kpRaw: Record<string, any> = response.kp_marriage || {};
  const kpAvailable = Boolean(response.kp_marriage && Object.keys(kpRaw).length > 0);
  const gKpCsl = kpRaw.groom_analysis?.csl_7th || {};
  const bKpCsl = kpRaw.bride_analysis?.csl_7th || {};
  const gCslEn = String(gKpCsl.sub_lord || kpRaw.groom_7th_csl_planet || "-");
  const bCslEn = String(bKpCsl.sub_lord || kpRaw.bride_7th_csl_planet || "-");
  const gKpVerdictEn = String(gKpCsl.verdict || kpRaw.groom_7th_csl_promise || "-").toUpperCase();
  const bKpVerdictEn = String(bKpCsl.verdict || kpRaw.bride_7th_csl_promise || "-").toUpperCase();
  const gKpHouses: number[] = Array.isArray(gKpCsl.supporting_houses_signified) ? gKpCsl.supporting_houses_signified : [];
  const bKpHouses: number[] = Array.isArray(bKpCsl.supporting_houses_signified) ? bKpCsl.supporting_houses_signified : [];
  const rpLevelEn = String(kpRaw.ruling_planets_agreement_level || kpRaw.significators_agreement || "-").toUpperCase();
  const sharedRpList: string[] = Array.isArray(kpRaw.shared_ruling_planets)
    ? kpRaw.shared_ruling_planets.map((p: string) => PLANET_NAME_TO_TA[p] || p)
    : [];

  const sr = response.sivadasan_ravi_insights;
  const guruBalam = sr?.guru_balam;
  const nadiYogam = sr?.nadi_porutham;
  const inLaws = sr?.in_laws_nakshatras;
  const parikara = sr?.classical_remedies?.parikara_sthalam;
  const firstHymn = sr?.classical_remedies?.sacred_hymns?.[0];

  const gD9Ca = (response.groom_vedic as any)?.navamsa_cross_analysis;
  const bD9Ca = (response.bride_vedic as any)?.navamsa_cross_analysis;
  const formatD9Summary = (ca: any, roleTa: string) => {
    if (!ca) return `${roleTa}: நவாம்ச நிலை சரிபார்க்கப்பட்டது.`;
    const d9Lagna = getSignTa(ca.d9_lagna_sign_name);
    const d9Lord = PLANET_NAME_TO_TA[ca.d9_7th_lord] || ca.d9_7th_lord || "-";
    const venusSign = getSignTa(ca.venus_in_d9_sign);
    return `${roleTa}: நவாம்ச லக்னம் ${d9Lagna}, 7-ஆம் அதிபதி ${d9Lord}, சுக்கிரன் ${venusSign}`;
  };
  const d9BoundaryWarn = Boolean(gD9Ca?.navamsa_boundary_risk || bD9Ca?.navamsa_boundary_risk);

  return (
    <div className="bg-white text-slate-900 font-tamil max-w-[190mm] mx-auto">
      {/* ======================== PAGE 1 ======================== */}
      <section className="marriage-print-page pt-1 pb-2">
        {/* Header with Logo and Address */}
        <div className="flex items-center justify-between border-b border-slate-300 pb-3 mb-4">
          <div className="w-16 h-16 shrink-0">
            <img
              src="/logo.png"
              alt="Gokul's Astrological Insights Logo"
              className="w-16 h-16 object-contain"
            />
          </div>
          <div className="flex-1 text-center pr-16">
            <h1 className="text-[20px] font-bold text-slate-900 tracking-tight leading-tight">
              Gokul&apos;s Astrological Insights
            </h1>
            <p className="text-[11px] text-slate-700 mt-0.5 leading-snug">
              165, Sakreeshwari Nagar, 2nd Street,
              <br />
              Thiruverkadu, Chennai - 600077
            </p>
          </div>
        </div>

        {/* Groom & Bride Summary Grid */}
        <div className="grid grid-cols-2 gap-8 mb-4 text-[11.5px]">
          {/* Groom */}
          <div>
            <h2 className="text-center text-[15px] font-bold text-[#0284C7] mb-2">மணமகன்</h2>
            <table className="w-full">
              <tbody className="leading-[1.75]">
                <tr>
                  <td className="text-slate-500 w-[44%]">பெயர்</td>
                  <td className="font-bold text-slate-900">{gp.name}</td>
                </tr>
                <tr>
                  <td className="text-slate-500">ராசி</td>
                  <td className="font-bold text-slate-900">{gRasiTa}</td>
                </tr>
                <tr>
                  <td className="text-slate-500">நட்சத்திரம் (பாதம்)</td>
                  <td className="font-bold text-slate-900">
                    {gNakTa} ({gp.moon_pada})
                  </td>
                </tr>
                <tr>
                  <td className="text-slate-500">லக்கினம்</td>
                  <td className="font-bold text-slate-900">{gLagnaTa}</td>
                </tr>
                <tr>
                  <td className="text-slate-500">பிறந்த தேதி</td>
                  <td className="font-bold text-slate-900">{formatBirthDateWithAge(gp.birth_date)}</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Bride */}
          <div>
            <h2 className="text-center text-[15px] font-bold text-[#0D9488] mb-2">மணமகள்</h2>
            <table className="w-full">
              <tbody className="leading-[1.75]">
                <tr>
                  <td className="text-slate-500 w-[44%]">பெயர்</td>
                  <td className="font-bold text-slate-900">{bp.name}</td>
                </tr>
                <tr>
                  <td className="text-slate-500">ராசி</td>
                  <td className="font-bold text-slate-900">{bRasiTa}</td>
                </tr>
                <tr>
                  <td className="text-slate-500">நட்சத்திரம் (பாதம்)</td>
                  <td className="font-bold text-slate-900">
                    {bNakTa} ({bp.moon_pada})
                  </td>
                </tr>
                <tr>
                  <td className="text-slate-500">லக்கினம்</td>
                  <td className="font-bold text-slate-900">{bLagnaTa}</td>
                </tr>
                <tr>
                  <td className="text-slate-500">பிறந்த தேதி</td>
                  <td className="font-bold text-slate-900">{formatBirthDateWithAge(bp.birth_date)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Verdict Banner */}
        <div className={`rounded-md overflow-hidden border ${bannerBodyBg} mb-4`}>
          <div className={`${bannerHeaderBg} text-white text-center font-bold text-[14px] py-1.5`}>
            {bannerTitle}
          </div>
          <div className="grid grid-cols-3 divide-x divide-slate-300/60 py-2.5 text-center">
            <div className="px-2">
              <div className="text-[10.5px] text-slate-700 font-medium">பொருத்தம் மதிப்பெண்</div>
              <div className="text-[14px] font-bold text-slate-900 mt-0.5">{passedCount11} / 11</div>
            </div>
            <div className="px-2">
              <div className="text-[10.5px] text-slate-700 font-medium">தோஷ சமநிலை</div>
              <div className="text-[13px] font-bold text-slate-900 mt-0.5">{kujaSummaryTa}</div>
            </div>
            <div className="px-2">
              <div className="text-[10.5px] text-slate-700 font-medium">அஷ்டகூட மதிப்பெண் (36)</div>
              <div className="text-[14px] font-bold text-slate-900 mt-0.5">{ashtakootaPts} / 36</div>
            </div>
          </div>
        </div>

        {/* Porutham Assessment Table */}
        <h3 className="text-[17px] font-bold text-slate-900 mb-2">பொருத்த மதிப்பீடு</h3>
        <table className="w-full border-collapse border border-slate-400 text-[11px]">
          <thead>
            <tr className="bg-slate-100 text-slate-900 font-bold">
              <th className="border border-slate-400 p-2 text-left w-[18%]">
                பொருத்தம்
                <br />
                (கூட்டம்)
              </th>
              <th className="border border-slate-400 p-2 text-left w-[34%]">விளக்கம்</th>
              <th className="border border-slate-400 p-2 text-left w-[17%]">
                மணமகன்
                <br />
                அம்சம்
              </th>
              <th className="border border-slate-400 p-2 text-left w-[17%]">
                மணமகள்
                <br />
                அம்சம்
              </th>
              <th className="border border-slate-400 p-2 text-center w-[14%]">பொருத்தம்</th>
            </tr>
          </thead>
          <tbody>
            {matchingRows.map((row) => (
              <tr key={row.label} className="bg-white">
                <td className="border border-slate-400 px-2 py-1.5 font-bold text-slate-900">{row.label}</td>
                <td className="border border-slate-400 px-2 py-1.5 text-slate-800 leading-snug">{row.desc}</td>
                <td className="border border-slate-400 px-2 py-1.5 text-slate-900">{row.groomVal}</td>
                <td className="border border-slate-400 px-2 py-1.5 text-slate-900">{row.brideVal}</td>
                <td className="border border-slate-400 px-2 py-1.5 text-center font-bold text-[13px]">
                  {row.pass ? (
                    <span className="text-emerald-600">✓</span>
                  ) : (
                    <span className="text-rose-600">✗</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* ======================== PAGE 2 ======================== */}
      <section className="marriage-print-page pt-4 pb-2">
        <div className="grid grid-cols-2 gap-x-8 gap-y-10">
          <SouthIndianPrintChart
            chartData={response.groom_chart}
            fallbackAscSign={gp.ascendant_sign}
            title="மணமகன் ராசி"
            centerLabel="ராசி (1)"
          />
          <SouthIndianPrintChart
            chartData={response.bride_chart}
            fallbackAscSign={bp.ascendant_sign}
            title="மணமகள் ராசி"
            centerLabel="ராசி (1)"
          />
          <SouthIndianPrintChart
            chartData={response.groom_d9_chart}
            fallbackAscSign={gp.ascendant_navamsa_sign}
            title="மணமகன் நவாம்சம் (Navamsa)"
            centerLabel="நவாம்சம் (9)"
          />
          <SouthIndianPrintChart
            chartData={response.bride_d9_chart}
            fallbackAscSign={bp.ascendant_navamsa_sign}
            title="மணமகள் நவாம்சம் (Navamsa)"
            centerLabel="நவாம்சம் (9)"
          />
        </div>
      </section>

      {/* ======================== PAGE 3 ======================== */}
      <section className="marriage-print-page pt-2 pb-2">
        <h2 className="text-[19px] font-bold text-slate-900 mb-3">தோஷ ஆய்வு</h2>
        <table className="w-full border-collapse border border-slate-400 text-[10.5px]">
          <thead>
            <tr className="bg-slate-100 text-slate-900 font-bold">
              <th className="border border-slate-400 p-2 text-left w-[24%]">தோஷ வகை</th>
              <th className="border border-slate-400 p-2 text-left w-[38%]">மணமகன் ஜாதகம்</th>
              <th className="border border-slate-400 p-2 text-left w-[38%]">மணமகள் ஜாதகம்</th>
            </tr>
          </thead>
          <tbody>
            {doshaAuditRows.map((row: any) => (
              <tr key={row.id || row.label_ta} className="bg-white align-middle">
                <td className="border border-slate-400 px-2.5 py-2 font-bold text-slate-900">{row.label_ta}</td>
                <td className="border border-slate-400 px-2.5 py-2">{renderDoshaCell(row.groom)}</td>
                <td className="border border-slate-400 px-2.5 py-2">{renderDoshaCell(row.bride)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* ======================== PAGE 4 ======================== */}
      <section className="marriage-print-page pt-2 pb-2">
        <h2 className="text-[19px] font-bold text-slate-900 mb-3">Dasa Bhukti Sequence</h2>
        <div className="grid grid-cols-2 mb-2 text-center font-bold text-[13px] text-slate-900">
          <div className="pr-16">மணமகன்</div>
          <div className="pl-16">மணமகள்</div>
        </div>

        <svg
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          className="w-full h-auto max-h-[240mm] mx-auto block"
          role="img"
          aria-label="Dasa Bhukti Sequence Timeline"
        >
          <defs>
            <marker id="arrowRedEnd" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
              <path d="M0,0 L6,3 L0,6 Z" fill="#DC2626" />
            </marker>
            <marker id="arrowRedStart" markerWidth="6" markerHeight="6" refX="1" refY="3" orient="auto">
              <path d="M6,0 L0,3 L6,6 Z" fill="#DC2626" />
            </marker>
          </defs>

          {/* Groom Mahadasha Blocks (Left) */}
          {gVisibleMds.map((md: any, idx: number) => {
            const yTop = yForYear(md.start_year);
            const yBot = yForYear(md.end_year);
            const h = Math.max(2, yBot - yTop);
            const col = DASA_COLORS[md.lord_en] || { bg: "#64748B", lightBg: "#CBD5E1", text: "#FFFFFF" };
            const isActiveSpan = md.start_year < currentYearNum && md.end_year > currentYearNum;

            return (
              <g key={`g-rect-${idx}`}>
                {isActiveSpan ? (
                  <>
                    <rect
                      x={70}
                      y={yTop}
                      width={145}
                      height={Math.max(1, nowY - yTop)}
                      fill={col.lightBg}
                      stroke="#FFFFFF"
                      strokeWidth="1"
                    />
                    <rect
                      x={70}
                      y={nowY}
                      width={145}
                      height={Math.max(1, yBot - nowY)}
                      fill={col.bg}
                      stroke="#FFFFFF"
                      strokeWidth="1"
                    />
                  </>
                ) : (
                  <rect
                    x={70}
                    y={yTop}
                    width={145}
                    height={h}
                    fill={col.bg}
                    stroke="#FFFFFF"
                    strokeWidth="1"
                  />
                )}
                <text x={62} y={yTop + 4} textAnchor="end" fontSize="10" fill="#64748B">
                  {md.start_cal_year}
                </text>
                {idx === gVisibleMds.length - 1 ? (
                  <text x={62} y={yBot + 3} textAnchor="end" fontSize="10" fill="#64748B">
                    {md.end_cal_year}
                  </text>
                ) : null}
              </g>
            );
          })}

          {/* Bride Mahadasha Blocks (Right) */}
          {bVisibleMds.map((md: any, idx: number) => {
            const yTop = yForYear(md.start_year);
            const yBot = yForYear(md.end_year);
            const h = Math.max(2, yBot - yTop);
            const col = DASA_COLORS[md.lord_en] || { bg: "#64748B", lightBg: "#CBD5E1", text: "#FFFFFF" };
            const isActiveSpan = md.start_year < currentYearNum && md.end_year > currentYearNum;

            return (
              <g key={`b-rect-${idx}`}>
                {isActiveSpan ? (
                  <>
                    <rect
                      x={465}
                      y={yTop}
                      width={145}
                      height={Math.max(1, nowY - yTop)}
                      fill={col.lightBg}
                      stroke="#FFFFFF"
                      strokeWidth="1"
                    />
                    <rect
                      x={465}
                      y={nowY}
                      width={145}
                      height={Math.max(1, yBot - nowY)}
                      fill={col.bg}
                      stroke="#FFFFFF"
                      strokeWidth="1"
                    />
                  </>
                ) : (
                  <rect
                    x={465}
                    y={yTop}
                    width={145}
                    height={h}
                    fill={col.bg}
                    stroke="#FFFFFF"
                    strokeWidth="1"
                  />
                )}
                <text x={618} y={yTop + 4} textAnchor="start" fontSize="10" fill="#64748B">
                  {md.start_cal_year}
                </text>
                {idx === bVisibleMds.length - 1 ? (
                  <text x={618} y={yBot + 3} textAnchor="start" fontSize="10" fill="#64748B">
                    {md.end_cal_year}
                  </text>
                ) : null}
              </g>
            );
          })}

          {/* Now Marker Line (drawn beneath text labels so active Mahadasha text stays uncrossed) */}
          {nowY >= topPad && nowY <= svgHeight - botPad && (
            <g>
              <line x1={32} y1={nowY} x2={215} y2={nowY} stroke="#DC2626" strokeWidth="1.5" />
              <text
                x={nowCollidesWithGStart ? 30 : 60}
                y={nowY - 4}
                textAnchor={nowCollidesWithGStart ? "start" : "end"}
                fontSize="10"
                fontWeight="700"
                fill="#DC2626"
              >
                Now
              </text>
            </g>
          )}

          {/* Groom & Bride Mahadasha Labels (rendered above Now line with subtle backdrop protection) */}
          {gVisibleMds.map((md: any, idx: number) => {
            const yTop = yForYear(md.start_year);
            const yBot = yForYear(md.end_year);
            const h = Math.max(2, yBot - yTop);
            if (h < 18) return null;
            const col = DASA_COLORS[md.lord_en] || { bg: "#64748B", lightBg: "#CBD5E1", text: "#FFFFFF" };
            const isActiveSpan = md.start_year < currentYearNum && md.end_year > currentYearNum;
            let textY = yTop + h / 2 + 4;
            if (isActiveSpan && Math.abs(nowY - (yTop + h / 2)) < 11) {
              const upperH = nowY - yTop;
              const lowerH = yBot - nowY;
              textY = lowerH >= upperH ? nowY + Math.max(13, lowerH / 2 + 3) : nowY - Math.max(6, upperH / 2 - 3);
            }
            const labelBg = isActiveSpan && textY < nowY ? col.lightBg : col.bg;
            return (
              <text
                key={`g-lbl-${idx}`}
                x={142.5}
                y={Math.min(yBot - 5, Math.max(yTop + 13, textY))}
                textAnchor="middle"
                fontSize="12"
                fontWeight="700"
                fill={col.text}
                stroke={labelBg}
                strokeWidth="3"
                paintOrder="stroke"
              >
                {md.lord_ta}
              </text>
            );
          })}
          {bVisibleMds.map((md: any, idx: number) => {
            const yTop = yForYear(md.start_year);
            const yBot = yForYear(md.end_year);
            const h = Math.max(2, yBot - yTop);
            if (h < 18) return null;
            const col = DASA_COLORS[md.lord_en] || { bg: "#64748B", lightBg: "#CBD5E1", text: "#FFFFFF" };
            const isActiveSpan = md.start_year < currentYearNum && md.end_year > currentYearNum;
            const textY = yTop + h / 2 + 4;
            const labelBg = isActiveSpan && textY < nowY ? col.lightBg : col.bg;
            return (
              <text
                key={`b-lbl-${idx}`}
                x={537.5}
                y={textY}
                textAnchor="middle"
                fontSize="12"
                fontWeight="700"
                fill={col.text}
                stroke={labelBg}
                strokeWidth="3"
                paintOrder="stroke"
              >
                {md.lord_ta}
              </text>
            );
          })}

          {/* Cross-Transition Arrows & Bukthi Labels */}
          {renderedTransitions.map((tr, idx) => (
            <g key={`tr-${idx}`}>
              <line
                x1={221}
                y1={tr.y}
                x2={459}
                y2={tr.y}
                stroke="#DC2626"
                strokeWidth="1.1"
                markerStart="url(#arrowRedStart)"
                markerEnd="url(#arrowRedEnd)"
              />
              <text
                x={340}
                y={tr.y - 3}
                textAnchor="middle"
                fontSize="9.5"
                fontWeight="600"
                fill="#7F1D1D"
              >
                {tr.label_ta}
              </text>
            </g>
          ))}
        </svg>
      </section>

      {/* ======================== PAGE 5 ======================== */}
      <section className="marriage-print-page pt-2 pb-2 space-y-5">
        {/* 1. Dasa Sandhi Analysis */}
        <div>
          <h2 className="text-[19px] font-bold text-slate-900 mb-2">தசா சந்தி ஆய்வு</h2>
          <div
            className={`rounded-md border p-3.5 text-[11px] space-y-2 ${
              dasaSandhi.has_sandhi
                ? "bg-rose-50/70 border-rose-200 text-rose-800"
                : "bg-emerald-50/70 border-emerald-200 text-emerald-800"
            }`}
          >
            <div className="font-bold text-[12px]">
              நிலை: {dasaSandhi.has_sandhi ? "இருக்கிறது" : "இல்லை"}
            </div>
            <div className="font-medium leading-snug">{dasaSandhi.summary_ta}</div>
            <div className="text-slate-600 text-[10.5px] leading-snug">{dasaSandhi.note_ta}</div>
          </div>
        </div>

        {/* 2. Planetary Positions Analysis */}
        <div>
          <h2 className="text-[18px] font-bold text-slate-900 mb-2">கிரக நிலைகள் ஆய்வு (கிரக பகுப்பாய்வு)</h2>

          {/* Harmonious Connections */}
          <h3 className="text-[13px] font-bold text-slate-900 mb-1.5">பொருத்தமான இணைப்புகள்</h3>
          <table className="w-full border-collapse border border-slate-400 text-[10.5px] mb-4">
            <thead>
              <tr className="bg-slate-100 text-slate-900 font-bold">
                <th className="border border-slate-400 p-2 text-left w-[18%]">
                  மணமகனின்
                  <br />
                  கிரகம்
                </th>
                <th className="border border-slate-400 p-2 text-left w-[18%]">
                  மணமகளின்
                  <br />
                  கிரகம்
                </th>
                <th className="border border-slate-400 p-2 text-left w-[64%]">விளக்கம்</th>
              </tr>
            </thead>
            <tbody>
              {harmoniousConns.length > 0 ? (
                harmoniousConns.map((item, idx) => (
                  <tr key={idx} className="bg-white align-middle">
                    <td className="border border-slate-400 px-2.5 py-2 font-medium text-emerald-700">
                      {item.groom_planet_ta}
                    </td>
                    <td className="border border-slate-400 px-2.5 py-2 font-medium text-emerald-700">
                      {item.bride_planet_ta}
                    </td>
                    <td className="border border-slate-400 px-2.5 py-2 text-emerald-700 leading-snug">
                      {item.description_ta}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={3} className="border border-slate-400 px-2.5 py-2 text-slate-600">
                    இரு ஜாதகங்களிலும் ஒரே ராசியில் இணையும் சுப கிரக அமைப்புகள் குறைவாக உள்ளன; நட்சத்திரப் பொருத்தம் அடிப்படையில் மதிப்பீடு செய்யப்பட்டது.
                  </td>
                </tr>
              )}
            </tbody>
          </table>

          {/* Incompatible Combinations */}
          <h3 className="text-[13px] font-bold text-slate-900 mb-1.5">பொருத்தமற்ற சேர்க்கைகள்</h3>
          <table className="w-full border-collapse border border-slate-400 text-[10.5px]">
            <thead>
              <tr className="bg-slate-100 text-slate-900 font-bold">
                <th className="border border-slate-400 p-2 text-left w-[18%]">
                  மணமகனின்
                  <br />
                  கிரகம்
                </th>
                <th className="border border-slate-400 p-2 text-left w-[18%]">
                  மணமகளின்
                  <br />
                  கிரகம்
                </th>
                <th className="border border-slate-400 p-2 text-left w-[64%]">விளக்கம்</th>
              </tr>
            </thead>
            <tbody>
              {incompatibleCombs.length > 0 ? (
                incompatibleCombs.map((item, idx) => (
                  <tr key={idx} className="bg-white align-middle">
                    <td className="border border-slate-400 px-2.5 py-2 font-medium text-rose-700">
                      {item.groom_planet_ta}
                    </td>
                    <td className="border border-slate-400 px-2.5 py-2 font-medium text-rose-700">
                      {item.bride_planet_ta}
                    </td>
                    <td className="border border-slate-400 px-2.5 py-2 text-rose-700 leading-snug">
                      {item.description_ta}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={3} className="border border-slate-400 px-2.5 py-2 text-emerald-700">
                    பொருத்தமற்ற எதிர்மறை கிரக சேர்க்கைகள் எதுவும் கண்டறியப்படவில்லை.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* 3. Sage's Verdict */}
        <div>
          <h2 className="text-[18px] font-bold text-slate-900 mb-2">முனிவரின் வாக்கு</h2>
          <p className="text-[11.5px] leading-[1.65] text-slate-900">{sageVerdictTa}</p>
        </div>
      </section>

      {/* ======================== PAGE 6 ======================== */}
      <section className="marriage-print-page pt-1 pb-2 space-y-3">
        {/* Ashtakoota 8-Koota Breakdown */}
        <div className="flex items-center justify-between gap-2">
          <h2 className="text-[17px] font-bold text-slate-900">அஷ்டகூட (36) &amp; கூடுதல் பொருத்த ஆய்வுகள்</h2>
          <span
            className={`px-2 py-0.5 rounded border text-[10px] font-bold ${
              ashThresholdMet
                ? "bg-emerald-50 border-emerald-200 text-emerald-700"
                : "bg-rose-50 border-rose-200 text-rose-700"
            }`}
          >
            மொத்தம்: {fmtPts(ashtakootaPts)} / 36 (குறைந்தபட்சம் {fmtPts(ashThreshold)})
          </span>
        </div>

        <table className="w-full border-collapse border border-slate-400 text-[9.8px]">
          <thead>
            <tr className="bg-slate-100 text-slate-900 font-bold">
              <th className="border border-slate-400 px-2 py-1.5 text-left w-[25%]">கூடம் (Koota)</th>
              <th className="border border-slate-400 px-2 py-1.5 text-left w-[47%]">விளக்கம் &amp; விலக்கு</th>
              <th className="border border-slate-400 px-2 py-1.5 text-center w-[14%]">மதிப்பெண்</th>
              <th className="border border-slate-400 px-2 py-1.5 text-center w-[14%]">நிலை</th>
            </tr>
          </thead>
          <tbody>
            {ashtakootaRows.map((row) => (
              <tr key={row.id} className="bg-white align-middle">
                <td className="border border-slate-400 px-2 py-1 font-bold text-slate-900">{row.labelTa}</td>
                <td className="border border-slate-400 px-2 py-1 text-slate-700 leading-snug">
                  <div>{row.sigTa}</div>
                  {row.cancelReason && (
                    <div className="text-[9px] text-emerald-700 font-semibold">விலக்கு: {row.cancelReason}</div>
                  )}
                </td>
                <td className="border border-slate-400 px-2 py-1 text-center font-bold text-slate-900">
                  {row.earnedStr} / {row.maxStr}
                </td>
                <td className={`border border-slate-400 px-2 py-1 text-center ${row.statusCls}`}>
                  {row.statusTa}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Papasamya & KP 7th CSL */}
        <div className="grid grid-cols-2 gap-3 text-[9.8px]">
          <div className="rounded-md border border-slate-300 bg-slate-50 p-2.5 space-y-1">
            <div className="font-bold text-[11px] text-slate-900 border-b border-slate-200 pb-1">
              தென் இந்திய பாபசாம்யம் (Papasamya)
            </div>
            <div className="text-slate-900">
              மணமகன் பாபம்: <b>{fmtPts(gPapa.total_papam)}</b> | மணமகள் பாபம்: <b>{fmtPts(bPapa.total_papam)}</b>
            </div>
            <div className="text-[9px] text-slate-600">
              மணமகன்: {Object.keys(gPapa).length > 0 ? `லக்னம்: ${fmtPts(gPapa.lagna_papam)} | சந்திரன்: ${fmtPts(gPapa.moon_papam)} | சுக்கிரன்: ${fmtPts(gPapa.venus_papam)}` : "-"}
            </div>
            <div className="text-[9px] text-slate-600">
              மணமகள்: {Object.keys(bPapa).length > 0 ? `லக்னம்: ${fmtPts(bPapa.lagna_papam)} | சந்திரன்: ${fmtPts(bPapa.moon_papam)} | சுக்கிரன்: ${fmtPts(bPapa.venus_papam)}` : "-"}
            </div>
            <div className="pt-1 border-t border-dashed border-slate-300 text-[9.2px] text-slate-800 leading-snug">
              வித்தியாசம்: <b>{papaDiffStr}</b> | தீர்ப்பு: <span className={papaToneCls}>{papaVerdictTa}</span>
              <br />
              {doshaAny.papasamya_explanation_ta || "இருவரின் பாபசாம்ய புள்ளிகள் ஒப்பிடப்பட்டன."}
            </div>
          </div>

          <div className="rounded-md border border-slate-300 bg-slate-50 p-2.5 space-y-1">
            <div className="font-bold text-[11px] text-slate-900 border-b border-slate-200 pb-1">
              கே.பி (KP) 7-ஆம் உப அதிபதி &amp; ஆளுமை கிரகங்கள்
            </div>
            {kpAvailable ? (
              <>
                <div className="text-slate-900">
                  மணமகன் 7-ஆம் உப அதிபதி: <b>{PLANET_NAME_TO_TA[gCslEn] || gCslEn}</b> ({KP_VERDICT_TA[gKpVerdictEn] || gKpVerdictEn})
                </div>
                <div className="text-[9px] text-slate-600">
                  சாதக பாவங்கள்: [{gKpHouses.length > 0 ? gKpHouses.join(", ") : "-"}]
                </div>
                <div className="text-slate-900 pt-0.5">
                  மணமகள் 7-ஆம் உப அதிபதி: <b>{PLANET_NAME_TO_TA[bCslEn] || bCslEn}</b> ({KP_VERDICT_TA[bKpVerdictEn] || bKpVerdictEn})
                </div>
                <div className="text-[9px] text-slate-600">
                  சாதக பாவங்கள்: [{bKpHouses.length > 0 ? bKpHouses.join(", ") : "-"}]
                </div>
                <div className="pt-1 border-t border-dashed border-slate-300 text-[9.2px] text-slate-800 leading-snug">
                  ஆளுமை கிரக ஒப்பீடு: <b>{KP_VERDICT_TA[rpLevelEn] || kpRaw.ruling_planets_agreement_level || "ஆய்வு செய்யப்பட்டது"}</b> | பொது கிரகங்கள்: {sharedRpList.length > 0 ? sharedRpList.join(", ") : "-"}
                </div>
              </>
            ) : (
              <div className="text-slate-600 text-[9.5px]">கே.பி (KP) 7-ஆம் உப அதிபதி தரவு சேர்க்கப்படவில்லை.</div>
            )}
          </div>
        </div>

        {/* Guru Balam, Nandi Yogam, In-Laws & Navamsa */}
        <div className="rounded-md border border-slate-300 bg-white p-2.5 space-y-1 text-[9.8px]">
          <div className="font-bold text-[11px] text-slate-900 border-b border-slate-200 pb-1">
            கோட்சார குரு பலம், நாடி &amp; நவாம்ச சிறப்பு ஆய்வு
          </div>
          <div className="text-slate-800 leading-snug">
            <b>கோட்சார குரு பலம்:</b> {guruBalam?.label_ta || "கோட்சார குரு பலம் சரிபார்க்கப்பட்டது"}
            {guruBalam?.description_ta ? ` — ${guruBalam.description_ta}` : ""}
          </div>
          {nadiYogam && (
            <>
              <div className="text-slate-800 leading-snug">
                <b>நாடிப் பொருத்தம் &amp; நந்தியோகம்:</b> {nadiYogam.verdict_ta}
              </div>
              {(nadiYogam.nandi_obstacles_ta || []).slice(0, 2).map((obs, idx) => (
                <div key={idx} className="text-[9px] text-slate-600 pl-2.5 leading-snug">
                  • {obs}
                </div>
              ))}
            </>
          )}
          {inLaws?.has_special_nakshatra && inLaws.findings.length > 0 ? (
            inLaws.findings.slice(0, 3).map((f, idx) => (
              <div key={idx} className="text-slate-800 leading-snug">
                <b>
                  {f.nakshatra_ta} ({f.relative_ta}):
                </b>{" "}
                {f.is_exempt ? "விதிவிலக்கு பொருந்தியது (தோஷமில்லை)" : "கவனம் தேவை"} — {f.explanation_ta}
              </div>
            ))
          ) : (
            <div className="text-slate-800 leading-snug">
              <b>மாமனார்/மாமியார் விசேஷ நட்சத்திர ஆய்வு:</b> விசேஷ நட்சத்திர தோஷம் எதுவும் இல்லை.
            </div>
          )}
          <div className="text-slate-800 leading-snug">
            <b>நவாம்ச (D9) நிலை:</b> {formatD9Summary(gD9Ca, "மணமகன்")} | {formatD9Summary(bD9Ca, "மணமகள்")}
          </div>
          {d9BoundaryWarn && (
            <div className="text-[9.2px] font-semibold text-amber-700">
              நேர எச்சரிக்கை: பிறப்பு நேர சிறு மாற்றத்தால் நவாம்ச லக்னம் மாற வாய்ப்புள்ளதால் நேர உறுதிப்படுத்தல் நல்லது.
            </div>
          )}
        </div>

        {/* Parikara Sthalam & Ethical Disclaimer */}
        <div className="rounded-md border border-amber-200 bg-amber-50 p-2.5 text-[9.8px]">
          <div className="font-bold text-[10.5px] text-amber-900 mb-0.5">முதன்மை பரிகார ஸ்தலம் &amp; வழிகாட்டுதல்</div>
          <div className="text-slate-800 leading-snug">
            <b>{parikara?.name_ta || "குலதெய்வ வழிபாடு & திருக்கோவில் தரிசனம்"}</b> —{" "}
            {parikara?.significance_ta || "திருமண நல்வாழ்விற்காக இறை வழிபாடு மேற்கொள்ளவும்."}
            {firstHymn?.title_ta ? ` | பரிந்துரைக்கப்படும் பாராயணம்: ${firstHymn.title_ta}` : ""}
          </div>
        </div>

        <p className="text-[8.8px] text-slate-500 border-t border-slate-200 pt-1.5 leading-snug">
          குறிப்பு: இந்த அறிக்கை பாரம்பரிய தமிழ் பொருத்தம், 36 அஷ்டகூடம், பாபசாம்யம், வேத மற்றும் கே.பி. (KP) ஜோதிட விதிகளின் அடிப்படையில் தயாரிக்கப்பட்டது; இறுதி திருமண முடிவிற்கு குடும்ப ஆலோசனையும் சுப முகூர்த்த தேர்வும் பரிந்துரைக்கப்படுகிறது.
        </p>
      </section>
    </div>
  );
}
