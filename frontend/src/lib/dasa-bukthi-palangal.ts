/**
 * Vimshottari Dasa Bukthi Palangal Engine (தசா புத்தி பலன்கள்)
 * Based on the classical treatise:
 * "Vimshottari Dasha System - Timings of all possible results of horoscope"
 * by Krishan Kant Bhardwaj.
 *
 * Implements:
 * 1. Auspicious & Inauspicious Dasha evaluation (Shadbala, Ashtakavarga, Dignity, Vargas, Bhavas).
 * 2. Mahadasha-Antardasha Sambandha & Bhavat Bhavam distance (1 to 12) and derived house from Lagna.
 * 3. Rising sign delivery timing (Shirshodaya, Prishtodaya, Ubhayodaya).
 * 4. Specific House rulership manifestations (Lagnesh through Dvadadhesh in 12 houses).
 * 5. Full classical matrix of 9 Mahadashas and 81 Antardashas with tailored predictions.
 * 6. Sun transit manifestation windows and classical Vedic remedies.
 */

import {
  HoroscopeResponse,
  DasaResponse,
  DasaPeriodNode,
  PlanetInfo,
  HouseInfo,
  ShadbalaResponse,
  AshtakavargaResponse,
} from "./types";
import { normalizePlanetName, getPlanetOccupiedHouse, getPlanetOwnedHouses } from "./benefit-bhavas";
import {
  jdToCalendarDateTime,
  calculateCalendarAge,
  formatCalendarAge,
  generateChildSubPeriods,
} from "./dasa-helpers";

// ---------------------------------------------------------------------------
// Types & Interfaces
// ---------------------------------------------------------------------------

export type DignityLevel =
  | "exalted"
  | "moolatrikona"
  | "own_sign"
  | "friendly_sign"
  | "neutral_sign"
  | "enemy_sign"
  | "debilitated";

export type RisingSignType = "shirshodaya" | "prishtodaya" | "ubhayodaya";

export type SambandhaType =
  | "conjunction" // Yuti
  | "mutual_aspect" // Samasaptaka / Drishti
  | "sign_exchange" // Parivartana
  | "aspect_on_sign"
  | "unrelated";

export interface PlanetStrengthProfile {
  planet: string;
  signName: string;
  signIndex: number; // 1-12
  houseOccupied: number; // 1-12
  housesOwned: number[]; // e.g. [4, 9]
  degreeInSign: number;
  isRetrograde: boolean;
  isCombust: boolean;
  isVargottama: boolean;
  dignity: DignityLevel;
  dignityScorePercent: number; // Exalted=100%, Moolatrikona=75%, Own=50%, Friend=25%, Debilitated=0%
  shadbalaRupas?: number;
  shadbalaRequiredRupas?: number;
  shadbalaPass: boolean;
  ashtakavargaBindus: number;
  ashtakavargaStatus: "auspicious" | "normal" | "inauspicious"; // >=5, 4, <4
  taraBala: {
    number: number;
    nameEn: string;
    nameTa: string;
    isAuspicious: boolean;
  };
  avasthaNameEn: string; // Pradeept, Savasth, Shant, Shakt, Deen, Peedit, Kopi, Khal
  avasthaNameTa: string;
  risingSignType: RisingSignType;
  deliveryTimingEn: string; // Beginning, Middle, End, Throughout
  deliveryTimingTa: string;
  isKarakoBhavanasaya: boolean;
  isBadhakesh: boolean;
  isMarakesh: boolean;
}

export interface PeriodRelationshipAnalysis {
  distanceFromMahaToAntar: number; // 1 to 12
  derivedHouseFromLagna: number; // 1 to 12
  sambandha: SambandhaType;
  sambandhaTextEn: string;
  sambandhaTextTa: string;
  relationshipNature: "mutual_friends" | "neutral" | "mutual_enemies" | "mixed";
  relationshipNatureTextEn: string;
  relationshipNatureTextTa: string;
  axisNameEn: string; // e.g. "Navapanchama (5/9)", "Shadashtaka (6/8)", "Dvidvadasa (2/12)", "Samasaptaka (1/7)"
  axisNameTa: string;
  isRajayogaSambandha: boolean;
  isShadashtakaWarning: boolean; // 6/8
  isDvidvadasaWarning: boolean; // 2/12
  isMarakaInfluence: boolean;
  deliveryWindowTextEn: string;
  deliveryWindowTextTa: string;
}

export interface PredictionCategoryBlock {
  titleEn: string;
  titleTa: string;
  iconName: string;
  favorableScore: number; // 0 to 100
  summaryEn: string;
  summaryTa: string;
  pointsEn: string[];
  pointsTa: string[];
}

export interface SunTransitManifestation {
  signsRuledEn: string[];
  signsRuledTa: string[];
  manifestationWindowEn: string;
  manifestationWindowTa: string;
  descriptionEn: string;
  descriptionTa: string;
}

export interface RemedialMeasure {
  deityEn: string;
  deityTa: string;
  mantraEn: string;
  mantraTa: string;
  charityEn: string;
  charityTa: string;
  gemstoneEn: string;
  gemstoneTa: string;
  colorEn: string;
  colorTa: string;
  generalRemedyEn: string;
  generalRemedyTa: string;
}

export interface AndharaItem {
  lord: string;
  startDateIso: string;
  endDateIso: string;
  startDateFormatted: string;
  endDateFormatted: string;
  durationDays: number;
  durationFormatted: string;
  isActiveNow: boolean;
  isPast: boolean;
  isFuture: boolean;
  progressPercent: number;
}

export interface AndharaAnalysisDetail {
  lord: string;
  timing: AndharaItem;
  strength: PlanetStrengthProfile;
  relationshipFromBhukti: PeriodRelationshipAnalysis;
  relationshipFromMaha: PeriodRelationshipAnalysis;
  catalystThemeEn: string;
  catalystThemeTa: string;
  predictionEn: string;
  predictionTa: string;
  eventTriggerFocusEn: string;
  eventTriggerFocusTa: string;
}

export interface DasaBukthiAnalysis {
  mahadashaLord: string;
  antardashaLord: string;
  pratyantardashaLord: string;
  startDateIso: string;
  endDateIso: string;
  startDateFormatted: string;
  endDateFormatted: string;
  durationYearsFormatted: string;
  ageAtStartFormatted: string;
  ageAtEndFormatted: string;
  isActiveNow: boolean;
  isPast: boolean;
  isFuture: boolean;
  progressPercent: number; // 0 to 100 if active
  overallAuspiciousScore: number; // 0 to 100 (matches active mode: Dasa-Bukthi or Dasa-Bukthi-Andhara)
  dasaBukthiPositiveScore: number; // Dasa + Bukthi alone (2-level calculation, 0-100)
  dasaBukthiNegativeScore: number; // 100 - dasaBukthiPositiveScore
  andharaPositiveScore: number; // Dasa + Bukthi + Andhara (3-level calculation, 0-100)
  andharaNegativeScore: number; // 100 - andharaPositiveScore
  keyPositivePointsEn: string[];
  keyPositivePointsTa: string[];
  keyCautionPointsEn: string[];
  keyCautionPointsTa: string[];
  bhavaSignificationsEn: string[];
  bhavaSignificationsTa: string[];
  verdictLabelEn: "Highly Auspicious" | "Favorable" | "Mixed / Average" | "Challenging" | "Sensitive / Precautions Required";
  verdictLabelTa: "மிகவும் சுபகரமானது" | "அனுகூலமான காலம்" | "சம பலன் / கலப்பு பலன்" | "கவனமுடன் இருக்க வேண்டிய காலம்" | "கண்ட காலம் / சாந்தி தேவை";
  verdictBadgeClass: string;
  summaryQuoteEn: string;
  summaryQuoteTa: string;
  mahaStrength: PlanetStrengthProfile;
  antarStrength: PlanetStrengthProfile;
  relationship: PeriodRelationshipAnalysis;
  andhara: AndharaAnalysisDetail;
  availableAndharas: AndharaItem[];
  categories: {
    general: PredictionCategoryBlock;
    career: PredictionCategoryBlock;
    wealth: PredictionCategoryBlock;
    marriage: PredictionCategoryBlock;
    educationChildren: PredictionCategoryBlock;
    healthMaraka: PredictionCategoryBlock;
  };
  sunTransit: SunTransitManifestation;
  remedies: RemedialMeasure;
  classicalCitation: string;
}

// ---------------------------------------------------------------------------
// Constants & Classical Tables from Krishan Kant Bhardwaj
// ---------------------------------------------------------------------------

export const ZODIAC_SIGNS_EN = [
  "Aries", "Taurus", "Gemini", "Cancer",
  "Leo", "Virgo", "Libra", "Scorpio",
  "Sagittarius", "Capricorn", "Aquarius", "Pisces"
];

export const ZODIAC_SIGNS_TA = [
  "மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்",
  "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்",
  "தனுசு", "மகரம்", "கும்பம்", "மீனம்"
];

// Shirshodaya, Prishtodaya, Ubhayodaya classification (Chapter 2, Rule 1)
// Shirshodaya: Gemini (3), Leo (5), Virgo (6), Libra (7), Scorpio (8), Aquarius (11) -> beginning of dasha
// Prishtodaya: Aries (1), Taurus (2), Cancer (4), Sagittarius (9), Capricorn (10) -> end of dasha
// Ubhayodaya: Pisces (12) -> entire period
export const SHIRSHODAYA_SIGNS = [3, 5, 6, 7, 8, 11];
export const PRISHTODAYA_SIGNS = [1, 2, 4, 9, 10];
export const UBHAYODAYA_SIGNS = [12];

// Classical Shadbala requirements in Rupas (Chapter 1, Rule 1)
export const SHADBALA_REQUIRED_RUPAS: Record<string, number> = {
  Sun: 6.5,
  Moon: 6.0,
  Mars: 5.0,
  Mercury: 7.0,
  Jupiter: 6.0,
  Venus: 5.0,
  Saturn: 5.0,
  Rahu: 5.5,
  Ketu: 5.5,
};

// Exaltation & Debilitation signs (1-indexed)
export const EXALTATION_SIGNS: Record<string, { sign: number; degree: number }> = {
  Sun: { sign: 1, degree: 10 }, // Aries 10°
  Moon: { sign: 2, degree: 3 }, // Taurus 3°
  Mars: { sign: 10, degree: 28 }, // Capricorn 28°
  Mercury: { sign: 6, degree: 15 }, // Virgo 15°
  Jupiter: { sign: 4, degree: 5 }, // Cancer 5°
  Venus: { sign: 12, degree: 27 }, // Pisces 27°
  Saturn: { sign: 7, degree: 20 }, // Libra 20°
  Rahu: { sign: 2, degree: 15 }, // Taurus / Gemini
  Ketu: { sign: 8, degree: 15 }, // Scorpio / Sagittarius
};

export const DEBILITATION_SIGNS: Record<string, { sign: number; degree: number }> = {
  Sun: { sign: 7, degree: 10 }, // Libra 10°
  Moon: { sign: 8, degree: 3 }, // Scorpio 3°
  Mars: { sign: 4, degree: 28 }, // Cancer 28°
  Mercury: { sign: 12, degree: 15 }, // Pisces 15°
  Jupiter: { sign: 10, degree: 5 }, // Capricorn 5°
  Venus: { sign: 6, degree: 27 }, // Virgo 27°
  Saturn: { sign: 1, degree: 20 }, // Aries 20°
  Rahu: { sign: 8, degree: 15 }, // Scorpio
  Ketu: { sign: 2, degree: 15 }, // Taurus
};

export const MOOLATRIKONA_SIGNS: Record<string, { sign: number; fromDeg: number; toDeg: number }> = {
  Sun: { sign: 5, fromDeg: 0, toDeg: 20 },
  Moon: { sign: 2, fromDeg: 3, toDeg: 30 },
  Mars: { sign: 1, fromDeg: 0, toDeg: 12 },
  Mercury: { sign: 6, fromDeg: 15, toDeg: 20 },
  Jupiter: { sign: 9, fromDeg: 0, toDeg: 10 },
  Venus: { sign: 7, fromDeg: 0, toDeg: 15 },
  Saturn: { sign: 11, fromDeg: 0, toDeg: 20 },
};

export const SIGNS_OWNED: Record<string, number[]> = {
  Sun: [5],
  Moon: [4],
  Mars: [1, 8],
  Mercury: [3, 6],
  Jupiter: [9, 12],
  Venus: [2, 7],
  Saturn: [10, 11],
  Rahu: [],
  Ketu: [],
};

// Natural friendships (Naisargika Mitra)
export const NATURAL_FRIENDS: Record<string, string[]> = {
  Sun: ["Moon", "Mars", "Jupiter"],
  Moon: ["Sun", "Mercury"],
  Mars: ["Sun", "Moon", "Jupiter"],
  Mercury: ["Sun", "Venus"],
  Jupiter: ["Sun", "Moon", "Mars"],
  Venus: ["Mercury", "Saturn"],
  Saturn: ["Mercury", "Venus"],
  Rahu: ["Venus", "Saturn", "Mercury"],
  Ketu: ["Mars", "Venus", "Jupiter"],
};

export const NATURAL_ENEMIES: Record<string, string[]> = {
  Sun: ["Venus", "Saturn", "Rahu", "Ketu"],
  Moon: ["Rahu", "Ketu"],
  Mars: ["Mercury", "Rahu"],
  Mercury: ["Moon"],
  Jupiter: ["Mercury", "Venus"],
  Venus: ["Sun", "Moon"],
  Saturn: ["Sun", "Moon", "Mars"],
  Rahu: ["Sun", "Moon", "Mars"],
  Ketu: ["Sun", "Moon"],
};

// Tara Bala names from Janma Nakshatra
export const TARA_BALA_LIST = [
  { num: 1, en: "Janma (Birth/Body)", ta: "ஜன்ம தாரை (உடல்/மனம்)", good: true },
  { num: 2, en: "Sampat (Wealth & Prosperity)", ta: "சம்பத்து தாரை (தன லாபம்)", good: true },
  { num: 3, en: "Vipat (Danger & Obstacles)", ta: "விபத்து தாரை (தடைகள்)", good: false },
  { num: 4, en: "Kshema (Well-being & Safety)", ta: "சேம தாரை (சுகம் & பாதுகாப்பு)", good: true },
  { num: 5, en: "Pratyari (Opposition & Delays)", ta: "பிரத்யரி தாரை (எதிர்ப்பு)", good: false },
  { num: 6, en: "Sadhaka (Accomplishment)", ta: "சாதக தாரை (வெற்றி & காரியசித்தி)", good: true },
  { num: 7, en: "Vadha (Lethal / Severe Strain)", ta: "வத தாரை (கண்டம் & சிரமம்)", good: false },
  { num: 8, en: "Maitra (Friendship & Harmony)", ta: "மைத்ர தாரை (நட்பு & ஆதரவு)", good: true },
  { num: 9, en: "Parama Maitra (Great Fortune)", ta: "பரம மைத்ர தாரை (பேரின்பம் & யோகம்)", good: true },
];

// Maraka planets per Ascendant according to Maharishi Parashara (Chapter 11)
export const PARASHARA_MARAKAS: Record<number, string[]> = {
  1: ["Venus"], // Aries
  2: ["Jupiter", "Moon", "Mars"], // Taurus
  3: ["Mars", "Moon"], // Gemini
  4: ["Saturn"], // Cancer
  5: ["Saturn", "Mercury"], // Leo
  6: ["Mars"], // Virgo
  7: ["Mars", "Jupiter"], // Libra
  8: ["Venus", "Mercury", "Saturn"], // Scorpio
  9: ["Venus", "Saturn"], // Sagittarius
  10: ["Mars"], // Capricorn
  11: ["Jupiter", "Sun", "Mars"], // Aquarius
  12: ["Mercury", "Saturn"], // Pisces
};

// ---------------------------------------------------------------------------
// Helper Evaluation Functions
// ---------------------------------------------------------------------------

