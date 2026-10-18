#!/usr/bin/env node
/**
 * Gokul's Astrological Insights - Comprehensive Live Supabase Verification Suite
 * Tests against live Supabase project (pcwiopxewlxhwvddpndq):
 * 1. Admin Bootstrap state & initial password check
 * 2. Role enforcement & must_change_password flag
 * 3. Normal user registration & default 'user' role
 * 4. Client-side privilege escalation prevention (RLS / trigger defense)
 * 5. Sequential display_order transaction safety in saved_horoscopes
 * 6. Cross-user RLS data isolation
 * 7. Clean teardown of test artifacts
 */

import { createClient } from "@supabase/supabase-js";
import assert from "node:assert";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
const adminUsername = process.env.ADMIN_USERNAME || "gokul_admin";
const adminEmail = process.env.ADMIN_EMAIL || "admin@gokul-astrology.local";
const adminPassword = process.env.ADMIN_INITIAL_PASSWORD || "ChangeMeOnFirstLogin#2026";

if (!supabaseUrl || !anonKey || !serviceRoleKey) {
  console.error("Missing required Supabase environment variables in .env.local");
  process.exit(1);
}

const adminClient = createClient(supabaseUrl, serviceRoleKey, {
  auth: { autoRefreshToken: false, persistSession: false },
});

const anonClient = createClient(supabaseUrl, anonKey, {
  auth: { autoRefreshToken: false, persistSession: false },
});

