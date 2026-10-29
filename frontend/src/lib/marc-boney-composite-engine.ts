/**
 * Marc Boney & K.N. Rao Composite Astrological Engine
 * 
 * Implements classical principles from:
 * 1. "Predicting Major Life Events" (2020) by Marc Boney, M.A. (dedicated to K.N. Rao)
 * 2. K.N. Rao's Double Transit Principle (Jupiter & Saturn concurrent sanction)
 *    - Includes K.N. Rao's Retrograde Rule: Retrograde transiting planets also aspect from the preceding sign!
 * 3. Jaimini 7 Chara Karaka System (AK, AmK, BK, MK, PK, GK, DK) and Karakamsha
 * 4. Beeja Sphuta (Male progeny potency) & Kshetra Sphuta (Female progeny receptivity)
 * 5. Dasa Lagna methodology (evaluating houses from Mahadasha lord's natal position)
 * 6. Synthesis across 8 Major Life Domains:
 *    - Educational Achievement (D-24, 5th/4th/9th, Budhaditya, Saraswati)
 *    - Career Rise & Status (D-10, 10th/1st/11th, Amatya Karaka [AmK])
 *    - Financial Prosperity (D-11, 2nd/11th, Jaimini Moon-Venus Dhana Yoga)
 *    - Marriage & Relationship Timing (D-9, 7th/1st, Dara Karaka [DK], Upapada Lagna [UL])
 *    - Childbirth & Progeny (D-7, 5th/9th, Putra Karaka [PK], Beeja/Kshetra Sphuta)
 *    - Property, Land & Conveyance (D-4, 4th, Matri Karaka [MK], Pada 4 [A4])
 *    - Foreign Settlement & Relocation (12th/9th/4th affliction, Rahu activation)
 *    - Spiritual Initiation & Guru (9th/5th/8th/12th, Ketu, Jupiter, Virinchi Yoga)
 */

import { HoroscopeResponse, DasaResponse, PlanetInfo, HouseInfo, LiveTransitsResponse } from "./types";
import { normalizePlanetName } from "./benefit-bhavas";
import { getLordName, getGrahaName, getRasiName, LanguageCode } from "./translations";

