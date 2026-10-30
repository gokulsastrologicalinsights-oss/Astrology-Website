/**
 * Gokul's Astrological Insights - Dasa-Bhukti Caution Alert & Reminder Engine
 *
 * Scans saved horoscopes to identify active and upcoming "Worst-Case" or "High-Caution"
 * Dasa-Bhukti periods (e.g. Shadashtaka 6/8 axis, Maraka/Badhaka confluence, 8th/12th lords,
 * combust or debilitated periods, and adverse scores).
 *
 * Generates personalized, professional WhatsApp advisory links in Tamil & English
 * with prescribed Vedic remedies, mantras, and precautions.
 */

import fs from "fs";
import path from "path";
import { createAdminClient } from "./supabase/admin.ts";
import {
  HoroscopeResponse,
  DasaResponse,
  DasaPeriodNode,
  FullHoroscopeResult,
  ShadbalaResponse,
  AshtakavargaResponse,
} from "./types.ts";
import {
  analyzeDasaBukthiPalangal,
  DasaBukthiAnalysis,
} from "./dasa-bukthi-palangal.ts";
import { generateChildSubPeriods, jdToCalendarDateTime } from "./dasa-helpers.ts";
import { normalizePlanetName } from "./benefit-bhavas.ts";
import { validateAndNormalizePhone } from "./phone-utils.ts";

export type CautionSeverity = "critical" | "moderate";
export type RiskDomain = "health" | "finance" | "career" | "relationships" | "general";

export interface DasaCautionItem {
  id: string; // unique item id e.g. `${horoscopeId}_${mahaLord}_${antarLord}_${andharLord}_${antharaStartIso}`
  customerId?: string;
  horoscopeId: string;
  fullName: string;
  birthDate: string;
  countryCode?: string;
  phoneNumber?: string;
  normalizedPhone?: string;
  whatsappNumber?: string;
  hasValidPhone: boolean;

  // 3-tier hierarchy lords
  mahadashaLord: string;
  antardashaLord: string;
  andharLord: string;
  mahadashaLordTa: string;
  antardashaLordTa: string;
  andharLordTa: string;

  // Exact Antharam Dates & Duration (the short time period alone)
  startDateIso: string;
  endDateIso: string;
  startDateFormatted: string;
  endDateFormatted: string;
  durationDays: number;
  durationFormatted: string;

  // Parent Bhukti context (for reference)
  bhuktiStartDateFormatted?: string;
  bhuktiEndDateFormatted?: string;

  isActiveNow: boolean;
  isUpcoming: boolean;
  progressPercent: number;

  // Astrological Risk & Remedies
  severity: CautionSeverity;
  adverseScore: number; // 0 to 100
  andharaPositiveScore: number;
  dasaBukthiPositiveScore: number;
  verdictEn: string;
  verdictTa: string;
  primaryRiskDomain: RiskDomain;
  riskDomainLabelEn: string;
  riskDomainLabelTa: string;
  reasonsEn: string[];
  reasonsTa: string[];
  remedyDeityEn: string;
  remedyDeityTa: string;
  remedyMantraEn: string;
  remedyMantraTa: string;
  remedyCharityEn: string;
  remedyCharityTa: string;
  generalRemedyEn: string;
  generalRemedyTa: string;
  avoidNotesEn: string;
  avoidNotesTa: string;

  // WhatsApp & Message Links
  whatsappLinkEn: string;
  whatsappLinkTa: string;
  messageTextEn: string;
  messageTextTa: string;
  alertSent: boolean;
  alertSentAt?: string | null;
}

export interface CautionAlertRecord {
  id?: string;
  horoscope_id: string;
  customer_id?: string;
  dasa_lord: string;
  bhukti_lord: string;
  andhar_lord?: string;
  period_start: string;
  period_end?: string;
  severity: string;
  sent_by?: string;
  sent_at: string;
}

// Planet Tamil Names mapping
const PLANET_NAMES_TA: Record<string, string> = {
  Sun: "சூரியன்",
  Moon: "சந்திரன்",
  Mars: "செவ்வாய்",
  Mercury: "புதன்",
  Jupiter: "குரு",
  Venus: "சுக்கிரன்",
  Saturn: "சனி",
  Rahu: "ராகு",
  Ketu: "கேது",
};

export function getPlanetNameTa(lord: string): string {
  const norm = normalizePlanetName(lord);
  return PLANET_NAMES_TA[norm] || lord;
}

// Resilient JSON storage paths
function getAlertsFilePath(): string {
  const rootData = path.join(process.cwd(), "data");
  if (fs.existsSync(rootData)) {
    return path.join(rootData, "dasa_caution_alerts.json");
  }
  const frontendData = path.join(process.cwd(), "frontend", "data");
  if (fs.existsSync(frontendData)) {
    return path.join(frontendData, "dasa_caution_alerts.json");
  }
  return path.join(process.cwd(), "data", "dasa_caution_alerts.json");
}

