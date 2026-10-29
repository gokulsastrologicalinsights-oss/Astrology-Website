"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { getNumerologyReport, downloadNumerologyReportPdf } from "@/lib/api";
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
  const [pdfDownloading, setPdfDownloading] = useState(false);
  const [pdfError, setPdfError] = useState<string | null>(null);

  const handleDownloadPdf = async (lang: "en" | "ta" = "en") => {
    if (!report || !session?.access_token) return;
    setPdfDownloading(true);
    setPdfError(null);
    try {
      const blob = await downloadNumerologyReportPdf(report.id, lang, session.access_token);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const safeName = (report.person_name || "Report").replace(/\s+/g, "_");
      a.download = `Numerology_Report_${report.display_number}_${safeName}_${lang}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setPdfError(err?.message || "Failed to download numerology PDF.");
    } finally {
      setPdfDownloading(false);
    }
  };

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
      <div className="w-full px-4 py-20 text-center">
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
        title: "Birth / Psychic (Mulank)",
        value: calc.birth_psychic_number?.number_value ?? "-",
        subtitle: calc.birth_psychic_number?.ruling_planet
          ? `${calc.birth_psychic_number.ruling_planet} • ${calc.birth_psychic_number.short_interpretation}`
          : calc.birth_psychic_number?.short_interpretation,
      },
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
  } else if (report.method === "name_correction") {
    const orig = calc.original_analysis || {};
    const topCand = calc.candidates?.[0];
    coreCards = [
      {
        title: "Original Expression",
        value: orig.expression ?? "-",
        subtitle: `Compound: ${orig.compound_expression ?? "-"}`,
        isMaster: orig.is_master,
      },
      {
        title: "Target Vibration",
        value: calc.target_number ?? "-",
        subtitle: `Source: ${calc.target_source ?? "Harmonic Optimization"}`,
      },
      {
        title: "Soul Urge (Vowels)",
        value: orig.soul_urge ?? "-",
        subtitle: "Inner Motivation Vibration",
      },
      {
        title: "Personality (Consonants)",
        value: orig.personality ?? "-",
        subtitle: "Outer Persona Vibration",
      },
      {
        title: "Top Variation Score",
        value: topCand?.composite_score !== undefined ? `${topCand.composite_score} / 100` : "-",
        subtitle: topCand ? `${topCand.name} (${topCand.variation_type})` : "Standard Analysis",
      },
    ];
  } else if (report.method === "business") {
    coreCards = [
      {
        title: "Legal Expression",
        value: calc.legal_analysis?.expression_number ?? "-",
        subtitle: `Compound: ${calc.legal_analysis?.compound_expression ?? "-"}`,
      },
      {
        title: "Brand Expression",
        value: calc.brand_analysis?.expression_number ?? "-",
        subtitle: `Compound: ${calc.brand_analysis?.compound_expression ?? "-"}`,
        isMaster: calc.brand_analysis?.is_master,
      },
      {
        title: "Industry Harmony",
        value: `${calc.brand_analysis?.industry_harmony_score ?? "-"}%`,
        subtitle: calc.industry_category ? `${calc.industry_category.toUpperCase()}` : "-",
      },
      {
        title: "Partnership Score",
        value: `${calc.partnership_matrix?.overall_partnership_score ?? "-"}%`,
        subtitle: calc.partnership_matrix?.has_friction ? "Friction Alert" : "Harmonious",
      },
      {
        title: "Top Composite Score",
        value: `${calc.candidates?.[0]?.composite_score ?? calc.brand_analysis?.composite_score ?? "-"} / 100`,
        subtitle: calc.candidates?.[0]?.name ?? calc.normalized_brand_name,
      },
    ];
  } else if (report.method === "phone") {
    coreCards = [
      {
        title: "Phone Root Number",
        value: calc.primary_analysis?.root_number ?? "-",
        subtitle: `Ruler: ${calc.primary_analysis?.ruling_planet ?? "-"}`,
        isMaster: calc.primary_analysis?.is_master,
      },
      {
        title: "Compound Digit Sum",
        value: calc.primary_analysis?.compound_sum ?? "-",
        subtitle: `${calc.primary_analysis?.digit_count ?? 10} Digits Total`,
      },
      {
        title: "Vanity / Rhythm Score",
        value: `${calc.primary_analysis?.patterns?.vanity_score ?? "-"}%`,
        subtitle: calc.primary_analysis?.patterns?.is_vip_vanity ? "VIP Vanity Number" : "Standard Rhythm",
      },
      {
        title: "Personal Synergy",
        value: calc.personal_compatibility?.personal_score ? `${calc.personal_compatibility.personal_score}%` : "N/A",
        subtitle: calc.personal_compatibility?.level ?? "No Birth Date Set",
      },
      {
        title: "Zero Frequency",
        value: calc.primary_analysis?.zero_count ?? 0,
        subtitle: calc.primary_analysis?.zero_count === 0 ? "Direct Energy" : "Catalyst / Amplifier",
      },
    ];
  } else if (report.method === "vehicle") {
    coreCards = [
      {
        title: "Vehicle Root Number",
        value: calc.primary_analysis?.root_number ?? "-",
        subtitle: `Ruler: ${calc.primary_analysis?.ruler ?? calc.primary_analysis?.ruling_planet ?? "-"}`,
        isMaster: calc.primary_analysis?.is_master,
      },
      {
        title: "Registration Plate",
        value: calc.formatted_registration ?? calc.raw_input,
        subtitle: `${calc.state_name ?? calc.state_code ?? "Vehicle Plate"} • Mode: ${calc.calculation_mode}`,
      },
      {
        title: "Vanity / VIP Score",
        value: `${calc.vanity_score ?? calc.patterns?.vanity_score ?? "-"}%`,
        subtitle: calc.patterns?.pattern_classification ?? "Standard Registration",
      },
      {
        title: "Usage Alignment",
        value: interp.usage_alignment?.score ? `${interp.usage_alignment.score}%` : "Optimal",
        subtitle: interp.usage_alignment?.usage_name ?? calc.vehicle_usage,
      },
      {
        title: "Driver Affinity",
        value: interp.overall_owner_score !== undefined && interp.overall_owner_score !== null ? `${interp.overall_owner_score}%` : "N/A",
        subtitle: interp.owner_alignments?.[0]?.level ?? "Single / Multi Driver",
      },
    ];
  } else if (report.method === "property") {
    coreCards = [
      {
        title: "Property Root Number",
        value: calc.primary_analysis?.root_number ?? "-",
        subtitle: `Ruler: ${calc.primary_analysis?.ruler ?? calc.primary_analysis?.ruling_planet ?? "-"}`,
        isMaster: calc.primary_analysis?.is_master,
      },
      {
        title: "Active Calculation Mode",
        value: calc.active_mode?.replace(/_/g, " ").toUpperCase() ?? "COMBINED",
        subtitle: `Compound: ${calc.primary_analysis?.compound_sum ?? "-"} • ${calc.property_category ?? "Property"}`,
      },
      {
        title: "Vastu Orientation",
        value: calc.vastu_facing?.direction ? `${calc.vastu_facing.direction} (${calc.vastu_facing.sanskrit_name})` : "Not Specified",
        subtitle: calc.vastu_facing?.element ? `Element: ${calc.vastu_facing.element} • Ruler: ${calc.vastu_facing.ruler}` : "General Orientation",
      },
      {
        title: "Usage Resonance",
        value: interp.usage_alignment?.score ? `${interp.usage_alignment.score}%` : "Harmonious",
        subtitle: interp.usage_alignment?.usage_name ?? calc.property_usage,
      },
      {
        title: "Resident Alignment",
        value: interp.overall_resident_score !== undefined && interp.overall_resident_score !== null ? `${interp.overall_resident_score}%` : "N/A",
        subtitle: interp.resident_alignments?.length ? `${interp.resident_alignments.length} Resident(s) Evaluated` : "No Residents Added",
      },
    ];
  } else if (report.method === "marriage") {
    coreCards = [
      {
        title: "Overall Couple Synergy",
        value: `${calc.overall_score ?? interp.overall_score ?? "-"} / 100`,
        subtitle: calc.overall_harmony_level ?? interp.overall_harmony_level ?? "Compatibility Assessment",
      },
      {
        title: "Life Path Alignment",
        value: `${calc.life_path_compatibility?.score ?? "-"}%`,
        subtitle: `A: LP ${calc.person_a_profile?.life_path_number} • B: LP ${calc.person_b_profile?.life_path_number}`,
        isMaster: calc.person_a_profile?.is_life_path_master || calc.person_b_profile?.is_life_path_master,
      },
      {
        title: "Psychic / Mulank Harmony",
        value: `${calc.psychic_compatibility?.score ?? "-"}%`,
        subtitle: `A: Day ${calc.person_a_profile?.birth_psychic_number} • B: Day ${calc.person_b_profile?.birth_psychic_number}`,
      },
      {
        title: "Expression / Destiny",
        value: calc.expression_compatibility?.score ? `${calc.expression_compatibility.score}%` : "DOB Only",
        subtitle: calc.expression_compatibility?.harmony_level ?? "Name Comparison",
      },
      {
        title: "Emotional Longing (Soul Urge)",
        value: calc.soul_urge_compatibility?.score ? `${calc.soul_urge_compatibility.score}%` : "DOB Only",
        subtitle: calc.soul_urge_compatibility?.harmony_level ?? "Heart's Desire",
      },
    ];
  } else if ((report.method as string) === "family") {
    const mems = calc.members_evaluated || calc.members || [];
    const dom = (calc.dominant_vibrations || []).join(", ") || "Balanced";
    const cands = calc.baby_name_candidates || calc.candidate_names || [];
    const elem = calc.elemental_balance || {};
    coreCards = [
      {
        title: "Family Harmony Score",
        value: `${calc.overall_family_harmony_score ?? calc.family_harmony_score ?? "-"}%`,
        subtitle: calc.overall_family_harmony_level ?? "Collective Resonance",
      },
      {
        title: "Family Members",
        value: mems.length,
        subtitle: `${mems.map((m: any) => m.name).slice(0, 3).join(", ")}${mems.length > 3 ? "..." : ""}`,
      },
      {
        title: "Dominant Root",
        value: dom,
        subtitle: "Core Archetype Vibration",
      },
      {
        title: "Leading Element",
        value: elem.dominant_element || "Balanced",
        subtitle: `Fire: ${elem.Fire ?? 0} • Earth: ${elem.Earth ?? 0}`,
      },
      {
        title: "Baby Name Candidates",
        value: cands.length,
        subtitle: cands[0] ? `Top: ${cands[0].name || cands[0].candidate_name} (${cands[0].composite_score} pts)` : "None added",
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

  let detailedCalcs: Array<{
    name: string;
    value: string | number;
    method: string;
    interpretation: string;
    attributes?: string[];
  }> = [];

  if (report.method === "traditional") {
    if (calc.birth_psychic_number) {
      detailedCalcs.push({
        name: calc.birth_psychic_number.number_name || "Birth / Psychic Number",
        value: calc.birth_psychic_number.number_value,
        method: calc.birth_psychic_number.calculation_method || "Day of month reduction",
        interpretation: calc.birth_psychic_number.detailed_interpretation || "",
        attributes: calc.birth_psychic_number.key_attributes || [],
      });
    }
    if (calc.life_path) {
      detailedCalcs.push({
        name: calc.life_path.number_name || "Life Path Number",
        value: calc.life_path.number_value,
        method: calc.life_path.calculation_method || "Month + Day + Year reduction",
        interpretation: calc.life_path.detailed_interpretation || "",
        attributes: calc.life_path.key_attributes || [],
      });
    }
    if (calc.expression_destiny) {
      detailedCalcs.push({
        name: calc.expression_destiny.number_name || "Expression / Destiny Number",
        value: calc.expression_destiny.number_value,
        method: calc.expression_destiny.calculation_method || "Full Name letter sum",
        interpretation: calc.expression_destiny.detailed_interpretation || "",
        attributes: calc.expression_destiny.key_attributes || [],
      });
    }
    if (calc.soul_urge) {
      detailedCalcs.push({
        name: calc.soul_urge.number_name || "Soul Urge Number",
        value: calc.soul_urge.number_value,
        method: calc.soul_urge.calculation_method || "Vowels sum",
        interpretation: calc.soul_urge.detailed_interpretation || "",
        attributes: calc.soul_urge.key_attributes || [],
      });
    }
    if (calc.personality) {
      detailedCalcs.push({
        name: calc.personality.number_name || "Personality Number",
        value: calc.personality.number_value,
        method: calc.personality.calculation_method || "Consonants sum",
        interpretation: calc.personality.detailed_interpretation || "",
        attributes: calc.personality.key_attributes || [],
      });
    }
    if (calc.maturity_number) {
      detailedCalcs.push({
        name: calc.maturity_number.number_name || "Maturity Number",
        value: calc.maturity_number.number_value,
        method: calc.maturity_number.calculation_method || "Life Path + Expression sum",
        interpretation: calc.maturity_number.detailed_interpretation || "",
        attributes: calc.maturity_number.key_attributes || [],
      });
    }
  } else if (report.method === "name_correction") {
    if (calc.original_analysis) {
      detailedCalcs.push({
        name: `Original Name (${calc.original_name || report.person_name})`,
        value: calc.original_analysis.expression,
        method: `${report.system_convention.toUpperCase()} Letter Reduction`,
        interpretation: `Expression ${calc.original_analysis.expression} (Compound: ${calc.original_analysis.compound_expression})`,
        attributes: [
          `Soul Urge: ${calc.original_analysis.soul_urge}`,
          `Personality: ${calc.original_analysis.personality}`,
          `Target: ${calc.target_number ?? "N/A"} (${calc.target_source ?? "Harmonious"})`,
        ],
      });
    }
    if (calc.candidates?.length) {
      calc.candidates.slice(0, 4).forEach((cand: any) => {
        detailedCalcs.push({
          name: `Candidate: ${cand.name} (${cand.variation_type || "Optimized"})`,
          value: `${cand.composite_score} pts`,
          method: `Expression ${cand.expression_number} (Compound: ${cand.compound_expression})`,
          interpretation: cand.vibrational_synthesis || (cand.matches_target ? "Matches Target Vibration" : "Harmonic Candidate"),
          attributes: [
            `Harmony: ${cand.harmony_score}%`,
            `Pronunciation: ${cand.pronunciation_score}%`,
            `Simplicity: ${cand.simplicity_score}%`,
          ],
        });
      });
    }
  } else if (report.method === "business") {
    if (calc.legal_analysis) {
      detailedCalcs.push({
        name: "Statutory Legal Entity",
        value: calc.legal_analysis.expression_number,
        method: `${report.system_convention.toUpperCase()} Letter Sum (Full Corporate Name)`,
        interpretation: calc.legal_analysis.vibrational_synthesis,
        attributes: [
          `Compound: ${calc.legal_analysis.compound_expression}`,
          `Soul: ${calc.legal_analysis.soul_urge_number}`,
          `Personality: ${calc.legal_analysis.personality_number}`,
        ],
      });
    }
    if (calc.brand_analysis) {
      detailedCalcs.push({
        name: "Normalized Public Brand",
        value: calc.brand_analysis.expression_number,
        method: `${report.system_convention.toUpperCase()} Letter Sum (Brand Without Suffixes)`,
        interpretation: calc.brand_analysis.vibrational_synthesis,
        attributes: [
          `Compound: ${calc.brand_analysis.compound_expression}`,
          `Soul: ${calc.brand_analysis.soul_urge_number}`,
          `Personality: ${calc.brand_analysis.personality_number}`,
          `Industry Harmony: ${calc.brand_analysis.industry_harmony_score}%`,
          `Founder Harmony: ${calc.brand_analysis.founder_harmony_score}%`,
          `Composite Score: ${calc.brand_analysis.composite_score}/100`,
        ],
      });
    }
    if (calc.tagline_analysis) {
      detailedCalcs.push({
        name: "Brand Slogan / Tagline",
        value: calc.tagline_analysis.expression_number,
        method: "Tagline Reduction & Brand Synergy",
        interpretation: calc.tagline_analysis.synergy_interpretation,
        attributes: [
          `Tagline: "${calc.tagline_analysis.tagline}"`,
          `Compound: ${calc.tagline_analysis.compound_expression}`,
          `Synergy Score: ${calc.tagline_analysis.synergy_score}%`,
        ],
      });
    }
  } else if (report.method === "phone") {
    if (calc.primary_analysis) {
      detailedCalcs.push({
        name: "National Phone Vibration",
        value: calc.primary_analysis.root_number,
        method: `${report.system_convention.toUpperCase()} Digit Reduction (${calc.formatted_national || calc.national_number})`,
        interpretation: calc.primary_analysis.vibrational_meaning,
        attributes: [
          `Compound: ${calc.primary_analysis.compound_sum}`,
          `Keyword: ${calc.primary_analysis.keyword}`,
          `Vanity Score: ${calc.primary_analysis.patterns?.vanity_score}%`,
          `Missing Digits: ${calc.primary_analysis.missing_digits?.join(", ") || "None"}`,
        ],
      });
    }
    if (calc.personal_compatibility) {
      detailedCalcs.push({
        name: "Personal Owner Affinity",
        value: `${calc.personal_compatibility.personal_score}%`,
        method: `Resonance with DOB: ${calc.personal_compatibility.birth_date}`,
        interpretation: calc.personal_compatibility.synthesis,
        attributes: [
          `Psychic Number: ${calc.personal_compatibility.psychic_number} (${calc.personal_compatibility.psychic_harmony_score}%)`,
          `Life Path: ${calc.personal_compatibility.life_path_number} (${calc.personal_compatibility.life_path_harmony_score}%)`,
          `Resonance Level: ${calc.personal_compatibility.level}`,
        ],
      });
    }
    if (calc.zero_significance) {
      detailedCalcs.push({
        name: "Zero (0) Catalyst Interpretation",
        value: calc.primary_analysis?.zero_count ?? 0,
        method: "Chaldean / Vedic Cipher Dynamics",
        interpretation: calc.zero_significance,
        attributes: [
          `Zero Count: ${calc.primary_analysis?.zero_count ?? 0}`,
        ],
      });
    }
  } else if (report.method === "vehicle") {
    if (calc.primary_analysis) {
      detailedCalcs.push({
        name: `Plate Vibration (${calc.formatted_registration || calc.raw_input})`,
        value: calc.primary_analysis.root_number,
        method: `${report.system_convention.toUpperCase()} (${calc.primary_analysis.mode_label || calc.calculation_mode})`,
        interpretation: calc.primary_analysis.vibrational_meaning,
        attributes: [
          `Compound Sum: ${calc.primary_analysis.compound_sum}`,
          `Ruling Planet: ${calc.primary_analysis.ruling_planet}`,
          `Archetype: ${calc.primary_analysis.keyword}`,
          `Formula Steps: ${calc.primary_analysis.reduction_steps?.join(" -> ")}`,
        ],
      });
    }
    if (interp.usage_alignment) {
      detailedCalcs.push({
        name: "Vehicle Usage Resonance",
        value: `${interp.usage_alignment.score}%`,
        method: `Usage Archetype: ${interp.usage_alignment.usage_name}`,
        interpretation: interp.usage_alignment.description,
        attributes: [
          `Category: ${interp.usage_alignment.vehicle_usage}`,
          `Planetary Rulers: ${interp.usage_alignment.planetary_rulers}`,
          `Synergy Level: ${interp.usage_alignment.level}`,
        ],
      });
    }
    if (interp.owner_alignments?.length) {
      for (const owner of interp.owner_alignments) {
        detailedCalcs.push({
          name: `Driver Synergy: ${owner.name} (${owner.role})`,
          value: `${owner.personal_score}%`,
          method: `DOB: ${owner.birth_date}`,
          interpretation: owner.synthesis,
          attributes: [
            `Psychic Number: ${owner.psychic_number} (${owner.psychic_harmony_score}%)`,
            `Life Path Number: ${owner.life_path_number} (${owner.life_path_harmony_score}%)`,
            `Harmony Level: ${owner.level}`,
          ],
        });
      }
    }
  } else if (report.method === "property") {
    if (calc.primary_analysis) {
      detailedCalcs.push({
        name: `Property Vibration (${calc.active_mode?.replace(/_/g, " ")})`,
        value: calc.primary_analysis.root_number,
        method: `${report.system_convention.toUpperCase()} (${calc.primary_analysis.calculation_mode || calc.active_mode})`,
        interpretation: calc.primary_analysis.vibrational_meaning,
        attributes: [
          `Compound Sum: ${calc.primary_analysis.compound_sum}`,
          `Ruling Planet: ${calc.primary_analysis.ruler || calc.primary_analysis.ruling_planet || "N/A"}`,
          `Archetype: ${calc.primary_analysis.keyword || "N/A"}`,
          `Reduction Formula: ${calc.primary_analysis.reduction_steps?.join(" -> ") || "N/A"}`,
        ],
      });
    }
    if (calc.components) {
      for (const comp of Object.values(calc.components) as any[]) {
        if (comp && comp.raw_input) {
          detailedCalcs.push({
            name: `Component: ${comp.component_name?.replace(/_/g, " ").toUpperCase()}`,
            value: comp.root_number,
            method: `Compound: ${comp.compound_sum} (Input: "${comp.raw_input}")`,
            interpretation: comp.vibrational_meaning,
            attributes: [
              `Planet: ${comp.ruler || comp.ruling_planet}`,
              `Steps: ${comp.reduction_steps?.join(" -> ")}`,
            ],
          });
        }
      }
    }
    if (calc.vastu_facing) {
      detailedCalcs.push({
        name: `Vastu Facing: ${calc.vastu_facing.direction} (${calc.vastu_facing.sanskrit_name})`,
        value: `${calc.vastu_facing.vastu_score}%`,
        method: `Classical Directional Mandala (${calc.vastu_facing.deity})`,
        interpretation: calc.vastu_facing.recommendation,
        attributes: [
          `Presiding Deity: ${calc.vastu_facing.deity}`,
          `Mahabhuta Element: ${calc.vastu_facing.element}`,
          `Planetary Ruler: ${calc.vastu_facing.ruler}`,
          `Recommended For: ${calc.vastu_facing.suitable_for?.join(", ") || "General Living"}`,
        ],
      });
    }
    if (interp.usage_alignment) {
      detailedCalcs.push({
        name: "Property Usage Resonance",
        value: `${interp.usage_alignment.score}%`,
        method: `Usage: ${interp.usage_alignment.usage_name}`,
        interpretation: interp.usage_alignment.description,
        attributes: [
          `Category: ${calc.property_category}`,
          `Tenure: ${calc.tenure_type}`,
          `Planetary Rulers: ${interp.usage_alignment.planetary_rulers}`,
        ],
      });
    }
    if (interp.resident_alignments?.length) {
      for (const resident of interp.resident_alignments) {
        detailedCalcs.push({
          name: `Resident Alignment: ${resident.name} (${resident.role})`,
          value: `${resident.personal_score}%`,
          method: `DOB: ${resident.birth_date}`,
          interpretation: resident.synthesis,
          attributes: [
            `Psychic Number: ${resident.psychic_number} (${resident.psychic_harmony_score}%)`,
            `Life Path: ${resident.life_path_number} (${resident.life_path_harmony_score}%)`,
            `Harmonic Level: ${resident.level}`,
          ],
        });
      }
    }
  } else if (report.method === "marriage") {
    if (calc.life_path_compatibility) {
      detailedCalcs.push({
        name: "Life Path (Bhagyank) Compatibility",
        value: `${calc.life_path_compatibility.score}%`,
        method: `Planetary Dynamic: ${calc.life_path_compatibility.planetary_dynamic}`,
        interpretation: calc.life_path_compatibility.interpretation,
        attributes: [
          `Partner A Life Path: ${calc.person_a_profile?.life_path_number} (${calc.person_a_profile?.life_path_planet})`,
          `Partner B Life Path: ${calc.person_b_profile?.life_path_number} (${calc.person_b_profile?.life_path_planet})`,
          `Harmony Level: ${calc.life_path_compatibility.harmony_level}`,
        ],
      });
    }
    if (calc.psychic_compatibility) {
      detailedCalcs.push({
        name: "Birth / Psychic Number (Mulank) Compatibility",
        value: `${calc.psychic_compatibility.score}%`,
        method: `Planetary Dynamic: ${calc.psychic_compatibility.planetary_dynamic}`,
        interpretation: calc.psychic_compatibility.interpretation,
        attributes: [
          `Partner A Day Number: ${calc.person_a_profile?.birth_psychic_number} (${calc.person_a_profile?.birth_psychic_planet})`,
          `Partner B Day Number: ${calc.person_b_profile?.birth_psychic_number} (${calc.person_b_profile?.birth_psychic_planet})`,
          `Harmony Level: ${calc.psychic_compatibility.harmony_level}`,
        ],
      });
    }
    if (calc.expression_compatibility) {
      detailedCalcs.push({
        name: "Expression / Destiny Name Compatibility",
        value: `${calc.expression_compatibility.score}%`,
        method: `${report.system_convention.toUpperCase()} Name Letter Reduction`,
        interpretation: calc.expression_compatibility.interpretation,
        attributes: [
          `Partner A Expression: ${calc.person_a_profile?.expression_number}`,
          `Partner B Expression: ${calc.person_b_profile?.expression_number}`,
          `Harmony Level: ${calc.expression_compatibility.harmony_level}`,
        ],
      });
    }
    if (calc.soul_urge_compatibility) {
      detailedCalcs.push({
        name: "Soul Urge (Heart's Desire) Compatibility",
        value: `${calc.soul_urge_compatibility.score}%`,
        method: "Vowel Energy Resonance",
        interpretation: calc.soul_urge_compatibility.interpretation,
        attributes: [
          `Partner A Soul Urge: ${calc.person_a_profile?.soul_urge_number}`,
          `Partner B Soul Urge: ${calc.person_b_profile?.soul_urge_number}`,
          `Harmony Level: ${calc.soul_urge_compatibility.harmony_level}`,
        ],
      });
    }
    if (calc.shared_strengths?.length) {
      detailedCalcs.push({
        name: "Key Mutual Strengths",
        value: `${calc.shared_strengths.length} Synergies`,
        method: "Relationship Strengths Synthesis",
        interpretation: calc.overall_synthesis || "",
        attributes: calc.shared_strengths,
      });
    }
    if (calc.potential_challenges?.length) {
      detailedCalcs.push({
        name: "Growth & Friction Points",
        value: `${calc.potential_challenges.length} Areas`,
        method: "Contrasting Polarities Analysis",
        interpretation: "Conscious awareness and open communication bridge natural differences.",
        attributes: calc.potential_challenges,
      });
    }
    if (calc.conversation_prompts?.length) {
      detailedCalcs.push({
        name: "Couples Dialogue Prompts",
        value: `${calc.conversation_prompts.length} Prompts`,
        method: "Constructive Relationship Inquiry",
        interpretation: "Recommended questions to explore together for emotional intimacy.",
        attributes: calc.conversation_prompts,
      });
    }
  } else if ((report.method as string) === "family") {
    const mems = calc.members_evaluated || calc.members || [];
    mems.forEach((m: any) => {
      detailedCalcs.push({
        name: `${m.name} (${(m.role || m.relationship || "Member").toUpperCase()})`,
        value: `Mulank: ${m.birth_psychic_number ?? "-"} | Bhagyank: ${m.life_path_number ?? "-"}`,
        method: `${m.birth_date ? `DOB: ${m.birth_date}` : "Name only"} • Element: ${m.element}`,
        interpretation: m.short_summary || m.archetype,
        attributes: [
          `Expression: ${m.expression_number ?? "-"}`,
          `Ruling Planet: ${m.ruling_planet ?? "-"}`,
          `Archetype: ${m.archetype}`,
        ],
      });
    });
    const pairs = calc.pairwise_comparisons || calc.pairwise_dynamics || [];
    pairs.slice(0, 4).forEach((p: any) => {
      detailedCalcs.push({
        name: `${p.person_a_name || p.member_a_name} ↔ ${p.person_b_name || p.member_b_name} (${p.relationship_type})`,
        value: `${p.composite_harmony_score || p.compatibility_score}%`,
        method: p.planetary_dynamic,
        interpretation: p.nurturing_prompt || p.parenting_dialogue_prompt,
        attributes: p.shared_strengths || [],
      });
    });
  }

  return (
    <div className="w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 sm:py-8 space-y-8">
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

      {pdfError && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
          <span>{pdfError}</span>
        </div>
      )}

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
        detailedCalculations={detailedCalcs}
        karmicDebts={calc.karmic_debts}
        calculationBreakdown={calc.calculation_breakdown}
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
        reportId={report.id}
        onDownloadPdf={handleDownloadPdf}
        isDownloadingPdf={pdfDownloading}
      />
    </div>
  );
}
