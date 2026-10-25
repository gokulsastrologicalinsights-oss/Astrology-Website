/**
 * Gokul's Astrological Insights - Deterministic Chart Correctness & Formatting Test Suite
 *
 * Validates:
 * 1. South Indian 4x4 fixed-sign grid mapping and planet distribution.
 * 2. North Indian diamond fixed-house mapping and anti-clockwise sign progression.
 * 3. 12 signs and 12 houses complete bijective coverage.
 * 4. Ascendant placement and retrograde indicator accuracy.
 * 5. Multi-planet stellium placement and boundary bounding without overlap.
 * 6. Astronomical DMS coordinate formatters (60-second carryover verification).
 * 7. Fliegel-Van Flandern Julian Day to Gregorian calendar converter.
 */

import assert from "node:assert";

console.log("=== Gokul's Astrological Insights - Deterministic Chart Correctness Suite ===\n");

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
// 1. South Indian Fixed Grid Mapping Verification
// --------------------------------------------------------------------------
const SOUTH_GRID = [
  { row: 0, col: 0, signIndex: 12 }, // Pisces
  { row: 0, col: 1, signIndex: 1 },  // Aries
  { row: 0, col: 2, signIndex: 2 },  // Taurus
  { row: 0, col: 3, signIndex: 3 },  // Gemini
  { row: 1, col: 3, signIndex: 4 },  // Cancer
  { row: 2, col: 3, signIndex: 5 },  // Leo
  { row: 3, col: 3, signIndex: 6 },  // Virgo
  { row: 3, col: 2, signIndex: 7 },  // Libra
  { row: 3, col: 1, signIndex: 8 },  // Scorpio
  { row: 3, col: 0, signIndex: 9 },  // Sagittarius
  { row: 2, col: 0, signIndex: 10 }, // Capricorn
  { row: 1, col: 0, signIndex: 11 }, // Aquarius
];

runTest("South Indian chart fixed 12-sign grid structure", () => {
  assert.strictEqual(SOUTH_GRID.length, 12, "Must contain exactly 12 outer cells");

  const signIndices = SOUTH_GRID.map((c) => c.signIndex).sort((a, b) => a - b);
  for (let s = 1; s <= 12; s++) {
    assert.strictEqual(signIndices[s - 1], s, `Sign ${s} must be present exactly once`);
  }

  // Canonical clockwise order along the perimeter:
  // (0,1)=Aries -> (0,2)=Taurus -> (0,3)=Gemini -> (1,3)=Cancer -> (2,3)=Leo ->
  // (3,3)=Virgo -> (3,2)=Libra -> (3,1)=Scorpio -> (3,0)=Sagittarius ->
  // (2,0)=Capricorn -> (1,0)=Aquarius -> (0,0)=Pisces
  const cellMap = new Map();
  SOUTH_GRID.forEach((c) => cellMap.set(`${c.row},${c.col}`, c.signIndex));

  assert.strictEqual(cellMap.get("0,1"), 1, "Aries must be at row 0, col 1");
  assert.strictEqual(cellMap.get("0,2"), 2, "Taurus must be at row 0, col 2");
  assert.strictEqual(cellMap.get("0,3"), 3, "Gemini must be at row 0, col 3");
  assert.strictEqual(cellMap.get("1,3"), 4, "Cancer must be at row 1, col 3");
  assert.strictEqual(cellMap.get("2,3"), 5, "Leo must be at row 2, col 3");
  assert.strictEqual(cellMap.get("3,3"), 6, "Virgo must be at row 3, col 3");
  assert.strictEqual(cellMap.get("3,2"), 7, "Libra must be at row 3, col 2");
  assert.strictEqual(cellMap.get("3,1"), 8, "Scorpio must be at row 3, col 1");
  assert.strictEqual(cellMap.get("3,0"), 9, "Sagittarius must be at row 3, col 0");
  assert.strictEqual(cellMap.get("2,0"), 10, "Capricorn must be at row 2, col 0");
  assert.strictEqual(cellMap.get("1,0"), 11, "Aquarius must be at row 1, col 0");
  assert.strictEqual(cellMap.get("0,0"), 12, "Pisces must be at row 0, col 0");
});

// --------------------------------------------------------------------------
// 2. North Indian Fixed House Mapping & Sign Numbering
// --------------------------------------------------------------------------
function getNorthIndianHouseSign(ascSign, houseNumber) {
  return ((ascSign - 1 + (houseNumber - 1)) % 12) + 1;
}

