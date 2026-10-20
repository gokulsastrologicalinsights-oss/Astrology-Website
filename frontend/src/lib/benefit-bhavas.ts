/**
 * Four-Category Benefit Bhavas Calculation Service (Frontend)
 *
 * Required calculation order:
 * 1. Star Lord Occupied House  — house occupied by period lord's Nakshatra star lord
 * 2. Star Lord Owned Houses    — houses owned by that star lord
 * 3. Period Lord Occupied House — house occupied by planet ruling current period
 * 4. Period Lord Owned Houses  — houses owned by planet ruling current period
 *
 * Rahu / Ketu convention:
 * - Rahu and Ketu own no houses.
 * - If star lord is Rahu or Ketu, category 2 is omitted.
 * - If period lord is Rahu or Ketu, category 4 is omitted.
 * - Only the applicable category is omitted; remaining values are NOT shifted.
 */

import type { PlanetInfo, HouseInfo, AscendantInfo, DasaPeriodNode } from "./types";

export const VIMSHOTTARI_LORDS: string[] = [
  "Ketu",
  "Venus",
  "Sun",
  "Moon",
  "Mars",
  "Rahu",
  "Jupiter",
  "Saturn",
  "Mercury",
];

const NAKSHATRA_SPAN_DEG = 360.0 / 27.0; // 13° 20' = 13.333333333333334°

export const SIGNS_RULED_BY: Record<string, string[]> = {
  Sun: ["Leo"],
  Moon: ["Cancer"],
  Mars: ["Aries", "Scorpio"],
  Mercury: ["Gemini", "Virgo"],
  Jupiter: ["Sagittarius", "Pisces"],
  Venus: ["Taurus", "Libra"],
  Saturn: ["Capricorn", "Aquarius"],
  Rahu: [],
  Ketu: [],
};

export const ZODIAC_SIGNS: string[] = [
  "Aries",
  "Taurus",
  "Gemini",
  "Cancer",
  "Leo",
  "Virgo",
  "Libra",
  "Scorpio",
  "Sagittarius",
  "Capricorn",
  "Aquarius",
  "Pisces",
];

export const SIGN_LORDS: Record<string, string> = {
  Aries: "Mars",
  Taurus: "Venus",
  Gemini: "Mercury",
  Cancer: "Moon",
  Leo: "Sun",
  Virgo: "Mercury",
  Libra: "Venus",
  Scorpio: "Mars",
  Sagittarius: "Jupiter",
  Capricorn: "Saturn",
  Aquarius: "Saturn",
  Pisces: "Jupiter",
};

const PLANET_ALIASES: Record<string, string> = {
  sun: "Sun",
  surya: "Sun",
  su: "Sun",
  moon: "Moon",
  chandra: "Moon",
  mo: "Moon",
  mars: "Mars",
  mangal: "Mars",
  mangala: "Mars",
  sevvai: "Mars",
  ma: "Mars",
  mercury: "Mercury",
  budh: "Mercury",
  budha: "Mercury",
  me: "Mercury",
  jupiter: "Jupiter",
  guru: "Jupiter",
  ju: "Jupiter",
  venus: "Venus",
  sukra: "Venus",
  sukran: "Venus",
  shukra: "Venus",
  shukran: "Venus",
  ve: "Venus",
  saturn: "Saturn",
  shani: "Saturn",
  sani: "Saturn",
  sa: "Saturn",
  rahu: "Rahu",
  ra: "Rahu",
  ketu: "Ketu",
  ke: "Ketu",
};

export function normalizePlanetName(name: string): string {
  if (!name) return "";
  const clean = name.trim().toLowerCase();
  return PLANET_ALIASES[clean] || (name.charAt(0).toUpperCase() + name.slice(1).toLowerCase());
}

/**
 * Determine the Nakshatra star lord of any sidereal longitude [0, 360).
 */
export function resolveStarLord(longitude: number): string {
  const norm = ((longitude % 360.0) + 360.0) % 360.0;
  const nakIdx = Math.floor(norm / NAKSHATRA_SPAN_DEG);
  return VIMSHOTTARI_LORDS[nakIdx % 9];
}

/**
 * Calculate the house (1-12) containing a longitude under 12 house cusps.
 */
export function houseOfLongitude(lon: number, cusps: number[]): number {
  if (!cusps || cusps.length < 12) return 1;
  const lonNorm = ((lon % 360.0) + 360.0) % 360.0;
  const c0 = ((cusps[0] % 360.0) + 360.0) % 360.0;
  const lonRel = ((lonNorm - c0 + 360.0) % 360.0);

  for (let i = 0; i < 12; i++) {
    const cRel = ((cusps[i] - c0 + 360.0) % 360.0);
    const nxtRel = i < 11 ? ((cusps[i + 1] - c0 + 360.0) % 360.0) : 360.0;
    if (cRel <= lonRel && lonRel < nxtRel) {
      return i + 1;
    }
  }
  return 12;
}

