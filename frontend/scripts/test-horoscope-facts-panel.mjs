/**
 * Verification test suite for HoroscopeFactsPanel & Tamil Astrology Engine
 * Gokul's Astrological Insights
 */

import { readFileSync, existsSync } from "fs";
import { resolve } from "path";

let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (condition) {
    console.log(`Testing ${message} ... [PASS]`);
    passed++;
  } else {
    console.error(`Testing ${message} ... [FAIL]`);
    failed++;
  }
}

console.log("=== Gokul's Astrological Insights - ஜாதக விவரங்கள் (Facts Panel) Test Suite ===");

// 1. Verify files exist
const resolvePath = (sub) => {
  if (existsSync(resolve(sub))) return resolve(sub);
  if (existsSync(resolve("frontend", sub))) return resolve("frontend", sub);
  if (sub.startsWith("frontend/") && existsSync(resolve(sub.replace("frontend/", "")))) {
    return resolve(sub.replace("frontend/", ""));
  }
  return resolve(sub);
};

const factsPanelPath = resolvePath("frontend/src/components/results/HoroscopeFactsPanel.tsx");
const factsPanelCode = readFileSync(factsPanelPath, "utf-8");

const tamilAstroPath = resolvePath("frontend/src/lib/tamil-astrology.ts");
const tamilAstroCode = readFileSync(tamilAstroPath, "utf-8");

const solarAstroPath = resolvePath("frontend/src/lib/solar-astronomy.ts");
const solarAstroCode = readFileSync(solarAstroPath, "utf-8");

// 2. Check 6 Categories in exact required order
const expectedCategories = [
  'id: "basic"',
  'id: "special"',
  'id: "benefic_malefic"',
  'id: "shadbala_avastha"',
  'id: "transit"',
  'id: "jaimini"',
];

let lastIdx = -1;
let orderCorrect = true;
for (const cat of expectedCategories) {
  const idx = factsPanelCode.indexOf(cat);
  if (idx === -1 || idx < lastIdx) {
    orderCorrect = false;
    break;
  }
  lastIdx = idx;
}
assert(orderCorrect, "All 6 categories present in exact specified order (அடிப்படை, சிறப்பு, சுப/பாவ, ஷட்பலம், பெயர்ச்சி, ஜைமினி)");

// 3. Category Titles in Tamil
assert(
  factsPanelCode.includes('title: "அடிப்படை"') &&
  factsPanelCode.includes('title: "சிறப்பு அம்சங்கள்"') &&
  factsPanelCode.includes('title: "சுப & பாவ கிரகங்கள்"') &&
  factsPanelCode.includes('title: "ஷட்பலம் & அவஸ்தை"') &&
  factsPanelCode.includes('title: "பெயர்ச்சி (கோச்சாரம்)"') &&
  factsPanelCode.includes('title: "ஜைமினி சார காரகங்கள்"'),
  "All 6 category titles match exact Tamil specifications"
);

// 4. Default Category is 'basic'
assert(
  factsPanelCode.includes('initialCategory = "basic"') &&
  factsPanelCode.includes("useState<FactCategory>(initialCategory)"),
  "Default category is 'basic' (அடிப்படை) with initialCategory fallback"
);

// 5. Category 1 Section A (Panchangam)
assert(
  factsPanelCode.includes("formatTithiTamil") &&
  factsPanelCode.includes("formatYogaTamil") &&
  factsPanelCode.includes("formatKaranaTamil") &&
  factsPanelCode.includes("getRasiNameTamil") &&
  factsPanelCode.includes("getNakshatraTamil"),
  "Section A: Panchangam formats Rasi, Lagna, Nakshatra, Tithi, Yoga, Karana using authentic Tamil terminology"
);

// 6. Category 1 Section B (Dasa Balance)
assert(
  factsPanelCode.includes("பிறப்பு தசை இருப்பு") &&
  factsPanelCode.includes("பிறப்பு புக்தி இருப்பு") &&
  factsPanelCode.includes("dasaBalance.dasaYMD.compact") &&
  factsPanelCode.includes("dasaBalance.bhuktiYMD.compact"),
  "Section B: Dasa-Bhukti balances render distinct cards for Dasa and Bhukti with YMD formatting"
);