export function getDignity(planetName: string, signIndex: number, degInSign: number): DignityLevel {
  const norm = normalizePlanetName(planetName);
  if (EXALTATION_SIGNS[norm]?.sign === signIndex) return "exalted";
  if (DEBILITATION_SIGNS[norm]?.sign === signIndex) return "debilitated";

  const mt = MOOLATRIKONA_SIGNS[norm];
  if (mt && mt.sign === signIndex && degInSign >= mt.fromDeg && degInSign <= mt.toDeg) {
    return "moolatrikona";
  }

  const owned = SIGNS_OWNED[norm] || [];
  if (owned.includes(signIndex)) return "own_sign";

  const friends = NATURAL_FRIENDS[norm] || [];
  const enemies = NATURAL_ENEMIES[norm] || [];

  // Determine sign lord
  const signLords = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"];
  const signLord = signLords[signIndex - 1];

  if (friends.includes(signLord)) return "friendly_sign";
  if (enemies.includes(signLord)) return "enemy_sign";
  return "neutral_sign";
}

export function evaluatePlanetStrength(
  planetName: string,
  horoscope: HoroscopeResponse,
  shadbala?: ShadbalaResponse,
  ashtakavarga?: AshtakavargaResponse,
  birthNakshatraIndex: number = 0
): PlanetStrengthProfile {
  const norm = normalizePlanetName(planetName);
  const planetInfo = horoscope.planets.find((p) => normalizePlanetName(p.name) === norm);
  const sunInfo = horoscope.planets.find((p) => normalizePlanetName(p.name) === "Sun");
  const ascSign = horoscope.ascendant.sign_index;

  const signIndex = planetInfo ? planetInfo.sign_index : 1;
  const degreeInSign = planetInfo ? planetInfo.degree_in_sign : 0;
  const isRetrograde = planetInfo ? !!planetInfo.is_retrograde : false;

  // Combustion check
  let isCombust = false;
  if (sunInfo && planetInfo && norm !== "Sun" && norm !== "Rahu" && norm !== "Ketu") {
    const diff = Math.abs((planetInfo.longitude - sunInfo.longitude + 360) % 360);
    const angularDiff = diff > 180 ? 360 - diff : diff;
    const orb = norm === "Venus" ? 10 : norm === "Mercury" ? 14 : norm === "Moon" ? 12 : 8.5;
    isCombust = angularDiff <= orb;
  }

  // House occupied & owned
  const houseOccupied = planetInfo
    ? getPlanetOccupiedHouse(planetInfo.longitude, horoscope.houses.map((h) => h.cusp_degree), ascSign) || 1
    : 1;
  const housesOwned = getPlanetOwnedHouses(norm, ascSign);

  // Dignity
  const dignity = getDignity(norm, signIndex, degreeInSign);
  let dignityScorePercent = 50;
  if (dignity === "exalted") dignityScorePercent = 100;
  else if (dignity === "moolatrikona") dignityScorePercent = 75;
  else if (dignity === "own_sign") dignityScorePercent = 60;
  else if (dignity === "friendly_sign") dignityScorePercent = 45;
  else if (dignity === "neutral_sign") dignityScorePercent = 35;
  else if (dignity === "enemy_sign") dignityScorePercent = 20;
  else if (dignity === "debilitated") dignityScorePercent = 5;

  // Vargottama check (Chapter 1, Rule 7)
  let isVargottama = false;
  if (horoscope.varga_d1_d9?.planets) {
    const vp = horoscope.varga_d1_d9.planets.find(
      (p) => normalizePlanetName(p.name) === norm
    );
    if (vp) {
      isVargottama = vp.d1_sign_index === vp.d9_sign_index;
    }
  } else if (planetInfo) {
    // Navamsha sign calculation if varga_d1_d9 is not pre-calculated:
    // Fire signs (1, 5, 9) start from Aries (1)
    // Earth signs (2, 6, 10) start from Capricorn (10)
    // Air signs (3, 7, 11) start from Libra (7)
    // Water signs (4, 8, 12) start from Cancer (4)
    const padaInSign = Math.floor(planetInfo.degree_in_sign / (30.0 / 9.0));
    const elementStarts = [1, 10, 7, 4];
    const elStart = elementStarts[(planetInfo.sign_index - 1) % 4];
    const d9Sign = ((elStart - 1 + padaInSign) % 12) + 1;
    isVargottama = d9Sign === planetInfo.sign_index;
  }

  // Shadbala check
  let shadbalaRupas: number | undefined = undefined;
  let shadbalaPass = true;
  const reqRupas = SHADBALA_REQUIRED_RUPAS[norm] || 5.0;
  if (shadbala?.planets) {
    const sDetail = shadbala.planets.find((p) => normalizePlanetName(p.planet) === norm);
    if (sDetail) {
      shadbalaRupas = sDetail.total_rupas;
      shadbalaPass = sDetail.total_rupas >= reqRupas;
    }
  }

  // Ashtakavarga Bindus in current sign/house
  let ashtakavargaBindus = 4;
  if (ashtakavarga?.bhinnashtakavarga) {
    const bDetail = ashtakavarga.bhinnashtakavarga[norm];
    if (bDetail?.house_bindus) {
      ashtakavargaBindus = bDetail.house_bindus[String(houseOccupied)] ?? 4;
    } else if (bDetail?.sign_bindus) {
      const sName = ZODIAC_SIGNS_EN[signIndex - 1];
      ashtakavargaBindus = bDetail.sign_bindus[sName] ?? 4;
    }
  }
  const ashtakavargaStatus: "auspicious" | "normal" | "inauspicious" =
    ashtakavargaBindus >= 5 ? "auspicious" : ashtakavargaBindus === 4 ? "normal" : "inauspicious";

  // Tara Bala calculation
  let taraNumber = 1;
  if (planetInfo?.nakshatra?.index !== undefined && birthNakshatraIndex > 0) {
    const diff = (planetInfo.nakshatra.index - birthNakshatraIndex + 27) % 27;
    taraNumber = (diff % 9) + 1;
  }
  const tbObj = TARA_BALA_LIST[taraNumber - 1] || TARA_BALA_LIST[0];

  // Avastha classification (Chapter 3)
  let avasthaEn = "Shant (Peaceful)";
  let avasthaTa = "சாந்த நிலை (அமைதி & நல்லிணக்கம்)";
  if (dignity === "exalted") {
    avasthaEn = "Pradeept / Garvit (Illuminated & Proud)";
    avasthaTa = "பிரதீப்த / கர்வ நிலை (முழு சுபத்தன்மை)";
  } else if (dignity === "own_sign" || dignity === "moolatrikona") {
    avasthaEn = "Savasth (Healthy & Content)";
    avasthaTa = "சுவஸ்த நிலை (ஆரோக்கியம் & வளர்ச்சி)";
  } else if (isCombust) {
    avasthaEn = "Kopi / Kshobhit (Agitated & Combust)";
    avasthaTa = "கோபி / சோபித நிலை (அஸ்தங்க வெப்பம்)";
  } else if (dignity === "debilitated") {
    avasthaEn = "Deen (Miserable & Weak)";
    avasthaTa = "தீன நிலை (பலவீனம் & சோதனைகள்)";
  } else if (dignity === "enemy_sign") {
    avasthaEn = "Peedit / Kshudhit (Afflicted & Distressed)";
    avasthaTa = "பீடித்த நிலை (சிரமம் & அலைச்சல்)";
  }

  // Rising Sign delivery timing (Chapter 2, Rule 1)
  let risingSignType: RisingSignType = "prishtodaya";
  let deliveryTimingEn = "End of Dasha period (Prishtodaya)";
  let deliveryTimingTa = "தசையின் இறுதிப் பகுதியில் பலன்கள் (பிருஷ்டோதய ராசி)";
  if (SHIRSHODAYA_SIGNS.includes(signIndex)) {
    risingSignType = "shirshodaya";
    deliveryTimingEn = "Beginning of Dasha period (Shirshodaya)";
    deliveryTimingTa = "தசையின் ஆரம்பப் பகுதியில் விரைவான பலன்கள் (சீர்ஷோதய ராசி)";
  } else if (UBHAYODAYA_SIGNS.includes(signIndex)) {
    risingSignType = "ubhayodaya";
    deliveryTimingEn = "Evenly distributed throughout the Dasha (Ubhayodaya)";
    deliveryTimingTa = "தசா காலம் முழுவதும் சமமாகப் பரவிய பலன்கள் (உபயோதய ராசி)";
  }

  // Karako Bhavanasaya check
  const isKarakoBhavanasaya =
    (norm === "Jupiter" && (houseOccupied === 2 || houseOccupied === 5)) ||
    (norm === "Sun" && houseOccupied === 9) ||
    (norm === "Venus" && houseOccupied === 7) ||
    (norm === "Mars" && houseOccupied === 3);

  // Badhakesh check
  let isBadhakesh = false;
  if ([1, 4, 7, 10].includes(ascSign)) {
    // Chara (Movable): 11th lord is Badhaka
    const badhakaSigns = [(ascSign + 10 - 1) % 12 + 1];
    isBadhakesh = housesOwned.some((h) => h === 11);
  } else if ([2, 5, 8, 11].includes(ascSign)) {
    // Sthira (Fixed): 9th lord is Badhaka
    isBadhakesh = housesOwned.some((h) => h === 9);
  } else if ([3, 6, 9, 12].includes(ascSign)) {
    // Ubhaya (Dual): 7th lord is Badhaka
    isBadhakesh = housesOwned.some((h) => h === 7);
  }

  // Marakesh check
  const marakaPlanets = PARASHARA_MARAKAS[ascSign] || [];
  const isMarakesh = marakaPlanets.includes(norm) || housesOwned.includes(2) || housesOwned.includes(7);

  return {
    planet: norm,
    signName: ZODIAC_SIGNS_EN[signIndex - 1],
    signIndex,
    houseOccupied,
    housesOwned,
    degreeInSign,
    isRetrograde,
    isCombust,
    isVargottama,
    dignity,
    dignityScorePercent,
    shadbalaRupas,
    shadbalaRequiredRupas: reqRupas,
    shadbalaPass,
    ashtakavargaBindus,
    ashtakavargaStatus,
    taraBala: {
      number: tbObj.num,
      nameEn: tbObj.en,
      nameTa: tbObj.ta,
      isAuspicious: tbObj.good,
    },
    avasthaNameEn: avasthaEn,
    avasthaNameTa: avasthaTa,
    risingSignType,
    deliveryTimingEn,
    deliveryTimingTa,
    isKarakoBhavanasaya,
    isBadhakesh,
    isMarakesh,
  };
}

export function evaluatePeriodRelationship(
  maha: PlanetStrengthProfile,
  antar: PlanetStrengthProfile,
  ascSign: number
): PeriodRelationshipAnalysis {
  // Distance from Maha lord's sign to Antar lord's sign (1-12)
  const distanceFromMahaToAntar = ((antar.signIndex - maha.signIndex + 12) % 12) + 1;

  // Derived house counted from Lagna (Chapter 1, Rule 12):
  // "Count the distance of houses of lord of Antardasha from lord of Mahadasha.
  // Now count that number of houses from Lagna -> results of that house manifest!"
  const derivedHouseFromLagna = distanceFromMahaToAntar;

  // Sambandha Evaluation
  let sambandha: SambandhaType = "unrelated";
  let sambandhaTextEn = "Independent / Neutral Axis";
  let sambandhaTextTa = "தனித்த நிலை / நேரடி சேர்க்கையற்ற அமைப்பு";

  if (maha.signIndex === antar.signIndex) {
    sambandha = "conjunction";
    sambandhaTextEn = "Conjunction in the same house (Yuti)";
    sambandhaTextTa = "ஒரே ராசியில் இணைவு (யுதி சம்பந்தம்)";
  } else if (distanceFromMahaToAntar === 7) {
    sambandha = "mutual_aspect";
    sambandhaTextEn = "Mutual 7th Aspect (Samasaptaka Drishti)";
    sambandhaTextTa = "நேர் எதிரே 7-ஆம் பார்வை (சமசப்தக சம்பந்தம்)";
  } else if (
    maha.housesOwned.some((h) => antar.housesOwned.includes(h)) ||
    (SIGNS_OWNED[maha.planet]?.includes(antar.signIndex) && SIGNS_OWNED[antar.planet]?.includes(maha.signIndex))
  ) {
    sambandha = "sign_exchange";
    sambandhaTextEn = "Mutual Sign Exchange (Parivartana Yoga)";
    sambandhaTextTa = "பரிவர்த்தனை யோகம் (வீடு மாறி அமர்ந்த நிலை)";
  }

  // Axis naming
  let axisNameEn = `${distanceFromMahaToAntar}th House Disposition`;
  let axisNameTa = `${distanceFromMahaToAntar}-ஆம் இடம் தொடர்பு`;
  const isShadashtakaWarning = distanceFromMahaToAntar === 6 || distanceFromMahaToAntar === 8;
  const isDvidvadasaWarning = distanceFromMahaToAntar === 2 || distanceFromMahaToAntar === 12;

  if (distanceFromMahaToAntar === 1) {
    axisNameEn = "1/1 Conjunction (Sama Bhavana)";
    axisNameTa = "1/1 ஒரே ராசி சேர்க்கை (சம பாவகம்)";
  } else if (distanceFromMahaToAntar === 5 || distanceFromMahaToAntar === 9) {
    axisNameEn = "5/9 Navapanchama (Trikona Auspicious Axis)";
    axisNameTa = "5/9 நவபஞ்சம யோக அச்சு (திரிகோண சுப நிலை)";
  } else if (isShadashtakaWarning) {
    axisNameEn = "6/8 Shadashtaka (Adverse Obstacle Axis)";
    axisNameTa = "6/8 ஷடாஷ்டக அச்சு (சிரமம் & தற்காலிக தடைகள்)";
  } else if (isDvidvadasaWarning) {
    axisNameEn = "2/12 Dvidvadasa (Financial & Expense Axis)";
    axisNameTa = "2/12 துவிதவாதச அச்சு (விரயம் & தன பரிவர்த்தனை)";
  } else if (distanceFromMahaToAntar === 3 || distanceFromMahaToAntar === 11) {
    axisNameEn = "3/11 Upachaya Axis (Gains through Effort)";
    axisNameTa = "3/11 உபசய அச்சு (முயற்சி வழி தன லாபம்)";
  } else if (distanceFromMahaToAntar === 4 || distanceFromMahaToAntar === 10) {
    axisNameEn = "4/10 Kendra Axis (Status, Home & Career)";
    axisNameTa = "4/10 கேந்திர அச்சு (அந்தஸ்து, வீடு & உத்தியோகம்)";
  } else if (distanceFromMahaToAntar === 7) {
    axisNameEn = "1/7 Samasaptaka (Direct Partnership Axis)";
    axisNameTa = "1/7 சமசப்தக அச்சு (நேரடி கூட்டு & இல்லறம்)";
  }

  // Mutual Friendship
  const mahaFriends = NATURAL_FRIENDS[maha.planet] || [];
  const mahaEnemies = NATURAL_ENEMIES[maha.planet] || [];
  let relationshipNature: "mutual_friends" | "neutral" | "mutual_enemies" | "mixed" = "neutral";
  let relationshipNatureTextEn = "Neutral Harmony";
  let relationshipNatureTextTa = "சம நிலை தொடர்பு";

  if (mahaFriends.includes(antar.planet)) {
    relationshipNature = "mutual_friends";
    relationshipNatureTextEn = "Harmonious Natural Friendship (Mitra)";
    relationshipNatureTextTa = "சுப நட்பு கிரகம் (மித்ர சம்பந்தம்)";
  } else if (mahaEnemies.includes(antar.planet)) {
    relationshipNature = "mutual_enemies";
    relationshipNatureTextEn = "Inimical Natural Relationship (Shatru)";
    relationshipNatureTextTa = "பகை கிரக தொடர்பு (சத்ரு சம்பந்தம்)";
  } else {
    relationshipNature = "mixed";
    relationshipNatureTextEn = "Moderate / Mixed Disposition";
    relationshipNatureTextTa = "மத்தியம / கலப்பு தொடர்பு";
  }

  // Kendra - Trikona Raja Yoga relationship (Chapter 1, Rule 3 & 13)
  const isMahaKendra = maha.housesOwned.some((h) => [1, 4, 7, 10].includes(h));
  const isMahaTrikona = maha.housesOwned.some((h) => [1, 5, 9].includes(h));
  const isAntarKendra = antar.housesOwned.some((h) => [1, 4, 7, 10].includes(h));
  const isAntarTrikona = antar.housesOwned.some((h) => [1, 5, 9].includes(h));

  const isRajayogaSambandha =
    sambandha !== "unrelated" &&
    ((isMahaKendra && isAntarTrikona) || (isMahaTrikona && isAntarKendra));

  // Maraka check (Chapter 11)
  const isMarakaInfluence =
    (maha.isMarakesh && antar.housesOwned.some((h) => [2, 7, 6, 8, 12].includes(h))) ||
    (antar.isMarakesh && maha.housesOwned.some((h) => [2, 7, 6, 8, 12].includes(h)));

  // Delivery Window text
  const deliveryWindowTextEn =
    antar.risingSignType === "shirshodaya"
      ? "Peak manifestation occurs in the first third of this Antardasha period (Shirshodaya Rashi)."
      : antar.risingSignType === "ubhayodaya"
      ? "Results distribute steadily throughout this Antardasha period (Ubhayodaya Rashi)."
      : "Major events materialize in the final third and culmination of this Antardasha (Prishtodaya Rashi).";

  const deliveryWindowTextTa =
    antar.risingSignType === "shirshodaya"
      ? "இந்த புக்தியின் ஆரம்ப 3-ல் 1 பங்கு காலத்திலேயே முக்கிய பலன்கள் விரையமாக வெளிப்படும் (சீர்ஷோதய ராசி)."
      : antar.risingSignType === "ubhayodaya"
      ? "இந்த புக்தி காலம் முழுவதும் பலன்கள் சமச்சீராகவும் சீராகவும் தொடர்ந்து நடக்கும் (உபயோதய ராசி)."
      : "இந்த புக்தியின் இறுதிப் பகுதியில் முக்கிய நன்மைகளும் திருப்புமுனைகளும் முழுமையாகக் கைகூடும் (பிருஷ்டோதய ராசி).";

  return {
    distanceFromMahaToAntar,
    derivedHouseFromLagna,
    sambandha,
    sambandhaTextEn,
    sambandhaTextTa,
    relationshipNature,
    relationshipNatureTextEn,
    relationshipNatureTextTa,
    axisNameEn,
    axisNameTa,
    isRajayogaSambandha,
    isShadashtakaWarning,
    isDvidvadasaWarning,
    isMarakaInfluence,
    deliveryWindowTextEn,
    deliveryWindowTextTa,
  };
}

