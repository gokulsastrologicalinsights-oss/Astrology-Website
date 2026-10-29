import fs from "fs";
import path from "path";
import assert from "assert";

console.log("=== Marriage Compatibility Report PDF Download Verification Suite ===\n");

function test(description, fn) {
  try {
    fn();
    console.log(`Testing ${description} ... [PASS]`);
  } catch (err) {
    console.error(`Testing ${description} ... [FAIL]`);
    console.error(err);
    process.exit(1);
  }
}

const frontendRoot = path.resolve(import.meta.dirname, "..");
const typesPath = path.join(frontendRoot, "src", "lib", "types.ts");
const apiPath = path.join(frontendRoot, "src", "lib", "api.ts");
const pagePath = path.join(frontendRoot, "src", "app", "tools", "marriage-compatibility", "page.tsx");

const typesContent = fs.readFileSync(typesPath, "utf-8");
const apiContent = fs.readFileSync(apiPath, "utf-8");
const pageContent = fs.readFileSync(pagePath, "utf-8");

test("types.ts exports MarriageCompatibilityPdfReportRequest interface", () => {
  assert(typesContent.includes("export interface MarriageCompatibilityPdfReportRequest"), "Missing MarriageCompatibilityPdfReportRequest interface");
  assert(typesContent.includes("report_data?:"), "Missing report_data field");
  assert(typesContent.includes("language?: \"en\" | \"ta\""), "Missing language field");
});

test("api.ts exports downloadMarriageCompatibilityPdf function", () => {
  assert(apiContent.includes("export async function downloadMarriageCompatibilityPdf"), "Missing downloadMarriageCompatibilityPdf export");
  assert(apiContent.includes("/api/v1/reports/marriage-compatibility/pdf"), "Missing endpoint URL in api.ts");
});

test("page.tsx imports downloadMarriageCompatibilityPdf and Download icon", () => {
  assert(pageContent.includes("downloadMarriageCompatibilityPdf"), "Missing downloadMarriageCompatibilityPdf import");
  assert(pageContent.includes("Download"), "Missing Download icon import");
});

test("page.tsx has Download Report button in results hero card", () => {
  assert(pageContent.includes("handleOpenDownloadModal"), "Missing handleOpenDownloadModal handler");
  assert(pageContent.includes("Download Report"), "Missing 'Download Report' button label");
  assert(pageContent.includes("அறிக்கையைப் பதிவிறக்குக"), "Missing Tamil 'அறிக்கையைப் பதிவிறக்குக' button label");
});

test("page.tsx has Download PDF button in historical snapshot banner", () => {
  assert(pageContent.includes("PDF பதிவிறக்கம்"), "Missing 'PDF பதிவிறக்கம்' button in historical banner");
});

test("page.tsx renders language selection modal before download", () => {
  assert(pageContent.includes("isDownloadModalOpen"), "Missing isDownloadModalOpen modal state");
  assert(pageContent.includes("downloadLanguage"), "Missing downloadLanguage state");
  assert(pageContent.includes("Report Language"), "Missing Report Language label in modal");
  assert(pageContent.includes("தமிழ் (Tamil)"), "Missing Tamil option in modal");
  assert(pageContent.includes("English"), "Missing English option in modal");
  assert(pageContent.includes("handleConfirmDownload"), "Missing handleConfirmDownload handler");
});

console.log("\n=============================================");
console.log("Verification Complete: All PDF UI & API Checks Passed!");
console.log("=============================================");
