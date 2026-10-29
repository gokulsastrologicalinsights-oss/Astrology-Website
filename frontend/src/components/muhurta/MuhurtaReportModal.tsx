"use client";

import React, { useRef } from "react";
import { useLanguage } from "@/lib/i18n";
import {
  Compass,
  Printer,
  X,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  ShieldCheck,
  Calendar,
  Clock,
  MapPin,
  Sparkles,
  Layers,
  Heart,
  FileText,
} from "lucide-react";

interface MuhurtaReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  reportData: {
    title?: string;
    occasion_name: string;
    client_name?: string | null;
    event_date: string;
    start_time_local: string;
    end_time_local: string;
    duration_minutes: number;
    location_name: string;
    latitude: number;
    longitude: number;
    timezone: string;
    score: number;
    status: string;
    explanation: string;
    tithi: {
      number: number;
      name: string;
      name_ta?: string;
      paksha: string;
      start_time_local?: string;
      end_time_local?: string;
    };
    nakshatra: {
      number: number;
      name: string;
      name_ta?: string;
      lord: string;
      pada: number;
      start_time_local?: string;
      end_time_local?: string;
    };
    yoga?: { number: number; name: string };
    karana?: { number: number; name: string };
    ascendant: {
      sign_index: number;
      sign_name: string;
      sign_name_ta: string;
      degree_in_sign: number;
      nakshatra?: string;
    };
    passed_rules: Array<{ rule: string; message: string }>;
    failed_rules?: Array<{ rule: string; severity?: string; message: string }>;
    advisories?: Array<{ rule: string; message: string }>;
    incomplete_checks?: Array<{ check: string; message: string }>;
    inauspicious_periods?: Record<string, any>;
    notes?: string | null;
    ayanamsa_name?: string;
  };
}

