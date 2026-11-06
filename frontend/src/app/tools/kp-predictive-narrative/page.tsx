"use client";

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { FeatureGuard } from "@/components/auth/FeatureGuard";
import {
  KpNarrativeRequest,
  KpNarrativeResponse,
  SavedKpNarrativeItem,
  SavedHoroscopeItem,
} from "@/lib/types";
import {
  generateKpNarrative,
  downloadKpNarrativePdf,
  saveKpNarrative,
  listSavedKpNarratives,
  getSavedKpNarrative,
  deleteSavedKpNarrative,
} from "@/lib/api";
import {
  Compass,
  Calendar,
  Clock,
  Sparkles,
  Download,
  Printer,
  Copy,
  Check,
  RefreshCw,
  Bookmark,
  FileText,
  User,
  Heart,
  Briefcase,
  Coins,
  ShieldAlert,
  ShieldCheck,
  ChevronRight,
  Trash2,
  ExternalLink,
  Info,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Share2,
  Save,
  Sliders,
  Layers,
  ArrowRight,
} from "lucide-react";

function getTodayIsoDate(): string {
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, "0");
  const d = String(now.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function KpPredictiveNarrativeContent() {
  const searchParams = useSearchParams();
  const savedIdParam = searchParams.get("id") || "";

  const { language: uiLang } = useLanguage();
  const { session, isAuthenticated } = useAuth();

  // Mode: "saved" | "manual" | "saved_reports"
  const [inputMode, setInputMode] = useState<"saved" | "manual" | "saved_reports">(
    savedIdParam ? "saved" : "saved"
  );

  // Saved Horoscopes
  const [savedHoroscopes, setSavedHoroscopes] = useState<SavedHoroscopeItem[]>([]);
  const [selectedHoroscopeId, setSelectedHoroscopeId] = useState<string>(savedIdParam);
  const [loadingHoroscopes, setLoadingHoroscopes] = useState<boolean>(false);

  // Manual Birth Input State
  const [manualName, setManualName] = useState<string>("Client Chart");
  const [manualDate, setManualDate] = useState<string>("1992-05-15");
  const [manualTime, setManualTime] = useState<string>("14:30:00");
  const [manualPlace, setManualPlace] = useState<string>("Chennai, India");
  const [manualLat, setManualLat] = useState<string>("13.0827");
  const [manualLon, setManualLon] = useState<string>("80.2707");
  const [manualTz, setManualTz] = useState<string>("Asia/Kolkata");
  const [manualGender, setManualGender] = useState<string>("male");

  // Options
  const [targetDate, setTargetDate] = useState<string>(getTodayIsoDate());
  const [reportLang, setReportLang] = useState<"ta" | "en" | "bilingual">(
    uiLang === "ta" ? "ta" : "en"
  );
  const [monthsAhead, setMonthsAhead] = useState<number>(24);

  // Results State
  const [reportData, setReportData] = useState<KpNarrativeResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Saved Reports List
  const [savedReports, setSavedReports] = useState<SavedKpNarrativeItem[]>([]);
  const [loadingSavedReports, setLoadingSavedReports] = useState<boolean>(false);
  const [saveTitle, setSaveTitle] = useState<string>("");
  const [saving, setSaving] = useState<boolean>(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);

  // Active View Tab: "all" | "promise" | "dasha" | "milestones" | "remedies"
  const [activeTab, setActiveTab] = useState<"all" | "promise" | "dasha" | "milestones" | "remedies">("all");

  // Feedback states
  const [copied, setCopied] = useState<boolean>(false);
  const [downloadingPdf, setDownloadingPdf] = useState<boolean>(false);

  // Load saved horoscopes list on mount
  useEffect(() => {
    async function loadSavedList() {
      if (!isAuthenticated || !session?.access_token) return;
      setLoadingHoroscopes(true);
      try {
        const res = await fetch("/api/horoscopes?page=1&limit=1000", {
          cache: "no-store",
          headers: {
            Authorization: `Bearer ${session.access_token}`,
          },
        });
        if (res.ok) {
          const data = await res.json();
          const items: SavedHoroscopeItem[] = data.horoscopes || [];
          setSavedHoroscopes(items);
          if (!selectedHoroscopeId && items.length > 0) {
            setSelectedHoroscopeId(items[0].id);
          }
        }
      } catch (err) {
        console.warn("Could not load saved horoscopes:", err);
      } finally {
        setLoadingHoroscopes(false);
      }
    }
    loadSavedList();
  }, [isAuthenticated, session?.access_token, selectedHoroscopeId]);

  // Load saved narrative reports list
  const loadSavedReports = async () => {
    setLoadingSavedReports(true);
    try {
      const token = session?.access_token;
      const res = await listSavedKpNarratives(token);
      setSavedReports(res.items || []);
    } catch (err) {
      console.warn("Error loading saved narrative reports:", err);
    } finally {
      setLoadingSavedReports(false);
    }
  };

  useEffect(() => {
    if (inputMode === "saved_reports") {
      loadSavedReports();
    }
  }, [inputMode]);

  // Generate Report Handler
  const handleGenerate = async () => {
    setLoading(true);
    setErrorMsg(null);
    setSaveSuccessMsg(null);
    try {
      const token = session?.access_token;
      let req: KpNarrativeRequest;

      if (inputMode === "saved") {
        if (!selectedHoroscopeId) {
          throw new Error(
            uiLang === "ta"
              ? "தயவுசெய்து ஒரு ஜாதகத்தைத் தேர்ந்தெடுக்கவும்."
              : "Please select a saved horoscope."
          );
        }
        req = {
          saved_horoscope_id: selectedHoroscopeId,
          target_date: targetDate,
          language: reportLang,
          months_ahead: monthsAhead,
        };
      } else {
        const lat = parseFloat(manualLat);
        const lon = parseFloat(manualLon);
        if (isNaN(lat) || isNaN(lon)) {
          throw new Error("Invalid latitude/longitude coordinates.");
        }
        req = {
          birth_input: {
            birth_date: manualDate,
            birth_time: manualTime,
            latitude: lat,
            longitude: lon,
            timezone: manualTz,
          },
          person_name: manualName || "Native",
          gender: manualGender,
          target_date: targetDate,
          language: reportLang,
          months_ahead: monthsAhead,
        };
      }

      const res = await generateKpNarrative(req, token);
      setReportData(res);
      setSaveTitle(
        `${res.person_details.name} - KP Predictive Narrative (${res.target_date})`
      );
    } catch (err: any) {
      console.error("Narrative generation error:", err);
      setErrorMsg(err.message || "Failed to generate KP predictive narrative.");
    } finally {
      setLoading(false);
    }
  };

  // Download PDF Handler
  const handleDownloadPdf = async (pdfLang: "ta" | "en" | "bilingual") => {
    if (!reportData) return;
    setDownloadingPdf(true);
    try {
      const token = session?.access_token;
      const blob = await downloadKpNarrativePdf(
        {
          language: pdfLang,
          months_ahead: monthsAhead,
          precalculated_data: reportData,
        },
        token
      );
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const safeName = reportData.person_details.name.replace(/\s+/g, "_");
      a.download = `KP_Predictive_Narrative_${safeName}_${pdfLang.toUpperCase()}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      alert(`PDF download failed: ${err.message}`);
    } finally {
      setDownloadingPdf(false);
    }
  };

  // Copy Narrative Markdown
  const handleCopyNarrative = () => {
    if (!reportData) return;
    const isTa = reportLang === "ta";
    const p = reportData.person_details;
    const np = reportData.natal_promise;
    const rd = reportData.running_dasha;

    let md = `# ${isTa ? "கே.பி. கணிப்பு உரை அறிக்கை" : "KP Predictive Narrative Report"}\n`;
    md += `**${isTa ? "ஜாதகர்" : "Native"}:** ${p.name} | **${isTa ? "பிறந்த தேதி" : "DOB"}:** ${p.birth_date} ${p.birth_time}\n`;
    md += `**${isTa ? "லக்னம்" : "Lagna"}:** ${isTa ? p.lagna_ta : p.lagna} | **${isTa ? "ராசி" : "Moon Sign"}:** ${isTa ? p.moon_sign_ta : p.moon_sign} | **${isTa ? "நட்சத்திரம்" : "Star"}:** ${isTa ? p.nakshatra_ta : p.nakshatra}\n\n`;

    md += `## 1. ${isTa ? "ஜாதக வாக்குறுதி" : "Natal Event Promise"}\n`;
    md += `> ${isTa ? np.overall_synthesis_ta : np.overall_synthesis_en}\n\n`;
    np.items.forEach((it) => {
      md += `### Cusp ${it.cusp}: ${isTa ? it.domain_ta : it.domain_en}\n`;
      md += `**${isTa ? "தீர்ப்பு" : "Verdict"}:** ${isTa ? it.verdict_label_ta : it.verdict_label_en} (CSL: ${it.cusp_sub_lord} | Star: ${it.star_lord})\n`;
      md += `${isTa ? it.plain_narrative_ta : it.plain_narrative_en}\n`;
      md += `*${isTa ? "நடைமுறை வழிகாட்டல்" : "Actionable Takeaway"}:* ${isTa ? it.practical_takeaway_ta : it.practical_takeaway_en}\n\n`;
    });

    md += `## 2. ${isTa ? "தற்போதைய தசா-புத்தி பலன்கள்" : "Running Dasha-Bhukti Analysis"}\n`;
    md += `**${isTa ? rd.phase_title_ta : rd.phase_title_en}** (${isTa ? "சாதகக் குறியீடு" : "Favorability"}: ${rd.favorable_score}%)\n`;
    md += `> ${isTa ? rd.phase_theme_ta : rd.phase_theme_en}\n\n`;
    md += `- **${isTa ? "தொழில்" : "Career"}:** ${isTa ? rd.career_impact_ta : rd.career_impact_en}\n`;
    md += `- **${isTa ? "நிதி" : "Finances"}:** ${isTa ? rd.finance_impact_ta : rd.finance_impact_en}\n`;
    md += `- **${isTa ? "குடும்பம்" : "Relationships"}:** ${isTa ? rd.relationship_impact_ta : rd.relationship_impact_en}\n`;
    md += `- **${isTa ? "ஆரோக்கியம்" : "Health"}:** ${isTa ? rd.health_impact_ta : rd.health_impact_en}\n\n`;

    md += `## 3. ${isTa ? "அடுத்த 12-24 மாத முக்கிய காலக்கட்டங்கள்" : "Upcoming Milestone Windows"}\n`;
    reportData.milestone_windows.forEach((m) => {
      md += `### ${isTa ? m.window_title_ta : m.window_title_en} — ${isTa ? m.domain_label_ta : m.domain_label_en}\n`;
      md += `**${isTa ? m.headline_ta : m.headline_en}** (${isTa ? m.status_ta : m.status})\n`;
      md += `${isTa ? m.plain_narrative_ta : m.plain_narrative_en}\n\n`;
    });

    md += `## 4. ${isTa ? "செய்ய வேண்டியவை & பரிகாரங்கள்" : "Do's, Don'ts & Remedial Advice"}\n`;
    const dos = isTa ? reportData.remedies.dos_ta : reportData.remedies.dos_en;
    const donts = isTa ? reportData.remedies.donts_ta : reportData.remedies.donts_en;
    md += `### ${isTa ? "செய்ய வேண்டியவை" : "Do's"}:\n` + dos.map((d) => `- ${d}`).join("\n") + "\n\n";
    md += `### ${isTa ? "தவிர்க்க வேண்டியவை" : "Don'ts"}:\n` + donts.map((d) => `- ${d}`).join("\n") + "\n\n";
    md += `**${isTa ? "இறை வழிபாடு" : "Deity"}:** ${isTa ? reportData.remedies.deity_prayer_ta : reportData.remedies.deity_prayer_en}\n`;
    md += `**${isTa ? "தானம்" : "Charity"}:** ${isTa ? reportData.remedies.charity_action_ta : reportData.remedies.charity_action_en}\n`;

    navigator.clipboard.writeText(md);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  // Save Report Handler
  const handleSaveReport = async () => {
    if (!reportData) return;
    setSaving(true);
    setSaveSuccessMsg(null);
    try {
      const token = session?.access_token;
      const p = reportData.person_details;
      await saveKpNarrative(
        {
          title: saveTitle || `${p.name} KP Narrative`,
          person_name: p.name,
          saved_horoscope_id: selectedHoroscopeId || undefined,
          birth_date: p.birth_date,
          birth_time: p.birth_time,
          latitude: p.latitude,
          longitude: p.longitude,
          timezone: p.timezone,
          gender: p.gender,
          language: reportLang,
          report_data: reportData,
        },
        token
      );
      setSaveSuccessMsg(
        uiLang === "ta"
          ? "அறிக்கை வெற்றிகரமாக சேமிக்கப்பட்டது!"
          : "Report successfully saved to your library!"
      );
    } catch (err: any) {
      alert(`Save failed: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  // Load a Saved Report from Library
  const handleLoadSavedReport = async (recordId: string) => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const token = session?.access_token;
      const rec = await getSavedKpNarrative(recordId, token);
      if (rec && rec.report_data) {
        setReportData(rec.report_data as KpNarrativeResponse);
        setSaveTitle(rec.title || "KP Narrative Report");
        setInputMode("saved");
      }
    } catch (err: any) {
      alert(`Could not load report: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Delete a Saved Report
  const handleDeleteSavedReport = async (recordId: string) => {
    if (!confirm(uiLang === "ta" ? "இந்த அறிக்கையை நீக்க விரும்புகிறீர்களா?" : "Delete this saved report?")) return;
    try {
      const token = session?.access_token;
      await deleteSavedKpNarrative(recordId, token);
      setSavedReports((prev) => prev.filter((r) => r.id !== recordId));
    } catch (err: any) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  const isTa = reportLang === "ta";

  return (
    <FeatureGuard permission="kp_astrology">
      <div className="min-h-screen bg-[#F8FAFC] pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
          <Breadcrumbs
            items={[
              { label: uiLang === "ta" ? "முகப்பு" : "Home", href: "/home" },
              { label: uiLang === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools", href: "/tools" },
              {
                label: uiLang === "ta" ? "கே.பி. கணிப்பு உரை அறிக்கை" : "KP Predictive Narrative Engine",
                href: "/tools/kp-predictive-narrative",
              },
            ]}
          />

          {/* Page Hero Header */}
          <div className="mt-4 bg-gradient-to-r from-[#0A192F] via-[#153F6B] to-[#0A192F] rounded-2xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden border border-[#B4872B]/30">
            <div className="absolute top-0 right-0 w-96 h-96 bg-[#B4872B]/10 rounded-full blur-3xl pointer-events-none" />
            <div className="relative z-10">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#B4872B]/20 border border-[#B4872B]/40 text-[#FAF2DE] text-xs font-semibold uppercase tracking-wider mb-3">
                <Sparkles className="w-3.5 h-3.5 text-[#B4872B]" />
                Feature 2 • Automated Plain-Language Stellar Narrative
              </div>
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold tracking-tight">
                {uiLang === "ta"
                  ? "கே.பி. கணிப்பு உரை அறிக்கை (English & Tamil)"
                  : "Automated KP Predictive Narrative Engine"}
              </h1>
              <p className="mt-2 text-sm sm:text-base text-slate-300 max-w-3xl leading-relaxed">
                {uiLang === "ta"
                  ? "ஜோதிட கலைச்சொற்கள் எதுவும் இன்றி எவரும் எளிதில் புரிந்து கொள்ளக்கூடிய வகையில் ஜாதக வாக்குறுதி, தற்போதைய தசா-புத்தி பலன்கள், அடுத்த 12–24 மாதங்களின் முக்கிய காலக்கட்டங்கள் மற்றும் பரிகாரங்களை சுயமாக உருவாக்கும் கணிப்பு இயந்திரம்."
                  : "Generates a structured, professional, plain-language predictive report that anyone can understand without knowing astrology jargon. Evaluates Natal Event Promises, running Dasha-Bhukti, 12–24 month milestone windows, and tailored remedial guidance."}
              </p>
            </div>
          </div>

          {/* Control & Input Card */}
          <div className="mt-6 bg-white rounded-2xl shadow-sm border border-slate-200 p-5 sm:p-6">
            <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-100">
              {/* Input Mode Selector */}
              <div className="inline-flex p-1 bg-slate-100 rounded-xl text-xs font-medium">
                <button
                  onClick={() => setInputMode("saved")}
                  className={`px-3 py-1.5 rounded-lg transition-all ${
                    inputMode === "saved"
                      ? "bg-white text-[#153F6B] shadow-sm font-semibold"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  <User className="w-3.5 h-3.5 inline mr-1.5" />
                  {uiLang === "ta" ? "வாடிக்கையாளர் ஜாதகம்" : "Saved Horoscope"}
                </button>
                <button
                  onClick={() => setInputMode("manual")}
                  className={`px-3 py-1.5 rounded-lg transition-all ${
                    inputMode === "manual"
                      ? "bg-white text-[#153F6B] shadow-sm font-semibold"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  <Clock className="w-3.5 h-3.5 inline mr-1.5" />
                  {uiLang === "ta" ? "நேரடி உள்ளீடு" : "Direct Input"}
                </button>
                <button
                  onClick={() => setInputMode("saved_reports")}
                  className={`px-3 py-1.5 rounded-lg transition-all ${
                    inputMode === "saved_reports"
                      ? "bg-white text-[#153F6B] shadow-sm font-semibold"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  <Bookmark className="w-3.5 h-3.5 inline mr-1.5" />
                  {uiLang === "ta" ? "சேமித்த அறிக்கைகள்" : "Saved Reports"}
                </button>
              </div>

              {/* Language & Horizon Options */}
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1">
                  <span className="text-xs text-slate-500 font-medium">
                    {uiLang === "ta" ? "மொழி:" : "Lang:"}
                  </span>
                  <select
                    value={reportLang}
                    onChange={(e) => setReportLang(e.target.value as any)}
                    className="bg-transparent text-xs font-semibold text-[#153F6B] focus:outline-none cursor-pointer"
                  >
                    <option value="ta">தமிழ் (Tamil)</option>
                    <option value="en">English</option>
                    <option value="bilingual">இருமொழி (Bilingual)</option>
                  </select>
                </div>

                <div className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1">
                  <span className="text-xs text-slate-500 font-medium">
                    {uiLang === "ta" ? "கால அளவு:" : "Scan:"}
                  </span>
                  <select
                    value={monthsAhead}
                    onChange={(e) => setMonthsAhead(Number(e.target.value))}
                    className="bg-transparent text-xs font-semibold text-[#153F6B] focus:outline-none cursor-pointer"
                  >
                    <option value={12}>12 {uiLang === "ta" ? "மாதங்கள்" : "Months"}</option>
                    <option value={18}>18 {uiLang === "ta" ? "மாதங்கள்" : "Months"}</option>
                    <option value={24}>24 {uiLang === "ta" ? "மாதங்கள்" : "Months"}</option>
                    <option value={36}>36 {uiLang === "ta" ? "மாதங்கள்" : "Months"}</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Mode 1: Saved Horoscope Select */}
            {inputMode === "saved" && (
              <div className="mt-5 grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
                <div className="md:col-span-2">
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                    {uiLang === "ta" ? "வாடிக்கையாளர் ஜாதகத்தைத் தேர்ந்தெடுக்கவும்" : "Select Saved Horoscope"}
                  </label>
                  <select
                    value={selectedHoroscopeId}
                    onChange={(e) => setSelectedHoroscopeId(e.target.value)}
                    disabled={loadingHoroscopes}
                    className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm font-medium text-slate-900 focus:bg-white focus:ring-2 focus:ring-[#153F6B]/20 focus:border-[#153F6B] transition-all"
                  >
                    <option value="">-- {uiLang === "ta" ? "ஜாதகத்தை தேர்வு செய்க" : "Choose a horoscope"} --</option>
                    {savedHoroscopes.map((h) => (
                      <option key={h.id} value={h.id}>
                        {h.person_name} ({h.birth_date} • {h.birth_time})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                    {uiLang === "ta" ? "கணிப்பு தொடக்க தேதி" : "Target Reference Date"}
                  </label>
                  <input
                    type="date"
                    value={targetDate}
                    onChange={(e) => setTargetDate(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm text-slate-900 focus:bg-white focus:ring-2 focus:ring-[#153F6B]/20 focus:border-[#153F6B]"
                  />
                </div>
              </div>
            )}

            {/* Mode 2: Manual Direct Input */}
            {inputMode === "manual" && (
              <div className="mt-5 space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      {uiLang === "ta" ? "பெயர்" : "Native Name"}
                    </label>
                    <input
                      type="text"
                      value={manualName}
                      onChange={(e) => setManualName(e.target.value)}
                      placeholder="e.g. Suresh Kumar"
                      className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-sm text-slate-900 focus:bg-white focus:border-[#153F6B]"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      {uiLang === "ta" ? "பிறந்த தேதி" : "Birth Date"}
                    </label>
                    <input
                      type="date"
                      value={manualDate}
                      onChange={(e) => setManualDate(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-sm text-slate-900 focus:bg-white focus:border-[#153F6B]"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      {uiLang === "ta" ? "பிறந்த நேரம்" : "Birth Time (24h)"}
                    </label>
                    <input
                      type="time"
                      step="1"
                      value={manualTime}
                      onChange={(e) => setManualTime(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-sm text-slate-900 focus:bg-white focus:border-[#153F6B]"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      {uiLang === "ta" ? "பாலினம்" : "Gender"}
                    </label>
                    <select
                      value={manualGender}
                      onChange={(e) => setManualGender(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-sm text-slate-900 focus:bg-white focus:border-[#153F6B]"
                    >
                      <option value="male">{uiLang === "ta" ? "ஆண்" : "Male"}</option>
                      <option value="female">{uiLang === "ta" ? "பெண்" : "Female"}</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      {uiLang === "ta" ? "அட்சரேகை (Latitude)" : "Latitude"}
                    </label>
                    <input
                      type="text"
                      value={manualLat}
                      onChange={(e) => setManualLat(e.target.value)}
                      placeholder="13.0827"
                      className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-sm text-slate-900 focus:bg-white"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      {uiLang === "ta" ? "தீர்க்கரேகை (Longitude)" : "Longitude"}
                    </label>
                    <input
                      type="text"
                      value={manualLon}
                      onChange={(e) => setManualLon(e.target.value)}
                      placeholder="80.2707"
                      className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-sm text-slate-900 focus:bg-white"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      {uiLang === "ta" ? "கணிப்பு தொடக்க தேதி" : "Target Reference Date"}
                    </label>
                    <input
                      type="date"
                      value={targetDate}
                      onChange={(e) => setTargetDate(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-sm text-slate-900 focus:bg-white"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Mode 3: Saved Narrative Reports List */}
            {inputMode === "saved_reports" && (
              <div className="mt-5">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-bold text-slate-800">
                    {uiLang === "ta" ? "சேமிக்கப்பட்ட கணிப்பு அறிக்கைகள்" : "Saved Predictive Narrative Reports"}
                  </h3>
                  <button
                    onClick={loadSavedReports}
                    className="text-xs text-[#153F6B] hover:underline inline-flex items-center gap-1 font-medium"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${loadingSavedReports ? "animate-spin" : ""}`} />
                    {uiLang === "ta" ? "புதுப்பி" : "Refresh"}
                  </button>
                </div>

                {loadingSavedReports ? (
                  <div className="py-8 text-center text-slate-500 text-sm">
                    {uiLang === "ta" ? "ஏற்றுகிறது..." : "Loading saved reports..."}
                  </div>
                ) : savedReports.length === 0 ? (
                  <div className="py-8 text-center border-2 border-dashed border-slate-200 rounded-xl text-slate-500 text-sm">
                    {uiLang === "ta"
                      ? "இதுவரை எந்த அறிக்கையும் சேமிக்கப்படவில்லை. புதிய அறிக்கையை உருவாக்கி சேமிக்கவும்."
                      : "No saved reports yet. Generate a narrative report and click 'Save to Library'."}
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {savedReports.map((r) => (
                      <div
                        key={r.id}
                        className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 hover:border-[#153F6B]/40 transition-all flex flex-col justify-between"
                      >
                        <div>
                          <div className="flex items-center justify-between gap-2">
                            <span className="text-xs font-bold text-[#153F6B] truncate">{r.title}</span>
                            <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded bg-slate-200 text-slate-700">
                              {r.language}
                            </span>
                          </div>
                          <div className="mt-1 text-xs text-slate-600">
                            {r.person_name} • {r.birth_date}
                          </div>
                        </div>
                        <div className="mt-3 pt-2 border-t border-slate-200 flex items-center justify-between">
                          <button
                            onClick={() => handleLoadSavedReport(r.id)}
                            className="text-xs text-[#153F6B] font-semibold hover:underline inline-flex items-center gap-1"
                          >
                            <ExternalLink className="w-3.5 h-3.5" />
                            {uiLang === "ta" ? "திறக்க" : "Open"}
                          </button>
                          <button
                            onClick={() => handleDeleteSavedReport(r.id)}
                            className="text-xs text-rose-600 hover:text-rose-800 p-1"
                            title="Delete"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Error Message */}
            {errorMsg && (
              <div className="mt-4 p-3.5 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* Submit Action Button */}
            {inputMode !== "saved_reports" && (
              <div className="mt-6 flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-slate-100">
                <div className="text-xs text-slate-500">
                  {uiLang === "ta"
                    ? "கிருஷ்ணமூர்த்தி பத்ததி (249 உப-அதிபதி) கணித முறையில் நொடிகளின் துல்லியத்தில் கணக்கிடப்படுகிறது."
                    : "Deterministic KP stellar calculations using Krishnamurti 249 sub-division table."}
                </div>
                <button
                  onClick={handleGenerate}
                  disabled={loading}
                  className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-[#153F6B] to-[#0A192F] text-white text-sm font-semibold shadow-md hover:from-[#1b4e84] hover:to-[#122849] disabled:opacity-50 transition-all inline-flex items-center gap-2"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      {uiLang === "ta" ? "கணக்கிடப்படுகிறது..." : "Generating Report..."}
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 text-[#B4872B]" />
                      {uiLang === "ta" ? "கணிப்பு உரை அறிக்கை உருவாக்குக" : "Generate Narrative Report"}
                    </>
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Report Display Container */}
          {reportData && (
            <div className="mt-8 space-y-6">
              {/* Report Executive Bar */}
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-5 flex flex-wrap items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-[#B4872B]">
                      {reportData.report_id}
                    </span>
                    <span className="text-slate-300">•</span>
                    <span className="text-xs text-slate-500">
                      {uiLang === "ta" ? "ஆய்வு நாள்" : "Reference Date"}: {reportData.target_date}
                    </span>
                  </div>
                  <h2 className="text-xl font-extrabold text-[#0A192F] mt-0.5">
                    {reportData.person_details.name}
                  </h2>
                  <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-slate-600">
                    <span>
                      <b>{isTa ? "லக்னம்" : "Lagna"}:</b> {isTa ? reportData.person_details.lagna_ta : reportData.person_details.lagna}
                    </span>
                    <span>•</span>
                    <span>
                      <b>{isTa ? "ராசி" : "Moon Sign"}:</b> {isTa ? reportData.person_details.moon_sign_ta : reportData.person_details.moon_sign}
                    </span>
                    <span>•</span>
                    <span>
                      <b>{isTa ? "நட்சத்திரம்" : "Star"}:</b> {isTa ? reportData.person_details.nakshatra_ta : reportData.person_details.nakshatra}
                    </span>
                    <span>•</span>
                    <span>
                      <b>{isTa ? "வயது" : "Age"}:</b> {reportData.person_details.current_age}
                    </span>
                  </div>
                </div>

                {/* Toolbar Buttons */}
                <div className="flex flex-wrap items-center gap-2">
                  <button
                    onClick={handleCopyNarrative}
                    className="px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700 text-xs font-semibold inline-flex items-center gap-1.5 transition-all"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5 text-slate-500" />}
                    {copied ? (uiLang === "ta" ? "நகலெடுக்கப்பட்டது!" : "Copied!") : (uiLang === "ta" ? "நகலெடு" : "Copy")}
                  </button>

                  <button
                    onClick={() => handleDownloadPdf("ta")}
                    disabled={downloadingPdf}
                    className="px-3 py-1.5 rounded-lg border border-[#B4872B]/40 bg-[#FAF2DE] hover:bg-[#faebd0] text-[#8B6914] text-xs font-semibold inline-flex items-center gap-1.5 transition-all"
                  >
                    <Download className="w-3.5 h-3.5" />
                    PDF (தமிழ்)
                  </button>

                  <button
                    onClick={() => handleDownloadPdf("en")}
                    disabled={downloadingPdf}
                    className="px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700 text-xs font-semibold inline-flex items-center gap-1.5 transition-all"
                  >
                    <Download className="w-3.5 h-3.5" />
                    PDF (English)
                  </button>

                  <button
                    onClick={handleSaveReport}
                    disabled={saving}
                    className="px-3 py-1.5 rounded-lg bg-[#153F6B] hover:bg-[#0A192F] text-white text-xs font-semibold inline-flex items-center gap-1.5 transition-all shadow-sm"
                  >
                    <Save className="w-3.5 h-3.5 text-[#B4872B]" />
                    {saving ? (uiLang === "ta" ? "சேமிக்கிறது..." : "Saving...") : (uiLang === "ta" ? "சேமி" : "Save")}
                  </button>
                </div>
              </div>

              {saveSuccessMsg && (
                <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 text-xs flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>{saveSuccessMsg}</span>
                </div>
              )}

              {/* View Navigation Tabs */}
              <div className="flex border-b border-slate-200 overflow-x-auto gap-2 text-xs font-semibold">
                <button
                  onClick={() => setActiveTab("all")}
                  className={`pb-3 px-3 transition-all border-b-2 whitespace-nowrap ${
                    activeTab === "all"
                      ? "border-[#153F6B] text-[#153F6B]"
                      : "border-transparent text-slate-500 hover:text-slate-800"
                  }`}
                >
                  {uiLang === "ta" ? "முழு அறிக்கை (All Sections)" : "Complete Report"}
                </button>
                <button
                  onClick={() => setActiveTab("promise")}
                  className={`pb-3 px-3 transition-all border-b-2 whitespace-nowrap ${
                    activeTab === "promise"
                      ? "border-[#153F6B] text-[#153F6B]"
                      : "border-transparent text-slate-500 hover:text-slate-800"
                  }`}
                >
                  1. {uiLang === "ta" ? "ஜாதக வாக்குறுதி" : "Natal Event Promise"}
                </button>
                <button
                  onClick={() => setActiveTab("dasha")}
                  className={`pb-3 px-3 transition-all border-b-2 whitespace-nowrap ${
                    activeTab === "dasha"
                      ? "border-[#153F6B] text-[#153F6B]"
                      : "border-transparent text-slate-500 hover:text-slate-800"
                  }`}
                >
                  2. {uiLang === "ta" ? "தசா-புத்தி பலன்கள்" : "Running Dasha-Bhukti"}
                </button>
                <button
                  onClick={() => setActiveTab("milestones")}
                  className={`pb-3 px-3 transition-all border-b-2 whitespace-nowrap ${
                    activeTab === "milestones"
                      ? "border-[#153F6B] text-[#153F6B]"
                      : "border-transparent text-slate-500 hover:text-slate-800"
                  }`}
                >
                  3. {uiLang === "ta" ? "முக்கிய காலக்கட்டங்கள் (12–24 Months)" : "Milestone Windows"}
                </button>
                <button
                  onClick={() => setActiveTab("remedies")}
                  className={`pb-3 px-3 transition-all border-b-2 whitespace-nowrap ${
                    activeTab === "remedies"
                      ? "border-[#153F6B] text-[#153F6B]"
                      : "border-transparent text-slate-500 hover:text-slate-800"
                  }`}
                >
                  4. {uiLang === "ta" ? "வழிகாட்டல் & பரிகாரங்கள்" : "Do's & Don'ts / Remedies"}
                </button>
              </div>

              {/* ------------------------------------------------------------- */}
              {/* SECTION 1: NATAL EVENT PROMISE (ஜாதக வாக்குறுதி)             */}
              {/* ------------------------------------------------------------- */}
              {(activeTab === "all" || activeTab === "promise") && (
                <section className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 space-y-6">
                  <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                    <div>
                      <h3 className="text-lg font-extrabold text-[#0A192F] flex items-center gap-2">
                        <span className="w-7 h-7 rounded-lg bg-[#153F6B] text-white flex items-center justify-center text-xs font-bold">
                          1
                        </span>
                        {isTa
                          ? "ஜாதக வாக்குறுதி (Natal Event Promise)"
                          : "Natal Event Promise (Evaluated Cuspal Sub-Lords)"}
                      </h3>
                      <p className="text-xs text-slate-500 mt-1">
                        {isTa
                          ? "1, 2, 5, 7, 10, 11-ஆம் பாவக உப-அதிபதிகளை ஆய்வு செய்து வாழ்க்கையில் உறுதியாக கிடைக்கும் பலன்கள், தாமதங்கள் மற்றும் விழிப்புணர்வு பகுதிகள்."
                          : "Evaluates primary cuspal sub-lords (1st, 2nd, 5th, 7th, 10th, 11th) to clearly state what life events are strongly promised, delayed, or cautioned in this lifetime."}
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        {reportData.natal_promise.strong_promises_count} {isTa ? "உறுதி" : "Promised"}
                      </span>
                      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
                        {reportData.natal_promise.delayed_count} {isTa ? "தாமதம்" : "Delayed"}
                      </span>
                      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
                        {reportData.natal_promise.caution_count} {isTa ? "கவனம்" : "Caution"}
                      </span>
                    </div>
                  </div>

                  {/* Overall Synthesis Banner */}
                  <div className="bg-amber-50/70 border border-amber-200 rounded-xl p-4.5 text-amber-950 flex items-start gap-3">
                    <Sparkles className="w-5 h-5 text-[#B4872B] shrink-0 mt-0.5" />
                    <div>
                      <div className="text-xs font-bold uppercase tracking-wider text-[#8B6914] mb-1">
                        {isTa ? "ஜாதக வாக்குறுதி பொது சுருக்கம்" : "Life Blueprint Executive Synthesis"}
                      </div>
                      <p className="text-sm font-medium leading-relaxed">
                        {isTa
                          ? reportData.natal_promise.overall_synthesis_ta
                          : reportData.natal_promise.overall_synthesis_en}
                      </p>
                    </div>
                  </div>

                  {/* 6 Primary Cuspal Sub-Lord Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {reportData.natal_promise.items.map((it) => {
                      const isPromised = it.verdict === "strongly_promised";
                      const isDelayed = it.verdict === "delayed_fruition";
                      const badgeBg = isPromised
                        ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                        : isDelayed
                        ? "bg-amber-50 text-amber-800 border-amber-200"
                        : "bg-rose-50 text-rose-800 border-rose-200";

                      return (
                        <div
                          key={it.cusp}
                          className="bg-slate-50/70 rounded-xl p-4.5 border border-slate-200 flex flex-col justify-between hover:border-slate-300 transition-all"
                        >
                          <div>
                            <div className="flex items-start justify-between gap-2 mb-2">
                              <div>
                                <span className="inline-block px-2 py-0.5 rounded text-[11px] font-bold bg-[#153F6B] text-white mr-1.5">
                                  Cusp {it.cusp}
                                </span>
                                <span className="text-sm font-bold text-slate-900">
                                  {isTa ? it.domain_ta : it.domain_en}
                                </span>
                              </div>
                              <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold border shrink-0 ${badgeBg}`}>
                                {isTa ? it.verdict_label_ta : it.verdict_label_en}
                              </span>
                            </div>

                            <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500 mb-3">
                              <span className="font-semibold text-slate-700">
                                CSL: {it.cusp_sub_lord}
                              </span>
                              <span>•</span>
                              <span>Star: {it.star_lord}</span>
                              <span>•</span>
                              <span>Sub-Sub: {it.sub_sub_lord}</span>
                            </div>

                            <p className="text-xs text-slate-700 leading-relaxed">
                              {isTa ? it.plain_narrative_ta : it.plain_narrative_en}
                            </p>
                          </div>

                          <div className="mt-3 pt-3 border-t border-slate-200/80 text-xs text-[#0F766E] font-medium flex items-start gap-1.5">
                            <span className="font-bold shrink-0">{isTa ? "வழிகாட்டல்:" : "Takeaway:"}</span>
                            <span>{isTa ? it.practical_takeaway_ta : it.practical_takeaway_en}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </section>
              )}

              {/* ------------------------------------------------------------- */}
              {/* SECTION 2: RUNNING DASHA-BHUKTI ANALYSIS                    */}
              {/* ------------------------------------------------------------- */}
              {(activeTab === "all" || activeTab === "dasha") && (
                <section className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 space-y-6">
                  <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                    <div>
                      <h3 className="text-lg font-extrabold text-[#0A192F] flex items-center gap-2">
                        <span className="w-7 h-7 rounded-lg bg-[#153F6B] text-white flex items-center justify-center text-xs font-bold">
                          2
                        </span>
                        {isTa
                          ? "தற்போதைய தசா-புத்தி பலன்கள் (Running Dasha-Bhukti Impact)"
                          : "Running Dasha-Bhukti Analysis & Real-World Impact"}
                      </h3>
                      <p className="text-xs text-slate-500 mt-1">
                        {isTa
                          ? "தற்போது நடைபெறும் மகா திசை, புக்தி மற்றும் அந்தர நாதர்களின் நட்சத்திர, உப-அதிபதி தொடர்புகள் மற்றும் அன்றாட வாழ்வியல் தாக்கம்."
                          : "Breaks down currently running Mahadasha, Bhukti, and Antara lords, their star lords, sub-lords, and their practical real-world impact."}
                      </p>
                    </div>

                    <div className="text-right">
                      <div className="text-[11px] font-semibold text-slate-500 uppercase">
                        {isTa ? "சாதகக் குறியீடு" : "Favorability Index"}
                      </div>
                      <div className="text-xl font-extrabold text-[#153F6B]">
                        {reportData.running_dasha.favorable_score}%
                      </div>
                    </div>
                  </div>

                  {/* Active Period Banner */}
                  <div className="bg-slate-900 text-white rounded-xl p-5 border border-slate-800">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <h4 className="text-base font-extrabold text-[#B4872B]">
                        {isTa ? reportData.running_dasha.phase_title_ta : reportData.running_dasha.phase_title_en}
                      </h4>
                      <span className="text-xs text-slate-400">
                        {reportData.running_dasha.bhukti.start_date} to {reportData.running_dasha.bhukti.end_date}
                      </span>
                    </div>
                    <p className="mt-2 text-xs sm:text-sm text-slate-300 leading-relaxed">
                      {isTa ? reportData.running_dasha.phase_theme_ta : reportData.running_dasha.phase_theme_en}
                    </p>
                  </div>

                  {/* Hierarchy Table */}
                  <div className="overflow-x-auto border border-slate-200 rounded-xl">
                    <table className="w-full text-xs text-left">
                      <thead className="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                        <tr>
                          <th className="px-3.5 py-2.5">{isTa ? "நிலை" : "Hierarchy Level"}</th>
                          <th className="px-3.5 py-2.5">{isTa ? "அதிபதி" : "Planet Lord"}</th>
                          <th className="px-3.5 py-2.5">{isTa ? "நட்சத்திர அதிபதி" : "Star Lord"}</th>
                          <th className="px-3.5 py-2.5">{isTa ? "உப-அதிபதி" : "Sub-Lord"}</th>
                          <th className="px-3.5 py-2.5">{isTa ? "கால அளவு" : "Duration & Dates"}</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {[
                          reportData.running_dasha.mahadasha,
                          reportData.running_dasha.bhukti,
                          reportData.running_dasha.antara,
                        ].map((d, idx) => (
                          <tr key={idx} className="hover:bg-slate-50/80">
                            <td className="px-3.5 py-2.5 font-bold text-[#153F6B]">
                              {isTa ? d.level_name_ta : d.level_name_en}
                            </td>
                            <td className="px-3.5 py-2.5 font-medium text-slate-900">
                              {isTa ? d.lord_ta : d.lord}
                            </td>
                            <td className="px-3.5 py-2.5 text-slate-700">
                              {isTa ? d.star_lord_ta : d.star_lord}
                            </td>
                            <td className="px-3.5 py-2.5 text-slate-700">
                              {isTa ? d.sub_lord_ta : d.sub_lord}
                            </td>
                            <td className="px-3.5 py-2.5 text-slate-600">
                              {d.start_date} → {d.end_date} ({d.duration_formatted})
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* 4-Dimensional Real-World Impact Grid */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="bg-blue-50/60 border border-blue-200 rounded-xl p-4">
                      <div className="flex items-center gap-2 text-blue-900 font-bold text-xs uppercase mb-1.5">
                        <Briefcase className="w-4 h-4 text-blue-600" />
                        {isTa ? "தொழில் மற்றும் பணிச் சூழல்" : "Career & Work Environment"}
                      </div>
                      <p className="text-xs text-slate-700 leading-relaxed">
                        {isTa ? reportData.running_dasha.career_impact_ta : reportData.running_dasha.career_impact_en}
                      </p>
                    </div>

                    <div className="bg-emerald-50/60 border border-emerald-200 rounded-xl p-4">
                      <div className="flex items-center gap-2 text-emerald-900 font-bold text-xs uppercase mb-1.5">
                        <Coins className="w-4 h-4 text-emerald-600" />
                        {isTa ? "பணப்புழக்கம் மற்றும் சேமிப்பு" : "Financial Liquidity & Savings"}
                      </div>
                      <p className="text-xs text-slate-700 leading-relaxed">
                        {isTa ? reportData.running_dasha.finance_impact_ta : reportData.running_dasha.finance_impact_en}
                      </p>
                    </div>

                    <div className="bg-rose-50/60 border border-rose-200 rounded-xl p-4">
                      <div className="flex items-center gap-2 text-rose-900 font-bold text-xs uppercase mb-1.5">
                        <Heart className="w-4 h-4 text-rose-600" />
                        {isTa ? "குடும்பம் மற்றும் தாம்பத்திய உறவு" : "Family & Marital Harmony"}
                      </div>
                      <p className="text-xs text-slate-700 leading-relaxed">
                        {isTa
                          ? reportData.running_dasha.relationship_impact_ta
                          : reportData.running_dasha.relationship_impact_en}
                      </p>
                    </div>

                    <div className="bg-purple-50/60 border border-purple-200 rounded-xl p-4">
                      <div className="flex items-center gap-2 text-purple-900 font-bold text-xs uppercase mb-1.5">
                        <Sparkles className="w-4 h-4 text-purple-600" />
                        {isTa ? "உடல் நலம் மற்றும் மன அமைதி" : "Health, Energy & Vitality"}
                      </div>
                      <p className="text-xs text-slate-700 leading-relaxed">
                        {isTa ? reportData.running_dasha.health_impact_ta : reportData.running_dasha.health_impact_en}
                      </p>
                    </div>
                  </div>
                </section>
              )}

              {/* ------------------------------------------------------------- */}
              {/* SECTION 3: UPCOMING MILESTONE WINDOWS                       */}
              {/* ------------------------------------------------------------- */}
              {(activeTab === "all" || activeTab === "milestones") && (
                <section className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 space-y-6">
                  <div className="pb-3 border-b border-slate-100">
                    <h3 className="text-lg font-extrabold text-[#0A192F] flex items-center gap-2">
                      <span className="w-7 h-7 rounded-lg bg-[#153F6B] text-white flex items-center justify-center text-xs font-bold">
                        3
                      </span>
                      {isTa
                        ? `அடுத்த ${monthsAhead} மாதங்களின் முக்கிய காலக்கட்டங்கள்`
                        : `Upcoming Milestone Windows (Next ${monthsAhead} Months)`}
                    </h3>
                    <p className="text-xs text-slate-500 mt-1">
                      {isTa
                        ? "தொழில் உயர்வு, தன வரவு மற்றும் திருமண முன்னேற்றத்திற்கான குறிப்பிட்ட மாதக் காலக்கட்டங்கள் மற்றும் செயல் திட்டங்கள்."
                        : "Pinpoints specific monthly windows over the next 12–24 months for career leaps, financial gains, or matrimonial progress."}
                    </p>
                  </div>

                  <div className="space-y-4">
                    {reportData.milestone_windows.map((w) => (
                      <div
                        key={w.id}
                        className="bg-slate-50/70 border border-slate-200 rounded-xl p-5 hover:border-[#153F6B]/30 transition-all"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                          <div className="flex items-center gap-2">
                            <span className="px-2.5 py-1 rounded-lg bg-[#153F6B] text-white text-xs font-bold">
                              {isTa ? w.window_title_ta : w.window_title_en}
                            </span>
                            <span className="text-xs font-bold text-slate-700">
                              {isTa ? w.domain_label_ta : w.domain_label_en}
                            </span>
                          </div>
                          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800">
                            {isTa ? w.status_ta : w.status}
                          </span>
                        </div>

                        <h4 className="text-sm font-bold text-slate-900 mt-2">
                          {isTa ? w.headline_ta : w.headline_en}
                        </h4>

                        <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">
                          {isTa ? w.plain_narrative_ta : w.plain_narrative_en}
                        </p>

                        {/* Action Steps */}
                        <div className="mt-3 pt-3 border-t border-slate-200">
                          <div className="text-[11px] font-bold uppercase tracking-wider text-[#0F766E] mb-1.5">
                            {isTa ? "செயல் திட்டம் (Practical Checklist)" : "Action Steps Checklist"}
                          </div>
                          <ul className="space-y-1 text-xs text-slate-700">
                            {(isTa ? w.action_plan_ta : w.action_plan_en).map((step, sIdx) => (
                              <li key={sIdx} className="flex items-start gap-2">
                                <Check className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                                <span>{step}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {/* ------------------------------------------------------------- */}
              {/* SECTION 4: DO'S, DON'TS & TAILORED REMEDIAL ADVICE           */}
              {/* ------------------------------------------------------------- */}
              {(activeTab === "all" || activeTab === "remedies") && (
                <section className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 space-y-6">
                  <div className="pb-3 border-b border-slate-100">
                    <h3 className="text-lg font-extrabold text-[#0A192F] flex items-center gap-2">
                      <span className="w-7 h-7 rounded-lg bg-[#153F6B] text-white flex items-center justify-center text-xs font-bold">
                        4
                      </span>
                      {isTa
                        ? "செய்ய வேண்டியவை, தவிர்க்க வேண்டியவை & பரிகார ஆலோசனைகள்"
                        : "Do's & Don'ts / Tailored Remedial Guidance"}
                    </h3>
                    <p className="text-xs text-slate-500 mt-1">
                      {isTa
                        ? "தற்போதைய தசா-புத்தி மற்றும் பாவக உப-அதிபதி ஆற்றல்களுக்கு ஏற்ற நடைமுறை நற்செயல்கள் மற்றும் எளிய பரிகாரங்கள்."
                        : "Actionable real-world advice and spiritual balancing tailored directly to active sub-lord significations."}
                    </p>
                  </div>

                  {/* Side-by-Side Do's and Don'ts */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-emerald-50/70 border border-emerald-200 rounded-xl p-5">
                      <div className="flex items-center gap-2 text-emerald-900 font-bold text-sm mb-3">
                        <ShieldCheck className="w-4 h-4 text-emerald-600" />
                        {isTa ? "செய்ய வேண்டியவை (Do's)" : "What To Do (Do's)"}
                      </div>
                      <ul className="space-y-2 text-xs text-slate-800">
                        {(isTa ? reportData.remedies.dos_ta : reportData.remedies.dos_en).map((d, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <Check className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                            <span>{d}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="bg-rose-50/70 border border-rose-200 rounded-xl p-5">
                      <div className="flex items-center gap-2 text-rose-900 font-bold text-sm mb-3">
                        <ShieldAlert className="w-4 h-4 text-rose-600" />
                        {isTa ? "தவிர்க்க வேண்டியவை (Don'ts)" : "What To Avoid (Don'ts)"}
                      </div>
                      <ul className="space-y-2 text-xs text-slate-800">
                        {(isTa ? reportData.remedies.donts_ta : reportData.remedies.donts_en).map((d, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <span className="text-rose-600 font-bold shrink-0">✕</span>
                            <span>{d}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Spiritual, Charitable & Lifestyle Balancing Cards */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="bg-purple-50/60 border border-purple-200 rounded-xl p-4.5">
                      <div className="text-xs font-bold text-purple-900 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                        <span>🕉️</span>
                        {isTa ? "இறை வழிபாடு & மந்திரம்" : "Deity Meditation & Prayers"}
                      </div>
                      <p className="text-xs text-slate-700 leading-relaxed">
                        {isTa ? reportData.remedies.deity_prayer_ta : reportData.remedies.deity_prayer_en}
                      </p>
                    </div>

                    <div className="bg-amber-50/60 border border-amber-200 rounded-xl p-4.5">
                      <div className="text-xs font-bold text-amber-900 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                        <span>🤝</span>
                        {isTa ? "கர்ம விழிப்புணர்வு & தானம்" : "Charitable Dhanam"}
                      </div>
                      <p className="text-xs text-slate-700 leading-relaxed">
                        {isTa ? reportData.remedies.charity_action_ta : reportData.remedies.charity_action_en}
                      </p>
                    </div>

                    <div className="bg-sky-50/60 border border-sky-200 rounded-xl p-4.5">
                      <div className="text-xs font-bold text-sky-900 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                        <span>🧘</span>
                        {isTa ? "வாழ்க்கை முறை சீரமைப்பு" : "Lifestyle & Focus Habits"}
                      </div>
                      <p className="text-xs text-slate-700 leading-relaxed">
                        {isTa ? reportData.remedies.lifestyle_guidance_ta : reportData.remedies.lifestyle_guidance_en}
                      </p>
                    </div>

                    <div className="bg-slate-100 border border-slate-200 rounded-xl p-4.5">
                      <div className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                        <span>🍀</span>
                        {isTa ? "அதிர்ஷ்ட தினங்கள் & நிறங்கள்" : "Auspicious Days & Colors"}
                      </div>
                      <p className="text-xs text-slate-700 leading-relaxed">
                        {isTa ? reportData.remedies.lucky_day_color_ta : reportData.remedies.lucky_day_color_en}
                      </p>
                    </div>
                  </div>
                </section>
              )}

              {/* Ethical Astrological Disclaimer */}
              <div className="p-4 bg-slate-100 border border-slate-200 rounded-xl text-slate-500 text-xs text-center leading-relaxed">
                {isTa ? reportData.disclaimer_ta : reportData.disclaimer_en}
              </div>
            </div>
          )}
        </div>
      </div>
    </FeatureGuard>
  );
}

export default function KpPredictiveNarrativePage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-[#F8FAFC]">
          <div className="w-8 h-8 border-4 border-[#153F6B] border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <KpPredictiveNarrativeContent />
    </Suspense>
  );
}
