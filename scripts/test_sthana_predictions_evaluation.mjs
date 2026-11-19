// Verification script for planetary sthana predictions evaluation
import { evaluateHoroscopePlanetarySthanas } from "../frontend/src/lib/planetary-sthana-predictions.ts";

// Sample horoscope data (Mesha Lagna / Aries Ascendant)
const sampleHoroscope = {
  ascendant: {
    sign_index: 1, // Aries (மேஷம்)
    degree_in_sign: 15.2,
    degree: 15.2,
  },
  planets: [
    {
      name: "Sun",
      sign_index: 1, // Sun in 1st house (Exalted in Aries!)
      degree_in_sign: 10.0,
      is_retrograde: false,
    },
    {
      name: "Moon",
      sign_index: 4, // Moon in 4th house (Cancer - Own sign!)
      degree_in_sign: 12.5,
      is_retrograde: false,
    },
    {
      name: "Mars",
      sign_index: 10, // Mars in 10th house (Exalted in Capricorn + Digbala!)
      degree_in_sign: 28.0,
      is_retrograde: false,
    },
    {
      name: "Mercury",
      sign_index: 6, // Mercury in 6th house (Exalted in Virgo!)
      degree_in_sign: 15.0,
      is_retrograde: false,
    },
    {
      name: "Jupiter",
      sign_index: 9, // Jupiter in 9th house (Own sign Sagittarius!)
      degree_in_sign: 22.0,
      is_retrograde: false,
    },
    {
      name: "Venus",
      sign_index: 12, // Venus in 12th house (Exalted in Pisces!)
      degree_in_sign: 27.0,
      is_retrograde: false,
    },
    {
      name: "Saturn",
      sign_index: 7, // Saturn in 7th house (Exalted in Libra + Digbala!)
      degree_in_sign: 20.0,
      is_retrograde: false,
    },
    {
      name: "Rahu",
      sign_index: 3, // Rahu in 3rd house (Gemini)
      degree_in_sign: 5.0,
      is_retrograde: true,
    },
    {
      name: "Ketu",
      sign_index: 9, // Ketu in 9th house (Sagittarius)
      degree_in_sign: 5.0,
      is_retrograde: true,
    },
  ],
  shadbala: {
    planets: [
      { planet: "Sun", total_rupas: 8.5, ratio: 1.35, is_strong: true },
      { planet: "Moon", total_rupas: 7.2, ratio: 1.15, is_strong: true },
      { planet: "Mars", total_rupas: 9.1, ratio: 1.48, is_strong: true },
      { planet: "Mercury", total_rupas: 7.8, ratio: 1.18, is_strong: true },
      { planet: "Jupiter", total_rupas: 8.9, ratio: 1.32, is_strong: true },
      { planet: "Venus", total_rupas: 7.0, ratio: 1.05, is_strong: true },
      { planet: "Saturn", total_rupas: 8.4, ratio: 1.28, is_strong: true },
      { planet: "Rahu", total_rupas: 6.5, ratio: 1.0, is_strong: true },
      { planet: "Ketu", total_rupas: 6.5, ratio: 1.0, is_strong: true },
    ],
  },
};

console.log("=== Testing evaluateHoroscopePlanetarySthanas ===");
const results = evaluateHoroscopePlanetarySthanas(sampleHoroscope);

console.log(`Evaluated ${results.length} planets successfully!\n`);

for (const r of results) {
  console.log(`--- [${r.symbol} ${r.planet_name} / ${r.planet_name_ta}] ---`);
  console.log(`House: ${r.house_number} (${r.sign_name_ta} / ${r.sign_name_en})`);
  console.log(`Bhava Class: ${r.bhava_category}`);
  console.log(`Dignity: ${r.dignity_label_ta} (${r.dignity_label_en})`);
  console.log(`Shadbala: ${r.shadbala_percentage}% (Rupas: ${r.shadbala_rupas})`);
  console.log(`Verdict: ${r.status_summary_ta}`);
  console.log(`Core Traits (${r.prediction.core_traits_ta.length} points):`);
  r.prediction.core_traits_ta.slice(0, 2).forEach((pt) => console.log(`  • ${pt}`));
  console.log(`Career / Wealth (${r.prediction.career_wealth_ta.length} points):`);
  r.prediction.career_wealth_ta.slice(0, 1).forEach((pt) => console.log(`  • ${pt}`));
  console.log(`Reference: ${r.prediction.source_reference}\n`);
}