runTest("North Indian chart ascendant-relative sign progression", () => {
  // Test across all 12 ascendants
  for (let asc = 1; asc <= 12; asc++) {
    const signs = [];
    for (let h = 1; h <= 12; h++) {
      const sign = getNorthIndianHouseSign(asc, h);
      assert.ok(sign >= 1 && sign <= 12, `House ${h} sign out of bounds: ${sign}`);
      signs.push(sign);
    }
    // Verify all 12 signs are uniquely present
    const unique = new Set(signs);
    assert.strictEqual(unique.size, 12, `Asc ${asc} does not produce 12 unique signs`);
    // House 1 must be the ascendant sign
    assert.strictEqual(signs[0], asc, `House 1 must be Ascendant sign ${asc}`);
  }
});

// --------------------------------------------------------------------------
// 3. Known Astronomical Chart Placement Verification (1995-10-24 14:30 Chennai)
// Known Real Ephemeris Values:
// Ascendant: Aquarius (11), 9.408°
// Sun: Libra (7), 6.676°, Direct
// Moon: Libra (7), 9.105°, Direct
// Mars: Scorpio (8), 8.709°, Direct
// Mercury: Virgo (6), 19.252°, Direct
// Jupiter: Scorpio (8), 20.720°, Direct
// Venus: Libra (7), 23.687°, Direct
// Saturn: Aquarius (11), 24.886°, Retrograde
// Rahu: Libra (7), 2.270°, Retrograde
// Ketu: Aries (1), 2.270°, Retrograde
// --------------------------------------------------------------------------
const KNOWN_CHART = {
  ascendant: { sign_index: 11, sign_name: "Aquarius", degree_in_sign: 9.408 },
  planets: [
    { name: "Sun", sign_index: 7, degree_in_sign: 6.676, is_retrograde: false },
    { name: "Moon", sign_index: 7, degree_in_sign: 9.105, is_retrograde: false },
    { name: "Mars", sign_index: 8, degree_in_sign: 8.709, is_retrograde: false },
    { name: "Mercury", sign_index: 6, degree_in_sign: 19.252, is_retrograde: false },
    { name: "Jupiter", sign_index: 8, degree_in_sign: 20.72, is_retrograde: false },
    { name: "Venus", sign_index: 7, degree_in_sign: 23.687, is_retrograde: false },
    { name: "Saturn", sign_index: 11, degree_in_sign: 24.886, is_retrograde: true },
    { name: "Rahu", sign_index: 7, degree_in_sign: 2.27, is_retrograde: true },
    { name: "Ketu", sign_index: 1, degree_in_sign: 2.27, is_retrograde: true },
    { name: "Uranus", sign_index: 10, degree_in_sign: 2.861, is_retrograde: false },
    { name: "Neptune", sign_index: 9, degree_in_sign: 29.077, is_retrograde: false },
    { name: "Pluto", sign_index: 8, degree_in_sign: 5.543, is_retrograde: false },
  ],
};

runTest("South Indian chart placement with known 4-planet Libra stellium", () => {
  const planetsBySign = {};
  for (let s = 1; s <= 12; s++) planetsBySign[s] = [];
  KNOWN_CHART.planets.forEach((p) => planetsBySign[p.sign_index].push(p));

  // Cell (3,2) is Libra (Sign 7) -> Must contain Sun, Moon, Venus, Rahu (4 planets!)
  assert.strictEqual(planetsBySign[7].length, 4, "Libra must have 4 occupants");
  const libraNames = planetsBySign[7].map((p) => p.name).sort();
  assert.deepStrictEqual(libraNames, ["Moon", "Rahu", "Sun", "Venus"]);

  // Cell (3,1) is Scorpio (Sign 8) -> Must contain Mars, Jupiter, Pluto (3 planets)
  assert.strictEqual(planetsBySign[8].length, 3, "Scorpio must have 3 occupants");

  // Cell (1,0) is Aquarius (Sign 11) -> Contains Ascendant + Saturn (R)
  assert.strictEqual(KNOWN_CHART.ascendant.sign_index, 11, "Ascendant must be in Aquarius");
  assert.strictEqual(planetsBySign[11].length, 1, "Aquarius must have 1 planet (Saturn)");
  assert.strictEqual(planetsBySign[11][0].name, "Saturn");
  assert.strictEqual(planetsBySign[11][0].is_retrograde, true, "Saturn must be retrograde");

  // Empty cells verification
  assert.strictEqual(planetsBySign[12].length, 0, "Pisces must be empty");
  assert.strictEqual(planetsBySign[2].length, 0, "Taurus must be empty");
  assert.strictEqual(planetsBySign[3].length, 0, "Gemini must be empty");
  assert.strictEqual(planetsBySign[4].length, 0, "Cancer must be empty");
  assert.strictEqual(planetsBySign[5].length, 0, "Leo must be empty");
});

