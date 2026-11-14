"use client";

import React, { useState, useEffect, useCallback, useMemo } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  getKpDailyHoroscope,
  getKpWeeklyHoroscope,
  getKpMonthlyHoroscope,
  publishToFacebookPage,
  KpDailyHoroscopeResponse,
  KpWeeklyHoroscopeResponse,
  KpMonthlyHoroscopeResponse,
  RashiDailyPrediction,
  RashiWeeklyPrediction,
  RashiMonthlyPrediction,
  KpAspectPrediction,
  MoonSubLordWindow,
  TransitMovement,
  TransitSummaryPerRashi,
} from "@/lib/api";
import {
  Compass,
  Calendar,
  Clock,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Star,
  Briefcase,
  Coins,
  Heart,
  Activity,
  Plane,
  ShieldCheck,
  RefreshCw,
  Sun,
  Moon,
  TrendingUp,
  Award,
  ChevronRight,
  ChevronLeft,
  Flame,
  Copy,
  Check,
  Share2,
  MessageCircle,
  CalendarDays,
  Globe,
  Radio,
  Layers,
} from "lucide-react";

type PeriodMode = "daily" | "weekly" | "monthly";

const RASHI_SYMBOLS: Record<number, string> = {
  1: "♈",
  2: "♉",
  3: "♊",
  4: "♋",
  5: "♌",
  6: "♍",
  7: "♎",
  8: "♏",
  9: "♐",
  10: "♑",
  11: "♒",
  12: "♓",
};

const PLANET_SYMBOLS: Record<string, string> = {
  Sun: "☀️",
  Moon: "🌙",
  Mars: "♂️",
  Mercury: "☿",
  Jupiter: "♃",
  Venus: "♀️",
  Saturn: "♄",
  Rahu: "☊",
  Ketu: "☋",
};

const ASPECT_ICONS: Record<string, string> = {
  career: "💼",
  finance: "💰",
  love: "❤️",
  health: "🩺",
  travel: "✈️",
};

const SENTIMENT_MAP_TA: Record<string, string> = {
  Excellent: "மிகச் சிறப்பான நிலை",
  Favorable: "சாதகமான நிலை",
  Mixed: "மிதமான நிலை",
  Challenging: "சவாலான நிலை",
};

const MONTHS_TA: Record<number, string> = {
  1: "ஜனவரி",
  2: "பிப்ரவரி",
  3: "மார்ச்",
  4: "ஏப்ரல்",
  5: "மே",
  6: "ஜூன்",
  7: "ஜூலை",
  8: "ஆகஸ்ட்",
  9: "செப்டம்பர்",
  10: "அக்டோபர்",
  11: "நவம்பர்",
  12: "டிசம்பர்",
};

const MONTHS_EN: Record<number, string> = {
  1: "January",
  2: "February",
  3: "March",
  4: "April",
  5: "May",
  6: "June",
  7: "July",
  8: "August",
  9: "September",
  10: "October",
  11: "November",
  12: "December",
};

function formatTamilDate(dateStr: string, dayTa: string): string {
  try {
    const parts = dateStr.split("-");
    if (parts.length === 3) {
      const year = parts[0];
      const month = parseInt(parts[1], 10);
      const day = parseInt(parts[2], 10);
      const mName = MONTHS_TA[month] || parts[1];
      return `${day} ${mName} ${year} – ${dayTa}`;
    }
  } catch {}
  return `${dateStr} – ${dayTa}`;
}

function formatEnglishDate(dateStr: string, dayEn: string): string {
  try {
    const parts = dateStr.split("-");
    if (parts.length === 3) {
      const year = parts[0];
      const month = parseInt(parts[1], 10);
      const day = parseInt(parts[2], 10);
      const mName = MONTHS_EN[month] || parts[1];
      return `${day} ${mName} ${year} – ${dayEn}`;
    }
  } catch {}
  return `${dateStr} – ${dayEn}`;
}