export function MuhurtaReportModal({ isOpen, onClose, reportData }: MuhurtaReportModalProps) {
  const { language } = useLanguage();
  const printAreaRef = useRef<HTMLDivElement>(null);

  if (!isOpen || !reportData) return null;

  const handlePrint = () => {
    window.print();
  };

  const getStatusBadge = () => {
    switch (reportData.status) {
      case "meets_configured_rules":
        return {
          bg: "bg-emerald-50 text-emerald-700 border-emerald-200",
          label: language === "ta" ? "முழுமையான சுப முகூர்த்தம்" : "Pristine Auspicious Window",
        };
      case "meets_rules_with_advisories":
        return {
          bg: "bg-amber-50 text-amber-700 border-amber-200",
          label: language === "ta" ? "சுப முகூர்த்தம் (ஆலோசனைகளுடன்)" : "Meets Rules with Advisories",
        };
      case "incomplete":
        return {
          bg: "bg-purple-50 text-purple-700 border-purple-200",
          label: language === "ta" ? "பிறப்பு விவரங்கள் தேவை" : "Incomplete (Birth Data Missing)",
        };
      default:
        return {
          bg: "bg-rose-50 text-rose-700 border-rose-200",
          label: language === "ta" ? "விதி விலக்குகள் உள்ளன" : "Fails Mandatory Rules",
        };
    }
  };

  const statusBadge = getStatusBadge();

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-6 print:p-0 print:bg-white">
      <div className="relative w-full max-w-5xl bg-white rounded-3xl shadow-2xl border border-[#DDE5F0] overflow-hidden flex flex-col max-h-[92vh] print:max-h-none print:shadow-none print:border-none">
        {/* Modal Top Bar (Hidden on print) */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#DDE5F0] bg-[#F8FAFC] print:hidden">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-[#B8862B]" />
            <span className="font-serif font-bold text-sm text-[#102A4C]">
              {language === "ta" ? "முகூர்த்த சான்றிதழ் & அறிக்கை" : "Official Muhurta Calculation Report"}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handlePrint}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#102A4C] hover:bg-[#1E3A61] text-white text-xs font-semibold shadow-xs transition-colors cursor-pointer"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>{language === "ta" ? "அச்சிடுக / PDF" : "Print / PDF"}</span>
            </button>
            <button
              type="button"
              onClick={onClose}
              className="p-1.5 rounded-xl text-[#64748B] hover:text-[#102A4C] hover:bg-[#E2E8F0] transition-colors cursor-pointer"
              aria-label="Close modal"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Printable Report Body */}
        <div ref={printAreaRef} className="p-6 sm:p-10 overflow-y-auto space-y-8 text-[#102A4C] print:p-4">
          {/* 1. Branded Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-6 border-b-2 border-[#102A4C] gap-4">
            <div className="flex items-center gap-3.5">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#102A4C] via-[#1E3A61] to-[#3478F6] flex items-center justify-center text-white shadow-sm border border-[#3478F6]/30">
                <Compass className="w-6 h-6 text-[#FAF2DE]" />
              </div>
              <div>
                <h1 className="font-serif text-xl sm:text-2xl font-bold tracking-tight text-[#102A4C] leading-tight">
                  Gokul&apos;s Astrological Insights
                </h1>
                <p className="text-xs text-[#52667E] font-medium">
                  {language === "ta"
                    ? "துல்லிய வேத வானியல் முகூர்த்த சான்றிதழ்"
                    : "Precision Vedic Astronomical Muhurta Certificate"}
                </p>
              </div>
            </div>

            <div className="text-left sm:text-right space-y-1">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold border ${statusBadge.bg}`}>
                {statusBadge.label}
              </span>
              <div className="text-[11px] text-[#64748B]">
                Score: <strong className="text-[#102A4C]">{reportData.score}/100</strong> (Rule-based)
              </div>
            </div>
          </div>

          {/* 2. Key Timing Banner */}
          <div className="p-5 rounded-2xl bg-gradient-to-br from-[#F8FAFC] to-[#EFF6FF] border border-[#BFDBFE] space-y-2">
            <div className="text-xs font-bold uppercase tracking-wider text-[#3478F6]">
              {reportData.occasion_name}
            </div>
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
              <div>
                <div className="font-serif text-2xl sm:text-3xl font-bold text-[#102A4C]">
                  {reportData.start_time_local} — {reportData.end_time_local}
                </div>
                <div className="text-xs sm:text-sm text-[#52667E] font-medium flex items-center gap-2 mt-1">
                  <Calendar className="w-3.5 h-3.5 text-[#B8862B]" />
                  <span>{reportData.event_date}</span>
                  <span>•</span>
                  <Clock className="w-3.5 h-3.5 text-[#3478F6]" />
                  <span>{reportData.duration_minutes} Minutes Duration</span>
                </div>
              </div>

              <div className="text-xs text-[#52667E] space-y-1 md:text-right">
                <div className="flex items-center md:justify-end gap-1 font-semibold text-[#102A4C]">
                  <MapPin className="w-3.5 h-3.5 text-rose-500" />
                  <span>{reportData.location_name}</span>
                </div>
                <div className="text-[11px] text-[#64748B]">
                  Coords: {reportData.latitude.toFixed(4)}° N, {reportData.longitude.toFixed(4)}° E ({reportData.timezone})
                </div>
                {reportData.client_name && (
                  <div className="text-xs font-bold text-[#102A4C]">
                    Beneficiary: {reportData.client_name}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 3. Four Core Pillars Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Pillar 1: Tithi */}
            <div className="p-4 rounded-xl border border-[#DDE5F0] bg-[#FAF8F5] space-y-1">
              <span className="text-[11px] font-bold uppercase text-[#8C6D23]">திதி / Tithi</span>
              <div className="text-sm font-bold text-[#102A4C]">{reportData.tithi.name}</div>
              <div className="text-[11px] text-[#52667E]">
                {reportData.tithi.paksha} Paksha (#{reportData.tithi.number})
              </div>
            </div>

            {/* Pillar 2: Nakshatra */}
            <div className="p-4 rounded-xl border border-[#DDE5F0] bg-[#FAF8F5] space-y-1">
              <span className="text-[11px] font-bold uppercase text-[#8C6D23]">நட்சத்திரம் / Nakshatra</span>
              <div className="text-sm font-bold text-[#102A4C]">{reportData.nakshatra.name}</div>
              <div className="text-[11px] text-[#52667E]">
                Pada {reportData.nakshatra.pada} • Lord: {reportData.nakshatra.lord}
              </div>
            </div>

            {/* Pillar 3: Ascendant / Lagna */}
            <div className="p-4 rounded-xl border border-[#DDE5F0] bg-[#FAF8F5] space-y-1">
              <span className="text-[11px] font-bold uppercase text-[#8C6D23]">லக்னம் / Ascendant</span>
              <div className="text-sm font-bold text-[#102A4C]">
                {reportData.ascendant.sign_name} ({reportData.ascendant.sign_name_ta})
              </div>
              <div className="text-[11px] text-[#52667E]">
                Degree: {reportData.ascendant.degree_in_sign}° in Sign
              </div>
            </div>

            {/* Pillar 4: Yoga & Karana */}
            <div className="p-4 rounded-xl border border-[#DDE5F0] bg-[#FAF8F5] space-y-1">
              <span className="text-[11px] font-bold uppercase text-[#8C6D23]">யோகம் &amp; கரணம்</span>
              <div className="text-sm font-bold text-[#102A4C]">
                {reportData.yoga?.name || "Auspicious"}
              </div>
              <div className="text-[11px] text-[#52667E]">
                Karana: {reportData.karana?.name || "Standard"}
              </div>
            </div>
          </div>

          {/* 4. Rule Evaluation Audit */}
          <div className="space-y-4">
            <h3 className="font-serif text-base font-bold text-[#102A4C] pb-2 border-b border-[#DDE5F0] flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>{language === "ta" ? "விதிமுறை தணிக்கை மற்றும் பலன்கள்" : "Traditional Rule Compliance Audit"}</span>
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              {/* Passed Rules */}
              <div className="space-y-2">
                <span className="font-bold text-emerald-700 text-[11px] uppercase tracking-wider">
                  Satisfied Criteria ({reportData.passed_rules.length})
                </span>
                <ul className="space-y-1.5">
                  {reportData.passed_rules.map((r, i) => (
                    <li key={i} className="flex items-start gap-2 p-2 rounded-lg bg-emerald-50/60 border border-emerald-100">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                      <div>
                        <strong className="text-[#102A4C]">{r.rule}: </strong>
                        <span className="text-[#52667E]">{r.message}</span>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Advisories & Failed Rules */}
              <div className="space-y-2">
                <span className="font-bold text-[#52667E] text-[11px] uppercase tracking-wider">
                  Advisories &amp; Prohibitions ({((reportData.advisories?.length || 0) + (reportData.failed_rules?.length || 0))})
                </span>
                <ul className="space-y-1.5">
                  {reportData.failed_rules?.map((f, i) => (
                    <li key={`fail-${i}`} className="flex items-start gap-2 p-2 rounded-lg bg-rose-50 border border-rose-200">
                      <AlertTriangle className="w-3.5 h-3.5 text-rose-600 shrink-0 mt-0.5" />
                      <div>
                        <strong className="text-rose-900">{f.rule}: </strong>
                        <span className="text-rose-700">{f.message}</span>
                      </div>
                    </li>
                  ))}

                  {reportData.advisories?.map((a, i) => (
                    <li key={`adv-${i}`} className="flex items-start gap-2 p-2 rounded-lg bg-amber-50 border border-amber-200">
                      <HelpCircle className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
                      <div>
                        <strong className="text-amber-900">{a.rule}: </strong>
                        <span className="text-amber-700">{a.message}</span>
                      </div>
                    </li>
                  ))}

                  {reportData.incomplete_checks?.map((ic, i) => (
                    <li key={`inc-${i}`} className="flex items-start gap-2 p-2 rounded-lg bg-purple-50 border border-purple-200">
                      <HelpCircle className="w-3.5 h-3.5 text-purple-600 shrink-0 mt-0.5" />
                      <div>
                        <strong className="text-purple-900">{ic.check}: </strong>
                        <span className="text-purple-700">{ic.message}</span>
                      </div>
                    </li>
                  ))}

                  {(!reportData.failed_rules?.length && !reportData.advisories?.length && !reportData.incomplete_checks?.length) && (
                    <li className="p-3 text-center text-[#52667E] bg-[#F8FAFC] rounded-lg border border-[#E2E8F0]">
                      No disqualifying conditions or negative advisories identified.
                    </li>
                  )}
                </ul>
              </div>
            </div>
          </div>

          {/* 5. Astrological Notes / Custom Remarks */}
          {reportData.notes && (
            <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#DDE5F0] space-y-1 text-xs">
              <span className="font-bold text-[#102A4C]">Astrologer Remarks / Notes:</span>
              <p className="text-[#52667E] leading-relaxed">{reportData.notes}</p>
            </div>
          )}

          {/* 6. Scientific Provenance & Certification */}
          <div className="pt-6 border-t border-[#DDE5F0] flex flex-col sm:flex-row sm:items-center justify-between text-[11px] text-[#64748B] gap-2">
            <div>
              <strong>Calculation Convention:</strong> {reportData.ayanamsa_name || "Chitrapaksha Lahiri Ayanamsa"} • True Solar Horizon
            </div>
            <div className="sm:text-right">
              Validated by <strong>Gokul&apos;s Astrological Insights</strong> Ephemeris Engine
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
