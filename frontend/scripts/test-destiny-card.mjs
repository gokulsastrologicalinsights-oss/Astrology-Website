/**
 * Gokul's Astrological Insights - Destiny Card Test Suite
 *
 * Validates:
 * 1. Correct field mapping from authoritative XALEN horoscope and Dasa results.
 * 2. Graceful missing-data handling (rejects incomplete or fabricated charts).
 * 3. Accurate bilingual rendering (Tamil and English) for Rasis, Nakshatras, and Dasa lords.
 * 4. Privacy compliance (verifies omission of exact geographic coordinates and API secrets).
 * 5. Deterministic Canvas 2D rendering calls without NaN or runtime exceptions.
 * 6. Fallback from active Mahadasha to birth Mahadasha when target date is omitted.
 */

import assert from "node:assert";
import {
  extractDestinyCardData,
  renderDestinyCardToCanvas,
  formatCompactDeg,
} from "../src/lib/destiny-card-utils.ts";
import {
  getRasiName,
  getNakshatraName,
  getLordName,
  translations,
} from "../src/lib/translations.ts";

console.log("=== Gokul's Astrological Insights - Destiny Card Test Suite ===\n");

let passed = 0;
let failed = 0;

function runTest(name, fn) {
  try {
    process.stdout.write(`Testing ${name} ... `);
    fn();
    console.log("[PASS]");
    passed++;
  } catch (err) {
    console.log(`[FAIL] ${err.message}`);
    failed++;
  }
}

// --------------------------------------------------------------------------
// Sample Authoritative Calculation Fixture
// --------------------------------------------------------------------------
const mockCompleteResult = {
  horoscope: {
    metadata: {
      engine: "XALEN Ephemeris Engine (Rust Core)",
      ayanamsa_name: "Lahiri (Chitra Paksha)",
      ayanamsa_id: 1,
      julian_day_ut1: 2447907.1041,
      birth_utc_iso: "1990-01-15T14:30:00Z",
    },
    ascendant: {
      degree: 44.52,
      sign_index: 2,
      sign_name: "Vrishabha",
      sign_name_tamil: "ரிஷபம்",
      degree_in_sign: 14.52,
      nakshatra: {
        name: "Rohini",
        index: 4,
        pada: 2,
        lord: "Moon",
        deity: "Brahma",
      },
    },
    midheaven: {
      degree: 310.2,
      sign_index: 11,
      sign_name: "Kumbha",
      sign_name_tamil: "கும்பம்",
      degree_in_sign: 10.2,
      nakshatra: { name: "Shatabhisha", index: 24, pada: 2, lord: "Rahu", deity: "Varuna" },
    },
    planets: [
      {
        name: "Sun",
        body_id: 0,
        longitude: 271.15,
        sign_index: 10,
        sign_name: "Makara",
        sign_name_tamil: "மகரம்",
        degree_in_sign: 1.15,
        nakshatra: { name: "Uttara Ashadha", index: 21, pada: 2, lord: "Sun", deity: "Vishwadevas" },
      },
      {
        name: "Moon",
        body_id: 1,
        longitude: 142.8,
        sign_index: 5,
        sign_name: "Simha",
        sign_name_tamil: "சிம்மம்",
        degree_in_sign: 22.8,
        nakshatra: { name: "Purva Phalguni", index: 11, pada: 3, lord: "Venus", deity: "Bhaga" },
      },
      {
        name: "Mars",
        body_id: 4,
        longitude: 245.0,
        sign_index: 9,
        sign_name: "Dhanus",
        sign_name_tamil: "தனுசு",
        degree_in_sign: 5.0,
        nakshatra: { name: "Moola", index: 19, pada: 2, lord: "Ketu", deity: "Nirriti" },
      },
    ],
    houses: [],
  },
  dasa: {
    metadata: {
      engine: "XALEN Ephemeris Engine",
      ayanamsa_name: "Lahiri",
    },
    moon_sidereal_deg: 142.8,
    nakshatra: { name: "Purva Phalguni", index: 11, pada: 3, lord: "Venus", deity: "Bhaga" },
    birth_dasa_lord: "Venus",
    birth_balance_years: 9.42,
    birth_balance_formatted: "9y 5m 2d",
    active_period: {
      mahadasha: "Jupiter",
      antardasha: "Saturn",
      pratyantardasha: "Mercury",
      target_jd: 2461332.5,
      target_date_iso: "2026-10-18T00:00:00Z",
      target_age: "36y 9m 3d",
    },
    dasa_tree: [],
  },
  clientInputs: {
    fullName: "Arun Kumar",
    birthDate: "1990-01-15",
    birthTime: "14:30:00",
    isTimeConfirmed: true,
    locationName: "Chennai, Tamil Nadu, India",
    latitude: 13.0827,
    longitude: 80.2707,
    timezone: "Asia/Kolkata",
    ayanamsaId: 1,
    houseSystemId: 1,
  },
  calculatedAt: "2026-10-18T09:00:00Z",
};

