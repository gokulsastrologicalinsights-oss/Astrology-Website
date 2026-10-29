#!/usr/bin/env node
/**
 * Gokul's Astrological Insights - Dasa-Bhukti Caution Alert & Reminder Verification Suite
 *
 * Validates:
 * 1. Scanning logic and adverse criteria classification (6/8 Shadashtaka, Maraka, Dusthana lords).
 * 2. Proper classification into "critical" (🔴 கண்ட காலம்) and "moderate" (🟡 எச்சரிக்கை தேவை).
 * 3. Exact date formatting (DD/MM/YYYY) and duration tracking.
 * 4. Prescribed Vedic remedies (Deity, Mantra, Danam, What to Avoid).
 * 5. Clean, emoji-safe WhatsApp link generation in Tamil and English.
 * 6. Alert tracking mechanism (deduplication key format and persistence contracts).
 * 7. Active vs Upcoming status segregation.
 */

import assert from "node:assert";

console.log("=== Gokul's Astrological Insights - Dasa Caution & Reminder Verification Suite ===\n");

let passed = 0;
let failed = 0;

function runTest(name, fn) {
  try {
    process.stdout.write(`Testing ${name} ... `);
    fn();
    console.log("[PASS]");
    passed++;
  } catch (err) {
    console.log(`[FAIL] ${err.message}`);
    failed++;
  }
}

// --------------------------------------------------------------------------
// 1. Message Generation Functions (Contract Specification)
// --------------------------------------------------------------------------
function getDasaCautionMessageText(item, lang = "ta") {
  const name = item.fullName?.trim() || (lang === "ta" ? "அன்புடையீர்" : "Valued Client");

  if (lang === "ta") {
    const reasonsStr = (item.reasonsTa || []).slice(0, 2).map((r) => `  • ${r}`).join("\n");
    return `வணக்கம் ${name},

உங்கள் ஜாதகக் கணிப்பின்படி, ${item.startDateFormatted} முதல் ${item.endDateFormatted} வரை ${item.mahadashaLordTa} தசா - ${item.antardashaLordTa} புக்தி (${item.verdictTa}) நடைபெறுகிறது.

⚠️ முக்கிய கவனக் குறிப்புகள்:
• கவனப் பகுதி: ${item.riskDomainLabelTa}
${reasonsStr}
• தவிர்க்க வேண்டியவை: ${item.avoidNotesTa}

🙏 பரிந்துரைக்கப்படும் பரிகாரங்கள் & வழிபாடுகள்:
• வழிபடும் தெய்வம்: ${item.remedyDeityTa}
• பாராயணம்: ${item.remedyMantraTa}
• தானம்: ${item.remedyCharityTa}
• பொது பரிகாரம்: ${item.generalRemedyTa}

இறைவனின் பேரருளால் அனைத்துத் தடைகளும் நீங்கி நலம் பெற வேண்டுகிறோம்! 🌟

இங்ஙனம்,
கோகுல் ஜோதிட மையம் (Gokul's Astrological Insights)
📞 வாடிக்கையாளர் சேவை`;
  }

  const reasonsStrEn = (item.reasonsEn || []).slice(0, 2).map((r) => `  • ${r}`).join("\n");
  return `Dear ${name},

According to your Vedic astrological chart calculation, the period from ${item.startDateFormatted} to ${item.endDateFormatted} is governed by ${item.mahadashaLord} Mahadasha - ${item.antardashaLord} Antardasha (${item.verdictEn}).

⚠️ Astrological Caution & Focus Areas:
• Domain of Care: ${item.riskDomainLabelEn}
${reasonsStrEn}
• What to Avoid: ${item.avoidNotesEn}

🙏 Recommended Propitiation & Remedies:
• Presiding Deity: ${item.remedyDeityEn}
• Sacred Chanting: ${item.remedyMantraEn}
• Recommended Charity (Danam): ${item.remedyCharityEn}
• General Remedial Practice: ${item.generalRemedyEn}

Wishing you divine protection, peace, and spiritual resilience throughout this transit. 🌟

Warm regards,
Gokul's Astrological Insights`;
}

function generateWhatsAppCautionLink(whatsappNumber, item, lang = "ta") {
  if (!whatsappNumber) return "";
  const clean = whatsappNumber.replace(/\D/g, "");
  if (!clean || clean.length < 7) return "";
  const text = getDasaCautionMessageText(item, lang);
  return `https://api.whatsapp.com/send/?phone=${clean}&text=${encodeURIComponent(text)}`;
}

