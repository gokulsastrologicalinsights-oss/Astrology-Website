"use client";

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  MarriagePartnerInput,
  MarriageCompatibilityRequest,
  MarriageCompatibilityResponse,
  CategoryVerdictModel,
  ConflictFindingModel,
  SavedHoroscopeItem,
  SavedMarriageReportDetail,
  SaveMarriageCompatibilityReportRequest,
  HoroscopeResponse,
} from "@/lib/types";
import { SouthIndianChart } from "@/components/charts/SouthIndianChart";
import { NorthIndianChart } from "@/components/charts/NorthIndianChart";
import {
  analyzeMarriageCompatibility,
  saveMarriageCompatibilityReport,
  ApiError,
} from "@/lib/api";
import { SavedMarriageReportsList } from "@/components/marriage-compatibility/SavedMarriageReportsList";
import {
  HeartHandshake,
  User,
  Calendar,
  Clock,
  MapPin,
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Sliders,
  ChevronDown,
  ChevronUp,
  Info,
  Layers,
  ArrowRight,
  Database,
  Scale,
  ShieldAlert,
  HelpCircle,
  BookOpen,
  BookmarkCheck,
  Save,
  X,
  History,
  Eye,
} from "lucide-react";

const ASHTAKOOTA_META_TA: Record<string, { nameTa: string; significanceTa: string }> = {
  "ASHTA-01": { nameTa: "வர்ண கூடம்", significanceTa: "ஆன்ம சுபாவம், அக உணர்வு மற்றும் பரஸ்பர ஈகோ சமநிலை" },
  "ASHTA-02": { nameTa: "வசிய கூடம்", significanceTa: "பரஸ்பர காந்த ஈர்ப்பு, வசீகரம் மற்றும் பிரியமான கட்டுப்பாடு" },
  "ASHTA-03": { nameTa: "தார கூடம்", significanceTa: "நவதாரை பலன், ஆரோக்கியம், ஆயுள் பலம் மற்றும் நல்வாழ்வு" },
  "ASHTA-04": { nameTa: "யோனி கூடம்", significanceTa: "உயிரியல் உடலமைவு, தாம்பத்திய ஈர்ப்பு மற்றும் மிருகப் பகை தவிர்த்தல்" },
  "ASHTA-05": { nameTa: "கிரக மைத்ரி", significanceTa: "ராசிநாதர்களின் நட்பு, மன ஒற்றுமை மற்றும் சிந்தனை உடன்பாடு" },
  "ASHTA-06": { nameTa: "கண கூடம்", significanceTa: "தேவ, மனுஷ, ராக்ஷஸ கண சுபாவம் மற்றும் நடத்தை பொருத்தம்" },
  "ASHTA-07": { nameTa: "பகுட் கூடம்", significanceTa: "குடும்ப சந்தோஷம், வம்சம், மற்றும் 6/8 சஷ்டாஷ்டக தோஷ விலக்கு" },
  "ASHTA-08": { nameTa: "நாடி கூடம்", significanceTa: "மரபணு, ரத்த ஓட்டம், நரம்பு மண்டலம் மற்றும் ஆரோக்கியமான சந்ததி" },
};

const SIGN_NAME_TO_IDX: Record<string, number> = {
  Aries: 1, Taurus: 2, Gemini: 3, Cancer: 4,
  Leo: 5, Virgo: 6, Libra: 7, Scorpio: 8,
  Sagittarius: 9, Capricorn: 10, Aquarius: 11, Pisces: 12,
};

function getUserDefaultTimezone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Kolkata";
  } catch {
    return "Asia/Kolkata";
  }
}

const COMMON_CITIES = [
  { name: "Chennai", lat: "13.0827", lon: "80.2707", tz: "Asia/Kolkata" },
  { name: "Coimbatore", lat: "11.0168", lon: "76.9558", tz: "Asia/Kolkata" },
  { name: "Madurai", lat: "9.9252", lon: "78.1198", tz: "Asia/Kolkata" },
  { name: "Bangalore", lat: "12.9716", lon: "77.5946", tz: "Asia/Kolkata" },
  { name: "Hyderabad", lat: "17.3850", lon: "78.4867", tz: "Asia/Kolkata" },
  { name: "Mumbai", lat: "19.0760", lon: "72.8777", tz: "Asia/Kolkata" },
  { name: "Delhi", lat: "28.6139", lon: "77.2090", tz: "Asia/Kolkata" },
  { name: "Kolkata", lat: "22.5726", lon: "88.3639", tz: "Asia/Kolkata" },
  { name: "Singapore", lat: "1.3521", lon: "103.8198", tz: "Asia/Singapore" },
  { name: "Dubai", lat: "25.2048", lon: "55.2708", tz: "Asia/Dubai" },
  { name: "London", lat: "51.5074", lon: "-0.1278", tz: "Europe/London" },
  { name: "New York", lat: "40.7128", lon: "-74.0060", tz: "America/New_York" },
];

