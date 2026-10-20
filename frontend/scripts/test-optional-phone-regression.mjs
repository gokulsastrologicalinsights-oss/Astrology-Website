/**
 * Regression Test Suite: Optional Customer WhatsApp Number
 * Tests all 7 Acceptance Criteria:
 * 1. Vedic horoscope saves without a phone number.
 * 2. KP horoscope saves without a phone number.
 * 3. Birthday popup appears for a legacy horoscope without a phone number.
 * 4. A customer with a phone number receives a valid click-to-chat link.
 * 5. A customer without a phone number receives no invalid WhatsApp link but still appears in the popup.
 * 6. Multiple horoscopes belonging to one customer produce one birthday reminder.
 * 7. Existing customer profiles and legacy records remain preserved and usable.
 */

import {
  getOrCreateCustomerRecord,
  updateCustomerContactDetails,
  getTodayBirthdayCelebrants,
  listCustomersForUser,
  markBirthdayWishSent,
} from "../src/lib/customer-service.ts";
import {
  generateWhatsAppBirthdayLink,
  getTodayKolkataDateString,
  isBirthdayTodayInKolkata,
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

async function runRegressionSuite() {
  console.log("=================================================================");
  console.log("  OPTIONAL CUSTOMER WHATSAPP NUMBER - REGRESSION TEST SUITE");
  console.log("=================================================================\n");

  const testUserId = `test_opt_${Date.now()}`;
  const todayKolkata = getTodayKolkataDateString();
  const [currY, currM, currD] = todayKolkata.split("-");
  const celebrantDob = `1995-${currM}-${currD}`;

  // ---------------------------------------------------------------------------
  console.log("--- Test 1: Vedic Horoscope Saves Without Phone Number ---");
  // ---------------------------------------------------------------------------
  const vedicCust = await getOrCreateCustomerRecord(testUserId, {
    fullName: "Vedic Client Without Phone",
    birthDate: "1994-06-20",
    phoneNumber: "", // No phone supplied
    countryCode: "+91",
  });
  assert(vedicCust.customer.id !== undefined, "Vedic customer record created successfully without phone");
  assert(!vedicCust.customer.normalized_phone, "Normalized phone is empty or null");
  assert(!vedicCust.customer.whatsapp_number, "WhatsApp number is empty or null");
  assert(vedicCust.customer.full_name === "Vedic Client Without Phone", "Full name preserved accurately");

  // ---------------------------------------------------------------------------
  console.log("\n--- Test 2: KP Horoscope Saves Without Phone Number ---");
  // ---------------------------------------------------------------------------
  const kpCust = await getOrCreateCustomerRecord(testUserId, {
    fullName: "KP Querent Without Phone",
    birthDate: "1988-12-14",
    phoneNumber: undefined, // Phone omitted entirely
    countryCode: "+91",
  });
  assert(kpCust.customer.id !== undefined, "KP customer record created successfully without phone");
  assert(!kpCust.customer.normalized_phone, "KP customer normalized phone is empty or null");
  assert(kpCust.customer.birth_date === "1988-12-14", "KP birth date preserved");

  // ---------------------------------------------------------------------------
  console.log("\n--- Test 3: Customer WITH Phone Receives Valid Click-to-Chat Link ---");
  // ---------------------------------------------------------------------------
  const phoneCust = await getOrCreateCustomerRecord(testUserId, {
    fullName: "Ramanathan Narayanan",
    birthDate: celebrantDob,
    phoneNumber: "9876543210",
    countryCode: "+91",
  });
  assert(phoneCust.customer.normalized_phone === "+919876543210", "Stored valid E.164 phone");
  assert(phoneCust.customer.whatsapp_number === "919876543210", "Stored WhatsApp number digits-only");

  const celebrantsWithPhone = await getTodayBirthdayCelebrants(testUserId, false, "en");
  const ramanathan = celebrantsWithPhone.celebrants.find((c) => c.id === phoneCust.customer.id);
  assert(ramanathan !== undefined, "Ramanathan detected for today's birthday in Asia/Kolkata");
  assert(ramanathan.hasValidPhone === true, "hasValidPhone is true for customer with phone");
  assert(
    ramanathan.whatsappLink.startsWith("https://wa.me/919876543210?text="),
    "Generated valid WhatsApp click-to-chat URL"
  );
  assert(!ramanathan.whatsappLink.includes("+"), "WhatsApp URL contains no '+' sign");
  assert(ramanathan.whatsappLink.includes(encodeURIComponent("Ramanathan Narayanan")), "URL contains encoded personal name");

  // ---------------------------------------------------------------------------
  console.log("\n--- Test 4: Customer WITHOUT Phone Receives NO Invalid WhatsApp Link But Still Appears in Popup ---");
  // ---------------------------------------------------------------------------
  const noPhoneCelebrant = await getOrCreateCustomerRecord(testUserId, {
    fullName: "Divya Lakshmi",
    birthDate: celebrantDob, // Birthday today
    phoneNumber: "", // No phone
  });
  const celebrantsNoPhone = await getTodayBirthdayCelebrants(testUserId, false, "en");
  const divya = celebrantsNoPhone.celebrants.find((c) => c.id === noPhoneCelebrant.customer.id);
  assert(divya !== undefined, "Divya appears in birthday celebrants list despite having no phone");
  assert(divya.hasValidPhone === false, "hasValidPhone is false");
  assert(divya.whatsappLink === "", "whatsappLink is strictly empty (never 'https://wa.me/?text=...')");
  assert(
    divya.warningMessage && divya.warningMessage.includes("WhatsApp number not added"),
    `Displays clear notice: '${divya.warningMessage}'`
  );

  // ---------------------------------------------------------------------------
  console.log("\n--- Test 5: Multiple Horoscopes for One Customer Produce Exactly ONE Birthday Reminder ---");
  // ---------------------------------------------------------------------------
  // Save second horoscope for Ramanathan using his customerId
  const horo2 = await getOrCreateCustomerRecord(testUserId, {
    customerId: phoneCust.customer.id,
    fullName: "Ramanathan Narayanan",
    birthDate: celebrantDob,
    phoneNumber: "9876543210",
  });
  assert(horo2.isNew === false, "Second horoscope deduplicates to existing customer");

  // Save third horoscope using name + formatted phone match
  const horo3 = await getOrCreateCustomerRecord(testUserId, {
    fullName: "Ramanathan Narayanan",
    birthDate: celebrantDob,
    phoneNumber: "+91 98765 43210",
  });
  assert(horo3.isNew === false, "Third horoscope deduplicates to existing customer");

  const celebrantsMulti = await getTodayBirthdayCelebrants(testUserId, false, "en");
  const ramanathanMatches = celebrantsMulti.celebrants.filter((c) => c.id === phoneCust.customer.id);
  assert(
    ramanathanMatches.length === 1,
    `Multiple horoscopes produced exactly 1 reminder (found: ${ramanathanMatches.length})`
  );

  // ---------------------------------------------------------------------------
  console.log("\n--- Test 6: Legacy Horoscopes Detected for Birthday Reminders ---");
  // ---------------------------------------------------------------------------
  const legacyChart = await getOrCreateCustomerRecord(testUserId, {
    fullName: "Legacy Archive Client",
    birthDate: celebrantDob,
    isLegacyWithoutPhone: true,
  });
  const celebrantsLegacy = await getTodayBirthdayCelebrants(testUserId, false, "en");
  const legacyFound = celebrantsLegacy.celebrants.find((c) => c.id === legacyChart.customer.id);
  assert(legacyFound !== undefined, "Legacy archive horoscope detected for birthday popup");
  assert(legacyFound.hasValidPhone === false, "Legacy horoscope hasValidPhone is false");
  assert(legacyFound.whatsappLink === "", "Legacy horoscope does not have invalid link");

  // ---------------------------------------------------------------------------
  console.log("\n--- Test 7: Updating Contact Converts No-Phone Record to Active WhatsApp Chat ---");
  // ---------------------------------------------------------------------------
  const updatedDivya = await updateCustomerContactDetails(noPhoneCelebrant.customer.id, {
    fullName: "Divya Lakshmi",
    birthDate: celebrantDob,
    countryCode: "+91",
    phoneNumber: "9876543288",
  });
  assert(updatedDivya.normalized_phone === "+919876543288", "Contact updated to +919876543288");
  assert(updatedDivya.whatsapp_number === "919876543288", "WhatsApp number updated");

  const celebrantsAfterUpdate = await getTodayBirthdayCelebrants(testUserId, false, "en");
  const refreshedDivya = celebrantsAfterUpdate.celebrants.find((c) => c.id === noPhoneCelebrant.customer.id);
  assert(refreshedDivya.hasValidPhone === true, "After update, hasValidPhone is now true");
  assert(
    refreshedDivya.whatsappLink.startsWith("https://wa.me/919876543288?text="),
    "Divya now has valid click-to-chat WhatsApp link pointing to 919876543288"
  );

  // ---------------------------------------------------------------------------
  console.log("\n--- Test 8: Manual Status Update & Dismissal Independence ---");
  // ---------------------------------------------------------------------------
  assert(refreshedDivya.wishSent === false, "Wish is pending before manual confirmation");
  const markRes = await markBirthdayWishSent(noPhoneCelebrant.customer.id, testUserId);
  assert(markRes.success === true, "Mark wish sent succeeded");

  const celebrantsAfterMark = await getTodayBirthdayCelebrants(testUserId, false, "en");
  const markedDivya = celebrantsAfterMark.celebrants.find((c) => c.id === noPhoneCelebrant.customer.id);
  assert(markedDivya.wishSent === true, "Wish marked as sent");
  assert(typeof markedDivya.wishSentAt === "string", "wishSentAt ISO timestamp populated");

  console.log("\n=================================================================");
  console.log(`TOTAL: ${passed} passed, ${failed} failed`);
  console.log("=================================================================");

  if (failed > 0) {
    process.exit(1);
  } else {
    console.log("All Regression Criteria Verified Successfully!");
  }
}

runRegressionSuite().catch((err) => {
  console.error("Test execution failed:", err);
  process.exit(1);
});
