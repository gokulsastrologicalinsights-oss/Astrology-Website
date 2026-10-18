"use client";

import React, { useState, useEffect, useMemo } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import {
  RemedyAnalysisResponse,
  RecommendedRemedy,
  ChartFactorExplanation,
  SaveRemedyReportRequest,
  SavedRemedyReportResponse,
} from "@/lib/types";
import {
  saveRemedyReport,
  listRemedyReportsForHoroscope,
} from "@/lib/api";
import {
  Sparkles,
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Printer,
  Save,
  BookOpen,
  MapPin,
  Calendar,
  Clock,
  Flame,
  Filter,
  Check,
  FileText,
  ChevronDown,
  ChevronUp,
  Info,
  UserCheck,
  Layers,
  Search,
} from "lucide-react";

interface PersonalizedRemedySectionProps {
  analysis: RemedyAnalysisResponse;
  horoscopeId?: string;
  onRefresh?: () => void;
  isLoading?: boolean;
}

export function PersonalizedRemedySection({
  analysis,
  horoscopeId,
  onRefresh,
  isLoading = false,
}: PersonalizedRemedySectionProps) {
  const { language } = useLanguage();
  const { user, session, isAuthenticated } = useAuth();

  // Astrologer report configuration state
  const [reviewStatus, setReviewStatus] = useState<"draft" | "reviewed" | "approved">("draft");
  const [astrologerNotes, setAstrologerNotes] = useState<string>("");
  const [reportLanguage, setReportLanguage] = useState<"en" | "ta">(language === "ta" ? "ta" : "en");
  const [selectedRemedyCodes, setSelectedRemedyCodes] = useState<Set<string>>(
    () => new Set(analysis.recommendations.map((r) => r.remedy.code))
  );

  // Saving state
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccessMessage, setSaveSuccessMessage] = useState<string | null>(null);
  const [saveErrorMessage, setSaveErrorMessage] = useState<string | null>(null);

  // Saved reports history
  const [savedReports, setSavedReports] = useState<SavedRemedyReportResponse[]>([]);
  const [loadingReports, setLoadingReports] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  // Filters state
  const [factorFilter, setFactorFilter] = useState<string>("all");
  const [remedyTypeFilter, setRemedyTypeFilter] = useState<string>("all");
  const [priorityFilter, setPriorityFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Keep reportLanguage synced with app language unless edited
  useEffect(() => {
    setReportLanguage(language === "ta" ? "ta" : "en");
  }, [language]);

  // Load existing saved reports for this horoscope if horoscopeId is provided
  useEffect(() => {
    if (horoscopeId && session?.access_token) {
      setLoadingReports(true);
      listRemedyReportsForHoroscope(horoscopeId, session.access_token)
        .then((res) => {
          setSavedReports(res.reports || []);
          if (res.reports && res.reports.length > 0) {
            const latest = res.reports[0];
            setReviewStatus(latest.review_status);
            if (latest.astrologer_notes) {
              setAstrologerNotes(latest.astrologer_notes);
            }
            if (latest.selected_remedy_codes && latest.selected_remedy_codes.length > 0) {
              setSelectedRemedyCodes(new Set(latest.selected_remedy_codes));
            }
          }
        })
        .catch((err) => {
          console.warn("Could not fetch saved remedy reports:", err);
        })
        .finally(() => {
          setLoadingReports(false);
        });
    }
  }, [horoscopeId, session?.access_token]);

  const toggleRemedySelection = (code: string) => {
    const next = new Set(selectedRemedyCodes);
    if (next.has(code)) {
      next.delete(code);
    } else {
      next.add(code);
    }
    setSelectedRemedyCodes(next);
  };

  const selectAllRemedies = () => {
    setSelectedRemedyCodes(new Set(analysis.recommendations.map((r) => r.remedy.code)));
  };

  const deselectAllRemedies = () => {
    setSelectedRemedyCodes(new Set());
  };

  const handleSaveReport = async () => {
    if (!horoscopeId) {
      setSaveErrorMessage(
        language === "ta"
          ? "சேமிக்கப்பட்ட ஜாதகத்திற்கான பரிகார அறிக்கையை மட்டுமே சேமிக்க முடியும். முதலில் உங்கள் ஜாதகத்தை சேமிக்கவும்."
          : "You can only persist reports for saved horoscopes. Please save the horoscope first."
      );
      return;
    }

    if (!session?.access_token) {
      setSaveErrorMessage(
        language === "ta"
          ? "பரிகார அறிக்கையைச் சேமிக்க உள்நுழையவும்."
          : "Please sign in with an authenticated session to save remedy reports."
      );
      return;
    }

    setIsSaving(true);
    setSaveSuccessMessage(null);
    setSaveErrorMessage(null);

    try {
      const payload: SaveRemedyReportRequest = {
        horoscope_id: horoscopeId,
        input_data_fingerprint: analysis.input_fingerprint,
        person_name: analysis.person_name || "Birth Chart",
        review_status: reviewStatus,
        astrologer_notes: astrologerNotes.trim() || undefined,
        selected_remedy_codes: Array.from(selectedRemedyCodes),
        language: reportLanguage,
        analysis_snapshot: analysis,
      };

      const saved = await saveRemedyReport(payload, session.access_token);
      setSaveSuccessMessage(
        language === "ta"
          ? "பரிகார அறிக்கை வெற்றிகரமாகச் சேமிக்கப்பட்டது!"
          : "Remedy report saved successfully!"
      );
      setSavedReports((prev) => [saved, ...prev.filter((r) => r.id !== saved.id)]);
    } catch (err: any) {
      console.error("Failed to save remedy report:", err);
      setSaveErrorMessage(
        err?.data?.detail ||
          err?.message ||
          (language === "ta"
            ? "அறிக்கையைச் சேமிப்பதில் பிழை ஏற்பட்டது. மீண்டும் முயற்சிக்கவும்."
            : "Failed to save remedy report. Please try again.")
      );
    } finally {
      setIsSaving(false);
    }
  };

  // Filter diagnosed factors
  const filteredFactors = useMemo(() => {
    return analysis.diagnosed_factors.filter((f) => {
      if (factorFilter === "affliction") {
        return f.factor_type === "debilitation" || f.factor_type === "combustion" || f.factor_type === "dusthana";
      }
      if (factorFilter === "kuja") return f.factor_type === "kuja_dosha";
      if (factorFilter === "dasa") return f.factor_type === "running_dasa";
      return true;
    });
  }, [analysis.diagnosed_factors, factorFilter]);

  // Filter recommendations
  const filteredRecommendations = useMemo(() => {
    return analysis.recommendations.filter((rec) => {
      if (remedyTypeFilter !== "all" && rec.remedy.remedy_type !== remedyTypeFilter) {
        return false;
      }
      if (priorityFilter !== "all" && rec.priority_tier !== priorityFilter) {
        return false;
      }
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesName =
          rec.remedy.name_en.toLowerCase().includes(q) ||
          rec.remedy.name_ta.toLowerCase().includes(q) ||
          rec.remedy.graha.toLowerCase().includes(q);
        const matchesMantra =
          rec.remedy.sanskrit_text?.toLowerCase().includes(q) ||
          rec.remedy.meaning_en?.toLowerCase().includes(q) ||
          rec.remedy.meaning_ta?.toLowerCase().includes(q);
        return matchesName || matchesMantra;
      }
      return true;
    });
  }, [analysis.recommendations, remedyTypeFilter, priorityFilter, searchQuery]);

  // Check if Yogakaraka protection is active
  const hasYogakarakaWarning = analysis.recommendations.some((r) => r.yogakaraka_warning);

  const yogakaraka =
    (analysis.chart_context as any)?.yogakaraka_graha ||
    (analysis.chart_context?.yogakaraka_planets && analysis.chart_context.yogakaraka_planets.length > 0
      ? analysis.chart_context.yogakaraka_planets[0]
      : null);

  const afflictedGrahas: string[] =
    (analysis.chart_context as any)?.afflicted_grahas ||
    [
      ...(analysis.chart_context?.debilitated_planets || []),
      ...(analysis.chart_context?.combust_planets || []),
    ];

  const kujaStatus =
    analysis.chart_context?.kuja_dosha_status ||
    ((analysis.chart_context as any)?.kuja_dosha_present
      ? (analysis.chart_context as any)?.kuja_dosha_cancelled
        ? "cancelled"
        : "present"
      : "none");

  return (
    <div className="space-y-6">
      {/* 1. Header Banner & Chart Context Card */}
      <div className="rounded-2xl border border-[#DDE5F0] bg-white p-5 sm:p-6 shadow-xs relative overflow-hidden space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-50 text-purple-800 border border-purple-200">
                <Sparkles className="w-3.5 h-3.5 text-purple-600" />
                <span>
                  {language === "ta"
                    ? "ஜாதக பரிசீலனை அடிப்படையிலான பரிகாரங்கள்"
                    : "Personalized Chart-Based Remedies"}
                </span>
              </span>
              {yogakaraka && (
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-50 text-amber-900 border border-amber-300">
                  <Flame className="w-3.5 h-3.5 text-amber-600" />
                  <span>
                    {language === "ta"
                      ? `யோககாரகன்: ${String(yogakaraka).toUpperCase()}`
                      : `Yogakaraka: ${String(yogakaraka).toUpperCase()}`}
                  </span>
                </span>
              )}
            </div>

            <h2 className="font-serif text-xl sm:text-2xl font-bold text-[#102A4C] flex items-center gap-2">
              <span>{analysis.person_name || "Birth Chart"}</span>
              <span className="text-xs font-sans font-normal text-[#64748B]">
                ({analysis.birth_date} {analysis.birth_time})
              </span>
            </h2>

            <p className="text-xs sm:text-sm text-[#52667E] max-w-2xl leading-relaxed">
              {language === "ta"
                ? "பராசர சாஸ்திர விதிகளின்படி நவகிரக அமைப்புகள், நீச-அஸ்தமன நிலைகள், தசா-புக்தி மற்றும் பாவங்கள் ஆராயப்பட்டு வடிவமைக்கப்பட்ட பரிந்துரைகள்."
                : "Deterministic rule-based diagnosis of debilitation, combustion, dusthana placements, running Dasa-Bhukti periods, and BPHS Ch. 34 Yogakaraka protections."}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2 shrink-0">
            <button
              type="button"
              onClick={() => window.print()}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl border border-[#DDE5F0] bg-white text-xs font-bold text-[#102A4C] hover:bg-[#FAF6EC] shadow-2xs"
            >
              <Printer className="w-4 h-4 text-[#8C6D23]" />
              <span>{language === "ta" ? "அச்சிடுக" : "Print Prescription"}</span>
            </button>
            {onRefresh && (
              <button
                type="button"
                onClick={onRefresh}
                disabled={isLoading}
                className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl border border-purple-200 bg-purple-50 hover:bg-purple-100 text-xs font-bold text-purple-900 shadow-2xs"
              >
                <Sparkles className={`w-4 h-4 text-purple-600 ${isLoading ? "animate-spin" : ""}`} />
                <span>{language === "ta" ? "மறுஆய்வு" : "Refresh"}</span>
              </button>
            )}
          </div>
        </div>

        {/* Chart Context Summary Badges */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 pt-3 border-t border-[#F1F5F9] text-xs">
          <div className="p-2.5 rounded-xl bg-[#FAF7F0] border border-[#E2DCD5]">
            <span className="text-[10px] uppercase font-bold text-[#64748B] block">
              {language === "ta" ? "லக்னம்" : "Ascendant (Lagna)"}
            </span>
            <span className="font-bold text-[#102A4C] text-sm">
              {analysis.chart_context.lagna_sign}
            </span>
            {analysis.chart_context.lagna_lord && (
              <span className="text-[11px] text-[#8C6D23] block">
                Lord: {analysis.chart_context.lagna_lord}
              </span>
            )}
          </div>

          <div className="p-2.5 rounded-xl bg-purple-50/60 border border-purple-200">
            <span className="text-[10px] uppercase font-bold text-purple-900 block">
              {language === "ta" ? "நடப்பு தசா - புக்தி" : "Running Dasa - Bhukti"}
            </span>
            <span className="font-bold text-purple-950 text-sm capitalize">
              {analysis.chart_context.running_mahadasha || "—"} / {analysis.chart_context.running_bhukti || "—"}
            </span>
            {analysis.chart_context.running_pratyantardasha && (
              <span className="text-[11px] text-purple-800 block capitalize">
                Antara: {analysis.chart_context.running_pratyantardasha}
              </span>
            )}
          </div>

          <div className="p-2.5 rounded-xl bg-emerald-50/60 border border-emerald-200">
            <span className="text-[10px] uppercase font-bold text-emerald-900 block">
              {language === "ta" ? "சுப கிரகங்கள்" : "Functional Benefics"}
            </span>
            <div className="flex flex-wrap gap-1 mt-0.5">
              {analysis.chart_context.functional_benefics.map((g) => (
                <span
                  key={g}
                  className="px-1.5 py-0.2 rounded bg-emerald-100 text-emerald-900 font-bold text-[11px] uppercase"
                >
                  {g}
                </span>
              ))}
            </div>
          </div>

          <div className="p-2.5 rounded-xl bg-rose-50/60 border border-rose-200">
            <span className="text-[10px] uppercase font-bold text-rose-900 block">
              {language === "ta" ? "அசுப கிரகங்கள்" : "Functional Malefics"}
            </span>
            <div className="flex flex-wrap gap-1 mt-0.5">
              {analysis.chart_context.functional_malefics.map((g) => (
                <span
                  key={g}
                  className="px-1.5 py-0.2 rounded bg-rose-100 text-rose-900 font-bold text-[11px] uppercase"
                >
                  {g}
                </span>
              ))}
            </div>
          </div>

          <div className="p-2.5 rounded-xl bg-amber-50/60 border border-amber-200">
            <span className="text-[10px] uppercase font-bold text-amber-900 block">
              {language === "ta" ? "பாதிக்கப்பட்ட கிரகங்கள்" : "Afflicted Grahas"}
            </span>
            <div className="flex flex-wrap gap-1 mt-0.5">
              {afflictedGrahas.length > 0 ? (
                afflictedGrahas.map((g) => (
                  <span
                    key={g}
                    className="px-1.5 py-0.2 rounded bg-amber-100 text-amber-900 font-bold text-[11px] uppercase"
                  >
                    {g}
                  </span>
                ))
              ) : (
                <span className="text-[11px] text-amber-800 font-medium">None critical</span>
              )}
            </div>
          </div>

          <div className="p-2.5 rounded-xl bg-blue-50/60 border border-blue-200">
            <span className="text-[10px] uppercase font-bold text-blue-900 block">
              {language === "ta" ? "செவ்வாய் தோஷம்" : "Kuja Dosha"}
            </span>
            <span
              className={`font-bold text-xs inline-block mt-0.5 ${
                kujaStatus === "present"
                  ? "text-rose-700"
                  : kujaStatus === "cancelled"
                  ? "text-amber-700"
                  : "text-emerald-700"
              }`}
            >
              {kujaStatus === "present"
                ? language === "ta"
                  ? "தோஷம் உள்ளது (Active)"
                  : "Active Kuja Dosha"
                : kujaStatus === "cancelled"
                ? language === "ta"
                  ? "தோஷ நிவர்த்தி உண்டு (Cancelled)"
                  : "Present (Cancelled by BPHS Rule)"
                : language === "ta"
                ? "தோஷம் இல்லை (Absent)"
                : "No Kuja Dosha"}
            </span>
          </div>
        </div>
      </div>

      {/* 2. Yogakaraka Protection Alert (BPHS Ch. 34) */}
      {hasYogakarakaWarning && (
        <div className="p-4 sm:p-5 rounded-2xl bg-amber-50 border-2 border-amber-400 text-amber-950 space-y-2.5 shadow-sm">
          <div className="flex items-center gap-2.5">
            <ShieldAlert className="w-6 h-6 text-amber-700 shrink-0" />
            <h3 className="font-serif text-base font-bold text-amber-900">
              {language === "ta"
                ? "யோககாரகன் தான பாதுகாப்பு எச்சரிக்கை (பிருஹத் பராசர ஹோரா சாஸ்திரம் அதிகாரம் 34)"
                : "BPHS Ch. 34 Strict Yogakaraka Daan Protection Safeguard"}
            </h3>
          </div>
          <p className="text-xs sm:text-sm text-amber-900 leading-relaxed">
            {language === "ta"
              ? "உங்கள் லக்னத்திற்கு மிகவும் சுபமான யோககாரக கிரகம் நலிவடைந்தாலோ அல்லது மறைவிடத்தில் இருந்தாலோ அதற்கு தானம் (Daan) செய்வது சாஸ்திரப்படி முற்றிலும் தடைசெய்யப்பட்டுள்ளது. தானம் தருவது யோக பலனை பலவீனப்படுத்திவிடும். இதற்குப் பதிலாக காயத்ரி அல்லது ஸ்தோத்திர ஜபம், நெய் தீபம் ஏற்றுதல் மற்றும் காவிரி டெல்டா ஸ்தலங்களில் அர்ச்சனை செய்தல் போன்ற சாத்வீக வழிபாடுகளே உகந்தவை."
              : "Brihat Parashara Hora Shastra Chapter 34 mandates that for a Yogakaraka planet (such as Saturn for Taurus/Libra, Mars for Cancer/Leo, or Venus for Capricorn/Aquarius), charity (daan) of related items is strictly prohibited. Daan gives away planetary strength, depleting the benefic life force protecting your Kendra-Trikona houses. Only Sattvic Stotras, Gayatri recitation, and Navagraha temple archana are prescribed."}
          </p>
        </div>
      )}

      {/* 3. Diagnosed Chart Factors Grid */}
      <div className="space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <h3 className="font-serif text-lg font-bold text-[#102A4C] flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-purple-600" />
            <span>
              {language === "ta"
                ? "கண்டறியப்பட்ட ஜோதிட நிலைகள் (சாஸ்திர ஆதாரங்களுடன்)"
                : "Diagnosed Astrological Factors (Parashari Shastras)"}
            </span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-purple-100 text-purple-900 font-semibold">
              {filteredFactors.length}
            </span>
          </h3>

          <div className="flex items-center gap-1.5 overflow-x-auto text-xs">
            <button
              type="button"
              onClick={() => setFactorFilter("all")}
              className={`px-2.5 py-1 rounded-lg font-semibold transition-colors ${
                factorFilter === "all" ? "bg-[#102A4C] text-white" : "bg-[#F1F5F9] text-[#52667E] hover:bg-gray-200"
              }`}
            >
              {language === "ta" ? "அனைத்தும்" : "All Factors"}
            </button>
            <button
              type="button"
              onClick={() => setFactorFilter("affliction")}
              className={`px-2.5 py-1 rounded-lg font-semibold transition-colors ${
                factorFilter === "affliction" ? "bg-rose-700 text-white" : "bg-rose-50 text-rose-800 hover:bg-rose-100"
              }`}
            >
              {language === "ta" ? "நீசம் & மறைவிடங்கள்" : "Debilitation & Dusthana"}
            </button>
            <button
              type="button"
              onClick={() => setFactorFilter("kuja")}
              className={`px-2.5 py-1 rounded-lg font-semibold transition-colors ${
                factorFilter === "kuja" ? "bg-amber-700 text-white" : "bg-amber-50 text-amber-800 hover:bg-amber-100"
              }`}
            >
              {language === "ta" ? "செவ்வாய் தோஷம்" : "Kuja Dosha"}
            </button>
            <button
              type="button"
              onClick={() => setFactorFilter("dasa")}
              className={`px-2.5 py-1 rounded-lg font-semibold transition-colors ${
                factorFilter === "dasa" ? "bg-purple-700 text-white" : "bg-purple-50 text-purple-800 hover:bg-purple-100"
              }`}
            >
              {language === "ta" ? "நடப்பு தசா" : "Active Dasa"}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {filteredFactors.map((fac, idx) => (
            <div
              key={idx}
              className={`p-4 rounded-xl border transition-shadow bg-white shadow-xs space-y-2.5 ${
                fac.severity === "high"
                  ? "border-rose-200 hover:border-rose-300"
                  : fac.severity === "moderate"
                  ? "border-amber-200 hover:border-amber-300"
                  : "border-blue-200 hover:border-blue-300"
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <span
                    className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                      fac.severity === "high"
                        ? "bg-rose-100 text-rose-900"
                        : fac.severity === "moderate"
                        ? "bg-amber-100 text-amber-900"
                        : "bg-blue-100 text-blue-900"
                    }`}
                  >
                    {fac.factor_type.replace("_", " ")}
                  </span>
                  <h4 className="font-serif font-bold text-sm text-[#102A4C] mt-1">
                    {language === "ta" ? fac.title_ta : fac.title_en}
                  </h4>
                </div>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80] font-bold shrink-0">
                  {fac.rule_reference}
                </span>
              </div>

              <p className="text-xs text-[#52667E] leading-relaxed">
                {language === "ta" ? fac.description_ta : fac.description_en}
              </p>

              {fac.neecha_bhanga && (
                <div className="mt-2 pt-2 border-t border-slate-100 space-y-1.5 text-[11px]">
                  <div className="flex flex-wrap items-center gap-1.5">
                    {fac.neecha_bhanga.is_d9_exalted && (
                      <span className="px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 font-semibold">
                        {language === "ta" ? "நவாம்ச உட்சம் (D9)" : "D9 Exalted"}
                      </span>
                    )}
                    {fac.neecha_bhanga.is_d9_own_sign && (
                      <span className="px-1.5 py-0.5 rounded bg-teal-100 text-teal-800 font-semibold">
                        {language === "ta" ? "நவாம்ச ஆட்சி (D9)" : "D9 Own Sign"}
                      </span>
                    )}
                    {fac.neecha_bhanga.is_vargottama && (
                      <span className="px-1.5 py-0.5 rounded bg-indigo-100 text-indigo-800 font-semibold">
                        {language === "ta" ? "வர்கோத்தமம்" : "Vargottama"}
                      </span>
                    )}
                    {fac.neecha_bhanga.cancellation_status === "complete_nbry_qualifying" && (
                      <span className="px-1.5 py-0.5 rounded bg-amber-100 text-amber-900 font-bold border border-amber-300">
                        {language === "ta" ? "நீச பங்க ராஜ யோகம்" : "Complete NBRY"}
                      </span>
                    )}
                    {fac.neecha_bhanga.cancellation_status === "nbry_neutralized_by_combustion" && (
                      <span className="px-1.5 py-0.5 rounded bg-rose-100 text-rose-800 font-semibold">
                        {language === "ta" ? "அஸ்தமனத்தால் யோக பங்கம்" : "NBRY Neutralized (Combust)"}
                      </span>
                    )}
                    {fac.neecha_bhanga.d9_data_status === "unavailable" && (
                      <span className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 italic">
                        {language === "ta" ? "D9 தரவு நிலுவை" : "D9 Data Unavailable"}
                      </span>
                    )}
                  </div>
                  {fac.neecha_bhanga.qualifying_criteria.length > 0 && (
                    <ul className="list-disc pl-4 text-slate-600 text-[10px] space-y-0.5">
                      {fac.neecha_bhanga.qualifying_criteria.map((c, i) => (
                        <li key={i}>{c}</li>
                      ))}
                    </ul>
                  )}
                </div>
              )}

              <div className="flex items-center justify-between pt-2 border-t border-[#F8FAFC] text-[11px]">
                <span className="text-[#64748B] capitalize">
                  Graha: <strong className="text-[#102A4C]">{fac.graha}</strong>
                  {fac.house ? ` (H${fac.house})` : ""}
                </span>
                <span className="text-emerald-700 font-semibold flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                  <span>{fac.is_confirmed ? "Calculated" : "Inferred"}</span>
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 4. Curated & Ranked Remedies Section */}
      <div className="space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pt-4 border-t border-[#E2DCD5]">
          <div>
            <h3 className="font-serif text-lg font-bold text-[#102A4C] flex items-center gap-2">
              <Flame className="w-5 h-5 text-amber-600" />
              <span>
                {language === "ta"
                  ? "பரிந்துரைக்கப்பட்ட பரிகாரங்கள் (வரிசைப்படுத்தப்பட்டது)"
                  : "Prescribed Classical Remedies (Ranked)"}
              </span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-900 font-semibold">
                {filteredRecommendations.length}
              </span>
            </h3>
            <p className="text-xs text-[#64748B]">
              {language === "ta"
                ? "உங்கள் ஜாதகத்தில் உள்ள கிரக பலவீனங்களை சமன் செய்ய சாஸ்திர விதிகளின்படி தேர்ந்தெடுக்கப்பட்டவை."
                : "Selected according to classical priority rules, prioritizing running Dasa and severe afflictions."}
            </p>
          </div>

          {/* Bulk Selection Actions */}
          <div className="flex items-center gap-2 text-xs">
            <button
              type="button"
              onClick={selectAllRemedies}
              className="px-2.5 py-1 rounded-lg border border-[#DDE5F0] bg-white text-[#102A4C] hover:bg-[#FAF6EC] font-semibold"
            >
              {language === "ta" ? "அனைத்தையும் தேர்ந்தெடு" : "Select All"}
            </button>
            <button
              type="button"
              onClick={deselectAllRemedies}
              className="px-2.5 py-1 rounded-lg border border-[#DDE5F0] bg-white text-[#64748B] hover:bg-[#FAF6EC] font-semibold"
            >
              {language === "ta" ? "நீக்கு" : "Clear All"}
            </button>
          </div>
        </div>

        {/* Filters and Search Bar */}
        <div className="flex flex-col sm:flex-row items-center gap-2 bg-[#FAF7F0] p-3 rounded-2xl border border-[#E2DCD5]">
          <div className="relative flex-1 w-full sm:w-auto">
            <Search className="w-4 h-4 text-[#64748B] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={
                language === "ta"
                  ? "மந்திரம், கிரகம் அல்லது பரிகாரத்தைத் தேடுங்கள்..."
                  : "Search mantra, deity, or planet..."
              }
              className="w-full pl-9 pr-3 py-1.5 rounded-xl border border-[#DDE5F0] bg-white text-xs text-[#102A4C] focus:outline-hidden focus:border-[#B8862B]"
            />
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto overflow-x-auto">
            <select
              value={remedyTypeFilter}
              onChange={(e) => setRemedyTypeFilter(e.target.value)}
              className="px-3 py-1.5 rounded-xl border border-[#DDE5F0] bg-white text-xs font-semibold text-[#102A4C]"
            >
              <option value="all">{language === "ta" ? "அனைத்து வகைகள்" : "All Types"}</option>
              <option value="mantra">{language === "ta" ? "மந்திரம்" : "Mantra"}</option>
              <option value="worship">{language === "ta" ? "வழிபாடு" : "Worship"}</option>
              <option value="charity">{language === "ta" ? "தானம் (Daan)" : "Charity"}</option>
              <option value="temple">{language === "ta" ? "கோவில் யாத்திரை" : "Temple Visit"}</option>
            </select>

            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="px-3 py-1.5 rounded-xl border border-[#DDE5F0] bg-white text-xs font-semibold text-[#102A4C]"
            >
              <option value="all">{language === "ta" ? "அனைத்து முன்னுரிமை" : "All Priorities"}</option>
              <option value="essential">{language === "ta" ? "முக்கியமானது (Essential)" : "Essential"}</option>
              <option value="recommended">{language === "ta" ? "பரிந்துரை (Recommended)" : "Recommended"}</option>
              <option value="optional">{language === "ta" ? "விருப்பம் (Optional)" : "Optional"}</option>
            </select>
          </div>
        </div>

        {/* Remedies Cards List */}
        <div className="space-y-4">
          {filteredRecommendations.map((rec) => {
            const isSelected = selectedRemedyCodes.has(rec.remedy.code);

            return (
              <div
                key={rec.remedy.code}
                className={`rounded-2xl border transition-all p-5 bg-white shadow-xs space-y-4 ${
                  isSelected
                    ? "border-purple-300 ring-2 ring-purple-100"
                    : "border-[#E2DCD5] opacity-80 hover:opacity-100"
                }`}
              >
                {/* Top Row: Checkbox, Name, Score, Priority */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <button
                      type="button"
                      onClick={() => toggleRemedySelection(rec.remedy.code)}
                      className={`w-5 h-5 rounded-md mt-0.5 flex items-center justify-center transition-colors cursor-pointer shrink-0 ${
                        isSelected
                          ? "bg-purple-600 text-white"
                          : "border border-gray-300 hover:border-purple-500 bg-white"
                      }`}
                    >
                      {isSelected && <Check className="w-3.5 h-3.5" />}
                    </button>

                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-bold text-xs uppercase px-2 py-0.5 rounded bg-[#FAF2DE] text-[#8C6D23]">
                          {rec.remedy.graha} • {rec.remedy.remedy_type}
                        </span>

                        <span
                          className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
                            rec.priority_tier === "essential"
                              ? "bg-rose-100 text-rose-900"
                              : rec.priority_tier === "recommended"
                              ? "bg-amber-100 text-amber-900"
                              : "bg-blue-100 text-blue-900"
                          }`}
                        >
                          {rec.priority_tier.toUpperCase()}
                        </span>

                        <span className="text-[11px] font-mono text-[#64748B]">
                          Relevance: {rec.relevance_score}/100
                        </span>
                      </div>

                      <h4 className="font-serif font-bold text-base sm:text-lg text-[#102A4C] mt-1">
                        {language === "ta" ? rec.remedy.name_ta : rec.remedy.name_en}
                      </h4>
                    </div>
                  </div>

                  {/* Matching Factors Pills */}
                  <div className="flex flex-wrap items-center gap-1.5 sm:justify-end">
                    {rec.matching_factors.map((mf, i) => (
                      <span
                        key={i}
                        className="px-2 py-0.5 rounded-full bg-purple-50 text-purple-900 text-[10px] font-semibold border border-purple-200"
                      >
                        {mf}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Reason */}
                <div className="p-3 rounded-xl bg-[#FAF8F5] border border-[#F1EBE4] text-xs text-[#475569]">
                  <strong className="text-[#102A4C]">
                    {language === "ta" ? "காரணம்: " : "Astrological Reason: "}
                  </strong>
                  <span>{language === "ta" ? rec.reason_ta : rec.reason_en}</span>
                </div>

                {/* Sanskrit Mantra Display (if applicable) */}
                {rec.remedy.sanskrit_text && (
                  <div className="p-4 rounded-xl bg-gradient-to-r from-amber-50/70 to-orange-50/50 border border-amber-200 space-y-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-amber-800 block">
                      {language === "ta" ? "மூல மந்திரம் (தேவநாகரி / தமிழ்)" : "Vedic Root Mantra (Devanagari)"}
                    </span>
                    <p className="font-serif text-base sm:text-lg font-bold text-[#784E0E] leading-relaxed">
                      {rec.remedy.sanskrit_text}
                    </p>
                    {rec.remedy.transliteration_ta && (
                      <p className="text-xs font-semibold text-amber-950 font-serif">
                        {rec.remedy.transliteration_ta}
                      </p>
                    )}
                    {rec.remedy.transliteration_iast && (
                      <p className="text-xs font-mono text-[#64748B]">
                        IAST: {rec.remedy.transliteration_iast}
                      </p>
                    )}
                    {(rec.remedy.meaning_en || rec.remedy.meaning_ta) && (
                      <p className="text-xs text-[#52667E] pt-2 border-t border-amber-200/60">
                        <strong>Meaning: </strong>
                        {language === "ta" ? rec.remedy.meaning_ta : rec.remedy.meaning_en}
                      </p>
                    )}
                  </div>
                )}

                {/* Procedure, Japa Count, Timing */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs pt-1">
                  <div className="p-2.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                    <span className="text-[10px] uppercase font-bold text-[#64748B] block">
                      {language === "ta" ? "வழிமுறை" : "Procedure"}
                    </span>
                    <span className="text-[#334155] leading-relaxed mt-0.5 block">
                      {language === "ta" ? rec.remedy.procedure_ta : rec.remedy.procedure_en}
                    </span>
                  </div>

                  <div className="p-2.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                    <span className="text-[10px] uppercase font-bold text-[#64748B] block">
                      {language === "ta" ? "ஜப எண்ணிக்கை" : "Japa Count"}
                    </span>
                    <span className="font-bold text-[#102A4C] text-sm mt-0.5 block">
                      {rec.remedy.japa_count ? `${rec.remedy.japa_count} times` : "As prescribed"}
                    </span>
                  </div>

                  <div className="p-2.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                    <span className="text-[10px] uppercase font-bold text-[#64748B] block">
                      {language === "ta" ? "உகந்த நேரம்" : "Timing & Day"}
                    </span>
                    <span className="text-[#334155] mt-0.5 block">
                      {language === "ta"
                        ? rec.remedy.timing_recommendation_ta || "காலை நேரத்தில்"
                        : rec.remedy.timing_recommendation_en || "During Brahma Muhurta / Morning"}
                    </span>
                  </div>
                </div>

                {/* Associated Kaveri Delta Temple (if present) */}
                {rec.temple && (
                  <div className="p-3.5 rounded-xl bg-emerald-50/50 border border-emerald-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                    <div className="flex items-start gap-2.5">
                      <MapPin className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
                      <div>
                        <span className="text-[10px] font-bold text-emerald-800 uppercase block">
                          {language === "ta" ? "பரிந்துரைக்கப்பட்ட ஸ்தலம்" : "Recommended Navagraha Temple"}
                        </span>
                        <h5 className="font-serif font-bold text-sm text-emerald-950">
                          {language === "ta" ? rec.temple.name_ta : rec.temple.name_en}
                        </h5>
                        <p className="text-[11px] text-emerald-800">
                          {rec.temple.place_name_en}, {rec.temple.district_en} • Visiting Day: {rec.temple.visiting_day_en}
                        </p>
                      </div>
                    </div>

                    <div className="text-[11px] text-emerald-900 bg-white p-2 rounded-lg border border-emerald-200 shrink-0">
                      <strong>Offerings: </strong>
                      <span>
                        {language === "ta" ? rec.temple.remedy_offerings_ta : rec.temple.remedy_offerings_en}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* 5. Astrologer Report Review & Persistence Card */}
      <div className="rounded-2xl border border-purple-200 bg-gradient-to-b from-purple-50/40 to-white p-6 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <UserCheck className="w-6 h-6 text-purple-700" />
            <div>
              <h3 className="font-serif text-lg font-bold text-[#102A4C]">
                {language === "ta"
                  ? "ஜோதிடர் ஆய்வு & பரிகார அறிக்கை சேமிப்பு"
                  : "Astrologer Review & Report Persistence"}
              </h3>
              <p className="text-xs text-[#52667E]">
                {language === "ta"
                  ? "வாடிக்கையாளருக்கு வழங்குவதற்கு முன் குறிப்புகளையும் ஆய்வு நிலையையும் பதிவு செய்யவும்."
                  : "Attach astrologer clinical notes and save the official remedy prescription to Supabase."}
              </p>
            </div>
          </div>

          {savedReports.length > 0 && (
            <button
              type="button"
              onClick={() => setShowHistory(!showHistory)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-purple-300 bg-white text-xs font-semibold text-purple-900 hover:bg-purple-50"
            >
              <FileText className="w-3.5 h-3.5 text-purple-600" />
              <span>
                {language === "ta"
                  ? `முந்தைய அறிக்கைகள் (${savedReports.length})`
                  : `Previous Reports (${savedReports.length})`}
              </span>
              {showHistory ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          )}
        </div>

        {/* History Accordion */}
        {showHistory && savedReports.length > 0 && (
          <div className="p-4 rounded-xl bg-white border border-purple-200 space-y-3">
            <h4 className="text-xs font-bold text-[#102A4C] uppercase tracking-wider">
              {language === "ta" ? "சேமிக்கப்பட்ட அறிக்கைகள்" : "Saved Remedy Reports History"}
            </h4>
            <div className="divide-y divide-gray-100 text-xs">
              {savedReports.map((rpt) => (
                <div key={rpt.id} className="py-2.5 flex items-center justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                          rpt.review_status === "approved"
                            ? "bg-emerald-100 text-emerald-900"
                            : rpt.review_status === "reviewed"
                            ? "bg-blue-100 text-blue-900"
                            : "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {rpt.review_status}
                      </span>
                      <span className="font-bold text-[#102A4C]">{rpt.person_name}</span>
                      <span className="text-[#64748B] text-[11px]">
                        ({new Date(rpt.created_at).toLocaleDateString()})
                      </span>
                    </div>
                    {rpt.astrologer_notes && (
                      <p className="text-[#52667E] text-[11px] mt-1 line-clamp-1">
                        Notes: {rpt.astrologer_notes}
                      </p>
                    )}
                  </div>
                  <span className="text-[11px] font-semibold text-purple-700 shrink-0">
                    {rpt.selected_remedy_codes.length} remedies
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Status Messages */}
        {saveSuccessMessage && (
          <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span className="font-bold">{saveSuccessMessage}</span>
          </div>
        )}
        {saveErrorMessage && (
          <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-900 text-xs flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
            <span className="font-bold">{saveErrorMessage}</span>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold text-[#102A4C] mb-1">
              {language === "ta" ? "ஆய்வு நிலை (Review Status)" : "Review Status"}
            </label>
            <select
              value={reviewStatus}
              onChange={(e) => setReviewStatus(e.target.value as any)}
              className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] bg-white text-xs font-semibold text-[#102A4C] focus:outline-hidden focus:border-purple-600"
            >
              <option value="draft">Draft (வரைவு - ஆய்வுக்கு உட்பட்டது)</option>
              <option value="reviewed">Reviewed (ஜோதிடரால் பரிசீலிக்கப்பட்டது)</option>
              <option value="approved">Approved (வாடிக்கையாளருக்கு வழங்க அங்கீகரிக்கப்பட்டது)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-[#102A4C] mb-1">
              {language === "ta" ? "அறிக்கை மொழி (Report Language)" : "Report Language"}
            </label>
            <select
              value={reportLanguage}
              onChange={(e) => setReportLanguage(e.target.value as any)}
              className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] bg-white text-xs font-semibold text-[#102A4C] focus:outline-hidden focus:border-purple-600"
            >
              <option value="en">English (Classical Shastra Reference)</option>
              <option value="ta">தமிழ் (பாரம்பரிய பரிகார முறை)</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-xs font-bold text-[#102A4C] mb-1">
            {language === "ta"
              ? "ஜோதிடர் குறிப்புகள் & அறிவுரைகள் (Astrologer Clinical Notes)"
              : "Astrologer Clinical Notes & Client Instructions"}
          </label>
          <textarea
            rows={3}
            value={astrologerNotes}
            onChange={(e) => setAstrologerNotes(e.target.value)}
            placeholder={
              language === "ta"
                ? "வாடிக்கையாளருக்கான தனிப்பட்ட ஆலோசனைகள், ஜப முறைகள் அல்லது ஸ்தல யாத்திரை வழிகாட்டல்கள்..."
                : "Enter special guidance, observances, temple sequence, or precautions for the client..."
            }
            className="w-full p-3 rounded-xl border border-[#DDE5F0] bg-white text-xs text-[#102A4C] focus:outline-hidden focus:border-purple-600"
          />
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
          <span className="text-xs text-[#64748B]">
            Selected <strong>{selectedRemedyCodes.size}</strong> of {analysis.recommendations.length} remedies
          </span>

          <button
            type="button"
            onClick={handleSaveReport}
            disabled={isSaving}
            className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-purple-700 hover:bg-purple-800 text-white text-xs font-bold transition-colors shadow-sm cursor-pointer disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            <span>
              {isSaving
                ? language === "ta"
                  ? "சேமிக்கப்படுகிறது..."
                  : "Saving Report..."
                : language === "ta"
                ? "பரிகார அறிக்கையை சேமி"
                : "Save Astrologer Report"}
            </span>
          </button>
        </div>
      </div>

      {/* 6. Classical Disclaimer Banner */}
      <div className="p-4 rounded-xl bg-[#FAF7F0] border border-[#E2DCD5] text-xs text-[#52667E] leading-relaxed">
        <strong className="text-[#102A4C] block mb-1">
          {language === "ta" ? "சாஸ்திர மறுப்புரை (Classical Disclaimer)" : "Classical Shastric Disclaimer"}
        </strong>
        <span>
          {language === "ta" ? analysis.classical_disclaimer_ta : analysis.classical_disclaimer_en}
        </span>
      </div>
    </div>
  );
}
