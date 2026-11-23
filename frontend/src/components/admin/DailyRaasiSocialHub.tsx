"use client";

import React, { useEffect, useState, useTransition } from "react";
import {
  Share2,
  Download,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Send,
  Sparkles,
  Copy,
  Check,
  Eye,
  Calendar,
  Layers,
  MessageCircle,
} from "lucide-react";
import { useLanguage } from "@/lib/i18n";

interface SocialStatusResponse {
  credentials?: {
    configured: boolean;
    valid: boolean;
    page_id?: string;
    page_name?: string;
    page_link?: string;
  };
  instagram?: {
    configured: boolean;
    valid: boolean;
    ig_user_id?: string;
    username?: string;
    name?: string;
  };
  telegram?: {
    configured: boolean;
    valid: boolean;
    bot_username?: string;
    chat_id?: string;
    error?: string;
  };
  scheduler?: {
    auto_post_enabled: boolean;
    is_running: boolean;
    in_progress: boolean;
    post_time_ist: string;
    post_mode: string;
    next_run_ist: string;
    last_run?: {
      last_run_time?: string;
      last_posted_date?: string;
      status?: string;
      post_id?: string;
      error?: string;
    };
  };
}

export const WHATSAPP_CHANNEL_URL = "https://whatsapp.com/channel/0029Vb98kyhD8SDrF4PozB0L";

export const RASHIS = [
  { id: 1, key: "aries", nameTa: "மேஷம்", nameEn: "Aries", symbol: "♈", ruler: "செவ்வாய்" },
  { id: 2, key: "taurus", nameTa: "ரிஷபம்", nameEn: "Taurus", symbol: "♉", ruler: "சுக்கிரன்" },
  { id: 3, key: "gemini", nameTa: "மிதுனம்", nameEn: "Gemini", symbol: "♊", ruler: "புதன்" },
  { id: 4, key: "cancer", nameTa: "கடகம்", nameEn: "Cancer", symbol: "♋", ruler: "சந்திரன்" },
  { id: 5, key: "leo", nameTa: "சிம்மம்", nameEn: "Leo", symbol: "♌", ruler: "சூரியன்" },
  { id: 6, key: "virgo", nameTa: "கன்னி", nameEn: "Virgo", symbol: "♍", ruler: "புதன்" },
  { id: 7, key: "libra", nameTa: "துலாம்", nameEn: "Libra", symbol: "♎", ruler: "சுக்கிரன்" },
  { id: 8, key: "scorpio", nameTa: "விருச்சிகம்", nameEn: "Scorpio", symbol: "♏", ruler: "செவ்வாய்" },
  { id: 9, key: "sagittarius", nameTa: "தனுசு", nameEn: "Sagittarius", symbol: "♐", ruler: "குரு" },
  { id: 10, key: "capricorn", nameTa: "மகரம்", nameEn: "Capricorn", symbol: "♑", ruler: "சனி" },
  { id: 11, key: "aquarius", nameTa: "கும்பம்", nameEn: "Aquarius", symbol: "♒", ruler: "சனி" },
  { id: 12, key: "pisces", nameTa: "மீனம்", nameEn: "Pisces", symbol: "♓", ruler: "குரு" },
];

