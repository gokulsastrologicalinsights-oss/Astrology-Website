"use client";

import React, { useState, useEffect, useCallback, useMemo, useRef, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  KpMonthlyPredictionResponse,
  AvailableMonthItem,
  SavedHoroscopeItem,
  KpMonthlyEventItem,
  LiveTransitsResponse,
  DasaResponse,
  PlanetInfo,
} from "@/lib/types";
import {
  getAvailableKpMonths,
  getKpMonthlyPrediction,
  getLiveTransits,
  calculateDasa,
} from "@/lib/api";
import { getLordName, getGrahaName, getRasiName } from "@/lib/translations";
import {
  Compass,
  Calendar,
  Clock,
  Sparkles,
  Search,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  ShieldCheck,
  ArrowRight,
  Briefcase,
  Coins,
  Heart,
  Home,
  Car,
  Plane,
  GraduationCap,
  Baby,
  Scale,
  Activity,
  Flame,
  Star,
  Zap,
  Sun,
  Moon,
  Info,
  Printer,
  Sliders,
  ShieldAlert,
} from "lucide-react";

// Helper to render relevant domain icon
function getDomainIcon(category: string) {
  const cat = category.toLowerCase();
  if (cat.includes("career") || cat.includes("job") || cat.includes("profession") || cat.includes("business")) {
    return <Briefcase className="w-5 h-5 text-indigo-400" />;
  }
  if (cat.includes("money") || cat.includes("finance") || cat.includes("wealth") || cat.includes("income")) {
    return <Coins className="w-5 h-5 text-amber-400" />;
  }
  if (cat.includes("love") || cat.includes("marriage") || cat.includes("relationship")) {
    return <Heart className="w-5 h-5 text-pink-400" />;
  }
  if (cat.includes("health") || cat.includes("vitality") || cat.includes("wellness")) {
    return <Activity className="w-5 h-5 text-emerald-400" />;
  }
  if (cat.includes("travel") || cat.includes("journey") || cat.includes("abroad") || cat.includes("vehicle")) {
    return <Plane className="w-5 h-5 text-cyan-400" />;
  }
  if (cat.includes("home") || cat.includes("property")) {
    return <Home className="w-5 h-5 text-emerald-400" />;
  }
  return <Sparkles className="w-5 h-5 text-amber-400" />;
}

// Planetary archetypes for the Dasha commentary
const PLANET_ARCHETYPES: Record<string, { en: string; ta: string }> = {
  Sun: {
    en: "Leadership, vitality, authority, self-respect, government matters, and clarity of purpose.",
    ta: "தலைமைத்துவம், ஆன்ம பலம், கௌரவம், அரசாங்க அனுகூலம், மற்றும் தெளிவான முடிவுகள்.",
  },
  Moon: {
    en: "Emotional mind, motherly care, public relations, travel, mental peace, and fluctuations.",
    ta: "மன அமைதி, தாயின் அன்பு, மக்கள் தொடர்பு, பயணங்கள் மற்றும் உணர்ச்சிப்பூர்வ மாற்றங்கள்.",
  },
  Mars: {
    en: "Courage, dynamic drive, physical energy, property, competitive spirit, and swift action.",
    ta: "தைரியம், சுறுசுறுப்பு, நிலம்/சொத்து ஆதாயம், போட்டிகளில் வெற்றி மற்றும் வேகமான செயல்பாடுகள்.",
  },
  Rahu: {
    en: "Unconventional ambition, sudden breakthroughs, technological growth, foreign avenues, and material expansion.",
    ta: "திடீர் முன்னேற்றம், புதிய தொழில்நுட்பம், வெளிநாட்டு வாய்ப்புகள் மற்றும் தீவிர விருப்பங்கள்.",
  },
  Jupiter: {
    en: "Wisdom, wealth, children, higher learning, spiritual guidance, divine grace, and ethical expansion.",
    ta: "ஞானம், பண வரவு, புத்திர பாக்கியம், ஆன்மீகம், குருவருள் மற்றும் நல்ல வழிகாட்டுதல்.",
  },
  Saturn: {
    en: "Discipline, karmic restructuring, patience, hard work, durability, and practical reality.",
    ta: "கடின உழைப்பு, பொறுமை, தொழில் ஸ்திரத்தன்மை, கடமை உணர்வு மற்றும் நீண்ட கால வெற்றி.",
  },
  Mercury: {
    en: "Intellect, commerce, communication, analytical logic, documentation, and networking.",
    ta: "புத்தி கூர்மை, வியாபாரம், பேச்சுத்திறன், கணக்கு மற்றும் சிறந்த தகவல்தொடர்பு.",
  },
  Ketu: {
    en: "Spiritual liberation, intuition, detachment from vanity, analytical research, and hidden depth.",
    ta: "ஆன்மீக நாட்டம், உள்ளுணர்வு, உலகியல் பற்றின்மை மற்றும் ஆழ்ந்த ஆராய்ச்சி அறிவு.",
  },
  Venus: {
    en: "Relationships, artistic creativity, comfort, luxury, diplomacy, harmony, and material joy.",
    ta: "காதல், தாம்பத்தியம், சுகபோகம், கலை ஆர்வம், நட்பு மற்றும் செல்வச் செழிப்பு.",
  },
};

