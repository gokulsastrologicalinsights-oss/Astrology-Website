/**
 * Gokul's Astrological Insights - Tirupur S. Gopalakrishnan (Tirupur GK) Transit Engine
 *
 * Implements classical principles from:
 * 1. "Accurate Transit Predictions" (Chandra Nadi / Jyotish 2024) by Guruji Tirupur S. Gopalakrishnan (GK)
 * 2. Transit over Natal Planets (Conjunction & Degree Proximity)
 * 3. GK Specific Planetary Enmity & Friendship Matrix
 * 4. GK Special Aspects (Mars 4,7,8; Jupiter 5,7,9; Saturn 3,7,10; Rahu/Ketu 3,11 control; All 7)
 * 5. Chapter 3: Transit and Medical Treatment (Moon through Kalapurusha body parts & surgery timings)
 * 6. Principle 4: Transit = Character / Temporary Catalysts, Maha Dasha / Antar Dasha = Concrete Permanent Events
 * 7. Gochara Confluence with Dasa - Bukthi - Andhara positive percentage calculation.
 */

import { PlanetInfo, HouseInfo, AscendantInfo } from "./types";
import { LanguageCode } from "./translations";

export interface GkPlanetTransitConjunction {
  transitingPlanet: string;
  natalPlanet: string;
  signIndex: number;
  signNameEn: string;
  signNameTa: string;
  degreeOrb: number;
  isExactOrb: boolean; // <= 5 degrees
  nature: "benefic" | "caution" | "mixed";
  predictionTitleEn: string;
  predictionTitleTa: string;
  effectsEn: string[];
  effectsTa: string[];
  gkRuleQuoteEn: string;
  gkRuleQuoteTa: string;
  intensityScore: number; // -10 to +10
}

export interface GkPlanetTransitAspect {
  transitingPlanet: string;
  natalPlanet: string;
  aspectType: "4th" | "7th" | "8th" | "5th" | "9th" | "3rd" | "10th" | "control_3_11";
  effectTitleEn: string;
  effectTitleTa: string;
  descriptionEn: string;
  descriptionTa: string;
  nature: "benefic" | "caution" | "mixed";
  intensityScore: number; // -5 to +5
}

export interface GkMoonTransitMedicalAlert {
  moonSignIndex: number;
  moonSignNameEn: string;
  moonSignNameTa: string;
  vulnerableOrganEn: string;
  vulnerableOrganTa: string;
  avoidSurgeriesEn: string[];
  avoidSurgeriesTa: string[];
  medicalAdviceEn: string;
  medicalAdviceTa: string;
  safeHealingWindow: boolean;
}

export interface GkDasaTransitConfluence {
  dasaLord: string;
  bukthiLord: string;
  andharaLord?: string;
  transitScoreModifier: number; // e.g. +7% or -5%
  combinedAdjustedScore: number; // baseScore + transitScoreModifier clamped 5..98
  transitConfluenceSummaryEn: string;
  transitConfluenceSummaryTa: string;
  keyCatalystsEn: string[];
  keyCatalystsTa: string[];
}

export interface GkTransitAnalysisResult {
  calculatedAt: string;
  totalTransitingPlanets: number;
  conjunctions: GkPlanetTransitConjunction[];
  aspects: GkPlanetTransitAspect[];
  moonMedical: GkMoonTransitMedicalAlert;
  dasaConfluence?: GkDasaTransitConfluence;
  transitModifierPercent: number;
  gkCoreRuleEn: string;
  gkCoreRuleTa: string;
  summaryHighlightsEn: string[];
  summaryHighlightsTa: string[];
}

// Tirupur GK Specific Enmity Definition
export const GK_PLANETARY_ENEMIES: Record<string, string[]> = {
  Sun: ["Saturn", "Rahu", "Ketu"],
  Moon: ["Rahu", "Ketu"],
  Mars: ["Mercury", "Saturn", "Rahu", "Ketu"],
  Mercury: ["Moon", "Mars", "Rahu", "Ketu"],
  Jupiter: ["Rahu", "Ketu"],
  Venus: ["Rahu", "Ketu"],
  Saturn: ["Mars", "Rahu", "Ketu"],
  Rahu: ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Ketu"],
  Ketu: ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"],
};

export const ZODIAC_SIGNS_EN = [
  "",
  "Aries",
  "Taurus",
  "Gemini",
  "Cancer",
  "Leo",
  "Virgo",
  "Libra",
  "Scorpio",
  "Sagittarius",
  "Capricorn",
  "Aquarius",
  "Pisces",
];

export const ZODIAC_SIGNS_TA = [
  "",
  "மேஷம்",
  "ரிஷபம்",
  "மிதுனம்",
  "கடகம்",
  "சிம்மம்",
  "கன்னி",
  "துலாம்",
  "விருச்சிகம்",
  "தனுசு",
  "மகரம்",
  "கும்பம்",
  "மீனம்",
];

// Kalapurusha Body Parts for Medical & Surgery Warnings (Tirupur GK Chapter 3)
const KALAPURUSHA_MEDICAL: Record<
  number,
  {
    organEn: string;
    organTa: string;
    avoidEn: string[];
    avoidTa: string[];
    adviceEn: string;
    adviceTa: string;
  }
> = {
  1: {
    organEn: "Head, brain, skull, facial bones",
    organTa: "தலை, மூளை, மண்டை ஓடு, முக எலும்புகள்",
    avoidEn: ["Cranial surgeries", "Head/Brain procedures", "Ophthalmic head surgeries"],
    avoidTa: ["தலை/மூளை அறுவை சிகிச்சைகள்", "கபால சிகிச்சைகள்", "முக அறுவை சிகிச்சை"],
    adviceEn: "When transit Moon passes over Aries, avoid elective cranial operations; fluids are heightened in cranial capillaries.",
    adviceTa: "சந்திரன் மேஷத்தில் சஞ்சரிக்கும் போது தலை மற்றும் மூளை அறுவை சிகிச்சைகளை தள்ளி வைப்பது சிறப்பு.",
  },
  2: {
    organEn: "Throat, neck, thyroid, vocal cords, tonsils",
    organTa: "தொண்டை, கழுத்து, தைராய்டு, குரல்வளை, டான்சில்",
    avoidEn: ["Thyroidectomy", "Tonsil surgery", "Vocal cord operations"],
    avoidTa: ["தைராய்டு அறுவை சிகிச்சை", "தொண்டை/டான்சில் சிகிச்சை", "குரல்வளை அறுவை சிகிச்சை"],
    adviceEn: "Avoid throat and thyroid elective surgeries while Moon transits Taurus.",
    adviceTa: "ரிஷப ராசியில் சந்திரன் செல்லும் போது தொண்டை மற்றும் தைராய்டு அறுவை சிகிச்சைகளை தவிர்க்கவும்.",
  },
  3: {
    organEn: "Shoulders, arms, upper bronchial tubes, collarbone",
    organTa: "தோள்பட்டை, கைகள், மூச்சுக்குழாய், நரம்பு மண்டலம்",
    avoidEn: ["Shoulder reconstruction", "Bronchial surgery", "Arm/clavicle operations"],
    avoidTa: ["தோள்பட்டை அறுவை சிகிச்சை", "மூச்சுக்குழாய் சிகிச்சை", "கை எலும்பு சிகிச்சை"],
    adviceEn: "Avoid elective operations on shoulders, respiratory bronchi, and nervous pathways in arms.",
    adviceTa: "மிதுன ராசியில் சந்திரன் உள்ள போது தோள்பட்டை மற்றும் மூச்சுக்குழாய் சிகிச்சைகளை தவிர்க்கவும்.",
  },
  4: {
    organEn: "Chest, breasts, lungs, upper stomach lining",
    organTa: "மார்பு, நுரையீரல், மார்பகங்கள், மேல் இரைப்பை",
    avoidEn: ["Thoracic surgeries", "Breast operations", "Pleural fluid procedures"],
    avoidTa: ["மார்பு அறுவை சிகிச்சை", "மார்பக சிகிச்சை", "நுரையீரல் திரவ அறுவை சிகிச்சை"],
    adviceEn: "Thoracic and breast procedures should not be scheduled during Cancer Moon transit; fluid retention peaks.",
    adviceTa: "கடக ராசியில் சந்திரன் சஞ்சரிக்கும் போது மார்பு மற்றும் நுரையீரல் அறுவை சிகிச்சைகளை தவிர்க்கவும்.",
  },
  5: {
    organEn: "Stomach, naval, umbilical cord, solar plexus, upper spine",
    organTa: "வயிற்றுப்பகுதி, தொப்புள், இரைப்பை, முதுகுத்தண்டு",
    avoidEn: ["Stomach surgeries", "Umbilical/naval procedures", "Upper gastric operations"],
    avoidTa: ["வயிற்று அறுவை சிகிச்சை", "தொப்புள் கொடி சீரமைப்பு", "இரைப்பை அறுவை சிகிச்சை"],
    adviceEn: "Stomach, large intestine, naval, and umbilical cord operations must not be undertaken while Moon transits Leo.",
    adviceTa: "சிம்ம ராசியில் சந்திரன் செல்லும் போது வயிறு, தொப்புள் மற்றும் இரைப்பை அறுவை சிகிச்சைகளை கண்டிப்பாக தவிர்க்க வேண்டும்.",
  },
  6: {
    organEn: "Lower abdomen, intestines, appendix, digestive tract",
    organTa: "கீழ் வயிறு, குடல் பகுதிகள், குடல்வால் (அப்பன்டிக்ஸ்)",
    avoidEn: ["Intestinal resection", "Elective appendectomy", "Colon surgeries"],
    avoidTa: ["குடல் அறுவை சிகிச்சை", "அப்பன்டிக்ஸ் சிகிச்சை", "செரிமான மண்டல சிகிச்சை"],
    adviceEn: "Avoid elective intestinal and digestive tract operations during Virgo Moon transit.",
    adviceTa: "கன்னி ராசியில் சந்திரன் செல்லும் போது குடல் மற்றும் குடல்வால் அறுவை சிகிச்சைகளை தவிர்க்கவும்.",
  },
  7: {
    organEn: "Kidneys, lumbar region, lower back, adrenal glands",
    organTa: "சிறுநீரகங்கள் (Kidneys), கீழ் முதுகு, இடுப்பு பகுதி",
    avoidEn: ["Kidney stone removals", "Renal surgeries", "Lumbar back surgeries"],
    avoidTa: ["சிறுநீரக கல் அகற்றுதல்", "சிறுநீரக அறுவை சிகிச்சை", "இடுப்பு எலும்பு சிகிச்சை"],
    adviceEn: "Avoid elective renal and lumbar procedures during Libra Moon transit.",
    adviceTa: "துலாம் ராசியில் சந்திரன் செல்லும் போது சிறுநீரகம் மற்றும் இடுப்பு அறுவை சிகிச்சைகளை தள்ளி வைக்கவும்.",
  },
  8: {
    organEn: "Genitals, rectum, uterus, prostate, excretory organs",
    organTa: "இனப்பெருக்க உறுப்புகள், கர்ப்பப்பை, மலக்குடல், புரோஸ்டேட்",
    avoidEn: ["Uterus operations (Hysterectomy)", "Rectum/piles surgeries", "Prostate procedures"],
    avoidTa: ["கர்ப்பப்பை அறுவை சிகிச்சை", "மலக்குடல்/மூல நோய் சிகிச்சை", "புரோஸ்டேட் அறுவை சிகிச்சை"],
    adviceEn: "Abdomen, uterus, rectum, and prostate surgeries must not be carried out while Moon transits Scorpio; complications remain lingering.",
    adviceTa: "விருச்சிக ராசியில் சந்திரன் செல்லும் போது கர்ப்பப்பை, மலக்குடல், மற்றும் மூல அறுவை சிகிச்சைகளை கண்டிப்பாக செய்யக்கூடாது.",
  },
  9: {
    organEn: "Thighs, hips, arterial system, femoral vessels",
    organTa: "தொடைகள், இடுப்பு மூட்டு, தமனி ரத்த நாளங்கள்",
    avoidEn: ["Hip replacements", "Femoral artery procedures", "Thigh surgeries"],
    avoidTa: ["இடுப்பு மூட்டு மாற்று அறுவை சிகிச்சை", "தொடை நரம்பு அறுவை சிகிச்சை"],
    adviceEn: "Avoid hip joint replacement and femoral operations during Sagittarius Moon transit.",
    adviceTa: "தனுசு ராசியில் சந்திரன் செல்லும் போது இடுப்பு மூட்டு மற்றும் தொடை அறுவை சிகிச்சைகளை தவிர்க்கவும்.",
  },
  10: {
    organEn: "Knees, joint caps, skeletal kneecap, skin barriers",
    organTa: "முழங்கால்கள், மூட்டு சில்லுகள், எலும்பு மூட்டுகள்",
    avoidEn: ["Knee replacement surgeries", "Patellar tendon procedures", "Joint arthroscopies"],
    avoidTa: ["முழங்கால் மூட்டு மாற்று சிகிச்சை", "மூட்டு சில்லு அறுவை சிகிச்சை"],
    adviceEn: "Knee and major bone joint surgeries should not be scheduled during Capricorn Moon transit.",
    adviceTa: "மகர ராசியில் சந்திரன் செல்லும் போது முழங்கால் மூட்டு அறுவை சிகிச்சைகளை தவிர்க்க வேண்டும்.",
  },
  11: {
    organEn: "Calves, shins, ankles, lower leg circulation",
    organTa: "கால் கெண்டை கால்கள், கணுக்கால்கள், ரத்த ஓட்ட நாளங்கள்",
    avoidEn: ["Ankle reconstructions", "Varicose vein stripping", "Achilles surgeries"],
    avoidTa: ["கணுக்கால் அறுவை சிகிச்சை", "வெரிகோஸ் வெயின் சிகிச்சை", "கால் தசைநார் அறுவை சிகிச்சை"],
    adviceEn: "Avoid elective operations on ankles and lower leg veins during Aquarius Moon transit.",
    adviceTa: "கும்ப ராசியில் சந்திரன் செல்லும் போது கணுக்கால் மற்றும் ரத்த நாள அறுவை சிகிச்சைகளை தவிர்க்கவும்.",
  },
  12: {
    organEn: "Feet, toes, lymphatic nodes, immune fluid balance",
    organTa: "பாதங்கள், கால் விரல்கள், நிணநீர் மண்டலம்",
    avoidEn: ["Foot reconstructions", "Lymph node biopsies", "Toe orthopedic surgeries"],
    avoidTa: ["பாத அறுவை சிகிச்சைகள்", "நிணநீர் சுரப்பி சிகிச்சை", "கால் விரல் எலும்பு சிகிச்சை"],
    adviceEn: "Avoid foot and lymphatic operations during Pisces Moon transit.",
    adviceTa: "மீன ராசியில் சந்திரன் செல்லும் போது பாதங்கள் மற்றும் கால் விரல் அறுவை சிகிச்சைகளை தவிர்க்கவும்.",
  },
};

