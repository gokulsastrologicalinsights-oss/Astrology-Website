import assert from "node:assert/strict";
import {
  getGrahaDignity,
  normalizePlanetKey,
  NAVAGRAHA_RULES,
} from "../src/lib/dignity.ts";

console.log("=== Gokul's Astrological Insights - Navagraha Dignity & Dik Balam Test Suite ===\n");

// 1. Verify Rules Dictionary matches User Specification exactly
console.log("1. Verifying Exaltation (Ucham), Debilitation (Neecham), and Dik Balam Definitions...");
const expectedRules = [
  { name: "Sun", ucham: 1, uchamDeg: 10, neecham: 7, neechamDeg: 10, dikBalaHouse: 10 },
  { name: "Moon", ucham: 2, uchamDeg: 3, neecham: 8, neechamDeg: 3, dikBalaHouse: 4 },
  { name: "Mars", ucham: 10, uchamDeg: 28, neecham: 4, neechamDeg: 28, dikBalaHouse: 10 },
  { name: "Mercury", ucham: 6, uchamDeg: 15, neecham: 12, neechamDeg: 15, dikBalaHouse: 1 },
  { name: "Jupiter", ucham: 4, uchamDeg: 5, neecham: 10, neechamDeg: 5, dikBalaHouse: 1 },
  { name: "Venus", ucham: 12, uchamDeg: 27, neecham: 6, neechamDeg: 27, dikBalaHouse: 4 },
  { name: "Saturn", ucham: 7, uchamDeg: 20, neecham: 1, neechamDeg: 20, dikBalaHouse: 7 },
  { name: "Rahu", ucham: 2, neecham: 8 },
  { name: "Ketu", ucham: 8, neecham: 2 },
];

for (const exp of expectedRules) {
  const rule = NAVAGRAHA_RULES[exp.name];
  assert.ok(rule, `Rule exists for ${exp.name}`);
  assert.equal(rule.uchamSign, exp.ucham, `${exp.name} Ucham sign is ${exp.ucham}`);
  assert.equal(rule.neechamSign, exp.neecham, `${exp.name} Neecham sign is ${exp.neecham}`);
  if (exp.uchamDeg !== undefined) {
    assert.equal(rule.uchamDeepDeg, exp.uchamDeg, `${exp.name} Deep Ucham is ${exp.uchamDeg}°`);
    assert.equal(rule.neechamDeepDeg, exp.neechamDeg, `${exp.name} Deep Neecham is ${exp.neechamDeg}°`);
  }
  if (exp.dikBalaHouse !== undefined) {
    assert.equal(rule.dikBalaHouse, exp.dikBalaHouse, `${exp.name} Dik Bala house is ${exp.dikBalaHouse}`);
  }
}
console.log("  [PASS] All 9 Graha rules match user specification.\n");

// 2. Testing Ucham (Exaltation) color -> GREEN (#16A34A)
console.log("2. Testing Ucham (Exaltation) returns Green (#16A34A)...");
for (const exp of expectedRules) {
  const result = getGrahaDignity(exp.name, exp.ucham, 11); // Lagna 11 so not necessarily dikbala
  assert.equal(result.isUcham, true, `${exp.name} in sign ${exp.ucham} must be Ucham`);
  assert.equal(result.colorHex, "#16A34A", `${exp.name} Ucham must have Green hex #16A34A`);
  assert.equal(result.colorClass, "text-[#16A34A]", `${exp.name} Ucham must have green text class`);
  assert.match(result.labelEn, /Ucham/i);
  assert.match(result.labelTa, /உச்சம்/);
}
console.log("  [PASS] All Ucham placements are colored GREEN.\n");

// 3. Testing Neecham (Debilitation) color -> RED (#DC2626)
console.log("3. Testing Neecham (Debilitation) returns RED (#DC2626)...");
for (const exp of expectedRules) {
  const result = getGrahaDignity(exp.name, exp.neecham, 11);
  assert.equal(result.isNeecham, true, `${exp.name} in sign ${exp.neecham} must be Neecham`);
  assert.equal(result.colorHex, "#DC2626", `${exp.name} Neecham must have Red hex #DC2626`);
  assert.equal(result.colorClass, "text-[#DC2626]", `${exp.name} Neecham must have red text class`);
  assert.match(result.labelEn, /Neecham/i);
  assert.match(result.labelTa, /நீசம்/);
}
console.log("  [PASS] All Neecham placements are colored RED.\n");

// 4. Testing Dik Balam (Directional Strength) -> YELLOW (#CA8A04)
console.log("4. Testing Dik Balam (Directional Strength) returns Yellow (#CA8A04)...");
// Sun in 10th house: Lagna Leo (5), 10th house is Taurus (2). Sun in Taurus (neither ucham nor neecham).
const sunDikBala = getGrahaDignity("Sun", 2, 5); // sign 2 from Lagna 5 is House 10
assert.equal(sunDikBala.isDikBala, true, "Sun in 10th house gets Dik Balam");
assert.equal(sunDikBala.colorHex, "#CA8A04", "Sun Dik Balam has Yellow hex #CA8A04");
assert.equal(sunDikBala.colorClass, "text-[#CA8A04]", "Sun Dik Balam has yellow text class");

