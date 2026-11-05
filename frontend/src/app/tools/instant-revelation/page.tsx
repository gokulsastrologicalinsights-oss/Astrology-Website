"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { analyzeInstantRevelation } from "@/lib/api";
import {
  InstantRevelationRequest,
  InstantRevelationResponse,
  RevelationBullet,
  FutureTimelineWindow,
} from "@/lib/types";
import {
  Sparkles,
  Compass,
  Calendar,
  Clock,
  MapPin,
  AlertCircle,
  CheckCircle2,
  AlertTriangle,
  Flame,
  ShieldCheck,
  Copy,
  Printer,
  ChevronRight,
  User,
  Zap,
  Home,
  Eye,
  Award,
  RefreshCw,
  Briefcase,
  Users,
  Activity,
  ShieldAlert,
  Heart,
  Car,
  Landmark,
  Shield,
} from "lucide-react";

const MAJOR_TN_CITIES = [
  { name: "Chennai (சென்னை)", lat: 13.0827, lon: 80.2707, tz: "Asia/Kolkata" },
  { name: "Coimbatore (கோயம்புத்தூர்)", lat: 11.0168, lon: 76.9558, tz: "Asia/Kolkata" },
  { name: "Madurai (மதுரை)", lat: 9.9252, lon: 78.1198, tz: "Asia/Kolkata" },
  { name: "Tiruchirappalli (திருச்சிராப்பள்ளி)", lat: 10.7905, lon: 78.7047, tz: "Asia/Kolkata" },
  { name: "Salem (சேலம்)", lat: 11.6643, lon: 78.146, tz: "Asia/Kolkata" },
  { name: "Tirunelveli (திருநெல்வேலி)", lat: 8.7139, lon: 77.7567, tz: "Asia/Kolkata" },
  { name: "Thanjavur (தஞ்சாவூர்)", lat: 10.787, lon: 79.1378, tz: "Asia/Kolkata" },
  { name: "Bengaluru (பெங்களூரு)", lat: 12.9716, lon: 77.5946, tz: "Asia/Kolkata" },
  { name: "Mumbai (மும்பை)", lat: 19.076, lon: 72.8777, tz: "Asia/Kolkata" },
  { name: "New Delhi (புது தில்லி)", lat: 28.6139, lon: 77.209, tz: "Asia/Kolkata" },
];

