/**
 * Test script for Horoscope Writing frontend component and routing.
 */

import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const frontendDir = path.resolve(__dirname, "..");

console.log("=== Testing Horoscope Writing Frontend Integration ===");

// 1. Verify page.tsx exists
const pagePath = path.join(frontendDir, "src", "app", "tools", "horoscope-writing", "page.tsx");
assert(fs.existsSync(pagePath), "horoscope-writing/page.tsx should exist");
const pageContent = fs.readFileSync(pagePath, "utf-8");
assert(pageContent.includes("HoroscopeWritingContent"), "page.tsx should contain HoroscopeWritingContent");
assert(pageContent.includes("downloadHoroscopeWritingPdf"), "page.tsx should include PDF download handler");
assert(pageContent.includes("isEditingOverrides"), "page.tsx should support astrologer overrides");

// 2. Verify tools/page.tsx includes Horoscope Writing
const toolsPagePath = path.join(frontendDir, "src", "app", "tools", "page.tsx");
const toolsContent = fs.readFileSync(toolsPagePath, "utf-8");
assert(toolsContent.includes("/tools/horoscope-writing"), "tools/page.tsx must link to /tools/horoscope-writing");
assert(toolsContent.includes("பாரம்பரிய தமிழ் ஜாதகக் குறிப்பு"), "tools/page.tsx must contain Tamil title");

// 3. Verify Navbar.tsx includes Horoscope Writing
const navbarPath = path.join(frontendDir, "src", "components", "layout", "Navbar.tsx");
const navbarContent = fs.readFileSync(navbarPath, "utf-8");
assert(navbarContent.includes("/tools/horoscope-writing"), "Navbar.tsx must link to /tools/horoscope-writing");

// 4. Verify types.ts includes HoroscopeWriting models
const typesPath = path.join(frontendDir, "src", "lib", "types.ts");
const typesContent = fs.readFileSync(typesPath, "utf-8");
assert(typesContent.includes("HoroscopeWritingResponse"), "types.ts must declare HoroscopeWritingResponse");
assert(typesContent.includes("HoroscopeWritingRequest"), "types.ts must declare HoroscopeWritingRequest");

// 5. Verify api.ts includes client functions
const apiPath = path.join(frontendDir, "src", "lib", "api.ts");
const apiContent = fs.readFileSync(apiPath, "utf-8");
assert(apiContent.includes("calculateHoroscopeWriting"), "api.ts must export calculateHoroscopeWriting");
assert(apiContent.includes("downloadHoroscopeWritingPdf"), "api.ts must export downloadHoroscopeWritingPdf");
assert(apiContent.includes("saveHoroscopeWriting"), "api.ts must export saveHoroscopeWriting");

console.log("=== All Frontend Horoscope Writing Integration Checks Passed! ===");
