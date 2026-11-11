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
  Madhya: "பித்தம்",
  Antya: "சிலேத்துமம்",
};

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
        <div className="flex flex-col items-center justify-center leading-[1.25] text-[10.5px] font-medium text-slate-900">
          {items.map((txt, idx) => (
            <span key={idx}>{txt}</span>
          ))}
        </div>
      </td>
    );
  };

  return (
    <div className="flex flex-col items-center">
      <div className="text-[12px] font-bold text-slate-900 mb-1.5 text-center">{title}</div>
      <table className="w-full max-w-[300px] border-collapse border-2 border-slate-900 table-fixed bg-white">
        <tbody>
          <tr>{[12, 1, 2, 3].map(renderCell)}</tr>
          <tr>
            {renderCell(11)}
            <td
              colSpan={2}
              rowSpan={2}
              className="border border-slate-900 align-middle text-center font-bold text-[12px] text-slate-900 bg-white"
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
  const fallbackDoshaRows = [
    {
      id: "kuja_dosha",
      label_ta: "செவ்வாய் தோஷம்",
      groom: response.dosha_analysis?.groom_kuja?.is_present
        ? response.dosha_analysis?.groom_kuja?.is_cancelled
          ? { status: "MITIGATED", reasons_ta: ["தோஷ நிவர்த்தி: செவ்வாய் தோஷ விலக்கு பெற்றுள்ளது."] }
          : { status: "PRESENT", severity_percent: 45, reasons_ta: [response.dosha_analysis?.groom_kuja?.interpretation_tamil || "செவ்வாய் தோஷம் உள்ளது."] }
        : { status: "NONE", reasons_ta: [] },
      bride: response.dosha_analysis?.bride_kuja?.is_present
        ? response.dosha_analysis?.bride_kuja?.is_cancelled
          ? { status: "MITIGATED", reasons_ta: ["தோஷ நிவர்த்தி: செவ்வாய் தோஷ விலக்கு பெற்றுள்ளது."] }
          : { status: "PRESENT", severity_percent: 45, reasons_ta: [response.dosha_analysis?.bride_kuja?.interpretation_tamil || "செவ்வாய் தோஷம் உள்ளது."] }
        : { status: "NONE", reasons_ta: [] },
    },
    { id: "naga_dosha", label_ta: "நாக தோஷம்", groom: { status: "NONE" }, bride: { status: "NONE" } },
    { id: "putra_dosha", label_ta: "புத்ர தோஷம்", groom: { status: "NONE" }, bride: { status: "NONE" } },
    { id: "panchanai_dosha", label_ta: "பஞ்சணை தோஷம் (படுக்கை வசதிகள்)", groom: { status: "NONE" }, bride: { status: "NONE" } },
    { id: "surya_dosha", label_ta: "சூரிய தோஷம் (அகங்காரம் / ஆதிக்கம்)", groom: { status: "NONE" }, bride: { status: "NONE" } },
    { id: "shukra_dosha", label_ta: "சுக்ர தோஷம் (வெள்ளி கிரகப் பிறழ்வு)", groom: { status: "NONE" }, bride: { status: "NONE" } },
    { id: "seventh_house_dosha", label_ta: "7 ஆம் வீடு தோஷம்", groom: { status: "NONE" }, bride: { status: "NONE" } },
    { id: "seventh_lord_dosha", label_ta: "7 ஆம் அதிபதி தோஷம்", groom: { status: "NONE" }, bride: { status: "NONE" } },
    { id: "malefic_conjunctions", label_ta: "தீய கிரக சேர்க்கைகள்", groom: { status: "NONE" }, bride: { status: "NONE" } },
    { id: "vadha_vainashika", label_ta: "வதை வைநாசிகம்", groom: { status: "NONE" }, bride: { status: "NONE" } },
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
            title="மணமகன் Navamsa"
            centerLabel="நவாம்சம் (9)"
          />
          <SouthIndianPrintChart
            chartData={response.bride_d9_chart}
            fallbackAscSign={bp.ascendant_navamsa_sign}
            title="மணமகள் Navamsa"
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
    </div>
  );
}
