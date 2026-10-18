"use client";

import React, { useState, useEffect, useRef, useCallback, Suspense } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { TransitTimelineRequest, TransitTimelineResponse } from "@/lib/types";
import { getTransitTimeline } from "@/lib/api";
import { TransitWatchControls } from "@/components/transit-watch/TransitWatchControls";
import { TransitWatchTimeline } from "@/components/transit-watch/TransitWatchTimeline";
import {
  Clock,
  ArrowLeft,
  AlertCircle,
  RefreshCw,
  Layers,
} from "lucide-react";

function getTodayIsoDate(): string {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function getUserTimezone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Kolkata";
  } catch {
    return "Asia/Kolkata";
  }
}

function TransitWatchContent() {
  const router = useRouter();
  const { language } = useLanguage();
  const { session, isAuthenticated, isLoading } = useAuth();

  const [requestParams, setRequestParams] = useState<TransitTimelineRequest>(() => ({
    start_date: getTodayIsoDate(),
    start_time: "00:00:00",
    forecast_days: 7,
    timezone: getUserTimezone(),
    planets: ["Moon", "Sun", "Jupiter", "Saturn", "Rahu", "Ketu"],
    ayanamsa: 0,
    max_events: 500,
  }));

  const [timelineData, setTimelineData] = useState<TransitTimelineResponse | null>(null);
  const [calculating, setCalculating] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Prevent duplicate concurrent requests during mounting & auth state changes
  const activeRequestRef = useRef<boolean>(false);
  const initialFetchDoneRef = useRef<boolean>(false);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  const executeCalculation = useCallback(
    async (params: TransitTimelineRequest) => {
      if (!session?.access_token) return;
      if (activeRequestRef.current) return;

      activeRequestRef.current = true;
      setCalculating(true);
      setErrorMsg(null);

      try {
        const response = await getTransitTimeline(params, session.access_token);
        setTimelineData(response);
      } catch (err: unknown) {
        console.warn("Transit timeline calculation failed:", err);
        const errMessage = err instanceof Error ? err.message : null;
        setErrorMsg(
          errMessage ||
            (language === "ta"
              ? "கோசார கணக்கீடு தோல்வியடைந்தது. தயவுசெய்து மீண்டும் முயற்சிக்கவும்."
              : "Failed to calculate KP transit ingress timeline. Please check your inputs and try again.")
        );
      } finally {
        setCalculating(false);
        activeRequestRef.current = false;
      }
    },
    [session, language]
  );

  // Initial calculation trigger once authenticated
  useEffect(() => {
    if (session?.access_token && !initialFetchDoneRef.current) {
      initialFetchDoneRef.current = true;
      executeCalculation(requestParams);
    }
  }, [session?.access_token, executeCalculation, requestParams]);

  const handleParamsChange = (newParams: TransitTimelineRequest) => {
    setRequestParams(newParams);
    executeCalculation(newParams);
  };

  const handleRetry = () => {
    executeCalculation(requestParams);
  };

  if (isLoading) {
    return (
      <div className="min-h-[calc(100vh-14rem)] flex items-center justify-center bg-[#E8EEF7]">
        <div className="w-8 h-8 border-4 border-[#B8862B] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-8">
      {/* 1. Breadcrumbs */}
      <Breadcrumbs
        items={[
          {
            label: language === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools",
            href: "/tools",
          },
          {
            label: language === "ta" ? "KP கோசார காலவரிசை" : "KP Transit Watch",
          },
        ]}
      />

      {/* 2. Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-[#DDE5F0]">
        <div className="space-y-1.5">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
            <Clock className="w-3.5 h-3.5 text-[#B8862B]" />
            <span>{language === "ta" ? "நேரலை கோசார கண்காணிப்பு" : "Real-Time Planetary Ingress Engine"}</span>
          </div>
          <h1 className="font-serif text-3xl sm:text-4xl font-bold text-[#102A4C] tracking-tight">
            KP Transit Watch | கோசார கிரக நிலைகள்
          </h1>
          <p className="text-xs sm:text-sm text-[#52667E] max-w-2xl leading-relaxed">
            {language === "ta"
              ? "கிருஷ்ணமூர்த்தி பத்ததியின் 249 உப-அதிபதி (Sub-Lord) மற்றும் நட்சத்திர எல்லை மாற்றங்களை வினாடி துல்லியத்துடன் கண்காணிக்கும் உயர்நிலை கணக்கீட்டு அமைப்பு."
              : "High-precision KP Sub-Lord (Tier 3 / 249 divisions), Nakshatra, and Rashi ingress boundary transitions computed using native XALEN numerical bisection."}
          </p>
        </div>

        <div className="flex items-center gap-2 self-start md:self-auto">
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-[#52667E] bg-white border border-[#DDE5F0] hover:bg-[#F8FAFC] shadow-2xs transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>{language === "ta" ? "முகப்பு பலகை" : "Dashboard"}</span>
          </Link>

          <Link
            href="/tools/advanced-kp"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-[#B8862B] bg-[#FAF2DE] border border-[#D8BD80] hover:bg-[#F2E5C2] shadow-2xs transition-colors"
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Advanced KP</span>
          </Link>
        </div>
      </div>

      {/* 3. Controls & Configuration */}
      <TransitWatchControls
        initialValues={requestParams}
        onCalculate={handleParamsChange}
        isLoading={calculating}
        language={language}
      />

      {/* 4. Error State */}
      {errorMsg && (
        <div className="rounded-2xl border border-rose-300 bg-rose-50 p-6 text-center space-y-3">
          <div className="w-10 h-10 rounded-xl bg-rose-100 text-rose-700 flex items-center justify-center mx-auto">
            <AlertCircle className="w-5 h-5" />
          </div>
          <h3 className="font-serif text-base font-bold text-rose-950">
            {language === "ta" ? "கணக்கீடு பிழை" : "Calculation Error"}
          </h3>
          <p className="text-xs text-rose-800 max-w-lg mx-auto">{errorMsg}</p>
          <div className="pt-2">
            <button
              type="button"
              onClick={handleRetry}
              disabled={calculating}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white bg-rose-700 hover:bg-rose-800 shadow-xs transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${calculating ? "animate-spin" : ""}`} />
              <span>{language === "ta" ? "மீண்டும் முயற்சி செய்" : "Retry Calculation"}</span>
            </button>
          </div>
        </div>
      )}

      {/* 5. Loading State Skeleton */}
      {calculating && !errorMsg && (
        <div className="space-y-6 animate-pulse">
          <div className="h-20 rounded-2xl bg-white border border-[#DDE5F0] p-4 flex items-center justify-between">
            <div className="w-1/3 h-4 bg-slate-200 rounded-md" />
            <div className="w-1/4 h-4 bg-slate-200 rounded-md" />
          </div>
          <div className="space-y-4">
            <div className="w-48 h-6 bg-slate-200 rounded-md" />
            <div className="h-32 rounded-2xl bg-white border border-[#DDE5F0] p-4 space-y-3">
              <div className="w-1/2 h-4 bg-slate-200 rounded-md" />
              <div className="grid grid-cols-3 gap-3">
                <div className="h-16 bg-slate-100 rounded-xl" />
                <div className="h-16 bg-slate-100 rounded-xl" />
                <div className="h-16 bg-slate-100 rounded-xl" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 6. Ingress Timeline Output */}
      {!calculating && !errorMsg && timelineData && (
        <TransitWatchTimeline data={timelineData} language={language} />
      )}
    </div>
  );
}

export default function TransitWatchPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-[calc(100vh-14rem)] flex items-center justify-center bg-[#E8EEF7]">
          <div className="w-8 h-8 border-4 border-[#B8862B] border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <TransitWatchContent />
    </Suspense>
  );
}
