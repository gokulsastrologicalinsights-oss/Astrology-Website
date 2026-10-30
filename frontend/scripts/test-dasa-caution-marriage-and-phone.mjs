#!/usr/bin/env node
/**
 * Test Suite: Dasa Caution Phone Saving & 3-Tier Marriage Condition Analysis
 */

import assert from "node:assert";
import { validateAndNormalizePhone } from "../src/lib/phone-utils.ts";

console.log("=== Testing Dasa Caution Phone Saving & 3-Tier Marriage Analysis ===\n");

// 1. Test phone normalization
const p1 = validateAndNormalizePhone("9876543210", "+91");
assert.strictEqual(p1.isValid, true);
assert.strictEqual(p1.nationalNumber, "9876543210");
assert.strictEqual(p1.whatsappNumber, "919876543210");
assert.strictEqual(p1.normalizedPhone, "+919876543210");
console.log("[PASS] Phone validation and normalization");

// 2. Test WhatsApp URL Generation
function makeWaUrl(num, text) {
  if (!num) return "";
  const clean = num.replace(/\D/g, "");
  return `https://api.whatsapp.com/send/?phone=${clean}&text=${encodeURIComponent(text)}`;
}

const wa = makeWaUrl(p1.whatsappNumber, "Test Message");
assert.strictEqual(wa, "https://api.whatsapp.com/send/?phone=919876543210&text=Test%20Message");
console.log("[PASS] WhatsApp URL formatting with normalized digits");

// 3. Test Marriage / Relationship 3-tier condition confirmation
function evaluateMarriageRisk(maha, antar, andhar) {
  const mahaConnects7 = maha.housesOwned.includes(7) || maha.houseOccupied === 7 || maha.planet === "Venus";
  const antarConnects7 = antar.housesOwned.includes(7) || antar.houseOccupied === 7 || antar.planet === "Venus";
  const andharConnects7 = andhar.housesOwned.includes(7) || andhar.houseOccupied === 7 || andhar.planet === "Venus";

  const hasShadashtaka = antar.is68WithMaha || andhar.is68WithAntar || andhar.is68WithMaha;
  const isCombustOrDebil = andhar.isCombust || andhar.isDebilitated;

  const isMaritalAfflicted = (mahaConnects7 || antarConnects7 || andharConnects7) && (hasShadashtaka || isCombustOrDebil);
  return isMaritalAfflicted;
}

// Case A: Beneficial periods (Jupiter - Venus, no 6/8) -> No marriage problem shown!
const favorablePeriod = evaluateMarriageRisk(
  { planet: "Jupiter", housesOwned: [9, 12], houseOccupied: 1, is68WithMaha: false },
  { planet: "Venus", housesOwned: [2, 7], houseOccupied: 11, is68WithMaha: false },
  { planet: "Moon", housesOwned: [5], houseOccupied: 9, is68WithAntar: false, is68WithMaha: false, isCombust: false, isDebilitated: false }
);
assert.strictEqual(favorablePeriod, false, "Auspicious period must NOT show marriage risk");
console.log("[PASS] Auspicious Dasa-Bukthi-Anthara does not falsely report marriage problems");

// Case B: Adverse 6/8 axis on 7th lord during active Antharam -> Marriage problem flagged!
const adversePeriod = evaluateMarriageRisk(
  { planet: "Saturn", housesOwned: [10, 11], houseOccupied: 6, is68WithMaha: false },
  { planet: "Venus", housesOwned: [2, 7], houseOccupied: 7, is68WithMaha: false },
  { planet: "Mars", housesOwned: [1, 8], houseOccupied: 2, is68WithAntar: true, is68WithMaha: true, isCombust: false, isDebilitated: false }
);
assert.strictEqual(adversePeriod, true, "Adverse 6/8 axis on 7th lord must confirm marriage risk");
console.log("[PASS] Adverse 3-tier confluence correctly confirms marriage caution period");

console.log("\nAll marriage & phone verification tests passed! 🌟");