function MarriageCompatibilityContent() {
  const { language } = useLanguage();
  const { session, isAuthenticated } = useAuth();
  const searchParams = useSearchParams();

  // Mode: "manual" or "saved"
  const [groomMode, setGroomMode] = useState<"manual" | "saved">("manual");
  const [brideMode, setBrideMode] = useState<"manual" | "saved">("manual");
  const [savedHoroscopes, setSavedHoroscopes] = useState<SavedHoroscopeItem[]>([]);
  const [loadingSavedList, setLoadingSavedList] = useState<boolean>(false);

  // Groom Form
  const [groomName, setGroomName] = useState<string>("Groom");
  const [groomDate, setGroomDate] = useState<string>("1992-04-14");
  const [groomTime, setGroomTime] = useState<string>("05:30:00");
  const [groomApprox, setGroomApprox] = useState<boolean>(false);
  const [groomTz, setGroomTz] = useState<string>(getUserDefaultTimezone());
  const [groomLat, setGroomLat] = useState<string>("13.0827");
  const [groomLon, setGroomLon] = useState<string>("80.2707");
  const [groomCity, setGroomCity] = useState<string>("Chennai");
  const [groomSavedId, setGroomSavedId] = useState<string>("");

  // Bride Form
  const [brideName, setBrideName] = useState<string>("Bride");
  const [brideDate, setBrideDate] = useState<string>("1994-08-20");
  const [brideTime, setBrideTime] = useState<string>("14:15:00");
  const [brideApprox, setBrideApprox] = useState<boolean>(false);
  const [brideTz, setBrideTz] = useState<string>(getUserDefaultTimezone());
  const [brideLat, setBrideLat] = useState<string>("13.0827");
  const [brideLon, setBrideLon] = useState<string>("80.2707");
  const [brideCity, setBrideCity] = useState<string>("Chennai");
  const [brideSavedId, setBrideSavedId] = useState<string>("");

  // Advanced Calculation Settings
  const [showAdvanced, setShowAdvanced] = useState<boolean>(false);
  const [ayanamsaId, setAyanamsaId] = useState<number>(0);
  const [houseSystemId, setHouseSystemId] = useState<number>(0);
  const [includeKp, setIncludeKp] = useState<boolean>(true);
  const [includeTiming, setIncludeTiming] = useState<boolean>(true);

  // Validation & Execution State
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState<boolean>(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [response, setResponse] = useState<MarriageCompatibilityResponse | null>(null);

  // Results Active Tab
  const [activeTab, setActiveTab] = useState<
    "charts" | "porutham" | "ashtakoota" | "doshas" | "vedic" | "synastry" | "kp" | "conflicts"
  >("charts");

  // Dual Chart Switchers
  const [partnerChartDivision, setPartnerChartDivision] = useState<"d1" | "d9">("d1");
  const [partnerChartStyle, setPartnerChartStyle] = useState<"south" | "north">("south");

  // View Switcher: "analysis" | "saved_reports"
  const [activeView, setActiveView] = useState<"analysis" | "saved_reports">("analysis");

  // Historical Report State
  const [viewingHistoricalReport, setViewingHistoricalReport] = useState<SavedMarriageReportDetail | null>(null);

  // Save Modal & Status State
  const [isSaveModalOpen, setIsSaveModalOpen] = useState<boolean>(false);
  const [saveTitle, setSaveTitle] = useState<string>("");
  const [savingReport, setSavingReport] = useState<boolean>(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [savedReportRecord, setSavedReportRecord] = useState<{ id: string; display_number: number } | null>(null);
  const [refreshSavedTrigger, setRefreshSavedTrigger] = useState<number>(0);

  // Sync with searchParams
  useEffect(() => {
    const viewParam = searchParams.get("view");
    if (viewParam === "saved") {
      setActiveView("saved_reports");
    }
  }, [searchParams]);

  const handleOpenSavedReport = (report: SavedMarriageReportDetail) => {
    setViewingHistoricalReport(report);
    setResponse(report.report_data as unknown as MarriageCompatibilityResponse);
    setSavedReportRecord({ id: report.id, display_number: report.display_number });
    setActiveView("analysis");
    setTimeout(() => {
      const el = document.getElementById("compatibility-results");
      if (el) el.scrollIntoView({ behavior: "smooth" });
    }, 100);
  };

  const handleCloseHistoricalReport = () => {
    setViewingHistoricalReport(null);
    setSavedReportRecord(null);
  };

  const handleOpenSaveModal = () => {
    if (!response) return;
    setSaveError(null);
    setSaveTitle(`${groomName || "Groom"} & ${brideName || "Bride"} Compatibility`);
    setIsSaveModalOpen(true);
  };

  const handleConfirmSave = async () => {
    if (!response || !session?.access_token) return;
    setSavingReport(true);
    setSaveError(null);
    try {
      const payload: SaveMarriageCompatibilityReportRequest = {
        title: saveTitle.trim() || `${groomName || "Groom"} & ${brideName || "Bride"} Compatibility`,
        groom_name: groomName || "Groom",
        bride_name: brideName || "Bride",
        groom_birth_date: groomDate ? `${groomDate}T${groomTime || "12:00"}:00` : new Date().toISOString(),
        bride_birth_date: brideDate ? `${brideDate}T${brideTime || "12:00"}:00` : new Date().toISOString(),
        overall_outcome: response.composite_assessment.overall_outcome,
        groom_saved_horoscope_id: groomMode === "saved" && groomSavedId ? groomSavedId : undefined,
        bride_saved_horoscope_id: brideMode === "saved" && brideSavedId ? brideSavedId : undefined,
        report_data: response,
      };

      const saved = await saveMarriageCompatibilityReport(payload, session.access_token);
      setSavedReportRecord({ id: saved.id, display_number: saved.display_number });
      setIsSaveModalOpen(false);
      setRefreshSavedTrigger((prev) => prev + 1);
    } catch (err: any) {
      console.error("Failed to save marriage report:", err);
      setSaveError(err?.message || "Failed to save compatibility report. Please try again.");
    } finally {
      setSavingReport(false);
    }
  };

  // Fetch saved horoscopes if authenticated
  useEffect(() => {
    if (!isAuthenticated) return;
    let isMounted = true;
    setLoadingSavedList(true);
    fetch("/api/horoscopes?page=1&limit=50", { cache: "no-store" })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (isMounted && data?.horoscopes) {
          setSavedHoroscopes(data.horoscopes);
        }
      })
      .catch((err) => {
        console.warn("Could not load saved horoscopes:", err);
      })
      .finally(() => {
        if (isMounted) setLoadingSavedList(false);
      });
    return () => {
      isMounted = false;
    };
  }, [isAuthenticated]);

  const handleGroomCityChange = (cityName: string) => {
    setGroomCity(cityName);
    const found = COMMON_CITIES.find((c) => c.name === cityName);
    if (found) {
      setGroomLat(found.lat);
      setGroomLon(found.lon);
      setGroomTz(found.tz);
    }
  };

  const handleBrideCityChange = (cityName: string) => {
    setBrideCity(cityName);
    const found = COMMON_CITIES.find((c) => c.name === cityName);
    if (found) {
      setBrideLat(found.lat);
      setBrideLon(found.lon);
      setBrideTz(found.tz);
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    // Validate Groom
    if (groomMode === "saved") {
      if (!groomSavedId) {
        errors.groomSaved = language === "ta" ? "ஜாதகத்தை தேர்ந்தெடுக்கவும்" : "Select saved horoscope";
      }
    } else {
      if (!groomDate) {
        errors.groomDate = language === "ta" ? "பிறந்த தேதி தேவை" : "Birth date required";
      }
      if (!groomTime) {
        errors.groomTime = language === "ta" ? "பிறந்த நேரம் தேவை" : "Birth time required";
      }
      const latNum = parseFloat(groomLat);
      if (isNaN(latNum) || latNum < -90 || latNum > 90) {
        errors.groomLat = language === "ta" ? "அட்சரேகை செல்லுபடியாகவில்லை (-90 முதல் 90)" : "Invalid latitude (-90 to 90)";
      }
      const lonNum = parseFloat(groomLon);
      if (isNaN(lonNum) || lonNum < -180 || lonNum > 180) {
        errors.groomLon = language === "ta" ? "தீர்க்கரேகை செல்லுபடியாகவில்லை (-180 முதல் 180)" : "Invalid longitude (-180 to 180)";
      }
    }

    // Validate Bride
    if (brideMode === "saved") {
      if (!brideSavedId) {
        errors.brideSaved = language === "ta" ? "ஜாதகத்தை தேர்ந்தெடுக்கவும்" : "Select saved horoscope";
      }
    } else {
      if (!brideDate) {
        errors.brideDate = language === "ta" ? "பிறந்த தேதி தேவை" : "Birth date required";
      }
      if (!brideTime) {
        errors.brideTime = language === "ta" ? "பிறந்த நேரம் தேவை" : "Birth time required";
      }
      const latNum = parseFloat(brideLat);
      if (isNaN(latNum) || latNum < -90 || latNum > 90) {
        errors.brideLat = language === "ta" ? "அட்சரேகை செல்லுபடியாகவில்லை (-90 முதல் 90)" : "Invalid latitude (-90 to 90)";
      }
      const lonNum = parseFloat(brideLon);
      if (isNaN(lonNum) || lonNum < -180 || lonNum > 180) {
        errors.brideLon = language === "ta" ? "தீர்க்கரேகை செல்லுபடியாகவில்லை (-180 முதல் 180)" : "Invalid longitude (-180 to 180)";
      }
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    setApiError(null);

    const groomInput: MarriagePartnerInput =
      groomMode === "saved"
        ? { name: groomName, gender: "male", saved_horoscope_id: groomSavedId }
        : {
            name: groomName || "Groom",
            gender: "male",
            birth_date: groomDate,
            birth_time: groomTime.length === 5 ? `${groomTime}:00` : groomTime,
            is_birth_time_approximate: groomApprox,
            timezone: groomTz,
            latitude: parseFloat(groomLat),
            longitude: parseFloat(groomLon),
          };

    const brideInput: MarriagePartnerInput =
      brideMode === "saved"
        ? { name: brideName, gender: "female", saved_horoscope_id: brideSavedId }
        : {
            name: brideName || "Bride",
            gender: "female",
            birth_date: brideDate,
            birth_time: brideTime.length === 5 ? `${brideTime}:00` : brideTime,
            is_birth_time_approximate: brideApprox,
            timezone: brideTz,
            latitude: parseFloat(brideLat),
            longitude: parseFloat(brideLon),
          };

    const payload: MarriageCompatibilityRequest = {
      groom: groomInput,
      bride: brideInput,
      rule_system: "all",
      ayanamsa_id: ayanamsaId,
      house_system_id: houseSystemId,
      include_kp: includeKp,
      include_timing: includeTiming,
    };

    try {
      const res = await analyzeMarriageCompatibility(payload, session?.access_token);
      setResponse(res);
      // Scroll to results
      setTimeout(() => {
        const el = document.getElementById("compatibility-results");
        if (el) el.scrollIntoView({ behavior: "smooth" });
      }, 100);
    } catch (err: any) {
      console.error("Marriage Compatibility API Error:", err);
      if (err instanceof ApiError) {
        const msg = err.data?.detail || err.message;
        setApiError(msg);
      } else {
        setApiError(err?.message || "Failed to calculate marriage compatibility. Please check birth parameters.");
      }
    } finally {
      setLoading(false);
    }
  };

  const getVerdictBadgeStyle = (outcome: string) => {
    switch (outcome) {
      case "FAVOURABLE_UNDER_SELECTED_RULES":
        return {
          bg: "bg-emerald-50 border-emerald-300 text-emerald-800",
          dot: "bg-emerald-500",
          icon: CheckCircle2,
        };
      case "MIXED_OR_CONDITIONAL":
        return {
          bg: "bg-amber-50 border-amber-300 text-amber-800",
          dot: "bg-amber-500",
          icon: AlertTriangle,
        };
      case "UNFAVOURABLE_UNDER_SELECTED_RULES":
        return {
          bg: "bg-rose-50 border-rose-300 text-rose-800",
          dot: "bg-rose-500",
          icon: ShieldAlert,
        };
      default:
        return {
          bg: "bg-slate-50 border-slate-300 text-slate-800",
          dot: "bg-slate-400",
          icon: HelpCircle,
        };
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] pb-24 text-slate-800">
      {/* Breadcrumbs & Header */}
      <div className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Breadcrumbs
            items={[
              { label: language === "ta" ? "முகப்பு" : "Home", href: "/" },
              { label: language === "ta" ? "கருவிகள்" : "Tools", href: "/tools" },
              { label: language === "ta" ? "திருமணப் பொருத்தம்" : "Marriage Compatibility" },
            ]}
          />
          <div className="mt-3 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80] mb-2">
                <HeartHandshake className="w-3.5 h-3.5 text-[#B8862B]" />
                <span>Kundli Matching &amp; 36 Ashta Kuta Compatibility Studio</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold text-[#153F6B] flex items-center gap-3">
                {language === "ta"
                  ? "திருமணப் பொருத்தம் & 36 அஷ்டகூட ஆய்வுக்கூடம்"
                  : "Kundli Matching & 36 Ashta Kuta Compatibility Studio"}
              </h1>
              <p className="mt-1 text-sm text-slate-600 max-w-3xl">
                {language === "ta"
                  ? "தமிழ் 10 பொருத்தங்கள் (தின, கண, மகேந்திர, ஸ்திரீ தீர்க்க, யோனி, ராசி, ராசி அதிபதி, வசிய, ரஜ்ஜு, வேத), வட இந்திய 36 அஷ்டகூடம் (வர்ண, வசிய, தார, யோனி, மைத்ரி, கண, பகுட், நாடி), செவ்வாய் தோஷ சமதோஷம், பாபசாம்யம் மற்றும் இருவர் D1/D9 சக்கரங்கள்."
                  : "Comprehensive multi-tradition synastry: Tamil 10 Poruthams (Dina, Gana, Mahendra, Stree-Deergha, Yoni, Rasi, Rasyadhipati, Vasya, Rajju, Vedha), North Indian 36-Point Ashtakoota, Kuja / Manglik Samadosham, Papasamya, and side-by-side D1/D9 Kundli visualizer."}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[#FAF2DE] text-[#B4872B] border border-[#B4872B]/30">
                <Sparkles className="w-3.5 h-3.5" />
                Deterministic &amp; Source-Backed
              </span>
            </div>
          </div>

          {/* View Mode Navigation Tabs */}
          <div className="mt-6 flex items-center gap-2 border-b border-slate-200">
            <button
              type="button"
              onClick={() => setActiveView("analysis")}
              className={`pb-3 px-4 text-sm font-bold border-b-2 flex items-center gap-2 transition ${
                activeView === "analysis"
                  ? "border-[#153F6B] text-[#153F6B]"
                  : "border-transparent text-slate-500 hover:text-slate-700"
              }`}
            >
              <HeartHandshake className="w-4 h-4" />
              {language === "ta" ? "பொருத்த ஆய்வு" : "Compatibility Analysis"}
            </button>
            <button
              type="button"
              onClick={() => setActiveView("saved_reports")}
              className={`pb-3 px-4 text-sm font-bold border-b-2 flex items-center gap-2 transition ${
                activeView === "saved_reports"
                  ? "border-[#153F6B] text-[#153F6B]"
                  : "border-transparent text-slate-500 hover:text-slate-700"
              }`}
            >
              <BookmarkCheck className="w-4 h-4 text-[#B4872B]" />
              {language === "ta" ? "சேமிக்கப்பட்ட அறிக்கைகள்" : "Saved Reports"}
            </button>
          </div>
        </div>
      </div>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        {activeView === "saved_reports" ? (
          <SavedMarriageReportsList
            onOpenReport={handleOpenSavedReport}
            language={language}
            refreshTrigger={refreshSavedTrigger}
          />
        ) : (
          <>
            {/* Historical Snapshot Banner if viewing loaded report */}
            {viewingHistoricalReport && (
              <div className="mb-6 p-4 rounded-xl bg-amber-50/90 border border-amber-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-sm">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-[#FAF2DE] border border-[#B4872B]/30 flex items-center justify-center shrink-0">
                    <History className="w-5 h-5 text-[#B4872B]" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded text-[11px] font-extrabold bg-[#153F6B] text-white">
                        Report #{viewingHistoricalReport.display_number}
                      </span>
                      <h3 className="font-bold text-slate-800 text-sm">
                        {viewingHistoricalReport.title}
                      </h3>
                    </div>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {language === "ta"
                        ? `சேமிக்கப்பட்ட வரலாற்று அறிக்கை • ${new Date(viewingHistoricalReport.created_at).toLocaleDateString()} • மாற்ற முடியாத கணக்கீட்டு நகல்`
                        : `Historical snapshot saved on ${new Date(viewingHistoricalReport.created_at).toLocaleDateString()} • Read-only immutable calculation record`}
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={handleCloseHistoricalReport}
                  className="px-3.5 py-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-xs font-semibold text-slate-700 flex items-center gap-1.5 shrink-0 self-start sm:self-auto"
                >
                  <X className="w-3.5 h-3.5" />
                  {language === "ta" ? "மூடுக" : "Close Historical View"}
                </button>
              </div>
            )}

            {/* Form Container */}
            <form onSubmit={handleAnalyze} className="space-y-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* GROOM CARD */}
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
              <div className="bg-gradient-to-r from-[#153F6B] to-[#1E5692] px-6 py-4 text-white flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-full bg-white/10 flex items-center justify-center font-bold">
                    ♂
                  </div>
                  <div>
                    <h2 className="text-lg font-bold">
                      {language === "ta" ? "மணமகன் விவரங்கள்" : "Groom Particulars"}
                    </h2>
                    <span className="text-xs text-white/80">
                      {language === "ta" ? "முதன்மை ஜாதகம் (ஆண்)" : "Partner 1 (Male)"}
                    </span>
                  </div>
                </div>
                {isAuthenticated && (
                  <div className="flex bg-white/10 p-1 rounded-lg text-xs">
                    <button
                      type="button"
                      onClick={() => setGroomMode("manual")}
                      className={`px-2.5 py-1 rounded-md transition ${
                        groomMode === "manual" ? "bg-white text-[#153F6B] font-bold shadow-sm" : "text-white/80"
                      }`}
                    >
                      {language === "ta" ? "நேரடி உள்ளீடு" : "Direct Input"}
                    </button>
                    <button
                      type="button"
                      onClick={() => setGroomMode("saved")}
                      className={`px-2.5 py-1 rounded-md transition ${
                        groomMode === "saved" ? "bg-white text-[#153F6B] font-bold shadow-sm" : "text-white/80"
                      }`}
                    >
                      {language === "ta" ? "சேமிக்கப்பட்டவை" : "Saved Chart"}
                    </button>
                  </div>
                )}
              </div>

              <div className="p-6 space-y-5 flex-1">
                {groomMode === "saved" ? (
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">
                      {language === "ta" ? "சேமிக்கப்பட்ட ஜாதகத்தைத் தேர்ந்தெடுக்கவும்" : "Select Saved Horoscope"} *
                    </label>
                    <select
                      value={groomSavedId}
                      onChange={(e) => setGroomSavedId(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-[#153F6B] focus:border-[#153F6B]"
                    >
                      <option value="">{language === "ta" ? "-- தேர்வு செய்க --" : "-- Select Horoscope --"}</option>
                      {savedHoroscopes.map((h) => (
                        <option key={h.id} value={h.id}>
                          {h.person_name || "Horoscope"} ({h.birth_date} {h.birth_time})
                        </option>
                      ))}
                    </select>
                    {validationErrors.groomSaved && (
                      <p className="text-xs text-rose-600 mt-1">{validationErrors.groomSaved}</p>
                    )}
                  </div>
                ) : (
                  <>
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">
                        {language === "ta" ? "மணமகன் பெயர்" : "Groom Name"} ({language === "ta" ? "விருப்பத்தேர்வு" : "Optional"})
                      </label>
                      <input
                        type="text"
                        value={groomName}
                        onChange={(e) => setGroomName(e.target.value)}
                        placeholder="e.g. Karthik"
                        className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-[#153F6B] focus:border-[#153F6B]"
                      />
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">
                          {language === "ta" ? "பிறந்த தேதி" : "Birth Date"} *
                        </label>
                        <input
                          type="date"
                          value={groomDate}
                          onChange={(e) => setGroomDate(e.target.value)}
                          className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-[#153F6B] focus:border-[#153F6B]"
                        />
                        {validationErrors.groomDate && (
                          <p className="text-xs text-rose-600 mt-1">{validationErrors.groomDate}</p>
                        )}
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">
                          {language === "ta" ? "பிறந்த நேரம்" : "Birth Time (24h)"} *
                        </label>
                        <input
                          type="time"
                          step="1"
                          value={groomTime}
                          onChange={(e) => setGroomTime(e.target.value)}
                          className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-[#153F6B] focus:border-[#153F6B]"
                        />
                        {validationErrors.groomTime && (
                          <p className="text-xs text-rose-600 mt-1">{validationErrors.groomTime}</p>
                        )}
                      </div>
                    </div>

                    {/* Approximate checkbox */}
                    <div className="flex items-center gap-2 pt-1">
                      <input
                        type="checkbox"
                        id="groomApprox"
                        checked={groomApprox}
                        onChange={(e) => setGroomApprox(e.target.checked)}
                        className="w-4 h-4 text-[#153F6B] rounded border-slate-300 focus:ring-[#153F6B]"
                      />
                      <label htmlFor="groomApprox" className="text-xs text-slate-700 select-none">
                        {language === "ta"
                          ? "பிறப்பு நேரம் தோராயமானது அல்லது நிச்சயமற்றது"
                          : "Birth time is approximate / uncertain (propagates sensitivity checks)"}
                      </label>
                    </div>

                    {/* Location Presets */}
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">
                        {language === "ta" ? "பிறந்த ஊர்" : "Birth City / Location"}
                      </label>
                      <select
                        value={groomCity}
                        onChange={(e) => handleGroomCityChange(e.target.value)}
                        className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-[#153F6B] focus:border-[#153F6B]"
                      >
                        {COMMON_CITIES.map((c) => (
                          <option key={c.name} value={c.name}>
                            {c.name}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div>
                        <span className="text-slate-500">{language === "ta" ? "அட்சரேகை" : "Latitude"}:</span>
                        <input
                          type="text"
                          value={groomLat}
                          onChange={(e) => setGroomLat(e.target.value)}
                          className="w-full mt-1 px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs text-slate-700"
                        />
                        {validationErrors.groomLat && (
                          <p className="text-xs text-rose-600 mt-0.5">{validationErrors.groomLat}</p>
                        )}
                      </div>
                      <div>
                        <span className="text-slate-500">{language === "ta" ? "தீர்க்கரேகை" : "Longitude"}:</span>
                        <input
                          type="text"
                          value={groomLon}
                          onChange={(e) => setGroomLon(e.target.value)}
                          className="w-full mt-1 px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs text-slate-700"
                        />
                        {validationErrors.groomLon && (
                          <p className="text-xs text-rose-600 mt-0.5">{validationErrors.groomLon}</p>
                        )}
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* BRIDE CARD */}
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
              <div className="bg-gradient-to-r from-[#B4872B] to-[#996F1D] px-6 py-4 text-white flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-full bg-white/10 flex items-center justify-center font-bold">
                    ♀
                  </div>
                  <div>
                    <h2 className="text-lg font-bold">
                      {language === "ta" ? "மணமகள் விவரங்கள்" : "Bride Particulars"}
                    </h2>
                    <span className="text-xs text-white/80">
                      {language === "ta" ? "இணை ஜாதகம் (பெண்)" : "Partner 2 (Female)"}
                    </span>
                  </div>
                </div>
                {isAuthenticated && (
                  <div className="flex bg-white/10 p-1 rounded-lg text-xs">
                    <button
                      type="button"
                      onClick={() => setBrideMode("manual")}
                      className={`px-2.5 py-1 rounded-md transition ${
                        brideMode === "manual" ? "bg-white text-[#B4872B] font-bold shadow-sm" : "text-white/80"
                      }`}
                    >
                      {language === "ta" ? "நேரடி உள்ளீடு" : "Direct Input"}
                    </button>
                    <button
                      type="button"
                      onClick={() => setBrideMode("saved")}
                      className={`px-2.5 py-1 rounded-md transition ${
                        brideMode === "saved" ? "bg-white text-[#B4872B] font-bold shadow-sm" : "text-white/80"
                      }`}
                    >
                      {language === "ta" ? "சேமிக்கப்பட்டவை" : "Saved Chart"}
                    </button>
                  </div>
                )}
              </div>

              <div className="p-6 space-y-5 flex-1">
                {brideMode === "saved" ? (
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">
                      {language === "ta" ? "சேமிக்கப்பட்ட ஜாதகத்தைத் தேர்ந்தெடுக்கவும்" : "Select Saved Horoscope"} *
                    </label>
                    <select
                      value={brideSavedId}
                      onChange={(e) => setBrideSavedId(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-[#B4872B] focus:border-[#B4872B]"
                    >
                      <option value="">{language === "ta" ? "-- தேர்வு செய்க --" : "-- Select Horoscope --"}</option>
                      {savedHoroscopes.map((h) => (
                        <option key={h.id} value={h.id}>
                          {h.person_name || "Horoscope"} ({h.birth_date} {h.birth_time})
                        </option>
                      ))}
                    </select>
                    {validationErrors.brideSaved && (
                      <p className="text-xs text-rose-600 mt-1">{validationErrors.brideSaved}</p>
                    )}
                  </div>
                ) : (
                  <>
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">
                        {language === "ta" ? "மணமகள் பெயர்" : "Bride Name"} ({language === "ta" ? "விருப்பத்தேர்வு" : "Optional"})
                      </label>
                      <input
                        type="text"
                        value={brideName}
                        onChange={(e) => setBrideName(e.target.value)}
                        placeholder="e.g. Revathi"
                        className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-[#B4872B] focus:border-[#B4872B]"
                      />
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">
                          {language === "ta" ? "பிறந்த தேதி" : "Birth Date"} *
                        </label>
                        <input
                          type="date"
                          value={brideDate}
                          onChange={(e) => setBrideDate(e.target.value)}
                          className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-[#B4872B] focus:border-[#B4872B]"
                        />
                        {validationErrors.brideDate && (
                          <p className="text-xs text-rose-600 mt-1">{validationErrors.brideDate}</p>
                        )}
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">
                          {language === "ta" ? "பிறந்த நேரம்" : "Birth Time (24h)"} *
                        </label>
                        <input
                          type="time"
                          step="1"
                          value={brideTime}
                          onChange={(e) => setBrideTime(e.target.value)}
                          className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-[#B4872B] focus:border-[#B4872B]"
                        />
                        {validationErrors.brideTime && (
                          <p className="text-xs text-rose-600 mt-1">{validationErrors.brideTime}</p>
                        )}
                      </div>
                    </div>

                    {/* Approximate checkbox */}
                    <div className="flex items-center gap-2 pt-1">
                      <input
                        type="checkbox"
                        id="brideApprox"
                        checked={brideApprox}
                        onChange={(e) => setBrideApprox(e.target.checked)}
                        className="w-4 h-4 text-[#B4872B] rounded border-slate-300 focus:ring-[#B4872B]"
                      />
                      <label htmlFor="brideApprox" className="text-xs text-slate-700 select-none">
                        {language === "ta"
                          ? "பிறப்பு நேரம் தோராயமானது அல்லது நிச்சயமற்றது"
                          : "Birth time is approximate / uncertain (propagates sensitivity checks)"}
                      </label>
                    </div>

                    {/* Location Presets */}
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">
                        {language === "ta" ? "பிறந்த ஊர்" : "Birth City / Location"}
                      </label>
                      <select
                        value={brideCity}
                        onChange={(e) => handleBrideCityChange(e.target.value)}
                        className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-[#B4872B] focus:border-[#B4872B]"
                      >
                        {COMMON_CITIES.map((c) => (
                          <option key={c.name} value={c.name}>
                            {c.name}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div>
                        <span className="text-slate-500">{language === "ta" ? "அட்சரேகை" : "Latitude"}:</span>
                        <input
                          type="text"
                          value={brideLat}
                          onChange={(e) => setBrideLat(e.target.value)}
                          className="w-full mt-1 px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs text-slate-700"
                        />
                        {validationErrors.brideLat && (
                          <p className="text-xs text-rose-600 mt-0.5">{validationErrors.brideLat}</p>
                        )}
                      </div>
                      <div>
                        <span className="text-slate-500">{language === "ta" ? "தீர்க்கரேகை" : "Longitude"}:</span>
                        <input
                          type="text"
                          value={brideLon}
                          onChange={(e) => setBrideLon(e.target.value)}
                          className="w-full mt-1 px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs text-slate-700"
                        />
                        {validationErrors.brideLon && (
                          <p className="text-xs text-rose-600 mt-0.5">{validationErrors.brideLon}</p>
                        )}
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Advanced Astrological Calculation Settings Toggle */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="flex items-center justify-between w-full text-left text-sm font-semibold text-slate-700"
            >
              <span className="flex items-center gap-2">
                <Sliders className="w-4 h-4 text-[#153F6B]" />
                {language === "ta" ? "கூடுதல் கணக்கீட்டு அமைப்புகள்" : "Advanced Calculation Settings"}
              </span>
              {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {showAdvanced && (
              <div className="mt-4 pt-4 border-t border-slate-100 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                <div>
                  <label className="block font-semibold text-slate-600 mb-1">
                    {language === "ta" ? "அயனாம்சம்" : "Ayanamsa System"}
                  </label>
                  <select
                    value={ayanamsaId}
                    onChange={(e) => setAyanamsaId(parseInt(e.target.value, 10))}
                    className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 text-xs"
                  >
                    <option value={0}>Lahiri (Chitrapaksha) - Standard</option>
                    <option value={1}>KP (Krishnamurti)</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-slate-600 mb-1">
                    {language === "ta" ? "பாவ ஆரம்ப முறை" : "House System"}
                  </label>
                  <select
                    value={houseSystemId}
                    onChange={(e) => setHouseSystemId(parseInt(e.target.value, 10))}
                    className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 text-xs"
                  >
                    <option value={0}>Whole Sign (Rasi Bhava) - Vedic Default</option>
                    <option value={2}>Placidus - KP Default</option>
                  </select>
                </div>

                <div className="flex items-center gap-2 pt-4">
                  <input
                    type="checkbox"
                    id="includeKp"
                    checked={includeKp}
                    onChange={(e) => setIncludeKp(e.target.checked)}
                    className="w-4 h-4 text-[#153F6B] rounded border-slate-300"
                  />
                  <label htmlFor="includeKp" className="text-slate-700">
                    {language === "ta" ? "கே.பி 7-ம் பாவ ஆய்வு" : "Include KP 7th CSL"}
                  </label>
                </div>

                <div className="flex items-center gap-2 pt-4">
                  <input
                    type="checkbox"
                    id="includeTiming"
                    checked={includeTiming}
                    onChange={(e) => setIncludeTiming(e.target.checked)}
                    className="w-4 h-4 text-[#153F6B] rounded border-slate-300"
                  />
                  <label htmlFor="includeTiming" className="text-slate-700">
                    {language === "ta" ? "தசா-புக்தி கால அமைவு" : "Include Dasa Timing"}
                  </label>
                </div>
              </div>
            )}
          </div>

          {/* Error Banner */}
          {apiError && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
              <div>
                <p className="font-bold">{language === "ta" ? "கணக்கீட்டுப் பிழை" : "Analysis Error"}</p>
                <p className="mt-0.5 text-xs text-rose-700">{apiError}</p>
              </div>
            </div>
          )}

          {/* Submit Action */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
            <div className="text-xs text-slate-500 flex items-center gap-1.5">
              <ShieldAlert className="w-4 h-4 text-slate-400" />
              <span>
                {language === "ta"
                  ? "நேரடி உள்ளீட்டு விவரங்கள் தற்காலிகமாக மட்டுமே கணக்கிடப்படும்; தரவுத்தளத்தில் சேமிக்கப்படாது."
                  : "Transient birth inputs are processed entirely in-memory and never persisted."}
              </span>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-gradient-to-r from-[#153F6B] to-[#1E5692] text-white font-bold text-base shadow-lg shadow-[#153F6B]/20 hover:from-[#1E5692] hover:to-[#153F6B] disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  <span>{language === "ta" ? "பொருத்தம் கணிக்கப்படுகிறது..." : "Analyzing Compatibility..."}</span>
                </>
              ) : (
                <>
                  <Scale className="w-5 h-5 text-[#B4872B]" />
                  <span>{language === "ta" ? "பொருத்தம் கணிக்க" : "Analyze Compatibility"}</span>
                </>
              )}
            </button>
          </div>
        </form>

        {/* RESULTS SECTION */}
        {response && (
          <div id="compatibility-results" className="mt-12 space-y-8 animate-fadeIn">
            {/* 1. MASTER ASSESSMENT HERO CARD */}
            {(() => {
              const comp = response.composite_assessment;
              const badge = getVerdictBadgeStyle(comp.overall_outcome);
              const BadgeIcon = badge.icon;

              return (
                <div className="bg-white rounded-2xl border border-slate-200 shadow-md p-6 sm:p-8">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-100">
                    <div>
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                        {language === "ta" ? "ஒருங்கிணைந்த இறுதி முடிவு" : "Master Composite Assessment"}
                      </span>
                      <h2 className="text-2xl sm:text-3xl font-extrabold text-[#153F6B] mt-1">
                        {language === "ta" ? comp.overall_outcome_label_ta : comp.overall_outcome_label_en}
                      </h2>
                      <p className="mt-1 text-sm text-slate-600">
                        {language === "ta" ? comp.explanation_ta : comp.explanation_en}
                      </p>
                    </div>

                    <div className="flex flex-wrap items-center gap-3">
                      <div className={`px-4 py-2.5 rounded-xl border flex items-center gap-2.5 ${badge.bg}`}>
                        <BadgeIcon className="w-5 h-5 shrink-0" />
                        <span className="font-bold text-sm">
                          {comp.overall_outcome.replace(/_/g, " ")}
                        </span>
                      </div>

                      {/* Save Report Action / Saved Status */}
                      {savedReportRecord ? (
                        <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 px-3 py-2 rounded-xl">
                          <span className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-800">
                            <BookmarkCheck className="w-4 h-4 text-emerald-600" />
                            {language === "ta"
                              ? `சேமிக்கப்பட்டது (#${savedReportRecord.display_number})`
                              : `Saved (#${savedReportRecord.display_number})`}
                          </span>
                          <button
                            type="button"
                            onClick={() => setActiveView("saved_reports")}
                            className="text-xs font-semibold text-[#153F6B] hover:underline ml-1"
                          >
                            {language === "ta" ? "அனைத்தையும் பார்க்க" : "View All"}
                          </button>
                        </div>
                      ) : !viewingHistoricalReport ? (
                        <button
                          type="button"
                          onClick={handleOpenSaveModal}
                          disabled={savingReport}
                          className="px-4 py-2.5 rounded-xl bg-[#FAF2DE] hover:bg-[#F3E5BE] text-[#B4872B] border border-[#B4872B]/40 font-bold text-xs flex items-center gap-2 shadow-sm transition disabled:opacity-50"
                        >
                          {savingReport ? (
                            <>
                              <RefreshCw className="w-4 h-4 animate-spin" />
                              <span>{language === "ta" ? "சேமிக்கப்படுகிறது..." : "Saving..."}</span>
                            </>
                          ) : (
                            <>
                              <Save className="w-4 h-4" />
                              <span>{language === "ta" ? "அறிக்கையைச் சேமிக்க" : "Save Report"}</span>
                            </>
                          )}
                        </button>
                      ) : null}
                    </div>
                  </div>

                  {/* Summary Columns: Strengths & Cautions */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                    <div className="p-4 rounded-xl bg-emerald-50/50 border border-emerald-100 space-y-2">
                      <h3 className="text-xs font-bold text-emerald-800 uppercase tracking-wider flex items-center gap-1.5">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        {language === "ta" ? "முதன்மை சாதகங்கள்" : "Key Supportive Factors"}
                      </h3>
                      <ul className="text-xs text-slate-700 space-y-1.5 list-disc list-inside">
                        {comp.major_supportive_indicators.length > 0 ? (
                          comp.major_supportive_indicators.map((ind, i) => <li key={i}>{ind}</li>)
                        ) : (
                          <li className="text-slate-400 italic">No prominent supportive factors isolated.</li>
                        )}
                      </ul>
                    </div>

                    <div className="p-4 rounded-xl bg-amber-50/50 border border-amber-100 space-y-2">
                      <h3 className="text-xs font-bold text-amber-800 uppercase tracking-wider flex items-center gap-1.5">
                        <AlertTriangle className="w-4 h-4 text-amber-600" />
                        {language === "ta" ? "கவனிக்கப்பட வேண்டியவை" : "Considerations & Mitigations"}
                      </h3>
                      <ul className="text-xs text-slate-700 space-y-1.5 list-disc list-inside">
                        {comp.major_challenging_indicators.length > 0 ? (
                          comp.major_challenging_indicators.map((ind, i) => <li key={i}>{ind}</li>)
                        ) : (
                          <li className="text-slate-400 italic">No severe afflictions detected.</li>
                        )}
                      </ul>
                    </div>
                  </div>

                  {/* Category Status Cards Grid */}
                  <div className="mt-6 pt-6 border-t border-slate-100">
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
                      {language === "ta" ? "ஆய்வு செய்யப்பட்ட துறைகள்" : "Independent Evaluation Layers"}
                    </h3>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-2.5">
                      {Object.values(comp.category_verdicts).map((cv) => {
                        const style = getVerdictBadgeStyle(cv.status);
                        return (
                          <div
                            key={cv.category_id}
                            className={`p-3 rounded-xl border text-center transition ${style.bg}`}
                          >
                            <span className="block text-[11px] font-bold truncate">
                              {language === "ta" ? cv.category_name_ta : cv.category_name_en}
                            </span>
                            <span className="inline-block mt-1 px-2 py-0.5 rounded text-[10px] font-extrabold uppercase bg-white/70">
                              {cv.status}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Missing or Uncertain Evidence & Sensitivity Advisory */}
                  {comp.missing_or_uncertain_evidence && comp.missing_or_uncertain_evidence.length > 0 && (
                    <div className="mt-6 p-4 rounded-xl bg-amber-50/70 border border-amber-200 text-xs text-amber-900 space-y-2">
                      <div className="flex items-center gap-2 font-bold text-amber-800">
                        <AlertTriangle className="w-4 h-4 shrink-0 text-amber-600" />
                        <span>
                          {language === "ta"
                            ? "நிச்சயமற்ற அல்லது கூடுதல் ஆய்வு தேவைப்படும் காரணிகள்"
                            : "Missing Evidence & Sensitivity Advisory"}
                        </span>
                      </div>
                      <ul className="space-y-1 list-disc list-inside text-slate-700">
                        {comp.missing_or_uncertain_evidence.map((item, idx) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Recommended Astrologer Review Points */}
                  {comp.recommended_astrologer_review && comp.recommended_astrologer_review.length > 0 && (
                    <div className="mt-4 p-4 rounded-xl bg-blue-50/60 border border-blue-200 text-xs text-blue-900 space-y-2">
                      <div className="flex items-center gap-2 font-bold text-blue-800">
                        <BookOpen className="w-4 h-4 shrink-0 text-blue-600" />
                        <span>
                          {language === "ta"
                            ? "நேரடி ஜோதிடர் ஆலோசனையின் போது கவனிக்க வேண்டியவை"
                            : "Recommended Areas for In-Person Astrological Consultation"}
                        </span>
                      </div>
                      <ul className="space-y-1 list-disc list-inside text-slate-700">
                        {comp.recommended_astrologer_review.map((item, idx) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Mandatory Ethical Non-Guarantee Disclaimer */}
                  <div className="mt-6 p-4 rounded-xl bg-[#FAF2DE]/50 border border-[#B4872B]/30 text-xs text-slate-700 space-y-1.5">
                    <div className="flex items-center gap-2 font-bold text-[#B4872B]">
                      <Info className="w-4 h-4 shrink-0" />
                      <span>{language === "ta" ? "ஜோதிட நெறிமுறை அறிவிப்பு" : "Ethical Astrological Disclaimer"}</span>
                    </div>
                    <p className="leading-relaxed">
                      {language === "ta" ? comp.disclaimers[1] || comp.disclaimers[0] : comp.disclaimers[0]}
                    </p>
                  </div>
                </div>
              );
            })()}

            {/* 2. TABBED DEEP DIVE NAVIGATION */}
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="border-b border-slate-200 bg-slate-50/50 px-4 pt-3 flex flex-wrap gap-2">
                {[
                  {
                    id: "charts",
                    labelEn: "Dual Kundli Charts (D1/D9)",
                    labelTa: "இருவர் ஜாதகக் கட்டங்கள் (D1/D9)",
                  },
                  {
                    id: "porutham",
                    labelEn: `Tamil 10 Porutham (${response.tamil_porutham?.total_score || 0}/10)`,
                    labelTa: `10 பொருத்தங்கள் (${response.tamil_porutham?.total_score || 0}/10)`,
                  },
                  {
                    id: "ashtakoota",
                    labelEn: `Ashtakoota (${response.ashtakoota?.total_points || 0}/36)`,
                    labelTa: `அஷ்டகூடம் (${response.ashtakoota?.total_points || 0}/36)`,
                  },
                  {
                    id: "doshas",
                    labelEn: "Kuja & Papasamya",
                    labelTa: "செவ்வாய் & பாபசாம்யம்",
                  },
                  {
                    id: "vedic",
                    labelEn: "Vedic Houses & D9",
                    labelTa: "களத்திர பாவம் & D9",
                  },
                  {
                    id: "synastry",
                    labelEn: "Synastry Overlays",
                    labelTa: "இருவழி இணைவு",
                  },
                  {
                    id: "kp",
                    labelEn: "KP 7th CSL & Timing",
                    labelTa: "கே.பி & தசா-புக்தி",
                  },
                  {
                    id: "conflicts",
                    labelEn: `Divergences (${response.composite_assessment.conflicting_findings.length})`,
                    labelTa: `முரண்பாடுகள் (${response.composite_assessment.conflicting_findings.length})`,
                  },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`px-4 py-2.5 text-xs sm:text-sm font-bold rounded-t-xl transition border-t border-l border-r cursor-pointer ${
                      activeTab === tab.id
                        ? "bg-white text-[#153F6B] border-slate-200 -mb-px shadow-2xs"
                        : "text-slate-600 border-transparent hover:text-slate-900 hover:bg-slate-100/60"
                    }`}
                  >
                    {language === "ta" ? tab.labelTa : tab.labelEn}
                  </button>
                ))}
              </div>

              <div className="p-6">
                {/* TAB 0: DUAL KUNDLI CHARTS (D1 / D9) */}
                {activeTab === "charts" && (
                  <div className="space-y-6">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 p-4 rounded-xl bg-slate-50 border border-slate-200">
                      <div>
                        <h4 className="font-bold text-sm text-[#153F6B] flex items-center gap-2">
                          <Eye className="w-4 h-4 text-[#B4872B]" />
                          {language === "ta"
                            ? "இருவர் ஜாதக கட்டங்கள் (D1 ராசி & D9 நவாம்சம்)"
                            : "Dual Synastry Kundli Charts (D1 Rasi & D9 Navamsa)"}
                        </h4>
                        <p className="text-xs text-slate-600 mt-0.5">
                          {language === "ta"
                            ? "மணமகன் மற்றும் மணமகள் ஜாதக கட்டங்களின் நேரடி ஒப்பீடு."
                            : "Side-by-side planetary comparison of Groom and Bride birth and navamsa charts."}
                        </p>
                      </div>

                      <div className="flex flex-wrap items-center gap-3 text-xs">
                        {/* Division Selector */}
                        <div className="inline-flex p-1 rounded-xl bg-white border border-slate-200">
                          <button
                            type="button"
                            onClick={() => setPartnerChartDivision("d1")}
                            className={`px-3 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                              partnerChartDivision === "d1"
                                ? "bg-[#153F6B] text-white shadow-2xs"
                                : "text-slate-600 hover:text-slate-900"
                            }`}
                          >
                            D1 Rasi
                          </button>
                          <button
                            type="button"
                            onClick={() => setPartnerChartDivision("d9")}
                            className={`px-3 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                              partnerChartDivision === "d9"
                                ? "bg-[#153F6B] text-white shadow-2xs"
                                : "text-slate-600 hover:text-slate-900"
                            }`}
                          >
                            D9 Navamsa
                          </button>
                        </div>

                        {/* Style Selector */}
                        <div className="inline-flex p-1 rounded-xl bg-white border border-slate-200">
                          <button
                            type="button"
                            onClick={() => setPartnerChartStyle("south")}
                            className={`px-3 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                              partnerChartStyle === "south"
                                ? "bg-[#B4872B] text-white shadow-2xs"
                                : "text-slate-600 hover:text-slate-900"
                            }`}
                          >
                            South Indian
                          </button>
                          <button
                            type="button"
                            onClick={() => setPartnerChartStyle("north")}
                            className={`px-3 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                              partnerChartStyle === "north"
                                ? "bg-[#B4872B] text-white shadow-2xs"
                                : "text-slate-600 hover:text-slate-900"
                            }`}
                          >
                            North Indian
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Dual Charts Grid */}
                    {(() => {
                      const groomChartPayload =
                        (partnerChartDivision === "d1"
                          ? response.groom_chart
                          : response.groom_d9_chart) || {
                          ascendant: {
                            sign_index:
                              partnerChartDivision === "d1"
                                ? SIGN_NAME_TO_IDX[response.groom_profile.ascendant_sign] || 1
                                : SIGN_NAME_TO_IDX[response.groom_profile.ascendant_navamsa_sign] || 1,
                            sign_name:
                              partnerChartDivision === "d1"
                                ? response.groom_profile.ascendant_sign
                                : response.groom_profile.ascendant_navamsa_sign,
                            degree_in_sign: response.groom_profile.ascendant_degree % 30.0,
                          },
                          planets: [
                            {
                              name: "Moon",
                              sign_index:
                                partnerChartDivision === "d1"
                                  ? SIGN_NAME_TO_IDX[response.groom_profile.moon_sign] || 1
                                  : SIGN_NAME_TO_IDX[response.groom_profile.moon_navamsa_sign] || 1,
                              degree_in_sign: response.groom_profile.moon_degree % 30.0,
                            },
                            {
                              name: "Venus",
                              sign_index: SIGN_NAME_TO_IDX[response.groom_profile.venus_sign] || 1,
                              degree_in_sign: 0.0,
                            },
                            {
                              name: "Mars",
                              sign_index: SIGN_NAME_TO_IDX[response.groom_profile.mars_sign] || 1,
                              degree_in_sign: 0.0,
                            },
                            {
                              name: "Jupiter",
                              sign_index: SIGN_NAME_TO_IDX[response.groom_profile.jupiter_sign] || 1,
                              degree_in_sign: 0.0,
                            },
                          ],
                        };

                      const brideChartPayload =
                        (partnerChartDivision === "d1"
                          ? response.bride_chart
                          : response.bride_d9_chart) || {
                          ascendant: {
                            sign_index:
                              partnerChartDivision === "d1"
                                ? SIGN_NAME_TO_IDX[response.bride_profile.ascendant_sign] || 1
                                : SIGN_NAME_TO_IDX[response.bride_profile.ascendant_navamsa_sign] || 1,
                            sign_name:
                              partnerChartDivision === "d1"
                                ? response.bride_profile.ascendant_sign
                                : response.bride_profile.ascendant_navamsa_sign,
                            degree_in_sign: response.bride_profile.ascendant_degree % 30.0,
                          },
                          planets: [
                            {
                              name: "Moon",
                              sign_index:
                                partnerChartDivision === "d1"
                                  ? SIGN_NAME_TO_IDX[response.bride_profile.moon_sign] || 1
                                  : SIGN_NAME_TO_IDX[response.bride_profile.moon_navamsa_sign] || 1,
                              degree_in_sign: response.bride_profile.moon_degree % 30.0,
                            },
                            {
                              name: "Venus",
                              sign_index: SIGN_NAME_TO_IDX[response.bride_profile.venus_sign] || 1,
                              degree_in_sign: 0.0,
                            },
                            {
                              name: "Mars",
                              sign_index: SIGN_NAME_TO_IDX[response.bride_profile.mars_sign] || 1,
                              degree_in_sign: 0.0,
                            },
                            {
                              name: "Jupiter",
                              sign_index: SIGN_NAME_TO_IDX[response.bride_profile.jupiter_sign] || 1,
                              degree_in_sign: 0.0,
                            },
                          ],
                        };

                      return (
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
                          {/* Groom Chart */}
                          <div className="space-y-3">
                            <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                              <div className="flex items-center gap-2">
                                <User className="w-4 h-4 text-[#153F6B]" />
                                <h5 className="font-bold text-sm text-[#153F6B]">
                                  {response.groom_profile.name} ({partnerChartDivision === "d1" ? "D1 Rasi" : "D9 Navamsa"})
                                </h5>
                              </div>
                              <span className="text-xs text-slate-500 font-mono">
                                {partnerChartDivision === "d1"
                                  ? `Lagna: ${response.groom_profile.ascendant_sign}`
                                  : `Navamsa: ${response.groom_profile.ascendant_navamsa_sign}`}
                              </span>
                            </div>

                            <div className="p-4 rounded-2xl bg-[#FAF7F0] border border-[#E8DEC8]">
                              {partnerChartStyle === "south" ? (
                                <SouthIndianChart horoscope={groomChartPayload as unknown as HoroscopeResponse} />
                              ) : (
                                <NorthIndianChart horoscope={groomChartPayload as unknown as HoroscopeResponse} />
                              )}
                            </div>

                            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-1 text-slate-700">
                              <div>
                                <span className="font-semibold text-slate-500">Moon Nakshatra:</span>{" "}
                                {response.groom_profile.moon_nakshatra} (Pada {response.groom_profile.moon_pada})
                              </div>
                              <div>
                                <span className="font-semibold text-slate-500">Moon Sign:</span>{" "}
                                {response.groom_profile.moon_sign} ({response.groom_profile.moon_sign_tamil})
                              </div>
                              <div>
                                <span className="font-semibold text-slate-500">Venus (Kalatra Karaka):</span>{" "}
                                {response.groom_profile.venus_sign} • Mars: {response.groom_profile.mars_sign}
                              </div>
                            </div>
                          </div>

                          {/* Bride Chart */}
                          <div className="space-y-3">
                            <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                              <div className="flex items-center gap-2">
                                <User className="w-4 h-4 text-[#B4872B]" />
                                <h5 className="font-bold text-sm text-[#B4872B]">
                                  {response.bride_profile.name} ({partnerChartDivision === "d1" ? "D1 Rasi" : "D9 Navamsa"})
                                </h5>
                              </div>
                              <span className="text-xs text-slate-500 font-mono">
                                {partnerChartDivision === "d1"
                                  ? `Lagna: ${response.bride_profile.ascendant_sign}`
                                  : `Navamsa: ${response.bride_profile.ascendant_navamsa_sign}`}
                              </span>
                            </div>

                            <div className="p-4 rounded-2xl bg-[#FAF7F0] border border-[#E8DEC8]">
                              {partnerChartStyle === "south" ? (
                                <SouthIndianChart horoscope={brideChartPayload as unknown as HoroscopeResponse} />
                              ) : (
                                <NorthIndianChart horoscope={brideChartPayload as unknown as HoroscopeResponse} />
                              )}
                            </div>

                            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-1 text-slate-700">
                              <div>
                                <span className="font-semibold text-slate-500">Moon Nakshatra:</span>{" "}
                                {response.bride_profile.moon_nakshatra} (Pada {response.bride_profile.moon_pada})
                              </div>
                              <div>
                                <span className="font-semibold text-slate-500">Moon Sign:</span>{" "}
                                {response.bride_profile.moon_sign} ({response.bride_profile.moon_sign_tamil})
                              </div>
                              <div>
                                <span className="font-semibold text-slate-500">Jupiter (Pati Karaka):</span>{" "}
                                {response.bride_profile.jupiter_sign} • Mars: {response.bride_profile.mars_sign}
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })()}
                  </div>
                )}
                {/* TAB 1: TAMIL 10 PORUTHAMS */}
                {activeTab === "porutham" && response.tamil_porutham && (
                  <div className="space-y-6">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-slate-50 border border-slate-200">
                      <div>
                        <span className="text-xs text-slate-500 font-semibold uppercase">
                          Traditional South Indian Score
                        </span>
                        <div className="text-2xl font-black text-[#153F6B] mt-0.5">
                          {response.tamil_porutham.total_score} / 10.0
                          <span className="text-sm font-semibold ml-2 text-slate-600">
                            ({response.tamil_porutham.aggregate_verdict})
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span
                          className={`px-3 py-1.5 rounded-lg text-xs font-bold border ${
                            response.tamil_porutham.rajju_status === "PASS"
                              ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                              : "bg-rose-50 text-rose-800 border-rose-300 animate-pulse"
                          }`}
                        >
                          Rajju: {response.tamil_porutham.rajju_status}
                        </span>
                        <span
                          className={`px-3 py-1.5 rounded-lg text-xs font-bold border ${
                            response.tamil_porutham.vedha_status === "PASS"
                              ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                              : "bg-rose-50 text-rose-800 border-rose-300"
                          }`}
                        >
                          Vedha: {response.tamil_porutham.vedha_status}
                        </span>
                      </div>
                    </div>

                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-slate-100 text-slate-600 uppercase font-semibold">
                          <tr>
                            <th className="p-3">Porutham</th>
                            <th className="p-3">Score</th>
                            <th className="p-3">Grade</th>
                            <th className="p-3">Evaluation & Meaning</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                          {Object.values(response.tamil_porutham.poruthams).map((p) => (
                            <tr key={p.rule_id} className="hover:bg-slate-50/60">
                              <td className="p-3 font-bold text-slate-900">
                                {language === "ta" ? p.name_ta : p.name_en}
                                <span className="block text-[10px] text-slate-400 font-normal">
                                  {p.classical_reference}
                                </span>
                              </td>
                              <td className="p-3 font-semibold text-[#153F6B]">
                                {p.score} / {p.max_score}
                              </td>
                              <td className="p-3">
                                <span
                                  className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                    p.is_favorable
                                      ? "bg-emerald-100 text-emerald-800"
                                      : "bg-slate-100 text-slate-600"
                                  }`}
                                >
                                  {p.grade}
                                </span>
                              </td>
                              <td className="p-3 text-slate-700">
                                {language === "ta" ? p.description_tamil : p.description}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* TAB 2: NORTH INDIAN ASHTAKOOTA */}
                {activeTab === "ashtakoota" && response.ashtakoota && (
                  <div className="space-y-6">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-slate-50 border border-slate-200">
                      <div>
                        <span className="text-xs text-slate-500 font-semibold uppercase">
                          North Indian 36-Point Ashtakoota
                        </span>
                        <div className="text-2xl font-black text-[#153F6B] mt-0.5">
                          {response.ashtakoota.total_points} / 36.0
                          <span className="text-sm font-semibold ml-2 text-slate-600">
                            (Min: {response.ashtakoota.minimum_threshold} pts)
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span
                          className={`px-3 py-1.5 rounded-lg text-xs font-bold border ${
                            response.ashtakoota.is_threshold_met
                              ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                              : "bg-rose-50 text-rose-800 border-rose-300"
                          }`}
                        >
                          {response.ashtakoota.is_threshold_met ? "Threshold Met" : "Below Minimum"}
                        </span>
                        <span
                          className={`px-3 py-1.5 rounded-lg text-xs font-bold border ${
                            !response.ashtakoota.nadi_dosha_present || response.ashtakoota.nadi_dosha_cancelled
                              ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                              : "bg-rose-50 text-rose-800 border-rose-300"
                          }`}
                        >
                          Nadi: {response.ashtakoota.nadi_dosha_present ? (response.ashtakoota.nadi_dosha_cancelled ? "Cancelled" : "Active Dosha") : "Clear"}
                        </span>
                      </div>
                    </div>

                    {/* Score Bar Meter */}
                    <div className="p-4 rounded-xl bg-white border border-slate-200 space-y-2">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-bold text-[#102A4C]">
                          Ashtakoota Score Meter: {response.ashtakoota.total_points} / 36.0 (
                          {((response.ashtakoota.total_points / 36.0) * 100).toFixed(0)}%)
                        </span>
                        <span
                          className={`font-bold ${
                            response.ashtakoota.total_points >= 28
                              ? "text-emerald-700"
                              : response.ashtakoota.total_points >= 18
                              ? "text-amber-700"
                              : "text-rose-700"
                          }`}
                        >
                          {response.ashtakoota.total_points >= 28
                            ? "Uthama (உத்தமம்) - Excellent"
                            : response.ashtakoota.total_points >= 18
                            ? "Madhyama (மத்திமம்) - Acceptable"
                            : "Adhama (அதமம்) - Inauspicious"}
                        </span>
                      </div>
                      <div className="w-full h-3 rounded-full bg-slate-100 overflow-hidden relative border border-slate-200">
                        {/* 18-point threshold line at 50% */}
                        <div
                          className="absolute top-0 bottom-0 w-0.5 bg-slate-400 z-10"
                          style={{ left: "50%" }}
                          title="Minimum Pass Threshold (18 pts)"
                        />
                        {/* 28-point threshold line at 77.7% */}
                        <div
                          className="absolute top-0 bottom-0 w-0.5 bg-emerald-400 z-10"
                          style={{ left: "77.7%" }}
                          title="Uthama Threshold (28 pts)"
                        />
                        <div
                          className={`h-full transition-all duration-500 ${
                            response.ashtakoota.total_points >= 28
                              ? "bg-gradient-to-r from-emerald-500 to-emerald-600"
                              : response.ashtakoota.total_points >= 18
                              ? "bg-gradient-to-r from-amber-400 to-[#B4872B]"
                              : "bg-gradient-to-r from-rose-400 to-rose-600"
                          }`}
                          style={{
                            width: `${Math.min(100, Math.max(0, (response.ashtakoota.total_points / 36.0) * 100))}%`,
                          }}
                        />
                      </div>
                      <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                        <span>0 pts</span>
                        <span>18 pts (Min Passing)</span>
                        <span>28 pts (Uthama)</span>
                        <span>36 pts</span>
                      </div>
                    </div>

                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-slate-100 text-slate-600 uppercase font-semibold">
                          <tr>
                            <th className="p-3">Koota</th>
                            <th className="p-3">Points</th>
                            <th className="p-3">Status</th>
                            <th className="p-3">Calculation & Rule</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                          {Object.values(response.ashtakoota.kootas).map((k) => (
                            <tr key={k.koota_id} className="hover:bg-slate-50/60">
                              <td className="p-3 font-bold text-slate-900">
                                <div>{k.name_en}</div>
                                <div className="text-[11px] text-[#B4872B] font-semibold">
                                  {ASHTAKOOTA_META_TA[k.koota_id]?.nameTa || ""}
                                </div>
                                <span className="block text-[10px] text-slate-400 font-normal mt-0.5">
                                  {k.classical_reference}
                                </span>
                              </td>
                              <td className="p-3 font-semibold text-[#153F6B]">
                                {k.earned_points} / {k.max_points}
                              </td>
                              <td className="p-3">
                                <span
                                  className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                    k.earned_points > 0
                                      ? "bg-emerald-100 text-emerald-800"
                                      : "bg-rose-100 text-rose-800"
                                  }`}
                                >
                                  {k.status}
                                </span>
                              </td>
                              <td className="p-3 text-slate-700">
                                <div>{k.description}</div>
                                {language === "ta" && ASHTAKOOTA_META_TA[k.koota_id] && (
                                  <div className="text-[11px] text-[#52667E] mt-0.5">
                                    {ASHTAKOOTA_META_TA[k.koota_id].significanceTa}
                                  </div>
                                )}
                                {k.cancellation_reason && (
                                  <div className="text-[11px] text-amber-700 mt-1 font-medium bg-amber-50 p-1.5 rounded border border-amber-200">
                                    Mitigation: {k.cancellation_reason}
                                  </div>
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* TAB 3: KUJA SAMADOSHAM & PAPASAMYA */}
                {activeTab === "doshas" && response.dosha_analysis && (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* Kuja Samadosham */}
                      <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3">
                        <div className="flex items-center justify-between">
                          <h4 className="font-bold text-sm text-[#153F6B] flex items-center gap-2">
                            <Scale className="w-4 h-4 text-[#B4872B]" />
                            Kuja / Manglik Samadosham
                          </h4>
                          <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-slate-100 text-slate-700">
                            {response.dosha_analysis.samadosham_status || "BALANCED"}
                          </span>
                        </div>
                        <p className="text-xs text-slate-600 leading-relaxed">
                          {language === "ta"
                            ? response.dosha_analysis.samadosham_explanation_ta || "இருவர் ஜாதகங்களிலும் செவ்வாய் தோஷ சமநிலை சரிபார்க்கப்பட்டது."
                            : response.dosha_analysis.samadosham_explanation_en || "Mutual Kuja Dosha counterpoise evaluated across both horoscopes."}
                        </p>
                      </div>

                      {/* Papasamya Malefic Balance */}
                      <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3">
                        <div className="flex items-center justify-between">
                          <h4 className="font-bold text-sm text-[#153F6B] flex items-center gap-2">
                            <ShieldAlert className="w-4 h-4 text-[#B4872B]" />
                            South Indian Papasamya Balance
                          </h4>
                          <span
                            className={`px-2.5 py-1 rounded-md text-xs font-bold ${
                              response.dosha_analysis.papasamya_verdict === "FAVORABLE"
                                ? "bg-emerald-100 text-emerald-800"
                                : "bg-amber-100 text-amber-800"
                            }`}
                          >
                            {response.dosha_analysis.papasamya_verdict}
                          </span>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-xs py-2 bg-slate-50 p-3 rounded-xl">
                          <div>
                            <span className="text-slate-400 block">Groom Papam:</span>
                            <span className="font-bold text-slate-800 text-sm">
                              {response.dosha_analysis.groom_papasamya?.total_papam} pts
                            </span>
                          </div>
                          <div>
                            <span className="text-slate-400 block">Bride Papam:</span>
                            <span className="font-bold text-slate-800 text-sm">
                              {response.dosha_analysis.bride_papasamya?.total_papam} pts
                            </span>
                          </div>
                        </div>
                        <p className="text-xs text-slate-600">
                          {language === "ta"
                            ? response.dosha_analysis.papasamya_explanation_ta
                            : response.dosha_analysis.papasamya_explanation_en}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* TAB 4: INDIVIDUAL VEDIC HOUSES & D9 */}
                {activeTab === "vedic" && (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
                        <h4 className="font-bold text-sm text-[#153F6B] flex items-center gap-2">
                          <User className="w-4 h-4" />
                          Groom Vedic Profile: {response.groom_profile.name}
                        </h4>
                        <div className="text-xs space-y-1.5 text-slate-700">
                          <p>
                            <span className="font-semibold">Lagna:</span> {response.groom_profile.ascendant_sign} (
                            {response.groom_profile.ascendant_sign_tamil}) @ {response.groom_profile.ascendant_degree}°
                          </p>
                          <p>
                            <span className="font-semibold">Moon:</span> {response.groom_profile.moon_sign} -{" "}
                            {response.groom_profile.moon_nakshatra} (Pada {response.groom_profile.moon_pada})
                          </p>
                          <p>
                            <span className="font-semibold">Navamsa (D9) Lagna:</span>{" "}
                            {response.groom_profile.ascendant_navamsa_sign}
                          </p>
                          <p>
                            <span className="font-semibold">Venus (Kalatra Karaka):</span>{" "}
                            {response.groom_profile.venus_sign}
                          </p>
                        </div>
                      </div>

                      <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
                        <h4 className="font-bold text-sm text-[#B4872B] flex items-center gap-2">
                          <User className="w-4 h-4" />
                          Bride Vedic Profile: {response.bride_profile.name}
                        </h4>
                        <div className="text-xs space-y-1.5 text-slate-700">
                          <p>
                            <span className="font-semibold">Lagna:</span> {response.bride_profile.ascendant_sign} (
                            {response.bride_profile.ascendant_sign_tamil}) @ {response.bride_profile.ascendant_degree}°
                          </p>
                          <p>
                            <span className="font-semibold">Moon:</span> {response.bride_profile.moon_sign} -{" "}
                            {response.bride_profile.moon_nakshatra} (Pada {response.bride_profile.moon_pada})
                          </p>
                          <p>
                            <span className="font-semibold">Navamsa (D9) Lagna:</span>{" "}
                            {response.bride_profile.ascendant_navamsa_sign}
                          </p>
                          <p>
                            <span className="font-semibold">Jupiter (Pati Karaka):</span>{" "}
                            {response.bride_profile.jupiter_sign}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* TAB 5: SYNASTRY OVERLAYS */}
                {activeTab === "synastry" && response.synastry && (
                  <div className="space-y-4 text-xs">
                    <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                      <h4 className="font-bold text-sm text-[#153F6B]">
                        Cross-Chart Planetary Resonances
                      </h4>
                      <p className="text-slate-600">
                        {language === "ta"
                          ? response.synastry.explanation_ta || "சந்திர அச்சு மற்றும் லக்ன அச்சு ஆய்வு செய்யப்பட்டது."
                          : response.synastry.explanation_en || "Moon and Lagna relationship evaluated across both horoscopes."}
                      </p>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div className="p-4 rounded-xl border border-slate-200 bg-white space-y-1.5">
                        <span className="font-semibold text-slate-500 uppercase text-[10px]">Moon-to-Moon Axis</span>
                        <div className="font-bold text-slate-900 text-sm">
                          {response.synastry.moon_to_moon?.sign_relationship || "Samasaptaka"}
                        </div>
                        <p className="text-slate-600 text-[11px]">
                          {response.synastry.moon_to_moon?.explanation_en}
                        </p>
                      </div>

                      <div className="p-4 rounded-xl border border-slate-200 bg-white space-y-1.5">
                        <span className="font-semibold text-slate-500 uppercase text-[10px]">Lagna-to-Lagna Axis</span>
                        <div className="font-bold text-slate-900 text-sm">
                          {response.synastry.lagna_to_lagna?.lagna_relationship || "Trine"}
                        </div>
                        <p className="text-slate-600 text-[11px]">
                          {response.synastry.lagna_to_lagna?.explanation_en}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* TAB 6: KP 7TH CSL & TIMING */}
                {activeTab === "kp" && (
                  <div className="space-y-4 text-xs">
                    {response.kp_marriage ? (
                      <div className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                            <span className="font-bold text-slate-700">Groom 7th Cuspal Sub-Lord</span>
                            <p className="text-slate-600 text-[11px]">
                              CSL Planet: {response.kp_marriage.groom_analysis?.csl_7th?.sub_lord_planet}
                            </p>
                            <p className="text-slate-600 text-[11px]">
                              Verdict: {response.kp_marriage.groom_analysis?.csl_7th?.verdict}
                            </p>
                          </div>

                          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                            <span className="font-bold text-slate-700">Bride 7th Cuspal Sub-Lord</span>
                            <p className="text-slate-600 text-[11px]">
                              CSL Planet: {response.kp_marriage.bride_analysis?.csl_7th?.sub_lord_planet}
                            </p>
                            <p className="text-slate-600 text-[11px]">
                              Verdict: {response.kp_marriage.bride_analysis?.csl_7th?.verdict}
                            </p>
                          </div>
                        </div>

                        <div className="p-4 rounded-xl bg-[#FAF2DE]/40 border border-[#B4872B]/30 space-y-1">
                          <span className="font-bold text-[#B4872B]">Ruling Planets Agreement</span>
                          <p className="text-slate-700">
                            Agreement Level: {response.kp_marriage.ruling_planets_agreement_level}
                          </p>
                        </div>
                      </div>
                    ) : (
                      <div className="p-8 text-center bg-slate-50 rounded-xl text-slate-500">
                        <Info className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                        <p className="font-semibold">KP Analysis Excluded or Indeterminate</p>
                        <p className="text-[11px] text-slate-400 mt-1">
                          Enable KP evaluation in Advanced Calculation Settings to view 7th CSL significations.
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {/* TAB 7: CROSS-TRADITION DIVERGENCES */}
                {activeTab === "conflicts" && (
                  <div className="space-y-4">
                    {response.composite_assessment.conflicting_findings.length > 0 ? (
                      response.composite_assessment.conflicting_findings.map((cf, idx) => (
                        <div key={idx} className="p-4 rounded-xl bg-amber-50/60 border border-amber-200 space-y-2 text-xs">
                          <div className="flex items-center justify-between">
                            <h4 className="font-bold text-amber-900 text-sm flex items-center gap-2">
                              <AlertTriangle className="w-4 h-4 text-amber-600" />
                              {language === "ta" ? cf.title_ta : cf.title_en}
                            </h4>
                            <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-amber-100 text-amber-800">
                              {cf.conflict_type.replace(/_/g, " ")}
                            </span>
                          </div>

                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-slate-700 py-1">
                            <div className="bg-white/80 p-2.5 rounded-lg border border-amber-100">
                              <span className="font-semibold block text-[10px] text-slate-400">Finding A:</span>
                              {cf.finding_a}
                            </div>
                            <div className="bg-white/80 p-2.5 rounded-lg border border-amber-100">
                              <span className="font-semibold block text-[10px] text-slate-400">Finding B:</span>
                              {cf.finding_b}
                            </div>
                          </div>

                          <div className="text-[11px] text-amber-900 bg-white/50 p-2 rounded-lg">
                            <span className="font-bold">Resolution Principle:</span> {cf.resolution_principle}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="p-8 text-center bg-slate-50 rounded-xl text-slate-500 text-xs">
                        <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
                        <p className="font-semibold">Complete Harmonious Alignment</p>
                        <p className="text-[11px] text-slate-400 mt-1">
                          Zero cross-tradition divergences detected across all evaluated astrological layers.
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </>
    )}

      {/* Save Report Modal Dialog */}
      {isSaveModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fadeIn">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-[#FAF2DE] border border-[#B4872B]/30 flex items-center justify-center">
                  <Save className="w-4 h-4 text-[#B4872B]" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-[#153F6B]">
                    {language === "ta" ? "பொருத்த அறிக்கையைச் சேமிக்க" : "Save Compatibility Report"}
                  </h3>
                  <p className="text-xs text-slate-500">
                    {language === "ta"
                      ? "கணக்கீட்டு முடிவுகளை உங்கள் கணக்கில் சேமிக்கவும்"
                      : "Save immutable calculation snapshot to your account"}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setIsSaveModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {!isAuthenticated ? (
              <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs space-y-2">
                <p className="font-bold flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  {language === "ta" ? "உள்நுழைவு தேவை" : "Authentication Required"}
                </p>
                <p>
                  {language === "ta"
                    ? "பொருத்த அறிக்கைகளைச் சேமிக்க நீங்கள் உள்நுழைய வேண்டும்."
                    : "You must be signed in to save and access your compatibility reports."}
                </p>
                <div className="pt-2">
                  <Link
                    href="/login?redirect=/tools/marriage-compatibility"
                    className="inline-flex items-center px-3.5 py-1.5 rounded-lg bg-[#153F6B] text-white font-semibold text-xs hover:bg-[#1E5692]"
                  >
                    {language === "ta" ? "உள்நுழைக" : "Sign In"}
                  </Link>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">
                    {language === "ta" ? "அறிக்கைத் தலைப்பு" : "Report Title"}
                  </label>
                  <input
                    type="text"
                    value={saveTitle}
                    onChange={(e) => setSaveTitle(e.target.value)}
                    placeholder="e.g. Groom & Bride Compatibility"
                    className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-[#B4872B] focus:border-[#B4872B]"
                  />
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-1 text-slate-600">
                  <div className="flex justify-between">
                    <span className="font-medium text-slate-500">{language === "ta" ? "மணமகன்:" : "Groom:"}</span>
                    <span className="font-bold text-slate-800">{groomName || "Groom"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium text-slate-500">{language === "ta" ? "மணமகள்:" : "Bride:"}</span>
                    <span className="font-bold text-slate-800">{brideName || "Bride"}</span>
                  </div>
                </div>

                {saveError && (
                  <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
                    <span>{saveError}</span>
                  </div>
                )}

                <div className="flex items-center justify-end gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setIsSaveModalOpen(false)}
                    className="px-4 py-2 rounded-xl border border-slate-300 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                  >
                    {language === "ta" ? "ரத்து செய்" : "Cancel"}
                  </button>
                  <button
                    type="button"
                    onClick={handleConfirmSave}
                    disabled={savingReport}
                    className="px-5 py-2 rounded-xl bg-[#153F6B] hover:bg-[#1E5692] text-white text-xs font-bold shadow-md shadow-[#153F6B]/20 flex items-center gap-1.5 disabled:opacity-50"
                  >
                    {savingReport ? (
                      <>
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        <span>{language === "ta" ? "சேமிக்கப்படுகிறது..." : "Saving..."}</span>
                      </>
                    ) : (
                      <>
                        <Save className="w-3.5 h-3.5" />
                        <span>{language === "ta" ? "சேமிக்கவும்" : "Confirm Save"}</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </main>
  </div>
);
}

export default function MarriageCompatibilityPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-[#F8FAFC]">
          <div className="w-8 h-8 border-4 border-[#153F6B] border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <MarriageCompatibilityContent />
    </Suspense>
  );
}