// ---------------------------------------------------------------------------
// Mantreswara's Phaladeepika (Adhyaya 20) Bhava Lord Influence Generator
// ---------------------------------------------------------------------------

export function getPhaladeepikaBhavaEffects(
  houses: number[],
  planet: string,
  dignity: DignityLevel
): { en: string[]; ta: string[] } {
  const en: string[] = [];
  const ta: string[] = [];

  const BHAVA_DESCRIPTIONS: Record<number, { en: string; ta: string }> = {
    1: {
      en: "Lagnesha (1st Lord): Bestows physical vitality, self-confidence, societal respect, personal charisma, and overall life advancement (Phaladeepika Ch. 20).",
      ta: "லக்னாதிபதி பலன்: உடல் ஆரோக்கியம், தேக காந்தி, சமூகத்தில் உயரிய கௌரவம், நன்மதிப்பு மற்றும் ஆளுமைத் திறன் மேலோங்கும் (பலதீபிகை அத்தியாயம் 20).",
    },
    2: {
      en: "Dhanesha (2nd Lord): Accelerates financial accumulation, liquid savings, acquisition of precious articles, sweet speech, and auspicious domestic celebrations.",
      ta: "இரண்டாம் அதிபதி பலன்: குடும்பத்தில் மகிழ்ச்சி, தன வரவு, சேமிப்பு பெருகுதல், சொல்வாக்கு கூடுதல் மற்றும் சுப காரிய செலவுகள் நடைபெறும்.",
    },
    3: {
      en: "Bhratresha (3rd Lord): Boosts courageous initiatives, support and coordination with younger siblings, short journeys, communication wins, and enterprising contracts.",
      ta: "மூன்றாம் அதிபதி பலன்: தைரிய வீரியம், புதிய முயற்சிகளில் வெற்றி, சகோதர ஆதரவு, பிரயாணங்கள் மற்றும் ஒப்பந்தங்களில் ஆதாயம் கிட்டும்.",
    },
    4: {
      en: "Sukhesha (4th Lord): Brings domestic tranquility, maternal happiness, acquisition of vehicles, landed property or renovations, and higher academic success.",
      ta: "நான்காம் அதிபதி பலன்: சுக போக வாழ்வு, தாய்வழி ஆதரவு, வாகன யோகம், நிலம் அல்லது வீடு வாங்கும் பாக்கியம் மற்றும் மன நிம்மதி கூடும்.",
    },
    5: {
      en: "Putresha (5th Lord): Activates Purva Punya, children's success, creative brilliance, strategic investments, intuitive intellect, and spiritual merits.",
      ta: "ஐந்தாம் அதிபதி பலன்: பூர்வ புண்ணிய பலன்கள், புத்திர பாக்கியம் அல்லது குழந்தைகளின் வளர்ச்சி, புத்தி சாதுரியம் மற்றும் யோக யோசனைகள் கைகூடும்.",
    },
    6: {
      en: "Satresha (6th Lord): Mastery over competitors, favorable resolution of disputes, debt clearance; disciplined lifestyle prevents digestive or inflammatory ailments.",
      ta: "ஆறாம் அதிபதி பலன்: எதிரிகள் மற்றும் போட்டிகளில் வெற்றி, கடன் சுமைகள் குறையும் வாய்ப்பு; உணவுப் பழக்கங்களில் எச்சரிக்கையால் உடல் நலம் பேணப்படும்.",
    },
    7: {
      en: "Kalatresha (7th Lord): Fosters matrimonial prospects, cordial conjugal partnership, success in commercial negotiations, client relationships, and public interactions.",
      ta: "ஏழாம் அதிபதி பலன்: திருமண சுபகாரியங்கள், இல்லற சுகம், கூட்டுத் தொழிலில் நல்ல லாபம், வாடிக்கையாளர் ஆதரவு மற்றும் நற்பெயர் வளரும்.",
    },
    8: {
      en: "Randhresha (8th Lord): Governs transformative life shifts, research breakthroughs, ancestral inheritances, insurance payouts, and deep longevity safeguards.",
      ta: "எட்டாம் அதிபதி பலன்: எதிர்பாராத திடீர் மாற்றங்கள், ஆயுள் பலம், மறைமுக தன வரவு அல்லது பரம்பரைச் சொத்து விவகாரங்களில் தெளிவு ஏற்படும்.",
    },
    9: {
      en: "Bhagyesha (9th Lord): High fortune (Bhagya Vriddhi), divine pilgrimages, father's prosperity, charitable inclinations, and righteous mentorship.",
      ta: "ஒன்பதாம் அதிபதி பலன்: பாக்கிய விருத்தி, தந்தை மற்றும் குருமார்களின் ஆசிகள், புண்ணிய ஸ்தல யாத்திரைகள் மற்றும் தெய்வ அனுகூலம் உச்சம் பெறும்.",
    },
    10: {
      en: "Karmesha (10th Lord): Professional zenith, promotions, government or corporate honor, executive authority, entrepreneurship, and enduring community status.",
      ta: "பத்தாம் அதிபதி பலன்: தொழில் மேன்மை, புதிய வேலைவாய்ப்பு, உயர் பதவி, அதிகாரிகளிடம் நன்மதிப்பு மற்றும் சமுதாய அந்தஸ்து சிறக்கும்.",
    },
    11: {
      en: "Labhesha (11th Lord): Supreme gains (Sarva Labha), multiple income streams, fulfillment of long-held desires, and prosperous alliances with elder siblings.",
      ta: "பதினொன்றாம் அதிபதி பலன்: சகல லாபங்கள், புதிய வழிகளில் வருமானம், எண்ணிய ஆசைகள் நிறைவேறுதல் மற்றும் மூத்த சகோதரர்களின் உதவிகள் கிடைக்கும்.",
    },
    12: {
      en: "Vyayesha (12th Lord): Foreign journeys, spiritual detachment, investment in lasting sanctuaries, meditation, and redirection towards noble philanthropic causes.",
      ta: "பன்னிரண்டாம் அதிபதி பலன்: தூரதேச அல்லது வெளிநாட்டுப் பயணம், ஆன்மீக ஈடுபாடு, சுப விரயங்கள் மற்றும் தான தர்மங்களில் ஆர்வம் கூடும்.",
    },
  };

  for (const h of houses) {
    if (BHAVA_DESCRIPTIONS[h]) {
      en.push(BHAVA_DESCRIPTIONS[h].en);
      ta.push(BHAVA_DESCRIPTIONS[h].ta);
    }
  }

  return { en, ta };
}

// ---------------------------------------------------------------------------
// Classical Dasha-Bhukti Prediction Matrix (Krishan Kant Bhardwaj)
// ---------------------------------------------------------------------------

interface ClassicalCombinationData {
  summaryQuoteEn: string;
  summaryQuoteTa: string;
  generalEn: string;
  generalTa: string;
  careerEn: string;
  careerTa: string;
  wealthEn: string;
  wealthTa: string;
  marriageEn: string;
  marriageTa: string;
  educationEn: string;
  educationTa: string;
  healthEn: string;
  healthTa: string;
  remedyMantraEn: string;
  remedyMantraTa: string;
  remedyCharityEn: string;
  remedyCharityTa: string;
}