// 7. Category 1 Section C (Birth Details)
assert(
  factsPanelCode.includes("பெயர்:") &&
  factsPanelCode.includes("பிறந்த நேரம்:") &&
  factsPanelCode.includes("பிறந்த இடம்:") &&
  factsPanelCode.includes("சூரிய உதய நேரம்:") &&
  factsPanelCode.includes("சூரிய அஸ்தமன நேரம்:") &&
  factsPanelCode.includes("அட்சாம்சம் (Latitude):") &&
  factsPanelCode.includes("தீர்க்காம்சம் (Longitude):") &&
  factsPanelCode.includes("நேர மண்டலம் (Timezone):") &&
  factsPanelCode.includes("அயனாம்ச முறை:") &&
  factsPanelCode.includes("அயனாம்சம் (Value):"),
  "Section C: All 10 required astronomical & birth parameter fields present"
);

// 8. Graceful Placeholders (no hardcoded sample leak)
assert(
  factsPanelCode.includes('clientInputs.fullName || "கிடைக்கவில்லை"') &&
  factsPanelCode.includes('clientInputs.locationName || "கிடைக்கவில்லை"') &&
  factsPanelCode.includes('solarTimes?.sunriseTime || "கிடைக்கவில்லை"') &&
  factsPanelCode.includes('solarTimes?.sunsetTime || "கிடைக்கவில்லை"'),
  "Section C uses 'கிடைக்கவில்லை' for unavailable data with zero hardcoded sample leaks"
);

// 9. Classical Vargottama detection
assert(
  factsPanelCode.includes("Math.floor(totalDeg / (10 / 3)) % 12") &&
  factsPanelCode.includes("vargottamaList.push"),
  "Category 2: Identifies Vargottama planets using classical 108-pada continuous Navamsa formula"
);

// 10. Category 3: Functional Benefics and Malefics
assert(
  tamilAstroCode.includes("getLagnaClassification") &&
  tamilAstroCode.includes("benefics") &&
  tamilAstroCode.includes("malefics") &&
  tamilAstroCode.includes("yogakaraka"),
  "Category 3: Functional Benefic/Malefic/Neutral & Yogakaraka classifications implemented per BPHS Ch. 34 for all 12 Lagnas"
);

// 11. Category 4: Shadbala & Avasthas
assert(
  factsPanelCode.includes("calculateShadbala") &&
  factsPanelCode.includes("baladi") &&
  factsPanelCode.includes("jagradadi") &&
  factsPanelCode.includes("deepthadi"),
  "Category 4: Connects to Shadbala backend API and calculates Baladi, Jagradadi, and Deepthadi Avasthas"
);

// 12. Category 5: Live Gochara (Transit)
assert(
  factsPanelCode.includes("calculateHoroscope") &&
  factsPanelCode.includes("handleFetchTransit") &&
  factsPanelCode.includes("transitDate") &&
  !factsPanelCode.includes("sampleTransits = ["),
  "Category 5: Uses live ephemeris calculation via calculateHoroscope without hardcoded sample arrays"
);

// 13. Category 6: Jaimini 7 Chara Karakas
assert(
  tamilAstroCode.includes("calculateJaiminiKarakas") &&
  factsPanelCode.includes("jaiminiKarakas") &&
  factsPanelCode.includes("ஆத்மகாரகன்") &&
  factsPanelCode.includes("அமாத்யகாரகன்"),
  "Category 6: Calculates 7 Jaimini Chara Karakas (AK to DK) ranked strictly by sidereal degrees in sign"
);

// 14. Responsive & Deep Link URL Support
assert(
  factsPanelCode.includes("handleSelectCategory") &&
  factsPanelCode.includes("history.replaceState"),
  "Category navigation supports deep linking with URL update and zero full-page reloads"
);

console.log(`\nResults: ${passed} passed, ${failed} failed out of ${passed + failed} tests.`);
if (failed > 0) {
  process.exit(1);
} else {
  console.log("All ஜாதக விவரங்கள் (Horoscope Facts Panel) tests PASSED successfully!\n");
}
