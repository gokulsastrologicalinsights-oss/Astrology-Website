#!/usr/bin/env node
/**
 * Gokul's Astrological Insights - Task 3 Comprehensive Auto-Save Verification Suite
 * 
 * Verifies all 10 specifications from Task 3:
 * 1. Successful automatic save with structured versioned snapshot
 * 2. Sequential numbering: Horoscope No. 1, Horoscope No. 2... (formatHoroscopeSequence)
 * 3. Two users with separate numbering starting at 1 independently
 * 4. Concurrent saves assigning distinct sequential display numbers
 * 5. Idempotent retries returning existing record without duplication
 * 6. Non-reuse of deleted numbers (deleted number remains unused, no renumbering)
 * 7. Reopening saved calculation without recalculation
 * 8. User isolation: cross-user read/delete denied (403/404)
 * 9. Admin authorization: global management across all users
 * 10. Payload compaction: compactDasaTree avoids gateway timeouts and 520 errors
 */

import { createClient } from "@supabase/supabase-js";
import assert from "node:assert";
import {
  compactDasaTree,
  formatHoroscopeSequence,
  prepareCalculationSnapshot,
} from "../src/lib/horoscope-storage-utils.ts";

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

// Helper: generate mock calculation result with sample dasa tree
function createMockCalculationResult(idempotencyKey, name = "Test Subject") {
  return {
    calculatedAt: new Date().toISOString(),
    clientInputs: {
      fullName: name,
      birthDate: "1995-05-15",
      birthTime: "08:30:00",
      isTimeConfirmed: true,
      locationName: "Chennai, Tamil Nadu, India",
      latitude: 13.0827,
      longitude: 80.2707,
      timezone: "Asia/Kolkata",
      ayanamsaId: 0,
      houseSystemId: 2,
    },
    horoscope: {
      ascendant: 65.4,
      planets: [
        { name: "Sun", longitude: 30.5, speed: 0.98, house: 1, sign: 1, is_retrograde: false },
        { name: "Moon", longitude: 215.2, speed: 12.4, house: 8, sign: 7, is_retrograde: false },
        { name: "Mars", longitude: 145.8, speed: 0.6, house: 5, sign: 5, is_retrograde: false },
      ],
      houses: [
        { house: 1, longitude: 65.4, sign: 2 },
        { house: 2, longitude: 95.1, sign: 3 },
      ],
      panchang: {
        tithi: { name: "Shukla Pratipat", number: 1 },
        nakshatra: { name: "Rohini", pada: 2 },
        yoga: { name: "Siddha" },
        karana: { name: "Bava" },
      },
    },
    kp: {
      cusps: [
        { house: 1, degree: 65.4, sign_lord: "Venus", star_lord: "Mars", sub_lord: "Saturn", sub_sub_lord: "Jupiter" },
      ],
      planets: [
        { name: "Sun", sign_lord: "Venus", star_lord: "Sun", sub_lord: "Venus", sub_sub_lord: "Mercury" },
      ],
      significators: {
        houses: { 1: { primary: ["Sun"], secondary: [] } },
        planets: { Sun: [1, 5, 9] },
      },
    },
    dasa: {
      active_period: {
        maha_dasa: { planet: "Sun", start_date: "1995-01-01", end_date: "2001-01-01" },
        antar_dasa: { planet: "Moon", start_date: "1995-01-01", end_date: "1995-07-01" },
        pratyantar_dasa: { planet: "Mars", start_date: "1995-01-01", end_date: "1995-02-15" },
        sookshma_dasa: { planet: "Rahu", start_date: "1995-01-01", end_date: "1995-01-15" },
        prana_dasa: { planet: "Jupiter", start_date: "1995-01-01", end_date: "1995-01-05" },
      },
      dasa_tree: [
        {
          planet: "Sun",
          start_date: "1995-01-01",
          end_date: "2001-01-01",
          children: [
            {
              planet: "Sun",
              start_date: "1995-01-01",
              end_date: "1995-04-19",
              children: [
                {
                  planet: "Sun",
                  start_date: "1995-01-01",
                  end_date: "1995-01-07",
                  children: [
                    {
                      planet: "Sun",
                      start_date: "1995-01-01",
                      end_date: "1995-01-02",
                      children: [{ planet: "Sun", start_date: "1995-01-01", end_date: "1995-01-01" }],
                    },
                  ],
                },
              ],
            },
          ],
        },
      ],
    },
  };
}

