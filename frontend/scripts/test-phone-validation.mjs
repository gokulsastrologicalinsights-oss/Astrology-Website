/**
 * Verification Test: Phone Number Validation, Normalization, and WhatsApp Link Generation
 */

import {
  cleanRawPhone,
  validateAndNormalizePhone,
  generateWhatsAppBirthdayLink,
  isBirthdayTodayInKolkata,
  getTodayKolkataDateString,
} from "../src/lib/phone-utils.ts";

let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (condition) {
    console.log(`  ✅ PASS: ${message}`);
    passed++;
  } else {
    console.error(`  ❌ FAIL: ${message}`);
    failed++;
  }
}

console.log("=== 1. Testing Raw Phone Cleaning ===");
assert(cleanRawPhone(" 98765 43210 ") === "9876543210", "Strips spaces");
assert(cleanRawPhone("(987) 654-3210") === "9876543210", "Strips parentheses and dashes");
assert(cleanRawPhone("987.654.3210") === "9876543210", "Strips dots");
assert(cleanRawPhone("") === "", "Handles empty string");

console.log("\n=== 2. Testing Mandatory Phone Rejection ===");
const emptyRes = validateAndNormalizePhone("", "+91");
assert(!emptyRes.isValid, "Rejects empty phone number");
assert(emptyRes.error.includes("required"), "Clear error message on empty");

console.log("\n=== 3. Testing Indian (+91) Phone Numbers ===");
// Valid 10-digit starting with 6,7,8,9
const v1 = validateAndNormalizePhone("9876543210", "+91");
assert(v1.isValid, "Accepts 10-digit number starting with 9");
assert(v1.normalizedPhone === "+919876543210", "Normalized E.164 has +91");
assert(v1.whatsappNumber === "919876543210", "WhatsApp number has digits only, no +");
assert(v1.displayPhone === "+91 98765 43210", "Display formatted correctly");

const v2 = validateAndNormalizePhone("+91 87654 32109", "+91");
assert(v2.isValid, "Accepts formatted number with +91 prefix");
assert(v2.normalizedPhone === "+918765432109", "Normalized without duplicate +91");
assert(v2.whatsappNumber === "918765432109", "WhatsApp number without duplicate 91");

const v3 = validateAndNormalizePhone("07654321098", "+91");
assert(v3.isValid, "Accepts number with leading zero");
assert(v3.normalizedPhone === "+917654321098", "Strips leading zero before normalising");

// Invalid Indian numbers
const inv1 = validateAndNormalizePhone("5876543210", "+91");
assert(!inv1.isValid, "Rejects 10 digits starting with 5 (must be 6-9)");

const inv2 = validateAndNormalizePhone("987654321", "+91");
assert(!inv2.isValid, "Rejects 9 digits (too short)");

const inv3 = validateAndNormalizePhone("987654321012", "+91");
assert(!inv3.isValid, "Rejects 12 digits (too long)");

console.log("\n=== 4. Testing International Phone Numbers ===");
// US (+1)
const us = validateAndNormalizePhone("202 555 0123", "+1");
assert(us.isValid, "Accepts valid US number");
assert(us.normalizedPhone === "+12025550123", "Normalized US number");
assert(us.whatsappNumber === "12025550123", "WhatsApp US number digits only");

// UK (+44)
const uk = validateAndNormalizePhone("7911 123456", "+44");
assert(uk.isValid, "Accepts valid UK number");
assert(uk.normalizedPhone === "+447911123456", "Normalized UK number");
assert(uk.whatsappNumber === "447911123456", "WhatsApp UK number digits only");

// UAE (+971)
const uae = validateAndNormalizePhone("50 123 4567", "+971");
assert(uae.isValid, "Accepts valid UAE number");
assert(uae.normalizedPhone === "+971501234567", "Normalized UAE number");
assert(uae.whatsappNumber === "971501234567", "WhatsApp UAE number digits only");

console.log("\n=== 5. Testing WhatsApp Birthday Link Generation ===");
const waLink = generateWhatsAppBirthdayLink("919876543210", "Ananya Sharma", "en");
assert(waLink.startsWith("https://api.whatsapp.com/send/?phone=919876543210&text="), "WhatsApp link starts with https://api.whatsapp.com/send/?phone=919876543210&text=");
assert(!waLink.includes("+"), "WhatsApp link contains NO leading plus sign");
assert(!waLink.includes(" "), "WhatsApp link contains NO unencoded spaces");
assert(waLink.includes(encodeURIComponent("Ananya Sharma")), "Personalized with customer name");

const waLinkTa = generateWhatsAppBirthdayLink("919876543210", "விஜய் முருகன்", "ta");
assert(waLinkTa.startsWith("https://api.whatsapp.com/send/?phone=919876543210&text="), "Tamil WhatsApp link generated");
assert(waLinkTa.includes(encodeURIComponent("விஜய் முருகன்")), "Tamil personalized name encoded");

// Never generate a WhatsApp URL for an empty or invalid number
assert(generateWhatsAppBirthdayLink("", "Test Client") === "", "Returns empty string for empty WhatsApp number");
assert(generateWhatsAppBirthdayLink(null, "Test Client") === "", "Returns empty string for null WhatsApp number");
assert(generateWhatsAppBirthdayLink("   ", "Test Client") === "", "Returns empty string for whitespace WhatsApp number");
assert(generateWhatsAppBirthdayLink("12345", "Test Client") === "", "Returns empty string for too short (<7 digits) number");

console.log("\n=== 6. Testing Birthday In Asia/Kolkata Matching ===");
const todayKolkata = getTodayKolkataDateString();
console.log(`  Info: Current date in Asia/Kolkata is ${todayKolkata}`);
const [y, m, d] = todayKolkata.split("-");

const testBirthDateToday = `1990-${m}-${d}`;
assert(isBirthdayTodayInKolkata(testBirthDateToday), `Correctly identifies today's celebrant (${testBirthDateToday})`);

const otherMonth = m === "01" ? "02" : "01";
const testBirthDateOther = `1990-${otherMonth}-${d}`;
assert(!isBirthdayTodayInKolkata(testBirthDateOther), `Correctly ignores different month (${testBirthDateOther})`);

console.log(`\n========================================`);
console.log(`Summary: ${passed} passed, ${failed} failed`);
console.log(`========================================`);

if (failed > 0) {
  process.exit(1);
} else {
  console.log("All Phone Validation and Normalization Tests Passed!");
}
