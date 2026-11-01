"use client";

import React, { useState, useMemo } from "react";
import {
  MedicalAstrologyResponse,
  MedicalRule,
  ProgenyShapaDetail,
  HoroscopeResponse,
  PlanetInfo,
} from "@/lib/types";
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  HeartPulse,
  Sparkles,
  BookOpen,
  Filter,
  Search,
  Droplet,
  Droplets,
  Pill,
  Award,
  Stethoscope,
  Compass,
  Calendar,
  Layers,
  ChevronDown,
  ChevronUp,
  Info,
  Flame,
  Activity,
  Baby,
} from "lucide-react";

interface ChartMatchedRulesSectionProps {
  medicalData: MedicalAstrologyResponse;
  horoscope?: HoroscopeResponse | null;
  language: "en" | "ta";
  onSelectRule?: (rule: MedicalRule) => void;
}

// -----------------------------------------------------------------------------
// COMPREHENSIVE CLASSICAL & AYURVEDIC REMEDY LOOKUP MATRIX
// -----------------------------------------------------------------------------
interface TraditionalRemedyItem {
  mantra_ta: string;
  mantra_en: string;
  diet_herbs_ta: string;
  diet_herbs_en: string;
  charity_ta: string;
  charity_en: string;
  lifestyle_therapy_ta: string;
  lifestyle_therapy_en: string;
  temples_ta: string;
  temples_en: string;
}

const PLANETARY_REMEDY_MATRIX: Record<string, TraditionalRemedyItem> = {
  Sun: {
    mantra_ta: "ஓம் நமோ பகவதே ராமச்சந்திராய | ஆதித்ய ஹிருதய ஸ்தோத்திரம் மற்றும் காயத்ரி ஜபம்.",
    mantra_en: "Om Namo Bhagavate Ramachandraya | Recite Aditya Hridaya Stotram and Surya Gayatri daily at sunrise.",
    diet_herbs_ta: "செப்புப் பாத்திரத்தில் வைத்த நீர் (தாமிர ஜலம்), நெல்லிக்காய், கோதுமை, பட்டை மற்றும் குங்குமப்பூ கலந்த உணவு.",
    diet_herbs_en: "Copper vessel water (Tamra Jal), Indian Gooseberry (Amla), unrefined wheat, cinnamon, and saffron.",
    charity_ta: "ஞாயிற்றுக்கிழமைகளில் கோதுமை, வெல்லம், செப்புப் பாத்திரம் அல்லது மாணிக்கம் தானம் செய்தல்.",
    charity_en: "Donate wheat, jaggery, copper utensils, or ruby to elders on Sunday mornings.",
    lifestyle_therapy_ta: "சூரிய நமஸ்காரம், அதிகாலை சூரிய ஒளி குளியல் (ஆரஞ்சு நிற கதிர்வீச்சு), கண் பாதுகாப்பு பயிற்சிகள்.",
    lifestyle_therapy_en: "Daily Surya Namaskar, early morning sun exposure (Orange/Amber chromotherapy), eye-cooling exercises.",
    temples_ta: "சூரியனார் கோவில் (தஞ்சாவூர்), கோனார்க் சூரிய கோவில்.",
    temples_en: "Suryanar Kovil (Thanjavur, Tamil Nadu), Konark Sun Temple.",
  },
  Moon: {
    mantra_ta: "ஓம் நம சிவாய | சந்திர காயத்ரி & ருத்ர பாராயணம்.",
    mantra_en: "Om Namah Shivaya | Recite Chandra Gayatri and Sri Rudram.",
    diet_herbs_ta: "வெள்ளி நாணயம் இட்டு காய்ச்சிய நீர் (ரௌப்ய ஜலம்), வெதுவெதுப்பான பால், மஞ்சள், தர்பூசணி, சீரக நீர்.",
    diet_herbs_en: "Silver-charged boiled water (Roupya Jal), lukewarm milk with turmeric, cumin water, hydrating foods.",
    charity_ta: "திங்கட்கிழமைகளில் பச்சரிசி, பால், சர்க்கரை, வெண்ணெய் அல்லது வெள்ளை வஸ்திரம் தானம்.",
    charity_en: "Donate raw rice, fresh milk, butter, camphor, or white cloth on Mondays.",
    lifestyle_therapy_ta: "தியானம், பிராணாயாமம், இரவு நேர குளிர் பானங்களைத் தவிர்த்தல், வெண்மை/வெள்ளி நிற சிகிச்சை.",
    lifestyle_therapy_en: "Meditation, deep breathing (Pranayama), avoiding cold night drinks, White/Silver chromotherapy.",
    temples_ta: "திங்களூர் கைலாசநாதர் கோவில் (தஞ்சாவூர்), மதுரை மீனாட்சி சுந்தரேஸ்வரர் கோவில்.",
    temples_en: "Thingalur Kailasanathar Temple (Thanjavur, Tamil Nadu), Madurai Meenakshi Sundareswarar Temple.",
  },
  Mars: {
    mantra_ta: "ஓம் சரவணபவாய நம | அங்காரக காயத்ரி & கந்த சஷ்டி கவசம்.",
    mantra_en: "Om Saravanabhavaya Namah | Recite Angaraka Gayatri and Kanda Sashti Kavacham.",
    diet_herbs_ta: "இளநீர், கற்றாழை சாறு, மாதுளம் பழம், கொத்தமல்லி விதை ஊறவைத்த நீர், அதிமதுரம்.",
    diet_herbs_en: "Fresh coconut water, aloe vera juice, pomegranate, coriander seed infusion, liquorice (Yashtimadhu).",
    charity_ta: "செவ்வாய்க்கிழமைகளில் துவரம்பருப்பு, சிவப்பு வஸ்திரம், ரத்த தானம் செய்தல்.",
    charity_en: "Donate red lentils (masoor/toor dal), red garments, or participate in voluntary blood donation.",
    lifestyle_therapy_ta: "அதி உஷ்ணத்தை தணிக்கும் உணவு முறை, காரம் குறைத்தல், சிவப்பு ரத்தின நிற சிகிச்சை, மிதமான உடற்பயிற்சி.",
    lifestyle_therapy_en: "Pitta-cooling diet, cutting excessive chilies/deep frying, Ruby red ray harmonization, measured cardio.",
    temples_ta: "வைத்தீஸ்வரன் கோவில் (மயிலாடுதுறை), பழனி மற்றும் திருச்செந்தூர் முருகன் கோவில்.",
    temples_en: "Vaitheeswaran Kovil (Mayiladuthurai, Tamil Nadu), Palani & Tiruchendur Murugan Temples.",
  },
  Mercury: {
    mantra_ta: "ஓம் நமோ நாராயணாய | புதன் காயத்ரி & விஷ்ணு சஹஸ்ரநாமம்.",
    mantra_en: "Om Namo Narayanaya | Recite Budha Gayatri and Sri Vishnu Sahasranamam.",
    diet_herbs_ta: "பாசிப்பயறு (முளைகட்டிய பயறு), துளசி இலை நீர், புதினா, வெந்தயக் கீரை, நாவல் பழம்.",
    diet_herbs_en: "Sprouted green gram (moong), sacred basil (Tulsi) water, fresh mint, fenugreek leaves, jamun fruit.",
    charity_ta: "புதன்கிழமைகளில் பச்சைப்பயறு, பேனா/புத்தகங்கள் ஏழை மாணவர்களுக்கு தானம், மரக்கன்றுகள் நடுதல்.",
    charity_en: "Donate green moong, books/stationery to underprivileged students, plant green shady trees on Wednesdays.",
    lifestyle_therapy_ta: "நரம்பு மண்டலத்தை அமைதிப்படுத்தும் யோகாசனம், பிராணாயாமம், மரகதப் பச்சை நிற சிகிச்சை.",
    lifestyle_therapy_en: "Nervous-calming yoga (Nadi Shodhana), Emerald green chromotherapy, regular digital detox.",
    temples_ta: "திருவெண்காடு சுவேதாரண்யேஸ்வரர் கோவில் (நாகப்பட்டினம்), மதுரை சொக்கநாதர் கோவில்.",
    temples_en: "Thiruvenkadu Swetharanyeswarar Temple (Nagapattinam, Tamil Nadu), Srirangam Ranganathaswamy Temple.",
  },
  Jupiter: {
    mantra_ta: "ஓம் நமோ பகவதே தட்சிணாமூர்த்தயே | குரு காயத்ரி & ஸ்ரீ தட்சிணாமூர்த்தி அஷ்டகம்.",
    mantra_en: "Om Namo Bhagavate Dakshinamurtaye | Recite Guru Gayatri and Sri Dakshinamurthy Ashtakam.",
    diet_herbs_ta: "மஞ்சள், சுக்கு வெந்நீர், முளைகட்டிய கடலை, நெல்லிக்காய் சாறு, வெந்தயம்.",
    diet_herbs_en: "Turmeric, dried ginger infusion, roasted/sprouted Bengal gram, Amla juice, fenugreek seeds.",
    charity_ta: "வியாழக்கிழமைகளில் கொண்டைக்கடலை, மஞ்சள் வஸ்திரம், இனிப்பு, சான்றோர்களுக்கு பணிவிடை செய்தல்.",
    charity_en: "Donate Bengal gram (chana dal), yellow clothes, honey/sweets, serve elderly scholars on Thursdays.",
    lifestyle_therapy_ta: "வயிற்றுப் பகுதி கொழுப்பைக் குறைக்கும் நடைபயிற்சி, அதிக சர்க்கரை தவிர்த்தல், பொன்மஞ்சள் நிற சிகிச்சை.",
    lifestyle_therapy_en: "Brisk post-meal walking to reduce visceral fat, strict reduction of refined carbohydrates, Golden Yellow chromotherapy.",
    temples_ta: "ஆலங்குடி ஆபத்சகாயேஸ்வரர் கோவில் (திருவாரூர்), திருச்செந்தூர் குரு ஸ்தலம்.",
    temples_en: "Alangudi Apatsahayeswarar Temple (Tiruvarur, Tamil Nadu), Thiruchendur Murugan Sannidhi.",
  },
  Venus: {
    mantra_ta: "ஓம் ஸ்ரீம் மஹாலக்ஷ்ம்யை நம | சுக்கிர காயத்ரி & கனகதாரா ஸ்தோத்திரம்.",
    mantra_en: "Om Shreem Mahalakshmyai Namah | Recite Shukra Gayatri and Sri Kanakadhara Stotram.",
    diet_herbs_ta: "கற்றாழை, நெல்லி, தாழம்பூ நீர், மோர், வெண்பூசணி சாறு, பட்டைப் பொடி.",
    diet_herbs_en: "Aloe vera pulp, Indian gooseberry, buttermilk with rock salt, white ash gourd juice, cinnamon powder.",
    charity_ta: "வெள்ளிக்கிழமைகளில் நெய், மொச்சைப்பயறு, வெள்ளி, ஏழைப் பெண்களுக்கு புத்தாடை தானம்.",
    charity_en: "Donate pure cow ghee, white field beans (mochai), silver, or clothes to underprivileged brides.",
    lifestyle_therapy_ta: "சிறுநீரக நச்சு நீக்கம், போதுமான நீர் அருந்துதல், வைரம்/வெண்மை நிற சிகிச்சை, தாமரை மலர் வழிபாடு.",
    lifestyle_therapy_en: "Renal hydration hygiene, Diamond White/Rose chromotherapy, clean sleep environment.",
    temples_ta: "கஞ்சனூர் அக்னீஸ்வரர் கோவில் (தஞ்சாவூர்), ஸ்ரீரங்கம் தாயார் சன்னதி.",
    temples_en: "Kanjanur Agneeswarar Temple (Thanjavur, Tamil Nadu), Srirangam Ranganayaki Thayar Sannidhi.",
  },
  Saturn: {
    mantra_ta: "ஓம் நீலாஞ்சன ஸமாபாஸம் ரவிபுத்ரம் யமாக்ரஜம் | மகா மிருத்யுஞ்சய ஜபம் & சனி காயத்ரி.",
    mantra_en: "Om Nilanjana Samabhasam Raviputram Yamagrajam | Maha Mrityunjaya Japa and Shani Gayatri.",
    diet_herbs_ta: "நல்லெண்ணெய் தேய்த்துக் குளித்தல், திரிபலா சூரணம், எள், கறுப்பு உளுந்து, சுடுநீர் அருந்துதல்.",
    diet_herbs_en: "Weekly sesame oil body massage (Abhyanga), Triphala churnam, sesame seeds, black gram, warm water.",
    charity_ta: "சனிக்கிழமைகளில் நல்லெண்ணெய் தீபம் ஏற்றுதல், கறுப்பு எள் தானம், ஊனமுற்றோருக்கு உணவு & கம்பளி அளித்தல்.",
    charity_en: "Light sesame oil deepam, donate black sesame, feed differently-abled persons and street animals on Saturdays.",
    lifestyle_therapy_ta: "மூட்டு வாதத்தைத் தவிர்க்கும் எளிய யோகாசனம், மலச்சிக்கல் நீக்கம், இரும்புச் சத்து, ஊதா/நீல நிற சிகிச்சை.",
    lifestyle_therapy_en: "Joint-gentle mobility yoga, preventing chronic constipation with dietary fibre, Indigo/Violet chromotherapy.",
    temples_ta: "திருநள்ளாறு தர்பாரண்யேஸ்வரர் கோவில் (காரைக்கால்), திருக்கொள்ளிக்காடு அக்னீஸ்வரர் கோவில்.",
    temples_en: "Thirunallar Dharbaranyeswarar Temple (Karaikal), Thirukollikadu Agneeswarar Temple.",
  },
  Rahu: {
    mantra_ta: "ஓம் அர்தகாயம் மஹாவீர்யம் சந்த்ராதித்ய விமர்தனம் | துர்க்கா கவசம் & ராகு காயத்ரி.",
    mantra_en: "Om Ardhakayam Mahaviryam Chandraditya Vimardanam | Durga Kavacham and Rahu Gayatri.",
    diet_herbs_ta: "சுத்தமான வெதுவெதுப்பான கொதித்து ஆறிய நீர், இஞ்சி, மிளகு, மஞ்சள், இயற்கை நச்சுநீக்க மூலிகைகள்.",
    diet_herbs_en: "Boiled and cooled lukewarm water, ginger, black pepper, turmeric, gentle detoxifying herbs.",
    charity_ta: "கறுப்பு உளுந்து, தேங்காய், நீல வஸ்திரம் அல்லது ஏழைகளுக்கு காலணி தானம்.",
    charity_en: "Donate black gram (urad dal), whole coconuts, dark blue cloth, or footwear to the needy.",
    lifestyle_therapy_ta: "உணவுத் தூய்மை (வயிற்று ஒட்டுண்ணிகளைத் தவிர்த்தல்), இருண்ட அறைகளில் தூங்குதல், புகைப் பழக்கம் தவிர்த்தல்.",
    lifestyle_therapy_en: "Rigorous food hygiene against intestinal parasites, complete dark room sleeping, avoiding synthetic toxins.",
    temples_ta: "திருநாகேஸ்வரம் நாகநாதசுவாமி கோவில் (தஞ்சாவூர்), காளஹஸ்தி சிவன் கோவில்.",
    temples_en: "Thirunageswaram Naganathaswamy Temple (Thanjavur, Tamil Nadu), Srikalahasti Temple (Andhra Pradesh).",
  },
  Ketu: {
    mantra_ta: "ஓம் பலாச புஷ்ப சங்காசம் தாரகாக்ரஹ மஸ்தகம் | கணபதி அதர்வஷீர்ஷம் & கேது காயத்ரி.",
    mantra_en: "Om Palashapushpa Samkasam Tarakagraha Mastakam | Ganapati Atharvashirsha and Ketu Gayatri.",
    diet_herbs_ta: "கொள்ளு ரசம் (குதிரைப்பயறு), வெண்பூசணி, அஸ்வகந்தா சூரணம், வெதுவெதுப்பான சுக்கு நீர்.",
    diet_herbs_en: "Horse gram (kollu) soup, ash gourd juice, Ashwagandha powder with warm milk, dry ginger water.",
    charity_ta: "கொள்ளு தானம், பலவண்ண கம்பளி, ஏழைகளுக்கு மருத்துவ சிகிச்சை உதவி (மருந்து தானம்).",
    charity_en: "Donate horse gram, multi-coloured blankets, or sponsor essential medicines for impoverished patients.",
    lifestyle_therapy_ta: "தியானம், நரம்புத் தளர்ச்சி நீக்கும் உடற்பயிற்சி, ஆத்ம ஞான சிந்தனை, எளிய தூய வாழ்க்கை முறை.",
    lifestyle_therapy_en: "Daily meditation, gentle spine stretches, quiet spiritual study, minimalist clean living.",
    temples_ta: "கீழ்ப்பெரும்பள்ளம் நாகநாதசுவாமி கோவில் (நாகப்பட்டினம்), பிள்ளையார்பட்டி கற்பக விநாயகர் கோவில்.",
    temples_en: "Keezhperumpallam Naganathaswamy Temple (Nagapattinam, Tamil Nadu), Pillayarpatti Karpaga Vinayagar Temple.",
  },
};

