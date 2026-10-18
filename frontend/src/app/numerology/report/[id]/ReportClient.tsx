"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { getNumerologyReport } from "@/lib/api";
import { SavedNumerologyReportResponse } from "@/lib/types";
import { NumerologyReportView } from "@/components/numerology/NumerologyReportView";
import { DestinyMatrixChart } from "@/components/numerology/DestinyMatrixChart";
import { LoShuGrid } from "@/components/numerology/LoShuGrid";
import { ArrowLeft, AlertCircle, Loader2 } from "lucide-react";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";

interface ReportClientProps {
  reportId: string;
}

export default function ReportClient({ reportId }: ReportClientProps) {
  const { session, isLoading: authLoading, isAuthenticated } = useAuth();
  const [report, setReport] = useState<SavedNumerologyReportResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading) {
      if (!isAuthenticated || !session?.access_token) {
        setError("You must be logged in to access saved numerology reports.");
        setLoading(false);
        return;
      }

      getNumerologyReport(reportId, session.access_token)
        .then((data) => {
          setReport(data);
        })
        .catch((err) => {
          setError(err?.data?.detail || err?.message || "Failed to load saved report.");
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [reportId, session?.access_token, isAuthenticated, authLoading]);

  if (loading || authLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <Loader2 className="w-8 h-8 mx-auto animate-spin text-[#B8860B] mb-3" />
        <p className="text-sm text-[#64748B]">Loading saved numerology report #{reportId.slice(0, 8)}...</p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center space-y-4">
        <div className="w-12 h-12 mx-auto rounded-full bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-600">
          <AlertCircle className="w-6 h-6" />
        </div>
        <h2 className="font-serif text-xl font-bold text-[#0F172A]">
          Report Unavailable
        </h2>
        <p className="text-xs text-[#64748B] max-w-md mx-auto">{error}</p>
        <div className="pt-2">
          <Link
            href="/numerology"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-white bg-[#0F172A] hover:bg-[#1E293B]"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Return to Numerology</span>
          </Link>
        </div>
      </div>
    );
  }

  // Parse stored calculations and interpretations
  const calc = report.calculation_data;
  const interp = report.interpretation_data;

  // Determine method rendering
  let chartNode: React.ReactNode = null;
  let coreCards: Array<{
    title: string;
    value: string | number;
    subtitle?: string;
    isMaster?: boolean;
  }> = [];

  if (report.method === "traditional") {
    coreCards = [
      {
        title: "Life Path",
        value: calc.life_path?.number_value ?? "-",
        subtitle: calc.life_path?.short_interpretation,
        isMaster: calc.life_path?.is_master,
      },
      {
        title: "Expression / Destiny",
        value: calc.expression_destiny?.number_value ?? "-",
        subtitle: calc.expression_destiny?.short_interpretation,
        isMaster: calc.expression_destiny?.is_master,
      },
      {
        title: "Soul Urge",
        value: calc.soul_urge?.number_value ?? "-",
        subtitle: calc.soul_urge?.short_interpretation,
        isMaster: calc.soul_urge?.is_master,
      },
      {
        title: "Personality",
        value: calc.personality?.number_value ?? "-",
        subtitle: calc.personality?.short_interpretation,
        isMaster: calc.personality?.is_master,
      },
      {
        title: "Birthday Number",
        value: calc.birthday_number?.number_value ?? "-",
        subtitle: calc.birthday_number?.short_interpretation,
      },
      {
        title: "Attitude Number",
        value: calc.attitude_number?.number_value ?? "-",
        subtitle: calc.attitude_number?.short_interpretation,
      },
      {
        title: "Maturity Number",
        value: calc.maturity_number?.number_value ?? "-",
        subtitle: calc.maturity_number?.short_interpretation,
      },
      {
        title: "Personal Year",
        value: calc.personal_year?.number_value ?? "-",
        subtitle: calc.personal_year?.short_interpretation,
      },
    ];
  } else if (report.method === "destiny_matrix") {
    chartNode = <DestinyMatrixChart matrix={calc as any} />;
    coreCards = [
      {
        title: "Day Arcana",
        value: `Arcana ${calc.day_arcana?.arcana_number}`,
        subtitle: calc.day_arcana?.arcana_name,
      },
      {
        title: "Month Arcana",
        value: `Arcana ${calc.month_arcana?.arcana_number}`,
        subtitle: calc.month_arcana?.arcana_name,
      },
      {
        title: "Year Arcana",
        value: `Arcana ${calc.year_arcana?.arcana_number}`,
        subtitle: calc.year_arcana?.arcana_name,
      },
      {
        title: "Comfort Zone (Center)",
        value: `Arcana ${calc.comfort_zone?.arcana_number}`,
        subtitle: calc.comfort_zone?.arcana_name,
        isMaster: true,
      },
      {
        title: "Personal Purpose",
        value: `Arcana ${calc.purpose?.personal_purpose}`,
        subtitle: "Ages 20-40",
      },
      {
        title: "Social Purpose",
        value: `Arcana ${calc.purpose?.social_purpose}`,
        subtitle: "Ages 40-60",
      },
    ];
  } else {
    // Advanced
    chartNode = calc.lo_shu ? <LoShuGrid loShu={calc.lo_shu} /> : null;
    coreCards = [
      {
        title: "Unicode Vibration",
        value: calc.unicode_derived_name_number ?? "-",
        subtitle: "Universal Code-Point Root",
      },
      {
        title: "Missing Karmic Lessons",
        value: calc.karmic_lessons?.length ?? 0,
        subtitle: calc.karmic_lessons?.join(", ") || "None",
      },
      {
        title: "Dominant Frequencies",
        value: calc.dominant_vibrations?.join(", ") || "None",
        subtitle: "Most repeated digits",
      },
    ];
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Navigation Breadcrumbs & Back Link */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <Breadcrumbs
          items={[
            {
              label: "Astrology Tools",
              href: "/tools",
            },
            {
              label: "Numerology",
              href: "/tools/numerology",
            },
            {
              label: `Saved Report #${report.display_number}`,
            },
          ]}
        />

        <Link
          href="/tools/numerology?tab=reports"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#52667E] hover:text-[#102A4C] transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Numerology Reports</span>
        </Link>
      </div>

      <NumerologyReportView
        title={`Saved Numerology Reading #${report.display_number}: ${report.person_name}`}
        methodName={report.method.replace("_", " ").toUpperCase()}
        systemConvention={report.system_convention}
        personName={report.person_name}
        birthDate={report.birth_date}
        displayNumber={report.display_number}
        engineVersion={report.engine_version}
        chartComponent={chartNode}
        coreSummaryCards={coreCards}
        strengths={interp.strengths || []}
        challenges={interp.challenges || []}
        careerTendencies={interp.career_tendencies || []}
        financialTendencies={interp.financial_tendencies || []}
        loveThemes={interp.love_themes || []}
        compatibility={
          calc.compatibility
            ? {
                partnerName: calc.compatibility.person2_name,
                relationshipPurpose: calc.compatibility.relationship_purpose,
                sharedFinance: calc.compatibility.shared_finance,
                loveHarmony: calc.compatibility.love_harmony,
                synthesis: calc.compatibility.compatibility_synthesis,
              }
            : null
        }
        cyclesOrForecast={
          calc.age_timeline
            ? calc.age_timeline.map((item: any) => ({
                label: `Age ${item.age} Years`,
                value: `Arcana ${item.arcana_number}`,
                description: `${item.theme}: ${item.description}`,
              }))
            : undefined
        }
        overallSynthesis={interp.overall_synthesis || "Deterministic numerology reading completed successfully."}
      />
    </div>
  );
}
