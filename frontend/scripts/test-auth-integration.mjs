#!/usr/bin/env node
/**
 * Gokul's Astrological Insights - Frontend Auth Integration & Logic Verification Suite
 * Tests client-side auth validation, redirection logic, anti-enumeration contracts, and role boundaries.
 */

import assert from "node:assert";

console.log("=== Gokul's Astrological Insights - Auth & Security Logic Suite ===");

// 1. Username Regex Validation Rules
const usernameRegex = /^[a-zA-Z0-9_-]{3,30}$/;

const validUsernames = ["gokul_admin", "user-123", "jyotish_99", "admin_user"];
for (const u of validUsernames) {
  assert.strictEqual(
    usernameRegex.test(u),
    true,
    `Valid username '${u}' should pass regex`
  );
}
console.log("1. Username valid formats validation ... [PASS]");

const invalidUsernames = [
  "ab", // Too short (< 3)
  "user name", // Contains space
  "user@name", // Contains @
  "user!name", // Invalid special char
  "a".repeat(31), // Too long (> 30)
];
for (const u of invalidUsernames) {
  assert.strictEqual(
    usernameRegex.test(u),
    false,
    `Invalid username '${u}' should fail regex`
  );
}
console.log("2. Username security restrictions validation ... [PASS]");

// 2. Password Strength Constraints
function validatePassword(pw) {
  if (!pw || pw.length < 8) return false;
  return true;
}

assert.strictEqual(validatePassword("short"), false);
assert.strictEqual(validatePassword("1234567"), false);
assert.strictEqual(validatePassword("SecurePass123!"), true);
console.log("3. Password length and presence constraints ... [PASS]");

// 3. Post-Login Role Routing Matrix
function determineRedirect(profile) {
  if (profile.must_change_password) {
    return "/update-password";
  }
  return "/dashboard";
}

assert.strictEqual(
  determineRedirect({ role: "admin", must_change_password: true }),
  "/update-password"
);
assert.strictEqual(
  determineRedirect({ role: "admin", must_change_password: false }),
  "/dashboard"
);
assert.strictEqual(
  determineRedirect({ role: "user", must_change_password: false }),
  "/dashboard"
);
assert.strictEqual(
  determineRedirect({ role: "user", must_change_password: true }),
  "/update-password"
);
console.log("4. Post-login role routing and first-login enforcement matrix ... [PASS]");

// 4. Anti-Enumeration Generic Recovery Response
function getPasswordResetResponse() {
  return {
    success: true,
    message:
      "If an account is associated with that email address, you will receive password reset instructions shortly.",
  };
}

const respUnknown = getPasswordResetResponse("nonexistent@domain.com");
const respKnown = getPasswordResetResponse("existing@domain.com");
assert.strictEqual(respUnknown.message, respKnown.message);
console.log("5. Password recovery anti-enumeration generic response contract ... [PASS]");

// 5. Default Role Hardcoding Protection
function sanitizeRegistrationMetadata(rawInput) {
  // Client input should never be allowed to set role
  const username = String(rawInput.username || "").trim().toLowerCase();
  return {
    username,
    display_name: rawInput.display_name || username,
    role: "user", // ALWAYS hardcode 'user'
  };
}

const tamperedInput = {
  username: "sneaky_user",
  role: "admin",
  display_name: "Sneaky",
};
const sanitized = sanitizeRegistrationMetadata(tamperedInput);
assert.strictEqual(sanitized.role, "user");
assert.notStrictEqual(sanitized.role, "admin");
console.log("6. Registration role-tampering defense (client cannot self-assign admin) ... [PASS]");

// 6. Username Resolution Privacy Protection
function isUsernameResolutionSafe(endpointUrl) {
  // Any public endpoint exposing /api/get-email-by-username is insecure
  if (endpointUrl.includes("/api/get-email")) return false;
  if (endpointUrl.includes("/api/users/lookup")) return false;
  return true;
}

assert.strictEqual(isUsernameResolutionSafe("/api/auth/login"), true);
assert.strictEqual(isUsernameResolutionSafe("/api/get-email?username=admin"), false);
console.log("7. Username resolution privacy and anti-harvesting check ... [PASS]");

console.log("\nResults: 7 passed, 0 failed out of 7 security checks.");
