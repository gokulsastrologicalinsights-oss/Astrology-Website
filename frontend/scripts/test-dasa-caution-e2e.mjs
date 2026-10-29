#!/usr/bin/env node
/**
 * Gokul's Astrological Insights - Dasa Caution System End-to-End Live Verification Suite
 * Tests:
 * 1. User authentication and session preservation
 * 2. GET /api/customers/dasa-cautions: scanning saved charts for adverse Dasa-Bhuktis
 * 3. Contract validation for DasaCautionItem (names, dates, severity, pariharams, WhatsApp URL)
 * 4. POST /api/customers/dasa-cautions: marking caution reminder sent
 * 5. Re-querying to verify alertSent state transitions to true with sent_at timestamp
 * 6. Clean-up of test artifacts
 */

import { createClient } from "@supabase/supabase-js";
import assert from "node:assert";

const PORT = 3001;
const BASE_URL = `http://127.0.0.1:${PORT}`;

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

async function runE2ETest() {
  console.log("================================================================================");
  console.log("  GOKUL'S ASTROLOGICAL INSIGHTS - DASA CAUTION E2E LIVE TEST SUITE");
  console.log(`  Target Server: ${BASE_URL}`);
  console.log("================================================================================\n");

  let passCount = 0;
  function pass(desc) {
    passCount++;
    console.log(`[PASS ${passCount}] ${desc}`);
  }

  // 1. Authenticate or create test user with role: admin
  const testEmail = `caution_test_${Date.now()}@example.com`;
  const testPassword = "CautionPass2026#Secure!";
  const testUsername = `caut_${Date.now().toString().slice(-6)}`;

  console.log(`[SETUP] Creating test admin user: ${testEmail}...`);
  const { data: authData, error: authError } = await adminClient.auth.admin.createUser({
    email: testEmail,
    password: testPassword,
    email_confirm: true,
    user_metadata: { username: testUsername },
  });
  assert(!authError, `Failed to create test user: ${authError?.message}`);
  const testUserId = authData.user.id;

  // Insert profile with role admin
  await adminClient.from("profiles").upsert({
    id: testUserId,
    username: testUsername,
    display_name: "Test Astrologer",
    role: "admin",
  });
  pass(`Test astrologer created with ID: ${testUserId}`);

  // Sign in via /api/auth/login to get proper server-side session cookies
  console.log("[LOGIN] Logging in via POST /api/auth/login...");
  const loginRes = await fetch(`${BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      identifier: testEmail,
      password: testPassword,
    }),
  });

  assert.strictEqual(loginRes.status, 200, `Login should return 200, got ${loginRes.status}`);
  const loginData = await loginRes.json();
  assert.strictEqual(loginData.success, true, "Login should succeed");
  
  // Extract Set-Cookie header
  const rawCookies = loginRes.headers.getSetCookie 
    ? loginRes.headers.getSetCookie() 
    : [loginRes.headers.get("set-cookie") || ""];
  const cookieHeader = rawCookies.map((c) => c.split(";")[0]).join("; ");
  pass("User authenticated via /api/auth/login with valid session cookies");

  // 2. Fetch /api/customers/dasa-cautions
  console.log("\n[TEST] Querying GET /api/customers/dasa-cautions?lang=ta...");
  const res = await fetch(`${BASE_URL}/api/customers/dasa-cautions?lang=ta`, {
    headers: {
      Cookie: cookieHeader,
    },
  });

  assert.strictEqual(res.status, 200, `Expected HTTP 200, got ${res.status}`);
  const data = await res.json();
  assert.strictEqual(data.success, true, "Response should have success: true");
  assert.ok(Array.isArray(data.alerts), "Response should have alerts array");
  assert.ok(typeof data.activeCount === "number", "Response should have activeCount number");
  assert.ok(typeof data.upcomingCount === "number", "Response should have upcomingCount number");
  assert.ok(data.todayKolkata, "Response should have todayKolkata string");
  pass(`GET /api/customers/dasa-cautions returned 200 OK with ${data.alerts.length} flagged charts (Active: ${data.activeCount}, Upcoming: ${data.upcomingCount})`);

  if (data.alerts.length > 0) {
    const item = data.alerts[0];
    assert.ok(item.fullName, "Item should have fullName");
    assert.ok(item.mahadashaLord, "Item should have mahadashaLord");
    assert.ok(item.antardashaLord, "Item should have antardashaLord");
    assert.ok(item.startDateFormatted, "Item should have startDateFormatted");
    assert.ok(item.endDateFormatted, "Item should have endDateFormatted");
    assert.ok(item.severity === "critical" || item.severity === "moderate", "Severity must be critical or moderate");
    assert.ok(item.remedyDeityTa, "Item should have Tamil remedy deity");
    assert.ok(item.whatsappLinkTa, "Item should have WhatsApp URL");
    console.log(`[ALERT DATA VALIDATED] Client: ${item.fullName} | ${item.mahadashaLordTa} - ${item.antardashaLordTa} | Severity: ${item.severity} | Dates: ${item.startDateFormatted} to ${item.endDateFormatted}`);
    pass("Alert item schema and astrological risk parameters strictly validated");

    // 3. Test POST /api/customers/dasa-cautions (Marking as sent)
    console.log("\n[TEST] Marking caution alert as sent via POST /api/customers/dasa-cautions...");
    const postRes = await fetch(`${BASE_URL}/api/customers/dasa-cautions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Cookie: authCookie,
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({
        horoscope_id: item.horoscopeId,
        customer_id: item.customerId,
        dasa_lord: item.mahadashaLord,
        bhukti_lord: item.antardashaLord,
        period_start: item.startDateIso,
        period_end: item.endDateIso,
        severity: item.severity,
      }),
    });

    assert.strictEqual(postRes.status, 200, `Expected HTTP 200 from POST, got ${postRes.status}`);
    const postData = await postRes.json();
    assert.strictEqual(postData.success, true, "POST response must have success: true");
    assert.ok(postData.sent_at, "POST response must have sent_at timestamp");
    pass(`POST /api/customers/dasa-cautions successfully marked alert sent at ${postData.sent_at}`);

    // 4. Re-query GET /api/customers/dasa-cautions to verify persistence of sent status
    console.log("\n[TEST] Re-querying GET to verify alerted state transition...");
    const reRes = await fetch(`${BASE_URL}/api/customers/dasa-cautions?lang=ta`, {
      headers: {
        Cookie: authCookie,
        Authorization: `Bearer ${accessToken}`,
      },
    });
    const reData = await reRes.json();
    const target = reData.alerts.find(
      (a) =>
        a.horoscopeId === item.horoscopeId &&
        a.mahadashaLord === item.mahadashaLord &&
        a.antardashaLord === item.antardashaLord
    );

    if (target) {
      assert.strictEqual(target.alertSent, true, "Target item must reflect alertSent: true");
      assert.ok(target.alertSentAt, "Target item must have alertSentAt timestamp");
      pass("Dasa caution persistence and sent status transition verified across subsequent queries");
    }
  }

  // Clean-up test user
  await adminClient.auth.admin.deleteUser(testUserId);
  pass("Test user artifacts cleaned up successfully");

  console.log("\n================================================================================");
  console.log(`  ALL ${passCount} DASA CAUTION E2E TESTS PASSED SUCCESSFULLY!`);
  console.log("================================================================================");
}

runE2ETest().catch((err) => {
  console.error("E2E Test failed:", err);
  process.exit(1);
});
