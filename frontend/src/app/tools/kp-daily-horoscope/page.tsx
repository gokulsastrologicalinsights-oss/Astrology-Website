"use client";

import React, { useState, useEffect, useCallback, useMemo } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  getKpDailyHoroscope,
  publishToFacebookPage,
  KpDailyHoroscopeResponse,
  RashiDailyPrediction,
  KpAspectPrediction,
  MoonSubLordWindow,
} from "@/lib/api";
import {
  Compass,
  Calendar,
  Clock,
  Sparkles,
  Search,
  CheckCircle2,
  AlertTriangle,
  Star,
  Zap,
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
  Info,
  ChevronRight,
  Flame,
  Copy,
  Check,
  Share2,
} from "lucide-react";

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

const ASPECT_ICONS: Record<string, string> = {
  career: "💼",
  finance: "💰",
  love: "❤️",
  health: "🩺",
  travel: "✈️",
};

const SENTIMENT_MAP_TA: Record<string, string> = {
  Excellent: "மிகச் சிறப்பான நாள்",
  Favorable: "சாதகமான நாள்",
  Mixed: "மிதமான நாள்",
  Challenging: "சவாலான நாள்",
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

  // Date selection state
  const [todayStr, setTodayStr] = useState<string>("");
  const [selectedDate, setSelectedDate] = useState<string>("");
  const [activeRashiId, setActiveRashiId] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [horoscopeData, setHoroscopeData] = useState<KpDailyHoroscopeResponse | null>(null);

  // Initialize date on mount
  useEffect(() => {
    const today = new Date().toISOString().split("T")[0];
    setTodayStr(today);
    setSelectedDate(today);
  }, []);

  const handleTomorrow = () => {
    const d = new Date();
    d.setDate(d.getDate() + 1);
    setSelectedDate(d.toISOString().split("T")[0]);
  };

  // Fetch horoscope data
  const loadData = useCallback(async (targetDate: string) => {
    if (!targetDate) return;
    try {
      setLoading(true);
      setError(null);
      const res = await getKpDailyHoroscope({ date: targetDate, rashi: "all", ayanamsa: 1 });
      setHoroscopeData(res);
    } catch (err: any) {
      console.error("Failed to load daily KP horoscope:", err);
      setError(err?.message || "Failed to calculate daily KP horoscope");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (selectedDate) {
      loadData(selectedDate);
    }
  }, [selectedDate, loadData]);

  // Current active prediction
  const activePrediction = useMemo<RashiDailyPrediction | null>(() => {
    if (!horoscopeData || !horoscopeData.predictions) return null;
    return horoscopeData.predictions.find((p) => p.rashi_id === activeRashiId) || horoscopeData.predictions[0];
  }, [horoscopeData, activeRashiId]);

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
    if (!activePrediction || !horoscopeData) return "";

    const rNameEn = `${activePrediction.rashi_name_en} (${activePrediction.rashi_name_ta})`;
    const rNameTa = `${activePrediction.rashi_name_ta} (${activePrediction.rashi_name_en})`;
    const symbol = RASHI_SYMBOLS[activePrediction.rashi_id] || "✨";
    const starsDisplay = Math.round(activePrediction.daily_rating_stars);
    const sentimentTa = SENTIMENT_MAP_TA[activePrediction.day_sentiment] || activePrediction.day_sentiment;
    const sentimentEn = activePrediction.day_sentiment;

    // Filter Moon Sub-Lord timings using en-dash " – "
    const goldenTimes =
      activePrediction.moon_sub_windows
        .filter((w) => w.sentiment === "golden")
        .map((w) => `${w.start_time} – ${w.end_time}`)
        .join(", ") || (activePrediction.golden_hour_window ? activePrediction.golden_hour_window.replace(/ - /g, " – ") : "");

    const cautionTimes =
      activePrediction.moon_sub_windows
        .filter((w) => w.sentiment === "caution")
        .map((w) => `${w.start_time} – ${w.end_time}`)
        .join(", ") || (activePrediction.caution_hour_window ? activePrediction.caution_hour_window.replace(/ - /g, " – ") : "");

    const luckyColorTa = activePrediction.lucky_color_ta.split("&")[0].trim() || activePrediction.lucky_color_ta;
    const luckyColorEn = activePrediction.lucky_color_en.split("&")[0].trim() || activePrediction.lucky_color_en;

    if (shareLanguage === "ta") {
      const formattedDateTa = formatTamilDate(horoscopeData.date, horoscopeData.day_of_week_ta);
      const aspectsTa = activePrediction.aspects
        .map((a) => {
          const icon = ASPECT_ICONS[a.aspect_code] || "•";
          const body = formatAspectTextTa(a.insight_ta, a.key_recommendation_ta);
          return `${icon} ${a.aspect_name_tamil} – ${a.score}%\n${body}`;
        })
        .join("\n\n");

      return `தினசரி ராசிபலன்
📅 தேதி: ${formattedDateTa}

${symbol} ${rNameTa} - ⭐ இன்றைய சாதக நிலை: ${activePrediction.daily_score}% (${starsDisplay}/5 – ${sentimentTa})

🔮 இன்றைய பொதுப்பலன்:

${cleanBrief(activePrediction.brief_statement_ta)}

📊 இன்றைய விரிவான பலன்கள்:

${aspectsTa}

⏰ இன்றைய நேர வழிகாட்டல்:

🌟 அதிர்ஷ்ட நேரம்: ${goldenTimes || "குறிப்பிட்ட சிறப்பான நேரம் இல்லை"}

⚠️ கவனமான நேரம்: ${cautionTimes || "குறிப்பிடத்தக்க எச்சரிக்கை நேரம் இல்லை"}

🎨 அதிர்ஷ்ட நிறம்: ${luckyColorTa}

🔢 அதிர்ஷ்ட எண்: ${activePrediction.lucky_number}

🧭 அதிர்ஷ்ட திசை: ${activePrediction.lucky_direction_ta}

🛡️ இன்றைய ஆலோசனை:

${activePrediction.daily_remedy_ta}

🙏 Gokul's Astrological Insights
Gokul Murugan | Thiruverkadu`;
    }

    if (shareLanguage === "en") {
      const formattedDateEn = formatEnglishDate(horoscopeData.date, horoscopeData.day_of_week);
      const aspectsEn = activePrediction.aspects
        .map((a) => {
          const icon = ASPECT_ICONS[a.aspect_code] || "•";
          const body = formatAspectTextEn(a.insight_en, a.key_recommendation_en);
          return `${icon} ${a.aspect_name} – ${a.score}%\n${body}`;
        })
        .join("\n\n");

      return `Daily Horoscope
📅 Date: ${formattedDateEn}

${symbol} ${rNameEn} - ⭐ Today's Energy Score: ${activePrediction.daily_score}% (${starsDisplay}/5 – ${sentimentEn} day)

🔮 Today's General Outlook:

${cleanBrief(activePrediction.brief_statement_en)}

📊 Today's Detailed Breakdown:

${aspectsEn}

⏰ Today's Timing Guidance:

🌟 Lucky Hours: ${goldenTimes || "No specific golden window"}

⚠️ Caution Hours: ${cautionTimes || "No major caution period"}

🎨 Lucky Color: ${luckyColorEn}

🔢 Lucky Number: ${activePrediction.lucky_number}

🧭 Lucky Direction: ${activePrediction.lucky_direction_en}

🛡️ Today's Guidance:

${activePrediction.daily_remedy_en}

🙏 Gokul's Astrological Insights
Gokul Murugan | Thiruverkadu`;
    }

    // Bilingual format
    const formattedDateBi = `${formatTamilDate(horoscopeData.date, horoscopeData.day_of_week_ta)} (${horoscopeData.day_of_week})`;
    const luckyColorBi = `${luckyColorTa} / ${luckyColorEn}`;

    const aspectsBi = activePrediction.aspects
      .map((a) => {
        const icon = ASPECT_ICONS[a.aspect_code] || "•";
        const bodyTa = formatAspectTextTa(a.insight_ta, a.key_recommendation_ta);
        const bodyEn = formatAspectTextEn(a.insight_en, a.key_recommendation_en);
        return `${icon} **${a.aspect_name_tamil} / ${a.aspect_name} – ${a.score}%**\n${bodyTa}\n(${bodyEn})`;
      })
      .join("\n\n");

    return `**Daily Horoscope | தினசரி ராசிபலன்**
📅 **Date / தேதி:** ${formattedDateBi}

${symbol} **${rNameTa}** - ⭐ **Score: ${activePrediction.daily_score}%** (${starsDisplay}/5 – ${sentimentTa})

🔮 **General Outlook / பொதுப்பலன்:**

${cleanBrief(activePrediction.brief_statement_ta)}
(${cleanBrief(activePrediction.brief_statement_en)})

📊 **Detailed Breakdown / விரிவான பலன்கள்:**

${aspectsBi}

⏰ **Timing Guidance / நேர வழிகாட்டல்:**

🌟 Lucky Hours / அதிர்ஷ்ட நேரம்: ${goldenTimes || "—"}

⚠️ Caution Hours / கவனமான நேரம்: ${cautionTimes || "—"}

🎨 Lucky Color / நிறம்: ${luckyColorBi}

🔢 Lucky Number / எண்: ${activePrediction.lucky_number}

🧭 Lucky Direction / திசை: ${activePrediction.lucky_direction_ta} (${activePrediction.lucky_direction_en})

🛡️ **Today's Guidance / ஆலோசனை:**

${activePrediction.daily_remedy_ta}
(${activePrediction.daily_remedy_en})

🙏 **Gokul's Astrological Insights**
*Gokul Murugan | Thiruverkadu*`;
  }, [activePrediction, horoscopeData, shareLanguage]);

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
    if (!horoscopeData || !activePrediction) return;
    setFbPosting(true);
    setFbResult(null);
    const isAll = rashiTarget === "all";
    try {
      const res = await publishToFacebookPage({
        date: horoscopeData.date,
        rashi: isAll ? "all" : activePrediction.rashi_name_en,
      });
      if (res.success) {
        if (isAll) {
          setFbResult({
            type: "success",
            text: isTa
              ? "12 ராசிகளின் தினசரி பலன்களும் வரிசையாக Facebook பக்கத்தில் பதிவிடப்பட்டன!"
              : "All 12 Rashis published successfully to your Facebook Page!",
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

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
      {/* Top Breadcrumb & Hero */}
      <div className="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Breadcrumbs
            items={[
              { label: isTa ? "முகப்பு" : "Home", href: "/" },
              { label: isTa ? "ஜோதிடக் கருவிகள்" : "Tools", href: "/tools" },
              { label: isTa ? "கே.பி. தினசரி ராசிபலன்" : "KP Daily Horoscope", href: "/tools/kp-daily-horoscope" },
            ]}
          />

          <div className="mt-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300 border border-purple-300 dark:border-purple-800">
                  {isTa ? "கே.பி. 249 உப-அதிபதி முறை" : "KP 249 Sub-Lord System"}
                </span>
                <span className="text-xs text-slate-500 flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  {isTa ? "நிகழ்நேர கோச்சாரம்" : "Real-time Transits"}
                </span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold mt-1 text-slate-900 dark:text-white">
                {isTa ? "தினசரி கே.பி. ராசிபலன்" : "KP Daily Transit Horoscope"}
              </h1>
              <p className="text-sm text-slate-600 dark:text-slate-400 mt-1 max-w-2xl">
                {isTa
                  ? "சந்திரனின் 249 உப-அதிபதி கோச்சாரம் மற்றும் பாவ காரகத்துவங்களின் அடிப்படையில் துல்லியமான தினசரி வழிகாட்டுதல்."
                  : "Accurate daily predictive forecast for all 12 Rashis based on real-time Moon sub-lord ingress and KP cuspal house significations."}
              </p>
            </div>

            {/* Date Quick Switcher */}
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
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Planetary Overview Banner */}
        {horoscopeData && (
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

        {/* 12 Rashis Selector Carousel / Grid */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-bold flex items-center gap-2">
              <Compass className="w-4 h-4 text-purple-600" />
              {isTa ? "ராசியைத் தேர்ந்தெடுக்கவும்" : "Select Your Rashi (Moon / Lagna Sign)"}
            </h2>
            <span className="text-xs text-slate-500">
              {isTa ? "12 ராசிகளின் கே.பி. கணிப்பு" : "12 Signs Available"}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-12 gap-2">
            {horoscopeData?.predictions.map((p) => {
              const isActive = p.rashi_id === activeRashiId;
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
                    {p.daily_score}%
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
              {isTa ? "கே.பி. உப-அதிபதி கோச்சாரம் கணக்கிடப்படுகிறது..." : "Calculating KP 249 sub-lord transits..."}
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
        {!loading && activePrediction && (
          <div className="space-y-8">
            {/* 1. Daily Executive Brief Statement Hero Card */}
            <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-purple-900 via-indigo-900 to-slate-950 text-white p-6 sm:p-8 shadow-xl">
              <div className="relative z-10 space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-5">
                  <div className="flex items-center gap-3">
                    <span className="text-4xl">{RASHI_SYMBOLS[activePrediction.rashi_id]}</span>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="text-2xl font-bold tracking-tight">
                          {isTa ? activePrediction.rashi_name_ta : activePrediction.rashi_name_en}
                        </h3>
                        <span className="text-xs px-2.5 py-0.5 rounded-full bg-white/15 text-purple-200 font-medium">
                          {isTa ? `ராசி நாதன்: ${activePrediction.sign_lord}` : `Lord: ${activePrediction.sign_lord}`}
                        </span>
                      </div>
                      <p className="text-xs text-purple-200 mt-0.5">
                        {isTa ? "இன்றைய தினசரி கே.பி. வழிகாட்டல்" : "Today's KP Executive Brief"}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 bg-white/10 backdrop-blur-md px-4 py-2.5 rounded-2xl border border-white/15">
                    <div>
                      <p className="text-[11px] text-purple-200 uppercase font-semibold">
                        {isTa ? "சாதக நிலை" : "Day Favorability"}
                      </p>
                      <div className="flex items-center gap-2">
                        <span className="text-2xl font-extrabold text-amber-300">
                          {activePrediction.daily_score}%
                        </span>
                        <div className="flex items-center text-amber-300 text-sm">
                          <Star className="w-4 h-4 fill-amber-300" />
                          <span className="ml-1 text-xs font-bold text-white">{activePrediction.daily_rating_stars}</span>
                        </div>
                      </div>
                    </div>
                    <span className="px-3 py-1 rounded-xl text-xs font-bold uppercase bg-white/20 text-white">
                      {activePrediction.day_sentiment}
                    </span>
                  </div>
                </div>

                {/* The Brief Statement */}
                <div className="bg-white/10 backdrop-blur-md p-5 rounded-2xl border border-white/15 space-y-2">
                  <p className="text-xs font-bold uppercase tracking-wider text-amber-300 flex items-center gap-1.5">
                    <Flame className="w-4 h-4 text-amber-300" />
                    {isTa ? "இன்றைய முக்கிய தாரக மந்திரம் / ஒரு வரி சுருக்கம்" : "Core Daily Punchline"}
                  </p>
                  <p className="text-base sm:text-lg font-semibold leading-relaxed text-slate-100">
                    "{isTa ? activePrediction.brief_statement_ta : activePrediction.brief_statement_en}"
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
                        {isTa ? "வெற்றி வாய்ப்பு (சிறப்பான அம்சம்)" : "Peak Opportunity (Where You Win)"}
                      </h4>
                      <p className="text-xs text-slate-200 mt-1 leading-relaxed">
                        {isTa ? activePrediction.peak_highlight_ta : activePrediction.peak_highlight_en}
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
                        {isTa ? activePrediction.caution_trap_ta : activePrediction.caution_trap_en}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Auspicious Slots & Lucky Attributes */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
                  <div className="bg-white/5 border border-white/10 p-3 rounded-xl">
                    <p className="text-[11px] text-purple-200">{isTa ? "பொன்னான நேரம்" : "Golden Hours"}</p>
                    <p className="text-xs font-bold text-amber-300 mt-0.5">{activePrediction.golden_hour_window}</p>
                  </div>
                  <div className="bg-white/5 border border-white/10 p-3 rounded-xl">
                    <p className="text-[11px] text-purple-200">{isTa ? "கவன நேரம்" : "Caution Hours"}</p>
                    <p className="text-xs font-bold text-rose-300 mt-0.5">{activePrediction.caution_hour_window}</p>
                  </div>
                  <div className="bg-white/5 border border-white/10 p-3 rounded-xl">
                    <p className="text-[11px] text-purple-200">{isTa ? "அதிர்ஷ்ட நிறம் & எண்" : "Lucky Color & No."}</p>
                    <p className="text-xs font-bold text-slate-100 mt-0.5">
                      {isTa ? activePrediction.lucky_color_ta : activePrediction.lucky_color_en} (#{activePrediction.lucky_number})
                    </p>
                  </div>
                  <div className="bg-white/5 border border-white/10 p-3 rounded-xl">
                    <p className="text-[11px] text-purple-200">{isTa ? "அதிர்ஷ்ட திசை" : "Lucky Direction"}</p>
                    <p className="text-xs font-bold text-slate-100 mt-0.5">
                      {isTa ? activePrediction.lucky_direction_ta : activePrediction.lucky_direction_en}
                    </p>
                  </div>
                </div>

                {/* KP Daily Remedy */}
                <div className="bg-purple-950/60 border border-purple-500/30 p-3.5 rounded-2xl flex items-center gap-3">
                  <ShieldCheck className="w-5 h-5 text-purple-300 flex-shrink-0" />
                  <p className="text-xs text-purple-200">
                    <span className="font-bold text-white mr-1.5">{isTa ? "கே.பி. பரிகார வழிகாட்டல்:" : "KP Daily Action:"}</span>
                    {isTa ? activePrediction.daily_remedy_ta : activePrediction.daily_remedy_en}
                  </p>
                </div>
              </div>
            </div>

            {/* 2. All 5 Life Aspects Detailed Analysis */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-purple-600" />
                  {isTa ? "அனைத்து அம்சங்களின் விரிவான பலன்கள்" : "In-Depth Life Aspects Analysis"}
                </h3>
                <span className="text-xs text-slate-500">
                  {isTa ? "காரகத்துவ பாவகங்கள் அடிப்படையில்" : "Cuspal Significations Breakdown"}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {activePrediction.aspects.map((aspect) => (
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

            {/* 3. Moon Sub-Lord Hourly Transit Windows */}
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
                {activePrediction.moon_sub_windows.map((win, idx) => {
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

            {/* 4. WhatsApp / Client Shareable Mini Summary Card (Copy & Paste Model) */}
            <div className="bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-slate-900 dark:to-purple-950/40 rounded-3xl border border-purple-200 dark:border-purple-800/60 p-6 sm:p-7 shadow-sm space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-purple-200/60 dark:border-purple-800/60 pb-4">
                <div className="flex items-center gap-2.5">
                  <div className="p-2.5 rounded-xl bg-purple-600 text-white shadow-sm">
                    <Share2 className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                      {isTa ? "வாட்ஸ்அப் / வாடிக்கையாளர் ஒருவரி சுருக்கம் (Copy & Paste)" : "Shareable Mini Paragraph Summary (Copy & Paste)"}
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {isTa
                        ? "வாடிக்கையாளர்கள் அல்லது குடும்பத்தினருக்கு பகிர ஒரே கிளிக்கில் நகலெடுக்கக்கூடிய தினசரி அறிக்கை."
                        : "One-click copy-ready format perfect for WhatsApp, SMS, or client briefings."}
                    </p>
                  </div>
                </div>

                {/* Language Format Toggle + Copy Button */}
                <div className="flex items-center gap-2 self-start sm:self-auto">
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

              {/* The Preformatted Text Box */}
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