async function runLiveVerification() {
  console.log("================================================================================");
  console.log("  GOKUL'S ASTROLOGICAL INSIGHTS - LIVE SUPABASE VERIFICATION SUITE");
  console.log(`  Target Project: ${supabaseUrl}`);
  console.log("================================================================================\n");

  let testPassed = 0;
  let testTotal = 0;

  function pass(title) {
    testTotal++;
    testPassed++;
    console.log(`[PASS ${testTotal}] ${title}`);
  }

  function fail(title, err) {
    testTotal++;
    console.error(`[FAIL ${testTotal}] ${title}:`, err);
  }

  // TEST 1: Admin Account Bootstrap Verification
  try {
    const normalizedAdminUsername = adminUsername.toLowerCase().replace(/\s+/g, "_");
    const { data: adminProfiles, error } = await adminClient
      .from("profiles")
      .select("id, username, display_name, role, must_change_password")
      .or(`username.ilike.${normalizedAdminUsername},display_name.ilike.${adminUsername}`);

    assert(!error, `Failed to query admin profile: ${error?.message}`);
    assert(adminProfiles && adminProfiles.length === 1, `Expected 1 admin profile, found ${adminProfiles?.length}`);
    const admin = adminProfiles[0];
    assert.strictEqual(admin.role, "admin", "Admin role must be 'admin'");
    pass(`Admin account '${adminUsername}' verified with role='admin'.`);
  } catch (err) {
    fail("Admin account verification", err);
  }

  // TEST 2: Admin Authentication with Initial Password
  try {
    const { data: authData, error: authError } = await anonClient.auth.signInWithPassword({
      email: adminEmail,
      password: adminPassword,
    });
    assert(!authError, `Failed to authenticate admin: ${authError?.message}`);
    assert(authData.user, "Admin sign-in returned no user");
    assert.strictEqual(authData.user.email, adminEmail, "Admin user email mismatch");
    pass(`Admin authenticated successfully using configured credentials via Supabase Auth.`);
  } catch (err) {
    fail("Admin authentication", err);
  }

  // TEST 3: Normal User Registration & Role Enforcement
  const testEmail = `testuser_${Date.now()}@example.com`;
  const testUsername = `user_${Date.now().toString().slice(-6)}`;
  const testPassword = "UserPass2026#Secure!";
  let testUserId = null;
  let userClient = null;

  try {
    // Create pre-confirmed user via admin client to test normal user session & permissions
    const { data: regData, error: regError } = await adminClient.auth.admin.createUser({
      email: testEmail,
      password: testPassword,
      email_confirm: true,
      user_metadata: {
        username: testUsername,
        display_name: "Test User",
      },
    });

    assert(!regError, `User sign-up failed: ${regError?.message}`);
    assert(regData.user, "No user returned from sign up");
    testUserId = regData.user.id;

    // Wait a brief moment for database trigger to create profile
    await new Promise((r) => setTimeout(r, 600));

    // Verify profile in database
    const { data: profile, error: profError } = await adminClient
      .from("profiles")
      .select("id, username, role, must_change_password")
      .eq("id", testUserId)
      .single();

    assert(!profError, `Profile query failed: ${profError?.message}`);
    assert.strictEqual(profile.role, "user", "Normal user must be assigned role='user'");
    assert.strictEqual(profile.must_change_password, false, "Normal user must_change_password must be false");
    pass(`Normal user registration succeeded: '${testUsername}' created with default role='user'.`);

    // Create authenticated client for this test user
    userClient = createClient(supabaseUrl, anonKey, {
      auth: { autoRefreshToken: false, persistSession: false },
    });
    const { error: sessionError } = await userClient.auth.signInWithPassword({
      email: testEmail,
      password: testPassword,
    });
    assert(!sessionError, `Test user sign-in failed: ${sessionError?.message}`);
    pass(`Normal user signed in and obtained authenticated session.`);
  } catch (err) {
    fail("Normal user registration & sign-in", err);
  }

  // TEST 4: Client Privilege Escalation Defense (RLS / Trigger)
  try {
    // Attempt to update own role to 'admin' using normal user's client
    const { error: tamperError } = await userClient
      .from("profiles")
      .update({ role: "admin" })
      .eq("id", testUserId);

    assert(tamperError, "Expected role-tampering update to fail, but it succeeded!");
    pass(`Privilege escalation prevented: Normal user cannot elevate role to 'admin' (${tamperError.message}).`);
  } catch (err) {
    fail("Privilege escalation defense", err);
  }

  // TEST 5: Saved Horoscopes Sequential Numbering & Isolation
  try {
    // Insert horoscope 1 as test user
    const sampleHoroscope1 = {
      user_id: testUserId,
      person_name: "Test Person 1",
      birth_date: "1995-05-15",
      birth_time: "14:30:00",
      birthplace: "Chennai, Tamil Nadu, India",
      latitude: 13.0827,
      longitude: 80.2707,
      timezone: "Asia/Kolkata",
      ayanamsa_id: 0,
      house_system_id: 2,
      calculation_result: { ascendant: "Virgo", moon_sign: "Scorpio" },
    };

    const { data: h1, error: h1Error } = await userClient
      .from("saved_horoscopes")
      .insert(sampleHoroscope1)
      .select("id, display_number, person_name")
      .single();

    assert(!h1Error, `Failed to insert horoscope 1: ${h1Error?.message}`);
    assert.strictEqual(h1.display_number, 1, `Expected display_number 1, got ${h1.display_number}`);

    // Insert horoscope 2 as test user
    const sampleHoroscope2 = {
      ...sampleHoroscope1,
      person_name: "Test Person 2",
    };

    const { data: h2, error: h2Error } = await userClient
      .from("saved_horoscopes")
      .insert(sampleHoroscope2)
      .select("id, display_number, person_name")
      .single();

    assert(!h2Error, `Failed to insert horoscope 2: ${h2Error?.message}`);
    assert.strictEqual(h2.display_number, 2, `Expected display_number 2, got ${h2.display_number}`);
    pass(`Sequential numbering verified: First record display_number=1, second display_number=2.`);

    // TEST 6: Unauthenticated Access Blocked
    const unauthenticatedClient = createClient(supabaseUrl, anonKey, {
      auth: { autoRefreshToken: false, persistSession: false },
    });
    const { data: anonView, error: anonError } = await unauthenticatedClient
      .from("saved_horoscopes")
      .select("id, person_name");

    assert(!anonError, `Anon query returned error: ${anonError?.message}`);
    assert.strictEqual(anonView.length, 0, "Anonymous user should see 0 saved horoscopes due to RLS");
    pass(`RLS isolation verified: Unauthenticated visitors cannot view saved horoscopes.`);

    // TEST 7: Cross-User Tampering Blocked
    // Create second temporary user
    const rivalEmail = `rival_${Date.now()}@example.com`;
    const rivalUsername = `rival_${Date.now().toString().slice(-6)}`;
    const { data: rivalAuth, error: rivalCreateErr } = await adminClient.auth.admin.createUser({
      email: rivalEmail,
      password: "RivalPassword#2026",
      email_confirm: true,
      user_metadata: { username: rivalUsername },
    });
    assert(!rivalCreateErr, `Failed to create rival user: ${rivalCreateErr?.message}`);
    const rivalUserId = rivalAuth.user.id;

    const rivalClient = createClient(supabaseUrl, anonKey, {
      auth: { autoRefreshToken: false, persistSession: false },
    });
    await rivalClient.auth.signInWithPassword({
      email: rivalEmail,
      password: "RivalPassword#2026",
    });

    // Rival user tries to query test user's horoscopes
    const { data: rivalHoroscopes } = await rivalClient
      .from("saved_horoscopes")
      .select("id, person_name");

    assert.strictEqual(rivalHoroscopes.length, 0, "Rival user cannot see test user's horoscopes");

    // Rival user tries to delete test user's horoscope
    const { error: rivalDeleteError } = await rivalClient
      .from("saved_horoscopes")
      .delete()
      .eq("id", h1.id);

    // RLS policy denies delete of non-owned rows silently or with 0 rows affected
    const { data: checkStillExists } = await adminClient
      .from("saved_horoscopes")
      .select("id")
      .eq("id", h1.id);
    assert.strictEqual(checkStillExists.length, 1, "Horoscope must still exist; rival delete had no effect");
    pass(`Cross-user isolation verified: Another authenticated user cannot read or delete foreign horoscopes.`);

    // Clean up rival user
    await adminClient.auth.admin.deleteUser(rivalUserId);
  } catch (err) {
    fail("Saved horoscopes RLS and sequential numbering", err);
  } finally {
    // Cleanup primary test user and their horoscopes
    if (testUserId) {
      await adminClient.from("saved_horoscopes").delete().eq("user_id", testUserId);
      await adminClient.from("profiles").delete().eq("id", testUserId);
      await adminClient.auth.admin.deleteUser(testUserId);
    }
  }

  console.log("\n================================================================================");
  console.log(`  VERIFICATION RESULTS: ${testPassed} / ${testTotal} TESTS PASSED`);
  console.log("================================================================================");

  if (testPassed !== testTotal) {
    process.exitCode = 1;
  }
}

runLiveVerification().catch((err) => {
  console.error("Fatal verification error:", err);
  process.exitCode = 1;
});