runTest("North Indian chart house mapping for Aquarius Ascendant", () => {
  const ascSign = KNOWN_CHART.ascendant.sign_index; // 11
  const planetsBySign = {};
  for (let s = 1; s <= 12; s++) planetsBySign[s] = [];
  KNOWN_CHART.planets.forEach((p) => planetsBySign[p.sign_index].push(p));

  // House 1 = Aquarius (Sign 11): contains Ascendant & Saturn (R)
  assert.strictEqual(getNorthIndianHouseSign(ascSign, 1), 11);
  assert.strictEqual(planetsBySign[11][0].name, "Saturn");

  // House 9 = Libra (Sign 7): contains 4-planet stellium (Sun, Moon, Venus, Rahu)
  assert.strictEqual(getNorthIndianHouseSign(ascSign, 9), 7);
  assert.strictEqual(planetsBySign[7].length, 4);

  // House 10 = Scorpio (Sign 8): contains Mars, Jupiter, Pluto
  assert.strictEqual(getNorthIndianHouseSign(ascSign, 10), 8);
  assert.strictEqual(planetsBySign[8].length, 3);

  // House 3 = Aries (Sign 1): contains Ketu
  assert.strictEqual(getNorthIndianHouseSign(ascSign, 3), 1);
  assert.strictEqual(planetsBySign[1][0].name, "Ketu");

  // House 8 = Virgo (Sign 6): contains Mercury
  assert.strictEqual(getNorthIndianHouseSign(ascSign, 8), 6);
  assert.strictEqual(planetsBySign[6][0].name, "Mercury");
});

// --------------------------------------------------------------------------
// 4. North Indian SVG Compartment Bounding & Overlap Checks
// --------------------------------------------------------------------------
const NORTH_HOUSES = [
  { houseNumber: 1, labelX: 200, labelY: 175, planetsX: 200, planetsY: 105 },
  { houseNumber: 2, labelX: 140, labelY: 80, planetsX: 100, planetsY: 45 },
  { houseNumber: 3, labelX: 75, labelY: 140, planetsX: 45, planetsY: 100 },
  { houseNumber: 4, labelX: 175, labelY: 200, planetsX: 105, planetsY: 200 },
  { houseNumber: 5, labelX: 75, labelY: 260, planetsX: 45, planetsY: 300 },
  { houseNumber: 6, labelX: 140, labelY: 320, planetsX: 100, planetsY: 355 },
  { houseNumber: 7, labelX: 200, labelY: 230, planetsX: 200, planetsY: 295 },
  { houseNumber: 8, labelX: 260, labelY: 320, planetsX: 300, planetsY: 355 },
  { houseNumber: 9, labelX: 325, labelY: 260, planetsX: 355, planetsY: 300 },
  { houseNumber: 10, labelX: 225, labelY: 200, planetsX: 295, planetsY: 200 },
  { houseNumber: 11, labelX: 325, labelY: 140, planetsX: 355, planetsY: 100 },
  { houseNumber: 12, labelX: 260, labelY: 80, planetsX: 300, planetsY: 45 },
];

runTest("North Indian SVG coordinates bounded within 400x400 canvas", () => {
  NORTH_HOUSES.forEach((h) => {
    assert.ok(h.labelX >= 20 && h.labelX <= 380, `House ${h.houseNumber} labelX ${h.labelX} out of canvas bounds`);
    assert.ok(h.labelY >= 20 && h.labelY <= 380, `House ${h.houseNumber} labelY ${h.labelY} out of canvas bounds`);
    assert.ok(h.planetsX >= 20 && h.planetsX <= 380, `House ${h.houseNumber} planetsX ${h.planetsX} out of canvas bounds`);
    assert.ok(h.planetsY >= 20 && h.planetsY <= 380, `House ${h.houseNumber} planetsY ${h.planetsY} out of canvas bounds`);
  });

  // Verify House 1 Ascendant marker does not collide with House 1 label (y=175)
  // For 1 occupant: ascY = 105 - (1 * 6 + 12) = 87. Label is at 175. Delta = 88px.
  const h1 = NORTH_HOUSES[0];
  const ascY = h1.planetsY - (1 * 6 + 12);
  const planet0Y = h1.planetsY + 8;
  assert.ok(ascY < planet0Y, "Ascendant marker must be above occupant planets");
  assert.ok(planet0Y < h1.labelY, "Occupant planets must be above sign label");
});

