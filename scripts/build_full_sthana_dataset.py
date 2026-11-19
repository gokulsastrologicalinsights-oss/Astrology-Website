# -*- coding: utf-8 -*-
"""
Builder script to generate frontend/src/lib/planetary-sthana-predictions.ts
Assembles all 108 authentic planetary house placement records from:
- sthana_data_sun_moon_mars.py
- sthana_data_mercury_jupiter_venus.py
- sthana_data_saturn_rahu_ketu.py
"""

import os
import json
import sys

# Add scripts directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sthana_data_sun_moon_mars import SUN_DATA, MOON_DATA, MARS_DATA
from sthana_data_mercury_jupiter_venus import MERCURY_DATA, JUPITER_DATA, VENUS_DATA
from sthana_data_saturn_rahu_ketu import SATURN_DATA, RAHU_DATA, KETU_DATA

PLANET_SPECS = [
    {"name": "Sun", "name_ta": "சூரியன்", "symbol": "☀️", "element": "தீ (Agni)", "data": SUN_DATA},
    {"name": "Moon", "name_ta": "சந்திரன்", "symbol": "🌙", "element": "நீர் (Jala)", "data": MOON_DATA},
    {"name": "Mars", "name_ta": "செவ்வாய்", "symbol": "🔴", "element": "தீ (Agni)", "data": MARS_DATA},
    {"name": "Mercury", "name_ta": "புதன்", "symbol": "🟢", "element": "நிலம் (Prithvi)", "data": MERCURY_DATA},
    {"name": "Jupiter", "name_ta": "குரு", "symbol": "🟡", "element": "ஆகாயம் (Akasha)", "data": JUPITER_DATA},
    {"name": "Venus", "name_ta": "சுக்கிரன்", "symbol": "✨", "element": "நீர் (Jala)", "data": VENUS_DATA},
    {"name": "Saturn", "name_ta": "சனி", "symbol": "🪐", "element": "காற்று (Vayu)", "data": SATURN_DATA},
    {"name": "Rahu", "name_ta": "ராகு", "symbol": "🐉", "element": "மாயை / காற்று", "data": RAHU_DATA},
    {"name": "Ketu", "name_ta": "கேது", "symbol": "☄️", "element": "மோட்சம் / நெருப்பு", "data": KETU_DATA},
]

all_records = []
for p in PLANET_SPECS:
    for item in p["data"]:
        rec = {
            "planet": p["name"],
            "planet_name_ta": p["name_ta"],
            "symbol": p["symbol"],
            "element": p["element"],
            "house": item["house"],
            "bhava_category": item["bhava_category"],
            "house_title_ta": item["house_title_ta"],
            "house_title_en": item["house_title_en"],
            "core_traits_ta": item["core_traits_ta"],
            "core_traits_en": item["core_traits_en"],
            "strong_placement_ta": item["strong_placement_ta"],
            "strong_placement_en": item["strong_placement_en"],
            "weak_placement_ta": item["weak_placement_ta"],
            "weak_placement_en": item["weak_placement_en"],
            "career_wealth_ta": item["career_wealth_ta"],
            "career_wealth_en": item["career_wealth_en"],
            "health_precautions_ta": item["health_precautions_ta"],
            "health_precautions_en": item["health_precautions_en"],
            "source_reference": item["source_reference"]
        }
        all_records.append(rec)

print(f"Total compiled records: {len(all_records)} (Expected: 108)")

OUTPUT_PATH = os.path.join("frontend", "src", "lib", "planetary-sthana-predictions.ts")

