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
  AshtakavargaResponse,
  PlanetBavDetail,
  PrastaraDetail,
  KakshaTransitResult,
  HoroscopeResponse,
} from "@/lib/types";
import {
  calculateAshtakavarga,
  calculateKakshaTransit,
} from "@/lib/api";
import { formatDm } from "@/lib/formatters";
import {
  Grid,
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
  Star,
  Award,
  BookOpen,
  ShieldCheck,
  Flame,
  Info,
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

const ZODIAC_SIGNS: Record<number, { en: string; ta: string; lord: string }> = {
  1: { en: "Aries", ta: "மேஷம்", lord: "Mars" },
  2: { en: "Taurus", ta: "ரிஷபம்", lord: "Venus" },
  3: { en: "Gemini", ta: "மிதுனம்", lord: "Mercury" },
  4: { en: "Cancer", ta: "கடகம்", lord: "Moon" },
  5: { en: "Leo", ta: "சிம்மம்", lord: "Sun" },
  6: { en: "Virgo", ta: "கன்னி", lord: "Mercury" },
  7: { en: "Libra", ta: "துலாம்", lord: "Venus" },
  8: { en: "Scorpio", ta: "விருச்சிகம்", lord: "Mars" },
  9: { en: "Sagittarius", ta: "தனுசு", lord: "Jupiter" },
  10: { en: "Capricorn", ta: "மகரம்", lord: "Saturn" },
  11: { en: "Aquarius", ta: "கும்பம்", lord: "Saturn" },
  12: { en: "Pisces", ta: "மீனம்", lord: "Jupiter" },
};

const PLANETS_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"] as const;

const PLANET_META: Record<string, { en: string; ta: string; expected: number }> = {
  Sun: { en: "Sun (Surya)", ta: "சூரியன்", expected: 48 },
  Moon: { en: "Moon (Chandra)", ta: "சந்திரன்", expected: 49 },
  Mars: { en: "Mars (Mangal)", ta: "செவ்வாய்", expected: 39 },
  Mercury: { en: "Mercury (Budha)", ta: "புதன்", expected: 54 },
  Jupiter: { en: "Jupiter (Guru)", ta: "குரு", expected: 56 },
  Venus: { en: "Venus (Shukra)", ta: "சுக்கிரன்", expected: 52 },
  Saturn: { en: "Saturn (Shani)", ta: "சனி", expected: 39 },
};

const KAKSHA_LORDS_ORDER = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Lagna"];

const HOUSE_DOMAINS: Record<number, { en: string; ta: string }> = {
  1: { en: "Body, Health, Vitality & Personality", ta: "உடல் நலம், தோற்றம் & ஆயுள்" },
  2: { en: "Wealth, Family, Speech & Assets", ta: "தனம், வாக்கு, குடும்பம் & செல்வம்" },
  3: { en: "Siblings, Courage, Vitality & Efforts", ta: "தைரியம், இளைய சகோதரம் & முயற்சி" },
  4: { en: "Mother, Real Estate, Vehicles & Peace", ta: "தாய், சுகம், பூமி & வாகனம்" },
  5: { en: "Children, Intelligence, Purva Punya & Mantras", ta: "புத்திர பாக்கியம், பூர்வ புண்ணியம் & அறிவு" },
  6: { en: "Debts, Diseases, Enemies & Competition", ta: "ருணம், ரோகம், சத்ரு & வெற்றி" },
  7: { en: "Spouse, Marriage, Partnerships & Trade", ta: "களத்திரம், திருமணம் & கூட்டாண்மை" },
  8: { en: "Longevity, Hidden Obstacles & Transformation", ta: "ஆயுள், மறைமுக இடர் & ஆன்மீக மாற்றம்" },
  9: { en: "Fortune, Dharma, Father & Divine Grace", ta: "பாக்கியம், தந்தை, தர்மம் & தெய்வீகம்" },
  10: { en: "Career, Honors, Social Status & Authority", ta: "ஜீவனம், தொழில், பதவி & கீர்த்தி" },
  11: { en: "Gains, Income, Elder Siblings & Desires", ta: "லாபம், வருமானம், மூத்த சகோதரம் & ஆசை நிறைவேறல்" },
  12: { en: "Expenditures, Moksha, Foreign Lands & Sleep", ta: "விரயம், மோட்சம், அயன சயனம் & வெளிநாடு" },
};

function AshtakavargaContent() {
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

  // Studio Active Tab
  const [activeTab, setActiveTab] = useState<"sav" | "bav" | "prastara" | "kakshya">("sav");

  // Planet Switcher for BAV / Prastara / Kakshya
  const [selectedPlanet, setSelectedPlanet] = useState<typeof PLANETS_7[number]>("Saturn");

  // Chart Rendering Style
  const [chartStyle, setChartStyle] = useState<"south" | "north">("south");

  // Calculation Results & State
  const [ashtakavargaData, setAshtakavargaData] = useState<AshtakavargaResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Interactive Kakshya Transit Evaluator State
  const [transitPlanet, setTransitPlanet] = useState<typeof PLANETS_7[number]>("Saturn");
  const [transitSignIndex, setTransitSignIndex] = useState<number>(12); // Pisces
  const [transitDegreeInSign, setTransitDegreeInSign] = useState<number>(5.5);
  const [evaluatingTransit, setEvaluatingTransit] = useState<boolean>(false);
  const [transitResult, setTransitResult] = useState<KakshaTransitResult | null>(null);

  // Fetch list of saved horoscopes for authenticated user
  useEffect(() => {
    async function fetchSavedList() {
      if (!session?.access_token) return;
      setLoadingSavedList(true);
      try {
        const resp = await fetch("/api/horoscopes?limit=1000", {
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
      let payloadBirth: any;
      if (inputMode === "saved") {
        if (!selectedHoroscopeId) {
          throw new Error("Please select a saved horoscope.");
        }
        const found = savedHoroscopes.find((h) => h.id === selectedHoroscopeId);
        if (!found) {
          throw new Error("Selected saved horoscope not found.");
        }
        payloadBirth = {
          birth_date: found.birth_date,
          birth_time: found.birth_time,
          timezone: found.timezone,
          latitude: found.latitude,
          longitude: found.longitude,
          ayanamsa,
        };
      } else {
        payloadBirth = {
          birth_date: birthDate,
          birth_time: birthTime,
          timezone,
          latitude,
          longitude,
          ayanamsa,
        };
      }

      const res = await calculateAshtakavarga(payloadBirth);
      setAshtakavargaData(res);
      setTransitResult(null); // Reset transit calculation
    } catch (err: any) {
      console.error("Ashtakavarga calculation failed:", err);
      setErrorMsg(err.message || "Failed to calculate Ashtakavarga.");
    } finally {
      setLoading(false);
    }
  };

  // Evaluate Kakshya Transit
  const handleEvaluateTransit = async () => {
    if (!ashtakavargaData) return;
    setEvaluatingTransit(true);
    try {
      let payloadBirth: any;
      if (inputMode === "saved") {
        const found = savedHoroscopes.find((h) => h.id === selectedHoroscopeId);
        payloadBirth = {
          birth_date: found?.birth_date || birthDate,
          birth_time: found?.birth_time || birthTime,
          timezone: found?.timezone || timezone,
          latitude: found?.latitude || latitude,
          longitude: found?.longitude || longitude,
          ayanamsa,
        };
      } else {
        payloadBirth = {
          birth_date: birthDate,
          birth_time: birthTime,
          timezone,
          latitude,
          longitude,
          ayanamsa,
        };
      }

      const result = await calculateKakshaTransit({
        ...payloadBirth,
        transit: {
          transiting_planet: transitPlanet,
          transit_sign_index: transitSignIndex,
          transit_degree_in_sign: transitDegreeInSign,
        },
      });
      setTransitResult(result);
    } catch (err: any) {
      console.error("Kakshya transit evaluation failed:", err);
    } finally {
      setEvaluatingTransit(false);
    }
  };

  // Auto-calculate if saved_id was provided in URL query param
  const initialCalcRef = useRef(false);
  useEffect(() => {
    if (savedIdParam && session?.access_token && !initialCalcRef.current) {
      initialCalcRef.current = true;
      setInputMode("saved");
      setSelectedHoroscopeId(savedIdParam);
    }
  }, [savedIdParam, session?.access_token]);

  // Build SAV Chart for South/North Chart Component
  const savChartObject = ashtakavargaData
    ? {
        metadata: ashtakavargaData.metadata,
        ascendant: {
          sign_index: ashtakavargaData.lagna_sign_index,
          sign_name: ZODIAC_SIGNS[ashtakavargaData.lagna_sign_index]?.en || "Aries",
          sign_name_tamil: ZODIAC_SIGNS[ashtakavargaData.lagna_sign_index]?.ta || "மேஷம்",
          degree_in_sign: 15.0,
        },
        planets: Object.entries(ashtakavargaData.sarvashtakavarga.sign_bindus).map(
          ([signIdx, binduCount]) => ({
            name: `${binduCount} pts`,
            sign_index: parseInt(signIdx, 10),
            sign_name: ZODIAC_SIGNS[parseInt(signIdx, 10)]?.en || "",
            sign_name_tamil: ZODIAC_SIGNS[parseInt(signIdx, 10)]?.ta || "",
            degree_in_sign: 15.0,
            is_retrograde: false,
          })
        ),
      }
    : null;

  return (
    <div className="w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 sm:py-8 space-y-8">
      {/* Breadcrumbs */}
      <Breadcrumbs
        items={[
          {
            label: language === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools",
            href: "/tools",
          },
          {
            label: language === "ta" ? "அஷ்டகவர்க்கம் & கக்ஷா ஆய்வுக்கூடம்" : "Ashtakavarga & Kakshya Studio",
          },
        ]}
      />

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-[#DDE5F0] pb-6">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80] mb-2">
            <Grid className="w-3.5 h-3.5 text-[#B8862B]" />
            <span>Classical Ashtakavarga System (BPHS Ch. 66–73)</span>
          </div>
          <h1 className="font-serif text-2xl sm:text-3xl lg:text-4xl font-bold text-[#102A4C]">
            {language === "ta"
              ? "அஷ்டகவர்க்கம் & கக்ஷா கோச்சார ஆய்வுக்கூடம்"
              : "Ashtakavarga & Kakshya Transit Studio"}
          </h1>
          <p className="text-xs sm:text-sm text-[#52667E] mt-1 max-w-2xl">
            {language === "ta"
              ? "337 சர்வ அஷ்டகவர்க்க பிந்து பரவல், திரிகோண/ஏகாதிபத்ய சோதனைகள், சோத்திய பிண்டம், 8-நபர் பிரஸ்தார சக்கரம் மற்றும் 3°45' கக்ஷா கோச்சார பலன்கள்."
              : "Complete 337-bindu Sarvashtakavarga matrix, Shodhana reductions, Shodhya Pinda, 8-donor Prastarashtakavarga, and real-time 3°45' Kakshya transit timing windows per BPHS."}
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
        <div className="pt-2 flex flex-wrap items-center justify-between gap-3">
          <button
            type="button"
            onClick={handleCalculate}
            disabled={loading || (inputMode === "saved" && !selectedHoroscopeId)}
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-[#B8862B] to-[#9E6E1A] text-white font-bold text-xs shadow-md hover:shadow-lg transition-all cursor-pointer disabled:opacity-50"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>{language === "ta" ? "கணக்கிடப்படுகிறது..." : "Computing Ashtakavarga..."}</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>
                  {language === "ta"
                    ? "அஷ்டகவர்க்கம் & கக்ஷா கணக்கிடு"
                    : "Calculate Ashtakavarga & Kakshya"}
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

      {/* Results Studio Workspace */}
      {ashtakavargaData && (
        <div className="space-y-8">
          {/* Main Studio Navigation Tabs */}
          <div className="flex border-b border-[#DDE5F0] overflow-x-auto gap-2 text-xs sm:text-sm">
            <button
              type="button"
              onClick={() => setActiveTab("sav")}
              className={`flex items-center gap-2 py-3 px-4 font-bold border-b-2 whitespace-nowrap transition-colors cursor-pointer ${
                activeTab === "sav"
                  ? "border-[#B8862B] text-[#B8862B]"
                  : "border-transparent text-[#64748B] hover:text-[#102A4C]"
              }`}
            >
              <Grid className="w-4 h-4" />
              <span>{language === "ta" ? "சர்வ அஷ்டகவர்க்கம் (SAV)" : "Sarvashtakavarga (SAV - 337)"}</span>
              <span className="px-1.5 py-0.5 rounded-full text-[10px] bg-emerald-100 text-emerald-800 font-mono">
                337
              </span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("bav")}
              className={`flex items-center gap-2 py-3 px-4 font-bold border-b-2 whitespace-nowrap transition-colors cursor-pointer ${
                activeTab === "bav"
                  ? "border-[#B8862B] text-[#B8862B]"
                  : "border-transparent text-[#64748B] hover:text-[#102A4C]"
              }`}
            >
              <Award className="w-4 h-4" />
              <span>{language === "ta" ? "பின்ன அஷ்டகவர்க்கம் (BAV)" : "Bhinnashtakavarga (7 Grahas & Shodhana)"}</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("prastara")}
              className={`flex items-center gap-2 py-3 px-4 font-bold border-b-2 whitespace-nowrap transition-colors cursor-pointer ${
                activeTab === "prastara"
                  ? "border-[#B8862B] text-[#B8862B]"
                  : "border-transparent text-[#64748B] hover:text-[#102A4C]"
              }`}
            >
              <Layers className="w-4 h-4" />
              <span>{language === "ta" ? "பிரஸ்தார சக்கரம் (8-நபர் அணி)" : "Prastarashtakavarga (8-Donor Grid)"}</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("kakshya")}
              className={`flex items-center gap-2 py-3 px-4 font-bold border-b-2 whitespace-nowrap transition-colors cursor-pointer ${
                activeTab === "kakshya"
                  ? "border-[#B8862B] text-[#B8862B]"
                  : "border-transparent text-[#64748B] hover:text-[#102A4C]"
              }`}
            >
              <Flame className="w-4 h-4 text-amber-600" />
              <span>{language === "ta" ? "கக்ஷா கோச்சார ஆய்வு (3°45')" : "Kakshya Transit Timing Engine"}</span>
              <span className="px-1.5 py-0.5 rounded-full text-[10px] bg-amber-100 text-amber-800 font-mono">
                96 Kakshas
              </span>
            </button>
          </div>

          {/* TAB 1: SARVASHTAKAVARGA (SAV) */}
          {activeTab === "sav" && (
            <div className="space-y-8">
              {/* SAV KPI Metrics */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-4 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-1">
                  <div className="text-[11px] font-bold text-[#8C6D23] uppercase tracking-wider">
                    Total SAV Bindus
                  </div>
                  <div className="text-2xl font-serif font-bold text-[#102A4C]">
                    {ashtakavargaData.sarvashtakavarga.total_bindus} / 337
                  </div>
                  <div className="text-xs text-emerald-700 flex items-center gap-1 font-semibold">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Canonical Invariant Verified</span>
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-1">
                  <div className="text-[11px] font-bold text-[#8C6D23] uppercase tracking-wider">
                    Mathematical Mean
                  </div>
                  <div className="text-2xl font-serif font-bold text-[#102A4C]">
                    {ashtakavargaData.sarvashtakavarga.average_per_sign.toFixed(2)} pts
                  </div>
                  <div className="text-xs text-[#64748B]">
                    Benchmark threshold: 28 bindus
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-emerald-50/70 border border-emerald-200 shadow-2xs space-y-1">
                  <div className="flex items-center justify-between text-[11px] font-bold text-emerald-800 uppercase tracking-wider">
                    <span>Auspicious Signs</span>
                    <Star className="w-4 h-4 text-emerald-600 fill-emerald-600" />
                  </div>
                  <div className="text-2xl font-serif font-bold text-emerald-900">
                    {ashtakavargaData.sarvashtakavarga.auspicious_signs.length} Signs
                  </div>
                  <div className="text-xs text-emerald-700 truncate">
                    Bindus ≥ 28 (Protective transit zones)
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-rose-50/60 border border-rose-200 shadow-2xs space-y-1">
                  <div className="flex items-center justify-between text-[11px] font-bold text-rose-800 uppercase tracking-wider">
                    <span>Deficient Signs</span>
                    <AlertCircle className="w-4 h-4 text-rose-600" />
                  </div>
                  <div className="text-2xl font-serif font-bold text-rose-900">
                    {ashtakavargaData.sarvashtakavarga.inauspicious_signs.length} Signs
                  </div>
                  <div className="text-xs text-rose-700 truncate">
                    Bindus &lt; 28 (Caution required during transits)
                  </div>
                </div>
              </div>

              {/* Visual SAV Chart & Breakdown Table */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                {/* Left: Visual Chart */}
                <div className="lg:col-span-5 space-y-4">
                  <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-4">
                    <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
                      <div>
                        <h3 className="font-serif text-lg font-bold text-[#102A4C]">
                          Sarvashtakavarga Chakra
                        </h3>
                        <p className="text-xs text-[#64748B]">
                          Bindu concentration across 12 houses from Lagna
                        </p>
                      </div>

                      {/* Style Switcher */}
                      <div className="inline-flex p-1 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] text-xs">
                        <button
                          type="button"
                          onClick={() => setChartStyle("south")}
                          className={`px-2.5 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                            chartStyle === "south"
                              ? "bg-[#B8862B] text-white shadow-2xs"
                              : "text-[#64748B] hover:text-[#102A4C]"
                          }`}
                        >
                          South
                        </button>
                        <button
                          type="button"
                          onClick={() => setChartStyle("north")}
                          className={`px-2.5 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                            chartStyle === "north"
                              ? "bg-[#B8862B] text-white shadow-2xs"
                              : "text-[#64748B] hover:text-[#102A4C]"
                          }`}
                        >
                          North
                        </button>
                      </div>
                    </div>

                    <div className="p-4 rounded-2xl bg-[#FAF7F0] border border-[#E8DEC8]">
                      {chartStyle === "south" ? (
                        <SouthIndianChart
                          horoscope={savChartObject as unknown as HoroscopeResponse}
                          isSaved={Boolean(savedIdParam || (inputMode === "saved" && selectedHoroscopeId))}
                        />
                      ) : (
                        <NorthIndianChart
                          horoscope={savChartObject as unknown as HoroscopeResponse}
                          isSaved={Boolean(savedIdParam || (inputMode === "saved" && selectedHoroscopeId))}
                        />
                      )}
                    </div>
                  </div>
                </div>

                {/* Right: 12-Sign & 12-House SAV Breakdown Table */}
                <div className="lg:col-span-7 space-y-4">
                  <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-4">
                    <div>
                      <h4 className="font-serif text-base font-bold text-[#102A4C]">
                        12-House Sarvashtakavarga Distribution
                      </h4>
                      <p className="text-xs text-[#64748B]">
                        Evaluation of life domains and Gochara transit fertility per house.
                      </p>
                    </div>

                    <div className="overflow-x-auto">
                      <table className="w-full text-xs text-left">
                        <thead className="bg-[#FAF7F0] text-[#8C6D23] font-bold uppercase tracking-wider border-b border-[#E8DEC8]">
                          <tr>
                            <th className="py-2.5 px-3">House / Bhava</th>
                            <th className="py-2.5 px-3">Zodiac Sign</th>
                            <th className="py-2.5 px-3">Bindus</th>
                            <th className="py-2.5 px-3">Classification</th>
                            <th className="py-2.5 px-3">Domain</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#334155]">
                          {Array.from({ length: 12 }, (_, i) => i + 1).map((hNum) => {
                            const lagnaIdx = ashtakavargaData.lagna_sign_index;
                            const signIdx = ((lagnaIdx - 1 + (hNum - 1)) % 12) + 1;
                            const bindus = ashtakavargaData.sarvashtakavarga.sign_bindus[signIdx] || 0;
                            const signInfo = ZODIAC_SIGNS[signIdx];
                            const domain = HOUSE_DOMAINS[hNum];

                            const isVeryHigh = bindus >= 30;
                            const isAboveAvg = bindus >= 28;
                            const isDeficient = bindus < 25;

                            return (
                              <tr key={hNum} className="hover:bg-[#FAF6EC]/40 transition-colors">
                                <td className="py-2 px-3 font-bold text-[#102A4C]">
                                  House {hNum}
                                  {hNum === 1 && (
                                    <span className="text-[10px] text-[#B8862B] ml-1 font-semibold">
                                      (Lagna)
                                    </span>
                                  )}
                                </td>
                                <td className="py-2 px-3">
                                  <span className="font-semibold">{signInfo.en}</span>{" "}
                                  <span className="text-[10px] text-[#8C6D23]">({signInfo.ta})</span>
                                </td>
                                <td className="py-2 px-3 font-mono font-bold text-sm">
                                  {bindus}
                                </td>
                                <td className="py-2 px-3">
                                  <span
                                    className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold border ${
                                      isVeryHigh
                                        ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                                        : isAboveAvg
                                        ? "bg-teal-50 text-teal-800 border-teal-200"
                                        : isDeficient
                                        ? "bg-rose-50 text-rose-700 border-rose-200"
                                        : "bg-amber-50 text-amber-800 border-amber-200"
                                    }`}
                                  >
                                    {isVeryHigh
                                      ? "Excellent (≥ 30)"
                                      : isAboveAvg
                                      ? "Favorable (≥ 28)"
                                      : isDeficient
                                      ? "Deficient (< 25)"
                                      : "Moderate (25-27)"}
                                  </span>
                                </td>
                                <td className="py-2 px-3 text-[#64748B] text-[11px] truncate max-w-xs">
                                  {language === "ta" ? domain.ta : domain.en}
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>

              {/* Classical Shastra Guidance */}
              <div className="p-6 rounded-2xl bg-[#FAF7F0] border border-[#E8DEC8] text-xs text-[#52667E] space-y-3 shadow-2xs">
                <div className="flex items-center gap-2 text-[#8C6D23] font-bold text-sm">
                  <BookOpen className="w-4 h-4 text-[#B8862B]" />
                  <span>Classical Ashtakavarga Transit Rules (Brihat Parashara Hora Shastra)</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
                  <div className="space-y-1">
                    <strong className="text-[#102A4C] block">The 28-Bindu Line</strong>
                    <p className="leading-relaxed">
                      337 bindus across 12 signs yield an average of 28.08. Any sign with 28 or more bindus confers auspicious results when transited by natural benefics or malefics.
                    </p>
                  </div>
                  <div className="space-y-1">
                    <strong className="text-[#102A4C] block">Saturn &amp; Sade Sati Shield</strong>
                    <p className="leading-relaxed">
                      If Saturn transits natal Moon sign or adjacent signs with 30+ bindus, Sade Sati causes minimal distress and instead yields professional elevations and land acquisitions.
                    </p>
                  </div>
                  <div className="space-y-1">
                    <strong className="text-[#102A4C] block">10th &amp; 11th House Surplus</strong>
                    <p className="leading-relaxed">
                      Classical aphorisms state: if the 11th house has more bindus than the 10th, and the 10th more than the 12th, the native effortlessly accumulates great wealth and renown.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: BHINNASHTAKAVARGA (BAV) & SHODHANA REDUCTIONS */}
          {activeTab === "bav" && (
            <div className="space-y-6">
              {/* Planet Selector Pills */}
              <div className="flex flex-wrap items-center gap-2 p-3 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs">
                {PLANETS_7.map((p) => {
                  const isSelected = selectedPlanet === p;
                  const meta = PLANET_META[p];
                  const pBav = ashtakavargaData.bhinnashtakavarga[p];
                  return (
                    <button
                      key={p}
                      type="button"
                      onClick={() => setSelectedPlanet(p)}
                      className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-2 ${
                        isSelected
                          ? "bg-[#102A4C] text-white shadow-2xs"
                          : "bg-[#F8FAFC] text-[#64748B] hover:text-[#102A4C] hover:bg-[#F1F5F9]"
                      }`}
                    >
                      <span>{language === "ta" ? meta.ta : p}</span>
                      <span
                        className={`px-1.5 py-0.5 rounded-md text-[10px] font-mono ${
                          isSelected ? "bg-white/20 text-white" : "bg-slate-200 text-slate-700"
                        }`}
                      >
                        {pBav?.total_bindus || meta.expected} pts
                      </span>
                    </button>
                  );
                })}
              </div>

              {/* Selected Planet BAV Showcase */}
              {(() => {
                const bav = ashtakavargaData.bhinnashtakavarga[selectedPlanet];
                if (!bav) return null;

                return (
                  <div className="space-y-6">
                    {/* BAV & Shodhya Pinda Header Banner */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                      <div className="p-4 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-1">
                        <div className="text-[11px] font-bold text-[#8C6D23] uppercase tracking-wider">
                          {selectedPlanet} Total Bindus
                        </div>
                        <div className="text-2xl font-serif font-bold text-[#102A4C]">
                          {bav.total_bindus} / {bav.expected_total}
                        </div>
                        <div className="text-xs text-emerald-700 font-semibold">
                          Reconciles with BPHS Invariant
                        </div>
                      </div>

                      <div className="p-4 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-1">
                        <div className="text-[11px] font-bold text-[#8C6D23] uppercase tracking-wider">
                          Rashi Pinda (Sign Multiplier)
                        </div>
                        <div className="text-2xl font-serif font-bold text-[#102A4C]">
                          {bav.rashi_pinda ?? "—"}
                        </div>
                        <div className="text-xs text-[#64748B]">
                          Multipliers: Sun 10, Jupiter 10, etc.
                        </div>
                      </div>

                      <div className="p-4 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-1">
                        <div className="text-[11px] font-bold text-[#8C6D23] uppercase tracking-wider">
                          Graha Pinda (Planet Multiplier)
                        </div>
                        <div className="text-2xl font-serif font-bold text-[#102A4C]">
                          {bav.graha_pinda ?? "—"}
                        </div>
                        <div className="text-xs text-[#64748B]">
                          Planetary occupation weights
                        </div>
                      </div>

                      <div className="p-4 rounded-2xl bg-[#FAF2DE]/70 border border-[#D8BD80] shadow-2xs space-y-1">
                        <div className="flex items-center justify-between text-[11px] font-bold text-[#8C6D23] uppercase tracking-wider">
                          <span>Shodhya Pinda</span>
                          <Award className="w-4 h-4 text-[#B8862B]" />
                        </div>
                        <div className="text-2xl font-serif font-bold text-[#8C6D23]">
                          {bav.shodhya_pinda ?? "—"}
                        </div>
                        <div className="text-xs text-[#52667E] truncate">
                          Net Karmic Force (Rashi + Graha)
                        </div>
                      </div>
                    </div>

                    {/* Shodhana Reductions Table */}
                    <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-4">
                      <div>
                        <h4 className="font-serif text-base font-bold text-[#102A4C]">
                          {selectedPlanet} BAV &amp; Shodhana Reduction Steps
                        </h4>
                        <p className="text-xs text-[#64748B]">
                          Step-by-step classical reduction via Trikona Shodhana and Ekadhipatya Shodhana.
                        </p>
                      </div>

                      <div className="overflow-x-auto">
                        <table className="w-full text-xs text-left">
                          <thead className="bg-[#FAF7F0] text-[#8C6D23] font-bold uppercase tracking-wider border-b border-[#E8DEC8]">
                            <tr>
                              <th className="py-2.5 px-3">Sign Index</th>
                              <th className="py-2.5 px-3">Zodiac Sign</th>
                              <th className="py-2.5 px-3">House</th>
                              <th className="py-2.5 px-3">Raw BAV Bindus</th>
                              <th className="py-2.5 px-3">After Trikona</th>
                              <th className="py-2.5 px-3">After Ekadhipatya</th>
                              <th className="py-2.5 px-3">Net Shodhita</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#334155]">
                            {Array.from({ length: 12 }, (_, i) => i + 1).map((sIdx) => {
                              const signInfo = ZODIAC_SIGNS[sIdx];
                              const lagnaIdx = ashtakavargaData.lagna_sign_index;
                              const houseNum = ((sIdx - lagnaIdx + 12) % 12) + 1;
                              const raw = bav.sign_bindus[sIdx] || 0;
                              const trikona = bav.trikona_reduced?.[sIdx] ?? raw;
                              const ekadh = bav.ekadhipatya_reduced?.[sIdx] ?? trikona;

                              return (
                                <tr key={sIdx} className="hover:bg-[#FAF6EC]/40 transition-colors">
                                  <td className="py-2 px-3 font-mono font-bold text-[#8C6D23]">
                                    #{sIdx}
                                  </td>
                                  <td className="py-2 px-3 font-semibold text-[#102A4C]">
                                    {signInfo.en}{" "}
                                    <span className="text-[10px] text-[#8C6D23]">
                                      ({signInfo.ta})
                                    </span>
                                  </td>
                                  <td className="py-2 px-3">
                                    <span className="px-1.5 py-0.5 rounded-sm bg-[#F1F5F9] text-[#475569] font-bold text-[10px]">
                                      H{houseNum}
                                    </span>
                                  </td>
                                  <td className="py-2 px-3 font-mono font-bold text-sm">
                                    {raw}
                                  </td>
                                  <td className="py-2 px-3 font-mono text-slate-700">
                                    {trikona}
                                  </td>
                                  <td className="py-2 px-3 font-mono text-slate-700">
                                    {ekadh}
                                  </td>
                                  <td className="py-2 px-3 font-mono font-bold text-emerald-700">
                                    {ekadh}
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                );
              })()}
            </div>
          )}

          {/* TAB 3: PRASTARASHTAKAVARGA (8-DONOR GRID) */}
          {activeTab === "prastara" && ashtakavargaData.prastara && (
            <div className="space-y-6">
              {/* Planet Selector Pills */}
              <div className="flex flex-wrap items-center gap-2 p-3 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs">
                {PLANETS_7.map((p) => {
                  const isSelected = selectedPlanet === p;
                  return (
                    <button
                      key={p}
                      type="button"
                      onClick={() => setSelectedPlanet(p)}
                      className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                        isSelected
                          ? "bg-[#102A4C] text-white shadow-2xs"
                          : "bg-[#F8FAFC] text-[#64748B] hover:text-[#102A4C]"
                      }`}
                    >
                      {p} Prastara
                    </button>
                  );
                })}
              </div>

              {/* Selected Planet Prastara Matrix */}
              {(() => {
                const prastara: PrastaraDetail | undefined =
                  ashtakavargaData.prastara[selectedPlanet];
                if (!prastara) return null;

                return (
                  <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-4">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-[#F1F5F9] pb-4">
                      <div>
                        <h4 className="font-serif text-lg font-bold text-[#102A4C]">
                          {selectedPlanet} Prastarashtakavarga Matrix (8 Donors × 12 Signs)
                        </h4>
                        <p className="text-xs text-[#64748B]">
                          Rows ordered by classical Kaksha speed sequence: Saturn (slowest) to Lagna (fastest).
                        </p>
                      </div>
                      <div className="flex items-center gap-2 text-xs">
                        <span className="px-2.5 py-1 rounded-md bg-emerald-50 text-emerald-800 font-bold border border-emerald-200">
                          Total: {prastara.total_bindus} Bindus
                        </span>
                      </div>
                    </div>

                    <div className="overflow-x-auto">
                      <table className="w-full text-xs text-center border-collapse">
                        <thead>
                          <tr className="bg-[#FAF7F0] text-[#8C6D23] font-bold border-b border-[#E8DEC8]">
                            <th className="py-3 px-3 text-left">Donor / Kaksha Ruler</th>
                            {Array.from({ length: 12 }, (_, i) => i + 1).map((sIdx) => (
                              <th key={sIdx} className="py-3 px-2 font-mono">
                                <div>{ZODIAC_SIGNS[sIdx]?.en.slice(0, 3)}</div>
                                <div className="text-[9px] font-normal text-[#64748B]">
                                  #{sIdx}
                                </div>
                              </th>
                            ))}
                            <th className="py-3 px-3 text-right">Row Sum</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#334155]">
                          {prastara.rows.map((row) => (
                            <tr key={row.contributor} className="hover:bg-[#FAF6EC]/40 transition-colors">
                              <td className="py-2.5 px-3 text-left font-bold text-[#102A4C]">
                                {row.contributor}
                              </td>
                              {Array.from({ length: 12 }, (_, i) => i + 1).map((sIdx) => {
                                const val = row.sign_bindus[sIdx] || row.sign_bindus[String(sIdx)] || 0;
                                return (
                                  <td
                                    key={sIdx}
                                    className={`py-2 px-1 font-mono ${
                                      val === 1
                                        ? "text-emerald-700 font-bold bg-emerald-50/50"
                                        : "text-slate-300"
                                    }`}
                                  >
                                    {val === 1 ? "1" : "—"}
                                  </td>
                                );
                              })}
                              <td className="py-2.5 px-3 text-right font-bold text-[#8C6D23] font-mono">
                                {row.total_contributions}
                              </td>
                            </tr>
                          ))}

                          {/* Column Totals Row */}
                          <tr className="bg-[#FAF2DE]/50 font-bold text-[#102A4C] border-t-2 border-[#D8BD80]">
                            <td className="py-2.5 px-3 text-left uppercase text-[11px] tracking-wider text-[#8C6D23]">
                              BAV Column Total
                            </td>
                            {Array.from({ length: 12 }, (_, i) => i + 1).map((sIdx) => {
                              const colTotal =
                                prastara.sign_totals[sIdx] ||
                                prastara.sign_totals[String(sIdx)] ||
                                0;
                              return (
                                <td key={sIdx} className="py-2 px-1 font-mono text-sm text-[#8C6D23]">
                                  {colTotal}
                                </td>
                              );
                            })}
                            <td className="py-2.5 px-3 text-right font-mono text-sm text-[#8C6D23]">
                              {prastara.total_bindus}
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                );
              })()}
            </div>
          )}

          {/* TAB 4: KAKSHYA TRANSIT TIMING ENGINE (3°45') */}
          {activeTab === "kakshya" && (
            <div className="space-y-8">
              {/* Introduction Banner */}
              <div className="p-6 rounded-2xl bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 shadow-xs space-y-2">
                <div className="flex items-center gap-2 text-amber-900 font-bold">
                  <Flame className="w-5 h-5 text-amber-600 fill-amber-600" />
                  <h3 className="font-serif text-lg">
                    {language === "ta"
                      ? "கக்ஷா கோச்சார ஆய்வு (3° 45' நுட்பப் பிரிவுகள்)"
                      : "Kakshya Transit Timing Engine — Pinpoint Micro-Windows"}
                  </h3>
                </div>
                <p className="text-xs text-amber-800 leading-relaxed max-w-4xl">
                  {language === "ta"
                    ? "ஒவ்வொரு ராசியும் தலா 3° 45' கொண்ட 8 கக்ஷா பிரிவுகளாக பிரிக்கப்படுகிறது (சனி, குரு, செவ்வாய், சூரியன், சுக்கிரன், புதன், சந்திரன், லக்னம்). கோச்சார கிரகம் செல்லும் கக்ஷாவில் உங்கள் அசல் ஜாதகத்தில் பிந்து (1) இருந்தால், அந்த காலகட்டம் மகா சுப பலன்களை வழங்கும். பிந்து இல்லையெனில் தற்காலிக தடைகள் ஏற்படும்."
                    : "Each zodiac sign of 30° is divided into eight equal Kakshas of exactly 3°45' each, ruled in strict planetary speed order (Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon, Lagna). When a transiting planet enters a Kaksha where it earned a natal bindu in Prastara, it triggers breakthrough auspicious events."}
                </p>
              </div>

              {/* Interactive Transit Evaluator Tool Card */}
              <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-4">
                <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
                  <h4 className="font-serif text-base font-bold text-[#102A4C]">
                    Interactive Live Kakshya Transit Checker
                  </h4>
                  <span className="text-xs text-[#64748B]">
                    Span: exactly 3° 45&apos; per Kaksha
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
                  <div>
                    <label className="block font-semibold text-[#334155] mb-1">
                      Transiting Planet
                    </label>
                    <select
                      value={transitPlanet}
                      onChange={(e) => setTransitPlanet(e.target.value as any)}
                      className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] bg-white text-[#102A4C] font-semibold focus:outline-hidden focus:border-[#B8862B]"
                    >
                      {PLANETS_7.map((p) => (
                        <option key={p} value={p}>
                          {p}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block font-semibold text-[#334155] mb-1">
                      Transit Zodiac Sign
                    </label>
                    <select
                      value={transitSignIndex}
                      onChange={(e) => setTransitSignIndex(parseInt(e.target.value, 10))}
                      className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] bg-white text-[#102A4C] font-semibold focus:outline-hidden focus:border-[#B8862B]"
                    >
                      {Array.from({ length: 12 }, (_, i) => i + 1).map((sIdx) => (
                        <option key={sIdx} value={sIdx}>
                          {sIdx}. {ZODIAC_SIGNS[sIdx]?.en} ({ZODIAC_SIGNS[sIdx]?.ta})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block font-semibold text-[#334155] mb-1">
                      Degree in Sign (0.0° – 29.99°)
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      max="29.99"
                      value={transitDegreeInSign}
                      onChange={(e) => setTransitDegreeInSign(parseFloat(e.target.value) || 0)}
                      className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] bg-white text-[#102A4C] font-mono focus:outline-hidden focus:border-[#B8862B]"
                    />
                  </div>
                </div>

                <div className="pt-2 flex items-center justify-between">
                  <button
                    type="button"
                    onClick={handleEvaluateTransit}
                    disabled={evaluatingTransit}
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#102A4C] text-white font-bold text-xs shadow-md hover:bg-[#1E3A8A] transition-all cursor-pointer disabled:opacity-50"
                  >
                    {evaluatingTransit ? (
                      <>
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        <span>Evaluating Kakshya...</span>
                      </>
                    ) : (
                      <>
                        <Flame className="w-3.5 h-3.5 text-amber-400" />
                        <span>Evaluate Transit Position</span>
                      </>
                    )}
                  </button>

                  <div className="text-xs text-[#64748B]">
                    Current Presets: Saturn in Pisces (12), Jupiter in Taurus (2)
                  </div>
                </div>

                {/* Live Transit Result Banner */}
                {transitResult && (
                  <div
                    className={`mt-4 p-5 rounded-2xl border text-xs space-y-3 ${
                      transitResult.effect === "Auspicious"
                        ? "bg-emerald-50/80 border-emerald-200 text-emerald-900"
                        : "bg-rose-50/80 border-rose-200 text-rose-900"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 font-bold text-sm">
                        {transitResult.effect === "Auspicious" ? (
                          <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                        ) : (
                          <AlertCircle className="w-5 h-5 text-rose-600" />
                        )}
                        <span>
                          {transitResult.transiting_planet} Transit at {transitResult.sign_name}{" "}
                          {formatDm(transitResult.degree_in_sign)}: {transitResult.effect} Window
                        </span>
                      </div>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-bold border ${
                          transitResult.effect === "Auspicious"
                            ? "bg-emerald-100 text-emerald-800 border-emerald-300"
                            : "bg-rose-100 text-rose-800 border-rose-300"
                        }`}
                      >
                        {transitResult.has_bindu ? "Bindu Present (1)" : "No Bindu (0)"}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-white/70 p-3 rounded-xl border border-black/5">
                      <div>
                        <span className="text-[#64748B] block text-[11px]">Kakshya Division:</span>
                        <strong className="text-sm">
                          Kakshya #{transitResult.kaksha_number} of 8
                        </strong>
                      </div>
                      <div>
                        <span className="text-[#64748B] block text-[11px]">Kakshya Ruler (Lord):</span>
                        <strong className="text-sm text-[#102A4C]">
                          {transitResult.kaksha_lord}
                        </strong>
                      </div>
                      <div>
                        <span className="text-[#64748B] block text-[11px]">Active Degree Span:</span>
                        <strong className="text-sm font-mono text-[#8C6D23]">
                          {transitResult.kaksha_range}
                        </strong>
                      </div>
                    </div>

                    <p className="leading-relaxed">{transitResult.interpretation}</p>
                  </div>
                )}
              </div>

              {/* 96-Kaksha Master Matrix for Selected Planet */}
              {ashtakavargaData.kaksha_grids?.[selectedPlanet] && (
                <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-4">
                  <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
                    <h4 className="font-serif text-base font-bold text-[#102A4C]">
                      96-Kaksha Master Map for {selectedPlanet}
                    </h4>
                    <span className="text-xs text-[#64748B]">
                      12 Signs × 8 Kaksha Divisions
                    </span>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-center border-collapse">
                      <thead>
                        <tr className="bg-[#FAF7F0] text-[#8C6D23] font-bold border-b border-[#E8DEC8]">
                          <th className="py-3 px-3 text-left">Sign</th>
                          {KAKSHA_LORDS_ORDER.map((lord, idx) => (
                            <th key={lord} className="py-3 px-2">
                              <div>K#{idx + 1}</div>
                              <div className="text-[10px] text-[#64748B]">{lord.slice(0, 3)}</div>
                            </th>
                          ))}
                          <th className="py-3 px-3 text-right">Sign Bindus</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#334155]">
                        {ashtakavargaData.kaksha_grids[selectedPlanet].map((signDetail) => (
                          <tr key={signDetail.sign_index} className="hover:bg-[#FAF6EC]/40 transition-colors">
                            <td className="py-2 px-3 text-left font-bold text-[#102A4C]">
                              #{signDetail.sign_index} {signDetail.sign_name}
                            </td>
                            {signDetail.divisions.map((kDiv) => (
                              <td
                                key={kDiv.kaksha_number}
                                className={`py-2 px-1 font-mono ${
                                  kDiv.has_bindu
                                    ? "bg-emerald-50 text-emerald-800 font-bold border border-emerald-200"
                                    : "text-slate-300"
                                }`}
                                title={`${signDetail.sign_name} K#${kDiv.kaksha_number} (${kDiv.lord}): ${kDiv.range_display} -> ${kDiv.has_bindu ? "Bindu (1)" : "Zero (0)"}`}
                              >
                                {kDiv.has_bindu ? "1" : "—"}
                              </td>
                            ))}
                            <td className="py-2 px-3 text-right font-mono font-bold text-[#8C6D23]">
                              {signDetail.total_bindus}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function AshtakavargaPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-[50vh] flex items-center justify-center">
          <div className="w-8 h-8 border-4 border-[#B8862B] border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <AshtakavargaContent />
    </Suspense>
  );
}
