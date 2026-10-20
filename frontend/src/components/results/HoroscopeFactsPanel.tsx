"use client";

import React, { useState, useEffect, useMemo } from "react";
import Link from "next/link";
import { FullHoroscopeResult, ShadbalaResponse } from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { formatDms, formatBirthDate, formatBirthTime } from "@/lib/formatters";
import { calculateSolarTimes } from "@/lib/solar-astronomy";
import { calculateShadbala, calculateHoroscope } from "@/lib/api";
import {
  getRasiNameTamil,
  getPlanetNameTamil,
  getPlanetAbbrTamil,
  getNakshatraTamil,
  formatTithiTamil,
  formatYogaTamil,
  formatKaranaTamil,
  formatLatitudeDms,
  formatLongitudeDms,
  formatAyanamsaDms,
  formatBalanceYMD,
  getLagnaClassification,
  calculateJaiminiKarakas,
  calculatePlanetAvastha,
  evaluateGocharaHouse,
  RASI_NAMES_TA,
  PLANET_TA_MAP,
} from "@/lib/tamil-astrology";
import { HousesTable } from "@/components/results/HousesTable";
import {
  Compass,
  Sparkles,
  ShieldCheck,
  Activity,
  RotateCw,
  Crown,
  Sun,
  Moon,
  Clock,
  Calendar,
  MapPin,
  Globe,
  Sliders,
  Award,
  Layers,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Zap,
  Star,
  Info,
} from "lucide-react";

export type FactCategory =
  | "basic"
  | "special"
  | "benefic_malefic"
  | "shadbala_avastha"
  | "transit"
  | "jaimini";

interface HoroscopeFactsPanelProps {
  result: FullHoroscopeResult;
  onCalculateExtensions?: () => Promise<void>;
  isCalculatingExtensions?: boolean;
  initialCategory?: FactCategory;
}

