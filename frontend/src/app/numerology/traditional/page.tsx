"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import {
  calculateTraditionalNumerology,
  saveNumerologyReport,
  downloadNumerologyReportPdf,
  exportNumerologyPdf,
} from "@/lib/api";
import {
  TraditionalNumerologyResponse,
  SavedNumerologyReportResponse,
} from "@/lib/types";
import { NumerologyReportView } from "@/components/numerology/NumerologyReportView";
import {
  Compass,
  Calendar,
  User,
  Sparkles,
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  RotateCcw,
} from "lucide-react";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";

export default function TraditionalNumerologyPage() {
  const { language, t } = useLanguage();
  const { session, isAuthenticated } = useAuth();

  // Form states
  const [fullName, setFullName] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [systemConvention, setSystemConvention] = useState<"pythagorean" | "chaldean">("pythagorean");
  const [reportLang, setReportLang] = useState<"en" | "ta">(language);

  // Execution states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TraditionalNumerologyResponse | null>(null);
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
      const res = await calculateTraditionalNumerology(
        {
          full_name: fullName.trim(),
          birth_date: birthDate.trim(),
          system_convention: systemConvention,
          language: reportLang,
        },
        token
      );
      setResult(res);

      // Automatic report saving for authenticated users
      if (isAuthenticated && token) {
        try {
          const saved = await saveNumerologyReport(
            {
              person_name: res.person_name,
              birth_date: res.birth_date,
              method: "traditional",
              system_convention: res.system_convention,
              calculation_data: {
                birth_psychic_number: res.birth_psychic_number,
                life_path: res.life_path,
                expression_destiny: res.expression_destiny,
                soul_urge: res.soul_urge,
                personality: res.personality,
                birthday_number: res.birthday_number,
                attitude_number: res.attitude_number,
                maturity_number: res.maturity_number,
                personal_year: res.personal_year,
                karmic_debts: res.karmic_debts,
                calculation_breakdown: res.calculation_breakdown,
                karmic_lessons: res.karmic_lessons,
                hidden_passion: res.hidden_passion,
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
      setError(err?.data?.detail || err?.message || "Failed to calculate numerology.");
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
            person_name: result.person_name,
            birth_date: result.birth_date,
            method: "traditional",
            system_convention: result.system_convention,
            language: lang,
            calculation_data: result as any,
            interpretation_data: {
              strengths: result.strengths,
              challenges: result.challenges,
              career_tendencies: result.career_tendencies,
              financial_tendencies: result.financial_tendencies,
              love_themes: result.love_themes,
              overall_synthesis: result.overall_synthesis,
            },
            display_number: savedRecord?.display_number,
          },
          session?.access_token
        );
      }
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const safeName = (result.person_name || "Traditional").replace(/\s+/g, "_");
      a.download = `Numerology_Traditional_${safeName}_${lang}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setPdfError(err?.message || "Failed to download PDF report.");
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
              label: language === "ta" ? "பாரம்பரிய எண் கணிதம்" : "Traditional Numerology",
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
        /* Input Form Screen */
        <div className="max-w-2xl mx-auto rounded-2xl border border-[#E2DCD5] bg-white p-6 sm:p-8 shadow-xs">
          <div className="text-center pb-6 border-b border-[#E2DCD5]">
            <div className="w-12 h-12 mx-auto rounded-2xl bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center text-[#B8860B] mb-3 shadow-2xs">
              <Compass className="w-6 h-6" />
            </div>
            <h1 className="font-serif text-2xl font-bold text-[#0F172A]">
              Traditional Numerology Reading
            </h1>
            <p className="mt-1 text-xs text-[#64748B]">
              Calculates Life Path, Expression, Soul Urge, and Personality numbers with strict Master Number preservation.
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
                Full Name (as given at birth or commonly used) <span className="text-rose-500">*</span>
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-[#94A3B8] absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g., Sundar Raman"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-[#CBD5E1] bg-[#FAF8F5] text-xs text-[#0F172A] placeholder-[#94A3B8] focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-[#B8860B]/20 focus:border-[#B8860B]"
                />
              </div>
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

            {/* Calculation Convention */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-[#334155] mb-1.5">
                  Calculation System
                </label>
                <select
                  value={systemConvention}
                  onChange={(e) => setSystemConvention(e.target.value as any)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-[#CBD5E1] bg-[#FAF8F5] text-xs text-[#0F172A] focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-[#B8860B]/20 focus:border-[#B8860B]"
                >
                  <option value="pythagorean">Pythagorean (Western Standard 1-9)</option>
                  <option value="chaldean">Chaldean (Ancient Esoteric 1-8)</option>
                </select>
              </div>

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
                    <span>Calculating Core Vibrations...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-[#D8BD80]" />
                    <span>Calculate Traditional Numerology</span>
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
              <span>Calculate Another Person</span>
            </button>
          </div>

          {pdfError && (
            <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{pdfError}</span>
            </div>
          )}

          <NumerologyReportView
            title={`Traditional Numerology Reading for ${result.person_name}`}
            methodName="Traditional Numerology"
            systemConvention={result.system_convention}
            personName={result.person_name}
            birthDate={result.birth_date}
            displayNumber={savedRecord?.display_number}
            engineVersion={result.engine_version}
            reportId={savedRecord?.id}
            onDownloadPdf={handleDownloadPdf}
            isDownloadingPdf={pdfDownloading}
            coreSummaryCards={[
              ...(result.birth_psychic_number
                ? [
                    {
                      title: "Birth / Psychic (Mulank)",
                      value: result.birth_psychic_number.number_value,
                      subtitle: result.birth_psychic_number.short_interpretation,
                      isMaster: result.birth_psychic_number.is_master,
                    },
                  ]
                : []),
              {
                title: "Life Path",
                value: result.life_path.number_value,
                subtitle: result.life_path.short_interpretation,
                isMaster: result.life_path.is_master,
              },
              {
                title: "Expression / Destiny",
                value: result.expression_destiny.number_value,
                subtitle: result.expression_destiny.short_interpretation,
                isMaster: result.expression_destiny.is_master,
              },
              {
                title: "Soul Urge",
                value: result.soul_urge.number_value,
                subtitle: result.soul_urge.short_interpretation,
                isMaster: result.soul_urge.is_master,
              },
              {
                title: "Personality",
                value: result.personality.number_value,
                subtitle: result.personality.short_interpretation,
                isMaster: result.personality.is_master,
              },
              {
                title: "Birthday Number",
                value: result.birthday_number.number_value,
                subtitle: result.birthday_number.short_interpretation,
                isMaster: result.birthday_number.is_master,
              },
              {
                title: "Attitude Number",
                value: result.attitude_number.number_value,
                subtitle: result.attitude_number.short_interpretation,
                isMaster: result.attitude_number.is_master,
              },
              {
                title: "Maturity Number",
                value: result.maturity_number.number_value,
                subtitle: result.maturity_number.short_interpretation,
                isMaster: result.maturity_number.is_master,
              },
              {
                title: "Personal Year (2026)",
                value: result.personal_year.number_value,
                subtitle: result.personal_year.short_interpretation,
                isMaster: result.personal_year.is_master,
              },
            ]}
            detailedCalculations={[
              ...(result.birth_psychic_number
                ? [
                    {
                      name: result.birth_psychic_number.number_name,
                      value: result.birth_psychic_number.number_value,
                      method: result.birth_psychic_number.calculation_method,
                      interpretation: result.birth_psychic_number.detailed_interpretation,
                      attributes: result.birth_psychic_number.key_attributes,
                    },
                  ]
                : []),
              {
                name: result.life_path.number_name,
                value: result.life_path.number_value,
                method: result.life_path.calculation_method,
                interpretation: result.life_path.detailed_interpretation,
                attributes: result.life_path.key_attributes,
              },
              {
                name: result.expression_destiny.number_name,
                value: result.expression_destiny.number_value,
                method: result.expression_destiny.calculation_method,
                interpretation: result.expression_destiny.detailed_interpretation,
                attributes: result.expression_destiny.key_attributes,
              },
              {
                name: result.soul_urge.number_name,
                value: result.soul_urge.number_value,
                method: result.soul_urge.calculation_method,
                interpretation: result.soul_urge.detailed_interpretation,
                attributes: result.soul_urge.key_attributes,
              },
              {
                name: result.personality.number_name,
                value: result.personality.number_value,
                method: result.personality.calculation_method,
                interpretation: result.personality.detailed_interpretation,
                attributes: result.personality.key_attributes,
              },
              {
                name: result.birthday_number.number_name,
                value: result.birthday_number.number_value,
                method: result.birthday_number.calculation_method,
                interpretation: result.birthday_number.detailed_interpretation,
                attributes: result.birthday_number.key_attributes,
              },
              {
                name: result.attitude_number.number_name,
                value: result.attitude_number.number_value,
                method: result.attitude_number.calculation_method,
                interpretation: result.attitude_number.detailed_interpretation,
                attributes: result.attitude_number.key_attributes,
              },
              {
                name: result.maturity_number.number_name,
                value: result.maturity_number.number_value,
                method: result.maturity_number.calculation_method,
                interpretation: result.maturity_number.detailed_interpretation,
                attributes: result.maturity_number.key_attributes,
              },
              {
                name: result.personal_year.number_name,
                value: result.personal_year.number_value,
                method: result.personal_year.calculation_method,
                interpretation: result.personal_year.detailed_interpretation,
                attributes: result.personal_year.key_attributes,
              },
            ]}
            karmicDebts={result.karmic_debts}
            calculationBreakdown={result.calculation_breakdown}
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
