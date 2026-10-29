"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import {
  calculateAdvancedAnalysis,
  saveNumerologyReport,
  downloadNumerologyReportPdf,
  exportNumerologyPdf,
} from "@/lib/api";
import {
  AdvancedAnalysisResponse,
  SavedNumerologyReportResponse,
} from "@/lib/types";
import { LoShuGrid } from "@/components/numerology/LoShuGrid";
import { NumerologyReportView } from "@/components/numerology/NumerologyReportView";
import {
  Grid3X3,
  Calendar,
  User,
  Sparkles,
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  RotateCcw,
  Zap,
  Clock,
  Layers,
} from "lucide-react";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";

export default function AdvancedAnalysisPage() {
  const { language } = useLanguage();
  const { session, isAuthenticated } = useAuth();

  // Form states
  const [fullName, setFullName] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [reportLang, setReportLang] = useState<"en" | "ta">(language);

  // Execution states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AdvancedAnalysisResponse | null>(null);
  const [savedRecord, setSavedRecord] = useState<SavedNumerologyReportResponse | null>(null);
  const [pdfDownloading, setPdfDownloading] = useState(false);
  const [pdfError, setPdfError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim()) {
      setError("Please enter your full name.");
      return;
    }
    if (!birthDate.trim()) {
      setError("Please select a valid birth date.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setSavedRecord(null);

    try {
      const token = session?.access_token;
      const res = await calculateAdvancedAnalysis(
        {
          full_name: fullName.trim(),
          birth_date: birthDate.trim(),
          language: reportLang,
        },
        token
      );
      setResult(res);

      // Auto-save for authenticated users
      if (isAuthenticated && token) {
        try {
          const saved = await saveNumerologyReport(
            {
              person_name: res.full_name,
              birth_date: res.birth_date,
              method: "advanced",
              system_convention: "yuan_lo_shu_pinnacles",
              calculation_data: {
                unicode_derived_name_number: res.unicode_derived_name_number,
                lo_shu: res.lo_shu,
                pinnacles_challenges: res.pinnacles_challenges,
                karmic_debts: res.karmic_debts,
                karmic_lessons: res.karmic_lessons,
                dominant_vibrations: res.dominant_vibrations,
              },
              interpretation_data: {
                strengths: res.strengths,
                challenges: res.challenges,
                career_tendencies: res.career_tendencies,
                financial_tendencies: res.financial_tendencies,
                love_themes: res.love_themes,
                overall_synthesis: res.overall_synthesis,
              },
            },
            token
          );
          setSavedRecord(saved);
        } catch (saveErr) {
          console.warn("Auto-save failed:", saveErr);
        }
      }
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || "Failed to calculate Advanced Analysis.");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setSavedRecord(null);
    setError(null);
    setPdfError(null);
  };

  const handleDownloadPdf = async (lang: "en" | "ta" = "en") => {
    if (!result) return;
    setPdfDownloading(true);
    setPdfError(null);
    try {
      let blob: Blob;
      if (savedRecord?.id && session?.access_token) {
        blob = await downloadNumerologyReportPdf(savedRecord.id, lang, session.access_token);
      } else {
        blob = await exportNumerologyPdf(
          {
            person_name: result.full_name || "Advanced Subject",
            birth_date: result.birth_date,
            method: "advanced",
            system_convention: "lo_shu_grid",
            language: lang,
            calculation_data: result as any,
            interpretation_data: {
              overall_synthesis: "Advanced Yuan and Lo Shu numerology reading completed successfully.",
            },
            display_number: savedRecord?.display_number,
          },
          session?.access_token
        );
      }
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const safeName = (result.full_name || "Subject").replace(/\s+/g, "_");
      a.download = `Advanced_LoShu_${safeName}_${lang}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setPdfError(err?.message || "Failed to download Advanced Numerology PDF report.");
    } finally {
      setPdfDownloading(false);
    }
  };

  return (
    <div className="w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 sm:py-8 space-y-8">
      {/* Navigation Breadcrumbs & Back Link */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <Breadcrumbs
          items={[
            {
              label: language === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools",
              href: "/tools",
            },
            {
              label: language === "ta" ? "எண் கணிதம்" : "Numerology",
              href: "/tools/numerology",
            },
            {
              label: language === "ta" ? "மேம்பட்ட பகுப்பாய்வு (Yuan)" : "Advanced Analysis",
            },
          ]}
        />

        <Link
          href="/tools/numerology"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#52667E] hover:text-[#102A4C] transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>
            {language === "ta" ? "எண் கணித அடைவு" : "Back to Numerology"}
          </span>
        </Link>
      </div>

      {!result ? (
        /* Form Card */
        <div className="max-w-2xl mx-auto rounded-2xl border border-[#E2DCD5] bg-white p-6 sm:p-8 shadow-xs">
          <div className="text-center pb-6 border-b border-[#E2DCD5]">
            <div className="w-12 h-12 mx-auto rounded-2xl bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center text-[#B8860B] mb-3 shadow-2xs">
              <Grid3X3 className="w-6 h-6" />
            </div>
            <h1 className="font-serif text-2xl font-bold text-[#0F172A]">
              Advanced Analysis (Yuan Framework &amp; Lo Shu)
            </h1>
            <p className="mt-1 text-xs text-[#64748B]">
              Multi-dimensional synthesis combining 3x3 Lo Shu magic square, 8 Arrows of Pythagoras, Life Pinnacles, Challenges, and Karmic Debts.
            </p>
          </div>

          {error && (
            <div className="mt-6 p-4 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-800 flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 text-rose-600 mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="mt-6 space-y-5">
            {/* Full Name */}
            <div>
              <label className="block text-xs font-semibold text-[#334155] mb-1.5">
                Full Name (Universal Script Support) <span className="text-rose-500">*</span>
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-[#94A3B8] absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g., Sundar Raman / 张伟 / கோகுல்"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-[#CBD5E1] bg-[#FAF8F5] text-xs text-[#0F172A] placeholder-[#94A3B8] focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-[#B8860B]/20 focus:border-[#B8860B]"
                />
              </div>
              <p className="mt-1 text-[11px] text-[#64748B]">
                Supports Latin, Tamil, Chinese, and Unicode scripts via deterministic code-point reduction.
              </p>
            </div>

            {/* Date of Birth */}
            <div>
              <label className="block text-xs font-semibold text-[#334155] mb-1.5">
                Date of Birth <span className="text-rose-500">*</span>
              </label>
              <div className="relative">
                <Calendar className="w-4 h-4 text-[#94A3B8] absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="date"
                  required
                  value={birthDate}
                  onChange={(e) => setBirthDate(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-[#CBD5E1] bg-[#FAF8F5] text-xs text-[#0F172A] focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-[#B8860B]/20 focus:border-[#B8860B]"
                />
              </div>
            </div>

            {/* Language */}
            <div>
              <label className="block text-xs font-semibold text-[#334155] mb-1.5">
                Report Language
              </label>
              <select
                value={reportLang}
                onChange={(e) => setReportLang(e.target.value as any)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-[#CBD5E1] bg-[#FAF8F5] text-xs text-[#0F172A] focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-[#B8860B]/20 focus:border-[#B8860B]"
              >
                <option value="en">English</option>
                <option value="ta">தமிழ் (Tamil)</option>
              </select>
            </div>

            <div className="pt-3">
              <button
                type="submit"
                disabled={loading}
                className="w-full inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl text-xs font-bold text-white bg-[#0F172A] hover:bg-[#1E293B] shadow-xs transition-colors cursor-pointer disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Processing Multi-Dimensional Synthesis...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-[#D8BD80]" />
                    <span>Run Advanced Analysis</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      ) : (
        /* Results View */
        <div className="space-y-6">
          {savedRecord && (
            <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-900 flex items-center justify-between shadow-2xs">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>
                  <strong>Report Auto-Saved:</strong> Recorded as{" "}
                  <strong className="underline">Report #{savedRecord.display_number}</strong>{" "}
                  under your account.
                </span>
              </div>
              <span className="text-[10px] font-mono text-emerald-700">
                ID: {savedRecord.id.slice(0, 8)}...
              </span>
            </div>
          )}

          <div className="flex justify-end print:hidden">
            <button
              type="button"
              onClick={handleReset}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-[#CBD5E1] bg-white hover:bg-[#FAF8F5] text-xs font-semibold text-[#0F172A] shadow-2xs transition-colors cursor-pointer"
            >
              <RotateCcw className="w-3.5 h-3.5 text-[#64748B]" />
              <span>Calculate Another Profile</span>
            </button>
          </div>

          {/* Lo Shu Grid component */}
          <LoShuGrid loShu={result.lo_shu} />

          {/* Karmic Debts Warning if any detected */}
          {result.karmic_debts.length > 0 && (
            <div className="p-5 rounded-2xl border border-amber-200 bg-amber-50/60 shadow-xs space-y-3">
              <div className="flex items-center gap-2 font-serif text-base font-bold text-amber-950 pb-2 border-b border-amber-200">
                <Zap className="w-5 h-5 text-amber-600" />
                <span>Karmic Debt Vibrations Detected</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {result.karmic_debts.map((kd, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-xl bg-white border border-amber-200/80 text-xs space-y-1 shadow-2xs"
                  >
                    <div className="font-bold text-amber-900">
                      {kd.title} ({kd.origin})
                    </div>
                    <p className="text-[#475569] leading-relaxed">
                      {kd.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {pdfError && (
            <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{pdfError}</span>
            </div>
          )}

          {/* Full Report View */}
          <NumerologyReportView
            title={`Advanced Numerology Analysis for ${result.full_name}`}
            methodName="Advanced Analysis (Yuan & Lo Shu)"
            systemConvention="Unicode Code-Point & 3x3 Magic Square"
            personName={result.full_name}
            birthDate={result.birth_date}
            displayNumber={savedRecord?.display_number}
            engineVersion={result.engine_version}
            reportId={savedRecord?.id}
            onDownloadPdf={handleDownloadPdf}
            isDownloadingPdf={pdfDownloading}
            coreSummaryCards={[
              {
                title: "Unicode Vibration Number",
                value: result.unicode_derived_name_number,
                subtitle: "Universal Multi-Script Name Root",
                isMaster: result.unicode_derived_name_number in [11, 22, 33],
              },
              {
                title: "Dominant Frequencies",
                value: result.dominant_vibrations.join(", ") || "None",
                subtitle: "Most repeated name energies",
              },
              {
                title: "Karmic Lessons",
                value: result.karmic_lessons.length,
                subtitle: `Missing: ${result.karmic_lessons.join(", ") || "None"}`,
              },
              {
                title: "Active Strength Arrows",
                value: result.lo_shu.arrows_of_strength.length,
                subtitle: "Pythagorean arrows present",
              },
            ]}
            detailedCalculations={[
              {
                name: "Unicode Code-Point Derivation",
                value: result.unicode_derived_name_number,
                method: "Sum of decimal unicode points reduced via Yuan algorithm",
                interpretation: "Establishes language-agnostic vibrational continuity across multi-script naming conventions.",
              },
              ...result.pinnacles_challenges.pinnacles.map((pin) => ({
                name: `Pinnacle ${pin.pinnacle_number} (${pin.age_span})`,
                value: pin.value,
                method: `Major life peak transition for ${pin.age_span}`,
                interpretation: pin.theme,
              })),
              ...result.pinnacles_challenges.challenges.map((chal) => ({
                name: `Challenge ${chal.challenge_number} (${chal.age_span})`,
                value: chal.value,
                method: `Life lesson constraint for ${chal.age_span}`,
                interpretation: chal.theme,
              })),
            ]}
            cyclesOrForecast={result.pinnacles_challenges.pinnacles.map((pin) => ({
              label: `Pinnacle ${pin.pinnacle_number}`,
              value: `${pin.value} (${pin.age_span})`,
              description: pin.theme,
            }))}
            strengths={result.strengths}
            challenges={result.challenges}
            careerTendencies={result.career_tendencies}
            financialTendencies={result.financial_tendencies}
            loveThemes={result.love_themes}
            overallSynthesis={result.overall_synthesis}
          />
        </div>
      )}
    </div>
  );
}