// Tirupur GK Specific Conjunction Interpretations (Transiting Planet over Natal Planet)
interface GkConjunctionEntry {
  titleEn: string;
  titleTa: string;
  nature: "benefic" | "caution" | "mixed";
  intensity: number;
  effectsEn: string[];
  effectsTa: string[];
  quoteEn: string;
  quoteTa: string;
}

const GK_CONJUNCTION_DATABASE: Record<string, Record<string, GkConjunctionEntry>> = {
  Sun: {
    Saturn: {
      titleEn: "Transit Sun over Natal Saturn: Conflict between Authority & Subordinate",
      titleTa: "கோச்சார சூரியன் மீது ஜனன சனி: மேலதிகாரி மற்றும் பணியாளர் மோதல்",
      nature: "caution",
      intensity: -4,
      effectsEn: [
        "Sun represents superiors, managers, and government; Saturn represents subordinates and workers.",
        "Superiors will extract intensive work and enforce strict discipline, causing workplace friction.",
        "Delays in official approvals; karma-related responsibilities must be handled with utmost diligence.",
        "Watch for bone stiffness, fatigue, eye strain, or misunderstandings with elderly fatherly figures.",
      ],
      effectsTa: [
        "சூரியன் அதிகாரத்தையும் மேலதிகாரியையும் குறிக்கிறது; சனி பணியாளரையும் உழைப்பையும் குறிக்கிறது.",
        "பணியிடத்தில் மேலதிகாரிகள் கடுமையான வேலைச்சுமையை கொடுத்து அழுத்தம் தருவார்கள்.",
        "அரசு காரியங்கள் மற்றும் அதிகாரப்பூர்வ அனுமதிகளில் சிறு தாமதங்கள் ஏற்படும்; கடமைகளில் விழிப்புணர்வு தேவை.",
        "எலும்பு சோர்வு, கண் எரிச்சல் மற்றும் தந்தை வழியில் கருத்து வேறுபாடுகள் வரலாம்.",
      ],
      quoteEn: "Sun will extract work from Saturn and boss over it. The native will face challenges from superiors.",
      quoteTa: "சூரியன் சனியிடமிருந்து வேலை வாங்கி ஆதிக்கம் செலுத்துவார். மேலதிகாரிகளால் தொல்லைகள் வர வாய்ப்புண்டு.",
    },
    Moon: {
      titleEn: "Transit Sun over Natal Moon: Ego Waves & Maternal Management",
      titleTa: "கோச்சார சூரியன் மீது ஜனன சந்திரன்: மன அலைச்சல் மற்றும் தாய் வழி மேலாண்மை",
      nature: "mixed",
      intensity: 1,
      effectsEn: [
        "Mother's management involvement increases; family administrative matters take center stage.",
        "Mental restlessness and fluctuations of ego; skin sensitivity or body warmth.",
        "Rapid official interactions and travel proposals begin to take shape.",
      ],
      effectsTa: [
        "தாயாரின் குடும்ப நிர்வாக பொறுப்புகள் அதிகரிக்கும்; தந்தை வழியில் சில அமைதியின்மை உண்டாகலாம்.",
        "மனதில் அலைபாயும் எண்ணங்கள், தோல் உணர்திறன் மற்றும் உடல் உஷ்ணம் அதிகரிக்கும்.",
        "அதிகாரப்பூர்வ தொடர்புகள் மற்றும் பயண திட்டங்கள் உருவாகும்.",
      ],
      quoteEn: "Mother's management capacities will increase; imaginations and worries haunt the native.",
      quoteTa: "தாயாரின் நிர்வாகத் திறன் வெளிப்படும்; மன கற்பனைகளும் கவலைகளும் எழும்.",
    },
    Mars: {
      titleEn: "Transit Sun over Natal Mars: Heroic Drive, Loans & Property Progress",
      titleTa: "கோச்சார சூரியன் மீது ஜனன செவ்வாய்: வீரம், சொத்து கடன் யோகம் மற்றும் சகோதர கௌரவம்",
      nature: "benefic",
      intensity: 6,
      effectsEn: [
        "Elders who were distant or aggrieved will reconcile and visit the native.",
        "Loans applied against house/land properties will fructify successfully.",
        "Elder siblings and brothers gain prestige, public recognition, and praise from superiors.",
        "Avoid fiery arguments; channeling energy into construction or technical pursuits yields triumphs.",
      ],
      effectsTa: [
        "பிரிந்து சென்ற பெரியோர்கள் மற்றும் உறவினர்கள் மீண்டும் வந்து நல்லுறவை நாடுவார்கள்.",
        "வீடு மற்றும் நில சொத்துக்களின் மீதான கடன் உதவிகள் எதிர்பார்த்தபடி நிறைவேறும்.",
        "உடன் பிறந்த சகோதரர்களுக்கு உயர் பதவி, கௌரவம் மற்றும் அதிகாரிகளின் ஆதரவு கிடைக்கும்.",
        "கோபத்தை தவிர்த்து, நிலம் மற்றும் தொழில்நுட்ப பணிகளில் ஈடுபட்டால் பெரும் வெற்றி நிச்சயம்.",
      ],
      quoteEn: "Expected loans against property fructify; elder siblings receive high honor and official backing.",
      quoteTa: "சொத்து மீதான கடன் நிறைவேறும்; சகோதரர்களுக்கு கௌரவமும் அதிகாரிகளின் நன்மதிப்பும் கிட்டும்.",
    },
    Mercury: {
      titleEn: "Transit Sun over Natal Mercury: Intellectual Awakening & Commercial Review",
      titleTa: "கோச்சார சூரியன் மீது ஜனன புதன்: புத்தி கூர்மை, கல்வி முன்னேற்றம் மற்றும் வியாபார பேச்சு",
      nature: "benefic",
      intensity: 5,
      effectsEn: [
        "Students and professionals experience rapid mental sharpness and brisk academic grasp.",
        "Commercial contracts, accounting books, and legal documents receive executive review.",
        "Romantic interests in office/educational environments will face strict scrutiny by administrators.",
      ],
      effectsTa: [
        "மாணவர்கள் மற்றும் ஆய்வாளர்களுக்கு படிப்பில் விரைவான கிரகண சக்தியும் புத்தி கூர்மையும் உண்டாகும்.",
        "வியாபார ஒப்பந்தங்கள், கணக்கு வழக்குகள் மற்றும் ஆவணங்கள் அதிகாரிகளால் ஆராயப்படும்.",
        "பணியிடம் அல்லது கல்வி நிறுவனங்களில் உள்ள காதல் விவகாரங்கள் பெரியவர்களின் கண்காணிப்புக்கு உள்ளாகும்.",
      ],
      quoteEn: "Students will be induced to brisk learning; administrators monitor communications closely.",
      quoteTa: "படிக்கும் ஆர்வமும் புத்தி கூர்மையும் அதிகரிக்கும்; வணிக மற்றும் கல்வி முயற்சிகள் சிறக்கும்.",
    },
    Jupiter: {
      titleEn: "Transit Sun over Natal Jupiter: Spiritual Radiance & Divine Favor",
      titleTa: "கோச்சார சூரியன் மீது ஜனன குரு: குருவருள், ஆன்மிக நாட்டம் மற்றும் கௌரவ உயர்வு",
      nature: "benefic",
      intensity: 8,
      effectsEn: [
        "The soul indicator (Sun) unites with the devotion/wisdom indicator (Jupiter).",
        "Adoption of sacred spiritual paths, visiting preceptors, receiving blessings from noble guides.",
        "Promotion to advisory roles, ethical leadership recognition, and expansion of respect.",
      ],
      effectsTa: [
        "ஆத்மகாரக சூரியன் ஞானகாரக குருவுடன் இணைகிறார்; ஆன்மிக நாட்டம் மற்றும் தெய்வ பக்தி மேலோங்கும்.",
        "பெரியோர்கள் மற்றும் குருமார்களின் ஆசிர்வாதம் கிடைக்கும்; உயரிய ஆலோசனைப் பொறுப்புகள் கிட்டும்.",
        "சமூகத்தில் மதிப்பும் மரியாதையும் உயரும்; அரசு மற்றும் அதிகாரிகளால் மேன்மை உண்டாகும்.",
      ],
      quoteEn: "Sun and Jupiter are trinal friends; native adopts devotion, wisdom, and gains honors.",
      quoteTa: "சூரியனும் குருவும் நட்பு கிரகங்கள்; ஆன்மிக நன்மைகளும் கௌரவ உயர்வும் ஏற்படும்.",
    },
    Venus: {
      titleEn: "Transit Sun over Natal Venus: Royal Luxuries & Financial Outlays",
      titleTa: "கோச்சார சூரியன் மீது ஜனன சுக்கிரன்: ஆடம்பர செலவுகள் மற்றும் சமூக அலங்காரம்",
      nature: "mixed",
      intensity: 2,
      effectsEn: [
        "Expenditure on status symbols, luxury clothing, vehicles, or decorative items.",
        "Heat meets financial elegance: swift spending that requires balancing the budget.",
        "Pleasurable social engagements, diplomatic interactions, and romantic vanity.",
      ],
      effectsTa: [
        "கௌரவத்திற்காக ஆடம்பர பொருட்கள், உடைகள் மற்றும் வாகனங்களுக்கு பணச்செலவு ஏற்படும்.",
        "பண வரவு இருந்தாலும் அதைவிட செலவுகள் விரைவாகக் கரையும்; பட்ஜெட்டில் கவனம் தேவை.",
        "சமூக விசேஷங்களில் முக்கியத்துவம் பெறுதல் மற்றும் அலங்கார ஈடுபாடு அதிகரிக்கும்.",
      ],
      quoteEn: "Travel of planet of heat over planet of money causes transient expenditures.",
      quoteTa: "உஷ்ண கிரகம் சுக்கிரனின் மீது செல்வதால் விரைவான ஆடம்பர விரயங்கள் உண்டாகும்.",
    },
    Rahu: {
      titleEn: "Transit Sun over Natal Rahu: Eclipse Friction & Sudden Turning Points",
      titleTa: "கோச்சார சூரியன் மீது ஜனன ராகு: கிரகண தோஷம், அதிகார உரசல் மற்றும் திடீர் திருப்பங்கள்",
      nature: "caution",
      intensity: -5,
      effectsEn: [
        "Collision of natural arch-enemies; challenges to reputation, father's health, or executive standing.",
        "Illusory ambitions or deceptive foreign opportunities; verify all legal documents twice.",
        "Avoid clashes with governmental authorities and law enforcement during this 30-day window.",
      ],
      effectsTa: [
        "இயற்கை பகை கிரகங்களின் மோதல்; தந்தை வழி உடல்நிலை மற்றும் நற்பெயரில் கவனம் தேவை.",
        "போலியான வெளிநாட்டு கவர்ச்சிகள் அல்லது தவறான ஆலோசனைகளை நம்பி ஏமாற வேண்டாம்.",
        "அரசு அதிகாரிகளுடன் தேவையற்ற வாக்குவாதங்களை தவிர்ப்பது மிகவும் நன்று.",
      ],
      quoteEn: "Collision of inimical planets impacts native and imparts turbulent temper on Sun's karakatvas.",
      quoteTa: "பகை கிரகங்கள் மோதுவதால் சூரிய காரகத்துவங்களில் மன அழுத்தமும் திடீர் மாற்றங்களும் வரும்.",
    },
    Ketu: {
      titleEn: "Transit Sun over Natal Ketu: Ego Sublimation & Ascetic Insight",
      titleTa: "கோச்சார சூரியன் மீது ஜனன கேது: அகந்தை அடக்கம், ஆன்மிக ஞானம் மற்றும் தனிமை நாட்டம்",
      nature: "mixed",
      intensity: 1,
      effectsEn: [
        "Detachment from mundane titles and power; strong pull toward meditation, temples, and philosophy.",
        "Subtle physical fatigue, low energy in heart/eyes; need for restorative pranayama.",
        "Ancestral karmas surface to be healed; peace found in charity and seclusion.",
      ],
      effectsTa: [
        "பதவி மற்றும் புகழின் மீதான ஆசை குறையும்; ஆன்மிகம், ஆலய தரிசனம் மற்றும் தியானத்தில் அமைதி கிட்டும்.",
        "உடல் ஆற்றலில் சற்றே மந்தம் ஏற்படலாம்; கண் மற்றும் இதய ஆரோக்கியத்தில் மிதமான ஓய்வு தேவை.",
        "முன்னோர் ஆசிகள் மற்றும் தர்ம காரியங்கள் மூலம் கர்ம வினைகள் நீங்கும்.",
      ],
      quoteEn: "Inimical collision imparts spiritual detachment compulsorily on the native.",
      quoteTa: "சூரியனுடன் கேது இணையும் போது உலக ஆசைகள் விலகி ஆன்மிக முதிர்ச்சி உண்டாகும்.",
    },
  },

  Mars: {
    Sun: {
      titleEn: "Transit Mars over Natal Sun: Dynamic Combustion & Authority Clashes",
      titleTa: "கோச்சார செவ்வாய் மீது ஜனன சூரியன்: அதிகப்படியான வீரியம் மற்றும் தந்தை/அதிகார உரசல்",
      nature: "mixed",
      intensity: 2,
      effectsEn: [
        "Warrior energy blends with royal fire: heightened ambition, courage, and executive drive.",
        "Risk of friction with fathers, bosses, or government agencies; avoid impulsiveness.",
        "High body temperature, inflammatory blood rush; physical exercise is essential.",
      ],
      effectsTa: [
        "வீரியமும் அதிகாரமும் இணையும் காலம்; அபார துணிச்சலும் செயலாற்றலும் வெளிப்படும்.",
        "தந்தை மற்றும் உயரதிகாரிகளுடன் தேவையற்ற வாக்குவாதம் வரலாம்; நிதானம் மிக முக்கியம்.",
        "உடல் உஷ்ணம் மற்றும் ரத்த ஓட்டம் அதிகரிக்கும்; உடற்பயிற்சி மூலம் ஆற்றலை சமப்படுத்தவும்.",
      ],
      quoteEn: "Transit of monthly planet over another monthly planet; rapid surge in assertive courage.",
      quoteTa: "அதிவேக கிரகங்களின் சேர்க்கை; வீரியமும் துணிச்சலும் அதிகரித்தாலும் பொறுமை அவசியம்.",
    },
    Moon: {
      titleEn: "Transit Mars over Natal Moon: Impatience, Blood Pressure & Property Urgency",
      titleTa: "கோச்சார செவ்வாய் மீது ஜனன சந்திரன்: ரத்த அழுத்த அவசரம் மற்றும் மன உளைச்சல்",
      nature: "caution",
      intensity: -4,
      effectsEn: [
        "Mars debilitates in Moon's Cancer, while Moon debilitates in Mars' Scorpio: volatile sensitivity.",
        "Spouses or maternal figures face stress or public humiliation if provoked.",
        "Blood pressure spikes, digestive acidity, urgency in transactions, and hasty driving risks.",
        "Avoid water-related recklessness; do not make emotional real estate agreements.",
      ],
      effectsTa: [
        "சந்திரனின் கடகத்தில் செவ்வாய் நீசமும், செவ்வாயின் விருச்சிகத்தில் சந்திரன் நீசமும் அடைவர்; உணர்ச்சி மோதல் காலம்.",
        "மனைவி அல்லது தாயாருக்கு மன உளைச்சல் வரலாம்; தேவையற்ற ஆத்திரங்களை தவிர்க்கவும்.",
        "ரத்த அழுத்தம் மற்றும் படபடப்பு ஏற்படலாம்; வாகன பயணங்களில் மித வேகம் அவசியம்.",
        "சொத்து விவகாரங்களில் அவசர முடிவுகளை தவிர்ப்பது நல்லது.",
      ],
      quoteEn: "Husband of female native faces humiliation; brothers face testing circumstances.",
      quoteTa: "குடும்பத்தில் உணர்ச்சிவசப்படாமல் நிதானத்தை கடைப்பிடிக்க வேண்டிய கோச்சார காலம்.",
    },
    Mars: {
      titleEn: "Transit Mars over Natal Mars: Double Warrior Return & Mechanical Triumph",
      titleTa: "கோச்சார செவ்வாய் மீது ஜனன செவ்வாய்: செவ்வாய் திரும்புதல் மற்றும் இயந்திர சாதனை",
      nature: "benefic",
      intensity: 6,
      effectsEn: [
        "Administrative power and executive drive double; technical leadership shines.",
        "Success in sports, gym, surgery, machinery, military, or civil construction.",
        "If afflicted, avoid rash brawls and handle sharp tools or heavy machinery carefully.",
      ],
      effectsTa: [
        "நிர்வாகத் திறனும் வேகமும் இருமடங்காக உயரும்; தொழில்நுட்பத்தில் சாதனை படைக்கலாம்.",
        "விளையாட்டு, இயந்திரவியல், அறுவை சிகிச்சை மற்றும் கட்டிட பணிகளில் மகத்தான வெற்றி.",
        "ஆயுதங்கள், கூர்மையான பொருட்கள் மற்றும் வாகனங்களை கவனமாக கையாள வேண்டும்.",
      ],
      quoteEn: "Administrative capacity increases multifold; handle machinery and temper with discipline.",
      quoteTa: "நிர்வாக பலம் அதிகரிக்கும்; அதே சமயம் ஆத்திரத்தை கட்டுப்படுத்துவது வெற்றியை தரும்.",
    },
    Mercury: {
      titleEn: "Transit Mars over Natal Mercury: Stagnation in Romance & Brokerage Boom",
      titleTa: "கோச்சார செவ்வாய் மீது ஜனன புதன்: காதல் முடிவுகளில் தேக்கம் மற்றும் தரகு/நில லாபம்",
      nature: "mixed",
      intensity: 3,
      effectsEn: [
        "Mercury denotes the lover/intellect and Mars denotes brother/combat: romantic friction.",
        "Testing time for young lovers and youth; temporary delays in marriage finalization.",
        "Tremendous boom for real estate brokers, land promoters, construction dealers, and bankers.",
        "Sharp verbal arguments; transform critical wit into mathematical or engineering success.",
      ],
      effectsTa: [
        "காதல் விவகாரங்கள் மற்றும் திருமண முடிவுகளில் சிறு முட்டுக்கட்டைகள் அல்லது காலதாமதம் எழும்.",
        "நில வியாபாரிகள், புரோக்கர்கள், ரியல் எஸ்டேட் மற்றும் வங்கித் துறையினருக்கு அபார லாபம் கிடைக்கும்.",
        "சொந்த நிலம் உள்ளவர்கள் புதிய கட்டிட பணிகளை துவக்கலாம்; பேச்சில் முன்கோபத்தை தவிர்க்கவும்.",
      ],
      quoteEn: "Stagnation in marriage decisions, yet gives beneficial results to land promoters and banking.",
      quoteTa: "திருமண பேச்சில் தேக்கம் வந்தாலும், நில வியாபாரம் மற்றும் வங்கி துறையில் நல்ல முன்னேற்றம்.",
    },
    Jupiter: {
      titleEn: "Transit Mars over Natal Jupiter: Guru-Mangala Yoga & Property Renovation",
      titleTa: "கோச்சார செவ்வாய் மீது ஜனன குரு: குரு-மங்கள யோகம், புதிய சொத்து யோகம் மற்றும் அதிகாரம்",
      nature: "benefic",
      intensity: 9,
      effectsEn: [
        "Auspicious trinal friendship: monthly action planet passes over the yearly wealth preceptor.",
        "Acquisition of prime real estate, new houses, or extensive renovation of ancestral property.",
        "Income floods from land, agriculture, and construction contracts; meeting hierarchy leaders.",
        "In female horoscopes, estranged husbands visit lovingly to reconcile with children.",
        "Watch for minor muscle twisting/cramps; overall highly rewarding period.",
      ],
      effectsTa: [
        "குரு மங்கள யோக காலம்; நிலம், வீடு அல்லது பூர்வீக சொத்துக்களை வாங்குதல் மற்றும் புதுப்பித்தல் யோகம்.",
        "உயர் பதவியில் உள்ள அதிகாரிகளின் சந்திப்பு ஆதாயம் தரும்; அரசு வழியில் முன்னேற்றம்.",
        "பிரிந்த தம்பதிகள் மீண்டும் ஒன்று சேர நல்ல வாய்ப்புகள் உருவாகும்.",
        "தசைப்பிடிப்பு போன்ற சிறு உபாதைகள் வந்தாலும், நிதி மற்றும் சொத்து விஷயத்தில் பொற்காலம்.",
      ],
      quoteEn: "Mars travels over Jupiter: native renovates ancestral properties, acquires new lands, meets hierarchy.",
      quoteTa: "குரு மீது செவ்வாய் செல்வது மங்களகரமானது; புதிய நிலம் மற்றும் சொத்து சேர்க்கை உண்டாகும்.",
    },
    Venus: {
      titleEn: "Transit Mars over Natal Venus: Two Kalathra Karakas Unite & Passion Rejuvenation",
      titleTa: "கோச்சார செவ்வாய் மீது ஜனன சுக்கிரன்: களத்திர காரக சேர்க்கை மற்றும் தாம்பத்ய இணக்கம்",
      nature: "benefic",
      intensity: 7,
      effectsEn: [
        "Meeting of the two prime relationship karakas: romantic magnetism surges to its peak.",
        "Estranged husbands and wives feel drawn together; golden time for matrimonial reconciliation.",
        "High expenditure on luxury comfort, jewelry, perfumes, and intimate celebrations.",
        "Energy must be channeled into loving artistic creation rather than possessive jealousy.",
      ],
      effectsTa: [
        "இரு களத்திர காரகர்கள் இணைகிறார்கள்; கணவன்-மனைவி இடையே ஈர்ப்பும் அன்பும் அதிகரிக்கும்.",
        "கருத்து வேறுபாட்டால் பிரிந்த தம்பதிகள் மீண்டும் இணைந்து வாழ நல்ல சமரச பேச்சுக்கள் நடக்கும்.",
        "ஆடை, ஆபரணம், சுகபோகங்கள் மற்றும் கலை ரசனையில் அதிக ஆர்வம் உண்டாகும்.",
      ],
      quoteEn: "Meeting of two Kalathra Karaka lords: husband and wife will be deeply attracted and unite.",
      quoteTa: "இரு களத்திர கிரகங்களின் சேர்க்கை; தாம்பத்திய ஒற்றுமையும் காதலும் சிறந்து விளங்கும்.",
    },
    Saturn: {
      titleEn: "Transit Mars over Natal Saturn: Kalapurusha 8th & 11th Lords Clash",
      titleTa: "கோச்சார செவ்வாய் மீது ஜனன சனி: காலபுருஷ 8 மற்றும் 11-ம் அதிபதிகள் மோதல்",
      nature: "caution",
      intensity: -5,
      effectsEn: [
        "Mars (8th lord) collides with Saturn (11th lord): mechanical breakdowns and structural friction.",
        "Labor strikes, factory machine repairs, or disputes with contractors; patience is mandatory.",
        "High risk of muscular sprains, joint injuries, or accidents if rushing in traffic.",
        "Triumph occurs only when the native applies disciplined perseverance and avoids wrath.",
      ],
      effectsTa: [
        "அஷ்டமாதிபதி செவ்வாயும் பாதகாதிபதி சனியும் மோதுவதால் வேலைகளில் திடீர் தடைகளும் இயந்திர பழுதுகளும் வரலாம்.",
        "தொழிலாளர்கள், ஒப்பந்தக்காரர்களுடன் கருத்து வேறுபாடுகள் எழும்; அமைதி காப்பது அவசியம்.",
        "மூட்டு பிடிப்பு, விபத்து அபாயங்கள் உள்ளதால் வாகனங்களை மிக எச்சரிக்கையுடன் இயக்கவும்.",
        "விடாமுயற்சியும் நிதானமும் இருந்தால் மட்டுமே இந்த காலத்தின் சோதனைகளை கடக்க முடியும்.",
      ],
      quoteEn: "Transit of Ashtamathipathi Mars over Bhadagathipathi Saturn: industrial and joint challenges.",
      quoteTa: "செவ்வாய் சனி சேர்க்கை; தொழிற்சாலை மற்றும் இயந்திர பணிகளில் கவனமும் விழிப்புணர்வும் தேவை.",
    },
    Rahu: {
      titleEn: "Transit Mars over Natal Rahu: Explosive Angaraka Energy & Tech Breakthroughs",
      titleTa: "கோச்சார செவ்வாய் மீது ஜனன ராகு: அங்காரக ராகு சேர்க்கை மற்றும் அதிவேக திருப்பம்",
      nature: "caution",
      intensity: -6,
      effectsEn: [
        "Volatile technical firepower; breakthroughs in AI, coding, electricity, or heavy chemicals.",
        "Risk of rash outbursts, sudden collisions, fire hazards, or legal friction.",
        "Drive carefully and do not engage with shady intermediaries or dangerous machinery.",
      ],
      effectsTa: [
        "அங்காரக ராகு சேர்க்கை; மின்சாரம், ரசாயனம் மற்றும் கணினி மென்பொருள் துறையில் தீவிர வேகம்.",
        "தீடீர் ஆத்திரம், தீ விபத்து அல்லது விபத்து அபாயங்கள் உள்ளதால் மிகுந்த நிதானம் தேவை.",
        "சட்டத்திற்கு புறம்பான நபர்களுடன் பழக்கத்தை தவிர்த்து அமைதியாக இருக்கவும்.",
      ],
      quoteEn: "Mars afflicted by Rahu triggers volatile events; extreme caution in driving and heat.",
      quoteTa: "அங்காரக யோகம்; வாகன ஓட்டுதலிலும் நெருப்பு சம்பந்தப்பட்ட விஷயங்களிலும் அதீத கவனம் தேவை.",
    },
    Ketu: {
      titleEn: "Transit Mars over Natal Ketu: Surgical Precision & Spiritual Laser Drive",
      titleTa: "கோச்சார செவ்வாய் மீது ஜனன கேது: அறுவை சிகிச்சை திறன் மற்றும் ஞான வைராக்கியம்",
      nature: "mixed",
      intensity: 1,
      effectsEn: [
        "Ketu acts as Mars' spiritual mirror (Kujavat Ketu): laser focus on technical or occult mastery.",
        "Ideal for surgeons, acupuncturists, and martial artists; deep spiritual discipline.",
        "Caution against minor cuts, burns, or inflammatory boils; drink cooling beverages.",
      ],
      effectsTa: [
        "குஜவத் கேது கோட்பாடு; மருத்துவர்கள், அறுவை சிகிச்சை நிபுணர்கள் மற்றும் ஆய்வாளர்களுக்கு அபார ஆற்றல்.",
        "ஆன்மிக வைராக்கியமும் தியான தீவிரமும் உண்டாகும்; அமானுஷ்ய அறிவில் முன்னேற்றம்.",
        "கத்தி, நெருப்பு மற்றும் ரத்த காயங்களில் கவனமாக இருக்கவும்; உடல் உஷ்ணத்தை தணிக்கவும்.",
      ],
      quoteEn: "Kujavat Ketu transit: sharp precision, ascetic courage, but requires protection against cuts.",
      quoteTa: "செவ்வாயும் கேதுவும் இணைவது கூர்மையான அறிவுத்திறனையும் ஆன்மிக வைராக்கியத்தையும் தரும்.",
    },
  },

  Jupiter: {
    Sun: {
      titleEn: "Transit Jupiter over Natal Sun: Golden Royal Honors & Fatherly Elevation",
      titleTa: "கோச்சார குரு மீது ஜனன சூரியன்: ராஜ யோகம், பதவி உயர்வு மற்றும் தந்தை மேன்மை",
      nature: "benefic",
      intensity: 10,
      effectsEn: [
        "The great benefic expands the soul and career: royal favor, high appointments, and promotions.",
        "Father's health and societal honor surge; long-standing disputes with authorities resolve.",
        "Divine grace safeguards all major endeavors; best time to launch ambitious institutions.",
      ],
      effectsTa: [
        "குரு பகவான் ஆத்மகாரக சூரியனை தழுவுகிறார்; அரசு கௌரவம், பதவி உயர்வு மற்றும் தலைமை வாய்ப்பு.",
        "தந்தையின் உடல்நிலை மற்றும் புகழ் மேலோங்கும்; அரசு விவகாரங்கள் தடையின்றி முடியும்.",
        "தெய்வ அருள் முழுமையாக துணை நிற்கும்; புதிய உயரிய பொறுப்புகளை ஏற்க உகந்த காலம்.",
      ],
      quoteEn: "Transit of yearly benefic over soul indicator Sun: monumental elevation in status and divine grace.",
      quoteTa: "குரு சூரியன் மீது செல்வது ராஜ யோகத்தை தரும்; மதிப்பும் பதவியும் தானாக தேடி வரும்.",
    },
    Moon: {
      titleEn: "Transit Jupiter over Natal Moon: Gochara Gajakesari & Domestic Bliss",
      titleTa: "கோச்சார குரு மீது ஜனன சந்திரன்: கோச்சார கஜகேசரி யோகம், மன நிம்மதி மற்றும் சுப காரியம்",
      nature: "benefic",
      intensity: 10,
      effectsEn: [
        "Gajakesari Gochara! Depression, mental anxieties, and grief vanish like morning mist.",
        "Prosperity multiplies; maternal joy, family celebrations, weddings, and arrival of good news.",
        "Financial liquidity improves significantly; wisdom and benevolent speech charm all audiences.",
      ],
      effectsTa: [
        "கோச்சார கஜகேசரி யோகம்! மன அழுத்தம் மற்றும் கவலைகள் நீங்கி ஆழ்ந்த நிம்மதி பிறக்கும்.",
        "குடும்பத்தில் சுப நிகழ்ச்சிகள், திருமணம், குழந்தை பாக்கியம் மற்றும் மங்களகரமான நிகழ்வுகள் கூடிவரும்.",
        "பொருளாதார நிலை உயரும்; தாயாரின் ஆசியும் குடும்ப மகிழ்ச்சியும் தழைத்தோங்கும்.",
      ],
      quoteEn: "Transit Jupiter over Moon dissolves sorrow and confers Gajakesari prosperity and domestic peace.",
      quoteTa: "சந்திரன் மீது குரு வருவது கஜகேசரி சுப பலன்களை தந்து கவலைகளை போக்கும்.",
    },
    Mars: {
      titleEn: "Transit Jupiter over Natal Mars: Sovereign Land Acquisitions & Brotherly Glory",
      titleTa: "கோச்சார குரு மீது ஜனன செவ்வாய்: நில யோகம், சகோதர ஆதரவு மற்றும் வெற்றி யோகம்",
      nature: "benefic",
      intensity: 8,
      effectsEn: [
        "Wisdom guides martial energy: acquisition of fertile lands, houses, or industrial properties.",
        "Brothers and younger siblings attain high prosperity and lend unwavering support.",
        "Courageous legal victories; sports or technical contracts are finalized fruitfully.",
      ],
      effectsTa: [
        "ஞானம் வீரத்தை வழிநடத்துகிறது; பூமி லாபம், புதிய மனை அல்லது வீடு வாங்கும் யோகம் உண்டாகும்.",
        "சகோதரர்களின் ஆதரவு கிடைக்கும்; உடன் பிறந்தவர்களுக்கு நல்ல வேலை அல்லது முன்னேற்றம் ஏற்படும்.",
        "வழக்குகள் மற்றும் போட்டிகளில் மகத்தான வெற்றி கிட்டும்.",
      ],
      quoteEn: "Jupiter over Mars transforms martial force into dharmic prosperity and property mastery.",
      quoteTa: "செவ்வாய் மீது குரு செல்வதால் பூமி சேர்க்கையும் சகோதர நலன்களும் பெருகும்.",
    },
    Mercury: {
      titleEn: "Transit Jupiter over Natal Mercury: Saraswati Yoga & Commercial Triumph",
      titleTa: "கோச்சார குரு மீது ஜனன புதன்: சரஸ்வதி யோகம், கல்வி சாதனை மற்றும் வணிக பெருக்கம்",
      nature: "benefic",
      intensity: 9,
      effectsEn: [
        "Conjunction of higher wisdom (Jupiter) and analytical intelligence (Mercury): Saraswati Yoga.",
        "Outstanding success in examinations, publishing, teaching, consulting, and trade agreements.",
        "Sound financial investments; sharp acumen transforms negotiations into profitable assets.",
      ],
      effectsTa: [
        "சரஸ்வதி யோக காலம்! கல்வி, ஆராய்ச்சி, எழுத்து மற்றும் வெளியீட்டுத் துறையில் மகத்தான சாதனை.",
        "ஆலோசனைப் பணிகள், கற்பித்தல் மற்றும் வணிக ஒப்பந்தங்கள் மிகச் சிறந்த லாபத்தை ஈட்டித் தரும்.",
        "புத்தி கூர்மையும் வாக்கு சாதுரியமும் பாராட்டைப் பெறும்; நிதி நிலைமை ஸ்திரப்படும்.",
      ],
      quoteEn: "Jupiter blesses Mercury with Saraswati intellect: peak academic and commercial success.",
      quoteTa: "புதன் மீது குரு சஞ்சரிப்பது அறிவாற்றலையும் வியாபார மேன்மையையும் பன்மடங்கு பெருக்கும்.",
    },
    Jupiter: {
      titleEn: "Transit Jupiter over Natal Jupiter: 12-Year Jupiter Return & Spiritual Epoch",
      titleTa: "கோச்சார குரு மீது ஜனன குரு: 12 வருட குரு திரும்புதல் மற்றும் புதிய வாழ்க்கை உதயம்",
      nature: "benefic",
      intensity: 10,
      effectsEn: [
        "Monumental 12-year cycle renewal: divine rebirth of destiny, life purpose, and righteousness.",
        "Arrival of noble progeny, performance of major sacred rituals, pilgrimages to holy shrines.",
        "Elevation to advisory status or spiritual leadership; lifelong dharmic foundations established.",
      ],
      effectsTa: [
        "12 வருடங்களுக்கு ஒருமுறை நிகழும் மகா குரு திரும்புதல்! வாழ்க்கையில் ஒரு புதிய பொற்கால துவக்கம்.",
        "புத்திர பாக்கியம், புனித யாத்திரைகள் மற்றும் குலதெய்வ வழிபாடுகள் மிகச் சிறப்பாக நிறைவேறும்.",
        "ஆன்மிக ஞானமும், தலைமைத்துவ கௌரவமும் தானாக வந்து சேரும்.",
      ],
      quoteEn: "Jupiter Return marks the dawn of a grand 12-year epoch of virtue, progeny, and wisdom.",
      quoteTa: "ஜன்ம குருவின் திரும்புதல் வாழ்வின் மிக முக்கியமான சுப மாற்றங்களை நல்கும்.",
    },
    Venus: {
      titleEn: "Transit Jupiter over Natal Venus: Matrimonial Bliss, Progeny & Opulence",
      titleTa: "கோச்சார குரு மீது ஜனன சுக்கிரன்: சுப விவாக யோகம், செல்வ வளம் மற்றும் வாகன சேர்க்கை",
      nature: "benefic",
      intensity: 10,
      effectsEn: [
        "The two great preceptors (Deva Guru & Asura Guru) unite: boundless prosperity and grace.",
        "Arrival of ideal life partners, grand weddings, childbirth, or acquisition of luxury conveyances.",
        "Substantial financial windfalls, elegant jewelry purchases, and aesthetic harmony.",
      ],
      effectsTa: [
        "இருபெரும் சுப கிரகங்களின் அனுகிரகம்; திருமண தடைகள் விலகி திருமணம் இனிதே கைகூடும்.",
        "மழலைச் செல்வம், புதிய சொகுசு வாகனம், ஆபரணங்கள் மற்றும் நிதி பெருக்கம் உண்டாகும்.",
        "தாம்பத்திய வாழ்க்கை மகிழ்ச்சியாகவும், கலை சார்ந்த முயற்சிகள் பெரும் வெற்றியையும் தரும்.",
      ],
      quoteEn: "Jupiter over Venus awakens Kalathra and Dhana yogas: marriages and wealth blossom.",
      quoteTa: "சுக்கிரன் மீது குருவின் பார்வை அல்லது சேர்க்கை திருமண பந்தத்தையும் செல்வத்தையும் தரும்.",
    },
    Saturn: {
      titleEn: "Transit Jupiter over Natal Saturn: Brahma-Karma Synthesis & Debt Relief",
      titleTa: "கோச்சார குரு மீது ஜனன சனி: பிரம்ம-கர்ம யோகம், கடன் நிவாரணம் மற்றும் உத்தியோக ஸ்திரத்தன்மை",
      nature: "benefic",
      intensity: 8,
      effectsEn: [
        "Wisdom sanctifies hard labor: promotion to permanent senior positions and societal respect.",
        "Relief from chronic debts, legal disputes, and exhausting burdens of the past.",
        "Foundation of lasting institutions, retirement security, and humanitarian projects.",
      ],
      effectsTa: [
        "கடின உழைப்பிற்கு தகுந்த கௌரவமும் நிரந்தர பதவியும் கிடைக்கும்; உத்தியோகத்தில் ஸ்திரத்தன்மை.",
        "நீண்ட நாள் கடன்கள், வழக்குகள் மற்றும் மனபாரங்களில் இருந்து பெரும் விடுதலை கிட்டும்.",
        "சமூக பணிகளில் நற்பெயர் உண்டாகும்; நீண்ட கால சேமிப்பு திட்டங்கள் வெற்றியடையும்.",
      ],
      quoteEn: "Jupiter over Saturn transforms karmic toil into enduring societal authority and peace.",
      quoteTa: "சனி மீது குரு செல்வதால் உழைப்பு பலன் தரும்; கடன்களும் இன்னல்களும் விலகும்.",
    },
    Rahu: {
      titleEn: "Transit Jupiter over Natal Rahu: Transformation of Karmic Knots & Foreign Joy",
      titleTa: "கோச்சார குரு மீது ஜனன ராகு: குரு-சண்டாள தோஷ நிவர்த்தி மற்றும் வெளிநாட்டு யோகம்",
      nature: "mixed",
      intensity: 4,
      effectsEn: [
        "Guru sanctifies the shadow node: foreign travels materialize fruitfully with reputable sponsors.",
        "Purification of unconventional desires; past karmic obsessions turn toward philanthropy.",
        "Need to avoid financial speculation based on unverified tips; seek verified expert counsel.",
      ],
      effectsTa: [
        "ராகுவின் நிழல் தோஷத்தை குருவின் ஒளி போக்குகிறது; வெளிநாட்டு பயணங்கள் நன்மையில் முடியும்.",
        "வித்தியாசமான சிந்தனைகள் ஆக்கப்பூர்வமாக மாறும்; தர்ம காரியங்களில் நாட்டம் ஏற்படும்.",
        "ஊக வணிகம் மற்றும் தவறான குறுக்கு வழி ஆலோசனைகளில் எச்சரிக்கையாக இருக்கவும்.",
      ],
      quoteEn: "Jupiter over Rahu dissolves illusions and yields auspicious international breakthroughs.",
      quoteTa: "ராகு மீது குரு செல்வது வெளிநாட்டு வாய்ப்புகளையும் கர்ம வினைகளில் நிவர்த்தியையும் தரும்.",
    },
    Ketu: {
      titleEn: "Transit Jupiter over Natal Ketu: Highest Moksha Karaka & Spiritual Awakening",
      titleTa: "கோச்சார குரு மீது ஜனன கேது: மோட்ச யோகம், ஞானோதயம் மற்றும் குலதெய்வ அனுகிரகம்",
      nature: "benefic",
      intensity: 8,
      effectsEn: [
        "The two ultimate spiritual forces unite: transcendental insight, deep meditation, and bliss.",
        "Pilgrimages to ancient Himalayan or coastal shrines; initiation into higher mantra disciplines.",
        "Disregard for petty ego disputes; deep peace and intuition illuminate the life path.",
      ],
      effectsTa: [
        "இருபெரும் ஞான கிரகங்களின் சங்கமம்; உயர்ந்த ஆன்மிக நாட்டம், யோக சாதனை மற்றும் மன அமைதி.",
        "புனித தலங்களுக்கு தீர்த்த யாத்திரை செல்லுதல் மற்றும் குலதெய்வ அருள் பூரணமாக கிடைக்கும்.",
        "உள்ளுணர்வு மிகத் துல்லியமாக வழிகாட்டும்; உலகியல் சச்சரவுகளை தாண்டி சாந்தம் பிறக்கும்.",
      ],
      quoteEn: "Jupiter over Ketu is the classic signature of spiritual liberation and dharmic realization.",
      quoteTa: "கேது மீது குரு செல்வது ஞானத்தையும் மோட்ச சிந்தனையையும் மேலோங்கச் செய்யும்.",
    },
  },

  Saturn: {
    Sun: {
      titleEn: "Transit Saturn over Natal Sun: Karmic Testing of Authority & Fatherly Duties",
      titleTa: "கோச்சார சனி மீது ஜனன சூரியன்: அதிகாரம் மற்றும் தந்தை வழி கர்ம கடமைகள்",
      nature: "caution",
      intensity: -6,
      effectsEn: [
        "The dark taskmaster presses upon the soul: immense work burden and bureaucratic scrutiny.",
        "Father's health or elder family elders require responsible care and support.",
        "Avoid ego showdowns with top management; disciplined patience and humility turn trial into mastery.",
        "Watch for bone fatigue, spinal posture, and cardiovascular vitality.",
      ],
      effectsTa: [
        "சூரியன் மீது சனி சஞ்சரிப்பதால் வேலைச்சுமை மற்றும் அதிகாரிகளின் கெடுபிடிகள் அதிகரிக்கும்.",
        "தந்தையின் உடல்நிலையில் அக்கறை தேவை; குடும்ப பெரியவர்களின் பொறுப்புகளை ஏற்க வேண்டி வரும்.",
        "மேலதிகாரிகளுடன் ஈகோ மோதல்களை முற்றிலும் தவிர்க்கவும்; பணிவும் பொறுமையும் வெற்றியைத் தரும்.",
        "முதுகுத்தண்டு, எலும்பு மற்றும் கண் ஆரோக்கியத்தில் கூடுதல் கவனம் தேவை.",
      ],
      quoteEn: "Saturn tests the Sun with duty and endurance: humility and hard labor ensure survival.",
      quoteTa: "சூரியன் மீது சனி செல்வது கடமை உணர்வையும் பொறுமையையும் சோதிக்கும் காலமாகும்.",
    },
    Moon: {
      titleEn: "Transit Saturn over Natal Moon: Peak Sade Sati (Janma Shani) & Deep Maturation",
      titleTa: "கோச்சார சனி மீது ஜனன சந்திரன்: ஜன்ம சனி (ஏழரை சனி நடுப்பகுதி) மற்றும் மன முதிர்ச்சி",
      nature: "caution",
      intensity: -7,
      effectsEn: [
        "The epicenter of Sade Sati: deep psychological purification, sobriety, and emotional resilience.",
        "Restructuring of living conditions, domestic responsibilities, and maternal obligations.",
        "Feelings of loneliness or isolation; do not succumb to pessimism, for Saturn builds character.",
        "Meditation, temple lamps with sesame oil, and service to the underprivileged bring profound solace.",
      ],
      effectsTa: [
        "ஏழரை சனியின் நடுப்பகுதி (ஜன்ம சனி); மன சஞ்சலங்களும், தனிமை உணர்வும் தோன்றி மறையலாம்.",
        "வாழ்க்கை சூழல் மற்றும் குடும்ப பொறுப்புகள் மறுசீரமைக்கப்படும்; தாயாரின் உடல்நிலையில் கவனம்.",
        "எதிர்மறை எண்ணங்களை தவிர்த்து, தியானம் மற்றும் சிவ வழிபாட்டை தொடர்ந்து செய்வது நல்லது.",
        "ஏழைகளுக்கு அன்னதானம் செய்தல் மற்றும் எள் தீபம் ஏற்றுவது சிறந்த நிம்மதியை தரும்.",
      ],
      quoteEn: "Saturn over natal Moon represents Janma Shani: endurance, duty, and spiritual stoicism required.",
      quoteTa: "சந்திரன் மீது சனி செல்வது ஜன்ம சனியாகும்; பொறுமையும் தர்ம சிந்தனையும் மனதை காக்கும்.",
    },
    Mars: {
      titleEn: "Transit Saturn over Natal Mars: Mechanical Rigor & Temperamental Mastery",
      titleTa: "கோச்சார சனி மீது ஜனன செவ்வாய்: இயந்திர உழைப்பு, வீரிய கட்டுப்பாடு மற்றும் உறுதி",
      nature: "caution",
      intensity: -5,
      effectsEn: [
        "Collision of cool earth/air (Saturn) and flaming fire (Mars): friction requires channelized discipline.",
        "Delays in engineering projects, property clearances, or machinery maintenance.",
        "Extreme caution against road haste, sharp instruments, or sudden muscular overexertion.",
        "Meticulous, methodical work conquers obstacles where hasty outbursts fail.",
      ],
      effectsTa: [
        "நெருப்பும் காற்றும் உராய்வது போன்ற காலம்; ஆத்திரப்படாமல் காரியங்களை நிதானமாக அணுக வேண்டும்.",
        "கட்டிட பணிகள், இயந்திர பழுதுகள் அல்லது சொத்து விவகாரங்களில் தாமதங்கள் எழலாம்.",
        "வாகனம் ஓட்டும் போதும், இயந்திரங்களை கையாளும் போதும் முழு எச்சரிக்கை தேவை.",
        "கடுமையான உழைப்பும் திட்டமிடலும் இறுதியில் நிலையான வெற்றியை கொடுக்கும்.",
      ],
      quoteEn: "Saturn over Mars demands mastery over impulsiveness; avoid road rash and haste.",
      quoteTa: "செவ்வாய் மீது சனி செல்வது அவசரத்தை தடுத்து நிதான உழைப்பை கோரும் காலமாகும்.",
    },
    Mercury: {
      titleEn: "Transit Saturn over Natal Mercury: Analytical Depth & Contractual Scrutiny",
      titleTa: "கோச்சார சனி மீது ஜனன புதன்: தீவிர ஆராய்ச்சி, கணக்கு தணிக்கை மற்றும் சட்ட விழிப்புணர்வு",
      nature: "mixed",
      intensity: 2,
      effectsEn: [
        "Saturn stabilizes Mercury's quick intellect: extraordinary concentration for research, law, and coding.",
        "Meticulous review of commercial agreements, financial balance sheets, and tax audits.",
        "Avoid signing unverified contracts; slow and steady intellectual construction prevails.",
      ],
      effectsTa: [
        "புதனின் வேகத்தை சனி ஒழுங்குபடுத்துகிறார்; ஆராய்ச்சி, கணக்கு மற்றும் சட்ட ஆய்வுகளுக்கு மிகச் சிறந்த காலம்.",
        "நிதி தணிக்கைகள் மற்றும் வணிக ஒப்பந்தங்களை மிக நுணுக்கமாக படித்து கையொப்பமிடவும்.",
        "படிப்பிலும் எழுத்திலும் தீவிர கவனமும் விடாமுயற்சியும் நிலையான புகழை தரும்.",
      ],
      quoteEn: "Saturn lends gravitas and analytical discipline to Mercury's versatile intellect.",
      quoteTa: "புதன் மீது சனி செல்வது ஆழமான ஆய்வறிவையும் கணக்கு வழக்குகளில் விழிப்புணர்வையும் தரும்.",
    },
    Jupiter: {
      titleEn: "Transit Saturn over Natal Jupiter: Dharma-Karma Synthesis & Societal Foundation",
      titleTa: "கோச்சார சனி மீது ஜனன குரு: தர்ம-கர்ம யோகம், உழைப்பின் பலன் மற்றும் நிலையான செல்வம்",
      nature: "benefic",
      intensity: 7,
      effectsEn: [
        "The lord of karma meets the lord of dharma: righteous, hard-earned wealth and enduring legacy.",
        "Recognition for long years of faithful service; promotion to trusted fiduciary or directorship roles.",
        "Building lasting assets, educational endowments, or charitable trusts for family welfare.",
      ],
      effectsTa: [
        "தர்மமும் கர்மமும் இணையும் உன்னத காலம்; நேர்மையான உழைப்பிற்கு தக்க நிலையான செல்வம் சேரும்.",
        "நீண்ட கால விசுவாசமான பணிக்கு அங்கீகாரம் கிடைக்கும்; உயரிய நிர்வாகப் பொறுப்புகள் தேடி வரும்.",
        "குடும்ப பாதுகாப்பு மற்றும் எதிர்கால சேமிப்புக்கான ஆக்கப்பூர்வமான திட்டங்கள் நிறைவேறும்.",
      ],
      quoteEn: "Saturn over Jupiter generates Brahma-Karma stability: hard labor rewarded with lasting honor.",
      quoteTa: "குரு மீது சனி செல்வது தர்ம நெறியிலான உழைப்பையும் அதன் நிரந்தர நற்பலனையும் நல்கும்.",
    },
    Venus: {
      titleEn: "Transit Saturn over Natal Venus: Relationship Sobriety & Financial Prudence",
      titleTa: "கோச்சார சனி மீது ஜனன சுக்கிரன்: குடும்ப நிதி கட்டுப்பாடு மற்றும் உறவுகளில் முதிர்ச்சி",
      nature: "mixed",
      intensity: 1,
      effectsEn: [
        "Sensual extravagance is tempered by financial budgeting and practical realism.",
        "Marriages and partnerships require sober maturity, emotional commitment, and mutual respect.",
        "Aesthetic taste turns toward classic, enduring heritage architecture, antiques, and minimalism.",
      ],
      effectsTa: [
        "ஆடம்பர செலவுகள் குறைக்கப்பட்டு, குடும்பத்தில் நிதி மேலாண்மையும் சேமிப்பும் முக்கியத்துவம் பெறும்.",
        "காதல் மற்றும் திருமண பந்தத்தில் முதிர்ச்சியான அணுகுமுறையும் பரஸ்பர மரியாதையும் தேவை.",
        "பழங்கால பொருட்கள், பாரம்பரிய கலைகள் மற்றும் எளிமையான வாழ்க்கை முறையில் நாட்டம் ஏற்படும்.",
      ],
      quoteEn: "Saturn over Venus tempers transient desires into enduring, mature relationship values.",
      quoteTa: "சுக்கிரன் மீது சனி செல்வது நிதி கட்டுப்பாட்டையும் தாம்பத்தியத்தில் முதிர்ச்சியையும் கற்றுத்தரும்.",
    },
    Saturn: {
      titleEn: "Transit Saturn over Natal Saturn: 30-Year Saturn Return & Milestone Reckoning",
      titleTa: "கோச்சார சனி மீது ஜனன சனி: 30 வருட சனி திரும்புதல் மற்றும் வாழ்வின் முக்கிய மைல்கல்",
      nature: "mixed",
      intensity: 3,
      effectsEn: [
        "The monumental Saturn Return (~ages 29.5 & 59): shedding outdated identities and building bedrock foundations.",
        "Major career milestone, assumption of substantial societal or familial mantle.",
        "Unforgiving karmic audit: whatever is built on integrity endures; illusions crumble away cleanly.",
      ],
      effectsTa: [
        "வாழ்வின் முக்கிய 30 வருட சனி திரும்புதல் காலம்! போலியான மாயைகள் அகன்று உண்மையான பலம் வெளிப்படும்.",
        "தொழில் மற்றும் குடும்பத்தில் மிகப்பெரிய திருப்புமுனையும் நிரந்தர அடித்தளமும் அமையும்.",
        "நேர்மையும் தர்மமும் உள்ள காரியங்கள் தழைத்தோங்கும்; வாழ்வின் புதிய சகாப்தம் தொடங்கும்.",
      ],
      quoteEn: "Saturn Return tests the foundations of life: enduring structures are permanently established.",
      quoteTa: "ஜன்ம சனி திரும்புதல் வாழ்வின் மிக முக்கியமான கர்ம மைல்கல்லாக விளங்கும்.",
    },
    Rahu: {
      titleEn: "Transit Saturn over Natal Rahu: Unmasking of Illusions & Karmic Purge",
      titleTa: "கோச்சார சனி மீது ஜனன ராகு: மாயைகள் விலகுதல், நிஜத்தை உணர்தல் மற்றும் கர்ம தூய்மை",
      nature: "caution",
      intensity: -5,
      effectsEn: [
        "Saturn dissolves Rahu's smoke and mirrors: confrontation with raw reality and factual truth.",
        "Cessation of unrealistic speculative gambles; focus shifts to rigorous grassroots execution.",
        "Protect joints, nervous pathways, and maintain transparent accounting to avoid audit friction.",
      ],
      effectsTa: [
        "ராகுவின் மாயைகளும் மிகையான கற்பனைகளும் விலகி நடைமுறை நிஜம் புரியவரும்.",
        "ஊக வணிகம் மற்றும் தவறான குறுக்கு வழிகளை கைவிட்டு உழைப்பை நம்பி வாழ வேண்டிய காலம்.",
        "நரம்பு மண்டலம் மற்றும் மூட்டு ஆரோக்கியத்தில் கவனம் தேவை; கணக்குகளில் நேர்மை காக்கவும்.",
      ],
      quoteEn: "Saturn over Rahu strips away artificial glamour and grounds the native in duty.",
      quoteTa: "ராகு மீது சனி செல்வது மாயைகளை அகற்றி உண்மையான உழைப்பிற்கு வழிவகுக்கும்.",
    },
    Ketu: {
      titleEn: "Transit Saturn over Natal Ketu: Hermetic Solitude & Karmic Detachment",
      titleTa: "கோச்சார சனி மீது ஜனன கேது: துறவற நாட்டம், மன அமைதி மற்றும் கர்ம விமோசனம்",
      nature: "mixed",
      intensity: 2,
      effectsEn: [
        "Deep detachment from superficial status; inner peace found in minimalist living and meditation.",
        "Purging of generational baggage; visiting quiet, solitary coastal or mountain temples.",
        "Subtle joint stiffness; staying warm and consuming warm herbal nutrition is recommended.",
      ],
      effectsTa: [
        "உலகியல் ஆடம்பரங்களில் நாட்டம் குறையும்; எளிமையான வாழ்க்கையும் தியானமும் ஆனந்தம் தரும்.",
        "பழைய கர்ம சுமைகள் நீங்கும்; அமைதியான பழமையான திருத்தலங்களுக்கு சென்று வரலாம்.",
        "உடலில் வாதம் மற்றும் மூட்டு வலிகள் வராமல் இருக்க சூடான ஆரோக்கியமான உணவுகளை உட்கொள்ளவும்.",
      ],
      quoteEn: "Saturn over Ketu confers profound spiritual asceticism and release of karmic burdens.",
      quoteTa: "கேது மீது சனி செல்வது வைராக்கியத்தையும் ஆன்மிக ஈடேற்றத்தையும் வழங்கும்.",
    },
  },
};

