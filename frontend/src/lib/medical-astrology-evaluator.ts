/**
 * Gokul's Astrological Insights - Medical Astrology Engine (Client-side & Hybrid Evaluator)
 * 
 * Evaluates Classical Vedic and Krishnamurti Paddhati (KP) Medical Astrology directly
 * from existing calculation results (horoscope, kp, dasa, liveTransits).
 * 
 * Adheres strictly to the safety mandate:
 * - Traditional astrological research only
 * - No medical diagnoses or treatment recommendations
 * - No disease probabilities, onset dates, or lifespan predictions
 * - Separate Vedic and KP analytical perspectives
 */

import type {
  HoroscopeResponse,
  KpResponse,
  DasaResponse,
  LiveTransitsResponse,
  MedicalAstrologyResponse,
  MedicalRule,
  HouseHealthAnalysis,
  AnatomicalSystemMapping,
  BirthChartPerspective,
  CurrentPeriodPerspective,
  HistoricalPeriodItem,
  HistoricalPeriodPerspective,
  TransitInfluence,
  KpCslAnalysis,
  SignificatorSourceDetail,
  KpDasaSignification,
  KpMedicalAnalysis,
} from "./types.ts";

export const SAFETY_DISCLAIMER_EN =
  "Medical Astrology presents traditional astrological interpretations for educational and research purposes only. Astrological combinations cannot diagnose, confirm or predict disease. For health concerns, consult a qualified healthcare professional.";

export const SAFETY_DISCLAIMER_TA =
  "மருத்துவ ஜோதிடம் பாரம்பரிய ஜோதிட விளக்கங்களை கல்வி மற்றும் ஆராய்ச்சி நோக்கங்களுக்காக மட்டுமே வழங்குகிறது. ஜோதிடக் கிரக அமைப்புகளால் நோயைக் கண்டறியவோ, உறுதிப்படுத்தவோ, எதிர்காலத்தில் ஏற்படும் எனக் கணிக்கவோ முடியாது. உடல்நலம் குறித்த கவலைகளுக்கு தகுதியான மருத்துவ நிபுணரை அணுகவும்.";

export const RULE_SET_VERSION = "1.0.0";

const SIGN_LORDS: Record<number, string> = {
  1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
  5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
  9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter",
};

const OWN_SIGNS: Record<string, number[]> = {
  Sun: [5], Moon: [4], Mars: [1, 8], Mercury: [3, 6],
  Jupiter: [9, 12], Venus: [2, 7], Saturn: [10, 11],
};

const EXALTATION_SIGNS: Record<string, number> = {
  Sun: 1, Moon: 2, Mars: 10, Mercury: 6,
  Jupiter: 4, Venus: 12, Saturn: 7, Rahu: 2, Ketu: 8,
};

const DEBILITATION_SIGNS: Record<string, number> = {
  Sun: 7, Moon: 8, Mars: 4, Mercury: 12,
  Jupiter: 10, Venus: 6, Saturn: 1, Rahu: 8, Ketu: 2,
};

const NATURAL_MALEFICS = new Set(["Sun", "Mars", "Saturn", "Rahu", "Ketu"]);
const NATURAL_BENEFICS = new Set(["Jupiter", "Venus", "Mercury"]);

const SIGN_NAMES_EN: Record<number, string> = {
  1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer",
  5: "Leo", 6: "Virgo", 7: "Libra", 8: "Scorpio",
  9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces",
};

const SIGN_NAMES_TA: Record<number, string> = {
  1: "மேஷம்", 2: "ரிஷபம்", 3: "மிதுனம்", 4: "கடகம்",
  5: "சிம்மம்", 6: "கன்னி", 7: "துலாம்", 8: "விருச்சிகம்",
  9: "தனுசு", 10: "மகரம்", 11: "கும்பம்", 12: "மீனம்",
};

export const KALAPURUSHA_ANATOMY: Record<number, {
  sign_en: string; sign_ta: string; lord: string;
  system_en: string; system_ta: string;
  organs_en: string; organs_ta: string; humor: string;
}> = {
  1: { sign_en: "Aries (Mesha)", sign_ta: "மேஷம்", lord: "Mars", system_en: "Cerebral & Cranial Axis", system_ta: "மூளை மற்றும் தலைப் பகுதி", organs_en: "Head, Brain, Cranial Bones, Facial Symmetry, Pineal Gland", organs_ta: "தலை, மூளை, மண்டை ஓடு, முக எலும்புகள்", humor: "Pitta (Fire)" },
  2: { sign_en: "Taurus (Vrishabha)", sign_ta: "ரிஷபம்", lord: "Venus", system_en: "Facial & Vocal Axis", system_ta: "முகம், குரல்வளை மற்றும் கழுத்துப் பகுதி", organs_en: "Face, Throat, Vocal Cords, Neck, Teeth, Right Eye, Thyroid", organs_ta: "முகம், தொண்டை, குரல்வளை, பற்கள், வலது கண், தைராய்டு", humor: "Vata/Kapha (Earth)" },
  3: { sign_en: "Gemini (Mithuna)", sign_ta: "மிதுனம்", lord: "Mercury", system_en: "Respiratory & Brachial Axis", system_ta: "தோள்பட்டை, கைகள் மற்றும் சுவாசப் பாதை", organs_en: "Shoulders, Arms, Hands, Upper Respiratory Tract, Bronchi", organs_ta: "தோள்கள், கைகள், மேல் சுவாசக் குழாய், மூச்சுக்குழல்", humor: "Vata (Air)" },
  4: { sign_en: "Cancer (Karka)", sign_ta: "கடகம்", lord: "Moon", system_en: "Thoracic & Gastric Axis", system_ta: "மார்பு, நுரையீரல் மற்றும் இரைப்பை பகுதி", organs_en: "Chest, Breasts, Lower Lungs, Stomach, Epigastric Cavity", organs_ta: "மார்பு, நுரையீரல் அடிப்பகுதி, இரைப்பை, செரிமானப் பை", humor: "Kapha (Water)" },
  5: { sign_en: "Leo (Simha)", sign_ta: "சிம்மம்", lord: "Sun", system_en: "Cardiovascular & Spinal Axis", system_ta: "இதயம், தண்டுவடம் மற்றும் முதுகெலும்பு", organs_en: "Heart, Upper Back, Spine, Aorta, Core Vital Energy", organs_ta: "இதயம், முதுகெலும்பு, தண்டுவடம், முதன்மை ரத்த நாளங்கள்", humor: "Pitta (Fire)" },
  6: { sign_en: "Virgo (Kanya)", sign_ta: "கன்னி", lord: "Mercury", system_en: "Digestive & Intestinal Axis", system_ta: "அடிவயிறு, குடல் மற்றும் செரிமான மண்டலம்", organs_en: "Lower Abdomen, Small & Large Intestines, Appendix, Spleen", organs_ta: "அடிவயிறு, சிறுகுடல், பெருங்குடல், குடல்வால்", humor: "Vata/Pitta (Earth)" },
  7: { sign_en: "Libra (Tula)", sign_ta: "துலாம்", lord: "Venus", system_en: "Renal & Pelvic Axis", system_ta: "சிறுநீரகம் மற்றும் இடுப்புப் பகுதி", organs_en: "Kidneys, Lumbar Region, Pelvis, Internal Reproductive Vasculature", organs_ta: "சிறுநீரகங்கள், இடுப்பு எலும்புப் பகுதி, கீழ்முதுகு", humor: "Vata (Air)" },
  8: { sign_en: "Scorpio (Vrishchika)", sign_ta: "விருச்சிகம்", lord: "Mars", system_en: "Excretory & Reproductive Axis", system_ta: "இனப்பெருக்கம் மற்றும் கழிவு மண்டலம்", organs_en: "External Genitalia, Excretory Organs, Rectum, Bladder, Prostate", organs_ta: "இனப்பெருக்க உறுப்புகள், மலக்குடல், சிறுநீர்ப்பை", humor: "Kapha/Pitta (Water)" },
  9: { sign_en: "Sagittarius (Dhanus)", sign_ta: "தனுசு", lord: "Jupiter", system_en: "Hepato-Femoral Axis", system_ta: "இடுப்பு மூட்டு மற்றும் தொடைகள்", organs_en: "Hips, Thighs, Femoral Arteries, Sciatic Nerve, Hepatic System", organs_ta: "இடுப்பு, தொடைகள், தொடை ரத்த நாளங்கள், இடுப்பு நரம்புகள்", humor: "Pitta (Fire)" },
  10: { sign_en: "Capricorn (Makara)", sign_ta: "மகரம்", lord: "Saturn", system_en: "Skeletal & Articular Axis", system_ta: "முழங்கால், மூட்டுகள் மற்றும் எலும்புக் கூடு", organs_en: "Knees, Knee Caps, Skeletal System, Bones, Joints, Skin Barrier", organs_ta: "முழங்கால்கள், எலும்புகள், மூட்டு இணைப்புகள், தோல் பாதுகாப்பு", humor: "Vata (Earth)" },
  11: { sign_en: "Aquarius (Kumbha)", sign_ta: "கும்பம்", lord: "Saturn", system_en: "Circulatory & Crural Axis", system_ta: "கணுக்கால், கெண்டைக்கால் மற்றும் ரத்த ஓட்டம்", organs_en: "Calves, Shins, Ankles, Peripheral Circulation, Oxygen Transport", organs_ta: "கெண்டைக் கால்கள், கணுக்கால்கள், ரத்த ஓட்ட மண்டலம்", humor: "Vata (Air)" },
  12: { sign_en: "Pisces (Meena)", sign_ta: "மீனம்", lord: "Jupiter", system_en: "Pedal & Lymphatic Axis", system_ta: "பாதங்கள் மற்றும் நிணநீர் மண்டலம்", organs_en: "Feet, Toes, Lymphatic Circulation, Left Eye, Sleep Induction", organs_ta: "பாதங்கள், கால்விரல்கள், நிணநீர் திரவம், இடது கண்", humor: "Kapha (Water)" },
};

