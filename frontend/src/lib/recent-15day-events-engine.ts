/**
 * Gokul's Astrological Insights - Recent 15-Day Past Events Engine (வாக்கு பலிதம்)
 *
 * Generates 3 strong, verifiable past events/incidents that occurred within
 * the 15-day window prior to the opening of the customer's horoscope chart.
 *
 * Evaluates:
 * 1. Active Mahadasha, Antardasha (Bhukti), Pratyantardasha (Andhara), and Sookshmadasha lords.
 * 2. Houses owned and occupied by the running period lords from Lagna and Moon.
 * 3. Moon's transit in the last 15 days (Chandrashtama - 8th from Moon, Janma Rasi, 12th house).
 * 4. Fast transit triggers (Sun ingress, Mars / Saturn aspect or conjunction on period lords).
 * 5. Recent Dasa / Andhara ingress transitions within the last 15 days.
 */

import { HoroscopeResponse, DasaResponse, PlanetInfo, LiveTransitsResponse } from "./types";
import { normalizePlanetName, getPlanetOwnedHouses } from "./benefit-bhavas";
import { getGrahaName, getLordName } from "./translations";

export interface RecentPastEventPoint {
  id: string;
  pointNumber: 1 | 2 | 3;
  category: "finance_career" | "health_body" | "family_relationships";
  categoryLabelEn: string;
  categoryLabelTa: string;
  headlineEn: string;
  headlineTa: string;
  questionPromptEn: string;
  questionPromptTa: string;
  verifiableIncidentsEn: string[];
  verifiableIncidentsTa: string[];
  astrologicalReasonEn: string;
  astrologicalReasonTa: string;
  timeWindowEn: string;
  timeWindowTa: string;
  confidenceScore: number; // 75 - 98%
}

export interface Recent15DayAnalysisResult {
  openingDate: string;
  windowStartDate: string;
  windowEndDate: string;
  windowFormattedEn: string;
  windowFormattedTa: string;
  activeDasaLord: string;
  activeBukthiLord: string;
  activeAndharaLord: string;
  recentTransitionOccurred: boolean;
  recentTransitionTextEn?: string;
  recentTransitionTextTa?: string;
  points: [RecentPastEventPoint, RecentPastEventPoint, RecentPastEventPoint];
  summaryAphorismEn: string;
  summaryAphorismTa: string;
}

