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
import { createAdminClient } from "./supabase/admin";
import {
  HoroscopeResponse,
  DasaResponse,
  DasaPeriodNode,
  FullHoroscopeResult,
  ShadbalaResponse,
  AshtakavargaResponse,
} from "./types";
import {
  analyzeDasaBukthiPalangal,
  DasaBukthiAnalysis,
} from "./dasa-bukthi-palangal";
import { generateChildSubPeriods } from "./dasa-helpers";
import { normalizePlanetName } from "./benefit-bhavas";
import { validateAndNormalizePhone } from "./phone-utils";

export type CautionSeverity = "critical" | "moderate";
export type RiskDomain = "health" | "finance" | "career" | "relationships" | "general";

export interface DasaCautionItem {
  id: string; // unique item id e.g. `${horoscopeId}_${mahaLord}_${antarLord}`
  customerId?: string;
  horoscopeId: string;
  fullName: string;
  birthDate: string;
  countryCode?: string;
  phoneNumber?: string;
  normalizedPhone?: string;
  whatsappNumber?: string;
  hasValidPhone: boolean;
  mahadashaLord: string;
  antardashaLord: string;
  mahadashaLordTa: string;
  antardashaLordTa: string;
  startDateIso: string;
  endDateIso: string;
  startDateFormatted: string;
  endDateFormatted: string;
  durationFormatted: string;
  isActiveNow: boolean;
  isUpcoming: boolean;
  progressPercent: number;
  severity: CautionSeverity;
  adverseScore: number; // 0 to 100
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
    mahadashaLordTa: string;
    antardashaLordTa: string;
    startDateFormatted: string;
    endDateFormatted: string;
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

  if (lang === "ta") {
    const reasonsStr = item.reasonsTa.slice(0, 2).map((r) => `  • ${r}`).join("\n");
    return `வணக்கம் ${name},

உங்கள் ஜாதகக் கணிப்பின்படி, ${item.startDateFormatted} முதல் ${item.endDateFormatted} வரை ${item.mahadashaLordTa} தசா - ${item.antardashaLordTa} புக்தி (${item.verdictTa}) நடைபெறுகிறது.

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

இங்ஙனம்,
கோகுல் ஜோதிட மையம் (Gokul's Astrological Insights)
📞 வாடிக்கையாளர் சேவை`;
  }