// Default fallback generator for any remaining pair
function getFallbackConjunction(
  transitPlanet: string,
  natalPlanet: string,
  signIndex: number
): GkConjunctionEntry {
  const isTransitEnemy = GK_PLANETARY_ENEMIES[transitPlanet]?.includes(natalPlanet);
  const signEn = ZODIAC_SIGNS_EN[signIndex] || "";
  const signTa = ZODIAC_SIGNS_TA[signIndex] || "";

  if (isTransitEnemy) {
    return {
      titleEn: `Transit ${transitPlanet} over Natal ${natalPlanet} in ${signEn}: Inimical Friction`,
      titleTa: `${signTa}வில் கோச்சார ${transitPlanet} ஜனன ${natalPlanet} மீது: பகை கிரக சேர்க்கை`,
      nature: "caution",
      intensity: -4,
      effectsEn: [
        `Transit of ${transitPlanet} over inimical natal ${natalPlanet} creates friction in their significations.`,
        "Patience and caution are required; avoid impulsive confrontations or risky commitments.",
        "Focus on daily duty while allowing the transit cycle to unfold peacefully.",
      ],
      effectsTa: [
        `பகை கிரகமான ஜனன ${natalPlanet} மீது கோச்சார ${transitPlanet} செல்வதால் காரகத்துவங்களில் சிறு சோதனைகள் எழும்.`,
        "முன்கோபத்தையும் அவசர முடிவுகளையும் தவிர்த்து நிதானமாக செயல்படுவது அவசியம்.",
        "கடமைகளை அமைதியாக செய்து வர நற்பலன்கள் கிட்டும்.",
      ],
      quoteEn: "Tirupur GK Chandra Nadi rule: transit over inimical natal planet tests temporary character.",
      quoteTa: "திருப்பூர் ஜிகே சந்திர நாடி விதி: பகை கிரகம் மீது கோச்சார கிரகம் செல்வது மனதை சோதிக்கும்.",
    };
  }

  return {
    titleEn: `Transit ${transitPlanet} over Natal ${natalPlanet} in ${signEn}: Auspicious Catalyst`,
    titleTa: `${signTa}வில் கோச்சார ${transitPlanet} ஜனன ${natalPlanet} மீது: சுப கிரக சேர்க்கை`,
    nature: "benefic",
    intensity: 5,
    effectsEn: [
      `Harmonious transit of ${transitPlanet} over natal ${natalPlanet} activates supportive opportunities.`,
      "Energies align favorably with life goals; communications and actions yield encouraging results.",
      "Good time for collaborative endeavors and productive initiatives.",
    ],
    effectsTa: [
      `சுப கிரகமான ஜனன ${natalPlanet} மீது கோச்சார ${transitPlanet} செல்வது அனுகூலமான வாய்ப்புகளை உருவாக்கும்.`,
      "முயற்சிகள் எளிதில் கைகூடும்; மன அமைதியும் உற்சாகமும் பெருகும்.",
      "புதிய பணிகளை திட்டமிட்டு செயல்படுத்த நல்ல தருணம்.",
    ],
    quoteEn: "Tirupur GK Chandra Nadi rule: transit over friendly planet catalyzes positive developments.",
    quoteTa: "திருப்பூர் ஜிகே சந்திர நாடி விதி: நட்பு கிரகம் மீது கோச்சாரம் செல்வது சுப விளைவுகளை தரும்.",
  };
}