function KalaChakraContent() {
  const searchParams = useSearchParams();
  const initialHoroscopeId = searchParams.get("id") || "";

  const { language } = useLanguage();
  const isTa = language === "ta";
  const { session, isAuthenticated, isLoading: authLoading } = useAuth();

  // Mode: "saved" or "manual"
  const [chartMode, setChartMode] = useState<"saved" | "manual">(
    initialHoroscopeId ? "saved" : "manual"
  );

  // Saved horoscopes state
  const [savedHoroscopes, setSavedHoroscopes] = useState<SavedHoroscopeItem[]>([]);
  const [selectedHoroscopeId, setSelectedHoroscopeId] = useState<string>(initialHoroscopeId);
  const [loadingHoroscopes, setLoadingHoroscopes] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Manual chart input state
  const [manualName, setManualName] = useState<string>("My Chart");
  const [manualDate, setManualDate] = useState<string>("1995-08-25");
  const [manualTime, setManualTime] = useState<string>("07:30:00");
  const [manualLat, setManualLat] = useState<string>("13.0827");
  const [manualLon, setManualLon] = useState<string>("80.2707");
  const [manualTz, setManualTz] = useState<string>("Asia/Kolkata");

  // Selected horoscope object
  const selectedHoroscope = useMemo(() => {
    return savedHoroscopes.find((h) => h.id === selectedHoroscopeId) || null;
  }, [savedHoroscopes, selectedHoroscopeId]);

  // Filtered saved horoscopes for search
  const filteredSavedHoroscopes = useMemo(() => {
    if (!searchQuery.trim()) return savedHoroscopes;
    const q = searchQuery.toLowerCase();
    return savedHoroscopes.filter(
      (h) =>
        h.person_name?.toLowerCase().includes(q) ||
        h.birthplace?.toLowerCase().includes(q) ||
        h.birth_date?.includes(q)
    );
  }, [savedHoroscopes, searchQuery]);

  // Target Timing selection
  const now = new Date();
  const [availableMonths, setAvailableMonths] = useState<AvailableMonthItem[]>([]);
  const [selectedYear, setSelectedYear] = useState<number>(now.getFullYear());
  const [selectedMonth, setSelectedMonth] = useState<number>(now.getMonth() + 1);

  // Results State
  const [calculating, setCalculating] = useState<boolean>(false);
  const [predictionData, setPredictionData] = useState<KpMonthlyPredictionResponse | null>(null);
  const [dasaData, setDasaData] = useState<DasaResponse | null>(null);
  const [transitsData, setTransitsData] = useState<LiveTransitsResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [copiedSummary, setCopiedSummary] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<"all" | "favorable" | "caution">("all");
  const [expandedEvents, setExpandedEvents] = useState<Record<string, boolean>>({});

  // Populate manual inputs from a horoscope record
  const applyHoroscopeToInputs = useCallback((h: SavedHoroscopeItem) => {
    if (h.person_name) setManualName(h.person_name);
    if (h.birth_date) setManualDate(h.birth_date);
    if (h.birth_time) {
      let t = h.birth_time.trim();
      if (t.length === 5) t += ":00";
      setManualTime(t);
    }
    if (h.latitude !== undefined && h.latitude !== null) setManualLat(String(h.latitude));
    if (h.longitude !== undefined && h.longitude !== null) setManualLon(String(h.longitude));
    if (h.timezone) setManualTz(h.timezone);
  }, []);

  const handleSelectHoroscope = useCallback((newId: string) => {
    setSelectedHoroscopeId(newId);
    const found = savedHoroscopes.find((h) => h.id === newId);
    if (found) {
      applyHoroscopeToInputs(found);
    }
  }, [savedHoroscopes, applyHoroscopeToInputs]);

  // Load available candidate months
  useEffect(() => {
    getAvailableKpMonths()
      .then((res) => {
        if (res && res.months && res.months.length > 0) {
          setAvailableMonths(res.months);
          const current = res.months.find((m) => m.is_current) || res.months[0];
          setSelectedYear(current.year);
          setSelectedMonth(current.month);
        }
      })
      .catch((err) => console.warn("Failed to load candidate months:", err));
  }, []);

  // Load saved horoscopes if authenticated
  const loadSavedHoroscopes = useCallback(async () => {
    if (authLoading || !isAuthenticated) return;
    try {
      setLoadingHoroscopes(true);
      const headers: Record<string, string> = {};
      if (session?.access_token) {
        headers["Authorization"] = `Bearer ${session.access_token}`;
      }
      const res = await fetch("/api/horoscopes?page=1&limit=1000", {
        cache: "no-store",
        headers,
      });
      if (res.ok) {
        const data = await res.json();
        const items: SavedHoroscopeItem[] = data.horoscopes || data.items || [];
        setSavedHoroscopes(items);
        if (items.length > 0) {
          const target = initialHoroscopeId
            ? items.find((h) => h.id === initialHoroscopeId) || items[0]
            : (selectedHoroscopeId ? items.find((h) => h.id === selectedHoroscopeId) || items[0] : items[0]);
          setSelectedHoroscopeId(target.id);
          setChartMode("saved");
          applyHoroscopeToInputs(target);
        }
      }
    } catch (err) {
      console.warn("Failed to fetch saved horoscopes:", err);
    } finally {
      setLoadingHoroscopes(false);
    }
  }, [authLoading, isAuthenticated, session?.access_token, initialHoroscopeId, selectedHoroscopeId, applyHoroscopeToInputs]);

  useEffect(() => {
    loadSavedHoroscopes();
  }, [loadSavedHoroscopes]);

  // If ?id= URL parameter is provided, fetch single horoscope immediately
  useEffect(() => {
    if (!initialHoroscopeId) return;
    let isMounted = true;
    const fetchTargetChart = async () => {
      try {
        const headers: Record<string, string> = {};
        if (session?.access_token) {
          headers["Authorization"] = `Bearer ${session.access_token}`;
        }
        const res = await fetch(`/api/horoscopes/${initialHoroscopeId}`, { headers });
        if (res.ok && isMounted) {
          const data = await res.json();
          const h = data.horoscope;
          if (h) {
            setSelectedHoroscopeId(h.id);
            setChartMode("saved");
            applyHoroscopeToInputs(h);
            setSavedHoroscopes((prev) => {
              if (prev.some((p) => p.id === h.id)) return prev;
              return [h, ...prev];
            });
          }
        }
      } catch (err) {
        console.warn("Failed to fetch initial horoscope by ID:", err);
      }
    };
    fetchTargetChart();
    return () => {
      isMounted = false;
    };
  }, [initialHoroscopeId, session?.access_token, applyHoroscopeToInputs]);

  // Main calculation handler
  const handleCalculateRadar = useCallback(async () => {
    setCalculating(true);
    setErrorMsg(null);
    try {
      const targetDateStr = `${selectedYear}-${String(selectedMonth).padStart(2, "0")}-15`;
      const found = chartMode === "saved" ? savedHoroscopes.find((h) => h.id === selectedHoroscopeId) : null;

      const activeLat = found && found.latitude !== undefined ? parseFloat(found.latitude as any) || 13.0827 : parseFloat(manualLat) || 13.0827;
      const activeLon = found && found.longitude !== undefined ? parseFloat(found.longitude as any) || 80.2707 : parseFloat(manualLon) || 80.2707;
      const activeTz = found?.timezone || manualTz || "Asia/Kolkata";
      const activeDate = found?.birth_date || manualDate;
      let activeTime = (found?.birth_time || manualTime || "12:00:00").trim();
      if (activeTime.length === 5) activeTime += ":00";
      const activeName = (found?.person_name || manualName || "Native").trim();

      // 1. Fetch Live Planetary Transits (Gochara) using active coordinates
      const transitsPromise = getLiveTransits({
        latitude: activeLat,
        longitude: activeLon,
        timezone: activeTz,
      }).catch((e) => {
        console.warn("Live transits fetch failed:", e);
        return null;
      });

      // 2. Fetch KP Monthly & Period Prediction
      let kpReq: any = {
        year: selectedYear,
        month: selectedMonth,
        birth: {
          birth_date: activeDate,
          birth_time: activeTime,
          latitude: activeLat,
          longitude: activeLon,
          timezone: activeTz,
        },
        native_name: activeName,
      };

      if (chartMode === "saved" && selectedHoroscopeId) {
        kpReq.saved_horoscope_id = selectedHoroscopeId;
      }

      const kpPromise = getKpMonthlyPrediction(kpReq, session?.access_token);

      // 3. Fetch Precise Dasa with Target Date
      let dasaReq: any = {
        depth: 3,
        target_date: targetDateStr,
        birth_date: activeDate,
        birth_time: activeTime,
        latitude: activeLat,
        longitude: activeLon,
        timezone: activeTz,
      };

      const dasaPromise = calculateDasa(dasaReq).catch((e) => {
        console.warn("Dasa calculate failed:", e);
        return null;
      });

      const [kpRes, dasaRes, transitsRes] = await Promise.all([
        kpPromise,
        dasaPromise,
        transitsPromise,
      ]);

      setPredictionData(kpRes);
      if (dasaRes) setDasaData(dasaRes);
      if (transitsRes) setTransitsData(transitsRes);
    } catch (err: any) {
      console.error("KalaChakra calculation error:", err);
      setErrorMsg(
        err?.message || (isTa ? "கணிப்பு செய்வதில் பிழை ஏற்பட்டது. தயவுசெய்து மீண்டும் முயற்சிக்கவும்." : "Failed to calculate current period radar. Please verify inputs.")
      );
    } finally {
      setCalculating(false);
    }
  }, [
    chartMode,
    selectedHoroscopeId,
    manualDate,
    manualTime,
    manualLat,
    manualLon,
    manualTz,
    manualName,
    selectedYear,
    selectedMonth,
    session?.access_token,
    savedHoroscopes,
    isTa,
  ]);

  // Trigger initial calculation once target horoscope is ready
  const hasAutoRunRef = useRef(false);
  useEffect(() => {
    if (initialHoroscopeId && !hasAutoRunRef.current && savedHoroscopes.length > 0) {
      const found = savedHoroscopes.find((h) => h.id === initialHoroscopeId);
      if (found) {
        hasAutoRunRef.current = true;
        setSelectedHoroscopeId(found.id);
        applyHoroscopeToInputs(found);
        handleCalculateRadar();
      }
    }
  }, [initialHoroscopeId, savedHoroscopes, applyHoroscopeToInputs, handleCalculateRadar]);

  // Filter events based on active tab
  const filteredEvents = useMemo(() => {
    if (!predictionData) return [];
    if (activeTab === "favorable") {
      return [...predictionData.guaranteed_events, ...predictionData.favorable_events];
    }
    if (activeTab === "caution") {
      return predictionData.caution_events;
    }
    return predictionData.all_events || [];
  }, [predictionData, activeTab]);

  const toggleEventExpand = (eventId: string) => {
    setExpandedEvents((prev) => ({ ...prev, [eventId]: !prev[eventId] }));
  };

  // Copy Executive Summary
  const handleCopySummary = () => {
    if (!predictionData) return;
    const dba = predictionData.dasha_hierarchy;
    const summaryText = `--- KALACHAKRA: CURRENT PERIOD RADAR ---
Native: ${predictionData.native_name}
Target Window: ${predictionData.month_label}
Active Mahadasha: ${dba.mahadasha} (${dba.mahadasha_ta})
Active Antardasha: ${dba.antardasha} (${dba.antardasha_ta})
Active Pratyantara: ${dba.pratyantardasha} (${dba.pratyantardasha_ta})
Period Span: ${dba.period_start} to ${dba.period_end}

Guaranteed / Highly Favorable Signals: ${predictionData.guaranteed_events.length + predictionData.favorable_events.length}
Caution Areas: ${predictionData.caution_events.length}

Guidance Summary:
${predictionData.overall_month_summary_ta || "Maintain balanced effort and align actions with active planetary energies."}
----------------------------------------`;

    navigator.clipboard.writeText(summaryText);
    setCopiedSummary(true);
    setTimeout(() => setCopiedSummary(false), 2500);
  };

  // Extract key transits (Saturn, Jupiter, Rahu, Ketu)
  const keyTransits = useMemo(() => {
    if (!transitsData || !transitsData.planets) return [];
    const targetNames = ["Saturn", "Jupiter", "Rahu", "Ketu", "Sun", "Mars"];
    return transitsData.planets.filter((p) => targetNames.includes(p.name));
  }, [transitsData]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 pb-20">
      {/* Top Banner / Breadcrumb */}
      <div className="bg-slate-900/90 border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <Breadcrumbs
            items={[
              { label: isTa ? "முகப்பு" : "Home", href: "/" },
              { label: isTa ? "ஜோதிடக் கருவிகள்" : "Astrology Tools", href: "/tools" },
              { label: isTa ? "காலச்சக்கரம்" : "KalaChakra Radar", href: "/tools/kalachakra" },
            ]}
          />
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
        {/* Header Hero Section */}
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-950 via-slate-900 to-slate-950 p-8 border border-indigo-500/20 shadow-2xl">
          <div className="absolute top-0 right-0 -mt-10 -mr-10 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute bottom-0 left-0 -mb-10 -ml-10 w-80 h-80 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />

          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-3">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-xs font-semibold uppercase tracking-wider">
                <Compass className="w-3.5 h-3.5 animate-spin-slow text-amber-400" />
                {isTa ? "நிகழ்கால தசா-புத்தி & கோச்சார வழிகாட்டி" : "Real-Time Period & Cosmic Weather"}
              </div>
              <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight text-white flex items-center gap-3">
                <span>{isTa ? "காலச்சக்கரம்" : "KalaChakra"}</span>
                <span className="text-amber-400 text-2xl md:text-4xl font-light">
                  {isTa ? "நேரக் கணிப்பு ரேடார்" : "Timing Radar"}
                </span>
              </h1>
              <p className="text-slate-300 text-sm md:text-base max-w-3xl leading-relaxed">
                {isTa
                  ? "விம்சோத்தரி தசா-புத்தி சுழற்சி, கோச்சார கிரக நிலைகள் (சனி, குரு, ராகு-கேது) மற்றும் கே.பி 4-தூண் விதிகளை ஒருங்கிணைத்து உங்கள் தற்போதைய காலகட்டத்தின் சாத்தியக்கூறுகள், நன்மைகள் மற்றும் கவனிக்க வேண்டிய விஷயங்களை துல்லியமாக அறியும் கருவி."
                  : "A precision life-timing radar combining Vimshottari Dasa-Bhukti cycles, live planetary transits (Saturn, Jupiter, Rahu-Ketu), and KP 4-pillar event probability significations."}
              </p>
            </div>

            {/* Quick Action Buttons */}
            {predictionData && (
              <div className="flex flex-wrap items-center gap-3 self-start md:self-auto">
                <button
                  onClick={handleCopySummary}
                  className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center gap-2 text-sm font-medium transition-all shadow-sm"
                >
                  {copiedSummary ? (
                    <>
                      <Check className="w-4 h-4 text-emerald-400" />
                      <span>{isTa ? "நகலெடுக்கப்பட்டது!" : "Copied!"}</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4 text-indigo-400" />
                      <span>{isTa ? "சுருக்கத்தை நகலெடு" : "Copy Summary"}</span>
                    </>
                  )}
                </button>
                <button
                  onClick={() => window.print()}
                  className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center gap-2 text-sm font-medium transition-all shadow-sm"
                >
                  <Printer className="w-4 h-4 text-amber-400" />
                  <span>{isTa ? "அச்சிடு / PDF" : "Print Report"}</span>
                </button>
              </div>
            )}
          </div>

          {/* Ethical Disclaimer Notice */}
          <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-start gap-2.5 text-xs text-slate-400">
            <Info className="w-4 h-4 text-amber-400/80 shrink-0 mt-0.5" />
            <p>
              {isTa
                ? "ஜோதிடக் கால கணிப்பு என்பது கிரக ஆற்றல்களின் சாத்தியக்கூறுகள் மற்றும் சாதகமான நேரங்களை உணர்த்தும் ஒரு வழிகாட்டி மட்டுமே; இது விதியை 100% மாற்றிவிடாது. உங்கள் முயற்சி, விவேகம் மற்றும் நேர்மறை முடிவுகளே இறுதியானது."
                : "Astrological timing maps cosmic tendencies, energy windows, and favorable moments. It is designed as a strategic awareness tool to align your conscious choices, not a 100% rigid fatalistic prediction."}
            </p>
          </div>
        </div>

        {/* Configuration / Input Card */}
        <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6 shadow-xl space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div className="flex items-center gap-3">
              <Sliders className="w-5 h-5 text-indigo-400" />
              <h2 className="text-lg font-bold text-white">
                {isTa ? "1. ஜாதகம் & காலகட்டத் தேர்வு" : "1. Select Chart & Target Period"}
              </h2>
            </div>

            {/* Mode Toggle */}
            <div className="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs font-semibold">
              <button
                onClick={() => setChartMode("saved")}
                disabled={!isAuthenticated || (savedHoroscopes.length === 0 && !loadingHoroscopes)}
                className={`px-3 py-1.5 rounded-lg transition-all ${
                  chartMode === "saved"
                    ? "bg-indigo-600 text-white shadow"
                    : "text-slate-400 hover:text-slate-200 disabled:opacity-40"
                }`}
              >
                {isTa ? "சேமித்த ஜாதகம்" : "Saved Chart"} ({loadingHoroscopes ? "..." : savedHoroscopes.length})
              </button>
              <button
                onClick={() => setChartMode("manual")}
                className={`px-3 py-1.5 rounded-lg transition-all ${
                  chartMode === "manual" ? "bg-indigo-600 text-white shadow" : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {isTa ? "நேரடி உள்ளீடு" : "Manual Input"}
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Chart Selection */}
            {chartMode === "saved" ? (
              <div className="space-y-3 md:col-span-2">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                    <Star className="w-3.5 h-3.5 text-amber-400" />
                    {isTa ? "சேமிக்கப்பட்ட ஜாதகத்தைத் தேர்ந்தெடுக்கவும்" : "Select Saved Horoscope"}
                  </label>
                  {savedHoroscopes.length > 4 && (
                    <div className="relative">
                      <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder={isTa ? "ஜாதகத்தைத் தேடுக..." : "Search horoscopes..."}
                        className="w-full sm:w-48 bg-slate-950/80 border border-slate-700/80 rounded-lg px-2.5 py-1 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                      />
                    </div>
                  )}
                </div>
                {loadingHoroscopes ? (
                  <div className="h-10 bg-slate-800/60 animate-pulse rounded-xl" />
                ) : filteredSavedHoroscopes.length > 0 ? (
                  <>
                    <select
                      value={selectedHoroscopeId}
                      onChange={(e) => handleSelectHoroscope(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
                    >
                      {filteredSavedHoroscopes.map((h) => (
                        <option key={h.id} value={h.id}>
                          {h.person_name} — {h.birth_date} ({h.birthplace || "N/A"})
                        </option>
                      ))}
                    </select>

                    {selectedHoroscope && (
                      <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-xs text-slate-300 grid grid-cols-2 sm:grid-cols-4 gap-2">
                        <div>
                          <span className="text-slate-500 block text-[10px] uppercase font-semibold">
                            {isTa ? "பெயர்" : "Name"}
                          </span>
                          <span className="font-bold text-white truncate block">
                            {selectedHoroscope.person_name}
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-500 block text-[10px] uppercase font-semibold">
                            {isTa ? "பிறந்த நேரம்" : "Date & Time"}
                          </span>
                          <span className="text-slate-200 block truncate">
                            {selectedHoroscope.birth_date} {selectedHoroscope.birth_time || ""}
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-500 block text-[10px] uppercase font-semibold">
                            {isTa ? "இடம்" : "Birthplace"}
                          </span>
                          <span className="text-slate-200 block truncate">
                            {selectedHoroscope.birthplace || "N/A"}
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-500 block text-[10px] uppercase font-semibold">
                            {isTa ? "ஆயனாம்சம்" : "Ayanamsa"}
                          </span>
                          <span className="text-amber-400 font-semibold block">
                            {selectedHoroscope.ayanamsa_id === 1 ? "KP Original" : selectedHoroscope.ayanamsa_id === 3 ? "KP New" : "Lahiri"}
                          </span>
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <p className="text-xs text-amber-400/90">
                    {searchQuery
                      ? (isTa ? "பொருத்தமான ஜாதகங்கள் எதுவும் இல்லை." : "No matching horoscopes found.")
                      : (isTa
                          ? "சேமிக்கப்பட்ட ஜாதகங்கள் இல்லை. 'நேரடி உள்ளீடு' முறையைப் பயன்படுத்தவும்."
                          : "No saved charts found. Switch to 'Manual Input' tab.")}
                  </p>
                )}
              </div>
            ) : (
              <div className="space-y-4 md:col-span-2">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <label className="text-xs text-slate-400">{isTa ? "பெயர்" : "Native Name"}</label>
                    <input
                      type="text"
                      value={manualName}
                      onChange={(e) => setManualName(e.target.value)}
                      className="w-full mt-1 bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-slate-400">{isTa ? "பிறந்த தேதி" : "Birth Date"}</label>
                    <input
                      type="date"
                      value={manualDate}
                      onChange={(e) => setManualDate(e.target.value)}
                      className="w-full mt-1 bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-slate-400">{isTa ? "பிறந்த நேரம்" : "Birth Time"}</label>
                    <input
                      type="time"
                      step="1"
                      value={manualTime}
                      onChange={(e) => setManualTime(e.target.value)}
                      className="w-full mt-1 bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                  <div>
                    <label className="text-slate-400">{isTa ? "அட்சரேகை (Lat)" : "Latitude"}</label>
                    <input
                      type="text"
                      value={manualLat}
                      onChange={(e) => setManualLat(e.target.value)}
                      className="w-full mt-1 bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-white"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400">{isTa ? "தீர்க்கரேகை (Lon)" : "Longitude"}</label>
                    <input
                      type="text"
                      value={manualLon}
                      onChange={(e) => setManualLon(e.target.value)}
                      className="w-full mt-1 bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-white"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400">{isTa ? "நேர மண்டலம்" : "Timezone"}</label>
                    <input
                      type="text"
                      value={manualTz}
                      onChange={(e) => setManualTz(e.target.value)}
                      className="w-full mt-1 bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-white"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Target Period Selector */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-indigo-400" />
                {isTa ? "கணிக்க வேண்டிய மாதம் / ஆண்டு" : "Target Month & Year"}
              </label>
              {availableMonths.length > 0 ? (
                <select
                  value={`${selectedYear}-${selectedMonth}`}
                  onChange={(e) => {
                    const [y, m] = e.target.value.split("-").map(Number);
                    setSelectedYear(y);
                    setSelectedMonth(m);
                  }}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
                >
                  {availableMonths.map((m) => (
                    <option key={`${m.year}-${m.month}`} value={`${m.year}-${m.month}`}>
                      {isTa ? m.label_ta : m.label_en} {m.is_current ? `(${isTa ? "தற்போது" : "Current"})` : ""}
                    </option>
                  ))}
                </select>
              ) : (
                <div className="flex gap-2">
                  <input
                    type="number"
                    value={selectedYear}
                    onChange={(e) => setSelectedYear(Number(e.target.value))}
                    className="w-1/2 bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white"
                  />
                  <input
                    type="number"
                    min="1"
                    max="12"
                    value={selectedMonth}
                    onChange={(e) => setSelectedMonth(Number(e.target.value))}
                    className="w-1/2 bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white"
                  />
                </div>
              )}

              <button
                onClick={handleCalculateRadar}
                disabled={calculating}
                className="w-full mt-3 py-3 rounded-xl bg-gradient-to-r from-indigo-600 via-indigo-500 to-indigo-600 hover:from-indigo-500 hover:to-indigo-500 text-white font-bold text-sm shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
              >
                {calculating ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin text-amber-300" />
                    <span>{isTa ? "கணிக்கப்படுகிறது..." : "Scanning Cosmic Radar..."}</span>
                  </>
                ) : (
                  <>
                    <Compass className="w-4 h-4 text-amber-300" />
                    <span>{isTa ? "ரேடார் பலன்களைக் காண்க" : "Calculate Period Radar"}</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {errorMsg && (
            <div className="p-4 rounded-xl bg-red-950/60 border border-red-500/40 text-red-300 text-sm flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}
        </div>

        {/* Results Display */}
        {predictionData && (
          <div className="space-y-8 animate-fadeIn">
            {/* 1. Dasha-Bhukti Karmic Clock Card */}
            <div className="bg-slate-900 rounded-2xl border border-indigo-500/30 p-6 md:p-8 shadow-xl space-y-6">
              <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                    <Clock className="w-5 h-5" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                      {isTa ? "நிகழ்கால தசா-புக்தி சுழற்சி" : "Active Dasha-Bhukti Karmic Clock"}
                    </h2>
                    <p className="text-xs text-slate-400">
                      {isTa
                        ? "உங்கள் அகக் கடிகாரம் — தற்போது இயங்கும் கிரகக் கூட்டணிகள்"
                        : "Your internal timing engine — active planetary lords guiding this phase"}
                    </p>
                  </div>
                </div>

                <span className="px-3 py-1 rounded-full bg-slate-800 text-amber-400 text-xs font-semibold border border-slate-700">
                  {predictionData.month_label} ({predictionData.native_name})
                </span>
              </div>

              {/* 3-Tier Period Badges */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Mahadasha */}
                <div className="p-5 rounded-2xl bg-indigo-950/40 border border-indigo-500/30 space-y-2 relative overflow-hidden">
                  <div className="text-xs font-semibold uppercase text-indigo-300 tracking-wider">
                    {isTa ? "முதன்மை மகா தசை" : "1. Mahadasha (Major)"}
                  </div>
                  <div className="text-2xl font-black text-white flex items-center justify-between">
                    <span>{predictionData.dasha_hierarchy.mahadasha}</span>
                    <span className="text-sm font-medium text-amber-400">
                      {predictionData.dasha_hierarchy.mahadasha_ta}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed pt-1">
                    {PLANET_ARCHETYPES[predictionData.dasha_hierarchy.mahadasha]?.[isTa ? "ta" : "en"] ||
                      (isTa ? "முக்கிய வாழ்க்கை மாற்றங்கள் மற்றும் பொதுவான நோக்கம்." : "Broad thematic foundation.")}
                  </p>
                </div>

                {/* Antardasha (Bhukti) */}
                <div className="p-5 rounded-2xl bg-indigo-950/40 border border-indigo-500/30 space-y-2 relative overflow-hidden">
                  <div className="text-xs font-semibold uppercase text-indigo-300 tracking-wider">
                    {isTa ? "உள் புக்தி (அந்தர்தசை)" : "2. Antardasha / Bhukti"}
                  </div>
                  <div className="text-2xl font-black text-white flex items-center justify-between">
                    <span>{predictionData.dasha_hierarchy.antardasha}</span>
                    <span className="text-sm font-medium text-amber-400">
                      {predictionData.dasha_hierarchy.antardasha_ta}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed pt-1">
                    {PLANET_ARCHETYPES[predictionData.dasha_hierarchy.antardasha]?.[isTa ? "ta" : "en"] ||
                      (isTa ? "தற்போதைய நிகழ்வுகளின் நேரடி ஆதிக்க காரகர்." : "Primary trigger of immediate events.")}
                  </p>
                </div>

                {/* Pratyantardasha */}
                <div className="p-5 rounded-2xl bg-indigo-950/40 border border-indigo-500/30 space-y-2 relative overflow-hidden">
                  <div className="text-xs font-semibold uppercase text-indigo-300 tracking-wider">
                    {isTa ? "பிரத்யந்தர தசை (மின்னோட்டம்)" : "3. Pratyantardasha"}
                  </div>
                  <div className="text-2xl font-black text-white flex items-center justify-between">
                    <span>{predictionData.dasha_hierarchy.pratyantardasha}</span>
                    <span className="text-sm font-medium text-amber-400">
                      {predictionData.dasha_hierarchy.pratyantardasha_ta}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed pt-1">
                    {PLANET_ARCHETYPES[predictionData.dasha_hierarchy.pratyantardasha]?.[isTa ? "ta" : "en"] ||
                      (isTa ? "நாட்களின் நுட்பமான உணர்வுகள் மற்றும் மனநிலை." : "Subtle daily micro-frequency.")}
                  </p>
                </div>
              </div>

              {/* Period Timeline & Span Info */}
              <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 flex flex-wrap items-center justify-between gap-4 text-xs">
                <div className="flex items-center gap-2 text-slate-300">
                  <Calendar className="w-4 h-4 text-indigo-400" />
                  <span>
                    {isTa ? "இந்த புக்தி செயல்படும் காலம்:" : "Active Sub-Period Window:"}{" "}
                    <strong className="text-white">
                      {predictionData.dasha_hierarchy.period_start} → {predictionData.dasha_hierarchy.period_end}
                    </strong>
                  </span>
                </div>
                {dasaData?.active_period?.target_age && (
                  <div className="text-slate-400">
                    {isTa ? "கணிக்கப்பட்ட வயது:" : "Age at Target Date:"}{" "}
                    <strong className="text-amber-400">{dasaData.active_period.target_age}</strong>
                  </div>
                )}
              </div>
            </div>

            {/* 2. Live Cosmic Weather (Gochara Transits) */}
            <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6 md:p-8 shadow-xl space-y-6">
              <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400">
                    <Sun className="w-5 h-5" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                      {isTa ? "தற்போதைய கோச்சார வானிலை (Gochara Radar)" : "Live Cosmic Weather (Transits)"}
                    </h2>
                    <p className="text-xs text-slate-400">
                      {isTa
                        ? "பிரபஞ்சத்தில் இப்போது நகரும் கிரகங்களின் நேரடித் தாக்கம்"
                        : "Real-time physical planetary positions in the sky impacting the current moment"}
                    </p>
                  </div>
                </div>

                <span className="text-xs text-slate-400 flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                  {isTa ? "சூரியனின் சஞ்சாரம்:" : "Transit Sun:"}{" "}
                  <strong className="text-white">
                    {isTa ? predictionData.transit_sun.month_name_ta : predictionData.transit_sun.month_name}
                  </strong>
                </span>
              </div>

              {/* Transit Planetary Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
                {keyTransits.length > 0 ? (
                  keyTransits.map((planet) => {
                    const isRetro = planet.is_retrograde;
                    const isSaturn = planet.name === "Saturn";
                    const isJupiter = planet.name === "Jupiter";
                    return (
                      <div
                        key={planet.name}
                        className={`p-3.5 rounded-xl border transition-all ${
                          isSaturn
                            ? "bg-slate-950/80 border-blue-500/30"
                            : isJupiter
                            ? "bg-slate-950/80 border-amber-500/30"
                            : "bg-slate-950/60 border-slate-800"
                        }`}
                      >
                        <div className="flex items-center justify-between text-xs mb-1">
                          <span className="font-bold text-white">
                            {isTa ? getGrahaName(planet.name, "ta") : planet.name}
                          </span>
                          {isRetro && (
                            <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                              {isTa ? "வக்ரம்" : "Rx"}
                            </span>
                          )}
                        </div>
                        <div className="text-sm font-semibold text-slate-200">
                          {isTa ? planet.sign_name_tamil || planet.sign_name : planet.sign_name}
                        </div>
                        <div className="text-[11px] text-slate-400 mt-1">
                          {planet.degree_in_sign.toFixed(1)}°
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="col-span-full text-xs text-slate-400 italic">
                    {isTa ? "கோச்சாரத் தகவல்கள் ஏற்றப்படுகின்றன..." : "Loading transit alignments..."}
                  </div>
                )}
              </div>

              {/* Transit Highlights & Protection Banner */}
              <div className="p-4 rounded-xl bg-gradient-to-r from-slate-950 to-indigo-950/40 border border-indigo-500/20 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 text-xs">
                <div className="flex items-center gap-3">
                  <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0" />
                  <div>
                    <span className="font-bold text-white">
                      {isTa ? "சூரியனின் நட்சத்திர சஞ்சாரம்:" : "Active Solar Transits:"}
                    </span>{" "}
                    <span className="text-slate-300">
                      {isTa
                        ? predictionData.transit_sun.activated_stars_ta.join(", ")
                        : predictionData.transit_sun.activated_stars.join(", ")}
                    </span>
                  </div>
                </div>
                <div className="text-slate-400">
                  {isTa ? predictionData.transit_sun.summary_ta : "Transit triggers activate specific house cusps."}
                </div>
              </div>
            </div>

            {/* 3. KP Life Domain Signals (Traffic Light Probability) */}
            <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6 md:p-8 shadow-xl space-y-6">
              <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                    <Activity className="w-5 h-5" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                      {isTa ? "வாழ்க்கை வழிகாட்டல் & சாத்தியக்கூறுகள் (KP Radar)" : "Life Domain Signals & Probability"}
                    </h2>
                    <p className="text-xs text-slate-400">
                      {isTa
                        ? "தொழில், வருமானம், குடும்பம், ஆரோக்கியம் ஆகியவற்றின் சமிக்ஞைகள்"
                        : "KP 4-Pillar traffic light analysis for core life domains"}
                    </p>
                  </div>
                </div>

                {/* Filter Tabs */}
                <div className="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs font-semibold">
                  <button
                    onClick={() => setActiveTab("all")}
                    className={`px-3 py-1.5 rounded-lg transition-all ${
                      activeTab === "all" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {isTa ? "அனைத்தும்" : "All"} ({predictionData.all_events.length})
                  </button>
                  <button
                    onClick={() => setActiveTab("favorable")}
                    className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${
                      activeTab === "favorable" ? "bg-emerald-600 text-white" : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    <span className="w-2 h-2 rounded-full bg-emerald-400" />
                    {isTa ? "சாதகமானவை" : "Favorable"} (
                    {predictionData.guaranteed_events.length + predictionData.favorable_events.length})
                  </button>
                  <button
                    onClick={() => setActiveTab("caution")}
                    className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${
                      activeTab === "caution" ? "bg-amber-600 text-white" : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    <span className="w-2 h-2 rounded-full bg-amber-400" />
                    {isTa ? "கவனம் தேவை" : "Caution"} ({predictionData.caution_events.length})
                  </button>
                </div>
              </div>

              {/* Event Cards Grid */}
              <div className="space-y-4">
                {filteredEvents.length > 0 ? (
                  filteredEvents.map((item) => {
                    const isExpanded = !!expandedEvents[item.event_id];
                    const isFavorable = item.status === "GUARANTEED" || item.status === "HIGHLY_FAVORABLE";
                    const isCaution = item.status === "CAUTION";

                    return (
                      <div
                        key={item.event_id}
                        className={`rounded-xl border transition-all p-5 ${
                          isFavorable
                            ? "bg-slate-950/70 border-emerald-500/30 hover:border-emerald-500/50"
                            : isCaution
                            ? "bg-slate-950/70 border-amber-500/30 hover:border-amber-500/50"
                            : "bg-slate-950/70 border-slate-800 hover:border-slate-700"
                        }`}
                      >
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                          <div className="flex items-start gap-3">
                            <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 shrink-0">
                              {getDomainIcon(item.category)}
                            </div>
                            <div>
                              <div className="flex flex-wrap items-center gap-2">
                                <h3 className="font-bold text-white text-base">
                                  {isTa ? item.title_ta : item.title_en}
                                </h3>
                                <span
                                  className={`px-2 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider ${
                                    isFavorable
                                      ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                                      : isCaution
                                      ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                                      : "bg-blue-500/20 text-blue-300 border border-blue-500/30"
                                  }`}
                                >
                                  {isTa ? item.status_label_ta : item.status.replace("_", " ")}
                                </span>
                              </div>
                              <p className="text-xs text-slate-300 mt-1">
                                {isTa ? item.summary_verdict_ta : item.detailed_analysis_ta}
                              </p>
                            </div>
                          </div>

                          {/* Score and Toggle */}
                          <div className="flex items-center gap-4 self-end sm:self-auto shrink-0">
                            <div className="text-right">
                              <div className="text-xs text-slate-400">
                                {isTa ? "சாத்தியக்கூறு" : "Probability"}
                              </div>
                              <div
                                className={`text-lg font-black ${
                                  isFavorable
                                    ? "text-emerald-400"
                                    : isCaution
                                    ? "text-amber-400"
                                    : "text-blue-400"
                                }`}
                              >
                                {item.probability_score}%
                              </div>
                            </div>
                            <button
                              onClick={() => toggleEventExpand(item.event_id)}
                              className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 transition-all border border-slate-800"
                            >
                              {isExpanded ? (
                                <ChevronUp className="w-4 h-4" />
                              ) : (
                                <ChevronDown className="w-4 h-4" />
                              )}
                            </button>
                          </div>
                        </div>

                        {/* Expanded KP 4-Pillars Detail */}
                        {isExpanded && (
                          <div className="mt-4 pt-4 border-t border-slate-800/80 space-y-3 text-xs animate-fadeIn">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-slate-300">
                              <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
                                <span className="font-semibold text-indigo-300 block mb-1">
                                  {isTa ? "1. ஆரம்ப விதி (Cuspal Promise):" : "1. Cuspal Promise:"}
                                </span>
                                <p>{item.cuspal_promise_ta}</p>
                              </div>
                              <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
                                <span className="font-semibold text-amber-300 block mb-1">
                                  {isTa ? "2. தசா-புக்தி பங்கு (Dasa Role):" : "2. Dasa-Bhukti Role:"}
                                </span>
                                <p>{item.dasha_bhukti_role_ta}</p>
                              </div>
                            </div>

                            <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-slate-300">
                              <span className="font-semibold text-emerald-300 block mb-1">
                                {isTa ? "3. கோச்சாரத் தூண்டுதல் (Transit Trigger):" : "3. Transit Trigger:"}
                              </span>
                              <p>{item.transit_trigger_ta}</p>
                              {item.trigger_window_dates && (
                                <span className="inline-block mt-2 px-2 py-0.5 rounded bg-slate-800 text-slate-200 text-[11px] font-mono">
                                  {isTa ? "தூண்டும் நாட்கள்:" : "Active Window:"} {item.trigger_window_dates}
                                </span>
                              )}
                            </div>

                            {/* Remedy for this event */}
                            {item.actionable_remedy_ta && (
                              <div className="p-3 rounded-lg bg-amber-950/30 border border-amber-500/20 text-amber-200 flex items-start gap-2">
                                <Flame className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                                <div>
                                  <span className="font-semibold block">
                                    {isTa ? "பரிந்துரைக்கப்படும் எளிய பரிகாரம்:" : "Recommended Remedy:"}
                                  </span>
                                  <p>{item.actionable_remedy_ta}</p>
                                </div>
                              </div>
                            )}

                            {/* Houses Tag */}
                            <div className="flex flex-wrap items-center gap-1.5 pt-1 text-[11px] text-slate-400">
                              <span>{isTa ? "தொடர்புடைய பாவங்கள்:" : "Activated Houses:"}</span>
                              {item.primary_houses.map((h) => (
                                <span
                                  key={h}
                                  className="px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 font-mono border border-indigo-500/30"
                                >
                                  H{h}
                                </span>
                              ))}
                              {item.significator_planets && item.significator_planets.length > 0 && (
                                <>
                                  <span className="ml-2">{isTa ? "காரக கிரகங்கள்:" : "Lords:"}</span>
                                  <span className="text-slate-300 font-mono">
                                    {item.significator_planets.join(", ")}
                                  </span>
                                </>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })
                ) : (
                  <div className="p-8 text-center text-slate-400 text-sm">
                    {isTa ? "இந்த பிரிவில் நிகழ்வுகள் எதுவும் இல்லை." : "No signals in this filter category."}
                  </div>
                )}
              </div>
            </div>

            {/* 4. Strategic Guidance & Remedies Card */}
            <div className="bg-gradient-to-br from-slate-900 to-indigo-950/60 rounded-2xl border border-indigo-500/30 p-6 md:p-8 shadow-xl space-y-6">
              <div className="flex items-center gap-3 border-b border-slate-800 pb-4">
                <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400">
                  <Flame className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    {isTa ? "இக்காலகட்டத்திற்கான செயல் திட்டம் & பரிகாரங்கள்" : "Actionable Wisdom & Remedies"}
                  </h2>
                  <p className="text-xs text-slate-400">
                    {isTa
                      ? "உங்கள் முயற்சிகளை இயற்கை சுழற்சியோடு இணைத்து வெற்றி பெறுவதற்கான வழிகள்"
                      : "Strategic alignment: What to push forward, what to delay, and mindfulness remedies"}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* What to Do Now */}
                <div className="p-5 rounded-2xl bg-slate-950/70 border border-emerald-500/30 space-y-3">
                  <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
                    <CheckCircle2 className="w-5 h-5" />
                    <span>{isTa ? "தற்போது செய்ய வேண்டியவை (Do's)" : "Recommended Initiatives (Do's)"}</span>
                  </div>
                  <ul className="space-y-2 text-xs text-slate-300 list-disc list-inside leading-relaxed">
                    <li>
                      {isTa
                        ? `${predictionData.dasha_hierarchy.mahadasha_ta} தசை நடப்பதால் அக்கிரகத்தின் காரகத்துவங்களை (தொழில்/கல்வி/ஆன்மீகம்) முன்னிறுத்தி திட்டமிடுங்கள்.`
                        : `Leverage ${predictionData.dasha_hierarchy.mahadasha} energy for disciplined long-term plans.`}
                    </li>
                    <li>
                      {isTa
                        ? "சாதகமான பாவங்கள் (2, 6, 10, 11) சுட்டிக்காட்டும் புதிய தொழில் மற்றும் நிதி முயற்சிகளை தைரியமாகத் தொடங்குங்கள்."
                        : "Focus on areas aligned with active houses 2, 6, 10, 11 (career growth, skills, networking)."}
                    </li>
                    <li>
                      {isTa
                        ? "சுப முகூர்த்த நாட்களில் முக்கியமான ஒப்பந்தங்கள் மற்றும் பேச்சுவார்த்தைகளை முடிக்கவும்."
                        : "Schedule key discussions and negotiations during favorable transit windows."}
                    </li>
                  </ul>
                </div>

                {/* What to Avoid */}
                <div className="p-5 rounded-2xl bg-slate-950/70 border border-amber-500/30 space-y-3">
                  <div className="flex items-center gap-2 text-amber-400 font-bold text-sm">
                    <AlertTriangle className="w-5 h-5" />
                    <span>{isTa ? "தவிர்க்க வேண்டியவை (Don'ts)" : "Things to Avoid (Don'ts)"}</span>
                  </div>
                  <ul className="space-y-2 text-xs text-slate-300 list-disc list-inside leading-relaxed">
                    <li>
                      {isTa
                        ? "திடீர் ஊக வணிகம், அவசரக் கடன் கொடுத்தல் அல்லது ஆவணங்களை சரிபார்க்காமல் கையெழுத்திடுவதைத் தவிர்க்கவும்."
                        : "Avoid impulsive speculation, unverified financial lending, and signing contracts without review."}
                    </li>
                    <li>
                      {isTa
                        ? "மன உளைச்சல் அல்லது குடும்ப வாக்குவாதங்களில் பிடிவாதமாக இருப்பதைத் தவிர்த்து அமைதி காக்கவும்."
                        : "De-escalate personal arguments; avoid stubbornness during sensitive planetary transits."}
                    </li>
                    <li>
                      {isTa
                        ? "உடல் உபாதைகள் அல்லது தூக்கமின்மையை அலட்சியப்படுத்தாமல் சீரான உணவு பழக்கத்தைப் பின்பற்றவும்."
                        : "Do not ignore physical fatigue; balance screen time and prioritize restorative sleep."}
                    </li>
                  </ul>
                </div>
              </div>

              {/* Overall Summary Verdict */}
              {predictionData.overall_month_summary_ta && (
                <div className="p-5 rounded-xl bg-slate-950 border border-indigo-500/30 space-y-2">
                  <div className="flex items-center gap-2 text-indigo-300 font-bold text-xs uppercase tracking-wider">
                    <Sparkles className="w-4 h-4 text-amber-400" />
                    <span>{isTa ? "பொதுவான மாத வழிகாட்டல் உரை" : "Period Executive Summary"}</span>
                  </div>
                  <p className="text-sm text-slate-200 leading-relaxed font-sans">
                    {predictionData.overall_month_summary_ta}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function KalaChakraPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
          <div className="flex items-center gap-3 text-amber-400">
            <RefreshCw className="w-6 h-6 animate-spin" />
            <span>Loading KalaChakra Radar...</span>
          </div>
        </div>
      }
    >
      <KalaChakraContent />
    </Suspense>
  );
}
