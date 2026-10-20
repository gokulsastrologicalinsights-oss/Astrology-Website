/**
 * Verification Test: Customer Deduplication, Multiple Horoscopes Linking,
 * Birthday Reminders (Asia/Kolkata), Authoritative Updates, and Manual Status Tracking.
 */

import {
  getOrCreateCustomerRecord,
  updateCustomerContactDetails,
  getTodayBirthdayCelebrants,
  markBirthdayWishSent,
  listCustomersForUser,
} from "../src/lib/customer-service.ts";
import { getTodayKolkataDateString } from "../src/lib/phone-utils.ts";

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

async function runTests() {
  const testUserId = `test_user_${Date.now()}`;
  const todayKolkata = getTodayKolkataDateString();
  const [currY, currM, currD] = todayKolkata.split("-");
  const celebrantBirthDate = `1992-${currM}-${currD}`;

  console.log(`=== 1. Testing Customer Creation & Deduplication ===`);
  const cust1 = await getOrCreateCustomerRecord(testUserId, {
    fullName: "Karthik Subramanian",
    birthDate: celebrantBirthDate,
    phoneNumber: "9876543210",
    countryCode: "+91",
  });

  assert(cust1.isNew === true, "First horoscope creates new customer record");
  assert(cust1.customer.normalized_phone === "+919876543210", "Stored normalized E.164 phone");
  assert(cust1.customer.whatsapp_number === "919876543210", "Stored WhatsApp digits-only number");

  // Create second horoscope for the SAME customer with slightly different phone formatting
  const cust2 = await getOrCreateCustomerRecord(testUserId, {
    fullName: "Karthik Subramanian",
    birthDate: celebrantBirthDate,
    phoneNumber: "+91 98765 43210",
    countryCode: "+91",
  });

  assert(cust2.isNew === false, "Second horoscope deduplicates to existing customer");
  assert(cust2.customer.id === cust1.customer.id, "Reuses the exact same customer ID");

  // Create third horoscope specifying customerId directly
  const cust3 = await getOrCreateCustomerRecord(testUserId, {
    customerId: cust1.customer.id,
    fullName: "Karthik Subramanian",
    birthDate: celebrantBirthDate,
    phoneNumber: "9876543210",
    countryCode: "+91",
  });
  assert(cust3.isNew === false, "Explicit customerId reuses customer");
  assert(cust3.customer.id === cust1.customer.id, "Customer ID matches");

  console.log(`\n=== 2. Testing Multiple Horoscopes Produce Exactly 1 Birthday Reminder ===`);
  const reminders1 = await getTodayBirthdayCelebrants(testUserId, false, "en");
  const karthikCelebrants = reminders1.celebrants.filter((c) => c.id === cust1.customer.id);
  assert(
    karthikCelebrants.length === 1,
    `Multiple horoscopes for one customer produced exactly 1 reminder (found ${karthikCelebrants.length})`
  );

  const celebrant = karthikCelebrants[0];
  assert(celebrant.hasValidPhone === true, "Celebrant has valid phone");
  assert(celebrant.whatsappNumber === "919876543210", "Celebrant whatsapp number is digits only");
  assert(
    celebrant.whatsappLink.startsWith("https://wa.me/919876543210?text="),
    "Personalized WhatsApp link has wa.me/919876543210 format without +"
  );
  assert(!celebrant.whatsappLink.includes("+"), "WhatsApp link has no plus sign");
  assert(celebrant.wishSent === false, "Wish is initially pending (not sent)");

  console.log(`\n=== 3. Testing Authoritative Contact Update Across Horoscopes ===`);
  // Admin updates customer's phone number
  const updatedCust = await updateCustomerContactDetails(cust1.customer.id, {
    phoneNumber: "9876543299",
    countryCode: "+91",
  });
  assert(updatedCust.normalized_phone === "+919876543299", "Authoritative phone updated to +919876543299");
  assert(updatedCust.whatsapp_number === "919876543299", "Authoritative whatsapp_number updated");

  // Verify birthday reminder immediately reflects the new authoritative phone
  const reminders2 = await getTodayBirthdayCelebrants(testUserId, false, "en");
  const updatedCelebrant = reminders2.celebrants.find((c) => c.id === cust1.customer.id);
  assert(
    updatedCelebrant.normalizedPhone === "+919876543299",
    "Birthday reminder reflects updated normalized phone"
  );
  assert(
    updatedCelebrant.whatsappLink.startsWith("https://wa.me/919876543299?text="),
    "Birthday reminder WhatsApp link points to updated phone 919876543299"
  );

  console.log(`\n=== 4. Testing Customer Creation Without Phone (Optional Phone Feature) ===`);
  // New customer created without phone number
  const noPhoneCust = await getOrCreateCustomerRecord(testUserId, {
    fullName: "Priya Senthil",
    birthDate: celebrantBirthDate,
    phoneNumber: "", // Empty phone
    countryCode: "+91",
  });
  assert(noPhoneCust.customer.phone_number === "" || noPhoneCust.customer.phone_number === null, "Saved customer with null/empty phone");
  assert(!noPhoneCust.customer.normalized_phone, "Normalized phone is empty/null");

  // Deduplicate second horoscope for same customer without phone by name + DOB
  const noPhoneCust2 = await getOrCreateCustomerRecord(testUserId, {
    fullName: "Priya Senthil",
    birthDate: celebrantBirthDate,
  });
  assert(noPhoneCust2.isNew === false, "Second horoscope without phone deduplicates to existing customer");
  assert(noPhoneCust2.customer.id === noPhoneCust.customer.id, "Reuses the same customer ID");

  console.log(`\n=== 5. Testing Birthday Detection For Customer Without Phone ===`);
  const reminders3 = await getTodayBirthdayCelebrants(testUserId, false, "en");
  const priyaCelebrant = reminders3.celebrants.find((c) => c.id === noPhoneCust.customer.id);
  assert(priyaCelebrant !== undefined, "Priya detected for birthday today without phone");
  assert(priyaCelebrant.hasValidPhone === false, "Celebrant hasValidPhone is false");
  assert(priyaCelebrant.whatsappLink === "", "Celebrant does NOT have an invalid WhatsApp link (link is empty string)");
  assert(
    priyaCelebrant.warningMessage && priyaCelebrant.warningMessage.includes("WhatsApp number not added"),
    `Celebrant has exact warning message: '${priyaCelebrant.warningMessage}'`
  );

  console.log(`\n=== 6. Testing Manual Status Update Isolation ===`);
  // Opening the link does not mark as sent
  assert(updatedCelebrant.wishSent === false, "Wish is still pending after link generated");

  // Manual status update
  const markRes = await markBirthdayWishSent(cust1.customer.id, testUserId);
  assert(markRes.success === true, "Manual mark wish sent succeeded");
  assert(markRes.alreadySent === false, "Previously unsent");

  // Subsequent check
  const reminders4 = await getTodayBirthdayCelebrants(testUserId, false, "en");
  const markedCelebrant = reminders4.celebrants.find((c) => c.id === cust1.customer.id);
  assert(markedCelebrant.wishSent === true, "Wish is marked as sent");
  assert(typeof markedCelebrant.wishSentAt === "string", "Wish sent timestamp is populated");

  console.log(`\n========================================`);
  console.log(`Summary: ${passed} passed, ${failed} failed`);
  console.log(`========================================`);

  if (failed > 0) {
    process.exit(1);
  } else {
    console.log("All Customer Deduplication and Birthday Tests Passed!");
  }
}

runTests().catch((err) => {
  console.error("Test execution failed:", err);
  process.exit(1);
});
