"use client";

import React, { useState, useEffect } from "react";
import {
  HoraryKpRequest,
  HoraryKpResponse,
  SavedKpChartRecord,
} from "@/lib/types";
import { calculateHoraryKp, saveKpChart } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { formatDms } from "@/lib/formatters";
import { getGrahaName, getRasiName, getLordName } from "@/lib/translations";
import { KpCuspAnalysisTab } from "./KpCuspAnalysisTab";
import { KpSignificatorsTab } from "./KpSignificatorsTab";
import { KpBirthChartTab } from "./KpBirthChartTab";
import {
  HelpCircle,
  Clock,
  MapPin,
  Sparkles,
  Save,
  CheckCircle2,
  AlertCircle,
  RotateCcw,
} from "lucide-react";

interface HoraryPrashnaTabProps {
  language: "en" | "ta";
  onSavedRecord?: (record: SavedKpChartRecord) => void;
}

export function HoraryPrashnaTab({ language, onSavedRecord }: HoraryPrashnaTabProps) {
  const { session } = useAuth();

  // Form State
  const [horaryNumber, setHoraryNumber] = useState<number>(1);
  const [questionText, setQuestionText] = useState<string>("");
  const [questionDate, setQuestionDate] = useState<string>("");
  const [questionTime, setQuestionTime] = useState<string>("");
  const [locationName, setLocationName] = useState<string>("Chennai, India");
  const [latitude, setLatitude] = useState<number>(13.0827);
  const [longitude, setLongitude] = useState<number>(80.2707);
  const [timezone, setTimezone] = useState<string>("Asia/Kolkata");
  const [ayanamsa, setAyanamsa] = useState<number>(1); // 1 = KP

  // Execution State
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<HoraryKpResponse | null>(null);

  // Persistence State
  const [saving, setSaving] = useState<boolean>(false);
  const [savedSuccess, setSavedSuccess] = useState<string | null>(null);

  // Set current date/time on mount
  useEffect(() => {
    handleSetNow();
  }, []);

  const handleSetNow = () => {
    const now = new Date();
    const yyyy = now.getFullYear();
    const mm = String(now.getMonth() + 1).padStart(2, "0");
    const dd = String(now.getDate()).padStart(2, "0");
    const hh = String(now.getHours()).padStart(2, "0");
    const min = String(now.getMinutes()).padStart(2, "0");
    const ss = String(now.getSeconds()).padStart(2, "0");

    setQuestionDate(`${yyyy}-${mm}-${dd}`);
    setQuestionTime(`${hh}:${min}:${ss}`);
  };

  const handleCalculate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSavedSuccess(null);

    if (horaryNumber < 1 || horaryNumber > 249) {
      setError(
        language === "ta"
          ? "பிரஸ்ன எண் 1 முதல் 249 வரை இருக்க வேண்டும்."
          : "Horary number must be between 1 and 249."
      );
      return;
    }

    if (!questionDate || !questionTime) {
      setError(
        language === "ta"
          ? "கேள்வி தேதி மற்றும் நேரத்தை உள்ளிடவும்."
          : "Please specify the question date and exact time."
      );
      return;
    }

    setLoading(true);
    try {
      const payload: HoraryKpRequest = {
        horary_number: horaryNumber,
        question_text: questionText.trim() || undefined,
        question_date: questionDate,
        question_time: questionTime,
        location_name: locationName.trim() || undefined,
        latitude,
        longitude,
        timezone,
        ayanamsa,
      };

      const res = await calculateHoraryKp(payload);
      setResult(res);
    } catch (err: any) {
      setError(err?.message || "Failed to calculate Horary Prashna chart.");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveChart = async () => {
    if (!result || !session?.access_token) return;
    setSaving(true);
    setError(null);
    setSavedSuccess(null);

    try {
      const title =
        questionText.trim() ||
        `Horary #${result.horary_number} (${result.horary_division.sign}/${result.horary_division.sub_lord})`;

      const payload = {
        chart_type: "horary" as const,
        title,
        horary_number: result.horary_number,
        question_text: result.question_text || undefined,
        question_date: questionDate,
        question_time: questionTime,
        location_name: locationName,
        latitude,
        longitude,
        timezone,
        ayanamsa_id: ayanamsa,
        calculation_result: result,
      };

      const saved = await saveKpChart(session.access_token, payload);
      setSavedSuccess(
        language === "ta"
          ? `பிரஸ்ன ஜாதகம் வெற்றிகரமாக சேமிக்கப்பட்டது! வரிசை எண் #${saved.display_number}`
          : `Horary chart successfully saved! Assigned Record #${saved.display_number}`
      );
      if (onSavedRecord) {
        onSavedRecord(saved);
      }
    } catch (err: any) {
      setError(err?.message || "Failed to persist Horary chart.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Input Form Card */}
      <div className="rounded-2xl border border-[#DDE5F0] bg-white p-6 sm:p-8 shadow-xs space-y-6">
        <div className="flex items-center justify-between pb-4 border-b border-[#F1F5F9]">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center text-[#B8862B]">
              <HelpCircle className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-serif text-lg sm:text-xl font-bold text-[#102A4C]">
                {language === "ta"
                  ? "கே.பி. பிரஸ்னம் (1 - 249 எண் முறை)"
                  : "Authentic KP Horary Prashna (1 - 249)"}
              </h2>
              <p className="text-xs text-[#52667E]">
                {language === "ta"
                  ? "கேள்வி எண் லக்னத்தை நிர்ணயிக்க, கேள்வி கேட்ட கணத்தின் கிரக நிலைகள் மற்றும் காரகத்துவங்கள் கணக்கிடப்படும்."
                  : "The querent's seed number fixes Cusp 1; all planets, Moon, and Dasa are computed at the exact question moment."}
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={handleSetNow}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#FAF6EC] text-[#8C6D23] border border-[#D8BD80] hover:bg-[#F3E8CD] transition-colors"
          >
            <Clock className="w-3.5 h-3.5" />
            <span>{language === "ta" ? "தற்போதைய நேரம்" : "Use Current Time"}</span>
          </button>
        </div>

        <form onSubmit={handleCalculate} noValidate className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Horary Number Picker */}
            <div className="space-y-2">
              <label className="block text-xs font-bold text-[#102A4C] uppercase tracking-wider">
                {language === "ta" ? "பிரஸ்ன எண் (1 - 249)*" : "Horary Seed Number (1 - 249)*"}
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  min={1}
                  max={249}
                  required
                  value={horaryNumber}
                  onChange={(e) => setHoraryNumber(parseInt(e.target.value, 10) || 1)}
                  className="w-24 px-3 py-2 text-center text-lg font-bold font-serif text-[#102A4C] rounded-xl border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] focus:outline-hidden"
                />
                <input
                  type="range"
                  min={1}
                  max={249}
                  value={horaryNumber}
                  onChange={(e) => setHoraryNumber(parseInt(e.target.value, 10) || 1)}
                  className="flex-1 accent-[#B8862B] cursor-pointer"
                />
              </div>
              <p className="text-[11px] text-[#64748B]">
                {language === "ta"
                  ? "கேட்பவர் 1 முதல் 249-க்குள் தேர்ந்தெடுத்த எண்"
                  : "Random number provided by querent (1..249)"}
              </p>
            </div>

            {/* Question Text */}
            <div className="space-y-2 md:col-span-2">
              <label className="block text-xs font-bold text-[#102A4C] uppercase tracking-wider">
                {language === "ta" ? "கேள்வி அல்லது ஆலோசனை குறிப்பு" : "Querent Question / Consultation Label"}
              </label>
              <input
                type="text"
                placeholder={
                  language === "ta"
                    ? "எ.கா: புதிய வேலை வாய்ப்பு கிடைக்குமா? (Will I get the new job?)"
                    : "e.g., Will I get the new job offer this month?"
                }
                value={questionText}
                onChange={(e) => setQuestionText(e.target.value)}
                className="w-full px-3.5 py-2.5 text-sm rounded-xl border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] focus:outline-hidden text-[#102A4C]"
              />
            </div>
          </div>

          {/* Date, Time, Location Coordinates */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            <div className="space-y-1.5">
              <label className="block text-xs font-bold text-[#52667E]">
                {language === "ta" ? "கேள்வி தேதி*" : "Question Date*"}
              </label>
              <input
                type="date"
                required
                value={questionDate}
                onChange={(e) => setQuestionDate(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-lg border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] text-[#102A4C]"
              />
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-bold text-[#52667E]">
                {language === "ta" ? "கேள்வி நேரம்*" : "Question Time*"}
              </label>
              <input
                type="time"
                step="1"
                required
                value={questionTime}
                onChange={(e) => setQuestionTime(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-lg border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] text-[#102A4C]"
              />
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-bold text-[#52667E]">
                {language === "ta" ? "இடம் (City)*" : "Location Name*"}
              </label>
              <input
                type="text"
                required
                value={locationName}
                onChange={(e) => setLocationName(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-lg border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] text-[#102A4C]"
              />
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-bold text-[#52667E]">
                {language === "ta" ? "நேர மண்டலம்*" : "Timezone*"}
              </label>
              <input
                type="text"
                required
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-lg border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] text-[#102A4C]"
              />
            </div>
          </div>

          {/* Coordinates and Ayanamsa */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="space-y-1.5">
              <label className="block text-xs font-bold text-[#52667E]">Latitude (-90 to +90)</label>
              <input
                type="number"
                step="0.0001"
                required
                value={latitude}
                onChange={(e) => setLatitude(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 text-xs rounded-lg border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] text-[#102A4C]"
              />
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-bold text-[#52667E]">Longitude (-180 to +180)</label>
              <input
                type="number"
                step="0.0001"
                required
                value={longitude}
                onChange={(e) => setLongitude(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 text-xs rounded-lg border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] text-[#102A4C]"
              />
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-bold text-[#52667E]">
                {language === "ta" ? "அயனாம்சம்" : "Ayanamsa"}
              </label>
              <select
                value={ayanamsa}
                onChange={(e) => setAyanamsa(parseInt(e.target.value, 10))}
                className="w-full px-3 py-2 text-xs rounded-lg border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] text-[#102A4C] bg-white"
              >
                <option value={1}>KP Krishnamurti (Standard)</option>
                <option value={0}>Lahiri (Chitrapaksha)</option>
              </select>
            </div>
          </div>

          {error && (
            <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {savedSuccess && (
            <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-700 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{savedSuccess}</span>
            </div>
          )}

          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-bold text-white bg-[#B8862B] hover:bg-[#996515] transition-colors shadow-xs disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4" />
              <span>
                {loading
                  ? language === "ta"
                    ? "கணக்கிடப்படுகிறது..."
                    : "Computing Horary..."
                  : language === "ta"
                  ? "பிரஸ்ன ஜாதகம் கணக்கிடுக"
                  : "Calculate Horary Chart"}
              </span>
            </button>
          </div>
        </form>
      </div>

      {/* Result Section */}
      {result && (
        <div className="space-y-6 pt-2">
          {/* Horary Summary Header Card */}
          <div className="rounded-2xl border border-[#DDE5F0] bg-white p-6 shadow-sm space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-[#F1F5F9]">
              <div>
                <div className="flex items-center gap-2">
                  <span className="w-9 h-9 rounded-xl bg-[#FAF2DE] border border-[#D8BD80] text-[#8C6D23] font-serif font-bold text-base flex items-center justify-center">
                    #{result.horary_number}
                  </span>
                  <div>
                    <h3 className="font-serif text-lg font-bold text-[#102A4C]">
                      {result.question_text || `Horary Query #${result.horary_number}`}
                    </h3>
                    <div className="text-xs text-[#52667E] flex items-center gap-2">
                      <Clock className="w-3.5 h-3.5 text-[#B8862B]" />
                      <span>{new Date(result.question_datetime).toLocaleString()}</span>
                      <span>•</span>
                      <MapPin className="w-3.5 h-3.5 text-[#B8862B]" />
                      <span>{result.location_name || "Query Location"}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleSaveChart}
                  disabled={saving || !session?.access_token}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white bg-[#102A4C] hover:bg-[#1E3A61] transition-colors shadow-xs disabled:opacity-50"
                  title={
                    !session?.access_token
                      ? "Sign-in required to persist charts"
                      : "Save Horary chart to public.saved_kp_charts"
                  }
                >
                  <Save className="w-3.5 h-3.5" />
                  <span>
                    {saving
                      ? language === "ta"
                        ? "சேமிக்கப்படுகிறது..."
                        : "Saving..."
                      : language === "ta"
                      ? "ஜாதகத்தை சேமி"
                      : "Save Horary Chart"}
                  </span>
                </button>
              </div>
            </div>

            {/* Ascendant & Division Metric Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3 pt-2">
              <div className="p-3 rounded-xl bg-[#FAF6EC] border border-[#D8BD80] text-center">
                <div className="text-[10px] text-[#8C6D23] font-semibold uppercase">Horary Ascendant</div>
                <div className="text-sm font-bold font-mono text-[#102A4C] mt-0.5">
                  {formatDms(result.ascendant_degree % 30.0)}
                </div>
                <div className="text-[10px] text-[#52667E] mt-0.5">{result.horary_division.sign}</div>
              </div>

              <div className="p-3 rounded-xl bg-white border border-[#E2DCD5] text-center">
                <div className="text-[10px] text-[#52667E] font-semibold uppercase">Sign Lord</div>
                <div className="text-sm font-bold text-[#102A4C] mt-0.5">
                  {getLordName(result.horary_division.sign_lord, language)}
                </div>
              </div>

              <div className="p-3 rounded-xl bg-white border border-[#E2DCD5] text-center">
                <div className="text-[10px] text-[#52667E] font-semibold uppercase">Star Lord</div>
                <div className="text-sm font-bold text-[#102A4C] mt-0.5">
                  {getLordName(result.horary_division.star_lord, language)}
                </div>
                <div className="text-[10px] text-[#52667E] mt-0.5">{result.horary_division.star}</div>
              </div>

              <div className="p-3 rounded-xl bg-[#FAF2DE] border border-[#D8BD80] text-center">
                <div className="text-[10px] text-[#8C6D23] font-bold uppercase">Sub-Lord (Arbiter)</div>
                <div className="text-sm font-bold text-[#8C6D23] mt-0.5">
                  {getLordName(result.horary_division.sub_lord, language)}
                </div>
              </div>

              <div className="p-3 rounded-xl bg-[#EBF2FE] border border-[#BFDBFE] text-center">
                <div className="text-[10px] text-[#2563EB] font-bold uppercase">Sub-Sub-Lord</div>
                <div className="text-sm font-bold text-[#2563EB] mt-0.5">
                  {getLordName(result.horary_division.sub_sub_lord, language)}
                </div>
              </div>

              <div className="p-3 rounded-xl bg-white border border-[#E2DCD5] text-center">
                <div className="text-[10px] text-[#52667E] font-semibold uppercase">Division Span</div>
                <div className="text-xs font-mono text-[#102A4C] mt-1">
                  {formatDms(result.horary_division.start_degree % 30.0)} - {formatDms(result.horary_division.end_degree % 30.0)}
                </div>
              </div>
            </div>

            {/* Ruling Planets Banner */}
            {result.ruling_planets && (
              <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-[#102A4C] uppercase tracking-wider">
                    {language === "ta" ? "கேள்வி நேர ஆளும் கிரகங்கள் (Ruling Planets - RPs)" : "Ruling Planets of the Query Moment (RPs)"}
                  </span>
                  <span className="text-xs text-[#64748B]">Day Lord: <strong>{result.ruling_planets.day_lord}</strong></span>
                </div>
                <div className="flex flex-wrap gap-2 text-xs">
                  {result.ruling_planets.details.map((rp, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white border border-[#DDE5F0] text-[#1E293B]"
                    >
                      <strong className="text-[#B8862B]">{rp.planet}</strong>
                      <span className="text-[10px] text-[#64748B]">({rp.role})</span>
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Detailed Sub Sections for the Horary Result */}
          <div className="space-y-6">
            <div>
              <h4 className="font-serif text-base font-bold text-[#102A4C] mb-3">
                {language === "ta" ? "1. பிரஸ்ன பாவக முனை ஆய்வு (12 Cusps)" : "1. Horary Placidus Cusps & CSL Analysis"}
              </h4>
              <KpCuspAnalysisTab cusps={result.cuspal_analysis} language={language} />
            </div>

            <div>
              <h4 className="font-serif text-base font-bold text-[#102A4C] mb-3">
                {language === "ta" ? "2. கேள்வி நேர கிரக நிலைகள்" : "2. Planetary Positions at Question Moment"}
              </h4>
              <KpBirthChartTab planets={result.planetary_positions} metadata={result.metadata} language={language} />
            </div>

            <div>
              <h4 className="font-serif text-base font-bold text-[#102A4C] mb-3">
                {language === "ta" ? "3. பிரஸ்ன காரகத்துவங்கள் (A, B, C, D)" : "3. Horary Significators (A, B, C, D)"}
              </h4>
              <KpSignificatorsTab
                houseSignificators={result.house_significators}
                planetSignificators={result.significators}
                language={language}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