/**
 * Determine the house occupied by a planet.
 * In Vedic Vimshottari Dasa Benefit Bhavas, the planet's house occupancy
 * is canonically determined by Rashi-Bhava (sign relative to the Ascendant sign).
 */
export function getPlanetOccupiedHouse(
  planetLon: number | null | undefined,
  cusps?: number[],
  ascendantSignIdx?: number,
  preferRashi: boolean = true
): number | null {
  if (planetLon === null || planetLon === undefined || isNaN(planetLon)) {
    return null;
  }
  if (preferRashi && ascendantSignIdx && ascendantSignIdx >= 1 && ascendantSignIdx <= 12) {
    const planetSign = Math.floor((((planetLon % 360.0) + 360.0) % 360.0) / 30.0) + 1;
    return (((planetSign - ascendantSignIdx + 12) % 12) + 1);
  }
  if (cusps && cusps.length >= 12) {
    return houseOfLongitude(planetLon, cusps);
  }
  if (ascendantSignIdx && ascendantSignIdx >= 1 && ascendantSignIdx <= 12) {
    const planetSign = Math.floor((((planetLon % 360.0) + 360.0) % 360.0) / 30.0) + 1;
    return (((planetSign - ascendantSignIdx + 12) % 12) + 1);
  }
  return null;
}

/**
 * Determine the houses owned by a planet.
 * Rahu and Ketu own NO houses (returns empty array).
 */
export function getPlanetOwnedHouses(
  planetName: string,
  ascendantSignIdx?: number,
  houseSignNames?: string[],
  preferRashi: boolean = true
): number[] {
  const canonical = normalizePlanetName(planetName);
  if (canonical === "Rahu" || canonical === "Ketu") {
    return [];
  }

  // 1. Canonical Vedic WholeSign calculation from Ascendant sign index
  if (preferRashi && ascendantSignIdx && ascendantSignIdx >= 1 && ascendantSignIdx <= 12) {
    const signsRuled = SIGNS_RULED_BY[canonical] || [];
    const owned: number[] = [];
    for (const sName of signsRuled) {
      const sIdx = ZODIAC_SIGNS.indexOf(sName) + 1;
      const h = (((sIdx - ascendantSignIdx + 12) % 12) + 1);
      owned.push(h);
    }
    return owned.sort((a, b) => a - b);
  }

  // 2. If house sign names are provided from 12 houses
  if (houseSignNames && houseSignNames.length === 12) {
    const owned: number[] = [];
    houseSignNames.forEach((sName, idx) => {
      if (SIGN_LORDS[sName] === canonical) {
        owned.push(idx + 1);
      }
    });
    if (owned.length > 0) {
      return owned.sort((a, b) => a - b);
    }
  }

  // 3. Fallback WholeSign calculation from Ascendant sign index
  if (ascendantSignIdx && ascendantSignIdx >= 1 && ascendantSignIdx <= 12) {
    const signsRuled = SIGNS_RULED_BY[canonical] || [];
    const owned: number[] = [];
    for (const sName of signsRuled) {
      const sIdx = ZODIAC_SIGNS.indexOf(sName) + 1;
      const h = (((sIdx - ascendantSignIdx + 12) % 12) + 1);
      owned.push(h);
    }
    return owned.sort((a, b) => a - b);
  }

  return [];
}

/**
 * Format available categories into compact pipe-separated string.
 */
export function formatBenefitBhavas(
  cat1StarLordOcc: number | null | undefined,
  cat2StarLordOwn: number[],
  cat3PeriodLordOcc: number | null | undefined,
  cat4PeriodLordOwn: number[],
  starLord: string,
  periodLord: string
): string {
  const canonicalSl = normalizePlanetName(starLord);
  const canonicalPl = normalizePlanetName(periodLord);

  const available: string[] = [];

  // Category 1: Star Lord Occupied House
  if (cat1StarLordOcc !== null && cat1StarLordOcc !== undefined) {
    available.push(cat1StarLordOcc.toString());
  } else {
    available.push("Unavailable");
  }

  // Category 2: Star Lord Owned Houses (OMITTED for Rahu and Ketu)
  if (canonicalSl !== "Rahu" && canonicalSl !== "Ketu") {
    if (cat2StarLordOwn && cat2StarLordOwn.length > 0) {
      available.push(cat2StarLordOwn.slice().sort((a, b) => a - b).join(", "));
    } else {
      available.push("Unavailable");
    }
  }

  // Category 3: Period Lord Occupied House
  if (cat3PeriodLordOcc !== null && cat3PeriodLordOcc !== undefined) {
    available.push(cat3PeriodLordOcc.toString());
  } else {
    available.push("Unavailable");
  }

  // Category 4: Period Lord Owned Houses (OMITTED for Rahu and Ketu)
  if (canonicalPl !== "Rahu" && canonicalPl !== "Ketu") {
    if (cat4PeriodLordOwn && cat4PeriodLordOwn.length > 0) {
      available.push(cat4PeriodLordOwn.slice().sort((a, b) => a - b).join(", "));
    } else {
      available.push("Unavailable");
    }
  }

  return available.join(" | ");
}

