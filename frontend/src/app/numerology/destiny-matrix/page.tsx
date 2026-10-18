"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { calculateDestinyMatrix, saveNumerologyReport } from "@/lib/api";
import {
  DestinyMatrixResponse,
  SavedNumerologyReportResponse,
} from "@/lib/types";
import { DestinyMatrixChart } from "@/components/numerology/DestinyMatrixChart";
import { NumerologyReportView } from "@/components/numerology/NumerologyReportView";
import {
  Sparkles,
  Calendar,
  User,
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  RotateCcw,
  Heart,
  Users,
} from "lucide-react";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";

export default function DestinyMatrixPage() {
  const { language } = useLanguage();
  const { session, isAuthenticated } = useAuth();

  // Form states
  const [personName, setPersonName] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [enableCompatibility, setEnableCompatibility] = useState(false);
  const [partnerName, setPartnerName] = useState("");
  const [partnerBirthDate, setPartnerBirthDate] = useState("");
  const [reportLang, setReportLang] = useState<"en" | "ta">(language);

  // Execution states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DestinyMatrixResponse | null>(null);
  const [savedRecord, setSavedRecord] = useState<SavedNumerologyReportResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!birthDate.trim()) {
      setError("Please select a valid birth date.");
      return;
    }
    if (enableCompatibility && !partnerBirthDate.trim()) {
      setError("Please enter the partner's birth date for compatibility analysis.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setSavedRecord(null);

    try {
      const token = session?.access_token;
      const res = await calculateDestinyMatrix(
        {
          birth_date: birthDate.trim(),
          person_name: personName.trim() || undefined,
          partner_birth_date: enableCompatibility ? partnerBirthDate.trim() : undefined,
          partner_name: enableCompatibility ? partnerName.trim() || undefined : undefined,
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
              person_name: res.person_name || "Self",
              birth_date: res.birth_date,
              method: "destiny_matrix",
              system_convention: "22_major_arcana",
              calculation_data: {
                day_arcana: res.day_arcana,
                month_arcana: res.month_arcana,
                year_arcana: res.year_arcana,
                karmic_tail_base: res.karmic_tail_base,
                karmic_tail_triad: res.karmic_tail_triad,
                comfort_zone: res.comfort_zone,
                father_spirit: res.father_spirit,
                mother_spirit: res.mother_spirit,
                father_matter: res.father_matter,
                mother_matter: res.mother_matter,
                love_line: res.love_line,
                money_line: res.money_line,
                purpose: res.purpose,
                age_timeline: res.age_timeline,
                compatibility: res.compatibility,
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
      setError(err?.data?.detail || err?.message || "Failed to calculate Destiny Matrix.");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setSavedRecord(null);
    setError(null);
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
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
              label: language === "ta" ? "விதி அணி (Destiny Matrix)" : "Destiny Matrix",
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
              <Sparkles className="w-6 h-6" />
            </div>
            <h1 className="font-serif text-2xl font-bold text-[#0F172A]">
              Destiny Matrix (Soul Blueprint)
            </h1>
            <p className="mt-1 text-xs text-[#64748B]">
              Calculates your 22-Arcana octagram, Karmic Tail, Comfort Zone, and Life Purpose roadmap.
            </p>
          </div>

          {error && (
            <div className="mt-6 p-4 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-800 flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 text-rose-600 mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="mt-6 space-y-5">
            {/* Person Name (Optional) */}
            <div>
              <label className="block text-xs font-semibold text-[#334155] mb-1.5">
                Person Name (Optional)
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-[#94A3B8] absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={personName}
                  onChange={(e) => setPersonName(e.target.value)}
                  placeholder="e.g., Sundar"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-[#CBD5E1] bg-[#FAF8F5] text-xs text-[#0F172A] placeholder-[#94A3B8] focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-[#B8860B]/20 focus:border-[#B8860B]"
                />
              </div>
            </div>

            {/* Birth Date */}
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

            {/* Compatibility Mode Toggle */}
            <div className="pt-2 border-t border-[#E2DCD5]">
              <label className="flex items-center gap-2.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={enableCompatibility}
                  onChange={(e) => setEnableCompatibility(e.target.checked)}
                  className="w-4 h-4 rounded text-[#B8860B] focus:ring-[#B8860B] border-[#CBD5E1]"
                />
                <span className="text-xs font-bold text-[#0F172A] flex items-center gap-1.5">
                  <Heart className="w-3.5 h-3.5 text-rose-500" />
                  <span>Enable Couples Compatibility Matrix</span>
                </span>
              </label>

              {enableCompatibility && (
                <div className="mt-4 p-4 rounded-xl bg-[#FAF8F5] border border-[#E2DCD5] space-y-4">
                  <div className="flex items-center gap-2 text-xs font-bold text-[#8C6D23]">
                    <Users className="w-4 h-4 text-[#B8860B]" />
                    <span>Partner Information</span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-[11px] font-semibold text-[#334155] mb-1">
                        Partner Name
                      </label>
                      <input
                        type="text"
                        value={partnerName}
                        onChange={(e) => setPartnerName(e.target.value)}
                        placeholder="e.g., Priya"
                        className="w-full px-3 py-2 rounded-lg border border-[#CBD5E1] bg-white text-xs text-[#0F172A]"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-[#334155] mb-1">
                        Partner Date of Birth *
                      </label>
                      <input
                        type="date"
                        required={enableCompatibility}
                        value={partnerBirthDate}
                        onChange={(e) => setPartnerBirthDate(e.target.value)}
                        className="w-full px-3 py-2 rounded-lg border border-[#CBD5E1] bg-white text-xs text-[#0F172A]"
                      />
                    </div>
                  </div>
                </div>
              )}
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
                    <span>Generating Octagram Matrix...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-[#D8BD80]" />
                    <span>Generate Destiny Matrix Chart</span>
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
              <span>Calculate Another Chart</span>
            </button>
          </div>

          <NumerologyReportView
            title={`Destiny Matrix for ${result.person_name || "Birth Date " + result.birth_date}`}
            methodName="Destiny Matrix (22 Arcana)"
            systemConvention="22 Major Arcana Modulo Reduction"
            personName={result.person_name || "Subject"}
            birthDate={result.birth_date}
            displayNumber={savedRecord?.display_number}
            engineVersion={result.engine_version}
            chartComponent={<DestinyMatrixChart matrix={result} />}
            coreSummaryCards={[
              {
                title: "Day Arcana (Personal)",
                value: `Arcana ${result.day_arcana.arcana_number}`,
                subtitle: result.day_arcana.arcana_name,
              },
              {
                title: "Month Arcana (Spiritual)",
                value: `Arcana ${result.month_arcana.arcana_number}`,
                subtitle: result.month_arcana.arcana_name,
              },
              {
                title: "Year Arcana (Material)",
                value: `Arcana ${result.year_arcana.arcana_number}`,
                subtitle: result.year_arcana.arcana_name,
              },
              {
                title: "Karmic Tail Base",
                value: `Arcana ${result.karmic_tail_base.arcana_number}`,
                subtitle: `Triad: ${result.karmic_tail_triad.join("-")}`,
              },
              {
                title: "Comfort Zone (Center)",
                value: `Arcana ${result.comfort_zone.arcana_number}`,
                subtitle: result.comfort_zone.arcana_name,
                isMaster: true,
              },
              {
                title: "Personal Purpose (20-40y)",
                value: `Arcana ${result.purpose.personal_purpose}`,
                subtitle: "Sky + Earth Line Convergence",
              },
              {
                title: "Social Purpose (40-60y)",
                value: `Arcana ${result.purpose.social_purpose}`,
                subtitle: "Father + Mother Ancestral Synthesis",
              },
              {
                title: "Spiritual Purpose",
                value: `Arcana ${result.purpose.spiritual_purpose}`,
                subtitle: "Personal + Social Transcendence",
              },
            ]}
            detailedCalculations={[
              {
                name: "Day of Birth (Left Vertex)",
                value: result.day_arcana.arcana_number,
                method: `Arcana ${result.day_arcana.arcana_number}: ${result.day_arcana.arcana_name}`,
                interpretation: result.day_arcana.meaning,
              },
              {
                name: "Month of Birth (Top Vertex)",
                value: result.month_arcana.arcana_number,
                method: `Arcana ${result.month_arcana.arcana_number}: ${result.month_arcana.arcana_name}`,
                interpretation: result.month_arcana.meaning,
              },
              {
                name: "Year of Birth (Right Vertex)",
                value: result.year_arcana.arcana_number,
                method: `Arcana ${result.year_arcana.arcana_number}: ${result.year_arcana.arcana_name}`,
                interpretation: result.year_arcana.meaning,
              },
              {
                name: "Karmic Tail Base (Bottom Vertex)",
                value: result.karmic_tail_base.arcana_number,
                method: `Karmic Triad: ${result.karmic_tail_triad.join("-")}`,
                interpretation: result.karmic_tail_base.meaning,
              },
              {
                name: "Soul Comfort Zone (Center)",
                value: result.comfort_zone.arcana_number,
                method: `Convergence point of all 4 cardinal energies`,
                interpretation: result.comfort_zone.meaning,
              },
              {
                name: "Father's Spiritual Line (Top-Left)",
                value: result.father_spirit.arcana_number,
                method: `Day + Month Arcana reduced`,
                interpretation: result.father_spirit.meaning,
              },
              {
                name: "Mother's Spiritual Line (Top-Right)",
                value: result.mother_spirit.arcana_number,
                method: `Month + Year Arcana reduced`,
                interpretation: result.mother_spirit.meaning,
              },
              {
                name: "Money Line & Love Line Channels",
                value: `${result.money_line.arcana_number} / ${result.love_line.arcana_number}`,
                method: `Money Channel (${result.money_line.arcana_name}) & Love Channel (${result.love_line.arcana_name})`,
                interpretation: `Financial energy flows through Arcana ${result.money_line.arcana_number}. Love and relationship harmony is governed by Arcana ${result.love_line.arcana_number}.`,
              },
            ]}
            compatibility={
              result.compatibility
                ? {
                    partnerName: result.compatibility.person2_name,
                    relationshipPurpose: result.compatibility.relationship_purpose,
                    sharedFinance: result.compatibility.shared_finance,
                    loveHarmony: result.compatibility.love_harmony,
                    synthesis: result.compatibility.compatibility_synthesis,
                  }
                : null
            }
            cyclesOrForecast={result.age_timeline.map((item) => ({
              label: `Age ${item.age} Years`,
              value: `Arcana ${item.arcana_number}`,
              description: `${item.theme}: ${item.description}`,
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