function ensureDataDir(filePath: string) {
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    try {
      fs.mkdirSync(dir, { recursive: true });
    } catch {
      // ignore
    }
  }
}

export function loadLocalCautionAlerts(): CautionAlertRecord[] {
  const file = getAlertsFilePath();
  if (fs.existsSync(file)) {
    try {
      const content = fs.readFileSync(file, "utf-8");
      return JSON.parse(content);
    } catch {
      return [];
    }
  }
  return [];
}

export function saveLocalCautionAlerts(alerts: CautionAlertRecord[]) {
  const file = getAlertsFilePath();
  ensureDataDir(file);
  try {
    fs.writeFileSync(file, JSON.stringify(alerts, null, 2), "utf-8");
  } catch (err) {
    console.warn("Could not save local caution alerts:", err);
  }
}

/**
 * Generates personalized, professional WhatsApp caution message in Tamil or English.
 */
export function getDasaCautionMessageText(
  item: {
    fullName: string;
    mahadashaLord: string;
    antardashaLord: string;
    andharLord?: string;
    mahadashaLordTa: string;
    antardashaLordTa: string;
    andharLordTa?: string;
    startDateFormatted: string;
    endDateFormatted: string;
    durationFormatted?: string;
    severity: CautionSeverity;
    verdictEn: string;
    verdictTa: string;
    riskDomainLabelEn: string;
    riskDomainLabelTa: string;
    reasonsEn: string[];
    reasonsTa: string[];
    remedyDeityEn: string;
    remedyDeityTa: string;
    remedyMantraEn: string;
    remedyMantraTa: string;
    remedyCharityEn: string;
    remedyCharityTa: string;
    generalRemedyEn: string;
    generalRemedyTa: string;
    avoidNotesEn: string;
    avoidNotesTa: string;
  },
  lang: "ta" | "en" = "ta"
): string {
  const name = item.fullName.trim() || (lang === "ta" ? "அன்புடையீர்" : "Valued Client");
  const andharTa = item.andharLordTa || (item.andharLord ? getPlanetNameTa(item.andharLord) : null);
  const andharEn = item.andharLord || null;
  const durStr = item.durationFormatted ? ` (${item.durationFormatted})` : "";

  if (lang === "ta") {
    const reasonsStr = item.reasonsTa.slice(0, 3).map((r) => `  • ${r}`).join("\n");
    const andharHeading = andharTa
      ? `${item.mahadashaLordTa} தசா - ${item.antardashaLordTa} புக்தியில், ${andharTa} அந்தர காலம் (${item.startDateFormatted} முதல் ${item.endDateFormatted} வரை${durStr})`
      : `${item.startDateFormatted} முதல் ${item.endDateFormatted} வரை ${item.mahadashaLordTa} தசா - ${item.antardashaLordTa} புக்தி`;

    return `வணக்கம் ${name},

உங்கள் ஜாதகக் கணிப்பின்படி, ${andharHeading} அதிக கவனமும் விழிப்புணர்வும் தேவைப்படும் கண்ட காலமாகும்.

⚠️ முக்கிய கவனக் குறிப்புகள்:
• கவனப் பகுதி: ${item.riskDomainLabelTa}
${reasonsStr}
• தவிர்க்க வேண்டியவை: ${item.avoidNotesTa}

🙏 பரிந்துரைக்கப்படும் பரிகாரங்கள் & வழிபாடுகள்:
• வழிபடும் தெய்வம்: ${item.remedyDeityTa}
• பாராயணம்: ${item.remedyMantraTa}
• தானம்: ${item.remedyCharityTa}
• பொது பரிகாரம்: ${item.generalRemedyTa}

இறைவனின் பேரருளால் அனைத்துத் தடைகளும் நீங்கி நலம் பெற வேண்டுகிறோம்! 🌟

📞 ஏதேனும் சந்தேகங்கள் அல்லது ஆலோசனைகளுக்கு 9444 55 9071 என்ற எண்ணை அழைக்கவும்.

இங்ஙனம்,
கோகுல் ஜோதிட மையம் (Gokul's Astrological Insights)`;
  }

  const reasonsStrEn = item.reasonsEn.slice(0, 3).map((r) => `  • ${r}`).join("\n");
  const andharHeadingEn = andharEn
    ? `under ${item.mahadashaLord} Mahadasha - ${item.antardashaLord} Antardasha, the ${andharEn} Anthara period (${item.startDateFormatted} to ${item.endDateFormatted}${durStr})`
    : `the period from ${item.startDateFormatted} to ${item.endDateFormatted} is governed by ${item.mahadashaLord} Mahadasha - ${item.antardashaLord} Antardasha`;

  return `Dear ${name},

According to your Vedic astrological chart calculation, ${andharHeadingEn} is a sensitive caution period requiring vigilance.

⚠️ Astrological Caution & Focus Areas:
• Domain of Care: ${item.riskDomainLabelEn}
${reasonsStrEn}
• What to Avoid: ${item.avoidNotesEn}

🙏 Recommended Propitiation & Remedies:
• Presiding Deity: ${item.remedyDeityEn}
• Sacred Chanting: ${item.remedyMantraEn}
• Recommended Charity (Danam): ${item.remedyCharityEn}
• General Remedial Practice: ${item.generalRemedyEn}

Wishing you divine protection, peace, and spiritual resilience throughout this transit. 🌟

📞 For any doubts or consultation, please call 9444 55 9071.

Warm regards,
Gokul's Astrological Insights`;
}

