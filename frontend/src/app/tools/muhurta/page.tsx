"use client";

import React, { useState, useEffect, useMemo, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  FindMuhurtaResponse,
  CandidateSlot,
  OccasionItem,
} from "@/lib/types";
import { findMuhurtas, getOccasions } from "@/lib/api";
import {
  Calendar,
  Clock,
  Sparkles,
  MapPin,
  RefreshCw,
  AlertCircle,
  ShieldCheck,
  ShieldAlert,
  ChevronLeft,
  ChevronRight,
  Flame,
  CheckCircle2,
  XCircle,
  Info,
  Layers,
  ArrowRight,
  Heart,
  Home,
  ShoppingBag,
  Car,
  Briefcase,
  Sliders,
  Filter,
  Star,
  Bookmark,
  Check,
  Compass,
  User,
  Users,
} from "lucide-react";

interface CityPreset {
  name_en: string;
  name_ta: string;
  lat: number;
  lon: number;
  tz: string;
}

const CITY_PRESETS: CityPreset[] = [
  { name_en: "Chennai", name_ta: "சென்னை", lat: 13.0827, lon: 80.2707, tz: "Asia/Kolkata" },
  { name_en: "Madurai", name_ta: "மதுரை", lat: 9.9252, lon: 78.1198, tz: "Asia/Kolkata" },
  { name_en: "Coimbatore", name_ta: "கோயம்புத்தூர்", lat: 11.0168, lon: 76.9558, tz: "Asia/Kolkata" },
  { name_en: "Tiruchirappalli", name_ta: "திருச்சி", lat: 10.7905, lon: 78.7047, tz: "Asia/Kolkata" },
  { name_en: "Bengaluru", name_ta: "பெங்களூரு", lat: 12.9716, lon: 77.5946, tz: "Asia/Kolkata" },
  { name_en: "Mumbai", name_ta: "மும்பை", lat: 19.0760, lon: 72.8777, tz: "Asia/Kolkata" },
  { name_en: "New Delhi", name_ta: "புது தில்லி", lat: 28.6139, lon: 77.2090, tz: "Asia/Kolkata" },
  { name_en: "Singapore", name_ta: "சிங்கப்பூர்", lat: 1.3521, lon: 103.8198, tz: "Asia/Singapore" },
  { name_en: "London", name_ta: "லண்டன்", lat: 51.5074, lon: -0.1278, tz: "Europe/London" },
  { name_en: "New York", name_ta: "நியூயார்க்", lat: 40.7128, lon: -74.0060, tz: "America/New_York" },
];

const PREMIER_OCCASIONS = [
  {
    code: "marriage",
    name_en: "Marriage (Vivaha)",
    name_ta: "திருமணம் (விவாஹ முகூர்த்தம்)",
    icon: Heart,
    color: "from-rose-500 to-pink-600",
    badge_en: "Lagna Shuddhi • Ashtama Shuddhi • Sapthama Cleanliness",
    badge_ta: "லக்ன சுத்தி • அஷ்டம சுத்தி • சப்தம தோஷ நீக்கம்",
    desc_en: "Pristine wedding timing avoiding Rikta tithis, 8th house occupants, and 7th house malefics.",
    desc_ta: "ரிஷபம், மிதுனம், கடகம் போன்ற சுப லக்னங்களில் மங்களகரமான திருமண முகூர்த்தம்.",
  },
  {
    code: "griha_pravesham",
    name_en: "Housewarming (Griha Pravesham)",
    name_ta: "கிரகப்பிரவேசம் (புதுமனை புகுவிழா)",
    icon: Home,
    color: "from-amber-500 to-orange-600",
    badge_en: "Sthira/Dual Lagna • 4th Sukhasthana • 8th Shuddhi",
    badge_ta: "ஸ்திர/உபய லக்னம் • 4-ம் சுகஸ்தானம் • அஷ்டம சுத்தி",
    desc_en: "First auspicious entry into new dwelling ensuring domestic peace, family prosperity, and longevity.",
    desc_ta: "வீட்டில் சுப அதிர்வுகள் நிலைத்திருக்க ஸ்திர லக்னத்தில் பால் காய்ச்சும் நன்னாட்கள்.",
  },
  {
    code: "shop_opening",
    name_en: "Shop & Business Launch",
    name_ta: "வியாபாரத் துவக்கம் & கடை திறப்பு",
    icon: ShoppingBag,
    color: "from-emerald-500 to-teal-600",
    badge_en: "Budha (Mercury) Hora • 11th Labhasthana • 10th Karmasthana",
    badge_ta: "புதன் ஹோரை • 11-ம் லாபஸ்தானம் • 10-ம் கர்மஸ்தானம்",
    desc_en: "Commercial inauguration with Mercury strength, profitable Tithis, and steady client footfall.",
    desc_ta: "வணிக வளர்ச்சி, தொடர் வாடிக்கையாளர் வரவு மற்றும் லாபப் பெருக்கத்திற்கான சுப நேரம்.",
  },
  {
    code: "vehicle_purchase",
    name_en: "Vehicle Purchase & Delivery",
    name_ta: "வாகனம் வாங்குதல் & வண்டி எடுத்தல்",
    icon: Car,
    color: "from-blue-500 to-indigo-600",
    badge_en: "Shukra Vahana Hora • 4th Bhava Protection • Chara Stars",
    badge_ta: "சுக்கிர ஹோரை • 4-ம் வாகன ஸ்தானம் • விபத்து இல்லா பாதுகாப்பு",
    desc_en: "Auspicious delivery timing under Venus/Moon horas ensuring smooth travels and accident-free rides.",
    desc_ta: "சுக்கிரனின் அருளுடன் விபத்து இன்றி க்ஷேமமாக பயணிக்க புதிய வாகனம் எடுக்கும் முகூர்த்தம்.",
  },
];

const NAKSHATRA_OPTIONS = [
  "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",
  "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
  "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Moola", "Purva Ashadha",
  "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
  "Uttara Bhadrapada", "Revati"
];

const RASHI_OPTIONS = [
  "Aries (மேஷம்)", "Taurus (ரிஷபம்)", "Gemini (மிதுனம்)", "Cancer (கடகம்)",
  "Leo (சிம்மம்)", "Virgo (கன்னி)", "Libra (துலாம்)", "Scorpio (விருச்சிகம்)",
  "Sagittarius (தனுசு)", "Capricorn (மகரம்)", "Aquarius (கும்பம்)", "Pisces (மீனம்)"
];