// Specific Rule Remedy Enhancer
function resolveRemedyForRule(rule: MedicalRule): { en: string; ta: string } {
  if (rule.remedy_en && rule.remedy_ta) {
    return { en: rule.remedy_en, ta: rule.remedy_ta };
  }

  // Check planets involved
  const planet = rule.planets_involved && rule.planets_involved.length > 0 ? rule.planets_involved[0] : null;
  if (planet && PLANETARY_REMEDY_MATRIX[planet]) {
    const pRem = PLANETARY_REMEDY_MATRIX[planet];
    return {
      en: `${pRem.mantra_en} Herbs & Diet: ${pRem.diet_herbs_en}. Charity: ${pRem.charity_en}. Lifestyle: ${pRem.lifestyle_therapy_en}. Temples: ${pRem.temples_en}.`,
      ta: `${pRem.mantra_ta} மூலிகை & உணவு: ${pRem.diet_herbs_ta}. தானம்: ${pRem.charity_ta}. வாழ்வியல்: ${pRem.lifestyle_therapy_ta}. வழிபாட்டு ஸ்தலங்கள்: ${pRem.temples_ta}.`,
    };
  }

  // Fallback to general Parashari health remedies
  return {
    en: "Recite Sri Maha Mrityunjaya Japa 108 times daily; consume lukewarm water charged in copper/silver; perform Annadanam and worship Kuladevata on auspicious tithis.",
    ta: "தினசரி 108 முறை ஸ்ரீ மகா மிருத்யுஞ்சய ஜபம் செய்தல்; தாமிர அல்லது வெள்ளிப் பாத்திர நீர் அருந்துதல்; குலதெய்வ வழிபாடு மற்றும் அன்னதானம் செய்தல் சிறந்த பரிகாரமாகும்.",
  };
}

