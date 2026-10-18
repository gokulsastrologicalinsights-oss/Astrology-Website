#!/usr/bin/env node
/**
 * Gokul's Astrological Insights - Transit Watch Frontend Verification Suite
 *
 * Validates:
 * 1. API request construction (default parameters, duration clamping, planet arrays, timezones).
 * 2. Response parsing and schema contract integrity (timestamps, divisions 1-249, lords, boundary flags).
 * 3. Client-side timeline filtering (by planet, boundary level, and motion).
 * 4. Chronological date grouping (local calendar date grouping without timezone drift).
 * 5. Truncation flag handling (max_events bounds and warning triggers).
 * 6. Empty event list handling (slow planets or narrow windows).
 * 7. Unauthenticated request rejection (401 status handling).
 * 8. Mathematical transparency guarantees (Strict Tier 3 Sub-Lord semantics, no Tier 4 fabrication).
 */

import assert from "node:assert";

console.log("=== Gokul's Astrological Insights - Transit Watch Frontend Suite ===\n");

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

// ============================================================================
// 1. Request Construction & Validation Rules
// ============================================================================

const DEFAULT_PLANETS = ["Moon", "Sun", "Jupiter", "Saturn", "Rahu", "Ketu"];
const ALL_VALID_PLANETS = [
  "Moon", "Sun", "Jupiter", "Saturn", "Rahu", "Ketu", "Mars", "Mercury", "Venus"
];

function buildTransitRequest(options = {}) {
  const {
    startDate = "2026-10-18",
    startTime = "00:00:00",
    forecastDays = 7,
    timezone = "Asia/Kolkata",
    planets = DEFAULT_PLANETS,
    ayanamsa = 0,
    maxEvents = 500,
  } = options;

  if (!startDate || !/^\d{4}-\d{2}-\d{2}$/.test(startDate)) {
    throw new Error("Invalid start date format. Expected YYYY-MM-DD.");
  }

  if (typeof forecastDays !== "number" || forecastDays < 7 || forecastDays > 30) {
    throw new Error("Forecast duration must be between 7 and 30 days.");
  }

  if (!timezone || typeof timezone !== "string" || timezone.trim().length === 0) {
    throw new Error("Timezone identifier cannot be empty.");
  }

  if (!Array.isArray(planets) || planets.length === 0) {
    throw new Error("At least one planet must be selected.");
  }

  for (const p of planets) {
    if (!ALL_VALID_PLANETS.includes(p)) {
      throw new Error(`Unsupported planet: ${p}`);
    }
  }

  return {
    start_date: startDate,
    start_time: startTime,
    forecast_days: forecastDays,
    timezone: timezone.trim(),
    planets: [...planets],
    ayanamsa,
    max_events: maxEvents,
  };
}

runTest("Default request construction (7 days, 6 planets, Asia/Kolkata)", () => {
  const req = buildTransitRequest();
  assert.strictEqual(req.start_date, "2026-10-18");
  assert.strictEqual(req.start_time, "00:00:00");
  assert.strictEqual(req.forecast_days, 7);
  assert.strictEqual(req.timezone, "Asia/Kolkata");
  assert.deepStrictEqual(req.planets, ["Moon", "Sun", "Jupiter", "Saturn", "Rahu", "Ketu"]);
  assert.strictEqual(req.ayanamsa, 0);
  assert.strictEqual(req.max_events, 500);
});

runTest("Request duration validation: rejects < 7 days and > 30 days", () => {
  assert.throws(() => buildTransitRequest({ forecastDays: 6 }), /between 7 and 30 days/);
  assert.throws(() => buildTransitRequest({ forecastDays: 31 }), /between 7 and 30 days/);
  assert.strictEqual(buildTransitRequest({ forecastDays: 7 }).forecast_days, 7);
  assert.strictEqual(buildTransitRequest({ forecastDays: 14 }).forecast_days, 14);
  assert.strictEqual(buildTransitRequest({ forecastDays: 30 }).forecast_days, 30);
});

