"use client";

import React, { useState, useEffect, useRef } from "react";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { getOccasions, findMuhurtas, saveMuhurtaSelection } from "@/lib/api";
import { searchLocations, LocationSearchResult } from "@/lib/geocoding";
import {
  OccasionItem,
  CandidateSlot,
  FindMuhurtaResponse,
  SaveMuhurtaRequest,
} from "@/lib/types";
import { MuhurtaReportModal } from "./MuhurtaReportModal";
import {
  Search,
  Sparkles,
  Calendar,
  Clock,
  MapPin,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  ShieldCheck,
  Bookmark,
  Printer,
  ChevronDown,
  Layers,
  Heart,
  Home,
  Briefcase,
  Car,
  GraduationCap,
  Sparkle,
  Sliders,
  Filter,
  Check,
} from "lucide-react";

const NAKSHATRAS_LIST = [
  { id: 1, en: "Ashwini", ta: "அசுவினி" },
  { id: 2, en: "Bharani", ta: "பரணி" },
  { id: 3, en: "Krittika", ta: "கிருத்திகை" },
  { id: 4, en: "Rohini", ta: "ரோகிணி" },
  { id: 5, en: "Mrigashira", ta: "மிருகசீரிஷம்" },
  { id: 6, en: "Ardra", ta: "திருவாதிரை" },
  { id: 7, en: "Punarvasu", ta: "புனர்பூசம்" },
  { id: 8, en: "Pushya", ta: "பூசம்" },
  { id: 9, en: "Ashlesha", ta: "ஆயில்யம்" },
  { id: 10, en: "Magha", ta: "மகம்" },
  { id: 11, en: "Purva Phalguni", ta: "பூரம்" },
  { id: 12, en: "Uttara Phalguni", ta: "உத்திரம்" },
  { id: 13, en: "Hasta", ta: "ஹஸ்தம்" },
  { id: 14, en: "Chitra", ta: "சித்திரை" },
  { id: 15, en: "Swati", ta: "சுவாதி" },
  { id: 16, en: "Vishakha", ta: "விசாகம்" },
  { id: 17, en: "Anuradha", ta: "அனுஷம்" },
  { id: 18, en: "Jyeshtha", ta: "கேட்டை" },
  { id: 19, en: "Mula", ta: "மூலம்" },
  { id: 20, en: "Purva Ashadha", ta: "பூராடம்" },
  { id: 21, en: "Uttara Ashadha", ta: "உத்திராடம்" },
  { id: 22, en: "Shravana", ta: "திருவோணம்" },
  { id: 23, en: "Dhanishta", ta: "அவிட்டம்" },
  { id: 24, en: "Shatabhisha", ta: "சதயம்" },
  { id: 25, en: "Purva Bhadrapada", ta: "பூரட்டாதி" },
  { id: 26, en: "Uttara Bhadrapada", ta: "உத்திரட்டாதி" },
  { id: 27, en: "Revati", ta: "ரேவதி" },
];

const RASHIS_LIST = [
  { id: 1, en: "Mesha (Aries)", ta: "மேஷம்" },
  { id: 2, en: "Vrishabha (Taurus)", ta: "ரிஷபம்" },
  { id: 3, en: "Mithuna (Gemini)", ta: "மிதுனம்" },
  { id: 4, en: "Karka (Cancer)", ta: "கடகம்" },
  { id: 5, en: "Simha (Leo)", ta: "சிம்மம்" },
  { id: 6, en: "Kanya (Virgo)", ta: "கன்னி" },
  { id: 7, en: "Tula (Libra)", ta: "துலாம்" },
  { id: 8, en: "Vrishchika (Scorpio)", ta: "விருச்சிகம்" },
  { id: 9, en: "Dhanus (Sagittarius)", ta: "தனுசு" },
  { id: 10, en: "Makara (Capricorn)", ta: "மகரம்" },
  { id: 11, en: "Kumbha (Aquarius)", ta: "கும்பம்" },
  { id: 12, en: "Meena (Pisces)", ta: "மீனம்" },
];

