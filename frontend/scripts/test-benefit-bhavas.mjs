/**
 * Verification test script for Four-Category Benefit Bhavas in frontend.
 */

import {
  formatBenefitBhavas,
  calculateBenefitBhavas,
  getPlanetOwnedHouses,
  getPlanetOccupiedHouse,
  resolveStarLord,
  enrichDasaTreeWithBenefitBhavas,
  normalizePlanetName,
} from "../src/lib/benefit-bhavas.ts";

let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (condition) {
    passed++;
    console.log(`  ✓ ${message}`);
  } else {
    failed++;
    console.error(`  ✗ FAIL: ${message}`);
  }
}

console.log("=== Testing Benefit Bhavas Calculation Service (Frontend) ===");

// 1. Reference Example B: Sukran (Sun's star)
console.log("\n1. Reference Example B: Sukran (Sun's star) on Sagittarius Ascendant");
const refBContexts = {
  Sun: {
    name: "Sun",
    longitude: 245.0,
    starLord: "Ketu",
    occupiedHouse: 1,
    ownedHouses: [9],
  },
  Venus: {
    name: "Venus",
    longitude: 275.0, // Uttara Ashadha (Sun star)
    starLord: "Sun",
    occupiedHouse: 2,
    ownedHouses: [6, 11],
  },
};
const resB = calculateBenefitBhavas("Venus", refBContexts);
assert(resB.formatted === "1 | 9 | 2 | 6, 11", `Formatted is '1 | 9 | 2 | 6, 11', got '${resB.formatted}'`);
assert(resB.starLord === "Sun", "Star lord is Sun");
assert(resB.starLordOccupied === 1, "Star lord occupied is 1");
assert(JSON.stringify(resB.starLordOwned) === "[9]", "Star lord owned is [9]");
assert(resB.periodLordOccupied === 2, "Period lord occupied is 2");
assert(JSON.stringify(resB.periodLordOwned) === "[6,11]", "Period lord owned is [6, 11]");

// 2. Reference Example A: Mercury with Ketu as star lord
console.log("\n2. Reference Example A: Mercury with Ketu star lord");
const refAContexts = {
  Ketu: {
    name: "Ketu",
    longitude: 310.0,
    starLord: "Rahu",
    occupiedHouse: 3,
    ownedHouses: [],
  },
  Mercury: {
    name: "Mercury",
    longitude: 242.0, // Mula (Ketu star)
    starLord: "Ketu",
    occupiedHouse: 1,
    ownedHouses: [7, 10],
  },
};
const resA = calculateBenefitBhavas("Mercury", refAContexts);
assert(resA.formatted === "3 | 1 | 7, 10", `Formatted is '3 | 1 | 7, 10', got '${resA.formatted}'`);
assert(resA.starLord === "Ketu", "Star lord is Ketu");
assert(resA.starLordOccupied === 3, "Star lord occupied is 3");
assert(resA.starLordOwned.length === 0, "Star lord owned omitted (length 0)");
assert(resA.periodLordOccupied === 1, "Period lord occupied is 1");
assert(JSON.stringify(resA.periodLordOwned) === "[7,10]", "Period lord owned is [7, 10]");

// 3. Reference Example C: Period lord is Rahu or Ketu
console.log("\n3. Reference Example C: Rahu period lord with Mars star lord");
const refCContexts = {
  Mars: {
    name: "Mars",
    longitude: 5.0,
    starLord: "Ketu",
    occupiedHouse: 5,
    ownedHouses: [5, 12],
  },
  Rahu: {
    name: "Rahu",
    longitude: 185.0, // Chitra (Mars star)
    starLord: "Mars",
    occupiedHouse: 11,
    ownedHouses: [],
  },
};
const resC = calculateBenefitBhavas("Rahu", refCContexts);
assert(resC.formatted === "5 | 5, 12 | 11", `Formatted is '5 | 5, 12 | 11', got '${resC.formatted}'`);
assert(resC.starLordOwned.length === 2, "Star lord owned is included");
assert(resC.periodLordOwned.length === 0, "Period lord owned omitted");

// 4. Case 4: Both Rahu/Ketu
console.log("\n4. Both period lord and star lord are Rahu/Ketu");
const bothNodesContexts = {
  Rahu: {
    name: "Rahu",
    longitude: 220.0,
    starLord: "Saturn",
    occupiedHouse: 8,
    ownedHouses: [],
  },
  Ketu: {
    name: "Ketu",
    longitude: 40.0,
    starLord: "Rahu",
    occupiedHouse: 2,
    ownedHouses: [],
  },
};
const resBoth = calculateBenefitBhavas("Ketu", bothNodesContexts);
assert(resBoth.formatted === "8 | 2", `Formatted is '8 | 2', got '${resBoth.formatted}'`);