export function ChartMatchedRulesSection({
  medicalData,
  horoscope,
  language,
  onSelectRule,
}: ChartMatchedRulesSectionProps) {
  const [selectedFilter, setSelectedFilter] = useState<
    "all" | "protective" | "vedic" | "kp" | "krishna_kumar" | "chatterjee" | "heindel" | "ridder_patrick" | "daath" | "remedies_only"
  >("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [expandedCardId, setExpandedCardId] = useState<string | null>(null);

  const {
    vedic_analysis: vedic,
    kp_analysis: kpData,
    dr_krishna_kumar_compendium: krishnaKumar,
    dr_chatterjee_compendium: chatterjee,
    max_heindel_compendium: heindel,
    jane_ridder_patrick_compendium: ridderPatrick,
    heinrich_daath_compendium: daath,
  } = medicalData;

  // ---------------------------------------------------------------------------
  // 1. EXTRACT ALL ACTIVE / MATCHED RULES ACROSS ALL BOOKS AND SOURCES
  // ---------------------------------------------------------------------------

  // A. Classical Parashari / Vedic Matched Rules
  const matchedVedicRules = useMemo(() => {
    const list = vedic?.birth_chart?.triggered_rules || [];
    return list.filter((r: MedicalRule) => r.is_active);
  }, [vedic]);

  // Protective Shields (Arishta Bhanga, Arogya, Parijata)
  const protectiveShields = useMemo(() => {
    const shields: MedicalRule[] = [];
    matchedVedicRules.forEach((r: MedicalRule) => {
      if (r.category === "Vedic Mitigation" || r.id.includes("arishta_bhanga")) {
        shields.push(r);
      }
    });
    if (chatterjee?.golden_rules) {
      chatterjee.golden_rules.forEach((r: MedicalRule) => {
        if (
          r.is_active &&
          (r.id === "chatterjee_parijata_longevity" ||
            r.id === "chatterjee_disease_free_benefic_6th" ||
            r.id === "chatterjee_lagna_lord_shubha_kartari")
        ) {
          shields.push(r);
        }
      });
    }
    return shields;
  }, [matchedVedicRules, chatterjee]);

  // Non-shield Vedic Problem Rules
  const vedicProblemRules = useMemo(() => {
    return matchedVedicRules.filter((r: MedicalRule) => r.category !== "Vedic Mitigation" && !r.id.includes("arishta_bhanga"));
  }, [matchedVedicRules]);

  // B. KP Medical Matched Rules & CSL Significations
  const matchedKpRules = useMemo(() => {
    return (kpData?.kp_rules || []).filter((r: MedicalRule) => r.is_active);
  }, [kpData]);

  // C. Dr. Krishna Kumar Matched Items
  const matchedProgenyCurses = useMemo(() => {
    return (krishnaKumar?.progeny_shapas || []).filter((s: ProgenyShapaDetail) => s.is_indicated);
  }, [krishnaKumar]);

  const matchedKrishnaKumarYogas = useMemo(() => {
    const manasika = (krishnaKumar?.manasika_buddhi_yogas || []).filter((r: MedicalRule) => r.is_active);
    const organ = (krishnaKumar?.organ_specific_yogas || []).filter((r: MedicalRule) => r.is_active);
    return [...manasika, ...organ];
  }, [krishnaKumar]);

  // E. Max Heindel Matched Rules
  const matchedHeindelRules = useMemo(() => {
    return (heindel?.matched_rules || []).filter((r: MedicalRule) => r.is_active);
  }, [heindel]);

  // F. Jane Ridder-Patrick Matched Rules
  const matchedRidderPatrickRules = useMemo(() => {
    return (ridderPatrick?.matched_rules || []).filter((r: MedicalRule) => r.is_active);
  }, [ridderPatrick]);

  // G. Heinrich Däath Matched Rules
  const matchedDaathRules = useMemo(() => {
    return (daath?.matched_rules || []).filter((r: MedicalRule) => r.is_active);
  }, [daath]);

  // D. Dr. S. S. Chatterjee Matched Items
  const matchedChatterjeeGoldenRules = useMemo(() => {
    const positiveIds = new Set([
      "chatterjee_parijata_longevity",
      "chatterjee_disease_free_benefic_6th",
      "chatterjee_lagna_lord_shubha_kartari",
    ]);
    return (chatterjee?.golden_rules || []).filter((r: MedicalRule) => r.is_active && !positiveIds.has(r.id));
  }, [chatterjee]);

  const isDeathPointTriggered = chatterjee?.death_point?.transit_saturn_aspect_active || false;
  const isDiabetesIndicated = chatterjee?.diabetes_assessment && chatterjee.diabetes_assessment.risk_level !== "Low";

  // E. Unique Afflicted Planets Identified Across All Matched Rules
  const uniqueAfflictedPlanets = useMemo(() => {
    const set = new Set<string>();
    vedicProblemRules.forEach((r: MedicalRule) => (r.planets_involved || []).forEach((p: string) => set.add(p)));
    matchedChatterjeeGoldenRules.forEach((r: MedicalRule) => (r.planets_involved || []).forEach((p: string) => set.add(p)));
    matchedKrishnaKumarYogas.forEach((r: MedicalRule) => (r.planets_involved || []).forEach((p: string) => set.add(p)));
    matchedHeindelRules.forEach((r: MedicalRule) => (r.planets_involved || []).forEach((p: string) => set.add(p)));
    matchedRidderPatrickRules.forEach((r: MedicalRule) => (r.planets_involved || []).forEach((p: string) => set.add(p)));
    matchedDaathRules.forEach((r: MedicalRule) => (r.planets_involved || []).forEach((p: string) => set.add(p)));

    // Check houses 6, 8, 12 occupants from horoscope if available
    if (horoscope?.planets) {
      horoscope.planets.forEach((p: PlanetInfo) => {
        if (p.house && [6, 8, 12].includes(p.house)) {
          set.add(p.name);
        }
      });
    }

    if (isDiabetesIndicated) {
      set.add("Venus");
      set.add("Jupiter");
    }
    if (isDeathPointTriggered) {
      set.add("Saturn");
    }

    return Array.from(set).filter((p) => PLANETARY_REMEDY_MATRIX[p] !== undefined);
  }, [
    vedicProblemRules,
    matchedChatterjeeGoldenRules,
    matchedKrishnaKumarYogas,
    matchedHeindelRules,
    matchedRidderPatrickRules,
    matchedDaathRules,
    horoscope,
    isDiabetesIndicated,
    isDeathPointTriggered,
  ]);

  // Total Matched Count
  const totalMatchedCount =
    protectiveShields.length +
    vedicProblemRules.length +
    matchedKpRules.length +
    matchedProgenyCurses.length +
    matchedKrishnaKumarYogas.length +
    matchedChatterjeeGoldenRules.length +
    matchedHeindelRules.length +
    matchedRidderPatrickRules.length +
    matchedDaathRules.length +
    (isDeathPointTriggered ? 1 : 0) +
    (isDiabetesIndicated ? 1 : 0);

  // ---------------------------------------------------------------------------
  // FILTERING LOGIC
  // ---------------------------------------------------------------------------
  const searchFilter = (text: string) => {
    if (!searchQuery.trim()) return true;
    return text.toLowerCase().includes(searchQuery.toLowerCase());
  };

  const toggleExpand = (id: string) => {
    setExpandedCardId(expandedCardId === id ? null : id);
  };

  return (
    <div className="space-y-6">
      {/* 1. MASTER HEADER BANNER: Jaadhagathil Poruthugirathu */}
      <div className="rounded-2xl bg-gradient-to-r from-[#0F355A] via-[#154674] to-[#1E5A8E] p-5 sm:p-7 text-white shadow-md relative overflow-hidden">
        <div className="absolute right-0 top-0 translate-x-8 -translate-y-8 w-48 h-48 bg-emerald-500/10 rounded-full blur-2xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-5">
          <div className="space-y-2 max-w-2xl">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-400/25 border border-emerald-300/40 px-3 py-1 text-xs font-bold text-emerald-200">
                <CheckCircle2 className="w-4 h-4 text-emerald-300" />
                {language === "ta" ? "ஜாதகத்தில் பொருந்துகிறது" : "Chart-Matched Medical Rules"}
              </span>
              <span className="text-2xs text-white/80 bg-white/10 px-2 py-0.5 rounded font-mono">
                Cross-Tradition Unified Matrix
              </span>
            </div>

            <h2 className="text-xl sm:text-2xl font-serif font-bold tracking-tight text-white">
              {language === "ta"
                ? "ஜாதகத்தில் பொருந்தும் மருத்துவ ஜோதிட அமைப்புகள் & பரிகாரங்கள்"
                : "Medical Astrology Rules Matching This Horoscope & Prescribed Remedies"}
            </h2>

            <p className="text-xs sm:text-sm text-white/85 leading-relaxed">
              {language === "ta"
                ? "பராசர ஹோரா சாஸ்திரம், பலதீபிகை, சாராவளி, கிருஷ்ணமூர்த்தி பத்ததி (KP), டாக்டர் எஸ். கிருஷ்ண குமார் மற்றும் டாக்டர் எஸ்.எஸ். சாட்டர்ஜி ஆகிய அனைத்து மூல நூல்களும் ஆய்வு செய்யப்பட்டு, இந்த குறிப்பிட்ட ஜாதகத்திற்கு நேரடியாகப் பொருந்தும் அமைப்புகள் மற்றும் அவற்றுக்கான பாரம்பரிய பரிகாரங்கள் மட்டும் இங்கே வரிசைப்படுத்தப்பட்டுள்ளன."
                : "Cross-analyzing Parashara Hora Shastra, Phaladeepika, Saravali, Krishnamurti Paddhati (KP), Dr. S. Krishna Kumar, and Dr. S. S. Chatterjee to strictly present only the rules and classical remedies that match this native's chart."}
            </p>
          </div>

          {/* Quick Counter Box */}
          <div className="shrink-0 flex items-center gap-3">
            <div className="rounded-xl bg-white/10 border border-white/20 p-4 text-center backdrop-blur-xs min-w-[130px]">
              <div className="text-3xl font-black text-amber-300 font-mono">{totalMatchedCount}</div>
              <div className="text-2xs font-bold uppercase tracking-wider text-white/90 mt-1">
                {language === "ta" ? "பொருந்திய விதிகள்" : "Matched Rules"}
              </div>
            </div>

            <div className="rounded-xl bg-emerald-500/20 border border-emerald-300/30 p-4 text-center backdrop-blur-xs min-w-[130px]">
              <div className="text-3xl font-black text-emerald-300 font-mono">
                {uniqueAfflictedPlanets.length}
              </div>
              <div className="text-2xs font-bold uppercase tracking-wider text-emerald-100 mt-1">
                {language === "ta" ? "பரிகார கிரகங்கள்" : "Remedy Grahas"}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 2. FILTER & SEARCH CONTROLS */}
      <div className="bg-white rounded-xl border border-[#D9DEE7] p-3 sm:p-4 shadow-2xs space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          {/* Filter Pills */}
          <div className="flex items-center gap-1.5 overflow-x-auto text-xs pb-1 sm:pb-0 font-medium">
            <button
              type="button"
              onClick={() => setSelectedFilter("all")}
              className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer whitespace-nowrap ${
                selectedFilter === "all"
                  ? "bg-[#153F6B] text-white font-bold shadow-2xs"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
            >
              {language === "ta" ? `அனைத்தும் (${totalMatchedCount})` : `All (${totalMatchedCount})`}
            </button>

            {protectiveShields.length > 0 && (
              <button
                type="button"
                onClick={() => setSelectedFilter("protective")}
                className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer whitespace-nowrap flex items-center gap-1 ${
                  selectedFilter === "protective"
                    ? "bg-emerald-700 text-white font-bold shadow-2xs"
                    : "bg-emerald-50 text-emerald-800 hover:bg-emerald-100"
                }`}
              >
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                <span>{language === "ta" ? `ஆரோக்கிய யோகம் (${protectiveShields.length})` : `Shields (${protectiveShields.length})`}</span>
              </button>
            )}

            <button
              type="button"
              onClick={() => setSelectedFilter("vedic")}
              className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer whitespace-nowrap ${
                selectedFilter === "vedic"
                  ? "bg-[#B4872B] text-white font-bold shadow-2xs"
                  : "bg-amber-50 text-amber-900 hover:bg-amber-100"
              }`}
            >
              {language === "ta" ? `வேத ஜோதிடம் (${vedicProblemRules.length})` : `Vedic (${vedicProblemRules.length})`}
            </button>

            <button
              type="button"
              onClick={() => setSelectedFilter("kp")}
              className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer whitespace-nowrap ${
                selectedFilter === "kp"
                  ? "bg-[#153F6B] text-white font-bold shadow-2xs"
                  : "bg-blue-50 text-blue-900 hover:bg-blue-100"
              }`}
            >
              {language === "ta" ? `கே.பி. முறை (${matchedKpRules.length})` : `KP System (${matchedKpRules.length})`}
            </button>

            <button
              type="button"
              onClick={() => setSelectedFilter("krishna_kumar")}
              className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer whitespace-nowrap ${
                selectedFilter === "krishna_kumar"
                  ? "bg-[#69235B] text-white font-bold shadow-2xs"
                  : "bg-fuchsia-50 text-fuchsia-900 hover:bg-fuchsia-100"
              }`}
            >
              {language === "ta"
                ? `டாக்டர் கிருஷ்ண குமார் (${matchedProgenyCurses.length + matchedKrishnaKumarYogas.length})`
                : `Dr. Krishna Kumar (${matchedProgenyCurses.length + matchedKrishnaKumarYogas.length})`}
            </button>

            <button
              type="button"
              onClick={() => setSelectedFilter("chatterjee")}
              className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer whitespace-nowrap ${
                selectedFilter === "chatterjee"
                  ? "bg-[#69235B] text-white font-bold shadow-2xs"
                  : "bg-purple-50 text-purple-900 hover:bg-purple-100"
              }`}
            >
              {language === "ta"
                ? `டாக்டர் சாட்டர்ஜி (${matchedChatterjeeGoldenRules.length + (isDeathPointTriggered ? 1 : 0) + (isDiabetesIndicated ? 1 : 0)})`
                : `Dr. Chatterjee (${matchedChatterjeeGoldenRules.length + (isDeathPointTriggered ? 1 : 0) + (isDiabetesIndicated ? 1 : 0)})`}
            </button>

            <button
              type="button"
              onClick={() => setSelectedFilter("heindel")}
              className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer whitespace-nowrap ${
                selectedFilter === "heindel"
                  ? "bg-[#1B365D] text-white font-bold shadow-2xs"
                  : "bg-blue-50 text-blue-900 hover:bg-blue-100"
              }`}
            >
              {language === "ta"
                ? `மேக்ஸ் ஹெய்ண்டல் (${matchedHeindelRules.length})`
                : `Max Heindel (${matchedHeindelRules.length})`}
            </button>

            {matchedRidderPatrickRules.length > 0 && (
              <button
                type="button"
                onClick={() => setSelectedFilter("ridder_patrick")}
                className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer whitespace-nowrap ${
                  selectedFilter === "ridder_patrick"
                    ? "bg-teal-800 text-white font-bold shadow-2xs"
                    : "bg-teal-50 text-teal-900 hover:bg-teal-100"
                }`}
              >
                {language === "ta" ? "ரிடர்-பேட்ரிக்" : "Ridder-Patrick"} ({matchedRidderPatrickRules.length})
              </button>
            )}

            {matchedDaathRules.length > 0 && (
              <button
                type="button"
                onClick={() => setSelectedFilter("daath")}
                className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer whitespace-nowrap ${
                  selectedFilter === "daath"
                    ? "bg-indigo-800 text-white font-bold shadow-2xs"
                    : "bg-indigo-50 text-indigo-900 hover:bg-indigo-100"
                }`}
              >
                {language === "ta" ? "ஹென்ரிச் டாத்" : "Heinrich Däath"} ({matchedDaathRules.length})
              </button>
            )}

            <button
              type="button"
              onClick={() => setSelectedFilter("remedies_only")}
              className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer whitespace-nowrap flex items-center gap-1 ${
                selectedFilter === "remedies_only"
                  ? "bg-teal-700 text-white font-bold shadow-2xs"
                  : "bg-teal-50 text-teal-900 hover:bg-teal-100"
              }`}
            >
              <Pill className="w-3.5 h-3.5 text-teal-600" />
              <span>{language === "ta" ? "பரிகார அட்டவணை" : "Remedies Guide"}</span>
            </button>
          </div>

          {/* Search Box */}
          <div className="relative shrink-0 sm:w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={language === "ta" ? "கிரகம், உறுப்பு அல்லது நோய்..." : "Filter rules, organs, planet..."}
              className="w-full pl-9 pr-3 py-1.5 text-xs rounded-lg border border-slate-200 focus:outline-none focus:ring-1 focus:ring-sky-500"
            />
          </div>
        </div>
      </div>

      {/* ------------------------------------------------------------------- */}
      {/* SECTION 1: POSITIVE CONSTITUTIONAL & LONGEVITY SHIELDS (IF PRESENT) */}
      {/* ------------------------------------------------------------------- */}
      {(selectedFilter === "all" || selectedFilter === "protective") && protectiveShields.length > 0 && (
        <div className="rounded-xl border border-emerald-300 bg-emerald-50/80 p-5 shadow-2xs space-y-3">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-emerald-200 text-emerald-900 flex items-center justify-center shrink-0">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-emerald-950">
                {language === "ta"
                  ? "ஜாதகத்தில் அமைந்த இயற்கை நோய் எதிர்ப்பு & ஆயுள் பலம் (Protective Shields)"
                  : "Natural Immunity & Vital Longevity Shields Active in This Chart"}
              </h3>
              <p className="text-xs text-emerald-800">
                {language === "ta"
                  ? "இந்த சுப யோகங்கள் ஜாதகருக்கு இயல்பான நோய் எதிர்ப்பு ஆற்றலையும், தீவிர பாதிப்புகளிலிருந்து மீளும் வல்லமையையும் அளிக்கின்றன."
                  : "These classical benefic yogas confer strong constitutional vitality, resilience against acute illnesses, and longevity protections."}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
            {protectiveShields.map((shield: MedicalRule) => {
              const ruleName = language === "ta" && shield.name_tamil ? shield.name_tamil : shield.name;
              const ruleDesc =
                language === "ta" && shield.interpretation_tamil
                  ? shield.interpretation_tamil
                  : shield.traditional_interpretation;
              return (
                <div key={shield.id} className="rounded-lg bg-white border border-emerald-200 p-3.5 space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs font-bold text-emerald-900">{ruleName}</span>
                    <span className="text-2xs font-mono px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                      {shield.source}
                    </span>
                  </div>
                  <p className="text-xs text-slate-700 leading-relaxed">{ruleDesc}</p>
                  <div className="border-t border-emerald-100 pt-1.5 flex items-center justify-between text-2xs text-emerald-800">
                    <span>{language === "ta" ? "பாதுகாக்கும் நிலை: உறுதி செய்யப்பட்டது" : "Status: Active Protective Armor"}</span>
                    <span className="font-semibold">{shield.anatomical_system}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* SECTION 2: CLASSICAL PARASHARI / VEDIC MATCHED RULES & REMEDIES     */}
      {/* ------------------------------------------------------------------- */}
      {(selectedFilter === "all" || selectedFilter === "vedic") && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-serif font-bold text-[#183047] flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[#B4872B]" />
              <span>
                {language === "ta"
                  ? "பராசரர் & பாரம்பரிய வேத ஜோதிடப் பொருத்தம் (Parashari / Vedic Rules)"
                  : "Classical Vedic & Parashari Rules Matching This Horoscope"}
              </span>
            </h3>
            <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-amber-100 text-amber-900">
              {vedicProblemRules.length} {language === "ta" ? "விதிகள் பொருந்தியுள்ளன" : "Matched"}
            </span>
          </div>

          {vedicProblemRules.length === 0 ? (
            <div className="rounded-xl border border-slate-200 bg-white p-5 text-center space-y-1">
              <CheckCircle2 className="w-6 h-6 text-emerald-600 mx-auto" />
              <p className="text-xs text-slate-600 font-medium">
                {language === "ta"
                  ? "பாரம்பரிய வேத ஜோதிட நூல்களின்படி கடுமையான 6-ம் பாவ ரோக அமைப்புகள் இந்த ஜாதகத்தில் அமையவில்லை."
                  : "No severe classical 6th house malefic disease combinations are active in this birth chart."}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-3.5">
              {vedicProblemRules.filter((r: MedicalRule) => searchFilter(r.name + r.name_tamil + r.anatomical_system)).map((rule: MedicalRule) => {
                const ruleName = language === "ta" && rule.name_tamil ? rule.name_tamil : rule.name;
                const ruleDesc =
                  language === "ta" && rule.interpretation_tamil
                    ? rule.interpretation_tamil
                    : rule.traditional_interpretation;
                const isExpanded = expandedCardId === rule.id;
                const remedy = resolveRemedyForRule(rule);

                return (
                  <div
                    key={rule.id}
                    className="rounded-xl border border-slate-200 bg-white p-4 sm:p-5 shadow-2xs space-y-3 hover:border-amber-300 transition-colors"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-2.5">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-amber-50 text-amber-900 border border-amber-200">
                          {rule.chapter_verse || rule.source}
                        </span>
                        {rule.anatomical_system && (
                          <span className="text-xs font-semibold px-2 py-0.5 rounded bg-sky-50 text-sky-800 border border-sky-100">
                            {rule.anatomical_system}
                          </span>
                        )}
                      </div>
                      <span className="text-2xs font-bold px-2.5 py-0.5 rounded-full bg-rose-600 text-white self-start sm:self-auto">
                        {language === "ta" ? "ஜாதகத்தில் உறுதியானது" : "Chart Confirmed"}
                      </span>
                    </div>

                    <div>
                      <h4 className="text-sm sm:text-base font-bold text-slate-900">{ruleName}</h4>
                      <p className="text-xs text-slate-700 leading-relaxed mt-1">{ruleDesc}</p>
                    </div>

                    {/* Placements Triggered */}
                    {rule.triggered_positions && rule.triggered_positions.length > 0 && (
                      <div className="text-2xs bg-slate-50 rounded-lg p-2.5 text-slate-700 font-mono space-y-1">
                        <span className="font-bold text-slate-800 block">
                          {language === "ta" ? "பொருந்திய ஜாதக அமைப்புகள்:" : "Triggered Planetary Placements in Chart:"}
                        </span>
                        {rule.triggered_positions.map((pos: string, pIdx: number) => (
                          <div key={pIdx} className="flex items-center gap-1.5 text-slate-600">
                            <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                            <span>{pos}</span>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Prescribed Remedies Card */}
                    <div className="rounded-lg bg-amber-50/70 border border-amber-200/80 p-3.5 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-amber-950 flex items-center gap-1.5">
                          <Pill className="w-3.5 h-3.5 text-amber-700" />
                          {language === "ta" ? "சாஸ்திர பரிகாரங்கள் & வாழ்வியல் வழிகாட்டல்:" : "Prescribed Classical Remedies & Lifestyle:"}
                        </span>
                        <button
                          type="button"
                          onClick={() => toggleExpand(rule.id)}
                          className="text-2xs text-amber-900 font-semibold hover:underline flex items-center gap-0.5 cursor-pointer"
                        >
                          <span>{isExpanded ? (language === "ta" ? "சுருக்குக" : "Less") : (language === "ta" ? "விரிவாக" : "More")}</span>
                          {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                        </button>
                      </div>

                      <p className="text-xs text-amber-900 leading-relaxed font-medium">
                        {language === "ta" ? remedy.ta : remedy.en}
                      </p>

                      {isExpanded && (
                        <div className="text-2xs text-amber-950/90 pt-2 border-t border-amber-200/60 space-y-1.5">
                          <div>
                            <span className="font-bold">{language === "ta" ? "ஆயுர்வேத உணவு முறை: " : "Dietary Therapy: "}</span>
                            {language === "ta"
                              ? "உணவில் பித்த-வாத சமநிலையை கடைபிடித்தல், அதிக காரம், புளிப்பு மற்றும் இரவு நேர துரித உணவுகளை தவிர்த்தல்."
                              : "Adopt Sattvic dosha-balancing diet, moderate sodium/spices, avoid late-night heavy meals."}
                          </div>
                          <div>
                            <span className="font-bold">{language === "ta" ? "முக்கிய தானம்: " : "Charitable Action: "}</span>
                            {language === "ta"
                              ? "சம்பந்தப்பட்ட கிரகத்தின் காரக தானத்தை ஏழைகளுக்கு அளிப்பது நோயின் தாக்கத்தை குறைக்கும்."
                              : "Perform prescribed planetary grain/garment charity on the ruler's weekday."}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* SECTION 3: KP MEDICAL ASTROLOGY CSL RULES & REMEDIES               */}
      {/* ------------------------------------------------------------------- */}
      {(selectedFilter === "all" || selectedFilter === "kp") && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-serif font-bold text-[#183047] flex items-center gap-2">
              <Award className="w-4 h-4 text-[#153F6B]" />
              <span>
                {language === "ta"
                  ? "கே.பி. மருத்துவ ஜோதிடப் பொருத்தம் (KP 6th CSL Analysis)"
                  : "Krishnamurti Paddhati (KP) 6th Cuspal Sub-Lord Analysis"}
              </span>
            </h3>
            <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-blue-100 text-blue-900">
              {matchedKpRules.length + (kpData?.sixth_csl ? 1 : 0)} {language === "ta" ? "அமைப்புகள்" : "Items"}
            </span>
          </div>

          {/* 6th CSL Diagnostic Summary */}
          {kpData?.sixth_csl && (
            <div className="rounded-xl border border-blue-200 bg-blue-50/60 p-4 sm:p-5 space-y-3 shadow-2xs">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-blue-200/60 pb-2.5">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-900">
                    KP Reader IV Medical Diagnostics
                  </span>
                  <span className="text-xs font-semibold px-2 py-0.5 rounded bg-white text-blue-800 border border-blue-200">
                    6th Cusp Sub-Lord: {kpData.sixth_csl.csl_planet}
                  </span>
                </div>
                <span className="text-2xs font-bold px-2 py-0.5 rounded-full bg-blue-700 text-white self-start sm:self-auto">
                  {language === "ta" ? "உப-அதிபதி முடிவு" : "Cuspal Sub-Lord Governs"}
                </span>
              </div>

              <div className="space-y-1.5 text-xs text-blue-950">
                <p className="font-semibold">
                  {language === "ta"
                    ? `6-ம் உப-அதிபதி ${kpData.sixth_csl.csl_planet} நின்ற நட்சத்திராதிபதி: ${kpData.sixth_csl.csl_star_lord || "N/A"}`
                    : `6th Cuspal Sub-Lord ${kpData.sixth_csl.csl_planet} posited in the Star of: ${kpData.sixth_csl.csl_star_lord || "N/A"}`}
                </p>
                <p className="leading-relaxed">
                  {language === "ta" && kpData.sixth_csl.primary_signification_ta
                    ? kpData.sixth_csl.primary_signification_ta
                    : kpData.sixth_csl.primary_signification_en}
                </p>
              </div>

              {/* KP Prescribed Remedies */}
              <div className="rounded-lg bg-white border border-blue-200 p-3.5 space-y-1.5">
                <span className="text-xs font-bold text-blue-900 flex items-center gap-1.5">
                  <Pill className="w-3.5 h-3.5 text-blue-700" />
                  {language === "ta" ? "கே.பி. முறை பரிகார வழிகாட்டுதல்:" : "KP Remedial Strategy:"}
                </span>
                <p className="text-xs text-slate-700 leading-relaxed">
                  {language === "ta"
                    ? "கே.பி. ஜோதிட விதிகளின்படி, 6-ம் உப-அதிபதி 6, 8, 12-ம் பாவங்களை தொடர்பு கொண்டால், 1, 5, 11-ம் (குணப்படுத்தும்) பாவ அதிபதிகளை பலப்படுத்துவதும், 6/8/12-ம் அதிபதிகளின் காரக தானங்களை மேற்கொள்வதும் விரைவான நிவாரணம் அளிக்கும்."
                    : "In Krishnamurti Paddhati, when the 6th CSL signifies houses 6, 8, or 12, strengthening planets signifying recovery houses (1, 5, and 11) while performing charity for 6th/8th significator planets neutralizes medical vulnerability."}
                </p>
              </div>
            </div>
          )}

          {/* Triggered KP Rules */}
          {matchedKpRules.map((rule: MedicalRule) => {
            const ruleName = language === "ta" && rule.name_tamil ? rule.name_tamil : rule.name;
            const ruleDesc =
              language === "ta" && rule.interpretation_tamil
                ? rule.interpretation_tamil
                : rule.traditional_interpretation;
            return (
              <div key={rule.id} className="rounded-xl border border-slate-200 bg-white p-4 space-y-2 shadow-2xs">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-mono font-bold text-blue-900 bg-blue-50 px-2 py-0.5 rounded">
                    {rule.chapter_verse || "KP Reader IV"}
                  </span>
                  <span className="text-2xs font-semibold text-slate-500">{rule.anatomical_system}</span>
                </div>
                <h4 className="text-sm font-bold text-slate-900">{ruleName}</h4>
                <p className="text-xs text-slate-700 leading-relaxed">{ruleDesc}</p>
              </div>
            );
          })}
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* SECTION 4: DR. S. KRISHNA KUMAR COMPENDIUM MATCHED RULES & REMEDIES */}
      {/* ------------------------------------------------------------------- */}
      {(selectedFilter === "all" || selectedFilter === "krishna_kumar") && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-serif font-bold text-[#183047] flex items-center gap-2">
              <Stethoscope className="w-4 h-4 text-[#69235B]" />
              <span>
                {language === "ta"
                  ? "டாக்டர் எஸ். கிருஷ்ண குமார் நூல் தொகுதிப் பொருத்தம் (Horoscope or Stethoscope)"
                  : "Dr. S. Krishna Kumar Compendium Matching This Horoscope"}
              </span>
            </h3>
            <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-fuchsia-100 text-fuchsia-900">
              {matchedProgenyCurses.length + matchedKrishnaKumarYogas.length + (krishnaKumar?.native_moon_star ? 1 : 0)}{" "}
              {language === "ta" ? "விதிகள்" : "Matched"}
            </span>
          </div>

          {/* 4.1 Native's Moon Nakshatra Disease Tendency */}
          {krishnaKumar?.native_moon_star && (
            <div className="rounded-xl border border-fuchsia-200 bg-gradient-to-br from-fuchsia-50/50 to-white p-4 sm:p-5 shadow-2xs space-y-3">
              <div className="flex items-center justify-between gap-2 border-b border-fuchsia-100 pb-2">
                <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-fuchsia-100 text-fuchsia-900">
                  {language === "ta" ? "ஜென்ம நட்சத்திர மருத்துவ அமைப்பு" : "Natal Moon Nakshatra Vulnerability"}
                </span>
                <span className="text-xs font-bold text-fuchsia-800">
                  {language === "ta" ? krishnaKumar.native_moon_star.name_ta : krishnaKumar.native_moon_star.name}
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs text-slate-800">
                <div className="space-y-1">
                  <span className="text-2xs uppercase tracking-wider text-fuchsia-900 font-bold block">
                    {language === "ta" ? "ஆளும் உடல் உறுப்புகள்:" : "Governed Anatomical Organs:"}
                  </span>
                  <p className="font-semibold text-slate-900">
                    {language === "ta"
                      ? krishnaKumar.native_moon_star.body_part_ta
                      : krishnaKumar.native_moon_star.body_part_en}
                  </p>
                </div>

                <div className="space-y-1">
                  <span className="text-2xs uppercase tracking-wider text-rose-800 font-bold block">
                    {language === "ta" ? "பாரம்பரிய நோய் சாத்தியங்கள்:" : "Traditional Disease Tendencies:"}
                  </span>
                  <p className="text-rose-950 font-medium">
                    {language === "ta"
                      ? krishnaKumar.native_moon_star.disease_tendency_ta
                      : krishnaKumar.native_moon_star.disease_tendency_en}
                  </p>
                </div>
              </div>

              {/* Devata Prayer & Remedy */}
              <div className="rounded-lg bg-fuchsia-50 border border-fuchsia-200/80 p-3 text-xs space-y-1">
                <span className="font-bold text-fuchsia-950 flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-fuchsia-700" />
                  {language === "ta" ? "நட்சத்திர அதிதேவதை & பாதுகாப்பு:" : "Nakshatra Presiding Deity & Protection:"}
                </span>
                <p className="text-fuchsia-900">
                  {language === "ta"
                    ? `அதிதேவதை: ${krishnaKumar.native_moon_star.devata}. ஜென்ம நட்சத்திர நாளில் அதிதேவதை வழிபாடு, நெய் தீபம் ஏற்றுதல் மற்றும் எளிய தானம் செய்வது உடல் ஆரோக்கியத்தை பாதுகாக்கும்.`
                    : `Presiding Deity: ${krishnaKumar.native_moon_star.devata}. Worshipping the nakshatra devata with ghee deepam and performing charity on natal star days maintains constitutional balance.`}
                </p>
              </div>
            </div>
          )}

          {/* 4.2 Active Progeny Curses (Shapa) & Exact Vedic Remedies */}
          {matchedProgenyCurses.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                <h4 className="text-sm font-bold text-slate-900">
                  {language === "ta"
                    ? "ஜாதகத்தில் உறுதி செய்யப்பட்ட சாபங்கள் & முழுமையான வேத பரிகாரங்கள்"
                    : "Active Progeny Curses (Shapas) & Prescribed Vedic Remedies"}
                </h4>
              </div>

              <div className="grid grid-cols-1 gap-3.5">
                {matchedProgenyCurses.map((curse: ProgenyShapaDetail) => (
                  <div
                    key={curse.id}
                    className="rounded-xl border border-amber-300 bg-gradient-to-br from-amber-50/70 via-white to-rose-50/40 p-4 sm:p-5 shadow-2xs space-y-3"
                  >
                    <div className="flex items-center justify-between gap-2 border-b border-amber-200 pb-2">
                      <span className="text-xs font-bold text-amber-950 font-serif">{curse.shapa_name}</span>
                      <span className="text-2xs font-bold px-2 py-0.5 rounded bg-rose-100 text-rose-800">
                        {language === "ta" ? "ஜாதகத்தில் அமைந்தது" : "Active in Chart"}
                      </span>
                    </div>

                    {curse.chart_observation && (
                      <div className="text-2xs bg-amber-100/50 rounded-lg p-2.5 text-amber-900 font-mono">
                        <span className="font-bold block mb-1">
                          {language === "ta" ? "காரண கிரக அமைப்புகள்:" : "Triggered Combinations in Chart:"}
                        </span>
                        <span>{curse.chart_observation}</span>
                      </div>
                    )}

                    {/* Complete Prescribed Vedic Remedy */}
                    <div className="rounded-lg bg-emerald-50/90 border border-emerald-300 p-3.5 space-y-1.5">
                      <span className="text-xs font-bold text-emerald-950 flex items-center gap-1.5">
                        <Sparkles className="w-3.5 h-3.5 text-emerald-700" />
                        {language === "ta" ? "சாஸ்திர வேத பரிகாரம் (Authentic Vedic Remedy):" : "Authentic Prescribed Vedic Remedy:"}
                      </span>
                      <p className="text-xs text-emerald-900 leading-relaxed font-medium">
                        {language === "ta" ? curse.remedy_ta : curse.remedy_en}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 4.3 Matched Manasika, Buddhi & Organ-Specific Yogas */}
          {matchedKrishnaKumarYogas.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-sm font-bold text-slate-900">
                {language === "ta"
                  ? "மனநலம் மற்றும் உறுப்பு சார்ந்த மருத்துவ அமைப்புகள்"
                  : "Psychological, Intellectual & Organ-Specific Yogas"}
              </h4>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {matchedKrishnaKumarYogas.map((yoga: MedicalRule) => {
                  const yName = language === "ta" && yoga.name_tamil ? yoga.name_tamil : yoga.name;
                  const yDesc =
                    language === "ta" && yoga.interpretation_tamil
                      ? yoga.interpretation_tamil
                      : yoga.traditional_interpretation;
                  const remedy = resolveRemedyForRule(yoga);

                  return (
                    <div key={yoga.id} className="rounded-xl border border-slate-200 bg-white p-4 space-y-2 shadow-2xs">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-xs font-mono font-bold text-fuchsia-900 bg-fuchsia-50 px-2 py-0.5 rounded">
                          {yoga.chapter_verse || "Horoscope or Stethoscope"}
                        </span>
                        <span className="text-2xs font-semibold text-slate-500">{yoga.anatomical_system}</span>
                      </div>
                      <h5 className="text-xs font-bold text-slate-900">{yName}</h5>
                      <p className="text-xs text-slate-700 leading-relaxed">{yDesc}</p>
                      <div className="rounded bg-amber-50 p-2 text-2xs text-amber-950 border border-amber-200/60">
                        <span className="font-bold">{language === "ta" ? "பரிகாரம்: " : "Remedy: "}</span>
                        <span>{language === "ta" ? remedy.ta : remedy.en}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* SECTION 5: DR. S. S. CHATTERJEE COMPENDIUM MATCHED RULES & REMEDIES */}
      {/* ------------------------------------------------------------------- */}
      {(selectedFilter === "all" || selectedFilter === "chatterjee") && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-serif font-bold text-[#183047] flex items-center gap-2">
              <Award className="w-4 h-4 text-[#69235B]" />
              <span>
                {language === "ta"
                  ? "டாக்டர் எஸ்.எஸ். சாட்டர்ஜி அட்வான்ஸ் மருத்துவ ஜோதிடப் பொருத்தம்"
                  : "Dr. S. S. Chatterjee Advance Medical Astrology Matching This Horoscope"}
              </span>
            </h3>
            <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-purple-100 text-purple-900">
              {matchedChatterjeeGoldenRules.length + (isDeathPointTriggered ? 1 : 0) + (isDiabetesIndicated ? 1 : 0)}{" "}
              {language === "ta" ? "அமைப்புகள்" : "Items"}
            </span>
          </div>

          {/* 5.1 Death Point Trigger Alert & Remedies */}
          {isDeathPointTriggered && chatterjee?.death_point && (
            <div className="rounded-xl border border-rose-300 bg-rose-50/90 p-4 sm:p-5 shadow-2xs space-y-3">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-rose-700 mt-0.5 shrink-0" />
                <div className="space-y-1.5 flex-1 text-xs text-rose-950">
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <span className="font-bold text-rose-900 text-sm">
                      {language === "ta"
                        ? "டாக்டர் சாட்டர்ஜியின் ஆயுள் புள்ளி (Death Point) மீது சனியின் பார்வை"
                        : "Dr. Chatterjee's Death Point Receiving Saturn's Direct Drishti"}
                    </span>
                    <span className="font-mono text-2xs bg-rose-200/80 px-2 py-0.5 rounded text-rose-950">
                      {chatterjee.death_point.degree_in_sign.toFixed(2)}° {chatterjee.death_point.sign_name_en}
                    </span>
                  </div>

                  <p className="leading-relaxed">
                    {language === "ta"
                      ? "சாட்டர்ஜி கண்டறிந்த கணித முறையின்படி, லக்னம் + சூரியன் + சந்திரன் + குரு ஆகிய நால்வரின் பாகை கூட்டுத்தொகையாக அமைந்த ஆயுள் புள்ளி மீது சனியின் நேரடிப் பார்வை படுவதால், உடல் சோர்வு மற்றும் மூட்டு/நரம்பு அழுத்தங்கள் ஏற்படலாம்."
                      : "Dr. S. S. Chatterjee's empirical discovery: When transit or natal Saturn casts aspect on the sensitive mathematical Death Point (Asc + Sun + Moon + Jupiter), acute physical fatigue and muscular-joint vulnerabilities may be experienced."}
                  </p>

                  <div className="rounded-lg bg-white border border-rose-200 p-3 space-y-1 mt-2">
                    <span className="font-bold text-rose-900 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-rose-700" />
                      {language === "ta" ? "சாஸ்திர பரிகாரங்கள்:" : "Prescribed Classical Remedies:"}
                    </span>
                    <p className="text-slate-800">
                      {language === "ta"
                        ? "ஸ்ரீ மகா மிருத்யுஞ்சய ஜபம் தினசரி 108 முறை, ருத்ராபிஷேகம், திருக்கடையூர் அல்லது நள்ளாறு ஸ்தல வழிபாடு, மற்றும் நல்லெண்ணெய் தீபம் ஏற்றுதல் சிறந்த பலன் தரும்."
                        : "Chant Sri Maha Mrityunjaya Mantra 108 times daily; perform Rudrabhishekam on Pradosham; visit Lord Shiva or Shani kshetras (e.g. Thirukadaiyur); light sesame oil lamps."}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 5.2 Diabetes Mellitus (Madhumeha) Assessment & Remedies */}
          {isDiabetesIndicated && chatterjee?.diabetes_assessment && (
            <div className="rounded-xl border border-amber-300 bg-amber-50/70 p-4 sm:p-5 shadow-2xs space-y-3">
              <div className="flex items-center justify-between border-b border-amber-200 pb-2">
                <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-amber-200 text-amber-950">
                  {language === "ta" ? "சர்க்கரை நோய் மருத்துவ ஜோதிட ஆய்வு" : "Diabetes Mellitus (Madhumeha) Evaluation"}
                </span>
                <span className="text-xs font-bold text-amber-900">
                  {language === "ta" ? `அபாய நிலை: ${chatterjee.diabetes_assessment.risk_level}` : `Risk Level: ${chatterjee.diabetes_assessment.risk_level}`}
                </span>
              </div>

              <div className="space-y-1 text-xs text-amber-950">
                <p className="font-semibold">
                  {language === "ta"
                    ? `சுக்கிரன் நிலை: ${chatterjee.diabetes_assessment.venus_status} | குரு நிலை: ${chatterjee.diabetes_assessment.jupiter_status}`
                    : `Venus Status: ${chatterjee.diabetes_assessment.venus_status} | Jupiter Status: ${chatterjee.diabetes_assessment.jupiter_status}`}
                </p>
                <p className="leading-relaxed">
                  {language === "ta"
                    ? "டாக்டர் சாட்டர்ஜியின் விரிவான மருத்துவ ஜோதிட ஆய்வின்படி, சுக்கிரன்/குரு துஸ்தானங்களில் அமைவது அல்லது 6-ஆம் அதிபதியின் சேர்க்கை கணைய இன்சுலின் சுரப்பில் ஏற்றத்தாழ்வுகளை ஏற்படுத்தலாம்."
                    : "According to Dr. S. S. Chatterjee, affliction to Venus, Jupiter, or the 6th sign (Virgo) predisposes the native to pancreatic glycemic sensitivity."}
                </p>
              </div>

              {/* Natural Dietetic Remedies */}
              <div className="rounded-lg bg-white border border-amber-200 p-3.5 space-y-2">
                <span className="text-xs font-bold text-amber-900 flex items-center gap-1.5">
                  <Pill className="w-3.5 h-3.5 text-amber-700" />
                  {language === "ta" ? "டாக்டர் சாட்டர்ஜியின் இயற்கை உணவுப் பரிகாரங்கள்:" : "Dr. Chatterjee's Natural Dietetic Protocol:"}
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-2xs text-slate-700">
                  <div className="flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                    <span>{language === "ta" ? "காலை உணவாக முளைகட்டிய கடலை மற்றும் மோர்" : "Sprouted Bengal gram (chana) with buttermilk"}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                    <span>{language === "ta" ? "வெந்தய நீர் & பாகற்காய் சாறு" : "Fenugreek (methi) soaked water & bitter gourd"}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                    <span>{language === "ta" ? "சூரிய அஸ்தமனத்திற்கு முன் இரவு உணவு" : "Dinner before sunset (early light meal)"}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                    <span>{language === "ta" ? "உணவுக்குப் பின் மிதமான நடைபயிற்சி" : "Post-meal gentle walking (15-20 mins)"}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 5.3 Golden Rules Triggered */}
          {matchedChatterjeeGoldenRules.length > 0 && (
            <div className="grid grid-cols-1 gap-3">
              {matchedChatterjeeGoldenRules.map((rule: MedicalRule) => {
                const ruleName = language === "ta" && rule.name_tamil ? rule.name_tamil : rule.name;
                const ruleDesc =
                  language === "ta" && rule.interpretation_tamil
                    ? rule.interpretation_tamil
                    : rule.traditional_interpretation;
                const remedy = resolveRemedyForRule(rule);

                return (
                  <div key={rule.id} className="rounded-xl border border-purple-200 bg-white p-4 space-y-2 shadow-2xs">
                    <div className="flex items-center justify-between gap-2 border-b border-purple-100 pb-2">
                      <span className="text-xs font-mono font-bold text-purple-900 bg-purple-50 px-2 py-0.5 rounded">
                        {rule.chapter_verse || "Advance Medical Astrology"}
                      </span>
                      <span className="text-2xs font-semibold px-2 py-0.5 rounded bg-indigo-50 text-indigo-700">
                        {rule.anatomical_system}
                      </span>
                    </div>

                    <h4 className="text-sm font-bold text-slate-900">{ruleName}</h4>
                    <p className="text-xs text-slate-700 leading-relaxed">{ruleDesc}</p>

                    <div className="rounded-lg bg-amber-50/80 border border-amber-200 p-3 text-2xs space-y-1">
                      <span className="font-bold text-amber-950 flex items-center gap-1">
                        <Pill className="w-3 h-3 text-amber-700" />
                        {language === "ta" ? "பரிகார வழிகாட்டுதல்:" : "Prescribed Remedy:"}
                      </span>
                      <p className="text-amber-900 font-medium">
                        {language === "ta" ? remedy.ta : remedy.en}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* SECTION 5.5: MAX HEINDEL (ROSICRUCIAN ASTRO-DIAGNOSIS) RULES        */}
      {/* ------------------------------------------------------------------- */}
      {(selectedFilter === "all" || selectedFilter === "heindel") && matchedHeindelRules.length > 0 && (
        <div className="space-y-4 pt-4 border-t border-slate-200">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-serif font-bold text-[#1B365D] flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-[#1B365D]" />
              <span>
                {language === "ta"
                  ? "மேக்ஸ் ஹெய்ண்டல்: ரோசிகுரூசியன் ஆஸ்ட்ரோ-டயக்னாசிஸ் உறுதி செய்யப்பட்ட விதிகள்"
                  : "Max Heindel: Rosicrucian Astro-Diagnosis Active Rules in This Chart"}
              </span>
            </h3>
            <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-blue-100 text-blue-900">
              {matchedHeindelRules.length} {language === "ta" ? "விதிகள்" : "Rules"}
            </span>
          </div>

          <p className="text-xs text-slate-600">
            {language === "ta"
              ? "மேக்ஸ் ஹெய்ண்டல் & அகஸ்டா பாஸ் ஹெய்ண்டல் அருளிய 'ஆஸ்ட்ரோ-டயக்னாசிஸ்: ஹீலிங் கையேடு' நூலின்படி, ஜாதகத்தில் கிரக சேர்க்கைகள், பார்வைகள் மற்றும் கேந்திர/திரிகோண பலவீனங்களால் தூண்டப்பட்ட மருத்துவ விதிகள்:"
              : "Diagnostic and physiological predispositions triggered according to Max Heindel & Augusta Foss Heindel's 'Astro-Diagnosis: A Guide to Healing' based on planetary afflictions, aspects, and cross reflexes:"}
          </p>

          <div className="grid grid-cols-1 gap-3">
            {matchedHeindelRules.map((rule: MedicalRule) => {
              const ruleName = language === "ta" && rule.name_tamil ? rule.name_tamil : rule.name;
              const ruleDesc =
                language === "ta" && rule.interpretation_tamil
                  ? rule.interpretation_tamil
                  : rule.traditional_interpretation;
              const remedy = resolveRemedyForRule(rule);

              return (
                <div key={rule.id} className="rounded-xl border border-blue-200 bg-white p-4 space-y-2 shadow-2xs">
                  <div className="flex items-center justify-between gap-2 border-b border-blue-100 pb-2">
                    <span className="text-xs font-mono font-bold text-blue-900 bg-blue-50 px-2 py-0.5 rounded">
                      {rule.chapter_verse || "Astro-Diagnosis"}
                    </span>
                    <span className="text-2xs font-semibold px-2 py-0.5 rounded bg-sky-50 text-sky-800">
                      {rule.anatomical_system}
                    </span>
                  </div>

                  <h4 className="text-sm font-bold text-slate-900">{ruleName}</h4>
                  <p className="text-xs text-slate-700 leading-relaxed">{ruleDesc}</p>

                  <div className="rounded-lg bg-amber-50/80 border border-amber-200 p-3 text-2xs space-y-1">
                    <span className="font-bold text-amber-950 flex items-center gap-1">
                      <Pill className="w-3 h-3 text-amber-700" />
                      {language === "ta" ? "பரிகார வழிகாட்டுதல் & ரோசிகுரூசியன் அறிவியல்:" : "Prescribed Rosicrucian & Natural Remedy:"}
                    </span>
                    <p className="text-amber-900 font-medium">
                      {language === "ta" ? remedy.ta : remedy.en}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* SECTION 5B: JANE RIDDER-PATRICK MATCHED RULES                       */}
      {/* ------------------------------------------------------------------- */}
      {(selectedFilter === "all" || selectedFilter === "ridder_patrick") && matchedRidderPatrickRules.length > 0 && (
        <div className="space-y-4 pt-4 border-t border-slate-200">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-serif font-bold text-teal-900 flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-teal-700" />
              <span>
                {language === "ta"
                  ? "ஜேன் ரிடர்-பேட்ரிக்: மருத்துவ ஜோதிட உறுதி செய்யப்பட்ட விதிகள்"
                  : "Jane Ridder-Patrick: Classical & Clinical Astrological Active Rules"}
              </span>
            </h3>
            <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-teal-100 text-teal-900">
              {matchedRidderPatrickRules.length} {language === "ta" ? "விதிகள் பொருந்தியுள்ளன" : "Active Rules"}
            </span>
          </div>

          <div className="grid grid-cols-1 gap-3">
            {matchedRidderPatrickRules.map((rule: MedicalRule) => {
              const ruleName = language === "ta" && rule.name_tamil ? rule.name_tamil : rule.name;
              const ruleDesc =
                language === "ta" && rule.interpretation_tamil
                  ? rule.interpretation_tamil
                  : rule.traditional_interpretation;
              const remedy = resolveRemedyForRule(rule);

              return (
                <div key={rule.id} className="rounded-xl border border-teal-200 bg-white p-4 space-y-2 shadow-2xs">
                  <div className="flex items-center justify-between gap-2 border-b border-teal-100 pb-2">
                    <span className="text-sm font-bold text-teal-950">{ruleName}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-teal-50 text-teal-700 border border-teal-200 font-semibold">
                      {rule.category}
                    </span>
                  </div>
                  <p className="text-xs text-slate-700 leading-relaxed">{ruleDesc}</p>
                  {rule.triggered_positions && rule.triggered_positions.length > 0 && (
                    <div className="text-[11px] text-teal-800 bg-teal-50/60 p-2 rounded-lg">
                      <strong>{language === "ta" ? "பொருந்திய அமைப்புகள்: " : "Matched Placements: "}</strong>
                      {rule.triggered_positions.join(", ")}
                    </div>
                  )}
                  <div className="text-[11px] text-slate-600 bg-slate-50 p-2 rounded-lg border border-slate-200/80">
                    <strong className="text-slate-800">{language === "ta" ? "பரிகாரம் & சமநிலை: " : "Therapeutic Remedy: "}</strong>
                    {language === "ta" ? remedy.ta : remedy.en}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* SECTION 5C: HEINRICH DÄATH MATCHED RULES                            */}
      {/* ------------------------------------------------------------------- */}
      {(selectedFilter === "all" || selectedFilter === "daath") && matchedDaathRules.length > 0 && (
        <div className="space-y-4 pt-4 border-t border-slate-200">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-serif font-bold text-indigo-950 flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-indigo-700" />
              <span>
                {language === "ta"
                  ? "ஹென்ரிச் டாத்: பண்டைய ஜாத்ரோமேத்தமேட்டிக்ஸ் உறுதி செய்யப்பட்ட விதிகள்"
                  : "Heinrich Däath: Classical Jatromathematical Active Rules in Chart"}
              </span>
            </h3>
            <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-indigo-100 text-indigo-900">
              {matchedDaathRules.length} {language === "ta" ? "விதிகள் பொருந்தியுள்ளன" : "Active Rules"}
            </span>
          </div>

          <div className="grid grid-cols-1 gap-3">
            {matchedDaathRules.map((rule: MedicalRule) => {
              const ruleName = language === "ta" && rule.name_tamil ? rule.name_tamil : rule.name;
              const ruleDesc =
                language === "ta" && rule.interpretation_tamil
                  ? rule.interpretation_tamil
                  : rule.traditional_interpretation;
              const remedy = resolveRemedyForRule(rule);

              return (
                <div key={rule.id} className="rounded-xl border border-indigo-200 bg-white p-4 space-y-2 shadow-2xs">
                  <div className="flex items-center justify-between gap-2 border-b border-indigo-100 pb-2">
                    <span className="text-sm font-bold text-indigo-950">{ruleName}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200 font-semibold">
                      {rule.category}
                    </span>
                  </div>
                  <p className="text-xs text-slate-700 leading-relaxed">{ruleDesc}</p>
                  {rule.triggered_positions && rule.triggered_positions.length > 0 && (
                    <div className="text-[11px] text-indigo-900 bg-indigo-50/60 p-2 rounded-lg">
                      <strong>{language === "ta" ? "பொருந்திய அமைப்புகள்: " : "Matched Placements: "}</strong>
                      {rule.triggered_positions.join(", ")}
                    </div>
                  )}
                  <div className="text-[11px] text-slate-600 bg-slate-50 p-2 rounded-lg border border-slate-200/80">
                    <strong className="text-slate-800">{language === "ta" ? "எதிர் சமநிலை & பரிகாரம்: " : "Antipathic Remedy: "}</strong>
                    {language === "ta" ? (rule.remedy_ta || remedy.ta) : (rule.remedy_en || remedy.en)}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* SECTION 6: CONSOLIDATED PLANETARY REMEDIES TABLE                    */}
      {/* ------------------------------------------------------------------- */}
      {(selectedFilter === "all" || selectedFilter === "remedies_only") && uniqueAfflictedPlanets.length > 0 && (
        <div className="space-y-4 pt-4 border-t border-slate-200">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-serif font-bold text-[#183047] flex items-center gap-2">
              <Pill className="w-4 h-4 text-emerald-700" />
              <span>
                {language === "ta"
                  ? "இந்த ஜாதகத்தில் பாதிக்கப்பட்ட கிரகங்களுக்கான விரிவான பரிகார வழிகாட்டி"
                  : "Consolidated Remedies Guide for All Afflicted Grahas in This Horoscope"}
              </span>
            </h3>
            <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-900">
              {uniqueAfflictedPlanets.length} {language === "ta" ? "கிரகங்கள்" : "Grahas"}
            </span>
          </div>

          <p className="text-xs text-slate-600">
            {language === "ta"
              ? "மேலே ஆய்வு செய்யப்பட்ட விதிகளின்படி இந்த குறிப்பிட்ட ஜாதகத்தில் பலவீனமடைந்த அல்லது தோஷம் பெற்ற கிரகங்கள் கண்டறியப்பட்டு, அவற்றுக்கான மூலிகை, உணவு, நீர் சிகிச்சை, தானம் மற்றும் வழிபாட்டுப் பரிகாரங்கள் கீழே விரிவாகத் தரப்பட்டுள்ளன."
              : "Synthesizing all afflicted planetary significators identified across classical rules, cuspal sub-lords, and treatises with targeted Ayurvedic herbs, water therapy, chromotherapy, charity, and mantras."}
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {uniqueAfflictedPlanets.map((pName: string) => {
              const rem = PLANETARY_REMEDY_MATRIX[pName];
              if (!rem) return null;

              return (
                <div
                  key={pName}
                  className="rounded-xl border border-slate-200 bg-gradient-to-br from-white via-slate-50/50 to-amber-50/20 p-4 sm:p-5 shadow-2xs space-y-3"
                >
                  <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                    <span className="text-sm font-bold text-slate-900 flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-amber-600" />
                      {pName}
                    </span>
                    <span className="text-2xs font-semibold px-2 py-0.5 rounded bg-rose-100 text-rose-800">
                      {language === "ta" ? "பரிகாரம் தேவை" : "Remedy Recommended"}
                    </span>
                  </div>

                  <div className="space-y-2 text-xs">
                    <div>
                      <span className="font-bold text-slate-800 block text-2xs uppercase tracking-wider">
                        {language === "ta" ? "மந்திரம் & ஜபம்:" : "Mantra & Japa:"}
                      </span>
                      <p className="text-slate-700 mt-0.5">{language === "ta" ? rem.mantra_ta : rem.mantra_en}</p>
                    </div>

                    <div>
                      <span className="font-bold text-slate-800 block text-2xs uppercase tracking-wider">
                        {language === "ta" ? "ஆயுர்வேத உணவு & மூலிகைகள்:" : "Ayurvedic Food & Herbs:"}
                      </span>
                      <p className="text-slate-700 mt-0.5">{language === "ta" ? rem.diet_herbs_ta : rem.diet_herbs_en}</p>
                    </div>

                    <div>
                      <span className="font-bold text-slate-800 block text-2xs uppercase tracking-wider">
                        {language === "ta" ? "வாழ்வியல் & நீர் சிகிச்சை:" : "Lifestyle & Water Therapy:"}
                      </span>
                      <p className="text-slate-700 mt-0.5">{language === "ta" ? rem.lifestyle_therapy_ta : rem.lifestyle_therapy_en}</p>
                    </div>

                    <div>
                      <span className="font-bold text-slate-800 block text-2xs uppercase tracking-wider">
                        {language === "ta" ? "தானம் & திருப்பணி:" : "Charity & Dana:"}
                      </span>
                      <p className="text-slate-700 mt-0.5">{language === "ta" ? rem.charity_ta : rem.charity_en}</p>
                    </div>

                    <div className="pt-1 border-t border-slate-100">
                      <span className="font-bold text-slate-800 block text-2xs uppercase tracking-wider">
                        {language === "ta" ? "வழிபாட்டு ஸ்தலங்கள்:" : "Sacred Temples:"}
                      </span>
                      <p className="text-slate-700 mt-0.5">{language === "ta" ? rem.temples_ta : rem.temples_en}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* SECTION 7: VEGA DHARANA - 13 NATURAL URGES HAZARDS (AYURVEDIC)      */}
      {/* ------------------------------------------------------------------- */}
      {chatterjee?.natural_remedies?.vega_dharana_urges && (
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-2xs space-y-3">
          <div className="flex items-center gap-2">
            <HeartPulse className="w-5 h-5 text-rose-600" />
            <div>
              <h4 className="text-sm font-bold text-slate-900">
                {language === "ta"
                  ? "13 இயற்கை வேகங்களை அடக்குவதால் ஏற்படும் உபாதைகள் (வேக தாரணம் - ஆயுர்வேத விதிமுறை)"
                  : "Suppression of 13 Natural Bodily Urges (Classical Vega Dharana Preventive Guidelines)"}
              </h4>
              <p className="text-2xs text-slate-500">
                {language === "ta"
                  ? "மருத்துவ ஜோதிடத்தில் நோய்களை தடுக்கும் முதன்மை விதியாக இயற்கை உபாதைகளை அடக்காமல் இருத்தல் குறிப்பிடப்படுகிறது."
                  : "Charaka Samhita & Advance Medical Astrology emphasize non-suppression of biological reflexes as primary defense against pathology."}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5 pt-2">
            {chatterjee.natural_remedies.vega_dharana_urges.slice(0, 6).map((urge, uIdx: number) => (
              <div key={uIdx} className="rounded-lg bg-slate-50 border border-slate-200/80 p-3 space-y-1 text-xs">
                <span className="font-bold text-slate-900 block">
                  {language === "ta" ? urge.urge_ta : urge.urge_en}
                </span>
                <p className="text-2xs text-slate-600 leading-relaxed">
                  {language === "ta" ? urge.suppression_hazard_ta : urge.suppression_hazard_en}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