export function FindAuspiciousDates() {
  const { language } = useLanguage();
  const { session } = useAuth();

  // Occasions Catalog
  const [occasions, setOccasions] = useState<OccasionItem[]>([]);
  const [selectedOccasion, setSelectedOccasion] = useState<string>("marriage");
  const [activeCategory, setActiveCategory] = useState<string>("all");

  // Date Range (default next 14 days)
  const [startDate, setStartDate] = useState<string>(() => {
    return new Date().toISOString().split("T")[0];
  });
  const [endDate, setEndDate] = useState<string>(() => {
    const d = new Date();
    d.setDate(d.getDate() + 14);
    return d.toISOString().split("T")[0];
  });

  // Location
  const [cityName, setCityName] = useState("Chennai, Tamil Nadu, India");
  const [latitude, setLatitude] = useState(13.0827);
  const [longitude, setLongitude] = useState(80.2707);
  const [timezoneStr, setTimezoneStr] = useState("Asia/Kolkata");
  const [locationQuery, setLocationQuery] = useState("");
  const [locationResults, setLocationResults] = useState<LocationSearchResult[]>([]);
  const [showLocationDropdown, setShowLocationDropdown] = useState(false);
  const [isSearchingLocation, setIsSearchingLocation] = useState(false);

  // Time Window Preference
  const [timeRange, setTimeRange] = useState<string>("all_day");

  // Optional Birth Details
  const [showBirthDetails, setShowBirthDetails] = useState(false);
  const [groomStar, setGroomStar] = useState<number | "">("");
  const [groomRashi, setGroomRashi] = useState<number | "">("");
  const [brideStar, setBrideStar] = useState<number | "">("");
  const [brideRashi, setBrideRashi] = useState<number | "">("");
  const [nativeStar, setNativeStar] = useState<number | "">("");
  const [nativeRashi, setNativeRashi] = useState<number | "">("");

  // Tradition & Ayanamsa
  const [ayanamsaId, setAyanamsaId] = useState<number>(0); // 0 = Lahiri
  const [tradition, setTradition] = useState<string>("south_indian");

  // Results State
  const [searchResponse, setSearchResponse] = useState<FindMuhurtaResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>("all");

  // Save State
  const [savingId, setSavingId] = useState<string | null>(null);
  const [savedSuccessMap, setSavedSuccessMap] = useState<Record<string, number>>({});
  const [saveNotes, setSaveNotes] = useState<string>("");
  const [saveClientName, setSaveClientName] = useState<string>("");
  const [candidateToSave, setCandidateToSave] = useState<CandidateSlot | null>(null);

  // Report Modal State
  const [reportCandidate, setReportCandidate] = useState<any | null>(null);
  const [isReportOpen, setIsReportOpen] = useState(false);

  // Load occasions on mount
  useEffect(() => {
    getOccasions()
      .then((data) => {
        if (data && data.occasions) {
          setOccasions(data.occasions);
        }
      })
      .catch((err) => console.error("Failed to load occasions:", err));
  }, []);

  // Handle location search debounced
  useEffect(() => {
    if (!locationQuery.trim() || locationQuery.length < 2) {
      setLocationResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      setIsSearchingLocation(true);
      try {
        const results = await searchLocations(locationQuery);
        setLocationResults(results);
      } catch (e) {
        console.error(e);
      } finally {
        setIsSearchingLocation(false);
      }
    }, 350);
    return () => clearTimeout(timer);
  }, [locationQuery]);

  // Execute Search
  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError(null);

    // Build birth details object if provided
    let birthDetails: Record<string, any> | undefined = undefined;
    if (selectedOccasion === "marriage" || selectedOccasion.includes("marriage") || selectedOccasion === "engagement") {
      if (groomStar || groomRashi || brideStar || brideRashi) {
        birthDetails = {
          groom_nakshatra: groomStar ? Number(groomStar) : undefined,
          groom_moon_sign: groomRashi ? Number(groomRashi) : undefined,
          bride_nakshatra: brideStar ? Number(brideStar) : undefined,
          bride_moon_sign: brideRashi ? Number(brideRashi) : undefined,
        };
      }
    } else {
      if (nativeStar || nativeRashi) {
        birthDetails = {
          nakshatra: nativeStar ? Number(nativeStar) : undefined,
          moon_sign: nativeRashi ? Number(nativeRashi) : undefined,
        };
      }
    }

    try {
      const res = await findMuhurtas({
        occasion_code: selectedOccasion,
        start_date: startDate,
        end_date: endDate,
        latitude,
        longitude,
        location_name: cityName,
        timezone: timezoneStr,
        preferred_time_range: timeRange,
        ayanamsa_id: ayanamsaId,
        tradition,
        birth_details: birthDetails,
        limit: 100,
      });
      setSearchResponse(res);
    } catch (err: any) {
      setError(err?.message || "Failed to calculate auspicious Muhurtas.");
    } finally {
      setLoading(false);
    }
  };

  // Trigger Save Selection
  const handleConfirmSave = async () => {
    if (!candidateToSave) return;
    const token = session?.access_token || "cookie";
    setSavingId(candidateToSave.id);
    try {
      const payload: SaveMuhurtaRequest = {
        title: `${searchResponse?.occasion.name_en || "Muhurta"} - ${candidateToSave.event_date}`,
        occasion_code: selectedOccasion,
        occasion_name: searchResponse?.occasion.name_en || selectedOccasion,
        event_date: candidateToSave.event_date,
        start_time: candidateToSave.start_time_utc,
        end_time: candidateToSave.end_time_utc,
        local_start_time: candidateToSave.start_time_local,
        local_end_time: candidateToSave.end_time_local,
        duration_minutes: candidateToSave.duration_minutes,
        location_name: cityName,
        latitude,
        longitude,
        timezone: timezoneStr,
        ayanamsa_id: ayanamsaId,
        tradition,
        score: candidateToSave.score,
        status: candidateToSave.status,
        panchang_summary: {
          tithi: candidateToSave.tithi,
          nakshatra: candidateToSave.nakshatra,
          yoga: candidateToSave.yoga,
          karana: candidateToSave.karana,
          weekday: candidateToSave.weekday,
        },
        lagna_summary: candidateToSave.ascendant,
        rule_evaluations: {
          passed: candidateToSave.passed_rules,
          failed: candidateToSave.failed_rules,
          advisories: candidateToSave.advisories,
          incomplete: candidateToSave.incomplete_checks,
          explanation: candidateToSave.explanation,
        },
        notes: saveNotes || undefined,
        client_name: saveClientName || undefined,
      };

      const result = await saveMuhurtaSelection(token, payload);
      setSavedSuccessMap((prev) => ({
        ...prev,
        [candidateToSave.id]: result.record.display_number,
      }));
      setCandidateToSave(null);
      setSaveNotes("");
      setSaveClientName("");
    } catch (err: any) {
      alert(`Save failed: ${err?.message || "Ensure you are logged in."}`);
    } finally {
      setSavingId(null);
    }
  };

  // Open Report Modal
  const openReportForCandidate = (cand: CandidateSlot) => {
    const report = {
      title: `${searchResponse?.occasion.name_en || "Muhurta"} Certificate`,
      occasion_name: searchResponse?.occasion.name_en || selectedOccasion,
      client_name: saveClientName || null,
      event_date: cand.event_date,
      start_time_local: cand.start_time_local,
      end_time_local: cand.end_time_local,
      duration_minutes: cand.duration_minutes,
      location_name: cityName,
      latitude,
      longitude,
      timezone: timezoneStr,
      score: cand.score,
      status: cand.status,
      explanation: cand.explanation,
      tithi: cand.tithi,
      nakshatra: cand.nakshatra,
      yoga: cand.yoga,
      karana: cand.karana,
      ascendant: cand.ascendant,
      planets: cand.planets,
      inauspicious_periods: cand.inauspicious_periods,
      auspicious_periods: cand.auspicious_periods,
      passed_rules: cand.passed_rules,
      failed_rules: cand.failed_rules,
      advisories: cand.advisories,
      incomplete_checks: cand.incomplete_checks,
    };
    setReportCandidate(report);
    setIsReportOpen(true);
  };

  // Filter candidates
  const filteredCandidates = searchResponse?.candidates.filter((c) => {
    if (statusFilter === "all") return true;
    if (statusFilter === "auspicious") return c.status === "meets_configured_rules";
    if (statusFilter === "advisory") return c.status === "meets_rules_with_advisories";
    if (statusFilter === "restricted") return c.status === "fails_mandatory_rules";
    return true;
  });

  const isMarriageOccasion =
    selectedOccasion === "marriage" ||
    selectedOccasion.includes("marriage") ||
    selectedOccasion === "engagement";

  return (
    <div className="space-y-8">
      {/* Search Header Banner */}
      <div className="bg-gradient-to-r from-[#201538] via-[#2F1E4E] to-[#1F1735] text-white p-6 sm:p-8 rounded-3xl shadow-xl border border-amber-500/20 relative overflow-hidden">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-amber-400/20 text-amber-300 border border-amber-400/30 mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            <span>
              {language === "ta" ? "சுவிஸ் எபிமெரிஸ் கணிதம்" : "Swiss Ephemeris Vedic Precision"}
            </span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            {language === "ta"
              ? "சுப முகூர்த்த நேரம் கண்டறியுங்கள்"
              : "Find Auspicious Muhurta Windows"}
          </h2>
          <p className="mt-2 text-sm sm:text-base text-purple-200/90 leading-relaxed">
            {language === "ta"
              ? "பாரம்பரிய ஜோதிட விதிகளின்படி ராகு காலம், எமகண்டம், வர்ஜியம் தவிர்ந்து, தாரா பலம் மற்றும் சுப லக்ன சுத்தியுடன் கூடிய துல்லியமான முகூர்த்தங்களைத் தேர்வு செய்யுங்கள்."
              : "Search and rank exact auspicious time windows for weddings, housewarmings, business launches, and life ceremonies with classical Panchanga and Lagna Shuddhi."}
          </p>
        </div>
      </div>

      {/* Main Search Form Card */}
      <div className="bg-white rounded-3xl shadow-md border border-slate-200 p-6 sm:p-8 space-y-6">
        <form onSubmit={handleSearch} className="space-y-6">
          {/* 1. Occasion Selector */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <label className="text-sm font-bold text-slate-800 flex items-center gap-2">
                <Sparkle className="w-4 h-4 text-amber-600" />
                {language === "ta" ? "நிகழ்வு வகை (Occasion)" : "Select Occasion"}
              </label>
              <div className="flex gap-1 overflow-x-auto text-xs">
                {["all", "marriage_relationships", "home_property", "business_professional", "family_ceremonies"].map((cat) => (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => setActiveCategory(cat)}
                    className={`px-2.5 py-1 rounded-lg font-medium transition-colors ${
                      activeCategory === cat
                        ? "bg-purple-100 text-purple-900 font-semibold"
                        : "text-slate-600 hover:bg-slate-100"
                    }`}
                  >
                    {cat === "all"
                      ? language === "ta" ? "அனைத்தும்" : "All"
                      : cat === "marriage_relationships"
                      ? language === "ta" ? "திருமணம்" : "Marriage"
                      : cat === "home_property"
                      ? language === "ta" ? "மனை/வீடு" : "Property"
                      : cat === "business_professional"
                      ? language === "ta" ? "தொழில்" : "Business"
                      : language === "ta" ? "குடும்பம்" : "Family"}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2.5">
              {occasions
                .filter((o) => activeCategory === "all" || o.category === activeCategory)
                .map((occ) => {
                  const isSelected = selectedOccasion === occ.code;
                  return (
                    <button
                      key={occ.code}
                      type="button"
                      onClick={() => setSelectedOccasion(occ.code)}
                      className={`p-3 rounded-2xl border text-left flex flex-col justify-between transition-all ${
                        isSelected
                          ? "border-amber-500 bg-amber-50/70 shadow-sm ring-2 ring-amber-500/20"
                          : "border-slate-200 hover:border-slate-300 hover:bg-slate-50/60"
                      }`}
                    >
                      <div>
                        <div className="text-xs font-semibold text-slate-900 truncate">
                          {occ.name_en}
                        </div>
                        <div className="text-[11px] text-amber-700 font-tamil truncate mt-0.5">
                          {occ.name_ta}
                        </div>
                      </div>
                      {isSelected && (
                        <div className="mt-2 flex items-center justify-end text-amber-600">
                          <Check className="w-3.5 h-3.5" />
                        </div>
                      )}
                    </button>
                  );
                })}
            </div>
          </div>

          {/* 2. Date Range & Location Row */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-5 pt-2 border-t border-slate-100">
            {/* Start Date */}
            <div className="md:col-span-3">
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                {language === "ta" ? "தொடக்கத் தேதி" : "Search Start Date"}
              </label>
              <div className="relative">
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-amber-500 focus:border-amber-500 text-slate-800"
                  required
                />
              </div>
            </div>

            {/* End Date */}
            <div className="md:col-span-3">
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                {language === "ta" ? "முடிவுத் தேதி" : "Search End Date"}
              </label>
              <div className="relative">
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-amber-500 focus:border-amber-500 text-slate-800"
                  required
                />
              </div>
            </div>

            {/* Location Search */}
            <div className="md:col-span-6 relative">
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                {language === "ta" ? "நிகழ்வு இடம் (Event Location)" : "Event Location (Default: Chennai)"}
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <MapPin className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  value={locationQuery || cityName}
                  onChange={(e) => {
                    setLocationQuery(e.target.value);
                    setShowLocationDropdown(true);
                  }}
                  onFocus={() => {
                    if (locationResults.length > 0) setShowLocationDropdown(true);
                  }}
                  placeholder="Search city (e.g. Madurai, Coimbatore, Bangalore, Singapore)"
                  className="w-full pl-9 pr-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-amber-500 focus:border-amber-500 text-slate-800"
                />
              </div>

              {/* Location Results Dropdown */}
              {showLocationDropdown && locationResults.length > 0 && (
                <div className="absolute z-30 left-0 right-0 mt-1 bg-white border border-slate-200 rounded-xl shadow-xl max-h-56 overflow-y-auto">
                  {locationResults.map((loc, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => {
                        setCityName(loc.displayName);
                        setLatitude(loc.latitude);
                        setLongitude(loc.longitude);
                        if (loc.estimatedTimezone) setTimezoneStr(loc.estimatedTimezone);
                        setLocationQuery("");
                        setShowLocationDropdown(false);
                      }}
                      className="w-full text-left px-4 py-2.5 hover:bg-amber-50/80 border-b border-slate-100 last:border-0 flex items-center justify-between text-xs"
                    >
                      <div>
                        <div className="font-semibold text-slate-900">{loc.shortName}</div>
                        <div className="text-[11px] text-slate-500 truncate max-w-sm">{loc.displayName}</div>
                      </div>
                      <div className="text-[11px] text-amber-700 font-mono">
                        {loc.latitude.toFixed(2)}°, {loc.longitude.toFixed(2)}°
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* 3. Preferred Time Window & Tradition */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 pt-2 border-t border-slate-100">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                {language === "ta" ? "விருப்பமான நேரம்" : "Preferred Time of Day"}
              </label>
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:ring-2 focus:ring-amber-500"
              >
                <option value="all_day">{language === "ta" ? "முழு நாள் (All Day)" : "All Day (06:00 - 21:00)"}</option>
                <option value="morning">{language === "ta" ? "காலை (Morning 06:00 - 12:00)" : "Morning (06:00 - 12:00)"}</option>
                <option value="afternoon">{language === "ta" ? "மதியம் (Afternoon 12:00 - 18:00)" : "Afternoon (12:00 - 18:00)"}</option>
                <option value="evening">{language === "ta" ? "மாலை (Evening 18:00 - 22:00)" : "Evening (18:00 - 22:00)"}</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                {language === "ta" ? "அயனாம்சம் (Ayanamsa)" : "Ayanamsa Convention"}
              </label>
              <select
                value={ayanamsaId}
                onChange={(e) => setAyanamsaId(Number(e.target.value))}
                className="w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:ring-2 focus:ring-amber-500"
              >
                <option value={0}>Lahiri / Chitra Paksha (Standard)</option>
                <option value={1}>Krishnamurti Paddhati (KP)</option>
                <option value={2}>Raman Ayanamsa</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                {language === "ta" ? "பாரம்பரிய முறை" : "Regional Rule Profile"}
              </label>
              <select
                value={tradition}
                onChange={(e) => setTradition(e.target.value)}
                className="w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:ring-2 focus:ring-amber-500"
              >
                <option value="south_indian">South Indian / Tamil Classical</option>
                <option value="north_indian">North Indian Classical</option>
                <option value="kp_astrology">KP System Muhurta</option>
              </select>
            </div>
          </div>

          {/* 4. Optional Birth Details Collapsible */}
          <div className="pt-2 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setShowBirthDetails(!showBirthDetails)}
              className="inline-flex items-center gap-2 text-xs font-semibold text-purple-700 hover:text-purple-900 transition-colors"
            >
              <Sliders className="w-4 h-4" />
              <span>
                {showBirthDetails
                  ? language === "ta"
                    ? "பிறப்பு நட்சத்திர விவரங்களை மறை"
                    : "Hide Optional Birth Details"
                  : language === "ta"
                  ? "+ தாரா பலம் / சந்திர பலத்திற்கு பிறப்பு விவரங்களைச் சேர் (விருப்பத்தேர்வு)"
                  : "+ Add Optional Birth Stars for Tara Bala & Chandra Bala"}
              </span>
              <ChevronDown className={`w-3.5 h-3.5 transition-transform ${showBirthDetails ? "rotate-180" : ""}`} />
            </button>

            {showBirthDetails && (
              <div className="mt-4 p-4 rounded-2xl bg-purple-50/60 border border-purple-100 space-y-4">
                <p className="text-xs text-purple-900/80">
                  {language === "ta"
                    ? "குறிப்பு: பிறப்பு விவரங்கள் தரப்படாவிட்டால், தனிநபர் தாரா பலம் மற்றும் சந்திர பலம் சோதனைகள் தவிர்க்கப்பட்டு பொதுவான சுப நேரம் கணக்கிடப்படும்."
                    : "Notice: If birth details are omitted, personal Tara Bala and Chandra Bala compatibility will be marked as incomplete while evaluating universal classical rules."}
                </p>

                {isMarriageOccasion ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div>
                      <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                        {language === "ta" ? "மணமகன் நட்சத்திரம்" : "Groom's Nakshatra"}
                      </label>
                      <select
                        value={groomStar}
                        onChange={(e) => setGroomStar(e.target.value ? Number(e.target.value) : "")}
                        className="w-full px-2.5 py-1.5 text-xs bg-white border border-slate-200 rounded-lg text-slate-800"
                      >
                        <option value="">-- None / Unknown --</option>
                        {NAKSHATRAS_LIST.map((n) => (
                          <option key={n.id} value={n.id}>
                            {n.id}. {n.en} ({n.ta})
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                        {language === "ta" ? "மணமகன் ராசி" : "Groom's Moon Sign"}
                      </label>
                      <select
                        value={groomRashi}
                        onChange={(e) => setGroomRashi(e.target.value ? Number(e.target.value) : "")}
                        className="w-full px-2.5 py-1.5 text-xs bg-white border border-slate-200 rounded-lg text-slate-800"
                      >
                        <option value="">-- None / Unknown --</option>
                        {RASHIS_LIST.map((r) => (
                          <option key={r.id} value={r.id}>
                            {r.id}. {r.en} ({r.ta})
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                        {language === "ta" ? "மணமகள் நட்சத்திரம்" : "Bride's Nakshatra"}
                      </label>
                      <select
                        value={brideStar}
                        onChange={(e) => setBrideStar(e.target.value ? Number(e.target.value) : "")}
                        className="w-full px-2.5 py-1.5 text-xs bg-white border border-slate-200 rounded-lg text-slate-800"
                      >
                        <option value="">-- None / Unknown --</option>
                        {NAKSHATRAS_LIST.map((n) => (
                          <option key={n.id} value={n.id}>
                            {n.id}. {n.en} ({n.ta})
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                        {language === "ta" ? "மணமகள் ராசி" : "Bride's Moon Sign"}
                      </label>
                      <select
                        value={brideRashi}
                        onChange={(e) => setBrideRashi(e.target.value ? Number(e.target.value) : "")}
                        className="w-full px-2.5 py-1.5 text-xs bg-white border border-slate-200 rounded-lg text-slate-800"
                      >
                        <option value="">-- None / Unknown --</option>
                        {RASHIS_LIST.map((r) => (
                          <option key={r.id} value={r.id}>
                            {r.id}. {r.en} ({r.ta})
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                        {language === "ta" ? "பிறந்த நட்சத்திரம்" : "Native's Nakshatra"}
                      </label>
                      <select
                        value={nativeStar}
                        onChange={(e) => setNativeStar(e.target.value ? Number(e.target.value) : "")}
                        className="w-full px-2.5 py-1.5 text-xs bg-white border border-slate-200 rounded-lg text-slate-800"
                      >
                        <option value="">-- None / Unknown --</option>
                        {NAKSHATRAS_LIST.map((n) => (
                          <option key={n.id} value={n.id}>
                            {n.id}. {n.en} ({n.ta})
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                        {language === "ta" ? "சந்திர ராசி" : "Native's Moon Sign"}
                      </label>
                      <select
                        value={nativeRashi}
                        onChange={(e) => setNativeRashi(e.target.value ? Number(e.target.value) : "")}
                        className="w-full px-2.5 py-1.5 text-xs bg-white border border-slate-200 rounded-lg text-slate-800"
                      >
                        <option value="">-- None / Unknown --</option>
                        {RASHIS_LIST.map((r) => (
                          <option key={r.id} value={r.id}>
                            {r.id}. {r.en} ({r.ta})
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Submit Action */}
          <div className="flex items-center justify-end gap-4 pt-2">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-gradient-to-r from-amber-600 via-amber-700 to-amber-800 hover:from-amber-700 hover:to-amber-900 text-white font-bold rounded-2xl shadow-lg hover:shadow-xl transition-all flex items-center gap-2 text-sm disabled:opacity-50"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>{language === "ta" ? "கணக்கிடப்படுகிறது..." : "Calculating Ephemeris..."}</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>{language === "ta" ? "சுப முகூர்த்தங்களைத் தேடு" : "Calculate Auspicious Muhurtas"}</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-600 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Candidate Results View */}
      {searchResponse && (
        <div className="space-y-6">
          {/* Summary & Filters Header */}
          <div className="bg-white rounded-3xl p-5 border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <span>{searchResponse.occasion.name_en}</span>
                <span className="text-amber-700 font-tamil font-semibold">({searchResponse.occasion.name_ta})</span>
                <span className="px-2 py-0.5 rounded-full text-xs bg-slate-100 text-slate-700 font-mono">
                  {searchResponse.total_candidates} {language === "ta" ? "நேரங்கள்" : "candidate windows"}
                </span>
              </div>
              <div className="text-xs text-slate-500 mt-1 flex items-center gap-3">
                <span>📍 {cityName}</span>
                <span>📅 {startDate} to {endDate}</span>
              </div>
            </div>

            {/* Filter Chips */}
            <div className="flex items-center gap-1.5 overflow-x-auto text-xs">
              <button
                type="button"
                onClick={() => setStatusFilter("all")}
                className={`px-3 py-1.5 rounded-xl font-medium transition-all ${
                  statusFilter === "all"
                    ? "bg-slate-900 text-white font-semibold"
                    : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                }`}
              >
                {language === "ta" ? "அனைத்தும்" : "All"} ({searchResponse.candidates.length})
              </button>
              <button
                type="button"
                onClick={() => setStatusFilter("auspicious")}
                className={`px-3 py-1.5 rounded-xl font-medium transition-all ${
                  statusFilter === "auspicious"
                    ? "bg-emerald-600 text-white font-semibold"
                    : "bg-emerald-50 text-emerald-800 hover:bg-emerald-100"
                }`}
              >
                {language === "ta" ? "முழு சுப நேரம்" : "Auspicious"} (
                {searchResponse.candidates.filter((c) => c.status === "meets_configured_rules").length})
              </button>
              <button
                type="button"
                onClick={() => setStatusFilter("advisory")}
                className={`px-3 py-1.5 rounded-xl font-medium transition-all ${
                  statusFilter === "advisory"
                    ? "bg-amber-600 text-white font-semibold"
                    : "bg-amber-50 text-amber-800 hover:bg-amber-100"
                }`}
              >
                {language === "ta" ? "எச்சரிக்கையுடன்" : "With Advisories"} (
                {searchResponse.candidates.filter((c) => c.status === "meets_rules_with_advisories").length})
              </button>
              <button
                type="button"
                onClick={() => setStatusFilter("restricted")}
                className={`px-3 py-1.5 rounded-xl font-medium transition-all ${
                  statusFilter === "restricted"
                    ? "bg-rose-600 text-white font-semibold"
                    : "bg-rose-50 text-rose-800 hover:bg-rose-100"
                }`}
              >
                {language === "ta" ? "தடைபட்டவை" : "Restricted"} (
                {searchResponse.candidates.filter((c) => c.status === "fails_mandatory_rules").length})
              </button>
            </div>
          </div>

          {/* Candidates List */}
          {filteredCandidates && filteredCandidates.length === 0 ? (
            <div className="bg-white rounded-3xl p-12 text-center border border-slate-200">
              <HelpCircle className="w-12 h-12 text-slate-300 mx-auto mb-3" />
              <h4 className="text-base font-bold text-slate-700">
                {language === "ta" ? "முகூர்த்தங்கள் எதுவும் இல்லை" : "No candidate windows found"}
              </h4>
              <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
                {language === "ta"
                  ? "தேர்ந்தெடுக்கப்பட்ட தேதி எல்லை அல்லது நேர வரம்பில் விதிகளை நிறைவு செய்யும் சுப முகூர்த்தங்கள் அமையவில்லை. தேதி எல்லையை நீட்டிக்கவும்."
                  : "No slots met the selected criteria within this date range and location. Try widening the date range or selecting All Day."}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-5">
              {filteredCandidates?.map((cand) => {
                const isSaved = savedSuccessMap[cand.id] !== undefined;
                const isSaving = savingId === cand.id;

                const statusBg =
                  cand.status === "meets_configured_rules"
                    ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                    : cand.status === "meets_rules_with_advisories"
                    ? "bg-amber-50 text-amber-800 border-amber-200"
                    : cand.status === "incomplete"
                    ? "bg-blue-50 text-blue-800 border-blue-200"
                    : "bg-rose-50 text-rose-800 border-rose-200";

                return (
                  <div
                    key={cand.id}
                    className="bg-white rounded-3xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow overflow-hidden p-6 sm:p-7 space-y-5"
                  >
                    {/* Top Row: Date, Time Window, Status Badge, Score */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-base sm:text-lg font-extrabold text-slate-900">
                            {cand.event_date} ({cand.weekday})
                          </span>
                          <span className="text-xs text-amber-700 font-tamil font-bold">
                            {cand.weekday_ta}
                          </span>
                        </div>
                        <div className="text-sm font-bold text-amber-700 flex items-center gap-1.5 mt-0.5">
                          <Clock className="w-4 h-4 text-amber-600" />
                          <span>
                            {cand.start_time_local} – {cand.end_time_local}
                          </span>
                          <span className="text-xs font-normal text-slate-500">
                            ({cand.duration_minutes} {language === "ta" ? "நிமிடங்கள்" : "mins"})
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        {/* Score Indicator */}
                        <div className="text-right">
                          <div className="text-xl sm:text-2xl font-black text-slate-900 leading-none">
                            {cand.score}
                            <span className="text-xs font-normal text-slate-400">/100</span>
                          </div>
                          <div className="text-[10px] text-slate-500 font-medium mt-0.5">
                            {language === "ta" ? "விதி மதிப்பெண்" : "Rule Score"}
                          </div>
                        </div>

                        {/* Status Chip */}
                        <span className={`px-3 py-1.5 rounded-xl text-xs font-bold border ${statusBg}`}>
                          {cand.status === "meets_configured_rules"
                            ? language === "ta" ? "சுப முகூர்த்தம்" : "Meets Rules"
                            : cand.status === "meets_rules_with_advisories"
                            ? language === "ta" ? "எச்சரிக்கையுடன்" : "Advisories"
                            : cand.status === "incomplete"
                            ? language === "ta" ? "முழுமையடையாதது" : "Incomplete Data"
                            : language === "ta" ? "தடைபட்டது" : "Fails Rules"}
                        </span>
                      </div>
                    </div>

                    {/* Middle Row: Astrological Limbs (Tithi, Nakshatra, Lagna, Yoga/Karana) */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-50/70 p-4 rounded-2xl border border-slate-100 text-xs">
                      {/* Ascendant / Lagna */}
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-bold tracking-wider">
                          {language === "ta" ? "சுப லக்னம்" : "Ascendant / Lagna"}
                        </span>
                        <div className="font-extrabold text-slate-900 mt-0.5">
                          {cand.ascendant.sign_name}
                        </div>
                        <div className="text-amber-700 font-tamil text-[11px]">
                          {cand.ascendant.sign_name_ta} ({cand.ascendant.degree_in_sign.toFixed(1)}°)
                        </div>
                      </div>

                      {/* Nakshatra */}
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-bold tracking-wider">
                          {language === "ta" ? "நட்சத்திரம்" : "Nakshatra"}
                        </span>
                        <div className="font-extrabold text-slate-900 mt-0.5">
                          {cand.nakshatra.name}
                        </div>
                        <div className="text-slate-600 text-[11px]">
                          {language === "ta" ? "பாதம்" : "Pada"} {cand.nakshatra.pada} • {cand.nakshatra.lord}
                        </div>
                      </div>

                      {/* Tithi */}
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-bold tracking-wider">
                          {language === "ta" ? "திதி" : "Tithi"}
                        </span>
                        <div className="font-extrabold text-slate-900 mt-0.5">
                          {cand.tithi.name}
                        </div>
                        <div className="text-slate-600 text-[11px]">
                          {cand.tithi.paksha}
                        </div>
                      </div>

                      {/* Yoga & Karana */}
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-bold tracking-wider">
                          {language === "ta" ? "யோகம் / கரணம்" : "Yoga / Karana"}
                        </span>
                        <div className="font-extrabold text-slate-900 mt-0.5 truncate">
                          {cand.yoga.name}
                        </div>
                        <div className="text-slate-600 text-[11px] truncate">
                          {cand.karana.name}
                        </div>
                      </div>
                    </div>

                    {/* Prohibited & Auspicious Overlap Warnings */}
                    <div className="flex flex-wrap items-center gap-3 text-xs">
                      {cand.inauspicious_periods.rahu_kalam && (
                        <div className="text-slate-600 flex items-center gap-1 bg-slate-100 px-2.5 py-1 rounded-lg">
                          <span className="font-semibold">{language === "ta" ? "ராகு காலம்:" : "Rahu Kalam:"}</span>
                          <span>{cand.inauspicious_periods.rahu_kalam.start_local} – {cand.inauspicious_periods.rahu_kalam.end_local}</span>
                        </div>
                      )}
                      {cand.inauspicious_periods.yamagandam && (
                        <div className="text-slate-600 flex items-center gap-1 bg-slate-100 px-2.5 py-1 rounded-lg">
                          <span className="font-semibold">{language === "ta" ? "எமகண்டம்:" : "Yamagandam:"}</span>
                          <span>{cand.inauspicious_periods.yamagandam.start_local} – {cand.inauspicious_periods.yamagandam.end_local}</span>
                        </div>
                      )}
                      {cand.inauspicious_periods.varjyam && (
                        <div className="text-rose-800 flex items-center gap-1 bg-rose-50 border border-rose-200 px-2.5 py-1 rounded-lg">
                          <span className="font-semibold">{language === "ta" ? "வர்ஜியம்:" : "Varjyam:"}</span>
                          <span>{cand.inauspicious_periods.varjyam.start_local} – {cand.inauspicious_periods.varjyam.end_local}</span>
                        </div>
                      )}
                      {cand.auspicious_periods.abhijit && (
                        <div className="text-emerald-800 flex items-center gap-1 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-lg">
                          <Sparkles className="w-3 h-3 text-emerald-600" />
                          <span className="font-semibold">{language === "ta" ? "அபிஜித் முகூர்த்தம்:" : "Abhijit:"}</span>
                          <span>{cand.auspicious_periods.abhijit.start_local} – {cand.auspicious_periods.abhijit.end_local}</span>
                        </div>
                      )}
                    </div>

                    {/* Rule Breakdown (Passed, Advisories, Incomplete) */}
                    <div className="space-y-1.5 pt-1">
                      {/* Explanation */}
                      <p className="text-xs text-slate-700 italic">
                        "{cand.explanation}"
                      </p>

                      {/* Passed Rules */}
                      {cand.passed_rules.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mt-2">
                          {cand.passed_rules.slice(0, 4).map((p, i) => (
                            <span
                              key={i}
                              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-800 text-[11px] border border-emerald-100"
                            >
                              <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                              <span>{p.message}</span>
                            </span>
                          ))}
                          {cand.passed_rules.length > 4 && (
                            <span className="text-[11px] text-slate-400 self-center">
                              +{cand.passed_rules.length - 4} {language === "ta" ? "கூடுதல் விதிகளுக்கு உட்பட்டது" : "more rules passed"}
                            </span>
                          )}
                        </div>
                      )}

                      {/* Advisories */}
                      {cand.advisories.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mt-1.5">
                          {cand.advisories.map((adv, i) => (
                            <span
                              key={i}
                              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-amber-50 text-amber-800 text-[11px] border border-amber-200"
                            >
                              <AlertTriangle className="w-3 h-3 text-amber-600" />
                              <span>{adv.message}</span>
                            </span>
                          ))}
                        </div>
                      )}

                      {/* Failed Rules */}
                      {cand.failed_rules.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mt-1.5">
                          {cand.failed_rules.map((fail, i) => (
                            <span
                              key={i}
                              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-rose-50 text-rose-800 text-[11px] border border-rose-200"
                            >
                              <XCircle className="w-3 h-3 text-rose-600" />
                              <span>{fail.message}</span>
                            </span>
                          ))}
                        </div>
                      )}

                      {/* Incomplete Checks */}
                      {cand.incomplete_checks && cand.incomplete_checks.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mt-1.5">
                          {cand.incomplete_checks.map((inc, i) => (
                            <span
                              key={i}
                              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-blue-50 text-blue-800 text-[11px] border border-blue-200"
                            >
                              <HelpCircle className="w-3 h-3 text-blue-600" />
                              <span>{inc.message}</span>
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Bottom Action Buttons */}
                    <div className="flex items-center justify-between pt-3 border-t border-slate-100">
                      <div className="text-[11px] text-slate-500">
                        {isSaved ? (
                          <span className="text-emerald-700 font-bold flex items-center gap-1">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            {language === "ta"
                              ? `முகூர்த்தம் #${savedSuccessMap[cand.id]} என சேமிக்கப்பட்டது`
                              : `Saved as Muhurta #${savedSuccessMap[cand.id]}`}
                          </span>
                        ) : (
                          <span>
                            {language === "ta" ? "கணக்கீட்டு முறை:" : "Engine:"} Swiss Ephemeris (Meeus/NOAA)
                          </span>
                        )}
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => openReportForCandidate(cand)}
                          className="px-3 py-1.5 rounded-xl border border-slate-300 hover:border-slate-400 bg-white text-slate-700 hover:bg-slate-50 text-xs font-semibold flex items-center gap-1.5 transition-colors"
                        >
                          <Printer className="w-3.5 h-3.5" />
                          <span>{language === "ta" ? "சான்றிதழ் / அறிக்கை" : "Certificate / PDF"}</span>
                        </button>

                        <button
                          type="button"
                          disabled={isSaved || isSaving}
                          onClick={() => setCandidateToSave(cand)}
                          className={`px-3.5 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all ${
                            isSaved
                              ? "bg-emerald-100 text-emerald-800 cursor-default"
                              : "bg-slate-900 hover:bg-black text-white shadow-sm"
                          }`}
                        >
                          <Bookmark className="w-3.5 h-3.5" />
                          <span>
                            {isSaved
                              ? language === "ta" ? "சேமிக்கப்பட்டது" : "Saved"
                              : language === "ta" ? "சேமிக்க" : "Save Selection"}
                          </span>
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Save Modal Dialog */}
      {candidateToSave && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-white rounded-3xl p-6 sm:p-7 max-w-md w-full shadow-2xl border border-slate-200 space-y-4">
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Bookmark className="w-5 h-5 text-amber-600" />
              <span>{language === "ta" ? "முகூர்த்தத்தை சேமிக்கவும்" : "Save Muhurta Selection"}</span>
            </h3>
            <p className="text-xs text-slate-600">
              {language === "ta"
                ? `தேதி: ${candidateToSave.event_date} (${candidateToSave.start_time_local} - ${candidateToSave.end_time_local}) லக்னம்: ${candidateToSave.ascendant.sign_name}`
                : `Date: ${candidateToSave.event_date} (${candidateToSave.start_time_local} - ${candidateToSave.end_time_local}) Lagna: ${candidateToSave.ascendant.sign_name}`}
            </p>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                {language === "ta" ? "வாடிக்கையாளர் / நபர் பெயர் (விருப்பத்தேர்வு)" : "Client / Family Name (Optional)"}
              </label>
              <input
                type="text"
                value={saveClientName}
                onChange={(e) => setSaveClientName(e.target.value)}
                placeholder="e.g. Ramesh & Priya Wedding"
                className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-800"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                {language === "ta" ? "குறிப்புகள் / சடங்கு விவரங்கள்" : "Notes / Ceremony Details"}
              </label>
              <textarea
                value={saveNotes}
                onChange={(e) => setSaveNotes(e.target.value)}
                rows={3}
                placeholder="Add special instructions, pandit contacts, or hall booking notes..."
                className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-800"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setCandidateToSave(null)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 transition-colors"
              >
                {language === "ta" ? "ரத்து" : "Cancel"}
              </button>
              <button
                type="button"
                disabled={savingId !== null}
                onClick={handleConfirmSave}
                className="px-5 py-2 rounded-xl text-xs font-bold bg-amber-600 hover:bg-amber-700 text-white shadow-md transition-colors flex items-center gap-1.5"
              >
                {savingId !== null ? (
                  <>
                    <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>{language === "ta" ? "சேமிக்கப்படுகிறது..." : "Saving..."}</span>
                  </>
                ) : (
                  <>
                    <Check className="w-3.5 h-3.5" />
                    <span>{language === "ta" ? "உறுதி செய்து சேமி" : "Confirm & Save"}</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Official Certificate Report Modal */}
      {reportCandidate && (
        <MuhurtaReportModal
          isOpen={isReportOpen}
          onClose={() => setIsReportOpen(false)}
          reportData={reportCandidate}
        />
      )}
    </div>
  );
}
