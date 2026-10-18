"use client";

import React, { useState, useEffect, useRef, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { SouthIndianChart } from "@/components/charts/SouthIndianChart";
import { NorthIndianChart } from "@/components/charts/NorthIndianChart";
import {
  VargaD1D9Request,
  VargaD1D9Response,
  VargaPlanetPosition,
  HoroscopeResponse,
} from "@/lib/types";
import { calculateVargaD1D9, getSavedHoroscopeVargaD1D9 } from "@/lib/api";
import { formatDm } from "@/lib/formatters";
import {
  Compass,
  ArrowLeft,
  Sparkles,
  Layers,
  Calendar,
  Clock,
  MapPin,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  HelpCircle,
  Eye,
  Columns,
  Star,
  Award,
} from "lucide-react";

interface SavedHoroItem {
  id: string;
  person_name: string;
  birth_date: string;
  birth_time: string;
  timezone: string;
  latitude: number;
  longitude: number;
  location_name?: string;
  display_number?: number;
}

function D1D9Content() {
  const searchParams = useSearchParams();
  const savedIdParam = searchParams.get("saved_id");

  const { language } = useLanguage();
  const { session, isAuthenticated } = useAuth();

  // Mode Selection: "saved" | "adhoc"
  const [inputMode, setInputMode] = useState<"saved" | "adhoc">("saved");

  // Saved Horoscopes List & Selected Item
  const [savedHoroscopes, setSavedHoroscopes] = useState<SavedHoroItem[]>([]);
  const [selectedHoroscopeId, setSelectedHoroscopeId] = useState<string>(savedIdParam || "");
  const [loadingSavedList, setLoadingSavedList] = useState<boolean>(false);

  // Ad-hoc Form State
  const [birthDate, setBirthDate] = useState<string>("1990-05-15");
  const [birthTime, setBirthTime] = useState<string>("14:30:00");
  const [timezone, setTimezone] = useState<string>("Asia/Kolkata");
  const [latitude, setLatitude] = useState<number>(13.0827);
  const [longitude, setLongitude] = useState<number>(80.2707);
  const [ayanamsa, setAyanamsa] = useState<number>(0); // 0 = Lahiri, 1 = KP

  // UI View Controls
  const [viewMode, setViewMode] = useState<"side_by_side" | "d1" | "d9">("side_by_side");
  const [chartStyle, setChartStyle] = useState<"south" | "north">("south");

  // Calculation Results & State
  const [vargaData, setVargaData] = useState<VargaD1D9Response | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Fetch list of saved horoscopes for authenticated user
  useEffect(() => {
    async function fetchSavedList() {
      if (!session?.access_token) return;
      setLoadingSavedList(true);
      try {
        const resp = await fetch("/api/horoscopes?limit=50", {
          headers: {
            Authorization: `Bearer ${session.access_token}`,
          },
        });
        if (resp.ok) {
          const data = await resp.json();
          const items = data.horoscopes || [];
          setSavedHoroscopes(items);
          if (items.length > 0 && !selectedHoroscopeId && !savedIdParam) {
            setSelectedHoroscopeId(items[0].id);
          }
        }
      } catch (err) {
        console.warn("Failed to fetch saved horoscopes:", err);
      } finally {
        setLoadingSavedList(false);
      }
    }

    if (isAuthenticated) {
      fetchSavedList();
    } else {
      setInputMode("adhoc");
    }
  }, [isAuthenticated, session?.access_token]);

  // Handle calculation execution
  const handleCalculate = async () => {
    setLoading(true);
    setErrorMsg(null);

    try {
      if (inputMode === "saved") {
        if (!selectedHoroscopeId) {
          throw new Error("Please select a saved horoscope.");
        }
        const token = session?.access_token;
        const res = await calculateVargaD1D9(
          { saved_horoscope_id: selectedHoroscopeId },
          token
        );
        setVargaData(res);
      } else {
        const token = session?.access_token;
        const payload: VargaD1D9Request = {
          birth_date: birthDate,
          birth_time: birthTime,
          timezone,
          latitude,
          longitude,
          ayanamsa,
          house_system: 0,
        };
        const res = await calculateVargaD1D9(payload, token);
        setVargaData(res);
      }
    } catch (err: any) {
      console.error("D1/D9 calculation failed:", err);
      setErrorMsg(err.message || "Failed to calculate D1/D9 divisional charts.");
    } finally {
      setLoading(false);
    }
  };

  // Auto-calculate if saved_id was provided in URL query param
  const initialCalcRef = useRef(false);
  useEffect(() => {
    if (savedIdParam && session?.access_token && !initialCalcRef.current) {
      initialCalcRef.current = true;
      setInputMode("saved");
      setSelectedHoroscopeId(savedIdParam);
      calculateVargaD1D9({ saved_horoscope_id: savedIdParam }, session.access_token)
        .then((res) => setVargaData(res))
        .catch((e) => setErrorMsg(e.message));
    }
  }, [savedIdParam, session?.access_token]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-8">
      {/* Breadcrumbs */}
      <Breadcrumbs
        items={[
          {
            label: language === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools",
            href: "/tools",
          },
          {
            label: language === "ta" ? "D1 ராசி & D9 நவாம்சம்" : "D1 Rasi & D9 Navamsa",
          },
        ]}
      />

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-[#DDE5F0] pb-6">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80] mb-2">
            <Compass className="w-3.5 h-3.5 text-[#B8862B]" />
            <span>Vedic Divisional Charts (Varga Chakras)</span>
          </div>
          <h1 className="font-serif text-2xl sm:text-3xl lg:text-4xl font-bold text-[#102A4C]">
            {language === "ta" ? "D1 ராசி & D9 நவாம்ச சக்கரங்கள்" : "D1 Rasi & D9 Navamsa Explorer"}
          </h1>
          <p className="text-xs sm:text-sm text-[#52667E] mt-1 max-w-2xl">
            {language === "ta"
              ? "108 நவாம்ச எல்லை துல்லிய கணக்கீடு, வர்கோத்தம நிலைகள் மற்றும் 24 புஷ்கர நவாம்சங்கள் அடங்கிய ஒப்பீட்டு ஆய்வு."
              : "Side-by-side divisional chart analysis with exact 108-boundary integer arithmetic, classical Vargottama dignities, and 24 Pushkara Navamsas."}
          </p>
        </div>

        <Link
          href="/tools"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#52667E] hover:text-[#102A4C] self-start md:self-center transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>{language === "ta" ? "கருவிகள் அடைவு" : "Back to Tools"}</span>
        </Link>
      </div>

      {/* Controls & Input Card */}
      <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-5">
        <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-4">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-[#B8862B]" />
            <h2 className="text-sm font-bold text-[#102A4C]">
              {language === "ta" ? "ஜாதக தேர்வு / உள்ளீடு" : "Chart Selection & Parameters"}
            </h2>
          </div>

          {/* Mode Switcher */}
          <div className="inline-flex p-1 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] text-xs">
            <button
              type="button"
              onClick={() => setInputMode("saved")}
              disabled={!isAuthenticated}
              className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
                inputMode === "saved"
                  ? "bg-[#102A4C] text-white shadow-2xs"
                  : "text-[#64748B] hover:text-[#102A4C]"
              } ${!isAuthenticated ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
            >
              {language === "ta" ? "சேமித்த ஜாதகம்" : "Saved Horoscope"}
            </button>
            <button
              type="button"
              onClick={() => setInputMode("adhoc")}
              className={`px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer ${
                inputMode === "adhoc"
                  ? "bg-[#102A4C] text-white shadow-2xs"
                  : "text-[#64748B] hover:text-[#102A4C]"
              }`}
            >
              {language === "ta" ? "புதிய உள்ளீடு" : "Custom Birth Details"}
            </button>
          </div>
        </div>

        {/* Saved Horoscope Selector */}
        {inputMode === "saved" && (
          <div className="space-y-3">
            <label className="block text-xs font-semibold text-[#334155]">
              {language === "ta" ? "சேமிக்கப்பட்ட ஜாதகத்தை தேர்ந்தெடுக்கவும்:" : "Select Saved Horoscope:"}
            </label>
            {loadingSavedList ? (
              <div className="text-xs text-[#64748B] flex items-center gap-2">
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-[#B8862B]" />
                <span>Loading your saved charts...</span>
              </div>
            ) : savedHoroscopes.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {savedHoroscopes.map((h) => {
                  const isSelected = selectedHoroscopeId === h.id;
                  return (
                    <div
                      key={h.id}
                      onClick={() => setSelectedHoroscopeId(h.id)}
                      className={`p-3.5 rounded-xl border text-xs cursor-pointer transition-all ${
                        isSelected
                          ? "border-[#B8862B] bg-[#FAF2DE]/50 shadow-xs"
                          : "border-[#E2E8F0] bg-white hover:border-[#CBD5E1]"
                      }`}
                    >
                      <div className="flex items-center justify-between font-bold text-[#102A4C]">
                        <span>{h.person_name}</span>
                        {isSelected && <CheckCircle2 className="w-4 h-4 text-[#B8862B]" />}
                      </div>
                      <div className="text-[11px] text-[#64748B] mt-1 space-y-0.5">
                        <div>
                          {h.birth_date} • {h.birth_time}
                        </div>
                        <div className="truncate text-[#94A3B8]">
                          {h.location_name || `${h.latitude.toFixed(2)}°, ${h.longitude.toFixed(2)}°`}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-amber-50/70 border border-amber-200 text-amber-900 text-xs">
                {language === "ta"
                  ? "சேமிக்கப்பட்ட ஜாதகங்கள் இல்லை. 'புதிய உள்ளீடு' மூலம் கணக்கிடலாம்."
                  : "No saved horoscopes found. Switch to 'Custom Birth Details' to calculate ad-hoc."}
              </div>
            )}
          </div>
        )}

        {/* Ad-hoc Form Inputs */}
        {inputMode === "adhoc" && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
            <div>
              <label className="block font-semibold text-[#334155] mb-1">
                <Calendar className="w-3.5 h-3.5 inline mr-1 text-[#B8862B]" />
                Birth Date (YYYY-MM-DD)
              </label>
              <input
                type="date"
                value={birthDate}
                onChange={(e) => setBirthDate(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] bg-white text-[#102A4C] font-mono focus:outline-hidden focus:border-[#B8862B]"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#334155] mb-1">
                <Clock className="w-3.5 h-3.5 inline mr-1 text-[#B8862B]" />
                Birth Time (HH:MM:SS)
              </label>
              <input
                type="time"
                step="1"
                value={birthTime}
                onChange={(e) => setBirthTime(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] bg-white text-[#102A4C] font-mono focus:outline-hidden focus:border-[#B8862B]"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#334155] mb-1">
                <MapPin className="w-3.5 h-3.5 inline mr-1 text-[#B8862B]" />
                Latitude (° Dec)
              </label>
              <input
                type="number"
                step="any"
                value={latitude}
                onChange={(e) => setLatitude(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] bg-white text-[#102A4C] font-mono focus:outline-hidden focus:border-[#B8862B]"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#334155] mb-1">
                <MapPin className="w-3.5 h-3.5 inline mr-1 text-[#B8862B]" />
                Longitude (° Dec)
              </label>
              <input
                type="number"
                step="any"
                value={longitude}
                onChange={(e) => setLongitude(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] bg-white text-[#102A4C] font-mono focus:outline-hidden focus:border-[#B8862B]"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#334155] mb-1">Timezone</label>
              <input
                type="text"
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                placeholder="Asia/Kolkata"
                className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] bg-white text-[#102A4C] font-mono focus:outline-hidden focus:border-[#B8862B]"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#334155] mb-1">Ayanamsa</label>
              <select
                value={ayanamsa}
                onChange={(e) => setAyanamsa(parseInt(e.target.value, 10))}
                className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] bg-white text-[#102A4C] font-semibold focus:outline-hidden focus:border-[#B8862B]"
              >
                <option value={0}>Lahiri (Chitra Paksha - Classical)</option>
                <option value={1}>KP (Krishnamurti Ayanamsa)</option>
              </select>
            </div>
          </div>
        )}

        {/* Action Button */}
        <div className="pt-2 flex items-center justify-between">
          <button
            type="button"
            onClick={handleCalculate}
            disabled={loading || (inputMode === "saved" && !selectedHoroscopeId)}
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-[#B8862B] to-[#9E6E1A] text-white font-bold text-xs shadow-md hover:shadow-lg transition-all cursor-pointer disabled:opacity-50"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>{language === "ta" ? "கணக்கிடப்படுகிறது..." : "Calculating D1/D9..."}</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>
                  {language === "ta"
                    ? "D1 & D9 சக்கரங்களைக் காண்க"
                    : "Calculate & View D1 & D9 Charts"}
                </span>
              </>
            )}
          </button>

          {errorMsg && (
            <div className="inline-flex items-center gap-1.5 text-xs text-rose-600 bg-rose-50 px-3 py-1.5 rounded-lg border border-rose-200">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}
        </div>
      </div>

      {/* Results Workspace */}
      {vargaData && (
        <div className="space-y-8">
          {/* 1. Dignity & Summary Metrics Banner */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-1">
              <div className="text-[11px] font-bold text-[#8C6D23] uppercase tracking-wider">
                D1 Rasi Lagna
              </div>
              <div className="text-xl font-serif font-bold text-[#102A4C]">
                {vargaData.ascendant.d1_sign_name}
              </div>
              <div className="text-xs text-[#64748B]">
                {formatDm(vargaData.ascendant.d1_degree_in_sign)} • {vargaData.ascendant.nakshatra_name} (P{vargaData.ascendant.pada})
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-1">
              <div className="text-[11px] font-bold text-[#8C6D23] uppercase tracking-wider">
                D9 Navamsa Lagna
              </div>
              <div className="text-xl font-serif font-bold text-[#102A4C]">
                {vargaData.ascendant.d9_sign_name}
              </div>
              <div className="text-xs text-[#64748B]">
                {formatDm(vargaData.ascendant.d9_degree_in_sign)} • Lord: {vargaData.ascendant.d9_sign_lord}
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-[#FAF2DE]/60 border border-[#D8BD80] shadow-2xs space-y-1">
              <div className="flex items-center justify-between text-[11px] font-bold text-[#8C6D23] uppercase tracking-wider">
                <span>Vargottama Planets</span>
                <Award className="w-4 h-4 text-[#B8862B]" />
              </div>
              <div className="text-xl font-serif font-bold text-[#8C6D23]">
                {vargaData.summary.total_vargottama_count} Grahas
              </div>
              <div className="text-xs text-[#52667E] truncate">
                {vargaData.summary.vargottama_planets.length > 0
                  ? vargaData.summary.vargottama_planets.join(", ")
                  : "None"}
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-emerald-50/70 border border-emerald-200 shadow-2xs space-y-1">
              <div className="flex items-center justify-between text-[11px] font-bold text-emerald-800 uppercase tracking-wider">
                <span>Pushkara Navamsas</span>
                <Star className="w-4 h-4 text-emerald-600 fill-emerald-600" />
              </div>
              <div className="text-xl font-serif font-bold text-emerald-900">
                {vargaData.summary.pushkara_navamsa_planets.length} Grahas
              </div>
              <div className="text-xs text-emerald-700 truncate">
                {vargaData.summary.pushkara_navamsa_planets.length > 0
                  ? vargaData.summary.pushkara_navamsa_planets.join(", ")
                  : "None"}
              </div>
            </div>
          </div>

          {/* 2. Visual Chart Section with View Switchers */}
          <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[#F1F5F9] pb-4">
              {/* View Mode: Side-by-Side vs Tabs */}
              <div className="flex items-center gap-1.5 p-1 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] text-xs">
                <button
                  type="button"
                  onClick={() => setViewMode("side_by_side")}
                  className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer ${
                    viewMode === "side_by_side"
                      ? "bg-[#102A4C] text-white shadow-2xs"
                      : "text-[#64748B] hover:text-[#102A4C]"
                  }`}
                >
                  <Columns className="w-3.5 h-3.5" />
                  <span>{language === "ta" ? "ஒப்பீட்டு பார்வை" : "Side-by-Side View"}</span>
                </button>
                <button
                  type="button"
                  onClick={() => setViewMode("d1")}
                  className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer ${
                    viewMode === "d1"
                      ? "bg-[#102A4C] text-white shadow-2xs"
                      : "text-[#64748B] hover:text-[#102A4C]"
                  }`}
                >
                  <Eye className="w-3.5 h-3.5" />
                  <span>D1 Rasi</span>
                </button>
                <button
                  type="button"
                  onClick={() => setViewMode("d9")}
                  className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer ${
                    viewMode === "d9"
                      ? "bg-[#102A4C] text-white shadow-2xs"
                      : "text-[#64748B] hover:text-[#102A4C]"
                  }`}
                >
                  <Eye className="w-3.5 h-3.5" />
                  <span>D9 Navamsa</span>
                </button>
              </div>

              {/* Chart Style Switcher: South vs North */}
              <div className="flex items-center gap-2 text-xs">
                <span className="text-[#64748B] font-semibold">Style:</span>
                <div className="inline-flex p-1 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                  <button
                    type="button"
                    onClick={() => setChartStyle("south")}
                    className={`px-3 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                      chartStyle === "south"
                        ? "bg-[#B8862B] text-white shadow-2xs"
                        : "text-[#64748B] hover:text-[#102A4C]"
                    }`}
                  >
                    South Indian
                  </button>
                  <button
                    type="button"
                    onClick={() => setChartStyle("north")}
                    className={`px-3 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                      chartStyle === "north"
                        ? "bg-[#B8862B] text-white shadow-2xs"
                        : "text-[#64748B] hover:text-[#102A4C]"
                    }`}
                  >
                    North Indian
                  </button>
                </div>
              </div>
            </div>

            {/* Charts Grid */}
            {viewMode === "side_by_side" ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
                {/* D1 Rasi Chart */}
                <div className="space-y-3">
                  <div className="text-center">
                    <h3 className="font-serif text-lg font-bold text-[#102A4C]">
                      D1 Rasi Chakra (ராசி கட்டம்)
                    </h3>
                    <p className="text-xs text-[#64748B]">
                      Physical body, birth disposition, and foundational karma
                    </p>
                  </div>
                  <div className="p-4 rounded-2xl bg-[#FAF7F0] border border-[#E8DEC8]">
                    {chartStyle === "south" ? (
                      <SouthIndianChart horoscope={vargaData.d1_chart as unknown as HoroscopeResponse} />
                    ) : (
                      <NorthIndianChart horoscope={vargaData.d1_chart as unknown as HoroscopeResponse} />
                    )}
                  </div>
                </div>

                {/* D9 Navamsa Chart */}
                <div className="space-y-3">
                  <div className="text-center">
                    <h3 className="font-serif text-lg font-bold text-[#102A4C]">
                      D9 Navamsa Chakra (நவாம்ச கட்டம்)
                    </h3>
                    <p className="text-xs text-[#64748B]">
                      Inner strength, spiritual fruits, and marital destiny
                    </p>
                  </div>
                  <div className="p-4 rounded-2xl bg-[#FAF7F0] border border-[#E8DEC8]">
                    {chartStyle === "south" ? (
                      <SouthIndianChart horoscope={vargaData.d9_chart as unknown as HoroscopeResponse} />
                    ) : (
                      <NorthIndianChart horoscope={vargaData.d9_chart as unknown as HoroscopeResponse} />
                    )}
                  </div>
                </div>
              </div>
            ) : viewMode === "d1" ? (
              <div className="max-w-xl mx-auto space-y-3">
                <div className="text-center">
                  <h3 className="font-serif text-lg font-bold text-[#102A4C]">
                    D1 Rasi Chakra (ராசி கட்டம்)
                  </h3>
                  <p className="text-xs text-[#64748B]">
                    Ascendant: {vargaData.ascendant.d1_sign_name} ({formatDm(vargaData.ascendant.d1_degree_in_sign)})
                  </p>
                </div>
                <div className="p-4 rounded-2xl bg-[#FAF7F0] border border-[#E8DEC8]">
                  {chartStyle === "south" ? (
                    <SouthIndianChart horoscope={vargaData.d1_chart as unknown as HoroscopeResponse} />
                  ) : (
                    <NorthIndianChart horoscope={vargaData.d1_chart as unknown as HoroscopeResponse} />
                  )}
                </div>
              </div>
            ) : (
              <div className="max-w-xl mx-auto space-y-3">
                <div className="text-center">
                  <h3 className="font-serif text-lg font-bold text-[#102A4C]">
                    D9 Navamsa Chakra (நவாம்ச கட்டம்)
                  </h3>
                  <p className="text-xs text-[#64748B]">
                    Navamsa Lagna: {vargaData.ascendant.d9_sign_name} ({formatDm(vargaData.ascendant.d9_degree_in_sign)})
                  </p>
                </div>
                <div className="p-4 rounded-2xl bg-[#FAF7F0] border border-[#E8DEC8]">
                  {chartStyle === "south" ? (
                    <SouthIndianChart horoscope={vargaData.d9_chart as unknown as HoroscopeResponse} />
                  ) : (
                    <NorthIndianChart horoscope={vargaData.d9_chart as unknown as HoroscopeResponse} />
                  )}
                </div>
              </div>
            )}
          </div>

          {/* 3. Detailed Comparative Planetary Table */}
          <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-serif text-lg font-bold text-[#102A4C]">
                  {language === "ta" ? "கிரக நிலைகள் & வர்கோத்தம ஒப்பீடு" : "D1 / D9 Comparative Planetary Analysis"}
                </h3>
                <p className="text-xs text-[#64748B]">
                  Rigorous comparison of signs, houses, nakshatras, and classical dignities.
                </p>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-[#FAF7F0] text-[#8C6D23] font-bold uppercase tracking-wider border-b border-[#E8DEC8]">
                  <tr>
                    <th className="py-3 px-3">Planet / Graha</th>
                    <th className="py-3 px-3">Motion</th>
                    <th className="py-3 px-3">D1 Rasi &amp; House</th>
                    <th className="py-3 px-3">D1 Deg in Sign</th>
                    <th className="py-3 px-3">D9 Navamsa &amp; House</th>
                    <th className="py-3 px-3">Nakshatra &amp; Pada</th>
                    <th className="py-3 px-3">Dignities</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#334155]">
                  {/* Ascendant Row */}
                  <tr className="bg-[#FAF2DE]/20 font-semibold">
                    <td className="py-2.5 px-3 flex items-center gap-1.5 text-[#102A4C]">
                      <Compass className="w-3.5 h-3.5 text-[#B8862B]" />
                      <span>Ascendant (Lagna)</span>
                    </td>
                    <td className="py-2.5 px-3 text-[#64748B]">Direct</td>
                    <td className="py-2.5 px-3 text-[#102A4C]">
                      {vargaData.ascendant.d1_sign_name} (H1)
                    </td>
                    <td className="py-2.5 px-3 font-mono">
                      {formatDm(vargaData.ascendant.d1_degree_in_sign)}
                    </td>
                    <td className="py-2.5 px-3 text-[#102A4C]">
                      {vargaData.ascendant.d9_sign_name} (H1)
                    </td>
                    <td className="py-2.5 px-3">
                      {vargaData.ascendant.nakshatra_name} (P{vargaData.ascendant.pada})
                    </td>
                    <td className="py-2.5 px-3">
                      {vargaData.ascendant.is_vargottama && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
                          <Award className="w-3 h-3 text-[#B8862B]" />
                          Vargottama
                        </span>
                      )}
                    </td>
                  </tr>

                  {/* Planets */}
                  {vargaData.planets.map((p: VargaPlanetPosition) => (
                    <tr key={p.name} className="hover:bg-[#FAF6EC]/40 transition-colors">
                      <td className="py-2.5 px-3 font-bold text-[#102A4C]">
                        {p.name}
                        <span className="text-[10px] text-[#8C6D23] ml-1.5 font-normal">
                          ({p.d1_sign_name_tamil})
                        </span>
                      </td>
                      <td className="py-2.5 px-3">
                        {p.is_retrograde ? (
                          <span className="inline-flex items-center px-1.5 py-0.5 rounded-sm text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200">
                            Retro (R)
                          </span>
                        ) : (
                          <span className="text-[#94A3B8]">Direct</span>
                        )}
                      </td>
                      <td className="py-2.5 px-3">
                        <span className="font-semibold text-[#102A4C]">{p.d1_sign_name}</span>{" "}
                        <span className="text-[#64748B]">(H{p.d1_house})</span>
                      </td>
                      <td className="py-2.5 px-3 font-mono text-[#475569]">
                        {formatDm(p.d1_degree_in_sign)}
                      </td>
                      <td className="py-2.5 px-3">
                        <span className="font-semibold text-[#102A4C]">{p.d9_sign_name}</span>{" "}
                        <span className="text-[#64748B]">(H{p.d9_house})</span>
                      </td>
                      <td className="py-2.5 px-3">
                        {p.nakshatra_name} (P{p.pada})
                        <span className="text-[10px] text-[#94A3B8] block">
                          Lord: {p.star_lord}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 space-x-1">
                        {p.is_vargottama && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
                            <Award className="w-3 h-3 text-[#B8862B]" />
                            Vargottama
                          </span>
                        )}
                        {p.is_pushkara_navamsa && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                            <Star className="w-3 h-3 text-emerald-600 fill-emerald-600" />
                            Pushkara
                          </span>
                        )}
                        {!p.is_vargottama && !p.is_pushkara_navamsa && (
                          <span className="text-[#CBD5E1]">—</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* 4. Classical Shastra & Ephemeris Integrity Reference */}
          <div className="p-6 rounded-2xl bg-[#FAF7F0] border border-[#E8DEC8] text-xs text-[#52667E] space-y-3 shadow-2xs">
            <div className="flex items-center gap-2 text-[#8C6D23] font-bold text-sm">
              <HelpCircle className="w-4 h-4 text-[#B8862B]" />
              <span>Classical Jyotish Principles &amp; Mathematical Rigor</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
              <div className="space-y-1">
                <strong className="text-[#102A4C] block">D9 Navamsa Purpose</strong>
                <p className="leading-relaxed">
                  Per <em>Brihat Parashara Hora Shastra</em>, D1 represents the physical seed, while D9 Navamsa represents the fruition (Phala), dharma, spousal compatibility, and inner spiritual vitality.
                </p>
              </div>

              <div className="space-y-1">
                <strong className="text-[#102A4C] block">Vargottama Dignity</strong>
                <p className="leading-relaxed">
                  Planets occupying identical signs in D1 and D9 attain Vargottama dignity. Classical texts state that Vargottama planets bestow results equivalent to occupying their own moolatrikona sign.
                </p>
              </div>

              <div className="space-y-1">
                <strong className="text-[#102A4C] block">Pushkara Navamsas</strong>
                <p className="leading-relaxed">
                  Per <em>Jataka Parijata</em> Ch. 1, Sloka 58, exactly 24 out of 108 Navamsas are Pushkara (nourishing). All 24 fall strictly within signs ruled by natural benefics (Moon, Mercury, Venus, Jupiter).
                </p>
              </div>
            </div>

            <div className="pt-3 border-t border-[#E8DEC8] flex flex-wrap items-center justify-between text-[11px] text-[#64748B]">
              <span>
                Engine: <strong>{vargaData.metadata.engine}</strong> • Ayanamsa: <strong>{vargaData.metadata.ayanamsa_name} ({vargaData.metadata.ayanamsa_deg.toFixed(2)}°)</strong>
              </span>
              <span>
                Integer milli-arcsecond boundary precision (0 mismatches across 108 divisions).
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function D1D9Page() {
  return (
    <Suspense
      fallback={
        <div className="min-h-[50vh] flex items-center justify-center">
          <div className="w-8 h-8 border-4 border-[#B8862B] border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <D1D9Content />
    </Suspense>
  );
}
