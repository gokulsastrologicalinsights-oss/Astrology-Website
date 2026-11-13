#!/usr/bin/env node
/**
 * Verification test for Saved Chart Search functionality in Marriage Compatibility tool
 */

import { readFileSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import assert from "node:assert";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log("=== Marriage Compatibility Saved Chart Search Test Suite ===\n");

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

const modalPath = resolve(__dirname, "../src/components/marriage-compatibility/SavedChartSearchModal.tsx");
const pagePath = resolve(__dirname, "../src/app/tools/marriage-compatibility/page.tsx");

runTest("SavedChartSearchModal.tsx exists", () => {
  assert(existsSync(modalPath), "SavedChartSearchModal.tsx does not exist");
});

const modalContent = readFileSync(modalPath, "utf-8");
const pageContent = readFileSync(pagePath, "utf-8");

runTest("SavedChartSearchModal exports the modal component", () => {
  assert(modalContent.includes("export function SavedChartSearchModal"), "Missing SavedChartSearchModal component");
});

runTest("SavedChartSearchModal supports search input, clear button, and refresh", () => {
  assert(modalContent.includes("searchQuery"), "Missing searchQuery state");
  assert(modalContent.includes("filteredHoroscopes"), "Missing filteredHoroscopes memo");
  assert(modalContent.includes("onRefresh"), "Missing onRefresh prop support");
});

runTest("SavedChartSearchModal displays complete birth particulars and Get Data button", () => {
  assert(modalContent.includes("birth_date"), "Missing birth_date display");
  assert(modalContent.includes("birth_time"), "Missing birth_time display");
  assert(modalContent.includes("birthplace"), "Missing birthplace display");
  assert(modalContent.includes("Get Data") || modalContent.includes("விவரங்களைப் பெறுக"), "Missing Get Data action button");
});

runTest("marriage-compatibility/page.tsx imports and renders SavedChartSearchModal", () => {
  assert(pageContent.includes("import { SavedChartSearchModal }"), "Missing import of SavedChartSearchModal");
  assert(pageContent.includes("<SavedChartSearchModal"), "Missing <SavedChartSearchModal usage in page");
});

runTest("Page contains dedicated Search buttons for Groom and Bride", () => {
  assert(pageContent.includes('setSearchModalTarget("groom")'), "Missing Groom search modal trigger");
  assert(pageContent.includes('setSearchModalTarget("bride")'), "Missing Bride search modal trigger");
  assert(pageContent.includes("Search Chart") || pageContent.includes("ஜாதகம் தேடுக"), "Missing Search Chart button text");
});

runTest("Page provides inline search inputs with dedicated Search buttons", () => {
  assert(pageContent.includes("groomSearchQuery"), "Missing groomSearchQuery state");
  assert(pageContent.includes("brideSearchQuery"), "Missing brideSearchQuery state");
  assert(pageContent.includes("filteredGroomSavedHoroscopes"), "Missing filteredGroomSavedHoroscopes");
  assert(pageContent.includes("filteredBrideSavedHoroscopes"), "Missing filteredBrideSavedHoroscopes");
});

runTest("Page provides 'Load from Saved Chart' in Direct Input mode", () => {
  assert(pageContent.includes("Load from Saved Chart") || pageContent.includes("சேமித்த ஜாதகத்திலிருந்து பெறுக"), "Missing Load from Saved Chart button");
});

runTest("Page retrieves and populates all data from saved chart", () => {
  assert(pageContent.includes("handleApplyGroomSaved"), "Missing handleApplyGroomSaved");
  assert(pageContent.includes("handleApplyBrideSaved"), "Missing handleApplyBrideSaved");
  assert(pageContent.includes("setGroomDate(item.birth_date)"), "Missing setGroomDate from saved item");
  assert(pageContent.includes("setGroomTime"), "Missing setGroomTime from saved item");
  assert(pageContent.includes("setGroomLat"), "Missing setGroomLat from saved item");
  assert(pageContent.includes("setGroomLon"), "Missing setGroomLon from saved item");
  assert(pageContent.includes("setGroomTz"), "Missing setGroomTz from saved item");
  assert(pageContent.includes("setBrideDate(item.birth_date)"), "Missing setBrideDate from saved item");
  assert(pageContent.includes("setBrideTime"), "Missing setBrideTime from saved item");
  assert(pageContent.includes("setBrideLat"), "Missing setBrideLat from saved item");
  assert(pageContent.includes("setBrideLon"), "Missing setBrideLon from saved item");
  assert(pageContent.includes("setBrideTz"), "Missing setBrideTz from saved item");
});

runTest("Page displays active confirmation cards with retrieved data", () => {
  assert(pageContent.includes("selectedGroomHoroscope"), "Missing selectedGroomHoroscope");
  assert(pageContent.includes("selectedBrideHoroscope"), "Missing selectedBrideHoroscope");
  assert(pageContent.includes("Data retrieved from saved chart") || pageContent.includes("விவரங்கள் பெறப்பட்டன"), "Missing confirmation card label");
});

console.log(`\n=============================================`);
console.log(`Verification Complete: ${passed} passed, ${failed} failed`);
console.log(`=============================================\n`);

if (failed > 0) process.exit(1);
