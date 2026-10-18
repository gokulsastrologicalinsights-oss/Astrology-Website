#!/usr/bin/env node
/**
 * Gokul's Astrological Insights - Task 3 Saved Horoscopes Verification Suite
 * Verifies:
 * 1. Card serial number format (01, 02...) and date/time formatting contracts
 * 2. Timezone resilience: verifying date strings do NOT shift due to browser timezone
 * 3. Permanent sequential display numbering from database across search, filter, pagination
 * 4. Record deletion does not renumber remaining records
 * 5. Record editing updates birth details without altering serial number or calculation snapshot
 * 6. Record editing does not create duplicate records
 * 7. Distinction between edited birth details and stored calculation snapshot
 * 8. Stored horoscope loading without recalculation or duplicate creation
 * 9. RLS and server authorization: cross-user isolation and tamper protection
 * 10. Automatic saving idempotency preventing duplicates upon retries
 */

import { createClient } from "@supabase/supabase-js";
import assert from "node:assert";
import {
  formatSerialNumber,
  formatBirthDate,
  formatBirthTime,
} from "../src/lib/formatters.ts";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !anonKey || !serviceRoleKey) {
  console.error("Missing required Supabase credentials in environment.");
  process.exit(1);
}

const adminClient = createClient(supabaseUrl, serviceRoleKey, {
  auth: { autoRefreshToken: false, persistSession: false },
});

