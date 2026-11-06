/**
 * Brighu Naadi Sangraha & Bhrigu Nandi Nadi Client-Side Evaluator
 *
 * Classical Authorities:
 * 1. "Brighu Naadi Sangraha: (Pearls of Brighu Naadi)" by Dr. N. Srinivasan Shastry (Sagar Publications).
 * 2. "A Study of the Basic Rules in Bhrigu Nandi Nadi" by A. Jagadeesan & Dr. K. Jothimani
 *    (School of Vedic Astrology, Vels University / VISTAS, Chennai - IJCRME 2022).
 *    Synthesizing Mr. R. G. Rao's foundational 20 Golden Rules.
 */

import {
  PlanetInfo,
  AscendantInfo,
  BrighuNaadiResponse,
  BrighuBirthEnvironment,
  BrighuJeevaKaraka,
  BrighuKarmaKaraka,
  BrighuTimingMilestone,
  BrighuPhysicalMarker,
  BrighuNaadiRuleMatch,
  BnnRuleEvaluation,
} from "./types";

const SIGN_NAMES_EN = [
  "Aries", "Taurus", "Gemini", "Cancer",
  "Leo", "Virgo", "Libra", "Scorpio",
  "Sagittarius", "Capricorn", "Aquarius", "Pisces"
];

const SIGN_NAMES_TA = [
  "மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்",
  "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்",
  "தனுசு", "மகரம்", "கும்பம்", "மீனம்"
];

const DOOR_FACING_MAP: Record<number, { en: string; ta: string }> = {
  1: { en: "East (Fire Sign: Aries)", ta: "கிழக்கு (நெருப்பு ராசி: மேஷம்)" },
  2: { en: "South (Earth Sign: Taurus)", ta: "தெற்கு (நில ராசி: ரிஷபம்)" },
  3: { en: "West (Air Sign: Gemini)", ta: "மேற்கு (காற்று ராசி: மிதுனம்)" },
  4: { en: "North (Water Sign: Cancer)", ta: "வடக்கு (நீர் ராசி: கடகம்)" },
  5: { en: "East (Fire Sign: Leo)", ta: "கிழக்கு (நெருப்பு ராசி: சிம்மம்)" },
  6: { en: "South (Earth Sign: Virgo)", ta: "தெற்கு (நில ராசி: கன்னி)" },
  7: { en: "West (Air Sign: Libra)", ta: "மேற்கு (காற்று ராசி: துலாம்)" },
  8: { en: "North (Water Sign: Scorpio)", ta: "வடக்கு (நீர் ராசி: விருச்சிகம்)" },
  9: { en: "East (Fire Sign: Sagittarius)", ta: "கிழக்கு (நெருப்பு ராசி: தனுசு)" },
  10: { en: "South (Earth Sign: Capricorn)", ta: "தெற்கு (நில ராசி: மகரம்)" },
  11: { en: "West (Air Sign: Aquarius)", ta: "மேற்கு (காற்று ராசி: கும்பம்)" },
  12: { en: "North (Water Sign: Pisces)", ta: "வடக்கு (நீர் ராசி: மீனம்)" },
};

const CITY_SECTOR_MAP: Record<number, { en: string; ta: string }> = {
  1: { en: "Western / North-Western part of city", ta: "ஊரின் மேற்கு / வடமேற்கு பகுதி" },
  2: { en: "Southern / South-Eastern part of city", ta: "ஊரின் தெற்கு / தென்கிழக்கு பகுதி" },
  3: { en: "South-Western / Central part of city", ta: "ஊரின் தென்மேற்கு / மத்திய பகுதி" },
  4: { en: "Northern / North-Eastern part of city", ta: "ஊரின் வடக்கு / வடகிழக்கு பகுதி" },
  5: { en: "Eastern part of city", ta: "ஊரின் கிழக்கு பகுதி" },
  6: { en: "South / South-Western part of city", ta: "ஊரின் தெற்கு / தென்மேற்கு பகுதி" },
  7: { en: "Western part of city", ta: "ஊரின் மேற்கு பகுதி" },
  8: { en: "Northern part of city", ta: "ஊரின் வடக்கு பகுதி" },
  9: { en: "Eastern / North-Eastern part of city", ta: "ஊரின் கிழக்கு / வடகிழக்கு பகுதி" },
  10: { en: "Southern part of city", ta: "ஊரின் தெற்கு பகுதி" },
  11: { en: "Western / North-Western part of city", ta: "ஊரின் மேற்கு / வடமேற்கு பகுதி" },
  12: { en: "Northern / North-Eastern part of city", ta: "ஊரின் வடக்கு / வடகிழக்கு பகுதி" },
};

const SUN_TEMPLE_MAP: Record<number, { en: string; ta: string }> = {
  1: { en: "Hanuman or Fierce Durga Temple", ta: "ஆஞ்சநேயர் அல்லது உக்கிர துர்க்கை ஆலயம்" },
  2: { en: "Lakshmi / Annapoorneshwari Temple", ta: "மகாலட்சுமி / அன்னபூரணி ஆலயம்" },
  3: { en: "Maha Vishnu / Krishna Temple", ta: "மகாவிஷ்ணு / கிருஷ்ணர் ஆலயம்" },
  4: { en: "Snake God / Subrahmanya Temple", ta: "நாகர் / சுப்பிரமணியர் ஆலயம்" },
  5: { en: "Shiva / Rudra Temple", ta: "சிவபெருமான் / ருத்ரர் ஆலயம்" },
  6: { en: "Lakshmi Narayana / Venkateshwara Temple", ta: "லட்சுமி நாராயணர் / வெங்கடேஸ்வரர் ஆலயம்" },
  7: { en: "Kanyakaparameshwari / Mariamman Temple", ta: "கன்னிகா பரமேஸ்வரி / மாரியம்மன் ஆலயம்" },
  8: { en: "Kali / Shakthi Temple", ta: "காளி / சக்தி ஆலயம்" },
  9: { en: "Ganesha / Dattatreya / Shirdi Sai Baba", ta: "விநாயகர் / தத்தாத்ரேயர் / சீரடி சாயிபாபா ஆலயம்" },
  10: { en: "Kala Bhairava / Dharma Sastha Temple", ta: "கால பைரவர் / தர்ம சாஸ்தா ஆலயம்" },
  11: { en: "Sacred Water Tank / Temple Well / River Shrine", ta: "தீர்த்தக் குளம் / நதிக்கரை ஆலயம்" },
  12: { en: "Rishi Ashram, Shiva Samadhi or Secluded Hermitage", ta: "ரிஷி ஆசிரமம் / சிவ சமாதி அல்லது அமைதியான தியான பீடம்" },
};

const SPOUSE_DIRECTION_MAP: Record<number, { en: string; ta: string }> = {
  1: { en: "East", ta: "கிழக்கு" },
  2: { en: "South", ta: "தெற்கு" },
  3: { en: "West", ta: "மேற்கு" },
  4: { en: "North", ta: "வடக்கு" },
  5: { en: "East", ta: "கிழக்கு" },
  6: { en: "South", ta: "தெற்கு" },
  7: { en: "West", ta: "மேற்கு" },
  8: { en: "North", ta: "வடக்கு" },
  9: { en: "East", ta: "கிழக்கு" },
  10: { en: "South", ta: "தெற்கு" },
  11: { en: "West", ta: "மேற்கு" },
  12: { en: "North", ta: "வடக்கு" },
};

