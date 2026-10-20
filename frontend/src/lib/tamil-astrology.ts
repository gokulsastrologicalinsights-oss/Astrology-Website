/**
 * Gokul's Astrological Insights - Tamil Astrology Vocabulary & Calculation Utilities
 * 
 * Provides comprehensive Tamil translations, planetary characterizations,
 * functional classifications, Jaimini Chara Karakas, Avasthas, and Gochara rules.
 */

import { formatDms } from "./formatters";

// ---------------------------------------------------------------------------
// 1. 12 Zodiac Signs (Rasis)
// ---------------------------------------------------------------------------
export const RASI_MAP: Record<string, { ta: string; lord: string; lordTa: string; element: string }> = {
  Aries: { ta: "மேஷம்", lord: "Mars", lordTa: "செவ்வாய்", element: "நெருப்பு" },
  Taurus: { ta: "ரிஷபம்", lord: "Venus", lordTa: "சுக்கிரன்", element: "நிலம்" },
  Gemini: { ta: "மிதுனம்", lord: "Mercury", lordTa: "புதன்", element: "காற்று" },
  Cancer: { ta: "கடகம்", lord: "Moon", lordTa: "சந்திரன்", element: "நீர்" },
  Leo: { ta: "சிம்மம்", lord: "Sun", lordTa: "சூரியன்", element: "நெருப்பு" },
  Virgo: { ta: "கன்னி", lord: "Mercury", lordTa: "புதன்", element: "நிலம்" },
  Libra: { ta: "துலாம்", lord: "Venus", lordTa: "சுக்கிரன்", element: "காற்று" },
  Scorpio: { ta: "விருச்சிகம்", lord: "Mars", lordTa: "செவ்வாய்", element: "நீர்" },
  Sagittarius: { ta: "தனுசு", lord: "Jupiter", lordTa: "குரு", element: "நெருப்பு" },
  Capricorn: { ta: "மகரம்", lord: "Saturn", lordTa: "சனி", element: "நிலம்" },
  Aquarius: { ta: "கும்பம்", lord: "Saturn", lordTa: "சனி", element: "காற்று" },
  Pisces: { ta: "மீனம்", lord: "Jupiter", lordTa: "குரு", element: "நீர்" },
};

export const RASI_NAMES_TA = [
  "மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி",
  "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்",
];

export function getRasiNameTamil(name?: string | null, index?: number | null): string {
  if (name && RASI_MAP[name]) return RASI_MAP[name].ta;
  if (index && index >= 1 && index <= 12) return RASI_NAMES_TA[index - 1];
  return name || "கிடைக்கவில்லை";
}

// ---------------------------------------------------------------------------
// 2. 9 Planets (Grahas) & Abbreviations
// ---------------------------------------------------------------------------
export const PLANET_TA_MAP: Record<
  string,
  { name: string; abbr: string; fullTitle: string; naturalNature: "subha" | "papa" | "krura" | "neutral" }
> = {
  Sun: { name: "சூரியன்", abbr: "சூரி", fullTitle: "சூரிய பகவான்", naturalNature: "krura" },
  Moon: { name: "சந்திரன்", abbr: "சந்", fullTitle: "சந்திர பகவான்", naturalNature: "subha" },
  Mars: { name: "செவ்வாய்", abbr: "செவ்", fullTitle: "செவ்வாய் பகவான்", naturalNature: "papa" },
  Mercury: { name: "புதன்", abbr: "புத", fullTitle: "புத பகவான்", naturalNature: "neutral" },
  Jupiter: { name: "குரு", abbr: "குரு", fullTitle: "குரு பகவான் (வியாழன்)", naturalNature: "subha" },
  Venus: { name: "சுக்கிரன்", abbr: "சுக்", fullTitle: "சுக்கிர பகவான்", naturalNature: "subha" },
  Saturn: { name: "சனி", abbr: "சனி", fullTitle: "சனி பகவான்", naturalNature: "papa" },
  Rahu: { name: "ராகு", abbr: "ராகு", fullTitle: "ராகு பகவான்", naturalNature: "papa" },
  Ketu: { name: "கேது", abbr: "கேது", fullTitle: "கேது பகவான்", naturalNature: "papa" },
};

export function getPlanetNameTamil(name?: string | null): string {
  if (!name) return "கிடைக்கவில்லை";
  return PLANET_TA_MAP[name]?.name || name;
}

export function getPlanetAbbrTamil(name?: string | null): string {
  if (!name) return "—";
  return PLANET_TA_MAP[name]?.abbr || name.slice(0, 3);
}