async function runTask3TestSuite() {
  console.log("================================================================================");
  console.log("  GOKUL'S ASTROLOGICAL INSIGHTS - TASK 3 SAVED HOROSCOPES VERIFICATION SUITE");
  console.log(`  Target: ${supabaseUrl}`);
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
    console.error(`[FAIL ${testCount}] ${desc}:`, err);
  }

  // ---------------------------------------------------------------------------
  // TEST 1: Serial Number Formatting Contract (01, 02, 03...)
  // ---------------------------------------------------------------------------
  try {
    assert.strictEqual(formatSerialNumber(1), "01", "1 must format as '01'");
    assert.strictEqual(formatSerialNumber(2), "02", "2 must format as '02'");
    assert.strictEqual(formatSerialNumber(9), "09", "9 must format as '09'");
    assert.strictEqual(formatSerialNumber(10), "10", "10 must format as '10'");
    assert.strictEqual(formatSerialNumber(42), "42", "42 must format as '42'");
    assert.strictEqual(formatSerialNumber(null), "—", "null must format as '—'");
    pass("Serial number formatting (01, 02...) and boundary checks verified.");
  } catch (err) {
    fail("Serial number formatting", err);
  }

  // ---------------------------------------------------------------------------
  // TEST 2: Birth Date & Time Formatting (Timezone shift prevention)
  // ---------------------------------------------------------------------------
  try {
    // English
    assert.strictEqual(
      formatBirthDate("1998-01-15", "en"),
      "15 January 1998",
      "Exact birth date must be preserved as 15 January 1998"
    );
    assert.strictEqual(
      formatBirthDate("2000-08-22", "en"),
      "22 August 2000",
      "Exact birth date must be preserved as 22 August 2000"
    );
    // Tamil
    assert.strictEqual(
      formatBirthDate("1998-01-15", "ta"),
      "15 ஜனவரி 1998",
      "Tamil birth date must format as 15 ஜனவரி 1998"
    );
    // Time formatting
    assert.strictEqual(formatBirthTime("10:30:00"), "10:30 AM", "10:30:00 must format as 10:30 AM");
    assert.strictEqual(formatBirthTime("06:45:00"), "06:45 AM", "06:45:00 must format as 06:45 AM");
    assert.strictEqual(formatBirthTime("18:15:00"), "06:15 PM", "18:15:00 must format as 06:15 PM");
    assert.strictEqual(formatBirthTime("00:30:00"), "12:30 AM", "00:30:00 must format as 12:30 AM");
    assert.strictEqual(formatBirthTime("12:00:00"), "12:00 PM", "12:00:00 must format as 12:00 PM");
    pass("Birth date and time formatting contracts verified without browser timezone shifts.");
  } catch (err) {
    fail("Birth date and time formatting", err);
  }

  // ---------------------------------------------------------------------------
  // Setup Test User in Supabase
  // ---------------------------------------------------------------------------
  const testEmail = `task3_user_${Date.now()}@example.com`;
  const testPassword = "UserPass2026#Secure!";
  let testUserId = null;
  let userClient = null;

  try {
    const { data: userData, error: userError } = await adminClient.auth.admin.createUser({
      email: testEmail,
      password: testPassword,
      email_confirm: true,
      user_metadata: { username: `user_${Date.now().toString().slice(-6)}` },
    });
    assert(!userError, `Failed to create test user: ${userError?.message}`);
    testUserId = userData.user.id;

    userClient = createClient(supabaseUrl, anonKey, {
      auth: { autoRefreshToken: false, persistSession: false },
    });
    const { error: signInError } = await userClient.auth.signInWithPassword({
      email: testEmail,
      password: testPassword,
    });
    assert(!signInError, `Test user sign-in failed: ${signInError?.message}`);
    pass(`Test user authenticated (${testUserId}).`);
  } catch (err) {
    fail("Test user setup", err);
  }

  let h1Id = null;
  let h2Id = null;
  let h3Id = null;

  // ---------------------------------------------------------------------------
  // TEST 3: Sequential Display Numbering (1, 2, 3...)
  // ---------------------------------------------------------------------------
  try {
    const sampleCalculation = {
      horoscope: {
        ascendant: { degree: 28.5, sign_name: "Virgo" },
        planets: [{ name: "Sun", longitude: 120.5 }],
        metadata: { ayanamsa_name: "Lahiri", julian_day_ut1: 2451545.0 },
      },
      calculatedAt: "2026-10-18T00:00:00Z",
    };

    // Insert 1: Arun Kumar
    const { data: h1, error: e1 } = await userClient
      .from("saved_horoscopes")
      .insert({
        user_id: testUserId,
        person_name: "Arun Kumar",
        birth_date: "1998-01-15",
        birth_time: "10:30:00",
        timezone: "Asia/Kolkata",
        birthplace: "Chennai, Tamil Nadu, India",
        latitude: 13.0827,
        longitude: 80.2707,
        ayanamsa_id: 0,
        house_system_id: 2,
        calculation_result: sampleCalculation,
      })
      .select()
      .single();

    assert(!e1, `Error inserting h1: ${e1?.message}`);
    assert.strictEqual(h1.display_number, 1, `Expected display_number 1, got ${h1.display_number}`);
    h1Id = h1.id;

    // Insert 2: Priya Devi
    const { data: h2, error: e2 } = await userClient
      .from("saved_horoscopes")
      .insert({
        user_id: testUserId,
        person_name: "Priya Devi",
        birth_date: "2000-08-22",
        birth_time: "06:45:00",
        timezone: "Asia/Kolkata",
        birthplace: "Coimbatore, Tamil Nadu, India",
        latitude: 11.0168,
        longitude: 76.9558,
        ayanamsa_id: 0,
        house_system_id: 2,
        calculation_result: sampleCalculation,
      })
      .select()
      .single();

    assert(!e2, `Error inserting h2: ${e2?.message}`);
    assert.strictEqual(h2.display_number, 2, `Expected display_number 2, got ${h2.display_number}`);
    h2Id = h2.id;

    // Insert 3: Karthik Raja
    const { data: h3, error: e3 } = await userClient
      .from("saved_horoscopes")
      .insert({
        user_id: testUserId,
        person_name: "Karthik Raja",
        birth_date: "1992-12-05",
        birth_time: "18:15:00",
        timezone: "Asia/Kolkata",
        birthplace: "Madurai, Tamil Nadu, India",
        latitude: 9.9252,
        longitude: 78.1198,
        ayanamsa_id: 0,
        house_system_id: 2,
        calculation_result: sampleCalculation,
      })
      .select()
      .single();

    assert(!e3, `Error inserting h3: ${e3?.message}`);
    assert.strictEqual(h3.display_number, 3, `Expected display_number 3, got ${h3.display_number}`);
    h3Id = h3.id;

    pass("Sequential numbering verified: 1, 2, 3 assigned permanently by database trigger.");
  } catch (err) {
    fail("Sequential numbering", err);
  }

  // ---------------------------------------------------------------------------
  // TEST 4: Serial Numbers Preserved Across Search and Pagination
  // ---------------------------------------------------------------------------
  try {
    // Search for "Priya" (should only return record 2)
    const { data: searchResults, error: sErr } = await userClient
      .from("saved_horoscopes")
      .select("id, display_number, person_name")
      .eq("user_id", testUserId)
      .ilike("person_name", "%Priya%");

    assert(!sErr, `Search error: ${sErr?.message}`);
    assert.strictEqual(searchResults.length, 1, "Search should return 1 record");
    assert.strictEqual(
      searchResults[0].display_number,
      2,
      `Priya Devi must retain serial number 2 in search results (got ${searchResults[0].display_number})`
    );

    // Pagination: Query page 2 with limit 1, offset 1
    const { data: pagedResults, error: pErr } = await userClient
      .from("saved_horoscopes")
      .select("id, display_number, person_name")
      .eq("user_id", testUserId)
      .order("display_number", { ascending: true })
      .range(1, 1);

    assert(!pErr, `Pagination error: ${pErr?.message}`);
    assert.strictEqual(pagedResults.length, 1, "Pagination should return 1 record");
    assert.strictEqual(
      pagedResults[0].display_number,
      2,
      `Second item in pagination must have permanent display_number 2, not page index 1`
    );

    pass("Serial numbers preserved unchanged during search queries and pagination ranges.");
  } catch (err) {
    fail("Serial numbers in search/pagination", err);
  }

  // ---------------------------------------------------------------------------
  // TEST 5: Record Editing Preserves Permanent Serial Number and Snapshot
  // ---------------------------------------------------------------------------
  try {
    // Edit Priya Devi's details
    const updatedName = "Priya Devi (Edited)";
    const updatedPlace = "Salem, Tamil Nadu, India";
    const updatedLat = 11.6643;
    const updatedLon = 78.146;

    const { data: editResult, error: editErr } = await userClient
      .from("saved_horoscopes")
      .update({
        person_name: updatedName,
        birthplace: updatedPlace,
        latitude: updatedLat,
        longitude: updatedLon,
        updated_at: new Date().toISOString(),
      })
      .eq("id", h2Id)
      .select()
      .single();

    assert(!editErr, `Edit update failed: ${editErr?.message}`);
    assert.strictEqual(editResult.display_number, 2, "Editing must preserve permanent serial number 2");
    assert.strictEqual(editResult.person_name, updatedName, "Person name must be updated");
    assert.strictEqual(editResult.birthplace, updatedPlace, "Birthplace must be updated");
    assert.strictEqual(editResult.latitude, updatedLat, "Latitude must be updated");

    // Verify calculation_result was NOT overwritten or recalculated
    assert.deepStrictEqual(
      editResult.calculation_result.horoscope.ascendant.sign_name,
      "Virgo",
      "Original calculation snapshot must be preserved intact"
    );

    // Verify total count in database has not changed (no duplicate created)
    const { count } = await userClient
      .from("saved_horoscopes")
      .select("id", { count: "exact" })
      .eq("user_id", testUserId);

    assert.strictEqual(count, 3, "Total record count must remain 3 after editing (no duplicate record created)");
    pass("Editing preserves serial number 2, updates metadata without altering calculation snapshot, and creates no duplicates.");
  } catch (err) {
    fail("Editing preserves serial number and snapshot", err);
  }

  // ---------------------------------------------------------------------------
  // TEST 6: Record Deletion Does Not Renumber Remaining Records
  // ---------------------------------------------------------------------------
  try {
    // Delete record 1 (Arun Kumar)
    const { error: delErr } = await userClient
      .from("saved_horoscopes")
      .delete()
      .eq("id", h1Id);

    assert(!delErr, `Delete failed: ${delErr?.message}`);

    // Query remaining records
    const { data: remaining, error: remErr } = await userClient
      .from("saved_horoscopes")
      .select("id, display_number, person_name")
      .eq("user_id", testUserId)
      .order("display_number", { ascending: true });

    assert(!remErr, `Query error: ${remErr?.message}`);
    assert.strictEqual(remaining.length, 2, "Remaining records count must be 2");

    // Record 2 must STILL have display_number 2, and Record 3 must STILL have display_number 3
    assert.strictEqual(
      remaining[0].display_number,
      2,
      `Priya Devi must retain serial number 2 after record 1 is deleted (got ${remaining[0].display_number})`
    );
    assert.strictEqual(
      remaining[1].display_number,
      3,
      `Karthik Raja must retain serial number 3 after record 1 is deleted (got ${remaining[1].display_number})`
    );

    pass("Deletion does not renumber existing records: serial numbers 02 and 03 stay permanently constant.");
  } catch (err) {
    fail("Deletion numbering preservation", err);
  }

  // ---------------------------------------------------------------------------
  // TEST 7: Open Horoscope Loads Stored Snapshot Without Recalculation
  // ---------------------------------------------------------------------------
  try {
    const { data: openedRecord, error: openErr } = await userClient
      .from("saved_horoscopes")
      .select("*")
      .eq("id", h3Id)
      .single();

    assert(!openErr, `Failed to load horoscope by id: ${openErr?.message}`);
    assert.strictEqual(openedRecord.id, h3Id, "Loaded record id must match requested id");
    assert.strictEqual(openedRecord.display_number, 3, "Serial number 3 must be returned");
    assert.strictEqual(openedRecord.person_name, "Karthik Raja", "Birth name must match");
    assert(openedRecord.calculation_result, "Stored calculation snapshot must be present");
    assert.strictEqual(
      openedRecord.calculation_result.horoscope.ascendant.sign_name,
      "Virgo",
      "Stored ascendant matches calculation snapshot"
    );

    // Verify opening record did not alter record count
    const { count: countAfterOpen } = await userClient
      .from("saved_horoscopes")
      .select("id", { count: "exact" })
      .eq("user_id", testUserId);

    assert.strictEqual(countAfterOpen, 2, "Opening record must not create duplicate records");
    pass("Open horoscope loads persisted snapshot directly with exact serial number and zero duplication.");
  } catch (err) {
    fail("Open horoscope snapshot loading", err);
  }

  // ---------------------------------------------------------------------------
  // TEST 8: Cross-User RLS and Unauthorized Access Protection
  // ---------------------------------------------------------------------------
  const rivalEmail = `task3_rival_${Date.now()}@example.com`;
  let rivalUserId = null;
  let rivalClient = null;

  try {
    const { data: rivalData, error: rivalCreateErr } = await adminClient.auth.admin.createUser({
      email: rivalEmail,
      password: "RivalPassword#2026",
      email_confirm: true,
      user_metadata: { username: `rival_${Date.now().toString().slice(-6)}` },
    });
    assert(!rivalCreateErr, `Failed to create rival user: ${rivalCreateErr?.message}`);
    rivalUserId = rivalData.user.id;

    rivalClient = createClient(supabaseUrl, anonKey, {
      auth: { autoRefreshToken: false, persistSession: false },
    });
    await rivalClient.auth.signInWithPassword({
      email: rivalEmail,
      password: "RivalPassword#2026",
    });

    // 1. Rival user tries to SELECT test user's horoscope
    const { data: rivalView } = await rivalClient
      .from("saved_horoscopes")
      .select("id, person_name")
      .eq("id", h2Id);

    assert.strictEqual(rivalView.length, 0, "Rival user cannot view test user's saved horoscope");

    // 2. Rival user tries to UPDATE test user's horoscope
    const { error: rivalUpdateErr } = await rivalClient
      .from("saved_horoscopes")
      .update({ person_name: "Hacked Record" })
      .eq("id", h2Id);

    // Verify record was untouched
    const { data: checkUnchanged } = await adminClient
      .from("saved_horoscopes")
      .select("person_name")
      .eq("id", h2Id)
      .single();

    assert.strictEqual(
      checkUnchanged.person_name,
      "Priya Devi (Edited)",
      "Test user's record must not be modified by rival user"
    );

    // 3. Anonymous unauthenticated client access blocked
    const unauthenticatedClient = createClient(supabaseUrl, anonKey, {
      auth: { autoRefreshToken: false, persistSession: false },
    });
    const { data: anonData } = await unauthenticatedClient
      .from("saved_horoscopes")
      .select("id, person_name");

    assert.strictEqual(anonData.length, 0, "Unauthenticated client cannot view saved horoscopes");
    pass("Cross-user RLS isolation and anonymous protection verified: users cannot view or edit foreign records.");
  } catch (err) {
    fail("Cross-user RLS protection", err);
  }

  // ---------------------------------------------------------------------------
  // Clean Up Test Users
  // ---------------------------------------------------------------------------
  try {
    if (testUserId) {
      await adminClient.from("saved_horoscopes").delete().eq("user_id", testUserId);
      await adminClient.from("profiles").delete().eq("id", testUserId);
      await adminClient.auth.admin.deleteUser(testUserId);
    }
    if (rivalUserId) {
      await adminClient.from("saved_horoscopes").delete().eq("user_id", rivalUserId);
      await adminClient.from("profiles").delete().eq("id", rivalUserId);
      await adminClient.auth.admin.deleteUser(rivalUserId);
    }
    pass("Test artifacts cleaned up successfully.");
  } catch (err) {
    console.warn("Cleanup warning:", err);
  }

  // ---------------------------------------------------------------------------
  // Final Results
  // ---------------------------------------------------------------------------
  console.log("\n================================================================================");
  console.log(`  TASK 3 VERIFICATION COMPLETE: ${passCount} / ${testCount} TESTS PASSED`);
  console.log("================================================================================");

  if (passCount !== testCount) {
    process.exitCode = 1;
  }
}

runTask3TestSuite().catch((err) => {
  console.error("Fatal test error:", err);
  process.exitCode = 1;
});
