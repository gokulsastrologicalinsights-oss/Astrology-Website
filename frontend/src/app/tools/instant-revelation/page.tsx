"use client";

import React, { useState, useEffect, useMemo, useCallback } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { analyzeInstantRevelation, calculateHoroscope } from "@/lib/api";
import { SouthIndianChart } from "@/components/charts/SouthIndianChart";
import { buildNavamsaHoroscope } from "@/lib/chart-transforms";
import {
  InstantRevelationRequest,
  InstantRevelationResponse,
  RevelationBullet,
  FutureTimelineWindow,
  HoroscopeResponse,
} from "@/lib/types";
import {
  getRasiNameTamil,
  getPlanetNameTamil,
  getNakshatraTamil,
} from "@/lib/tamil-astrology";
import { getGrahaDignity } from "@/lib/dignity";
import { formatDms } from "@/lib/formatters";
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
  Search,
  ExternalLink,
  FolderOpen,
  X,
  Check,
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

function InstantRevelationContent() {
  const { language, t } = useLanguage();
  const { session, isAuthenticated } = useAuth();
  const searchParams = useSearchParams();
  const idParam = searchParams.get("id");

  // Mode: Saved Horoscopes vs Manual Entry
  const [inputMode, setInputMode] = useState<"saved" | "manual">(idParam ? "saved" : "saved");
  const [savedSearchQuery, setSavedSearchQuery] = useState("");
  const [selectedSavedId, setSelectedSavedId] = useState<string | null>(idParam);
  const [loadingSavedList, setLoadingSavedList] = useState(false);

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

  // Chart Viewer State
  const [showChartViewer, setShowChartViewer] = useState(false);
  const [chartTab, setChartTab] = useState<"rasi" | "navamsa" | "table">("rasi");
  const [chartData, setChartData] = useState<HoroscopeResponse | null>(null);
  const [loadingChartData, setLoadingChartData] = useState(false);

  // Response State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<InstantRevelationResponse | null>(null);
  const [scriptLanguage, setScriptLanguage] = useState<"ta" | "en" | "both">("both");
  const [copied, setCopied] = useState(false);
  const [shockerFilter, setShockerFilter] = useState<"all" | "EXTREME" | "HIGH">("all");
  const [showAllShockers, setShowAllShockers] = useState(false);

  // Ensure Chart Data exists (computes or extracts from snapshot)
  const ensureChartData = useCallback(async (profileToUse?: any) => {
    // If profile has calculation snapshot with planets
    const snapshot = profileToUse?.calculation_result || profileToUse?.horoscope;
    if (snapshot?.planets && snapshot?.ascendant) {
      setChartData(snapshot as HoroscopeResponse);
      return snapshot as HoroscopeResponse;
    }
    const innerHoro = snapshot?.horoscope;
    if (innerHoro?.planets && innerHoro?.ascendant) {
      setChartData(innerHoro as HoroscopeResponse);
      return innerHoro as HoroscopeResponse;
    }

    setLoadingChartData(true);
    try {
      const bDate = profileToUse?.birth_date || birthDate;
      const bTime = profileToUse?.birth_time || birthTime;
      const lat = profileToUse?.latitude || latitude;
      const lon = profileToUse?.longitude || longitude;
      const tz = profileToUse?.timezone || timezone;

      const res = await calculateHoroscope({
        birth_date: bDate,
        birth_time: bTime,
        latitude: lat,
        longitude: lon,
        timezone: tz,
        ayanamsa: 0,
        house_system: 0,
        include_panchang: false,
        include_outer_planets: true,
      });
      setChartData(res);
      return res;
    } catch (e) {
      console.warn("Could not calculate visual chart data:", e);
      return null;
    } finally {
      setLoadingChartData(false);
    }
  }, [birthDate, birthTime, latitude, longitude, timezone]);

  const handleCityChange = (cityName: string) => {
    setSelectedCity(cityName);
    const found = MAJOR_TN_CITIES.find((c) => c.name === cityName);
    if (found) {
      setLatitude(found.lat);
      setLongitude(found.lon);
      setTimezone(found.tz);
    }
  };

  const handleLoadProfile = useCallback((profile: any, autoRun = false) => {
    if (!profile) return;
    const resolvedName = profile.person_name || profile.name || "Client";
    setName(resolvedName);
    if (profile.birth_date) setBirthDate(profile.birth_date);
    if (profile.birth_time) setBirthTime(profile.birth_time);
    if (profile.latitude) setLatitude(profile.latitude);
    if (profile.longitude) setLongitude(profile.longitude);
    if (profile.timezone) setTimezone(profile.timezone);
    if (profile.gender) setGender(profile.gender.toLowerCase());
    if (profile.id) setSelectedSavedId(profile.id);

    const place = profile.birthplace || profile.location_name;
    if (place) setSelectedCity(place);

    // Extract or pre-fill chart data
    const snapshot = profile.calculation_result || profile.horoscope;
    if (snapshot?.planets && snapshot?.ascendant) {
      setChartData(snapshot as HoroscopeResponse);
    } else if (snapshot?.horoscope?.planets) {
      setChartData(snapshot.horoscope as HoroscopeResponse);
    }

    if (autoRun) {
      setTimeout(() => {
        runRevelationWithPayload({
          name: resolvedName,
          birth_date: profile.birth_date,
          birth_time: profile.birth_time,
          latitude: profile.latitude,
          longitude: profile.longitude,
          timezone: profile.timezone || "Asia/Kolkata",
          gender: (profile.gender || "male").toLowerCase(),
          saved_horoscope_id: profile.id,
        });
      }, 50);
    }
  }, []);

  // Load Saved Horoscopes on mount & fetch from database
  useEffect(() => {
    async function loadAllSaved() {
      setLoadingSavedList(true);
      const combined: any[] = [];

      // 1. Local Storage Fallback
      try {
        const stored = localStorage.getItem("gai_saved_horoscopes") || localStorage.getItem("saved_horoscopes");
        if (stored) {
          const parsed = JSON.parse(stored);
          if (Array.isArray(parsed)) {
            parsed.forEach((item) => {
              combined.push({
                ...item,
                person_name: item.name || item.person_name,
              });
            });
          }
        }
      } catch {}

      // 2. Fetch authenticated database horoscopes
      try {
        const headers: Record<string, string> = {};
        if (session?.access_token) {
          headers["Authorization"] = `Bearer ${session.access_token}`;
        }
        const resp = await fetch("/api/horoscopes?limit=1000", { headers });
        if (resp.ok) {
          const resJson = await resp.json();
          const dbItems = resJson.horoscopes || [];
          dbItems.forEach((h: any) => {
            if (!combined.some((c) => c.id === h.id)) {
              combined.push(h);
            }
          });
        }
      } catch (err) {
        console.warn("Could not load database horoscopes:", err);
      }

      setSavedProfiles(combined);
      setLoadingSavedList(false);

      // Handle ?id= param
      if (idParam) {
        const target = combined.find((p) => p.id === idParam);
        if (target) {
          handleLoadProfile(target, true);
        } else {
          // Fetch single horoscope by ID
          try {
            const singleResp = await fetch(`/api/horoscopes/${idParam}`);
            if (singleResp.ok) {
              const singleJson = await singleResp.json();
              if (singleJson.horoscope) {
                handleLoadProfile(singleJson.horoscope, true);
              }
            }
          } catch {}
        }
      }
    }

    loadAllSaved();
  }, [session?.access_token, idParam, handleLoadProfile]);

  // Filtered saved profiles
  const filteredSavedProfiles = useMemo(() => {
    if (!savedSearchQuery.trim()) return savedProfiles;
    const q = savedSearchQuery.toLowerCase().trim();
    return savedProfiles.filter((p) => {
      const pName = (p.person_name || p.name || "").toLowerCase();
      const pDate = (p.birth_date || "").toLowerCase();
      const pCity = (p.birthplace || p.location_name || "").toLowerCase();
      return pName.includes(q) || pDate.includes(q) || pCity.includes(q);
    });
  }, [savedProfiles, savedSearchQuery]);

  const runRevelationWithPayload = async (customPayload?: Partial<InstantRevelationRequest>) => {
    setLoading(true);
    setError(null);
    try {
      const payload: InstantRevelationRequest = {
        name: customPayload?.name || name,
        birth_date: customPayload?.birth_date || birthDate,
        birth_time: customPayload?.birth_time || birthTime,
        latitude: customPayload?.latitude || latitude,
        longitude: customPayload?.longitude || longitude,
        timezone: customPayload?.timezone || timezone,
        gender: customPayload?.gender || gender,
        saved_horoscope_id: customPayload?.saved_horoscope_id || selectedSavedId || undefined,
        consultation_time: useCurrentTime ? new Date().toISOString() : customArrivalMoment || undefined,
      };

      const res = await analyzeInstantRevelation(payload);
      setData(res);

      // Auto-load chart data in background so the user can toggle chart immediately
      ensureChartData();

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

  const handleGenerate = () => {
    runRevelationWithPayload();
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

    if (data.lagna_nadiamsa_name) {
      lines.push(`\n--- DEVA KERALAM (CHANDRA KALA NADI) 150 NADIAMSA & LONGEVITY ---`);
      lines.push(`Lagna Nadiamsa: #${data.lagna_nadiamsa_number} (${data.lagna_nadiamsa_name_ta} / ${data.lagna_nadiamsa_name}) - ${data.lagna_nadiamsa_half_ta}`);
      lines.push(`Delineation (TA): "${data.lagna_nadiamsa_script_ta}"`);
      lines.push(`Delineation (EN): "${data.lagna_nadiamsa_script_en}"`);
      lines.push(`Longevity Class: ${data.khanda_nirnaya_longevity_ta}`);
      lines.push(`Father Critical Transit Degree: ${data.father_critical_degree}`);
      lines.push(`Mother Critical Transit Degree: ${data.mother_critical_degree}`);
    }

    if (data.guaranteed_chart_shockers && data.guaranteed_chart_shockers.length > 0) {
      lines.push(`\n--- பிருகு நந்தி நாடி சாஸ்திரக் காரகங்கள் (BNN & CLASSICAL VERIFIED) ---`);
      data.guaranteed_chart_shockers.forEach((s, idx) => {
        lines.push(`[${idx + 1}] [${s.shock_factor} SHOCK] ${s.headline_en} / ${s.headline_ta}:`);
        lines.push(`  TA: "${s.script_ta}"`);
        lines.push(`  EN: "${s.script_en}"`);
        lines.push(`  PROOF: ${s.astrological_proof}`);
      });
    }

    if (data.remedial_taboos_ta && data.remedial_taboos_ta.length > 0) {
      lines.push(`\n--- STRICT SHASTRIC TABOOS & DIETARY RESTRICTIONS ---`);
      data.remedial_taboos_ta.forEach((t) => lines.push(`• ${t}`));
    }

    lines.push(`\n--- THE 5 SHOCK AMPLIFIERS ---`);
    lines.push(`[1. CAREER CALLING]:`);
    lines.push(`  EN: "${data.career_calling_en}"`);
    lines.push(`  TA: "${data.career_calling_ta}"`);
    lines.push(`[2. BIRTH ORDER & SIBLINGS]:`);
    lines.push(`  EN: "${data.family_birth_order_en}"`);
    lines.push(`  TA: "${data.family_birth_order_ta}"`);
    lines.push(`[3. SHANI & GURU GOCHARA]:`);
    lines.push(`  EN: "${data.gochara_saturn_verdict_en} | ${data.gochara_jupiter_verdict_en}"`);
    lines.push(`  TA: "${data.gochara_saturn_verdict_ta} | ${data.gochara_jupiter_verdict_ta}"`);
    lines.push(`[4. DASA CHIDRA ALERT]:`);
    lines.push(`  Active: ${data.dasa_chidra_active}`);
    if (data.dasa_chidra_active) {
      lines.push(`  EN: "${data.dasa_chidra_warning_en}"`);
      lines.push(`  TA: "${data.dasa_chidra_warning_ta}"`);
    }
    lines.push(`[5. MEDICAL ORGAN VULNERABILITY]:`);
    lines.push(`  EN: "${data.medical_organ_vulnerability_en}"`);
    lines.push(`  TA: "${data.medical_organ_vulnerability_ta}"`);

    lines.push(`\n--- 4 ULTRA-PRECISION NADI SHOCKERS (OPTION B) ---`);
    lines.push(`[1. SPOUSE & IN-LAWS SECRETS]:`);
    lines.push(`  EN: "${data.spouse_secrets_en}"`);
    lines.push(`  TA: "${data.spouse_secrets_ta}"`);
    lines.push(`[2. VEHICLE & CONVEYANCE MARKER]:`);
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
                அதிர்ச்சி சம்பவங்கள், வீட்டு வாஸ்து அடையாளங்கள், 4 பிருகு நாடி ரகசியங்கள் மற்றும் எதிர்கால துல்லிய காலங்களை
                நேரடியாகப் பேசும் வாக்கு பலகை.
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
                வாடிக்கையாளர் விபரம் (Customer Intake & Saved Charts)
              </h2>
            </div>

            {/* Input Mode Toggle */}
            <div className="flex items-center gap-2">
              <div className="inline-flex rounded-lg bg-gray-100 p-1 border border-gray-200 text-xs">
                <button
                  type="button"
                  onClick={() => setInputMode("saved")}
                  className={`px-3 py-1.5 rounded-md font-semibold transition flex items-center gap-1.5 ${
                    inputMode === "saved"
                      ? "bg-[#153F6B] text-white shadow-xs"
                      : "text-gray-600 hover:text-gray-900"
                  }`}
                >
                  <FolderOpen className="w-3.5 h-3.5" />
                  <span>சேமிக்கப்பட்ட ஜாதகங்கள் ({savedProfiles.length})</span>
                </button>
                <button
                  type="button"
                  onClick={() => setInputMode("manual")}
                  className={`px-3 py-1.5 rounded-md font-semibold transition flex items-center gap-1.5 ${
                    inputMode === "manual"
                      ? "bg-[#153F6B] text-white shadow-xs"
                      : "text-gray-600 hover:text-gray-900"
                  }`}
                >
                  <User className="w-3.5 h-3.5" />
                  <span>புதிய வாடிக்கையாளர் (Manual)</span>
                </button>
              </div>
            </div>
          </div>

          {/* SAVED HOROSCOPES SELECTOR */}
          {inputMode === "saved" && (
            <div className="mb-5 space-y-3 bg-amber-50/50 border border-amber-200/70 p-4 rounded-xl">
              <div className="flex flex-col sm:flex-row gap-3">
                <div className="relative flex-1">
                  <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={savedSearchQuery}
                    onChange={(e) => setSavedSearchQuery(e.target.value)}
                    placeholder="பெயர், பிறந்த தேதி அல்லது ஊர் மூலம் தேடுங்கள் (Search saved charts by name, date or place)..."
                    className="w-full text-xs sm:text-sm pl-9 pr-8 py-2 bg-white border border-amber-300 rounded-lg focus:ring-2 focus:ring-[#B4872B] focus:border-transparent outline-none"
                  />
                  {savedSearchQuery && (
                    <button
                      onClick={() => setSavedSearchQuery("")}
                      className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                <div className="sm:w-80">
                  <select
                    className="w-full text-xs sm:text-sm bg-white border border-amber-300 rounded-lg px-3 py-2 text-gray-800 font-medium focus:ring-2 focus:ring-[#B4872B] outline-none"
                    value={selectedSavedId || ""}
                    onChange={(e) => {
                      const found = savedProfiles.find((p) => (p.id || p.name) === e.target.value);
                      if (found) handleLoadProfile(found);
                    }}
                  >
                    <option value="" disabled>
                      {filteredSavedProfiles.length === 0
                        ? "-- பொருந்தும் ஜாதகங்கள் இல்லை --"
                        : `-- ஜாதகரைத் தேர்ந்தெடுக்கவும் (${filteredSavedProfiles.length}) --`}
                    </option>
                    {filteredSavedProfiles.map((p, i) => {
                      const pName = p.person_name || p.name || `Profile #${i + 1}`;
                      const pDate = p.birth_date || "";
                      const pCity = p.birthplace || p.location_name || "";
                      return (
                        <option key={p.id || i} value={p.id || pName}>
                          {pName} {pDate ? `(${pDate})` : ""} {pCity ? `• ${pCity}` : ""}
                        </option>
                      );
                    })}
                  </select>
                </div>
              </div>

              {selectedSavedId && (
                <div className="flex flex-col sm:flex-row sm:items-center justify-between pt-2 border-t border-amber-200/60 gap-3">
                  <div className="flex items-center gap-2 text-xs text-amber-900 font-medium">
                    <Check className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                    <span>
                      தேர்ந்தெடுக்கப்பட்ட ஜாதகர்: <strong className="font-bold text-[#153F6B]">{name}</strong> (பிறப்பு: {birthDate} {birthTime}, {selectedCity})
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        setShowChartViewer(!showChartViewer);
                        if (!chartData) ensureChartData();
                      }}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-indigo-300 bg-indigo-50 hover:bg-indigo-100 text-indigo-900 text-xs font-bold transition cursor-pointer"
                    >
                      <Compass className="w-3.5 h-3.5 text-indigo-600" />
                      <span>{showChartViewer ? "கட்டத்தை மறை (Hide Chart)" : "ஜாதகக் கட்டம் பார் (View Natal Chart)"}</span>
                    </button>

                    <Link
                      href={`/horoscope/results?id=${selectedSavedId}`}
                      target="_blank"
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-gray-300 bg-white hover:bg-gray-50 text-gray-800 text-xs font-semibold transition"
                    >
                      <ExternalLink className="w-3.5 h-3.5 text-gray-600" />
                      <span>முழு ஜாதகம் (Results Page)</span>
                    </Link>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* FORM FIELDS (Editable in both Saved and Manual modes) */}
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

            <div className="flex items-center gap-3 w-full sm:w-auto">
              <button
                type="button"
                onClick={() => {
                  setShowChartViewer(!showChartViewer);
                  if (!chartData) ensureChartData();
                }}
                className="px-4 py-3 bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold rounded-xl border border-slate-300 transition-all flex items-center justify-center gap-1.5 text-xs sm:text-sm cursor-pointer"
                title="இராசி மற்றும் நவாம்ச கட்டத்தைப் பார்க்க"
              >
                <Compass className="w-4 h-4 text-indigo-600" />
                <span>{showChartViewer ? "கட்டத்தை மறை" : "ஜாதகக் கட்டம்"}</span>
              </button>

              <button
                onClick={handleGenerate}
                disabled={loading}
                className="flex-1 sm:flex-initial px-8 py-3 bg-gradient-to-r from-[#B4872B] to-[#996f21] hover:from-[#996f21] hover:to-[#7f5a18] text-white font-bold rounded-xl shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 text-sm disabled:opacity-60 cursor-pointer"
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
          </div>

          {error && (
            <div className="mt-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* =========================================================================
            ASTROLOGICAL NATAL CHART VIEWER (ராசி & நவாம்ச கட்ட நேரடி பார்வை)
           ========================================================================= */}
        {showChartViewer && (
          <div className="bg-white rounded-2xl shadow-xl border-2 border-indigo-200 overflow-hidden mb-8 transition-all print:hidden">
            <div className="bg-gradient-to-r from-indigo-900 via-indigo-800 to-slate-900 text-white px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-indigo-500/20 rounded-xl border border-indigo-400/30">
                  <Compass className="w-6 h-6 text-indigo-300" />
                </div>
                <div>
                  <span className="text-[11px] font-bold text-indigo-300 uppercase tracking-widest block">
                    Natal Chart Viewer • ஜாதகக் கட்ட நேரடி பார்வை
                  </span>
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <span>{name} - இராசி & நவாம்ச கட்டங்கள்</span>
                    {selectedSavedId && (
                      <span className="text-xs bg-indigo-500/30 text-indigo-200 px-2 py-0.5 rounded font-mono">
                        Saved #{selectedSavedId.slice(0, 8)}
                      </span>
                    )}
                  </h3>
                </div>
              </div>

              <div className="flex items-center gap-2 flex-wrap">
                {/* Sub-tabs: Rasi / Navamsa / Table */}
                <div className="inline-flex rounded-lg bg-black/30 p-1 border border-indigo-500/30 text-xs">
                  <button
                    onClick={() => setChartTab("rasi")}
                    className={`px-3 py-1 rounded-md font-medium transition ${
                      chartTab === "rasi" ? "bg-indigo-600 text-white" : "text-gray-300 hover:text-white"
                    }`}
                  >
                    இராசி (D1 Rasi)
                  </button>
                  <button
                    onClick={() => setChartTab("navamsa")}
                    className={`px-3 py-1 rounded-md font-medium transition ${
                      chartTab === "navamsa" ? "bg-indigo-600 text-white" : "text-gray-300 hover:text-white"
                    }`}
                  >
                    நவாம்சம் (D9 Navamsa)
                  </button>
                  <button
                    onClick={() => setChartTab("table")}
                    className={`px-3 py-1 rounded-md font-medium transition ${
                      chartTab === "table" ? "bg-indigo-600 text-white" : "text-gray-300 hover:text-white"
                    }`}
                  >
                    கிரக பாதசாரம் (Table)
                  </button>
                </div>

                {selectedSavedId && (
                  <Link
                    href={`/horoscope/results?id=${selectedSavedId}`}
                    target="_blank"
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-xs shadow transition"
                    title="முழுமையான 100-பக்க ஜாதகப் பக்கத்தை புதிய தத்தலில் திறக்க"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                    <span>முழு ஜாதகம்</span>
                  </Link>
                )}

                <button
                  onClick={() => setShowChartViewer(false)}
                  className="p-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-gray-300 hover:text-white transition"
                  title="கட்டத்தை மூடு"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="p-6">
              {loadingChartData ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mb-3" />
                  <p className="text-sm text-gray-600">ஜாதகக் கட்டத்தை கணித்துக் கொண்டிருக்கிறது...</p>
                </div>
              ) : chartData ? (
                <div>
                  {chartTab === "rasi" && (
                    <div className="flex flex-col items-center">
                      <div className="w-full max-w-xl">
                        <SouthIndianChart
                          horoscope={chartData}
                          centerLabel={language === "ta" ? "இராசி" : "Rasi"}
                          centerNumber="(1)"
                          isSaved={Boolean(selectedSavedId)}
                        />
                      </div>
                    </div>
                  )}

                  {chartTab === "navamsa" && (
                    <div className="flex flex-col items-center">
                      <div className="w-full max-w-xl">
                        <SouthIndianChart
                          horoscope={buildNavamsaHoroscope(chartData)}
                          centerLabel={language === "ta" ? "நவாம்சம்" : "Navamsa"}
                          centerNumber="(9)"
                          isSaved={Boolean(selectedSavedId)}
                        />
                      </div>
                    </div>
                  )}

                  {chartTab === "table" && (
                    <div className="overflow-x-auto">
                      <table className="w-full text-xs text-left border-collapse">
                        <thead>
                          <tr className="bg-slate-100 text-slate-700 border-b border-slate-200">
                            <th className="p-2.5 font-bold">கிரகம் (Graha)</th>
                            <th className="p-2.5 font-bold">இராசி (Sign)</th>
                            <th className="p-2.5 font-bold">பாகை (Longitude)</th>
                            <th className="p-2.5 font-bold">நட்சத்திரம் & பாதம் (Nakshatra)</th>
                            <th className="p-2.5 font-bold">அதிபதி (Lord)</th>
                            <th className="p-2.5 font-bold">நிலை (Status)</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                          {/* Ascendant */}
                          <tr className="bg-amber-50/40 font-semibold">
                            <td className="p-2.5 text-[#B4872B] font-bold">லக்னம் (Lagna)</td>
                            <td className="p-2.5">{chartData.ascendant.sign_name_tamil || getRasiNameTamil(chartData.ascendant.sign_name)} ({chartData.ascendant.sign_name})</td>
                            <td className="p-2.5 font-mono">{formatDms(chartData.ascendant.degree_in_sign)}</td>
                            <td className="p-2.5">{getNakshatraTamil(chartData.ascendant.nakshatra?.name)} (பாதம் {chartData.ascendant.nakshatra?.pada})</td>
                            <td className="p-2.5">{chartData.ascendant.nakshatra?.lord}</td>
                            <td className="p-2.5 text-xs text-amber-800">ஜன்ம லக்னம்</td>
                          </tr>
                          {/* Planets */}
                          {chartData.planets.map((p) => {
                            const dig = getGrahaDignity(p.name, p.sign_index);
                            return (
                              <tr key={p.name} className="hover:bg-slate-50 transition">
                                <td className="p-2.5 font-bold text-slate-800">
                                  {getPlanetNameTamil(p.name)} ({p.name})
                                </td>
                                <td className="p-2.5">{p.sign_name_tamil || getRasiNameTamil(p.sign_name)} ({p.sign_name})</td>
                                <td className="p-2.5 font-mono">{formatDms(p.degree_in_sign)}</td>
                                <td className="p-2.5">{getNakshatraTamil(p.nakshatra?.name)} (பாதம் {p.nakshatra?.pada})</td>
                                <td className="p-2.5">{p.nakshatra?.lord}</td>
                                <td className="p-2.5">
                                  <div className="flex items-center gap-1">
                                    {p.is_retrograde && (
                                      <span className="px-1.5 py-0.5 rounded text-[10px] bg-red-100 text-red-700 font-bold">
                                        வக்கிரம் (R)
                                      </span>
                                    )}
                                    {dig.isUcham && (
                                      <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-100 text-emerald-800 font-bold">
                                        உச்சம்
                                      </span>
                                    )}
                                    {dig.isNeecham && (
                                      <span className="px-1.5 py-0.5 rounded text-[10px] bg-rose-100 text-rose-800 font-bold">
                                        நீசம்
                                      </span>
                                    )}
                                    <span className="text-[11px] text-slate-600 font-medium capitalize">{dig.status}</span>
                                  </div>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <p className="text-sm">ஜாதகக் கட்ட விபரங்கள் இன்னும் கணக்கிடப்படவில்லை.</p>
                  <button
                    onClick={() => ensureChartData()}
                    className="mt-3 px-4 py-2 bg-indigo-600 text-white rounded-lg text-xs font-semibold hover:bg-indigo-700 cursor-pointer"
                  >
                    இப்போது கணக்கிடு (Compute Chart)
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

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

              <div className="flex items-center gap-2 flex-wrap">
                {/* View Natal Chart Toggle in Teleprompter */}
                <button
                  onClick={() => {
                    setShowChartViewer(!showChartViewer);
                    if (!chartData) ensureChartData();
                  }}
                  className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-medium border border-indigo-500 flex items-center gap-1.5 transition cursor-pointer"
                  title="இராசி மற்றும் நவாம்ச கட்டத்தை திற/மறை"
                >
                  <Compass className="w-3.5 h-3.5 text-indigo-200" />
                  <span>{showChartViewer ? "கட்டத்தை மறை" : "ஜாதகக் கட்டம்"}</span>
                </button>

                {selectedSavedId && (
                  <Link
                    href={`/horoscope/results?id=${selectedSavedId}`}
                    target="_blank"
                    className="px-3 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-200 text-xs font-medium border border-amber-500/40 flex items-center gap-1.5 transition"
                    title="முழுமையான ஜாதக முடிவுகள் பக்கத்தை திற"
                  >
                    <ExternalLink className="w-3.5 h-3.5 text-amber-400" />
                    <span className="hidden sm:inline">முழு ஜாதகம்</span>
                  </Link>
                )}

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
                  className="px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-200 text-xs font-medium border border-gray-700 flex items-center gap-1.5 transition cursor-pointer"
                  title="முழு வாக்கு பலனையும் நகலெடு"
                >
                  <Copy className="w-3.5 h-3.5 text-amber-400" />
                  <span>{copied ? "நகலெடுக்கப்பட்டது!" : "Copy Script"}</span>
                </button>

                <button
                  onClick={handlePrint}
                  className="px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-200 text-xs font-medium border border-gray-700 flex items-center gap-1.5 transition cursor-pointer"
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

                    {bullet.checklist && bullet.checklist.length > 0 && (
                      <div className="mt-3 p-3 rounded-xl bg-rose-50/70 border border-rose-200/80 space-y-1.5">
                        <div className="flex items-center gap-1.5 text-[11px] font-extrabold text-rose-950 uppercase tracking-wider">
                          <ShieldCheck className="w-3.5 h-3.5 text-rose-600 flex-shrink-0" />
                          திரிவித ஜாமக்கோள் சரிபார்ப்பு (3-Tier Jamakkol Verification):
                        </div>
                        <div className="space-y-1">
                          {bullet.checklist.map((item, cIdx) => (
                            <div key={cIdx} className="flex items-start gap-2 text-xs text-rose-950 leading-snug">
                              <span className="inline-block mt-0.5 px-1.5 py-0.2 rounded text-[10px] font-black bg-rose-600 text-white flex-shrink-0">
                                ✓
                              </span>
                              <span className="font-mono text-[11px]">{item.replace("[✓] ", "")}</span>
                            </div>
                          ))}
                        </div>
                      </div>
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

            {/* =========================================================================
                DEVA KERALAM (CHANDRA KALA NADI) 150 NADIAMSA & LONGEVITY PLATFORM
               ========================================================================= */}
            {data.lagna_nadiamsa_name && (
              <div className="bg-gradient-to-br from-[#1A1C29] via-[#12131C] to-[#1A1C29] text-white rounded-2xl shadow-xl border-2 border-indigo-400/60 p-6 space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-indigo-900/60 gap-3">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 bg-indigo-500/20 rounded-xl border border-indigo-400/40">
                      <Compass className="w-6 h-6 text-indigo-300" />
                    </div>
                    <div>
                      <span className="text-[11px] font-bold text-indigo-300 uppercase tracking-widest block">
                        Deva Keralam • சந்திர கலா நாடி 150 நாடியம்சம் & ஆயுள் நிர்ணயம்
                      </span>
                      <h3 className="text-xl font-bold text-white flex items-center gap-2">
                        <span>லக்ன நாடியம்சம் #{data.lagna_nadiamsa_number}: {data.lagna_nadiamsa_name_ta} ({data.lagna_nadiamsa_name})</span>
                      </h3>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs bg-indigo-500/20 text-indigo-200 border border-indigo-400/40 px-3 py-1 rounded-full font-semibold">
                      {data.lagna_nadiamsa_half_ta}
                    </span>
                    <span className="text-xs bg-amber-400/10 text-amber-300 border border-amber-400/30 px-3 py-1 rounded-full font-mono">
                      12-Minute Arc Precision
                    </span>
                  </div>
                </div>

                {/* Nadiamsa Delineation Script */}
                <div className="bg-indigo-950/40 border border-indigo-800/50 rounded-xl p-5 space-y-3">
                  <span className="text-xs font-bold text-indigo-300 uppercase tracking-wider block">
                    தேவ கேரளம் மூல நூல் வாக்கு பலன் (Nadi Delineation):
                  </span>
                  {(scriptLanguage === "ta" || scriptLanguage === "both") && (
                    <p className="text-sm sm:text-base font-serif text-gray-100 leading-relaxed bg-black/40 p-4 rounded-lg border border-indigo-900/40">
                      "{data.lagna_nadiamsa_script_ta}"
                    </p>
                  )}
                  {(scriptLanguage === "en" || scriptLanguage === "both") && (
                    <p className="text-xs sm:text-sm font-serif text-gray-300 leading-relaxed bg-black/40 p-3 rounded-lg border border-indigo-900/40">
                      "{data.lagna_nadiamsa_script_en}"
                    </p>
                  )}
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {/* Khanda Nirnaya & Longevity */}
                  <div className="bg-slate-900/80 border border-indigo-900/50 rounded-xl p-4 space-y-2">
                    <span className="text-xs font-bold text-amber-300 uppercase tracking-wide flex items-center gap-1.5">
                      <Award className="w-4 h-4 text-amber-400" />
                      கண்ட நிர்ணயம் & ஆயுள் தரம் (Longevity Assessment):
                    </span>
                    <p className="text-xs sm:text-sm text-gray-200 font-serif leading-relaxed">
                      {scriptLanguage === "en" ? data.khanda_nirnaya_longevity_en : data.khanda_nirnaya_longevity_ta}
                    </p>
                    {scriptLanguage === "both" && (
                      <p className="text-[11px] text-gray-400 italic">
                        {data.khanda_nirnaya_longevity_en}
                      </p>
                    )}
                  </div>

                  {/* Parent Critical Transit Degrees */}
                  <div className="bg-slate-900/80 border border-indigo-900/50 rounded-xl p-4 space-y-2.5">
                    <span className="text-xs font-bold text-rose-300 uppercase tracking-wide flex items-center gap-1.5">
                      <AlertTriangle className="w-4 h-4 text-rose-400" />
                      பெற்றோர் கண்ட கோச்சார பாகை (Deva Keralam Transit Criticals):
                    </span>
                    <div className="space-y-1.5 text-xs">
                      <div className="bg-black/30 p-2.5 rounded-lg border border-rose-900/30">
                        <span className="font-semibold text-rose-300 block">தந்தை கண்ட பாகை (Father Critical Degree):</span>
                        <span className="text-gray-200 font-mono text-[11px]">{data.father_critical_degree}</span>
                      </div>
                      <div className="bg-black/30 p-2.5 rounded-lg border border-rose-900/30">
                        <span className="font-semibold text-rose-300 block">தாய் கண்ட பாகை (Mother Critical Degree):</span>
                        <span className="text-gray-200 font-mono text-[11px]">{data.mother_critical_degree}</span>
                      </div>
                    </div>
                    <span className="text-[10px] text-gray-400 block italic">
                      *கோச்சார சனி இப்பாகைக்கோ அல்லது இதன் திரிகோணங்களுக்கோ வரும் காலங்களில் பெற்றோருக்கு ஆரோக்கிய கண்டங்கள் சம்பவிக்கும்.
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* =========================================================================
                BHRIGU NANDI NADI & CLASSICAL SHASTRA RULE VERIFICATION
               ========================================================================= */}
            {data.guaranteed_chart_shockers && data.guaranteed_chart_shockers.length > 0 && (
              <div className="bg-white rounded-2xl shadow-xl border-2 border-emerald-500 overflow-hidden">
                <div className="bg-gradient-to-r from-emerald-800 via-teal-800 to-emerald-950 text-white px-6 py-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 bg-emerald-500/20 rounded-xl border border-emerald-400/40">
                      <ShieldCheck className="w-7 h-7 text-emerald-300" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-[11px] font-bold text-emerald-300 uppercase tracking-widest block">
                          Bhrigu Nandi Nadi • பிருகு நந்தி நாடி சாஸ்திரக் காரக ஆய்வு
                        </span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-400 text-slate-950 animate-pulse">
                          பாகை உறுதி (VERIFIED)
                        </span>
                      </div>
                      <h3 className="text-xl font-bold text-white flex items-center gap-2">
                        <span>ஜாதகத்தில் உறுதிசெய்யப்பட்ட {data.guaranteed_chart_shockers.length} சாஸ்திரக் கூட்டமைப்புகள்</span>
                      </h3>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 flex-wrap">
                    <button
                      onClick={() => setShockerFilter("all")}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition cursor-pointer ${
                        shockerFilter === "all" ? "bg-white text-emerald-950 shadow" : "bg-emerald-900/70 text-emerald-100 hover:bg-emerald-900"
                      }`}
                    >
                      அனைத்தும் ({data.guaranteed_chart_shockers.length})
                    </button>
                    <button
                      onClick={() => setShockerFilter("EXTREME")}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition cursor-pointer ${
                        shockerFilter === "EXTREME" ? "bg-rose-500 text-white shadow" : "bg-emerald-900/70 text-emerald-100 hover:bg-emerald-900"
                      }`}
                    >
                      அதிதீவிரம் ({data.guaranteed_chart_shockers.filter(s => s.shock_factor === "EXTREME").length})
                    </button>
                    <button
                      onClick={() => setShockerFilter("HIGH")}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition cursor-pointer ${
                        shockerFilter === "HIGH" ? "bg-amber-400 text-slate-950 shadow" : "bg-emerald-900/70 text-emerald-100 hover:bg-emerald-900"
                      }`}
                    >
                      உயர் உண்மை ({data.guaranteed_chart_shockers.filter(s => s.shock_factor === "HIGH").length})
                    </button>
                  </div>
                </div>

                <div className="p-6 space-y-4">
                  <div className="bg-emerald-50 border-l-4 border-emerald-600 p-3.5 rounded-r-xl flex items-center justify-between text-xs text-emerald-950">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                      <span>
                        கீழே உள்ள பலன்கள் பிருகு நந்தி நாடி மற்றும் தேவ கேரளம் சாஸ்திர விதிகளின்படி <b>கிரகங்களின் பாகை சேர்க்கை மற்றும் நவாம்ச பலத்தை</b> அடிப்படையாகக் கொண்டு துல்லியமாக கணிக்கப்பட்டவை.
                      </span>
                    </div>
                    <span className="font-mono font-bold text-emerald-800 hidden sm:inline">
                      Strict Degree Orbs
                    </span>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {data.guaranteed_chart_shockers
                      .filter(s => shockerFilter === "all" || s.shock_factor === shockerFilter)
                      .slice(0, showAllShockers ? undefined : 8)
                      .map((shocker, i) => {
                        const isExtreme = shocker.shock_factor === "EXTREME";
                        return (
                          <div
                            key={shocker.id || i}
                            className={`rounded-xl p-5 border-2 transition-all flex flex-col justify-between hover:shadow-md ${
                              isExtreme
                                ? "bg-gradient-to-b from-rose-50/50 to-white border-rose-300"
                                : "bg-gradient-to-b from-amber-50/40 to-white border-amber-300"
                            }`}
                          >
                            <div>
                              <div className="flex items-center justify-between gap-2 mb-2.5">
                                <span
                                  className={`px-2.5 py-0.5 rounded text-[10px] font-extrabold uppercase tracking-wider ${
                                    isExtreme
                                      ? "bg-rose-600 text-white"
                                      : "bg-amber-500 text-slate-950"
                                  }`}
                                >
                                  {shocker.shock_factor} SHOCK
                                </span>

                                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-300 flex items-center gap-1">
                                  <ShieldCheck className="w-3 h-3 text-emerald-600" />
                                  சாஸ்திர காரக ஆய்வு
                                </span>
                              </div>

                              <h4 className="text-sm sm:text-base font-bold text-[#153F6B] mb-2 leading-snug">
                                {scriptLanguage === "en" ? shocker.headline_en : shocker.headline_ta}
                              </h4>

                              {(scriptLanguage === "ta" || scriptLanguage === "both") && (
                                <p className="text-sm sm:text-base font-serif text-gray-900 leading-relaxed mb-2 bg-white p-3 rounded-lg border border-gray-200 shadow-2xs">
                                  "{shocker.script_ta}"
                                </p>
                              )}

                              {(scriptLanguage === "en" || scriptLanguage === "both") && (
                                <p className="text-xs sm:text-sm font-serif text-gray-700 leading-relaxed bg-white p-2.5 rounded-lg border border-gray-200 shadow-2xs">
                                  "{shocker.script_en}"
                                </p>
                              )}
                            </div>

                            {shocker.checklist && shocker.checklist.length > 0 && (
                              <div className="mt-3 p-3 rounded-xl bg-emerald-50/70 border border-emerald-200/80 space-y-1.5">
                                <div className="flex items-center gap-1.5 text-[11px] font-extrabold text-emerald-950 uppercase tracking-wider">
                                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
                                  திரிவித சாஸ்திர சரிபார்ப்பு (3-Tier Verification Checklist):
                                </div>
                                <div className="space-y-1">
                                  {shocker.checklist.map((item, cIdx) => (
                                    <div key={cIdx} className="flex items-start gap-2 text-xs text-emerald-950 leading-snug">
                                      <span className="inline-block mt-0.5 px-1.5 py-0.2 rounded text-[10px] font-black bg-emerald-600 text-white flex-shrink-0">
                                        ✓
                                      </span>
                                      <span className="font-mono text-[11px]">{item.replace("[✓] ", "")}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            <div className="mt-3 pt-2.5 border-t border-gray-200 flex items-center gap-1.5 text-[10px] text-gray-600 font-mono">
                              <Compass className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
                              <span>சாஸ்திர நிரூபணம் (Proof): {shocker.astrological_proof}</span>
                            </div>
                          </div>
                        );
                      })}
                  </div>

                  {data.guaranteed_chart_shockers.length > 8 && (
                    <div className="text-center pt-3">
                      <button
                        onClick={() => setShowAllShockers(!showAllShockers)}
                        className="px-5 py-2 rounded-xl bg-emerald-100 hover:bg-emerald-200 text-emerald-900 text-xs font-bold transition cursor-pointer border border-emerald-300"
                      >
                        {showAllShockers
                          ? "சுருக்கமாகப் பார் (Show Less)"
                          : `அனைத்து ${data.guaranteed_chart_shockers.length} உறுதியான வாக்குகளையும் பார் (View All ${data.guaranteed_chart_shockers.length} Shockers)`}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* =========================================================================
                STRICT SHASTRIC TABOOS & BEHAVIORAL DIRECTIVES
               ========================================================================= */}
            {data.remedial_taboos_ta && data.remedial_taboos_ta.length > 0 && (
              <div className="bg-gradient-to-r from-red-950 via-rose-900 to-red-950 text-white rounded-2xl shadow-xl border-2 border-rose-400/80 p-6 space-y-4">
                <div className="flex items-center gap-3 pb-3 border-b border-rose-800/80">
                  <div className="p-2.5 bg-rose-500/20 rounded-xl border border-rose-400/40">
                    <ShieldAlert className="w-6 h-6 text-rose-300 animate-pulse" />
                  </div>
                  <div>
                    <span className="text-[11px] font-bold text-rose-300 uppercase tracking-widest block">
                      Strict Shastric Taboos • சாஸ்திர கடுமையான விலக்குகள்
                    </span>
                    <h3 className="text-lg font-bold text-white">
                      ஜாதகர் வாழ்நாளில் செய்யக்கூடாத கடுமையான கட்டளைகள் (Do Not Violate)
                    </h3>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs sm:text-sm">
                  {data.remedial_taboos_ta.map((taboo, idx) => (
                    <div key={idx} className="bg-black/40 border border-rose-700/60 p-3.5 rounded-xl flex items-start gap-2.5">
                      <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
                      <div className="space-y-1">
                        <p className="text-rose-100 font-medium leading-relaxed">{taboo}</p>
                        {scriptLanguage === "both" && data.remedial_taboos_en[idx] && (
                          <p className="text-rose-300/80 text-xs italic">{data.remedial_taboos_en[idx]}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* THE 5 SHOCK AMPLIFIERS (5 துல்லிய உச்சக்கட்ட உண்மைகள்) */}
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
                                ? "bg-emerald-700 text-white"
                                : "bg-amber-600 text-white"
                            }`}
                          >
                            {win.status === "RED_ALERT"
                              ? "சிவப்பு எச்சரிக்கை (RED ALERT)"
                              : win.status === "GOLDEN_BREAKTHROUGH"
                              ? "பொற்காலம் (GOLDEN BREAKTHROUGH)"
                              : "தயாரிப்பு காலம் (PREPARATION)"}
                          </span>
                          <span className="text-xs text-gray-600 font-mono font-medium">
                            {win.start_date} முதல் {win.end_date} வரை
                          </span>
                        </div>

                        <span className="text-xs font-bold text-gray-800">
                          {scriptLanguage === "en" ? win.title_en : win.title_ta}
                        </span>
                      </div>

                      {(scriptLanguage === "ta" || scriptLanguage === "both") && (
                        <p className="text-sm sm:text-base font-serif text-gray-900 leading-relaxed mb-3 bg-white p-3 rounded-lg border border-gray-200">
                          "{win.script_ta}"
                        </p>
                      )}

                      {(scriptLanguage === "en" || scriptLanguage === "both") && (
                        <p className="text-xs sm:text-sm font-serif text-gray-700 leading-relaxed bg-white p-3 rounded-lg border border-gray-200 mb-3">
                          "{win.script_en}"
                        </p>
                      )}

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 text-xs">
                        <div className="bg-emerald-50/80 p-3 rounded-lg border border-emerald-200">
                          <span className="font-bold text-emerald-900 flex items-center gap-1.5 mb-1.5">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                            செய்ய வேண்டியவை (Do's):
                          </span>
                          <ul className="list-disc list-inside space-y-1 text-emerald-950">
                            {(scriptLanguage === "en" ? win.do_rules_en : win.do_rules_ta).map((r, i) => (
                              <li key={i}>{r}</li>
                            ))}
                          </ul>
                        </div>

                        <div className="bg-rose-50/80 p-3 rounded-lg border border-rose-200">
                          <span className="font-bold text-rose-900 flex items-center gap-1.5 mb-1.5">
                            <AlertCircle className="w-3.5 h-3.5 text-rose-600" />
                            தவிர்க்க வேண்டியவை (Don'ts / Hazards):
                          </span>
                          <ul className="list-disc list-inside space-y-1 text-rose-950">
                            {(scriptLanguage === "en" ? win.dont_rules_en : win.dont_rules_ta).map((r, i) => (
                              <li key={i}>{r}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* CARD 5: 🛡️ TURN-KEY ACTIONABLE REMEDY */}
            <div className="bg-white rounded-2xl shadow-md border-2 border-amber-400 overflow-hidden">
              <div className="bg-gradient-to-r from-amber-600 to-amber-700 text-white px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-white/10 rounded-lg">
                    <ShieldCheck className="w-6 h-6 text-amber-100" />
                  </div>
                  <div>
                    <span className="text-[11px] font-semibold text-amber-100 tracking-wider uppercase block">
                      Pillar 5 • Actionable Remedy
                    </span>
                    <h3 className="text-lg font-bold">5. உடனடி நிவர்த்தி & எளிய பரிகாரம் (1 ஆலயம் • 1 தானம் • 1 மணி)</h3>
                  </div>
                </div>

                <span className="text-xs bg-amber-900/60 text-amber-100 border border-amber-300/30 px-3 py-1 rounded-full font-medium">
                  செலவில்லாத நேரடி கர்மா நிவர்த்தி
                </span>
              </div>

              <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-5">
                <div className="bg-amber-50/60 border border-amber-200 rounded-xl p-4 flex flex-col justify-between">
                  <div>
                    <span className="text-xs font-bold text-[#8B6914] uppercase tracking-wide block mb-1">
                      1. செல்ல வேண்டிய பரிகார ஸ்தலம்
                    </span>
                    <p className="text-sm font-bold text-gray-900 mb-2">
                      {scriptLanguage === "en" ? data.temple_recommendation_en : data.temple_recommendation_ta}
                    </p>
                    {scriptLanguage === "both" && (
                      <p className="text-xs text-gray-600 italic">
                        {data.temple_recommendation_en}
                      </p>
                    )}
                  </div>
                  <span className="text-[10px] text-amber-700 font-medium mt-3 block">
                    ஆரூடம் மற்றும் லக்னாதிபதியின் சாப நிவர்த்தி ஸ்தலம்
                  </span>
                </div>

                <div className="bg-emerald-50/60 border border-emerald-200 rounded-xl p-4 flex flex-col justify-between">
                  <div>
                    <span className="text-xs font-bold text-emerald-800 uppercase tracking-wide block mb-1">
                      2. வாராந்திர கர்மா தானம்
                    </span>
                    <p className="text-sm font-bold text-gray-900 mb-2">
                      {scriptLanguage === "en" ? data.daily_karma_action_en : data.daily_karma_action_ta}
                    </p>
                    {scriptLanguage === "both" && (
                      <p className="text-xs text-gray-600 italic">
                        {data.daily_karma_action_en}
                      </p>
                    )}
                  </div>
                  <span className="text-[10px] text-emerald-700 font-medium mt-3 block">
                    தசா நாதனின் கர்ம வினையை நீக்கும் ஜீவ காருண்யம்
                  </span>
                </div>

                <div className="bg-purple-50/60 border border-purple-200 rounded-xl p-4 flex flex-col justify-between">
                  <div>
                    <span className="text-xs font-bold text-purple-800 uppercase tracking-wide block mb-1">
                      3. நவரத்தினம் அல்லது ருத்ராட்சம்
                    </span>
                    <p className="text-sm font-bold text-gray-900 mb-2">
                      {scriptLanguage === "en" ? data.gem_or_rudraksha_en : data.gem_or_rudraksha_ta}
                    </p>
                    {scriptLanguage === "both" && (
                      <p className="text-xs text-gray-600 italic">
                        {data.gem_or_rudraksha_en}
                      </p>
                    )}
                  </div>
                  <span className="text-[10px] text-purple-700 font-medium mt-3 block">
                    உடல் காந்த அலைவரிசையை பலப்படுத்தும் தாரணை
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function InstantRevelationPage() {
  return (
    <React.Suspense
      fallback={
        <div className="min-h-screen bg-[#FDFBF7] flex items-center justify-center">
          <div className="w-8 h-8 border-4 border-[#B4872B] border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <InstantRevelationContent />
    </React.Suspense>
  );
}
