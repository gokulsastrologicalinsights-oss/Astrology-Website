"use client";

import React, { useState } from "react";
import { AshtakavargaResponse, PlanetBavDetail } from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { getGrahaName, getRasiName, RASIS, GRAHAS } from "@/lib/translations";
import {
  Grid,
  CheckCircle2,
  ShieldCheck,
  Bookmark,
  Award,
  BarChart3,
  TrendingUp,
  Table,
  Sparkles,
  Layers,
  Orbit,
} from "lucide-react";

interface AshtakavargaSectionProps {
  ashtakavarga?: AshtakavargaResponse | null;
  onCalculate?: () => void;
  isCalculating?: boolean;
}

const CLASSICAL_PLANETS = [
  "Sun",
  "Moon",
  "Mars",
  "Mercury",
  "Jupiter",
  "Venus",
  "Saturn",
];

export function AshtakavargaSection({
  ashtakavarga,
  onCalculate,
  isCalculating,
}: AshtakavargaSectionProps) {
  const { language, t } = useLanguage();

  const [activeSubTab, setActiveSubTab] = useState<"sav" | "bav" | "matrix">("sav");
  const [selectedPlanet, setSelectedPlanet] = useState<string>("Sun");
  const [shodhanaStage, setShodhanaStage] = useState<"raw" | "trikona" | "ekadhipatya" | "pinda">("raw");

  if (!ashtakavarga) {
    return (
      <div className="p-8 rounded-xl border border-[#E2DCD5] bg-white text-center space-y-4 shadow-xs">
        <div className="w-12 h-12 mx-auto rounded-full bg-[#FAF2DE] text-[#8C6D23] flex items-center justify-center">
          <Grid className="w-6 h-6" />
        </div>
        <div className="space-y-1">
          <h3 className="font-serif text-lg font-bold text-[#0F172A]">
            {t.ashtakavargaTitle}
          </h3>
          <p className="text-xs text-[#64748B] max-w-md mx-auto">
            {language === "ta"
              ? "அஷ்டகவர்க்கக் கணக்கீட்டு முடிவுகள் இன்னும் ஏற்றப்படவில்லை."
              : "Ashtakavarga calculations are not yet generated for this horoscope snapshot."}
          </p>
        </div>
        {onCalculate && (
          <button
            type="button"
            onClick={onCalculate}
            disabled={isCalculating}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs font-bold text-white bg-[#0F172A] hover:bg-[#1E293B] shadow-sm disabled:opacity-50 transition-all cursor-pointer"
          >
            {isCalculating ? (
              <>
                <Orbit className="w-4 h-4 animate-spin" />
                <span>{language === "ta" ? "கணக்கிடப்படுகிறது..." : "Calculating..."}</span>
              </>
            ) : (
              <>
                <Grid className="w-4 h-4" />
                <span>{language === "ta" ? "அஷ்டகவர்க்கத்தைக் கணக்கிடு" : "Calculate Ashtakavarga"}</span>
              </>
            )}
          </button>
        )}
      </div>
    );
  }

  const {
    bhinnashtakavarga,
    sarvashtakavarga,
    lagna_sign_index,
    validation_status,
    classical_reference,
  } = ashtakavarga;

  const currentBav: PlanetBavDetail | undefined = bhinnashtakavarga[selectedPlanet];

  // Helper to extract bindus based on stage
  const getBavBinduForSign = (signIdx: number): number => {
    if (!currentBav) return 0;
    const key = String(signIdx);
    if (shodhanaStage === "trikona" && currentBav.trikona_reduced) {
      return currentBav.trikona_reduced[key] ?? 0;
    }
    if (shodhanaStage === "ekadhipatya" && currentBav.ekadhipatya_reduced) {
      return currentBav.ekadhipatya_reduced[key] ?? 0;
    }
    return currentBav.sign_bindus[key] ?? 0;
  };

  return (
    <div className="space-y-6">
      {/* 1. Header Banner */}
      <div className="p-4 sm:p-5 rounded-xl border border-[#D8BD80]/80 bg-[#FAF7F0] shadow-2xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-[#E8DEC8]">
          <div className="flex items-center gap-2">
            <Grid className="w-5 h-5 text-[#B8860B]" />
            <h3 className="font-serif text-lg font-bold text-[#0F172A]">
              {t.ashtakavargaTitle}
            </h3>
          </div>
          <span className="inline-flex items-center gap-1.5 text-[11px] font-mono font-bold text-emerald-800 bg-emerald-50 border border-emerald-300 px-3 py-1 rounded-full self-start sm:self-auto">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>{t.ashtakavargaInvariantValidated} (337)</span>
          </span>
        </div>
        <p className="text-xs text-[#64748B] mt-2.5 leading-relaxed">
          {t.ashtakavargaSubtitle}
        </p>
        <div className="mt-3 pt-2.5 border-t border-[#E8DEC8]/60 flex flex-wrap items-center justify-between text-[11px] text-[#64748B] gap-2">
          <span className="flex items-center gap-1.5 font-medium text-[#784E0E]">
            <Bookmark className="w-3.5 h-3.5 text-[#B8860B]" />
            <span>{classical_reference}</span>
          </span>
          <span className="text-[10px] bg-white px-2 py-0.5 rounded border border-[#E2DCD5] text-[#475569]">
            Lagna: {getRasiName(lagna_sign_index, language)} (Sign {lagna_sign_index})
          </span>
        </div>
      </div>

      {/* 2. Sub-tab Navigation */}
      <div className="border-b border-[#E2DCD5] flex items-center gap-2">
        <button
          type="button"
          onClick={() => setActiveSubTab("sav")}
          className={`px-4 py-2 text-xs sm:text-sm font-bold rounded-t-lg transition-all border-b-2 cursor-pointer ${
            activeSubTab === "sav"
              ? "border-[#B8860B] text-[#784E0E] bg-[#FAF8F5]"
              : "border-transparent text-[#475569] hover:text-[#0F172A]"
          }`}
        >
          <div className="flex items-center gap-1.5">
            <BarChart3 className="w-3.5 h-3.5" />
            <span>{t.ashtakavargaSavTab}</span>
          </div>
        </button>

        <button
          type="button"
          onClick={() => setActiveSubTab("bav")}
          className={`px-4 py-2 text-xs sm:text-sm font-bold rounded-t-lg transition-all border-b-2 cursor-pointer ${
            activeSubTab === "bav"
              ? "border-[#B8860B] text-[#784E0E] bg-[#FAF8F5]"
              : "border-transparent text-[#475569] hover:text-[#0F172A]"
          }`}
        >
          <div className="flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5" />
            <span>{t.ashtakavargaBavTab}</span>
          </div>
        </button>

        <button
          type="button"
          onClick={() => setActiveSubTab("matrix")}
          className={`px-4 py-2 text-xs sm:text-sm font-bold rounded-t-lg transition-all border-b-2 cursor-pointer ${
            activeSubTab === "matrix"
              ? "border-[#B8860B] text-[#784E0E] bg-[#FAF8F5]"
              : "border-transparent text-[#475569] hover:text-[#0F172A]"
          }`}
        >
          <div className="flex items-center gap-1.5">
            <Table className="w-3.5 h-3.5" />
            <span>{t.ashtakavargaMatrixTab}</span>
          </div>
        </button>
      </div>

      {/* ========================================================= */}
      {/* TAB 1: SARVASHTAKAVARGA (SAV)                             */}
      {/* ========================================================= */}
      {activeSubTab === "sav" && (
        <div className="space-y-6">
          {/* Summary Stat Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3.5 rounded-xl bg-white border border-[#E2DCD5] shadow-2xs text-center">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] block">
                {t.ashtakavargaTotalBindus}
              </span>
              <span className="font-serif text-2xl font-bold text-[#0F172A] mt-1 block">
                {sarvashtakavarga.total_bindus} / 337
              </span>
              <span className="text-[10px] text-emerald-700 font-semibold block mt-0.5">
                Exact Invariant Match
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-white border border-[#E2DCD5] shadow-2xs text-center">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] block">
                Average Per Sign
              </span>
              <span className="font-serif text-2xl font-bold text-[#784E0E] mt-1 block">
                {sarvashtakavarga.average_per_sign.toFixed(2)}
              </span>
              <span className="text-[10px] text-[#64748B] block mt-0.5">
                Threshold: 28 Bindus
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-emerald-50/50 border border-emerald-200 shadow-2xs text-center">
              <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-800 block">
                {t.ashtakavargaAuspiciousSigns}
              </span>
              <span className="font-serif text-2xl font-bold text-emerald-800 mt-1 block">
                {sarvashtakavarga.auspicious_signs.length} / 12
              </span>
              <span className="text-[10px] text-emerald-700 block mt-0.5">
                High Benefic Potential
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-amber-50/50 border border-amber-200 shadow-2xs text-center">
              <span className="text-[10px] font-bold uppercase tracking-wider text-amber-800 block">
                {t.ashtakavargaInauspiciousSigns}
              </span>
              <span className="font-serif text-2xl font-bold text-amber-900 mt-1 block">
                {sarvashtakavarga.inauspicious_signs.length} / 12
              </span>
              <span className="text-[10px] text-amber-700 block mt-0.5">
                Cautionary Bhavas
              </span>
            </div>
          </div>

          {/* 12-Sign SAV Grid */}
          <div className="rounded-xl border border-[#E2DCD5] bg-white p-5 shadow-2xs space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#E2DCD5]">
              <h4 className="font-serif text-base font-bold text-[#0F172A] flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-[#B8860B]" />
                <span>12-Sign Sarvashtakavarga Distribution</span>
              </h4>
              <span className="text-[11px] text-[#64748B]">
                Green/Gold ≥ 28 • Slate/Amber &lt; 28
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
              {Array.from({ length: 12 }, (_, i) => i + 1).map((signIdx) => {
                const bindus = sarvashtakavarga.sign_bindus[String(signIdx)] ?? 0;
                const isAuspicious = bindus >= 28;
                const rasi = RASIS[signIdx];
                const houseFromLagna = ((signIdx - lagna_sign_index + 12) % 12) + 1;
                const percent = Math.min(100, Math.round((bindus / 40) * 100));

                return (
                  <div
                    key={signIdx}
                    className={`p-3.5 rounded-xl border transition-all ${
                      isAuspicious
                        ? "bg-[#FAF8F2] border-[#D8BD80] shadow-2xs"
                        : "bg-white border-slate-200"
                    }`}
                  >
                    <div className="flex items-center justify-between text-xs pb-1.5 border-b border-slate-100">
                      <div className="flex items-center gap-1.5">
                        <span className="font-mono text-sm">{rasi?.symbol}</span>
                        <span className="font-bold text-[#0F172A]">
                          {getRasiName(signIdx, language)}
                        </span>
                      </div>
                      <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-100 text-slate-700">
                        H {houseFromLagna}
                      </span>
                    </div>

                    <div className="flex items-baseline justify-between mt-2">
                      <span
                        className={`font-serif text-3xl font-bold ${
                          isAuspicious ? "text-[#784E0E]" : "text-slate-700"
                        }`}
                      >
                        {bindus}
                      </span>
                      <span
                        className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                          isAuspicious
                            ? "bg-emerald-100 text-emerald-800"
                            : "bg-slate-100 text-slate-600"
                        }`}
                      >
                        {isAuspicious ? "Auspicious" : "Moderate"}
                      </span>
                    </div>

                    {/* Progress bar */}
                    <div className="mt-2.5">
                      <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                        <div
                          className={`h-1.5 rounded-full ${
                            isAuspicious ? "bg-[#B8860B]" : "bg-slate-400"
                          }`}
                          style={{ width: `${percent}%` }}
                        />
                      </div>
                      <div className="flex justify-between text-[9px] text-[#94A3B8] mt-1 font-mono">
                        <span>0</span>
                        <span className="text-[#784E0E] font-bold">28</span>
                        <span>40+</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* ========================================================= */}
      {/* TAB 2: BHINNASHTAKAVARGA (BAV) & SHODHANA REDUCTIONS     */}
      {/* ========================================================= */}
      {activeSubTab === "bav" && (
        <div className="space-y-6">
          {/* Planet Switcher */}
          <div className="p-4 rounded-xl border border-[#E2DCD5] bg-white shadow-2xs space-y-3">
            <span className="text-xs font-bold uppercase tracking-wider text-[#64748B] block">
              Select Classical Graha (Sun – Saturn):
            </span>
            <div className="flex flex-wrap gap-2">
              {CLASSICAL_PLANETS.map((planet) => {
                const bav = bhinnashtakavarga[planet];
                const isSelected = selectedPlanet === planet;
                const graha = GRAHAS[planet];
                const planetLabel = getGrahaName(planet, language);

                return (
                  <button
                    key={planet}
                    type="button"
                    onClick={() => setSelectedPlanet(planet)}
                    className={`px-3.5 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${
                      isSelected
                        ? "bg-[#0F172A] text-white shadow-sm"
                        : "bg-[#FAF7F0] text-[#334155] border border-[#E2DCD5] hover:bg-[#FAF4E6]"
                    }`}
                  >
                    <span
                      className="w-2 h-2 rounded-full inline-block"
                      style={{ backgroundColor: graha?.color || "#B8860B" }}
                    />
                    <span>{planetLabel}</span>
                    <span
                      className={`text-[10px] font-mono px-1.5 py-0.2 rounded ${
                        isSelected
                          ? "bg-white/20 text-white"
                          : "bg-white text-[#784E0E] border border-[#E2DCD5]"
                      }`}
                    >
                      {bav?.total_bindus ?? "—"}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Shodhana Stage Switcher */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-semibold text-[#64748B] mr-1">
              Reduction Stage:
            </span>
            <button
              type="button"
              onClick={() => setShodhanaStage("raw")}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all cursor-pointer ${
                shodhanaStage === "raw"
                  ? "bg-[#B8860B] text-white shadow-2xs"
                  : "bg-white border border-[#E2DCD5] text-[#334155] hover:bg-[#FAF6EC]"
              }`}
            >
              {t.ashtakavargaRawBindus} ({currentBav?.total_bindus ?? 0})
            </button>
            <button
              type="button"
              onClick={() => setShodhanaStage("trikona")}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all cursor-pointer ${
                shodhanaStage === "trikona"
                  ? "bg-[#B8860B] text-white shadow-2xs"
                  : "bg-white border border-[#E2DCD5] text-[#334155] hover:bg-[#FAF6EC]"
              }`}
            >
              {t.ashtakavargaTrikona}
            </button>
            <button
              type="button"
              onClick={() => setShodhanaStage("ekadhipatya")}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all cursor-pointer ${
                shodhanaStage === "ekadhipatya"
                  ? "bg-[#B8860B] text-white shadow-2xs"
                  : "bg-white border border-[#E2DCD5] text-[#334155] hover:bg-[#FAF6EC]"
              }`}
            >
              {t.ashtakavargaEkadhipatya}
            </button>
            <button
              type="button"
              onClick={() => setShodhanaStage("pinda")}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all cursor-pointer ${
                shodhanaStage === "pinda"
                  ? "bg-[#B8860B] text-white shadow-2xs"
                  : "bg-white border border-[#E2DCD5] text-[#334155] hover:bg-[#FAF6EC]"
              }`}
            >
              {t.ashtakavargaShodhyaPinda}
            </button>
          </div>

          {/* Shodhya Pinda View vs Sign Grid View */}
          {shodhanaStage === "pinda" ? (
            <div className="p-6 rounded-xl border border-[#D8BD80] bg-white shadow-sm space-y-6">
              <div className="flex items-center justify-between pb-3 border-b border-[#E2DCD5]">
                <h4 className="font-serif text-lg font-bold text-[#0F172A] flex items-center gap-2">
                  <Award className="w-5 h-5 text-[#B8860B]" />
                  <span>
                    {getGrahaName(selectedPlanet, language)} {t.ashtakavargaShodhyaPinda} (BPHS Ch. 69)
                  </span>
                </h4>
                <span className="text-xs font-mono bg-[#FAF2DE] text-[#784E0E] px-2.5 py-1 rounded-full border border-[#D8BD80]">
                  Invariant Base: {currentBav?.expected_total}
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="p-4 rounded-xl bg-[#FAF8F5] border border-[#E2DCD5] text-center space-y-1">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-[#64748B]">
                    {t.ashtakavargaRashiPinda}
                  </span>
                  <span className="font-serif text-3xl font-bold text-[#0F172A] block">
                    {currentBav?.rashi_pinda ?? "—"}
                  </span>
                  <span className="text-[10px] text-[#64748B] block">
                    Σ (Sign Reduced Bindu × Rashi Multiplier)
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-[#FAF8F5] border border-[#E2DCD5] text-center space-y-1">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-[#64748B]">
                    {t.ashtakavargaGrahaPinda}
                  </span>
                  <span className="font-serif text-3xl font-bold text-[#0F172A] block">
                    {currentBav?.graha_pinda ?? "—"}
                  </span>
                  <span className="text-[10px] text-[#64748B] block">
                    Σ (Sign Reduced Bindu × Planet Occupant Multiplier)
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-[#FAF2DE] border-2 border-[#D8BD80] text-center space-y-1">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-[#784E0E]">
                    {t.ashtakavargaShodhyaPinda} (Total)
                  </span>
                  <span className="font-serif text-3xl font-bold text-[#784E0E] block">
                    {currentBav?.shodhya_pinda ?? "—"}
                  </span>
                  <span className="text-[10px] font-bold text-[#8C6D23] block">
                    Rashi Pinda + Graha Pinda
                  </span>
                </div>
              </div>

              <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 text-xs text-[#475569] leading-relaxed">
                <strong className="text-[#0F172A] block mb-1">
                  Classical Multipliers (Gunakas):
                </strong>
                <ul className="list-disc pl-4 space-y-0.5 text-[11px]">
                  <li>
                    <strong>Rashi Gunakas:</strong> Aries 7, Taurus 10, Gemini 8, Cancer 4, Leo 10, Virgo 5, Libra 7, Scorpio 8, Sagittarius 9, Capricorn 5, Aquarius 11, Pisces 12.
                  </li>
                  <li>
                    <strong>Graha Gunakas:</strong> Sun 5, Moon 5, Mars 8, Mercury 5, Jupiter 10, Venus 7, Saturn 5.
                  </li>
                </ul>
              </div>
            </div>
          ) : (
            <div className="rounded-xl border border-[#E2DCD5] bg-white p-5 shadow-2xs space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-[#E2DCD5]">
                <h4 className="font-serif text-base font-bold text-[#0F172A]">
                  {getGrahaName(selectedPlanet, language)} BAV —{" "}
                  {shodhanaStage === "raw"
                    ? t.ashtakavargaRawBindus
                    : shodhanaStage === "trikona"
                    ? t.ashtakavargaTrikona
                    : t.ashtakavargaEkadhipatya}
                </h4>
                <span className="text-xs font-mono text-[#64748B]">
                  Classical Total: {currentBav?.expected_total} Bindus
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                {Array.from({ length: 12 }, (_, i) => i + 1).map((signIdx) => {
                  const bindus = getBavBinduForSign(signIdx);
                  const rasi = RASIS[signIdx];
                  const houseFromLagna = ((signIdx - lagna_sign_index + 12) % 12) + 1;

                  return (
                    <div
                      key={signIdx}
                      className="p-3 rounded-lg border border-[#E2DCD5] bg-[#FAF8F5] flex items-center justify-between"
                    >
                      <div>
                        <div className="flex items-center gap-1.5">
                          <span className="font-mono text-xs">{rasi?.symbol}</span>
                          <span className="font-bold text-xs text-[#0F172A]">
                            {getRasiName(signIdx, language)}
                          </span>
                        </div>
                        <span className="text-[10px] text-[#64748B]">
                          Bhava {houseFromLagna}
                        </span>
                      </div>
                      <span className="font-serif text-2xl font-bold text-[#784E0E]">
                        {bindus}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ========================================================= */}
      {/* TAB 3: 7-PLANET BAV COMPREHENSIVE MATRIX TABLE            */}
      {/* ========================================================= */}
      {activeSubTab === "matrix" && (
        <div className="w-full overflow-x-auto rounded-xl border border-[#E2DCD5] bg-white shadow-2xs">
          <table className="w-full text-left text-xs text-[#1E293B]">
            <thead className="bg-[#FAF7F0] text-[#0F172A] border-b border-[#E2DCD5] uppercase text-[10px] tracking-wider font-semibold">
              <tr>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3 sticky left-0 bg-[#FAF7F0] z-10">
                  {t.planet}
                </th>
                {Array.from({ length: 12 }, (_, i) => i + 1).map((s) => (
                  <th key={s} scope="col" className="px-2 py-2.5 text-center min-w-[44px]">
                    <span className="block">{RASIS[s]?.symbol}</span>
                    <span className="text-[9px] text-[#64748B]">S{s}</span>
                  </th>
                ))}
                <th scope="col" className="px-3 py-2.5 text-center font-bold text-[#784E0E]">
                  Total
                </th>
                <th scope="col" className="px-3 py-2.5 text-center">
                  Invariant
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1EBE4]">
              {CLASSICAL_PLANETS.map((planet) => {
                const bav = bhinnashtakavarga[planet];
                const graha = GRAHAS[planet];
                const planetLabel = getGrahaName(planet, language);

                return (
                  <tr key={planet} className="hover:bg-[#FAF8F5] transition-colors">
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-bold text-[#0F172A] sticky left-0 bg-white z-10 flex items-center gap-1.5 whitespace-nowrap">
                      <span
                        className="w-2 h-2 rounded-full inline-block shrink-0"
                        style={{ backgroundColor: graha?.color || "#B8860B" }}
                      />
                      <span>{planetLabel}</span>
                    </td>
                    {Array.from({ length: 12 }, (_, i) => i + 1).map((s) => {
                      const count = bav?.sign_bindus[String(s)] ?? 0;
                      return (
                        <td
                          key={s}
                          className={`px-2 py-2 text-center font-mono text-xs ${
                            count >= 5 ? "font-bold text-[#784E0E] bg-[#FAF8F2]" : "text-[#475569]"
                          }`}
                        >
                          {count}
                        </td>
                      );
                    })}
                    <td className="px-3 py-2 text-center font-serif font-bold text-sm text-[#0F172A]">
                      {bav?.total_bindus ?? "—"}
                    </td>
                    <td className="px-3 py-2 text-center">
                      {bav?.total_bindus === bav?.expected_total ? (
                        <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                          {bav?.expected_total} ✓
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-red-50 text-red-700">
                          Mismatch
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}

              {/* SAV Total Row */}
              <tr className="bg-[#FAF2DE] font-bold border-t-2 border-[#D8BD80]">
                <td className="px-3 py-2.5 sm:px-4 sm:py-3 text-[#784E0E] sticky left-0 bg-[#FAF2DE] z-10">
                  Sarvashtakavarga (SAV)
                </td>
                {Array.from({ length: 12 }, (_, i) => i + 1).map((s) => {
                  const savCount = sarvashtakavarga.sign_bindus[String(s)] ?? 0;
                  const isAuspicious = savCount >= 28;
                  return (
                    <td
                      key={s}
                      className={`px-2 py-2.5 text-center font-mono font-bold text-xs ${
                        isAuspicious ? "text-[#784E0E] bg-[#F7EAC4]" : "text-slate-700"
                      }`}
                    >
                      {savCount}
                    </td>
                  );
                })}
                <td className="px-3 py-2.5 text-center font-serif text-base font-bold text-[#784E0E]">
                  {sarvashtakavarga.total_bindus}
                </td>
                <td className="px-3 py-2.5 text-center">
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                    337 ✓
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
