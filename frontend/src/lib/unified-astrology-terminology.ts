/**
 * Gokul's Astrological Insights (GAI)
 * Centralized Unified Astrology Terminology & Customer-Facing Content Mapping.
 *
 * This module enforces Phase 2 Unified Astrology Content Architecture:
 * - Replaces author-wise and book-wise presentation with clean, professional,
 *   customer-facing unified categories.
 * - Preserves internal technical, mathematical, and algorithmic integrity.
 * - Bilingual support for English (en) and Tamil (ta).
 */

export interface UnifiedTerm {
  en: string;
  ta: string;
  descriptionEn: string;
  descriptionTa: string;
}

export const UNIFIED_ASTROLOGY_TERMS = {
  // 1. Life Milestones & Timing
  lifeMilestones: {
    en: "Major Life Milestones & Planetary Timing Analysis",
    ta: "முக்கிய வாழ்க்கை மைல்கற்கள் & கால கணிப்பு",
    descriptionEn: "Composite timing synthesis combining periodic dasha cycles, divisional charts, and major transit alignments.",
    descriptionTa: "விம்சோத்தரி தசா-புக்தி, வர்க்க சக்கரங்கள் மற்றும் முக்கிய கோச்சார கிரக நிலைகளை இணைக்கும் முழுமையான கால கணிப்பு.",
  },

  // 2. Dual Transits
  dualTransit: {
    en: "Dual Planetary Transit Alignment (Jupiter & Saturn)",
    ta: "குரு-சனி இரட்டை பெயர்ச்சி கால கணிப்பு",
    descriptionEn: "Evaluates the concurrent catalytic aspect of Jupiter and Saturn confirming the manifestation of major life events.",
    descriptionTa: "வாழ்க்கையின் முக்கிய நிகழ்வுகள் உறுதியாவதை நிர்ணயிக்கும் குரு மற்றும் சனியின் ஒருங்கிணைந்த பார்வை ஆய்வு.",
  },

  // 3. Career & Trajectory
  careerTrajectory: {
    en: "Career & Financial Trajectory Analysis",
    ta: "தொழில், அந்தஸ்து & நிதி வளர்ச்சி ஆய்வு",
    descriptionEn: "Empirically validated classical models analyzing profession, executive status, business vs service, and wealth accumulation.",
    descriptionTa: "தொழில் வாய்ப்புகள், சுயதொழில் vs உத்தியோகம், தலைமை அந்தஸ்து மற்றும் செல்வ யோகங்களை நிர்ணயிக்கும் துல்லிய ஆய்வு.",
  },

  // 4. Vitality & Constitution (Dr. Krishna Kumar compendium unified replacement)
  vitalityAssessment: {
    en: "Ayurvedic Constitution & Vitality Assessment",
    ta: "உடல்நலக் கூறுகள் & ஆயுர்வேத திரிகோண ஆய்வு",
    descriptionEn: "Synthesized classical Ayurvedic Tridosha balance (Vata, Pitta, Kapha) and organ governance mapped to planetary longitudes.",
    descriptionTa: "வாதம், பித்தம், கபம் சமநிலை மற்றும் கிரக நிலைகளின் வழியே உடல் உறுப்புகளின் ஆரோக்கியத்தை மதிப்பீடு செய்யும் முறை.",
  },

  // 5. Planetary Pathology (Heinrich Daath compendium unified replacement)
  pathologySusceptibility: {
    en: "Planetary Pathology & Physical Susceptibility Analysis",
    ta: "கிரக பாதிப்புகள் & உடல்நல எச்சரிக்கைகள்",
    descriptionEn: "Critical astronomical indications for anatomical susceptibility, periodic vulnerability, and preventative wellness safeguards.",
    descriptionTa: "உடல் உறுப்புகளின் சாத்தியமான பலவீனங்கள் மற்றும் ஆரோக்கிய பாதுகாப்பிற்கான கிரக வழிகாட்டல்கள்.",
  },

  // 6. Planetary Connectivity & Significations (Brighu Naadi compendium unified replacement)
  planetaryConnectivity: {
    en: "Planetary Connectivity & Destiny Significations",
    ta: "கிரக இணைப்புகள் & விதி பலன்கள்",
    descriptionEn: "Foundational planetary mutual aspects, directional trines, and sign connectivity revealing innate life purpose.",
    descriptionTa: "கிரகங்களின் திரிகோண சேர்க்கைகள், பரிவர்த்தனை மற்றும் திசை தொடர்புகளின் மூலம் வெளிப்படும் ஜாதகரின் வாழ்க்கை நோக்கம்.",
  },

  // 7. Matrimonial Compatibility & Matching
  marriageCompatibility: {
    en: "Comprehensive Matrimonial Compatibility & 36 Ashta Kuta",
    ta: "திருமணப் பொருத்தங்கள் & 36 அஷ்டகூட ஆய்வு",
    descriptionEn: "Classical 36-point Kuta analysis, planetary friendship, Kuja Dosha evaluation, and mutual dasha synchronicity.",
    descriptionTa: "36 அஷ்டகூடப் புள்ளிகள், கிரக மைத்ரி, செவ்வாய் தோஷ ஆய்வு மற்றும் தசா சமநிலை அடிப்படையிலான திருமணப் பொருத்தம்.",
  },

  // 8. Spouse Characteristics (Sivadasan Ravi card unified replacement)
  spouseCharacteristics: {
    en: "Spouse Characteristics & Directional Analysis",
    ta: "வாழ்க்கைத் துணைவர் குணாதிசயங்கள் & திசை கணிப்பு",
    descriptionEn: "Astrological indications of spouse's temperament, physical constitution, profession, and directional orientation.",
    descriptionTa: "வாழ்க்கைத் துணையின் குணநலன்கள், உடல் வாகு, தொழில் பின்னணி மற்றும் பூர்வீகத் திசை பற்றிய ஜோதிடக் கணிப்பு.",
  },

  // 9. Planetary Strength (Shadbala)
  planetaryStrength: {
    en: "Six-Fold Planetary Strength Analysis (Shadbala)",
    ta: "அறுவகை கிரக பலம் (ஷட்பலம்)",
    descriptionEn: "Classical quantitative planetary strength evaluation across positional, directional, temporal, motional, natural, and aspectual balas.",
    descriptionTa: "ஸ்தான, திக், கால, சேஷ்டா, நைசர்கிக மற்றும் த்ரிக் பலங்கள் வழியே கணக்கிடப்படும் கிரகங்களின் அறுவகை வலிமை.",
  },

  // 10. House Placement Predictions
  housePlacements: {
    en: "Planetary House Placement Predictions",
    ta: "பாவக கிரக நிலைகள் & பொதுப் பலன்கள்",
    descriptionEn: "Detailed life effects of planetary occupants and rulers across the twelve houses of the birth horoscope.",
    descriptionTa: "ஜாதகத்தின் 12 பாவங்களில் அமைந்துள்ள ஒன்பது கிரகங்களின் விரிவான பலன்கள் மற்றும் வாழ்க்கை வழிகாட்டல்கள்.",
  },

  // 11. Traditional Remedial Guidance (Sannu rituals explorer unified replacement)
  remedialGuidance: {
    en: "Traditional Remedial Guidance & Sanctification Directives",
    ta: "பாரம்பரிய பரிகாரங்கள் & வழிபாட்டு நெறிமுறைகள்",
    descriptionEn: "Sanctified Vedic mantras, temple pilgrimages, charity, and gemstone weight formulas harmonizing challenging planetary karmas.",
    descriptionTa: "கிரக தோஷங்களை நிவர்த்தி செய்யும் வேத மந்திரங்கள், திருத்தல வழிபாடுகள், தானங்கள் மற்றும் ரத்தின பரிந்துரைகள்.",
  },

  // 12. Current Transits
  currentTransits: {
    en: "Current Planetary Transit Alignments",
    ta: "தற்போதைய கிரகப் பெயர்ச்சி பலன்கள்",
    descriptionEn: "Real-time astronomical ephemeris transit positions overlaying the native's natal chart and active dasha period.",
    descriptionTa: "தற்போதைய கோச்சார கிரக நிலைகள் உங்கள் ஜாதகத்துடன் ஏற்படுத்தும் தொடர்புகள் மற்றும் உடனடி பலன்கள்.",
  },

  // 13. Calculation Framework (Replaces XALEN / Swiss Ephemeris)
  calculationStandard: {
    en: "High-Precision Astronomical Calculations",
    ta: "உயர் துல்லிய வானியல் கணித முறை",
    descriptionEn: "Deterministic, sub-arcsecond sidereal ephemeris algorithms computing planetary longitudes and unequal cuspal sub-divisions.",
    descriptionTa: "பூமி மைய நிராயன முறையில் துல்லியமான வினாடி அளவீடுகளுடன் கணக்கிடப்படும் வானியல் ஜோதிட சூத்திரங்கள்.",
  },
} as const;

/**
 * Returns the customer-facing label for a unified term key.
 */
export function getUnifiedLabel(
  key: keyof typeof UNIFIED_ASTROLOGY_TERMS,
  lang: "en" | "ta" = "en"
): string {
  const term = UNIFIED_ASTROLOGY_TERMS[key];
  return term ? (lang === "ta" ? term.ta : term.en) : "";
}

/**
 * Returns the customer-facing description for a unified term key.
 */
export function getUnifiedDescription(
  key: keyof typeof UNIFIED_ASTROLOGY_TERMS,
  lang: "en" | "ta" = "en"
): string {
  const term = UNIFIED_ASTROLOGY_TERMS[key];
  return term ? (lang === "ta" ? term.descriptionTa : term.descriptionEn) : "";
}
