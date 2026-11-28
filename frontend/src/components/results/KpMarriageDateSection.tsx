"use client";

import React, { useState, useCallback, useEffect, useRef } from "react";
import {
  HoroscopeResponse,
  KpMarriageDateResponse,
  BirthInput,
} from "@/lib/types";
import { findKpMarriageDate } from "@/lib/api";
import { useLanguage } from "@/lib/i18n";
import { formatDate } from "@/lib/formatters";
import {
  Heart,
  Calendar,
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Compass,
  RefreshCw,
  Info,
} from "lucide-react";

interface KpMarriageDateSectionProps {
  horoscope?: HoroscopeResponse;
  savedHoroscopeId?: string;
}

export function KpMarriageDateSection({
  horoscope,
  savedHoroscopeId,
}: KpMarriageDateSectionProps) {
  const { language } = useLanguage();
  const isTa = language === "ta";

  const todayIso = new Date().toISOString().slice(0, 10);
  const [startDate, setStartDate] = useState<string>(todayIso);
  const [yearsAhead, setYearsAhead] = useState<number>(2);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<KpMarriageDateResponse | null>(null);
  const hasAutoFetchedRef = useRef<boolean>(false);

  const buildBirthInput = useCallback((): BirthInput | undefined => {
    const meta = horoscope?.metadata;
    if (!meta?.birth_utc_iso) return undefined;
    const utcMs = Date.parse(meta.birth_utc_iso);
    if (Number.isNaN(utcMs)) return undefined;
    const offsetHours = typeof meta.utc_offset_hours === "number" ? meta.utc_offset_hours : 5.5;
    const localDate = new Date(utcMs + offsetHours * 3600 * 1000);
    const iso = localDate.toISOString();
    return {
      birth_date: iso.slice(0, 10),
      birth_time: iso.slice(11, 19),
      latitude: Number(meta.coordinates?.latitude ?? 13.0827),
      longitude: Number(meta.coordinates?.longitude ?? 80.2707),
      timezone: meta.local_timezone || "Asia/Kolkata",
    };
  }, [horoscope]);

  const handleCalculate = useCallback(async () => {
    const birth = buildBirthInput();
    if (!birth && !savedHoroscopeId) {
      setError(
        isTa
          ? "பிறப்பு விவரங்கள் கிடைக்கவில்லை."
          : "Birth details are unavailable for this horoscope."
      );
      return;
    }

    setLoading(true);
    setError(null);
    const timeoutPromise = new Promise<never>((_, reject) =>
      setTimeout(
        () =>
          reject(
            new Error(
              isTa
                ? "கணக்கீடு நேரம் முடிந்தது (30 வினாடிகள்). பின்தள சர்வர் இயங்குகிறதா என சரிபார்க்கவும்."
                : "Request timed out after 30s. Please ensure the backend server is running and updated."
            )
          ),
        30000
      )
    );
    try {
      const data = await Promise.race([
        findKpMarriageDate({
          birth,
          saved_horoscope_id: birth ? undefined : savedHoroscopeId,
          start_date: startDate,
          years_ahead: yearsAhead,
          ayanamsa_id: 1,
        }),
        timeoutPromise,
      ]);
      setResult(data);
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : isTa
          ? "கணக்கீட்டில் பிழை ஏற்பட்டது."
          : "Failed to compute KP marriage dates.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [buildBirthInput, savedHoroscopeId, startDate, yearsAhead, isTa]);

  useEffect(() => {
    if (hasAutoFetchedRef.current) return;
    if (horoscope?.metadata?.birth_utc_iso || savedHoroscopeId) {
      hasAutoFetchedRef.current = true;
      handleCalculate();
    }
  }, [horoscope?.metadata?.birth_utc_iso, savedHoroscopeId, handleCalculate]);

  const verdictBadgeClass = (verdict: string) => {
    if (verdict === "Strong") return "bg-emerald-100 text-emerald-800 border-emerald-300";
    if (verdict === "Moderate") return "bg-amber-100 text-amber-800 border-amber-300";
    return "bg-rose-100 text-rose-800 border-rose-300";
  };

  return (
    <div className="space-y-6">
      {/* Header & Search Controls */}
      <div className="p-4 sm:p-5 rounded-xl bg-gradient-to-r from-rose-50 via-amber-50/70 to-purple-50 border border-rose-200/80 shadow-xs">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <h3 className="text-base sm:text-lg font-bold text-[#0F172A] flex items-center gap-2">
              <Heart className="w-5 h-5 text-rose-600" />
              <span>
                {isTa
                  ? "KP திருமண கொடுப்பினை & தேதி கணிப்பு"
                  : "KP Marriage Promise, Timing & Date Finder"}
              </span>
            </h3>
            <p className="text-xs sm:text-sm text-[#475569] mt-1">
              {isTa
                ? "கொடுப்பினை (40/40/15/5) + தசா-புத்தி-அந்தரம் (25) + 7ஆம் பாவ முனை நட்சத்திரம் + முகூர்த்த பஞ்சாங்கம்"
                : "4-Stage Engine: Promise (40/40/15/5) + Dasha-Bhukti-Antara (25) + 7th Cusp Star/Sub/Sub-Sub + Muhurta Panchangam"}
            </p>
          </div>

          <div className="flex flex-wrap items-end gap-3">
            <div>
              <label className="block text-[11px] font-semibold text-[#475569] mb-1">
                {isTa ? "தொடக்க தேதி" : "Search From"}
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="px-3 py-1.5 text-xs sm:text-sm rounded-lg border border-[#CBD5E1] bg-white text-[#0F172A]"
              />
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-[#475569] mb-1">
                {isTa ? "கால அளவு" : "Horizon"}
              </label>
              <select
                value={yearsAhead}
                onChange={(e) => setYearsAhead(Number(e.target.value))}
                className="px-3 py-1.5 text-xs sm:text-sm rounded-lg border border-[#CBD5E1] bg-white text-[#0F172A]"
              >
                {[1, 2, 3, 4, 5].map((y) => (
                  <option key={y} value={y}>
                    {isTa ? `${y} ஆண்டு${y > 1 ? "கள்" : ""}` : `${y} Year${y > 1 ? "s" : ""}`}
                  </option>
                ))}
              </select>
            </div>
            <button
              type="button"
              onClick={handleCalculate}
              disabled={loading}
              className="px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-700 disabled:opacity-60 text-white text-xs sm:text-sm font-bold flex items-center gap-1.5 shadow-xs transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
              <span>
                {loading
                  ? isTa
                    ? "கணக்கிடுகிறது..."
                    : "Calculating..."
                  : isTa
                  ? "திருமண தேதி தேடு"
                  : "Find Marriage Dates"}
              </span>
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {result && (
        <>
          {/* Weak Promise Warning */}
          {result.promise.verdict === "Weak / Delayed" && (
            <div className="p-4 rounded-xl bg-amber-50 border border-amber-300 text-amber-900 text-xs sm:text-sm flex items-start gap-2.5">
              <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <div className="font-bold">
                  {isTa
                    ? "எச்சரிக்கை: பலவீனமான / தாமதக் கொடுப்பினை"
                    : "Caution: Weak / Delayed Marriage Promise"}
                </div>
                <p className="mt-0.5">{isTa ? result.promise.summary_ta : result.promise.summary_en}</p>
              </div>
            </div>
          )}

          {/* Stage 1: Promise Assessment (100 pts) + 70:25:5 Composite */}
          <div className="bg-white rounded-xl border border-[#E2DCD5] p-4 sm:p-5 shadow-2xs space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#F1EBE4] pb-3">
              <div>
                <h4 className="text-sm sm:text-base font-bold text-[#0F172A] flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-[#B8860B]" />
                  <span>
                    {isTa
                      ? "1. திருமணக் கொடுப்பினை மதிப்பீடு (100 மதிப்பெண்)"
                      : "1. Marriage Promise Assessment (100-Point Scale)"}
                  </span>
                </h4>
                <p className="text-xs text-[#64748B] mt-0.5">
                  {isTa ? result.promise.summary_ta : result.promise.summary_en}
                </p>
              </div>
              <div className="flex items-center gap-3 shrink-0">
                <div className="text-right">
                  <div className="text-2xl font-extrabold text-[#0F172A]">
                    {result.promise.total_score}
                    <span className="text-xs font-medium text-[#64748B]">/100</span>
                  </div>
                  <div className="text-[11px] text-[#64748B]">
                    {isTa ? result.promise.confidence_ta : `${result.promise.confidence} Confidence`}
                  </div>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-bold border ${verdictBadgeClass(
                    result.promise.verdict
                  )}`}
                >
                  {isTa ? result.promise.verdict_ta : result.promise.verdict}
                </span>
              </div>
            </div>

            {/* 40 / 40 / 15 / 5 Factors */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {result.promise.factors.map((f) => {
                const pct = Math.min(100, Math.round((f.score / f.max_score) * 100));
                return (
                  <div
                    key={f.factor_key}
                    className="p-3.5 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5] space-y-2"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs sm:text-sm font-bold text-[#0F172A]">
                        {isTa ? f.title_ta : f.title_en}
                      </span>
                      <span className="text-xs font-bold text-[#B8860B]">
                        {f.score} / {f.max_score}
                      </span>
                    </div>
                    <div className="w-full h-2 bg-[#E2DCD5] rounded-full overflow-hidden">
                      <div
                        className="h-full bg-[#B8860B] rounded-full transition-all"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <div className="text-xs text-[#475569]">
                      {isTa ? f.detail_ta : f.detail_en}
                    </div>
                    <div className="flex flex-wrap gap-1.5 text-[11px]">
                      {f.supporting_houses.length > 0 && (
                        <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                          {isTa ? "சாதகம்:" : "Support:"} {f.supporting_houses.join(", ")}
                        </span>
                      )}
                      {f.obstacle_houses.length > 0 && (
                        <span className="px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200">
                          {isTa ? "தடை:" : "Obstacle:"} {f.obstacle_houses.join(", ")}
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* 70 / 25 / 5 Composite Strip */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 text-center">
              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                <div className="text-[11px] text-[#64748B]">
                  {isTa ? "கொடுப்பினை (70%)" : "Promise (70%)"}
                </div>
                <div className="text-sm font-bold text-[#0F172A]">
                  {result.composite_weights.promise_70} / 70
                </div>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                <div className="text-[11px] text-[#64748B]">
                  {isTa ? "தசா-புத்தி (25%)" : "Dasha-Bhukti (25%)"}
                </div>
                <div className="text-sm font-bold text-[#0F172A]">
                  {result.composite_weights.dasha_bhukti_25} / 25
                </div>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                <div className="text-[11px] text-[#64748B]">
                  {isTa ? "கோச்சாரம் / முகூர்த்தம் (5%)" : "Transit / Muhurta (5%)"}
                </div>
                <div className="text-sm font-bold text-[#0F172A]">
                  {result.composite_weights.transit_muhurta_5} / 5
                </div>
              </div>
              <div className="p-2.5 rounded-lg bg-amber-50 border border-amber-200">
                <div className="text-[11px] text-amber-800 font-semibold">
                  {isTa ? "மொத்த வலிமை" : "Overall Strength"}
                </div>
                <div className="text-sm font-extrabold text-amber-900">
                  {result.composite_weights.overall_100} / 100
                </div>
              </div>
            </div>
          </div>

          {/* Stage 2: 7th Cusp Analysis & Target Stars */}
          <div className="bg-white rounded-xl border border-[#E2DCD5] p-4 sm:p-5 shadow-2xs space-y-3">
            <h4 className="text-sm sm:text-base font-bold text-[#0F172A] flex items-center gap-2">
              <Compass className="w-4 h-4 text-[#B8860B]" />
              <span>
                {isTa
                  ? "2. 7ஆம் பாவ ஆரம்ப முனை & இலக்கு நட்சத்திரங்கள்"
                  : "2. 7th House Cusp & Target Wedding Nakshatras"}
              </span>
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5 text-xs">
              <div className="p-2.5 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5]">
                <div className="text-[#64748B]">{isTa ? "7ஆம் பாவம்" : "7th Cusp"}</div>
                <div className="font-bold text-[#0F172A] mt-0.5">
                  {isTa ? result.seventh_cusp.sign_ta : result.seventh_cusp.sign}{" "}
                  {result.seventh_cusp.degree_dms}
                </div>
              </div>
              <div className="p-2.5 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5]">
                <div className="text-[#64748B]">{isTa ? "ராசி அதிபதி" : "Sign Lord"}</div>
                <div className="font-bold text-[#0F172A] mt-0.5">
                  {isTa ? result.seventh_cusp.sign_lord_ta : result.seventh_cusp.sign_lord}
                </div>
              </div>
              <div className="p-2.5 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5]">
                <div className="text-[#64748B]">{isTa ? "நட்சத்திர அதிபதி" : "Star Lord"}</div>
                <div className="font-bold text-[#0F172A] mt-0.5">
                  {isTa ? result.seventh_cusp.star_lord_ta : result.seventh_cusp.star_lord}
                </div>
              </div>
              <div className="p-2.5 rounded-lg bg-amber-50 border border-amber-200">
                <div className="text-amber-800 font-semibold">
                  {isTa ? "உபநட்சத்திர அதிபதி (முதன்மை)" : "Sub Lord (Primary)"}
                </div>
                <div className="font-extrabold text-amber-900 mt-0.5">
                  {isTa ? result.seventh_cusp.sub_lord_ta : result.seventh_cusp.sub_lord}
                </div>
              </div>
              <div className="p-2.5 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5]">
                <div className="text-[#64748B]">{isTa ? "உப-உப அதிபதி" : "Sub-Sub Lord"}</div>
                <div className="font-bold text-[#0F172A] mt-0.5">
                  {isTa ? result.seventh_cusp.sub_sub_lord_ta : result.seventh_cusp.sub_sub_lord}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-1">
              {result.seventh_cusp.target_lords.map((tl) => (
                <div
                  key={`${tl.priority}-${tl.planet}`}
                  className="p-3 rounded-lg border border-[#E2DCD5] bg-white text-xs"
                >
                  <div className="flex items-center justify-between font-bold text-[#0F172A]">
                    <span>
                      #{tl.priority} {isTa ? tl.role_ta : tl.role_en}
                    </span>
                    <span className="text-[#B8860B]">
                      {isTa ? tl.planet_ta : tl.planet}
                    </span>
                  </div>
                  <div className="text-[#475569] mt-1">
                    {isTa ? tl.stars_ta.join(", ") : tl.stars_en.join(", ")}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Stage 3: Favorable Dasha-Bhukti-Antara Windows */}
          <div className="bg-white rounded-xl border border-[#E2DCD5] p-4 sm:p-5 shadow-2xs space-y-3">
            <h4 className="text-sm sm:text-base font-bold text-[#0F172A] flex items-center gap-2">
              <Clock className="w-4 h-4 text-[#B8860B]" />
              <span>
                {isTa
                  ? "3. சாதகமான தசா – புத்தி – அந்தர காலங்கள் (25 மதிப்பெண்)"
                  : "3. Top Favorable Dasha – Bhukti – Antara Windows (25-Pt Scale)"}
              </span>
            </h4>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs sm:text-sm">
                <thead>
                  <tr className="border-b border-[#E2DCD5] bg-[#FAF8F5] text-[11px] uppercase text-[#64748B]">
                    <th className="px-3 py-2">{isTa ? "தசா - புத்தி - அந்தரம்" : "Dasha - Bhukti - Antara"}</th>
                    <th className="px-3 py-2">{isTa ? "காலம்" : "Period"}</th>
                    <th className="px-3 py-2">{isTa ? "மதிப்பெண் (10+10+5)" : "Score (10+10+5)"}</th>
                    <th className="px-3 py-2">{isTa ? "நிலை" : "Rating"}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F1EBE4]">
                  {result.dasha_windows.map((w, idx) => (
                    <tr key={`${w.start_date}-${idx}`} className="hover:bg-[#FAF8F5]">
                      <td className="px-3 py-2 font-semibold text-[#0F172A]">
                        {isTa
                          ? `${w.dasha_lord_ta} – ${w.bhukti_lord_ta} – ${w.antara_lord_ta}`
                          : `${w.dasha_lord} – ${w.bhukti_lord} – ${w.antara_lord}`}
                        {w.is_current && (
                          <span className="ml-2 px-1.5 py-0.5 text-[10px] rounded bg-emerald-100 text-emerald-800 font-bold">
                            {isTa ? "நடப்பு" : "Current"}
                          </span>
                        )}
                      </td>
                      <td className="px-3 py-2 font-mono text-xs text-[#475569]">
                        {formatDate(w.start_date)} → {formatDate(w.end_date)}
                      </td>
                      <td className="px-3 py-2 font-bold text-[#B8860B]">
                        {w.total_score}/25{" "}
                        <span className="text-[11px] font-normal text-[#64748B]">
                          ({w.dasha_score}+{w.bhukti_score}+{w.antara_score})
                        </span>
                      </td>
                      <td className="px-3 py-2 text-xs font-medium text-[#334155]">
                        {isTa ? w.rating_ta : w.rating}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Stage 4: Candidate Marriage Dates (Muhurta + 7th Cusp Sync) */}
          <div className="bg-white rounded-xl border border-[#E2DCD5] p-4 sm:p-5 shadow-2xs space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <h4 className="text-sm sm:text-base font-bold text-[#0F172A] flex items-center gap-2">
                <Calendar className="w-4 h-4 text-rose-600" />
                <span>
                  {isTa
                    ? "4. பரிந்துரைக்கப்படும் திருமண முகூர்த்த தேதிகள்"
                    : "4. Ranked Candidate Marriage Dates (KP + Muhurta)"}
                </span>
              </h4>
              <span className="text-xs text-[#64748B]">
                {isTa
                  ? "வளர்பிறை, சுப திதி, செவ்வாய்/சனி தவிர்ப்பு & 7ஆம் பாவ நட்சத்திரப் பொருத்தம்"
                  : "Shukla Paksha preferred • Tue/Sat & Rikta/Ashtami/Navami excluded"}
              </span>
            </div>

            {result.candidate_dates.length === 0 ? (
              <div className="p-6 text-center text-sm text-[#64748B] bg-[#FAF8F5] rounded-lg">
                {isTa
                  ? "தேர்ந்தெடுக்கப்பட்ட காலத்தில் பொருத்தமான முகூர்த்த நாட்கள் கிடைக்கவில்லை."
                  : "No matching Muhurta dates found in the top Antara windows."}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {result.candidate_dates.map((cd) => (
                  <div
                    key={cd.date}
                    className="p-3.5 rounded-xl border border-[#E2DCD5] hover:border-rose-300 bg-[#FAF8F5]/60 transition-colors space-y-2"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <div className="text-sm font-extrabold text-[#0F172A] flex items-center gap-1.5">
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                          <span>{formatDate(cd.date)}</span>
                          <span className="text-xs font-semibold text-[#475569]">
                            ({isTa ? cd.weekday_ta : cd.weekday_en})
                          </span>
                        </div>
                        <div className="text-[11px] font-semibold text-rose-700 mt-0.5">
                          {isTa ? cd.match_tier_ta : cd.match_tier}
                        </div>
                      </div>
                      <span className="px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold">
                        {cd.score}/100
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs text-[#334155] bg-white p-2.5 rounded-lg border border-[#E2DCD5]/70">
                      <div>
                        <span className="text-[#64748B]">{isTa ? "பக்ஷம் / திதி:" : "Paksha / Tithi:"}</span>{" "}
                        <span className="font-semibold">
                          {isTa ? `${cd.paksha_ta}, ${cd.tithi_ta}` : `${cd.paksha}, ${cd.tithi_en}`}
                        </span>
                      </div>
                      <div>
                        <span className="text-[#64748B]">{isTa ? "நட்சத்திரம்:" : "Nakshatra:"}</span>{" "}
                        <span className="font-semibold">
                          {isTa ? cd.nakshatra_ta : cd.nakshatra_en} ({isTa ? cd.nakshatra_lord_ta : cd.nakshatra_lord})
                        </span>
                      </div>
                      <div>
                        <span className="text-[#64748B]">{isTa ? "அபிஜித்:" : "Abhijit:"}</span>{" "}
                        <span className="font-mono text-[11px]">{cd.abhijit_window}</span>
                      </div>
                      <div>
                        <span className="text-[#64748B]">{isTa ? "ராகு காலம் (தவிர்க்க):" : "Avoid Rahu:"}</span>{" "}
                        <span className="font-mono text-[11px] text-rose-700">{cd.rahu_kalam_avoid}</span>
                      </div>
                    </div>

                    <div className="text-[11px] text-[#475569]">
                      <span className="font-semibold">{isTa ? "தசா:" : "DBA:"}</span>{" "}
                      {isTa ? cd.dasha_bhukti_antara_ta : cd.dasha_bhukti_antara}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Disclaimer */}
          <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 text-[11px] sm:text-xs text-[#64748B] flex items-start gap-2">
            <Info className="w-4 h-4 shrink-0 mt-0.5 text-slate-500" />
            <span>{isTa ? result.disclaimer_ta : result.disclaimer_en}</span>
          </div>
        </>
      )}
    </div>
  );
}
