"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { getVastuReport, getVastuDirections } from "@/lib/api";
import {
  SavedVastuReportResponse,
  VastuEvaluationResponse,
  DirectionMetadata,
  PadaDeityMetadata,
} from "@/lib/types";
import { VastuMandala } from "@/components/vastu/VastuMandala";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  Compass,
  Home,
  Building,
  Factory,
  MapPin,
  Sparkles,
  CheckCircle,
  AlertTriangle,
  Printer,
  ArrowLeft,
  ShieldCheck,
  ShieldAlert,
  Layers,
  Award,
  Info,
  Calendar,
  RotateCw,
  Loader2,
  AlertCircle,
  Check,
} from "lucide-react";

interface ReportClientProps {
  reportId: string;
}

export default function ReportClient({ reportId }: ReportClientProps) {
  const { session, isLoading: authLoading, isAuthenticated } = useAuth();
  const [report, setReport] = useState<SavedVastuReportResponse | null>(null);
  const [directions16, setDirections16] = useState<DirectionMetadata[]>([]);
  const [padas32, setPadas32] = useState<PadaDeityMetadata[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [factorFilter, setFactorFilter] = useState<"all" | "defects" | "ideal" | "unassessed">("all");

  useEffect(() => {
    // 1. Fetch reference directions & padas
    getVastuDirections()
      .then((data) => {
        setDirections16(data.directions_16);
        setPadas32(data.padas_32);
      })
      .catch((err) => {
        console.warn("Could not load Vastu metadata:", err);
      });
  }, []);

  useEffect(() => {
    if (!authLoading) {
      if (!isAuthenticated || !session?.access_token) {
        setError("You must be logged in to access saved Vastu assessment reports.");
        setLoading(false);
        return;
      }

      getVastuReport(session.access_token, reportId)
        .then((data) => {
          setReport(data);
        })
        .catch((err) => {
          setError(err?.data?.detail || err?.message || "Failed to load saved Vastu assessment.");
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [reportId, session?.access_token, isAuthenticated, authLoading]);

  const handlePrint = () => {
    if (typeof window !== "undefined") {
      window.print();
    }
  };

  if (loading || authLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <Loader2 className="w-8 h-8 mx-auto animate-spin text-blue-600 mb-3" />
        <p className="text-sm text-slate-500">
          Loading saved Vastu assessment report #{reportId.slice(0, 8)}...
        </p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center space-y-4">
        <div className="w-12 h-12 mx-auto rounded-full bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-600">
          <AlertCircle className="w-6 h-6" />
        </div>
        <h2 className="font-serif text-xl font-bold text-slate-900">Report Unavailable</h2>
        <p className="text-xs text-slate-500 max-w-md mx-auto">{error}</p>
        <div className="pt-2">
          <Link
            href="/vastu"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-white bg-slate-900 hover:bg-slate-800"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Return to Vastu Module</span>
          </Link>
        </div>
      </div>
    );
  }

  // The stored evaluation payload
  const evalData: VastuEvaluationResponse = (report.calculation_data as VastuEvaluationResponse) || {};
  const score = report.compliance_score ?? evalData.compliance_score ?? 0;
  const grade = evalData.score_grade || (score >= 80 ? "Excellent" : score >= 60 ? "Favorable" : "Moderate");
  const factors = evalData.factor_results || [];
  const doshas = evalData.doshas || report.dosha_evaluations || [];
  const remedies = evalData.general_remedies || report.remedy_recommendations || [];
  const astro = evalData.astro_overlay;

  const filteredFactors = factors.filter((f) => {
    if (factorFilter === "defects") {
      return f.severity === "moderate_defect" || f.severity === "severe_defect";
    }
    if (factorFilter === "ideal") {
      return f.severity === "ideal" || f.severity === "acceptable";
    }
    if (factorFilter === "unassessed") {
      return !f.assessed || f.severity === "unassessed";
    }
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-8 print:p-0 print:m-0 print:max-w-full">
      {/* Breadcrumb Navigation (Hidden in Print) */}
      <div className="print:hidden">
        <Breadcrumbs
          items={[
            { label: "Home", href: "/" },
            { label: "Dashboard", href: "/dashboard" },
            { label: "Vastu Shastra", href: "/vastu" },
            { label: `Report VASTU-#${report.display_number}` },
          ]}
        />
      </div>

      {/* Report Header Card */}
      <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm p-6 sm:p-8 space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 pb-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full font-bold text-xs">
                VASTU-#{report.display_number}
              </span>
              <span className="px-3 py-1 bg-slate-100 text-slate-700 rounded-full font-semibold text-xs capitalize flex items-center gap-1">
                {report.property_type === "residential" && <Home className="w-3.5 h-3.5" />}
                {report.property_type === "commercial" && <Building className="w-3.5 h-3.5" />}
                {report.property_type === "plot" && <MapPin className="w-3.5 h-3.5" />}
                {report.property_type === "industrial" && <Factory className="w-3.5 h-3.5" />}
                {report.property_type} Property
              </span>
              <span className="px-3 py-1 bg-amber-50 text-amber-800 border border-amber-200 rounded-full font-semibold text-xs">
                Facing: {report.facing_direction}
                {report.facing_degrees != null && ` (${report.facing_degrees}°)`}
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              {report.property_name}
            </h1>
            <p className="text-xs sm:text-sm text-slate-500">
              Evaluated on {new Date(report.created_at).toLocaleDateString()} at{" "}
              {new Date(report.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              {" · "}Engine v{report.engine_version || "1.0.0"} · Rubric v{evalData.rubric_version || "1.0.0"}
            </p>
          </div>

          {/* Action Buttons (Hidden in Print) */}
          <div className="flex items-center gap-2 print:hidden">
            <button
              onClick={handlePrint}
              className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-bold shadow-xs transition-all cursor-pointer"
            >
              <Printer className="w-4 h-4 text-slate-500" />
              <span>Print / PDF</span>
            </button>
            <Link
              href="/vastu"
              className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shadow-xs transition-all"
            >
              <RotateCw className="w-4 h-4" />
              <span>New Assessment</span>
            </Link>
          </div>
        </div>

        {/* Score & Key Findings Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-stretch">
          {/* Main Score Gauge */}
          <div className="rounded-2xl border border-slate-200/80 bg-gradient-to-br from-slate-50 to-blue-50/30 p-6 flex flex-col justify-between items-center text-center space-y-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Deterministic Vastu Score
            </span>
            <div className="relative flex items-center justify-center w-28 h-28">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                <path
                  className="text-slate-200"
                  strokeWidth="3.5"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <path
                  className={
                    score >= 75
                      ? "text-emerald-500"
                      : score >= 50
                      ? "text-amber-500"
                      : "text-rose-500"
                  }
                  strokeDasharray={`${score}, 100`}
                  strokeLinecap="round"
                  strokeWidth="3.5"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
              </svg>
              <div className="absolute flex flex-col items-center">
                <span className="text-3xl font-extrabold text-slate-900">{score}</span>
                <span className="text-[10px] text-slate-400 font-semibold">/ 100</span>
              </div>
            </div>
            <div>
              <span
                className={`inline-block px-3 py-1 rounded-full text-xs font-bold ${
                  score >= 75
                    ? "bg-emerald-100 text-emerald-800"
                    : score >= 50
                    ? "bg-amber-100 text-amber-800"
                    : "bg-rose-100 text-rose-800"
                }`}
              >
                {grade}
              </span>
            </div>
            <p className="text-[11px] text-slate-500 max-w-xs">
              Normalized strictly across {evalData.factors_assessed || factors.filter(f => f.assessed).length} assessed factors.
            </p>
          </div>

          {/* Assessment Breakdown Summary */}
          <div className="rounded-2xl border border-slate-200/80 bg-white p-6 space-y-4 flex flex-col justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Factor Coverage Metrics
            </h3>
            <div className="space-y-3 text-xs">
              <div className="flex justify-between items-center py-1.5 border-b border-slate-100">
                <span className="text-slate-600">Assessed Elements</span>
                <span className="font-bold text-slate-900">
                  {evalData.factors_assessed || 0} of {evalData.factors_total || factors.length}
                </span>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-slate-100">
                <span className="text-slate-600">Ideal Placements</span>
                <span className="font-bold text-emerald-600">
                  {factors.filter((f) => f.severity === "ideal").length}
                </span>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-slate-100">
                <span className="text-slate-600">Acceptable Placements</span>
                <span className="font-bold text-blue-600">
                  {factors.filter((f) => f.severity === "acceptable").length}
                </span>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-slate-100">
                <span className="text-slate-600">Defects / Inauspicious</span>
                <span className="font-bold text-rose-600">
                  {factors.filter((f) => f.severity === "moderate_defect" || f.severity === "severe_defect").length}
                </span>
              </div>
              <div className="flex justify-between items-center py-1.5">
                <span className="text-slate-600">Unassessed / Missing</span>
                <span className="font-bold text-slate-400">
                  {factors.filter((f) => !f.assessed || f.severity === "unassessed").length}
                </span>
              </div>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200/60 text-[11px] text-slate-600 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>Unassessed factors were excluded from score calculations without penalty.</span>
            </div>
          </div>

          {/* Dosha & Defect Alert */}
          <div className="rounded-2xl border border-slate-200/80 bg-white p-6 space-y-4 flex flex-col justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Spatial Dosha Status
            </h3>
            {doshas.length > 0 ? (
              <div className="space-y-3">
                <div className="p-3 rounded-xl bg-rose-50 border border-rose-200/80 flex items-start gap-2.5">
                  <ShieldAlert className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold text-rose-900 text-xs block">
                      {doshas.length} Spatial Dosha{doshas.length > 1 ? "s" : ""} Identified
                    </span>
                    <p className="text-[11px] text-rose-700 mt-0.5 leading-relaxed">
                      Classical texts (*Mayamata* & *Manasara*) require specific remedial harmonization for these zones.
                    </p>
                  </div>
                </div>
                <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
                  {doshas.map((d: any, idx: number) => (
                    <div
                      key={idx}
                      className="px-2.5 py-1.5 rounded-lg bg-slate-50 border border-slate-200/60 text-[11px] flex justify-between items-center"
                    >
                      <span className="font-semibold text-slate-800">{d.dosha_name || d.name}</span>
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-bold uppercase bg-rose-100 text-rose-800">
                        {d.severity}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center py-6 space-y-2">
                <div className="w-12 h-12 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto">
                  <CheckCircle className="w-6 h-6" />
                </div>
                <h4 className="font-bold text-slate-800 text-sm">Harmonious Alignment</h4>
                <p className="text-[11px] text-slate-500 max-w-xs mx-auto">
                  No major classical spatial doshas (Ishanya, Agneya, or Nairruti corruptions) were detected in this configuration.
                </p>
              </div>
            )}
            <div className="text-[11px] text-slate-500 border-t border-slate-100 pt-2 flex items-center gap-1.5">
              <Info className="w-3.5 h-3.5 text-blue-500" />
              <span>Remedies detailed below for every non-ideal zone.</span>
            </div>
          </div>
        </div>
      </div>

      {/* Warnings & Non-Penalization Notices (if any) */}
      {(evalData.missing_data_warnings?.length > 0 || evalData.conflicting_input_warnings?.length > 0) && (
        <div className="rounded-2xl border border-amber-200 bg-amber-50/70 p-5 space-y-2 text-xs">
          <div className="flex items-center gap-2 font-bold text-amber-900">
            <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
            <span>Assessment Scope &amp; Input Notices:</span>
          </div>
          <ul className="list-disc list-inside space-y-1 text-amber-800 text-[11px]">
            {evalData.missing_data_warnings?.map((w, idx) => (
              <li key={`mis-${idx}`}>{w}</li>
            ))}
            {evalData.conflicting_input_warnings?.map((w, idx) => (
              <li key={`cnf-${idx}`}>{w}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Interactive Vastu Purusha Mandala Visualizer */}
      <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm p-6 sm:p-8 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div>
            <h3 className="text-lg font-bold text-slate-900">
              Paramasayika Mandala (9×9) Directional Alignment
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Highlighting property facing direction ({report.facing_direction}) and cardinal deity padas.
            </p>
          </div>
          <span className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-semibold">
            <Compass className="w-3.5 h-3.5" />
            <span>Interactive Visualizer</span>
          </span>
        </div>

        <VastuMandala
          directions={directions16}
          padas={padas32}
          highlightDirection={report.facing_direction}
          favorableDirections={astro?.favorable_directions || []}
        />
      </div>

      {/* Astro-Vastu Personalized Overlay (If Present) */}
      {astro && (
        <div className="rounded-3xl border border-indigo-200/80 bg-gradient-to-br from-indigo-50/60 to-purple-50/30 p-6 sm:p-8 shadow-sm space-y-5">
          <div className="flex items-center gap-3 border-b border-indigo-100 pb-4">
            <div className="w-10 h-10 rounded-2xl bg-indigo-600 text-white flex items-center justify-center shadow-xs">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-indigo-950">
                Astro-Vastu Resident Chart Integration
              </h3>
              <p className="text-xs text-indigo-800">
                Calculated natively with precision XALEN ephemeris core (no fallback assumptions).
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="p-4 rounded-xl bg-white border border-indigo-100 space-y-1.5">
              <span className="text-[11px] font-semibold text-slate-400 block uppercase">
                Resident Lagna (Ascendant)
              </span>
              <p className="text-base font-bold text-indigo-950">{astro.lagna_sign}</p>
              <p className="text-[11px] text-slate-500">Governing Planet: {astro.lagna_ruler}</p>
            </div>

            <div className="p-4 rounded-xl bg-white border border-indigo-100 space-y-1.5">
              <span className="text-[11px] font-semibold text-slate-400 block uppercase">
                Auspicious Facing Directions
              </span>
              <div className="flex flex-wrap gap-1 pt-0.5">
                {astro.favorable_directions.map((d, i) => (
                  <span
                    key={i}
                    className="px-2 py-0.5 rounded-md bg-emerald-100 text-emerald-800 font-bold text-xs"
                  >
                    {d}
                  </span>
                ))}
              </div>
              <p className="text-[11px] text-slate-500">Strengthens vitality and prosperity.</p>
            </div>

            <div className="p-4 rounded-xl bg-white border border-indigo-100 space-y-1.5">
              <span className="text-[11px] font-semibold text-slate-400 block uppercase">
                Directions Requiring Remediation
              </span>
              <div className="flex flex-wrap gap-1 pt-0.5">
                {astro.unfavorable_directions.map((d, i) => (
                  <span
                    key={i}
                    className="px-2 py-0.5 rounded-md bg-rose-100 text-rose-800 font-bold text-xs"
                  >
                    {d}
                  </span>
                ))}
              </div>
              <p className="text-[11px] text-slate-500">Neutralize with elemental remedies.</p>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-white/80 border border-indigo-100 space-y-2 text-xs">
            <span className="font-bold text-indigo-950">Planetary &amp; Elemental Resonance:</span>
            <p className="text-slate-600 text-[11px] leading-relaxed">{astro.elemental_synergy}</p>
            {astro.planetary_zone_notes?.length > 0 && (
              <div className="pt-2 border-t border-indigo-50 space-y-1">
                {astro.planetary_zone_notes.map((note, idx) => (
                  <p key={idx} className="text-slate-600 text-[11px]">
                    • {note}
                  </p>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Factor-by-Factor Comprehensive Evaluation */}
      <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm p-6 sm:p-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
          <div>
            <h3 className="text-lg font-bold text-slate-900">
              Factor-by-Factor Evaluation &amp; Classical Rules
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Specific Vedic citations (*Mayamata*, *Manasara*, *Brihat Samhita*) and remedial recommendations.
            </p>
          </div>

          {/* Filter Pills (Hidden in Print) */}
          <div className="flex items-center gap-1.5 bg-slate-100 p-1 rounded-xl text-xs print:hidden">
            <button
              onClick={() => setFactorFilter("all")}
              className={`px-3 py-1 rounded-lg font-semibold transition-all ${
                factorFilter === "all" ? "bg-white text-slate-900 shadow-xs" : "text-slate-600 hover:text-slate-900"
              }`}
            >
              All ({factors.length})
            </button>
            <button
              onClick={() => setFactorFilter("ideal")}
              className={`px-3 py-1 rounded-lg font-semibold transition-all ${
                factorFilter === "ideal" ? "bg-white text-slate-900 shadow-xs" : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Favorable
            </button>
            <button
              onClick={() => setFactorFilter("defects")}
              className={`px-3 py-1 rounded-lg font-semibold transition-all ${
                factorFilter === "defects" ? "bg-white text-rose-700 shadow-xs" : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Defects
            </button>
            <button
              onClick={() => setFactorFilter("unassessed")}
              className={`px-3 py-1 rounded-lg font-semibold transition-all ${
                factorFilter === "unassessed" ? "bg-white text-slate-700 shadow-xs" : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Unassessed
            </button>
          </div>
        </div>

        {/* Factors Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredFactors.map((f, idx) => (
            <div
              key={idx}
              className={`p-5 rounded-2xl border transition-all space-y-3.5 text-xs ${
                f.severity === "ideal"
                  ? "border-emerald-200 bg-emerald-50/20"
                  : f.severity === "acceptable"
                  ? "border-blue-200 bg-blue-50/20"
                  : f.severity === "moderate_defect"
                  ? "border-amber-200 bg-amber-50/30"
                  : f.severity === "severe_defect"
                  ? "border-rose-200 bg-rose-50/30"
                  : "border-slate-200 bg-slate-50/40"
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h4 className="font-bold text-sm text-slate-900">{f.factor_name}</h4>
                  <span className="text-[11px] text-slate-500 font-medium">
                    Placed: {f.input_value || "Not Assessed"}
                  </span>
                </div>

                <div className="flex items-center gap-1.5 shrink-0">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                      f.severity === "ideal"
                        ? "bg-emerald-100 text-emerald-800"
                        : f.severity === "acceptable"
                        ? "bg-blue-100 text-blue-800"
                        : f.severity === "moderate_defect"
                        ? "bg-amber-100 text-amber-800"
                        : f.severity === "severe_defect"
                        ? "bg-rose-100 text-rose-800"
                        : "bg-slate-200 text-slate-700"
                    }`}
                  >
                    {f.severity.replace("_", " ")}
                  </span>
                  <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-800 font-bold text-[10px]">
                    {f.score != null ? `${f.score}/${f.max_weight} pts` : "0 pts (unassessed)"}
                  </span>
                </div>
              </div>

              <div className="space-y-1.5 text-[11px]">
                <p className="text-slate-700 leading-relaxed">{f.explanation}</p>
                <p className="text-slate-500 italic">
                  <strong>Classical Rule ({f.rule_source}):</strong> {f.traditional_rule}
                </p>
              </div>

              {f.remedy && f.severity !== "ideal" && (
                <div className="pt-2.5 border-t border-slate-200/80 space-y-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-amber-900 flex items-center gap-1">
                    <Sparkles className="w-3 h-3 text-amber-600" />
                    Traditional Remedial Action:
                  </span>
                  <p className="text-[11px] text-slate-700 leading-relaxed">{f.remedy}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* General Remedial Recommendations Matrix */}
      {remedies.length > 0 && (
        <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm p-6 sm:p-8 space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-4">
            <Sparkles className="w-5 h-5 text-amber-600" />
            <h3 className="text-lg font-bold text-slate-900">
              Traditional Remedial Guidance Matrix
            </h3>
          </div>
          <p className="text-xs text-slate-500">
            Remedies derived from classical Vastu treatises for non-destructive energy harmonization.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            {remedies.map((rem: string, idx: number) => (
              <div
                key={idx}
                className="p-3.5 rounded-xl border border-amber-200/70 bg-amber-50/20 text-slate-800 flex items-start gap-2.5 leading-relaxed"
              >
                <span className="w-5 h-5 rounded-full bg-amber-100 text-amber-800 font-bold text-[10px] flex items-center justify-center shrink-0 mt-0.5">
                  {idx + 1}
                </span>
                <span className="text-[11px]">{rem}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Classical Academic & Heritage Disclaimer */}
      <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5 text-xs text-slate-500 space-y-2 leading-relaxed">
        <div className="flex items-center gap-1.5 font-bold text-slate-700">
          <Info className="w-4 h-4 text-blue-500 shrink-0" />
          <span>Classical Heritage &amp; Educational Notice</span>
        </div>
        <p className="text-[11px] leading-relaxed">
          {evalData.disclaimer ||
            "Disclaimer: Vastu Shastra principles presented herein represent classical architectural and cultural traditions (primarily Mayamata, Manasara, and Brihat Samhita) and are provided for cultural, educational, and heritage reference purposes only. They do not constitute structural engineering, legal, or guaranteed life outcomes."}
        </p>
      </div>
    </div>
  );
}