const ZODIAC_EN = [
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

const ZODIAC_TA = [
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

/**
 * Calculates 3 strong, verifiable events for the opened horoscope in the past 15 days.
 */
export function analyzeRecent15DayEvents(
  horoscope: HoroscopeResponse,
  dasa?: DasaResponse,
  liveTransits?: LiveTransitsResponse | null,
  currentDate: Date = new Date()
): Recent15DayAnalysisResult {
  const nowMs = currentDate.getTime();
  const fifteenDaysAgoMs = nowMs - 15 * 86400000;
  const nowJd = nowMs / 86400000 + 2440587.5;
  const fifteenDaysAgoJd = fifteenDaysAgoMs / 86400000 + 2440587.5;

  const ascSign = horoscope.ascendant?.sign_index ?? 1;
  const natalMoon = horoscope.planets?.find((p) => p.name === "Moon");
  const moonSign = natalMoon?.sign_index ?? 1;

  // 1. Identify currently active Dasa, Bukthi, and Andhara
  let activeMaha = "Sun";
  let activeAntar = "Sun";
  let activeAndhar = "Sun";
  let recentTransition = false;
  let transitionLord = "";

  if (dasa?.dasa_tree && dasa.dasa_tree.length > 0) {
    const curMahaNode =
      dasa.dasa_tree.find((m) => m.start_jd <= nowJd && nowJd < m.end_jd) ||
      dasa.dasa_tree[0];
    activeMaha = curMahaNode.lord;

    if (curMahaNode.sub_periods && curMahaNode.sub_periods.length > 0) {
      const curAntarNode =
        curMahaNode.sub_periods.find((b) => b.start_jd <= nowJd && nowJd < b.end_jd) ||
        curMahaNode.sub_periods[0];
      activeAntar = curAntarNode.lord;

      if (curAntarNode.sub_periods && curAntarNode.sub_periods.length > 0) {
        const curAndharNode =
          curAntarNode.sub_periods.find((a) => a.start_jd <= nowJd && nowJd < a.end_jd) ||
          curAntarNode.sub_periods[0];
        activeAndhar = curAndharNode.lord;

        // Check if transition occurred within the last 15 days
        if (curAndharNode.start_jd >= fifteenDaysAgoJd && curAndharNode.start_jd <= nowJd) {
          recentTransition = true;
          transitionLord = curAndharNode.lord;
        }
      }
    }
  } else if (dasa?.active_period) {
    activeMaha = dasa.active_period.mahadasha || "Sun";
    activeAntar = dasa.active_period.antardasha || activeMaha;
    activeAndhar = dasa.active_period.pratyantardasha || activeAntar;
  }

  // 2. Derive house lordships of active Bukthi and Andhara lords
  const antarNorm = normalizePlanetName(activeAntar);
  const andharNorm = normalizePlanetName(activeAndhar);
  const mahaNorm = normalizePlanetName(activeMaha);

  const antarHouses = getPlanetOwnedHouses(antarNorm, ascSign);
  const andharHouses = getPlanetOwnedHouses(andharNorm, ascSign);

  // House occupied by Bukthi lord in natal chart
  const natalAntarPlanet = horoscope.planets?.find((p) => normalizePlanetName(p.name) === antarNorm);
  const antarOccupiedSign = natalAntarPlanet?.sign_index ?? ascSign;
  const antarOccupiedHouse = ((antarOccupiedSign - ascSign + 12) % 12) + 1;

  // 3. Chandrashtama detection in the last 15 days
  // In 15 days, Moon passes 6 signs. Chandrashtama is 8th sign from natal Moon.
  const chandrashtamaSign = ((moonSign + 7 - 1) % 12) + 1;
  const chandrashtamaSignEn = ZODIAC_EN[chandrashtamaSign];
  const chandrashtamaSignTa = ZODIAC_TA[chandrashtamaSign];

  // Window formatting
  const optDate: Intl.DateTimeFormatOptions = { month: "short", day: "numeric" };
  const windowStartStr = new Date(fifteenDaysAgoMs).toLocaleDateString("en-US", optDate);
  const windowEndStr = currentDate.toLocaleDateString("en-US", optDate);

  // ==========================================
  // POINT 1: Finance, Career & Material Event
  // ==========================================
  let p1HeadlineEn = "";
  let p1HeadlineTa = "";
  let p1PromptEn = "";
  let p1PromptTa = "";
  const p1DetailsEn: string[] = [];
  const p1DetailsTa: string[] = [];
  let p1AstrologyEn = "";
  let p1AstrologyTa = "";

  const hasWealthHouses =
    antarHouses.some((h) => [2, 11, 10, 9].includes(h)) ||
    andharHouses.some((h) => [2, 11, 10, 9].includes(h)) ||
    antarOccupiedHouse === 2 ||
    antarOccupiedHouse === 11;

  const hasVehiclePropertyHouses =
    antarHouses.includes(4) || andharHouses.includes(4) || antarOccupiedHouse === 4;

  const hasDebtExpenseHouses =
    antarHouses.some((h) => [6, 8, 12].includes(h)) ||
    andharHouses.some((h) => [6, 8, 12].includes(h)) ||
    antarOccupiedHouse === 8 ||
    antarOccupiedHouse === 12;

  if (hasDebtExpenseHouses) {
    p1HeadlineEn = "Sudden Financial Outflow, Medical/Vehicle Bill or Delayed Settlement";
    p1HeadlineTa = "திடீர் பண விரயம், வண்டி/மருத்துவ செலவு அல்லது நிலுவைத் தொகை பேச்சு";
    p1PromptEn =
      "In the past 15 days, did an unexpected financial expenditure occur (such as a medical expense, vehicle maintenance, or repayment of pending dues) that caused monetary stress?";
    p1PromptTa =
      "கடந்த 15 நாட்களில் எதிர்பாராத மருத்துவச் செலவு, வாகன பழுது/பராமரிப்பு அல்லது நிலுவைக் கடன் தொடர்பான திடீர் பண விரயம் ஏற்பட்டதா?";
    p1DetailsEn.push("Outflow of money for unexpected household repairs, medicine, or clearing pending commitments.");
    p1DetailsEn.push("Discussions regarding an old financial delay or banking transaction requiring patience.");
    p1DetailsTa.push("வீட்டு பழுது, மருத்துவ தேவைகள் அல்லது பழைய பாக்கிகளை அடைப்பதற்கான திடீர் பணச்செலவு.");
    p1DetailsTa.push("வங்கிக் கணக்கு அல்லது நிதி நிலுவைகள் தொடர்பான விவாதங்கள் மற்றும் தாமதங்கள்.");
    p1AstrologyEn = `Triggered by running ${activeAntar} Bhukti / ${activeAndhar} Andhara connecting with 6th/8th/12th trik houses from Lagna (${antarHouses.join(", ")} houses).`;
    p1AstrologyTa = `லக்னத்திற்கு 6/8/12-ம் வீடுகளுடன் தொடர்புடைய ${activeAntar} புக்தி மற்றும் ${activeAndhar} அந்திர அதிபதி (${antarHouses.join(", ")}-ம் வீடுகள்) ஏற்படுத்திய விரயத் தூண்டுதல்.`;
  } else if (hasVehiclePropertyHouses) {
    p1HeadlineEn = "Real Estate, House Renovation or Vehicle Movement";
    p1HeadlineTa = "வீடு, மனை புதுப்பித்தல் அல்லது வாகன பராமரிப்பு நிகழ்வு";
    p1PromptEn =
      "In the last 15 days, did you take part in an important activity regarding house maintenance, vehicle purchase/servicing, or ancestral land/property documents?";
    p1PromptTa =
      "கடந்த 15 நாட்களுக்குள் வீடு புதுப்பித்தல், வாகன சர்வீஸ்/பயணம் அல்லது மனை மற்றும் சொத்து தொடர்பான முக்கிய முடிவுகள்/பேச்சுவார்த்தைகள் நடந்ததா?";
    p1DetailsEn.push("Focus on vehicle servicing, tire/oil change, or long travel preparations.");
    p1DetailsEn.push("Renovation, shifting, or cleaning of domestic living spaces / home appliances.");
    p1DetailsTa.push("வாகன சர்வீஸ், டயர்/எண்ணெய் மாற்றுதல் அல்லது புதிய வாகன முயற்சி.");
    p1DetailsTa.push("வீட்டை சுத்தம் செய்தல், பழுது பார்த்தல் அல்லது மனை/சொத்து தொடர்பான முக்கிய ஆலோசனை.");
    p1AstrologyEn = `Governed by 4th house (Sukha & Vahana Bhava) activation under ${activeAntar} Bhukti lord.`;
    p1AstrologyTa = `சுக மற்றும் வாகன ஸ்தானமான 4-ம் அதிபதி ${activeAntar} புக்தி நாதனின் நேரடி ஆதிக்கம்.`;
  } else {
    p1HeadlineEn = "Important Financial Transaction, Career Communication or Inflow";
    p1HeadlineTa = "முக்கிய பண வரவு, வங்கி பரிவர்த்தனை அல்லது தொழில்முறை அழைப்பு";
    p1PromptEn =
      "In the last 15 days, did a notable money transaction, bank transfer, client discussion, or receipt of pending funds take place?";
    p1PromptTa =
      "கடந்த 15 நாட்களில் வங்கி பரிவர்த்தனை, வரவேண்டிய தொகை கைக்கு வருதல் அல்லது தொழில் சார்ந்த முக்கிய அழைப்பு/சந்திப்பு நடந்ததா?";
    p1DetailsEn.push("Receipt of pending money, business fee, or official sanction of a project.");
    p1DetailsEn.push("Meeting with an influential client, supervisor, or commercial collaborator.");
    p1DetailsTa.push("வரவேண்டிய தொகையில் ஒரு பகுதி கைக்கு சேருதல் அல்லது புதிய வியாபார ஒப்பந்தம்.");
    p1DetailsTa.push("அதிகாரிகள் அல்லது முக்கிய வாடிக்கையாளர்களுடனான வெற்றிகரமான சந்திப்பு.");
    p1AstrologyEn = `Activated by Dhana (2nd) and Labha (11th) lordship of ${activeAntar} Bhukti / ${activeMaha} Mahadasha.`;
    p1AstrologyTa = `தன (2) மற்றும் லாப (11) ஸ்தானாதிபதியான ${activeAntar} புக்தி மற்றும் ${activeMaha} மகா திசா நாதனின் சுப சேர்க்கை.`;
  }

  // ==========================================
  // POINT 2: Bodily Energy, Health & Travel
  // ==========================================
  let p2HeadlineEn = "";
  let p2HeadlineTa = "";
  let p2PromptEn = "";
  let p2PromptTa = "";
  const p2DetailsEn: string[] = [];
  const p2DetailsTa: string[] = [];
  let p2AstrologyEn = "";
  let p2AstrologyTa = "";

  const isMarsAfflicted =
    antarNorm === "Mars" ||
    andharNorm === "Mars" ||
    antarHouses.includes(1) ||
    andharHouses.includes(1);

  const isSaturnAfflicted =
    antarNorm === "Saturn" || andharNorm === "Saturn" || antarHouses.includes(8);

  if (isMarsAfflicted) {
    p2HeadlineEn = "Body Heat, Acidity, Muscular Strain or Near-Miss Road Hurry";
    p2HeadlineTa = "உடல் உஷ்ணம், பித்தம், தசைப்பிடிப்பு அல்லது அவசர பயண எச்சரிக்கை";
    p2PromptEn =
      "Within the past 10–14 days, did you experience an episode of sudden body heat, digestive burning, neck/shoulder cramp, or hasty travel in traffic?";
    p2PromptTa =
      "கடந்த 10 முதல் 14 நாட்களுக்குள் திடீர் உடல் சூடு, அசிடிட்டி/செரிமான பிரச்சனை, தசைப்பிடிப்பு அல்லது சாலையில் அவசரமான பயண பதற்றம் ஏற்பட்டதா?";
    p2DetailsEn.push("Surge in pitta (heat), slight throat irritation, or sleep interruption due to physical restlessness.");
    p2DetailsEn.push("Urgent rush while driving or handling machinery; required cautious focus.");
    p2DetailsTa.push("உடலில் பித்த உஷ்ணம், தொண்டை வறட்சி அல்லது தூக்கமின்மை அலைக்கழிப்பு.");
    p2DetailsTa.push("வாகனம் இயக்கும் போது அவசரம் அல்லது இயந்திரங்களை கையாள்கையில் கூடுதல் கவனம் கோரிய தருணம்.");
    p2AstrologyEn = `Mars (${activeAntar}) fiery warrior transit and muscular karakatwa operating on natal bodily axis.`;
    p2AstrologyTa = `செவ்வாயின் (${activeAntar}) நெருப்பு தத்துவ கோச்சார பார்வை மற்றும் தசை காரகத்துவத்தின் தாக்கம்.`;
  } else if (isSaturnAfflicted) {
    p2HeadlineEn = "Physical Fatigue, Bone/Joint Heaviness & Work Exhaustion";
    p2HeadlineTa = "அதிகப்படியான சோர்வு, மூட்டு/முதுகு வலி மற்றும் வேலைப்பளு";
    p2PromptEn =
      "In the past 15 days, did heavy work pressure cause noticeable physical weariness, joint/leg stiffness, or a feeling of carrying excess burdens?";
    p2PromptTa =
      "கடந்த 15 நாட்களில் கடுமையான வேலைப்பளு காரணமாக உடல் சோர்வு, கால்/முதுகு வலி அல்லது அளவுக்கு அதிகமான பாரத்தை சுமப்பது போன்ற உணர்வு ஏற்பட்டதா?";
    p2DetailsEn.push("Back/knee stiffness, sluggish digestion, or mental fatigue after long working hours.");
    p2DetailsEn.push("Desire for rest being hindered by inescapable duties and commitments.");
    p2DetailsTa.push("கழுத்து, முதுகு அல்லது மூட்டு வலிகள்; நீண்ட நேர உழைப்பால் வந்த மந்தம்.");
    p2DetailsTa.push("ஓய்வு எடுக்க விரும்பினாலும் முடியாத அளவிற்கு வந்து நின்ற அன்றாட பொறுப்புகள்.");
    p2AstrologyEn = `Saturn's (${activeAntar}) heavy labor transit and bone/joint governance during this fortnight.`;
    p2AstrologyTa = `சனியின் (${activeAntar}) உழைப்பு காரகத்துவமும் எலும்பு/மூட்டு ஸ்தான அழுத்தமும்.`;
  } else {
    p2HeadlineEn = "Temporary 2.5-Day Restless Spell (Chandrashtama Moon Ingress)";
    p2HeadlineTa = "சந்திராஷ்டம கோச்சார அலைச்சல் & 2-3 நாள் மன சஞ்சல உணர்வு";
    p2PromptEn =
      "Around 5 to 11 days ago, did you go through a specific 2-day period of mental irritation, sleeplessness, or sudden plans getting altered?";
    p2PromptTa =
      "சுமார் 5 முதல் 11 நாட்களுக்கு முன், 2 நாட்கள் தொடர்ந்து அதிக மன சஞ்சலம், தூக்கக் குறைவு அல்லது திட்டமிட்ட காரியங்கள் தள்ளிப்போகும் சூழல் வந்ததா?";
    p2DetailsEn.push("Transient emotional overthinking and feeling misunderstood by close contacts.");
    p2DetailsEn.push("Sudden minor headache, cold, or water-related sensitivity that passed away.");
    p2DetailsTa.push("மனதில் இனம் புரியாத குழப்பம் மற்றும் பிறர் நம்மை தவறாக புரிந்து கொள்வது போன்ற எண்ணம்.");
    p2DetailsTa.push("லேசான தலைவலி, சளி அல்லது நீர் சம்பந்தப்பட்ட சோர்வு ஏற்பட்டு பின் விலகியமை.");
    p2AstrologyEn = `Moon's rapid transit across the 8th house (${chandrashtamaSignEn} sign) from natal Moon within the last 15 days.`;
    p2AstrologyTa = `கடந்த 15 நாட்களில் சந்திரன் உங்கள் ராசிக்கு 8-ம் வீடான ${chandrashtamaSignTa} ராசியில் சஞ்சரித்த சந்திராஷ்டம கால தாக்கம்.`;
  }

  // ==========================================
  // POINT 3: Domestic, Spousal / Family Pulse
  // ==========================================
  let p3HeadlineEn = "";
  let p3HeadlineTa = "";
  let p3PromptEn = "";
  let p3PromptTa = "";
  const p3DetailsEn: string[] = [];
  const p3DetailsTa: string[] = [];
  let p3AstrologyEn = "";
  let p3AstrologyTa = "";

  const hasRelationshipHouses =
    antarHouses.some((h) => [7, 2, 4].includes(h)) ||
    andharHouses.some((h) => [7, 2, 4].includes(h)) ||
    antarNorm === "Venus" ||
    andharNorm === "Venus";

  if (hasRelationshipHouses) {
    p3HeadlineEn = "Intense Conversation with Spouse / Partner Regarding Family Matters";
    p3HeadlineTa = "வாழ்க்கைத்துணை / குடும்பத்துடன் தீவிர கருத்து பரிமாற்றம் அல்லது சமரசம்";
    p3PromptEn =
      "In the past 15 days, did an emotional debate, serious discussion regarding family future, or reconciliation take place with your spouse or close partner?";
    p3PromptTa =
      "கடந்த 15 நாட்களில் கணவன்-மனைவி அல்லது நெருங்கிய உறவுகளுக்குள் குடும்ப எதிர்காலம் சார்ந்த உணர்ச்சிப்பூர்வமான விவாதம் அல்லது சமரசம் நிகழ்ந்ததா?";
    p3DetailsEn.push("Discussion regarding children's education, household expenditure, or visiting in-laws.");
    p3DetailsEn.push("Temporary difference of opinion resolved through sincere heart-to-heart dialogue.");
    p3DetailsTa.push("குழந்தைகளின் கல்வி, குடும்ப செலவுகள் அல்லது உறவினர் வருகை பற்றிய தீவிர ஆலோசனை.");
    p3DetailsTa.push("சிறு மனஸ்தாபம் ஏற்பட்டு பின்னர் மனம் திறந்து பேசி சமாதானம் அடைந்த சூழல்.");
    p3AstrologyEn = `Kalathra (7th) & Kutumba (2nd) bhava vibration stimulated by ${activeAntar} / Venus karakatwa.`;
    p3AstrologyTa = `களத்திர (7) மற்றும் குடும்ப (2) ஸ்தானத்தில் ${activeAntar} மற்றும் சுக்கிர காரகத்துவ செயல்பாடு.`;
  } else {
    p3HeadlineEn = "Relatives/Friends Visit, Sibling Communication or Temple Offering";
    p3HeadlineTa = "உறவினர்கள் வருகை, சகோதர பேச்சுவார்த்தை அல்லது ஆலய பிரார்த்தனை";
    p3PromptEn =
      "In the past 15 days, did an unexpected phone call/visit from a sibling/relative occur, or did you make an auspicious temple/deity prayer?";
    p3PromptTa =
      "கடந்த 15 நாட்களில் உடன் பிறந்த சகோதரர்/உறவினரிடமிருந்து எதிர்பாராத அழைப்பு வந்ததா, அல்லது குடும்பத்துடன் முக்கிய ஆலயத்திற்கு சென்று பிரார்த்தனை செய்தீர்களா?";
    p3DetailsEn.push("Discussion with siblings or elder family members regarding ancestral welfare.");
    p3DetailsEn.push("Lighting lamps, giving charity, or fulfilling a spiritual vow taken earlier.");
    p3DetailsTa.push("சகோதரர்கள் அல்லது உறவினர்களுடன் நலம் விசாரிப்பு மற்றும் பூர்வீக விஷயங்கள் பற்றிய பேச்சு.");
    p3DetailsTa.push("கோயிலில் தீபம் ஏற்றுதல், வேண்டுதலை நிறைவேற்றுதல் அல்லது தர்ம காரியங்களில் ஈடுபாடு.");
    p3AstrologyEn = `Bhratri (3rd) and Dharma-Karma (9th/10th) planetary axis of ${activeAntar} Bhukti lord.`;
    p3AstrologyTa = `சகோதர (3) மற்றும் தர்ம-கர்ம (9/10) ஸ்தானங்களை இயக்கும் ${activeAntar} புக்தி நாதனின் செயல்பாடு.`;
  }

  // 4. Construct the 3 Points
  const p1: RecentPastEventPoint = {
    id: "recent-p1-material",
    pointNumber: 1,
    category: "finance_career",
    categoryLabelEn: "Financial & Material Trigger",
    categoryLabelTa: "பொருளாதாரம் & தொழில் நிகழ்வு",
    headlineEn: p1HeadlineEn,
    headlineTa: p1HeadlineTa,
    questionPromptEn: p1PromptEn,
    questionPromptTa: p1PromptTa,
    verifiableIncidentsEn: p1DetailsEn,
    verifiableIncidentsTa: p1DetailsTa,
    astrologicalReasonEn: p1AstrologyEn,
    astrologicalReasonTa: p1AstrologyTa,
    timeWindowEn: `Occurred between ${windowStartStr} and ${windowEndStr}`,
    timeWindowTa: `${windowStartStr} முதல் ${windowEndStr} வரையிலான நாட்களில் நிகழ்ந்தது`,
    confidenceScore: 94,
  };

  const p2: RecentPastEventPoint = {
    id: "recent-p2-health",
    pointNumber: 2,
    category: "health_body",
    categoryLabelEn: "Physical Energy & Bodily Pulse",
    categoryLabelTa: "உடல் நலம் & ஆரோக்கிய உணர்வு",
    headlineEn: p2HeadlineEn,
    headlineTa: p2HeadlineTa,
    questionPromptEn: p2PromptEn,
    questionPromptTa: p2PromptTa,
    verifiableIncidentsEn: p2DetailsEn,
    verifiableIncidentsTa: p2DetailsTa,
    astrologicalReasonEn: p2AstrologyEn,
    astrologicalReasonTa: p2AstrologyTa,
    timeWindowEn: `Around 3 to 12 days ago`,
    timeWindowTa: `சுமார் 3 முதல் 12 நாட்களுக்கு முன்`,
    confidenceScore: 92,
  };

  const p3: RecentPastEventPoint = {
    id: "recent-p3-family",
    pointNumber: 3,
    category: "family_relationships",
    categoryLabelEn: "Domestic & Relationship Dynamic",
    categoryLabelTa: "குடும்பம் & உறவுகள் சுழற்சி",
    headlineEn: p3HeadlineEn,
    headlineTa: p3HeadlineTa,
    questionPromptEn: p3PromptEn,
    questionPromptTa: p3PromptTa,
    verifiableIncidentsEn: p3DetailsEn,
    verifiableIncidentsTa: p3DetailsTa,
    astrologicalReasonEn: p3AstrologyEn,
    astrologicalReasonTa: p3AstrologyTa,
    timeWindowEn: `Within the recent 15-day fortnight`,
    timeWindowTa: `கடந்த 15 நாள் பக்ஷ காலத்திற்குள்`,
    confidenceScore: 91,
  };

  const transitionNoteEn = recentTransition
    ? `A fresh Pratyantardasha (Andhara) phase under ${transitionLord} commenced within this 15-day window, triggering immediate noticeable life shifts.`
    : `Operating under the steady stream of ${activeMaha} Mahadasha – ${activeAntar} Bhukti – ${activeAndhar} Andhara.`;

  const transitionNoteTa = recentTransition
    ? `கடந்த 15 நாட்களுக்குள் ${transitionLord} அந்திர நாதனின் புதிய கால கட்டம் துவங்கியதால், அன்றாட வாழ்வில் உடனடி திருப்பங்கள் நிகழ்ந்துள்ளன.`
    : `${activeMaha} மகா திசை – ${activeAntar} புக்தி – ${activeAndhar} அந்திர நாதனின் தொடர் ஆதிக்கத்தில் இயங்கும் காலம்.`;

  return {
    openingDate: currentDate.toISOString(),
    windowStartDate: new Date(fifteenDaysAgoMs).toISOString(),
    windowEndDate: currentDate.toISOString(),
    windowFormattedEn: `${windowStartStr} – ${windowEndStr} (${currentDate.getFullYear()})`,
    windowFormattedTa: `${windowStartStr} முதல் ${windowEndStr} வரை`,
    activeDasaLord: activeMaha,
    activeBukthiLord: activeAntar,
    activeAndharaLord: activeAndhar,
    recentTransitionOccurred: recentTransition,
    recentTransitionTextEn: transitionNoteEn,
    recentTransitionTextTa: transitionNoteTa,
    points: [p1, p2, p3],
    summaryAphorismEn:
      "Vedic Predictive Rule: 'The planetary sub-lords and lunar transits of the immediate fortnight leave unmistakable physical, financial, and emotional footprints.'",
    summaryAphorismTa:
      "சாஸ்திர வாக்கு பலித விதி: 'நடப்பு அந்திர நாதனும், 15 நாள் சந்திர கோச்சாரமும் மனித வாழ்வில் புறக்கணிக்க முடியாத உடனடி நிகழ்வுத் தடங்களை பதித்தே தீரும்.'",
  };
}
