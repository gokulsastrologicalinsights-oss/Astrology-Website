"use client";

import React, { useState, useEffect, useMemo, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { getActiveCalculation, saveActiveCalculation } from "@/lib/storage";
import { FullHoroscopeResult, HoroscopeResponse } from "@/lib/types";
import {
  formatSerialNumber,
  formatBirthDate,
  formatBirthTime,
  calculateCalendarAge,
} from "@/lib/formatters";
import {
  formatHoroscopeSequence,
  prepareCalculationSnapshot,
} from "@/lib/horoscope-storage-utils";
import { SouthIndianChart } from "@/components/charts/SouthIndianChart";
import { NorthIndianChart } from "@/components/charts/NorthIndianChart";
import { PlanetaryTable } from "@/components/results/PlanetaryTable";
import { HousesTable } from "@/components/results/HousesTable";
import { DasaTimeline } from "@/components/results/DasaTimeline";
import { KpSection } from "@/components/results/KpSection";
import { PanchangCard } from "@/components/results/PanchangCard";
import { VedicYogaSection } from "@/components/results/VedicYogaSection";
import { NabhashaSection } from "@/components/results/NabhashaSection";
import { AshtakavargaSection } from "@/components/results/AshtakavargaSection";
import { DestinyCard } from "@/components/results/DestinyCard";
import {
  calculateNabhasha,
  calculateAshtakavarga,
  calculateVedicYogas,
  calculateVargaD1D9,
} from "@/lib/api";
import { buildPlanetContexts, enrichDasaTreeWithBenefitBhavas } from "@/lib/benefit-bhavas";
import { buildNavamsaHoroscope, buildBhavaHoroscope } from "@/lib/chart-transforms";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  Compass,
  ArrowLeft,
  Calendar,
  Clock,
  MapPin,
  Globe,
  Sliders,
  Printer,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Info,
  Sparkles,
  ShieldCheck,
  Edit3,
  FileText,
  Phone,
  MessageCircle,
  Download,
  Share2,
  X,
  Save,
  Check,
  Award,
  Layers,
  Star,
} from "lucide-react";

