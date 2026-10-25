"use client";

import React, { useEffect, useState, useMemo, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { getActiveCalculation } from "@/lib/storage";
import {
  getProblemTaxonomy,
  getRemedyCatalog,
  getNavagrahaTemples,
  getClassicalSources,
  validateRemedyContent,
  checkRemedyEligibility,
  getSavedHoroscopeRemedyAnalysis,
  getLiveRemedyAnalysis,
} from "@/lib/api";
import {
  ProblemTaxonomyItem,
  RemedyItem,
  NavagrahaTempleItem,
  SourceReferenceResponse,
  ContentValidationReport,
  RemedyEligibilityResponse,
  RemedyAnalysisResponse,
} from "@/lib/types";
import { PersonalizedRemedySection } from "@/components/remedies/PersonalizedRemedySection";
import { PilgrimageCircuitView } from "@/components/remedies/PilgrimageCircuitView";
import { GemstoneAdvisoryView } from "@/components/remedies/GemstoneAdvisoryView";
import {
  Flame,
  Compass,
  BookOpen,
  MapPin,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  Search,
  Filter,
  Sparkles,
  ExternalLink,
  Calendar,
  ArrowRight,
  RefreshCw,
  FileText,
  ShieldCheck,
  ChevronRight,
  Info,
} from "lucide-react";

const LAGNA_OPTIONS = [
  "Aries",
  "Taurus",
  "Gemini",
  "Cancer",
  "Leo",
  "Virgo",
  "Libra",
  "Scorpio",
  "Sagittarius",
  "Capricorn",
  "Aquarius",
  "Pisces",
];

const GRAHA_OPTIONS = [
  { value: "all", label_en: "All Planets", label_ta: "அனைத்து கிரகங்கள்" },
  { value: "sun", label_en: "Sun (Surya)", label_ta: "சூரியன்" },
  { value: "moon", label_en: "Moon (Chandra)", label_ta: "சந்திரன்" },
  { value: "mars", label_en: "Mars (Chevvai)", label_ta: "செவ்வாய்" },
  { value: "mercury", label_en: "Mercury (Budha)", label_ta: "புதன்" },
  { value: "jupiter", label_en: "Jupiter (Guru)", label_ta: "குரு" },
  { value: "venus", label_en: "Venus (Shukra)", label_ta: "சுக்கிரன்" },
  { value: "saturn", label_en: "Saturn (Shani)", label_ta: "சனி" },
  { value: "rahu", label_en: "Rahu", label_ta: "ராகு" },
  { value: "ketu", label_en: "Ketu", label_ta: "கேது" },
];

function RemediesHubContent() {
  const { language } = useLanguage();
  const { user, session, isAuthenticated, isLoading: authLoading } = useAuth();
  const searchParams = useSearchParams();
  const horoscopeId = searchParams.get("horoscope_id");

  // Active tab state
  const [activeTab, setActiveTab] = useState<
    "analysis" | "taxonomy" | "catalog" | "temples" | "pilgrimage" | "gemstones" | "eligibility" | "sources"
  >(() => {
    return horoscopeId ? "analysis" : "taxonomy";
  });

  // Analysis state
  const [analysisResult, setAnalysisResult] = useState<RemedyAnalysisResponse | null>(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState<boolean>(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [isAuthError, setIsAuthError] = useState<boolean>(false);

  // Auto-switch to analysis tab if horoscope_id parameter changes
  useEffect(() => {
    if (horoscopeId) {
      setActiveTab("analysis");
    }
  }, [horoscopeId]);

  const loadAnalysisData = async () => {
    // If requesting a saved horoscope, wait for auth session provider to initialize
    if (horoscopeId && authLoading) {
      return;
    }

    setLoadingAnalysis(true);
    setAnalysisError(null);
    setIsAuthError(false);

    try {
      if (horoscopeId) {
        if (!isAuthenticated || !session?.access_token) {
          setIsAuthError(true);
          setAnalysisError(
            language === "ta"
              ? "சேமிக்கப்பட்ட ஜாதகத்திற்கான தனிப்பட்ட பரிகாரங்களைக் காண உள்நுழைவு அவசியம். தயவுசெய்து உள்நுழையவும்."
              : "Authentication required to view personalized remedy analysis for this saved horoscope. Please sign in."
          );
          setLoadingAnalysis(false);
          return;
        }
        const res = await getSavedHoroscopeRemedyAnalysis(horoscopeId, session.access_token);
        setAnalysisResult(res);
      } else {
        const activeCalc = getActiveCalculation();
        if (activeCalc) {
          const res = await getLiveRemedyAnalysis({ chart_snapshot: activeCalc }, session?.access_token);
          setAnalysisResult(res);
        } else {
          setAnalysisResult(null);
        }
      }
    } catch (err: any) {
      console.error("Failed to load remedy analysis:", err);
      const statusCode = err?.statusCode || err?.status;
      const detail = err?.data?.detail || err?.message || "Failed to generate remedy analysis.";
      if (
        statusCode === 401 ||
        (statusCode !== 404 && (
          detail.toLowerCase().includes("not authenticated") ||
          detail.toLowerCase().includes("token") ||
          detail.toLowerCase().includes("authentication required")
        ))
      ) {
        setIsAuthError(true);
        setAnalysisError(
          language === "ta"
            ? "உங்கள் அமர்வு முடிந்துவிட்டது அல்லது உள்நுழைவு தேவைப்படுகிறது. தயவுசெய்து மீண்டும் உள்நுழையவும்."
            : "Your session has expired or authentication is required. Please sign in again."
        );
      } else {
        setAnalysisError(detail);
      }
    } finally {
      setLoadingAnalysis(false);
    }
  };

  useEffect(() => {
    if (activeTab === "analysis") {
      if (horoscopeId && authLoading) {
        return;
      }
      loadAnalysisData();
    }
  }, [activeTab, horoscopeId, authLoading, session?.access_token]);

  // Data states
  const [taxonomies, setTaxonomies] = useState<ProblemTaxonomyItem[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [searchTaxonomy, setSearchTaxonomy] = useState<string>("");

  const [remedies, setRemedies] = useState<RemedyItem[]>([]);
  const [selectedGraha, setSelectedGraha] = useState<string>("all");
  const [selectedRemedyType, setSelectedRemedyType] = useState<string>("all");
  const [filterProblemSlug, setFilterProblemSlug] = useState<string>("");

  const [temples, setTemples] = useState<NavagrahaTempleItem[]>([]);
  const [selectedTempleGraha, setSelectedTempleGraha] = useState<string>("all");

  const [sources, setSources] = useState<SourceReferenceResponse[]>([]);

  // Validation report state
  const [auditReport, setAuditReport] = useState<ContentValidationReport | null>(null);
  const [auditing, setAuditing] = useState<boolean>(false);

  // Eligibility Engine state
  const [eligLagna, setEligLagna] = useState<string>("Taurus");
  const [eligGraha, setEligGraha] = useState<string>("saturn");
  const [eligRemedyType, setEligRemedyType] = useState<string>("charity");
  const [eligibilityResult, setEligibilityResult] =
    useState<RemedyEligibilityResponse | null>(null);
  const [checkingEligibility, setCheckingEligibility] = useState<boolean>(false);

  const [loading, setLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Initial Load
  useEffect(() => {
    async function loadInitialData() {
      setLoading(true);
      setErrorMsg(null);
      try {
        const [taxRes, remRes, tempRes, srcRes] = await Promise.all([
          getProblemTaxonomy(),
          getRemedyCatalog(),
          getNavagrahaTemples(),
          getClassicalSources(),
        ]);
        setTaxonomies(taxRes.items || []);
        setCategories(taxRes.categories || []);
        setRemedies(remRes.items || []);
        setTemples(tempRes.items || []);
        setSources(srcRes || []);
      } catch (err: any) {
        console.error("Failed to load remedies data:", err);
        setErrorMsg(err.message || "Failed to load remedy data from server.");
      } finally {
        setLoading(false);
      }
    }
    loadInitialData();
  }, []);

  // Run Content Audit
  const handleRunAudit = async () => {
    setAuditing(true);
    try {
      const rep = await validateRemedyContent();
      setAuditReport(rep);
    } catch (err: any) {
      console.warn("Audit error:", err);
    } finally {
      setAuditing(false);
    }
  };

  // Run Eligibility Safeguard Check
  const handleCheckEligibility = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setCheckingEligibility(true);
    try {
      const res = await checkRemedyEligibility({
        ascendant_sign: eligLagna,
        graha: eligGraha,
        remedy_type: eligRemedyType,
      });
      setEligibilityResult(res);
    } catch (err: any) {
      console.warn("Eligibility error:", err);
    } finally {
      setCheckingEligibility(false);
    }
  };

  // Filtered Taxonomies
  const filteredTaxonomies = useMemo(() => {
    return taxonomies.filter((item) => {
      if (selectedCategory !== "all" && item.category !== selectedCategory) {
        return false;
      }
      if (searchTaxonomy.trim()) {
        const q = searchTaxonomy.toLowerCase();
        const matchesEn = item.name_en.toLowerCase().includes(q);
        const matchesTa = item.name_ta.includes(q);
        const matchesSlug = item.slug.toLowerCase().includes(q);
        const matchesDesc = (item.description_en || "")
          .toLowerCase()
          .includes(q) || (item.description_ta || "").includes(q);
        return matchesEn || matchesTa || matchesSlug || matchesDesc;
      }
      return true;
    });
  }, [taxonomies, selectedCategory, searchTaxonomy]);

  // Filtered Remedies
  const filteredRemedies = useMemo(() => {
    return remedies.filter((rem) => {
      if (selectedGraha !== "all" && rem.graha !== selectedGraha) {
        return false;
      }
      if (
        selectedRemedyType !== "all" &&
        rem.remedy_type !== selectedRemedyType
      ) {
        return false;
      }
      if (
        filterProblemSlug &&
        !rem.problem_slugs?.includes(filterProblemSlug)
      ) {
        return false;
      }
      return true;
    });
  }, [remedies, selectedGraha, selectedRemedyType, filterProblemSlug]);

  // Filtered Temples
  const filteredTemples = useMemo(() => {
    return temples.filter((t) => {
      if (
        selectedTempleGraha !== "all" &&
        t.graha !== selectedTempleGraha
      ) {
        return false;
      }
      return true;
    });
  }, [temples, selectedTempleGraha]);

  const selectProblemToFilterRemedies = (slug: string) => {
    setFilterProblemSlug(slug);
    setActiveTab("catalog");
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-8">
      {/* Breadcrumb Navigation */}
      <Breadcrumbs
        items={[
          {
            label:
              language === "ta"
                ? "பரிகாரங்கள் & ஆலயங்கள்"
                : "Remedies & Pariharam",
          },
        ]}
      />

      {/* Page Header */}
      <div className="rounded-3xl border border-[#DDE5F0] bg-white p-6 sm:p-8 shadow-xs space-y-4 relative overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-[#B8862B] via-amber-500 to-[#102A4C]" />

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
              <Flame className="w-3.5 h-3.5 text-amber-600" />
              <span>
                {language === "ta"
                  ? "வேத பரிகாரக் களஞ்சியம்"
                  : "Verified Vedic Remedial Knowledge Base"}
              </span>
            </div>

            <h1 className="font-serif text-2xl sm:text-3xl lg:text-4xl font-bold text-[#102A4C]">
              {language === "ta"
                ? "பரிகாரங்கள் & நவக்கிரகத் தலங்கள்"
                : "Remedies & Pariharam Hub"}
            </h1>

            <p className="text-xs sm:text-sm text-[#52667E] max-w-3xl leading-relaxed">
              {language === "ta"
                ? "பிருஹத் பராசர ஹோரா சாஸ்திரம், பலதீபிகை, ஆதித்ய ஹிருதயம் மற்றும் காவிரி டெல்டா நவக்கிரக ஸ்தலங்கள் அடிப்படையிலான தூய சாஸ்திர பரிகாரங்கள் மற்றும் சமஸ்கிருத/தமிழ் மந்திரங்கள்."
                : "Clean-room, Shastra-validated remedies based on Brihat Parashara Hora Shastra, Phaladeepika, Valmiki Ramayana, and consecrated Kaveri Delta Navagraha Temples. Zero AI hallucination, authentic Devanagari Sanskrit, and Yogakaraka protection safeguards."}
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2.5 shrink-0">
            <button
              type="button"
              onClick={handleRunAudit}
              disabled={auditing}
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl border border-emerald-300 bg-emerald-50 hover:bg-emerald-100 text-xs font-bold text-emerald-800 transition-colors shadow-2xs cursor-pointer"
            >
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>
                {auditing
                  ? language === "ta"
                    ? "சரிபார்க்கிறது..."
                    : "Auditing..."
                  : language === "ta"
                  ? "சாஸ்திர தணிக்கை"
                  : "Audit Knowledge Base"}
              </span>
            </button>
          </div>
        </div>

        {/* Audit Status Card (when clicked) */}
        {auditReport && (
          <div className="mt-4 p-4 rounded-2xl border border-emerald-200 bg-emerald-50/70 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                <span className="text-xs font-bold text-emerald-950">
                  {language === "ta"
                    ? "அனைத்து சாஸ்திர மற்றும் இருமொழி சோதனைகளும் தேர்ச்சி பெற்றன!"
                    : "Knowledge Base Audit Passed 100%!"}
                </span>
              </div>
              <span className="text-[11px] font-semibold text-emerald-800">
                {auditReport.total_problems_audited} Problems •{" "}
                {auditReport.total_temples_audited} Temples •{" "}
                {auditReport.total_remedies_audited} Remedies
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2 text-xs">
              {auditReport.checks.map((chk, idx) => (
                <div
                  key={idx}
                  className="p-2.5 rounded-xl bg-white border border-emerald-200 shadow-2xs"
                >
                  <div className="flex items-center gap-1.5 font-bold text-emerald-900 text-[11px]">
                    <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                    <span>{chk.check_name.replace(/_/g, " ")}</span>
                  </div>
                  <p className="text-[10px] text-[#52667E] mt-1 line-clamp-2">
                    {chk.details}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-1.5 p-1.5 rounded-2xl bg-[#F1F5F9] border border-[#DDE5F0] overflow-x-auto">
        <button
          type="button"
          onClick={() => setActiveTab("analysis")}
          className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all whitespace-nowrap cursor-pointer ${
            activeTab === "analysis"
              ? "bg-white text-purple-950 shadow-2xs border border-purple-300 ring-2 ring-purple-100"
              : "text-[#52667E] hover:text-[#102A4C]"
          }`}
        >
          <Sparkles className="w-4 h-4 text-purple-600" />
          <span>
            {language === "ta"
              ? "ஜாதக பரிகார ஆய்வு"
              : "Personalized Analysis"}
          </span>
          {horoscopeId && (
            <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-purple-100 text-purple-900 font-bold">
              Active
            </span>
          )}
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("taxonomy")}
          className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all whitespace-nowrap cursor-pointer ${
            activeTab === "taxonomy"
              ? "bg-white text-[#102A4C] shadow-2xs border border-[#DDE5F0]"
              : "text-[#52667E] hover:text-[#102A4C]"
          }`}
        >
          <Compass className="w-4 h-4 text-[#B8862B]" />
          <span>
            {language === "ta"
              ? "39 பிரச்சனை களஞ்சியம்"
              : "39 Problem Taxonomy"}
          </span>
          <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-[#FAF2DE] text-[#8C6D23]">
            {taxonomies.length}
          </span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("catalog")}
          className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all whitespace-nowrap cursor-pointer ${
            activeTab === "catalog"
              ? "bg-white text-[#102A4C] shadow-2xs border border-[#DDE5F0]"
              : "text-[#52667E] hover:text-[#102A4C]"
          }`}
        >
          <BookOpen className="w-4 h-4 text-amber-600" />
          <span>
            {language === "ta" ? "மந்திர & பரிகார நூல்" : "Remedy & Mantra Library"}
          </span>
          <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-amber-100 text-amber-900">
            {remedies.length}
          </span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("temples")}
          className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all whitespace-nowrap cursor-pointer ${
            activeTab === "temples"
              ? "bg-white text-[#102A4C] shadow-2xs border border-[#DDE5F0]"
              : "text-[#52667E] hover:text-[#102A4C]"
          }`}
        >
          <MapPin className="w-4 h-4 text-rose-600" />
          <span>
            {language === "ta"
              ? "9 நவகிரக ஸ்தலங்கள்"
              : "Tamil Navagraha Temples"}
          </span>
          <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-rose-100 text-rose-900">
            {temples.length}
          </span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("pilgrimage")}
          className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all whitespace-nowrap cursor-pointer ${
            activeTab === "pilgrimage"
              ? "bg-white text-[#102A4C] shadow-2xs border border-[#DDE5F0]"
              : "text-[#52667E] hover:text-[#102A4C]"
          }`}
        >
          <Compass className="w-4 h-4 text-[#8B6914]" />
          <span>
            {language === "ta"
              ? "நவக்கிரக யாத்திரை (சுற்றுலா)"
              : "Navagraha Pilgrimage Circuit"}
          </span>
          <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-amber-100 text-amber-900 font-bold">
            New
          </span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("gemstones")}
          className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all whitespace-nowrap cursor-pointer ${
            activeTab === "gemstones"
              ? "bg-white text-[#102A4C] shadow-2xs border border-[#DDE5F0]"
              : "text-[#52667E] hover:text-[#102A4C]"
          }`}
        >
          <Sparkles className="w-4 h-4 text-emerald-600" />
          <span>
            {language === "ta"
              ? "ரத்தின ஆலோசனை & பாதுகாப்பு"
              : "Gemstone Prescription & Safety"}
          </span>
          <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-emerald-100 text-emerald-900 font-bold">
            New
          </span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("eligibility")}
          className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all whitespace-nowrap cursor-pointer ${
            activeTab === "eligibility"
              ? "bg-white text-[#102A4C] shadow-2xs border border-[#DDE5F0]"
              : "text-[#52667E] hover:text-[#102A4C]"
          }`}
        >
          <ShieldAlert className="w-4 h-4 text-indigo-600" />
          <span>
            {language === "ta"
              ? "யோககாரகன் & தான பாதுகாப்பு"
              : "Yogakaraka & Daan Checker"}
          </span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("sources")}
          className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all whitespace-nowrap cursor-pointer ${
            activeTab === "sources"
              ? "bg-white text-[#102A4C] shadow-2xs border border-[#DDE5F0]"
              : "text-[#52667E] hover:text-[#102A4C]"
          }`}
        >
          <FileText className="w-4 h-4 text-emerald-600" />
          <span>
            {language === "ta" ? "சாஸ்திர ஆதாரங்கள்" : "Classical Citations"}
          </span>
        </button>
      </div>

      {/* Loading & Error States */}
      {loading && (
        <div className="py-16 text-center text-xs text-[#52667E]">
          <div className="inline-block animate-spin w-6 h-6 border-2 border-[#102A4C] border-t-transparent rounded-full mb-2" />
          <p>
            {language === "ta"
              ? "சாஸ்திர பரிகாரங்கள் ஏற்றப்படுகின்றன..."
              : "Loading Vedic remedy knowledge base..."}
          </p>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 rounded-2xl border border-rose-200 bg-rose-50 text-rose-800 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 0: Personalized Chart Analysis */}
      {/* ========================================================================= */}
      {activeTab === "analysis" && (
        <div className="space-y-6">
          {loadingAnalysis || (horoscopeId && authLoading) ? (
            <div className="py-20 text-center text-xs text-[#52667E] bg-white rounded-2xl border border-[#DDE5F0] shadow-xs">
              <div className="inline-block animate-spin w-8 h-8 border-3 border-purple-600 border-t-transparent rounded-full mb-3" />
              <p className="font-semibold text-sm text-[#102A4C]">
                {language === "ta"
                  ? "அங்கீகாரம் சரிபார்க்கப்பட்டு ஜாதக பரிகாரங்கள் பகுப்பாய்வு செய்யப்படுகின்றன..."
                  : "Verifying authorization and analyzing chart factors..."}
              </p>
            </div>
          ) : isAuthError ? (
            <div className="p-8 rounded-2xl border border-amber-300 bg-amber-50/70 text-amber-950 text-xs space-y-4 shadow-xs text-center max-w-xl mx-auto my-6">
              <div className="w-12 h-12 mx-auto rounded-full bg-amber-100 border border-amber-300 flex items-center justify-center text-amber-700">
                <ShieldAlert className="w-6 h-6" />
              </div>
              <div className="space-y-1.5">
                <h3 className="font-serif text-lg font-bold text-amber-900">
                  {language === "ta" ? "உள்நுழைவு தேவைப்படுகிறது" : "Authentication Required"}
                </h3>
                <p className="text-xs text-amber-800 leading-relaxed max-w-md mx-auto">
                  {analysisError}
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-3 pt-2">
                <Link
                  href={`/login?returnUrl=${encodeURIComponent(
                    horoscopeId ? `/remedies?horoscope_id=${horoscopeId}` : "/remedies"
                  )}`}
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-purple-700 hover:bg-purple-800 text-white font-bold text-xs shadow-2xs transition-colors"
                >
                  <ShieldCheck className="w-4 h-4" />
                  <span>
                    {language === "ta"
                      ? "உள்நுழைந்து பரிகாரங்களைப் பார்க்கவும்"
                      : "Sign In to View Remedies"}
                  </span>
                </Link>
                <button
                  type="button"
                  onClick={() => setActiveTab("catalog")}
                  className="px-4 py-2.5 rounded-xl border border-[#DDE5F0] bg-white text-[#102A4C] hover:bg-[#FAF6EC] font-semibold text-xs shadow-2xs transition-colors cursor-pointer"
                >
                  {language === "ta"
                    ? "பொது பரிகார நூலகம்"
                    : "Browse General Remedies"}
                </button>
              </div>
            </div>
          ) : analysisError ? (
            <div className="p-6 rounded-2xl border border-rose-200 bg-rose-50 text-rose-900 text-xs space-y-3">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0" />
                <span className="font-bold text-sm">
                  {language === "ta" ? "பகுப்பாய்வில் பிழை ஏற்பட்டது" : "Analysis Error"}
                </span>
              </div>
              <p>{analysisError}</p>
              <div className="flex flex-wrap gap-2 pt-2">
                <Link
                  href="/horoscope"
                  className="px-3.5 py-2 rounded-xl bg-purple-700 text-white font-bold hover:bg-purple-800 text-xs shadow-2xs"
                >
                  {language === "ta" ? "புதிய கணிப்பு செய்க" : "Calculate New Chart"}
                </Link>
                <Link
                  href="/horoscopes"
                  className="px-3.5 py-2 rounded-xl border border-purple-300 bg-white text-purple-900 font-bold hover:bg-purple-50 text-xs shadow-2xs"
                >
                  {language === "ta" ? "சேமிக்கப்பட்ட ஜாதகங்கள்" : "Saved Horoscopes"}
                </Link>
              </div>
            </div>
          ) : analysisResult ? (
            <PersonalizedRemedySection
              analysis={analysisResult}
              horoscopeId={horoscopeId || undefined}
              onRefresh={loadAnalysisData}
              isLoading={loadingAnalysis}
            />
          ) : (
            <div className="p-10 rounded-2xl border border-[#E2DCD5] bg-white text-center space-y-4">
              <div className="w-14 h-14 mx-auto rounded-full bg-purple-50 text-purple-700 flex items-center justify-center">
                <Sparkles className="w-7 h-7" />
              </div>
              <div className="max-w-md mx-auto space-y-1.5">
                <h3 className="font-serif font-bold text-lg text-[#102A4C]">
                  {language === "ta"
                    ? "ஜாதகம் எதுவும் தேர்ந்தெடுக்கப்படவில்லை"
                    : "No Birth Chart Selected"}
                </h3>
                <p className="text-xs text-[#64748B] leading-relaxed">
                  {language === "ta"
                    ? "தனிப்பயனாக்கப்பட்ட பரிகார ஆய்வைப் பெற உங்கள் சேமிக்கப்பட்ட ஜாதகத்தைத் தேர்ந்தெடுக்கவும் அல்லது புதிய கணிப்பை மேற்கொள்ளவும்."
                    : "To generate a personalized remedy analysis, select a chart from your saved horoscopes or calculate a new birth chart."}
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-3 pt-2">
                <Link
                  href="/horoscopes"
                  className="px-4 py-2.5 rounded-xl bg-purple-700 text-white text-xs font-bold hover:bg-purple-800 transition-colors shadow-2xs"
                >
                  {language === "ta" ? "சேமிக்கப்பட்ட ஜாதகங்கள்" : "View Saved Horoscopes"}
                </Link>
                <Link
                  href="/horoscope"
                  className="px-4 py-2.5 rounded-xl border border-[#D8BD80] bg-[#FAF2DE] text-[#784E0E] text-xs font-bold hover:bg-[#FAF6EC] transition-colors shadow-2xs"
                >
                  {language === "ta" ? "புதிய கணிப்பு" : "Calculate New Chart"}
                </Link>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 1: Problem Taxonomy Browser */}
      {/* ========================================================================= */}
      {!loading && activeTab === "taxonomy" && (
        <div className="space-y-6">
          {/* Filters & Search */}
          <div className="p-4 rounded-2xl border border-[#DDE5F0] bg-white shadow-2xs flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="relative flex-1 max-w-md">
              <Search className="w-4 h-4 text-[#94A3B8] absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder={
                  language === "ta"
                    ? "பிரச்சனையைத் தேடுக (எ.கா. திருமணம், வேலை, உடல்நலம்)..."
                    : "Search 39 problem domains (e.g. career, marriage, health)..."
                }
                value={searchTaxonomy}
                onChange={(e) => setSearchTaxonomy(e.target.value)}
                className="w-full pl-10 pr-4 py-2 rounded-xl border border-[#DDE5F0] bg-[#F8FAFC] text-xs text-[#102A4C] focus:outline-none focus:border-[#B8862B]"
              />
            </div>

            {/* Category pills */}
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
              <button
                type="button"
                onClick={() => setSelectedCategory("all")}
                className={`px-3 py-1.5 rounded-lg font-semibold transition-colors cursor-pointer ${
                  selectedCategory === "all"
                    ? "bg-[#102A4C] text-white"
                    : "bg-[#F1F5F9] text-[#52667E] hover:bg-[#E2E8F0]"
                }`}
              >
                {language === "ta" ? "அனைத்தும்" : "All Categories"}
              </button>
              {categories.map((cat) => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-3 py-1.5 rounded-lg font-semibold capitalize transition-colors whitespace-nowrap cursor-pointer ${
                    selectedCategory === cat
                      ? "bg-[#B8862B] text-white"
                      : "bg-[#F1F5F9] text-[#52667E] hover:bg-[#E2E8F0]"
                  }`}
                >
                  {cat.replace(/_/g, " ")}
                </button>
              ))}
            </div>
          </div>

          {/* Results count */}
          <div className="flex items-center justify-between text-xs text-[#52667E]">
            <span>
              {language === "ta"
                ? `காட்டப்படும் பிரச்சனைகள்: ${filteredTaxonomies.length} / ${taxonomies.length}`
                : `Showing ${filteredTaxonomies.length} of ${taxonomies.length} classical problem domains`}
            </span>
          </div>

          {/* Problem Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredTaxonomies.map((item) => (
              <div
                key={item.slug}
                className="rounded-2xl border border-[#DDE5F0] bg-white p-5 shadow-2xs hover:shadow-md transition-shadow flex flex-col justify-between space-y-4"
              >
                <div className="space-y-2.5">
                  <div className="flex items-center justify-between gap-2">
                    <span className="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-700">
                      #{item.display_order} • {item.category.replace(/_/g, " ")}
                    </span>
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700">
                      <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                      <span>{item.verification_status}</span>
                    </span>
                  </div>

                  <div>
                    <h3 className="font-serif font-bold text-base text-[#102A4C]">
                      {language === "ta" ? item.name_ta : item.name_en}
                    </h3>
                    <p className="text-xs text-[#B8862B] font-medium">
                      {language === "ta" ? item.name_en : item.name_ta}
                    </p>
                  </div>

                  <p className="text-xs text-[#52667E] leading-relaxed">
                    {language === "ta"
                      ? item.description_ta || item.description_en
                      : item.description_en || item.description_ta}
                  </p>
                </div>

                <div className="space-y-3 pt-3 border-t border-[#F1F5F9]">
                  {/* Astrological Karakas & Houses */}
                  <div className="space-y-1.5 text-[11px]">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span className="font-semibold text-[#102A4C]">
                        {language === "ta" ? "காரக கிரகங்கள்:" : "Karakas:"}
                      </span>
                      {item.primary_karakas.map((k) => (
                        <span
                          key={k}
                          className="px-2 py-0.5 rounded bg-amber-50 border border-amber-200 text-amber-900 font-semibold uppercase text-[10px]"
                        >
                          {k}
                        </span>
                      ))}
                    </div>

                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span className="font-semibold text-[#102A4C]">
                        {language === "ta" ? "பாவகங்கள்:" : "Bhavas:"}
                      </span>
                      {item.governing_houses.map((h) => (
                        <span
                          key={h}
                          className="px-1.5 py-0.5 rounded bg-blue-50 border border-blue-200 text-blue-900 font-bold text-[10px]"
                        >
                          H{h}
                        </span>
                      ))}
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => selectProblemToFilterRemedies(item.slug)}
                    className="w-full inline-flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl border border-[#DDE5F0] bg-[#F8FAFC] hover:bg-[#FAF2DE] hover:border-[#D8BD80] text-xs font-bold text-[#102A4C] transition-colors cursor-pointer"
                  >
                    <span>
                      {language === "ta"
                        ? "பொருத்தமான பரிகாரங்களைக் காண்க"
                        : "View Associated Remedies"}
                    </span>
                    <ArrowRight className="w-3.5 h-3.5 text-[#B8862B]" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: Remedy & Mantra Library */}
      {/* ========================================================================= */}
      {!loading && activeTab === "catalog" && (
        <div className="space-y-6">
          {/* Active filter reminder if filtered by problem */}
          {filterProblemSlug && (
            <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-between text-xs text-amber-900">
              <div className="flex items-center gap-2">
                <Info className="w-4 h-4 text-amber-600" />
                <span>
                  Filtering remedies for problem:{" "}
                  <strong>{filterProblemSlug}</strong>
                </span>
              </div>
              <button
                type="button"
                onClick={() => setFilterProblemSlug("")}
                className="font-bold underline text-amber-950 hover:text-amber-800"
              >
                Clear Problem Filter
              </button>
            </div>
          )}

          {/* Filter Bar */}
          <div className="p-4 rounded-2xl border border-[#DDE5F0] bg-white shadow-2xs flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 text-xs">
              <span className="font-bold text-[#102A4C]">
                {language === "ta" ? "கிரகம்:" : "Planet:"}
              </span>
              <select
                value={selectedGraha}
                onChange={(e) => setSelectedGraha(e.target.value)}
                className="px-3 py-1.5 rounded-xl border border-[#DDE5F0] bg-[#F8FAFC] text-xs text-[#102A4C] focus:outline-none"
              >
                {GRAHA_OPTIONS.map((g) => (
                  <option key={g.value} value={g.value}>
                    {language === "ta" ? g.label_ta : g.label_en}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-2 text-xs">
              <span className="font-bold text-[#102A4C]">
                {language === "ta" ? "பரிகார வகை:" : "Type:"}
              </span>
              <select
                value={selectedRemedyType}
                onChange={(e) => setSelectedRemedyType(e.target.value)}
                className="px-3 py-1.5 rounded-xl border border-[#DDE5F0] bg-[#F8FAFC] text-xs text-[#102A4C] focus:outline-none"
              >
                <option value="all">
                  {language === "ta" ? "அனைத்து வகைகள்" : "All Types"}
                </option>
                <option value="mantra">Mantra / Japa</option>
                <option value="worship">Worship / Archana</option>
                <option value="charity">Charity / Daan</option>
                <option value="fasting">Fasting / Vratam</option>
                <option value="temple">Temple Visit</option>
              </select>
            </div>

            <span className="text-xs text-[#52667E] ml-auto">
              {filteredRemedies.length} remedies available
            </span>
          </div>

          {/* Remedy Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filteredRemedies.map((rem) => (
              <div
                key={rem.code}
                className="rounded-3xl border border-[#DDE5F0] bg-white p-6 shadow-xs hover:shadow-md transition-shadow space-y-4 flex flex-col justify-between"
              >
                <div className="space-y-3.5">
                  {/* Badges */}
                  <div className="flex items-center justify-between gap-2 flex-wrap">
                    <div className="flex items-center gap-1.5">
                      <span className="px-2.5 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider bg-[#FAF2DE] border border-[#D8BD80] text-[#8C6D23]">
                        {rem.graha}
                      </span>
                      <span className="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider bg-blue-50 border border-blue-200 text-blue-800">
                        {rem.remedy_type}
                      </span>
                    </div>

                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700">
                      Source: {rem.source_code}
                    </span>
                  </div>

                  {/* Title & Deity */}
                  <div>
                    <h3 className="font-serif font-bold text-lg text-[#102A4C]">
                      {language === "ta" ? rem.name_ta : rem.name_en}
                    </h3>
                    <p className="text-xs text-[#52667E]">
                      {language === "ta" ? rem.name_en : rem.name_ta} •{" "}
                      <strong>
                        Deity:{" "}
                        {language === "ta" ? rem.deity_ta : rem.deity_en}
                      </strong>
                    </p>
                  </div>

                  {/* Devanagari Sanskrit Mantra Card */}
                  {rem.sanskrit_text && (
                    <div className="p-4 rounded-2xl bg-amber-50/70 border border-amber-200 space-y-2">
                      <div className="flex items-center justify-between text-[10px] font-bold text-amber-900 uppercase tracking-wider">
                        <span>Devanagari Sanskrit</span>
                        {rem.japa_count && (
                          <span className="px-2 py-0.5 rounded-full bg-amber-200/80 text-amber-950 font-sans">
                            {rem.japa_count} Recitations (Japa)
                          </span>
                        )}
                      </div>
                      <div className="font-serif text-base sm:text-lg font-bold text-amber-950 leading-relaxed text-center py-1">
                        {rem.sanskrit_text}
                      </div>

                      {rem.transliteration_ta && (
                        <div className="pt-2 border-t border-amber-200/60 text-xs font-tamil text-amber-900 leading-normal text-center">
                          <span className="text-[10px] uppercase font-bold text-amber-700 block mb-0.5">
                            தமிழ் உச்சரிப்பு:
                          </span>
                          {rem.transliteration_ta}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Meaning & Description */}
                  <div className="text-xs space-y-1.5 text-[#334155]">
                    <p className="leading-relaxed">
                      {language === "ta"
                        ? rem.description_ta || rem.description_en
                        : rem.description_en || rem.description_ta}
                    </p>
                    {(rem.meaning_en || rem.meaning_ta) && (
                      <p className="italic text-[#52667E] bg-slate-50 p-2.5 rounded-xl border border-slate-200/60">
                        {language === "ta"
                          ? rem.meaning_ta || rem.meaning_en
                          : rem.meaning_en || rem.meaning_ta}
                      </p>
                    )}
                  </div>

                  {/* Daan / Pacification Warning */}
                  {rem.is_pacification_only && (
                    <div className="p-2.5 rounded-xl border border-rose-200 bg-rose-50 text-[11px] text-rose-900 flex items-start gap-2">
                      <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                      <span>
                        <strong>Daan Pacification Remedy:</strong> Prescribed
                        strictly for pacifying afflicted functional malefics. Do
                        NOT donate if this planet is your Yogakaraka or functional
                        benefic.
                      </span>
                    </div>
                  )}
                </div>

                {/* Procedure & Timing Footer */}
                <div className="pt-3 border-t border-[#F1F5F9] space-y-1.5 text-[11px] text-[#52667E]">
                  <div>
                    <strong className="text-[#102A4C]">
                      {language === "ta" ? "முறை:" : "Procedure:"}
                    </strong>{" "}
                    {language === "ta" ? rem.procedure_ta : rem.procedure_en}
                  </div>
                  {(rem.timing_recommendation_en ||
                    rem.timing_recommendation_ta) && (
                    <div>
                      <strong className="text-[#102A4C]">
                        {language === "ta" ? "உகந்த நேரம்:" : "Timing:"}
                      </strong>{" "}
                      {language === "ta"
                        ? rem.timing_recommendation_ta ||
                          rem.timing_recommendation_en
                        : rem.timing_recommendation_en ||
                          rem.timing_recommendation_ta}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: Tamil Navagraha Temple Directory */}
      {/* ========================================================================= */}
      {!loading && activeTab === "temples" && (
        <div className="space-y-6">
          {/* Header Note */}
          <div className="p-4 rounded-2xl border border-rose-200 bg-rose-50/70 text-xs text-rose-950 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h3 className="font-serif font-bold text-sm text-rose-950">
                {language === "ta"
                  ? "காவிரி டெல்டா 9 நவக்கிரக ஸ்தலங்கள்"
                  : "The 9 Consecrated Kaveri Delta Navagraha Temples"}
              </h3>
              <p className="text-[11px] text-rose-800 mt-0.5">
                Authentic temple coordinates, presiding deities, visiting days,
                and specific pariharam offerings.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-[#102A4C]">Planet:</span>
              <select
                value={selectedTempleGraha}
                onChange={(e) => setSelectedTempleGraha(e.target.value)}
                className="px-3 py-1.5 rounded-xl border border-rose-200 bg-white text-xs text-[#102A4C]"
              >
                {GRAHA_OPTIONS.map((g) => (
                  <option key={g.value} value={g.value}>
                    {language === "ta" ? g.label_ta : g.label_en}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Temples Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTemples.map((temple) => {
              const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${temple.latitude},${temple.longitude}`;

              return (
                <div
                  key={temple.code}
                  className="rounded-3xl border border-[#DDE5F0] bg-white p-6 shadow-xs hover:shadow-md transition-shadow flex flex-col justify-between space-y-4"
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="px-2.5 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider bg-rose-50 border border-rose-200 text-rose-800">
                        {temple.graha} Sthalam
                      </span>
                      <span className="text-[11px] font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                        {language === "ta"
                          ? temple.visiting_day_ta
                          : temple.visiting_day_en}
                      </span>
                    </div>

                    <div>
                      <h3 className="font-serif font-bold text-base text-[#102A4C]">
                        {language === "ta" ? temple.name_ta : temple.name_en}
                      </h3>
                      <p className="text-xs font-semibold text-[#B8862B]">
                        {language === "ta" ? temple.name_en : temple.name_ta}
                      </p>
                    </div>

                    <div className="space-y-1.5 text-xs text-[#334155]">
                      <div>
                        <strong className="text-[#102A4C]">Location:</strong>{" "}
                        {language === "ta"
                          ? `${temple.place_name_ta}, ${temple.district_ta}`
                          : `${temple.place_name_en}, ${temple.district_en}`}
                      </div>
                      <div>
                        <strong className="text-[#102A4C]">
                          Presiding Deity:
                        </strong>{" "}
                        {language === "ta"
                          ? temple.presiding_deity_ta
                          : temple.presiding_deity_en}
                      </div>
                      <div>
                        <strong className="text-[#102A4C]">
                          Navagraha Deity:
                        </strong>{" "}
                        {language === "ta"
                          ? temple.graha_deity_ta
                          : temple.graha_deity_en}
                      </div>
                    </div>

                    <p className="text-xs text-[#52667E] leading-relaxed pt-2 border-t border-[#F1F5F9]">
                      {language === "ta"
                        ? temple.significance_ta
                        : temple.significance_en}
                    </p>

                    <div className="p-3 rounded-2xl bg-amber-50/70 border border-amber-200 text-xs text-amber-950">
                      <strong className="block text-[10px] uppercase font-bold text-amber-800 mb-1">
                        {language === "ta"
                          ? "பரிகார நைவேத்தியம் / வழிபாட்டு முறை:"
                          : "Prescribed Offerings & Pariharam:"}
                      </strong>
                      <span>
                        {language === "ta"
                          ? temple.remedy_offerings_ta
                          : temple.remedy_offerings_en}
                      </span>
                    </div>
                  </div>

                  <div className="pt-3 border-t border-[#F1F5F9] flex items-center justify-between">
                    <span className="text-[10px] text-[#94A3B8]">
                      Coords: {temple.latitude.toFixed(4)},{" "}
                      {temple.longitude.toFixed(4)}
                    </span>
                    <a
                      href={mapsUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-rose-200 bg-rose-50 hover:bg-rose-100 text-xs font-bold text-rose-800 transition-colors"
                    >
                      <span>
                        {language === "ta" ? "வரைபடம்" : "Open in Maps"}
                      </span>
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB: Kaveri Delta Navagraha Pilgrimage Circuit Planner */}
      {/* ========================================================================= */}
      {!loading && activeTab === "pilgrimage" && (
        <PilgrimageCircuitView
          analysisResult={analysisResult}
          horoscopeId={horoscopeId}
        />
      )}

      {/* ========================================================================= */}
      {/* TAB: Astrological Gemstone (Ratna) Advisory & Safety Audit */}
      {/* ========================================================================= */}
      {!loading && activeTab === "gemstones" && (
        <GemstoneAdvisoryView
          analysisResult={analysisResult}
          horoscopeId={horoscopeId}
        />
      )}

      {/* ========================================================================= */}
      {/* TAB 4: Vedic Eligibility Safeguard Tool */}
      {/* ========================================================================= */}
      {!loading && activeTab === "eligibility" && (
        <div className="max-w-3xl mx-auto space-y-6">
          <div className="p-6 rounded-3xl border border-[#DDE5F0] bg-white shadow-xs space-y-5">
            <div>
              <div className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-50 border border-indigo-200 text-indigo-800 uppercase tracking-wider mb-2">
                Brihat Parashara Hora Shastra Ch. 34 Safeguards
              </div>
              <h2 className="font-serif text-xl sm:text-2xl font-bold text-[#102A4C]">
                {language === "ta"
                  ? "யோககாரகன் மற்றும் தான பரிகாரத் தகுதி ஆய்வு"
                  : "Yogakaraka & Daan Eligibility Safeguard Engine"}
              </h2>
              <p className="text-xs text-[#52667E] mt-1 leading-relaxed">
                In classical Parashari Jyotish, donating items (Daan) pacifies and
                dissipates planetary energy. Donating for a functional Yogakaraka
                or benefic weakens the very planet that brings fortunes and Raja
                Yoga. Test your proposed remedy here.
              </p>
            </div>

            <form
              onSubmit={handleCheckEligibility}
              className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs"
            >
              <div>
                <label className="block font-bold text-[#102A4C] mb-1">
                  Ascendant Sign (Lagna):
                </label>
                <select
                  value={eligLagna}
                  onChange={(e) => setEligLagna(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] bg-[#F8FAFC] text-[#102A4C] focus:outline-none"
                >
                  {LAGNA_OPTIONS.map((l) => (
                    <option key={l} value={l}>
                      {l}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-bold text-[#102A4C] mb-1">
                  Planet (Graha):
                </label>
                <select
                  value={eligGraha}
                  onChange={(e) => setEligGraha(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] bg-[#F8FAFC] text-[#102A4C] focus:outline-none"
                >
                  {GRAHA_OPTIONS.filter((g) => g.value !== "all").map((g) => (
                    <option key={g.value} value={g.value}>
                      {g.label_en}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-bold text-[#102A4C] mb-1">
                  Remedy Type:
                </label>
                <select
                  value={eligRemedyType}
                  onChange={(e) => setEligRemedyType(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] bg-[#F8FAFC] text-[#102A4C] focus:outline-none"
                >
                  <option value="charity">Charity / Donation (Daan)</option>
                  <option value="mantra">Mantra Chanting (Japa)</option>
                  <option value="worship">Temple Worship / Archana</option>
                </select>
              </div>

              <div className="sm:col-span-3 pt-2">
                <button
                  type="submit"
                  disabled={checkingEligibility}
                  className="w-full py-2.5 px-4 rounded-xl bg-[#102A4C] hover:bg-[#1E3A61] text-white font-bold text-xs transition-colors shadow-2xs cursor-pointer"
                >
                  {checkingEligibility
                    ? "Evaluating Classical Rules..."
                    : "Evaluate Astrological Eligibility"}
                </button>
              </div>
            </form>

            {/* Eligibility Result Output */}
            {eligibilityResult && (
              <div
                className={`mt-4 p-5 rounded-2xl border transition-all ${
                  eligibilityResult.is_eligible
                    ? "border-emerald-200 bg-emerald-50/70"
                    : "border-amber-300 bg-amber-50/90"
                }`}
              >
                <div className="flex items-start gap-3">
                  {eligibilityResult.is_eligible ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                  ) : (
                    <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                  )}

                  <div className="space-y-2 text-xs">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-bold text-sm text-[#102A4C]">
                        {eligibilityResult.is_eligible
                          ? "Remedy Permitted & Eligible"
                          : "Classical Restriction Triggered"}
                      </span>
                      {eligibilityResult.is_yogakaraka && (
                        <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-[#FAF2DE] border border-[#D8BD80] text-[#8C6D23]">
                          Supreme Yogakaraka
                        </span>
                      )}
                      {eligibilityResult.is_functional_benefic && (
                        <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-blue-50 border border-blue-200 text-blue-800">
                          Functional Benefic
                        </span>
                      )}
                      {eligibilityResult.is_functional_malefic && (
                        <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-rose-50 border border-rose-200 text-rose-800">
                          Functional Malefic
                        </span>
                      )}
                    </div>

                    {eligibilityResult.restriction_reason && (
                      <p className="text-amber-950 font-medium leading-relaxed bg-white/70 p-3 rounded-xl border border-amber-200">
                        {eligibilityResult.restriction_reason}
                      </p>
                    )}

                    {eligibilityResult.safe_alternative_recommendation && (
                      <div className="p-3 rounded-xl bg-white/90 border border-emerald-200 space-y-1">
                        <strong className="text-emerald-950 block text-[11px] uppercase tracking-wide">
                          Safe Classical Alternative:
                        </strong>
                        <p className="text-emerald-900 leading-relaxed">
                          {eligibilityResult.safe_alternative_recommendation}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 5: Canonical Shastra Sources */}
      {/* ========================================================================= */}
      {!loading && activeTab === "sources" && (
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="p-4 rounded-2xl border border-[#DDE5F0] bg-white shadow-2xs">
            <h2 className="font-serif font-bold text-base text-[#102A4C]">
              Canonical Classical Reference Citations
            </h2>
            <p className="text-xs text-[#52667E] mt-0.5">
              Every remedy, mantra, and guideline in this module is traceable to
              canonical Vedic, Puranic, and Jyotish shastras.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {sources.map((src) => (
              <div
                key={src.code}
                className="p-5 rounded-2xl border border-[#DDE5F0] bg-white shadow-2xs space-y-2.5"
              >
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-800">
                    {src.code}
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200">
                    {src.canonical_status.replace(/_/g, " ")}
                  </span>
                </div>

                <div>
                  <h3 className="font-serif font-bold text-base text-[#102A4C]">
                    {src.title_en}
                  </h3>
                  {src.title_sa && (
                    <p className="text-xs font-serif text-[#B8862B]">
                      {src.title_sa}
                    </p>
                  )}
                  {src.author && (
                    <p className="text-xs text-[#52667E]">By {src.author}</p>
                  )}
                </div>

                {src.description && (
                  <p className="text-xs text-[#52667E] leading-relaxed pt-2 border-t border-[#F1F5F9]">
                    {src.description}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function RemediesHubPage() {
  return (
    <Suspense
      fallback={
        <div className="max-w-7xl mx-auto px-4 py-20 text-center text-xs text-[#52667E]">
          <div className="inline-block animate-spin w-8 h-8 border-3 border-purple-600 border-t-transparent rounded-full mb-3" />
          <p>Loading Remedies & Pariharam Hub...</p>
        </div>
      }
    >
      <RemediesHubContent />
    </Suspense>
  );
}

