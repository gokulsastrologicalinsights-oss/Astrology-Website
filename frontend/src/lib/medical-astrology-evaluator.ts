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
  NakshatraMedicalDetail,
  GestationalMonthDetail,
  ProgenyShapaDetail,
  ClinicalCaseStudy,
  TatwaNavadwaraDetail,
  DrKrishnaKumarCompendium,
  DrChatterjeeCompendium,
  SaptaDhatuDetail,
  EndocrineGlandDetail,
  TridoshaSiteDetail,
  DeathPointCalculation,
  DiabetesMellitusAssessment,
  ModernComplexDiseaseDetail,
  NaturalRemediesGuide,
  HeindelSignAnatomy,
  HeindelPlanetPhysiology,
  HeindelViciousCircle,
  HeindelNailDiagnosis,
  HeindelPlanetaryAntidote,
  HeindelAphorism,
  HeindelNebularSpot,
  MaxHeindelCompendium,
  JaneDecumbitureEvaluation,
  JaneArabianParts,
  JaneElementalAnalysis,
  JaneCellSaltCorrespondence,
  JaneBachFlowerCorrespondence,
  JaneAcupunctureMeridian,
  JaneRidderPatrickCompendium,
  DaathSignAnatomy,
  DaathPlanetAction,
  DaathAntipathicTherapy,
  DaathPlanetaryPeriod,
  DaathDecumbitureCriticalDays,
  DaathStrengthEvaluation,
  HeinrichDaathCompendium,
} from "./types.ts";
import {
  DAATH_METADATA_RAW,
  DAATH_SIGNS_RAW,
  DAATH_PLANETS_RAW,
  DAATH_TEMPERAMENTS_AND_CROSSES_RAW,
  DAATH_ANTIPATHIC_RAW,
  DAATH_PLANETARY_PERIODS_RAW,
  DAATH_DECUMBITURE_RAW,
  DAATH_RULES_RAW,
} from "./daath-data.ts";

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


export const DR_KRISHNA_KUMAR_METADATA = {
  "book_title": "A Book on Medical Astrology: Horoscope or Stethoscope (Diagnosis of Diseases, Problems in Progeny, Their Remedies)",
  "book_title_ta": "மருத்துவ ஜோதிடம்: ஜாதகமா அல்லது ஸ்டெதாஸ்கோப்பா (நோய் கண்டறிதல், சந்தான தோஷங்கள் மற்றும் பரிகாரங்கள்)",
  "author": "Dr. S. Krishna Kumar, Chairman Bangalore Chapter of Indian Council of Astrological Sciences (Regd.) Chennai",
  "publisher": "Bhartiya Prachya Evam Sanatan Vigyan Sansthan, Delhi (4649/21 Darya Ganj New Delhi-110002)",
  "submission": "Submitted to Open International University, Sri Lanka",
  "salient_features": [
    "Astrological Diagnosis vs. Medical Stethoscope: Pre-symptomatic detection via Karmic / Vidhi chart and Dasha periods years in advance.",
    "Prarabdha & Sanchita Karma Theory: Law of karma manifesting as physical constitution and diseases.",
    "Macrocosm & Microcosm (Pindanda & Brahmanda): Pancha Bhootas (5 Tatwas), Tanmatras, and Abhimani Devatas of organs.",
    "Navadwaras & Navagrahas: The nine body openings governed by planetary forces.",
    "Tridosha Ayurvedic Classification: Planetary constitution balancing Vata, Pitta, and Kapha.",
    "27 Nakshatras & Medical Anatomy: Governed body parts, Nakshatra Devatas, and specific disease susceptibilities for natives born in each star.",
    "Manasika & Buddhi Yogas: 11 classical combinations for intellect, memory retention, dullness, insanity (Unmada), and wavering mind.",
    "Organ-Specific & Systemic Yogas: Comprehensive diagnosis for head, eyes, ears, mouth, throat, boils, urinary tract, heart, kidneys, and leprosy.",
    "Progeny Problems & 9 Curses (Shapa): Detailed causes and precise Vedic propitiations for Sarpa, Pitru, Bhratru, Matru, Matula, Brahma, Patni, and Preta Shapa.",
    "Female Horoscopy & 10 Gestational Months: Month-by-month fetal development governed by Grahas (Kalala, Ghana, Ankura, Asthi, Charma, Angaja, Chethanatha, Adhana, Udvega, Prasava).",
    "Caesarean vs. Normal Delivery: Predictive indicators based on Mars, Moon, and Jupiter aspects.",
    "12 Classical Clinical Case Histories: Real consulting horoscopes illustrating brain tumour, blood cancer, breast cancer, vitiligo, and blindness via Dagdha Rashis."
  ]
};

export const NAKSHATRA_27_MEDICAL_MATRIX: Record<number, NakshatraMedicalDetail> = {
  "1": {
    "number": 1,
    "name": "Ashwini",
    "name_ta": "அஸ்வினி",
    "body_part_en": "Upper feet and toes",
    "body_part_ta": "மேல் பாதம் மற்றும் கால் விரல்கள்",
    "devata": "Ashwini Kumaras (Celestial Physicians)",
    "disease_tendency_en": "Periodical fever, sudden body temperature spikes, malaria-like fevers",
    "disease_tendency_ta": "விட்டு விட்டு வரும் காய்ச்சல், திடீர் உடல் உஷ்ண மாறுபாடுகள்",
    "propitiation_en": "Propitiation of Ashwini Devatas with herbal ghee and charity of horse gram.",
    "propitiation_ta": "அஸ்வினி குமாரர்கள் ஆராதனை, மூலிகைத் தைல வழிபாடு மற்றும் கொள்ளு தானம்."
  },
  "2": {
    "number": 2,
    "name": "Bharani",
    "name_ta": "பரணி",
    "body_part_en": "Lower feet and soles",
    "body_part_ta": "கீழ் பாதம் மற்றும் பாத அடிப் பகுதி",
    "devata": "Yama (Lord of Dharma & Mortality)",
    "disease_tendency_en": "Dysentery, acute loose bowels, lower bowel inflammation",
    "disease_tendency_ta": "வயிற்றுப்போக்கு, சீதபேதி, அடிக்குடல் அழற்சி",
    "propitiation_en": "Yama Devata pooja, Tila Homa (sesame fire ritual), and serving cool water to travelers.",
    "propitiation_ta": "யம தர்மராஜன் வழிபாடு, எள் ஹோமம் மற்றும் தாகசாந்தி தானம்."
  },
  "3": {
    "number": 3,
    "name": "Krittika",
    "name_ta": "கிருத்திகை",
    "body_part_en": "Head and cerebral crown",
    "body_part_ta": "தலை மற்றும் உச்சிப் பகுதி",
    "devata": "Agni (God of Fire)",
    "disease_tendency_en": "Intestinal disorders with alternating constipation and diarrhoea, gastric heat",
    "disease_tendency_ta": "மாறி மாறி வரும் மலச்சிக்கல் & வயிற்றுப்போக்கு, குடல் உஷ்ணம்",
    "propitiation_en": "Agni pooja with pure cow ghee oblations, feeding fasting devotees.",
    "propitiation_ta": "பசு நெய் கொண்டு அக்னி வழிபாடு மற்றும் அன்னதானம்."
  },
  "4": {
    "number": 4,
    "name": "Rohini",
    "name_ta": "ரோகிணி",
    "body_part_en": "Forehead and cranial frontal bone",
    "body_part_ta": "நெற்றி மற்றும் முன்தலை எலும்பு",
    "devata": "Brahma / Prajapati (Creator)",
    "disease_tendency_en": "Piles, haemorrhoids, and ano-rectal inflammatory disorders",
    "disease_tendency_ta": "மூல நோய், பௌத்திரம் மற்றும் ஆசனவாய் கோளாறுகள்",
    "propitiation_en": "Surya & Brahma worship, consuming coolant foods, and charity of white rice.",
    "propitiation_ta": "பிரம்மா மற்றும் சூரியன் வழிபாடு, குளிர்ச்சி உணவுகள் உட்கொள்ளுதல், பச்சரிசி தானம்."
  },
  "5": {
    "number": 5,
    "name": "Mrigashira",
    "name_ta": "மிருகசீரிஷம்",
    "body_part_en": "Eyebrows and ocular ridge",
    "body_part_ta": "புருவங்கள் மற்றும் கண் புருவ எலும்பு",
    "devata": "Moon / Soma (Nectar of Immortality)",
    "disease_tendency_en": "Chronic indigestion, sluggish digestive metabolism, bilious nausea",
    "disease_tendency_ta": "அஜீரணம், செரிமான மந்தம், பித்த குமட்டல்",
    "propitiation_en": "Chandra pooja on Mondays, offering raw milk to Shiva, consuming digestive herbs.",
    "propitiation_ta": "திங்கட்கிழமை சந்திர வழிபாடு, சிவபெருமானுக்கு பால் அபிஷேகம், சீரக நீர் அருந்துதல்."
  },
  "6": {
    "number": 6,
    "name": "Ardra",
    "name_ta": "திருவாதிரை",
    "body_part_en": "Eyes and optic pathways",
    "body_part_ta": "கண்கள் மற்றும் பார்வை நரம்புகள்",
    "devata": "Rudra (Lord of Destructive Transformation)",
    "disease_tendency_en": "Mandagni (weak gastric fire), chronic low appetite, metabolic deficiency",
    "disease_tendency_ta": "மந்தாக்னி (பசியின்மை / பலவீனமான செரிமான நெருப்பு)",
    "propitiation_en": "Rudrabhisheka with bilva leaves and recitation of Sri Rudram.",
    "propitiation_ta": "வில்வ இலைகளால் ருத்ராபிஷேகம் மற்றும் ஸ்ரீ ருத்ர பாராயணம்."
  },
  "7": {
    "number": 7,
    "name": "Punarvasu",
    "name_ta": "புனர்பூசம்",
    "body_part_en": "Nose and nasal cavities",
    "body_part_ta": "மூக்கு மற்றும் நாசித் துவாரங்கள்",
    "devata": "Aditi (Universal Cosmic Mother)",
    "disease_tendency_en": "Cholera, acute water-borne gastrointestinal infections, dehydration",
    "disease_tendency_ta": "வாந்திபேதி, நீர் தொற்று மற்றும் தீவிர நீரிழப்பு",
    "propitiation_en": "Aditi Devi worship, donating pure drinking water facilities to the public.",
    "propitiation_ta": "அதிதி தேவி வழிபாடு, பொதுமக்களுக்கு குடிநீர் வசதி ஏற்படுத்தித் தருதல்."
  },
  "8": {
    "number": 8,
    "name": "Pushya",
    "name_ta": "பூசம்",
    "body_part_en": "Face and oral structure",
    "body_part_ta": "முகம் மற்றும் வாய் அமைப்பு",
    "devata": "Brihaspati (Preceptor of Gods)",
    "disease_tendency_en": "Tastelessness (Anorexia / Aruchi), loss of palate sensation, mouth dryness",
    "disease_tendency_ta": "சுவையின்மை (அரோசகம்), நாக்கு சுவை இழப்பு, வாய் உலர்வு",
    "propitiation_en": "Brihaspati Shanti, Guru stotra recitation, donating yellow chickpeas and saffron.",
    "propitiation_ta": "பிரகஸ்பதி சாந்தி, குரு தியானம், கொண்டைக்கடலை மற்றும் குங்குமப்பூ தானம்."
  },
  "9": {
    "number": 9,
    "name": "Ashlesha",
    "name_ta": "ஆயில்யம்",
    "body_part_en": "Ears and auditory channels",
    "body_part_ta": "காதுகள் மற்றும் செவிப்பாதை",
    "devata": "Sarpa (Serpent Deity)",
    "disease_tendency_en": "Anemia (Pandu Roga), blood weakness, pale complexion, lack of stamina",
    "disease_tendency_ta": "ரத்த சோகை (பாண்டு நோய்), ரத்த அணுக்கள் குறைபாடு, உடல் சோர்வு",
    "propitiation_en": "Sarpa pooja, offering milk to Naga deities, consuming iron-rich satwik diet.",
    "propitiation_ta": "நாகர் வழிபாடு, புற்றுக்குப் பால் வார்த்தல் மற்றும் ஊட்டச்சத்து பராமரிப்பு."
  },
  "10": {
    "number": 10,
    "name": "Magha",
    "name_ta": "மகம்",
    "body_part_en": "Chin and mandibular jaw",
    "body_part_ta": "தாடை மற்றும் கீழ்த்தாடை எலும்பு",
    "devata": "Pitrus (Ancestral Forefathers)",
    "disease_tendency_en": "Breathing problems, asthma, chronic respiratory congestion",
    "disease_tendency_ta": "மூச்சுத்திணறல், ஆஸ்துமா மற்றும் நாள்பட்ட சுவாசக் கோளாறுகள்",
    "propitiation_en": "Pitru Tarpanam, Amavasya oblations, and serving food to elderly seekers.",
    "propitiation_ta": "பித்ரு தர்ப்பணம், அமாவாசை திதி வழிபாடு மற்றும் முதியோருக்கு அன்னதானம்."
  },
  "11": {
    "number": 11,
    "name": "Purva Phalguni",
    "name_ta": "பூரம்",
    "body_part_en": "Right hand and arm",
    "body_part_ta": "வலது கை மற்றும் முழங்கை",
    "devata": "Surya / Bhaga (Solar Deity)",
    "disease_tendency_en": "Chronic cough (both dry and productive bronchitis), bronchial irritation",
    "disease_tendency_ta": "வறட்டு இருமல் அல்லது சளி இருமல், மூச்சுக்குழாய் அழற்சி",
    "propitiation_en": "Surya Namaskara at dawn, Aditya Hridaya recitation, drinking warm tulsi decoctions.",
    "propitiation_ta": "சூரிய நமஸ்காரம், ஆதித்ய ஹிருதய பாராயணம் மற்றும் துளசி தீர்த்தம்."
  },
  "12": {
    "number": 12,
    "name": "Uttara Phalguni",
    "name_ta": "உத்திரம்",
    "body_part_en": "Left hand and arm",
    "body_part_ta": "இடது கை மற்றும் முழங்கை",
    "devata": "Aryama (Deity of Honorable Treaties)",
    "disease_tendency_en": "Leprosy (Kushta), persistent dermatological eruptions, fungal skin lesions",
    "disease_tendency_ta": "குஷ்டம், நாள்பட்ட தோல் நோய்கள், படர்தாமரை",
    "propitiation_en": "Aryama worship, supporting orphanages, applying sandalwood and neem preparations.",
    "propitiation_ta": "அரியமான் வழிபாடு, ஆதரவற்றோருக்கு உதவுதல், சந்தன-வேப்பிலை பயன்பாடு."
  },
  "13": {
    "number": 13,
    "name": "Hasta",
    "name_ta": "அஸ்தம்",
    "body_part_en": "Fingers and manual dexterity joints",
    "body_part_ta": "கை விரல்கள் மற்றும் கை மூட்டுகள்",
    "devata": "Savitru (Creative Solar Luminary)",
    "disease_tendency_en": "Diabetes mellitus of various types (Prameha), pancreatic weakness",
    "disease_tendency_ta": "பல்வேறு வகையான நீரிழிவு (பிரமேகம்), கணைய பலவீனம்",
    "propitiation_en": "Gayatri Japa at sunrise, donating green grams, avoiding excessive sweets.",
    "propitiation_ta": "காலை காயத்ரி ஜபம், பாசிப்பயறு தானம், சர்க்கரை உணவுகளை மட்டுப்படுத்துதல்."
  },
  "14": {
    "number": 14,
    "name": "Chitra",
    "name_ta": "சித்திரை",
    "body_part_en": "Neck and cervical vertebrae",
    "body_part_ta": "கழுத்து மற்றும் பிடரிப் பகுதி",
    "devata": "Tvashtru (Celestial Architect Vishwakarma)",
    "disease_tendency_en": "Giddiness, vertigo, cervical balance disorders, partial loss of consciousness",
    "disease_tendency_ta": "தலைச்சுற்றல், மயக்கம், கழுத்து நரம்பு அழுத்தம்",
    "propitiation_en": "Tvashtru Vishwakarma worship, donating tools or support to artisans.",
    "propitiation_ta": "துவஷ்டா வழிபாடு, கைவினைஞர்களுக்கு உதவுதல், கழுத்துக்கான எளிய யோகாசனம்."
  },
  "15": {
    "number": 15,
    "name": "Swati",
    "name_ta": "சுவாதி",
    "body_part_en": "Chest and upper thoracic cavity",
    "body_part_ta": "மார்பு மற்றும் மேல் நெஞ்சுப் பகுதி",
    "devata": "Vayu (Wind Deity / Prana Lord)",
    "disease_tendency_en": "Eye diseases, corneal irritation, blurred vision, ocular dryness",
    "disease_tendency_ta": "கண் நோய்கள், கண் வறட்சி, பார்வை மங்குதல்",
    "propitiation_en": "Vayu stotra, lighting pure camphor for Shiva, pranayama practice.",
    "propitiation_ta": "வாயு பகவான் பிரார்த்தனை, கற்பூர தீப வழிபாடு மற்றும் பிராணாயாமப் பயிற்சி."
  },
  "16": {
    "number": 16,
    "name": "Vishakha",
    "name_ta": "விசாகம்",
    "body_part_en": "Lungs and respiratory alveoli",
    "body_part_ta": "நுரையீரல் மற்றும் மூச்சு நுண்குழல்கள்",
    "devata": "Indra & Agni (Dual Rulers of Might and Fire)",
    "disease_tendency_en": "Ear diseases, auditory canal infections, tinnitus, partial hearing loss",
    "disease_tendency_ta": "காது நோய்கள், காது இரைச்சல் (டின்னிடஸ்), செவித்திறன் குறைவு",
    "propitiation_en": "Murugan / Skanda worship, lighting ghee lamps on Tuesdays, ear hygiene.",
    "propitiation_ta": "முருகப்பெருமான் வழிபாடு, செவ்வாய்க்கிழமை நெய் தீபம் ஏற்றுதல்."
  },
  "17": {
    "number": 17,
    "name": "Anuradha",
    "name_ta": "அனுஷம்",
    "body_part_en": "Stomach and epigastric zone",
    "body_part_ta": "வயிறு மற்றும் இரைப்பை மேல் பகுதி",
    "devata": "Mitra (Deity of Friendship & Universal Light)",
    "disease_tendency_en": "Diseases of the nose (Peenasa Roga), chronic catarrh, sinus blockages",
    "disease_tendency_ta": "மூக்கு நோய்கள் (பீனச ரோகம்), நாள்பட்ட சளி, சைனஸ் அடைப்பு",
    "propitiation_en": "Mitra Devata aradhana, nasal steam therapies, donating bell-metal vessels.",
    "propitiation_ta": "மித்ர தேவதை வழிபாடு, மூலிகை ஆவி பிடித்தல் மற்றும் வெண்கல பாத்திரம் தானம்."
  },
  "18": {
    "number": 18,
    "name": "Jyeshtha",
    "name_ta": "கேட்டை",
    "body_part_en": "Right portion of stomach and hepatic margin",
    "body_part_ta": "வயிற்றின் வலது பகுதி மற்றும் கல்லீரல் ஓரம்",
    "devata": "Indra / Moon (King of Devas)",
    "disease_tendency_en": "Diseases of the mouth: teeth decay, tongue sores, lip fissures, gums & throat",
    "disease_tendency_ta": "வாய் நோய்கள்: பல் சொத்தை, நாக்கு புண்கள், உதடு வெடிப்பு, தொண்டை வலி",
    "propitiation_en": "Indra worship, salt-water oral rinses, charity of fresh green vegetables.",
    "propitiation_ta": "இந்திர பகவான் வழிபாடு, மூலிகை வாய் கொப்பளிப்பு, பசும் காய்கறிகள் தானம்."
  },
  "19": {
    "number": 19,
    "name": "Mula",
    "name_ta": "மூலம்",
    "body_part_en": "Left portion of stomach and splenic zone",
    "body_part_ta": "வயிற்றின் இடது பகுதி மற்றும் மண்ணீரல்",
    "devata": "Nirriti / Rakshasa (Goddess of Calamity & Dissolution)",
    "disease_tendency_en": "Tuberculosis of any type (Kshaya Roga), deep chest and lung wasting",
    "disease_tendency_ta": "எவ்வகை காசநோயும் (க்ஷய ரோகம்), நுரையீரல் பலவீனம்",
    "propitiation_en": "Maha Mrityunjaya Japa, donating roots and tubers, worshipping Lord Hanuman.",
    "propitiation_ta": "மகா மிருத்யுஞ்சய ஜபம், கிழங்கு வகைகள் தானம் மற்றும் அனுமன் வழிபாடு."
  },
  "20": {
    "number": 20,
    "name": "Purvashada",
    "name_ta": "பூராடம்",
    "body_part_en": "Back and lumbar vertebral column",
    "body_part_ta": "முதுகு மற்றும் கீழ்முதுகு எலும்புகள்",
    "devata": "Apas / Jala Devata (Primordial Waters)",
    "disease_tendency_en": "Formation of stones in urinary tract (kidney/bladder calculi / Ashmari)",
    "disease_tendency_ta": "சிறுநீரகக் கற்கள் (அஷ்மரீ) மற்றும் சிறுநீர்ப்பை அடைப்புகள்",
    "propitiation_en": "Varuna Pooja, maintaining high fluid intake, donating tender coconuts.",
    "propitiation_ta": "வருண பகவான் பூஜை, அதிக நீர் அருந்துதல், இளநீர் தானம்."
  },
  "21": {
    "number": 21,
    "name": "Uttarashada",
    "name_ta": "உத்திராடம்",
    "body_part_en": "Waist and pelvic girdle",
    "body_part_ta": "இடுப்பு மற்றும் இடுப்பு வளைய எலும்பு",
    "devata": "Vishwadevas (Universal Divine Virtues)",
    "disease_tendency_en": "Vomiting, bilious reflux, gastric emesis, chronic nausea",
    "disease_tendency_ta": "வாந்தி, பித்த வாந்தி, அமில ஏப்பம், செரிமான எதிர்ப்போக்கு",
    "propitiation_en": "Vishwadeva worship, light alkaline diet, charity to temples.",
    "propitiation_ta": "விஸ்வே தேவர்கள் ஆராதனை, எளிமையான காரசாரமற்ற உணவு மற்றும் ஆலய வழிபாடு."
  },
  "22": {
    "number": 22,
    "name": "Shravana",
    "name_ta": "திருவோணம்",
    "body_part_en": "Upper genital region and groins",
    "body_part_ta": "மேல் பிறப்புறுப்பு மற்றும் தொடை இடுக்கு",
    "devata": "Lord Vishnu (Preserver of Cosmos)",
    "disease_tendency_en": "Tastelessness disease, neurological loss of oral sensation, digestive apathy",
    "disease_tendency_ta": "சுவை நரம்பு பலவீனம், நாக்கு மரத்துப்போதல், உணவு விருப்பமின்மை",
    "propitiation_en": "Vishnu Sahasranama recitation on Dwadashi, donating Tulasi plants and curd rice.",
    "propitiation_ta": "துவாதசி திதியில் விஷ்ணு சகஸ்ரநாமம், துளசி மாலை சாற்றுதல், தயிர்சாத தானம்."
  },
  "23": {
    "number": 23,
    "name": "Dhanishta",
    "name_ta": "அவிட்டம்",
    "body_part_en": "Generative organs and perineum",
    "body_part_ta": "பிறப்புறுப்பு மற்றும் கீழ் இடுப்பு பகுதி",
    "devata": "Ashta Vasus (Eight Cosmic Elements)",
    "disease_tendency_en": "Pains caused by Vata disorder, sprains, sciatica, severe rheumatism",
    "disease_tendency_ta": "வாத வலிகள், சுளுக்கு, மூட்டு வாதம், தசைப்பிடிப்பு",
    "propitiation_en": "Ashta Vasu worship, application of medicinal sesame oil, keeping warm.",
    "propitiation_ta": "அஷ்ட வசுக்கள் வழிபாடு, நல்லெண்ணெய் மசாஜ் மற்றும் வெந்நீர் குளியல்."
  },
  "24": {
    "number": 24,
    "name": "Shatabhisha",
    "name_ta": "சதயம்",
    "body_part_en": "Right thigh and femoral muscles",
    "body_part_ta": "வலது தொடை மற்றும் தொடை தசைகள்",
    "devata": "Varuna (Cosmic Ocean & Mystic Healer)",
    "disease_tendency_en": "Bilious diseases, liver heat, gallbladder inflammation, yellow bile excess",
    "disease_tendency_ta": "பித்த நோய்கள், கல்லீரல் உஷ்ணம், பித்தப்பை அழற்சி",
    "propitiation_en": "Varuna homa, bathing in holy rivers, consuming cooling herbal bitters.",
    "propitiation_ta": "வருண ஹோமம், புண்ணிய தீர்த்த ஸ்நானம், வேப்பிலை கஷாயம் போன்ற பித்த நிவாரணிகள்."
  },
  "25": {
    "number": 25,
    "name": "Purva Bhadrapada",
    "name_ta": "பூரட்டாதி",
    "body_part_en": "Left thigh and femoral muscles",
    "body_part_ta": "இடது தொடை மற்றும் தொடை தசைகள்",
    "devata": "Aja Ekapada / Jala (One-Footed Cosmic Serpent)",
    "disease_tendency_en": "Phlegmatic diseases (Kapha excess), severe mucus accumulation, bronchial edema",
    "disease_tendency_ta": "கப நோய்கள் (சளி மிகுதி), நுரையீரல் கோழை அடைப்பு",
    "propitiation_en": "Rudra Japa, dry herbal fomentation, consuming trikatu (dry ginger, pepper, pippali).",
    "propitiation_ta": "ருத்ர ஜபம், திரிகடுக சூரணம் உட்கொள்ளுதல், உலர் ஒத்தடம் கொடுத்தல்."
  },
  "26": {
    "number": 26,
    "name": "Uttara Bhadrapada",
    "name_ta": "உத்திரட்டாதி",
    "body_part_en": "Ankles and Achilles tendon",
    "body_part_ta": "கணுக்கால் மற்றும் குதிகால் நரம்பு",
    "devata": "Ahirbudhnya / Brahma (Serpent of the Depths)",
    "disease_tendency_en": "Diseases developed from chronic fatigue, physical exhaustion, adrenal burnout",
    "disease_tendency_ta": "அதிசோர்வு, உடல் தளர்ச்சி, நரம்பு பலவீனம் மற்றும் தளர்வு நோய்கள்",
    "propitiation_en": "Brahma aradhana, disciplined sleep schedules, nourishing rasayana tonics.",
    "propitiation_ta": "பிரம்மா ஆராதனை, முறையான ஆழ்ந்த உறக்கம், ரசாயன சத்தான உணவுகள்."
  },
  "27": {
    "number": 27,
    "name": "Revati",
    "name_ta": "ரேவதி",
    "body_part_en": "Feet and pedal digits",
    "body_part_ta": "பாதங்கள் மற்றும் கால் பெருவிரல்கள்",
    "devata": "Pushan (Solar Nourisher & Guide)",
    "disease_tendency_en": "Diseases developed from boils, carbuncles, unhealed ulcerations, and wounds",
    "disease_tendency_ta": "புண்கள், கொப்புளங்கள், ஆறாத காயங்கள் மற்றும் ரத்தக் கட்டிகள்",
    "propitiation_en": "Pushan worship, feeding cows green grass, topical antiseptic herbal care.",
    "propitiation_ta": "பூஷா வழிபாடு, பசுக்களுக்கு அகத்திக்கீரை வழங்குதல், மூலிகைப் புண் பராமரிப்பு."
  }
};

export const PREGNANCY_GESTATIONAL_MONTHS: GestationalMonthDetail[] = [
  {
    "month": 1,
    "ruling_planet": "Venus",
    "sanskrit_term": "Kalala (கலலம்)",
    "stage_en": "Fleshy Zygote / Seminal-Ovular Fluid Union",
    "stage_ta": "விந்து-சுக்கில சேர்க்கை / கருக்கோளம்",
    "description_en": "In the 1st month, the fluid union of male semen (Shukla) and female ovum (Shonitha) forms a viscous fleshy mass called Kalala, ruled by Venus. Affliction in this month risks early zygotic dissolution.",
    "description_ta": "முதல் மாதத்தில் சுக்ல-சோணித இணைப்பால் 'கலலம்' எனும் திரவக் கரு உருவாகிறது; இதற்கு சுக்கிரன் அதிபதி."
  },
  {
    "month": 2,
    "ruling_planet": "Mars",
    "sanskrit_term": "Ghana (கனம்)",
    "stage_en": "Solidification into Kidney-Bean Mass",
    "stage_ta": "கரு திரட்சியடைந்து கெட்டிப்படுதல்",
    "description_en": "In the 2nd month, the mass undergoes solidification (Ghana) into an embryonic vesicle shaped like a kidney bean, ruled by Mars. Excessive heat or Mars affliction causes cramping.",
    "description_ta": "இரண்டாம் மாதத்தில் கரு கெட்டிப்பட்டு (கனம்) சிறுநீரக விதை வடிவம் பெறுகிறது; இதற்கு செவ்வாய் அதிபதி."
  },
  {
    "month": 3,
    "ruling_planet": "Jupiter",
    "sanskrit_term": "Ankura (அங்குரம்)",
    "stage_en": "Sprouting of Limbs, Buds, and Organ Primordia",
    "stage_ta": "உறுப்புகளின் முளைப்பு மற்றும் கிளைத்தல்",
    "description_en": "In the 3rd month, the sprouts (Ankura) of the arms, legs, and internal organ primordia show themselves, governed by Jupiter (Karaka for expansion and growth).",
    "description_ta": "மூன்றாம் மாதத்தில் கை, கால்கள் மற்றும் உள்ளுறுப்புகளின் அரும்புகள் முளைக்கின்றன (அங்குரம்); குரு பகவான் இதற்கு அதிபதி."
  },
  {
    "month": 4,
    "ruling_planet": "Sun",
    "sanskrit_term": "Asthi (அஸ்தி)",
    "stage_en": "Bone Formation & Skeletal Matrix",
    "stage_ta": "எலும்பு உருவாக்கம் மற்றும் மண்டை ஓடு உறுதிபெறுதல்",
    "description_en": "In the 4th month, skeletal ossification takes place; bones, vertebrae, and cranial structures harden, governed by the Sun (Karaka for Asthi/Bones). If Sun is debilitated/afflicted, developmental arrest occurs.",
    "description_ta": "நான்காம் மாதத்தில் எலும்புகள், தண்டுவடம் உறுதியாகின்றன (அஸ்தி); சூரிய பகவான் இதன் அதிபதி."
  },
  {
    "month": 5,
    "ruling_planet": "Moon",
    "sanskrit_term": "Charma (சர்மம்)",
    "stage_en": "Skin Layers, Epidermis & Bodily Fluids",
    "stage_ta": "தோல் அடுக்குகள் மற்றும் திரவப் படலம் உருவாக்கம்",
    "description_en": "In the 5th month, the skin (Charma) develops over the muscular structure, and subcutaneous bodily fluids are regulated by the Moon.",
    "description_ta": "ஐந்தாம் மாதத்தில் தோல், தோல் நிறமிகள் மற்றும் நீர்ச்சத்து உருவாகிறது; சந்திரன் இதன் அதிபதி."
  },
  {
    "month": 6,
    "ruling_planet": "Saturn",
    "sanskrit_term": "Angaja (அங்கஜம்)",
    "stage_en": "Nails, Hair, Body Bristles & Sensory Openings",
    "stage_ta": "முடி, நகங்கள், உடல் ரோமங்கள் மற்றும் அங்கங்கள்",
    "description_en": "In the 6th month, hairs, fingernails, and delicate peripheral structures (Angaja) take form, governed by Saturn (controller of structural maturation).",
    "description_ta": "ஆறாம் மாதத்தில் தலைமுடி, நகங்கள், ரோமங்கள் வளர்கின்றன; சனி பகவான் இதன் அதிபதி."
  },
  {
    "month": 7,
    "ruling_planet": "Mercury",
    "sanskrit_term": "Chethanathaha (சேதனா)",
    "stage_en": "Sensory Animation, Nervous Impulses & Consciousness",
    "stage_ta": "உயிரோட்ட உணர்வு, நரம்பு இயக்கம் மற்றும் சைதன்யம்",
    "description_en": "In the 7th month, consciousness (Chethanathaha) awakens; the fetal nervous system and sensory coordination become active, ruled by Mercury.",
    "description_ta": "ஏழாம் மாதத்தில் கருவிற்குள் சைதன்யம் (உயிர் உணர்வு) மற்றும் நரம்பியல் இயக்கம் துவங்குகிறது; புதன் இதன் அதிபதி."
  },
  {
    "month": 8,
    "ruling_planet": "Adhana Lagna Lord",
    "sanskrit_term": "Adhana / Ojas (ஆதான லக்னாதிபதி)",
    "stage_en": "Nourishment via Umbilical Cord (High Vulnerability)",
    "stage_ta": "தொப்புள் கொடி வழியே தாயின் சத்து பெறுதல் (மிக முக்கிய மாதம்)",
    "description_en": "In the 8th month, the vital fluid (Ojas) oscillates between mother and child via the umbilical cord, governed by the lord of conception time (Adhana Lagna). Ancients considered this a highly delicate month.",
    "description_ta": "எட்டாம் மாதத்தில் ஓஜஸ் சக்தி தாய்க்கும் சேய்க்கும் மாறி மாறி சுழலும்; ஆதான லக்னாதிபதி ஆளும் இந்நாட்களில் மிகுந்த கவனம் தேவை."
  },
  {
    "month": 9,
    "ruling_planet": "Moon",
    "sanskrit_term": "Udvega (உத்வேகம்)",
    "stage_en": "Maternal Anxiety & Fetal Labour Readiness",
    "stage_ta": "பிரசவ உத்வேகம், பிரசவ வலி தயார்நிலை",
    "description_en": "In the 9th month, maternal labour anxiety (Udvega) and fetal descent begin, governed by the Moon.",
    "description_ta": "ஒன்பதாம் மாதத்தில் குழந்தை வெளிப்பட எத்தனிக்கும் உத்வேகம் உண்டாகிறது; சந்திரன் இதற்கு அதிபதி."
  },
  {
    "month": 10,
    "ruling_planet": "Sun",
    "sanskrit_term": "Prasava (பிரசவம்)",
    "stage_en": "Delivery and Emergence into Sunlight",
    "stage_ta": "சுகப்பிரசவம் மற்றும் வெளி உலகுக்கு வருதல்",
    "description_en": "In the 10th month, birth and delivery (Prasava) take place under the governance of the Sun (bringer of life into daylight).",
    "description_ta": "பத்தாம் மாதத்தில் குழந்தை பிரசவமாகி உலகுக்கு வருகிறது; சூரிய பகவான் இதற்கு அதிபதி."
  }
];

export const PROGENY_CURSES_AND_REMEDIES: ProgenyShapaDetail[] = [
  {
    "id": "sarpa_shapa",
    "shapa_name": "Sarpa Shapa (Curse of Snake / Serpent)",
    "shapa_name_ta": "சர்ப்ப சாபம் (நாக சாபம்)",
    "afflicted_karaka": "Rahu & 5th House / Jupiter",
    "cause_en": "Harm inflicted on serpents or destroying ant-hills in previous or present births.",
    "cause_ta": "முற்பிறவியில் அல்லது இப்பிறவியில் பாம்புகளைத் துன்புறுத்துதல் அல்லது புற்று அழித்தல்.",
    "combinations": [
      "Rahu occupies the 5th house and receives the aspect of Mars, or occupies Aries/Scorpio.",
      "Saturn conjoins the 5th lord in the 5th house aspected by Moon, or conjoined with Moon & Rahu.",
      "Jupiter (Putrakaraka) conjoins Rahu and 5th lord while Lagna lord conjoins Mars.",
      "5th house falls in Aries/Scorpio with Rahu and Mercury."
    ],
    "remedy_en": "Perform Naga Pratishtha (installing a consecrated golden or stone Naga idol), worship Nagaraja with milk, donate a milch cow (Godana), fertile land, sesame seeds (Tila), and gold.",
    "remedy_ta": "சுயகிருஹ்ய சூத்திரப்படி தங்கத்தில் நாக பிரதிஷ்டை செய்து பூஜித்தல், கோதானம், பூமிதானம், எள் மற்றும் பொன் தானம் செய்தல்."
  },
  {
    "id": "pitru_shapa",
    "shapa_name": "Pitru Shapa (Curse of Forefathers / Departed Souls)",
    "shapa_name_ta": "பித்ரு சாபம் (முன்னோர்கள் சாபம்)",
    "afflicted_karaka": "Sun & 9th House / 9th Lord",
    "cause_en": "Neglecting father, ancestors, or failing to perform annual Shraddha ceremonies.",
    "cause_ta": "தந்தையை அவமதித்தல், பித்ரு தர்ப்பணம் மற்றும் வருடாந்திர சிரார்த்தங்களை கைவிடுதல்.",
    "combinations": [
      "Sun is debilitated in 5th house in Saturn's Navamsha and hemmed between malefics.",
      "5th lord Sun is in 5th or 9th with malefics or aspected by malefics.",
      "Jupiter is in Leo while 5th lord conjoins Sun, and malefics occupy 5th and Lagna.",
      "9th lord is in 6, 8, or 12 while Jupiter is in a malefic house.",
      "Sun in 8th, Saturn in 5th, 5th lord with Rahu, and malefics in Lagna."
    ],
    "remedy_en": "Perform Gaya Shraddha at Gaya Kshetra for departed souls; perform Anna-dana (feeding 1,000 or 10,000 Brahmins), or perform Kanya Dana (sponsoring marriage of an underprivileged girl), and donate a cow with calf.",
    "remedy_ta": "கயா க்ஷேத்திரத்தில் கயா சிரார்த்தம் செய்தல், 10,000 பேருக்கு அன்னதானம் அல்லது கன்னிகாதானம் மற்றும் கன்றுடன் கூடிய பசு தானம்."
  },
  {
    "id": "bhratru_shapa",
    "shapa_name": "Bhratru Shapa (Curse of Brothers)",
    "shapa_name_ta": "ப்ராத்ரு சாபம் (சகோதரர்கள் சாபம்)",
    "afflicted_karaka": "Mars & 3rd Lord",
    "cause_en": "Cheating brothers out of ancestral wealth or inheritance, driving them into distress and anguish.",
    "cause_ta": "சகோதரர்களுக்குரிய சொத்து அல்லது பணத்தை தராமல் ஏமாற்றி அவர்களின் மனவேதனைக்கு ஆளாதல்.",
    "combinations": [
      "3rd lord occupies 5th conjoined with Mars & Rahu, while 5th and Lagna lords are in 8th.",
      "Mars in Lagna, Saturn in 5th, 3rd lord in 9th, and Jupiter in 12th.",
      "5th lord debilitated in 3rd while Saturn is in 5th, and Mars in 5th or 12th.",
      "Lagna lord in 12th, Mars in 5th, and 5th lord in 8th."
    ],
    "remedy_en": "Listen to Srimad Vishnu Purana; observe Chandrayana Vrata; bathe in the sacred Kaveri River or visit a revered Vishnu Kshetra; plant an Ashwatha tree with sacred thread and marriage rites; donate 10 cows, observe Prajapatya Vrata, and donate land with fruit trees.",
    "remedy_ta": "விஷ்ணு புராணம் கேட்டல், சந்திராயண விரதம், காவேரி ஸ்நானம், அரச மரக் கன்று நட்டு உபநயன-விவாக சடங்கு செய்தல், 10 பசுக்கள் தானம் மற்றும் பழமரங்கள் உள்ள நிலதானம்."
  },
  {
    "id": "matru_shapa",
    "shapa_name": "Matru Shapa (Curse of Mother)",
    "shapa_name_ta": "மாத்ரு சாபம் (தாயின் சாபம்)",
    "afflicted_karaka": "Moon & 4th Lord",
    "cause_en": "Hurting, abandoning, or speaking cruelly to one's mother or maternal figures.",
    "cause_ta": "தாயை உதாசீனப்படுத்துதல், கடுமையான சொற்களால் நோகடித்தல் மற்றும் அன்னையை கைவிடுதல்.",
    "combinations": [
      "5th lord is Moon, debilitated or hemmed with malefics, with malefics in 4th and 5th.",
      "Saturn in 11th, malefics in 4th, and Moon in 5th in debilitation.",
      "5th lord in 6, 8, or 12, Lagna lord debilitated, and Moon conjoined with malefics.",
      "Moon in 5th or 9th conjoined with Saturn, Rahu, Mars, and Jupiter.",
      "Cancer Lagna with Mars & Rahu, while Moon & Saturn occupy Scorpio."
    ],
    "remedy_en": "Perform 100,000 Gayatri Japa; donate a house or shelter; distribute milk boiled in silver vessels to scholars; serve food and perform 28,000 pradakshinas (circumambulations) around the sacred Ashwatha tree.",
    "remedy_ta": "ஒரு லட்சம் காயத்ரி ஜபம், இல்லம் தானம், வெள்ளிப் பாத்திரத்தில் பால் தானம் மற்றும் அரச மரத்தை 28,000 முறை வலம் வருதல்."
  },
  {
    "id": "matula_shapa",
    "shapa_name": "Matula Shapa (Curse of Maternal Uncle)",
    "shapa_name_ta": "மாதுல சாபம் (தாய்மாமன் சாபம்)",
    "afflicted_karaka": "Mercury & 6th Lord",
    "cause_en": "Betraying or humiliating maternal uncles or their rightful dues.",
    "cause_ta": "தாய்மாமனை வஞ்சிப்பது அல்லது தாய்மாமனின் உரிமைகளைப் பறிப்பது.",
    "combinations": [
      "5th house occupied by Mercury and Jupiter along with Mars and Rahu, with Saturn in Lagna.",
      "Lagna lord and 5th lord in 5th along with Mercury, Mars, and Saturn.",
      "5th lord in Lagna, combust Saturn in 7th, and Lagna lord with Mercury."
    ],
    "remedy_en": "Install a consecrated idol of Lord Vishnu; dig public drinking water wells, tanks, or reservoirs for the general public, and bathe at Rama Setu (Rameswaram).",
    "remedy_ta": "விஷ்ணு சிலை பிரதிஷ்டை செய்தல், பொதுமக்களுக்கு பயன்படும் குளம், கிணறு அல்லது குடிநீர் மையம் அமைத்தல், ராமேஸ்வர ராம சேதுவில் நீராடுதல்."
  },
  {
    "id": "brahma_shapa",
    "shapa_name": "Brahma Shapa (Curse of Scholars / Brahmins)",
    "shapa_name_ta": "பிரம்ம சாபம் (வேத வித்தகர்கள் சாபம்)",
    "afflicted_karaka": "Jupiter & 9th Lord",
    "cause_en": "Arrogance of one's education/wealth leading to insulting, ridiculing, or deceiving pious teachers and spiritual scholars.",
    "cause_ta": "கல்வி அல்லது செல்வச் செருக்கால் பெரியோர்களையும், சாதுக்களையும் அவமதித்தல்.",
    "combinations": [
      "Rahu in Jupiter's signs (Sagittarius/Pisces), 5th house occupied by Jupiter, Mars, Saturn, and 9th lord in 8th.",
      "9th lord in 5th, while 5th lord is in 8th with Jupiter, Mars, and Rahu.",
      "Jupiter debilitated in Lagna or 5th, while 5th lord occupies 6, 8, or 12.",
      "5th lord Jupiter occupies 8th with malefics while Sun or Moon is 5th lord."
    ],
    "remedy_en": "Observe Chandrayana Vrata and Brahma Koorcha Traya; donate cows facing south direction; donate five gems (Pancharatna) and gold; feed 1,000 to 10,000 Vedic scholars.",
    "remedy_ta": "சந்திராயண விரதம் மற்றும் பிரம்ம கூர்ச்ச த்ரயம், தெற்கு நோக்கி நின்று கோதானம் செய்தல், பஞ்சரத்னம் மற்றும் தங்கம் தானம், 10,000 பேருக்கு அன்னதானம்."
  },
  {
    "id": "patni_shapa",
    "shapa_name": "Patni / Stree Shapa (Curse of Wife / Woman)",
    "shapa_name_ta": "பத்னி / ஸ்த்ரீ சாபம் (மனைவி அல்லது பெண்ணின் சாபம்)",
    "afflicted_karaka": "Venus & 7th Lord",
    "cause_en": "Cruelty, infidelity, abandonment, or causing severe mental anguish to a wedded wife or noble women.",
    "cause_ta": "மனைவியை கைவிடுதல், துரோகம் செய்தல் அல்லது பெண்களை கண்ணீர் வடிக்க வைத்தல்.",
    "combinations": [
      "7th lord in 5th in Saturn's Navamsha, while 5th lord occupies 8th.",
      "Venus in 5th, 7th lord in 8th, and Jupiter conjoined with malefics.",
      "7th house occupied by Saturn and Venus, 8th lord Sun in 5th, Rahu in Lagna.",
      "5th house is Venus's sign (Taurus/Libra) occupied by Rahu and Moon, with malefics in 12, 1, 2."
    ],
    "remedy_en": "Perform Kanya Dana (sponsoring the wedding of an impoverished virtuous bride); donate decorated golden idols of Lakshmi-Narayana, along with 10 cows, clothes, bedding, and jewellery to deserving couples.",
    "remedy_ta": "கன்னிகாதானம் செய்து வைத்தல், லக்ஷ்மி-நாராயணன் விக்கிரகம், 10 பசுக்கள், புத்தாடைகள் மற்றும் படுக்கைகளை தம்பதிகளுக்கு தானம் செய்தல்."
  },
  {
    "id": "preta_shapa",
    "shapa_name": "Preta Shapa (Curse of Unfulfilled Ancestors / Disembodied Spirits)",
    "shapa_name_ta": "ப்ரேத சாபம் (சாந்தியடையாத ஆத்மாக்களின் சாபம்)",
    "afflicted_karaka": "Saturn, Rahu & 5th House",
    "cause_en": "Failure to perform proper funeral rites (Karma Lopa) at death, leaving ancestral souls un-emancipated and lingering in Pretatva.",
    "cause_ta": "முன்னோர்களுக்குரிய ஈமச் சடங்குகளை (கர்மாக்களை) முறையாக செய்யாமல் விடுவதால் ஆன்மாக்கள் சாந்தியடையாமல் தவித்தல்.",
    "combinations": [
      "Saturn and Sun in 5th, waning Moon in 7th, Rahu in Lagna, and Jupiter in 12th.",
      "Malefics in Lagna, Sun in 12th, Saturn, Mars & Mercury in 5th, and 5th lord in 8th.",
      "Rahu in Lagna, Saturn in 5th, and Jupiter in 8th.",
      "Lagna occupied by Saturn and Mandi, Rahu in 5th, Sun in 8th."
    ],
    "remedy_en": "Perform Vishnu Shraddha ceremony; take sacred Rudra Snana; donate an idol of Lord Brahma, milch cows, silver, and Blue Sapphire (Neela Ratna).",
    "remedy_ta": "விஷ்ணு சிரார்த்தம் செய்தல், ருத்ர ஸ்நானம், பிரம்மா விக்கிரகம், பசுக்கள், வெள்ளி மற்றும் நீலக்கல் (நீல ரத்தினம்) தானம் செய்தல்."
  },
  {
    "id": "parashara_planetary_progeny_remedies",
    "shapa_name": "Parashara's 9 Planetary Mitigations for Progeny Obstacles",
    "shapa_name_ta": "பராசரரின் ஒன்பது கிரக சந்தான பரிகாரங்கள்",
    "afflicted_karaka": "Specific Obstacle-Causing Graha",
    "cause_en": "Specific planetary doshas obstructing progeny and family expansion.",
    "cause_ta": "குழந்தைப்பேற்றைத் தடுக்கும் குறிப்பிட்ட கிரக தோஷங்கள்.",
    "combinations": [
      "Sun obstacle: Recite Harivamsha Purana (Harivamsha Parayana).",
      "Moon obstacle: Perform Shiva / Ishwara Aradhana.",
      "Mars obstacle: Perform Rudrabhisheka with red flowers and ghee.",
      "Mercury obstacle: Donate curd rice placed in a Kansya (bronze) vessel.",
      "Jupiter obstacle: Feed guests and perform dedicated Pitru Pooja.",
      "Venus obstacle: Donate healthy cows to deserving recipients.",
      "Saturn obstacle: Perform Maha Mrityunjaya Japa.",
      "Rahu obstacle: Perform Kanya Dana (sponsoring a virtuous girl's wedding).",
      "Ketu obstacle: Donate cows to virtuous and spiritual souls."
    ],
    "remedy_en": "Recitation of Valmiki Ramayana Bala Kanda (Payasa Paravrithi sarga - Dasharatha distributing payasam to his queens) and performing Santana Gopala Krishna Homa on Shravana star falling on Dwadashi tithi.",
    "remedy_ta": "ராமாயண பால காண்டத்தில் உள்ள பாயச தான சர்க்கத்தை பாராயணம் செய்தல் மற்றும் திருவோண நட்சத்திரம் துவாதசி திதியில் கூடும் நாளில் சந்தான கோபால கிருஷ்ண ஹோமம் செய்தல்."
  }
];

export const TATWAS_AND_NAVADWARAS: TatwaNavadwaraDetail[] = [
  {
    "tatwa_en": "Akasha (Ether / Space)",
    "tatwa_ta": "ஆகாய தத்துவம்",
    "planet": "Jupiter",
    "sense_en": "Shabda (Sound / Hearing)",
    "sense_ta": "சப்தம் (கேட்கும் உணர்வு)",
    "body_parts_en": "Ears, speech organ, lightning pathways, intellectual expansion",
    "body_parts_ta": "காதுகள், வாக்கு, செவிப்பாதை",
    "abhimani_devata": "Dishanatha (Directional Lords)"
  },
  {
    "tatwa_en": "Vayu (Air)",
    "tatwa_ta": "வாயு தத்துவம்",
    "planet": "Saturn",
    "sense_en": "Sparsha (Touch)",
    "sense_ta": "ஸ்பரிசம் (தொடு உணர்வு)",
    "body_parts_en": "Skin, nervous transmission, hands, bodily motions and joints",
    "body_parts_ta": "தோல், தொடு உணர்வு, நரம்புகள், மூட்டு அசைவுகள்",
    "abhimani_devata": "Vayu & Mitra"
  },
  {
    "tatwa_en": "Agni (Fire)",
    "tatwa_ta": "தேயு / அக்னி தத்துவம்",
    "planet": "Sun & Mars",
    "sense_en": "Roopa (Sight / Form)",
    "sense_ta": "ரூபம் (பார்வை உணர்வு)",
    "body_parts_en": "Eyes, face, body heat, digestive fire (Jatharagni), blood",
    "body_parts_ta": "கண்கள், முகம், உடற்சூடு, ஜடராக்னி",
    "abhimani_devata": "Agni & Surya"
  },
  {
    "tatwa_en": "Aapa / Jala (Water)",
    "tatwa_ta": "அப்பு / ஜல தத்துவம்",
    "planet": "Moon & Venus",
    "sense_en": "Rasa (Taste)",
    "sense_ta": "ரசம் (சுவை உணர்வு)",
    "body_parts_en": "Tongue, palate, all bodily juices, plasma, urine, mucus, semen",
    "body_parts_ta": "நாக்கு, ரத்த பிளாஸ்மா, சிறுநீர், சுக்ல-சோணிதம், கபம்",
    "abhimani_devata": "Varuna & Chandra"
  },
  {
    "tatwa_en": "Prithvi (Earth)",
    "tatwa_ta": "பிருத்வி / நில தத்துவம்",
    "planet": "Mercury",
    "sense_en": "Gandha (Smell)",
    "sense_ta": "கந்தம் (நுகரும் உணர்வு)",
    "body_parts_en": "Nose, smelling power, muscular tissue, nervous system (Naramandala)",
    "body_parts_ta": "மூக்கு, நுகர்வு ஆற்றல், தசை மண்டலம், நரம்பு மண்டலம்",
    "abhimani_devata": "Vishnu & Prajapati"
  }
];

export const CLASSICAL_CASE_STUDIES: ClinicalCaseStudy[] = [
  {
    "id": "case_1_mental_aberration_liver",
    "title_en": "Case 1: Mental Aberration & Liver Disorder",
    "title_ta": "வழக்கு 1: திடீர் மனக்குழப்பம் & கல்லீரல் பாதிப்பு",
    "patient_profile": "Female, Born 12-10-1972 at 11:50 AM (Sagittarius Lagna)",
    "disease_diagnosed": "Acute Mental Aberration & Hepatic Dysregulation",
    "astrological_indicators": [
      "Ascendant lord Jupiter afflicted by conjunction with Rahu in Lagna.",
      "Mind significator Moon debilitated in Scorpio aspected by Saturn.",
      "In Navamsha, Moon is further conjoined with Rahu.",
      "Liver significator Jupiter under shadow of Rahu."
    ],
    "dasha_timing": "Venus Mahadasha (6th lord of disease) and Moon Bhukti (debilitated mind significator).",
    "key_takeaway": "When the 6th lord dasha runs concurrently with an afflicted Moon sub-period and Jupiter is shadowed by Rahu, psychological disorientation and hepatic vulnerability manifest simultaneously."
  },
  {
    "id": "case_2_blood_cancer",
    "title_en": "Case 2: Blood Cancer (Leukemia)",
    "title_ta": "வழக்கு 2: ரத்தப் புற்றுநோய் (Blood Cancer)",
    "patient_profile": "Male, Born 15-11-1937 at 16:09 Bangalore (Aries Lagna)",
    "disease_diagnosed": "Leukemia / Blood Cancer",
    "astrological_indicators": [
      "Aries Lagna: 8th lord Mars (Swadeha Maraka) exalted in Capricorn with 12th lord Jupiter (expansion).",
      "8th house occupied by Rahu and Mercury, disposited by blood significator Mars.",
      "Mercury and Rahu occupy the asterism of Saturn, which aspects the 6th house."
    ],
    "dasha_timing": "Fag end of Mars Mahadasha at the Kuja-Rahu Sandhi transition point.",
    "key_takeaway": "Exalted Mars with expansive 12th lord Jupiter combined with Rahu in 8th in Saturn's star produced expansive blood cellular proliferation precisely at Kuja-Rahu Sandhi."
  },
  {
    "id": "case_3_mental_depression",
    "title_en": "Case 3: Chronic Mental Depression & Retardation",
    "title_ta": "வழக்கு 3: நாள்பட்ட மன அழுத்தம் & மூளை பலவீனம்",
    "patient_profile": "Male, Born 03-10-1981 at 01:15 Medak (Cancer Lagna)",
    "disease_diagnosed": "Chronic Mental Depression & Imbalance",
    "astrological_indicators": [
      "Lagna lord Moon debilitated in Scorpio receiving aspect of 8th lord Saturn.",
      "Lagna (Shiro Bhava) occupied by Mars and Rahu in Ashlesha star (12th lord).",
      "Intellect significator Mercury placed in the star of Rahu.",
      "4th lord Venus posited in the star of 6th lord Jupiter."
    ],
    "dasha_timing": "Perpetual psychological strain during Dasha of stars ruled by Rahu and Saturn.",
    "key_takeaway": "Debilitated Moon aspected by Saturn with Mars and Rahu directly in the head zone creates an enduring mental cloudiness (opacity) that defies standard therapy."
  },
  {
    "id": "case_4_cervical_spondylitis",
    "title_en": "Case 4: Cervical Spondylitis",
    "title_ta": "வழக்கு 4: கழுத்து எலும்புத் தேய்மானம் (Cervical Spondylitis)",
    "patient_profile": "Native with severe cervical spine degeneration",
    "disease_diagnosed": "Cervical Spondylitis & Nerve Compression",
    "astrological_indicators": [
      "3rd house (neck and cervical zone) receives combined aspects of Saturn and Mars.",
      "Lagna lord is conjoined with 8th lord Mercury (ruler of nerves and spinal signals).",
      "Jupiter aspects 3rd house, preventing complete structural paralysis."
    ],
    "dasha_timing": "Onset during operating periods of 3rd lord and aspecting Mars.",
    "key_takeaway": "Malefic aspects of Mars (inflammation) and Saturn (degeneration) on the 3rd house coupled with afflicted Mercury pinpoint spinal cervical spondylitis."
  },
  {
    "id": "case_5_bronchial_asthma",
    "title_en": "Case 5: Chronic Bronchial Asthma",
    "title_ta": "வழக்கு 5: நாள்பட்ட ஆஸ்துமா (Bronchial Asthma)",
    "patient_profile": "Native, Born 07-04-1991 at 14:35 Bangalore (Cancer Lagna)",
    "disease_diagnosed": "Bronchial Asthma & Mucous Obstruction",
    "astrological_indicators": [
      "6th lord Jupiter is retrograde and exalted in Cancer (watery sign).",
      "Ascendant lord Moon occupies the 6th house (Deha Kashta Yoga).",
      "Saturn (chronic illness) aspects both Lagna and 6th lord Jupiter."
    ],
    "dasha_timing": "Active Dasha periods of Jupiter and Saturn.",
    "key_takeaway": "Retrograde 6th lord exalted in a watery sign with Moon in 6th and Saturn's cold aspect creates chronic phlegmatic airway constriction."
  },
  {
    "id": "case_6_gynaecological_uterus_removal",
    "title_en": "Case 6: Gynaecological Complications & Uterus Removal",
    "title_ta": "வழக்கு 6: கருப்பை அறுவைசிகிச்சை (Hysterectomy)",
    "patient_profile": "Female native with severe uterine pathology",
    "disease_diagnosed": "Uterine Fibroids & Surgical Hysterectomy",
    "astrological_indicators": [
      "5th lord Venus (womb) debilitated in Virgo in the star of 8th lord Sun.",
      "Rahu occupies the 5th house.",
      "6th lord Mercury exalted in Virgo with Venus, aspected by surgical Mars and chronic Saturn.",
      "Venus hemmed in Papa Kartari Yoga between Sun, waning Moon, Ketu, and Saturn."
    ],
    "dasha_timing": "Mercury Mahadasha and Mercury Bhukti (6th lord of disease in Uccha Vargottama).",
    "key_takeaway": "Affliction to 5th house by Mars and Saturn while 5th lord is debilitated and conjoined with 6th lord compels surgical excision of the uterus."
  },
  {
    "id": "case_7_caesarean_delivery",
    "title_en": "Case 7: Urgent Caesarean Operation",
    "title_ta": "வழக்கு 7: அவசர சிசேரியன் அறுவைசிகிச்சை",
    "patient_profile": "Female, Capricorn Lagna with obstructed labour",
    "disease_diagnosed": "Obstructed Labour & Surgical Delivery",
    "astrological_indicators": [
      "7th house (abdominal zone) occupied by Moon and aspected by surgical planet Mars.",
      "No protective aspect of Jupiter on the 7th house or on Moon.",
      "Moon (governor of natural labour pains) afflicted by Mars and Saturn.",
      "Putrakaraka Jupiter conjoined with Ketu (which acts like Mars) in 6th house."
    ],
    "dasha_timing": "Mercury Mahadasha with Mars transit triggering the 7th house.",
    "key_takeaway": "When Mars aspects the Moon in the 7th without Jupiter's intervention, natural labour pains fail to manifest, necessitating urgent surgical intervention."
  },
  {
    "id": "case_8_normal_delivery",
    "title_en": "Case 8: Normal Child Delivery without Surgery",
    "title_ta": "வழக்கு 8: அறுவைசிகிச்சையற்ற சுகப்பிரசவம்",
    "patient_profile": "Female, Born 11-12-1954 at 03:30 AM",
    "disease_diagnosed": "Successful Natural Delivery",
    "astrological_indicators": [
      "7th house (abdomen) occupied by its own lord Venus and exalted Saturn without Mars aspect.",
      "Moon (labour pains) is completely free from the aspect of Mars.",
      "Exalted Jupiter in 4th casts full aspect on 5th lord Sun."
    ],
    "dasha_timing": "Mercury Mahadasha under Jupiter's protective transit.",
    "key_takeaway": "Even with badhakadhipati Saturn present, the complete absence of Mars's aspect on Moon and 7th plus Jupiter's exaltation aspect guarantees a safe natural delivery."
  },
  {
    "id": "case_9_brain_tumour_cross_chart",
    "title_en": "Case 9: Brain Tumour & Cross-Diagnosis via Husband's Chart",
    "title_ta": "வழக்கு 9: மூளைக் கட்டி & கணவர் ஜாதக வழி கண்டறிதல்",
    "patient_profile": "Wife Born 07-09-1958 at 17:46; Husband born in Sagittarius Lagna",
    "disease_diagnosed": "Brain Tumour (Meningioma) & Successful Surgery",
    "astrological_indicators": [
      "Wife: Lagna lord Moon (head) in 11th (badhaka sthana) with Mars (boils/tumours) in Mars star.",
      "Husband's Chart: 7th house (wife) is Gemini, ruled by Mercury; Mercury conjoins Mars and Ketu in 8th from Lagna.",
      "Wife's tumour detected during husband's Jupiter dasha (Jupiter in star of 7th lord Mercury)."
    ],
    "dasha_timing": "End of Jupiter Mahadasha (Rogadhipati dasha for wife).",
    "key_takeaway": "Astrology allows precise disease cross-diagnosis: the husband's 7th house derivative (Gemini with Mercury, Mars, Ketu) accurately mirrored his wife's brain surgery."
  },
  {
    "id": "case_10_leucoderma",
    "title_en": "Case 10: Leucoderma (Vitiligo) with Multi-Coloured Patches",
    "title_ta": "வழக்கு 10: வெண்புள்ளி நோய் (Leucoderma / Vitiligo)",
    "patient_profile": "Male, Born 15/16-07-1915 (Taurus Lagna)",
    "disease_diagnosed": "Leucoderma / Vitiligo",
    "astrological_indicators": [
      "Saturn aspects Venus (Lagna lord and Karaka for bodily radiance/beauty), creating ugliness.",
      "Mercury (ruler of skin) is conjoined with Ketu.",
      "Ketu rules 'Chitra Varna' (multi-coloured substances / depigmented white patches)."
    ],
    "dasha_timing": "Saturn Mahadasha at the Saturnine age of 60 years.",
    "key_takeaway": "Affliction of Venus by Saturn combined with Mercury and Ketu produces multi-coloured skin depigmentation known classically as Shvitra."
  },
  {
    "id": "case_11_breast_cancer",
    "title_en": "Case 11: Breast Cancer & Mastectomy",
    "title_ta": "வழக்கு 11: மார்பகப் புற்றுநோய் & அறுவைசிகிச்சை",
    "patient_profile": "Female, Born 03-04-1972 (Aries Lagna)",
    "disease_diagnosed": "Malignant Breast Tumour & Mastectomy",
    "astrological_indicators": [
      "4th house (breasts) occupied by Ketu.",
      "4th lord Moon is debilitated in 8th (Scorpio) and receives combined aspects of Mars and badhakadhipati Saturn.",
      "Lagna lord Mars is conjoined with badhakadhipati Saturn in the 2nd house."
    ],
    "dasha_timing": "Mercury Mahadasha (6th lord of disease and surgery).",
    "key_takeaway": "Affliction to the 4th house and 4th lord Moon by Saturn, Mars, and Ketu indicates tumours in the breast region, with surgery removing the organ."
  },
  {
    "id": "case_12_blindness_dagdha_rashis",
    "title_en": "Case 12: Blindness via Burnt Signs (Dagdha Rashis)",
    "title_ta": "வழக்கு 12: தக்த ராசிகள் மூலம் கண் பார்வை இழப்பு",
    "patient_profile": "Female, Born 12/13-07-1984 on Chaturdashi Tithi (Aries Lagna)",
    "disease_diagnosed": "Congenital / Juvenile Blindness",
    "astrological_indicators": [
      "Born on Chaturdashi Tithi, where Gemini, Virgo, Sagittarius, and Pisces become Dagdha (Burnt) Rashis.",
      "Both eye karakas, Sun and Moon, occupy Dagdha Rashis (Gemini and Sagittarius).",
      "2nd house occupied by Rahu; 12th lord Jupiter aspected by badhakadhipati Saturn.",
      "2nd lord Venus conjoined with 6th lord Mercury and aspected by exalted Saturn."
    ],
    "dasha_timing": "Early childhood dasha of afflicted 2nd and 12th lords.",
    "key_takeaway": "When both natural eye karakas (Sun and Moon) are trapped in Tithi Dagdha (Burnt) Rashis while 2nd and 12th houses are afflicted, irreversible loss of eyesight occurs."
  }
];


function resolveNakshatraInfo(nakObj: any): NakshatraMedicalDetail | null {
  if (!nakObj) return null;
  let starNum: number | null = null;
  if (typeof nakObj === "object") {
    if (typeof nakObj.index === "number") starNum = nakObj.index + 1;
    else if (typeof nakObj.number === "number") starNum = nakObj.number;
  } else if (typeof nakObj === "string") {
    for (const [num, data] of Object.entries(NAKSHATRA_27_MEDICAL_MATRIX)) {
      if (nakObj.toLowerCase().includes(data.name.toLowerCase())) {
        starNum = Number(num);
        break;
      }
    }
  }
  if (starNum && NAKSHATRA_27_MEDICAL_MATRIX[starNum]) {
    return NAKSHATRA_27_MEDICAL_MATRIX[starNum];
  }
  return null;
}

function evaluateDrKrishnaKumarCompendium(
  horoscope: HoroscopeResponse,
  houseOccupants: Record<number, string[]>,
  planetHouse: Record<string, number>,
  planetSign: Record<string, number>,
  houseToSign: Record<number, number>
): DrKrishnaKumarCompendium {
  const planets = (horoscope as any).planets || [];
  let moonStar: NakshatraMedicalDetail | null = null;
  for (const p of planets) {
    if (p.name === "Moon") {
      moonStar = resolveNakshatraInfo(p.nakshatra);
      break;
    }
  }

  const ascObj = (horoscope as any).ascendant;
  const lagnaStar = ascObj ? resolveNakshatraInfo(ascObj.nakshatra) : null;

  const all27 = Object.values(NAKSHATRA_27_MEDICAL_MATRIX);

  const h5Occ = houseOccupants[5] || [];
  const l5 = SIGN_LORDS[houseToSign[5]];
  const hL5 = planetHouse[l5];
  const l9 = SIGN_LORDS[houseToSign[9]];
  const hL9 = planetHouse[l9];
  const l3 = SIGN_LORDS[houseToSign[3]];
  const hL3 = planetHouse[l3];
  const l7 = SIGN_LORDS[houseToSign[7]];
  const hL7 = planetHouse[l7];
  const l4 = SIGN_LORDS[houseToSign[4]];
  const hL4 = planetHouse[l4];

  const jupH = planetHouse["Jupiter"];
  const rahuH = planetHouse["Rahu"];
  const satH = planetHouse["Saturn"];
  const marsH = planetHouse["Mars"];
  const moonH = planetHouse["Moon"];
  const sunH = planetHouse["Sun"];
  const mercH = planetHouse["Mercury"];
  const venH = planetHouse["Venus"];

  const evaluatedShapas: ProgenyShapaDetail[] = PROGENY_CURSES_AND_REMEDIES.map((sh) => {
    let isInd = false;
    let obs: string | null = null;

    if (sh.id === "sarpa_shapa") {
      if (h5Occ.includes("Rahu") || [1, 8].includes(planetSign["Rahu"])) {
        isInd = true;
        obs = "Rahu placed in 5th house or Mars sign (Aries/Scorpio) aligns with Sarpa Shapa indications.";
      } else if (satH === 5 && hL5 === 5) {
        isInd = true;
        obs = "Saturn conjoins 5th lord in the 5th house.";
      }
    } else if (sh.id === "pitru_shapa") {
      if (sunH === 5 && planetSign["Sun"] === 7) {
        isInd = true;
        obs = "Sun is debilitated in the 5th house.";
      } else if ([5, 9].includes(sunH) && (houseOccupants[sunH] || []).some(m => NATURAL_MALEFICS.has(m) && m !== "Sun")) {
        isInd = true;
        obs = `Sun posited in house ${sunH} with natural malefics.`;
      } else if ([6, 8, 12].includes(hL9)) {
        isInd = true;
        obs = `9th lord ${l9} placed in Dusthana (House ${hL9}).`;
      }
    } else if (sh.id === "bhratru_shapa") {
      if (hL3 === 5 && (h5Occ.includes("Mars") || h5Occ.includes("Rahu"))) {
        isInd = true;
        obs = `3rd lord ${l3} occupies 5th house alongside Mars/Rahu.`;
      } else if (marsH === 1 && satH === 5) {
        isInd = true;
        obs = "Mars occupies Lagna while Saturn is placed in 5th house.";
      }
    } else if (sh.id === "matru_shapa") {
      if (l5 === "Moon" && ([6, 8, 12].includes(moonH) || planetSign["Moon"] === 8)) {
        isInd = true;
        obs = "Moon is 5th lord in debilitation or placed in a Dusthana.";
      } else if (satH === 11 && moonH === 5 && planetSign["Moon"] === 8) {
        isInd = true;
        obs = "Saturn in 11th with debilitated Moon in 5th house.";
      }
    } else if (sh.id === "matula_shapa") {
      if (h5Occ.includes("Mercury") && ["Mars", "Rahu", "Saturn"].some(m => h5Occ.includes(m))) {
        isInd = true;
        obs = "Mercury occupies 5th house with natural malefics (Mars/Rahu/Saturn).";
      }
    } else if (sh.id === "brahma_shapa") {
      if ([9, 12].includes(planetSign["Rahu"]) && [5, 8].includes(jupH)) {
        isInd = true;
        obs = "Rahu in Jupiter's signs (Sagittarius/Pisces) while Jupiter is in 5th/8th.";
      } else if ([1, 5].includes(jupH) && planetSign["Jupiter"] === 10 && [6, 8, 12].includes(hL5)) {
        isInd = true;
        obs = "Jupiter debilitated in 1st/5th while 5th lord occupies Dusthana.";
      }
    } else if (sh.id === "patni_shapa") {
      if (hL7 === 5 && hL5 === 8) {
        isInd = true;
        obs = `7th lord ${l7} in 5th house while 5th lord ${l5} occupies 8th house.`;
      } else if ([6, 8, 12].includes(venH) && (houseOccupants[venH] || []).some(m => NATURAL_MALEFICS.has(m))) {
        isInd = true;
        obs = `Venus in Dusthana house ${venH} afflicted by malefics.`;
      }
    } else if (sh.id === "preta_shapa") {
      if (h5Occ.includes("Saturn") && h5Occ.includes("Sun")) {
        isInd = true;
        obs = "Saturn and Sun conjoined in 5th house.";
      } else if (rahuH === 1 && satH === 5) {
        isInd = true;
        obs = "Rahu in Lagna while Saturn occupies 5th house.";
      }
    } else if (sh.id === "parashara_planetary_progeny_remedies") {
      isInd = h5Occ.some(p => NATURAL_MALEFICS.has(p)) || [6, 8, 12].includes(hL5);
      obs = "Evaluated against 5th house occupants and 5th lord status.";
    }

    return {
      ...sh,
      is_indicated: isInd,
      chart_observation: obs,
    };
  });

  // Manasika & Organ Yogas evaluation
  const manasikaRules: MedicalRule[] = [];
  const organRules: MedicalRule[] = [];

  const addRule = (
    id: string,
    name: string,
    name_tamil: string,
    category: string,
    placements: string,
    interpEn: string,
    interpTa: string,
    anat: string,
    active: boolean,
    trig: string[],
    planetsInv: string[],
    housesInv: number[]
  ) => {
    const rule: MedicalRule = {
      id,
      name,
      name_tamil,
      source: "A Book on Medical Astrology (Dr. S. Krishna Kumar)",
      chapter_verse: "Chapters 1 & 2",
      category,
      system: "vedic",
      required_placements: placements,
      mandatory_conditions: [placements],
      traditional_interpretation: interpEn,
      interpretation_tamil: interpTa,
      anatomical_system: anat,
      is_active: active,
      status: active ? "Qualifying" : "Not Qualifying",
      triggered_positions: trig,
      planets_involved: planetsInv,
      relevant_houses: housesInv,
      conditions: [{ condition: placements, passed: active, detail: trig[0] || "Placement not fulfilled." }],
    };
    if (category.includes("Manasika")) manasikaRules.push(rule);
    else organRules.push(rule);
  };

  addRule("kk_theevra_buddhi", "Theevra Buddhi Yoga (Profound Intellect)", "தீவிர புத்தி யோகம் (அசாத்திய நுண்ணறிவு)", "Manasika & Buddhi Yogas", "5th lord in Kendra/Trikona", "Classical texts record superior intellectual acumen and deep analytical capacity.", "5-ம் அதிபதி சுப ஸ்தானத்தில் அமர்ந்து அசாத்திய நுண்ணறிவைத் தருகிறார்.", "Cerebral Cortex, Buddhi", [1, 4, 5, 7, 9, 10].includes(hL5), [`5th Lord ${l5} in House ${hL5}`], [l5], [5, hL5]);
  addRule("kk_parengita_gnana", "Parengita Gnana Yoga (Understanding Others)", "பரேங்கித ஞான யோகம் (பிறர் மனதை அறிதல்)", "Manasika & Buddhi Yogas", "Jupiter in Kendra/Trikona", "Intuitive psychological discernment into other minds.", "பிறர் மனதில் நடப்பதை அறியும் உள்ளுணர்வு மற்றும் விவேகம்.", "Intuitive Neural Pathways", [1, 4, 5, 7, 9, 10].includes(jupH), [`Jupiter in House ${jupH}`], ["Jupiter"], [jupH]);
  addRule("kk_buddhida_yoga", "Buddhida Yoga (Psychological Advisor)", "புத்தித யோகம் (ஆலோசகர் புத்தி)", "Manasika & Buddhi Yogas", "Benefics in 5th House", "Confers natural talent for counseling, psychological advisory, and mentorship.", "5-ம் வீட்டில் சுபர்கள் அமர்ந்து சிறந்த ஆலோசனை மற்றும் வழிகாட்டும் திறனைத் தருகின்றனர்.", "Cognitive Equilibrium", h5Occ.some(p => NATURAL_BENEFICS.has(p)), [`Benefics in 5th: ${h5Occ.filter(p => NATURAL_BENEFICS.has(p)).join(", ")}`], h5Occ.filter(p => NATURAL_BENEFICS.has(p)), [5]);
  addRule("kk_dharanadhi_samartha", "Dharanadhi Samartha Buddhi (Memory Retention)", "தாரணாதி சமர்த்த புத்தி யோகம் (நினைவாற்றல்)", "Manasika & Buddhi Yogas", "5th Lord & Jupiter in Kendras/Trikonas", "Extraordinary retention of knowledge, scripts, and texts.", "கேட்டதை மறக்காத அபார நினைவாற்றல் மற்றும் தாரணா சக்தி.", "Hippocampus, Memory Axis", [1, 4, 5, 7, 9, 10].includes(hL5) && [1, 4, 5, 7, 9, 10].includes(jupH), [`5th Lord in ${hL5}, Jupiter in ${jupH}`], [l5, "Jupiter"], [hL5, jupH]);
  addRule("kk_unmada_yoga", "Unmada Yoga (Emotional Surge & High BP)", "உன்மாத யோகம் (அதி தீவிர உணர்ச்சி & ரத்த அழுத்தம்)", "Manasika & Buddhi Yogas", "Jupiter in Lagna and Mars in 7th", "Predisposition to intense emotional swings and vascular reactivity.", "லக்னத்தில் குருவும் 7-ல் செவ்வாயும் நின்று அதி தீவிர உணர்ச்சிவசப்படுதலைத் தருகின்றனர்.", "Neuro-Vascular Axis", (jupH === 1 && marsH === 7) || (satH === 1 && [5, 7, 9].includes(marsH)), ["Jupiter/Mars or Saturn/Mars axis in Kendra/Trikona"], ["Jupiter", "Mars"], [1, 7]);
  addRule("kk_mati_bhramana", "Mati Bhramana Yoga (Mental Wavering)", "மதி பிரமண யோகம் (மனக் குழப்பம்)", "Manasika & Buddhi Yogas", "Moon & Saturn in 12th House", "Subconscious melancholy, restless sleep, and mental wavering.", "12-ல் சந்திரன்-சனி கூடி மனக்குழப்பம் மற்றும் தூக்கமின்மை தருகின்றனர்.", "Subconscious Processing", moonH === 12 && satH === 12, ["Moon and Saturn in House 12"], ["Moon", "Saturn"], [12]);

  // Organ Yogas
  addRule("kk_shiro_vyadhi", "Shiro Vyadhi Yoga (Head & Cranial Care)", "சிரோ வியாதி யோகம் (தலைப் பகுதி உணர்திறன்)", "Organ-Specific Yogas", "Lagna/6th Lord with Rahu/Ketu", "Cranial sensitivity to tension, vascular headaches, and sinus pressure.", "தலை மற்றும் மண்டை ஓட்டுப் பகுதியில் நரம்பு அழுத்தம் அல்லது தலைவலி கவனம்.", "Cranial Cavity, Head Nerves", [planetSign["Rahu"], planetSign["Ketu"]].includes(planetSign[SIGN_LORDS[houseToSign[1]]]) || [planetSign["Rahu"], planetSign["Ketu"]].includes(planetSign[SIGN_LORDS[houseToSign[6]]]), ["Lagna/6th lord conjoined Rahu/Ketu"], ["Rahu"], [1, 6]);
  addRule("kk_nethra_roga", "Nethra Roga Yoga (Vision Care & Eyes)", "நேத்ர ரோக யோகம் (கண் பார்வை பராமரிப்பு)", "Organ-Specific Yogas", "2nd Lord or Sun/Moon in Dusthanas", "Advises regular ocular checks and eye relaxation habits.", "கண் பார்வை, விழித்திரை ஆரோக்கியத்தில் தொடர் கவனிப்பு தேவை.", "Ocular System, Retina", [6, 8, 12].includes(planetHouse[SIGN_LORDS[houseToSign[2]]]) || [6, 8, 12].includes(sunH) || [6, 8, 12].includes(moonH), ["Eye indicators in Dusthana houses"], ["Sun", "Moon"], [2, 12]);
  addRule("kk_dantha_roga", "Dantha Roga Yoga (Dental Hygiene)", "தந்த ரோக யோகம் (பல் மற்றும் ஈறு பராமரிப்பு)", "Organ-Specific Yogas", "Rahu/Ketu in 2nd or 6th House", "Proactive dental hygiene to protect enamel and prevent periodontal decay.", "பல் சொத்தை மற்றும் ஈறுகளில் சோர்வு ஏற்படாமல் தொடர் பல் சுத்தம் அவசியம்.", "Dentition, Gums", (houseOccupants[6] || []).includes("Rahu") || (houseOccupants[6] || []).includes("Ketu") || (houseOccupants[2] || []).includes("Rahu"), ["Rahu/Ketu in 2nd or 6th house"], ["Rahu"], [2, 6]);
  addRule("kk_hridaya_roga", "Hridaya Roga Yoga (Cardiovascular Vitality)", "ஹிருதய ரோக யோகம் (இதய நலம்)", "Organ-Specific Yogas", "4th Lord in Dusthana or afflicted Sun", "Mindful pacing of physical exertion and cardiovascular wellness.", "இதயம் மற்றும் ரத்த ஓட்ட மண்டலத்தில் சீரான வாழ்க்கை முறை பேணல்.", "Cardiovascular System, Heart", [6, 8, 12].includes(hL4) || [6, 8, 12].includes(sunH), ["4th Lord or Sun in Dusthana house"], ["Sun"], [4]);
  addRule("kk_mrityunjaya_resuscitation", "Mrityunjaya Resuscitation Yoga", "மிருத்யுஞ்சய மீட்சி யோகம் (ஆபத்திலிருந்து மீளுதல்)", "Vedic Mitigation", "8th Lord in Kendra with Saturn", "Celebrated longevity formula conferring resilience to overcome critical emergencies.", "8-ம் அதிபதி சனியுடன் கூடி கேந்திரத்தில் அமர்ந்து ஆபத்துகளிலிருந்து காக்கும் அரிய யோகம்.", "Autonomic Life Reserves", [1, 4, 7, 10].includes(planetHouse[SIGN_LORDS[houseToSign[8]]]) && planetHouse[SIGN_LORDS[houseToSign[8]]] === satH, ["8th Lord in Kendra with Saturn"], ["Saturn"], [8, satH]);

  const delivObs = (marsH === 7 || (houseOccupants[7] || []).includes("Mars"))
    ? "Classical criteria from Chapter 4 of Dr. S. Krishna Kumar's book indicate that Mars influencing the 7th house (abdominal zone) or Moon without mitigating Jupiter aspect traditionally correlates with Caesarean surgical intervention."
    : "Classical criteria from Chapter 4 of Dr. S. Krishna Kumar's book indicate the absence of Mars's surgical aspect on the 7th house and Moon, supporting an uncomplicated natural delivery.";

  const spermObs = ([satH, mercH].includes(moonH) || moonH === planetHouse["Ketu"]) && ([satH, mercH].includes(venH) || venH === planetHouse["Ketu"])
    ? "Classical Beeja Dosha notice (Chapter 3): Dual interaction of Moon and Venus with neutral/eunuch planets. Classical texts prescribe Santana Gopala Krishna Homa on Shravana star falling on Dwadashi tithi."
    : "Balanced Beeja indicators: Primary reproductive significators (Moon and Venus) maintain balanced constitutional strength.";

  return {
    book_title: DR_KRISHNA_KUMAR_METADATA.book_title,
    book_title_ta: DR_KRISHNA_KUMAR_METADATA.book_title_ta,
    author: DR_KRISHNA_KUMAR_METADATA.author,
    publisher: DR_KRISHNA_KUMAR_METADATA.publisher,
    salient_features: DR_KRISHNA_KUMAR_METADATA.salient_features,
    native_moon_star: moonStar,
    native_lagna_star: lagnaStar,
    all_27_nakshatras: all27,
    gestational_months: PREGNANCY_GESTATIONAL_MONTHS,
    progeny_shapas: evaluatedShapas,
    case_studies: CLASSICAL_CASE_STUDIES,
    tatwas_and_senses: TATWAS_AND_NAVADWARAS,
    manasika_buddhi_yogas: manasikaRules,
    organ_specific_yogas: organRules,
    caesarean_vs_normal_delivery_observation: delivObs,
    sperm_potency_observation: spermObs,
  };
}


export function evaluateDrChatterjeeCompendium(
  horoscope: HoroscopeResponse,
  houseOccupants: Record<number, string[]>,
  planetHouse: Record<string, number>,
  planetSign: Record<string, number>,
  houseToSign: Record<number, number>,
  liveTransits?: LiveTransitsResponse | null
): DrChatterjeeCompendium {
  const planets = (horoscope as any).planets || [];
  const asc = (horoscope as any).ascendant;
  const ascLong = asc?.longitude ? Number(asc.longitude) : 0;

  let sunLong = 0;
  let moonLong = 0;
  let jupLong = 0;
  for (const p of planets) {
    const pName = p.name || "";
    const pLong = Number(p.longitude || 0);
    if (pName === "Sun") sunLong = pLong;
    else if (pName === "Moon") moonLong = pLong;
    else if (pName === "Jupiter") jupLong = pLong;
  }

  // 1. Death Point Calculation: (Ascendant + Sun + Moon + Jupiter) % 360
  const dpLong = (ascLong + sunLong + moonLong + jupLong) % 360.0;
  const dpSignIdx = Math.floor(dpLong / 30) + 1;
  const degInSign = Math.round((dpLong % 30) * 100) / 100;
  const signNamesEn = [
    "", "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
  ];
  const signNamesTa = [
    "", "மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி",
    "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"
  ];
  const dpSignEn = signNamesEn[dpSignIdx] || "Unknown";
  const dpSignTa = signNamesTa[dpSignIdx] || "தெரியவில்லை";

  const nakshatraNames = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
  ];
  const nakSpan = 360.0 / 27.0;
  const dpNakIdx = Math.floor(dpLong / nakSpan);
  const dpNakName = nakshatraNames[dpNakIdx % 27] || "Ashwini";
  const degInNak = dpLong % nakSpan;
  const dpNakPada = Math.floor(degInNak / (nakSpan / 4.0)) + 1;

  let satCurrSign = planetSign["Saturn"] || 10;
  if (liveTransits && liveTransits.planets) {
    const tSat = Array.isArray(liveTransits.planets)
      ? liveTransits.planets.find((p: any) => p.name === "Saturn")
      : (liveTransits.planets as any)["Saturn"];
    if (tSat && tSat.sign_index) satCurrSign = Number(tSat.sign_index);
  }

  const satAspectSigns = new Set([
    satCurrSign,
    ((satCurrSign + 2 - 1) % 12) + 1,
    ((satCurrSign + 6 - 1) % 12) + 1,
    ((satCurrSign + 9 - 1) % 12) + 1,
  ]);
  const satAspectActive = satAspectSigns.has(dpSignIdx);

  const deathPoint: DeathPointCalculation = {
    formula: "Ascendant Longitude + Sun Longitude + Moon Longitude + Jupiter Longitude (mod 360°)",
    longitude_deg: Math.round(dpLong * 100) / 100,
    sign_index: dpSignIdx,
    sign_name_en: dpSignEn,
    sign_name_ta: dpSignTa,
    degree_in_sign: degInSign,
    nakshatra_name: dpNakName,
    nakshatra_pada: dpNakPada,
    transit_saturn_aspect_active: satAspectActive,
    aspect_details_en: `Death Point at ${degInSign.toFixed(2)}° ${dpSignEn} (${dpNakName} Pada ${dpNakPada}). Transit Saturn in Sign ${satCurrSign} (${signNamesEn[satCurrSign] || ""}) ` +
      (satAspectActive
        ? "casts direct drishti/conjunction upon this sensitive point, indicating heightened constitutional vigilance."
        : "does not aspect this sensitive point, signifying general vital stability."),
    aspect_details_ta: `மிருத்யு புள்ளி ${dpSignTa} ராசியில் ${degInSign.toFixed(2)}° (${dpNakName} பாதம் ${dpNakPada})-ல் அமைந்துள்ளது. கோச்சார சனி ${signNamesTa[satCurrSign] || ""}-ல் நின்று ` +
      (satAspectActive
        ? "இப்புள்ளியைப் பார்ப்பதால் உடல் ஆரோக்கியத்தில் கூடுதல் விழிப்புணர்வு தேவைப்படுகிறது."
        : "இப்புள்ளியைப் பார்க்கவில்லை; எனவே ஆயுள் பலம் சீராக உள்ளது."),
  };

  // 2. Parijata Longevity Shield
  const kendraOccupants = [1, 4, 7, 10].flatMap(h => houseOccupants[h] || []);
  const trikonaOccupants = [1, 5, 9].flatMap(h => houseOccupants[h] || []);
  const kendraBenefics = kendraOccupants.filter(p => ["Jupiter", "Venus", "Mercury"].includes(p));
  const maleficsIn3or11 = [3, 11].flatMap(h => houseOccupants[h] || []).filter(p => ["Saturn", "Mars", "Rahu", "Sun"].includes(p));
  const hasShield = kendraBenefics.length > 0 || maleficsIn3or11.length > 0;
  const parijataLongevity = hasShield
    ? `Parijata Shield Active: Natural benefics (${kendraBenefics.join(", ") || "supportive"}) in Angles/Trines and/or Malefics (${maleficsIn3or11.join(", ") || "favorable"}) in Upachaya (3/11) promote sustained resilience and disease containment.`
    : "Standard constitutional vitality. Preserving daily Ayurvedic routine (Dinacharya) supports metabolic equilibrium.";

  // 3. Sapta Dhatus (7 tissues)
  const saptaDhatus: SaptaDhatuDetail[] = [
    {
      dhatu_number: 1,
      dhatu_name_en: "Asthi (Bone System)",
      dhatu_name_ta: "அஸ்தி (எலும்பு மண்டலம்)",
      sanskrit_term: "Asthi Dhatu",
      governing_planet: "Sun",
      physiological_function_en: "Skeletal framework, calcium metabolism, dental roots, cranial architecture",
      physiological_function_ta: "எலும்புக் கட்டமைப்பு, கால்சியம் சத்து, பற்கள் மற்றும் மண்டை ஓட்டு வலிமை",
      status: planetHouse["Sun"] ? `House ${planetHouse["Sun"]}` : "Active",
      observations_en: `Sun placed in House ${planetHouse["Sun"] || 1}. Governs structural posture and bone mineral density.`,
      observations_ta: `சூரியன் பாவம் ${planetHouse["Sun"] || 1}-ல் உள்ளார். எலும்பு மற்றும் தண்டுவட ஆரோக்கியத்தை வழிநடத்துகிறார்.`,
    },
    {
      dhatu_number: 2,
      dhatu_name_en: "Rasa (Plasma & Lymph)",
      dhatu_name_ta: "ரசம் (பிளாஸ்மா & நிணநீர்)",
      sanskrit_term: "Rasa Dhatu",
      governing_planet: "Moon",
      physiological_function_en: "Fluid balance, lymphatic circulation, extracellular moisture, nourishment delivery",
      physiological_function_ta: "உடல் திரவ சமநிலை, நிணநீர் சுழற்சி மற்றும் ஊட்டச்சத்து விநியோகம்",
      status: planetHouse["Moon"] ? `House ${planetHouse["Moon"]}` : "Active",
      observations_en: `Moon placed in House ${planetHouse["Moon"] || 1}. Governs emotional fluids, mucosal membranes, and plasma volume.`,
      observations_ta: `சந்திரன் பாவம் ${planetHouse["Moon"] || 1}-ல் உள்ளார். உடல் நீர்ப்பதம் மற்றும் நிணநீர் அமைப்பை ஆளுகிறார்.`,
    },
    {
      dhatu_number: 3,
      dhatu_name_en: "Rakta (Blood & Hemoglobin)",
      dhatu_name_ta: "ரக்தம் (இரத்தம் & சிவப்பணுக்கள்)",
      sanskrit_term: "Rakta Dhatu",
      governing_planet: "Mars",
      physiological_function_en: "Oxygenation, hemoglobin synthesis, thermal distribution, hepatic circulation",
      physiological_function_ta: "ஆக்ஸிஜன் விநியோகம், இரத்த அணுக்கள் உருவாக்கம் மற்றும் உடல் வெப்பம்",
      status: planetHouse["Mars"] ? `House ${planetHouse["Mars"]}` : "Active",
      observations_en: `Mars placed in House ${planetHouse["Mars"] || 1}. Regulates vital warmth, bone marrow stimulation, and arterial vitality.`,
      observations_ta: `செவ்வாய் பாவம் ${planetHouse["Mars"] || 1}-ல் உள்ளார். இரத்த ஓட்டம் மற்றும் சிவப்பணுக்கள் உற்பத்தியை வழிநடத்துகிறார்.`,
    },
    {
      dhatu_number: 4,
      dhatu_name_en: "Mamsa / Twak (Muscle & Skin Tissue)",
      dhatu_name_ta: "மாம்சம் / த்வக் (தசை & தோல் திசு)",
      sanskrit_term: "Mamsa Dhatu",
      governing_planet: "Mercury",
      physiological_function_en: "Muscular covering, epidermal barrier, neurotransmission to dermis, visceral motor control",
      physiological_function_ta: "தசை வளர்ச்சி, தோல் பாதுகாப்பு உறை மற்றும் நரம்புத் தூண்டுதல்",
      status: planetHouse["Mercury"] ? `House ${planetHouse["Mercury"]}` : "Active",
      observations_en: `Mercury placed in House ${planetHouse["Mercury"] || 1}. Controls neuromuscular coordination and dermal integrity.`,
      observations_ta: `புதன் பாவம் ${planetHouse["Mercury"] || 1}-ல் உள்ளார். நரம்பு-தசை ஒருங்கிணைப்பு மற்றும் தோல் நலம் காக்கிறார்.`,
    },
    {
      dhatu_number: 5,
      dhatu_name_en: "Medas (Adipose Tissue & Fat)",
      dhatu_name_ta: "மேதஸ் (கொழுப்புத் திசு)",
      sanskrit_term: "Medas Dhatu",
      governing_planet: "Jupiter",
      physiological_function_en: "Lubrication of joints, insulation, energy reserves, protective cushioning around organs",
      physiological_function_ta: "மூட்டுகளின் நெகிழ்வுத்தன்மை, உடல் கொழுப்பு சமநிலை மற்றும் உள்ளுறுப்புப் பாதுகாப்பு",
      status: planetHouse["Jupiter"] ? `House ${planetHouse["Jupiter"]}` : "Active",
      observations_en: `Jupiter placed in House ${planetHouse["Jupiter"] || 1}. Directs lipid digestion, hepatic glycogen reserves, and endocrine cushioning.`,
      observations_ta: `குரு பாவம் ${planetHouse["Jupiter"] || 1}-ல் உள்ளார். கொழுப்பு செரிமானம் மற்றும் கல்லீரல் கிளைகோஜன் அளவை ஒழுங்குபடுத்துகிறார்.`,
    },
    {
      dhatu_number: 6,
      dhatu_name_en: "Majja (Bone Marrow & Nervous Core)",
      dhatu_name_ta: "மஜ்ஜை (எலும்பு மஜ்ஜை & நரம்பு மையம்)",
      sanskrit_term: "Majja Dhatu",
      governing_planet: "Venus",
      physiological_function_en: "Internal marrow synthesis, cerebrospinal lubrication, sensory nerve myelin sheath",
      physiological_function_ta: "எலும்பு மஜ்ஜை ஆழம், மூளைத்தண்டு திரவம் மற்றும் நரம்பு உறை பாதுகாப்பு",
      status: planetHouse["Venus"] ? `House ${planetHouse["Venus"]}` : "Active",
      observations_en: `Venus placed in House ${planetHouse["Venus"] || 1}. Governs reproductive longevity and neural contentment.`,
      observations_ta: `சுக்கிரன் பாவம் ${planetHouse["Venus"] || 1}-ல் உள்ளார். நரம்பு மண்டல சுறுசுறுப்பு மற்றும் மஜ்ஜை ஊட்டம் காக்கிறார்.`,
    },
    {
      dhatu_number: 7,
      dhatu_name_en: "Snayu / Shukra (Tendons & Reproductive Essence)",
      dhatu_name_ta: "ஸ்நாயு / சுக்கிரன் (தசைநாண்கள் & சுக்லம்)",
      sanskrit_term: "Shukra / Snayu Dhatu",
      governing_planet: "Saturn",
      physiological_function_en: "Ligaments, tendons, collagen fibres, somatic endurance, generative vitality",
      physiological_function_ta: "தசைநாண்கள், தசைப்பிணைப்புகள், உடலின் சகிப்புத்தன்மை மற்றும் உயிர் ஆற்றல்",
      status: planetHouse["Saturn"] ? `House ${planetHouse["Saturn"]}` : "Active",
      observations_en: `Saturn placed in House ${planetHouse["Saturn"] || 1}. Regulates structural tension, ligament strength, and long-term stamina.`,
      observations_ta: `சனி பாவம் ${planetHouse["Saturn"] || 1}-ல் உள்ளார். தசைநாண்கள் வலிமை மற்றும் நீண்டகால உடல் சகிப்புத்தன்மையை ஆளுகிறார்.`,
    },
  ];

  // 4. Endocrine Glands (8 glands)
  const endocrineGlands: EndocrineGlandDetail[] = [
    {
      gland_name_en: "Pituitary Gland (Master Gland)",
      gland_name_ta: "பிட்யூட்டரி சுரப்பி (தலைமைச் சுரப்பி)",
      governing_planets: ["Sun", "Moon", "Jupiter"],
      hormones_secreted: "ACTH, TSH, GH, LH, FSH, Oxytocin, Vasopressin",
      physiological_role_en: "Coordinates entire endocrine symphony; governs somatic growth, metabolic cues, and stress axis",
      physiological_role_ta: "உடலின் அனைத்து சுரப்பிகளையும் வழிநடத்துதல், உடல் வளர்ச்சி மற்றும் மன அழுத்தச் சமநிலை",
      status: "Active",
      observations_en: "Governed by the luminaries and Jupiter. Stable Lagna lord supports pituitary equilibrium.",
      observations_ta: "சூரியன், சந்திரன் மற்றும் குருவால் ஆளப்படுகிறது. லக்னாதிபதி பலம் தலைமைச் சுரப்பியின் செயல்பாட்டைச் சீராக்கும்.",
    },
    {
      gland_name_en: "Pineal Gland",
      gland_name_ta: "பீனியல் சுரப்பி",
      governing_planets: ["Moon", "Ketu"],
      hormones_secreted: "Melatonin, Serotonin derivatives",
      physiological_role_en: "Circadian sleep-wake rhythm, seasonal bioperiodicity, spiritual intuitions",
      physiological_role_ta: "உறக்கம்-விழிப்பு சுழற்சி மற்றும் இரவு நேர மெலடோனின் உற்பத்தி",
      status: "Active",
      observations_en: "Governed by Moon and Ketu. Harmonious 12th house fosters uninterrupted melatonin secretion.",
      observations_ta: "சந்திரன் மற்றும் கேதுவால் ஆளப்படுகிறது. 12-ம் பாவம் சுபமாக இருப்பது அமைதியான உறக்கத்திற்கு உகந்தது.",
    },
    {
      gland_name_en: "Thyroid Gland",
      gland_name_ta: "தைராய்டு சுரப்பி",
      governing_planets: ["Mercury", "Venus"],
      hormones_secreted: "Thyroxine (T4), Triiodothyronine (T3)",
      physiological_role_en: "Basal metabolic rate, heat production, cellular respiration, oxygen utilization",
      physiological_role_ta: "அடிப்படை வளர்சிதை மாற்றம், உடல் வெப்ப உற்பத்தி மற்றும் ஆற்றல் சமநிலை",
      status: "Active",
      observations_en: "Mapped to the 2nd/3rd houses (throat). Mercury and Venus govern vocal cords and thyroid lobules.",
      observations_ta: "தொண்டைப் பகுதியைக் குறிக்கும் 2 மற்றும் 3-ம் வீடுகள். புதன் மற்றும் சுக்கிரன் தைராய்டு நலனை வழிநடத்துகின்றனர்.",
    },
    {
      gland_name_en: "Parathyroid Gland",
      gland_name_ta: "பாராதைராய்டு சுரப்பி",
      governing_planets: ["Sun", "Saturn"],
      hormones_secreted: "Parathyroid Hormone (PTH / Parathormone)",
      physiological_role_en: "Calcium-phosphate homeostasis, neuromuscular excitability, bone resorption equilibrium",
      physiological_role_ta: "கால்சியம் மற்றும் பாஸ்பரஸ் சமநிலை, நரம்புத் துடிப்பு மற்றும் எலும்பு உறுதி",
      status: "Active",
      observations_en: "Sun rules calcium assimilation while Saturn governs bone retention. Both govern PTH balance.",
      observations_ta: "சூரியன் மற்றும் சனியின் சமநிலை உடலின் கால்சியம் மற்றும் தாது உப்புக்களைக் கட்டுப்படுத்துகிறது.",
    },
    {
      gland_name_en: "Thymus Gland",
      gland_name_ta: "தைமஸ் சுரப்பி",
      governing_planets: ["Moon", "Sun"],
      hormones_secreted: "Thymosin, Thymopoietin",
      physiological_role_en: "T-cell maturation, cellular adaptive immunity, youthful resilience, self-non-self discrimination",
      physiological_role_ta: "நோய் எதிர்ப்பு சக்திக்கான T-செல்கள் முதிர்ச்சி மற்றும் மார்பக மையப் பாதுகாப்பு",
      status: "Active",
      observations_en: "Located in 4th house (thoracic cavity). Sun and Moon nourish primary lymphatic immune defense.",
      observations_ta: "மார்புப் பகுதியான 4-ம் வீட்டில் அமைந்துள்ளது. சூரிய-சந்திர பலம் இயற்கையான நோய் எதிர்ப்பு ஆற்றலைத் தரும்.",
    },
    {
      gland_name_en: "Pancreas (Endocrine Islets)",
      gland_name_ta: "கணையம் (லாங்கர்ஹான்ஸ் திட்டுக்கள்)",
      governing_planets: ["Venus", "Jupiter"],
      hormones_secreted: "Insulin (Beta cells), Glucagon (Alpha cells), Somatostatin",
      physiological_role_en: "Blood glucose regulation, carbohydrate glycolysis, cellular energy uptake, lipid anabolism",
      physiological_role_ta: "இரத்த சர்க்கரை அளவு கட்டுப்பாடு, இன்சுலின் சுரப்பு மற்றும் குளுக்கோஸ் பயன்பாடு",
      status: "Active",
      observations_en: "Venus (insulin) and Jupiter (glycogen storage) operate in tandem. Virgo represents anatomical site.",
      observations_ta: "சுக்கிரன் (இன்சுலின்) மற்றும் குரு (கிளைகோஜன்) இணைந்து கன்னி ராசி வழியாக கணையத்தை ஆளுகின்றனர்.",
    },
    {
      gland_name_en: "Adrenal Glands",
      gland_name_ta: "அட்ரீனல் சுரப்பிகள்",
      governing_planets: ["Mars", "Sun"],
      hormones_secreted: "Adrenaline, Noradrenaline, Cortisol, Aldosterone, DHEA",
      physiological_role_en: "Sympathetic fight-or-flight surge, vascular pressure, fluid electrolyte balance, anti-inflammatory buffer",
      physiological_role_ta: "அவசரகால சண்டை அல்லது தப்பிக்கும் ஹார்மோன்கள், இரத்த அழுத்தம் மற்றும் கார்டிசால் கட்டுப்பாடு",
      status: "Active",
      observations_en: "Mars governs the inner medulla (adrenaline surge) while Sun rules the outer cortex (cortisol).",
      observations_ta: "செவ்வாய் அட்ரீனல் மையத்தையும் (அட்ரினலின்), சூரியன் வெளிப்புற கார்டெக்ஸையும் ஆளுகின்றனர்.",
    },
    {
      gland_name_en: "Sex Glands (Gonads / Ovaries / Testes)",
      gland_name_ta: "இனப்பெருக்க சுரப்பிகள் (கருப்பை / விந்தகம்)",
      governing_planets: ["Venus", "Mars"],
      hormones_secreted: "Estrogen, Progesterone, Testosterone",
      physiological_role_en: "Gamete maturation, secondary sexual traits, tissue rejuvenation, vitality preservation",
      physiological_role_ta: "இனப்பெருக்க அணுக்கள் உற்பத்தி, உடற்கூறு இளமை மற்றும் ஹார்மோன் சுழற்சி",
      status: "Active",
      observations_en: "7th and 8th houses mapped to pelvis. Venus and Mars govern hormonal potency and ovulatory rhythm.",
      observations_ta: "இடுப்புப் பகுதியான 7 மற்றும் 8-ம் வீடுகள். சுக்கிரன் மற்றும் செவ்வாய் இனப்பெருக்க சமநிலையை வழிநடத்துகின்றனர்.",
    },
  ];

  // 5. Tridosha Sites
  const tridoshaSites: TridoshaSiteDetail[] = [
    {
      site_en: "Head & Cranium (Kalapurusha House 1)",
      site_ta: "தலை & மண்டை ஓடு (காலபுருஷனின் 1-ம் பாவம்)",
      governing_signs: ["Aries", "Taurus"],
      vata_manifestation: "Tension headache, neural twitches, cerebral dryness, vertigo",
      pitta_manifestation: "Temporal burning, ocular inflammation, vascular migraine, hypertension",
      kapha_manifestation: "Sinus congestion, lethargy, heavy occiput, mucus buildup in cranium",
    },
    {
      site_en: "Throat & Neck (Kalapurusha Houses 2 & 3)",
      site_ta: "தொண்டை & கழுத்து (காலபுருஷனின் 2 & 3-ம் பாவங்கள்)",
      governing_signs: ["Gemini"],
      vata_manifestation: "Hoarseness, vocal cord spasm, cervical disc stiffness, dry throat",
      pitta_manifestation: "Pharyngitis, acid reflux burn in esophagus, thyroid inflammation",
      kapha_manifestation: "Goitre enlargement, excessive phlegm, tonsillar swelling, uvular edema",
    },
    {
      site_en: "Thorax & Chest (Kalapurusha House 4)",
      site_ta: "மார்பு & நுரையீரல் (காலபுருஷனின் 4-ம் பாவம்)",
      governing_signs: ["Cancer", "Leo"],
      vata_manifestation: "Cardiac arrhythmia, dry nocturnal cough, dyspnoea on minimal exertion",
      pitta_manifestation: "Myocardial burning, acute bronchitis with fever, pericardial heat",
      kapha_manifestation: "Bronchial asthma, chronic pulmonary effusion, productive coughing, heaviness",
    },
    {
      site_en: "Abdomen & Viscera (Kalapurusha Houses 5, 6, 7)",
      site_ta: "வயிறு & உள்ளுறுப்புகள் (காலபுருஷனின் 5, 6, 7-ம் பாவங்கள்)",
      governing_signs: ["Virgo", "Libra", "Scorpio"],
      vata_manifestation: "Colic spasm, chronic flatulence, erratic appetite (Vishamagni), constipation",
      pitta_manifestation: "Hyperacidity (Tikshnagni), peptic ulcer, bile reflux, inflammatory bowel",
      kapha_manifestation: "Sluggish metabolism (Mandagni), fatty liver infiltration, ascites, diabetes",
    },
    {
      site_en: "Pelvis, Knees & Lower Extremities (Kalapurusha Houses 8, 9, 10, 11, 12)",
      site_ta: "இடுப்பு, மூட்டுகள் & கால்கள் (காலபுருஷனின் 8 முதல் 12-ம் பாவங்கள்)",
      governing_signs: ["Sagittarius", "Capricorn", "Aquarius", "Pisces"],
      vata_manifestation: "Sciatica, osteoarthritis, cracking synovial joints, lumbar stiffness",
      pitta_manifestation: "Gouty arthritis (Vata-Rakta), burning feet syndrome, hot joint effusions",
      kapha_manifestation: "Pedal edema, varicose sluggishness, heavy swollen ankles, lymph stasis",
    },
  ];

  // 6. Diabetes Mellitus Special Diagnostic Module
  const venH = planetHouse["Venus"] || 1;
  const venSign = planetSign["Venus"] || 1;
  const jupH = planetHouse["Jupiter"] || 1;
  const jupSign = planetSign["Jupiter"] || 1;
  const virgoOcc = houseOccupants[6] || [];
  const h6Occ = houseOccupants[6] || [];

  let afflictionScore = 0;
  if (venSign === 6 || [6, 8, 12].includes(venH)) afflictionScore += 1;
  if (jupSign === 10 || [6, 8, 12].includes(jupH)) afflictionScore += 1;
  if (h6Occ.includes("Sun") || h6Occ.includes("Saturn")) afflictionScore += 1;

  const riskLevel = afflictionScore >= 3 ? "High" : (afflictionScore >= 1 ? "Moderate" : "Low");

  const diabetesAssessment: DiabetesMellitusAssessment = {
    venus_status: `Occupies House ${venH} in Sign ${signNamesEn[venSign] || ""}` + (venSign === 6 || [6, 8, 12].includes(venH) ? " (Debilitated/Dusthana)" : " (Stable)"),
    jupiter_status: `Occupies House ${jupH} in Sign ${signNamesEn[jupSign] || ""}` + (jupSign === 10 || [6, 8, 12].includes(jupH) ? " (Debilitated/Dusthana)" : " (Stable)"),
    virgo_status: `Occupants in Virgo: ${virgoOcc.join(", ") || "Unoccupied (Clear)"}`,
    sixth_house_status: `Occupants in 6th: ${h6Occ.join(", ") || "Unoccupied (Clear)"}`,
    affliction_score: afflictionScore,
    risk_level: riskLevel,
    symptoms_noted: [
      "Sudden loss of physical stamina and unexplained fatigue",
      "Polydipsia (excessive thirst) and polyuria (frequent urination)",
      "Polyphagia (excessive hunger) coupled with sudden weight loss",
      "Slow-healing dermal boils, skin dryness, and neuritis tingling in extremities",
      "Fluctuating blood glucose levels causing ocular or emotional distress",
    ],
    remedial_measures_en: [
      "Germinated Bengal gram (chana) with curd / buttermilk in morning breakfast",
      "Fresh tender neem leaves (5-7 leaves) chewed on an empty stomach with warm water",
      "Bitter gourd (karela) juice extracted with skin, consumed 3 mornings weekly",
      "Fenugreek seeds (methi) soaked overnight in water, masticated thoroughly before meals",
      "Strict avoidance of refined white sugar, sweets, cold refrigerated drinks, and oily sweets",
      "Brisk morning walking for 30-40 minutes daily to enhance somatic insulin receptor sensitivity",
    ],
    remedial_measures_ta: [
      "காலை உணவாக முளைகட்டிய கடலை மற்றும் மோர் சேர்த்த உணவு உட்கொள்ளுதல்",
      "வெறும் வயிற்றில் 5-7 இளம் வேப்பிலைகளை மென்று உண்டு வெந்நீர் அருந்துதல்",
      "வாரத்திற்கு 3 நாட்கள் காலையில் தோல் நீக்காத பாகற்காய் சாறு அருந்துதல்",
      "இரவில் ஊறவைத்த வெந்தயத்தை காலையில் மென்று தின்று அதன் நீரைக் குடித்தல்",
      "வெள்ளை சர்க்கரை, இனிப்புகள் மற்றும் குளிர்ந்த குளிர்பானங்களைத் தவிர்த்தல்",
      "தினசரி 30 நிமிடங்கள் விறுவிறுப்பான நடைபயிற்சி மேற்கொண்டு இன்சுலின் ஏற்பித் திறனை அதிகரித்தல்",
    ],
  };

  // 7. 10 Modern Complex Diseases
  const modernDiseases: ModernComplexDiseaseDetail[] = [
    {
      name_en: "Hepatitis C Viral Hepatic Strain",
      name_ta: "ஹெபடைடிஸ் சி கல்லீரல் பாதிப்பு",
      key_symptoms: "Chronic fatigue, elevated transaminases, abdominal fullness, digestive sluggishness",
      astrological_indicators: "Ketu in Lagna with 8th lord affliction and Jupiter-Mars friction in Dusthanas",
    },
    {
      name_en: "Systemic Lupus Erythematosus (SLE / Autoimmune)",
      name_ta: "லூபஸ் தன்னுடல் தாங்குதிறன் குறைபாடு",
      key_symptoms: "Malar butterfly rash, recurrent joint inflammation, photosensitivity, renal protein leaks",
      astrological_indicators: "Moon-Rahu afflicted in Lagna or 6th, alongside debilitated Mars-Saturn nexus",
    },
    {
      name_en: "Celiac Disease & Gluten Enteropathy",
      name_ta: "சீலியாக் குடல் செரிமானப் பிரச்சனை",
      key_symptoms: "Intestinal villous atrophy, chronic diarrhea, malabsorption, bloating after cereal grains",
      astrological_indicators: "Virgo (6th sign) afflicted by Rahu/Saturn; 5th lord combust in 6th or 8th house",
    },
    {
      name_en: "Meniere's Disease & Paroxysmal Vertigo",
      name_ta: "மெனியர்ஸ் காது சமநிலை & தலைசுற்றல்",
      key_symptoms: "Spinning vertigo attacks, tinnitus ringing, progressive sensorineural hearing loss",
      astrological_indicators: "Mercury afflicted in 6th receiving harsh aspect of Saturn; 3rd house afflicted",
    },
    {
      name_en: "Crohn's Disease & Inflammatory Bowel Disorder",
      name_ta: "கிரோன் குடல் அழற்சி நோய்",
      key_symptoms: "Transmural intestinal ulceration, severe abdominal cramping, weight loss, fever",
      astrological_indicators: "Mars and Ketu conjoined in 6th or 8th house, vitiating the pitta-rakta gut lining",
    },
    {
      name_en: "Fibromyalgia & Somatoform Myalgia",
      name_ta: "ஃபைப்ரோமயால்ஜியா நாள்பட்ட தசை வலி",
      key_symptoms: "Widespread musculo-skeletal aching, sleep fragmentation, morning stiffness, cognitive fog",
      astrological_indicators: "Saturn and Moon mutual aspect from 6th to 12th; Vata vitiation in Mamsa dhatu",
    },
    {
      name_en: "Ankylosing Spondylitis & Spinal Rigidity",
      name_ta: "முதுகெலும்பு விறைப்பு அழற்சி",
      key_symptoms: "Sacroiliac joint fusion, bamboo spine curvature, thoracic stiffness, nocturnal pain",
      astrological_indicators: "Saturn in Leo or with Sun; 8th lord afflicted by Mars in bone-ruling Leo/Capricorn",
    },
    {
      name_en: "Multiple Sclerosis & Neural Demyelination",
      name_ta: "மல்டிபிள் ஸ்களீரோசிஸ் நரம்பு உறை பாதிப்பு",
      key_symptoms: "Optic neuritis, muscle spasticity, loss of motor coordination, neuropathic burning",
      astrological_indicators: "Mercury, Moon, and Saturn combust or conjoined with Rahu in Airy signs",
    },
    {
      name_en: "Chronic Renal Failure & Uremic Toxin Retention",
      name_ta: "நாள்பட்ட சிறுநீரக செயலிழப்பு",
      key_symptoms: "Elevated blood urea & creatinine, fluid retention in ankles, hypertension, anemia",
      astrological_indicators: "7th house afflicted by 6th lord; Venus afflicted in Scorpio/Virgo by Saturn/Rahu",
    },
    {
      name_en: "Bronchiectasis & Chronic Cavitary Lung Strain",
      name_ta: "நுரையீரல் மூச்சுக்குழாய் அழற்சி",
      key_symptoms: "Persistent purulent sputum, recurrent hemoptysis, clubbing of fingers, dyspnea",
      astrological_indicators: "Sun-Saturn or Rahu-Moon occupying Cancer (4th sign) under malefic aspect",
    },
  ];

  // 8. Natural Remedies Guide
  const naturalRemedies: NaturalRemediesGuide = {
    planetary_colour_therapy: {
      Sun: "Orange / Deep Amber rays (stimulates cardiac heat and bone vitality)",
      Moon: "Soft White / Silvery Blue rays (calms nervous irritability and balances bodily fluids)",
      Mars: "Ruby Red rays (stimulates sluggish circulation and hemoglobin formation)",
      Mercury: "Emerald Green rays (regulates nervous transmission and dermal tissue renewal)",
      Jupiter: "Golden Yellow rays (nourishes liver metabolism, adipose balance, and mental serenity)",
      Venus: "Diamond White / Iridescent Rose rays (tonifies reproductive fluids and mucosal immunity)",
      Saturn: "Violet / Indigo rays (sedates acute inflammation and calms excessive joint tremors)",
    },
    metal_charged_waters: {
      "Copper Water (Tamra Jal)": "Water kept overnight in clean copper vessel. Purifies digestive tract, stimulates Pitta-Agni, and curbs Kapha sluggishness.",
      "Silver Water (Roupya Jal)": "Water boiled with pure silver coin. Cools excessive gastric fire, soothes burning micturition, and pacifies mental agitation.",
      "Gold Water (Suvarna Jal)": "Water boiled with pure 24-carat gold coin. Enhances Ojas (vital immunity), memory retention, and cardiac muscular tone.",
      "Iron Water (Lauha Jal)": "Water charged with non-rusted iron utensil. Stimulates bone marrow, combatting nutritional anemia and pale extremities.",
    },
    fasting_and_diet: [
      "Fasting once weekly on day of afflicted benefic or running Dasha lord",
      "Tuesday / Saturday light diet with unpolished millets and rock salt (Saindhava)",
      "Strict reduction of table salt (sodium) to minimize capillary water retention",
      "Abstaining from cold refrigerated water; consuming only lukewarm boiled water",
      "Early dinner before sunset to facilitate unobstructed gastric digestion before sleep",
    ],
    vega_dharana_urges: [
      { urge_en: "Suppression of Flatus (Apana Vata)", urge_ta: "மலக்காற்று அடக்குதல்", suppression_hazard_en: "Causes abdominal distension, severe colic pain, constipation, and retrosternal distress.", suppression_hazard_ta: "வயிற்று உப்புசம், வலி, மலச்சிக்கல் மற்றும் நெஞ்சுப் பகுதி அழுத்தத்தை உண்டாக்கும்." },
      { urge_en: "Suppression of Feces (Purisha)", urge_ta: "மலம் அடக்குதல்", suppression_hazard_en: "Causes fecal impaction, headache, calf muscle cramps, and autointoxication of tissues.", suppression_hazard_ta: "தலைவலி, கால் தசை பிடிப்பு, குடல் நச்சுத்தன்மை மற்றும் கடுமையான மலச்சிக்கலை ஏற்படுத்தும்." },
      { urge_en: "Suppression of Urine (Mutra)", urge_ta: "சிறுநீர் அடக்குதல்", suppression_hazard_en: "Causes dysuria, renal gravel, urinary tract infections, and pelvic tension.", suppression_hazard_ta: "சிறுநீரகக் கற்கள், சிறுநீர்ப் பாதை அழற்சி மற்றும் அடிவயிற்று வலியை உண்டாக்கும்." },
      { urge_en: "Suppression of Eructation / Belching (Udgara)", urge_ta: "ஏப்பம் அடக்குதல்", suppression_hazard_en: "Causes anorexia, chest tightness, palpitations, and abdominal bloating.", suppression_hazard_ta: "பசியின்மை, மார்புப் பிடிப்பு, நெஞ்சுப் படபடப்பு மற்றும் வயிற்றுப் பொருமலை உருவாக்கும்." },
      { urge_en: "Suppression of Sneezing (Kshavathu)", urge_ta: "தும்மல் அடக்குதல்", suppression_hazard_en: "Causes headache, facial palsy twitches, sensory dullness, and neck stiffness.", suppression_hazard_ta: "தலைவலி, கழுத்து விறைப்பு மற்றும் முக நரம்புகளில் அழுத்தத்தை ஏற்படுத்தும்." },
      { urge_en: "Suppression of Thirst (Trishna)", urge_ta: "தாகம் அடக்குதல்", suppression_hazard_en: "Causes dry mouth, cognitive dullness, hearing impairment, cardiac exhaustion, and vertigo.", suppression_hazard_ta: "தொண்டை வறட்சி, தலைசுற்றல், இதய பலவீனம் மற்றும் உடல் சோர்வை உண்டாக்கும்." },
      { urge_en: "Suppression of Hunger (Kshut)", urge_ta: "பசி அடக்குதல்", suppression_hazard_en: "Causes muscular emaciation, gastric ulceration, loss of vitality, and vertigo.", suppression_hazard_ta: "உடல் இளைத்தல், இரைப்பை புண், தலைசுற்றல் மற்றும் ஊட்டச்சத்து குறைபாட்டைத் தரும்." },
      { urge_en: "Suppression of Sleep (Nidra)", urge_ta: "தூக்கம் அடக்குதல்", suppression_hazard_en: "Causes delusions, ocular fatigue, cognitive disorientation, and somatic heaviness.", suppression_hazard_ta: "கண் சோர்வு, சிந்தனைக் குழப்பம், உடல் கனத்தல் மற்றும் மன அழுத்தத்தை உண்டாக்கும்." },
      { urge_en: "Suppression of Cough (Kasa)", urge_ta: "இருமல் அடக்குதல்", suppression_hazard_en: "Causes worsening bronchial spasm, thoracic pressure, and cardiac strain.", suppression_hazard_ta: "மூச்சுக்குழாய் அழற்சி, மார்பு நெரிசல் மற்றும் இருதயப் பகுதியில் அழுத்தத்தை உருவாக்கும்." },
      { urge_en: "Suppression of Panting / Heavy Breathing (Shwasa)", urge_ta: "மூச்சு வாங்குதல் அடக்குதல்", suppression_hazard_en: "Causes cardiac strain, abdominal tumours (Gulma), and cognitive syncope.", suppression_hazard_ta: "இருதய உழைப்பு, மயக்க உணர்வு மற்றும் வயிற்றுப் பிடிப்புகளை உண்டாக்கும்." },
      { urge_en: "Suppression of Yawning (Jrimbha)", urge_ta: "கொட்டாவி அடக்குதல்", suppression_hazard_en: "Causes convulsions, cervical muscle contractions, and motor sluggishness.", suppression_hazard_ta: "கழுத்துத் தசை சுருக்கம், உடல் நடுக்கம் மற்றும் நரம்புத் தளர்ச்சியை ஏற்படுத்தும்." },
      { urge_en: "Suppression of Tears (Ashru)", urge_ta: "கண்ணீர் அடக்குதல்", suppression_hazard_en: "Causes chronic rhinitis, ocular glaucoma strain, cardiac constriction, and mental melancholy.", suppression_hazard_ta: "கண் பார்வை பாதிப்பு, இதய அழுத்தம், தலைவலி மற்றும் தீவிர மன அழுத்தத்தை உண்டாக்கும்." },
      { urge_en: "Suppression of Semen (Shukra)", urge_ta: "விந்து அடக்குதல்", suppression_hazard_en: "Causes testicular inflammation, prostate congestion, dysuria, and pelvic stagnation.", suppression_hazard_ta: "விந்துப் பை வீக்கம், புரோஸ்டேட் பாதிப்பு மற்றும் சிறுநீரகத் தடையை உருவாக்கும்." },
    ],
  };

  // 9. Practical Clinical Cases
  const caseStudies: ClinicalCaseStudy[] = [
    {
      id: "chatterjee_case_1_diabetes",
      title_en: "Practical Case 1: Diabetic Patient with Severe Visual & Neural Strain",
      title_ta: "நடைமுறை ஆய்வு 1: சர்க்கரை நோயாளி - தீவிர பார்வை & நரம்பு உபாதை",
      patient_profile: "Male born 1958, Executive Engineer, diagnosed with severe diabetes mellitus in 1994",
      disease_diagnosed: "Chronic Diabetes Mellitus with peripheral neuropathy and early diabetic retinopathy",
      astrological_indicators: [
        "Venus debilitated in Virgo (6th sign) receiving direct drishti of Saturn",
        "Jupiter in 8th house conjoined with Rahu forming Guru-Chandal dosha",
        "6th lord placed in 2nd house (food intake/sugar craving)",
      ],
      dasha_timing: "Onset triggered during Jupiter-Rahu Dasha; exacerbated in Saturn Bhukti",
      key_takeaway: "Demonstrates Dr. Chatterjee's golden finding: Venus in Virgo aspected by Saturn invariably impairs pancreatic insulin secretion.",
    },
    {
      id: "chatterjee_case_2_robust_health",
      title_en: "Practical Case 2: Prof. Galgali - Extraordinary Longevity & Disease Resistance",
      title_ta: "நடைமுறை ஆய்வு 2: பேராசிரியர் கல்கலி - அபார ஆயுள் பலம் & நோய் எதிர்ப்பு",
      patient_profile: "Celebrated Sanskrit scholar living past 88 years without hospitalization",
      disease_diagnosed: "Complete absence of chronic degenerative illnesses; natural robust vitality",
      astrological_indicators: [
        "Benefics (Jupiter & Venus) prominently placed in Kendras (1st and 4th)",
        "Malefics (Mars, Saturn) firmly entrenched in 3rd and 11th Upachaya houses",
        "Lagna lord exalted in 9th house forming Parijata Longevity Shield",
      ],
      dasha_timing: "Sustained good health across Saturn, Mercury, and Ketu major periods",
      key_takeaway: "Classic textbook confirmation: Benefics in Angles and Malefics in 3/11 grant exceptional immunity and disease-free longevity.",
    },
    {
      id: "chatterjee_case_3_deaf_mute_child",
      title_en: "Practical Case 3: Deaf and Mute Child with Afflicted 2nd & 3rd Houses",
      title_ta: "நடைமுறை ஆய்வு 3: வாய் பேசாத, காது கேளாத குழந்தை - 2 & 3-ம் பாவ பாதிப்பு",
      patient_profile: "Female child born 1989, congenital hearing and speech impediment",
      disease_diagnosed: "Congenital sensorineural deafness and muteness",
      astrological_indicators: [
        "Mercury (speech lord) combust in 6th house with Rahu",
        "2nd house (speech) occupied by retrograde Saturn",
        "3rd house (hearing/ears) aspected by Mars from 8th house",
      ],
      dasha_timing: "Born in Ketu Dasha; speech therapy during Venus-Mercury showed marginal improvement",
      key_takeaway: "Affliction to Mercury, 2nd house, and 3rd house without benefic aspect produces irrevocable auditory-speech impediments.",
    },
    {
      id: "chatterjee_case_4_diabetic_lady",
      title_en: "Practical Case 4: Lifelong Diabetic Lady Maintaining Normal Kidney Functions",
      title_ta: "நடைமுறை ஆய்வு 4: நீண்டகால சர்க்கரை நோய் இருந்தும் சிறுநீரகம் பாதுகாக்கப்பட்ட பெண்மணி",
      patient_profile: "Female born 1944, diagnosed with diabetes at age 35, survived to age 78",
      disease_diagnosed: "Type 2 Diabetes Mellitus successfully contained through strict natural diet",
      astrological_indicators: [
        "Venus in 6th house (diabetes marker) but aspected by exalted Jupiter from 2nd house",
        "7th and 8th houses clean of malefic influence (protecting renal filtering units)",
        "Sun strong in 10th house providing somatic vital warmth",
      ],
      dasha_timing: "Diagnosed in Mercury Dasha; sustained stable renal filtration through Venus Dasha",
      key_takeaway: "When Jupiter aspects afflicted Venus, natural dietary discipline (curd, neem, methi) neutralizes diabetic microvascular damage.",
    },
    {
      id: "chatterjee_case_5_chronic_ailments",
      title_en: "Practical Case 5: Chronic Arthritic Lady with Severe Joint Fusion",
      title_ta: "நடைமுறை ஆய்வு 5: தீவிர மூட்டு அழற்சி மற்றும் விறைப்பு கொண்ட பெண்மணி",
      patient_profile: "Female born 1962, severe rheumatoid joint deformities since age 40",
      disease_diagnosed: "Rheumatoid Arthritis (Vata-Rakta) with knee and finger swelling",
      astrological_indicators: [
        "Saturn (Vata) in Lagna receiving direct 7th aspect from debilitated Mars (Rakta)",
        "Moon in 8th house in Scorpio (debilitated) causing chronic lymphatic fluid stagnation",
        "6th lord in 10th aspecting 4th house joints",
      ],
      dasha_timing: "Severe immobilization commenced during Mars Dasha - Saturn Bhukti",
      key_takeaway: "Mutual aspect between Saturn (wind/bones) and Mars (blood/heat) in dusthana angles produces intractable Vata-Rakta.",
    },
    {
      id: "chatterjee_case_6_khorana_nobel",
      title_en: "Practical Case 6: Dr. Hargobind Khorana - Nobel Laureate Geneticist Vitality",
      title_ta: "நடைமுறை ஆய்வு 6: நோபல் பரிசு பெற்ற விஞ்ஞானி ஹர்கோவிந்த் கொரானாவின் ஜாதகம்",
      patient_profile: "Nobel Laureate in Physiology/Medicine (1922-2011), lived to age 89 with razor-sharp intellect",
      disease_diagnosed: "Superlative mental stamina, sustained longevity, peaceful senescence",
      astrological_indicators: [
        "Mercury exalted in Virgo forming Bhadra Mahapurusha Yoga in Kendra",
        "Jupiter in 1st house granting divine protection (Deva Guru Shield)",
        "8th house occupied by Sun and Rahu, transmuted into deep biological research focus",
      ],
      dasha_timing: "Nobel prize in Mercury Dasha; sustained research activity into Saturn and Mercury periods",
      key_takeaway: "Exalted Mercury and Kendra Jupiter protect the brain and vital organs from premature senescence, transmuting 8th house Rahu into revolutionary scientific insight.",
    },
  ];

  return {
    book_title: "Advance Medical Astrology",
    book_title_ta: "அட்வான்ஸ் மருத்துவ ஜோதிடம்",
    author: "Dr. S. S. Chatterjee, Ph.D. (BHU)",
    publisher: "Banaras Hindu University Research Series",
    salient_features: [
      "Scientific & Electro-chemical correlation with classical Vedic and Ayurvedic medical astrology principles",
      "Signature mathematical Death Point formula: (Ascendant + Sun + Moon + Jupiter) % 360 with transit Saturn drishti triggers",
      "Sapta Dhatus (7 bodily tissues) ruled by 7 physical planets",
      "Detailed endocrine gland planetary governance matrix",
      "Anatomical Tridosha (Vata, Pitta, Kapha) diagnosis and site mapping",
      "Exhaustive Diabetes Mellitus (Madhumeha) biochemical analysis, symptoms, and empirical natural dietetic remedies",
      "10 Modern complex 21st-century illnesses (Hepatitis C, Lupus, Celiac, Vertigo, etc.) with planetary markers",
      "Natural therapies: Planetary colour therapy, metal-charged waters (Copper, Silver, Gold, Iron), and Vega Dharana natural urges",
      "Comprehensive clinical research backed by practical horoscopes from author's research diary",
    ],
    death_point: deathPoint,
    parijata_longevity_eval: parijataLongevity,
    sapta_dhatus: saptaDhatus,
    endocrine_glands: endocrineGlands,
    tridosha_sites: tridoshaSites,
    diabetes_assessment: diabetesAssessment,
    modern_diseases: modernDiseases,
    natural_remedies: naturalRemedies,
    golden_rules: [
      {
        id: "chatterjee_death_point_saturn",
        name: "Dr. Chatterjee's Death Point Triggered by Saturn Aspect",
        name_tamil: "மிருத்யு புள்ளி மீது கோச்சார சனி பார்வை (ஆயுள் விழிப்புணர்வு)",
        source: "Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse: "Chapter 1, Death Point Principles",
        category: "Death Point Trigger",
        system: "vedic",
        required_placements: "Transit Saturn casting direct drishti (conjunction, 3rd, 7th, 10th) upon Death Point",
        mandatory_conditions: ["Transit Saturn aspects native Death Point"],
        traditional_interpretation: "When transit Saturn casts aspect on the mathematically derived Death Point ((Asc + Sun + Moon + Jup) % 360), constitutional vitality requires heightened medical protection and avoidance of physical overexertion.",
        interpretation_tamil: "லக்னம், சூரியன், சந்திரன் மற்றும் குருவின் கூட்டு ஸ்புடத்தால் பெறப்படும் மிருத்யு புள்ளியை கோச்சார சனி பார்க்கும் போது, உடல் ஆரோக்கியத்தில் தீவிர விழிப்புணர்வும் மருத்துவப் பாதுகாப்பும் தேவைப்படுகிறது.",
        anatomical_system: "Somatic Vitality & Longevity Core",
        is_active: satAspectActive,
        status: satAspectActive ? "Qualifying" : "Not Qualifying",
        triggered_positions: satAspectActive ? [`Transit Saturn in Sign ${satCurrSign} aspects Death Point at ${degInSign.toFixed(1)}° ${dpSignEn}`] : [],
        planets_involved: ["Saturn"],
        relevant_houses: [dpSignIdx],
        conditions: [{ condition: "Transit Saturn aspects Death Point", passed: satAspectActive, detail: deathPoint.aspect_details_en }],
      },
      {
        id: "chatterjee_parijata_longevity",
        name: "Parijata Yoga & Kendra-Benefic Longevity Shield",
        name_tamil: "பாரிஜாத யோகம் & கேந்திர சுப ஆயுள் கவசம்",
        source: "Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse: "Preface, Longevity Axioms",
        category: "Classical Longevity Shield",
        system: "vedic",
        required_placements: "Natural benefics in Kendras/Trikonas with malefics in 3rd or 11th house",
        mandatory_conditions: ["Benefics in Angles/Trines", "Malefics in Upachaya"],
        traditional_interpretation: "Benefics in angles and trines act as impenetrable pillars shielding against virulent pathogens, while strong malefics in 3 or 11 neutralize disease-causing agents, conferring extended longevity.",
        interpretation_tamil: "கேந்திர மற்றும் திரிகோணங்களில் சுபக் கிரகங்களும், 3 அல்லது 11-ல் பாவர்களும் அமையப்பெற்ற ஜாதகருக்கு இயல்பான நோய் எதிர்ப்பு சக்தியும், நீண்ட ஆயுளும் அமையும்.",
        anatomical_system: "Immune Architecture & Lifespan",
        is_active: hasShield,
        status: hasShield ? "Qualifying" : "Not Qualifying",
        triggered_positions: hasShield ? [parijataLongevity] : [],
        planets_involved: [...kendraBenefics, ...maleficsIn3or11],
        relevant_houses: [1, 4, 7, 10, 3, 11],
        conditions: [{ condition: "Kendra/Trine benefics with Upachaya malefics", passed: hasShield, detail: parijataLongevity }],
      },
      {
        id: "chatterjee_diabetes_mellitus",
        name: "Diabetes Mellitus (Madhumeha) Pancreatic-Glycemic Imbalance",
        name_tamil: "மதுமேகம் (சர்க்கரை நோய்) - கணைய இன்சுலின் சமநிலையின்மை",
        source: "Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse: "Chapter 4, Madhumeha Formulary",
        category: "Endocrine & Metabolic",
        system: "vedic",
        required_placements: "Venus in Dusthana (6, 8, 12) or Virgo, Jupiter debilitated or 6th/Virgo afflicted",
        mandatory_conditions: ["Affliction to Venus, Jupiter, or 6th house"],
        traditional_interpretation: "Venus controls sweetness and insulin reception; Jupiter governs glycogen metabolism; Virgo rules abdominal viscera. Afflictions here impair pancreatic beta-cell function, causing sudden fatigue, excessive thirst, and fluctuating blood sugar.",
        interpretation_tamil: "சுக்கிரன் இனிப்பையும், குரு வளர்சிதை மாற்றத்தையும், கன்னி ராசி வயிற்றுப் பகுதியையும் ஆளுகின்றன. இவற்றில் ஏற்படும் பாதிப்பு கணைய இன்சுலின் சுரப்பைக் குறைத்து சர்க்கரை நோயை உருவாக்கும்.",
        anatomical_system: "Endocrine Pancreas & Glycemic Regulation",
        is_active: afflictionScore >= 2,
        status: afflictionScore >= 2 ? "Qualifying" : "Not Qualifying",
        triggered_positions: afflictionScore >= 2 ? [`Affliction score ${afflictionScore}/5: Venus in House ${venH}, Jupiter in House ${jupH}`] : [],
        planets_involved: ["Venus", "Jupiter"],
        relevant_houses: [6, 12, venH],
        conditions: [{ condition: "Metabolic marker score >= 2", passed: afflictionScore >= 2, detail: `Score: ${afflictionScore}` }],
      },
      {
        id: "chatterjee_rahu_5th_gastro",
        name: "Rahu in 5th House (Vata Abdominal Spasms & Gastroenteritis)",
        name_tamil: "5-ம் வீட்டில் ராகு (வயிற்றுப் பிடிப்பு & தீவிர குடல் அழற்சி)",
        source: "Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse: "Chapter 2, Golden Rule 84",
        category: "Gastrointestinal & Digestive",
        system: "vedic",
        required_placements: "Rahu posited in 5th House from Ascendant",
        mandatory_conditions: ["Rahu in 5th house"],
        traditional_interpretation: "5th house governs the upper stomach, gastric fire (Jatharagni), and diaphragm. Rahu generates dry, windy Vata spasms, episodic gastroenteritis, indigestion, and sudden severe colic pains.",
        interpretation_tamil: "5-ம் பாவம் வயிற்றின் மேற்பகுதி மற்றும் செரிமானத் தீயைக் குறிக்கிறது. ராகு இங்கு அமர்வதால் தீவிர வாயுப் பிடிப்பு, அஜீரணம் மற்றும் குடல் அழற்சி உருவாகும்.",
        anatomical_system: "Gastrointestinal & Peptic Axis",
        is_active: planetHouse["Rahu"] === 5,
        status: planetHouse["Rahu"] === 5 ? "Qualifying" : "Not Qualifying",
        triggered_positions: planetHouse["Rahu"] === 5 ? ["Rahu posited in 5th House"] : [],
        planets_involved: ["Rahu"],
        relevant_houses: [5],
        conditions: [{ condition: "Rahu in 5th house", passed: planetHouse["Rahu"] === 5, detail: "Rahu in House 5" }],
      },
      {
        id: "chatterjee_saturn_5th_dyspepsia",
        name: "Saturn in 5th House (Vata-Kapha Dyspepsia & Sluggish Agni)",
        name_tamil: "5-ம் வீட்டில் சனி (மந்தமான செரிமானம் & அஜீரணம்)",
        source: "Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse: "Chapter 2, Golden Rule 85",
        category: "Gastrointestinal & Digestive",
        system: "vedic",
        required_placements: "Saturn posited in 5th House from Ascendant",
        mandatory_conditions: ["Saturn in 5th house"],
        traditional_interpretation: "Saturn's cold, dry nature in the 5th house suppresses digestive enzymes (Mandagni), leading to chronic dyspepsia, gastric heaviness after minimal food, and slow nutrient absorption.",
        interpretation_tamil: "5-ம் வீட்டில் சனி அமர்வது செரிமானத் தீயை மந்தமாக்கி, குறைந்த உணவிலும் வயிறு உப்புசம், அஜீரணம் மற்றும் பலவீனத்தை உண்டாக்கும்.",
        anatomical_system: "Gastric Enzymatic Secretion",
        is_active: planetHouse["Saturn"] === 5,
        status: planetHouse["Saturn"] === 5 ? "Qualifying" : "Not Qualifying",
        triggered_positions: planetHouse["Saturn"] === 5 ? ["Saturn posited in 5th House"] : [],
        planets_involved: ["Saturn"],
        relevant_houses: [5],
        conditions: [{ condition: "Saturn in 5th house", passed: planetHouse["Saturn"] === 5, detail: "Saturn in House 5" }],
      },
      {
        id: "chatterjee_sun_rahu_4th_skin",
        name: "Sun and Rahu in 4th House (Atrophic Skin & Tissue Degeneration)",
        name_tamil: "4-ம் வீட்டில் சூரியன்-ராகு (தோல் தடிப்பு & திசு நலிவு)",
        source: "Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse: "Chapter 2, Golden Rule 102",
        category: "Dermatological & Cellular",
        system: "vedic",
        required_placements: "Sun and Rahu conjoined in 4th House",
        mandatory_conditions: ["Sun and Rahu in 4th house"],
        traditional_interpretation: "Sun represents cellular vitality and blood warmth, while Rahu causes toxic vitiation. Together in the 4th, they induce dermal pigment degeneration, skin thinning, and thoracic heat.",
        interpretation_tamil: "4-ம் பாவத்தில் சூரியனும் ராகுவும் இணைவது இரத்த நச்சுத்தன்மையை உண்டாக்கி, தோல் தடிப்பு மற்றும் திசுக்களின் பலவீனத்தை ஏற்படுத்தும்.",
        anatomical_system: "Dermis & Thoracic Cavity",
        is_active: planetHouse["Sun"] === 4 && planetHouse["Rahu"] === 4,
        status: (planetHouse["Sun"] === 4 && planetHouse["Rahu"] === 4) ? "Qualifying" : "Not Qualifying",
        triggered_positions: (planetHouse["Sun"] === 4 && planetHouse["Rahu"] === 4) ? ["Sun and Rahu conjoined in 4th House"] : [],
        planets_involved: ["Sun", "Rahu"],
        relevant_houses: [4],
        conditions: [{ condition: "Sun and Rahu in 4th house", passed: planetHouse["Sun"] === 4 && planetHouse["Rahu"] === 4, detail: "Sun-Rahu in House 4" }],
      },
      {
        id: "chatterjee_venus_saturn_8th_chronic",
        name: "Venus and Saturn in 8th House (Protracted Chronic Ailments)",
        name_tamil: "8-ம் வீட்டில் சுக்கிரன்-சனி (நீண்டகால உபாதைகள் & தாமத குணம்)",
        source: "Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse: "Chapter 2, Golden Rule 112",
        category: "Chronic & Degenerative",
        system: "vedic",
        required_placements: "Venus and Saturn conjoined in 8th House",
        mandatory_conditions: ["Venus and Saturn in 8th house"],
        traditional_interpretation: "Venus in the 8th with Saturn delays recovery from systemic disorders, inducing chronic pelvic or renal sluggishness, expensive therapies, and prolonged convalescence.",
        interpretation_tamil: "8-ம் பாவத்தில் சுக்கிரனும் சனியும் இணைவது நோயிலிருந்து மீள்வதை தாமதப்படுத்தி, நீண்டகால மருத்துவச் சிகிச்சைகளைத் தரும்.",
        anatomical_system: "Pelvic Viscera & Convalescence",
        is_active: planetHouse["Venus"] === 8 && planetHouse["Saturn"] === 8,
        status: (planetHouse["Venus"] === 8 && planetHouse["Saturn"] === 8) ? "Qualifying" : "Not Qualifying",
        triggered_positions: (planetHouse["Venus"] === 8 && planetHouse["Saturn"] === 8) ? ["Venus and Saturn conjoined in 8th House"] : [],
        planets_involved: ["Venus", "Saturn"],
        relevant_houses: [8],
        conditions: [{ condition: "Venus and Saturn in 8th house", passed: planetHouse["Venus"] === 8 && planetHouse["Saturn"] === 8, detail: "Venus-Saturn in House 8" }],
      },
      {
        id: "chatterjee_mars_venus_8th_urogenital",
        name: "Mars and Venus in 8th House (Urogenital & Reproductive Vulnerability)",
        name_tamil: "8-ம் வீட்டில் செவ்வாய்-சுக்கிரன் (சிறுநீரக & இனப்பெருக்க வெப்பம்)",
        source: "Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse: "Chapter 2, Golden Rule 113",
        category: "Urogenital & Reproductive",
        system: "vedic",
        required_placements: "Mars and Venus conjoined in 8th House",
        mandatory_conditions: ["Mars and Venus in 8th house"],
        traditional_interpretation: "Mars brings acute inflammatory Pitta heat into Venus's fluid-ruled domain within the 8th pelvic house, producing recurrent burning micturition, cystitis, and reproductive strain.",
        interpretation_tamil: "8-ம் பாவத்தில் செவ்வாயும் சுக்கிரனும் இணைவது சிறுநீர்ப் பாதை எரிச்சல், தொற்று மற்றும் இனப்பெருக்க உறுப்புகளில் அதிக வெப்பத்தை உண்டாக்கும்.",
        anatomical_system: "Urogenital Tract & Pelvic Vascularity",
        is_active: planetHouse["Mars"] === 8 && planetHouse["Venus"] === 8,
        status: (planetHouse["Mars"] === 8 && planetHouse["Venus"] === 8) ? "Qualifying" : "Not Qualifying",
        triggered_positions: (planetHouse["Mars"] === 8 && planetHouse["Venus"] === 8) ? ["Mars and Venus conjoined in 8th House"] : [],
        planets_involved: ["Mars", "Venus"],
        relevant_houses: [8],
        conditions: [{ condition: "Mars and Venus in 8th house", passed: planetHouse["Mars"] === 8 && planetHouse["Venus"] === 8, detail: "Mars-Venus in House 8" }],
      },
      {
        id: "chatterjee_mars_saturn_8th_digestive",
        name: "Mars and Saturn in 8th House (Digestive Turmoil, Waist Adiposity & Fracture Risk)",
        name_tamil: "8-ம் வீட்டில் செவ்வாய்-சனி (இடுப்பு வலி, செரிமானக் குழப்பம் & எலும்பு முறிவு)",
        source: "Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse: "Chapter 2, Golden Rule 114",
        category: "Musculoskeletal & Trauma",
        system: "vedic",
        required_placements: "Mars and Saturn conjoined in 8th House",
        mandatory_conditions: ["Mars and Saturn in 8th house"],
        traditional_interpretation: "The friction between fiery Mars and frosty Saturn in the 8th house creates sharp lower back spasms, pelvic fractures, and severe digestive colic.",
        interpretation_tamil: "8-ம் வீட்டில் செவ்வாயும் சனியும் இணைவது இடுப்புப் பகுதி தசைப்பிடிப்பு, எலும்பு முறிவு அபாயம் மற்றும் செரிமானக் கோளாறுகளை உண்டாக்கும்.",
        anatomical_system: "Pelvis, Sacrum & Lower Vertebrae",
        is_active: planetHouse["Mars"] === 8 && planetHouse["Saturn"] === 8,
        status: (planetHouse["Mars"] === 8 && planetHouse["Saturn"] === 8) ? "Qualifying" : "Not Qualifying",
        triggered_positions: (planetHouse["Mars"] === 8 && planetHouse["Saturn"] === 8) ? ["Mars and Saturn conjoined in 8th House"] : [],
        planets_involved: ["Mars", "Saturn"],
        relevant_houses: [8],
        conditions: [{ condition: "Mars and Saturn in 8th house", passed: planetHouse["Mars"] === 8 && planetHouse["Saturn"] === 8, detail: "Mars-Saturn in House 8" }],
      },
      {
        id: "chatterjee_saturn_rahu_8th_obesity",
        name: "Saturn and Rahu in 8th House (Lower Body Adiposity & Sluggish Recuperation)",
        name_tamil: "8-ம் வீட்டில் சனி-ராகு (கீழ் உடல் பருமன் & மெதுவான குணம்)",
        source: "Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse: "Chapter 2, Golden Rule 115",
        category: "Metabolic & Lymphatic",
        system: "vedic",
        required_placements: "Saturn and Rahu conjoined in 8th House",
        mandatory_conditions: ["Saturn and Rahu in 8th house"],
        traditional_interpretation: "Saturn and Rahu in the 8th obstruct lymphatic drainage in the pelvic basin, triggering excessive hip/thigh adiposity, water retention, and protracted sluggishness.",
        interpretation_tamil: "8-ம் வீட்டில் சனியும் ராகுவும் இணைவது நிணநீர் ஓட்டத்தைத் தடுத்து கீழ் உடல் பருமன், நீர் தேக்கம் மற்றும் மந்தமான உடல்நிலையைத் தரும்.",
        anatomical_system: "Lower Pelvic Drainage & Adipose Reserve",
        is_active: planetHouse["Saturn"] === 8 && planetHouse["Rahu"] === 8,
        status: (planetHouse["Saturn"] === 8 && planetHouse["Rahu"] === 8) ? "Qualifying" : "Not Qualifying",
        triggered_positions: (planetHouse["Saturn"] === 8 && planetHouse["Rahu"] === 8) ? ["Saturn and Rahu conjoined in 8th House"] : [],
        planets_involved: ["Saturn", "Rahu"],
        relevant_houses: [8],
        conditions: [{ condition: "Saturn and Rahu in 8th house", passed: planetHouse["Saturn"] === 8 && planetHouse["Rahu"] === 8, detail: "Saturn-Rahu in House 8" }],
      },
      {
        id: "chatterjee_saturn_ketu_8th_gangrene",
        name: "Saturn and Ketu in 8th House (Septic Complications & Delayed Healing)",
        name_tamil: "8-ம் வீட்டில் சனி-கேது (நச்சுத் தொற்று & தாமதமான காயம் ஆறுதல்)",
        source: "Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse: "Chapter 2, Golden Rule 116",
        category: "Cellular & Microvascular",
        system: "vedic",
        required_placements: "Saturn and Ketu conjoined in 8th House",
        mandatory_conditions: ["Saturn and Ketu in 8th house"],
        traditional_interpretation: "Saturn restricts vascular perfusion while Ketu invites hidden microbial proliferation, producing slow-healing wounds, carbuncles, and microvascular necrosis.",
        interpretation_tamil: "8-ம் வீட்டில் சனியும் கேதுவும் இணைவது இரத்த ஓட்டக் குறைவால் புண்கள் மற்றும் காயங்கள் தாமதமாக ஆற வழிவகுக்கும்.",
        anatomical_system: "Microvascular Perfusion & Deep Healing",
        is_active: planetHouse["Saturn"] === 8 && planetHouse["Ketu"] === 8,
        status: (planetHouse["Saturn"] === 8 && planetHouse["Ketu"] === 8) ? "Qualifying" : "Not Qualifying",
        triggered_positions: (planetHouse["Saturn"] === 8 && planetHouse["Ketu"] === 8) ? ["Saturn and Ketu conjoined in 8th House"] : [],
        planets_involved: ["Saturn", "Ketu"],
        relevant_houses: [8],
        conditions: [{ condition: "Saturn and Ketu in 8th house", passed: planetHouse["Saturn"] === 8 && planetHouse["Ketu"] === 8, detail: "Saturn-Ketu in House 8" }],
      },
      {
        id: "chatterjee_sun_mars_8th_pitta_burn",
        name: "Sun and Mars in 8th House (Acute Pitta Flare-Ups & Thermal Hazards)",
        name_tamil: "8-ம் வீட்டில் சூரியன்-செவ்வாய் (அதிக பித்த உஷ்ணம் & அழற்சி)",
        source: "Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse: "Chapter 2, Golden Rule 117",
        category: "Inflammatory & Thermal",
        system: "vedic",
        required_placements: "Sun and Mars conjoined in 8th House",
        mandatory_conditions: ["Sun and Mars in 8th house"],
        traditional_interpretation: "Two fiery malefics in the pelvic 8th house overheat the circulatory and urinary passages, predisposing to sudden acute fevers, hemorrhoids, and bile reflux.",
        interpretation_tamil: "8-ம் வீட்டில் சூரியனும் செவ்வாயும் இணைவது தீவிர பித்த உஷ்ணம், மூல உபாதைகள் மற்றும் இரத்த அழுத்த உயர்வை உண்டாக்கும்.",
        anatomical_system: "Pelvic Hemodynamics & Thermal Core",
        is_active: planetHouse["Sun"] === 8 && planetHouse["Mars"] === 8,
        status: (planetHouse["Sun"] === 8 && planetHouse["Mars"] === 8) ? "Qualifying" : "Not Qualifying",
        triggered_positions: (planetHouse["Sun"] === 8 && planetHouse["Mars"] === 8) ? ["Sun and Mars conjoined in 8th House"] : [],
        planets_involved: ["Sun", "Mars"],
        relevant_houses: [8],
        conditions: [{ condition: "Sun and Mars in 8th house", passed: planetHouse["Sun"] === 8 && planetHouse["Mars"] === 8, detail: "Sun-Mars in House 8" }],
      },
      {
        id: "chatterjee_sun_mars_lagna_bp",
        name: "Sun and Mars in Lagna (Arterial Tension & Pitta Blood Pressure Surges)",
        name_tamil: "லக்னத்தில் சூரியன்-செவ்வாய் (இரத்த அழுத்த ஏற்றம் & பித்த உஷ்ணம்)",
        source: "Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse: "Chapter 2, Golden Rule 125",
        category: "Cardiovascular & Hemodynamic",
        system: "vedic",
        required_placements: "Sun and Mars conjoined in Lagna (1st House)",
        mandatory_conditions: ["Sun and Mars in Lagna"],
        traditional_interpretation: "Sun and Mars in the 1st house overheat cranial and arterial vessels, causing vascular tension, sudden temporal surges, and flushing under stress.",
        interpretation_tamil: "லக்னத்தில் சூரியன் மற்றும் செவ்வாய் இணைவு இரத்தக் குழாய்களில் அழுத்தத்தை அதிகரித்து இரத்த அழுத்தம் மற்றும் பித்த உஷ்ணத்தை உருவாக்கும்.",
        anatomical_system: "Cranial Blood Vessels & Arterial Tone",
        is_active: planetHouse["Sun"] === 1 && planetHouse["Mars"] === 1,
        status: (planetHouse["Sun"] === 1 && planetHouse["Mars"] === 1) ? "Qualifying" : "Not Qualifying",
        triggered_positions: (planetHouse["Sun"] === 1 && planetHouse["Mars"] === 1) ? ["Sun and Mars conjoined in Lagna (1st House)"] : [],
        planets_involved: ["Sun", "Mars"],
        relevant_houses: [1],
        conditions: [{ condition: "Sun and Mars in Lagna", passed: planetHouse["Sun"] === 1 && planetHouse["Mars"] === 1, detail: "Sun-Mars in Lagna" }],
      },
      {
        id: "chatterjee_saturn_rahu_2nd_constipation",
        name: "Saturn and Rahu in 2nd House (Chronic Constipation - Grandmother of Diseases)",
        name_tamil: "2-ம் வீட்டில் சனி-ராகு (நாள்பட்ட மலச்சிக்கல் & மந்தமான குடல்)",
        source: "Advance Medical Astrology (Dr. S.S. Chatterjee)",
        chapter_verse: "Chapter 2, Golden Rule 155",
        category: "Digestive & Dietetic",
        system: "vedic",
        required_placements: "Saturn and Rahu conjoined in 2nd House",
        mandatory_conditions: ["Saturn and Rahu in 2nd house"],
        traditional_interpretation: "Dr. Chatterjee calls constipation the 'grandmother of all diseases'. Saturn and Rahu together in the 2nd house cause erratic eating habits, dry intake, and chronic colon sluggishness.",
        interpretation_tamil: "2-ம் வீட்டில் சனியும் ராகுவும் இணைவது உணவுக் கட்டுப்பாடின்மை, வறண்ட உணவுகள் மற்றும் குடல் இயக்க மந்தத்தால் கடுமையான மலச்சிக்கலைத் தரும்.",
        anatomical_system: "Oral Intake, Throat & Colon Motility",
        is_active: planetHouse["Saturn"] === 2 && planetHouse["Rahu"] === 2,
        status: (planetHouse["Saturn"] === 2 && planetHouse["Rahu"] === 2) ? "Qualifying" : "Not Qualifying",
        triggered_positions: (planetHouse["Saturn"] === 2 && planetHouse["Rahu"] === 2) ? ["Saturn and Rahu conjoined in 2nd House"] : [],
        planets_involved: ["Saturn", "Rahu"],
        relevant_houses: [2],
        conditions: [{ condition: "Saturn and Rahu in 2nd house", passed: planetHouse["Saturn"] === 2 && planetHouse["Rahu"] === 2, detail: "Saturn-Rahu in House 2" }],
      },
    ],
    case_studies: caseStudies,
  };
}



// ===========================================================================
// Max Heindel & Augusta Foss Heindel "Astro-Diagnosis: A Guide to Healing" Module
// ===========================================================================

export const HEINDEL_METADATA = {
  "book_title": "Astro-Diagnosis: A Guide to Healing & The Message of the Stars",
  "book_title_ta": "ஜோதிட நோய்நிர்ணயம்: குணமளிக்கும் வழிகாட்டி மற்றும் விண்மீன்களின் செய்தி",
  "authors": "Max Heindel & Augusta Foss Heindel (The Rosicrucian Fellowship, Oceanside, CA)",
  "historical_foundation": "Marcus Manilius (1st Century AD Astronomica) & Rosicrucian Esoteric Astro-Diagnosis",
  "core_philosophy_en": "Disease is fundamentally a lack of harmony between the spirit and the personality — a conflict between the lower and the higher man. In ninety-five cases out of every hundred, disease originates in wrong methods of living and ignorant violations of the laws of nature. The true healer never treats merely the physical symptom, but seeks the first cause in the horoscope. By removing the primary cause and guiding the patient into harmony with nature's cosmic laws, the cure follows as an inevitable consequence. The stars impel but do not compel; by will-power, self-control, and spiritual enlightenment, man may rule his stars.",
  "core_philosophy_ta": "நோய் என்பது ஆன்மாவிற்கும் உடலின் ஆளுமைக்கும் இடையே ஏற்படும் இசைவின்மையே ஆகும் (உயர் ஆன்மாவிற்கும் கீழ்நிலை மனதிற்குமான முரண்பாடு). நூற்றுக்கு தொண்ணூற்றைந்து சதவீத நோய்கள் தவறான வாழ்க்கை முறையினாலும் இயற்கையின் விதிகளை மீறுவதாலுமே ஏற்படுகின்றன. உண்மையான ஜோதிட மருத்துவர் வெறும் புற அறிகுறிகளை மட்டும் கவனிக்காமல், ஜாதகத்தின் வழியே நோய்க்கான மூலக் காரணத்தைக் கண்டறிகிறார். மூலக் காரணத்தை அகற்றி, இயற்கையின் நெறிமுறைகளுக்கு ஏற்ப வாழ வழிகாட்டுவதன் மூலம் நலமுறுதல் இயல்பாக நிகழ்கிறது. விண்மீன்கள் உந்துகின்றன, கட்டாயப்படுத்துவதில்லை; மன உறுதியாலும் ஆன்ம விழிப்பினாலும் மனிதன் தன் விதியை வெல்ல முடியும்.",
  "healer_injunctions": [
    {
      "id": "1",
      "rule_en": "NEVER, NEVER predict the time of death to your patient. While there is life, there is HOPE. Predicting death makes you an executioner.",
      "rule_ta": "நோயாளியிடம் மரண காலத்தை ஒருபோதும் கணிக்கவோ கூறவோ கூடாது. உயிர் இருக்கும் வரை நம்பிக்கை உண்டு. மரணத்தை அறிவிப்பது நோயாளியின் நம்பிக்கையைக் கொல்வதாகும்."
    },
    {
      "id": "2",
      "rule_en": "The LAW does not permit a layman to diagnose disease for others; only licensed physicians may do this. Keep astrological indications for holistic guidance.",
      "rule_ta": "சட்டப்படி மருத்துவர் மட்டுமே நோயை உறுதிப்படுத்த முடியும். ஜோதிடர் ஆன்மவியல் காரணங்களையும் முழுமையான நல்வாழ்வு ஆலோசனைகளையும் மட்டுமே பயன்படுத்த வேண்டும்."
    },
    {
      "id": "3",
      "rule_en": "The wise healer will NEVER discuss disease with his patient nor pronounce scary medical names. Keep esoteric knowledge for your own guidance in healing.",
      "rule_ta": "புத்திசாலித்தனமான குணப்படுத்துபவர் நோயாளியிடம் நோயைப் பற்றியோ அதன் தீவிர பெயர்களையோ விவாதிக்க மாட்டார்; ஜோதிட அறிவை நோயாளிக்கு தைரியம் அளிக்க மட்டுமே பயன்படுத்த வேண்டும்."
    },
    {
      "id": "4",
      "rule_en": "At all times keep the patient's mind away from thoughts of illness. Laugh and joke with him; cheerfulness is half the cure.",
      "rule_ta": "எப்போதும் நோயாளியின் மனதை நோயின் நினைவிலிருந்து விலக்கி வையுங்கள். மகிழ்ச்சியாகவும் புன்னகையுடனும் உரையாடுங்கள்; மனமகிழ்ச்சியே நோயைக் குணப்படுத்தும் பாதி மருந்தாகும்."
    },
    {
      "id": "5",
      "rule_en": "Refrain from asking 'How do you feel?'. This draws consciousness back to the physical affliction. Greet with: 'What a beautiful day! I am glad to see you.'",
      "rule_ta": "'உடல்நிலை எப்படி இருக்கிறது?' என்று கேட்க வேண்டாம். அது உடலின் வலியை மீண்டும் நினைவூட்டும். 'இன்று இனிய நாள்! உங்களைக் காண்பதில் மகிழ்ச்சி' என உற்சாகமாக வாழ்த்துங்கள்."
    },
    {
      "id": "6",
      "rule_en": "Request the patient to discontinue morbidly studying their own horoscope while under care, as adverse suggestions in the mind severely hinder recovery.",
      "rule_ta": "சிகிச்சையில் இருக்கும்போது நோயாளி தனது சொந்த ஜாதகத்தை பயத்துடன் ஆராய்வதைத் தவிர்க்கச் சொல்லுங்கள்; எதிர்மறை அச்சங்கள் குணமாவதைத் தடுக்கும்."
    },
    {
      "id": "7",
      "rule_en": "Magnetic polarity principle: An ill patient expresses the negative receptive pole. The healer must actively radiate the opposite positive pole of vitality and cheerfulness.",
      "rule_ta": "காந்த துருவ விதி: நோயுற்றவர் எதிர்மறை (நெகட்டிவ்) ஏற்பு நிலையில் உள்ளார். குணப்படுத்துபவர் நேர்மறை (பாசிட்டிவ்) பிராண ஆற்றலையும் நம்பிக்கையையும் வீச வேண்டும்."
    },
    {
      "id": "8",
      "rule_en": "When a man is ill, his vital ethers turn inward, leaving him hypersensitive to negative thoughts. The healer must live a life of pristine moral purity to transmit wholesome vibrations.",
      "rule_ta": "நோயுற்றபோது பிராண உடல் சுருங்கி உள்நோக்கும். அப்போது தீய அதிர்வுகள் எளிதில் தாக்கும். எனவே குணப்படுத்துபவர் மிகத் தூய்மையான நெறிசார்ந்த வாழ்க்கை வாழ வேண்டும்."
    },
    {
      "id": "9",
      "rule_en": "If the healer's Saturn falls upon the Ascendant or 6th house of the patient, the healer will have little success in helping that particular individual.",
      "rule_ta": "குணப்படுத்துபவரின் சனி கிரகம் நோயாளியின் லக்னத்திலோ அல்லது 6-ம் வீட்டிலோ அமைந்தால், அவரால் அந்த நோயாளிக்கு பயனுள்ள உதவி செய்வது கடினம்."
    },
    {
      "id": "10",
      "rule_en": "Healers with Sun in Scorpio or Scorpio rising possess natural healing magnetism and excel in restorative arts and surgery.",
      "rule_ta": "விருச்சிகத்தில் சூரியன் அல்லது விருச்சிக லக்னம் கொண்டவர்கள் இயல்பாகவே சிறந்த பிராண குணப்படுத்தும் ஆற்றலும் அறுவை சிகிச்சைத் திறனும் கொண்டவர்கள்."
    },
    {
      "id": "11",
      "rule_en": "The Sun in fiery signs (Aries, Leo, Sagittarius) grants intense healing vital force and restorative power over the diseases of those signs.",
      "rule_ta": "சூரியன் நெருப்பு ராசிகளில் (மேஷம், சிம்மம், தனுசு) அமர்ந்தால் மிகுந்த பிராண குணப்படுத்தும் சக்தியையும் நோய்களை வெல்லும் ஆற்றலையும் தருகிறது."
    },
    {
      "id": "12",
      "rule_en": "People born with Common signs on angles or Sun in common signs make the best nurses; their gentle aura brings a soothing, quieting influence to the sickroom.",
      "rule_ta": "உபய ராசிகள் (மிதுனம், கன்னி, தனுசு, மீனம்) கேந்திரங்களில் அமைந்தவர்கள் சிறந்த செவிலியர்களாக திகழ்கிறார்கள்; நோயாளியின் அறையை சாந்தப்படுத்தும் ஆற்றல் இவர்களிடம் உண்டு."
    },
    {
      "id": "13",
      "rule_en": "When Saturn is the afflicter, the skin is dry and vital circulation sluggish. Rub the skin briskly with rough bath gloves to stimulate peripheral circulation.",
      "rule_ta": "சனி பாதகமாக இருக்கும்போது தோல் வறண்டு இரத்த ஓட்டம் மந்தமாகும். சொரசொரப்பான குளியல் துணியால் உடலைத் தேய்த்து புற இரத்த ஓட்டத்தைத் தூண்ட வேண்டும்."
    },
    {
      "id": "14",
      "rule_en": "People with Virgo on the Ascendant or Sun in Virgo are natural dietitians and nurses, provided they guard against absorbing the patient's symptoms.",
      "rule_ta": "கன்னி லக்னம் அல்லது கன்னியில் சூரியன் உள்ளவர்கள் சிறந்த உணவு முறை நிபுணர்களாகவும் செவிலியர்களாகவும் இருப்பார்கள் (நோயாளியின் நோயை மனதளவில் உள்வாங்காமல் இருக்க வேண்டும்)."
    },
    {
      "id": "15",
      "rule_en": "To calm a patient with an afflicted or over-excited Mars, it is ideal to choose a Saturn planetary hour for therapies.",
      "rule_ta": "செவ்வாயின் கொதிப்பால் அவதிப்படும் நோயாளிக்கு அமைதி தர, சனி ஓரையில் சிகிச்சைகளைத் தொடங்குவது நற்பலன் தரும்."
    },
    {
      "id": "16",
      "rule_en": "People with Saturn in the sixth house rarely succeed as professional healers, as their own constitutional vitality is impeded.",
      "rule_ta": "6-ம் வீட்டில் சனி உள்ளவர்கள் பிறரை குணப்படுத்தும் துறையில் வெற்றி பெறுவது அரிது, ஏனெனில் அவர்களின் சொந்த பிராண சக்தி தடைகளுக்கு உள்ளாகிறது."
    },
    {
      "id": "17",
      "rule_en": "When the patient suffers from nervous disorders but Mars is unafflicted, apply manipulations or ministrations during a Sun or Mars hour.",
      "rule_ta": "நரம்பு தளர்ச்சி அல்லது மந்தநிலை உள்ளபோது செவ்வாய் கெடாமல் இருந்தால், சூரியன் அல்லது செவ்வாய் ஓரையில் சிகிச்சைகளை மேற்கொள்ள வேண்டும்."
    },
    {
      "id": "18",
      "rule_en": "When the Moon is Waxing (New to Full), stimulants produce the maximum effect while sedatives are weakest; adjust therapeutic dosages accordingly.",
      "rule_ta": "சந்திரன் வளர்பிறையாக இருக்கும்போது (அமாவாசை முதல் பௌர்ணமி வரை) ஊக்க மருந்துகள் அதிக வீரியத்துடனும், அமைதிப்படுத்தும் மருந்துகள் குறைந்த வீரியத்துடனும் செயல்படும்."
    },
    {
      "id": "19",
      "rule_en": "When the Moon is conjunct Saturn, stimulants have very little effect. When Moon is conjoined to Mars (especially in Aries), administer stimulants with extreme care.",
      "rule_ta": "சந்திரன் சனியுடன் இணையும் போது ஊக்க மருந்துகள் பலனளிப்பது குறைவு; சந்திரன் செவ்வாயுடன் இணைந்தால் (குறிப்பாக மேஷத்தில்) உஷ்ண ஊக்கிகளை மிக எச்சரிக்கையுடன் கையாள வேண்டும்."
    }
  ]
};
export const HEINDEL_SIGNS_RAW = [
  {
    "sign_index": 1,
    "sign_name_en": "Aries",
    "sign_name_ta": "மேஷம்",
    "manilius_rulership": "The Head and Cranium (Caput)",
    "heindel_anatomical_systems": [
      "Brain",
      "Cerebral hemispheres",
      "Cranium",
      "Eyes",
      "Face",
      "Upper jaw",
      "Internal carotid arteries"
    ],
    "pathological_qualities": "Hot, dry, inflammatory; excess life force, quick temper, rushing blood.",
    "physiological_afflictions": [
      "Brain fever",
      "Neuralgia",
      "Insomnia",
      "Cerebral congestion",
      "Dizziness",
      "Headaches",
      "Baldness",
      "Eye affections",
      "Toothache",
      "Gumboils"
    ],
    "temperament_and_healing_reaction": "Positive, aggressive, impulsive. Can withstand fevers 3-4 degrees higher than other signs. Responds rapidly to healing effort because the will is strong. Aries dislikes being ordered; the healer must ask diplomatically so the patient feels they are directing their own cure."
  },
  {
    "sign_index": 2,
    "sign_name_en": "Taurus",
    "sign_name_ta": "ரிஷபம்",
    "manilius_rulership": "The Neck and Throat (Cervix)",
    "heindel_anatomical_systems": [
      "Neck",
      "Throat",
      "Palate",
      "Larynx",
      "Tonsils",
      "Thyroid gland",
      "Lower jaw",
      "Occipital region",
      "Cerebellum",
      "Atlas",
      "Axis",
      "External carotid arteries",
      "Jugular veins",
      "Pharynx",
      "Cervical vertebrae"
    ],
    "pathological_qualities": "Cold, dry, earthy, stubborn; fear of sickness, luxurious appetite, fleshiness about neck.",
    "physiological_afflictions": [
      "Goiter",
      "Diphtheria",
      "Laryngitis",
      "Tonsillitis",
      "Croup",
      "Polypi",
      "Quinsy",
      "Glandular throat swelling",
      "Apoplexy"
    ],
    "temperament_and_healing_reaction": "Negative, tenacious, stubborn. Holds on to disease tenaciously due to morbid fear of sickness. Never tell a Taurean they are seriously ill, as their anxiety will precipitate a crisis. Needs gentle reassurance, outdoor activity, and moderation in rich food."
  },
  {
    "sign_index": 3,
    "sign_name_en": "Gemini",
    "sign_name_ta": "மிதுனம்",
    "manilius_rulership": "The Shoulders, Arms, and Hands (Brachia)",
    "heindel_anatomical_systems": [
      "Shoulders",
      "Arms",
      "Hands",
      "Upper ribs",
      "Lungs",
      "Thymus gland",
      "Trachea",
      "Bronchi",
      "Capillaries",
      "Breath",
      "Oxygenation of blood"
    ],
    "pathological_qualities": "Airy, nervous, dual, restless; careless habits, shallow breathing.",
    "physiological_afflictions": [
      "Bronchitis",
      "Asthma",
      "Pneumonia",
      "Consumption (Tuberculosis)",
      "Pleurisy",
      "Corrupted blood",
      "Nervous disorders",
      "Anemia"
    ],
    "temperament_and_healing_reaction": "Positive, flexible, common sign. Frequently careless of health habits. Responds quickly to treatment if given slight assistance. Greatly benefited by systematic deep breathing exercises and calisthenics."
  },
  {
    "sign_index": 4,
    "sign_name_en": "Cancer",
    "sign_name_ta": "கடகம்",
    "manilius_rulership": "The Chest, Breasts, and Stomach (Pectus)",
    "heindel_anatomical_systems": [
      "Stomach",
      "Esophagus",
      "Diaphragm",
      "Mammae (breasts)",
      "Lacteals",
      "Upper lobes of liver",
      "Thoracic duct",
      "Pancreas",
      "Serum of blood",
      "Peristalsis of stomach",
      "Chymification"
    ],
    "pathological_qualities": "Watery, negative, low vitality; emotional sensitivity, over-eating, sweet cravings.",
    "physiological_afflictions": [
      "Indigestion",
      "Dipsomania",
      "Gastric catarrh",
      "Hiccough",
      "Flatulency",
      "Dropsy",
      "Sclerosis"
    ],
    "temperament_and_healing_reaction": "Negative, timid, suspicious yet loyal once faith is established. Lowest natural vitality of the zodiac; requires praise and encouragement. Saturn in Cancer creates intense craving for sweets and pastries, robbing stomach of fluids and disturbing kidneys."
  },
  {
    "sign_index": 5,
    "sign_name_en": "Leo",
    "sign_name_ta": "சிம்மம்",
    "manilius_rulership": "The Heart and Upper Back (Humeri & Dorsum)",
    "heindel_anatomical_systems": [
      "Heart",
      "Dorsal region of spine",
      "Spinal cord",
      "Aorta",
      "Superior and inferior vena cava",
      "Etheric solar fluid via Spleen"
    ],
    "pathological_qualities": "Fiery, fixed, ardent, vital; excessive expenditure of surplus energy.",
    "physiological_afflictions": [
      "Heart disease",
      "Angina pectoris",
      "Locomotor ataxia",
      "Hyperemia",
      "Spinal disease",
      "Spinal meningitis",
      "High fevers",
      "Disturbed spleen"
    ],
    "temperament_and_healing_reaction": "Positive, noble, great vitality. Fights illness bravely without burdening others; when succumbing, is very sick but recovers quickly. Must avoid sudden violent exertion to protect cardiac tissues."
  },
  {
    "sign_index": 6,
    "sign_name_en": "Virgo",
    "sign_name_ta": "கன்னி",
    "manilius_rulership": "The Abdomen and Digestive Organs (Venter)",
    "heindel_anatomical_systems": [
      "Abdominal region",
      "Large and small intestines",
      "Lower lobes of liver",
      "Spleen",
      "Duodenum",
      "Chylification",
      "Peristalsis of bowels",
      "Sympathetic nervous system"
    ],
    "pathological_qualities": "Earthy, negative, cold, wiry; natural 6th sign of sickness, food faddism, hypochondria.",
    "physiological_afflictions": [
      "Peritonitis",
      "Malnutrition",
      "Dysentery",
      "Colic",
      "Constipation",
      "Diarrhea",
      "Cholera",
      "Typhoid",
      "Appendicitis",
      "Tapeworm",
      "Catarrh of bowels"
    ],
    "temperament_and_healing_reaction": "Negative, analytical. Virgos absorb disease vibrations like sponges. Once in the clutches of illness, they actually 'enjoy' discussing symptoms and become chronic invalids unless treated with firm conviction. Make wonderful nurses if they remain emotionally detached."
  },
  {
    "sign_index": 7,
    "sign_name_en": "Libra",
    "sign_name_ta": "துலாம்",
    "manilius_rulership": "The Kidneys, Lumbar Region, and Hips (Lumbi)",
    "heindel_anatomical_systems": [
      "Kidneys",
      "Adrenals",
      "Lumbar region of spine",
      "Skin",
      "Ureters",
      "Vasomotor system"
    ],
    "pathological_qualities": "Airy, cardinal, fluctuating moods; Sun weak (fall of Sun / exaltation of Saturn).",
    "physiological_afflictions": [
      "Bright's disease",
      "Lumbago",
      "Suppression of urine (Saturn)",
      "Excessive urine (Jupiter)",
      "Nephritis",
      "Diabetes",
      "Renal calculi (kidney stones)",
      "Uremia",
      "Eczema"
    ],
    "temperament_and_healing_reaction": "Cardinal, changeable. Swings between optimism and despair like scales. Discouragement directly poisons the kidneys. Must cultivate mental equilibrium, serene surroundings, and drink pure fluids."
  },
  {
    "sign_index": 8,
    "sign_name_en": "Scorpio",
    "sign_name_ta": "விருச்சிகம்",
    "manilius_rulership": "The Generative Organs and Genitals (Tuber)",
    "heindel_anatomical_systems": [
      "Bladder",
      "Urethra",
      "Genitals",
      "Prostate gland",
      "Descending colon",
      "Rectum",
      "Sigmoid flexure",
      "Pubic bone",
      "Nasal bones",
      "Red coloring matter in blood"
    ],
    "pathological_qualities": "Watery, fixed, martial; volcanic desires, secretiveness, unexpressed resentment.",
    "physiological_afflictions": [
      "Syphilis",
      "Hernia / rupture",
      "Gravel",
      "Fistula",
      "Piles (hemorrhoids)",
      "Diseases of uterus",
      "Urethral stricture",
      "Prostatic stricture",
      "Nasal catarrh"
    ],
    "temperament_and_healing_reaction": "Fixed, determined. Scorpio natives possess immense regenerative power and make superior surgeons and healers. Health danger stems from unrestrained passion sapping generative force. Moral cleanliness and emotional serenity are paramount."
  },
  {
    "sign_index": 9,
    "sign_name_en": "Sagittarius",
    "sign_name_ta": "தனுசு",
    "manilius_rulership": "The Hips and Thighs (Femina)",
    "heindel_anatomical_systems": [
      "Hips",
      "Thighs",
      "Femur",
      "Ileum",
      "Coccygeal vertebrae",
      "Sacral region of spine",
      "Sciatic nerves",
      "Ischium",
      "Iliac arteries"
    ],
    "pathological_qualities": "Fiery, mutable, sporting, restless; excessive physical momentum, sports accidents.",
    "physiological_afflictions": [
      "Locomotor ataxia",
      "Sciatica",
      "Lumbago",
      "Rheumatism",
      "Hip disease",
      "Fractures and broken bones of femur"
    ],
    "temperament_and_healing_reaction": "Gentle, frank, trusting; most easily cured of all patients, but highly suggestible to well-meaning friends. Protect the Sagittarian from negative visitors who suggest sickness or question the treatment."
  },
  {
    "sign_index": 10,
    "sign_name_en": "Capricorn",
    "sign_name_ta": "மகரம்",
    "manilius_rulership": "The Knees and Skeletal Articulations (Genua)",
    "heindel_anatomical_systems": [
      "Knees",
      "Skin",
      "Joints",
      "Skeletal system",
      "Hair",
      "Patella"
    ],
    "pathological_qualities": "Earthy, cardinal, cold, Saturnine; crystallization, dryness, chronic melancholy.",
    "physiological_afflictions": [
      "Eczema",
      "Erysipelas",
      "Leprosy",
      "Dislocation of bones",
      "Weak knees",
      "Dry sallow skin",
      "Stiff articulations",
      "Hypochondriasis"
    ],
    "temperament_and_healing_reaction": "Wiry, persistent, stolid. Does not yield to disease readily, but once succumbing, clings to sickness stubbornly. May resist help if aware someone is trying to 'manage' them. Requires cheerfulness, sunlight, warmth, and humorous entertainment."
  },
  {
    "sign_index": 11,
    "sign_name_en": "Aquarius",
    "sign_name_ta": "கும்பம்",
    "manilius_rulership": "The Calves, Shins, and Ankles (Tibiae)",
    "heindel_anatomical_systems": [
      "Lower limbs",
      "Calves",
      "Shins",
      "Ankles",
      "Circulatory system",
      "Venous blood flow"
    ],
    "pathological_qualities": "Airy, fixed, nervous, alternating between Saturnine gloom and Uranian hysteria.",
    "physiological_afflictions": [
      "Varicose veins",
      "Swollen ankles",
      "Leg ache",
      "Nervous exhaustion",
      "Hypersensitive skin (crawling sensation like insects)"
    ],
    "temperament_and_healing_reaction": "Ambitious, wiry, prone to overwork until bodily reserves collapse. Highly cooperative with healers. Valvular heart strain frequently manifests by reflex sympathy as swollen ankles."
  },
  {
    "sign_index": 12,
    "sign_name_en": "Pisces",
    "sign_name_ta": "மீனம்",
    "manilius_rulership": "The Feet and Toes (Pedis)",
    "heindel_anatomical_systems": [
      "Feet",
      "Toes",
      "Fibrin of blood",
      "Lymphatic system",
      "Adipose tissue"
    ],
    "pathological_qualities": "Watery, negative, lymphatic; love of ease and rich drinks, low recuperative power.",
    "physiological_afflictions": [
      "Bunions",
      "Gout",
      "Deformed feet and toes",
      "Tumors",
      "Dropsy",
      "Swelling of feet",
      "Alcohol or narcotic addictions when Moon/Neptune afflicted"
    ],
    "temperament_and_healing_reaction": "Extremely sensitive to suggestions and emotional environment. Keep away overly sympathetic visitors who encourage discussion of sickness ('No sympathetic visitors allowed' rule). Requires a bright, cheerful room."
  }
];
export const HEINDEL_PLANETS_RAW = [
  {
    "planet": "Sun",
    "planet_ta": "சூரியன்",
    "salient_keyword": "Life",
    "anatomical_rulership": "Vital fluid specialized through spleen, distribution of heat, pons varolii, heart, oxygen",
    "pathological_quality": "Hot, dry, vital, constructive, expansive, tonic",
    "positive_expression": "Radiant health, indestructible vitality, moral courage, prompt recuperation",
    "afflicted_expression": "Feverish delirium, cerebral hyperemia, cardiac strain, loss of vitality, baldness"
  },
  {
    "planet": "Venus",
    "planet_ta": "சுக்கிரன்",
    "salient_keyword": "Coalition",
    "anatomical_rulership": "Throat, kidneys, thymus gland, venous circulation, sense of touch, ovaries",
    "pathological_quality": "Warm, lymphatic, relaxing, sedentary",
    "positive_expression": "Harmony of bodily fluids, healthy venous circulation, graceful poise, artistic peace",
    "afflicted_expression": "Extravagance, sluggishness, throat relaxed tissues, kidney congestion, sensual excesses"
  },
  {
    "planet": "Mercury",
    "planet_ta": "புதன்",
    "salient_keyword": "Reason",
    "anatomical_rulership": "Nerves, bronchial tubes, pulmonary circulation, thyroid, right cerebral hemisphere, vocal cords, sensory perception",
    "pathological_quality": "Cold, dry, nervous",
    "positive_expression": "Keen intellectual alertness, prompt neurological reflexes, clear articulation",
    "afflicted_expression": "Nervous breakdown, speech impediment, auditory impairment, mental gloom (with Saturn), restlessness"
  },
  {
    "planet": "Moon",
    "planet_ta": "சந்திரன்",
    "salient_keyword": "Fecundation",
    "anatomical_rulership": "Esophagus, stomach, uterus, ovaries, lymphatics, sympathetic nervous system, synovial fluid, alimentary canal",
    "pathological_quality": "Moist, cold, nutritive, receptive, collective, fluidic",
    "positive_expression": "Healthy digestion, wholesome cellular gestation, rhythmic monthly hormonal cycles",
    "afflicted_expression": "Fluidic retention, dropsy, acute recurring illnesses (7-day cycles), digestive disturbance, lunatic hysteria"
  },
  {
    "planet": "Saturn",
    "planet_ta": "சனி",
    "salient_keyword": "Obstruction",
    "anatomical_rulership": "Gall bladder, vagus (pneumogastric) nerve, teeth, skin, joints, ligaments, sigmoid flexure",
    "pathological_quality": "Cold, dry, chronic, contracting, crystallizing, binding, restricting, centripetal, obstructive",
    "positive_expression": "Endurance, structural bone density, defensive shielding against external infection",
    "afflicted_expression": "Crystallization, gallstones, dry sallow skin, stiff joints, chronic lingering invalidism, hypochondria"
  },
  {
    "planet": "Jupiter",
    "planet_ta": "குரு",
    "salient_keyword": "Idealism",
    "anatomical_rulership": "Liver, glycogen reserves, suprarenals, arterial circulation, fibrin of blood, disposition of fats",
    "pathological_quality": "Warm, moist, nourishing, expansive, corpulent, gourmandizing",
    "positive_expression": "Benevolent vitality, clean arterial flow, generous bodily warmth, rapid recuperative rebound",
    "afflicted_expression": "Fatty liver, apoplexy, plethoric arterial hypertension, gout, indolent growths"
  },
  {
    "planet": "Mars",
    "planet_ta": "செவ்வாய்",
    "salient_keyword": "Dynamic Energy",
    "anatomical_rulership": "Iron in blood, red coloring matter (hemoglobin), genitals, motor nerves, left cerebral hemisphere, rectum",
    "pathological_quality": "Hot, dry, inflammatory, energetic, eruptive, excessive, violent, positive",
    "positive_expression": "Dynamic muscular tone, robust hemoglobin, iron-willed recuperative stamina",
    "afflicted_expression": "High fevers, acute inflammation, hemorrhage, surgical lacerations, burns, eruptive skin boils"
  },
  {
    "planet": "Uranus",
    "planet_ta": "யுரேனஸ்",
    "salient_keyword": "Altruism",
    "anatomical_rulership": "Ethers, eyes, pituitary body, bodily gases, neural electricity",
    "pathological_quality": "Dry, spasmodic, electric, explosive, convulsive, disorganizing",
    "positive_expression": "Intuition, inventive original genius, spiritual aura attunement",
    "afflicted_expression": "Sudden nervous spasms, cramps, St. Vitus dance, electrical shock accidents, hysteria"
  },
  {
    "planet": "Neptune",
    "planet_ta": "நெப்டியூன்",
    "salient_keyword": "Divinity",
    "anatomical_rulership": "Pineal gland, spinal canal, subtle nerve fiber",
    "pathological_quality": "Comatose, shrinking, stunting, restricting, constricting",
    "positive_expression": "Cosmic consciousness, mystical inspiration, spiritual healing sensitivity",
    "afflicted_expression": "Unhealthy mediumship, alcoholic delirium tremens, drug hallucinations, comatose stupor"
  },
  {
    "planet": "Pluto",
    "planet_ta": "புளூட்டோ",
    "salient_keyword": "Regeneration",
    "anatomical_rulership": "Pancreas, cellular metabolism, deep excretory elimination",
    "pathological_quality": "Volcanic, transforming, eliminative, deep metamorphic",
    "positive_expression": "Cellular rebirth, profound systemic detoxification, survival under crisis",
    "afflicted_expression": "Metabolic breakdown, pancreatic degeneration, toxic cellular stagnation"
  }
];
export const HEINDEL_SENSE_ORGANS_RAW = [
  {
    "organ_en": "Eyes (Vision)",
    "organ_ta": "கண்கள் (பார்வை)",
    "astrological_rulers": "Aries, Uranus, Sun, Moon; Critical Nebulae: Pleiades (Taurus 29°), Ascelli (Leo 6°), Antares (Sagittarius 8°)",
    "pathological_notes_en": "Sun/Moon afflicted in Aries or conjoined with nebular fixed stars causes cataracts, glaucoma, or blindness.",
    "pathological_notes_ta": "சூரியன் அல்லது சந்திரன் மேஷத்திலோ அல்லது கிருத்திகை/மகம்/கேட்டை நட்சத்திர நெபுலா புள்ளிகளிலோ பாதிக்கப்பட்டால் கண் பார்வைக் குறைபாடுகள் தோன்றும்."
  },
  {
    "organ_en": "Ears (Hearing)",
    "organ_ta": "காதுகள் (கேட்டல்)",
    "astrological_rulers": "Taurus, Mercury; 12th House / Capricorn",
    "pathological_notes_en": "Mercury in 12th house or in Capricorn afflicted by malefics impairs the auditory nerve and causes hearing loss.",
    "pathological_notes_ta": "புதன் 12-ம் வீட்டில் அல்லது மகரத்தில் சனியின் சேர்க்கை அல்லது பார்வையில் பாதிக்கப்பட்டால் செவிப்புலன் நரம்புகள் பாதிக்கப்படும்."
  },
  {
    "organ_en": "Nose (Smell)",
    "organ_ta": "மூக்கு (நுகர்தல்)",
    "astrological_rulers": "Scorpio, Mars",
    "pathological_notes_en": "Scorpio rules nasal bones, cartilage, and mucous membrane; afflicted Scorpio causes chronic nasal catarrh and polypi.",
    "pathological_notes_ta": "விருச்சிகம் மூக்கு எலும்பு மற்றும் சளிச் சவ்வுகளை ஆள்கிறது; இங்கு செவ்வாய் அல்லது சனி பாதித்தால் நாசி சதை வளர்ச்சி, சைனஸ் ஏற்படும்."
  },
  {
    "organ_en": "Tongue (Taste & Speech)",
    "organ_ta": "நாக்கு (சுவை & பேச்சு)",
    "astrological_rulers": "Taurus, Mercury",
    "pathological_notes_en": "Taurus rules larynx, vocal cords, and tongue; afflictions cause loss of speech, stammering, and taste blunting.",
    "pathological_notes_ta": "ரிஷபமும் புதனும் நாக்கு, குரல்வளையை ஆளுகின்றன; இவற்றின் பாதிப்பு பேச்சுத் தடுமாற்றம், தொண்டை அழற்சியை உண்டாக்கும்."
  }
];
export const HEINDEL_CIRCLES_RAW = [
  {
    "cross_name": "The Cardinal (Equinoctial) Cross",
    "cross_name_ta": "சர ராசி வட்டப் பிணைப்பு (Equinoctial Circle)",
    "signs_involved": [
      "Aries",
      "Cancer",
      "Libra",
      "Capricorn"
    ],
    "organ_sympathies": "Head/Eyes (Aries) <-> Stomach (Cancer) <-> Kidneys/Skin (Libra) <-> Knees/Joints (Capricorn)",
    "clinical_mechanism": "Doctors have noted strange sympathy between distant organs. Trouble in the stomach (Cancer) frequently manifests as eye glaucoma (Aries) or disturbed kidneys (Libra). Saturn in Cancer robs the stomach of fluids, invariably disturbing kidney elimination and causing stiff knee joints (Capricorn).",
    "clinical_examples": [
      "Glaucoma and eye strain whose real seat is rooted in digestive indigestion or kidney failure.",
      "Saturn in Cancer (fall): Extreme food likes/dislikes -> gastric catarrh -> kidney toxicity -> stiff knees.",
      "Headaches and migraines triggered by autointoxication from stomach and sluggish kidneys."
    ]
  },
  {
    "cross_name": "The Fixed Cross",
    "cross_name_ta": "ஸ்திர ராசி வட்டப் பிணைப்பு (Fixed Circle)",
    "signs_involved": [
      "Taurus",
      "Leo",
      "Scorpio",
      "Aquarius"
    ],
    "organ_sympathies": "Throat/Vocal (Taurus) <-> Heart/Spine (Leo) <-> Generative/Rectum/Nose (Scorpio) <-> Calves/Ankles (Aquarius)",
    "clinical_mechanism": "Profound sympathy exists between the sex organs (Scorpio) and speech organs (Taurus). Tonsil or adenoid operations in childhood often create severe reproductive/childbirth difficulties at puberty. Valvular heart trouble (Leo) regularly precipitates dropsical swelling of the ankles (Aquarius).",
    "clinical_examples": [
      "Childhood vocal/tonsil surgeries producing menstrual disorders and difficult labor in later female life.",
      "Valvular heart disease (Leo) producing venous stasis and ankle edema (Aquarius).",
      "Removal of sex organs causing sudden shift in voice pitch (male voice becoming feminine, female voice masculine)."
    ]
  },
  {
    "cross_name": "The Mutable (Common) Cross",
    "cross_name_ta": "உபய ராசி வட்டப் பிணைப்பு (Common / Cadent Circle)",
    "signs_involved": [
      "Gemini",
      "Virgo",
      "Sagittarius",
      "Pisces"
    ],
    "organ_sympathies": "Lungs/Breathing (Gemini) <-> Intestines/Spleen (Virgo) <-> Hips/Sciatic (Sagittarius) <-> Feet/Fibrin (Pisces)",
    "clinical_mechanism": "Mutable signs rule the cadent houses (6th house of sickness & 12th house of hospitals). They produce more chronic invalids due to fluctuating willpower. Sympathy between feet (Pisces) and lungs (Gemini) is confirmed by the universal clinical experience: 'catching cold or pneumonia due to wet feet'. Intestinal stasis (Virgo) floods the bloodstream and strains pulmonary oxygenation.",
    "clinical_examples": [
      "Wet and cold feet (Pisces) instantly precipitating acute bronchitis or pneumonia in lungs (Gemini).",
      "Sluggish intestinal toxemia (Virgo) undermining sciatic nerves (Sagittarius) and respiratory vitality.",
      "Lack of willpower in common signs allowing acute functional disorders to slip into chronic invalidism."
    ]
  }
];
export const HEINDEL_NAILS_RAW = [
  {
    "nail_type_en": "Heart Trouble Indications (Leo Type)",
    "nail_type_ta": "இதயக் கோளாறு நக அறிகுறிகள் (சிம்ம வகை)",
    "physical_indicators": "Large broad nail; blue half-moons (lunulae); blue palm lines; longitudinal lengthwise ridges; corners curving upwards away from flesh in chronic cases.",
    "pathological_significance": "Weakened cardiac circulation, valvular insufficiency, poor venous oxygenation.",
    "constitutional_correlation": "Leo Ascendant or Mars/Saturn square Venus afflicting the cardiac center.",
    "remedial_and_hygiene_guidance": "Avoid heavy athletic strain, maintain regular rest, avoid rich heavy meals that burden the heart."
  },
  {
    "nail_type_en": "Liver & Hepatic Trouble (Jupiter Type)",
    "nail_type_ta": "கல்லீரல் & பித்தக் கோளாறு நக அறிகுறிகள் (குரு வகை)",
    "physical_indicators": "Large nail longer than normal; wedging into flesh on the sides; yellowish tint on nails and yellow lines in palm.",
    "pathological_significance": "Biliary stasis, liver enlargement, glycogen sluggishness, sluggish bowel detox.",
    "constitutional_correlation": "Jupiter afflicted by Saturn or Mars in Virgo/Cancer/Sagittarius.",
    "remedial_and_hygiene_guidance": "Eliminate fried and fatty foods, drink lemon water, incorporate daily walking and bitter leafy greens."
  },
  {
    "nail_type_en": "Pulmonary & Lung Weakness (Gemini / Watery Type)",
    "nail_type_ta": "நுரையீரல் பலவீன நக அறிகுறிகள் (மிதுன வகை)",
    "physical_indicators": "Long slender claw-like nails; pale whitish hue; ridged lengthwise; thin delicate skin.",
    "pathological_significance": "Tubercular susceptibility, weak thoracic capacity, shallow pulmonary exchange, chronic coughs.",
    "constitutional_correlation": "Gemini rising or Saturn/Mars afflicting Sun or Mercury in common signs.",
    "remedial_and_hygiene_guidance": "Calisthenics, fresh sleeping apartment ventilation, rhythmic deep breathing exercises."
  },
  {
    "nail_type_en": "Nervous Exhaustion (Mercury Type)",
    "nail_type_ta": "நரம்புத் தளர்ச்சி நக அறிகுறிகள் (புதன் வகை)",
    "physical_indicators": "Narrow, delicate, thin, brittle nails; white spots scattered across nail plates.",
    "pathological_significance": "Impoverished blood, anemia, nervous overwork, sensory tension.",
    "constitutional_correlation": "Mercury square or opposite Saturn or Uranus; prominent airy signs.",
    "remedial_and_hygiene_guidance": "Nervine rest, warm oil massage, reduction of intellectual hyper-stimulation, calm rose-colored environment."
  },
  {
    "nail_type_en": "Temperamental Lack of Control (Nail Biting)",
    "nail_type_ta": "முன்கோபம் & கட்டுப்பாடின்மை (நகங்களைக் கடிக்கும் இயல்பு)",
    "physical_indicators": "Short, bitten, jagged nail beds; carrying chips on shoulder, easily wounded feelings.",
    "pathological_significance": "Explosive temper, lack of nervous self-control, subconscious emotional tension.",
    "constitutional_correlation": "Mars afflicted by Uranus or Mercury in fiery or cardinal signs.",
    "remedial_and_hygiene_guidance": "Cultivate conscious emotional pause, rhythmic slow breathing when irritated, artistic outlets."
  },
  {
    "nail_type_en": "Spinal & Structural Weakness",
    "nail_type_ta": "முதுகெலும்பு பலவீன நக அறிகுறிகள்",
    "physical_indicators": "Concave top surface of nails ('spooned' nail plates / koilonychia).",
    "pathological_significance": "Spinal weakness, vertebral misalignment, calcium metabolic deficiency.",
    "constitutional_correlation": "Afflictions in Leo (dorsal spine) or Capricorn/Sagittarius (sacral/skeletal).",
    "remedial_and_hygiene_guidance": "Postural exercises, gentle spinal traction, sunlight therapy for mineral assimilation."
  },
  {
    "nail_type_en": "The Thumb: Will vs Logic Proportion",
    "nail_type_ta": "பெருவிரல்: இச்சை & புத்தி சமநிலை",
    "physical_indicators": "Well-proportioned: 1st phalanx (will) = 2/5th, 2nd phalanx (reason) = 3/5th. Tip reaches middle joint of index finger. Club-shaped thumb with short nail = ungovernable temper ('sees red'). Very long 1st phalanx = reckless impulse; very long 2nd phalanx = talker but not doer.",
    "pathological_significance": "Reveals whether the patient has sufficient willpower to follow hygienic directions and overcome illness.",
    "constitutional_correlation": "Mount of Venus at base of thumb (vitality & desire); Mount of Luna (imagination & nervous balance).",
    "remedial_and_hygiene_guidance": "Healers must gauge patient will-power from the thumb before outlining extensive lifestyle regimes."
  }
];
export const HEINDEL_ANTIDOTES_RAW = [
  {
    "afflicting_planet": "Mars (Excessive Heat, Fevers, Violence, Inflammation)",
    "afflicting_metal": "Iron",
    "antidote_planet": "Venus",
    "antidote_metal": "Copper",
    "antidote_gem": "Emerald / Moss Agate",
    "antidote_color": "Yellow / Soft Green",
    "polarity_law": "Mars represents animal passion, physical friction, and inflammatory heat. Venus is the celestial opposite of Mars; her soothing love-ray and metal Copper act as a natural vibratory antidote for harsh martial vibrations. A person with excessive Mars should have minimal contact with raw iron and utilize copper and calm colors.",
    "practical_application": "Drink water stored in copper vessels, wear soft green or yellow tones, avoid fiery spices."
  },
  {
    "afflicting_planet": "Saturn (Cold Obstruction, Melancholy, Crystallization)",
    "afflicting_metal": "Lead",
    "antidote_planet": "Jupiter",
    "antidote_metal": "Tin",
    "antidote_gem": "Turquoise / Carbuncle",
    "antidote_color": "Sky Blue",
    "polarity_law": "Saturn represents contraction, binding, cold, and obstruction. Jupiter is his celestial opposite; his expansive, benevolent warmth and metal Tin dissolve Saturnian crystallization and melancholia. Tin and sky-blue vibrations stimulate cheerfulness and arterial warmth.",
    "practical_application": "Wear tin-based talismanic charms or sky-blue apparel, spend time in sunny rooms, cultivate jovial company."
  }
];
export const HEINDEL_NEBULAR_RAW = [
  {
    "name": "Pleiades",
    "zodiac_degree": "29° Taurus",
    "pathological_focus": "Severe Ocular Affections, Visual Weakness, Cataracts",
    "esoteric_mitigation": "When benevolence aspects this degree, loss of physical sight awakens inner clairvoyant second-sight."
  },
  {
    "name": "Ascelli",
    "zodiac_degree": "6° Leo",
    "pathological_focus": "Ocular Inflammation, Corneal Affections, Impaired Visual Acuity",
    "esoteric_mitigation": "Encourages spiritual introspection and deep solar inner light."
  },
  {
    "name": "Antares",
    "zodiac_degree": "8° Sagittarius",
    "pathological_focus": "Acute Eye Afflictions, Traumatic Eye Injuries, Blindness Risk",
    "esoteric_mitigation": "The most potent nebular spot. While malefic configurations harm physical sight, benefic aspects bestow profound second-sight."
  }
];
export const HEINDEL_APHORISMS_RAW = [
  {
    "number": 1,
    "category": "Lunar Cycles",
    "aphorism_en": "The Moon may be regarded as the giver and the taker of life; carrying life forces from Sun to earth, and eventually producing death.",
    "aphorism_ta": "சந்திரன் உயிரை அளிப்பவராகவும் எடுப்பவராகவும் கருதப்படுகிறார்; சூரியனின் பிராண சக்தியை பூமிக்குக் கடத்துகிறார், முடிவில் மரணத்தையும் ஏற்படுத்துகிறார்.",
    "practical_implication": "Watch the Moon's phase and aspects continuously in all therapeutic schedules."
  },
  {
    "number": 2,
    "category": "Lunar Cycles",
    "aphorism_en": "When the Moon is full, tides are higher, bones are fuller of marrow, and body temperature is highest in fevers.",
    "aphorism_ta": "பௌர்ணமி நாளில் கடல் அலைகள் உயர்வது போல், எலும்பு மஜ்ஜை நிரம்புகிறது; காய்ச்சலின் போது உடல் வெப்பம் உச்சமடைகிறது.",
    "practical_implication": "Anticipate fever spikes during the Full Moon; employ cooling hydropathy."
  },
  {
    "number": 3,
    "category": "Natal Constitution",
    "aphorism_en": "During the first half of life (particularly childhood) the Moon has greatest rule; in the latter half, the Sun has strongest influence.",
    "aphorism_ta": "வாழ்வின் முதல் பாதியில் (குறிப்பாக குழந்தைப் பருவத்தில்) சந்திரன் ஆதிக்கமும், இரண்டாம் பாதியில் சூரியனின் ஆதிக்கமும் மேலோங்குகிறது.",
    "practical_implication": "Pediatric ailments correlate primarily to the Moon; adult degenerative issues to the Sun."
  },
  {
    "number": 4,
    "category": "Natal Constitution",
    "aphorism_en": "The Moon has great influence over nervous, hysterical, and lunatic patients. They should never sleep with the moon shining on them.",
    "aphorism_ta": "மன அழுத்தம், நரம்புத் தளர்ச்சி, ஹிஸ்டீரியா நோயாளிகள் மீது சந்திரன் அதிக தாக்கம் செலுத்துகிறார். அவர்கள் நிலா வெளிச்சம் நேராகப் படும்படி தூங்கக் கூடாது.",
    "practical_implication": "Shield bedrooms of sensitive or insomnia patients from direct lunar rays."
  },
  {
    "number": 5,
    "category": "Lunar Cycles",
    "aphorism_en": "At New Moon material forces are weakest. The waning moon (Full to New) is strongest for spiritual healing and elimination.",
    "aphorism_ta": "அமாவாசையில் உடலின் ஸ்தூல ஆற்றல் மிகக் குறைவாக இருக்கும். பௌர்ணமி முதல் அமாவாசை வரையிலான தேய்பிறை காலம் நச்சு நீக்கத்திற்கும் ஆன்மீக சிகிச்சைகளுக்கும் உகந்தது.",
    "practical_implication": "Schedule detoxification, cleansing fasts, and spiritual meditations during waning moon."
  },
  {
    "number": 6,
    "category": "Surgical Precaution",
    "aphorism_en": "Do not perform an operation when the Moon is in the sign ruling that part of the body. (Ptolemy: 'Pierce not with iron that part of the body governed by the sign occupied by the Moon').",
    "aphorism_ta": "சந்திரன் எந்த ராசியில் சஞ்சரிக்கிறதோ, அந்த ராசிக்குரிய உடல் உறுப்பில் அறுவை சிகிச்சை செய்யக் கூடாது (தாலமியின் பொன்மொழி: 'சந்திரன் நிற்கும் ராசியின் உறுப்பை இரும்பால் துளைக்காதே').",
    "practical_implication": "Golden rule of surgical timing: avoid operations when transiting Moon occupies the governed organ sign."
  },
  {
    "number": 7,
    "category": "Surgical Precaution",
    "aphorism_en": "Operations performed at exact change of the Moon are rarely successful. Choose waxing moon ('light of the moon'). Do not operate when Sun is in sign of the organ.",
    "aphorism_ta": "சந்திர மாற்ற தினங்களில் (அமாவாசை/பௌர்ணமி சந்தி) செய்யப்படும் அறுவை சிகிச்சைகள் அரிதாகவே வெற்றியடைகின்றன. வளர்பிறையைத் தேர்ந்தெடுக்கவும்; சூரியன் அந்த உறுப்பு ராசியில் இருக்கும்போதும் அறுவை சிகிச்சை செய்யக் கூடாது.",
    "practical_implication": "Avoid surgery at exact lunations; favor waxing lunar phases for tissue repair."
  },
  {
    "number": 8,
    "category": "Lunar Cycles",
    "aphorism_en": "Disease reaches a critical turning point every 7 days (7th day square, 14th day opposition, 21st day square, 28th day cycle).",
    "aphorism_ta": "நோய்கள் ஒவ்வொரு 7 நாட்களுக்கும் ஒரு திருப்புமுனையை அடைகின்றன (7-ம் நாள் கேந்திர சதுரம், 14-ம் நாள் சமசப்தகம், 21-ம் நாள் மறு சதுரம், 28-ம் நாள் முழுச் சுற்று).",
    "practical_implication": "Carefully manage patient crisis on the 7th, 14th, and 21st days of an acute illness."
  },
  {
    "number": 9,
    "category": "Natal Constitution",
    "aphorism_en": "The Moon rules acute disease; the Sun rules chronic disease.",
    "aphorism_ta": "சந்திரன் குறுகிய கால தீவிர நோய்களையும், சூரியன் நீண்ட கால நாள்பட்ட நோய்களையும் ஆளுகிறார்.",
    "practical_implication": "Trace acute flare-ups to lunar transits; evaluate chronic endurance via solar dignity."
  },
  {
    "number": 10,
    "category": "Surgical Precaution",
    "aphorism_en": "Watch squares and oppositions of the Moon to transiting Sun, Mars, and Saturn when operating.",
    "aphorism_ta": "அறுவை சிகிச்சையின் போது சந்திரன் கோச்சார சூரியன், செவ்வாய், சனியுடன் 90° அல்லது 180° பார்வையில் இருப்பதைத் தவிர்க்க வேண்டும்.",
    "practical_implication": "Elective surgery must avoid lunar square or opposition to Mars (hemorrhage) or Saturn (hypothermia/collapse)."
  },
  {
    "number": 11,
    "category": "Natal Constitution",
    "aphorism_en": "The Moon has greatest rule over the health of woman, while the Sun influences the health of man.",
    "aphorism_ta": "பெண்களின் உடல்நலத்தில் சந்திரன் பிரதான ஆதிக்கம் செலுத்துகிறார்; ஆண்களின் உடல்நலத்தில் சூரியன் முதன்மை பெறுகிறார்.",
    "practical_implication": "Weigh Moon afflictions heavier in female nativities and Sun afflictions in male nativities."
  },
  {
    "number": 12,
    "category": "Therapeutic Dosage",
    "aphorism_en": "From New to Full Moon stimulants produce the most effect and sedatives are weakest; decrease stimulant dose and increase sedatives.",
    "aphorism_ta": "அமாவாசை முதல் பௌர்ணமி வரை ஊக்கிகள் தீவிரமாகவும் அமைதிப்படுத்திகள் பலவீனமாகவும் செயல்படும்; ஊக்கிகளின் அளவைக் குறைத்து அமைதிப்படுத்திகளை அதிகரிக்க வேண்டும்.",
    "practical_implication": "Calibrate pharmacological and herbal dosages to waxing vs waning lunar phases."
  },
  {
    "number": 13,
    "category": "Therapeutic Dosage",
    "aphorism_en": "When increasing Moon is in good aspect to radical Jupiter or Venus, cardiac stimulation produces most lasting results.",
    "aphorism_ta": "வளர்பிறை சந்திரன் ஜாதக குரு அல்லது சுக்கிரனுடன் சுப பார்வை பெறும்போது இதய ஊட்ட சிகிச்சைகள் நீடித்த பலனைத் தரும்.",
    "practical_implication": "Best timing for heart tonic therapies is during waxing Moon trine/sextile Venus or Jupiter."
  },
  {
    "number": 14,
    "category": "Transits",
    "aphorism_en": "Good aspects to radical Moon from transiting Jupiter and Venus are very helpful in overcoming illness.",
    "aphorism_ta": "கோச்சார குரு மற்றும் சுக்கிரன் ஜாதக சந்திரன் மீது நல்ல பார்வை செலுத்தும் போது நோயில் இருந்து மீள்வது மிக எளிதாகிறது.",
    "practical_implication": "Look to transit Jupiter or Venus trines to natal Moon for optimal convalescence."
  },
  {
    "number": 15,
    "category": "Natal Constitution",
    "aphorism_en": "Saturn placed in the 6th house of the horoscope at birth has a persistent tendency to lower vitality.",
    "aphorism_ta": "பிறப்பு ஜாதகத்தில் 6-ம் பாவத்தில் அமரும் சனி உடலின் நோய் எதிர்ப்பு சக்தியையும் பிராண பலத்தையும் குறைக்கும் தன்மையுடையவர்.",
    "practical_implication": "Native requires lifelong habits of regular rest, warm foods, and avoidance of chills."
  },
  {
    "number": 16,
    "category": "Natal Constitution",
    "aphorism_en": "The sign and house of the Sun at birth is a vital locality; from its strength one may judge the patient's recuperative power.",
    "aphorism_ta": "சூரியன் நிற்கும் ராசியும் பாவமும் மிக முக்கியமானவை; அதன் பலத்தைக் கொண்டே நோயாளியின் குணமாகும் வேகத்தைக் கணிக்கலாம்.",
    "practical_implication": "Strong Sun in Aries/Leo/Sagittarius ensures rapid cellular recovery."
  },
  {
    "number": 17,
    "category": "Natal Constitution",
    "aphorism_en": "Benefic aspects between Sun and Mars give great vitality. An evil aspect between Sun and Mars is better than no aspect at all.",
    "aphorism_ta": "சூரியன் மற்றும் செவ்வாய் இடையேயான சுப சேர்க்கை அதீத பலத்தைத் தரும்; இவற்றிடையே அசுப பார்வை இருந்தாலும் கூட, எந்த பார்வையும் இல்லாமல் இருப்பதை விட அது நன்று.",
    "practical_implication": "Mars-Sun aspects provide dynamic fighting vitality against bacterial onslaughts."
  },
  {
    "number": 18,
    "category": "Diagnostic Discretion",
    "aphorism_en": "Aspects to Ascendant and Midheaven should be used with great discretion unless the minute of birth is verified.",
    "aphorism_ta": "பிறப்பு நேரம் மிகத் துல்லியமாக உறுதி செய்யப்படாதவரை லக்னம் மற்றும் பத்தாம் பாவ புள்ளியின் பார்வைகளை எச்சரிக்கையுடன் கையாள வேண்டும்.",
    "practical_implication": "Verify birth time against physical appearance and nail types before relying on degree cusps."
  },
  {
    "number": 19,
    "category": "Critical Degrees",
    "aphorism_en": "Planets in critical degrees have a greater influence for good or evil than in other degrees.",
    "aphorism_ta": "முக்கிய சந்திகளிலும் நெருக்கடி பாகைகளிலும் நிற்கும் கிரகங்கள் அதீத நன்மையையோ அல்லது தீவிர தீமையையோ உண்டாக்கும்.",
    "practical_implication": "Examine planets in 0° or 29° of signs for intense constitutional reactions."
  },
  {
    "number": 20,
    "category": "Fixed Stars",
    "aphorism_en": "Watch three nebular spots: Pleiades (29° Taurus), Ascelli (6° Leo), and Antares (8° Sagittarius); they powerfully affect eyesight.",
    "aphorism_ta": "மூன்று நட்சத்திர நெபுலா புள்ளிகளைக் கவனியுங்கள்: கிருத்திகை (ரிஷபம் 29°), மகம் (சிம்மம் 6°), கேட்டை (தனுசு 8°); இவை கண் பார்வையை பெரிதும் பாதிக்கும்.",
    "practical_implication": "Check Sun, Moon, or malefics on these coordinates for ocular vulnerability."
  },
  {
    "number": 21,
    "category": "Natal Constitution",
    "aphorism_en": "A child with no aspect between Sun and Mars is subject to many childhood illnesses due to lack of muscular fighting heat.",
    "aphorism_ta": "சூரியனுக்கும் செவ்வாய்க்கும் இடையே எந்தத் தொடர்பும் இல்லாத குழந்தை, தற்காப்பு உஷ்ணம் இன்மையால் அடிக்கடி நோய்களுக்கு ஆளாகும்.",
    "practical_implication": "Nourish the child with iron-rich foods, sunlight, and invigorating play."
  },
  {
    "number": 22,
    "category": "Environment Therapy",
    "aphorism_en": "Patients with planets in airy signs require abundant fresh air; fiery signs require sunlight; watery/earthy signs suffer from excessive sun.",
    "aphorism_ta": "காற்று ராசியினர் அதிக தூய காற்றையும், நெருப்பு ராசியினர் அதிக சூரிய ஒளியையும் விரும்புகிறார்கள்; நீர் மற்றும் நில ராசியினருக்கு அதிக வெயில் பாதகமாகும்.",
    "practical_implication": "Customize patient sickroom ventilation and sunlight exposure to natal elemental dominance."
  },
  {
    "number": 23,
    "category": "Natal Constitution",
    "aphorism_en": "Fixed signs on angles with afflictions in common signs allows native to overcome disease. Common signs on angles with fixed afflictions succumbs easily.",
    "aphorism_ta": "ஸ்திர ராசிகள் கேந்திரத்தில் இருந்து உபய ராசிகளில் தோஷம் இருந்தால் நோய் குணமாகும்; உபய ராசிகள் கேந்திரத்தில் இருந்து ஸ்திர ராசிகளில் தோஷம் இருந்தால் நோயில் வீழ்வர்.",
    "practical_implication": "Angular stability determines constitutional tenacity to throw off disease."
  },
  {
    "number": 24,
    "category": "Natal Constitution",
    "aphorism_en": "A well-aspected Sun in Aries or Leo gives radiant vitality and an innate ability to throw off disease.",
    "aphorism_ta": "மேஷம் அல்லது சிம்மத்தில் சுப பார்வை பெற்ற சூரியன் அபார பிராண சக்தியையும் நோய்களை அண்டவிடாத இயற்கை வலிமையையும் தருகிறார்.",
    "practical_implication": "Native rarely requires extensive pharmaceuticals; simple natural hygiene suffices."
  },
  {
    "number": 25,
    "category": "Natal Constitution",
    "aphorism_en": "People with Aries rising or Sun/Mars in Aries develop very high temperatures quickly, blood rushing to head and skin.",
    "aphorism_ta": "மேஷ லக்னம் அல்லது மேஷத்தில் சூரியன்/செவ்வாய் உள்ளவர்கள் நோயுற்றால் தலைக்கும் தோலுக்கும் இரத்தம் பாய்ந்து அதிதீவிர காய்ச்சல் உடனடியாகத் தோன்றும்.",
    "practical_implication": "Apply prompt cold compresses to head; do not panic as Aries easily endures high fevers."
  },
  {
    "number": 26,
    "category": "Natal Constitution",
    "aphorism_en": "Sun afflicted by Saturn or Moon square Sun yields low vitality. Watch progressed Moon and lunation transits.",
    "aphorism_ta": "சூரியன் சனியால் பாதிக்கப்பட்டாலோ அல்லது சந்திரன் சூரியனுடன் சதுரப் பார்வை பெற்றாலோ குறைந்த பிராண சக்தியே இருக்கும்.",
    "practical_implication": "Native must pace their daily exertions and avoid extreme physical fatigue."
  },
  {
    "number": 27,
    "category": "Planetary Motion",
    "aphorism_en": "Retrograde planets give latent influence in disease; their effect is dormant until they turn direct in progression or transit.",
    "aphorism_ta": "வக்ர கிரகங்கள் நோயில் மறைமுக தாக்கத்தை அளிக்கின்றன; அவை நேர்கதியில் திரும்பும் போதே அவற்றின் உண்மையான பலன் வெளிப்படும்.",
    "practical_implication": "Dormant symptoms may flare into clinical manifestation when the afflicting planet turns direct."
  },
  {
    "number": 28,
    "category": "Planetary Motion",
    "aphorism_en": "Planets turning from retrograde to direct move slowly; their influence is not as vital as when swiftly moving.",
    "aphorism_ta": "வக்ர நிவர்த்தியாகி மெதுவாக நகரும் கிரகங்களின் ஆற்றல் வேகமாக நகரும் நிலையை விட மந்தமாகவே செயல்படும்.",
    "practical_implication": "Convalescence proceeds slowly while key significators linger in stationary motion."
  },
  {
    "number": 29,
    "category": "Planetary Dignity",
    "aphorism_en": "Planets are strong when in signs of their own nature, and when in aspect to planets in compatible signs.",
    "aphorism_ta": "கிரகங்கள் தங்கள் சுபாவத்திற்கு ஒத்த ராசிகளிலும், நட்பான ராசி கிரகங்களுடன் இணையும் போதும் வலிமை பெறுகின்றன.",
    "practical_implication": "Elemental compatibility between aspecting planets fosters physiological harmony."
  },
  {
    "number": 30,
    "category": "Diagnostic Method",
    "aphorism_en": "When birth hour is unknown, a fairly accurate diagnosis can be obtained using a flat chart (Aries on 1st house).",
    "aphorism_ta": "பிறந்த நேரம் தெரியாத போது, மேஷத்தை முதல் வீடாகக் கொண்டு அமைக்கும் காலபுருஷ சக்கரம் மூலமும் துல்லியமாக ஆராயலாம்.",
    "practical_implication": "Flat Kalapurusha charts provide invaluable baseline organ vulnerability assessments."
  },
  {
    "number": 31,
    "category": "Planetary Action",
    "aphorism_en": "Saturn's influence is contracting and binding, while Mars' influence is loosening, inflammatory, and eruptive.",
    "aphorism_ta": "சனியின் தாக்கம் சுருக்குதல், இறுக்குதல் மற்றும் அடைப்பைத் தரும்; செவ்வாயின் தாக்கம் தளர்வு, உஷ்ணம் மற்றும் வெடிப்பைத் தரும்.",
    "practical_implication": "Distinguish between Saturnine stricture/atrophy and Martial hemorrhage/ulceration."
  },
  {
    "number": 32,
    "category": "Solar Vitality",
    "aphorism_en": "The Sun rules the vital etheric fluid specialized through the spleen; afflictions to Sun cause vitality breakdown.",
    "aphorism_ta": "மண்ணீரல் மூலம் உடலுக்குள் பரவும் பிராண எத்தர் திரவத்தை சூரியன் ஆள்கிறார்; சூரியன் கெட்டால் பிராண சக்தி வடிந்துவிடும்.",
    "practical_implication": "Support spleen and solar plexus through morning sunlight and deep conscious respiration."
  },
  {
    "number": 33,
    "category": "Fixed Stars",
    "aphorism_en": "Radical Sun or Moon within orb of Pleiades (29° Taurus), Ascelli (6° Leo), or Antares (8° Sag) indicates serious eye trouble.",
    "aphorism_ta": "ஜாதக சூரியன் அல்லது சந்திரன் கிருத்திகை (29°), மகம் (6°), அல்லது கேட்டை (8°) பாகையில் இருந்தால் தீவிர கண் கோளாறுகள் ஏற்படும்.",
    "practical_implication": "Protect vision from glare and avoid eye surgeries during adverse transits to these points."
  },
  {
    "number": 34,
    "category": "Sense Organs",
    "aphorism_en": "Mercury in the 12th house afflicted by malefics, or Mercury in Capricorn afflicted, will impair hearing.",
    "aphorism_ta": "புதன் 12-ம் வீட்டில் அசுப கிரகங்களால் பாதிக்கப்பட்டாலோ அல்லது மகரத்தில் பாதிக்கப்பட்டாலோ செவித்திறன் குறையும்.",
    "practical_implication": "Examine auditory nerves and avoid loud noise trauma for natives with this placement."
  },
  {
    "number": 35,
    "category": "House Influences",
    "aphorism_en": "Watch malefic planets placed in 6th (sickness) or 12th (hospitals and confinement).",
    "aphorism_ta": "6-ம் பாவம் (நோய்) அல்லது 12-ம் பாவத்தில் (மருத்துவமனை அனுமதி) உள்ள அசுப கிரகங்களை மிகக் கவனமாக ஆராய வேண்டும்.",
    "practical_implication": "Malefics in 12th signal prolonged hospital confinement during their active dasha periods."
  },
  {
    "number": 36,
    "category": "Planetary Detriment",
    "aphorism_en": "Antipathy between signs and planets (e.g. fiery Mars in watery Pisces, cold Saturn in fiery Aries) becomes a menace to health.",
    "aphorism_ta": "பகை ராசிகளில் கிரகங்கள் அமர்வது (எ.கா: நீரில் செவ்வாய், நெருப்பில் சனி) உடல் நலத்திற்கு பெரும் அச்சுறுத்தலாக மாறும்.",
    "practical_implication": "Elemental friction in fall/detriment signs triggers metabolic toxicity."
  },
  {
    "number": 37,
    "category": "Natal Weakness",
    "aphorism_en": "The place where Saturn is found in the horoscope is most likely to be the weakest spot in the physical body.",
    "aphorism_ta": "ஜாதகத்தில் சனி அமர்ந்துள்ள ராசியும் பாவமுமே அந்த மனிதனின் உடலில் மிகவும் பலவீனமான, நோயால் எளிதில் தாக்கப்படும் பகுதியாகும்.",
    "practical_implication": "Focus preventive care directly upon the anatomical organ ruled by Saturn's natal house and sign."
  },
  {
    "number": 38,
    "category": "Blood Chemistry",
    "aphorism_en": "Mars aids blood heat by dissolving iron (Mars metal), enabling hemoglobin to attract oxygen (a Sun element).",
    "aphorism_ta": "செவ்வாய் உடலில் இரும்புச்சத்தை கரைத்து வெப்பத்தை உண்டாக்குகிறது; இது சூரியனின் பிராணவாயுவை (ஆக்ஸிஜன்) இரத்தம் ஈர்க்க உதவுகிறது.",
    "practical_implication": "Anemia and cold extremities indicate deficient Martial dynamic ignition of solar oxygen."
  },
  {
    "number": 39,
    "category": "Mental Hygiene",
    "aphorism_en": "A patient with Mercury square Saturn suffers from constitutional gloom; choose a cheerful sunny room with rose-colored walls.",
    "aphorism_ta": "புதன்-சனி சதுரப் பார்வை கொண்ட நோயாளி மனச்சோர்வால் வாடுவார்; அவருக்கு இளஞ்சிவப்பு (ரோஸ்) நிற சுவர்கள் கொண்ட சூரிய வெளிச்சம் உள்ள அறையைத் தேர்வு செய்யவும்.",
    "practical_implication": "Chromotherapy: Rose and warm tints antidote Saturnian melancholia and stimulate neurological joy."
  },
  {
    "number": 40,
    "category": "Natal Constitution",
    "aphorism_en": "Leo on the Ascendant with Sun in Aries (exaltation) gives abundant vitality and supreme power to throw off disease.",
    "aphorism_ta": "சிம்ம லக்னமாகி சூரியன் மேஷத்தில் உச்சம் பெற்றால் அளப்பரிய பிராண சக்தியும் நோய்களை வெல்லும் மகா ஆற்றலும் உண்டாகும்.",
    "practical_implication": "Native possesses extraordinary natural self-healing and recuperative longevity."
  },
  {
    "number": 41,
    "category": "Therapeutic Relief",
    "aphorism_en": "For Mars afflictions, seek relief when progressed Moon reaches good aspect of Venus. For Saturn afflictions, seek Moon-Jupiter aspects.",
    "aphorism_ta": "செவ்வாயின் நோய்களுக்கு சந்திரன் சுக்கிரனை சுபமாகப் பார்க்கும் போதும், சனியின் நோய்களுக்கு சந்திரன் குருவைப் பார்க்கும் போதும் நிவாரணம் கிட்டும்.",
    "practical_implication": "Venus antidotes Mars; Jupiter antidotes Saturn. Time therapeutic breakthroughs accordingly."
  },
  {
    "number": 42,
    "category": "Disease Onset",
    "aphorism_en": "If the Moon is in conjunction with Saturn at the inception of an illness, expect the disease to be of long duration.",
    "aphorism_ta": "ஒரு நோய் தொடங்கும் நேரத்தில் சந்திரன் சனியுடன் இணைந்திருந்தால், அந்த நோய் நீண்ட காலம் நீடிக்கும் நாள்பட்ட நோயாக மாறும்.",
    "practical_implication": "Prepare the patient for long-term supportive therapy and prevent discouragement."
  },
  {
    "number": 43,
    "category": "Disease Timing",
    "aphorism_en": "Disease related to the Moon changes within 28 days; disease related to the Sun is chronic, stubborn, and of long duration.",
    "aphorism_ta": "சந்திரன் சார்ந்த நோய் 28 நாட்களுக்குள் மாற்றம் அடையும்; சூரியன் சார்ந்த நோய் நாள்பட்டதாகவும் சிகிச்சைக்கு பிடிவாதமானதாகவும் இருக்கும்.",
    "practical_implication": "Reassure acute lunar patients of imminent recovery, while fortifying solar patients with patience."
  }
];

export function evaluateMaxHeindelCompendium(
  horoscope: HoroscopeResponse,
  houseOccupants: Record<number, string[]>,
  planetHouse: Record<string, number>,
  planetSign: Record<string, number>,
  houseToSign: Record<number, number>
): MaxHeindelCompendium {
  const asc = (horoscope as any).ascendant;
  const lagnaSign = houseToSign[1] || 1;
  const sunSign = planetSign["Sun"] || 1;
  const moonSign = planetSign["Moon"] || 1;
  const sunH = planetHouse["Sun"] || 1;
  const satH = planetHouse["Saturn"] || 1;
  const satSign = planetSign["Saturn"] || 1;
  const marsH = planetHouse["Mars"] || 1;
  const marsSign = planetSign["Mars"] || 1;
  const mercH = planetHouse["Mercury"] || 1;
  const mercSign = planetSign["Mercury"] || 1;
  const venSign = planetSign["Venus"] || 1;
  const venH = planetHouse["Venus"] || 1;

  // 1. Signs Anatomy
  const signsAnatomy: HeindelSignAnatomy[] = HEINDEL_SIGNS_RAW.map((s: any) => ({
    sign_index: s.sign_index,
    sign_name_en: s.sign_name_en,
    sign_name_ta: s.sign_name_ta,
    manilius_rulership: s.manilius_rulership,
    heindel_anatomical_systems: s.heindel_anatomical_systems,
    pathological_qualities: s.pathological_qualities,
    physiological_afflictions: s.physiological_afflictions,
    temperament_and_healing_reaction: s.temperament_and_healing_reaction,
    is_native_ascendant: s.sign_index === lagnaSign,
    is_native_sun_sign: s.sign_index === sunSign,
    is_native_moon_sign: s.sign_index === moonSign,
  }));

  // 2. Planets Physiology
  const planetsPhysiology: HeindelPlanetPhysiology[] = HEINDEL_PLANETS_RAW.map((p: any) => {
    const pSign = planetSign[p.planet];
    const pH = planetHouse[p.planet];
    let status = "Balanced";
    if (pSign !== undefined && pH !== undefined) {
      if (pH === 6 || pH === 8 || pH === 12) {
        status = `In House ${pH} (Dusthana/Sensitive)`;
      } else if ([1, 5, 9].includes(pSign)) {
        status = `In Fire Sign (Active)`;
      } else if ([2, 6, 10].includes(pSign)) {
        status = `In Earth Sign (Material)`;
      } else if ([3, 7, 11].includes(pSign)) {
        status = `In Air Sign (Mental)`;
      } else {
        status = `In Water Sign (Fluidic)`;
      }
      if ((p.planet === "Saturn" || p.planet === "Mars") && (pH === 1 || pH === 6 || pH === 8)) {
        status += " (Active Constitutional Afflicter)";
      }
    }
    return {
      planet: p.planet,
      planet_ta: p.planet_ta,
      salient_keyword: p.salient_keyword,
      anatomical_rulership: p.anatomical_rulership,
      pathological_quality: p.pathological_quality,
      positive_expression: p.positive_expression,
      afflicted_expression: p.afflicted_expression,
      chart_status: status,
    };
  });

  // 3. Vicious Circles
  const cardinalSigns = new Set([1, 4, 7, 10]);
  const fixedSigns = new Set([2, 5, 8, 11]);
  const mutableSigns = new Set([3, 6, 9, 12]);

  const viciousCircles: HeindelViciousCircle[] = HEINDEL_CIRCLES_RAW.map((vc: any) => {
    let isActive = false;
    let crossPlanets: string[] = [];
    if (vc.cross_name.includes("Cardinal")) {
      isActive = cardinalSigns.has(lagnaSign);
      crossPlanets = Object.keys(planetSign).filter((pl) => cardinalSigns.has(planetSign[pl]));
    } else if (vc.cross_name.includes("Fixed")) {
      isActive = fixedSigns.has(lagnaSign);
      crossPlanets = Object.keys(planetSign).filter((pl) => fixedSigns.has(planetSign[pl]));
    } else {
      isActive = mutableSigns.has(lagnaSign);
      crossPlanets = Object.keys(planetSign).filter((pl) => mutableSigns.has(planetSign[pl]));
    }
    return {
      cross_name: vc.cross_name,
      cross_name_ta: vc.cross_name_ta,
      signs_involved: vc.signs_involved,
      organ_sympathies: vc.organ_sympathies,
      clinical_mechanism: vc.clinical_mechanism,
      clinical_examples: vc.clinical_examples,
      is_native_cross_active: isActive,
      chart_notes: `Lagna in this cross: ${isActive ? "Yes" : "No"}. Planets in cross: ${crossPlanets.join(", ") || "None"}.`,
    };
  });

  // 4. Nail Diagnosis
  const nailDiagnosis: HeindelNailDiagnosis[] = HEINDEL_NAILS_RAW.map((n: any) => ({
    nail_type_en: n.nail_type_en,
    nail_type_ta: n.nail_type_ta,
    physical_indicators: n.physical_indicators,
    pathological_significance: n.pathological_significance,
    constitutional_correlation: n.constitutional_correlation,
    remedial_and_hygiene_guidance: n.remedial_and_hygiene_guidance,
  }));

  // 5. Planetary Antidotes
  const planetaryAntidotes: HeindelPlanetaryAntidote[] = HEINDEL_ANTIDOTES_RAW.map((a: any) => ({
    afflicting_planet: a.afflicting_planet,
    afflicting_metal: a.afflicting_metal,
    antidote_planet: a.antidote_planet,
    antidote_metal: a.antidote_metal,
    antidote_gem: a.antidote_gem,
    antidote_color: a.antidote_color,
    polarity_law: a.polarity_law,
    practical_application: a.practical_application,
  }));

  // 6. Nebular Spots
  const planetsList = (horoscope as any).planets || [];
  const nebularSpots: HeindelNebularSpot[] = HEINDEL_NEBULAR_RAW.map((ns: any) => {
    let prox = false;
    const conjoined: string[] = [];
    for (const pl of planetsList) {
      const pName = pl.name || "";
      const pSign = pl.sign || "";
      const pDeg = Number(pl.degree || 0);
      if (ns.name === "Pleiades" && (pSign.includes("Taurus") || pSign.includes("Rishaba")) && pDeg >= 26.0) {
        conjoined.push(`${pName} (${pDeg.toFixed(1)}° Taurus)`);
      } else if (ns.name === "Ascelli" && (pSign.includes("Leo") || pSign.includes("Simha")) && pDeg >= 3.0 && pDeg <= 9.0) {
        conjoined.push(`${pName} (${pDeg.toFixed(1)}° Leo)`);
      } else if (ns.name === "Antares" && (pSign.includes("Sagittarius") || pSign.includes("Dhanus")) && pDeg >= 5.0 && pDeg <= 11.0) {
        conjoined.push(`${pName} (${pDeg.toFixed(1)}° Sagittarius)`);
      }
    }
    if (conjoined.length > 0) prox = true;
    return {
      name: ns.name,
      zodiac_degree: ns.zodiac_degree,
      pathological_focus: ns.pathological_focus,
      esoteric_mitigation: ns.esoteric_mitigation,
      native_chart_proximity: prox,
      chart_details: conjoined.length > 0 ? `Natal presence: ${conjoined.join(", ")}. Ocular awareness advised.` : "No natal planets conjoined this nebular spot.",
    };
  });

  // 7. Aphorisms
  const aphorisms: HeindelAphorism[] = HEINDEL_APHORISMS_RAW.map((a: any) => ({
    number: a.number,
    category: a.category,
    aphorism_en: a.aphorism_en,
    aphorism_ta: a.aphorism_ta,
    practical_implication: a.practical_implication,
  }));

  // 8. Evaluated Rules
  const matchedRules: MedicalRule[] = [
    {
      id: "heindel_saturn_in_cancer",
      name: "Saturn in Cancer (Fall) - Stomach Dehydration & Reflex Kidney/Joint Impairment",
      name_tamil: "கடகத்தில் சனி (நீச்ச ஆதிக்கம்) - இரைப்பை வறட்சி & சிறுநீரக/மூட்டு உபாதைகள்",
      source: "Astro-Diagnosis: A Guide to Healing (Max Heindel)",
      chapter_verse: "Chapter I & III: The Cardinal Vicious Circle",
      category: "Vedic Birth Chart",
      system: "vedic",
      required_placements: "Saturn in Cancer (4th zodiac sign)",
      mandatory_conditions: ["Saturn occupies Cancer"],
      traditional_interpretation: "Cancer rules stomach and peristalsis. Saturn in Cancer robs organs of fluids, producing food cravings. By reflex action through the Cardinal Cross, this impairs kidneys (Libra) and stiffens knees (Capricorn).",
      interpretation_tamil: "கடகத்தில் சனி அமைவது இரைப்பையின் செரிமானத் திரவங்களை வற்றச் செய்து அஜீரணத்தை உண்டாக்குகிறது. இது துலாம் ராசி சிறுநீரகங்களையும் மகர ராசி மூட்டுகளையும் பாதிக்கும்.",
      anatomical_system: "Gastric Peristalsis, Kidneys, and Knees",
      is_active: satSign === 4,
      status: satSign === 4 ? "Qualifying" : "Not Qualifying",
      triggered_positions: satSign === 4 ? [`Saturn in Cancer in House ${satH}`] : [],
      planets_involved: ["Saturn"],
      relevant_houses: [satH, 4],
      conditions: [{ condition: "Saturn in Cancer", passed: satSign === 4, detail: `Saturn in Sign ${satSign}` }],
      remedy_en: "Cultivate frugal diet, strictly reduce refined sugars/pastries, and hydrate regularly.",
      remedy_ta: "சுத்திகரிக்கப்பட்ட சர்க்கரை மற்றும் இனிப்புகளைத் தவிர்த்து, எளிய இயற்கை உணவுகளையும் நீரையும் அருந்துதல்.",
    },
    {
      id: "heindel_saturn_in_6th",
      name: "Saturn in 6th House - Lowered Vitality & Lingering Complaints",
      name_tamil: "6-ம் வீட்டில் சனி - பிராண சக்தி குறைவு & நாள்பட்ட மந்தமான உபாதைகள்",
      source: "Astro-Diagnosis: A Guide to Healing (Max Heindel)",
      chapter_verse: "Chapter VI & Aphorism 15",
      category: "Vedic House Lord",
      system: "vedic",
      required_placements: "Saturn posited in 6th House from Lagna",
      mandatory_conditions: ["Saturn in 6th House"],
      traditional_interpretation: "Saturn in the 6th house persistently lowers constitutional vitality, causing illnesses to linger obstinately.",
      interpretation_tamil: "6-ம் பாவத்தில் சனி அமைவது உடலின் பிராண சக்தியை மட்டுப்படுத்துகிறது. நோய் எளிதில் விலகாமல் இழுத்தடிக்கும்.",
      anatomical_system: "Constitutional Immunity & Vagus Nerve",
      is_active: satH === 6,
      status: satH === 6 ? "Qualifying" : "Not Qualifying",
      triggered_positions: satH === 6 ? ["Saturn in 6th House"] : [],
      planets_involved: ["Saturn"],
      relevant_houses: [6],
      conditions: [{ condition: "Saturn in 6th House", passed: satH === 6, detail: `Saturn in House ${satH}` }],
      remedy_en: "Brisk friction baths with rough gloves to stimulate circulation; warmth, sun, and active walks.",
      remedy_ta: "குளியலின் போது கரடுமுரடான துணியால் உடலைத் தேய்த்து இரத்த ஓட்டத்தை அதிகரித்தல்; நடைப்பயிற்சி.",
    },
    {
      id: "heindel_sun_in_6th",
      name: "Sun in 6th House - Obstruction of Solar Life-Fluid",
      name_tamil: "6-ம் வீட்டில் சூரியன் - பிராண சக்தி ஓட்டத்தடை & நீண்ட நலிவுத்தன்மை",
      source: "The Message of the Stars (Max Heindel)",
      chapter_verse: "Chapter VIII: The Sun in the Sixth House",
      category: "Vedic Birth Chart",
      system: "vedic",
      required_placements: "Sun in 6th House from Lagna",
      mandatory_conditions: ["Sun in 6th House"],
      traditional_interpretation: "Sun in 6th house confines the solar vitality, making the native slow to recuperate from illness unless strong benefics assist.",
      interpretation_tamil: "சூரியன் 6-ம் வீட்டில் அமையும் போது ஜீவ சக்தி மட்டுப்படுகிறது; நோய் வந்தால் குணமடைய நீண்ட காலம் எடுக்கும்.",
      anatomical_system: "Solar Vital Fluid & Cellular Regeneration",
      is_active: sunH === 6,
      status: sunH === 6 ? "Qualifying" : "Not Qualifying",
      triggered_positions: sunH === 6 ? ["Sun in 6th House"] : [],
      planets_involved: ["Sun"],
      relevant_houses: [6],
      conditions: [{ condition: "Sun in 6th House", passed: sunH === 6, detail: `Sun in House ${sunH}` }],
      remedy_en: "Daily Surya Namaskar at sunrise, pranayama, and light nourishing diet.",
      remedy_ta: "அதிகாலை சூரிய நமஸ்காரம், பிராணாயாமப் பயிற்சிகள் மற்றும் எளிய சத்தான உணவுகள்.",
    },
    {
      id: "heindel_sun_in_8th",
      name: "Sun in 8th House - Life-Giver in the House of Death-Dealing Forces",
      name_tamil: "8-ம் வீட்டில் சூரியன் - ஆயுள் காரகன் மரண பாவத்தில் அமைதல்",
      source: "The Message of the Stars (Max Heindel)",
      chapter_verse: "Chapter VIII: The Sun in the Eighth House",
      category: "Vedic Birth Chart",
      system: "vedic",
      required_placements: "Sun in 8th House from Lagna",
      mandatory_conditions: ["Sun in 8th House"],
      traditional_interpretation: "Sun in the 8th house places vitality under severe testing, requiring mindful conservation of physical resources.",
      interpretation_tamil: "8-ம் பாவம் ஆயுள் போராட்ட பாவமாகும்; அங்கு சூரியன் அமர்வது உயிர் சக்தியை சோதனைகளுக்கு உள்ளாக்குகிறது.",
      anatomical_system: "Core Vital Reserve & Autonomic Homeostasis",
      is_active: sunH === 8,
      status: sunH === 8 ? "Qualifying" : "Not Qualifying",
      triggered_positions: sunH === 8 ? ["Sun in 8th House"] : [],
      planets_involved: ["Sun"],
      relevant_houses: [8],
      conditions: [{ condition: "Sun in 8th House", passed: sunH === 8, detail: `Sun in House ${sunH}` }],
      remedy_en: "Cultivate tranquil living, avoid rash hazards, chant Aditya Hridaya Stotram daily.",
      remedy_ta: "ஆதித்ய ஹிருதய ஸ்தோத்திரம் பாராயணம் செய்தல்; அமைதியான நல்வாழ்வு முறை.",
    },
    {
      id: "heindel_sun_mars_fiery_fever",
      name: "Sun-Mars Conjunction / Fiery Connection - High Fevers & Inflammatory Endurance",
      name_tamil: "சூரியன்-செவ்வாய் சேர்க்கை - அதீத உஷ்ணக் காய்ச்சல் & எதிர்ப்புத்திறன்",
      source: "Astro-Diagnosis: A Guide to Healing (Max Heindel)",
      chapter_verse: "Chapter I & Aphorism 25",
      category: "Vedic Conjunction/Aspect",
      system: "vedic",
      required_placements: "Sun and Mars conjoined, or Mars in fire sign with Sun",
      mandatory_conditions: ["Sun and Mars conjoined or in Fire signs"],
      traditional_interpretation: "Sun and Mars in fire signs produce super-abundance of vital energy. Fevers rise rapidly 3-4 degrees higher, yet native endures high temperatures.",
      interpretation_tamil: "சூரியன்-செவ்வாய் சேர்க்கை இரத்த நாளங்களில் கொதிப்பை உண்டாக்கி, காய்ச்சல் வந்தால் அதிக வெப்பத்தை ஏற்படுத்தும்.",
      anatomical_system: "Arterial Pressure, Thermoregulation, Motor Cortex",
      is_active: sunH === marsH || [4, 8].includes(Math.abs(sunH - marsH)),
      status: (sunH === marsH || [4, 8].includes(Math.abs(sunH - marsH))) ? "Qualifying" : "Not Qualifying",
      triggered_positions: (sunH === marsH || [4, 8].includes(Math.abs(sunH - marsH))) ? [`Sun in H${sunH}, Mars in H${marsH}`] : [],
      planets_involved: ["Sun", "Mars"],
      relevant_houses: [sunH, marsH],
      conditions: [{ condition: "Sun-Mars connection", passed: sunH === marsH, detail: `Sun H${sunH}, Mars H${marsH}` }],
      remedy_en: "Copper-charged water, cooling coconut water, avoiding red meat and hot spices.",
      remedy_ta: "வெட்டிவேர் மற்றும் சீரக நீர், இளநீர் பருகுதல்; கார உணவுகளைத் தவிர்த்தல்.",
    },
    {
      id: "heindel_mercury_saturn_melancholy",
      name: "Mercury Afflicted by Saturn - Nervous Melancholy & Chronic Pessimism",
      name_tamil: "புதன்-சனி பாதிப்பு - நரம்புத் தளர்ச்சி & மனச்சோர்வு",
      source: "Astro-Diagnosis: A Guide to Healing (Max Heindel)",
      chapter_verse: "Chapter V & Aphorism 39",
      category: "Vedic Conjunction/Aspect",
      system: "vedic",
      required_placements: "Mercury conjunct, square, or opposite Saturn",
      mandatory_conditions: ["Mercury afflicted by Saturn"],
      traditional_interpretation: "Mercury afflicted by Saturn produces a mind subject to melancholia and morbid worry. Room must be sunny with rose-colored walls.",
      interpretation_tamil: "புதன்-சனி பாதிப்பு நரம்பு சோர்வு, மனக்கவலை மற்றும் அவநம்பிக்கையை உண்டாக்கும். ரோஸ் நிற சுவர்கள் கொண்ட வெளிச்ச அறை நலம் தரும்.",
      anatomical_system: "Central Nervous System & Sensory Nerves",
      is_active: mercH === satH || Math.abs(mercH - satH) === 6 || [3, 9].includes(Math.abs(mercH - satH)),
      status: (mercH === satH || Math.abs(mercH - satH) === 6 || [3, 9].includes(Math.abs(mercH - satH))) ? "Qualifying" : "Not Qualifying",
      triggered_positions: [`Mercury H${mercH}, Saturn H${satH}`],
      planets_involved: ["Mercury", "Saturn"],
      relevant_houses: [mercH, satH],
      conditions: [{ condition: "Mercury-Saturn aspect", passed: mercH === satH, detail: `Merc H${mercH}, Sat H${satH}` }],
      remedy_en: "Rose chromotherapy, joyful companionship, listening to rhythmic uplifting music.",
      remedy_ta: "ரோஸ் நிற ஒளி சிகிச்சை, நேர்மறை சிந்தனையாளர்களின் நட்பு, இனிமையான சங்கீதம் கேட்டல்.",
    },
    {
      id: "heindel_venus_scorpio_fall",
      name: "Venus in Scorpio - Generative Vitality Sapping & Sensual Thermal Strain",
      name_tamil: "விருச்சிகத்தில் சுக்கிரன் - பிறப்புறுப்பு நலிவு & உணர்ச்சிவசப்பட்ட பிராண விரயம்",
      source: "The Message of the Stars (Max Heindel)",
      chapter_verse: "Chapter IX: Venus in the Twelve Signs",
      category: "Vedic Birth Chart",
      system: "vedic",
      required_placements: "Venus in Scorpio (8th sign)",
      mandatory_conditions: ["Venus in Scorpio"],
      traditional_interpretation: "Venus in Scorpio blends love with martial passion, sapping vitality if desires are uncurbed. Sublimation into devotion and art is essential.",
      interpretation_tamil: "சுக்கிரன் விருச்சிகத்தில் அமைவது காம உணர்வுகளைத் தூண்டி உயிர் சக்தியை விரயமாக்கலாம்; பக்தி மற்றும் கலைகளில் மனதைச் செலுத்த வேண்டும்.",
      anatomical_system: "Generative Organs, Prostate, Ovaries",
      is_active: venSign === 8,
      status: venSign === 8 ? "Qualifying" : "Not Qualifying",
      triggered_positions: venSign === 8 ? [`Venus in Scorpio in House ${venH}`] : [],
      planets_involved: ["Venus"],
      relevant_houses: [venH],
      conditions: [{ condition: "Venus in Scorpio", passed: venSign === 8, detail: `Venus in Sign ${venSign}` }],
      remedy_en: "Practice sensory self-mastery, sublimate creative energies into fine arts and selfless devotion.",
      remedy_ta: "சுய ஒழுக்கம், கலைகள் மற்றும் ஆன்மீக பக்தி வழியே உணர்ச்சி வேகங்களை நல்வழிப்படுத்துதல்.",
    },
    {
      id: "heindel_common_signs_angular_vitality",
      name: "Common Signs on the Four Angles - Wavering Willpower & Chronic Relapse Vulnerability",
      name_tamil: "நான்கு கேந்திரங்களில் உபய ராசிகள் - பலவீனமான மன உறுதி & நோய் மீள்தன்மை",
      source: "Astro-Diagnosis: A Guide to Healing (Max Heindel)",
      chapter_verse: "Chapter VII & Aphorism 23",
      category: "Vedic Birth Chart",
      system: "vedic",
      required_placements: "Common signs (Gemini, Virgo, Sagittarius, Pisces) on the 4 angles",
      mandatory_conditions: ["Ascendant is Gemini, Virgo, Sagittarius, or Pisces"],
      traditional_interpretation: "When common signs occupy the 4 angles, the native's willpower wavers under illness. They easily absorb adverse suggestions from visitors.",
      interpretation_tamil: "லக்னம் உள்ளிட்ட நான்கு கேந்திரங்களிலும் உபய ராசிகள் அமைந்தால் மன உறுதி எளிதில் அலைபாயும்; ஊக்கமளிக்கும் சூழல் தேவை.",
      anatomical_system: "Psychosomatic Willpower & Neuro-Immune Axis",
      is_active: [3, 6, 9, 12].includes(lagnaSign),
      status: [3, 6, 9, 12].includes(lagnaSign) ? "Qualifying" : "Not Qualifying",
      triggered_positions: [3, 6, 9, 12].includes(lagnaSign) ? [`Ascendant in Common Sign ${lagnaSign}`] : [],
      planets_involved: [],
      relevant_houses: [1, 4, 7, 10],
      conditions: [{ condition: "Common signs on 4 angles", passed: [3, 6, 9, 12].includes(lagnaSign), detail: `Lagna in Sign ${lagnaSign}` }],
      remedy_en: "Shield the patient from gloomy visitors; provide daily structured lifestyle routines.",
      remedy_ta: "நோயாளியிடம் நோய் பற்றிப் பேசும் மனிதர்களைத் தவிர்ப்பது; ஒழுங்கான நல்வாழ்வு அட்டவணை.",
    },
    {
      id: "heindel_fixed_signs_angles_resilience",
      name: "Fixed Signs on the Four Angles - Formidable Stamina & Disease Resistance",
      name_tamil: "நான்கு கேந்திரங்களில் ஸ்திர ராசிகள் - அசாத்திய மன உறுதி & நோய் எதிர்ப்பு பலம்",
      source: "Astro-Diagnosis: A Guide to Healing (Max Heindel)",
      chapter_verse: "Chapter VII & The Message of the Stars",
      category: "Vedic Mitigation",
      system: "vedic",
      required_placements: "Fixed signs (Taurus, Leo, Scorpio, Aquarius) on the 4 angles",
      mandatory_conditions: ["Ascendant is Taurus, Leo, Scorpio, or Aquarius"],
      traditional_interpretation: "When fixed signs occupy the angles, the native possesses iron determination and great physical stamina to overcome lingering illnesses.",
      interpretation_tamil: "கேந்திரங்களில் ஸ்திர ராசிகள் அமைவது இரும்பு போன்ற மன உறுதியையும் உடலின் அசாத்திய நோய் எதிர்ப்புத் திறனையும் தரும்.",
      anatomical_system: "Skeletal Stamina & Immune Resilience",
      is_active: [2, 5, 8, 11].includes(lagnaSign),
      status: [2, 5, 8, 11].includes(lagnaSign) ? "Qualifying" : "Not Qualifying",
      triggered_positions: [2, 5, 8, 11].includes(lagnaSign) ? [`Ascendant in Fixed Sign ${lagnaSign}`] : [],
      planets_involved: [],
      relevant_houses: [1, 4, 7, 10],
      conditions: [{ condition: "Fixed signs on 4 angles", passed: [2, 5, 8, 11].includes(lagnaSign), detail: `Lagna in Sign ${lagnaSign}` }],
      remedy_en: "Harness natural persistence towards constructive healing habits and physical exercise.",
      remedy_ta: "இயற்கையான மன உறுதியைக் கொண்டு உடற்பயிற்சி மற்றும் நற்பழக்கங்களை உறுதியாகப் பின்பற்றுதல்.",
    },
  ];

  return {
    book_title: HEINDEL_METADATA.book_title,
    book_title_ta: HEINDEL_METADATA.book_title_ta,
    authors: HEINDEL_METADATA.authors,
    historical_foundation: HEINDEL_METADATA.historical_foundation,
    core_philosophy_en: HEINDEL_METADATA.core_philosophy_en,
    core_philosophy_ta: HEINDEL_METADATA.core_philosophy_ta,
    healer_injunctions: HEINDEL_METADATA.healer_injunctions,
    signs_anatomy: signsAnatomy,
    planets_physiology: planetsPhysiology,
    sense_organs_affinities: HEINDEL_SENSE_ORGANS_RAW,
    vicious_circles: viciousCircles,
    nail_and_hand_diagnosis: nailDiagnosis,
    planetary_antidotes: planetaryAntidotes,
    nebular_spots: nebularSpots,
    aphorisms: aphorisms,
    chart_evaluation: {
      lagna_sign: lagnaSign,
      sun_sign: sunSign,
      moon_sign: moonSign,
      active_rules_count: matchedRules.filter((r) => r.is_active).length,
    },
    matched_rules: matchedRules,
  };
}



// ---------------------------------------------------------------------------
// Jane Ridder-Patrick: A Handbook of Medical Astrology Raw Data
// ---------------------------------------------------------------------------

const JANE_METADATA_RAW = {
  "book_title": "A Handbook of Medical Astrology (Second Edition, Revised and Enlarged)",
  "book_title_ta": "மருத்துவ ஜோதிட கையேடு (இரண்டாம் பதிப்பு - ஜேன் ரிடர்-பேட்ரிக்)",
  "author": "Jane Ridder-Patrick, Ph.D., N.D., M.N.I.M.H.",
  "author_credentials": "Practising Pharmacist, Medical Herbalist, Naturopath, and Astrologer (Edinburgh, Scotland)",
  "publisher": "CrabApple Press, Edinburgh (ISBN 978 0 9551989 0 8)",
  "foreword_by": "Charles Harvey, Past President of the Astrological Association of Great Britain",
  "philosophical_motto": "Let it be stated here once and for all that we are not dealing with symbols but activities, are not instituting metaphorical allusions but commenting upon urgent forces, quite capable of practical demonstration. — Heinrich Daath",
  "alphabet_framework": {
    "Planets": "WHAT is happening — action, physiological processes in the body (the verbs)",
    "Signs": "WHERE these processes take place — location, structure, anatomy (the adjectives/adverbs)",
    "Aspects": "HOW planets modify the physiological processes of other planets",
    "Houses": "WHICH external and environmental factors affect health",
    "Transits_Progressions": "WHEN — timing of onset, crisis, remission, and recurrence of health problems"
  },
  "three_factors_of_disease": {
    "1_disease_potential": "Natal chart vulnerability: without natal significators, a disease will never manifest.",
    "2_conducive_conditions": "Physical, emotional, mental hygiene and the presence/absence of internal/external toxins.",
    "3_triggers": "Transits and progressions activating chart potential at 3 levels: Inner Mind, Outer Events, or Physical Body."
  }
};

const JANE_THREE_CROSSES_RAW = [
  {
    "cross": "Cardinal Cross",
    "cross_ta": "சர ராசிகள் (மேஷம், கடகம், துலாம், மகரம்)",
    "theme": "Regulation, Structure and Protection",
    "systems": "Skin, Skeletal, Endocrine and Immune systems",
    "reflex_dynamics": "Aries (Adrenals) -> Libra (Kidneys/Blood sugar/Sodium balance) -> Cancer (Body water/Mucous membranes) -> Capricorn (Anterior Pituitary/Bones/Skin). Disorders in one sign reflexly trigger symptoms across the cross.",
    "therapeutic_focus": "Endocrine harmony, fluid homeostasis, skeletal density, and pituitary-adrenal balance."
  },
  {
    "cross": "Fixed Cross",
    "cross_ta": "ஸ்திர ராசிகள் (ரிஷபம், சிம்மம், விருச்சிகம், கும்பம்)",
    "theme": "Vital Functions & Accumulation",
    "systems": "Cardiovascular, Reproductive, Excretory systems & Reptilian Brain",
    "reflex_dynamics": "Taurus (Throat/Thyroid) <-> Scorpio (Colon/Reproductive organs); Leo (Heart/Spine) <-> Aquarius (Calf venous pump/Corticospinal tract). Tends toward cellular proliferation, stones, and tissue engorgement.",
    "therapeutic_focus": "Cardiovascular circulation, metabolic detox, lower bowel regularity, and anti-engorgement."
  },
  {
    "cross": "Mutable Cross",
    "cross_ta": "உபய ராசிகள் (மிதுனம், கன்னி, தனுசு, மீனம்)",
    "theme": "Metabolic Cross: Change and Exchange",
    "systems": "Respiratory, Digestive, and Nervous systems (Least robust, body mediators)",
    "reflex_dynamics": "Gemini (Tubes, lungs, peripheral nerves) <-> Sagittarius (Locomotion, cerebral cortex, higher integration); Virgo (Enteric belly brain, digestion, enzymes) <-> Pisces (Lymphatic, pineal, immune boundary dissolution).",
    "therapeutic_focus": "Nervous regulation, digestive enzyme support (naturopathy), and emotional boundary consolidation."
  }
];

const JANE_CELL_SALTS_RAW = [
  {
    "sign": "Aries",
    "sign_ta": "மேஷம்",
    "cell_salt": "Potassium phosphate",
    "abbreviation": "Kali. phos.",
    "action_en": "Brain and nerve nutrient, relieves mental exhaustion, tension headaches.",
    "action_ta": "மூளை மற்றும் நரம்பு ஊட்டச்சத்து, மன உளைச்சல் தலைவலியைப் போக்கும்."
  },
  {
    "sign": "Taurus",
    "sign_ta": "ரிஷபம்",
    "cell_salt": "Sodium sulphate",
    "abbreviation": "Nat. sulph.",
    "action_en": "Liver and water eliminator, supports bile flow, relieves biliousness.",
    "action_ta": "கல்லீரல் மற்றும் நீர் கழிவு நீக்கி, பித்த ஓட்டத்தை சீராக்கும்."
  },
  {
    "sign": "Gemini",
    "sign_ta": "மிதுனம்",
    "cell_salt": "Potassium chloride",
    "abbreviation": "Kali. mur.",
    "action_en": "Respiratory and glandular decongestant, clears bronchial phlegm and fibrinous exudates.",
    "action_ta": "சுவாச மற்றும் நிணநீர் சளி நீக்கி, மூச்சுக்குழாய் அடைப்பை அகற்றும்."
  },
  {
    "sign": "Cancer",
    "sign_ta": "கடகம்",
    "cell_salt": "Calcium fluoride",
    "abbreviation": "Calc. fluor.",
    "action_en": "Elastic tissue and vascular toner, maintains stomach elasticity, prevents vein laxity.",
    "action_ta": "திசு நெகிழ்ச்சி மற்றும் இரத்தக்குழாய் வலுவூட்டி, வீங்கி பருத்த நரம்புகளைத் தடுக்கும்."
  },
  {
    "sign": "Leo",
    "sign_ta": "சிம்மம்",
    "cell_salt": "Magnesium phosphate",
    "abbreviation": "Mag. phos.",
    "action_en": "Muscular and antispasmodic salt, relieves cardiac tension, muscle spasms and cramps.",
    "action_ta": "தசை பிடிப்பு நிவாரணி, இதய தசை மற்றும் நரம்பு இறுக்கத்தைத் தளர்த்தும்."
  },
  {
    "sign": "Virgo",
    "sign_ta": "கன்னி",
    "cell_salt": "Potassium sulphate",
    "abbreviation": "Kali. sulph.",
    "action_en": "Skin and mucous membrane oxygen carrier, supports enteric digestion and enzyme balance.",
    "action_ta": "தோல் மற்றும் சளிச்சவ்வு பிராணவாயு கடத்தி, செரிமான என்சைம்களை சீராக்கும்."
  },
  {
    "sign": "Libra",
    "sign_ta": "துலாம்",
    "cell_salt": "Sodium phosphate",
    "abbreviation": "Nat. phos.",
    "action_en": "Acid-base neutralizer, prevents lactic and uric acid accumulation, supports kidneys.",
    "action_ta": "அமில-கார சமநிலைப்படுத்தி, யூரிக் அமில தேக்கத்தைத் தடுத்து சிறுநீரகத்தை காக்கும்."
  },
  {
    "sign": "Scorpio",
    "sign_ta": "விருச்சிகம்",
    "cell_salt": "Calcium sulphate",
    "abbreviation": "Calc. sulph.",
    "action_en": "Cellular cleanser and purifier, heals suppurating wounds, boils, and clears colon wastes.",
    "action_ta": "உயிரணு கழிவகற்றி, சீழ் பிடித்த கட்டிகளை குணமாக்கி குடல் நச்சுக்களை நீக்கும்."
  },
  {
    "sign": "Sagittarius",
    "sign_ta": "தனுசு",
    "cell_salt": "Silicon oxide",
    "abbreviation": "Silica",
    "action_en": "Connective tissue cleanser and strengthener, gives tensile strength to joints and nerve sheaths.",
    "action_ta": "இணைப்பு திசு வலுவூட்டி, மூட்டுகள் மற்றும் நரம்பு உறைகளுக்கு நெகிழ்வுத்தன்மை தரும்."
  },
  {
    "sign": "Capricorn",
    "sign_ta": "மகரம்",
    "cell_salt": "Calcium phosphate",
    "abbreviation": "Calc. phos.",
    "action_en": "Bone and skeletal builder, essential for tooth dentine, joint repair, and convalescence.",
    "action_ta": "எலும்பு மற்றும் எலும்புக்கூடு கட்டமைப்பாளர், பற்கள் மற்றும் மூட்டு தேய்மானத்தை சீராக்கும்."
  },
  {
    "sign": "Aquarius",
    "sign_ta": "கும்பம்",
    "cell_salt": "Sodium chloride",
    "abbreviation": "Nat. mur.",
    "action_en": "Osmotic fluid distributor, regulates hydration of cells and blood circulation in lower limbs.",
    "action_ta": "செல்லுலார் நீர் சமநிலைப் படுத்தி, கால் நரம்புகள் மற்றும் ரத்த ஓட்டத்தை சீராக்கும்."
  },
  {
    "sign": "Pisces",
    "sign_ta": "மீனம்",
    "cell_salt": "Iron phosphate",
    "abbreviation": "Ferr. phos.",
    "action_en": "Oxygen carrier and anti-inflammatory, relieves early stages of fever, congestion and chills.",
    "action_ta": "ஆக்சிஜன் கடத்தி மற்றும் அழற்சி எதிர்ப்பு உப்பு, காய்ச்சல் மற்றும் சளி தொற்றை நீக்கும்."
  }
];

const JANE_BACH_FLOWERS_RAW = [
  {
    "sign": "Aries",
    "sign_ta": "மேஷம்",
    "flower": "Impatiens",
    "action_en": "For impatience, tension, irritability, and driving body beyond limits.",
    "action_ta": "பொறுமையின்மை, எரிச்சல் மற்றும் உடலை வருத்தும் அவசர நிலையைத் தணிக்கும்."
  },
  {
    "sign": "Taurus",
    "sign_ta": "ரிஷபம்",
    "flower": "Gentian",
    "action_en": "For discouragement, despondency, and resistance to unexpected bodily changes.",
    "action_ta": "மனச்சோர்வு, நம்பிக்கை இழப்பு மற்றும் மாற்றங்களை ஏற்க மறுக்கும் மனதை மாற்றும்."
  },
  {
    "sign": "Gemini",
    "sign_ta": "மிதுனம்",
    "flower": "Cerato",
    "action_en": "For doubting one's inner voice, mental vacillation, and sensory distraction.",
    "action_ta": "தன் சுய உள்ளுணர்வை நம்பாமை மற்றும் சிதறும் கவனத்தை ஒருமுகப்படுத்தும்."
  },
  {
    "sign": "Cancer",
    "sign_ta": "கடகம்",
    "flower": "Clematis",
    "action_en": "For ungrounded daydreaming, withdrawal into shell, and fluid sluggishness.",
    "action_ta": "கனவுலகில் வாழ்தல், நிஜத்தை எதிர்கொள்ள தயங்குதல் மற்றும் மந்தநிலையை அகற்றும்."
  },
  {
    "sign": "Leo",
    "sign_ta": "சிம்மம்",
    "flower": "Vervain",
    "action_en": "For over-enthusiasm, stress from over-exertion, and driving the heart too hard.",
    "action_ta": "அளவுக்கு மிஞ்சிய வைராக்கியம், இதயத்தை வருத்தும் அதீத உழைப்பை சமநிலைப்படுத்தும்."
  },
  {
    "sign": "Virgo",
    "sign_ta": "கன்னி",
    "flower": "Centaury",
    "action_en": "For inability to say 'no', anxious over-service, and psychosomatic gut strain.",
    "action_ta": "'முடியாது' என மறுக்க முடியாமல் பிறருக்கு உழைத்து குடல் சோர்வு அடைவதைத் தடுக்கும்."
  },
  {
    "sign": "Libra",
    "sign_ta": "துலாம்",
    "flower": "Scleranthus",
    "action_en": "For indecision, emotional mood swings, and erratic fluctuating kidney/hormone tone.",
    "action_ta": "முடிவெடுக்க இயலாமை, ஊசலாடும் மனநிலை மற்றும் ஹார்மோன் சமநிலையின்மையை சீராக்கும்."
  },
  {
    "sign": "Scorpio",
    "sign_ta": "விருச்சிகம்",
    "flower": "Chicory",
    "action_en": "For possessiveness, holding on to old resentments, and colon congestion.",
    "action_ta": "பற்றுதல், பழைய கோபங்களை அடக்கி வைத்தல் மற்றும் கழிவுத் தேக்கத்தை போக்கும்."
  },
  {
    "sign": "Sagittarius",
    "sign_ta": "தனுசு",
    "flower": "Agrimony",
    "action_en": "For hiding inner pain behind a cheerful face, restlessness, and reckless stress.",
    "action_ta": "மனக்கவலையை சிரித்த முகத்திற்குள் மறைத்தல் மற்றும் அமைதியின்மையை போக்கும்."
  },
  {
    "sign": "Capricorn",
    "sign_ta": "மகரம்",
    "flower": "Mimulus",
    "action_en": "For fear of worldly failure, chronic anxiety, joint stiffness, and cold depression.",
    "action_ta": "தோல்வி பயம், வாழ்வியல் அச்சம், மூட்டு விறைப்பு மற்றும் மன அழுத்தத்தை நீக்கும்."
  },
  {
    "sign": "Aquarius",
    "sign_ta": "கும்பம்",
    "flower": "Water Violet",
    "action_en": "For proud aloofness, nervous tension, feeling disconnected from human warmth.",
    "action_ta": "தனிமை விரும்புதல், நரம்பு அதிர்வு மற்றும் சமூக பற்றுதலற்ற இறுக்கத்தை தளர்த்தும்."
  },
  {
    "sign": "Pisces",
    "sign_ta": "மீனம்",
    "flower": "Rock Rose",
    "action_en": "For acute panic, terror, psychic over-sensitivity, and immune collapse.",
    "action_ta": "திடீர் பீதி, பயம், அதிகப்படியான உணர்திறன் மற்றும் நோய் எதிர்ப்பு தளர்ச்சியை நீக்கும்."
  }
];

const JANE_ACUPUNCTURE_MERIDIANS_RAW = [
  {
    "sign": "Aries",
    "sign_ta": "மேஷம்",
    "meridian": "Kidney Meridian",
    "meridian_ta": "சிறுநீரக மெரிடியன்"
  },
  {
    "sign": "Taurus",
    "sign_ta": "ரிஷபம்",
    "meridian": "Triple Warmer Meridian",
    "meridian_ta": "மூவெப்ப கட்டுப்பாட்டு மெரிடியன்"
  },
  {
    "sign": "Gemini",
    "sign_ta": "மிதுனம்",
    "meridian": "Liver Meridian",
    "meridian_ta": "கல்லீரல் மெரிடியன்"
  },
  {
    "sign": "Cancer",
    "sign_ta": "கடகம்",
    "meridian": "Stomach Meridian",
    "meridian_ta": "இரைப்பை மெரிடியன்"
  },
  {
    "sign": "Leo",
    "sign_ta": "சிம்மம்",
    "meridian": "Heart Meridian",
    "meridian_ta": "இதய மெரிடியன்"
  },
  {
    "sign": "Virgo",
    "sign_ta": "கன்னி",
    "meridian": "Large Intestine Meridian",
    "meridian_ta": "பெருங்குடல் மெரிடியன்"
  },
  {
    "sign": "Libra",
    "sign_ta": "துலாம்",
    "meridian": "Circulation-Sexuality (Pericardium) Meridian",
    "meridian_ta": "இதய உறை / பாலியல் மெரிடியன்"
  },
  {
    "sign": "Scorpio",
    "sign_ta": "விருச்சிகம்",
    "meridian": "Bladder Meridian",
    "meridian_ta": "சிறுநீர்ப்பை மெரிடியன்"
  },
  {
    "sign": "Sagittarius",
    "sign_ta": "தனுசு",
    "meridian": "Pancreas-Spleen Meridian",
    "meridian_ta": "கணையம்-மண்ணீரல் மெரிடியன்"
  },
  {
    "sign": "Capricorn",
    "sign_ta": "மகரம்",
    "meridian": "Gall Bladder Meridian",
    "meridian_ta": "பித்தப்பை மெரிடியன்"
  },
  {
    "sign": "Aquarius",
    "sign_ta": "கும்பம்",
    "meridian": "Lung Meridian",
    "meridian_ta": "நுரையீரல் மெரிடியன்"
  },
  {
    "sign": "Pisces",
    "sign_ta": "மீனம்",
    "meridian": "Small Intestine Meridian",
    "meridian_ta": "சிறுகுடல் மெரிடியன்"
  }
];

const JANE_CULPEPER_RULES_RAW = [
  {
    "rule_number": "1",
    "rule_en": "Fortify the body with herbs of the nature of the Lord of the Ascendant, 'tis no matter whether he be a Fortune or Infortune in this case.",
    "rule_ta": "லக்னாதிபதியின் தன்மை கொண்ட மூலிகைகளால் உடலை வலுப்படுத்த வேண்டும்; அவர் சுபரோ அல்லது அசுபரோ என்பது இங்கு முக்கியமல்ல.",
    "application": "Reinforces native constitution and vitality through Ascendant lord's botanical affinities."
  },
  {
    "rule_number": "2",
    "rule_en": "Let your medicine be something antipathetical to the Lord of the Sixth.",
    "rule_ta": "உங்கள் மருந்து 6-ஆம் அதிபதியின் தன்மைக்கு எதிர்நிலையானதாக (முரண்பட்டதாக) இருக்க வேண்டும்.",
    "application": "Doctrine of contraries: opposes the pathogenic influence generating the ailment."
  },
  {
    "rule_number": "3",
    "rule_en": "Let your medicine be something of the nature of the sign ascending.",
    "rule_ta": "உங்கள் மருந்து உதயமாகும் லக்ன ராசியின் இயல்புக்கு ஒத்ததாக இருக்க வேண்டும்.",
    "application": "Nourishes the physical form and elemental temperament of the rising sign."
  },
  {
    "rule_number": "4",
    "rule_en": "If the Lord of the Tenth be strong make use of his medicines.",
    "rule_ta": "10-ஆம் அதிபதி வலுவாக இருப்பின், அவரது ஆதிக்கத்திற்குரிய மருந்துகளைப் பயன்படுத்தவும்.",
    "application": "The 10th house is the house of the physician and medicine; its strong lord guarantees therapeutic efficacy."
  },
  {
    "rule_number": "5",
    "rule_en": "If this cannot well be make use of the medicines of the Light of Time [Sun by day, Moon by night].",
    "rule_ta": "இது சாத்தியமில்லை எனில், காலத்தின் ஒளியான கிரகத்தின் (பகலில் சூரியன், இரவில் சந்திரன்) மருந்துகளைப் பயன்படுத்தவும்.",
    "application": "Draws upon diurnal solar vitality or nocturnal lunar fluid nourishment."
  },
  {
    "rule_number": "6",
    "rule_en": "Be sure always to fortify the grieved part of the body by sympathetical remedies.",
    "rule_ta": "பாதிக்கப்பட்ட உடல் உறுப்பை அதற்குரிய ஒத்த சுபாவமுள்ள (அனுதாப) மருந்துகளால் எப்போதும் தேற்ற வேண்டும்.",
    "application": "Sympathetic remedies support and nourish the specific organ in distress."
  },
  {
    "rule_number": "7",
    "rule_en": "Regard the heart, keep that upon the wheels, because the Sun is the foundation of life, and therefore universal remedies cure all diseases by fortifying the heart.",
    "rule_ta": "இதயத்தை கண்ணும் கருத்துமாகப் பாதுகாக்கவும்; ஏனெனில் சூரியனே உயிரின் ஆதாரம், இதயத்தை வலுப்படுத்துவதே அனைத்து பிணிகளையும் தீர்க்கும்.",
    "application": "Protecting the solar pump ensures oxygen and vital prana reach every tissue cell."
  }
];

const JANE_ELEMENTAL_BALANCING_RAW = {
  "Excess Air": {
    "qualities": "Light, dry, and cold (Ayurvedic Vata - 'what blows')",
    "symptoms": "Lean dry skin, rapid aging, low blood sugar, flatulence, constipation, shooting pains, creaking joints, insomnia (2am-6am), racing anxious mind.",
    "balancing_diet": "Heavy, moist, and hot foods. Dairy products (yoghurt), cooked rice, oats, warm oily vegetables, generous salad dressings, digestive warming spices.",
    "avoid": "Raw food, yeast, mushrooms, refined sugars, dry beans, excess cabbage family.",
    "indicated_herbs": "Digestive stimulants, nervine sedatives, demulcents, bulk laxatives (valerian, liquorice, marshmallow, psyllium)."
  },
  "Low Air": {
    "qualities": "Deficiency of circulation, flexibility, and nervous responsiveness",
    "symptoms": "Sluggish reflex action, poor peripheral circulation, rigid mental patterns.",
    "balancing_diet": "Light, dry, stimulating foods. Raw foods, raw vegetable juices, sprouted grains and seeds, low oil intake, small infrequent meals.",
    "avoid": "Heavy dense greasy foods.",
    "indicated_herbs": "Circulatory stimulants, nerve stimulants, bitter tonics (peppermint, tea, rosemary, gentian)."
  },
  "Excess Fire": {
    "qualities": "Hot, light, and dry (Ayurvedic Pitta - 'what cooks')",
    "symptoms": "High body temperature, reddish complexion, greasy skin, acne, voracious appetite, hyperacidity, diarrhea, irritability, aggressive drive.",
    "balancing_diet": "Cold, moist, heavy foods. Bland foods, steamed vegetables, sweet fruits, fresh milk (minimizing sour yoghurt), sweet grains.",
    "avoid": "Hot chilies, mustard, vinegar, alcohol, excessive meat, deep-fried foods.",
    "indicated_herbs": "Bitter tonics, alteratives, demulcents, cooling sedatives (burdock, dandelion root, chamomile, yarrow)."
  },
  "Low Fire": {
    "qualities": "Deficiency of digestive fire (Agni), vitality, and enthusiasm",
    "symptoms": "Cold pale skin, poor sluggish digestion, food fermentation, gas, depression, low self-esteem, weak immunity against pathogens.",
    "balancing_diet": "Hot, dry, aromatic foods. Warm whole grains cooked with oil and warming spices, ginger, garlic, onions, rock salt, frequent small meals.",
    "avoid": "Cold iced drinks, heavy dairy, raw chilled salads, refined sugar.",
    "indicated_herbs": "Digestive and circulatory stimulants (ginger, cinnamon, cayenne pepper, angelica)."
  },
  "Excess Water": {
    "qualities": "Cold, wet, and heavy (Ayurvedic Kapha - 'what sticks')",
    "symptoms": "Plump soft body, fluid retention, oedema, excess mucous in stomach/lungs, asthma, slow monotone speech, clinginess, possessiveness.",
    "balancing_diet": "Hot, dry, and light foods. Lightly cooked vegetables, beans, pungent spices, light grains (millet, barley).",
    "avoid": "Heavy oily foods, dairy, sweet foods, refined wheat, salt (which retains water), large quantities of melons.",
    "indicated_herbs": "Diaphoretics, diuretics, bitter tonics, expectorants (yarrow, cleavers, couchgrass, elderflowers)."
  },
  "Low Water": {
    "qualities": "Dehydration, stiffness, dry mucous membranes, lack of softness",
    "symptoms": "Dry brittle tissues, lack of emotional buffering, poor joint lubrication, insomnia.",
    "balancing_diet": "Juicy fruits and vegetables, judicious salt, wheat, oats, seaweed, milk, natural honey.",
    "avoid": "Strong diuretics, dry crackers, astringent unlubricated foods.",
    "indicated_herbs": "Demulcents, soothing mucilaginous herbs (liquorice, marshmallow, comfrey, slippery elm)."
  },
  "Excess Earth": {
    "qualities": "Dense, heavy, cold, and slow",
    "symptoms": "Leathery thickened skin, tissue sclerosis, calcium deposits, sluggish elimination, extreme rigidity.",
    "balancing_diet": "Light freshly cooked foods, sprouts, steamed greens, stimulating spices, no desserts.",
    "avoid": "Heavy dairy, dense meats, rich pastries, excess potatoes.",
    "indicated_herbs": "Bitter tonics, digestive and mental stimulants, purgatives (senna, aloes, gentian)."
  },
  "Low Earth": {
    "qualities": "Lack of physical stamina, grounding, and structural minerals",
    "symptoms": "Fragile bones, weak teeth, poor convalescent rebuilding, ungroundedness.",
    "balancing_diet": "Heavy, nutritious, grounding foods. Potatoes, unrefined whole grains, dairy, butter, oils, root vegetables with garlic and onions.",
    "avoid": "Extreme fasting, skipped meals, raw insubstantial snacks.",
    "indicated_herbs": "Nourishing tonics, minerals, seaweeds, bone restoratives (comfrey, horsetail, nettles)."
  }
};

const JANE_RULES_RAW = [
  {
    "id": "jrp_sun_saturn",
    "name": "Sun–Saturn Tension: Slowed Metabolism & Arteriosclerosis",
    "name_tamil": "சூரியன்–சனி பார்வை/சேர்க்கை: மெதுவான வளர்சிதை மாற்றம் & தமனி தடிப்பு",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 3: The Planets and Aspects (Sun–Saturn)",
    "category": "Vedic Conjunction/Aspect",
    "system": "vedic",
    "required_placements": "Sun conjunct, square, or opposite Saturn in natal chart",
    "mandatory_conditions": [
      "Sun forms hard aspect (0°, 90°, or 180°) with Saturn",
      "Evaluate constitutional temperature and cardiovascular tone"
    ],
    "traditional_interpretation": "According to Jane Ridder-Patrick, Saturn slows down the vital fire of the Sun. Subjects tend to be cool to the touch yet tolerate cold well. A hallmark is the accumulation of mineral deposits causing tissues to harden, thicken, and lose flexibility, predisposing to rheumatic stiffness and arteriosclerosis. Later in life, repeated onslaughts on solar vitality produce chronic conditions.",
    "interpretation_tamil": "ஜேன் ரிடர்-பேட்ரிக் கூற்றுப்படி, சனி பகவான் சூரியனின் பிராண அக்னியை மட்டுப்படுத்துகிறார். இதனால் உடல் குளிர்ந்து காணப்படும்; தாது உப்புகள் தேங்கி திசுக்கள் தடித்து நெகிழ்வுத்தன்மை குறையலாம். தமனி தடிப்பு (Arteriosclerosis) மற்றும் மூட்டு விறைப்பு ஏற்பட வாய்ப்புள்ளது. முதிய வயதில் தீராத நோய்கள் எழாமல் இருக்க முன் எச்சரிக்கை தேவை.",
    "anatomical_system": "Arterial System, Bone Structure, Basal Metabolism, Connective Tissue",
    "modifiers": "Benefic aspect from Jupiter softens arterial stiffness; fire sign placements improve warmth.",
    "conflicting_indications": "Sun exalted in Aries or strong Mars counters hypothermia and circulatory stagnation.",
    "remedy_en": "Daily morning cold shower or cold water hydrotherapy to stimulate vitality; structured regular exercise; Calcium phosphate (Calc. phos.) tissue salt; Mimulus Bach flower; warm nourishing unrefined diet.",
    "remedy_ta": "அதிகாலை குளிர்ந்த நீர் குளியல் மூலம் நரம்புகளைத் தூண்டுதல்; முறையான உடற்பயிற்சி; கால்சியம் பாஸ்பேட் (Calc phos) தாது உப்பு; மிமுலஸ் மலர் மருந்து; சத்தான கதகதப்பான உணவு."
  },
  {
    "id": "jrp_sun_mars",
    "name": "Sun–Mars Dynamic: High Metabolic Fire, Fevers & Acidosis",
    "name_tamil": "சூரியன்–செவ்வாய் உக்கிரம்: அதீத வளர்சிதை மாற்றம், காய்ச்சல் & அமிலத்தன்மை",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 3: The Planets and Aspects (Sun–Mars)",
    "category": "Vedic Conjunction/Aspect",
    "system": "vedic",
    "required_placements": "Sun conjunct, square, or opposite Mars in natal chart",
    "mandatory_conditions": [
      "Sun forms hard aspect (0°, 90°, or 180°) with Mars",
      "Examine inflammatory tendencies and basal heat production"
    ],
    "traditional_interpretation": "Ridder-Patrick records that Mars in hard aspect to Sun produces an accelerated basal metabolic rate. Individuals emit copious heat yet subjectively feel chills. There is a strong tendency toward systemic acidosis, rapid waste accumulation, acute high fevers, and inflammatory conditions. Eliminative organs must function optimally to expel metabolic wastes promptly.",
    "interpretation_tamil": "சூரியன்–செவ்வாய் தீவிர சேர்க்கை அல்லது பார்வை உடலில் அதீத உஷ்ணத்தையும், விரைவான வளர்சிதை மாற்றத்தையும் உருவாக்கும். உடலில் அமிலத்தன்மை (Acidosis) அதிகரித்தல், திடீர் அதிகக் காய்ச்சல், அழற்சி மற்றும் தீக்காயப் பாதிப்புகள் ஏற்படலாம். கழிவகற்றும் உறுப்புகள் முறையாகச் செயல்படுவது இன்றியமையாதது.",
    "anatomical_system": "Immune Inflammatory Response, Muscular Heat Production, Adrenal Medulla, Blood Fibrinogen",
    "modifiers": "Cooling signs (Taurus, Cancer, Pisces) mitigate febrile spikes; Jupiter aspect protects blood purity.",
    "conflicting_indications": "Saturn aspect cools inflammation, though it may turn acute states into stiffness.",
    "remedy_en": "Alkaline, cooling diet with frequent light meals to compensate for energy expenditure; fresh chamomile and eyebright tea; Potassium phosphate (Kali phos); Impatiens Bach flower; avoiding violent stimulants.",
    "remedy_ta": "காரத்தன்மை கொண்ட குளிர்ச்சியான உணவு முறை; சிறிய அளவிலான அடிக்கடி உணவு; சீமைச்சாமந்தி (Chamomile) தேநீர்; காலி பாஸ் (Kali phos) உப்பு; இம்பேஷன்ஸ் மலர் மருந்து; அதிக காரம் மற்றும் துரித உணவுகளைத் தவிர்த்தல்."
  },
  {
    "id": "jrp_sun_neptune",
    "name": "Sun–Neptune Sensitivity: Compromised Vitality & Porous Boundaries",
    "name_tamil": "சூரியன்–நெப்டியூன் பலவீனம்: பிராண பலவீனம் & எல்லை மயக்கம்",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 3: The Planets and Aspects (Sun–Neptune)",
    "category": "Vedic Conjunction/Aspect",
    "system": "vedic",
    "required_placements": "Sun conjunct, square, or opposite Neptune in natal chart",
    "mandatory_conditions": [
      "Sun forms hard aspect with Neptune",
      "Assess immune boundary resilience and subtle fatigue"
    ],
    "traditional_interpretation": "Neptune breaks down boundaries and renders tissues permeable. Sun–Neptune contacts compromise vitality and immune resistance, often leading to subtle anaemia, fatigue, and breaks in clear waking consciousness. Individuals are highly susceptible to reality-altering addictions (alcohol, refined sugars) that act as slow physical self-sabotage, as well as focus-related eye disorders.",
    "interpretation_tamil": "நெப்டியூன் உடல் மற்றும் மன எல்லைகளைக் கரைக்கும் தன்மை கொண்டது. சூரியனுடன் தொடர்பு கொள்ளும்போது நோய் எதிர்ப்பு சக்தி மற்றும் பிராண பலம் குறையலாம். சோகை (Anaemia), தெளிவின்மை, போதை அல்லது சர்க்கரைப் பழக்கங்களுக்கு அடிமையாதல் மற்றும் கண் பார்வைக் கவனம் தேவைப்படலாம்.",
    "anatomical_system": "Cellular Membrane Permeability, Pineal Gland, Retinal Focus, Vital Aura",
    "modifiers": "Strong Mars or Sun in fire signs supplies physical grit; Saturn lends solid protective boundaries.",
    "conflicting_indications": "Exalted Sun in Aries resists debility.",
    "remedy_en": "Creative visualization and meditation; strict abstinence from alcohol and reality-dulling substances; Angelica and Rosemary tonics; Rock Rose Bach flower; yellow sunlight therapy to charge the pineal gland.",
    "remedy_ta": "ஆக்கப்பூர்வமான மனக்காட்சி தியானம்; மது, அதிக சர்க்கரை மற்றும் புகையிலை தவிர்த்தல்; ரோஸ்மேரி மற்றும் ஏஞ்சலிகா மூலிகைகள்; ராக் ரோஸ் மலர் மருந்து; அதிகாலை சூரிய ஒளி குளியல்."
  },
  {
    "id": "jrp_sun_uranus",
    "name": "Sun–Uranus Disruption: Cardiac Arrhythmia & Neuro-Circulatory Asthenia",
    "name_tamil": "சூரியன்–யுரேனஸ் அதிர்வு: இதயத் துடிப்பு ஒழுங்கின்மை & நரம்பு சோர்வு",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 3: The Planets and Aspects (Sun–Uranus)",
    "category": "Vedic Conjunction/Aspect",
    "system": "vedic",
    "required_placements": "Sun conjunct, square, or opposite Uranus in natal chart",
    "mandatory_conditions": [
      "Sun in hard aspect (0°, 90°, 180°) to Uranus",
      "Evaluate biological rhythms (heartbeat, pulse, respiration)"
    ],
    "traditional_interpretation": "Sun–Uranus governs the rhythmic pulsations of the organism. Difficult aspects manifest as disrupted cardiac rhythm, atrial fibrillation, or neuro-circulatory asthenia (effort syndrome / anxiety neurosis mimicking functional autonomic disorders). The body's electrical pacing becomes erratic, requiring conscious low-stimulus relaxation.",
    "interpretation_tamil": "சூரியன்–யுரேனஸ் தொடர்பு உடலின் சீரான தாள லயங்களை (இதயத் துடிப்பு, நாடி, சுவாசம்) குறிக்கிறது. கடுமையான பார்வைகள் இதயத் துடிப்பு தாறுமாறாதல் (Arrhythmia), நரம்பு வழி இதய பதற்றம் (NCA) மற்றும் பதற்ற நரம்புத் தளர்ச்சியைத் தூண்டலாம்.",
    "anatomical_system": "Cardiac Pacemaker, Autonomic Nervous System, Membrane Electrical Potential, Pyramidal Tract",
    "modifiers": "Fixed signs (Leo, Aquarius) concentrate voltage in heart; airy signs agitate nervous impulses.",
    "conflicting_indications": "Harmonious aspects of Jupiter or Venus restore emotional stability.",
    "remedy_en": "Low-stimulus downtime; conscious somatic grounding; magnesium-rich diet; Magnesium phosphate (Mag. phos.); Water Violet Bach flower; steady rhythmic pranayama breathing.",
    "remedy_ta": "அமைதியான சூழலில் ஓய்வு; நரம்பு மண்டலத்தை சாந்தப்படுத்தும் தியானம்; மெக்னீசியம் பாஸ்பேட் (Mag phos) உப்பு; வாட்டர் வயலட் மலர் மருந்து; சீரான பிராணாயாம மூச்சுப் பயிற்சி."
  },
  {
    "id": "jrp_sun_pluto",
    "name": "Sun–Pluto Stress: Cellular Transformation & Radical Endurance",
    "name_tamil": "சூரியன்–புளூட்டோ அழுத்தம்: உயிரணு மாற்றம் & தீவிர சகிப்புத்தன்மை",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 3: The Planets and Aspects (Sun–Pluto)",
    "category": "Vedic Conjunction/Aspect",
    "system": "vedic",
    "required_placements": "Sun conjunct, square, or opposite Pluto in natal chart",
    "mandatory_conditions": [
      "Sun forms hard aspect with Pluto",
      "Particularly scrutinized if placed in Fixed signs (Taurus, Leo, Scorpio, Aquarius)"
    ],
    "traditional_interpretation": "Sun–Pluto grants tremendous stamina and resilience, yet when subjected to prolonged stress beyond the breaking point, it can lead to dramatic physical breakdowns. Davidson noted that Pluto in a fixed sign afflicting a fixed sign Sun predisposes to sarcoma (connective tissue malignancy) or deep abscess formation. Regeneration requires addressing psychological survival drives.",
    "interpretation_tamil": "சூரியன்–புளூட்டோ சேர்க்கை அபரிமிதமான உடல் சகிப்புத்தன்மையை அளிக்கும்; ஆனால் எல்லையை மீறிய தொடர் மன அழுத்தத்தில் திசுக்கள் அடிமட்டத்தில் பாதிக்கப்பட்டு கட்டிகள், தீவிர அழற்சி அல்லது ஸ்திர ராசிகளில் இதய பாதிப்புகளை ஏற்படுத்தலாம். ஆழ்ந்த நச்சு நீக்கம் தேவை.",
    "anatomical_system": "Cell Nucleus, DNA Blueprint, Connective Tissue Integrity, Deep Cellular Elimination",
    "modifiers": "Sextiles and trines provide peerless recuperation and tissue rebuilding.",
    "conflicting_indications": "Strong benefic placement in Kendra prevents malign tissue degeneration.",
    "remedy_en": "Gerson therapy nutritional principles; deep psychological shadow release; radical honesty; Bloodstone or Almandine grounding; Calcium sulphate (Calc. sulph.) cell salt.",
    "remedy_ta": "கெர்சன் ஊட்டச்சத்து நச்சு நீக்கம்; ஆழ்ந்த உளவியல் ஆலோசனைகள்; கால்சியம் சல்பேட் (Calc sulph) உப்பு; பிளட்ஸ்டோன் ரத்தின சிகிச்சை; தற்காப்புக் கலை அல்லது கடின உடற்பயிற்சி மூலம் தீவிர ஆற்றலை வெளிப்படுத்துதல்."
  },
  {
    "id": "jrp_moon_saturn",
    "name": "Moon–Saturn Chill: Water Balance, Mucosa Defects & Depressive Tone",
    "name_tamil": "சந்திரன்–சனி சேர்க்கை: நீர்ச்சத்து குறைபாடு, சளிச்சவ்வு பலவீனம் & மனச்சோர்வு",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 3: The Planets and Aspects (Moon–Saturn)",
    "category": "Vedic Conjunction/Aspect",
    "system": "vedic",
    "required_placements": "Moon conjunct, square, or opposite Saturn in natal chart",
    "mandatory_conditions": [
      "Moon in hard aspect to Saturn",
      "Assess fluid balance, emotional constriction, and digestive motility"
    ],
    "traditional_interpretation": "Saturn constricts the fluid, responsive nature of the Moon. This combination produces slowed emotional responses, restrictive eating habits, chronic disturbances in the body water balance, defective mucous membranes, and bladder weakness. In women, it frequently correlates with delayed puberty, dysmenorrhoea, or scanty menses accompanied by depressive tendencies.",
    "interpretation_tamil": "சனி சந்திரனின் இயல்பான நீர் ஓட்டத்தை சுருக்குகிறது. இதனால் உடலின் நீர் சமநிலைக் கோளாறுகள், சளிச்சவ்வு வறட்சி, சிறுநீர்ப்பை மென்மை, பசியின்மை மற்றும் மன உளைச்சல் ஏற்படலாம். பெண்களுக்கு மாதவிடாய் தாமதம் அல்லது வலியைத் தரலாம்.",
    "anatomical_system": "Body Fluids, Mucous Membranes, Bladder Tone, Limbic Emotional Response, Menstrual Rhythm",
    "modifiers": "Waxing Moon or Jupiter aspect softens depressive chilling.",
    "conflicting_indications": "Moon in Taurus or Cancer exhibits innate constitutional moisture.",
    "remedy_en": "Warm, moist, grounding diet; emotional counseling; White willow and chickweed remedies; Sodium sulphate (Nat. sulph.); Mimulus / Gentian Bach flowers; warm baths with essential oils.",
    "remedy_ta": "சூடான, சத்தான திரவ உணவுகள்; உளவியல் ஆற்றுப்படுத்துதல்; வெள்ளை வில்லோ மூலிகை; நேட் சல்ப் (Nat sulph) உப்பு; மிமுலஸ் மலர் மருந்து; வெதுவெதுப்பான எண்ணெய் தேய்த்துக் குளித்தல்."
  },
  {
    "id": "jrp_moon_neptune",
    "name": "Moon–Neptune Fluidity: Idiopathic Oedema, Allergies & Psychic Porosity",
    "name_tamil": "சந்திரன்–நெப்டியூன் இணைப்பு: திரவத் தேக்கம், ஒவ்வாமை & அதீத உணர்திறன்",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 3: The Planets and Aspects (Moon–Neptune)",
    "category": "Vedic Conjunction/Aspect",
    "system": "vedic",
    "required_placements": "Moon conjunct, square, trine, or opposite Neptune in natal chart",
    "mandatory_conditions": [
      "Moon in major aspect to Neptune (including trines which strongly link to sensitivities)",
      "Scrutinize fluid retention, osmotic pressure shifts, and food/metal allergies"
    ],
    "traditional_interpretation": "Jane Ridder-Patrick emphasizes that Moon–Neptune erodes emotional and cellular boundaries. Highly impressionable individuals suffer from osmotic shifts, premenstrual bloating, or full-blown idiopathic oedema where weight fluctuates drastically. Moon–Neptune trines, even more than hard aspects, correlate with food sensitivities (dairy, wheat, sugar), candida overgrowth, asthma, and metal allergies (especially silver, the metal of Moon).",
    "interpretation_tamil": "சந்திரன்–நெப்டியூன் இணைப்பு உடல் திரவங்கள் மற்றும் உணர்வு எல்லைகளை எளிதில் ஊடுருவச் செய்கிறது. இடியோபாடிக் எடிமா (காரணமற்ற நீர் வீக்கம்), உணவு ஒவ்வாமை (பால், கோதுமை, சர்க்கரை), ஆஸ்துமா மற்றும் வெள்ளி ஆபரண ஒவ்வாமை ஏற்படலாம். சூழல் உணர்வுகளைத் தன்னுள் உறிஞ்சும் மனநிலை தோன்றும்.",
    "anatomical_system": "Lymphatic Drainage, Osmotic Pressure, Intracellular Fluid, Immune Boundary Recognition",
    "modifiers": "Presence in water signs (Cancer, Scorpio, Pisces) magnifies fluid swelling.",
    "conflicting_indications": "Saturn aspect imposes firm boundary limits and dispels psychic fog.",
    "remedy_en": "Practice the 3 'M's: Mastication (thorough chewing of food & experience), Massage (claiming physical skin boundaries), and Meditation (centering awareness); avoid pasteurized dairy; Clematis / Rock Rose Bach flowers; Natrum muriaticum.",
    "remedy_ta": "மூன்று 'M' பயிற்சி: மென்று உண்ணுதல் (Mastication), தைல மசாஜ் (Massage - தோல் எல்லையை உணர்தல்), தியானம் (Meditation); பதப்படுத்தப்பட்ட பால் பொருட்களைத் தவிர்த்தல்; கிளிமேடிஸ் மலர் மருந்து; நேட் மியூர் உப்பு."
  },
  {
    "id": "jrp_moon_mars",
    "name": "Moon–Mars Friction: Repressed Anger, Bilious Nausea & Hyperthyroidism",
    "name_tamil": "சந்திரன்–செவ்வாய் முரண்பாடு: அடக்கிய கோபம், பித்த குமட்டல் & தைராய்டு பாதிப்பு",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 3: The Planets and Aspects (Moon–Mars)",
    "category": "Vedic Conjunction/Aspect",
    "system": "vedic",
    "required_placements": "Moon conjunct, square, or opposite Mars in natal chart",
    "mandatory_conditions": [
      "Moon forms hard aspect with Mars",
      "Examine emotional assertiveness, bile secretion, and thyroid status"
    ],
    "traditional_interpretation": "Conflict between the need to nurture (Moon) and the drive to fight (Mars). Carter and Ridder-Patrick state that when emotional anger does not find an external constructive outlet, it turns inward, undermining health. Clinically manifests as copious menses, bilious nausea, reddish skin eruptions, and involuntary muscle twitches. Reinhold Ebertin linked it directly with Graves' disease (hyperthyroidism).",
    "interpretation_tamil": "பராமரிக்கும் குணம் (சந்திரன்) மற்றும் மோதும் குணம் (செவ்வாய்) இடையேயான முரண்பாடு. அடக்கப்பட்ட கோபம் உள்ளுறுப்புகளை தாக்கி, அதிக ரத்தப்போக்கு, பித்த குமட்டல், சிவப்பு தடிப்புகள் மற்றும் தைராய்டு அதீத சுரப்பு (கிரேவ்ஸ் நோய்) ஏற்பட வழிவகுக்கும்.",
    "anatomical_system": "Thyroid Gland, Gastric Motility, Bilious Secretions, Involuntary Muscular Action, Menstruation",
    "modifiers": "Benefic aspects from Jupiter convert martial friction into righteous vitality.",
    "conflicting_indications": "Venus in good dignity soothes emotional temper.",
    "remedy_en": "Assertiveness training; active physical sports or martial arts; cooling bitter tonics (gentian, barberry); Potassium phosphate (Kali phos); Impatiens Bach flower; avoiding overheated emotional confrontations.",
    "remedy_ta": "சுய உரிமையை வெளிப்படுத்தும் பயிற்சி; யோகா மற்றும் உடற்பயிற்சி; கசப்புச் சுவை கொண்ட மூலிகைகள் (Dandelion, Barberry); காலி பாஸ் உப்பு; இம்பேஷன்ஸ் மலர் மருந்து; வீண் வாக்குவாதங்களைத் தவிர்த்தல்."
  },
  {
    "id": "jrp_moon_uranus",
    "name": "Moon–Uranus Tension: Visceral Colic, Neuro-Glandular Spasms & Bulimia",
    "name_tamil": "சந்திரன்–யுரேனஸ் அதிர்வு: உள்ளுறுப்பு வலி, நரம்பு பிடிப்பு & உணவு முறை ஒழுங்கின்மை",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 3: The Planets and Aspects (Moon–Uranus)",
    "category": "Vedic Conjunction/Aspect",
    "system": "vedic",
    "required_placements": "Moon conjunct, square, or opposite Uranus in natal chart",
    "mandatory_conditions": [
      "Moon forms hard aspect with Uranus",
      "Examine visceral smooth muscle spasms and autonomic stability"
    ],
    "traditional_interpretation": "Psychologically manifests as unpredictable emotional electricity and lack of felt safety. Pathologically, Uranus induces spasmodic colic in fluid-containing or fluid-excreting organs (bladder, colon, gall bladder, prostate) and blood pressure instability. Sufferers frequently override bodily rhythms (delaying menses at will, ignoring prompts to eat or sleep, or developing bulimic gorge-and-purge cycles).",
    "interpretation_tamil": "உணர்ச்சித் தளத்தில் மின்னல் போன்ற திடீர் மாற்றங்கள் தோன்றும். சிறுநீர்ப்பை, குடல், பித்தப்பை போன்ற உள்ளுறுப்புகளில் திடீர் பிடிப்பு வலிகள் (Colic), ரத்த அழுத்த மாறுபாடுகள், மற்றும் உடலின் பசி, தூக்க சுழற்சிகளை மீறி நடக்கும் போக்குகள் (Bulimia) ஏற்படலாம்.",
    "anatomical_system": "Visceral Smooth Muscle, Bladder & Colon Sphincters, Neuro-Hormonal Rhythms, Blood Pressure",
    "modifiers": "Earth sign placements anchor electrical surges.",
    "conflicting_indications": "Saturn trine stabilizes autonomic periodicity.",
    "remedy_en": "Strict routine for meals and sleep; low-stimulus relaxation; Magnesium phosphate (Mag. phos.); Water Violet Bach flower; grounding breathing exercises.",
    "remedy_ta": "சீரான உணவு மற்றும் தூக்க அட்டவணை; அமைதியான சூழல்; மெக்னீசியம் பாஸ்பேட் (Mag phos) தாது உப்பு; வாட்டர் வயலட் மலர் மருந்து; நரம்புகளை அமைதிப்படுத்தும் பயிற்சிகள்."
  },
  {
    "id": "jrp_moon_pluto",
    "name": "Moon–Pluto Holding: Endometriosis, Fibroids & Deep Visceral Cleansing",
    "name_tamil": "சந்திரன்–புளூட்டோ தேக்கம்: எண்டோமெட்ரியோசிஸ், கருப்பை கட்டிகள் & குடல் கழிவு",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 3: The Planets and Aspects (Moon–Pluto)",
    "category": "Vedic Conjunction/Aspect",
    "system": "vedic",
    "required_placements": "Moon conjunct, square, or opposite Pluto in natal chart",
    "mandatory_conditions": [
      "Moon forms hard aspect with Pluto",
      "Examine reproductive and lower bowel eliminative integrity"
    ],
    "traditional_interpretation": "Pluto intensifies lunar reproductive and eliminative processes. Women with Moon–Pluto aspects frequently experience fibroids, endometriosis, severe menorrhagia, intense childbirth crises, or disturbances of bowel function requiring surgical intervention. Deep holding patterns represent fear of emotional vulnerability; healing occurs when intuitive power and bodily ripening are embraced.",
    "interpretation_tamil": "புளூட்டோ சந்திரனின் இனப்பெருக்க மற்றும் கழிவகற்றும் உறுப்புகளில் தீவிர தாக்கத்தை ஏற்படுத்துகிறது. பெண்களுக்கு கருப்பை நார்த்திசுக்கட்டிகள் (Fibroids), எண்டோமெட்ரியோசிஸ், அதிக உதிரப்போக்கு அல்லது பெருங்குடல் கழிவுத் தேக்கப் பிரச்சினைகள் ஏற்படலாம். அடிவயிற்று நச்சு நீக்கம் அவசியம்.",
    "anatomical_system": "Uterus, Endometrium, Ovarian Follicles, Sigmoid Colon, Pelvic Lymphatics",
    "modifiers": "Benefic aspect from Jupiter eases pelvic stagnation.",
    "conflicting_indications": "Venus in Taurus or Libra provides natural hormonal balance.",
    "remedy_en": "Pelvic castor oil packs; colon detox; psychological acceptance of emotional boundaries; Calcium sulphate (Calc. sulph.); Chicory Bach flower; radical nutritional cleansing.",
    "remedy_ta": "அடிவயிற்று விளக்கெண்ணெய் ஒத்தடம்; குடல் நச்சு நீக்கம்; உணர்ச்சி வடிகால் பயிற்சிகள்; கால்கேரியா சல்பேட் (Calc sulph) உப்பு; சிக்கரி மலர் மருந்து; நார்ச்சத்து நிறைந்த உணவுகள்."
  },
  {
    "id": "jrp_mars_neptune",
    "name": "Mars–Neptune: The Classical Pathological Aspect (Autoimmune & Low Resistance)",
    "name_tamil": "செவ்வாய்–நெப்டியூன் இணைப்பு: 'நோயியல் அம்சம்' — தன்னுடல் தாக்குதல் & குறைந்த எதிர்ப்பு சக்தி",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 3: The Planets and Aspects (Mars–Neptune)",
    "category": "Vedic Conjunction/Aspect",
    "system": "vedic",
    "required_placements": "Mars conjunct, square, or opposite Neptune in natal chart",
    "mandatory_conditions": [
      "Mars forms hard aspect with Neptune",
      "Evaluate white blood cell defense, autoimmune markers, and insidious infections"
    ],
    "traditional_interpretation": "Jane Ridder-Patrick titles this 'the pathological aspect' because Mars, the warrior of bodily defense, is confused and undermined by Neptune's diffuseness. The body does not know whether to attack or surrender, leading to autoimmune disorders where immune cells turn upon the host's own tissues, as well as chronic pus discharges and low-grade elusive infections. Transmuted through altruistic causes.",
    "interpretation_tamil": "மருத்துவ ஜோதிடத்தில் இது 'நோயியல் சேர்க்கை' என அழைக்கப்படுகிறது. உடலின் பாதுகாப்பு வீரனான செவ்வாய், நெப்டியூனின் எல்லையற்ற மயக்கத்தால் குழம்பி, உடலின் சொந்த திசுக்களையே தாக்கும் 'தன்னுடல் தாக்குதல்' (Autoimmune) நோய்களையும், நாள்பட்ட மர்மமான தொற்றுகளையும் உருவாக்கலாம்.",
    "anatomical_system": "White Blood Cells, Lymphocyte Recognition, Muscular Tone, Pus Elimination",
    "modifiers": "Mars in Capricorn (exalted) maintains structural resistance despite Neptunian mist.",
    "conflicting_indications": "Sun in fiery signs fortifies the core vitality.",
    "remedy_en": "Dedication of physical energy to a noble altruistic cause; alterative immune-modulating herbs (burdock, yellow dock, sarsaparilla); Ferrum phosphate (Ferr. phos.); Rock Rose Bach flower; avoiding martyrdom dynamics.",
    "remedy_ta": "சுயநலமற்ற அறப்பணிகளில் உடலுழைப்பை செலுத்துதல்; இரத்தத்தை சுத்தி செய்யும் மூலிகைகள் (Burdock, Sarsaparilla); பெர்ரம் பாஸ்பேட் (Ferr phos) உப்பு; ராக் ரோஸ் மலர் மருந்து; மருத்துவ நிபுணரின் வழிகாட்டல்."
  },
  {
    "id": "jrp_mars_saturn",
    "name": "Mars–Saturn Tension: Joint Inflammation, Arthritis & Gallstones",
    "name_tamil": "செவ்வாய்–சனி முரண்பாடு: மூட்டு அழற்சி, வாத நோய் & பித்தப்பை கற்கள்",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 3: The Planets and Aspects (Mars–Saturn)",
    "category": "Vedic Conjunction/Aspect",
    "system": "vedic",
    "required_placements": "Mars conjunct, square, or opposite Saturn in natal chart",
    "mandatory_conditions": [
      "Mars forms hard aspect with Saturn",
      "Examine bone formation, red blood cells, joint synovial fluid, and bile concentration"
    ],
    "traditional_interpretation": "Mars (inflammatory heat) collides with Saturn (cold contraction and crystallization). The classic manifestation is joint inflammation alternating with chronic stiffness, as seen in arthritis, bone malformations, and pathological fractures. It also governs gallstone formation from crystallized bile salts and impaired red cell maturation in the bone marrow.",
    "interpretation_tamil": "செவ்வாயின் அக்னி வெப்பமும் சனியின் குளிர்ந்த இறுகும் தன்மையும் மோதும் போது மூட்டு அழற்சி (Arthritis), எலும்பு தேய்மானம், மற்றும் பித்தப்பையில் கற்கள் (Gallstones) உருவாகும் சூழல் ஏற்படுகிறது. ஒழுங்கமைக்கப்பட்ட உடற்பயிற்சி மூலம் இதனை சமநிலைப்படுத்தலாம்.",
    "anatomical_system": "Articular Joints, Bone Marrow, Red Blood Cell Synthesis, Gall Bladder Bile Concentration",
    "modifiers": "Mars in Capricorn reconciles both planetary energies; benefic Jupiter aspect alleviates joint pain.",
    "conflicting_indications": "Strong Venus maintains synovial fluid lubrication.",
    "remedy_en": "Disciplined martial arts or structured physiotherapy (karate, resistance training); antirheumatic herbs (celery seed, angelica, bogbean); Calcium phosphate (Calc. phos.); Centaury / Mimulus Bach flowers.",
    "remedy_ta": "கராத்தே அல்லது சீரான தசைப் பயிற்சி; வாதம் தணிக்கும் மூலிகைகள் (Celery seed, Angelica); கால்கேரியா பாஸ்பேட் உப்பு; செண்டாரி மலர் மருந்து; மூட்டுகளுக்கு வெதுவெதுப்பான ஒத்தடம்."
  },
  {
    "id": "jrp_mercury_mars",
    "name": "Mercury–Mars Irritability: Motor Nerve Tension, Tics & Spasticity",
    "name_tamil": "புதன்–செவ்வாய் உக்கிரம்: நரம்பு எரிச்சல், துடிப்பு & தசை பிடிப்பு",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 3: The Planets and Aspects (Mercury–Mars)",
    "category": "Vedic Conjunction/Aspect",
    "system": "vedic",
    "required_placements": "Mercury conjunct, square, or opposite Mars in natal chart",
    "mandatory_conditions": [
      "Mercury forms hard aspect with Mars",
      "Assess motor nerve conduction, reflex excitability, and speech velocity"
    ],
    "traditional_interpretation": "Mercury represents neural pathways; Mars introduces violent heat and speed. Hard aspects create motor nerve irritability, involuntary twitchings, tics, nervous tissue inflammation, and spastic tremors. When anxiety surges, it frequently triggers bilious diarrhea accompanied by intense thirst.",
    "interpretation_tamil": "புதன் நரம்பு மண்டலத்தையும், செவ்வாய் உஷ்ண வேகத்தையும் குறிக்கின்றன. இச்சேர்க்கை மோட்டார் நரம்புகளில் அதீத தூண்டுதலை உண்டாக்கி, கண் அல்லது தசை துடிப்பு (Tics), நரம்பு அழற்சி மற்றும் பதற்றத்தால் ஏற்படும் பித்த வயிற்றுப்போக்கை உருவாக்கலாம்.",
    "anatomical_system": "Motor Efferent Nerves, Neuromuscular Junction, Enteric Nerve Motility, Speech Articulation",
    "modifiers": "Placement in Gemini or Virgo speeds up nervous impulse; Jupiter aspect broadens patience.",
    "conflicting_indications": "Saturn aspect slows down neural firing, transforming tics into stiffness.",
    "remedy_en": "Nervine tonics to soothe nerve sheath (valerian, skullcap, passionflower); eliminating caffeine and energy drinks; Potassium phosphate (Kali phos); Impatiens Bach flower; conscious breath pacing.",
    "remedy_ta": "நரம்புகளை சாந்தப்படுத்தும் மூலிகைத் தேநீர் (Valerian, Passionflower); காபி, தேநீர் மற்றும் செயற்கை குளிர்பானங்களைத் தவிர்த்தல்; காலி பாஸ் உப்பு; இம்பேஷன்ஸ் மலர் மருந்து."
  },
  {
    "id": "jrp_mercury_saturn",
    "name": "Mercury–Saturn Retardation: Auditory Ossicle Stiffness & Dyslexia",
    "name_tamil": "புதன்–சனி மந்தம்: காது எலும்பு இறுக்கம், பேச்சுக் குறைபாடு & மூட்டு வலி",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 3: The Planets and Aspects (Mercury–Saturn)",
    "category": "Vedic Conjunction/Aspect",
    "system": "vedic",
    "required_placements": "Mercury conjunct, square, or opposite Saturn in natal chart",
    "mandatory_conditions": [
      "Mercury forms hard aspect with Saturn",
      "Assess auditory nerve & middle ear bones, speech fluency, and cognitive processing speed"
    ],
    "traditional_interpretation": "Saturn restrains and cools Mercury's nervous communication. Clinically correlates with under-functioning of the nervous system, specifically the auditory nerve and tiny middle ear bones (ruled by Saturn), predisposing to hearing impairment and tinnitus. Commonly found in cases of developmental dyslexia, delayed speech articulation, and deep dull pain in the joints.",
    "interpretation_tamil": "சனி புதனின் நரம்புத் தொடர்பை மட்டுப்படுத்துகிறது. இதனால் நடுச்செவி சிற்றெலும்புகள் (Middle ear bones) மற்றும் செவி நரம்புகளில் மந்தம் ஏற்பட்டு கேட்கும் திறன் குறைபாடு, டின்னிடஸ் (Tinnitus), பேச்சில் தயக்கம் அல்லது மூட்டுகளில் மந்தமான வலி ஏற்படலாம்.",
    "anatomical_system": "Auditory Nerve, Middle Ear Ossicles, Speech Centers (Broca's area), Joint Nerve Supply",
    "modifiers": "Air signs mitigate speech delay; earth signs intensify acoustic stiffness.",
    "conflicting_indications": "Sun conjunct Mercury (Cazimi) preserves sharp mental clarity.",
    "remedy_en": "Vocal articulation and singing exercises; ear warmth therapy; warm nervine spices (fennel, dill, liquorice); Silicon oxide (Silica); Mimulus Bach flower; warm ear oil drops (Karna Poorana).",
    "remedy_ta": "குரல் பயிற்சி மற்றும் மந்திர உச்சரிப்பு; காதுகளுக்கு கதகதப்பான நல்லெண்ணெய் சிகிச்சை; பெருஞ்சீரகம், அதிமதுரம் உட்கொள்ளுதல்; சிலிக்கா தாது உப்பு; மிமுலஸ் மலர் மருந்து."
  },
  {
    "id": "jrp_venus_saturn",
    "name": "Venus–Saturn Stasis: Endocrine Hypofunction, Renal Sclerosis & Varicose Veins",
    "name_tamil": "சுக்கிரன்–சனி தேக்கம்: நாளமில்லா சுரப்பி மந்தம், சிறுநீரக இறுக்கம் & நரம்பு சுருளல்",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 3: The Planets and Aspects (Venus–Saturn)",
    "category": "Vedic Conjunction/Aspect",
    "system": "vedic",
    "required_placements": "Venus conjunct, square, or opposite Saturn in natal chart",
    "mandatory_conditions": [
      "Venus in hard aspect to Saturn",
      "Scrutinize venous return, hormonal output, and renal tubule elasticity"
    ],
    "traditional_interpretation": "Venus rules balance, venous return, and hormonal feedback; Saturn introduces sclerosis and atrophy. Hard aspects lead to under-functioning of endocrine glands (compensatory enlargement such as goitre), emphysema of pulmonary alveoli, hardening of kidney tubules, and venous stasis. Venus conjunct Saturn in Aquarius is particularly documented for varicose veins in the lower extremities.",
    "interpretation_tamil": "சுக்கிரன் ஹார்மோன் சமநிலையையும், சனி சுருங்குதலையும் குறிக்கின்றன. இதனால் தைராய்டு சுரப்புக் குறைவு (Goitre), சிறுநீரகக் குழாய்கள் தடித்தல் மற்றும் கால்களில் நரம்பு சுருண்டு வீங்குதல் (Varicose veins - குறிப்பாக கும்பத்தில் இவ்விருவர் இணையும் போது) ஏற்படலாம்.",
    "anatomical_system": "Venous Circulation, Endocrine Regulatory Feedback, Kidney Glomeruli, Pulmonary Alveoli",
    "modifiers": "Benefic aspect from Jupiter eases venous pressure; fire signs stimulate glandular secretion.",
    "conflicting_indications": "Venus in own signs (Taurus, Libra) retains homeostatic resilience.",
    "remedy_en": "Leg elevation; daily brisk walking to activate calf muscle venous pumps; Burdock and Lady's mantle; Calcium fluoride (Calc. fluor.); Scleranthus Bach flower; emerald / copper vibrational balancing.",
    "remedy_ta": "கால்களை உயர்த்தி வைத்து ஓய்வெடுத்தல்; தினமும் நடைப்பயிற்சி மூலம் கால் நரம்பு ஓட்டத்தை சீராக்குதல்; பரங்கிப்பட்டை, லேடிஸ் மேண்டில் மூலிகைகள்; கால்கேரியா புளோர் (Calc fluor) உப்பு; ஸ்கிளராந்தஸ் மலர் மருந்து."
  },
  {
    "id": "jrp_jupiter_saturn",
    "name": "Jupiter–Saturn Tension: Sluggish Liver Metabolism & Arterial Rigidity",
    "name_tamil": "குரு–சனி முரண்பாடு: மந்தமான கல்லீரல் செயல்பாடு & தமனி இறுக்கம்",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 3: The Planets and Aspects (Jupiter–Saturn)",
    "category": "Vedic Conjunction/Aspect",
    "system": "vedic",
    "required_placements": "Jupiter conjunct, square, or opposite Saturn in natal chart",
    "mandatory_conditions": [
      "Jupiter in hard aspect to Saturn",
      "Assess liver size and detoxification, arterial elasticity, and mood fluctuation"
    ],
    "traditional_interpretation": "Jupiter governs liver synthesis and arterial expansion; Saturn restricts and hardens. Hard aspects produce an under-functioning, often small or congested liver, sluggish bile emulsification of fats, gall bladder colic, and arterial hardening associated with high blood pressure. Psychologically leads to seesawing between exuberant optimism and deep pessimism.",
    "interpretation_tamil": "குரு கல்லீரல் கொழுப்பு செரிமானத்தையும், சனி சுருங்குதலையும் ஆள்கின்றனர். இவ்விருவர் முரண்பாடு கல்லீரல் மந்தம், பித்தப்பைக் கோளாறுகள், மற்றும் தமனி தடிப்பினால் உண்டாகும் ரத்த அழுத்தத்தை (Hypertension) உருவாக்கலாம். மனநிலையில் அதீத நம்பிக்கையும் சோர்வும் மாறி மாறி வரும்.",
    "anatomical_system": "Hepatic Lobes, Gall Bladder Bile Synthesis, Arterial Walls, Fat Emulsification",
    "modifiers": "Jupiter in Cancer (exalted) shields liver parenchyma; Sun aspect boosts arterial vitality.",
    "conflicting_indications": "Benefic Mars aspect stimulates active circulation.",
    "remedy_en": "Liver decongestant tonics (dandelion root, yellow dock, agrimony); low saturated-fat diet; Sodium sulphate (Nat. sulph.); Agrimony Bach flower; steady disciplined physical routine.",
    "remedy_ta": "கல்லீரல் சுத்தி மூலிகைகள் (Dandelion root, Agrimony); குறைந்த கொழுப்புள்ள சமச்சீர் உணவு; சோடியம் சல்பேட் (Nat sulph) உப்பு; அக்ரிமனி மலர் மருந்து; சீரான உடற்பயிற்சி."
  },
  {
    "id": "jrp_jupiter_neptune",
    "name": "Jupiter–Neptune Permeability: Waterlogged Tissues & Gas Fermentation",
    "name_tamil": "குரு–நெப்டியூன் பலவீனம்: திசுக்களில் நீர் கசிவு & குடல் வாயு உப்புசம்",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 3: The Planets and Aspects (Jupiter–Neptune)",
    "category": "Vedic Conjunction/Aspect",
    "system": "vedic",
    "required_placements": "Jupiter conjunct, square, or opposite Neptune in natal chart",
    "mandatory_conditions": [
      "Jupiter in hard aspect to Neptune",
      "Evaluate small arterial permeability, liver enzyme potency, and intestinal gas"
    ],
    "traditional_interpretation": "Neptune renders small arterial walls abnormally permeable, allowing fluid leakage into interstitial tissues (waterlogged boggy tissues). Hepatic enzyme metabolism becomes deficient, leaving food particles incompletely digested; this results in excessive intestinal fermentation, severe gas bloating, and floating fatty or clay-coloured stools. Misdiagnoses are extremely frequent.",
    "interpretation_tamil": "நெப்டியூன் தமனிகளின் சுவர்களை அதீத கசிவுத்தன்மை கொண்டதாக மாற்றுகிறது; இதனால் திசுக்களில் நீர் தேங்கி உடல் பருமன் போலத் தோன்றும். செரிமான என்சைம்கள் குறைந்து குடலில் வாயு உற்பத்தியாகி வயிறு உப்பும்; மிதக்கும் கொழுப்பு கலந்த கழிவுகள் வெளியேறலாம்.",
    "anatomical_system": "Arterial Capillaries, Liver Detoxification Enzymes, Intestinal Gas Balance, Stool Consistency",
    "modifiers": "Virgo emphasis demands strict food hygiene; fire signs help burn off swampy dampness.",
    "conflicting_indications": "Saturn aspect dries up excessive mucosal leakage.",
    "remedy_en": "Digestive enzymes; bitter digestive stimulants (gentian, barberry); avoiding rich creamy foods and excess alcohol; Potassium sulphate (Kali. sulph.); Scleranthus Bach flower.",
    "remedy_ta": "இயற்கை செரிமான என்சைம்கள்; கசப்பு மூலிகைகள் (ஜென்சியன், பார்மெர்ரி); அதிக கொழுப்பு, மது மற்றும் பால் உணவுகளைத் தவிர்த்தல்; பொட்டாசியம் சல்பேட் உப்பு; ஸ்கிளராந்தஸ் மலர் மருந்து."
  },
  {
    "id": "jrp_cardinal_cross_reflex",
    "name": "Cardinal Cross Reflex Axis: Regulation, Structure & Endocrine Interplay",
    "name_tamil": "சர ராசி முரண் அச்சு: கட்டுப்பாடு, கட்டமைப்பு & நாளமில்லா சுரப்பி ஒருங்கிணைப்பு",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 4: The Signs and Houses (The Cardinal Cross)",
    "category": "Vedic Birth Chart",
    "system": "vedic",
    "required_placements": "Two or more planets in hard aspect across Cardinal signs (Aries, Cancer, Libra, Capricorn)",
    "mandatory_conditions": [
      "Multiple planets situated in Cardinal quadruplicity signs",
      "Examine reflex organ axes: Adrenals <-> Kidneys <-> Water mucosa <-> Pituitary/Skeleton"
    ],
    "traditional_interpretation": "The Cardinal Cross is the cross of Regulation, Structure, and Protection. The four signs act in an intimately linked reflex loop: Aries rules the adrenals (blood pressure and fight-or-flight); Libra rules the kidneys (blood filtration, sugar balance, sodium retention); Cancer rules body water and protective mucous membranes; Capricorn rules the anterior pituitary (master regulator of adrenals and bones). Affliction in one sign reflexly disturbs the entire protective endocrine chain.",
    "interpretation_tamil": "சர ராசிகளான மேஷம் (அட்ரினல்), கடகம் (உடல் நீர், சளிச்சவ்வு), துலாம் (சிறுநீரகம், சர்க்கரை சமநிலை), மகரம் (பிட்யூட்டரி, எலும்பு) ஆகிய நான்கும் உடலின் கட்டுப்பாட்டு சங்கிலியாகும். ஒன்றில் ஏற்படும் அழுத்தம் மற்ற உறுப்புகளில் எதிரொலித்து (Reflex action) நீர் தேக்கம், தலைவலி, சர்க்கரை மற்றும் ரத்த அழுத்த மாற்றங்களை உண்டாக்கும்.",
    "anatomical_system": "Pituitary–Adrenal–Renal Axis, Mucous Membranes, Skeleton and Bone Density",
    "modifiers": "Benefics in Cardinal angles preserve homeostatic equilibrium.",
    "conflicting_indications": "Lagna lord strong in Kendra minimizes reflex systemic spread.",
    "remedy_en": "Balancing water and sodium intake; kidney flushing herbal infusions (cleavers, couchgrass); endocrine-soothing foods; Calc. fluor. and Nat. phos. cell salts; maintaining strict sleep rhythm for the pituitary.",
    "remedy_ta": "உப்பு மற்றும் நீர் உட்கொள்ளலை சமநிலையில் வைத்தல்; சிறுநீரக கழிவகற்றும் மூலிகை நீர்; பிட்யூட்டரி சுரப்பியை பாதுகாக்க சரியான தூக்க முறை; கால்கேரியா புளோர் மற்றும் நேட் பாஸ் உப்புகள்."
  },
  {
    "id": "jrp_fixed_cross_reflex",
    "name": "Fixed Cross Reflex Axis: Vital Functions, Organ Engorgement & Cellular Proliferation",
    "name_tamil": "ஸ்திர ராசி முரண் அச்சு: பிராண இயக்கங்கள், இரத்த ஓட்டம் & உயிரணு பெருக்கம்",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 4: The Signs and Houses (The Fixed Cross)",
    "category": "Vedic Birth Chart",
    "system": "vedic",
    "required_placements": "Two or more planets in hard aspect across Fixed signs (Taurus, Leo, Scorpio, Aquarius)",
    "mandatory_conditions": [
      "Multiple planets situated in Fixed quadruplicity signs",
      "Examine reflex links: Thyroid <-> Colon/Reproductive; Heart <-> Calf Venous Circulation"
    ],
    "traditional_interpretation": "The Fixed Cross governs the Vital Functions: cardiovascular, reproductive, excretory, and reptilian brain instincts. Fixed signs are aggregative, tending to hold fast, accumulate toxic wastes, and proliferate cellular overgrowth (cysts, benign tumours, stones). Classic reflex pairs: Taurus (neck/thyroid) reflexes into Scorpio (pelvic organs/colon); Leo (heart/spine) reflexes into Aquarius (calf muscle venous pump and spinal motor tracts).",
    "interpretation_tamil": "ஸ்திர ராசிகளான ரிஷபம் (தொண்டை/தைராய்டு), சிம்மம் (இதயம்/முதுகுத்தண்டு), விருச்சிகம் (பெருங்குடல்/பாலியல் உறுப்புகள்), கும்பம் (கால் நரம்புகள்/சுழற்சி) ஆகியவை உடலின் அடிப்படை வாழ்வாதாரத்தை ஆள்கின்றன. இவை கழிவுகளை அடக்கி வைத்து கட்டிகள், கற்கள் அல்லது நரம்பு வீக்கத்தை உருவாக்கலாம். தீவிர உடற்பயிற்சி மற்றும் மலக்குடல் சுத்தி அவசியம்.",
    "anatomical_system": "Cardiovascular System, Endocrine Thyroid, Pelvic Reproductive Organs, Venous Return, Deep Colon",
    "modifiers": "Harmonious aspects of Sun prevent cardiovascular stagnation.",
    "conflicting_indications": "Strong Mars provides dynamic centrifugal cleansing.",
    "remedy_en": "Cardiovascular walking and swimming; colon cleansing high-fiber diet; thyroid nutritional support (kelp, seaweeds); Mag. phos. and Calc. sulph. cell salts; avoiding rich aggregative foods.",
    "remedy_ta": "தினமும் நடைப்பயிற்சி மற்றும் நீச்சல்; குடல் கழிவகற்றும் நார்ச்சத்து உணவுகள்; தைராய்டு ஊட்டச்சத்து (கடல் பாசி); மெக் பாஸ் மற்றும் கால்கேரியா சல்பேட் உப்புகள்; அதிக கொழுப்பு உணவுகளைத் தவிர்த்தல்."
  },
  {
    "id": "jrp_mutable_cross_reflex",
    "name": "Mutable Cross Reflex Axis: Metabolism, Enteric Belly-Brain & Psychosomatics",
    "name_tamil": "உபய ராசி முரண் அச்சு: வளர்சிதை மாற்றம், வயிற்று மூளை (ENS) & மனோதத்துவ பாதிப்புகள்",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 4: The Signs and Houses (The Mutable Cross)",
    "category": "Vedic Birth Chart",
    "system": "vedic",
    "required_placements": "Two or more planets in hard aspect across Mutable signs (Gemini, Virgo, Sagittarius, Pisces)",
    "mandatory_conditions": [
      "Multiple planets situated in Mutable quadruplicity signs",
      "Examine reflex linkages: Gemini (Lungs/Nerves) <-> Sagittarius (Locomotion/Brain); Virgo (Enteric ENS) <-> Pisces (Immune/Pineal)"
    ],
    "traditional_interpretation": "The Mutable Cross is the Metabolic Cross (Greek 'metabole' = change and exchange), governing respiratory, digestive, and nervous mediators. Mutable signs are the least robust due to high sensitivity. Virgo rules the enteric nervous system ('belly brain') and digestive enzymes, which reflex directly into Pisces (lymphatic and immune dissolution, psychosomatic somatization). When external stress strikes, the vagus nerve discharges shock into the intestines, causing IBS, diarrhea, or ulcers.",
    "interpretation_tamil": "உபய ராசிகளான மிதுனம் (சுவாசம்/நரம்புகள்), கன்னி (குடல் நரம்பு/செரிமானம்), தனுசு (இயக்கம்/பெருமூளை), மீனம் (நிணநீர்/உள்ளுணர்வு) ஆகியவை உடலின் வளர்சிதை மாற்ற தூதுவர்கள் ஆகும். மன அழுத்தம் ஏற்படும் போது, குடல் நரம்பு மண்டலம் (Belly Brain) பாதிக்கப்பட்டு IBS, அஜீரணம் அல்லது ஆஸ்துமா போன்ற மனோதத்துவ (Psychosomatic) உடல் உபாதைகள் தோன்றலாம்.",
    "anatomical_system": "Enteric Nervous System (ENS), Bronchial Airways, Pancreatic Enzymes, Lymphatic Immune Boundary",
    "modifiers": "Earth placement grounds flighty nervous excitability; water placement soothes gut mucosa.",
    "conflicting_indications": "Well-placed Mercury or Jupiter strengthens mental-digestive resilience.",
    "remedy_en": "Virgo Naturopathic approach: pure, unadulterated, whole foods; mindful eating with thorough chewing (Mastication); soothing nervine teas (chamomile, peppermint); Kali. sulph. and Ferr. phos.; Centaury / Cerato Bach flowers.",
    "remedy_ta": "கன்னி ராசி இயற்கை மருத்துவ முறை: தூய்மையான இயற்கை உணவுகள்; உணவை நன்றாக மென்று உண்ணுதல்; சீமைச்சாமந்தி, புதினா தேநீர்; காலி சல்ப் மற்றும் பெர்ரம் பாஸ் உப்புகள்; செண்டாரி மலர் மருந்து."
  },
  {
    "id": "jrp_decumbiture_early_late_asc",
    "name": "Decumbiture Stricture: Premature (<3°) or Protracted (>27°) Ascendant",
    "name_tamil": "நோய்விவர ஜோதிட எச்சரிக்கை: ஆரம்ப நிலை (<3°) அல்லது தாமதமான (>27°) லக்னம்",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 6: The Decumbiture Chart (Strictures on Judgement)",
    "category": "Vedic Birth Chart",
    "system": "vedic",
    "required_placements": "Decumbiture or consultation chart Ascendant is less than 3° or greater than 27° in any sign",
    "mandatory_conditions": [
      "Ascendant longitude in sign is < 3.0° or > 27.0°",
      "Cross-verify with patient age or exact moment of confinement to bed"
    ],
    "traditional_interpretation": "William Lilly and Jane Ridder-Patrick instruct that if the Ascendant is less than 3 degrees (especially in signs of short ascension), the ailment is in its embryonic inception—premature for definitive astrological judgment. If 27 degrees or more, the illness is already deeply ingrained, past its crisis turning point, or the matter has slipped out of the practitioner's direct control.",
    "interpretation_tamil": "வில்லியம் லில்லி மற்றும் ஜேன் ரிடர்-பேட்ரிக் கூற்றுப்படி, ஒரு நோய்விவர அல்லது பிரசன்ன லக்னம் 3 பாகைக்குள் இருந்தால், நோய் இன்னும் முழுமையாக வெளிப்படவில்லை (ஆரம்ப நிலை); 27 பாகைக்கு மேல் இருந்தால், நோய் முற்றிவிட்டது அல்லது முக்கிய திருப்புமுனையைத் தாண்டிவிட்டது என்பதைக் குறிக்கும். மருத்துவர் மிகுந்த எச்சரிக்கையுடன் அணுக வேண்டும்.",
    "anatomical_system": "Diagnostic Timing, Disease Chronicity, Crisis Turning Point",
    "modifiers": "If native is very young or facial marks match Ascendant sign, judgement is permissible.",
    "conflicting_indications": "Chart taken at exact second patient took to bed overrides stricture.",
    "remedy_en": "Patient observation; postpone invasive interventions until symptoms consolidate; monitor critical Moon days (45°, 90°, 135°, 180°); support natural vital forces.",
    "remedy_ta": "நோயாளிக்கு உடனடியாக தீவிர சிகிச்சைகள் செய்யாமல் கவனிப்பில் வைத்தல்; சந்திரனின் முக்கிய திருப்புமுனை நாட்களைக் (Critical Days) கண்காணித்தல்; உடலின் இயற்கை குணமளிக்கும் ஆற்றலை ஆதரித்தல்."
  },
  {
    "id": "jrp_decumbiture_via_combusta",
    "name": "Decumbiture Stricture: Moon in Via Combusta (15° Libra – 15° Scorpio)",
    "name_tamil": "நோய்விவர ஜோதிட எச்சரிக்கை: எரிந்த பாதையில் சந்திரன் (15° துலாம் – 15° விருச்சிகம்)",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 6: The Decumbiture Chart (Strictures on Judgement)",
    "category": "Vedic Birth Chart",
    "system": "vedic",
    "required_placements": "Natal or Decumbiture Moon between 195°00' and 225°00' (15° Libra to 15° Scorpio)",
    "mandatory_conditions": [
      "Moon is situated in the fiery, turbulent zone of Via Combusta",
      "Scrutinize extreme subjective fear, toxic exacerbations, and emotional turbulence"
    ],
    "traditional_interpretation": "The Moon in the Via Combusta ('the fiery way' from 15° Libra to 15° Scorpio) signifies a state of severe internal toxic agitation, heightened subjective distress, and unpredictable vital flow. Traditional masters warn that remedies may produce paradoxical reactions or that the patient is panicking beyond objective symptom severity.",
    "interpretation_tamil": "சந்திரன் 'எரிந்த பாதையில்' (15° துலாம் முதல் 15° விருச்சிகம் வரை) இருக்கும் போது, உடலின் பிராண ஓட்டம் அமைதியிழந்து, நச்சுத் தேக்கம் மற்றும் தீவிர மனப்பயத்தை உண்டாக்கும். மருந்துகள் எதிர்பாராத விளைவுகளைத் தரலாம்; நோயாளியின் பயத்தை ஆற்றுப்படுத்துவதே முதல் தேவையாகும்.",
    "anatomical_system": "Emotional Limbic Axis, Autonomic Fear Response, Toxic Elimination",
    "modifiers": "Spica conjunction at 24° Libra softens distress.",
    "conflicting_indications": "Native having natal Ascendant in this degree range tolerates this transit naturally.",
    "remedy_en": "Cooling demulcent remedies; quiet emotional grounding; calming silver-charged water; Rock Rose Bach flower for panic; avoiding sudden aggressive medical changes.",
    "remedy_ta": "குளிர்ச்சியான சாந்தப்படுத்தும் மருந்துகள்; மன அமைதி தியானம்; வெள்ளி நாணயம் இட்டு காய்ச்சிய நீர்; பீதி நீங்க ராக் ரோஸ் மலர் மருந்து; அவசர அறுவை சிகிச்சைகளை தவிர்த்தல்."
  },
  {
    "id": "jrp_decumbiture_void_moon",
    "name": "Decumbiture Condition: Void of Course Moon (No Acute Organic Progression)",
    "name_tamil": "நோய்விவர நிலை: தொடர்பற்ற சந்திரன் (Void of Course Moon)",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 6: The Decumbiture Chart (The Moon's Aspects)",
    "category": "Vedic Birth Chart",
    "system": "vedic",
    "required_placements": "Moon makes no further major applying aspect before leaving its current sign",
    "mandatory_conditions": [
      "Moon is Void of Course",
      "Examine whether immediate health panic will dissolve without structural organic harm"
    ],
    "traditional_interpretation": "When the Moon is Void of Course, traditional horary and medical rules judge that 'nothing will come of the matter'. While remedies may act sluggishly, the acute crisis will not advance into fatal organic destruction. It advises against elective surgery during this period as procedures may fail to accomplish their desired objective or require repeat intervention.",
    "interpretation_tamil": "சந்திரன் ஒரு ராசியைக் கடக்கும் முன் எவ்வித கிரக பார்வையோ சேர்க்கையோ பெறாமல் (Void of Course) இருக்கும் போது, அப்போதைய நோய் அச்சுறுத்தல் பெரும் ஆபத்தாக மாறாது. எனினும், இக்காலத்தில் திட்டமிடப்பட்ட அறுவை சிகிச்சைகளைத் தவிர்ப்பது நல்லது; ஏனெனில் சிகிச்சை முழு பலன் தராமல் போகலாம்.",
    "anatomical_system": "Autonomic Stabilization, Post-Surgical Healing Tone, Visceral Recovery",
    "modifiers": "Void Moon in Taurus, Cancer, Sagittarius, or Pisces is less vulnerable.",
    "conflicting_indications": "Strong Ascendant lord guarantees smooth recuperation.",
    "remedy_en": "Rest and recuperation; postponing non-emergency surgery until Moon enters a fruitful sign and makes benefic applying aspects; Clematis Bach flower; gentle supportive fluids.",
    "remedy_ta": "முழுமையான ஓய்வு; அவசரமில்லாத அறுவை சிகிச்சைகளை சந்திரன் சுப கிரக பார்வை பெறும் வரை ஒத்திவைத்தல்; கிளிமேடிஸ் மலர் மருந்து; எளிய திரவ உணவுகள் உட்கொள்ளுதல்."
  },
  {
    "id": "jrp_culpeper_ascendant_fortification",
    "name": "Culpeper's Golden Injunction: Fortification of the Ascendant Lord",
    "name_tamil": "கல்பேப்பரின் முதன்மை விதி: லக்னாதிபதியை பலப்படுத்துதல்",
    "source": "A Handbook of Medical Astrology (Jane Ridder-Patrick)",
    "chapter_verse": "Chapter 6: The Decumbiture Chart & Chapter 9: Materia Medica",
    "category": "Vedic Mitigation",
    "system": "vedic",
    "required_placements": "Evaluates natal Ascendant sign and its governing planetary ruler",
    "mandatory_conditions": [
      "Identify the lord of the Ascendant and its elemental temperament",
      "Apply Culpeper's 1st Rule of Astro-Medicine to fortify bodily integrity"
    ],
    "traditional_interpretation": "Nicholas Culpeper's foundational rule, highlighted by Jane Ridder-Patrick: 'Fortify the body with herbs of the nature of the Lord of the Ascendant, 'tis no matter whether he be a Fortune or Infortune in this case.' Strengthening the Lagna lord reinforces the vital conductor of prana, ensuring the host constitution resists and expels all pathogenic incursions.",
    "interpretation_tamil": "17-ஆம் நூற்றாண்டு மாமேதை நிக்கோலஸ் கல்பேப்பர் மற்றும் ஜேன் ரிடர்-பேட்ரிக் வலியுறுத்தும் முதன்மை விதி: லக்னாதிபதி சுபரோ அசுபரோ, அவரது தன்மைக்குரிய மூலிகைகள் மற்றும் உணவுகளால் உடலின் உயிர் சக்தியை பலப்படுத்த வேண்டும். லக்னாதிபதி வலுப்பெற்றால் உடல் எத்தகைய நோயையும் எதிர்த்து வெல்லும்.",
    "anatomical_system": "Vital Host Constitution, Pranic Conductivity, Cellular Rebuilding",
    "modifiers": "Exaltation or own-sign placement of Lagna lord provides inherent constitutional invulnerability.",
    "conflicting_indications": "Combustion of Lagna lord demands extra gentle non-heating remedies.",
    "remedy_en": "Consume botanicals, whole foods, and cell salts ruled by your Ascendant lord; wear the corresponding harmonizing metal or gemstone; practice targeted breathing aligned with your rising element.",
    "remedy_ta": "உங்கள் லக்னாதிபதிக்குரிய மூலிகைகள், முழு தானியங்கள் மற்றும் தாது உப்புகளை உட்கொள்ளுதல்; லக்னாதிபதிக்குரிய ரத்தினம் அல்லது உலோகத்தை அணிதல்; லக்ன பூத தத்துவத்திற்குரிய மூச்சுப் பயிற்சி செய்தல்."
  }
];

function evaluateJaneRidderPatrickCompendium(
  horoscope: HoroscopeResponse,
  houseOccupants: Record<number, string[]>,
  planetHouse: Record<string, number>,
  planetSign: Record<string, number>,
  houseToSign: Record<number, number>
): JaneRidderPatrickCompendium {
  const asc = (horoscope as any).ascendant;
  const ascLong = Number(asc?.longitude || 0.0);
  const ascDeg = ascLong % 30.0;
  const lagnaSign = houseToSign[1] || 1;
  const moonSign = planetSign["Moon"] || 1;
  const sunSign = planetSign["Sun"] || 1;

  const planetsList: any[] = (horoscope as any).planets || [];
  const pLongs: Record<string, number> = {};
  planetsList.forEach((p: any) => {
    if (p.name && p.longitude !== undefined) {
      pLongs[p.name] = Number(p.longitude);
    }
  });

  const moonLong = pLongs["Moon"] || 0.0;
  const sunLong = pLongs["Sun"] || 0.0;
  const marsLong = pLongs["Mars"] || 0.0;
  const satLong = pLongs["Saturn"] || 0.0;

  // 1. Decumbiture & Strictures
  const isAscEarlyOrLate = ascDeg < 3.0 || ascDeg > 27.0;
  let ascStrictureNote = `Ascendant is at ${ascDeg.toFixed(2)}° (within 3°–27° safe zone), radical for decumbiture evaluation.`;
  if (ascDeg < 3.0) {
    ascStrictureNote = `Ascendant is at ${ascDeg.toFixed(2)}° (< 3°): According to William Lilly and Jane Ridder-Patrick, this indicates the condition is premature or in its embryonic stage.`;
  } else if (ascDeg > 27.0) {
    ascStrictureNote = `Ascendant is at ${ascDeg.toFixed(2)}° (> 27°): The condition is chronic, deeply entrenched, or past its decisive turning point.`;
  }

  const moonInViaCombusta = moonLong >= 225.0 && moonLong <= 255.0;
  const saturnInSeventh = planetHouse["Saturn"] === 7;
  const seventhHouseAfflicted = saturnInSeventh || planetHouse["Mars"] === 7;
  const ascLordCombust = (planetHouse["Saturn"] === 1) || Math.abs(ascLong - sunLong) < 8.5;

  const decumbiture: JaneDecumbitureEvaluation = {
    ascendant_degree: Number(ascDeg.toFixed(2)),
    is_asc_early_or_late: isAscEarlyOrLate,
    asc_stricture_note: ascStrictureNote,
    moon_in_via_combusta: moonInViaCombusta,
    moon_void_of_course: false,
    saturn_in_seventh: saturnInSeventh,
    seventh_house_afflicted: seventhHouseAfflicted,
    asc_lord_combust_or_saturn_in_first: ascLordCombust,
    critical_days_cycle_en: "Moon 45° (semi-square, ~3.5 days), 90° (square, 7th day - acute crisis), 135° (sesquiquadrate, 10.5 days), 180° (opposition, 14th day - decisive turning point).",
    critical_days_cycle_ta: "சந்திரன் 45° (3.5 நாட்கள்), 90° (7வது நாள் - முக்கியமான நெருக்கடி), 135° (10.5 நாட்கள்), 180° (14வது நாள் - தீர்மானகரமான திருப்பம்).",
    sidedness_indicator: [1, 2, 3, 10, 11, 12].includes(planetHouse["Moon"] || 1) ? "Eastern / Right Sided" : "Western / Left Sided",
  };

  // 2. Arabian Parts
  const sunHouse = planetHouse["Sun"] || 1;
  const isDay = sunHouse >= 7 && sunHouse <= 12;

  const partSicknessDeg = isDay
    ? ((ascLong + marsLong - satLong) % 360.0 + 360.0) % 360.0
    : ((ascLong + satLong - marsLong) % 360.0 + 360.0) % 360.0;
  const partSurgeryDeg = ((ascLong + satLong - marsLong) % 360.0 + 360.0) % 360.0;
  const partDeathDeg = ((ascLong + 240.0 - moonLong) % 360.0 + 360.0) % 360.0;

  const signNames = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"];
  const formatCoord = (deg: number) => {
    const sIdx = Math.floor(deg / 30.0) % 12;
    const d = deg % 30.0;
    const wholeD = Math.floor(d);
    const m = Math.floor((d - wholeD) * 60.0);
    return `${wholeD}°${m.toString().padStart(2, "0")}' ${signNames[sIdx]}`;
  };

  const arabianParts: JaneArabianParts = {
    part_of_sickness_deg: Number(partSicknessDeg.toFixed(2)),
    part_of_sickness_sign: signNames[Math.floor(partSicknessDeg / 30.0) % 12],
    part_of_sickness_coord: formatCoord(partSicknessDeg),
    part_of_surgery_deg: Number(partSurgeryDeg.toFixed(2)),
    part_of_surgery_sign: signNames[Math.floor(partSurgeryDeg / 30.0) % 12],
    part_of_surgery_coord: formatCoord(partSurgeryDeg),
    part_of_death_deg: Number(partDeathDeg.toFixed(2)),
    part_of_death_sign: signNames[Math.floor(partDeathDeg / 30.0) % 12],
    part_of_death_coord: formatCoord(partDeathDeg),
    clinical_notes_en: "Classical Hermetic Arabian Parts: Sickness (underlying chronic weakness), Surgery (operative trauma risk), Death (crisis endurance point).",
    clinical_notes_ta: "பாரம்பரிய அரேபிய புள்ளிகள்: நோய் புள்ளி (அடிப்படை பலவீனம்), அறுவைசிகிச்சை புள்ளி, நெருக்கடி புள்ளி.",
  };

  // 3. Elemental Analysis
  let fire = 0, earth = 0, air = 0, water = 0;
  Object.values(planetSign).forEach((s) => {
    if ([1, 5, 9].includes(s)) fire++;
    else if ([2, 6, 10].includes(s)) earth++;
    else if ([3, 7, 11].includes(s)) air++;
    else if ([4, 8, 12].includes(s)) water++;
  });

  const elemCounts = [{ name: "Earth", val: earth }, { name: "Fire", val: fire }, { name: "Air", val: air }, { name: "Water", val: water }];
  elemCounts.sort((a, b) => b.val - a.val);
  const domElem = elemCounts[0].name;
  const lowElem = elemCounts[elemCounts.length - 1].name;
  const dietKey = elemCounts[0].val >= 4 ? `Excess ${domElem}` : `Low ${lowElem}`;
  const elemBal = (JANE_ELEMENTAL_BALANCING_RAW as any)[dietKey] || (JANE_ELEMENTAL_BALANCING_RAW as any)["Excess Earth"];

  const elementalAnalysis: JaneElementalAnalysis = {
    air_count: air,
    fire_count: fire,
    water_count: water,
    earth_count: earth,
    moon_element: [1, 5, 9].includes(moonSign) ? "Fire" : [2, 6, 10].includes(moonSign) ? "Earth" : [3, 7, 11].includes(moonSign) ? "Air" : "Water",
    dominant_element: domElem,
    deficient_element: lowElem,
    dietary_balancing_en: `Constitutional Temperament: ${domElem} dominant, ${lowElem} deficient. Recommended balancing diet: ${elemBal?.balancing_diet || ""} Avoid: ${elemBal?.avoid || ""}`,
    dietary_balancing_ta: `பூத தத்துவம்: ${domElem} ஆதிக்கம், ${lowElem} குறைவு. சமநிலைப்படுத்தும் உணவு முறை: ${elemBal?.balancing_diet || ""} தவிர்க்க வேண்டியவை: ${elemBal?.avoid || ""}`,
    herbal_classes_indicated: typeof elemBal?.indicated_herbs === "string" ? elemBal.indicated_herbs.split(",").map((s: string) => s.trim()) : [],
  };

  // 4. Cell Salts (12)
  const cellSalts: JaneCellSaltCorrespondence[] = JANE_CELL_SALTS_RAW.map((cs: any) => ({
    sign: cs.sign,
    sign_ta: cs.sign_ta,
    cell_salt: cs.cell_salt,
    abbreviation: cs.abbreviation,
    physiological_action_en: cs.physiological_action_en,
    physiological_action_ta: cs.physiological_action_ta,
    is_native_sign: cs.sign === signNames[lagnaSign - 1] || cs.sign === signNames[moonSign - 1],
  }));

  // 5. Bach Flowers (12)
  const bachFlowers: JaneBachFlowerCorrespondence[] = JANE_BACH_FLOWERS_RAW.map((bf: any) => ({
    sign: bf.sign,
    sign_ta: bf.sign_ta,
    flower_remedy: bf.flower_remedy,
    emotional_archetype_en: bf.emotional_archetype_en,
    emotional_archetype_ta: bf.emotional_archetype_ta,
    is_native_sign: bf.sign === signNames[lagnaSign - 1] || bf.sign === signNames[moonSign - 1],
  }));

  // 6. Acupuncture Meridians (12)
  const acupunctureMeridians: JaneAcupunctureMeridian[] = JANE_ACUPUNCTURE_MERIDIANS_RAW.map((am: any) => ({
    sign: am.sign,
    sign_ta: am.sign_ta,
    meridian: am.meridian,
    meridian_ta: am.meridian_ta,
    is_native_sign: am.sign === signNames[lagnaSign - 1],
  }));

  // 7. Matched Rules
  const matchedRules: MedicalRule[] = JANE_RULES_RAW.map((r: any) => {
    let isActive = false;
    const cond = r.conditions || {};
    const p1 = cond.planet_1;
    const p2 = cond.planet_2;
    const aspect = cond.aspect;
    const house = cond.house;

    if (p1 && p2 && aspect && pLongs[p1] !== undefined && pLongs[p2] !== undefined) {
      const diff = Math.abs(pLongs[p1] - pLongs[p2]);
      const shortestDiff = diff > 180.0 ? 360.0 - diff : diff;
      const orb = Number(cond.orb_deg || 8.0);
      if (aspect === "conjunction" && shortestDiff <= orb) isActive = true;
      else if (aspect === "square" && Math.abs(shortestDiff - 90.0) <= orb) isActive = true;
      else if (aspect === "opposition" && Math.abs(shortestDiff - 180.0) <= orb) isActive = true;
      else if (aspect === "hard_aspect") {
        if (shortestDiff <= orb || Math.abs(shortestDiff - 90.0) <= orb || Math.abs(shortestDiff - 180.0) <= orb) {
          isActive = true;
        }
      }
    } else if (p1 && house && planetHouse[p1] === house) {
      isActive = true;
    }

    return {
      id: r.id,
      name: r.name,
      name_tamil: r.name_tamil,
      source: r.source,
      chapter_verse: r.chapter_verse,
      category: r.category,
      system: r.system,
      required_placements: r.required_placements || [],
      mandatory_conditions: r.mandatory_conditions || [],
      traditional_interpretation: r.traditional_interpretation,
      interpretation_tamil: r.interpretation_tamil,
      anatomical_system: r.anatomical_system,
      modifiers: r.modifiers || [],
      conflicting_indications: r.conflicting_indications || [],
      is_active: isActive,
      status: isActive ? "Qualifying" : "Not Qualifying",
      triggered_positions: [r.source],
      planets_involved: r.planets_involved || [],
      relevant_houses: r.relevant_houses || [],
      conditions: r.conditions || {},
      remedy_en: r.remedy_en,
      remedy_ta: r.remedy_ta,
    };
  });

  const stagesOfTherapy = [
    {
      stage: 1,
      title_en: "Identification & Acknowledgment",
      title_ta: "கண்டறிதல் மற்றும் ஒப்புக்கொள்ளுதல்",
      description_en: "Recognizing underlying planetary tensions and physiological imbalances without judgment.",
      description_ta: "உடலில் உள்ள கிரக அழுத்தங்கள் மற்றும் சமநிலையின்மையை அறிதல்.",
    },
    {
      stage: 2,
      title_en: "Exploration & Understanding",
      title_ta: "ஆராய்ச்சி மற்றும் புரிதல்",
      description_en: "Understanding how psychosomatic stresses and dietary triggers affect the corresponding organs.",
      description_ta: "மன அழுத்தங்கள் மற்றும் உணவுப் பழக்கங்கள் உறுப்புகளை எவ்வாறு பாதிக்கின்றன என்பதைப் புரிந்துகொள்ளுதல்.",
    },
    {
      stage: 3,
      title_en: "Upgrading & Conscious Integration",
      title_ta: "மேம்படுத்துதல் மற்றும் ஒருங்கிணைத்தல்",
      description_en: "Employing constitutional herbs, cell salts, and lifestyle adjustments to upgrade physical vitality.",
      description_ta: "மூலிகைகள், திசு உப்புகள் மற்றும் வாழ்க்கைமுறை மாற்றங்கள் மூலம் ஆரோக்கியத்தை மேம்படுத்துதல்.",
    },
  ];

  return {
    book_title: JANE_METADATA_RAW.book_title,
    book_title_ta: JANE_METADATA_RAW.book_title_ta,
    author: JANE_METADATA_RAW.author,
    publisher: JANE_METADATA_RAW.publisher,
    alphabet_framework: JANE_METADATA_RAW.alphabet_framework,
    three_crosses: JANE_THREE_CROSSES_RAW,
    decumbiture,
    arabian_parts: arabianParts,
    elemental_analysis: elementalAnalysis,
    culpeper_therapeutic_rules: JANE_CULPEPER_RULES_RAW,
    stages_of_therapy: stagesOfTherapy,
    cell_salts: cellSalts,
    bach_flowers: bachFlowers,
    acupuncture_meridians: acupunctureMeridians,
    matched_rules: matchedRules,
  };
}


function evaluateHeinrichDaathCompendium(
  horoscope: HoroscopeResponse,
  houseOccupants: Record<number, string[]>,
  planetHouse: Record<string, number>,
  planetSign: Record<string, number>,
  houseToSign: Record<number, number>,
  liveTransits?: LiveTransitsResponse | null
): HeinrichDaathCompendium {
  const ascSignIdx = houseToSign[1] || 1;
  const sunSign = planetSign["Sun"] || 1;
  const moonSign = planetSign["Moon"] || 1;
  const sixthSign = houseToSign[6] || (((ascSignIdx - 1 + 5) % 12) + 1);

  // 1. 12 Sign Anatomical Rulerships
  const signsAnatomy: DaathSignAnatomy[] = DAATH_SIGNS_RAW.map((s: any) => ({
    sign_index: s.sign_index,
    sign_name_en: s.sign_name_en,
    sign_name_ta: s.sign_name_ta,
    symbolic_quality: s.symbolic_quality,
    principal_bones: s.principal_bones || [],
    muscles: s.muscles || [],
    arteries: s.arteries || [],
    veins: s.veins || [],
    morbid_actions: s.morbid_actions || [],
    kidney_pelvis_distinction: s.kidney_pelvis_distinction || null,
    is_native_ascendant: s.sign_index === ascSignIdx,
    is_native_sun_sign: s.sign_index === sunSign,
    is_native_moon_sign: s.sign_index === moonSign,
    is_native_sixth_house: s.sign_index === sixthSign,
  }));

  // 2. 9 Planets Biodynamics and Chart Status
  const planetsList: any[] = (horoscope as any).planets || [];
  const pLongs: Record<string, number> = {};
  const pRetro: Record<string, boolean> = {};
  planetsList.forEach((p: any) => {
    if (p.name && p.longitude !== undefined) {
      pLongs[p.name] = Number(p.longitude);
      pRetro[p.name] = Boolean(p.is_retrograde);
    }
  });

  const satHouse = planetHouse["Saturn"] || 1;
  const marsHouse = planetHouse["Mars"] || 1;
  const jupSign = planetSign["Jupiter"] || 1;
  const marsSign = planetSign["Mars"] || 1;
  const sunHouse = planetHouse["Sun"] || 1;

  const planetsBiodynamics: DaathPlanetAction[] = DAATH_PLANETS_RAW.map((p: any) => {
    const pName = p.planet;
    let chartCond = "Normal / Balanced";
    const isRx = Boolean(pRetro[pName]);

    if (pName === "Mars") {
      if (marsSign === 4) chartCond = "Perverted / Atonic Heat (Fall in Cancer - Gastric Irritability)";
      else if (marsSign === 1 || marsSign === 8) chartCond = "Tonic / High Tension (Ruler in Own Sign)";
      else if (isRx) chartCond = "Retrograde / Internalized Combustive Heat";
    } else if (pName === "Saturn") {
      if (planetSign["Saturn"] === 10 || planetSign["Saturn"] === 11) chartCond = "Tonic Structural Limitation (Strong in Own Sign)";
      else if (planetSign["Saturn"] === 1) chartCond = "Atonic / Excessive Depressive Cold (Fall in Aries)";
      else if (isRx) chartCond = "Retrograde Centripetal Contraction";
    } else if (pName === "Jupiter") {
      if (isRx) chartCond = "Retrograde (Weakened Life-Preserving Power - Däath Doctrine)";
      else if ([9, 12, 4].includes(jupSign)) chartCond = "Tonic / Splendid Vital Preservation";
    } else if (pName === "Sun") {
      if (sunSign === 7) chartCond = "Atonic Vitality (Fall in Libra)";
      else if (sunSign === 1 || sunSign === 5) chartCond = "Tonic / High Caloric Vitality";
    } else if (pName === "Moon") {
      if (moonSign === 8) chartCond = "Atonic / Perverted Radical Moisture (Fall in Scorpio)";
      else if (moonSign === 2 || moonSign === 4) chartCond = "Tonic Fluidic Plenitude";
    }

    return {
      planet: pName,
      planet_ta: p.planet_ta,
      esoteric_title: p.esoteric_title,
      biodynamic_motion: p.biodynamic_motion,
      polarity: p.polarity,
      functional_group: p.functional_group,
      tissue_building: p.tissue_building,
      elemental_degrees: p.elemental_degrees,
      salient_pathognomy: p.salient_pathognomy,
      typical_drugs: p.typical_drugs || [],
      typical_plants: p.typical_plants || [],
      therapeutic_properties: p.therapeutic_properties || [],
      metals_minerals: p.metals_minerals || [],
      native_chart_condition: chartCond,
    };
  });

  // 3. Temperaments & Quadruplicities
  const fireSigns = [1, 5, 9];
  const earthSigns = [2, 6, 10];
  const airSigns = [3, 7, 11];
  const waterSigns = [4, 8, 12];

  const cardinalSigns = [1, 4, 7, 10];
  const fixedSigns = [2, 5, 8, 11];
  const mutableSigns = [3, 6, 9, 12];

  let fireCount = 0;
  let earthCount = 0;
  let airCount = 0;
  let waterCount = 0;
  let cardinalCount = 0;
  let fixedCount = 0;
  let mutableCount = 0;

  Object.values(planetSign).forEach((s) => {
    if (fireSigns.includes(s)) fireCount++;
    if (earthSigns.includes(s)) earthCount++;
    if (airSigns.includes(s)) airCount++;
    if (waterSigns.includes(s)) waterCount++;
    if (cardinalSigns.includes(s)) cardinalCount++;
    if (fixedSigns.includes(s)) fixedCount++;
    if (mutableSigns.includes(s)) mutableCount++;
  });

  const counts = [
    { name: "Sanguine (Air)", count: airCount },
    { name: "Choleric/Bilious (Fire)", count: fireCount },
    { name: "Nervous (Earth)", count: earthCount },
    { name: "Lymphatic (Water)", count: waterCount },
  ];
  counts.sort((a, b) => b.count - a.count);
  const dominantTemperament = counts[0].name;

  const temperamentsAndCrosses = {
    dominant_temperament: dominantTemperament,
    fire_count: fireCount,
    earth_count: earthCount,
    air_count: airCount,
    water_count: waterCount,
    cardinal_count: cardinalCount,
    fixed_count: fixedCount,
    mutable_count: mutableCount,
    temperament_definitions: DAATH_TEMPERAMENTS_AND_CROSSES_RAW.temperaments,
    cross_definitions: DAATH_TEMPERAMENTS_AND_CROSSES_RAW.quadruplicities,
  };

  // 4. Antipathic Therapeutics
  const antipathicTherapeutics: DaathAntipathicTherapy[] = DAATH_ANTIPATHIC_RAW.map((at: any) => ({
    category: at.category,
    category_ta: at.category_ta,
    opposing_polarity_rule: at.opposing_polarity_rule,
    afflicting_planetary_force: at.afflicting_planetary_force,
    curative_planetary_remedy: at.curative_planetary_remedy,
    substances_and_application: at.substances_and_application,
  }));

  // 5. Seven Ages of Man
  let birthYear = 1990;
  try {
    const meta = (horoscope as any).metadata;
    if (meta?.birth_date) {
      birthYear = parseInt(String(meta.birth_date).split("-")[0], 10);
    }
  } catch {}
  const currentYear = new Date().getFullYear();
  const nativeAge = Math.max(0, currentYear - birthYear);

  const sevenAgesOfMan: DaathPlanetaryPeriod[] = DAATH_PLANETARY_PERIODS_RAW.map((sap: any) => ({
    planet: sap.planet,
    planet_ta: sap.planet_ta,
    start_age: sap.start_age,
    end_age: sap.end_age,
    age_label: sap.age_label,
    age_label_ta: sap.age_label_ta,
    biological_development: sap.biological_development,
    astrological_vulnerability: sap.astrological_vulnerability,
    is_native_current_age: nativeAge >= sap.start_age && nativeAge < sap.end_age,
  }));

  // 6. Decumbiture
  const decumbitureAndCycles: DaathDecumbitureCriticalDays = {
    lunar_critical_cycles: DAATH_DECUMBITURE_RAW.lunar_critical_cycles,
    lunar_phases_metabolism: DAATH_DECUMBITURE_RAW.lunar_phases_metabolism,
    climacteric_seven_year_law: DAATH_DECUMBITURE_RAW.climacteric_seven_year_law,
    climacteric_seven_year_law_ta: DAATH_DECUMBITURE_RAW.climacteric_seven_year_law_ta,
  };

  // 7. Strength Evaluation
  const signRulers: Record<number, string> = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
    5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
    9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter",
  };
  const mutualReceptions: string[] = [];
  const checkedPairs = new Set<string>();
  Object.entries(planetSign).forEach(([p1, s1]) => {
    const ruler1 = signRulers[Number(s1)];
    if (ruler1 && ruler1 !== p1 && planetSign[ruler1]) {
      const s2 = planetSign[ruler1];
      const ruler2 = signRulers[Number(s2)];
      if (ruler2 === p1) {
        const pairKey = [p1, ruler1].sort().join("-");
        if (!checkedPairs.has(pairKey)) {
          checkedPairs.add(pairKey);
          mutualReceptions.push(
            `Mutual Reception: ${p1} in sign of ${ruler1} (${SIGN_NAMES_EN[Number(s1)] || ""}) <-> ${ruler1} in sign of ${p1} (${SIGN_NAMES_EN[Number(s2)] || ""})`
          );
        }
      }
    }
  });
  if (mutualReceptions.length === 0) {
    mutualReceptions.push("No strict mutual reception by domicile sign detected in chart.");
  }

  const retroPlanets = Object.entries(pRetro).filter(([_, isRx]) => isRx).map(([p]) => p);
  const retroStr = retroPlanets.length > 0 ? `Retrograde planets: ${retroPlanets.join(", ")} (internalized biodynamic force)` : "No major retrograde planets (direct kinetic action)";

  const strengthEvaluation: DaathStrengthEvaluation = {
    drikbalam_aspect_summary: "Harmonious aspects (trines/sextiles) act anabolically promoting vitality; squares/oppositions act katabolically provoking inflammation or structural breakdown.",
    sthanabalam_summary: `Radix Ascendant in ${SIGN_NAMES_EN[ascSignIdx] || ""}, Sun in ${SIGN_NAMES_EN[sunSign] || ""}, Moon in ${SIGN_NAMES_EN[moonSign] || ""}. Strong domicile/exalted planets strengthen vitality and tissue resilience.`,
    nisargikabalam_mutual_receptions: mutualReceptions,
    mundane_strength_summary: "Planets in angles (1, 4, 7, 10) manifest acute outward symptoms; planets in cadent 6th and 12th houses produce chronic, insidious visceral tendencies.",
    motional_strength_summary: retroStr,
    directional_hexis_vs_diathesis: "Däath distinguishes Hexis (inborn constitutional habitus) from Diathesis (transient morbid disposition activated by progressions/transits). Radix indicates the organic seed; current planetary cycles awaken the dormant pathognomy.",
  };

  // 8. Rules evaluation
  function isHardAsp(deg1: number, deg2: number): [boolean, string] {
    let diff = Math.abs(deg1 - deg2) % 360.0;
    if (diff > 180.0) diff = 360.0 - diff;
    if (diff <= 9.0) return [true, `Conjunction (${diff.toFixed(1)}° orb)`];
    if (diff >= 82.0 && diff <= 98.0) return [true, `Square (${diff.toFixed(1)}°)`];
    if (diff >= 171.0 && diff <= 180.0) return [true, `Opposition (${diff.toFixed(1)}°)`];
    return [false, ""];
  }

  const sunDeg = pLongs["Sun"] || 0.0;
  const moonDeg = pLongs["Moon"] || 0.0;
  const marsDeg = pLongs["Mars"] || 0.0;
  const satDeg = pLongs["Saturn"] || 0.0;
  const mercDeg = pLongs["Mercury"] || 0.0;
  const venDeg = pLongs["Venus"] || 0.0;
  const jupDeg = pLongs["Jupiter"] || 0.0;
  const uranusDeg = pLongs["Uranus"] || 0.0;
  const neptuneDeg = pLongs["Neptune"] || 0.0;

  const matchedRules: MedicalRule[] = DAATH_RULES_RAW.map((rDef: any) => {
    const rId = rDef.id;
    let isActive = false;
    const trigPos: string[] = [];
    let planetsInv: string[] = [];
    let relHouses: number[] = [];

    if (rId === "daath_diphtheria_fixed_signs") {
      const fixedPls = Object.entries(planetSign).filter(([_, s]) => fixedSigns.includes(s)).map(([p]) => p);
      const [hasSatMoon] = isHardAsp(satDeg, moonDeg);
      const [hasMarsSun] = isHardAsp(marsDeg, sunDeg);
      if ((fixedSigns.includes(ascSignIdx) || fixedPls.length >= 3) && (hasSatMoon || hasMarsSun || ascSignIdx === 2 || ascSignIdx === 8)) {
        isActive = true;
        trigPos.push(`Fixed signs prominent (${fixedPls.length} planets), Ascendant in ${SIGN_NAMES_EN[ascSignIdx] || ""}`);
        planetsInv = (hasSatMoon || hasMarsSun) ? ["Saturn", "Mars"] : ["Moon"];
        relHouses = [1, 12, 6];
      }
    } else if (rId === "daath_renal_pelvis_calculus") {
      const [hasVenSat, vDesc] = isHardAsp(venDeg, satDeg);
      const scorpioPls = Object.entries(planetSign).filter(([_, s]) => s === 8).map(([p]) => p);
      if (hasVenSat || scorpioPls.includes("Saturn") || scorpioPls.includes("Mars")) {
        isActive = true;
        trigPos.push(`Renal Pelvis zone: ${hasVenSat ? "Venus-Saturn " + vDesc : "Scorpio tenanted by " + scorpioPls.join(", ")}`);
        planetsInv = hasVenSat ? ["Venus", "Saturn"] : scorpioPls;
        relHouses = [planetHouse["Saturn"] || 8, 8];
      }
    } else if (rId === "daath_brights_disease_nephritis") {
      const [hasVenSat] = isHardAsp(venDeg, satDeg);
      const [hasVenJup] = isHardAsp(venDeg, jupDeg);
      const [hasSunJup] = isHardAsp(sunDeg, jupDeg);
      if ((hasVenSat || hasVenJup || hasSunJup) && (waterSigns.includes(moonSign) || fixedCount >= 3)) {
        isActive = true;
        trigPos.push(`Bright's disease indicators: Venus/Sun aspected by Saturn/Jupiter; Moon in water sign (${SIGN_NAMES_EN[moonSign] || ""})`);
        planetsInv = ["Venus", "Jupiter", "Saturn"];
        relHouses = [7, 8, 6];
      }
    } else if (rId === "daath_ocular_blindness_rule") {
      const [hasLumAsp] = isHardAsp(sunDeg, moonDeg);
      const eyeSigns = [1, 2, 4, 5, 10, 11];
      const [hasSatAff] = isHardAsp(satDeg, sunDeg);
      const [hasMarsAff] = isHardAsp(marsDeg, moonDeg);
      if ((hasLumAsp || (eyeSigns.includes(sunSign) && eyeSigns.includes(moonSign))) && (hasSatAff || hasMarsAff)) {
        isActive = true;
        trigPos.push(`Ocular affliction: Luminaries in sensitive signs (${SIGN_NAMES_EN[sunSign] || ""}/${SIGN_NAMES_EN[moonSign] || ""}) aspected by Mars/Saturn`);
        planetsInv = ["Sun", "Moon", "Saturn"];
        relHouses = [1, 2, 12];
      }
    } else if (rId === "daath_pulmonary_consumption_phthisis") {
      const hasGemAff = ["Saturn", "Mars", "Rahu"].some((p) => planetSign[p] === 3);
      const lumInCadentCommon = (mutableSigns.includes(sunSign) && (sunHouse === 6 || sunHouse === 12)) ||
        (mutableSigns.includes(moonSign) && (planetHouse["Moon"] === 6 || planetHouse["Moon"] === 12));
      if (hasGemAff || lumInCadentCommon) {
        isActive = true;
        trigPos.push("Pulmonary affliction: Gemini tenanted or Luminaries in cadent mutable signs (6th/12th)");
        planetsInv = ["Mercury", "Saturn"];
        relHouses = [3, 6, 12];
      }
    } else if (rId === "daath_mental_genius_vs_derangement") {
      const [hasMercMars, mmDesc] = isHardAsp(mercDeg, marsDeg);
      const [hasMercSat, msDesc] = isHardAsp(mercDeg, satDeg);
      const [hasMoonMerc, momDesc] = isHardAsp(moonDeg, mercDeg);
      if (hasMercMars || hasMercSat || hasMoonMerc) {
        isActive = true;
        trigPos.push(`Mental dynamics: ${hasMercMars ? mmDesc : (hasMercSat ? msDesc : momDesc)}`);
        planetsInv = hasMercMars ? ["Mercury", "Mars"] : ["Mercury", "Moon"];
        relHouses = [planetHouse["Mercury"] || 1, 3, 9];
      }
    } else if (rId === "daath_varicose_veins_lower_limbs") {
      const venInAq = planetSign["Venus"] === 11;
      const moonInAq = moonSign === 11;
      const hasAff = ["Mars", "Saturn", "Rahu"].some((p) => planetSign[p] === 11);
      if (venInAq || moonInAq || (hasAff && planetHouse["Venus"] === 11)) {
        isActive = true;
        trigPos.push("Aquarius (calves/venous return) tenanted by Venus/Moon/Malefics");
        planetsInv = ["Venus", "Mars"];
        relHouses = [11, 1];
      }
    } else if (rId === "daath_hip_joint_coxalgia_rule") {
      const sagAff = planetSign["Saturn"] === 9 || planetSign["Mars"] === 9;
      const [hasMarsSat] = isHardAsp(marsDeg, satDeg);
      if (sagAff || (hasMarsSat && mutableSigns.includes(planetSign["Saturn"]))) {
        isActive = true;
        trigPos.push("Sagittarius (hips/femur) influenced by Saturn and Mars");
        planetsInv = ["Saturn", "Mars"];
        relHouses = [9, 6];
      }
    } else if (rId === "daath_gastritis_peptic_irritability") {
      if (marsSign === 4 || (marsHouse === 4 && moonSign === 4)) {
        isActive = true;
        trigPos.push("Mars in Cancer (fall sign, stomach seat) - acute gastric irritability");
        planetsInv = ["Mars", "Moon"];
        relHouses = [4, 6];
      }
    } else if (rId === "daath_spasms_ruptures_uranus") {
      if (uranusDeg > 0) {
        const [hasUMars] = isHardAsp(uranusDeg, marsDeg);
        const [hasUMoon] = isHardAsp(uranusDeg, moonDeg);
        if (hasUMars || hasUMoon) {
          isActive = true;
          trigPos.push("Uranian spasmodic aspect to Mars or Moon");
          planetsInv = ["Uranus", "Mars"];
          relHouses = [1, 6, 8];
        }
      }
    } else if (rId === "daath_coma_psychic_drugs_neptune") {
      if (neptuneDeg > 0) {
        const [hasNepMoon] = isHardAsp(neptuneDeg, moonDeg);
        const [hasNepMerc] = isHardAsp(neptuneDeg, mercDeg);
        if (hasNepMoon || hasNepMerc || moonSign === 12) {
          isActive = true;
          trigPos.push("Neptune aspect to Moon/Mercury or Moon in 12th/Pisces");
          planetsInv = ["Neptune", "Moon"];
          relHouses = [12, 6];
        }
      }
    } else if (rId === "daath_short_life_early_infancy") {
      const [hasSunSat] = isHardAsp(sunDeg, satDeg);
      const lowVitSigns = [4, 10, 12];
      if (hasSunSat && (lowVitSigns.includes(sunSign) || lowVitSigns.includes(moonSign))) {
        isActive = true;
        trigPos.push(`Sun afflicted by Saturn in low vitality sign (${SIGN_NAMES_EN[sunSign] || ""})`);
        planetsInv = ["Sun", "Saturn"];
        relHouses = [1, 8];
      }
    } else if (rId === "daath_cardiac_aneurism_spinal_rule") {
      const leoAff = ["Mars", "Saturn", "Rahu"].some((p) => planetSign[p] === 5);
      const [hasSunMars, smDesc] = isHardAsp(sunDeg, marsDeg);
      if (leoAff || hasSunMars || (sunHouse === 5 && marsHouse === 5)) {
        isActive = true;
        trigPos.push(`Cardiac & spinal focus: Leo afflicted or Sun-Mars ${smDesc}`);
        planetsInv = ["Sun", "Mars"];
        relHouses = [5, 1];
      }
    } else if (rId === "daath_enteritis_intestinal_digestion") {
      const virgoAff = ["Mars", "Saturn", "Rahu"].some((p) => planetSign[p] === 6);
      if (virgoAff || marsHouse === 6 || satHouse === 6) {
        isActive = true;
        trigPos.push("Virgo / 6th house (chylification/enteric absorption) influenced by Mars or Saturn");
        planetsInv = ["Mars", "Saturn"];
        relHouses = [6];
      }
    } else if (rId === "daath_cutaneous_epidermal_saturn") {
      const capAff = ["Mars", "Saturn", "Rahu"].some((p) => planetSign[p] === 10);
      if (capAff || satHouse === 1 || satHouse === 6) {
        isActive = true;
        trigPos.push(`Capricorn / Saturn prominent on epidermal boundary (House ${satHouse})`);
        planetsInv = ["Saturn"];
        relHouses = [10, satHouse];
      }
    } else if (rId === "daath_blood_poisoning_oxygenation") {
      const aqAff = ["Mars", "Saturn", "Rahu"].some((p) => planetSign[p] === 11);
      if (aqAff || satHouse === 11) {
        isActive = true;
        trigPos.push("Aquarius (fixed air / carbonic acid elimination) influenced by Mars/Saturn");
        planetsInv = ["Saturn", "Mars"];
        relHouses = [11];
      }
    }

    const condItems = (rDef.mandatory_conditions || []).map((c: string) => ({
      condition: c,
      passed: isActive,
      detail: `Condition status: ${isActive ? "Fulfilled" : "Not satisfied"} in native's chart`,
    }));

    return {
      id: rDef.id,
      name: rDef.name,
      name_tamil: rDef.name_tamil,
      source: rDef.source,
      chapter_verse: rDef.chapter_verse,
      category: rDef.category,
      system: rDef.system,
      required_placements: Array.isArray(rDef.required_placements) ? rDef.required_placements.join(", ") : String(rDef.required_placements || ""),
      mandatory_conditions: rDef.mandatory_conditions || [],
      traditional_interpretation: rDef.traditional_interpretation,
      interpretation_tamil: rDef.interpretation_tamil,
      anatomical_system: rDef.anatomical_system,
      modifiers: Array.isArray(rDef.modifiers) ? rDef.modifiers.join(", ") : (rDef.modifiers ? String(rDef.modifiers) : ""),
      conflicting_indications: Array.isArray(rDef.conflicting_indications) ? rDef.conflicting_indications.join(", ") : (rDef.conflicting_indications ? String(rDef.conflicting_indications) : ""),
      is_active: isActive,
      status: isActive ? "Qualifying" : "Not Qualifying",
      triggered_positions: trigPos,
      planets_involved: planetsInv,
      relevant_houses: relHouses,
      conditions: condItems,
      remedy_en: rDef.remedy_en,
      remedy_ta: rDef.remedy_ta,
    };
  });

  return {
    book_title: DAATH_METADATA_RAW.book_title,
    book_title_ta: DAATH_METADATA_RAW.book_title_ta,
    author: DAATH_METADATA_RAW.author,
    publisher: DAATH_METADATA_RAW.publisher,
    historical_foundation: DAATH_METADATA_RAW.historical_foundation,
    core_philosophy_en: DAATH_METADATA_RAW.core_philosophy_en,
    core_philosophy_ta: DAATH_METADATA_RAW.core_philosophy_ta,
    signs_anatomy: signsAnatomy,
    planets_biodynamics: planetsBiodynamics,
    temperaments_and_crosses: temperamentsAndCrosses,
    antipathic_therapeutics: antipathicTherapeutics,
    seven_ages_of_man: sevenAgesOfMan,
    decumbiture_and_cycles: decumbitureAndCycles,
    strength_evaluation: strengthEvaluation,
    matched_rules: matchedRules,
  };
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

  if (dasa?.active_period?.mahadasha) {
    mahaLord = dasa.active_period.mahadasha;
    bhuktiLord = dasa.active_period.antardasha || null;
    antaraLord = dasa.active_period.pratyantardasha || null;
    startIso = dasa.active_period.target_date_iso || null;
  }

  // Dynamic Dasa Tree Traversal if active_period is missing or incomplete
  if ((mahaLord === "Unknown" || !bhuktiLord) && dasa?.dasa_tree && dasa.dasa_tree.length > 0) {
    const nowJd = Date.now() / 86400000 + 2440587.5;
    const liveMaha = dasa.dasa_tree.find((m) => m.start_jd <= nowJd && nowJd < m.end_jd);
    if (liveMaha) {
      mahaLord = liveMaha.lord;
      const sub = liveMaha.sub_periods || [];
      const liveBhukti = sub.find((b) => b.start_jd <= nowJd && nowJd < b.end_jd);
      if (liveBhukti) {
        bhuktiLord = liveBhukti.lord;
        const andhar = liveBhukti.sub_periods || [];
        const liveAntara = andhar.find((a) => a.start_jd <= nowJd && nowJd < a.end_jd);
        if (liveAntara) {
          antaraLord = liveAntara.lord;
        }
      }
    }
  }

  if (mahaLord === "Unknown" && dasa?.birth_dasa_lord) {
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
    dr_krishna_kumar_compendium: evaluateDrKrishnaKumarCompendium(
      horoscope,
      houseOccupants,
      planetHouse,
      planetSign,
      houseToSign
    ),
    dr_chatterjee_compendium: evaluateDrChatterjeeCompendium(
      horoscope,
      houseOccupants,
      planetHouse,
      planetSign,
      houseToSign,
      liveTransits
    ),
    max_heindel_compendium: evaluateMaxHeindelCompendium(
      horoscope,
      houseOccupants,
      planetHouse,
      planetSign,
      houseToSign
    ),
    jane_ridder_patrick_compendium: evaluateJaneRidderPatrickCompendium(
      horoscope,
      houseOccupants,
      planetHouse,
      planetSign,
      houseToSign
    ),
    heinrich_daath_compendium: evaluateHeinrichDaathCompendium(
      horoscope,
      houseOccupants,
      planetHouse,
      planetSign,
      houseToSign,
      liveTransits
    ),
  };
}
