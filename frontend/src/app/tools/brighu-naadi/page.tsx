"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  BrighuNaadiRequest,
  BrighuNaadiResponse,
} from "@/lib/types";
import { getBrighuNaadiAnalysis } from "@/lib/api";
import { BrighuNaadiSection } from "@/components/results/BrighuNaadiSection";
import {
  Compass,
  Calendar,
  Clock,
  MapPin,
  Sparkles,
  AlertCircle,
  RefreshCw,
  BookOpen,
  ArrowRight,
  User,
} from "lucide-react";

export default function BrighuNaadiToolPage() {
  const { language } = useLanguage();
  const isTa = language === "ta";

  // Form State
  const [birthDate, setBirthDate] = useState("1985-05-15");
  const [birthTime, setBirthTime] = useState("10:30:00");
  const [latitude, setLatitude] = useState(13.0827); // Chennai
  const [longitude, setLongitude] = useState(80.2707);
  const [timezone, setTimezone] = useState("Asia/Kolkata");
  const [gender, setGender] = useState("male");
  const [placeName, setPlaceName] = useState("Chennai, Tamil Nadu, India");

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<BrighuNaadiResponse | null>(null);

  // Pre-load Case Study from Book (pp. 128-129)
  const handleLoadCaseStudy = () => {
    setBirthDate("1980-04-14");
    setBirthTime("06:30:00");
    setLatitude(12.9716); // Bangalore
    setLongitude(77.5946);
    setTimezone("Asia/Kolkata");
    setGender("male");
    setPlaceName("Bangalore (Case Study pp. 128-129)");
  };

  const handleCalculate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setIsLoading(true);
    setError(null);

    const req: BrighuNaadiRequest = {
      birth_date: birthDate,
      birth_time: birthTime,
      latitude: Number(latitude),
      longitude: Number(longitude),
      timezone: timezone || "Asia/Kolkata",
      gender: gender,
      ayanamsa: 0,
    };

    try {
      const resp = await getBrighuNaadiAnalysis(req);
      setAnalysisResult(resp);
    } catch (err: any) {
      console.error("Brighu Naadi API error:", err);
      setError(
        err?.message ||
          (isTa
            ? "பிருகு நாடி பலன்களைக் கணக்கிடுவதில் பிழை ஏற்பட்டது. தயவுசெய்து மீண்டும் முயற்சிக்கவும்."
            : "Failed to calculate Brighu Naadi analysis. Please verify details and retry.")
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] dark:bg-slate-950 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Breadcrumbs */}
        <Breadcrumbs
          items={[
            { label: isTa ? "முகப்பு" : "Home", href: "/" },
            { label: isTa ? "ஜோதிடக் கருவிகள்" : "Astrology Tools", href: "/tools" },
            { label: isTa ? "பிருகு நாடி சங்கிரகம்" : "Brighu Naadi Sangraha", href: "/tools/brighu-naadi" },
          ]}
        />

        {/* Page Header */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-50 dark:bg-amber-950/40 text-amber-800 dark:text-amber-300 text-xs font-bold border border-amber-200 dark:border-amber-800/60 mb-2">
                <Compass className="w-3.5 h-3.5 text-amber-600" />
                <span>{isTa ? "பிருகு நாடி ஜோதிட ஆய்வகம்" : "Classical Brighu Naadi Laboratory"}</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
                {isTa ? "பிருகு நாடி சங்கிரகம்" : "Brighu Naadi Sangraha"}
              </h1>
              <p className="text-sm text-slate-600 dark:text-slate-400 mt-1 max-w-2xl leading-relaxed">
                {isTa
                  ? "டாக்டர் என். சீனிவாசன் சாஸ்திரியின் 'பிருகு நாடி சங்கிரகம்' நூலின் வழி ஜீவ காரகர் (குரு), கர்ம காரகர் (சனி), பிறந்த வீட்டு வாஸ்து, மற்றும் துல்லிய வயது மைல்கற்கள் ஆய்வு."
                  : "Authentic classical engine based on Dr. N. Srinivasan Shastry's 'Brighu Naadi Sangraha' (Sagar Publications). Analyzes Jeeva Karaka (Jupiter), Karma Karaka (Saturn), birth Vastu, and exact age milestones."}
              </p>
            </div>

            <button
              type="button"
              onClick={handleLoadCaseStudy}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold bg-amber-100 hover:bg-amber-200 dark:bg-amber-900/40 dark:hover:bg-amber-900/60 text-amber-900 dark:text-amber-200 border border-amber-300 dark:border-amber-700 transition-all cursor-pointer shadow-sm"
            >
              <BookOpen className="w-4 h-4 text-amber-700 dark:text-amber-300" />
              <span>{isTa ? "நூல் மாதிரி ஜாதகம் (pp. 128-129)" : "Load Book Case Study (pp. 128-129)"}</span>
            </button>
          </div>
        </div>

        {/* Input Form */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 shadow-sm">
          <form onSubmit={handleCalculate} className="space-y-6">
            <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Calendar className="w-4 h-4 text-amber-600" />
              {isTa ? "பிறப்பு விபரங்கள் உள்ளீடு" : "Enter Birth Coordinates"}
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Date */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                  {isTa ? "பிறந்த தேதி:" : "Date of Birth:"}
                </label>
                <div className="relative">
                  <input
                    type="date"
                    required
                    value={birthDate}
                    onChange={(e) => setBirthDate(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-amber-500"
                  />
                </div>
              </div>

              {/* Time */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                  {isTa ? "பிறந்த நேரம் (HH:MM:SS):" : "Time of Birth (HH:MM:SS):"}
                </label>
                <div className="relative">
                  <input
                    type="text"
                    required
                    value={birthTime}
                    onChange={(e) => setBirthTime(e.target.value)}
                    placeholder="10:30:00"
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-amber-500 font-mono"
                  />
                </div>
              </div>

              {/* Gender */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                  {isTa ? "பாலினம்:" : "Gender:"}
                </label>
                <select
                  value={gender}
                  onChange={(e) => setGender(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-amber-500"
                >
                  <option value="male">{isTa ? "ஆண் (Male)" : "Male"}</option>
                  <option value="female">{isTa ? "பெண் (Female)" : "Female"}</option>
                </select>
              </div>

              {/* Place Name */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                  {isTa ? "பிறந்த இடம்:" : "Place Name:"}
                </label>
                <input
                  type="text"
                  value={placeName}
                  onChange={(e) => setPlaceName(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-amber-500"
                />
              </div>
            </div>

            {/* Coordinates */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                  {isTa ? "அட்சரேகை (Latitude):" : "Latitude:"}
                </label>
                <input
                  type="number"
                  step="0.0001"
                  required
                  value={latitude}
                  onChange={(e) => setLatitude(parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-amber-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                  {isTa ? "தீர்க்கரேகை (Longitude):" : "Longitude:"}
                </label>
                <input
                  type="number"
                  step="0.0001"
                  required
                  value={longitude}
                  onChange={(e) => setLongitude(parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-amber-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                  {isTa ? "நேர வலயம் (Timezone):" : "Timezone:"}
                </label>
                <input
                  type="text"
                  value={timezone}
                  onChange={(e) => setTimezone(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-amber-500 font-mono"
                />
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100 dark:border-slate-800">
              <button
                type="submit"
                disabled={isLoading}
                className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-amber-700 via-amber-800 to-orange-900 hover:from-amber-800 hover:to-orange-950 text-white shadow-md transition-all cursor-pointer disabled:opacity-50"
              >
                {isLoading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>{isTa ? "கணக்கிடப்படுகிறது..." : "Calculating..."}</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>{isTa ? "பிருகு நாடி பலன்களைக் காண்க" : "Generate Brighu Naadi Analysis"}</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Error Notification */}
        {error && (
          <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-800 flex items-start gap-3 text-xs text-rose-800 dark:text-rose-200">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
            <div>
              <span className="font-bold">{isTa ? "பிழை:" : "Error:"} </span>
              {error}
            </div>
          </div>
        )}

        {/* Results Section */}
        {analysisResult && (
          <div className="pt-2">
            <BrighuNaadiSection
              data={analysisResult}
              gender={gender}
              language={language as "en" | "ta"}
            />
          </div>
        )}
      </div>
    </div>
  );
}