// Moon in 4th house: Lagna Aries (1), 4th house is Cancer (4). Moon in Cancer (neither ucham nor neecham).
const moonDikBala = getGrahaDignity("Moon", 4, 1);
assert.equal(moonDikBala.isDikBala, true, "Moon in 4th house gets Dik Balam");
assert.equal(moonDikBala.colorHex, "#CA8A04");

// Mars in 10th house: Lagna Gemini (3), 10th house is Pisces (12). Mars in Pisces.
const marsDikBala = getGrahaDignity("Mars", 12, 3);
assert.equal(marsDikBala.isDikBala, true, "Mars in 10th house gets Dik Balam");
assert.equal(marsDikBala.colorHex, "#CA8A04");

// Mercury in 1st house (Lagna): Lagna Gemini (3), Mercury in Gemini (3).
const mercDikBala = getGrahaDignity("Mercury", 3, 3);
assert.equal(mercDikBala.isDikBala, true, "Mercury in 1st house gets Dik Balam");
assert.equal(mercDikBala.colorHex, "#CA8A04");

// Jupiter in 1st house (Lagna): Lagna Sagittarius (9), Jupiter in Sagittarius (9).
const jupDikBala = getGrahaDignity("Jupiter", 9, 9);
assert.equal(jupDikBala.isDikBala, true, "Jupiter in 1st house gets Dik Balam");
assert.equal(jupDikBala.colorHex, "#CA8A04");

// Venus in 4th house: Lagna Taurus (2), 4th house is Leo (5). Venus in Leo.
const venDikBala = getGrahaDignity("Venus", 5, 2);
assert.equal(venDikBala.isDikBala, true, "Venus in 4th house gets Dik Balam");
assert.equal(venDikBala.colorHex, "#CA8A04");

// Saturn in 7th house: Lagna Gemini (3), 7th house is Sagittarius (9). Saturn in Sagittarius.
const satDikBala = getGrahaDignity("Saturn", 9, 3);
assert.equal(satDikBala.isDikBala, true, "Saturn in 7th house gets Dik Balam");
assert.equal(satDikBala.colorHex, "#CA8A04");
console.log("  [PASS] All 7 Dik Balam placements return YELLOW.\n");

// 5. Testing Dual Condition: Ucham + Dik Balam
console.log("5. Testing Dual Condition: Ucham + Dik Balam...");
// Sun in Aries (1) with Cancer Lagna (4): 10th house is Aries! Both Ucham & Dik Balam!
const sunDual = getGrahaDignity("Sun", 1, 4, 10.0);
assert.equal(sunDual.isUcham, true, "Sun is Ucham");
assert.equal(sunDual.isDikBala, true, "Sun is Dik Balam");
assert.equal(sunDual.status, "ucham_dikbala");
assert.equal(sunDual.colorHex, "#16A34A", "Exaltation takes green color tone");
assert.match(sunDual.tooltipEn, /Exalted.*Directional Strength/);
console.log("  [PASS] Ucham + Dik Balam dual condition evaluated seamlessly.\n");

// 6. Testing Tamil and Transliteration Input Names
console.log("6. Testing Tamil and Transliteration Input Names...");
assert.equal(normalizePlanetKey("சூரியன்"), "Sun");
assert.equal(normalizePlanetKey("Suriyan"), "Sun");
assert.equal(normalizePlanetKey("Chandran"), "Moon");
assert.equal(normalizePlanetKey("சந்திரன்"), "Moon");
assert.equal(normalizePlanetKey("செவ்வாய்"), "Mars");
assert.equal(normalizePlanetKey("Sevvai"), "Mars");
assert.equal(normalizePlanetKey("புதன்"), "Mercury");
assert.equal(normalizePlanetKey("Budhan"), "Mercury");
assert.equal(normalizePlanetKey("குரு"), "Jupiter");
assert.equal(normalizePlanetKey("Guru"), "Jupiter");
assert.equal(normalizePlanetKey("சுக்கிரன்"), "Venus");
assert.equal(normalizePlanetKey("Sukran"), "Venus");
assert.equal(normalizePlanetKey("சனி"), "Saturn");
assert.equal(normalizePlanetKey("Sani"), "Saturn");
assert.equal(normalizePlanetKey("ராகு"), "Rahu");
assert.equal(normalizePlanetKey("கேது"), "Ketu");

const tamilResult = getGrahaDignity("சூரியன்", 1, 11);
assert.equal(tamilResult.isUcham, true);
assert.equal(tamilResult.colorHex, "#16A34A");
console.log("  [PASS] Tamil and transliterated Graha names verified.\n");

console.log("All Navagraha Dignity & Dik Balam tests PASSED successfully! 🌟");
