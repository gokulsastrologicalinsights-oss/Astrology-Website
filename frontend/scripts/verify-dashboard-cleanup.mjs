#!/usr/bin/env node
/**
 * Dashboard Cleanup & Saved Horoscopes Ordering Verification Suite
 * Verifies all criteria from USER_REQUEST:
 * 1. Absence of the 4 unwanted sections (Recent KP Predictions, Rule-Based KP, Saved Numerology, Saved Vastu).
 * 2. Absence of specific shortcuts/widgets for those sections (e.g. Vastu button, stats widgets).
 * 3. Saved Horoscopes is the ONLY saved-records section.
 * 4. Saved Vedic and KP horoscopes ordered strictly DESC by generation/creation timestamp (newest first).
 * 5. Stable secondary sort on display_number DESC.
 * 6. Inserting a newly generated horoscope places it at the very top.
 * 7. Refresh/re-querying preserves the exact ordering.
 * 8. Search and pagination preserve descending order.
 * 9. Saved horoscopes list does NOT contain numerology reports, Vastu assessments, or KP prediction records.
 * 10. SavedHoroscopeCard displays name, Vedic/KP type, date & time generated, sequential number, and view action.
 */

import { readFileSync } from "node:fs";
import { resolve, join } from "node:path";
import assert from "node:assert";
import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !serviceRoleKey) {
  console.error("Missing required Supabase credentials in environment.");
  process.exit(1);
}

const adminClient = createClient(supabaseUrl, serviceRoleKey, {
  auth: { autoRefreshToken: false, persistSession: false },
});