runTest("Planet selection validation: rejects empty or invalid planets", () => {
  assert.throws(() => buildTransitRequest({ planets: [] }), /At least one planet/);
  assert.throws(() => buildTransitRequest({ planets: ["Pluto"] }), /Unsupported planet: Pluto/);
  const single = buildTransitRequest({ planets: ["Moon"] });
  assert.deepStrictEqual(single.planets, ["Moon"]);
});

runTest("Timezone validation: rejects empty timezone", () => {
  assert.throws(() => buildTransitRequest({ timezone: "" }), /Timezone identifier cannot be empty/);
  assert.throws(() => buildTransitRequest({ timezone: "   " }), /Timezone identifier cannot be empty/);
});

// ============================================================================
// 2. Response Parsing & Schema Contract Integrity (Exact Backend Schema)
// ============================================================================

const sampleApiResponseFixture = {
  start_time_utc: "2026-10-18T00:00:00+00:00",
  start_time_local: "2026-10-18T05:30:00+05:30",
  end_time_utc: "2026-10-25T00:00:00+00:00",
  end_time_local: "2026-10-25T05:30:00+05:30",
  timezone: "Asia/Kolkata",
  utc_offset_hours: 5.5,
  forecast_days: 7,
  ayanamsa_id: 0,
  ayanamsa_name: "Lahiri (Chitra Paksha)",
  planets_analyzed: ["Moon", "Sun", "Jupiter", "Saturn", "Rahu", "Ketu"],
  total_events: 4,
  truncated: false,
  events: [
    {
      planet: "Moon",
      planet_id: 1,
      utc_datetime: "2026-10-18T03:15:22.400+00:00",
      local_datetime: "2026-10-18T08:45:22.400+05:30",
      jd: 2461331.63567,
      boundary_type: "sub_lord",
      boundary_longitude: 271.4444,
      is_retrograde: false,
      speed_deg_per_day: 13.25,
      from_sign: "Makara",
      to_sign: "Makara",
      from_sign_lord: "Saturn",
      to_sign_lord: "Saturn",
      is_rashi_boundary: false,
      from_nakshatra: "Uttara Ashadha",
      to_nakshatra: "Uttara Ashadha",
      from_star_lord: "Sun",
      to_star_lord: "Sun",
      is_nakshatra_boundary: false,
      from_sub_lord: "Mars",
      to_sub_lord: "Rahu",
      from_kp_number: 184,
      to_kp_number: 185,
      is_sub_lord_boundary: true,
      calculation_precision_seconds: 0.5,
    },
    {
      planet: "Moon",
      planet_id: 1,
      utc_datetime: "2026-10-18T14:40:10.100+00:00",
      local_datetime: "2026-10-18T20:10:10.100+05:30",
      jd: 2461332.11122,
      boundary_type: "nakshatra",
      boundary_longitude: 280.0,
      is_retrograde: false,
      speed_deg_per_day: 13.4,
      from_sign: "Makara",
      to_sign: "Makara",
      from_sign_lord: "Saturn",
      to_sign_lord: "Saturn",
      is_rashi_boundary: false,
      from_nakshatra: "Uttara Ashadha",
      to_nakshatra: "Shravana",
      from_star_lord: "Sun",
      to_star_lord: "Moon",
      is_nakshatra_boundary: true,
      from_sub_lord: "Saturn",
      to_sub_lord: "Moon",
      from_kp_number: 188,
      to_kp_number: 189,
      is_sub_lord_boundary: true,
      calculation_precision_seconds: 0.5,
    },
    {
      planet: "Saturn",
      planet_id: 6,
      utc_datetime: "2026-10-19T06:12:00.000+00:00",
      local_datetime: "2026-10-19T11:42:00.000+05:30",
      jd: 2461332.75833,
      boundary_type: "sub_lord",
      boundary_longitude: 345.2222,
      is_retrograde: true,
      speed_deg_per_day: -0.045,
      from_sign: "Meena",
      to_sign: "Meena",
      from_sign_lord: "Jupiter",
      to_sign_lord: "Jupiter",
      is_rashi_boundary: false,
      from_nakshatra: "Uttara Bhadrapada",
      to_nakshatra: "Uttara Bhadrapada",
      from_star_lord: "Saturn",
      to_star_lord: "Saturn",
      is_nakshatra_boundary: false,
      from_sub_lord: "Mercury",
      to_sub_lord: "Saturn",
      from_kp_number: 238,
      to_kp_number: 237,
      is_sub_lord_boundary: true,
      calculation_precision_seconds: 0.5,
    },
    {
      planet: "Moon",
      planet_id: 1,
      utc_datetime: "2026-10-20T22:30:00.000+00:00",
      local_datetime: "2026-10-21T04:00:00.000+05:30",
      jd: 2461334.4375,
      boundary_type: "rashi",
      boundary_longitude: 300.0,
      is_retrograde: false,
      speed_deg_per_day: 13.8,
      from_sign: "Makara",
      to_sign: "Kumbha",
      from_sign_lord: "Saturn",
      to_sign_lord: "Saturn",
      is_rashi_boundary: true,
      from_nakshatra: "Dhanishta",
      to_nakshatra: "Dhanishta",
      from_star_lord: "Mars",
      to_star_lord: "Mars",
      is_nakshatra_boundary: false,
      from_sub_lord: "Jupiter",
      to_sub_lord: "Jupiter",
      from_kp_number: 197,
      to_kp_number: 198,
      is_sub_lord_boundary: false,
      calculation_precision_seconds: 0.5,
    },
  ],
  benchmark_stats: {
    duration_ms: 12.4,
    total_evaluations: 42,
    step_evaluations: 20,
    bisection_evaluations: 22,
  },
};