export default function InstantRevelationPage() {
  const { language, t } = useLanguage();

  // Form State
  const [name, setName] = useState("Client / ஜாதகர்");
  const [birthDate, setBirthDate] = useState("1992-08-14");
  const [birthTime, setBirthTime] = useState("06:45:00");
  const [selectedCity, setSelectedCity] = useState(MAJOR_TN_CITIES[0].name);
  const [latitude, setLatitude] = useState(MAJOR_TN_CITIES[0].lat);
  const [longitude, setLongitude] = useState(MAJOR_TN_CITIES[0].lon);
  const [timezone, setTimezone] = useState(MAJOR_TN_CITIES[0].tz);
  const [gender, setGender] = useState("male");
  const [useCurrentTime, setUseCurrentTime] = useState(true);
  const [customArrivalMoment, setCustomArrivalMoment] = useState("");

  // Saved Horoscopes for 1-Click Load
  const [savedProfiles, setSavedProfiles] = useState<any[]>([]);

  // Response State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<InstantRevelationResponse | null>(null);
  const [scriptLanguage, setScriptLanguage] = useState<"ta" | "en" | "both">("both");
  const [copied, setCopied] = useState(false);

  // Load Saved Horoscopes on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem("gai_saved_horoscopes") || localStorage.getItem("saved_horoscopes");
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setSavedProfiles(parsed);
        }
      }
    } catch {
      // Ignore fallback
    }
  }, []);

  const handleCityChange = (cityName: string) => {
    setSelectedCity(cityName);
    const found = MAJOR_TN_CITIES.find((c) => c.name === cityName);
    if (found) {
      setLatitude(found.lat);
      setLongitude(found.lon);
      setTimezone(found.tz);
    }
  };

  const handleLoadProfile = (profile: any) => {
    if (!profile) return;
    if (profile.name) setName(profile.name);
    if (profile.birth_date) setBirthDate(profile.birth_date);
    if (profile.birth_time) setBirthTime(profile.birth_time);
    if (profile.latitude) setLatitude(profile.latitude);
    if (profile.longitude) setLongitude(profile.longitude);
    if (profile.timezone) setTimezone(profile.timezone);
    if (profile.gender) setGender(profile.gender.toLowerCase());
  };

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload: InstantRevelationRequest = {
        name,
        birth_date: birthDate,
        birth_time: birthTime,
        latitude,
        longitude,
        timezone,
        gender,
        consultation_time: useCurrentTime ? new Date().toISOString() : customArrivalMoment || undefined,
      };

      const res = await analyzeInstantRevelation(payload);
      setData(res);
      // Smooth scroll to teleprompter
      setTimeout(() => {
        document.getElementById("teleprompter-view")?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    } catch (err: any) {
      setError(err?.message || "Failed to generate instant revelation dossier. Please check input parameters.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopyScript = () => {
    if (!data) return;
    const lines: string[] = [];
    lines.push(`=== ${data.name} - INSTANT CONSULTATION TELEPROMPTER ===`);
    lines.push(`Birth Date: ${data.birth_date} | Age: ${data.current_age}`);
    lines.push(`Active Cycle: ${data.current_dasa_summary}`);
    lines.push(`\n--- 1. THE MIND READER (WHY YOU ARE HERE) ---`);
    data.arrival_reason_bullets.forEach((b) => {
      lines.push(`• ${b.headline_en}:`);
      lines.push(`  EN: "${b.script_en}"`);
      lines.push(`  TA: "${b.script_ta}"`);
    });

    lines.push(`\n--- 2. VERIFIABLE PAST PROOFS (SHOCK HITS) ---`);
    data.past_verifiable_hits.forEach((h, idx) => {
      lines.push(`[Hit ${idx + 1}] (${h.calendar_period || "Past Year"}):`);
      lines.push(`  EN: "${h.script_en}"`);
      lines.push(`  TA: "${h.script_ta}"`);
    });

    lines.push(`\n--- 3. PERSONAL & DOMESTIC IDENTIFIERS ---`);
    data.personal_and_home_markers.forEach((m) => {
      lines.push(`• ${m.headline_en}:`);
      lines.push(`  EN: "${m.script_en}"`);
      lines.push(`  TA: "${m.script_ta}"`);
    });

    lines.push(`\n--- THE 5 SHOCK AMPLIFIERS ---`);
    lines.push(`[1. CAREER CALLING]:`);
    lines.push(`  EN: "${data.career_calling_en}"`);
    lines.push(`  TA: "${data.career_calling_ta}"`);
    lines.push(`[2. BIRTH ORDER & SIBLINGS]:`);
    lines.push(`  EN: "${data.family_birth_order_en}"`);
    lines.push(`  TA: "${data.family_birth_order_ta}"`);
    lines.push(`[3. SHANI & GURU GOCHARA]:`);
    lines.push(`  Phase: ${data.gochara_saturn_phase}`);
    lines.push(`  Shani EN: "${data.gochara_saturn_verdict_en}"`);
    lines.push(`  Shani TA: "${data.gochara_saturn_verdict_ta}"`);
    lines.push(`  Guru EN: "${data.gochara_jupiter_verdict_en}"`);
    lines.push(`  Guru TA: "${data.gochara_jupiter_verdict_ta}"`);
    if (data.dasa_chidra_active) {
      lines.push(`[4. DASA CHIDRA ALERT (UNTIL ${data.dasa_chidra_end_date})]:`);
      lines.push(`  EN: "${data.dasa_chidra_warning_en}"`);
      lines.push(`  TA: "${data.dasa_chidra_warning_ta}"`);
    }
    lines.push(`[5. MEDICAL VULNERABILITY]:`);
    lines.push(`  EN: "${data.medical_organ_vulnerability_en}"`);
    lines.push(`  TA: "${data.medical_organ_vulnerability_ta}"`);

    lines.push(`\n--- THE 4 ULTRA-PRECISION NADI SHOCKERS (OPTION B) ---`);
    lines.push(`[1. SPOUSE & IN-LAWS]:`);
    lines.push(`  EN: "${data.spouse_secrets_en}"`);
    lines.push(`  TA: "${data.spouse_secrets_ta}"`);
    lines.push(`[2. VEHICLE COLOR & SCRATCH MARKER]:`);
    lines.push(`  EN: "${data.vehicle_marker_en}"`);
    lines.push(`  TA: "${data.vehicle_marker_ta}"`);
    lines.push(`[3. ANCESTRAL LAND & WELL DISPUTE]:`);
    lines.push(`  EN: "${data.ancestral_land_rift_en}"`);
    lines.push(`  TA: "${data.ancestral_land_rift_ta}"`);
    lines.push(`[4. CHILDHOOD BALARISHTA ESCAPE]:`);
    lines.push(`  EN: "${data.childhood_balarishta_en}"`);
    lines.push(`  TA: "${data.childhood_balarishta_ta}"`);

    lines.push(`\n--- 4. EXACT FUTURE WINDOWS ---`);
    data.future_windows.forEach((w) => {
      lines.push(`[${w.status}] ${w.start_date} to ${w.end_date}:`);
      lines.push(`  EN: "${w.script_en}"`);
      lines.push(`  TA: "${w.script_ta}"`);
    });

    lines.push(`\n--- 5. DIRECT REMEDY ---`);
    lines.push(`Temple: ${data.temple_recommendation_en} / ${data.temple_recommendation_ta}`);
    lines.push(`Weekly Action: ${data.daily_karma_action_en} / ${data.daily_karma_action_ta}`);
    lines.push(`Gemstone/Rudraksha: ${data.gem_or_rudraksha_en} / ${data.gem_or_rudraksha_ta}`);

    navigator.clipboard.writeText(lines.join("\n"));
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="min-h-screen bg-[#FDFBF7] text-[#222222] pb-24">
      {/* Top Banner / Breadcrumb */}
      <div className="bg-[#153F6B] text-white py-8 border-b-4 border-[#B4872B] shadow-md print:hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-4">
            <Breadcrumbs
              items={[
                { label: language === "ta" ? "முகப்பு" : "Home", href: "/" },
                { label: language === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools", href: "/tools" },
                { label: language === "ta" ? "வாடிக்கையாளர் நேரடி வாக்கு பலகை" : "Instant Revelation Teleprompter" },
              ]}
            />
          </div>

          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-[#B4872B]/20 text-amber-200 border border-[#B4872B]/40 mb-2">
                <Flame className="w-3.5 h-3.5 text-[#B4872B] animate-pulse" />
                <span>ஜோதிடர் நேரடி வாக்கு அரங்கம் • Instant Client Revelation</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white flex items-center gap-3">
                <span>வாடிக்கையாளர் நேரடி வாக்கு பலகை</span>
                <span className="text-sm font-normal text-amber-200 hidden sm:inline-block">
                  (Zero-Analysis Client Shock Teleprompter)
                </span>
              </h1>
              <p className="mt-1 text-sm text-gray-200 max-w-3xl">
                வாடிக்கையாளர் அமர்ந்தவுடன் எந்தவித கிரகக் கணக்கீடும் இன்றி, அவர்களின் வருகை நோக்கம், நடந்து முடிந்த 3
                அதிர்ச்சி சம்பவங்கள், வீட்டு வாஸ்து அடையாளங்கள் மற்றும் எதிர்கால துல்லிய காலங்களை நேரடியாகப் பேசும்
                வாக்கு பலகை.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs bg-emerald-950/60 border border-emerald-500/40 text-emerald-200 px-3 py-1.5 rounded-lg flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                Live Jamakkol & BNN Engine Active
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        {/* Intake & Quick-Load Panel */}
        <div className="bg-white rounded-2xl shadow-sm border border-amber-900/10 p-6 print:hidden mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-5 border-b border-gray-100 gap-3">
            <div className="flex items-center gap-2">
              <User className="w-5 h-5 text-[#B4872B]" />
              <h2 className="text-base font-bold text-[#153F6B]">
                வாடிக்கையாளர் விபரம் (Customer Input & 1-Click Load)
              </h2>
            </div>

            {savedProfiles.length > 0 && (
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500">சேமிக்கப்பட்ட ஜாதகர்:</span>
                <select
                  className="text-xs bg-amber-50/70 border border-amber-300 rounded-lg px-2.5 py-1 text-amber-900 font-medium focus:ring-1 focus:ring-amber-500 outline-none"
                  onChange={(e) => {
                    const prof = savedProfiles.find((p) => (p.id || p.name) === e.target.value);
                    if (prof) handleLoadProfile(prof);
                  }}
                  defaultValue=""
                >
                  <option value="" disabled>
                    -- ஜாதகரைத் தேர்ந்தெடுக்கவும் --
                  </option>
                  {savedProfiles.map((p, i) => (
                    <option key={p.id || i} value={p.id || p.name}>
                      {p.name || `Profile #${i + 1}`} ({p.birth_date})
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
            <div className="lg:col-span-2">
              <label className="block text-xs font-semibold text-gray-700 mb-1">வாடிக்கையாளர் பெயர் (Client Name)</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#B4872B] focus:border-transparent outline-none"
                placeholder="எ.கா. சுரேஷ் குமார்"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">பிறந்த தேதி (Birth Date)</label>
              <input
                type="date"
                value={birthDate}
                onChange={(e) => setBirthDate(e.target.value)}
                className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#B4872B] focus:border-transparent outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">பிறந்த நேரம் (Birth Time)</label>
              <input
                type="time"
                step="1"
                value={birthTime}
                onChange={(e) => setBirthTime(e.target.value)}
                className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#B4872B] focus:border-transparent outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">பிறந்த நகரம் (City)</label>
              <select
                value={selectedCity}
                onChange={(e) => handleCityChange(e.target.value)}
                className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#B4872B] focus:border-transparent outline-none bg-white"
              >
                {MAJOR_TN_CITIES.map((c) => (
                  <option key={c.name} value={c.name}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">பாலினம் (Gender)</label>
              <select
                value={gender}
                onChange={(e) => setGender(e.target.value)}
                className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#B4872B] focus:border-transparent outline-none bg-white"
              >
                <option value="male">ஆண் (Male)</option>
                <option value="female">பெண் (Female)</option>
              </select>
            </div>
          </div>

          <div className="mt-4 pt-4 border-t border-gray-100 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-2 cursor-pointer text-xs font-medium text-gray-700">
                <input
                  type="checkbox"
                  checked={useCurrentTime}
                  onChange={(e) => setUseCurrentTime(e.target.checked)}
                  className="rounded text-[#B4872B] focus:ring-[#B4872B] w-4 h-4"
                />
                <span>வாடிக்கையாளர் வருகை நேரம்: <b>தற்போதைய வினாடி (Live Now)</b></span>
              </label>

              {!useCurrentTime && (
                <input
                  type="datetime-local"
                  value={customArrivalMoment}
                  onChange={(e) => setCustomArrivalMoment(e.target.value)}
                  className="text-xs border border-gray-300 rounded-md px-2 py-1"
                />
              )}
            </div>

            <button
              onClick={handleGenerate}
              disabled={loading}
              className="w-full sm:w-auto px-8 py-3 bg-gradient-to-r from-[#B4872B] to-[#996f21] hover:from-[#996f21] hover:to-[#7f5a18] text-white font-bold rounded-xl shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 text-sm disabled:opacity-60 cursor-pointer"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>கணக்கிடுகிறது... (Synthesizing...)</span>
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 text-amber-200 fill-amber-200" />
                  <span>உடனடி வாக்கு பலன் திரையிடு (Generate Teleprompter)</span>
                </>
              )}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* =========================================================================
            THE TELEPROMPTER VIEW
           ========================================================================= */}
        {data && (
          <div id="teleprompter-view" className="space-y-6">
            {/* Teleprompter Controls Bar */}
            <div className="bg-[#1F2937] text-white rounded-xl p-4 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4 print:hidden">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse" />
                <div className="text-sm">
                  <span className="font-semibold text-amber-300">{data.name}</span>
                  <span className="text-gray-400 mx-2">•</span>
                  <span className="text-gray-300">{data.current_age} வயது</span>
                  <span className="text-gray-400 mx-2">•</span>
                  <span className="text-emerald-300 text-xs font-mono">{data.current_dasa_summary_ta}</span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {/* Language Switch */}
                <div className="inline-flex rounded-lg bg-gray-800 p-1 border border-gray-700 text-xs">
                  <button
                    onClick={() => setScriptLanguage("ta")}
                    className={`px-3 py-1 rounded-md font-medium transition ${
                      scriptLanguage === "ta" ? "bg-[#B4872B] text-white" : "text-gray-300 hover:text-white"
                    }`}
                  >
                    தமிழ் மட்டும்
                  </button>
                  <button
                    onClick={() => setScriptLanguage("both")}
                    className={`px-3 py-1 rounded-md font-medium transition ${
                      scriptLanguage === "both" ? "bg-[#B4872B] text-white" : "text-gray-300 hover:text-white"
                    }`}
                  >
                    இருமொழி (Both)
                  </button>
                  <button
                    onClick={() => setScriptLanguage("en")}
                    className={`px-3 py-1 rounded-md font-medium transition ${
                      scriptLanguage === "en" ? "bg-[#B4872B] text-white" : "text-gray-300 hover:text-white"
                    }`}
                  >
                    English Only
                  </button>
                </div>

                <button
                  onClick={handleCopyScript}
                  className="px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-200 text-xs font-medium border border-gray-700 flex items-center gap-1.5 transition"
                  title="முழு வாக்கு பலனையும் நகலெடு"
                >
                  <Copy className="w-3.5 h-3.5 text-amber-400" />
                  <span>{copied ? "நகலெடுக்கப்பட்டது!" : "Copy Script"}</span>
                </button>

                <button
                  onClick={handlePrint}
                  className="px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-200 text-xs font-medium border border-gray-700 flex items-center gap-1.5 transition"
                  title="ஜோதிடர் பலன் ஏடு அச்சிடு"
                >
                  <Printer className="w-3.5 h-3.5 text-gray-300" />
                  <span>Print Sheet</span>
                </button>
              </div>
            </div>

            {/* CARD 0: ⚡ 10-SECOND EXECUTIVE COLD READ */}
            <div className="bg-gradient-to-br from-[#FAF2DE] via-[#FFF9ED] to-[#FAF2DE] border-2 border-[#B4872B] rounded-2xl p-6 shadow-md">
              <div className="flex items-center justify-between pb-3 mb-3 border-b border-[#B4872B]/30">
                <div className="flex items-center gap-2">
                  <Zap className="w-5 h-5 text-[#B4872B] fill-[#B4872B]" />
                  <h3 className="font-bold text-[#153F6B] text-base">
                    ⚡ 10-வினாடி பார்வை சுருக்கம் (Astrologer Fast-Scan Bullets)
                  </h3>
                </div>
                <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-[#B4872B]/20 text-[#8B6914] border border-[#B4872B]/40">
                  வாடிக்கையாளரிடம் பேசும் முன் ஒரு பார்வை
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                {(scriptLanguage === "ta" || scriptLanguage === "both") && (
                  <div className="space-y-2">
                    <span className="text-xs font-bold text-[#8B6914] uppercase tracking-wide">தமிழ் வழிகாட்டி:</span>
                    {data.quick_glance_teleprompter_ta.map((line, i) => (
                      <div key={i} className="flex items-start gap-2 bg-white/70 p-2 rounded-lg border border-amber-200/50">
                        <span className="w-5 h-5 rounded-full bg-[#B4872B] text-white text-[11px] font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                          {i + 1}
                        </span>
                        <p className="text-gray-800 text-xs sm:text-sm font-medium leading-snug">{line}</p>
                      </div>
                    ))}
                  </div>
                )}

                {(scriptLanguage === "en" || scriptLanguage === "both") && (
                  <div className="space-y-2">
                    <span className="text-xs font-bold text-[#8B6914] uppercase tracking-wide">English Cheat-Sheet:</span>
                    {data.quick_glance_teleprompter_en.map((line, i) => (
                      <div key={i} className="flex items-start gap-2 bg-white/70 p-2 rounded-lg border border-amber-200/50">
                        <span className="w-5 h-5 rounded-full bg-[#153F6B] text-white text-[11px] font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                          {i + 1}
                        </span>
                        <p className="text-gray-800 text-xs sm:text-sm font-medium leading-snug">{line}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* CARD 1: 🎯 THE MIND-READER (Why You Came Here Today) */}
            <div className="bg-white rounded-2xl shadow-md border-2 border-rose-300 overflow-hidden">
              <div className="bg-gradient-to-r from-rose-700 via-rose-800 to-rose-900 text-white px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-white/10 rounded-lg">
                    <Eye className="w-6 h-6 text-rose-200" />
                  </div>
                  <div>
                    <span className="text-[11px] font-semibold text-rose-200 tracking-wider uppercase block">
                      Pillar 1 • The Mind Reader
                    </span>
                    <h3 className="text-lg font-bold">1. வருகை நோக்கம் & தற்போதைய மனப்போராட்டம்</h3>
                  </div>
                </div>

                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-white text-rose-800 shadow-sm self-start sm:self-auto animate-pulse">
                  <span>வாடிக்கையாளரிடம் நேரடியாக வாசிக்கவும்</span>
                </span>
              </div>

              <div className="p-6 space-y-5">
                <div className="bg-rose-50 border-l-4 border-rose-600 p-4 rounded-r-xl">
                  <span className="text-xs font-bold text-rose-800 uppercase tracking-wide block mb-1">
                    பிரதான சிக்கல் (Core Diagnosis):
                  </span>
                  <p className="text-base sm:text-lg font-bold text-gray-900 leading-snug">
                    {language === "ta" || scriptLanguage === "ta" ? data.primary_arrival_reason_ta : data.primary_arrival_reason_en}
                  </p>
                  {scriptLanguage === "both" && (
                    <p className="text-xs text-gray-600 mt-1 italic">
                      {data.primary_arrival_reason_ta} / {data.primary_arrival_reason_en}
                    </p>
                  )}
                </div>

                {data.arrival_reason_bullets.map((bullet) => (
                  <div key={bullet.id} className="bg-gray-50/70 border border-gray-200 rounded-xl p-5 hover:border-rose-300 transition">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold text-rose-900 uppercase tracking-wider">
                        {scriptLanguage === "en" ? bullet.headline_en : bullet.headline_ta}
                      </span>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-100 text-rose-700">
                        {bullet.shock_factor} SHOCK
                      </span>
                    </div>

                    {(scriptLanguage === "ta" || scriptLanguage === "both") && (
                      <p className="text-base sm:text-lg font-serif text-gray-900 font-medium leading-relaxed mb-2 bg-white p-3 rounded-lg border border-gray-100 shadow-sm">
                        "{bullet.script_ta}"
                      </p>
                    )}

                    {(scriptLanguage === "en" || scriptLanguage === "both") && (
                      <p className="text-sm sm:text-base font-serif text-gray-800 font-medium leading-relaxed bg-white p-3 rounded-lg border border-gray-100 shadow-sm">
                        "{bullet.script_en}"
                      </p>
                    )}

                    <div className="mt-2 flex items-center gap-1.5 text-[11px] text-gray-500 font-mono">
                      <Compass className="w-3.5 h-3.5 text-rose-500" />
                      <span>சாஸ்திர அடிப்படை (Proof): {bullet.astrological_proof}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* CARD 2: 📜 VERIFIABLE PAST PROOFS (3 Shock-Value Hits) */}
            <div className="bg-white rounded-2xl shadow-md border-2 border-amber-300 overflow-hidden">
              <div className="bg-gradient-to-r from-[#8B6914] to-[#B4872B] text-white px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-white/10 rounded-lg">
                    <Award className="w-6 h-6 text-amber-200" />
                  </div>
                  <div>
                    <span className="text-[11px] font-semibold text-amber-100 tracking-wider uppercase block">
                      Pillar 2 • Cold-Reading Verification
                    </span>
                    <h3 className="text-lg font-bold">2. கடந்த கால உண்மைத்தன்மை சரிபார்ப்பு (3 அதிர்ச்சி உண்மைகள்)</h3>
                  </div>
                </div>

                <span className="text-xs bg-amber-950/40 text-amber-100 border border-amber-200/30 px-3 py-1 rounded-full font-medium">
                  நம்பிக்கையை உறுதிப்படுத்தும் காலங்கள்
                </span>
              </div>

              <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                {data.past_verifiable_hits.map((hit, idx) => (
                  <div key={hit.id} className="bg-gradient-to-b from-[#FFFDF9] to-[#F9F5EC] border border-amber-200 rounded-xl p-4 flex flex-col justify-between shadow-sm hover:shadow transition">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="w-6 h-6 rounded-full bg-[#B4872B] text-white text-xs font-bold flex items-center justify-center">
                          {idx + 1}
                        </span>
                        <span className="text-xs font-extrabold px-2.5 py-1 rounded bg-[#B4872B]/20 text-[#8B6914] border border-[#B4872B]/40">
                          {hit.calendar_period || "Past Event"}
                        </span>
                      </div>

                      <h4 className="text-sm font-bold text-[#153F6B] mb-2">
                        {scriptLanguage === "en" ? hit.headline_en : hit.headline_ta}
                      </h4>

                      {(scriptLanguage === "ta" || scriptLanguage === "both") && (
                        <p className="text-sm font-serif text-gray-900 leading-snug mb-2 bg-white p-2.5 rounded-lg border border-amber-100">
                          "{hit.script_ta}"
                        </p>
                      )}

                      {(scriptLanguage === "en" || scriptLanguage === "both") && (
                        <p className="text-xs font-serif text-gray-700 leading-snug bg-white p-2.5 rounded-lg border border-amber-100">
                          "{hit.script_en}"
                        </p>
                      )}
                    </div>

                    <div className="mt-3 pt-2 border-t border-amber-200/60 text-[10px] text-gray-500 font-mono">
                      {hit.astrological_proof}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* CARD 3: 🔍 PERSONAL & DOMESTIC IDENTIFIERS */}
            <div className="bg-white rounded-2xl shadow-md border-2 border-indigo-200 overflow-hidden">
              <div className="bg-gradient-to-r from-indigo-800 to-indigo-950 text-white px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-white/10 rounded-lg">
                    <Home className="w-6 h-6 text-indigo-200" />
                  </div>
                  <div>
                    <span className="text-[11px] font-semibold text-indigo-200 tracking-wider uppercase block">
                      Pillar 3 • Vastu & Physical Secrets
                    </span>
                    <h3 className="text-lg font-bold">3. பிறந்த வீட்டு வாஸ்து & உடல் ரகசிய அடையாளங்கள்</h3>
                  </div>
                </div>

                <span className="text-xs bg-indigo-900/60 text-indigo-100 border border-indigo-400/30 px-3 py-1 rounded-full font-medium">
                  பிருகு நாடி & சாராவளி பிரமாணம்
                </span>
              </div>

              <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                {data.personal_and_home_markers.map((marker) => (
                  <div key={marker.id} className="bg-indigo-50/50 border border-indigo-100 rounded-xl p-4 flex flex-col justify-between">
                    <div>
                      <span className="text-xs font-bold text-indigo-900 uppercase tracking-wide block mb-2">
                        {scriptLanguage === "en" ? marker.headline_en : marker.headline_ta}
                      </span>

                      {(scriptLanguage === "ta" || scriptLanguage === "both") && (
                        <p className="text-sm font-serif text-gray-900 leading-relaxed mb-2 bg-white p-3 rounded-lg border border-indigo-100 shadow-2xs">
                          "{marker.script_ta}"
                        </p>
                      )}

                      {(scriptLanguage === "en" || scriptLanguage === "both") && (
                        <p className="text-xs font-serif text-gray-700 leading-relaxed bg-white p-3 rounded-lg border border-indigo-100 shadow-2xs">
                          "{marker.script_en}"
                        </p>
                      )}
                    </div>

                    <div className="mt-3 pt-2 border-t border-indigo-100 text-[10px] text-gray-500 font-mono">
                      {marker.astrological_proof}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* THE 5 SHOCK AMPLIFIERS (5 துல்லிய அதிர்ச்சி உண்மைகள்) */}
            <div className="bg-gradient-to-br from-[#1E293B] via-[#0F172A] to-[#1E293B] text-white rounded-2xl shadow-xl border-2 border-amber-400/60 p-6 space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-gray-700 gap-2">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 bg-amber-400/20 rounded-xl border border-amber-400/30">
                    <Zap className="w-6 h-6 text-amber-300 fill-amber-300 animate-pulse" />
                  </div>
                  <div>
                    <span className="text-[11px] font-bold text-amber-300 uppercase tracking-widest block">
                      The 5 Shock Amplifiers • துல்லிய உச்சக்கட்ட உண்மைகள்
                    </span>
                    <h3 className="text-xl font-bold text-white flex items-center gap-2">
                      <span>எந்த வாடிக்கையாளரும் மறுக்க முடியாத 5 ரகசியங்கள்</span>
                    </h3>
                  </div>
                </div>
                <span className="text-xs bg-amber-400/10 text-amber-200 border border-amber-400/40 px-3 py-1 rounded-full font-mono self-start sm:self-auto">
                  100% Cold-Reading Verification
                </span>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
                {/* 1. Career Calling */}
                <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 hover:border-amber-400/50 transition">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Briefcase className="w-4 h-4 text-amber-400" />
                      <span className="text-xs font-bold text-amber-300 uppercase tracking-wider">
                        1. தொழில் காரகம் & துறை (Career Calling)
                      </span>
                    </div>
                    <div className="flex gap-1 flex-wrap">
                      {data.career_fields.map((f, i) => (
                        <span key={i} className="text-[10px] font-semibold bg-amber-400/20 text-amber-200 px-2 py-0.5 rounded">
                          {f}
                        </span>
                      ))}
                    </div>
                  </div>

                  {(scriptLanguage === "ta" || scriptLanguage === "both") && (
                    <p className="text-sm sm:text-base font-serif text-gray-100 leading-relaxed mb-2 bg-slate-900/70 p-3 rounded-lg border border-slate-700">
                      "{data.career_calling_ta}"
                    </p>
                  )}
                  {(scriptLanguage === "en" || scriptLanguage === "both") && (
                    <p className="text-xs sm:text-sm font-serif text-gray-300 leading-relaxed bg-slate-900/70 p-3 rounded-lg border border-slate-700">
                      "{data.career_calling_en}"
                    </p>
                  )}
                </div>

                {/* 2. Birth Order & Sibling Secret */}
                <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 hover:border-amber-400/50 transition">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Users className="w-4 h-4 text-rose-400" />
                      <span className="text-xs font-bold text-rose-300 uppercase tracking-wider">
                        2. பிறப்பு வரிசை & குடும்ப ரகசியம் (Birth Order)
                      </span>
                    </div>
                    <span className="text-[10px] font-bold bg-rose-500/20 text-rose-300 px-2 py-0.5 rounded border border-rose-500/30">
                      மூத்தவர் / உடன்பிறப்பு கண்டம்
                    </span>
                  </div>

                  {(scriptLanguage === "ta" || scriptLanguage === "both") && (
                    <p className="text-sm sm:text-base font-serif text-gray-100 leading-relaxed mb-2 bg-slate-900/70 p-3 rounded-lg border border-slate-700">
                      "{data.family_birth_order_ta}"
                    </p>
                  )}
                  {(scriptLanguage === "en" || scriptLanguage === "both") && (
                    <p className="text-xs sm:text-sm font-serif text-gray-300 leading-relaxed bg-slate-900/70 p-3 rounded-lg border border-slate-700">
                      "{data.family_birth_order_en}"
                    </p>
                  )}
                </div>

                {/* 3. Gochara Sledgehammer: Shani & Guru */}
                <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 hover:border-amber-400/50 transition lg:col-span-2">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-3 gap-2">
                    <div className="flex items-center gap-2">
                      <Activity className="w-4 h-4 text-purple-400" />
                      <span className="text-xs font-bold text-purple-300 uppercase tracking-wider">
                        3. சனி மற்றும் குரு பெயர்ச்சி நேரடி தாக்கம் (Gochara Sledgehammer)
                      </span>
                    </div>
                    <span className="text-xs font-bold px-3 py-1 rounded-full bg-purple-950 border border-purple-400 text-purple-200 self-start sm:self-auto">
                      {data.gochara_saturn_phase}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs sm:text-sm">
                    <div className="bg-slate-900/70 p-3 rounded-lg border border-slate-700 space-y-1.5">
                      <span className="font-bold text-amber-300 text-xs flex items-center gap-1.5">
                        <Flame className="w-3.5 h-3.5 text-amber-400" />
                        சனிப் பெயர்ச்சி நேரடி வாக்கு (Saturn Verdict):
                      </span>
                      <p className="font-serif text-gray-200 leading-relaxed">
                        {scriptLanguage === "en" ? data.gochara_saturn_verdict_en : data.gochara_saturn_verdict_ta}
                      </p>
                      {scriptLanguage === "both" && (
                        <p className="font-serif text-gray-400 text-xs italic">
                          {data.gochara_saturn_verdict_en}
                        </p>
                      )}
                    </div>

                    <div className="bg-slate-900/70 p-3 rounded-lg border border-slate-700 space-y-1.5">
                      <span className="font-bold text-emerald-300 text-xs flex items-center gap-1.5">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                        குருப் பார்வை மற்றும் அருள் (Jupiter Shield):
                      </span>
                      <p className="font-serif text-gray-200 leading-relaxed">
                        {scriptLanguage === "en" ? data.gochara_jupiter_verdict_en : data.gochara_jupiter_verdict_ta}
                      </p>
                      {scriptLanguage === "both" && (
                        <p className="font-serif text-gray-400 text-xs italic">
                          {data.gochara_jupiter_verdict_en}
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                {/* 4. Dasa Chidra Alert */}
                <div
                  className={`border rounded-xl p-5 transition ${
                    data.dasa_chidra_active
                      ? "bg-rose-950/60 border-rose-500 shadow-lg shadow-rose-950/50 ring-2 ring-rose-500/50"
                      : "bg-slate-800/80 border-slate-700/80"
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className={`w-4 h-4 ${data.dasa_chidra_active ? "text-rose-400 animate-bounce" : "text-emerald-400"}`} />
                      <span className={`text-xs font-bold uppercase tracking-wider ${data.dasa_chidra_active ? "text-rose-300" : "text-emerald-300"}`}>
                        4. தசா சந்தி எச்சரிக்கை (Dasa Chidra Alert)
                      </span>
                    </div>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        data.dasa_chidra_active
                          ? "bg-rose-500 text-white animate-pulse"
                          : "bg-emerald-500/20 text-emerald-300"
                      }`}
                    >
                      {data.dasa_chidra_active ? `தீவிர முடக்கம் (${data.dasa_chidra_end_date} வரை)` : "சீரான தசா காலம் (Normal)"}
                    </span>
                  </div>

                  {data.dasa_chidra_active ? (
                    <div className="space-y-2">
                      {(scriptLanguage === "ta" || scriptLanguage === "both") && (
                        <p className="text-sm font-serif text-rose-100 leading-relaxed bg-black/40 p-3 rounded-lg border border-rose-500/40">
                          "{data.dasa_chidra_warning_ta}"
                        </p>
                      )}
                      {(scriptLanguage === "en" || scriptLanguage === "both") && (
                        <p className="text-xs font-serif text-rose-200 leading-relaxed bg-black/40 p-3 rounded-lg border border-rose-500/40">
                          "{data.dasa_chidra_warning_en}"
                        </p>
                      )}
                    </div>
                  ) : (
                    <p className="text-xs text-gray-400 leading-relaxed bg-slate-900/60 p-3 rounded-lg">
                      மகாதிசை சுமுகமாக இயங்குகிறது; தசா சந்தி தொடர்பான திடீர் முடக்கங்கள் தற்சமயம் இல்லை.
                    </p>
                  )}
                </div>

                {/* 5. Medical Vulnerability */}
                <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-5 hover:border-amber-400/50 transition">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <ShieldAlert className="w-4 h-4 text-amber-400" />
                      <span className="text-xs font-bold text-amber-300 uppercase tracking-wider">
                        5. உடல்நலக் கோளாறு & பலவீன உறுப்பு (Medical Alert)
                      </span>
                    </div>
                    <div className="flex gap-1 flex-wrap">
                      {data.vulnerable_organs.map((org, idx) => (
                        <span key={idx} className="text-[10px] font-medium bg-red-950/80 text-rose-300 border border-rose-800/50 px-2 py-0.5 rounded">
                          {org}
                        </span>
                      ))}
                    </div>
                  </div>

                  {(scriptLanguage === "ta" || scriptLanguage === "both") && (
                    <p className="text-sm sm:text-base font-serif text-gray-100 leading-relaxed mb-2 bg-slate-900/70 p-3 rounded-lg border border-slate-700">
                      "{data.medical_organ_vulnerability_ta}"
                    </p>
                  )}
                  {(scriptLanguage === "en" || scriptLanguage === "both") && (
                    <p className="text-xs sm:text-sm font-serif text-gray-300 leading-relaxed bg-slate-900/70 p-3 rounded-lg border border-slate-700">
                      "{data.medical_organ_vulnerability_en}"
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* ULTRA-PRECISION NADI SHOCKERS (4 அதிநுட்ப பிருகு நாடி ரகசியங்கள் - Option B) */}
            <div className="bg-gradient-to-br from-[#1F1610] via-[#2A1810] to-[#140E0A] text-white rounded-2xl shadow-xl border-2 border-orange-400/60 p-6 space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-orange-900/60 gap-2">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 bg-orange-400/20 rounded-xl border border-orange-400/30">
                    <Sparkles className="w-6 h-6 text-orange-300 animate-spin" />
                  </div>
                  <div>
                    <span className="text-[11px] font-bold text-orange-300 uppercase tracking-widest block">
                      Ultra-Precision Nadi Secrets • அதிநுட்ப பிருகு நாடி ரகசியங்கள்
                    </span>
                    <h3 className="text-xl font-bold text-white flex items-center gap-2">
                      <span>4 அதிநுட்ப நாடி ரகசிய வாக்குகள் (Instant Jaw-Droppers)</span>
                    </h3>
                  </div>
                </div>
                <span className="text-xs bg-orange-400/10 text-orange-200 border border-orange-400/40 px-3 py-1 rounded-full font-mono self-start sm:self-auto">
                  Classical Nadi Palm-Leaf Precision
                </span>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
                {/* 1. Spouse & In-Laws Secrets */}
                <div className="bg-stone-900/80 border border-orange-900/40 rounded-xl p-5 hover:border-pink-400/50 transition">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Heart className="w-4 h-4 text-pink-400" />
                      <span className="text-xs font-bold text-pink-300 uppercase tracking-wider">
                        1. களத்திரம் & மாமனார் வழி ரகசியங்கள் (Spouse & In-Laws)
                      </span>
                    </div>
                    <span className="text-[10px] font-bold bg-pink-500/20 text-pink-300 px-2 py-0.5 rounded border border-pink-500/30">
                      களத்திர காரகன் & 7-ம் பாவம்
                    </span>
                  </div>

                  {(scriptLanguage === "ta" || scriptLanguage === "both") && (
                    <p className="text-sm sm:text-base font-serif text-gray-100 leading-relaxed mb-2 bg-black/40 p-3 rounded-lg border border-pink-900/30">
                      "{data.spouse_secrets_ta}"
                    </p>
                  )}
                  {(scriptLanguage === "en" || scriptLanguage === "both") && (
                    <p className="text-xs sm:text-sm font-serif text-gray-300 leading-relaxed bg-black/40 p-3 rounded-lg border border-pink-900/30">
                      "{data.spouse_secrets_en}"
                    </p>
                  )}
                </div>

                {/* 2. Vehicle & Conveyance Marker */}
                <div className="bg-stone-900/80 border border-orange-900/40 rounded-xl p-5 hover:border-cyan-400/50 transition">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Car className="w-4 h-4 text-cyan-400" />
                      <span className="text-xs font-bold text-cyan-300 uppercase tracking-wider">
                        2. வாகன நிறம் & பழுது அடையாளம் (Vehicle Marker)
                      </span>
                    </div>
                    <span className="text-[10px] font-bold bg-cyan-500/20 text-cyan-300 px-2 py-0.5 rounded border border-cyan-500/30">
                      சுக்கிரன் & 4-ம் அதிபதி
                    </span>
                  </div>

                  {(scriptLanguage === "ta" || scriptLanguage === "both") && (
                    <p className="text-sm sm:text-base font-serif text-gray-100 leading-relaxed mb-2 bg-black/40 p-3 rounded-lg border border-cyan-900/30">
                      "{data.vehicle_marker_ta}"
                    </p>
                  )}
                  {(scriptLanguage === "en" || scriptLanguage === "both") && (
                    <p className="text-xs sm:text-sm font-serif text-gray-300 leading-relaxed bg-black/40 p-3 rounded-lg border border-cyan-900/30">
                      "{data.vehicle_marker_en}"
                    </p>
                  )}
                </div>

                {/* 3. Ancestral Land & Well Dispute */}
                <div className="bg-stone-900/80 border border-orange-900/40 rounded-xl p-5 hover:border-amber-400/50 transition">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Landmark className="w-4 h-4 text-amber-400" />
                      <span className="text-xs font-bold text-amber-300 uppercase tracking-wider">
                        3. பூர்வீக சொத்து & தந்தை வழி சிக்கல் (Ancestral Land / Well)
                      </span>
                    </div>
                    <span className="text-[10px] font-bold bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded border border-amber-500/30">
                      சூரியன் - செவ்வாய் நாடி
                    </span>
                  </div>

                  {(scriptLanguage === "ta" || scriptLanguage === "both") && (
                    <p className="text-sm sm:text-base font-serif text-gray-100 leading-relaxed mb-2 bg-black/40 p-3 rounded-lg border border-amber-900/30">
                      "{data.ancestral_land_rift_ta}"
                    </p>
                  )}
                  {(scriptLanguage === "en" || scriptLanguage === "both") && (
                    <p className="text-xs sm:text-sm font-serif text-gray-300 leading-relaxed bg-black/40 p-3 rounded-lg border border-amber-900/30">
                      "{data.ancestral_land_rift_en}"
                    </p>
                  )}
                </div>

                {/* 4. Childhood Balarishta Escape */}
                <div className="bg-stone-900/80 border border-orange-900/40 rounded-xl p-5 hover:border-emerald-400/50 transition">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Shield className="w-4 h-4 text-emerald-400" />
                      <span className="text-xs font-bold text-emerald-300 uppercase tracking-wider">
                        4. பாலாரிஷ்டம் - சிறுவயது கண்டம் (Childhood Balarishta)
                      </span>
                    </div>
                    <span className="text-[10px] font-bold bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded border border-emerald-500/30">
                      மரண கண்டத்திலிருந்து தப்பிய வயது
                    </span>
                  </div>

                  {(scriptLanguage === "ta" || scriptLanguage === "both") && (
                    <p className="text-sm sm:text-base font-serif text-gray-100 leading-relaxed mb-2 bg-black/40 p-3 rounded-lg border border-emerald-900/30">
                      "{data.childhood_balarishta_ta}"
                    </p>
                  )}
                  {(scriptLanguage === "en" || scriptLanguage === "both") && (
                    <p className="text-xs sm:text-sm font-serif text-gray-300 leading-relaxed bg-black/40 p-3 rounded-lg border border-emerald-900/30">
                      "{data.childhood_balarishta_en}"
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* CARD 4: ⏳ FUTURE TIMELINE WINDOWS (Next 12–24 Months) */}
            <div className="bg-white rounded-2xl shadow-md border-2 border-emerald-300 overflow-hidden">
              <div className="bg-gradient-to-r from-emerald-800 to-teal-900 text-white px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-white/10 rounded-lg">
                    <Calendar className="w-6 h-6 text-emerald-200" />
                  </div>
                  <div>
                    <span className="text-[11px] font-semibold text-emerald-200 tracking-wider uppercase block">
                      Pillar 4 • Predictive Windows
                    </span>
                    <h3 className="text-lg font-bold">4. இனி நடக்கப்போகும் துல்லிய காலங்கள் (Next 12–24 Months)</h3>
                  </div>
                </div>

                <span className="text-xs bg-emerald-950/60 text-emerald-100 border border-emerald-300/30 px-3 py-1 rounded-full font-medium">
                  அபாய மற்றும் வெற்றி காலக்கட்டங்கள்
                </span>
              </div>

              <div className="p-6 space-y-4">
                {data.future_windows.map((win, idx) => {
                  const isRed = win.status === "RED_ALERT";
                  const isGreen = win.status === "GOLDEN_BREAKTHROUGH";

                  return (
                    <div
                      key={idx}
                      className={`border-2 rounded-xl p-5 ${
                        isRed
                          ? "bg-rose-50/50 border-rose-300"
                          : isGreen
                          ? "bg-emerald-50/50 border-emerald-400"
                          : "bg-amber-50/40 border-amber-300"
                      }`}
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                        <div className="flex items-center gap-2">
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-bold tracking-wide uppercase ${
                              isRed
                                ? "bg-rose-600 text-white"
                                : isGreen
                                ? "bg-emerald-600 text-white"
                                : "bg-amber-600 text-white"
                            }`}
                          >
                            {isRed ? "🔴 எச்சரிக்கை காலம் (Caution)" : isGreen ? "🟢 வெற்றி காலம் (Breakthrough)" : "🟡 தயாரிப்பு காலம் (Preparation)"}
                          </span>
                          <h4 className="font-bold text-gray-900 text-sm sm:text-base">
                            {scriptLanguage === "en" ? win.title_en : win.title_ta}
                          </h4>
                        </div>

                        <span className="text-xs font-mono font-bold bg-white px-3 py-1 rounded-lg border border-gray-300 text-gray-800 shadow-2xs">
                          {win.start_date} முதல் {win.end_date} வரை
                        </span>
                      </div>

                      {(scriptLanguage === "ta" || scriptLanguage === "both") && (
                        <p className="text-base font-serif text-gray-900 leading-relaxed mb-2 bg-white p-3 rounded-lg border border-gray-200 shadow-2xs font-medium">
                          "{win.script_ta}"
                        </p>
                      )}

                      {(scriptLanguage === "en" || scriptLanguage === "both") && (
                        <p className="text-sm font-serif text-gray-700 leading-relaxed bg-white p-3 rounded-lg border border-gray-200 shadow-2xs mb-3">
                          "{win.script_en}"
                        </p>
                      )}

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3 pt-3 border-t border-gray-200 text-xs">
                        <div className="bg-emerald-100/60 p-2.5 rounded-lg border border-emerald-200">
                          <span className="font-bold text-emerald-900 flex items-center gap-1 mb-1">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
                            செய்ய வேண்டியவை (Do's):
                          </span>
                          <ul className="list-disc list-inside space-y-0.5 text-emerald-950 font-medium">
                            {(scriptLanguage === "ta" || scriptLanguage === "both" ? win.do_rules_ta : win.do_rules_en).map((rule, rIdx) => (
                              <li key={rIdx}>{rule}</li>
                            ))}
                          </ul>
                        </div>

                        <div className="bg-rose-100/60 p-2.5 rounded-lg border border-rose-200">
                          <span className="font-bold text-rose-900 flex items-center gap-1 mb-1">
                            <AlertTriangle className="w-3.5 h-3.5 text-rose-700" />
                            தவிர்க்க வேண்டியவை (Don'ts):
                          </span>
                          <ul className="list-disc list-inside space-y-0.5 text-rose-950 font-medium">
                            {(scriptLanguage === "ta" || scriptLanguage === "both" ? win.dont_rules_ta : win.dont_rules_en).map((rule, rIdx) => (
                              <li key={rIdx}>{rule}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* CARD 5: 🪔 DIRECT TURN-KEY REMEDY */}
            <div className="bg-white rounded-2xl shadow-md border-2 border-[#B4872B] overflow-hidden">
              <div className="bg-gradient-to-r from-[#153F6B] to-[#205284] text-white px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-white/10 rounded-lg">
                    <Flame className="w-6 h-6 text-amber-300" />
                  </div>
                  <div>
                    <span className="text-[11px] font-semibold text-amber-200 tracking-wider uppercase block">
                      Pillar 5 • Direct Turn-Key Remedy
                    </span>
                    <h3 className="text-lg font-bold">5. உடனடி நேரடி பரிகாரம் & திருப்புமுனை</h3>
                  </div>
                </div>

                <span className="text-xs bg-[#B4872B] text-white font-bold px-3 py-1 rounded-full shadow-sm">
                  1-Action Solution
                </span>
              </div>

              <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-amber-50/70 border border-amber-200 rounded-xl p-4">
                  <span className="text-xs font-bold text-amber-900 uppercase tracking-wide flex items-center gap-1.5 mb-2">
                    <Compass className="w-4 h-4 text-[#B4872B]" />
                    செல்ல வேண்டிய புண்ணிய தலம் (Sacred Temple):
                  </span>
                  <p className="text-base font-bold text-gray-900 mb-1">
                    {data.temple_recommendation_ta}
                  </p>
                  <p className="text-xs text-gray-600">
                    {data.temple_recommendation_en}
                  </p>
                </div>

                <div className="bg-emerald-50/70 border border-emerald-200 rounded-xl p-4">
                  <span className="text-xs font-bold text-emerald-900 uppercase tracking-wide flex items-center gap-1.5 mb-2">
                    <ShieldCheck className="w-4 h-4 text-emerald-600" />
                    வாராந்திர கர்ம செயல் (Weekly Action):
                  </span>
                  <p className="text-sm font-medium text-gray-900 leading-snug mb-1">
                    {data.daily_karma_action_ta}
                  </p>
                  <p className="text-xs text-gray-600 leading-snug">
                    {data.daily_karma_action_en}
                  </p>
                </div>

                <div className="bg-indigo-50/70 border border-indigo-200 rounded-xl p-4">
                  <span className="text-xs font-bold text-indigo-900 uppercase tracking-wide flex items-center gap-1.5 mb-2">
                    <Sparkles className="w-4 h-4 text-indigo-600" />
                    ரத்தினம் & ருத்ராட்சம் (Gem & Rudraksha):
                  </span>
                  <p className="text-sm font-medium text-gray-900 leading-snug mb-1">
                    {data.gem_or_rudraksha_ta}
                  </p>
                  <p className="text-xs text-gray-600 leading-snug">
                    {data.gem_or_rudraksha_en}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