  const reasonsStrEn = item.reasonsEn.slice(0, 2).map((r) => `  • ${r}`).join("\n");
  return `Dear ${name},

According to your Vedic astrological chart calculation, the period from ${item.startDateFormatted} to ${item.endDateFormatted} is governed by ${item.mahadashaLord} Mahadasha - ${item.antardashaLord} Antardasha (${item.verdictEn}).

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

/**
 * Core Scanner: Inspects saved charts for the authenticated user and flags
 * active or upcoming critical Dasa-Bhuktis.
 */
export async function getTodayDasaCautionAlerts(
  userId: string,
  isAdmin: boolean = false,
  lang: "ta" | "en" = "ta"
): Promise<{
  alerts: DasaCautionItem[];
  activeCount: number;
  upcomingCount: number;
  todayKolkata: string;
}> {
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
    const { data, error } = await query;
    if (!error && data) {
      savedList = data;
    }
  } catch (err) {
    console.warn("Could not fetch saved_horoscopes from Supabase:", err);
  }

  // 2. Load sent alerts to know if already notified
  const localSentAlerts = loadLocalCautionAlerts();
  const sentMap = new Map<string, string>(); // key -> sent_at
  for (const s of localSentAlerts) {
    const key = `${s.horoscope_id}_${s.dasa_lord}_${s.bhukti_lord}_${s.period_start}`;
    sentMap.set(key, s.sent_at);
  }

  // Also query DB for sent alerts if table exists
  try {
    const { data: dbSent } = await (adminClient.from("customer_dasa_caution_alerts") as any)
      .select("*");
    if (dbSent && Array.isArray(dbSent)) {
      for (const s of dbSent) {
        const key = `${s.horoscope_id}_${s.dasa_lord}_${s.bhukti_lord}_${s.period_start}`;
        sentMap.set(key, s.sent_at);
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
    const shadbala: ShadbalaResponse | undefined = record.shadbala || record.calculation_result?.shadbala;
    const ashtakavarga: AshtakavargaResponse | undefined = record.ashtakavarga || record.calculation_result?.ashtakavarga;

    if (!horoscope || !dasa || !dasa.dasa_tree) {
      continue;
    }

    const birthDate: string = record.birth_date || "";
    const fullName = customerMeta.full_name || record.person_name || "Client";
    const phoneVal = validateAndNormalizePhone(
      customerMeta.phone_number || "",
      customerMeta.country_code || "+91"
    );

    const tree: DasaPeriodNode[] = dasa.dasa_tree;

    // We scan:
    // 1. Currently active Mahadasha and its Bhuktis
    // 2. Next upcoming Mahadasha (if current ends within 60 days)
    const targetMahaNodes = tree.filter(
      (m) =>
        (m.start_jd <= nowJd && nowJd < m.end_jd) ||
        (m.start_jd >= nowJd && m.start_jd <= upcomingHorizonJd)
    );

    for (const mahaNode of targetMahaNodes) {
      let subPeriods: DasaPeriodNode[] = mahaNode.sub_periods || [];
      if (!subPeriods || subPeriods.length === 0) {
        subPeriods = generateChildSubPeriods(mahaNode, 5.5, birthDate);
      }

      for (const antarNode of subPeriods) {
        const isActiveNow = antarNode.start_jd <= nowJd && nowJd < antarNode.end_jd;
        const isUpcoming = antarNode.start_jd > nowJd && antarNode.start_jd <= upcomingHorizonJd;

        // Only evaluate active or soon-approaching periods
        if (!isActiveNow && !isUpcoming) {
          continue;
        }

        // Run Dasa-Bhukti deep evaluation
        const analysis: DasaBukthiAnalysis | null = analyzeDasaBukthiPalangal(
          horoscope,
          dasa,
          mahaNode.lord,
          antarNode.lord,
          undefined,
          undefined,
          undefined,
          birthDate
        );

        if (!analysis) continue;

        // Check adverse criteria
        const isShadashtaka = !!analysis.relationship?.isShadashtakaWarning; // 6/8 axis
        const isDvidvadasa = !!analysis.relationship?.isDvidvadasaWarning; // 2/12 axis
        const isMaraka = !!analysis.relationship?.isMarakaInfluence;
        const isNaturalEnemies = analysis.relationship?.relationshipNature === "mutual_enemies";
        const isCombustOrDebil =
          analysis.antarStrength?.isCombust ||
          analysis.antarStrength?.dignity === "debilitated";
        const score = analysis.overallAuspiciousScore;
        const isChallengingVerdict =
          analysis.verdictLabelEn === "Sensitive / Precautions Required" ||
          analysis.verdictLabelEn === "Challenging";
        const adverseScore = 100 - score;

        // Qualify as caution alert if:
        // - 6/8 Shadashtaka Axis (classic adverse condition)
        // - 2/12 Dvidvadasa Axis (unplanned expenses & separation)
        // - Maraka (2nd/7th house) activation
        // - Inimical natural relationship (mutual enemies like Sun-Saturn, Mars-Mercury)
        // - Combust / Debilitated period lords
        // - Challenging / Sensitive verdict
        // - Adverse score >= 45
        const isCautionPeriod =
          isShadashtaka ||
          isDvidvadasa ||
          isMaraka ||
          isNaturalEnemies ||
          isCombustOrDebil ||
          isChallengingVerdict ||
          adverseScore >= 45;

        if (!isCautionPeriod) {
          continue;
        }

        // Determine severity
        const severity: CautionSeverity =
          isShadashtaka ||
          isMaraka ||
          adverseScore >= 60 ||
          analysis.verdictLabelEn === "Sensitive / Precautions Required"
            ? "critical"
            : "moderate";

        // Determine primary risk domain
        let primaryRiskDomain: RiskDomain = "general";
        let riskDomainLabelEn = "General Vigilance & Vital Energy";
        let riskDomainLabelTa = "பொதுவான விழிப்புணர்வும் மன அமைதியும்";

        if (isMaraka || isShadashtaka || adverseScore >= 70) {
          primaryRiskDomain = "health";
          riskDomainLabelEn = "Health, Road Safety & Bodily Energy";
          riskDomainLabelTa = "ஆரோக்கியம், வாகனப் பயணம் & உடல் நலம்";
        } else if (isDvidvadasa) {
          primaryRiskDomain = "finance";
          riskDomainLabelEn = "Financial Expenses & Asset Preservation";
          riskDomainLabelTa = "பொருளாதார விரயம் & தேவையற்ற செலவுகள்";
        } else if (isCombustOrDebil) {
          primaryRiskDomain = "career";
          riskDomainLabelEn = "Career Decisions & Professional Relations";
          riskDomainLabelTa = "தொழில் முடிவுகள் & பணியிட விழிப்புணர்வு";
        }

        // Reasons
        const reasonsEn: string[] = [];
        const reasonsTa: string[] = [];

        if (isShadashtaka) {
          reasonsEn.push(
            `Shadashtaka (6/8) mutual distance between ${mahaNode.lord} and ${antarNode.lord} causes sudden friction and hurdles.`
          );
          reasonsTa.push(
            `திசா நாதன் ${getPlanetNameTa(mahaNode.lord)} மற்றும் புக்தி நாதன் ${getPlanetNameTa(
              antarNode.lord
            )} 6/8 ஷடாஷ்டக அமைப்பில் இருப்பதால் திடீர் தடைகள் மற்றும் விரயங்கள் நேரலாம்.`
          );
        }
        if (isMaraka) {
          reasonsEn.push(
            "Activation of Maraka (2nd/7th house) significations warrants physical health care."
          );
          reasonsTa.push("மாரக ஸ்தான தொடர்பு ஏற்படுவதால் உடல் நலப் பராமரிப்பில் விழிப்புணர்வு தேவை.");
        }
        if (isDvidvadasa) {
          reasonsEn.push(
            "Dvidvadasa (2/12) axis causes unplanned expenditures and mental restlessness."
          );
          reasonsTa.push("2/12 துவித்வாதச அமைப்பால் தேவையற்ற செலவுகளும் அலைச்சலும் ஏற்படலாம்.");
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

        // Remedies from analysis or planet defaults
        const rem = analysis.remedies;
        const remedyDeityEn = rem?.deityEn || "Lord Shiva & Lord Ganesha";
        const remedyDeityTa = rem?.deityTa || "சிவபெருமான் & விநாயகர் வழிபாடு";
        const remedyMantraEn = rem?.mantraEn || "Maha Mrityunjaya Mantra";
        const remedyMantraTa = rem?.mantraTa || "மகா மிருத்யுஞ்சய மந்திரம் அல்லது கந்த சஷ்டி கவசம்";
        const remedyCharityEn = rem?.charityEn || "Feeding cows (Go-Danam) or anna danam to the needy";
        const remedyCharityTa = rem?.charityTa || "கோமாதாவுக்கு அகத்திக்கீரை அல்லது ஏழைகளுக்கு அன்னதானம்";
        const generalRemedyEn = rem?.generalRemedyEn || "Light sesame oil deepam on Saturdays / Tuesdays";
        const generalRemedyTa = rem?.generalRemedyTa || "செவ்வாய் அல்லது சனிக்கிழமைகளில் நல்லெண்ணெய் தீபம் ஏற்றுதல்";

        const startDateIso = antarNode.start_date_iso || "";
        const endDateIso = antarNode.end_date_iso || "";
        const startDateFormatted = formatIsoToDisplayDate(startDateIso);
        const endDateFormatted = formatIsoToDisplayDate(endDateIso);

        const durationFormatted =
          antarNode.duration_years
            ? `${antarNode.duration_years.toFixed(1)}y`
            : "Active Period";

        // Progress percent
        let progressPercent = 0;
        if (isActiveNow && antarNode.end_jd > antarNode.start_jd) {
          const span = antarNode.end_jd - antarNode.start_jd;
          const elapsed = nowJd - antarNode.start_jd;
          progressPercent = Math.min(100, Math.max(0, Math.round((elapsed / span) * 100)));
        }

        const sentKey = `${record.id}_${mahaNode.lord}_${antarNode.lord}_${startDateIso}`;
        const alertSentAt = sentMap.get(sentKey) || null;
        const alertSent = !!alertSentAt;

        const cautionItemPayload = {
          fullName,
          mahadashaLord: mahaNode.lord,
          antardashaLord: antarNode.lord,
          mahadashaLordTa: getPlanetNameTa(mahaNode.lord),
          antardashaLordTa: getPlanetNameTa(antarNode.lord),
          startDateFormatted,
          endDateFormatted,
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

        const messageTextTa = getDasaCautionMessageText(cautionItemPayload, "ta");
        const messageTextEn = getDasaCautionMessageText(cautionItemPayload, "en");
        const whatsappLinkTa = generateWhatsAppCautionLink(
          phoneVal.whatsappNumber,
          cautionItemPayload,
          "ta"
        );
        const whatsappLinkEn = generateWhatsAppCautionLink(
          phoneVal.whatsappNumber,
          cautionItemPayload,
          "en"
        );

        alerts.push({
          id: `${record.id}_${mahaNode.lord}_${antarNode.lord}`,
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
          mahadashaLordTa: getPlanetNameTa(mahaNode.lord),
          antardashaLordTa: getPlanetNameTa(antarNode.lord),
          startDateIso,
          endDateIso,
          startDateFormatted,
          endDateFormatted,
          durationFormatted,
          isActiveNow,
          isUpcoming,
          progressPercent,
          severity,
          adverseScore,
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

  return {
    alerts,
    activeCount,
    upcomingCount,
    todayKolkata: kolkataDate,
  };
}

/**
 * Mark a caution reminder as sent.
 */
export async function markDasaCautionAlertSent(params: {
  horoscopeId: string;
  customerId?: string;
  dasaLord: string;
  bhuktiLord: string;
  periodStart: string;
  periodEnd?: string;
  severity?: string;
  sentBy: string;
}): Promise<{ success: boolean; sent_at: string }> {
  const nowIso = new Date().toISOString();

  // 1. Try Supabase table if provisioned
  try {
    const adminClient = createAdminClient();
    await (adminClient.from("customer_dasa_caution_alerts") as any).insert({
      horoscope_id: params.horoscopeId,
      customer_id: params.customerId || null,
      dasa_lord: params.dasaLord,
      bhukti_lord: params.bhuktiLord,
      period_start: params.periodStart,
      period_end: params.periodEnd || null,
      severity: params.severity || "high",
      sent_by: params.sentBy,
      sent_at: nowIso,
    });
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
      a.period_start === params.periodStart
  );

  if (existingIdx >= 0) {
    localAlerts[existingIdx].sent_at = nowIso;
    localAlerts[existingIdx].sent_by = params.sentBy;
  } else {
    localAlerts.push({
      horoscope_id: params.horoscopeId,
      customer_id: params.customerId,
      dasa_lord: params.dasaLord,
      bhukti_lord: params.bhuktiLord,
      period_start: params.periodStart,
      period_end: params.periodEnd,
      severity: params.severity || "high",
      sent_by: params.sentBy,
      sent_at: nowIso,
    });
  }

  saveLocalCautionAlerts(localAlerts);

  return { success: true, sent_at: nowIso };
}
