"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  findKuladeivamFromHoroscope,
  findKuladeivamFromPrasanna,
  getKuladeivamUniversalTemples,
} from "@/lib/api";
import {
  KuladeivamRequest,
  KuladeivamPrasannaRequest,
  KuladeivamResponse,
  UniversalRefugeTemple,
} from "@/lib/types";
import {
  Compass,
  Calendar,
  Clock,
  MapPin,
  Sparkles,
  AlertCircle,
  RefreshCw,
  BookOpen,
  ShieldCheck,
  Flame,
  CheckCircle2,
  TreeDeciduous,
  Navigation,
  HelpCircle,
  Info,
  ChevronRight,
  Sun,
  Award,
} from "lucide-react";

const TN_DISTRICTS = [
  "Madurai (மதுரை)",
  "Thanjavur (தஞ்சாவூர்)",
  "Coimbatore (கோயம்புத்தூர்)",
  "Tirunelveli (திருநெல்வேலி)",
  "Tiruchirappalli (திருச்சிராப்பள்ளி)",
  "Salem (சேலம்)",
  "Dindigul (திண்டுக்கல்)",
  "Erode (ஈரோடு)",
  "Tiruppur (திருப்பூர்)",
  "Sivagangai (சிவகங்கை)",
  "Ramanathapuram (ராமநாதபுரம்)",
  "Theni (தேனி)",
  "Virudhunagar (விருதுநகர்)",
  "Kanchipuram (காஞ்சிபுரம்)",
  "Thiruvannamalai (திருவண்ணாமலை)",
  "Vellore (வேலூர்)",
  "Cuddalore (கடலூர்)",
  "Nagapattinam (நாகப்பட்டினம்)",
  "Pudukkottai (புதுக்கோட்டை)",
  "Kanyakumari (கன்னியாகுமரி)",
  "Chennai / Tiruvallur (சென்னை / திருவள்ளூர்)",
  "Other Ancestral Root (பிற பூர்வீகம்)",
];

