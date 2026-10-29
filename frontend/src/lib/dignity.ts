/**
 * Navagraha Dignity & Directional Strength (Dik Balam) Engine
 *
 * Classical Vedic Rules:
 * -------------------------------------------------------------
 * Graha            Ucham (Exaltation)       Neecham (Debilitation)   Dik Balam (Directional Strength)
 * Sun (Suriyan)    Mesham (Aries) 10°       Thulam (Libra) 10°       10th house (South)
 * Moon (Chandran)  Rishabam (Taurus) 3°     Viruchigam (Scorpio) 3°  4th house (North)
 * Mars (Sevvai)    Magaram (Capricorn) 28°  Katakam (Cancer) 28°     10th house (South)
 * Mercury (Budhan) Kanni (Virgo) 15°        Meenam (Pisces) 15°      1st house, Lagna (East)
 * Jupiter (Guru)   Katakam (Cancer) 5°      Magaram (Capricorn) 5°   1st house, Lagna (East)
 * Venus (Sukran)   Meenam (Pisces) 27°      Kanni (Virgo) 27°        4th house (North)
 * Saturn (Sani)    Thulam (Libra) 20°       Mesham (Aries) 20°       7th house (West)
 * Rahu             Rishabam (Taurus)        Viruchigam (Scorpio)     —
 * Ketu             Viruchigam (Scorpio)     Rishabam (Taurus)        —
 *
 * Color Standards:
 * - Ucham (Exalted): Green (#16A34A)
 * - Neecham (Debilitated): Red (#DC2626)
 * - Dik Balam (Directional Strength): Yellow / Golden Yellow (#CA8A04)
 */

export interface GrahaRule {
  canonicalName: string;
  nameTa: string;
  uchamSign: number;       // 1 to 12
  uchamDeepDeg: number;    // Point of deepest exaltation
  neechamSign: number;     // 1 to 12
  neechamDeepDeg: number;  // Point of deepest debilitation
  dikBalaHouse?: number;   // 1, 4, 7, 10
  directionEn?: string;
  directionTa?: string;
}

export const NAVAGRAHA_RULES: Record<string, GrahaRule> = {
  Sun: {
    canonicalName: "Sun",
    nameTa: "சூரியன்",
    uchamSign: 1, // Mesham (Aries)
    uchamDeepDeg: 10,
    neechamSign: 7, // Thulam (Libra)
    neechamDeepDeg: 10,
    dikBalaHouse: 10, // 10th house (South)
    directionEn: "10th House (South)",
    directionTa: "10-ம் வீடு (தெற்கு)",
  },
  Moon: {
    canonicalName: "Moon",
    nameTa: "சந்திரன்",
    uchamSign: 2, // Rishabam (Taurus)
    uchamDeepDeg: 3,
    neechamSign: 8, // Viruchigam (Scorpio)
    neechamDeepDeg: 3,
    dikBalaHouse: 4, // 4th house (North)
    directionEn: "4th House (North)",
    directionTa: "4-ம் வீடு (வடக்கு)",
  },
  Mars: {
    canonicalName: "Mars",
    nameTa: "செவ்வாய்",
    uchamSign: 10, // Magaram (Capricorn)
    uchamDeepDeg: 28,
    neechamSign: 4, // Katakam (Cancer)
    neechamDeepDeg: 28,
    dikBalaHouse: 10, // 10th house (South)
    directionEn: "10th House (South)",
    directionTa: "10-ம் வீடு (தெற்கு)",
  },
  Mercury: {
    canonicalName: "Mercury",
    nameTa: "புதன்",
    uchamSign: 6, // Kanni (Virgo)
    uchamDeepDeg: 15,
    neechamSign: 12, // Meenam (Pisces)
    neechamDeepDeg: 15,
    dikBalaHouse: 1, // 1st house / Lagna (East)
    directionEn: "1st House / Lagna (East)",
    directionTa: "1-ம் வீடு / லக்னம் (கிழக்கு)",
  },
  Jupiter: {
    canonicalName: "Jupiter",
    nameTa: "குரு",
    uchamSign: 4, // Katakam (Cancer)
    uchamDeepDeg: 5,
    neechamSign: 10, // Magaram (Capricorn)
    neechamDeepDeg: 5,
    dikBalaHouse: 1, // 1st house / Lagna (East)
    directionEn: "1st House / Lagna (East)",
    directionTa: "1-ம் வீடு / லக்னம் (கிழக்கு)",
  },
  Venus: {
    canonicalName: "Venus",
    nameTa: "சுக்கிரன்",
    uchamSign: 12, // Meenam (Pisces)
    uchamDeepDeg: 27,
    neechamSign: 6, // Kanni (Virgo)
    neechamDeepDeg: 27,
    dikBalaHouse: 4, // 4th house (North)
    directionEn: "4th House (North)",
    directionTa: "4-ம் வீடு (வடக்கு)",
  },
  Saturn: {
    canonicalName: "Saturn",
    nameTa: "சனி",
    uchamSign: 7, // Thulam (Libra)
    uchamDeepDeg: 20,
    neechamSign: 1, // Mesham (Aries)
    neechamDeepDeg: 20,
    dikBalaHouse: 7, // 7th house (West)
    directionEn: "7th House (West)",
    directionTa: "7-ம் வீடு (மேற்கு)",
  },
  Rahu: {
    canonicalName: "Rahu",
    nameTa: "ராகு",
    uchamSign: 2, // Rishabam (Taurus)
    uchamDeepDeg: 20,
    neechamSign: 8, // Viruchigam (Scorpio)
    neechamDeepDeg: 20,
  },
  Ketu: {
    canonicalName: "Ketu",
    nameTa: "கேது",
    uchamSign: 8, // Viruchigam (Scorpio)
    uchamDeepDeg: 20,
    neechamSign: 2, // Rishabam (Taurus)
    neechamDeepDeg: 20,
  },
};