export const PLANET_ANATOMY_GOVERNANCE: Record<string, {
  organs_en: string; organs_ta: string; dosha: string; governance: string;
}> = {
  Sun: { organs_en: "Heart, Bones, Vital Force, Head, Right Eye (day)", organs_ta: "இதயம், எலும்புகள், உயிர்ச்சத்து, தலை, வலது கண்", dosha: "Pitta (Bile / Heat)", governance: "Vitality, circulation, central cardiac rhythm" },
  Moon: { organs_en: "Bodily Fluids, Blood Plasma, Stomach, Breasts, Left Eye", organs_ta: "நீர்ச்சத்து, ரத்த பிளாஸ்மா, இரைப்பை, மார்பகம், இடது கண்", dosha: "Kapha / Vata (Fluids)", governance: "Emotional somaticization, hydration, lymphatic rhythm" },
  Mars: { organs_en: "Red Blood Cells, Bone Marrow, Muscular Tone, Cranial Base", organs_ta: "சிவப்பு ரத்த அணுக்கள், எலும்பு மச்சை, தசைகள், பித்தம்", dosha: "Pitta (Inflammatory)", governance: "Cellular defense, inflammation, acute trauma repair" },
  Mercury: { organs_en: "Nervous System, Skin Epidermis, Bronchi, Vocal Organs", organs_ta: "நரம்பு மண்டலம், தோல், மூச்சுக்குழாய், குரல்வளை", dosha: "Tridosha (Equi-balanced)", governance: "Neurotransmitter signaling, skin respiration, coordination" },
  Jupiter: { organs_en: "Liver, Gallbladder, Pancreas, Arteries, Fat Tissue (Medas)", organs_ta: "கல்லீரல், பித்தப்பை, கணையம், கொழுப்பு திசுக்கள், காதுகள்", dosha: "Kapha (Nutritive)", governance: "Metabolism, hepatic detoxification, cellular replenishment" },
  Venus: { organs_en: "Kidneys, Endocrine Hormones, Reproductive Fluids", organs_ta: "சிறுநீரகம், ஹார்மோன்கள், இனப்பெருக்க திரவம், கண் பார்வை", dosha: "Kapha / Vata", governance: "Osmotic regulation, hormonal homeostasis, sensory ease" },
  Saturn: { organs_en: "Skeletal System, Joints, Teeth, Chronic Nerve Wind", organs_ta: "எலும்புகள், மூட்டு இணைப்புகள், பற்கள், வாத மண்டலம்", dosha: "Vata (Cold / Dry / Chronic)", governance: "Structural endurance, degenerative buffering, cellular aging" },
  Rahu: { organs_en: "Immune Matrix, Environmental Allergens, Subtle Toxic Strains", organs_ta: "ஒவ்வாமை (அலர்ஜி), கண்டறிய கடினமான உடல் நிலைகள்", dosha: "Vata / Pitta", governance: "Immunological hypersensitivity, neuro-endocrine anomalies" },
  Ketu: { organs_en: "Microbial Resistance, Autoimmune Signatures, Inflammatory Fevers", organs_ta: "நுண்ணுயிர் தொற்று எதிர்ப்பு, வைரஸ் பாதிப்பு, திடீர் உஷ்ணம்", dosha: "Pitta (Intense heat)", governance: "Deep cellular immunity, sudden diagnostic inflection points" },
};

function checkPlanetDrishtiOnHouse(sourceHouse: number, targetHouse: number, planet: string): boolean {
  const diff = ((targetHouse - sourceHouse + 12) % 12) + 1;
  if (planet === "Mars") return diff === 4 || diff === 7 || diff === 8;
  if (planet === "Jupiter" || planet === "Rahu" || planet === "Ketu") return diff === 5 || diff === 7 || diff === 9;
  if (planet === "Saturn") return diff === 3 || diff === 7 || diff === 10;
  return diff === 7;
}