export default function KuladeivamFinderPage() {
  const { language } = useLanguage();
  const isTa = language === "ta";

  const [activeMode, setActiveMode] = useState<"horoscope" | "prasanna" | "guide">("horoscope");

  // Horoscope Inputs
  const [birthDate, setBirthDate] = useState("1992-06-18");
  const [birthTime, setBirthTime] = useState("08:45:00");
  const [latitude, setLatitude] = useState(13.0827); // Chennai
  const [longitude, setLongitude] = useState(80.2707);
  const [timezone, setTimezone] = useState("Asia/Kolkata");
  const [gender, setGender] = useState("male");
  const [ancestralDistrict, setAncestralDistrict] = useState("Madurai (மதுரை)");

  // Prasanna Inputs
  const [prasannaDateTime, setPrasannaDateTime] = useState("2026-01-01T12:00:00");
  const [querentSeed, setQuerentSeed] = useState<number | undefined>(undefined);

  useEffect(() => {
    setPrasannaDateTime(new Date().toISOString().slice(0, 19));
  }, []);

  // States
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<KuladeivamResponse | null>(null);

  // Quick preset loader
  const handleLoadSample = (sampleType: "rural" | "agamic") => {
    if (sampleType === "rural") {
      setBirthDate("1988-11-20");
      setBirthTime("18:15:00");
      setLatitude(9.9252); // Madurai
      setLongitude(78.1198);
      setAncestralDistrict("Madurai (மதுரை)");
      setGender("male");
    } else {
      setBirthDate("1995-04-14");
      setBirthTime("06:30:00");
      setLatitude(10.787); // Thanjavur
      setLongitude(79.1378);
      setAncestralDistrict("Thanjavur (தஞ்சாவூர்)");
      setGender("male");
    }
  };

  const handleCalculateHoroscope = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setIsLoading(true);
    setError(null);

    const req: KuladeivamRequest = {
      birth_date: birthDate,
      birth_time: birthTime,
      timezone: timezone || "Asia/Kolkata",
      latitude: Number(latitude),
      longitude: Number(longitude),
      gender: gender,
      ancestral_district: ancestralDistrict,
      ayanamsa: 0,
      house_system: 0,
    };

    try {
      const resp = await findKuladeivamFromHoroscope(req);
      setResult(resp);
    } catch (err: any) {
      setError(err?.message || "Failed to analyze Kuladeivam chart.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCalculatePrasanna = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setIsLoading(true);
    setError(null);

    const req: KuladeivamPrasannaRequest = {
      query_datetime: prasannaDateTime,
      latitude: Number(latitude),
      longitude: Number(longitude),
      timezone: timezone || "Asia/Kolkata",
      querent_seed: querentSeed ? Number(querentSeed) : undefined,
      ancestral_district: ancestralDistrict,
    };

    try {
      const resp = await findKuladeivamFromPrasanna(req);
      setResult(resp);
    } catch (err: any) {
      setError(err?.message || "Failed to calculate Prasanna guidance.");
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
            { label: isTa ? "குலதெய்வம் கண்டறிதல்" : "Kuladeivam Finder", href: "/tools/kuladeivam-finder" },
          ]}
        />

        {/* Page Header */}
        <div className="bg-gradient-to-r from-amber-900 via-amber-800 to-amber-950 text-white rounded-3xl p-6 sm:p-8 shadow-xl relative overflow-hidden border border-amber-700/40">
          <div className="absolute right-0 top-0 bottom-0 w-96 bg-[radial-gradient(circle_at_center,rgba(251,191,36,0.15),transparent_70%)] pointer-events-none" />
          
          <div className="relative z-10 flex flex-wrap items-center justify-between gap-6">
            <div className="space-y-3 max-w-2xl">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 text-amber-200 text-xs font-bold border border-amber-400/30 backdrop-blur-sm">
                <Flame className="w-3.5 h-3.5 text-amber-300" />
                <span>{isTa ? "பாரம்பரிய தமிழ் ஜோதிட ஆய்வு அரங்கம்" : "Classical Tamil Jyotish Sastra"}</span>
              </div>
              <h1 className="text-2xl sm:text-4xl font-black tracking-tight text-white flex items-center gap-3">
                {isTa ? "குலதெய்வம் கண்டறியும் ஆய்வு அரங்கம்" : "Kuladeivam (Family Deity) Finder"}
              </h1>
              <p className="text-sm text-amber-100/90 leading-relaxed">
                {isTa
                  ? "பூர்வ புண்ணிய ஸ்தானம் (5-ஆம் பாவம்), பாக்கிய/பித்ரு ஸ்தானம் (9-ஆம் பாவம்), நவாம்சம் (D9) மற்றும் ஜாமக்கோள் பிரசன்ன ஆருட முறைப்படி உங்கள் வம்சக் குலதெய்வம், கிராமிய/ஆகம வடிவம், திசை மற்றும் கோவில் அமைப்பைக் கண்டறியும் சாஸ்திர இயந்திரம்."
                  : "Discover your ancestral family deity, deity gender, worship category (Grama Devata vs Agamic Temple), cardinal direction, and sacred landscape markers through classical 5th/9th Bhavas, D9 Navamsha, and Horary Prasna."}
              </p>
            </div>

            {/* Quick Action Sample */}
            <div className="bg-amber-950/60 border border-amber-600/40 rounded-2xl p-4 backdrop-blur-md space-y-2 text-xs">
              <span className="font-semibold text-amber-200 block">
                {isTa ? "மாதிரி ஆய்வு ஜாதகங்கள்:" : "Load Sample Case Study:"}
              </span>
              <div className="flex flex-col gap-2">
                <button
                  type="button"
                  onClick={() => handleLoadSample("rural")}
                  className="px-3 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-100 font-medium text-left border border-amber-400/30 transition-colors"
                >
                  🌾 {isTa ? "கிராமக் காவல் தெய்வம் (மதுரை மரபு)" : "Grama Devata (Madurai Lineage)"}
                </button>
                <button
                  type="button"
                  onClick={() => handleLoadSample("agamic")}
                  className="px-3 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-100 font-medium text-left border border-amber-400/30 transition-colors"
                >
                  🛕 {isTa ? "ஆகமப் பெருங்கோவில் (தஞ்சை மரபு)" : "Agamic Temple (Thanjavur Lineage)"}
                </button>
              </div>
            </div>
          </div>

          {/* Mode Switcher Tabs */}
          <div className="mt-8 pt-4 border-t border-amber-700/50 flex flex-wrap gap-2">
            <button
              onClick={() => setActiveMode("horoscope")}
              className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-bold flex items-center gap-2 transition-all cursor-pointer ${
                activeMode === "horoscope"
                  ? "bg-white text-amber-950 shadow-md scale-102"
                  : "bg-amber-900/60 text-amber-200 hover:bg-amber-800/80 border border-amber-600/40"
              }`}
            >
              <Compass className="w-4 h-4" />
              <span>{isTa ? "1. ஜாதக வழி ஆய்வு (பிறப்பு விபரம்)" : "1. Birth Chart Analysis"}</span>
            </button>

            <button
              onClick={() => setActiveMode("prasanna")}
              className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-bold flex items-center gap-2 transition-all cursor-pointer ${
                activeMode === "prasanna"
                  ? "bg-white text-amber-950 shadow-md scale-102"
                  : "bg-amber-900/60 text-amber-200 hover:bg-amber-800/80 border border-amber-600/40"
              }`}
            >
              <Clock className="w-4 h-4" />
              <span>{isTa ? "2. பிரசன்ன வழி ஆய்வு (நேரம் அறியாதோர்)" : "2. Horary Prasanna Method"}</span>
            </button>

            <button
              onClick={() => setActiveMode("guide")}
              className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-bold flex items-center gap-2 transition-all cursor-pointer ${
                activeMode === "guide"
                  ? "bg-white text-amber-950 shadow-md scale-102"
                  : "bg-amber-900/60 text-amber-200 hover:bg-amber-800/80 border border-amber-600/40"
              }`}
            >
              <BookOpen className="w-4 h-4" />
              <span>{isTa ? "3. அறியாதோர் பரிகார பூஜை முறை" : "3. Discovery Ritual Protocol"}</span>
            </button>
          </div>
        </div>

        {/* Mode A: Horoscope Form */}
        {activeMode === "horoscope" && (
          <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4">
              <div>
                <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-amber-600" />
                  {isTa ? "பிறப்பு ஜாதக விபரங்கள்" : "Enter Birth Coordinates"}
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {isTa
                    ? "பிறந்த தேதி, நேரம் மற்றும் பூர்வீக மாவட்டத்தைக் கொண்டு 5 & 9-ஆம் பாவகங்கள் கணிக்கப்படும்."
                    : "Accurate computation of 5th/9th Bhava lords, planetary occupants, aspects, and D9 Navamsha."}
                </p>
              </div>
            </div>

            <form onSubmit={handleCalculateHoroscope} className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                    {isTa ? "பிறந்த தேதி (Date of Birth)" : "Date of Birth"}
                  </label>
                  <input
                    type="date"
                    value={birthDate}
                    onChange={(e) => setBirthDate(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 focus:outline-none"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                    {isTa ? "பிறந்த நேரம் (Birth Time - 24 Hr)" : "Birth Time (24 Hr)"}
                  </label>
                  <input
                    type="time"
                    step="1"
                    value={birthTime}
                    onChange={(e) => setBirthTime(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 focus:outline-none"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                    {isTa ? "பாலினம் (Gender)" : "Gender"}
                  </label>
                  <select
                    value={gender}
                    onChange={(e) => setGender(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 focus:outline-none"
                  >
                    <option value="male">{isTa ? "ஆண் (Male - தந்தை வழி குலம்)" : "Male (Paternal Lineage)"}</option>
                    <option value="female">{isTa ? "பெண் (Female - தந்தை/புகுந்த வீடு)" : "Female (Paternal/Marital Lineage)"}</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                    {isTa ? "பூர்வீக மாவட்டம் (Ancestral Root)" : "Ancestral District"}
                  </label>
                  <select
                    value={ancestralDistrict}
                    onChange={(e) => setAncestralDistrict(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 focus:outline-none"
                  >
                    {TN_DISTRICTS.map((dist) => (
                      <option key={dist} value={dist}>
                        {dist}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                    {isTa ? "அட்சரேகை (Latitude)" : "Latitude"}
                  </label>
                  <input
                    type="number"
                    step="0.0001"
                    value={latitude}
                    onChange={(e) => setLatitude(Number(e.target.value))}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 focus:outline-none"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                    {isTa ? "தீர்க்கரேகை (Longitude)" : "Longitude"}
                  </label>
                  <input
                    type="number"
                    step="0.0001"
                    value={longitude}
                    onChange={(e) => setLongitude(Number(e.target.value))}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 focus:outline-none"
                    required
                  />
                </div>
              </div>

              <div className="flex justify-end pt-2">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="px-6 py-3 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-bold text-sm flex items-center gap-2 shadow-lg shadow-amber-600/20 transition-all cursor-pointer disabled:opacity-50"
                >
                  {isLoading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>{isTa ? "கணிக்கப்படுகிறது..." : "Computing..."}</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 text-amber-200" />
                      <span>{isTa ? "குலதெய்வம் கண்டறிக (Find Kuladeivam)" : "Find Lineage Deity"}</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Mode B: Prasanna Form */}
        {activeMode === "prasanna" && (
          <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4">
              <div>
                <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <Clock className="w-5 h-5 text-amber-600" />
                  {isTa ? "ஜாமக்கோள் பிரசன்ன ஆருட விபரங்கள்" : "Horary Prasna Consultation Moment"}
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {isTa
                    ? "சரியான பிறந்த நேரம் தெரியாதவர்கள், கேள்வி கேட்கும் தற்போதைய நேரத்தைக் கொண்டு ஆருடம், உதயம், மற்றும் கவிப்பு மூலம் துல்லியமாக அறியலாம்."
                    : "For querents without verified birth times. Evaluates the divine synchronicity of query instant via Jamakkol pillars."}
                </p>
              </div>
            </div>

            <form onSubmit={handleCalculatePrasanna} className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                    {isTa ? "கேள்வி கேட்ட நேரம் (Query Datetime)" : "Query Datetime"}
                  </label>
                  <input
                    type="datetime-local"
                    value={prasannaDateTime}
                    onChange={(e) => setPrasannaDateTime(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 focus:outline-none"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                    {isTa ? "ஆருட விதை எண் (Seed 1-249 - Optional)" : "Horary Seed Number (1-249 Optional)"}
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="249"
                    placeholder={isTa ? "எண் (1-249 விருப்பத்தேர்வு)" : "Optional 1-249 seed"}
                    value={querentSeed || ""}
                    onChange={(e) => setQuerentSeed(e.target.value ? Number(e.target.value) : undefined)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                    {isTa ? "பூர்வீக மாவட்டம் (Ancestral Root)" : "Ancestral District"}
                  </label>
                  <select
                    value={ancestralDistrict}
                    onChange={(e) => setAncestralDistrict(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 focus:outline-none"
                  >
                    {TN_DISTRICTS.map((dist) => (
                      <option key={dist} value={dist}>
                        {dist}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex justify-end pt-2">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="px-6 py-3 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-bold text-sm flex items-center gap-2 shadow-lg shadow-amber-600/20 transition-all cursor-pointer disabled:opacity-50"
                >
                  {isLoading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>{isTa ? "பிரசன்னம் கணிக்கப்படுகிறது..." : "Casting Horary Wheel..."}</span>
                    </>
                  ) : (
                    <>
                      <Compass className="w-4 h-4 text-amber-200" />
                      <span>{isTa ? "பிரசன்ன ஆருடம் பார்க்க (Cast Prasanna)" : "Cast Horary Chart"}</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Error Notification */}
        {error && (
          <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-rose-600 dark:text-rose-400 mt-0.5 shrink-0" />
            <div className="text-sm text-rose-800 dark:text-rose-200">{error}</div>
          </div>
        )}

        {/* Mode C: Discovery Guide & Universal Temples */}
        {activeMode === "guide" && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
              <div className="border-b border-slate-100 dark:border-slate-800 pb-4">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-50 dark:bg-amber-950/40 text-amber-800 dark:text-amber-300 text-xs font-bold border border-amber-200 dark:border-amber-800/60 mb-2">
                  <Flame className="w-3.5 h-3.5 text-amber-600" />
                  <span>{isTa ? "வீட்டிலேயே செய்யும் பரிகாரம்" : "Domestic Propitiation"}</span>
                </div>
                <h2 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white">
                  {isTa ? "குலதெய்வம் அறியாதோர் கண்டறியும் 6 சாஸ்திரப் படிகள்" : "6 Classical Steps to Discover an Unknown Family Deity"}
                </h2>
                <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                  {isTa
                    ? "தலைமுறைகளாக இடம் பெயர்ந்து குலதெய்வம் எதுவென்று தெரியாமல் தவிக்கும் குடும்பங்கள், தங்கள் இல்லத்திலேயே செய்து வழிகாட்டுதலைப் பெறும் சாஸ்திர முறை."
                    : "For families who lost ancestral records. Following this 48-day protocol awakens ancestral memory and reveals clues through elder relatives or intuitive dreams."}
                </p>
              </div>

              <div className="space-y-4">
                {[
                  {
                    step: 1,
                    titleTa: "அமாவாசை / தமிழ் மாதப் பிறப்பு சங்கல்பம்",
                    titleEn: "Amavasya / Solar Transit Resolution",
                    descTa: "அமாவாசை அல்லது தமிழ் முதல் நாளன்று அதிகாலை நீராடி பூசை அறையில் பச்சரிசி பரப்பி காமாட்சி தீபமேற்றி சங்கல்பம் செய்யவும்.",
                    descEn: "Bathe at dawn on Amavasya or the 1st day of a Tamil month, spread raw rice on a clean wooden plank, and light a brass Kamakshi lamp.",
                  },
                  {
                    step: 2,
                    titleTa: "மஞ்சள் துணி நாணயம் முடிப்பு (காணிக்கை சங்கல்பம்)",
                    titleEn: "Yellow Cloth Sanctified Coin Pledge",
                    descTa: "புதிய மஞ்சள் துணியில் ஒரு வெள்ளி நாணயம் அல்லது 5 ரூபாய் நாணயத்தை பச்சரிசியுடன் வைத்து முடிந்து, 'குலதெய்வ காணிக்கை' என்று பூசை அறையில் வைக்கவும்.",
                    descEn: "Wrap a coin with unbroken raw rice in a turmeric-stained yellow cloth as a sealed pledge, dedicated to your Kuladeivam until you find the shrine.",
                  },
                  {
                    step: 3,
                    titleTa: "மாவிளக்கு தீபம் ஏற்றுதல்",
                    titleEn: "Maa-Vilakku Sacred Dough Lamp",
                    descTa: "பச்சரிசி மாவில் வெல்லம், ஏலக்காய், பசு நெய் கலந்து உருண்டையாக்கி நடுவில் குழி செய்து நெய் தீபமேற்றி வணங்கவும்.",
                    descEn: "A sacred dough lamp made of soaked raw rice flour, jaggery, cardamom, and pure ghee. Dissolves generational karmic veils.",
                  },
                  {
                    step: 4,
                    titleTa: "மண்டல தீப வழிபாடு (48 நாட்கள்)",
                    titleEn: "48-Day (One Mandala) Evening Lamp",
                    descTa: "தொடர்ந்து 48 நாட்கள் மாலை 6 மணிக்கு 'எங்கள் குலதெய்வமே உன்னை வெளிப்படுத்து' என மனமுருகி நெய் தீபமேற்றி வரவும்.",
                    descEn: "Maintain an uninterrupted cow's ghee lamp every evening at 6 PM for 48 consecutive days with prayers for revelation.",
                  },
                  {
                    step: 5,
                    titleTa: "பங்காளி / தாயாதி மற்றும் மூத்தோர் விசாரணை",
                    titleEn: "Elder Relatives & Pangali Investigation",
                    descTa: "பூர்வீக ஊர் மற்றும் தந்தை வழி பங்காளி உறவுகளிடம் பழைய நில ஆவணங்கள் அல்லது கிராமத்து கோவில் பெயர்களைக் கேட்டு அறியவும்.",
                    descEn: "Inquire with elder lineage relatives (Pangalis) regarding old patta land records, clan migrations, and native village boundaries.",
                  },
                  {
                    step: 6,
                    titleTa: "பொதுக் குலதல தரிசனம்",
                    titleEn: "Universal Lineage Refuge Pilgrimage",
                    descTa: "திருச்செந்தூர் சுப்பிரமணிய சுவாமி அல்லது சமயபுரம் மாரியம்மன் கோவிலுக்கு குடும்பத்தோடு சென்று பொங்கலிட்டு வழிபடவும்.",
                    descEn: "Visit universal sanctuary temples like Tiruchendur Murugan or Samayapuram Mariamman and offer traditional sweet pongal.",
                  },
                ].map((item) => (
                  <div
                    key={item.step}
                    className="p-4 rounded-2xl bg-amber-50/50 dark:bg-amber-950/20 border border-amber-200/60 dark:border-amber-900/40 flex items-start gap-4"
                  >
                    <div className="w-8 h-8 rounded-full bg-amber-600 text-white font-black flex items-center justify-center shrink-0 text-sm shadow">
                      {item.step}
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-amber-950 dark:text-amber-200">
                        {isTa ? item.titleTa : item.titleEn}
                      </h3>
                      <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 leading-relaxed">
                        {isTa ? item.descTa : item.descEn}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 4 Universal Refuge Shrines */}
            <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
              <div>
                <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <Award className="w-5 h-5 text-amber-600" />
                  {isTa ? "குலதெய்வம் அறியாதோர் சரணடையும் 4 மகா தலங்கள்" : "The 4 Universal Sanctuary Temples"}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {isTa
                    ? "குலதெய்வம் எதுவென்று அறியாதவர்கள் தற்காலிகமாகக் குலதெய்வமாக ஏற்று வழிபடத் தகுந்த தமிழ்நாட்டின் முதன்மைப் புண்ணியத் தலங்கள்."
                    : "Classical refuge shrines where any family without an identified clan deity can surrender to receive complete generational protection."}
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-5 rounded-2xl bg-gradient-to-br from-amber-50 to-orange-50 dark:from-slate-800 dark:to-slate-800/80 border border-amber-200 dark:border-slate-700 space-y-2">
                  <div className="text-xs font-bold text-amber-800 dark:text-amber-400 uppercase tracking-wide">
                    {isTa ? "1. தமிழ் மண்ணின் பொதுக் குலதெய்வம்" : "Universal Tamil Kuladeivam"}
                  </div>
                  <h4 className="text-base font-black text-slate-900 dark:text-white">
                    {isTa ? "அருள்மிகு சுப்பிரமணிய சுவாமி திருக்கோவில்" : "Arulmigu Subramaniaswamy Temple"}
                  </h4>
                  <div className="text-xs text-amber-700 dark:text-amber-300 font-semibold flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5" />
                    <span>{isTa ? "திருச்செந்தூர், தூத்துக்குடி மாவட்டம்" : "Tiruchendur, Thoothukudi District"}</span>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed pt-1">
                    {isTa
                      ? "கடற்கரையில் அமைந்த இந்த சன்னதியில் கடலில் நீராடி விரதமிருந்து வழிபடக் குலசாபம் நீங்கி, மூதாதையர் ஆசி பரிபூரணமாகக் கிட்டும்."
                      : "Lord Murugan at the seashore dissolves ancestral curses. Bathing in the holy sea cleanses generational karma and unblocks family prosperity."}
                  </p>
                </div>

                <div className="p-5 rounded-2xl bg-gradient-to-br from-amber-50 to-orange-50 dark:from-slate-800 dark:to-slate-800/80 border border-amber-200 dark:border-slate-700 space-y-2">
                  <div className="text-xs font-bold text-amber-800 dark:text-amber-400 uppercase tracking-wide">
                    {isTa ? "2. கிராம அம்மன் தெய்வங்களின் தாய்" : "Mother of All Rural Amman Deities"}
                  </div>
                  <h4 className="text-base font-black text-slate-900 dark:text-white">
                    {isTa ? "அருள்மிகு சமயபுரம் மாரியம்மன் திருக்கோவில்" : "Arulmigu Samayapuram Mariamman Temple"}
                  </h4>
                  <div className="text-xs text-amber-700 dark:text-amber-300 font-semibold flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5" />
                    <span>{isTa ? "சமயபுரம், திருச்சிராப்பள்ளி மாவட்டம்" : "Samayapuram, Tiruchirappalli District"}</span>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed pt-1">
                    {isTa
                      ? "குலதெய்வம் பெண் தெய்வம் (அம்மன்) என்று மட்டும் தெரிந்து ஊர் அறியாதவர்கள் இத்தலத்தில் மாவிளக்கு ஏற்றி வழிபடலாம்."
                      : "For all who know their deity is a Goddess/Amman but lack the exact village shrine, Samayapuram serves as the supreme mother sanctuary."}
                  </p>
                </div>

                <div className="p-5 rounded-2xl bg-gradient-to-br from-amber-50 to-orange-50 dark:from-slate-800 dark:to-slate-800/80 border border-amber-200 dark:border-slate-700 space-y-2">
                  <div className="text-xs font-bold text-amber-800 dark:text-amber-400 uppercase tracking-wide">
                    {isTa ? "3. அகில உலக தாய்-தந்தை தலம்" : "Universal Cosmic Parents"}
                  </div>
                  <h4 className="text-base font-black text-slate-900 dark:text-white">
                    {isTa ? "அருள்மிகு மீனாட்சி சுந்தரேஸ்வரர் திருக்கோவில்" : "Arulmigu Meenakshi Sundareswarar Temple"}
                  </h4>
                  <div className="text-xs text-amber-700 dark:text-amber-300 font-semibold flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5" />
                    <span>{isTa ? "மதுரை திருத்தலம்" : "Madurai, Tamil Nadu"}</span>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed pt-1">
                    {isTa
                      ? "அனைத்து ஜீவராசிகளுக்கும் தாய் தந்தையாக விளங்குபவர்கள். வம்ச விருத்தி மற்றும் குழந்தைகளின் திருமண பாக்கியத்திற்கு முதன்மை தலம்."
                      : "Divine mother and father of all living souls. Guarantees lineage continuation, children's health, and timely auspicious weddings."}
                  </p>
                </div>

                <div className="p-5 rounded-2xl bg-gradient-to-br from-amber-50 to-orange-50 dark:from-slate-800 dark:to-slate-800/80 border border-amber-200 dark:border-slate-700 space-y-2">
                  <div className="text-xs font-bold text-amber-800 dark:text-amber-400 uppercase tracking-wide">
                    {isTa ? "4. பித்ரு தோஷ நிவர்த்தி தலம்" : "Ancestral Debt & Pitru Cleansing"}
                  </div>
                  <h4 className="text-base font-black text-slate-900 dark:text-white">
                    {isTa ? "அருள்மிகு ராமநாதசுவாமி திருக்கோவில்" : "Arulmigu Ramanathaswamy Temple"}
                  </h4>
                  <div className="text-xs text-amber-700 dark:text-amber-300 font-semibold flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5" />
                    <span>{isTa ? "ராமேஸ்வரம், ராமநாதபுரம் மாவட்டம்" : "Rameswaram, Ramanathapuram District"}</span>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed pt-1">
                    {isTa
                      ? "22 புண்ணிய தீர்த்தங்களில் நீராடி முன்னோர்களுக்கு திதி கொடுத்து வழிபட, குலதெய்வம் குறித்த கனவுகள் மற்றும் வெளிப்பாடுகள் துரிதமாகும்."
                      : "Bathing in the 22 holy theerthams dispels ancestral displeasure, triggering intuitive dreams and unexpected connections leading to the lost shrine."}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* RESULTS SECTION */}
        {result && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Primary & Secondary Deity Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Primary Deity Card */}
              <div className="bg-gradient-to-br from-amber-900 to-amber-950 text-white rounded-3xl p-6 sm:p-8 border border-amber-600/50 shadow-xl space-y-5 relative overflow-hidden">
                <div className="flex items-center justify-between border-b border-amber-700/60 pb-4">
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 text-xs font-bold border border-amber-400/30">
                    <Award className="w-3.5 h-3.5" />
                    <span>{isTa ? "முதன்மைக் குலதெய்வ அடையாளம்" : "Primary Lineage Deity Profile"}</span>
                  </div>
                  <span className="px-3 py-1 rounded-full bg-amber-400/20 text-amber-200 text-xs font-black">
                    {result.primary_deity.prominence_score}% {isTa ? "துல்லியம்" : "Match"}
                  </span>
                </div>

                <div>
                  <div className="text-xs text-amber-300 font-semibold uppercase tracking-wider">
                    {isTa ? result.primary_deity.deity_category_ta : result.primary_deity.deity_category_en} • {isTa ? result.primary_deity.gender_ta : result.primary_deity.gender_en}
                  </div>
                  <h3 className="text-2xl sm:text-3xl font-black text-white mt-1">
                    {isTa ? result.primary_deity.deity_name_ta : result.primary_deity.deity_name_en}
                  </h3>
                  <div className="text-xs text-amber-200/80 font-medium mt-1">
                    {isTa ? result.primary_deity.governing_house_ta : result.primary_deity.governing_house_en} • {isTa ? "அதிபதி: " : "Lord: "} 
                    <span className="font-bold text-amber-100">
                      {isTa ? result.primary_deity.governing_planet_ta : result.primary_deity.governing_planet_en}
                    </span>
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-amber-950/70 border border-amber-700/50 space-y-2 text-xs">
                  <span className="font-bold text-amber-300 block">
                    {isTa ? "பாரம்பரிய வழிபாட்டு வடிவங்கள் / கோவில்கள்:" : "Classical Shrines & Manifestations:"}
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {(isTa ? result.primary_deity.traditional_forms_ta : result.primary_deity.traditional_forms_en).map((form, i) => (
                      <span key={i} className="px-2.5 py-1 rounded-lg bg-amber-800/60 border border-amber-600/40 text-amber-100 text-xs">
                        {form}
                      </span>
                    ))}
                  </div>
                </div>

                <p className="text-xs sm:text-sm text-amber-100/90 leading-relaxed">
                  {isTa ? result.primary_deity.description_ta : result.primary_deity.description_en}
                </p>
              </div>

              {/* Secondary Deity Card */}
              {result.secondary_deity && (
                <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 shadow-sm space-y-5">
                  <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 dark:bg-indigo-950/40 text-indigo-800 dark:text-indigo-300 text-xs font-bold border border-indigo-200 dark:border-indigo-800/60">
                      <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
                      <span>{isTa ? "பூர்வ புண்ணிய / இஷ்ட குலதெய்வம்" : "Purva Punya / Secondary Protector"}</span>
                    </div>
                    <span className="px-3 py-1 rounded-full bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 text-xs font-black">
                      {result.secondary_deity.prominence_score}% {isTa ? "பொருத்தம்" : "Confidence"}
                    </span>
                  </div>

                  <div>
                    <div className="text-xs text-indigo-700 dark:text-indigo-400 font-semibold uppercase tracking-wider">
                      {isTa ? result.secondary_deity.deity_category_ta : result.secondary_deity.deity_category_en} • {isTa ? result.secondary_deity.gender_ta : result.secondary_deity.gender_en}
                    </div>
                    <h3 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white mt-1">
                      {isTa ? result.secondary_deity.deity_name_ta : result.secondary_deity.deity_name_en}
                    </h3>
                    <div className="text-xs text-slate-500 dark:text-slate-400 font-medium mt-1">
                      {isTa ? result.secondary_deity.governing_house_ta : result.secondary_deity.governing_house_en} • {isTa ? "அதிபதி: " : "Lord: "} 
                      <span className="font-bold text-slate-800 dark:text-slate-200">
                        {isTa ? result.secondary_deity.governing_planet_ta : result.secondary_deity.governing_planet_en}
                      </span>
                    </div>
                  </div>

                  <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 space-y-2 text-xs">
                    <span className="font-bold text-slate-700 dark:text-slate-300 block">
                      {isTa ? "பிரசித்தி பெற்ற திருத்தல வடிவங்கள்:" : "Traditional Manifestations:"}
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {(isTa ? result.secondary_deity.traditional_forms_ta : result.secondary_deity.traditional_forms_en).map((form, i) => (
                        <span key={i} className="px-2.5 py-1 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800 text-indigo-900 dark:text-indigo-200 text-xs">
                          {form}
                        </span>
                      ))}
                    </div>
                  </div>

                  <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                    {isTa ? result.secondary_deity.description_ta : result.secondary_deity.description_en}
                  </p>
                </div>
              )}
            </div>

            {/* Temple Landscape & Direction Radar */}
            <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
              <div className="border-b border-slate-100 dark:border-slate-800 pb-4">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 text-xs font-bold border border-emerald-200 dark:border-emerald-800/60 mb-2">
                  <Navigation className="w-3.5 h-3.5 text-emerald-600" />
                  <span>{isTa ? "கோவில் அமைவிடம் & நில அடையாளங்கள்" : "Temple Geography & Landscape Markers"}</span>
                </div>
                <h3 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white">
                  {isTa ? "பூர்வீகக் கோவில் திசை மற்றும் சூழல் ஆய்வு" : "Direction, Landscape & Sacred Tree Association"}
                </h3>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Primary Direction */}
                <div className="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/40 space-y-1">
                  <span className="text-xs font-semibold text-amber-800 dark:text-amber-400">
                    {isTa ? "முதன்மைத் திசை (Primary Direction)" : "Primary Direction"}
                  </span>
                  <div className="text-lg font-black text-amber-950 dark:text-amber-100 flex items-center gap-2">
                    <Compass className="w-5 h-5 text-amber-600" />
                    <span>{isTa ? result.temple_landscape.primary_direction_ta : result.temple_landscape.primary_direction_en}</span>
                  </div>
                  <span className="text-[11px] text-amber-700 dark:text-amber-300 block">
                    {isTa ? "பூர்வீக ஊரிலிருந்து பார்க்கும் போது" : "From ancestral homeland"}
                  </span>
                </div>

                {/* Landscape Type */}
                <div className="p-4 rounded-2xl bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-900/40 space-y-1">
                  <span className="text-xs font-semibold text-blue-800 dark:text-blue-400">
                    {isTa ? "நில அமைப்பு (Landscape Setting)" : "Landscape Setting"}
                  </span>
                  <div className="text-sm font-black text-blue-950 dark:text-blue-100">
                    {isTa ? result.temple_landscape.landscape_nature_ta : result.temple_landscape.landscape_nature_en}
                  </div>
                  <span className="text-[11px] text-blue-700 dark:text-blue-300 block">
                    {isTa ? "பஞ்சபூத தத்துவ அடிப்படையில்" : "Elemental Tattva Indication"}
                  </span>
                </div>

                {/* Sacred Trees */}
                <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-900/40 space-y-1">
                  <span className="text-xs font-semibold text-emerald-800 dark:text-emerald-400">
                    {isTa ? "புனித மரங்கள் (Sacred Sthala Vriksha)" : "Associated Sacred Trees"}
                  </span>
                  <div className="text-sm font-black text-emerald-950 dark:text-emerald-100 flex items-center gap-1.5">
                    <TreeDeciduous className="w-4 h-4 text-emerald-600 shrink-0" />
                    <span>{isTa ? result.temple_landscape.associated_sacred_tree_ta : result.temple_landscape.associated_sacred_tree_en}</span>
                  </div>
                  <span className="text-[11px] text-emerald-700 dark:text-emerald-300 block">
                    {isTa ? "கோவில் வளாகத்தில் உள்ள மரம்" : "Temple precinct flora"}
                  </span>
                </div>

                {/* Distance Indication */}
                <div className="p-4 rounded-2xl bg-purple-50 dark:bg-purple-950/30 border border-purple-200 dark:border-purple-900/40 space-y-1">
                  <span className="text-xs font-semibold text-purple-800 dark:text-purple-400">
                    {isTa ? "தொலைவு வட்டம் (Distance Radius)" : "Distance Radius"}
                  </span>
                  <div className="text-xs font-bold text-purple-950 dark:text-purple-100 leading-snug">
                    {isTa ? result.temple_landscape.distance_indication_ta : result.temple_landscape.distance_indication_en}
                  </div>
                  <span className="text-[11px] text-purple-700 dark:text-purple-300 block">
                    {isTa ? "பூர்வீக வட்டார எல்லை" : "From native circle"}
                  </span>
                </div>
              </div>
            </div>

            {/* Dosha & Blessing Status */}
            <div className={`rounded-3xl p-6 sm:p-8 border shadow-sm space-y-5 ${
              result.dosha_analysis.is_afflicted
                ? "bg-rose-50/60 dark:bg-rose-950/20 border-rose-200 dark:border-rose-900/50"
                : "bg-emerald-50/60 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-900/50"
            }`}>
              <div className="flex items-center justify-between border-b pb-4 border-slate-200 dark:border-slate-800">
                <div className="flex items-center gap-2">
                  {result.dosha_analysis.is_afflicted ? (
                    <AlertCircle className="w-6 h-6 text-rose-600 dark:text-rose-400" />
                  ) : (
                    <ShieldCheck className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
                  )}
                  <h3 className="text-lg sm:text-xl font-black text-slate-900 dark:text-white">
                    {isTa ? result.dosha_analysis.status_ta : result.dosha_analysis.status_en}
                  </h3>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-black ${
                  result.dosha_analysis.is_afflicted
                    ? "bg-rose-200 dark:bg-rose-900/60 text-rose-900 dark:text-rose-200"
                    : "bg-emerald-200 dark:bg-emerald-900/60 text-emerald-900 dark:text-emerald-200"
                }`}>
                  {result.dosha_analysis.is_afflicted ? (isTa ? "பரிகாரம் தேவை" : "Remedy Recommended") : (isTa ? "பரிபூரண அருள்" : "Active Protection")}
                </span>
              </div>

              <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                {isTa ? result.dosha_analysis.explanation_ta : result.dosha_analysis.explanation_en}
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                {/* Traditional Symptoms */}
                <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-2">
                  <span className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                    <Info className="w-4 h-4 text-amber-600" />
                    {isTa ? "குடும்பத்தில் காணப்படும் பாரம்பரிய அறிகுறிகள்:" : "Family Experience Indicators:"}
                  </span>
                  <ul className="space-y-1.5 text-xs text-slate-600 dark:text-slate-400">
                    {(isTa ? result.dosha_analysis.traditional_symptoms_ta : result.dosha_analysis.traditional_symptoms_en).map((symp, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-amber-500 font-bold">•</span>
                        <span>{symp}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Mitigation Steps */}
                <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-2">
                  <span className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    {isTa ? "உடனடி சாஸ்திர பரிகார நடவடிக்கைகள்:" : "Recommended Propitiation Actions:"}
                  </span>
                  <ul className="space-y-1.5 text-xs text-slate-600 dark:text-slate-400">
                    {(isTa ? result.dosha_analysis.mitigation_steps_ta : result.dosha_analysis.mitigation_steps_en).map((step, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-emerald-500 font-bold">✓</span>
                        <span>{step}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* Lineage Insights & Classical Sources */}
            <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
              <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-amber-600" />
                {isTa ? "சாஸ்திரக் குறிப்புகள் & வம்ச ஞானம்" : "Classical Treatises & Lineage Insights"}
              </h3>
              <div className="space-y-2">
                {(isTa ? result.lineage_insights_ta : result.lineage_insights_en).map((insight, i) => (
                  <div key={i} className="text-xs text-slate-600 dark:text-slate-300 flex items-start gap-2">
                    <span className="text-amber-600 font-black">✦</span>
                    <span>{insight}</span>
                  </div>
                ))}
              </div>
              <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex flex-wrap gap-2 text-[11px] text-slate-400">
                {result.classical_references.map((ref, idx) => (
                  <span key={idx} className="bg-slate-100 dark:bg-slate-800 px-2.5 py-1 rounded-md">
                    📜 {ref}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