export function HoroscopeFactsPanel({
  result,
  onCalculateExtensions,
  isCalculatingExtensions = false,
  initialCategory = "basic",
}: HoroscopeFactsPanelProps) {
  const { language } = useLanguage();
  const [activeCategory, setActiveCategory] = useState<FactCategory>(initialCategory);
  const [showHousesTable, setShowHousesTable] = useState(false);

  // Local Shadbala state
  const [shadbalaData, setShadbalaData] = useState<ShadbalaResponse | null>(
    () => result.shadbala || (result.horoscope as any).shadbala || null
  );
  const [isLoadingShadbala, setIsLoadingShadbala] = useState(false);
  const [shadbalaError, setShadbalaError] = useState<string | null>(null);

  const { horoscope, dasa, kp, clientInputs } = result;

  // 1. Core Native Elements
  const moon = useMemo(
    () => horoscope.planets?.find((p) => p.name === "Moon"),
    [horoscope.planets]
  );
  const ascendant = horoscope.ascendant;
  const panchang = horoscope.panchang;

  // 2. Solar Sunrise and Sunset
  const solarTimes = useMemo(() => {
    const tzHours =
      horoscope.metadata?.utc_offset_hours !== undefined
        ? horoscope.metadata.utc_offset_hours
        : 5.5;
    return calculateSolarTimes(
      clientInputs.birthDate,
      clientInputs.latitude,
      clientInputs.longitude,
      tzHours
    );
  }, [clientInputs, horoscope.metadata]);

  // 3. Dasa and Bhukti Balances
  const dasaBalance = useMemo(() => {
    // A: Check Dasa tree & birth_balance_years
    const dasaLord = dasa?.birth_dasa_lord || "Unknown";
    const dasaYears = dasa?.birth_balance_years ?? (kp?.dasa_hierarchy?.mahadasha_balance_years || 0);
    const dasaYMD = formatBalanceYMD(dasaYears);

    // B: Check birth bhukti
    let bhuktiLord = "Unknown";
    let bhuktiYears = 0;

    if (dasa?.dasa_tree?.[0]?.sub_periods?.[0]) {
      const firstSub = dasa.dasa_tree[0].sub_periods[0];
      bhuktiLord = firstSub.lord;
      bhuktiYears = firstSub.duration_years || (firstSub.duration_days ? firstSub.duration_days / 365.25 : 0);
    } else if (kp?.dasa_hierarchy?.antardasha_lord) {
      bhuktiLord = kp.dasa_hierarchy.antardasha_lord;
      bhuktiYears = (kp.dasa_hierarchy.antardasha_balance_days || 0) / 365.25;
    }

    const bhuktiYMD = formatBalanceYMD(bhuktiYears);

    return {
      dasaLord,
      dasaLordTa: getPlanetNameTamil(dasaLord),
      dasaLordAbbr: getPlanetAbbrTamil(dasaLord),
      dasaYMD,
      bhuktiLord,
      bhuktiLordTa: getPlanetNameTamil(bhuktiLord),
      bhuktiLordAbbr: getPlanetAbbrTamil(bhuktiLord),
      bhuktiYMD,
    };
  }, [dasa, kp]);

  // 4. Lagna Classification (Functional Benefics & Malefics)
  const lagnaInfo = useMemo(() => {
    return getLagnaClassification(ascendant?.sign_name);
  }, [ascendant?.sign_name]);

  // 5. Jaimini Chara Karakas
  const jaiminiKarakas = useMemo(() => {
    return calculateJaiminiKarakas(horoscope.planets || []);
  }, [horoscope.planets]);

  // 6. Planetary Avasthas
  const avasthas = useMemo(() => {
    return (horoscope.planets || [])
      .filter((p) =>
        ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"].includes(p.name)
      )
      .map((p) =>
        calculatePlanetAvastha(p.name, p.sign_name, p.sign_index, p.degree_in_sign)
      );
  }, [horoscope.planets]);

  // 7. Special Features (Vargottama, Dignities, Yogas)
  const specialFeatures = useMemo(() => {
    const vargottamaList: string[] = [];
    const exaltedList: string[] = [];
    const ownSignList: string[] = [];
    const debilitatedList: string[] = [];

    const d9Map = (horoscope as any).varga_d1_d9?.d9_planets || {};

    (horoscope.planets || []).forEach((p) => {
      // Vargottama: D1 sign matches D9 sign
      // Calculated via classical Parashara continuous 108-pada Navamsa cycle (3°20' per Navamsa)
      const d1SignIdx = p.sign_index;
      const totalDeg = (d1SignIdx - 1) * 30 + p.degree_in_sign;
      const calculatedD9Idx = (Math.floor(totalDeg / (10 / 3)) % 12) + 1;
      const d9Sign = d9Map[p.name]?.sign_name || d9Map[p.name]?.rasi;
      const isVargottama =
        calculatedD9Idx === d1SignIdx ||
        (d9Sign && d9Sign.toLowerCase() === p.sign_name.toLowerCase());

      if (isVargottama) {
        vargottamaList.push(getPlanetNameTamil(p.name));
      }

      // Dignities
      const name = p.name;
      const sign = p.sign_name;
      const exSigns: Record<string, string> = {
        Sun: "Aries",
        Moon: "Taurus",
        Mars: "Capricorn",
        Mercury: "Virgo",
        Jupiter: "Cancer",
        Venus: "Pisces",
        Saturn: "Libra",
      };
      const debSigns: Record<string, string> = {
        Sun: "Libra",
        Moon: "Scorpio",
        Mars: "Cancer",
        Mercury: "Pisces",
        Jupiter: "Capricorn",
        Venus: "Virgo",
        Saturn: "Aries",
      };
      const ownSigns: Record<string, string[]> = {
        Sun: ["Leo"],
        Moon: ["Cancer"],
        Mars: ["Aries", "Scorpio"],
        Mercury: ["Gemini", "Virgo"],
        Jupiter: ["Sagittarius", "Pisces"],
        Venus: ["Taurus", "Libra"],
        Saturn: ["Capricorn", "Aquarius"],
      };

      if (exSigns[name] === sign) exaltedList.push(getPlanetNameTamil(name));
      if (debSigns[name] === sign) debilitatedList.push(getPlanetNameTamil(name));
      if (ownSigns[name]?.includes(sign)) ownSignList.push(getPlanetNameTamil(name));
    });

    // Lagna Lord & Placement
    const lagnaLord = lagnaInfo.lagnaLord;
    const lagnaLordPlanet = horoscope.planets?.find((p) => p.name === lagnaLord);
    const lagnaLordHouse = lagnaLordPlanet?.house || "—";
    const lagnaLordSignTa = lagnaLordPlanet?.sign_name_tamil || getRasiNameTamil(lagnaLordPlanet?.sign_name);

    // Moon Lord & Placement
    const moonSign = moon?.sign_name || "Aries";
    const moonLordSignMap: Record<string, string> = {
      Aries: "Mars", Taurus: "Venus", Gemini: "Mercury", Cancer: "Moon",
      Leo: "Sun", Virgo: "Mercury", Libra: "Venus", Scorpio: "Mars",
      Sagittarius: "Jupiter", Capricorn: "Saturn", Aquarius: "Saturn", Pisces: "Jupiter",
    };
    const moonLord = moonLordSignMap[moonSign] || "Moon";
    const moonLordPlanet = horoscope.planets?.find((p) => p.name === moonLord);
    const moonLordHouse = moonLordPlanet?.house || "—";
    const moonLordSignTa = moonLordPlanet?.sign_name_tamil || getRasiNameTamil(moonLordPlanet?.sign_name);

    // Active Vedic Yogas
    const rawYogas = (horoscope.vedic_yogas?.yogas || (horoscope as any).vedic_yogas?.qualifying_yogas || []) as Array<{
      name?: string;
      name_tamil?: string;
      category?: string;
      short_interpretation?: string;
      description?: string;
      is_qualifying?: boolean;
      status?: string;
    }>;
    const activeYogas = rawYogas
      .filter((y) => y.is_qualifying !== false && y.status !== "Cancelled" && y.status !== "Not Qualifying")
      .map((y) => ({
        name: y.name || "Yoga",
        nameTa: y.name_tamil || y.name || "யோகம்",
        category: y.category || "General",
        description: y.short_interpretation || y.description || "சுப பலன்களைத் தரக்கூடிய யோகம்.",
        isBenefic: true,
      }));

    return {
      vargottamaList,
      exaltedList,
      ownSignList,
      debilitatedList,
      lagnaLordTa: getPlanetNameTamil(lagnaLord),
      lagnaLordHouse,
      lagnaLordSignTa,
      moonLordTa: getPlanetNameTamil(moonLord),
      moonLordHouse,
      moonLordSignTa,
      activeYogas,
    };
  }, [horoscope, lagnaInfo, moon]);

  // 8. Gochara (Transit Positions) - Live Ephemeris Calculation
  const [transitDate, setTransitDate] = useState<string>(() => {
    const d = new Date();
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  });
  const [transitPlanets, setTransitPlanets] = useState<any[] | null>(null);
  const [isLoadingTransit, setIsLoadingTransit] = useState(false);
  const [transitError, setTransitError] = useState<string | null>(null);

  const handleFetchTransit = async (targetDate?: string) => {
    const dateToUse = targetDate || transitDate;
    setIsLoadingTransit(true);
    setTransitError(null);
    try {
      const res = await calculateHoroscope({
        birth_date: dateToUse,
        birth_time: "12:00",
        timezone: clientInputs.timezone || "Asia/Kolkata",
        latitude: clientInputs.latitude || 13.0827,
        longitude: clientInputs.longitude || 80.2707,
        ayanamsa: clientInputs.ayanamsaId ?? 1,
        house_system: clientInputs.houseSystemId || 0,
        include_panchang: false,
        include_outer_planets: false,
        include_nabhasha: false,
        include_ashtakavarga: false,
        include_vedic_yogas: false,
      });
      setTransitPlanets(res.planets || []);
    } catch (err: any) {
      console.warn("Failed to calculate Gochara transit:", err);
      setTransitError(err?.message || "கோச்சார கணக்கீட்டில் பிழை ஏற்பட்டது.");
    } finally {
      setIsLoadingTransit(false);
    }
  };

  useEffect(() => {
    if (activeCategory === "transit" && !transitPlanets && !isLoadingTransit) {
      handleFetchTransit();
    }
  }, [activeCategory]);

  // Evaluates real transiting planets relative to natal Moon and natal Lagna
  const transitEvaluations = useMemo(() => {
    if (!transitPlanets || transitPlanets.length === 0) return null;

    const natalMoonSignIdx = moon?.sign_index || 4; // Cancer default
    const natalLagnaSignIdx = ascendant?.sign_index || 9; // Sagittarius default

    const PLANET_ORDER = ["Jupiter", "Saturn", "Rahu", "Ketu", "Sun", "Moon", "Mars", "Mercury", "Venus"];

    const sortedPlanets = [...transitPlanets]
      .filter((p) => PLANET_ORDER.includes(p.name))
      .sort((a, b) => PLANET_ORDER.indexOf(a.name) - PLANET_ORDER.indexOf(b.name));

    return sortedPlanets.map((tr) => {
      const signIdx = tr.sign_index;
      const houseFromMoon = ((signIdx - natalMoonSignIdx + 12) % 12) + 1;
      const houseFromLagna = ((signIdx - natalLagnaSignIdx + 12) % 12) + 1;
      const evaluation = evaluateGocharaHouse(tr.name, houseFromMoon);

      return {
        planet: tr.name,
        planetTa: tr.name_tamil || getPlanetNameTamil(tr.name),
        transitSign: tr.sign_name_tamil || getRasiNameTamil(tr.sign_name),
        degFormatted: formatDms(tr.degree_in_sign),
        houseFromMoon,
        houseFromLagna,
        isRetrograde: tr.is_retrograde,
        nature: evaluation.nature,
        natureTa: evaluation.natureTa,
        summaryTa: evaluation.summaryTa,
      };
    });
  }, [transitPlanets, moon, ascendant]);

  // Auto-fetch Shadbala if not yet present
  const handleFetchShadbala = async () => {
    if (shadbalaData || isLoadingShadbala) return;
    setIsLoadingShadbala(true);
    setShadbalaError(null);
    try {
      const res = await calculateShadbala({
        birth_date: clientInputs.birthDate,
        birth_time: clientInputs.birthTime,
        timezone: clientInputs.timezone,
        latitude: clientInputs.latitude,
        longitude: clientInputs.longitude,
        ayanamsa: clientInputs.ayanamsaId,
        house_system: clientInputs.houseSystemId || 0,
      });
      setShadbalaData(res);
    } catch (err: any) {
      console.warn("Failed to calculate Shadbala:", err);
      setShadbalaError(err?.message || "ஷட்பலம் கணக்கிடுவதில் பிழை ஏற்பட்டது.");
    } finally {
      setIsLoadingShadbala(false);
    }
  };

  useEffect(() => {
    if (activeCategory === "shadbala_avastha" && !shadbalaData && !isLoadingShadbala) {
      handleFetchShadbala();
    }
  }, [activeCategory]);

  // Categories list in exact order:
  // 1. அடிப்படை
  // 2. சிறப்பு அம்சங்கள்
  // 3. சுப & பாவ கிரகங்கள்
  // 4. ஷட்பலம் & அவஸ்தை
  // 5. பெயர்ச்சி (கோச்சாரம்)
  // 6. ஜைமினி சார காரகங்கள்
  const categories: Array<{
    id: FactCategory;
    title: string;
    subtitle: string;
    icon: React.ComponentType<{ className?: string }>;
  }> = [
    {
      id: "basic",
      title: "அடிப்படை",
      subtitle: "பஞ்சாங்கம், தசை இருப்பு, பிறப்பு விவரங்கள்",
      icon: Compass,
    },
    {
      id: "special",
      title: "சிறப்பு அம்சங்கள்",
      subtitle: "லக்னாதிபதி, வர்க்கோத்தமம், விசேஷ யோகங்கள்",
      icon: Sparkles,
    },
    {
      id: "benefic_malefic",
      title: "சுப & பாவ கிரகங்கள்",
      subtitle: "லக்ன சுபர்கள், பாவிகள், யோககாரகன்",
      icon: ShieldCheck,
    },
    {
      id: "shadbala_avastha",
      title: "ஷட்பலம் & அவஸ்தை",
      subtitle: "ஆறு வகை கிரக பலம் மற்றும் அவஸ்தைகள்",
      icon: Activity,
    },
    {
      id: "transit",
      title: "பெயர்ச்சி (கோச்சாரம்)",
      subtitle: "குரு, சனி, ராகு-கேது கோசார பலன்கள்",
      icon: RotateCw,
    },
    {
      id: "jaimini",
      title: "ஜைமினி சார காரகங்கள்",
      subtitle: "ஆத்மகாரகன், அமாத்யகாரகன் (7 காரகங்கள்)",
      icon: Crown,
    },
  ];

  const handleSelectCategory = (catId: FactCategory) => {
    setActiveCategory(catId);
    if (typeof window !== "undefined") {
      const url = new URL(window.location.href);
      url.searchParams.set("category", catId);
      window.history.replaceState(null, "", url.toString());
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner introducing the Tamil Horoscope Details Section */}
      <div className="bg-gradient-to-r from-[#153F6B] to-[#1F548A] rounded-xl p-4 sm:p-5 text-white shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#FAF2DE] text-[#B4872B] tracking-wider uppercase">
              ஜாதக விவரங்கள்
            </span>
            <span className="text-xs text-blue-200">
              {clientInputs.fullName || (language === "ta" ? "ஜாதகர்" : "Native")}
            </span>
          </div>
          <h2 className="font-serif text-lg sm:text-xl font-bold tracking-tight">
            ஜாதக உண்மைகள் & விரிவான கணிப்புகள்
          </h2>
          <p className="text-xs text-blue-100 max-w-2xl">
            வேத முறைப்படியான பஞ்சாங்கம், தசா-புக்தி இருப்பு, லக்ன சுப/பாவ தன்மை, ஷட்பலம் மற்றும் ஜைமினி காரகங்களின் முழுமையான தொகுப்பு.
          </p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <div className="text-right hidden sm:block text-xs text-blue-200">
            <div>ராசி: <strong className="text-white">{moon?.sign_name_tamil || getRasiNameTamil(moon?.sign_name)}</strong></div>
            <div>லக்கினம்: <strong className="text-white">{ascendant?.sign_name_tamil || getRasiNameTamil(ascendant?.sign_name)}</strong></div>
          </div>
        </div>
      </div>

      {/* Main 2-Column Responsive Layout: Left Sidebar + Right Content */}
      <div className="flex flex-col lg:flex-row gap-6 items-start">
        {/* ========================================================================= */}
        {/* LEFT-SIDE CATEGORY NAVIGATION (Mobile: Horizontal Scroll, Desktop: Vertical) */}
        {/* ========================================================================= */}
        <div className="w-full lg:w-72 shrink-0 space-y-3">
          <div className="bg-white rounded-xl border border-[#D9DEE7] p-2.5 sm:p-3 shadow-2xs">
            <div className="px-3 py-2 text-[11px] font-bold text-[#8190A6] uppercase tracking-wider hidden lg:block border-b border-[#F2F3F5] mb-2">
              பிரிவுகள் (Categories)
            </div>

            {/* Navigation buttons */}
            <div className="flex lg:flex-col overflow-x-auto lg:overflow-visible gap-1.5 pb-1 lg:pb-0 scrollbar-thin">
              {categories.map((cat, idx) => {
                const Icon = cat.icon;
                const isSelected = activeCategory === cat.id;

                return (
                  <button
                    key={cat.id}
                    type="button"
                    onClick={() => handleSelectCategory(cat.id)}
                    className={`flex items-center gap-3 px-3.5 py-3 rounded-lg text-left transition-all cursor-pointer whitespace-nowrap lg:whitespace-normal shrink-0 lg:shrink ${
                      isSelected
                        ? "bg-[#153F6B] text-white shadow-2xs font-bold"
                        : "bg-transparent text-[#52667E] hover:text-[#183047] hover:bg-[#F2F6FA]"
                    }`}
                  >
                    <span
                      className={`p-2 rounded-lg shrink-0 ${
                        isSelected
                          ? "bg-white/15 text-white"
                          : "bg-[#F2F3F5] text-[#153F6B]"
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                    </span>

                    <div className="min-w-0">
                      <div className="flex items-center gap-1.5">
                        <span className="text-xs font-mono opacity-60">
                          {idx + 1}.
                        </span>
                        <span className="text-xs sm:text-sm font-semibold truncate">
                          {cat.title}
                        </span>
                      </div>
                      <p
                        className={`text-[10px] truncate hidden sm:block ${
                          isSelected ? "text-blue-100" : "text-[#8190A6]"
                        }`}
                      >
                        {cat.subtitle}
                      </p>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Quick Info card below sidebar on desktop */}
          <div className="hidden lg:block bg-[#FAF8F5] rounded-xl border border-[#E2DCD5] p-4 text-xs space-y-2">
            <div className="flex items-center gap-1.5 font-bold text-[#183047]">
              <Sparkles className="w-4 h-4 text-[#B4872B]" />
              <span>பாரம்பரிய ஜோதிட முறை</span>
            </div>
            <p className="text-[11px] text-[#52667E] leading-relaxed">
              அனைத்து கணிப்புகளும் சித்திரபக்ஷ லாகிரி அயனாம்சம் மற்றும் பராசர முனிவரின் சாஸ்திர விதிகளை அடிப்படையாகக் கொண்டவை.
            </p>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* MAIN CONTENT PANEL ON THE RIGHT */}
        {/* ========================================================================= */}
        <div className="flex-1 w-full min-w-0 space-y-6">
          {/* ===================================================================== */}
          {/* CATEGORY 1: அடிப்படை */}
          {/* ===================================================================== */}
          {activeCategory === "basic" && (
            <div className="space-y-6">
              {/* SECTION A: பஞ்சாங்கம் (Panchangam) */}
              <div className="bg-white rounded-xl border border-[#D9DEE7] p-5 shadow-2xs space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-[#F2F3F5]">
                  <div className="flex items-center gap-2.5">
                    <span className="p-2 rounded-lg bg-[#FAF2DE] text-[#B4872B] border border-[#D8BD80]">
                      <Compass className="w-4 h-4" />
                    </span>
                    <div>
                      <h3 className="font-serif text-base font-bold text-[#183047]">
                        பஞ்சாங்கம் (ஐந்து அங்கங்கள்)
                      </h3>
                      <p className="text-xs text-[#8190A6]">
                        பிறந்த துல்லிய கணத்தில் பஞ்சாங்க நிலைகள்
                      </p>
                    </div>
                  </div>
                  <span className="text-[11px] font-mono font-semibold px-2 py-0.5 rounded bg-[#F2F3F5] text-[#52667E]">
                    Section A
                  </span>
                </div>

                {/* 2-Column Responsive Information Grid (Screenshot & Table Spec) */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
                  {/* 1. ராசி */}
                  <div className="p-3.5 rounded-lg border border-[#D9DEE7] bg-[#FAF8F5] flex items-center justify-between">
                    <div className="space-y-0.5">
                      <span className="text-[11px] font-bold text-[#8190A6] uppercase tracking-wider block">
                        ராசி (Moon Sign)
                      </span>
                      <span className="text-sm sm:text-base font-bold text-[#153F6B]">
                        {moon?.sign_name_tamil || getRasiNameTamil(moon?.sign_name)}
                      </span>
                    </div>
                    <span className="p-2 rounded-full bg-blue-50 text-[#153F6B]">
                      <Moon className="w-4 h-4" />
                    </span>
                  </div>

                  {/* 2. லக்கினம் */}
                  <div className="p-3.5 rounded-lg border border-[#D9DEE7] bg-[#FAF8F5] flex items-center justify-between">
                    <div className="space-y-0.5">
                      <span className="text-[11px] font-bold text-[#8190A6] uppercase tracking-wider block">
                        லக்கினம் (Ascendant)
                      </span>
                      <span className="text-sm sm:text-base font-bold text-[#153F6B]">
                        {ascendant?.sign_name_tamil || getRasiNameTamil(ascendant?.sign_name)}
                      </span>
                    </div>
                    <span className="p-2 rounded-full bg-amber-50 text-[#B4872B]">
                      <Sun className="w-4 h-4" />
                    </span>
                  </div>

                  {/* 3. நட்சத்திரம் */}
                  <div className="p-3.5 rounded-lg border border-[#D9DEE7] bg-[#FAF8F5] flex items-center justify-between">
                    <div className="space-y-0.5">
                      <span className="text-[11px] font-bold text-[#8190A6] uppercase tracking-wider block">
                        நட்சத்திரம் (Star & Pada)
                      </span>
                      <span className="text-sm sm:text-base font-bold text-[#183047]">
                        {moon?.nakshatra?.name
                          ? `${getNakshatraTamil(moon.nakshatra.name)}${moon.nakshatra.pada ? ` - பாதம் ${moon.nakshatra.pada}` : ""}`
                          : panchang?.nakshatra
                          ? getNakshatraTamil(panchang.nakshatra)
                          : "கிடைக்கவில்லை"}
                      </span>
                    </div>
                    <span className="p-2 rounded-full bg-purple-50 text-purple-600">
                      <Sparkles className="w-4 h-4" />
                    </span>
                  </div>

                  {/* 4. திதி */}
                  <div className="p-3.5 rounded-lg border border-[#D9DEE7] bg-[#FAF8F5] flex items-center justify-between">
                    <div className="space-y-0.5">
                      <span className="text-[11px] font-bold text-[#8190A6] uppercase tracking-wider block">
                        திதி (Tithi)
                      </span>
                      <span className="text-sm sm:text-base font-bold text-[#183047]">
                        {formatTithiTamil(panchang?.tithi)}
                      </span>
                    </div>
                    <span className="p-2 rounded-full bg-emerald-50 text-emerald-600">
                      <Calendar className="w-4 h-4" />
                    </span>
                  </div>

                  {/* 5. யோகம் */}
                  <div className="p-3.5 rounded-lg border border-[#D9DEE7] bg-[#FAF8F5] flex items-center justify-between">
                    <div className="space-y-0.5">
                      <span className="text-[11px] font-bold text-[#8190A6] uppercase tracking-wider block">
                        யோகம் (Yoga)
                      </span>
                      <span className="text-sm sm:text-base font-bold text-[#183047]">
                        {formatYogaTamil(panchang?.yoga?.name)}
                      </span>
                    </div>
                    <span className="p-2 rounded-full bg-sky-50 text-sky-600">
                      <Activity className="w-4 h-4" />
                    </span>
                  </div>

                  {/* 6. கரணம் */}
                  <div className="p-3.5 rounded-lg border border-[#D9DEE7] bg-[#FAF8F5] flex items-center justify-between">
                    <div className="space-y-0.5">
                      <span className="text-[11px] font-bold text-[#8190A6] uppercase tracking-wider block">
                        கரணம் (Karana)
                      </span>
                      <span className="text-sm sm:text-base font-bold text-[#183047]">
                        {formatKaranaTamil(panchang?.karana)}
                      </span>
                    </div>
                    <span className="p-2 rounded-full bg-orange-50 text-orange-600">
                      <Clock className="w-4 h-4" />
                    </span>
                  </div>
                </div>
              </div>

              {/* SECTION B: தசா இருப்பு (Dasa Balance) */}
              <div className="bg-white rounded-xl border border-[#D9DEE7] p-5 shadow-2xs space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-[#F2F3F5]">
                  <div className="flex items-center gap-2.5">
                    <span className="p-2 rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-200">
                      <Clock className="w-4 h-4" />
                    </span>
                    <div>
                      <h3 className="font-serif text-base font-bold text-[#183047]">
                        தசா இருப்பு
                      </h3>
                      <p className="text-xs text-[#8190A6]">
                        விம்சோத்தரி தசா-புக்தி இருப்பு கால அளவு (Vimshottari Dasa Balance)
                      </p>
                    </div>
                  </div>
                  <span className="text-[11px] font-mono font-semibold px-2 py-0.5 rounded bg-[#F2F3F5] text-[#52667E]">
                    Section B
                  </span>
                </div>

                {/* 2 Distinct Rows/Cards per Specification */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Card 1: பிறப்பு தசை இருப்பு */}
                  <div className="p-4 rounded-xl border border-[#D8BD80] bg-[#FAF2DE]/50 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-[#8C6D23] uppercase tracking-wider flex items-center gap-1.5">
                        <Star className="w-3.5 h-3.5 text-[#B4872B]" />
                        <span>பிறப்பு தசை இருப்பு</span>
                      </span>
                      <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-[#FAF2DE] text-[#B4872B] border border-[#D8BD80]">
                        மகா தசை
                      </span>
                    </div>
                    <div className="flex items-baseline gap-2">
                      <span className="text-xl sm:text-2xl font-bold font-mono text-[#183047]">
                        {dasaBalance.dasaLordAbbr} {dasaBalance.dasaYMD.compact}
                      </span>
                    </div>
                    <p className="text-xs text-[#52667E] pt-1 border-t border-[#D8BD80]/40">
                      {dasaBalance.dasaLordTa} மகா தசை இருப்பு —{" "}
                      <strong>{dasaBalance.dasaYMD.tamil}</strong>
                    </p>
                  </div>

                  {/* Card 2: பிறப்பு புக்தி இருப்பு */}
                  <div className="p-4 rounded-xl border border-[#BFDBFE] bg-[#EBF2FE]/60 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-[#153F6B] uppercase tracking-wider flex items-center gap-1.5">
                        <Sparkles className="w-3.5 h-3.5 text-[#153F6B]" />
                        <span>பிறப்பு புக்தி இருப்பு</span>
                      </span>
                      <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-[#EBF2FE] text-[#153F6B] border border-[#BFDBFE]">
                        அந்தர்தசை (புக்தி)
                      </span>
                    </div>
                    <div className="flex items-baseline gap-2">
                      <span className="text-xl sm:text-2xl font-bold font-mono text-[#183047]">
                        {dasaBalance.bhuktiLordAbbr} {dasaBalance.bhuktiYMD.compact}
                      </span>
                    </div>
                    <p className="text-xs text-[#52667E] pt-1 border-t border-[#BFDBFE]/60">
                      {dasaBalance.bhuktiLordTa} புக்தி இருப்பு —{" "}
                      <strong>{dasaBalance.bhuktiYMD.tamil}</strong>
                    </p>
                  </div>
                </div>
              </div>

              {/* SECTION C: பிறப்பு விவரங்கள் (Birth Details) */}
              <div className="bg-white rounded-xl border border-[#D9DEE7] p-5 shadow-2xs space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-[#F2F3F5]">
                  <div className="flex items-center gap-2.5">
                    <span className="p-2 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200">
                      <Globe className="w-4 h-4" />
                    </span>
                    <div>
                      <h3 className="font-serif text-base font-bold text-[#183047]">
                        பிறப்பு விவரங்கள் & வானியல் அளவுருக்கள்
                      </h3>
                      <p className="text-xs text-[#8190A6]">
                        துல்லிய புவியியல் மற்றும் வானியல் தரவுகள் (Birth Details & Astronomy)
                      </p>
                    </div>
                  </div>
                  <span className="text-[11px] font-mono font-semibold px-2 py-0.5 rounded bg-[#F2F3F5] text-[#52667E]">
                    Section C
                  </span>
                </div>

                {/* 10 Required Fields Grid per Specification Table */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-x-6 gap-y-3 text-xs">
                  {/* 1. பெயர் */}
                  <div className="flex items-center justify-between p-2.5 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5]/70">
                    <span className="font-semibold text-[#52667E] flex items-center gap-1.5">
                      <span>பெயர்:</span>
                    </span>
                    <span className="font-bold text-[#183047] text-sm">
                      {clientInputs.fullName || "கிடைக்கவில்லை"}
                    </span>
                  </div>

                  {/* 2. பிறந்த நேரம் */}
                  <div className="flex items-center justify-between p-2.5 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5]/70">
                    <span className="font-semibold text-[#52667E] flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5 text-[#B4872B]" />
                      <span>பிறந்த நேரம்:</span>
                    </span>
                    <span className="font-mono font-bold text-[#153F6B]">
                      {formatBirthDate(clientInputs.birthDate, "ta")}{" "}
                      {formatBirthTime(clientInputs.birthTime)}
                    </span>
                  </div>

                  {/* 3. பிறந்த இடம் */}
                  <div className="flex items-center justify-between p-2.5 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5]/70">
                    <span className="font-semibold text-[#52667E] flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-[#B4872B]" />
                      <span>பிறந்த இடம்:</span>
                    </span>
                    <span className="font-semibold text-[#183047] truncate max-w-[200px]" title={clientInputs.locationName}>
                      {clientInputs.locationName || "கிடைக்கவில்லை"}
                    </span>
                  </div>

                  {/* 4. சூரிய உதய நேரம் */}
                  <div className="flex items-center justify-between p-2.5 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5]/70">
                    <span className="font-semibold text-[#52667E] flex items-center gap-1.5">
                      <Sun className="w-3.5 h-3.5 text-amber-500" />
                      <span>சூரிய உதய நேரம்:</span>
                    </span>
                    <span className="font-mono font-bold text-amber-700">
                      {solarTimes?.sunriseTime || "கிடைக்கவில்லை"}
                    </span>
                  </div>

                  {/* 5. சூரிய அஸ்தமன நேரம் */}
                  <div className="flex items-center justify-between p-2.5 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5]/70">
                    <span className="font-semibold text-[#52667E] flex items-center gap-1.5">
                      <Moon className="w-3.5 h-3.5 text-indigo-500" />
                      <span>சூரிய அஸ்தமன நேரம்:</span>
                    </span>
                    <span className="font-mono font-bold text-indigo-700">
                      {solarTimes?.sunsetTime || "கிடைக்கவில்லை"}
                    </span>
                  </div>

                  {/* 6. அட்சாம்சம் */}
                  <div className="flex items-center justify-between p-2.5 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5]/70">
                    <span className="font-semibold text-[#52667E] flex items-center gap-1.5">
                      <span>அட்சாம்சம் (Latitude):</span>
                    </span>
                    <span className="font-mono font-bold text-[#183047]">
                      {formatLatitudeDms(clientInputs.latitude)}
                    </span>
                  </div>

                  {/* 7. தீர்க்காம்சம் */}
                  <div className="flex items-center justify-between p-2.5 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5]/70">
                    <span className="font-semibold text-[#52667E] flex items-center gap-1.5">
                      <span>தீர்க்காம்சம் (Longitude):</span>
                    </span>
                    <span className="font-mono font-bold text-[#183047]">
                      {formatLongitudeDms(clientInputs.longitude)}
                    </span>
                  </div>

                  {/* 8. நேர மண்டலம் */}
                  <div className="flex items-center justify-between p-2.5 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5]/70">
                    <span className="font-semibold text-[#52667E] flex items-center gap-1.5">
                      <span>நேர மண்டலம் (Timezone):</span>
                    </span>
                    <span className="font-mono font-semibold text-[#183047]">
                      {clientInputs.timezone
                        ? `${clientInputs.timezone} (UTC ${
                            horoscope.metadata?.utc_offset_hours !== undefined
                              ? (horoscope.metadata.utc_offset_hours >= 0 ? "+" : "") +
                                horoscope.metadata.utc_offset_hours
                              : "+05:30"
                          })`
                        : "கிடைக்கவில்லை"}
                    </span>
                  </div>

                  {/* 9. அயனாம்ச முறை */}
                  <div className="flex items-center justify-between p-2.5 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5]/70">
                    <span className="font-semibold text-[#52667E] flex items-center gap-1.5">
                      <Sliders className="w-3.5 h-3.5 text-[#8190A6]" />
                      <span>அயனாம்ச முறை:</span>
                    </span>
                    <span className="font-bold text-[#153F6B]">
                      {horoscope.metadata?.ayanamsa_name || "Lahiri"}
                    </span>
                  </div>

                  {/* 10. அயனாம்சம் */}
                  <div className="flex items-center justify-between p-2.5 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5]/70">
                    <span className="font-semibold text-[#52667E] flex items-center gap-1.5">
                      <span>அயனாம்சம் (Value):</span>
                    </span>
                    <span className="font-mono font-bold text-[#183047]">
                      {formatAyanamsaDms(horoscope.metadata?.ayanamsa_deg)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Collapsible Houses Table (Preserving full data integrity) */}
              <div className="bg-white rounded-xl border border-[#D9DEE7] p-4 shadow-2xs space-y-3">
                <button
                  type="button"
                  onClick={() => setShowHousesTable(!showHousesTable)}
                  className="w-full flex items-center justify-between text-left cursor-pointer"
                >
                  <div className="flex items-center gap-2">
                    <Layers className="w-4 h-4 text-[#153F6B]" />
                    <span className="font-serif text-sm font-bold text-[#183047]">
                      12 பாவக ஆரம்ப நிலைகள் (Bhava Cusps Table)
                    </span>
                  </div>
                  <div className="flex items-center gap-1 text-xs text-[#8190A6]">
                    <span>{showHousesTable ? "மறைக்குக" : "காண்க"}</span>
                    {showHousesTable ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </div>
                </button>
                {showHousesTable && (
                  <div className="pt-2 border-t border-[#F2F3F5]">
                    <HousesTable houses={horoscope.houses} />
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ===================================================================== */}
          {/* CATEGORY 2: சிறப்பு அம்சங்கள் (Special Features) */}
          {/* ===================================================================== */}
          {activeCategory === "special" && (
            <div className="space-y-5">
              <div className="bg-white rounded-xl border border-[#D9DEE7] p-5 shadow-2xs space-y-5">
                <div className="flex items-center justify-between pb-3 border-b border-[#F2F3F5]">
                  <div className="flex items-center gap-2.5">
                    <span className="p-2 rounded-lg bg-purple-50 text-purple-700 border border-purple-200">
                      <Sparkles className="w-4 h-4" />
                    </span>
                    <div>
                      <h3 className="font-serif text-base font-bold text-[#183047]">
                        ஜாதக சிறப்பு அம்சங்கள் (Special Astrological Features)
                      </h3>
                      <p className="text-xs text-[#8190A6]">
                        லக்னாதிபதி நிலை, வர்க்கோத்தமம் மற்றும் முக்கிய பல யோகங்கள்
                      </p>
                    </div>
                  </div>
                </div>

                {/* Grid of Key Pillars: Lagna Lord, Moon Lord, Yogakaraka */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Lagna Lord Card */}
                  <div className="p-4 rounded-xl border border-[#D9DEE7] bg-[#FAF8F5] space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-bold text-[#8190A6] uppercase tracking-wider">
                        லக்னாதிபதி
                      </span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-50 text-[#153F6B] border border-blue-200">
                        1-ஆம் பாவாதிபதி
                      </span>
                    </div>
                    <div className="text-base font-bold text-[#153F6B]">
                      {specialFeatures.lagnaLordTa}
                    </div>
                    <p className="text-xs text-[#52667E] leading-relaxed">
                      {specialFeatures.lagnaLordSignTa} ராசியில், {specialFeatures.lagnaLordHouse}-ஆம் பாவத்தில் சஞ்சரிக்கிறார்.
                    </p>
                  </div>

                  {/* Moon Sign Lord Card */}
                  <div className="p-4 rounded-xl border border-[#D9DEE7] bg-[#FAF8F5] space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-bold text-[#8190A6] uppercase tracking-wider">
                        ராசிநாதன்
                      </span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
                        ஜன்ம ராசி அதிபதி
                      </span>
                    </div>
                    <div className="text-base font-bold text-indigo-900">
                      {specialFeatures.moonLordTa}
                    </div>
                    <p className="text-xs text-[#52667E] leading-relaxed">
                      {specialFeatures.moonLordSignTa} ராசியில், {specialFeatures.moonLordHouse}-ஆம் பாவத்தில் சஞ்சரிக்கிறார்.
                    </p>
                  </div>

                  {/* Yogakaraka Planet Card */}
                  <div className="p-4 rounded-xl border border-[#D8BD80] bg-[#FAF2DE]/50 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-bold text-[#8C6D23] uppercase tracking-wider">
                        யோககாரகன்
                      </span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#FAF2DE] text-[#B4872B] border border-[#D8BD80]">
                        கேந்திர-திரிகோணாதிபதி
                      </span>
                    </div>
                    <div className="text-base font-bold text-[#183047]">
                      {lagnaInfo.yogakarakaTa || "தனி யோககாரகன் இல்லை"}
                    </div>
                    <p className="text-xs text-[#52667E] leading-relaxed">
                      {lagnaInfo.specialNoteTa}
                    </p>
                  </div>
                </div>

                {/* Vargottama & Planetary Dignity Summary */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                  <div className="p-4 rounded-xl border border-[#D9DEE7] bg-white space-y-2">
                    <h4 className="text-xs font-bold text-[#183047] flex items-center gap-1.5">
                      <Award className="w-4 h-4 text-[#B4872B]" />
                      <span>வர்க்கோத்தம கிரகங்கள் (Vargottama)</span>
                    </h4>
                    {specialFeatures.vargottamaList.length > 0 ? (
                      <div className="flex flex-wrap gap-2 pt-1">
                        {specialFeatures.vargottamaList.map((p, i) => (
                          <span
                            key={i}
                            className="px-2.5 py-1 rounded-lg text-xs font-bold bg-amber-50 text-amber-900 border border-amber-300"
                          >
                            ⭐ {p} (D1 & D9 சம ராசி)
                          </span>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-[#8190A6]">
                        இந்த ஜாதகத்தில் கிரகங்கள் வர்க்கோத்தமம் பெறவில்லை.
                      </p>
                    )}
                  </div>

                  <div className="p-4 rounded-xl border border-[#D9DEE7] bg-white space-y-2">
                    <h4 className="text-xs font-bold text-[#183047] flex items-center gap-1.5">
                      <Star className="w-4 h-4 text-[#153F6B]" />
                      <span>ஆட்சி / உச்ச / நீச நிலைகள்</span>
                    </h4>
                    <div className="text-xs space-y-1 text-[#52667E]">
                      <div>
                        ஆட்சி பெற்ற கிரகங்கள்:{" "}
                        <strong className="text-[#183047]">
                          {specialFeatures.ownSignList.length > 0
                            ? specialFeatures.ownSignList.join(", ")
                            : "இல்லை"}
                        </strong>
                      </div>
                      <div>
                        உச்சம் பெற்ற கிரகங்கள்:{" "}
                        <strong className="text-emerald-700">
                          {specialFeatures.exaltedList.length > 0
                            ? specialFeatures.exaltedList.join(", ")
                            : "இல்லை"}
                        </strong>
                      </div>
                      <div>
                        நீசம் பெற்ற கிரகங்கள்:{" "}
                        <strong className="text-rose-700">
                          {specialFeatures.debilitatedList.length > 0
                            ? specialFeatures.debilitatedList.join(", ")
                            : "இல்லை"}
                        </strong>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Classical Vedic Yogas list if available */}
                <div className="pt-2 space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-[#183047] uppercase tracking-wider">
                      ஜாதகத்தில் அமைந்த முக்கிய யோகங்கள் (Vedic Yogas)
                    </h4>
                    {onCalculateExtensions && (
                      <button
                        type="button"
                        onClick={onCalculateExtensions}
                        disabled={isCalculatingExtensions}
                        className="inline-flex items-center gap-1 text-[11px] font-bold text-[#153F6B] hover:underline cursor-pointer disabled:opacity-50"
                      >
                        <RefreshCw className={`w-3 h-3 ${isCalculatingExtensions ? "animate-spin" : ""}`} />
                        <span>{isCalculatingExtensions ? "கணக்கிடப்படுகிறது…" : "மறுகணக்கீடு செய்க"}</span>
                      </button>
                    )}
                  </div>

                  {specialFeatures.activeYogas.length > 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {specialFeatures.activeYogas.map((yoga, i) => (
                        <div
                          key={i}
                          className="p-3 rounded-lg border border-[#D9DEE7] bg-[#FAF8F5] space-y-1"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-xs text-[#153F6B]">
                              ✨ {yoga.nameTa}
                            </span>
                            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-200">
                              சுப யோகம்
                            </span>
                          </div>
                          <p className="text-[11px] text-[#52667E] leading-relaxed">
                            {yoga.description}
                          </p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-4 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5] text-xs text-[#8190A6] text-center">
                      விசேஷ யோகங்களைக் காண &quot;மறுகணக்கீடு செய்க&quot; பொத்தானை அழுத்தவும்.
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* ===================================================================== */}
          {/* CATEGORY 3: சுப & பாவ கிரகங்கள் */}
          {/* ===================================================================== */}
          {activeCategory === "benefic_malefic" && (
            <div className="space-y-5">
              <div className="bg-white rounded-xl border border-[#D9DEE7] p-5 shadow-2xs space-y-5">
                <div className="flex items-center justify-between pb-3 border-b border-[#F2F3F5]">
                  <div className="flex items-center gap-2.5">
                    <span className="p-2 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200">
                      <ShieldCheck className="w-4 h-4" />
                    </span>
                    <div>
                      <h3 className="font-serif text-base font-bold text-[#183047]">
                        சுப & பாவ கிரகங்கள் (Benefic & Malefic Planets)
                      </h3>
                      <p className="text-xs text-[#8190A6]">
                        {ascendant?.sign_name_tamil || "தனுசு"} லக்னத்திற்கான தர்ம, அர்த்த, காம, மோட்ச கிரக வகைப்பாடு
                      </p>
                    </div>
                  </div>
                </div>

                {/* 3 Pillars: Functional Benefics, Functional Malefics, Neutrals */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Functional Benefics */}
                  <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/60 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-emerald-900 uppercase tracking-wider flex items-center gap-1.5">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        <span>லக்ன சுபர்கள்</span>
                      </span>
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800">
                        Benefics
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {lagnaInfo.beneficsTa.map((p, i) => (
                        <span
                          key={i}
                          className="px-2.5 py-1 rounded-lg text-xs font-bold bg-white text-emerald-900 border border-emerald-300 shadow-2xs"
                        >
                          🌟 {p}
                        </span>
                      ))}
                    </div>
                    <p className="text-[11px] text-emerald-800 pt-1">
                      திரிகோண (1, 5, 9) மற்றும் கேந்திர அதிபதிகளாகி வாழ்வை மேம்படுத்துவர்.
                    </p>
                  </div>

                  {/* Functional Malefics */}
                  <div className="p-4 rounded-xl border border-rose-200 bg-rose-50/60 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-rose-900 uppercase tracking-wider flex items-center gap-1.5">
                        <AlertCircle className="w-4 h-4 text-rose-600" />
                        <span>லக்ன பாவிகள்</span>
                      </span>
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-rose-100 text-rose-800">
                        Malefics
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {lagnaInfo.maleficsTa.map((p, i) => (
                        <span
                          key={i}
                          className="px-2.5 py-1 rounded-lg text-xs font-bold bg-white text-rose-900 border border-rose-300 shadow-2xs"
                        >
                          ⚠️ {p}
                        </span>
                      ))}
                    </div>
                    <p className="text-[11px] text-rose-800 pt-1">
                      திரிஷடாய (3, 6, 11) அல்லது விரைய அதிபதிகளாகி தடைகளைத் தருவர்.
                    </p>
                  </div>

                  {/* Neutrals & Yogakaraka */}
                  <div className="p-4 rounded-xl border border-amber-200 bg-amber-50/60 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-amber-900 uppercase tracking-wider flex items-center gap-1.5">
                        <HelpCircle className="w-4 h-4 text-amber-600" />
                        <span>சமர்கள் & யோககாரகன்</span>
                      </span>
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-100 text-amber-800">
                        Neutral / Yoga
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {lagnaInfo.neutralsTa.map((p, i) => (
                        <span
                          key={i}
                          className="px-2.5 py-1 rounded-lg text-xs font-bold bg-white text-amber-900 border border-amber-300 shadow-2xs"
                        >
                          ⚖️ {p}
                        </span>
                      ))}
                    </div>
                    <p className="text-[11px] text-amber-800 pt-1">
                      {lagnaInfo.yogakarakaTa
                        ? `யோககாரகன்: ${lagnaInfo.yogakarakaTa}`
                        : "சேரும் கிரகம் மற்றும் பாவ நிலைக்கு ஏற்ப பலன் தருவர்."}
                    </p>
                  </div>
                </div>

                {/* Natural Benefics & Malefics Reference */}
                <div className="p-4 rounded-xl border border-[#D9DEE7] bg-[#FAF8F5] space-y-2 text-xs">
                  <div className="font-bold text-[#183047] flex items-center gap-2">
                    <Sparkles className="w-3.5 h-3.5 text-[#B4872B]" />
                    <span>இயற்கை சுபர்கள் vs இயற்கை பாவிகள் (Natural Planetary Natures)</span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-[#52667E] pt-1">
                    <div>
                      <strong className="text-emerald-700">இயற்கை சுபர்கள்:</strong> குரு, சுக்கிரன், வளர்பிறை சந்திரன், தனித்த புதன்.
                    </div>
                    <div>
                      <strong className="text-rose-700">இயற்கை பாவிகள்:</strong> சனி, செவ்வாய், சூரியன் (க்ரூர கிரகம்), ராகு, கேது.
                    </div>
                  </div>
                </div>

                {/* Full 9-Planets Classification Table */}
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-[#183047] uppercase tracking-wider">
                    ஜாதக கிரகங்களின் சுப/பாவ வகைப்பாடு அட்டவணை
                  </h4>
                  <div className="overflow-x-auto rounded-lg border border-[#D9DEE7]">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-[#F2F3F5] text-[#183047] font-bold border-b border-[#D9DEE7]">
                        <tr>
                          <th className="p-2.5">கிரகம்</th>
                          <th className="p-2.5">ராசி & பாகை</th>
                          <th className="p-2.5">பாவம்</th>
                          <th className="p-2.5">லக்னத் தன்மை</th>
                          <th className="p-2.5">இயற்கைத் தன்மை</th>
                          <th className="p-2.5">நிலை (Dignity)</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#F2F3F5] bg-white">
                        {(horoscope.planets || []).map((p, idx) => {
                          const pName = p.name;
                          const pNameTa = getPlanetNameTamil(pName);
                          const isBenefic = lagnaInfo.benefics.includes(pName);
                          const isMalefic = lagnaInfo.malefics.includes(pName);
                          const isYogakaraka = lagnaInfo.yogakaraka?.toLowerCase() === pName.toLowerCase();

                          const functionalTag = isYogakaraka
                            ? { label: "யோககாரகன்", color: "bg-amber-50 text-amber-800 border-amber-300" }
                            : isBenefic
                            ? { label: "சுபர்", color: "bg-emerald-50 text-emerald-800 border-emerald-300" }
                            : isMalefic
                            ? { label: "பாவி", color: "bg-rose-50 text-rose-800 border-rose-300" }
                            : { label: "சமர்", color: "bg-slate-50 text-slate-700 border-slate-300" };

                          const natNature =
                            ["Jupiter", "Venus"].includes(pName) || (pName === "Moon")
                              ? "இயற்கை சுபர்"
                              : pName === "Mercury"
                              ? "இயற்கை சமர்"
                              : "இயற்கை பாவி";

                          return (
                            <tr key={idx} className="hover:bg-[#FAF8F5] transition-colors">
                              <td className="p-2.5 font-bold text-[#183047] flex items-center gap-1.5">
                                <span>{pNameTa}</span>
                                <span className="text-[10px] text-[#8190A6]">({pName})</span>
                              </td>
                              <td className="p-2.5">
                                {p.sign_name_tamil || getRasiNameTamil(p.sign_name)} {formatDms(p.degree_in_sign)}
                              </td>
                              <td className="p-2.5 font-bold text-[#153F6B]">
                                {p.house ? `${p.house}-ஆம் பாவம்` : "—"}
                              </td>
                              <td className="p-2.5">
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${functionalTag.color}`}>
                                  {functionalTag.label}
                                </span>
                              </td>
                              <td className="p-2.5 text-[#52667E]">
                                {natNature}
                              </td>
                              <td className="p-2.5 font-semibold text-[#183047]">
                                {p.is_retrograde ? "வக்ரம் (R)" : "நேர்கதி"}
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
          )}

          {/* ===================================================================== */}
          {/* CATEGORY 4: ஷட்பலம் & அவஸ்தை */}
          {/* ===================================================================== */}
          {activeCategory === "shadbala_avastha" && (
            <div className="space-y-6">
              {/* Part 1: ஷட்பலம் (Shadbala) */}
              <div className="bg-white rounded-xl border border-[#D9DEE7] p-5 shadow-2xs space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-[#F2F3F5]">
                  <div className="flex items-center gap-2.5">
                    <span className="p-2 rounded-lg bg-blue-50 text-[#153F6B] border border-blue-200">
                      <Activity className="w-4 h-4" />
                    </span>
                    <div>
                      <h3 className="font-serif text-base font-bold text-[#183047]">
                        ஷட்பலம் (ஆறு வகை கிரக பலம் — Six-Fold Strength)
                      </h3>
                      <p className="text-xs text-[#8190A6]">
                        ஸ்தான, திக், கால, சேஷ்டா, நைசர்கிக, த்ரிக் பலன்களின் விகிதம் (BPHS Ch. 23)
                      </p>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={handleFetchShadbala}
                    disabled={isLoadingShadbala}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#D9DEE7] bg-[#F2F3F5] text-xs font-semibold text-[#153F6B] hover:bg-[#E2E8F0] cursor-pointer disabled:opacity-50"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${isLoadingShadbala ? "animate-spin" : ""}`} />
                    <span>{isLoadingShadbala ? "கணக்கிடப்படுகிறது…" : "மீண்டும் கணக்கிடு"}</span>
                  </button>
                </div>

                {isLoadingShadbala && !shadbalaData && (
                  <div className="p-8 text-center space-y-3 bg-[#FAF8F5] rounded-xl border border-[#E2DCD5]">
                    <RefreshCw className="w-6 h-6 text-[#153F6B] animate-spin mx-auto" />
                    <p className="text-xs font-bold text-[#183047]">
                      சுவிஸ் எபிமெரிஸ் மூலம் ஷட்பல பலன்கள் துல்லியமாகக் கணக்கிடப்படுகின்றன…
                    </p>
                  </div>
                )}

                {shadbalaError && (
                  <div className="p-3 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
                    <span>{shadbalaError}</span>
                  </div>
                )}

                {shadbalaData && shadbalaData.planets && (
                  <div className="space-y-4">
                    {/* Strongest & Weakest Badges */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div className="p-3 rounded-lg border border-emerald-200 bg-emerald-50 flex items-center justify-between">
                        <div>
                          <span className="text-[10px] font-bold text-emerald-800 uppercase tracking-wider block">
                            மிக வலிமையான கிரகம் (Rank #1)
                          </span>
                          <span className="text-base font-bold text-emerald-950">
                            🏆 {getPlanetNameTamil(shadbalaData.strongest_planet)} ({shadbalaData.strongest_planet})
                          </span>
                        </div>
                        <span className="text-xs font-bold px-2 py-1 rounded bg-emerald-200 text-emerald-900">
                          முழு பலம்
                        </span>
                      </div>

                      <div className="p-3 rounded-lg border border-slate-200 bg-slate-50 flex items-center justify-between">
                        <div>
                          <span className="text-[10px] font-bold text-slate-600 uppercase tracking-wider block">
                            குறைந்த பலம் கொண்ட கிரகம் (Rank #7)
                          </span>
                          <span className="text-base font-bold text-slate-800">
                            {getPlanetNameTamil(shadbalaData.weakest_planet)} ({shadbalaData.weakest_planet})
                          </span>
                        </div>
                        <span className="text-xs font-bold px-2 py-1 rounded bg-slate-200 text-slate-700">
                          பரிகாரம் நலம்
                        </span>
                      </div>
                    </div>

                    {/* Shadbala Table */}
                    <div className="overflow-x-auto rounded-lg border border-[#D9DEE7]">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-[#F2F3F5] text-[#183047] font-bold border-b border-[#D9DEE7]">
                          <tr>
                            <th className="p-2.5">கிரகம்</th>
                            <th className="p-2.5">ஸ்தான பலம்</th>
                            <th className="p-2.5">திக் பலம்</th>
                            <th className="p-2.5">கால பலம்</th>
                            <th className="p-2.5">சேஷ்டா பலம்</th>
                            <th className="p-2.5">மொத்த பலம் (ரூபா)</th>
                            <th className="p-2.5">தேவையான பலம்</th>
                            <th className="p-2.5">விகிதம் (Ratio)</th>
                            <th className="p-2.5">முடிவு</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#F2F3F5] bg-white">
                          {shadbalaData.planets.map((pl, idx) => {
                            const isStrong = pl.is_strong;
                            return (
                              <tr key={idx} className="hover:bg-[#FAF8F5] transition-colors">
                                <td className="p-2.5 font-bold text-[#183047]">
                                  {getPlanetNameTamil(pl.planet)}{" "}
                                  <span className="text-[10px] text-[#8190A6]">({pl.planet})</span>
                                </td>
                                <td className="p-2.5 font-mono">{Math.round(pl.sthana_bala.total)}</td>
                                <td className="p-2.5 font-mono">{Math.round(pl.dig_bala)}</td>
                                <td className="p-2.5 font-mono">{Math.round(pl.kala_bala.total)}</td>
                                <td className="p-2.5 font-mono">{Math.round(pl.cheshta_bala)}</td>
                                <td className="p-2.5 font-mono font-bold text-[#153F6B]">
                                  {pl.total_rupas.toFixed(2)} ரூபா ({Math.round(pl.total_virupas)} வி)
                                </td>
                                <td className="p-2.5 font-mono text-[#52667E]">
                                  {Math.round(pl.required_virupas)} வி
                                </td>
                                <td className="p-2.5 font-mono font-bold">
                                  {pl.ratio.toFixed(2)}x
                                </td>
                                <td className="p-2.5">
                                  <span
                                    className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                                      isStrong
                                        ? "bg-emerald-50 text-emerald-800 border-emerald-300"
                                        : "bg-amber-50 text-amber-800 border-amber-300"
                                    }`}
                                  >
                                    {isStrong ? "பலம்" : "பலவீனம்"}
                                  </span>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>

              {/* Part 2: அவஸ்தைகள் (Planetary Avasthas) */}
              <div className="bg-white rounded-xl border border-[#D9DEE7] p-5 shadow-2xs space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-[#F2F3F5]">
                  <div className="flex items-center gap-2.5">
                    <span className="p-2 rounded-lg bg-purple-50 text-purple-700 border border-purple-200">
                      <Zap className="w-4 h-4" />
                    </span>
                    <div>
                      <h3 className="font-serif text-base font-bold text-[#183047]">
                        கிரக அவஸ்தைகள் (Planetary States per BPHS)
                      </h3>
                      <p className="text-xs text-[#8190A6]">
                        பாலாதி (வயது), ஜாக்கிரதாதி (விழிப்புணர்வு) மற்றும் தீப்தாதி (குண) அவஸ்தைகள்
                      </p>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
                  {avasthas.map((av, idx) => (
                    <div
                      key={idx}
                      className="p-3.5 rounded-xl border border-[#D9DEE7] bg-[#FAF8F5] space-y-2.5"
                    >
                      <div className="flex items-center justify-between border-b border-[#E2DCD5] pb-2">
                        <span className="font-bold text-sm text-[#153F6B]">
                          {av.planetTa} ({av.planet})
                        </span>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-50 text-[#153F6B] border border-blue-200">
                          {av.baladi.fruitPercent} பலன்
                        </span>
                      </div>

                      {/* 1. பாலாதி அவஸ்தை */}
                      <div className="space-y-0.5 text-xs">
                        <span className="text-[10px] font-bold text-[#8190A6] uppercase tracking-wider block">
                          பாலாதி அவஸ்தை:
                        </span>
                        <div className="font-bold text-[#183047] flex items-center justify-between">
                          <span>{av.baladi.stateTa}</span>
                          <span className="text-[10px] text-[#8190A6]">({av.baladi.stateEn})</span>
                        </div>
                        <p className="text-[11px] text-[#52667E]">{av.baladi.meaningTa}</p>
                      </div>

                      {/* 2. ஜாக்கிரதாதி அவஸ்தை */}
                      <div className="space-y-0.5 text-xs pt-1 border-t border-[#F2F3F5]">
                        <span className="text-[10px] font-bold text-[#8190A6] uppercase tracking-wider block">
                          ஜாக்கிரதாதி அவஸ்தை:
                        </span>
                        <div className="font-bold text-[#183047]">
                          {av.jagradadi.stateTa}
                        </div>
                        <p className="text-[11px] text-[#52667E]">{av.jagradadi.meaningTa}</p>
                      </div>

                      {/* 3. தீப்தாதி அவஸ்தை */}
                      <div className="space-y-0.5 text-xs pt-1 border-t border-[#F2F3F5]">
                        <span className="text-[10px] font-bold text-[#8190A6] uppercase tracking-wider block">
                          தீப்தாதி அவஸ்தை:
                        </span>
                        <div className="font-bold text-purple-900">
                          {av.deepthadi.stateTa}
                        </div>
                        <p className="text-[11px] text-[#52667E]">{av.deepthadi.meaningTa}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* ===================================================================== */}
          {/* CATEGORY 5: பெயர்ச்சி (கோச்சாரம்) */}
          {/* ===================================================================== */}
          {activeCategory === "transit" && (
            <div className="space-y-5">
              <div className="bg-white rounded-xl border border-[#D9DEE7] p-5 shadow-2xs space-y-5">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-[#F2F3F5]">
                  <div className="flex items-center gap-2.5">
                    <span className="p-2 rounded-lg bg-orange-50 text-orange-700 border border-orange-200">
                      <RotateCw className="w-4 h-4" />
                    </span>
                    <div>
                      <h3 className="font-serif text-base font-bold text-[#183047]">
                        பெயர்ச்சி பலன்கள் (கோச்சாரம் — Transit Analysis)
                      </h3>
                      <p className="text-xs text-[#8190A6]">
                        ஜன்ம ராசி ({moon?.sign_name_tamil || getRasiNameTamil(moon?.sign_name)}) அடிப்படையிலான தற்போதைய கோசார பலன்கள்
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-2">
                    <Link
                      href="/tools/transit-watch"
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#D9DEE7] bg-[#F2F3F5] hover:bg-[#E2E8F0] text-xs font-bold text-[#153F6B] transition-colors"
                    >
                      <span>முழு கோசார கடிகாரம்</span>
                      <ExternalLink className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>

                {/* Date Controls & Refresh Bar */}
                <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5]">
                  <div className="flex flex-wrap items-center gap-2.5">
                    <span className="text-xs font-bold text-[#183047] flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 text-[#B4872B]" />
                      <span>கோசார தேதி:</span>
                    </span>
                    <input
                      type="date"
                      value={transitDate}
                      onChange={(e) => setTransitDate(e.target.value)}
                      className="px-2.5 py-1 text-xs border border-[#D9DEE7] rounded-md bg-white text-[#183047] font-mono focus:outline-none focus:ring-1 focus:ring-[#153F6B]"
                    />
                    <button
                      type="button"
                      onClick={() => handleFetchTransit(transitDate)}
                      disabled={isLoadingTransit}
                      className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-[#153F6B] text-white text-xs font-bold hover:bg-[#1F548A] transition-colors disabled:opacity-50 cursor-pointer"
                    >
                      <RefreshCw className={`w-3 h-3 ${isLoadingTransit ? "animate-spin" : ""}`} />
                      <span>{isLoadingTransit ? "கணக்கிடப்படுகிறது…" : "கோசாரம் காண்க"}</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        const today = new Date();
                        const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;
                        setTransitDate(todayStr);
                        handleFetchTransit(todayStr);
                      }}
                      className="px-2.5 py-1 rounded-md border border-[#D9DEE7] bg-white text-xs font-semibold text-[#52667E] hover:text-[#183047] hover:bg-[#F2F3F5] transition-colors cursor-pointer"
                    >
                      இன்று (Today)
                    </button>
                  </div>

                  <span className="text-[11px] text-[#8190A6]">
                    சுவிஸ் எபிமெரிஸ் கணிப்பு
                  </span>
                </div>

                {/* Loading State */}
                {isLoadingTransit && (
                  <div className="p-8 text-center space-y-3 bg-[#FAF8F5] rounded-xl border border-[#E2DCD5]">
                    <RefreshCw className="w-6 h-6 text-[#153F6B] animate-spin mx-auto" />
                    <p className="text-xs font-bold text-[#183047]">
                      சுவிஸ் எபிமெரிஸ் மூலம் {transitDate} தேதிக்கான துல்லிய கோசார கிரக நிலைகள் கணக்கிடப்படுகின்றன…
                    </p>
                  </div>
                )}

                {/* Error State */}
                {transitError && (
                  <div className="p-3 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
                      <span>{transitError}</span>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleFetchTransit(transitDate)}
                      className="px-2.5 py-1 rounded bg-amber-200 text-amber-900 font-bold hover:bg-amber-300"
                    >
                      மீண்டும் முயற்சிக்கவும்
                    </button>
                  </div>
                )}

                {/* Empty State when not loading and no transit data */}
                {!isLoadingTransit && !transitError && !transitEvaluations && (
                  <div className="p-8 text-center space-y-3 bg-[#FAF8F5] rounded-xl border border-[#E2DCD5]">
                    <RotateCw className="w-8 h-8 text-[#8190A6] mx-auto opacity-60" />
                    <h4 className="text-sm font-bold text-[#183047]">
                      கோச்சார விவரங்கள் தற்சமயம் கிடைக்கவில்லை
                    </h4>
                    <p className="text-xs text-[#52667E] max-w-md mx-auto">
                      தற்போதைய கோசார கிரக நிலைகளைக் கணக்கிட கீழே உள்ள பொத்தானை அழுத்தவும்.
                    </p>
                    <button
                      type="button"
                      onClick={() => handleFetchTransit(transitDate)}
                      className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-[#153F6B] text-white text-xs font-bold hover:bg-[#1F548A] transition-colors cursor-pointer"
                    >
                      <RefreshCw className="w-3.5 h-3.5" />
                      <span>கோசாரம் கணக்கிடுக</span>
                    </button>
                  </div>
                )}

                {/* Loaded Content: Spotlight Cards + Table */}
                {!isLoadingTransit && transitEvaluations && (
                  <div className="space-y-5">
                    {/* Major Transits Spotlight Cards: Guru, Sani, Rahu-Ketu */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {/* Guru Peyarchi */}
                      {(() => {
                        const guru = transitEvaluations.find((p) => p.planet === "Jupiter");
                        if (!guru) return null;
                        const h = guru.houseFromMoon;
                        let text = "";
                        if (h === 1) text = `ஜன்ம ராசியில் குரு சஞ்சரிப்பதால் (${guru.transitSign}) மன அமைதி, ஆன்மீக நாட்டம் மற்றும் புதிய முயற்சிகளில் நிதானம் தேவை.`;
                        else if (h === 2) text = `ராசிக்கு 2-ஆம் இடமான தன ஸ்தானத்தில் குரு (${guru.transitSign}) சஞ்சரிப்பது தனவரவு, குடும்ப மகிழ்ச்சி மற்றும் வாக்கு மேன்மையை அருளும்.`;
                        else if (h === 5) text = `ராசிக்கு 5-ஆம் இடமான பூர்வ புண்ணிய ஸ்தானத்தில் குரு (${guru.transitSign}) சஞ்சரிப்பது புத்திர பாக்கியம், அதிர்ஷ்டம் மற்றும் சுப காரியங்களை நல்கும்.`;
                        else if (h === 7) text = `ராசிக்கு 7-ஆம் இடமான களத்திர ஸ்தானத்தில் குரு (${guru.transitSign}) சஞ்சரிப்பது திருமண சுபகாரியம், கூட்டாண்மை மேன்மை மற்றும் வெற்றியைத் தரும்.`;
                        else if (h === 9) text = `ராசிக்கு 9-ஆம் இடமான பாக்கிய ஸ்தானத்தில் குரு (${guru.transitSign}) சஞ்சரிப்பது தந்தை வழி நலம், பாக்கிய விருத்தி, மற்றும் பெரியோரின் ஆசியை அருளும்.`;
                        else if (h === 11) text = `ராசிக்கு 11-ஆம் இடமான லாப ஸ்தானத்தில் குரு (${guru.transitSign}) சஞ்சரிப்பது பெரும் பொருளாதார முன்னேற்றம், லாபம் மற்றும் சகல காரிய வெற்றியைத் தரும்.`;
                        else text = `ராசிக்கு ${h}-ஆம் இடத்தில் குரு பகவான் (${guru.transitSign}) சஞ்சரிக்கும் காலம். வழிபாடும் நிதானமும் நற்பலன்களைத் தரும்.`;

                        return (
                          <div className="p-4 rounded-xl border border-amber-300 bg-amber-50/50 space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="text-xs font-bold text-amber-950 flex items-center gap-1.5">
                                <Sparkles className="w-3.5 h-3.5 text-amber-600" />
                                <span>குரு பெயர்ச்சி (Jupiter)</span>
                              </span>
                              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-100 text-amber-800">
                                {h}-ஆம் இடம்
                              </span>
                            </div>
                            <div className="text-sm font-bold text-[#183047]">
                              {guru.transitSign} ராசியில் சஞ்சாரம் ({guru.degFormatted})
                            </div>
                            <p className="text-xs text-[#52667E] leading-relaxed">
                              {text}
                            </p>
                          </div>
                        );
                      })()}

                      {/* Sani Peyarchi & Sade Sati Status */}
                      {(() => {
                        const sani = transitEvaluations.find((p) => p.planet === "Saturn");
                        if (!sani) return null;
                        const h = sani.houseFromMoon;
                        let badge = `${h}-ஆம் இடம்`;
                        let text = "";
                        if (h === 12) {
                          badge = "12-ஆம் இடம் (விரையச் சனி)";
                          text = `ராசிக்கு 12-ஆம் இடத்தில் சனி (${sani.transitSign}) சஞ்சரிக்கும் விரையச் சனி காலம் (ஏழரை சனியின் ஆரம்பம்). சுப விரயங்களும் இறை வழிபாடும் நலம் பயக்கும்.`;
                        } else if (h === 1) {
                          badge = "1-ஆம் இடம் (ஜன்மச் சனி)";
                          text = `ஜன்ம ராசியில் சனி பகவான் (${sani.transitSign}) சஞ்சரிக்கும் ஜன்மச் சனி காலம் (ஏழரை சனியின் நடுப்பகுதி). பொறுமை, ஆரோக்கிய பராமரிப்பு மற்றும் விழிப்புணர்வு அவசியம்.`;
                        } else if (h === 2) {
                          badge = "2-ஆம் இடம் (பாதச் சனி)";
                          text = `ராசிக்கு 2-ஆம் இடத்தில் சனி (${sani.transitSign}) சஞ்சரிக்கும் பாதச் சனி காலம் (ஏழரை சனியின் நிறைவு). பொருளாதார வரவில் நிதானமும் குடும்ப அமைதியும் பேணல் நன்று.`;
                        } else if (h === 8) {
                          badge = "8-ஆம் இடம் (அஷ்டம சனி)";
                          text = `ராசிக்கு 8-ஆம் இடத்தில் சனி (${sani.transitSign}) சஞ்சரிக்கும் அஷ்டம சனி காலம். உடல் நலனில் அக்கறையும், நிதி சார்ந்த முடிவுகளில் நிதானமும் அவசியம்.`;
                        } else if (h === 4) {
                          badge = "4-ஆம் இடம் (அர்த்தாஷ்டம சனி)";
                          text = `ராசிக்கு 4-ஆம் இடத்தில் சனி (${sani.transitSign}) சஞ்சரிக்கும் அர்த்தாஷ்டம சனி காலம். சுக ஸ்தானத்தில் கவனம் மற்றும் தாயார் நலனில் அக்கறை தேவை.`;
                        } else if (h === 7) {
                          badge = "7-ஆம் இடம் (கண்ட சனி)";
                          text = `ராசிக்கு 7-ஆம் இடத்தில் சனி (${sani.transitSign}) சஞ்சரிக்கும் கண்ட சனி காலம். கூட்டாண்மை மற்றும் உறவுகளில் பொறுமை அவசியம்.`;
                        } else if ([3, 6, 11].includes(h)) {
                          badge = `${h}-ஆம் இடம் (சுப சனி)`;
                          text = `ராசிக்கு ${h}-ஆம் இடமான உபஜெய ஸ்தானத்தில் சனி (${sani.transitSign}) சஞ்சரிப்பது மிகுந்த மன தைரியம், கடன்/நோய் எதிர்ப்பாற்றல் மற்றும் பெரும் வெற்றியைத் தரும்.`;
                        } else {
                          text = `ராசிக்கு ${h}-ஆம் இடத்தில் சனி பகவான் (${sani.transitSign}) சஞ்சரிக்கும் காலம். சனீஸ்வர வழிபாடு நற்பலன்களைத் தரும்.`;
                        }

                        return (
                          <div className="p-4 rounded-xl border border-indigo-200 bg-indigo-50/50 space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="text-xs font-bold text-indigo-950 flex items-center gap-1.5">
                                <Clock className="w-3.5 h-3.5 text-indigo-600" />
                                <span>சனி பெயர்ச்சி (Saturn)</span>
                              </span>
                              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-indigo-100 text-indigo-800">
                                {badge}
                              </span>
                            </div>
                            <div className="text-sm font-bold text-[#183047]">
                              {sani.transitSign} ராசியில் சஞ்சாரம் ({sani.degFormatted})
                            </div>
                            <p className="text-xs text-[#52667E] leading-relaxed">
                              {text}
                            </p>
                          </div>
                        );
                      })()}

                      {/* Rahu - Ketu Peyarchi */}
                      {(() => {
                        const rahu = transitEvaluations.find((p) => p.planet === "Rahu");
                        const ketu = transitEvaluations.find((p) => p.planet === "Ketu");
                        if (!rahu || !ketu) return null;

                        return (
                          <div className="p-4 rounded-xl border border-purple-200 bg-purple-50/50 space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="text-xs font-bold text-purple-950 flex items-center gap-1.5">
                                <Compass className="w-3.5 h-3.5 text-purple-600" />
                                <span>ராகு-கேது பெயர்ச்சி</span>
                              </span>
                              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-purple-100 text-purple-800">
                                {rahu.houseFromMoon} / {ketu.houseFromMoon} அச்சு
                              </span>
                            </div>
                            <div className="text-sm font-bold text-[#183047]">
                              {rahu.transitSign} / {ketu.transitSign} சஞ்சாரம்
                            </div>
                            <p className="text-xs text-[#52667E] leading-relaxed">
                              ராசிக்கு {rahu.houseFromMoon}-ஆம் இடத்தில் ராகுவும் ({rahu.transitSign}), {ketu.houseFromMoon}-ஆம் இடத்தில் கேதுவும் ({ketu.transitSign}) சஞ்சரிக்கின்றனர். {rahu.natureTa} ராகு மற்றும் {ketu.natureTa} கேது சஞ்சார பலன்கள்.
                            </p>
                          </div>
                        );
                      })()}
                    </div>

                    {/* Complete Gochara Table */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h4 className="text-xs font-bold text-[#183047] uppercase tracking-wider">
                          கோசார கிரக நிலைகள் அட்டவணை ({transitDate} — Gochara Planetary Positions)
                        </h4>
                        <span className="text-[11px] text-[#52667E]">
                          ஜன்ம ராசி: <strong>{moon?.sign_name_tamil || getRasiNameTamil(moon?.sign_name)}</strong>
                        </span>
                      </div>
                      <div className="overflow-x-auto rounded-lg border border-[#D9DEE7]">
                        <table className="w-full text-left text-xs">
                          <thead className="bg-[#F2F3F5] text-[#183047] font-bold border-b border-[#D9DEE7]">
                            <tr>
                              <th className="p-2.5">கிரகம்</th>
                              <th className="p-2.5">கோசார ராசி & பாகை</th>
                              <th className="p-2.5">ராசியிலிருந்து பாவம்</th>
                              <th className="p-2.5">லக்னத்திலிருந்து பாவம்</th>
                              <th className="p-2.5">இயக்கம்</th>
                              <th className="p-2.5">கோசார பலன் நிலை</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-[#F2F3F5] bg-white">
                            {transitEvaluations.map((tr, idx) => (
                              <tr key={idx} className="hover:bg-[#FAF8F5] transition-colors">
                                <td className="p-2.5 font-bold text-[#183047]">
                                  {tr.planetTa} <span className="text-[10px] text-[#8190A6]">({tr.planet})</span>
                                </td>
                                <td className="p-2.5 font-mono">
                                  {tr.transitSign} {tr.degFormatted}
                                </td>
                                <td className="p-2.5 font-bold text-[#153F6B]">
                                  {tr.houseFromMoon}-ஆம் இடம்
                                </td>
                                <td className="p-2.5 font-mono text-[#52667E]">
                                  {tr.houseFromLagna}-ஆம் இடம்
                                </td>
                                <td className="p-2.5 text-[#52667E]">
                                  {tr.isRetrograde ? "வக்ரம் (R)" : "நேர்கதி"}
                                </td>
                                <td className="p-2.5">
                                  <span
                                    className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                                      tr.nature === "auspicious"
                                        ? "bg-emerald-50 text-emerald-800 border-emerald-300"
                                        : tr.nature === "inauspicious"
                                        ? "bg-rose-50 text-rose-800 border-rose-300"
                                        : "bg-slate-50 text-slate-700 border-slate-300"
                                    }`}
                                  >
                                    {tr.natureTa}
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ===================================================================== */}
          {/* CATEGORY 6: ஜைமினி சார காரகங்கள் */}
          {/* ===================================================================== */}
          {activeCategory === "jaimini" && (
            <div className="space-y-5">
              <div className="bg-white rounded-xl border border-[#D9DEE7] p-5 shadow-2xs space-y-5">
                <div className="flex items-center justify-between pb-3 border-b border-[#F2F3F5]">
                  <div className="flex items-center gap-2.5">
                    <span className="p-2 rounded-lg bg-amber-50 text-[#B4872B] border border-amber-200">
                      <Crown className="w-4 h-4" />
                    </span>
                    <div>
                      <h3 className="font-serif text-base font-bold text-[#183047]">
                        ஜைமினி சப்த சார காரகங்கள் (Jaimini 7 Chara Karakas)
                      </h3>
                      <p className="text-xs text-[#8190A6]">
                        ஜைமினி உபதேச சூத்திரப்படி அதிக பாகை பெற்ற 7 கிரகங்களின் காரகத்துவ பகுப்பாய்வு
                      </p>
                    </div>
                  </div>
                  <span className="text-[11px] font-mono font-semibold px-2 py-0.5 rounded bg-[#FAF2DE] text-[#B4872B] border border-[#D8BD80]">
                    7-Karaka Scheme
                  </span>
                </div>

                {/* Spotlight on AK and AmK */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Atmakaraka Card */}
                  <div className="p-4 rounded-xl border border-[#D8BD80] bg-[#FAF2DE]/50 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-[#8C6D23] uppercase tracking-wider flex items-center gap-1.5">
                        <Crown className="w-4 h-4 text-[#B4872B]" />
                        <span>ஆத்மகாரகன் (Atmakaraka - AK)</span>
                      </span>
                      <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-[#FAF2DE] text-[#B4872B] border border-[#D8BD80]">
                        அதிஷ்ட கிரகம்
                      </span>
                    </div>
                    <div className="flex items-baseline gap-2">
                      <span className="text-lg sm:text-xl font-bold text-[#183047]">
                        {jaiminiKarakas[0]?.grahaNameTa} ({jaiminiKarakas[0]?.grahaName})
                      </span>
                      <span className="text-xs font-mono text-[#153F6B] font-semibold">
                        {jaiminiKarakas[0]?.degreeFormatted}
                      </span>
                    </div>
                    <p className="text-xs text-[#52667E] leading-relaxed pt-1 border-t border-[#D8BD80]/40">
                      {jaiminiKarakas[0]?.signNameTa} ராசி, {jaiminiKarakas[0]?.nakshatraName} நட்சத்திரத்தில் அதிக பாகை பெற்று ஆன்ம காரகனாக விளங்குகிறார்.
                    </p>
                  </div>

                  {/* Amatyakaraka Card */}
                  <div className="p-4 rounded-xl border border-[#BFDBFE] bg-[#EBF2FE]/60 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-[#153F6B] uppercase tracking-wider flex items-center gap-1.5">
                        <Award className="w-4 h-4 text-[#153F6B]" />
                        <span>அமாத்யகாரகன் (Amatyakaraka - AmK)</span>
                      </span>
                      <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-[#EBF2FE] text-[#153F6B] border border-[#BFDBFE]">
                        தொழில் காரகன்
                      </span>
                    </div>
                    <div className="flex items-baseline gap-2">
                      <span className="text-lg sm:text-xl font-bold text-[#183047]">
                        {jaiminiKarakas[1]?.grahaNameTa} ({jaiminiKarakas[1]?.grahaName})
                      </span>
                      <span className="text-xs font-mono text-[#153F6B] font-semibold">
                        {jaiminiKarakas[1]?.degreeFormatted}
                      </span>
                    </div>
                    <p className="text-xs text-[#52667E] leading-relaxed pt-1 border-t border-[#BFDBFE]/60">
                      {jaiminiKarakas[1]?.signNameTa} ராசியில் 2-வது அதிக பாகை பெற்று தொழில், அந்தஸ்து மற்றும் அதிகார காரகனாகிறார்.
                    </p>
                  </div>
                </div>

                {/* Complete 7-Karaka Table */}
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-[#183047] uppercase tracking-wider">
                    7 சார காரகங்கள் முழுமையான விவர அட்டவணை
                  </h4>
                  <div className="overflow-x-auto rounded-lg border border-[#D9DEE7]">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-[#F2F3F5] text-[#183047] font-bold border-b border-[#D9DEE7]">
                        <tr>
                          <th className="p-2.5">காரகம்</th>
                          <th className="p-2.5">தமிழ் தலைப்பு</th>
                          <th className="p-2.5">கிரகம்</th>
                          <th className="p-2.5">ராசியில் பாகை</th>
                          <th className="p-2.5">ராசி</th>
                          <th className="p-2.5">நட்சத்திரம்</th>
                          <th className="p-2.5">காரகத்துவ விளக்கம்</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#F2F3F5] bg-white">
                        {jaiminiKarakas.map((k, idx) => (
                          <tr key={idx} className="hover:bg-[#FAF8F5] transition-colors">
                            <td className="p-2.5 font-bold font-mono text-[#153F6B]">
                              <span className="px-1.5 py-0.5 rounded bg-blue-50 border border-blue-200">
                                {k.code}
                              </span>
                            </td>
                            <td className="p-2.5 font-bold text-[#183047]">
                              {k.titleTa}
                            </td>
                            <td className="p-2.5 font-bold text-[#B4872B]">
                              {k.grahaNameTa}{" "}
                              <span className="text-[10px] text-[#8190A6]">({k.grahaName})</span>
                            </td>
                            <td className="p-2.5 font-mono">
                              {k.degreeFormatted}
                            </td>
                            <td className="p-2.5">
                              {k.signNameTa}
                            </td>
                            <td className="p-2.5 text-[#52667E]">
                              {k.nakshatraName} {k.pada ? `(${k.pada})` : ""}
                            </td>
                            <td className="p-2.5 text-[11px] text-[#52667E] max-w-xs">
                              {k.significanceTa}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
