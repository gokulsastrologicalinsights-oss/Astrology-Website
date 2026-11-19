// Classical Planetary House Placement Predictions Engine
// Synthesized directly from Dr. B. V. Raman's "How to Judge a Horoscope" (Vol 1 & 2),
// Kalyana Varma's "Saravali" (Ch. 30), and Maharishi Parashara's BPHS.

import { getGrahaDignity } from "./dignity";

export type BhavaCategory = "kendra" | "trikona" | "upachaya" | "dusthana" | "panaphara" | "apoklima";

export interface PlanetarySthanaPrediction {
  planet: "Sun" | "Moon" | "Mars" | "Mercury" | "Jupiter" | "Venus" | "Saturn" | "Rahu" | "Ketu";
  planet_name_ta: string;
  symbol: string;
  element: string;
  house: number; // 1 to 12 from Lagna
  bhava_category: BhavaCategory;
  house_title_ta: string;
  house_title_en: string;
  core_traits_ta: string[];
  core_traits_en: string[];
  strong_placement_ta: string[];
  strong_placement_en: string[];
  weak_placement_ta: string[];
  weak_placement_en: string[];
  career_wealth_ta: string[];
  career_wealth_en: string[];
  health_precautions_ta: string[];
  health_precautions_en: string[];
  source_reference: string;
}

export interface EvaluatedPlanetSthana {
  planet_name: string;
  planet_name_ta: string;
  symbol: string;
  element: string;
  house_number: number;
  house_name_ta: string;
  house_name_en: string;
  bhava_category: BhavaCategory;
  sign_index: number;
  sign_name_ta: string;
  sign_name_en: string;
  degree_in_sign: number;
  is_retrograde: boolean;
  dignity_label_ta: string;
  dignity_label_en: string;
  dignity_type: "exalted" | "own_sign" | "dikbala" | "friendly" | "debilitated" | "enemy" | "neutral";
  shadbala_rupas?: number;
  shadbala_ratio?: number;
  shadbala_percentage?: number;
  shadbala_is_strong?: boolean;
  is_net_strong: boolean;
  status_summary_ta: string;
  status_summary_en: string;
  prediction: PlanetarySthanaPrediction;
}

const SIGN_NAMES_TA = [
  "மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்",
  "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்",
  "தனுசு", "மகரம்", "கும்பம்", "மீனம்"
];

const SIGN_NAMES_EN = [
  "Aries", "Taurus", "Gemini", "Cancer",
  "Leo", "Virgo", "Libra", "Scorpio",
  "Sagittarius", "Capricorn", "Aquarius", "Pisces"
];

export const PLANETARY_STHANA_PREDICTIONS: PlanetarySthanaPrediction[] = [
  {
    "planet": "Sun",
    "planet_name_ta": "சூரியன்",
    "symbol": "☀️",
    "element": "தீ (Agni)",
    "house": 1,
    "bhava_category": "kendra",
    "house_title_ta": "1-ஆம் பாவம் - லக்னம் (தனு பாவம் / சுய கௌரவம்)",
    "house_title_en": "1st House - Ascendant / Tanu Bhava (Self & Dignity)",
    "core_traits_ta": [
      "அதிகமான தன்னம்பிக்கை, கம்பீரமான தோற்றம் மற்றும் தலைமை தாங்கும் குணம் கொண்டவர்.",
      "மானமரியாதை மற்றும் சுயகௌரவத்திற்கு அதிமுக்கியத்துவம் கொடுப்பவர்; தலைவணங்க விரும்பாத சுபாவம்.",
      "விரைவில் கோபமும் ஆவேசமும் வரும் முன்கோபித்தனம் உண்டு; ஆனால் கோபம் நிலைக்காது.",
      "உயர்ந்த லட்சியங்கள், நேர்மையான கொள்கைகள் மற்றும் சுதந்திரமான சிந்தனைப்போக்கு உடையவர்.",
      "பிறர் ஆதிக்கத்தையோ கட்டுப்பாட்டையோ ஒருபோதும் ஏற்க மாட்டார்."
    ],
    "core_traits_en": [
      "Strong moral nature, righteous minded, ambitious, and lover of authority and power.",
      "Places immense value on personal self-respect, honor, and dignity; refuses subservience.",
      "Quick-tempered and spirited with a fiery temperament, though anger subsides quickly.",
      "Possesses a magnetic presence, robust vitality, and natural leadership aptitude.",
      "Cherishes independence and fiercely resists being dominated by others."
    ],
    "strong_placement_ta": [
      "மேஷத்தில் உச்சம் அல்லது சிம்மத்தில் ஆட்சி பெற்றால்: அளப்பரிய அரசு கௌரவம், சமுதாயத்தில் முதன்மை அந்தஸ்து மற்றும் நீண்ட ஆயுள் உண்டாகும்.",
      "திக்பலம் அல்லது அதிக ஷட்பலத்துடன் இருப்பின்: அரசாங்க உயர்பதவி, அரசியல் செல்வாக்கு மற்றும் பிறரால் போற்றப்படும் பெருவாழ்வு அமையும்."
    ],
    "strong_placement_en": [
      "Exalted in Aries or in own sign Leo: Confers high government rank, commanding stature, robust health, and longevity.",
      "High Shadbala or Digbala: Endows executive power, magnetic charisma, and triumph in all public endeavors."
    ],
    "weak_placement_ta": [
      "துலாத்தில் நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: கண் உபாதைகள், தலைவலி, அதிக அலைச்சல் மற்றும் பிடிவாத குணம் உண்டாகலாம்.",
      "பகை/நீச பலம் பெற்றால்: காரணமற்ற கோபம், தற்பெருமை மற்றும் தந்தையுடன் கருத்து வேறுபாடுகள் ஏற்பட வாய்ப்புண்டு."
    ],
    "weak_placement_en": [
      "Debilitated in Libra or afflicted by Saturn/Rahu: Tends towards eye afflictions, chronic headaches, ego clashes, and restless wandering.",
      "Low planetary strength: Leads to unwarranted arrogance, strained relations with the father, and obstacles in public life."
    ],
    "career_wealth_ta": [
      "நிர்வாகத் துறை, அரசுப் பணிகள், மருத்துவம், அரசியல், அதிகாரப் பதவிகள் மற்றும் தலைமைப் பொறுப்புகளில் பெரும் வெற்றி.",
      "சொந்த உழைப்பாலும் கௌரவமான வழிகளாலும் செல்வமும் சமுதாய மதிப்பும் ஈட்டுவார்."
    ],
    "career_wealth_en": [
      "Success in administrative services, state leadership, governance, medicine, defense, and entrepreneurial leadership.",
      "Acquires wealth through honorable self-exertion, commanding positions, and royal or state patronage."
    ],
    "health_precautions_ta": [
      "உடலில் பித்த உஷ்ணம், கண் சம்மந்தப்பட்ட உபாதைகள், ரத்த அழுத்த மாறுபாடுகள் மற்றும் தலைவலி ஏற்பட வாய்ப்புண்டு.",
      "குளிர்ந்த நீர் அருந்துதல் மற்றும் அதிக வெயிலைத் தவிர்ப்பது நலம் பயக்கும்."
    ],
    "health_precautions_en": [
      "Prone to bilious heat, febrile complaints, eye strain, and blood pressure fluctuations.",
      "Benefited by cooling foods, balanced hydration, and regular eye care."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 51) & Saravali Ch. 30"
  },
  {
    "planet": "Sun",
    "planet_name_ta": "சூரியன்",
    "symbol": "☀️",
    "element": "தீ (Agni)",
    "house": 2,
    "bhava_category": "panaphara",
    "house_title_ta": "2-ஆம் பாவம் - தன பாவம் (வாக்கு, தனம் & குடும்பம்)",
    "house_title_en": "2nd House - Dhana Bhava (Wealth, Speech & Family)",
    "core_traits_ta": [
      "பேச்சில் உறுதியும், அதிகார தோரணையும், கம்பீரமான குரல்வளமும் கொண்டவர்.",
      "தான் நினைத்ததை வெளிப்படையாகவும் அழுத்தமாகவும் பேசும் நேர்மையான குணம்.",
      "குடும்பத்தில் தலைமைப் பொறுப்பை ஏற்று நடத்தும் சுபாவம்; விட்டுக் கொடுக்காத கொள்கை.",
      "கடின உழைப்பால் மட்டுமே செல்வத்தைச் சேர்க்க வேண்டும் என்ற தளராத உறுதி கொண்டவர்."
    ],
    "core_traits_en": [
      "Possesses a firm, commanding, and authoritative tone of voice; speaks truthfully and directly.",
      "Values financial independence through industrious, hard-earned effort.",
      "Tends to assume headship of family affairs; unyielding on ethical principles.",
      "May display stubbornness in financial and domestic negotiations."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: பூர்வீகச் சொத்துகள், அரசாங்கக் கொடைகள் மற்றும் நிலையான வங்கி இருப்பு அமையும்.",
      "சுபப் பார்வை இருப்பின்: வாக்கு பலிதம், இனிமையான பேச்சு மற்றும் செல்வச் செழிப்புடன் கூடிய குடும்ப நலம் கிட்டும்."
    ],
    "strong_placement_en": [
      "Exalted or well-placed: Accumulates solid ancestral wealth, earns state subsidies, and gains high financial security.",
      "Benefic aspects: Confers influential speech, respected lineage, and abundant fiscal prosperity."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: அதிகாரிகளிடம் வாக்குவாதம் செய்து இழப்பு ஏற்படுதல், முகத்தில் வடுக்கள் உண்டாகலாம்.",
      "பண விரயங்களும், பேச்சினால் உறவினர்களிடம் மனக்கசப்புகளும் ஏற்படக்கூடும்."
    ],
    "weak_placement_en": [
      "Afflicted or debilitated: Financial losses due to friction with authorities, domestic disputes, and face/mouth ailments.",
      "Harsh speech may alienate family members and lead to sudden financial drain."
    ],
    "career_wealth_ta": [
      "வங்கிகள், நிதித்துறை, அரசு கருவூலம், நகை/தங்கம் வர்த்தகம் மற்றும் சட்ட ஆலோசனைகளில் தன லாபம்.",
      "சுயமுயற்சியால் சொத்துகளைச் சேர்ப்பார்; அரசு வழியில் ஆதாயம் உண்டு."
    ],
    "career_wealth_en": [
      "Gains through banking, government treasury, precious metals/gems, legal advocacy, and revenue administration.",
      "Builds tangible assets through resolute perseverance and disciplined money management."
    ],
    "health_precautions_ta": [
      "வலது கண் கோளாறுகள், தொண்டை அல்லது பற்கள் சம்மந்தப்பட்ட வியாதிகள், வாய் புண்கள் வரலாம்.",
      "சூடான மற்றும் அதிக காரமான உணவுப் பண்டங்களைக் குறைப்பது நல்லது."
    ],
    "health_precautions_en": [
      "Susceptibility to right-eye afflictions, facial heat eruptions, and throat irritations.",
      "Advised to moderate spicy food intake and maintain oral dental hygiene."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 99) & Saravali Ch. 30"
  },
  {
    "planet": "Sun",
    "planet_name_ta": "சூரியன்",
    "symbol": "☀️",
    "element": "தீ (Agni)",
    "house": 3,
    "bhava_category": "upachaya",
    "house_title_ta": "3-ஆம் பாவம் - சகஜ பாவம் (தைரியம் & வீரியம்)",
    "house_title_en": "3rd House - Sahaja Bhava (Courage, Valor & Enterprise)",
    "core_traits_ta": [
      "அசாத்தியமான மனத்துணிச்சல், வீரம் மற்றும் எந்த சவாலையும் எதிர்கொள்ளும் திடமான குணம்.",
      "எதிரிகளைத் துணிச்சலாக வெல்லும் ஆற்றல்; உபசய ஸ்தானத்தில் சூரியன் அமர்வது சிறந்த அமைப்பாகும்.",
      "சுயமரியாதையும் கம்பீரமும் கொண்ட செயல்வீரர்; பிறரிடம் கையேந்தாத சுயசார்பு.",
      "இளைய சகோதரர்களிடம் சற்று கண்டிப்பும் மேலாதிக்கப் போக்கும் கொண்டிருக்கலாம்."
    ],
    "core_traits_en": [
      "Extraordinary courage, high fortitude, and undaunted valor in overcoming obstacles.",
      "Sun in the 3rd (an Upachaya house) is hailed as an auspicious placement for vanquishing adversaries.",
      "Self-reliant, highly spirited, and capable of driving ventures with fearless enterprise.",
      "May exert a firm, demanding authority over younger siblings."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: நாடெங்கும் புகழ், மாபெரும் பராக்கிரமம் மற்றும் வெற்றிகள் குவியும்.",
      "உயர் அதிகாரிகளுடனும் முக்கியஸ்தர்களுடனும் நெருங்கிய நட்பும் அதனால் பெரும் நன்மைகளும் கிட்டும்."
    ],
    "strong_placement_en": [
      "Strong or exalted: Confers far-reaching fame, heroic standing, and prosperous journeys.",
      "Commands respect among dignitaries, armed forces, or top-level corporate boards."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாப தொடர்புகள் பெற்றால்: சகோதரர்களுடன் கருத்து வேறுபாடுகள், கைகளில் வலி அல்லது காயங்கள் உண்டாகலாம்.",
      "அதிகமான பிடிவாதத்தால் வீண் பகைகளும் மன உளைச்சலும் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Afflicted or debilitated: Friction with brothers, shoulder/arm injuries, and unyielding obstinacy.",
      "May foster unnecessary antagonisms through excessive rashness."
    ],
    "career_wealth_ta": [
      "ராணுவம், காவல் துறை, விளையாட்டு, எழுத்து, தகவல் தொடர்பு, பிரசுரத் தொழில் மற்றும் பொது நிர்வாகத்தில் உயர்வு.",
      "தைரியமான முதலீடுகள் மற்றும் குறுகிய பயணங்கள் மூலம் தன வரவு அதிகரிக்கும்."
    ],
    "career_wealth_en": [
      "Lucrative success in defense services, policing, journalism, competitive sports, publishing, and transport.",
      "Gains wealth through audacious strategic initiatives and lucrative business travels."
    ],
    "health_precautions_ta": [
      "தோள்பட்டை வலி, கைகளில் நரம்புத் தளர்ச்சி, காது கேளாமை அல்லது காது குடைச்சல் வரலாம்.",
      "முறையான உடற்பயிற்சியும் தோள் பட்டைக்கான ஆசனங்களும் நலம் தரும்."
    ],
    "health_precautions_en": [
      "Vulnerable to shoulder stiffness, upper arm injuries, and hearing or ear sensitivities.",
      "Benefited by regular shoulder exercises and balanced nervous relaxation."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 139) & Saravali Ch. 30"
  },
  {
    "planet": "Sun",
    "planet_name_ta": "சூரியன்",
    "symbol": "☀️",
    "element": "தீ (Agni)",
    "house": 4,
    "bhava_category": "kendra",
    "house_title_ta": "4-ஆம் பாவம் - சுக பாவம் (தாய், நிலம் & மன அமைதி)",
    "house_title_en": "4th House - Sukha Bhava (Mother, Property & Domestic Life)",
    "core_traits_ta": [
      "உயர்ந்த கொள்கைகளும், தத்துவ சிந்தனைகளும், பாரம்பரியத்தின் மீது தீவிர பற்றும் கொண்டவர்.",
      "வீட்டிலும் குடும்பத்திலும் தன் ஆதிக்கமும் கட்டுப்பாடும் இருக்க வேண்டும் என விரும்புவார்.",
      "மனதில் ஒருவிதமான அலைபாயும் தன்மையும், அடிக்கடி உள்ளுக்குள் கொதிக்கும் வேகமும் இருக்கலாம்.",
      "தாய் வழியில் ஒழுக்கமும் மரியாதையும் பெற்றவர்; ஆன்மீக மற்றும் ரகசிய சாஸ்திரங்களில் ஆர்வம்."
    ],
    "core_traits_en": [
      "Philosophical, dignified, and holds deep attachment to family heritage and traditional values.",
      "Desires order and authority within the domestic household; can be strict with dependents.",
      "Experiences occasional internal restlessness despite an outward poise.",
      "Inclined towards deep contemplation, ancient scriptures, and occult wisdom."
    ],
    "strong_placement_ta": [
      "சுப ஸ்தானம் அல்லது ஆட்சி/உச்சம் பெற்றால்: மாட மாளிகைகள், பூமி லாபம், ஆடம்பர வாகனங்கள் மற்றும் மன நிம்மதி கிட்டும்.",
      "தந்தையின் சொத்துகள் தடையின்றி வந்து சேரும்; தாய்வழி உறவுகளால் மரியாதை உண்டாகும்."
    ],
    "strong_placement_en": [
      "Exalted or well-aspected: Grants grand residential estates, fertile lands, conveyance luxuries, and stable peace.",
      "Inherits ancestral properties seamlessly and enjoys honorable paternal favor."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தாயாரின் உடல்நலக் குறைவு, வீட்டு சூழலில் அமைதியின்மை மற்றும் சொத்து தகராறுகள் ஏற்படலாம்.",
      "வாகனங்களால் செலவுகளும், பூர்வீக வீட்டை விட்டு இடம்பெயரும் சூழ்நிலையும் உருவாகலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Domestic friction, mother's frail health, property litigations, and heart anxieties.",
      "Disputes over parental inheritance and frequent changes of residence."
    ],
    "career_wealth_ta": [
      "நிலம், ரியல் எஸ்டேட், சுரங்கத் தொழில், விவசாயம், கட்டிடக் கலை மற்றும் அரசு மானியங்கள் மூலம் செல்வம்.",
      "அரசு வாகன யோகம் மற்றும் கௌரவப் பதவிகள் கிட்டும்."
    ],
    "career_wealth_en": [
      "Thrives in real estate, civil engineering, mining, agriculture, automotive industries, and government quarters.",
      "Builds enduring asset portfolios in prime landed properties."
    ],
    "health_precautions_ta": [
      "இதயப் படபடப்பு, நெஞ்சு சளி, ரத்த அழுத்தம் மற்றும் மன உளைச்சலுக்கு வாய்ப்புண்டு.",
      "யோகா, பிராணாயாமம் மற்றும் எளிய உணவுகள் இதய நலனைப் பாதுகாக்கும்."
    ],
    "health_precautions_en": [
      "Vulnerable to cardiac strain, chest congestion, blood pressure surges, and mental stress.",
      "Cardiovascular checkups and deep breathing meditation are strongly advised."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 173) & Saravali Ch. 30"
  },
  {
    "planet": "Sun",
    "planet_name_ta": "சூரியன்",
    "symbol": "☀️",
    "element": "தீ (Agni)",
    "house": 5,
    "bhava_category": "trikona",
    "house_title_ta": "5-ஆம் பாவம் - பூர்வ புண்ணியம் (புத்தி & புத்திர பாவம்)",
    "house_title_en": "5th House - Putra & Poorvapunya Bhava (Intellect, Progeny & Merit)",
    "core_traits_ta": [
      "கூர்மையான மதிநுட்பம், ஆழமான புத்திசாலித்தனம் மற்றும் திட்டமிட்டு செயலாற்றும் திறன் கொண்டவர்.",
      "தெய்வ பக்தி, மந்திர சித்தி மற்றும் வேத சாஸ்திரங்களை எளிதில் கிரகிக்கும் ஆற்றல் உண்டு.",
      "மானமரியாதைக்கு முதலிடம் கொடுப்பதால் தன் புத்திசாலித்தனத்தைப் பிறர் குறை கூற அனுமதிக்க மாட்டார்.",
      "குழந்தைகளிடம் சற்று கண்டிப்பான அணுகுமுறையைக் கடைப்பிடிக்க வாய்ப்புண்டு."
    ],
    "core_traits_en": [
      "Sharp intellect, piercing analytical insight, and impressive strategic acumen.",
      "Deep spiritual inclination, inclination towards mantras, ethical philosophy, and higher research.",
      "Takes immense pride in intellectual superiority; hates superficiality.",
      "May exhibit an authoritative, disciplinary attitude towards children."
    ],
    "strong_placement_ta": [
      "சிம்மத்தில் ஆட்சி அல்லது மேஷத்தில் உச்சம் பெற்றால்: புகழ்பெற்ற சந்ததிகள், சமுதாயத்தில் உயரிய ஆலோசனைப் பதவிகள் மற்றும் அரச யோகம்.",
      "முற்பிறவி புண்ணிய பலத்தால் எடுத்த காரியங்கள் யாவிலும் தொடர் வெற்றி மற்றும் செல்வச் செழிப்பு."
    ],
    "strong_placement_en": [
      "Exalted or in own sign: Bestows distinguished, successful children, royal counsel status, and vast good fortune.",
      "Harvests the fruits of past-life merit (Poorvapunya) through intuitive breakthroughs and fame."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் பார்வை இருப்பின்: புத்திர பாக்கியத்தில் காலதாமதம், பிள்ளைகளுடன் கருத்து வேறுபாடு ஏற்படலாம்.",
      "ஊக வணிகம் (Speculation) அல்லது பங்குச் சந்தையில் அவசரப்பட்டு நஷ்டமடையக்கூடும்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Delays or anxieties regarding children, strained relationship with first child.",
      "Heavy losses through impulsive speculative trades or gambling tendencies."
    ],
    "career_wealth_ta": [
      "அரசியல் ஆலோசகர், பேராசிரியர், திட்ட இயக்குநர், நிதி மேலாண்மை, ஆராய்ச்சி மற்றும் கலைத் துறைகளில் சாதனை.",
      "மந்திர, ஜோதிட அல்லது ஆன்மீகத் துறைகளிலும் நல்ல வருமானம் கிட்டும்."
    ],
    "career_wealth_en": [
      "Excels as political strategist, university dean, corporate director, fund manager, and scientific researcher.",
      "Financial success through administrative advisory and intellectual creations."
    ],
    "health_precautions_ta": [
      "வயிற்றுப் பகுதியில் உஷ்ணக் கோளாறுகள், செரிமானக் குறைபாடு மற்றும் அமிலத்தன்மை (Acidity) வரலாம்.",
      "காரமான உணவுகளைத் தவிர்த்து நீர்ச்சத்து மிகுந்த காய்கறிகளை உண்பது நல்லது."
    ],
    "health_precautions_en": [
      "Prone to stomach gastric fires, indigestion, liver sluggishness, and peptic discomfort.",
      "A balanced alkaline diet with abundant fluids is recommended."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 219) & Saravali Ch. 30"
  },
  {
    "planet": "Sun",
    "planet_name_ta": "சூரியன்",
    "symbol": "☀️",
    "element": "தீ (Agni)",
    "house": 6,
    "bhava_category": "dusthana",
    "house_title_ta": "6-ஆம் பாவம் - சத்ரு & ரோக பாவம் (எதிரி ஜெயம் & தைரியம்)",
    "house_title_en": "6th House - Satru & Roga Bhava (Victory Over Foes & Immunity)",
    "core_traits_ta": [
      "எதிரிகளை அடியோடு முறியடிக்கும் பராக்கிரமம்; வழக்குகளிலும் போட்டிகளிலும் வெல்லும் ஆற்றல்.",
      "சூரியன் 6-ஆம் பாவத்தில் அமர்வது மிகச் சிறந்த உபசய பலனாகும்; சவால்களைத் துணிவுடன் தகர்ப்பார்.",
      "கடுமையான உழைப்பாளி; மற்றவர்களுக்குக் கீழ் வேலை செய்வதிலும் தன் ஆளுமையை நிலைநாட்டுவார்.",
      "தாய்மாமனுடன் சில சமயம் கருத்து மோதல்கள் ஏற்படலாம்."
    ],
    "core_traits_en": [
      "Unflinching valor in overcoming opposition; crushes competitors and legal adversaries.",
      "Sun in the 6th is classically celebrated as a powerful Upachaya shield that bestows heroic resilience.",
      "Indefatigable worker with high executive discipline; refuses to succumb under pressure.",
      "May encounter complex relations or boundary disputes with maternal relatives."
    ],
    "strong_placement_ta": [
      "சுப வலுவுடன் இருப்பின்: அரசாங்க உயர் பொறுப்புகள், எதிரிகள் இல்லாத நிம்மதியான வாழ்வு மற்றும் அசைக்க முடியாத சரீர பலம்.",
      "நீதித்துறை, ராணுவம் அல்லது நிர்வாகப் போட்டிகளில் எப்போதும் முதலிடம் பிடிப்பார்."
    ],
    "strong_placement_en": [
      "Strong or exalted: Ensures total conquest of all foes, debt-free prosperity, and ironclad physical immunity.",
      "Commands high authority in civil services, judiciary, military, or labor unions."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாப யோகம் இருப்பின்: தீராத உஷ்ண வியாதிகள், ரத்த சோகை அல்லது கடன் தொல்லைகள் வரலாம்.",
      "வேலையாட்களால் ஏமாற்றப்படுதலும், கண் வலி அல்லது சிறுநீரக பாதிப்புகள் ஏற்பட வாய்ப்புண்டு."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Recurrent febrile conditions, chronic blood impurities, and burdensome debt litigation.",
      "Troubles through subordinates, servants, or hostile workplace rivals."
    ],
    "career_wealth_ta": [
      "மருத்துவம், சட்டம் மற்றும் நீதித்துறை, ஆயுதப் படைகள், வங்கித் துறையில் கடன் மீட்பு மற்றும் தணிக்கைத் துறை.",
      "எதிர்ப்புகளையும் தடைகளையும் தனக்குச் சாதகமாக மாற்றிப் பெரும்பொருள் ஈட்டுவார்."
    ],
    "career_wealth_en": [
      "Thrives in healthcare/surgery, corporate law, forensic auditing, defense, and debt restructuring.",
      "Turns competitive crises into lucrative career breakthroughs and steady financial power."
    ],
    "health_precautions_ta": [
      "வயிற்றுக்கடுப்பு, பித்தக் கோளாறுகள், தொடை மற்றும் இடுப்புப் பகுதியில் வலிகள் வரலாம்.",
      "உடலில் நீரிழப்பு ஏற்படாமல் பார்த்துக் கொள்வதும் சீரான உடற்பயிற்சியும் அவசியம்."
    ],
    "health_precautions_en": [
      "Susceptible to kidney stones, hepatic irritation, lower intestinal inflammation, and skin rashes.",
      "Maintain proper hydration and avoid over-exertion under the hot sun."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 260) & Saravali Ch. 30"
  },
  {
    "planet": "Sun",
    "planet_name_ta": "சூரியன்",
    "symbol": "☀️",
    "element": "தீ (Agni)",
    "house": 7,
    "bhava_category": "kendra",
    "house_title_ta": "7-ஆம் பாவம் - களத்திர பாவம் (வாழ்க்கைத் துணை & கூட்டுத்தொழில்)",
    "house_title_en": "7th House - Kalathra Bhava (Spouse & Partnerships)",
    "core_traits_ta": [
      "வாழ்க்கைத் துணையிடம் ஆதிக்கமும் மேலாதிக்கப் போக்கும் செலுத்தும் குணம்; தன் சொல்லே எடுபட வேண்டும் என்ற எண்ணம்.",
      "வெளிப்படையான மற்றும் கம்பீரமான ஆளுமை; பிறரை எளிதில் ஈர்க்கும் தகைமை.",
      "திருமண வாழ்வில் ஈகோ (Ego) மோதல்கள் வராமல் கவனமாகப் பேண வேண்டியது அவசியம்.",
      "தொழில் கூட்டாளிகளுடன் ஒப்பந்தங்களில் கண்டிப்பும் வெளிப்படைத்தன்மையும் கொண்டிருப்பார்."
    ],
    "core_traits_en": [
      "Authoritative attitude towards spouse; desires to be the dominant guiding voice in matrimonial ties.",
      "Possesses a regal demeanor that naturally attracts public attention and social recognition.",
      "Requires conscious management of pride and ego to maintain harmonious marital peace.",
      "Demands absolute transparency and formal protocol in business joint ventures."
    ],
    "strong_placement_ta": [
      "சுப கிரகங்களின் சேர்க்கை அல்லது ஆட்சி/உச்சம் பெற்றால்: புகழ்பெற்ற, வசதியான குடும்பத்திலிருந்து வாழ்க்கைத் துணை அமைவார்.",
      "வெளிநாட்டு வர்த்தகங்களிலும், பொது அமைப்புகளிலும் மாபெரும் மதிப்பும் வருமானமும் கிட்டும்."
    ],
    "strong_placement_en": [
      "Well-aspected or exalted: Partner comes from an honorable, prosperous, and high-status family background.",
      "Brings remarkable prestige and fiscal windfalls through foreign trade and diplomatic missions."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் தாக்கம் இருப்பின்: திருமண வாழ்வில் மனக்கசப்புகள், காலதாமதமான திருமணம் அல்லது தற்காலிகப் பிரிவு.",
      "கூட்டுத் தொழிலில் பார்ட்னர்களால் ஏமாற்றப்படுதலும் அரசுத் தடைகளும் உண்டாகலாம்."
    ],
    "weak_placement_en": [
      "Afflicted or debilitated: Marital friction, domestic estrangement, delayed nuptials, or spousal health challenges.",
      "Disputes and unexpected financial losses in commercial partnerships."
    ],
    "career_wealth_ta": [
      "பொது நிர்வாகம், அரசியல் பிரதிநிதித்துவம், ஏற்றுமதி-இறக்குமதி, சட்ட ஒப்பந்தங்கள் மற்றும் வர்த்தகப் பிரதிநிதித்துவம்.",
      "வாழ்க்கைத் துணையின் வழியே கௌரவமும் அதிர்ஷ்டமும் சேர்ந்து வரக்கூடும்."
    ],
    "career_wealth_en": [
      "Success in international diplomacy, foreign commerce, contract negotiation, corporate lobbying, and public arbitration.",
      "Potential for substantial financial advancement through marriage and strategic alliances."
    ],
    "health_precautions_ta": [
      "சிறுநீரகக் கோளாறுகள், அடிவயிற்று வலி, நீரிழிவு அல்லது தாம்பத்திய உறுப்புகளில் உஷ்ணம் உண்டாகலாம்.",
      "முறையான ஓய்வும் மருத்துவப் பரிசோதனைகளும் அவசியமாகும்."
    ],
    "health_precautions_en": [
      "Vulnerability to renal imbalances, urinary tract irritation, and groin area heat.",
      "Adequate hydration and periodic reproductive health monitoring are advised."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Sun",
    "planet_name_ta": "சூரியன்",
    "symbol": "☀️",
    "element": "தீ (Agni)",
    "house": 8,
    "bhava_category": "dusthana",
    "house_title_ta": "8-ஆம் பாவம் - ஆயுள் பாவம் (அஷ்டம ஸ்தானம் & மறைமுக ஞானம்)",
    "house_title_en": "8th House - Ayur Bhava (Longevity, Legacies & Occult Secrets)",
    "core_traits_ta": [
      "ஆழமான மறைபொருள் ஞானம், ஆன்மீக ரகசியங்களை ஆராயும் ஆர்வம் மற்றும் கூரிய உள்ளுணர்வு கொண்டவர்.",
      "வாழ்க்கையில் திடீர் திருப்பங்களையும், எதிர்பாராத அதிர்ஷ்டங்களையும் அல்லது திடீர் சரிவுகளையும் சந்திப்பார்.",
      "தன்னம்பிக்கை குறையாமல் நெருக்கடிகளில் சாதிக்கும் மன உறுதி; தன் பலவீனங்களை வெளிக்காட்டாதவர்.",
      "அரசாங்க வழியிலோ அல்லது வரி விவகாரங்களிலோ எச்சரிக்கையுடன் இருக்க வேண்டும்."
    ],
    "core_traits_en": [
      "Deep fascination with esoteric mysteries, research, astrology, and the metaphysics of life and death.",
      "Experiences dramatic life fluctuations, sudden windfalls, or sudden structural crises.",
      "Maintains a stoic, secretive composure during turbulent storms; masks emotional vulnerabilities.",
      "Must maintain strict compliance in taxation and governmental statutory matters."
    ],
    "strong_placement_ta": [
      "சுப பலம் பெற்றால்: நீண்ட ஆயுள், எதிர்பாராத உயில் சொத்துகள், காப்பீடு அல்லது மனைவி வழியில் தன வரவு.",
      "அஷ்டம சனியின் தாக்கத்தைக் குறைத்து ஆன்மீக முக்தி நிலையை நோக்கிப் பயணிக்கும் ஆற்றல்."
    ],
    "strong_placement_en": [
      "Well-placed or strong: Grants long life, handsome insurance or legacy inheritances, and spousal dowry benefits.",
      "Endows deep occult mastery and ability to survive critical physical perils."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாப தொடர்புகள் இருப்பின்: கண் பார்வைக் குறைபாடு, திடீர் விபத்துகள் அல்லது அரசாங்க அபராதங்கள்.",
      "தந்தைக்கு அற்பாயுள் அல்லது தந்தையுடன் நீண்ட காலப் பிரிவு ஏற்பட வாய்ப்புண்டு."
    ],
    "weak_placement_en": [
      "Afflicted or debilitated: Impaired eyesight, head injuries, government tax penalties, or sudden disgrace.",
      "Paternal health complications or early estrangement from the father."
    ],
    "career_wealth_ta": [
      "புலனாய்வுத் துறை, தொல்பொருள் ஆராய்ச்சி, தடயவியல், சுரங்கத் தொழில், ஆயுள் காப்பீடு மற்றும் மெட்டபாலிசம் சார்ந்த மருத்துவம்.",
      "மறைமுக சொத்துகள் மற்றும் திடீர் நிதி ஒதுக்கீடுகள் மூலம் பண வரவு."
    ],
    "career_wealth_en": [
      "Thrives in forensic investigation, archaeology, petroleum/mining exploration, life insurance, and toxicology.",
      "Gains wealth through settlement claims, legacies, and hidden financial assets."
    ],
    "health_precautions_ta": [
      "தலைக் காயம், இருதய பலவீனம், கண் புரை அல்லது அதிக உஷ்ணக் கட்டிகள் வரலாம்.",
      "வாகனம் ஓட்டும்போது அதிக கவனம் தேவை; கண்களைப் பரிசோதித்துக் கொள்ளவும்."
    ],
    "health_precautions_en": [
      "Prone to sudden head trauma, high febrile attacks, chronic eye defects, and cardiovascular strain.",
      "Cautious driving habits and preventive ocular care are recommended."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Sun",
    "planet_name_ta": "சூரியன்",
    "symbol": "☀️",
    "element": "தீ (Agni)",
    "house": 9,
    "bhava_category": "trikona",
    "house_title_ta": "9-ஆம் பாவம் - பாக்கிய பாவம் (தர்மம், தந்தை & குரு அருள்)",
    "house_title_en": "9th House - Bhagya Bhava (Fortune, Father, Dharma & Grace)",
    "core_traits_ta": [
      "உயரிய தர்ம சிந்தனை, நேர்மை, தெய்வ பக்தி மற்றும் பெரியோர்களை மதிக்கும் உன்னத சுபாவம்.",
      "தந்தையின் மீது அளப்பரிய மரியாதையும் அவர் வழியில் நற்பெயரைக் காக்கும் கடமையும் கொண்டவர்.",
      "ஆன்மீகத் திருத்தலப் பயணங்கள், தர்ம காரியங்கள் செய்வதில் பேரானந்தம் அடைவார்.",
      "சமுதாயத்தில் மதிப்பிற்குரிய வழிகாட்டியாகவும் ஆசானாகவும் விளங்குவார்."
    ],
    "core_traits_en": [
      "High philosophical nobility, pious disposition, unwavering ethics, and deep reverence for preceptors.",
      "Holds paternal heritage in high esteem and strives to preserve family ancestral honors.",
      "Fond of sacred pilgrimages, charitable endowments, and exploring world philosophies.",
      "Naturally rises as an esteemed moral counselor and inspiring guide in society."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: பரம்பரைச் செல்வம், தந்தை நீண்ட ஆயுளுடன் உயர் பதவியில் இருத்தல், அளப்பரிய பாக்கியம்.",
      "அரசு விருதுகள், ஆன்மீக பீடாதிபதிகளின் ஆசி மற்றும் வாழ்நாள் முழுவதும் குறைவற்ற செல்வம்."
    ],
    "strong_placement_en": [
      "Exalted or own house: Bestows radiant fortune, noble and long-lived father, and royal dignities.",
      "Blessings from spiritual gurus, government honors, and perpetual financial grace."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாப தாக்கங்கள் இருப்பின்: தந்தையின் உடல்நலம் பாதித்தல், தந்தையுடன் கருத்து வேறுபாடுகள்.",
      "முன்னோர்களின் புண்ணியம் குறைந்து தர்ம காரியங்களில் தடைகளும் அவப்பெயரும் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Paternal health reversals, ideological clashes with father, and religious skepticism.",
      "Obstacles in higher studies and potential disappointment in legal or spiritual proceedings."
    ],
    "career_wealth_ta": [
      "நீதிபதி, வழக்கறிஞர், அறக்கட்டளைத் தலைவர், பல்கலைக்கழக வேந்தர், சர்வதேசத் தூதர் மற்றும் ஆன்மீக விரிவுரையாளர்.",
      "தர்ம வழியில் சேர்க்கும் நிலையான சொத்துகள் மற்றும் வெளிநாட்டு தொடர்புகளால் ஆதாயம்."
    ],
    "career_wealth_en": [
      "Distinguished success as magistrate, legal luminary, university dean, religious trustee, or diplomat.",
      "Builds honorable wealth through ethical enterprises, foundations, and cross-border projects."
    ],
    "health_precautions_ta": [
      "தொடைப் பகுதியில் வலி, இடுப்பு நரம்புத் தளர்ச்சி (Sciatica) மற்றும் கல்லீரல் உஷ்ணம் ஏற்படலாம்.",
      "நடைப்பயிற்சியும், முறையான ஆன்மீக விரதங்களும் ஆரோக்கியத்திற்குப் பலம் சேர்க்கும்."
    ],
    "health_precautions_en": [
      "Prone to femoral fatigue, sciatica nerve sensitivity, and hepatic heat.",
      "Regular stretching, walking regimens, and sattvic diet optimize vitality."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Sun",
    "planet_name_ta": "சூரியன்",
    "symbol": "☀️",
    "element": "தீ (Agni)",
    "house": 10,
    "bhava_category": "kendra",
    "house_title_ta": "10-ஆம் பாவம் - ஜீவன பாவம் (திக்பலம் / அரசு அதிகாரம் & கீர்த்தி)",
    "house_title_en": "10th House - Karma Bhava (Digbala / Supreme Career, Power & Fame)",
    "core_traits_ta": [
      "சூரியன் 10-ஆம் பாவத்தில் திக்பலம் (Digbala) பெற்று அமர்வது மாபெரும் ராஜயோக அமைப்பாகும்.",
      "அரசு அதிகாரம், தலைமை ஆளுமை, கம்பீரம் மற்றும் ஆயிரக்கணக்கான மக்களை வழிநடத்தும் திறன்.",
      "தொழிலில் அசைக்க முடியாத தன்னம்பிக்கை; தோல்விகளை வெற்றிகளாக மாற்றும் துணிவு.",
      "கீர்த்தி, புகழ் மற்றும் சமுதாயத்தின் உச்சாணிக் கொம்பில் அமரும் உயர்நிலை."
    ],
    "core_traits_en": [
      "Sun attains absolute Digbala (directional strength) in the 10th house, generating a supreme Raja Yoga.",
      "Natural commanding authority, visionary administrative genius, and effortless executive leadership.",
      "Unyielding confidence in professional pursuits; turns adversity into triumph.",
      "Garlands the native with widespread fame, royal favors, and premier public stature."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்று திக்பலத்துடன் திகழின்: நாட்டின் மிக உயர்ந்த ஆட்சிப் பதவிகள், ஐ.ஏ.எஸ்/ஐ.பி.எஸ் அல்லது கேபினட் அந்தஸ்து.",
      "தொழிலில் மாபெரும் சாம்ராஜ்யம் அமைத்து சரித்திரத்தில் இடம்பிடிக்கும் சாதனையாளராகத் திகழ்வார்."
    ],
    "strong_placement_en": [
      "Exalted or in own sign with Digbala: Crown administrative posts, ministerial positions, or top corporate chairmanships.",
      "Builds a monumental professional empire and earns enduring historical acclaim."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: உயர் அதிகாரிகளால் வீண் தொல்லைகள், உத்தியோகத்தில் திடீர் இடமாற்றம்.",
      "அரசியல் பகைகளும் பொது வாழ்வில் நற்பெயருக்கு களங்கமும் ஏற்பட வாய்ப்புண்டு."
    ],
    "weak_placement_en": [
      "Debilitated or heavily afflicted: Sudden political fall, conflict with government regulators, and professional demotion.",
      "Public scandals and hurdles in career advancement despite high intellectual capacity."
    ],
    "career_wealth_ta": [
      "அரசாங்கத் தலைமைப் பதவிகள், நீதித்துறைத் தலைமை, அரசியல் தலைவர்கள், பெருநிறுவன மேலாண்மை இயக்குநர்கள்.",
      "அதிகார பலத்தாலும் தொழில் மேன்மையாலும் அள்ள அள்ளக் குறையாத தன வரவும் அரச மரியாதையும்."
    ],
    "career_wealth_en": [
      "Prime minister/cabinet ranks, supreme judiciary, CEO/managing directors of conglomerates, defense chiefs.",
      "Vast financial empire generated directly from authoritative executive command."
    ],
    "health_precautions_ta": [
      "அதிக பணிச்சுமையால் ரத்த அழுத்தம், தூக்கமின்மை, மூட்டு வலி மற்றும் உஷ்ணக் கோளாறுகள்.",
      "தவறாமல் ஓய்வெடுத்தலும் தியானமும் உடல் சமநிலையைக் காக்கும்."
    ],
    "health_precautions_en": [
      "Occupational stress, hypertension, insomnia, knee strain, and metabolic heat.",
      "Daily meditation and mandatory work-life balance boundaries are essential."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Sun",
    "planet_name_ta": "சூரியன்",
    "symbol": "☀️",
    "element": "தீ (Agni)",
    "house": 11,
    "bhava_category": "upachaya",
    "house_title_ta": "11-ஆம் பாவம் - லாப பாவம் (அகண்ட தன லாபம் & உயர் நட்பு)",
    "house_title_en": "11th House - Labha Bhava (Abundant Gains & Influential Network)",
    "core_traits_ta": [
      "எண்ணிய எண்ணங்கள் யாவும் நிறைவேறும் அதிர்ஷ்டம்; உபசய ஸ்தானத்தில் சூரியன் அமர்வது பெரும் தன லாபத்தைத் தரும்.",
      "செல்வாக்கு மிக்க மனிதர்கள், அரசியல் பிரமுகர்கள் மற்றும் அரசாங்க உயர் அதிகாரிகளின் நட்பு கிட்டும்.",
      "தன்னம்பிக்கை, நேர்மை மற்றும் சுதந்திரமான உழைப்பால் செல்வத்தைச் சேர்க்கும் ஆர்வம்.",
      "மூத்த சகோதரர்களிடம் அன்பும் அதே சமயம் சில கருத்து வேறுபாடுகளும் ஏற்படலாம்."
    ],
    "core_traits_en": [
      "Fulfillment of cherished long-term aspirations; Sun in the 11th is a classic guarantor of steady financial growth.",
      "Builds an elite network with statesmen, industry titans, and influential administrative leaders.",
      "Self-made magnate who cherishes financial autonomy and upright business ethics.",
      "Affectionate yet independently minded relationship with elder siblings."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: பல வழிகளிலிருந்து கோடிக் கணக்கில் வருமானம், அசைக்க முடியாத செல்வச் செழிப்பு.",
      "சமூகத்தில் பெரும் கௌரவப் பதவிகள், வாகனங்கள் மற்றும் ஆடம்பர வாழ்க்கை வசதிகள் அமையும்."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Bestows immense multi-channel revenue streams, monumental liquid wealth, and luxury assets.",
      "Appointed to prestigious public boards and celebrated for grand philanthropic benevolence."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாப சேர்க்கை பெற்றால்: நண்பர்களால் ஏமாற்றப்படுதல், எதிர்பார்க்கும் லாபத்தில் காலதாமதம்.",
      "மூத்த சகோதரருடன் சொத்து தகராறுகள் அல்லது பிரிவுகள் ஏற்படக்கூடும்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Exploitation by unreliable associates, delayed business receivables, and fiscal bottlenecks.",
      "Estrangement or legal disputes with elder siblings over ancestral partitions."
    ],
    "career_wealth_ta": [
      "பெரு நிறுவன வர்த்தகம், நிதி ஆலோசகர், அரசாங்க ஒப்பந்தங்கள், பொது நிறுவனப் பங்குகள் மற்றும் ரியல் எஸ்டேட்.",
      "குறைந்த முதலீட்டில் பெரும் லாபம் ஈட்டும் வர்த்தகச் சாதுரியம்."
    ],
    "career_wealth_en": [
      "Thrives in venture capitalism, state procurement contracts, corporate finance, equity markets, and industrial scaling.",
      "Exceptional skill in multiplying capital through high-level social leverage."
    ],
    "health_precautions_ta": [
      "இடது காது கேளாமை அல்லது வலி, கணுக்கால் வலி, ரத்த ஓட்டக் குறைபாடுகள் வரலாம்.",
      "கால் தசைகளுக்கான உடற்பயிற்சியும், காது ஆரோக்கியமும் முக்கியம்."
    ],
    "health_precautions_en": [
      "Vulnerable to left-ear infections, ankle sprains, and sluggish peripheral blood circulation.",
      "Calf stretching and routine otic checkups are beneficial."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Sun",
    "planet_name_ta": "சூரியன்",
    "symbol": "☀️",
    "element": "தீ (Agni)",
    "house": 12,
    "bhava_category": "dusthana",
    "house_title_ta": "12-ஆம் பாவம் - விரய பாவம் (மோட்சம், வெளிநாட்டு வாழ்க்கை & ஆன்மீகம்)",
    "house_title_en": "12th House - Vraya & Moksha Bhava (Liberation, Foreign Lands & Expenses)",
    "core_traits_ta": [
      "தனிமையை விரும்பும் அமைதியான சுபாவம்; உலக மாயைகளிலிருந்து விடுபடும் ஆன்மீக நாட்டம்.",
      "பிறந்த ஊரை விட்டுத் தொலைதூரத்திலோ அல்லது வெளிநாடுகளிலோ வாழ்வதில் அனுகூலம்.",
      "பணத்தை தர்ம காரியங்களுக்கும் ஆன்மீக திருப்பணிகளுக்கும் தாராளமாகச் செலவிடும் மனப்பான்மை.",
      "அரசாங்க விவகாரங்களில் அல்லது அதிகாரிகளிடம் பேசும்போது அடக்கத்தைக் கடைப்பிடிப்பது நல்லது."
    ],
    "core_traits_en": [
      "Introspective temperament, loves solitude, and harbors an instinctive yearning for spiritual transcendence.",
      "Remarkable prosperity and peaceful life when settled far away from birthplace or in foreign lands.",
      "Spends generously on noble charities, temple construction, and philosophical institutions.",
      "Must practice diplomatic restraint to avoid confrontations with governmental authorities."
    ],
    "strong_placement_ta": [
      "சுப தொடர்புகளுடன் இருப்பின்: வெளிநாட்டில் மாபெரும் அரசு கௌரவம், பன்னாட்டு நிறுவனங்களில் உயர் பதவி மற்றும் மோட்ச சாதனை.",
      "சுயமரியாதையுடன் கூடிய அமைதியான வாழ்க்கை மற்றும் ஆன்மீக முதிர்ச்சி."
    ],
    "strong_placement_en": [
      "Well-placed with benefics: High diplomatic standing abroad, executive tenure in multinational agencies, and spiritual enlightenment.",
      "Attains tranquil detachment and honorable status in far-flung territories."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: விரயச் செலவுகள், தந்தைக்கு நஷ்டம், கண் பார்வைக் குறைபாடு.",
      "அரசாங்க அபராதங்கள், வழக்குகளால் நிம்மதியின்மை அல்லது தூக்கமின்மை ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Excessive expenditure, financial drains on behalf of father, and defective left eye.",
      "Susceptible to penalties from tax authorities, confinement, or persistent sleep disorders."
    ],
    "career_wealth_ta": [
      "தூதரகப் பணிகள், வெளிநாட்டு வர்த்தகம், கப்பல் போக்குவரத்து, மருத்துவமனை நிர்வாகம், ஆன்மீக மடாலயங்கள்.",
      "அந்நிய தேசத்து கரன்சி மூலம் வருவாய் பெருகுதல்."
    ],
    "career_wealth_en": [
      "Flourishes in diplomatic consulates, international shipping, sanatorium/hospital administration, and spiritual retreats.",
      "Financial inflow derived predominantly from foreign currencies and distant shores."
    ],
    "health_precautions_ta": [
      "இடது கண் பாதிப்பு, பாதங்களில் வலி, தூக்கமின்மை (Insomnia) மற்றும் உடல் சோர்வு.",
      "தூங்குவதற்கு முன் தியானம் செய்தலும் கண்களைக் குளிர்ந்த நீரால் கழுவுவதும் நலம் தரும்."
    ],
    "health_precautions_en": [
      "Left eye sensitivities, foot ailments, chronic sleeplessness, and general physical exhaustion.",
      "Nightly grounding meditation, eye relaxation, and consistent sleep hygiene are indicated."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Moon",
    "planet_name_ta": "சந்திரன்",
    "symbol": "🌙",
    "element": "நீர் (Jala)",
    "house": 1,
    "bhava_category": "kendra",
    "house_title_ta": "1-ஆம் பாவம் - லக்னம் (மனோ பாவம் / காந்தக் கவர்ச்சி)",
    "house_title_en": "1st House - Ascendant / Tanu Bhava (Mind & Magnetic Charm)",
    "core_traits_ta": [
      "வசீகரமான தோற்றம், மென்மையான கண்கள் மற்றும் அனைவரையும் ஈர்க்கும் காந்தக் கவர்ச்சி உடையவர்.",
      "கற்பனைத் திறன், உணர்ச்சிப் பெருக்கு மற்றும் கவிதை/கலைகளில் ஆழ்ந்த ஈடுபாடு கொண்டவர்.",
      "மனநிலை அடிக்கடி மாறும் சுபாவம்; சந்திரனின் வளர்-தேய் நிலைகளைப் போல எண்ணங்களில் ஏற்ற இறக்கங்கள் இருக்கும்.",
      "பயணங்களை மிகவும் விரும்புவார்; புதிய இடங்களையும் மனிதர்களையும் சந்திப்பதில் அலாதி பிரியம்.",
      "மக்கள் செல்வாக்கு எளிதில் கிட்டும்; பொதுவாழ்வில் பெரும் ஆதரவு பெறுவார்."
    ],
    "core_traits_en": [
      "Charming physical appearance, soft luminous eyes, and an instinctively magnetic aura.",
      "High poetic imagination, artistic sensitivity, romantic idealism, and emotional depth.",
      "Fluctuating mental temperament echoing lunar waxing and waning cycles; prone to mood shifts.",
      "Passionate traveler and explorer, thriving on variety and social change.",
      "Commands widespread popularity and connects effortlessly with the masses."
    ],
    "strong_placement_ta": [
      "ரிஷபத்தில் உச்சம் அல்லது கடகத்தில் ஆட்சி பெற்று வளர்பிறை சந்திரனாக இருப்பின்: நீண்ட ஆயுள், அரச போக வாழ்க்கை மற்றும் அசைக்க முடியாத மக்கள் செல்வாக்கு.",
      "குருவின் சேர்க்கை (கஜகேசரி யோகம்) பெற்றால்: அறிவுக் களஞ்சியமாகவும், செல்வந்தராகவும் திகழ்வார்."
    ],
    "strong_placement_en": [
      "Exalted in Taurus, in own sign Cancer, or Full Waxing Moon: Confers aristocratic lifestyle, immense public acclaim, and serene longevity.",
      "In Gajakesari Yoga with Jupiter: Becomes a renowned intellectual luminary and wealthy community leader."
    ],
    "weak_placement_ta": [
      "விருச்சிகத்தில் நீசம் அல்லது தேய்பிறைச் சந்திரன், ராகு/சனியின் சேர்க்கை பெற்றால்: மன உளைச்சல், அதீத பயம், நரம்புத் தளர்ச்சி மற்றும் சளித் தொல்லைகள்.",
      "முடிவெடுக்க முடியாமல் தடுமாறுதல் மற்றும் பிறர் சொல்லைக் கேட்டு குழம்புதல்."
    ],
    "weak_placement_en": [
      "Debilitated in Scorpio, waning, or conjunct Saturn/Rahu: Chronic anxiety, melancholia, phobias, and emotional volatility.",
      "Difficulty in firm decision-making; highly susceptible to external mental manipulation."
    ],
    "career_wealth_ta": [
      "பொதுமக்கள் தொடர்பு, திரவப் பொருட்கள், பால் பண்ணை, ஹோட்டல் துறை, நாவலாசிரியர், சினிமா மற்றும் கலைத் துறை.",
      "மக்கள் ஆதரவாலும் வர்த்தகப் பயணங்களாலும் நிலையான தன வரவு."
    ],
    "career_wealth_en": [
      "Success in public relations, maritime trade, hospitality, culinary arts, cinema, literature, and luxury retail.",
      "Accumulates wealth through popular mass appeal and consumer-facing enterprises."
    ],
    "health_precautions_ta": [
      "கபக் கோளாறுகள், ஜலதோஷம், ஆஸ்துமா, ஜீரணக் குறைபாடு மற்றும் பெண்களுக்கு மாதவிடாய் கோளாறுகள் வரலாம்.",
      "குளிர்ந்த உணவுகளையும் பனி பொழிவையும் தவிர்ப்பது நல்லது."
    ],
    "health_precautions_en": [
      "Prone to phlegmatic chills, respiratory sensitivity, water-retention, and menstrual irregularities in women.",
      "Avoid chilled foods, damp environments, and maintain respiratory warmth."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 52) & Saravali Ch. 30"
  },
  {
    "planet": "Moon",
    "planet_name_ta": "சந்திரன்",
    "symbol": "🌙",
    "element": "நீர் (Jala)",
    "house": 2,
    "bhava_category": "panaphara",
    "house_title_ta": "2-ஆம் பாவம் - தன பாவம் (இனிமையான வாக்கு & தனம்)",
    "house_title_en": "2nd House - Dhana Bhava (Sweet Eloquence & Prosperity)",
    "core_traits_ta": [
      "இனிமையான, கனிவான மற்றும் அனைவரையும் வசீகரிக்கும் பேச்சாற்றல் கொண்டவர்.",
      "பெரிய குடும்பம், விருந்தோம்பல் குணம் மற்றும் உறவினர்களை அரவணைத்துச் செல்லும் சுபாவம்.",
      "அழகான முகம், வசீகரமான புன்னகை மற்றும் ஒளிமயமான கண்கள் அமைந்திருக்கும்.",
      "கலைகள், சுவையான உணவுகள் மற்றும் ஆடை ஆபரணங்களின் மீது பேரார்வம் உடையவர்."
    ],
    "core_traits_en": [
      "Possesses a sweet, persuasive, and melodious voice; speaks with comforting kindness.",
      "Enjoys a large, supportive family and delights in gracious domestic hospitality.",
      "Blessed with a pleasant, handsome facial countenance and captivating eyes.",
      "Has refined taste in culinary delicacies, exquisite attire, and aesthetic gems."
    ],
    "strong_placement_ta": [
      "வளர்பிறை சந்திரன் ஆட்சி அல்லது உச்சம் பெற்றால்: பரம்பரை சொத்துகள், நவரத்தினங்கள், வெள்ளி மற்றும் வங்கி சேமிப்புகள் நிரம்பி வழியும்.",
      "வாக்கு பலிதம் உண்டாகும்; இவரது சொல்லுக்கு குடும்பத்திலும் சமுதாயத்திலும் தனி மதிப்பு இருக்கும்."
    ],
    "strong_placement_en": [
      "Waxing Moon in exaltation or own house: Vast liquid wealth, silver, pearls, heirloom jewellery, and substantial bank deposits.",
      "Words carry prophetic authority and persuasive sway in public and family deliberations."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் தாக்கம் பெற்றால்: பேச்சில் குழப்பம், குடும்பத்தில் மனஸ்தாபங்கள் மற்றும் பண விரயங்கள்.",
      "வலது கண்ணில் பார்வைக் குறைபாடு அல்லது பல் வலிகள் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Financial instability, domestic discord, and speech stammer or hesitations.",
      "Prone to right-eye vision impairments and dental sensitivities."
    ],
    "career_wealth_ta": [
      "வங்கி, நிதி நிறுவனம், உணவு மற்றும் பேக்கரி தொழில், நவரத்தின வர்த்தகம், பாடகர், பேச்சாளர் மற்றும் இசைக்கலைஞர்.",
      "சுமுகமான பேச்சாலும் மக்கள் ஆதரவாலும் பெரும் தன லாபம்."
    ],
    "career_wealth_en": [
      "Thrives in banking, culinary entrepreneurship, pearl/gem trading, professional singing, and voiceover arts.",
      "Attracts steady income through charming customer engagement and financial services."
    ],
    "health_precautions_ta": [
      "தொண்டை சளி, டான்சில்ஸ், பல் சொத்தை, முகம் மற்றும் கண்ணில் உஷ்ணக் கட்டிகள் வரலாம்.",
      "வெதுவெதுப்பான நீர் அருந்துதலும் தொண்டை பராமரிப்பும் அவசியம்."
    ],
    "health_precautions_en": [
      "Susceptible to tonsillitis, oral inflammation, dental caries, and right-eye strain.",
      "Warm fluids and regular dental hygiene are strongly encouraged."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 99) & Saravali Ch. 30"
  },
  {
    "planet": "Moon",
    "planet_name_ta": "சந்திரன்",
    "symbol": "🌙",
    "element": "நீர் (Jala)",
    "house": 3,
    "bhava_category": "upachaya",
    "house_title_ta": "3-ஆம் பாவம் - சகஜ பாவம் (கலைத் திறன் & சகோதர நலம்)",
    "house_title_en": "3rd House - Sahaja Bhava (Artistic Flair & Sibling Harmony)",
    "core_traits_ta": [
      "மென்மையான உள்ளமும், கலை ஆர்வமும், சிறந்த எழுத்து மற்றும் தகவல் தொடர்புத் திறனும் உடையவர்.",
      "சகோதர சகோதரிகளிடம் அதிக பாசம் வைத்திருப்பார்; குறிப்பாக பெண் சகோதரிகளால் நன்மை உண்டு.",
      "பயணங்களை மிகவும் விரும்புவார்; அடிக்கடி குறுகிய தூரப் பயணங்கள் மேற்கொள்வார்.",
      "மனதில் தைரியம் இருந்தாலும் சில நேரங்களில் அவசியமற்ற சந்தேகங்களும் தயக்கங்களும் வரலாம்."
    ],
    "core_traits_en": [
      "Artistic mindset, highly talented in creative writing, fine arts, and communicative diplomacy.",
      "Affectionate bond with siblings, with special assistance and goodwill from sisters.",
      "Fond of frequent, picturesque short travels, outings, and changing environments.",
      "Courageous yet emotionally sensitive; occasionally prone to hesitations or mild vacillation."
    ],
    "strong_placement_ta": [
      "வளர்பிறை அல்லது சுப கிரக சேர்க்கை பெற்றால்: கலைத் துறையில் சர்வதேசப் புகழ், சிறந்த எழுத்தாளராக வலம் வருதல், சகோதரர்களால் பெரும் ஆதரவு.",
      "எடுத்த முயற்சிகள் யாவும் சுமுகமாக நிறைவேறி சமுதாயத்தில் நற்பெயர் கிட்டும்."
    ],
    "strong_placement_en": [
      "Strong waxing Moon: International acclaim in literary and performing arts, supportive siblings, and triumphant initiatives.",
      "Attains great social esteem and honors through elegant diplomacy."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாப பார்வை பெற்றால்: சகோதரர்களுடன் மனக்கசப்புகள், கைகளில் வலி, பயணங்களால் வீண் அலைச்சல்.",
      "தைரியக் குறைபாடும் காரணமற்ற அச்சமும் முயற்சிகளில் சுணக்கத்தை ஏற்படுத்தலாம்."
    ],
    "weak_placement_en": [
      "Afflicted or debilitated: Estrangement from siblings, fatigue from fruitless journeys, and upper limb pain.",
      "Lack of inner resolve and unnecessary anxious timidity hampering bold initiatives."
    ],
    "career_wealth_ta": [
      "பத்திரிகைத் துறை, நாவல் மற்றும் கதை எழுதுதல், விளம்பரத் துறை, பயண ஏஜென்சி, தொலைத்தொடர்பு மற்றும் இசை.",
      "எழுத்தாற்றலாலும் புதிய சிந்தனைகளாலும் தன வரவு பெருகும்."
    ],
    "career_wealth_en": [
      "Flourishes in journalism, screenplay writing, travel agency operations, telecommunications, and digital media.",
      "Gains wealth through intellectual and creative expressions."
    ],
    "health_precautions_ta": [
      "கைகளில் நரம்பு வலி, தோள்பட்டை இறுக்கம், காதுகளில் நீர் வடிதல் அல்லது ஜலதோஷம் வரலாம்.",
      "குளிர்காலத்தில் காது மற்றும் தொண்டையை மூடிப் பாதுகாப்பது நல்லது."
    ],
    "health_precautions_en": [
      "Prone to shoulder strain, ear fluid imbalances, and recurring colds.",
      "Keep chest and throat protected during cold weather spells."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 140) & Saravali Ch. 30"
  },
  {
    "planet": "Moon",
    "planet_name_ta": "சந்திரன்",
    "symbol": "🌙",
    "element": "நீர் (Jala)",
    "house": 4,
    "bhava_category": "kendra",
    "house_title_ta": "4-ஆம் பாவம் - மாத்ரு & சுக பாவம் (தாயன்பு, சொத்து & மன அமைதி)",
    "house_title_en": "4th House - Matru & Sukha Bhava (Mother, Comforts & Serenity)",
    "core_traits_ta": [
      "தாயாரின் மீது அளப்பரிய அன்பும், தாயாரின் ஆசியால் வாழ்வில் சகல சௌபாக்கியங்களும் பெறுபவர்.",
      "அமைதியான இல்லற வாழ்க்கை, நற்பண்புகள், தாராள மனப்பான்மை மற்றும் இரக்க சுபாவம் கொண்டவர்.",
      "நீர்நிலைகள், தோட்டங்கள், பசுமையான இடங்கள் மற்றும் ஆடம்பர வீடுகளில் வசிப்பதில் விருப்பம்.",
      "உணர்ச்சிவசப்படும் சுபாவம் கொண்டிருப்பதால் மன நிம்மதிக்கு அதிக முக்கியத்துவம் கொடுப்பார்."
    ],
    "core_traits_en": [
      "Deep filial devotion to mother; receives bountiful maternal blessings and emotional nurturing.",
      "Gracious host, generous philanthropist, and seeks harmonious, aesthetic home sanctuaries.",
      "Loves waterbodies, lush gardens, scenic retreats, and luxurious residential spaces.",
      "Emotionally attuned; prioritizes peace of mind above raw worldly aggression."
    ],
    "strong_placement_ta": [
      "சந்திரன் கடகத்தில் ஆட்சி அல்லது ரிஷபத்தில் உச்சம் பெற்றால்: மாளிகைகள் போன்ற வீடு, சொகுசு வாகனங்கள், தாயார் நீண்ட ஆயுளுடன் இருத்தல்.",
      "மனதில் பூரண அமைதியும், சமுதாயத்தில் உயரிய மதிப்பும் பெற்று சுகவாழ்வு வாழ்வார்."
    ],
    "strong_placement_en": [
      "In Cancer or Taurus: Bestows stately palatial mansions, premium vehicular fleet, and long-lived, noble mother.",
      "Enjoys unperturbed emotional tranquility, refined comforts, and civic honors."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தாயாரின் உடல்நலக்குறைவு, பூர்வீக சொத்துகளில் இழப்பு, வீட்டு சூழலில் அமைதியின்மை.",
      "நெஞ்சு சளி, மன உளைச்சல் மற்றும் அடிக்கடி வீட்டை மாற்ற வேண்டிய கட்டாயம் உண்டாகலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Fragile health of mother, property disputes, and emotional unhappiness at home.",
      "Susceptible to chest congestion, acute melancholy, and frequent changes of residence."
    ],
    "career_wealth_ta": [
      "ரியல் எஸ்டேட், பால் மற்றும் நீர்வழி வர்த்தகம், விவசாயப் பண்ணைகள், உளவியல் ஆலோசனை மற்றும் வாகனத் தொழில்.",
      "தாய்வழிச் சொத்துகளாலும் வீட்டுமனை வர்த்தகத்தாலும் தன வரவு கொழிக்கும்."
    ],
    "career_wealth_en": [
      "Profitable avenues in residential architecture, dairy agriculture, marine logistics, psychology, and luxury hospitality.",
      "Inherits substantial maternal properties and realizes rapid appreciation on real estate."
    ],
    "health_precautions_ta": [
      "நெஞ்சு சளி, நுரையீரல் அலர்ஜி, இருமல் மற்றும் தூக்கமின்மை வரலாம்.",
      "இரவில் அதிக நேரம் விழித்திருப்பதைத் தவிர்த்து ஆழ்ந்த தூக்கம் கொள்வது நலம் பயக்கும்."
    ],
    "health_precautions_en": [
      "Prone to pulmonary congestion, bronchial allergies, and water retention around heart.",
      "Ensure restful sleep patterns and avoid cold nighttime drafts."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 174) & Saravali Ch. 30"
  },
  {
    "planet": "Moon",
    "planet_name_ta": "சந்திரன்",
    "symbol": "🌙",
    "element": "நீர் (Jala)",
    "house": 5,
    "bhava_category": "trikona",
    "house_title_ta": "5-ஆம் பாவம் - புத்திர பாவம் (கற்பனை வளம் & பூர்வ புண்ணியம்)",
    "house_title_en": "5th House - Putra Bhava (Creativity, Progeny & Devotion)",
    "core_traits_ta": [
      "அசாத்தியமான கற்பனை வளம், கவிதை எழுதும் ஆற்றல், கூர்மையான நினைவாற்றல் மற்றும் கலை உணர்வு.",
      "குழந்தைகளிடம் பேரன்பு செலுத்துவார்; நற்குணமும் அழகும் நிறைந்த பெண் குழந்தைகள் அமைய வாய்ப்புண்டு.",
      "தெய்வ பக்தி, தியானம் மற்றும் சாத்வீக வழிபாடுகளில் அதிக ஈடுபாடு காட்டுவார்.",
      "மனதில் தூய்மையான எண்ணங்களும், பிறருக்கு நலம் பயக்கும் ஆலோசனைகளை வழங்கும் பண்பும் உண்டு."
    ],
    "core_traits_en": [
      "Profound creative genius, poetic eloquence, stellar intuitive memory, and aesthetic flair.",
      "Deep affection for children; often blessed with charming, accomplished daughters.",
      "Pious devotional heart, drawn to meditation, mantra sadhana, and sattvic temple worship.",
      "Pure-hearted counselor whose instinctive advice brings healing and solace to others."
    ],
    "strong_placement_ta": [
      "பூர்ண சந்திரன் சுப தொடர்புடன் இருப்பின்: அறிவார்ந்த சந்ததிகள், கலை மற்றும் இலக்கியத்தில் விருதுகள், அரச யோகம்.",
      "பூர்வ புண்ணிய பலத்தால் தொட்டதெல்லாம் பொன்னாகும் யோகமும், திடீர் தன லாபங்களும் கிட்டும்."
    ],
    "strong_placement_en": [
      "Bright waxing Moon: Celebrated, virtuous children, national honors in arts or literature, and royal fortune.",
      "Reaps past-life blessings through effortless creative triumphs and sudden speculative prosperity."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: புத்திர பாக்கியத்தில் கவலைகள், குழந்தைகளின் உடல்நலம் பாதித்தல்.",
      "பங்குச் சந்தை அல்லது ஊக வணிகத்தில் உணர்ச்சிவசப்பட்டு முதலீடு செய்து நஷ்டமடைதல்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Emotional distress regarding children, erratic schooling for progeny.",
      "Financial setbacks through emotional, ill-calculated investments in speculative markets."
    ],
    "career_wealth_ta": [
      "சினிமா இயக்குநர், இசை அமைப்பாளர், எழுத்தாளர், கல்வியாளர், குழந்தைகள் நல மருத்துவர் மற்றும் பங்கு ஆலோசகர்.",
      "கலை படைப்புகள், அறிவுசார் சொத்துரிமை மற்றும் ஆலோசனைகள் மூலம் அபரிமிதமான செல்வம்."
    ],
    "career_wealth_en": [
      "Distinction as film director, composer, literary novelist, child educator, pediatrician, or financial analyst.",
      "Generates wealth through intellectual property, creative royalties, and intuitive advisory."
    ],
    "health_precautions_ta": [
      "செரிமானக் கோளாறுகள், வயிற்றுப் பகுதியில் நீர் கட்டிகள், பித்த நீர் சமநிலையின்மை வரலாம்.",
      "எளிதில் செரிக்கும் சத்தான உணவுகளை வேளைக்கு உண்பது ஆரோக்கியம் தரும்."
    ],
    "health_precautions_en": [
      "Vulnerable to gastric acidity, stomach bloating, lymphatic cysts, and sluggish digestion.",
      "Adopt easily digestible light meals and regular meal timings."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 220) & Saravali Ch. 30"
  },
  {
    "planet": "Moon",
    "planet_name_ta": "சந்திரன்",
    "symbol": "🌙",
    "element": "நீர் (Jala)",
    "house": 6,
    "bhava_category": "dusthana",
    "house_title_ta": "6-ஆம் பாவம் - ரோக பாவம் (நோய் எதிர்ப்பு & பணிவு)",
    "house_title_en": "6th House - Satru & Roga Bhava (Health Care & Diligence)",
    "core_traits_ta": [
      "அமைதியான சுபாவம்; வாக்குவாதங்களையும் நேரடி மோதல்களையும் விரும்புவதில்லை.",
      "பிறருக்கு உதவும் தாராள உள்ளமும், சேவை மனப்பான்மையும், அர்ப்பணிப்புடன் உழைக்கும் குணமும் கொண்டவர்.",
      "மனதில் தேவையில்லாத கவலைகளையும், பயங்களையும் வளர்த்துக்கொண்டு அமைதியை இழக்கக்கூடும்.",
      "தாய்மாமன் அல்லது தாய்வழி உறவினர்களுடன் உறவில் சற்று ஏற்ற இறக்கங்கள் இருக்கலாம்."
    ],
    "core_traits_en": [
      "Gentle, conflict-averse temperament; prefers conciliation over aggressive showdowns.",
      "Compassionate humanitarian spirit, dedicated to humble service and patient diligence.",
      "Prone to psychosomatic worries and internal anxieties that affect general vitality.",
      "Experiences fluctuating dynamics with maternal uncles and domestic servants."
    ],
    "strong_placement_ta": [
      "வளர்பிறை சந்திரனாக இருந்து சுப பார்வை பெற்றால்: நோய்களை வெல்லும் மன உறுதி, கடன்கள் இல்லாத அமைதியான வாழ்க்கை.",
      "மருத்துவத் துறையிலும், சேவை நிறுவனங்களிலும் உயர் பதவிகளை வகித்து நற்பெயர் பெறுவார்."
    ],
    "strong_placement_en": [
      "Waxing Moon with benefic aspects: Robust psychological immunity against disease, debt-free living, and reliable staff.",
      "Attains respected executive standing in medical, public health, or charitable service foundations."
    ],
    "weak_placement_ta": [
      "தேய்பிறை சந்திரன் அல்லது நீசமாக இருப்பின்: தீராத சளி, வயிற்றுப் போக்கு, செரிமானக் கோளாறுகள், ரத்த சோகை.",
      "எதிரிகளால் மறைமுகத் தொல்லைகளும், வேலையாட்களால் நஷ்டமும் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Waning or debilitated: Chronic bronchial catarrh, dysentery, stomach ulcers, and anemia.",
      "Subtle undermining from covert rivals and financial leakages caused by dishonest subordinates."
    ],
    "career_wealth_ta": [
      "செவிலியர் துறை, பார்மசி, சத்துணவு நிபுணர், ஹோட்டல் உணவு வழங்கல், சமூக சேவை மற்றும் கால்நடை பராமரிப்பு.",
      "உழைப்பிற்கேற்ற நியாயமான ஊதியமும், சேவையின் மூலமான நற்பெயரும் கிட்டும்."
    ],
    "career_wealth_en": [
      "Career fulfillment in nursing, pharmaceuticals, dietetics, catering, welfare agencies, and veterinary care.",
      "Earns stable income through honest, compassionate service to people in distress."
    ],
    "health_precautions_ta": [
      "ஜலதோஷம், நுரையீரல் தொற்று, அஜீரணம் மற்றும் நீர் மூலம் பரவும் நோய்கள் வரலாம்.",
      "காய்ச்சிய சுத்தமான குடிநீரை அருந்துவதும், குளிர்ச்சியான உணவுகளைத் தவிர்ப்பதும் அவசியம்."
    ],
    "health_precautions_en": [
      "Prone to pulmonary phlegm, bowel infections, amoebiasis, and waterborne pathogens.",
      "Drink purified boiled water and avoid refrigerated or uncooked street foods."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 261) & Saravali Ch. 30"
  },
  {
    "planet": "Moon",
    "planet_name_ta": "சந்திரன்",
    "symbol": "🌙",
    "element": "நீர் (Jala)",
    "house": 7,
    "bhava_category": "kendra",
    "house_title_ta": "7-ஆம் பாவம் - களத்திர பாவம் (அழகான துணை & பொது ஈர்ப்பு)",
    "house_title_en": "7th House - Kalathra Bhava (Charming Spouse & Public Allure)",
    "core_traits_ta": [
      "அழகான, கனிவான, கவர்ச்சிகரமான குணநலன்கள் கொண்ட வாழ்க்கைத் துணை அமையப் பெறுவார்.",
      "தாம்பத்திய வாழ்வில் ரொமான்ஸ், பரஸ்பர அன்பு மற்றும் பாசம் நிறைந்திருக்கும்.",
      "பொதுமக்கள் தொடர்பில் சிறந்தவர்; வணிக கூட்டாளிகளுடன் சுமுகமாகப் பழகி காரியம் சாதிப்பார்.",
      "அடிக்கடி கடல் கடந்த பயணங்கள் மற்றும் வியாபார நிமித்தமான பயணங்களை மேற்கொள்வார்."
    ],
    "core_traits_en": [
      "Blessed with an attractive, gentle, affectionate, and aesthetically refined spouse.",
      "Enjoys romantic warmth, mutual devotion, and harmonious conjugal bliss.",
      "Natural diplomat in public interactions; builds agreeable, trust-based business alliances.",
      "Fond of overseas voyages, maritime trade, and scenic recreational travels."
    ],
    "strong_placement_ta": [
      "பூர்ண சந்திரன் சுப கிரகங்களுடன் இருப்பின்: அதிர்ஷ்டகரமான செல்வந்த குடும்பத் துணை, திருமணத்திற்குப் பின் அபரிமிதமான வளர்ச்சி.",
      "பன்னாட்டு வர்த்தகத்தில் பெரும் லாபமும், சமூகத்தில் உயர்ந்த தம்பதிகளாகப் போற்றப்படும் நிலையும் கிட்டும்."
    ],
    "strong_placement_en": [
      "Full Moon with benefics: Marries into an affluent, distinguished family; exponential post-marital prosperity.",
      "Reaps huge profits from transnational commerce and enjoys enviable social prestige as an ideal couple."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் தாக்கம் இருப்பின்: துணையின் உடல்நலத்தில் அடிக்கடி பாதிப்பு, மனநிலை ஊசலாட்டங்களால் குடும்பத்தில் சலசலப்பு.",
      "கூட்டுத் தொழிலில் பங்குதாரர்களால் ஏமாற்றப்பட்டு இழப்புகள் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Emotional fragility or health ailments in spouse, moodiness causing marital tension.",
      "Vulnerable to deceit and capital erosion through untrustworthy business partners."
    ],
    "career_wealth_ta": [
      "சுற்றுலாத் துறை, கப்பல் போக்குவரத்து, இறக்குமதி-ஏற்றுமதி, அழகு சாதனப் பொருட்கள், ஆடை வடிவமைப்பு மற்றும் பொது உறவுகள்.",
      "வாழ்க்கைத் துணையின் அதிர்ஷ்டத்தாலும் பொதுமக்கள் செல்வாக்கினாலும் தன லாபம் பெருகும்."
    ],
    "career_wealth_en": [
      "High rewards in hospitality, luxury travel, marine logistics, cosmetics, fashion apparel, and public advocacy.",
      "Financial prosperity augmented substantially through marital fortunes and joint assets."
    ],
    "health_precautions_ta": [
      "சிறுநீரகத் தொற்று, அடிவயிறு மற்றும் பிறப்புறுப்புப் பகுதியில் நீர் வீக்கம், உஷ்ணக் கோளாறுகள்.",
      "முறையான நீர் அருந்துதலும் தனிநபர் சுகாதாரமும் நலம் காக்கும்."
    ],
    "health_precautions_en": [
      "Susceptible to renal congestion, bladder irritations, and pelvic fluid imbalances.",
      "Maintain optimal daily fluid intake and attentive personal hygiene."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Moon",
    "planet_name_ta": "சந்திரன்",
    "symbol": "🌙",
    "element": "நீர் (Jala)",
    "house": 8,
    "bhava_category": "dusthana",
    "house_title_ta": "8-ஆம் பாவம் - ஆயுள் பாவம் (உள்ளுணர்வு & மறைபொருள் நாட்டம்)",
    "house_title_en": "8th House - Ayur Bhava (Intuition, Occult Mysteries & Legacies)",
    "core_traits_ta": [
      "அசாத்தியமான உள்ளுணர்வு (Intuition), கனவுகள் பலிக்கும் ஆற்றல் மற்றும் ஆன்மீக ரகசியங்களில் ஈடுபாடு.",
      "மனதில் ஆழமான உணர்ச்சிகளை மறைத்து வைத்திருக்கும் சுபாவம்; எதையும் வெளிப்படையாகப் பேச மாட்டார்.",
      "வாழ்க்கையில் எதிர்பாராத அதிர்ஷ்டங்களும் அல்லது திடீர் மன அழுத்தங்களும் மாறி மாறி வரலாம்.",
      "நீர்நிலைகளில் செல்லும்போது மிகுந்த எச்சரிக்கையுடன் இருக்க வேண்டும்."
    ],
    "core_traits_en": [
      "Extraordinary intuitive perception, vivid prophetic dreams, and fascination with occult mysteries.",
      "Guarded emotional core; conceals profound internal feelings beneath an enigmatic surface.",
      "Encounters sudden financial windfalls alternating with acute psychological transformations.",
      "Must exercise supreme caution around deep waterbodies and aquatic journeys."
    ],
    "strong_placement_ta": [
      "வளர்பிறை அல்லது சுப பார்வை இருப்பின்: நீண்ட ஆயுள், எதிர்பாராத உயில் சொத்துகள், மனைவியின் வழியில் பெரும் தன வரவு.",
      "ஆழ்ந்த ஆன்மீக ஞானமும், மறைமுக சாஸ்திரங்களில் தேர்ச்சியும் பெற்று பிறருக்கு வழிகாட்டுவார்."
    ],
    "strong_placement_en": [
      "Waxing Moon with benefics: Extended longevity, substantial unearned legacies, and prosperous dowry assets.",
      "Attains mystical enlightenment and deep psychological wisdom, guiding seekers."
    ],
    "weak_placement_ta": [
      "தேய்பிறை அல்லது விருச்சிகத்தில் நீசம் பெற்றால்: மன அழுத்தம் (Depression), நீரில் கண்டம், கண் உபாதைகள்.",
      "தாயாரின் ஆயுளுக்கு பலவீனம் அல்லது தாயை விட்டுப் பிரியும் சூழல் உருவாகலாம்."
    ],
    "weak_placement_en": [
      "Waning or debilitated in Scorpio: Acute mental depression, danger of drowning, ocular weakness.",
      "Fragile vitality for the mother or painful early maternal separation."
    ],
    "career_wealth_ta": [
      "மறைமுகப் புலனாய்வு, ஜோதிடம், ஹிப்னாட்டிசம், உளவியல் சிகிச்சை, ஆயுள் காப்பீடு மற்றும் தொல்பொருள் ஆராய்ச்சி.",
      "திடீர் தன லாபங்கள், பங்குச் சந்தை டிவிடெண்டுகள் மற்றும் உயில் சொத்துகள் மூலம் வரவு."
    ],
    "career_wealth_en": [
      "Success in psychoanalysis, astrology, hypnotherapy, insurance settlements, toxicology, and esoteric research.",
      "Financial windfalls from inherited estates, insurance payouts, and strategic private equity."
    ],
    "health_precautions_ta": [
      "மன அழுத்தம், மூளை நரம்பு பலவீனம், நாள்பட்ட சளி, சிறுநீரகக் கோளாறுகள் மற்றும் நீரிழிவு அபாயம்.",
      "தியானம், பிராணாயாமம் மற்றும் மனநல ஆலோசனைகள் புத்துணர்ச்சி தரும்."
    ],
    "health_precautions_en": [
      "Prone to melancholic depressive states, chronic sinus congestion, and endocrine imbalances.",
      "Daily meditation, breathwork, and emotional grounding practices are essential."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Moon",
    "planet_name_ta": "சந்திரன்",
    "symbol": "🌙",
    "element": "நீர் (Jala)",
    "house": 9,
    "bhava_category": "trikona",
    "house_title_ta": "9-ஆம் பாவம் - பாக்கிய பாவம் (தர்மம், தீர்த்த யாத்திரை & தந்தை)",
    "house_title_en": "9th House - Bhagya Bhava (Fortune, Pilgrimage & Divine Grace)",
    "core_traits_ta": [
      "உன்னதமான தர்ம சிந்தனை, பக்தி, இரக்கம் மற்றும் அனைவராலும் போற்றப்படும் நற்குணங்கள் கொண்டவர்.",
      "புனிதத் தலங்களுக்கு யாத்திரை செல்வதிலும், திருக்குளங்களில் நீராடுவதிலும் அலாதி பிரியம்.",
      "தந்தையின் மீது பாசமும் மரியாதையும் கொண்டவர்; தந்தை வழியில் நன்மைகளும் ஆசிகளும் கிட்டும்.",
      "அதிர்ஷ்டம் நிறைந்த வாழ்வு; இக்கட்டான நேரங்களில் இறைவனின் அருள் கைகொடுத்துக் காப்பாற்றும்."
    ],
    "core_traits_en": [
      "Sublime spiritual piety, deep compassion, ethical uprightness, and universally admired virtues.",
      "Passionate love for pilgrimages to sacred river shrines, holy temples, and spiritual retreats.",
      "Cherishes deep affection for the father; reaps noble paternal heritage and divine blessings.",
      "A genuinely fortunate soul whom serendipitous grace rescues from life's toughest corners."
    ],
    "strong_placement_ta": [
      "பூர்ண சந்திரன் ஆட்சி அல்லது உச்சம் பெற்றால்: அகண்ட பாக்கிய யோகம், அரசாங்க கௌரவம், வற்றாத செல்வம்.",
      "தர்ம ஸ்தாபனங்களை நிறுவுதல், சமுதாயத்தில் உயர்ந்த ஆன்மீகத் தலைவராகப் போற்றப்படுதல்."
    ],
    "strong_placement_en": [
      "Full Moon in strength: Bestows boundless Bhagya Yoga, supreme civic honors, and perennial wealth.",
      "Founding philanthropic trusts, rising as an inspiring philosophical leader across nations."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தந்தையின் உடல்நலக் குறைவு, மத நம்பிக்கைகளில் குழப்பம்.",
      "புனிதப் பயணங்களில் பொருள் இழப்பு அல்லது ஏமாற்றங்கள் ஏற்பட வாய்ப்புண்டு."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Paternal health trials, religious disillusionment, and ideological clashes with mentors.",
      "Loss of baggage or financial deceit during sacred pilgrimages."
    ],
    "career_wealth_ta": [
      "ஆன்மீக அறக்கட்டளைகள், பல்கலைக்கழகப் பேராசிரியர்கள், சட்ட ஆலோசகர்கள், சர்வதேச வர்த்தகம் மற்றும் நூலாசிரியர்கள்.",
      "தர்ம வழியில் ஈட்டும் செல்வமும், வெளிநாட்டு முதலீடுகளால் அபரிமிதமான வளர்ச்சியும்."
    ],
    "career_wealth_en": [
      "Thrives in philanthropic foundations, academic deanships, international jurisprudence, and spiritual literature.",
      "Amasses pure, untainted wealth through principled cross-border commerce."
    ],
    "health_precautions_ta": [
      "தொடை மற்றும் இடுப்புப் பகுதியில் நரம்பு வலி, உடல் சோர்வு மற்றும் செரிமானக் கோளாறுகள்.",
      "மிதமான நடைப்பயிற்சியும் சாத்வீக உணவு முறையும் உடல்நலனைப் பேணும்."
    ],
    "health_precautions_en": [
      "Susceptible to hip stiffness, sciatica sensitivity, and intermittent physical fatigue.",
      "Gentle walking outdoors and a nourishing sattvic diet preserve long-term vitality."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Moon",
    "planet_name_ta": "சந்திரன்",
    "symbol": "🌙",
    "element": "நீர் (Jala)",
    "house": 10,
    "bhava_category": "kendra",
    "house_title_ta": "10-ஆம் பாவம் - ஜீவன பாவம் (மக்கள் செல்வாக்கு & தொழில் மேன்மை)",
    "house_title_en": "10th House - Karma Bhava (Mass Popularity & Professional Glory)",
    "core_traits_ta": [
      "மக்கள் மத்தியில் அளப்பரிய செல்வாக்கும், நற்பெயரும், உயர்ந்த தொழில் நிலையும் உடையவர்.",
      "எந்தத் துறையிலும் முன்னணியில் நிற்கும் தலைமைப் பண்பும், சுறுசுறுப்பும் கொண்ட செயல்வீரர்.",
      "அரசாங்க ஆதரவு, பொதுமக்களின் ஏகோபித்த அன்பு மற்றும் கௌரவப் பதவிகள் எளிதில் கிட்டும்.",
      "தன் தொழில் மூலம் பல்லாயிரக்கணக்கான மக்களுக்கு வேலைவாய்ப்பும் நன்மையும் செய்வார்."
    ],
    "core_traits_en": [
      "Enormous public acclaim, immaculate professional repute, and elevated occupational stature.",
      "Energetic dynamism, natural flair for leadership, and decisive organizational execution.",
      "Commands governmental patronage, civic adoration, and prestigious chairmanships.",
      "Builds enterprises that provide livelihood and benevolent welfare to hundreds of families."
    ],
    "strong_placement_ta": [
      "பூர்ண சந்திரன் சுப பலத்துடன் இருப்பின்: அமைச்சரவை யோகம், பெருநிறுவனத் தலைவர் அந்தஸ்து, அழியாத புகழ்.",
      "தொழிலில் அசைக்க முடியாத சாம்ராஜ்யத்தை நிறுவி சமூகத்தின் வழிகாட்டியாகத் திகழ்வார்."
    ],
    "strong_placement_en": [
      "Bright Moon with strength: Confers ministerial portfolios, CEO status of mega-corporations, and timeless fame.",
      "Constructs an unshakeable commercial empire and serves as a celebrated icon of industry."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தொழிலில் அடிக்கடி மாற்றங்கள், பொது வாழ்வில் அவப்பெயர்.",
      "உயர் அதிகாரிகளால் நெருக்கடிகளும், வியாபாரத்தில் நிலையற்ற தன்மையும் உண்டாகலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Occupational instability, sudden public fall from grace, and emotional burnout.",
      "Frequent erratic job switches and unmerited criticism from civic regulators."
    ],
    "career_wealth_ta": [
      "அரசியல், மக்கள் தொடர்பு, மருத்துவம், ஹோட்டல் மற்றும் சுற்றுலா, கப்பல் போக்குவரத்து, திரவப் பொருட்கள் வர்த்தகம்.",
      "மக்கள் ஆதரவாலும் தொழில் மேன்மையாலும் கோடிக் கணக்கில் செல்வம் சேரும்."
    ],
    "career_wealth_en": [
      "Stellar career in statesmanship, public administration, healthcare, maritime logistics, and hospitality.",
      "Multi-million liquid capital generated via widespread customer trust and civic goodwill."
    ],
    "health_precautions_ta": [
      "மூட்டு வலி, பணிச்சுமையால் தூக்கமின்மை, மன அழுத்தம் மற்றும் கபத் தொல்லைகள்.",
      "வேலைக்கு நடுவே தகுந்த ஓய்வும், தியானப் பயிற்சிகளும் மிகவும் அவசியம்."
    ],
    "health_precautions_en": [
      "Vulnerable to knee joint stiffness, occupational sleep deprivation, and psychosomatic tension.",
      "Pace work rhythms mindfully and engage in restful evening relaxation rituals."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Moon",
    "planet_name_ta": "சந்திரன்",
    "symbol": "🌙",
    "element": "நீர் (Jala)",
    "house": 11,
    "bhava_category": "upachaya",
    "house_title_ta": "11-ஆம் பாவம் - லாப பாவம் (அனைத்து விருப்பங்களும் நிறைவேறுதல்)",
    "house_title_en": "11th House - Labha Bhava (Abundant Gains & Wish Fulfillment)",
    "core_traits_ta": [
      "தொட்ட காரியங்களில் எல்லாம் லாபம், ஆசைகள் யாவும் நிறைவேறுதல் மற்றும் நிலையான பொருளாதார உயர்வு.",
      "உயர் அந்தஸ்து படைத்த பெண்களின் நட்பும் ஆதரவும் வாழ்வின் உயர்வுக்குப் பெரிதும் உதவும்.",
      "தாராள மனப்பான்மை, விருந்தோம்பல் குணம் மற்றும் சமூகத்தில் பல நண்பர்களைக் கொண்டிருப்பார்.",
      "மூத்த சகோதர சகோதரிகளுடன் அன்பான இணக்கமும் அவர்களால் நன்மைகளும் கிட்டும்."
    ],
    "core_traits_en": [
      "Boundless prosperity, steady streams of revenue, and smooth realization of cherished ambitions.",
      "Enjoys beneficial patronage and enduring friendship from influential, noble women.",
      "Magnanimous, hospitable, and surrounded by a vast network of loyal, supportive associates.",
      "Deeply fulfilling companionship with elder siblings who foster career elevation."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்று பூர்ண சந்திரனாக இருப்பின்: கணக்கிலடங்கா செல்வம், சொகுசு வாகனங்கள், சமூகத்தின் முதன்மை அந்தஸ்து.",
      "பல வழிகளிலிருந்து தொடர் வருமானம் வந்து வங்கி இருப்பு எப்போதும் பெருகிக் கொண்டே இருக்கும்."
    ],
    "strong_placement_en": [
      "Bright Moon in Taurus/Cancer: Tremendous wealth accumulation, fleet of luxury cars, and premier social rank.",
      "Unceasing multi-faceted financial inflows ensuring massive liquidity and asset appreciation."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: நண்பர்களால் ஏமாற்றப்பட்டு தன நஷ்டம், மூத்த சகோதரருடன் பிரிவு.",
      "லாபங்கள் கைக்கு எட்டும் நேரத்தில் நழுவிப் போதல் அல்லது பண விரயங்கள் ஏற்படுதல்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Exploitation by counterfeit friends, financial leakages, and sibling estrangement.",
      "Anticipated dividends slip away at the last moment due to bad timing or misjudgment."
    ],
    "career_wealth_ta": [
      "நிதி நிறுவனங்கள், பங்குச் சந்தை, ஏற்றுமதி வர்த்தகம், உணவு மற்றும் பானங்கள், ரத்தின வர்த்தகம், சமூக வலைப்பின்னல்கள்.",
      "குறைந்த உழைப்பில் அபரிமிதமான லாபம் ஈட்டும் வணிகத் திறமை."
    ],
    "career_wealth_en": [
      "Lucrative success in fintech, stock brokerage, food commodities, gemstone export, and media platforms.",
      "Exceptional ability to turn ideas into scalable cash cows."
    ],
    "health_precautions_ta": [
      "இடது காது வலி, கணுக்கால் வீக்கம், ரத்த ஓட்டக் குறைபாடுகள் மற்றும் சளித் தொல்லைகள்.",
      "முறையான பாத பராமரிப்பும் உடற்பயிற்சியும் நலம் காக்கும்."
    ],
    "health_precautions_en": [
      "Susceptible to left-ear aches, ankle edema, sluggish lymphatic circulation, and colds.",
      "Leg stretching and keeping ankles warm assist lymphatic drainage."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Moon",
    "planet_name_ta": "சந்திரன்",
    "symbol": "🌙",
    "element": "நீர் (Jala)",
    "house": 12,
    "bhava_category": "dusthana",
    "house_title_ta": "12-ஆம் பாவம் - விரய பாவம் (அமைதி, அயன சயன சுகம் & வெளிநாடு)",
    "house_title_en": "12th House - Vraya & Moksha Bhava (Inner Peace, Seclusion & Foreign Lands)",
    "core_traits_ta": [
      "அமைதியான தனிமையை விரும்பும் சுபாவம்; ஆழ்ந்த தூக்கமும் ஆன்மீக சிந்தனைகளும் கொண்டவர்.",
      "பிறந்த மண்ணை விட வெளிநாடுகளிலோ அல்லது கடல் கடந்த இடங்களிலோ அபரிமிதமான யோகம் பெறுவார்.",
      "ஏழை எளியவர்களுக்கும், மருத்துவமனைகளுக்கும், ஆன்மீக ஸ்தலங்களுக்கும் தாராளமாக வாரி வழங்கும் வள்ளல் தன்மை.",
      "மனதில் சில நேரங்களில் காரணமற்ற தனிமை உணர்வும் விரக்தியும் எட்டிப் பார்க்கக்கூடும்."
    ],
    "core_traits_en": [
      "Loves peaceful seclusion, contemplative solitude, deep sleep, and transcendent spiritual musings.",
      "Achieves peak prosperity and renown when settled far away from natal home or in overseas territories.",
      "Benevolent philanthropist who spends liberally on hospices, ashrams, and humanitarian causes.",
      "May occasionally suffer from subjective loneliness or vague emotional isolation."
    ],
    "strong_placement_ta": [
      "சுப பலத்துடன் இருப்பின்: வெளிநாட்டில் மாபெரும் சொத்துகள், அமைதியான இல்லற சுகம், ஆன்மீக முக்தி நிலை.",
      "அயன சயன சுகம் பூரணமாகக் கிட்டும்; மனக் குழப்பங்கள் நீங்கி ஆத்ம சாந்தி அடைவார்."
    ],
    "strong_placement_en": [
      "Strong with benefic aspects: Vast real estate holdings abroad, blissful conjugal rest, and spiritual Moksha.",
      "Enjoys sound restorative sleep, serene mental clarity, and divine tranquility."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தூக்கமின்மை, கண் பார்வைக் குறைபாடு, பண விரயங்கள்.",
      "மனக் கவலைகள், வீண் பயம் மற்றும் மருத்துவச் செலவுகளால் நிம்மதி குறையலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Severe insomnia, left-eye vision defects, chronic financial drain, and hospital bills.",
      "Haunted by irrational anxieties, nightmares, and heavy domestic expenditure."
    ],
    "career_wealth_ta": [
      "மருத்துவமனை நிர்வாகம், வெளிநாட்டுத் தூதரகம், சர்வதேசக் கப்பல் போக்குவரத்து, ஆன்மீக மடங்கள், உளவியல் காப்பகங்கள்.",
      "வெளிநாட்டு பண வரவாலும் ஆன்மீகப் பணிகளாலும் செல்வம் சேரும்."
    ],
    "career_wealth_en": [
      "High success in hospital administration, international diplomacy, overseas logistics, and meditative retreats.",
      "Income derived extensively in foreign currencies and specialized offshore institutions."
    ],
    "health_precautions_ta": [
      "இடது கண் உபாதை, பாதங்களில் வலி, தூக்கமின்மை (Insomnia) மற்றும் சளித் தொல்லைகள்.",
      "இரவில் படுக்கும் முன் பாதங்களை வெதுவெதுப்பான நீரில் கழுவுதலும் தியானமும் அமைதி தரும்."
    ],
    "health_precautions_en": [
      "Prone to left-eye strain, foot nerve pain, chronic insomnia, and recurring phlegm.",
      "Warm foot soaks and guided meditation before sleep restore equilibrium."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Mars",
    "planet_name_ta": "செவ்வாய்",
    "symbol": "🔴",
    "element": "தீ (Agni)",
    "house": 1,
    "bhava_category": "kendra",
    "house_title_ta": "1-ஆம் பாவம் - லக்னம் (வீரம், பராக்கிரமம் & ஆவேசம்)",
    "house_title_en": "1st House - Ascendant / Tanu Bhava (Heroic Valor & Fiery Will)",
    "core_traits_ta": [
      "அசாத்தியமான உடல்பலம், அஞ்சாநெஞ்சம், தளராத தைரியம் மற்றும் கம்பீரமான ஆளுமை கொண்டவர்.",
      "முன்கோபமும், எதையும் உடனே செய்து முடிக்க வேண்டும் என்ற அவசரமும், துடிப்பான சுபாவமும் இருக்கும்.",
      "சுயமரியாதைக்குக் களங்கம் விளைவித்தால் ஆவேசமடைவார்; யாருக்கும் தலைவணங்காத சுதந்திரப் போக்கு.",
      "தலை அல்லது முகத்தில் சிறிய தழும்பு அல்லது காயம் இருக்க வாய்ப்புண்டு; உஷ்ண தேகம்.",
      "சவால்களையும் போட்டிகளையும் துணிவுடன் எதிர்கொண்டு வெற்றிகொள்ளும் பேராற்றல்."
    ],
    "core_traits_en": [
      "Tremendous physical vitality, indomitable bravery, iron constitution, and commanding persona.",
      "Quick to flare up with a rash, impetuous temper; eager for immediate action and dynamic breakthroughs.",
      "Fiercely protective of self-respect; scorns defeat and rejects subordination.",
      "Often carries a scar or mark on the forehead or face; hot, pitta-dominated constitution.",
      "Fearless competitor who thrives in high-stakes adversarial contests."
    ],
    "strong_placement_ta": [
      "மேஷம்/விருச்சிகத்தில் ஆட்சி அல்லது மகரத்தில் உச்சம் பெற்று ருசக யோகம் (Ruchaka Yoga) அமைந்தால்: தலைமைத் தளபதி யோகம், போலீஸ்/ராணுவ உயர்பதவி, பரந்த நிலபுலன்கள்.",
      "அசைக்க முடியாத செல்வாக்கு, ஆயிரக்கணக்கான மக்களை வழிநடத்தும் அதிகாரம் மற்றும் வீரப்புகழ்."
    ],
    "strong_placement_en": [
      "Exalted in Capricorn or in own signs Aries/Scorpio forming Ruchaka Mahapurusha Yoga: Supreme military commander, high police chief, vast landed wealth.",
      "Commands invincible influence, monumental administrative muscle, and national honors for bravery."
    ],
    "weak_placement_ta": [
      "கடகத்தில் நீசம் அல்லது ராகு/சனியின் தாக்கம் பெற்றால்: விபத்துகளில் காயங்கள், அவசர முடிவுகளால் நஷ்டம், ரத்தக் கொதிப்பு.",
      "காரணமற்ற சண்டை சச்சரவுகள், பிடிவாதம் மற்றும் திருமண வாழ்வில் குஜ தோஷத்தால் (Kuja Dosha) பாதிப்புகள் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated in Cancer or afflicted by Rahu/Saturn: Prone to physical accidents, burns, head trauma, and hypertension.",
      "Reckless anger causes self-destructive disputes; Kuja Dosha sparks marital discords if unchecked."
    ],
    "career_wealth_ta": [
      "ராணுவம், காவல்துறை, அறுவை சிகிச்சை மருத்துவர், ரியல் எஸ்டேட், மெக்கானிக்கல் இன்ஜினியரிங், சுரங்கத் தொழில், தீயணைப்பு.",
      "துணிச்சலான முதலீடுகள், பூமி/நில வர்த்தகம் மற்றும் சொந்தத் தொழில் மூலம் அபரிமிதமான தன லாபம்."
    ],
    "career_wealth_en": [
      "Exemplary career in armed forces, IPS/defense command, trauma surgery, real estate development, mechanical engineering, and mining.",
      "Amasses great fortune through bold capital deployments and landed property acquisition."
    ],
    "health_precautions_ta": [
      "தலையில் காயங்கள், ரத்தக் கொதிப்பு, மூல நோய், உஷ்ணக் கட்டிகள் மற்றும் தீக்காயங்கள் ஏற்பட வாய்ப்புண்டு.",
      "காரமான உணவுகளைக் குறைத்து உடலை குளிர்ச்சியாக வைத்திருப்பதும், நிதானமாக வாகனம் ஓட்டுவதும் நலம் தரும்."
    ],
    "health_precautions_en": [
      "Vulnerable to cranial lacerations, hypertension, hemorrhoids, inflammatory boils, and burn hazards.",
      "Adopt cooling diets, avoid explosive temper tantrums, and maintain speed limits on roads."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 52) & Saravali Ch. 30"
  },
  {
    "planet": "Mars",
    "planet_name_ta": "செவ்வாய்",
    "symbol": "🔴",
    "element": "தீ (Agni)",
    "house": 2,
    "bhava_category": "panaphara",
    "house_title_ta": "2-ஆம் பாவம் - தன பாவம் (கூர்மையான வாக்கு & பூமி லாபம்)",
    "house_title_en": "2nd House - Dhana Bhava (Sharp Speech & Landed Wealth)",
    "core_traits_ta": [
      "வெளிப்படையான, கூர்மையான மற்றும் தயவுதாட்சண்யமற்ற பேச்சாற்றல்; பேச்சில் காரமும் உறுதியும் இருக்கும்.",
      "கடின உழைப்பாலும், விடாமுயற்சியாலும் சொத்துகளைச் சேர்க்கும் தன்னம்பிக்கை உடையவர்.",
      "குடும்பத்தில் சில சமயம் வீண் வாக்குவாதங்கள் வரலாம்; விட்டுக்கொடுத்துச் செல்வது நலம்.",
      "இரும்பு, உலோகம், இயந்திரங்கள் மற்றும் நிலம் தொடர்பான விஷயங்களில் நல்ல ஞானம் இருக்கும்."
    ],
    "core_traits_en": [
      "Blunt, incisive, and unvarnished speech; cuts straight to the core without diplomatic sugarcoating.",
      "Tenacious drive to amass tangible physical properties through hard enterprise.",
      "Prone to sudden domestic arguments within the family circle; requires tactful speech control.",
      "Innate flair for metals, weaponry, heavy machinery, and real estate evaluation."
    ],
    "strong_placement_ta": [
      "மகரத்தில் உச்சம் அல்லது சொந்த வீட்டில் பலம் பெற்றால்: பல கோடி மதிப்பிலான நிலபுலன்கள், தங்கக் கட்டிகள், அசைக்க முடியாத வங்கி இருப்பு.",
      "பேச்சில் கம்பீரமும் அதிகாரமும் கூடி சமுதாயத்தில் உயர்ந்த அந்தஸ்து கிட்டும்."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Bestows multi-million dollar real estate estates, bullion wealth, and robust liquidity.",
      "Voice commands respect and persuasive authority in boardroom negotiations."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: பேச்சினால் குடும்பத்தில் விரிசல், வழக்குகளால் தன விரயம்.",
      "வலது கண்ணில் அடிபடுதல், பல் பிடுங்குதல் அல்லது முகத்தில் தழும்புகள் உண்டாகலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Harsh words causing broken family ties, litigation costs, and sudden fiscal erosion.",
      "Prone to right-eye trauma, severe dental issues, and facial scars."
    ],
    "career_wealth_ta": [
      "ரியல் எஸ்டேட் புரோக்கரேஜ், இரும்பு/உலோக வர்த்தகம், இயந்திர உதிரிபாகங்கள், காண்ட்ராக்டர், வெடிபொருள் தயாரிப்பு, சமையல் கலை.",
      "பூமி லாபம் மற்றும் தொழில்நுட்ப உழைப்பால் செல்வச் சேர்க்கை உண்டாகும்."
    ],
    "career_wealth_en": [
      "Lucrative earnings in real estate development, scrap metal, hardware manufacturing, defense contracting, and industrial fabrication.",
      "Substantial wealth generated via property flipping and mechanical ventures."
    ],
    "health_precautions_ta": [
      "பல் வலி, ஈறுகளில் ரத்தம் வடிதல், தொண்டை அழற்சி, முகப்பருக்கள் மற்றும் வலது கண் பார்வை பாதிப்பு.",
      "வாய் சுகாதாரத்தைப் பேணுதலும், சூடான கார உணவுகளைத் தவிர்ப்பதும் அவசியம்."
    ],
    "health_precautions_en": [
      "Susceptible to dental abscesses, bleeding gums, pharyngeal inflammation, and right-eye irritation.",
      "Strict oral dental care and moderation of heavily spiced dishes are indicated."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 100) & Saravali Ch. 30"
  },
  {
    "planet": "Mars",
    "planet_name_ta": "செவ்வாய்",
    "symbol": "🔴",
    "element": "தீ (Agni)",
    "house": 3,
    "bhava_category": "upachaya",
    "house_title_ta": "3-ஆம் பாவம் - சகஜ பாவம் (அசாத்திய வீரியம் & வெற்றி)",
    "house_title_en": "3rd House - Sahaja Bhava (Extraordinary Valour & Triumph)",
    "core_traits_ta": [
      "செவ்வாய் 3-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமைவது இணையற்ற வீரத்தையும் துணிவையும் தரும் ராஜ யோகமாகும்.",
      "எந்தவிதமான ஆபத்தையும் கண்டு அஞ்சாத சிங்கம் போன்ற பராக்கிரமம்; எதிரிகளைப் புறமுதுகிடச் செய்வார்.",
      "விளையாட்டு, சாகசப் பயணங்கள், உடற்கட்டு மற்றும் போட்டிகளில் எப்போதும் முதலிடம் பிடிப்பார்.",
      "இளைய சகோதரர்களிடம் கண்டிப்பு காட்டினாலும் அவர்களுக்கு அரணாக நின்று காப்பார்."
    ],
    "core_traits_en": [
      "Mars in the 3rd (Upachaya house) is classically venerated as a formidable engine of heroic valor and victory.",
      "Lionhearted bravery in the face of imminent peril; scatters opponents with decisive boldness.",
      "Stellar athletic stamina, fond of martial arts, adventurous explorations, and physical conditioning.",
      "Acts as a fierce protector for younger siblings despite an authoritative demeanor."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: நாடாளும் அதிகாரம், ராணுவம்/காவல்துறையில் மிக உயரிய தலைமை, சரித்திரப் புகழ்.",
      "எடுத்த காரியங்கள் அனைத்திலும் அசுர வெற்றி; தோல்வி என்பதே அறியாத சாதனையாளராக விளங்குவார்."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Bestows apex command in armed forces, legendary athletic laurels, and national honors.",
      "Triumphs decisively in every competitive arena; builds a legacy of fearless excellence."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாப தொடர்புகள் இருப்பின்: சகோதரர்களுடன் நிலத்தகராறு, கைகளில் முறிவு அல்லது காயங்கள்.",
      "அவசரப்பட்டு வாக்குவாதம் செய்வதால் சட்டச் சிக்கல்கள் வரலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Acrimonious land disputes with brothers, collarbone/arm fractures, and rash legal altercations.",
      "Impulsive, aggressive outbursts causing alienation of well-wishers."
    ],
    "career_wealth_ta": [
      "ராணுவ அதிகாரிகள், விளையாட்டு வீரர்கள், துப்பறிவாளர், அறுவை சிகிச்சை நிபுணர், கட்டுமானத் துறை, பாதுகாப்பு ஏஜென்சிகள்.",
      "தைரியமான முதலீடுகளாலும் சாதனைகளாலும் அள்ள அள்ளக் குறையாத செல்வம்."
    ],
    "career_wealth_en": [
      "Celebrated success as defense commodore, elite athlete, trauma surgeon, construction developer, and security contractor.",
      "Generates vast capital through audacious enterprise and competitive contracts."
    ],
    "health_precautions_ta": [
      "தோள்பட்டை வலி, கைகளில் எலும்பு முறிவு, காது நரம்புக் கோளாறு மற்றும் ரத்த உறைவு.",
      "சாகச விளையாட்டுகளின் போது பாதுகாப்பு உபகரணங்களை தவறாமல் அணிய வேண்டும்."
    ],
    "health_precautions_en": [
      "Prone to collarbone trauma, shoulder dislocations, upper limb fractures, and auditory inflammation.",
      "Mandatory usage of protective sports gear and defensive driving habits."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 140) & Saravali Ch. 30"
  },
  {
    "planet": "Mars",
    "planet_name_ta": "செவ்வாய்",
    "symbol": "🔴",
    "element": "தீ (Agni)",
    "house": 4,
    "bhava_category": "kendra",
    "house_title_ta": "4-ஆம் பாவம் - சுக பாவம் (பூமி யோகம் & வீரம் நிறைந்த இல்லம்)",
    "house_title_en": "4th House - Sukha Bhava (Landed Estates & Domineering Home)",
    "core_traits_ta": [
      "சொந்தமாக நிலம், தோட்டம், வீடுகள் வாங்குவதில் அதிக ஆர்வமும் சாதனையும் படைப்பவர்.",
      "வீட்டிலும் குடும்பத்திலும் தன் கட்டுப்பாடும் அதிகாரமும் இருக்க வேண்டும் என கண்டிப்பு காட்டுவார்.",
      "மனதில் ஒருவிதமான அமைதியின்மையும், அடிக்கடி கோபம் தலைக்கேறும் வேகமும் இருக்கலாம்.",
      "தாய் வழியில் கருத்து வேறுபாடுகள் வராமல் பொறுமையைக் கடைப்பிடிப்பது நல்லது."
    ],
    "core_traits_en": [
      "Tremendous passion for acquiring vast landed estates, agricultural farms, and solid brick structures.",
      "Exercises rigid, no-nonsense control within the domestic sphere; demands strict discipline at home.",
      "Harbors internal fiery restlessness, periodically venting bursts of acute irritation.",
      "Must temper domestic interactions with patience to avoid friction with mother."
    ],
    "strong_placement_ta": [
      "மகரத்தில் உச்சம் அல்லது சொந்த வீட்டில் ருசக யோகம் அமைந்தால்: ஏக்கர் கணக்கில் நிலங்கள், மாளிகைகள், சொகுசு வாகனங்கள்.",
      "அரசாங்கத்தால் வழங்கப்படும் பங்களாக்கள், கௌரவப் பதவிகள் மற்றும் நிலையான செல்வ வளம்."
    ],
    "strong_placement_en": [
      "Exalted in Capricorn forming Ruchaka Yoga: Enormous acreage of land, prime real estate complexes, and heavy vehicle fleets.",
      "Granted state residences, executive privileges, and enduring ancestral security."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தாய் உடல்நலம் பாதித்தல், பூர்வீக நிலங்கள் கைவிட்டுப் போதல், வீட்டு விபத்துகள்.",
      "வாகன விபத்துகள், நிலத்தகராறுகளால் வழக்குகள் மற்றும் மன நிம்மதியின்மை ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated in Cancer or afflicted: Severe maternal health crises, loss of parental land to litigations, and vehicle collisions.",
      "Domestic turbulence, persistent friction with relatives, and property encumbrances."
    ],
    "career_wealth_ta": [
      "கட்டிடக் கலை, சிவில் இன்ஜினியரிங், விவசாய நில வர்த்தகம், ஆட்டோமொபைல் உதிரிபாகங்கள், சுரங்கம், செங்கல் சூளைகள்.",
      "பூமி பரிவர்த்தனைகளாலும் கட்டுமானத் தொழிலாலும் கோடிக்கணக்கில் வருமானம்."
    ],
    "career_wealth_en": [
      "Flourishes in civil engineering, commercial architecture, real estate syndication, automotive logistics, and quarrying.",
      "Massive capital accumulated through property land banking and urban development."
    ],
    "health_precautions_ta": [
      "நெஞ்சு வலி, ரத்த அழுத்த ஏற்றத்தாழ்வு, இதயப் படபடப்பு, வயிற்றில் அமிலம் மற்றும் உஷ்ண வியாதிகள்.",
      "எண்ணெயில் பொரித்த உணவுகளைத் தவிர்த்து இதய நலனைப் பரிசோதித்துக் கொள்ளவும்."
    ],
    "health_precautions_en": [
      "Prone to angina pectoris, cardiovascular strain, severe gastric reflux, and chest bruising.",
      "Avoid excessive fried foods, practice cardio exercise, and schedule routine cardiac checkups."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 174) & Saravali Ch. 30"
  },
  {
    "planet": "Mars",
    "planet_name_ta": "செவ்வாய்",
    "symbol": "🔴",
    "element": "தீ (Agni)",
    "house": 5,
    "bhava_category": "trikona",
    "house_title_ta": "5-ஆம் பாவம் - புத்திர பாவம் (கூர்மையான புத்தி & தைரியமான முதலீடு)",
    "house_title_en": "5th House - Putra Bhava (Sharp Intellect & Bold Speculation)",
    "core_traits_ta": [
      "மின்னல் போன்ற கூர்மையான புத்திசாலித்தனம், விரைவான முடிவெடுக்கும் திறன் மற்றும் தந்திரமான செயலாற்றல்.",
      "பங்குச் சந்தை, புதிய கண்டுபிடிப்புகள் மற்றும் சவாலான முதலீடுகளில் தைரியமாக இறங்குவார்.",
      "பிள்ளைகளிடம் அதிக கண்டிப்பு காட்டுவார்; இதனால் பிள்ளைகளுடன் கருத்து மோதல்கள் வர வாய்ப்புண்டு.",
      "தன் அறிவாற்றலையும் திறமையையும் சவால் விடுபவர்களை ஒருபோதும் சும்மா விட மாட்டார்."
    ],
    "core_traits_en": [
      "Lightning-fast analytical intellect, incisive tactical brilliance, and instant decision-making capacity.",
      "Audacious appetite for stock markets, venture risk, technological innovations, and strategic games.",
      "Tends to enforce military discipline with children, which can create emotional friction with them.",
      "Ferociously competitive when intellectual mastery or status is challenged."
    ],
    "strong_placement_ta": [
      "சுப ஸ்தானத்தில் ஆட்சி அல்லது உச்சம் பெற்றால்: புகழ்பெற்ற, தைரியமான ஆண் குழந்தைகள் பிறக்கும்; பூர்வ புண்ணியம் பலம் பெறும்.",
      "அரசாங்க உயர் ஆலோசனை குழுக்களில் இடம் பெறுதல், பெரிய அளவிலான முதலீடுகளில் அசுர லாபம் ஈட்டுதல்."
    ],
    "strong_placement_en": [
      "Exalted or well-placed: Bestows bold, valiant, and accomplished sons; magnifies past-life merit.",
      "Appointed to top government defense/intelligence advisory boards; massive speculative jackpots."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: புத்திர பாக்கியத்தில் தடைகள், கருச்சிதைவு அபாயம், பிள்ளைகளால் மனக்கவலை.",
      "சூதாட்டம், தவறான பங்கு வர்த்தகத்தால் பெரும் நிதி இழப்புகள் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Miscarriages, painful surgeries regarding progeny, and troubled relations with offspring.",
      "Crippling financial losses incurred through rash, impulsive gambling or day-trading."
    ],
    "career_wealth_ta": [
      "மென்பொருள் பொறியியல், சிஸ்டம் ஆர்க்கிடெக்ட், பங்குச் சந்தை முதலீட்டாளர், ஆயுத வடிவமைப்பு, விளையாட்டு பயிற்சியாளர்.",
      "புத்தி சாதுரியத்தாலும் தைரியமான ரிஸ்க் எடுக்கும் குணத்தாலும் பெரும் தன சேர்க்கை."
    ],
    "career_wealth_en": [
      "Thrives in algorithms/fintech, systems engineering, proprietary stock trading, defense hardware, and athletic coaching.",
      "Attains massive wealth through calculated high-stakes entrepreneurial gambles."
    ],
    "health_precautions_ta": [
      "அஜீரணம், வயிற்றுப் புண் (Peptic Ulcer), குடல் அழற்சி, கல்லீரல் உஷ்ணம் மற்றும் குடல்வால் அழற்சி (Appendicitis).",
      "காரமான உணவுகளைக் கட்டுப்படுத்தி சரியான நேரத்தில் உணவு உட்கொள்ளுதல் அவசியம்."
    ],
    "health_precautions_en": [
      "Susceptible to peptic ulcers, hyperacidity, acute appendicitis, and inflammatory colitis.",
      "Strictly moderate spicy dishes, avoid skipping meals, and keep stomach lining soothed."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 220) & Saravali Ch. 30"
  },
  {
    "planet": "Mars",
    "planet_name_ta": "செவ்வாய்",
    "symbol": "🔴",
    "element": "தீ (Agni)",
    "house": 6,
    "bhava_category": "dusthana",
    "house_title_ta": "6-ஆம் பாவம் - சத்ரு பாவம் (அசைக்க முடியாத சத்ரு ஜெயம் / மகா பலம்)",
    "house_title_en": "6th House - Satru Bhava (Total Conquest Over Foes & Invincible Immunity)",
    "core_traits_ta": [
      "செவ்வாய் 6-ஆம் பாவத்தில் அமைவது ஜாதகத்திற்கு மாபெரும் கவசமாகும்; எதிரிகள் இவரைக் கண்டு அஞ்சுவர்.",
      "எந்தவிதமான வழக்கு, போட்டி, சதித்திட்டம் மற்றும் கடன் தொல்லைகளையும் தவிடுபொடியாக்கும் அசுர பலம்.",
      "அளப்பரிய நோய் எதிர்ப்புச் சக்தி; கடினமான உடலுழைப்பையும் தாங்கும் திடகாத்திரமான உடல்வாகு.",
      "பணியாளர்களையும் வேலைக்காரர்களையும் திறம்பட வழிநடத்தி வேலை வாங்கும் சாமர்த்தியம் உண்டு."
    ],
    "core_traits_en": [
      "Mars in the 6th is classically celebrated as an impenetrable fortress of strength; totally annihilates opposition.",
      "Crushes all litigation, hostile conspiracies, and financial liabilities with unyielding resolve.",
      "Possesses iron physical stamina, supreme immune resilience, and boundless work capacity.",
      "Commands absolute obedience and high productivity from subordinates and staff."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: சத்ரு சம்ஹார யோகம்! எதிரிகள் இல்லா பெருவாழ்வு, நீதித்துறை/ராணுவத்தில் சர்வாதிகார அதிகாரம்.",
      "அளப்பரிய செல்வம், உடல் ஆரோக்கியம் மற்றும் போட்டிகளில் தொடர் வெற்றிகள் குவியும்."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Bestows complete Shatru Samhara Yoga! Total absence of enemies, premier defense/judicial supreme command.",
      "Immense accumulated wealth, unassailable physical vitality, and perpetual competitive victories."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: உடலில் உஷ்ண வியாதிகள், கொப்பளங்கள், அறுவை சிகிச்சைகள்.",
      "வேலையாட்களால் தகராறுகள், கடன் சுமைகள் அல்லது தாய்மாமனுடன் விரோதம் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated in Cancer or afflicted: Recurring acute inflammatory fevers, painful surgeries, and blood impurities.",
      "Troublesome labor disputes, insubordinate employees, and financial friction with maternal uncles."
    ],
    "career_wealth_ta": [
      "அறுவை சிகிச்சை மருத்துவர், குற்றவியல் வழக்கறிஞர், ராணுவத் தளபதி, வங்கி கடன் வசூலிப்பு, பாதுகாப்புத் துறை, சுங்கத்துறை.",
      "போட்டிகளையும் எதிர்ப்புகளையும் முறியடித்து அதன் வழியே அபரிமிதமான செல்வம் ஈட்டுவார்."
    ],
    "career_wealth_en": [
      "Dominates in trauma/orthopedic surgery, criminal trial law, armed forces, debt recovery, and border customs enforcement.",
      "Extracts substantial financial wealth directly from competitive conquests."
    ],
    "health_precautions_ta": [
      "அடிவயிற்று வலி, சிறுநீரகக் கற்கள், ரத்தக் கொப்பளங்கள், தீக்காயங்கள் மற்றும் அறுவை சிகிச்சைத் தழும்புகள்.",
      "அதிக நீர் அருந்துதலும், ரத்த அழுத்தப் பரிசோதனைகளும் அவசியமாகும்."
    ],
    "health_precautions_en": [
      "Vulnerable to kidney stones, acute abscesses, blood toxicities, burns, and surgical interventions.",
      "Maintain high fluid intake, monitor blood pressure, and avoid extreme heat exposure."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 261) & Saravali Ch. 30"
  },
  {
    "planet": "Mars",
    "planet_name_ta": "செவ்வாய்",
    "symbol": "🔴",
    "element": "தீ (Agni)",
    "house": 7,
    "bhava_category": "kendra",
    "house_title_ta": "7-ஆம் பாவம் - களத்திர பாவம் (குஜ தோஷம் / ஆற்றல்மிக்க துணை)",
    "house_title_en": "7th House - Kalathra Bhava (Kuja Dosha / Dynamic Spouse)",
    "core_traits_ta": [
      "துணிச்சலான, கம்பீரமான மற்றும் சுதந்திரமான சுபாவம் கொண்ட வாழ்க்கைத் துணை அமைவார்.",
      "குஜ தோஷம் (Kuja Dosha) அமைவதால் வாழ்க்கைத் துணையுடன் ஈகோ மோதல்களும் சூடான வாக்குவாதங்களும் வரலாம்.",
      "கூட்டுத் தொழிலில் பார்ட்னர்களிடம் கண்டிப்பும் வெளிப்படைத்தன்மையும் கொண்டிருப்பார்.",
      "சுயமரியாதையை விட்டுக்கொடுக்க மாட்டார்; தாம்பத்தியத்தில் சமரசமும் பொறுமையும் மிக அவசியமாகும்."
    ],
    "core_traits_en": [
      "Spouse is dynamic, spirited, courageous, fiercely independent, and possessing strong willpower.",
      "Classic Kuja Dosha (Mangal Dosha) configuration; sparks volatile ego clashes if mutual patience is lacking.",
      "Direct and strictly contractual in commercial business partnerships.",
      "Refuses to compromise on personal dignity; conscious harmony and emotional tact are essential."
    ],
    "strong_placement_ta": [
      "மகரத்தில் உச்சம் அல்லது சொந்த வீட்டில் சுப சேர்க்கை பெற்றால்: குஜ தோஷம் நிவர்த்தியாகி வசதியான, செல்வாக்கு மிக்க துணை அமைவார்.",
      "ரியல் எஸ்டேட் மற்றும் தொழில் கூட்டாண்மைகளில் பன்னாட்டு அளவில் பெரும் லாபமும் வெற்றியும் கிட்டும்."
    ],
    "strong_placement_en": [
      "Exalted in Capricorn or in own signs with benefics: Kuja Dosha is cancelled, granting an affluent, high-status, devoted partner.",
      "Remarkable financial windfalls through multinational corporate joint ventures and real estate syndicates."
    ],
    "weak_placement_ta": [
      "கடகத்தில் நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: திருமண வாழ்வில் கடும் விரிசல், விவாகரத்து அல்லது பிரிவினை அபாயம்.",
      "துணைக்கு விபத்துகள், ரத்த அழுத்தம் அல்லது கூட்டுத் தொழிலில் பெரும் ஏமாற்றங்கள் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated in Cancer or afflicted by malefics: Severe marital turbulence, threat of separation or divorce.",
      "Spouse prone to physical injuries, surgeries, or hypertension; financial betrayal by business partners."
    ],
    "career_wealth_ta": [
      "சர்வதேச வர்த்தகம், கட்டுமான காண்ட்ராக்ட், இயந்திர இறக்குமதி, சட்ட ஒப்பந்தங்கள், விளையாட்டு பொருட்கள் உற்பத்தி.",
      "வாழ்க்கைத் துணையின் குடும்ப வழியிலும் துணிச்சலான கூட்டு வர்த்தகத்தாலும் தன சேர்க்கை."
    ],
    "career_wealth_en": [
      "Lucrative success in international engineering trade, construction contracting, industrial imports, and sports goods.",
      "Substantial capital influx via marital alliances and strategic commercial consortiums."
    ],
    "health_precautions_ta": [
      "சிறுநீரகப் பாதை எரிச்சல், அடிவயிற்று உஷ்ணம், விரைவாதம், கருப்பை அல்லது விதைப்பை உபாதைகள்.",
      "முறையான மருத்துவப் பரிசோதனைகளும், உஷ்ணத்தைத் தணிக்கும் உணவுகளும் அவசியம்."
    ],
    "health_precautions_en": [
      "Susceptible to urinary tract inflammation, pelvic inflammatory disease, prostatitis, and reproductive heat.",
      "Routine medical screenings and staying well-hydrated are strongly indicated."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Mars",
    "planet_name_ta": "செவ்வாய்",
    "symbol": "🔴",
    "element": "தீ (Agni)",
    "house": 8,
    "bhava_category": "dusthana",
    "house_title_ta": "8-ஆம் பாவம் - ஆயுள் பாவம் (அஷ்டம செவ்வாய் / ஆபத்துகளிலிருந்து தப்புதல்)",
    "house_title_en": "8th House - Ayur Bhava (Survival from Peril & Secret Assets)",
    "core_traits_ta": [
      "அசாத்தியமான மன உறுதி; ஆபத்தான சூழ்நிலைகளில் கூட தற்காத்துக் கொள்ளும் துணிச்சலான உள்ளுணர்வு உடையவர்.",
      "அஷ்டமத்தில் செவ்வாய் அமர்வது மாங்கல்ய தோஷம் மற்றும் ஆயுள் பரிசோதனைகளைத் தரக்கூடிய அமைப்பாகும்.",
      "வாழ்க்கையில் திடீர் விபத்துகள், ரத்தக் காயங்கள் அல்லது அறுவை சிகிச்சைகளை சந்திக்க நேரிடலாம்.",
      "ரகசியத் திட்டங்களைத் தீட்டுவதிலும் மறைமுக எதிரிகளை எதிர்கொள்வதிலும் வல்லவர்."
    ],
    "core_traits_en": [
      "Exceptional survival instincts; possesses an uncanny reflex to extricate self from hazardous emergencies.",
      "Mars in the 8th is a critical placement for Kuja Dosha, testing marital harmony and physical safety.",
      "Prone to unexpected accidental mishaps, lacerations, or sudden surgical operations during Dasa periods.",
      "Highly adept at keeping confidential secrets and outmaneuvering covert adversaries."
    ],
    "strong_placement_ta": [
      "விருச்சிகத்தில் ஆட்சி அல்லது மகரத்தில் உச்சம் பெற்றால்: விபத்துகளிலிருந்து தப்பும் யோகம், நீண்ட ஆயுள், எதிர்பாராத உயில் சொத்துகள்.",
      "துணையின் வழியே மாபெரும் காப்பீட்டுத் தொகையோ அல்லது பூர்வீக சொத்துகளோ வந்து சேரும்."
    ],
    "strong_placement_en": [
      "In own sign Scorpio or exalted in Capricorn: Miraculous escapes from physical danger, sturdy longevity, vast legacies.",
      "Acquires substantial insurance claims, estates, and concealed wealth through marital ties."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தீக்காயங்கள், ஆயுதங்களால் காயங்கள், வாகன விபத்துகள், மூல நோய்.",
      "திருமண வாழ்வில் துணையின் ஆயுளுக்கு கண்டம் அல்லது கடுமையான சண்டை சச்சரவுகள் உண்டாகலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Burns, severe lacerations from metal/weapons, traffic crashes, and severe piles.",
      "Severe physical trials for the spouse, legal entanglements, and sudden wealth depletion."
    ],
    "career_wealth_ta": [
      "தடயவியல் துறை, பிரேதப் பரிசோதனை மருத்துவர், வெடிபொருள் நிபுணர், ஆயுள் காப்பீட்டு தணிக்கை, சுரங்க இன்ஜினியரிங்.",
      "திடீர் இன்சூரன்ஸ் இழப்பீடுகள், உயில் சொத்துகள் மற்றும் ரகசிய ஒப்பந்தங்கள் மூலம் தன வரவு."
    ],
    "career_wealth_en": [
      "Excels in forensic pathology, trauma surgery, demolition engineering, insurance auditing, and oil drilling.",
      "Wealth derived through settlement windfalls, unearned inheritance, and crisis management fees."
    ],
    "health_precautions_ta": [
      "மூல நோய் (Piles), ஆசனவாய் வெடிப்பு, ரத்தப் போக்கு, இடுப்பு எலும்பு முறிவு மற்றும் விபத்துக் காயங்கள்.",
      "வாகனம் ஓட்டும்போது மிகுந்த எச்சரிக்கை தேவை; நார்ச்சத்து மிகுந்த உணவுகளை உண்பது நல்லது."
    ],
    "health_precautions_en": [
      "Vulnerable to hemorrhoidal bleeding, anal fissures, acute pelvic trauma, and bone fractures.",
      "Extreme caution required when handling vehicles or machinery; maintain a high-fiber cooling diet."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Mars",
    "planet_name_ta": "செவ்வாய்",
    "symbol": "🔴",
    "element": "தீ (Agni)",
    "house": 9,
    "bhava_category": "trikona",
    "house_title_ta": "9-ஆம் பாவம் - பாக்கிய பாவம் (தர்ம வீரம் & தந்தை நலம்)",
    "house_title_en": "9th House - Bhagya Bhava (Righteous Crusader & Paternal Fortune)",
    "core_traits_ta": [
      "நியாயத்திற்காகவும் அநீதியை எதிர்த்தும் துணிவுடன் குரல் கொடுக்கும் தர்ம வீரர்.",
      "தனக்கென தனித்துவமான கொள்கைகளை வகுத்துக்கொண்டு வாழ்வார்; பிறர் சொல்வதை அப்படியே ஏற்க மாட்டார்.",
      "தந்தையுடன் கருத்து வேறுபாடுகள் வரலாம்; ஆனால் தந்தையின் நலனில் எப்போதும் அக்கறை கொண்டிருப்பார்.",
      "நீண்ட தூர சாகசப் பயணங்கள், மலைப் பிரதேசங்கள் மற்றும் வரலாற்றுச் சிறப்புமிக்க இடங்களுக்குச் செல்வதில் விருப்பம்."
    ],
    "core_traits_en": [
      "Fierce champion of justice; ready to combat ethical wrongdoing and stand up for righteous causes.",
      "Possesses an independent philosophical worldview; refuses blind dogmatic conformism.",
      "Periodic ideological clashes with the father, yet preserves a fundamental filial loyalty.",
      "Passionate affinity for high-altitude treks, rugged adventures, and exploring ancient battlefields."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்று சுப பார்வை அமைந்தால்: தந்தையின் செல்வாக்கு உயர்தல், முன்னோர்களின் பூமி பலம், அரசு கௌரவம்.",
      "ஆன்மீகத் தலைமை, தர்ம ஸ்தாபனங்களில் நிர்வாகப் பதவி மற்றும் சமுதாயத்தில் மாபெரும் நற்பெயர்."
    ],
    "strong_placement_en": [
      "Exalted or in own house with benefics: Elevates paternal stature, inherits vast ancestral lands, and wins civic awards.",
      "Attains executive stewardship over religious or philanthropic foundations and universal respect."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தந்தையின் உடல்நலம் பாதித்தல், தந்தையுடன் கடுமையான விரோதம்.",
      "ஆன்மீக குருமார்களுடன் மோதல்கள், சட்டச் சிக்கல்கள் மற்றும் வெளிநாட்டுப் பயணங்களில் தடைகள்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Paternal health breakdown, bitter estrangement from father, and legal suits.",
      "Clashes with religious mentors, anti-establishment rebelliousness, and visa/immigration denials."
    ],
    "career_wealth_ta": [
      "சட்டத்துறை, உயர் நீதிமன்ற நீதிபதி, அரசியல் பேச்சாளர், சர்வதேச பாதுகாப்பு ஆலோசகர், வனத்துறை அதிகாரி.",
      "நீதி மற்றும் தர்ம வழியிலும், வெளிநாட்டுத் தொடர்புகளாலும் நிலையான சொத்துகள் சேரும்."
    ],
    "career_wealth_en": [
      "Thrives as appellate judge, constitutional attorney, geopolitical defense analyst, and forestry conservator.",
      "Builds enduring real estate assets through ethical practice and multinational contracts."
    ],
    "health_precautions_ta": [
      "தொடை எலும்பு வலி, இடுப்பு நரம்புப் பிடிப்பு (Sciatica), கல்லீரல் உஷ்ணம் மற்றும் தசைப் பிடிப்புகள்.",
      "முறையான யோகாசனப் பயிற்சிகளும், தசைப் பிடிப்புகளுக்கான மசாஜ்களும் நலம் தரும்."
    ],
    "health_precautions_en": [
      "Prone to femoral strain, sciatic nerve irritation, liver heat, and hamstring muscle tears.",
      "Regular yoga stretching and therapeutic muscular massage optimize lower limb mobility."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Mars",
    "planet_name_ta": "செவ்வாய்",
    "symbol": "🔴",
    "element": "தீ (Agni)",
    "house": 10,
    "bhava_category": "kendra",
    "house_title_ta": "10-ஆம் பாவம் - ஜீவன பாவம் (குலதீபக யோகம் / திக்பலம் & தலைமை)",
    "house_title_en": "10th House - Karma Bhava (Kuladipaka Yoga / Supreme Digbala & Command)",
    "core_traits_ta": [
      "செவ்வாய் 10-ஆம் பாவத்தில் திக்பலம் (Digbala) பெற்று குலதீபக யோகத்தை (Kuladipaka Yoga) உருவாக்குகிறார்.",
      "தன் குலத்திற்கே விளக்காகத் திகழ்ந்து குடும்பத்தையும் தொழிலையும் மாபெரும் உச்சிக்குக் கொண்டு செல்வார்.",
      "தளராத சுறுசுறுப்பு, தலைமை தாங்கும் பேராற்றல், இரும்பு போன்ற மன உறுதி மற்றும் கம்பீரம்.",
      "சவாலான திட்டங்களை முன்னின்று நடத்தி முடிக்கும் செயல்வீரர்; எதிர்ப்புகளைத் தூள்தூளாக்குவார்."
    ],
    "core_traits_en": [
      "Mars attains maximum Digbala (directional potency) in the 10th house, generating the prestigious Kuladipaka Yoga.",
      "Acts as the radiant beacon of the lineage, elevating family name and commercial fortunes to unprecedented peaks.",
      "Unbounded dynamism, invincible leadership prowess, iron fortitude, and commanding imperial aura.",
      "Relentless executor who spearheads daunting missions and obliterates institutional stagnation."
    ],
    "strong_placement_ta": [
      "மகரத்தில் உச்சம் அல்லது சொந்த வீட்டில் ருசக யோகம் பெற்றால்: நாட்டின் முதன்மை ராணுவத் தளபதி, போலீஸ் டிஜிபி, கேபினட் மந்திரி யோகம்.",
      "பல்லாயிரக்கணக்கான பணியாளர்களை வழிநடத்தும் தலைமை நிர்வாக அதிகாரி (CEO) அந்தஸ்து மற்றும் சரித்திரப் புகழ்."
    ],
    "strong_placement_en": [
      "Exalted in Capricorn or in own signs forming Ruchaka Yoga: Chief of Army Staff, Director General of Police, Cabinet Minister.",
      "Global industrialist or CEO commanding thousands of personnel; enters history books as a transformative pioneer."
    ],
    "weak_placement_ta": [
      "கடகத்தில் நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: அதிகாரிகளுடன் மோதல், பதவியிறக்கம், பொது வாழ்வில் சரிவு.",
      "தொழிலில் விபத்துகள், இயந்திரச் சேதங்கள் மற்றும் திடீர் நஷ்டங்கள் ஏற்பட வாய்ப்புண்டு."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Sudden workplace fall, clashes with state regulators, demotion from high office.",
      "Severe industrial accidents, mechanical breakdowns, and catastrophic business liabilities."
    ],
    "career_wealth_ta": [
      "பாதுகாப்புப் படைகள், காவல்துறை, சிவில் இன்ஜினியரிங், அறுவை சிகிச்சை மருத்துவமனை அதிபர், பெரிய தொழிற்சாலைகள், கனரக இயந்திரங்கள்.",
      "அரசாங்க ஒப்பந்தங்கள் மற்றும் தொழில் ஆளுமை மூலம் பல கோடிகளில் சொத்துக்களும் அதிகாரமும்."
    ],
    "career_wealth_en": [
      "Dominant in military defense, police leadership, heavy civil construction, hospital chains, and steel fabrication.",
      "Multi-million dollar assets accrued through authoritative leadership and state infrastructure tenders."
    ],
    "health_precautions_ta": [
      "பணிச்சுமையால் ரத்த அழுத்தம், மூட்டு வலி, தசை இறுக்கம் மற்றும் உஷ்ணக் கட்டிகள்.",
      "முறையான உடற்பயிற்சியும், ஓய்வுக்கான நேரத்தை ஒதுக்குவதும் நீண்ட ஆயுளைத் தரும்."
    ],
    "health_precautions_en": [
      "Occupational stress, hypertension, knee cartilage wear, muscle spasms, and febrile inflammation.",
      "Structured cardiovascular workouts and disciplined sleep patterns protect executive vitality."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Mars",
    "planet_name_ta": "செவ்வாய்",
    "symbol": "🔴",
    "element": "தீ (Agni)",
    "house": 11,
    "bhava_category": "upachaya",
    "house_title_ta": "11-ஆம் பாவம் - லாப பாவம் (அகண்ட பூமி லாபம் & மாபெரும் தன வரவு)",
    "house_title_en": "11th House - Labha Bhava (Massive Real Estate Gains & Wealth Accumulation)",
    "core_traits_ta": [
      "செவ்வாய் 11-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமைவது அளப்பரிய செல்வத்தையும், தொடர் லாபங்களையும் தரும் யோகமாகும்.",
      "எடுத்த முதலீடுகள் யாவிலும் இரட்டிப்பு லாபம்; ஆசைகள் அனைத்தும் தன்னம்பிக்கையால் நிறைவேறும்.",
      "செல்வாக்கு மிக்க தலைவர்கள், தொழில் அதிபர்கள் மற்றும் பாதுகாப்பு அதிகாரிகளின் நட்பு கிட்டும்.",
      "மூத்த சகோதரர்களிடம் அன்பும் அதே சமயம் சில கருத்து வேறுபாடுகளும் ஏற்படலாம்."
    ],
    "core_traits_en": [
      "Mars in the 11th (an Upachaya house) is a premier harbinger of relentless wealth creation and continuous financial expansion.",
      "Multiplies capital returns on every enterprise; fulfills grand ambitions through bold self-effort.",
      "Cultivates powerful camaraderie with magnates, top bureaucrats, and military chiefs.",
      "Maintains a respectful yet occasionally combative dynamic with elder siblings."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: எண்ணற்ற நிலங்கள், அடுக்குமாடிக் குடியிருப்புகள், தொழிற்சாலைகள், தங்கக் கட்டிகள் குவியும்.",
      "சமுதாயத்தில் மாபெரும் செல்வந்தராகப் போற்றப்படுதல், அரசியலில் பெரிய ஆதரவு பெறுதல்."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Bestows multiple residential towers, vast agricultural acreages, factories, and gold bullion.",
      "Ranked among the elite wealthy tier of society; commands formidable political muscle."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாப சேர்க்கை பெற்றால்: நண்பர்களால் ஏமாற்றப்பட்டு பெரும் இழப்பு, மூத்த சகோதரருடன் சொத்துத் தகராறு.",
      "லாபங்கள் கைநழுவுதல், கடன் சுமைகள் அல்லது தவறான முதலீடுகளால் விரயங்கள்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Heavy betrayal by deceptive associates, bitter partition lawsuits with elder brother.",
      "Sudden loss of profit margins and capital entrapment in disputed properties."
    ],
    "career_wealth_ta": [
      "ரியல் எஸ்டேட் வளர்ச்சி, நில மேம்பாடு, இரும்பு மற்றும் எஃகு ஆலைகள், கட்டுமான ஒப்பந்தங்கள், வென்ச்சர் கேபிடல்.",
      "நிலங்களின் மதிப்பு பல மடங்கு உயர்வதாலும், துணிச்சலான வணிகத்தாலும் பெரும் தன லாபம்."
    ],
    "career_wealth_en": [
      "Magnificent success in mega-real-estate syndicates, steel manufacturing, infrastructure procurement, and venture capital.",
      "Huge exponential capital appreciation realized from prime urban land parcels."
    ],
    "health_precautions_ta": [
      "இடது காது வலி, கணுக்கால் சுளுக்கு, ரத்தக் கொதிப்பு மற்றும் தசைநார் கிழிசல்.",
      "கால் நரம்புகளுக்கான உடற்பயிற்சியும், ரத்த அழுத்தப் பரிசோதனைகளும் நலம் காக்கும்."
    ],
    "health_precautions_en": [
      "Susceptible to left-ear inflammation, ankle sprains, arterial hypertension, and ligament tears.",
      "Calf stretching, ankle mobility drills, and routine vascular monitoring are advised."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Mars",
    "planet_name_ta": "செவ்வாய்",
    "symbol": "🔴",
    "element": "தீ (Agni)",
    "house": 12,
    "bhava_category": "dusthana",
    "house_title_ta": "12-ஆம் பாவம் - விரய பாவம் (குஜ தோஷம் / வெளிநாட்டு வெற்றி & விரயம்)",
    "house_title_en": "12th House - Vraya Bhava (Kuja Dosha / Foreign Conquests & Heavy Expenses)",
    "core_traits_ta": [
      "சுதந்திரமான மனப்பான்மை; பிறந்த ஊரை விட வெளிநாடுகளிலோ அல்லது கடல் கடந்த இடங்களிலோ சாதிப்பார்.",
      "செவ்வாய் 12-ஆம் பாவத்தில் அமர்வது குஜ தோஷத்தை (Kuja Dosha) உண்டாக்கும்; தாம்பத்தியத்தில் சகிப்புத்தன்மை தேவை.",
      "பணத்தை தாராளமாகச் செலவழிக்கும் சுபாவம்; திடீர் விரயங்களும் எதிர்பாராத நஷ்டங்களும் வரலாம்.",
      "ரகசிய எதிரிகளை எளிதில் அடையாளம் கண்டு அவர்களைத் துணிவுடன் முறியடிப்பார்."
    ],
    "core_traits_en": [
      "Restless independent spirit; thrives far more dramatically abroad or in distant jurisdictions than in birth city.",
      "Triggers Kuja Dosha (Mangal Dosha) from the 12th; necessitates conscious tolerance and tenderness in marital intimacy.",
      "Spends with open-handed impetuosity; prone to sudden drain of liquid funds.",
      "Possesses sharp instincts to sniff out hidden conspirators and neutralize them proactively."
    ],
    "strong_placement_ta": [
      "மகரத்தில் உச்சம் அல்லது சொந்த வீட்டில் சுப சேர்க்கை பெற்றால்: வெளிநாட்டில் மாபெரும் ரியல் எஸ்டேட் சாம்ராஜ்யம், ஆயுத ஏற்றுமதி.",
      "அரசாங்கத் தூதரகங்களில் பாதுகாப்பு அதிகாரி யோகம், எதிரிகளைத் தன் காலடியில் வீழ்த்தும் பராக்கிரமம்."
    ],
    "strong_placement_en": [
      "Exalted or well-placed: Commands massive offshore real estate holdings, defense hardware contracts, and global standing.",
      "Attains prestigious diplomatic defense attache roles; totally subjugates covert adversaries."
    ],
    "weak_placement_ta": [
      "கடகத்தில் நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: இடது கண் காயம், தூக்கமின்மை, மருத்துவச் செலவுகள், சிறைவாசம் அல்லது சட்ட அபராதங்கள்.",
      "தாம்பத்திய சுகக் குறைவு, விவாகரத்து வழக்குகள் மற்றும் திடீர் நிதி திவால் அபாயம்."
    ],
    "weak_placement_en": [
      "Debilitated or heavily afflicted: Left eye ocular injury, acute insomnia, crushing surgical debts, confinement or penal fines.",
      "Marital estrangement, bedroom coldness, and risk of sudden insolvency."
    ],
    "career_wealth_ta": [
      "வெளிநாட்டு காண்ட்ராக்ட், கப்பல் படை, சிறைத்துறை நிர்வாகம், சர்வதேச உளவுத்துறை, மெட்டலர்ஜி மற்றும் ஆயுத வர்த்தகம்.",
      "வெளிநாட்டு முதலீடுகளாலும் தூரதேசப் பணிகளாலும் செல்வம் சேரும்."
    ],
    "career_wealth_en": [
      "Dominates in foreign defense contracting, naval navigation, correctional administration, international espionage, and metallurgy.",
      "Generates vast revenues in foreign currencies from remote overseas installations."
    ],
    "health_precautions_ta": [
      "இடது கண் பாதிப்பு, பாதங்களில் வெட்டுக்காயங்கள்/தீக்காயங்கள், மூல நோய் மற்றும் தூக்கமின்மை.",
      "இரவில் அமைதியான சூழலில் தூங்குவதும், பாதங்களைப் பாதுகாப்பதும் மிகவும் அவசியம்."
    ],
    "health_precautions_en": [
      "Vulnerable to left-eye lacerations, foot burns/puncture wounds, acute hemorrhoids, and insomnia.",
      "Wear sturdy footwear, secure protective eyewear, and practice sleep hygiene."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Mercury",
    "planet_name_ta": "புதன்",
    "symbol": "🟢",
    "element": "நிலம் (Prithvi)",
    "house": 1,
    "bhava_category": "kendra",
    "house_title_ta": "1-ஆம் பாவம் - லக்னம் (திக்பலம் / மகா புத்தி & வித்யா யோகம்)",
    "house_title_en": "1st House - Ascendant / Tanu Bhava (Digbala / Intellect & Wit)",
    "core_traits_ta": [
      "புதன் லக்னத்தில் திக்பலம் (Digbala) பெற்று அமர்வது மாபெரும் வித்யா யோகத்தையும் கூர்மையான புத்திக்கூர்மையையும் தரும்.",
      "கவர்ச்சிகரமான இளமைத் தோற்றம், நகைச்சுவை உணர்வு, வசீகரமான பேச்சாற்றல் மற்றும் விரைந்து கற்கும் திறன்.",
      "கணிதம், ஜோதிடம், கணக்கியல், தர்க்க சாஸ்திரம் மற்றும் பல மொழிகளில் புலமை பெறும் ஆற்றல் உண்டு.",
      "விவேகமான முடிவுகள், சாதுரியமான அணுகுமுறை மற்றும் எந்தச் சூழ்நிலையிலும் நயமாகப் பேசி காரியம் சாதிக்கும் சாமர்த்தியம்.",
      "மானமரியாதைக்கு முக்கியத்துவம் கொடுப்பார்; தன் அறிவை யாரேனும் குறைத்து மதிப்பிடுவதை விரும்ப மாட்டார்."
    ],
    "core_traits_en": [
      "Mercury attains supreme Digbala (directional potency) in the 1st house, generating extraordinary intellectual brilliance.",
      "Youthful countenance, delightful wit, magnetic eloquence, and an agile, lightning-fast learning capacity.",
      "Natural genius in mathematics, astrology, accountancy, logic, linguistics, and literature.",
      "Diplomatic acumen; navigates convoluted interpersonal scenarios with polished grace and persuasive tact.",
      "Treasures intellectual self-respect; disdains superficiality and arrogance in peers."
    ],
    "strong_placement_ta": [
      "கன்னியில் உச்சம் அல்லது மிதுனத்தில் ஆட்சி பெற்று பத்ர யோகம் (Bhadra Yoga) அமைந்தால்: உலகப் புகழ் பெற்ற அறிஞர், அரசாங்க முதன்மை ஆலோசகர்.",
      "நூற்றுக்கணக்கான நூல்களை இயற்றும் ஆற்றல், சர்வதேச விருதுகள் மற்றும் மாபெரும் தொழில் சாம்ராஜ்யம்."
    ],
    "strong_placement_en": [
      "Exalted in Virgo or own sign Gemini forming Bhadra Mahapurusha Yoga: Globally acclaimed scholar, chief ministerial advisor.",
      "Prolific author of masterworks, recipient of international scholastic laurels, and creator of successful commercial conglomerates."
    ],
    "weak_placement_ta": [
      "மீனத்தில் நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: நரம்புத் தளர்ச்சி, முடிவெடுப்பதில் குழப்பம், பேச்சில் தடுமாற்றம்.",
      "அதிக சிந்தனையால் மன உளைச்சல் மற்றும் சூதாட்டம் அல்லது தவறான கணக்குகளால் நஷ்டம்."
    ],
    "weak_placement_en": [
      "Debilitated in Pisces or afflicted: Nervous debility, mental indecision, stammering, and erratic memory lapses.",
      "Overthinking inducing chronic mental exhaustion and fiscal losses due to fraudulent book-keeping."
    ],
    "career_wealth_ta": [
      "தகவல் தொழில்நுட்பம் (IT), மென்பொருள் உருவாக்கம், தணிக்கையாளர் (CA), பத்திரிகையாளர், எழுத்தாளர், பங்கு வர்த்தகம், கல்வித்துறை.",
      "அறிவுசார் சொத்துரிமை, வர்த்தக சாதுரியம் மற்றும் தரகு/கமிஷன் மூலம் அபரிமிதமான செல்வம்."
    ],
    "career_wealth_en": [
      "Eminent success in information technology, software architecture, chartered accountancy, journalism, equity trading, and publishing.",
      "Generates vast wealth through intellectual property, syndication royalties, and commercial brokerage."
    ],
    "health_precautions_ta": [
      "நரம்பு மண்டல பலவீனம், தோல் அலர்ஜி, ஆஸ்துமா, தலைவலி மற்றும் கைகளில் நடுக்கம்.",
      "தியானம், பிராணாயாமம் மற்றும் கீரை வகைகளை உணவில் சேர்ப்பது நரம்புகளைப் பலப்படுத்தும்."
    ],
    "health_precautions_en": [
      "Prone to nervous breakdown, skin dermatosis, bronchial asthma, vertigo, and hand tremors.",
      "Deep yogic breathing, nervous relaxation therapies, and green leafy nutrition preserve equilibrium."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 52) & Saravali Ch. 30"
  },
  {
    "planet": "Mercury",
    "planet_name_ta": "புதன்",
    "symbol": "🟢",
    "element": "நிலம் (Prithvi)",
    "house": 2,
    "bhava_category": "panaphara",
    "house_title_ta": "2-ஆம் பாவம் - தன பாவம் (சாதுரிய வாக்கு & வணிகச் செல்வம்)",
    "house_title_en": "2nd House - Dhana Bhava (Eloquent Speech & Commercial Wealth)",
    "core_traits_ta": [
      "நயமான, இனிமையான மற்றும் எந்தக் கூட்டத்தையும் தன் பேச்சால் மயக்கும் அபார பேச்சாற்றல்.",
      "வணிக நுணுக்கங்கள், கணக்கு வழக்குகளில் துல்லியம் மற்றும் பணத்தைச் சுழற்றிப் பெருக்கும் சாதுரியம்.",
      "குடும்பத்தில் மகிழ்ச்சியான சூழல்; உறவினர்களுடன் கலகலப்பாகப் பழகும் சுபாவம்.",
      "நகைச்சுவை ததும்பப் பேசி அனைவரையும் சிரிக்க வைக்கும் கலை உணர்வு கொண்டவர்."
    ],
    "core_traits_en": [
      "Exceptional eloquence; enchants audiences with persuasive, humorous, and lucid expression.",
      "Acute mercantile instincts, flawless mathematical ledgering, and masterly financial acumen.",
      "Fosters a joyful, lively, and intellectually stimulating domestic atmosphere.",
      "Spontaneous sense of humor and quick repartee that endears him across social circles."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: கோடிக்கணக்கான திரவ சேமிப்பு, வைர-வைடூரியங்கள், வாக்கு பலிதம்.",
      "பேச்சையே மூலதனமாக வைத்துப் பெரும் பணம் ஈட்டும் வித்தாக விளங்குவார்."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Bestows massive liquid banking reserves, precious gems, and prophetic speech accuracy.",
      "Monetizes communicative intellect into an inexhaustible goldmine of wealth."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: பேச்சில் பொய்மை, வாக்கு தவறுகை, தவறான முதலீடுகளால் நஷ்டம்.",
      "பற்களில் சொத்தை, வாய் புண்கள் அல்லது வலது கண்ணில் பார்வை மங்குதல் வரலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Deceptive speech, breach of financial trusts, and heavy trading losses.",
      "Prone to dental decay, oral ulcerations, and right-eye vision impairments."
    ],
    "career_wealth_ta": [
      "வங்கி மேலாளர், தணிக்கையாளர், முதலீட்டு ஆலோசகர், தொலைக்காட்சி நிகழ்ச்சித் தொகுப்பாளர், பேராசிரியர், பதிப்பகத் தொழில்.",
      "பேச்சாற்றல், எழுத்து மற்றும் வர்த்தக பரிவர்த்தனைகள் மூலம் வற்றாத தன வரவு."
    ],
    "career_wealth_en": [
      "Thrives in banking management, forensic auditing, investment brokerage, media broadcasting, and publishing.",
      "Continuous revenue streams flowing directly from intellectual and rhetorical services."
    ],
    "health_precautions_ta": [
      "தொண்டை எரிச்சல், வாய் துர்நாற்றம், பற்கள் ஆடுதல், நாக்கில் வெடிப்பு மற்றும் நரம்புத் தளர்ச்சி.",
      "வாய் சுகாதாரத்தைப் பேணுதலும் சத்தான காய்கறிகளை உண்பதும் நலம் பயக்கும்."
    ],
    "health_precautions_en": [
      "Susceptible to pharyngeal irritation, halitosis, periodontal disease, and lingual sensitivity.",
      "Strict oral hygiene and antioxidant-rich organic nutrition prevent flare-ups."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 100) & Saravali Ch. 30"
  },
  {
    "planet": "Mercury",
    "planet_name_ta": "புதன்",
    "symbol": "🟢",
    "element": "நிலம் (Prithvi)",
    "house": 3,
    "bhava_category": "upachaya",
    "house_title_ta": "3-ஆம் பாவம் - சகஜ பாவம் (படைப்பாற்றல் & தகவல் தொடர்பு)",
    "house_title_en": "3rd House - Sahaja Bhava (Literary Creativity & Media Enterprise)",
    "core_traits_ta": [
      "அசாத்தியமான எழுத்தாற்றல், பத்திரிகைத் துறையில் மேன்மை மற்றும் புதிய யோசனைகளை உருவாக்கும் திறன்.",
      "சகோதர சகோதரிகளுடன் நல்ல தோழமையும், அவர்களுடன் இணைந்து புதிய முயற்சிகளைத் தொடங்கும் ஆர்வமும் இருக்கும்.",
      "சுறுசுறுப்பான செயல்பாடுகள், குறுகிய வணிகப் பயணங்கள் மற்றும் நண்பர்களின் விரிவான வட்டாரம்.",
      "கைகளால் செய்யும் நுணுக்கமான வேலைகள், சித்திரங்கள், சிற்பங்கள் அல்லது கணினி தட்டச்சில் அசாத்திய வேகம்."
    ],
    "core_traits_en": [
      "Prolific literary ability, journalistic finesse, and brilliant creative conceptualization.",
      "Fraternal warmth; collaborates with siblings on pioneering media or technological ventures.",
      "Agile, restless energy; thrives on frequent short commercial trips and diverse social networking.",
      "Deft manual dexterity; excels in fine draftsmanship, calligraphy, digital programming, and instrumental music."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: புகழ்பெற்ற நாவலாசிரியர், ஊடக சாம்ராஜ்யத்தின் அதிபர், சர்வதேசப் புகழ்.",
      "தொலைத்தொடர்பு மற்றும் பதிப்பகத் துறையில் பெரும் முதலீடுகளும் வெற்றிகளும் குவியும்."
    ],
    "strong_placement_en": [
      "Strong or exalted: Becomes a celebrated literary novelist, media mogul, and recipient of international acclaim.",
      "Builds lucrative empires across digital communications, satellite broadcasting, and publishing."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: சகோதரர்களுடன் கருத்து வேறுபாடுகள், கைகளில் நரம்பு வலி.",
      "எழுதிய எழுத்துகளால் வீண் வழக்குகள் அல்லது பத்திரிகை விவகாரங்களில் அவப்பெயர் உண்டாகலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Bitter sibling misunderstandings, writer's block, and carpal tunnel syndrome.",
      "Defamation lawsuits or copyright controversies arising from rash publications."
    ],
    "career_wealth_ta": [
      "பத்திரிகை ஆசிரியர், நாவலாசிரியர், டிஜிட்டல் மார்க்கெட்டிங், விளம்பர ஏஜென்சி, தபால் மற்றும் பார்சல் சர்வீஸ், திரைக்கதை ஆசிரியர்.",
      "எழுத்தாற்றலாலும் தகவல் தொடர்பு நெட்வொர்க்குகளாலும் அபரிமிதமான செல்வம் சேரும்."
    ],
    "career_wealth_en": [
      "High rewards in editor-in-chief roles, digital marketing, screenplay creation, logistics syndicates, and advertising.",
      "Wealth surges through syndicate content, book royalties, and high-velocity digital networks."
    ],
    "health_precautions_ta": [
      "கைகளில் நரம்புப் பிடிப்பு, தோள்பட்டை வலி, காதுகளில் இரைச்சல் (Tinnitus) மற்றும் விரல் நடுக்கம்.",
      "கணினியில் வேலை செய்வோர் விரல்களுக்கும் கண்களுக்கும் குறிப்பிட்ட இடைவெளியில் ஓய்வு கொடுக்க வேண்டும்."
    ],
    "health_precautions_en": [
      "Prone to carpal tunnel syndrome, shoulder tension, tinnitus, and finger muscular fatigue.",
      "Ergonomic computer posture and periodic typing breaks protect musculoskeletal agility."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 140) & Saravali Ch. 30"
  },
  {
    "planet": "Mercury",
    "planet_name_ta": "புதன்",
    "symbol": "🟢",
    "element": "நிலம் (Prithvi)",
    "house": 4,
    "bhava_category": "kendra",
    "house_title_ta": "4-ஆம் பாவம் - சுக பாவம் (உயர்கல்வி, சொத்து & மகிழ்ச்சியான இல்லம்)",
    "house_title_en": "4th House - Sukha Bhava (Higher Education, Property & Joyful Home)",
    "core_traits_ta": [
      "ஆழ்ந்த கல்வி ஞானம், பல பட்டங்களைப் பெறும் யோகம் மற்றும் ஆராய்ச்சிகளில் ஆர்வம் கொண்டவர்.",
      "தாய் வழியில் அன்பும் ஆதரவும் பரிபூரணமாகக் கிட்டும்; தாயார் அறிவார்ந்த பெண்ணாக இருப்பார்.",
      "அழகிய நூலகம் கொண்ட சொகுசு வீடு, நவீன வாகனங்கள் மற்றும் பசுமையான சூழலில் வாழும் யோகம்.",
      "மனதில் நிம்மதியும், நண்பர்களை இன்முகத்துடன் வரவேற்று உபசரிக்கும் பண்பும் இருக்கும்."
    ],
    "core_traits_en": [
      "Scholastic brilliance, multiple advanced academic degrees, and relentless scientific curiosity.",
      "Cherished bond with an erudite, accomplished mother who acts as primary intellectual guide.",
      "Resides in a tastefully decorated home with an extensive personal library and modern vehicles.",
      "Radiates domestic serenity, refined manners, and delightful intellectual hospitality."
    ],
    "strong_placement_ta": [
      "கன்னியில் உச்சம் அல்லது மிதுனத்தில் ஆட்சி பெற்று பத்ர யோகம் அமைந்தால்: பல்கலைக்கழக துணைவேந்தர், பெரும் நூலாசிரியர்.",
      "அரசாங்கத்தால் வழங்கப்படும் உயரிய கௌரவங்கள், நவீன பங்களாக்கள் மற்றும் பூமி லாபம்."
    ],
    "strong_placement_en": [
      "Exalted or own house forming Bhadra Yoga: University Vice-Chancellor, premier scholar-statesman.",
      "Honored with state residences, luxurious fleet of conveyances, and flourishing estates."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: படிப்பில் தடைகள், தாயாரின் நரம்பு மண்டலம் பாதித்தல்.",
      "வீடு மற்றும் வாகனப் பராமரிப்புக்காக அதிக விரயங்கள், சொத்து ஆவணங்களில் மோசடிகள் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Disruptions in higher education, mother's nervous exhaustion, and forged property deeds.",
      "Repeated vehicle repair expenses, domestic anxiety, and insecure residential titles."
    ],
    "career_wealth_ta": [
      "கல்வி நிறுவனங்கள், மென்பொருள் பயிற்சி மையங்கள், வாகன உற்பத்தி மற்றும் விற்பனை, ரியல் எஸ்டேட் ஆவண ஆலோசகர், நூலகத் துறை.",
      "கல்வி சேவைகளாலும் நில ஆவண தரகு மூலமும் அளப்பரிய வருமானம்."
    ],
    "career_wealth_en": [
      "Flourishes in university administration, ed-tech startups, automotive dealership, title deed conveyancing, and libraries.",
      "Generates solid long-term equity through educational assets and commercial realty."
    ],
    "health_precautions_ta": [
      "நெஞ்சு சளி, இருதய நரம்பு பலவீனம், ஆஸ்துமா மற்றும் மன அமைதியின்மை.",
      "பிராணாயாமம், சுத்தமான காற்று மற்றும் எளிதில் செரிக்கும் காய்கறிகள் நலம் தரும்."
    ],
    "health_precautions_en": [
      "Susceptible to pulmonary spasms, intercostal neuralgia, bronchial asthma, and hyperactive anxiety.",
      "Breath control exercises and dwelling in well-ventilated, green environments promote longevity."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 175) & Saravali Ch. 30"
  },
  {
    "planet": "Mercury",
    "planet_name_ta": "புதன்",
    "symbol": "🟢",
    "element": "நிலம் (Prithvi)",
    "house": 5,
    "bhava_category": "trikona",
    "house_title_ta": "5-ஆம் பாவம் - புத்திர பாவம் (மகா மேதை / மந்திர சித்தி & புத்தி)",
    "house_title_en": "5th House - Putra Bhava (Genius Intellect, Mantra Siddhi & Speculation)",
    "core_traits_ta": [
      "அசாத்தியமான புத்திக்கூர்மை, நுட்பமான தர்க்க அறிவு மற்றும் எதிர்காலத்தைக் கணிக்கும் உள்ளுணர்வு.",
      "அறிவார்ந்த, கலை உணர்வுள்ள மற்றும் நல்லொழுக்கம் நிறைந்த குழந்தைகள் அமைவார்கள்.",
      "மந்திர சாஸ்திரங்கள், வேதங்கள், சமஸ்கிருதம் மற்றும் நவீன அறிவியல் ஆய்வுகளில் தேர்ச்சி.",
      "பங்குச் சந்தை, கணித மாதிரிகள் மற்றும் திட்டமிடல் மூலம் துல்லியமாக கணித்துச் சாதிக்கும் ஆற்றல்."
    ],
    "core_traits_en": [
      "Genius-level deductive intellect, deep mathematical modeling skills, and prophetic foresight.",
      "Blessed with witty, intellectually accomplished, and morally upright children.",
      "Mastery over sacred mantras, esoteric scriptures, linguistics, and cutting-edge data science.",
      "Exceptional forecasting ability in financial markets, options algorithms, and strategic gaming."
    ],
    "strong_placement_ta": [
      "சுப பலத்துடன் ஆட்சி அல்லது உச்சம் பெற்றால்: அமைச்சர்களுக்கு முதன்மை ஆலோசகர், நோபல் பரிசு அளவிலான சாதனைகள்.",
      "பூர்வ புண்ணிய பலத்தால் எடுத்த முயற்சிகள் யாவும் பல்கிப் பெருகி கோடிக்கணக்கில் தன லாபம் தரும்."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Chief cabinet strategist, internationally decorated academic pioneer.",
      "Past-life merits unlock frictionless intellectual breakthroughs and colossal financial windfalls."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: குழந்தைகளின் நரம்பு மண்டலம் பாதித்தல், கல்வியில் மந்த நிலை.",
      "பங்கு வர்த்தகத்தில் தவறான கணக்குகளால் பெரும் நிதி இழப்புகள் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Cognitive fatigue in children, learning disabilities in offspring.",
      "Disastrous financial bleedings caused by erratic speculative gambling and flawed algorithms."
    ],
    "career_wealth_ta": [
      "டேட்டா சயின்டிஸ்ட், செயற்கை நுண்ணறிவு (AI) ஆய்வாளர், பங்குச் சந்தை ஃபண்ட் மேனேஜர், நாடக ஆசிரியர், ஜோதிட ஆராய்ச்சியாளர்.",
      "அறிவுசார் படைப்புகளாலும் துல்லியமான முதலீடுகளாலும் கோடீஸ்வர யோகம்."
    ],
    "career_wealth_en": [
      "Distinction as quantitative fund manager, AI algorithm architect, playwright, data scientist, and astrological scholar.",
      "Reaps monumental fortunes through proprietary patents, copyrights, and algorithmic trading."
    ],
    "health_precautions_ta": [
      "அஜீரணம், வயிற்றில் வாயுத் தொல்லை, குடல் நரம்பு பலவீனம் மற்றும் தலைவலி.",
      "சரியான நேரத்திற்கு எளிமையான உணவை உண்பதும், அதிக மன உளைச்சலைத் தவிர்ப்பதும் அவசியம்."
    ],
    "health_precautions_en": [
      "Prone to nervous dyspepsia, gastrointestinal bloating, irritable bowel syndrome, and tension headaches.",
      "Maintain timely meals, avoid intellectual burnout, and consume gut-soothing herbal teas."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 220) & Saravali Ch. 30"
  },
  {
    "planet": "Mercury",
    "planet_name_ta": "புதன்",
    "symbol": "🟢",
    "element": "நிலம் (Prithvi)",
    "house": 6,
    "bhava_category": "dusthana",
    "house_title_ta": "6-ஆம் பாவம் - சத்ரு பாவம் (சாதுரியத்தால் எதிரிகளை வெல்லுதல்)",
    "house_title_en": "6th House - Satru Bhava (Defeating Adversaries Through Wit)",
    "core_traits_ta": [
      "புத்தி சாதுரியத்தாலும், பேச்சுத் திறனாலும் எதிரிகளையும் போட்டியாளர்களையும் எளிதில் வீழ்த்துவார்.",
      "வழக்குகளிலும் சட்டப் போராட்டங்களிலும் தர்க்க வாதங்களை முன்வைத்து வெற்றி வாகை சூடுவார்.",
      "கடுமையான உழைப்பாளி; கணக்கு வழக்குகளையும் அலுவலகப் பணிகளையும் துல்லியமாக நிர்வகிப்பார்.",
      "தாய்மாமனுடன் நல்ல நட்பும் வணிகத் தொடர்புகளும் கொண்டிருப்பார்."
    ],
    "core_traits_en": [
      "Subdues competitors and legal adversaries through tactical intellectual maneuver rather than blunt force.",
      "Triumphs decisively in complex litigations and arbitration through razor-sharp analytical arguments.",
      "Meticulous, tireless worker with unmatched precision in administrative ledgering.",
      "Enjoys fruitful commercial collaborations and mutual goodwill with maternal relatives."
    ],
    "strong_placement_ta": [
      "கன்னியில் உச்சம் பெற்று சுப பலத்துடன் இருப்பின்: எதிரிகள் இல்லாத பெருவாழ்வு, நிதி மோசடிகளைக் கண்டறியும் உயர் பதவி.",
      "அளப்பரிய செல்வம், கடன் இல்லாத அமைதியான வாழ்க்கை மற்றும் சமூகத்தில் உயர்ந்த மரியாதை."
    ],
    "strong_placement_en": [
      "Exalted in Virgo with benefics: Total eradication of adversaries; heads anti-corruption/forensic regulatory agencies.",
      "Vast accumulated capital, completely debt-free living, and unassailable civic respect."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தோல் அலர்ஜி, நரம்புத் தளர்ச்சி, கடன்களால் மன உளைச்சல்.",
      "வேலையாட்களால் கணக்குத் தில்லுமுல்லுகள் மற்றும் தாய்மாமனுடன் கருத்து மோதல்கள் வரலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Chronic dermatological rashes, nervous twitching, and anxiety over unsettled debts.",
      "Embezzlement by untrustworthy accountants or clerks; disputes with maternal uncles."
    ],
    "career_wealth_ta": [
      "சட்டத்துறை, தணிக்கை மற்றும் வரி ஆலோசகர் (Tax Consultant), மருத்துவப் பரிசோதனையாளர், வங்கியாளர், பொது நிர்வாகம்.",
      "போட்டிகளைத் தனக்குச் சாதகமாக மாற்றி வணிக லாபங்களை ஈட்டுவார்."
    ],
    "career_wealth_en": [
      "Excels in corporate taxation, forensic accounting, clinical pathology, banking risk management, and labor arbitration.",
      "Turns competitor blunders into handsome commercial windfalls."
    ],
    "health_precautions_ta": [
      "குடல் அழற்சி, நரம்புத் தளர்ச்சி, சரும நோய்கள், ஆஸ்துமா மற்றும் மலச்சிக்கல்.",
      "நார்ச்சத்து மிகுந்த காய்கறிகளையும் பழங்களையும் உண்பதும், தோலை சுத்தமாகப் பராமரிப்பதும் நலம் தரும்."
    ],
    "health_precautions_en": [
      "Susceptible to colitis, nervous exhaustion, eczema, bronchial allergies, and chronic constipation.",
      "High-fiber dietary regimen, probiotics, and dermatological care are essential."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 261) & Saravali Ch. 30"
  },
  {
    "planet": "Mercury",
    "planet_name_ta": "புதன்",
    "symbol": "🟢",
    "element": "நிலம் (Prithvi)",
    "house": 7,
    "bhava_category": "kendra",
    "house_title_ta": "7-ஆம் பாவம் - களத்திர பாவம் (அறிவார்ந்த துணை & வர்த்தகக் கூட்டாண்மை)",
    "house_title_en": "7th House - Kalathra Bhava (Erudite Spouse & Commercial Alliances)",
    "core_traits_ta": [
      "அழகான, அறிவார்ந்த, பேச்சாற்றலும் வணிக ஞானமும் நிறைந்த வாழ்க்கைத் துணை அமைவார்.",
      "தம்பதியரிடையே அறிவுசார் உரையாடல்களும், நகைச்சுவையும், பரஸ்பர மரியாதையும் நிறைந்திருக்கும்.",
      "கூட்டு வர்த்தகத்தில் (Partnership) அளப்பரிய வெற்றி; ஒப்பந்தங்களை நேர்த்தியாக முடிக்கும் சாதுரியம்.",
      "பொதுமக்கள் தொடர்பிலும் தூதரகப் பணிகளிலும் சிறந்த நற்பெயரையும் செல்வாக்கையும் பெறுவார்."
    ],
    "core_traits_en": [
      "Blessed with a charming, intellectually brilliant, articulate, and commercially astute spouse.",
      "Marital life sparkles with witty repartee, shared literary pursuits, and deep intellectual companionship.",
      "Sensational success in commercial partnerships; negotiates joint contracts with masterly finesse.",
      "Natural diplomat in public interactions, arbitration boards, and overseas commercial consortia."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: புகழ்பெற்ற செல்வந்த குடும்பத்திலிருந்து அறிவுக்களஞ்சியமான துணை அமைவார்.",
      "பன்னாட்டு வர்த்தகத்தில் பெரும் லாபமும், சமூகத்தில் சிறந்த தம்பதியராகப் போற்றப்படும் நிலையும் கிட்டும்."
    ],
    "strong_placement_en": [
      "Exalted or own house: Marries into a prominent, scholarly, and affluent dynasty; partner contributes directly to business expansion.",
      "Reaps huge fortunes from transnational trade agreements and commands widespread civic respect."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: திருமணத்தில் காலதாமதம், துணையுடன் வாக்குவாதங்கள்.",
      "கூட்டுத் தொழிலில் பங்குதாரர்களால் ஒப்பந்த மீறல்கள் மற்றும் பண இழப்புகள் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Delay in marital union, intellectual disputes causing domestic estrangement.",
      "Breach of contract by commercial partners resulting in arbitration costs and capital loss."
    ],
    "career_wealth_ta": [
      "சர்வதேச வர்த்தகம், ஏற்றுமதி-இறக்குமதி, மக்கள் தொடர்பு மேலாண்மை, சட்ட ஒப்பந்தங்கள், விநியோகஸ்தர் ஏஜென்சி.",
      "வாழ்க்கைத் துணையின் ஆலோசனைகளாலும் கூட்டுத் தொழிலாலும் தன வரவு பலமடங்கு உயரும்."
    ],
    "career_wealth_en": [
      "Dominant in cross-border trade, import-export logistics, public relations, corporate contract law, and retail distribution.",
      "Vast wealth multiplication achieved via spousal counsel and well-structured joint ventures."
    ],
    "health_precautions_ta": [
      "சிறுநீரகக் கோளாறுகள், நரம்புத் தளர்ச்சி, அடிவயிற்றில் வலி மற்றும் தோல் அரிப்பு.",
      "முறையான நீர் அருந்துதலும், நரம்புகளைத் தளர்வாக்கும் பயிற்சிகளும் ஆரோக்கியத்திற்கு உதவும்."
    ],
    "health_precautions_en": [
      "Vulnerable to renal sensitivity, pelvic nervous strain, urinary irritation, and skin rashes.",
      "Abundant hydration and routine pelvic floor relaxation maintain health."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Mercury",
    "planet_name_ta": "புதன்",
    "symbol": "🟢",
    "element": "நிலம் (Prithvi)",
    "house": 8,
    "bhava_category": "dusthana",
    "house_title_ta": "8-ஆம் பாவம் - ஆயுள் பாவம் (தீர்க்காயுள் / மறைமுக ஞானம் & உயில் தனம்)",
    "house_title_en": "8th House - Ayur Bhava (Long Longevity, Occult Lore & Legacies)",
    "core_traits_ta": [
      "புதன் 8-ஆம் பாவத்தில் அமர்வது நீண்ட ஆயுளையும், எதிர்பாராத அதிர்ஷ்டங்களையும் தரும் அமைப்பாகும்.",
      "ரகசிய சாஸ்திரங்கள், ஜோதிடம், குறியீட்டு முறைகள் (Cryptography) மற்றும் மறைமுக உண்மைகளை ஆராய்வதில் வல்லவர்.",
      "ஆபத்தான சூழ்நிலைகளிலும் தன் சாதுரியமான பேச்சால் தப்பிக்கும் விவேகம் கொண்டவர்.",
      "அரசாங்கத் தணிக்கைகள் அல்லது ஒப்பந்த ஆவணங்களில் மிகுந்த எச்சரிக்கையுடன் கையெழுத்திட வேண்டும்."
    ],
    "core_traits_en": [
      "Mercury in the 8th is a classical guarantor of extended longevity and sudden unexpected windfalls.",
      "Profound mastery over esoteric symbology, cryptographic coding, astrology, and forensic research.",
      "Escapes precarious dangers using razor-sharp presence of mind and persuasive diplomacy.",
      "Must maintain impeccable transparency in statutory filings and signed contractual documentation."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: மாபெரும் உயில் சொத்துகள், காப்பீட்டுத் தொகைகள், பூரண தீர்க்காயுள்.",
      "மறைமுகத் தொழில் மூலம் கோடிக்கணக்கில் வருமானம் மற்றும் உலகப் புகழ் பெற்ற ஆராய்ச்சியாளராகத் திகழுதல்."
    ],
    "strong_placement_en": [
      "Strong or exalted: Bestows massive ancestral bequests, life insurance endowments, and robust long life.",
      "Monetizes proprietary data analytics and covert algorithms into immense confidential wealth."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: நரம்புத் தளர்ச்சி, மூளை சோர்வு, கண் உபாதைகள்.",
      "பங்கு வர்த்தகத்தில் திடீர் சரிவுகள், ஏமாற்றங்கள் மற்றும் உயில் விவகாரங்களில் வழக்குகள் வரலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Nervous exhaustion, brain fog, chronic insomnia, and speech stammers under pressure.",
      "Sudden market crashes eroding speculative gains; protracted probate litigations."
    ],
    "career_wealth_ta": [
      "தடயவியல் கணக்காளர், சைபர் செக்யூரிட்டி நிபுணர், உளவுத்துறை பகுப்பாய்வாளர், இன்சூரன்ஸ் தணிக்கையாளர், காப்புரிமை வழக்கறிஞர்.",
      "உயில் சொத்துகள், திடீர் டிவிடெண்டுகள் மற்றும் மறைமுக ஒப்பந்தங்கள் மூலம் தன வரவு."
    ],
    "career_wealth_en": [
      "Eminence in forensic audit, cybersecurity encryption, intelligence analytics, insurance claims, and patent law.",
      "Gains unearned wealth through inheritances, court settlements, and confidential contracts."
    ],
    "health_precautions_ta": [
      "நரம்புத் தளர்ச்சி, மன அழுத்தம், பக்கவாதம் அபாயம், செரிமானக் கோளாறுகள் மற்றும் மலச்சிக்கல்.",
      "தியானம், நல்ல தூக்கம் மற்றும் நரம்புகளை அமைதிப்படுத்தும் ஊட்டச்சத்துகள் அவசியம்."
    ],
    "health_precautions_en": [
      "Prone to nervous breakdown, peripheral neuropathy, cognitive burnout, and sluggish bowels.",
      "Requires calming meditation, sound sleep hygiene, and B-complex vitamin supplementation."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Mercury",
    "planet_name_ta": "புதன்",
    "symbol": "🟢",
    "element": "நிலம் (Prithvi)",
    "house": 9,
    "bhava_category": "trikona",
    "house_title_ta": "9-ஆம் பாவம் - பாக்கிய பாவம் (தர்ம சிந்தனை, உயர்கல்வி & குருவருள்)",
    "house_title_en": "9th House - Bhagya Bhava (Righteous Wisdom, Higher Learning & Guru's Grace)",
    "core_traits_ta": [
      "உன்னதமான தர்ம சிந்தனை, தத்துவ ஞானம், பக்தி மற்றும் பெரியோர்களை மதிக்கும் நற்பண்புகள்.",
      "தந்தையின் மீது பாசமும், தந்தை வழியில் சிறந்த அறிவுரைகளும் வழிகாட்டல்களும் கிட்டும்.",
      "வெளிநாட்டுப் பல்கலைக்கழகங்களில் கல்வி பயிலும் யோகம் மற்றும் பன்னாட்டு ஆய்வுகளில் வெற்றி.",
      "மத நல்லிணக்கம், ஆன்மீக நூல்களை எழுதுதல் மற்றும் சமுதாயத்திற்கு நல்ல கருத்துகளைப் போதிக்கும் ஆற்றல்."
    ],
    "core_traits_en": [
      "Sublime ethical nobility, deep philosophical learning, pious devotion, and reverent mentorship.",
      "Harmonious, inspiring relationship with an intellectual father whose counsel guides life choices.",
      "High fortune in gaining admission to premier global universities and spearheading cross-border studies.",
      "Promotes interfaith harmony, publishes spiritual treatises, and inspires seekers through lucid discourse."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: அகண்ட பாக்கிய யோகம், அரசாங்க சர்வதேசத் தூதர், உலகளாவிய கௌரவம்.",
      "நிறுவனங்களைத் தோற்றுவித்து சர்வதேச அளவில் பல்லாயிரக்கணக்கான மாணவர்களுக்குக் கல்வி புகட்டும் சாதனை."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Bestows supreme Bhagya Yoga; appointed as international ambassador or cultural delegate.",
      "Founds global academic institutions and chairs worldwide philanthropic educational endowments."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: உயர்கல்வியில் தடைகள், தந்தையின் நரம்பு ஆரோக்கியம் பாதித்தல்.",
      "மத விஷயங்களில் வீண் வாதங்கள், வெளிநாட்டுப் பயணங்களில் ஆவணக் குறைபாடுகளால் இழப்புகள்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Academic disruptions in postgraduate studies, paternal nervous frailty.",
      "Futile ideological arguments and costly visa or documentation delays during international travel."
    ],
    "career_wealth_ta": [
      "பல்கலைக்கழகப் பேராசிரியர், சர்வதேசச் சட்ட ஆலோசகர், மத அறக்கட்டளைத் தலைவர், பதிப்பக அதிபர், ஆன்மீக எழுத்தாளர்.",
      "கல்வி, தர்ம வழிகள் மற்றும் பன்னாட்டு அறிவுசார் பரிமாற்றங்கள் மூலம் கோடீஸ்வர யோகம்."
    ],
    "career_wealth_en": [
      "Distinguished as university chair professor, international legal jurist, publishing conglomerate executive, and author.",
      "Amasses pure, untainted wealth through educational licensing and intellectual cross-border initiatives."
    ],
    "health_precautions_ta": [
      "தொடை நரம்பு வலி (Sciatica), இடுப்புப் பிடிப்பு, கல்லீரல் மந்தம் மற்றும் உடல் சோர்வு.",
      "முறையான நடைப்பயிற்சியும், உடலை வளைக்கும் ஆசனங்களும் ஆரோக்கியம் தரும்."
    ],
    "health_precautions_en": [
      "Susceptible to femoral neuropathy, sciatica sensitivity, sluggish hepatic bile, and fatigue.",
      "Daily stretching routines and brisk walking optimize lower extremity nerve vitality."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Mercury",
    "planet_name_ta": "புதன்",
    "symbol": "🟢",
    "element": "நிலம் (Prithvi)",
    "house": 10,
    "bhava_category": "kendra",
    "house_title_ta": "10-ஆம் பாவம் - ஜீவன பாவம் (வர்த்தக சாம்ராஜ்யம் & தொழில் வெற்றி)",
    "house_title_en": "10th House - Karma Bhava (Commercial Empire & Professional Glory)",
    "core_traits_ta": [
      "வணிகத்தில் அசுர வேகம், தொழில் மேலாண்மை மற்றும் பல துறைகளில் ஒரே நேரத்தில் வெற்றிபெறும் ஆற்றல்.",
      "அரசாங்க உயர் அதிகாரிகளுடனும் தொழில் அதிபர்களுடனும் சுமுகமான நட்பும் செல்வாக்கும்.",
      "நேர்மையான நிர்வாகம், புதுமையான தொழில் யுக்திகள் மற்றும் பல்லாயிரக்கணக்கானோரை வழிநடத்தும் திறன்.",
      "சமூகத்தில் பெரும் புகழும், கௌரவப் பட்டங்களும், அழியாத தொழில் முத்திரையும் பெறுவார்."
    ],
    "core_traits_en": [
      "Dynamic commercial acumen, masterly enterprise leadership, and effortless multitasking across diverse ventures.",
      "Commands high respect and lucrative patronage among top governmental regulators and industrialists.",
      "Ethical administrative governance combined with cutting-edge innovations; natural corporate leader.",
      "Crowns life with enduring public renown, honorary academic doctorates, and celebrated institutional status."
    ],
    "strong_placement_ta": [
      "கன்னியில் உச்சம் அல்லது மிதுனத்தில் ஆட்சி பெற்று பத்ர யோகம் அமைந்தால்: நாட்டின் முன்னணி வர்த்தக சாம்ராஜ்ய அதிபர், நிதி மந்திரி யோகம்.",
      "பன்னாட்டு மென்பொருள் மற்றும் ஊடக நிறுவனங்களின் தலைவர் அந்தஸ்து மற்றும் அரச கௌரவம்."
    ],
    "strong_placement_en": [
      "Exalted or own house with Bhadra Yoga: Titan of national commerce, finance minister or central bank governor.",
      "Chairman of multinational software conglomerates and recipient of peak civic decorations."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தொழிலில் அடிக்கடி மாற்றங்கள், தவறான கணக்கு வழக்குகளால் தணிக்கைச் சிக்கல்கள்.",
      "உயர் அதிகாரிகளால் நெருக்கடிகளும், வியாபாரத்தில் வாடிக்கையாளர் நம்பிக்கையை இழத்தலும்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Frequent erratic job switches, accounting discrepancies leading to tax audits.",
      "Regulatory sanctions, sudden commercial setbacks, and erosion of consumer brand trust."
    ],
    "career_wealth_ta": [
      "தகவல் தொழில்நுட்பம், வங்கித் தலைமை, ஊடக நிறுவனம், பங்குச் சந்தை தரகு நிறுவனம், ஆடிட்டிங் நிறுவனம், ஆட்டோமொபைல் மார்க்கெட்டிங்.",
      "தொழில் சாதுரியத்தாலும் வர்த்தக விரிவாக்கத்தாலும் கோடிக்கணக்கில் வற்றாத தன லாபம்."
    ],
    "career_wealth_en": [
      "Dominant in IT software services, investment banking, media networks, audit practices, and global marketing.",
      "Multi-million dollar liquid fortunes accumulated through scalable high-margin commercial expansion."
    ],
    "health_precautions_ta": [
      "மூட்டு வலி, பணிச்சுமையால் நரம்புத் தளர்ச்சி, தூக்கமின்மை மற்றும் தோள்பட்டை இறுக்கம்.",
      "வேலைக்கு நடுவே ஓய்வும், முறையான தூக்கமும் உடல்நலனைப் பாதுகாக்கும்."
    ],
    "health_precautions_en": [
      "Vulnerable to knee osteoarthritis, occupational nervous exhaustion, insomnia, and neck spasms.",
      "Disciplined work-life boundaries and structured sleep schedules preserve vitality."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Mercury",
    "planet_name_ta": "புதன்",
    "symbol": "🟢",
    "element": "நிலம் (Prithvi)",
    "house": 11,
    "bhava_category": "upachaya",
    "house_title_ta": "11-ஆம் பாவம் - லாப பாவம் (அகண்ட தன லாபம் & அறிவுசார் வருவாய்)",
    "house_title_en": "11th House - Labha Bhava (Massive Liquid Gains & Intellectual Inflows)",
    "core_traits_ta": [
      "புதன் 11-ஆம் பாவத்தில் அமைவது தொட்டதெல்லாம் பொன்னாகும் தன லாபத்தைத் தரும் மிகச் சிறந்த யோகமாகும்.",
      "குறைந்த முதலீட்டில் பல மடங்கு லாபம் ஈட்டும் வணிகச் சாதுரியம்; ஆசைகள் அனைத்தும் எளிதில் நிறைவேறும்.",
      "அறிவார்ந்த நண்பர்கள், எழுத்தாளர்கள், தொழில் அதிபர்களின் விரிவான நட்பு வட்டம் அமையும்.",
      "மூத்த சகோதரர்களிடம் நல்ல தோழமையும், அவர்களுடன் இணைந்து வணிகம் செய்து முன்னேறும் யோகமும் உண்டு."
    ],
    "core_traits_en": [
      "Mercury in the 11th is a peerless generator of exponential financial profit and compounding wealth.",
      "Extraordinary skill in multiplying capital with lean overheads; swift realization of long-term aspirations.",
      "Surrounded by a stellar network of erudite friends, venture capitalists, authors, and industry pioneers.",
      "Harmonious camaraderie with elder siblings, often partnering with them on lucrative intellectual enterprises."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: எண்ணற்ற வழிகளிலிருந்து பணம் கொட்டும், நவீன பங்களாக்கள், ஆடம்பர வாழ்க்கை.",
      "பங்கு வர்த்தகம், தகவல் தொழில்நுட்பம் மற்றும் முதலீட்டு நிறுவனங்களில் மாபெரும் முதலீட்டாளராக உயருதல்."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Bestows unceasing multichannel cash flows, premier residential estates, and luxury assets.",
      "Rises as a celebrated venture angel investor in tech unicorns, equities, and media companies."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: நண்பர்களால் ஏமாற்றப்படுதல், எதிர்பார்க்கும் தரகுத் தொகைகள் கைநழுவுதல்.",
      "மூத்த சகோதரருடன் சொத்துத் தகராறுகள் அல்லது பிரிவுகள் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Exploitation by counterfeit associates, delayed commissions, and unpaid invoices.",
      "Estrangement or legal disputes with elder brother over commercial division of assets."
    ],
    "career_wealth_ta": [
      "வென்ச்சர் கேபிடல், பங்குச் சந்தை அல்காரிதம், கமிஷன் ஏஜென்சி, ஈ-காமர்ஸ், டிஜிட்டல் தளங்கள், மென்பொருள் உரிமங்கள்.",
      "புத்தி சாதுரியத்தாலும் முதலீட்டுப் பெருக்கத்தாலும் கோடீஸ்வர அந்தஸ்து."
    ],
    "career_wealth_en": [
      "Lucrative success in venture funds, algorithmic equity trading, e-commerce networks, and software licensing.",
      "Vast fortune generated from automated royalties and digital asset platforms."
    ],
    "health_precautions_ta": [
      "இடது காது வலி, கணுக்கால் நரம்பு இழுத்தல், கைகளில் நடுக்கம் மற்றும் தோல் அரிப்பு.",
      "கால் நரம்புகளுக்கான உடற்பயிற்சியும், காது ஆரோக்கியத்தைப் பேணுதலும் நல்லது."
    ],
    "health_precautions_en": [
      "Susceptible to left-ear ache, ankle ligament stiffness, hand tremors, and skin itching.",
      "Daily ankle mobility drills and preventive otic hygiene keep limbs supple."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Mercury",
    "planet_name_ta": "புதன்",
    "symbol": "🟢",
    "element": "நிலம் (Prithvi)",
    "house": 12,
    "bhava_category": "dusthana",
    "house_title_ta": "12-ஆம் பாவம் - விரய பாவம் (அயன சயனம், வெளிநாட்டு யோகம் & ஆன்மீகம்)",
    "house_title_en": "12th House - Vraya & Moksha Bhava (Foreign Success, Solitude & Deep Research)",
    "core_traits_ta": [
      "தனிமையில் அமர்ந்து ஆழ்ந்த ஆராய்ச்சி செய்வதிலும், எழுதுவதிலும், தியானிப்பதிலும் பேரானந்தம் அடைவார்.",
      "பிறந்த ஊரை விட வெளிநாடுகளிலோ அல்லது கடல் கடந்த இடங்களிலோ அபரிமிதமான வெற்றியும் புகழும் கிட்டும்.",
      "பணத்தை கல்வி நிறுவனங்கள், புத்தகங்கள் மற்றும் தர்ம காரியங்களுக்காக தாராளமாகச் செலவிடுவார்.",
      "அரசாங்க வரி விவகாரங்களிலும் சட்ட ஆவணங்களிலும் எச்சரிக்கையுடன் கையெழுத்திட வேண்டும்."
    ],
    "core_traits_en": [
      "Finds profound creative joy in tranquil solitude, deep scholarly research, philosophical writing, and meditation.",
      "Realizes spectacular career elevation and wealth when operating in distant overseas lands.",
      "Spends generously on educational charities, esoteric books, philanthropic trusts, and scholastic scholarships.",
      "Must practice diligence in tax compliance, offshore accounting, and signed statutory filings."
    ],
    "strong_placement_ta": [
      "சுப பலத்துடன் இருப்பின்: வெளிநாட்டில் மாபெரும் கல்வி சாம்ராஜ்யம், சர்வதேச தூதரகம், மோட்ச சாதனை.",
      "அயன சயன சுகம், நல்ல தூக்கம் மற்றும் வெளிநாட்டு நாணயங்கள் மூலம் அளப்பரிய தன வரவு."
    ],
    "strong_placement_en": [
      "Well-placed with benefics: Vast academic or IT operations abroad, international diplomacy, and spiritual illumination.",
      "Enjoys restorative sleep, psychic balance, and tremendous income denominated in strong foreign currencies."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தூக்கமின்மை, நரம்புத் தளர்ச்சி, தவறான ஆவணங்களால் அபராதங்கள்.",
      "இடது கண் பார்வைக் குறைபாடு, மனக் குழப்பம் மற்றும் வீண் மருத்துவச் செலவுகள்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Severe insomnia, nervous anxiety, and penalties incurred from forged or flawed papers.",
      "Left eye vision defects, mental disorientation, and burdensome clinical expenses."
    ],
    "career_wealth_ta": [
      "சர்வதேச மென்பொருள் ஏற்றுமதி, வெளிநாட்டுத் தூதரகங்கள், சர்வதேச கப்பல் மற்றும் வான்வழி சரக்கு, மொழிபெயர்ப்பாளர், ஆன்மீக நூலகங்கள்.",
      "அந்நிய முதலீடுகளாலும் பன்னாட்டு நிறுவனங்களின் மூலமும் தொடர் தன வரவு."
    ],
    "career_wealth_en": [
      "Thrives in cross-border software export, consular services, aviation cargo, technical translation, and overseas research.",
      "Accumulates substantial wealth through foreign currency reserves and offshore contracts."
    ],
    "health_precautions_ta": [
      "இடது கண் பார்வை பாதிப்பு, பாதங்களில் நரம்பு வலி, தூக்கமின்மை மற்றும் தோல் வியாதிகள்.",
      "படுக்கும் முன் கண்களைக் குளிர்ந்த நீரால் கழுவுதலும், தியானமும் மன அமைதியைத் தரும்."
    ],
    "health_precautions_en": [
      "Prone to left-eye refractive strain, peripheral foot neuropathy, insomnia, and dermatological rashes.",
      "Nightly ocular cold-compresses and grounding meditation induce deep restorative sleep."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Jupiter",
    "planet_name_ta": "குரு",
    "symbol": "🟡",
    "element": "ஆகாயம் (Akasha)",
    "house": 1,
    "bhava_category": "kendra",
    "house_title_ta": "1-ஆம் பாவம் - லக்னம் (திக்பலம் / ஹம்ச யோகம் / மகா ஞானம்)",
    "house_title_en": "1st House - Ascendant / Tanu Bhava (Digbala / Hamsa Yoga / Supreme Wisdom)",
    "core_traits_ta": [
      "குரு லக்னத்தில் திக்பலம் (Digbala) பெற்று அமர்வது கோடி நன்மைகளைத் தரும் மகா புண்ணிய அமைப்பாகும்.",
      "கம்பீரமான, வசீகரமான, தங்க நிற மேனி, பரந்த நெற்றி மற்றும் தெய்வீகக் களை பொருந்திய அழகிய முகம்.",
      "அசைக்க முடியாத தன்னம்பிக்கை, நேர்மை, உயர்ந்த ஒழுக்கம் மற்றும் சுயமரியாதைக்கு முதலிடம் தரும் சுபாவம்.",
      "ஆன்மீகம், வேதம், சட்டம் மற்றும் மெய்யியலில் ஆழ்ந்த ஞானம்; சமுதாயத்தின் உன்னத வழிகாட்டியாகத் திகழ்வார்.",
      "எந்தப் பாப தோஷங்களையும் போக்கும் ஆற்றல்; ஒரு லட்சம் தோஷங்களை நிவர்த்தி செய்யும் தேவ குருவின் நேரடி பார்வை."
    ],
    "core_traits_en": [
      "Jupiter achieves supreme Digbala (directional potency) in the 1st house; celebrated as canceling a hundred thousand chart flaws.",
      "Noble, majestic, and commanding physical presence; golden aura, broad forehead, and radiant countenance.",
      "Unshakeable self-confidence, uncompromising righteousness, spotless moral integrity, and high personal dignity.",
      "Mastery of theology, jurisprudence, statecraft, and higher philosophy; natural statesman and preceptor.",
      "Radiates benign spiritual protection, uplifting everyone who comes into his orbit."
    ],
    "strong_placement_ta": [
      "கடகத்தில் உச்சம் அல்லது தனுசு/மீனத்தில் ஆட்சி பெற்று ஹம்ச யோகம் (Hamsa Yoga) அமைந்தால்: நாட்டின் தலைமை நீதிபதி, ஜனாதிபதி, ஜகத்குரு யோகம்.",
      "வாழ்நாள் முழுவதும் குறைவற்ற செல்வம், உலகெங்கும் சீடர்கள் மற்றும் சரித்திரத்தில் அழியாத பொற்பெயர்."
    ],
    "strong_placement_en": [
      "Exalted in Cancer or in own signs Sagittarius/Pisces forming Hamsa Mahapurusha Yoga: Chief Justice, Prime Minister, World Spiritual Preceptor.",
      "Enduring multi-generational wealth, millions of devoted followers, and golden historical immortality."
    ],
    "weak_placement_ta": [
      "மகரத்தில் நீசம் அல்லது ராகுவின் சேர்க்கை (குரு சண்டாள யோகம்) பெற்றால்: உடல் பருமன், கல்லீரல் பாதிப்பு, மத நம்பிக்கைகளில் குழப்பம்.",
      "அளவுக்கு மீறிய நம்பிக்கை வைத்து ஏமாறுதல் அல்லது கௌரவக் குறைவுகள் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated in Capricorn or conjunct Rahu (Guru Chandala Yoga): Severe obesity, hepatic imbalances, and doctrinal disillusionment.",
      "Vulnerability to exploitation through naive credulity; occasional setbacks to public prestige."
    ],
    "career_wealth_ta": [
      "தலைமை நீதிபதி, சட்ட வல்லுநர், பல்கலைக்கழக வேந்தர், மத்திய மந்திரி, சர்வதேச நிதி ஆலோசகர், ஆன்மீக பீடாதிபதி.",
      "அரசாங்க விருதுகள், கௌரவப் பதவிகள் மற்றும் தர்ம வழியில் கோடிக்கணக்கான சொத்துச் சேர்க்கை."
    ],
    "career_wealth_en": [
      "Peerless career as supreme appellate judge, constitutional luminary, university chancellor, cabinet minister, and pontiff.",
      "Amasses vast, clean wealth through state patronage, high consultancy, and ethical leadership."
    ],
    "health_precautions_ta": [
      "உடல் பருமன் (Obesity), கல்லீரல் கொழுப்பு (Fatty Liver), நீரிழிவு நோய் (Diabetes) மற்றும் ரத்தக் கொதிப்பு.",
      "மிதமான சாத்வீக உணவுகளும், சர்க்கரையைக் கட்டுப்படுத்துவதும், தினசரி நடைப்பயிற்சியும் அவசியம்."
    ],
    "health_precautions_en": [
      "Prone to metabolic obesity, hepatic steatosis (fatty liver), diabetes mellitus, and high triglycerides.",
      "Adhere to a low-glycemic sattvic diet, eliminate refined sugars, and maintain daily brisk walking."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 53) & Saravali Ch. 30"
  },
  {
    "planet": "Jupiter",
    "planet_name_ta": "குரு",
    "symbol": "🟡",
    "element": "ஆகாயம் (Akasha)",
    "house": 2,
    "bhava_category": "panaphara",
    "house_title_ta": "2-ஆம் பாவம் - தன பாவம் (வாக்கு பலிதம், அகண்ட தனம் & குடும்ப நலம்)",
    "house_title_en": "2nd House - Dhana Bhava (Prophetic Speech & Boundless Wealth)",
    "core_traits_ta": [
      "குரு 2-ஆம் பாவத்தில் அமர்வது வாக்கு பலிதம், சிறந்த கல்வியறிவு மற்றும் அளப்பரிய குடும்ப மகிழ்ச்சியைத் தரும்.",
      "கனிவான, கம்பீரமான மற்றும் கேட்போரை மெய்சிலிர்க்க வைக்கும் தெய்வீகப் பேச்சாற்றல்.",
      "பணத்தை தர்ம வழியில் ஈட்டி பல மடங்காகப் பெருக்கும் பொருளாதாரச் சாதுரியம்.",
      "பெரிய குடும்பம், நற்குணமுள்ள உறவினர்கள் மற்றும் அனைவராலும் மதிக்கப்படும் குடும்பப் பாரம்பரியம்."
    ],
    "core_traits_en": [
      "Jupiter in the 2nd is an illustrious harbinger of prophetic truth in speech, vast learning, and domestic felicity.",
      "Commands a majestic, resonant, and inspiring tone that commands instant silence and reverence.",
      "Accumulates abundant capital through righteous channels and multiplies assets through ethical investment.",
      "Enjoys a large, harmonious family circle rooted in prestigious ancestral lineage."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: குபேர யோகம்! வற்றாத தங்கக் கையிருப்பு, பல நூறு கோடி சொத்துகள், வாக்கு பலிதம்.",
      "குடும்பத்தில் அனைவரும் கல்வியாளர்களாகவும் செல்வந்தர்களாகவும் திகழ்ந்து குலப் பெருமையைக் காப்பார்கள்."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Bestows Kubera Yoga! Immense reserves of gold bullion, multi-million dollar liquidity, and infallible speech.",
      "Family lineage thrives with generational scholars, philanthropists, and dignified community leaders."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தவறான முதலீடுகளால் தன இழப்பு, குடும்பத்தில் முரண்பாடுகள்.",
      "பற்களில் நோய், வாய் துர்நாற்றம் அல்லது தொண்டையில் கட்டிகள் வரலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Financial hemorrhaging through misplaced altruism, domestic disputes, and speech harshness.",
      "Susceptible to dental caries, oral lesions, and chronic thyroid/throat inflammations."
    ],
    "career_wealth_ta": [
      "வங்கி அதிபர், நிதி அமைச்சகம், நீதித்துறை, பெரிய கல்வி நிறுவனங்கள், தங்க/நகை வர்த்தகம், அறக்கட்டளைகள்.",
      "வாக்கு பலிதத்தாலும் நிதி மேலாண்மையாலும் தலைமுறை தலைமுறைக்கும் அழியாத செல்வம்."
    ],
    "career_wealth_en": [
      "Superlative success in banking chairmanships, ministry of finance, judiciary, university trusts, and bullion commerce.",
      "Creates generational wealth through visionary stewardship and prudent asset preservation."
    ],
    "health_precautions_ta": [
      "தொண்டை சதை வளர்ச்சி, தைராய்டு கோளாறுகள், நாக்கில் புண்கள் மற்றும் பல் வியாதிகள்.",
      "உப்பு கலந்த வெதுவெதுப்பான நீரால் தொண்டையை கொப்பளிப்பதும், இனிப்புகளைக் குறைப்பதும் நல்லது."
    ],
    "health_precautions_en": [
      "Vulnerable to thyroid dysfunctions, tonsillar hypertrophy, oral ulcers, and dental decay.",
      "Warm saline gargling, minimal processed sugar intake, and annual dental checkups are advised."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 100) & Saravali Ch. 30"
  },
  {
    "planet": "Jupiter",
    "planet_name_ta": "குரு",
    "symbol": "🟡",
    "element": "ஆகாயம் (Akasha)",
    "house": 3,
    "bhava_category": "upachaya",
    "house_title_ta": "3-ஆம் பாவம் - சகஜ பாவம் (தர்ம தைரியம் & சகோதர ஆசி)",
    "house_title_en": "3rd House - Sahaja Bhava (Righteous Fortitude & Sibling Goodwill)",
    "core_traits_ta": [
      "அமைதியான, உறுதியான மனத்துணிச்சல்; அநீதிக்கு எதிராக தர்ம வழியில் போராடும் குணம்.",
      "சகோதர சகோதரிகளிடம் அதிக அன்பும், அவர்களுக்குத் தேவையான அறிவுரைகளையும் உதவிகளையும் செய்யும் வழிகாட்டியாகத் திகழ்வார்.",
      "உன்னதமான எழுத்தாற்றல், ஆன்மீக தத்துவங்களை எளிய நடையில் விளக்கும் சொல்வளம்.",
      "தீர்த்த யாத்திரைகள், ஆன்மீகப் பயணங்கள் மற்றும் புனித நதிகளில் நீராடுவதில் மிகுந்த ஈடுபாடு உண்டு."
    ],
    "core_traits_en": [
      "Calm, steadfast fortitude; champions righteousness through intellectual conviction and moral authority.",
      "Devoted guardian and mentor to siblings, extending paternal guidance and material support.",
      "Distinguished literary prose; translates complex metaphysical treatises into lucid, inspiring literature.",
      "Deep affinity for pilgrimages, visiting ancient hermits, and bathing in sanctified river confluences."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: சர்வதேசப் புகழ்பெற்ற ஆன்மீக எழுத்தாளர், தத்துவ மாமேதை, சகோதரர்களால் பெரும் மேன்மை.",
      "எடுத்த காரியங்கள் அனைத்திலும் தெய்வீக வெற்றி; எந்த முயற்சியிலும் தோல்வியைத் தழுவாத நிலை."
    ],
    "strong_placement_en": [
      "Strong or exalted: Internationally celebrated metaphysical author, philosophical savant, and proud brothers.",
      "Divine grace crowns all initiatives with triumphant fruition; shielded against worldly failure."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: சகோதரர்களுடன் கருத்து வேறுபாடுகள், கைகளில் வலி.",
      "முயற்சிகளில் காலதாமதம் மற்றும் தேவையில்லாத சந்தேகங்களால் மன சோர்வு."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Strained relations with brothers, fatigue in arms, and lack of decisive enterprise.",
      "Pessimistic procrastination hindering literary and commercial achievements."
    ],
    "career_wealth_ta": [
      "ஆன்மீக வெளியீட்டாளர், மத விரிவுரையாளர், உயர்நிலை தகவல் தொடர்பு, தத்துவ நூலாசிரியர், தொண்டு நிறுவனங்கள்.",
      "எழுத்து, அறிவுரை மற்றும் தர்ம காரியங்கள் மூலம் கௌரவமான செல்வச் சேர்க்கை."
    ],
    "career_wealth_en": [
      "Flourishes in spiritual publishing, ethical telecommunications, motivational lecturing, and charitable trusts.",
      "Honorable wealth gained through intellectual consulting, royalties, and philanthropic syndicates."
    ],
    "health_precautions_ta": [
      "தோள்பட்டை வலி, கைகளில் நரம்புப் பிடிப்பு, காதுகளில் மந்தம் மற்றும் தசை இறுக்கம்.",
      "முறையான யோகாசனங்களும், உடற்பயிற்சியும் உடலை ஆரோக்கியமாக வைத்திருக்கும்."
    ],
    "health_precautions_en": [
      "Susceptible to shoulder stiffness, upper arm neuralgia, auditory dullness, and muscular tension.",
      "Yogic asanas and gentle arm stretching optimize upper quadrant vitality."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 141) & Saravali Ch. 30"
  },
  {
    "planet": "Jupiter",
    "planet_name_ta": "குரு",
    "symbol": "🟡",
    "element": "ஆகாயம் (Akasha)",
    "house": 4,
    "bhava_category": "kendra",
    "house_title_ta": "4-ஆம் பாவம் - சுக பாவம் (ஹம்ச யோகம் / பூரண சுகம், மாளிகைகள் & தாயன்பு)",
    "house_title_en": "4th House - Sukha Bhava (Hamsa Yoga / Mansions, Inner Peace & Mother's Grace)",
    "core_traits_ta": [
      "குரு 4-ஆம் பாவத்தில் அமர்வது அளவில்லாத மன நிம்மதி, குடும்ப சுகம் மற்றும் உயர் கல்வி யோகத்தைத் தரும்.",
      "தாய் வழியில் அளப்பரிய ஆசியும், தாயார் உன்னத ஆன்மீகப் பெண்ணாக விளங்கி நல்வழிகாட்டுவார்.",
      "பரந்த மாளிகைகள் போன்ற வீடு, நிலபுலன்கள், சொகுசு வாகனங்கள் மற்றும் அமைதியான இல்லற வாழ்க்கை.",
      "வீட்டில் எப்போதும் ஆன்மீகச் சூழல் நிலவும்; விருந்தினர்களுக்கு அன்னதானம் செய்வதில் பேரானந்தம் அடைவார்."
    ],
    "core_traits_en": [
      "Jupiter in the 4th generates profound inner tranquility, supreme domestic contentment, and scholastic distinction.",
      "Blessed by an exceptionally noble, virtuous mother who provides unconditional spiritual nurturing.",
      "Commands palatial residential estates, vast fertile lands, luxury conveyances, and serene domestic bliss.",
      "Home serves as a sanctuary for spiritual discourse, hospitable banquets, and continuous charitable feeding."
    ],
    "strong_placement_ta": [
      "கடகத்தில் உச்சம் அல்லது தனுசு/மீனத்தில் ஆட்சி பெற்று ஹம்ச யோகம் அமைந்தால்: அரண்மனை போன்ற வாழ்க்கை, பல்கலைக்கழகத் தலைமை.",
      "அரசாங்கத்தால் சகல மரியாதைகளும் வழங்கப்பட்டு, சமுதாயத்தில் மிக உயர்ந்த ஆன்மீகத் தலைவராகப் போற்றப்படுவார்."
    ],
    "strong_placement_en": [
      "Exalted in Cancer or own sign forming Hamsa Yoga: Princely residential compounds, university chancellor status.",
      "Garlanded with sovereign state honors, commanding reverence as a beacon of cultural wisdom."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தாயாரின் கல்லீரல் அல்லது உடல்நலம் பாதித்தல், பூர்வீக வீட்டை விட்டுப் பிரிதல்.",
      "வாகனங்களால் செலவுகள் மற்றும் சொத்து ஆவணங்களில் வில்லங்கங்கள் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated in Capricorn or afflicted: Maternal hepatic or cardiac ailments, estrangement from ancestral manor.",
      "Heavy financial drains on vehicular repairs and encumbrances on real estate titles."
    ],
    "career_wealth_ta": [
      "பல்கலைக்கழகங்கள், பெரிய கல்லூரிகள், விவசாயப் பண்ணைகள், ரியல் எஸ்டேட் வளர்ச்சி, ஆன்மீக மடங்கள், அரசு வாகனத் துறை.",
      "சொத்துகளின் மதிப்பு அபரிமிதமாக உயர்வதாலும் கல்விச் சேவைகளாலும் கோடிக்கணக்கில் தன வரவு."
    ],
    "career_wealth_en": [
      "Distinguished in university ownership, sprawling agro-farms, residential township development, and sacred ashrams.",
      "Colossal capital growth realized via real estate appreciation and educational foundations."
    ],
    "health_precautions_ta": [
      "இதயப் பகுதியில் கொழுப்பு படிதல், ரத்த அழுத்தம், கல்லீரல் வீக்கம் மற்றும் ஆஸ்துமா.",
      "கொழுப்புச் சத்துள்ள உணவுகளைக் குறைத்து, காய்கறிகளையும் பழங்களையும் அதிகமாக உண்பது நலம் பயக்கும்."
    ],
    "health_precautions_en": [
      "Prone to coronary lipid plaque, hypertension, hepatic enlargement, and bronchial congestion.",
      "Adopt a strictly low-fat plant-based diet, schedule cardiovascular diagnostics, and avoid sedentary inertia."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 175) & Saravali Ch. 30"
  },
  {
    "planet": "Jupiter",
    "planet_name_ta": "குரு",
    "symbol": "🟡",
    "element": "ஆகாயம் (Akasha)",
    "house": 5,
    "bhava_category": "trikona",
    "house_title_ta": "5-ஆம் பாவம் - பூர்வ புண்ணியம் (புத்திர பாக்கியம் / பிரம்ம ஞானம் & அதிர்ஷ்டம்)",
    "house_title_en": "5th House - Putra Bhava (Divine Progeny, Higher Wisdom & Serendipity)",
    "core_traits_ta": [
      "குரு 5-ஆம் பாவத்தில் (காரகோ பாவக நாஸ்தி விதிக்கு உட்படாமல் சுப பலத்துடன் இருந்தால்) மாபெரும் பூர்வ புண்ணிய யோகத்தைத் தரும்.",
      "அசாத்தியமான ஆன்மீக ஞானம், மந்திர சித்தி, தெய்வ கடாட்சம் மற்றும் கூர்மையான தொலைநோக்குப் பார்வை.",
      "சமுதாயத்தில் மிக உயர்ந்த அந்தஸ்தை அடையும் உன்னதமான, நல்லொழுக்கம் நிறைந்த புத்திரர்கள் அமைவார்கள்.",
      "எடுத்த காரியங்கள் அனைத்திலும் இறைவனின் கருணையால் எதிர்பாராத அதிர்ஷ்டங்களும் வெற்றிகளும் குவியும்."
    ],
    "core_traits_en": [
      "Jupiter in the 5th (unafflicted) unlocks past-life spiritual merit (Poorvapunya), higher gnosis, and divine benediction.",
      "Exceptional intuitive foresight, mastery of mantra sciences, and sublime theological insight.",
      "Blessed with virtuous, brilliant, and highly accomplished progeny who elevate the family dynasty.",
      "Serendipitous breakthroughs manifest effortlessly throughout life as if guided by an unseen guardian angel."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: நாட்டின் மிக உயர்ந்த அரசியல் ஆலோசகர், வேத வித்வான், பல்லாயிரம் கோடீஸ்வர யோகம்.",
      "பிள்ளைகள் உலகப் புகழ் பெறுவார்கள்; முன்னோர்களின் புண்ணியத்தால் வாழ்நாள் முழுவதும் யோக வாழ்வு."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Premier state counselor, Vedic preceptor, multi-millionaire through past-life grace.",
      "Progeny achieve world renown in science, statecraft, or arts; unending streams of good fortune."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: புத்திர பாக்கியத்தில் காலதாமதம் அல்லது பிள்ளைகளின் ஆரோக்கியத்தில் கவலை.",
      "பங்குச் சந்தையில் குருட்டுத்தனமாக முதலீடு செய்து நஷ்டமடைதல்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Delays or emotional anxieties regarding children; frail constitution in firstborn.",
      "Heavy financial setbacks from ill-considered speculative ventures and ideological rigidity."
    ],
    "career_wealth_ta": [
      "முதலீட்டு நிதி மேலாண்மை (Hedge Fund), அரசாங்க உயர் ஆலோசனைக் குழு, வேதாந்தப் பேராசிரியர், ஜோதிட ஆராய்ச்சி, நீதித்துறை.",
      "அறிவுசார் திட்டமிடலாலும் திடீர் அதிர்ஷ்ட வாய்ப்புகளாலும் அள்ள அள்ளக் குறையாத தன லாபம்."
    ],
    "career_wealth_en": [
      "Stellar career in hedge fund strategy, governmental think-tanks, philosophy deanships, and judicial advisory.",
      "Monumental wealth generated through prescient investments and intellectual endowments."
    ],
    "health_precautions_ta": [
      "வயிற்றுப் பகுதியில் கொழுப்பு, கணையக் கோளாறுகள் (Pancreas), நீரிழிவு மற்றும் கல்லீரல் உஷ்ணம்.",
      "இனிப்புப் பண்டங்களைத் தவிர்த்து சத்தான நார்ச்சத்துள்ள உணவுகளை உண்பது அவசியம்."
    ],
    "health_precautions_en": [
      "Susceptible to abdominal adiposity, pancreatic enzymes imbalance, type-2 diabetes, and liver congestion.",
      "Strict glycemic regulation, elimination of processed confectionery, and routine insulin checks."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 221) & Saravali Ch. 30"
  },
  {
    "planet": "Jupiter",
    "planet_name_ta": "குரு",
    "symbol": "🟡",
    "element": "ஆகாயம் (Akasha)",
    "house": 6,
    "bhava_category": "dusthana",
    "house_title_ta": "6-ஆம் பாவம் - சத்ரு பாவம் (பகைவர்களை நல்வழிப்படுத்துதல் & கடன் தீர்த்தல்)",
    "house_title_en": "6th House - Satru Bhava (Reconciling Enemies & Discharging Debts)",
    "core_traits_ta": [
      "எதிரிகளையும் தன் கருணையாலும், விவேகத்தாலும், சாந்த குணத்தாலும் நண்பர்களாக மாற்றும் மாண்புடையவர்.",
      "நேரடி மோதல்களைத் தவிர்த்து அமைதியான சமரசப் பேச்சுவார்த்தைகள் மூலம் வழக்குகளை முடித்து வைப்பார்.",
      "பிறருக்கு உதவும் தாராள உள்ளமும், தொண்டு நிறுவனங்கள் மற்றும் மருத்துவமனைகளுக்கு உதவும் அறப்பண்பும் உண்டு.",
      "தாய்மாமனுடன் சுமுகமான உறவும், அவரது வழிகாட்டலால் நன்மைகளும் கிட்டும்."
    ],
    "core_traits_en": [
      "Converts bitter adversaries into allies through magnanimity, supreme patience, and moral suasion.",
      "Avoids toxic confrontations, settling litigations and commercial disputes via high-minded mediation.",
      "Deep humanitarian compassion; donates liberally to hospices, free clinics, and orphanages.",
      "Maintains affectionate bonds with maternal uncles, deriving spiritual and ethical advice from them."
    ],
    "strong_placement_ta": [
      "சுப பலத்துடன் இருப்பின்: கடன்கள் இல்லாத பூரண வாழ்க்கை, வழக்குகளில் சுமுக வெற்றி, அசைக்க முடியாத உடல் ஆரோக்கியம்.",
      "மருத்துவத் துறையிலும், சமூக நல்லிணக்க அமைப்புகளிலும் உயர்ந்த தலைமைப் பதவிகளை வகிப்பார்."
    ],
    "strong_placement_en": [
      "Strong with benefic aspects: Completely debt-free existence, triumphant out-of-court settlements, and robust health.",
      "Appointed to presidential boards of health, medical ethics commissions, and humanitarian councils."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: கல்லீரல் நோய்கள், நீரிழிவு, கடன் தொல்லைகளால் மன உளைச்சல்.",
      "வேலையாட்களால் பண இழப்புகளும், காரணமற்ற அவப்பெயரும் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Severe hepatic cirrhosis, uncontrolled diabetes, and anxiety over unpaid liabilities.",
      "Financial leakages through unscrupulous subordinates and unmerited public criticism."
    ],
    "career_wealth_ta": [
      "மருத்துவமனை இயக்குநர், சர்வதேச சமரச தீர்ப்பாயம் (Arbitration), பொது சுகாதாரம், வங்கி கடன் மேலாண்மை, தொண்டு நிறுவனங்கள்.",
      "நேர்மையான உழைப்பாலும் சேவைகளாலும் நிலையான தன வரவு."
    ],
    "career_wealth_en": [
      "Flourishes as hospital director, international ombudsman, public health executive, and charitable trustee.",
      "Steady, secure income built upon principled public service and administrative competence."
    ],
    "health_precautions_ta": [
      "கல்லீரல் வீக்கம், செரிமானக் கோளாறுகள், பித்தப்பை கற்கள், நீரிழிவு மற்றும் குடல் புண்கள்.",
      "கொழுப்பு மற்றும் எண்ணெய் உணவுகளைக் குறைத்து, எளிய சமைத்த உணவுகளை உட்கொள்ளுதல் நலம்."
    ],
    "health_precautions_en": [
      "Vulnerable to hepatomegaly, biliary colic, gallstones, insulin resistance, and intestinal ulcers.",
      "Low-fat nutrition, zero alcohol consumption, and periodic liver function blood panels."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 261) & Saravali Ch. 30"
  },
  {
    "planet": "Jupiter",
    "planet_name_ta": "குரு",
    "symbol": "🟡",
    "element": "ஆகாயம் (Akasha)",
    "house": 7,
    "bhava_category": "kendra",
    "house_title_ta": "7-ஆம் பாவம் - களத்திர பாவம் (ஹம்ச யோகம் / உன்னத துணை & கூட்டு வெற்றி)",
    "house_title_en": "7th House - Kalathra Bhava (Hamsa Yoga / Noble Spouse & Blessed Alliances)",
    "core_traits_ta": [
      "குரு 7-ஆம் பாவத்தில் அமைவது பூரண தாம்பத்திய சுகம், தெய்வ பக்திமிக்க வாழ்க்கைத் துணை மற்றும் லக்னத்திற்கு 100% சுப பார்வையைத் தரும்.",
      "அழகான, உயர்ந்த பண்புகள் நிறைந்த, செல்வந்த குடும்பத்தில் பிறந்த உன்னதமான வாழ்க்கைத் துணை அமைவார்.",
      "திருமணத்திற்குப் பின் ஜாதகருக்கு ராஜயோகம் செயல்படத் தொடங்கும்; சமூக அந்தஸ்து பலமடங்கு உயரும்.",
      "வணிக கூட்டாண்மைகளில் நேர்மையும் பரஸ்பர நம்பிக்கையும் நிலவி பல கோடி ரூபாயில் வர்த்தகம் பெருகும்."
    ],
    "core_traits_en": [
      "Jupiter in the 7th is a sublime blessing for conjugal harmony, bestowing a pious, noble partner and casting a golden aspect on Lagna.",
      "Blessed with an exquisitely virtuous, educated, prosperous, and devoted spouse.",
      "Marriage acts as the supreme catalyst for Raja Yoga, catapulting the native into high societal prominence.",
      "Commercial partnerships thrive upon ironclad mutual trust, ethical contracts, and massive turnover."
    ],
    "strong_placement_ta": [
      "கடகத்தில் உச்சம் அல்லது தனுசு/மீனத்தில் ஆட்சி பெற்று ஹம்ச யோகம் அமைந்தால்: நாட்டின் மிக உயர்ந்த குடும்பத்துடன் திருமண பந்தம், அரசு கௌரவங்கள்.",
      "சர்வதேச வர்த்தகத்தில் வெற்றி, இல்லறத்தில் சகல சௌபாக்கியங்களும் நிறைந்து தேவதம்பதிகளாக வாழ்வர்."
    ],
    "strong_placement_en": [
      "Exalted or own house forming Hamsa Yoga: Marries into royal or national leadership dynasties; shower of civic honors.",
      "Triumphs in international commerce, embodying the archetype of an ideal, prosperous divine couple."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: திருமணத்தில் காலதாமதம், துணையின் ஆரோக்கியத்தில் குறைபாடுகள்.",
      "கூட்டுத் தொழிலில் பங்குதாரர்களை அளவுக்கு அதிகமாக நம்பி ஏமாறுதல்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Protracted delays in solemnizing marriage; partner prone to metabolic health frailties.",
      "Loss of capital through naive over-trust in opportunistic business associates."
    ],
    "career_wealth_ta": [
      "சர்வதேச வர்த்தகம், தூதரக சேவைகள், சட்ட ஒப்பந்தங்கள், பெரிய வணிகக் கூட்டாண்மை, ஆலோசனை நிறுவனங்கள்.",
      "வாழ்க்கைத் துணையின் அதிர்ஷ்டத்தாலும் நேர்மையான கூட்டாண்மையாலும் கோடிக்கணக்கில் சொத்துக்கள் சேரும்."
    ],
    "career_wealth_en": [
      "Dominant in international jurisprudence, consular missions, luxury trade syndicates, and corporate arbitration.",
      "Magnificent fortune accumulated through spousal providence and lucrative consortiums."
    ],
    "health_precautions_ta": [
      "சிறுநீரகக் கோளாறுகள், நீரிழிவு, அடிவயிற்று உஷ்ணம் மற்றும் கொழுப்பு படிதல்.",
      "முறையான குடிநீர் அருந்துதலும், சர்க்கரை அளவைக் கட்டுப்பாட்டில் வைத்திருப்பதும் அவசியம்."
    ],
    "health_precautions_en": [
      "Prone to renal fat accumulation, glycosuria, diabetic complications, and pelvic sluggishness.",
      "Consistent daily hydration, low-glycemic meal planning, and annual urological screenings."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Jupiter",
    "planet_name_ta": "குரு",
    "symbol": "🟡",
    "element": "ஆகாயம் (Akasha)",
    "house": 8,
    "bhava_category": "dusthana",
    "house_title_ta": "8-ஆம் பாவம் - ஆயுள் பாவம் (பூரண தீர்க்காயுள், மறைபொருள் ஞானம் & உயில் சொத்து)",
    "house_title_en": "8th House - Ayur Bhava (Immaculate Longevity, Esoteric Wisdom & Inheritances)",
    "core_traits_ta": [
      "குரு 8-ஆம் பாவத்தில் அமர்வது ஜாதகருக்கு நோயற்ற பூரண தீர்க்காயுளை (80+ வயது) வழங்கும் உன்னத அமைப்பாகும்.",
      "மறைமுக சாஸ்திரங்கள், வேதாந்தம், மரணத்திற்குப் பின் உள்ள நிலை மற்றும் பிரபஞ்ச ரகசியங்களை உணரும் ஞானம்.",
      "வாழ்க்கையில் நெருக்கடிகள் வரும்போதெல்லாம் கண்ணுக்குத் தெரியாத இறைவனின் அருள் இவரைக் காக்கும்.",
      "மனைவி வழியில் எதிர்பாராத பெரும் உயில் சொத்துகள், காப்பீடுகள் மற்றும் பரம்பரைச் செல்வங்கள் வந்து சேரும்."
    ],
    "core_traits_en": [
      "Jupiter in the 8th is classically celebrated as an invincible guarantor of long, dignified longevity (80+ years).",
      "Profound metaphysical comprehension of afterlife realms, Vedic esotericism, and cosmic quantum laws.",
      "Divine grace serves as an invisible shield, miraculously pulling the native out of life-threatening crises.",
      "Reaps unexpected testamentary windfalls, insurance estates, and unearned ancestral inheritances through marriage."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: சதாபிஷேகம் (80 வயது நிறைவு) காணும் யோகம், பல்லாயிரம் கோடி உயில் சொத்துகள், ஆன்மீக முக்தி.",
      "சமுதாயத்தில் உன்னத ஆன்மீக வழிகாட்டியாகத் திகழ்ந்து அமைதியான சமாதி நிலை எய்துவார்."
    ],
    "strong_placement_en": [
      "Exalted or in own sign: Attains auspicious Centenarian age, colossal legacy inheritances, and serene Moksha.",
      "Revered as an enlightened saintly counselor, transitioning peacefully in exalted conscious meditation."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: கல்லீரல் கோளாறுகள், மஞ்சள் காமாலை, உயில் சொத்துகளில் தகராறுகள்.",
      "அரசாங்க வரி ஏய்ப்பு அல்லது அபராதங்களால் மன உளைச்சல் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Chronic hepatitis, severe jaundice, and litigious partition battles over inheritances.",
      "Anxieties over estate taxes and legal probate encumbrances."
    ],
    "career_wealth_ta": [
      "ஆயுள் காப்பீட்டுத் தலைவர், தொல்பொருள் ஆராய்ச்சி, வேதாந்த ஆராய்ச்சி, டிரஸ்டி, உயில் நிர்வாகி, ரகசிய நிதி ஆலோசகர்.",
      "உயில் சொத்துகள், பரம்பரை அறக்கட்டளைகள் மற்றும் காப்பீட்டு முதிர்வுகள் மூலம் பெருஞ்செல்வம்."
    ],
    "career_wealth_en": [
      "Distinguished as life insurance commissioner, archaeological research fellow, trust executor, and private wealth manager.",
      "Vast windfalls realized through family legacies, estate settlements, and offshore annuities."
    ],
    "health_precautions_ta": [
      "மஞ்சள் காமாலை, கல்லீரல் கொழுப்பு, நீரிழிவு மற்றும் குடல் நோய்கள்.",
      "மது, கொழுப்பு உணவுகளை முற்றிலும் தவிர்த்து கல்லீரலைப் பாதுகாப்பது மிக அவசியம்."
    ],
    "health_precautions_en": [
      "Susceptible to jaundice, non-alcoholic fatty liver, diabetic neuropathy, and sluggish bowels.",
      "Strictly avoid alcohol, eliminate saturated fats, and undergo bi-annual hepatic ultrasound scans."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Jupiter",
    "planet_name_ta": "குரு",
    "symbol": "🟡",
    "element": "ஆகாயம் (Akasha)",
    "house": 9,
    "bhava_category": "trikona",
    "house_title_ta": "9-ஆம் பாவம் - பாக்கிய பாவம் (காரகோ பாவக நாஸ்திக்கு அப்பாற்பட்ட பரம பாக்கியம் & தர்மம்)",
    "house_title_en": "9th House - Bhagya Bhava (Supreme Fortune, Pious Father & Divine Grace)",
    "core_traits_ta": [
      "குரு 9-ஆம் பாவத்தில் அமர்வது மனிதப் பிறவியின் ஆகச்சிறந்த பாக்கிய அமைப்பாகும்; தர்மத்தின் உருவமாகத் திகழ்வார்.",
      "தந்தையின் மீது எல்லை இல்லாத பக்தி; தந்தை உயர்ந்த ஆன்மீகவாதியாகவும் செல்வந்தராகவும் விளங்குவார்.",
      "புனிதத் தலங்களுக்கு யாத்திரை செல்லுதல், திருவிழாக்களை முன்னின்று நடத்துதல், வேத பாடசாலைகளை உருவாக்குதல்.",
      "எடுத்த காரியங்கள் யாவும் வெற்றி பெறும்; வாழ்க்கையில் வறுமை என்பது இவரை எட்டிக்கூடப் பார்க்காது."
    ],
    "core_traits_en": [
      "Jupiter in the 9th is hailed as one of the most sublime placements in Vedic astrology; embodies living Dharma.",
      "Boundless devotion to the father, who is typically an esteemed, spiritual, and affluent patriarch.",
      "Passionate sponsor of pilgrimages, temple consecrations, Vedic academies, and Vedic chanting schools.",
      "Every enterprise is crowned with divine fruition; poverty and misery are utterly alien to his destiny."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: அகண்ட ராஜயோகம்! நாட்டின் மாபெரும் மத பீடாதிபதி அல்லது ஜனாதிபதி அந்தஸ்து.",
      "கோடிக்கணக்கான மக்களின் நல்வழிகாட்டி, உலகெங்கும் ஆசிரமங்கள், அரச குடும்பங்களின் ராஜகுருவாகத் திகழ்தல்."
    ],
    "strong_placement_en": [
      "Exalted or in own sign: Supreme Raja Yoga! Revered as Jagadguru, National President, or Royal Preceptor.",
      "Inspires millions of souls globally; founds international philanthropic ashrams with royal patronage."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தந்தையின் உடல்நலக்குறைவு, ஆன்மீக குருக்களுடன் முரண்பாடுகள்.",
      "வெளிநாட்டுப் பயணங்களில் தடைகள் மற்றும் தர்ம காரியங்களில் அவப்பெயர்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Paternal health setbacks, philosophical disillusionment with institutional priesthood.",
      "Delays in foreign travel and unmerited scandals regarding charitable funds."
    ],
    "career_wealth_ta": [
      "மத அறக்கட்டளைத் தலைவர், பல்கலைக்கழக வேந்தர், உச்ச நீதிமன்றத் தலைமை நீதிபதி, சர்வதேச தூதர், நூலாசிரியர்.",
      "தர்ம வழியில் சேர்க்கும் வற்றாத செல்வமும், பரம்பரைச் சொத்துகளும் தலைமுறைக்கும் நிலைத்து நிற்கும்."
    ],
    "career_wealth_en": [
      "Commands top status as religious trust president, supreme court justice, ambassador, and theological author.",
      "Multi-generational noble wealth preserved intact through institutional trusts and endowments."
    ],
    "health_precautions_ta": [
      "தொடைப் பகுதியில் கொழுப்பு படிதல், இடுப்பு வாதம், கல்லீரல் உஷ்ணம் மற்றும் சர்க்கரை நோய்.",
      "நடைப்பயிற்சியும், எளிய சாத்வீக உணவு முறையும் உடல் ஆரோக்கியத்தை நீண்ட காலத்திற்குப் பாதுகாக்கும்."
    ],
    "health_precautions_en": [
      "Prone to femoral adiposity, sciatica flares, hepatic sluggishness, and late-onset hyperglycemia.",
      "Brisk morning walking and a clean sattvic lifestyle safeguard vitality into advanced age."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Jupiter",
    "planet_name_ta": "குரு",
    "symbol": "🟡",
    "element": "ஆகாயம் (Akasha)",
    "house": 10,
    "bhava_category": "kendra",
    "house_title_ta": "10-ஆம் பாவம் - ஜீவன பாவம் (ஹம்ச யோகம் / உயர் அதிகாரம், அரசு கௌரவம் & தர்ம தொழில்)",
    "house_title_en": "10th House - Karma Bhava (Hamsa Yoga / High Executive Power & Dharmic Career)",
    "core_traits_ta": [
      "குரு 10-ஆம் பாவத்தில் அமைவது உன்னதமான தர்ம நெறி தவறாத தொழில் மேன்மையையும், ஆட்சி அதிகாரத்தையும் தரும்.",
      "நேர்மையான நிர்வாகி; எந்தச் சூழ்நிலையிலும் லஞ்சம், ஊழல் மற்றும் அதர்ம வழிகளுக்கு ஒருபோதும் தலைவணங்க மாட்டார்.",
      "சமுதாயத்தில் மக்கள் போற்றும் உயர்ந்த கௌரவப் பதவிகள், பல்லாயிரக்கணக்கான பணியாளர்களை வழிநடத்தும் தலைமைப் பண்பு.",
      "தொழிலில் அசைக்க முடியாத நற்பெயர்; சரித்திரத்தில் போற்றப்படும் நல்லாசிரியராகவும் வழிகாட்டியாகவும் திகழ்வார்."
    ],
    "core_traits_en": [
      "Jupiter in the 10th confers stellar professional elevation anchored in unbending ethical righteousness.",
      "Impeccable administrator; steadfastly refuses corruption, deceit, or underhanded shortcuts.",
      "Commands high public acclaim, sovereign ministerial portfolios, and paternal leadership over thousands.",
      "Builds an unblemished professional reputation, immortalized as a visionary statesman and moral mentor."
    ],
    "strong_placement_ta": [
      "கடகத்தில் உச்சம் அல்லது தனுசு/மீனத்தில் ஆட்சி பெற்று ஹம்ச யோகம் அமைந்தால்: தலைமை நீதிபதி, கவர்னர், கேபினட் மந்திரி அந்தஸ்து.",
      "நாட்டின் முதன்மை பல்கலைக்கழகங்களின் வேந்தராகவோ அல்லது பெரிய அறக்கட்டளைகளின் தலைவராகவோ முடிசூடுவார்."
    ],
    "strong_placement_en": [
      "Exalted or own house forming Hamsa Yoga: State Governor, Supreme Court Chief Justice, Cabinet Minister.",
      "Presides as Chancellor of premier universities or Governor of the Central Reserve Bank."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: உத்தியோகத்தில் உயர் அதிகாரிகளுடன் கருத்து மோதல்கள், திடீர் இடமாற்றம்.",
      "தொழிலில் நேர்மையாக இருந்தும் அவப்பெயர் உண்டாக வாய்ப்புண்டு."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Friction with autocratic superiors, sudden political transfers, and bureaucratic disillusionment.",
      "Unmerited public scrutiny despite transparently honest intentions."
    ],
    "career_wealth_ta": [
      "நீதித்துறை, உயர் கல்வித்துறை, நிதி அமைச்சகம், சர்வதேச வங்கிகள், அறக்கட்டளை நிர்வாகம், அரசு ஆலோசகர்.",
      "அரசாங்க கௌரவ ஊதியங்களாலும், தொழில் மேன்மையாலும் கோடிக்கணக்கில் சொத்துகள் சேரும்."
    ],
    "career_wealth_en": [
      "Flourishes in the judiciary, higher education, treasury leadership, sovereign wealth funds, and policy think-tanks.",
      "Commanding multi-million dollar asset accumulation through state pensions, consultancy, and board directorships."
    ],
    "health_precautions_ta": [
      "பணிச்சுமையால் உடல் பருமன், மூட்டு தேய்மானம், ரத்த அழுத்தம் மற்றும் நீரிழிவு.",
      "வேலைக்கு நடுவே தியானமும், உடற்பயிற்சியும் செய்வது நீண்ட ஆயுளைத் தரும்."
    ],
    "health_precautions_en": [
      "Occupational stress, metabolic syndrome, knee osteoarthritis, and fluctuating blood pressure.",
      "Structured meditation, daily exercise, and portion control maintain executive health."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Jupiter",
    "planet_name_ta": "குரு",
    "symbol": "🟡",
    "element": "ஆகாயம் (Akasha)",
    "house": 11,
    "bhava_category": "upachaya",
    "house_title_ta": "11-ஆம் பாவம் - லாப பாவம் (அகண்ட தன லாபம் / குபேர யோகம் & உயர் நட்பு)",
    "house_title_en": "11th House - Labha Bhava (Abundant Gains, Kubera Yoga & Saintly Network)",
    "core_traits_ta": [
      "குரு 11-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமர்வது ஜாதகருக்கு கோடீஸ்வர யோகத்தையும், எண்ணிய ஆசைகள் அனைத்தையும் நிறைவேற்றும் வரப்பிரசாதமாகும்.",
      "தொட்டதெல்லாம் பொன்னாகும் தன யோகம்; பல துறைகளிலிருந்து வற்றாத நிதி வரவு வந்துகொண்டே இருக்கும்.",
      "அரசியல் தலைவர்கள், நீதிபதிகள், ஆன்மீக மகான்கள் மற்றும் பெரும் செல்வந்தர்களின் உயர்ந்த நட்பு வட்டம்.",
      "மூத்த சகோதரர்களிடம் அளப்பரிய அன்பும் பாசமும் நிலவும்; அவர்களால் பெரும் நன்மைகள் கிட்டும்."
    ],
    "core_traits_en": [
      "Jupiter in the 11th (an Upachaya house) is one of the most magnificent placements for compounding wealth and wish-fulfillment.",
      "Midas touch in financial undertakings; unceasing multi-channel cash streams flood his banking reserves.",
      "Surrounded by an elite network of statesmen, appellate judges, spiritual luminaries, and philanthropists.",
      "Cherished, profoundly harmonious bond with elder siblings, who facilitate monumental career breakthroughs."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: பல நூறு கோடி மதிப்பிலான சொத்துகள், சொகுசு வாகனங்கள், சமூகத்தின் முதன்மை அந்தஸ்து.",
      "அறக்கட்டளைகளை நிறுவி பல்லாயிரக்கணக்கான ஏழை எளியவர்களுக்கு அன்னதானமும் கல்விக் கொடையும் வழங்கும் வள்ளல் யோகம்."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Bestows multi-billion dollar asset portfolios, private air fleet, and premier social stature.",
      "Acts as a legendary philanthropist, establishing university scholarships, hospitals, and heritage restorations."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: நண்பர்களால் ஏமாற்றப்பட்டு நிதி இழப்பு, மூத்த சகோதரருடன் பிரிவு.",
      "லாபங்கள் கைநழுவிப் போதல் அல்லது எதிர்பாராத விரயங்கள் ஏற்படுதல்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Exploitation by unscrupulous cronies, capital erosion, and sibling estrangement.",
      "Anticipated revenues delayed by bureaucratic entanglements."
    ],
    "career_wealth_ta": [
      "பெருநிறுவன முதலீடுகள், வென்ச்சர் கேபிடல், வங்கி மேலாண்மை, கல்வி நிறுவனங்கள், ஏற்றுமதி-இறக்குமதி, தொண்டு அறக்கட்டளைகள்.",
      "முதலீடுகளின் அபரிமிதமான வளர்ச்சியால் சமுதாயத்தின் பெரும் பணக்காரராக உயருதல்."
    ],
    "career_wealth_en": [
      "Unrivaled success in mega-venture capital, corporate investment banking, educational syndicates, and global philanthropy.",
      "Extraordinary capital multiplication placing the native in the billionaire tier."
    ],
    "health_precautions_ta": [
      "இடது காது கேளாமை, கணுக்கால் வீக்கம், ரத்த ஓட்டக் குறைபாடுகள் மற்றும் சர்க்கரை நோய்.",
      "கால் நரம்புகளுக்கான உடற்பயிற்சியும், காது ஆரோக்கியத்தைப் பேணுதலும் நல்லது."
    ],
    "health_precautions_en": [
      "Susceptible to left-ear dullness, peripheral ankle edema, circulatory sluggishness, and diabetes.",
      "Regular ankle mobility stretching, compression socks for long flights, and otic checkups."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Jupiter",
    "planet_name_ta": "குரு",
    "symbol": "🟡",
    "element": "ஆகாயம் (Akasha)",
    "house": 12,
    "bhava_category": "dusthana",
    "house_title_ta": "12-ஆம் பாவம் - விரய பாவம் (மோட்ச காரகன் / ஆன்மீக முக்தி & தர்ம விரயம்)",
    "house_title_en": "12th House - Vraya & Moksha Bhava (Spiritual Liberation, Sacred Solitude & Foreign Renown)",
    "core_traits_ta": [
      "குரு 12-ஆம் பாவத்தில் அமர்வது பிறவிப் பெருங்கடலை நீந்தி முக்தி அடையும் உன்னதமான ஆன்மீக யோகமாகும்.",
      "பணத்தை ஆடம்பரங்களுக்கு வீணாக்காமல், கோவில் திருப்பணிகள், தர்ம ஸ்தாபனங்கள் மற்றும் ஆன்மீக காரியங்களுக்குச் செலவிடுவார்.",
      "பிறந்த மண்ணை விட வெளிநாடுகளிலோ அல்லது தொலைதூரத் தீவுகளிலோ அளப்பரிய நற்பெயரும் யோகமும் பெறுவார்.",
      "தனிமையை விரும்பும் அமைதியான முனிவர் போன்ற சுபாவம்; ஆழ்ந்த தூக்கமும் மன அமைதியும் நிறைந்திருக்கும்."
    ],
    "core_traits_en": [
      "Jupiter in the 12th is the classic harbinger of spiritual Moksha (emancipation from the cycle of rebirth).",
      "Directs worldly wealth away from frivolous vanity towards magnificent temple restorations and humanitarian endowments.",
      "Achieves peak spiritual honors, peaceful existence, and immense respect when residing in foreign lands.",
      "Contemplative, monastic inner disposition; blessed with serene restorative sleep and profound detachment."
    ],
    "strong_placement_ta": [
      "கடகத்தில் உச்சம் அல்லது சொந்த வீட்டில் சுப பலத்துடன் இருப்பின்: வெளிநாட்டில் மாபெரும் ஆன்மீக ஆசிரமங்கள், சர்வதேச அங்கீகாரம்.",
      "அயன சயன சுகம் பூரணமாகக் கிட்டும்; ஜீவன் முக்தி அடைந்து ஆன்மீக வரலாற்றில் இடம்பெறுவார்."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Founds renowned international spiritual retreats abroad; revered as an enlightened sage.",
      "Attains effortless Samadhi, blissful restorative sleep, and transcendental liberation (Jivanmukti)."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: மதத்தின் பெயரால் ஏமாற்றப்படுதல், வீண் விரயங்கள், தூக்கமின்மை.",
      "இடது கண் பார்வை மங்குதல் மற்றும் குடும்பச் சொத்துகளில் இழப்பு ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Exploitation by bogus spiritual cults, fruitless financial drainage, and insomnia.",
      "Left eye vision defects and wasteful dissipation of family patrimony."
    ],
    "career_wealth_ta": [
      "சர்வதேச ஆன்மீக ஆசிரமங்கள், வெளிநாட்டுத் தூதரகங்கள், உலகளாவிய தொண்டு நிறுவனங்கள், மருத்துவமனை அறக்கட்டளைகள், தத்துவ ஆராய்ச்சி.",
      "வெளிநாட்டு நாணயங்களாலும் ஆன்மீக கொடைகளாலும் நிறைவான செல்வம்."
    ],
    "career_wealth_en": [
      "Stellar leadership in international ashrams, consular diplomacy, global humanitarian agencies, and theological institutes.",
      "Wealth sustained through generous foreign donations, international royalties, and endowment funds."
    ],
    "health_precautions_ta": [
      "இடது கண் பாதிப்பு, பாதங்களில் நீர் வீக்கம், தூக்கமின்மை மற்றும் கல்லீரல் பலவீனம்.",
      "இரவில் அமைதியான தியானமும், பாதங்களை மசாஜ் செய்வதும் ஆழ்ந்த தூக்கத்தைத் தரும்."
    ],
    "health_precautions_en": [
      "Prone to left-eye ocular strain, lymphatic foot edema, insomnia, and sluggish hepatic drainage.",
      "Nightly grounding meditation, warm foot massages, and calming chamomile infusions promote tranquility."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Venus",
    "planet_name_ta": "சுக்கிரன்",
    "symbol": "✨",
    "element": "நீர் (Jala)",
    "house": 1,
    "bhava_category": "kendra",
    "house_title_ta": "1-ஆம் பாவம் - லக்னம் (மாளவ்ய யோகம் / பேரழகு, காந்தக் கவர்ச்சி & கலை மேதை)",
    "house_title_en": "1st House - Ascendant / Tanu Bhava (Malavya Yoga / Peerless Beauty & Artistic Genius)",
    "core_traits_ta": [
      "அழகிய காந்தக் கண்கள், பிரகாசமான வசீகர முகம், நளினமான உடல்வாகு மற்றும் அனைவரையும் கவரும் பேரழகு உடையவர்.",
      "கலை, இசை, சினிமா, இலக்கியம், ஆடை வடிவமைப்பு மற்றும் நவரத்தினங்களில் ஆழ்ந்த ரசனை கொண்டவர்.",
      "இனிமையான சுபாவம், கனிவான பேச்சு, தாராள மனப்பான்மை மற்றும் அனைவரையும் நேசிக்கும் அன்பு உள்ளம்.",
      "சொகுசு வாழ்க்கை, வாசனைத் திரவியங்கள், ஆடம்பர வாகனங்கள் மற்றும் சுகபோகங்களை முழுமையாக அனுபவிப்பார்.",
      "சுயமரியாதையை அழகாகவும் நயமாகவும் நிலைநாட்டுவார்; எவரிடமும் முரட்டுத்தனமாக நடக்க மாட்டார்."
    ],
    "core_traits_en": [
      "Dazzling magnetic physical allure, luminous eyes, proportionate facial symmetry, and graceful posture.",
      "Refined connoisseur of fine arts, classical music, cinema, literature, haute couture, and precious gems.",
      "Sweet, charming temperament; radiates effortless courtesy, generosity, and charismatic warmth.",
      "Innate destiny for luxurious living, aromatic scents, premium sports cars, and sensory delights.",
      "Preserves self-respect through exquisite diplomacy; utterly disdains vulgarity and coarse aggression."
    ],
    "strong_placement_ta": [
      "மீனத்தில் உச்சம் அல்லது ரிஷபம்/துலாத்தில் ஆட்சி பெற்று மாளவ்ய யோகம் (Malavya Yoga) அமைந்தால்: உலகப் புகழ் பெற்ற சினிமா நட்சத்திரம், அரச போகம்.",
      "அரண்மனை போன்ற பங்களாக்கள், எண்ணற்ற சொகுசு கார்கள், உலகின் தலைசிறந்த கலைஞராகப் போற்றப்படுதல்."
    ],
    "strong_placement_en": [
      "Exalted in Pisces or in own signs Taurus/Libra forming Malavya Mahapurusha Yoga: Iconic superstar of screen and stage, princely luxuries.",
      "Commands palatial residential villas, fleets of exotic vehicles, and international adulation as an artistic legend."
    ],
    "weak_placement_ta": [
      "கன்னியில் நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தாம்பத்திய சுகக் குறைவு, பாலியல் நோய்கள், அழகில் வாட்டம்.",
      "ஆடம்பரச் செலவுகளால் நிதி நெருக்கடி, தவறான நட்புகளால் அவப்பெயர் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated in Virgo or afflicted: Marital dissatisfaction, reproductive/urological ailments, and premature loss of physical charm.",
      "Financial ruin through profligate hedonism and scandalous entanglements with unreliable companions."
    ],
    "career_wealth_ta": [
      "சினிமா, தொலைக்காட்சி, இசை, ஆடை வடிவமைப்பு (Fashion Design), அழகு சாதனங்கள், நவரத்தின வர்த்தகம், சொகுசு ஹோட்டல்கள்.",
      "கலை படைப்புகளாலும் மக்கள் செல்வாக்கினாலும் கோடிக்கணக்கில் வற்றாத தன லாபம்."
    ],
    "career_wealth_en": [
      "Superstar acclaim in entertainment, high fashion, luxury cosmetics, jewelry design, and five-star hospitality.",
      "Multi-million dollar revenues flowing from brand endorsements, creative royalties, and luxury enterprises."
    ],
    "health_precautions_ta": [
      "சிறுநீரகக் கோளாறுகள், நீரிழிவு நோய் (Diabetes), பாலியல் உறுப்புகளில் உஷ்ணம், முகம் மற்றும் சரும நோய்கள்.",
      "அதிக இனிப்புகளையும், கொழுப்பு உணவுகளையும் தவிர்த்து உடற்பயிற்சி செய்வது ஆரோக்கியம் தரும்."
    ],
    "health_precautions_en": [
      "Vulnerable to renal dysfunctions, diabetes mellitus, reproductive tract inflammation, and facial acne.",
      "Moderate refined sugar and dairy fat consumption, hydrate generously, and maintain active lifestyle."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 53) & Saravali Ch. 30"
  },
  {
    "planet": "Venus",
    "planet_name_ta": "சுக்கிரன்",
    "symbol": "✨",
    "element": "நீர் (Jala)",
    "house": 2,
    "bhava_category": "panaphara",
    "house_title_ta": "2-ஆம் பாவம் - தன பாவம் (கவிதை வாக்கு, குபேர தனம் & ஆபரணச் சேர்க்கை)",
    "house_title_en": "2nd House - Dhana Bhava (Poetic Eloquence, Boundless Luxury & Fine Jewels)",
    "core_traits_ta": [
      "சுக்கிரன் 2-ஆம் பாவத்தில் அமைவது தேன் போன்ற இனிமையான பேச்சையும், கவிதை நயத்தையும், அகண்ட தன லாபத்தையும் தரும்.",
      "வசீகரமான புன்னகை, ஒளிமயமான முகத்தோற்றம் மற்றும் அறுசுவை உணவுகளை ரசித்து உண்ணும் பழக்கம்.",
      "நவரத்தினங்கள், தங்கம், வெள்ளி, வைர நகைகள் மற்றும் விலையுயர்ந்த ஆடைகளைச் சேர்ப்பதில் ஆர்வம்.",
      "குடும்பத்தில் மகிழ்ச்சி, அன்பு மற்றும் கணவன்-மனைவி இடையே அன்யோன்யம் நிறைந்திருக்கும்."
    ],
    "core_traits_en": [
      "Venus in the 2nd endows honeyed poetic speech, mesmerizing vocal timbre, and immense fiscal opulence.",
      "Irresistible charming smile, radiant facial glow, and an epicurean appreciation for gourmet cuisine.",
      "Avid collector of fine diamond jewelry, gold bullion, silver artifacts, and designer apparel.",
      "Fosters a joyful, harmonious, and affectionate domestic household overflowing with luxury."
    ],
    "strong_placement_ta": [
      "மீனத்தில் உச்சம் அல்லது சொந்த வீட்டில் பலம் பெற்றால்: பல நூறு கோடி திரவ சேமிப்பு, வைர மாலைகள், வாக்கு பலிதம்.",
      "பேச்சையே முதலீடாக வைத்து சினிமா, பாட்டு மற்றும் வர்த்தகத்தில் உலகளவில் பெரும் புகழ் பெறுவார்."
    ],
    "strong_placement_en": [
      "Exalted in Pisces or in own house: Bestows colossal liquid capital, legendary diamond heirlooms, and prophetic vocal charisma.",
      "Monetizes speech and singing into a multi-million dollar global entertainment and business empire."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: பேச்சில் அதீத கற்பனை, ஆடம்பர விரயங்களால் கடன்கள்.",
      "பற்களில் கோளாறுகள், வாய் புண்கள் அல்லது வலது கண்ணில் பார்வை மங்குதல் வரலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Pretentious speech, profligate debt incurred on luxury ostentation, and family disputes.",
      "Prone to periodontal decay, oral ulcerations, and right-eye vision impairments."
    ],
    "career_wealth_ta": [
      "பாடகர், இசை அமைப்பாளர், பின்னணிக் குரல் கலைஞர், வைர வர்த்தகம், அழகு நிலையம், உணவு விடுதிகள், வங்கித் துறை.",
      "வசீகரப் பேச்சாலும் கலைத் திறனாலும் கோடிக்கணக்கில் செல்வம் குவியும்."
    ],
    "career_wealth_en": [
      "Eminence as playback singer, composer, voice actor, diamond trader, luxury salon founder, and restaurateur.",
      "Vast fortune generated directly through vocal gifts, culinary mastery, and aesthetic commerce."
    ],
    "health_precautions_ta": [
      "தொண்டை அழற்சி, நாக்கில் புண்கள், பற்கள் ஆடுதல், கண் பலவீனம் மற்றும் தைராய்டு குறைபாடுகள்.",
      "குளிர்ந்த பானங்களைத் தவிர்த்து, தொண்டையையும் பற்களையும் சுத்தமாகப் பராமரிக்கவும்."
    ],
    "health_precautions_en": [
      "Susceptible to vocal cord nodules, pharyngitis, tooth decay, ocular strain, and thyroid sluggishness.",
      "Avoid iced beverages, practice vocal warmups, and adhere to strict oral dental hygiene."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 101) & Saravali Ch. 30"
  },
  {
    "planet": "Venus",
    "planet_name_ta": "சுக்கிரன்",
    "symbol": "✨",
    "element": "நீர் (Jala)",
    "house": 3,
    "bhava_category": "upachaya",
    "house_title_ta": "3-ஆம் பாவம் - சகஜ பாவம் (கலை வீரியம் & சகோதரிகளின் அன்பு)",
    "house_title_en": "3rd House - Sahaja Bhava (Artistic Enterprise & Sisters' Goodwill)",
    "core_traits_ta": [
      "நளினமான செயல்பாடுகள், நாடக மற்றும் கலை உணர்வு, புதிய கலை வடிவங்களை உருவாக்கும் கற்பனைத் திறன்.",
      "சகோதர சகோதரிகளிடம் அளப்பரிய பாசம்; குறிப்பாக பெண் சகோதரிகளால் வாழ்வில் அளப்பரிய அதிர்ஷ்டமும் நன்மைகளும் கிட்டும்.",
      "அடிக்கடி பொழுதுபோக்கு உல்லாசப் பயணங்கள், படகு சவாரிகள் மற்றும் இயற்கை எழில் கொஞ்சும் இடங்களுக்குச் செல்லுதல்.",
      "இசைக் கருவிகளை வாசிப்பதிலும், நடனம், புகைப்படம் எடுப்பதிலும் அசாத்திய திறமை படைத்திருப்பார்."
    ],
    "core_traits_en": [
      "Graceful coordination, flair for dramatic performing arts, and inventive aesthetic imagination.",
      "Cherished, deeply loving bond with sisters, who bring immense good fortune and social elevation.",
      "Fond of romantic holidays, scenic yachting voyages, and weekend retreats in luxury resorts.",
      "Innate talent for mastering musical instruments, choreography, fine art photography, and design."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: சர்வதேசப் புகழ் பெற்ற இசைக் கலைஞர், ஆடை வடிவமைப்பாளர், சகோதரிகளால் பெரும் செல்வம்.",
      "கலை முயற்சிகள் யாவும் அமோக வெற்றி பெற்று நாடெங்கும் விருதுகளும் கௌரவங்களும் குவியும்."
    ],
    "strong_placement_en": [
      "Strong or exalted: World-renowned virtuoso musician, celebrity couturier, and immense wealth via sisters.",
      "Artistic projects achieve international box-office and critical acclaim; showered with golden awards."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: சகோதரிகளுடன் கருத்து வேறுபாடுகள், கைகளில் நரம்பு வலி.",
      "சிற்றின்பங்களில் அதிக நாட்டம் கொண்டு ஆற்றலை வீணடித்தல் அல்லது கலை முயற்சிகளில் தோல்வி."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Bitter sibling misunderstandings, wrist nerve fatigue, and dissipated artistic potential.",
      "Indolence, hedonistic lethargy, and commercial failures in creative ventures."
    ],
    "career_wealth_ta": [
      "இசைக் கச்சேரிகள், சினிமா இயக்கம், விளம்பர வடிவமைப்பு, கலைக்கூடங்கள் (Art Galleries), புகைப்படத் துறை, பொழுதுபோக்கு பூங்காக்கள்.",
      "கலைத் துறையாலும் பெண்களின் பேராதரவாலும் அபரிமிதமான தன சேர்க்கை."
    ],
    "career_wealth_en": [
      "Dominant in concert performance, cinema production, creative direction, luxury art galleries, and digital visual media.",
      "Tremendous financial harvest reaped through artistic syndication and female demographic appeal."
    ],
    "health_precautions_ta": [
      "தோள்பட்டை வலி, கைகளில் நரம்புத் தளர்ச்சி, காதுகளில் நீர் வடிதல் மற்றும் சரும வறட்சி.",
      "முறையான கைகளுக்கான ஆசனங்களும், சருமத்திற்கு நல்ல ஈரப்பதமும் தருவது நலம் பயக்கும்."
    ],
    "health_precautions_en": [
      "Prone to shoulder bursitis, upper limb neuralgia, otic fluid accumulation, and skin dehydration.",
      "Gentle yoga stretches and regular skin hydration preserve physical flexibility."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 141) & Saravali Ch. 30"
  },
  {
    "planet": "Venus",
    "planet_name_ta": "சுக்கிரன்",
    "symbol": "✨",
    "element": "நீர் (Jala)",
    "house": 4,
    "bhava_category": "kendra",
    "house_title_ta": "4-ஆம் பாவம் - சுக பாவம் (மாளவ்ய யோகம் / சொகுசு மாளிகைகள், வாகன யோகம் & சுகபோகம்)",
    "house_title_en": "4th House - Sukha Bhava (Malavya Yoga / Luxury Mansions, Exotic Cars & Pure Bliss)",
    "core_traits_ta": [
      "சுக்கிரன் 4-ஆம் பாவத்தில் திக்பலம் (Digbala) பெற்று மாளவ்ய யோகத்தை (Malavya Yoga) உண்டாக்குகிறார்.",
      "அரண்மனை போன்ற ஆடம்பர பங்களா, சொகுசு கார்கள், நீச்சல் குளம், மலர்த் தோட்டங்கள் அமைந்த அழகிய இல்லம்.",
      "தாயாரின் மீது அளப்பரிய பாசம்; தாயார் மிகுந்த வசீகரமும் கலை உணர்வும் கொண்ட பெண்ணாக விளங்குவார்.",
      "வாழ்க்கையில் சகல சௌபாக்கியங்களும் குறைவின்றி அனுபவிக்கும் பூரண சுகபோக யோகம் உண்டு.",
      "இசை, நறுமணம், மென்மையான படுக்கைகள் மற்றும் அழகியல் சூழலில் வாழ்வதில் பேரானந்தம் அடைவார்."
    ],
    "core_traits_en": [
      "Venus attains peak directional potency (Digbala) in the 4th, establishing the celestial Malavya Mahapurusha Yoga.",
      "Destined for magnificent architectural mansions featuring botanical gardens, swimming pools, and imported supercars.",
      "Profound emotional bond with a refined, graceful, and affectionate mother who bestows vast material fortunes.",
      "Enjoys unalloyed domestic tranquility, sensory delight, and luxurious opulence without toil.",
      "Surrounded by ambient melodies, rare fragrances, plush furnishings, and an aesthetic sanctuary."
    ],
    "strong_placement_ta": [
      "மீனத்தில் உச்சம் அல்லது ரிஷபம்/துலாத்தில் ஆட்சி பெற்று மாளவ்ய யோகம் அமைந்தால்: நாட்டின் முன்னணி சொகுசு ரியல் எஸ்டேட் அதிபர், அரச மாளிகைகள்.",
      "எண்ணற்ற சொகுசு கார்களின் அணிவகுப்பு, பூரண மன அமைதி மற்றும் உலகளாவிய கௌரவம்."
    ],
    "strong_placement_en": [
      "Exalted or own house with Malavya Yoga: Premier luxury real estate tycoon, owner of celebrated heritage palaces.",
      "Commands a prestigious garage of exotic supercars, serene bliss, and universal civic honors."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தாயாரின் சிறுநீரக ஆரோக்கியம் பாதித்தல், சொகுசுப் பொருட்களால் கடன்கள்.",
      "வாகன விபத்துகள், வீட்டு அலங்காரங்களில் வீண் விரயங்கள் மற்றும் குடும்பத்தில் சலசலப்பு."
    ],
    "weak_placement_en": [
      "Debilitated in Virgo or afflicted: Maternal renal ailments, financial distress from reckless luxury spending.",
      "Vehicle breakdowns, litigations over residential estates, and domestic discontent."
    ],
    "career_wealth_ta": [
      "சொகுசு ரியல் எஸ்டேட், இன்டீரியர் டிசைனிங், ஆட்டோமொபைல் ஷோரூம்கள், வாசனைத் திரவிய தயாரிப்பு, நட்சத்திர விடுதிகள்.",
      "சொத்துகளின் மதிப்பு பல மடங்கு உயர்வதாலும் அழகியல் தொழில்களாலும் பல நூறு கோடி செல்வம்."
    ],
    "career_wealth_en": [
      "Superlative success in luxury architectural realty, interior aesthetics, exotic automobile dealerships, and resorts.",
      "Vast generational capital accrued through real estate appreciation and hospitality empires."
    ],
    "health_precautions_ta": [
      "இதயத்தில் கொழுப்பு, நெஞ்சு சளி, நீரிழிவு, சுவாசப் பாதையில் ஒவ்வாமை மற்றும் சிறுநீரக மந்தம்.",
      "கொழுப்பு மற்றும் பால் சார்ந்த இனிப்புகளைக் குறைத்து இதய ஆரோக்கியத்தைப் பேண வேண்டும்."
    ],
    "health_precautions_en": [
      "Susceptible to coronary lipid build-up, bronchial asthma, hyperglycemia, and sluggish renal drainage.",
      "Avoid heavy dairy confectionery, engage in cardiovascular fitness, and monitor lipid ratios."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 175) & Saravali Ch. 30"
  },
  {
    "planet": "Venus",
    "planet_name_ta": "சுக்கிரன்",
    "symbol": "✨",
    "element": "நீர் (Jala)",
    "house": 5,
    "bhava_category": "trikona",
    "house_title_ta": "5-ஆம் பாவம் - புத்திர பாவம் (கலை ஞானம், காதல் யோகம் & அழகான சந்ததிகள்)",
    "house_title_en": "5th House - Putra Bhava (Artistic Intellect, Romantic Bliss & Beautiful Progeny)",
    "core_traits_ta": [
      "கவிதை, நாடகம், சினிமா மற்றும் நுண்கலைகளில் அசாத்தியமான கற்பனைத் திறனும் புத்திசாலித்தனமும் கொண்டவர்.",
      "அழகான, குணவதியான மற்றும் கலைத் துறையில் சாதனை படைக்கும் பெண் குழந்தைகள் அமைய வாய்ப்புண்டு.",
      "வாழ்க்கையில் காதல், ரொமான்ஸ் மற்றும் கவர்ச்சிகரமான நட்பு வட்டாரம் நிறைந்து காணப்படும்.",
      "பூர்வ புண்ணிய பலத்தால் தொட்ட கலை முயற்சிகள் யாவும் வெற்றி பெற்று சமூகத்தில் பெரும் வரவேற்பைப் பெறும்."
    ],
    "core_traits_en": [
      "Sublime creative intellect; master of poetic romance, cinematic dramaturgy, and visual aesthetics.",
      "Blessed with beautiful, graceful, and artistically gifted children (often charming daughters).",
      "Romantic, passionate heart; experiences fulfilling love affairs and magnetic social associations.",
      "Past-life merit (Poorvapunya) fuels frictionless breakthroughs in entertainment, fashion, and speculative investments."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: புகழ்பெற்ற திரைப்பட இயக்குநர், கலை வித்தகர், பன்னாட்டு விருதுகள், கோடீஸ்வர யோகம்.",
      "குழந்தைகள் உலகப் புகழ் பெறுவார்கள்; மகிழ்ச்சி நிறைந்த குடும்பமும், முதலீடுகளில் அபரிமிதமான லாபமும் கிட்டும்."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Celebrated film director, artistic luminary, international trophy winner, and multi-millionaire.",
      "Progeny become globally renowned icons; abundant financial returns from creative investments."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: காதலில் ஏமாற்றங்கள், புத்திர பாக்கியத்தில் காலதாமதம்.",
      "சினிமா அல்லது கலை முதலீடுகளில் பெரும் நிதி இழப்புகள் மற்றும் பெண்களால் அவப்பெயர்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Bitter heartbreaks, delayed childbearing, and anxieties regarding daughters.",
      "Crippling financial losses incurred through failed creative speculations and romantic scandals."
    ],
    "career_wealth_ta": [
      "திரைப்படத் தயாரிப்பாளர், ஆடை வடிவமைப்பாளர், நாவலாசிரியர், பங்குச் சந்தை முதலீட்டாளர், கலைக்கூடம், ஒப்பனைக் கலை.",
      "கலை படைப்புகளின் உரிமங்கள், சினிமா மற்றும் முதலீடுகள் மூலம் கோடிக்கணக்கில் வருவாய்."
    ],
    "career_wealth_en": [
      "Eminence as cinema producer, fashion designer, novelist, venture capital partner, and artistic curator.",
      "Immense royalties and investment jackpots derived from intellectual entertainment properties."
    ],
    "health_precautions_ta": [
      "செரிமானக் கோளாறுகள், வயிற்றுப் பகுதியில் கொழுப்பு, கருப்பை/விதைப்பை உபாதைகள் மற்றும் நீரிழிவு.",
      "சரியான நேரத்திற்கு சத்தான உணவை உட்கொள்ளுதலும், இனிப்புகளைக் கட்டுப்படுத்துவதும் அவசியம்."
    ],
    "health_precautions_en": [
      "Prone to gastric dysbiosis, abdominal adiposity, ovarian/testicular hormonal imbalances, and hyperglycemia.",
      "Maintain clean dietary habits, moderate dessert consumption, and undergo routine endocrine tests."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 221) & Saravali Ch. 30"
  },
  {
    "planet": "Venus",
    "planet_name_ta": "சுக்கிரன்",
    "symbol": "✨",
    "element": "நீர் (Jala)",
    "house": 6,
    "bhava_category": "dusthana",
    "house_title_ta": "6-ஆம் பாவம் - சத்ru பாவம் (எதிரிகள் இல்லாமை & ஆரோக்கியப் பராமரிப்பு)",
    "house_title_en": "6th House - Satru Bhava (Harmonizing Foes & Urological Care)",
    "core_traits_ta": [
      "அமைதியான சுபாவம்; யாரிடமும் விரோதம் பாராட்டாமல் தன் கவர்ச்சியாலும் இன்முகத்தாலும் அனைவரையும் வசீகரிப்பார்.",
      "நேரடி மோதல்களைத் தவிர்த்து நயமாகப் பேசி பிரச்சினைகளைத் தீர்த்து வைக்கும் ராஜதந்திர குணம்.",
      "சுக்கிரன் 6-ஆம் பாவத்தில் இருப்பது மறைவு ஸ்தானம் என்பதால் ஆரோக்கியத்தில் அதிக கவனம் செலுத்த வேண்டும்.",
      "வேலையாட்களிடம் அன்பாகவும் பெருந்தன்மையாகவும் நடந்து கொண்டு வேலை வாங்குவார்."
    ],
    "core_traits_en": [
      "Gentle, peace-loving temperament; charms potential adversaries with disarming courtesy and warmth.",
      "Resolves conflicts through refined diplomatic tact rather than harsh adversarial clashes.",
      "Venus in the 6th occupies a dusthana; calls for conscious discipline regarding sensual excesses and health.",
      "Treats employees and domestic staff with kindness and generous consideration."
    ],
    "strong_placement_ta": [
      "சுப பலத்துடன் இருப்பின்: எதிரிகள் தானாகவே விலகிப் போதல், கடன் இல்லாத வாழ்க்கை, ஆரோக்கியத்தில் முன்னேற்றம்.",
      "அழகு சாதனங்கள், பெண்கள் நலம் மற்றும் மருத்துவத் துறைகளில் நற்பெயர் பெறுவார்."
    ],
    "strong_placement_en": [
      "Strong with benefic aspects: Complete dissolution of hostilities, debt-free living, and restored vitality.",
      "Achieves respected standing in aesthetic medicine, cosmetics dermatology, and female healthcare."
    ],
    "weak_placement_ta": [
      "கன்னியில் நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: நீரிழிவு நோய் (Diabetes), சிறுநீரகக் கற்கள், பாலியல் வியாதிகள்.",
      "பெண்களால் வழக்குகளும், வீண் விரயங்களும், வேலையாட்களால் ஏமாற்றங்களும் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated in Virgo or afflicted: Chronic diabetes, kidney stones, reproductive tract infections, and low vitality.",
      "Litigations with female acquaintances, heavy expenses on treatments, and deceit by subordinates."
    ],
    "career_wealth_ta": [
      "காஸ்மெட்டிக் அறுவை சிகிச்சை, தோல் மருத்துவம், பெண்களுக்கான ஆடைகள், அழகு நிலையங்கள், ஹோட்டல் உணவு நிர்வாகம்.",
      "வாடிக்கையாளர் சேவைகளாலும் நேர்மையான உழைப்பாலும் நிலையான வருமானம்."
    ],
    "career_wealth_en": [
      "Thrives in cosmetic surgery, dermatology, female couture, luxury spa management, and dietetics.",
      "Earns stable revenues by serving high-end clientele with personalized aesthetic solutions."
    ],
    "health_precautions_ta": [
      "சிறுநீரகக் கற்கள், நீரிழிவு நோய், பாலியல் உறுப்புகளில் தொற்று, கண் பார்வைக் கோளாறு மற்றும் அதிக சோர்வு.",
      "தினமும் அதிகளவு சுத்தமான தண்ணீர் குடிப்பதும், சர்க்கரை அளவை தவறாமல் பரிசோதிப்பதும் மிக அவசியம்."
    ],
    "health_precautions_en": [
      "High susceptibility to nephrolithiasis (kidney stones), glycosuria, urinary tract infections, and chronic fatigue.",
      "Drink 3-4 liters of purified water daily, eliminate refined sugars, and schedule regular renal ultrasound scans."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 261) & Saravali Ch. 30"
  },
  {
    "planet": "Venus",
    "planet_name_ta": "சுக்கிரன்",
    "symbol": "✨",
    "element": "நீர் (Jala)",
    "house": 7,
    "bhava_category": "kendra",
    "house_title_ta": "7-ஆம் பாவம் - களத்திர பாவம் (மாளவ்ய யோகம் / பேரழகான துணை & தாம்பத்திய சுகம்)",
    "house_title_en": "7th House - Kalathra Bhava (Malavya Yoga / Exceptionally Beautiful Spouse & Conjugal Bliss)",
    "core_traits_ta": [
      "சுக்கிரன் 7-ஆம் பாவத்தில் (காரகோ பாவக நாஸ்தி விதிக்கு உட்படாமல் சுப பலத்துடன் இருந்தால்) பேரழகான, காந்தக் கவர்ச்சிமிக்க வாழ்க்கைத் துணையைத் தருவார்.",
      "வாழ்க்கைத் துணை கலை உணர்வும், நற்குணமும், செல்வச் செழிப்பும் பொருந்திய குடும்பத்திலிருந்து வருவார்.",
      "தம்பதியரிடையே அளப்பரிய ரொமான்ஸ், பரஸ்பர கவர்ச்சி, தாம்பத்திய சுகம் மற்றும் ஆடம்பர வாழ்க்கை அமையும்.",
      "கூட்டு வர்த்தகத்தில் பெண்களின் ஆதரவாலும், அழகியல் தொழில்களாலும் அளப்பரிய தன லாபம் கிட்டும்."
    ],
    "core_traits_en": [
      "Venus in the 7th (unafflicted) gifts an extraordinarily gorgeous, graceful, and aesthetically refined spouse.",
      "Partner hails from a distinguished, wealthy, and cultured family; embodies charm and emotional tenderness.",
      "Marital union radiates romance, mutual adoration, sensual fulfillment, and aristocratic luxury.",
      "Commercial partnerships thrive spectacularly through female demographic engagement and aesthetic ventures."
    ],
    "strong_placement_ta": [
      "மீனத்தில் உச்சம் அல்லது ரிஷபம்/துலாத்தில் ஆட்சி பெற்று மாளவ்ய யோகம் அமைந்தால்: உலகப் பேரழகி/அழகன் போன்ற துணை, அரச யோகம்.",
      "பன்னாட்டு வர்த்தகத்தில் மாபெரும் வெற்றி, தம்பதிகள் இருவரும் சமுதாயத்தில் உன்னத நட்சத்திரங்களாகப் போற்றப்படுவர்."
    ],
    "strong_placement_en": [
      "Exalted in Pisces or in own signs forming Malavya Yoga: Marries a breathtakingly attractive partner of aristocratic lineage.",
      "Triumphs in international fashion and luxury trade, celebrated universally as an enchanting power couple."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தாம்பத்தியத்தில் அதிருப்தி, பல பெண்களின்/ஆண்களின் தொடர்புகளால் குடும்ப விரிசல்.",
      "விவாகரத்து வழக்குகள், துணையின் ஆரோக்கியக் குறைவு மற்றும் கூட்டாளிகளால் ஏமாற்றப்பட்டு இழப்பு."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Severe conjugal friction, infidelity scandals eroding marital trust, and bitter divorces.",
      "Spouse suffers from chronic reproductive ailments; heavy losses through deceitful business partners."
    ],
    "career_wealth_ta": [
      "சர்வதேச ஆடை வர்த்தகம், அழகு சாதன ஏற்றுமதி, சினிமா-நாடகக் கூட்டாண்மை, சொகுசு விடுதிகள், திருமண நிகழ்வு மேலாண்மை (Wedding Planning).",
      "வாழ்க்கைத் துணையின் அதிர்ஷ்டத்தாலும் சர்வதேச வர்த்தகத்தாலும் கோடிக்கணக்கில் சொத்துகள் சேரும்."
    ],
    "career_wealth_en": [
      "Dominant in luxury bridal couture, cosmetics export, cinema consortiums, resort hospitality, and celebrity event management.",
      "Vast wealth multiplication generated via spousal fortunes and joint commercial syndicates."
    ],
    "health_precautions_ta": [
      "சிறுநீரகக் கோளாறுகள், பாலியல் உறுப்பு அழற்சி, விரைவாதம், நீரிழிவு மற்றும் அடிவயிற்று உஷ்ணம்.",
      "முறையான மருத்துவப் பரிசோதனைகளும், உஷ்ணத்தைத் தணிக்கும் உணவுகளும் மிகவும் அவசியம்."
    ],
    "health_precautions_en": [
      "Susceptible to renal congestion, reproductive tract inflammation, prostatitis, diabetes, and pelvic heat.",
      "Strict personal hygiene, ample hydration, and periodic urogenital examinations are mandatory."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Venus",
    "planet_name_ta": "சுக்கிரன்",
    "symbol": "✨",
    "element": "நீர் (Jala)",
    "house": 8,
    "bhava_category": "dusthana",
    "house_title_ta": "8-ஆம் பாவம் - ஆயுள் பாவம் (தீர்க்காயுள், எதிர்பாராத தன வரவு & மறைமுக சுகம்)",
    "house_title_en": "8th House - Ayur Bhava (Long Longevity, Hidden Riches & Sudden Legacies)",
    "core_traits_ta": [
      "சுக்கிரன் 8-ஆம் பாவத்தில் அமர்வது ஜாதகருக்கு நீண்ட ஆயுளையும், எதிர்பாராத திடீர் தன யோகத்தையும் தரும்.",
      "மனைவி/கணவன் வழியில் பெரும் சொத்துகள், காப்பீட்டுத் தொகைகள் மற்றும் உயில் சொத்துகள் தடையின்றி வந்து சேரும்.",
      "மறைமுக இன்பங்களை அனுபவிப்பதில் ஆர்வம்; ரகசிய உறவுகள் அல்லது சாகசங்களில் ஈடுபாடு ஏற்படலாம்.",
      "ஆபத்தான சூழ்நிலைகளிலும் தன் வசீகரத்தாலும் சாதுரியத்தாலும் தப்பிக்கும் விவேகம் கொண்டிருப்பார்."
    ],
    "core_traits_en": [
      "Venus in the 8th is classically celebrated for bestowing smooth, peaceful longevity and sudden financial windfalls.",
      "Reaps substantial unearned wealth, life insurance settlements, and rich legacy inheritances through marriage.",
      "Fascinated by clandestine pleasures, private luxuries, and the hidden psychological dynamics of relationships.",
      "Survives perilous crises effortlessly through personal charm, diplomacy, and unexpected goodwill."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: அமைதியான பூரண தீர்க்காயுள், பல நூறு கோடி உயில் சொத்துகள், நவரத்தினங்கள்.",
      "துணையின் குடும்பத்திலிருந்து மாபெரும் வரதட்சணை மற்றும் அசையா சொத்துகள் வந்து குவியும்."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Serene long life, multi-million dollar testamentary estates, and ancestral gems.",
      "Acquires massive dowry assets, prime real estate, and financial trusts through marital ties."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: பாலியல் நோய்கள், சிறுநீரகக் கோளாறுகள், துணையின் ஆரோக்கியம் பாதித்தல்.",
      "பெண்களால் வழக்குகளும், ரகசிய உறவுகளால் சமுதாயத்தில் மானபங்கமும் ஏற்பட வாய்ப்புண்டு."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Veneral/urological infections, severe kidney disease, and spousal ill-health.",
      "Blackmail or defamation litigations arising from illicit affairs; sudden dissipation of inherited wealth."
    ],
    "career_wealth_ta": [
      "ஆயுள் காப்பீட்டு நிறுவனம், தொல்பொருள் நகை மதிப்பீட்டாளர், ரகசிய நிதி ஆலோசகர், நச்சுயியல் மருத்துவர், அழகியல் துறை.",
      "உயில் சொத்துகள், இன்சூரன்ஸ் முதிர்வுகள் மற்றும் திடீர் தன வரவால் பெரும் பணக்கார யோகம்."
    ],
    "career_wealth_en": [
      "Flourishes in insurance syndicates, antique gem valuation, private family office advisory, and aesthetic toxicology.",
      "Enormous fortune derived from testamentary inheritances, structured settlements, and windfall trusts."
    ],
    "health_precautions_ta": [
      "சிறுநீரகக் கோளாறுகள், நீரிழிவு, சிறுநீர்ப் பாதை தொற்று, பாலியல் பலவீனம் மற்றும் மூல நோய்.",
      "அதிக தண்ணீர் அருந்துவதும், சர்க்கரை மற்றும் கொழுப்பைக் கட்டுப்படுத்துவதும் மிக அவசியம்."
    ],
    "health_precautions_en": [
      "Vulnerable to renal lithiasis, diabetic nephropathy, chronic urinary tract infections, and hemorrhoids.",
      "Maintain high fluid intake, strictly regulate glycemic index, and practice defensive sexual hygiene."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Venus",
    "planet_name_ta": "சுக்கிரன்",
    "symbol": "✨",
    "element": "நீர் (Jala)",
    "house": 9,
    "bhava_category": "trikona",
    "house_title_ta": "9-ஆம் பாவம் - பாக்கிய பாவம் (பரம பாக்கியம், தர்ம செல்வம் & கலை யாத்திரை)",
    "house_title_en": "9th House - Bhagya Bhava (Sublime Fortune, Righteous Wealth & Cultural Travel)",
    "core_traits_ta": [
      "சுக்கிரன் 9-ஆம் பாவத்தில் அமர்வது மனிதப் பிறவியின் சகல சுகங்களையும் அனுபவிக்கும் மகா பாக்கிய அமைப்பாகும்.",
      "தந்தையின் மீது அளப்பரிய பாசமும் மரியாதையும்; தந்தை கலை உணர்வும் செல்வமும் பொருந்தியவராக இருப்பார்.",
      "அழகிய கோவில்கள், கலாச்சார மையங்கள் மற்றும் வெளிநாடுகளுக்கு உல்லாசப் பயணங்கள் செல்வதில் பேரானந்தம்.",
      "மனைவி வந்த பிறகு வாழ்க்கை பொற்காலமாக மாறும்; தர்ம சிந்தனையும், வறியவர்களுக்கு உதவும் வள்ளல் தன்மையும் உண்டு."
    ],
    "core_traits_en": [
      "Venus in the 9th is one of the most radiant placements for continuous worldly bliss, elegance, and good fortune.",
      "Deep affection for a cultivated, prosperous, and artistically refined father who acts as a loving patron.",
      "Delights in cultural tours, exploring architectural wonders, visiting ornate temples, and world journeys.",
      "Marriage ushers in a golden epoch of prosperity; generous philanthropist supporting artistic and cultural trusts."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: லக்ஷ்மி யோகம்! கோடானுகோடி சொத்துகள், சர்வதேச கௌரவங்கள், அரச போகம்.",
      "கலை கலாச்சார அறக்கட்டளைகளை நிறுவி உலகளாவிய நற்பெயரையும், வற்றாத செல்வத்தையும் பெறுவார்."
    ],
    "strong_placement_en": [
      "Exalted or own house: Bestows supreme Lakshmi Yoga! Multi-million dollar patrimony, global honors, and aristocratic bliss.",
      "Founds monumental cultural endowments, recognized internationally as an icon of cultural sophistication."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தந்தையின் உடல்நலம் பாதித்தல், மத சடங்குகளில் ஈடுபாடின்மை.",
      "வெளிநாட்டுப் பயணங்களில் பண விரயங்கள் மற்றும் காதல் விவகாரங்களால் குடும்பத்தில் கசப்புகள்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Paternal health difficulties, cynicism towards spiritual traditions, and wasted travel funds.",
      "Disruptions in overseas journeys and familial tensions caused by controversial romantic liaisons."
    ],
    "career_wealth_ta": [
      "கலாச்சாரத் தூதர், சர்வதேச சுற்றுலா அதிபர், கலைப் பல்கலைக்கழக அறங்காவலர், உயர் ஆடை ஏற்றுமதி, திரைப்பட விநியோகம்.",
      "தர்ம வழியிலும், வெளிநாட்டுத் தொடர்புகளாலும் பல தலைமுறைகளுக்கு நிலைக்கும் மாபெரும் செல்வம்."
    ],
    "career_wealth_en": [
      "Distinction as cultural ambassador, international tourism magnate, trustee of arts academies, and cinema distributor.",
      "Generates pure, enduring generational fortunes through principled cultural and creative enterprises."
    ],
    "health_precautions_ta": [
      "தொடைப் பகுதியில் நரம்பு வலி, இடுப்பு வாதம், நீரிழிவு மற்றும் கல்லீரல் கொழுப்பு.",
      "முறையான உடற்பயிற்சியும், சமச்சீரான உணவு முறையும் உடல் வனப்பை நீண்ட காலம் காக்கும்."
    ],
    "health_precautions_en": [
      "Susceptible to femoral neuropathy, sciatica sensitivity, hyperglycemia, and mild hepatic steatosis.",
      "Daily stretching, moderate low-sugar nutrition, and active recreational walking preserve bodily grace."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Venus",
    "planet_name_ta": "சுக்கிரன்",
    "symbol": "✨",
    "element": "நீர் (Jala)",
    "house": 10,
    "bhava_category": "kendra",
    "house_title_ta": "10-ஆம் பாவம் - ஜீவன பாவம் (மாளவ்ய யோகம் / கலை சாம்ராஜ்யம் & மக்கள் செல்வாக்கு)",
    "house_title_en": "10th House - Karma Bhava (Malavya Yoga / Entertainment Empire & Celebrity Acclaim)",
    "core_traits_ta": [
      "சுக்கிரன் 10-ஆம் பாவத்தில் அமர்வது கலை, சினிமா, அழகு சாதனங்கள் மற்றும் பெண்களுக்கான வர்த்தகத்தில் மாபெரும் சாம்ராஜ்யத்தை உருவாக்கும்.",
      "கவர்ச்சிகரமான ஆளுமை; உயர் அதிகாரிகளுடனும் மக்கள் மத்தியிலும் அளப்பரிய அன்பும் ஆதரவும் பெறுவார்.",
      "தொழிலில் புதுமையான அழகியல் யுக்திகளைக் கையாண்டு லட்சக்கணக்கான வாடிக்கையாளர்களை ஈர்க்கும் சாமர்த்தியம்.",
      "சமூகத்தில் பெரும் புகழும், பன்னாட்டு விருதுகளும், ஆடம்பரமான வாழ்க்கை முறையும் பெறுவார்."
    ],
    "core_traits_en": [
      "Venus in the 10th builds towering commercial empires across entertainment, cosmetics, cinema, and luxury lifestyle.",
      "Irresistible executive charisma; wins unstinting affection and patronage from civic dignitaries and the public.",
      "Infuses commerce with creative elegance, captivating millions of devoted consumers worldwide.",
      "Celebrated with stellar public fame, international industry awards, and an enviable, glamorous lifestyle."
    ],
    "strong_placement_ta": [
      "மீனத்தில் உச்சம் அல்லது ரிஷபம்/துலாத்தில் ஆட்சி பெற்று மாளவ்ய யோகம் அமைந்தால்: உலக சினிமா சூப்பர் ஸ்டார், ஃபேஷன் சாம்ராஜ்ய அதிபர்.",
      "அரசாங்கத்தால் சகல மரியாதைகளும் வழங்கப்பட்டு, சமுதாயத்தின் முதன்மை நட்சத்திரமாக முடிசூடுவார்."
    ],
    "strong_placement_en": [
      "Exalted in Pisces or in own signs forming Malavya Yoga: International cinema icon, chairman of global luxury fashion conglomerates.",
      "Conferred premier cultural awards by heads of state; reigns as the undisputed monarch of style."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தொழிலில் திடீர் வீழ்ச்சி, பெண்களால் அவப்பெயர் மற்றும் வழக்குகளால் நஷ்டம்.",
      "வாடிக்கையாளர் நம்பிக்கையை இழத்தலும், உத்தியோகத்தில் நிலையற்ற தன்மையும் உண்டாகலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Sudden downfall in public prestige, controversies with female associates, and litigation losses.",
      "Erosion of brand equity, workplace scandals, and volatile employment trajectory."
    ],
    "career_wealth_ta": [
      "திரைப்படத்துறை, தொலைக்காட்சி, ஃபேஷன் டிசைனிங், அழகு நிலையங்கள், வைர வர்த்தகம், ஐந்து நட்சத்திர விடுதிகள், வாசனைத் திரவியங்கள்.",
      "கலை படைப்புகளாலும் பிராண்ட் அம்பாசிடர் ஒப்பந்தங்களாலும் பல நூறு கோடி செல்வம் குவியும்."
    ],
    "career_wealth_en": [
      "Dominant in film production, digital entertainment, haute couture, diamond retail, luxury hospitality, and perfumery.",
      "Accumulates colossal multi-million dollar capital via commercial royalties, equity stakes, and global brand endorsements."
    ],
    "health_precautions_ta": [
      "பணிச்சுமையால் நீரிழிவு, மூட்டு வலி, ரத்த அழுத்தம் மற்றும் தூக்கமின்மை.",
      "ஆடம்பர விருந்துகளையும், மது-கொழுப்பு உணவுகளையும் தவிர்த்து உடலை ஆரோக்கியமாகப் பேண வேண்டும்."
    ],
    "health_precautions_en": [
      "Prone to metabolic syndrome, knee cartilage wear, hypertension, and occupational insomnia.",
      "Avoid lavish late-night banquets, eliminate alcohol and trans-fats, and prioritize deep restorative rest."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Venus",
    "planet_name_ta": "சுக்கிரன்",
    "symbol": "✨",
    "element": "நீர் (Jala)",
    "house": 11,
    "bhava_category": "upachaya",
    "house_title_ta": "11-ஆம் பாவம் - லாப பாவம் (அகண்ட தன லாபம் / பெண்களின் பேராதரவு & குபேர யோகம்)",
    "house_title_en": "11th House - Labha Bhava (Massive Liquid Wealth, Women's Patronage & Wish Fulfillment)",
    "core_traits_ta": [
      "சுக்கிரன் 11-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமர்வது அளவில்லாத செல்வச் செழிப்பையும், அனைத்து ஆசைகளும் உடனே நிறைவேறுதலையும் தரும்.",
      "செல்வாக்கு மிக்க பெண்களின் நட்பும், ஆதரவும் கிடைத்து வாழ்வில் அடுத்தடுத்து மாபெரும் உயர்வுகளை அடைவார்.",
      "சொகுசு கார்கள், வைர நகைகள், பட்டு ஆடைகள் மற்றும் உயர்ரக வசதிகள் எப்போதும் நிறைந்து காணப்படும்.",
      "மூத்த சகோதர சகோதரிகளிடம் அளப்பரிய பாசம் நிலவும்; அவர்களால் பல கோடி ரூபாய் தன லாபம் கிட்டும்."
    ],
    "core_traits_en": [
      "Venus in the 11th (an Upachaya house) is a golden engine for compounding luxury wealth and effortless wish-fulfillment.",
      "Enjoys decisive patronage, funding, and mentorship from highly placed, affluent women across sectors.",
      "Surrounded by premium sports cars, diamond jewellery, bespoke designer wardrobes, and effortless luxury.",
      "Cherishes deep fraternal devotion with elder siblings, who facilitate lucrative investments and social prominence."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: எண்ணற்ற வழிகளிலிருந்து பணம் கொட்டும், சொகுசு மாளிகைகள், குபேர யோகம்.",
      "திரைப்படம், அழகு சாதனங்கள் மற்றும் கலை வர்த்தகத்தில் நாட்டின் முன்னணி பணக்காரராகத் திகழுதல்."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Bestows multi-billion dollar liquid holdings, luxury estates, and supreme Kubera Yoga.",
      "Ranks among the foremost wealthy magnates in entertainment, cosmetics, and luxury consumer goods."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: நண்பர்களால் ஏமாற்றப்பட்டு தன நஷ்டம், பெண்களால் வீண் விரயங்கள்.",
      "லாபங்கள் கைநழுவிப் போதல் அல்லது ஆடம்பரச் செலவுகளால் வங்கி இருப்பு குறைதல்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Exploitation by counterfeit socialite companions, financial bleedings through indiscreet liaisons.",
      "Anticipated dividends vanish through profligate party expenditures and unhedged investments."
    ],
    "career_wealth_ta": [
      "சினிமா நிதி முதலீடு, சொகுசு கார்கள் வர்த்தகம், வைர நகைக் கடைகள், பெண்களுக்கான ஆடைகள், நட்சத்திர ஹோட்டல்கள், வென்ச்சர் கேபிடல்.",
      "முதலீடுகளின் அதிவேக வளர்ச்சியாலும் பெண்கள் ஆதரவாலும் கோடீஸ்வர யோகம்."
    ],
    "career_wealth_en": [
      "Lucrative success in film finance syndication, exotic car imports, diamond retail chains, luxury apparel, and venture capital.",
      "Extraordinary capital multiplication placing the native in the elite billionaire tier."
    ],
    "health_precautions_ta": [
      "இடது காது வலி, கணுக்கால் நரம்பு இழுத்தல், நீரிழிவு மற்றும் சரும அலர்ஜி.",
      "கால் நரம்புகளுக்கான உடற்பயிற்சியும், ரத்த சர்க்கரை பரிசோதனைகளும் நலம் காக்கும்."
    ],
    "health_precautions_en": [
      "Susceptible to left-ear ache, ankle ligament stiffness, hyperglycemia, and skin dermatosis.",
      "Daily ankle mobility drills, compression wear during flights, and strict glycemic monitoring."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Venus",
    "planet_name_ta": "சுக்கிரன்",
    "symbol": "✨",
    "element": "நீர் (Jala)",
    "house": 12,
    "bhava_category": "dusthana",
    "house_title_ta": "12-ஆம் பாவம் - விரய பாவம் (அயன சயன சுகம் / சொகுசு வெளிநாட்டு வாழ்க்கை & ஆன்மீக கலை)",
    "house_title_en": "12th House - Vraya Bhava (Supreme Bedroom Pleasures, Luxurious Foreign Living & Spiritual Art)",
    "core_traits_ta": [
      "சுக்கிரன் 12-ஆம் பாவத்தில் அமர்வது காரகோ பாவக நாஸ்தி இல்லாத மிகச்சிறந்த அயன சயன சுகத்தைத் தரும் ராஜ யோகமாகும்.",
      "மஞ்சத்தில் பூரண சுகம், அழகான தாம்பத்திய வாழ்க்கை, நறுமணம் வீசும் ஆடம்பர படுக்கையறைகள் மற்றும் ஆழ்ந்த தூக்கம்.",
      "பிறந்த ஊரை விட வெளிநாடுகளிலோ அல்லது கடல் கடந்த இடங்களிலோ அளப்பரிய செல்வமும், சொகுசு வாழ்க்கையும் கிட்டும்.",
      "பணத்தை ஆடம்பரப் பொருட்கள், கலைப் படைப்புகள் மற்றும் தர்ம காரியங்களுக்காக தாராளமாக வாரி வழங்குவார்."
    ],
    "core_traits_en": [
      "Venus in the 12th is classically hailed as an extraordinary exception: bestows unmatched sensory pleasure and bedroom bliss (Ayana Sayana Sukha).",
      "Exquisite marital intimacy, aromatic bedrooms furnished in plush silks, and deeply restorative, peaceful sleep.",
      "Achieves peak wealth, glamorous status, and aristocratic comforts when settled in foreign or overseas territories.",
      "Spends with magnificent liberality on bespoke luxuries, world art treasures, and noble philanthropic donations."
    ],
    "strong_placement_ta": [
      "மீனத்தில் உச்சம் அல்லது சொந்த வீட்டில் சுப பலத்துடன் இருப்பின்: வெளிநாட்டில் அரண்மனை போன்ற மாளிகை, பன்னாட்டுச் செல்வம்.",
      "அயன சயன சுகம் பூரணமாகக் கிட்டும்; சமுதாயத்தில் பெரும் மதிப்பும், ஆன்மீக முக்தியும் பெறுவார்."
    ],
    "strong_placement_en": [
      "Exalted in Pisces or in own house: Commands fairy-tale estates in prime overseas locales; vast foreign exchange wealth.",
      "Unblemished conjugal ecstasy, blissful peace of mind, and sublime spiritual liberation (Moksha)."
    ],
    "weak_placement_ta": [
      "கன்னியில் நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தாம்பத்திய சுகக் குறைவு, பாலியல் வியாதிகள், தூக்கமின்மை.",
      "இடது கண் பாதிப்பு, ஆடம்பரப் பழக்கங்களால் கடன் மற்றும் வெளிநாட்டில் சட்டச் சிக்கல்கள் வரலாம்."
    ],
    "weak_placement_en": [
      "Debilitated in Virgo or afflicted: Bedroom coldness, urogenital infections, acute insomnia, and left eye vision defects.",
      "Heavy debts incurred through reckless nocturnal dissipation; legal disputes with foreign authorities."
    ],
    "career_wealth_ta": [
      "சர்வதேச சொகுசு விடுதிகள், கப்பல் போக்குவரத்து, வெளிநாட்டுத் தூதரகங்கள், வாசனைத் திரவிய ஏற்றுமதி, உலகளாவிய ஆடை வர்த்தகம்.",
      "வெளிநாட்டு நாணயங்களாலும் பன்னாட்டு வர்த்தகத்தாலும் கோடிக்கணக்கில் வற்றாத தன லாபம்."
    ],
    "career_wealth_en": [
      "Dominates in international luxury hospitality, cruise liners, consular diplomacy, perfume export, and global fashion.",
      "Colossal income denominated in hard foreign currencies flowing from overseas holdings."
    ],
    "health_precautions_ta": [
      "இடது கண் பார்வைக் கோளாறு, பாதங்களில் வலி, நீரிழிவு, சிறுநீரகக் கோளாறுகள் மற்றும் தூக்கமின்மை.",
      "தூங்கும் முன் கண்களைக் குளிர்ந்த நீரால் கழுவுதலும், பாதங்களை மசாஜ் செய்வதும் நல்ல தூக்கத்தைத் தரும்."
    ],
    "health_precautions_en": [
      "Prone to left-eye refractive strain, peripheral foot neuralgia, diabetes, renal weakness, and insomnia.",
      "Nightly cold eye-compresses, gentle foot reflexology, and regular renal health screenings."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Saturn",
    "planet_name_ta": "சனி",
    "symbol": "🪐",
    "element": "காற்று (Vayu)",
    "house": 1,
    "bhava_category": "kendra",
    "house_title_ta": "1-ஆம் பாவம் - லக்னம் (சச யோகம் / இரும்பு போன்ற மன உறுதி & உழைப்பு)",
    "house_title_en": "1st House - Ascendant / Tanu Bhava (Sasa Yoga / Iron Will & Enduring Discipline)",
    "core_traits_ta": [
      "ஆழ்ந்த சிந்தனை, பக்குவமான முதிர்ச்சி, அடக்கம் மற்றும் இரும்பு போன்ற விடாமுயற்சி கொண்டவர்.",
      "இளமைக் காலத்தில் போராட்டங்களையும் தடைகளையும் சந்தித்தாலும், தனது சுய உழைப்பால் பிற்காலத்தில் மாபெரும் உச்சியை அடைவார்.",
      "மானமரியாதைக்கு முதலிடம் கொடுப்பவர்; எவரிடமும் வீணாகக் கையேந்தாத சுயசார்பு குணம் உடையவர்.",
      "அமைதியான முகம், சில சமயம் சோர்வான தோற்றம் அல்லது மெலிந்த உடல்வாகு அமைந்திருக்கலாம்; காற்று/வாத தேகம்.",
      "பொறுமையும் விவேகமும் இவரின் மாபெரும் பலமாகும்; காலத்தின் அருமையை உணர்ந்து காரியம் சாதிப்பார்."
    ],
    "core_traits_en": [
      "Profound gravity, mature wisdom, stoic endurance, and unyielding perseverance.",
      "Encounters early hardships and uphill struggles, yet ascends steadily through self-exertion to peak worldly eminence.",
      "Fiercely guarded self-respect and integrity; refuses unearned charity or degrading compromises.",
      "Lean, spare physique with contemplative, serious eyes; melancholic or vata-dominated constitution.",
      "Supreme patience and discipline are his greatest weapons; triumphs through the inexorable compound power of time."
    ],
    "strong_placement_ta": [
      "துலாத்தில் உச்சம் அல்லது மகரம்/கும்பத்தில் ஆட்சி பெற்று சச யோகம் (Sasa Yoga) அமைந்தால்: லட்சக்கணக்கான உழைப்பாளர்களை வழிநடத்தும் மக்கள் தலைவர், தொழில் அதிபர்.",
      "நீண்ட ஆயுள், பரந்த நிலபுலன்கள், சுரங்கங்கள் மற்றும் சமுதாயத்தில் அழியாத செல்வாக்கு கிட்டும்."
    ],
    "strong_placement_en": [
      "Exalted in Libra or in own signs Capricorn/Aquarius forming Sasa Mahapurusha Yoga: Legendary mass leader of the working class, industrial baron.",
      "Exceptional longevity, vast landed estates, mining concessions, and enduring civic authority."
    ],
    "weak_placement_ta": [
      "மேஷத்தில் நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: மந்த நிலை, சோம்பல், மூட்டு வலி மற்றும் நரம்புத் தளர்ச்சி.",
      "காரணமற்ற அவநம்பிக்கை, தனிமை பயம் மற்றும் முயற்சிகளில் தொடர்ந்து தடைகள் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated in Aries or afflicted: Chronic lethargy, articular rheumatism, spinal curvature, and melancholy.",
      "Persistent self-doubt, morbidity, social withdrawal, and frustrating career bottlenecks."
    ],
    "career_wealth_ta": [
      "தொழிலாளர் நலத்துறை, சுரங்கத் தொழில், இரும்பு மற்றும் எஃகு உற்பத்தி, நீதித்துறை, தொல்பொருள் ஆராய்ச்சி, விவசாயம்.",
      "சொந்த உழைப்பாலும் கடினமான பணிகளாலும் நிலையான, நீண்ட காலச் சொத்துகள் சேரும்."
    ],
    "career_wealth_en": [
      "Thrives in labor union leadership, mining exploration, metallurgy, criminal judiciary, archaeology, and heavy civil construction.",
      "Builds indestructible long-term capital assets through disciplined sweat and patient compounding."
    ],
    "health_precautions_ta": [
      "மூட்டு வலி, வாதக் கோளாறுகள் (Arthritis), எலும்பு பலவீனம், மலச்சிக்கல் மற்றும் தோல் வறட்சி.",
      "எண்ணெய் தேய்த்துக் குளிப்பதும், உடற்பயிற்சியும், சூடான புதிய உணவுகளை உண்பதும் வாதத்தைத் தணிக்கும்."
    ],
    "health_precautions_en": [
      "Prone to rheumatoid arthritis, bone density loss, chronic constipation, and dry eczema.",
      "Weekly warm sesame oil self-massages, mobility drills, and warm grounding meals subdue vata."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 53) & Saravali Ch. 30"
  },
  {
    "planet": "Saturn",
    "planet_name_ta": "சனி",
    "symbol": "🪐",
    "element": "காற்று (Vayu)",
    "house": 2,
    "bhava_category": "panaphara",
    "house_title_ta": "2-ஆம் பாவம் - தன பாவம் (சிக்கனம், உழைப்பால் தனம் & நிதான வாக்கு)",
    "house_title_en": "2nd House - Dhana Bhava (Frugality, Self-Earned Riches & Measured Speech)",
    "core_traits_ta": [
      "பேச்சில் நிதானம், ஆழ்ந்த அர்த்தம் மற்றும் குறைத்துப் பேசும் சுபாவம்; வீண் பேச்சுகளைத் தவிர்ப்பார்.",
      "பணத்தின் அருமையை உணர்ந்து சிக்கனமாகச் செலவு செய்வார்; ஒரு காசையும் வீணாக்க மாட்டார்.",
      "குடும்பத்தில் பொறுப்புமிக்க மனிதராக இருந்து அனைவருக்கும் வழிகாட்டுவார்.",
      "நிலம், பழைய பொருட்கள், இரும்பு மற்றும் பூமி சார்ந்த தொழில்களில் தன லாபம் ஈட்டுவார்."
    ],
    "core_traits_en": [
      "Measured, deliberate, and laconic speech; prefers meaningful silence over superficial chatter.",
      "Acute financial discipline and frugality; abhors wasteful indulgence and safeguards every penny.",
      "Acts as the responsible, dependable pillar of the family through trials.",
      "Innate commercial instincts for scrap recycling, heavy hardware, commodities, and agricultural lands."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: பல நூறு கோடி மதிப்பிலான நிலங்கள், இரும்பு ஆலைகள், பரம்பரைச் சொத்துகள் குவியும்.",
      "அரசாங்கத் கருவூலங்கள் மற்றும் நிதி நிறுவனங்களில் உயர் பொறுப்புகள் வகித்து நற்பெயர் பெறுவார்."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Bestows colossal real estate holdings, steel foundries, and robust generational liquidity.",
      "Entrusted with sovereign treasuries and premier fiscal directorships."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: கடுமையான பேச்சு, குடும்பத்தில் விரிசல், பண நெருக்கடிகள்.",
      "வலது கண்ணில் பார்வைக் குறைபாடு அல்லது பற்களில் சொத்தை வரலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Harsh, biting speech causing broken family ties; protracted financial insolvency.",
      "Prone to right-eye cataracts, periodontal degeneration, and severe dental cavities."
    ],
    "career_wealth_ta": [
      "பழைய இரும்பு வர்த்தகம், நிலக்கரி, பெட்ரோலியம், கனரக வாகன உதிரிபாகங்கள், தோல் தொழில், தணிக்கை.",
      "விடாமுயற்சியாலும் சிறுகச் சிறுகச் சேமிப்பதாலும் பெருஞ்செல்வந்தராக உயருவார்."
    ],
    "career_wealth_en": [
      "High returns in metal scrap recycling, coal/oil extraction, heavy equipment salvage, and forensic auditing.",
      "Rises to profound wealth through patient compounding and frugal asset conservation."
    ],
    "health_precautions_ta": [
      "பல் வலி, ஈறுகளில் ரத்தம் வடிதல், தொண்டை வறட்சி, வலது கண் பார்வை மங்குதல் மற்றும் முகத்தில் கரும் புள்ளிகள்.",
      "பல் ஆரோக்கியத்தையும், கண்களுக்கான வைட்டமின் உணவுகளையும் தவறாமல் எடுத்துக்கொள்ள வேண்டும்."
    ],
    "health_precautions_en": [
      "Susceptible to periodontal disease, vocal dryness, right-eye optic strain, and facial blemishes.",
      "Routine dental checkups and ocular vitamin A & lutein supplementation are essential."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 101) & Saravali Ch. 30"
  },
  {
    "planet": "Saturn",
    "planet_name_ta": "சனி",
    "symbol": "🪐",
    "element": "காற்று (Vayu)",
    "house": 3,
    "bhava_category": "upachaya",
    "house_title_ta": "3-ஆம் பாவம் - சகஜ பாவம் (அசைக்க முடியாத வீரம் & வெற்றி)",
    "house_title_en": "3rd House - Sahaja Bhava (Invincible Fortitude & Upachaya Triumph)",
    "core_traits_ta": [
      "சனி 3-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமர்வது ஜாதகருக்கு இமாலய பலத்தையும், தளராத மன உறுதியையும் தரும் சிறந்த யோகமாகும்.",
      "எந்தவிதமான சோதனைகளையும் துணிவுடன் தாங்கி வெல்லும் ஆற்றல்; எதிரிகளைத் தன் அமைதியாலும் வியூகத்தாலும் வீழ்த்துவார்.",
      "செயல்வீரர்; வார்த்தைகளை விட தன் கடுமையான உழைப்பால் வெற்றிகளை நிரூபித்துக் காட்டுவார்.",
      "இளைய சகோதரர்களிடம் சற்று கண்டிப்பு காட்டினாலும் அவர்களுக்கு அரணாக நிற்பார்."
    ],
    "core_traits_en": [
      "Saturn in the 3rd (an Upachaya house) is classically venerated as a formidable engine of heroic resilience and steady victory.",
      "Possesses titanic endurance to absorb life's shocks; outmaneuvers adversaries through strategic patience.",
      "Man of solid action rather than boastful words; proves worth through undeniable accomplishments.",
      "Demanding yet fiercely protective guardian to younger siblings."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: நாடெங்கும் புகழ், ராணுவம்/காவல்துறையில் மிக உயரிய தலைமை, மாபெரும் சாதனைகள்.",
      "எடுத்த முயற்சிகள் யாவும் தாமதமானாலும் அசுர வெற்றியடைந்து சரித்திரத்தில் இடம்பிடிக்கும்."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Confers far-reaching fame, top command in police or armed forces, and heroic stature.",
      "All ventures culminate in monumental success; builds an enduring legacy of gritty triumph."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: சகோதரர்களுடன் நிலத்தகராறு, கைகளில் நரம்பு வலி.",
      "காரணமற்ற பயமும் தயக்கமும் முயற்சிகளில் சுணக்கத்தை ஏற்படுத்தலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Acrimonious sibling disputes over inheritances, upper arm numbness, and chronic fatigue.",
      "Paralyzing indecision and pessimistic hesitation sabotaging key commercial openings."
    ],
    "career_wealth_ta": [
      "காவல்துறை, ராணுவ தளவாடங்கள், போக்குவரத்து கழகங்கள், ரயில்வே, அச்சு மற்றும் கூரியர் தொழில், விளையாட்டு.",
      "கடின உழைப்பாலும் மூலோபாய திட்டங்களாலும் கோடிக்கணக்கில் சொத்துக்கள் சேரும்."
    ],
    "career_wealth_en": [
      "Superlative success in policing, defense logistics, railway syndicates, courier networks, and athletics.",
      "Amasses substantial capital through strategic resilience and industrial transport contracts."
    ],
    "health_precautions_ta": [
      "தோள்பட்டை வலி, கைகளில் நரம்புத் தளர்ச்சி, காது கேளாமை மற்றும் எலும்பு முறிவுகள்.",
      "முறையான கைகளுக்கான உடற்பயிற்சிகளும், எலும்புகளுக்கு கால்சியம் சத்தும் மிகவும் அவசியம்."
    ],
    "health_precautions_en": [
      "Prone to shoulder frozen syndrome, brachial neuralgia, auditory nerve dullness, and bone fractures.",
      "Upper body mobility routines and dietary calcium-vitamin D3 optimization maintain structural strength."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 141) & Saravali Ch. 30"
  },
  {
    "planet": "Saturn",
    "planet_name_ta": "சனி",
    "symbol": "🪐",
    "element": "காற்று (Vayu)",
    "house": 4,
    "bhava_category": "kendra",
    "house_title_ta": "4-ஆம் பாவம் - சுக பாவம் (சச யோகம் / பூமி லாபம், பழைய சொத்துகள் & ஆழமான அமைதி)",
    "house_title_en": "4th House - Sukha Bhava (Sasa Yoga / Landed Acquisitions & Deep Contemplation)",
    "core_traits_ta": [
      "பழமையான வீடுகள், பாரம்பரிய நிலங்கள், தோட்டங்கள் மற்றும் விவசாயப் பண்ணைகளை வாங்குவதில் ஆர்வம்.",
      "வீட்டிலும் குடும்பத்திலும் ஒழுக்கமும் கட்டுப்பாடும் நிலவ வேண்டும் என கண்டிப்பாக இருப்பார்.",
      "மனதில் ஆழ்ந்த அமைதியும் தத்துவ சிந்தனைகளும் இருக்கும்; சில சமயம் காரணமற்ற தனிமை உணர்வு எட்டிப்பார்க்கும்.",
      "தாயாரின் நலனில் மிகுந்த அக்கறை காட்ட வேண்டும்; தாய்வழியில் பக்குவமும் ஆசியும் கிட்டும்."
    ],
    "core_traits_en": [
      "Passion for acquiring ancient heritage properties, agricultural acreage, sprawling orchards, and rustic estates.",
      "Enforces strict Spartan discipline and order within the domestic household.",
      "Possesses a deeply contemplative, philosophical inner life, punctuated by periodic monastic solitude.",
      "Requires attentive care for mother's health; absorbs profound maternal stoicism and wisdom."
    ],
    "strong_placement_ta": [
      "துலாத்தில் உச்சம் அல்லது சொந்த வீட்டில் சச யோகம் அமைந்தால்: பல ஏக்கர் நிலங்கள், பண்ணை மாளிகைகள், கௌரவப் பதவிகள்.",
      "அரசாங்கத்தால் சகல மரியாதைகளும் வழங்கப்பட்டு, விவசாயம் மற்றும் சுரங்கத் துறையில் பெரும் செல்வந்தராக வாழ்வார்."
    ],
    "strong_placement_en": [
      "Exalted in Libra or own signs forming Sasa Yoga: Vast acreage of prime lands, rustic country palaces, and civic honors.",
      "Amasses profound wealth in agrarian conglomerates and mineral extraction."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தாயாரின் வாதக் கோளாறுகள், பூர்வீக சொத்துகளில் இழப்பு, வீட்டு விபத்துகள்.",
      "வாகனங்களால் செலவுகளும், பூர்வீக வீட்டை விட்டுப் பிரியும் சூழ்நிலையும் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated in Aries or afflicted: Maternal rheumatoid ailments, loss of ancestral manor to debts, and vehicular accidents.",
      "Chronic domestic gloom, dilapidated home conditions, and forced relocation."
    ],
    "career_wealth_ta": [
      "விவசாயப் பண்ணைகள், சுரங்கத் தொழில், நிலக்கரி, செங்கல் சூளைகள், பழைய வாகன வர்த்தகம், ரியல் எஸ்டேட்.",
      "பூமி பரிவர்த்தனைகளாலும் விவசாயத்தாலும் தலைமுறைக்கு நிலைக்கும் சொத்துகள் சேரும்."
    ],
    "career_wealth_en": [
      "Thrives in commercial farming, quarrying, coal energy, brick kilns, salvage automotive yards, and realty.",
      "Builds immense generational equity anchored in tangible land parcels."
    ],
    "health_precautions_ta": [
      "நெஞ்சு சளி, இருதய பலவீனம், ஆஸ்துமா, மூட்டு வலி மற்றும் மன அழுத்தம்.",
      "சூடான மூலிகைக் குடிநீரும், பிராணாயாமப் பயிற்சிகளும் நுரையீரல் நலனைக் காக்கும்."
    ],
    "health_precautions_en": [
      "Susceptible to bronchial asthma, coronary sclerosis, articular stiffness, and melancholic depression.",
      "Warm herbal decoctions, breathwork pranayama, and avoiding damp basements preserve vigor."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 176) & Saravali Ch. 30"
  },
  {
    "planet": "Saturn",
    "planet_name_ta": "சனி",
    "symbol": "🪐",
    "element": "காற்று (Vayu)",
    "house": 5,
    "bhava_category": "trikona",
    "house_title_ta": "5-ஆம் பாவம் - புத்திர பாவம் (ஆழ்ந்த ஆராய்ச்சி / தத்துவ புத்தி & பிற்கால யோகம்)",
    "house_title_en": "5th House - Putra Bhava (Deep Analytical Intellect & Eventual Progeny Triumph)",
    "core_traits_ta": [
      "ஆழ்ந்த சிந்தனை, ஆராய்ச்சி மனப்பான்மை, வரலாற்றுப் பற்று மற்றும் எதையும் எளிதில் நம்பாத விவேகமான புத்தி.",
      "புத்திர பாக்கியம் சற்று காலதாமதமாக அமைந்தாலும், பிற்காலத்தில் குழந்தைகள் பெரும் சாதனையாளர்களாகத் திகழ்வார்கள்.",
      "பூர்வ புண்ணியத்தில் ஆரம்பத்தில் சோதனைகள் இருந்தாலும், 36 வயதுக்குப் பிறகு அசைக்க முடியாத யோகம் செயல்படும்.",
      "பங்குச் சந்தை போன்ற சூதாட்டங்களைத் தவிர்த்து, நீண்ட கால நிலையான முதலீடுகளில் மட்டுமே ஈடுபடுவார்."
    ],
    "core_traits_en": [
      "Profound analytical intellect, deep historical interest, scientific skepticism, and rigorous logical discipline.",
      "Childbearing may experience delays, yet progeny mature into exceptionally responsible, accomplished pillars of society.",
      "Past-life karma demands early trials, unlocking magnificent unshakeable fortune after age 36.",
      "Shuns speculative day-trading, anchoring wealth exclusively in disciplined long-term compounding."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: உலகப் புகழ் பெற்ற தத்துவ அறிஞர், விஞ்ஞானி, பிற்காலத்தில் மாபெரும் கோடீஸ்வர யோகம்.",
      "குழந்தைகள் உயர் அரசுப் பதவிகளை அடைவார்கள்; குடும்பத்திற்கு அழியாத புகழையும் பெருமையையும் சேர்ப்பார்கள்."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Renowned scientific philosopher, master investigator, and multi-millionaire through patient compounding.",
      "Progeny attain apex judicial or administrative ranks, elevating lineage honors."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: புத்திர பாக்கியத்தில் கடும் தடைகள், பிள்ளைகளுடன் கருத்து மோதல்கள்.",
      "தவறான நிதித் திட்டங்களால் சேமிப்பு விரயமாதல் மற்றும் மன அமைதியின்மை."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Severe delay or heartache regarding children; ideological alienation from firstborn.",
      "Heavy financial erosion from rigid, outdated investment schemes."
    ],
    "career_wealth_ta": [
      "ஆராய்ச்சி விஞ்ஞானி, வரலாற்றுப் பேராசிரியர், தத்துவ ஆசிரியர், நில அளவையாளர், சுரங்கப் பொறியாளர், தொல்பொருள் துறை.",
      "நீண்ட கால முதலீடுகளாலும் அறிவுசார் ஆய்வுகளாலும் கோடிக்கணக்கில் சொத்துக்கள் சேரும்."
    ],
    "career_wealth_en": [
      "Distinction as research scientist, history dean, philosopher, geodesic surveyor, petroleum engineer, and archaeologist.",
      "Vast capital accumulated via long-horizon equity value-investing and research grants."
    ],
    "health_precautions_ta": [
      "அஜீரணம், மலச்சிக்கல், குடல் வாதம், கல்லீரல் மந்தம் மற்றும் மன அழுத்தம்.",
      "நார்ச்சத்து மிகுந்த உணவுகளையும், வெதுவெதுப்பான நீரையும் அருந்துவது செரிமானத்திற்கு உதவும்."
    ],
    "health_precautions_en": [
      "Prone to sluggish peristalsis, chronic constipation, irritable bowel spasms, and hepatic torpor.",
      "High-fiber dietary intake, abundant warm water, and physical movement keep gut healthy."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 221) & Saravali Ch. 30"
  },
  {
    "planet": "Saturn",
    "planet_name_ta": "சனி",
    "symbol": "🪐",
    "element": "காற்று (Vayu)",
    "house": 6,
    "bhava_category": "dusthana",
    "house_title_ta": "6-ஆம் பாவம் - சத்ரு பாவம் (அசைக்க முடியாத சத்ரு ஜெயம் / மகா உபசய யோகம்)",
    "house_title_en": "6th House - Satru Bhava (Unassailable Conquest of Enemies & Grand Upachaya Power)",
    "core_traits_ta": [
      "சனி 6-ஆம் பாவத்தில் அமைவது ஜாதகத்திற்கு மாபெரும் கவசமாகும்; எதிரிகள் தானாகவே அடிபணிவர்.",
      "எந்தவிதமான வழக்குகள், போட்டிகள் மற்றும் கடன் தொல்லைகளையும் தன் விடாமுயற்சியால் அடியோடு தீர்த்து வைப்பார்.",
      "இரும்பு போன்ற நோய் எதிர்ப்புச் சக்தி; கடுமையான உழைப்பையும் தாங்கும் திடகாத்திரமான உடல்வாகு.",
      "பணியாளர்களையும் தொழிலாளர்களையும் அன்பாலும் ஒழுக்கத்தாலும் தன் கட்டுப்பாட்டில் வைத்திருப்பார்."
    ],
    "core_traits_en": [
      "Saturn in the 6th is classically celebrated as an invincible fortress; crushes all adversaries and hostility.",
      "Eliminates litigations, legal disputes, and financial debts through relentless, unyielding stamina.",
      "Possesses iron physical stamina, supreme immune resilience, and boundless work capacity.",
      "Commands total loyalty and high productivity from manual laborers and subordinates."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: சத்ரு சம்ஹார யோகம்! எதிரிகள் இல்லா பெருவாழ்வு, நீதித்துறை/தொழிலாளர் நலத்துறையில் சர்வாதிகார அதிகாரம்.",
      "அளப்பரிய செல்வம், கடன் இல்லாத வாழ்க்கை மற்றும் போட்டிகளில் தொடர் வெற்றிகள் குவியும்."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Bestows complete Shatru Samhara Yoga! Total eradication of foes, supreme judicial/labor command.",
      "Immense accumulated wealth, unassailable physical vitality, and perpetual competitive victories."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தீராத வாத நோய்கள், மூட்டு வலி, கடன் சுமைகளால் மன உளைச்சல்.",
      "வேலையாட்களால் வழக்குகள், திருட்டு அல்லது தாய்மாமனுடன் கடுமையான விரோதம் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated in Aries or afflicted: Chronic rheumatologic disorders, gout, and anxiety over unpaid liabilities.",
      "Troublesome labor strikes, employee embezzlement, and bitter feuds with maternal uncles."
    ],
    "career_wealth_ta": [
      "தொழிலாளர் தீர்ப்பாயம், குற்றவியல் சட்டம், சுரங்க நிர்வாகம், கனரக இயந்திர பராமரிப்பு, பொது சுகாதாரம், சிறைத்துறை.",
      "போட்டிகளையும் சவால்களையும் தனக்குச் சாதகமாக மாற்றி கோடிக்கணக்கில் வருவாய் ஈட்டுவார்."
    ],
    "career_wealth_en": [
      "Dominates in labor tribunal arbitration, criminal trial law, mining logistics, correctional administration, and sanitation.",
      "Extracts substantial financial wealth directly from crisis management and competitive victories."
    ],
    "health_precautions_ta": [
      "மூட்டு வலி (Rheumatism), இடுப்பு வாதம், குடல் புண்கள், ஆசனவாய் வெடிப்பு மற்றும் தோல் நோய்கள்.",
      "உடலில் வாதத்தைக் குறைக்கும் எளிய சமைத்த உணவுகளும், வெந்நீர் ஒத்தடமும் நலம் தரும்."
    ],
    "health_precautions_en": [
      "Vulnerable to articular rheumatism, lumbar sciatica, peptic ulcers, anal fissures, and eczema.",
      "Adopt an anti-inflammatory vata-pacifying diet, warm baths, and avoid cold drafts."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 262) & Saravali Ch. 30"
  },
  {
    "planet": "Saturn",
    "planet_name_ta": "சனி",
    "symbol": "🪐",
    "element": "காற்று (Vayu)",
    "house": 7,
    "bhava_category": "kendra",
    "house_title_ta": "7-ஆம் பாவம் - களத்திர பாவம் (சச யோகம் / பக்குவமான துணை & காலதாமத திருமணம்)",
    "house_title_en": "7th House - Kalathra Bhava (Sasa Yoga / Mature Spouse & Delayed Nuptials)",
    "core_traits_ta": [
      "சனி 7-ஆம் பாவத்தில் திக்பலம் (Digbala) பெற்று சச யோகத்தை (Sasa Yoga) உருவாக்குகிறார்.",
      "திருமணம் சற்று காலதாமதமாக அமைவது நல்லது; வாழ்க்கைத் துணை மிகுந்த பக்குவமும், பொறுப்பும், அடக்கமும் கொண்டவராக இருப்பார்.",
      "வாழ்க்கைத் துணையுடன் நிலையான, பிரிக்க முடியாத ஆழமான பந்தம் இருக்கும்; விட்டுக் கொடுத்துச் செல்வது அமைதி தரும்.",
      "கூட்டு வர்த்தகத்தில் நேர்மையும், நம்பகத்தன்மையும் கொண்டவர்களுடன் மட்டுமே ஒப்பந்தம் செய்து சாதிப்பார்."
    ],
    "core_traits_en": [
      "Saturn attains supreme Digbala (directional potency) in the 7th, generating the prestigious Sasa Mahapurusha Yoga.",
      "Marriage is typically solemnized later in life; spouse is mature, highly responsible, prudent, and stoic.",
      "Marital bond is cemented by enduring loyalty and shared duties rather than fleeting frivolity.",
      "Conducts commercial partnerships exclusively with seasoned, trustworthy, and battle-tested veterans."
    ],
    "strong_placement_ta": [
      "துலாத்தில் உச்சம் அல்லது மகரம்/கும்பத்தில் ஆட்சி பெற்று சச யோகம் அமைந்தால்: நாட்டின் முன்னணி தொழில் சாம்ராஜ்ய அதிபர், பன்னாட்டு ஒப்பந்தங்கள்.",
      "வாழ்க்கைத் துணையால் மாபெரும் சொத்துகளும் கௌரவங்களும் வந்து சேரும்; இல்லறத்தில் பூரண அமைதி நிலவும்."
    ],
    "strong_placement_en": [
      "Exalted in Libra or own signs with Sasa Yoga: Industrial titan, commands multinational syndicates and supreme civic prestige.",
      "Spouse brings vast ancestral estates and stability; union is universally respected for steadfast dignity."
    ],
    "weak_placement_ta": [
      "மேஷத்தில் நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: திருமண வாழ்வில் கடுமையான விரிசல், துணையின் ஆரோக்கியம் பாதித்தல்.",
      "கூட்டுத் தொழிலில் பார்ட்னர்களால் ஏமாற்றப்பட்டு பெரும் நிதி இழப்புகள் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated in Aries or afflicted: Cold, acrimonious marital friction; spouse suffers from chronic rheumatologic ailments.",
      "Heavy financial loss through unscrupulous business partners and protracted arbitration."
    ],
    "career_wealth_ta": [
      "சர்வதேச வர்த்தகம், கனரக இயந்திர ஏற்றுமதி, தொழிலாளர் சங்கம், சட்ட ஒப்பந்தங்கள், ரியல் எஸ்டேட் கூட்டாண்மை.",
      "வாழ்க்கைத் துணையின் ஆலோசனைகளாலும் விடாமுயற்சியாலும் கோடிக்கணக்கில் சொத்துக்கள் சேரும்."
    ],
    "career_wealth_en": [
      "Thrives in international mineral export, heavy hardware trade, collective bargaining mediation, and commercial realty.",
      "Substantial capital accumulation achieved through joint commercial endurance and steady expansion."
    ],
    "health_precautions_ta": [
      "சிறுநீரகக் கற்கள், வாதக் கோளாறுகள், அடிவயிற்றில் வலி மற்றும் பாலியல் பலவீனம்.",
      "முறையான குடிநீர் அருந்துதலும், உடலை சூடாக வைத்திருப்பதும் ஆரோக்கியத்திற்கு உதவும்."
    ],
    "health_precautions_en": [
      "Susceptible to renal calculi, pelvic sciatica, chronic urinary sluggishness, and reproductive fatigue.",
      "Ample warm hydration, keeping lumbar region warm, and periodic urological screenings."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Saturn",
    "planet_name_ta": "சனி",
    "symbol": "🪐",
    "element": "காற்று (Vayu)",
    "house": 8,
    "bhava_category": "dusthana",
    "house_title_ta": "8-ஆம் பாவம் - ஆயுள் பாவம் (பூரண தீர்க்காயுள் / ஆயுள்காரகன் அஷ்டமத்தில் அமர்தல்)",
    "house_title_en": "8th House - Ayur Bhava (Impregnable Longevity / Ayushkaraka in 8th)",
    "core_traits_ta": [
      "ஆயுள்காரகனான சனி 8-ஆம் பாவத்தில் அமர்வது ஜாதகருக்கு இரும்பு போன்ற பூரண தீர்க்காயுளை (85+ வயது) வழங்கும் மகா அமைப்பாகும்.",
      "எந்தவிதமான விபத்துகள், ஆபத்துகள் மற்றும் கொடிய நோய்களிலிருந்தும் தப்பித்து நீண்ட காலம் வாழும் யோகம் உண்டு.",
      "வாழ்க்கையில் பல ஏற்ற இறக்கங்களையும், சோதனைகளையும் தாண்டி முதிர்ந்த ஞானமும் பக்குவமும் அடைவார்.",
      "மனைவி வழியில் பழைய நிலங்கள், உயில் சொத்துகள் மற்றும் காப்பீடுகள் தாமதமாக வந்து சேரும்."
    ],
    "core_traits_en": [
      "Ayushkaraka Saturn in the 8th is classically celebrated as the supreme guarantor of monumental longevity (85+ years).",
      "Miraculously survives fatal catastrophes, acute epidemics, and dangerous accidents unscathed.",
      "Weathers dramatic life tempests with unshakeable stoicism, evolving into a revered elder sage.",
      "Eventually inherits ancient landholdings, insurance payouts, and testamentary bequests through marriage."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: சதாபிஷேகம் கண்டு நூற்றாண்டு வாழும் யோகம், பல்லாயிரம் கோடி உயில் சொத்துகள், ஆன்மீக முக்தி.",
      "எதிர்பாராத தன வரவுகள் வந்து சேரும்; சமுதாயத்தில் மூத்த வழிகாட்டியாகத் திகழ்வார்."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Bestows Centenarian longevity, vast testamentary ancestral properties, and serene Moksha.",
      "Revered as an unshakeable patriarch; commands universal veneration across generations."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தீராத வாத நோய்கள், பக்கவாதம், கண் பார்வை மங்குதல், ஏழ்மை.",
      "உயில் விவகாரங்களில் வழக்குகளும், அரசாங்க அபராதங்களால் மன உளைச்சலும் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Chronic paralysis, osteoarthritis, severe visual degeneration, and financial distress.",
      "Protracted court litigations over disputed wills and crippling probate penalties."
    ],
    "career_wealth_ta": [
      "ஆயுள் காப்பீட்டுத் தலைவர், தொல்பொருள் ஆராய்ச்சி, நிலக்கரி மற்றும் கனிம வளங்கள், மரண சான்றிதழ் நிர்வாகம், கழிவு மேலாண்மை.",
      "உயில் சொத்துகள், பழைய முதலீடுகளின் முதிர்வு மற்றும் திடீர் தன வரவால் பெருஞ்செல்வம்."
    ],
    "career_wealth_en": [
      "Distinguished in life insurance underwriting, palaeontology, petroleum extraction, mortuary science, and waste recycling.",
      "Vast windfalls realized from mature pension funds, inherited estates, and mineral leases."
    ],
    "health_precautions_ta": [
      "மூல நோய் (Piles), ஆசனவாய் வெடிப்பு, மூட்டு வாதம், பக்கவாதம் மற்றும் கால் எலும்பு முறிவு.",
      "நார்ச்சத்து மிகுந்த உணவுகளையும், எண்ணெய் மசாஜ்களையும் தவறாமல் எடுத்துக்கொள்ள வேண்டும்."
    ],
    "health_precautions_en": [
      "Vulnerable to chronic hemorrhoids, anal fissures, severe rheumatoid arthritis, and femoral neck fractures.",
      "High-fiber diet, routine warm oil therapeutic massages, and falls-prevention care in old age."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Saturn",
    "planet_name_ta": "சனி",
    "symbol": "🪐",
    "element": "காற்று (Vayu)",
    "house": 9,
    "bhava_category": "trikona",
    "house_title_ta": "9-ஆம் பாவம் - பாக்கிய பாவம் (தர்ம நீதி, பிற்கால பாக்கியம் & தத்துவ ஞானம்)",
    "house_title_en": "9th House - Bhagya Bhava (Righteous Morality, Delayed Fortune & Philosophical Depth)",
    "core_traits_ta": [
      "ஆழ்ந்த தர்ம சிந்தனை, நேர்மை, வேதாந்த தத்துவங்களில் பற்று மற்றும் உழைப்பையே தெய்வமாக மதிக்கும் சுபாவம்.",
      "தந்தையுடன் ஆரம்பத்தில் கருத்து வேறுபாடுகள் இருந்தாலும், பிற்காலத்தில் தந்தையின் பெருமையைக் காப்பார்.",
      "வாழ்க்கையின் பிற்பகுதியில் (36 வயதுக்கு மேல்) பாக்கியங்கள் பூரணமாகச் செயல்பட்டு பெரும் செல்வந்தராக மாற்றுவார்.",
      "பழமையான புண்ணியத் தலங்களுக்கும், மலைக் குகைகளுக்கும் சென்று அமைதியான தியானம் செய்வதில் விருப்பம்."
    ],
    "core_traits_en": [
      "Profound ethical conviction, rigorous honesty, devotion to Vedanta, and regards hard honest toil as sacred worship.",
      "Initial ideological distance from father dissolves into deep filial reverence and preservation of family heritage.",
      "Fortune compounds steadily, manifesting monumental prosperity and universal acclaim after age 36.",
      "Drawn to ancient stone shrines, remote Himalayan hermitages, and austere meditative disciplines."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: அகண்ட தர்ம யோகம், உச்ச நீதிமன்றத் தலைமை நீதிபதி, சர்வதேச தத்துவ மேதை.",
      "அறக்கட்டளைகளை நிறுவி பல்லாயிரக்கணக்கான ஏழை எளியவர்களுக்கு வாழ்வளிக்கும் மகா வள்ளலாகத் திகழ்வார்."
    ],
    "strong_placement_en": [
      "Exalted or own house: Supreme Dharma Yoga! Appellate chief justice, globally acclaimed constitutional jurist.",
      "Establishes monumental philanthropic foundations, uplifting countless destitute lives with dignity."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தந்தையின் உடல்நலம் பாதித்தல், மத சடங்குகளில் வெறுப்பு.",
      "வெளிநாட்டுப் பயணங்களில் தடைகள் மற்றும் தர்ம காரியங்களில் வீண் அவப்பெயர்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Severe paternal health reversals, bitter cynicism towards religion, and travel delays.",
      "Misappropriation of trust funds by relatives causing unmerited scandal."
    ],
    "career_wealth_ta": [
      "நீதிபதி, வழக்கறிஞர், தத்துவப் பேராசிரியர், தொண்டு நிறுவனத் தலைவர், சுரங்க ஏற்றுமதி, சர்வதேச வர்த்தகம்.",
      "நேர்மையான தர்ம வழியிலும், பழைய சொத்துகளாலும் கோடிக்கணக்கில் வற்றாத தன சேர்க்கை."
    ],
    "career_wealth_en": [
      "Exemplary career as constitutional magistrate, jurist, philosophy professor, mineral exporter, and foundation trustee.",
      "Generational wealth accumulated through unblemished professional ethics and prime real estate."
    ],
    "health_precautions_ta": [
      "தொடை எலும்பு வலி, இடுப்பு வாதம் (Sciatica), மூட்டுத் தேய்மானம் மற்றும் கால் வீக்கம்.",
      "முறையான நடைப்பயிற்சியும், வெதுவெதுப்பான எண்ணெய் மசாஜ்களும் மூட்டுகளுக்குப் பலம் தரும்."
    ],
    "health_precautions_en": [
      "Prone to femoral osteoporosis, chronic sciatica, hip joint degeneration, and lower leg edema.",
      "Gentle walking outdoors and regular warm herbal oil joint applications safeguard mobility."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Saturn",
    "planet_name_ta": "சனி",
    "symbol": "🪐",
    "element": "காற்று (Vayu)",
    "house": 10,
    "bhava_category": "kendra",
    "house_title_ta": "10-ஆம் பாவம் - ஜீவன பாவம் (சச யோகம் / சமுதாயத் தலைமை & தொழில் சாம்ராஜ்யம்)",
    "house_title_en": "10th House - Karma Bhava (Sasa Yoga / Mass Leadership & Industrial Hegemony)",
    "core_traits_ta": [
      "சனி 10-ஆம் பாவத்தில் அமர்வது உழைப்பாளர் வர்க்கத்தின் மாபெரும் தலைவராக உயர்த்தும் மிகச் சிறந்த ராஜ யோகமாகும்.",
      "சுய உழைப்பால் அடிமட்டத்திலிருந்து படிப்படியாக முன்னேறி நாட்டின் உச்ச பதவியை அடையும் விடாமுயற்சி.",
      "நேர்மையான நிர்வாகம், இரும்பு போன்ற ஒழுக்கம் மற்றும் பல்லாயிரக்கணக்கான தொழிலாளர்களை வழிநடத்தும் தலைமைப் பண்பு.",
      "அரசாங்க உயர் விருதுகள், கௌரவப் பட்டங்கள் மற்றும் சமுதாயத்தில் அழிக்க முடியாத சரித்திரப் புகழ்."
    ],
    "core_traits_en": [
      "Saturn in the 10th is a legendary hallmark of self-made titans who rise from humble origins to sovereign heights.",
      "Rises step-by-step through grueling industry and indomitable fortitude to apex positions of national statecraft.",
      "Uncompromising administrative integrity, Spartan discipline, and paternal authority over millions of working people.",
      "Garlanded with sovereign decorations, lifelong chairmanships, and timeless historical veneration."
    ],
    "strong_placement_ta": [
      "துலாத்தில் உச்சம் அல்லது மகரம்/கும்பத்தில் ஆட்சி பெற்று சச யோகம் அமைந்தால்: நாட்டின் பிரதமர், தொழிலாளர் நலத்துறை மந்திரி, தொழில் சக்கரவர்த்தி.",
      "நாட்டின் முதன்மை இரும்பு ஆலைகள், சுரங்கங்கள் மற்றும் உள்கட்டமைப்பு சாம்ராஜ்யத்தை வழிநடத்துவார்."
    ],
    "strong_placement_en": [
      "Exalted in Libra or own signs with Sasa Yoga: Prime Minister, Minister of Labor, Titan of heavy national industry.",
      "Chairs monumental state infrastructure conglomerates, steel mills, and mineral resources."
    ],
    "weak_placement_ta": [
      "மேஷத்தில் நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தொழிலில் திடீர் சரிவு, அதிகாரிகளால் தண்டனைகள், பொது வாழ்வில் சறுக்கல்.",
      "வேலையாட்களால் வேலைநிறுத்தங்களும், தொழிலில் பெரும் நஷ்டமும் ஏற்பட வாய்ப்புண்டு."
    ],
    "weak_placement_en": [
      "Debilitated in Aries or afflicted: Catastrophic political fall, penal sanctions from regulators, and sudden public disgrace.",
      "Calamitous labor strikes, industrial sabotage, and severe commercial insolvency."
    ],
    "career_wealth_ta": [
      "அரசியல் தலைவர், பொது நிர்வாகம், இரும்பு மற்றும் எஃகு உற்பத்தி, சுரங்கத் துறை, ரயில்வே, உள்கட்டமைப்பு பொறியியல்.",
      "அரசாங்க கௌரவப் பதவிகளாலும் தொழில் ஆளுமையாலும் பல நூறு கோடி செல்வம் குவியும்."
    ],
    "career_wealth_en": [
      "Dominant in political governance, public sector administration, metallurgical manufacturing, railways, and civil infrastructure.",
      "Accumulates multi-million dollar equity holdings through transformative industrial leadership."
    ],
    "health_precautions_ta": [
      "பணிச்சுமையால் மூட்டு வலி, ரத்த அழுத்தம், தூக்கமின்மை மற்றும் வாதக் கோளாறுகள்.",
      "வேலைக்கு நடுவே ஓய்வும், தியானப் பயிற்சிகளும் மிகவும் அவசியம்."
    ],
    "health_precautions_en": [
      "Occupational physical exhaustion, severe knee osteoarthritis, hypertension, and insomnia.",
      "Strict pacing of executive workload, daily meditation, and restorative orthopedic care."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Saturn",
    "planet_name_ta": "சனி",
    "symbol": "🪐",
    "element": "காற்று (Vayu)",
    "house": 11,
    "bhava_category": "upachaya",
    "house_title_ta": "11-ஆம் பாவம் - லாப பாவம் (அகண்ட நில லாபம் / குபேர யோகம் & வற்றாத தன வரவு)",
    "house_title_en": "11th House - Labha Bhava (Massive Landed Wealth, Compounding Fortune & Wish Fulfillment)",
    "core_traits_ta": [
      "சனி 11-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமர்வது ஜாதகருக்கு கோடி கோடியாய் குவியும் தன யோகத்தையும், நீடித்த செல்வத்தையும் தரும்.",
      "வயது ஏற ஏற வருமானமும், சொத்துகளின் மதிப்பும் பல மடங்கு உயர்ந்து கொண்டே போகும்.",
      "செல்வாக்கு மிக்க தொழிலதிபர்கள், அரசியல்வாதிகள் மற்றும் முதியோர்களின் உயர்ந்த நட்பு வட்டம்.",
      "மூத்த சகோதரர்களிடம் நல்ல தோழமையும், அவர்களுடன் இணைந்து தொழில் செய்து முன்னேறும் யோகமும் உண்டு."
    ],
    "core_traits_en": [
      "Saturn in the 11th (an Upachaya house) is one of the grandest placements for inexorable, compounding wealth creation.",
      "Financial net worth and real estate valuations escalate exponentially with age, cresting into majestic abundance.",
      "Surrounded by seasoned industrial barons, elder statesmen, and powerful community patriarchs.",
      "Solid, enduring partnership with elder siblings who assist in expanding commercial enterprises."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: எண்ணற்ற நிலங்கள், அடுக்குமாடி கட்டிடங்கள், ஆலைகள், குபேர யோகம்.",
      "அரசாங்க ஒப்பந்தங்கள் மற்றும் கனரகத் தொழில்களில் நாட்டின் முன்னணி பணக்காரராகத் திகழுதல்."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Bestows multi-billion dollar real estate complexes, heavy industrial plants, and supreme Kubera Yoga.",
      "Ranks among the foremost infrastructure magnates commanding prime governmental contracts."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: நண்பர்களால் ஏமாற்றப்பட்டு தன நஷ்டம், மூத்த சகோதரருடன் சொத்துத் தகராறு.",
      "லாபங்கள் கைநழுவுதல் அல்லது பண விரயங்களால் கடன்கள் ஏற்படுதல்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Exploitation by unscrupulous associates, litigious partitions with elder brother.",
      "Delayed cash flows and capital trapped in non-performing assets."
    ],
    "career_wealth_ta": [
      "ரியல் எஸ்டேட் முதலீடுகள், சுரங்க காண்ட்ராக்ட், கனரக போக்குவரத்து, உள்கட்டமைப்பு நிதி, விவசாய நில மேம்பாடு.",
      "முதலீடுகளின் அசுர வளர்ச்சியாலும் சொத்து வாடகைகளாலும் கோடீஸ்வர யோகம்."
    ],
    "career_wealth_en": [
      "Lucrative success in commercial realty syndication, mineral concessions, fleet logistics, and infrastructure private equity.",
      "Immense compounding rental yields and long-term capital gains."
    ],
    "health_precautions_ta": [
      "இடது காது கேளாமை, கணுக்கால் வாதம், தசை இறுக்கம் மற்றும் ரத்த ஓட்டக் குறைபாடுகள்.",
      "கால் நரம்புகளுக்கான உடற்பயிற்சியும், காது ஆரோக்கியத்தைப் பேணுதலும் நல்லது."
    ],
    "health_precautions_en": [
      "Susceptible to left-ear auditory nerve dullness, ankle joint stiffness, and sluggish peripheral circulation.",
      "Daily ankle mobility drills, compression stockings, and regular otic checkups."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Saturn",
    "planet_name_ta": "சனி",
    "symbol": "🪐",
    "element": "காற்று (Vayu)",
    "house": 12,
    "bhava_category": "dusthana",
    "house_title_ta": "12-ஆம் பாவம் - விரய பாவம் (வைராக்கியம் / மோட்ச சாதனை & வெளிநாட்டு வாழ்க்கை)",
    "house_title_en": "12th House - Vraya & Moksha Bhava (Austere Renunciation, Foreign Settlement & Spiritual Release)",
    "core_traits_ta": [
      "உலக மாயைகளிலிருந்து விடுபடும் வைராக்கியம், ஆன்மீக பற்றற்ற நிலை மற்றும் தனிமையை விரும்பும் சுபாவம்.",
      "பிறந்த ஊரை விட வெளிநாடுகளிலோ அல்லது தொலைதூரத் தனிமையான இடங்களிலோ அனுகூலமும் வெற்றியும் கிட்டும்.",
      "பணத்தை ஆடம்பரங்களுக்கு வீணாக்காமல், அனாதை இல்லங்கள், முதியோர் காப்பகங்கள் மற்றும் தொண்டு நிறுவனங்களுக்குச் செலவிடுவார்.",
      "அரசாங்க வரி விவகாரங்களிலும் சட்ட விதிகளிலும் மிகுந்த எச்சரிக்கையுடன் செயல்பட வேண்டும்."
    ],
    "core_traits_en": [
      "Profound ascetic detachment, indifference to worldly superficiality, and deep love of meditative seclusion.",
      "Realizes superior peace of mind, high career standing, and prosperity when residing in foreign lands.",
      "Directs financial resources towards hospices, geriatric care sanitariums, and destitute relief charities.",
      "Must maintain strict compliance in statutory audits and cross-border regulatory reporting."
    ],
    "strong_placement_ta": [
      "துலாத்தில் உச்சம் அல்லது சொந்த வீட்டில் சுப பலத்துடன் இருப்பின்: வெளிநாட்டில் மாபெரும் தொழில் நிறுவனங்கள், சர்வதேச அங்கீகாரம்.",
      "அயன சயன சுகம், அமைதியான ஆத்ம சாந்தி மற்றும் பிறவிப் பெருங்கடலை நீந்தி மோட்சம் அடைதல்."
    ],
    "strong_placement_en": [
      "Exalted in Libra or own signs with benefics: Vast industrial conglomerates headquartered abroad; international acclaim.",
      "Attains peaceful inner serenity, unbroken restorative rest, and transcendent spiritual liberation (Moksha)."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: கடுமையான தூக்கமின்மை, இடது கண் பார்வை மங்குதல், சிறைவாசம் அல்லது அபராதங்கள்.",
      "வீண் மருத்துவச் செலவுகள், ஏமாற்றங்கள் மற்றும் மன உளைச்சலால் அமைதியின்மை."
    ],
    "weak_placement_en": [
      "Debilitated in Aries or afflicted: Chronic severe insomnia, left-eye blindness risk, confinement or legal penalties.",
      "Crushing hospital debts, isolation, and persistent melancholic anxiety."
    ],
    "career_wealth_ta": [
      "சர்வதேச கப்பல் போக்குவரத்து, வெளிநாட்டு கட்டுமான ஒப்பந்தங்கள், சிறைத்துறை நிர்வாகம், முதியோர் இல்லங்கள், ஆன்மீக மடங்கள்.",
      "வெளிநாட்டு நாணயங்களாலும் தூரதேசப் பணிகளாலும் நிலையான தன வரவு."
    ],
    "career_wealth_en": [
      "Flourishes in international maritime freight, overseas civil contracting, correctional governance, and hospice administration.",
      "Substantial foreign currency reserves earned through operations in remote territories."
    ],
    "health_precautions_ta": [
      "இடது கண் பாதிப்பு, பாதங்களில் நரம்பு வலி, தூக்கமின்மை (Insomnia) மற்றும் வாத நோய்கள்.",
      "இரவில் அமைதியான தியானமும், பாதங்களை வெதுவெதுப்பான நீரால் கழுவுதலும் நல்ல தூக்கத்தைத் தரும்."
    ],
    "health_precautions_en": [
      "Prone to left-eye ocular degeneration, severe plantar fasciitis, chronic insomnia, and systemic vata disorders.",
      "Warm foot reflexology baths, calming bedtime rituals, and avoiding late-night digital screens promote rest."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Rahu",
    "planet_name_ta": "ராகு",
    "symbol": "🐉",
    "element": "மாயை / காற்று",
    "house": 1,
    "bhava_category": "kendra",
    "house_title_ta": "1-ஆம் பாவம் - லக்னம் (தீவிர லட்சியம், காந்த ஆளுமை & உலகளாவிய ஆதிக்கம்)",
    "house_title_en": "1st House - Ascendant / Tanu Bhava (Fierce Ambition, Magnetic Persona & Unconventional Rise)",
    "core_traits_ta": [
      "அபாரமான தன்னம்பிக்கை, தீவிரமான லட்சிய வெறி, காந்தக் கவர்ச்சி மற்றும் அனைவரையும் ஈர்க்கும் வசீகர ஆளுமை.",
      "பாரம்பரிய முறைகளை உடைத்து புதிய வழிகளில் சிந்தித்து வெற்றிபெறும் நவீன சிந்தனைப்போக்கு.",
      "சுயமரியாதைக்கு முதலிடம் கொடுப்பவர்; எவருக்கும் எளிதில் அடிபணியாத தன்னாட்சி சுபாவம்.",
      "வெளிநாட்டினர், வேற்று மதத்தினர் மற்றும் பலதரப்பட்ட மக்களுடன் எளிதில் பழகி காரியம் சாதிக்கும் சாமர்த்தியம்.",
      "மனதில் சில சமயம் காரணமற்ற பயமும், அதீத கற்பனைகளும், மாய எண்ணங்களும் எட்டிப்பார்க்கக்கூடும்."
    ],
    "core_traits_en": [
      "Inordinate worldly ambition, magnetic personal presence, and an unconventional trailblazing temperament.",
      "Breaks rigid orthodox taboos, deploying disruptive strategies to conquer contemporary frontiers.",
      "Fiercely protective of self-respect; scorns servitude and demands autonomous leadership.",
      "Effortlessly interacts with foreign cultures, diverse ethnicities, and global networks.",
      "Periodic psychological bouts of unexplained anxiety, vivid phobias, or restless hallucinations."
    ],
    "strong_placement_ta": [
      "ரிஷபம்/மிதுனத்தில் பலம் பெற்று சுப சேர்க்கை அமைந்தால்: உலகப் புகழ் பெற்ற தலைவர், சினிமா சூப்பர் ஸ்டார், பன்னாட்டு தொழில் அதிபர்.",
      "அரசாங்கத்தால் சகல மரியாதைகளும் வழங்கப்பட்டு, உலகளவில் பெரும் செல்வாக்குடன் முடிசூடுவார்."
    ],
    "strong_placement_en": [
      "Exalted in Taurus/Gemini with benefic aspects: Internationally celebrated mass hero, cinema icon, or billionaire tycoon.",
      "Garlanded with state honors, wielding global geopolitical and commercial influence."
    ],
    "weak_placement_ta": [
      "விருச்சிகம்/தனுசில் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: மன பிரமை, போதை பழக்கங்கள், நரம்புத் தளர்ச்சி, தலை காயங்கள்.",
      "தவறான நபர்களின் தொடர்பால் அவப்பெயரும், சமுதாயத்தில் வீண் சர்ச்சைகளும் வரலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Acute paranoia, substance addictions, severe nervous breakdown, and head trauma.",
      "Disrepute through shady associations and explosive public controversies."
    ],
    "career_wealth_ta": [
      "செயற்கை நுண்ணறிவு (AI), சைபர் செக்யூரிட்டி, விண்வெளி ஆராய்ச்சி, சினிமா, அரசியல், பன்னாட்டு ஏற்றுமதி-இறக்குமதி, பங்குச் சந்தை.",
      "துணிச்சலான நவீன முதலீடுகளாலும் பன்னாட்டு வர்த்தகத்தாலும் கோடிக்கணக்கில் வற்றாத தன லாபம்."
    ],
    "career_wealth_en": [
      "Phenomenal success in artificial intelligence, cybersecurity, aerospace, cinema, politics, cross-border import-export, and equities.",
      "Amasses colossal fortunes through disruptive technological patents and foreign currency inflows."
    ],
    "health_precautions_ta": [
      "தலையில் காயங்கள், நரம்பு மண்டல பாதிப்பு, ஒவ்வாமை (Allergies), விஷக்கடி அபாயம் மற்றும் தூக்கமின்மை.",
      "தியானம், பிராணாயாமம் மற்றும் எளிய இயற்கை உணவுகள் மன அமைதியைத் தரும்."
    ],
    "health_precautions_en": [
      "Susceptible to cranial trauma, neurological tremors, sudden systemic allergies, venomous stings, and insomnia.",
      "Daily grounding meditation, breathwork, and clean organic nutrition stabilize the nervous system."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 54) & Saravali Ch. 30"
  },
  {
    "planet": "Rahu",
    "planet_name_ta": "ராகு",
    "symbol": "🐉",
    "element": "மாயை / காற்று",
    "house": 2,
    "bhava_category": "panaphara",
    "house_title_ta": "2-ஆம் பாவம் - தன பாவம் (மந்திர வாக்கு, திடீர் தன வரவு & அந்நிய மொழி ஞானம்)",
    "house_title_en": "2nd House - Dhana Bhava (Mesmerizing Speech, Sudden Windfalls & Polyglot Intellect)",
    "core_traits_ta": [
      "பேச்சில் அசாத்தியமான வசீகரமும், கேட்போரை வசியப்படுத்தும் தந்திரமும் கொண்ட பேச்சாற்றல்.",
      "பல மொழிகளை எளிதில் கற்கும் ஆர்வம்; அந்நிய மொழிகளில் சரளமாகப் பேசும் திறன்.",
      "எதிர்பாராத வழிகளில் திடீரென கோடிக்கணக்கில் தன வரவு வந்து சேரும் அதிர்ஷ்ட யோகம்.",
      "குடும்பத்தில் சில சமயம் ரகசியங்களும், கருத்து முரண்பாடுகளும் வரலாம்; விட்டுக்கொடுத்துச் செல்வது நல்லது."
    ],
    "core_traits_en": [
      "Mesmerizing, hypnotic verbal eloquence; sways audiences through uncanny rhetoric and persuasive craft.",
      "Natural polyglot aptitude; learns foreign languages and international idioms with effortless fluency.",
      "Subject to sudden financial windfalls and unconventional revenue streams from unexpected quarters.",
      "Experiences domestic secrets or ideological friction within the family circle; requires diplomatic candor."
    ],
    "strong_placement_ta": [
      "சுப பலத்துடன் அமையும் போது: குபேர தன யோகம்! அந்நிய தேசத்து கரன்சி, கிரிப்டோகரன்சி, நவரத்தினங்கள் குவியும்.",
      "பேச்சையே மூலதனமாக வைத்து பன்னாட்டு அளவில் மாபெரும் கோடீஸ்வரராக உயருவார்."
    ],
    "strong_placement_en": [
      "Well-placed with benefics: Vast Kubera wealth! Foreign exchange reserves, digital assets/crypto, and fine gems.",
      "Monetizes rhetorical and negotiating wizardry into a global multi-million dollar fortune."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: பேச்சில் பொய்மை, வாக்கு தவறுகை, தவறான முதலீடுகளால் திடீர் திவால்.",
      "வலது கண்ணில் பார்வைக் குறைபாடு, பல் வியாதிகள் அல்லது முகத்தில் வடுக்கள் வரலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Deceptive promises, breach of financial contracts, and sudden fiscal ruin.",
      "Prone to right-eye vision loss, severe dental abscesses, and facial scars."
    ],
    "career_wealth_ta": [
      "சர்வதேச வர்த்தகம், அந்நிய செலாவணி வர்த்தகம் (Forex), மொழிபெயர்ப்பாளர், கிரிப்டோகரன்சி, ரசாயனம், தொலைக்காட்சி தொகுப்பாளர்.",
      "அந்நிய முதலீடுகளாலும் துணிச்சலான நிதி பரிவர்த்தனைகளாலும் பெரும் தன வரவு."
    ],
    "career_wealth_en": [
      "Thrives in foreign exchange markets, crypto syndicates, diplomatic translation, petrochemicals, and broadcasting.",
      "Vast capital multiplication achieved through international currency arbitrage."
    ],
    "health_precautions_ta": [
      "தொண்டை எரிச்சல், நாக்கில் புண்கள், பற்கள் ஆடுதல், வாய் துர்நாற்றம் மற்றும் வலது கண் பார்வை பாதிப்பு.",
      "வாய் சுகாதாரத்தைப் பேணுதலும், சூடான கார உணவுகளைத் தவிர்ப்பதும் அவசியம்."
    ],
    "health_precautions_en": [
      "Susceptible to pharyngeal ulceration, lingual fissures, dental cavities, and right-eye optic strain.",
      "Strict oral dental hygiene and avoidance of heavily spiced or toxic foods."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 102) & Saravali Ch. 30"
  },
  {
    "planet": "Rahu",
    "planet_name_ta": "ராகு",
    "symbol": "🐉",
    "element": "மாயை / காற்று",
    "house": 3,
    "bhava_category": "upachaya",
    "house_title_ta": "3-ஆம் பாவம் - சகஜ பாவம் (அசாத்திய தைரியம், வெற்றி & சர்வதேச தொடர்பு)",
    "house_title_en": "3rd House - Sahaja Bhava (Audacious Bravery, Upachaya Triumph & Global Media)",
    "core_traits_ta": [
      "ராகு 3-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமைவது ஜாதகருக்கு இமாலய வீரத்தையும், தீராத புகழையும் தரும் சிறந்த அமைப்பாகும்.",
      "எந்தவிதமான ஆபத்தையும் கண்டு அஞ்சாத சிங்கம் போன்ற பராக்கிரமம்; எதிரிகளைத் தன் சாதுரியத்தால் தவிடுபொடியாக்குவார்.",
      "நவீன தொழில்நுட்பங்கள், டிஜிட்டல் மீடியா மற்றும் சமூக வலைத்தளங்களில் அசாத்திய ஆதிக்கம் செலுத்துவார்.",
      "இளைய சகோதரர்களிடம் சற்று இடைவெளி இருக்கலாம்; ஆனால் பிற மனிதர்களை எளிதில் வழிநடத்துவார்."
    ],
    "core_traits_en": [
      "Rahu in the 3rd (an Upachaya house) is classically praised as an unstoppable engine of audacious valor and triumph.",
      "Lionhearted courage in perilous crises; shatters adversaries through technological and tactical ingenuity.",
      "Dominates modern digital communications, viral media, and cutting-edge electronic platforms.",
      "Independent dynamic with younger siblings; effortlessly commands large social crowds."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: சர்வதேசப் புகழ் பெற்ற ஊடக சாம்ராஜ்ய அதிபர், அரசியல் செல்வாக்கு, நாடெங்கும் வெற்றி.",
      "எடுத்த புதிய முயற்சிகள் யாவும் பல்கிப் பெருகி சரித்திரத்தில் அழியாத பொற்பெயர் பெறும்."
    ],
    "strong_placement_en": [
      "Exalted or well-placed: Globally celebrated media baron, political mastermind, and conqueror of international markets.",
      "Pioneering digital enterprises achieve viral exponential scaling and enduring acclaim."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: சகோதரர்களுடன் கருத்து வேறுபாடுகள், கைகளில் நரம்பு வலி.",
      "சமூக வலைத்தளங்களில் வீண் சர்ச்சைகள் மற்றும் சட்டச் சிக்கல்கள் வரலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Estrangement from siblings, brachial nerve inflammation, and upper limb trauma.",
      "Explosive online defamation controversies and cyber litigation entanglements."
    ],
    "career_wealth_ta": [
      "டிஜிட்டல் மார்க்கெட்டிங், ஊடக நிறுவனம், விண்வெளி மற்றும் வான்வழிப் போக்குவரத்து, விளம்பர ஏஜென்சி, தொலைத்தொடர்பு.",
      "புதிய தொழில்நுட்பங்களாலும் சர்வதேச ஒப்பந்தங்களாலும் கோடிக்கணக்கில் செல்வம் குவியும்."
    ],
    "career_wealth_en": [
      "Dominant in digital marketing networks, electronic media, aviation logistics, cyber advertising, and satellite communications.",
      "Enormous wealth generated via scalable technological patents and viral internet infrastructure."
    ],
    "health_precautions_ta": [
      "தோள்பட்டை வலி, கைகளில் நரம்புத் தளர்ச்சி, காதுகளில் இரைச்சல் மற்றும் விரல் நடுக்கம்.",
      "கணினியில் வேலை செய்வோர் உடற்பயிற்சியும் ஓய்வும் எடுப்பது அவசியம்."
    ],
    "health_precautions_en": [
      "Prone to shoulder strain, brachial plexus neuropathy, tinnitus, and carpal tunnel syndrome.",
      "Ergonomic computer practices and routine upper body mobility stretching are recommended."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 142) & Saravali Ch. 30"
  },
  {
    "planet": "Rahu",
    "planet_name_ta": "ராகு",
    "symbol": "🐉",
    "element": "மாயை / காற்று",
    "house": 4,
    "bhava_category": "kendra",
    "house_title_ta": "4-ஆம் பாவம் - சுக பாவம் (நவீன மாளிகைகள், வெளிநாட்டு வாழ்க்கை & தீவிர மன ஓட்டம்)",
    "house_title_en": "4th House - Sukha Bhava (Ultra-Modern Mansions, Foreign Residence & Restless Mind)",
    "core_traits_ta": [
      "அல்ட்ரா-மாடர்ன் சொகுசு வீடுகள், அதிநவீன மின்னணு உபகரணங்கள் மற்றும் ஆடம்பர கார்களில் வாழ்வதில் ஆர்வம்.",
      "பிறந்த மண்ணை விட்டு வெளிநாடுகளிலோ அல்லது பெருநகரங்களிலோ வாழ்வதில் அபரிமிதமான வளர்ச்சி பெறுவார்.",
      "மனதில் எப்போதும் புதிய யோசனைகளும், அடங்காத தீவிர எண்ணங்களும் அலைபாய்ந்து கொண்டிருக்கும்.",
      "தாயாரின் உடல்நலத்தில் அதிக கவனம் செலுத்த வேண்டும்; தாய் வழியில் சில கருத்து முரண்பாடுகள் வரலாம்."
    ],
    "core_traits_en": [
      "Affinity for ultra-modern smart homes, cutting-edge automated electronics, and high-tech automotive fleet.",
      "Achieves exponential material elevation when settled far away from natal home or in futuristic global metropolises.",
      "Mind surges with relentless conceptual ambition and futuristic vision, occasionally verging on chronic restlessness.",
      "Requires tender vigilance regarding mother's health; periodic emotional misunderstandings in maternal lineage."
    ],
    "strong_placement_ta": [
      "சுப பலத்துடன் இருப்பின்: வெளிநாட்டில் பல நூறு கோடி மதிப்பிலான சொகுசு பங்களாக்கள், ஆடம்பர வாகனங்கள்.",
      "பன்னாட்டு நிறுவனங்களில் உயர் தலைமைப் பதவிகள் மற்றும் நவீன சொத்துகளால் மாபெரும் யோகம்."
    ],
    "strong_placement_en": [
      "Well-placed with benefics: Multi-million dollar prime luxury estates abroad, exotic supercar fleet, and executive fame.",
      "Heads multinational infrastructure corporations with immense sovereign prestige."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தாயாரின் நரம்பு ஆரோக்கியம் பாதித்தல், பூர்வீக சொத்துகளில் தகராறுகள்.",
      "வீடு மற்றும் வாகனங்களால் எதிர்பாராத நஷ்டங்கள், விபத்துகள் மற்றும் மன அமைதியின்மை."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Maternal nervous fragility, litigations over ancestral home, and sudden domestic turbulence.",
      "Heavy financial losses through flawed property deals, vehicular collisions, and acute insomnia."
    ],
    "career_wealth_ta": [
      "ஸ்மார்ட் சிட்டி ரியல் எஸ்டேட், ஆட்டோமோட்டிவ் டெக்னாலஜி, ஏவியேஷன், எலக்ட்ரானிக்ஸ் தயாரிப்பு, இன்டீரியர் ஆட்டோமேஷன்.",
      "நவீன சொத்து பரிவர்த்தனைகளாலும் வெளிநாட்டு வர்த்தகத்தாலும் கோடிக்கணக்கில் செல்வம் சேரும்."
    ],
    "career_wealth_en": [
      "Flourishes in smart city development, automotive electrification, aviation logistics, microelectronics, and home automation.",
      "Massive capital accumulated through international property syndication and tech-enabled assets."
    ],
    "health_precautions_ta": [
      "நெஞ்சு சளி, இருதய படபடப்பு, ஆஸ்துமா, ஒவ்வாமை மற்றும் மன அழுத்தம்.",
      "சுத்தமான காற்றோட்டமான சூழலில் வாழ்வதும், சுவாசப் பயிற்சிகளும் நலம் தரும்."
    ],
    "health_precautions_en": [
      "Susceptible to pulmonary spasms, cardiac palpitations, bronchial allergies, and psychosomatic anxiety.",
      "Dwelling in unpolluted, well-ventilated environments and daily pranayama protect cardiovascular health."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 176) & Saravali Ch. 30"
  },
  {
    "planet": "Rahu",
    "planet_name_ta": "ராகு",
    "symbol": "🐉",
    "element": "மாயை / காற்று",
    "house": 5,
    "bhava_category": "trikona",
    "house_title_ta": "5-ஆம் பாவம் - புத்திர பாவம் (கூர்மையான தந்திர புத்தி, பங்குச் சந்தை & புதிய கண்டுபிடிப்புகள்)",
    "house_title_en": "5th House - Putra Bhava (Tactical Cunning, Speculative Windfalls & Disruptive Inventions)",
    "core_traits_ta": [
      "மின்னல் போன்ற கூர்மையான புத்திசாலித்தனம், புதுமையான தொழில் யுக்திகள் மற்றும் தந்திரமான திட்டமிடல்.",
      "பங்குச் சந்தை, கிரிப்டோகரன்சி, ஊக வணிகம் மற்றும் நவீன ஸ்டார்ட்-அப்களில் துணிச்சலாக இறங்கிச் சாதிப்பார்.",
      "புத்திர பாக்கியத்தில் ஆரம்பத்தில் சில மருத்துவக் கவனங்கள் தேவைப்படலாம்; குழந்தைகள் நவீன துறைகளில் சிறந்து விளங்குவர்.",
      "மந்திரங்கள், ஆன்மீக ரகசியங்கள் மற்றும் மாய சாஸ்திரங்களில் ஆழமான ஈடுபாடு கொண்டிருப்பார்."
    ],
    "core_traits_en": [
      "Razor-sharp tactical brilliance, avant-garde inventive ingenuity, and masterly unconventional planning.",
      "Audacious appetite for stock markets, crypto-derivatives, venture startups, and algorithmic trading.",
      "Progeny may require initial prenatal care; children excel in cutting-edge technological or artistic disciplines.",
      "Deep fascination with esoteric occult lore, hypnotic psychology, and mystical symbology."
    ],
    "strong_placement_ta": [
      "சுப பலத்துடன் அமையும் போது: பங்குச் சந்தையில் பல நூறு கோடி ஜாக்பாட் லாபம், சர்வதேச புதிய கண்டுபிடிப்பாளர்.",
      "அரசாங்க உயர் ஆலோசனை குழுக்களில் இடம் பெறுதல், உலகளாவிய ஸ்டார்ட்-அப் நிறுவனங்களின் அதிபர்."
    ],
    "strong_placement_en": [
      "Well-placed with benefics: Massive speculative jackpots in financial derivatives, celebrated tech inventor.",
      "Founder of global unicorn tech startups and advisor to state technological commissions."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: புத்திர பாக்கியத்தில் காலதாமதம், கருச்சிதைவு அபாயம்.",
      "சூதாட்டம் அல்லது தவறான ஊக வணிகத்தால் பெரும் நிதி இழப்புகள் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Miscarriages, complications in childbearing, and acute anxieties regarding progeny.",
      "Crippling financial bankruptcies incurred through reckless, impulsive speculative gambling."
    ],
    "career_wealth_ta": [
      "பங்குச் சந்தை அல்காரிதம், கிரிப்டோ டிரேடிங், கேமிங் தொழில், செயற்கை நுண்ணறிவு, சினிமா இயக்கம், மருந்து ஆராய்ச்சி.",
      "அறிவுசார் படைப்புகளாலும் துணிச்சலான நவீன முதலீடுகளாலும் அள்ள அள்ளக் குறையாத தன லாபம்."
    ],
    "career_wealth_en": [
      "Dominant in algorithmic trading, crypto asset management, video game engineering, AI research, and biotechnology.",
      "Generates vast fortunes through proprietary algorithms, tech patents, and venture exits."
    ],
    "health_precautions_ta": [
      "அஜீரணம், வயிற்றில் வாயுத் தொல்லை, குடல் புண்கள், அமிலத்தன்மை மற்றும் உணவு ஒவ்வாமை.",
      "இயற்கையான சத்தான உணவுகளை உட்கொள்ளுதலும், நச்சு உணவுகளைத் தவிர்ப்பதும் அவசியம்."
    ],
    "health_precautions_en": [
      "Prone to nervous dyspepsia, gastrointestinal gas, peptic ulcerations, hyperacidity, and severe food allergies.",
      "Consume pure, preservative-free organic foods and avoid unhygienic processed foods."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 222) & Saravali Ch. 30"
  },
  {
    "planet": "Rahu",
    "planet_name_ta": "ராகு",
    "symbol": "🐉",
    "element": "மாயை / காற்று",
    "house": 6,
    "bhava_category": "dusthana",
    "house_title_ta": "6-ஆம் பாவம் - சத்ரு பாவம் (எதிரிகளைத் தவிடுபொடியாக்குதல் / மகா உபசய பலம்)",
    "house_title_en": "6th House - Satru Bhava (Annihilation of Adversaries & Supreme Upachaya Might)",
    "core_traits_ta": [
      "ராகு 6-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமர்வது ஜாதகருக்கு இமாலய பலத்தையும், அசைக்க முடியாத சத்ரு ஜெயத்தையும் தரும்.",
      "எதிரிகள், வழக்குகள், சதித்திட்டங்கள் மற்றும் போட்டிகளைத் தன் சாதுரியத்தாலும் பலத்தாலும் தூள்தூளாக்குவார்.",
      "அளப்பரிய நோய் எதிர்ப்புச் சக்தி; கொடிய ஆபத்துகளிலிருந்தும் நோய்களிலிருந்தும் எளிதில் மீண்டு வருவார்.",
      "பணியாளர்களையும், பல்வேறு மொழி பேசும் உழைப்பாளர்களையும் தன் கட்டுப்பாட்டில் வைத்து வேலை வாங்குவார்."
    ],
    "core_traits_en": [
      "Rahu in the 6th (an Upachaya house) is a classically celebrated powerhouse of victory and invincible immunity.",
      "Totally demolishes adversaries, political conspiracies, hostile litigations, and commercial competitors.",
      "Possesses astonishing physiological immunity and rapid recuperative power from physical perils.",
      "Commands absolute obedience and high productivity from diverse, multicultural labor forces."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: சத்ரு சம்ஹார யோகம்! எதிரிகள் இல்லாத பெருவாழ்வு, சர்வதேசப் புலனாய்வுத் தலைமை.",
      "அளப்பரிய செல்வம், கடன் இல்லாத அமைதியான வாழ்க்கை மற்றும் அனைத்துப் போட்டிகளிலும் தொடர் வெற்றி."
    ],
    "strong_placement_en": [
      "Exalted or well-placed: Bestows complete Shatru Samhara Yoga! Total elimination of foes, heads intelligence agencies.",
      "Immense accumulated wealth, unassailable physical vitality, and perpetual competitive victories."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: புரியாத மர்ம நோய்கள், ரத்தத்தில் நச்சுத்தன்மை, தோல் வியாதிகள்.",
      "வேலையாட்களால் ஏமாற்றப்படுதலும், கடன் சுமைகளால் மன உளைச்சலும் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Baffling undiagnosable illnesses, systemic blood toxicities, and severe dermatosis.",
      "Embezzlement by treacherous employees and anxiety over mounting unpaid debts."
    ],
    "career_wealth_ta": [
      "சைபர் கிரைம் புலனாய்வு, குற்றவியல் சட்டம், மருந்து உற்பத்தி, சர்வதேச கடத்தல் தடுப்புப் பிரிவு, சுங்கத்துறை, பொது சுகாதாரம்.",
      "சவால்களையும் போட்டிகளையும் தனக்குச் சாதகமாக மாற்றி கோடிக்கணக்கில் வருவாய் ஈட்டுவார்."
    ],
    "career_wealth_en": [
      "Excels in cyber-crime forensics, criminal trial jurisprudence, pharmaceutical synthesis, customs enforcement, and epidemiology.",
      "Extracts substantial financial wealth directly from crisis management and competitive conquests."
    ],
    "health_precautions_ta": [
      "ஒவ்வாமை (Allergies), ரத்தத்தில் நச்சுத்தன்மை, பூச்சிக்கடி, குடல் தொற்று மற்றும் தோல் அரிப்பு.",
      "சுத்தமான உணவையும் நீரையும் உட்கொள்ளுதலும், நச்சுப் பொருட்களைத் தவிர்ப்பதும் அவசியம்."
    ],
    "health_precautions_en": [
      "Susceptible to sudden systemic anaphylaxis, blood impurities, venomous bites, intestinal parasites, and eczema.",
      "Strict water purification, allergen avoidance, and periodic lymphatic detox regimens are indicated."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 262) & Saravali Ch. 30"
  },
  {
    "planet": "Rahu",
    "planet_name_ta": "ராகு",
    "symbol": "🐉",
    "element": "மாயை / காற்று",
    "house": 7,
    "bhava_category": "kendra",
    "house_title_ta": "7-ஆம் பாவம் - களத்திர பாவம் (வேற்றுமொழி/கலாச்சாரத் துணை & பன்னாட்டு வர்த்தகம்)",
    "house_title_en": "7th House - Kalathra Bhava (Cross-Cultural Spouse & Transnational Alliances)",
    "core_traits_ta": [
      "வேற்று மதம், வேற்று மொழி அல்லது முற்றிலும் மாறுபட்ட கலாச்சாரப் பின்னணியிலிருந்து கவர்ச்சிகரமான வாழ்க்கைத் துணை அமைவார்.",
      "வாழ்க்கைத் துணையிடம் சுதந்திர மனப்பான்மையும், நவீன வாழ்க்கை முறையும் நிறைந்திருக்கும்.",
      "தாம்பத்தியத்தில் ஈகோ மோதல்கள் வராமல் பரஸ்பர புரிதலுடன் நடந்து கொள்வது மிக அவசியம்.",
      "கூட்டு வர்த்தகத்தில் வெளிநாட்டினருடனும், பன்னாட்டு நிறுவனங்களுடனும் ஒப்பந்தங்கள் செய்து வெற்றிபெறுவார்."
    ],
    "core_traits_en": [
      "Spouse hails from a diverse ethnic, foreign, or unconventional cultural background; highly charismatic and modern.",
      "Partner possesses an independent, dynamic mindset with a forward-looking lifestyle.",
      "Requires conscious emotional maturity and open communication to prevent volatile misunderstandings.",
      "Sensational success in transnational joint ventures, forging alliances with foreign conglomerates."
    ],
    "strong_placement_ta": [
      "சுப பலத்துடன் அமைந்தால்: பன்னாட்டு செல்வந்த குடும்பத் துணை, வெளிநாட்டில் மாபெரும் ராஜயோக வாழ்க்கை.",
      "சர்வதேச வர்த்தகத்தில் பல நூறு கோடி லாபமும், சமூகத்தில் கவர்ச்சிகரமான தம்பதியராகப் போற்றப்படும் நிலையும் கிட்டும்."
    ],
    "strong_placement_en": [
      "Well-placed with benefics: Marries into an affluent international dynasty; lavish global lifestyle abroad.",
      "Multi-million dollar windfalls from global trade pacts; celebrated as an influential cosmopolitan couple."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: திருமண வாழ்வில் கடும் விரிசல், ரகசிய உறவுகளால் குடும்பப் பிரிவு.",
      "கூட்டுத் தொழிலில் பார்ட்னர்களால் ஏமாற்றப்பட்டு சர்வதேச அளவில் வழக்குகளும் நஷ்டங்களும் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Bitter matrimonial strife, scandalous clandestine affairs causing separation or divorce.",
      "Catastrophic financial betrayal by foreign business partners leading to international arbitration."
    ],
    "career_wealth_ta": [
      "சர்வதேச வர்த்தகம், ஏற்றுமதி-இறக்குமதி, வெளிநாட்டுத் தூதரகங்கள், பன்னாட்டு மக்கள் தொடர்பு, சர்வதேச விமானப் போக்குவரத்து.",
      "வாழ்க்கைத் துணையின் வழியிலும், வெளிநாட்டு கூட்டாண்மையாலும் கோடிக்கணக்கில் தன சேர்க்கை."
    ],
    "career_wealth_en": [
      "Dominant in cross-border commerce, global export-import, consular representation, international PR, and aviation.",
      "Substantial capital influx via multinational partnerships and foreign spousal assets."
    ],
    "health_precautions_ta": [
      "சிறுநீரகப் பாதை அழற்சி, பாலியல் உறுப்புகளில் தொற்று, அடிவயிற்று உஷ்ணம் மற்றும் ஒவ்வாமை.",
      "முறையான மருத்துவப் பரிசோதனைகளும், தனிநபர் சுகாதாரமும் மிகவும் அவசியம்."
    ],
    "health_precautions_en": [
      "Susceptible to urinary tract infections, urogenital inflammation, reproductive heat, and systemic allergies.",
      "Strict personal hygiene, ample hydration, and periodic reproductive health screenings."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Rahu",
    "planet_name_ta": "ராகு",
    "symbol": "🐉",
    "element": "மாயை / காற்று",
    "house": 8,
    "bhava_category": "dusthana",
    "house_title_ta": "8-ஆம் பாவம் - ஆயுள் பாவம் (ரகசிய ஞானம், திடீர் யோகம் & ஆபத்துகளிலிருந்து தப்புதல்)",
    "house_title_en": "8th House - Ayur Bhava (Occult Mastery, Sudden Windfalls & Miraculous Survival)",
    "core_traits_ta": [
      "ஆழ்ந்த மறைபொருள் ஞானம், ஜோதிடம், தாந்திரீகம், உளவியல் மற்றும் பிரபஞ்ச ரகசியங்களை ஆராயும் பேரார்வம்.",
      "வாழ்க்கையில் திடீரென ஏற்படும் இமாலய அதிர்ஷ்டங்களும், அதே சமயம் எதிர்பாராத சரிவுகளும் மாறி மாறி வரும்.",
      "ஆபத்தான விபத்துகள் மற்றும் நெருக்கடிகளிலிருந்து மயிரிழையில் உயிர் தப்பிக்கும் விசித்திர யோகம் உண்டு.",
      "அரசாங்க வரி விவகாரங்களிலும் சட்ட விதிகளிலும் மிகுந்த விழிப்புணர்வுடன் இருக்க வேண்டும்."
    ],
    "core_traits_en": [
      "Profound fascination with occult metaphysics, astrology, esoteric tantra, and clandestine psychology.",
      "Experiences dramatic roller-coaster fluctuations: sudden stratospheric windfalls alternating with abrupt crises.",
      "Possesses an uncanny knack for surviving life-threatening disasters by a hair's breadth.",
      "Must maintain impeccable transparency in taxation, offshore finances, and legal compliance."
    ],
    "strong_placement_ta": [
      "சுப பலத்துடன் அமைந்தால்: வெளிநாட்டிலிருந்து திடீர் உயில் சொத்துகள், கிரிப்டோ முதலீடுகளில் மாபெரும் லாபம், நீண்ட ஆயுள்.",
      "ரகசியத் திட்டங்கள் மூலம் பல நூறு கோடி ஈட்டி சமுதாயத்தில் செல்வாக்குடன் வாழ்வார்."
    ],
    "strong_placement_en": [
      "Well-placed with benefics: Massive foreign legacy windfalls, phenomenal crypto investment yields, and long life.",
      "Monetizes proprietary confidential research into vast multi-million dollar liquidity."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: மர்ம நோய்கள், விஷக்கடி, அரசு வழக்குகளால் அபராதங்கள்.",
      "துணையின் ஆரோக்கியத்தில் பின்னடைவுகள் மற்றும் திடீர் நிதி இழப்புகள் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Baffling chronic ailments, toxic envenomation, punitive tax penalties, and sudden disgrace.",
      "Severe health trials for spouse and rapid dissipation of inherited assets."
    ],
    "career_wealth_ta": [
      "சைபர் செக்யூரிட்டி ஹேக்கிங், தடயவியல் துறை, சர்வதேச உளவுத்துறை, நச்சுயியல், காப்பீட்டுத் தணிக்கை, கிரிப்டோகரன்சி.",
      "திடீர் இன்சூரன்ஸ் இழப்பீடுகள், உயில் சொத்துகள் மற்றும் ரகசிய ஒப்பந்தங்கள் மூலம் தன வரவு."
    ],
    "career_wealth_en": [
      "Excels in cybersecurity penetration testing, forensic pathology, international espionage, toxicology, and crypto assets.",
      "Wealth derived through settlement windfalls, unearned inheritance, and crisis advisory."
    ],
    "health_precautions_ta": [
      "மூல நோய், ஆசனவாய் புண்கள், மர்மமான நரம்பு வலிகள், விஷக்கடி மற்றும் தூக்கமின்மை.",
      "சுத்தமான உணவை உண்பதும், நச்சுப் பொருட்களைத் தவிர்ப்பதும் நலம் தரும்."
    ],
    "health_precautions_en": [
      "Vulnerable to hemorrhoidal bleeding, anal fissures, idiopathic nerve pain, toxic stings, and insomnia.",
      "Strict dietary hygiene, avoidance of chemical toxins, and grounding meditative rest."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Rahu",
    "planet_name_ta": "ராகு",
    "symbol": "🐉",
    "element": "மாயை / காற்று",
    "house": 9,
    "bhava_category": "trikona",
    "house_title_ta": "9-ஆம் பாவம் - பாக்கிய பாவம் (நவீன தத்துவம், சர்வதேசப் பயணம் & புதுமை யோகம்)",
    "house_title_en": "9th House - Bhagya Bhava (Unconventional Philosophy, Global Odysseys & Breakthrough Fortune)",
    "core_traits_ta": [
      "பாரம்பரிய மதச் சடங்குகளைத் தாண்டி, நவீன உலகளாவிய ஆன்மீக சிந்தனைகளை விரும்பும் முற்போக்குவாதி.",
      "வெளிநாடுகளுக்கு அடிக்கடி பயணம் செய்தல்; பன்னாட்டுப் பல்கலைக்கழகங்களில் ஆராய்ச்சி செய்தல்.",
      "தந்தையுடன் கருத்து வேறுபாடுகள் வரலாம்; ஆனால் தந்தையின் நலனில் அக்கறை கொண்டிருப்பார்.",
      "வாழ்க்கையில் வழக்கத்திற்கு மாறான வழிகளில் அபரிமிதமான அதிர்ஷ்டங்களும் வெற்றிகளும் தேடி வரும்."
    ],
    "core_traits_en": [
      "Transcends rigid orthodoxy, championing universal spiritual humanism and progressive philosophical outlooks.",
      "Passionate world traveler; pursues cutting-edge research in premier global universities.",
      "Periodic ideological friction with father, yet strives to establish independent worldly laurels.",
      "Fortune arrives through non-traditional, innovative pathways and foreign patronages."
    ],
    "strong_placement_ta": [
      "சுப பலத்துடன் அமைந்தால்: சர்வதேச அங்கீகாரம், பன்னாட்டு அமைப்புகளில் உயரிய பதவி, வெளிநாட்டு யோகம்.",
      "உலகளாவிய நிறுவனங்களைத் தோற்றுவித்து சர்வதேச அளவில் புகழ்பெற்ற தலைவராக உயருவார்."
    ],
    "strong_placement_en": [
      "Well-placed with benefics: International cultural acclaim, executive directorships in global multilateral bodies.",
      "Founds multinational innovation hubs and commands widespread international respect."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தந்தையின் உடல்நலக்குறைவு, மத நம்பிக்கைகளில் குழப்பம்.",
      "வெளிநாட்டு விசா மற்றும் குடியுரிமை விவகாரங்களில் சட்டச் சிக்கல்கள் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Paternal health complications, acute spiritual disillusionment, and ideological alienation.",
      "Visa denials, immigration litigation, and document hassles during international relocations."
    ],
    "career_wealth_ta": [
      "சர்வதேச வர்த்தகப் பிரதிநிதி, ஏவியேஷன் நிர்வாகம், சர்வதேசச் சட்டம், வெளிநாட்டுப் பல்கலைக்கழகப் பேராசிரியர், புதுமைத் தொழில்.",
      "வெளிநாட்டு நாணயங்களாலும் பன்னாட்டுத் தொடர்புகளாலும் பல கோடிகளில் சொத்துக்கள் சேரும்."
    ],
    "career_wealth_en": [
      "Distinguished as transnational trade commissioner, aviation executive, international jurist, and foreign professor.",
      "Generates vast wealth through offshore royalties, foreign exchange earnings, and cross-border consulting."
    ],
    "health_precautions_ta": [
      "தொடைப் பகுதியில் நரம்பு வலி, இடுப்பு வாதம் (Sciatica), ஒவ்வாமை மற்றும் தசைப் பிடிப்புகள்.",
      "நீண்ட விமானப் பயணங்களின் போது உடற்பயிற்சியும், போதுமான நீர் அருந்துதலும் அவசியம்."
    ],
    "health_precautions_en": [
      "Susceptible to femoral neuropathy, sciatica sensitivity, travel-induced deep vein thrombosis, and allergies.",
      "Hydrate generously during long flights, wear compression socks, and maintain regular lower body mobility."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Rahu",
    "planet_name_ta": "ராகு",
    "symbol": "🐉",
    "element": "மாயை / காற்று",
    "house": 10,
    "bhava_category": "kendra",
    "house_title_ta": "10-ஆம் பாவம் - ஜீவன பாவம் (அதிவேக வளர்ச்சி, சர்வதேச அதிகாரம் & அரசியல் செல்வாக்கு)",
    "house_title_en": "10th House - Karma Bhava (Meteoric Rise, Global Authority & Political Stature)",
    "core_traits_ta": [
      "ராகு 10-ஆம் பாவத்தில் அமைவது தொழிலில் மின்னல் வேக வளர்ச்சியையும், சர்வதேச செல்வாக்கையும் தரும் மாபெரும் யோகமாகும்.",
      "சாதாரண நிலையிலிருந்து தொடங்கி குறுகிய காலத்தில் சமுதாயத்தின் உச்சாணிக் கொம்பில் அமரும் அசுர வேகம்.",
      "அரசியல், சினிமா, ஊடகம் மற்றும் பன்னாட்டு வர்த்தகத்தில் ஆயிரக்கணக்கான மக்களை வசீகரிக்கும் தலைமை ஆளுமை.",
      "எதிர்ப்புகளையும் விமர்சனங்களையும் தனக்குச் சாதகமான விளம்பரமாக மாற்றி வெற்றிபெறும் வித்தைக்காரர்."
    ],
    "core_traits_en": [
      "Rahu in the 10th is a celebrated catalyst for meteoric, sensational career elevation and international prominence.",
      "Ascends from total obscurity to supreme public heights with astonishing velocity and daring audacity.",
      "Commands magnetic authority across politics, cinema, media conglomerates, and multinational commerce.",
      "Master of public relations; turns hostile controversies into free publicity and stepping stones to power."
    ],
    "strong_placement_ta": [
      "சுப பலத்துடன் அமைந்தால்: நாட்டின் முதன்மை மந்திரி, சர்வதேச பெருநிறுவனத் தலைவர் (CEO), சரித்திரப் புகழ்.",
      "பல்லாயிரம் கோடி மதிப்பிலான தொழில் சாம்ராஜ்யத்தை நிறுவி உலகளவில் தலைசிறந்த மனிதராகத் திகழ்வார்."
    ],
    "strong_placement_en": [
      "Exalted or well-placed: Sovereign minister, global CEO of Fortune 50 mega-corporation, and iconic historical figure.",
      "Builds a multi-billion dollar industrial and media empire, celebrated globally as a visionary trailblazer."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தொழிலில் திடீர் வீழ்ச்சி, பொது வாழ்வில் ஊழல் குற்றச்சாட்டுகள்.",
      "அரசியல் சதிகளாலும் தவறான ஆலோசகர்களாலும் நற்பெயருக்குக் களங்கம் ஏற்பட வாய்ப்புண்டு."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Sudden catastrophic fall from power, corruption scandals, and public opprobrium.",
      "Victim of political conspiracies and toxic advice from manipulative retainers."
    ],
    "career_wealth_ta": [
      "அரசியல் தலைமை, சினிமா தயாரிப்பு, தகவல் தொழில்நுட்பத் தலைமை, வான்வழி மற்றும் விண்வெளித் துறை, சர்வதேச எண்ணெய் வர்த்தகம்.",
      "அரசாங்க செல்வாக்காலும் தொழில் மேன்மையாலும் பல நூறு கோடி செல்வம் குவியும்."
    ],
    "career_wealth_en": [
      "Dominant in political statecraft, major film production, big-tech executive suites, aerospace, and energy syndicates.",
      "Accumulates immense wealth through high-level state influence, equity shares, and multinational ventures."
    ],
    "health_precautions_ta": [
      "பணிச்சுமையால் ரத்த அழுத்தம், தூக்கமின்மை, நரம்புத் தளர்ச்சி மற்றும் மர்மமான தலைவலிகள்.",
      "வேலைக்கு நடுவே அமைதியான தியானமும், முறையான ஓய்வும் எடுப்பது ஆரோக்கியத்தைப் பாதுகாக்கும்."
    ],
    "health_precautions_en": [
      "Prone to executive burnout, hypertension, chronic insomnia, nervous exhaustion, and idiopathic migraines.",
      "Daily transcendental meditation and structured relaxation intervals preserve executive stamina."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Rahu",
    "planet_name_ta": "ராகு",
    "symbol": "🐉",
    "element": "மாயை / காற்று",
    "house": 11,
    "bhava_category": "upachaya",
    "house_title_ta": "11-ஆம் பாவம் - லாப பாவம் (அகண்ட தன லாபம் / குபேர யோகம் & வெளிநாட்டு வருவாய்)",
    "house_title_en": "11th House - Labha Bhava (Massive Multi-Channel Gains, Kubera Wealth & Global Network)",
    "core_traits_ta": [
      "ராகு 11-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமர்வது ஜாதகருக்கு கோடானுகோடி தன லாபத்தைத் தரும் மிக உன்னதமான யோகமாகும்.",
      "எண்ணிய ஆசைகள் அனைத்தும் எளிதில் நிறைவேறும்; பல வழிகளிலிருந்து பணம் வந்து கொண்டே இருக்கும்.",
      "அரசியல்வாதிகள், தொழில் அதிபர்கள் மற்றும் செல்வாக்கு மிக்க வெளிநாட்டினரின் விரிவான நட்பு வட்டம்.",
      "மூத்த சகோதரர்களிடம் சற்று சுதந்திரமான அணுகுமுறை இருக்கும்; ஆனால் அவர்களால் தன ஆதாயம் கிட்டும்."
    ],
    "core_traits_en": [
      "Rahu in the 11th (an Upachaya house) is one of the most prolific engines of boundless multi-stream wealth and ambition.",
      "Rapid, frictionless fulfillment of grand aspirations; money pours in through unconventional channels.",
      "Surrounded by a high-powered global network of politicians, venture capitalists, and foreign magnates.",
      "Maintains an independent yet profitable dynamic with elder siblings, benefiting materially through them."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: எண்ணற்ற வழிகளிலிருந்து பணம் கொட்டும், சொகுசு மாளிகைகள், குபேர யோகம்.",
      "கிரிப்டோ, பங்குச் சந்தை மற்றும் பன்னாட்டு வர்த்தகத்தில் நாட்டின் முன்னணி பணக்காரராகத் திகழுதல்."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Bestows multi-billion dollar liquid holdings, luxury estates, and supreme Kubera Yoga.",
      "Ranks among the foremost wealthy magnates in tech startups, speculative markets, and global commerce."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: நண்பர்களால் ஏமாற்றப்பட்டு தன நஷ்டம், சட்டவிரோத முதலீடுகளால் இழப்பு.",
      "லாபங்கள் கைநழுவுதல் அல்லது பண விரயங்களால் அரசு அபராதங்கள் ஏற்படுதல்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Heavy betrayal by counterfeit associates, catastrophic losses in dubious unregulated schemes.",
      "Capital frozen by regulatory authorities and punitive fines."
    ],
    "career_wealth_ta": [
      "வென்ச்சர் கேபிடல், கிரிப்டோகரன்சி, பங்கு வர்த்தகம், ஈ-காமர்ஸ், டிஜிட்டல் ஊடகம், சர்வதேச ஏற்றுமதி.",
      "முதலீடுகளின் அதிவேக வளர்ச்சியாலும் பன்னாட்டு தொடர்புகளாலும் கோடீஸ்வர யோகம்."
    ],
    "career_wealth_en": [
      "Lucrative success in venture capital funds, crypto networks, high-frequency trading, e-commerce, and global import-export.",
      "Extraordinary capital multiplication placing the native in the elite billionaire tier."
    ],
    "health_precautions_ta": [
      "இடது காது வலி, கணுக்கால் நரம்பு இழுத்தல், ரத்த ஓட்டக் குறைபாடுகள் மற்றும் ஒவ்வாமை.",
      "கால் நரம்புகளுக்கான உடற்பயிற்சியும், காது ஆரோக்கியத்தைப் பேணுதலும் நல்லது."
    ],
    "health_precautions_en": [
      "Susceptible to left-ear ache, ankle ligament stiffness, sluggish peripheral circulation, and systemic allergies.",
      "Daily ankle mobility drills, compression wear during flights, and regular otic checkups."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Rahu",
    "planet_name_ta": "ராகு",
    "symbol": "🐉",
    "element": "மாயை / காற்று",
    "house": 12,
    "bhava_category": "dusthana",
    "house_title_ta": "12-ஆம் பாவம் - விரய பாவம் (வெளிநாட்டு குடியுரிமை, ரகசிய முதலீடுகள் & அயன சயனம்)",
    "house_title_en": "12th House - Vraya Bhava (Permanent Foreign Settlement, Secret Offshores & Restless Sleep)",
    "core_traits_ta": [
      "பிறந்த மண்ணை விட்டு வெளிநாடுகளில் நிரந்தரமாகக் குடியேறும் பிராப்தி; அந்நிய தேசத்தில் மாபெரும் யோகம்.",
      "பணத்தை ரகசியமாக முதலீடு செய்வதிலும், வெளிநாட்டு வங்கிகளில் சொத்துகளைச் சேர்ப்பதிலும் ஆர்வம்.",
      "தனிமையை விரும்புவார்; இரவு நேரங்களில் அதிக விழிப்புடனும் படைப்பாற்றலுடனும் செயல்படுவார்.",
      "அரசாங்க சட்ட விதிகளிலும் வரி விவகாரங்களிலும் மிகுந்த எச்சரிக்கையுடன் கையெழுத்திட வேண்டும்."
    ],
    "core_traits_en": [
      "Destiny for permanent foreign residency or citizenship; thrives incomparably better abroad than in birth land.",
      "Acute acumen for managing confidential offshore investments, private trusts, and international bank holdings.",
      "Loves solitary night hours; nocturnal bursts of creative and strategic genius.",
      "Must maintain strict compliance in immigration filings, international taxation, and signed cross-border declarations."
    ],
    "strong_placement_ta": [
      "சுப பலத்துடன் இருப்பின்: வெளிநாட்டில் மாபெரும் தொழில் சாம்ராஜ்யம், சர்வதேசக் குடியுரிமை, பன்னாட்டுச் செல்வம்.",
      "அயன சயன சுகம், அமைதியான ஆத்ம சாந்தி மற்றும் வெளிநாட்டு நாணயங்கள் மூலம் அளப்பரிய தன வரவு."
    ],
    "strong_placement_en": [
      "Well-placed with benefics: Commands vast commercial conglomerates abroad; dual citizenship in premier nations.",
      "Substantial foreign currency reserves and profound peace of mind in exotic overseas retreats."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: கடுமையான தூக்கமின்மை, கண் பார்வை பாதிப்பு, வெளிநாட்டில் சிறைவாசம் அல்லது நாடு கடத்தல்.",
      "வீண் விரயங்கள், சட்டவிரோத பழக்கங்களால் அபராதங்கள் மற்றும் மன உளைச்சல்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Severe insomnia, left-eye vision defects, visa deportation, or foreign confinement.",
      "Heavy financial dissipation through reckless nocturnal habits and regulatory penalties."
    ],
    "career_wealth_ta": [
      "சர்வதேச கப்பல் போக்குவரத்து, வெளிநாட்டுத் தூதரகங்கள், சர்வதேச நிதி ஆலோசகர், விமானப் போக்குவரத்து, ரசாயன ஏற்றுமதி.",
      "வெளிநாட்டு நாணயங்களாலும் பன்னாட்டு வர்த்தகத்தாலும் கோடிக்கணக்கில் வற்றாத தன லாபம்."
    ],
    "career_wealth_en": [
      "Thrives in international maritime logistics, consular diplomacy, offshore finance, aviation, and petrochemical export.",
      "Colossal income denominated in hard foreign currencies flowing from overseas holdings."
    ],
    "health_precautions_ta": [
      "இடது கண் பார்வைக் கோளாறு, பாதங்களில் வலி, தூக்கமின்மை (Insomnia) மற்றும் மர்ம நோய்கள்.",
      "இரவில் படுக்கும் முன் கண்களைக் குளிர்ந்த நீரால் கழுவுதலும், தியானமும் நல்ல தூக்கத்தைத் தரும்."
    ],
    "health_precautions_en": [
      "Prone to left-eye refractive strain, peripheral foot neuropathy, chronic insomnia, and psychosomatic ailments.",
      "Nightly cold eye-compresses, gentle foot reflexology, and regular renal health screenings."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Ketu",
    "planet_name_ta": "கேது",
    "symbol": "☄️",
    "element": "மோட்சம் / நெருப்பு",
    "house": 1,
    "bhava_category": "kendra",
    "house_title_ta": "1-ஆம் பாவம் - லக்னம் (ஞான காரகன் / உள்ளுணர்வு, பற்றற்ற நிலை & ஆன்மீக முகம்)",
    "house_title_en": "1st House - Ascendant / Tanu Bhava (Mokshakaraka / Gnostic Intuition & Ascetic Persona)",
    "core_traits_ta": [
      "ஆழ்ந்த ஆன்மீக நாட்டம், கூர்மையான உள்ளுணர்வு (Intuition), எதையும் ஊடுருவிப் பார்க்கும் ஞானப் பார்வை.",
      "உலகியல் மாயைகளில் எளிதில் மயங்காத பற்றற்ற சுபாவம்; அமைதியான, முனிவர் போன்ற முகத்தோற்றம்.",
      "சுயமரியாதைக்கு முக்கியத்துவம் கொடுப்பார்; ஆடம்பரங்களை விட எளிமையான வாழ்வையே விரும்புவார்.",
      "மருத்துவம், ஜோதிடம், யோகா மற்றும் ரகசிய சாஸ்திரங்களை இயல்பாகவே உணரும் தெய்வீக ஆற்றல் உண்டு.",
      "மனதில் சில சமயம் காரணமற்ற தனிமை உணர்வும், உலகப் பற்றுகளிலிருந்து விலகும் எண்ணமும் வரலாம்."
    ],
    "core_traits_en": [
      "Profound spiritual orientation, piercing intuitive foresight, and an uncanny ability to perceive hidden motives.",
      "Natural detachment from shallow material vanity; carries an enigmatic, ascetic countenance.",
      "Quietly guarded self-respect; prefers austere, unpretentious simplicity over gaudy ostentation.",
      "Innate flair for healing arts, Vedic astrology, yogic metaphysics, and occult diagnostics.",
      "Periodic bouts of subjective isolation, yearning to transcend worldly attachments."
    ],
    "strong_placement_ta": [
      "விருச்சிகம்/தனுசில் பலம் பெற்று சுப சேர்க்கை அமைந்தால்: உலகப் புகழ் பெற்ற ஆன்மீக குரு, சித்த மருத்துவர், ஞான யோகி.",
      "அரசாங்கத்தால் போற்றப்படும் மாபெரும் மெய்யியலாளராகத் திகழ்ந்து சரித்திரத்தில் இடம்பிடிப்பார்."
    ],
    "strong_placement_en": [
      "Exalted in Scorpio/Sagittarius with benefic aspects: Internationally revered spiritual preceptor, master naturopath, or gnostic sage.",
      "Conferred premier civic honors as an iconic philosopher, leaving an immortal legacy of wisdom."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தலைவலி, கண் பார்வைக் குறைபாடு, நரம்புத் தளர்ச்சி, சரும நோய்கள்.",
      "தன்னம்பிக்கைக் குறைவு, முடிவெடுப்பதில் குழப்பம் மற்றும் சமுதாயத்திலிருந்து விலகி வாழும் எண்ணம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Chronic cranial pain, ocular defects, nervous debility, and stubborn eczema.",
      "Erosion of self-confidence, vacillating indecision, and neurotic social alienation."
    ],
    "career_wealth_ta": [
      "ஆன்மீக ஆசிரமங்கள், யோகா மற்றும் இயற்கை மருத்துவம், ஜோதிட ஆராய்ச்சி, உளவியல் ஆலோசனை, ஹோமியோபதி.",
      "அறிவுசார் வழிகாட்டலாலும் ஆன்மீக சேவைகளாலும் கௌரவமான செல்வச் சேர்க்கை."
    ],
    "career_wealth_en": [
      "Distinction as spiritual ashram director, naturopathic physician, master astrologer, psychologist, and homeopath.",
      "Honorable wealth accrued through institutional donations, consulting honorariums, and literary treatises."
    ],
    "health_precautions_ta": [
      "தலையில் காயங்கள், ஒவ்வாமை (Allergies), தோல் வறட்சி, நரம்புத் தளர்ச்சி மற்றும் தூக்கமின்மை.",
      "தியானம், பிராணாயாமம் மற்றும் எளிய இயற்கை உணவுகள் மன அமைதியையும் ஆரோக்கியத்தையும் தரும்."
    ],
    "health_precautions_en": [
      "Susceptible to head lacerations, mysterious allergies, dry skin eruptions, nervous exhaustion, and insomnia.",
      "Daily transcendental meditation, breathwork, and clean organic nutrition stabilize the nervous system."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 54) & Saravali Ch. 30"
  },
  {
    "planet": "Ketu",
    "planet_name_ta": "கேது",
    "symbol": "☄️",
    "element": "மோட்சம் / நெருப்பு",
    "house": 2,
    "bhava_category": "panaphara",
    "house_title_ta": "2-ஆம் பாவம் - தன பாவம் (மௌன வாக்கு, வேதாந்தப் பேச்சு & திடீர் விரயம்)",
    "house_title_en": "2nd House - Dhana Bhava (Laconic Truth, Vedantic Speech & Detached Wealth)",
    "core_traits_ta": [
      "குறைத்துப் பேசும் சுபாவம்; ஆனால் பேசும் வார்த்தைகளில் ஆழமான உண்மையும், வேதாந்த தத்துவமும் நிறைந்திருக்கும்.",
      "பணத்தின் மீது அளவுகடந்த ஆசை இல்லாத பற்றற்ற மனப்பான்மை; தேவைக்கேற்ற செல்வத்தை மட்டுமே நாடுவார்.",
      "குடும்பத்தில் சில சமயம் முரண்பாடுகளும், அமைதியின்மையும் வரலாம்; பொறுமை காப்பது நலம்.",
      "பழைய நூல்கள், ரகசிய சாஸ்திரங்கள் மற்றும் ஆன்மீக விஷயங்களை கற்பதில் ஆர்வம் காட்டுவார்."
    ],
    "core_traits_en": [
      "Laconic, minimalist speech; speaks with piercing, unvarnished metaphysical truth and philosophical gravity.",
      "Philosophical detachment from money; views material capital as mere transient energy.",
      "Experiences domestic turbulence or emotional distance from family; requires conscious patience.",
      "Avid student of ancient manuscripts, scriptural commentaries, and esoteric metaphysics."
    ],
    "strong_placement_ta": [
      "சுப பலத்துடன் அமையும் போது: ஆன்மீக அறக்கட்டளைகளின் சொத்துகள், திடீர் பூமி தன யோகம், வாக்கு பலிதம்.",
      "பேச்சையே தர்ம வழியில் பயன்படுத்தி பல்லாயிரக்கணக்கான மக்களின் வாழ்வை நல்வழிப்படுத்துவார்."
    ],
    "strong_placement_en": [
      "Well-placed with benefics: Stewardship over sacred trust estates, unexpected legacy landholdings, and prophetic speech.",
      "Deploys speech to illuminate and counsel thousands onto the path of righteousness."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: பேச்சில் கடுமை, வாக்கு தவறுகை, தவறான முதலீடுகளால் திடீர் இழப்பு.",
      "வலது கண்ணில் பார்வைக் குறைபாடு, பல் வியாதிகள் அல்லது நாக்கில் புண்கள் வரலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Biting, harsh speech; broken financial commitments, and sudden capital erosion.",
      "Prone to right-eye vision impairments, dental decay, and lingual ulcerations."
    ],
    "career_wealth_ta": [
      "ஆன்மீகப் பேச்சாளர், மத தத்துவ நூலாசிரியர், தொல்பொருள் ஆய்வாளர், இயற்கை மூலிகை வர்த்தகம், ஜோதிடர்.",
      "நேர்மையான ஆலோசனைகளாலும் ஆன்மீகப் பணிகளாலும் நிலையான வருவாய்."
    ],
    "career_wealth_en": [
      "Thrives as philosophical lecturer, scriptural author, epigraphist, herbal medicines trader, and astrologer.",
      "Steady livelihood derived from scholarly consultancy and ethical services."
    ],
    "health_precautions_ta": [
      "தொண்டை வறட்சி, நாக்கில் புண்கள், பற்கள் ஆடுதல், வலது கண் பார்வை மங்குதல் மற்றும் வாய் துர்நாற்றம்.",
      "வாய் சுகாதாரத்தைப் பேணுதலும், மிதமான மூலிகைக் குடிநீர் அருந்துவதும் நலம் பயக்கும்."
    ],
    "health_precautions_en": [
      "Susceptible to pharyngeal dryness, oral ulcers, dental cavities, and right-eye optic strain.",
      "Strict oral hygiene, saline gargling, and organic herbal teas promote throat comfort."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 102) & Saravali Ch. 30"
  },
  {
    "planet": "Ketu",
    "planet_name_ta": "கேது",
    "symbol": "☄️",
    "element": "மோட்சம் / நெருப்பு",
    "house": 3,
    "bhava_category": "upachaya",
    "house_title_ta": "3-ஆம் பாவம் - சகஜ பாவம் (அசாத்திய ஆன்மீக தைரியம், வெற்றி & ஞான வீரியம்)",
    "house_title_en": "3rd House - Sahaja Bhava (Spiritual Valour, Upachaya Triumph & Mystical Enterprise)",
    "core_traits_ta": [
      "கேது 3-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமைவது ஜாதகருக்கு இமாலய ஆன்மீக தைரியத்தையும், வெற்றிகளையும் தரும் சிறந்த அமைப்பாகும்.",
      "எந்தவிதமான சோதனைகளையும் துணிவுடன் தாங்கி வெல்லும் ஆற்றல்; எதிரிகளைத் தன் அமைதியாலும் ஞானத்தாலும் வீழ்த்துவார்.",
      "எழுத்தாற்றல், ஆன்மீகக் கட்டுரைகள் மற்றும் தத்துவ நூல்களை இயற்றுவதில் அசாத்திய திறமை படைத்திருப்பார்.",
      "இளைய சகோதரர்களிடம் சற்று பற்றற்ற உறவு இருக்கலாம்; ஆனால் அவர்களுக்குத் தேவையான நன்மைகளைச் செய்வார்."
    ],
    "core_traits_en": [
      "Ketu in the 3rd (an Upachaya house) is classically venerated as a powerhouse of fearless spiritual fortitude and triumph.",
      "Possesses indomitable resilience in the face of worldly crises; disarms adversaries through serene detachment.",
      "Exceptional literary talent for penning profound metaphysical treatises, esoteric essays, and poetry.",
      "Maintains an emotionally detached yet supportive dynamic with younger siblings."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: சர்வதேசப் புகழ் பெற்ற ஆன்மீக எழுத்தாளர், தத்துவ மாமேதை, நாடெங்கும் வெற்றி.",
      "எடுத்த ஆன்மீக முயற்சிகள் யாவும் அமோக வெற்றி பெற்று சரித்திரத்தில் அழியாத பொற்பெயர் பெறும்."
    ],
    "strong_placement_en": [
      "Exalted or well-placed: Internationally acclaimed spiritual author, philosophical savant, and conqueror of inner faculties.",
      "Pioneering metaphysical works achieve global recognition and timeless literary honors."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: சகோதரர்களுடன் கருத்து வேறுபாடுகள், கைகளில் நரம்பு வலி.",
      "காரணமற்ற பயமும் தயக்கமும் முயற்சிகளில் சுணக்கத்தை ஏற்படுத்தலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Bitter sibling misunderstandings, brachial nerve inflammation, and upper limb numbness.",
      "Paralyzing self-doubt and pessimistic procrastination sabotaging creative initiatives."
    ],
    "career_wealth_ta": [
      "ஆன்மீக வெளியீட்டாளர், தத்துவ ஆசிரியர், யோகா பயிற்சியாளர், சர்வதேச தொண்டு நிறுவனம், ஆயுர்வேத மருத்துவம்.",
      "எழுத்து, அறிவுரை மற்றும் தர்ம காரியங்கள் மூலம் கௌரவமான செல்வச் சேர்க்கை."
    ],
    "career_wealth_en": [
      "Dominant in spiritual publishing, philosophical pedagogy, yoga instruction, humanitarian trusts, and Ayurvedic medicine.",
      "Substantial capital accumulated through intellectual consulting, royalties, and philanthropic syndicates."
    ],
    "health_precautions_ta": [
      "தோள்பட்டை வலி, கைகளில் நரம்புத் தளர்ச்சி, காது கேளாமை மற்றும் விரல் நடுக்கம்.",
      "முறையான யோகாசனங்களும், உடற்பயிற்சியும் உடலை ஆரோக்கியமாக வைத்திருக்கும்."
    ],
    "health_precautions_en": [
      "Prone to shoulder stiffness, brachial plexus neuralgia, auditory dullness, and finger muscular tremors.",
      "Yogic asanas and upper quadrant stretching optimize neuromuscular flexibility."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 142) & Saravali Ch. 30"
  },
  {
    "planet": "Ketu",
    "planet_name_ta": "கேது",
    "symbol": "☄️",
    "element": "மோட்சம் / நெருப்பு",
    "house": 4,
    "bhava_category": "kendra",
    "house_title_ta": "4-ஆம் பாவம் - சுக பாவம் (ஆன்மீக இல்லம், தாயன்பில் பக்குவம் & ஆத்ம சாந்தி)",
    "house_title_en": "4th House - Sukha Bhava (Spiritual Home, Maternal Stoicism & Inner Solace)",
    "core_traits_ta": [
      "வீட்டில் எப்போதும் ஆன்மீகச் சூழல், அமைதி, தியான அறை மற்றும் பூஜைகள் நிறைந்திருக்கும்.",
      "தாயாரின் மீது ஆழ்ந்த பக்தி; தாயார் பக்குவமான ஆன்மீகப் பெண்ணாக விளங்கி நல்வழிகாட்டுவார்.",
      "ஆடம்பர மாளிகைகளை விட இயற்கை எழில் கொஞ்சும் அமைதியான கிராமப்புறங்களில் வசிப்பதில் விருப்பம்.",
      "மனதில் பூரண ஆத்ம சாந்தியும், உலக இன்பங்களை விட ஆன்மீக விடுதலையை நோக்கிய தீவிர பயணமும் இருக்கும்."
    ],
    "core_traits_en": [
      "Transforms the domestic home into a tranquil spiritual sanctuary, complete with meditation rooms and daily worship.",
      "Deep devotion to a stoic, spiritually enlightened mother who serves as primary moral guide.",
      "Prefers rustic country homes, hermitage retreats, and nature sanctuaries over ostentatious city mansions.",
      "Harbors deep inner solace, prioritizing spiritual emancipation (Moksha) above transient sensory pleasures."
    ],
    "strong_placement_ta": [
      "சுப பலத்துடன் இருப்பின்: ஆன்மீக ஆசிரமங்கள், தியான மையங்கள், அமைதியான இல்லற சுகம்.",
      "பூர்வீகச் சொத்துகள் தடையின்றி வந்து சேரும்; சமுதாயத்தில் உன்னத ஞானியாகப் போற்றப்படுவார்."
    ],
    "strong_placement_en": [
      "Well-placed with benefics: Founds renowned spiritual ashrams and meditation sanctuaries; deep domestic harmony.",
      "Smoothly inherits ancestral heritage properties; universally revered as an enlightened householder-sage."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தாயாரின் உடல்நலக்குறைவு, பூர்வீக சொத்துகளில் தகராறுகள்.",
      "வீடு மற்றும் வாகனங்களால் எதிர்பாராத நஷ்டங்கள் மற்றும் மன அமைதியின்மை ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Maternal health frailties, disputes over ancestral lands, and domestic discontent.",
      "Financial drain from recurring property maintenance and vehicles; persistent heart palpitations."
    ],
    "career_wealth_ta": [
      "ஆன்மீக ஆசிரம நிர்வாகம், இயற்கை விவசாயம், மூலிகைப் பண்ணைகள், நில அளவையாளர், ஆயுர்வேத மருந்து தயாரிப்பு.",
      "பூமி பரிவர்த்தனைகளாலும் ஆன்மீக சேவைகளாலும் நிலையான சொத்துக்கள் சேரும்."
    ],
    "career_wealth_en": [
      "Flourishes in ashram administration, organic permaculture, medicinal herbal farming, land survey, and Ayurveda.",
      "Steady capital accumulation through real estate preservation and holistic institutional assets."
    ],
    "health_precautions_ta": [
      "நெஞ்சு சளி, இருதய பலவீனம், ஆஸ்துமா, மூட்டு வலி மற்றும் மன அழுத்தம்.",
      "சூடான மூலிகைக் குடிநீரும், பிராணாயாமப் பயிற்சிகளும் நுரையீரல் நலனைக் காக்கும்."
    ],
    "health_precautions_en": [
      "Susceptible to bronchial asthma, cardiac rhythm irregularities, joint stiffness, and melancholic anxiety.",
      "Warm herbal decoctions, breathwork pranayama, and dwelling in clean rural air preserve health."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 176) & Saravali Ch. 30"
  },
  {
    "planet": "Ketu",
    "planet_name_ta": "கேது",
    "symbol": "☄️",
    "element": "மோட்சம் / நெருப்பு",
    "house": 5,
    "bhava_category": "trikona",
    "house_title_ta": "5-ஆம் பாவம் - பூர்வ புண்ணியம் (மகா ஞானம், மந்திர சித்தி & ஆன்மீக சந்ததிகள்)",
    "house_title_en": "5th House - Putra Bhava (Supreme Gnosis, Mantra Siddhi & Spiritual Progeny)",
    "core_traits_ta": [
      "கேது 5-ஆம் பாவத்தில் அமர்வது முற்பிறவி புண்ணியத்தின் வெளிப்பாடாகும்; அசாத்தியமான ஆன்மீக ஞானம் கிட்டும்.",
      "மந்திர சாஸ்திரங்கள், தியானம், காயத்ரி ஜபம் மற்றும் வேதங்களை எளிதில் கிரகிக்கும் ஆற்றல் உண்டு.",
      "புத்திர பாக்கியத்தில் ஆரம்பத்தில் சில காலதாமதம் இருந்தாலும், பிற்காலத்தில் குழந்தைகள் சிறந்த ஆன்மீகவாதிகளாகத் திகழ்வர்.",
      "பங்குச் சந்தை போன்ற ஊக வணிகங்களைத் தவிர்த்து, தர்ம காரியங்களில் மட்டுமே ஈடுபடுவார்."
    ],
    "core_traits_en": [
      "Ketu in the 5th signifies ripe fruits of past-life spiritual merit (Poorvapunya); unlocks transcendent gnosis.",
      "Effortless mastery of sacred mantras, esoteric meditation, Gayatri japa, and scriptural comprehension.",
      "Progeny may experience initial delays; children mature into highly moral, spiritually elevated souls.",
      "Completely shuns speculative gambling, dedicating mental energy to intellectual and charitable causes."
    ],
    "strong_placement_ta": [
      "சுப பலத்துடன் அமையும் போது: மந்திர சித்தி பெற்ற மகா ஞானி, வேதாந்தப் பேராசிரியர், சர்வதேச விருதுகள்.",
      "குழந்தைகள் ஆன்மீகத்திலும் கல்வியிலும் உலகப் புகழ் பெறுவார்கள்; முன்னோர்களின் புண்ணியத்தால் யோக வாழ்வு."
    ],
    "strong_placement_en": [
      "Well-placed with benefics: Realizes authentic Mantra Siddhi, celebrated professor of philosophy and Vedanta.",
      "Progeny attain global renown for intellectual and spiritual purity; lives under the protection of divine grace."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: புத்திர பாக்கியத்தில் கடும் தடைகள், கருச்சிதைவு அபாயம்.",
      "தவறான நிதித் திட்டங்களால் சேமிப்பு விரயமாதல் மற்றும் மன அமைதியின்மை."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Acute delays in childbearing, miscarriages, and persistent worry regarding progeny.",
      "Financial drain from ill-considered schemes and dogmatic philosophical rigidity."
    ],
    "career_wealth_ta": [
      "வேதாந்த ஆசிரியர், ஜோதிட ஆராய்ச்சியாளர், சமஸ்கிருதப் பேராசிரியர், அறக்கட்டளை நிர்வாகி, இயற்கை மருத்துவர்.",
      "அறிவுசார் படைப்புகளாலும் ஆன்மீக ஆலோசனைகளாலும் கௌரவமான செல்வச் சேர்க்கை."
    ],
    "career_wealth_en": [
      "Distinction as Vedanta professor, astrological research director, Sanskrit scholar, trust manager, and naturopath.",
      "Generates honorable wealth via book royalties, educational endowments, and institutional consultancy."
    ],
    "health_precautions_ta": [
      "அஜீரணம், வயிற்றில் வாயுத் தொல்லை, குடல் புண்கள், அமிலத்தன்மை மற்றும் உணவு ஒவ்வாமை.",
      "இயற்கையான சத்தான உணவுகளை உட்கொள்ளுதலும், நச்சு உணவுகளைத் தவிர்ப்பதும் அவசியம்."
    ],
    "health_precautions_en": [
      "Prone to nervous dyspepsia, gastrointestinal bloating, peptic ulcers, and food sensitivities.",
      "Adopt simple, easily digestible sattvic foods and avoid irregular meal schedules."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 222) & Saravali Ch. 30"
  },
  {
    "planet": "Ketu",
    "planet_name_ta": "கேது",
    "symbol": "☄️",
    "element": "மோட்சம் / நெருப்பு",
    "house": 6,
    "bhava_category": "dusthana",
    "house_title_ta": "6-ஆம் பாவம் - சத்ரு பாவம் (பகைவர்களை வெல்லுதல் / மகா உபசய பலம் & சேவை)",
    "house_title_en": "6th House - Satru Bhava (Vanquishing Opposition, Upachaya Strength & Selfless Service)",
    "core_traits_ta": [
      "கேது 6-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமர்வது ஜாதகருக்கு இமாலய பலத்தையும், அசைக்க முடியாத சத்ரு ஜெயத்தையும் தரும்.",
      "எதிரிகள், வழக்குகள் மற்றும் கடன் தொல்லைகளைத் தன் பற்றற்ற தன்மையாலும் விவேகத்தாலும் எளிதில் முறியடிப்பார்.",
      "இரும்பு போன்ற நோய் எதிர்ப்புச் சக்தி; எந்தவிதமான நோய்களிலிருந்தும் இயற்கை மருத்துவத்தால் மீண்டு வருவார்.",
      "எளிய மக்களுக்கும், ஆதரவற்றோருக்கும் சேவை செய்வதில் பேரானந்தம் அடைவார்."
    ],
    "core_traits_en": [
      "Ketu in the 6th (an Upachaya house) is classically celebrated as an invincible fortress of resilience and triumph.",
      "Overcomes all adversaries, litigations, and debts through fearless equanimity and intellectual detachment.",
      "Possesses robust physiological immunity, recovering swiftly from illness via holistic therapies.",
      "Derives profound personal fulfillment from humble, selfless service to marginalized and suffering souls."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: சத்ரு சம்ஹார யோகம்! எதிரிகள் இல்லா பெருவாழ்வு, மருத்துவத் துறையில் உயர் அதிகாரம்.",
      "அளப்பரிய செல்வம், கடன் இல்லாத அமைதியான வாழ்க்கை மற்றும் அனைத்துப் போட்டிகளிலும் தொடர் வெற்றி."
    ],
    "strong_placement_en": [
      "Exalted or well-placed: Bestows complete Shatru Samhara Yoga! Total elimination of foes, heads healthcare commissions.",
      "Immense accumulated wealth, unassailable physical vitality, and perpetual competitive victories."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: மர்ம நோய்கள், தோல் அலர்ஜி, பூச்சிக்கடி, கடன் தொல்லைகள்.",
      "வேலையாட்களால் ஏமாற்றப்படுதலும், தாய்மாமனுடன் கருத்து மோதல்களும் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Baffling immune disorders, chronic dermatitis, insect venom reactions, and debt worries.",
      "Deceit by domestic servants and strained relations with maternal relatives."
    ],
    "career_wealth_ta": [
      "இயற்கை மருத்துவம், ஆயுர்வேத கிளினிக், தொண்டு நிறுவனங்கள், குற்றவியல் வழக்கறிஞர், பொது சுகாதாரம், கால்நடை மருத்துவர்.",
      "சேவை மனப்பான்மையாலும் நேர்மையான உழைப்பாலும் நிலையான வருமானம்."
    ],
    "career_wealth_en": [
      "Thrives in naturopathy, Ayurvedic hospital ownership, philanthropic relief agencies, public health, and veterinary medicine.",
      "Earns stable revenues by serving community health and institutional welfare."
    ],
    "health_precautions_ta": [
      "குடல் அழற்சி, நரம்புத் தளர்ச்சி, சரும நோய்கள், ஆஸ்துமா மற்றும் மலச்சிக்கல்.",
      "நார்ச்சத்து மிகுந்த காய்கறிகளையும் பழங்களையும் உண்பதும், தோலை சுத்தமாகப் பராமரிப்பதும் நலம் தரும்."
    ],
    "health_precautions_en": [
      "Susceptible to colitis, nervous exhaustion, eczema, bronchial allergies, and chronic constipation.",
      "High-fiber dietary regimen, probiotics, and dermatological care are essential."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 1, p. 262) & Saravali Ch. 30"
  },
  {
    "planet": "Ketu",
    "planet_name_ta": "கேது",
    "symbol": "☄️",
    "element": "மோட்சம் / நெருப்பு",
    "house": 7,
    "bhava_category": "kendra",
    "house_title_ta": "7-ஆம் பாவம் - களத்திர பாவம் (பக்குவமான ஆன்மீகத் துணை & பற்றற்ற தாம்பத்தியம்)",
    "house_title_en": "7th House - Kalathra Bhava (Ascetic Spiritual Spouse & Detached Matrimony)",
    "core_traits_ta": [
      "ஆன்மீக நாட்டம், பக்குவம், அமைதி மற்றும் எளிய வாழ்க்கை முறையைக் கொண்ட வாழ்க்கைத் துணை அமைவார்.",
      "தாம்பத்தியத்தில் உடல் கவர்ச்சியை விட மனரீதியான புரிதலும், ஆன்மீக நட்பும் மேலோங்கி நிற்கும்.",
      "திருமண வாழ்வில் ஈகோ மோதல்கள் வராமல் பரஸ்பர மரியாதையுடன் நடந்து கொள்வது அமைதி தரும்.",
      "கூட்டு வர்த்தகத்தில் யாரையும் அளவுக்கு அதிகமாக நம்பாமல் வெளிப்படைத்தன்மையுடன் இருப்பது நல்லது."
    ],
    "core_traits_en": [
      "Blessed with a deeply spiritual, stoic, modest, and philosophically inclined spouse.",
      "Matrimonial bond is anchored in soul communion and mutual respect rather than sensory indulgence.",
      "Requires conscious avoidance of emotional coldness to nurture warmth in domestic companionship.",
      "Must practice formal contractual diligence and avoid naive credulity in commercial partnerships."
    ],
    "strong_placement_ta": [
      "சுப பலத்துடன் அமைந்தால்: உன்னத ஆன்மீகக் குடும்பத் துணை, இல்லறத்தில் பூரண அமைதி, தெய்வீக தம்பதிகள்.",
      "பன்னாட்டு அமைப்புகளிலும், ஆன்மீக அறக்கட்டளைகளிலும் மாபெரும் நற்பெயரும் யோகமும் கிட்டும்."
    ],
    "strong_placement_en": [
      "Well-placed with benefics: Partner hails from an esteemed spiritual family; sublime peace in domestic life.",
      "Attains high honors in international charitable foundations, celebrated as an exemplary divine couple."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: திருமண வாழ்வில் கருத்து வேறுபாடுகள், தற்காலிகப் பிரிவு, துணையின் ஆரோக்கியக் குறைவு.",
      "கூட்டுத் தொழிலில் பங்குதாரர்களால் ஏமாற்றப்பட்டு நிதி இழப்புகள் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Marital estrangement, emotional distance causing trial separation, spousal health trials.",
      "Heavy financial losses through unprincipled business partners and breach of trust."
    ],
    "career_wealth_ta": [
      "ஆன்மீக ஆசிரமங்கள், மாற்று மருத்துவம், தொண்டு நிறுவனங்கள், சட்ட சமரசம், புத்தக வெளியீடு.",
      "வாழ்க்கைத் துணையின் ஆலோசனைகளாலும் ஆன்மீகப் பணிகளாலும் கௌரவமான தன சேர்க்கை."
    ],
    "career_wealth_en": [
      "Dominant in spiritual ashrams, alternative medicine, philanthropic trusts, legal mediation, and publishing.",
      "Steady livelihood augmented through spousal frugality and ethical institutional assets."
    ],
    "health_precautions_ta": [
      "சிறுநீரகக் கோளாறுகள், அடிவயிற்று வலி, பாலியல் பலவீனம் மற்றும் ஒவ்வாமை.",
      "முறையான நீர் அருந்துதலும், தனிநபர் சுகாதாரமும் நலம் காக்கும்."
    ],
    "health_precautions_en": [
      "Susceptible to renal sluggishness, pelvic aching, reproductive fatigue, and systemic allergies.",
      "Abundant warm hydration, strict personal hygiene, and periodic urological checkups."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Ketu",
    "planet_name_ta": "கேது",
    "symbol": "☄️",
    "element": "மோட்சம் / நெருப்பு",
    "house": 8,
    "bhava_category": "dusthana",
    "house_title_ta": "8-ஆம் பாவம் - ஆயுள் பாவம் (ரகசிய சித்திகள் / உள்ளுணர்வு & எதிர்பாராத ஆன்மீக யோகம்)",
    "house_title_en": "8th House - Ayur Bhava (Mystical Siddhis, Piercing Intuition & Sudden Spiritual Awakening)",
    "core_traits_ta": [
      "கேது 8-ஆம் பாவத்தில் அமைவது அசாத்தியமான உள்ளுணர்வையும், மறைபொருள் சித்திகளையும் தரும் அமைப்பாகும்.",
      "கனவுகள் பலிக்கும் ஆற்றல், எதிர்காலத்தை முன்கூட்டியே உணரும் நுண்ணறிவு, மந்திர-தந்திர சாஸ்திரங்களில் தேர்ச்சி.",
      "ஆபத்தான விபத்துகள் மற்றும் நெருக்கடிகளிலிருந்து கண்ணுக்குத் தெரியாத தெய்வ சக்தியால் காப்பாற்றப்படுவார்.",
      "மனைவி வழியில் பழைய நிலங்கள், உயில் சொத்துகள் அல்லது காப்பீட்டுத் தொகைகள் வந்து சேரும்."
    ],
    "core_traits_en": [
      "Ketu in the 8th endows extraordinary intuitive perception, prophetic dream visions, and esoteric occult mastery.",
      "Prophetic premonitions; pierces through illusions to discern future trajectories with uncanny precision.",
      "Miraculously safeguarded from catastrophic accidents and physical perils by unseen divine forces.",
      "Inherits unearned ancestral lands, insurance annuities, and testamentary estates through marital ties."
    ],
    "strong_placement_ta": [
      "விருச்சிகத்தில் ஆட்சி அல்லது தனுசில் பலம் பெற்றால்: குண்டலினி யோக சித்தி, ஆன்மீக முக்தி, பல நூறு கோடி உயில் சொத்துகள்.",
      "மறைமுக சாஸ்திரங்களில் மாமேதையாகத் திகழ்ந்து சமுதாயத்தில் உயர்ந்த வழிகாட்டியாக வாழ்வார்."
    ],
    "strong_placement_en": [
      "In own sign Scorpio or exalted in Sagittarius: Awakened Kundalini Siddhis, profound Moksha, and vast legacies.",
      "Revered as an enlightened master of occult metaphysics, guiding advanced spiritual aspirants."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: மூல நோய், ஆசனவாய் வெடிப்பு, தீராத வாத நோய்கள், விபத்துகள்.",
      "உயில் விவகாரங்களில் வழக்குகளும், அரசாங்க அபராதங்களால் மன உளைச்சலும் ஏற்படலாம்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Severe hemorrhoids, anal fissures, chronic rheumatoid disorders, and accidental injuries.",
      "Protracted probate disputes over contested inheritances and government tax scrutiny."
    ],
    "career_wealth_ta": [
      "ஜோதிட ஆராய்ச்சி, சித்த மருத்துவம், தொல்பொருள் ஆராய்ச்சி, தடயவியல், ஆயுள் காப்பீடு, ரகசிய நிதி ஆலோசகர்.",
      "உயில் சொத்துகள், காப்பீட்டு முதிர்வுகள் மற்றும் திடீர் தன வரவால் பெருஞ்செல்வம்."
    ],
    "career_wealth_en": [
      "Distinguished in astrological research, Siddha pharmacology, archaeology, forensic pathology, and private wealth office.",
      "Substantial capital influx via testamentary bequests, insurance settlements, and confidential contracts."
    ],
    "health_precautions_ta": [
      "மூல நோய் (Piles), ஆசனவாய் புண்கள், நரம்பு வலி, விஷக்கடி மற்றும் தூக்கமின்மை.",
      "நார்ச்சத்து மிகுந்த உணவுகளையும், எண்ணெய் மசாஜ்களையும் தவறாமல் எடுத்துக்கொள்ள வேண்டும்."
    ],
    "health_precautions_en": [
      "Vulnerable to hemorrhoidal inflammation, anal fissures, peripheral neuropathy, toxic stings, and insomnia.",
      "High-fiber cooling diet, warm sitz baths, and avoiding sedentary stagnation protect health."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Ketu",
    "planet_name_ta": "கேது",
    "symbol": "☄️",
    "element": "மோட்சம் / நெருப்பு",
    "house": 9,
    "bhava_category": "trikona",
    "house_title_ta": "9-ஆம் பாவம் - பாக்கிய பாவம் (தர்ம ஞானம், பரம பக்தி & ஆன்மீக யாத்திரை)",
    "house_title_en": "9th House - Bhagya Bhava (Dharmic Gnosis, Sublime Devotion & Sacred Pilgrimages)",
    "core_traits_ta": [
      "கேது 9-ஆம் பாவத்தில் அமைவது உன்னதமான தர்ம சிந்தனையையும், இறைவனின் மீது எல்லை இல்லாத பக்தியையும் தரும்.",
      "புனிதத் தலங்களுக்கு யாத்திரை செல்வதிலும், மலைக் குகைகளில் தியானம் செய்வதிலும் பேரானந்தம் அடைவார்.",
      "தந்தையின் மீது பக்தி; தந்தையிடமிருந்து ஆன்மீக நற்குணங்களையும் தர்ம வழிகளையும் கற்றுத் தேர்ந்திருப்பார்.",
      "வாழ்க்கையில் உலக ஆசைகளைக் கடந்து ஆத்ம ஞானத்தை அடைவதே இவரின் தலையாய லட்சியமாக இருக்கும்."
    ],
    "core_traits_en": [
      "Ketu in the 9th inspires pristine ethical nobility, deep scriptural piety, and boundless devotional love.",
      "Passionate love for pilgrimages to sacred mountain hermitages, remote river confluences, and ancient temples.",
      "Reverent bond with a noble, spiritually awakened father whose ethical legacy guides life decisions.",
      "Prioritizes the realization of Self-knowledge (Atma Jnana) above all ephemeral worldly accolades."
    ],
    "strong_placement_ta": [
      "சுப பலத்துடன் அமைந்தால்: அகண்ட தர்ம யோகம், சர்வதேச ஆன்மீக பீடாதிபதி, அரச குடும்பங்களின் கௌரவம்.",
      "வேத பாடசாலைகளையும், ஆசிரமங்களையும் நிறுவி உலகெங்கும் லட்சக்கணக்கான மக்களுக்கு வழிகாட்டுவார்."
    ],
    "strong_placement_en": [
      "Well-placed with benefics: Supreme Dharma Yoga! Revered as an international pontiff and saintly advisor to statesmen.",
      "Founds monumental Vedic academies and ashrams, guiding hundreds of thousands onto the path of liberation."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தந்தையின் உடல்நலக்குறைவு, மத நம்பிக்கைகளில் முரண்பாடுகள்.",
      "புனிதப் பயணங்களில் பொருள் இழப்பு அல்லது ஏமாற்றங்கள் ஏற்பட வாய்ப்புண்டு."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Paternal health difficulties, cynicism towards institutional priesthood, and travel hassles.",
      "Loss of baggage or financial disappointment during sacred pilgrimages."
    ],
    "career_wealth_ta": [
      "மத அறக்கட்டளைத் தலைவர், பல்கலைக்கழக வேந்தர், ஆன்மீக நூலாசிரியர், தொண்டு நிறுவனங்கள், இயற்கை மருத்துவம்.",
      "தர்ம வழியில் சேர்க்கும் வற்றாத செல்வமும், பரம்பரைச் சொத்துகளும் நிலைத்து நிற்கும்."
    ],
    "career_wealth_en": [
      "Commands high status as religious trust president, university chancellor, spiritual author, and humanitarian trustee.",
      "Pure, untainted wealth accrued through principled educational licensing and ethical donations."
    ],
    "health_precautions_ta": [
      "தொடைப் பகுதியில் நரம்பு வலி, இடுப்பு வாதம் (Sciatica), உடல் சோர்வு மற்றும் செரிமானக் கோளாறுகள்.",
      "மிதமான நடைப்பயிற்சியும் சாத்வீக உணவு முறையும் உடல்நலனைப் பேணும்."
    ],
    "health_precautions_en": [
      "Susceptible to hip stiffness, sciatica sensitivity, and intermittent physical fatigue.",
      "Gentle walking outdoors and a nourishing sattvic diet preserve long-term vitality."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Ketu",
    "planet_name_ta": "கேது",
    "symbol": "☄️",
    "element": "மோட்சம் / நெருப்பு",
    "house": 10,
    "bhava_category": "kendra",
    "house_title_ta": "10-ஆம் பாவம் - ஜீவன பாவம் (தர்ம தொழில், ஆன்மீக தலைமை & பற்றற்ற சாதனை)",
    "house_title_en": "10th House - Karma Bhava (Dharmic Career, Spiritual Leadership & Selfless Achievement)",
    "core_traits_ta": [
      "தொழிலில் நேர்மை, தர்ம நெறி தவறாமை, லஞ்ச-ஊழலை அடியோடு வெறுக்கும் உன்னதமான சுபாவம்.",
      "பதவி, அதிகாரம் ஆகியவற்றை விட சமுதாயத்திற்கு நல்ல சேவை செய்வதையே தன் கடமையாகக் கருதுவார்.",
      "அரசாங்க உயர் அதிகாரிகளுடனும் மக்கள் மத்தியிலும் சிறந்த நற்பெயரும், மரியாதையும் பெறுவார்.",
      "தொழிலில் சில சமயம் எதிர்பாராத மாற்றங்களும், ஆன்மீகத்தை நோக்கித் திரும்பும் சூழலும் உருவாகலாம்."
    ],
    "core_traits_en": [
      "Impeccable occupational integrity; steadfastly rejects corruption, deceit, or underhanded shortcuts.",
      "Views professional career as a sacred service (Seva) to society rather than a vehicle for selfish aggrandizement.",
      "Commands profound respect and moral authority among civic regulators, peers, and the public.",
      "May experience sudden vocational transitions, redirecting professional acumen towards spiritual or humanitarian frontiers."
    ],
    "strong_placement_ta": [
      "சுப பலத்துடன் அமைந்தால்: தலைமை நீதிபதி, ஆன்மீக நிறுவனங்களின் தலைவர், அரசாங்க கௌரவப் பதவிகள்.",
      "நாட்டின் முதன்மை அறக்கட்டளைகள் மற்றும் தொண்டு சாம்ராஜ்யத்தை வழிநடத்தி அழியாத புகழ் பெறுவார்."
    ],
    "strong_placement_en": [
      "Well-placed with benefics: Supreme Court justice, director of premier spiritual foundations, or cabinet counselor.",
      "Presides over monumental philanthropic trusts, immortalized as an unblemished public servant."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: தொழிலில் அடிக்கடி மாற்றங்கள், உயர் அதிகாரிகளுடன் கருத்து மோதல்கள்.",
      "தொழிலில் நேர்மையாக இருந்தும் அவப்பெயர் உண்டாக வாய்ப்புண்டு."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Frequent erratic job switches, friction with autocratic superiors, and professional disillusionment.",
      "Unmerited public scrutiny despite transparently honest intentions."
    ],
    "career_wealth_ta": [
      "நீதித்துறை, இயற்கை மருத்துவம், தொண்டு நிறுவனங்கள், தொல்பொருள் ஆராய்ச்சி, ஆன்மீக மடங்கள், சமூக சேவை.",
      "நேர்மையான உழைப்பாலும் சேவைகளாலும் நிலையான தன வரவு."
    ],
    "career_wealth_en": [
      "Flourishes in the judiciary, naturopathic healthcare, philanthropic trusts, epigraphy, and community welfare.",
      "Steady, secure income built upon principled public service and administrative competence."
    ],
    "health_precautions_ta": [
      "பணிச்சுமையால் மூட்டு வலி, ரத்த அழுத்தம், தூக்கமின்மை மற்றும் வாதக் கோளாறுகள்.",
      "வேலைக்கு நடுவே தியானமும், ஓய்வும் எடுப்பது ஆரோக்கியத்தைப் பாதுகாக்கும்."
    ],
    "health_precautions_en": [
      "Occupational stress, knee joint stiffness, hypertension, and sleep deprivation.",
      "Structured meditation, daily exercise, and portion control maintain executive health."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Ketu",
    "planet_name_ta": "கேது",
    "symbol": "☄️",
    "element": "மோட்சம் / நெருப்பு",
    "house": 11,
    "bhava_category": "upachaya",
    "house_title_ta": "11-ஆம் பாவம் - லாப பாவம் (அகண்ட தன லாபம் / பற்றற்ற வருவாய் & ஆன்மீக நட்பு)",
    "house_title_en": "11th House - Labha Bhava (Massive Inflows, Wish Fulfillment & Ascetic Allies)",
    "core_traits_ta": [
      "கேது 11-ஆம் பாவத்தில் (உபசய ஸ்தானம்) அமைவது ஜாதகருக்கு அளப்பரிய செல்வத்தையும், தொடர் லாபங்களையும் தரும் மிகச்சிறந்த யோகமாகும்.",
      "எடுத்த காரியங்கள் யாவும் எளிதில் நிறைவேறும்; பல வழிகளிலிருந்து வற்றாத நிதி வரவு வந்துகொண்டே இருக்கும்.",
      "ஆன்மீக மகான்கள், சித்தர்கள், தத்துவ ஞானிகள் மற்றும் செல்வந்தர்களின் உயர்ந்த நட்பு வட்டம் அமையும்.",
      "மூத்த சகோதரர்களிடம் அன்பான உறவும், அதே சமயம் சுதந்திரமான மனப்பான்மையும் நிலவும்."
    ],
    "core_traits_en": [
      "Ketu in the 11th (an Upachaya house) is one of the most prolific placements for effortless financial accumulation.",
      "Frictionless fulfillment of cherished goals; unceasing multi-channel cash streams flood his accounts.",
      "Surrounded by a high-minded circle of enlightened yogis, philosophers, philanthropists, and magnates.",
      "Harmonious camaraderie with elder siblings combined with mutual intellectual independence."
    ],
    "strong_placement_ta": [
      "ஆட்சி அல்லது உச்சம் பெற்றால்: பல நூறு கோடி மதிப்பிலான சொத்துகள், அறக்கட்டளைகள், குபேர யோகம்.",
      "அறக்கட்டளைகளை நிறுவி பல்லாயிரக்கணக்கான ஏழை எளியவர்களுக்கு வாழ்வளிக்கும் மகா வள்ளலாகத் திகழ்வார்."
    ],
    "strong_placement_en": [
      "Exalted or in own house: Bestows multi-million dollar asset portfolios, charitable foundations, and supreme Kubera Yoga.",
      "Acts as a legendary philanthropist, establishing university scholarships, hospitals, and heritage restorations."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: நண்பர்களால் ஏமாற்றப்பட்டு தன நஷ்டம், மூத்த சகோதரருடன் பிரிவு.",
      "லாபங்கள் கைநழுவுதல் அல்லது பண விரயங்களால் கடன்கள் ஏற்படுதல்."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Exploitation by counterfeit associates, capital erosion, and sibling estrangement.",
      "Anticipated dividends vanish through unexpected bureaucratic bottlenecks."
    ],
    "career_wealth_ta": [
      "ஆன்மீக அறக்கட்டளைகள், இயற்கை மூலிகை ஏற்றுமதி, தொண்டு நிறுவன முதலீடுகள், புத்தக பதிப்பகம், மாற்று மருத்துவம்.",
      "முதலீடுகளின் அபரிமிதமான வளர்ச்சியால் சமுதாயத்தின் பெரும் பணக்காரராக உயருதல்."
    ],
    "career_wealth_en": [
      "Lucrative success in spiritual foundations, organic herbal export, philanthropic endowments, and alternative medicine.",
      "Extraordinary capital multiplication placing the native in the elite wealthy tier."
    ],
    "health_precautions_ta": [
      "இடது காது கேளாமை, கணுக்கால் வாதம், தசை இறுக்கம் மற்றும் ரத்த ஓட்டக் குறைபாடுகள்.",
      "கால் நரம்புகளுக்கான உடற்பயிற்சியும், காது ஆரோக்கியத்தைப் பேணுதலும் நல்லது."
    ],
    "health_precautions_en": [
      "Susceptible to left-ear dullness, ankle joint stiffness, and sluggish peripheral circulation.",
      "Daily ankle mobility drills, compression socks for long flights, and otic checkups."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  },
  {
    "planet": "Ketu",
    "planet_name_ta": "கேது",
    "symbol": "☄️",
    "element": "மோட்சம் / நெருப்பு",
    "house": 12,
    "bhava_category": "dusthana",
    "house_title_ta": "12-ஆம் பாவம் - விரய பாவம் (மோட்ச காரகன் தன் சொந்த ஸ்தானத்தில் / பூரண ஜீவன் முக்தி)",
    "house_title_en": "12th House - Vraya & Moksha Bhava (Mokshakaraka in Prime House / Sublime Spiritual Liberation)",
    "core_traits_ta": [
      "மோட்ச காரகனான கேது 12-ஆம் பாவத்தில் அமர்வது மனிதப் பிறவியின் மிக உன்னதமான மோட்ச யோகமாகும் (Kaivalya Moksha).",
      "பிறவிப் பெருங்கடலை நீந்தி இறைவனின் திருவடிகளில் ஐக்கியமாகும் ஜீவன் முக்தி நிலை.",
      "பணத்தை ஆடம்பரங்களுக்கு வீணாக்காமல், கோவில் திருப்பணிகள், தியான மையங்கள் மற்றும் ஆன்மீக காரியங்களுக்குச் செலவிடுவார்.",
      "தனிமையில் தியானம் செய்வதில் பேரானந்தம் அடைவார்; ஆழ்ந்த தூக்கமும், அமைதியான மன நிலையும் நிறைந்திருக்கும்."
    ],
    "core_traits_en": [
      "Mokshakaraka Ketu in the 12th is celebrated as the absolute zenith of spiritual evolution: bestows Kaivalya Moksha.",
      "Attains definitive transcendence from the wheel of samsaric reincarnation, merging into the Divine Light.",
      "Directs worldly wealth exclusively towards temple renovations, secluded hermitages, and spiritual feeding.",
      "Delights in contemplative silence, experiencing ecstatic Samadhi and unperturbed restorative rest."
    ],
    "strong_placement_ta": [
      "விருச்சிகம்/தனுசில் சுப பலத்துடன் இருப்பின்: உலகப் புகழ் பெற்ற ஜீவன் முக்தர், சர்வதேச ஆன்மீக ஆசிரமங்கள், மோட்ச சாதனை.",
      "அயன சயன சுகம் பூரணமாகக் கிட்டும்; சமுதாயத்தில் பெரும் ஞானியாகப் போற்றப்பட்டு சமாதி நிலை எய்துவார்."
    ],
    "strong_placement_en": [
      "Well-placed with benefics: Revered as an authentic Jivanmukta (liberated soul), founding international ashrams.",
      "Enjoys divine peace, celestial dreams, and effortless conscious transition into Supreme Nirvana."
    ],
    "weak_placement_ta": [
      "நீசம் அல்லது பாபக் கிரகங்களின் சேர்க்கை பெற்றால்: கடுமையான தூக்கமின்மை, இடது கண் பார்வை மங்குதல், ஏமாற்றங்கள்.",
      "வீண் விரயங்கள், போலி ஆன்மீகவாதிகளால் பண இழப்பு மற்றும் மன அமைதியின்மை."
    ],
    "weak_placement_en": [
      "Debilitated or afflicted: Severe insomnia, left-eye vision defects, and financial deceit by bogus gurus.",
      "Fruitless financial drainage, loneliness, and persistent melancholic restlessness."
    ],
    "career_wealth_ta": [
      "ஆன்மீக ஆசிரமங்கள், தியான பீடங்கள், யோகா கல்வி நிறுவனங்கள், இயற்கை மருத்துவமனைகள், தொண்டு நிறுவனங்கள்.",
      "வெளிநாட்டு ஆன்மீகக் கொடைகளாலும் அறக்கட்டளைகளாலும் நிறைவான செல்வம்."
    ],
    "career_wealth_en": [
      "Stellar leadership in contemplative monasteries, meditation retreats, yogic universities, and holistic hospices.",
      "Sustained through generous spiritual endowments, book royalties, and international trust funds."
    ],
    "health_precautions_ta": [
      "இடது கண் பாதிப்பு, பாதங்களில் நரம்பு வலி, தூக்கமின்மை (Insomnia) மற்றும் வாத நோய்கள்.",
      "இரவில் அமைதியான தியானமும், பாதங்களை வெதுவெதுப்பான நீரால் கழுவுதலும் நல்ல தூக்கத்தைத் தரும்."
    ],
    "health_precautions_en": [
      "Prone to left-eye ocular strain, peripheral foot neuralgia, insomnia, and systemic vata disorders.",
      "Nightly grounding meditation, warm foot reflexology baths, and tranquil sleep hygiene."
    ],
    "source_reference": "Dr. B.V. Raman - How to Judge a Horoscope (Vol. 2) & Saravali Ch. 30"
  }
];

const OWN_SIGNS_MAP: Record<string, number[]> = {
  Sun: [5],
  Moon: [4],
  Mars: [1, 8],
  Mercury: [3, 6],
  Jupiter: [9, 12],
  Venus: [2, 7],
  Saturn: [10, 11],
  Rahu: [11],
  Ketu: [8],
};

/**
 * Evaluates the 9 planets' house placements from Lagna for any horoscope,
 * computing house distance, sign placement, dignity (Ucham/Aatchi/Neecham/Dikbala),
 * and Shadbala percentage.
 */
export function evaluateHoroscopePlanetarySthanas(horoscope: any): EvaluatedPlanetSthana[] {
  if (!horoscope || !horoscope.planets || !horoscope.ascendant) {
    return [];
  }

  const lagnaSignIndex = horoscope.ascendant.sign_index;
  const results: EvaluatedPlanetSthana[] = [];

  const targetPlanets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];

  // Normalize planets list from array or object
  const planetsList: any[] = Array.isArray(horoscope.planets)
    ? horoscope.planets
    : Object.values(horoscope.planets);

  for (const planetKey of targetPlanets) {
    const planetData = planetsList.find(
      (p: any) => p && p.name && p.name.toLowerCase() === planetKey.toLowerCase()
    );
    if (!planetData) continue;

    const signIndex = planetData.sign_index;
    const houseNumber =
      planetData.house && planetData.house >= 1 && planetData.house <= 12
        ? planetData.house
        : (((signIndex - lagnaSignIndex + 12) % 12) + 1);

    // Retrieve Dignity with correct arguments:
    // (planetName, signIndex, ascendantSignIndex, degreeInSign, explicitHouse)
    const dignity = getGrahaDignity(
      planetKey,
      signIndex,
      lagnaSignIndex,
      planetData.degree_in_sign || 0,
      houseNumber
    );

    const isOwnSign = Boolean(OWN_SIGNS_MAP[planetKey]?.includes(signIndex));

    // Retrieve Shadbala detail (handles both array and object formats)
    let shadbalaDetail: any = null;
    if (horoscope.shadbala?.planets) {
      if (Array.isArray(horoscope.shadbala.planets)) {
        shadbalaDetail = horoscope.shadbala.planets.find(
          (sp: any) => sp && sp.planet && sp.planet.toLowerCase() === planetKey.toLowerCase()
        );
      } else {
        shadbalaDetail = horoscope.shadbala.planets[planetKey];
      }
    }

    const shadbalaRatio = shadbalaDetail?.ratio ?? 1.0;
    const shadbalaPercentage = Math.round(shadbalaRatio * 100);
    const shadbalaRupas = shadbalaDetail?.total_rupas;
    const shadbalaIsStrong = shadbalaDetail?.is_strong ?? (shadbalaRatio >= 1.0);

    // Determine overall strength category
    let dignityType: EvaluatedPlanetSthana["dignity_type"] = "neutral";
    let dignityLabelTa = dignity.labelTa || "சமநிலை";
    let dignityLabelEn = dignity.labelEn || "Neutral";

    if (dignity.isUcham) {
      dignityType = "exalted";
      dignityLabelTa = dignity.isDeepUcham ? "பரம உச்சம்" : "உச்சம் (Exalted)";
      dignityLabelEn = dignity.isDeepUcham ? "Deep Exaltation" : "Exalted";
    } else if (isOwnSign) {
      dignityType = "own_sign";
      dignityLabelTa = "ஆட்சி (Own Sign)";
      dignityLabelEn = "Own Sign";
    } else if (dignity.isDikBala) {
      dignityType = "dikbala";
      dignityLabelTa = "திக்பலம் (Digbala)";
      dignityLabelEn = "Digbala";
    } else if (dignity.isNeecham) {
      dignityType = "debilitated";
      dignityLabelTa = dignity.isDeepNeecham ? "பரம நீசம்" : "நீசம் (Debilitated)";
      dignityLabelEn = dignity.isDeepNeecham ? "Deep Debilitation" : "Debilitated";
    } else if (shadbalaIsStrong) {
      dignityType = "friendly";
      dignityLabelTa = "சுப பலம் (Strong)";
      dignityLabelEn = "Strong Placement";
    }

    const isNetStrong = dignity.isUcham || isOwnSign || dignity.isDikBala || (shadbalaRatio >= 1.05 && !dignity.isNeecham);

    // Find the master prediction entry
    const matchedPrediction = PLANETARY_STHANA_PREDICTIONS.find(
      (p) => p.planet === planetKey && p.house === houseNumber
    );

    if (!matchedPrediction) continue;

    // Use sign_index (1-12) to get sign names
    const signNameTa = planetData.sign_name_tamil || SIGN_NAMES_TA[signIndex - 1] || "";
    const signNameEn = planetData.sign_name || SIGN_NAMES_EN[signIndex - 1] || "";

    // Generate dynamic 1-line highlights
    const statusSummaryTa = `${matchedPrediction.planet_name_ta} லக்னத்திலிருந்து ${houseNumber}-ஆம் பாவத்தில் (${signNameTa} ராசி) ${dignityLabelTa} - ${isNetStrong ? "வலுவான சாதக பலன்கள் கூடும்" : "கவனமும் சமநிலையும் நலம் தரும்"}.`;
    const statusSummaryEn = `${planetKey} in ${houseNumber}th House (${signNameEn}) with ${dignityLabelEn} - ${isNetStrong ? "Manifests positive strengths" : "Requires conscious mindfulness"}.`;

    results.push({
      planet_name: planetKey,
      planet_name_ta: matchedPrediction.planet_name_ta,
      symbol: matchedPrediction.symbol,
      element: matchedPrediction.element,
      house_number: houseNumber,
      house_name_ta: matchedPrediction.house_title_ta,
      house_name_en: matchedPrediction.house_title_en,
      bhava_category: matchedPrediction.bhava_category,
      sign_index: signIndex,
      sign_name_ta: signNameTa,
      sign_name_en: signNameEn,
      degree_in_sign: planetData.degree_in_sign || 0,
      is_retrograde: Boolean(planetData.is_retrograde),
      dignity_label_ta: dignityLabelTa,
      dignity_label_en: dignityLabelEn,
      dignity_type: dignityType,
      shadbala_rupas: shadbalaRupas,
      shadbala_ratio: shadbalaRatio,
      shadbala_percentage: shadbalaPercentage,
      shadbala_is_strong: shadbalaIsStrong,
      is_net_strong: isNetStrong,
      status_summary_ta: statusSummaryTa,
      status_summary_en: statusSummaryEn,
      prediction: matchedPrediction
    });
  }

  return results;
}
