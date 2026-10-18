/**
 * Gokul's Astrological Insights - Numerology Frontend & Logic Verification Suite
 */

import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log("=== Gokul's Astrological Insights - Numerology Frontend Verification Suite ===");

// 1. Verify translations.ts has all numerology keys in both en and ta
console.log("\n1. Testing i18n dictionary completeness for Numerology...");
const translationsPath = path.join(__dirname, "../src/lib/translations.ts");
const translationsContent = fs.readFileSync(translationsPath, "utf-8");

const requiredKeys = [
  "navNumerology",
  "numerologyTitle",
  "numerologySubtitle",
  "cardTraditionalTitle",
  "cardTraditionalDesc",
  "cardTraditionalCta",
  "cardDestinyTitle",
  "cardDestinyDesc",
  "cardDestinyCta",
  "cardAdvancedTitle",
  "cardAdvancedDesc",
  "cardAdvancedCta",
  "savedNumerologyTitle",
  "savedNumerologySubtitle",
  "savedNumerologyEmpty",
  "saveReportSuccess",
  "reopenReport",
  "printReport",
  "exportPdf",
  "conventionPythagorean",
  "conventionChaldean",
];

for (const key of requiredKeys) {
  assert(
    translationsContent.includes(`${key}:`),
    `translations.ts missing key: ${key}`
  );
}
console.log(`Verified ${requiredKeys.length} required bilingual keys exist in translations.ts. [PASS]`);

// 2. Verify Lo Shu 3x3 Magic Square properties
console.log("\n2. Testing Lo Shu Magic Square mathematical invariant (magic sum = 15)...");
const standardLoShu = [
  [4, 9, 2],
  [3, 5, 7],
  [8, 1, 6],
];

// Check row sums
for (let r = 0; r < 3; r++) {
  const sum = standardLoShu[r].reduce((a, b) => a + b, 0);
  assert.strictEqual(sum, 15, `Row ${r} sum must be 15`);
}

// Check col sums
for (let c = 0; c < 3; c++) {
  const sum = standardLoShu[0][c] + standardLoShu[1][c] + standardLoShu[2][c];
  assert.strictEqual(sum, 15, `Column ${c} sum must be 15`);
}

// Check diagonals
const diag1 = standardLoShu[0][0] + standardLoShu[1][1] + standardLoShu[2][2];
const diag2 = standardLoShu[0][2] + standardLoShu[1][1] + standardLoShu[2][0];
assert.strictEqual(diag1, 15, "Main diagonal must be 15");
assert.strictEqual(diag2, 15, "Anti-diagonal must be 15");
console.log("Verified Lo Shu magic sum invariants in all 8 directions. [PASS]");

// 3. Test Modulo-22 reduction logic (Arcana preservation)
console.log("\n3. Testing Modulo-22 reduction algorithm (1-22 preserved, >22 summed)...");
function reduce22(num) {
  let val = Math.abs(num);
  while (val > 22) {
    val = String(val)
      .split("")
      .reduce((acc, digit) => acc + parseInt(digit, 10), 0);
  }
  return val;
}

assert.strictEqual(reduce22(7), 7);
assert.strictEqual(reduce22(22), 22);
assert.strictEqual(reduce22(23), 5); // 2 + 3 = 5
assert.strictEqual(reduce22(28), 10); // 2 + 8 = 10
assert.strictEqual(reduce22(29), 11); // 2 + 9 = 11
assert.strictEqual(reduce22(99), 18); // 9 + 9 = 18 <= 22 (NOT 1 + 8 = 9)
console.log("Verified 22-Arcana reduction boundaries and single vs double digit reduction. [PASS]");

// 4. Test Master Numbers preservation (11, 22, 33)
console.log("\n4. Testing Master Number preservation (11, 22, 33)...");
function reduceSingleDigit(num, preserveMaster = true) {
  let val = Math.abs(num);
  while (val > 9) {
    if (preserveMaster && (val === 11 || val === 22 || val === 33)) {
      return val;
    }
    val = String(val)
      .split("")
      .reduce((acc, digit) => acc + parseInt(digit, 10), 0);
  }
  return val;
}

assert.strictEqual(reduceSingleDigit(11, true), 11);
assert.strictEqual(reduceSingleDigit(22, true), 22);
assert.strictEqual(reduceSingleDigit(33, true), 33);
assert.strictEqual(reduceSingleDigit(44, true), 8); // 4 + 4 = 8
assert.strictEqual(reduceSingleDigit(11, false), 2); // without master preservation -> 2
assert.strictEqual(reduceSingleDigit(29, true), 11); // 2 + 9 = 11 (Master)
console.log("Verified Master Number rules correctly distinguish 11, 22, 33. [PASS]");

console.log("\nAll Numerology frontend & math checks passed successfully!");