// Helper to construct classical combination predictions based on Chapters 16-24
export function getClassicalCombinationText(
  maha: string,
  antar: string,
  rel: PeriodRelationshipAnalysis,
  mahaP: PlanetStrengthProfile,
  antarP: PlanetStrengthProfile
): ClassicalCombinationData {
  const isAuspicious =
    (mahaP.shadbalaPass && antarP.shadbalaPass && !rel.isShadashtakaWarning && antarP.ashtakavargaBindus >= 4) ||
    rel.isRajayogaSambandha;

  const key = `${maha}-${antar}`;

  // Default rich Vedic interpretations drawn directly from Chapters 16 to 24 of Krishan Kant Bhardwaj
  const baseTexts: Record<string, Partial<ClassicalCombinationData>> = {
    "Sun-Sun": {
      summaryQuoteEn: "Awakening of vitality, authority, royal recognition, and father's support.",
      summaryQuoteTa: "ஆத்ம பலம், அரசு அனுகூலம், தந்தையின் ஆதரவு மற்றும் தலைமைப் பதவி யோகம்.",
      generalEn: "In the Antardasha of Sun within Sun Mahadasha, dignity, self-confidence, and social respect expand remarkably. If the Sun is well placed in own, friendly or exalted sign, government favors and executive leadership flourish.",
      generalTa: "சூரிய மகா திசையில் சூரிய புக்தி நடக்கும் காலத்தில் ஆத்ம தைரியம், கௌரவம் மற்றும் சமூக அந்தஸ்து உயரும். சூரியன் ஆட்சி அல்லது உச்சம் பெற்று பலமுடன் இருப்பின் அரசு வழியில் பெருமையும் கௌரவப் பதவிகளும் தேடி வரும்.",
      careerEn: "Promotions in administrative or state sectors, recognition from superiors, and expansion of official command.",
      careerTa: "அரசு வேலை, உயர் பதவிகள், நிர்வாகப் பொறுப்புகள் மற்றும் மேலதிகாரிகளின் பாராட்டுக்கள் சிறப்பாக அமையும்.",
      wealthEn: "Gains through father's assets, state contracts, gold, and leadership enterprises. Beware of sudden tax or bureaucratic scrutiny if afflicted.",
      wealthTa: "தந்தை வழிச் சொத்து, அரசு மானியம், தங்கம் மற்றும் நிர்வாக முயற்சிகள் வழியே தன லாபம் உண்டாகும்.",
      marriageEn: "Ego clashes or minor warmth in domestic affairs; mutual respect restores harmony when dealt with patience.",
      marriageTa: "குடும்பத்தில் அதிகார தொனி அல்லது சிறு ஈகோ முரண்பாடுகள் வரலாம்; விட்டுக் கொடுத்துச் செல்வது அமைதி தரும்.",
      educationEn: "Brilliance in governance, science, administration, and competitive examinations.",
      educationTa: "அரசுத் தேர்வுகள், நிர்வாகம், அரசியல் அறிவியல் துறைகளில் சிறந்த வெற்றி கிடைக்கும்.",
      healthEn: "High vitality. If afflicted, watch for bilious heat (Pitta), headaches, eye strain, or blood pressure fluctuations.",
      healthTa: "உடல் சூடு, பித்தம், தலைவலி, கண் எரிச்சல் போன்ற சிறு உபாதைகளில் கவனம் தேவை.",
      remedyMantraEn: "Chant the Gayatri Mantra or Aditya Hridaya Stotram at sunrise.",
      remedyMantraTa: "தினமும் சூரிய உதயத்தில் ஆதித்ய ஹிருதய ஸ்தோத்திரம் அல்லது காயத்ரி மந்திரம் பாராயணம் செய்யவும்.",
      remedyCharityEn: "Offer wheat, copper vessels, or red flowers to elders or temple priests on Sundays.",
      remedyCharityTa: "ஞாயிற்றுக்கிழமைகளில் கோதுமை, செம்பு பாத்திரம் அல்லது செந்நிற மலர்களை தானம் செய்யவும்.",
    },
    "Sun-Moon": {
      summaryQuoteEn: "Harmonious union of soul and mind, domestic celebration, mother's blessings, and journeys.",
      summaryQuoteTa: "மன அமைதி, தாயின் ஆசி, இல்லறத்தில் சுப மங்கல நிகழ்வுகள் மற்றும் பயண அனுகூலம்.",
      generalEn: "When Moon runs its Antardasha in Sun Mahadasha, inner calm, auspicious ceremonies, and cooperative partnerships manifest. Water-borne enterprises, travels, and maternal support bring immense happiness.",
      generalTa: "சூரிய திசையில் சந்திர புக்தி நடக்கும் போது மனத்தெளிவு, இல்லத்தில் சுபகாரியங்கள், மற்றும் தாயாரின் பரிபூரண ஆசி கிடைக்கும். நீர் சம்பந்தமான தொழில் மற்றும் கலை சார்ந்த முயற்சிகளில் சிறந்த முன்னேற்றம் ஏற்படும்.",
      careerEn: "Support from feminine associates, public popularity, success in healthcare, food, hospitality, and liquid trade.",
      careerTa: "பெண்களின் ஆதரவு, மக்கள் செல்வாக்கு, உணவு, மருத்துவம் மற்றும் திரவப் பொருட்கள் வர்த்தகத்தில் சிறப்பான லாபம்.",
      wealthEn: "Steady cash flow, acquisition of silver, pearl jewelry, comfortable clothing, and agricultural prosperity.",
      wealthTa: "வெள்ளி, முத்து, புதிய ஆடை ஆபரணங்கள் மற்றும் நிலம்/விவசாயம் வழியே நிலையான வருமானம் சேரும்.",
      marriageEn: "Marital joy, deep mutual affection, fulfillment of domestic desires, and peaceful family gatherings.",
      marriageTa: "தம்பதியர் இடையே அன்யோன்யம், குடும்பத்தில் மகிழ்ச்சியான சூழல் மற்றும் மன நிம்மதி கூடும்.",
      educationEn: "Creative writing, literature, humanities, psychological intuition, and artistic brilliance.",
      educationTa: "இலக்கியம், கலை, கற்பனை வளம் மற்றும் உளவியல் சார்ந்த படிப்புகளில் அபார தேர்ச்சி.",
      healthEn: "Watch for minor coughs, colds, sinus sensitivity, or sleep fluctuations during waning Moon phases.",
      healthTa: "சளி, இருமல், கப தொல்லைகள் மற்றும் தூக்கமின்மை வராமல் சீரான உணவு பழக்கம் அவசியம்.",
      remedyMantraEn: "Chant 'Om Som Somaya Namaha' or worship Goddess Parvati with white flowers.",
      remedyMantraTa: "திங்கள்கிழமைகளில் அம்பாள் வழிபாடு செய்து 'ஓம் சந்திராய நமஹ' ஜெபிக்கவும்.",
      remedyCharityEn: "Donate rice, milk, white clothing, or potable water on Mondays.",
      remedyCharityTa: "திங்கள்கிழமைகளில் பால், அரிசி அல்லது வெள்ளை வஸ்திரம் ஏழைகளுக்கு தானம் செய்யவும்.",
    },
    "Sun-Mars": {
      summaryQuoteEn: "Surge of courage, heroic achievements, land acquisitions, and victory over adversaries.",
      summaryQuoteTa: "வீரியம், நிலம் மற்றும் பூமி சேர்க்கை, சகோதர ஆதரவு மற்றும் எதிரிகளை வெல்லும் ஆற்றல்.",
      generalEn: "Sun and Mars are natural intimate friends and fiery Kshatriya planets. In this period, physical prowess, property acquisitions, and triumph in competitive or legal contests are guaranteed.",
      generalTa: "சூரியனும் செவ்வாயும் நெருங்கிய மித்ர கிரகங்கள். இந்த காலகட்டத்தில் அபார துணிச்சல், ரியல் எஸ்டேட் மற்றும் பூமி யோகம், மற்றும் வழக்குகளில் வெற்றி உண்டாகும்.",
      careerEn: "Prominence in engineering, real estate, police, defense, surgery, sports, and executive management.",
      careerTa: "பொறியியல், கட்டிடம், ராணுவம், காவல் துறை, விளையாட்டு மற்றும் மருத்துவத் துறையில் உயர் பதவி யோகம்.",
      wealthEn: "Gains through copper, lands, immovable property, red metals, and bold entrepreneurial risks.",
      wealthTa: "செம்பு, பூமி, மனைகள், செங்கல்/கட்டுமானப் பொருட்கள் வழியே எதிர்பாராத தன லாபம்.",
      marriageEn: "Passionate bond, but avoid hasty arguments or dominating behavior with the spouse.",
      marriageTa: "ஆவேசமும் காதலும் நிறைந்திருக்கும்; தம்பதியர் இடையே வீண் வாக்குவாதங்களை தவிர்ப்பது உத்தமம்.",
      educationEn: "Excellence in mathematics, physics, technological innovation, and competitive examinations.",
      educationTa: "கணிதம், அறிவியல், தொழில்நுட்பம் மற்றும் போட்டித் தேர்வுகளில் முதலிடம் பெறுவர்.",
      healthEn: "High physical stamina. Watch for fever, blood pressure spikes, cuts, or inflammatory boils.",
      healthTa: "இரத்த அழுத்தம், உஷ்ணக் கட்டிகள், தீக்காயங்கள் மற்றும் வாகனப் பயணங்களில் வேகம் தவிர்க்கவும்.",
      remedyMantraEn: "Chant 'Om Angarakaya Namaha' or recite Subramanya Bhujangam.",
      remedyMantraTa: "செவ்வாய்க்கிழமைகளில் கந்த சஷ்டி கவசம் அல்லது சுப்பிரமண்ய அஷ்டோத்திரம் பாராயணம் செய்யவும்.",
      remedyCharityEn: "Donate red lentils (masoor dal), jaggery, or blood donation on Tuesdays.",
      remedyCharityTa: "செவ்வாய்க்கிழமைகளில் துவரம்பருப்பு, வெல்லம் அல்லது சிவப்பு வஸ்திரம் தானம் செய்யவும்.",
    },
    "Sun-Rahu": {
      summaryQuoteEn: "Karmic tests, unexpected transformations, foreign connections, and diplomatic maneuvering.",
      summaryQuoteTa: "கர்ம வினைகளின் வெளிப்பாடு, எதிர்பாராத மாற்றங்கள், வெளிநாட்டுத் தொடர்பு மற்றும் ராஜதந்திரம்.",
      generalEn: "Rahu represents shadow and sudden eclipse. If Rahu is placed in Kendra or Trikona with benefic association, sudden royal status and foreign wealth manifest. If afflicted, beware of illusions and toxic companions.",
      generalTa: "சூரியனில் ராகு புக்தி சோதனைகளுடன் கூடிய திருப்புமுனைக் காலம். ராகு சுப ஸ்தானங்களில் இருப்பின் திடீர் யோகம் மற்றும் வெளிநாட்டு தன லாபம் தரும்; அசுப நிலையில் இருப்பின் கண்மூடித்தனமான முடிவுகளைத் தவிர்க்க வேண்டும்.",
      careerEn: "Aviation, foreign collaborations, technological ventures, electronics, politics, and unconventional paths.",
      careerTa: "வெளிநாட்டு நிறுவனங்கள், ஐடி, மின்னணுவியல், அரசியல் மற்றும் எதிர்பாராத புதிய பொறுப்புகள் கிடைக்கும்.",
      wealthEn: "Sudden speculative gains possible, but avoid unverified investments or shady schemes.",
      wealthTa: "திடீர் லாபங்கள் வரலாம்; ஆனால் ஊக வணிகம், குறுக்கு வழிகளில் முதலீடு செய்வதை முற்றாகத் தவிர்க்கவும்.",
      marriageEn: "Need for transparent communication; avoid misunderstandings fueled by third-party interference.",
      marriageTa: "குடும்பத்தில் மூன்றாம் நபர்களின் தலையீட்டைத் தவிர்த்து வெளிப்படைத்தன்மையுடன் பேசுவது நலம்.",
      educationEn: "Aviation, data science, research, foreign languages, and deep unconventional wisdom.",
      educationTa: "கம்ப்யூட்டர் சயின்ஸ், வெளிநாட்டுப் படிப்பு, நுண்ணறிவு மற்றும் ஆராய்ச்சிப் படிப்பில் முன்னேற்றம்.",
      healthEn: "Watch for skin allergies, poisonous insects, nervous anxiety, or mysterious fevers.",
      healthTa: "தோல் அரிப்பு, ஒவ்வாமை, விஷ ஜந்துக்கள், நரம்புத் தளர்ச்சி மற்றும் மன பயங்களைத் தவிர்க்க தியானம் நலம்.",
      remedyMantraEn: "Chant the Maha Mrityunjaya Mantra or Durga Chalisa regularly.",
      remedyMantraTa: "துர்கா தேவிக்கு எலுமிச்சை விளக்கு ஏற்றி 'மகா மிருத்யுஞ்சய மந்திரம்' பாராயணம் செய்யவும்.",
      remedyCharityEn: "Feed black sesame seeds or dark-colored dogs on Saturdays.",
      remedyCharityTa: "கருப்பு உளுந்து, எள் உருண்டை அல்லது ஏழைகளுக்கு அன்னதானம் செய்வது ராகு தோஷத்தைப் போக்கும்.",
    },
    "Sun-Jupiter": {
      summaryQuoteEn: "Pinnacle of divine grace, wisdom, virtuous deeds, birth of a son, and royal honors.",
      summaryQuoteTa: "தெய்வ அனுகூலம், குருவருள், புத்திர பாக்கியம், தர்ம காரியங்கள் மற்றும் அரச மரியாதை.",
      generalEn: "Sun and Jupiter create the most auspicious sattvic alliance. Higher spiritual wisdom, executive promotion, blessings of Gurus, pilgrimages, and birth of virtuous progeny materialize during this blessed sub-period.",
      generalTa: "சூரியன் மற்றும் குருவின் சேர்க்கை பேரருளைத் தரும் சாத்வீக யோகம். ஆன்மீக வளர்ச்சி, குருவின் ஆசி, உயர்கல்வி, புத்திர பாக்கியம் மற்றும் அரசு வழி உயர் பதவிகள் கை கூடும்.",
      careerEn: "Judiciary, professorship, advisory councils, public administration, banking, and spiritual mentorship.",
      careerTa: "நீதித்துறை, கல்லூரிப் பேராசிரியர், வங்கி, நிதி நிறுவனம், ஆன்மீக அறக்கட்டளை மற்றும் ஆலோசனைப் பணிகள்.",
      wealthEn: "Substantial wealth accumulation, gold purchases, prosperity through fair dealings, and ancestral blessings.",
      wealthTa: "தங்கம் வாங்குதல், நிலையான சேமிப்பு, நேர்மையான வழிகளில் பெரும் தன லாபம் மற்றும் பரம்பரை யோகம்.",
      marriageEn: "Sacred matrimonial joy, harmony, celebration of childbirth, and respectful family relationship.",
      marriageTa: "மங்களகரமான சுப காரியங்கள், வம்ச விருத்தி, தம்பதியர் இடையே பெருமதிப்பும் அன்பும் நிறையும்.",
      educationEn: "Mastery of scriptures, law, philosophy, higher academic degrees, and honorary doctorates.",
      educationTa: "வேத சாஸ்திரம், சட்டம், தத்துவம், உயர் ஆய்வு மற்றும் அரசு அங்கீகாரம் பெற்ற பட்டங்கள் பெறுவர்.",
      healthEn: "Robust health and luminous aura. If afflicted, watch for liver, cholesterol, or excessive weight gain.",
      healthTa: "பொதுவான உடல் நலம் பிரகாசிக்கும்; கல்லீரல், கொழுப்பு மற்றும் அதீத உணவுப் பழக்கங்களில் எச்சரிக்கை தேவை.",
      remedyMantraEn: "Chant 'Om Guruve Namaha' or Guru Ashtakam on Thursdays.",
      remedyMantraTa: "வியாழக்கிழமைகளில் தட்சிணாமூர்த்தி வழிபாடு செய்து 'ஓம் குருவே நமஹ' ஜெபிக்கவும்.",
      remedyCharityEn: "Donate yellow lentils (chana dal), turmeric, bananas, or books to students on Thursdays.",
      remedyCharityTa: "கொண்டைக்கடலை மாலை சாற்றி மாணவர்களுக்கு கல்வி உபகரணங்கள் மற்றும் மஞ்சள் தானம் செய்யவும்.",
    },
    "Sun-Saturn": {
      summaryQuoteEn: "Patience, disciplined duty, overcoming heavy responsibilities, and enduring perseverance.",
      summaryQuoteTa: "பொறுமை, கடின உழைப்பு, குடும்பக் கடமைகள் மற்றும் சோதனைகளைத் தாண்டி நிலைக்கும் வெற்றி.",
      generalEn: "Sun and Saturn represent father and son with contrasting energies (fire vs cold duty). While it requires immense patience and tests endurance, it builds unshakeable character and long-lasting stability.",
      generalTa: "சூரியனும் சனியும் தந்தை-மகன் ஆயினும் ஒன்றுக்கொன்று முரண்பட்ட தத்துவங்கள். இக்காலம் பொறுமையையும் கடும் உழைப்பையும் கோரும்; விடாமுயற்சியால் நிரந்தரமான வெற்றியை உருவாக்கும்.",
      careerEn: "Mass leadership, labor administration, civil infrastructure, manufacturing, minerals, and heavy industries.",
      careerTa: "கட்டமைப்பு, உற்பத்தி ஆலைகள், இரும்பு/நிலக்கரி, மக்கள் பணி மற்றும் நீண்ட கால திட்டங்களில் வெற்றி.",
      wealthEn: "Slow, steady gains. Avoid reckless loans or delayed tax liabilities. Budget diligently.",
      wealthTa: "மெதுவான ஆனால் நிலையான பணவரவு; கடன் வாங்குவதையும் தேவையற்ற உத்தரவாதங்கள் தருவதையும் தவிர்க்கவும்.",
      marriageEn: "Heavy domestic responsibilities; avoid emotional detachment or prolonged physical separation.",
      marriageTa: "குடும்பப் பொறுப்புகள் கூடும்; துணைவரிடம் உணர்ச்சிப்பூர்வமான இடைவெளி வராமல் பார்த்துக் கொள்ளவும்.",
      educationEn: "Deep focus in geology, metallurgy, structural engineering, law, and history.",
      educationTa: "புவியியல், சட்டம், வரலாறு மற்றும் கடினமான தொழிற்சார் படிப்புகளில் தேர்ச்சி பெறுவர்.",
      healthEn: "Watch for joint pain, Vata imbalance, bone stiffness, toothache, or physical fatigue.",
      healthTa: "மூட்டு வலி, வாதக் கோளாறுகள், எலும்பு பலவீனம் மற்றும் அதீத உடல் சோர்வை கவனிக்கவும்.",
      remedyMantraEn: "Chant the Hanuman Chalisa or Shani Stotram on Saturdays.",
      remedyMantraTa: "சனிக்கிழமைகளில் அனுமன் சாலிசா அல்லது சனீஸ்வர பகவான் அஷ்டோத்திரம் ஜெபிக்கவும்.",
      remedyCharityEn: "Donate sesame oil, black clothes, or iron utensils to the needy on Saturdays.",
      remedyCharityTa: "சனிக்கிழமைகளில் நல்லெண்ணெய் தீபம் ஏற்றி மாற்றுத்திறனாளிகளுக்கு உணவு மற்றும் வஸ்திர தானம் செய்யவும்.",
    },
    "Sun-Mercury": {
      summaryQuoteEn: "Budha-Aditya intellectual radiance, commercial triumph, persuasive eloquence, and joy.",
      summaryQuoteTa: "புதாதித்ய யோக பிரகாசம், வியாபார வளர்ச்சி, வாக்கு சாதுரியம் மற்றும் புத்திக் கூர்மை.",
      generalEn: "Mercury in Sun Mahadasha activates the celebrated Budha-Aditya combination. Intellectual brilliance, diplomatic wit, lucrative commerce, and joyful communications prosper without hindrance.",
      generalTa: "சூரியனில் புதன் புக்தி புதாதித்ய யோகத்தின் முழு பலனையும் தரும். அறிவுக்கூர்மை, வணிக வளர்ச்சி, சாமர்த்தியமான பேச்சு மற்றும் புதிய திட்டங்கள் அனைத்தும் வெற்றிகரமாக முடியும்.",
      careerEn: "Trade, banking, accounting, journalism, software, communications, public relations, and commerce.",
      careerTa: "வணிகம், தகவல் தொடர்பு, பத்திரிகை, வங்கி, ஆடிட்டிங் மற்றும் மென்பொருள் துறையில் அபார வளர்ச்சி.",
      wealthEn: "Substantial cash inflow from trade, commission, brokerage, publishing, and green investments.",
      wealthTa: "வியாபாரம், தரகு, கமிஷன், புத்தகம்/எழுத்து மற்றும் பசுமை முதலீடுகள் வழியே சிறந்த பணவரவு.",
      marriageEn: "Playful companionship, intellectual conversations, short pleasure trips, and amicable harmony.",
      marriageTa: "தம்பதியர் இடையே நகைச்சுவை உணர்வு, சிற்றின்பப் பயணங்கள் மற்றும் கலகலப்பான இல்லறம்.",
      educationEn: "First-class academic honors in mathematics, logic, coding, commerce, and creative eloquence.",
      educationTa: "கணிதம், கணினி, தர்க்க சாஸ்திரம் மற்றும் பேச்சாற்றலில் முதன்மை இடத்தைப் பிடிப்பர்.",
      healthEn: "Alert nervous system. If afflicted, watch for skin dryness, speech fatigue, or mild indigestion.",
      healthTa: "தோல் வறட்சி, நரம்புத் தளர்ச்சி, அஜீரணக் கோளாறுகள் வராமல் சீரான நீர் அருந்துதல் நலம்.",
      remedyMantraEn: "Chant 'Om Budhaya Namaha' or Vishnu Sahasranama on Wednesdays.",
      remedyMantraTa: "புதன்கிழமைகளில் மகாவிஷ்ணு வழிபாடு செய்து 'விஷ்ணு சஹஸ்ரநாமம்' பாராயணம் செய்யவும்.",
      remedyCharityEn: "Donate green gram (moong dal), green vegetables, or feed cows with green grass on Wednesdays.",
      remedyCharityTa: "பச்சை பயறு, கீரை வகைகள் தானம் செய்யவும்; பசு மாட்டிற்கு அகத்திக் கீரை கொடுக்கவும்.",
    },
    "Sun-Ketu": {
      summaryQuoteEn: "Spiritual introspection, detachment from trivial vanity, occult study, and karmic release.",
      summaryQuoteTa: "ஆன்மீக நாட்டம், வைராக்கியம், ஞானோதயம் மற்றும் கர்ம வினைகளில் இருந்து விடுதலை.",
      generalEn: "Ketu is Moksha-karaka. In this period, material pride yields to spiritual awakening. Occult insights, visits to ancient shrines, and deep philosophical reflections arise naturally.",
      generalTa: "கேது மோட்ச காரகன். உலகியல் மாயைகளில் இருந்து விடுபட்டு ஆன்மீகத் தேடலும், குலதெய்வ வழிபாடும், தத்துவ ஞானமும் ஓங்கும் புனிதமான காலகட்டம்.",
      careerEn: "Spiritual leadership, alternative medicine, coding, research behind the scenes, and solitary arts.",
      careerTa: "ஆராய்ச்சி, சித்த/ஆயுர்வேத மருத்துவம், மென்பொருள் ஆய்வு மற்றும் ஆன்மீக வழிகாட்டுதல் பணிகள்.",
      wealthEn: "Fluctuating cash flow; money spent on pilgrimages, charities, and spiritual temples.",
      wealthTa: "பணவரவு சமமாக இருக்கும்; கோவில் திருப்பணிகள், அன்னதானம் மற்றும் ஆன்மீகப் பயணங்களுக்கு செலவாகும்.",
      marriageEn: "Spiritual bond; avoid cold detachment or emotional withdrawal from family duties.",
      marriageTa: "இல்லறக் கடமைகளில் சலிப்பு அடையாமல் குடும்பத்தினருடன் அன்போடு கலந்து வாழ்வது நலம்.",
      educationEn: "Occult sciences, astrology, philosophy, ancient history, and metaphysical research.",
      educationTa: "ஜோதிடம், ஆன்மீகம், தத்துவம் மற்றும் மறைபொருள் ஆய்வுகளில் ஆழ்ந்த ஞானம் உண்டாகும்.",
      healthEn: "Watch for sudden viral fevers, mysterious rashes, digestive spasms, or leg injuries.",
      healthTa: "காய்ச்சல், வயிற்றுப் பிடிப்பு, விஷப் பூச்சிக் கடிகள் மற்றும் கால் வலி போன்றவற்றில் எச்சரிக்கை.",
      remedyMantraEn: "Chant Ganesha Atharvashirsha or 'Om Kethave Namaha'.",
      remedyMantraTa: "விநாயகப் பெருமானுக்கு அருகம்புல் சாற்றி 'கணபதி அதர்வசீரிடம்' பாராயணம் செய்யவும்.",
      remedyCharityEn: "Donate multi-colored blankets, sesame seeds, or feed stray dogs on Tuesdays.",
      remedyCharityTa: "பலவண்ண கம்பளி, எள் தானம் செய்யவும்; தெரு நாய்களுக்கு உணவு வழங்கவும்.",
    },
    "Sun-Venus": {
      summaryQuoteEn: "Luxurious comfort, aesthetic delights, vehicle acquisition, and diplomatic magnetism.",
      summaryQuoteTa: "ஆடம்பர வாழ்க்கை, வாகன யோகம், கலை ஆர்வம், இல்லற சுகம் மற்றும் கவர்ச்சிகரமான ஆளுமை.",
      generalEn: "Venus brings refined aesthetic tastes, luxurious comfort, acquisition of fine apparel and vehicles, and delightful romantic company to the energetic Sun period.",
      generalTa: "சுக்கிரன் ஆடம்பரம் மற்றும் சுகபோக காரகன். புதிய வாகனம், நவீன ஆடை ஆபரணங்கள், கலைகளில் ஆர்வம் மற்றும் சமூகத்தில் கவர்ச்சிகரமான செல்வாக்கு கூடும்.",
      careerEn: "Media, fashion, jewelry, hospitality, creative design, cosmetics, entertainment, and luxury trade.",
      careerTa: "திரைத்துறை, ஆடை வடிவமைப்பு, நகை வணிகம், அழகு சாதனங்கள், சுற்றுலா மற்றும் கலைத் துறை.",
      wealthEn: "Substantial prosperity, spending on beauty and real estate, and financial blessings through women.",
      wealthTa: "பெண்களின் வழியே தன லாபம், நிலம் மற்றும் சொகுசு வாகனங்கள் வாங்கும் யோகம் உண்டாகும்.",
      marriageEn: "Romantic warmth and marital joy; ensure mutual understanding and avoid excessive passions.",
      marriageTa: "காதல் மற்றும் இல்லற இன்பம் தழைக்கும்; தம்பதியர் இடையே மனமொத்த புரிதல் ஏற்படும்.",
      educationEn: "Fine arts, architecture, cinema, hotel management, graphic design, and performing arts.",
      educationTa: "நுண்கலைகள், கட்டிடக்கலை, இசை, நாட்டியம் மற்றும் ஆடை வடிவமைப்பு படிப்பில் சாதனை.",
      healthEn: "Good health; watch for urinary sensitivities, throat complaints, or excessive indulgence in sweets.",
      healthTa: "நீரிழிவு, சிறுநீரகக் கோளாறுகள் மற்றும் அதிக இனிப்பு உண்ணுதலைத் தவிர்ப்பது உடல் நலத்திற்கு நலம்.",
      remedyMantraEn: "Chant Sri Suktam or Mahalakshmi Ashtakam on Fridays.",
      remedyMantraTa: "வெள்ளிக்கிழமைகளில் ஸ்ரீ சூக்தம் அல்லது கனகதாரா ஸ்தோத்திரம் பாராயணம் செய்யவும்.",
      remedyCharityEn: "Donate curd, white sweets, silver, or silks to married women or temple priests on Fridays.",
      remedyCharityTa: "தயிரன்னம், வெள்ளை இனிப்புகள் அல்லது பட்டு வஸ்திரத்தை வெள்ளிக்கிழமைகளில் தானம் செய்யவும்.",
    },
  };

  // Generic fallback generator for all 81 combinations covering all 9 Mahadashas
  if (baseTexts[key]) {
    return baseTexts[key] as ClassicalCombinationData;
  }

  // Dynamic tailored classical generation for other Mahadasha-Antardasha combinations
  const mahaTamil: Record<string, string> = {
    Sun: "சூரிய", Moon: "சந்திர", Mars: "செவ்வாய்", Rahu: "ராகு",
    Jupiter: "குரு", Saturn: "சனி", Mercury: "புதன்", Ketu: "கேது", Venus: "சுக்கிர"
  };
  const antarTamil: Record<string, string> = {
    Sun: "சூரிய", Moon: "சந்திர", Mars: "செவ்வாய்", Rahu: "ராகு",
    Jupiter: "குரு", Saturn: "சனி", Mercury: "புதன்", Ketu: "கேது", Venus: "சுக்கிர"
  };

  const mName = maha;
  const aName = antar;
  const mT = mahaTamil[mName] || mName;
  const aT = antarTamil[aName] || aName;

  const quoteEn = isAuspicious
    ? `Auspicious convergence of ${mName} Mahadasha and ${aName} Antardasha conferring growth, honor, and success.`
    : `Transformational period of ${mName} Mahadasha and ${aName} Antardasha requiring steady discipline and patience.`;

  const quoteTa = isAuspicious
    ? `${mT} மகா திசையில் ${aT} புக்தி அனுகூலமான நற்பலன்களையும், காரிய வெற்றியையும், சமூக மேன்மையையும் தரும்.`
    : `${mT} மகா திசையில் ${aT} புக்தி சோதனைகளைக் கடந்து நிலைக்கும் வெற்றியையும், மன தைரியத்தையும் தரும் காலம்.`;

  const genEn = `During the ${aName} sub-period in ${mName} Mahadasha, the native experiences the combined vibrations of both lords posited at a distance of ${rel.distanceFromMahaToAntar} houses. Since the sub-period lord delivers its results in the ${antarP.deliveryTimingEn.toLowerCase()}, all matters of the derived ${rel.derivedHouseFromLagna}th house from Lagna materialize prominently.`;
  const genTa = `${mT} மகா திசையில் ${aT} புக்தி நடக்கும் போது, இரு கிரகங்களும் தங்களுக்குள் ${rel.distanceFromMahaToAntar}-ஆம் இடம் தொடர்பு கொண்டு செயல்படுகின்றன. ${aT} புக்தி நாதன் தனது பலன்களை ${antarP.deliveryTimingTa}-ல் வழங்குவதால், லக்னத்திற்குரிய ${rel.derivedHouseFromLagna}-ஆம் பாவத்தின் பலாபலன்கள் தீவிரமாக வெளிப்படும்.`;

  const carEn = isAuspicious
    ? `Steady professional ascent, favorable connections with superiors, and expansion of business frontiers.`
    : `Demands high patience at work, avoid conflicts with colleagues or supervisors, and adhere to compliance.`;
  const carTa = isAuspicious
    ? `உத்தியோகத்தில் பதவி உயர்வு, தொழில் கூட்டாளிகளின் முழு ஆதரவு மற்றும் புதிய வாய்ப்புகள் தடையின்றி கை கூடும்.`
    : `வேலை செய்யும் இடத்தில் நிதானமும், சக ஊழியர்களிடம் இணக்கமும் அவசியம்; புதிய விவகாரங்களில் அவசர முடிவுகள் வேண்டாம்.`;

  const wltEn = isAuspicious
    ? `Fruitful accumulation of wealth, profitable investments, and liquidation of lingering debts.`
    : `Prudent budgeting required; avoid speculative risks, curb unnecessary lifestyle expenditures.`;
  const wltTa = isAuspicious
    ? `நிலையான தன லாபம், முதலீடுகளில் நல்ல வருமானம் மற்றும் நீண்ட நாள் கடன் பாக்கிகள் வசூலாகும்.`
    : `பட்ஜெட் போட்டு செலவு செய்வது நலம்; ஊக வணிக முதலீடுகளையும், ஆடம்பர செலவுகளையும் கட்டுப்படுத்தவும்.`;

  const marEn = isAuspicious
    ? `Harmonious family life, happy celebrations, mutual understanding, and warmth among loved ones.`
    : `Maintain empathetic dialogue; avoid minor domestic squabbles from escalating into tension.`;
  const marTa = isAuspicious
    ? `குடும்பத்தில் அமைதியும் மகிழ்ச்சியும் நிலவும்; உறவினர்களின் வருகையும் சுப நிகழ்வுகளும் மனநிறைவை தரும்.`
    : `குடும்ப உறுப்பினர்களிடம் கனிவான அணுகுமுறை தேவை; சிறு மனஸ்தாபங்களை பெரிதுபடுத்தாமல் இருப்பது நலம்.`;

  const eduEn = isAuspicious
    ? `Clarity of intellect, academic laurels, intellectual growth, and blessings of knowledgeable mentors.`
    : `Requires persistent concentration in studies; avoid mental distractions and focus on fundamentals.`;
  const eduTa = isAuspicious
    ? `கல்வியில் சிறந்த மேன்மை, ஞாபக சக்தி அதிகரித்தல் மற்றும் ஆசிரியர்களின் பாராட்டுக்கள் கிடைக்கும்.`
    : `படிக்கும் போது கூடுதல் கவனமும் கவனச்சிதறல்களைத் தவிர்ப்பதும் அவசியம்; தொடர்ந்து விடாமுயற்சி தேவை.`;

  const hltEn = isAuspicious
    ? `Good stamina and physical vitality. Balanced lifestyle ensures peace of mind and bodily endurance.`
    : `Pay attention to diet, regular sleep, and timely medical check-ups; avoid stressful physical overexertion.`;
  const hltTa = isAuspicious
    ? `உடல் ஆரோக்கியம் சீராக இருக்கும்; உடற்பயிற்சியும் சீரான உணவும் உற்சாகத்தைத் தரும்.`
    : `சரியான நேரத்திற்கு உணவு உண்பதும், போதுமான தூக்கமும் அவசியம்; மன அழுத்தத்தைத் தவிர்க்க தியானம் நலம்.`;

  return {
    summaryQuoteEn: quoteEn,
    summaryQuoteTa: quoteTa,
    generalEn: genEn,
    generalTa: genTa,
    careerEn: carEn,
    careerTa: carTa,
    wealthEn: wltEn,
    wealthTa: wltTa,
    marriageEn: marEn,
    marriageTa: marTa,
    educationEn: eduEn,
    educationTa: eduTa,
    healthEn: hltEn,
    healthTa: hltTa,
    remedyMantraEn: `Chant Navagraha Stotram or deity prayers corresponding to ${antar}.`,
    remedyMantraTa: `${aT} பகவானுக்குரிய காயத்ரி மந்திரம் அல்லது நவகிரக ஸ்தோத்திரம் பாராயணம் செய்யவும்.`,
    remedyCharityEn: `Perform charity aligned with the elements of ${antar} on its sacred day.`,
    remedyCharityTa: `${aT} பகவானுக்குரிய நாளில் ஏழைகளுக்கு அன்னதானம் அல்லது வஸ்திர தானம் செய்வது நலம்.`,
  };
}

