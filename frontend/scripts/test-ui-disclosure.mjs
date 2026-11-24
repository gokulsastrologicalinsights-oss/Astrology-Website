/**
 * Automated Customer UI Disclosure Scan for GAI.
 * 
 * Scans all frontend components and pages to ensure no internal calculation engine
 * names, modern authors, or classical treatise book citations are displayed in
 * customer-facing code.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SRC_DIR = path.resolve(__dirname, '../src');

const FORBIDDEN_PATTERNS = [
  { name: 'Swiss Ephemeris', regex: /\bSwiss\s+Ephemeris\b/i },
  { name: 'XALEN', regex: /\bXALEN\b/ },
  { name: 'Marc Boney', regex: /\bMarc\s+Boney\b/i },
  { name: 'Mark Boney', regex: /\bMark\s+Boney\b/i },
  { name: 'Dr. S. Krishna Kumar', regex: /\bDr\.?\s*S\.?\s*Krishna\s*Kumar\b/i },
  { name: 'Heinrich Daath', regex: /\bHeinrich\s+D[aä]ath\b/i },
  { name: 'Sivadasan Ravi', regex: /\bSivadasan\s+Ravi\b/i },
  { name: 'Sannu Ahmed', regex: /\bSannu\s+Ahmed\b/i },
  { name: 'Picatrix', regex: /\bPicatrix\b/i },
];

function isCustomerFacingDirectory(dirPath) {
  const rel = path.relative(SRC_DIR, dirPath).replace(/\\/g, '/');
  return rel.startsWith('app') || rel.startsWith('components');
}

function scanFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n');
  const violations = [];

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i];
    const trimmed = rawLine.trim();

    // Skip comment lines and import declarations
    if (
      trimmed.startsWith('//') ||
      trimmed.startsWith('/*') ||
      trimmed.startsWith('*') ||
      trimmed.startsWith('{/*') ||
      trimmed.startsWith('import ')
    ) {
      continue;
    }

    for (const forbidden of FORBIDDEN_PATTERNS) {
      if (forbidden.regex.test(trimmed)) {
        violations.push({
          file: filePath,
          line: i + 1,
          term: forbidden.name,
          text: trimmed,
        });
      }
    }
  }

  return violations;
}

function walkDir(dir) {
  let results = [];
  const list = fs.readdirSync(dir);
  for (const file of list) {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);
    if (stat && stat.isDirectory()) {
      results = results.concat(walkDir(fullPath));
    } else if (file.endsWith('.tsx') || file.endsWith('.ts')) {
      if (isCustomerFacingDirectory(dir)) {
        results.push(fullPath);
      }
    }
  }
  return results;
}

console.log('--- Scanning Customer-Facing UI Components for Technical Disclosures ---');
const files = walkDir(SRC_DIR);
console.log(`Auditing ${files.length} customer UI files...`);

let totalViolations = 0;
for (const file of files) {
  const fileViolations = scanFile(file);
  if (fileViolations.length > 0) {
    for (const v of fileViolations) {
      console.error(`[DISCLOSURE VIOLATION] ${v.file}:${v.line} -> Found '${v.term}': "${v.text}"`);
      totalViolations++;
    }
  }
}

if (totalViolations === 0) {
  console.log(`✓ Verification Passed: 0 customer-facing disclosure violations detected across ${files.length} UI files.`);
  process.exit(0);
} else {
  console.error(`✗ Verification Failed: ${totalViolations} disclosure violations detected.`);
  process.exit(1);
}