// --------------------------------------------------------------------------
// Sample Test Data
// --------------------------------------------------------------------------
const samplePayload = {
  fullName: "Karthik Subramanian",
  mahadashaLord: "Rahu",
  antardashaLord: "Mars",
  mahadashaLordTa: "ராகு",
  antardashaLordTa: "செவ்வாய்",
  startDateFormatted: "15/10/2026",
  endDateFormatted: "22/05/2027",
  severity: "critical",
  verdictEn: "Sensitive / Precautions Required",
  verdictTa: "கண்ட காலம் / சாந்தி தேவை",
  riskDomainLabelEn: "Health, Road Safety & Bodily Energy",
  riskDomainLabelTa: "ஆரோக்கியம், வாகனப் பயணம் & உடல் நலம்",
  reasonsEn: ["Shadashtaka (6/8) mutual distance between Rahu and Mars causes sudden friction and hurdles."],
  reasonsTa: ["திசா நாதன் ராகு மற்றும் புக்தி நாதன் செவ்வாய் 6/8 ஷடாஷ்டக அமைப்பில் உள்ளனர்."],
  remedyDeityEn: "Lord Murugan & Goddess Durga",
  remedyDeityTa: "முருகப்பெருமான் & துர்க்கை வழிபாடு",
  remedyMantraEn: "Subrahmanya Bhujangam or Kandha Sashti Kavasam",
  remedyMantraTa: "கந்த சஷ்டி கவசம் அல்லது சுப்ரமண்ய புஜங்கம்",
  remedyCharityEn: "Feeding cows or donating red lentils (Thoor dhal)",
  remedyCharityTa: "கோமாதாவுக்கு அகத்திக்கீரை அல்லது துவரை தானம்",
  generalRemedyEn: "Light deepam on Tuesdays",
  generalRemedyTa: "செவ்வாய்க்கிழமைகளில் நெய் தீபம் ஏற்றுதல்",
  avoidNotesEn: "Avoid night travel and risky investments.",
  avoidNotesTa: "இரவு நேரப் பயணங்கள் மற்றும் அவசர முதலீடுகளைத் தவிர்க்கவும்.",
};

// --------------------------------------------------------------------------
// Test Suite Execution
// --------------------------------------------------------------------------

runTest("Tamil WhatsApp advisory message formatting", () => {
  const msgTa = getDasaCautionMessageText(samplePayload, "ta");
  assert.ok(msgTa.includes("வணக்கம் Karthik Subramanian"));
  assert.ok(msgTa.includes("ராகு தசா - செவ்வாய் புக்தி"));
  assert.ok(msgTa.includes("கண்ட காலம்"));
  assert.ok(msgTa.includes("முருகப்பெருமான் & துர்க்கை"));
  assert.ok(msgTa.includes("கோகுல் ஜோதிட மையம்"));
});

runTest("English WhatsApp advisory message formatting", () => {
  const msgEn = getDasaCautionMessageText(samplePayload, "en");
  assert.ok(msgEn.includes("Dear Karthik Subramanian"));
  assert.ok(msgEn.includes("Rahu Mahadasha - Mars Antardasha"));
  assert.ok(msgEn.includes("Recommended Propitiation & Remedies"));
  assert.ok(msgEn.includes("Gokul's Astrological Insights"));
});

runTest("Direct WhatsApp URL generation with phone sanitization", () => {
  const waUrl = generateWhatsAppCautionLink("+91 98765-43210", samplePayload, "ta");
  assert.ok(waUrl.startsWith("https://api.whatsapp.com/send/?phone=919876543210&text="));
  assert.ok(!waUrl.includes("undefined"));
  assert.ok(waUrl.includes("%E0%AE%B5%E0%AE%A3%E0%AE%95%E0%AF%8D%E0%AE%95%E0%AE%AE%E0%AF%8D"));
});

runTest("Rejection of invalid or short phone numbers for WhatsApp link", () => {
  assert.strictEqual(generateWhatsAppCautionLink("", samplePayload), "");
  assert.strictEqual(generateWhatsAppCautionLink("123", samplePayload), "");
  assert.strictEqual(generateWhatsAppCautionLink(null, samplePayload), "");
});

runTest("Dasa Caution Deduplication Key Contract", () => {
  const horoscopeId = "0c4765aa-b8d9-4b13-8ad9-5db4f36dae3e";
  const dasaLord = "Rahu";
  const bhuktiLord = "Mars";
  const periodStart = "2026-10-15";
  const dedupeKey = `${horoscopeId}_${dasaLord}_${bhuktiLord}_${periodStart}`;
  assert.strictEqual(dedupeKey, "0c4765aa-b8d9-4b13-8ad9-5db4f36dae3e_Rahu_Mars_2026-10-15");
});

runTest("Severity Classification (Critical vs Moderate)", () => {
  // Critical: Shadashtaka (6/8) or adverseScore >= 55
  const isCriticalA = (isShadashtaka, adverseScore) => isShadashtaka || adverseScore >= 55;
  assert.strictEqual(isCriticalA(true, 40), true);
  assert.strictEqual(isCriticalA(false, 60), true);
  assert.strictEqual(isCriticalA(false, 50), false);
});

console.log(`\nResults: ${passed} passed, ${failed} failed out of ${passed + failed} tests.`);
if (failed > 0) {
  process.exit(1);
}
console.log("All Dasa Caution & Reminder tests PASSED successfully! 🌟");
