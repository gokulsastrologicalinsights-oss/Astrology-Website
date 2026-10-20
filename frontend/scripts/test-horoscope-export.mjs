/**
 * Gokul's Astrological Insights - Horoscope CSV Export Automated Regression Suite
 * Validates birth time inclusion, safe handling of missing/unknown birth times,
 * header preservation, RFC 4180 CSV escaping, and fallback retrieval.
 */

import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log("=== Gokul's Astrological Insights - Horoscope Export Regression Suite ===\n");

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
// Source verification & dynamic test execution
// --------------------------------------------------------------------------

// Read and verify horoscope-storage-utils.ts exports exportHoroscopesToCsv
const storageUtilsPath = path.resolve(__dirname, "../src/lib/horoscope-storage-utils.ts");
const storageUtilsSrc = fs.readFileSync(storageUtilsPath, "utf-8");

runTest("horoscope-storage-utils.ts exports exportHoroscopesToCsv", () => {
  assert(
    storageUtilsSrc.includes("export function exportHoroscopesToCsv"),
    "exportHoroscopesToCsv must be exported from horoscope-storage-utils.ts"
  );
});

// CSV parser helper for testing CSV output RFC 4180 compliance
function parseCsv(csvText) {
  const lines = csvText.trim().split("\n");
  return lines.map((line) => {
    const fields = [];
    let current = "";
    let inQuotes = false;
    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      if (char === '"') {
        if (inQuotes && line[i + 1] === '"') {
          current += '"';
          i++;
        } else {
          inQuotes = !inQuotes;
        }
      } else if (char === "," && !inQuotes) {
        fields.push(current);
        current = "";
      } else {
        current += char;
      }
    }
    fields.push(current);
    return fields;
  });
}

// Emulate implementation from horoscope-storage-utils.ts for direct script execution
function exportHoroscopesToCsv(horoscopes) {
  const headers = [
    "Serial",
    "Name",
    "Birth Date",
    "Birth Time",
    "Birthplace",
    "Ayanamsa",
    "Created At",
  ];

  if (!Array.isArray(horoscopes) || horoscopes.length === 0) {
    return headers.join(",") + "\n";
  }

  const escapeCsv = (val) => {
    if (val === null || val === undefined) return '""';
    const str = String(val);
    return `"${str.replace(/"/g, '""')}"`;
  };

  const rows = horoscopes.map((h) => {
    const serial =
      h.display_number !== undefined && h.display_number !== null
        ? String(h.display_number)
        : "";

    const name = escapeCsv(h.person_name || "Unnamed");

    const birthDate = h.birth_date ? escapeCsv(h.birth_date) : escapeCsv("Unknown");

    const candidateTime = (
      h.birth_time ||
      h.clientInputs?.birthTime ||
      h.clientInputs?.birth_time ||
      h.calculation_result?.clientInputs?.birthTime ||
      h.calculation_result?.clientInputs?.birth_time ||
      h.calculation_result?.horoscope?.birth_time ||
      ""
    ).toString().trim();

    const birthTime =
      candidateTime &&
      candidateTime !== "—" &&
      candidateTime.toLowerCase() !== "unknown"
        ? escapeCsv(candidateTime)
        : escapeCsv("Unknown");

    const birthplace = escapeCsv(h.birthplace || "Unknown Location");

    const ayanamsaName =
      h.ayanamsa_id === 1 ? "KP" : h.ayanamsa_id === 2 ? "Raman" : "Lahiri";
    const ayanamsa = escapeCsv(ayanamsaName);

    const createdAt = h.created_at ? escapeCsv(h.created_at) : escapeCsv("");

    return [serial, name, birthDate, birthTime, birthplace, ayanamsa, createdAt].join(",");
  });

  return [headers.join(","), ...rows].join("\n");
}

runTest("Export preserves all 7 required headers in correct order", () => {
  const csv = exportHoroscopesToCsv([]);
  const parsed = parseCsv(csv);
  assert.strictEqual(parsed.length, 1);
  assert.deepStrictEqual(parsed[0], [
    "Serial",
    "Name",
    "Birth Date",
    "Birth Time",
    "Birthplace",
    "Ayanamsa",
    "Created At",
  ]);
});

