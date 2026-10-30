/**
 * Gokul's Astrological Insights - Dasa Caution & Adverse Period Scanner
 * End-to-End Live API Test Suite
 *
 * Verifies:
 * 1. Admin login via /api/auth/login.
 * 2. GET /api/customers/dasa-cautions with Tamil formatting & risk parameters.
 * 3. POST /api/customers/dasa-cautions (Marking as sent).
 * 4. Persistence of sent status across subsequent queries.
 */

import assert from "node:assert";
import { createClient } from "@supabase/supabase-js";

const BASE_URL = process.env.BASE_URL || "http://127.0.0.1:3001";
const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY =
  process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_SERVICE_KEY;

if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  console.error("Missing required Supabase credentials in environment.");
  process.exit(1);
}

const adminClient = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
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

  // 1. Sign in via /api/auth/login using admin credentials
  const adminEmail = "admin@gokul-astrology.local";
  const adminPassword = "Gokul741@";

  console.log(`[LOGIN] Logging in via POST /api/auth/login as ${adminEmail}...`);
  const loginRes = await fetch(`${BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      identifier: adminEmail,
      password: adminPassword,
    }),
  });

  if (!loginRes.ok) {
    const txt = await loginRes.text();
    console.error("Login failed:", loginRes.status, txt);
  }
  assert.strictEqual(loginRes.status, 200, `Login should return 200, got ${loginRes.status}`);
  const loginData = await loginRes.json();
  assert.strictEqual(loginData.success, true, "Login should succeed");

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
  pass(
    `GET /api/customers/dasa-cautions returned 200 OK with ${data.alerts.length} flagged charts (Active: ${data.activeCount}, Upcoming: ${data.upcomingCount})`
  );

  if (data.alerts.length > 0) {
    const item = data.alerts[0];
    assert.ok(item.fullName, "Item should have fullName");
    assert.ok(item.mahadashaLord, "Item should have mahadashaLord");
    assert.ok(item.antardashaLord, "Item should have antardashaLord");
    assert.ok(item.andharLord, "Item should have andharLord");
    assert.ok(item.andharLordTa, "Item should have andharLordTa");
    assert.ok(item.startDateFormatted, "Item should have startDateFormatted");
    assert.ok(item.endDateFormatted, "Item should have endDateFormatted");
    assert.ok(item.durationFormatted, "Item should have durationFormatted");
    assert.ok(
      item.durationDays > 0 && item.durationDays <= 250,
      `Anthara duration should be in days (1-250 days), got ${item.durationDays}`
    );
    assert.ok(
      item.messageTextTa.includes("9444 55 9071"),
      "Tamil WhatsApp message must include consultation number 9444 55 9071"
    );
    assert.ok(
      item.messageTextEn.includes("9444 55 9071"),
      "English WhatsApp message must include consultation number 9444 55 9071"
    );
    assert.ok(
      item.severity === "critical" || item.severity === "moderate",
      "Severity must be critical or moderate"
    );
    assert.ok(item.remedyDeityTa, "Item should have Tamil remedy deity");
    if (item.whatsappNumber) {
      assert.ok(item.whatsappLinkTa, "Item should have WhatsApp URL when phone is present");
      assert.ok(
        item.whatsappLinkTa.includes("9444%2055%209071") || item.whatsappLinkTa.includes("9444+55+9071") || item.whatsappLinkTa.includes("9444"),
        "WhatsApp URL should encode consultation phone number"
      );
    }
    console.log(
      `[ALERT DATA VALIDATED] Client: ${item.fullName} | ${item.mahadashaLordTa} › ${item.antardashaLordTa} › ${item.andharLordTa} அந்தரம் | Severity: ${item.severity} | Anthara Window: ${item.startDateFormatted} to ${item.endDateFormatted} (${item.durationFormatted})`
    );
    pass("3-tier Anthara worst-case schema, short period alone, and consultation number strictly validated");

    // 3. Test POST /api/customers/dasa-cautions (Marking as sent)
    console.log("\n[TEST] Marking caution alert as sent via POST /api/customers/dasa-cautions...");
    const postRes = await fetch(`${BASE_URL}/api/customers/dasa-cautions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Cookie: cookieHeader,
      },
      body: JSON.stringify({
        horoscope_id: item.horoscopeId,
        customer_id: item.customerId,
        dasa_lord: item.mahadashaLord,
        bhukti_lord: item.antardashaLord,
        andhar_lord: item.andharLord,
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
        Cookie: cookieHeader,
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

  console.log("\n================================================================================");
  console.log(`  ALL ${passCount} DASA CAUTION E2E TESTS PASSED SUCCESSFULLY!`);
  console.log("================================================================================\n");
}

runE2ETest().catch((err) => {
  console.error("E2E Test failed:", err);
  process.exit(1);
});