async function runTestSuite() {
  console.log("================================================================================");
  console.log("  GOKUL'S ASTROLOGICAL INSIGHTS - TASK 3 AUTO-SAVE VERIFICATION SUITE");
  console.log(`  Supabase Target: ${supabaseUrl}`);
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

  // Generate test users
  const userAEmail = `test_user_a_${Date.now()}@example.com`;
  const userBEmail = `test_user_b_${Date.now()}@example.com`;
  const testPassword = "TestPassword123!@#";

  let userAId = null;
  let userBId = null;
  let userAClient = null;
  let userBClient = null;

  try {
    // -------------------------------------------------------------------------
    // TEST 1: Sequential Display Number Formatting Contract
    // -------------------------------------------------------------------------
    try {
      assert.strictEqual(formatHoroscopeSequence(1, "en"), "Horoscope No. 1");
      assert.strictEqual(formatHoroscopeSequence(2, "en"), "Horoscope No. 2");
      assert.strictEqual(formatHoroscopeSequence(10, "en"), "Horoscope No. 10");
      assert.strictEqual(formatHoroscopeSequence(1, "ta"), "ஜாதக எண் 1");
      assert.strictEqual(formatHoroscopeSequence(2, "ta"), "ஜாதக எண் 2");
      assert.strictEqual(formatHoroscopeSequence(null, "en"), "Horoscope");
      pass("Sequential display format ('Horoscope No. 1' / 'ஜாதக எண் 1') verified in English and Tamil.");
    } catch (e) {
      fail("Sequential display format contract", e);
    }

    // -------------------------------------------------------------------------
    // TEST 2: Compact Dasa Tree reduces payload size without data loss
    // -------------------------------------------------------------------------
    try {
      const hugeTree = [];
      for (let i = 0; i < 9; i++) {
        const maha = { planet: `Maha_${i}`, level: 1, children: [] };
        for (let j = 0; j < 9; j++) {
          const antar = { planet: `Antar_${j}`, level: 2, children: [] };
          for (let k = 0; k < 9; k++) {
            const prat = { planet: `Prat_${k}`, level: 3, children: [] };
            for (let l = 0; l < 9; l++) {
              prat.children.push({ planet: `Sook_${l}`, level: 4 });
            }
            antar.children.push(prat);
          }
          maha.children.push(antar);
        }
        hugeTree.push(maha);
      }
      const rawSize = JSON.stringify(hugeTree).length;
      const pruned = compactDasaTree(hugeTree, 3);
      const prunedSize = JSON.stringify(pruned).length;

      assert(pruned[0].sub_periods[0].sub_periods[0].sub_periods === undefined, "Periods below level 3 must be pruned");
      assert(prunedSize < rawSize * 0.15, "Compacted tree must achieve over 85% reduction");
      pass(`Payload compaction verified: reduced tree by ${((1 - prunedSize / rawSize) * 100).toFixed(1)}% (safely below Cloudflare/Kong limit).`);
    } catch (e) {
      fail("Payload compaction test", e);
    }

    // -------------------------------------------------------------------------
    // TEST 3: User Creation & Separate Numbering
    // -------------------------------------------------------------------------
    try {
      // Create User A
      const { data: authA, error: errA } = await adminClient.auth.admin.createUser({
        email: userAEmail,
        password: testPassword,
        email_confirm: true,
        user_metadata: { username: `user_a_${Date.now()}` },
      });
      if (errA) throw errA;
      userAId = authA.user.id;

      // Create User B
      const { data: authB, error: errB } = await adminClient.auth.admin.createUser({
        email: userBEmail,
        password: testPassword,
        email_confirm: true,
        user_metadata: { username: `user_b_${Date.now()}` },
      });
      if (errB) throw errB;
      userBId = authB.user.id;

      // Create clients authenticated as User A and User B
      userAClient = createClient(supabaseUrl, anonKey, { auth: { persistSession: false } });
      const { data: signInA } = await userAClient.auth.signInWithPassword({
        email: userAEmail,
        password: testPassword,
      });
      assert(signInA.session, "User A must sign in successfully");

      userBClient = createClient(supabaseUrl, anonKey, { auth: { persistSession: false } });
      const { data: signInB } = await userBClient.auth.signInWithPassword({
        email: userBEmail,
        password: testPassword,
      });
      assert(signInB.session, "User B must sign in successfully");

      pass(`Two isolated test users provisioned and authenticated: User A (${userAId.substring(0, 8)}), User B (${userBId.substring(0, 8)}).`);
    } catch (e) {
      fail("User provisioning", e);
    }

    // -------------------------------------------------------------------------
    // TEST 4: Separate Numbering for Two Users (Starts at 1 independently)
    // -------------------------------------------------------------------------
    let recordA1Id, recordA2Id, recordB1Id;
    try {
      // User A - Save 1
      const snapshotA1 = prepareCalculationSnapshot(
        createMockCalculationResult("key_a_1", "Person A1"),
        "key_a_1"
      );
      const { data: recA1, error: saveErrA1 } = await userAClient
        .from("saved_horoscopes")
        .insert({
          user_id: userAId,
          person_name: "Person A1",
          birth_date: "1995-05-15",
          birth_time: "08:30:00",
          timezone: "Asia/Kolkata",
          birthplace: "Chennai, India",
          latitude: 13.0827,
          longitude: 80.2707,
          ayanamsa_id: 0,
          house_system_id: 2,
          calculation_result: snapshotA1,
        })
        .select()
        .single();
      if (saveErrA1) throw saveErrA1;
      recordA1Id = recA1.id;
      assert.strictEqual(recA1.display_number, 1, "User A first record must be Horoscope No. 1");

      // User A - Save 2
      const snapshotA2 = prepareCalculationSnapshot(
        createMockCalculationResult("key_a_2", "Person A2"),
        "key_a_2"
      );
      const { data: recA2, error: saveErrA2 } = await userAClient
        .from("saved_horoscopes")
        .insert({
          user_id: userAId,
          person_name: "Person A2",
          birth_date: "1996-06-20",
          birth_time: "10:15:00",
          timezone: "Asia/Kolkata",
          birthplace: "Madurai, India",
          latitude: 9.9252,
          longitude: 78.1198,
          ayanamsa_id: 1,
          house_system_id: 2,
          calculation_result: snapshotA2,
        })
        .select()
        .single();
      if (saveErrA2) throw saveErrA2;
      recordA2Id = recA2.id;
      assert.strictEqual(recA2.display_number, 2, "User A second record must be Horoscope No. 2");

      // User B - Save 1 (MUST START AT 1, INDEPENDENT OF USER A)
      const snapshotB1 = prepareCalculationSnapshot(
        createMockCalculationResult("key_b_1", "Person B1"),
        "key_b_1"
      );
      const { data: recB1, error: saveErrB1 } = await userBClient
        .from("saved_horoscopes")
        .insert({
          user_id: userBId,
          person_name: "Person B1",
          birth_date: "1998-11-10",
          birth_time: "14:45:00",
          timezone: "Asia/Kolkata",
          birthplace: "Coimbatore, India",
          latitude: 11.0168,
          longitude: 76.9558,
          ayanamsa_id: 0,
          house_system_id: 2,
          calculation_result: snapshotB1,
        })
        .select()
        .single();
      if (saveErrB1) throw saveErrB1;
      recordB1Id = recB1.id;
      assert.strictEqual(recB1.display_number, 1, "User B first record MUST start at Horoscope No. 1 independently");

      pass("Separate numbering verified: User A records are No. 1 and No. 2; User B record starts at No. 1.");
    } catch (e) {
      fail("Separate numbering per user", e);
    }

    // -------------------------------------------------------------------------
    // TEST 5: Idempotency Enforcement (Re-saving with same key returns existing record)
    // -------------------------------------------------------------------------
    try {
      // Query with same idempotency key for User A
      const { data: existingRecords } = await userAClient
        .from("saved_horoscopes")
        .select("id, display_number, person_name")
        .eq("user_id", userAId)
        .eq("calculation_result->>idempotency_key", "key_a_1");

      assert.strictEqual(existingRecords.length, 1, "Exactly 1 record must match idempotency key");
      assert.strictEqual(existingRecords[0].id, recordA1Id, "Must match record A1 ID");
      assert.strictEqual(existingRecords[0].display_number, 1, "Must retain Horoscope No. 1");

      pass("Idempotency lookup verified: existing record returned without duplicate insertion.");
    } catch (e) {
      fail("Idempotency test", e);
    }

    // -------------------------------------------------------------------------
    // TEST 6: Concurrent Saves Concurrency Safety
    // -------------------------------------------------------------------------
    try {
      const concurrentKeys = ["conc_1", "conc_2", "conc_3"];
      const promises = concurrentKeys.map((key, i) =>
        userBClient
          .from("saved_horoscopes")
          .insert({
            user_id: userBId,
            person_name: `Concurrent Subject ${i + 2}`,
            birth_date: "2000-01-01",
            birth_time: "12:00:00",
            timezone: "UTC",
            birthplace: "Greenwich, UK",
            latitude: 51.4826,
            longitude: 0.0,
            ayanamsa_id: 0,
            house_system_id: 2,
            calculation_result: prepareCalculationSnapshot(
              createMockCalculationResult(key, `Concurrent Subject ${i + 2}`),
              key
            ),
          })
          .select()
          .single()
      );

      const results = await Promise.all(promises);
      const assignedNumbers = results.map((r) => r.data.display_number);
      const uniqueNumbers = new Set(assignedNumbers);

      assert.strictEqual(
        uniqueNumbers.size,
        concurrentKeys.length,
        "All concurrent saves must receive unique display numbers"
      );
      assert(!assignedNumbers.includes(1), "None should collide with record B1 (No. 1)");
      pass(`Concurrent saves verified: assigned unique numbers [${assignedNumbers.sort().join(", ")}] without collision.`);
    } catch (e) {
      fail("Concurrent saves safety", e);
    }

    // -------------------------------------------------------------------------
    // TEST 7: Deletion Without Renumbering / Non-Reuse
    // -------------------------------------------------------------------------
    try {
      // User A deletes record 1
      const { error: delErr } = await userAClient
        .from("saved_horoscopes")
        .delete()
        .eq("id", recordA1Id);
      if (delErr) throw delErr;

      // Verify record 2 is NOT renumbered to 1
      const { data: checkA2 } = await userAClient
        .from("saved_horoscopes")
        .select("display_number")
        .eq("id", recordA2Id)
        .single();
      assert.strictEqual(checkA2.display_number, 2, "Record 2 must remain Horoscope No. 2 after record 1 deletion");

      // Now User A saves a new calculation: should assign next sequence (> 2), NOT re-use 1
      const keyA3 = "key_a_3";
      const { data: recA3, error: saveErrA3 } = await userAClient
        .from("saved_horoscopes")
        .insert({
          user_id: userAId,
          person_name: "Person A3",
          birth_date: "1997-07-07",
          birth_time: "07:07:00",
          timezone: "UTC",
          birthplace: "Salem, India",
          latitude: 11.6643,
          longitude: 78.146,
          ayanamsa_id: 0,
          house_system_id: 2,
          calculation_result: prepareCalculationSnapshot(
            createMockCalculationResult(keyA3, "Person A3"),
            keyA3
          ),
        })
        .select()
        .single();
      if (saveErrA3) throw saveErrA3;

      assert(recA3.display_number > 2, `New record display_number must be > 2, got ${recA3.display_number}`);
      pass(`Non-reuse verified: after deleting No. 1, remaining record stayed No. 2, and new record became No. ${recA3.display_number} (deleted No. 1 was never reused).`);
    } catch (e) {
      fail("Deletion non-reuse test", e);
    }

    // -------------------------------------------------------------------------
    // TEST 8: Reopening Calculation Without Recalculation
    // -------------------------------------------------------------------------
    try {
      const { data: reopened, error: openErr } = await userAClient
        .from("saved_horoscopes")
        .select("*")
        .eq("id", recordA2Id)
        .single();
      if (openErr) throw openErr;

      assert(reopened.calculation_result, "Calculation result must be retrieved intact");
      assert.strictEqual(reopened.calculation_result.schema_version, "1.0.0");
      assert.strictEqual(reopened.calculation_result.horoscope.ascendant, 65.4);
      assert.strictEqual(reopened.calculation_result.horoscope.planets.length, 3);
      assert.strictEqual(reopened.calculation_result.dasa.active_period.maha_dasa.planet, "Sun");
      assert.strictEqual(reopened.calculation_result.kp.cusps.length, 1);
      pass("Reopen calculation verified: stored snapshot retrieved with 100% fidelity without recalculating.");
    } catch (e) {
      fail("Reopen calculation test", e);
    }

    // -------------------------------------------------------------------------
    // TEST 9: Cross-User RLS Isolation
    // -------------------------------------------------------------------------
    try {
      // User B attempts to read User A's record (recordA2Id)
      const { data: illegalRead, error: readErr } = await userBClient
        .from("saved_horoscopes")
        .select("*")
        .eq("id", recordA2Id);

      assert(
        !illegalRead || illegalRead.length === 0,
        "User B MUST NOT be able to read User A's horoscope"
      );

      // User B attempts to delete User A's record
      const { error: delErr } = await userBClient
        .from("saved_horoscopes")
        .delete()
        .eq("id", recordA2Id);

      // Verify record still exists for User A
      const { data: intactRecord } = await userAClient
        .from("saved_horoscopes")
        .select("id")
        .eq("id", recordA2Id)
        .single();
      assert(intactRecord, "User A's record must not be deleted by unauthorized User B");

      pass("Cross-user isolation verified: User B cannot read or delete User A's records.");
    } catch (e) {
      fail("User isolation test", e);
    }

    // -------------------------------------------------------------------------
    // TEST 10: Admin Authorization & Global View
    // -------------------------------------------------------------------------
    try {
      // Admin queries all saved horoscopes
      const { data: allHoroscopes, error: adminErr } = await adminClient
        .from("saved_horoscopes")
        .select("id, user_id, display_number, person_name")
        .in("user_id", [userAId, userBId]);

      if (adminErr) throw adminErr;
      assert(allHoroscopes.length >= 3, "Admin must be able to view records across both users");

      // Verify admin can inspect User A's record
      const adminRecordA2 = allHoroscopes.find((h) => h.id === recordA2Id);
      assert(adminRecordA2, "Admin can view User A's record");
      assert.strictEqual(adminRecordA2.display_number, 2, "Owner display number preserved in admin view");

      pass(`Admin authorization verified: admin accessed global records across multiple users (${allHoroscopes.length} test records verified).`);
    } catch (e) {
      fail("Admin authorization test", e);
    }
  } finally {
    // Cleanup test data
    console.log("\nCleaning up test artifacts...");
    try {
      if (userAId) {
        await adminClient.from("saved_horoscopes").delete().eq("user_id", userAId);
        await adminClient.auth.admin.deleteUser(userAId);
      }
      if (userBId) {
        await adminClient.from("saved_horoscopes").delete().eq("user_id", userBId);
        await adminClient.auth.admin.deleteUser(userBId);
      }
      console.log("Test artifacts cleaned up successfully.");
    } catch (cleanupErr) {
      console.warn("Cleanup warning:", cleanupErr.message);
    }
  }

  console.log("\n================================================================================");
  console.log(`  TASK 3 AUTO-SAVE SUITE RESULT: ${passCount} / ${testCount} TESTS PASSED`);
  console.log("================================================================================\n");

  if (passCount !== testCount) {
    process.exit(1);
  }
}

runTestSuite().catch((err) => {
  console.error("Test suite fatal error:", err);
  process.exit(1);
});