function MuhurtaStudioInner() {
  const { language } = useLanguage();
  const searchParams = useSearchParams();

  // Occasion selection
  const initialOccasion = searchParams.get("occasion") || "marriage";
  const [selectedOccasionCode, setSelectedOccasionCode] = useState<string>(initialOccasion);
  const [allOccasions, setAllOccasions] = useState<OccasionItem[]>([]);

  // Search parameters
  const [startDateStr, setStartDateStr] = useState<string>(() => {
    return new Date().toISOString().split("T")[0];
  });
  const [endDateStr, setEndDateStr] = useState<string>(() => {
    const d = new Date();
    d.setDate(d.getDate() + 30);
    return d.toISOString().split("T")[0];
  });

  const [selectedCity, setSelectedCity] = useState<CityPreset>(CITY_PRESETS[0]);
  const [latitude, setLatitude] = useState<number>(CITY_PRESETS[0].lat);
  const [longitude, setLongitude] = useState<number>(CITY_PRESETS[0].lon);
  const [timezoneStr, setTimezoneStr] = useState<string>(CITY_PRESETS[0].tz);
  const [preferredTimeRange, setPreferredTimeRange] = useState<string>("morning");

  // Optional Birth details
  const [showBirthDetails, setShowBirthDetails] = useState<boolean>(false);
  const [groomNak, setGroomNak] = useState<number>(0);
  const [groomRashi, setGroomRashi] = useState<number>(0);
  const [brideNak, setBrideNak] = useState<number>(0);
  const [brideRashi, setBrideRashi] = useState<number>(0);
  const [nativeNak, setNativeNak] = useState<number>(0);
  const [nativeRashi, setNativeRashi] = useState<number>(0);

  // Results state
  const [results, setResults] = useState<FindMuhurtaResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Tabs & Filters
  const [activeTab, setActiveTab] = useState<"candidates" | "calendar" | "rules" | "saved">("candidates");
  const [statusFilter, setStatusFilter] = useState<"all" | "pristine" | "advisories">("all");
  const [selectedCandidateModal, setSelectedCandidateModal] = useState<CandidateSlot | null>(null);
  const [savedSlots, setSavedSlots] = useState<CandidateSlot[]>([]);

  // Load occasions list
  useEffect(() => {
    const loadOccasions = async () => {
      try {
        const res = await getOccasions(false);
        if (res?.occasions) {
          setAllOccasions(res.occasions);
        }
      } catch (e) {
        // Fallback silently if occasions endpoint fails
      }
    };
    loadOccasions();
  }, []);

  // Set date ranges helper
  const setRangeSpan = (days: number) => {
    const start = new Date(startDateStr);
    const end = new Date(start);
    end.setDate(end.getDate() + days);
    setEndDateStr(end.toISOString().split("T")[0]);
  };

  const handleSelectCity = (city: CityPreset) => {
    setSelectedCity(city);
    setLatitude(city.lat);
    setLongitude(city.lon);
    setTimezoneStr(city.tz);
  };

  const executeSearch = async () => {
    setLoading(true);
    setError(null);

    // Build birth details object if supplied
    let birthDetailsPayload: Record<string, any> | undefined = undefined;
    if (selectedOccasionCode === "marriage") {
      if (groomNak > 0 || groomRashi > 0 || brideNak > 0 || brideRashi > 0) {
        birthDetailsPayload = {
          groom_nakshatra: groomNak > 0 ? groomNak : undefined,
          groom_rashi: groomRashi > 0 ? groomRashi : undefined,
          bride_nakshatra: brideNak > 0 ? brideNak : undefined,
          bride_rashi: brideRashi > 0 ? brideRashi : undefined,
        };
      }
    } else {
      if (nativeNak > 0 || nativeRashi > 0) {
        birthDetailsPayload = {
          native_nakshatra: nativeNak > 0 ? nativeNak : undefined,
          native_rashi: nativeRashi > 0 ? nativeRashi : undefined,
        };
      }
    }

    try {
      const res = await findMuhurtas({
        occasion_code: selectedOccasionCode,
        start_date: startDateStr,
        end_date: endDateStr,
        latitude,
        longitude,
        location_name: `${selectedCity.name_en}, India`,
        timezone: timezoneStr,
        preferred_time_range: preferredTimeRange,
        birth_details: birthDetailsPayload,
        limit: 100,
      });
      setResults(res);
      setActiveTab("candidates");
    } catch (err: any) {
      setError(err?.message || "Failed to search candidate Muhurta slots.");
    } finally {
      setLoading(false);
    }
  };

  // Run search on initial load
  useEffect(() => {
    executeSearch();
  }, [selectedOccasionCode]);

  // Filtered candidate slots
  const filteredCandidates = useMemo(() => {
    if (!results?.candidates) return [];
    if (statusFilter === "pristine") {
      return results.candidates.filter((c) => c.status === "meets_configured_rules");
    }
    if (statusFilter === "advisories") {
      return results.candidates.filter(
        (c) => c.status === "meets_rules_with_advisories" || c.status === "meets_configured_rules"
      );
    }
    return results.candidates;
  }, [results, statusFilter]);

  // Bookmark toggle
  const toggleSaveSlot = (slot: CandidateSlot) => {
    if (savedSlots.some((s) => s.id === slot.id)) {
      setSavedSlots(savedSlots.filter((s) => s.id !== slot.id));
    } else {
      setSavedSlots([...savedSlots, slot]);
    }
  };

  return (
    <div className="min-h-screen bg-[#F4F6F9] text-[#102A4C]">
      {/* Top Header & Breadcrumbs */}
      <div className="bg-white border-b border-[#DDE5F0] sticky top-0 z-20 shadow-2xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4">
          <Breadcrumbs
            items={[
              { label: language === "ta" ? "முகப்பு" : "Home", href: "/" },
              { label: language === "ta" ? "கருவிகள்" : "Tools", href: "/tools" },
              {
                label:
                  language === "ta"
                    ? "சுப முகூர்த்த கால நிர்ணய அரங்கம்"
                    : "Muhurta Event Matching Studio",
              },
            ]}
          />

          <div className="mt-3 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold uppercase tracking-wider mb-1">
                <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
                <span>{language === "ta" ? "முழுமையான சாஸ்திர முகூர்த்த இயந்திரம்" : "Vedic Muhurta Precision Engine"}</span>
              </div>
              <h1 className="font-serif text-2xl sm:text-3xl font-bold text-[#102A4C]">
                {language === "ta"
                  ? "சுப முகூர்த்த கால நிர்ணய அரங்கம்"
                  : "Comprehensive Muhurta Event Matching Studio"}
              </h1>
              <p className="text-xs sm:text-sm text-[#52667E] mt-0.5">
                {language === "ta"
                  ? "திருமணம், புதுமனை புகுவிழா, வர்த்தகத் துவக்கம் மற்றும் வாகன முகூர்த்தங்களுக்கான சாஸ்திர விதிமுறை வடிகட்டல்."
                  : "Automated multi-criteria astrological matching and candidate scoring for Marriage, Griha Pravesha, Shop Launch, and Vehicle Purchase."}
              </p>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={executeSearch}
                disabled={loading}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#102A4C] hover:bg-[#16365C] text-white text-xs font-semibold shadow-xs transition-all cursor-pointer"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-amber-300" : ""}`} />
                <span>{loading ? (language === "ta" ? "ஆராய்கிறது..." : "Searching...") : (language === "ta" ? "முகூர்த்தம் தேடு" : "Find Muhurtas")}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-8">
        {/* 1. PREMIER OCCASIONS HERO SELECTOR */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold uppercase tracking-wider text-[#52667E]">
              {language === "ta" ? "முதன்மை சுப நிகழ்வுகள் / Premier Ceremonies" : "Select Auspicious Ceremony"}
            </h2>
            <div className="text-xs text-[#52667E]">
              {language === "ta" ? "அல்லது 21 நிகழ்வுகளிலிருந்து தேர்ந்தெடுக்கவும்" : "Or choose from 21 traditional occasions"}
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {PREMIER_OCCASIONS.map((occ) => {
              const isSelected = selectedOccasionCode === occ.code;
              const Icon = occ.icon;

              return (
                <div
                  key={occ.code}
                  onClick={() => setSelectedOccasionCode(occ.code)}
                  className={`p-5 rounded-3xl border-2 transition-all cursor-pointer relative overflow-hidden group ${
                    isSelected
                      ? "bg-white border-[#102A4C] shadow-lg ring-2 ring-[#102A4C]/10 scale-[1.01]"
                      : "bg-white border-[#DDE5F0] hover:border-[#3478F6]/40 hover:shadow-xs"
                  }`}
                >
                  {isSelected && (
                    <div className="absolute top-0 right-0 bg-[#102A4C] text-white p-1 rounded-bl-xl">
                      <Check className="w-3.5 h-3.5" />
                    </div>
                  )}

                  <div className="flex items-center gap-3">
                    <div
                      className={`w-11 h-11 rounded-2xl flex items-center justify-center text-white bg-linear-to-br ${occ.color} shadow-xs shrink-0`}
                    >
                      <Icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-serif font-bold text-base text-[#102A4C]">
                        {language === "ta" ? occ.name_ta.split(" (")[0] : occ.name_en.split(" (")[0]}
                      </h3>
                      <div className="text-[11px] font-medium text-[#52667E]">
                        {language === "ta" ? occ.name_en : occ.name_ta}
                      </div>
                    </div>
                  </div>

                  <div className="mt-3.5 pt-3 border-t border-[#F1F5F9] space-y-1.5">
                    <div className="inline-block px-2 py-0.5 rounded-md bg-[#FAF8F5] border border-[#E2E8F0] text-[10px] font-bold text-[#8C6D23] uppercase tracking-wider">
                      {language === "ta" ? occ.badge_ta : occ.badge_en}
                    </div>
                    <p className="text-[11px] text-[#52667E] line-clamp-2 leading-relaxed">
                      {language === "ta" ? occ.desc_ta : occ.desc_en}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Full Occasions Catalog Dropdown */}
          {allOccasions.length > 0 && (
            <div className="flex items-center gap-3 pt-2">
              <span className="text-xs font-bold text-[#52667E]">
                {language === "ta" ? "பிற அனைத்து நிகழ்வுகள்:" : "All 21 Life Events:"}
              </span>
              <select
                value={selectedOccasionCode}
                onChange={(e) => setSelectedOccasionCode(e.target.value)}
                className="px-3 py-1.5 rounded-xl border border-[#DDE5F0] bg-white text-xs font-semibold text-[#102A4C] focus:outline-hidden focus:border-[#3478F6]"
              >
                {allOccasions.map((o) => (
                  <option key={o.code} value={o.code}>
                    {language === "ta" ? o.name_ta : o.name_en} ({o.code})
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* 2. SEARCH & CRITERIA CONFIGURATION DRAWER */}
        <div className="p-6 rounded-3xl bg-white border border-[#DDE5F0] shadow-xs space-y-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
            {/* Start Date */}
            <div>
              <label className="block text-[11px] font-bold text-[#52667E] uppercase tracking-wider mb-1">
                {language === "ta" ? "தொடக்கத் தேதி / Start Date" : "Start Date"}
              </label>
              <input
                type="date"
                value={startDateStr}
                onChange={(e) => setStartDateStr(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] font-medium text-[#102A4C]"
              />
            </div>

            {/* End Date with Spans */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-[11px] font-bold text-[#52667E] uppercase tracking-wider">
                  {language === "ta" ? "முடிவுத் தேதி / End Date" : "End Date"}
                </label>
                <div className="flex gap-1">
                  {[14, 30, 60].map((days) => (
                    <button
                      key={days}
                      type="button"
                      onClick={() => setRangeSpan(days)}
                      className="text-[10px] text-[#3478F6] hover:underline font-bold"
                    >
                      +{days}d
                    </button>
                  ))}
                </div>
              </div>
              <input
                type="date"
                value={endDateStr}
                onChange={(e) => setEndDateStr(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] font-medium text-[#102A4C]"
              />
            </div>

            {/* City Preset */}
            <div>
              <label className="block text-[11px] font-bold text-[#52667E] uppercase tracking-wider mb-1">
                {language === "ta" ? "நகரம் / Location" : "Location"}
              </label>
              <select
                value={selectedCity.name_en}
                onChange={(e) => {
                  const f = CITY_PRESETS.find((c) => c.name_en === e.target.value);
                  if (f) handleSelectCity(f);
                }}
                className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] font-medium text-[#102A4C]"
              >
                {CITY_PRESETS.map((c) => (
                  <option key={c.name_en} value={c.name_en}>
                    {language === "ta" ? c.name_ta : c.name_en} ({c.name_en})
                  </option>
                ))}
              </select>
            </div>

            {/* Preferred Time Window */}
            <div>
              <label className="block text-[11px] font-bold text-[#52667E] uppercase tracking-wider mb-1">
                {language === "ta" ? "விருப்ப நேரம் / Preferred Hours" : "Preferred Time"}
              </label>
              <select
                value={preferredTimeRange}
                onChange={(e) => setPreferredTimeRange(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] font-medium text-[#102A4C]"
              >
                <option value="morning">🌅 {language === "ta" ? "காலை (06:00 - 12:00)" : "Morning (06:00 - 12:00)"}</option>
                <option value="afternoon">☀️ {language === "ta" ? "மதியம் (12:00 - 16:00)" : "Afternoon (12:00 - 16:00)"}</option>
                <option value="evening">🌆 {language === "ta" ? "மாலை (16:00 - 20:00)" : "Evening (16:00 - 20:00)"}</option>
                <option value="all_day">🌐 {language === "ta" ? "முழு பகல் (06:00 - 20:00)" : "All Day (06:00 - 20:00)"}</option>
              </select>
            </div>
          </div>

          {/* Optional Personalized Birth Star Accordion */}
          <div className="pt-3 border-t border-[#F1F5F9]">
            <button
              type="button"
              onClick={() => setShowBirthDetails(!showBirthDetails)}
              className="inline-flex items-center gap-2 text-xs font-bold text-[#3478F6] hover:text-[#16365C] cursor-pointer"
            >
              <Users className="w-4 h-4" />
              <span>
                {showBirthDetails
                  ? (language === "ta" ? "பிறப்பு விவரங்களை மறை" : "Hide Personalized Birth Data")
                  : (language === "ta" ? "+ தாரா பலன் & சந்திர பலன் சரிபார்க்க பிறப்பு நட்சத்திரம் சேர்க்க" : "+ Add Birth Stars for Personalized Tara Bala & Chandra Bala")}
              </span>
            </button>

            {showBirthDetails && (
              <div className="mt-4 p-4 rounded-2xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-4">
                {selectedOccasionCode === "marriage" ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
                    <div>
                      <label className="block text-[11px] font-bold text-[#52667E] mb-1">
                        {language === "ta" ? "மணமகன் நட்சத்திரம்" : "Groom Nakshatra"}
                      </label>
                      <select
                        value={groomNak}
                        onChange={(e) => setGroomNak(parseInt(e.target.value) || 0)}
                        className="w-full px-2.5 py-1.5 rounded-xl border border-[#DDE5F0] bg-white font-medium text-[#102A4C]"
                      >
                        <option value={0}>-- Select Nakshatra --</option>
                        {NAKSHATRA_OPTIONS.map((name, i) => (
                          <option key={i + 1} value={i + 1}>
                            #{i + 1} {name}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-bold text-[#52667E] mb-1">
                        {language === "ta" ? "மணமகன் ராசி" : "Groom Rashi"}
                      </label>
                      <select
                        value={groomRashi}
                        onChange={(e) => setGroomRashi(parseInt(e.target.value) || 0)}
                        className="w-full px-2.5 py-1.5 rounded-xl border border-[#DDE5F0] bg-white font-medium text-[#102A4C]"
                      >
                        <option value={0}>-- Select Rashi --</option>
                        {RASHI_OPTIONS.map((name, i) => (
                          <option key={i + 1} value={i + 1}>
                            {name}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-bold text-[#52667E] mb-1">
                        {language === "ta" ? "மணமகள் நட்சத்திரம்" : "Bride Nakshatra"}
                      </label>
                      <select
                        value={brideNak}
                        onChange={(e) => setBrideNak(parseInt(e.target.value) || 0)}
                        className="w-full px-2.5 py-1.5 rounded-xl border border-[#DDE5F0] bg-white font-medium text-[#102A4C]"
                      >
                        <option value={0}>-- Select Nakshatra --</option>
                        {NAKSHATRA_OPTIONS.map((name, i) => (
                          <option key={i + 1} value={i + 1}>
                            #{i + 1} {name}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-bold text-[#52667E] mb-1">
                        {language === "ta" ? "மணமகள் ராசி" : "Bride Rashi"}
                      </label>
                      <select
                        value={brideRashi}
                        onChange={(e) => setBrideRashi(parseInt(e.target.value) || 0)}
                        className="w-full px-2.5 py-1.5 rounded-xl border border-[#DDE5F0] bg-white font-medium text-[#102A4C]"
                      >
                        <option value={0}>-- Select Rashi --</option>
                        {RASHI_OPTIONS.map((name, i) => (
                          <option key={i + 1} value={i + 1}>
                            {name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                    <div>
                      <label className="block text-[11px] font-bold text-[#52667E] mb-1">
                        {language === "ta" ? "பிறந்த நட்சத்திரம் (Janma Nakshatra)" : "Native Nakshatra"}
                      </label>
                      <select
                        value={nativeNak}
                        onChange={(e) => setNativeNak(parseInt(e.target.value) || 0)}
                        className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] bg-white font-medium text-[#102A4C]"
                      >
                        <option value={0}>-- Select Nakshatra --</option>
                        {NAKSHATRA_OPTIONS.map((name, i) => (
                          <option key={i + 1} value={i + 1}>
                            #{i + 1} {name}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-bold text-[#52667E] mb-1">
                        {language === "ta" ? "பிறந்த ராசி (Janma Rashi)" : "Native Rashi"}
                      </label>
                      <select
                        value={nativeRashi}
                        onChange={(e) => setNativeRashi(parseInt(e.target.value) || 0)}
                        className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] bg-white font-medium text-[#102A4C]"
                      >
                        <option value={0}>-- Select Rashi --</option>
                        {RASHI_OPTIONS.map((name, i) => (
                          <option key={i + 1} value={i + 1}>
                            {name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Error notification */}
        {error && (
          <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-3">
            <AlertCircle className="w-5 h-5 shrink-0 text-rose-600" />
            <div>
              <strong className="font-bold">Search Error: </strong>
              <span>{error}</span>
            </div>
          </div>
        )}

        {/* Loading Spinner */}
        {loading && (
          <div className="p-16 text-center space-y-3">
            <div className="w-10 h-10 border-4 border-[#3478F6] border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-xs font-semibold text-[#52667E]">
              {language === "ta"
                ? "தேர்ந்தெடுக்கப்பட்ட நாட்களுக்கான லக்ன சுத்தி மற்றும் கிரக ஆதிக்கங்கள் கணக்கிடப்படுகின்றன..."
                : "Scanning dates, calculating rising Lagnas, and evaluating Shuddhi rules..."}
            </p>
          </div>
        )}

        {!loading && results && (
          <div className="space-y-6">
            {/* KPI Summary Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="p-5 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-1">
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#52667E]">
                  {language === "ta" ? "ஆய்வு செய்யப்பட்டவை" : "Total Slots Scanned"}
                </span>
                <div className="text-2xl font-serif font-bold text-[#102A4C]">
                  {results.total_candidates}
                </div>
                <div className="text-[11px] text-[#52667E]">{results.search_params.preferred_time_range} hours</div>
              </div>

              <div className="p-5 rounded-2xl bg-emerald-50/70 border border-emerald-200 space-y-1">
                <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-800">
                  {language === "ta" ? "பரிபூரண சுப முகூர்த்தங்கள்" : "Pristine Windows"}
                </span>
                <div className="text-2xl font-serif font-bold text-emerald-950">
                  {results.candidates.filter((c) => c.status === "meets_configured_rules").length}
                </div>
                <div className="text-[11px] text-emerald-700">100% Meets all criteria</div>
              </div>

              <div className="p-5 rounded-2xl bg-amber-50/70 border border-amber-200 space-y-1">
                <span className="text-[10px] font-bold uppercase tracking-wider text-amber-800">
                  {language === "ta" ? "சிறந்த பொருத்தம்" : "Top Ranked Score"}
                </span>
                <div className="text-2xl font-serif font-bold text-amber-950">
                  {results.candidates[0]?.score || 0}/100
                </div>
                <div className="text-[11px] text-amber-700">Highest alignment</div>
              </div>

              <div className="p-5 rounded-2xl bg-blue-50/70 border border-blue-200 space-y-1">
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#3478F6]">
                  {language === "ta" ? "கால அளவு" : "Date Window"}
                </span>
                <div className="text-base font-serif font-bold text-[#102A4C] truncate">
                  {results.search_params.start_date.slice(5)} to {results.search_params.end_date.slice(5)}
                </div>
                <div className="text-[11px] text-[#52667E]">{selectedCity.name_en}</div>
              </div>
            </div>

            {/* Studio Navigation Tabs */}
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-[#DDE5F0] pb-3">
              <div className="flex items-center gap-2">
                {[
                  { id: "candidates", en: `Ranked Windows (${filteredCandidates.length})`, ta: `தகுதி வரிசை முகூர்த்தங்கள் (${filteredCandidates.length})`, icon: Clock },
                  { id: "calendar", en: "Calendar Matrix", ta: "நாட்காட்டி வரைபடம்", icon: Calendar },
                  { id: "rules", en: "Occasion Rules Applied", ta: "சாஸ்திர விதிகள்", icon: ShieldCheck },
                  { id: "saved", en: `Shortlisted (${savedSlots.length})`, ta: `சேமிக்கப்பட்டவை (${savedSlots.length})`, icon: Bookmark },
                ].map((t) => {
                  const Icon = t.icon;
                  const isActive = activeTab === t.id;
                  return (
                    <button
                      key={t.id}
                      type="button"
                      onClick={() => setActiveTab(t.id as any)}
                      className={`inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all cursor-pointer ${
                        isActive
                          ? "bg-[#102A4C] text-white shadow-xs"
                          : "bg-white text-[#52667E] hover:bg-[#F1F5F9] border border-[#DDE5F0]"
                      }`}
                    >
                      <Icon className={`w-4 h-4 ${isActive ? "text-amber-300" : "text-[#52667E]"}`} />
                      <span>{language === "ta" ? t.ta : t.en}</span>
                    </button>
                  );
                })}
              </div>

              {/* Status Filter for Candidates Tab */}
              {activeTab === "candidates" && (
                <div className="flex items-center gap-1.5 text-xs">
                  <span className="font-bold text-[#52667E]">{language === "ta" ? "வடிகட்டி:" : "Filter:"}</span>
                  <button
                    type="button"
                    onClick={() => setStatusFilter("all")}
                    className={`px-2.5 py-1 rounded-lg font-medium transition-all cursor-pointer ${
                      statusFilter === "all" ? "bg-[#102A4C] text-white" : "bg-white border text-[#52667E]"
                    }`}
                  >
                    All ({results.candidates.length})
                  </button>
                  <button
                    type="button"
                    onClick={() => setStatusFilter("pristine")}
                    className={`px-2.5 py-1 rounded-lg font-medium transition-all cursor-pointer ${
                      statusFilter === "pristine" ? "bg-emerald-600 text-white" : "bg-white border text-emerald-700"
                    }`}
                  >
                    Pristine Only
                  </button>
                  <button
                    type="button"
                    onClick={() => setStatusFilter("advisories")}
                    className={`px-2.5 py-1 rounded-lg font-medium transition-all cursor-pointer ${
                      statusFilter === "advisories" ? "bg-amber-600 text-white" : "bg-white border text-amber-700"
                    }`}
                  >
                    With Advisories
                  </button>
                </div>
              )}
            </div>

            {/* TAB 1: CANDIDATE SLOTS LIST */}
            {activeTab === "candidates" && (
              <div className="space-y-4">
                {filteredCandidates.length === 0 ? (
                  <div className="p-12 text-center bg-white rounded-3xl border border-[#DDE5F0] space-y-3">
                    <AlertCircle className="w-8 h-8 text-amber-500 mx-auto" />
                    <h3 className="font-serif font-bold text-base text-[#102A4C]">
                      {language === "ta" ? "பொருத்தமான முகூர்த்தங்கள் கிடைக்கவில்லை" : "No candidates found for this filter"}
                    </h3>
                    <p className="text-xs text-[#52667E]">
                      Try widening the search date range or switching time preference to All Day.
                    </p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 gap-4">
                    {filteredCandidates.map((slot) => {
                      const isPristine = slot.status === "meets_configured_rules";
                      const isSaved = savedSlots.some((s) => s.id === slot.id);

                      return (
                        <div
                          key={slot.id}
                          className={`p-6 rounded-3xl bg-white border transition-all hover:shadow-md space-y-4 ${
                            isPristine
                              ? "border-emerald-300 ring-1 ring-emerald-200"
                              : "border-[#DDE5F0]"
                          }`}
                        >
                          {/* Card Header */}
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#F1F5F9]">
                            <div className="flex items-center gap-3">
                              {/* Score Badge */}
                              <div
                                className={`w-14 h-14 rounded-2xl flex flex-col items-center justify-center font-bold text-white shadow-xs ${
                                  slot.score >= 90
                                    ? "bg-linear-to-br from-emerald-500 to-teal-600"
                                    : slot.score >= 75
                                    ? "bg-linear-to-br from-amber-500 to-amber-600"
                                    : "bg-linear-to-br from-rose-500 to-rose-600"
                                }`}
                              >
                                <span className="text-lg font-serif leading-none">{slot.score}</span>
                                <span className="text-[9px] uppercase tracking-wider opacity-80">Score</span>
                              </div>

                              <div>
                                <div className="flex items-center gap-2">
                                  <span className="font-serif text-lg font-bold text-[#102A4C]">
                                    {slot.event_date}
                                  </span>
                                  <span className="text-xs font-semibold text-[#52667E]">
                                    ({slot.weekday} / {slot.weekday_ta})
                                  </span>
                                </div>
                                <div className="text-xs font-mono font-bold text-[#3478F6] flex items-center gap-1.5">
                                  <Clock className="w-3.5 h-3.5" />
                                  <span>{slot.start_time_local} — {slot.end_time_local}</span>
                                  <span className="text-[#52667E] font-normal">({slot.duration_minutes} mins)</span>
                                </div>
                              </div>
                            </div>

                            <div className="flex items-center gap-2">
                              <span
                                className={`px-3 py-1 rounded-full text-xs font-bold ${
                                  isPristine
                                    ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                                    : "bg-amber-50 text-amber-800 border border-amber-200"
                                }`}
                              >
                                {isPristine
                                  ? (language === "ta" ? "உத்தம சுப முகூர்த்தம்" : "Pristine Window")
                                  : (language === "ta" ? "மத்திம முகூர்த்தம் (ஆலோசனையுடன்)" : "With Advisories")}
                              </span>

                              <button
                                type="button"
                                onClick={() => toggleSaveSlot(slot)}
                                className={`p-2 rounded-xl border transition-all cursor-pointer ${
                                  isSaved
                                    ? "bg-amber-50 border-amber-300 text-amber-800"
                                    : "bg-white border-[#DDE5F0] text-[#52667E] hover:bg-[#F8FAFC]"
                                }`}
                                title="Shortlist this Muhurta"
                              >
                                <Bookmark className={`w-4 h-4 ${isSaved ? "fill-amber-500 text-amber-500" : ""}`} />
                              </button>
                            </div>
                          </div>

                          {/* Astrological Dimensions Grid */}
                          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 text-xs">
                            {/* Lagna */}
                            <div className="p-3 rounded-xl bg-[#FAF8F5] border border-[#E2E8F0]">
                              <span className="text-[10px] font-bold text-[#8C6D23] uppercase tracking-wider block">
                                {language === "ta" ? "லக்னம்" : "Ascendant"}
                              </span>
                              <strong className="text-sm font-serif text-[#102A4C] block mt-0.5">
                                {slot.ascendant.sign_name}
                              </strong>
                              <span className="text-[10px] text-[#52667E] font-tamil">
                                {slot.ascendant.sign_name_ta} ({slot.ascendant.degree_in_sign}°)
                              </span>
                            </div>

                            {/* Planetary Hora */}
                            <div className="p-3 rounded-xl bg-blue-50/50 border border-blue-200">
                              <span className="text-[10px] font-bold text-[#3478F6] uppercase tracking-wider block">
                                {language === "ta" ? "ஹோரை" : "Planetary Hora"}
                              </span>
                              <strong className="text-sm font-serif text-[#102A4C] block mt-0.5">
                                {slot.hora ? `${slot.hora.symbol} ${slot.hora.lord}` : "Benefic"}
                              </strong>
                              <span className="text-[10px] text-[#52667E] font-tamil">
                                {slot.hora?.lord_ta || "சுப ஹோரை"}
                              </span>
                            </div>

                            {/* Tithi */}
                            <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                              <span className="text-[10px] font-bold text-[#52667E] uppercase tracking-wider block">
                                {language === "ta" ? "திதி" : "Tithi"}
                              </span>
                              <strong className="text-xs font-bold text-[#102A4C] block mt-0.5 truncate">
                                {slot.tithi.name}
                              </strong>
                              <span className="text-[10px] text-[#52667E]">
                                {slot.tithi.paksha} Paksha
                              </span>
                            </div>

                            {/* Nakshatra */}
                            <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                              <span className="text-[10px] font-bold text-[#52667E] uppercase tracking-wider block">
                                {language === "ta" ? "நட்சத்திரம்" : "Nakshatra"}
                              </span>
                              <strong className="text-xs font-bold text-[#102A4C] block mt-0.5 truncate">
                                {slot.nakshatra.name}
                              </strong>
                              <span className="text-[10px] text-[#52667E]">
                                Pada {slot.nakshatra.pada} • {slot.nakshatra.lord}
                              </span>
                            </div>

                            {/* Yoga */}
                            <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                              <span className="text-[10px] font-bold text-[#52667E] uppercase tracking-wider block">
                                {language === "ta" ? "யோகம்" : "Yoga"}
                              </span>
                              <strong className="text-xs font-bold text-[#102A4C] block mt-0.5 truncate">
                                {slot.yoga.name}
                              </strong>
                              <span className="text-[10px] text-[#52667E]">#{slot.yoga.number}</span>
                            </div>

                            {/* Karana */}
                            <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                              <span className="text-[10px] font-bold text-[#52667E] uppercase tracking-wider block">
                                {language === "ta" ? "கரணம்" : "Karana"}
                              </span>
                              <strong className="text-xs font-bold text-[#102A4C] block mt-0.5 truncate">
                                {slot.karana.name}
                              </strong>
                              <span className="text-[10px] text-[#52667E]">Half-Tithi</span>
                            </div>
                          </div>

                          {/* Rule Checks & Diagnostics */}
                          <div className="space-y-2 pt-1 text-xs">
                            <div className="flex flex-wrap items-center gap-2">
                              {slot.passed_rules.map((pr, idx) => (
                                <span
                                  key={idx}
                                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 text-[11px]"
                                >
                                  <Check className="w-3 h-3 text-emerald-600 shrink-0" />
                                  <span>{pr.rule}: {pr.message}</span>
                                </span>
                              ))}

                              {slot.advisories.map((adv, idx) => (
                                <span
                                  key={idx}
                                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-amber-50 text-amber-800 border border-amber-200 text-[11px]"
                                >
                                  <AlertCircle className="w-3 h-3 text-amber-600 shrink-0" />
                                  <span>{adv.rule}: {adv.message}</span>
                                </span>
                              ))}

                              {slot.failed_rules.map((fr, idx) => (
                                <span
                                  key={idx}
                                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-rose-50 text-rose-800 border border-rose-200 text-[11px]"
                                >
                                  <XCircle className="w-3 h-3 text-rose-600 shrink-0" />
                                  <span>{fr.rule}: {fr.message}</span>
                                </span>
                              ))}
                            </div>
                          </div>

                          {/* Card Footer Button */}
                          <div className="flex items-center justify-between pt-2 text-xs">
                            <span className="text-[#52667E]">
                              {slot.explanation}
                            </span>
                            <button
                              type="button"
                              onClick={() => setSelectedCandidateModal(slot)}
                              className="inline-flex items-center gap-1 font-bold text-[#3478F6] hover:underline cursor-pointer"
                            >
                              <span>{language === "ta" ? "முழு கிரக நிலை காண்க" : "View Planetary Chart & Houses"}</span>
                              <ArrowRight className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {/* TAB 2: CALENDAR MATRIX */}
            {activeTab === "calendar" && (
              <div className="p-6 rounded-3xl bg-white border border-[#DDE5F0] space-y-4">
                <h3 className="font-serif text-lg font-bold text-[#102A4C]">
                  {language === "ta" ? "நாட்காட்டி வரைபடம் & தினசரி மதிப்பீடு" : "Calendar Matrix of Search Range"}
                </h3>

                <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
                  {Object.entries(results.calendar_summary).map(([dateKey, summary]) => {
                    const isAuspicious = summary.badge === "auspicious";
                    const isModerate = summary.badge === "moderate";

                    return (
                      <div
                        key={dateKey}
                        className={`p-3.5 rounded-2xl border text-xs space-y-1.5 transition-all ${
                          isAuspicious
                            ? "bg-emerald-50/60 border-emerald-300"
                            : isModerate
                            ? "bg-amber-50/60 border-amber-300"
                            : "bg-[#F8FAFC] border-[#E2E8F0]"
                        }`}
                      >
                        <div className="flex items-center justify-between font-bold">
                          <span className="text-[#102A4C]">{dateKey.slice(5)}</span>
                          <span
                            className={`w-2 h-2 rounded-full ${
                              isAuspicious
                                ? "bg-emerald-500"
                                : isModerate
                                ? "bg-amber-500"
                                : "bg-slate-300"
                            }`}
                          />
                        </div>
                        <div className="text-[11px] font-semibold text-[#52667E]">{summary.weekday}</div>
                        <div className="text-[10px] text-[#52667E] truncate">{summary.nakshatra}</div>
                        <div className="pt-1 border-t border-black/5 flex items-center justify-between text-[10px]">
                          <span>{summary.total_slots} slots</span>
                          <strong className="text-[#102A4C]">{summary.best_score}%</strong>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* TAB 3: OCCASION RULES APPLIED */}
            {activeTab === "rules" && (
              <div className="p-6 sm:p-8 rounded-3xl bg-white border border-[#DDE5F0] space-y-6">
                <div>
                  <h3 className="font-serif text-xl font-bold text-[#102A4C]">
                    {language === "ta" ? "சாஸ்திர முகூர்த்த விதிமுறைகள்" : "Astrological Rules Applied for this Occasion"}
                  </h3>
                  <p className="text-xs text-[#52667E] mt-0.5">
                    {language === "ta"
                      ? "நிகழ்வின் தன்மையைப் பொறுத்து மரபு சார்ந்த ஜோதிட சாஸ்திர விதிகள் கண்டிப்பாகப் பரிசீலிக்கப்படுகின்றன."
                      : "Classical Vedic rules enforced to ensure success, prosperity, and longevity for the selected ceremony."}
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  <div className="p-4 rounded-2xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-2">
                    <h4 className="font-bold text-[#102A4C] flex items-center gap-1.5 uppercase tracking-wider text-[11px]">
                      <ShieldCheck className="w-4 h-4 text-emerald-600" />
                      <span>{language === "ta" ? "கட்டாய நிபந்தனைகள்" : "Mandatory Disqualifying Rules"}</span>
                    </h4>
                    <ul className="space-y-1.5 pl-2 text-[#52667E]">
                      <li>• <strong>Rahu Kalam & Yamagandam Avoidance</strong>: Prohibits starting sacred deeds during local Rahu and Yama octants.</li>
                      <li>• <strong>Ashtama Shuddhi</strong>: 8th house from rising Lagna must be strictly vacant (no planets). Prevents accidental obstacles.</li>
                      <li>• <strong>Varjyam (Tyajyam) Avoidance</strong>: Strictly excludes the 4-ghatika toxic interval of the active Nakshatra.</li>
                      <li>• <strong>Dur Muhurta Avoidance</strong>: Daytime prohibited intervals ruled by malefic deities.</li>
                    </ul>
                  </div>

                  <div className="p-4 rounded-2xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-2">
                    <h4 className="font-bold text-[#102A4C] flex items-center gap-1.5 uppercase tracking-wider text-[11px]">
                      <Sparkles className="w-4 h-4 text-amber-600" />
                      <span>{language === "ta" ? "விசேஷ சுப யோகங்கள்" : "Auspicious Enhancements & Bonuses"}</span>
                    </h4>
                    <ul className="space-y-1.5 pl-2 text-[#52667E]">
                      <li>• <strong>Abhijit Muhurta</strong>: 8th midday Muhurta that neutralizes doshas (+10 bonus points).</li>
                      <li>• <strong>Amrita Kalam</strong>: Nectar window derived from Nakshatra ghatikas (+10 bonus points).</li>
                      <li>• <strong>Planetary Hora Alignment</strong>: Matching ruler (Venus for vehicles, Mercury for trade, Jupiter for marriage) awards +10 to +15 bonus.</li>
                      <li>• <strong>Navatara (Tara Bala) & Chandra Bala</strong>: Ensures harmony with native&apos;s birth star and avoids Ashtama Chandra.</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 4: SHORTLISTED MUHURTAS */}
            {activeTab === "saved" && (
              <div className="p-6 rounded-3xl bg-white border border-[#DDE5F0] space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-[#F1F5F9]">
                  <h3 className="font-serif text-lg font-bold text-[#102A4C]">
                    {language === "ta" ? "சேமிக்கப்பட்ட சுப முகூர்த்தங்கள்" : "Shortlisted Candidate Windows"}
                  </h3>
                  {savedSlots.length > 0 && (
                    <button
                      type="button"
                      onClick={() => setSavedSlots([])}
                      className="text-xs text-rose-600 hover:underline font-bold"
                    >
                      Clear All
                    </button>
                  )}
                </div>

                {savedSlots.length === 0 ? (
                  <div className="p-10 text-center text-xs text-[#52667E]">
                    No Muhurtas shortlisted yet. Click the bookmark icon on any candidate card to save it here.
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {savedSlots.map((slot) => (
                      <div
                        key={slot.id}
                        className="p-5 rounded-2xl border border-amber-300 bg-amber-50/30 space-y-2 text-xs"
                      >
                        <div className="flex items-center justify-between">
                          <strong className="text-sm font-serif text-[#102A4C]">{slot.event_date}</strong>
                          <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold text-[10px]">
                            {slot.score}/100
                          </span>
                        </div>
                        <div className="font-mono text-[#3478F6] font-bold">
                          {slot.start_time_local} — {slot.end_time_local} ({slot.weekday})
                        </div>
                        <div className="text-[#52667E]">
                          Lagna: <strong>{slot.ascendant.sign_name}</strong> • Nak: <strong>{slot.nakshatra.name}</strong>
                        </div>
                        <div className="pt-2 flex justify-end">
                          <button
                            type="button"
                            onClick={() => toggleSaveSlot(slot)}
                            className="text-[11px] text-rose-600 font-bold hover:underline"
                          >
                            Remove
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* PLANETARY CHART & HOUSE DETAILS MODAL */}
      {selectedCandidateModal && (
        <div
          className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4"
          onClick={() => setSelectedCandidateModal(null)}
        >
          <div
            className="w-full max-w-2xl bg-white rounded-3xl p-6 sm:p-8 space-y-6 shadow-2xl border border-[#DDE5F0] max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between pb-4 border-b border-[#F1F5F9]">
              <div>
                <span className="text-[10px] uppercase font-bold text-[#52667E] tracking-wider">
                  Muhurta Interval Astrological Chart
                </span>
                <h3 className="text-xl font-serif font-bold text-[#102A4C]">
                  {selectedCandidateModal.event_date} ({selectedCandidateModal.start_time_local} — {selectedCandidateModal.end_time_local})
                </h3>
              </div>

              <button
                type="button"
                onClick={() => setSelectedCandidateModal(null)}
                className="w-8 h-8 rounded-xl bg-[#F1F5F9] hover:bg-[#E2E8F0] text-[#52667E] flex items-center justify-center font-bold cursor-pointer"
              >
                ✕
              </button>
            </div>

            {/* Ascendant & Hora Summary */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-[#FAF8F5] border border-[#E2E8F0]">
                <span className="text-[10px] text-[#8C6D23] font-bold uppercase">Ascendant (Lagna)</span>
                <div className="text-sm font-bold text-[#102A4C]">{selectedCandidateModal.ascendant.sign_name}</div>
                <div className="text-[10px] text-[#52667E]">{selectedCandidateModal.ascendant.degree_in_sign}°</div>
              </div>

              <div className="p-3 rounded-xl bg-blue-50/50 border border-blue-200">
                <span className="text-[10px] text-[#3478F6] font-bold uppercase">Planetary Hora</span>
                <div className="text-sm font-bold text-[#102A4C]">
                  {selectedCandidateModal.hora ? `${selectedCandidateModal.hora.symbol} ${selectedCandidateModal.hora.lord}` : "Benefic"}
                </div>
                <div className="text-[10px] text-[#52667E]">{selectedCandidateModal.hora?.lord_ta || "சுப ஹோரை"}</div>
              </div>

              <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                <span className="text-[10px] text-[#52667E] font-bold uppercase">Tithi</span>
                <div className="text-sm font-bold text-[#102A4C]">{selectedCandidateModal.tithi.name}</div>
                <div className="text-[10px] text-[#52667E]">{selectedCandidateModal.tithi.paksha}</div>
              </div>

              <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                <span className="text-[10px] text-[#52667E] font-bold uppercase">Nakshatra</span>
                <div className="text-sm font-bold text-[#102A4C]">{selectedCandidateModal.nakshatra.name}</div>
                <div className="text-[10px] text-[#52667E]">Pada {selectedCandidateModal.nakshatra.pada}</div>
              </div>
            </div>

            {/* 12-House Planetary Placements Table */}
            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-[#102A4C]">
                Planetary Placements from Rising Lagna (Whole-Sign Bhavas)
              </h4>
              <div className="overflow-x-auto rounded-2xl border border-[#DDE5F0]">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#FAF8F5] text-[#102A4C] border-b border-[#DDE5F0]">
                    <tr>
                      <th className="p-3 font-bold">Planet</th>
                      <th className="p-3 font-bold">Sign (Rashi)</th>
                      <th className="p-3 font-bold">Bhava from Lagna</th>
                      <th className="p-3 font-bold">Degree</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#F1F5F9]">
                    {Object.entries(selectedCandidateModal.planets || {}).map(([pName, pData]: [string, any]) => (
                      <tr key={pName} className="hover:bg-[#F8FAFC]">
                        <td className="p-3 font-bold text-[#102A4C]">{pName}</td>
                        <td className="p-3">{pData.sign_name} ({pData.sign_name_ta})</td>
                        <td className="p-3 font-bold text-[#3478F6]">House {pData.bhava}</td>
                        <td className="p-3 font-mono">{pData.degree_in_sign}°</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="pt-2">
              <button
                type="button"
                onClick={() => setSelectedCandidateModal(null)}
                className="w-full py-2.5 rounded-xl bg-[#102A4C] hover:bg-[#16365C] text-white font-bold text-xs cursor-pointer transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function MuhurtaStudioPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-[#F4F6F9]">
          <div className="w-8 h-8 border-4 border-[#3478F6] border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <MuhurtaStudioInner />
    </Suspense>
  );
}