/**
 * Builds direct WhatsApp URL avoiding emoji corruption.
 */
export function generateWhatsAppCautionLink(
  whatsappNumber: string | undefined | null,
  item: Parameters<typeof getDasaCautionMessageText>[0],
  lang: "ta" | "en" = "ta"
): string {
  if (!whatsappNumber) return "";
  const clean = whatsappNumber.replace(/\D/g, "");
  if (!clean || clean.length < 7) return "";
  const msg = getDasaCautionMessageText(item, lang);
  return `https://api.whatsapp.com/send/?phone=${clean}&text=${encodeURIComponent(msg)}`;
}

/**
 * Formats Gregorian date to DD/MM/YYYY.
 */
function formatIsoToDisplayDate(iso: string): string {
  if (!iso) return "—";
  const [y, m, d] = iso.split("-");
  if (!y || !m || !d) return iso;
  return `${d.padStart(2, "0")}/${m.padStart(2, "0")}/${y}`;
}

interface CautionCacheEntry {
  timestamp: number;
  data: {
    alerts: DasaCautionItem[];
    activeCount: number;
    upcomingCount: number;
    todayKolkata: string;
    totalScanned: number;
    queryError: string | null;
  };
}

const CAUTION_CACHE = new Map<string, CautionCacheEntry>();
const CACHE_TTL_MS = 180_000; // 3 minutes

export function invalidateCautionCache() {
  CAUTION_CACHE.clear();
}

/**
 * Core Scanner: Inspects saved charts for the authenticated user and flags
 * active or upcoming critical Dasa-Bhuktis.
 */