// --------------------------------------------------------------------------
// 5. Astronomical Formatters & 60-Second Carryover Verification
// --------------------------------------------------------------------------
function formatDms(deg) {
  if (isNaN(deg) || deg === null || deg === undefined) return "—";
  let norm = deg % 360;
  if (norm < 0) norm += 360;

  let d = Math.floor(norm);
  const minFloat = (norm - d) * 60;
  let m = Math.floor(minFloat);
  let s = Math.round((minFloat - m) * 60);

  if (s >= 60) {
    s = 0;
    m += 1;
    if (m >= 60) {
      m = 0;
      d = (d + 1) % 360;
    }
  }

  return `${d}° ${m.toString().padStart(2, "0")}' ${s.toString().padStart(2, "0")}"`;
}

function formatDm(deg) {
  if (isNaN(deg) || deg === null || deg === undefined) return "—";
  let norm = deg % 360;
  if (norm < 0) norm += 360;

  let d = Math.floor(norm);
  const minFloat = (norm - d) * 60;
  let m = Math.round(minFloat);

  if (m >= 60) {
    m = 0;
    d = (d + 1) % 360;
  }

  return `${d}°${m.toString().padStart(2, "0")}'`;
}

runTest("formatDms mathematical carryover on 60-second boundary", () => {
  // Standard test
  assert.strictEqual(formatDms(14.5), `14° 30' 00"`);
  assert.strictEqual(formatDms(0.0), `0° 00' 00"`);

  // Edge cases that previously produced 60":
  assert.strictEqual(formatDms(14.499999), `14° 30' 00"`, "Must carry over to 30' 00\", never 29' 60\"");
  assert.strictEqual(formatDms(14.99999), `15° 00' 00"`, "Must carry over to 15° 00' 00\", never 14° 59' 60\"");
  assert.strictEqual(formatDms(359.99999), `0° 00' 00"`, "Must wrap around to 0° 00' 00\"");
});

runTest("formatDm compact degree-minute carryover", () => {
  assert.strictEqual(formatDm(14.5), `14°30'`);
  assert.strictEqual(formatDm(14.9999), `15°00'`);
  assert.strictEqual(formatDm(359.999), `0°00'`);
});

// --------------------------------------------------------------------------
// 6. Julian Day to Gregorian Date Algorithm Verification
// --------------------------------------------------------------------------
function jdToCalendarDate(jd) {
  if (!jd || jd < 0) return "—";
  const I = Math.floor(jd + 0.5);
  const J = I + 32044;
  const K = Math.floor((4 * J + 3) / 146097);
  const L = J - Math.floor((146097 * K) / 4);
  const M = Math.floor((4 * L + 3) / 1461);
  const N = L - Math.floor((1461 * M) / 4);
  const P = Math.floor((5 * N + 2) / 153);
  const day = N - Math.floor((153 * P + 2) / 5) + 1;
  const month = P + 3 - 12 * Math.floor(P / 10);
  const year = 100 * K + M - 4800 + Math.floor(P / 10);

  const mStr = month.toString().padStart(2, "0");
  const dStr = day.toString().padStart(2, "0");
  return `${year}-${mStr}-${dStr}`;
}

runTest("jdToCalendarDate Fliegel-Van Flandern canonical verification", () => {
  assert.strictEqual(jdToCalendarDate(2451545.0), "2000-01-01", "J2000.0 must be 2000-01-01");
  assert.strictEqual(jdToCalendarDate(2450015.0), "1995-10-24", "Birth date JD must be 1995-10-24");
  // 120 Julian years = exactly 43830.0 days. In Gregorian calendar, 2100 is NOT a leap year (29 leap days vs 30 Julian), so date is 2115-10-25.
  assert.strictEqual(jdToCalendarDate(2450015.0 + 43830.0), "2115-10-25", "120 Julian years in Gregorian calendar (2100 non-leap) must be 2115-10-25");
});

