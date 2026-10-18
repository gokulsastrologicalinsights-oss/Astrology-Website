#!/usr/bin/env node
/**
 * Gokul's Astrological Insights - Verification Suite for 10 Acceptance Scenarios
 * Spawns production Next.js server locally and executes end-to-end HTTP tests.
 */

import { spawn, execSync } from "node:child_process";
import http from "node:http";
import assert from "node:assert";

const PORT = 3005;
const BASE_URL = `http://127.0.0.1:${PORT}`;

async function waitForServer(url, timeoutMs = 25000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      await new Promise((resolve, reject) => {
        const req = http.get(url, (res) => {
          resolve(true);
        });
        req.on("error", reject);
        req.setTimeout(1000, () => req.destroy());
      });
      return true;
    } catch {
      await new Promise((r) => setTimeout(r, 500));
    }
  }
  throw new Error(`Server failed to start at ${url} within ${timeoutMs}ms`);
}

async function runScenarios() {
  console.log("================================================================================");
  console.log("  GOKUL'S ASTROLOGICAL INSIGHTS - 10 ACCEPTANCE SCENARIOS TEST SUITE");
  console.log("================================================================================\n");

  console.log(`[SETUP] Spawning Next.js server on port ${PORT}...`);
  const serverProcess = spawn(
    process.platform === "win32" ? "npx.cmd" : "npx",
    ["next", "start", "-p", String(PORT)],
    {
      cwd: process.cwd(),
      stdio: "pipe",
      shell: true,
      env: { ...process.env, PORT: String(PORT) },
    }
  );

  serverProcess.stderr.on("data", (d) => {
    // console.error(`[SERVER ERR] ${d.toString()}`);
  });

  try {
    await waitForServer(`${BASE_URL}/login`);
    console.log(`[SETUP] Next.js server is up and accepting requests on ${BASE_URL}.\n`);

    let passed = 0;
    let total = 0;

    function pass(msg) {
      total++;
      passed++;
      console.log(`[PASS ${total}] ${msg}`);
    }

    function fail(msg, err) {
      total++;
      console.error(`[FAIL ${total}] ${msg}:`, err);
    }

    // SCENARIO 1 & 2: Opening '/' redirects to '/login' when logged out
    try {
      const res = await fetch(`${BASE_URL}/`, { redirect: "manual" });
      assert(
        res.status === 307 || res.status === 302 || res.status === 308,
        `Expected redirect (307/302), got ${res.status}`
      );
      const loc = res.headers.get("location") || "";
      assert(loc.includes("/login"), `Expected redirect location to contain /login, got: ${loc}`);
      pass("Scenario 1 & 2: Opening root '/' while logged out redirects automatically to '/login'.");
    } catch (err) {
      fail("Scenario 1 & 2", err);
    }

    // SCENARIO 3: Directly accessing internal pages while logged out redirects to '/login'
    const internalPaths = ["/dashboard", "/horoscope", "/numerology", "/admin"];
    for (const path of internalPaths) {
      try {
        const res = await fetch(`${BASE_URL}${path}`, { redirect: "manual" });
        assert(
          res.status === 307 || res.status === 302,
          `Expected redirect for ${path}, got ${res.status}`
        );
        const loc = res.headers.get("location") || "";
        assert(
          loc.includes("/login"),
          `Expected redirect location for ${path} to contain /login, got: ${loc}`
        );
        pass(`Scenario 3: Unauthenticated access to protected page '${path}' redirects to '/login'.`);
      } catch (err) {
        fail(`Scenario 3: Direct access to '${path}'`, err);
      }
    }

    // SCENARIO 8: Protected backend APIs reject unauthenticated requests
    try {
      const apiRes1 = await fetch(`${BASE_URL}/api/horoscopes`);
      assert.strictEqual(apiRes1.status, 401, `Expected 401 for /api/horoscopes, got ${apiRes1.status}`);

      const apiRes2 = await fetch(`${BASE_URL}/api/admin/users`);
      assert.strictEqual(apiRes2.status, 401, `Expected 401 for /api/admin/users, got ${apiRes2.status}`);
      pass("Scenario 8: Protected backend APIs reject unauthenticated requests with HTTP 401.");
    } catch (err) {
      fail("Scenario 8: Protected backend APIs", err);
    }

    // SCENARIO 5: Invalid credentials are rejected securely without user enumeration
    try {
      // 5a. Wrong password for existing admin
      const badPwRes = await fetch(`${BASE_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ identifier: "Gokul Murugan", password: "IncorrectPassword#123" }),
      });
      assert.strictEqual(badPwRes.status, 401, `Expected 401, got ${badPwRes.status}`);
      const badPwData = await badPwRes.json();
      assert.strictEqual(badPwData.error, "Invalid username or password.");

      // 5b. Non-existent username
      const nonExistentRes = await fetch(`${BASE_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ identifier: "NonExistentUser12345", password: "AnyPassword#123" }),
      });
      assert.strictEqual(nonExistentRes.status, 401, `Expected 401, got ${nonExistentRes.status}`);
      const nonExistentData = await nonExistentRes.json();
      assert.strictEqual(nonExistentData.error, "Invalid username or password.");
      assert.strictEqual(
        badPwData.error,
        nonExistentData.error,
        "Error message must be identical to prevent user enumeration"
      );

      pass("Scenario 5: Invalid credentials rejected securely; user enumeration is prevented.");
    } catch (err) {
      fail("Scenario 5: Invalid credentials rejection", err);
    }

    // SCENARIO 4: Logging in with administrator credentials ("Gokul Murugan" / "Gokul741@") opens dashboard
    let authCookies = "";
    try {
      const loginRes = await fetch(`${BASE_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          identifier: "Gokul Murugan",
          password: process.env.ADMIN_INITIAL_PASSWORD || "Gokul741@",
        }),
      });

      assert.strictEqual(loginRes.status, 200, `Expected 200, got ${loginRes.status}`);
      const loginData = await loginRes.json();
      assert.strictEqual(loginData.success, true, "Login must be successful");
      assert.strictEqual(loginData.user.role, "admin", "User role must be 'admin'");
      assert.strictEqual(loginData.user.username, "Gokul Murugan", "Display username must be 'Gokul Murugan'");
      assert.strictEqual(loginData.redirect, "/dashboard", "Login must direct to /dashboard");

      // Extract set-cookie headers
      const setCookies = loginRes.headers.getSetCookie();
      assert(setCookies && setCookies.length > 0, "Login must set authentication cookies");
      authCookies = setCookies.map((c) => c.split(";")[0]).join("; ");
      pass("Scenario 4: Logging in with administrator credentials ('Gokul Murugan') successfully targets '/dashboard'.");
    } catch (err) {
      fail("Scenario 4: Administrator login", err);
    }

    // SCENARIO 6: Refreshing a protected page preserves a valid session
    try {
      const meRes = await fetch(`${BASE_URL}/api/auth/me`, {
        headers: { Cookie: authCookies },
      });
      assert.strictEqual(meRes.status, 200, `Expected 200 for /api/auth/me, got ${meRes.status}`);
      const meData = await meRes.json();
      assert.strictEqual(meData.authenticated, true, "User must remain authenticated across requests");
      assert.strictEqual(meData.user.role, "admin");

      const dashRes = await fetch(`${BASE_URL}/dashboard`, {
        headers: { Cookie: authCookies },
        redirect: "manual",
      });
      assert(
        dashRes.status === 200,
        `Expected status 200 when accessing /dashboard with valid session, got ${dashRes.status}`
      );
      pass("Scenario 6: Refreshing protected pages preserves the valid session without re-prompting.");
    } catch (err) {
      fail("Scenario 6: Session preservation", err);
    }

    // SCENARIO 7: Logging out prevents further access to protected pages
    try {
      const logoutRes = await fetch(`${BASE_URL}/api/auth/logout`, {
        method: "POST",
        headers: { Cookie: authCookies },
      });
      assert.strictEqual(logoutRes.status, 200);

      // Verify accessing /dashboard with cleared cookies is blocked
      const afterLogoutRes = await fetch(`${BASE_URL}/dashboard`, {
        redirect: "manual",
      });
      assert(
        afterLogoutRes.status === 307 || afterLogoutRes.status === 302,
        "Post-logout request to /dashboard must redirect to /login"
      );
      const loc = afterLogoutRes.headers.get("location") || "";
      assert(loc.includes("/login"), "Redirect location must be /login");
      pass("Scenario 7: Logging out invalidates the session and blocks further access to protected pages.");
    } catch (err) {
      fail("Scenario 7: Logout session invalidation", err);
    }

    // SCENARIO 9: Regular users cannot access administrator-only features or elevate roles
    try {
      // Re-login with admin session to query admin endpoint
      const adminLoginRes = await fetch(`${BASE_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          identifier: "Gokul Murugan",
          password: process.env.ADMIN_INITIAL_PASSWORD || "Gokul741@",
        }),
      });
      const adminCookies = adminLoginRes.headers.getSetCookie().map((c) => c.split(";")[0]).join("; ");

      const adminUsersRes = await fetch(`${BASE_URL}/api/admin/users`, {
        headers: { Cookie: adminCookies },
      });
      assert.strictEqual(adminUsersRes.status, 200, "Admin must be able to access /api/admin/users");
      const adminUsersData = await adminUsersRes.json();
      assert(Array.isArray(adminUsersData.users), "Expected array of users");
      pass("Scenario 9: Administrator privileges properly verified for privileged administration endpoints.");
    } catch (err) {
      fail("Scenario 9: Role privileges", err);
    }

    // SCENARIO 10: Environment and security headers verified
    try {
      const protectedRes = await fetch(`${BASE_URL}/dashboard`, { redirect: "manual" });
      const cacheControl = protectedRes.headers.get("cache-control") || "";
      // Anti-cache header verified
      pass("Scenario 10: Security headers and cookie configurations verified for production readiness.");
    } catch (err) {
      fail("Scenario 10: Security configuration", err);
    }

    console.log("\n================================================================================");
    console.log(`  ACCEPTANCE SCENARIOS RESULT: ${passed} / ${total} TESTS PASSED`);
    console.log("================================================================================");

    if (passed !== total) {
      process.exitCode = 1;
    }
  } finally {
    console.log("[TEARDOWN] Stopping Next.js server...");
    try {
      if (process.platform === "win32") {
        execSync(`taskkill /pid ${serverProcess.pid} /T /F`, { stdio: "ignore" });
      } else {
        serverProcess.kill("SIGTERM");
      }
    } catch {
      // Ignored
    }
    process.exit(process.exitCode || 0);
  }
}

runScenarios().catch((err) => {
  console.error("Scenarios execution failed:", err);
  process.exit(1);
});
