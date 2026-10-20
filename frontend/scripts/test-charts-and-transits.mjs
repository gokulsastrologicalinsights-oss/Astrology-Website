import fs from "fs";
import path from "path";
import assert from "assert";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const resolveFile = (rel) => {
  const candidates = [
    path.resolve(rel),
    path.resolve("frontend", rel),
    path.resolve(__dirname, "..", rel),
  ];
  for (const c of candidates) {
    if (fs.existsSync(c)) return c;
  }
  return candidates[0];
};

console.log("=== Testing Simplified Horoscope Charts & Live Transits Overlay ===");

// 1. Verify Zodiac Sign Icons Removal from SouthIndianChart.tsx
const southIndianPath = resolveFile("src/components/charts/SouthIndianChart.tsx");
const southIndianSrc = fs.readFileSync(southIndianPath, "utf-8");

assert(
  !southIndianSrc.includes("rasi?.symbol"),
  "FAIL: rasi?.symbol should be removed from SouthIndianChart.tsx"
);
assert(
  !southIndianSrc.includes("RASIS[cell.signIndex]"),
  "FAIL: RASIS corner lookup should be removed from SouthIndianChart.tsx"
);
assert(
  southIndianSrc.includes("transitPlanets"),
  "FAIL: transitPlanets prop should exist on SouthIndianChart.tsx"
);
assert(
  southIndianSrc.includes("showTransits"),
  "FAIL: showTransits prop should exist on SouthIndianChart.tsx"
);
console.log("✓ SouthIndianChart: Zodiac symbols removed and transit props added");

// 2. Verify NorthIndianChart.tsx supports live transits
const northIndianPath = resolveFile("src/components/charts/NorthIndianChart.tsx");
const northIndianSrc = fs.readFileSync(northIndianPath, "utf-8");

assert(
  northIndianSrc.includes("transitPlanets"),
  "FAIL: transitPlanets prop should exist on NorthIndianChart.tsx"
);
assert(
  northIndianSrc.includes("showTransits"),
  "FAIL: showTransits prop should exist on NorthIndianChart.tsx"
);
assert(
  northIndianSrc.includes("NORTH_TRANSIT_ANCHORS"),
  "FAIL: NORTH_TRANSIT_ANCHORS should exist on NorthIndianChart.tsx"
);
console.log("✓ NorthIndianChart: Live transit perimeter anchors and props verified");

// 3. Verify Results Page Layout: Only Rasi (D1) and Navamsa (D9), Bhava Chakra removed
const resultsPagePath = resolveFile("src/app/horoscope/results/page.tsx");
const resultsPageSrc = fs.readFileSync(resultsPagePath, "utf-8");

assert(
  !resultsPageSrc.includes("buildBhavaHoroscope(result.horoscope)"),
  "FAIL: buildBhavaHoroscope memoization should be removed from results page"
);
assert(
  !resultsPageSrc.includes("Chart 3: Bhava Chakra"),
  "FAIL: Bhava Chakra chart card must be removed from results page"
);
assert(
  !resultsPageSrc.includes("Bhava Chakra (House Cusps)"),
  "FAIL: Bhava Chakra title must not appear in charts tab on results page"
);
assert(
  resultsPageSrc.includes("grid-cols-1 lg:grid-cols-2"),
  "FAIL: 2-column responsive grid should be used for remaining charts"
);
assert(
  resultsPageSrc.includes("Show Live Transits"),
  "FAIL: Show Live Transits toggle must be present"
);
assert(
  resultsPageSrc.includes("getLiveTransits"),
  "FAIL: getLiveTransits API call should be present"
);
console.log("✓ Results Page: Bhava Chakra removed, 2-column layout active, live transits controls added");

// 4. Verify Backend Engine & API types
const typesPath = resolveFile("src/lib/types.ts");
const typesSrc = fs.readFileSync(typesPath, "utf-8");
assert(
  typesSrc.includes("export interface LiveTransitsResponse"),
  "FAIL: LiveTransitsResponse interface missing in types.ts"
);

const apiPath = resolveFile("src/lib/api.ts");
const apiSrc = fs.readFileSync(apiPath, "utf-8");
assert(
  apiSrc.includes("export async function getLiveTransits"),
  "FAIL: getLiveTransits missing in api.ts"
);
console.log("✓ API & Types: LiveTransitsResponse and getLiveTransits verified");

// 5. Verify buildBhavaHoroscope engine remains intact in chart-transforms.ts
const transformsPath = resolveFile("src/lib/chart-transforms.ts");
const transformsSrc = fs.readFileSync(transformsPath, "utf-8");
assert(
  transformsSrc.includes("export function buildBhavaHoroscope"),
  "FAIL: Underlying buildBhavaHoroscope in chart-transforms.ts must NOT be deleted"
);
console.log("✓ Underlying Engine: buildBhavaHoroscope calculation engine preserved in chart-transforms.ts");

console.log("\nALL VERIFICATION CHECKS PASSED SUCCESSFULLY!");