ts_content = """// Classical Planetary House Placement Predictions Engine
// Synthesized directly from Dr. B. V. Raman's "How to Judge a Horoscope" (Vol 1 & 2),
// Kalyana Varma's "Saravali" (Ch. 30), and Maharishi Parashara's BPHS.

import { getGrahaDignity } from "./dignity";

export type BhavaCategory = "kendra" | "trikona" | "upachaya" | "dusthana" | "panaphara" | "apoklima";

export interface PlanetarySthanaPrediction {
  planet: "Sun" | "Moon" | "Mars" | "Mercury" | "Jupiter" | "Venus" | "Saturn" | "Rahu" | "Ketu";
  planet_name_ta: string;
  symbol: string;
  element: string;
  house: number; // 1 to 12 from Lagna
  bhava_category: BhavaCategory;
  house_title_ta: string;
  house_title_en: string;
  core_traits_ta: string[];
  core_traits_en: string[];
  strong_placement_ta: string[];
  strong_placement_en: string[];
  weak_placement_ta: string[];
  weak_placement_en: string[];
  career_wealth_ta: string[];
  career_wealth_en: string[];
  health_precautions_ta: string[];
  health_precautions_en: string[];
  source_reference: string;
}

export interface EvaluatedPlanetSthana {
  planet_name: string;
  planet_name_ta: string;
  symbol: string;
  element: string;
  house_number: number;
  house_name_ta: string;
  house_name_en: string;
  bhava_category: BhavaCategory;
  sign_index: number;
  sign_name_ta: string;
  sign_name_en: string;
  degree_in_sign: number;
  is_retrograde: boolean;
  dignity_label_ta: string;
  dignity_label_en: string;
  dignity_type: "exalted" | "own_sign" | "dikbala" | "friendly" | "debilitated" | "enemy" | "neutral";
  shadbala_rupas?: number;
  shadbala_ratio?: number;
  shadbala_percentage?: number;
  shadbala_is_strong?: boolean;
  is_net_strong: boolean;
  status_summary_ta: string;
  status_summary_en: string;
  prediction: PlanetarySthanaPrediction;
}

const SIGN_NAMES_TA = [
  "மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்",
  "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்",
  "தனுசு", "மகரம்", "கும்பம்", "மீனம்"
];

const SIGN_NAMES_EN = [
  "Aries", "Taurus", "Gemini", "Cancer",
  "Leo", "Virgo", "Libra", "Scorpio",
  "Sagittarius", "Capricorn", "Aquarius", "Pisces"
];

export const PLANETARY_STHANA_PREDICTIONS: PlanetarySthanaPrediction[] = """ + json.dumps(all_records, ensure_ascii=False, indent=2) + """;

const OWN_SIGNS_MAP: Record<string, number[]> = {
  Sun: [5],
  Moon: [4],
  Mars: [1, 8],
  Mercury: [3, 6],
  Jupiter: [9, 12],
  Venus: [2, 7],
  Saturn: [10, 11],
  Rahu: [11],
  Ketu: [8],
};

/**
 * Evaluates the 9 planets' house placements from Lagna for any horoscope,
 * computing house distance, sign placement, dignity (Ucham/Aatchi/Neecham/Dikbala),
 * and Shadbala percentage.
 */
export function evaluateHoroscopePlanetarySthanas(horoscope: any): EvaluatedPlanetSthana[] {
  if (!horoscope || !horoscope.planets || !horoscope.ascendant) {
    return [];
  }

  const lagnaSignIndex = horoscope.ascendant.sign_index;
  const results: EvaluatedPlanetSthana[] = [];

  const targetPlanets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];

  // Normalize planets list from array or object
  const planetsList: any[] = Array.isArray(horoscope.planets)
    ? horoscope.planets
    : Object.values(horoscope.planets);

  for (const planetKey of targetPlanets) {
    const planetData = planetsList.find(
      (p: any) => p && p.name && p.name.toLowerCase() === planetKey.toLowerCase()
    );
    if (!planetData) continue;

    const signIndex = planetData.sign_index;
    const houseNumber =
      planetData.house && planetData.house >= 1 && planetData.house <= 12
        ? planetData.house
        : (((signIndex - lagnaSignIndex + 12) % 12) + 1);

    // Retrieve Dignity with correct arguments:
    // (planetName, signIndex, ascendantSignIndex, degreeInSign, explicitHouse)
    const dignity = getGrahaDignity(
      planetKey,
      signIndex,
      lagnaSignIndex,
      planetData.degree_in_sign || 0,
      houseNumber
    );

    const isOwnSign = Boolean(OWN_SIGNS_MAP[planetKey]?.includes(signIndex));

    // Retrieve Shadbala detail (handles both array and object formats)
    let shadbalaDetail: any = null;
    if (horoscope.shadbala?.planets) {
      if (Array.isArray(horoscope.shadbala.planets)) {
        shadbalaDetail = horoscope.shadbala.planets.find(
          (sp: any) => sp && sp.planet && sp.planet.toLowerCase() === planetKey.toLowerCase()
        );
      } else {
        shadbalaDetail = horoscope.shadbala.planets[planetKey];
      }
    }

    const shadbalaRatio = shadbalaDetail?.ratio ?? 1.0;
    const shadbalaPercentage = Math.round(shadbalaRatio * 100);
    const shadbalaRupas = shadbalaDetail?.total_rupas;
    const shadbalaIsStrong = shadbalaDetail?.is_strong ?? (shadbalaRatio >= 1.0);

    // Determine overall strength category
    let dignityType: EvaluatedPlanetSthana["dignity_type"] = "neutral";
    let dignityLabelTa = dignity.labelTa || "சமநிலை";
    let dignityLabelEn = dignity.labelEn || "Neutral";

    if (dignity.isUcham) {
      dignityType = "exalted";
      dignityLabelTa = dignity.isDeepUcham ? "பரம உச்சம்" : "உச்சம் (Exalted)";
      dignityLabelEn = dignity.isDeepUcham ? "Deep Exaltation" : "Exalted";
    } else if (isOwnSign) {
      dignityType = "own_sign";
      dignityLabelTa = "ஆட்சி (Own Sign)";
      dignityLabelEn = "Own Sign";
    } else if (dignity.isDikBala) {
      dignityType = "dikbala";
      dignityLabelTa = "திக்பலம் (Digbala)";
      dignityLabelEn = "Digbala";
    } else if (dignity.isNeecham) {
      dignityType = "debilitated";
      dignityLabelTa = dignity.isDeepNeecham ? "பரம நீசம்" : "நீசம் (Debilitated)";
      dignityLabelEn = dignity.isDeepNeecham ? "Deep Debilitation" : "Debilitated";
    } else if (shadbalaIsStrong) {
      dignityType = "friendly";
      dignityLabelTa = "சுப பலம் (Strong)";
      dignityLabelEn = "Strong Placement";
    }

    const isNetStrong = dignity.isUcham || isOwnSign || dignity.isDikBala || (shadbalaRatio >= 1.05 && !dignity.isNeecham);

    // Find the master prediction entry
    const matchedPrediction = PLANETARY_STHANA_PREDICTIONS.find(
      (p) => p.planet === planetKey && p.house === houseNumber
    );

    if (!matchedPrediction) continue;

    // Use sign_index (1-12) to get sign names
    const signNameTa = planetData.sign_name_tamil || SIGN_NAMES_TA[signIndex - 1] || "";
    const signNameEn = planetData.sign_name || SIGN_NAMES_EN[signIndex - 1] || "";

    // Generate dynamic 1-line highlights
    const statusSummaryTa = `${matchedPrediction.planet_name_ta} லக்னத்திலிருந்து ${houseNumber}-ஆம் பாவத்தில் (${signNameTa} ராசி) ${dignityLabelTa} - ${isNetStrong ? "வலுவான சாதக பலன்கள் கூடும்" : "கவனமும் சமநிலையும் நலம் தரும்"}.`;
    const statusSummaryEn = `${planetKey} in ${houseNumber}th House (${signNameEn}) with ${dignityLabelEn} - ${isNetStrong ? "Manifests positive strengths" : "Requires conscious mindfulness"}.`;

    results.push({
      planet_name: planetKey,
      planet_name_ta: matchedPrediction.planet_name_ta,
      symbol: matchedPrediction.symbol,
      element: matchedPrediction.element,
      house_number: houseNumber,
      house_name_ta: matchedPrediction.house_title_ta,
      house_name_en: matchedPrediction.house_title_en,
      bhava_category: matchedPrediction.bhava_category,
      sign_index: signIndex,
      sign_name_ta: signNameTa,
      sign_name_en: signNameEn,
      degree_in_sign: planetData.degree_in_sign || 0,
      is_retrograde: Boolean(planetData.is_retrograde),
      dignity_label_ta: dignityLabelTa,
      dignity_label_en: dignityLabelEn,
      dignity_type: dignityType,
      shadbala_rupas: shadbalaRupas,
      shadbala_ratio: shadbalaRatio,
      shadbala_percentage: shadbalaPercentage,
      shadbala_is_strong: shadbalaIsStrong,
      is_net_strong: isNetStrong,
      status_summary_ta: statusSummaryTa,
      status_summary_en: statusSummaryEn,
      prediction: matchedPrediction
    });
  }

  return results;
}
"""

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(ts_content)

print(f"Successfully generated {OUTPUT_PATH} ({os.path.getsize(OUTPUT_PATH)} bytes)")