// ---------------------------------------------------------------------------
// Andhara (Pratyantardasha) Catalyst Insights
// ---------------------------------------------------------------------------

export function getAndharaCatalystInsight(
  andharLord: string,
  bhuktiLord: string,
  relFromBhukti: PeriodRelationshipAnalysis,
  andharStrength: PlanetStrengthProfile
) {
  const norm = normalizePlanetName(andharLord);
  const catalysts: Record<
    string,
    {
      themeEn: string;
      themeTa: string;
      catalystEn: string;
      catalystTa: string;
      eventFocusEn: string;
      eventFocusTa: string;
    }
  > = {
    Sun: {
      themeEn: "Vitality, Executive Decisions & Royal Command",
      themeTa: "ஆத்ம தைரியம், நிர்வாக முடிவுகள் & அரசு அங்கீகாரம்",
      catalystEn: `Sun as Andhara acts as an energetic executive catalyst within ${bhuktiLord} Bhukti, triggering swift official decisions, leadership opportunities, and active support from father or government authorities.`,
      catalystTa: `${bhuktiLord} புக்தியில் சூரிய அந்திரம் ஒரு தூண்டுதல் சக்தியாக செயல்பட்டு, நிர்வாகப் பணிகளில் தெளிவு, தலைமை ஏற்கும் வாய்ப்புகள், தந்தை மற்றும் அரசு வழி உதவிகளை இந்த காலகட்டத்தில் விரைந்து பெற்றுத்தரும்.`,
      eventFocusEn: "High probability of government approvals, career elevation, and decisive breakthroughs.",
      eventFocusTa: "அரசு அனுமதி, உத்தியோகத்தில் கௌரவம் மற்றும் தள்ளிப்போன முக்கிய காரியங்கள் கைகூடும் காலம்.",
    },
    Moon: {
      themeEn: "Mental Serenity, Public Popularity & Maternal Grace",
      themeTa: "மன நிம்மதி, மக்கள் செல்வாக்கு & தாயின் பரிபூரண ஆசி",
      catalystEn: `Moon as Andhara soothes friction, enhances emotional clarity, stimulates cash liquidity, and triggers pleasant family visits or journeys over water.`,
      catalystTa: `${bhuktiLord} புக்தியில் சந்திர அந்திரம் மன அழுத்தங்களை நீக்கி, அமைதியான சிந்தனை, பணப்புழக்கம், தாயார் ஆசி மற்றும் குறுகிய பயணங்களை உடனடியாகத் தூண்டிவிடும்.`,
      eventFocusEn: "Positive domestic celebrations, peaceful settlements, and creative fulfillment.",
      eventFocusTa: "இல்லத்தில் சுப நிகழ்வுகள், சுமுகமான பேச்சுவார்த்தைகள் மற்றும் கலை/பயண மகிழ்ச்சி.",
    },
    Mars: {
      themeEn: "Dynamic Action, Land/Property Momentum & Heroic Courage",
      themeTa: "தீவிர செயல்பாடு, பூமி/மனை விவகாரங்கள் & துணிச்சல்",
      catalystEn: `Mars as Andhara injects dynamic momentum into ${bhuktiLord} Bhukti, enabling quick decisions regarding real estate, machinery, technical disputes, or competitive contests.`,
      catalystTa: `${bhuktiLord} புக்தியில் செவ்வாய் அந்திரம் அபார வீரியத்தை வழங்கி, நிலம், கட்டிடம், இயந்திரங்கள் வாங்குதல் மற்றும் போட்டித் தேர்வுகளில் உடனடி வெற்றியைத் தூண்டும்.`,
      eventFocusEn: "Fast-tracked real estate registration, overcoming competitors, and surgical/technical progress.",
      eventFocusTa: "நிலம்/மனை பதிவு, எதிரிகளை வீழ்த்துதல் மற்றும் துணிச்சலான திட்டங்களில் உடனடி முன்னேற்றம்.",
    },
    Rahu: {
      themeEn: "Sudden Breakthroughs, Unconventional Paths & Foreign Dealings",
      themeTa: "திடீர் திருப்பங்கள், புதுமையான வழிகள் & வெளிநாட்டுத் தொடர்பு",
      catalystEn: `Rahu as Andhara creates sudden shifts, unconventional opportunities, digital or technical achievements, and foreign communication during ${bhuktiLord} Bhukti.`,
      catalystTa: `${bhuktiLord} புக்தியில் ராகு அந்திரம் எதிர்பாராத திடீர் திருப்பங்களையும், தகவல் தொழில்நுட்பம் மற்றும் வெளிநாட்டுத் தொடர்புகளின் வழியே புதிய வாய்ப்புகளையும் உருவாக்கும்.`,
      eventFocusEn: "Sudden unexpected windfall or digital expansion; avoid risky speculations.",
      eventFocusTa: "திடீர் தன வரவு மற்றும் புதிய திட்டங்கள் தொடங்குதல்; சூதாட்டம்/ஊக வணிகத்தில் நிதானம் தேவை.",
    },
    Jupiter: {
      themeEn: "Divine Grace, Wise Counsel, Progeny & Financial Expansion",
      themeTa: "தெய்வ அனுகூலம், குருவருள், புத்திர சந்தோஷம் & தன வரவு",
      catalystEn: `Jupiter as Andhara brings the most auspicious expansion: counsel of wise mentors, wealth accrual, academic honors, and child-related auspiciousness into ${bhuktiLord} Bhukti.`,
      catalystTa: `${bhuktiLord} புக்தியில் குரு அந்திரம் மிகச் சிறந்த சுப யோகங்களைத் தரும். பெரியோர்களின் வழிகாட்டுதல், தர்ம சிந்தனை, தன வரவு மற்றும் புத்திர வழியில் மகிழ்ச்சியைத் தரும்.`,
      eventFocusEn: "Golden period for ceremonies, weddings, educational degrees, and auspicious investments.",
      eventFocusTa: "சுப காரியங்கள், உயர்கல்வி பட்டங்கள், வங்கி சேமிப்பு மற்றும் ஆன்மீகச் சுற்றுலா கைகூடும்.",
    },
    Saturn: {
      themeEn: "Enduring Duty, Systematic Labor & Resolving Pending Debts",
      themeTa: "கடமை உணர்வு, கடின உழைப்பின் பலன் & நிலுவைப் பணிகள் முடிவு",
      catalystEn: `Saturn as Andhara enforces discipline and patience, consolidating long-term foundations, finishing pending legal/administrative chores, and rewarding dedicated labor in ${bhuktiLord} Bhukti.`,
      catalystTa: `${bhuktiLord} புக்தியில் சனி அந்திரம் பொறுமையையும் நேர்மையையும் கோரும்; நீண்ட நாள் நிலுவையில் இருந்த சிக்கல்களைத் தீர்த்து, உழைப்பிற்கேற்ற நிரந்தர பலனை வழங்கும்.`,
      eventFocusEn: "Concrete progress on long-term infrastructure, labor coordination, and resolving chronic burdens.",
      eventFocusTa: "நீண்ட கால முதலீடுகள், தொழில் நிலையான கட்டமைப்பு மற்றும் பொறுப்புகளை வெற்றிகரமாக முடித்தல்.",
    },
    Mercury: {
      themeEn: "Commercial Triumph, Sharp Intellect, Speech & Trade Profits",
      themeTa: "வணிக வெற்றி, புத்திக் கூர்மை, வாக்கு சாதுரியம் & வர்த்தக லாபம்",
      catalystEn: `Mercury as Andhara stimulates business negotiations, trade profits, successful examinations, writing projects, and cheerful intellectual camaraderie within ${bhuktiLord} Bhukti.`,
      catalystTa: `${bhuktiLord} புக்தியில் புதன் அந்திரம் வியாபாரத்தில் புதிய வாடிக்கையாளர்கள், கணக்கு வழக்கைத் தீர்த்தல், போட்டித் தேர்வுகளில் வெற்றி மற்றும் பேச்சுத் திறமையால் லாபம் ஈட்டும்.`,
      eventFocusEn: "Lucrative commercial signings, scholastic awards, and seamless communications.",
      eventFocusTa: "புதிய வியாபார ஒப்பந்தங்கள், கல்வி மேன்மை மற்றும் தகவல் தொடர்பு சாதனங்கள் வழியே ஆதாயம்.",
    },
    Ketu: {
      themeEn: "Spiritual Insights, Karmic Liberation, Intuition & Altruism",
      themeTa: "ஆன்மீக நாட்டம், ஞானம், குலதெய்வ அருள் & பற்று நீக்கம்",
      catalystEn: `Ketu as Andhara inspires inward introspection, visits to ancestral or heritage shrines, research breakthroughs, and relief from karmic entrapments during ${bhuktiLord} Bhukti.`,
      catalystTa: `${bhuktiLord} புக்தியில் கேது அந்திரம் உலக மாயைகளில் இருந்து விடுபட்டு, குலதெய்வ வழிபாடு, ஆன்மீக தரிசனம் மற்றும் மன அமைதியைத் தரும்.`,
      eventFocusEn: "Spiritual healing, intuitive discovery, temple charity, and philosophical peace.",
      eventFocusTa: "ஆன்மீகப் பணிகள், குலதெய்வப் பிரார்த்தனை நிறைவேற்றுதல் மற்றும் மன நிம்மதி.",
    },
    Venus: {
      themeEn: "Aesthetic Pleasures, Romance, Vehicle Comfort & Social Charm",
      themeTa: "ஆடம்பர சுகம், இல்லற இன்பம், வாகன யோகம் & சமூக கௌரவம்",
      catalystEn: `Venus as Andhara activates beauty, procurement of fine apparel/vehicles, joyous social celebrations, romantic reconciliation, and artistic pleasures in ${bhuktiLord} Bhukti.`,
      catalystTa: `${bhuktiLord} புக்தியில் சுக்கிர அந்திரம் ஆடை, ஆபரணம், புதிய வாகன யோகம், கலை ஆர்வம் மற்றும் இல்லறத்தில் இனிய மகிழ்ச்சியை உடனடியாகத் தூண்டும்.`,
      eventFocusEn: "Procuring luxury items, joyous domestic festivities, romantic celebrations, and artistic ventures.",
      eventFocusTa: "வாகன வாங்குதல், புதிய நகைகள் சேர்க்கை, இல்லறத்தில் அன்யோன்யம் மற்றும் சுப விருந்துகள்.",
    },
  };

  return catalysts[norm] || catalysts["Sun"];
}