/**
 * Calculates GK Aspects from a transiting planet to a natal planet
 */
function evaluateGkAspect(
  transitPlanet: string,
  transitSign: number,
  natalPlanet: string,
  natalSign: number
): GkPlanetTransitAspect | null {
  if (transitSign === natalSign) return null; // That's a conjunction, not aspect

  // Count from transit sign to natal sign (1-based: same sign=1, next=2, etc.)
  const count = ((natalSign - transitSign + 12) % 12) + 1;

  // Mars: 4th, 7th, 8th aspects
  if (transitPlanet === "Mars") {
    if (count === 4) {
      return {
        transitingPlanet: "Mars",
        natalPlanet,
        aspectType: "4th",
        effectTitleEn: `Transit Mars 4th Special Aspect on Natal ${natalPlanet}`,
        effectTitleTa: `ஜனன ${natalPlanet} மீது கோச்சார செவ்வாயின் 4-ம் சிறப்புப் பார்வை`,
        descriptionEn: `Mars casts its forceful 4th home/property aspect on natal ${natalPlanet}, demanding urgent structural attention or protection.`,
        descriptionTa: `செவ்வாய் தனது 4-ம் பார்வையாக ஜனன ${natalPlanet}யை பார்ப்பதால் சொத்து மற்றும் குடும்ப விஷயங்களில் அவசர முடிவுகளை தவிர்க்கவும்.`,
        nature: "caution",
        intensityScore: -3,
      };
    }
    if (count === 8) {
      return {
        transitingPlanet: "Mars",
        natalPlanet,
        aspectType: "8th",
        effectTitleEn: `Transit Mars 8th Transformational Aspect on Natal ${natalPlanet}`,
        effectTitleTa: `ஜனன ${natalPlanet} மீது கோச்சார செவ்வாயின் 8-ம் ஆழப் பார்வை`,
        descriptionEn: `Mars 8th aspect brings sudden energetic developments and demands caution against accidents or mechanical strain.`,
        descriptionTa: `செவ்வாயின் 8-ம் பார்வை திடீர் திருப்பங்களையும் எச்சரிக்கையான அணுகுமுறையையும் கோருகிறது.`,
        nature: "caution",
        intensityScore: -4,
      };
    }
  }

  // Jupiter: 5th, 7th, 9th aspects (Amrita Drishti)
  if (transitPlanet === "Jupiter") {
    if (count === 5) {
      return {
        transitingPlanet: "Jupiter",
        natalPlanet,
        aspectType: "5th",
        effectTitleEn: `Transit Jupiter 5th Amrita Aspect on Natal ${natalPlanet}`,
        effectTitleTa: `ஜனன ${natalPlanet} மீது கோச்சார குருவின் 5-ம் அமிர்தப் பார்வை`,
        descriptionEn: `Jupiter casts its deeply auspicious 5th trinal vision upon natal ${natalPlanet}, bestowing divine grace, intelligence, and joy.`,
        descriptionTa: `குருவின் 5-ம் திரிகோண பார்வை ஜனன ${natalPlanet} மீது விழுவதால் புத்தி கூர்மை, தெய்வ அனுகிரகம் மற்றும் மங்கள பலன்கள் பெருகும்.`,
        nature: "benefic",
        intensityScore: 5,
      };
    }
    if (count === 9) {
      return {
        transitingPlanet: "Jupiter",
        natalPlanet,
        aspectType: "9th",
        effectTitleEn: `Transit Jupiter 9th Bhagya Aspect on Natal ${natalPlanet}`,
        effectTitleTa: `ஜனன ${natalPlanet} மீது கோச்சார குருவின் 9-ம் பாக்யப் பார்வை`,
        descriptionEn: `Jupiter's supreme 9th fortune glance purifies natal ${natalPlanet}, bringing long-distance blessings, fatherly fortune, and prosperity.`,
        descriptionTa: `குருவின் 9-ம் பாக்ய பார்வை ஜனன ${natalPlanet}யை புனிதப்படுத்துகிறது; பாக்ய விருத்தியும் பெரியோர்களின் ஆசியும் கிட்டும்.`,
        nature: "benefic",
        intensityScore: 5,
      };
    }
  }

  // Saturn: 3rd, 7th, 10th aspects
  if (transitPlanet === "Saturn") {
    if (count === 3) {
      return {
        transitingPlanet: "Saturn",
        natalPlanet,
        aspectType: "3rd",
        effectTitleEn: `Transit Saturn 3rd Rigorous Aspect on Natal ${natalPlanet}`,
        effectTitleTa: `ஜனன ${natalPlanet} மீது கோச்சார சனியின் 3-ம் தீவிரப் பார்வை`,
        descriptionEn: `Saturn's 3rd courage aspect tests natal ${natalPlanet} through relentless work and sibling/communication duties.`,
        descriptionTa: `சனியின் 3-ம் பார்வை உழைப்பையும் விடாமுயற்சியையும் சோதித்து இறுதியில் நிலையான வெற்றியை தரும்.`,
        nature: "caution",
        intensityScore: -3,
      };
    }
    if (count === 10) {
      return {
        transitingPlanet: "Saturn",
        natalPlanet,
        aspectType: "10th",
        effectTitleEn: `Transit Saturn 10th Karma Aspect on Natal ${natalPlanet}`,
        effectTitleTa: `ஜனன ${natalPlanet} மீது கோச்சார சனியின் 10-ம் கர்மப் பார்வை`,
        descriptionEn: `Saturn's 10th authority glance demands unyielding professional accountability and ethical discipline.`,
        descriptionTa: `சனியின் 10-ம் பார்வை தொழிலில் அதீத பொறுப்புணர்வையும் ஒழுக்கத்தையும் கோருகிறது.`,
        nature: "caution",
        intensityScore: -3,
      };
    }
  }

  // Rahu / Ketu: 3rd & 11th controls (Tirupur GK table)
  if (transitPlanet === "Rahu" || transitPlanet === "Ketu") {
    if (count === 3 || count === 11) {
      return {
        transitingPlanet: transitPlanet,
        natalPlanet,
        aspectType: "control_3_11",
        effectTitleEn: `Transit ${transitPlanet} Controls ${count}th House Natal ${natalPlanet}`,
        effectTitleTa: `ஜனன ${natalPlanet} மீது கோச்சார ${transitPlanet}வின் ${count}-ம் வீட்டு ஆதிக்கம்`,
        descriptionEn: `According to Tirupur GK, ${transitPlanet} controls the 3rd and 11th signs, creating unconventional momentum in ${natalPlanet}'s sphere.`,
        descriptionTa: `திருப்பூர் ஜிகே விதியின்படி, ${transitPlanet} 3 மற்றும் 11-ம் வீடுகளை கட்டுப்படுத்துவதால் திடீர் விழிப்புணர்வும் லாபங்களும் வரும்.`,
        nature: "mixed",
        intensityScore: 2,
      };
    }
  }

  // 7th Aspect for all planets
  if (count === 7) {
    const isEnemy = GK_PLANETARY_ENEMIES[transitPlanet]?.includes(natalPlanet);
    const isBenefic = transitPlanet === "Jupiter" || transitPlanet === "Venus";
    return {
      transitingPlanet: transitPlanet,
      natalPlanet,
      aspectType: "7th",
      effectTitleEn: `Transit ${transitPlanet} Direct 7th Opposition Aspect on Natal ${natalPlanet}`,
      effectTitleTa: `ஜனன ${natalPlanet} மீது கோச்சார ${transitPlanet}வின் நேரடி 7-ம் பார்வை`,
      descriptionEn: isBenefic
        ? `Auspicious 7th direct aspect from benefic ${transitPlanet} purifies and elevates natal ${natalPlanet}.`
        : isEnemy
        ? `Direct 7th confrontation aspect from inimical ${transitPlanet} demands diplomacy and patience.`
        : `Direct 7th aspect from transiting ${transitPlanet} shines light upon natal ${natalPlanet}.`,
      descriptionTa: isBenefic
        ? `சுப கிரகமான ${transitPlanet}வின் நேரடி 7-ம் பார்வை ஜனன ${natalPlanet}க்கு மங்களகரமான ஆதரவை நல்கும்.`
        : isEnemy
        ? `பகை கிரகமான ${transitPlanet}வின் நேரடி பார்வை என்பதால் நிதானமும் விழிப்புணர்வும் தேவை.`
        : `கோச்சார ${transitPlanet}வின் நேரடி 7-ம் பார்வை ஜனன ${natalPlanet} மீது ஆதிக்கம் செலுத்துகிறது.`,
      nature: isBenefic ? "benefic" : isEnemy ? "caution" : "mixed",
      intensityScore: isBenefic ? 4 : isEnemy ? -3 : 1,
    };
  }

  return null;
}

