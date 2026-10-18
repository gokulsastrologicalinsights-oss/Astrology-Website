"use client";

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { getActiveCalculation, saveActiveCalculation } from "@/lib/storage";
import { FullHoroscopeResult } from "@/lib/types";
import {
  formatSerialNumber,
  formatBirthDate,
  formatBirthTime,
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
import { calculateNabhasha, calculateAshtakavarga, calculateVedicYogas } from "@/lib/api";
import { buildPlanetContexts, enrichDasaTreeWithBenefitBhavas } from "@/lib/benefit-bhavas";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  Compass,
  ArrowLeft,
  Calendar,
  Clock,
  MapPin,
  Globe,
  Sliders,
  Layers,
  Printer,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  Database,
  RefreshCw,
  Info,
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

  const [chartMode, setChartMode] = useState<"south" | "north">("south");
  const [activeTab, setActiveTab] = useState<
    "chart" | "planets" | "houses" | "dasa" | "kp" | "panchang" | "vedic-yogas" | "nabhasha" | "ashtakavarga"
  >(() => {
    const validTabs = ["chart", "planets", "houses", "dasa", "kp", "panchang", "vedic-yogas", "nabhasha", "ashtakavarga"];
    if (tabParam && validTabs.includes(tabParam)) {
      return tabParam as any;
    }
    if (typeof window !== "undefined" && window.location.hash === "#kp-events") {
      return "kp";
    }
    return "chart";
  });

  useEffect(() => {
    const validTabs = ["chart", "planets", "houses", "dasa", "kp", "panchang", "vedic-yogas", "nabhasha", "ashtakavarga"];
    if (tabParam && validTabs.includes(tabParam)) {
      setActiveTab(tabParam as any);
    } else if (typeof window !== "undefined" && window.location.hash === "#kp-events") {
      setActiveTab("kp");
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

      const [nabhashaRes, ashtakavargaRes, vedicYogaRes] = await Promise.all([
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
      ]);

      const updatedHoroscope = {
        ...result.horoscope,
        nabhasha_yogas: nabhashaRes || result.horoscope.nabhasha_yogas,
        ashtakavarga: ashtakavargaRes || result.horoscope.ashtakavarga,
        vedic_yogas: vedicYogaRes || result.horoscope.vedic_yogas,
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
  // Does NOT recalculate the horoscope. Directly displays the stored calculation snapshot.
  useEffect(() => {
    if (idParam) {
      setIsLoadingSaved(true);
      setLoadError(null);
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

          // Auto-heal dasa tree to ensure accurate canonical Vedic house occupancies (Venus in H2)
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

          // If vedic_yogas is not in saved snapshot, auto-calculate in background
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
                console.warn("Auto-calculation of Vedic Yogas for saved horoscope failed:", e);
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

  if (isLoadingSaved) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-24 text-center space-y-4">
        <div className="inline-block animate-spin w-10 h-10 border-4 border-[#B8860B] border-t-transparent rounded-full" />
        <h2 className="font-serif text-lg font-bold text-[#0F172A]">
          {language === "ta"
            ? "சேமிக்கப்பட்ட ஜாதகம் ஏற்றப்படுகிறது..."
            : "Loading saved horoscope snapshot..."}
        </h2>
        <p className="text-xs text-[#64748B]">
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
        <h2 className="font-serif text-2xl font-bold text-[#0F172A]">
          {language === "ta" ? "ஜாதகத்தை ஏற்ற முடியவில்லை" : "Could Not Load Horoscope"}
        </h2>
        <p className="text-sm text-[#64748B] max-w-md mx-auto">{loadError}</p>
        <div className="pt-2">
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-bold text-white bg-[#0F172A] hover:bg-[#1E293B] shadow-md transition-all"
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
        <div className="w-16 h-16 rounded-full bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center mx-auto text-[#B8860B]">
          <Compass className="w-8 h-8" />
        </div>
        <h2 className="font-serif text-2xl font-bold text-[#0F172A]">
          {language === "ta"
            ? "ஜாதகத் தரவு எதுவும் கிடைக்கவில்லை"
            : "No Active Calculation Found"}
        </h2>
        <p className="text-sm text-[#64748B] leading-relaxed max-w-md mx-auto">
          {language === "ta"
            ? "ஜாதக முடிவுகளைப் பார்க்க தயவுசெய்து உங்கள் பிறப்பு விவரங்களை உள்ளிட்டு கணக்கீட்டைத் தொடங்கவும்."
            : "Please enter your birth details to generate and inspect planetary positions, charts, and dasa periods."}
        </p>
        <div className="pt-2">
          <Link
            href="/horoscope"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-lg text-sm font-bold text-white bg-[#0F172A] hover:bg-[#1E293B] shadow-md transition-all"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>{t.navHoroscope}</span>
          </Link>
        </div>
      </div>
    );
  }

  const { horoscope, dasa, kp, clientInputs } = result;
  const serialBadge = result.displayNumber ? formatSerialNumber(result.displayNumber) : null;
  const birthDateDisplay = formatBirthDate(clientInputs.birthDate, language);
  const birthTimeDisplay = formatBirthTime(clientInputs.birthTime);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12 space-y-8">
      {/* Navigation Breadcrumbs & Back Link */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <Breadcrumbs
          items={[
            {
              label: language === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools",
              href: "/tools",
            },
            {
              label: language === "ta" ? "ஜாதகம் மற்றும் கே.பி. ஜோதிடம்" : "Horoscope / KP System",
              href: "/tools/horoscope",
            },
            {
              label: clientInputs.fullName
                ? `${clientInputs.fullName}'s ${t.resultsTitle}`
                : t.resultsTitle,
            },
          ]}
        />

        <Link
          href="/tools/horoscope"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#52667E] hover:text-[#102A4C] transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>
            {language === "ta"
              ? "ஜாதகக் கருவிகள் அடைவு"
              : "Back to Horoscope / KP Tools"}
          </span>
        </Link>
      </div>

      {/* 1. Top Navigation & Action Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#DDE5F0]">
        <div className="space-y-1">
          <div className="flex items-center gap-2.5">
            <Link
              href="/tools/horoscope?tab=saved"
              className="text-xs font-semibold text-[#B8862B] hover:text-[#102A4C] inline-flex items-center gap-1"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>{t.backToSavedHoroscopes}</span>
            </Link>

            {result.displayNumber && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-serif font-bold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
                {formatHoroscopeSequence(result.displayNumber, language)}
              </span>
            )}
          </div>

          <h1 className="font-serif text-2xl sm:text-3xl font-bold text-[#0F172A] flex items-center gap-3">
            <span>
              {clientInputs.fullName
                ? `${clientInputs.fullName}'s ${t.resultsTitle}`
                : t.resultsTitle}
            </span>
          </h1>

          <p className="text-xs sm:text-sm text-[#64748B]">
            {t.resultsSubtitle}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => window.print()}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg border border-[#E2DCD5] bg-white text-xs font-medium text-[#334155] hover:bg-[#FAF8F5] shadow-2xs"
          >
            <Printer className="w-3.5 h-3.5" />
            <span>{language === "ta" ? "அச்சிடுக" : "Print"}</span>
          </button>
          <Link
            href="/horoscope"
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg border border-[#D8BD80] bg-[#FAF2DE] text-xs font-bold text-[#784E0E] hover:bg-[#FAF6EC] shadow-2xs"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>{language === "ta" ? "புதிய கணிப்பு" : "New Chart"}</span>
          </Link>
        </div>
      </div>

      {/* 2. Notification Banners: Saving..., Saved successfully, Save failed */}
      {isRetryingSave && (
        <div className="p-3.5 rounded-xl bg-blue-50 border border-blue-200 text-blue-900 text-xs flex items-center gap-2 shadow-2xs">
          <RefreshCw className="w-4 h-4 text-blue-600 animate-spin shrink-0" />
          <span className="font-semibold">
            {language === "ta" ? "சேமிக்கப்படுகிறது…" : "Saving…"}
          </span>
        </div>
      )}

      {result.isSaved && result.displayNumber && !isRetryingSave && (
        <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs flex items-center justify-between gap-3 shadow-2xs">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span className="font-medium">
              {language === "ta"
                ? `வெற்றிகரமாகச் சேமிக்கப்பட்டது — ${formatHoroscopeSequence(result.displayNumber, language)}.`
                : `Saved successfully — ${formatHoroscopeSequence(result.displayNumber, language)}.`}
            </span>
          </div>
          <Link
            href="/horoscopes"
            className="underline font-semibold text-emerald-800 hover:text-emerald-950 shrink-0"
          >
            {t.backToSavedHoroscopes}
          </Link>
        </div>
      )}

      {result.saveError && !result.isSaved && !isRetryingSave && (
        <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
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
            className="inline-flex items-center justify-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-700 text-white font-semibold text-xs transition-colors shrink-0 cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>{language === "ta" ? "மீண்டும் முயற்சிக்கவும்" : "Retry"}</span>
          </button>
        </div>
      )}

      {retryNotice && (
        <div className="p-3 rounded-xl bg-blue-50 border border-blue-200 text-blue-900 text-xs flex items-center gap-2">
          <Info className="w-4 h-4 text-blue-600 shrink-0" />
          <span>{retryNotice}</span>
        </div>
      )}

      {/* Distinction notice if birth details were edited after calculation */}
      {result.editedAfterCalculation && (
        <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-start gap-2.5">
          <Info className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <strong className="font-semibold block">{t.editedWithoutRecalcBadge}</strong>
            <p className="mt-0.5 leading-relaxed">{t.editedWithoutRecalcNotice}</p>
          </div>
        </div>
      )}

      {/* 3. Birth Details & Ephemeris Summary Banner */}
      <div className="p-4 sm:p-5 rounded-xl border border-[#D8BD80]/80 bg-[#FAF7F0] shadow-2xs">
        <div className="flex items-center justify-between pb-3 border-b border-[#E8DEC8] mb-3">
          <span className="text-xs font-bold uppercase tracking-wider text-[#8C6D23] flex items-center gap-1.5">
            <Compass className="w-4 h-4 text-[#B8860B]" />
            <span>{t.birthSummaryTitle}</span>
          </span>
          <span className="text-[11px] font-mono text-[#64748B]">
            JD (UT1): {horoscope.metadata?.julian_day_ut1?.toFixed(4) || "—"}
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 text-xs">
          <div className="space-y-0.5">
            <div className="text-[11px] text-[#64748B] flex items-center gap-1">
              <Calendar className="w-3 h-3 text-[#B8860B]" />
              <span>{t.fieldDate}</span>
            </div>
            <div className="font-semibold text-[#0F172A]">
              {birthDateDisplay}
            </div>
          </div>

          <div className="space-y-0.5">
            <div className="text-[11px] text-[#64748B] flex items-center gap-1">
              <Clock className="w-3 h-3 text-[#B8860B]" />
              <span>{t.fieldTime}</span>
            </div>
            <div className="font-semibold text-[#0F172A] font-mono">
              {birthTimeDisplay}
            </div>
          </div>

          <div className="space-y-0.5">
            <div className="text-[11px] text-[#64748B] flex items-center gap-1">
              <MapPin className="w-3 h-3 text-[#B8860B]" />
              <span>{t.fieldPlace}</span>
            </div>
            <div className="font-semibold text-[#0F172A] truncate" title={clientInputs.locationName}>
              {clientInputs.locationName || t.locationUnavailable}
            </div>
          </div>

          <div className="space-y-0.5">
            <div className="text-[11px] text-[#64748B] flex items-center gap-1">
              <Globe className="w-3 h-3 text-[#B8860B]" />
              <span>{language === "ta" ? "அட்ச/தீர்க்க ரேகை" : "Coordinates"}</span>
            </div>
            <div className="font-semibold text-[#0F172A] font-mono">
              {clientInputs.latitude?.toFixed(2)}°, {clientInputs.longitude?.toFixed(2)}°
            </div>
          </div>

          <div className="space-y-0.5">
            <div className="text-[11px] text-[#64748B] flex items-center gap-1">
              <Sliders className="w-3 h-3 text-[#B8860B]" />
              <span>{t.fieldAyanamsa}</span>
            </div>
            <div className="font-semibold text-[#0F172A]">
              {horoscope.metadata?.ayanamsa_name || "Lahiri"}
            </div>
          </div>

          <div className="space-y-0.5">
            <div className="text-[11px] text-[#64748B] flex items-center gap-1">
              <Layers className="w-3 h-3 text-[#B8860B]" />
              <span>{t.fieldHouseSystem}</span>
            </div>
            <div className="font-semibold text-[#0F172A]">
              {horoscope.metadata?.house_system_name || "Placidus"}
            </div>
          </div>
        </div>
      </div>

      {/* 4. Navigation Tabs */}
      <div className="border-b border-[#E2DCD5] flex items-center gap-2 overflow-x-auto pb-1">
        <button
          type="button"
          onClick={() => setActiveTab("chart")}
          className={`px-4 py-2 text-xs sm:text-sm font-bold rounded-lg transition-all ${
            activeTab === "chart"
              ? "bg-[#0F172A] text-white shadow-xs"
              : "text-[#475569] hover:bg-[#FAF6EC] hover:text-[#0F172A]"
          }`}
        >
          {t.tabChart}
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("planets")}
          className={`px-4 py-2 text-xs sm:text-sm font-bold rounded-lg transition-all ${
            activeTab === "planets"
              ? "bg-[#0F172A] text-white shadow-xs"
              : "text-[#475569] hover:bg-[#FAF6EC] hover:text-[#0F172A]"
          }`}
        >
          {t.tabPlanets}
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("houses")}
          className={`px-4 py-2 text-xs sm:text-sm font-bold rounded-lg transition-all ${
            activeTab === "houses"
              ? "bg-[#0F172A] text-white shadow-xs"
              : "text-[#475569] hover:bg-[#FAF6EC] hover:text-[#0F172A]"
          }`}
        >
          {t.tabHouses}
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("dasa")}
          className={`px-4 py-2 text-xs sm:text-sm font-bold rounded-lg transition-all ${
            activeTab === "dasa"
              ? "bg-[#0F172A] text-white shadow-xs"
              : "text-[#475569] hover:bg-[#FAF6EC] hover:text-[#0F172A]"
          }`}
        >
          {t.tabDasa}
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("kp")}
          className={`px-4 py-2 text-xs sm:text-sm font-bold rounded-lg transition-all ${
            activeTab === "kp"
              ? "bg-[#0F172A] text-white shadow-xs"
              : "text-[#475569] hover:bg-[#FAF6EC] hover:text-[#0F172A]"
          }`}
        >
          {t.tabKp}
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("panchang")}
          className={`px-4 py-2 text-xs sm:text-sm font-bold rounded-lg transition-all ${
            activeTab === "panchang"
              ? "bg-[#0F172A] text-white shadow-xs"
              : "text-[#475569] hover:bg-[#FAF6EC] hover:text-[#0F172A]"
          }`}
        >
          {t.tabPanchang}
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("nabhasha")}
          className={`px-4 py-2 text-xs sm:text-sm font-bold rounded-lg transition-all ${
            activeTab === "nabhasha"
              ? "bg-[#0F172A] text-white shadow-xs"
              : "text-[#475569] hover:bg-[#FAF6EC] hover:text-[#0F172A]"
          }`}
        >
          {t.tabNabhasha}
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("ashtakavarga")}
          className={`px-4 py-2 text-xs sm:text-sm font-bold rounded-lg transition-all ${
            activeTab === "ashtakavarga"
              ? "bg-[#0F172A] text-white shadow-xs"
              : "text-[#475569] hover:bg-[#FAF6EC] hover:text-[#0F172A]"
          }`}
        >
          {t.tabAshtakavarga}
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("vedic-yogas")}
          className={`px-4 py-2 text-xs sm:text-sm font-bold rounded-lg transition-all ${
            activeTab === "vedic-yogas"
              ? "bg-[#0F172A] text-white shadow-xs"
              : "text-[#475569] hover:bg-[#FAF6EC] hover:text-[#0F172A]"
          }`}
        >
          {t.tabVedicYogas}
        </button>
      </div>

      {/* 5. Tab Content Panels */}
      <div>
        {/* Tab 1: Birth Chart with South / North Switcher */}
        {activeTab === "chart" && (
          <div className="space-y-6">
            <div className="flex items-center justify-center gap-2">
              <span className="text-xs font-semibold text-[#64748B] mr-2">
                {t.chartSwitchMode}:
              </span>
              <button
                type="button"
                onClick={() => setChartMode("south")}
                className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
                  chartMode === "south"
                    ? "bg-[#B8860B] text-white shadow-2xs"
                    : "bg-white border border-[#E2DCD5] text-[#334155] hover:bg-[#FAF6EC]"
                }`}
              >
                {t.chartSouthIndian}
              </button>
              <button
                type="button"
                onClick={() => setChartMode("north")}
                className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
                  chartMode === "north"
                    ? "bg-[#B8860B] text-white shadow-2xs"
                    : "bg-white border border-[#E2DCD5] text-[#334155] hover:bg-[#FAF6EC]"
                }`}
              >
                {t.chartNorthIndian}
              </button>
            </div>

            <div className="py-2">
              {chartMode === "south" ? (
                <SouthIndianChart horoscope={horoscope} />
              ) : (
                <NorthIndianChart horoscope={horoscope} />
              )}
            </div>

            <div className="pt-6 border-t border-[#E2DCD5]">
              <h3 className="font-serif text-base font-bold text-[#0F172A] mb-3">
                {t.tabPlanets}
              </h3>
              <PlanetaryTable
                planets={horoscope.planets}
                ascendant={horoscope.ascendant}
              />
            </div>
          </div>
        )}

        {/* Tab 2: Planetary Positions */}
        {activeTab === "planets" && (
          <div className="space-y-4">
            <h3 className="font-serif text-lg font-bold text-[#0F172A]">
              {t.tabPlanets}
            </h3>
            <PlanetaryTable
              planets={horoscope.planets}
              ascendant={horoscope.ascendant}
            />
          </div>
        )}

        {/* Tab 3: Houses / Bhavas */}
        {activeTab === "houses" && (
          <div className="space-y-4">
            <h3 className="font-serif text-lg font-bold text-[#0F172A]">
              {t.tabHouses}
            </h3>
            <HousesTable houses={horoscope.houses} />
          </div>
        )}

        {/* Tab 4: Vimshottari Dasa */}
        {activeTab === "dasa" && (
          <div className="space-y-4">
            <h3 className="font-serif text-lg font-bold text-[#0F172A]">
              {t.tabDasa}
            </h3>
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

        {/* Tab 5: KP Krishnamurti Paddhati */}
        {activeTab === "kp" && (
          <div className="space-y-4">
            <h3 className="font-serif text-lg font-bold text-[#0F172A]">
              {t.tabKp}
            </h3>
            <KpSection
              kp={kp}
              dasa={dasa}
              horoscope={horoscope}
              savedHoroscopeId={result.savedId}
            />
          </div>
        )}

        {/* Tab 6: Panchang */}
        {activeTab === "panchang" && (
          <div className="space-y-4">
            <h3 className="font-serif text-lg font-bold text-[#0F172A]">
              {t.tabPanchang}
            </h3>
            <PanchangCard panchang={horoscope.panchang} />
          </div>
        )}

        {/* Tab 7: Classical Nabhasha Yogas */}
        {activeTab === "nabhasha" && (
          <div className="space-y-4">
            <NabhashaSection
              nabhasha={horoscope.nabhasha_yogas || result.nabhasha}
              onCalculate={handleCalculateVedicExtensions}
              isCalculating={isCalculatingExtensions}
            />
          </div>
        )}

        {/* Tab 8: Classical Ashtakavarga */}
        {activeTab === "ashtakavarga" && (
          <div className="space-y-4">
            <AshtakavargaSection
              ashtakavarga={horoscope.ashtakavarga || result.ashtakavarga}
              onCalculate={handleCalculateVedicExtensions}
              isCalculating={isCalculatingExtensions}
            />
          </div>
        )}

        {/* Tab 9: Classical Vedic Yogas */}
        {activeTab === "vedic-yogas" && (
          <div className="space-y-4">
            <VedicYogaSection
              vedicYogas={horoscope.vedic_yogas || result.vedic_yogas}
              onCalculate={handleCalculateVedicExtensions}
              isCalculating={isCalculatingExtensions}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default function HoroscopeResultsPage() {
  return (
    <Suspense
      fallback={
        <div className="max-w-5xl mx-auto px-4 py-20 text-center">
          <div className="inline-block animate-spin w-8 h-8 border-4 border-[#B8860B] border-t-transparent rounded-full mb-4" />
          <p className="text-sm text-[#64748B]">Loading horoscope...</p>
        </div>
      }
    >
      <HoroscopeResultsContent />
    </Suspense>
  );
}