// 5. Multiple Ascendants check
console.log("\n5. Different Ascendants house ownership rules");
// Aries Ascendant
assert(JSON.stringify(getPlanetOwnedHouses("Sun", 1)) === "[5]", "Aries Asc: Sun owns house 5");
assert(JSON.stringify(getPlanetOwnedHouses("Venus", 1)) === "[2,7]", "Aries Asc: Venus owns houses 2, 7");
assert(JSON.stringify(getPlanetOwnedHouses("Mars", 1)) === "[1,8]", "Aries Asc: Mars owns houses 1, 8");
assert(JSON.stringify(getPlanetOwnedHouses("Jupiter", 1)) === "[9,12]", "Aries Asc: Jupiter owns houses 9, 12");
assert(JSON.stringify(getPlanetOwnedHouses("Saturn", 1)) === "[10,11]", "Aries Asc: Saturn owns houses 10, 11");
assert(JSON.stringify(getPlanetOwnedHouses("Rahu", 1)) === "[]", "Aries Asc: Rahu owns no houses");

// Cancer Ascendant
assert(JSON.stringify(getPlanetOwnedHouses("Moon", 4)) === "[1]", "Cancer Asc: Moon owns house 1");
assert(JSON.stringify(getPlanetOwnedHouses("Sun", 4)) === "[2]", "Cancer Asc: Sun owns house 2");
assert(JSON.stringify(getPlanetOwnedHouses("Mars", 4)) === "[5,10]", "Cancer Asc: Mars owns houses 5, 10");

// 6. All 5 Dasa Levels independent calculation
console.log("\n6. All 5 Dasa Levels independent calculation");
const tree = [
  {
    lord: "Venus",
    level: "Mahadasha",
    sub_periods: [
      {
        lord: "Sun",
        level: "Antardasha",
        sub_periods: [
          {
            lord: "Mars",
            level: "Pratyantardasha",
            sub_periods: [
              {
                lord: "Jupiter",
                level: "Sookshmadasha",
                sub_periods: [
                  {
                    lord: "Saturn",
                    level: "Pranadasha",
                  },
                ],
              },
            ],
          },
        ],
      },
    ],
  },
];

const fiveLevelContexts = {
  Venus: { name: "Venus", longitude: 275.0, starLord: "Sun", occupiedHouse: 2, ownedHouses: [6, 11] },
  Sun: { name: "Sun", longitude: 245.0, starLord: "Ketu", occupiedHouse: 1, ownedHouses: [9] },
  Mars: { name: "Mars", longitude: 5.0, starLord: "Ketu", occupiedHouse: 5, ownedHouses: [5, 12] },
  Jupiter: { name: "Jupiter", longitude: 85.0, starLord: "Jupiter", occupiedHouse: 7, ownedHouses: [1, 4] },
  Saturn: { name: "Saturn", longitude: 305.0, starLord: "Mars", occupiedHouse: 3, ownedHouses: [2, 3] },
  Ketu: { name: "Ketu", longitude: 310.0, starLord: "Rahu", occupiedHouse: 3, ownedHouses: [] },
  Rahu: { name: "Rahu", longitude: 130.0, starLord: "Venus", occupiedHouse: 9, ownedHouses: [] },
};

enrichDasaTreeWithBenefitBhavas(tree, fiveLevelContexts);

const maha = tree[0];
const antar = maha.sub_periods[0];
const praty = antar.sub_periods[0];
const sook = praty.sub_periods[0];
const prana = sook.sub_periods[0];

assert(maha.benefit_bhavas === "1 | 9 | 2 | 6, 11", "Level 1 (Maha) is 1 | 9 | 2 | 6, 11");
assert(antar.benefit_bhavas === "3 | 1 | 9", "Level 2 (Antar) is 3 | 1 | 9 (Cat 2 omitted)");
assert(praty.benefit_bhavas === "3 | 5 | 5, 12", "Level 3 (Pratyantar) is 3 | 5 | 5, 12");
assert(sook.benefit_bhavas === "7 | 1, 4 | 7 | 1, 4", "Level 4 (Sookshma) is 7 | 1, 4 | 7 | 1, 4");
assert(prana.benefit_bhavas === "5 | 5, 12 | 3 | 2, 3", "Level 5 (Prana) is 5 | 5, 12 | 3 | 2, 3");

assert(maha.benefit_bhavas !== antar.benefit_bhavas, "Child does NOT copy parent (Maha != Antar)");
assert(antar.benefit_bhavas !== praty.benefit_bhavas, "Child does NOT copy parent (Antar != Pratyantar)");
assert(praty.benefit_bhavas !== sook.benefit_bhavas, "Child does NOT copy parent (Pratyantar != Sookshma)");
assert(sook.benefit_bhavas !== prana.benefit_bhavas, "Child does NOT copy parent (Sookshma != Prana)");

// 7. Unavailable data handling
console.log("\n7. Unavailable calculation data handling");
const unavailRes = formatBenefitBhavas(null, [9], 2, [6, 11], "Sun", "Venus");
assert(unavailRes === "Unavailable | 9 | 2 | 6, 11", "Outputs Unavailable instead of inventing house number");

console.log(`\n=== RESULTS: ${passed} PASSED, ${failed} FAILED ===\n`);
if (failed > 0) process.exit(1);