/**
 * Normalizes input name across English, Tamil, and common transliterations
 */
export function normalizePlanetKey(planetName: string): string | null {
  if (!planetName) return null;
  const s = planetName.trim().toLowerCase();

  // Venus (check before Sun because Sukran starts with 'su')
  if (s.startsWith("suk") || s.startsWith("shuk") || s.startsWith("ve") || s.includes("venus") || s.includes("சுக்") || s.includes("வெள்ளி") || s.includes("shukra") || s.includes("sukra")) return "Venus";

  // Saturn (check before Sun because Sani starts with 'sa')
  if (s.startsWith("san") || s.startsWith("shan") || s.startsWith("sat") || s.includes("saturn") || s.includes("சனி") || s.includes("manda")) return "Saturn";

  // Sun
  if (s.startsWith("su") || s.includes("sun") || s.includes("சூரி") || s.includes("ஞாயிறு") || s.includes("surya") || s.includes("suriyan")) return "Sun";

  // Moon
  if (s.startsWith("mo") || s.startsWith("ch") || s.includes("moon") || s.includes("சந்") || s.includes("திங்கள்") || s.includes("chandra")) return "Moon";

  // Mars
  if (s.startsWith("sev") || s.startsWith("chev") || (s.startsWith("ma") && !s.includes("mandi")) || s.includes("mars") || s.includes("செவ்") || s.includes("mangal") || s.includes("kuja") || s.includes("angarak")) return "Mars";

  // Mercury
  if (s.startsWith("me") || s.startsWith("bu") || s.includes("merc") || s.includes("புத") || s.includes("budh")) return "Mercury";

  // Jupiter
  if (s.startsWith("ju") || s.startsWith("gu") || s.startsWith("br") || s.includes("jup") || s.includes("குரு") || s.includes("வியாழன்") || s.includes("guru") || s.includes("brihaspati")) return "Jupiter";

  // Rahu
  if (s.startsWith("ra") || s.includes("rah") || s.includes("ராகு")) return "Rahu";

  // Ketu
  if (s.startsWith("ke") || s.includes("ket") || s.includes("கேது")) return "Ketu";

  return null;
}