export async function getTodayDasaCautionAlerts(
  userId: string,
  isAdmin: boolean = false,
  lang: "ta" | "en" = "ta",
  forceFresh: boolean = false
): Promise<{
  alerts: DasaCautionItem[];
  activeCount: number;
  upcomingCount: number;
  todayKolkata: string;
  totalScanned?: number;
  queryError?: string | null;
}> {
  const cacheKey = `${userId}_${isAdmin}_${lang}`;
  if (!forceFresh) {
    const cached = CAUTION_CACHE.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < CACHE_TTL_MS) {
      return cached.data;
    }
  }

  // Today's date in Asia/Kolkata
  const kolkataDate = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Kolkata",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());

  // Current Julian Day for now
  const nowJd = Date.now() / 86400000 + 2440587.5;
  // Upcoming horizon: 60 days into future
  const upcomingHorizonJd = nowJd + 60.0;

  // 1. Fetch saved horoscopes with selective JSON arrows for maximum speed & lightweight bandwidth
  const adminClient = createAdminClient();
  let savedList: any[] = [];

  let queryError: string | null = null;
  try {
    let query = adminClient
      .from("saved_horoscopes")
      .select(
        "id, user_id, person_name, birth_date, horoscope:calculation_result->horoscope, dasa:calculation_result->dasa, customer:calculation_result->customer, created_at, updated_at"
      )
      .order("created_at", { ascending: false });
    if (!isAdmin) {
      query = query.eq("user_id", userId);
    }
    const { data, error } = await query.limit(25);
    if (error) {
      console.warn("[CAUTION SCAN PRIMARY QUERY FAILED]", error.message);
      // Fallback with limit 12 to avoid statement timeout
      let fallbackQuery = adminClient
        .from("saved_horoscopes")
        .select(
          "id, user_id, person_name, birth_date, horoscope:calculation_result->horoscope, dasa:calculation_result->dasa, customer:calculation_result->customer, created_at, updated_at"
        )
        .order("created_at", { ascending: false });
      if (!isAdmin) {
        fallbackQuery = fallbackQuery.eq("user_id", userId);
      }
      const { data: fbData, error: fbError } = await fallbackQuery.limit(12);
      if (fbError) {
        queryError = fbError.message;
      } else if (fbData) {
        savedList = fbData;
      }
    } else if (data) {
      savedList = data;
    }
  } catch (err: any) {
    console.warn("Could not fetch saved_horoscopes from Supabase:", err);
    queryError = err?.message || String(err);
  }

  // 2. Load sent alerts to know if already notified
  const localSentAlerts = loadLocalCautionAlerts();
  const sentMap = new Map<string, string>(); // key -> sent_at
  for (const s of localSentAlerts) {
    if (s.andhar_lord) {
      sentMap.set(`${s.horoscope_id}_${s.dasa_lord}_${s.bhukti_lord}_${s.andhar_lord}_${s.period_start}`, s.sent_at);
    }
    sentMap.set(`${s.horoscope_id}_${s.dasa_lord}_${s.bhukti_lord}_${s.period_start}`, s.sent_at);
  }

  // Also query DB for sent alerts if table exists
  try {
    const { data: dbSent } = await (adminClient.from("customer_dasa_caution_alerts") as any)
      .select("*");
    if (dbSent && Array.isArray(dbSent)) {
      for (const s of dbSent) {
        if (s.andhar_lord) {
          sentMap.set(`${s.horoscope_id}_${s.dasa_lord}_${s.bhukti_lord}_${s.andhar_lord}_${s.period_start}`, s.sent_at);
        }
        sentMap.set(`${s.horoscope_id}_${s.dasa_lord}_${s.bhukti_lord}_${s.period_start}`, s.sent_at);
      }
    }
  } catch {
    // Ignore if table not created yet; local JSON fallback protects
  }

  const alerts: DasaCautionItem[] = [];

  for (const record of savedList) {
    const horoscope: HoroscopeResponse = record.horoscope || record.calculation_result?.horoscope;
    const dasa: DasaResponse = record.dasa || record.calculation_result?.dasa;
    const customerMeta = record.customer || record.calculation_result?.customer || {};

    if (!horoscope || !dasa || !dasa.dasa_tree) {
      console.log(`[CAUTION SCAN SKIP] Record ${record.id} (${record.person_name}) missing horoscope or dasa`);
      continue;
    }

    const birthDate: string = record.birth_date || "";
    const fullName = customerMeta.full_name || record.person_name || "Client";
    const phoneVal = validateAndNormalizePhone(
      customerMeta.phone_number || "",
      customerMeta.country_code || "+91"
    );

    const tree: DasaPeriodNode[] = dasa.dasa_tree;

    // Scan:
    // 1. Currently active Mahadashas
    // 2. Upcoming Mahadashas (starting within 60 days)
    const targetMahaNodes = tree.filter(
      (m) =>
        (m.start_jd <= nowJd && nowJd < m.end_jd) ||
        (m.start_jd >= nowJd && m.start_jd <= upcomingHorizonJd)
    );

    const clientCautionCandidates: DasaCautionItem[] = [];

    for (const mahaNode of targetMahaNodes) {
      let subPeriods: DasaPeriodNode[] = mahaNode.sub_periods || [];
      if (!subPeriods || subPeriods.length === 0) {
        subPeriods = generateChildSubPeriods(mahaNode, 5.5, birthDate);
      }

      for (const antarNode of subPeriods) {
        // Deep analysis down to Antharam (Level 3 - Pratyantardasha)
        let andharNodes: DasaPeriodNode[] = antarNode.sub_periods || [];
        if (!andharNodes || andharNodes.length === 0) {
          andharNodes = generateChildSubPeriods(antarNode, 5.5, birthDate);
        }

        // We evaluate Antharams that are:
        // 1. Currently active right now
        // 2. Entering within the next 60 days
        const candidateAndhars = andharNodes.filter(
          (a) =>
            (a.start_jd <= nowJd && nowJd < a.end_jd) ||
            (a.start_jd > nowJd && a.start_jd <= upcomingHorizonJd)
        );

        for (const andharNode of candidateAndhars) {
          const isAntharaActiveNow = andharNode.start_jd <= nowJd && nowJd < andharNode.end_jd;
          const isAntharaUpcoming = andharNode.start_jd > nowJd && andharNode.start_jd <= upcomingHorizonJd;

          // Run full 3-level evaluation combining Dasa, Bhukti, and Antharam
          const analysis: DasaBukthiAnalysis | null = analyzeDasaBukthiPalangal(
            horoscope,
            dasa,
            mahaNode.lord,
            antarNode.lord,
            andharNode.lord,
            undefined,
            undefined,
            birthDate
          );

          if (!analysis) continue;

          // Relationship evaluations across all 3 subdivisions
          const relMahaAntar = analysis.relationship;
          const relAntarAndhar = analysis.andhara?.relationshipFromBhukti;
          const relMahaAndhar = analysis.andhara?.relationshipFromMaha;
          const andharStr = analysis.andhara?.strength;

          // 1. Shadashtaka (6/8 Axis)
          const isBhuktiAntharaShadashtaka = !!relAntarAndhar?.isShadashtakaWarning;
          const isMahaAntharaShadashtaka = !!relMahaAndhar?.isShadashtakaWarning;
          const isMahaBhuktiShadashtaka = !!relMahaAntar?.isShadashtakaWarning;
          const hasShadashtaka = isBhuktiAntharaShadashtaka || isMahaAntharaShadashtaka || isMahaBhuktiShadashtaka;

          // 2. Dvidvadasa (2/12 Axis)
          const isBhuktiAntharaDvidvadasa = !!relAntarAndhar?.isDvidvadasaWarning;

          // 3. Maraka & Badhaka
          const isMaraka =
            !!andharStr?.isMarakesh ||
            (andharStr?.housesOwned || []).some((h: number) => [2, 7].includes(h)) ||
            [2, 7].includes(andharStr?.houseOccupied || 0);
          const isBadhaka = !!andharStr?.isBadhakesh;

          // 4. Dusthana (6, 8, 12)
          const isDusthana = [6, 8, 12].includes(andharStr?.houseOccupied || 0);

          // 5. Planetary Affliction (Combustion / Debilitation)
          const isCombustOrDebil = !!andharStr?.isCombust || andharStr?.dignity === "debilitated";

          // 6. Inimical Relationship across tiers
          const isMutualEnemies =
            relAntarAndhar?.relationshipNature === "mutual_enemies" ||
            relMahaAndhar?.relationshipNature === "mutual_enemies" ||
            relMahaAntar?.relationshipNature === "mutual_enemies";

          // 7. Blended 3-level adverse score (0 to 100)
          const threeLevelPositiveScore = analysis.andharaPositiveScore;
          const adverseScore = 100 - threeLevelPositiveScore;

          // Qualify as caution Antharam:
          const isCautionPeriod =
            isBhuktiAntharaShadashtaka ||
            isMahaAntharaShadashtaka ||
            (isMahaBhuktiShadashtaka && (isDusthana || isMaraka || isMutualEnemies)) ||
            isBhuktiAntharaDvidvadasa ||
            (isMaraka && (isDusthana || adverseScore >= 45)) ||
            (isCombustOrDebil && adverseScore >= 40) ||
            (isMutualEnemies && adverseScore >= 45) ||
            adverseScore >= 45;

          if (!isCautionPeriod) {
            continue;
          }

          // Severity: Critical vs Moderate
          const isCritical =
            isBhuktiAntharaShadashtaka ||
            (isMahaBhuktiShadashtaka && (isMaraka || isDusthana)) ||
            (isMaraka && isDusthana) ||
            adverseScore >= 60 ||
            analysis.verdictLabelEn === "Sensitive / Precautions Required";
          const severity: CautionSeverity = isCritical ? "critical" : "moderate";

          // Determine primary risk domain
          let primaryRiskDomain: RiskDomain = "general";
          let riskDomainLabelEn = "General Vigilance & Vital Energy";
          let riskDomainLabelTa = "பொதுவான விழிப்புணர்வும் மன அமைதியும்";

          if (isMaraka || isDusthana || isBhuktiAntharaShadashtaka || adverseScore >= 65) {
            primaryRiskDomain = "health";
            riskDomainLabelEn = "Health, Road Safety & Bodily Energy";
            riskDomainLabelTa = "ஆரோக்கியம், வாகனப் பயணம் & உடல் நலம்";
          } else if (isBhuktiAntharaDvidvadasa || (andharStr?.housesOwned || []).includes(12)) {
            primaryRiskDomain = "finance";
            riskDomainLabelEn = "Financial Expenses & Asset Preservation";
            riskDomainLabelTa = "பொருளாதார விரயம் & தேவையற்ற செலவுகள்";
          } else if (isCombustOrDebil || [10].includes(andharStr?.houseOccupied || 0)) {
            primaryRiskDomain = "career";
            riskDomainLabelEn = "Career Decisions & Professional Relations";
            riskDomainLabelTa = "தொழில் முடிவுகள் & பணியிட விழிப்புணர்வு";
          }

          // Reasons tailored to all 3 levels & Antharam alone
          const reasonsEn: string[] = [];
          const reasonsTa: string[] = [];

          const mahaTa = getPlanetNameTa(mahaNode.lord);
          const antarTa = getPlanetNameTa(antarNode.lord);
          const andharTa = getPlanetNameTa(andharNode.lord);

          if (isBhuktiAntharaShadashtaka) {
            reasonsTa.push(
              `புக்தி நாதன் ${antarTa} மற்றும் அந்தர நாதன் ${andharTa} 6/8 ஷடாஷ்டக அமைப்பில் உள்ளதால், இந்த குறுகிய அந்தர காலத்தில் திடீர் தடைகள், விபத்து மற்றும் உடல் உபாதைகளில் அதிக கவனம் தேவை.`
            );
            reasonsEn.push(
              `Shadashtaka (6/8 axis) between ${antarNode.lord} (Bhukti) and ${andharNode.lord} (Antharam) triggers sudden setbacks and bodily strain during this window.`
            );
          }
          if (isMahaAntharaShadashtaka) {
            reasonsTa.push(
              `திசா நாதன் ${mahaTa} மற்றும் அந்தர நாதன் ${andharTa} 6/8 அமைப்பில் உள்ளதால் மன உளைச்சலும் அலைச்சலும் நேரலாம்.`
            );
            reasonsEn.push(
              `6/8 axis between Mahadasha Lord ${mahaNode.lord} and Anthara Lord ${andharNode.lord} causes mental resistance and delays.`
            );
          }
          if (isMahaBhuktiShadashtaka && !isBhuktiAntharaShadashtaka) {
            reasonsTa.push(
              `திசா நாதன் ${mahaTa} மற்றும் புக்தி நாதன் ${antarTa} 6/8 ஷடாஷ்டக அமைப்பில் உள்ள நிலையில், ${andharTa} அந்தரம் கூடுதல் விழிப்புணர்வை கோருகிறது.`
            );
            reasonsEn.push(
              `Dasa-Bhukti 6/8 axis is activated by ${andharNode.lord} Anthara, requiring heightened patience.`
            );
          }
          if (isBhuktiAntharaDvidvadasa) {
            reasonsTa.push(
              `புக்தி-அந்தர நாதர்கள் 2/12 துவித்வாதச அமைப்பில் இருப்பதால் தேவையற்ற விரயங்களும் மருத்துவச் செலவுகளும் ஏற்பட வாய்ப்புள்ளது.`
            );
            reasonsEn.push(
              `Dvidvadasa (2/12 axis) between ${antarNode.lord} and ${andharNode.lord} causes unexpected expenditures and physical exhaustion.`
            );
          }
          if (isMaraka) {
            reasonsTa.push(
              `அந்தர நாதன் ${andharTa} மாரக (2/7) ஸ்தான ஆதிபத்தியம் பெறுவதால் உடல் நலனில் விசேஷ கவனம் தேவை.`
            );
            reasonsEn.push(
              `Maraka (2nd/7th house) activation under ${andharNode.lord} Anthara warrants careful health care.`
            );
          }
          if (isCombustOrDebil) {
            reasonsTa.push(
              `அந்தர நாதன் ${andharTa} ${andharStr?.isCombust ? "அஸ்தமனம்" : "நீசம்"} பெற்று பலவீனமாக இருப்பதால் சுப முயற்சிகளில் நிதானம் அவசியம்.`
            );
            reasonsEn.push(
              `Anthara Lord ${andharNode.lord} is ${andharStr?.isCombust ? "combust" : "debilitated"}, reducing natural protective vitality.`
            );
          }
          if (reasonsEn.length === 0 && analysis.keyCautionPointsEn.length > 0) {
            reasonsEn.push(analysis.keyCautionPointsEn[0]);
            reasonsTa.push(analysis.keyCautionPointsTa[0] || analysis.keyCautionPointsEn[0]);
          }

          // Avoid notes
          let avoidNotesEn = "Avoid signing hasty commitments, rash driving, and speculative investments.";
          let avoidNotesTa = "அவசர ஒப்பந்தங்கள், அதிவேக வாகனப் பயணம் மற்றும் ஊக வணிகங்களைத் தவிர்க்கவும்.";

          if (primaryRiskDomain === "finance") {
            avoidNotesEn = "Avoid lending huge sums, surety guarantees, and risky financial ventures.";
            avoidNotesTa = "பெரிய கடன் கொடுப்பது, ஜாமீன் கையொப்பம் இடுவது மற்றும் பண முதலீடுகளைத் தவிர்க்கவும்.";
          } else if (primaryRiskDomain === "health") {
            avoidNotesEn = "Avoid night-time travel, stressful arguments, and neglecting minor medical symptoms.";
            avoidNotesTa = "இரவு நேரப் பயணங்கள், மன உளைச்சல் தரும் விவாதங்கள் மற்றும் உடல் உபாதைகளை அலட்சியம் செய்வதைத் தவிர்க்கவும்.";
          }

          // Remedies
          const rem = analysis.remedies;
          const remedyDeityEn = rem?.deityEn || "Lord Shiva & Lord Ganesha";
          const remedyDeityTa = rem?.deityTa || "சிவபெருமான் & விநாயகர் வழிபாடு";
          const remedyMantraEn = rem?.mantraEn || "Maha Mrityunjaya Mantra";
          const remedyMantraTa = rem?.mantraTa || "மகா மிருத்யுஞ்சய மந்திரம் அல்லது கந்த சஷ்டி கவசம்";
          const remedyCharityEn = rem?.charityEn || "Feeding cows (Go-Danam) or anna danam to the needy";
          const remedyCharityTa = rem?.charityTa || "கோமாதாவுக்கு அகத்திக்கீரை அல்லது ஏழைகளுக்கு அன்னதானம்";
          const generalRemedyEn = rem?.generalRemedyEn || "Light sesame oil deepam on Saturdays / Tuesdays";
          const generalRemedyTa = rem?.generalRemedyTa || "செவ்வாய் அல்லது சனிக்கிழமைகளில் நல்லெண்ணெய் தீபம் ஏற்றுதல்";

          // Exact Antharam Dates alone (short time period)
          const aStartDt = jdToCalendarDateTime(andharNode.start_jd, 5.5);
          const aEndDt = jdToCalendarDateTime(andharNode.end_jd, 5.5);
          const startDateIso = aStartDt?.dateStr || "";
          const endDateIso = aEndDt?.dateStr || "";
          const startDateFormatted = formatIsoToDisplayDate(startDateIso);
          const endDateFormatted = formatIsoToDisplayDate(endDateIso);
          const durationDays = Math.max(1, Math.round(andharNode.duration_days));
          const durationFormatted = `${durationDays} நாட்கள்`;
          const durationFormattedEn = `${durationDays} days`;

          // Progress for this Antharam alone
          let progressPercent = 0;
          if (isAntharaActiveNow && andharNode.end_jd > andharNode.start_jd) {
            const span = andharNode.end_jd - andharNode.start_jd;
            const elapsed = nowJd - andharNode.start_jd;
            progressPercent = Math.min(100, Math.max(0, Math.round((elapsed / span) * 100)));
          } else if (nowJd >= andharNode.end_jd) {
            progressPercent = 100;
          }

          const sentKey = `${record.id}_${mahaNode.lord}_${antarNode.lord}_${andharNode.lord}_${startDateIso}`;
          const alertSentAt =
            sentMap.get(sentKey) ||
            sentMap.get(`${record.id}_${mahaNode.lord}_${antarNode.lord}_${startDateIso}`) ||
            null;
          const alertSent = !!alertSentAt;

          const cautionPayload = {
            fullName,
            mahadashaLord: mahaNode.lord,
            antardashaLord: antarNode.lord,
            andharLord: andharNode.lord,
            mahadashaLordTa: mahaTa,
            antardashaLordTa: antarTa,
            andharLordTa: andharTa,
            startDateFormatted,
            endDateFormatted,
            durationFormatted: lang === "ta" ? durationFormatted : durationFormattedEn,
            severity,
            verdictEn: analysis.verdictLabelEn,
            verdictTa: analysis.verdictLabelTa,
            riskDomainLabelEn,
            riskDomainLabelTa,
            reasonsEn,
            reasonsTa,
            remedyDeityEn,
            remedyDeityTa,
            remedyMantraEn,
            remedyMantraTa,
            remedyCharityEn,
            remedyCharityTa,
            generalRemedyEn,
            generalRemedyTa,
            avoidNotesEn,
            avoidNotesTa,
          };

          const messageTextTa = getDasaCautionMessageText(cautionPayload, "ta");
          const messageTextEn = getDasaCautionMessageText(cautionPayload, "en");
          const whatsappLinkTa = generateWhatsAppCautionLink(phoneVal.whatsappNumber, cautionPayload, "ta");
          const whatsappLinkEn = generateWhatsAppCautionLink(phoneVal.whatsappNumber, cautionPayload, "en");

          clientCautionCandidates.push({
            id: `${record.id}_${mahaNode.lord}_${antarNode.lord}_${andharNode.lord}_${startDateIso}`,
            customerId: customerMeta.id || undefined,
            horoscopeId: record.id,
            fullName,
            birthDate,
            countryCode: phoneVal.normalizedPhone?.startsWith("+91") ? "+91" : undefined,
            phoneNumber: phoneVal.nationalNumber,
            normalizedPhone: phoneVal.normalizedPhone,
            whatsappNumber: phoneVal.whatsappNumber,
            hasValidPhone: phoneVal.isValid,
            mahadashaLord: mahaNode.lord,
            antardashaLord: antarNode.lord,
            andharLord: andharNode.lord,
            mahadashaLordTa: mahaTa,
            antardashaLordTa: antarTa,
            andharLordTa: andharTa,
            startDateIso,
            endDateIso,
            startDateFormatted,
            endDateFormatted,
            durationDays,
            durationFormatted: lang === "ta" ? durationFormatted : durationFormattedEn,
            bhuktiStartDateFormatted: formatIsoToDisplayDate(antarNode.start_date_iso || ""),
            bhuktiEndDateFormatted: formatIsoToDisplayDate(antarNode.end_date_iso || ""),
            isActiveNow: isAntharaActiveNow,
            isUpcoming: isAntharaUpcoming,
            progressPercent,
            severity,
            adverseScore,
            andharaPositiveScore: threeLevelPositiveScore,
            dasaBukthiPositiveScore: analysis.dasaBukthiPositiveScore,
            verdictEn: analysis.verdictLabelEn,
            verdictTa: analysis.verdictLabelTa,
            primaryRiskDomain,
            riskDomainLabelEn,
            riskDomainLabelTa,
            reasonsEn,
            reasonsTa,
            remedyDeityEn,
            remedyDeityTa,
            remedyMantraEn,
            remedyMantraTa,
            remedyCharityEn,
            remedyCharityTa,
            generalRemedyEn,
            generalRemedyTa,
            avoidNotesEn,
            avoidNotesTa,
            whatsappLinkEn,
            whatsappLinkTa,
            messageTextEn,
            messageTextTa,
            alertSent,
            alertSentAt,
          });
        }
      }
    }

    // Pick the worst-case Antharam for this client
    if (clientCautionCandidates.length > 0) {
      clientCautionCandidates.sort((a, b) => {
        // 1. Active critical first
        if (a.isActiveNow && a.severity === "critical" && (!b.isActiveNow || b.severity !== "critical")) return -1;
        if (b.isActiveNow && b.severity === "critical" && (!a.isActiveNow || a.severity !== "critical")) return 1;

        // 2. Active now next
        if (a.isActiveNow && !b.isActiveNow) return -1;
        if (!a.isActiveNow && b.isActiveNow) return 1;

        // 3. Critical severity next
        if (a.severity === "critical" && b.severity !== "critical") return -1;
        if (b.severity === "critical" && a.severity !== "critical") return 1;

        // 4. Higher adverse score
        if (b.adverseScore !== a.adverseScore) return b.adverseScore - a.adverseScore;

        // 5. Earliest start date
        return a.startDateIso.localeCompare(b.startDateIso);
      });

      alerts.push(clientCautionCandidates[0]);
    }
  }

  // Sort by: Critical first, Active now first, then by earliest start date
  alerts.sort((a, b) => {
    if (a.severity === "critical" && b.severity !== "critical") return -1;
    if (b.severity === "critical" && a.severity !== "critical") return 1;
    if (a.isActiveNow && !b.isActiveNow) return -1;
    if (!a.isActiveNow && b.isActiveNow) return 1;
    return a.startDateIso.localeCompare(b.startDateIso);
  });

  const activeCount = alerts.filter((a) => a.isActiveNow).length;
  const upcomingCount = alerts.filter((a) => a.isUpcoming).length;

  const result = {
    alerts,
    activeCount,
    upcomingCount,
    todayKolkata: kolkataDate,
    totalScanned: savedList.length,
    queryError,
  };

  if (!queryError) {
    CAUTION_CACHE.set(cacheKey, { timestamp: Date.now(), data: result });
  }

  return result;
}