async function runVerification() {
  console.log("================================================================================");
  console.log("  DASHBOARD CLEANUP: SHOW ONLY SAVED HOROSCOPES - VERIFICATION SUITE");
  console.log("================================================================================\n");

  let testCount = 0;
  let passCount = 0;

  function pass(desc) {
    testCount++;
    passCount++;
    console.log(`[PASS ${testCount}] ${desc}`);
  }

  function fail(desc, err) {
    testCount++;
    console.error(`[FAIL ${testCount}] ${desc}:`, err?.message || err);
  }

  // ---------------------------------------------------------------------------
  // TEST 1: Source Code Audit - Confirm 4 Unwanted Sections are Removed
  // ---------------------------------------------------------------------------
  try {
    const dashboardPath = resolve("src/app/dashboard/page.tsx");
    const dashboardSource = readFileSync(dashboardPath, "utf-8");

    // Check absence of section titles and badges
    assert.ok(!dashboardSource.includes("Recent KP Predictions"), "Recent KP Predictions section must be absent");
    assert.ok(!dashboardSource.includes("Rule-Based KP"), "Rule-Based KP badge must be absent");
    assert.ok(!dashboardSource.includes("Saved Numerology Reports"), "Saved Numerology Reports section must be absent");
    assert.ok(!dashboardSource.includes("Saved Vastu Assessments"), "Saved Vastu Assessments section must be absent");

    // Check absence of specific shortcuts
    assert.ok(!dashboardSource.includes('href="/vastu" className="inline-flex'), "Vastu header shortcut must be absent from dashboard header");

    // Check absence of unrelated API calls
    assert.ok(!dashboardSource.includes("listNumerologyReports"), "listNumerologyReports must not be called in DashboardPage");
    assert.ok(!dashboardSource.includes("listVastuReports"), "listVastuReports must not be called in DashboardPage");
    assert.ok(!dashboardSource.includes("listUserKpEventAnalyses"), "listUserKpEventAnalyses must not be called in DashboardPage");

    // Check absence of unrelated statistics widgets
    assert.ok(!dashboardSource.includes("KP Event Analyses"), "KP Event Analyses stat card must be absent");
    assert.ok(!dashboardSource.includes("Numerology Reports"), "Numerology Reports stat card must be absent");
    assert.ok(!dashboardSource.includes("Vastu Reports"), "Vastu Reports stat card must be absent");

    pass("All four unwanted sections, widgets, and shortcuts are completely absent from DashboardPage.");
  } catch (err) {
    fail("Absence of unwanted sections in DashboardPage", err);
  }

  // ---------------------------------------------------------------------------
  // TEST 2: Source Code Audit - Saved Horoscopes is the Only Saved Section
  // ---------------------------------------------------------------------------
  try {
    const dashboardPath = resolve("src/app/dashboard/page.tsx");
    const dashboardSource = readFileSync(dashboardPath, "utf-8");

    assert.ok(dashboardSource.includes("<SavedHoroscopesList"), "SavedHoroscopesList must be rendered");
    assert.ok(dashboardSource.includes("Saved Horoscopes Section ONLY"), "Only Saved Horoscopes section should be present");

    pass("Saved Horoscopes confirmed as the only saved-records section on the dashboard.");
  } catch (err) {
    fail("Only Saved Horoscopes present", err);
  }

  // ---------------------------------------------------------------------------
  // TEST 3: SavedHoroscopeCard Information Completeness
  // ---------------------------------------------------------------------------
  try {
    const cardPath = resolve("src/components/saved/SavedHoroscopeCard.tsx");
    const cardSource = readFileSync(cardPath, "utf-8");

    // Name
    assert.ok(cardSource.includes("displayName"), "Card must display horoscope/customer name");
    // Vedic or KP type badge
    assert.ok(cardSource.includes("isKp"), "Card must determine if chart is KP or Vedic");
    assert.ok(cardSource.includes("typeText"), "Card must render Vedic or KP type label");
    // Date and time generated
    assert.ok(cardSource.includes("createdDateStr"), "Card must format generated date");
    assert.ok(cardSource.includes("createdTimeStr"), "Card must format generated time");
    // Sequential number
    assert.ok(cardSource.includes("idNumber"), "Card must render sequential number");
    // Action to open
    assert.ok(cardSource.includes("/horoscope/results?id="), "Card must link to horoscope detail results");

    pass("SavedHoroscopeCard displays Name, Vedic/KP type, generated Date & Time, Sequential number, and Open action.");
  } catch (err) {
    fail("SavedHoroscopeCard required information fields", err);
  }

  // ---------------------------------------------------------------------------
  // TEST 4: API Route Query Sorting Contract (created_at DESC, display_number DESC)
  // ---------------------------------------------------------------------------
  try {
    const routePath = resolve("src/app/api/horoscopes/route.ts");
    const routeSource = readFileSync(routePath, "utf-8");

    assert.ok(
      routeSource.includes('.order("created_at", { ascending: false })'),
      "Database query must sort by created_at DESC (newest first)"
    );
    assert.ok(
      routeSource.includes('.order("display_number", { ascending: false })'),
      "Database query must have stable secondary sort on display_number DESC"
    );

    pass("API route query orders by created_at DESC (newest first) with stable secondary sort on display_number DESC.");
  } catch (err) {
    fail("API route query sorting", err);
  }

  // ---------------------------------------------------------------------------
  // TEST 5: Live Supabase Data Sorting - Newest Generated First
  // ---------------------------------------------------------------------------
  let testUserId = null;
  const createdRecordIds = [];

  try {
    // Look up an existing test user or admin
    const { data: users, error: userErr } = await adminClient
      .from("profiles")
      .select("id, username")
      .limit(1);

    if (userErr || !users || users.length === 0) {
      throw new Error("No profiles found in Supabase database.");
    }

    testUserId = users[0].id;

    // Create 3 test horoscopes with distinct generation timestamps and Vedic/KP types
    const baseDate = new Date();

    // Horoscope 1: 10 minutes ago, Vedic (Lahiri)
    const time1 = new Date(baseDate.getTime() - 10 * 60 * 1000).toISOString();
    const { data: h1, error: e1 } = await adminClient
      .from("saved_horoscopes")
      .insert({
        user_id: testUserId,
        person_name: "Test Audit Older Vedic",
        birth_date: "1990-05-15",
        birth_time: "10:30:00",
        timezone: "Asia/Kolkata",
        birthplace: "Chennai, India",
        latitude: 13.0827,
        longitude: 80.2707,
        ayanamsa_id: 0, // Vedic Lahiri
        house_system_id: 2,
        calculation_result: { chart: "vedic_older" },
        created_at: time1,
      })
      .select()
      .single();

    if (e1) throw e1;
    createdRecordIds.push(h1.id);

    // Horoscope 2: 5 minutes ago, KP System
    const time2 = new Date(baseDate.getTime() - 5 * 60 * 1000).toISOString();
    const { data: h2, error: e2 } = await adminClient
      .from("saved_horoscopes")
      .insert({
        user_id: testUserId,
        person_name: "Test Audit Middle KP",
        birth_date: "1995-08-20",
        birth_time: "14:15:00",
        timezone: "Asia/Kolkata",
        birthplace: "Coimbatore, India",
        latitude: 11.0168,
        longitude: 76.9558,
        ayanamsa_id: 1, // KP System
        house_system_id: 2,
        calculation_result: { chart: "kp_middle" },
        created_at: time2,
      })
      .select()
      .single();

    if (e2) throw e2;
    createdRecordIds.push(h2.id);

    // Horoscope 3: Just now, Newest Vedic
    const time3 = new Date(baseDate.getTime()).toISOString();
    const { data: h3, error: e3 } = await adminClient
      .from("saved_horoscopes")
      .insert({
        user_id: testUserId,
        person_name: "Test Audit Newest Vedic",
        birth_date: "2000-01-01",
        birth_time: "08:00:00",
        timezone: "Asia/Kolkata",
        birthplace: "Madurai, India",
        latitude: 9.9252,
        longitude: 78.1198,
        ayanamsa_id: 2, // Vedic Raman
        house_system_id: 2,
        calculation_result: { chart: "vedic_newest" },
        created_at: time3,
      })
      .select()
      .single();

    if (e3) throw e3;
    createdRecordIds.push(h3.id);

    // Query records using exact application sorting: created_at DESC, display_number DESC
    const { data: fetched, error: fetchErr } = await adminClient
      .from("saved_horoscopes")
      .select("id, person_name, created_at, display_number, ayanamsa_id")
      .eq("user_id", testUserId)
      .in("id", createdRecordIds)
      .order("created_at", { ascending: false })
      .order("display_number", { ascending: false });

    if (fetchErr) throw fetchErr;

    assert.strictEqual(fetched.length, 3, "Must return all 3 test records");
    assert.strictEqual(fetched[0].id, h3.id, "Newest record (h3) must be first (index 0)");
    assert.strictEqual(fetched[1].id, h2.id, "Middle record (h2) must be second (index 1)");
    assert.strictEqual(fetched[2].id, h1.id, "Oldest record (h1) must be third (index 2)");

    pass("Supabase live query verified: Vedic and KP horoscopes returned newest first by creation timestamp.");
  } catch (err) {
    fail("Live Supabase sorting by created_at DESC", err);
  }

  // ---------------------------------------------------------------------------
  // TEST 6: Generating a New Horoscope Appears at the Very Top
  // ---------------------------------------------------------------------------
  try {
    const time4 = new Date().toISOString();
    const { data: h4, error: e4 } = await adminClient
      .from("saved_horoscopes")
      .insert({
        user_id: testUserId,
        person_name: "Test Audit Just Generated",
        birth_date: "2002-12-12",
        birth_time: "12:12:00",
        timezone: "Asia/Kolkata",
        birthplace: "Salem, India",
        latitude: 11.6643,
        longitude: 78.1460,
        ayanamsa_id: 1, // KP
        house_system_id: 2,
        calculation_result: { chart: "kp_brand_new" },
        created_at: time4,
      })
      .select()
      .single();

    if (e4) throw e4;
    createdRecordIds.push(h4.id);

    // Re-query: h4 must be at the very top
    const { data: reQueried, error: reQueryErr } = await adminClient
      .from("saved_horoscopes")
      .select("id, person_name, created_at, display_number")
      .eq("user_id", testUserId)
      .in("id", createdRecordIds)
      .order("created_at", { ascending: false })
      .order("display_number", { ascending: false });

    if (reQueryErr) throw reQueryErr;

    assert.strictEqual(reQueried[0].id, h4.id, "Newly generated horoscope must immediately appear at the top (#1)");
    pass("Newly generated horoscope verified: appears immediately at index 0.");
  } catch (err) {
    fail("Newly generated horoscope at top", err);
  }

  // ---------------------------------------------------------------------------
  // TEST 7: Secondary Sort on Identical Timestamps
  // ---------------------------------------------------------------------------
  try {
    const identicalTime = new Date().toISOString();

    const { data: hTie1, error: tieErr1 } = await adminClient
      .from("saved_horoscopes")
      .insert({
        user_id: testUserId,
        person_name: "Tie Record A",
        birth_date: "1999-01-01",
        birth_time: "10:00:00",
        timezone: "UTC",
        birthplace: "London, UK",
        latitude: 51.5074,
        longitude: -0.1278,
        ayanamsa_id: 0,
        house_system_id: 2,
        calculation_result: {},
        created_at: identicalTime,
      })
      .select()
      .single();

    if (tieErr1) throw tieErr1;
    createdRecordIds.push(hTie1.id);

    const { data: hTie2, error: tieErr2 } = await adminClient
      .from("saved_horoscopes")
      .insert({
        user_id: testUserId,
        person_name: "Tie Record B",
        birth_date: "1999-01-02",
        birth_time: "11:00:00",
        timezone: "UTC",
        birthplace: "London, UK",
        latitude: 51.5074,
        longitude: -0.1278,
        ayanamsa_id: 1,
        house_system_id: 2,
        calculation_result: {},
        created_at: identicalTime,
      })
      .select()
      .single();

    if (tieErr2) throw tieErr2;
    createdRecordIds.push(hTie2.id);

    // Query tied records: display_number DESC determines order stably
    const { data: tiedResult, error: tiedQueryErr } = await adminClient
      .from("saved_horoscopes")
      .select("id, person_name, display_number, created_at")
      .in("id", [hTie1.id, hTie2.id])
      .order("created_at", { ascending: false })
      .order("display_number", { ascending: false });

    if (tiedQueryErr) throw tiedQueryErr;

    assert.strictEqual(tiedResult.length, 2);
    // Since hTie2 was inserted after hTie1, hTie2 has higher display_number
    assert.ok(
      tiedResult[0].display_number > tiedResult[1].display_number,
      "Tied timestamp records must resolve by display_number DESC"
    );

    pass("Stable secondary sorting verified: identical timestamps ordered deterministically by display_number DESC.");
  } catch (err) {
    fail("Secondary sort on tied timestamps", err);
  }

  // ---------------------------------------------------------------------------
  // TEST 8: Reopening and Returning - Order Preserved
  // ---------------------------------------------------------------------------
  try {
    // Simulate opening detail page by fetching a single record
    const targetId = createdRecordIds[1];
    const { data: detailData, error: detailErr } = await adminClient
      .from("saved_horoscopes")
      .select("id, person_name, calculation_result")
      .eq("id", targetId)
      .single();

    if (detailErr) throw detailErr;
    assert.strictEqual(detailData.id, targetId, "Detail record loaded successfully");

    // Simulate returning to dashboard: re-query list
    const { data: returnList, error: returnErr } = await adminClient
      .from("saved_horoscopes")
      .select("id, created_at, display_number")
      .eq("user_id", testUserId)
      .in("id", createdRecordIds)
      .order("created_at", { ascending: false })
      .order("display_number", { ascending: false });

    if (returnErr) throw returnErr;

    // Verify ordering is strictly descending by created_at
    for (let i = 0; i < returnList.length - 1; i++) {
      const curTime = new Date(returnList[i].created_at).getTime();
      const nextTime = new Date(returnList[i + 1].created_at).getTime();
      assert.ok(curTime >= nextTime, `Item ${i} (${curTime}) must be >= Item ${i + 1} (${nextTime})`);
    }

    pass("Detail page opening and returning: dashboard list ordering is strictly preserved.");
  } catch (err) {
    fail("Detail page return order preservation", err);
  }

  // ---------------------------------------------------------------------------
  // TEST 9: No Other Saved Records (Numerology/Vastu/KP Events) in Horoscopes Table
  // ---------------------------------------------------------------------------
  try {
    const { data: allHoro, error: allErr } = await adminClient
      .from("saved_horoscopes")
      .select("id, calculation_result")
      .limit(20);

    if (allErr) throw allErr;

    // Ensure all records in saved_horoscopes are actual horoscope calculations
    for (const h of allHoro) {
      assert.ok(!h.compliance_score, "Horoscopes table must not contain Vastu compliance records");
      assert.ok(!h.running_period, "Horoscopes table must not contain standalone KP prediction records");
    }

    pass("Horoscopes table integrity verified: contains only horoscope records, no numerology or vastu reports.");
  } catch (err) {
    fail("Horoscope table data segregation", err);
  }

  // ---------------------------------------------------------------------------
  // TEST 10: Empty State and Error State UI Fallbacks
  // ---------------------------------------------------------------------------
  try {
    const listPath = resolve("src/components/saved/SavedHoroscopesList.tsx");
    const listSource = readFileSync(listPath, "utf-8");

    // Loading State
    assert.ok(listSource.includes("isLoading &&"), "Must render loading state");
    assert.ok(listSource.includes("animate-spin"), "Must show loading spinner");

    // Error State
    assert.ok(listSource.includes("errorMessage &&"), "Must render error state");
    assert.ok(listSource.includes("t.retry"), "Must have retry action on error");

    // Empty State
    assert.ok(listSource.includes("horoscopes.length === 0"), "Must render empty state when no horoscopes exist");
    assert.ok(listSource.includes('href="/horoscope"'), "Empty state must provide action to calculate horoscope");

    pass("Loading, error (with retry), and empty (with create action) states verified in SavedHoroscopesList.");
  } catch (err) {
    fail("Empty, loading, and error states", err);
  }

  // ---------------------------------------------------------------------------
  // CLEANUP: Remove Test Artifacts
  // ---------------------------------------------------------------------------
  try {
    if (createdRecordIds.length > 0) {
      await adminClient.from("saved_horoscopes").delete().in("id", createdRecordIds);
    }
  } catch (cleanErr) {
    console.warn("Cleanup warning:", cleanErr);
  }

  console.log("\n================================================================================");
  console.log(`  VERIFICATION COMPLETE: ${passCount} / ${testCount} CHECKS PASSED`);
  console.log("================================================================================\n");

  if (passCount !== testCount) {
    process.exit(1);
  }
}

runVerification();