// --------------------------------------------------------------------------
// 7. Graha Typography Scaling & Lagna Highlight Invariants
// --------------------------------------------------------------------------
function getCellItemClasses(totalItems) {
  if (totalItems >= 5) {
    return {
      textClass: "text-[9.5px] sm:text-[10.5px] md:text-[11px]",
      gapClass: "gap-x-1 gap-y-0.5",
      isMultiColumn: true,
    };
  } else if (totalItems === 4) {
    return {
      textClass: "text-[10.5px] sm:text-[11.5px] md:text-[12.5px]",
      gapClass: "gap-0.5",
      isMultiColumn: false,
    };
  } else if (totalItems === 3) {
    return {
      textClass: "text-[11.5px] sm:text-[12.5px] md:text-[13.5px]",
      gapClass: "gap-0.5 sm:gap-1",
      isMultiColumn: false,
    };
  } else if (totalItems === 2) {
    return {
      textClass: "text-[12.5px] sm:text-[14px] md:text-[15px]",
      gapClass: "gap-1 sm:gap-1.5",
      isMultiColumn: false,
    };
  } else {
    return {
      textClass: "text-sm sm:text-base md:text-[17px]",
      gapClass: "gap-1",
      isMultiColumn: false,
    };
  }
}

function getCellBgClass(isAscendant, isSavedChart) {
  const isLagnaHighlightedBlue = isSavedChart && isAscendant;
  if (isLagnaHighlightedBlue) {
    return "bg-[#D8E8FD] ring-1 ring-inset ring-[#2563EB]/40 border-[#153F6B]";
  } else if (isAscendant) {
    return "bg-[#FAF2DE]/45 border-[#183047]";
  }
  return "bg-white border-[#183047]";
}

runTest("South Indian chart Graha font scaling by occupant count", () => {
  // 1 Graha: largest prominent font
  const single = getCellItemClasses(1);
  assert.ok(single.textClass.includes("text-sm") && single.textClass.includes("md:text-[17px]"), "1 item should have large font");
  assert.strictEqual(single.isMultiColumn, false);

  // 2 Grahas: comfortably scaled font
  const double = getCellItemClasses(2);
  assert.ok(double.textClass.includes("text-[12.5px]") && double.textClass.includes("md:text-[15px]"), "2 items should scale gracefully");
  assert.strictEqual(double.isMultiColumn, false);

  // 3 Grahas: balanced readability (e.g. 9-Asc, 18-Su, Me)
  const triple = getCellItemClasses(3);
  assert.ok(triple.textClass.includes("text-[11.5px]") && triple.textClass.includes("md:text-[13.5px]"), "3 items should scale without clipping");
  assert.strictEqual(triple.isMultiColumn, false);

  // 4 Grahas: compact stacking
  const quad = getCellItemClasses(4);
  assert.ok(quad.textClass.includes("text-[10.5px]"), "4 items should fit cleanly");
  assert.strictEqual(quad.isMultiColumn, false);

  // 5+ Grahas: switches to 2-column grid to strictly prevent overflow/clipping
  const five = getCellItemClasses(5);
  assert.strictEqual(five.isMultiColumn, true, "5+ items must switch to 2-column grid");
  assert.ok(five.gapClass.includes("gap-x-1"), "2-column grid must have horizontal gap");
});

runTest("Saved horoscope chart highlights ONLY Lagna box in blue and keeps other boxes in existing style", () => {
  const ascSignIndex = 9; // Sagittarius Lagna as in user screenshot

  // Test all 12 cells for a saved chart
  for (let s = 1; s <= 12; s++) {
    const isAscendant = s === ascSignIndex;
    const bgClass = getCellBgClass(isAscendant, true);

    if (isAscendant) {
      assert.ok(bgClass.includes("bg-[#D8E8FD]"), `Lagna cell (sign ${s}) must be highlighted in blue for saved chart`);
      assert.ok(bgClass.includes("ring-[#2563EB]/40"), `Lagna cell must have blue accent ring`);
    } else {
      assert.strictEqual(bgClass, "bg-white border-[#183047]", `Non-Lagna cell (sign ${s}) must remain standard white`);
      assert.ok(!bgClass.includes("bg-[#D8E8FD]"), `Non-Lagna cell (sign ${s}) must NEVER be blue`);
    }
  }
});

runTest("Unsaved horoscope chart preserves original Lagna cream highlight", () => {
  const ascSignIndex = 1; // Aries Lagna

  for (let s = 1; s <= 12; s++) {
    const isAscendant = s === ascSignIndex;
    const bgClass = getCellBgClass(isAscendant, false);

    if (isAscendant) {
      assert.ok(bgClass.includes("bg-[#FAF2DE]/45"), `Unsaved chart Lagna must use existing cream highlight`);
      assert.ok(!bgClass.includes("bg-[#D8E8FD]"), `Unsaved chart Lagna must NOT be blue`);
    } else {
      assert.strictEqual(bgClass, "bg-white border-[#183047]", `Non-Lagna cell must be white`);
    }
  }
});

console.log(`\nResults: ${passed} passed, ${failed} failed out of ${passed + failed} tests.`);
if (failed > 0) process.exit(1);