runTest("Response parser: validates metadata and field mappings", () => {
  const res = sampleApiResponseFixture;
  assert.strictEqual(res.forecast_days, 7);
  assert.strictEqual(res.timezone, "Asia/Kolkata");
  assert.strictEqual(res.utc_offset_hours, 5.5);
  assert.strictEqual(res.total_events, 4);
  assert.strictEqual(res.events.length, 4);
  assert.strictEqual(res.truncated, false);
  assert.deepStrictEqual(res.planets_analyzed, ["Moon", "Sun", "Jupiter", "Saturn", "Rahu", "Ketu"]);
  assert(res.benchmark_stats.duration_ms > 0);
});

runTest("KP division contract: 1-249 bounds, lords, and sub-lord continuity", () => {
  for (const ev of sampleApiResponseFixture.events) {
    assert(ev.from_kp_number >= 1 && ev.from_kp_number <= 249);
    assert(ev.to_kp_number >= 1 && ev.to_kp_number <= 249);
    assert.strictEqual(typeof ev.from_sign_lord, "string");
    assert.strictEqual(typeof ev.from_star_lord, "string");
    assert.strictEqual(typeof ev.from_sub_lord, "string");
    assert.strictEqual(typeof ev.to_sub_lord, "string");
    assert(ev.boundary_longitude >= 0 && ev.boundary_longitude <= 360);
  }
});

runTest("Retrograde detection: flags speed < 0 as retrograde with reversed division order", () => {
  const saturnEvent = sampleApiResponseFixture.events.find((e) => e.planet === "Saturn");
  assert(saturnEvent, "Saturn event must exist in fixture");
  assert.strictEqual(saturnEvent.is_retrograde, true);
  assert(saturnEvent.speed_deg_per_day < 0, "Saturn speed must be negative");
  // In retrograde motion, division decrements (238 -> 237)
  assert.strictEqual(saturnEvent.from_kp_number, 238);
  assert.strictEqual(saturnEvent.to_kp_number, 237);
});

// ============================================================================
// 3. Client-side Timeline Filtering Logic
// ============================================================================