export function evaluateMedicalAstrologyClient(
  horoscope: HoroscopeResponse,
  kp?: KpResponse | null,
  dasa?: DasaResponse | null,
  liveTransits?: LiveTransitsResponse | null
): MedicalAstrologyResponse {
  const ascSignIdx = horoscope.ascendant.sign_index;

  // Build house to sign & sign to house mappings
  const houseToSign: Record<number, number> = {};
  const signToHouse: Record<number, number> = {};
  for (let h = 1; h <= 12; h++) {
    const s = ((ascSignIdx - 1 + (h - 1)) % 12) + 1;
    houseToSign[h] = s;
    signToHouse[s] = h;
  }

  // Planetary house occupancies & sign locations
  const planetHouse: Record<string, number> = {};
  const planetSign: Record<string, number> = {};
  const houseOccupants: Record<number, string[]> = {};
  for (let h = 1; h <= 12; h++) houseOccupants[h] = [];

  for (const p of horoscope.planets) {
    const s = p.sign_index;
    const h = signToHouse[s] || (((s - ascSignIdx + 12) % 12) + 1);
    planetHouse[p.name] = h;
    planetSign[p.name] = s;
    if (houseOccupants[h]) houseOccupants[h].push(p.name);
  }

  // Helper for house analysis
  function analyzeHouse(hNum: number): HouseHealthAnalysis {
    const sIdx = houseToSign[hNum];
    const sNameEn = SIGN_NAMES_EN[sIdx] || `Sign ${sIdx}`;
    const sNameTa = SIGN_NAMES_TA[sIdx] || `ராசி ${sIdx}`;
    const lord = SIGN_LORDS[sIdx] || "Unknown";
    const lordH = planetHouse[lord] || null;
    const lordS = planetSign[lord] || null;
    const lordSignName = lordS ? SIGN_NAMES_EN[lordS] : null;

    // Dignity
    let dignity = "Normal";
    if (lordS === EXALTATION_SIGNS[lord]) dignity = "Exalted (Uccha)";
    else if (lordS === DEBILITATION_SIGNS[lord]) dignity = "Debilitated (Neecha)";
    else if (OWN_SIGNS[lord]?.includes(lordS || 0)) dignity = "Own Sign (Swa-kshetra)";

    // Occupants and aspects
    const occ = houseOccupants[hNum] || [];
    const asp: string[] = [];
    for (const [pName, pHouse] of Object.entries(planetHouse)) {
      if (checkPlanetDrishtiOnHouse(pHouse, hNum, pName)) {
        asp.push(pName);
      }
    }

    const aff: string[] = [];
    const mit: string[] = [];

    const malOcc = occ.filter((p) => NATURAL_MALEFICS.has(p));
    const benOcc = occ.filter((p) => NATURAL_BENEFICS.has(p));
    if (malOcc.length > 0) aff.push(`Occupied by natural malefic(s): ${malOcc.join(", ")}`);
    if (benOcc.length > 0) mit.push(`Occupied by natural benefic(s): ${benOcc.join(", ")}`);

    const malAsp = asp.filter((p) => NATURAL_MALEFICS.has(p));
    const benAsp = asp.filter((p) => NATURAL_BENEFICS.has(p));
    if (malAsp.length > 0) aff.push(`Aspected by natural malefic(s): ${malAsp.join(", ")}`);
    if (benAsp.length > 0) mit.push(`Aspected by natural benefic(s): ${benAsp.join(", ")}`);

    if (dignity.startsWith("Debilitated")) aff.push(`House lord ${lord} is debilitated in ${lordSignName}`);
    if (dignity.startsWith("Exalted")) mit.push(`House lord ${lord} is exalted in ${lordSignName}`);
    if (dignity.startsWith("Own")) mit.push(`House lord ${lord} is fortified in own sign ${lordSignName}`);

    const anat = KALAPURUSHA_ANATOMY[sIdx] || { system_en: "General Body", system_ta: "பொது உடலமைப்பு" };

    let sumEn = "";
    let sumTa = "";
    if (hNum === 1) {
      if (mit.length > 0 && aff.length === 0) {
        sumEn = "Lagna and its lord are well-fortified, indicating robust natural vitality and strong recuperative capacity.";
        sumTa = "லக்னமும் லக்னாதிபதியும் பலம் பெற்றுள்ளதால் சிறந்த உடலமைப்பு, வலிமையான நோய் எதிர்ப்பு மற்றும் விரைவான குணமடையும் தன்மை அமைகிறது.";
      } else if (aff.length > 0 && mit.length === 0) {
        sumEn = "Lagna receives stress factors; classical texts advise conscious physical conditioning, balanced diet, and rest.";
        sumTa = "லக்னத்திற்கு அசுப தொடர்புகள் உள்ளதால் உடற்பயிற்சி, சத்தான உணவு மற்றும் போதுமான ஓய்வு மூலம் ஆரோக்கியத்தைப் பேண பாரம்பரிய சாஸ்திரங்கள் அறிவுறுத்துகின்றன.";
      } else {
        sumEn = "Lagna displays balanced vitality; natural resilience is supported by planetary mitigations.";
        sumTa = "லக்னம் சமநிலையான உடற்பலத்தைக் காட்டுகிறது; சுப பார்வைகள் மற்றும் பலங்களால் ஆரோக்கியம் பாதுகாக்கப்படுகிறது.";
      }
    } else if (hNum === 6) {
      if (malOcc.length > 0) {
        sumEn = `Natural malefics (${malOcc.join(", ")}) in the 6th house classically bestow formidable power to conquer diseases and enemies, alongside periodic heat notices.`;
        sumTa = `6-ம் பாவத்தில் அசுப கிரகங்கள் (${malOcc.join(", ")}) இருப்பது நோய்களை வெல்லும் அபார எதிர்ப்பு சக்தியைத் தரும்.`;
      } else if (benOcc.length > 0) {
        sumEn = `Natural benefics (${benOcc.join(", ")}) in the 6th house protect through gentle recovery and responsiveness to healthcare guidance.`;
        sumTa = `6-ம் பாவத்தில் சுப கிரகங்கள் (${benOcc.join(", ")}) இருப்பது மருத்துவ ஆலோசனைகளுக்கு சிறந்த முறையில் உடல் ஒத்துழைத்து குணமாகும் தன்மையைக் குறிக்கும்.`;
      } else {
        sumEn = "6th house (Roga Bhava) is undisturbed by occupants, with health conditions governed primarily by its lord and aspects.";
        sumTa = "6-ம் பாவம் நேரடி கிரக ஆக்கிரமிப்பு இன்றி உள்ளது; இதன் பலன்கள் அதிபதியின் நிலை மற்றும் பார்வைகளால் தீர்மானிக்கப்படுகின்றன.";
      }
    } else if (hNum === 8) {
      sumEn = mit.length > 0
        ? "8th house (Ayur Bhava) is protected by benefic factors, traditionally conferring longevity and cellular regeneration."
        : "8th house governs chronic endurance, cellular recovery, and unexpected stress thresholds.";
      sumTa = mit.length > 0
        ? "8-ம் பாவம் (ஆயுள் பாவம்) சுப தொடர்புகளால் பாதுகாக்கப்படுவதால் நீண்ட ஆயுளும், செல்களின் மீளுருவாக்கமும் உறுதி செய்யப்படுகின்றன."
        : "8-ம் பாவம் நீண்டகால சகிப்புத்தன்மை, உடல் ஆற்றல் சேமிப்பு மற்றும் திடீர் மாற்றங்களை நிர்வகிக்கிறது.";
    } else {
      sumEn = mit.length > 0
        ? "12th house (Vyaya Bhava) is supported by benefics, indicating restful recuperation and quick discharge from medical facilities."
        : "12th house governs sleep quality, lymphatic drainage, and health-related expenditures.";
      sumTa = mit.length > 0
        ? "12-ம் பாவம் சுப பலம் பெற்றுள்ளதால் ஆழ்ந்த தூக்கம், சிறந்த ஓய்வு மற்றும் சிகிச்சையிலிருந்து விரைவான குணம் பெறுதல் அமையும்."
        : "12-ம் பாவம் தூக்கத்தின் தரம், நிணநீர் ஓட்டம் மற்றும் ஆரோக்கியத்திற்கான நற்செலவுகளைக் குறிக்கிறது.";
    }

    return {
      house_number: hNum,
      sign_index: sIdx,
      sign_name_en: sNameEn,
      sign_name_ta: sNameTa,
      lord,
      lord_house: lordH,
      lord_sign: lordSignName,
      lord_dignity: dignity,
      occupants: occ,
      aspecting_planets: asp,
      anatomical_system_en: anat.system_en,
      anatomical_system_ta: anat.system_ta,
      traditional_summary_en: sumEn,
      traditional_summary_ta: sumTa,
      afflictions: aff,
      mitigations: mit,
    };
  }

  const h1 = analyzeHouse(1);
  const h6 = analyzeHouse(6);
  const h8 = analyzeHouse(8);
  const h12 = analyzeHouse(12);

  // Evaluate classical triggered rules
  const triggeredRules: MedicalRule[] = [];
  const conflictingIndications: string[] = [];

  // Single-planet in 6th rules
  const grahasIn6 = houseOccupants[6] || [];
  for (const p of grahasIn6) {
    const gov = PLANET_ANATOMY_GOVERNANCE[p];
    triggeredRules.push({
      id: `bphs_17_${p.toLowerCase()}_6th`,
      name: `${p} in 6th House (Classical Rogaphala)`,
      name_tamil: `6-ம் பாவத்தில் ${p} (பாரம்பரிய ரோக பலன்)`,
      source: "Brihat Parashara Hora Shastra",
      chapter_verse: "Chapter 17, Verses 1–16",
      category: "Vedic Birth Chart",
      system: "vedic",
      required_placements: `${p} occupies House 6 from Lagna`,
      mandatory_conditions: [`${p} is placed in House 6`],
      traditional_interpretation: `Traditional texts record that ${p} in the 6th house influences the ${gov?.organs_en || "bodily systems"}. In an Upachaya house, it activates immune defense mechanisms against ailments.`,
      interpretation_tamil: `6-ம் பாவத்தில் ${p} அமர்வது ${gov?.organs_ta || "உடல் உறுப்புகள்"} சார்ந்த செயல்பாடுகளைக் குறிக்கும். உபசெய ஸ்தானத்தில் இது நோய் எதிர்ப்பு சக்தியைத் தூண்டுகிறது.`,
      anatomical_system: gov?.organs_en || "General Bodily Systems",
      modifiers: "Benefic aspects from Jupiter enhance vitality.",
      conflicting_indications: "Arishta Bhanga from strong benefics in Kendras protects health.",
      is_active: true,
      status: "Qualifying",
      triggered_positions: [`${p} in House 6 (${SIGN_NAMES_EN[houseToSign[6]]})`],
      planets_involved: [p],
      relevant_houses: [6],
      conditions: [{ condition: `${p} occupies House 6`, passed: true, detail: `${p} is located at House 6.` }],
    });
  }

  // 6th lord in Lagna
  const l6 = SIGN_LORDS[houseToSign[6]];
  if (planetHouse[l6] === 1) {
    triggeredRules.push({
      id: "bphs_17_17_lord6_in_1",
      name: "6th Lord in Lagna (Constitution Closely Linked to Immunity)",
      name_tamil: "லக்னத்தில் 6-ம் அதிபதி (நோய் எதிர்ப்பு மற்றும் உடலமைப்பு இணைப்பு)",
      source: "Brihat Parashara Hora Shastra",
      chapter_verse: "Chapter 17, Verse 17",
      category: "Vedic House Lord",
      system: "vedic",
      required_placements: "6th Lord occupies House 1 (Lagna)",
      mandatory_conditions: ["6th lord is placed in house 1"],
      traditional_interpretation: "When the 6th lord resides in the 1st house, the physical body actively engages in building immune defense. Vitality strengthens as adulthood progresses, provided the Lagna lord is well-dignified.",
      interpretation_tamil: "6-ம் அதிபதி லக்னத்தில் இருப்பது, உடல் அமைப்பு நோய் எதிர்ப்பு ஆற்றலை சுயமாகக் கட்டமைப்பதைக் குறிக்கும். லக்னாதிபதி பலம் பெற்றிருந்தால் சிறந்த ஆரோக்கியம் கிட்டும்.",
      anatomical_system: "Head, Physical Constitution, General Immunity",
      modifiers: "Mitigated if 6th lord is also Lagna lord.",
      conflicting_indications: "Benefics in Kendras protect physical stamina and longevity.",
      is_active: true,
      status: "Qualifying",
      triggered_positions: [`6th Lord ${l6} placed in House 1 (Lagna)`],
      planets_involved: [l6],
      relevant_houses: [1, 6],
      conditions: [{ condition: "6th Lord placed in 1st house", passed: true, detail: `${l6} resides in House 1.` }],
    });
  }

  // 6th lord in 6th (Harsha Yoga)
  if (planetHouse[l6] === 6) {
    triggeredRules.push({
      id: "bphs_17_22_lord6_in_6",
      name: "6th Lord in 6th House (Harsha Yoga / Immunity Swa-kshetra)",
      name_tamil: "6-ம் அதிபதி 6-ல் ஆட்சி (ஹர்ஷ யோகம் / நோய் அழிக்கும் பலம்)",
      source: "Brihat Parashara Hora Shastra",
      chapter_verse: "Chapter 17, Verse 22",
      category: "Vedic House Lord",
      system: "vedic",
      required_placements: "6th Lord occupies 6th house in own sign",
      mandatory_conditions: ["6th lord in house 6"],
      traditional_interpretation: "6th lord in the 6th house forms the auspicious Harsha Yoga. Parashara states that the native possesses a strong constitution, sound digestive stamina, and natural immunity capable of dispelling bodily ailments swiftly.",
      interpretation_tamil: "6-ம் அதிபதி தன் சொந்த வீட்டில் 6-ல் ஆட்சி பெறுவது 'ஹர்ஷ யோகம்' எனப்படும். இது நோய்களை விரைவாக அழிக்கும் இயற்கையான உடற்பலத்தையும், நோய் எதிர்ப்பு சக்தியையும் அளிக்கும்.",
      anatomical_system: "Digestive Core, Intestinal Tract, Endogenous Immune Vitality",
      modifiers: "Free from malefic conjunction yields pristine stamina.",
      conflicting_indications: "None; this is a classical protective formation.",
      is_active: true,
      status: "Qualifying",
      triggered_positions: [`6th Lord ${l6} in own House 6`],
      planets_involved: [l6],
      relevant_houses: [6],
      conditions: [{ condition: "6th Lord in 6th house", passed: true, detail: `${l6} occupies House 6.` }],
    });
  }

  // Jupiter aspecting House 1 or 6 (Arishta Bhanga)
  const jupH = planetHouse["Jupiter"];
  if (jupH) {
    const asp1 = checkPlanetDrishtiOnHouse(jupH, 1, "Jupiter");
    const asp6 = checkPlanetDrishtiOnHouse(jupH, 6, "Jupiter");
    if (asp1 || asp6) {
      const targ = asp1 && asp6 ? "both House 1 and House 6" : asp1 ? "House 1 (Lagna)" : "House 6 (Roga Bhava)";
      conflictingIndications.push(`Classical Mitigation: Jupiter in H${jupH} casts aspect on ${targ}, conferring Arishta Bhanga immunity protection.`);
      triggeredRules.push({
        id: "arishta_bhanga_jupiter_aspect",
        name: "Jupiter Aspecting Lagna or 6th House (Arishta Bhanga Shield)",
        name_tamil: "லக்னம் அல்லது 6-ம் பாவத்திற்கு குரு பார்வை (அரிஷ்ட பங்க பாதுகாப்பு)",
        source: "Brihat Parashara Hora Shastra",
        chapter_verse: "Chapter 11, Verse 1",
        category: "Vedic Mitigation",
        system: "vedic",
        required_placements: "Jupiter casts 5th, 7th, or 9th aspect on House 1 or 6",
        mandatory_conditions: ["Jupiter aspects House 1 or 6"],
        traditional_interpretation: "Parashara declares that uncombust Jupiter aspecting the Ascendant or 6th house dissolves myriad bodily afflictions, conferring strong recuperative resilience and effective therapies.",
        interpretation_tamil: "லக்னத்தையோ 6-ம் வீட்டையோ பார்க்கும் குருவின் பார்வை ஆயிரக்கணக்கான நோய்களையும் அரிஷ்டங்களையும் அழித்துவிடும் என பராசரர் அருள்கிறார்.",
        anatomical_system: "Constitutional Immunity, Cellular Regeneration, Healing Receptivity",
        modifiers: "Exalted or own-sign Jupiter amplifies protective power.",
        conflicting_indications: "None; primary classical counter-measure.",
        is_active: true,
        status: "Qualifying",
        triggered_positions: [`Jupiter in H${jupH} aspecting ${targ}`],
        planets_involved: ["Jupiter"],
        relevant_houses: [jupH, asp1 ? 1 : 6],
        conditions: [{ condition: "Jupiter aspects House 1 or 6", passed: true, detail: `Jupiter in House ${jupH} aspects ${targ}.` }],
      });
    }
  }

  // Natural Benefics in Kendras
  const kendraBenefics: Array<{ planet: string; house: number }> = [];
  for (const b of ["Jupiter", "Venus", "Mercury"]) {
    const bh = planetHouse[b];
    if (bh && [1, 4, 7, 10].includes(bh)) kendraBenefics.push({ planet: b, house: bh });
  }
  if (kendraBenefics.length > 0) {
    const benStr = kendraBenefics.map((x) => `${x.planet} in H${x.house}`).join(", ");
    conflictingIndications.push(`Classical Longevity Citadel: Natural benefics in quadrant houses (${benStr}) sustain constitutional vitality.`);
    triggeredRules.push({
      id: "arishta_bhanga_benefics_kendras",
      name: "Natural Benefics in Kendras (Quadrants Sustaining Vital Longevity)",
      name_tamil: "கேந்திரங்களில் சுப கிரகங்கள் (நீண்ட ஆயுள் மற்றும் ஆரோக்கிய அரண்)",
      source: "Brihat Parashara Hora Shastra",
      chapter_verse: "Chapter 11, Verse 2",
      category: "Vedic Mitigation",
      system: "vedic",
      required_placements: "Natural benefics in houses 1, 4, 7, or 10",
      mandatory_conditions: ["At least one natural benefic in a Kendra house"],
      traditional_interpretation: "Natural benefics in quadrant houses form a classical citadel around constitutional vitality, guaranteeing longevity and cellular reserves.",
      interpretation_tamil: "1, 4, 7, 10 ஆகிய கேந்திர ஸ்தானங்களில் சுப கிரகங்கள் அமர்வது உடல் ஆரோக்கியத்திற்கு இரும்புக் கோட்டை போன்ற பாதுகாப்பைத் தரும்.",
      anatomical_system: "Vital Core Reserve, Long-term Constitutional Longevity",
      modifiers: "Multiple benefics in Kendras enhance vitality.",
      conflicting_indications: "None; primary life-preservation rule.",
      is_active: true,
      status: "Qualifying",
      triggered_positions: [benStr],
      planets_involved: kendraBenefics.map((x) => x.planet),
      relevant_houses: kendraBenefics.map((x) => x.house),
      conditions: [{ condition: "Natural benefics in Kendra", passed: true, detail: `Benefics in Kendras: ${benStr}.` }],
    });
  }

  // Kalapurusha anatomical audit
  const anatomicalMappings: AnatomicalSystemMapping[] = [];
  for (let s = 1; s <= 12; s++) {
    const info = KALAPURUSHA_ANATOMY[s];
    const h = signToHouse[s] || 0;
    const occ = houseOccupants[h] || [];
    const mal = occ.filter((p) => NATURAL_MALEFICS.has(p));
    const ben = occ.filter((p) => NATURAL_BENEFICS.has(p));

    let status: "Balanced" | "Afflicted" | "Mitigated" | "Neutral" = "Neutral";
    let obsEn = `No direct occupants in House ${h}; functions according to sign lord ${info.lord}.`;
    let obsTa = `நேரடி கிரக ஆக்கிரமிப்பு இன்றி உள்ளது; ராசிநாதன் ${info.lord}-ன் நிலைக்கு ஏற்ப செயல்படுகிறது.`;

    if (mal.length > 0 && ben.length === 0) {
      status = "Afflicted";
      obsEn = `Occupied by natural malefic(s) (${mal.join(", ")}) in House ${h}; classical texts suggest mindful care of ${info.organs_en}.`;
      obsTa = `வீடு ${h}-ல் அசுப கிரகங்கள் (${mal.join(", ")}) உள்ளதால் ${info.organs_ta} பகுதியில் கவனமும் பராமரிப்பும் தேவை.`;
    } else if (ben.length > 0 && mal.length === 0) {
      status = "Mitigated";
      obsEn = `Benefic presence (${ben.join(", ")}) in House ${h} nourishes and protects this anatomical zone.`;
      obsTa = `வீடு ${h}-ல் சுப கிரகங்கள் (${ben.join(", ")}) அமர்ந்து இந்த உடல் பகுதியை பலப்படுத்துகின்றன.`;
    } else if (ben.length > 0 && mal.length > 0) {
      status = "Balanced";
      obsEn = `Mixed influences in House ${h}; malefic strain is mitigated by benefic presence.`;
      obsTa = `வீடு ${h}-ல் சுப மற்றும் அசுப கிரகங்களின் கலவையான தாக்கம் காணப்படுகிறது.`;
    }

    anatomicalMappings.push({
      system_name_en: info.system_en,
      system_name_ta: info.system_ta,
      organs_en: info.organs_en,
      organs_ta: info.organs_ta,
      sign_governance: `${info.sign_en} (${s})`,
      planetary_governance: `${info.lord} (${info.humor})`,
      status,
      observations_en: obsEn,
      observations_ta: obsTa,
    });
  }

  const birthChartPerspective: BirthChartPerspective = {
    lagna_analysis: h1,
    sixth_house_analysis: h6,
    eighth_house_analysis: h8,
    twelfth_house_analysis: h12,
    triggered_rules: triggeredRules,
    conflicting_indications: conflictingIndications,
    anatomical_mappings: anatomicalMappings,
  };

  // Perspective B: Current Period Research
  let mahaLord = "Unknown";
  let bhuktiLord: string | null = null;
  let antaraLord: string | null = null;
  let startIso: string | null = null;
  let endIso: string | null = null;

  if (dasa?.active_period) {
    mahaLord = dasa.active_period.mahadasha;
    bhuktiLord = dasa.active_period.antardasha || null;
    antaraLord = dasa.active_period.pratyantardasha || null;
    startIso = dasa.active_period.target_date_iso || null;
  } else if (dasa?.birth_dasa_lord) {
    mahaLord = dasa.birth_dasa_lord;
  }

  const periodMatchingRules: MedicalRule[] = [];
  const activeLords = [mahaLord, bhuktiLord, antaraLord].filter((x): x is string => !!x && x !== "Unknown");
  for (const l of activeLords) {
    const gov = PLANET_ANATOMY_GOVERNANCE[l];
    if (gov) {
      periodMatchingRules.push({
        id: `active_period_${l.toLowerCase()}`,
        name: `Vimshottari Period of ${l} (Classical Anatomical Resonance)`,
        name_tamil: `${l} தசா-புத்தி காலம் (பாரம்பரிய உடல் உறுப்புத் தொடர்பு)`,
        source: "Brihat Parashara Hora Shastra & Phaladeepika",
        chapter_verse: "BPHS Dasa Phala; Phaladeepika Ch. 20",
        category: "Vedic Birth Chart",
        system: "vedic",
        required_placements: `Active period ruled by ${l}`,
        mandatory_conditions: [`${l} is currently operating as Dasa or Bhukti ruler`],
        traditional_interpretation: `Under the rulership of ${l}, classical texts observe traditional focus on the ${gov.organs_en}. Its natural humor is ${gov.dosha}. A well-placed ${l} enhances systemic vitality.`,
        interpretation_tamil: `${l} தசா-புத்தி காலத்தில் ${gov.organs_ta} மீது பாரம்பரிய கவனம் செலுத்தப்படுகிறது. இதன் சுபாவம் ${gov.dosha} ஆகும்.`,
        anatomical_system: gov.organs_en,
        modifiers: `${l} occupies House ${planetHouse[l] || 0} in natal chart.`,
        conflicting_indications: "Jupiter aspect on period lord ensures swift resolution of temporary fatigue.",
        is_active: true,
        status: "Qualifying",
        triggered_positions: [`${l} is currently active period lord`],
        planets_involved: [l],
        relevant_houses: [planetHouse[l] || 0],
        conditions: [{ condition: `${l} is active ruler`, passed: true, detail: `${l} rules current temporal window.` }],
      });
    }
  }

  // Live Transits
  const transitsList: TransitInfluence[] = [];
  if (liveTransits?.planets) {
    for (const tp of liveTransits.planets.slice(0, 9)) {
      const houseFromLagna = ((tp.sign_index - ascSignIdx + 12) % 12) + 1;
      const sEn = SIGN_NAMES_EN[tp.sign_index] || "";
      const sTa = SIGN_NAMES_TA[tp.sign_index] || "";
      transitsList.push({
        planet: tp.name,
        sign_index: tp.sign_index,
        sign_name_en: sEn,
        sign_name_ta: sTa,
        degree: Math.round(tp.degree_in_sign * 100) / 100,
        house_from_lagna: houseFromLagna,
        is_retrograde: tp.is_retrograde,
        traditional_symbolism_en: `Transiting ${sEn} (H${houseFromLagna} from natal Lagna)`,
        traditional_symbolism_ta: `லக்னத்திலிருந்து ${houseFromLagna}-ம் வீடான ${sTa}-ல் கோசாரம் செய்கிறது`,
      });
    }
  }

  const currentPeriodPerspective: CurrentPeriodPerspective = {
    mahadasha: mahaLord,
    bhukti: bhuktiLord,
    antara: antaraLord,
    start_date_iso: startIso,
    end_date_iso: endIso,
    matching_rules: periodMatchingRules,
    transits: transitsList,
    traditional_synthesis_en: `Active Vimshottari period is governed by ${mahaLord}${bhuktiLord ? ` with Bhukti of ${bhuktiLord}` : ""}${antaraLord ? ` and Antara of ${antaraLord}` : ""}. In traditional astrological research, health vitality during this temporal window is interpreted according to the natural humors and house lordships of these planets. This is an educational astrological perspective and does not forecast illness onset.`,
    traditional_synthesis_ta: `நடப்பு விம்சோத்தரி தசா நாதர்: ${mahaLord}${bhuktiLord ? `, புத்தி நாதர்: ${bhuktiLord}` : ""}${antaraLord ? `, அந்தர நாதர்: ${antaraLord}` : ""}. பாரம்பரிய ஜோதிட ஆராய்ச்சியின்படி இக்காலகட்டத்தின் உடல் பலம் இந்நாதர்களின் சுபாவம் மற்றும் ஆதிபத்தியங்களின் அடிப்படையில் விவரிக்கப்படுகிறது. இது கல்வி நோக்கிலான ஆய்வு மட்டுமே; நோயைக் கணிப்பது அல்ல.`,
  };

  // Perspective C: Historical Period Research
  const historicalPeriodsList: HistoricalPeriodItem[] = [];
  if (dasa?.dasa_tree) {
    for (const node of dasa.dasa_tree.slice(0, 9)) {
      const lord = node.lord;
      const gov = PLANET_ANATOMY_GOVERNANCE[lord];
      const ageStr = node.start_age && node.end_age ? `Age ${node.start_age} – ${node.end_age}` : "Documented span";
      historicalPeriodsList.push({
        period_name: `${lord} Mahadasha`,
        lord,
        sub_lord: null,
        start_date_iso: node.start_date_iso || "",
        end_date_iso: node.end_date_iso || "",
        age_range: ageStr,
        traditional_rules: [],
        traditional_notes_en: `Historical Vimshottari Mahadasha of ${lord}. Classical texts associate this planetary phase with ${gov?.organs_en || "vital reserves"}. Astrological records trace bodily rhythm shifts without inferring diagnosed historical ailments.`,
        traditional_notes_ta: `${lord} மகா தசை காலம். பாரம்பரிய நூல்கள் இக்காலகட்டத்தை ${gov?.organs_ta || "உடற்பலம்"}-உடன் தொடர்புபடுத்துகின்றன. இது கடந்த கால ஜோதிட ஆய்வு மட்டுமே; கடந்த கால நோய்களைக் குறிப்பது அல்ல.`,
      });
    }
  }

  const historicalPeriodPerspective: HistoricalPeriodPerspective = {
    periods: historicalPeriodsList,
  };

  // KP Analytical System
  let kpAnalysis: KpMedicalAnalysis | null = null;
  if (kp?.cuspal_analysis && kp.cuspal_analysis.length >= 6) {
    // 1. Planetary positions map (to resolve CSL planet's Star Lord)
    const planetMap: Record<string, any> = {};
    if (Array.isArray(kp.planetary_positions)) {
      for (const p of kp.planetary_positions) {
        if (p?.planet) planetMap[p.planet] = p;
      }
    }

    // 2. Cusp details map
    const cuspMap: Record<number, any> = {};
    for (const c of kp.cuspal_analysis) cuspMap[c.house] = c;

    // 3. Significators mapping
    const sigMap: Record<string, number[]> = {};
    const sigDetailsMap: Record<string, SignificatorSourceDetail[]> = {};

    if (Array.isArray(kp.significators)) {
      for (const s of kp.significators) {
        if (!s?.planet) continue;
        const pName = s.planet;
        const houses = new Set<number>();
        const details: SignificatorSourceDetail[] = [];

        // Primary: signified_houses
        if (Array.isArray(s.signified_houses)) {
          for (const h of s.signified_houses) {
            const hNum = Number(h);
            if (!isNaN(hNum)) houses.add(hNum);
          }
        }

        // Strength order / mechanisms
        if (Array.isArray(s.strength_order)) {
          for (const entry of s.strength_order) {
            const hNum = Number(entry?.house);
            const tType = String(entry?.type || "");
            if (hNum && !isNaN(hNum)) {
              houses.add(hNum);
              const pStar = planetMap[pName]?.star_lord || "";
              let channel = `${pName} (${tType})`;

              let lvlEn = `Significator (${tType})`;
              let lvlTa = `காரகம் (${tType})`;
              let descEn = `${pName} signifies House ${hNum} via ${tType}.`;
              let descTa = `${pName} ${tType} வாயிலாக ${hNum}-ம் பாவத்தைக் குறிக்கிறது.`;

              if (tType === "StarLord") {
                lvlEn = "Level 1 / 3 (Star Lord Agency)";
                lvlTa = "நிலை 1 / 3 (நட்சத்திர நாதர் வழி காரகம்)";
                channel = pStar ? `${pName} -> ${pStar}` : `${pName} (Star Lord)`;
                descEn = `${pName} signifies House ${hNum} through star lord ${pStar || "agency"}.`;
                descTa = `${pName} தனது நட்சத்திர நாதர் ${pStar || ""} மூலம் ${hNum}-ம் பாவத்தைக் குறிக்கிறது.`;
              } else if (tType === "Occupant") {
                lvlEn = "Level 2 (Planetary Occupation)";
                lvlTa = "நிலை 2 (நேரடி பாவக அமர்வு)";
                channel = `${pName} (Direct)`;
                descEn = `${pName} physically occupies House ${hNum} in Placidus sidereal division.`;
                descTa = `${pName} நேரடி பாகைப்படி ${hNum}-ம் பாவத்தில் அமர்ந்துள்ளது.`;
              } else if (tType === "Owner") {
                lvlEn = "Level 4 (House Ownership / Lordship)";
                lvlTa = "நிலை 4 (பாவக ஆதிபத்தியம் / உரிமை)";
                channel = `${pName} (Lord)`;
                descEn = `${pName} rules the sign on the cusp of House ${hNum}.`;
                descTa = `${pName} ${hNum}-ம் பாவ ஆரம்ப முனையின் ராசி நாதராக விளங்குகிறது.`;
              }

              details.push({
                house: hNum,
                source_type: tType,
                planet_channel: channel,
                level_name_en: lvlEn,
                level_name_ta: lvlTa,
                description_en: descEn,
                description_ta: descTa,
              });
            }
          }
        }

        // Check level_a..d fallbacks
        const levelDefs = [
          { key: "level_a", type: "StarLord", en: "Level A (Star of Occupant)", ta: "நிலை A (அமர்ந்த கிரகத்தின் நட்சத்திரம்)" },
          { key: "level_b", type: "Occupant", en: "Level B (Occupant)", ta: "நிலை B (நேரடி அமர்வு)" },
          { key: "level_c", type: "StarLord", en: "Level C (Star of House Lord)", ta: "நிலை C (அதிபதியின் நட்சத்திரம்)" },
          { key: "level_d", type: "Owner", en: "Level D (House Lord)", ta: "நிலை D (பாவக அதிபதி)" },
        ] as const;

        for (const def of levelDefs) {
          const val = (s as any)[def.key];
          if (Array.isArray(val)) {
            for (const hVal of val) {
              const hNum = Number(hVal);
              if (!isNaN(hNum)) {
                houses.add(hNum);
                if (!details.some((d) => d.house === hNum && d.source_type === def.type)) {
                  const pStar = planetMap[pName]?.star_lord || "";
                  const channel = (def.type === "StarLord" && pStar) ? `${pName} -> ${pStar}` : `${pName} (${def.type})`;
                  details.push({
                    house: hNum,
                    source_type: def.type,
                    planet_channel: channel,
                    level_name_en: def.en,
                    level_name_ta: def.ta,
                    description_en: `${pName} signifies House ${hNum} via ${def.en}.`,
                    description_ta: `${pName} ${def.ta} வாயிலாக ${hNum}-ம் பாவத்தைக் குறிக்கிறது.`,
                  });
                }
              }
            }
          }
        }

        sigMap[pName] = Array.from(houses).sort((a, b) => a - b);
        sigDetailsMap[pName] = details;
      }
    }

    // 4. Complement with house_significators (Bhaav Nirdeshan)
    if (Array.isArray(kp.house_significators)) {
      for (const hs of kp.house_significators) {
        const hNum = Number(hs?.house);
        if (!hNum || isNaN(hNum)) continue;

        const tiers = [
          { key: "level_a", type: "StarLord", en: "Level A (Star of Occupant)", ta: "நிலை A (அமர்ந்த கிரகத்தின் நட்சத்திரம்)" },
          { key: "level_b", type: "Occupant", en: "Level B (House Occupant)", ta: "நிலை B (நேரடி பாவக அமர்வு)" },
          { key: "level_c", type: "StarLord", en: "Level C (Star of House Lord)", ta: "நிலை C (அதிபதியின் நட்சத்திரம்)" },
          { key: "level_d", type: "Owner", en: "Level D (House Lord)", ta: "நிலை D (பாவக அதிபதி)" },
        ] as const;

        for (const tier of tiers) {
          const pList = (hs as any)[tier.key];
          if (Array.isArray(pList)) {
            for (const pl of pList) {
              if (typeof pl === "string" && pl) {
                if (!sigMap[pl]) sigMap[pl] = [];
                if (!sigMap[pl].includes(hNum)) {
                  sigMap[pl].push(hNum);
                  sigMap[pl].sort((a, b) => a - b);
                }
                if (!sigDetailsMap[pl]) sigDetailsMap[pl] = [];
                if (!sigDetailsMap[pl].some((d) => d.house === hNum && d.source_type === tier.type)) {
                  const plStar = planetMap[pl]?.star_lord || "";
                  const channel = (tier.type === "StarLord" && plStar) ? `${pl} -> ${plStar}` : `${pl} (${tier.type})`;
                  sigDetailsMap[pl].push({
                    house: hNum,
                    source_type: tier.type,
                    planet_channel: channel,
                    level_name_en: tier.en,
                    level_name_ta: tier.ta,
                    description_en: `${pl} signifies House ${hNum} as ${tier.en}.`,
                    description_ta: `${pl} ${tier.ta} வாயிலாக ${hNum}-ம் பாவத்தைக் குறிக்கிறது.`,
                  });
                }
              }
            }
          }
        }
      }
    }

    function buildKpCsl(hNum: number): KpCslAnalysis {
      const cd = cuspMap[hNum];
      if (!cd) {
        return {
          cusp_number: hNum,
          csl_planet: "Unavailable",
          csl_star_lord: "Unavailable",
          star_lord: "Unavailable",
          signified_houses: [],
          signification_details: [],
          primary_signification_en: `Cusp ${hNum} data unavailable in KP chart.`,
          primary_signification_ta: `கே.பி. அட்டவணையில் ${hNum}-ம் பாவத் தரவு கிடைக்கவில்லை.`,
          anatomical_rulership_en: "General Bodily Zone",
          anatomical_rulership_ta: "பொது உடலமைப்பு",
          recovery_status: "data_unavailable",
          disease_status: "data_unavailable",
          chronic_status: "data_unavailable",
          hospitalization_status: "data_unavailable",
          recovery_signified: false,
          disease_signified: false,
          chronic_signified: false,
          hospitalization_signified: false,
          is_data_available: false,
          missing_data_reason: `Cusp ${hNum} not found in KP cuspal analysis`,
          calculation_provenance: "KP Placidus Cusps & 4-tier Grah Nirdeshan (KP Reader IV reference framework)",
        };
      }

      const csl = cd?.sub_lord || "";
      const cuspStarL = cd?.star_lord || "";
      const cuspDeg = typeof cd?.cusp_degree === "number" ? cd.cusp_degree : undefined;
      const signN = cd?.sign_name || undefined;
      const signL = cd?.sign_lord || undefined;
      const subL = cd?.sub_sub_lord || undefined;

      if (!csl) {
        return {
          cusp_number: hNum,
          cusp_degree: cuspDeg,
          sign_name: signN,
          sign_lord: signL,
          cusp_star_lord: cuspStarL,
          csl_planet: "Unavailable",
          csl_star_lord: "Unavailable",
          star_lord: "Unavailable",
          signified_houses: [],
          signification_details: [],
          primary_signification_en: `Sub-Lord for Cusp ${hNum} is unavailable in KP chart.`,
          primary_signification_ta: `${hNum}-ம் பாவ உப அதிபதி (CSL) கே.பி. அட்டவணையில் கிடைக்கவில்லை.`,
          anatomical_rulership_en: "General Bodily Zone",
          anatomical_rulership_ta: "பொது உடலமைப்பு",
          recovery_status: "data_unavailable",
          disease_status: "data_unavailable",
          chronic_status: "data_unavailable",
          hospitalization_status: "data_unavailable",
          recovery_signified: false,
          disease_signified: false,
          chronic_signified: false,
          hospitalization_signified: false,
          is_data_available: false,
          missing_data_reason: `Sub-Lord (CSL) missing for Cusp ${hNum}`,
          calculation_provenance: "KP Placidus Cusps & 4-tier Grah Nirdeshan (KP Reader IV reference framework)",
        };
      }

      // Star lord of the CSL planet from planetary positions
      const cslPlanetData = planetMap[csl];
      const cslStarL = cslPlanetData?.star_lord || cuspStarL || csl;

      const sigHouses = sigMap[csl] || [];
      const detailsSig = sigDetailsMap[csl] || [];

      if (sigHouses.length === 0) {
        return {
          cusp_number: hNum,
          cusp_degree: cuspDeg,
          sign_name: signN,
          sign_lord: signL,
          cusp_star_lord: cuspStarL,
          csl_planet: csl,
          csl_star_lord: cslStarL,
          star_lord: cslStarL,
          sub_lord: subL,
          signified_houses: [],
          signification_details: [],
          primary_signification_en: `Cusp ${hNum} Sub-Lord is ${csl} (in star of ${cslStarL}), but planetary house significations are unavailable.`,
          primary_signification_ta: `${hNum}-ம் பாவ CSL ${csl} (${cslStarL} நட்சத்திரம்); ஆனால் பாவகக் காரகத்துவத் தரவுகள் கிடைக்கவில்லை.`,
          anatomical_rulership_en: "General Bodily Zone",
          anatomical_rulership_ta: "பொது உடலமைப்பு",
          recovery_status: "data_unavailable",
          disease_status: "data_unavailable",
          chronic_status: "data_unavailable",
          hospitalization_status: "data_unavailable",
          recovery_signified: false,
          disease_signified: false,
          chronic_signified: false,
          hospitalization_signified: false,
          is_data_available: false,
          missing_data_reason: `House significations unavailable for CSL planet ${csl}`,
          calculation_provenance: "KP Placidus Cusps & 4-tier Grah Nirdeshan (KP Reader IV reference framework)",
        };
      }

      const recHouses = [1, 5, 11].filter((h) => sigHouses.includes(h));
      const disHouses = sigHouses.includes(6) ? [6] : [];
      const chrHouses = sigHouses.includes(8) ? [8] : [];
      const hospHouses = sigHouses.includes(12) ? [12] : [];

      const rec = recHouses.length > 0;
      const dis = disHouses.length > 0;
      const chrAff = chrHouses.length > 0;
      const hosp = hospHouses.length > 0;

      const recStatus: "present" | "not_found" = rec ? "present" : "not_found";
      const disStatus: "present" | "not_found" = dis ? "present" : "not_found";
      const chrStatus: "present" | "not_found" = chrAff ? "present" : "not_found";
      const hospStatus: "present" | "not_found" = hosp ? "present" : "not_found";

      const gov = PLANET_ANATOMY_GOVERNANCE[csl];
      const anatEn = gov?.organs_en || "General Bodily Zone";
      const anatTa = gov?.organs_ta || "பொது உடலமைப்பு";

      const housesStr = sigHouses.join(", ");

      let primEn = `Cusp ${hNum} Sub-Lord ${csl} (star: ${cslStarL}) signifies houses ${housesStr}.`;
      let primTa = `${hNum}-ம் பாவ CSL ${csl} (${cslStarL} நட்சத்திரத்தில்) பாவங்கள் ${housesStr}-ஐக் குறிக்கிறது.`;

      if (hNum === 6) {
        const partsEn = [`6th Cusp Sub-Lord ${csl} (in star of ${cslStarL}) signifies houses ${housesStr}.`];
        const partsTa = [`6-ம் பாவ உப அதிபதி (CSL) ${csl} (${cslStarL} நட்சத்திரத்தில்) பாவங்கள் ${housesStr}-ஐக் குறிக்கிறது.`];

        if (rec) {
          partsEn.push(`Recovery / negation houses [${recHouses.join(", ")}] are present in calculated significations, indicating recuperative resilience.`);
          partsTa.push(`குணமடைதலைக் குறிக்கும் பாவங்கள் [${recHouses.join(", ")}] காரகத்துவங்களில் உள்ளதால் விரைவான நலம் பெறும் ஆற்றல் அமைகிறது.`);
        } else {
          partsEn.push("Recovery houses (1, 5, 11) are not found in current significations.");
          partsTa.push("குணமடைதல் பாவங்கள் (1, 5, 11) இந்த காரகத்துவங்களில் அமையவில்லை.");
        }

        const suscTagsEn: string[] = [];
        const suscTagsTa: string[] = [];
        if (dis) {
          suscTagsEn.push("House 6 (acute symptoms)");
          suscTagsTa.push("6-ம் பாவம் (நோய் நிலை)");
        }
        if (chrAff) {
          suscTagsEn.push("House 8 (chronic vulnerability / surgical diagnostics)");
          suscTagsTa.push("8-ம் பாவம் (நீண்டகால நிலை / அறுவை சிகிச்சை)");
        }
        if (hosp) {
          suscTagsEn.push("House 12 (clinical care / hospitalization)");
          suscTagsTa.push("12-ம் பாவம் (மருத்துவமனை அனுமதி / படுக்கை ஓய்வு)");
        }

        if (suscTagsEn.length > 0) {
          partsEn.push(`Susceptibility indications: ${suscTagsEn.join(", ")} are present; classical KP advises proactive care.`);
          partsTa.push(`கவனிக்கப்பட வேண்டியவை: ${suscTagsTa.join(", ")} காரகத்துவத்தில் உள்ளதால் உரிய உடல்நலப் பராமரிப்பு அவசியம்.`);
        } else {
          partsEn.push("Susceptibility houses (6, 8, 12) are not found in the primary CSL significations.");
          partsTa.push("பாதிப்பு பாவங்கள் (6, 8, 12) இந்த CSL காரகத்துவங்களில் அமையவில்லை.");
        }

        primEn = partsEn.join(" ").replace(/\{csl\}/gi, csl).replace(/\{cslStarL\}/gi, cslStarL);
        primTa = partsTa.join(" ").replace(/\{csl\}/gi, csl).replace(/\{cslStarL\}/gi, cslStarL);
      } else {
        primEn = primEn.replace(/\{csl\}/gi, csl).replace(/\{cslStarL\}/gi, cslStarL);
        primTa = primTa.replace(/\{csl\}/gi, csl).replace(/\{cslStarL\}/gi, cslStarL);
      }

      return {
        cusp_number: hNum,
        cusp_degree: cuspDeg,
        sign_name: signN,
        sign_lord: signL,
        cusp_star_lord: cuspStarL,
        csl_planet: csl,
        csl_star_lord: cslStarL,
        star_lord: cslStarL,
        sub_lord: subL,
        signified_houses: sigHouses,
        signification_details: detailsSig,
        primary_signification_en: primEn,
        primary_signification_ta: primTa,
        anatomical_rulership_en: anatEn,
        anatomical_rulership_ta: anatTa,
        recovery_status: recStatus,
        disease_status: disStatus,
        chronic_status: chrStatus,
        hospitalization_status: hospStatus,
        recovery_signified: rec,
        disease_signified: dis,
        chronic_signified: chrAff,
        hospitalization_signified: hosp,
        recovery_houses: recHouses,
        disease_houses: disHouses,
        chronic_houses: chrHouses,
        hospitalization_houses: hospHouses,
        is_data_available: true,
        missing_data_reason: null,
        calculation_provenance: "KP Placidus Cusps & 4-tier Grah Nirdeshan (KP Reader IV reference framework)",
      };
    }

    const sixthCsl = buildKpCsl(6);
    const lagnaCsl = cuspMap[1] ? buildKpCsl(1) : null;
    const eighthCsl = cuspMap[8] ? buildKpCsl(8) : null;
    const twelfthCsl = cuspMap[12] ? buildKpCsl(12) : null;

    const kpRulesList: MedicalRule[] = [];
    const recInd: string[] = [];
    const suscInd: string[] = [];

    if (sixthCsl.disease_signified) {
      suscInd.push(`6th CSL ${sixthCsl.csl_planet} signifies House 6 (acute roga)`);
      kpRulesList.push({
        id: "kp_rule_6csl_signifies_6",
        name: "KP Rule: 6th Cusp Sub-Lord Signifies House 6 (Acute Illness Indication)",
        name_tamil: "கே.பி. விதி: 6-ம் உப அதிபதி 6-ம் பாவத்தைக் குறித்தல் (நோய் நிலை)",
        source: "KP Reader IV: Medical Astrology",
        chapter_verse: "Section 'Disease and CSL'",
        category: "KP 6th Cusp Sub-Lord",
        system: "kp",
        required_placements: "Sub-Lord of 6th cusp signifies House 6",
        mandatory_conditions: ["6th CSL signifies house 6"],
        traditional_interpretation: "In KP Krishnamurti Paddhati, when the 6th CSL signifies house 6, the body experiences acute physical symptoms or conditions requiring medical attention during periods connected to this planet.",
        interpretation_tamil: "கே.பி. ஜோதிடத்தில் 6-ம் பாவத்தின் உப அதிபதி 6-ம் வீட்டைத் தொடர்பு கொண்டால், அவரது தசா புத்தி காலங்களில் சிகிச்சை தேவைப்படும் உடல் உபாதைகள் ஏற்பட பாரம்பரிய விதி கூறுகிறது.",
        anatomical_system: sixthCsl.anatomical_rulership_en,
        is_active: true,
        status: "Qualifying",
        triggered_positions: [`6th CSL ${sixthCsl.csl_planet} signifies House 6`],
        planets_involved: [sixthCsl.csl_planet],
        relevant_houses: [6],
        conditions: [{ condition: "6th CSL signifies House 6", passed: true, detail: `${sixthCsl.csl_planet} signifies houses ${sixthCsl.signified_houses.join(", ")}.` }],
      });
    }

    if (sixthCsl.chronic_signified) {
      suscInd.push(`6th CSL ${sixthCsl.csl_planet} signifies House 8 (chronic/surgical attention)`);
      kpRulesList.push({
        id: "kp_rule_6csl_signifies_8",
        name: "KP Rule: 6th Cusp Sub-Lord Signifies House 8 (Chronic Distress & Surgical Factor)",
        name_tamil: "கே.பி. விதி: 6-ம் உப அதிபதி 8-ம் பாவத்தைக் குறித்தல் (நீண்டகால உபாதை / அறுவை சிகிச்சை)",
        source: "KP Reader IV: Medical Astrology",
        chapter_verse: "Section 'Accidents and Surgery'",
        category: "KP 6th Cusp Sub-Lord",
        system: "kp",
        required_placements: "Sub-Lord of 6th cusp signifies House 8",
        mandatory_conditions: ["6th CSL signifies house 8"],
        traditional_interpretation: "According to KP principles, when the 6th CSL is connected to the 8th house, physical challenges tend to be intense or prolonged. If Mars is also involved, surgical intervention or invasive diagnostics are classically indicated.",
        interpretation_tamil: "6-ம் உப அதிபதி 8-ம் பாவத்தைக் குறிக்கும் போது, வலிகள், நீண்டகால உடல் சிரமங்கள் அல்லது அறுவை சிகிச்சைக்கான சாத்தியங்கள் கே.பி. முறையில் குறிப்பிடப்படுகின்றன.",
        anatomical_system: sixthCsl.anatomical_rulership_en,
        is_active: true,
        status: "Qualifying",
        triggered_positions: [`6th CSL ${sixthCsl.csl_planet} signifies House 8`],
        planets_involved: [sixthCsl.csl_planet],
        relevant_houses: [8],
        conditions: [{ condition: "6th CSL signifies House 8", passed: true, detail: `${sixthCsl.csl_planet} signifies houses ${sixthCsl.signified_houses.join(", ")}.` }],
      });
    }

    if (sixthCsl.hospitalization_signified) {
      suscInd.push(`6th CSL ${sixthCsl.csl_planet} signifies House 12 (bed rest/hospitalization)`);
      kpRulesList.push({
        id: "kp_rule_6csl_signifies_12",
        name: "KP Rule: 6th Cusp Sub-Lord Signifies House 12 (Hospitalization & Bed Rest)",
        name_tamil: "கே.பி. விதி: 6-ம் உப அதிபதி 12-ம் பாவத்தைக் குறித்தல் (மருத்துவமனை அனுமதி மற்றும் ஓய்வு)",
        source: "KP Reader IV: Medical Astrology",
        chapter_verse: "Section 'Hospitalization'",
        category: "KP 6th Cusp Sub-Lord",
        system: "kp",
        required_placements: "Sub-Lord of 6th cusp signifies House 12",
        mandatory_conditions: ["6th CSL signifies house 12"],
        traditional_interpretation: "KP astrology holds that the 12th house signifies confinement, clinics, hospital admission, and expenditures on cure. When 6th CSL signifies 12, physical ailments traditionally lead to institutional care.",
        interpretation_tamil: "கே.பி. விதிகளின்படி 6-ம் உப அதிபதி 12-ம் வீட்டைத் தொடர்பு கொண்டால், மருத்துவமனை அனுமதி, சிகிச்சைக்கான செலவுகள் அல்லது படுக்கை ஓய்வு தேவைப்படும் நிலைகளை பாரம்பரிய சாஸ்திரம் குறிப்பிடுகிறது.",
        anatomical_system: sixthCsl.anatomical_rulership_en,
        is_active: true,
        status: "Qualifying",
        triggered_positions: [`6th CSL ${sixthCsl.csl_planet} signifies House 12`],
        planets_involved: [sixthCsl.csl_planet],
        relevant_houses: [12],
        conditions: [{ condition: "6th CSL signifies House 12", passed: true, detail: `${sixthCsl.csl_planet} signifies houses ${sixthCsl.signified_houses.join(", ")}.` }],
      });
    }

    if (sixthCsl.recovery_signified) {
      const recH = [1, 5, 11].filter((x) => sixthCsl.signified_houses.includes(x));
      recInd.push(`6th CSL ${sixthCsl.csl_planet} signifies recovery houses ${recH.join(", ")}`);
      kpRulesList.push({
        id: "kp_rule_recovery_1_5_11",
        name: "KP Rule: 6th CSL Signifies 1, 5, or 11 (Cure, Recovery & Disease Negation)",
        name_tamil: "கே.பி. விதி: 6-ம் உப அதிபதி 1, 5, 11-ஐக் குறித்தல் (குணமடைதல் மற்றும் நோய் முறிவு)",
        source: "KP Reader IV: Medical Astrology",
        chapter_verse: "Section 'Cure of Disease'",
        category: "KP 6th Cusp Sub-Lord",
        system: "kp",
        required_placements: "6th CSL signifies houses 1, 5, or 11",
        mandatory_conditions: ["6th CSL signifies 1, 5, or 11"],
        traditional_interpretation: "In KP doctrine: House 5 is the 12th from 6th (negation/loss of disease); House 11 is the 12th from 12th (negation of hospitalization); House 1 is bodily vitality. When 6th CSL signifies 1, 5, or 11, the native experiences complete recovery and therapeutic success.",
        interpretation_tamil: "கே.பி. தத்துவப்படி: 5-ம் வீடு என்பது 6-க்கு 12-ம் வீடாகி நோயை அழிக்கும்; 11-ம் வீடு மருத்துவமனை வாசம் நீங்கி பூரண குணம் பெறுவதைக் குறிக்கும்; 1-ம் வீடு உடற்பலத்தைக் குறிக்கும்.",
        anatomical_system: "Cellular Restoration & Cure",
        is_active: true,
        status: "Qualifying",
        triggered_positions: [`6th CSL signifies houses ${recH.join(", ")}`],
        planets_involved: [sixthCsl.csl_planet],
        relevant_houses: recH,
        conditions: [{ condition: "6th CSL signifies recovery houses", passed: true, detail: `${sixthCsl.csl_planet} signifies ${recH.join(", ")}.` }],
      });
    }

    // Active Dasa Significations in KP
    const dasaSigs: KpDasaSignification[] = [];
    if (mahaLord && mahaLord !== "Unknown") {
      const sigs = sigMap[mahaLord] || [];
      dasaSigs.push({
        period_level: "Mahadasha",
        lord: mahaLord,
        signified_houses: sigs,
        indication_en: `Period lord ${mahaLord} signifies houses ${sigs.join(", ")}.`,
        indication_ta: `தசா நாதர் ${mahaLord} பாவங்கள் ${sigs.join(", ")}-ஐக் குறிக்கிறார்.`,
      });
      if (sigs.some((x) => [6, 8, 12].includes(x))) {
        suscInd.push(`Active Mahadasha lord ${mahaLord} signifies houses ${sigs.filter((x) => [6, 8, 12].includes(x)).join(", ")}`);
      }
      if (sigs.some((x) => [1, 5, 11].includes(x))) {
        recInd.push(`Active Mahadasha lord ${mahaLord} signifies recovery houses ${sigs.filter((x) => [1, 5, 11].includes(x)).join(", ")}`);
      }
    }
    if (bhuktiLord) {
      const sigs = sigMap[bhuktiLord] || [];
      dasaSigs.push({
        period_level: "Bhukti",
        lord: bhuktiLord,
        signified_houses: sigs,
        indication_en: `Bhukti lord ${bhuktiLord} signifies houses ${sigs.join(", ")}.`,
        indication_ta: `புத்தி நாதர் ${bhuktiLord} பாவங்கள் ${sigs.join(", ")}-ஐக் குறிக்கிறார்.`,
      });
    }

    kpAnalysis = {
      sixth_csl: sixthCsl,
      lagna_csl: lagnaCsl,
      eighth_csl: eighthCsl,
      twelfth_csl: twelfthCsl,
      current_dasa_significations: dasaSigs,
      kp_rules: kpRulesList,
      recovery_indicators: recInd,
      susceptibility_indicators: suscInd,
    };
  }

  return {
    metadata: horoscope.metadata,
    rule_set_version: RULE_SET_VERSION,
    disclaimer_en: SAFETY_DISCLAIMER_EN,
    disclaimer_ta: SAFETY_DISCLAIMER_TA,
    vedic_analysis: {
      birth_chart: birthChartPerspective,
      current_period: currentPeriodPerspective,
      historical_periods: historicalPeriodPerspective,
    },
    kp_analysis: kpAnalysis,
  };
}