function HoroscopeResultsContent() {
  const searchParams = useSearchParams();
  const idParam = searchParams.get("id");
  const tabParam = searchParams.get("tab");
  const { language, t } = useLanguage();

  const [result, setResult] = useState<FullHoroscopeResult | null>(() => {
    if (!idParam) {
      return getActiveCalculation();
    }
    return null;
  });

  const [isLoadingSaved, setIsLoadingSaved] = useState<boolean>(!!idParam);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [isRetryingSave, setIsRetryingSave] = useState<boolean>(false);
  const [retryNotice, setRetryNotice] = useState<string | null>(null);

  // System Mode Pill Toggle: "vedic" (ॐ வேத ஜாதகம்) vs "kp" (★ கே.பி ஜாதகம்)
  const [systemMode, setSystemMode] = useState<"vedic" | "kp">("vedic");

  // Main Tabs: "horoscope" (ஜாதகம்) | "consultation" (ஆலோசனை) | "reports" (அறிக்கைகள் மற்றும் பதிவிறக்கங்கள்)
  const [mainTab, setMainTab] = useState<"horoscope" | "consultation" | "reports">("horoscope");

  // Secondary Tabs under Horoscope: "chart" | "facts" | "planets" | "dasa" | "ashtakavarga" | "yogas" | "destiny-card"
  const [secondaryTab, setSecondaryTab] = useState<
    "chart" | "facts" | "planets" | "dasa" | "ashtakavarga" | "yogas" | "destiny-card"
  >(() => {
    const validSecondary = ["chart", "facts", "planets", "dasa", "ashtakavarga", "yogas", "destiny-card"];
    if (tabParam && validSecondary.includes(tabParam)) {
      return tabParam as any;
    }
    if (tabParam === "kp") {
      return "chart";
    }
    return "chart";
  });

  // Chart Style Switcher: South Indian vs North Indian
  const [chartMode, setChartMode] = useState<"south" | "north">("south");

  // Notes Modal state
  const [showNotesModal, setShowNotesModal] = useState<boolean>(false);
  const [consultationNotes, setConsultationNotes] = useState<string>("");
  const [isSavingNotes, setIsSavingNotes] = useState<boolean>(false);
  const [notesSaveStatus, setNotesSaveStatus] = useState<string | null>(null);

  // Load existing notes from local storage on mount / id change
  useEffect(() => {
    const noteKey = `horoscope_notes_${idParam || result?.savedId || "active"}`;
    const stored = localStorage.getItem(noteKey);
    if (stored) {
      setConsultationNotes(stored);
    }
  }, [idParam, result?.savedId]);

  // Handle URL hash or tab parameters
  useEffect(() => {
    if (tabParam === "kp" || (typeof window !== "undefined" && window.location.hash === "#kp-events")) {
      setSystemMode("kp");
    } else if (tabParam === "consultation") {
      setMainTab("consultation");
    } else if (tabParam === "reports") {
      setMainTab("reports");
    } else if (tabParam && ["chart", "facts", "planets", "dasa", "ashtakavarga", "yogas", "destiny-card"].includes(tabParam)) {
      setMainTab("horoscope");
      setSecondaryTab(tabParam as any);
    }
  }, [tabParam]);

  const [isCalculatingExtensions, setIsCalculatingExtensions] = useState(false);

  const handleCalculateVedicExtensions = async () => {
    if (!result || isCalculatingExtensions) return;
    setIsCalculatingExtensions(true);
    try {
      const birthInput = {
        birth_date: result.clientInputs.birthDate,
        birth_time: result.clientInputs.birthTime,
        timezone: result.clientInputs.timezone,
        latitude: result.clientInputs.latitude,
        longitude: result.clientInputs.longitude,
        ayanamsa: result.clientInputs.ayanamsaId,
      };

      const [nabhashaRes, ashtakavargaRes, vedicYogaRes, vargaRes] = await Promise.all([
        calculateNabhasha(birthInput).catch((e) => {
          console.warn("Nabhasha calculation failed:", e);
          return null;
        }),
        calculateAshtakavarga(birthInput).catch((e) => {
          console.warn("Ashtakavarga calculation failed:", e);
          return null;
        }),
        calculateVedicYogas(birthInput).catch((e) => {
          console.warn("Vedic Yoga calculation failed:", e);
          return null;
        }),
        calculateVargaD1D9(birthInput).catch((e) => {
          console.warn("Varga D1/D9 calculation failed:", e);
          return null;
        }),
      ]);

      const updatedHoroscope = {
        ...result.horoscope,
        nabhasha_yogas: nabhashaRes || result.horoscope.nabhasha_yogas,
        ashtakavarga: ashtakavargaRes || result.horoscope.ashtakavarga,
        vedic_yogas: vedicYogaRes || result.horoscope.vedic_yogas,
        varga_d1_d9: vargaRes || result.horoscope.varga_d1_d9,
      };

      const updatedResult: FullHoroscopeResult = {
        ...result,
        horoscope: updatedHoroscope,
        nabhasha: nabhashaRes || result.nabhasha,
        ashtakavarga: ashtakavargaRes || result.ashtakavarga,
        vedic_yogas: vedicYogaRes || result.vedic_yogas,
      };

      setResult(updatedResult);
      saveActiveCalculation(updatedResult);
    } catch (err) {
      console.error("Failed to compute Vedic extensions:", err);
    } finally {
      setIsCalculatingExtensions(false);
    }
  };

  // Load saved record directly from Supabase if id is present in URL
  useEffect(() => {
    if (idParam) {
      setIsLoadingSaved(true);
      setLoadError(null);
      setResult(null);
      fetch(`/api/horoscopes/${idParam}`)
        .then(async (res) => {
          if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.error || "Failed to load saved horoscope.");
          }
          return res.json();
        })
        .then((data) => {
          const item = data.horoscope;
          const calc = item.calculation_result;
          const isEdited =
            item.updated_at &&
            item.created_at &&
            new Date(item.updated_at).getTime() - new Date(item.created_at).getTime() > 1000;

          // Auto-heal dasa tree to ensure accurate canonical Vedic house occupancies
          if (calc.horoscope?.planets && calc.horoscope?.ascendant && calc.dasa?.dasa_tree) {
            try {
              const contexts = buildPlanetContexts(calc.horoscope.planets, calc.horoscope.ascendant, calc.horoscope.houses);
              enrichDasaTreeWithBenefitBhavas(calc.dasa.dasa_tree, contexts);
            } catch (healErr) {
              console.warn("Could not auto-heal dasa tree for saved record:", healErr);
            }
          }

          const unpackedResult: FullHoroscopeResult = {
            horoscope: calc.horoscope,
            dasa: calc.dasa,
            kp: calc.kp,
            nabhasha: calc.horoscope?.nabhasha_yogas || calc.nabhasha,
            ashtakavarga: calc.horoscope?.ashtakavarga || calc.ashtakavarga,
            vedic_yogas: calc.horoscope?.vedic_yogas || calc.vedic_yogas,
            calculatedAt: calc.calculatedAt || item.created_at,
            savedId: item.id,
            displayNumber: item.display_number,
            isSaved: true,
            editedAfterCalculation: isEdited,
            clientInputs: {
              fullName: item.person_name,
              birthDate: item.birth_date,
              birthTime: item.birth_time,
              isTimeConfirmed: true,
              locationName: item.birthplace,
              latitude: item.latitude,
              longitude: item.longitude,
              timezone: item.timezone,
              ayanamsaId: item.ayanamsa_id,
              houseSystemId: item.house_system_id,
            },
          };
          setResult(unpackedResult);
          saveActiveCalculation(unpackedResult);

          // If vedic_yogas or varga_d1_d9 is not in saved snapshot, auto-calculate in background
          if (!calc.horoscope?.vedic_yogas && !calc.vedic_yogas) {
            calculateVedicYogas({
              birth_date: item.birth_date,
              birth_time: item.birth_time,
              timezone: item.timezone,
              latitude: item.latitude,
              longitude: item.longitude,
              ayanamsa: item.ayanamsa_id,
              house_system: item.house_system_id,
            })
              .then((yogaRes) => {
                setResult((prev) => {
                  if (!prev) return null;
                  const updated: FullHoroscopeResult = {
                    ...prev,
                    vedic_yogas: yogaRes,
                    horoscope: {
                      ...prev.horoscope,
                      vedic_yogas: yogaRes,
                    },
                  };
                  saveActiveCalculation(updated);
                  return updated;
                });
              })
              .catch((e) => {
                console.warn("Auto-calculation of Vedic Yogas failed:", e);
              });
          }
        })
        .catch((err) => {
          setLoadError(err.message || "Failed to load saved horoscope.");
        })
        .finally(() => {
          setIsLoadingSaved(false);
        });
    }
  }, [idParam]);

  useEffect(() => {
    const pageTitle = result?.clientInputs?.fullName
      ? `${result.clientInputs.fullName}'s ${t.resultsTitle} | ${t.brandName}`
      : `${t.resultsTitle} | ${t.brandName}`;
    document.title = pageTitle;
  }, [result, t.resultsTitle, t.brandName]);

  // Retry Save handler for calculations where automatic save encountered an error
  const handleRetrySave = async () => {
    if (!result) return;
    setIsRetryingSave(true);
    setRetryNotice(null);

    const idempotencyKey =
      result.idempotencyKey ||
      (result as any).calculation_result?.idempotency_key ||
      `calc_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

    try {
      const compactedSnapshot = prepareCalculationSnapshot(result, idempotencyKey);
      const res = await fetch("/api/horoscopes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          idempotency_key: idempotencyKey,
          person_name: result.clientInputs.fullName?.trim() || "Unnamed Horoscope",
          birth_date: result.clientInputs.birthDate,
          birth_time: result.clientInputs.birthTime,
          timezone: result.clientInputs.timezone,
          birthplace: result.clientInputs.locationName,
          latitude: result.clientInputs.latitude,
          longitude: result.clientInputs.longitude,
          ayanamsa_id: result.clientInputs.ayanamsaId,
          house_system_id: result.clientInputs.houseSystemId,
          calculation_result: compactedSnapshot,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Save failed.");
      }

      const updated: FullHoroscopeResult = {
        ...result,
        savedId: data.horoscope.id,
        displayNumber: data.horoscope.display_number,
        isSaved: true,
        saveError: undefined,
        idempotencyKey,
      };
      setResult(updated);
      saveActiveCalculation(updated);
    } catch (err: any) {
      setResult((prev) =>
        prev
          ? {
              ...prev,
              isSaved: false,
              saveError: err?.message || "Failed to save horoscope.",
            }
          : null
      );
    } finally {
      setIsRetryingSave(false);
    }
  };

  // Save consultation notes handler
  const handleSaveNotes = () => {
    setIsSavingNotes(true);
    const noteKey = `horoscope_notes_${idParam || result?.savedId || "active"}`;
    localStorage.setItem(noteKey, consultationNotes);
    setTimeout(() => {
      setIsSavingNotes(false);
      setNotesSaveStatus(language === "ta" ? "குறிப்புகள் சேமிக்கப்பட்டன!" : "Notes saved successfully!");
      setTimeout(() => setNotesSaveStatus(null), 2500);
    }, 400);
  };

  // Derive Navamsa D9 and Bhava Chakra horoscopes
  const d9Horoscope = useMemo(() => {
    if (!result?.horoscope) return null;
    return buildNavamsaHoroscope(result.horoscope);
  }, [result?.horoscope]);

  const bhavaHoroscope = useMemo(() => {
    if (!result?.horoscope) return null;
    return buildBhavaHoroscope(result.horoscope);
  }, [result?.horoscope]);

  if (isLoadingSaved) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-24 text-center space-y-4">
        <div className="inline-block animate-spin w-10 h-10 border-4 border-[#153F6B] border-t-transparent rounded-full" />
        <h2 className="font-serif text-lg font-bold text-[#183047]">
          {language === "ta"
            ? "சேமிக்கப்பட்ட ஜாதகம் ஏற்றப்படுகிறது..."
            : "Loading saved horoscope snapshot..."}
        </h2>
        <p className="text-xs text-[#8190A6]">
          {t.openHoroscopeStoredNotice}
        </p>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center space-y-6">
        <div className="w-16 h-16 rounded-full bg-rose-50 border border-rose-200 flex items-center justify-center mx-auto text-rose-600">
          <AlertCircle className="w-8 h-8" />
        </div>
        <h2 className="font-serif text-2xl font-bold text-[#183047]">
          {language === "ta" ? "ஜாதகத்தை ஏற்ற முடியவில்லை" : "Could Not Load Horoscope"}
        </h2>
        <p className="text-sm text-[#8190A6] max-w-md mx-auto">{loadError}</p>
        <div className="pt-2">
          <Link
            href="/horoscopes"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-bold text-white bg-[#153F6B] hover:bg-[#0F3155] shadow-sm transition-all"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>{t.backToSavedHoroscopes}</span>
          </Link>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center space-y-6">
        <div className="w-16 h-16 rounded-full bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center mx-auto text-[#B4872B]">
          <Compass className="w-8 h-8" />
        </div>
        <h2 className="font-serif text-2xl font-bold text-[#183047]">
          {language === "ta"
            ? "ஜாதகத் தரவு எதுவும் கிடைக்கவில்லை"
            : "No Active Calculation Found"}
        </h2>
        <p className="text-sm text-[#8190A6] leading-relaxed max-w-md mx-auto">
          {language === "ta"
            ? "ஜாதக முடிவுகளைப் பார்க்க தயவுசெய்து உங்கள் பிறப்பு விவரங்களை உள்ளிட்டு கணக்கீட்டைத் தொடங்கவும்."
            : "Please enter your birth details to generate and inspect planetary positions, charts, and dasa periods."}
        </p>
        <div className="pt-2">
          <Link
            href="/horoscope"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-lg text-sm font-bold text-white bg-[#153F6B] hover:bg-[#0F3155] shadow-sm transition-all"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>{t.navHoroscope}</span>
          </Link>
        </div>
      </div>
    );
  }

  const { horoscope, dasa, kp, clientInputs } = result;
  const birthDateDisplay = formatBirthDate(clientInputs.birthDate, language);
  const birthTimeDisplay = formatBirthTime(clientInputs.birthTime);
  const calculatedAge = calculateCalendarAge(clientInputs.birthDate);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8 space-y-5">
      {/* 1. Breadcrumbs */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <Breadcrumbs
          items={[
            {
              label: language === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools",
              href: "/tools",
            },
            {
              label: language === "ta" ? "ஜாதகம்" : "Horoscopes",
              href: "/horoscopes",
            },
            {
              label: clientInputs.fullName || (language === "ta" ? "ஜாதக விவரங்கள்" : "Horoscope Details"),
            },
          ]}
        />
        <Link
          href="/horoscopes"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#8190A6] hover:text-[#153F6B] transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>{t.backToSavedHoroscopes}</span>
        </Link>
      </div>

      {/* 2. Page Header & Mode Selector Card (Screenshot 3 Reference) */}
      <div className="bg-white rounded-xl border border-[#D9DEE7] p-4 sm:p-5 shadow-2xs space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          {/* Left: Heading & Serial Number */}
          <div className="flex items-center gap-3">
            <h1 className="font-serif text-xl sm:text-2xl font-bold text-[#183047] flex items-center gap-2.5">
              <span>{language === "ta" ? "ஜாதக விவரங்கள்" : "Horoscope Details"}</span>
              {result.displayNumber && (
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono font-bold bg-[#FAF2DE] text-[#B4872B] border border-[#D8BD80]">
                  #{formatSerialNumber(result.displayNumber)}
                </span>
              )}
            </h1>
          </div>

          {/* Center: System Mode Pill Toggle [ ॐ வேத ஜாதகம் | ★ கே.பி ஜாதகம் ] (Screenshot 3) */}
          <div className="inline-flex items-center p-1 rounded-lg bg-[#F2F3F5] border border-[#D9DEE7] self-start lg:self-center">
            <button
              type="button"
              onClick={() => {
                setSystemMode("vedic");
                if (mainTab !== "horoscope") setMainTab("horoscope");
              }}
              className={`inline-flex items-center gap-1.5 px-4 py-1.5 rounded-md text-xs font-bold transition-all cursor-pointer ${
                systemMode === "vedic"
                  ? "bg-[#153F6B] text-white shadow-2xs"
                  : "text-[#52667E] hover:text-[#183047]"
              }`}
            >
              <span>ॐ</span>
              <span>{language === "ta" ? "வேத ஜாதகம்" : "Vedic Horoscope"}</span>
            </button>
            <button
              type="button"
              onClick={() => setSystemMode("kp")}
              className={`inline-flex items-center gap-1.5 px-4 py-1.5 rounded-md text-xs font-bold transition-all cursor-pointer ${
                systemMode === "kp"
                  ? "bg-[#153F6B] text-white shadow-2xs"
                  : "text-[#52667E] hover:text-[#183047]"
              }`}
            >
              <Star className="w-3.5 h-3.5 text-[#B4872B]" />
              <span>{language === "ta" ? "கே.பி ஜாதகம்" : "KP System"}</span>
            </button>
          </div>

          {/* Right: Actions [Remedies, Edit, Notes, Print, Back] */}
          <div className="flex flex-wrap items-center gap-2">
            <Link
              href={`/remedies${result.savedId || idParam ? `?horoscope_id=${encodeURIComponent(result.savedId || idParam || "")}` : ""}`}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-purple-300 bg-purple-50 text-xs font-bold text-purple-900 hover:bg-purple-100 shadow-2xs transition-colors"
            >
              <ShieldCheck className="w-3.5 h-3.5 text-purple-600" />
              <span>{language === "ta" ? "பரிகாரங்கள்" : "View Remedies"}</span>
            </Link>

            <Link
              href={`/horoscope?edit_id=${result.savedId || idParam || ""}`}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#D9DEE7] bg-white text-xs font-semibold text-[#183047] hover:bg-[#F2F3F5] shadow-2xs transition-colors"
            >
              <Edit3 className="w-3.5 h-3.5 text-[#153F6B]" />
              <span>{language === "ta" ? "திருத்துக" : "Edit"}</span>
            </Link>

            <button
              type="button"
              onClick={() => setShowNotesModal(true)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#D9DEE7] bg-white text-xs font-semibold text-[#183047] hover:bg-[#F2F3F5] shadow-2xs transition-colors cursor-pointer"
            >
              <FileText className="w-3.5 h-3.5 text-[#B4872B]" />
              <span>{language === "ta" ? "குறிப்புகள்" : "Notes"}</span>
            </button>

            <button
              type="button"
              onClick={() => window.print()}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#D9DEE7] bg-white text-xs font-semibold text-[#183047] hover:bg-[#F2F3F5] shadow-2xs transition-colors cursor-pointer"
            >
              <Printer className="w-3.5 h-3.5 text-[#52667E]" />
              <span>{language === "ta" ? "அச்சிடுக" : "Print"}</span>
            </button>

            <Link
              href="/horoscopes"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#D9DEE7] bg-[#F2F3F5] text-xs font-bold text-[#183047] hover:bg-[#E2E8F0] shadow-2xs transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>{language === "ta" ? "பின்செல்க" : "Back"}</span>
            </Link>
          </div>
        </div>

        {/* 3. Customer Details Horizontal Info Row (Screenshot 3 Reference) */}
        <div className="pt-3 border-t border-[#D9DEE7] flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-[#52667E]">
          <div className="flex items-center gap-1">
            <span className="font-semibold text-[#183047]">{language === "ta" ? "பெயர்:" : "Name:"}</span>
            <span className="font-bold text-[#153F6B]">{clientInputs.fullName || (language === "ta" ? "பெயரிடப்படாதவர்" : "Unnamed")}</span>
          </div>

          <span className="text-[#D9DEE7] hidden sm:inline">|</span>

          <div className="flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5 text-[#B4872B]" />
            <span className="font-semibold text-[#183047]">{language === "ta" ? "பிறந்த தேதி:" : "Date of Birth:"}</span>
            <span>{birthDateDisplay}</span>
            {calculatedAge !== null && (
              <span className="font-semibold text-[#153F6B]">
                ({language === "ta" ? `வயது: ${calculatedAge}` : `Age: ${calculatedAge}`})
              </span>
            )}
          </div>

          <span className="text-[#D9DEE7] hidden sm:inline">|</span>

          <div className="flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5 text-[#B4872B]" />
            <span className="font-semibold text-[#183047]">{language === "ta" ? "இடம்:" : "Place:"}</span>
            <span className="truncate max-w-xs">{clientInputs.locationName || t.locationUnavailable}</span>
          </div>

          <span className="text-[#D9DEE7] hidden sm:inline">|</span>

          <div className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5 text-[#B4872B]" />
            <span className="font-semibold text-[#183047]">{language === "ta" ? "பிறந்த நேரம்:" : "Time:"}</span>
            <span className="font-mono">{birthTimeDisplay}</span>
          </div>

          <span className="text-[#D9DEE7] hidden sm:inline">|</span>

          <div className="flex items-center gap-1">
            <Sliders className="w-3.5 h-3.5 text-[#8190A6]" />
            <span className="font-semibold text-[#183047]">{language === "ta" ? "அயனாம்சம்:" : "Ayanamsa:"}</span>
            <span>{horoscope.metadata?.ayanamsa_name || "Lahiri"}</span>
          </div>
        </div>
      </div>

      {/* Notifications / Status Banners */}
      {isRetryingSave && (
        <div className="p-3 rounded-lg bg-blue-50 border border-blue-200 text-blue-900 text-xs flex items-center gap-2 shadow-2xs">
          <RefreshCw className="w-4 h-4 text-blue-600 animate-spin shrink-0" />
          <span className="font-semibold">{language === "ta" ? "சேமிக்கப்படுகிறது…" : "Saving…"}</span>
        </div>
      )}

      {result.isSaved && result.displayNumber && !isRetryingSave && (
        <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs flex items-center justify-between gap-3 shadow-2xs">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>
              {language === "ta"
                ? `வெற்றிகரமாகச் சேமிக்கப்பட்டது — ${formatHoroscopeSequence(result.displayNumber, language)}.`
                : `Saved successfully — ${formatHoroscopeSequence(result.displayNumber, language)}.`}
            </span>
          </div>
          <Link href="/horoscopes" className="underline font-semibold text-emerald-800 hover:text-emerald-950 shrink-0">
            {t.backToSavedHoroscopes}
          </Link>
        </div>
      )}

      {result.saveError && !result.isSaved && !isRetryingSave && (
        <div className="p-3 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
            <div>
              <span className="font-bold text-amber-950">
                {language === "ta" ? "சேமிக்க முடியவில்லை — மீண்டும் முயற்சிக்கவும்." : "Save failed — Retry."}
              </span>
              <p className="text-[11px] text-amber-800 mt-0.5">
                {language === "ta"
                  ? "கணக்கீடு முடிந்தது, ஆனால் முடிவுகள் உங்கள் கணக்கில் இன்னும் சேமிக்கப்படவில்லை."
                  : "Calculation completed, but the result has not yet been saved to your account."}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={handleRetrySave}
            disabled={isRetryingSave}
            className="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#B4872B] hover:bg-[#8C6D23] text-white font-semibold text-xs transition-colors shrink-0 cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>{language === "ta" ? "மீண்டும் முயற்சிக்கவும்" : "Retry"}</span>
          </button>
        </div>
      )}

      {/* Distinction notice if birth details were edited after calculation */}
      {result.editedAfterCalculation && (
        <div className="p-3 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-start gap-2.5">
          <Info className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <strong className="font-semibold block">{t.editedWithoutRecalcBadge}</strong>
            <p className="mt-0.5 leading-relaxed">{t.editedWithoutRecalcNotice}</p>
          </div>
        </div>
      )}

      {/* 4. KP Mode View (Activated via Header Pill Toggle) */}
      {systemMode === "kp" ? (
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 rounded-lg bg-white border border-[#D9DEE7] shadow-2xs">
            <div className="flex items-center gap-2 text-xs font-bold text-[#153F6B]">
              <Star className="w-4 h-4 text-[#B4872B]" />
              <span>{language === "ta" ? "கே.பி. கிருஷ்ணமூர்த்தி பத்ததி முறை" : "KP Krishnamurti Paddhati System"}</span>
            </div>
            <button
              type="button"
              onClick={() => setSystemMode("vedic")}
              className="text-xs font-bold text-[#B4872B] hover:underline cursor-pointer"
            >
              {language === "ta" ? "← வேத ஜாதகத்திற்குத் திரும்பு" : "← Back to Vedic Horoscope"}
            </button>
          </div>

          <KpSection
            kp={kp}
            dasa={dasa}
            horoscope={horoscope}
            savedHoroscopeId={result.savedId}
          />
        </div>
      ) : (
        /* 5. Vedic Mode View */
        <div className="space-y-5">
          {/* Main Tabs (Screenshot 3 Reference: Horoscope | Consultation | Reports) */}
          <div className="flex items-center gap-1.5 border-b border-[#D9DEE7] pb-1 overflow-x-auto">
            <button
              type="button"
              onClick={() => setMainTab("horoscope")}
              className={`px-5 py-2 text-xs sm:text-sm font-bold rounded-lg transition-all cursor-pointer ${
                mainTab === "horoscope"
                  ? "bg-[#153F6B] text-white shadow-2xs"
                  : "text-[#52667E] hover:text-[#153F6B] hover:bg-white"
              }`}
            >
              {language === "ta" ? "ஜாதகம்" : "Horoscope"}
            </button>

            <button
              type="button"
              onClick={() => setMainTab("consultation")}
              className={`px-5 py-2 text-xs sm:text-sm font-bold rounded-lg transition-all cursor-pointer ${
                mainTab === "consultation"
                  ? "bg-[#153F6B] text-white shadow-2xs"
                  : "text-[#52667E] hover:text-[#153F6B] hover:bg-white"
              }`}
            >
              {language === "ta" ? "ஆலோசனை" : "Consultation"}
            </button>

            <button
              type="button"
              onClick={() => setMainTab("reports")}
              className={`px-5 py-2 text-xs sm:text-sm font-bold rounded-lg transition-all cursor-pointer ${
                mainTab === "reports"
                  ? "bg-[#153F6B] text-white shadow-2xs"
                  : "text-[#52667E] hover:text-[#153F6B] hover:bg-white"
              }`}
            >
              {language === "ta" ? "அறிக்கைகள் மற்றும் பதிவிறக்கங்கள்" : "Reports & Downloads"}
            </button>
          </div>

          {/* MAIN TAB 1: HOROSCOPE */}
          {mainTab === "horoscope" && (
            <div className="space-y-5">
              {/* Secondary Tabs (Screenshot 3 Reference: ஜாதகம் | உண்மைகள் | கிரக நிலைகள் | தசா புத்தி | அஷ்டகவர்க பலன்கள் | யோகங்கள் | விதி அட்டை) */}
              <div className="flex items-center gap-2 border-b border-[#D9DEE7] overflow-x-auto pb-0.5 text-xs font-semibold">
                <button
                  type="button"
                  onClick={() => setSecondaryTab("chart")}
                  className={`pb-2 px-3 transition-all cursor-pointer whitespace-nowrap ${
                    secondaryTab === "chart"
                      ? "border-b-2 border-[#B4872B] text-[#153F6B] font-bold"
                      : "text-[#52667E] hover:text-[#183047]"
                  }`}
                >
                  {language === "ta" ? "ஜாதகம்" : "Charts"}
                </button>

                <button
                  type="button"
                  onClick={() => setSecondaryTab("facts")}
                  className={`pb-2 px-3 transition-all cursor-pointer whitespace-nowrap ${
                    secondaryTab === "facts"
                      ? "border-b-2 border-[#B4872B] text-[#153F6B] font-bold"
                      : "text-[#52667E] hover:text-[#183047]"
                  }`}
                >
                  {language === "ta" ? "உண்மைகள்" : "Facts & Panchang"}
                </button>

                <button
                  type="button"
                  onClick={() => setSecondaryTab("planets")}
                  className={`pb-2 px-3 transition-all cursor-pointer whitespace-nowrap ${
                    secondaryTab === "planets"
                      ? "border-b-2 border-[#B4872B] text-[#153F6B] font-bold"
                      : "text-[#52667E] hover:text-[#183047]"
                  }`}
                >
                  {language === "ta" ? "கிரக நிலைகள்" : "Planetary Positions"}
                </button>

                <button
                  type="button"
                  onClick={() => setSecondaryTab("dasa")}
                  className={`pb-2 px-3 transition-all cursor-pointer whitespace-nowrap ${
                    secondaryTab === "dasa"
                      ? "border-b-2 border-[#B4872B] text-[#153F6B] font-bold"
                      : "text-[#52667E] hover:text-[#183047]"
                  }`}
                >
                  {language === "ta" ? "தசா புத்தி" : "Dasa–Bhukti"}
                </button>

                <button
                  type="button"
                  onClick={() => setSecondaryTab("ashtakavarga")}
                  className={`pb-2 px-3 transition-all cursor-pointer whitespace-nowrap ${
                    secondaryTab === "ashtakavarga"
                      ? "border-b-2 border-[#B4872B] text-[#153F6B] font-bold"
                      : "text-[#52667E] hover:text-[#183047]"
                  }`}
                >
                  {language === "ta" ? "அஷ்டகவர்க பலன்கள்" : "Ashtakavarga"}
                </button>

                <button
                  type="button"
                  onClick={() => setSecondaryTab("yogas")}
                  className={`pb-2 px-3 transition-all cursor-pointer whitespace-nowrap ${
                    secondaryTab === "yogas"
                      ? "border-b-2 border-[#B4872B] text-[#153F6B] font-bold"
                      : "text-[#52667E] hover:text-[#183047]"
                  }`}
                >
                  {language === "ta" ? "யோகங்கள்" : "Yogas"}
                </button>

                <button
                  type="button"
                  onClick={() => setSecondaryTab("destiny-card")}
                  className={`pb-2 px-3 transition-all cursor-pointer whitespace-nowrap flex items-center gap-1 ${
                    secondaryTab === "destiny-card"
                      ? "border-b-2 border-[#B4872B] text-[#B4872B] font-bold"
                      : "text-amber-800 hover:text-amber-950"
                  }`}
                >
                  <Sparkles className="w-3.5 h-3.5 text-[#B4872B]" />
                  <span>{language === "ta" ? "விதி அட்டை" : "Destiny Card"}</span>
                </button>
              </div>

              {/* Sub-Tab 1: CHARTS (Screenshot 3 Reference - 3 Charts Side-by-Side: Rasi, Navamsa, Bhava) */}
              {secondaryTab === "chart" && (
                <div className="space-y-6">
                  {/* Style Switcher Bar: South vs North Indian */}
                  <div className="flex items-center justify-between">
                    <div className="text-xs text-[#8190A6]">
                      {language === "ta"
                        ? "பாரம்பரிய தென்னிந்திய முறைப்படி ராசி, நவாம்சம் மற்றும் பாவக கட்டங்கள்."
                        : "Classical charts: Rasi (D1), Navamsa (D9), and Bhava Chakra."}
                    </div>

                    <div className="flex items-center gap-1.5 p-1 rounded-lg bg-white border border-[#D9DEE7] text-xs">
                      <button
                        type="button"
                        onClick={() => setChartMode("south")}
                        className={`px-2.5 py-1 rounded font-bold transition-all cursor-pointer ${
                          chartMode === "south"
                            ? "bg-[#153F6B] text-white shadow-2xs"
                            : "text-[#52667E] hover:text-[#183047]"
                        }`}
                      >
                        {t.chartSouthIndian}
                      </button>
                      <button
                        type="button"
                        onClick={() => setChartMode("north")}
                        className={`px-2.5 py-1 rounded font-bold transition-all cursor-pointer ${
                          chartMode === "north"
                            ? "bg-[#153F6B] text-white shadow-2xs"
                            : "text-[#52667E] hover:text-[#183047]"
                        }`}
                      >
                        {t.chartNorthIndian}
                      </button>
                    </div>
                  </div>

                  {/* 3 Charts Responsive Grid (Screenshot 3 Reference) */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 items-start">
                    {/* Chart 1: Rasi (D1) */}
                    <div className="bg-white rounded-xl border border-[#D9DEE7] p-3.5 sm:p-4 shadow-2xs flex flex-col items-center">
                      <div className="w-full text-center pb-2 mb-2 border-b border-[#F2F3F5]">
                        <h3 className="font-bold text-xs sm:text-sm text-[#183047]">
                          {language === "ta"
                            ? "ராசி (D1) - உடல் மற்றும் பொதுவானவை"
                            : "Rasi (D1) - Physical & General"}
                        </h3>
                      </div>
                      {chartMode === "south" ? (
                        <SouthIndianChart
                          horoscope={horoscope}
                          centerLabel={language === "ta" ? "ராசி" : "Rasi"}
                          centerNumber="(1)"
                        />
                      ) : (
                        <NorthIndianChart horoscope={horoscope} />
                      )}
                    </div>

                    {/* Chart 2: Navamsa (D9) */}
                    <div className="bg-white rounded-xl border border-[#D9DEE7] p-3.5 sm:p-4 shadow-2xs flex flex-col items-center">
                      <div className="w-full text-center pb-2 mb-2 border-b border-[#F2F3F5]">
                        <h3 className="font-bold text-xs sm:text-sm text-[#183047]">
                          {language === "ta"
                            ? "நவாம்சம் (D9) - வாழ்க்கைத் துணை மற்றும் பலம்"
                            : "Navamsa (D9) - Strength & Spouse"}
                        </h3>
                      </div>
                      {d9Horoscope && (
                        chartMode === "south" ? (
                          <SouthIndianChart
                            horoscope={d9Horoscope}
                            centerLabel={language === "ta" ? "நவாம்சம்" : "Navamsa"}
                            centerNumber="(9)"
                          />
                        ) : (
                          <NorthIndianChart horoscope={d9Horoscope} />
                        )
                      )}
                    </div>

                    {/* Chart 3: Bhava Chakra */}
                    <div className="bg-white rounded-xl border border-[#D9DEE7] p-3.5 sm:p-4 shadow-2xs flex flex-col items-center md:col-span-2 lg:col-span-1">
                      <div className="w-full text-center pb-2 mb-2 border-b border-[#F2F3F5]">
                        <h3 className="font-bold text-xs sm:text-sm text-[#183047]">
                          {language === "ta" ? "பாவக சக்கரம்" : "Bhava Chakra (House Cusps)"}
                        </h3>
                      </div>
                      {bhavaHoroscope && (
                        chartMode === "south" ? (
                          <SouthIndianChart
                            horoscope={bhavaHoroscope}
                            centerLabel={language === "ta" ? "பாவகம்" : "Bhava"}
                            centerNumber="(B)"
                          />
                        ) : (
                          <NorthIndianChart horoscope={bhavaHoroscope} />
                        )
                      )}
                    </div>
                  </div>

                  {/* Summary & Destiny Card Banner beneath Charts */}
                  <div className="p-4 rounded-xl bg-white border border-[#D9DEE7] flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 shadow-2xs">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center text-[#B4872B] shrink-0">
                        <Sparkles className="w-4 h-4" />
                      </div>
                      <div>
                        <h4 className="text-xs sm:text-sm font-bold text-[#183047]">
                          {language === "ta" ? "வேத விதி அட்டை மற்றும் பரிகாரங்கள்" : "Vedic Destiny Card & Remedies"}
                        </h4>
                        <p className="text-[11px] text-[#8190A6]">
                          {language === "ta"
                            ? "லக்னம், ராசி, நட்சத்திரம் மற்றும் நடப்பு தசா அடங்கிய பகிர்வு அட்டை."
                            : "Verified astrological identity card ready to export and share."}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Link
                        href={`/remedies${result.savedId || idParam ? `?horoscope_id=${encodeURIComponent(result.savedId || idParam || "")}` : ""}`}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#D9DEE7] bg-[#F2F3F5] text-xs font-bold text-[#153F6B] hover:bg-[#E2E8F0] shadow-2xs transition-colors"
                      >
                        <ShieldCheck className="w-3.5 h-3.5 text-[#153F6B]" />
                        <span>{language === "ta" ? "பரிகாரங்கள்" : "View Remedies"}</span>
                      </Link>
                      <button
                        type="button"
                        onClick={() => setSecondaryTab("destiny-card")}
                        className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-[#B4872B] hover:bg-[#8C6D23] text-white font-bold text-xs shadow-2xs transition-colors cursor-pointer"
                      >
                        <span>{language === "ta" ? "அட்டையைக் காண்க" : "View Destiny Card"}</span>
                      </button>
                    </div>
                  </div>

                  {/* Planetary Positions Table below charts matching reference */}
                  <div className="bg-white rounded-xl border border-[#D9DEE7] p-4 sm:p-5 shadow-2xs space-y-3">
                    <h3 className="font-serif text-base font-bold text-[#183047]">
                      {t.tabPlanets}
                    </h3>
                    <PlanetaryTable
                      planets={horoscope.planets}
                      ascendant={horoscope.ascendant}
                    />
                  </div>
                </div>
              )}

              {/* Sub-Tab 2: FACTS & PANCHANG */}
              {secondaryTab === "facts" && (
                <div className="space-y-5">
                  <PanchangCard panchang={horoscope.panchang} />
                  <div className="bg-white rounded-xl border border-[#D9DEE7] p-4 sm:p-5 shadow-2xs space-y-3">
                    <h3 className="font-serif text-base font-bold text-[#183047]">
                      {t.tabHouses}
                    </h3>
                    <HousesTable houses={horoscope.houses} />
                  </div>
                </div>
              )}

              {/* Sub-Tab 3: PLANETARY POSITIONS */}
              {secondaryTab === "planets" && (
                <div className="bg-white rounded-xl border border-[#D9DEE7] p-4 sm:p-5 shadow-2xs space-y-3">
                  <h3 className="font-serif text-lg font-bold text-[#183047]">
                    {t.tabPlanets}
                  </h3>
                  <PlanetaryTable
                    planets={horoscope.planets}
                    ascendant={horoscope.ascendant}
                  />
                </div>
              )}

              {/* Sub-Tab 4: DASA-BHUKTI (Screenshot 4 Reference) */}
              {secondaryTab === "dasa" && (
                <div className="space-y-4">
                  <DasaTimeline
                    dasa={dasa}
                    horoscope={horoscope}
                    birthDate={clientInputs?.birthDate}
                    birthTime={clientInputs?.birthTime}
                    timezone={clientInputs?.timezone}
                    kp={kp}
                  />
                </div>
              )}

              {/* Sub-Tab 5: ASHTAKAVARGA */}
              {secondaryTab === "ashtakavarga" && (
                <div className="space-y-4">
                  <AshtakavargaSection
                    ashtakavarga={horoscope.ashtakavarga || result.ashtakavarga}
                    onCalculate={handleCalculateVedicExtensions}
                    isCalculating={isCalculatingExtensions}
                  />
                </div>
              )}

              {/* Sub-Tab 6: YOGAS (Vedic + Nabhasha) */}
              {secondaryTab === "yogas" && (
                <div className="space-y-5">
                  <VedicYogaSection
                    vedicYogas={horoscope.vedic_yogas || result.vedic_yogas}
                    onCalculate={handleCalculateVedicExtensions}
                    isCalculating={isCalculatingExtensions}
                  />
                  <NabhashaSection
                    nabhasha={horoscope.nabhasha_yogas || result.nabhasha}
                    onCalculate={handleCalculateVedicExtensions}
                    isCalculating={isCalculatingExtensions}
                  />
                </div>
              )}

              {/* Sub-Tab 7: DESTINY CARD */}
              {secondaryTab === "destiny-card" && (
                <div className="space-y-4">
                  <DestinyCard result={result} />
                </div>
              )}
            </div>
          )}

          {/* MAIN TAB 2: CONSULTATION */}
          {mainTab === "consultation" && (
            <div className="space-y-5">
              <div className="bg-white rounded-xl border border-[#D9DEE7] p-5 shadow-2xs space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-[#F2F3F5] pb-4">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-full bg-[#153F6B]/10 flex items-center justify-center text-[#153F6B]">
                      <FileText className="w-4 h-4" />
                    </div>
                    <div>
                      <h3 className="font-bold text-base text-[#183047]">
                        {language === "ta" ? "ஜோதிட ஆலோசனை மற்றும் குறிப்புகள்" : "Consultation Notes & Remarks"}
                      </h3>
                      <p className="text-xs text-[#8190A6]">
                        {language === "ta"
                          ? "வாடிக்கையாளருக்கான ஜாதக கணிப்பு முடிவுகள் மற்றும் ஆலோசனைக் குறிப்புகள்."
                          : "Record client consultation remarks, focus questions, and remedies."}
                      </p>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={handleSaveNotes}
                    disabled={isSavingNotes}
                    className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-[#153F6B] hover:bg-[#0F3155] text-white text-xs font-bold shadow-2xs transition-colors cursor-pointer disabled:opacity-50"
                  >
                    {isSavingNotes ? (
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <Save className="w-3.5 h-3.5" />
                    )}
                    <span>{language === "ta" ? "சேமிக்க" : "Save Notes"}</span>
                  </button>
                </div>

                {notesSaveStatus && (
                  <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold flex items-center gap-2">
                    <Check className="w-4 h-4 text-emerald-600" />
                    <span>{notesSaveStatus}</span>
                  </div>
                )}

                <div>
                  <label className="block text-xs font-bold text-[#183047] mb-1.5">
                    {language === "ta" ? "ஆலோசனை குறிப்புகள்:" : "Astrologer Consultation Notes:"}
                  </label>
                  <textarea
                    rows={6}
                    value={consultationNotes}
                    onChange={(e) => setConsultationNotes(e.target.value)}
                    placeholder={
                      language === "ta"
                        ? "வாடிக்கையாளரின் கேள்விகள், திருமணப் பொருத்தம், தொழில் வழிகாட்டல் அல்லது பரிகாரங்கள் குறித்த குறிப்புகளை இங்கே தட்டச்சு செய்யவும்..."
                        : "Type consultation notes, client queries, career or marriage guidance, and custom remedies here..."
                    }
                    className="w-full text-xs sm:text-sm p-3 rounded-lg border border-[#D9DEE7] bg-[#F2F3F5]/40 text-[#183047] focus:outline-none focus:ring-1 focus:ring-[#153F6B] focus:border-[#153F6B] transition-all"
                  />
                </div>
              </div>

              {/* Consultation Quick Links */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-white border border-[#D9DEE7] shadow-2xs space-y-2">
                  <div className="flex items-center gap-2 text-xs font-bold text-[#153F6B]">
                    <ShieldCheck className="w-4 h-4 text-[#153F6B]" />
                    <span>{language === "ta" ? "பரிகாரங்கள் மற்றும் பரிகாரத் தலங்கள்" : "Remedies & Temples"}</span>
                  </div>
                  <p className="text-xs text-[#8190A6]">
                    {language === "ta"
                      ? "நடப்பு தசா-புத்தி மற்றும் பாதக கிரகங்களுக்கான தனிப்பயனாக்கப்பட்ட பரிகாரங்கள்."
                      : "Direct prescription of astrological remedies based on running Dasa-Bhukti."}
                  </p>
                  <Link
                    href={`/remedies${result.savedId || idParam ? `?horoscope_id=${encodeURIComponent(result.savedId || idParam || "")}` : ""}`}
                    className="inline-flex items-center gap-1.5 text-xs font-bold text-[#B4872B] hover:underline pt-1"
                  >
                    <span>{language === "ta" ? "பரிகாரங்களை ஆராய்க →" : "Explore Remedies →"}</span>
                  </Link>
                </div>

                <div className="p-4 rounded-xl bg-white border border-[#D9DEE7] shadow-2xs space-y-2">
                  <div className="flex items-center gap-2 text-xs font-bold text-[#153F6B]">
                    <Compass className="w-4 h-4 text-[#B4872B]" />
                    <span>{language === "ta" ? "D1 & D9 முழு ஒப்பீட்டு ஆய்வு" : "Full D1 / D9 Varga Analysis"}</span>
                  </div>
                  <p className="text-xs text-[#8190A6]">
                    {language === "ta"
                      ? "வர்கோத்தம கிரகங்கள் மற்றும் புஷ்கர நவாம்ச நிலைகளை விரிவாகக் காண்க."
                      : "Detailed comparative dignity analysis between Rasi and Navamsa charts."}
                  </p>
                  <Link
                    href={idParam ? `/tools/d1-d9?saved_id=${idParam}` : "/tools/d1-d9"}
                    className="inline-flex items-center gap-1.5 text-xs font-bold text-[#B4872B] hover:underline pt-1"
                  >
                    <span>{language === "ta" ? "வர்க்க ஆய்வுக்குச் செல்க →" : "Open Varga Analysis →"}</span>
                  </Link>
                </div>
              </div>
            </div>
          )}

          {/* MAIN TAB 3: REPORTS & DOWNLOADS */}
          {mainTab === "reports" && (
            <div className="space-y-5">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* 1. Print / PDF */}
                <div className="bg-white rounded-xl border border-[#D9DEE7] p-5 shadow-2xs space-y-3 flex flex-col justify-between">
                  <div className="space-y-2">
                    <div className="w-10 h-10 rounded-lg bg-[#153F6B]/10 flex items-center justify-center text-[#153F6B]">
                      <Printer className="w-5 h-5" />
                    </div>
                    <h3 className="font-bold text-sm text-[#183047]">
                      {language === "ta" ? "ஜாதக அச்சு மற்றும் PDF" : "Print & PDF Export"}
                    </h3>
                    <p className="text-xs text-[#8190A6]">
                      {language === "ta"
                        ? "முழு ஜாதகம், கட்டங்கள் மற்றும் தசா அட்டவணைகளை அச்சிட அல்லது PDF ஆக சேமிக்க."
                        : "Print full chart and Dasa tables or save directly as PDF."}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => window.print()}
                    className="w-full inline-flex items-center justify-center gap-1.5 px-4 py-2 rounded-lg bg-[#153F6B] hover:bg-[#0F3155] text-white text-xs font-bold shadow-2xs transition-colors cursor-pointer"
                  >
                    <Printer className="w-3.5 h-3.5" />
                    <span>{language === "ta" ? "அச்சிடுக / PDF" : "Print / PDF"}</span>
                  </button>
                </div>

                {/* 2. Destiny Card */}
                <div className="bg-white rounded-xl border border-[#D9DEE7] p-5 shadow-2xs space-y-3 flex flex-col justify-between">
                  <div className="space-y-2">
                    <div className="w-10 h-10 rounded-lg bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center text-[#B4872B]">
                      <Sparkles className="w-5 h-5" />
                    </div>
                    <h3 className="font-bold text-sm text-[#183047]">
                      {language === "ta" ? "வேத விதி அட்டை" : "Vedic Destiny Card"}
                    </h3>
                    <p className="text-xs text-[#8190A6]">
                      {language === "ta"
                        ? "லக்னம், ராசி மற்றும் நடப்பு தசா அடங்கிய பகிர்வு அட்டை."
                        : "High-resolution mobile-friendly astrological summary card."}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      setMainTab("horoscope");
                      setSecondaryTab("destiny-card");
                    }}
                    className="w-full inline-flex items-center justify-center gap-1.5 px-4 py-2 rounded-lg bg-[#B4872B] hover:bg-[#8C6D23] text-white text-xs font-bold shadow-2xs transition-colors cursor-pointer"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>{language === "ta" ? "அட்டையைப் பதிவிறக்கு" : "View & Download Card"}</span>
                  </button>
                </div>

                {/* 3. CSV Planetary Positions */}
                <div className="bg-white rounded-xl border border-[#D9DEE7] p-5 shadow-2xs space-y-3 flex flex-col justify-between">
                  <div className="space-y-2">
                    <div className="w-10 h-10 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-700">
                      <Download className="w-5 h-5" />
                    </div>
                    <h3 className="font-bold text-sm text-[#183047]">
                      {language === "ta" ? "கிரக நிலைகள் தரவு (CSV)" : "Planetary Data (CSV)"}
                    </h3>
                    <p className="text-xs text-[#8190A6]">
                      {language === "ta"
                        ? "அனைத்து 9 கிரகங்களின் பாகைகள் மற்றும் நட்சத்திரத் தரவுகளை எக்செல் கோப்பாகப் பதிவிறக்க."
                        : "Export raw planetary longitudes, speeds, and nakshatras."}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      if (!horoscope?.planets) return;
                      const headers = "Planet,Sign,Degree,Speed,Retrograde,Nakshatra,Pada,House\n";
                      const rows = horoscope.planets
                        .map((p) => {
                          const houseNum =
                            p.house ??
                            (((p.sign_index - horoscope.ascendant.sign_index + 12) % 12) + 1);
                          return `"${p.name}","${p.sign_name}",${p.degree_in_sign.toFixed(4)},${p.speed_deg_per_day.toFixed(4)},${p.is_retrograde ? "Yes" : "No"},"${p.nakshatra?.name || ""}",${p.nakshatra?.pada || 1},${houseNum}`;
                        })
                        .join("\n");
                      const blob = new Blob([headers + rows], { type: "text/csv;charset=utf-8;" });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = `${(clientInputs.fullName || "horoscope").replace(/\s+/g, "_")}_planets.csv`;
                      a.click();
                      URL.revokeObjectURL(url);
                    }}
                    className="w-full inline-flex items-center justify-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-2xs transition-colors cursor-pointer"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>{language === "ta" ? "CSV பதிவிறக்கம்" : "Export CSV"}</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 6. Notes Modal */}
      {showNotesModal && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl space-y-4 border border-[#D9DEE7]">
            <div className="flex items-center justify-between pb-3 border-b border-[#F2F3F5]">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-[#B4872B]" />
                <h3 className="font-bold text-base text-[#183047]">
                  {language === "ta" ? "ஜாதகக் குறிப்புகள்" : "Horoscope Notes"}
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setShowNotesModal(false)}
                className="p-1 rounded-lg text-[#8190A6] hover:bg-[#F2F3F5] hover:text-[#183047] transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {notesSaveStatus && (
              <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold flex items-center gap-2">
                <Check className="w-4 h-4 text-emerald-600" />
                <span>{notesSaveStatus}</span>
              </div>
            )}

            <div>
              <p className="text-xs text-[#8190A6] mb-2">
                {language === "ta"
                  ? `${clientInputs.fullName || "இந்த ஜாதகம்"} தொடர்பான முக்கிய குறிப்புகளைப் பதிவு செய்யவும்.`
                  : `Add consultation or analytical notes for ${clientInputs.fullName || "this client"}.`}
              </p>
              <textarea
                rows={6}
                value={consultationNotes}
                onChange={(e) => setConsultationNotes(e.target.value)}
                placeholder={
                  language === "ta"
                    ? "ஆலோசனை விவரங்கள், பரிகாரங்கள் அல்லது எதிர்கால பலன்கள் குறித்த குறிப்புகள்..."
                    : "Consultation findings, client questions, or suggested remedies..."
                }
                className="w-full text-xs sm:text-sm p-3 rounded-lg border border-[#D9DEE7] bg-[#F2F3F5]/30 text-[#183047] focus:outline-none focus:ring-1 focus:ring-[#153F6B]"
              />
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-[#F2F3F5]">
              <button
                type="button"
                onClick={() => setShowNotesModal(false)}
                className="px-4 py-2 rounded-lg border border-[#D9DEE7] text-xs font-semibold text-[#52667E] hover:bg-[#F2F3F5] cursor-pointer"
              >
                {language === "ta" ? "மூடுக" : "Close"}
              </button>
              <button
                type="button"
                onClick={handleSaveNotes}
                disabled={isSavingNotes}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-[#153F6B] hover:bg-[#0F3155] text-white text-xs font-bold cursor-pointer disabled:opacity-50"
              >
                {isSavingNotes ? (
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Save className="w-3.5 h-3.5" />
                )}
                <span>{language === "ta" ? "சேமிக்க" : "Save"}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function HoroscopeResultsPage() {
  return (
    <Suspense
      fallback={
        <div className="max-w-5xl mx-auto px-4 py-20 text-center">
          <div className="inline-block animate-spin w-8 h-8 border-4 border-[#153F6B] border-t-transparent rounded-full mb-4" />
          <p className="text-sm text-[#8190A6]">Loading horoscope...</p>
        </div>
      }
    >
      <HoroscopeResultsContent />
    </Suspense>
  );
}