const BNN_SATURN_SIGN_CAREERS_MAP: Record<number, { en: string; ta: string }> = {
  1: {
    en: "Machinery, mechanical engineering, uniformed services, military defense, and police departments.",
    ta: "எந்திரவியல், மெக்கானிக்கல் பணிகள், பொறியியல் துறை, சீருடைப் பணியாளர்கள், ராணுவம் மற்றும் காவல்துறை.",
  },
  2: {
    en: "Monetary business, automotive industry, banking, treasury, computer software, and digital technology.",
    ta: "நிதித்துறை, வாகன தொழில், வங்கித்துறை, கருவூலம், கணினி மென்பொருள் தொழினுட்பம்.",
  },
  3: {
    en: "Intellectual practice, writing, journalism, speech, mass communication, sports, commercial brokerage, and publishing.",
    ta: "புத்திபூர்வமான பணிகள், எழுத்து, பத்திரிகை, மக்கள் தொடர்பு, விளையாட்டு, வர்த்தக புரோக்கரேஜ் மற்றும் பதிப்பகம்.",
  },
  4: {
    en: "Hostel management, nursing, healthcare services, dairy, water industries, astrology, clerk, groceries, and agriculture.",
    ta: "விடுதி நிர்வாகம், நர்சிங், நல்வாழ்வு பணி, பால்பண்ணை, குடிநீர் வர்த்தகம், ஜோதிடம், எழுத்தர் பணி, மளிகை மற்றும் விவசாயம்.",
  },
  5: {
    en: "Government service, public administrative authority, medical professions, fine arts, electronics, and executive leadership.",
    ta: "அரசுப் பணி, பொது நிர்வாக அதிகாரம், மருத்துவத்துறை, நுண்கலை, மின்னணுவியல் மற்றும் அதிகாரப் பொறுப்புகள்.",
  },
  6: {
    en: "Highly lucrative commerce, stock market, real estate, brokerage, agro-based industries, building materials, and crop farming.",
    ta: "அதிக லாபகரமான வர்த்தகம், பங்குச் சந்தை, ரியல் எஸ்டேட், புரோக்கரேஜ், விவசாய சார் தொழில்கள் மற்றும் கட்டுமானப் பொருட்கள்.",
  },
  7: {
    en: "Exalted Saturn: Legal luminary, judge, legal counsel, luxury garments, interior decoration, engineering, fashion, and automobiles.",
    ta: "சனி உச்சம்: வழக்கறிஞர், நீதிபதி, ஆடை ஆபரணங்கள், உள் அலங்காரம், பொறியியல் துறை, பேஷன் டிசைனிங் மற்றும் சொகுசு வாகனத் தொழில்.",
  },
  8: {
    en: "Heavy machinery, metallurgical engineering, land management, elemental discovery, mineral research, astrology, and occult.",
    ta: "கனரக எந்திரங்கள், உலோகப் பொறியியல், நில மேலாண்மை, தாதுப் பொருட்கள் ஆராய்ச்சி, ஜோதிடம் மற்றும் மறைபொருள் சாஸ்திரங்கள்.",
  },
  9: {
    en: "Honorable legal profession, professorship, teachers, banking management, government treasury, law, and accounting.",
    ta: "கௌரவமிக்க சட்டத்துறை, பேராசிரியர், ஆசிரியர் பணி, வங்கி மேலாளர், அரசு கருவூலம், நீதித்துறை மற்றும் கணக்கியல்.",
  },
  10: {
    en: "Fertilizer industry, oil commerce, mining, restaurants, food enterprises, technological machinery, agriculture, and water management.",
    ta: "உரத் தொழில், எண்ணெய் வர்த்தகம், சுரங்கம், உணவகம், உணவுப் பொருட்கள், நவீன எந்திரவியல், விவசாயம் மற்றும் நீர் மேலாண்மை.",
  },
  11: {
    en: "Astrology, spirituality, higher teaching, psychology, scientific research, executive management, aviation, and defense.",
    ta: "ஜோதிடம், ஆன்மீகம், உயர் கல்வி, உளவியல், அறிவியல் ஆராய்ச்சி, நிர்வாகப் பொறுப்பு, விமானத்துறை மற்றும் பாதுகாப்பு துறை.",
  },
  12: {
    en: "Law, medicine, history, religion, asceticism, priesthood, banking, judiciary, philosophy, charitable trusts, and high prestige.",
    ta: "சட்டம், மருத்துவம், வரலாறு, மதம், துறவறம், ஆலயப் பணிகள், வங்கித்துறை, நீதித்துறை, தத்துவம், அறக்கட்டளைகள் மற்றும் உயரிய சமூக அந்தஸ்து.",
  },
};

function normalizePlanetName(name: string): string {
  const n = name.trim().toLowerCase();
  if (n.startsWith("sun") || n === "சூரியன்") return "Sun";
  if (n.startsWith("moon") || n === "சந்திரன்") return "Moon";
  if (n.startsWith("mar") || n === "செவ்வாய்") return "Mars";
  if (n.startsWith("mer") || n === "புதன்") return "Mercury";
  if (n.startsWith("jup") || n === "குரு") return "Jupiter";
  if (n.startsWith("ven") || n === "சுக்கிரன்") return "Venus";
  if (n.startsWith("sat") || n === "சனி") return "Saturn";
  if (n.startsWith("rah") || n === "ராகு") return "Rahu";
  if (n.startsWith("ket") || n === "கேது") return "Ketu";
  return name;
}

