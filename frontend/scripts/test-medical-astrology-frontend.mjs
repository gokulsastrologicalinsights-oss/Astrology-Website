/**
 * Frontend verification script for Medical Astrology.
 * Tests:
 * 1. Documented rule matching and negative cases.
 * 2. Vedic and KP separation.
 * 3. Perspectives A, B, C.
 * 4. Bilingual English and Tamil rendering.
 * 5. Strict safety policy compliance.
 */

import assert from "node:assert";

// Sample mock horoscope response matching backend XALEN ephemeris schema
const mockHoroscope = {
  metadata: {
    engine: "XALEN Ephemeris Engine v1.0",
    birth_utc_iso: "1990-05-15T09:00:00Z",
    julian_day_ut1: 2448026.875,
    ayanamsa_id: 0,
    ayanamsa_name: "Lahiri",
    ayanamsa_deg: 23.73,
    house_system_id: 0,
    house_system_name: "Whole Sign",
    calculation_frame: "Sidereal",
    notes: [],
  },
  ascendant: {
    degree: 142.5,
    sign_index: 5, // Leo (Simha)
    sign_name: "Leo",
    sign_name_tamil: "சிம்மம்",
    degree_in_sign: 22.5,
    nakshatra: { name: "Purva Phalguni", index: 11, pada: 3, lord: "Venus", deity: "Bhaga" },
  },
  midheaven: {
    degree: 52.5,
    sign_index: 2,
    sign_name: "Taurus",
    sign_name_tamil: "ரிஷபம்",
    degree_in_sign: 22.5,
    nakshatra: { name: "Rohini", index: 4, pada: 4, lord: "Moon", deity: "Brahma" },
  },
  planets: [
    { name: "Sun", sign_index: 1, longitude: 0.8, degree_in_sign: 0.8, is_retrograde: false }, // H9 (Aries) - Exalted
    { name: "Moon", sign_index: 10, longitude: 280.5, degree_in_sign: 10.5, is_retrograde: false }, // H6 (Capricorn)
    { name: "Mars", sign_index: 11, longitude: 315.0, degree_in_sign: 15.0, is_retrograde: false }, // H7 (Aquarius)
    { name: "Mercury", sign_index: 1, longitude: 14.2, degree_in_sign: 14.2, is_retrograde: false }, // H9 (Aries)
    { name: "Jupiter", sign_index: 4, longitude: 98.4, degree_in_sign: 8.4, is_retrograde: false }, // H12 (Cancer) - Exalted
    { name: "Venus", sign_index: 12, longitude: 350.1, degree_in_sign: 20.1, is_retrograde: false }, // H8 (Pisces) - Exalted
    { name: "Saturn", sign_index: 9, longitude: 264.2, degree_in_sign: 24.2, is_retrograde: true }, // H5 (Sagittarius)
    { name: "Rahu", sign_index: 10, longitude: 284.1, degree_in_sign: 14.1, is_retrograde: true }, // H6 (Capricorn)
    { name: "Ketu", sign_index: 4, longitude: 104.1, degree_in_sign: 14.1, is_retrograde: true }, // H12 (Cancer)
  ],
  houses: [],
};

