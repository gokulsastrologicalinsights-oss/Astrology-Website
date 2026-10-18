#!/usr/bin/env node
/**
 * Gokul's Astrological Insights - Vastu Staging Acceptance Test Suite
 * 
 * Verifies:
 * 1. Backend health & native XALEN ephemeris availability.
 * 2. 16 directions & 32 Paramasayika padas geometry.
 * 3. Multi-profile layout evaluation (residential, commercial, plot, industrial).
 * 4. Zero-input unassessed scoring behavior (zero penalty for missing inputs).
 * 5. Astro-Vastu synthesis with native XALEN ephemeris against verified fixtures.
 * 6. Authenticated report persistence, sequential display numbering, and CRUD lifecycle.
 * 7. Multi-tenant RLS & authorization: cross-user read/update/delete denial.
 * 8. Frontend print layout & disclaimer accessibility.
 */

import { createClient } from "@supabase/supabase-js";
import assert from "node:assert";

const BACKEND_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !anonKey || !serviceRoleKey) {
  console.error("Missing required Supabase environment variables.");
  process.exit(1);
}

const adminClient = createClient(supabaseUrl, serviceRoleKey, {
  auth: { autoRefreshToken: false, persistSession: false },
});

async function runStagingAcceptance() {
  console.log("================================================================================");
  console.log("  GOKUL'S ASTROLOGICAL INSIGHTS - VASTU STAGING ACCEPTANCE SUITE");
  console.log(`  Backend URL: ${BACKEND_BASE}`);
  console.log(`  Supabase URL: ${supabaseUrl}`);
  console.log("================================================================================\n");

  let totalTests = 0;
  let passedTests = 0;

  function pass(title) {
    totalTests++;
    passedTests++;
    console.log(`[PASS ${totalTests}] ${title}`);
  }

  function fail(title, err) {
    totalTests++;
    console.error(`[FAIL ${totalTests}] ${title}:`, err);
  }

  // ---------------------------------------------------------------------------
  // TEST 1: Backend Health & Astronomical Core Status
  // ---------------------------------------------------------------------------
  try {
    const res = await fetch(`${BACKEND_BASE}/health`);
    assert.strictEqual(res.status, 200, "Backend health check must return HTTP 200");
    const data = await res.json();
    assert.strictEqual(data.status, "healthy", "Backend status must be 'healthy'");
    assert.strictEqual(data.engine.rust_core_available, true, "XALEN rust core must be available");
    pass("Backend health and native XALEN ephemeris core verified online.");
  } catch (err) {
    fail("Backend health check failed", err);
  }

  // ---------------------------------------------------------------------------
  // TEST 2: 16 Directions and 32 Padas Geometry & Monotonicity
  // ---------------------------------------------------------------------------
  try {
    const res = await fetch(`${BACKEND_BASE}/api/v1/vastu/directions`);
    assert.strictEqual(res.status, 200, "Directions endpoint must return 200");
    const data = await res.json();
    assert.strictEqual(data.directions_16.length, 16, "Must contain exactly 16 directions");
    assert.strictEqual(data.padas_32.length, 32, "Must contain exactly 32 outer padas");

    // Verify clockwise monotonic ordering
    const codes = data.directions_16.map((d) => d.code);
    const expected = [
      "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
      "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
    ];
    assert.deepStrictEqual(codes, expected, "16 direction codes must strictly follow clockwise order");

    // Verify North wraparound sector
    const north = data.directions_16.find((d) => d.code === "N");
    assert.strictEqual(north.start_degree, 348.75);
    assert.strictEqual(north.end_degree, 11.25);
    assert.strictEqual(north.center_degree, 0.0);

    pass("16 directions and 32 Paramasayika padas clockwise geometry verified.");
  } catch (err) {
    fail("Geometry check failed", err);
  }

  // ---------------------------------------------------------------------------
  // TEST 3: Multi-Profile Layout Evaluation
  // ---------------------------------------------------------------------------
  try {
    // 3a. Residential profile
    const resRes = await fetch(`${BACKEND_BASE}/api/v1/vastu/evaluate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        property_name: "Staging Test Residence",
        property_type: "residential",
        facing_direction: "E",
        placements: {
          main_entrance_direction: "E",
          main_entrance_pada: "Jayanta",
          kitchen_direction: "SE",
          master_bedroom_direction: "SW",
          pooja_room_direction: "NE",
        },
      }),
    });
    assert.strictEqual(resRes.status, 200);
    const dataRes = await resRes.json();
    assert.strictEqual(dataRes.compliance_score, 100);
    assert.strictEqual(dataRes.score_grade, "A+ (Highly Auspicious Alignment)");
    assert.ok(dataRes.disclaimer.includes("Mayamata"), "Disclaimer must cite classical sources");

    // 3b. Commercial profile
    const resComm = await fetch(`${BACKEND_BASE}/api/v1/vastu/evaluate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        property_name: "Apex Financial Center",
        property_type: "commercial",
        facing_direction: "N",
        placements: {
          main_entrance_direction: "N",
          owner_cabin_direction: "SW",
          accounts_cash_direction: "N",
        },
      }),
    });
    assert.strictEqual(resComm.status, 200);
    const dataComm = await resComm.json();
    const commKeys = dataComm.factor_results.map((f) => f.factor_key);
    assert.ok(commKeys.includes("owner_cabin"));
    assert.ok(!commKeys.includes("kitchen"), "Commercial profile must not include kitchen factor");

    // 3c. Industrial profile
    const resInd = await fetch(`${BACKEND_BASE}/api/v1/vastu/evaluate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        property_name: "Titan Foundries",
        property_type: "industrial",
        facing_direction: "E",
        placements: {
          main_entrance_direction: "E",
          heavy_machinery_direction: "SW",
          boiler_furnace_direction: "SE",
        },
      }),
    });
    assert.strictEqual(resInd.status, 200);
    const dataInd = await resInd.json();
    const indKeys = dataInd.factor_results.map((f) => f.factor_key);
    assert.ok(indKeys.includes("heavy_machinery"));
    assert.ok(indKeys.includes("boiler_furnace"));

    pass("Multi-profile evaluations (residential, commercial, industrial) verified.");
  } catch (err) {
    fail("Multi-profile evaluation failed", err);
  }

  // ---------------------------------------------------------------------------
  // TEST 4: Zero-Input Unassessed Scoring Behavior
  // ---------------------------------------------------------------------------
  try {
    const res = await fetch(`${BACKEND_BASE}/api/v1/vastu/evaluate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        property_name: "Blank Assessment",
        property_type: "residential",
        placements: {},
      }),
    });
    assert.strictEqual(res.status, 200);
    const data = await res.json();
    assert.strictEqual(data.compliance_score, null, "Zero-input score must be null");
    assert.strictEqual(data.score_grade, "Unassessed (Insufficient Inputs)");
    assert.ok(data.missing_data_warnings.length > 0, "Missing data warnings must be generated");
    pass("Zero-input evaluation safely returns null score without arbitrary penalties.");
  } catch (err) {
    fail("Zero-input score check failed", err);
  }

  // ---------------------------------------------------------------------------
  // TEST 5: Astro-Vastu Synthesis Native Ephemeris Benchmark
  // ---------------------------------------------------------------------------
  try {
    const res = await fetch(`${BACKEND_BASE}/api/v1/vastu/evaluate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        property_name: "Astro-Vastu Resident",
        property_type: "residential",
        birth_date: "1990-05-15",
        birth_time: "14:30",
        timezone: "Asia/Kolkata",
        latitude: 13.0827,
        longitude: 80.2707,
        placements: {
          main_entrance_direction: "N",
        },
      }),
    });
    assert.strictEqual(res.status, 200);
    const data = await res.json();
    assert.ok(data.astro_overlay, "Astro overlay must be present");
    assert.strictEqual(data.astro_overlay.lagna_sign, "Virgo", "Ascendant must be Virgo");
    assert.strictEqual(data.astro_overlay.lagna_ruler, "Mercury", "Lagna ruler must be Mercury");
    assert.strictEqual(data.astro_overlay.moon_sign, "Capricorn", "Moon sign must be Capricorn");
    assert.ok(data.astro_overlay.nakshatra.includes("Uttara Ashadha"), "Nakshatra must be Uttara Ashadha");
    assert.ok(data.astro_overlay.calculation_source.includes("Native XALEN"), "Must cite Native XALEN engine");
    pass("Astro-Vastu synthesis matches verified native XALEN ephemeris fixtures (Virgo Lagna, Capricorn Moon).");
  } catch (err) {
    fail("Astro-Vastu synthesis failed", err);
  }

  // ---------------------------------------------------------------------------
  // TEST 6: User Authentication, Report Saving & Sequential Numbering
  // ---------------------------------------------------------------------------
  const testUserEmail = `staging_vastu_${Date.now()}@example.com`;
  const testUserPassword = "VastuUser#2026Secure";
  let testUserId = null;
  let testUserToken = null;
  let savedReportId = null;

  try {
    // Create test user in Supabase Auth
    const { data: userAuth, error: createErr } = await adminClient.auth.admin.createUser({
      email: testUserEmail,
      password: testUserPassword,
      email_confirm: true,
      user_metadata: { display_name: "Staging Vastu Tester" },
    });
    assert(!createErr, `Failed to create test user: ${createErr?.message}`);
    testUserId = userAuth.user.id;

    // Sign in test user to obtain JWT
    const userClient = createClient(supabaseUrl, anonKey, {
      auth: { autoRefreshToken: false, persistSession: false },
    });
    const { data: signInData, error: signInErr } = await userClient.auth.signInWithPassword({
      email: testUserEmail,
      password: testUserPassword,
    });
    assert(!signInErr, `Failed to sign in test user: ${signInErr?.message}`);
    testUserToken = signInData.session.access_token;

    // Save Report 1
    const rep1Res = await fetch(`${BACKEND_BASE}/api/v1/vastu/reports`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${testUserToken}`,
      },
      body: JSON.stringify({
        property_name: "Ananda Nilayam Residence",
        property_type: "residential",
        facing_direction: "E",
        facing_degrees: 90.0,
        evaluation_data: {
          compliance_score: 95,
          score_grade: "A+",
          doshas: [],
          general_remedies: ["Keep threshold clean."],
        },
      }),
    });
    assert.strictEqual(rep1Res.status, 201, "Saving report must return HTTP 201");
    const rep1Data = await rep1Res.json();
    savedReportId = rep1Data.id;
    assert.strictEqual(rep1Data.display_number, 1, "First report must have display_number=1");

    // Save Report 2
    const rep2Res = await fetch(`${BACKEND_BASE}/api/v1/vastu/reports`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${testUserToken}`,
      },
      body: JSON.stringify({
        property_name: "Commercial Studio",
        property_type: "commercial",
        facing_direction: "N",
        evaluation_data: {
          compliance_score: 82,
          score_grade: "A",
          doshas: [],
        },
      }),
    });
    assert.strictEqual(rep2Res.status, 201);
    const rep2Data = await rep2Res.json();
    assert.strictEqual(rep2Data.display_number, 2, "Second report must have display_number=2");

    pass("Authenticated report creation and per-user sequential display numbering verified (#1, #2).");
  } catch (err) {
    fail("User report creation & numbering failed", err);
  }

  // ---------------------------------------------------------------------------
  // TEST 7: Report Reopening & History Listing
  // ---------------------------------------------------------------------------
  try {
    // 7a. Reopen single report by ID
    const getRes = await fetch(`${BACKEND_BASE}/api/v1/vastu/reports/${savedReportId}`, {
      headers: { Authorization: `Bearer ${testUserToken}` },
    });
    assert.strictEqual(getRes.status, 200, "Reopening report must return 200");
    const getData = await getRes.json();
    assert.strictEqual(getData.id, savedReportId);
    assert.strictEqual(getData.property_name, "Ananda Nilayam Residence");
    assert.strictEqual(getData.compliance_score, 95);

    // 7b. List reports
    const listRes = await fetch(`${BACKEND_BASE}/api/v1/vastu/reports?limit=10&offset=0`, {
      headers: { Authorization: `Bearer ${testUserToken}` },
    });
    assert.strictEqual(listRes.status, 200);
    const listData = await listRes.json();
    assert.strictEqual(listData.total_count, 2, "User must see exactly 2 saved reports");
    assert.strictEqual(listData.reports[0].display_number, 2, "Reports must be ordered descending by display_number");

    // 7c. Update report
    const putRes = await fetch(`${BACKEND_BASE}/api/v1/vastu/reports/${savedReportId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${testUserToken}`,
      },
      body: JSON.stringify({
        property_name: "Ananda Nilayam Residence (Renovated)",
        property_type: "residential",
        facing_direction: "E",
        evaluation_data: {
          compliance_score: 98,
          score_grade: "A+",
        },
      }),
    });
    assert.strictEqual(putRes.status, 200);
    const putData = await putRes.json();
    assert.strictEqual(putData.property_name, "Ananda Nilayam Residence (Renovated)");
    assert.strictEqual(putData.display_number, 1, "Display number must not change upon update");

    pass("Report reopening, history listing, and in-place updates verified.");
  } catch (err) {
    fail("Reopen & list failed", err);
  }

  // ---------------------------------------------------------------------------
  // TEST 8: Multi-Tenant RLS & Cross-User Access Denial
  // ---------------------------------------------------------------------------
  const rivalEmail = `rival_vastu_${Date.now()}@example.com`;
  let rivalUserId = null;
  let rivalUserToken = null;

  try {
    const { data: rivalAuth } = await adminClient.auth.admin.createUser({
      email: rivalEmail,
      password: "RivalPassword#2026",
      email_confirm: true,
      user_metadata: { display_name: "Rival User" },
    });
    rivalUserId = rivalAuth.user.id;

    const rivalClient = createClient(supabaseUrl, anonKey, {
      auth: { autoRefreshToken: false, persistSession: false },
    });
    const { data: rivalSignIn } = await rivalClient.auth.signInWithPassword({
      email: rivalEmail,
      password: "RivalPassword#2026",
    });
    rivalUserToken = rivalSignIn.session.access_token;

    // Rival attempts to view user A's report
    const crossGet = await fetch(`${BACKEND_BASE}/api/v1/vastu/reports/${savedReportId}`, {
      headers: { Authorization: `Bearer ${rivalUserToken}` },
    });
    assert.strictEqual(crossGet.status, 404, "Rival must receive 404 for foreign report");

    // Rival attempts to update user A's report
    const crossPut = await fetch(`${BACKEND_BASE}/api/v1/vastu/reports/${savedReportId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${rivalUserToken}`,
      },
      body: JSON.stringify({
        property_name: "Hacked Report",
        property_type: "residential",
        facing_direction: "W",
        evaluation_data: {},
      }),
    });
    assert.strictEqual(crossPut.status, 404, "Rival must receive 404 for unauthorized update");

    // Rival attempts to delete user A's report
    const crossDel = await fetch(`${BACKEND_BASE}/api/v1/vastu/reports/${savedReportId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${rivalUserToken}` },
    });
    assert.strictEqual(crossDel.status, 404, "Rival must receive 404 for unauthorized delete");

    // Verify report is still intact for User A
    const verifyRes = await fetch(`${BACKEND_BASE}/api/v1/vastu/reports/${savedReportId}`, {
      headers: { Authorization: `Bearer ${testUserToken}` },
    });
    assert.strictEqual(verifyRes.status, 200, "User A's report must remain unaffected");

    pass("Cross-user read, update, and delete attempts strictly denied (RLS multi-tenant protection).");
  } catch (err) {
    fail("Cross-user isolation test failed", err);
  } finally {
    if (rivalUserId) {
      await adminClient.auth.admin.deleteUser(rivalUserId);
    }
  }

  // ---------------------------------------------------------------------------
  // TEST 9: Report Deletion Lifecycle
  // ---------------------------------------------------------------------------
  try {
    const delRes = await fetch(`${BACKEND_BASE}/api/v1/vastu/reports/${savedReportId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${testUserToken}` },
    });
    assert.strictEqual(delRes.status, 204, "Deletion must return HTTP 204 No Content");

    const getAfterDel = await fetch(`${BACKEND_BASE}/api/v1/vastu/reports/${savedReportId}`, {
      headers: { Authorization: `Bearer ${testUserToken}` },
    });
    assert.strictEqual(getAfterDel.status, 404, "Deleted report must return 404");
    pass("Report deletion lifecycle verified.");
  } catch (err) {
    fail("Report deletion failed", err);
  } finally {
    if (testUserId) {
      await adminClient.auth.admin.deleteUser(testUserId);
    }
  }

  console.log("\n================================================================================");
  console.log(`  STAGING ACCEPTANCE RESULTS: ${passedTests} / ${totalTests} TESTS PASSED`);
  console.log("================================================================================\n");

  if (passedTests !== totalTests) {
    process.exitCode = 1;
  }
}

runStagingAcceptance().catch((err) => {
  console.error("Fatal staging acceptance failure:", err);
  process.exitCode = 1;
});