// --------------------------------------------------------------------------
// 1. Correct Field Mapping & Extraction Test
// --------------------------------------------------------------------------
runTest("Correct field mapping from verified XALEN horoscope result", () => {
  const data = extractDestinyCardData(mockCompleteResult, false);
  assert.ok(data !== null, "Result must not be null");
  assert.strictEqual(data.isVerified, true, "Card must be marked verified");
  assert.strictEqual(data.personName, "Arun Kumar");

  // Ascendant
  assert.strictEqual(data.ascendantSignEn, "Vrishabha");
  assert.strictEqual(data.ascendantSignTa, "ரிஷபம்");
  assert.strictEqual(data.ascendantDegree, 14.52);
  assert.strictEqual(data.ascendantNakshatraEn, "Rohini");
  assert.strictEqual(data.ascendantNakshatraTa, "ரோகிணி");
  assert.strictEqual(data.ascendantPada, 2);

  // Moon Sign & Nakshatra
  assert.strictEqual(data.moonSignEn, "Simha");
  assert.strictEqual(data.moonSignTa, "சிம்மம்");
  assert.strictEqual(data.moonDegree, 22.8);
  assert.strictEqual(data.nakshatraEn, "Purva Phalguni");
  assert.strictEqual(data.nakshatraTa, "பூரம்");
  assert.strictEqual(data.pada, 3);
  assert.strictEqual(data.starLordEn, "Venus");
  assert.strictEqual(data.starLordTa, "சுக்கிரன் (வெள்ளி)");

  // Active Mahadasha
  assert.strictEqual(data.isCurrentDasa, true);
  assert.strictEqual(data.dasaLordEn, "Jupiter");
  assert.strictEqual(data.dasaLordTa, "குரு (வியாழன்)");
  assert.strictEqual(data.antardashaLordEn, "Saturn");
  assert.strictEqual(data.antardashaLordTa, "சனி");

  // Optional Sun Sign
  assert.strictEqual(data.sunSignEn, "Makara");
  assert.strictEqual(data.sunSignTa, "மகரம்");
  assert.strictEqual(data.sunDegree, 1.15);

  // Metadata
  assert.strictEqual(data.ayanamsaName, "Lahiri (Chitra Paksha)");
  assert.strictEqual(data.calculationEngine, "XALEN Ephemeris Engine (Rust Core)");
});

// --------------------------------------------------------------------------
// 2. Missing Data & Validation Safety
// --------------------------------------------------------------------------
runTest("Rejects null or missing calculation results", () => {
  assert.strictEqual(extractDestinyCardData(null), null);
  assert.strictEqual(extractDestinyCardData(undefined), null);
  assert.strictEqual(extractDestinyCardData({}), null);
});

runTest("Rejects charts missing Ascendant", () => {
  const invalid = JSON.parse(JSON.stringify(mockCompleteResult));
  invalid.horoscope.ascendant = null;
  assert.strictEqual(extractDestinyCardData(invalid), null);

  invalid.horoscope.ascendant = { sign_name: "", sign_index: 0 };
  assert.strictEqual(extractDestinyCardData(invalid), null);
});