export type DignityStatus =
  | "ucham"
  | "neecham"
  | "dikbala"
  | "ucham_dikbala"
  | "neecham_dikbala"
  | "none";

export interface GrahaDignityResult {
  status: DignityStatus;
  isUcham: boolean;
  isNeecham: boolean;
  isDikBala: boolean;
  isDeepUcham: boolean;
  isDeepNeecham: boolean;
  house?: number;
  colorClass: string;
  colorHex: string;
  badgeBgClass: string;
  badgeBorderClass: string;
  labelEn: string;
  labelTa: string;
  tooltipEn: string;
  tooltipTa: string;
}

/**
 * Evaluates whether a planet is Ucham, Neecham, or has Dik Balam (Directional Strength)
 *
 * @param planetName Planet name (e.g., "Sun", "சூரியன்", "Suriyan", etc.)
 * @param signIndex Zodiac sign index (1 = Aries ... 12 = Pisces)
 * @param ascendantSignIndex Ascendant / Lagna sign index (1 to 12)
 * @param degreeInSign Optional degree within sign (0.0 to 30.0)
 * @param explicitHouse Optional explicit house number (1 to 12)
 */
export function getGrahaDignity(
  planetName: string,
  signIndex: number,
  ascendantSignIndex?: number,
  degreeInSign?: number,
  explicitHouse?: number
): GrahaDignityResult {
  const defaultResult: GrahaDignityResult = {
    status: "none",
    isUcham: false,
    isNeecham: false,
    isDikBala: false,
    isDeepUcham: false,
    isDeepNeecham: false,
    colorClass: "text-[#183047]",
    colorHex: "#183047",
    badgeBgClass: "bg-slate-50",
    badgeBorderClass: "border-slate-200 text-slate-700",
    labelEn: "Neutral",
    labelTa: "சமநிலை",
    tooltipEn: planetName,
    tooltipTa: planetName,
  };

  const key = normalizePlanetKey(planetName);
  if (!key || !NAVAGRAHA_RULES[key]) {
    return defaultResult;
  }

  const rule = NAVAGRAHA_RULES[key];

  // Calculate House from Lagna
  let house: number | undefined = explicitHouse;
  if (!house && ascendantSignIndex && ascendantSignIndex >= 1 && ascendantSignIndex <= 12) {
    house = ((signIndex - ascendantSignIndex + 12) % 12) + 1;
  }

  const isUcham = signIndex === rule.uchamSign;
  const isNeecham = signIndex === rule.neechamSign;
  const isDikBala = Boolean(rule.dikBalaHouse && house === rule.dikBalaHouse);

  const isDeepUcham =
    isUcham &&
    typeof degreeInSign === "number" &&
    Math.abs(degreeInSign - rule.uchamDeepDeg) <= 1.5;

  const isDeepNeecham =
    isNeecham &&
    typeof degreeInSign === "number" &&
    Math.abs(degreeInSign - rule.neechamDeepDeg) <= 1.5;

  // Determine Dignity Status and Styling
  // User instructions:
  // - Ucham -> Green (#16A34A)
  // - Neecham -> RED (#DC2626)
  // - Dik Balam -> Yellow (#CA8A04)
  if (isUcham && isDikBala) {
    return {
      status: "ucham_dikbala",
      isUcham: true,
      isNeecham: false,
      isDikBala: true,
      isDeepUcham,
      isDeepNeecham: false,
      house,
      colorClass: "text-[#16A34A]",
      colorHex: "#16A34A",
      badgeBgClass: "bg-emerald-50",
      badgeBorderClass: "border-emerald-300 text-emerald-800",
      labelEn: `Ucham & Dik Balam`,
      labelTa: `உச்சம் & திக் பலம்`,
      tooltipEn: `${rule.canonicalName} is Exalted (Ucham) & has Directional Strength (Dik Balam in ${rule.directionEn})${isDeepUcham ? ` [Deepest at ${rule.uchamDeepDeg}°]` : ""}`,
      tooltipTa: `${rule.nameTa} உச்சம் பெற்று மற்றும் திக் பலமும் (${rule.directionTa}) கொண்டுள்ளது${isDeepUcham ? ` [பரமோச்ச பாகை ${rule.uchamDeepDeg}°]` : ""}`,
    };
  }

  if (isNeecham && isDikBala) {
    return {
      status: "neecham_dikbala",
      isUcham: false,
      isNeecham: true,
      isDikBala: true,
      isDeepUcham: false,
      isDeepNeecham,
      house,
      colorClass: "text-[#DC2626]",
      colorHex: "#DC2626",
      badgeBgClass: "bg-rose-50",
      badgeBorderClass: "border-rose-300 text-rose-800",
      labelEn: `Neecham & Dik Balam`,
      labelTa: `நீசம் & திக் பலம்`,
      tooltipEn: `${rule.canonicalName} is Debilitated (Neecham) but holds Directional Strength (Dik Balam in ${rule.directionEn})${isDeepNeecham ? ` [Deepest at ${rule.neechamDeepDeg}°]` : ""}`,
      tooltipTa: `${rule.nameTa} நீசம் பெற்றிருந்தாலும் திக் பலமும் (${rule.directionTa}) கொண்டுள்ளது${isDeepNeecham ? ` [பரமநீச பாகை ${rule.neechamDeepDeg}°]` : ""}`,
    };
  }

  if (isUcham) {
    return {
      status: "ucham",
      isUcham: true,
      isNeecham: false,
      isDikBala: false,
      isDeepUcham,
      isDeepNeecham: false,
      house,
      colorClass: "text-[#16A34A]",
      colorHex: "#16A34A",
      badgeBgClass: "bg-emerald-50",
      badgeBorderClass: "border-emerald-300 text-emerald-700",
      labelEn: `Ucham (Exalted)`,
      labelTa: `உச்சம் (Ucham)`,
      tooltipEn: `${rule.canonicalName} is Exalted (Ucham)${isDeepUcham ? ` [Deep Paramochha at ${rule.uchamDeepDeg}°]` : ""}`,
      tooltipTa: `${rule.nameTa} உச்சம் (Ucham)${isDeepUcham ? ` [பரமோச்ச பாகை ${rule.uchamDeepDeg}°]` : ""}`,
    };
  }

  if (isNeecham) {
    return {
      status: "neecham",
      isUcham: false,
      isNeecham: true,
      isDikBala: false,
      isDeepUcham: false,
      isDeepNeecham,
      house,
      colorClass: "text-[#DC2626]",
      colorHex: "#DC2626",
      badgeBgClass: "bg-rose-50",
      badgeBorderClass: "border-rose-300 text-rose-700",
      labelEn: `Neecham (Debilitated)`,
      labelTa: `நீசம் (Neecham)`,
      tooltipEn: `${rule.canonicalName} is Debilitated (Neecham)${isDeepNeecham ? ` [Deep Paramaneecha at ${rule.neechamDeepDeg}°]` : ""}`,
      tooltipTa: `${rule.nameTa} நீசம் (Neecham)${isDeepNeecham ? ` [பரமநீச பாகை ${rule.neechamDeepDeg}°]` : ""}`,
    };
  }

  if (isDikBala) {
    return {
      status: "dikbala",
      isUcham: false,
      isNeecham: false,
      isDikBala: true,
      isDeepUcham: false,
      isDeepNeecham: false,
      house,
      colorClass: "text-[#CA8A04]",
      colorHex: "#CA8A04",
      badgeBgClass: "bg-amber-50",
      badgeBorderClass: "border-amber-300 text-amber-700",
      labelEn: `Dik Balam (${rule.directionEn})`,
      labelTa: `திக் பலம் (${rule.directionTa})`,
      tooltipEn: `${rule.canonicalName} holds Directional Strength (Dik Balam) in the ${rule.directionEn}`,
      tooltipTa: `${rule.nameTa} திக் பலம் (${rule.directionTa}) கொண்டுள்ளது`,
    };
  }

  return defaultResult;
}