export const ZODIAC_NAMES_EN = [
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

export const ZODIAC_NAMES_TA = [
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

export const SIGN_LORDS_MAP: Record<number, string> = {
  1: "Mars",
  2: "Venus",
  3: "Mercury",
  4: "Moon",
  5: "Sun",
  6: "Mercury",
  7: "Venus",
  8: "Mars",
  9: "Jupiter",
  10: "Saturn",
  11: "Saturn",
  12: "Jupiter",
};

export interface CharaKarakaItem {
  role: "AK" | "AmK" | "BK" | "MK" | "PK" | "GK" | "DK";
  roleNameEn: string;
  roleNameTa: string;
  planet: string;
  degreeInSign: number;
  formattedDegree: string;
  signIndex: number;
  signNameEn: string;
  signNameTa: string;
  house: number;
  significationEn: string;
  significationTa: string;
}

export interface BeejaKshetraAnalysis {
  beejaSphuta: {
    longitude: number;
    signIndex: number;
    signNameEn: string;
    signNameTa: string;
    degreeInSign: number;
    formattedDegree: string;
    navamshaSignIndex: number;
    navamshaSignNameEn: string;
    navamshaSignNameTa: string;
    isSignOdd: boolean;
    isNavamshaOdd: boolean;
    fruitfulness: "fruitful" | "semi_fruitful" | "barren";
    potencyVerdictEn: string;
    potencyVerdictTa: string;
    vitalityScore: number; // 0-100
  };
  kshetraSphuta: {
    longitude: number;
    signIndex: number;
    signNameEn: string;
    signNameTa: string;
    degreeInSign: number;
    formattedDegree: string;
    navamshaSignIndex: number;
    navamshaSignNameEn: string;
    navamshaSignNameTa: string;
    isSignEven: boolean;
    isNavamshaEven: boolean;
    fruitfulness: "fruitful" | "semi_fruitful" | "barren";
    receptivityVerdictEn: string;
    receptivityVerdictTa: string;
    vitalityScore: number; // 0-100
  };
}

export interface DoubleTransitAspectDetail {
  planet: "Saturn" | "Jupiter";
  currentSignIndex: number;
  currentSignNameEn: string;
  currentSignNameTa: string;
  isRetrograde: boolean;
  aspectsCastingOnSigns: {
    signIndex: number;
    signNameEn: string;
    aspectType: string;
    isFromRetrogradePrecedingSign: boolean;
  }[];
}

export interface DoubleTransitStatus {
  isFulfilled: boolean;
  saturnInfluences: boolean;
  saturnAspectSource?: string;
  saturnAspectSourceTa?: string;
  jupiterInfluences: boolean;
  jupiterAspectSource?: string;
  jupiterAspectSourceTa?: string;
  summaryEn: string;
  summaryTa: string;
}

export type MilestoneDomainKey =
  | "education"
  | "career"
  | "wealth"
  | "marriage"
  | "childbirth"
  | "property"
  | "foreign"
  | "spirituality";

export interface LifeMilestonePrediction {
  id: MilestoneDomainKey;
  domainNameEn: string;
  domainNameTa: string;
  sanskritTermEn: string;
  sanskritTermTa: string;
  readinessScore: number; // 0 - 100%
  status: "high_imminent" | "favorable" | "moderate" | "preparatory";
  statusBadgeEn: string;
  statusBadgeTa: string;
  keyHouses: number[];
  primaryHouseLords: string[];
  karakasInvolved: {
    parashari: string;
    jaimini: string;
    charaRole: string;
  };
  dasaBhuktiAlignment: {
    isAligned: boolean;
    dasaLord: string;
    bukthiLord: string;
    andharaLord?: string;
    descriptionEn: string;
    descriptionTa: string;
  };
  doubleTransit: DoubleTransitStatus;
  dasaLagnaInsight: {
    dasaLagnaSignIndex: number;
    dasaLagnaSignEn: string;
    dasaLagnaSignTa: string;
    houseFromDasaLagna: number;
    insightEn: string;
    insightTa: string;
  };
  divisionalCheck: {
    vargaKey: string;
    vargaNameEn: string;
    vargaNameTa: string;
    focalPointEn: string;
    focalPointTa: string;
  };
  classicalRulesCitedEn: string[];
  classicalRulesCitedTa: string[];
  predictiveGuidanceEn: string;
  predictiveGuidanceTa: string;
}

export interface SpecialCompositeYogas {
  virinchiYoga: {
    present: boolean;
    strength: "powerful" | "moderate" | "none";
    descriptionEn: string;
    descriptionTa: string;
  };
  jaiminiMoonVenusDhanaYoga: {
    present: boolean;
    strength: "exceptional" | "moderate" | "none";
    descriptionEn: string;
    descriptionTa: string;
  };
  saraswatiYoga: {
    present: boolean;
    strength: "powerful" | "moderate" | "none";
    descriptionEn: string;
    descriptionTa: string;
  };
  upapadaLagna: {
    signIndex: number;
    signNameEn: string;
    signNameTa: string;
    houseNumber: number;
  };
  arudhaPada4: {
    signIndex: number;
    signNameEn: string;
    signNameTa: string;
    houseNumber: number;
  };
  arudhaPada11: {
    signIndex: number;
    signNameEn: string;
    signNameTa: string;
    houseNumber: number;
  };
}

export interface MarcBoneyAnalysisResult {
  calculatedAt: string;
  activeDasaLord: string;
  activeBukthiLord: string;
  activeAndharaLord?: string;
  dasaLagnaSignIndex: number;
  dasaLagnaSignNameEn: string;
  dasaLagnaSignNameTa: string;
  karakamshaSignIndex: number;
  karakamshaSignNameEn: string;
  karakamshaSignNameTa: string;
  charaKarakas: CharaKarakaItem[];
  beejaKshetra: BeejaKshetraAnalysis;
  specialYogas: SpecialCompositeYogas;
  saturnTransitDetail: DoubleTransitAspectDetail;
  jupiterTransitDetail: DoubleTransitAspectDetail;
  milestones: LifeMilestonePrediction[];
  marcBoneyCoreQuoteEn: string;
  marcBoneyCoreQuoteTa: string;
}

/**
 * Helper to calculate Navamsha sign (1-12) from continuous 0-360 longitude
 */
export function calculateNavamshaSign(longitude: number): number {
  const normLong = ((longitude % 360) + 360) % 360;
  const signIndex = Math.floor(normLong / 30) + 1; // 1-12
  const degInSign = normLong % 30;
  const pada = Math.floor(degInSign / (30 / 9)); // 0 to 8

  // Movable signs: Aries (1), Cancer (4), Libra (7), Capricorn (10) -> start from sign itself
  // Fixed signs: Taurus (2), Leo (5), Scorpio (8), Aquarius (11) -> start from 9th sign
  // Dual signs: Gemini (3), Virgo (6), Sagittarius (9), Pisces (12) -> start from 5th sign
  let startSign = signIndex;
  if ([1, 4, 7, 10].includes(signIndex)) {
    startSign = signIndex;
  } else if ([2, 5, 8, 11].includes(signIndex)) {
    startSign = ((signIndex - 1 + 8) % 12) + 1;
  } else {
    startSign = ((signIndex - 1 + 4) % 12) + 1;
  }

  return ((startSign - 1 + pada) % 12) + 1;
}

/**
 * Format degree minutes
 */
function formatDegMin(deg: number): string {
  const d = Math.floor(deg);
  const m = Math.floor((deg - d) * 60);
  return `${d}° ${m.toString().padStart(2, "0")}'`;
}

/**
 * Calculate Jaimini 7 Chara Karakas (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn)
 */
export function calculateCharaKarakas(
  planets: PlanetInfo[],
  ascendantSignIndex: number
): { charaKarakas: CharaKarakaItem[]; karakamshaSignIndex: number } {
  const physicalPlanets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"];
  const eligible = planets
    .filter((p) => physicalPlanets.includes(normalizePlanetName(p.name)))
    .map((p) => {
      const normLong = ((p.longitude % 360) + 360) % 360;
      const degInSign = p.degree_in_sign ?? (normLong % 30);
      const signIndex = p.sign_index || Math.floor(normLong / 30) + 1;
      const house = p.house || ((signIndex - ascendantSignIndex + 12) % 12) + 1;
      return {
        name: normalizePlanetName(p.name),
        longitude: normLong,
        degreeInSign: degInSign,
        signIndex,
        house,
      };
    });

  // Sort descending by degreeInSign
  eligible.sort((a, b) => b.degreeInSign - a.degreeInSign);

  const roles: {
    role: "AK" | "AmK" | "BK" | "MK" | "PK" | "GK" | "DK";
    nameEn: string;
    nameTa: string;
    sigEn: string;
    sigTa: string;
  }[] = [
    {
      role: "AK",
      nameEn: "Atma Karaka (Soul & Self)",
      nameTa: "ஆத்ம காரகன் (ஆன்ம பலம்)",
      sigEn: "Signifies spiritual essence, supreme destiny, life mission, and inner self.",
      sigTa: "ஆன்ம இயல்பு, தலையாய விதி மற்றும் ஜீவாத்மாவின் முக்கிய வாழ்க்கை நோக்கத்தை குறிக்கிறது.",
    },
    {
      role: "AmK",
      nameEn: "Amatya Karaka (Career & Status)",
      nameTa: "அமாத்திய காரகன் (தொழில் & பதவி)",
      sigEn: "Signifies career elevation, authority, professional status, and livelihood.",
      sigTa: "உத்தியோக வளர்ச்சி, சமூக அந்தஸ்து, தொழில் வெற்றி மற்றும் வாழ்வாதாரத்தை குறிக்கிறது.",
    },
    {
      role: "BK",
      nameEn: "Bhratri Karaka (Siblings & Guru)",
      nameTa: "பிராத்ரு காரகன் (உடன்பிறப்பு & குரு)",
      sigEn: "Signifies mentors, guru, advisors, siblings, and inner courage.",
      sigTa: "வழிகாட்டிகள், குருமார்கள், உடன் பிறந்தவர்கள் மற்றும் நெஞ்சின் துணிச்சலை குறிக்கிறது.",
    },
    {
      role: "MK",
      nameEn: "Matri Karaka (Mother & Property)",
      nameTa: "மாத்ரு காரகன் (தாய் & சொத்துக்கள்)",
      sigEn: "Signifies mother, home, fixed properties, conveyances, and emotional peace.",
      sigTa: "தாயார், வசிப்பிடம், சொந்த வீடு, வாகனம் மற்றும் மன நிம்மதியை குறிக்கிறது.",
    },
    {
      role: "PK",
      nameEn: "Putra Karaka (Progeny & Intellect)",
      nameTa: "புத்ர காரகன் (சந்ததி & புத்தி)",
      sigEn: "Signifies children, higher intelligence, creativity, and merit from past lives.",
      sigTa: "குழந்தைப் பேறு, கூர்மையான புத்தி கூர்மை மற்றும் பூர்வ புண்ணிய பலன்களை குறிக்கிறது.",
    },
    {
      role: "GK",
      nameEn: "Gnati Karaka (Strife & Resilience)",
      nameTa: "ஞானாதி காரகன் (போராட்டம் & வெற்றி)",
      sigEn: "Signifies competition, obstacles, kinship disputes, and perseverance under pressure.",
      sigTa: "போட்டி பொறாமைகள், தடைகள், பங்காளி பகைகள் மற்றும் சவால்களை வெல்லும் ஆற்றலை குறிக்கிறது.",
    },
    {
      role: "DK",
      nameEn: "Dara Karaka (Spouse & Partnerships)",
      nameTa: "தார காரகன் (களத்திரம் & துணை)",
      sigEn: "Signifies spouse, romantic unions, marital harmony, and intimate alliances.",
      sigTa: "வாழ்க்கைத் துணைவர், தாம்பத்திய உறவு, திருமண பந்தம் மற்றும் கூட்டாளிகளை குறிக்கிறது.",
    },
  ];

  const charaKarakas: CharaKarakaItem[] = eligible.slice(0, 7).map((p, idx) => {
    const meta = roles[idx] || roles[roles.length - 1];
    return {
      role: meta.role,
      roleNameEn: meta.nameEn,
      roleNameTa: meta.nameTa,
      planet: p.name,
      degreeInSign: parseFloat(p.degreeInSign.toFixed(3)),
      formattedDegree: formatDegMin(p.degreeInSign),
      signIndex: p.signIndex,
      signNameEn: ZODIAC_NAMES_EN[p.signIndex] || "Aries",
      signNameTa: ZODIAC_NAMES_TA[p.signIndex] || "மேஷம்",
      house: p.house,
      significationEn: meta.sigEn,
      significationTa: meta.sigTa,
    };
  });

  // Karakamsha is the Navamsha sign of Atma Karaka (AK)
  const akPlanet = charaKarakas.find((k) => k.role === "AK");
  const akLong = akPlanet
    ? (eligible.find((p) => p.name === akPlanet.planet)?.longitude ?? 0)
    : 0;
  const karakamshaSignIndex = calculateNavamshaSign(akLong);

  return { charaKarakas, karakamshaSignIndex };
}

/**
 * Calculate Jaimini Arudha Pada
 */
export function calculateArudhaPada(
  ascendantSignIndex: number,
  targetHouseNumber: number,
  planets: PlanetInfo[]
): { signIndex: number; houseNumber: number } {
  const targetSignIndex = ((ascendantSignIndex - 1 + (targetHouseNumber - 1)) % 12) + 1;
  const lordName = SIGN_LORDS_MAP[targetSignIndex];
  const lordPlanet = planets.find((p) => normalizePlanetName(p.name) === lordName);
  const lordSignIndex = lordPlanet
    ? lordPlanet.sign_index || Math.floor((((lordPlanet.longitude % 360) + 360) % 360) / 30) + 1
    : targetSignIndex;

  // Distance from target house to lord's sign
  const distance = ((lordSignIndex - targetSignIndex + 12) % 12);
  let arudhaSignIndex = ((lordSignIndex - 1 + distance) % 12) + 1;

  // Jaimini exception rule: If Pada falls in 1st or 7th from house, shift by 10 signs
  const distFromTarget = ((arudhaSignIndex - targetSignIndex + 12) % 12);
  if (distFromTarget === 0 || distFromTarget === 6) {
    arudhaSignIndex = ((arudhaSignIndex - 1 + 9) % 12) + 1;
  }

  const houseNumber = ((arudhaSignIndex - ascendantSignIndex + 12) % 12) + 1;
  return { signIndex: arudhaSignIndex, houseNumber };
}

/**
 * Calculate Beeja Sphuta & Kshetra Sphuta for Childbirth
 */
export function calculateBeejaKshetraSphuta(planets: PlanetInfo[]): BeejaKshetraAnalysis {
  const getLong = (name: string): number => {
    const p = planets.find((item) => normalizePlanetName(item.name) === name);
    return p ? ((p.longitude % 360) + 360) % 360 : 0;
  };

  const sunLong = getLong("Sun");
  const venusLong = getLong("Venus");
  const jupiterLong = getLong("Jupiter");
  const moonLong = getLong("Moon");
  const marsLong = getLong("Mars");

  // Beeja Sphuta = (Sun + Venus + Jupiter) % 360
  const beejaLong = ((sunLong + venusLong + jupiterLong) % 360 + 360) % 360;
  const beejaSignIndex = Math.floor(beejaLong / 30) + 1;
  const beejaDegInSign = beejaLong % 30;
  const beejaNavSign = calculateNavamshaSign(beejaLong);
  const isBeejaSignOdd = beejaSignIndex % 2 !== 0;
  const isBeejaNavOdd = beejaNavSign % 2 !== 0;

  // Watery signs (4 Cancer, 8 Scorpio, 12 Pisces) + 2 Taurus = Fruitful
  // Gemini 3, Leo 5, Virgo 6 = Barren
  const fruitfulSigns = [2, 4, 8, 12];
  const barrenSigns = [3, 5, 6];

  let beejaFruitfulness: "fruitful" | "semi_fruitful" | "barren" = "semi_fruitful";
  if (fruitfulSigns.includes(beejaSignIndex)) beejaFruitfulness = "fruitful";
  else if (barrenSigns.includes(beejaSignIndex)) beejaFruitfulness = "barren";

  let beejaVerdictEn = "";
  let beejaVerdictTa = "";
  let beejaScore = 70;

  if (isBeejaSignOdd && isBeejaNavOdd) {
    beejaVerdictEn = "Highly Potent & Auspicious (Odd Rasi + Odd Navamsha). Strong male vitality for progeny.";
    beejaVerdictTa = "முழுமையான விந்து வீரியம் (ஒற்றை ராசி + ஒற்றை நவாம்சம்). சந்தான பாக்கியத்திற்கான பலம் நிறைந்துள்ளது.";
    beejaScore = 95;
  } else if (!isBeejaSignOdd && !isBeejaNavOdd) {
    beejaVerdictEn = "Even Rasi & Even Navamsha. Medical vitality checks or Santana Gopala prayer recommended.";
    beejaVerdictTa = "இரட்டை ராசி + இரட்டை நவாம்சம். விந்து பலத்தை கூட்ட மருத்துவ ஆலோசனையும் சந்தான கோபால வழிபாடும் நலம்.";
    beejaScore = 55;
  } else {
    beejaVerdictEn = "Mixed Sign Harmony (One Odd, One Even). Moderate fertility; smooth conception during benefic Dasa-Bhuktis.";
    beejaVerdictTa = "சமநிலையான பலன் (ஒரு ஒற்றை, ஒரு இரட்டை). சுப தசா புக்திகளில் எளிதாக புத்திர பாக்கியம் கைகூடும்.";
    beejaScore = 78;
  }

  // Kshetra Sphuta = (Moon + Mars + Jupiter) % 360
  const kshetraLong = ((moonLong + marsLong + jupiterLong) % 360 + 360) % 360;
  const kshetraSignIndex = Math.floor(kshetraLong / 30) + 1;
  const kshetraDegInSign = kshetraLong % 30;
  const kshetraNavSign = calculateNavamshaSign(kshetraLong);
  const isKshetraSignEven = kshetraSignIndex % 2 === 0;
  const isKshetraNavEven = kshetraNavSign % 2 === 0;

  let kshetraFruitfulness: "fruitful" | "semi_fruitful" | "barren" = "semi_fruitful";
  if (fruitfulSigns.includes(kshetraSignIndex)) kshetraFruitfulness = "fruitful";
  else if (barrenSigns.includes(kshetraSignIndex)) kshetraFruitfulness = "barren";

  let kshetraVerdictEn = "";
  let kshetraVerdictTa = "";
  let kshetraScore = 70;

  if (isKshetraSignEven && isKshetraNavEven) {
    kshetraVerdictEn = "Deeply Receptive & Fertile (Even Rasi + Even Navamsha). Womb receptivity is optimally primed.";
    kshetraVerdictTa = "உன்னதமான கருப்பை ஏற்புத்திறன் (இரட்டை ராசி + இரட்டை நவாம்சம்). சந்ததி உருவாக்கத்திற்கு மிக உகந்தது.";
    kshetraScore = 95;
  } else if (!isKshetraSignEven && !isKshetraNavEven) {
    kshetraVerdictEn = "Odd Rasi & Odd Navamsha. Excess internal heat or hormonal delay; cooling nourishment and Garbharakshambigai puja advised.";
    kshetraVerdictTa = "ஒற்றை ராசி + ஒற்றை நவாம்சம். உடலின் அதீத உஷ்ணம் காரணமாக தாமதம் ஏற்படலாம்; கர்ப்பரக்ஷாம்பிகை வழிபாடு நலம்.";
    kshetraScore = 55;
  } else {
    kshetraVerdictEn = "Mixed Planetary Harmony. Receptive field; conception favorable when transit Jupiter touches 5th/9th.";
    kshetraVerdictTa = "மிதமான ஏற்புத்திறன். கோச்சார குரு 5 அல்லது 9-ம் வீட்டை நோக்கும்போது எளிதில் கருத்தரிப்பு நிகழும்.";
    kshetraScore = 78;
  }

  return {
    beejaSphuta: {
      longitude: beejaLong,
      signIndex: beejaSignIndex,
      signNameEn: ZODIAC_NAMES_EN[beejaSignIndex] || "Aries",
      signNameTa: ZODIAC_NAMES_TA[beejaSignIndex] || "மேஷம்",
      degreeInSign: beejaDegInSign,
      formattedDegree: formatDegMin(beejaDegInSign),
      navamshaSignIndex: beejaNavSign,
      navamshaSignNameEn: ZODIAC_NAMES_EN[beejaNavSign] || "Aries",
      navamshaSignNameTa: ZODIAC_NAMES_TA[beejaNavSign] || "மேஷம்",
      isSignOdd: isBeejaSignOdd,
      isNavamshaOdd: isBeejaNavOdd,
      fruitfulness: beejaFruitfulness,
      potencyVerdictEn: beejaVerdictEn,
      potencyVerdictTa: beejaVerdictTa,
      vitalityScore: beejaScore,
    },
    kshetraSphuta: {
      longitude: kshetraLong,
      signIndex: kshetraSignIndex,
      signNameEn: ZODIAC_NAMES_EN[kshetraSignIndex] || "Aries",
      signNameTa: ZODIAC_NAMES_TA[kshetraSignIndex] || "மேஷம்",
      degreeInSign: kshetraDegInSign,
      formattedDegree: formatDegMin(kshetraDegInSign),
      navamshaSignIndex: kshetraNavSign,
      navamshaSignNameEn: ZODIAC_NAMES_EN[kshetraNavSign] || "Aries",
      navamshaSignNameTa: ZODIAC_NAMES_TA[kshetraNavSign] || "மேஷம்",
      isSignEven: isKshetraSignEven,
      isNavamshaEven: isKshetraNavEven,
      fruitfulness: kshetraFruitfulness,
      receptivityVerdictEn: kshetraVerdictEn,
      receptivityVerdictTa: kshetraVerdictTa,
      vitalityScore: kshetraScore,
    },
  };
}

/**
 * Evaluates K.N. Rao's Double Transit aspect patterns for Saturn and Jupiter,
 * strictly incorporating K.N. Rao's Retrograde Rule (aspecting also from the previous sign).
 */
export function evaluateDoubleTransitSignAspects(
  transits?: LiveTransitsResponse | null
): { saturnDetail: DoubleTransitAspectDetail; jupiterDetail: DoubleTransitAspectDetail } {
  // Fallbacks if transits not yet loaded: use realistic default ephemeris positions
  let satPlanet = transits?.planets?.find((p) => normalizePlanetName(p.name) === "Saturn");
  let jupPlanet = transits?.planets?.find((p) => normalizePlanetName(p.name) === "Jupiter");

  // Default to Pisces (12) for Saturn and Taurus (2) / Gemini (3) for Jupiter if live data is not ready
  const satSign = satPlanet?.sign_index ?? 12; // Pisces
  const satIsRetro = satPlanet?.is_retrograde ?? false;

  const jupSign = jupPlanet?.sign_index ?? 2; // Taurus
  const jupIsRetro = jupPlanet?.is_retrograde ?? false;

  // Saturn casts: 1st (conjunction), 3rd, 7th, 10th aspects
  const satAspects: DoubleTransitAspectDetail["aspectsCastingOnSigns"] = [
    {
      signIndex: satSign,
      signNameEn: ZODIAC_NAMES_EN[satSign],
      aspectType: "1st (Conjunction)",
      isFromRetrogradePrecedingSign: false,
    },
    {
      signIndex: ((satSign - 1 + 2) % 12) + 1,
      signNameEn: ZODIAC_NAMES_EN[((satSign - 1 + 2) % 12) + 1],
      aspectType: "3rd Aspect",
      isFromRetrogradePrecedingSign: false,
    },
    {
      signIndex: ((satSign - 1 + 6) % 12) + 1,
      signNameEn: ZODIAC_NAMES_EN[((satSign - 1 + 6) % 12) + 1],
      aspectType: "7th Direct Aspect",
      isFromRetrogradePrecedingSign: false,
    },
    {
      signIndex: ((satSign - 1 + 9) % 12) + 1,
      signNameEn: ZODIAC_NAMES_EN[((satSign - 1 + 9) % 12) + 1],
      aspectType: "10th Aspect",
      isFromRetrogradePrecedingSign: false,
    },
  ];

  // K.N. RAO RETROGRADE RULE: If Saturn is retrograde, it ALSO aspects from the previous sign (sign - 1)
  if (satIsRetro) {
    const prevSatSign = ((satSign - 2 + 12) % 12) + 1;
    satAspects.push(
      {
        signIndex: prevSatSign,
        signNameEn: ZODIAC_NAMES_EN[prevSatSign],
        aspectType: "Preceding Sign Conjunction (Retrograde Influence)",
        isFromRetrogradePrecedingSign: true,
      },
      {
        signIndex: ((prevSatSign - 1 + 2) % 12) + 1,
        signNameEn: ZODIAC_NAMES_EN[((prevSatSign - 1 + 2) % 12) + 1],
        aspectType: "3rd Aspect (from Preceding Sign / Retrograde)",
        isFromRetrogradePrecedingSign: true,
      },
      {
        signIndex: ((prevSatSign - 1 + 6) % 12) + 1,
        signNameEn: ZODIAC_NAMES_EN[((prevSatSign - 1 + 6) % 12) + 1],
        aspectType: "7th Aspect (from Preceding Sign / Retrograde)",
        isFromRetrogradePrecedingSign: true,
      },
      {
        signIndex: ((prevSatSign - 1 + 9) % 12) + 1,
        signNameEn: ZODIAC_NAMES_EN[((prevSatSign - 1 + 9) % 12) + 1],
        aspectType: "10th Aspect (from Preceding Sign / Retrograde)",
        isFromRetrogradePrecedingSign: true,
      }
    );
  }

  // Jupiter casts: 1st (conjunction), 5th, 7th, 9th aspects
  const jupAspects: DoubleTransitAspectDetail["aspectsCastingOnSigns"] = [
    {
      signIndex: jupSign,
      signNameEn: ZODIAC_NAMES_EN[jupSign],
      aspectType: "1st (Conjunction)",
      isFromRetrogradePrecedingSign: false,
    },
    {
      signIndex: ((jupSign - 1 + 4) % 12) + 1,
      signNameEn: ZODIAC_NAMES_EN[((jupSign - 1 + 4) % 12) + 1],
      aspectType: "5th Trinal Aspect",
      isFromRetrogradePrecedingSign: false,
    },
    {
      signIndex: ((jupSign - 1 + 6) % 12) + 1,
      signNameEn: ZODIAC_NAMES_EN[((jupSign - 1 + 6) % 12) + 1],
      aspectType: "7th Direct Aspect",
      isFromRetrogradePrecedingSign: false,
    },
    {
      signIndex: ((jupSign - 1 + 8) % 12) + 1,
      signNameEn: ZODIAC_NAMES_EN[((jupSign - 1 + 8) % 12) + 1],
      aspectType: "9th Trinal Aspect",
      isFromRetrogradePrecedingSign: false,
    },
  ];

  // K.N. RAO RETROGRADE RULE: If Jupiter is retrograde, it ALSO aspects from the previous sign (sign - 1)
  if (jupIsRetro) {
    const prevJupSign = ((jupSign - 2 + 12) % 12) + 1;
    jupAspects.push(
      {
        signIndex: prevJupSign,
        signNameEn: ZODIAC_NAMES_EN[prevJupSign],
        aspectType: "Preceding Sign Conjunction (Retrograde Blessing)",
        isFromRetrogradePrecedingSign: true,
      },
      {
        signIndex: ((prevJupSign - 1 + 4) % 12) + 1,
        signNameEn: ZODIAC_NAMES_EN[((prevJupSign - 1 + 4) % 12) + 1],
        aspectType: "5th Trine Aspect (from Preceding Sign / Retrograde)",
        isFromRetrogradePrecedingSign: true,
      },
      {
        signIndex: ((prevJupSign - 1 + 6) % 12) + 1,
        signNameEn: ZODIAC_NAMES_EN[((prevJupSign - 1 + 6) % 12) + 1],
        aspectType: "7th Aspect (from Preceding Sign / Retrograde)",
        isFromRetrogradePrecedingSign: true,
      },
      {
        signIndex: ((prevJupSign - 1 + 8) % 12) + 1,
        signNameEn: ZODIAC_NAMES_EN[((prevJupSign - 1 + 8) % 12) + 1],
        aspectType: "9th Trine Aspect (from Preceding Sign / Retrograde)",
        isFromRetrogradePrecedingSign: true,
      }
    );
  }

  return {
    saturnDetail: {
      planet: "Saturn",
      currentSignIndex: satSign,
      currentSignNameEn: ZODIAC_NAMES_EN[satSign],
      currentSignNameTa: ZODIAC_NAMES_TA[satSign],
      isRetrograde: satIsRetro,
      aspectsCastingOnSigns: satAspects,
    },
    jupiterDetail: {
      planet: "Jupiter",
      currentSignIndex: jupSign,
      currentSignNameEn: ZODIAC_NAMES_EN[jupSign],
      currentSignNameTa: ZODIAC_NAMES_TA[jupSign],
      isRetrograde: jupIsRetro,
      aspectsCastingOnSigns: jupAspects,
    },
  };
}

/**
 * Checks whether Saturn and Jupiter concurrently influence a given target house or its lord
 */
export function checkDoubleTransitOnTarget(
  targetSignIndex: number,
  targetLordSignIndex: number,
  saturnDetail: DoubleTransitAspectDetail,
  jupiterDetail: DoubleTransitAspectDetail
): DoubleTransitStatus {
  // Check Saturn influence on target house OR target lord sign
  const satHitsHouse = saturnDetail.aspectsCastingOnSigns.find((a) => a.signIndex === targetSignIndex);
  const satHitsLord = saturnDetail.aspectsCastingOnSigns.find((a) => a.signIndex === targetLordSignIndex);
  const satInfluences = !!(satHitsHouse || satHitsLord);

  let satSourceEn = "";
  let satSourceTa = "";
  if (satHitsHouse) {
    satSourceEn = `Saturn influences House (${satHitsHouse.aspectType} on ${satHitsHouse.signNameEn}${
      satHitsHouse.isFromRetrogradePrecedingSign ? " via Retrograde backward aspect" : ""
    })`;
    satSourceTa = `சனி வீட்டை நோக்குகிறார் (${satHitsHouse.signNameEn} மீது ${satHitsHouse.aspectType})`;
  } else if (satHitsLord) {
    satSourceEn = `Saturn influences House Lord (${satHitsLord.aspectType} on ${satHitsLord.signNameEn})`;
    satSourceTa = `சனி அதிபதியை நோக்குகிறார் (${satHitsLord.signNameEn} மீது ${satHitsLord.aspectType})`;
  }

  // Check Jupiter influence on target house OR target lord sign
  const jupHitsHouse = jupiterDetail.aspectsCastingOnSigns.find((a) => a.signIndex === targetSignIndex);
  const jupHitsLord = jupiterDetail.aspectsCastingOnSigns.find((a) => a.signIndex === targetLordSignIndex);
  const jupInfluences = !!(jupHitsHouse || jupHitsLord);

  let jupSourceEn = "";
  let jupSourceTa = "";
  if (jupHitsHouse) {
    jupSourceEn = `Jupiter blesses House (${jupHitsHouse.aspectType} on ${jupHitsHouse.signNameEn}${
      jupHitsHouse.isFromRetrogradePrecedingSign ? " via Retrograde backward trine" : ""
    })`;
    jupSourceTa = `குரு வீட்டைப் பார்க்கிறார் (${jupHitsHouse.signNameEn} மீது ${jupHitsHouse.aspectType})`;
  } else if (jupHitsLord) {
    jupSourceEn = `Jupiter blesses House Lord (${jupHitsLord.aspectType} on ${jupHitsLord.signNameEn})`;
    jupSourceTa = `குரு அதிபதியைப் பார்க்கிறார் (${jupHitsLord.signNameEn} மீது ${jupHitsLord.aspectType})`;
  }

  const isFulfilled = satInfluences && jupInfluences;

  let summaryEn = "";
  let summaryTa = "";

  if (isFulfilled) {
    summaryEn =
      "Double Transit Fulfilled: Both Saturn (karmic sanction) and Jupiter (divine grace) actively influence this domain.";
    summaryTa =
      "இரட்டைப் பெயர்ச்சி விதி பூர்த்தியானது: சனி பகவானின் கர்ம முத்திரையும் குரு பகவானின் சுப கடாட்சமும் இணைந்து செயல்படுகின்றன.";
  } else if (jupInfluences && !satInfluences) {
    summaryEn =
      "Partial Sanction: Jupiter's divine grace is activated; awaiting Saturn's karmic maturation for final fruition.";
    summaryTa =
      "பகுதி சுபத்துவம்: குருவின் சுப பார்வை கிடைத்துள்ளது; சனியின் கர்ம அங்கீகாரத்திற்காக காத்திருக்க வேண்டும்.";
  } else if (satInfluences && !jupInfluences) {
    summaryEn =
      "Structural Pressure: Saturn demands discipline and foundation-building; event awaits Jupiter's protective glance.";
    summaryTa =
      "கட்டமைப்பு காலம்: சனியின் அழுத்தம் உள்ளது; குருவின் சுபப் பார்வை பட்டவுடன் காரியம் வெற்றி பெறும்.";
  } else {
    summaryEn =
      "Gochara Inactive: Transiting Saturn and Jupiter are currently dormant for this house; foundational phase.";
    summaryTa =
      "கோச்சாரம் அமைதி: தற்போதைய கோச்சாரத்தில் இந்த பாவத்திற்கு நேரடி பார்வைகள் இல்லை; முன்னேற்பாடு காலம்.";
  }

  return {
    isFulfilled,
    saturnInfluences: satInfluences,
    saturnAspectSource: satSourceEn,
    saturnAspectSourceTa: satSourceTa,
    jupiterInfluences: jupInfluences,
    jupiterAspectSource: jupSourceEn,
    jupiterAspectSourceTa: jupSourceTa,
    summaryEn,
    summaryTa,
  };
}

/**
 * Checks for Special Composite Yogas cited in Marc Boney's work:
 * - Virinchi Yoga (Spiritual wisdom & disciples)
 * - Jaimini Moon-Venus Dhana Yoga (Enormous wealth)
 * - Saraswati Yoga (Scholarly excellence)
 */
export function checkSpecialCompositeYogas(
  planets: PlanetInfo[],
  ascendantSignIndex: number
): SpecialCompositeYogas {
  const getPlanet = (name: string) => planets.find((p) => normalizePlanetName(p.name) === name);

  const jupiter = getPlanet("Jupiter");
  const saturn = getPlanet("Saturn");
  const venus = getPlanet("Venus");
  const moon = getPlanet("Moon");
  const mercury = getPlanet("Mercury");

  const fifthSign = ((ascendantSignIndex - 1 + 4) % 12) + 1;
  const fifthLordName = SIGN_LORDS_MAP[fifthSign];
  const fifthLord = getPlanet(fifthLordName);

  // 1. Virinchi Yoga: Jupiter, Saturn and 5th lord placed in Kendras (1,4,7,10) or Trikonas (1,5,9) in exalted or own signs
  let virinchiPresent = false;
  let virinchiStrength: "powerful" | "moderate" | "none" = "none";
  let virinchiDescEn = "Not present in the chart.";
  let virinchiDescTa = "ஜாதகத்தில் அமைந்திருக்கவில்லை.";

  if (jupiter && saturn && fifthLord) {
    const isKendraOrTrikona = (p: PlanetInfo) => {
      const h = p.house || ((((p.sign_index || 1) - ascendantSignIndex + 12) % 12) + 1);
      return [1, 4, 5, 7, 9, 10].includes(h);
    };

    const jupKendra = isKendraOrTrikona(jupiter);
    const satKendra = isKendraOrTrikona(saturn);
    const fifthKendra = isKendraOrTrikona(fifthLord);

    if (jupKendra && satKendra && fifthKendra) {
      virinchiPresent = true;
      virinchiStrength = "powerful";
      virinchiDescEn =
        "Virinchi Yoga Active: Jupiter, Saturn, and the 5th Lord are all strongly dignified in Kendras/Trikonas. Bestows supreme spiritual discrimination, disciples, scholarly authority, and long life.";
      virinchiDescTa =
        "விரிஞ்சி யோகம் செயலில் உள்ளது: குரு, சனி மற்றும் 5-ம் அதிபதி கேந்திர திரிகோணங்களில் பலம் பெற்றுள்ளனர். ஞானம், ஆன்மீக விழிப்புணர்வு, சீடர்கள் மற்றும் மேலான அறிவுத்திறனை நல்கும்.";
    } else if (jupKendra && (satKendra || fifthKendra)) {
      virinchiPresent = true;
      virinchiStrength = "moderate";
      virinchiDescEn =
        "Partial Virinchi Yoga: Jupiter and karmic benefics hold favorable trines, conferring philosophical maturity and intuitive depth.";
      virinchiDescTa =
        "பகுதி விரிஞ்சி யோகம்: குருவும் சனியும் சுப திரிகோண தொடர்பில் இருப்பதால் ஆழ்ந்த தத்துவ ஞானமும் உள்ளுணர்வும் வாய்க்கும்.";
    }
  }

  // 2. Jaimini Moon-Venus Dhana Yoga: Moon and Venus aspecting each other or conjunct
  let dhanaPresent = false;
  let dhanaStrength: "exceptional" | "moderate" | "none" = "none";
  let dhanaDescEn = "Standard planetary wealth configurations.";
  let dhanaDescTa = "சாதாரண தன அமைப்புகள்.";

  if (moon && venus) {
    const moonSign = moon.sign_index || 1;
    const venusSign = venus.sign_index || 1;
    const dist = ((venusSign - moonSign + 12) % 12);

    if (dist === 0) {
      dhanaPresent = true;
      dhanaStrength = "exceptional";
      dhanaDescEn =
        "Jaimini Moon-Venus Dhana Conjunction: Moon and Venus unite in the same sign, creating abundant liquidity, vehicular luxury, and financial magnetism.";
      dhanaDescTa =
        "ஜைமினி சந்திர-சுக்கிர தன யோகம்: சந்திரனும் சுக்கிரனும் ஒரே ராசியில் இணைந்து பெருமளவு பணப்புழக்கம், வாகன வசதி மற்றும் செல்வ வளத்தை உருவாக்குகின்றன.";
    } else if (dist === 6) {
      dhanaPresent = true;
      dhanaStrength = "exceptional";
      dhanaDescEn =
        "Jaimini Moon-Venus Mutual Aspect: Direct 7th mutual gaze between Moon and Venus forms a classic Jaimini Dhana Yoga of lasting prosperity.";
      dhanaDescTa =
        "சந்திர-சுக்கிர சமசப்தக பார்வை: சந்திரனும் சுக்கிரனும் ஒருவரையொருவர் 7-ம் பார்வையாக பார்த்து நீடித்த ராஜ யோக தன சம்பத்தை வழங்குகின்றனர்.";
    } else if ([3, 4, 8, 9].includes(dist)) {
      dhanaPresent = true;
      dhanaStrength = "moderate";
      dhanaDescEn =
        "Benefic Moon-Venus Kendra/Trikona geometry: Promotes steady cash flow and material comforts.";
      dhanaDescTa =
        "சந்திர-சுக்கிர திரிகோண அமைப்பு: சீரான தன வரவையும் இல்லற வசதிகளையும் நல்கும்.";
    }
  }

  // 3. Saraswati Yoga: Jupiter, Venus, and Mercury in Kendras, Trikonas, or 2nd house with strong Jupiter
  let saraswatiPresent = false;
  let saraswatiStrength: "powerful" | "moderate" | "none" = "none";
  let saraswatiDescEn = "Standard intellectual combinations.";
  let saraswatiDescTa = "சாதாரண வித்யா அமைப்புகள்.";

  if (jupiter && venus && mercury) {
    const getH = (p: PlanetInfo) => p.house || ((((p.sign_index || 1) - ascendantSignIndex + 12) % 12) + 1);
    const validHouses = [1, 2, 4, 5, 7, 9, 10];
    if (validHouses.includes(getH(jupiter)) && validHouses.includes(getH(venus)) && validHouses.includes(getH(mercury))) {
      saraswatiPresent = true;
      saraswatiStrength = "powerful";
      saraswatiDescEn =
        "Saraswati Yoga: All three intellectual benefics (Jupiter, Venus, Mercury) occupy Kendra/Trikona/2nd houses. Bestows eloquence, artistic virtuosity, literary talent, and scholastic acclaim.";
      saraswatiDescTa =
        "சரஸ்வதி யோகம்: குரு, சுக்கிரன், புதன் ஆகிய மூன்று சுப கிரகங்களும் கேந்திர, திரிகோண அல்லது 2-ம் வீட்டில் அமர்ந்துள்ளனர். வாக்கு வன்மை, எழுத்துத் திறன், கலை ஞானம் மற்றும் கல்விப் புகழை தரும்.";
    }
  }

  // Arudha Padas
  const upapada = calculateArudhaPada(ascendantSignIndex, 12, planets);
  const pada4 = calculateArudhaPada(ascendantSignIndex, 4, planets);
  const pada11 = calculateArudhaPada(ascendantSignIndex, 11, planets);

  return {
    virinchiYoga: {
      present: virinchiPresent,
      strength: virinchiStrength,
      descriptionEn: virinchiDescEn,
      descriptionTa: virinchiDescTa,
    },
    jaiminiMoonVenusDhanaYoga: {
      present: dhanaPresent,
      strength: dhanaStrength,
      descriptionEn: dhanaDescEn,
      descriptionTa: dhanaDescTa,
    },
    saraswatiYoga: {
      present: saraswatiPresent,
      strength: saraswatiStrength,
      descriptionEn: saraswatiDescEn,
      descriptionTa: saraswatiDescTa,
    },
    upapadaLagna: {
      signIndex: upapada.signIndex,
      signNameEn: ZODIAC_NAMES_EN[upapada.signIndex],
      signNameTa: ZODIAC_NAMES_TA[upapada.signIndex],
      houseNumber: upapada.houseNumber,
    },
    arudhaPada4: {
      signIndex: pada4.signIndex,
      signNameEn: ZODIAC_NAMES_EN[pada4.signIndex],
      signNameTa: ZODIAC_NAMES_TA[pada4.signIndex],
      houseNumber: pada4.houseNumber,
    },
    arudhaPada11: {
      signIndex: pada11.signIndex,
      signNameEn: ZODIAC_NAMES_EN[pada11.signIndex],
      signNameTa: ZODIAC_NAMES_TA[pada11.signIndex],
      houseNumber: pada11.houseNumber,
    },
  };
}

/**
 * Main Marc Boney & K.N. Rao Composite Analysis Engine
 */
export function analyzeMarcBoneyComposite(
  horoscope: HoroscopeResponse,
  dasa?: DasaResponse,
  liveTransits?: LiveTransitsResponse | null
): MarcBoneyAnalysisResult {
  const ascSign = horoscope.ascendant?.sign_index || 1;
  const planets = horoscope.planets || [];

  // Determine Active Dasa, Bukthi, Andhara Lords
  const activeDasaLord = dasa?.active_period?.mahadasha || "Jupiter";
  const activeBukthiLord = dasa?.active_period?.antardasha || "Saturn";
  const activeAndharaLord = dasa?.active_period?.pratyantardasha;

  // Dasa Lagna: Sign occupied by the active Mahadasha lord in the natal chart
  const dasaLordPlanet = planets.find((p) => normalizePlanetName(p.name) === activeDasaLord);
  const dasaLagnaSignIndex = dasaLordPlanet
    ? dasaLordPlanet.sign_index || Math.floor((((dasaLordPlanet.longitude % 360) + 360) % 360) / 30) + 1
    : ascSign;

  // Calculate Jaimini 7 Chara Karakas
  const { charaKarakas, karakamshaSignIndex } = calculateCharaKarakas(planets, ascSign);

  // Calculate Beeja & Kshetra Sphuta
  const beejaKshetra = calculateBeejaKshetraSphuta(planets);

  // Evaluate Live or Ephemeris Double Transit details
  const { saturnDetail, jupiterDetail } = evaluateDoubleTransitSignAspects(liveTransits);

  // Evaluate Special Yogas & Arudhas
  const specialYogas = checkSpecialCompositeYogas(planets, ascSign);

  // Helper to find lord of a house from Janma Lagna
  const getHouseLordName = (houseNum: number): string => {
    const signIdx = ((ascSign - 1 + (houseNum - 1)) % 12) + 1;
    return SIGN_LORDS_MAP[signIdx];
  };

  const getPlanetPlacementSign = (planetName: string): number => {
    const p = planets.find((item) => normalizePlanetName(item.name) === planetName);
    return p ? (p.sign_index || Math.floor((((p.longitude % 360) + 360) % 360) / 30) + 1) : 1;
  };

  // Helper to evaluate Dasa-Bhukti Lord alignment with houses
  const checkPeriodLordConnection = (
    lordName: string,
    targetHouses: number[]
  ): boolean => {
    const p = planets.find((item) => normalizePlanetName(item.name) === lordName);
    if (!p) return false;
    const h = p.house || ((((p.sign_index || 1) - ascSign + 12) % 12) + 1);
    if (targetHouses.includes(h)) return true;

    // Check houses owned by this lord
    for (const th of targetHouses) {
      if (getHouseLordName(th) === lordName) return true;
    }
    return false;
  };

  // Helper to determine status based on score
  const getStatusMeta = (score: number) => {
    if (score >= 82) {
      return {
        status: "high_imminent" as const,
        badgeEn: "Highly Favorable / Imminent",
        badgeTa: "மிகவும் சாதகமான உச்சக் காலம்",
      };
    }
    if (score >= 68) {
      return {
        status: "favorable" as const,
        badgeEn: "Favorable Alignment",
        badgeTa: "சுப யோக சங்கமம்",
      };
    }
    if (score >= 50) {
      return {
        status: "moderate" as const,
        badgeEn: "Moderate / Emerging",
        badgeTa: "மிதமான வளர்ச்சிக்காலம்",
      };
    }
    return {
      status: "preparatory" as const,
      badgeEn: "Preparatory Foundation",
      badgeTa: "முன்னேற்பாடு காலம்",
    };
  };

  // =========================================================================
  // 1. EDUCATIONAL ACHIEVEMENT (5th, 4th, 9th; PK; Saraswati/Budhaditya; D-24)
  // =========================================================================
  const eduLords = [getHouseLordName(5), getHouseLordName(4), getHouseLordName(9)];
  const eduHouse5Sign = ((ascSign - 1 + 4) % 12) + 1;
  const eduLord5Sign = getPlanetPlacementSign(eduLords[0]);
  const eduDoubleTransit = checkDoubleTransitOnTarget(
    eduHouse5Sign,
    eduLord5Sign,
    saturnDetail,
    jupiterDetail
  );

  const eduDasaActive =
    checkPeriodLordConnection(activeDasaLord, [5, 4, 9]) ||
    checkPeriodLordConnection(activeBukthiLord, [5, 4, 9]);

  const pkPlanet = charaKarakas.find((k) => k.role === "PK")?.planet || "Mercury";
  const pkConnected = [activeDasaLord, activeBukthiLord].includes(pkPlanet);

  let eduScore = 55;
  if (eduDasaActive) eduScore += 18;
  if (eduDoubleTransit.isFulfilled) eduScore += 20;
  else if (eduDoubleTransit.jupiterInfluences) eduScore += 10;
  if (pkConnected) eduScore += 8;
  if (specialYogas.saraswatiYoga.present) eduScore += 7;
  eduScore = Math.min(96, eduScore);
  const eduMeta = getStatusMeta(eduScore);

  const eduHouseFromDasaLagna = ((eduHouse5Sign - dasaLagnaSignIndex + 12) % 12) + 1;

  const eduPrediction: LifeMilestonePrediction = {
    id: "education",
    domainNameEn: "Academic Distinction & Higher Learning",
    domainNameTa: "உயர் கல்வி & வித்யா யோகம்",
    sanskritTermEn: "Vidya Prapti (5th Bhava)",
    sanskritTermTa: "வித்யா பிராப்தி (5-ம் பாவம்)",
    readinessScore: eduScore,
    status: eduMeta.status,
    statusBadgeEn: eduMeta.badgeEn,
    statusBadgeTa: eduMeta.badgeTa,
    keyHouses: [5, 4, 9],
    primaryHouseLords: eduLords,
    karakasInvolved: {
      parashari: "Mercury & Jupiter",
      jaimini: pkPlanet,
      charaRole: "PK (Putra Karaka)",
    },
    dasaBhuktiAlignment: {
      isAligned: eduDasaActive,
      dasaLord: activeDasaLord,
      bukthiLord: activeBukthiLord,
      andharaLord: activeAndharaLord,
      descriptionEn: eduDasaActive
        ? `Running ${activeDasaLord}-${activeBukthiLord} activates 4th/5th academic houses and Putra Karaka (${pkPlanet}).`
        : `Running period lords maintain indirect supportive connection to scholarship.`,
      descriptionTa: eduDasaActive
        ? `நடப்பு ${activeDasaLord}-${activeBukthiLord} தசா-புக்தி 4 மற்றும் 5-ம் வித்யா ஸ்தானங்களை விழிப்படையச் செய்கிறது.`
        : `தசா நாதர்கள் கல்வி ஸ்தானங்களுக்கு மறைமுக ஆதரவை வழங்குகின்றனர்.`,
    },
    doubleTransit: eduDoubleTransit,
    dasaLagnaInsight: {
      dasaLagnaSignIndex,
      dasaLagnaSignEn: ZODIAC_NAMES_EN[dasaLagnaSignIndex],
      dasaLagnaSignTa: ZODIAC_NAMES_TA[dasaLagnaSignIndex],
      houseFromDasaLagna: eduHouseFromDasaLagna,
      insightEn: `From Dasa Lagna (${ZODIAC_NAMES_EN[dasaLagnaSignIndex]}), the 5th house of intellect falls in house ${eduHouseFromDasaLagna}, indicating mental clarity for examinations.`,
      insightTa: `தசா லக்னத்தில் (${ZODIAC_NAMES_TA[dasaLagnaSignIndex]}) இருந்து 5-ம் அறிவு பாவம் ${eduHouseFromDasaLagna}-ம் வீட்டில் அமைந்து தேர்வுகளில் மேன்மையை உறுதி செய்கிறது.`,
    },
    divisionalCheck: {
      vargaKey: "D-24",
      vargaNameEn: "D-24 Siddhamsa (Higher Learning)",
      vargaNameTa: "D-24 சித்தாம்சம் (உயர் ஞானம்)",
      focalPointEn: "5th and 9th houses in D-24 validate competitive exams, scholarship, and specialized certification.",
      focalPointTa: "D-24-ல் 5 மற்றும் 9-ம் பாவங்கள் போட்டித் தேர்வுகள், பட்டம் மற்றும் ஆராய்ச்சிக் கல்வியை நிர்ணயிக்கின்றன.",
    },
    classicalRulesCitedEn: [
      "Marc Boney Principle: 'Academic breakthrough demands simultaneous activation of 5th house/lord, Putra Karaka, and D-24.'",
      "K.N. Rao Rule: 'Saturn and Jupiter must aspect the 5th house or 5th lord during graduation/competitive examination years.'",
    ],
    classicalRulesCitedTa: [
      "மார்க் போனி விதி: 'உயர் கல்வி சாதனைகளுக்கு 5-ம் அதிபதி, புத்ர காரகன் மற்றும் D-24 சித்தாம்சம் ஒரே நேரத்தில் தூண்டப்பட வேண்டும்.'",
      "கே.என். ராவ் சூத்திரம்: 'பட்டம் பெறும் காலகட்டத்தில் கோச்சார குரு மற்றும் சனியின் பார்வை 5-ம் பாவம் அல்லது அதிபதி மீது விழ வேண்டும்.'",
    ],
    predictiveGuidanceEn:
      "Golden window for professional certifications, competitive entrance exams, and academic honors. Devote focused time to research and writing.",
    predictiveGuidanceTa:
      "போட்டித் தேர்வுகள், பல்கலைக்கழக பட்டங்கள் மற்றும் புதிய சான்றிதழ்கள் பெற இது மிகச் சிறந்த பொற்காலம். கல்வி முயற்சிகள் பெருவெற்றி தரும்.",
  };

  // =========================================================================
  // 2. CAREER RISE & PROMOTION (10th, 1st, 11th; AmK; D-10 10th vs 6th)
  // =========================================================================
  const careerLords = [getHouseLordName(10), getHouseLordName(1), getHouseLordName(11)];
  const careerHouse10Sign = ((ascSign - 1 + 9) % 12) + 1;
  const careerLord10Sign = getPlanetPlacementSign(careerLords[0]);
  const careerDoubleTransit = checkDoubleTransitOnTarget(
    careerHouse10Sign,
    careerLord10Sign,
    saturnDetail,
    jupiterDetail
  );

  const amkPlanet = charaKarakas.find((k) => k.role === "AmK")?.planet || "Sun";
  const amkConnected = [activeDasaLord, activeBukthiLord].includes(amkPlanet);

  const careerDasaActive =
    checkPeriodLordConnection(activeDasaLord, [10, 1, 11]) ||
    checkPeriodLordConnection(activeBukthiLord, [10, 1, 11]);

  let careerScore = 58;
  if (careerDasaActive) careerScore += 18;
  if (careerDoubleTransit.isFulfilled) careerScore += 20;
  else if (careerDoubleTransit.saturnInfluences) careerScore += 10;
  if (amkConnected) careerScore += 10;
  careerScore = Math.min(97, careerScore);
  const careerMeta = getStatusMeta(careerScore);

  const careerHouseFromDasaLagna = ((careerHouse10Sign - dasaLagnaSignIndex + 12) % 12) + 1;

  const careerPrediction: LifeMilestonePrediction = {
    id: "career",
    domainNameEn: "Professional Breakthrough & Career Rise",
    domainNameTa: "உத்தியோக உயர்வு & அதிகார யோகம்",
    sanskritTermEn: "Karma Siddhi (10th Bhava)",
    sanskritTermTa: "கர்ம சித்தி (10-ம் பாவம்)",
    readinessScore: careerScore,
    status: careerMeta.status,
    statusBadgeEn: careerMeta.badgeEn,
    statusBadgeTa: careerMeta.badgeTa,
    keyHouses: [10, 1, 11],
    primaryHouseLords: careerLords,
    karakasInvolved: {
      parashari: "Sun & Saturn",
      jaimini: amkPlanet,
      charaRole: "AmK (Amatya Karaka)",
    },
    dasaBhuktiAlignment: {
      isAligned: careerDasaActive,
      dasaLord: activeDasaLord,
      bukthiLord: activeBukthiLord,
      andharaLord: activeAndharaLord,
      descriptionEn: careerDasaActive
        ? `Running ${activeDasaLord}-${activeBukthiLord} triggers 10th Karmasthana and Amatya Karaka (${amkPlanet}).`
        : `Dasa period supports steady professional consolidation.`,
      descriptionTa: careerDasaActive
        ? `நடப்பு ${activeDasaLord}-${activeBukthiLord} தசா-புக்தி 10-ம் கர்ம ஸ்தானத்தையும் அமாத்திய காரகனையும் (${amkPlanet}) எழுச்சியடையச் செய்கிறது.`
        : `தொழில் களம் சீரான முன்னேற்றப் பாதையில் உள்ளது.`,
    },
    doubleTransit: careerDoubleTransit,
    dasaLagnaInsight: {
      dasaLagnaSignIndex,
      dasaLagnaSignEn: ZODIAC_NAMES_EN[dasaLagnaSignIndex],
      dasaLagnaSignTa: ZODIAC_NAMES_TA[dasaLagnaSignIndex],
      houseFromDasaLagna: careerHouseFromDasaLagna,
      insightEn: `From Dasa Lagna (${ZODIAC_NAMES_EN[dasaLagnaSignIndex]}), the 10th house falls in ${careerHouseFromDasaLagna}, showing leadership elevation and status expansion.`,
      insightTa: `தசா லக்னத்தில் இருந்து 10-ம் கர்ம பாவம் ${careerHouseFromDasaLagna}-ல் அமைவது தலைமைப் பதவியையும் சமூக கௌரவத்தையும் உறுதிப்படுத்துகிறது.`,
    },
    divisionalCheck: {
      vargaKey: "D-10",
      vargaNameEn: "D-10 Dashamsa (Career & Power)",
      vargaNameTa: "D-10 தசாம்சம் (தொழில் & அதிகாரம்)",
      focalPointEn: "Marc Boney emphasizes: 10th house in D-10 represents independent executive authority; 6th house represents subordinate corporate service.",
      focalPointTa: "மார்க் போனி ஆய்வு: D-10-ல் 10-ம் பாவம் சுதந்திரமான அதிகாரத்தையும், 6-ம் பாவம் ஊழிய/சேவைத் துறையையும் குறிக்கிறது.",
    },
    classicalRulesCitedEn: [
      "K.N. Rao Principle: 'No promotion or career breakthrough materializes without Saturn-Jupiter double transit touching 10th house or 10th lord.'",
      "Marc Boney Chara Dasha Law: 'Amatya Karaka (AmK) activation brings peak professional elevation and governmental recognition.'",
    ],
    classicalRulesCitedTa: [
      "கே.என். ராவ் பொன்மொழி: 'கோச்சார சனி-குரு இரட்டைப் பார்வை 10-ம் பாவம் அல்லது அதன் அதிபதியைத் தொடாமல் பெரிய பதவி உயர்வு நடக்காது.'",
      "மார்க் போனி விதி: 'அமாத்திய காரகன் (AmK) தொடர்பு பெறும் காலத்தில் தொழில் அந்தஸ்தும் அரசு கௌரவமும் உச்சம் தொடும்.'",
    ],
    predictiveGuidanceEn:
      "Prime period for salary renegotiation, executive promotion, and launching high-visibility ventures. Assert your leadership.",
    predictiveGuidanceTa:
      "பதவி உயர்வு, ஊதிய உயர்வு மற்றும் புதிய அதிகாரப் பொறுப்புகளை ஏற்க மிக உகந்த தருணம். தயங்காமல் தலைமைப் பொறுப்பை முன்னெடுங்கள்.",
  };

  // =========================================================================
  // 3. FINANCIAL PROSPERITY & WEALTH ACCUMULATION (2nd, 11th; Moon-Venus; D-11)
  // =========================================================================
  const wealthLords = [getHouseLordName(2), getHouseLordName(11), getHouseLordName(9)];
  const wealthHouse11Sign = ((ascSign - 1 + 10) % 12) + 1;
  const wealthLord11Sign = getPlanetPlacementSign(wealthLords[1]);
  const wealthDoubleTransit = checkDoubleTransitOnTarget(
    wealthHouse11Sign,
    wealthLord11Sign,
    saturnDetail,
    jupiterDetail
  );

  const wealthDasaActive =
    checkPeriodLordConnection(activeDasaLord, [2, 11, 9, 5]) ||
    checkPeriodLordConnection(activeBukthiLord, [2, 11, 9, 5]);

  let wealthScore = 56;
  if (wealthDasaActive) wealthScore += 18;
  if (wealthDoubleTransit.isFulfilled) wealthScore += 18;
  else if (wealthDoubleTransit.jupiterInfluences) wealthScore += 10;
  if (specialYogas.jaiminiMoonVenusDhanaYoga.present) wealthScore += 12;
  wealthScore = Math.min(98, wealthScore);
  const wealthMeta = getStatusMeta(wealthScore);

  const wealthHouseFromDasaLagna = ((wealthHouse11Sign - dasaLagnaSignIndex + 12) % 12) + 1;

  const wealthPrediction: LifeMilestonePrediction = {
    id: "wealth",
    domainNameEn: "Financial Prosperity & Wealth Manifestation",
    domainNameTa: "தன லாபம் & அஷ்ட லட்சுமி யோகம்",
    sanskritTermEn: "Dhana & Labha (2nd & 11th Bhavas)",
    sanskritTermTa: "தன & லாப பாவம் (2 & 11)",
    readinessScore: wealthScore,
    status: wealthMeta.status,
    statusBadgeEn: wealthMeta.badgeEn,
    statusBadgeTa: wealthMeta.badgeTa,
    keyHouses: [2, 11, 9, 5],
    primaryHouseLords: wealthLords,
    karakasInvolved: {
      parashari: "Jupiter & Venus",
      jaimini: "Arudha Pada 11 (A11)",
      charaRole: "AmK / Moon-Venus",
    },
    dasaBhuktiAlignment: {
      isAligned: wealthDasaActive,
      dasaLord: activeDasaLord,
      bukthiLord: activeBukthiLord,
      andharaLord: activeAndharaLord,
      descriptionEn: wealthDasaActive
        ? `Active period lords connect with 2nd Dhana (accumulation) and 11th Labha (cash flow) houses.`
        : `Dasa lords ensure steady monetary safety.`,
      descriptionTa: wealthDasaActive
        ? `நடப்பு தசா நாதர்கள் 2-ம் தன ஸ்தானம் மற்றும் 11-ம் லாப ஸ்தானத்துடன் இணைந்து நிதிப் பெருக்கத்தை தருகின்றனர்.`
        : `நிதி நிலைமை ஸ்திரமாக இருக்கும்.`,
    },
    doubleTransit: wealthDoubleTransit,
    dasaLagnaInsight: {
      dasaLagnaSignIndex,
      dasaLagnaSignEn: ZODIAC_NAMES_EN[dasaLagnaSignIndex],
      dasaLagnaSignTa: ZODIAC_NAMES_TA[dasaLagnaSignIndex],
      houseFromDasaLagna: wealthHouseFromDasaLagna,
      insightEn: `From Dasa Lagna, Labhasthana occupies house ${wealthHouseFromDasaLagna}, conferring multiple income streams and return on investments.`,
      insightTa: `தசா லக்னத்தில் இருந்து 11-ம் லாப பாவம் ${wealthHouseFromDasaLagna}-ல் அமைவது முதலீடுகளில் பெருத்த லாபத்தையும் கூடுதல் வருமான வழிகளையும் திறக்கிறது.`,
    },
    divisionalCheck: {
      vargaKey: "D-11",
      vargaNameEn: "D-11 Rudramsa / Labhamsa (Windfall Gains)",
      vargaNameTa: "D-11 ருத்ராம்சம் / லாபாம்சம் (திடீர் தன வரவு)",
      focalPointEn: "Marc Boney & V.P. Goel: D-11 evaluates sudden financial settlements, inheritances, litigation windfalls, and high-stakes financial windfalls.",
      focalPointTa: "மார்க் போனி & வி.பி. கோயல்: D-11 மூலம் திடீர் நிதி அதிர்ஷ்டம், பரம்பரை சொத்து மற்றும் பெரிய நிதி வரவுகள் கணிக்கப்படுகின்றன.",
    },
    classicalRulesCitedEn: [
      "Marc Boney Dhana Principle: 'Interconnection of 2nd/11th with 1st/5th/9th during benefic transits triggers immense capital accumulation.'",
      "Jaimini Sutra: 'Mutual aspect between Moon and Venus forms an unfailing royal dhana yoga.'",
    ],
    classicalRulesCitedTa: [
      "மார்க் போனி தன விதி: '2 மற்றும் 11-ம் அதிபதிகள் 1, 5, 9-ம் அதிபதிகளுடன் சேரும் காலத்தில் பெரும் செல்வ சேர்க்கை நிகழும்.'",
      "ஜைமினி சூத்திரம்: 'சந்திரனும் சுக்கிரனும் ஒருவரையொருவர் பார்க்கும் போது குறைவற்ற ராஜ தன யோகம் உண்டாகும்.'",
    ],
    predictiveGuidanceEn:
      "Favorable cycle for major investments, portfolio expansion, and recovering long-pending receivables. Practice prudent financial compounding.",
    predictiveGuidanceTa:
      "நீண்ட நாள் வரவுகள் வசூலாவதற்கும், புதிய முதலீடுகளை தொடங்குவதற்கும் இது ஏற்ற காலம். நிதிப் பெருக்கத்திற்கான கதவுகள் திறக்கின்றன.",
  };

  // =========================================================================
  // 4. MARRIAGE & SACRED UNION (7th, 1st; DK; Upapada Lagna; D-9)
  // =========================================================================
  const marriageLords = [getHouseLordName(7), getHouseLordName(1), getHouseLordName(2)];
  const marriageHouse7Sign = ((ascSign - 1 + 6) % 12) + 1;
  const marriageLord7Sign = getPlanetPlacementSign(marriageLords[0]);
  const marriageDoubleTransit = checkDoubleTransitOnTarget(
    marriageHouse7Sign,
    marriageLord7Sign,
    saturnDetail,
    jupiterDetail
  );

  const dkPlanet = charaKarakas.find((k) => k.role === "DK")?.planet || "Venus";
  const dkConnected = [activeDasaLord, activeBukthiLord].includes(dkPlanet);

  const marriageDasaActive =
    checkPeriodLordConnection(activeDasaLord, [7, 1, 2]) ||
    checkPeriodLordConnection(activeBukthiLord, [7, 1, 2]);

  let marriageScore = 54;
  if (marriageDasaActive) marriageScore += 18;
  if (marriageDoubleTransit.isFulfilled) marriageScore += 22;
  else if (marriageDoubleTransit.jupiterInfluences) marriageScore += 12;
  if (dkConnected) marriageScore += 10;
  marriageScore = Math.min(97, marriageScore);
  const marriageMeta = getStatusMeta(marriageScore);

  const marriageHouseFromDasaLagna = ((marriageHouse7Sign - dasaLagnaSignIndex + 12) % 12) + 1;

  const marriagePrediction: LifeMilestonePrediction = {
    id: "marriage",
    domainNameEn: "Marriage Timing & Sacred Union",
    domainNameTa: "திருமண பாக்கியம் & களத்திர யோகம்",
    sanskritTermEn: "Vivaha Yoga (7th Bhava & Upapada)",
    sanskritTermTa: "விவாஹ யோகம் (7-ம் பாவம் & உபபதம்)",
    readinessScore: marriageScore,
    status: marriageMeta.status,
    statusBadgeEn: marriageMeta.badgeEn,
    statusBadgeTa: marriageMeta.badgeTa,
    keyHouses: [7, 1, 2],
    primaryHouseLords: marriageLords,
    karakasInvolved: {
      parashari: "Venus (for men) / Jupiter (for women)",
      jaimini: dkPlanet,
      charaRole: "DK (Dara Karaka)",
    },
    dasaBhuktiAlignment: {
      isAligned: marriageDasaActive,
      dasaLord: activeDasaLord,
      bukthiLord: activeBukthiLord,
      andharaLord: activeAndharaLord,
      descriptionEn: marriageDasaActive
        ? `Running period lords strongly trigger the 7th Kalatra Bhava and Dara Karaka (${dkPlanet}).`
        : `Dasa lords support emotional equilibrium and relational bonding.`,
      descriptionTa: marriageDasaActive
        ? `நடப்பு தசா நாதர்கள் 7-ம் களத்திர ஸ்தானத்தையும் தார காரகனையும் (${dkPlanet}) விழிப்படையச் செய்கின்றனர்.`
        : `தசா நாதர்கள் உறவுகளில் அமைதியையும் இணக்கத்தையும் பேணுகின்றனர்.`,
    },
    doubleTransit: marriageDoubleTransit,
    dasaLagnaInsight: {
      dasaLagnaSignIndex,
      dasaLagnaSignEn: ZODIAC_NAMES_EN[dasaLagnaSignIndex],
      dasaLagnaSignTa: ZODIAC_NAMES_TA[dasaLagnaSignIndex],
      houseFromDasaLagna: marriageHouseFromDasaLagna,
      insightEn: `From Dasa Lagna, the 7th house of partnerships falls in ${marriageHouseFromDasaLagna}, synchronizing relationship commitment and family endorsement.`,
      insightTa: `தசா லக்னத்தில் இருந்து 7-ம் பாவம் ${marriageHouseFromDasaLagna}-ல் அமைவது திருமண பேச்சுவார்த்தைகளில் சுமூக முடிவையும் வரன் அமைதலையும் தருகிறது.`,
    },
    divisionalCheck: {
      vargaKey: "D-9",
      vargaNameEn: "D-9 Navamsa (Dharma & Spouse)",
      vargaNameTa: "D-9 நவாம்சம் (களத்திரம் & தர்மம்)",
      focalPointEn: "7th lord in D-9 and connection with Upapada Lagna (UL) fixes marital stability and partner's character.",
      focalPointTa: "D-9-ல் 7-ம் அதிபதி மற்றும் உபபத லக்னம் (UL) சேர்க்கை திருமண பந்தத்தின் ஆயுளையும் துணையின் குணநலன்களையும் உறுதி செய்கிறது.",
    },
    classicalRulesCitedEn: [
      "K.N. Rao Golden Rule: 'Marriage cannot manifest unless Saturn and Jupiter jointly aspect the 7th house, 7th lord, or Lagna.'",
      "Marc Boney Upapada Principle: 'Planets transiting or aspecting Upapada Lagna (UL) bring the destined soulmate into one's life.'",
    ],
    classicalRulesCitedTa: [
      "கே.என். ராவ் தார சூத்திரம்: 'சனி மற்றும் குரு ஆகிய இரு கிரகங்களும் 7-ம் பாவம் அல்லது அதிபதியைப் பார்க்காமல் விவாகம் கூடிவராது.'",
      "மார்க் போனி உபபத விதி: 'உபபத லக்னத்தை (UL) கோச்சார சுப கிரகங்கள் தொடும்போது விதிக்கப்பட்ட துணைவருடனான சந்திப்பு நடக்கும்.'",
    ],
    predictiveGuidanceEn:
      "Highly auspicious window for matrimonial alliances, engagement ceremonies, and marital deepening. Mutual understanding flourishes.",
    predictiveGuidanceTa:
      "திருமணப் பேச்சுக்கள் முடிவாவதற்கும், சுப விவாகம் இனிதே நடந்தேறுவதற்கும் உகந்த பொற்காலம். வாழ்க்கை துணையுடன் அன்யோன்யம் கூடும்.",
  };

  // =========================================================================
  // 5. CHILDBIRTH & PROGENY (5th, 9th; PK; Beeja/Kshetra Sphuta; D-7)
  // =========================================================================
  const childLords = [getHouseLordName(5), getHouseLordName(9), getHouseLordName(2)];
  const childHouse5Sign = ((ascSign - 1 + 4) % 12) + 1;
  const childLord5Sign = getPlanetPlacementSign(childLords[0]);
  const childDoubleTransit = checkDoubleTransitOnTarget(
    childHouse5Sign,
    childLord5Sign,
    saturnDetail,
    jupiterDetail
  );

  const childDasaActive =
    checkPeriodLordConnection(activeDasaLord, [5, 9, 2]) ||
    checkPeriodLordConnection(activeBukthiLord, [5, 9, 2]);

  let childScore = 52;
  if (childDasaActive) childScore += 18;
  if (childDoubleTransit.isFulfilled) childScore += 20;
  else if (childDoubleTransit.jupiterInfluences) childScore += 12;
  // Blend Beeja / Kshetra score
  const avgSphuta = Math.round((beejaKshetra.beejaSphuta.vitalityScore + beejaKshetra.kshetraSphuta.vitalityScore) / 2);
  if (avgSphuta >= 80) childScore += 10;
  childScore = Math.min(97, childScore);
  const childMeta = getStatusMeta(childScore);

  const childHouseFromDasaLagna = ((childHouse5Sign - dasaLagnaSignIndex + 12) % 12) + 1;

  const childPrediction: LifeMilestonePrediction = {
    id: "childbirth",
    domainNameEn: "Progeny Blessings & Childbirth",
    domainNameTa: "சந்தான பாக்கியம் & புத்திர யோகம்",
    sanskritTermEn: "Santana Bhava (5th Bhava & Saptamsa)",
    sanskritTermTa: "சந்தான பாவம் (5-ம் பாவம் & சப்தாம்சம்)",
    readinessScore: childScore,
    status: childMeta.status,
    statusBadgeEn: childMeta.badgeEn,
    statusBadgeTa: childMeta.badgeTa,
    keyHouses: [5, 9, 2],
    primaryHouseLords: childLords,
    karakasInvolved: {
      parashari: "Jupiter (Putrakaraka)",
      jaimini: pkPlanet,
      charaRole: "PK (Putra Karaka)",
    },
    dasaBhuktiAlignment: {
      isAligned: childDasaActive,
      dasaLord: activeDasaLord,
      bukthiLord: activeBukthiLord,
      andharaLord: activeAndharaLord,
      descriptionEn: childDasaActive
        ? `Running period lords activate 5th Purva Punya & Santana Bhava alongside Putra Karaka (${pkPlanet}).`
        : `Dasa periods support family peace and reproductive wellness.`,
      descriptionTa: childDasaActive
        ? `நடப்பு தசா-புக்தி 5-ம் பூர்வ புண்ணிய பாக்கியத்தையும் புத்ர காரகனையும் (${pkPlanet}) நற்பலன் தர வைக்கிறது.`
        : `குடும்பத்தில் நிம்மதியும் உடல் ஆரோக்கியமும் நிலவும்.`,
    },
    doubleTransit: childDoubleTransit,
    dasaLagnaInsight: {
      dasaLagnaSignIndex,
      dasaLagnaSignEn: ZODIAC_NAMES_EN[dasaLagnaSignIndex],
      dasaLagnaSignTa: ZODIAC_NAMES_TA[dasaLagnaSignIndex],
      houseFromDasaLagna: childHouseFromDasaLagna,
      insightEn: `From Dasa Lagna, 5th house of children falls in ${childHouseFromDasaLagna}, showing fertility readiness and familial happiness.`,
      insightTa: `தசா லக்னத்தில் இருந்து 5-ம் புத்திர பாவம் ${childHouseFromDasaLagna}-ல் அமைவது கருத்தரிப்பு வாய்ப்பையும் மழலைச் செல்வத்தையும் சுட்டுகிறது.`,
    },
    divisionalCheck: {
      vargaKey: "D-7",
      vargaNameEn: "D-7 Saptamsa (Children & Lineage)",
      vargaNameTa: "D-7 சப்தாம்சம் (சந்ததி & வம்ச விருத்தி)",
      focalPointEn: "5th house and lord in D-7 determine ease of conception, pregnancy health, and noble character of progeny.",
      focalPointTa: "D-7-ல் 5-ம் பாவம் மற்றும் அதிபதி சுகப்பிரசவம், கருத்தரிப்பு ஆரோக்கியம் மற்றும் குழந்தையின் நற்குணங்களை நிர்ணயிக்கின்றன.",
    },
    classicalRulesCitedEn: [
      "K.N. Rao Transit Axiom: 'Childbirth fructifies only when Saturn and Jupiter double transit energizes the 5th house, 5th lord, or 9th house.'",
      "Marc Boney Composite Rule: 'Cross-verifying Beeja Sphuta (seed) and Kshetra Sphuta (soil) resolves medical fertility timing.'",
    ],
    classicalRulesCitedTa: [
      "கே.என். ராவ் சந்தான சூத்திரம்: 'சனி மற்றும் குரு இருவரின் பார்வையும் 5-ம் பாவம் அல்லது 9-ம் பாவத்தின் மீது பதியும் போதே குழந்தை பிறக்கும்.'",
      "மார்க் போனி வித்து-நில விதி: 'பீஜ ஸ்புடம் (விதை) மற்றும் ஷேத்ர ஸ்புடம் (நிலம்) இரண்டையும் சரிபார்த்து புத்திர பாக்கியத்தை உறுதி செய்ய வேண்டும்.'",
    ],
    predictiveGuidanceEn:
      "Auspicious cycle for conception planning and maternal vitality. Continue positive health practices and offer prayers to Lord Subramanya.",
    predictiveGuidanceTa:
      "சந்தான பாக்கியம் கைகூடுவதற்கும், கருத்தரிப்பு முயற்சிகள் வெற்றி பெறுவதற்கும் நற்காலம். முருகப் பெருமான் மற்றும் சந்தான கோபால வழிபாடு நலம் பயக்கும்.",
  };

  // =========================================================================
  // 6. PROPERTY, REAL ESTATE & CONVEYANCE (4th; MK; Pada 4; D-4)
  // =========================================================================
  const propLords = [getHouseLordName(4), getHouseLordName(1)];
  const propHouse4Sign = ((ascSign - 1 + 3) % 12) + 1;
  const propLord4Sign = getPlanetPlacementSign(propLords[0]);
  const propDoubleTransit = checkDoubleTransitOnTarget(
    propHouse4Sign,
    propLord4Sign,
    saturnDetail,
    jupiterDetail
  );

  const mkPlanet = charaKarakas.find((k) => k.role === "MK")?.planet || "Mars";
  const mkConnected = [activeDasaLord, activeBukthiLord].includes(mkPlanet);

  const propDasaActive =
    checkPeriodLordConnection(activeDasaLord, [4, 1]) ||
    checkPeriodLordConnection(activeBukthiLord, [4, 1]);

  let propScore = 55;
  if (propDasaActive) propScore += 18;
  if (propDoubleTransit.isFulfilled) propScore += 20;
  else if (propDoubleTransit.saturnInfluences) propScore += 10;
  if (mkConnected) propScore += 8;
  propScore = Math.min(96, propScore);
  const propMeta = getStatusMeta(propScore);

  const propHouseFromDasaLagna = ((propHouse4Sign - dasaLagnaSignIndex + 12) % 12) + 1;

  const propPrediction: LifeMilestonePrediction = {
    id: "property",
    domainNameEn: "Real Estate, Home & Property Acquisition",
    domainNameTa: "பூமி, வீடு & சொத்து வாங்கும் யோகம்",
    sanskritTermEn: "Gruha & Vahana (4th Bhava & D-4)",
    sanskritTermTa: "கிருக & வாகன பாவம் (4-ம் பாவம் & D-4)",
    readinessScore: propScore,
    status: propMeta.status,
    statusBadgeEn: propMeta.badgeEn,
    statusBadgeTa: propMeta.badgeTa,
    keyHouses: [4, 1],
    primaryHouseLords: propLords,
    karakasInvolved: {
      parashari: "Mars (Land) & Venus (Vehicle)",
      jaimini: mkPlanet,
      charaRole: "MK (Matri Karaka)",
    },
    dasaBhuktiAlignment: {
      isAligned: propDasaActive,
      dasaLord: activeDasaLord,
      bukthiLord: activeBukthiLord,
      andharaLord: activeAndharaLord,
      descriptionEn: propDasaActive
        ? `Running period lords activate 4th Matri/Sukhasthana and Matri Karaka (${mkPlanet}).`
        : `Dasa lords maintain stability in existing residence and domestic comfort.`,
      descriptionTa: propDasaActive
        ? `நடப்பு தசா நாதர்கள் 4-ம் சுக/மாத்ரு ஸ்தானத்தையும் மாத்ரு காரகனையும் (${mkPlanet}) சொத்து சேர்க்கைக்கு தூண்டுகின்றனர்.`
        : `வசிப்பிடத்தில் நிம்மதியும் அமைதியும் தொடரும்.`,
    },
    doubleTransit: propDoubleTransit,
    dasaLagnaInsight: {
      dasaLagnaSignIndex,
      dasaLagnaSignEn: ZODIAC_NAMES_EN[dasaLagnaSignIndex],
      dasaLagnaSignTa: ZODIAC_NAMES_TA[dasaLagnaSignIndex],
      houseFromDasaLagna: propHouseFromDasaLagna,
      insightEn: `From Dasa Lagna, 4th house of property falls in ${propHouseFromDasaLagna}, favoring title deed acquisition and construction work.`,
      insightTa: `தசா லக்னத்தில் இருந்து 4-ம் மனை பாவம் ${propHouseFromDasaLagna}-ல் அமைவது புது வீடு வாங்குதல் அல்லது நிலம் பத்திரப் பதிவிற்கு மிகவும் சாதகமானது.`,
    },
    divisionalCheck: {
      vargaKey: "D-4",
      vargaNameEn: "D-4 Chaturthamsa (Fixed Assets)",
      vargaNameTa: "D-4 சதுர்த்தாம்சம் (நிலையான சொத்துக்கள்)",
      focalPointEn: "4th house and Mars/Venus in D-4 confirm enduring real estate equity and vehicle acquisitions.",
      focalPointTa: "D-4-ல் 4-ம் பாவம் மற்றும் செவ்வாய்/சுக்கிரன் பலம் சொந்த வீடு மற்றும் நவீன வாகன யோகத்தை உறுதி செய்கிறது.",
    },
    classicalRulesCitedEn: [
      "K.N. Rao Rule: 'Double transit of Saturn and Jupiter touching 4th house or 4th lord crystallizes physical home or property acquisition.'",
      "Marc Boney Pada 4 Law: 'Arudha Pada 4 (A4) activation in Chara Dasha manifests new real estate construction.'",
    ],
    classicalRulesCitedTa: [
      "கே.என். ராவ் மனை சூத்திரம்: 'சனி மற்றும் குருவின் பார்வை 4-ம் வீடு அல்லது அதன் அதிபதியை தொடும்போது பூமி, வீடு யோகம் கைக்கூடும்.'",
      "மார்க் போனி A4 விதி: '4-ம் பாதமான A4 சஞ்சாரத்தின் போது புதிய மனை வாங்குதல் மற்றும் கட்டிட வேலைகள் நடக்கும்.'",
    ],
    predictiveGuidanceEn:
      "Favorable time for finalizing property deeds, home renovation, or upgrading to a new luxury vehicle.",
    predictiveGuidanceTa:
      "சொத்து வாங்குவதற்கும், புதிய மனை பதிவு செய்வதற்கும், புதிய வாகனம் எடுப்பதற்கும் இது மிகவும் உகந்த காலம்.",
  };

  // =========================================================================
  // 7. FOREIGN SETTLEMENT & RELOCATION (12th, 9th, 4th affliction; Rahu)
  // =========================================================================
  const foreignLords = [getHouseLordName(12), getHouseLordName(9), getHouseLordName(4)];
  const foreignHouse12Sign = ((ascSign - 1 + 11) % 12) + 1;
  const foreignLord12Sign = getPlanetPlacementSign(foreignLords[0]);
  const foreignDoubleTransit = checkDoubleTransitOnTarget(
    foreignHouse12Sign,
    foreignLord12Sign,
    saturnDetail,
    jupiterDetail
  );

  const rahuPlanet = planets.find((p) => normalizePlanetName(p.name) === "Rahu");
  const rahuInMovableOrWater = rahuPlanet && [1, 4, 7, 10, 8, 12].includes(rahuPlanet.sign_index || 1);

  const foreignDasaActive =
    checkPeriodLordConnection(activeDasaLord, [12, 9, 8]) ||
    checkPeriodLordConnection(activeBukthiLord, [12, 9, 8]) ||
    [activeDasaLord, activeBukthiLord].includes("Rahu");

  let foreignScore = 50;
  if (foreignDasaActive) foreignScore += 18;
  if (foreignDoubleTransit.isFulfilled) foreignScore += 18;
  else if (foreignDoubleTransit.saturnInfluences || foreignDoubleTransit.jupiterInfluences) foreignScore += 10;
  if (rahuInMovableOrWater) foreignScore += 8;
  foreignScore = Math.min(95, foreignScore);
  const foreignMeta = getStatusMeta(foreignScore);

  const foreignHouseFromDasaLagna = ((foreignHouse12Sign - dasaLagnaSignIndex + 12) % 12) + 1;

  const foreignPrediction: LifeMilestonePrediction = {
    id: "foreign",
    domainNameEn: "Foreign Travel & International Settlement",
    domainNameTa: "வெளிநாட்டுப் பயணம் & குடியேறும் யோகம்",
    sanskritTermEn: "Videsha Gamana (12th & 9th Bhavas)",
    sanskritTermTa: "விதேச கமன யோகம் (12 & 9-ம் பாவம்)",
    readinessScore: foreignScore,
    status: foreignMeta.status,
    statusBadgeEn: foreignMeta.badgeEn,
    statusBadgeTa: foreignMeta.badgeTa,
    keyHouses: [12, 9, 8, 4],
    primaryHouseLords: foreignLords,
    karakasInvolved: {
      parashari: "Rahu (Mleccha Karaka) & Moon",
      jaimini: "Karakamsha 12th / 9th",
      charaRole: "Rahu / BK",
    },
    dasaBhuktiAlignment: {
      isAligned: foreignDasaActive,
      dasaLord: activeDasaLord,
      bukthiLord: activeBukthiLord,
      andharaLord: activeAndharaLord,
      descriptionEn: foreignDasaActive
        ? `Running period lords stimulate the 12th overseas house, 9th long journeys, and Rahu.`
        : `Dasa periods favor local stability with occasional recreational travel.`,
      descriptionTa: foreignDasaActive
        ? `நடப்பு தசா நாதர்கள் 12-ம் வெளிநாட்டு ஸ்தானத்தையும், 9-ம் தூரப் பயண பாக்கியத்தையும், ராகுவையும் தூண்டுகின்றனர்.`
        : `தற்போதைய நிலை உள்நாட்டு ஸ்திரத்தன்மையையும் சிறு பயணங்களையும் ஆதரிக்கிறது.`,
    },
    doubleTransit: foreignDoubleTransit,
    dasaLagnaInsight: {
      dasaLagnaSignIndex,
      dasaLagnaSignEn: ZODIAC_NAMES_EN[dasaLagnaSignIndex],
      dasaLagnaSignTa: ZODIAC_NAMES_TA[dasaLagnaSignIndex],
      houseFromDasaLagna: foreignHouseFromDasaLagna,
      insightEn: `From Dasa Lagna, the 12th house falls in ${foreignHouseFromDasaLagna}, clearing visa pathways and expatriate relocation.`,
      insightTa: `தசா லக்னத்தில் இருந்து 12-ம் பாவம் ${foreignHouseFromDasaLagna}-ல் அமைவது விசா அனுமதி, கடல் கடந்த வேலை மற்றும் வெளிநாட்டு குடியேற்றத்திற்கு வழிவகுக்கிறது.`,
    },
    divisionalCheck: {
      vargaKey: "D-4 / D-9",
      vargaNameEn: "D-4 & D-9 (Relocation & Residence)",
      vargaNameTa: "D-4 & D-9 (குடியேற்றம் & வசிப்பிடம்)",
      focalPointEn: "Marc Boney: Relocation abroad requires detachment from 4th house of motherland alongside active 12th house in D-4 and D-9.",
      focalPointTa: "மார்க் போனி ஆய்வு: வெளிநாட்டு வாழ்க்கை அமைய தாயகத்தைக் குறிக்கும் 4-ம் பாவம் விடுபட்டு 12-ம் பாவம் D-4 மற்றும் D-9-ல் செயல்பட வேண்டும்.",
    },
    classicalRulesCitedEn: [
      "K.N. Rao Relocation Rule: 'Foreign travel manifests when 9th and 12th houses are activated and Rahu casts its influence on period lords.'",
      "Marc Boney Axiom: 'Double transit on 12th house creates unavoidable cross-border travels and international assignments.'",
    ],
    classicalRulesCitedTa: [
      "கே.என். ராவ் வெளிநாட்டு சூத்திரம்: '9 மற்றும் 12-ம் வீடுகளுடன் ராகுவின் தாக்கம் தசா நாதர்களிடம் சேரும்போது வெளிநாட்டுப் பயணம் நிகழும்.'",
      "மார்க் போனி விதி: '12-ம் வீட்டின் மீது விழும் இரட்டைப் பெயர்ச்சிப் பார்வை கடல் தாண்டிய பயணங்களை தவிர்க்க முடியாததாக்கும்.'",
    ],
    predictiveGuidanceEn:
      "Strong momentum for visa processing, passport renewal, and overseas job interviews. Ensure documentation is prepared in advance.",
    predictiveGuidanceTa:
      "விசா விண்ணப்பங்கள், பாஸ்போர்ட் வேலைகள் மற்றும் வெளிநாட்டு வேலை முயற்சிகளுக்கு இது மிகவும் உகந்த நேரம். காரியங்கள் விரைந்து முடியும்.",
  };

  // =========================================================================
  // 8. SPIRITUAL INITIATION & GURU (9th, 5th, 8th, 12th; Ketu; Virinchi)
  // =========================================================================
  const spirLords = [getHouseLordName(9), getHouseLordName(5), getHouseLordName(8), getHouseLordName(12)];
  const spirHouse9Sign = ((ascSign - 1 + 8) % 12) + 1;
  const spirLord9Sign = getPlanetPlacementSign(spirLords[0]);
  const spirDoubleTransit = checkDoubleTransitOnTarget(
    spirHouse9Sign,
    spirLord9Sign,
    saturnDetail,
    jupiterDetail
  );

  const spirDasaActive =
    checkPeriodLordConnection(activeDasaLord, [9, 5, 8, 12]) ||
    checkPeriodLordConnection(activeBukthiLord, [9, 5, 8, 12]) ||
    [activeDasaLord, activeBukthiLord].includes("Ketu") ||
    [activeDasaLord, activeBukthiLord].includes("Jupiter");

  let spirScore = 58;
  if (spirDasaActive) spirScore += 18;
  if (spirDoubleTransit.isFulfilled) spirScore += 18;
  else if (spirDoubleTransit.jupiterInfluences) spirScore += 10;
  if (specialYogas.virinchiYoga.present) spirScore += 10;
  spirScore = Math.min(98, spirScore);
  const spirMeta = getStatusMeta(spirScore);

  const spirHouseFromDasaLagna = ((spirHouse9Sign - dasaLagnaSignIndex + 12) % 12) + 1;

  const spirPrediction: LifeMilestonePrediction = {
    id: "spirituality",
    domainNameEn: "Spiritual Initiation, Guru & Deeper Wisdom",
    domainNameTa: "குரு அருள், தீட்சை & ஞான யோகம்",
    sanskritTermEn: "Dharma & Moksha (9th, 5th & 12th Bhavas)",
    sanskritTermTa: "தர்ம & மோட்ச பாவம் (9, 5 & 12)",
    readinessScore: spirScore,
    status: spirMeta.status,
    statusBadgeEn: spirMeta.badgeEn,
    statusBadgeTa: spirMeta.badgeTa,
    keyHouses: [9, 5, 8, 12],
    primaryHouseLords: spirLords,
    karakasInvolved: {
      parashari: "Jupiter (Guru) & Ketu (Moksha)",
      jaimini: "Atma Karaka (AK)",
      charaRole: "AK (Atma Karaka)",
    },
    dasaBhuktiAlignment: {
      isAligned: spirDasaActive,
      dasaLord: activeDasaLord,
      bukthiLord: activeBukthiLord,
      andharaLord: activeAndharaLord,
      descriptionEn: spirDasaActive
        ? `Running period lords awaken 9th Guru sthana, 5th Mantra Purva Punya, and Atma Karaka.`
        : `Dasa periods nurture ethical living and inner introspection.`,
      descriptionTa: spirDasaActive
        ? `நடப்பு தசா நாதர்கள் 9-ம் குரு பாக்கியத்தையும், 5-ம் மந்திர சித்தியையும், ஆத்ம காரகனையும் விழிப்படையச் செய்கின்றனர்.`
        : `மனதில் தர்ம சிந்தனையும் ஆன்மீக நாட்டமும் இயல்பாக வளரும்.`,
    },
    doubleTransit: spirDoubleTransit,
    dasaLagnaInsight: {
      dasaLagnaSignIndex,
      dasaLagnaSignEn: ZODIAC_NAMES_EN[dasaLagnaSignIndex],
      dasaLagnaSignTa: ZODIAC_NAMES_TA[dasaLagnaSignIndex],
      houseFromDasaLagna: spirHouseFromDasaLagna,
      insightEn: `From Dasa Lagna, the 9th Dharmasthana falls in ${spirHouseFromDasaLagna}, drawing authentic mentors, mantra deeksha, and temple pilgrimages.`,
      insightTa: `தசா லக்னத்தில் இருந்து 9-ம் தர்ம பாவம் ${spirHouseFromDasaLagna}-ல் அமைவது உத்தம குருவின் ஆசி, மந்திர உபதேசம் மற்றும் திருத்தல யாத்திரைகளை வழங்கும்.`,
    },
    divisionalCheck: {
      vargaKey: "D-9 / D-20",
      vargaNameEn: "D-9 & D-20 Vimsamsa (Spiritual Attainment)",
      vargaNameTa: "D-9 & D-20 விம்சாம்சம் (ஆன்மீக சித்தி)",
      focalPointEn: "9th and 12th houses in D-20 denote sadhana depth, ishta devata alignment, and spontaneous meditation states.",
      focalPointTa: "D-20-ல் 9 மற்றும் 12-ம் பாவங்கள் இஷ்ட தெய்வ அருள், தியான சித்தி மற்றும் ஆன்மீக முக்தியை குறிக்கின்றன.",
    },
    classicalRulesCitedEn: [
      "Marc Boney Guru Rule: 'Meeting an authentic spiritual master occurs during Vimshottari periods of 9th lord or Jupiter with double transit on 9th.'",
      "K.N. Rao Virinchi Principle: 'Ketu and Jupiter in trinal sambandha unlock past-life sadhana and spontaneous inner awakening.'",
    ],
    classicalRulesCitedTa: [
      "மார்க் போனி குரு சூத்திரம்: '9-ம் அதிபதி அல்லது குருவின் தசா காலத்தில் 9-ம் பாவத்தில் இரட்டைப் பெயர்ச்சி நிகழும்போது உண்மையான சத்குரு அமைவார்.'",
      "கே.என். ராவ் விரிஞ்சி விதி: 'கேது மற்றும் குரு திரிகோண தொடர்பு பெறும்போது பூர்வ ஜென்ம தவ வலிமை வெளிப்பட்டு ஞானம் பிறக்கும்.'",
    ],
    predictiveGuidanceEn:
      "Profound time for receiving Mantra Deeksha, holy river pilgrimages, and establishing regular daily meditation practice.",
    predictiveGuidanceTa:
      "மந்திர தீட்சை பெறுவதற்கும், புண்ணிய ஸ்தலங்களுக்கு செல்வதற்கும், ஆழ்ந்த தியான பயிற்சியை தொடங்குவதற்கும் இது உன்னதமான அருள் காலம்.",
  };

  const milestones: LifeMilestonePrediction[] = [
    careerPrediction,
    wealthPrediction,
    marriagePrediction,
    childPrediction,
    eduPrediction,
    propPrediction,
    foreignPrediction,
    spirPrediction,
  ];

  return {
    calculatedAt: new Date().toISOString(),
    activeDasaLord,
    activeBukthiLord,
    activeAndharaLord,
    dasaLagnaSignIndex,
    dasaLagnaSignNameEn: ZODIAC_NAMES_EN[dasaLagnaSignIndex],
    dasaLagnaSignNameTa: ZODIAC_NAMES_TA[dasaLagnaSignIndex],
    karakamshaSignIndex,
    karakamshaSignNameEn: ZODIAC_NAMES_EN[karakamshaSignIndex],
    karakamshaSignNameTa: ZODIAC_NAMES_TA[karakamshaSignIndex],
    charaKarakas,
    beejaKshetra,
    specialYogas,
    saturnTransitDetail: saturnDetail,
    jupiterTransitDetail: jupiterDetail,
    milestones,
    marcBoneyCoreQuoteEn:
      "Marc Boney Axiom (dedicated to K.N. Rao): 'No major life event manifests unless Vimshottari Dasa promises it, Dasa Lagna reinforces it, and transiting Saturn and Jupiter jointly sanction it.'",
    marcBoneyCoreQuoteTa:
      "மார்க் போனி & கே.என். ராவ் பொன்மொழி: 'விம்சForms தசா நாதன் அனுமதித்து, தசா லக்னம் உறுதி செய்து, கோச்சார சனி மற்றும் குரு பகவான்கள் ஒருமித்து அங்கீகரிக்கும் போதே எந்த ஒரு முக்கிய வாழ்க்கை நிகழ்வும் பௌதீகமாக நிகழ்கிறது.'",
  };
}