const mockDasa = {
  metadata: mockHoroscope.metadata,
  moon_sidereal_deg: 280.5,
  nakshatra: { name: "Shravana", index: 22, pada: 1, lord: "Moon", deity: "Vishnu" },
  birth_dasa_lord: "Moon",
  birth_balance_years: 7.5,
  birth_balance_formatted: "7y 6m 0d",
  dasa_tree: [
    { lord: "Moon", level: "Mahadasha", start_jd: 2448026.8, end_jd: 2450766.8, duration_days: 2740, duration_years: 7.5, start_date_iso: "1990-05-15", end_date_iso: "1997-11-15", start_age: "0y", end_age: "7y 6m" },
    { lord: "Mars", level: "Mahadasha", start_jd: 2450766.8, end_jd: 2453322.8, duration_days: 2556, duration_years: 7.0, start_date_iso: "1997-11-15", end_date_iso: "2004-11-15", start_age: "7y 6m", end_age: "14y 6m" },
    { lord: "Rahu", level: "Mahadasha", start_jd: 2453322.8, end_jd: 2459892.8, duration_days: 6570, duration_years: 18.0, start_date_iso: "2004-11-15", end_date_iso: "2022-11-15", start_age: "14y 6m", end_age: "32y 6m" },
    { lord: "Jupiter", level: "Mahadasha", start_jd: 2459892.8, end_jd: 2465736.8, duration_days: 5844, duration_years: 16.0, start_date_iso: "2022-11-15", end_date_iso: "2038-11-15", start_age: "32y 6m", end_age: "48y 6m" },
  ],
  active_period: {
    mahadasha: "Jupiter",
    antardasha: "Saturn",
    pratyantardasha: "Mercury",
    target_jd: 2461333.0,
    target_date_iso: "2026-10-19",
  },
};

const mockKp = {
  metadata: mockHoroscope.metadata,
  planetary_positions: [],
  cuspal_analysis: [
    { house: 1, cusp_degree: 142.5, sign_index: 5, sign_name: "Leo", sign_lord: "Sun", star_lord: "Venus", sub_lord: "Jupiter", sub_sub_lord: "Moon" },
    { house: 2, cusp_degree: 172.5, sign_index: 6, sign_name: "Virgo", sign_lord: "Mercury", star_lord: "Moon", sub_lord: "Mars", sub_sub_lord: "Saturn" },
    { house: 3, cusp_degree: 202.5, sign_index: 7, sign_name: "Libra", sign_lord: "Venus", star_lord: "Jupiter", sub_lord: "Mercury", sub_sub_lord: "Venus" },
    { house: 4, cusp_degree: 232.5, sign_index: 8, sign_name: "Scorpio", sign_lord: "Mars", star_lord: "Saturn", sub_lord: "Sun", sub_sub_lord: "Rahu" },
    { house: 5, cusp_degree: 262.5, sign_index: 9, sign_name: "Sagittarius", sign_lord: "Jupiter", star_lord: "Ketu", sub_lord: "Venus", sub_sub_lord: "Jupiter" },
    { house: 6, cusp_degree: 292.5, sign_index: 10, sign_name: "Capricorn", sign_lord: "Saturn", star_lord: "Mars", sub_lord: "Mercury", sub_sub_lord: "Sun" },
    { house: 7, cusp_degree: 322.5, sign_index: 11, sign_name: "Aquarius", sign_lord: "Saturn", star_lord: "Jupiter", sub_lord: "Jupiter", sub_sub_lord: "Moon" },
    { house: 8, cusp_degree: 352.5, sign_index: 12, sign_name: "Pisces", sign_lord: "Jupiter", star_lord: "Mercury", sub_lord: "Venus", sub_sub_lord: "Mars" },
    { house: 9, cusp_degree: 22.5, sign_index: 1, sign_name: "Aries", sign_lord: "Mars", star_lord: "Venus", sub_lord: "Saturn", sub_sub_lord: "Rahu" },
    { house: 10, cusp_degree: 52.5, sign_index: 2, sign_name: "Taurus", sign_lord: "Venus", star_lord: "Sun", sub_lord: "Moon", sub_sub_lord: "Jupiter" },
    { house: 11, cusp_degree: 82.5, sign_index: 3, sign_name: "Gemini", sign_lord: "Mercury", star_lord: "Rahu", sub_lord: "Mars", sub_sub_lord: "Saturn" },
    { house: 12, cusp_degree: 112.5, sign_index: 4, sign_name: "Cancer", sign_lord: "Moon", star_lord: "Saturn", sub_lord: "Jupiter", sub_sub_lord: "Sun" },
  ],
  significators: [
    { planet: "Mercury", level_a: [6], level_b: [9], level_c: [2, 11], level_d: [2, 11], all_houses: [2, 6, 9, 11] },
    { planet: "Jupiter", level_a: [12], level_b: [12], level_c: [5, 8], level_d: [5, 8], all_houses: [5, 8, 12] },
    { planet: "Saturn", level_a: [5], level_b: [5], level_c: [6, 7], level_d: [6, 7], all_houses: [5, 6, 7] },
  ],
};