/**
 * Main Tirupur S. Gopalakrishnan Transit Matching Function
 * Matches live (or user-selected) transits against the opened saved horoscope.
 */
export function analyzeGkTransits(
  natalPlanets: PlanetInfo[],
  transitingPlanets: PlanetInfo[],
  dasaLord?: string,
  bukthiLord?: string,
  andharaLord?: string,
  basePositiveScore?: number
): GkTransitAnalysisResult {
  const conjunctions: GkPlanetTransitConjunction[] = [];
  const aspects: GkPlanetTransitAspect[] = [];
  let totalTransitModifier = 0;

  // 1. Conjunctions & Degree Orb Proximity
  for (const tp of transitingPlanets) {
    for (const np of natalPlanets) {
      if (tp.sign_index === np.sign_index) {
        // Degree difference in sign
        const degDiff = Math.abs((tp.degree_in_sign ?? 0) - (np.degree_in_sign ?? 0));
        const isExactOrb = degDiff <= 5.0;

        // Lookup Tirupur GK Database entry
        const entry =
          GK_CONJUNCTION_DATABASE[tp.name]?.[np.name] ??
          getFallbackConjunction(tp.name, np.name, tp.sign_index);

        const orbMultiplier = isExactOrb ? 1.4 : 1.0;
        const weightedScore = Math.round(entry.intensity * orbMultiplier);
        totalTransitModifier += weightedScore;

        conjunctions.push({
          transitingPlanet: tp.name,
          natalPlanet: np.name,
          signIndex: tp.sign_index,
          signNameEn: ZODIAC_SIGNS_EN[tp.sign_index] || tp.sign_name,
          signNameTa: ZODIAC_SIGNS_TA[tp.sign_index] || tp.sign_name_tamil || tp.sign_name,
          degreeOrb: parseFloat(degDiff.toFixed(2)),
          isExactOrb,
          nature: entry.nature,
          predictionTitleEn: entry.titleEn,
          predictionTitleTa: entry.titleTa,
          effectsEn: entry.effectsEn,
          effectsTa: entry.effectsTa,
          gkRuleQuoteEn: entry.quoteEn,
          gkRuleQuoteTa: entry.quoteTa,
          intensityScore: weightedScore,
        });
      }

      // 2. Aspects from transiting planet to natal planet
      const asp = evaluateGkAspect(tp.name, tp.sign_index, np.name, np.sign_index);
      if (asp) {
        aspects.push(asp);
        totalTransitModifier += asp.intensityScore;
      }
    }
  }

  // Sort conjunctions: exact orbs first, then by intensity absolute magnitude
  conjunctions.sort((a, b) => {
    if (a.isExactOrb && !b.isExactOrb) return -1;
    if (!a.isExactOrb && b.isExactOrb) return 1;
    return Math.abs(b.intensityScore) - Math.abs(a.intensityScore);
  });

  // Sort aspects: benefics and high-intensity first
  aspects.sort((a, b) => Math.abs(b.intensityScore) - Math.abs(a.intensityScore));

  // 3. Moon Medical & Surgery Alert (Tirupur GK Chapter 3)
  const transitingMoon = transitingPlanets.find((p) => p.name === "Moon");
  const moonSign = transitingMoon?.sign_index ?? 1;
  const medData = KALAPURUSHA_MEDICAL[moonSign] || KALAPURUSHA_MEDICAL[1];

  // Check if transiting Moon is aspected by Jupiter (safe healing window)
  const jupiter = transitingPlanets.find((p) => p.name === "Jupiter");
  const jupAspectsMoon =
    jupiter &&
    ([5, 7, 9].includes(((moonSign - jupiter.sign_index + 12) % 12) + 1) ||
      jupiter.sign_index === moonSign);

  const moonMedical: GkMoonTransitMedicalAlert = {
    moonSignIndex: moonSign,
    moonSignNameEn: ZODIAC_SIGNS_EN[moonSign] || "Aries",
    moonSignNameTa: ZODIAC_SIGNS_TA[moonSign] || "மேஷம்",
    vulnerableOrganEn: medData.organEn,
    vulnerableOrganTa: medData.organTa,
    avoidSurgeriesEn: medData.avoidEn,
    avoidSurgeriesTa: medData.avoidTa,
    medicalAdviceEn: medData.adviceEn,
    medicalAdviceTa: medData.adviceTa,
    safeHealingWindow: !!jupAspectsMoon,
  };

  // 4. Confluence with running Dasa - Bukthi - Andhara
  let dasaConfluence: GkDasaTransitConfluence | undefined = undefined;
  if (dasaLord && bukthiLord) {
    const keyCatalystsEn: string[] = [];
    const keyCatalystsTa: string[] = [];
    let dModifier = 0;

    // Check if transiting Jupiter aspects or conjoins Dasa Lord
    const tJup = transitingPlanets.find((p) => p.name === "Jupiter");
    const nDasa = natalPlanets.find((p) => p.name === dasaLord);
    const nBukthi = natalPlanets.find((p) => p.name === bukthiLord);
    const nAndhara = andharaLord ? natalPlanets.find((p) => p.name === andharaLord) : undefined;

    if (tJup && nDasa) {
      const dist = ((nDasa.sign_index - tJup.sign_index + 12) % 12) + 1;
      if (dist === 1 || dist === 5 || dist === 7 || dist === 9) {
        dModifier += 6;
        keyCatalystsEn.push(
          `Transit Jupiter blesses running Maha Dasha lord (${dasaLord}) with divine Amrita vision (+6% auspicious boost).`
        );
        keyCatalystsTa.push(
          `கோச்சார குரு தசா நாதன் (${dasaLord}) மீது சுப பார்வை செலுத்துகிறார் (+6% மங்கள யோக உயர்வு).`
        );
      }
    }

    if (tJup && nBukthi) {
      const dist = ((nBukthi.sign_index - tJup.sign_index + 12) % 12) + 1;
      if (dist === 1 || dist === 5 || dist === 7 || dist === 9) {
        dModifier += 5;
        keyCatalystsEn.push(
          `Transit Jupiter casts protective glance over running Antar Dasha lord (${bukthiLord}) (+5% progress boost).`
        );
        keyCatalystsTa.push(
          `கோச்சார குரு புக்தி நாதன் (${bukthiLord}) மீது சுப பார்வை செலுத்துகிறார் (+5% காரிய சித்தி உயர்வு).`
        );
      }
    }

    // Check if transiting Saturn conjoins or afflicts Dasa/Bukthi Lord
    const tSat = transitingPlanets.find((p) => p.name === "Saturn");
    if (tSat && nDasa && tSat.sign_index === nDasa.sign_index) {
      dModifier -= 5;
      keyCatalystsEn.push(
        `Transit Saturn sits over Maha Dasha lord (${dasaLord}): temporary heavy duty and tests of patience (-5% transit friction).`
      );
      keyCatalystsTa.push(
        `கோச்சார சனி தசா நாதன் (${dasaLord}) மீது சஞ்சரிக்கிறார்: கடுமையான உழைப்பும் சோதனைகளும் (-5% தற்காலிக தாமதம்).`
      );
    }

    if (tSat && nBukthi && tSat.sign_index === nBukthi.sign_index) {
      dModifier -= 4;
      keyCatalystsEn.push(
        `Transit Saturn transits over Antar Dasha lord (${bukthiLord}): requires steady patience and endurance (-4% transit friction).`
      );
      keyCatalystsTa.push(
        `கோச்சார சனி புக்தி நாதன் (${bukthiLord}) மீது சஞ்சரிக்கிறார்: அமைதியும் நிதானமும் தேவை (-4% தற்காலிக சுணக்கம்).`
      );
    }

    // Check transiting Mars
    const tMars = transitingPlanets.find((p) => p.name === "Mars");
    if (tMars && nBukthi && tMars.sign_index === nBukthi.sign_index) {
      dModifier -= 3;
      keyCatalystsEn.push(
        `Transit Mars joins Antar Dasha lord (${bukthiLord}): swift temperamental urgency; channel energy into productive construction.`
      );
      keyCatalystsTa.push(
        `கோச்சார செவ்வாய் புக்தி நாதன் (${bukthiLord}) உடன் இணைகிறார்: அவசரத்தை தவிர்த்து ஆக்கப்பூர்வமாக செயல்படவும்.`
      );
    }

    // Check Andhara lord if present
    if (nAndhara && tJup) {
      const dist = ((nAndhara.sign_index - tJup.sign_index + 12) % 12) + 1;
      if (dist === 1 || dist === 5 || dist === 7 || dist === 9) {
        dModifier += 3;
        keyCatalystsEn.push(
          `Transit Jupiter illuminates current Andhara catalyst (${andharaLord}) (+3% rapid trigger).`
        );
        keyCatalystsTa.push(
          `கோச்சார குரு தற்போதைய அந்திர நாதன் (${andharaLord}) மீது சுப ஒளி பாய்ச்சுகிறார் (+3% உடனடி பலன்).`
        );
      }
    }

    // Clamp transit modifier between -15 and +15
    const clampedModifier = Math.max(-15, Math.min(15, dModifier));
    const rawBase = basePositiveScore ?? 65;
    const combinedScore = Math.max(5, Math.min(98, rawBase + clampedModifier));

    const summaryEn =
      clampedModifier >= 5
        ? `Highly Auspicious Gochara Alignment: Live transits strongly support the ${dasaLord} Dasa - ${bukthiLord} Bukthi period with a +${clampedModifier}% boost.`
        : clampedModifier <= -4
        ? `Testing Gochara Transit Friction: Live transits present temporary tests of patience (${clampedModifier}%), yet the fundamental Dasa-Bukthi destiny remains steady.`
        : `Balanced Gochara Confluence: Planetary transits act with steady harmony on the running ${dasaLord} Dasa - ${bukthiLord} Bukthi.`;

    const summaryTa =
      clampedModifier >= 5
        ? `மிகவும் சுபமான கோச்சார சேர்க்கை: தற்போதைய கோச்சார கிரகங்கள் ${dasaLord} தசை - ${bukthiLord} புக்திக்கு +${clampedModifier}% கூடுதல் சுப பலத்தை அளிக்கின்றன.`
        : clampedModifier <= -4
        ? `கோச்சார சோதனைக் காலம்: கோச்சார கிரகங்கள் தற்காலிக மன உளைச்சலையும் தாமதத்தையும் (${clampedModifier}%) தந்தாலும், மூல தசா பலன் நிலையாக இருக்கும்.`
        : `சமநிலையான கோச்சார சங்கமம்: கோச்சார கிரகங்கள் நடப்பு ${dasaLord} தசை - ${bukthiLord} புக்தியுடன் இணக்கமாக செயல்படுகின்றன.`;

    dasaConfluence = {
      dasaLord,
      bukthiLord,
      andharaLord,
      transitScoreModifier: clampedModifier,
      combinedAdjustedScore: combinedScore,
      transitConfluenceSummaryEn: summaryEn,
      transitConfluenceSummaryTa: summaryTa,
      keyCatalystsEn,
      keyCatalystsTa,
    };
  }

  // Summary Highlights
  const summaryHighlightsEn: string[] = [];
  const summaryHighlightsTa: string[] = [];

  if (conjunctions.length > 0) {
    summaryHighlightsEn.push(
      `${conjunctions.length} Active Conjunctions: Live transiting planets are currently passing directly over natal planets.`
    );
    summaryHighlightsTa.push(
      `${conjunctions.length} நேரடி கோச்சார சேர்க்கைகள்: கோச்சார கிரகங்கள் உங்கள் ஜனன கிரகங்களின் மீது நேரடியாக சஞ்சரிக்கின்றன.`
    );
  }

  if (aspects.length > 0) {
    const beneficAspects = aspects.filter((a) => a.nature === "benefic").length;
    summaryHighlightsEn.push(
      `${aspects.length} Significant Planetary Aspects active (${beneficAspects} Auspicious Trinal / Direct Glances).`
    );
    summaryHighlightsTa.push(
      `${aspects.length} முக்கிய பார்வைகள் செயல்பாட்டில் உள்ளன (${beneficAspects} சுப அமிர்தப் பார்வைகள்).`
    );
  }

  // Normalized overall modifier (-12 to +12)
  const normalizedTransitPercent = Math.max(-12, Math.min(12, Math.round(totalTransitModifier / 3)));

  return {
    calculatedAt: new Date().toISOString(),
    totalTransitingPlanets: transitingPlanets.length,
    conjunctions,
    aspects,
    moonMedical,
    dasaConfluence,
    transitModifierPercent: normalizedTransitPercent,
    gkCoreRuleEn:
      "Tirupur GK Golden Principle: 'Transit denotes Character, Temporary Mindsets & Catalysts; Maha Dasha & Antar Dasha determine Concrete Life Events and Destiny.'",
    gkCoreRuleTa:
      "திருப்பூர் ஜிகே பொன்மொழி: 'கோச்சாரம் என்பது தற்காலிக மனநிலை மற்றும் குண மாற்றங்களை மட்டுமே குறிக்கும்; விம்சForms மகா தசா மற்றும் அந்தர் தசா (புக்தி) மட்டுமே நிரந்தர வாழ்க்கை நிகழ்வுகளையும் விதியையும் தீர்மானிக்கும்.'",
    summaryHighlightsEn,
    summaryHighlightsTa,
  };
}