export function evaluateBrighuNaadiClient(
  planets: PlanetInfo[],
  ascendant?: AscendantInfo,
  gender: string = "male"
): BrighuNaadiResponse {
  const planetMap: Record<string, PlanetInfo> = {};
  for (const p of planets) {
    planetMap[normalizePlanetName(p.name)] = p;
  }

  const lagnaIdx = ascendant ? ascendant.sign_index : 1;
  const jup = planetMap["Jupiter"];
  const sat = planetMap["Saturn"];
  const rahu = planetMap["Rahu"];
  const ketu = planetMap["Ketu"];
  const sun = planetMap["Sun"];
  const mars = planetMap["Mars"];
  const venus = planetMap["Venus"];

  const jupSignIdx = jup ? jup.sign_index : 1;
  const satSignIdx = sat ? sat.sign_index : 10;
  const rahuSignIdx = rahu ? rahu.sign_index : 1;
  const ketuSignIdx = ketu ? ketu.sign_index : 7;
  const sunSignIdx = sun ? sun.sign_index : 1;

  // 1. Birth Environment
  const isOddRahu = rahuSignIdx % 2 !== 0;
  const roadDir = isOddRahu
    ? { en: "East to West (Rahu in odd sign)", ta: "கிழக்கு - மேற்கு (ராகு ஒற்றை ராசியில் உள்ளதால்)" }
    : { en: "South to North (Rahu in even sign)", ta: "தெற்கு - வடக்கு (ராகு இரட்டை ராசியில் உள்ளதால்)" };

  const doorFacing = DOOR_FACING_MAP[rahuSignIdx] || { en: "East", ta: "கிழக்கு" };
  const citySector = CITY_SECTOR_MAP[rahuSignIdx] || { en: "Central area", ta: "மத்திய பகுதி" };
  const templeNear = SUN_TEMPLE_MAP[sunSignIdx] || { en: "Ancient Shiva/Vishnu Temple", ta: "பழமையான சிவன்/விஷ்ணு ஆலயம்" };

  const spousePlanet = gender.toLowerCase() === "female" ? mars : venus;
  const spouseSignIdx = spousePlanet ? spousePlanet.sign_index : 7;
  const spouseDir = SPOUSE_DIRECTION_MAP[spouseSignIdx] || { en: "East", ta: "கிழக்கு" };

  const birthEnv: BrighuBirthEnvironment = {
    road_direction_en: roadDir.en,
    road_direction_ta: roadDir.ta,
    door_facing_en: doorFacing.en,
    door_facing_ta: doorFacing.ta,
    city_sector_en: citySector.en,
    city_sector_ta: citySector.ta,
    temple_near_birth_en: templeNear.en,
    temple_near_birth_ta: templeNear.ta,
    spouse_direction_en: `${spouseDir.en} direction (${spousePlanet?.name || "Venus"} in ${SIGN_NAMES_EN[spouseSignIdx - 1]})`,
    spouse_direction_ta: `${spouseDir.ta} திசை (${spousePlanet?.name || "Venus"} ${SIGN_NAMES_TA[spouseSignIdx - 1]} ராசியில்)`,
    rahu_sign: SIGN_NAMES_EN[rahuSignIdx - 1],
    ketu_sign: SIGN_NAMES_EN[ketuSignIdx - 1],
    sun_sign: SIGN_NAMES_EN[sunSignIdx - 1],
  };

  // 2. Jeeva Karaka: Jupiter for male, Venus for female per BNN Rule (R. G. Rao)
  const isFemale = gender.toLowerCase() === "female";
  const primaryJeevaPlanet = isFemale ? "Venus" : "Jupiter";

  const jupHouseFromLagna = ((jupSignIdx - lagnaIdx + 12) % 12) + 1;
  const prosperityAfter41 = [3, 9, 12].includes(jupSignIdx); // Gemini, Sagittarius, Pisces

  const bhavasFromJupiter: Record<number, string[]> = {};
  for (let b = 1; b <= 12; b++) {
    bhavasFromJupiter[b] = [];
  }
  for (const [pName, pInfo] of Object.entries(planetMap)) {
    const bhava = ((pInfo.sign_index - jupSignIdx + 12) % 12) + 1;
    bhavasFromJupiter[bhava].push(pName);
  }

  const adjacentCounts = [
    bhavasFromJupiter[2].length,
    bhavasFromJupiter[3].length,
    bhavasFromJupiter[4].length,
    bhavasFromJupiter[5].length,
  ];
  const emptyAdjacent = adjacentCounts.every(c => c === 0);

  const jeeva: BrighuJeevaKaraka = {
    sign: SIGN_NAMES_EN[jupSignIdx - 1],
    sign_ta: SIGN_NAMES_TA[jupSignIdx - 1],
    house_from_lagna: jupHouseFromLagna,
    lifestyle_profile_en: `Jeeva Karaka in ${SIGN_NAMES_EN[jupSignIdx - 1]} shapes a conscious soul seeking wisdom, moral righteousness, and community standing.`,
    lifestyle_profile_ta: `ஜீவ காரகரான குரு ${SIGN_NAMES_TA[jupSignIdx - 1]} ராசியில் அமர்ந்து ஞானமும் தர்ம சிந்தனையும் சமுதாய நன்மதிப்பும் கொண்ட வாழ்க்கை முறையை அளிக்கிறார்.`,
    prosperity_after_41: prosperityAfter41,
    planets_in_bhavas_from_jupiter: bhavasFromJupiter,
    empty_adjacent_misery_check: emptyAdjacent,
    primary_karaka_planet: primaryJeevaPlanet,
    gender_applied: gender.toLowerCase(),
  };

  // 3. Karma Karaka (Saturn)
  const satHouseFromLagna = ((satSignIdx - lagnaIdx + 12) % 12) + 1;
  const satConjuncts: string[] = [];
  for (const [pName, pInfo] of Object.entries(planetMap)) {
    if (pName !== "Saturn" && pInfo.sign_index === satSignIdx) {
      satConjuncts.push(pName);
    }
  }

  // Direction of Saturn & Directional Trines (Rule 1 & Rule 2)
  let satDir = "East (Fire)";
  let satDirSigns = [1, 5, 9];
  if ([2, 6, 10].includes(satSignIdx)) {
    satDir = "South (Earth)";
    satDirSigns = [2, 6, 10];
  } else if ([3, 7, 11].includes(satSignIdx)) {
    satDir = "West (Air)";
    satDirSigns = [3, 7, 11];
  } else if ([4, 8, 12].includes(satSignIdx)) {
    satDir = "North (Water)";
    satDirSigns = [4, 8, 12];
  }

  const satSameDir: string[] = [];
  const satOppPlanets: string[] = [];
  const sat2ndPlanets: string[] = [];
  const sat12thPlanets: string[] = [];

  const oppSignIdx = ((satSignIdx + 6 - 1) % 12) + 1;
  const sat2ndSignIdx = (satSignIdx % 12) + 1;
  const sat12thSignIdx = ((satSignIdx - 2 + 12) % 12) + 1;

  for (const [pName, pInfo] of Object.entries(planetMap)) {
    if (pName === "Saturn") continue;
    if (satDirSigns.includes(pInfo.sign_index)) satSameDir.push(pName);
    if (pInfo.sign_index === oppSignIdx) satOppPlanets.push(pName);
    if (pInfo.sign_index === sat2ndSignIdx) sat2ndPlanets.push(pName);
    if (pInfo.sign_index === sat12thSignIdx) sat12thPlanets.push(pName);
  }

  const satSignCareerInfo = BNN_SATURN_SIGN_CAREERS_MAP[satSignIdx] || { en: "Industry & Commerce", ta: "தொழில் மற்றும் வர்த்தகம்" };

  const careerFieldsEn: string[] = [];
  const careerFieldsTa: string[] = [];

  const combinedInfluences = new Set([...satConjuncts, ...satSameDir]);

  if (combinedInfluences.has("Jupiter")) {
    careerFieldsEn.push("Advisory / Consultancy", "Teaching & Academia", "Law & Judiciary", "Management");
    careerFieldsTa.push("ஆலோசனை / வழிகாட்டல்", "ஆசிரியர் / கல்வித்துறை", "சட்டம் மற்றும் நீதித்துறை", "நிர்வாகப் பொறுப்புகள்");
  }
  if (combinedInfluences.has("Sun")) {
    careerFieldsEn.push("Government Liaison", "Public Administration", "Political Advisory");
    careerFieldsTa.push("அரசுத் துறை", "பொது நிர்வாகம்", "அரசியல் தொடர்பு");
  }
  if (combinedInfluences.has("Moon")) {
    careerFieldsEn.push("Liquid Commerce / Shipping", "Hospitality & Food Services", "Nursing & Healthcare");
    careerFieldsTa.push("திரவ வர்த்தகம் / கப்பல் போக்குவரத்து", "உணவகம் மற்றும் விருந்தோம்பல்", "நர்சிங் மற்றும் நல்வாழ்வு பணி");
  }
  if (combinedInfluences.has("Mars")) {
    careerFieldsEn.push("Mechanical Engineering", "Industrial Construction", "Defense & Police", "Surgery");
    careerFieldsTa.push("எந்திரவியல் பொறியியல்", "தொழிலகக் கட்டுமானம்", "காவல் / ராணுவம்", "அறுவை சிகிச்சை");
  }
  if (combinedInfluences.has("Mercury")) {
    careerFieldsEn.push("Auditing & Accounts", "Commercial Trade", "Publishing & Media", "Agencies");
    careerFieldsTa.push("கணக்கியல் மற்றும் தணிக்கை", "வணிக வர்த்தகம்", "பத்திரிகை மற்றும் ஊடகம்", "ஏஜென்சி தொழில்");
  }
  if (combinedInfluences.has("Venus")) {
    careerFieldsEn.push("Finance & Banking", "Luxury Vehicles", "Art & Design", "Cosmetics & Fashion");
    careerFieldsTa.push("வங்கி நிதித்துறை", "வாகன வர்த்தகம்", "கலை மற்றும் அலங்காரம்", "ஜவுளி மற்றும் பேஷன்");
  }
  if (combinedInfluences.has("Rahu")) {
    careerFieldsEn.push("Computer Science & AI", "Aviation", "Chemicals & Pharma", "Foreign Multinationals");
    careerFieldsTa.push("மென்பொருள் மற்றும் ஏஐ", "விமானத்துறை", "ரசாயனம் மற்றும் மருந்தகம்", "பன்னாட்டு நிறுவனங்கள்");
  }
  if (combinedInfluences.has("Ketu")) {
    careerFieldsEn.push("Legal Practice", "Spiritual Counseling", "Textile Weaving", "Diagnostics & Research");
    careerFieldsTa.push("வழக்கறிஞர் பணி", "ஆன்மீக வழிகாட்டல்", "நெசவுத் தொழில்", "ஆய்வக பரிசோதனை");
  }
  if (careerFieldsEn.length === 0) {
    careerFieldsEn.push("Independent Industry / Service", "Organizational Management");
    careerFieldsTa.push("சுயதொழில் மற்றும் சேவைப்பணி", "நிறுவன நிர்வாகம்");
  }

  let careerStartAge: number | null = null;
  const signsSatToRahu = ((rahuSignIdx - satSignIdx + 12) % 12);
  if (signsSatToRahu > 0) {
    careerStartAge = Math.min(Math.max(Math.round(signsSatToRahu * 2.5 * 10) / 10, 18), 35);
  }

  const isSatRetrograde = sat?.is_retrograde || false;
  let satRetroBehindEn: string | null = null;
  let satRetroBehindTa: string | null = null;
  if (isSatRetrograde) {
    satRetroBehindEn = `Saturn is retrograde, casting backward energy vector toward ${SIGN_NAMES_EN[sat12thSignIdx - 1]} (12th from Saturn). Planets: ${sat12thPlanets.join(", ") || "Empty"}.`;
    satRetroBehindTa = `சனி பகவான் வக்ரம் பெற்று தனது 12-ஆம் வீடான ${SIGN_NAMES_TA[sat12thSignIdx - 1]} ராசியை நோக்கி பின்னோக்கிப் பலன் தருகிறார். கிரகங்கள்: ${sat12thPlanets.join(", ") || "எதுவுமில்லை"}.`;
  }

  const karma: BrighuKarmaKaraka = {
    sign: SIGN_NAMES_EN[satSignIdx - 1],
    sign_ta: SIGN_NAMES_TA[satSignIdx - 1],
    house_from_lagna: satHouseFromLagna,
    career_fields_en: careerFieldsEn,
    career_fields_ta: careerFieldsTa,
    career_start_age_approx: careerStartAge,
    career_status_en: satConjuncts.length > 0
      ? `Saturn conjoins ${satConjuncts.join(", ")} in ${satDir} direction, guiding career toward ${careerFieldsEn.slice(0, 2).join(" & ")}.`
      : `Saturn in ${SIGN_NAMES_EN[satSignIdx - 1]} (${satDir}) fosters steady dedication and progressive consolidation through persistence.`,
    career_status_ta: satConjuncts.length > 0
      ? `சனி பகவான் ${satConjuncts.join(", ")} கிரகங்களுடன் இணைந்து ${satDir} திசையில் ${careerFieldsTa.slice(0, 2).join(" மற்றும் ")} துறைகளில் முன்னேற்றம் தருகிறார்.`
      : `சனி பகவான் ${SIGN_NAMES_TA[satSignIdx - 1]} ராசியில் (${satDir}) அமைந்திருப்பது சீரான உழைப்பையும் காலப்போக்கில் உறுதியான வளர்ச்சியையும் தரும்.`,
    saturn_sign_career_en: satSignCareerInfo.en,
    saturn_sign_career_ta: satSignCareerInfo.ta,
    direction: satDir,
    planets_in_same_direction: satSameDir,
    planets_in_opposite_direction: satOppPlanets,
    planets_in_2nd: sat2ndPlanets,
    planets_in_12th: sat12thPlanets,
    is_retrograde: isSatRetrograde,
    retrograde_backward_house_influence_en: satRetroBehindEn,
    retrograde_backward_house_influence_ta: satRetroBehindTa,
  };

  // 4. Directional Groups across Zodiac
  const directionalGroups: Record<string, string[]> = {
    "East (Fire)": [],
    "South (Earth)": [],
    "West (Air)": [],
    "North (Water)": [],
  };
  for (const [pName, pInfo] of Object.entries(planetMap)) {
    if ([1, 5, 9].includes(pInfo.sign_index)) directionalGroups["East (Fire)"].push(pName);
    else if ([2, 6, 10].includes(pInfo.sign_index)) directionalGroups["South (Earth)"].push(pName);
    else if ([3, 7, 11].includes(pInfo.sign_index)) directionalGroups["West (Air)"].push(pName);
    else if ([4, 8, 12].includes(pInfo.sign_index)) directionalGroups["North (Water)"].push(pName);
  }

  // 5. Rule 10: Rahu-Ketu Axis Career Outside
  function getSignsBetween(fromS: number, toS: number): number[] {
    const list: number[] = [];
    let curr = (fromS % 12) + 1;
    while (curr !== toS) {
      list.push(curr);
      curr = (curr % 12) + 1;
    }
    return list;
  }
  const rkSide1 = getSignsBetween(rahuSignIdx, ketuSignIdx);
  const rkSide2 = getSignsBetween(ketuSignIdx, rahuSignIdx);
  const rkDivides =
    (rkSide1.includes(jupSignIdx) && rkSide2.includes(satSignIdx)) ||
    (rkSide2.includes(jupSignIdx) && rkSide1.includes(satSignIdx));

  const rahuKetuOutside = {
    is_triggered: rkDivides,
    rule_number: 10,
    rule_title_en: "Rule 10: Rahu-Ketu Division Causing Profession Outside",
    rule_title_ta: "விதி 10: ராகு-கேது அச்சு குருவையும் சனியையும் பிரிப்பதால் வெளியூர்/வெளிநாட்டு உத்தியோகம்",
    explanation_en: rkDivides
      ? "Jeeva Karaka (Jupiter) and Karma Karaka (Saturn) reside on opposite hemispheres of the Rahu-Ketu axis. Per Bhrigu Nandi Nadi Rule 10, the native's career is definitively established outside their birthplace or abroad."
      : "Jupiter and Saturn reside on the same hemisphere of the Rahu-Ketu axis, anchoring primary career activities within the regional/native territory.",
    explanation_ta: rkDivides
      ? "ஜீவ காரகரான குருவும் கர்ம காரகரான சனியும் ராகு-கேது அச்சின் எதிரெதிர் பகுதிகளில் அமைந்துள்ளனர். பிருகு நந்தி நாடி விதி 10-ன் படி, ஜாதகரின் தொழில் பிறந்த ஊருக்கு வெளியே அல்லது வெளிநாடுகளில் அமையும் என்பது உறுதியாகிறது."
      : "குருவும் சனியும் ராகு-கேது அச்சின் ஒரே பகுதியில் இருப்பதால் உள்ளூர் அல்லது சொந்த மாநிலத்திற்குள்ளேயே தொழில் அமையும் வாய்ப்பு அதிகம்.",
  };

  // 6. Milestones
  const milestones: BrighuTimingMilestone[] = [];

  // Marriage
  if (venus) {
    const signsJupToVen = ((venus.sign_index - jupSignIdx + 12) % 12);
    const mAge1 = 12 + signsJupToVen;
    const mAge2 = 24 + signsJupToVen;
    const mAge3 = 36 + signsJupToVen;
    const marrAges = [mAge1, mAge2, mAge3].filter(a => a >= 18 && a <= 45);
    milestones.push({
      category: "marriage",
      age_years: marrAges.length > 0 ? marrAges : [25, 28],
      event_en: "Auspicious matrimonial alliance and solemnization of marriage.",
      event_ta: "சுப விவாக யோகம் மற்றும் இல்லற பந்தம் அமையும் காலம்.",
      basis_en: `Distance from Jupiter to Venus (${signsJupToVen} signs) projected over Jupiter's 12-year orbits.`,
      basis_ta: `குருவிலிருந்து சுக்கிரன் உள்ள தூரம் (${signsJupToVen} ராசிகள்) குருவின் 12 ஆண்டு சுற்றுவட்டக் கணக்கீடு.`,
    });
  }

  // Fame & Authority
  if (sun) {
    const signsJupToSun = ((sun.sign_index - jupSignIdx + 12) % 12);
    const fAge1 = 12 + signsJupToSun;
    const fAge2 = 24 + signsJupToSun;
    const fameAges = [fAge1, fAge2, 36 + signsJupToSun].filter(a => a >= 20 && a <= 60);
    milestones.push({
      category: "fame",
      age_years: fameAges.length > 0 ? fameAges : [24, 36],
      event_en: "Surge in social recognition, professional elevation, or government honor.",
      event_ta: "சமூக கௌரவம், உத்தியோக உயர்வு அல்லது அரசாங்க நற்புகழ் கூடும் காலம்.",
      basis_en: `Distance from Jupiter to Sun (${signsJupToSun} signs) across life cycles.`,
      basis_ta: `குருவிலிருந்து சூரியன் அமைந்த தூரம் (${signsJupToSun} ராசிகள்) அடிப்படையிலான சுழற்சி.`,
    });
  }

  // Property
  if (mars) {
    const signsJupToMars = ((mars.sign_index - jupSignIdx + 12) % 12);
    const pAge1 = 24 + signsJupToMars;
    const pAge2 = 36 + signsJupToMars;
    milestones.push({
      category: "property",
      age_years: [pAge1, pAge2],
      event_en: "Significant acquisition of landed property, residential building, or renovation.",
      event_ta: "சொந்த வீடு, மனை வாங்குதல் அல்லது பூமி வழி லாபம் கைகூடும் காலம்.",
      basis_en: `Distance from Jupiter to Mars (Bhumi Karaka) across adult orbits.`,
      basis_ta: `குருவிலிருந்து பூமி காரகனான செவ்வாய் உள்ள தூரத்தின் அடிப்படையிலான கணக்கீடு.`,
    });
  }

  // Career Start
  if (careerStartAge) {
    milestones.push({
      category: "career",
      age_years: [Math.round(careerStartAge)],
      event_en: "Commencement of independent career, stable employment, or key livelihood shift.",
      event_ta: "சுய தொழில் ஆரம்பம், உத்தியோக நிலைப்பாடு அல்லது முக்கிய தொழில் மாற்றம்.",
      basis_en: `Signs between Saturn (Karma) and Rahu multiplied by 2.5 years (Saturn sign duration).`,
      basis_ta: `சனி முதல் ராகு வரை உள்ள ராசிகள் × 2.5 ஆண்டுகள் (சனி ராசி காலம்).`,
    });
  }

  // 7. Physical Markers
  const physicalMarkers: BrighuPhysicalMarker[] = [];
  physicalMarkers.push({
    source_planet: "Sun",
    sign: SIGN_NAMES_EN[sunSignIdx - 1],
    organ_en: "Head, Eyes & Vital Heart",
    organ_ta: "தலை, கண்கள் மற்றும் இதய பலம்",
    indication_en: `Sun in ${SIGN_NAMES_EN[sunSignIdx - 1]} bestows robust stamina and dignified presence. Maintain hydration and ocular hygiene.`,
    indication_ta: `சூரியன் ${SIGN_NAMES_TA[sunSignIdx - 1]} ராசியில் இருப்பதால் சிறந்த கம்பீரமும் உடற்கட்டும் கிட்டும். கண் பார்வை மற்றும் பித்த சமநிலையைக் காப்பது நன்று.`,
    is_caution: false,
  });

  if (rahu) {
    physicalMarkers.push({
      source_planet: "Rahu",
      sign: SIGN_NAMES_EN[rahuSignIdx - 1],
      organ_en: "Nervous System, Lower Limbs & Skin Allergies",
      organ_ta: "நரம்பு மண்டலம், கால்கள் மற்றும் தோல் ஒவ்வாமை",
      indication_en: "Vigilance advised against sudden allergic rashes, chemical sensitivities, or nocturnal fatigue.",
      indication_ta: "ஒவ்வாமை, தடிப்புகள், ரசாயன அலர்ஜி மற்றும் இரவில் உறக்கமின்மை குறித்து முன்னெச்சரிக்கை தேவை.",
      is_caution: true,
    });
  }

  if (ketu) {
    physicalMarkers.push({
      source_planet: "Ketu",
      sign: SIGN_NAMES_EN[ketuSignIdx - 1],
      organ_en: "Abdomen, Intestines & Metabolic Absorption",
      organ_ta: "வயிறு, குடல் மற்றும் செரிமான பகுதி",
      indication_en: "Advised to consume fresh sattvic meals; sensitive digestive flora responds best to warm herbal infusions.",
      indication_ta: "செரிமான மண்டலம் மென்மையானது; எளிய சாத்விக உணவுகளும் சீரகத் தண்ணீரும் செரிமானத்திற்கு உகந்தது.",
      is_caution: true,
    });
  }

  // 8. Matched Rules
  const matchedRules: BrighuNaadiRuleMatch[] = [];

  if (satConjuncts.includes("Jupiter")) {
    matchedRules.push({
      rule_id: "BNS-KARMA-01",
      category: "profession",
      title_en: "Saturn + Jupiter: Dharmakarmadhipati Yoga in Profession",
      title_ta: "சனி + குரு: கர்மத்தில் தர்ம கர்மாதிபதி யோகம்",
      interpretation_en: "Nobility, justice, teaching, and respected administrative duty. High ethical reputation in career.",
      interpretation_ta: "ஆசிரியர் பணி, நீதித்துறை, ஆலோசனை, நிர்வாகம் அல்லது அறப்பணிகளில் சமுதாய உயர்வு.",
      planets_involved: ["Saturn", "Jupiter"],
      source_page: "pp. 45-48",
    });
  }

  if (satConjuncts.includes("Sun")) {
    matchedRules.push({
      rule_id: "BNS-KARMA-02",
      category: "profession",
      title_en: "Saturn + Sun: Government Connection & Authority Challenges",
      title_ta: "சனி + சூரியன்: அரசு தொடர்பு மற்றும் அதிகார போராட்டம்",
      interpretation_en: "Public sector liaison or state honors, coupled with delays or friction with authoritative figures.",
      interpretation_ta: "அரசுத் தொடர்பு அமைந்தாலும் மேலதிகாரிகளுடன் கருத்துவேறுபாடுகள் மற்றும் கடின உழைப்பு தேவைப்படும்.",
      planets_involved: ["Saturn", "Sun"],
      source_page: "pp. 48-50",
    });
  }

  if (jup && venus && jup.sign_index === venus.sign_index) {
    matchedRules.push({
      rule_id: "BNS-JEEVA-01",
      category: "wealth",
      title_en: "Jupiter + Venus: Sreemantha Yoga",
      title_ta: "குரு + சுக்கிரன்: ஸ்ரீமந்த யோகம்",
      interpretation_en: "Exquisite aesthetics, virtuous spouse, expansive conveyance, and abundant prosperity.",
      interpretation_ta: "அழகான வாழ்க்கைத் துணை, ஆடம்பர வாகனங்கள் மற்றும் நிறைவான செல்வ வளம் அருளும் ஸ்ரீமந்த யோகம்.",
      planets_involved: ["Jupiter", "Venus"],
      source_page: "pp. 22-25",
    });
  }

  if (jup && mars && jup.sign_index === mars.sign_index) {
    matchedRules.push({
      rule_id: "BNS-JEEVA-03",
      category: "property",
      title_en: "Jupiter + Mars: Guru-Mangala Yoga",
      title_ta: "குரு + செவ்வாய்: குரு-மங்கள யோகம்",
      interpretation_en: "Extensive real estate, agricultural property, bold courage, and fraternal leadership.",
      interpretation_ta: "நிலபுலன்கள், சொந்த மனை யோகம் மற்றும் சகோதர வழியில் மேன்மை தரும் யோகம்.",
      planets_involved: ["Jupiter", "Mars"],
      source_page: "pp. 25-28",
    });
  }

  // R. G. Rao Bhrigu Nandi Nadi Classical Yogas & Karma Remedies
  if (sat && planetMap["Moon"] && sat.sign_index === planetMap["Moon"].sign_index) {
    matchedRules.push({
      rule_id: "BN-SAT-013",
      category: "profession",
      title_en: "Saturn + Moon: Chandra Mouli Yoga (Ascetic Stature & Public Honors)",
      title_ta: "சனி + சந்திரன்: சந்திர மௌலி யோகம் (துறவு, தர்ம அறக்கட்டளை & அரசு கௌரவம்)",
      interpretation_en: "Devotion to Lord Shiva, leadership of religious/charitable trusts, ascetic bent of mind, or high municipal and governmental honors.",
      interpretation_ta: "சிவபக்தி, தர்ம அறக்கட்டளை தலைமை, ஆன்மீக நாட்டம், துறவு மனப்பாங்கு அல்லது மக்கள் மற்றும் அரசு வழியில் உயரிய கௌரவங்கள்.",
      planets_involved: ["Saturn", "Moon"],
      source_page: "Bhrigu Nandi Nadi, Charts 31 & 70, pp. 31, 54",
    });
  }

  if (sat && venus && rahu && sat.sign_index === venus.sign_index && sat.sign_index === rahu.sign_index) {
    matchedRules.push({
      rule_id: "BN-SAT-014",
      category: "profession",
      title_en: "Saturn + Venus + Rahu: Cinema, Visual Media & Shadow Arts",
      title_ta: "சனி + சுக்கிரன் + ராகு: திரைப்படம், காட்சி ஊடகம் மற்றும் நிழற்கலை யோகம்",
      interpretation_en: "Careers in film direction, cinematography, television production, glamour entertainment, and optical media.",
      interpretation_ta: "சினிமா தயாரிப்பு, திரைப்பட இயக்கம், ஒளிப்பதிவு, தொலைக்காட்சி மற்றும் கவர்ச்சி ஊடகத் துறைகளில் அபார சாதனை.",
      planets_involved: ["Saturn", "Venus", "Rahu"],
      source_page: "Bhrigu Nandi Nadi, Charts 70, 362, 381, pp. 54, 243, 253",
    });
  }

  if (sat && mars && ketu && sat.sign_index === mars.sign_index && sat.sign_index === ketu.sign_index) {
    matchedRules.push({
      rule_id: "BN-SAT-018",
      category: "profession",
      title_en: "Saturn + Mars + Ketu: Precision Surgery, Medical Cutlery & Defense Hardware",
      title_ta: "சனி + செவ்வாய் + கேது: அறுவை சிகிச்சை நிபுணர், மருத்துவ கருவிகள் மற்றும் பாதுகாப்பு உபகரணங்கள்",
      interpretation_en: "Surgeons, orthopedic specialists, manufacturers of hospital surgical instruments, or defense armaments engineering.",
      interpretation_ta: "அறுவை சிகிச்சை நிபுணர் (Surgeon), மருத்துவக் கூர்முனை உபகரணம் தயாரிப்பு அல்லது ராணுவ பாதுகாப்பு தளவாட உற்பத்தி.",
      planets_involved: ["Saturn", "Mars", "Ketu"],
      source_page: "Bhrigu Nandi Nadi, Charts 102, 107, pp. 107, 109",
    });
  }

  if (sat && planetMap["Mercury"] && sat.sign_index === planetMap["Mercury"].sign_index) {
    matchedRules.push({
      rule_id: "BN-SAT-019",
      category: "profession",
      title_en: "Saturn + Mercury: Chartered Accountant, Auditor & Financial Registrar",
      title_ta: "சனி + புதன்: தலைமை கணக்காயர் (CA), தணிக்கையாளர் மற்றும் நிதி ஆலோசகர்",
      interpretation_en: "Commercial mathematics, Chartered Accountancy (CA), tax auditing, corporate accounts, or senior banking executive.",
      interpretation_ta: "கணக்கியல் நிபுணர் (CA), தலைமை தணிக்கை அதிகாரி, கார்ப்பரேட் வரி ஆலோசகர் மற்றும் வங்கி உயர் நிதி நிர்வாகப் பதவிகள்.",
      planets_involved: ["Saturn", "Mercury"],
      source_page: "Bhrigu Nandi Nadi, Charts 19, 70, pp. 20, 54",
    });
  }

  if (jup && ketu && jup.sign_index === ketu.sign_index) {
    matchedRules.push({
      rule_id: "BN-JUP-017",
      category: "spiritual",
      title_en: "Jupiter + Ketu: Maha Gnana Yoga (Supreme Vedanta & Intuition)",
      title_ta: "குரு + கேது: மகா ஞான யோகம் (வேதாந்த ஞானம் & ஆன்மீக விழிப்புணர்வு)",
      interpretation_en: "Profound metaphysical intuition, mastery over Vedic philosophy, and guidance of spiritual seekers.",
      interpretation_ta: "ஆழ்ந்த உள்ளுணர்வு, வேதாந்த சாஸ்திர ஞானம், ஆன்மீக பற்று மற்றும் உலக மாயைகளில் பற்றற்ற மேலான நிலை.",
      planets_involved: ["Jupiter", "Ketu"],
      source_page: "Bhrigu Nandi Nadi, Charts 19, 41, pp. 20, 41",
    });
  }

  if (jup && rahu && jup.sign_index === rahu.sign_index) {
    matchedRules.push({
      rule_id: "BN-JUP-018",
      category: "life_force",
      title_en: "Jupiter + Rahu: Guru Chandal Yoga & Unconventional Breakthroughs",
      title_ta: "குரு + ராகு: குரு சண்டாள யோகம் மற்றும் புதுமை சிந்தனைகள்",
      interpretation_en: "Questions obsolete dogma, masters foreign knowledge or modern science, and achieves breakthroughs through unconventional paths.",
      interpretation_ta: "பாரம்பரிய மரபுகளைத் தாண்டி சிந்திக்கும் திறன், வெளிநாட்டுத் தொடர்பு, நவீன அறிவியல் மற்றும் வழக்கத்திற்கு மாறான வழிகளில் பெரும் முன்னேற்றம்.",
      planets_involved: ["Jupiter", "Rahu"],
      source_page: "Bhrigu Nandi Nadi, Charts 107, 109, pp. 109, 114",
    });
  }

  if (isFemale && mars && jup && mars.sign_index === jup.sign_index) {
    matchedRules.push({
      rule_id: "BN-MAR-005",
      category: "marriage",
      title_en: "Female Chart: Mars + Jupiter (Devaguru Kalatra Yoga - Highly Noble Husband)",
      title_ta: "பெண் ஜாதகம்: செவ்வாயுடன் குரு (தேவகுரு களத்திர யோகம்) - உத்தம குணமும் அந்தஸ்தும் கொண்ட கணவர்",
      interpretation_en: "Scholarly, righteous, generous spouse blessed with high societal stature and enduring marital bliss.",
      interpretation_ta: "தர்ம சிந்தனையும், கல்வியறிவும், சமுதாய மரியாதையும் மற்றும் நிறைந்த பாசமும் கொண்ட உத்தம கணவரை அளிக்கும் தேவகுரு யோகம்.",
      planets_involved: ["Mars", "Jupiter"],
      source_page: "Bhrigu Nandi Nadi, Charts 31, 109, pp. 26, 114",
    });
  }

  // Karmic Curses & Pilgrimage Remedies (Sanchita Karma)
  if (jup && rahu && sat && jup.sign_index === rahu.sign_index && ((sat.sign_index - jup.sign_index + 12) % 12) + 1 === 7) {
    matchedRules.push({
      rule_id: "BN-KRM-001",
      category: "spiritual",
      title_en: "Daivadroha / Sadhu Curse: Jupiter Afflicted by Saturn & Rahu (Remedy: 48 Somavara Vratam)",
      title_ta: "தெய்வத் துரோகம் / சாது சாபம்: சனி-ராகுவால் குரு பாதிப்பு (பரிகாரம்: 48 சோமவார விரதம் & கோகர்ண யாத்திரை)",
      interpretation_en: "Past Life Karmic Indication: Breaches of sacred vows. Remedy: Observing 48 consecutive Monday fasts (Somavara Vrata), pilgrimage to Gokarna Mahabaleshwar, and Annadanam.",
      interpretation_ta: "முற்பிறவி கர்ம வினை: ஆன்மீக பெரியோர்களை அவமதித்ததால் ஏற்படும் தடைகள். பரிகாரம்: 48 வாரங்கள் சோமவார விரதம், கோகர்ணம் மகாபலேஸ்வரர் தரிசனம் மற்றும் சாதுக்களுக்கு அன்னதானம்.",
      planets_involved: ["Jupiter", "Rahu", "Saturn"],
      source_page: "Bhrigu Nandi Nadi, Charts 1, 31, pp. 4, 26",
    });
  }

  if (venus && ketu && mars && venus.sign_index === ketu.sign_index && ((mars.sign_index - venus.sign_index + 12) % 12) + 1 === 7) {
    matchedRules.push({
      rule_id: "BN-KRM-002",
      category: "spiritual",
      title_en: "Stri Dosha: Venus Afflicted by Ketu & Mars (Remedy: Vedaranyam Pilgrimage & Widow Support)",
      title_ta: "ஸ்திரீ தோஷம்: கேது மற்றும் செவ்வாயால் சுக்கிரன் பாதிப்பு (பரிகாரம்: வேதாரண்யம் யாத்திரை & ஆதரவற்றோருக்கு உதவுதல்)",
      interpretation_en: "Past Life Karmic Indication: Injustice caused to a virtuous woman. Remedy: Pilgrimage to Vedaranyam (Tamil Nadu), holy dip in Veda Theertham, and donating clothes/food to destitute widows and children.",
      interpretation_ta: "முற்பிறவி கர்ம வினை: உத்தம பெண்ணிற்கு இழைத்த அநீதியால் திருமணத்தில் தடை. பரிகாரம்: வேதாரண்யம் சென்று வேத தீர்த்தத்தில் நீராடி, ஆதரவற்ற விதவை பெண்கள், குழந்தைகளுக்கு ஆடை, உணவு தானம் வழங்குதல்.",
      planets_involved: ["Venus", "Ketu", "Mars"],
      source_page: "Bhrigu Nandi Nadi, Charts 12, 87, pp. 12, 92",
    });
  }

  if (planetMap["Moon"] && rahu && planetMap["Moon"].sign_index === rahu.sign_index) {
    matchedRules.push({
      rule_id: "BN-KRM-003",
      category: "spiritual",
      title_en: "Matru Dosha: Moon Afflicted by Rahu (Remedy: Madurai Meenakshi Puja & 5 Kanya Puja)",
      title_ta: "மாத்ரு தோஷம்: ராகுவால் சந்திரன் பாதிப்பு (பரிகாரம்: மதுரை மீனாட்சி வழிபாடு & 5 கன்னியா பூஜை)",
      interpretation_en: "Past Life Karmic Indication: Distress caused to motherly figures. Remedy: Worshipping Divine Mother Meenakshi at Madurai, offering silk saree, and performing Kanya Puja for 5 young girls.",
      interpretation_ta: "முற்பிறவி கர்ம வினை: தாயாரை மனவேதனைக்கு உள்ளாக்கியதால் மன அமைதியின்மை உண்டாதல். பரிகாரம்: மதுரை மீனாட்சி அம்மனை தரிசித்து பட்டு வஸ்திரம் சாற்றுதல் மற்றும் 5 சிறுமிகளுக்கு கன்னியா பூஜை செய்தல்.",
      planets_involved: ["Moon", "Rahu"],
      source_page: "Bhrigu Nandi Nadi, Charts 14, 21, pp. 14, 21",
    });
  }

  if (sun && rahu && sun.sign_index === rahu.sign_index) {
    matchedRules.push({
      rule_id: "BN-KRM-004",
      category: "spiritual",
      title_en: "Pitru Dosha: Sun Afflicted by Rahu (Remedy: Shiva Rudrabhishekam & Pradosha Vrata)",
      title_ta: "பித்ரு தோஷம்: ராகுவால் சூரியன் பாதிப்பு (பரிகாரம்: பிரதோஷ ருத்ராபிஷேகம் & பித்ரு தர்ப்பணம்)",
      interpretation_en: "Past Life Karmic Indication: Ancestral Pitru obligations. Remedy: Performing Rudrabhishekam to Lord Shiva on Pradosham days, revering elders, and conducting Pitru Tarpanam on Amavasya.",
      interpretation_ta: "முற்பிறவி கர்ம வினை: முன்னோர்களின் கடமைகளை மறந்ததால் ஏற்படும் பித்ரு தோஷம். பரிகாரம்: பிரதோஷ நாட்களில் சிவபெருமானுக்கு ருத்ராபிஷேகம் செய்தல், அமாவாசை தோறும் பித்ரு தர்ப்பணம் செய்தல்.",
      planets_involved: ["Sun", "Rahu"],
      source_page: "Bhrigu Nandi Nadi, Charts 6, 19, pp. 12, 20",
    });
  }

  // 9. 20 BNN Golden Rules Evaluation
  const bnn20Evaluations: BnnRuleEvaluation[] = [
    {
      rule_number: 1,
      title_en: "Activation of Karakatvas via 2nd, 12th, 7th, 5th, 9th",
      title_ta: "2, 12, 7 மற்றும் 5, 9 ஆம் வீடுகளின் மூலம் காரகத்துவங்கள் இயங்குதல்",
      is_active: satSameDir.length > 0 || satOppPlanets.length > 0 || sat2ndPlanets.length > 0 || sat12thPlanets.length > 0,
      principle_en: "A planet's karakatvas act effectively when planets occupy the 2nd, 12th, 7th, 5th, or 9th from its sign.",
      principle_ta: "ஒரு கிரகத்தின் காரகத்துவங்கள் அதற்கு 2, 12, 7 அல்லது 5, 9 ஆகிய வீடுகளில் பிற கிரகங்கள் நின்றால் மட்டுமே செயல்படும்.",
      chart_evidence_en: `Saturn karakatva is linked with ${[...satSameDir, ...satOppPlanets, ...sat2ndPlanets, ...sat12thPlanets].join(", ") || "no direct planets"}.`,
      chart_evidence_ta: `சனியின் தொழில் காரகத்துவத்துடன் ${[...satSameDir, ...satOppPlanets, ...sat2ndPlanets, ...sat12thPlanets].join(", ") || "கிரகங்கள் இல்லை"} தொடர்புகொண்டுள்ளன.`,
      source_ref: "Rule 1, IJCRME 2022, pp. 23-24",
    },
    {
      rule_number: 2,
      title_en: "Cooperation of Planets in the Same Direction",
      title_ta: "ஒரே திசையில் உள்ள கிரகங்கள் இணைந்து செயல்படுதல்",
      is_active: satSameDir.length > 0,
      principle_en: "Planets in the same direction work together; degrees define manifestation sequence.",
      principle_ta: "ஒரே திசைக்குரிய ராசிகளில் நிற்கும் கிரகங்கள் ஒன்றிணைந்து செயல்படுகின்றன.",
      chart_evidence_en: `Saturn in ${satDir} is supported by ${satSameDir.join(", ") || "none"} in the same direction.`,
      chart_evidence_ta: `${satDir} திசையில் சனியுடன் ${satSameDir.join(", ") || "வேறு கிரகங்கள் இல்லை"} இணைந்துள்ளன.`,
      source_ref: "Rule 2, IJCRME 2022, p. 24",
    },
    {
      rule_number: 3,
      title_en: "7th Sign Direct Influence (Friendly Auspicious, Inimical Adverse)",
      title_ta: "7-ஆம் வீட்டில் உள்ள கிரகத்தின் நேரடித் தாக்கம்",
      is_active: satOppPlanets.length > 0,
      principle_en: "A planet in the 7th sign to a karaka exerts direct polar aspect (auspicious if friendly, adverse if inimical).",
      principle_ta: "7-ஆம் வீட்டில் நிற்கும் கிரகம் நட்பு எனில் சுப பலனையும், பகை எனில் அசுப பலனையும் தரும்.",
      chart_evidence_en: satOppPlanets.length > 0 ? `Saturn is aspected by ${satOppPlanets.join(", ")} in 7th sign.` : "7th house from Saturn is unoccupied.",
      chart_evidence_ta: satOppPlanets.length > 0 ? `சனிக்கு 7-ல் ${satOppPlanets.join(", ")} கிரகங்கள் அமர்ந்துள்ளன.` : "சனிக்கு 7-ஆம் வீட்டில் கிரகங்கள் இல்லை.",
      source_ref: "Rule 3, IJCRME 2022, p. 24",
    },
    {
      rule_number: 4,
      title_en: "Flanking by 2nd and 12th Houses",
      title_ta: "2 மற்றும் 12-ஆம் வீடுகளில் நிற்கும் கிரகங்களின் தாக்கம்",
      is_active: sat2ndPlanets.length > 0 || sat12thPlanets.length > 0,
      principle_en: "Friendly planets in 2nd/12th give favorable results; inimical planets cause restless workplace and transfers.",
      principle_ta: "2, 12-ல் நட்பு கிரகங்கள் நின்றால் சுபமும், பகை கிரகங்கள் நின்றால் வேலை மாற்றங்களும் ஏற்படும்.",
      chart_evidence_en: `Saturn flanked by 12th: [${sat12thPlanets.join(", ") || "Empty"}] and 2nd: [${sat2ndPlanets.join(", ") || "Empty"}].`,
      chart_evidence_ta: `சனிக்கு 12-ல் [${sat12thPlanets.join(", ") || "எதுவுமில்லை"}] மற்றும் 2-ல் [${sat2ndPlanets.join(", ") || "எதுவுமில்லை"}] அமர்ந்துள்ளன.`,
      source_ref: "Rule 4, IJCRME 2022, p. 24",
    },
    {
      rule_number: 10,
      title_en: "Rahu-Ketu Bisection: Division of Jupiter and Saturn Causing Profession Outside",
      title_ta: "ராகு-கேது அச்சு குருவையும் சனியையும் பிரிப்பதால் வெளியூர் வேலை யோகம்",
      is_active: rkDivides,
      principle_en: "If Rahu-Ketu axis separates Jupiter on one side and Saturn on the other side, profession is set outside/abroad.",
      principle_ta: "ராகு-கேது அச்சின் ஒரு புறத்தில் குருவும் மறுபுறத்தில் சனியும் அமைந்தால் வெளியூர் அல்லது வெளிநாட்டில் உத்தியோகம் அமையும்.",
      chart_evidence_en: rahuKetuOutside.explanation_en,
      chart_evidence_ta: rahuKetuOutside.explanation_ta,
      source_ref: "Rule 10, IJCRME 2022, p. 26",
    },
    {
      rule_number: 14,
      title_en: "Retrograde Planet Moves toward 12th House with Half-Sight Aspect",
      title_ta: "வக்ர கிரகம் 12-ஆம் வீட்டை நோக்கி நகர்ந்து பின்னோக்கிய பார்வை செலுத்துதல்",
      is_active: isSatRetrograde || (jup?.is_retrograde || false),
      principle_en: "A retrograde planet shifts energy toward the 12th house from its sign, neutralizing past vulnerabilities.",
      principle_ta: "வக்ர கிரகம் தான் நின்ற ராசிக்கு 12-ஆம் வீட்டை நோக்கி பின்னோக்கி நகர்ந்து பலன் தருகிறது.",
      chart_evidence_en: isSatRetrograde ? "Saturn is retrograde, casting active backward influence into 12th house." : "Direct motion without backward shift.",
      chart_evidence_ta: isSatRetrograde ? "சனி வக்ரம் பெற்று 12-ஆம் வீட்டை நோக்கி பின்னோக்கிப் பலன் தருகிறார்." : "நேர்கதி இயக்கம்.",
      source_ref: "Rule 14, IJCRME 2022, p. 26",
    },
  ];

  return {
    treatise_metadata: {
      title: "Brighu Naadi Sangraha: (Pearls of Brighu Naadi)",
      author: "Dr. N. Srinivasan Shastry",
      publisher: "Sagar Publications",
      pages: 152,
      philosophy_en: "Sage Brighu's core doctrine posits that Jupiter (Jeeva) embodies the life force, and all 12 houses reckoned from Jupiter describe personal evolution, while Saturn (Karma) determines career and societal duty.",
      philosophy_ta: "மகரிஷி பிருகுவின் நாடி முறைப்படி லக்னத்தை விட குருவே ஜீவ காரகராகவும், சனியே கர்ம காரகராகவும் விளங்கி மனித விதியை அட்சரம் பிசகாமல் நிர்ணயிக்கின்றனர்.",
      jeeva_karaka_role: "Jupiter acts as the central pivot of health, character, marriage, wealth, and destiny.",
      karma_karaka_role: "Saturn dictates trade, employment, struggles, and professional achievement.",
    },
    bnn_research_metadata: {
      paper_title: "A Study of the Basic Rules in Bhrigu Nandi Nadi",
      paper_title_ta: "பிருகு நந்தி நாடியின் அடிப்படைக் கோட்பாடுகள் பற்றிய ஆய்வு",
      authors: [
        "A. Jagadeesan (Full Time Ph.D Research Scholar)",
        "Dr. K. Jothimani (HOD & Associate Professor)",
      ],
      institution: "School of Vedic Astrology, Vels Institute of Science, Technology & Advanced Studies (VISTAS), Chennai, Tamil Nadu",
      journal: "International Journal of Current Research and Modern Education (IJCRME)",
      volume_issue_pages: "Volume 7, Issue 2, pp. 23-31, 2022",
      issn: "2455-5428",
      impact_factor: "6.925",
      system_founder: "Mr. R. G. Rao (Astrological Grandfather of Bhrigu Nandi Nadi)",
      summary_en: "Comprehensive academic formulation of Mr. R. G. Rao's 20 golden Bhrigu Nandi Nadi predictive rules covering directional trines, friendships, flanking, and retrograde vector dynamics.",
      summary_ta: "ஆர். ஜி. ராவ் அவர்களின் பிருகு நந்தி நாடி முறையின் 20 அடிப்படைக் கணிப்பு விதிகள், திசை வழி சேர்க்கைகள் மற்றும் வக்ர கிரக இயக்கங்களின் விரிவான ஆய்வு.",
    },
    birth_environment: birthEnv,
    jeeva_karaka: jeeva,
    karma_karaka: karma,
    timing_milestones: milestones,
    physical_health_markers: physicalMarkers,
    matched_rules: matchedRules,
    bnn_directional_groups: directionalGroups,
    bnn_20_rules_evaluations: bnn20Evaluations,
    rahu_ketu_axis_career_outside: rahuKetuOutside,
    pankajj_duaa_compendium: {
      metadata: {
        title: "BNN Astrology Notes by Pankajj K Duaa",
        title_ta: "பங்கஜ் கே துவா அவர்களின் பிருகு நந்தி நாடி ஜோதிட விதிகள்",
        author: "Pankajj K Duaa",
        traditions: ["Bhrigu Nandi Nadi (BNN)", "Krishnamurti Paddhati (KP)", "Vedic Parashari", "Lal Kitab"],
        summary_en: "Comprehensive synthesis combining planetary karakatwas, Naadi house qualities irrespective of signs, directional trines, degree movements, CSL event combinations, medical diagnosis by organ and gender-differentiated life significators, and specific remedies.",
        summary_ta: "பங்கஜ் கே துவா அவர்களின் பிருகு நந்தி நாடி முறை: காரக தத்துவங்கள், ராசி சாரா பாவ பலன்கள், திசை திரிகோணங்கள், பாகை வினைகள், கே.பி. உப-அதிபதி விதிகள், மருத்துவ ஜோதிடம் மற்றும் பரிகாரங்கள்.",
      },
      rashi_mobility_summary: {
        char_movable_count: planets.filter(p => [1, 4, 7, 10].includes(p.sign_index)).length,
        char_planets: planets.filter(p => [1, 4, 7, 10].includes(p.sign_index)).map(p => p.name),
        sthir_fixed_count: planets.filter(p => [2, 5, 8, 11].includes(p.sign_index)).length,
        sthir_planets: planets.filter(p => [2, 5, 8, 11].includes(p.sign_index)).map(p => p.name),
        upaye_dual_count: planets.filter(p => [3, 6, 9, 12].includes(p.sign_index)).length,
        upaye_planets: planets.filter(p => [3, 6, 9, 12].includes(p.sign_index)).map(p => p.name),
      },
      naadi_house_qualities: (() => {
        const qualities: Record<string, { good: number[]; very_bad: number[]; mix: number[] }> = {
          Sun: { good: [1, 2, 3, 4, 5, 9, 10, 11], very_bad: [7], mix: [6, 8, 12] },
          Moon: { good: [1, 2, 3, 4, 5, 7, 9, 10, 11], very_bad: [6, 8, 12], mix: [] },
          Mars: { good: [1, 2, 5, 6, 9, 10, 11, 12], very_bad: [3, 4, 8], mix: [7] },
          Venus: { good: [1, 2, 3, 4, 5, 7, 9, 10, 11, 12], very_bad: [], mix: [6, 8] },
          Mercury: { good: [1, 2, 5, 6, 7, 9, 10, 11], very_bad: [3, 12], mix: [4, 8] },
          Jupiter: { good: [1, 2, 3, 4, 5, 7, 9, 11, 12], very_bad: [6, 8], mix: [10] },
          Saturn: { good: [2, 3, 5, 6, 9, 10, 11], very_bad: [1, 8, 9], mix: [4, 7, 12] },
          Rahu: { good: [3, 6, 10, 11], very_bad: [1, 2, 8, 9, 12], mix: [4, 5, 7] },
          Ketu: { good: [2, 5, 9, 10, 11, 12], very_bad: [3, 6, 8], mix: [1, 4, 7] },
        };
        const res: Record<string, { house: number; status: string; status_ta: string }> = {};
        for (const p of planets) {
          const h = ((p.sign_index - lagnaIdx + 12) % 12) + 1;
          const q = qualities[p.name];
          if (q) {
            let st = "Neutral", stTa = "நடுத்தரம்";
            if (q.good.includes(h)) { st = "Good (Ucch Effect)"; stTa = "உச்ச பலன் / நற்பலன்"; }
            else if (q.very_bad.includes(h)) { st = "Very Bad (Neech Effect)"; stTa = "நீச பலன் / கடும் பாதிப்பு"; }
            else if (q.mix.includes(h)) { st = "Mixed Effect"; stTa = "கலப்பு பலன்"; }
            res[p.name] = { house: h, status: st, status_ta: stTa };
          }
        }
        return res;
      })(),
      medical_astrology: {
        life_significator: {
          prime_planet: gender.toLowerCase() === "female" ? "Venus" : "Jupiter",
          is_afflicted: false,
          house: 1,
          evaluation_en: `Life significator (${gender.toLowerCase() === "female" ? "Venus" : "Jupiter"}) is analyzed for constitutional vitality.`,
          evaluation_ta: `ஜீவ காரகர் (${gender.toLowerCase() === "female" ? "சுக்கிரன்" : "குரு"}) ஆரோக்கியத்தின் அடிப்படையாக கணிக்கப்படுகிறார்.`,
        },
        organ_afflictions: [],
        cancer_yoga: {
          is_active: false,
          title_en: "Saturn-Rahu Cancer / Cellular Mutation Vulnerability",
          title_ta: "சனி - ராகு புற்றுநோய் / கட்டி பாதிப்பு எச்சரிக்கை",
          explanation_en: "Saturn and Rahu interaction checked for cellular vitality balance.",
          explanation_ta: "சனியும் ராகுவும் இணைவு ஆரோக்கியத்தில் கவனிக்கப்படுகிறது.",
        },
      },
      matched_pairs: [],
      matched_yogas: [],
      degree_border_alerts: [],
      prescribed_remedies: [
        {
          planet: "Saturn",
          rudraksha: "7 Mukhi Rudraksha",
          deities: "Lord Bhairava, Lord Shiva, Lord Shani",
          mantra: "Om Sham Shanaischaraya Namaha",
          key_remedies: [
            "Dana of mustard oil, whole black urad dal, water on Shivling.",
            "Feed visually challenged (blind) individuals for career breakthrough.",
            "Feed crows and black buffaloes.",
          ],
        },
      ],
      general_life_maxims: [
        { rule: "Bhandara Food Taboo", maxim: "Avoid eating in public free bhandaras; doing so severely afflicts the Sun and self-esteem." },
        { rule: "Used Articles Taboo", maxim: "Never wear clothes, shoes, or slippers discarded by others." },
        { rule: "Speech Purification", maxim: "Apply saffron (Kesar) tilak to the tongue to sweeten harsh speech (Vaani Dosha)." },
        { rule: "Evening Arrival Rule", maxim: "Never return home with empty hands in the evening; always bring fruits or household goods." },
        { rule: "Broken Rice Taboo", maxim: "Do not consume broken rice grains (Tukdi Chawal represents Ketu)." },
        { rule: "Masoor Dal Debt Remedy", maxim: "Offer 400g red masoor dal onto Shivling while chanting: 'Om Rin Mukteshvaraya Namah Mahadevaya Namah'." },
        { rule: "Universal S.O.S. Remedy", maxim: "When any planet is severely afflicted, offering its corresponding metal or grain to Lord Shiva, a cow, or a beggar removes negative karma with zero side effects." },
      ],
    },
  };
}