export interface PlanetContext {
  name: string;
  longitude: number;
  starLord: string;
  occupiedHouse: number | null;
  ownedHouses: number[];
}

export interface BenefitBhavasResult {
  periodLord: string;
  starLord: string;
  starLordOccupied: number | null;
  starLordOwned: number[];
  periodLordOccupied: number | null;
  periodLordOwned: number[];
  formatted: string;
}

/**
 * Build dictionary of PlanetContext from Horoscope response.
 */
export function buildPlanetContexts(
  planets: PlanetInfo[],
  ascendant: AscendantInfo,
  houses?: HouseInfo[],
  preferRashi: boolean = true
): Record<string, PlanetContext> {
  const contexts: Record<string, PlanetContext> = {};

  const cusps = houses && houses.length === 12 ? houses.map((h) => h.cusp_degree) : undefined;
  const houseSignNames = houses && houses.length === 12 ? houses.map((h) => h.sign_name) : undefined;
  const ascSignIdx = ascendant.sign_index;

  const rawMap: Record<string, PlanetInfo> = {};
  for (const p of planets) {
    rawMap[normalizePlanetName(p.name)] = p;
  }

  for (const lord of VIMSHOTTARI_LORDS) {
    const p = rawMap[lord];
    let lon = p?.longitude;
    let starLord = p?.nakshatra?.lord;

    if (lon !== undefined && lon !== null) {
      if (!starLord) {
        starLord = resolveStarLord(lon);
      }
      const occ = getPlanetOccupiedHouse(lon, cusps, ascSignIdx, preferRashi);
      const owned = getPlanetOwnedHouses(lord, ascSignIdx, houseSignNames, preferRashi);
      contexts[lord] = {
        name: lord,
        longitude: lon,
        starLord,
        occupiedHouse: occ,
        ownedHouses: owned,
      };
    } else {
      contexts[lord] = {
        name: lord,
        longitude: 0,
        starLord: "Unknown",
        occupiedHouse: null,
        ownedHouses: getPlanetOwnedHouses(lord, ascSignIdx, houseSignNames, preferRashi),
      };
    }
  }

  return contexts;
}

/**
 * Calculate Benefit Bhavas for a specific period lord.
 */
export function calculateBenefitBhavas(
  periodLord: string,
  contexts: Record<string, PlanetContext>
): BenefitBhavasResult {
  const plName = normalizePlanetName(periodLord);
  const plCtx = contexts[plName];

  if (!plCtx || plCtx.occupiedHouse === null) {
    const sl = plCtx?.starLord || "Unknown";
    return {
      periodLord: plName,
      starLord: sl,
      starLordOccupied: null,
      starLordOwned: [],
      periodLordOccupied: null,
      periodLordOwned: [],
      formatted: "Unavailable",
    };
  }

  const slName = normalizePlanetName(plCtx.starLord);
  const slCtx = contexts[slName];

  const slOcc = slCtx ? slCtx.occupiedHouse : null;
  const slOwn = slCtx ? slCtx.ownedHouses : [];
  const plOcc = plCtx.occupiedHouse;
  const plOwn = plCtx.ownedHouses;

  const formatted = formatBenefitBhavas(slOcc, slOwn, plOcc, plOwn, slName, plName);

  return {
    periodLord: plName,
    starLord: slName,
    starLordOccupied: slOcc,
    starLordOwned: slName !== "Rahu" && slName !== "Ketu" ? slOwn : [],
    periodLordOccupied: plOcc,
    periodLordOwned: plName !== "Rahu" && plName !== "Ketu" ? plOwn : [],
    formatted,
  };
}

/**
 * Recursively enrich every node across all 5 Dasa levels.
 * Never copies a parent's Benefit Bhavas into a child period.
 */
export function enrichDasaTreeWithBenefitBhavas(
  tree: DasaPeriodNode[],
  contexts: Record<string, PlanetContext>
): void {
  for (const node of tree) {
    if (node.lord) {
      const res = calculateBenefitBhavas(node.lord, contexts);
      node.star_lord = res.starLord;
      node.benefit_bhavas = res.formatted;
      node.period_lord_occupied = res.periodLordOccupied;
      node.star_lord_occupied = res.starLordOccupied;
      node.period_lord_owned = res.periodLordOwned;
      node.star_lord_owned = res.starLordOwned;
      node.benefit_bhavas_detail = {
        star_lord: res.starLord,
        period_lord: res.periodLord,
        star_lord_houses: res.starLordOccupied,
        star_lord_owned_houses: res.starLordOwned,
        planet_placement_house: res.periodLordOccupied,
        planet_owned_houses: res.periodLordOwned,
        formatted: res.formatted,
      };
    }
    if (node.sub_periods && node.sub_periods.length > 0) {
      enrichDasaTreeWithBenefitBhavas(node.sub_periods, contexts);
    }
  }
}
