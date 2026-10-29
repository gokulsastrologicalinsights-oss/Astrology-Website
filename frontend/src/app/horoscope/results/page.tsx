"use client";

import React, { useState, useEffect, useMemo, useRef, useCallback, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { getActiveCalculation, saveActiveCalculation } from "@/lib/storage";
import { FullHoroscopeResult, HoroscopeResponse, LiveTransitsResponse } from "@/lib/types";
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
import { HoroscopeFactsPanel, FactCategory } from "@/components/results/HoroscopeFactsPanel";
import { VedicYogaSection } from "@/components/results/VedicYogaSection";
import { MedicalAstrologySection } from "@/components/results/MedicalAstrologySection";
import { DoshaSection } from "@/components/results/DoshaSection";
import { NabhashaSection } from "@/components/results/NabhashaSection";
import { AshtakavargaSection } from "@/components/results/AshtakavargaSection";
import { AstrologicalPredictionsSection } from "@/components/results/AstrologicalPredictionsSection";
import { DasaBukthiPalangalSection } from "@/components/results/DasaBukthiPalangalSection";
import { GkTransitMatchingCard } from "@/components/results/GkTransitMatchingCard";
import { Recent15DayPastEventsCard } from "@/components/results/Recent15DayPastEventsCard";
import { MarcBoneyMilestonesCard } from "@/components/results/MarcBoneyMilestonesCard";
import { GemstoneDownload } from "@/components/results/GemstoneDownload";
import {
  calculateNabhasha,
  calculateAshtakavarga,
  calculateVedicYogas,
  calculateVargaD1D9,
  calculateShodashvarga,
  calculateDoshas,
  calculateShadbala,
  calculateMedicalAstrology,
  getLiveTransits,
} from "@/lib/api";
import { buildPlanetContexts, enrichDasaTreeWithBenefitBhavas } from "@/lib/benefit-bhavas";
import { buildNavamsaHoroscope } from "@/lib/chart-transforms";
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
  Radio,
  Gem,
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

  // Secondary Tabs under Horoscope: "chart" | "facts" | "planets" | "dasa" | "dasa-palangal" | "transits" | "milestones" | "ashtakavarga" | "yogas" | "medical" | "doshas" | "gemstone-download"
  const [secondaryTab, setSecondaryTab] = useState<
    "chart" | "facts" | "planets" | "dasa" | "dasa-palangal" | "transits" | "milestones" | "ashtakavarga" | "yogas" | "medical" | "doshas" | "gemstone-download"
  >(() => {
    const validSecondary = ["chart", "facts", "planets", "dasa", "dasa-palangal", "transits", "milestones", "ashtakavarga", "yogas", "medical", "doshas", "gemstone-download"];
    if (tabParam && (validSecondary.includes(tabParam) || ["dasa_palangal", "palangal", "dasa-bukthi-palangal"].includes(tabParam))) {
      return (tabParam === "dasa_palangal" || tabParam === "palangal" || tabParam === "dasa-bukthi-palangal") ? "dasa-palangal" : (tabParam as any);
    }
    if (tabParam && ["transits", "transit", "gochara", "gocharam", "gk-transits"].includes(tabParam)) {
      return "transits";
    }
    if (tabParam && ["milestones", "life-milestones", "marc-boney", "events"].includes(tabParam)) {
      return "milestones";
    }
    if (tabParam && ["gemstone", "gemstones", "gemstone-download", "gemstonedownload", "ratna"].includes(tabParam.toLowerCase())) {
      return "gemstone-download";
    }
    if (tabParam && ["d1-d9", "varga", "vargas", "shodashvarga"].includes(tabParam)) {
      return "divisional";
    }
    if (searchParams.get("category")) {
      return "facts";
    }
    if (tabParam === "kp") {
      return "chart";
    }
    return "chart";
  });

  // Chart Style Switcher: South Indian vs North Indian
  const [chartMode, setChartMode] = useState<"south" | "north">("south");

  // Live Transits state
  const [showTransits, setShowTransits] = useState<boolean>(false);
  const [liveTransitsData, setLiveTransitsData] = useState<LiveTransitsResponse | null>(null);
  const [isLoadingTransits, setIsLoadingTransits] = useState<boolean>(false);
  const [transitsError, setTransitsError] = useState<string | null>(null);
  const [transitsDevError, setTransitsDevError] = useState<string | null>(null);
  const [showTransitTable, setShowTransitTable] = useState<boolean>(false);

  // Live transits fetcher
  const fetchLiveTransits = useCallback(async () => {
    setIsLoadingTransits(true);
    setTransitsError(null);
    setTransitsDevError(null);
    try {
      const tz = result?.clientInputs?.timezone || result?.horoscope?.metadata?.local_timezone || "Asia/Kolkata";
      const lat = result?.clientInputs?.latitude ?? result?.horoscope?.metadata?.coordinates?.latitude ?? 13.0827;
      const lon = result?.clientInputs?.longitude ?? result?.horoscope?.metadata?.coordinates?.longitude ?? 80.2707;
      const aya = result?.clientInputs?.ayanamsaId ?? result?.horoscope?.metadata?.ayanamsa_id ?? 0;
      const res = await getLiveTransits({
        timezone: tz,
        latitude: lat,
        longitude: lon,
        ayanamsa: aya,
      });
      setLiveTransitsData(res);
    } catch (err: unknown) {
      console.error("[Live Transits Error]", err);
      const errMsg = err instanceof Error ? err.message : String(err);
      const errStatus = (err as any)?.statusCode ? ` (HTTP ${(err as any).statusCode})` : "";
      const errDetail = (err as any)?.data?.detail || errMsg;
      setTransitsError(
        language === "ta"
          ? "கோசார கணக்கீடு தற்போது கிடைக்கவில்லை. தயவுசெய்து மீண்டும் முயற்சிக்கவும்."
          : "Live ephemeris transit calculation is currently unavailable. Please check your connection and retry."
      );
      setTransitsDevError(`${errDetail}${errStatus}`);
    } finally {
      setIsLoadingTransits(false);
    }
  }, [result?.clientInputs, result?.horoscope?.metadata, language]);


  const handleToggleTransits = () => {
    const nextState = !showTransits;
    setShowTransits(nextState);
    if (nextState && !liveTransitsData && !isLoadingTransits) {
      fetchLiveTransits();
    }
  };

  // Auto-fetch live ephemeris transits when navigating to Ashtakavarga, Transits, Dasa-Palangal, or Milestones tab
  useEffect(() => {
    if (
      (secondaryTab === "ashtakavarga" || secondaryTab === "transits" || secondaryTab === "dasa-palangal" || secondaryTab === "milestones") &&
      !liveTransitsData &&
      !isLoadingTransits
    ) {
      fetchLiveTransits();
    }
  }, [secondaryTab, liveTransitsData, isLoadingTransits, fetchLiveTransits]);


  // Notes Modal state
  const [showNotesModal, setShowNotesModal] = useState<boolean>(false);
  const [consultationNotes, setConsultationNotes] = useState<string>("");
  const [isSavingNotes, setIsSavingNotes] = useState<boolean>(false);
  const [notesSaveStatus, setNotesSaveStatus] = useState<string | null>(null);

  // Load existing notes from local storage on mount / id change
  useEffect(() => {
    const noteKey = `horoscope_notes_${idParam || result?.savedId || "active"}`;
    const stored = localStorage.getItem(noteKey);
    setConsultationNotes(stored || "");
  }, [idParam, result?.savedId]);

  // Ensure live transits state is clean on horoscope change
  useEffect(() => {
    setShowTransits(false);
    setLiveTransitsData(null);
    setShowTransitTable(false);
  }, [idParam, result?.savedId]);

  // Handle URL hash or tab parameters
  useEffect(() => {
    if (tabParam === "kp" || (typeof window !== "undefined" && window.location.hash === "#kp-events")) {
      setSystemMode("kp");
    } else if (tabParam === "consultation") {
      setMainTab("consultation");
    } else if (tabParam === "reports") {
      setMainTab("reports");
    } else if (tabParam && ["dasa-palangal", "dasa_palangal", "palangal", "dasa-bukthi-palangal"].includes(tabParam)) {
      setMainTab("horoscope");
      setSecondaryTab("dasa-palangal");
    } else if (tabParam && ["transits", "transit", "gochara", "gocharam", "gk-transits"].includes(tabParam)) {
      setMainTab("horoscope");
      setSecondaryTab("transits");
    } else if (tabParam && ["milestones", "life-milestones", "marc-boney", "events"].includes(tabParam)) {
      setMainTab("horoscope");
      setSecondaryTab("milestones");
    } else if (tabParam && ["chart", "facts", "planets", "dasa", "ashtakavarga", "yogas", "doshas", "milestones", "gemstone-download"].includes(tabParam)) {
      setMainTab("horoscope");
      setSecondaryTab(tabParam as any);
    } else if (tabParam && ["gemstone", "gemstones", "gemstonedownload", "ratna"].includes(tabParam.toLowerCase())) {
      setMainTab("horoscope");
      setSecondaryTab("gemstone-download");
    }
  }, [tabParam]);

  const [isCalculatingExtensions, setIsCalculatingExtensions] = useState(false);
  const [isCalculatingLegacyDoshas, setIsCalculatingLegacyDoshas] = useState(false);
  const calculatedLegacyDoshasRef = useRef<Set<string>>(new Set());

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

      const [nabhashaRes, ashtakavargaRes, vedicYogaRes, vargaRes, shodashvargaRes, doshasRes, shadbalaRes, medicalRes] = await Promise.all([
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
        calculateShodashvarga(birthInput).catch((e) => {
          console.warn("Shodashvarga calculation failed:", e);
          return null;
        }),
        calculateDoshas(birthInput).catch((e) => {
          console.warn("Dosha calculation failed:", e);
          return null;
        }),
        calculateShadbala(birthInput).catch((e) => {
          console.warn("Shadbala calculation failed:", e);
          return null;
        }),
        calculateMedicalAstrology(birthInput).catch((e) => {
          console.warn("Medical astrology calculation failed:", e);
          return null;
        }),
      ]);

      const updatedHoroscope = {
        ...result.horoscope,
        nabhasha_yogas: nabhashaRes || result.horoscope.nabhasha_yogas,
        ashtakavarga: ashtakavargaRes || result.horoscope.ashtakavarga,
        vedic_yogas: vedicYogaRes || result.horoscope.vedic_yogas,
        varga_d1_d9: vargaRes || result.horoscope.varga_d1_d9,
        shodashvarga: shodashvargaRes || (result.horoscope as any).shodashvarga,
        doshas: doshasRes || result.horoscope.doshas,
        shadbala: shadbalaRes || (result.horoscope as any).shadbala,
        medical_astrology: medicalRes || result.horoscope.medical_astrology,
      };

      const updatedResult: FullHoroscopeResult = {
        ...result,
        horoscope: updatedHoroscope,
        nabhasha: nabhashaRes || result.nabhasha,
        ashtakavarga: ashtakavargaRes || result.ashtakavarga,
        vedic_yogas: vedicYogaRes || result.vedic_yogas,
        doshas: doshasRes || (result as any).doshas,
        shadbala: shadbalaRes || result.shadbala,
        medical_astrology: medicalRes || result.medical_astrology,
        ...(shodashvargaRes ? { shodashvarga: shodashvargaRes } : {}),
      };

      setResult(updatedResult);
      saveActiveCalculation(updatedResult);

      // Fix 3: Persist newly calculated extensions to database if this horoscope is saved
      const targetSavedId = result.savedId || idParam;
      if (targetSavedId) {
        const idempotencyKey =
          result.idempotencyKey ||
          (result as any).calculation_result?.idempotency_key ||
          `calc_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
        const snapshot = prepareCalculationSnapshot(updatedResult, idempotencyKey);

        fetch(`/api/horoscopes/${targetSavedId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ calculation_result: snapshot }),
        }).catch((persistErr) => {
          console.warn("Failed to persist updated calculation snapshot to database:", persistErr);
        });
      }
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
      fetch(`/api/horoscopes/${idParam}`, { cache: "no-store" })
        .then(async (res) => {
          if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.error || "Failed to load saved horoscope.");
          }
          return res.json();
        })
        .then((data) => {
          const item = data.horoscope;
          const calc = item.calculation_result || {};
          const calcTime = calc.calculatedAt
            ? new Date(calc.calculatedAt).getTime()
            : 0;
          const updateTime = item.updated_at
            ? new Date(item.updated_at).getTime()
            : 0;
          const createTime = item.created_at
            ? new Date(item.created_at).getTime()
            : 0;
          // Only flag as "edited without recalc" if metadata was modified without updating the calculation snapshot
          const isEdited =
            updateTime > createTime + 3000 &&
            (!calcTime || updateTime - calcTime > 10000);

          // Auto-heal dasa tree to ensure accurate canonical Vedic house occupancies
          if (calc.horoscope?.planets && calc.horoscope?.ascendant && calc.dasa?.dasa_tree) {
            try {
              const contexts = buildPlanetContexts(calc.horoscope.planets, calc.horoscope.ascendant, calc.horoscope.houses);
              enrichDasaTreeWithBenefitBhavas(calc.dasa.dasa_tree, contexts);
            } catch (healErr) {
              console.warn("Could not auto-heal dasa tree for saved record:", healErr);
            }
          }

          const existingDoshas = calc.horoscope?.doshas || calc.doshas;
          const unpackedResult: FullHoroscopeResult = {
            horoscope: {
              ...calc.horoscope,
              doshas: existingDoshas,
            },
            dasa: calc.dasa,
            kp: calc.kp,
            nabhasha: calc.horoscope?.nabhasha_yogas || calc.nabhasha,
            ashtakavarga: calc.horoscope?.ashtakavarga || calc.ashtakavarga,
            vedic_yogas: calc.horoscope?.vedic_yogas || calc.vedic_yogas,
            doshas: existingDoshas,
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

          // Fix 2: If doshas is missing from legacy saved snapshot, auto-calculate in background once
          if (!existingDoshas && item.id && !calculatedLegacyDoshasRef.current.has(item.id)) {
            calculatedLegacyDoshasRef.current.add(item.id);
            setIsCalculatingLegacyDoshas(true);
            calculateDoshas({
              birth_date: item.birth_date,
              birth_time: item.birth_time,
              timezone: item.timezone,
              latitude: item.latitude,
              longitude: item.longitude,
              ayanamsa: item.ayanamsa_id,
              house_system: item.house_system_id,
            })
              .then((doshaRes) => {
                setResult((prev) => {
                  if (!prev) return null;
                  const updated: FullHoroscopeResult = {
                    ...prev,
                    doshas: doshaRes,
                    horoscope: {
                      ...prev.horoscope,
                      doshas: doshaRes,
                    },
                  };
                  saveActiveCalculation(updated);

                  // Persist to database so subsequent reloads restore immediately
                  const idempotencyKey =
                    updated.idempotencyKey ||
                    (updated as any).calculation_result?.idempotency_key ||
                    `calc_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
                  const snapshot = prepareCalculationSnapshot(updated, idempotencyKey);
                  fetch(`/api/horoscopes/${item.id}`, {
                    method: "PATCH",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ calculation_result: snapshot }),
                  }).catch((err) => {
                    console.warn("Failed to persist auto-calculated doshas to database:", err);
                  });

                  return updated;
                });
              })
              .catch((e) => {
                console.warn("Auto-calculation of Vedic Doshas failed:", e);
              })
              .finally(() => {
                setIsCalculatingLegacyDoshas(false);
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
          customer_full_name: result.clientInputs.fullName?.trim() || "Unnamed Horoscope",
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

      if (typeof window !== "undefined" && data.horoscope?.id) {
        window.history.replaceState(null, "", `/horoscope/results?id=${data.horoscope.id}`);
      }
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

  // Auto-attempt background save if loaded active calculation is not yet saved to account
  const autoSaveAttemptedRef = useRef(false);
  useEffect(() => {
    if (!idParam && result && !result.isSaved && !result.savedId && !autoSaveAttemptedRef.current) {
      autoSaveAttemptedRef.current = true;
      handleRetrySave();
    }
  }, [idParam, result?.isSaved, result?.savedId]);

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

  // Derive Navamsa D9 horoscope
  const d9Horoscope = useMemo(() => {
    if (!result?.horoscope) return null;
    return buildNavamsaHoroscope(result.horoscope);
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
    <div className="w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 md:py-8 space-y-5">
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
              {result.saveError && result.saveError !== "Failed to save horoscope." && (
                <p className="text-[10px] text-amber-900/80 font-mono mt-1">
                  {result.saveError}
                </p>
              )}
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
              {/* Recent 15-Day Past Events Flashback & Client Verification */}
              <Recent15DayPastEventsCard
                horoscope={horoscope}
                dasa={dasa}
                liveTransits={liveTransitsData}
              />

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
                  onClick={() => setSecondaryTab("dasa-palangal")}
                  className={`pb-2 px-3 transition-all cursor-pointer whitespace-nowrap inline-flex items-center gap-1.5 ${
                    secondaryTab === "dasa-palangal"
                      ? "border-b-2 border-[#B4872B] text-[#153F6B] font-bold bg-[#FAF2DE]/40"
                      : "text-[#B4872B] hover:text-[#8C6D23] font-semibold"
                  }`}
                  title={language === "ta" ? "விம்சோத்தரி தசா புத்தி பலன்கள் (கிருஷன் காந்த் பரத்வாஜ் முறை)" : "Vimshottari Dasa Bukthi Palangal"}
                >
                  <Sparkles className="w-3.5 h-3.5 text-[#B4872B]" />
                  <span>{language === "ta" ? "தசா புத்தி பலன்கள்" : "Dasa Bukthi Palangal"}</span>
                </button>

                <button
                  type="button"
                  onClick={() => setSecondaryTab("transits")}
                  className={`pb-2 px-3 transition-all cursor-pointer whitespace-nowrap inline-flex items-center gap-1.5 ${
                    secondaryTab === "transits"
                      ? "border-b-2 border-[#B4872B] text-[#153F6B] font-bold bg-[#FAF2DE]/40"
                      : "text-[#52667E] hover:text-[#183047]"
                  }`}
                  title={
                    language === "ta"
                      ? "திருப்பூர் ஸ்ரீ எஸ். கோபாலகிருஷ்ணன் (ஜிகே) சந்திர நாடி துல்லிய கோச்சார பலன்கள்"
                      : "Tirupur S. Gopalakrishnan Accurate Transit Predictions"
                  }
                >
                  <Compass className="w-3.5 h-3.5 text-[#B4872B]" />
                  <span>{language === "ta" ? "கோச்சார பலன்கள் (GK Transits)" : "GK Transit Predictions"}</span>
                </button>

                <button
                  type="button"
                  onClick={() => setSecondaryTab("milestones")}
                  className={`pb-2 px-3 transition-all cursor-pointer whitespace-nowrap inline-flex items-center gap-1.5 ${
                    secondaryTab === "milestones"
                      ? "border-b-2 border-indigo-600 text-indigo-700 font-bold bg-indigo-50/50"
                      : "text-indigo-600 hover:text-indigo-800 font-semibold"
                  }`}
                  title={
                    language === "ta"
                      ? "மார்க் போனி & கே.என். ராவ்: 8 முக்கிய வாழ்க்கை நிகழ்வுகள் கணிப்பு"
                      : "Marc Boney & K.N. Rao Major Life Milestones Predictor"
                  }
                >
                  <Award className="w-3.5 h-3.5 text-indigo-600" />
                  <span>{language === "ta" ? "வாழ்க்கை மைல்கற்கள் (Marc Boney)" : "Life Milestones (Marc Boney)"}</span>
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
                  {language === "ta" ? "அஷ்டகவர்க பரல்கள்" : "Ashtakavarga"}
                </button>

                <button
                  type="button"
                  onClick={() => setSecondaryTab("medical")}
                  className={`pb-2 px-3 transition-all cursor-pointer whitespace-nowrap ${secondaryTab === "medical" ? "border-b-2 border-[#B4872B] text-[#153F6B] font-bold" : "text-[#52667E] hover:text-[#183047]"}`}
                >
                  {t.tabMedicalAstrology}
                </button>

                <button
                  type="button"
                  onClick={() => setSecondaryTab("yogas")}
                  className={`pb-2 px-3 transition-all cursor-pointer whitespace-nowrap ${secondaryTab === "yogas" ? "border-b-2 border-[#B4872B] text-[#153F6B] font-bold" : "text-[#52667E] hover:text-[#183047]"}`}
                >
                  {language === "ta" ? "யோகங்கள்" : "Yogas"}
                </button>

                <button
                  type="button"
                  onClick={() => setSecondaryTab("doshas")}
                  className={`pb-2 px-3 transition-all cursor-pointer whitespace-nowrap ${
                    secondaryTab === "doshas"
                      ? "border-b-2 border-[#B4872B] text-[#153F6B] font-bold"
                      : "text-[#52667E] hover:text-[#183047]"
                  }`}
                >
                  {language === "ta" ? "தோஷங்கள்" : "Doshas"}
                </button>

                <button
                  type="button"
                  onClick={() => setSecondaryTab("gemstone-download")}
                  className={`pb-2 px-3 transition-all cursor-pointer whitespace-nowrap inline-flex items-center gap-1.5 ${
                    secondaryTab === "gemstone-download"
                      ? "border-b-2 border-[#B4872B] text-[#153F6B] font-bold bg-[#FAF2DE]/50"
                      : "text-amber-800 hover:text-amber-950 font-semibold"
                  }`}
                  title={
                    language === "ta"
                      ? "ரத்ன சமாதானம்: ஜோதிட ரத்தின வழிகாட்டி & புனிதக் கையேடு பதிவிறக்கம் (GemstoneDownload)"
                      : "GemstoneDownload: Astrological Gem Solutions (Ratna Samadhan) & PDF Playbook Download"
                  }
                >
                  <Gem className="w-3.5 h-3.5 text-[#B4872B]" />
                  <span>{language === "ta" ? "ரத்தின வழிகாட்டி (GemstoneDownload)" : "GemstoneDownload"}</span>
                </button>
              </div>

              {/* Sub-Tab 1: CHARTS - 2 Classical Charts (Rasi D1 & Navamsa D9) with Live Planetary Transits */}
              {secondaryTab === "chart" && (
                <div className="max-w-7xl mx-auto w-full space-y-6">
                  {/* Style Switcher Bar & Live Transit Toggle */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="text-xs text-[#8190A6]">
                      {language === "ta"
                        ? "பாரம்பரிய முறைப்படி ராசி (D1) மற்றும் நவாம்ச (D9) கட்டங்கள்."
                        : "Classical charts: Rasi (D1) and Navamsa (D9)."}
                    </div>

                    <div className="flex items-center gap-2 flex-wrap">
                      {/* Show Live Transits Toggle Button */}
                      <button
                        type="button"
                        onClick={handleToggleTransits}
                        className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                          showTransits
                            ? "bg-[#FAF2DE] text-[#8C6D23] border border-[#B8862B] shadow-2xs"
                            : "bg-white text-[#52667E] border border-[#D9DEE7] hover:bg-[#F8FAFC]"
                        }`}
                        title={
                          showTransits
                            ? (language === "ta" ? "கோசார மேலடுக்கை மறை" : "Hide live transit overlay")
                            : (language === "ta" ? "நேரலை கோசார கிரகங்களை காட்டு" : "Show live planetary transits around Rasi chart")
                        }
                      >
                        <Radio className={`w-3.5 h-3.5 ${showTransits ? "text-[#B8862B] animate-pulse" : "text-[#8190A6]"}`} />
                        <span>{language === "ta" ? "நேரலை கோசாரம்" : "Show Live Transits"}</span>
                      </button>

                      {/* South vs North Indian Chart Selector */}
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
                  </div>

                  {/* 2 Charts Responsive Grid: Equal / Balanced Widths on Desktop, Stacked on Mobile */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
                    {/* Chart 1: Rasi (D1) – Physical & General (with Live Transits Overlay) */}
                    <div className="bg-white rounded-xl border border-[#D9DEE7] p-3.5 sm:p-5 shadow-2xs flex flex-col items-center w-full">
                      <div className="w-full text-center pb-2 mb-2 border-b border-[#F2F3F5] flex items-center justify-between gap-2">
                        <span className="text-[11px] font-mono text-[#8190A6] hidden sm:inline">D1</span>
                        <h3 className="font-bold text-xs sm:text-sm text-[#183047] flex-1 text-center">
                          {language === "ta"
                            ? "ராசி (D1) - உடல் மற்றும் பொதுவானவை"
                            : "Rasi (D1) - Physical & General"}
                        </h3>
                        <span className="text-[11px] font-mono text-[#8C6D23] font-semibold hidden sm:inline">
                          {horoscope.metadata?.ayanamsa_name || "Lahiri"}
                        </span>
                      </div>

                      {/* Live Transits Status Banner & Controls */}
                      {showTransits && (
                        <div className="w-full mb-3 space-y-2">
                          <div className="w-full bg-[#FAF8F2] border border-[#D8BD80]/60 rounded-lg p-2.5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 text-xs">
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                              <span className="font-semibold text-[#8C6D23]">
                                {language === "ta" ? "நேரலை கோசாரம்" : "Live Transits"}
                              </span>
                              {liveTransitsData && (
                                <span className="text-[#8190A6] text-[11px] font-mono">
                                  {new Date(liveTransitsData.calculated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })} ({liveTransitsData.timezone})
                                </span>
                              )}
                            </div>

                            <div className="flex items-center gap-2 self-end sm:self-auto">
                              <button
                                type="button"
                                onClick={fetchLiveTransits}
                                disabled={isLoadingTransits}
                                title={language === "ta" ? "கோசார நிலைகளை புதுப்பி" : "Recalculate live transits"}
                                className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-white border border-[#D8BD80] text-[11px] font-bold text-[#8C6D23] hover:bg-[#FAF2DE] disabled:opacity-50 transition-colors cursor-pointer shadow-2xs"
                              >
                                <RefreshCw className={`w-3 h-3 ${isLoadingTransits ? "animate-spin text-[#B8862B]" : ""}`} />
                                <span>{language === "ta" ? "புதுப்பி" : "Refresh"}</span>
                              </button>

                              <button
                                type="button"
                                onClick={() => setShowTransitTable((p) => !p)}
                                className="inline-flex items-center gap-1 px-2 py-1 rounded bg-white border border-[#D9DEE7] text-[11px] font-medium text-[#52667E] hover:bg-[#F8FAFC] transition-colors cursor-pointer"
                              >
                                <span>{showTransitTable ? (language === "ta" ? "அட்டவணை மறை" : "Hide Details") : (language === "ta" ? "அட்டவணை" : "Details")}</span>
                              </button>
                            </div>
                          </div>

                          {/* Graceful Error State with Diagnostics */}
                          {transitsError && (
                            <div className="w-full p-2.5 rounded-lg border border-rose-300 bg-rose-50 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-rose-800">
                              <div className="flex items-start sm:items-center gap-2">
                                <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5 sm:mt-0" />
                                <div>
                                  <span>{transitsError}</span>
                                  {process.env.NODE_ENV !== "production" && transitsDevError && (
                                    <span className="block text-[10px] text-rose-600 font-mono mt-0.5">
                                      Debug: {transitsDevError}
                                    </span>
                                  )}
                                </div>
                              </div>
                              <button
                                type="button"
                                onClick={fetchLiveTransits}
                                disabled={isLoadingTransits}
                                className="self-end sm:self-auto px-2.5 py-1 bg-rose-700 text-white font-bold rounded text-[11px] hover:bg-rose-800 transition-colors cursor-pointer"
                              >
                                {language === "ta" ? "மீண்டும் முயற்சி" : "Retry"}
                              </button>
                            </div>
                          )}

                          {/* Legend distinguishing Natal vs Live Transit planets */}
                          <div className="w-full flex items-center justify-center gap-4 py-1.5 px-2 rounded bg-[#F8FAFC] border border-[#E2E8F0] text-[11px]">
                            <div className="flex items-center gap-1.5">
                              <span className="w-2.5 h-2.5 rounded-full bg-[#153F6B]" />
                              <span className="font-semibold text-[#183047]">
                                {language === "ta" ? "பிறப்பு நிலைகள் (மையம்)" : "Natal Planets (Center)"}
                              </span>
                            </div>
                            <div className="flex items-center gap-1.5">
                              <span className="w-2.5 h-2.5 rounded-full bg-[#B8862B]" />
                              <span className="font-bold text-[#8C6D23] font-mono">
                                {language === "ta" ? "கோசாரம் TR (வெளிச்சுற்று)" : "Live Transits TR (Perimeter)"}
                              </span>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Rasi Chart Visualization */}
                      {chartMode === "south" ? (
                        <SouthIndianChart
                          horoscope={horoscope}
                          centerLabel={language === "ta" ? "ராசி" : "Rasi"}
                          centerNumber="(1)"
                          transitPlanets={liveTransitsData?.planets}
                          showTransits={showTransits}
                          isSaved={Boolean(idParam || result?.savedId || result?.isSaved)}
                        />
                      ) : (
                        <NorthIndianChart
                          horoscope={horoscope}
                          transitPlanets={liveTransitsData?.planets}
                          showTransits={showTransits}
                          isSaved={Boolean(idParam || result?.savedId || result?.isSaved)}
                        />
                      )}

                      {/* Compact Transit Table for Details */}
                      {showTransits && showTransitTable && liveTransitsData && (
                        <div className="w-full mt-4 pt-3 border-t border-[#F2F3F5] space-y-2">
                          <h4 className="text-xs font-bold text-[#183047]">
                            {language === "ta" ? "கோசார கிரக நிலைகள் அட்டவணை" : "Live Planetary Transits Breakdown"}
                          </h4>
                          <div className="overflow-x-auto rounded border border-[#E2E8F0]">
                            <table className="w-full text-[11px] text-left">
                              <thead className="bg-[#FAF8F2] text-[#8C6D23] font-semibold border-b border-[#E2E8F0]">
                                <tr>
                                  <th className="p-1.5">{language === "ta" ? "கிரகம்" : "Planet"}</th>
                                  <th className="p-1.5">{language === "ta" ? "ராசி" : "Sign"}</th>
                                  <th className="p-1.5 font-mono">{language === "ta" ? "பாகை" : "Degree"}</th>
                                  <th className="p-1.5">{language === "ta" ? "லக்னத்திலிருந்து" : "From Lagna"}</th>
                                  <th className="p-1.5">{language === "ta" ? "நட்சத்திரம்" : "Star"}</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-[#F2F3F5]">
                                {liveTransitsData.planets.slice(0, 9).map((tp) => {
                                  const houseFromLagna =
                                    ((tp.sign_index - horoscope.ascendant.sign_index + 12) % 12) + 1;
                                  return (
                                    <tr key={`tbl-tr-${tp.name}`} className="hover:bg-[#FAF8F2]/40">
                                      <td className="p-1.5 font-semibold text-[#183047] flex items-center gap-1">
                                        <span>{language === "ta" ? tp.sign_name_tamil : tp.name}</span>
                                        {tp.is_retrograde && (
                                          <span className="text-red-600 font-bold font-mono text-[9px]">(R)</span>
                                        )}
                                      </td>
                                      <td className="p-1.5 text-[#52667E]">
                                        {language === "ta" ? tp.sign_name_tamil : tp.sign_name}
                                      </td>
                                      <td className="p-1.5 font-mono text-[#183047]">
                                        {tp.degree_in_sign.toFixed(2)}°
                                      </td>
                                      <td className="p-1.5 font-mono text-[#8C6D23] font-semibold">
                                        H{houseFromLagna}
                                      </td>
                                      <td className="p-1.5 text-[#52667E]">
                                        {tp.nakshatra?.name || "-"} ({tp.nakshatra?.pada || "-"})
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

                    {/* Chart 2: Navamsa (D9) – Strength & Spouse */}
                    <div className="bg-white rounded-xl border border-[#D9DEE7] p-3.5 sm:p-5 shadow-2xs flex flex-col items-center w-full">
                      <div className="w-full text-center pb-2 mb-2 border-b border-[#F2F3F5] flex items-center justify-between gap-2">
                        <span className="text-[11px] font-mono text-[#8190A6] hidden sm:inline">D9</span>
                        <h3 className="font-bold text-xs sm:text-sm text-[#183047] flex-1 text-center">
                          {language === "ta"
                            ? "நவாம்சம் (D9) - வாழ்க்கைத் துணை மற்றும் பலம்"
                            : "Navamsa (D9) - Strength & Spouse"}
                        </h3>
                        <span className="text-[11px] font-mono text-[#8190A6] hidden sm:inline">Navamsha</span>
                      </div>
                      {d9Horoscope && (
                        chartMode === "south" ? (
                          <SouthIndianChart
                            horoscope={d9Horoscope}
                            centerLabel={language === "ta" ? "நவாம்சம்" : "Navamsa"}
                            centerNumber="(9)"
                            isSaved={Boolean(idParam || result?.savedId || result?.isSaved)}
                          />
                        ) : (
                          <NorthIndianChart
                            horoscope={d9Horoscope}
                            isSaved={Boolean(idParam || result?.savedId || result?.isSaved)}
                          />
                        )
                      )}
                    </div>
                  </div>

                  {/* Dasa Bukthi Palangal Quick Access Banner inside Chart Tab */}
                  <div className="p-4 rounded-xl bg-gradient-to-r from-[#153F6B] via-[#102d4d] to-[#183047] border border-[#B4872B]/40 text-white flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 shadow-2xs">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-[#B4872B] text-white flex items-center justify-center shrink-0 shadow-xs">
                        <Sparkles className="w-5 h-5 text-amber-100" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="text-xs sm:text-sm font-bold text-white">
                            {language === "ta" ? "தசா புத்தி பலன்கள் (Dasa Bukthi Palangal)" : "Dasa Bukthi Palangal & Timings"}
                          </h4>
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#B4872B]/30 border border-[#B4872B]/60 text-amber-200">
                            {language === "ta" ? "விம்சோத்தரி முறை" : "Krishan Kant Bhardwaj Canon"}
                          </span>
                        </div>
                        <p className="text-[11px] text-white/80">
                          {language === "ta"
                            ? "இந்த ஜாதகத்தின் தசா-புக்தி அதிபதிகளின் தூர கணிப்பு, ஷட்பலம், அஷ்டகவர்க்கம் மற்றும் நேரடி பலன்களைக் காணுங்கள்."
                            : "Analyze real-time Mahadasha-Antardasha life predictions, Bhavat Bhavam distance, Shadbala, and Sun transits."}
                        </p>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => setSecondaryTab("dasa-palangal")}
                      className="inline-flex items-center justify-center gap-1.5 px-4 py-2 rounded-lg bg-[#B4872B] hover:bg-[#8C6D23] text-white text-xs font-bold shrink-0 transition-colors cursor-pointer shadow-xs"
                    >
                      <span>{language === "ta" ? "தசா பலன்களைக் காண்க ➔" : "View Dasa Predictions ➔"}</span>
                    </button>
                  </div>

                  {/* Astrological Conditions & Predictions Engine directly below D1 & D9 charts */}
                  <AstrologicalPredictionsSection
                    horoscopeResult={result}
                    language={language}
                  />

                  {/* Summary & Remedies Fast Action Banner beneath Charts */}
                  <div className="p-4 rounded-xl bg-white border border-[#D9DEE7] flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 shadow-2xs">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center text-[#B4872B] shrink-0">
                        <Sparkles className="w-4 h-4" />
                      </div>
                      <div>
                        <h4 className="text-xs sm:text-sm font-bold text-[#183047]">
                          {language === "ta" ? "ஜோதிட பரிகாரங்கள் & ரத்தின வழிகாட்டி" : "Astrological Remedies & Gemstone Advisory"}
                        </h4>
                        <p className="text-[11px] text-[#8190A6]">
                          {language === "ta"
                            ? "கிரக தோஷங்களுக்கான வேத பரிகாரங்கள், நவகிரக ஆலயங்கள் மற்றும் ரத்தின பரிந்துரைகள்."
                            : "Vedic remedial measures, temple circuits, and gemstone recommendations."}
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
                        onClick={() => setSecondaryTab("gemstone-download")}
                        className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-[#B4872B] hover:bg-[#8C6D23] text-white font-bold text-xs shadow-2xs transition-colors cursor-pointer"
                      >
                        <Gem className="w-3.5 h-3.5" />
                        <span>{language === "ta" ? "ரத்தின வழிகாட்டி" : "Gemstone Advisory"}</span>
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

              {/* Sub-Tab 2: FACTS & PANCHANG (ஜாதக விவரங்கள் / உண்மைகள் - 6 Categories Dashboard) */}
              {secondaryTab === "facts" && (
                <div className="max-w-7xl mx-auto w-full">
                  <HoroscopeFactsPanel
                    result={result}
                    onCalculateExtensions={handleCalculateVedicExtensions}
                    isCalculatingExtensions={isCalculatingExtensions}
                    initialCategory={(searchParams.get("category") as FactCategory) || "basic"}
                  />
                </div>
              )}

              {/* Sub-Tab 3: PLANETARY POSITIONS */}
              {secondaryTab === "planets" && (
                <div className="max-w-7xl mx-auto w-full">
                  <div className="bg-white rounded-xl border border-[#D9DEE7] p-4 sm:p-5 shadow-2xs space-y-3">
                    <h3 className="font-serif text-lg font-bold text-[#183047]">
                      {t.tabPlanets}
                    </h3>
                    <PlanetaryTable
                      planets={horoscope.planets}
                      ascendant={horoscope.ascendant}
                    />
                  </div>
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
                    onViewPalangal={() => setSecondaryTab("dasa-palangal")}
                  />
                </div>
              )}

              {/* Sub-Tab 4b: DASA BUKTHI PALANGAL (Vimshottari Predictions - Krishan Kant Bhardwaj) */}
              {secondaryTab === "dasa-palangal" && (
                <div className="max-w-7xl mx-auto w-full space-y-4">
                  <DasaBukthiPalangalSection
                    horoscope={horoscope}
                    dasa={dasa}
                    shadbala={result.shadbala || (horoscope as any).shadbala}
                    ashtakavarga={horoscope.ashtakavarga || result.ashtakavarga}
                    birthDate={clientInputs?.birthDate}
                    birthTime={clientInputs?.birthTime}
                    timezone={clientInputs?.timezone}
                    onNavigateToTab={(tab) => setSecondaryTab(tab as any)}
                    liveTransits={liveTransitsData}
                    isLoadingTransits={isLoadingTransits}
                    onFetchTransits={fetchLiveTransits}
                  />
                </div>
              )}

              {/* Sub-Tab 4c: GK TRANSIT PREDICTIONS (Tirupur S. Gopalakrishnan Chandra Nadi Transits) */}
              {secondaryTab === "transits" && (
                <div className="space-y-4">
                  <GkTransitMatchingCard
                    horoscope={horoscope}
                    liveTransits={liveTransitsData}
                    isLoadingTransits={isLoadingTransits}
                    onRefreshTransits={fetchLiveTransits}
                    dasaLord={dasa?.active_period?.mahadasha}
                    bukthiLord={dasa?.active_period?.antardasha}
                    andharaLord={dasa?.active_period?.pratyantardasha}
                  />
                </div>
              )}

              {/* Sub-Tab 4d: MARC BONEY & K.N. RAO MAJOR LIFE MILESTONES */}
              {secondaryTab === "milestones" && (
                <div className="space-y-4">
                  <MarcBoneyMilestonesCard
                    horoscope={horoscope}
                    dasa={dasa}
                    liveTransits={liveTransitsData}
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
                    transitPlanets={liveTransitsData?.planets}
                    natalPlanets={horoscope.planets || result.horoscope?.planets}
                    ascendantSign={horoscope.ascendant?.sign_index || result.horoscope?.ascendant?.sign_index}
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

              {/* Sub-Tab 6b: MEDICAL ASTROLOGY (Classical Vedic & KP Research) */}
              {secondaryTab === "medical" && (
                <div className="space-y-5">
                  <MedicalAstrologySection
                    horoscope={horoscope}
                    kp={kp}
                    dasa={dasa}
                    liveTransits={liveTransitsData}
                    clientInputs={clientInputs}
                    savedHoroscopeId={result.savedId || idParam || undefined}
                  />
                </div>
              )}

              {/* Sub-Tab 7: DOSHAS */}
              {secondaryTab === "doshas" && (
                <div className="space-y-5">
                  <DoshaSection
                    doshas={horoscope.doshas || (result as any).doshas}
                    onCalculate={handleCalculateVedicExtensions}
                    isCalculating={isCalculatingExtensions || isCalculatingLegacyDoshas}
                  />
                </div>
              )}

              {/* Sub-Tab 8: GEMSTONE DOWNLOAD */}
              {secondaryTab === "gemstone-download" && (
                <div className="space-y-4">
                  <GemstoneDownload
                    horoscope={horoscope}
                    clientInputs={clientInputs}
                    doshas={horoscope.doshas || (result as any).doshas}
                    onNavigateTab={(t) => setSecondaryTab(t as any)}
                  />
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
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
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
                    <Gem className="w-4 h-4 text-[#B4872B]" />
                    <span>{language === "ta" ? "ரத்தின வழிகாட்டி (GemstoneDownload)" : "GemstoneDownload Advisory"}</span>
                  </div>
                  <p className="text-xs text-[#8190A6]">
                    {language === "ta"
                      ? "ரத்ன சமாதானம்: 3 தூண் ரத்தினங்கள், உடல் எடைக்கேற்ற ரட்டி அளவுகள் மற்றும் கையேடு பதிவிறக்கம்."
                      : "Personalized 3-Pillar Gems, proportional weight formulas, and downloadable PDF playbook."}
                  </p>
                  <button
                    type="button"
                    onClick={() => {
                      setMainTab("horoscope");
                      setSecondaryTab("gemstone-download");
                    }}
                    className="inline-flex items-center gap-1.5 text-xs font-bold text-[#B4872B] hover:underline pt-1 cursor-pointer"
                  >
                    <span>{language === "ta" ? "ரத்தின வழிகாட்டிக்குச் செல்க →" : "Open GemstoneDownload →"}</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* MAIN TAB 3: REPORTS & DOWNLOADS */}
          {mainTab === "reports" && (
            <div className="space-y-5">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
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

                {/* 2. GemstoneDownload Playbook PDF */}
                <div className="bg-white rounded-xl border-2 border-[#D8BD80] p-5 shadow-2xs space-y-3 flex flex-col justify-between relative overflow-hidden">
                  <div className="absolute top-0 right-0 bg-[#B4872B] text-white text-[9px] font-extrabold px-2 py-0.5 rounded-bl">
                    {language === "ta" ? "புதிய அம்சம்" : "FEATURED"}
                  </div>
                  <div className="space-y-2">
                    <div className="w-10 h-10 rounded-lg bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center text-[#B4872B]">
                      <Gem className="w-5 h-5" />
                    </div>
                    <h3 className="font-bold text-sm text-[#183047]">
                      {language === "ta"
                        ? "ரத்தின கையேடு (GemstoneDownload)"
                        : "GemstoneDownload Playbook"}
                    </h3>
                    <p className="text-xs text-[#8190A6]">
                      {language === "ta"
                        ? "ரத்ன சமாதானம்: 3 தூண் ரத்தினங்கள், மந்திரங்கள் மற்றும் ருத்ராட்ச சாஸ்திர PDF கையேடு."
                        : "3-Pillar Gems, body weight formulas, mantras, and Rudraksha sanctification PDF."}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      setMainTab("horoscope");
                      setSecondaryTab("gemstone-download");
                    }}
                    className="w-full inline-flex items-center justify-center gap-1.5 px-4 py-2 rounded-lg bg-gradient-to-r from-[#B4872B] to-[#D8BD80] hover:from-[#9B7322] hover:to-[#B4872B] text-[#0F2942] text-xs font-bold shadow-2xs transition-all cursor-pointer"
                  >
                    <Gem className="w-3.5 h-3.5" />
                    <span>{language === "ta" ? "வழிகாட்டி & PDF (GemstoneDownload)" : "Open GemstoneDownload"}</span>
                  </button>
                </div>

                {/* 4. CSV Planetary Positions */}
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
        <div className="w-full px-4 py-20 text-center">
          <div className="inline-block animate-spin w-8 h-8 border-4 border-[#153F6B] border-t-transparent rounded-full mb-4" />
          <p className="text-sm text-[#8190A6]">Loading horoscope...</p>
        </div>
      }
    >
      <HoroscopeResultsContent />
    </Suspense>
  );
}