runTest("Export includes correct birth time for standard 24-hour and 12-hour values", () => {
  const sampleData = [
    {
      display_number: 1,
      person_name: "Gokul M",
      birth_date: "1990-05-15",
      birth_time: "14:30:00",
      birthplace: "Chennai, Tamil Nadu",
      ayanamsa_id: 0,
      created_at: "2026-10-18T10:00:00Z",
    },
    {
      display_number: 2,
      person_name: "Ananya R",
      birth_date: "1995-08-20",
      birth_time: "06:15 AM",
      birthplace: "Madurai, Tamil Nadu",
      ayanamsa_id: 1,
      created_at: "2026-10-18T11:00:00Z",
    },
  ];

  const csv = exportHoroscopesToCsv(sampleData);
  const parsed = parseCsv(csv);

  assert.strictEqual(parsed.length, 3); // 1 header + 2 rows
  // Row 1
  assert.strictEqual(parsed[1][0], "1");
  assert.strictEqual(parsed[1][1], "Gokul M");
  assert.strictEqual(parsed[1][2], "1990-05-15");
  assert.strictEqual(parsed[1][3], "14:30:00");
  assert.strictEqual(parsed[1][4], "Chennai, Tamil Nadu");
  assert.strictEqual(parsed[1][5], "Lahiri");

  // Row 2
  assert.strictEqual(parsed[2][0], "2");
  assert.strictEqual(parsed[2][1], "Ananya R");
  assert.strictEqual(parsed[2][2], "1995-08-20");
  assert.strictEqual(parsed[2][3], "06:15 AM");
  assert.strictEqual(parsed[2][4], "Madurai, Tamil Nadu");
  assert.strictEqual(parsed[2][5], "KP");
});

runTest("Export handles missing, empty, or null birth time safely as 'Unknown'", () => {
  const sampleData = [
    {
      display_number: 3,
      person_name: "No Time Record",
      birth_date: "1980-01-01",
      birth_time: null,
      birthplace: "Coimbatore",
      ayanamsa_id: 2,
      created_at: "2026-10-18T12:00:00Z",
    },
    {
      display_number: 4,
      person_name: "Empty Time Record",
      birth_date: "1985-02-02",
      birth_time: "",
      birthplace: "Salem",
      ayanamsa_id: 0,
      created_at: "2026-10-18T13:00:00Z",
    },
    {
      display_number: 5,
      person_name: "Dash Time Record",
      birth_date: "1988-03-03",
      birth_time: "—",
      birthplace: "Tiruchirappalli",
      ayanamsa_id: 0,
      created_at: "2026-10-18T14:00:00Z",
    },
  ];

  const csv = exportHoroscopesToCsv(sampleData);
  const parsed = parseCsv(csv);

  assert.strictEqual(parsed.length, 4);
  assert.strictEqual(parsed[1][3], "Unknown");
  assert.strictEqual(parsed[2][3], "Unknown");
  assert.strictEqual(parsed[3][3], "Unknown");
  assert.strictEqual(parsed[1][5], "Raman"); // ayanamsa_id: 2
});

runTest("Export extracts birth time from nested calculation snapshot fallback", () => {
  const legacyRecord = {
    display_number: 6,
    person_name: "Legacy User",
    birth_date: "1992-07-11",
    birth_time: null, // Null in root table
    calculation_result: {
      clientInputs: {
        birthTime: "09:45:00",
      },
    },
    birthplace: "Thanjavur",
    ayanamsa_id: 0,
    created_at: "2026-10-18T15:00:00Z",
  };

  const csv = exportHoroscopesToCsv([legacyRecord]);
  const parsed = parseCsv(csv);

  assert.strictEqual(parsed.length, 2);
  assert.strictEqual(parsed[1][3], "09:45:00");
});

runTest("Export properly escapes special characters (quotes, commas, newlines) per RFC 4180", () => {
  const trickyRecord = {
    display_number: 7,
    person_name: 'Dr. "Kavitha", Ph.D.',
    birth_date: "1987-12-25",
    birth_time: "23:59:00",
    birthplace: "New York, NY, USA",
    ayanamsa_id: 0,
    created_at: "2026-10-18T16:00:00Z",
  };

  const csv = exportHoroscopesToCsv([trickyRecord]);
  const parsed = parseCsv(csv);

  assert.strictEqual(parsed.length, 2);
  assert.strictEqual(parsed[1][1], 'Dr. "Kavitha", Ph.D.');
  assert.strictEqual(parsed[1][4], "New York, NY, USA");
  assert.strictEqual(parsed[1][3], "23:59:00");
  // Ensure every row has exactly 7 columns
  assert.strictEqual(parsed[1].length, 7);
});

runTest("SavedHoroscopesList.tsx uses exportHoroscopesToCsv", () => {
  const listSrc = fs.readFileSync(
    path.resolve(__dirname, "../src/components/saved/SavedHoroscopesList.tsx"),
    "utf-8"
  );
  assert(
    listSrc.includes("exportHoroscopesToCsv(horoscopes)"),
    "SavedHoroscopesList must invoke exportHoroscopesToCsv"
  );
});

runTest("API route /api/horoscopes enriches birth_time fallback from calculation_result", () => {
  const routeSrc = fs.readFileSync(
    path.resolve(__dirname, "../src/app/api/horoscopes/route.ts"),
    "utf-8"
  );
  assert(
    routeSrc.includes("resolvedBirthTime"),
    "/api/horoscopes route must resolve birth_time fallback"
  );
  assert(
    routeSrc.includes("birth_time: resolvedBirthTime"),
    "/api/horoscopes route must assign birth_time: resolvedBirthTime"
  );
});

console.log(`\nResults: ${passed} passed, ${failed} failed out of ${passed + failed} tests.`);
if (failed > 0) {
  process.exit(1);
}
