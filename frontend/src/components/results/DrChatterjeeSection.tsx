"use client";

import React, { useMemo } from "react";
import {
  DrChatterjeeCompendium,
  SaptaDhatuDetail,
  EndocrineGlandDetail,
  MedicalRule,
} from "@/lib/types";
import {
  Activity,
  AlertCircle,
  AlertTriangle,
  Award,
  CheckCircle2,
  Compass,
  Droplet,
  Droplets,
  HeartPulse,
  Pill,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

interface DrChatterjeeSectionProps {
  compendium: DrChatterjeeCompendium;
  language: "en" | "ta";
  onSelectRule?: (rule: MedicalRule) => void;
}

export function DrChatterjeeSection({
  compendium,
  language,
  onSelectRule,
}: DrChatterjeeSectionProps) {
  const {
    death_point,
    parijata_longevity_eval,
    sapta_dhatus = [],
    endocrine_glands = [],
    diabetes_assessment,
    natural_remedies,
    golden_rules = [],
  } = compendium;

  // 1. FILTER ONLY ACTIVE HEALTH PROBLEMS MATCHING THIS SPECIFIC CHART
  // Separate pure positive longevity shields from genuine health hazards
  const positiveShieldIds = new Set([
    "chatterjee_parijata_longevity",
    "chatterjee_disease_free_benefic_6th",
    "chatterjee_lagna_lord_shubha_kartari",
  ]);

  const chartMatchedProblems = useMemo(() => {
    return golden_rules.filter(
      (rule) => rule.is_active && !positiveShieldIds.has(rule.id)
    );
  }, [golden_rules]);

  const activeShields = useMemo(() => {
    return golden_rules.filter(
      (rule) => rule.is_active && positiveShieldIds.has(rule.id)
    );
  }, [golden_rules]);

  // 2. IDENTIFY ALL PLANETS INVOLVED IN ACTIVE PROBLEMS / AFFLICTIONS
  const afflictedPlanets = useMemo(() => {
    const set = new Set<string>();
    chartMatchedProblems.forEach((r) => {
      (r.planets_involved || []).forEach((p) => set.add(p));
    });
    // Check diabetes affliction
    if (diabetes_assessment && diabetes_assessment.affliction_score > 0) {
      if (diabetes_assessment.venus_status.includes("Debilitated") || diabetes_assessment.venus_status.includes("Dusthana")) {
        set.add("Venus");
      }
      if (diabetes_assessment.jupiter_status.includes("Debilitated") || diabetes_assessment.jupiter_status.includes("Dusthana")) {
        set.add("Jupiter");
      }
    }
    // Check Saturn aspect on death point
    if (death_point && death_point.transit_saturn_aspect_active) {
      set.add("Saturn");
    }
    return Array.from(set);
  }, [chartMatchedProblems, diabetes_assessment, death_point]);

  // 3. FILTER ONLY AFFLICTED SAPTA DHATUS (TISSUES UNDER STRAIN IN THIS CHART)
  const strainedDhatus = useMemo(() => {
    return sapta_dhatus.filter((dhatu) => {
      // Check if planet is afflicted, in dusthana, or involved in active problems
      const isPlanetAfflicted = afflictedPlanets.includes(dhatu.governing_planet);
      const isDusthana =
        dhatu.status.includes("6") ||
        dhatu.status.includes("8") ||
        dhatu.status.includes("12") ||
        dhatu.observations_en.toLowerCase().includes("debilitat") ||
        dhatu.observations_en.toLowerCase().includes("combust") ||
        dhatu.observations_en.toLowerCase().includes("afflict");
      return isPlanetAfflicted || isDusthana;
    });
  }, [sapta_dhatus, afflictedPlanets]);

  // 4. FILTER ONLY STRAINED ENDOCRINE GLANDS FOR THIS CHART
  const strainedGlands = useMemo(() => {
    return endocrine_glands.filter((gland) => {
      return gland.governing_planets.some((p) => afflictedPlanets.includes(p));
    });
  }, [endocrine_glands, afflictedPlanets]);

  const totalProblemsCount =
    chartMatchedProblems.length +
    (death_point?.transit_saturn_aspect_active ? 1 : 0) +
    (diabetes_assessment && diabetes_assessment.risk_level !== "Low" ? 1 : 0);

  return (
    <div className="space-y-6">
      {/* Focused Header Banner */}
      <div className="rounded-2xl bg-gradient-to-r from-[#4A1640] via-[#69235B] to-[#80226D] p-5 sm:p-6 text-white shadow-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1 rounded-full bg-white/20 px-2.5 py-0.5 text-xs font-semibold backdrop-blur-xs">
                <Award className="w-3.5 h-3.5 text-amber-300" />
                {language === "ta" ? "டாக்டர் எஸ்.எஸ். சாட்டர்ஜி தொகுதி" : "Dr. S. S. Chatterjee Compendium"}
              </span>
              <span className="text-xs text-white/75">
                {language === "ta" ? "நேரடி ஜாதகப் பகுப்பாய்வு" : "Chart-Specific Diagnostics"}
              </span>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold tracking-tight">
              {language === "ta"
                ? "இந்த ஜாதகத்திற்குப் பொருந்திய மருத்துவ ஜோதிடப் பாதிப்புகள்"
                : "Health Vulnerabilities Matching This Specific Horoscope"}
            </h2>
            <p className="text-xs sm:text-sm text-white/85 max-w-2xl leading-relaxed">
              {language === "ta"
                ? "பொதுவான ஜோதிடக் குறிப்புகள் நீக்கப்பட்டு, திறக்கப்பட்டுள்ள இந்த குறிப்பிட்ட ஜாதக அமைப்பிற்கு நேரடியாகப் பொருந்தும் உடல்நலப் பாதிப்புகள், பாதிக்கப்பட்ட தாதுக்கள் மற்றும் விழிப்புணர்வு புள்ளிகள் மட்டும் கீழே தொகுக்கப்பட்டுள்ளன."
                : "Extraneous textbook data filtered out. Exclusively displaying the exact physical vulnerabilities, strained tissues, and classical health hazard combinations that match this native's chart."}
            </p>
          </div>

          <div className="shrink-0 flex items-center">
            {totalProblemsCount > 0 ? (
              <div className="rounded-xl bg-amber-500/20 border border-amber-300/30 p-3.5 text-center backdrop-blur-xs space-y-0.5">
                <div className="text-2xl font-bold text-amber-200">{totalProblemsCount}</div>
                <div className="text-2xs font-semibold uppercase tracking-wider text-amber-100">
                  {language === "ta" ? "கண்டறியப்பட்ட பாதிப்புகள்" : "Active Problem Markers"}
                </div>
              </div>
            ) : (
              <div className="rounded-xl bg-emerald-500/20 border border-emerald-300/30 p-3.5 text-center backdrop-blur-xs space-y-0.5">
                <ShieldCheck className="w-6 h-6 text-emerald-300 mx-auto" />
                <div className="text-xs font-bold text-emerald-100 mt-1">
                  {language === "ta" ? "தீவிர பாதிப்புகள் இல்லை" : "No Acute Afflictions"}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* POSITIVE CONSTITUTIONAL SHIELD (IF ACTIVE IN THIS CHART) */}
      {activeShields.length > 0 && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50/70 p-4 sm:p-5 shadow-2xs">
          <div className="flex items-start gap-3">
            <ShieldCheck className="w-5 h-5 text-emerald-700 mt-0.5 shrink-0" />
            <div className="space-y-1">
              <h4 className="text-sm font-bold text-emerald-950">
                {language === "ta"
                  ? "இயற்கை ஆயுள் & நோய் எதிர்ப்பு பலம் (Parijata / Arogya Shield)"
                  : "Natural Immunity & Vital Resistance Shield Active"}
              </h4>
              {activeShields.map((shield) => (
                <p key={shield.id} className="text-xs text-emerald-900 leading-relaxed">
                  {language === "ta" && shield.interpretation_tamil
                    ? shield.interpretation_tamil
                    : shield.traditional_interpretation}
                </p>
              ))}
              {parijata_longevity_eval && (
                <div className="text-2xs text-emerald-800 font-medium pt-1">
                  {parijata_longevity_eval}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* SECTION 1: CHART-MATCHED HEALTH PROBLEMS & HAZARDS */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-600" />
            <span>
              {language === "ta"
                ? "ஜாதகத்தில் அமைந்த தீவிர உடல்நலப் பாதிப்புகள்"
                : "Active Health Hazards Identified in This Chart"}
            </span>
          </h3>
          <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-rose-100 text-rose-800">
            {chartMatchedProblems.length} {language === "ta" ? "விதிகள் பொருந்தியுள்ளன" : "Matched"}
          </span>
        </div>

        {chartMatchedProblems.length === 0 ? (
          <div className="rounded-xl border border-gray-200 bg-white p-6 text-center space-y-2 shadow-2xs">
            <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto" />
            <h4 className="text-sm font-bold text-gray-900">
              {language === "ta"
                ? "இந்த ஜாதகத்தில் சாட்டர்ஜி குறிப்பிட்ட தீவிர நோய்க் கூட்டணிகள் ஏதுமில்லை"
                : "No Severe Classical Disease Combinations Found in This Chart"}
            </h4>
            <p className="text-xs text-gray-600 max-w-lg mx-auto leading-relaxed">
              {language === "ta"
                ? "லக்னம், 6-ம் பாவம் மற்றும் முதன்மை கிரகங்கள் கடுமையான தோஷங்கள் இன்றி இயல்பான அமைப்பில் உள்ளன. உடல் உறுப்புகள் சமநிலையான ஆற்றலுடன் விளங்குகின்றன."
                : "The Ascendant, 6th House, and key physical significators are devoid of severe malefic afflictions. Major organ systems exhibit stable functional vitality."}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3.5">
            {chartMatchedProblems.map((rule) => {
              const ruleName = language === "ta" && rule.name_tamil ? rule.name_tamil : rule.name;
              const ruleDesc =
                language === "ta" && rule.interpretation_tamil
                  ? rule.interpretation_tamil
                  : rule.traditional_interpretation;

              return (
                <div
                  key={rule.id}
                  onClick={() => onSelectRule && onSelectRule(rule)}
                  className="rounded-xl border border-rose-200 bg-gradient-to-br from-rose-50/60 via-white to-amber-50/30 p-4 sm:p-5 shadow-2xs space-y-3 hover:border-rose-300 transition-colors"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-rose-100 pb-2.5">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-rose-100 text-rose-800">
                        {rule.chapter_verse || "Advance Medical Astrology"}
                      </span>
                      {rule.anatomical_system && (
                        <span className="text-xs font-semibold px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-100">
                          {rule.anatomical_system}
                        </span>
                      )}
                    </div>
                    <span className="text-2xs font-bold px-2.5 py-0.5 rounded-full bg-rose-600 text-white self-start sm:self-auto">
                      {language === "ta" ? "ஜாதகத்தில் உறுதியானது" : "Chart Confirmed"}
                    </span>
                  </div>

                  <div>
                    <h4 className="text-base font-bold text-gray-950">{ruleName}</h4>
                    <p className="text-xs text-gray-700 mt-1.5 leading-relaxed">{ruleDesc}</p>
                  </div>

                  {rule.triggered_positions && rule.triggered_positions.length > 0 && (
                    <div className="p-2.5 rounded-lg bg-rose-100/70 border border-rose-200 text-xs text-rose-950 font-medium space-y-1">
                      <span className="font-bold flex items-center gap-1.5 text-rose-900">
                        <AlertCircle className="w-3.5 h-3.5" />
                        {language === "ta"
                          ? "இந்த ஜாதகத்தில் அமைந்துள்ள நேரடி கிரக அமைப்பு:"
                          : "Exact Planetary Placement in This Native's Chart:"}
                      </span>
                      <p className="pl-5 text-rose-900 font-mono text-2xs">
                        {rule.triggered_positions.join("; ")}
                      </p>
                    </div>
                  )}

                  {rule.planets_involved && rule.planets_involved.length > 0 && (
                    <div className="text-2xs text-gray-500 flex items-center gap-2 pt-1">
                      <span className="font-semibold text-gray-700">
                        {language === "ta" ? "சம்பந்தப்பட்ட கிரகங்கள்:" : "Planets Involved:"}
                      </span>
                      <span className="font-medium text-[#69235B]">
                        {rule.planets_involved.join(", ")}
                      </span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* SECTION 2: DEATH POINT & SATURN TRANSIT TRIGGER */}
      {death_point && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
              <Compass className="w-4 h-4 text-[#69235B]" />
              <span>
                {language === "ta"
                  ? "மிருத்யு புள்ளி & ஆயுள் விழிப்புணர்வு ஆய்வு"
                  : "Death Point & Transit Saturn Constitutional Trigger"}
              </span>
            </h3>
            <span className="text-2xs font-mono text-gray-500">
              (Asc + Sun + Moon + Jup) % 360°
            </span>
          </div>

          <div
            className={`rounded-xl border p-4 sm:p-5 shadow-2xs space-y-3 ${
              death_point.transit_saturn_aspect_active
                ? "border-amber-300 bg-amber-50/70"
                : "border-gray-200 bg-white"
            }`}
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="space-y-0.5">
                <span className="text-xs text-gray-500 font-medium">
                  {language === "ta" ? "ஜாதகரின் மிருத்யு புள்ளி:" : "Native's Calculated Death Point:"}
                </span>
                <div className="text-base font-bold text-gray-900">
                  {language === "ta" ? death_point.sign_name_ta : death_point.sign_name_en}{" "}
                  {death_point.degree_in_sign.toFixed(2)}° ({death_point.nakshatra_name}{" "}
                  {language === "ta" ? `பாதம் ${death_point.nakshatra_pada}` : `Pada ${death_point.nakshatra_pada}`})
                </div>
              </div>

              <div>
                {death_point.transit_saturn_aspect_active ? (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold bg-amber-200 text-amber-950 border border-amber-300">
                    <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0" />
                    {language === "ta"
                      ? "கோச்சார சனி பார்வை உள்ளது (கூடுதல் உடல்நலக் கவனம் தேவை)"
                      : "Transit Saturn Aspect Active (Heightened Vigilance Advised)"}
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-900 border border-emerald-300">
                    <CheckCircle2 className="w-4 h-4 text-emerald-700 shrink-0" />
                    {language === "ta"
                      ? "சனி பார்வை இல்லை (ஆயுள் பலம் சீராக உள்ளது)"
                      : "No Saturn Aspect (Vital Longevity Shield Protected)"}
                  </span>
                )}
              </div>
            </div>

            <p className="text-xs text-gray-700 leading-relaxed border-t border-gray-100 pt-2.5">
              {language === "ta" ? death_point.aspect_details_ta : death_point.aspect_details_en}
            </p>
          </div>
        </div>
      )}

      {/* SECTION 3: STRAINED TISSUES (SAPTA DHATUS) IN THIS CHART */}
      {strainedDhatus.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
              <Droplets className="w-4 h-4 text-teal-600" />
              <span>
                {language === "ta"
                  ? "இந்த ஜாதகத்தில் பலவீனமடைந்துள்ள சப்த தாதுக்கள் (உடல் திசுக்கள்)"
                  : "Strained Bodily Tissues (Sapta Dhatus) in This Chart"}
              </span>
            </h3>
            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-teal-100 text-teal-800">
              {strainedDhatus.length} {language === "ta" ? "தாதுக்கள்" : "Strained"}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
            {strainedDhatus.map((dhatu) => (
              <div
                key={dhatu.dhatu_number}
                className="rounded-xl border border-teal-200 bg-white p-4 shadow-2xs space-y-2 hover:border-teal-300 transition-colors"
              >
                <div className="flex items-center justify-between border-b border-gray-100 pb-1.5">
                  <span className="text-xs font-bold text-teal-800">
                    #{dhatu.dhatu_number} {language === "ta" ? dhatu.dhatu_name_ta : dhatu.dhatu_name_en}
                  </span>
                  <span className="text-xs font-bold px-2 py-0.5 rounded bg-teal-50 text-teal-700 border border-teal-100">
                    {dhatu.governing_planet}
                  </span>
                </div>
                <p className="text-xs text-gray-600 leading-relaxed">
                  {language === "ta" ? dhatu.physiological_function_ta : dhatu.physiological_function_en}
                </p>
                <div className="p-2 rounded bg-amber-50/80 border border-amber-100 text-2xs text-amber-900">
                  <span className="font-semibold">
                    {language === "ta" ? "ஜாதகத்தில் அமைந்த நிலை: " : "Chart Observation: "}
                  </span>
                  {language === "ta" ? dhatu.observations_ta : dhatu.observations_en}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SECTION 4: DIABETES MELLITUS (MADHUMEHA) VULNERABILITY IN THIS CHART */}
      {diabetes_assessment && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
              <Pill className="w-4 h-4 text-amber-600" />
              <span>
                {language === "ta"
                  ? "சர்க்கரை நோய் (மதுமேகம்) ஜாதக ஆய்வு & இயற்கை பரிகாரங்கள்"
                  : "Diabetes Mellitus (Madhumeha) Vulnerability in This Chart"}
              </span>
            </h3>
            <span
              className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${
                diabetes_assessment.risk_level === "High"
                  ? "bg-rose-100 text-rose-800 border-rose-200"
                  : diabetes_assessment.risk_level === "Moderate"
                  ? "bg-amber-100 text-amber-800 border-amber-200"
                  : "bg-emerald-100 text-emerald-800 border-emerald-200"
              }`}
            >
              {language === "ta"
                ? `பாதிப்பு அளவு: ${diabetes_assessment.risk_level}`
                : `Risk Level: ${diabetes_assessment.risk_level}`}
            </span>
          </div>

          <div className="rounded-xl border border-amber-200 bg-amber-50/40 p-4 sm:p-5 shadow-2xs space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2.5 text-xs">
              <div className="p-2.5 rounded-lg bg-white border border-amber-100">
                <span className="text-gray-500 block text-2xs">Venus (Insulin/Sugar):</span>
                <span className="font-semibold text-gray-900">{diabetes_assessment.venus_status}</span>
              </div>
              <div className="p-2.5 rounded-lg bg-white border border-amber-100">
                <span className="text-gray-500 block text-2xs">Jupiter (Metabolism/Fat):</span>
                <span className="font-semibold text-gray-900">{diabetes_assessment.jupiter_status}</span>
              </div>
              <div className="p-2.5 rounded-lg bg-white border border-amber-100">
                <span className="text-gray-500 block text-2xs">Virgo (Abdomen Sign):</span>
                <span className="font-semibold text-gray-900">{diabetes_assessment.virgo_status}</span>
              </div>
              <div className="p-2.5 rounded-lg bg-white border border-amber-100">
                <span className="text-gray-500 block text-2xs">6th House (Roga Bhava):</span>
                <span className="font-semibold text-gray-900">{diabetes_assessment.sixth_house_status}</span>
              </div>
            </div>

            {diabetes_assessment.affliction_score > 0 ? (
              <div className="space-y-3 pt-2 border-t border-amber-200">
                <h4 className="text-xs font-bold text-amber-950 flex items-center gap-1.5 uppercase tracking-wider">
                  <Sparkles className="w-3.5 h-3.5 text-amber-700" />
                  {language === "ta"
                    ? "சாட்டர்ஜியின் இயற்கை உணவு பரிகாரங்கள் (இந்த ஜாதகத்திற்கான பரிந்துரை):"
                    : "Dr. Chatterjee's Empirical Dietetic Remedies for This Native:"}
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-amber-950">
                  {(language === "ta"
                    ? diabetes_assessment.remedial_measures_ta
                    : diabetes_assessment.remedial_measures_en
                  ).map((med, i) => (
                    <div
                      key={i}
                      className="flex items-start gap-2 p-2 rounded-lg bg-white/90 border border-amber-100 text-xs"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                      <span>{med}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-xs text-emerald-800 font-medium">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>
                  {language === "ta"
                    ? "சுக்கிரன் மற்றும் குரு வலுவாக உள்ளதால் சர்க்கரை நோய் பாதிப்புக்கான வாய்ப்புகள் மிகக் குறைவு."
                    : "Venus and Jupiter operate in stable dignity; pancreatic glycemic balance is well-buffered."}
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* SECTION 5: TARGETED NATURAL REMEDIES ONLY FOR AFFLICTED PLANETS IN THIS CHART */}
      {afflictedPlanets.length > 0 && natural_remedies && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-purple-600" />
              <span>
                {language === "ta"
                  ? "பாதிக்கப்பட்ட கிரகங்களுக்கான குறிப்பிட்ட இயற்கை பரிகாரங்கள்"
                  : "Targeted Natural Therapies for Afflicted Planets in This Chart"}
              </span>
            </h3>
            <span className="text-xs text-gray-500 font-medium">
              {afflictedPlanets.join(", ")}
            </span>
          </div>

          <div className="rounded-xl border border-purple-200 bg-purple-50/30 p-4 sm:p-5 shadow-2xs space-y-4">
            {/* Targeted Colour Therapy */}
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-purple-950 uppercase tracking-wider">
                {language === "ta"
                  ? "இந்த ஜாதகத்திற்கான வண்ண சிகிச்சை (Planetary Colour Therapy):"
                  : "Colour Therapy for Strained Grahas in This Horoscope:"}
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 text-xs">
                {afflictedPlanets.map((planet) => {
                  const rayDesc = natural_remedies.planetary_colour_therapy[planet];
                  if (!rayDesc) return null;
                  return (
                    <div
                      key={planet}
                      className="p-3 rounded-lg bg-white border border-purple-100 shadow-2xs space-y-1"
                    >
                      <div className="font-bold text-[#69235B] flex items-center justify-between">
                        <span>{planet}</span>
                        <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                      </div>
                      <p className="text-2xs text-gray-700 leading-snug">{rayDesc}</p>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Targeted Metal Charged Water */}
            <div className="space-y-2 pt-3 border-t border-purple-100">
              <h4 className="text-xs font-bold text-purple-950 uppercase tracking-wider flex items-center gap-1.5">
                <Droplet className="w-3.5 h-3.5 text-cyan-600" />
                {language === "ta"
                  ? "உலோக நீர் சிகிச்சை பரிந்துரை (Metal-Charged Waters):"
                  : "Recommended Metal-Charged Waters for Systemic Recovery:"}
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-xs">
                {afflictedPlanets.includes("Mars") || afflictedPlanets.includes("Sun") ? (
                  <div className="p-3 rounded-lg bg-white border border-cyan-100 space-y-1">
                    <span className="font-bold text-cyan-950">Copper Water (Tamra Jal):</span>
                    <p className="text-2xs text-gray-700">
                      Purifies blood and liver, balances Pitta-Agni fire, and clears abdominal sluggishness caused by Mars/Sun strain.
                    </p>
                  </div>
                ) : null}

                {afflictedPlanets.includes("Moon") || afflictedPlanets.includes("Venus") ? (
                  <div className="p-3 rounded-lg bg-white border border-cyan-100 space-y-1">
                    <span className="font-bold text-cyan-950">Silver Water (Roupya Jal):</span>
                    <p className="text-2xs text-gray-700">
                      Soothes urinary tract inflammation, cools excessive heat, and nourishes mucosal and reproductive fluids caused by Moon/Venus strain.
                    </p>
                  </div>
                ) : null}

                {afflictedPlanets.includes("Saturn") || afflictedPlanets.includes("Rahu") ? (
                  <div className="p-3 rounded-lg bg-white border border-cyan-100 space-y-1">
                    <span className="font-bold text-cyan-950">Iron / Warm Water (Lauha Jal & Luke-warm):</span>
                    <p className="text-2xs text-gray-700">
                      Drink exclusively warm boiled water; combat chronic Vata constipation and joint stiffness triggered by Saturn/Rahu.
                    </p>
                  </div>
                ) : null}

                {afflictedPlanets.includes("Jupiter") ? (
                  <div className="p-3 rounded-lg bg-white border border-cyan-100 space-y-1">
                    <span className="font-bold text-cyan-950">Gold Water (Suvarna Jal):</span>
                    <p className="text-2xs text-gray-700">
                      Enhances Ojas (cellular vital immunity), aids liver metabolism, and balances lipid assimilation under Jupiter strain.
                    </p>
                  </div>
                ) : null}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