export function DailyRaasiSocialHub() {
  const { language } = useLanguage();
  const [targetDate, setTargetDate] = useState<string>(() => {
    // Current IST date in YYYY-MM-DD
    const now = new Date();
    const istOffset = 5.5 * 60 * 60 * 1000;
    const istDate = new Date(now.getTime() + (now.getTimezoneOffset() * 60000) + istOffset);
    return istDate.toISOString().slice(0, 10);
  });

  const [statusData, setStatusData] = useState<SocialStatusResponse | null>(null);
  const [loadingStatus, setLoadingStatus] = useState(false);
  const [sharingAll, setSharingAll] = useState(false);
  const [shareProgress, setShareProgress] = useState<string | null>(null);
  const [sharedRashis, setSharedRashis] = useState<Record<number, boolean>>({});
  const [sharingSingleId, setSharingSingleId] = useState<number | null>(null);
  const [dispatchingTelegram, setDispatchingTelegram] = useState(false);
  const [telegramNotice, setTelegramNotice] = useState<string | null>(null);
  const [copiedCaption, setCopiedCaption] = useState(false);
  const [previewModalImage, setPreviewModalImage] = useState<string | null>(null);
  const [readyModalData, setReadyModalData] = useState<{
    target: "status" | "channel";
    title: string;
    text: string;
    files: File[];
  } | null>(null);
  const [showDesktopNotice, setShowDesktopNotice] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      setIsMobile(/Android|iPhone|iPad|iPod/i.test(navigator.userAgent));
    }
  }, []);

  const getPosterUrl = (rashiId: number, rashiKey: string) => {
    return `/api/v1/social/facebook/posters/${targetDate}/rashi_${rashiId}_${rashiKey}.png`;
  };

  // Download all 12 posters to PC / device
  const handleDownloadAll12Posters = async () => {
    for (const rashi of RASHIS) {
      const url = getPosterUrl(rashi.id, rashi.key);
      const a = document.createElement("a");
      a.href = url;
      a.download = `rashi_${rashi.id}_${rashi.key}_${targetDate}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      await new Promise((r) => setTimeout(r, 250));
    }
  };

  const fetchStatus = async () => {
    setLoadingStatus(true);
    try {
      const res = await fetch("/api/v1/social/facebook/status", { cache: "no-store" });
      if (res.ok) {
        const data = await res.json();
        setStatusData(data);
      }
    } catch (e) {
      console.warn("Failed to fetch social media status:", e);
    } finally {
      setLoadingStatus(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  // Post All 12 Consecutive Slides at Once to WhatsApp Status or Channel
  const handleShareAllToWhatsApp = async (target: "status" | "channel" = "status") => {
    if (typeof window === "undefined") return;

    if (!navigator.share) {
      alert(
        language === "ta"
          ? "உங்கள் உலாவியில் Web Share ஆதரிக்கப்படவில்லை. மொபைல் Chrome (Android) அல்லது Safari (iPhone)-ல் திறக்கவும்."
          : "Web Share is not supported in this desktop browser. Please open this page on your Android (Chrome) or iPhone (Safari)."
      );
      return;
    }

    setSharingAll(true);
    setShareProgress(
      language === "ta"
        ? `12 படங்களையும் திரட்டுகிறது (${target === "channel" ? "Channel" : "Status"})...`
        : `Downloading 12 slides for ${target === "channel" ? "Channel" : "Status"}...`
    );

    try {
      const files: File[] = [];
      for (let i = 0; i < RASHIS.length; i++) {
        const rashi = RASHIS[i];
        setShareProgress(
          language === "ta"
            ? `படங்களை தயார் செய்கிறது (${i + 1}/12): ${rashi.nameTa}...`
            : `Preparing slide (${i + 1}/12): ${rashi.nameEn}...`
        );

        const imgUrl = getPosterUrl(rashi.id, rashi.key);
        let resp = await fetch(imgUrl);
        // If image is being rendered on demand, retry once after a short wait
        if (!resp.ok) {
          setShareProgress(
            language === "ta"
              ? `சேவையகத்தில் படம் உருவாகிறது (${i + 1}/12): ${rashi.nameTa}...`
              : `Rendering poster on server (${i + 1}/12): ${rashi.nameEn}...`
          );
          await new Promise((r) => setTimeout(r, 4000));
          resp = await fetch(imgUrl);
        }
        if (!resp.ok) {
          throw new Error(`Failed to fetch poster for ${rashi.nameEn} (HTTP ${resp.status})`);
        }
        const blob = await resp.blob();
        const file = new File(
          [blob],
          `rashi_${String(rashi.id).padStart(2, "0")}_${rashi.key}_${targetDate}.png`,
          { type: "image/png" }
        );
        files.push(file);
      }

      setShareProgress(
        target === "channel"
          ? language === "ta"
            ? "WhatsApp Channel-க்கு பகிரத் தயாராகிறது..."
            : "Opening WhatsApp Channel broadcast..."
          : language === "ta"
          ? "வாட்ஸ்அப் ஸ்டேட்டஸ் திறக்கிறது..."
          : "Opening WhatsApp Status composer..."
      );

      if (navigator.canShare && !navigator.canShare({ files })) {
        alert(
          language === "ta"
            ? "உங்கள் உலாவி பல படங்களை ஒரே நேரத்தில் பகிர அனுமதிக்கவில்லை. கீழே உள்ள ஒவ்வொரு ராசி பட்டனையும் தனித்தனியாகப் பகிரவும்."
            : "Multi-file sharing is not permitted by this browser. Please use the line-by-line Rashi buttons below."
        );
        return;
      }

      const captionText =
        target === "channel"
          ? `✨ இன்றைய தினசரி ராசிபலன் (${targetDate})\n` +
            `அனைத்து 12 ராசிகளுக்கான விரிவான சாதக நிலை, தொழில், தனம், குடும்ப பலன்கள், அதிர்ஷ்ட நேரம் மற்றும் பரிகாரங்களை மேலே உள்ள படங்களில் காண்க! 👆\n\n` +
            `🙏 Gokul's Astrological Insights | Thiruverkadu\n\n` +
            `📢 அதிகாரப்பூர்வ வாட்ஸ்அப் சேனல்:\n${WHATSAPP_CHANNEL_URL}`
          : `✨ இன்றைய தினசரி ராசிபலன் (${targetDate})\n` +
            `அனைத்து 12 ராசிகளின் முழுமையான பலன்கள்.\n` +
            `🙏 Gokul's Astrological Insights | Thiruverkadu\n\n` +
            `📢 எங்களின் WhatsApp Channel:\n${WHATSAPP_CHANNEL_URL}`;

      // Set the ready modal so navigator.share is invoked directly in a fresh user gesture tap!
      setReadyModalData({
        target,
        title: `தினசரி ராசிபலன் - ${targetDate}`,
        text: captionText,
        files: files,
      });
    } catch (err: any) {
      if (err?.name !== "AbortError") {
        console.error("Failed to prepare slides for WhatsApp:", err);
        alert(`Preparation failed: ${err.message || err}`);
      }
    } finally {
      setSharingAll(false);
      setShareProgress(null);
    }
  };

  // Line-by-line: Share a single Rashi to WhatsApp Status or Channel
  const handleShareSingleRashi = async (rashi: (typeof RASHIS)[0], target: "status" | "channel" = "status") => {
    if (typeof window === "undefined") return;

    if (!navigator.share) {
      alert(
        language === "ta"
          ? "உங்கள் உலாவியில் Web Share ஆதரிக்கப்படவில்லை. மொபைல் போனில் திறக்கவும்."
          : "Web Share is not supported in this browser. Please open on a mobile device."
      );
      return;
    }

    setSharingSingleId(rashi.id);
    try {
      const imgUrl = getPosterUrl(rashi.id, rashi.key);
      let resp = await fetch(imgUrl);
      if (!resp.ok) {
        await new Promise((r) => setTimeout(r, 4000));
        resp = await fetch(imgUrl);
      }
      if (!resp.ok) {
        throw new Error(`Failed to load poster (HTTP ${resp.status})`);
      }
      const blob = await resp.blob();
      const file = new File([blob], `rashi_${rashi.id}_${rashi.key}_${targetDate}.png`, { type: "image/png" });

      const captionText =
        target === "channel"
          ? `✨ இன்றைய தினசரி ராசிபலன்: ${rashi.nameTa} (${rashi.nameEn}) ${rashi.symbol}\n` +
            `📅 தேதி: ${targetDate}\n` +
            `🙏 Gokul's Astrological Insights | Thiruverkadu\n\n` +
            `📢 அதிகாரப்பூர்வ வாட்ஸ்அப் சேனல்:\n${WHATSAPP_CHANNEL_URL}`
          : `✨ இன்றைய தினசரி ராசிபலன்: ${rashi.nameTa} (${rashi.nameEn}) ${rashi.symbol}\n` +
            `📅 தேதி: ${targetDate}\n` +
            `🙏 Gokul's Astrological Insights | Thiruverkadu\n\n` +
            `📢 எங்களின் WhatsApp Channel:\n${WHATSAPP_CHANNEL_URL}`;

      // Open ready modal so share request is handled in a direct user gesture tap
      setReadyModalData({
        target,
        title: `${rashi.nameTa} ராசிபலன் - ${targetDate}`,
        text: captionText,
        files: [file],
      });
    } catch (err: any) {
      if (err?.name !== "AbortError") {
        alert(`Preparation failed: ${err.message || err}`);
      }
    } finally {
      setSharingSingleId(null);
    }
  };

  // Dispatch all 12 posters to Telegram
  const handleSendToTelegram = async () => {
    setDispatchingTelegram(true);
    setTelegramNotice(null);
    try {
      const res = await fetch(`/api/v1/social/facebook/telegram/send?date=${encodeURIComponent(targetDate)}`, {
        method: "POST",
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setTelegramNotice(
          language === "ta"
            ? "✅ 12 ராசி படங்களும் உங்கள் டெலிகிராமிற்கு 3 ஆல்பங்களாக அனுப்பப்பட்டுவிட்டன!"
            : "✅ All 12 Rashi posters have been delivered to your Telegram chat in 3 albums!"
        );
      } else {
        setTelegramNotice(
          `❌ ${data.detail || data.error || (language === "ta" ? "டெலிகிராமிற்கு அனுப்புவதில் தோல்வி" : "Failed to send to Telegram")}`
        );
      }
    } catch (err: any) {
      setTelegramNotice(`❌ Network error: ${err.message}`);
    } finally {
      setDispatchingTelegram(false);
    }
  };

  // Copy Tamil caption to clipboard
  const handleCopyCaption = () => {
    const fullText =
      `✨ இன்றைய தினசரி ராசிபலன் (${targetDate})\n\n` +
      `அனைத்து 12 ராசிகளுக்கான விரிவான சாதக நிலை, தொழில், தனம், குடும்ப பலன்கள், அதிர்ஷ்ட நேரம் மற்றும் பரிகாரங்களைக் காணுங்கள்!\n\n` +
      `🙏 Gokul's Astrological Insights\n` +
      `Gokul Murugan | Thiruverkadu\n\n` +
      `🌐 https://gai-astrology-frontend.onrender.com\n` +
      `#தினசரிராசிபலன் #DailyHoroscope #TamilAstrology #GokulsAstrologicalInsights`;

    navigator.clipboard.writeText(fullText);
    setCopiedCaption(true);
    setTimeout(() => setCopiedCaption(false), 2500);
  };

  const isTodayComplete =
    statusData?.scheduler?.last_run?.last_posted_date === targetDate &&
    statusData?.scheduler?.last_run?.status === "success";

  const nextRashi = RASHIS.find((r) => !sharedRashis[r.id]) || RASHIS[0];
  const completedCount = RASHIS.filter((r) => sharedRashis[r.id]).length;
  const isAllCompleted = completedCount === RASHIS.length;

  return (
    <div className="rounded-2xl border border-emerald-200 bg-white shadow-xs overflow-hidden">
      {/* Top Header Banner */}
      <div className="p-5 sm:p-6 bg-gradient-to-r from-emerald-900 via-[#0F382A] to-slate-900 text-white flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-emerald-500/20 border border-emerald-400/40 flex items-center justify-center text-emerald-400 shadow-inner">
              <Share2 className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-serif text-lg sm:text-xl font-bold text-white flex items-center gap-2">
                <span>
                  {language === "ta"
                    ? "தினசரி ராசிபலன் சோஷியல் ஹப்"
                    : "Daily Raasi Palan Social Hub"}
                </span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase bg-emerald-500 text-slate-950">
                  1-Click Status
                </span>
              </h2>
              <p className="text-xs text-emerald-200/80 mt-0.5">
                {language === "ta"
                  ? "WhatsApp Status, Facebook, Instagram & Telegram பப்ளிஷிங் மேலாண்மை"
                  : "Instant 12-Slide WhatsApp Status, Facebook, Instagram & Telegram broadcaster"}
              </p>
            </div>
          </div>
        </div>

        {/* Date Selector & Refresh */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/10 border border-white/15 text-xs text-emerald-100">
            <Calendar className="w-3.5 h-3.5 text-emerald-300" />
            <input
              type="date"
              value={targetDate}
              onChange={(e) => setTargetDate(e.target.value)}
              className="bg-transparent text-white font-mono text-xs focus:outline-hidden cursor-pointer"
            />
          </div>

          <button
            type="button"
            onClick={fetchStatus}
            disabled={loadingStatus}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 border border-white/15 text-xs font-medium text-white transition-colors cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loadingStatus ? "animate-spin" : ""}`} />
            <span>{language === "ta" ? "புதுப்பி" : "Refresh"}</span>
          </button>
        </div>
      </div>

      <div className="p-5 sm:p-6 space-y-6">
        {/* Multi-Channel Live Status Indicators */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {/* Facebook Status */}
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3.5 flex items-center justify-between">
            <div>
              <div className="text-[11px] font-bold uppercase text-slate-500">Facebook Page</div>
              <div className="text-xs font-semibold text-slate-800 mt-0.5 truncate max-w-[120px]">
                {statusData?.credentials?.page_name || "Gokul's Astro Forecast"}
              </div>
            </div>
            <span
              className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${
                statusData?.credentials?.valid
                  ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                  : "bg-amber-100 text-amber-800 border border-amber-300"
              }`}
            >
              {statusData?.credentials?.valid ? (
                <>
                  <CheckCircle2 className="w-3 h-3 text-emerald-600" /> Connected
                </>
              ) : (
                "Checking..."
              )}
            </span>
          </div>

          {/* Instagram Status */}
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3.5 flex items-center justify-between">
            <div>
              <div className="text-[11px] font-bold uppercase text-slate-500">Instagram</div>
              <div className="text-xs font-semibold text-slate-800 mt-0.5 truncate max-w-[120px]">
                @{statusData?.instagram?.username || "gokuls_astrological_insights_"}
              </div>
            </div>
            <span
              className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${
                statusData?.instagram?.valid
                  ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                  : "bg-amber-100 text-amber-800 border border-amber-300"
              }`}
            >
              {statusData?.instagram?.valid ? (
                <>
                  <CheckCircle2 className="w-3 h-3 text-emerald-600" /> Connected
                </>
              ) : (
                "Checking..."
              )}
            </span>
          </div>

          {/* WhatsApp Channel */}
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3.5 flex items-center justify-between">
            <div>
              <div className="text-[11px] font-bold uppercase text-slate-500">WhatsApp Channel</div>
              <a
                href={WHATSAPP_CHANNEL_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs font-semibold text-emerald-700 hover:text-emerald-800 hover:underline flex items-center gap-1 mt-0.5 truncate max-w-[120px]"
              >
                <span>GAI Channel</span>
                <ExternalLink className="w-3 h-3 shrink-0" />
              </a>
            </div>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
              <CheckCircle2 className="w-3 h-3 text-emerald-600" /> Active
            </span>
          </div>

          {/* Telegram Status */}
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3.5 flex items-center justify-between">
            <div>
              <div className="text-[11px] font-bold uppercase text-slate-500">Telegram Bot</div>
              <div className="text-xs font-semibold text-slate-800 mt-0.5 truncate max-w-[120px]">
                {statusData?.telegram?.valid
                  ? `@${statusData.telegram.bot_username}`
                  : statusData?.telegram?.configured
                  ? "Configured"
                  : "Not Configured"}
              </div>
            </div>
            <span
              className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${
                statusData?.telegram?.valid
                  ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                  : "bg-slate-200 text-slate-600 border border-slate-300"
              }`}
            >
              {statusData?.telegram?.valid ? "Active" : "Add Token"}
            </span>
          </div>

          {/* Today's Publish State */}
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3.5 flex items-center justify-between">
            <div>
              <div className="text-[11px] font-bold uppercase text-slate-500">Daily Auto-Post</div>
              <div className="text-xs font-semibold text-slate-800 mt-0.5 truncate max-w-[120px]">
                {isTodayComplete ? "Published" : statusData?.scheduler?.last_run?.status || "Idle"}
              </div>
            </div>
            <span
              className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${
                isTodayComplete
                  ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                  : "bg-blue-100 text-blue-800 border border-blue-300"
              }`}
            >
              {isTodayComplete ? "3/3 Carousels" : "Ready"}
            </span>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* RAPID-SEQUENCE STATUS HERO: 1-BY-1 FAST PLAYER (WHATSAPP NATIVE COMPLIANT) */}
        {/* ========================================================================= */}
        <div className="rounded-2xl p-6 bg-gradient-to-br from-emerald-700 via-green-600 to-teal-800 text-white shadow-lg relative overflow-hidden">
          <div className="absolute right-0 bottom-0 translate-x-8 translate-y-8 opacity-10 pointer-events-none">
            <MessageCircle className="w-64 h-64 text-white" />
          </div>

          <div className="relative z-10 space-y-5">
            {/* Header Strip */}
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex flex-wrap items-center gap-2">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase bg-white/20 text-white backdrop-blur-xs">
                  <Sparkles className="w-3.5 h-3.5 text-yellow-300" />
                  {language === "ta" ? "தொடர் வரிசை ஸ்டேட்டஸ் பிளேயர்" : "Rapid WhatsApp Status Player"}
                </span>
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-950/40 border border-white/20 text-emerald-200">
                  {completedCount}/12 {language === "ta" ? "பகிரப்பட்டது" : "Completed"}
                </span>
              </div>

              <div className="flex items-center gap-2">
                <a
                  href={WHATSAPP_CHANNEL_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold bg-emerald-950/40 border border-white/20 text-white hover:bg-emerald-950/60 transition-colors"
                >
                  <span>GAI Channel</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
                {completedCount > 0 && (
                  <button
                    type="button"
                    onClick={() => setSharedRashis({})}
                    className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-white/10 hover:bg-white/20 text-white transition-colors cursor-pointer"
                  >
                    Reset
                  </button>
                )}
              </div>
            </div>

            {/* Title & Guidance */}
            <div className="max-w-2xl">
              <h3 className="font-serif text-xl sm:text-2xl font-black text-white leading-tight">
                {isAllCompleted
                  ? language === "ta"
                    ? "🎉 வாழ்த்துகள்! 12 ராசிகளும் வாட்ஸ்அப்பில் வெற்றிகரமாக பகிரப்பட்டுவிட்டன!"
                    : "🎉 All 12 Rashis Successfully Posted to WhatsApp!"
                  : language === "ta"
                  ? `அடுத்த ராசி: ${nextRashi.symbol} ${nextRashi.nameTa} (${nextRashi.id}/12) – உடனே Status-ல் பகிர்க!`
                  : `Next Slide: ${nextRashi.symbol} ${nextRashi.nameEn} (${nextRashi.id}/12) – Post to Status!`}
              </h3>
              <p className="mt-1 text-xs sm:text-sm text-emerald-100/90 leading-relaxed">
                {language === "ta"
                  ? "கீழே உள்ள பெரிய பட்டனைத் தட்டினால், அடுத்த ராசியின் படம் நேரடியாக வாட்ஸ்அப் ஸ்டேட்டஸில் தயாராகும். 'My Status' & Send கொடுத்ததும் தானாக அடுத்த ராசிக்கு மாறிவிடும்!"
                  : "Tap the big button below to launch the next Rashi directly into WhatsApp Status. It auto-advances to the next slide every time you post!"}
              </p>
            </div>

            {/* Progress Bar */}
            <div className="space-y-1.5">
              <div className="w-full bg-emerald-950/50 rounded-full h-2.5 overflow-hidden border border-white/10">
                <div
                  className="bg-gradient-to-r from-yellow-400 to-emerald-300 h-full transition-all duration-300 rounded-full"
                  style={{ width: `${(completedCount / 12) * 100}%` }}
                />
              </div>
              <div className="flex justify-between text-[11px] font-mono text-emerald-200/80">
                <span>♈ மேஷம் (1)</span>
                <span>{completedCount} of 12 shared</span>
                <span>♓ மீனம் (12)</span>
              </div>
            </div>

            {/* Action Buttons Row */}
            <div className="flex flex-wrap items-center gap-3 pt-1">
              {!isAllCompleted ? (
                <>
                  {/* Next Rashi to Status */}
                  <button
                    type="button"
                    onClick={() => handleShareSingleRashi(nextRashi, "status")}
                    disabled={sharingSingleId === nextRashi.id}
                    className="inline-flex items-center justify-center gap-2 px-6 py-4 rounded-xl bg-white hover:bg-emerald-50 text-slate-950 font-black text-sm sm:text-base shadow-lg transition-transform active:scale-98 cursor-pointer"
                  >
                    {sharingSingleId === nextRashi.id ? (
                      <RefreshCw className="w-5 h-5 animate-spin text-emerald-600" />
                    ) : (
                      <MessageCircle className="w-5 h-5 text-emerald-600 fill-emerald-600" />
                    )}
                    <span>
                      {language === "ta"
                        ? `📲 அடுத்தது: ${nextRashi.nameTa} (${nextRashi.id}/12) Status-ல் பகிர்க ➔`
                        : `📲 Post Next: ${nextRashi.nameEn} (${nextRashi.id}/12) to Status ➔`}
                    </span>
                  </button>

                  {/* Next Rashi to Channel */}
                  <button
                    type="button"
                    onClick={() => handleShareSingleRashi(nextRashi, "channel")}
                    disabled={sharingSingleId === nextRashi.id}
                    className="inline-flex items-center justify-center gap-2 px-4 py-4 rounded-xl bg-slate-900 hover:bg-black text-white font-bold text-xs sm:text-sm border border-emerald-400/40 shadow-md transition-transform active:scale-98 cursor-pointer"
                  >
                    <Share2 className="w-4 h-4 text-emerald-300" />
                    <span>
                      {language === "ta"
                        ? `${nextRashi.nameTa} Channel-ல் பகிர்க`
                        : `Post ${nextRashi.nameEn} to Channel`}
                    </span>
                  </button>
                </>
              ) : (
                <button
                  type="button"
                  onClick={() => setSharedRashis({})}
                  className="inline-flex items-center justify-center gap-2 px-6 py-4 rounded-xl bg-white text-slate-950 font-black text-sm shadow-lg cursor-pointer"
                >
                  <RefreshCw className="w-4 h-4 text-emerald-600" />
                  <span>{language === "ta" ? "மீண்டும் முதன்முறையாகத் தொடங்குக (Reset)" : "Reset & Share Again"}</span>
                </button>
              )}

              {/* Telegram Action */}
              <button
                type="button"
                onClick={handleSendToTelegram}
                disabled={dispatchingTelegram}
                className="inline-flex items-center justify-center gap-2 px-4 py-4 rounded-xl bg-emerald-950/40 hover:bg-emerald-950/60 border border-white/20 text-white font-bold text-xs transition-colors cursor-pointer disabled:opacity-50"
                title="Send all 12 posters as 3 photo albums directly to your Telegram chat"
              >
                <Send className={`w-3.5 h-3.5 text-emerald-300 ${dispatchingTelegram ? "animate-spin" : ""}`} />
                <span>{dispatchingTelegram ? "Sending..." : "Telegram"}</span>
              </button>
            </div>
          </div>

          {telegramNotice && (
            <div className="mt-4 p-3 rounded-xl bg-black/25 border border-white/20 text-xs font-medium text-white flex items-center justify-between">
              <span>{telegramNotice}</span>
              <button
                onClick={() => setTelegramNotice(null)}
                className="text-white/70 hover:text-white ml-2 text-sm font-bold"
              >
                ✕
              </button>
            </div>
          )}
        </div>

        {/* Quick Utilities Strip */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-2 pb-1 border-b border-slate-200 text-xs">
          <div className="text-slate-600 font-medium">
            {language === "ta"
              ? "அல்லது கீழே உள்ள ராசிகளை தனித்தனியாக (Line-by-Line) பகிரலாம்:"
              : "Or share individually line-by-line using the cards below:"}
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleDownloadAll12Posters}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 font-semibold transition-colors cursor-pointer"
              title="Download all 12 poster PNGs to your computer"
            >
              <Download className="w-3.5 h-3.5 text-slate-500" />
              <span>{language === "ta" ? "12 படங்களையும் பதிவிறக்கு (PC)" : "Download All 12 (PC)"}</span>
            </button>

            <button
              type="button"
              onClick={handleCopyCaption}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 font-semibold transition-colors cursor-pointer"
            >
              {copiedCaption ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-600" />
                  <span className="text-emerald-700">{language === "ta" ? "நகலெடுக்கப்பட்டது!" : "Copied!"}</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5 text-slate-500" />
                  <span>{language === "ta" ? "முழு தமிழ் கேப்ஷன் காப்பி" : "Copy Tamil Caption"}</span>
                </>
              )}
            </button>

            <a
              href="https://web.whatsapp.com"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 font-semibold transition-colors"
            >
              <ExternalLink className="w-3.5 h-3.5 text-slate-500" />
              <span>WhatsApp Web</span>
            </a>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* LINE-BY-LINE RASHI GRID (12 RASHIS)                                       */}
        {/* ========================================================================= */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {RASHIS.map((rashi) => {
            const isShared = sharedRashis[rashi.id];
            const isSharingThis = sharingSingleId === rashi.id;
            const posterUrl = getPosterUrl(rashi.id, rashi.key);

            return (
              <div
                key={rashi.id}
                className={`rounded-2xl border transition-all p-4 flex flex-col justify-between ${
                  isShared
                    ? "border-emerald-300 bg-emerald-50/40 shadow-xs"
                    : "border-slate-200 bg-white hover:border-slate-300 hover:shadow-sm"
                }`}
              >
                <div>
                  {/* Card Header */}
                  <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                    <div className="flex items-center gap-2">
                      <span className="text-2xl text-amber-500">{rashi.symbol}</span>
                      <div>
                        <div className="font-serif font-bold text-slate-900 text-sm">
                          {rashi.nameTa}
                        </div>
                        <div className="text-[11px] text-slate-500 font-medium">
                          {rashi.nameEn} • {rashi.ruler}
                        </div>
                      </div>
                    </div>
                    {isShared && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" /> Shared
                      </span>
                    )}
                  </div>

                  {/* Thumbnail Preview Area */}
                  <div className="my-3 relative rounded-xl overflow-hidden border border-slate-200 bg-slate-900 aspect-square group">
                    <img
                      src={posterUrl}
                      alt={`${rashi.nameTa} Daily Poster`}
                      className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                      loading="lazy"
                      onError={(e) => {
                        // Fallback placeholder if image not rendered
                        (e.target as HTMLElement).style.display = "none";
                      }}
                    />
                    <div className="absolute inset-0 bg-slate-900/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                      <button
                        type="button"
                        onClick={() => setPreviewModalImage(posterUrl)}
                        className="p-2 rounded-full bg-white text-slate-900 hover:bg-slate-100 transition-colors cursor-pointer"
                        title="View Full 1080x1080 Poster"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <a
                        href={posterUrl}
                        download={`rashi_${rashi.id}_${rashi.key}_${targetDate}.png`}
                        className="p-2 rounded-full bg-white text-slate-900 hover:bg-slate-100 transition-colors"
                        title="Download Poster"
                      >
                        <Download className="w-4 h-4" />
                      </a>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="space-y-2 pt-2 border-t border-slate-100">
                  <div className="grid grid-cols-2 gap-1.5">
                    {/* Share to Status */}
                    <button
                      type="button"
                      onClick={() => handleShareSingleRashi(rashi, "status")}
                      disabled={isSharingThis}
                      className={`inline-flex items-center justify-center gap-1 px-2.5 py-2 rounded-xl font-bold text-[11px] transition-colors cursor-pointer disabled:opacity-50 ${
                        isShared
                          ? "bg-emerald-600 hover:bg-emerald-700 text-white"
                          : "bg-[#25D366] hover:bg-[#1EBE5D] text-slate-950"
                      }`}
                      title="Post this Rashi to WhatsApp Status"
                    >
                      {isSharingThis ? (
                        <RefreshCw className="w-3 h-3 animate-spin" />
                      ) : (
                        <MessageCircle className="w-3 h-3 fill-current" />
                      )}
                      <span>Status</span>
                    </button>

                    {/* Share to Channel */}
                    <button
                      type="button"
                      onClick={() => handleShareSingleRashi(rashi, "channel")}
                      disabled={isSharingThis}
                      className="inline-flex items-center justify-center gap-1 px-2.5 py-2 rounded-xl font-bold text-[11px] bg-slate-900 hover:bg-black text-white transition-colors cursor-pointer disabled:opacity-50"
                      title="Share this Rashi to WhatsApp Channel"
                    >
                      <Share2 className="w-3 h-3 text-emerald-400" />
                      <span>Channel</span>
                    </button>
                  </div>

                  <a
                    href={posterUrl}
                    download={`rashi_${rashi.id}_${rashi.key}_${targetDate}.png`}
                    className="w-full inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 font-semibold text-[11px] text-slate-700 transition-colors"
                  >
                    <Download className="w-3 h-3 text-slate-500" />
                    <span>{language === "ta" ? "பதிவிறக்கு" : "Download PNG"}</span>
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Ready to Share Modal (Guarantees user gesture activation for navigator.share) */}
      {readyModalData && (
        <div
          className="fixed inset-0 z-50 bg-black/75 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in"
          onClick={() => setReadyModalData(null)}
        >
          <div
            className="bg-white rounded-3xl p-6 sm:p-8 max-w-sm w-full text-center shadow-2xl border border-emerald-100"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="w-16 h-16 rounded-2xl bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto mb-4 shadow-inner">
              <MessageCircle className="w-8 h-8 fill-emerald-600" />
            </div>

            <h3 className="font-serif text-xl sm:text-2xl font-black text-slate-900">
              {readyModalData.files.length > 1
                ? language === "ta"
                  ? "12 படங்களும் தயாராக உள்ளன!"
                  : "All 12 Slides Ready!"
                : language === "ta"
                ? "படம் தயாராக உள்ளது!"
                : "Poster Ready!"}
            </h3>

            <p className="mt-2 text-xs sm:text-sm text-slate-600 leading-relaxed">
              {readyModalData.target === "channel"
                ? language === "ta"
                  ? "வாட்ஸ்அப் திறக்க கீழே உள்ள பட்டனைத் தொடவும். 'Channels' பிரிவில் 'Gokul's Astrological Insights' சேனலைத் தேர்வு செய்யவும்."
                  : "Tap below to launch WhatsApp. Select 'Channels' and choose 'Gokul's Astrological Insights'."
                : language === "ta"
                ? "வாட்ஸ்அப் திறக்க கீழே உள்ள பட்டனைத் தொடவும். 'My Status' என்பதைத் தேர்ந்தெடுத்து அனுப்பவும்."
                : "Tap below to launch WhatsApp. Select 'My Status' and tap Send."}
            </p>

            <div className="mt-6 space-y-3">
              <button
                type="button"
                onClick={async () => {
                  const data = readyModalData;
                  if (!data) return;

                  // Pre-flight check payload combinations with navigator.canShare
                  let payload: ShareData = {
                    title: data.title,
                    text: data.text,
                    files: data.files,
                  };

                  if (navigator.canShare && !navigator.canShare(payload)) {
                    // Some desktop/mobile OS targets reject combining files with text; fallback to files only
                    payload = { files: data.files };
                  }

                  if (navigator.canShare && !navigator.canShare(payload)) {
                    // If batch multi-file sharing is not permitted, fallback to single file
                    if (data.files.length > 0) {
                      payload = { files: [data.files[0]] };
                    }
                  }

                  try {
                    await navigator.share(payload);
                    setReadyModalData(null);
                    // Mark all or single as shared
                    if (data.files.length > 1) {
                      const allShared: Record<number, boolean> = {};
                      RASHIS.forEach((r) => {
                        allShared[r.id] = true;
                      });
                      setSharedRashis(allShared);
                    }
                  } catch (shareErr: any) {
                    setReadyModalData(null);
                    if (shareErr?.name !== "AbortError") {
                      setShowDesktopNotice(true);
                    }
                  }
                }}
                className="w-full py-4 rounded-xl bg-[#25D366] hover:bg-[#1EBE5D] text-slate-950 font-black text-sm sm:text-base shadow-lg transition-transform active:scale-98 cursor-pointer flex items-center justify-center gap-2"
              >
                <MessageCircle className="w-5 h-5 fill-current" />
                <span>
                  {readyModalData.target === "channel"
                    ? language === "ta"
                      ? "WhatsApp Channel-ல் பகிர்க 🚀"
                      : "Open WhatsApp Channel 🚀"
                    : language === "ta"
                    ? "WhatsApp Status-ல் பகிர்க 🚀"
                    : "Open WhatsApp Status 🚀"}
                </span>
              </button>

              <button
                type="button"
                onClick={() => setReadyModalData(null)}
                className="w-full py-2.5 rounded-xl text-xs font-semibold text-slate-500 hover:text-slate-800 cursor-pointer"
              >
                {language === "ta" ? "ரத்து செய்" : "Cancel"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Desktop Limitation Notice Modal */}
      {showDesktopNotice && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in"
          onClick={() => setShowDesktopNotice(false)}
        >
          <div
            className="bg-white rounded-3xl p-6 sm:p-8 max-w-md w-full text-center shadow-2xl border border-slate-200"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="w-16 h-16 rounded-2xl bg-amber-100 text-amber-600 flex items-center justify-center mx-auto mb-4 shadow-inner text-2xl font-black">
              📱
            </div>

            <h3 className="font-serif text-xl sm:text-2xl font-black text-slate-900">
              {language === "ta" ? "மொபைல் போனில் திறக்கவும்" : "Open on Your Mobile Phone"}
            </h3>

            <p className="mt-2 text-xs sm:text-sm text-slate-600 leading-relaxed text-left bg-slate-50 p-4 rounded-xl border border-slate-200">
              {language === "ta" ? (
                <>
                  💡 <b>வாட்ஸ்அப் ஸ்டேட்டஸ் மொபைல் போன்களுக்கானது:</b>
                  <br />
                  Windows கணினி உலாவிகள் வாட்ஸ்அப் ஸ்டேட்டஸில் நேரடியாகப் பகிர அனுமதிக்காது (Permission Denied).
                  <br /><br />
                  உங்கள் <b>Android போன் (Chrome)</b> அல்லது <b>iPhone (Safari)</b>-ல் <b>astro.gaionline.in/admin</b> தளத்தைத் திறந்து இதே பட்டனைத் தட்டினால், வாட்ஸ்அப் நேரடியாகத் திறந்து 12 ஸ்லைடுகளையும் உடனே பப்ளிஷ் செய்துவிடும்!
                </>
              ) : (
                <>
                  💡 <b>WhatsApp Status is Mobile-Only:</b>
                  <br />
                  Windows desktop browsers block direct file sharing to WhatsApp Status (Permission Denied).
                  <br /><br />
                  Please open <b>astro.gaionline.in/admin</b> on your <b>Android phone (Chrome)</b> or <b>iPhone (Safari)</b>. Tapping this button on mobile directly launches WhatsApp with all 12 slides queued!
                </>
              )}
            </p>

            <div className="mt-5 space-y-2.5">
              <button
                type="button"
                onClick={() => {
                  setShowDesktopNotice(false);
                  handleDownloadAll12Posters();
                }}
                className="w-full py-3 rounded-xl bg-slate-900 hover:bg-black text-white font-bold text-xs sm:text-sm flex items-center justify-center gap-2 cursor-pointer transition-colors"
              >
                <Download className="w-4 h-4 text-emerald-400" />
                <span>
                  {language === "ta"
                    ? "கணினியில் 12 படங்களையும் பதிவிறக்குக (Download 12 PNGs)"
                    : "Download All 12 Posters to PC"}
                </span>
              </button>

              <button
                type="button"
                onClick={() => {
                  setShowDesktopNotice(false);
                  handleSendToTelegram();
                }}
                className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs sm:text-sm flex items-center justify-center gap-2 cursor-pointer transition-colors"
              >
                <Send className="w-4 h-4 text-white" />
                <span>
                  {language === "ta"
                    ? "என் Telegram Bot-க்கு அனுப்புக (Send to Telegram)"
                    : "Send to My Telegram Bot"}
                </span>
              </button>

              <button
                type="button"
                onClick={() => setShowDesktopNotice(false)}
                className="w-full py-2 rounded-xl text-xs font-semibold text-slate-500 hover:text-slate-800 cursor-pointer"
              >
                {language === "ta" ? "மூடுக" : "Close"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Full Resolution Poster Modal */}
      {previewModalImage && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-xs flex items-center justify-center p-4"
          onClick={() => setPreviewModalImage(null)}
        >
          <div
            className="relative max-w-lg w-full bg-slate-950 rounded-2xl overflow-hidden border border-slate-800 p-2 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <img
              src={previewModalImage}
              alt="Full Resolution Poster"
              className="w-full h-auto rounded-xl object-contain max-h-[80vh]"
            />
            <div className="p-3 flex items-center justify-between">
              <a
                href={previewModalImage}
                download
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Download High-Res 1080x1080</span>
              </a>
              <button
                type="button"
                onClick={() => setPreviewModalImage(null)}
                className="px-4 py-2 rounded-xl border border-slate-700 text-slate-300 hover:text-white font-semibold text-xs"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