runTest("Rejects charts missing Moon placement or Nakshatra", () => {
  const invalidNoMoon = JSON.parse(JSON.stringify(mockCompleteResult));
  invalidNoMoon.horoscope.planets = invalidNoMoon.horoscope.planets.filter((p) => p.name !== "Moon");
  assert.strictEqual(extractDestinyCardData(invalidNoMoon), null);

  const invalidNoNak = JSON.parse(JSON.stringify(mockCompleteResult));
  const moonP = invalidNoNak.horoscope.planets.find((p) => p.name === "Moon");
  moonP.nakshatra = null;
  invalidNoNak.dasa = null;
  assert.strictEqual(extractDestinyCardData(invalidNoNak), null);
});

runTest("Rejects charts missing both active and birth Dasa", () => {
  const invalidNoDasa = JSON.parse(JSON.stringify(mockCompleteResult));
  invalidNoDasa.dasa = null;
  assert.strictEqual(extractDestinyCardData(invalidNoDasa), null);
});

runTest("Gracefully falls back to birth Dasa when active_period is omitted", () => {
  const fallbackChart = JSON.parse(JSON.stringify(mockCompleteResult));
  delete fallbackChart.dasa.active_period;
  fallbackChart.dasa.birth_dasa_lord = "Ketu";

  const data = extractDestinyCardData(fallbackChart);
  assert.ok(data !== null);
  assert.strictEqual(data.isCurrentDasa, false);
  assert.strictEqual(data.dasaLordEn, "Ketu");
  assert.strictEqual(data.dasaLordTa, "கேது");
});

// --------------------------------------------------------------------------
// 3. Bilingual Tamil & English Translations
// --------------------------------------------------------------------------
runTest("Bilingual Rasi translations match canonical 12 zodiac signs", () => {
  const rasiPairs = [
    [1, "Aries", "மேஷம்"],
    [2, "Taurus", "ரிஷபம்"],
    [3, "Gemini", "மிதுனம்"],
    [4, "Cancer", "கடகம்"],
    [5, "Leo", "சிம்மம்"],
    [6, "Virgo", "கன்னி"],
    [7, "Libra", "துலாம்"],
    [8, "Scorpio", "விருச்சிகம்"],
    [9, "Sagittarius", "தனுசு"],
    [10, "Capricorn", "மகரம்"],
    [11, "Aquarius", "கும்பம்"],
    [12, "Pisces", "மீனம்"],
  ];

  for (const [idx, en, ta] of rasiPairs) {
    assert.strictEqual(getRasiName(idx, "en"), en);
    assert.strictEqual(getRasiName(idx, "ta"), ta);
  }
});

runTest("Bilingual Nakshatra translations verify correctly", () => {
  assert.strictEqual(getNakshatraName("Ashwini", "ta"), "அஸ்வினி");
  assert.strictEqual(getNakshatraName("Rohini", "ta"), "ரோகிணி");
  assert.strictEqual(getNakshatraName("Purva Phalguni", "ta"), "பூரம்");
  assert.strictEqual(getNakshatraName("Chitra", "ta"), "சித்திரை");
  assert.strictEqual(getNakshatraName("Revati", "ta"), "ரேவதி");
});

runTest("Bilingual Graha / Lord names verify correctly", () => {
  assert.strictEqual(getLordName("Sun", "ta"), "சூரியன்");
  assert.strictEqual(getLordName("Moon", "ta"), "சந்திரன்");
  assert.strictEqual(getLordName("Mars", "ta"), "செவ்வாய்");
  assert.strictEqual(getLordName("Mercury", "ta"), "புதன்");
  assert.strictEqual(getLordName("Jupiter", "ta"), "குரு (வியாழன்)");
  assert.strictEqual(getLordName("Venus", "ta"), "சுக்கிரன் (வெள்ளி)");
  assert.strictEqual(getLordName("Saturn", "ta"), "சனி");
  assert.strictEqual(getLordName("Rahu", "ta"), "ராகு");
  assert.strictEqual(getLordName("Ketu", "ta"), "கேது");
});