// ---------------------------------------------------------------------------
// 3. 27 Nakshatras in Tamil
// ---------------------------------------------------------------------------
export const NAKSHATRA_TA_MAP: Record<string, string> = {
  Ashwini: "அசுவினி",
  Bharani: "பரணி",
  Krittika: "கார்த்திகை",
  Rohini: "ரோகிணி",
  Mrigashira: "மிருகசீரிஷம்",
  Mrigasira: "மிருகசீரிஷம்",
  Ardra: "திருவாதிரை",
  Punarvasu: "புனர்பூசம்",
  Pushya: "பூசம்",
  Ashlesha: "ஆயில்யம்",
  Aslesha: "ஆயில்யம்",
  Magha: "மகம்",
  "Purva Phalguni": "பூரம்",
  "Poorva Phalguni": "பூரம்",
  "Uttara Phalguni": "உத்திரம்",
  Hasta: "அஸ்தம்",
  Chitra: "சித்திரை",
  Swati: "சுவாதி",
  Vishakha: "விசாகம்",
  Anuradha: "அனுஷம்",
  Jyeshtha: "கேட்டை",
  Moola: "மூலம்",
  Mula: "மூலம்",
  "Purva Ashadha": "பூராடம்",
  "Poorva Ashadha": "பூராடம்",
  "Uttara Ashadha": "உத்திராடம்",
  Shravana: "திருவோணம்",
  Dhanishta: "அவிட்டம்",
  Shatabhisha: "சதயம்",
  Satabhisha: "சதயம்",
  "Purva Bhadrapada": "பூரட்டாதி",
  "Poorva Bhadrapada": "பூரட்டாதி",
  "Uttara Bhadrapada": "உத்திரட்டாதி",
  Revati: "ரேவதி",
};

export function getNakshatraTamil(name?: string | null): string {
  if (!name) return "கிடைக்கவில்லை";
  return NAKSHATRA_TA_MAP[name] || name;
}

// ---------------------------------------------------------------------------
// 4. Panchang Tithi, Yoga, Karana Mappings
// ---------------------------------------------------------------------------
export const TITHI_TA_NAMES: Record<string, string> = {
  Pratipada: "பிரதமை",
  Prathama: "பிரதமை",
  Dvitiya: "துவிதியை",
  Tritiya: "திருதியை",
  Chaturthi: "சதுர்த்தி",
  Panchami: "பஞ்சமி",
  Shashti: "சஷ்டி",
  Sashti: "சஷ்டி",
  Saptami: "சப்தமி",
  Ashtami: "அஷ்டமி",
  Navami: "நவமி",
  Dashami: "தசமி",
  Ekadashi: "ஏகாதசி",
  Dvadashi: "துவாதசி",
  Trayodashi: "திரயோதசி",
  Chaturdashi: "சதுர்தசி",
  Purnima: "பௌர்ணமி",
  Poornima: "பௌர்ணமி",
  Amavasya: "அமாவாசை",
};

export function formatTithiTamil(tithiObj?: { paksha?: string; name?: string; number?: number } | null): string {
  if (!tithiObj) return "கிடைக்கவில்லை";
  const pakshaTa =
    tithiObj.paksha?.toLowerCase() === "krishna"
      ? "கிருஷ்ண"
      : tithiObj.paksha?.toLowerCase() === "shukla"
      ? "சுக்ல"
      : tithiObj.paksha || "";

  const nameTa = TITHI_TA_NAMES[tithiObj.name || ""] || tithiObj.name || "";

  if (nameTa === "பௌர்ணமி" || nameTa === "அமாவாசை") {
    return nameTa;
  }
  if (pakshaTa && nameTa) {
    return `${pakshaTa} - ${nameTa}`;
  }
  return nameTa || pakshaTa || "கிடைக்கவில்லை";
}

export const YOGA_TA_NAMES: Record<string, string> = {
  Vishkambha: "விஷ்கம்பம்",
  Priti: "ப்ரீதி",
  Ayushman: "ஆயுஷ்மான்",
  Saubhagya: "சௌபாக்யம்",
  Shobhana: "சோபனம்",
  Atiganda: "அதிகண்டம்",
  Sukarma: "சுகர்மம்",
  Dhriti: "த்ருதி",
  Shula: "சூலம்",
  Ganda: "கண்டம்",
  Vriddhi: "வ்ருத்தி",
  Dhruva: "துருவம்",
  Vyaghata: "வ்யாகாதம்",
  Harshana: "ஹர்ஷணம்",
  Vajra: "வஜ்ரம்",
  Siddhi: "சித்தி",
  Vyatipata: "வ்யதிபாதம்",
  Variyan: "வரியான்",
  Parigha: "பரிகம்",
  Shiva: "சிவம்",
  Siddha: "சித்தம்",
  Sadhya: "சாத்தியம்",
  Shubha: "சுபம்",
  Shukla: "சுப்ரம்",
  Brahma: "பிராமியம்",
  Indra: "ஐந்திரம்",
  Vaidhriti: "வைதிருதி",
};

export function formatYogaTamil(name?: string | null): string {
  if (!name) return "கிடைக்கவில்லை";
  return YOGA_TA_NAMES[name] || name;
}

export const KARANA_TA_NAMES: Record<string, string> = {
  Bava: "பவம்",
  Balava: "பாலவம்",
  Kaulava: "கௌலவம்",
  Taitila: "தைதுலை",
  Garija: "கரசை",
  Vanija: "வனசை",
  Vishti: "பத்திரை (விஷ்டி)",
  Shakuni: "சகுனி",
  Chatushpada: "சதுஷ்பாதம்",
  Naga: "நாகவம்",
  Kimstughna: "கிமிஸ்துக்னம்",
};

export function formatKaranaTamil(name?: string | null): string {
  if (!name) return "கிடைக்கவில்லை";
  return KARANA_TA_NAMES[name] || name;
}