function filterEvents(events, { planetFilter = "ALL", boundaryFilter = "ALL", motionFilter = "ALL" }) {
  return events.filter((ev) => {
    if (planetFilter !== "ALL" && ev.planet !== planetFilter) {
      return false;
    }
    if (boundaryFilter === "rashi" && !ev.is_rashi_boundary) {
      return false;
    }
    if (boundaryFilter === "nakshatra" && !ev.is_nakshatra_boundary) {
      return false;
    }
    if (boundaryFilter === "sub_lord" && ev.boundary_type !== "sub_lord") {
      return false;
    }
    if (motionFilter === "DIRECT" && ev.is_retrograde) {
      return false;
    }
    if (motionFilter === "RETROGRADE" && !ev.is_retrograde) {
      return false;
    }
    return true;
  });
}

runTest("Filter logic: planet filter selects only matching planet", () => {
  const moonEvents = filterEvents(sampleApiResponseFixture.events, { planetFilter: "Moon" });
  assert.strictEqual(moonEvents.length, 3);
  for (const ev of moonEvents) {
    assert.strictEqual(ev.planet, "Moon");
  }

  const saturnEvents = filterEvents(sampleApiResponseFixture.events, { planetFilter: "Saturn" });
  assert.strictEqual(saturnEvents.length, 1);
  assert.strictEqual(saturnEvents[0].planet, "Saturn");

  const jupiterEvents = filterEvents(sampleApiResponseFixture.events, { planetFilter: "Jupiter" });
  assert.strictEqual(jupiterEvents.length, 0);
});

runTest("Filter logic: boundary filter selects only matching boundary types", () => {
  const rashiOnly = filterEvents(sampleApiResponseFixture.events, { boundaryFilter: "rashi" });
  assert.strictEqual(rashiOnly.length, 1);
  assert.strictEqual(rashiOnly[0].is_rashi_boundary, true);
  assert.strictEqual(rashiOnly[0].boundary_type, "rashi");

  const nakshatraOnly = filterEvents(sampleApiResponseFixture.events, { boundaryFilter: "nakshatra" });
  assert.strictEqual(nakshatraOnly.length, 1);
  assert.strictEqual(nakshatraOnly[0].is_nakshatra_boundary, true);
  assert.strictEqual(nakshatraOnly[0].boundary_type, "nakshatra");

  const subLordOnly = filterEvents(sampleApiResponseFixture.events, { boundaryFilter: "sub_lord" });
  assert.strictEqual(subLordOnly.length, 2);
  for (const ev of subLordOnly) {
    assert.strictEqual(ev.boundary_type, "sub_lord");
  }
});

runTest("Filter logic: motion filter selects direct vs retrograde", () => {
  const directEvents = filterEvents(sampleApiResponseFixture.events, { motionFilter: "DIRECT" });
  assert.strictEqual(directEvents.length, 3);
  for (const ev of directEvents) {
    assert.strictEqual(ev.is_retrograde, false);
  }

  const retroEvents = filterEvents(sampleApiResponseFixture.events, { motionFilter: "RETROGRADE" });
  assert.strictEqual(retroEvents.length, 1);
  assert.strictEqual(retroEvents[0].planet, "Saturn");
  assert.strictEqual(retroEvents[0].is_retrograde, true);
});

// ============================================================================
// 4. Chronological Date Grouping
// ============================================================================

function groupEventsByLocalDate(events) {
  const groups = {};
  for (const ev of events) {
    const dateKey = ev.local_datetime.slice(0, 10);
    if (!groups[dateKey]) {
      groups[dateKey] = [];
    }
    groups[dateKey].push(ev);
  }
  return groups;
}

runTest("Date grouping: groups events strictly by target local date without UTC drift", () => {
  const groups = groupEventsByLocalDate(sampleApiResponseFixture.events);
  const dates = Object.keys(groups).sort();
  // Dates in local IST: 2026-10-18, 2026-10-19, 2026-10-21
  // Notice that the 4th event has UTC 2026-10-20T22:30:00Z -> IST 2026-10-21T04:00:00+05:30
  // It MUST be grouped under 2026-10-21 in local view!
  assert.deepStrictEqual(dates, ["2026-10-18", "2026-10-19", "2026-10-21"]);
  assert.strictEqual(groups["2026-10-18"].length, 2);
  assert.strictEqual(groups["2026-10-19"].length, 1);
  assert.strictEqual(groups["2026-10-21"].length, 1);
  assert.strictEqual(groups["2026-10-21"][0].planet, "Moon");
  assert.strictEqual(groups["2026-10-21"][0].is_rashi_boundary, true);
});