// --------------------------------------------------------------------------
// 4. Privacy & Data Protection Compliance
// --------------------------------------------------------------------------
runTest("Sensitive birth coordinates and credentials excluded from card data", () => {
  // Without birth date
  const dataPrivate = extractDestinyCardData(mockCompleteResult, false);
  assert.strictEqual(dataPrivate.birthDateDisplay, undefined, "Birth date must be undefined by default");

  // With birth date
  const dataWithDate = extractDestinyCardData(mockCompleteResult, true);
  assert.strictEqual(dataWithDate.birthDateDisplay, "1990-01-15");

  // Geographic coordinates, time of birth, and tokens must NEVER be present on DestinyCardData
  const keys = Object.keys(dataWithDate);
  assert.ok(!keys.includes("latitude"), "Latitude must not be exposed");
  assert.ok(!keys.includes("longitude"), "Longitude must not be exposed");
  assert.ok(!keys.includes("birthTime"), "Exact birth minute must not be on card");
  assert.ok(!keys.includes("supabase"), "Supabase credentials must never be present");
});

// --------------------------------------------------------------------------
// 5. Degree Formatter & Mathematical Helpers
// --------------------------------------------------------------------------
runTest("Degree formatting generates clean compact strings", () => {
  assert.strictEqual(formatCompactDeg(14.52), "14° 31'");
  assert.strictEqual(formatCompactDeg(0.0), "0° 00'");
  assert.strictEqual(formatCompactDeg(29.999), "29° 59'");
});

// --------------------------------------------------------------------------
// 6. Mock Canvas 2D Execution Safety
// --------------------------------------------------------------------------
runTest("Canvas 2D rendering executes without error for English and Tamil", () => {
  const operations = [];

  const mockCtx = {
    createLinearGradient: () => ({ addColorStop: () => {} }),
    createRadialGradient: () => ({ addColorStop: () => {} }),
    fillRect: (...args) => operations.push(["fillRect", ...args]),
    strokeRect: (...args) => operations.push(["strokeRect", ...args]),
    fillText: (...args) => operations.push(["fillText", ...args]),
    beginPath: () => operations.push(["beginPath"]),
    closePath: () => operations.push(["closePath"]),
    moveTo: (...args) => operations.push(["moveTo", ...args]),
    lineTo: (...args) => operations.push(["lineTo", ...args]),
    quadraticCurveTo: (...args) => operations.push(["quadraticCurveTo", ...args]),
    arc: (...args) => operations.push(["arc", ...args]),
    stroke: () => operations.push(["stroke"]),
    fill: () => operations.push(["fill"]),
    save: () => operations.push(["save"]),
    restore: () => operations.push(["restore"]),
    translate: (...args) => operations.push(["translate", ...args]),
    rotate: (...args) => operations.push(["rotate", ...args]),
  };

  const mockCanvas = {
    width: 0,
    height: 0,
    getContext: (type) => (type === "2d" ? mockCtx : null),
  };

  const data = extractDestinyCardData(mockCompleteResult, true);

  // Render in English
  operations.length = 0;
  renderDestinyCardToCanvas(mockCanvas, data, "en");
  assert.strictEqual(mockCanvas.width, 1200);
  assert.strictEqual(mockCanvas.height, 1500);
  assert.ok(operations.length > 50, "English canvas operations must be recorded");

  // Render in Tamil
  operations.length = 0;
  renderDestinyCardToCanvas(mockCanvas, data, "ta");
  assert.strictEqual(mockCanvas.width, 1200);
  assert.strictEqual(mockCanvas.height, 1500);
  assert.ok(operations.length > 50, "Tamil canvas operations must be recorded");
});

// --------------------------------------------------------------------------
// Summary
// --------------------------------------------------------------------------
console.log(`\nResults: ${passed} passed, ${failed} failed out of ${passed + failed} tests.`);
if (failed > 0) {
  process.exit(1);
}