// ---------------------------------------------------------------------------
// 5. Geographic & Ayanamsa Coordinate Formatters
// ---------------------------------------------------------------------------
export function formatLatitudeDms(lat?: number | null): string {
  if (lat === null || lat === undefined || isNaN(lat)) return "கிடைக்கவில்லை";
  const dir = lat >= 0 ? "N" : "S";
  const abs = Math.abs(lat);
  const d = Math.floor(abs);
  const mFloat = (abs - d) * 60;
  const m = Math.floor(mFloat);
  const s = Math.round((mFloat - m) * 60);
  return `${d}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}${dir}`;
}

export function formatLongitudeDms(lon?: number | null): string {
  if (lon === null || lon === undefined || isNaN(lon)) return "கிடைக்கவில்லை";
  const dir = lon >= 0 ? "E" : "W";
  const abs = Math.abs(lon);
  const d = Math.floor(abs);
  const mFloat = (abs - d) * 60;
  const m = Math.floor(mFloat);
  const s = Math.round((mFloat - m) * 60);
  return `${d}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}${dir}`;
}

export function formatAyanamsaDms(deg?: number | null): string {
  if (deg === null || deg === undefined || isNaN(deg)) return "கிடைக்கவில்லை";
  const norm = Math.abs(deg % 360);
  const d = Math.floor(norm);
  const mFloat = (norm - d) * 60;
  const m = Math.floor(mFloat);
  const s = Math.round((mFloat - m) * 60);
  return `${d}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

// ---------------------------------------------------------------------------
// 6. Dasa-Bhukti Balance Formatter (Years, Months, Days)
// ---------------------------------------------------------------------------
export function formatBalanceYMD(yearsFloat?: number | null): {
  compact: string; // "3Y 8M 0D"
  tamil: string;   // "3 வருடங்கள் 8 மாதங்கள் 0 நாட்கள்"
  years: number;
  months: number;
  days: number;
} {
  if (yearsFloat === null || yearsFloat === undefined || isNaN(yearsFloat) || yearsFloat <= 0) {
    return { compact: "0Y 0M 0D", tamil: "0 நாட்கள்", years: 0, months: 0, days: 0 };
  }

  const totalDays = yearsFloat * 365.25;
  let years = Math.floor(totalDays / 365.25);
  const remDays = totalDays - years * 365.25;
  let months = Math.floor(remDays / 30.4375);
  let days = Math.round(remDays - months * 30.4375);

  if (days >= 30) {
    months += 1;
    days = 0;
  }
  if (months >= 12) {
    years += 1;
    months = 0;
  }

  return {
    compact: `${years}Y ${months}M ${days}D`,
    tamil: `${years} வருடம் ${months} மாதம் ${days} நாள்`,
    years,
    months,
    days,
  };
}

// ---------------------------------------------------------------------------
// 7. Functional Benefics & Malefics for each Lagna (BPHS Ch. 34)
// ---------------------------------------------------------------------------
export interface LagnaClassification {
  lagnaNameEn: string;
  lagnaNameTa: string;
  lagnaLord: string;
  lagnaLordTa: string;
  yogakaraka: string | null;
  yogakarakaTa: string | null;
  benefics: string[];
  beneficsTa: string[];
  malefics: string[];
  maleficsTa: string[];
  neutrals: string[];
  neutralsTa: string[];
  specialNoteTa: string;
}

export const LAGNA_CLASSIFICATIONS: Record<string, LagnaClassification> = {
  aries: {
    lagnaNameEn: "Aries",
    lagnaNameTa: "மேஷம்",
    lagnaLord: "Mars",
    lagnaLordTa: "செவ்வாய்",
    yogakaraka: null,
    yogakarakaTa: null,
    benefics: ["Jupiter", "Sun", "Mars"],
    beneficsTa: ["குரு", "சூரியன்", "செவ்வாய்"],
    malefics: ["Mercury", "Saturn", "Venus"],
    maleficsTa: ["புதன்", "சனி", "சுக்கிரன்"],
    neutrals: ["Moon"],
    neutralsTa: ["சந்திரன்"],
    specialNoteTa: "செவ்வாய் லக்னாதிபதியாகவும் 8-ஆம் அதிபதியாகவும் இருந்தாலும் லக்ன சுபரே.",
  },
  taurus: {
    lagnaNameEn: "Taurus",
    lagnaNameTa: "ரிஷபம்",
    lagnaLord: "Venus",
    lagnaLordTa: "சுக்கிரன்",
    yogakaraka: "Saturn",
    yogakarakaTa: "சனி (9, 10-ஆம் அதிபதி)",
    benefics: ["Saturn", "Mercury", "Sun"],
    beneficsTa: ["சனி", "புதன்", "சூரியன்"],
    malefics: ["Jupiter", "Mars", "Venus"],
    maleficsTa: ["குரு", "செவ்வாய்", "சுக்கிரன்"],
    neutrals: ["Moon"],
    neutralsTa: ["சந்திரன்"],
    specialNoteTa: "சனி பகவான் 9 (திரிகோணம்) மற்றும் 10 (கேந்திரம்) அதிபதியாகி பரிபூரண யோககாரகன் ஆவார்.",
  },
  gemini: {
    lagnaNameEn: "Gemini",
    lagnaNameTa: "மிதுனம்",
    lagnaLord: "Mercury",
    lagnaLordTa: "புதன்",
    yogakaraka: null,
    yogakarakaTa: null,
    benefics: ["Venus", "Mercury"],
    beneficsTa: ["சுக்கிரன்", "புதன்"],
    malefics: ["Mars", "Jupiter", "Sun"],
    maleficsTa: ["செவ்வாய்", "குரு", "சூரியன்"],
    neutrals: ["Moon", "Saturn"],
    neutralsTa: ["சந்திரன்", "சனி"],
    specialNoteTa: "சுக்கிரன் 5-ஆம் அதிபதியாகி மிகச்சிறந்த சுப பலன்களை வழங்குவார்.",
  },
  cancer: {
    lagnaNameEn: "Cancer",
    lagnaNameTa: "கடகம்",
    lagnaLord: "Moon",
    lagnaLordTa: "சந்திரன்",
    yogakaraka: "Mars",
    yogakarakaTa: "செவ்வாய் (5, 10-ஆம் அதிபதி)",
    benefics: ["Mars", "Moon", "Jupiter"],
    beneficsTa: ["செவ்வாய்", "சந்திரன்", "குரு"],
    malefics: ["Mercury", "Venus", "Saturn"],
    maleficsTa: ["புதன்", "சுக்கிரன்", "சனி"],
    neutrals: ["Sun"],
    neutralsTa: ["சூரியன்"],
    specialNoteTa: "செவ்வாய் 5 (திரிகோணம்) மற்றும் 10 (கேந்திரம்) அதிபதியாகி முதன்மை யோககாரகன் ஆவார்.",
  },
  leo: {
    lagnaNameEn: "Leo",
    lagnaNameTa: "சிம்மம்",
    lagnaLord: "Sun",
    lagnaLordTa: "சூரியன்",
    yogakaraka: "Mars",
    yogakarakaTa: "செவ்வாய் (4, 9-ஆம் அதிபதி)",
    benefics: ["Mars", "Sun", "Jupiter"],
    beneficsTa: ["செவ்வாய்", "சூரியன்", "குரு"],
    malefics: ["Saturn", "Venus", "Mercury"],
    maleficsTa: ["சனி", "சுக்கிரன்", "புதன்"],
    neutrals: ["Moon"],
    neutralsTa: ["சந்திரன்"],
    specialNoteTa: "செவ்வாய் 4 (கேந்திரம்) மற்றும் 9 (பாக்கியம்) அதிபதியாகி ராஜயோக பலன் தருகிறார்.",
  },
  virgo: {
    lagnaNameEn: "Virgo",
    lagnaNameTa: "கன்னி",
    lagnaLord: "Mercury",
    lagnaLordTa: "புதன்",
    yogakaraka: null,
    yogakarakaTa: null,
    benefics: ["Venus", "Mercury"],
    beneficsTa: ["சுக்கிரன்", "புதன்"],
    malefics: ["Mars", "Jupiter", "Moon"],
    maleficsTa: ["செவ்வாய்", "குரு", "சந்திரன்"],
    neutrals: ["Sun", "Saturn"],
    neutralsTa: ["சூரியன்", "சனி"],
    specialNoteTa: "சுக்கிரன் 2 மற்றும் 9-ஆம் அதிபதியாகி சிறந்த சுப பலன்களை அருளுவார்.",
  },
  libra: {
    lagnaNameEn: "Libra",
    lagnaNameTa: "துலாம்",
    lagnaLord: "Venus",
    lagnaLordTa: "சுக்கிரன்",
    yogakaraka: "Saturn",
    yogakarakaTa: "சனி (4, 5-ஆம் அதிபதி)",
    benefics: ["Saturn", "Mercury", "Venus"],
    beneficsTa: ["சனி", "புதன்", "சுக்கிரன்"],
    malefics: ["Jupiter", "Sun", "Mars"],
    maleficsTa: ["குரு", "சூரியன்", "செவ்வாய்"],
    neutrals: ["Moon"],
    neutralsTa: ["சந்திரன்"],
    specialNoteTa: "சனி 4 (சுகஸ்தானம்) மற்றும் 5 (பூர்வபுண்ணியம்) அதிபதியாகி மேன்மையான யோககாரகன்.",
  },
  scorpio: {
    lagnaNameEn: "Scorpio",
    lagnaNameTa: "விருச்சிகம்",
    lagnaLord: "Mars",
    lagnaLordTa: "செவ்வாய்",
    yogakaraka: null,
    yogakarakaTa: null,
    benefics: ["Jupiter", "Moon", "Sun", "Mars"],
    beneficsTa: ["குரு", "சந்திரன்", "சூரியன்", "செவ்வாய்"],
    malefics: ["Mercury", "Venus"],
    maleficsTa: ["புதன்", "சுக்கிரன்"],
    neutrals: ["Saturn"],
    neutralsTa: ["சனி"],
    specialNoteTa: "குரு மற்றும் சந்திரன் 5 மற்றும் 9-ஆம் அதிபதிகளாகி தர்மகர்மாதிபதி யோகத்தை தருவர்.",
  },
  sagittarius: {
    lagnaNameEn: "Sagittarius",
    lagnaNameTa: "தனுசு",
    lagnaLord: "Jupiter",
    lagnaLordTa: "குரு",
    yogakaraka: null,
    yogakarakaTa: null,
    benefics: ["Sun", "Mars", "Jupiter"],
    beneficsTa: ["சூரியன்", "செவ்வாய்", "குரு"],
    malefics: ["Venus", "Saturn"],
    maleficsTa: ["சுக்கிரன்", "சனி"],
    neutrals: ["Moon", "Mercury"],
    neutralsTa: ["சந்திரன்", "புதன்"],
    specialNoteTa: "சூரியன் (9-ஆம் பாக்கியாதிபதி) மற்றும் செவ்வாய் (5-ஆம் பூர்வபுண்ணியாதிபதி) சிறந்த சுபர்கள்.",
  },
  capricorn: {
    lagnaNameEn: "Capricorn",
    lagnaNameTa: "மகரம்",
    lagnaLord: "Saturn",
    lagnaLordTa: "சனி",
    yogakaraka: "Venus",
    yogakarakaTa: "சுக்கிரன் (5, 10-ஆம் அதிபதி)",
    benefics: ["Venus", "Mercury", "Saturn"],
    beneficsTa: ["சுக்கிரன்", "புதன்", "சனி"],
    malefics: ["Mars", "Jupiter", "Moon"],
    maleficsTa: ["செவ்வாய்", "குரு", "சந்திரன்"],
    neutrals: ["Sun"],
    neutralsTa: ["சூரியன்"],
    specialNoteTa: "சுக்கிரன் 5 மற்றும் 10-ஆம் அதிபதியாகி மகர லக்னத்தின் முழுமையான யோககாரகன் ஆவார்.",
  },
  aquarius: {
    lagnaNameEn: "Aquarius",
    lagnaNameTa: "கும்பம்",
    lagnaLord: "Saturn",
    lagnaLordTa: "சனி",
    yogakaraka: "Venus",
    yogakarakaTa: "சுக்கிரன் (4, 9-ஆம் அதிபதி)",
    benefics: ["Venus", "Saturn"],
    beneficsTa: ["சுக்கிரன்", "சனி"],
    malefics: ["Jupiter", "Moon", "Mars"],
    maleficsTa: ["குரு", "சந்திரன்", "செவ்வாய்"],
    neutrals: ["Sun", "Mercury"],
    neutralsTa: ["சூரியன்", "புதன்"],
    specialNoteTa: "சுக்கிரன் 4 மற்றும் 9-ஆம் அதிபதியாகி சுக-பாக்கிய ராஜயோகத்தை வழங்குகிறார்.",
  },
  pisces: {
    lagnaNameEn: "Pisces",
    lagnaNameTa: "மீனம்",
    lagnaLord: "Jupiter",
    lagnaLordTa: "குரு",
    yogakaraka: null,
    yogakarakaTa: null,
    benefics: ["Moon", "Mars", "Jupiter"],
    beneficsTa: ["சந்திரன்", "செவ்வாய்", "குரு"],
    malefics: ["Venus", "Sun", "Saturn"],
    maleficsTa: ["சுக்கிரன்", "சூரியன்", "சனி"],
    neutrals: ["Mercury"],
    neutralsTa: ["புதன்"],
    specialNoteTa: "சந்திரன் (5-ஆம் அதிபதி) மற்றும் செவ்வாய் (9-ஆம் அதிபதி) பெரும் சுப பலன் தருவர்.",
  },
};

export function getLagnaClassification(lagnaSignName?: string | null): LagnaClassification {
  if (!lagnaSignName) return LAGNA_CLASSIFICATIONS.aries;
  const key = lagnaSignName.trim().toLowerCase();
  return LAGNA_CLASSIFICATIONS[key] || LAGNA_CLASSIFICATIONS.aries;
}

// ---------------------------------------------------------------------------
// 8. Jaimini 7 Chara Karakas (சப்த சார காரகங்கள்)
// ---------------------------------------------------------------------------
export interface JaiminiKarakaResult {
  code: "AK" | "AmK" | "BK" | "MK" | "PK" | "GK" | "DK";
  titleTa: string;
  titleEn: string;
  grahaName: string;
  grahaNameTa: string;
  degreeInSign: number;
  degreeFormatted: string;
  signName: string;
  signNameTa: string;
  nakshatraName: string;
  pada: number;
  significanceTa: string;
  significanceEn: string;
}

const KARAKA_DEFINITIONS: Array<{
  code: "AK" | "AmK" | "BK" | "MK" | "PK" | "GK" | "DK";
  titleTa: string;
  titleEn: string;
  significanceTa: string;
  significanceEn: string;
}> = [
  {
    code: "AK",
    titleTa: "ஆத்மகாரகன்",
    titleEn: "Atmakaraka",
    significanceTa: "ஆன்மா, சுயம், வாழ்க்கை நோக்கம் மற்றும் தலைமைப் பண்புகள்.",
    significanceEn: "Soul, self, ego, true spiritual purpose and core identity.",
  },
  {
    code: "AmK",
    titleTa: "அமாத்யகாரகன்",
    titleEn: "Amatyakaraka",
    significanceTa: "தொழில், பதவி, அதிகாரம், அறிவுக்கூர்மை மற்றும் நிதி ஆலோசனை.",
    significanceEn: "Career, vocation, intellect, status, advisors and worldly success.",
  },
  {
    code: "BK",
    titleTa: "பிராத்ருகாரகன்",
    titleEn: "Bhratrikaraka",
    significanceTa: "உடன்பிறப்புகள், தைரியம், வழிகாட்டிகள், குருமார்கள் மற்றும் ஆற்றல்.",
    significanceEn: "Brothers, siblings, courage, father/gurus and guiding teachers.",
  },
  {
    code: "MK",
    titleTa: "மாத்ருகாரகன்",
    titleEn: "Matrikaraka",
    significanceTa: "தாய், சுகம், கல்வி, அசையா சொத்துக்கள், வாகனங்கள் மற்றும் மன அமைதி.",
    significanceEn: "Mother, nurturing, domestic comfort, fixed assets and education.",
  },
  {
    code: "PK",
    titleTa: "புத்ரகாரகன்",
    titleEn: "Putrakaraka",
    significanceTa: "குழந்தைகள், படைப்பாற்றல், ஆழ்ந்த புத்தி மற்றும் பூர்வ புண்ணியம்.",
    significanceEn: "Children, creative genius, intellect and past-life merits.",
  },
  {
    code: "GK",
    titleTa: "ஞானதிகாரகன்",
    titleEn: "Gnatikaraka",
    significanceTa: "போட்டி, எதிரிகள், நோய், வழக்குகள் மற்றும் வெற்றிகொள்ள வேண்டிய தடைகள்.",
    significanceEn: "Kinsmen, rivals, adversaries, obstacles, health challenges and resilience.",
  },
  {
    code: "DK",
    titleTa: "தாராகாரகன்",
    titleEn: "Darakaraka",
    significanceTa: "வாழ்க்கைத் துணை, களத்திரம், திருமண பந்தம் மற்றும் பொது மக்கள் தொடர்பு.",
    significanceEn: "Spouse, partner, marriage, intimate relationships and business dealings.",
  },
];

export function calculateJaiminiKarakas(
  planets: Array<{
    name: string;
    degree_in_sign: number;
    sign_name: string;
    sign_name_tamil?: string;
    nakshatra?: { name: string; pada: number };
  }>
): JaiminiKarakaResult[] {
  // Only 7 physical planets per classical Jaimini 7-Karaka system
  const sevenGrahas = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"];
  const eligible = planets.filter((p) => sevenGrahas.includes(p.name));

  // Sort descending by degree_in_sign (highest degree first)
  const sorted = [...eligible].sort((a, b) => b.degree_in_sign - a.degree_in_sign);

  return KARAKA_DEFINITIONS.map((def, idx) => {
    const planet = sorted[idx];
    if (!planet) {
      return {
        code: def.code,
        titleTa: def.titleTa,
        titleEn: def.titleEn,
        grahaName: "Unknown",
        grahaNameTa: "கிடைக்கவில்லை",
        degreeInSign: 0,
        degreeFormatted: "—",
        signName: "—",
        signNameTa: "—",
        nakshatraName: "—",
        pada: 1,
        significanceTa: def.significanceTa,
        significanceEn: def.significanceEn,
      };
    }

    return {
      code: def.code,
      titleTa: def.titleTa,
      titleEn: def.titleEn,
      grahaName: planet.name,
      grahaNameTa: getPlanetNameTamil(planet.name),
      degreeInSign: planet.degree_in_sign,
      degreeFormatted: formatDms(planet.degree_in_sign),
      signName: planet.sign_name,
      signNameTa: planet.sign_name_tamil || getRasiNameTamil(planet.sign_name),
      nakshatraName: getNakshatraTamil(planet.nakshatra?.name),
      pada: planet.nakshatra?.pada || 1,
      significanceTa: def.significanceTa,
      significanceEn: def.significanceEn,
    };
  });
}

// ---------------------------------------------------------------------------
// 9. Planetary Avasthas (Baladi, Jagradadi, Deepthadi per BPHS Ch. 45)
// ---------------------------------------------------------------------------
export interface PlanetAvastha {
  planet: string;
  planetTa: string;
  baladi: {
    stateTa: string;
    stateEn: string;
    fruitPercent: string;
    meaningTa: string;
  };
  jagradadi: {
    stateTa: string;
    stateEn: string;
    meaningTa: string;
  };
  deepthadi: {
    stateTa: string;
    stateEn: string;
    meaningTa: string;
  };
}

const EXALTATION_SIGNS: Record<string, string> = {
  Sun: "Aries",
  Moon: "Taurus",
  Mars: "Capricorn",
  Mercury: "Virgo",
  Jupiter: "Cancer",
  Venus: "Pisces",
  Saturn: "Libra",
};

const DEBILITATION_SIGNS: Record<string, string> = {
  Sun: "Libra",
  Moon: "Scorpio",
  Mars: "Cancer",
  Mercury: "Pisces",
  Jupiter: "Capricorn",
  Venus: "Virgo",
  Saturn: "Aries",
};

const OWN_SIGNS_MAP: Record<string, string[]> = {
  Sun: ["Leo"],
  Moon: ["Cancer"],
  Mars: ["Aries", "Scorpio"],
  Mercury: ["Gemini", "Virgo"],
  Jupiter: ["Sagittarius", "Pisces"],
  Venus: ["Taurus", "Libra"],
  Saturn: ["Capricorn", "Aquarius"],
};

export function calculatePlanetAvastha(
  planetName: string,
  signName: string,
  signIndex: number, // 1-12
  degInSign: number // 0-30
): PlanetAvastha {
  const isOddSign = signIndex % 2 !== 0; // 1, 3, 5, 7, 9, 11
  const deg = Math.max(0, Math.min(30, degInSign));

  // 1. Baladi Avastha (5 states of 6 deg each)
  let baladiState: { stateTa: string; stateEn: string; fruitPercent: string; meaningTa: string };
  const tier = Math.floor(deg / 6.0); // 0, 1, 2, 3, 4

  const oddAvasthas = [
    { stateTa: "பால அவஸ்தை", stateEn: "Bala (Infant)", fruitPercent: "25%", meaningTa: "ஆரம்ப நிலை பலன் (கால் பங்கு பலன்)" },
    { stateTa: "குமார அவஸ்தை", stateEn: "Kumara (Youth)", fruitPercent: "50%", meaningTa: "வளர்ச்சி நிலை பலன் (அரை பங்கு பலன்)" },
    { stateTa: "யுவ அவஸ்தை", stateEn: "Yuva (Adult)", fruitPercent: "100%", meaningTa: "பரிபூரண வீரியம் மற்றும் முழுமையான பலன்" },
    { stateTa: "விருத்த அவஸ்தை", stateEn: "Vriddha (Old)", fruitPercent: "15%", meaningTa: "முதிர்ந்த நிலை (சொற்ப பலன்)" },
    { stateTa: "மிருத அவஸ்தை", stateEn: "Mrita (Dead)", fruitPercent: "0%", meaningTa: "செயலற்ற பலன் (பயனற்ற நிலை)" },
  ];

  const evenAvasthas = [
    { stateTa: "மிருத அவஸ்தை", stateEn: "Mrita (Dead)", fruitPercent: "0%", meaningTa: "செயலற்ற பலன் (பயனற்ற நிலை)" },
    { stateTa: "விருத்த அவஸ்தை", stateEn: "Vriddha (Old)", fruitPercent: "15%", meaningTa: "முதிர்ந்த நிலை (சொற்ப பலன்)" },
    { stateTa: "யுவ அவஸ்தை", stateEn: "Yuva (Adult)", fruitPercent: "100%", meaningTa: "பரிபூரண வீரியம் மற்றும் முழுமையான பலன்" },
    { stateTa: "குமார அவஸ்தை", stateEn: "Kumara (Youth)", fruitPercent: "50%", meaningTa: "வளர்ச்சி நிலை பலன் (அரை பங்கு பலன்)" },
    { stateTa: "பால அவஸ்தை", stateEn: "Bala (Infant)", fruitPercent: "25%", meaningTa: "ஆரம்ப நிலை பலன் (கால் பங்கு பலன்)" },
  ];

  const safeTier = Math.min(4, Math.max(0, tier));
  baladiState = isOddSign ? oddAvasthas[safeTier] : evenAvasthas[safeTier];

  // 2. Jagradadi Avastha (Awakened, Dreaming, Sleeping)
  const isExalted = EXALTATION_SIGNS[planetName] === signName;
  const isDebilitated = DEBILITATION_SIGNS[planetName] === signName;
  const isOwnSign = (OWN_SIGNS_MAP[planetName] || []).includes(signName);

  let jagradadiState: { stateTa: string; stateEn: string; meaningTa: string };
  if (isExalted || isOwnSign) {
    jagradadiState = { stateTa: "ஜாக்கிரதம் (விழித்த நிலை)", stateEn: "Jagrata (Awake)", meaningTa: "முழு விழிப்புணர்வுடன் ஆக்கப்பூர்வ பலன்" };
  } else if (isDebilitated) {
    jagradadiState = { stateTa: "சுஷுப்தி (உறங்கும் நிலை)", stateEn: "Sushupti (Sleeping)", meaningTa: "செயலற்ற, பலனளிக்க முடியாத உறக்க நிலை" };
  } else {
    jagradadiState = { stateTa: "ஸ்வப்னம் (கனவு நிலை)", stateEn: "Svapna (Dreaming)", meaningTa: "மத்திம மற்றும் மாற்றங்களுக்குரிய பலன்" };
  }

  // 3. Deepthadi Avastha (Disposition)
  let deepthadiState: { stateTa: string; stateEn: string; meaningTa: string };
  if (isExalted) {
    deepthadiState = { stateTa: "தீப்தம் (உச்ச நிலை)", stateEn: "Deeptha (Exalted)", meaningTa: "ஒளி பொருந்திய பேரானந்த நிலை (முழு சுப யோகம்)" };
  } else if (isOwnSign) {
    deepthadiState = { stateTa: "ஸ்வஸ்தம் (ஆட்சி நிலை)", stateEn: "Swastha (Own Sign)", meaningTa: "தன் சொந்த வீட்டில் அமைதியான பலம்" };
  } else if (isDebilitated) {
    deepthadiState = { stateTa: "கலம் / தீனம் (நீச நிலை)", stateEn: "Khala / Deena (Debilitated)", meaningTa: "ஆற்றல் குன்றிய பலவீன நிலை" };
  } else {
    deepthadiState = { stateTa: "சாந்தம் / முதிதம் (நட்பு நிலை)", stateEn: "Shanta (Friendly)", meaningTa: "மகிழ்ச்சியான சாந்த நிலை" };
  }

  return {
    planet: planetName,
    planetTa: getPlanetNameTamil(planetName),
    baladi: baladiState,
    jagradadi: jagradadiState,
    deepthadi: deepthadiState,
  };
}

// ---------------------------------------------------------------------------
// 10. Gochara (Transit) Evaluator relative to Natal Moon (Janma Rasi)
// ---------------------------------------------------------------------------
export interface GocharaTransitInfo {
  planet: string;
  planetTa: string;
  transitSign: string;
  transitSignTa: string;
  houseFromMoon: number;
  houseFromLagna: number;
  nature: "auspicious" | "inauspicious" | "neutral";
  natureTa: string;
  summaryTa: string;
}

// Auspicious transit houses from Moon per Phaladeepika Ch. 26
const AUSPICIOUS_TRANSIT_HOUSES: Record<string, number[]> = {
  Sun: [3, 6, 10, 11],
  Moon: [1, 3, 6, 7, 10, 11],
  Mars: [3, 6, 11],
  Mercury: [2, 4, 6, 8, 10, 11],
  Jupiter: [2, 5, 7, 9, 11],
  Venus: [1, 2, 3, 4, 5, 8, 9, 11, 12],
  Saturn: [3, 6, 11],
  Rahu: [3, 6, 11],
  Ketu: [3, 9, 11],
};

export function evaluateGocharaHouse(planet: string, houseFromMoon: number): {
  nature: "auspicious" | "inauspicious" | "neutral";
  natureTa: string;
  summaryTa: string;
} {
  const goodHouses = AUSPICIOUS_TRANSIT_HOUSES[planet] || [3, 6, 11];
  const isGood = goodHouses.includes(houseFromMoon);

  if (planet === "Saturn") {
    if (houseFromMoon === 12) return { nature: "inauspicious", natureTa: "விரைய சனி (முதற்கட்டம்)", summaryTa: "ஏழரைச் சனியின் ஆரம்பக் கட்டம், செலவுகள் அதிகரிக்கும்." };
    if (houseFromMoon === 1) return { nature: "inauspicious", natureTa: "ஜென்ம சனி (இரண்டாம்கட்டம்)", summaryTa: "ஏழரைச் சனியின் உச்சக் கட்டம், பொறுமையும் விவேகமும் தேவை." };
    if (houseFromMoon === 2) return { nature: "inauspicious", natureTa: "பாத சனி (மூன்றாம்கட்டம்)", summaryTa: "ஏழரைச் சனியின் இறுதிக் கட்டம், வாக்குவாதம் தவிர்க்கவும்." };
    if (houseFromMoon === 4) return { nature: "inauspicious", natureTa: "அர்த்தாஷ்டம சனி / கண்டக சனி", summaryTa: "சுகஸ்தானத்தில் சனி, உடல்நலனில் கவனம் தேவை." };
    if (houseFromMoon === 8) return { nature: "inauspicious", natureTa: "அஷ்டம சனி", summaryTa: "8-ஆம் இடத்தில் சனி, புதிய முதலீடுகளில் கூடுதல் எச்சரிக்கை அவசியம்." };
    if (isGood) return { nature: "auspicious", natureTa: "அனுகூல சனி (சுப பலன்)", summaryTa: `${houseFromMoon}-ஆம் இடத்தில் சனி சஞ்சரிப்பது வெற்றி, பணவரவு மற்றும் எதிரிகளை வெல்லும் யோகம் தரும்.` };
  }

  if (planet === "Jupiter") {
    if (isGood) {
      return {
        nature: "auspicious",
        natureTa: "சுப குரு பார்வை (நற்பலன்)",
        summaryTa: `குரு பகவான் ராசிக்கு ${houseFromMoon}-ஆம் சுப ஸ்தானத்தில் அமர்ந்து மேன்மையான நன்மைகளை அருளுகிறார்.`,
      };
    } else {
      return {
        nature: "neutral",
        natureTa: "சுமாரான குரு பலன்",
        summaryTa: `குரு பகவான் ராசிக்கு ${houseFromMoon}-ஆம் இடத்தில் சஞ்சரிப்பதால் விவேகமான செயல்பாடுகள் நலம் தரும்.`,
      };
    }
  }

  if (isGood) {
    return {
      nature: "auspicious",
      natureTa: "அனுகூல சஞ்சாரம்",
      summaryTa: `ராசிக்கு ${houseFromMoon}-ஆம் சுப ஸ்தானத்தில் சஞ்சரித்து சுப பலன்களை அளிக்கிறார்.`,
    };
  }

  return {
    nature: "neutral",
    natureTa: "சம நிலை சஞ்சாரம்",
    summaryTa: `ராசிக்கு ${houseFromMoon}-ஆம் இடத்தில் சஞ்சரித்து பொதுவான பலன்களைத் தருகிறார்.`,
  };
}