async function testMedicalAstrologyFrontend() {
  console.log("=== Medical Astrology Frontend Evaluation Tests ===");

  // Import evaluator module dynamically
  const { evaluateMedicalAstrologyClient, SAFETY_DISCLAIMER_EN, SAFETY_DISCLAIMER_TA } =
    await import("../src/lib/medical-astrology-evaluator.ts");

  // 1. Test basic evaluation
  const result = evaluateMedicalAstrologyClient(mockHoroscope, mockKp, mockDasa, null);
  assert.ok(result, "Evaluation result must exist");
  assert.strictEqual(result.rule_set_version, "1.0.0");

  // 2. Test Safety Disclaimers
  console.log("Checking exact safety disclaimers...");
  assert.strictEqual(result.disclaimer_en, SAFETY_DISCLAIMER_EN);
  assert.strictEqual(result.disclaimer_ta, SAFETY_DISCLAIMER_TA);
  assert.ok(result.disclaimer_en.includes("educational and research purposes only"));
  assert.ok(result.disclaimer_ta.includes("கல்வி மற்றும் ஆராய்ச்சி நோக்கங்களுக்காக மட்டுமே"));

  // 3. Test Perspective A: Birth-Chart Research
  console.log("Checking Perspective A: Birth-chart research...");
  const bc = result.vedic_analysis.birth_chart;
  assert.strictEqual(bc.lagna_analysis.house_number, 1);
  assert.strictEqual(bc.sixth_house_analysis.house_number, 6);
  assert.strictEqual(bc.eighth_house_analysis.house_number, 8);
  assert.strictEqual(bc.twelfth_house_analysis.house_number, 12);
  assert.strictEqual(bc.anatomical_mappings.length, 12);

  // Check 6th house occupants in mock (Moon and Rahu are in House 6 Capricorn)
  assert.ok(bc.sixth_house_analysis.occupants.includes("Moon"));
  assert.ok(bc.sixth_house_analysis.occupants.includes("Rahu"));

  // Triggered classical rules should include Moon in 6th and Rahu in 6th
  const ruleIds = bc.triggered_rules.map((r) => r.id);
  assert.ok(ruleIds.includes("bphs_17_moon_6th"), "Must trigger Moon in 6th rule");
  assert.ok(ruleIds.includes("bphs_17_rahu_6th"), "Must trigger Rahu in 6th rule");

  // Check source citations
  const moonRule = bc.triggered_rules.find((r) => r.id === "bphs_17_moon_6th");
  assert.strictEqual(moonRule.source, "Brihat Parashara Hora Shastra");
  assert.strictEqual(moonRule.system, "vedic");
  assert.ok(moonRule.interpretation_tamil.length > 10);

  // 4. Test Perspective B: Current-Period Research
  console.log("Checking Perspective B: Current-period research...");
  const cp = result.vedic_analysis.current_period;
  assert.strictEqual(cp.mahadasha, "Jupiter");
  assert.strictEqual(cp.bhukti, "Saturn");
  assert.strictEqual(cp.antara, "Mercury");
  assert.ok(cp.traditional_synthesis_en.includes("Jupiter"));
  assert.ok(cp.traditional_synthesis_ta.includes("Jupiter"));

  // 5. Test Perspective C: Historical Period Research
  console.log("Checking Perspective C: Historical periods...");
  const hp = result.vedic_analysis.historical_periods;
  assert.strictEqual(hp.periods.length, 4);
  assert.strictEqual(hp.periods[0].lord, "Moon");
  assert.ok(hp.periods[0].traditional_notes_en.includes("Moon"));
  assert.ok(hp.periods[0].traditional_notes_ta.includes("Moon"));

  // 6. Test KP Analytical System
  console.log("Checking KP Analytical System...");
  const kpRes = result.kp_analysis;
  assert.ok(kpRes, "KP analysis must be populated");
  const c6 = kpRes.sixth_csl;
  assert.strictEqual(c6.cusp_number, 6);
  assert.strictEqual(c6.csl_planet, "Mercury");
  assert.strictEqual(c6.is_data_available, true);
  assert.strictEqual(c6.recovery_status, "present");
  assert.strictEqual(c6.disease_status, "present");
  assert.strictEqual(c6.chronic_status, "not_found");
  assert.strictEqual(c6.hospitalization_status, "not_found");
  assert.strictEqual(c6.disease_signified, true);
  assert.strictEqual(c6.recovery_signified, true);
  assert.ok(c6.recovery_houses.includes(11));
  assert.ok(c6.disease_houses.includes(6));
  assert.ok(c6.primary_signification_en.includes("Mercury"));
  assert.ok(c6.primary_signification_ta.includes("Mercury"));

  // KP rules triggered
  const kpRuleIds = kpRes.kp_rules.map((r) => r.id);
  assert.ok(kpRuleIds.includes("kp_rule_6csl_signifies_6"), "Should trigger 6th CSL signifies 6");
  assert.ok(kpRuleIds.includes("kp_rule_recovery_1_5_11"), "Should trigger recovery rule for 11");

  for (const r of kpRes.kp_rules) {
    assert.strictEqual(r.system, "kp", "KP rules must have system='kp'");
    assert.strictEqual(r.source, "KP Reader IV: Medical Astrology");
  }

  // 7. Test Missing Data Graceful Handling
  console.log("Checking missing data graceful handling...");
  const emptyRes = evaluateMedicalAstrologyClient(mockHoroscope, null, null, null);
  assert.ok(emptyRes);
  assert.strictEqual(emptyRes.kp_analysis, null);
  assert.strictEqual(emptyRes.vedic_analysis.current_period.mahadasha, "Unknown");
  assert.strictEqual(emptyRes.vedic_analysis.historical_periods.periods.length, 0);

  // 8. Test Missing CSL Data returns data_unavailable (never false negative 'No')
  console.log("Checking missing CSL data handling...");
  const kpMissingCsl = JSON.parse(JSON.stringify(mockKp));
  kpMissingCsl.cuspal_analysis[5].sub_lord = "";
  const missingCslRes = evaluateMedicalAstrologyClient(mockHoroscope, kpMissingCsl, mockDasa, null);
  assert.ok(missingCslRes.kp_analysis);
  const c6Missing = missingCslRes.kp_analysis.sixth_csl;
  assert.strictEqual(c6Missing.is_data_available, false);
  assert.strictEqual(c6Missing.recovery_status, "data_unavailable");
  assert.strictEqual(c6Missing.disease_status, "data_unavailable");
  assert.strictEqual(c6Missing.chronic_status, "data_unavailable");
  assert.strictEqual(c6Missing.hospitalization_status, "data_unavailable");

  // 9. Test Missing Significators Data returns data_unavailable
  console.log("Checking missing significators data handling...");
  const kpMissingSigs = JSON.parse(JSON.stringify(mockKp));
  kpMissingSigs.significators = [];
  kpMissingSigs.house_significators = [];
  const missingSigsRes = evaluateMedicalAstrologyClient(mockHoroscope, kpMissingSigs, mockDasa, null);
  assert.ok(missingSigsRes.kp_analysis);
  const c6NoSigs = missingSigsRes.kp_analysis.sixth_csl;
  assert.strictEqual(c6NoSigs.is_data_available, false);
  assert.strictEqual(c6NoSigs.recovery_status, "data_unavailable");
  assert.strictEqual(c6NoSigs.disease_status, "data_unavailable");
  assert.strictEqual(c6NoSigs.chronic_status, "data_unavailable");
  assert.strictEqual(c6NoSigs.hospitalization_status, "data_unavailable");

  // 10. Test Real Schema with signified_houses and strength_order
  console.log("Checking real KP engine schema mapping...");
  const realSchemaKp = {
    metadata: mockHoroscope.metadata,
    planetary_positions: [
      { planet: "Venus", longitude: 349.0, star_lord: "Mercury", sub_lord: "Ketu" },
      { planet: "Mercury", longitude: 14.2, star_lord: "Venus", sub_lord: "Sun" },
    ],
    cuspal_analysis: [
      { house: 1, cusp_degree: 142.5, sign_name: "Leo", star_lord: "Venus", sub_lord: "Sun" },
      { house: 2, cusp_degree: 172.5, sign_name: "Virgo", star_lord: "Moon", sub_lord: "Mars" },
      { house: 3, cusp_degree: 202.5, sign_name: "Libra", star_lord: "Jupiter", sub_lord: "Mercury" },
      { house: 4, cusp_degree: 232.5, sign_name: "Scorpio", star_lord: "Saturn", sub_lord: "Sun" },
      { house: 5, cusp_degree: 262.5, sign_name: "Sagittarius", star_lord: "Ketu", sub_lord: "Venus" },
      { house: 6, cusp_degree: 304.2, sign_name: "Aquarius", star_lord: "Mars", sub_lord: "Venus" },
    ],
    significators: [
      {
        planet: "Venus",
        signified_houses: [1, 2, 7, 8, 9, 10],
        strength_order: [
          { house: 1, type: "StarLord" },
          { house: 8, type: "StarLord" },
          { house: 10, type: "StarLord" },
          { house: 7, type: "Occupant" },
          { house: 2, type: "Owner" },
          { house: 9, type: "Owner" },
        ],
      },
    ],
  };

  const realSchemaRes = evaluateMedicalAstrologyClient(mockHoroscope, realSchemaKp, null, null);
  assert.ok(realSchemaRes.kp_analysis);
  const realC6 = realSchemaRes.kp_analysis.sixth_csl;
  assert.strictEqual(realC6.csl_planet, "Venus");
  assert.strictEqual(realC6.csl_star_lord, "Mercury");
  assert.deepStrictEqual(realC6.signified_houses, [1, 2, 7, 8, 9, 10]);
  assert.strictEqual(realC6.recovery_status, "present");
  assert.strictEqual(realC6.chronic_status, "present");
  assert.strictEqual(realC6.disease_status, "not_found");
  assert.strictEqual(realC6.hospitalization_status, "not_found");
  assert.strictEqual(realC6.signification_details.length, 6);

  console.log("Checking screenshot chart (Gokul 43.01° Taurus) and placeholder-free strings...");
  const screenshotKp = {
    metadata: {
      ayanamsa_name: "Lahiri",
      ayanamsa_deg: 23.8404,
      house_system_name: "Placidus",
    },
    planetary_positions: [
      { planet: "Rahu", longitude: 119.5631, sign_name: "Cancer", star_lord: "Mercury", sub_lord: "Saturn" },
      { planet: "Mercury", longitude: 255.4, sign_name: "Sagittarius", star_lord: "Venus", sub_lord: "Jupiter" },
      { planet: "Moon", longitude: 85.1, sign_name: "Gemini", star_lord: "Jupiter", sub_lord: "Saturn" },
    ],
    cuspal_analysis: [
      { house: 1, cusp_degree: 248.5, sign_name: "Sagittarius", star_lord: "Ketu", sub_lord: "Venus" },
      { house: 2, cusp_degree: 279.1, sign_name: "Capricorn", star_lord: "Sun", sub_lord: "Venus" },
      { house: 3, cusp_degree: 312.4, sign_name: "Aquarius", star_lord: "Rahu", sub_lord: "Saturn" },
      { house: 4, cusp_degree: 344.8, sign_name: "Pisces", star_lord: "Saturn", sub_lord: "Rahu" },
      { house: 5, cusp_degree: 14.5, sign_name: "Aries", star_lord: "Venus", sub_lord: "Venus" },
      { house: 6, cusp_degree: 43.006, sign_name: "Taurus", star_lord: "Moon", sub_lord: "Rahu" },
    ],
    significators: [
      {
        planet: "Rahu",
        signified_houses: [12],
        strength_order: [
          { house: 12, type: "StarLord" },
          { house: 12, type: "Occupant" },
        ],
      },
    ],
    house_significators: [
      { house: 7, level_a: [], level_b: [], level_c: ["Rahu"], level_d: ["Mercury"] },
      { house: 10, level_a: [], level_b: [], level_c: ["Rahu"], level_d: ["Mercury"] },
      { house: 12, level_a: ["Ketu"], level_b: ["Rahu", "Mercury"], level_c: [], level_d: [] },
    ],
  };

  const screenshotRes = evaluateMedicalAstrologyClient(mockHoroscope, screenshotKp, null, null);
  assert.ok(screenshotRes.kp_analysis);
  const sc6 = screenshotRes.kp_analysis.sixth_csl;

  // 1. Cusp and planet parameters match screenshot exactly
  assert.strictEqual(Math.round(sc6.cusp_degree * 100) / 100, 43.01);
  assert.strictEqual(sc6.sign_name, "Taurus");
  assert.strictEqual(sc6.cusp_star_lord, "Moon");
  assert.strictEqual(sc6.csl_planet, "Rahu");
  assert.strictEqual(sc6.csl_star_lord, "Mercury");

  // 2. Strict distinction between cusp star lord and CSL planet's star lord
  assert.notStrictEqual(sc6.cusp_star_lord, sc6.csl_star_lord);

  // 3. Strict check: NO un-interpolated placeholders ({csl}, {starLord}, etc.)
  for (const text of [sc6.primary_signification_en, sc6.primary_signification_ta]) {
    assert.ok(!text.includes("{csl}"), `Text must not contain literal {csl}: ${text}`);
    assert.ok(!text.includes("{cslStarL}"), `Text must not contain literal {cslStarL}: ${text}`);
    assert.ok(!text.includes("{starLord}"), `Text must not contain literal {starLord}: ${text}`);
    assert.ok(!text.includes("{housesStr}"), `Text must not contain literal {housesStr}: ${text}`);
    assert.ok(!/\{[a-zA-Z0-9_]+\}/.test(text), `Text must not contain un-interpolated placeholder: ${text}`);
  }

  // 4. Interpolation verified
  assert.ok(sc6.primary_signification_ta.includes("Rahu"), "Tamil explanation must include 'Rahu'");
  assert.ok(sc6.primary_signification_ta.includes("Mercury"), "Tamil explanation must include 'Mercury'");
  assert.ok(sc6.primary_signification_ta.includes("7, 10, 12"), "Tamil explanation must include houses '7, 10, 12'");

  // 5. Four categories
  assert.strictEqual(sc6.recovery_status, "not_found");
  assert.strictEqual(sc6.disease_status, "not_found");
  assert.strictEqual(sc6.chronic_status, "not_found");
  assert.strictEqual(sc6.hospitalization_status, "present");
  assert.deepStrictEqual(sc6.hospitalization_houses, [12]);

  // 6. Provenance multi-level preservation: H12 appears twice with distinct channels
  assert.strictEqual(sc6.signification_details.length, 4);
  const sc6H12Details = sc6.signification_details.filter((d) => d.house === 12);
  assert.strictEqual(sc6H12Details.length, 2);
  const channels = sc6.signification_details.map((d) => d.planet_channel);
  assert.ok(channels.some((c) => c && c.includes("Rahu -> Mercury")));
  assert.ok(channels.some((c) => c && c.includes("Rahu (Direct)")));

  console.log("All 11 Medical Astrology frontend verification tests PASSED successfully!");
}

testMedicalAstrologyFrontend().catch((err) => {
  console.error("Test failed:", err);
  process.exit(1);
});