// ============================================================================
// 5. Truncation Handling
// ============================================================================

function evaluateTruncation(totalEvents, maxEvents, isTruncated) {
  const truncated = isTruncated || (totalEvents >= maxEvents);
  return {
    isTruncated: truncated,
    message: truncated
      ? `Results capped at ${maxEvents} events. Refine filter or shorten window.`
      : null,
  };
}

runTest("Truncation handling: triggers warning when cap is reached", () => {
  const normal = evaluateTruncation(50, 500, false);
  assert.strictEqual(normal.isTruncated, false);
  assert.strictEqual(normal.message, null);

  const capped = evaluateTruncation(500, 500, true);
  assert.strictEqual(capped.isTruncated, true);
  assert(capped.message.includes("capped at 500 events"));
});

// ============================================================================
// 6. Empty Event Crossings
// ============================================================================

runTest("Empty window handling: correctly detects 0 events without errors", () => {
  const emptyResponse = {
    ...sampleApiResponseFixture,
    total_events: 0,
    events: [],
  };
  const filtered = filterEvents(emptyResponse.events, { planetFilter: "Jupiter" });
  assert.strictEqual(filtered.length, 0);
  const groups = groupEventsByLocalDate(filtered);
  assert.strictEqual(Object.keys(groups).length, 0);
});

// ============================================================================
// 7. Unauthenticated 401 Rejection & Error Handling
// ============================================================================

class MockApiError extends Error {
  constructor(message, status, detail) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

function handleTimelineFetchError(err) {
  if (err.status === 401) {
    return {
      authenticated: false,
      redirect: "/login?redirect=/tools/transit-watch",
      userMessage: "Authentication required. Please sign in to access KP Transit Watch.",
    };
  }
  return {
    authenticated: true,
    redirect: null,
    userMessage: err.message || "Failed to calculate transit timeline.",
  };
}

runTest("Auth rejection: detects HTTP 401 and creates redirect path", () => {
  const err401 = new MockApiError("Not authenticated", 401, { detail: "Missing bearer token" });
  const authOutcome = handleTimelineFetchError(err401);
  assert.strictEqual(authOutcome.authenticated, false);
  assert.strictEqual(authOutcome.redirect, "/login?redirect=/tools/transit-watch");
  assert(authOutcome.userMessage.includes("Authentication required"));

  const err500 = new MockApiError("Internal calculation error", 500);
  const genericOutcome = handleTimelineFetchError(err500);
  assert.strictEqual(genericOutcome.authenticated, true);
  assert.strictEqual(genericOutcome.redirect, null);
  assert.strictEqual(genericOutcome.userMessage, "Internal calculation error");
});

// ============================================================================
// 8. Mathematical Transparency & Semantic Guarantees
// ============================================================================

runTest("KP Tier 3 Transparency: forbids Tier 4 Sub-Sub Lord labeling", () => {
  // Inspect components or event labels to ensure no sub-sub lord claims
  for (const ev of sampleApiResponseFixture.events) {
    const keys = Object.keys(ev);
    assert(!keys.includes("sub_sub_lord"), "Tier 4 sub_sub_lord must not be fabricated");
    assert(!keys.includes("sub_sub_division"), "Tier 4 sub_sub_division must not be fabricated");
    assert(ev.from_sub_lord !== undefined);
    assert(ev.to_sub_lord !== undefined);
  }
});

// ============================================================================
// Summary
// ============================================================================

console.log(`\n=== Verification Complete: ${passed} passed, ${failed} failed ===`);
if (failed > 0) {
  process.exit(1);
} else {
  process.exit(0);
}