// ---------------------------------------------------------------------------
// Main Analysis Pipeline: analyzeDasaBukthiPalangal
// ---------------------------------------------------------------------------

export function analyzeDasaBukthiPalangal(
  horoscope: HoroscopeResponse,
  dasa: DasaResponse,
  targetMahaLord?: string,
  targetAntarLord?: string,
  targetAndharLord?: string,
  shadbala?: ShadbalaResponse,
  ashtakavarga?: AshtakavargaResponse,
  birthDate?: string,
  birthTime?: string,
  timezone?: string
): DasaBukthiAnalysis | null {
  if (!horoscope || !dasa || !dasa.dasa_tree || dasa.dasa_tree.length === 0) {
    return null;
  }

  const birthNakshatraIndex = dasa.nakshatra?.index ?? horoscope.ascendant?.nakshatra?.index ?? 0;
  const ascSign = horoscope.ascendant.sign_index;

  // 1. Identify active period nodes or targeted nodes
  const nowJd = Date.now() / 86400000 + 2440587.5;

  // Find target Mahadasha
  let mahaNode: DasaPeriodNode | undefined = undefined;
  if (targetMahaLord) {
    mahaNode = dasa.dasa_tree.find((m) => normalizePlanetName(m.lord) === normalizePlanetName(targetMahaLord));
  }
  if (!mahaNode) {
    mahaNode = dasa.dasa_tree.find((m) => m.start_jd <= nowJd && nowJd < m.end_jd) || dasa.dasa_tree[0];
  }
  if (!mahaNode) return null;

  // Sub-periods of Mahadasha (Bhuktis)
  let subPeriods: DasaPeriodNode[] = mahaNode.sub_periods || [];
  if (subPeriods.length === 0) {
    subPeriods = generateChildSubPeriods(mahaNode, 5.5, birthDate);
  }

  // Find target Antardasha (Bhukti)
  let antarNode: DasaPeriodNode | undefined = undefined;
  if (targetAntarLord) {
    antarNode = subPeriods.find((b) => normalizePlanetName(b.lord) === normalizePlanetName(targetAntarLord));
  }
  if (!antarNode) {
    antarNode = subPeriods.find((b) => b.start_jd <= nowJd && nowJd < b.end_jd) || subPeriods[0];
  }
  if (!antarNode) return null;

  // Level 3: Pratyantardashas (Andharas) under this Bhukti
  let andharNodes: DasaPeriodNode[] = antarNode.sub_periods || [];
  if (andharNodes.length === 0) {
    andharNodes = generateChildSubPeriods(antarNode, 5.5, birthDate);
  }

  const formatD = (iso: string) => {
    if (!iso) return "—";
    const [y, m, d] = iso.split("-");
    return `${d}/${m}/${y}`;
  };

  // Map available Andharas for easy UI pills/selector
  const availableAndharas: AndharaItem[] = andharNodes.map((aNode) => {
    const aStartDt = jdToCalendarDateTime(aNode.start_jd, 5.5);
    const aEndDt = jdToCalendarDateTime(aNode.end_jd, 5.5);
    const aStartIso = aStartDt?.dateStr || "";
    const aEndIso = aEndDt?.dateStr || "";
    const aIsActive = aNode.start_jd <= nowJd && nowJd < aNode.end_jd;
    const aIsPast = nowJd >= aNode.end_jd;
    const aIsFuture = nowJd < aNode.start_jd;
    let aProgress = 0;
    if (aIsActive && aNode.end_jd > aNode.start_jd) {
      aProgress = Math.min(
        100,
        Math.max(
          0,
          Math.round(((nowJd - aNode.start_jd) / (aNode.end_jd - aNode.start_jd)) * 100)
        )
      );
    } else if (aIsPast) {
      aProgress = 100;
    }
    const days = Math.round(aNode.duration_days);
    const durFormatted =
      days >= 30
        ? `${(days / 30.4375).toFixed(1)} mo (${days}d)`
        : `${days} days`;

    return {
      lord: aNode.lord,
      startDateIso: aStartIso,
      endDateIso: aEndIso,
      startDateFormatted: formatD(aStartIso),
      endDateFormatted: formatD(aEndIso),
      durationDays: days,
      durationFormatted: durFormatted,
      isActiveNow: aIsActive,
      isPast: aIsPast,
      isFuture: aIsFuture,
      progressPercent: aProgress,
    };
  });

  // Find target Andhara node
  let andharNode: DasaPeriodNode | undefined = undefined;
  if (targetAndharLord) {
    andharNode = andharNodes.find(
      (a) => normalizePlanetName(a.lord) === normalizePlanetName(targetAndharLord)
    );
  }
  if (!andharNode) {
    andharNode =
      andharNodes.find((a) => a.start_jd <= nowJd && nowJd < a.end_jd) ||
      andharNodes[0];
  }
  const selectedAndharLord = andharNode ? andharNode.lord : antarNode.lord;

  // Active status of Bhukti
  const isActiveNow = antarNode.start_jd <= nowJd && nowJd < antarNode.end_jd;
  const isPast = nowJd >= antarNode.end_jd;
  const isFuture = nowJd < antarNode.start_jd;

  let progressPercent = 0;
  if (isActiveNow && antarNode.end_jd > antarNode.start_jd) {
    progressPercent = Math.min(
      100,
      Math.max(
        0,
        Math.round(((nowJd - antarNode.start_jd) / (antarNode.end_jd - antarNode.start_jd)) * 100)
      )
    );
  } else if (isPast) {
    progressPercent = 100;
  }

  // Dates & Ages for Bhukti
  const startDt = jdToCalendarDateTime(antarNode.start_jd, 5.5);
  const endDt = jdToCalendarDateTime(antarNode.end_jd, 5.5);
  const startDateIso = startDt?.dateStr || "";
  const endDateIso = endDt?.dateStr || "";

  const startDateFormatted = formatD(startDateIso);
  const endDateFormatted = formatD(endDateIso);
  const durationYearsFormatted = `${antarNode.duration_years.toFixed(2)} yrs (${antarNode.duration_days.toFixed(0)} days)`;

  let ageAtStartFormatted = "—";
  let ageAtEndFormatted = "—";
  if (birthDate && startDt && endDt) {
    const [by, bm, bd] = birthDate.split("-").map(Number);
    const startAge = calculateCalendarAge(by, bm, bd, startDt.year, startDt.month, startDt.day);
    const endAge = calculateCalendarAge(by, bm, bd, endDt.year, endDt.month, endDt.day);
    ageAtStartFormatted = formatCalendarAge(startAge, "ta");
    ageAtEndFormatted = formatCalendarAge(endAge, "ta");
  }

  // 2. Planetary Strengths
  const mahaStrength = evaluatePlanetStrength(mahaNode.lord, horoscope, shadbala, ashtakavarga, birthNakshatraIndex);
  const antarStrength = evaluatePlanetStrength(antarNode.lord, horoscope, shadbala, ashtakavarga, birthNakshatraIndex);
  const andharaStrength = evaluatePlanetStrength(selectedAndharLord, horoscope, shadbala, ashtakavarga, birthNakshatraIndex);

  // 3. Relationship Analysis (Maha to Antar, and Antar to Andhara)
  const relationship = evaluatePeriodRelationship(mahaStrength, antarStrength, ascSign);
  const relationshipFromBhukti = evaluatePeriodRelationship(antarStrength, andharaStrength, ascSign);
  const relationshipFromMaha = evaluatePeriodRelationship(mahaStrength, andharaStrength, ascSign);

  // 4. Andhara Detail Assembly
  const matchingAndharItem =
    availableAndharas.find((a) => normalizePlanetName(a.lord) === normalizePlanetName(selectedAndharLord)) ||
    availableAndharas[0] || {
      lord: selectedAndharLord,
      startDateIso: "",
      endDateIso: "",
      startDateFormatted: "—",
      endDateFormatted: "—",
      durationDays: 30,
      durationFormatted: "30 days",
      isActiveNow: false,
      isPast: false,
      isFuture: false,
      progressPercent: 0,
    };

  const andharaCatalyst = getAndharaCatalystInsight(selectedAndharLord, antarNode.lord, relationshipFromBhukti, andharaStrength);

  const andharaDetail: AndharaAnalysisDetail = {
    lord: selectedAndharLord,
    timing: matchingAndharItem,
    strength: andharaStrength,
    relationshipFromBhukti,
    relationshipFromMaha,
    catalystThemeEn: andharaCatalyst.themeEn,
    catalystThemeTa: andharaCatalyst.themeTa,
    predictionEn: andharaCatalyst.catalystEn,
    predictionTa: andharaCatalyst.catalystTa,
    eventTriggerFocusEn: andharaCatalyst.eventFocusEn,
    eventTriggerFocusTa: andharaCatalyst.eventFocusTa,
  };

  // 5. Scientific 2-Tier & 3-Tier Auspiciousness Calculations
  // (Synthesizing Mantreswara's Phaladeepika Ch. 19-21 & Krishan Kant Bhardwaj)

  // --- CALCULATION A: DASA-BUKTHI (2-LEVEL) POSITIVE PERCENTAGE ---
  let dbScore = 50;

  // Level 1: Mahadasha Lord Influence (Weight ~30)
  if (mahaStrength.shadbalaPass) dbScore += 6; else dbScore -= 6;
  if (mahaStrength.dignity === "exalted") dbScore += 8;
  else if (mahaStrength.dignity === "moolatrikona") dbScore += 6;
  else if (mahaStrength.dignity === "own_sign") dbScore += 4;
  else if (mahaStrength.dignity === "debilitated") dbScore -= 10;
  else if (mahaStrength.dignity === "enemy_sign") dbScore -= 4;
  if (mahaStrength.isCombust) dbScore -= 6;
  if ([1, 4, 7, 10, 5, 9].includes(mahaStrength.houseOccupied)) dbScore += 5;
  if ([6, 8, 12].includes(mahaStrength.houseOccupied)) dbScore -= 5;

  // Level 2: Antardasha (Bhukti) Lord Influence (Weight ~45)
  if (antarStrength.shadbalaPass) dbScore += 10; else dbScore -= 10;
  if (antarStrength.dignity === "exalted") dbScore += 12;
  else if (antarStrength.dignity === "moolatrikona") dbScore += 9;
  else if (antarStrength.dignity === "own_sign") dbScore += 7;
  else if (antarStrength.dignity === "debilitated") dbScore -= 14;
  else if (antarStrength.dignity === "enemy_sign") dbScore -= 6;
  if (antarStrength.ashtakavargaStatus === "auspicious") dbScore += 10;
  else if (antarStrength.ashtakavargaStatus === "inauspicious") dbScore -= 10;
  if (antarStrength.isCombust) dbScore -= 10;
  if (antarStrength.isVargottama) dbScore += 8;
  if (antarStrength.taraBala.isAuspicious) dbScore += 6; else dbScore -= 6;

  // Level 1 & 2 Relationship Axis (Weight ~25) (Phaladeepika Ch. 21)
  if (relationship.isRajayogaSambandha) dbScore += 14;
  if (relationship.distanceFromMahaToAntar === 5 || relationship.distanceFromMahaToAntar === 9) dbScore += 10; // Navapanchama
  else if ([1, 4, 7, 10].includes(relationship.distanceFromMahaToAntar)) dbScore += 8; // Kendra
  else if ([3, 11].includes(relationship.distanceFromMahaToAntar)) dbScore += 6; // Upachaya
  else if (relationship.isShadashtakaWarning) dbScore -= 14; // 6/8
  else if (relationship.isDvidvadasaWarning) dbScore -= 8; // 2/12

  if (relationship.relationshipNature === "mutual_friends") dbScore += 6;
  else if (relationship.relationshipNature === "mutual_enemies") dbScore -= 6;

  const dasaBukthiPositiveScore = Math.min(95, Math.max(10, Math.round(dbScore)));
  const dasaBukthiNegativeScore = 100 - dasaBukthiPositiveScore;

  // --- CALCULATION B: DASA-BUKTHI-ANDHARA (3-LEVEL) POSITIVE PERCENTAGE ---
  let andharModifier = 0;
  if (andharaStrength.shadbalaPass) andharModifier += 8; else andharModifier -= 8;
  if (andharaStrength.dignity === "exalted") andharModifier += 10;
  else if (andharaStrength.dignity === "moolatrikona" || andharaStrength.dignity === "own_sign") andharModifier += 7;
  else if (andharaStrength.dignity === "debilitated") andharModifier -= 12;
  else if (andharaStrength.dignity === "enemy_sign") andharModifier -= 5;
  if (andharaStrength.ashtakavargaStatus === "auspicious") andharModifier += 8;
  else if (andharaStrength.ashtakavargaStatus === "inauspicious") andharModifier -= 8;
  if (andharaStrength.isCombust) andharModifier -= 8;
  if (andharaStrength.taraBala.isAuspicious) andharModifier += 6; else andharModifier -= 6;

  // Relationship of Andhara from Bhukti Lord (Phaladeepika Ch. 21)
  const andharDist = relationshipFromBhukti.distanceFromMahaToAntar;
  if (andharDist === 5 || andharDist === 9) andharModifier += 10;
  else if ([1, 4, 7, 10].includes(andharDist)) andharModifier += 8;
  else if ([3, 11].includes(andharDist)) andharModifier += 6;
  else if (relationshipFromBhukti.isShadashtakaWarning) andharModifier -= 14;
  else if (relationshipFromBhukti.isDvidvadasaWarning) andharModifier -= 8;

  // Blending: 65% Dasa-Bukthi baseline + 35% Andhara catalyst
  const blendedScore = dasaBukthiPositiveScore * 0.65 + (50 + andharModifier) * 0.35;
  const andharaPositiveScore = Math.min(96, Math.max(8, Math.round(blendedScore)));
  const andharaNegativeScore = 100 - andharaPositiveScore;

  const score = andharaPositiveScore;

  // Extract Key Positive Points and Caution Points
  const keyPositivePointsEn: string[] = [];
  const keyPositivePointsTa: string[] = [];
  const keyCautionPointsEn: string[] = [];
  const keyCautionPointsTa: string[] = [];

  if (antarStrength.shadbalaPass) {
    const rupasStr = antarStrength.shadbalaRupas != null ? ` (${antarStrength.shadbalaRupas.toFixed(2)} Rupas)` : "";
    keyPositivePointsEn.push(`Antardasha lord ${antarStrength.planet} has robust Shadbala strength${rupasStr}.`);
    keyPositivePointsTa.push(`புக்தி நாதன் ${antarStrength.planet} முழுமையான ஷட்பல ஆற்றல் பெற்றுள்ளார்${rupasStr}.`);
  }
  if (antarStrength.ashtakavargaBindus >= 5) {
    keyPositivePointsEn.push(`Auspicious Ashtakavarga transit environment (${antarStrength.ashtakavargaBindus} bindus in ${antarStrength.signName}).`);
    keyPositivePointsTa.push(`அஷ்டகவர்க்கத்தில் ${antarStrength.ashtakavargaBindus} பரல்கள் பெற்று சுப யோக சூழலைத் தருகிறார்.`);
  }
  if (relationship.distanceFromMahaToAntar === 5 || relationship.distanceFromMahaToAntar === 9) {
    keyPositivePointsEn.push("Harmonious Navapanchama (5/9) axis between Dasa and Bhukti lords confers luck and ease.");
    keyPositivePointsTa.push("மகா திசா நாதனுக்கும் புக்தி நாதனுக்கும் இடையே 5/9 நவபஞ்சம சுப அச்சு அமைந்திருப்பது விசேஷ பாக்கியங்களை வழங்கும்.");
  }
  if (relationship.isRajayogaSambandha) {
    keyPositivePointsEn.push("Direct Rajayoga Sambandha elevates authority, honor, and leadership recognition.");
    keyPositivePointsTa.push("கிரக சேர்க்கை மற்றும் பார்வையின் மூலமாக ராஜயோக சம்பந்தம் உண்டாகி கௌரவப் பதவிகளைத் தரும்.");
  }
  if (antarStrength.isVargottama) {
    keyPositivePointsEn.push("Vargottama placement in D1 and D9 solidifies lasting auspicious outcomes.");
    keyPositivePointsTa.push("வர்க்கோத்தம அமைப்பால் D1 மற்றும் D9-ல் சம பலம் பெற்று உறுதியான நற்பலன்களை உறுதி செய்கிறார்.");
  }
  if (andharaStrength.taraBala.isAuspicious) {
    keyPositivePointsEn.push(`Andhara Lord ${andharaStrength.planet} operates in favorable Tara Bala (${andharaStrength.taraBala.nameEn}).`);
    keyPositivePointsTa.push(`அந்திர நாதன் ${andharaStrength.planet} சாதகமான தார பலத்தில் உள்ளார் (${andharaStrength.taraBala.nameTa}).`);
  }

  // Cautions
  if (relationship.isShadashtakaWarning) {
    keyCautionPointsEn.push("Shadashtaka (6/8) mutual distance indicates intermittent friction, delays, or litigation.");
    keyCautionPointsTa.push("திசா-புக்தி அதிபதிகள் 6/8 ஷடாஷ்டக அமைப்பில் இருப்பதால் திடீர் விரயங்கள் மற்றும் விவாதங்களில் விழிப்புணர்வு தேவை.");
  }
  if (relationship.isDvidvadasaWarning) {
    keyCautionPointsEn.push("Dvidvadasa (2/12) placement may prompt unplanned travel expenses and mental restless.");
    keyCautionPointsTa.push("2/12 துவித்வாதச அமைப்பால் தேவையற்ற பிரயாண அலைச்சல் மற்றும் பொருள் விரயங்கள் நேரலாம்.");
  }
  if (antarStrength.isCombust) {
    keyCautionPointsEn.push("Combustion (Asta) alert: conserve vital energy, avoid rushed agreements.");
    keyCautionPointsTa.push("அஸ்தங்க தோஷம்: சூரியனின் சேர்க்கையால் அவசர முடிவுகளைத் தவிர்த்து பொறுமை காக்க வேண்டும்.");
  }
  if (relationship.isMarakaInfluence) {
    keyCautionPointsEn.push("Maraka house activation (2nd / 7th lord): maintain balanced health regimen and road safety.");
    keyCautionPointsTa.push("மாரக ஸ்தான தொடர்பு: ஆரோக்கியப் பராமரிப்பிலும் வாகனப் பயணங்களிலும் எச்சரிக்கை அவசியம்.");
  }
  if (keyCautionPointsEn.length === 0) {
    keyCautionPointsEn.push("No severe afflictions detected in this period alignment.");
    keyCautionPointsTa.push("இந்த தசா-புக்தி அமைப்பில் கடுமையான தோஷங்களோ பாதிப்புகளோ இல்லை.");
  }

  // Mantreswara's Phaladeepika Ch. 20 Bhava Significations
  const bhavaRes = getPhaladeepikaBhavaEffects(antarStrength.housesOwned, antarStrength.planet, antarStrength.dignity);
  const bhavaSignificationsEn = bhavaRes.en;
  const bhavaSignificationsTa = bhavaRes.ta;

  let verdictLabelEn: DasaBukthiAnalysis["verdictLabelEn"] = "Favorable";
  let verdictLabelTa: DasaBukthiAnalysis["verdictLabelTa"] = "அனுகூலமான காலம்";
  let verdictBadgeClass = "bg-emerald-100 text-emerald-800 border-emerald-300";

  if (score >= 80) {
    verdictLabelEn = "Highly Auspicious";
    verdictLabelTa = "மிகவும் சுபகரமானது";
    verdictBadgeClass = "bg-emerald-600 text-white border-emerald-700 shadow-sm";
  } else if (score >= 60) {
    verdictLabelEn = "Favorable";
    verdictLabelTa = "அனுகூலமான காலம்";
    verdictBadgeClass = "bg-teal-100 text-teal-800 border-teal-300";
  } else if (score >= 45) {
    verdictLabelEn = "Mixed / Average";
    verdictLabelTa = "சம பலன் / கலப்பு பலன்";
    verdictBadgeClass = "bg-amber-100 text-amber-800 border-amber-300";
  } else if (score >= 30) {
    verdictLabelEn = "Challenging";
    verdictLabelTa = "கவனமுடன் இருக்க வேண்டிய காலம்";
    verdictBadgeClass = "bg-orange-100 text-orange-800 border-orange-300";
  } else {
    verdictLabelEn = "Sensitive / Precautions Required";
    verdictLabelTa = "கண்ட காலம் / சாந்தி தேவை";
    verdictBadgeClass = "bg-rose-100 text-rose-800 border-rose-300";
  }

  // 5. Classical Combination Texts
  const comb = getClassicalCombinationText(mahaNode.lord, antarNode.lord, relationship, mahaStrength, antarStrength);

  // 6. Category Blocks
  const categories: DasaBukthiAnalysis["categories"] = {
    general: {
      titleEn: "General Overview & Soul Aura",
      titleTa: "பொது பலன் & ஆளுமை பிரகாசம்",
      iconName: "Sparkles",
      favorableScore: score,
      summaryEn: comb.generalEn,
      summaryTa: comb.generalTa,
      pointsEn: [
        `Mahadasha Lord: ${mahaStrength.planet} (${mahaStrength.avasthaNameEn}) situated in House ${mahaStrength.houseOccupied}.`,
        `Antardasha Lord: ${antarStrength.planet} (${antarStrength.avasthaNameEn}) situated in House ${antarStrength.houseOccupied}.`,
        `Axis Relationship: ${relationship.axisNameEn} (${relationship.sambandhaTextEn}).`,
        `Derived House Activation: House ${relationship.derivedHouseFromLagna} counted from Lagna governs core events.`,
        antarStrength.isVargottama ? "Vargottama Strength: Exceptional auspicious resilience across D1 and D9." : "Standard Divisional Dignity.",
      ],
      pointsTa: [
        `மகா திசா நாதன்: ${mahaStrength.planet} (${mahaStrength.avasthaNameTa}) - பாவக அமர்வு: ${mahaStrength.houseOccupied}.`,
        `புக்தி நாதன்: ${antarStrength.planet} (${antarStrength.avasthaNameTa}) - பாவக அமர்வு: ${antarStrength.houseOccupied}.`,
        `கிரக தொடர்பு அச்சு: ${relationship.axisNameTa} (${relationship.sambandhaTextTa}).`,
        `வெளிப்படும் பாவகம்: லக்னத்திலிருந்து ${relationship.derivedHouseFromLagna}-ஆம் பாவத்தின் விவகாரங்கள் முன்னிலை பெறும்.`,
        antarStrength.isVargottama ? "வர்க்கோத்தம பலம்: D1 மற்றும் D9-ல் ஒரே ராசியில் அமர்ந்து அபார யோக பலம் பெற்றுள்ளார்." : "வழக்கமான வர்க்க பலம்.",
      ],
    },
    career: {
      titleEn: "Career, Authority & Business Growth",
      titleTa: "தொழில், வேலை & அந்தஸ்து வளர்ச்சி",
      iconName: "Briefcase",
      favorableScore: Math.min(100, Math.max(20, score + (antarStrength.housesOwned.includes(10) || antarStrength.housesOwned.includes(1) ? 12 : 0))),
      summaryEn: comb.careerEn,
      summaryTa: comb.careerTa,
      pointsEn: [
        antarStrength.housesOwned.includes(10) || antarStrength.housesOwned.includes(9)
          ? "Strong Raja Yoga connection with 9th/10th houses signifies official elevation."
          : "Professional stability maintained through systematic duty.",
        `Timing of success: ${relationship.deliveryWindowTextEn}`,
        antarStrength.shadbalaPass
          ? "Planet Shadbala is robust, granting command over subordinates and executive clarity."
          : "Sub-period lord is slightly weak in Shadbala; avoid workplace friction or administrative delays.",
      ],
      pointsTa: [
        antarStrength.housesOwned.includes(10) || antarStrength.housesOwned.includes(9)
          ? "9 மற்றும் 10-ஆம் அதிபதிகளின் தொடர்பு உத்தியோகத்தில் புதிய பொறுப்புகளையும் பதவி யோகத்தையும் தரும்."
          : "வழக்கமான பணிகளில் நிலையான முன்னேற்றமும் நற்பெயரும் தொடரும்.",
        `வெற்றி கைகூடும் காலம்: ${relationship.deliveryWindowTextTa}`,
        antarStrength.shadbalaPass
          ? "கிரகம் ஷட்பல விதிகளின்படி முழு பலம் பெற்றுள்ளதால் மேலதிகாரிகள் மற்றும் அரசின் ஆதரவு கிட்டும்."
          : "புக்தி நாதன் குறைந்த பலத்தில் உள்ளதால் சக ஊழியர்களிடம் நிதானமும் சாதுரியமும் தேவை.",
      ],
    },
    wealth: {
      titleEn: "Wealth, Property & Vehicles",
      titleTa: "தனம், சொத்து & வாகன சுகம்",
      iconName: "Coins",
      favorableScore: Math.min(100, Math.max(15, score + (antarStrength.housesOwned.includes(2) || antarStrength.housesOwned.includes(11) || antarStrength.housesOwned.includes(4) ? 10 : 0))),
      summaryEn: comb.wealthEn,
      summaryTa: comb.wealthTa,
      pointsEn: [
        antarStrength.ashtakavargaBindus >= 5
          ? `Ashtakavarga score is high (${antarStrength.ashtakavargaBindus} bindus), assuring continuous inflow of liquid wealth.`
          : `Ashtakavarga score is moderate (${antarStrength.ashtakavargaBindus} bindus); manage assets with prudence.`,
        antarStrength.housesOwned.includes(4) || antarStrength.housesOwned.includes(2)
          ? "Auspicious indications for land purchase, house renovation, or acquiring vehicle comforts."
          : "Favorable conditions for long-term savings and productive fixed deposits.",
      ],
      pointsTa: [
        antarStrength.ashtakavargaBindus >= 5
          ? `அஷ்டகவர்க பரல்கள் உயர்வாக (${antarStrength.ashtakavargaBindus} புள்ளிகள்) உள்ளதால் பணப்புழக்கமும் சேமிப்பும் அதிகரிக்கும்.`
          : `அஷ்டகவர்க பரல்கள் நடுத்தரமாக (${antarStrength.ashtakavargaBindus} புள்ளிகள்) உள்ளதால் வரவுக்கேற்ற செலவுகள் இருக்கும்.`,
        antarStrength.housesOwned.includes(4) || antarStrength.housesOwned.includes(2)
          ? "வீடு, மனை வாங்குதல், வாகன யோகம் மற்றும் பூமி வழியே தன லாபம் உண்டாகும்."
          : "நிலையான முதலீடுகள் மற்றும் சேமிப்புத் திட்டங்கள் எதிர்கால நலம் பயக்கும்.",
      ],
    },
    marriage: {
      titleEn: "Marriage, Spouse & Relationships",
      titleTa: "திருமணம், வாழ்க்கைத்துணை & குடும்ப வாழ்க்கை",
      iconName: "Heart",
      favorableScore: Math.min(100, Math.max(20, score + (antarStrength.housesOwned.includes(7) || antarStrength.planet === "Venus" ? 10 : 0))),
      summaryEn: comb.marriageEn,
      summaryTa: comb.marriageTa,
      pointsEn: [
        antarStrength.housesOwned.includes(7) || antarStrength.housesOwned.includes(2) || antarStrength.planet === "Venus" || antarStrength.planet === "Jupiter"
          ? "Classical marriage-timing window active: strong indicators for wedlock or celebrating anniversaries."
          : "Domestic peace prospers through affectionate companionship and shared responsibilities.",
        relationship.isShadashtakaWarning
          ? "6/8 Shadashtaka axis warning: resolve misunderstandings swiftly with empathetic dialogue."
          : "Constructive relationship with in-laws and extended family.",
      ],
      pointsTa: [
        antarStrength.housesOwned.includes(7) || antarStrength.housesOwned.includes(2) || antarStrength.planet === "Venus" || antarStrength.planet === "Jupiter"
          ? "சாஸ்திர விதிகளின்படி திருமண யோகம் கைகூடும் காலம்; வரன் அமைதல் மற்றும் மங்கலப் பேச்சுகள் வெற்றியாகும்."
          : "தம்பதியர் இடையே அன்பும், குடும்பத்தில் மகிழ்ச்சியான நல்லிணக்கமும் நிலவும்.",
        relationship.isShadashtakaWarning
          ? "6/8 ஷடாஷ்டக எச்சரிக்கை: தம்பதியர் இடையே வீண் விவாதங்களைத் தவிர்த்து ஒருவருக்கொருவர் விட்டுக்கொடுத்துச் செல்லவும்."
          : "உறவினர்கள் மற்றும் மாமியார் வழி உறவுகளுடன் சுமுகமான நட்பு தொடரும்.",
      ],
    },
    educationChildren: {
      titleEn: "Education, Intellect & Children",
      titleTa: "கல்வி, புத்தி & குழந்தைகள் நலன்",
      iconName: "Baby",
      favorableScore: Math.min(100, Math.max(25, score + (antarStrength.housesOwned.includes(5) || antarStrength.planet === "Mercury" || antarStrength.planet === "Jupiter" ? 12 : 0))),
      summaryEn: comb.educationEn,
      summaryTa: comb.educationTa,
      pointsEn: [
        antarStrength.housesOwned.includes(5) || antarStrength.planet === "Jupiter"
          ? "5th house activation: auspicious for progeny conception, child prosperity, and creative masterstrokes."
          : "Intellectual retention and practical competence in specialized skill domains.",
        "Success in higher learning, professional certifications, or strategic research.",
      ],
      pointsTa: [
        antarStrength.housesOwned.includes(5) || antarStrength.planet === "Jupiter"
          ? "5-ஆம் பாவக பலன்: புத்திர பாக்கியம், குழந்தைகளின் கல்வி வளர்ச்சி மற்றும் சாதனைகள் மனமகிழ்ச்சி தரும்."
          : "புத்திக் கூர்மை, ஞாபக சக்தி மற்றும் புதிய திறன்களை எளிதில் கற்கும் ஆர்வம் மிகும்.",
        "உயர்கல்வி, தொழில்சார் சான்றிதழ்கள் மற்றும் போட்டித் தேர்வுகளில் நல்ல வெற்றி கிடைக்கும்.",
      ],
    },
    healthMaraka: {
      titleEn: "Health, Vitality & Cautionary Alerts",
      titleTa: "உடல் நலம், கண்டங்கள் & எச்சரிக்கைகள்",
      iconName: "ShieldAlert",
      favorableScore: Math.max(15, 100 - score + (relationship.isMarakaInfluence ? 25 : 0)),
      summaryEn: comb.healthEn,
      summaryTa: comb.healthTa,
      pointsEn: [
        relationship.isMarakaInfluence
          ? "Maraka lord confluence: maintain disciplined wellness habits and avoid hazardous travels."
          : "Vitality is preserved under harmonious planetary shielding.",
        antarStrength.isCombust
          ? "Combustion (Asta) alert: protect against heat, dehydration, and mental fatigue."
          : "Strong metabolic endurance and sound restorative sleep.",
      ],
      pointsTa: [
        relationship.isMarakaInfluence
          ? "மாரக ஸ்தான தொடர்பு உள்ளதால் ஆரோக்கியத்தில் கூடுதல் அக்கறையும், தொலைதூர பயணங்களில் எச்சரிக்கையும் தேவை."
          : "கிரகங்களின் சுப பார்வையால் பெரிய நோய்களின்றி உடல் நலம் சீராகப் பாதுகாக்கப்படும்.",
        antarStrength.isCombust
          ? "அஸ்தங்க தோஷம்: உஷ்ணம், தலைவலி, நீர்ச்சத்து குறைபாடு ஏற்படாமல் போதிய நீர் அருந்தவும்."
          : "மன அமைதியும், நல்ல தூக்கமும், சீரான உணவு முறையும் உடலை சுறுசுறுப்பாக வைத்திருக்கும்.",
      ],
    },
  };

  // 7. Sun Transit Manifestation Window (Chapter 2, Rule 9)
  const antarSignsOwned = SIGNS_OWNED[antarStrength.planet] || [antarStrength.signIndex];
  const signsRuledEn = antarSignsOwned.map((s) => ZODIAC_SIGNS_EN[s - 1]);
  const signsRuledTa = antarSignsOwned.map((s) => ZODIAC_SIGNS_TA[s - 1]);

  const sunTransit: SunTransitManifestation = {
    signsRuledEn,
    signsRuledTa,
    manifestationWindowEn: `When transit Sun passes through ${signsRuledEn.join(" or ")} (Approx. seasonal transit window).`,
    manifestationWindowTa: `கோச்சார சூரிய பகவான் ${signsRuledTa.join(" அல்லது ")} ராசியில் சஞ்சரிக்கும் காலகட்டத்தில் இந்த புக்தியின் முக்கிய பலன்கள் உச்சமாக வெளிப்படும்.`,
    descriptionEn: `According to Chapter 2 (Rule 9) of Krishan Kant Bhardwaj's Vimshottari Dasha treatise: During any Antardasha, when the transit Sun transits into the zodiac sign(s) ruled by that Antardasha lord, the auspicious or inauspicious events of the period reach peak manifestation.`,
    descriptionTa: `கிருஷன் காந்த் பரத்வாஜ் அவர்களின் விம்சோத்தரி தசா விதிகளின்படி (அத்தியாயம் 2, விதி 9): எந்த ஒரு புக்தி நடக்கும் போதும், அந்த புக்தி நாதனின் சொந்த ராசிகளில் கோச்சார சூரியன் பிரவேசிக்கும் மாதத்தில் அப்புக்தியின் நற்பலன்களோ அல்லது சோதனைகளோ மிகத் தெளிவாகவும் துல்லியமாகவும் நடந்தேறும்.`,
  };

  // 8. Remedial Measures
  const deityMap: Record<string, { en: string; ta: string }> = {
    Sun: { en: "Lord Shiva & Surya Narayana", ta: "சிவபெருமான் & சூரிய நாராயணர்" },
    Moon: { en: "Goddess Parvati & Sri Chandramouleeshwara", ta: "அம்பாள் & சந்திரமௌலீஸ்வரர்" },
    Mars: { en: "Lord Murugan (Subramanya) & Sri Narasimha", ta: "முருகப்பெருமான் & ஸ்ரீ நரசிம்மர்" },
    Mercury: { en: "Lord Maha Vishnu & Sri Hayagriva", ta: "மகாவிஷ்ணு & ஸ்ரீ ஹயக்ரீவர்" },
    Jupiter: { en: "Lord Dakshinamurthy & Brihaspati", ta: "ஸ்ரீ தட்சிணாமூர்த்தி & குரு பகவான்" },
    Venus: { en: "Goddess Mahalakshmi & Sri Ranganatha", ta: "மகாலட்சுமி தாயார் & ஸ்ரீ ரங்கநாதர்" },
    Saturn: { en: "Lord Hanuman & Lord Sastha (Ayyappa)", ta: "ஆஞ்சநேயர் & தர்ம சாஸ்தா (ஐயப்பன்)" },
    Rahu: { en: "Goddess Durga & Sri Nagaraja", ta: "துர்க்கை அம்மன் & நாகராஜர்" },
    Ketu: { en: "Lord Ganesha & Sri Chitragupta", ta: "விநாயகப் பெருமான் & கேது பகவான்" },
  };

  const gemstoneMap: Record<string, { en: string; ta: string }> = {
    Sun: { en: "Ruby (Manikyam)", ta: "மாணிக்கம் (Ruby)" },
    Moon: { en: "Pearl (Muthu)", ta: "முத்து (Pearl)" },
    Mars: { en: "Red Coral (Pavazham)", ta: "பவளம் (Red Coral)" },
    Mercury: { en: "Emerald (Maragatham)", ta: "மரகதம் (Emerald)" },
    Jupiter: { en: "Yellow Sapphire (Pushparagam)", ta: "மஞ்சள் புஷ்பராகம் (Yellow Sapphire)" },
    Venus: { en: "Diamond / White Zircon (Vairam)", ta: "வைரம் அல்லது வெள்ளைக் கல் (Diamond)" },
    Saturn: { en: "Blue Sapphire / Amethyst (Neelam)", ta: "நீலம் அல்லது அமேதிஸ்ட் (Blue Sapphire)" },
    Rahu: { en: "Hessonite (Gomedakam)", ta: "கோமேதகம் (Hessonite)" },
    Ketu: { en: "Cat's Eye (Vaidooryam)", ta: "வைடூரியம் (Cat's Eye)" },
  };

  const colorMap: Record<string, { en: string; ta: string }> = {
    Sun: { en: "Copper red, bright orange, gold", ta: "செந்நிறம், ஆரஞ்சு, தங்கம்" },
    Moon: { en: "Pure white, silver, pearl cream", ta: "வெள்ளை, வெள்ளி நிறம், பால் வண்ணம்" },
    Mars: { en: "Coral red, deep vermilion", ta: "சிவப்பு, இரத்தச் சிவப்பு" },
    Mercury: { en: "Emerald green, parrot green", ta: "பச்சை, கிளிப்பச்சை" },
    Jupiter: { en: "Golden yellow, saffron, turmeric", ta: "மஞ்சள், பொன்னிறம், காவி" },
    Venus: { en: "Sparkling white, cream, variegated silks", ta: "வெள்ளை, பட்டு நிறம், கிரீம்" },
    Saturn: { en: "Navy blue, black, dark grey", ta: "கருநீலம், கருப்பு, சாம்பல்" },
    Rahu: { en: "Smoky grey, dark blue, ultramarine", ta: "புகை நிறம், கரும் நீலம்" },
    Ketu: { en: "Multi-color, earthy brown, terracotta", ta: "பலவண்ணம், காவி, செம்பழுப்பு" },
  };

  const dObj = deityMap[antarStrength.planet] || deityMap["Sun"];
  const gObj = gemstoneMap[antarStrength.planet] || gemstoneMap["Sun"];
  const cObj = colorMap[antarStrength.planet] || colorMap["Sun"];

  const remedies: RemedialMeasure = {
    deityEn: dObj.en,
    deityTa: dObj.ta,
    mantraEn: comb.remedyMantraEn,
    mantraTa: comb.remedyMantraTa,
    charityEn: comb.remedyCharityEn,
    charityTa: comb.remedyCharityTa,
    gemstoneEn: gObj.en,
    gemstoneTa: gObj.ta,
    colorEn: cObj.en,
    colorTa: cObj.ta,
    generalRemedyEn: `Propitiate ${antarStrength.planet} during this Antardasha period by honoring parents/elders, visiting temples on its ruling weekday, and meditating on the divine light.`,
    generalRemedyTa: `இந்த ${antarStrength.planet} புக்தி காலத்தில் பெரியோர்களை மதித்து, குறிப்பிட்ட கிழமைகளில் கோவிலுக்குச் சென்று நெய் தீபம் ஏற்றி மனமுருகி வேண்டினால் அனைத்து தோஷங்களும் நீங்கி நற்பலன்கள் கூடும்.`,
  };

  return {
    mahadashaLord: mahaStrength.planet,
    antardashaLord: antarStrength.planet,
    pratyantardashaLord: selectedAndharLord,
    startDateIso,
    endDateIso,
    startDateFormatted,
    endDateFormatted,
    durationYearsFormatted,
    ageAtStartFormatted,
    ageAtEndFormatted,
    isActiveNow,
    isPast,
    isFuture,
    progressPercent,
    overallAuspiciousScore: score,
    dasaBukthiPositiveScore,
    dasaBukthiNegativeScore,
    andharaPositiveScore,
    andharaNegativeScore,
    keyPositivePointsEn,
    keyPositivePointsTa,
    keyCautionPointsEn,
    keyCautionPointsTa,
    bhavaSignificationsEn,
    bhavaSignificationsTa,
    verdictLabelEn,
    verdictLabelTa,
    verdictBadgeClass,
    summaryQuoteEn: comb.summaryQuoteEn,
    summaryQuoteTa: comb.summaryQuoteTa,
    mahaStrength,
    antarStrength,
    relationship,
    andhara: andharaDetail,
    availableAndharas,
    categories,
    sunTransit,
    remedies,
    classicalCitation: "Mantreswara's Phaladeepika (Ch. 19-21) & Krishan Kant Bhardwaj's Vimshottari Dasha System.",
  };
}