function cleanBrief(text: string): string {
  if (!text) return "";
  const cleaned = text.replace(/^.*?\):\s*/, "").replace(/^["']|["']$/g, "").trim();
  return cleaned || text;
}

function formatAspectTextTa(insight: string, rec: string): string {
  let clean = (insight || "")
    .replace(/(?:KP\s*பாவகங்கள்|(?:\d+(?:\s*அல்லது\s*\d+)?|\[[\d,\s]+\]|\{houses\}|\d+(?:,\s*\d+)*)-ம்\s*பாவக[^.;]*[.;]?)/gi, "")
    .replace(/\{houses\}/gi, "")
    .replace(/,\s*உப-அதிபதியின் ஆதிக்கத்தால்/g, "")
    .replace(/\s+/g, " ")
    .trim();

  if (clean.length < 35 && rec) {
    const recShort = rec.split(";")[0].trim().replace(/\.$/, "");
    if (recShort) {
      clean = clean ? `${clean.replace(/\.$/, "")}. ${recShort}.` : `${recShort}.`;
    }
  }
  return clean || rec || insight;
}

function formatAspectTextEn(insight: string, rec: string): string {
  let clean = (insight || "")
    .replace(/(?:Active KP houses|With houses|houses \d+|house \d+|KP houses)[^.;]*[.;]?/gi, "")
    .replace(/\{houses\}/gi, "")
    .replace(/\s+/g, " ")
    .trim();

  if (clean.length < 40 && rec) {
    const recShort = rec.split(";")[0].trim().replace(/\.$/, "");
    if (recShort) {
      clean = clean ? `${clean.replace(/\.$/, "")}. ${recShort}.` : `${recShort}.`;
    }
  }
  return clean || rec || insight;
}

export default function KpDailyHoroscopePage() {
  const { language } = useLanguage();
  const isTa = language === "ta";

  // Mode Selection State: Daily | Weekly | Monthly
  const [periodMode, setPeriodMode] = useState<PeriodMode>("daily");

  // Date selection state
  const [todayStr, setTodayStr] = useState<string>("");
  const [selectedDate, setSelectedDate] = useState<string>("");
  const [selectedWeekDate, setSelectedWeekDate] = useState<string>("");
  const [selectedYear, setSelectedYear] = useState<number>(2026);
  const [selectedMonth, setSelectedMonth] = useState<number>(11);

  // Active Rashi selection (1-12)
  const [activeRashiId, setActiveRashiId] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Data stores
  const [horoscopeData, setHoroscopeData] = useState<KpDailyHoroscopeResponse | null>(null);
  const [weeklyData, setWeeklyData] = useState<KpWeeklyHoroscopeResponse | null>(null);
  const [monthlyData, setMonthlyData] = useState<KpMonthlyHoroscopeResponse | null>(null);

  // Initialize dates on mount
  useEffect(() => {
    const today = new Date().toISOString().split("T")[0];
    const d = new Date();
    setTodayStr(today);
    setSelectedDate(today);
    setSelectedWeekDate(today);
    setSelectedYear(d.getFullYear());
    setSelectedMonth(d.getMonth() + 1);
  }, []);

  // Quick Daily navigation
  const handleTomorrow = () => {
    const d = new Date();
    d.setDate(d.getDate() + 1);
    setSelectedDate(d.toISOString().split("T")[0]);
  };

  // Quick Weekly navigation
  const handlePrevWeek = () => {
    if (!selectedWeekDate) return;
    const d = new Date(selectedWeekDate);
    d.setDate(d.getDate() - 7);
    setSelectedWeekDate(d.toISOString().split("T")[0]);
  };

  const handleNextWeek = () => {
    if (!selectedWeekDate) return;
    const d = new Date(selectedWeekDate);
    d.setDate(d.getDate() + 7);
    setSelectedWeekDate(d.toISOString().split("T")[0]);
  };

  const handleCurrentWeek = () => {
    if (!todayStr) return;
    setSelectedWeekDate(todayStr);
  };

  // Quick Monthly navigation
  const handlePrevMonth = () => {
    let m = selectedMonth - 1;
    let y = selectedYear;
    if (m < 1) {
      m = 12;
      y -= 1;
    }
    setSelectedMonth(m);
    setSelectedYear(y);
  };

  const handleNextMonth = () => {
    let m = selectedMonth + 1;
    let y = selectedYear;
    if (m > 12) {
      m = 1;
      y += 1;
    }
    setSelectedMonth(m);
    setSelectedYear(y);
  };

  const handleCurrentMonth = () => {
    const d = new Date();
    setSelectedYear(d.getFullYear());
    setSelectedMonth(d.getMonth() + 1);
  };

  // Fetch data depending on active mode
  const fetchHoroscope = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      if (periodMode === "daily") {
        if (!selectedDate) return;
        const res = await getKpDailyHoroscope({ date: selectedDate, rashi: "all", ayanamsa: 1 });
        setHoroscopeData(res);
      } else if (periodMode === "weekly") {
        if (!selectedWeekDate) return;
        const res = await getKpWeeklyHoroscope({ date: selectedWeekDate, rashi: "all", ayanamsa: 1 });
        setWeeklyData(res);
      } else if (periodMode === "monthly") {
        const res = await getKpMonthlyHoroscope({
          year: selectedYear,
          month: selectedMonth,
          rashi: "all",
          ayanamsa: 1,
        });
        setMonthlyData(res);
      }
    } catch (err: any) {
      console.error(`Failed to load ${periodMode} horoscope:`, err);
      setError(err?.message || `Failed to calculate ${periodMode} horoscope`);
    } finally {
      setLoading(false);
    }
  }, [periodMode, selectedDate, selectedWeekDate, selectedYear, selectedMonth]);

  useEffect(() => {
    fetchHoroscope();
  }, [fetchHoroscope]);

  // Current active prediction based on mode
  const activeDailyPrediction = useMemo<RashiDailyPrediction | null>(() => {
    if (!horoscopeData || !horoscopeData.predictions) return null;
    return horoscopeData.predictions.find((p) => p.rashi_id === activeRashiId) || horoscopeData.predictions[0];
  }, [horoscopeData, activeRashiId]);

  const activeWeeklyPrediction = useMemo<RashiWeeklyPrediction | null>(() => {
    if (!weeklyData || !weeklyData.predictions) return null;
    return weeklyData.predictions.find((p) => p.rashi_id === activeRashiId) || weeklyData.predictions[0];
  }, [weeklyData, activeRashiId]);

  const activeMonthlyPrediction = useMemo<RashiMonthlyPrediction | null>(() => {
    if (!monthlyData || !monthlyData.predictions) return null;
    return monthlyData.predictions.find((p) => p.rashi_id === activeRashiId) || monthlyData.predictions[0];
  }, [monthlyData, activeRashiId]);

  // Unified active card helper
  const activeGenericPrediction = useMemo(() => {
    if (periodMode === "daily") return activeDailyPrediction;
    if (periodMode === "weekly") return activeWeeklyPrediction;
    return activeMonthlyPrediction;
  }, [periodMode, activeDailyPrediction, activeWeeklyPrediction, activeMonthlyPrediction]);

  // Copy-paste summary state
  const [copied, setCopied] = useState<boolean>(false);
  const [shareLanguage, setShareLanguage] = useState<"ta" | "en" | "bilingual">("ta");
  const [fbPosting, setFbPosting] = useState<boolean>(false);
  const [fbResult, setFbResult] = useState<{ type: "success" | "error"; text: string; url?: string } | null>(null);

  // Synchronize initial shareLanguage with site language
  useEffect(() => {
    setShareLanguage(isTa ? "ta" : "en");
  }, [isTa]);

  // Formatted Mini Paragraph text for WhatsApp / Client Sharing
  const miniParagraphText = useMemo(() => {
    if (!activeGenericPrediction) return "";

    const symbol = RASHI_SYMBOLS[activeGenericPrediction.rashi_id] || "✨";
    const rNameEn = `${activeGenericPrediction.rashi_name_en} (${activeGenericPrediction.rashi_name_ta})`;
    const rNameTa = `${activeGenericPrediction.rashi_name_ta} (${activeGenericPrediction.rashi_name_en})`;

    // Lucky colors
    const luckyColorTa = activeGenericPrediction.lucky_color_ta.split("&")[0].trim() || activeGenericPrediction.lucky_color_ta;
    const luckyColorEn = activeGenericPrediction.lucky_color_en.split("&")[0].trim() || activeGenericPrediction.lucky_color_en;

    // ------------------------------------------------------------------------
    // 1. DAILY FORMAT
    // ------------------------------------------------------------------------
    if (periodMode === "daily" && activeDailyPrediction && horoscopeData) {
      const starsDisplay = Math.round(activeDailyPrediction.daily_rating_stars);
      const sentimentTa = SENTIMENT_MAP_TA[activeDailyPrediction.day_sentiment] || activeDailyPrediction.day_sentiment;
      const sentimentEn = activeDailyPrediction.day_sentiment;

      const goldenTimes =
        activeDailyPrediction.moon_sub_windows
          .filter((w) => w.sentiment === "golden")
          .map((w) => `${w.start_time} – ${w.end_time}`)
          .join(", ") || (activeDailyPrediction.golden_hour_window ? activeDailyPrediction.golden_hour_window.replace(/ - /g, " – ") : "");

      const cautionTimes =
        activeDailyPrediction.moon_sub_windows
          .filter((w) => w.sentiment === "caution")
          .map((w) => `${w.start_time} – ${w.end_time}`)
          .join(", ") || (activeDailyPrediction.caution_hour_window ? activeDailyPrediction.caution_hour_window.replace(/ - /g, " – ") : "");

      if (shareLanguage === "ta") {
        const formattedDateTa = formatTamilDate(horoscopeData.date, horoscopeData.day_of_week_ta);
        const aspectsTa = activeDailyPrediction.aspects
          .map((a) => {
            const icon = ASPECT_ICONS[a.aspect_code] || "•";
            const body = formatAspectTextTa(a.insight_ta, a.key_recommendation_ta);
            return `${icon} ${a.aspect_name_tamil} – ${a.score}%\n${body}`;
          })
          .join("\n\n");

        return `தினசரி ராசிபலன்
📅 தேதி: ${formattedDateTa}

${symbol} ${rNameTa} - ⭐ இன்றைய சாதக நிலை: ${activeDailyPrediction.daily_score}% (${starsDisplay}/5 – ${sentimentTa})

🔮 இன்றைய பொதுப்பலன்:

${cleanBrief(activeDailyPrediction.brief_statement_ta)}

📊 இன்றைய விரிவான பலன்கள்:

${aspectsTa}

⏰ இன்றைய நேர வழிகாட்டல்:

🌟 அதிர்ஷ்ட நேரம்: ${goldenTimes || "குறிப்பிட்ட சிறப்பான நேரம் இல்லை"}

⚠️ கவனமான நேரம்: ${cautionTimes || "குறிப்பிடத்தக்க எச்சரிக்கை நேரம் இல்லை"}

🎨 அதிர்ஷ்ட நிறம்: ${luckyColorTa}
🔢 அதிர்ஷ்ட எண்: ${activeDailyPrediction.lucky_number}
🧭 அதிர்ஷ்ட திசை: ${activeDailyPrediction.lucky_direction_ta}

🛡️ இன்றைய ஆலோசனை:
${activeDailyPrediction.daily_remedy_ta}

🙏 Gokul's Astrological Insights
Gokul Murugan | Thiruverkadu`;
      }

      if (shareLanguage === "en") {
        const formattedDateEn = formatEnglishDate(horoscopeData.date, horoscopeData.day_of_week);
        const aspectsEn = activeDailyPrediction.aspects
          .map((a) => {
            const icon = ASPECT_ICONS[a.aspect_code] || "•";
            const body = formatAspectTextEn(a.insight_en, a.key_recommendation_en);
            return `${icon} ${a.aspect_name} – ${a.score}%\n${body}`;
          })
          .join("\n\n");

        return `Daily Horoscope
📅 Date: ${formattedDateEn}

${symbol} ${rNameEn} - ⭐ Today's Energy Score: ${activeDailyPrediction.daily_score}% (${starsDisplay}/5 – ${sentimentEn} day)

🔮 Today's General Outlook:
${cleanBrief(activeDailyPrediction.brief_statement_en)}

📊 Today's Detailed Breakdown:
${aspectsEn}

⏰ Today's Timing Guidance:
🌟 Lucky Hours: ${goldenTimes || "No specific golden window"}
⚠️ Caution Hours: ${cautionTimes || "No major caution period"}

🎨 Lucky Color: ${luckyColorEn}
🔢 Lucky Number: ${activeDailyPrediction.lucky_number}
🧭 Lucky Direction: ${activeDailyPrediction.lucky_direction_en}

🛡️ Today's Guidance:
${activeDailyPrediction.daily_remedy_en}

🙏 Gokul's Astrological Insights
Gokul Murugan | Thiruverkadu`;
      }

      // Daily Bilingual
      const formattedDateBi = `${formatTamilDate(horoscopeData.date, horoscopeData.day_of_week_ta)} (${horoscopeData.day_of_week})`;
      return `Daily Horoscope | தினசரி ராசிபலன்
📅 ${formattedDateBi}

${symbol} ${rNameTa} - ⭐ Score: ${activeDailyPrediction.daily_score}% (${starsDisplay}/5 – ${sentimentTa})

🔮 General Outlook / பொதுப்பலன்:
${cleanBrief(activeDailyPrediction.brief_statement_ta)}
(${cleanBrief(activeDailyPrediction.brief_statement_en)})

⏰ Timing Guidance / நேர வழிகாட்டல்:
🌟 Lucky Hours / அதிர்ஷ்ட நேரம்: ${goldenTimes || "—"}
⚠️ Caution Hours / கவனமான நேரம்: ${cautionTimes || "—"}

🎨 Lucky Color: ${luckyColorTa} / ${luckyColorEn}
🔢 Lucky Number: ${activeDailyPrediction.lucky_number}
🧭 Lucky Direction: ${activeDailyPrediction.lucky_direction_ta}

🛡️ Guidance / ஆலோசனை:
${activeDailyPrediction.daily_remedy_ta}
(${activeDailyPrediction.daily_remedy_en})

🙏 Gokul's Astrological Insights | Gokul Murugan`;
    }

    // ------------------------------------------------------------------------
    // 2. WEEKLY FORMAT
    // ------------------------------------------------------------------------
    if (periodMode === "weekly" && activeWeeklyPrediction && weeklyData) {
      const starsDisplay = Math.round(activeWeeklyPrediction.weekly_rating_stars);
      const sentimentTa = SENTIMENT_MAP_TA[activeWeeklyPrediction.week_sentiment] || activeWeeklyPrediction.week_sentiment;
      const sentimentEn = activeWeeklyPrediction.week_sentiment;

      const aspectsTa = activeWeeklyPrediction.aspects
        .map((a) => {
          const icon = ASPECT_ICONS[a.aspect_code] || "•";
          const body = formatAspectTextTa(a.insight_ta, a.key_recommendation_ta);
          return `${icon} ${a.aspect_name_tamil} – ${a.score}%\n${body}`;
        })
        .join("\n\n");

      const aspectsEn = activeWeeklyPrediction.aspects
        .map((a) => {
          const icon = ASPECT_ICONS[a.aspect_code] || "•";
          const body = formatAspectTextEn(a.insight_en, a.key_recommendation_en);
          return `${icon} ${a.aspect_name} – ${a.score}%\n${body}`;
        })
        .join("\n\n");

      if (shareLanguage === "ta") {
        return `வார ராசிபலன் & கோச்சார சுருக்கம்
📅 வாரம்: ${weeklyData.week_label_ta}

${symbol} ${rNameTa} - ⭐ வார சாதக நிலை: ${activeWeeklyPrediction.weekly_score}% (${starsDisplay}/5 – ${sentimentTa})

🔮 வார பொதுப்பலன்:
${cleanBrief(activeWeeklyPrediction.brief_statement_ta)}

🪐 வாராந்திர கோச்சார தாக்கம்:
${activeWeeklyPrediction.transit_summary.transit_overview_ta}

⚠️ சந்திராஷ்டம நாட்கள்: ${activeWeeklyPrediction.chandrashtama_days_ta}
🌟 அதிர்ஷ்ட நாட்கள்: ${activeWeeklyPrediction.lucky_days_ta}

📊 விரிவான பலன்கள்:
${aspectsTa}

🎨 அதிர்ஷ்ட நிறம்: ${luckyColorTa}
🔢 அதிர்ஷ்ட எண்: ${activeWeeklyPrediction.lucky_number}
🧭 அதிர்ஷ்ட திசை: ${activeWeeklyPrediction.lucky_direction_ta}

🛡️ வார பரிகாரம்:
${activeWeeklyPrediction.weekly_remedy_ta}

🙏 Gokul's Astrological Insights
Gokul Murugan | Thiruverkadu`;
      }

      if (shareLanguage === "en") {
        return `Weekly Horoscope & Planetary Transit Forecast
📅 Week: ${weeklyData.week_label_en}

${symbol} ${rNameEn} - ⭐ Weekly Favorability: ${activeWeeklyPrediction.weekly_score}% (${starsDisplay}/5 – ${sentimentEn})

🔮 Weekly Executive Outlook:
${cleanBrief(activeWeeklyPrediction.brief_statement_en)}

🪐 Planetary Transit Influence:
${activeWeeklyPrediction.transit_summary.transit_overview_en}

⚠️ Caution / Chandrashtama Days: ${activeWeeklyPrediction.chandrashtama_days_en}
🌟 Favorable Days: ${activeWeeklyPrediction.lucky_days_en}

📊 Life Aspects Breakdown:
${aspectsEn}

🎨 Lucky Color: ${luckyColorEn}
🔢 Lucky Number: ${activeWeeklyPrediction.lucky_number}
🧭 Lucky Direction: ${activeWeeklyPrediction.lucky_direction_en}

🛡️ Weekly Guidance / Remedy:
${activeWeeklyPrediction.weekly_remedy_en}

🙏 Gokul's Astrological Insights
Gokul Murugan | Thiruverkadu`;
      }

      // Weekly Bilingual
      return `Weekly Horoscope | வார ராசிபலன்
📅 ${weeklyData.week_label_ta} (${weeklyData.week_label_en})

${symbol} ${rNameTa} - ⭐ Score: ${activeWeeklyPrediction.weekly_score}% (${starsDisplay}/5)

🔮 Weekly Summary / வார சுருக்கம்:
${cleanBrief(activeWeeklyPrediction.brief_statement_ta)}
(${cleanBrief(activeWeeklyPrediction.brief_statement_en)})

🪐 Planetary Transits / கோச்சார தாக்கம்:
${activeWeeklyPrediction.transit_summary.transit_overview_ta}

⚠️ Chandrashtama / சந்திராஷ்டமம்: ${activeWeeklyPrediction.chandrashtama_days_ta}
🌟 Lucky Days / அதிர்ஷ்ட நாட்கள்: ${activeWeeklyPrediction.lucky_days_ta}

🎨 Lucky Color: ${luckyColorTa} / ${luckyColorEn} | 🔢 No: ${activeWeeklyPrediction.lucky_number}
🧭 Direction / திசை: ${activeWeeklyPrediction.lucky_direction_ta}

🛡️ Weekly Remedy / வார பரிகாரம்:
${activeWeeklyPrediction.weekly_remedy_ta}

🙏 Gokul's Astrological Insights | Gokul Murugan`;
    }

    // ------------------------------------------------------------------------
    // 3. MONTHLY FORMAT
    // ------------------------------------------------------------------------
    if (periodMode === "monthly" && activeMonthlyPrediction && monthlyData) {
      const starsDisplay = Math.round(activeMonthlyPrediction.monthly_rating_stars);
      const sentimentTa = SENTIMENT_MAP_TA[activeMonthlyPrediction.month_sentiment] || activeMonthlyPrediction.month_sentiment;
      const sentimentEn = activeMonthlyPrediction.month_sentiment;

      const aspectsTa = activeMonthlyPrediction.aspects
        .map((a) => {
          const icon = ASPECT_ICONS[a.aspect_code] || "•";
          const body = formatAspectTextTa(a.insight_ta, a.key_recommendation_ta);
          return `${icon} ${a.aspect_name_tamil} – ${a.score}%\n${body}`;
        })
        .join("\n\n");

      const aspectsEn = activeMonthlyPrediction.aspects
        .map((a) => {
          const icon = ASPECT_ICONS[a.aspect_code] || "•";
          const body = formatAspectTextEn(a.insight_en, a.key_recommendation_en);
          return `${icon} ${a.aspect_name} – ${a.score}%\n${body}`;
        })
        .join("\n\n");

      if (shareLanguage === "ta") {
        return `மாத ராசிபலன் & கோச்சார சுருக்கம்
📅 மாதம்: ${monthlyData.month_name_ta}

${symbol} ${rNameTa} - ⭐ மாதாந்திர சாதக நிலை: ${activeMonthlyPrediction.monthly_score}% (${starsDisplay}/5 – ${sentimentTa})

🔮 மாதாந்திர பொதுப்பலன்:
${cleanBrief(activeMonthlyPrediction.brief_statement_ta)}

🪐 மாதாந்திர கோச்சார பலன்கள் & பெயர்ச்சி சுருக்கம்:
${activeMonthlyPrediction.transit_summary.transit_overview_ta}

⚠️ சந்திராஷ்டம தேதிகள்: ${activeMonthlyPrediction.chandrashtama_dates_ta}
🌟 சுப தேதிகள்: ${activeMonthlyPrediction.auspicious_dates_ta}

📊 விரிவான பலன்கள்:
${aspectsTa}

🎨 அதிர்ஷ்ட நிறம்: ${luckyColorTa}
🔢 அதிர்ஷ்ட எண்: ${activeMonthlyPrediction.lucky_number}
🧭 அதிர்ஷ்ட திசை: ${activeMonthlyPrediction.lucky_direction_ta}

🛡️ மாதாந்திர பரிகாரம்:
${activeMonthlyPrediction.monthly_remedy_ta}

🙏 Gokul's Astrological Insights
Gokul Murugan | Thiruverkadu`;
      }

      if (shareLanguage === "en") {
        return `Monthly Horoscope & Planetary Transit Forecast
📅 Month: ${monthlyData.month_name_en}

${symbol} ${rNameEn} - ⭐ Monthly Favorability: ${activeMonthlyPrediction.monthly_score}% (${starsDisplay}/5 – ${sentimentEn})

🔮 Monthly Executive Summary:
${cleanBrief(activeMonthlyPrediction.brief_statement_en)}

🪐 Planetary Transit Influence & Summary:
${activeMonthlyPrediction.transit_summary.transit_overview_en}

⚠️ Chandrashtama Dates: ${activeMonthlyPrediction.chandrashtama_dates_en}
🌟 Auspicious Dates: ${activeMonthlyPrediction.auspicious_dates_en}

📊 Life Aspects Breakdown:
${aspectsEn}

🎨 Lucky Color: ${luckyColorEn}
🔢 Lucky Number: ${activeMonthlyPrediction.lucky_number}
🧭 Lucky Direction: ${activeMonthlyPrediction.lucky_direction_en}

🛡️ Monthly Remedy / Guidance:
${activeMonthlyPrediction.monthly_remedy_en}

🙏 Gokul's Astrological Insights
Gokul Murugan | Thiruverkadu`;
      }

      // Monthly Bilingual
      return `Monthly Horoscope | மாத ராசிபலன்
📅 ${monthlyData.month_name_ta} (${monthlyData.month_name_en})

${symbol} ${rNameTa} - ⭐ Score: ${activeMonthlyPrediction.monthly_score}% (${starsDisplay}/5)

🔮 Monthly Outlook / மாதப் பொதுப்பலன்:
${cleanBrief(activeMonthlyPrediction.brief_statement_ta)}
(${cleanBrief(activeMonthlyPrediction.brief_statement_en)})

🪐 Transit Overview / கோச்சார சுருக்கம்:
${activeMonthlyPrediction.transit_summary.transit_overview_ta}

⚠️ Chandrashtama / சந்திராஷ்டமம்: ${activeMonthlyPrediction.chandrashtama_dates_ta}
🌟 Auspicious Dates / சுப தேதிகள்: ${activeMonthlyPrediction.auspicious_dates_ta}

🎨 Lucky Color: ${luckyColorTa} / ${luckyColorEn} | 🔢 No: ${activeMonthlyPrediction.lucky_number}
🧭 Direction / திசை: ${activeMonthlyPrediction.lucky_direction_ta}

🛡️ Monthly Remedy / மாத பரிகாரம்:
${activeMonthlyPrediction.monthly_remedy_ta}

🙏 Gokul's Astrological Insights | Gokul Murugan`;
    }

    return "";
  }, [
    periodMode,
    activeGenericPrediction,
    activeDailyPrediction,
    activeWeeklyPrediction,
    activeMonthlyPrediction,
    horoscopeData,
    weeklyData,
    monthlyData,
    shareLanguage,
  ]);

  const handleCopy = async () => {
    if (!miniParagraphText) return;
    try {
      await navigator.clipboard.writeText(miniParagraphText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch (e) {
      console.error("Failed to copy text:", e);
    }
  };

  const handlePostToFacebook = async (rashiTarget: string = "current") => {
    if (!activeGenericPrediction) return;
    setFbPosting(true);
    setFbResult(null);
    const isAll = rashiTarget === "all";
    const postDate =
      periodMode === "daily"
        ? horoscopeData?.date || todayStr
        : periodMode === "weekly"
        ? weeklyData?.start_date || selectedWeekDate
        : `${selectedYear}-${String(selectedMonth).padStart(2, "0")}-01`;

    try {
      const res = await publishToFacebookPage({
        date: postDate,
        rashi: isAll ? "all" : activeGenericPrediction.rashi_name_en,
      });
      if (res.success) {
        if (isAll) {
          setFbResult({
            type: "success",
            text: isTa
              ? `12 ராசிகளின் ${periodMode === "weekly" ? "வார" : periodMode === "monthly" ? "மாத" : "தினசரி"} ராசிபலனும் Facebook பக்கத்தில் பதிவிடப்பட்டன!`
              : `All 12 Rashis published to your Facebook Page!`,
          });
        } else {
          setFbResult({
            type: "success",
            text: isTa
              ? `Facebook பக்கத்தில் வெற்றிகரமாகப் பதிவிடப்பட்டது! (Post ID: ${res.post_id || "OK"})`
              : `Successfully published to Facebook Page! (Post ID: ${res.post_id || "OK"})`,
            url: res.fb_url,
          });
        }
      } else {
        setFbResult({
          type: "error",
          text: isTa ? "Facebook-ல் பதிவிட முடியவில்லை." : "Could not post to Facebook Page.",
        });
      }
    } catch (err: any) {
      setFbResult({
        type: "error",
        text:
          err?.message ||
          (isTa
            ? "Facebook API பிழை ஏற்பட்டது. தயவுசெய்து backend .env அமைப்புகளைச் சரிபார்க்கவும்."
            : "Facebook API error. Please check your backend .env FB_PAGE_ID and FB_PAGE_ACCESS_TOKEN."),
      });
    } finally {
      setFbPosting(false);
    }
  };

  const handleShareWhatsApp = (mode: "current" | "all" = "current") => {
    let textToSend = miniParagraphText;

    if (mode === "all") {
      const periodTitleTa = periodMode === "weekly" ? "வார ராசிபலன் (12 ராசிகள்)" : periodMode === "monthly" ? "மாத ராசிபலன் (12 ராசிகள்)" : "தினசரி ராசிபலன் (12 ராசிகள்)";
      const dateHeader =
        periodMode === "weekly"
          ? `📅 வாரம்: ${weeklyData?.week_label_ta || ""}`
          : periodMode === "monthly"
          ? `📅 மாதம்: ${monthlyData?.month_name_ta || ""}`
          : `📅 தேதி: ${horoscopeData ? formatTamilDate(horoscopeData.date, horoscopeData.day_of_week_ta) : ""}`;

      const listItems: string[] = [];
      const listData =
        periodMode === "daily"
          ? horoscopeData?.predictions
          : periodMode === "weekly"
          ? weeklyData?.predictions
          : monthlyData?.predictions;

      if (listData) {
        for (const p of listData) {
          const rName = `${p.rashi_name_ta} (${p.rashi_name_en})`;
          const symbol = RASHI_SYMBOLS[p.rashi_id] || "✨";
          const score = (p as any).daily_score ?? (p as any).weekly_score ?? (p as any).monthly_score;
          const stars = Math.round((p as any).daily_rating_stars ?? (p as any).weekly_rating_stars ?? (p as any).monthly_rating_stars);
          const brief = cleanBrief(p.brief_statement_ta);
          listItems.push(`${symbol} ${rName} - சாதக நிலை: ${score}% (⭐ ${stars}/5)\n${brief}`);
        }
      }

      textToSend = `${periodTitleTa}\n${dateHeader}\n\n${listItems.join("\n\n------------------------------\n\n")}\n\n🙏 Gokul's Astrological Insights\nGokul Murugan | Thiruverkadu`;
    }

    if (!textToSend) return;
    const encoded = encodeURIComponent(textToSend);
    window.open(`https://api.whatsapp.com/send?text=${encoded}`, "_blank");
  };

  const getAspectIcon = (code: string) => {
    switch (code) {
      case "career":
        return <Briefcase className="w-5 h-5 text-blue-500" />;
      case "finance":
        return <Coins className="w-5 h-5 text-emerald-500" />;
      case "love":
        return <Heart className="w-5 h-5 text-rose-500" />;
      case "health":
        return <Activity className="w-5 h-5 text-amber-500" />;
      case "travel":
        return <Plane className="w-5 h-5 text-indigo-500" />;
      default:
        return <Sparkles className="w-5 h-5 text-purple-500" />;
    }
  };

  const getSentimentBadge = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case "excellent":
        return "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800";
      case "favorable":
        return "bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300 border-blue-300 dark:border-blue-800";
      case "mixed":
        return "bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300 border-amber-300 dark:border-amber-800";
      default:
        return "bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300 border-rose-300 dark:border-rose-800";
    }
  };

  // Helper for active predictions list to map over the 12 rashis
  const currentRashiPredictions = useMemo(() => {
    if (periodMode === "daily") return horoscopeData?.predictions || [];
    if (periodMode === "weekly") return weeklyData?.predictions || [];
    return monthlyData?.predictions || [];
  }, [periodMode, horoscopeData, weeklyData, monthlyData]);

  // Overall favorability score of active prediction
  const activeScore = useMemo(() => {
    if (!activeGenericPrediction) return 50;
    if ("daily_score" in activeGenericPrediction) return activeGenericPrediction.daily_score;
    if ("weekly_score" in activeGenericPrediction) return activeGenericPrediction.weekly_score;
    if ("monthly_score" in activeGenericPrediction) return activeGenericPrediction.monthly_score;
    return 50;
  }, [activeGenericPrediction]);

  const activeRatingStars = useMemo(() => {
    if (!activeGenericPrediction) return 3.0;
    if ("daily_rating_stars" in activeGenericPrediction) return activeGenericPrediction.daily_rating_stars;
    if ("weekly_rating_stars" in activeGenericPrediction) return activeGenericPrediction.weekly_rating_stars;
    if ("monthly_rating_stars" in activeGenericPrediction) return activeGenericPrediction.monthly_rating_stars;
    return 3.0;
  }, [activeGenericPrediction]);

  const activeSentiment = useMemo(() => {
    if (!activeGenericPrediction) return "Favorable";
    if ("day_sentiment" in activeGenericPrediction) return activeGenericPrediction.day_sentiment;
    if ("week_sentiment" in activeGenericPrediction) return activeGenericPrediction.week_sentiment;
    if ("month_sentiment" in activeGenericPrediction) return activeGenericPrediction.month_sentiment;
    return "Favorable";
  }, [activeGenericPrediction]);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
      {/* Top Breadcrumb & Hero */}
      <div className="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Breadcrumbs
            items={[
              { label: isTa ? "முகப்பு" : "Home", href: "/" },
              { label: isTa ? "ஜோதிடக் கருவிகள்" : "Tools", href: "/tools" },
              {
                label:
                  periodMode === "weekly"
                    ? isTa
                      ? "வார ராசிபலன்"
                      : "Weekly Horoscope"
                    : periodMode === "monthly"
                    ? isTa
                      ? "மாத ராசிபலன்"
                      : "Monthly Horoscope"
                    : isTa
                    ? "தினசரி ராசிபலன்"
                    : "Daily Horoscope",
                href: "/tools/kp-daily-horoscope",
              },
            ]}
          />

          <div className="mt-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300 border border-purple-300 dark:border-purple-800">
                  {isTa ? "கே.பி. & கோச்சார முறை" : "KP & Transit Forecaster"}
                </span>
                <span className="text-xs text-slate-500 flex items-center gap-1">
                  <Globe className="w-3.5 h-3.5 text-purple-500" />
                  {isTa ? "நிகழ்நேர கிரகப் பெயர்ச்சிகள்" : "Live Planetary Transits"}
                </span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold mt-1 text-slate-900 dark:text-white flex items-center gap-2.5">
                {periodMode === "weekly" ? (
                  <>
                    <CalendarDays className="w-7 h-7 text-purple-600" />
                    <span>{isTa ? "வார ராசிபலன் & கோச்சார சுருக்கம்" : "Weekly Horoscope & Transit Prediction"}</span>
                  </>
                ) : periodMode === "monthly" ? (
                  <>
                    <Layers className="w-7 h-7 text-indigo-600" />
                    <span>{isTa ? "மாத ராசிபலன் & கோச்சார சுருக்கம்" : "Monthly Horoscope & Transit Forecast"}</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-7 h-7 text-purple-600" />
                    <span>{isTa ? "தினசரி கே.பி. ராசிபலன்" : "KP Daily Transit Horoscope"}</span>
                  </>
                )}
              </h1>
              <p className="text-sm text-slate-600 dark:text-slate-400 mt-1 max-w-2xl">
                {periodMode === "weekly"
                  ? isTa
                    ? "12 ராசிகளுக்குமான வாராந்திர கிரகப் பெயர்ச்சிகள், கோச்சார பலன் சுருக்கம், சந்திராஷ்டமம் மற்றும் விரிவான 5 அம்ச பலன்கள்."
                    : "Comprehensive weekly predictions for all 12 Rashis with planetary transit movements, house Gochara impacts, and Chandrashtama alerts."
                  : periodMode === "monthly"
                  ? isTa
                    ? "12 ராசிகளுக்குமான மாதாந்திர சூரியன், குரு, சனி உள்ளிட்ட முக்கிய பெயர்ச்சிகள், சுப தேதிகள் மற்றும் கோச்சார தாக்கம்."
                    : "In-depth monthly forecasts with major planetary shifts (Sun, Jupiter, Saturn, Rahu-Ketu), auspicious dates, and transit synthesis."
                  : isTa
                  ? "சந்திரனின் 249 உப-அதிபதி கோச்சாரம் மற்றும் பாவ காரகத்துவங்களின் அடிப்படையில் துல்லியமான தினசரி வழிகாட்டுதல்."
                  : "Accurate daily predictive forecast for all 12 Rashis based on real-time Moon sub-lord ingress and KP cuspal house significations."}
              </p>
            </div>

            {/* PERIOD MODE TABS (Daily / Weekly / Monthly) */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
              <div className="flex p-1 bg-slate-100 dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-inner">
                <button
                  type="button"
                  onClick={() => setPeriodMode("daily")}
                  className={`flex-1 sm:flex-none px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                    periodMode === "daily"
                      ? "bg-purple-600 text-white shadow-sm scale-[1.02]"
                      : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                  }`}
                >
                  <Clock className="w-3.5 h-3.5" />
                  <span>{isTa ? "தினசரி" : "Daily"}</span>
                </button>

                <button
                  type="button"
                  onClick={() => setPeriodMode("weekly")}
                  className={`flex-1 sm:flex-none px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                    periodMode === "weekly"
                      ? "bg-purple-600 text-white shadow-sm scale-[1.02]"
                      : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                  }`}
                >
                  <CalendarDays className="w-3.5 h-3.5" />
                  <span>{isTa ? "வார ராசிபலன்" : "Weekly"}</span>
                </button>

                <button
                  type="button"
                  onClick={() => setPeriodMode("monthly")}
                  className={`flex-1 sm:flex-none px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                    periodMode === "monthly"
                      ? "bg-purple-600 text-white shadow-sm scale-[1.02]"
                      : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                  }`}
                >
                  <Layers className="w-3.5 h-3.5" />
                  <span>{isTa ? "மாத ராசிபலன்" : "Monthly"}</span>
                </button>
              </div>
            </div>
          </div>

          {/* DATE / PERIOD NAVIGATION BAR */}
          <div className="mt-4 pt-4 border-t border-slate-200/60 dark:border-slate-800/60 flex flex-wrap items-center justify-between gap-3">
            {periodMode === "daily" ? (
              <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800/80 p-1.5 rounded-xl border border-slate-200 dark:border-slate-700">
                <button
                  type="button"
                  onClick={() => setSelectedDate(todayStr)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                    selectedDate === todayStr
                      ? "bg-purple-600 text-white shadow-sm"
                      : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                  }`}
                >
                  {isTa ? "இன்று" : "Today"}
                </button>
                <button
                  type="button"
                  onClick={handleTomorrow}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                    selectedDate && selectedDate !== todayStr
                      ? "bg-purple-600 text-white shadow-sm"
                      : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                  }`}
                >
                  {isTa ? "நாளை" : "Tomorrow"}
                </button>
                <div className="flex items-center gap-1.5 pl-2 border-l border-slate-300 dark:border-slate-700">
                  <Calendar className="w-4 h-4 text-slate-400" />
                  <input
                    type="date"
                    value={selectedDate}
                    onChange={(e) => setSelectedDate(e.target.value)}
                    className="bg-transparent text-xs font-medium focus:outline-none text-slate-800 dark:text-slate-200 cursor-pointer"
                  />
                </div>
              </div>
            ) : periodMode === "weekly" ? (
              <div className="flex flex-wrap items-center gap-2">
                <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800/80 p-1 rounded-xl border border-slate-200 dark:border-slate-700">
                  <button
                    type="button"
                    onClick={handlePrevWeek}
                    className="p-1.5 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 transition"
                    title={isTa ? "முந்தைய வாரம்" : "Previous Week"}
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <button
                    type="button"
                    onClick={handleCurrentWeek}
                    className="px-2.5 py-1 rounded-lg text-xs font-semibold text-purple-700 dark:text-purple-300 hover:bg-purple-50 dark:hover:bg-purple-950/60 transition"
                  >
                    {isTa ? "இந்த வாரம்" : "Current Week"}
                  </button>
                  <button
                    type="button"
                    onClick={handleNextWeek}
                    className="p-1.5 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 transition"
                    title={isTa ? "அடுத்த வாரம்" : "Next Week"}
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>

                {weeklyData && (
                  <span className="px-3 py-1.5 rounded-xl bg-purple-50 dark:bg-purple-950/50 border border-purple-200 dark:border-purple-800 text-xs font-bold text-purple-700 dark:text-purple-300 flex items-center gap-1.5 shadow-sm">
                    <CalendarDays className="w-3.5 h-3.5 text-purple-600" />
                    {isTa ? weeklyData.week_label_ta : weeklyData.week_label_en}
                  </span>
                )}

                <div className="flex items-center gap-1.5 pl-2 bg-slate-100 dark:bg-slate-800/80 p-1.5 rounded-xl border border-slate-200 dark:border-slate-700">
                  <span className="text-[11px] text-slate-500 font-medium">{isTa ? "வாரம் மாற்ற:" : "Jump to:"}</span>
                  <input
                    type="date"
                    value={selectedWeekDate}
                    onChange={(e) => setSelectedWeekDate(e.target.value)}
                    className="bg-transparent text-xs font-medium focus:outline-none text-slate-800 dark:text-slate-200 cursor-pointer"
                  />
                </div>
              </div>
            ) : (
              <div className="flex flex-wrap items-center gap-2">
                <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800/80 p-1 rounded-xl border border-slate-200 dark:border-slate-700">
                  <button
                    type="button"
                    onClick={handlePrevMonth}
                    className="p-1.5 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 transition"
                    title={isTa ? "முந்தைய மாதம்" : "Previous Month"}
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <button
                    type="button"
                    onClick={handleCurrentMonth}
                    className="px-2.5 py-1 rounded-lg text-xs font-semibold text-indigo-700 dark:text-indigo-300 hover:bg-indigo-50 dark:hover:bg-indigo-950/60 transition"
                  >
                    {isTa ? "இந்த மாதம்" : "Current Month"}
                  </button>
                  <button
                    type="button"
                    onClick={handleNextMonth}
                    className="p-1.5 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 transition"
                    title={isTa ? "அடுத்த மாதம்" : "Next Month"}
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>

                {monthlyData && (
                  <span className="px-3 py-1.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/50 border border-indigo-200 dark:border-indigo-800 text-xs font-bold text-indigo-700 dark:text-indigo-300 flex items-center gap-1.5 shadow-sm">
                    <Layers className="w-3.5 h-3.5 text-indigo-600" />
                    {isTa ? monthlyData.month_name_ta : monthlyData.month_name_en}
                  </span>
                )}

                {/* Month Picker dropdown */}
                <div className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-800/80 p-1.5 rounded-xl border border-slate-200 dark:border-slate-700 text-xs">
                  <select
                    value={selectedMonth}
                    onChange={(e) => setSelectedMonth(parseInt(e.target.value, 10))}
                    className="bg-transparent font-medium text-slate-800 dark:text-slate-200 focus:outline-none cursor-pointer"
                  >
                    {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
                      <option key={m} value={m} className="dark:bg-slate-900">
                        {isTa ? MONTHS_TA[m] : MONTHS_EN[m]}
                      </option>
                    ))}
                  </select>
                  <select
                    value={selectedYear}
                    onChange={(e) => setSelectedYear(parseInt(e.target.value, 10))}
                    className="bg-transparent font-medium text-slate-800 dark:text-slate-200 focus:outline-none cursor-pointer border-l border-slate-300 dark:border-slate-700 pl-1.5"
                  >
                    {[2024, 2025, 2026, 2027, 2028].map((y) => (
                      <option key={y} value={y} className="dark:bg-slate-900">
                        {y}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            )}

            <div className="text-xs text-slate-500 font-medium">
              {isTa ? "துல்லியமான கே.பி. & எபிமெரிஸ் கணிப்பு" : "KP Ephemeris & Gochara Engine"}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Planetary Overview Banner (Daily Mode) */}
        {periodMode === "daily" && horoscopeData && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-white dark:bg-slate-900 rounded-2xl p-4 border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400">
                <Sun className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs text-slate-500">{isTa ? "கிழமை அதிபதி" : "Day Lord"}</p>
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                  {horoscopeData.day_lord} ({isTa ? horoscopeData.day_of_week_ta : horoscopeData.day_of_week})
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-blue-100 dark:bg-blue-950/60 text-blue-700 dark:text-blue-400">
                <Moon className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs text-slate-500">{isTa ? "சந்திரன் ராசி" : "Moon Sign"}</p>
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                  {horoscopeData.moon_sign_at_noon}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-indigo-100 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-400">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs text-slate-500">{isTa ? "சந்திரன் நட்சத்திரம்" : "Moon Star"}</p>
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                  {horoscopeData.moon_star_at_noon}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-purple-100 dark:bg-purple-950/60 text-purple-700 dark:text-purple-400">
                <Award className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs text-slate-500">{isTa ? "மதிய உப-அதிபதி" : "Midday Sub-Lord"}</p>
                <p className="text-sm font-semibold text-purple-600 dark:text-purple-400">
                  {horoscopeData.moon_sub_lord_at_noon}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Major Transits Highlight Bar (Weekly / Monthly Mode) */}
        {periodMode !== "daily" && (
          <div className="bg-gradient-to-r from-purple-950/70 via-indigo-950/70 to-slate-900 rounded-2xl p-4 sm:p-5 border border-purple-800/50 shadow-md text-white">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-purple-600/40 text-purple-300 border border-purple-500/40">
                  <Globe className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    {periodMode === "weekly"
                      ? isTa
                        ? "வாராந்திர கிரகப் பெயர்ச்சி நிலைகள்"
                        : "Planetary Transits for the Week"
                      : isTa
                      ? "மாதாந்திர முக்கிய கிரகப் பெயர்ச்சிகள்"
                      : "Major Planetary Shifts of the Month"}
                  </h3>
                  <p className="text-xs text-purple-200 mt-0.5">
                    {periodMode === "weekly"
                      ? isTa
                        ? `${weeklyData?.week_label_ta || ""} வாரத்தில் நிகழ்நேர கிரக நிலைகள் & பெயர்ச்சி சுருக்கம்.`
                        : `Real-time transit ingresses & Gochara alignments for ${weeklyData?.week_label_en || ""}.`
                      : isTa
                      ? `${monthlyData?.month_name_ta || ""} மாதத்தில் சூரியன், குரு, சனி உள்ளிட்ட முக்கிய கோச்சாரம்.`
                      : `Major transit alignments governing ${monthlyData?.month_name_en || ""}.`}
                  </p>
                </div>
              </div>

              {/* Major Transits tags */}
              <div className="flex flex-wrap items-center gap-2">
                {((periodMode === "weekly" ? weeklyData?.major_transits : monthlyData?.major_transits) || [])
                  .slice(0, 4)
                  .map((tm, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 rounded-xl bg-white/10 text-[11px] font-semibold border border-white/15 text-purple-200 flex items-center gap-1.5"
                    >
                      <span>{PLANET_SYMBOLS[tm.planet] || "🪐"}</span>
                      <span>
                        {isTa ? tm.planet_ta : tm.planet}: {isTa ? tm.current_sign_ta : tm.current_sign}
                      </span>
                    </span>
                  ))}
              </div>
            </div>
          </div>
        )}

        {/* 12 Rashis Selector Carousel / Grid */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-bold flex items-center gap-2">
              <Compass className="w-4 h-4 text-purple-600" />
              {isTa ? "ராசியைத் தேர்ந்தெடுக்கவும்" : "Select Your Rashi (Moon / Lagna Sign)"}
            </h2>
            <span className="text-xs text-slate-500">
              {periodMode === "weekly"
                ? isTa
                  ? "12 ராசிகளின் வார ராசிபலன்"
                  : "Weekly Predictions for All 12 Signs"
                : periodMode === "monthly"
                ? isTa
                  ? "12 ராசிகளின் மாத ராசிபலன்"
                  : "Monthly Predictions for All 12 Signs"
                : isTa
                ? "12 ராசிகளின் தினசரி கே.பி. கணிப்பு"
                : "12 Signs Available"}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-12 gap-2">
            {currentRashiPredictions.map((p) => {
              const isActive = p.rashi_id === activeRashiId;
              const score = (p as any).daily_score ?? (p as any).weekly_score ?? (p as any).monthly_score ?? 50;

              return (
                <button
                  key={p.rashi_id}
                  type="button"
                  onClick={() => setActiveRashiId(p.rashi_id)}
                  className={`flex flex-col items-center justify-center p-3 rounded-2xl border transition-all ${
                    isActive
                      ? "bg-purple-600 text-white border-purple-500 shadow-md shadow-purple-500/20 scale-[1.03]"
                      : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-purple-300 dark:hover:border-purple-800 text-slate-700 dark:text-slate-300"
                  }`}
                >
                  <span className="text-xl mb-1">{RASHI_SYMBOLS[p.rashi_id]}</span>
                  <span className="text-xs font-bold leading-tight">
                    {isTa ? p.rashi_name_ta : p.rashi_name_en}
                  </span>
                  <span
                    className={`mt-1 text-[10px] px-1.5 py-0.5 rounded-full font-semibold ${
                      isActive
                        ? "bg-purple-500/80 text-white"
                        : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                    }`}
                  >
                    {score}%
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Loading / Error States */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-20 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800">
            <RefreshCw className="w-8 h-8 text-purple-600 animate-spin mb-3" />
            <p className="text-sm font-medium text-slate-600 dark:text-slate-400">
              {periodMode === "weekly"
                ? isTa
                  ? "வார ராசிபலன் & கோச்சார பெயர்ச்சிகள் கணக்கிடப்படுகிறது..."
                  : "Calculating weekly horoscope and planetary transits..."
                : periodMode === "monthly"
                ? isTa
                  ? "மாத ராசிபலன் & கோச்சார பலன்கள் கணக்கிடப்படுகிறது..."
                  : "Calculating monthly horoscope and Gochara transits..."
                : isTa
                ? "கே.பி. உப-அதிபதி கோச்சாரம் கணக்கிடப்படுகிறது..."
                : "Calculating KP 249 sub-lord transits..."}
            </p>
          </div>
        )}

        {error && (
          <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900 text-rose-800 dark:text-rose-300 flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
            <p className="text-sm font-medium">{error}</p>
          </div>
        )}

        {/* Active Prediction Main View */}
        {!loading && activeGenericPrediction && (
          <div className="space-y-8">
            {/* 1. Executive Brief Statement Hero Card */}
            <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-purple-900 via-indigo-900 to-slate-950 text-white p-6 sm:p-8 shadow-xl">
              <div className="relative z-10 space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-5">
                  <div className="flex items-center gap-3">
                    <span className="text-4xl">{RASHI_SYMBOLS[activeGenericPrediction.rashi_id]}</span>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="text-2xl font-bold tracking-tight">
                          {isTa ? activeGenericPrediction.rashi_name_ta : activeGenericPrediction.rashi_name_en}
                        </h3>
                        <span className="text-xs px-2.5 py-0.5 rounded-full bg-white/15 text-purple-200 font-medium">
                          {isTa ? `ராசி நாதன்: ${activeGenericPrediction.sign_lord}` : `Lord: ${activeGenericPrediction.sign_lord}`}
                        </span>
                      </div>
                      <p className="text-xs text-purple-200 mt-0.5">
                        {periodMode === "weekly"
                          ? isTa
                            ? `வார ராசிபலன் வழிகாட்டல் (${weeklyData?.week_label_ta || ""})`
                            : `Weekly Forecast (${weeklyData?.week_label_en || ""})`
                          : periodMode === "monthly"
                          ? isTa
                            ? `மாத ராசிபலன் வழிகாட்டல் (${monthlyData?.month_name_ta || ""})`
                            : `Monthly Forecast (${monthlyData?.month_name_en || ""})`
                          : isTa
                          ? "இன்றைய தினசரி கே.பி. வழிகாட்டல்"
                          : "Today's KP Executive Brief"}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 bg-white/10 backdrop-blur-md px-4 py-2.5 rounded-2xl border border-white/15">
                    <div>
                      <p className="text-[11px] text-purple-200 uppercase font-semibold">
                        {periodMode === "weekly"
                          ? isTa
                            ? "வார சாதக நிலை"
                            : "Week Favorability"
                          : periodMode === "monthly"
                          ? isTa
                            ? "மாத சாதக நிலை"
                            : "Month Favorability"
                          : isTa
                          ? "சாதக நிலை"
                          : "Day Favorability"}
                      </p>
                      <div className="flex items-center gap-2">
                        <span className="text-2xl font-extrabold text-amber-300">
                          {activeScore}%
                        </span>
                        <div className="flex items-center text-amber-300 text-sm">
                          <Star className="w-4 h-4 fill-amber-300" />
                          <span className="ml-1 text-xs font-bold text-white">{activeRatingStars}</span>
                        </div>
                      </div>
                    </div>
                    <span className="px-3 py-1 rounded-xl text-xs font-bold uppercase bg-white/20 text-white">
                      {activeSentiment}
                    </span>
                  </div>
                </div>

                {/* The Brief Statement */}
                <div className="bg-white/10 backdrop-blur-md p-5 rounded-2xl border border-white/15 space-y-2">
                  <p className="text-xs font-bold uppercase tracking-wider text-amber-300 flex items-center gap-1.5">
                    <Flame className="w-4 h-4 text-amber-300" />
                    {periodMode === "weekly"
                      ? isTa
                        ? "வாரத்தின் முக்கிய தாரக மந்திரம் / பொதுப்பலன்"
                        : "Weekly Executive Punchline"
                      : periodMode === "monthly"
                      ? isTa
                        ? "மாதாந்திர முக்கிய தாரக மந்திரம் / பொதுப்பலன்"
                        : "Monthly Executive Punchline"
                      : isTa
                      ? "இன்றைய முக்கிய தாரக மந்திரம் / ஒரு வரி சுருக்கம்"
                      : "Core Daily Punchline"}
                  </p>
                  <p className="text-base sm:text-lg font-semibold leading-relaxed text-slate-100">
                    "{isTa ? activeGenericPrediction.brief_statement_ta : activeGenericPrediction.brief_statement_en}"
                  </p>
                </div>

                {/* Highlight & Caution Pillars */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-emerald-950/40 border border-emerald-500/30 p-4 rounded-2xl flex items-start gap-3">
                    <div className="p-2 rounded-xl bg-emerald-500/20 text-emerald-300 flex-shrink-0 mt-0.5">
                      <Sparkles className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-300">
                        {isTa ? "வெற்றி வாய்ப்பு (சிறப்பான திருப்புமுனை)" : "Peak Opportunity (Where You Win)"}
                      </h4>
                      <p className="text-xs text-slate-200 mt-1 leading-relaxed">
                        {isTa ? activeGenericPrediction.peak_highlight_ta : activeGenericPrediction.peak_highlight_en}
                      </p>
                    </div>
                  </div>

                  <div className="bg-rose-950/40 border border-rose-500/30 p-4 rounded-2xl flex items-start gap-3">
                    <div className="p-2 rounded-xl bg-rose-500/20 text-rose-300 flex-shrink-0 mt-0.5">
                      <AlertTriangle className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-xs font-bold uppercase tracking-wider text-rose-300">
                        {isTa ? "கவனிக்க வேண்டிய பகுதி (தவிர்க்க வேண்டியவை)" : "Watch Out / Caution Trap"}
                      </h4>
                      <p className="text-xs text-slate-200 mt-1 leading-relaxed">
                        {isTa ? activeGenericPrediction.caution_trap_ta : activeGenericPrediction.caution_trap_en}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Auspicious Slots & Lucky Attributes */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
                  {periodMode === "daily" && activeDailyPrediction ? (
                    <>
                      <div className="bg-white/5 border border-white/10 p-3 rounded-xl">
                        <p className="text-[11px] text-purple-200">{isTa ? "பொன்னான நேரம்" : "Golden Hours"}</p>
                        <p className="text-xs font-bold text-amber-300 mt-0.5">{activeDailyPrediction.golden_hour_window}</p>
                      </div>
                      <div className="bg-white/5 border border-white/10 p-3 rounded-xl">
                        <p className="text-[11px] text-purple-200">{isTa ? "கவன நேரம்" : "Caution Hours"}</p>
                        <p className="text-xs font-bold text-rose-300 mt-0.5">{activeDailyPrediction.caution_hour_window}</p>
                      </div>
                    </>
                  ) : periodMode === "weekly" && activeWeeklyPrediction ? (
                    <>
                      <div className="bg-white/5 border border-white/10 p-3 rounded-xl">
                        <p className="text-[11px] text-purple-200">{isTa ? "அதிர்ஷ்ட நாட்கள்" : "Favorable Days"}</p>
                        <p className="text-xs font-bold text-amber-300 mt-0.5">{isTa ? activeWeeklyPrediction.lucky_days_ta : activeWeeklyPrediction.lucky_days_en}</p>
                      </div>
                      <div className="bg-white/5 border border-white/10 p-3 rounded-xl">
                        <p className="text-[11px] text-purple-200">{isTa ? "சந்திராஷ்டம நாட்கள்" : "Caution / Chandrashtama"}</p>
                        <p className="text-xs font-bold text-rose-300 mt-0.5">{isTa ? activeWeeklyPrediction.chandrashtama_days_ta : activeWeeklyPrediction.chandrashtama_days_en}</p>
                      </div>
                    </>
                  ) : activeMonthlyPrediction ? (
                    <>
                      <div className="bg-white/5 border border-white/10 p-3 rounded-xl">
                        <p className="text-[11px] text-purple-200">{isTa ? "சுப தேதிகள்" : "Auspicious Dates"}</p>
                        <p className="text-xs font-bold text-amber-300 mt-0.5">{isTa ? activeMonthlyPrediction.auspicious_dates_ta : activeMonthlyPrediction.auspicious_dates_en}</p>
                      </div>
                      <div className="bg-white/5 border border-white/10 p-3 rounded-xl">
                        <p className="text-[11px] text-purple-200">{isTa ? "சந்திராஷ்டம தேதிகள்" : "Chandrashtama Dates"}</p>
                        <p className="text-xs font-bold text-rose-300 mt-0.5">{isTa ? activeMonthlyPrediction.chandrashtama_dates_ta : activeMonthlyPrediction.chandrashtama_dates_en}</p>
                      </div>
                    </>
                  ) : null}

                  <div className="bg-white/5 border border-white/10 p-3 rounded-xl">
                    <p className="text-[11px] text-purple-200">{isTa ? "அதிர்ஷ்ட நிறம் & எண்" : "Lucky Color & No."}</p>
                    <p className="text-xs font-bold text-slate-100 mt-0.5">
                      {isTa ? activeGenericPrediction.lucky_color_ta : activeGenericPrediction.lucky_color_en} (#{activeGenericPrediction.lucky_number})
                    </p>
                  </div>
                  <div className="bg-white/5 border border-white/10 p-3 rounded-xl">
                    <p className="text-[11px] text-purple-200">{isTa ? "அதிர்ஷ்ட திசை" : "Lucky Direction"}</p>
                    <p className="text-xs font-bold text-slate-100 mt-0.5">
                      {isTa ? activeGenericPrediction.lucky_direction_ta : activeGenericPrediction.lucky_direction_en}
                    </p>
                  </div>
                </div>

                {/* Period Remedy */}
                <div className="bg-purple-950/60 border border-purple-500/30 p-3.5 rounded-2xl flex items-center gap-3">
                  <ShieldCheck className="w-5 h-5 text-purple-300 flex-shrink-0" />
                  <p className="text-xs text-purple-200">
                    <span className="font-bold text-white mr-1.5">
                      {periodMode === "weekly"
                        ? isTa
                          ? "வார பரிகார வழிகாட்டல்:"
                          : "Weekly Remedy & Guidance:"
                        : periodMode === "monthly"
                        ? isTa
                          ? "மாதாந்திர பரிகார வழிகாட்டல்:"
                          : "Monthly Remedy & Guidance:"
                        : isTa
                        ? "கே.பி. தினசரி பரிகாரம்:"
                        : "KP Daily Action:"}
                    </span>
                    {periodMode === "weekly" && activeWeeklyPrediction
                      ? isTa
                        ? activeWeeklyPrediction.weekly_remedy_ta
                        : activeWeeklyPrediction.weekly_remedy_en
                      : periodMode === "monthly" && activeMonthlyPrediction
                      ? isTa
                        ? activeMonthlyPrediction.monthly_remedy_ta
                        : activeMonthlyPrediction.monthly_remedy_en
                      : activeDailyPrediction
                      ? isTa
                        ? activeDailyPrediction.daily_remedy_ta
                        : activeDailyPrediction.daily_remedy_en
                      : ""}
                  </p>
                </div>
              </div>
            </div>

            {/* 2. PLANETARY TRANSITS & GOCHARA ANALYSIS SECTION (WEEKLY & MONTHLY) */}
            {(periodMode === "weekly" || periodMode === "monthly") && (
              <div className="space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div>
                    <h3 className="text-lg font-bold flex items-center gap-2">
                      <Globe className="w-5 h-5 text-purple-600" />
                      {periodMode === "weekly"
                        ? isTa
                          ? "வாராந்திர கோச்சார பலன் சுருக்கம் & கிரக நிலைகள்"
                          : "Weekly Transit Analysis & Gochara Positions"
                        : isTa
                        ? "மாதாந்திர கோச்சார பலன் சுருக்கம் & கிரக நிலைகள்"
                        : "Monthly Transit Analysis & Gochara Positions"}
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {isTa
                        ? "உங்கள் ராசிக்குரிய 9 கிரகங்களின் கோச்சார அமைப்புகள், சுப பலன்கள் மற்றும் எச்சரிக்கை வழிகாட்டல்."
                        : "House-by-house planetary Gochara influence and executive transit synthesis for your sign."}
                    </p>
                  </div>
                </div>

                {/* Synthesis Overview Card */}
                {("transit_summary" in activeGenericPrediction) && (
                  <div className="bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-slate-900 dark:to-purple-950/40 rounded-2xl border border-purple-200 dark:border-purple-800/60 p-5 shadow-sm space-y-4">
                    <div>
                      <p className="text-xs font-bold uppercase tracking-wider text-purple-700 dark:text-purple-300 flex items-center gap-1.5">
                        <Sparkles className="w-4 h-4 text-purple-600" />
                        {isTa ? "கோச்சார தாக்கம் & பலன் சுருக்கம்" : "Planetary Transit Synthesis & Impact Summary"}
                      </p>
                      <p className="text-xs sm:text-sm text-slate-700 dark:text-slate-300 mt-2 leading-relaxed">
                        {isTa
                          ? activeGenericPrediction.transit_summary.transit_overview_ta
                          : activeGenericPrediction.transit_summary.transit_overview_en}
                      </p>
                    </div>

                    {/* Special Yogas & Chandrashtama Badges */}
                    <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-purple-200/50 dark:border-purple-800/50">
                      {activeGenericPrediction.transit_summary.special_yogas_ta &&
                        (isTa
                          ? activeGenericPrediction.transit_summary.special_yogas_ta
                          : activeGenericPrediction.transit_summary.special_yogas_en
                        ).map((yoga, yIdx) => (
                          <span
                            key={yIdx}
                            className="px-2.5 py-1 rounded-xl bg-purple-100 dark:bg-purple-900/60 text-purple-800 dark:text-purple-200 text-xs font-semibold border border-purple-300 dark:border-purple-700 flex items-center gap-1"
                          >
                            <Award className="w-3.5 h-3.5 text-purple-600 dark:text-purple-300" />
                            {yoga}
                          </span>
                        ))}

                      {activeGenericPrediction.transit_summary.chandrashtama_period_ta && (
                        <span className="px-2.5 py-1 rounded-xl bg-rose-100 dark:bg-rose-950/60 text-rose-800 dark:text-rose-200 text-xs font-semibold border border-rose-300 dark:border-rose-800 flex items-center gap-1">
                          <AlertTriangle className="w-3.5 h-3.5 text-rose-600" />
                          <span>
                            {isTa ? "சந்திராஷ்டமம்:" : "Chandrashtama:"}{" "}
                            {isTa
                              ? activeGenericPrediction.transit_summary.chandrashtama_period_ta
                              : activeGenericPrediction.transit_summary.chandrashtama_period_en}
                          </span>
                        </span>
                      )}
                    </div>

                    {/* Planetary Movements Grid */}
                    <div className="pt-2">
                      <p className="text-xs font-semibold text-slate-500 mb-2.5">
                        {isTa ? "கிரகங்களின் கோச்சார ஸ்தானங்கள் & பலன்கள்:" : "Individual Planetary Placements & Influences:"}
                      </p>
                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                        {activeGenericPrediction.transit_summary.planet_transits.map((tm, tmIdx) => {
                          const isFav = tm.status === "favorable";
                          const isCaution = tm.status === "caution";
                          return (
                            <div
                              key={tmIdx}
                              className={`p-3.5 rounded-xl border transition-all ${
                                isFav
                                  ? "bg-emerald-50/50 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800"
                                  : isCaution
                                  ? "bg-rose-50/50 dark:bg-rose-950/20 border-rose-200 dark:border-rose-800"
                                  : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800"
                              }`}
                            >
                              <div className="flex items-center justify-between mb-1.5">
                                <div className="flex items-center gap-2">
                                  <span className="text-base">{PLANET_SYMBOLS[tm.planet] || "🪐"}</span>
                                  <div>
                                    <span className="text-xs font-bold text-slate-900 dark:text-white">
                                      {isTa ? tm.planet_ta : tm.planet}
                                    </span>
                                    <span className="text-[11px] text-slate-500 ml-1.5">
                                      ({isTa ? tm.current_sign_ta : tm.current_sign})
                                    </span>
                                  </div>
                                </div>
                                <span
                                  className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${
                                    isFav
                                      ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
                                      : isCaution
                                      ? "bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300"
                                      : "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300"
                                  }`}
                                >
                                  {isTa
                                    ? isFav
                                      ? `${tm.house_relative}-ம் பாவம் (நன்மை)`
                                      : isCaution
                                      ? `${tm.house_relative}-ம் பாவம் (கவனம்)`
                                      : `${tm.house_relative}-ம் பாவம் (சமம்)`
                                    : `${tm.house_relative}th House (${tm.status})`}
                                </span>
                              </div>

                              {tm.transit_ingress_event && (
                                <p className="text-[11px] font-semibold text-purple-600 dark:text-purple-400 mb-1">
                                  ⚡ {tm.transit_ingress_event}
                                </p>
                              )}

                              <p className="text-xs text-slate-600 dark:text-slate-400 leading-normal">
                                {isTa ? tm.impact_summary_ta : tm.impact_summary_en}
                              </p>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* 3. All 5 Life Aspects Detailed Analysis */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-purple-600" />
                  {isTa ? "அனைத்து அம்சங்களின் விரிவான பலன்கள்" : "In-Depth Life Aspects Analysis"}
                </h3>
                <span className="text-xs text-slate-500">
                  {isTa ? "காரகத்துவ பாவகங்கள் & கோச்சார அடிப்படையில்" : "Cuspal & Transit Breakdown"}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {activeGenericPrediction.aspects.map((aspect) => (
                  <div
                    key={aspect.aspect_code}
                    className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm space-y-4 hover:border-purple-300 dark:hover:border-purple-800 transition"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2.5">
                        <div className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800">
                          {getAspectIcon(aspect.aspect_code)}
                        </div>
                        <div>
                          <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                            {isTa ? aspect.aspect_name_tamil : aspect.aspect_name}
                          </h4>
                          <span className="text-[11px] text-slate-500">
                            {isTa ? "பாவகங்கள்: " : "Houses: "}
                            {aspect.signified_houses.join(", ")}
                          </span>
                        </div>
                      </div>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-semibold border ${getSentimentBadge(aspect.status)}`}>
                        {aspect.status}
                      </span>
                    </div>

                    {/* Score Bar */}
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-slate-500">{isTa ? "மதிப்பெண்" : "Score"}</span>
                        <span className="font-bold text-slate-800 dark:text-slate-200">{aspect.score}%</span>
                      </div>
                      <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-purple-500 to-indigo-600 rounded-full transition-all duration-500"
                          style={{ width: `${aspect.score}%` }}
                        />
                      </div>
                    </div>

                    {/* Insight */}
                    <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                      {isTa ? aspect.insight_ta : aspect.insight_en}
                    </p>

                    {/* Recommendation */}
                    <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                      <p className="text-[11px] text-slate-700 dark:text-slate-300 font-medium leading-normal">
                        {isTa ? aspect.key_recommendation_ta : aspect.key_recommendation_en}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 4. Moon Sub-Lord Hourly Transit Windows (Daily Mode Only) */}
            {periodMode === "daily" && activeDailyPrediction && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-bold flex items-center gap-2">
                      <Clock className="w-5 h-5 text-purple-600" />
                      {isTa ? "சந்திரனின் மணி நேர உப-அதிபதி கால அட்டவணை" : "Moon's Hourly KP Sub-Lord Schedule"}
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {isTa
                        ? "ஒவ்வொரு மணி நேரத்திலும் சந்திரனின் உப-அதிபதி மாற்றத்தால் ஏற்படும் நன்மை / எச்சரிக்கை நேரங்கள்."
                        : "Hourly shifts in the Moon's sub-lord triggering specific house combinations for your sign."}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 text-xs">
                    <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-medium">
                      <span className="w-2 h-2 rounded-full bg-emerald-500" />
                      {isTa ? "பொன்னான நேரம்" : "Golden"}
                    </span>
                    <span className="flex items-center gap-1 text-rose-600 dark:text-rose-400 font-medium">
                      <span className="w-2 h-2 rounded-full bg-rose-500" />
                      {isTa ? "கவன நேரம்" : "Caution"}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {activeDailyPrediction.moon_sub_windows.map((win, idx) => {
                    const isGolden = win.sentiment === "golden";
                    const isCaution = win.sentiment === "caution";
                    return (
                      <div
                        key={idx}
                        className={`p-4 rounded-2xl border transition-all ${
                          isGolden
                            ? "bg-emerald-50/60 dark:bg-emerald-950/30 border-emerald-300 dark:border-emerald-800"
                            : isCaution
                            ? "bg-rose-50/60 dark:bg-rose-950/30 border-rose-300 dark:border-rose-800"
                            : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800"
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                            <Clock className="w-3.5 h-3.5 text-purple-500" />
                            {win.start_time} - {win.end_time}
                          </span>
                          <span
                            className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                              isGolden
                                ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
                                : isCaution
                                ? "bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300"
                                : "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300"
                            }`}
                          >
                            {win.sentiment}
                          </span>
                        </div>

                        <div className="text-xs text-slate-600 dark:text-slate-400 mb-2">
                          <span className="font-semibold text-slate-900 dark:text-white">
                            {win.sub_lord} Sub
                          </span>{" "}
                          ({win.star_name} - {win.star_lord} Star)
                          {win.activated_houses.length > 0 && (
                            <span className="ml-1 text-slate-500">
                              • {isTa ? "பாவகங்கள்: " : "Houses: "}
                              {win.activated_houses.join(", ")}
                            </span>
                          )}
                        </div>

                        <p className="text-xs text-slate-700 dark:text-slate-300 font-medium">
                          {isTa ? win.advice_ta : win.advice_en}
                        </p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* 5. WhatsApp / Client Shareable Mini Summary Card (Copy & Paste Model) */}
            <div className="bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-slate-900 dark:to-purple-950/40 rounded-3xl border border-purple-200 dark:border-purple-800/60 p-6 sm:p-7 shadow-sm space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-purple-200/60 dark:border-purple-800/60 pb-4">
                <div className="flex items-center gap-2.5">
                  <div className="p-2.5 rounded-xl bg-purple-600 text-white shadow-sm">
                    <Share2 className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                      {isTa
                        ? `${periodMode === "weekly" ? "வார" : periodMode === "monthly" ? "மாத" : "தினசரி"} ராசிபலன் பகிர்வு (Copy & Paste)`
                        : `Shareable ${periodMode === "weekly" ? "Weekly" : periodMode === "monthly" ? "Monthly" : "Daily"} Summary (Copy & Paste)`}
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {isTa
                        ? "வாடிக்கையாளர்கள் அல்லது சமூக ஊடகங்களில் பகிர ஒரே கிளிக்கில் நகலெடுக்கக்கூடிய முழுமையான அறிக்கை."
                        : "One-click copy-ready format perfect for WhatsApp, SMS, or client briefings."}
                    </p>
                  </div>
                </div>

                {/* Language Format Toggle + Copy Button */}
                <div className="flex flex-wrap items-center gap-2 self-start sm:self-auto">
                  <div className="flex bg-white dark:bg-slate-800 p-1 rounded-xl border border-slate-200 dark:border-slate-700 text-xs">
                    <button
                      type="button"
                      onClick={() => setShareLanguage("ta")}
                      className={`px-2.5 py-1 rounded-lg font-medium transition ${
                        shareLanguage === "ta"
                          ? "bg-purple-600 text-white"
                          : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                      }`}
                    >
                      தமிழ்
                    </button>
                    <button
                      type="button"
                      onClick={() => setShareLanguage("en")}
                      className={`px-2.5 py-1 rounded-lg font-medium transition ${
                        shareLanguage === "en"
                          ? "bg-purple-600 text-white"
                          : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                      }`}
                    >
                      English
                    </button>
                    <button
                      type="button"
                      onClick={() => setShareLanguage("bilingual")}
                      className={`px-2.5 py-1 rounded-lg font-medium transition ${
                        shareLanguage === "bilingual"
                          ? "bg-purple-600 text-white"
                          : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                      }`}
                    >
                      இருமொழி
                    </button>
                  </div>

                  <button
                    type="button"
                    onClick={handleCopy}
                    className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white text-xs font-semibold shadow-sm transition active:scale-95"
                  >
                    {copied ? (
                      <>
                        <Check className="w-4 h-4 text-emerald-300" />
                        <span>{isTa ? "நகலெடுக்கப்பட்டது!" : "Copied!"}</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-4 h-4" />
                        <span>{isTa ? "சுருக்கத்தை நகலெடு" : "Copy Summary"}</span>
                      </>
                    )}
                  </button>

                  <button
                    type="button"
                    onClick={() => handleShareWhatsApp("current")}
                    className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-sm transition active:scale-95"
                    title={isTa ? "இந்த ராசிபலனை WhatsApp குரூப்பில் 1-கிளிக்கில் பகிரு" : "Share this Rashi to WhatsApp"}
                  >
                    <MessageCircle className="w-4 h-4" />
                    <span>{isTa ? "WhatsApp-ல் பகிரு" : "WhatsApp"}</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => handleShareWhatsApp("all")}
                    className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white text-xs font-semibold shadow-sm transition active:scale-95"
                    title={isTa ? "12 ராசிகளின் சுருக்கத்தையும் WhatsApp குரூப்பில் பகிரு" : "Share all 12 Rashis to WhatsApp"}
                  >
                    <MessageCircle className="w-4 h-4" />
                    <span>{isTa ? "12-ம் WhatsApp" : "All 12 WhatsApp"}</span>
                  </button>

                  <button
                    type="button"
                    disabled={fbPosting}
                    onClick={() => handlePostToFacebook("current")}
                    className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-xs font-semibold shadow-sm transition active:scale-95"
                    title={isTa ? "இந்த ராசியை மட்டும் Facebook-ல் பதிவிடு" : "Post this Rashi to Facebook"}
                  >
                    {fbPosting ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        <span>{isTa ? "பதிவிடுகிறது..." : "Posting..."}</span>
                      </>
                    ) : (
                      <>
                        <Share2 className="w-4 h-4" />
                        <span>{isTa ? "FB-ல் பதிவிடு" : "Post to Facebook"}</span>
                      </>
                    )}
                  </button>

                  <button
                    type="button"
                    disabled={fbPosting}
                    onClick={() => handlePostToFacebook("all")}
                    className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-xs font-semibold shadow-sm transition active:scale-95"
                    title={isTa ? "12 ராசிகளையும் வரிசையாக Facebook-ல் பதிவிடு" : "Post All 12 Rashis to Facebook"}
                  >
                    {fbPosting ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        <span>{isTa ? "பதிவிடுகிறது..." : "Posting..."}</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4" />
                        <span>{isTa ? "12 ராசிகளையும் FB-ல் பதிவிடு" : "Post All 12 to FB"}</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Facebook Posting Result Banner */}
              {fbResult && (
                <div
                  className={`p-3 rounded-xl text-xs sm:text-sm flex items-center justify-between border ${
                    fbResult.type === "success"
                      ? "bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800"
                      : "bg-rose-50 dark:bg-rose-950/40 text-rose-800 dark:text-rose-300 border-rose-300 dark:border-rose-800"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    {fbResult.type === "success" ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                    ) : (
                      <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
                    )}
                    <span>{fbResult.text}</span>
                  </div>
                  {fbResult.url && (
                    <a
                      href={fbResult.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="ml-3 underline font-semibold shrink-0 hover:opacity-80"
                    >
                      {isTa ? "பதிவைப் பார் ↗" : "View Post ↗"}
                    </a>
                  )}
                </div>
              )}

              {/* Preformatted Text Box */}
              <div className="relative">
                <pre className="p-4 sm:p-5 rounded-2xl bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-xs sm:text-sm font-mono text-slate-800 dark:text-slate-200 whitespace-pre-wrap leading-relaxed shadow-inner overflow-x-auto">
                  {miniParagraphText}
                </pre>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