/**
 * Mark a caution reminder as sent.
 */
export async function markDasaCautionAlertSent(params: {
  horoscopeId: string;
  customerId?: string;
  dasaLord: string;
  bhuktiLord: string;
  andharLord?: string;
  periodStart: string;
  periodEnd?: string;
  severity?: string;
  sentBy: string;
}): Promise<{ success: boolean; sent_at: string }> {
  const nowIso = new Date().toISOString();

  // 1. Try Supabase table if provisioned
  try {
    const adminClient = createAdminClient();
    const insertPayload: any = {
      horoscope_id: params.horoscopeId,
      customer_id: params.customerId || null,
      dasa_lord: params.dasaLord,
      bhukti_lord: params.bhuktiLord,
      period_start: params.periodStart,
      period_end: params.periodEnd || null,
      severity: params.severity || "high",
      sent_by: params.sentBy,
      sent_at: nowIso,
    };
    if (params.andharLord) {
      insertPayload.andhar_lord = params.andharLord;
    }
    await (adminClient.from("customer_dasa_caution_alerts") as any).insert(insertPayload);
  } catch {
    // Ignore and proceed to persistent JSON storage
  }

  // 2. Resilient local storage
  const localAlerts = loadLocalCautionAlerts();
  const existingIdx = localAlerts.findIndex(
    (a) =>
      a.horoscope_id === params.horoscopeId &&
      a.dasa_lord === params.dasaLord &&
      a.bhukti_lord === params.bhuktiLord &&
      (!params.andharLord || a.andhar_lord === params.andharLord) &&
      a.period_start === params.periodStart
  );

  if (existingIdx >= 0) {
    localAlerts[existingIdx].sent_at = nowIso;
    localAlerts[existingIdx].sent_by = params.sentBy;
    if (params.andharLord) {
      localAlerts[existingIdx].andhar_lord = params.andharLord;
    }
  } else {
    localAlerts.push({
      horoscope_id: params.horoscopeId,
      customer_id: params.customerId,
      dasa_lord: params.dasaLord,
      bhukti_lord: params.bhuktiLord,
      andhar_lord: params.andharLord,
      period_start: params.periodStart,
      period_end: params.periodEnd,
      severity: params.severity || "high",
      sent_by: params.sentBy,
      sent_at: nowIso,
    });
  }

  saveLocalCautionAlerts(localAlerts);
  invalidateCautionCache();

  return { success: true, sent_at: nowIso };
}
