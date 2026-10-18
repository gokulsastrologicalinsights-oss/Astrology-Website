"use client";

import React, { useState, useEffect } from "react";
import { KpResponse, DasaResponse, HoroscopeResponse } from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { getGrahaName, getRasiName, getLordName } from "@/lib/translations";
import { formatDms } from "@/lib/formatters";
import { KpEventAnalysisSection } from "./KpEventAnalysisSection";

interface KpSectionProps {
  kp?: KpResponse;
  dasa?: DasaResponse;
  horoscope?: HoroscopeResponse;
  savedHoroscopeId?: string;
}

function formatDate(isoStr?: string): string {
  if (!isoStr) return "—";
  return isoStr.split("T")[0];
}

function formatDays(days?: number): string {
  if (days === undefined || days === null) return "—";
  const y = Math.floor(days / 365.25);
  const remM = days % 365.25;
  const m = Math.floor(remM / 30.4375);
  const d = Math.round(remM % 30.4375);
  if (y > 0) return `${y}y ${m}m ${d}d`;
  if (m > 0) return `${m}m ${d}d`;
  return `${d}d`;
}

export function KpSection({ kp, dasa, horoscope, savedHoroscopeId }: KpSectionProps) {
  const { language, t } = useLanguage();
  const [activeSubTab, setActiveSubTab] = useState<
    "planets" | "cusps" | "significators" | "house_significators" | "ruling_planets" | "dasa" | "events"
  >(() => {
    if (typeof window !== "undefined" && window.location.hash === "#kp-events") {
      return "events";
    }
    return "planets";
  });

  useEffect(() => {
    const handleHash = () => {
      if (typeof window !== "undefined" && window.location.hash === "#kp-events") {
        setActiveSubTab("events");
        setTimeout(() => {
          const el = document.getElementById("kp-events");
          if (el) {
            el.scrollIntoView({ behavior: "smooth" });
          }
        }, 150);
      }
    };

    handleHash();
    window.addEventListener("hashchange", handleHash);
    return () => window.removeEventListener("hashchange", handleHash);
  }, []);

  if (!kp) {
    return (
      <div className="p-8 text-center bg-white rounded-lg border border-[#E2DCD5] text-[#64748B]">
        {t.notAvailableYet}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Sub Tabs */}
      <div className="flex border-b border-[#E2DCD5] gap-2 overflow-x-auto pb-1">
        <button
          type="button"
          onClick={() => setActiveSubTab("planets")}
          className={`px-3 py-1.5 text-xs sm:text-sm font-semibold rounded-md transition-colors whitespace-nowrap ${
            activeSubTab === "planets"
              ? "bg-[#B8860B] text-white"
              : "text-[#475569] hover:bg-[#FAF6EC]"
          }`}
        >
          {language === "ta" ? "கிரக உப-அதிபதிகள் (249)" : "Planetary Sub-Lords (249)"}
        </button>
        <button
          type="button"
          onClick={() => setActiveSubTab("cusps")}
          className={`px-3 py-1.5 text-xs sm:text-sm font-semibold rounded-md transition-colors whitespace-nowrap ${
            activeSubTab === "cusps"
              ? "bg-[#B8860B] text-white"
              : "text-[#475569] hover:bg-[#FAF6EC]"
          }`}
        >
          {language === "ta" ? "பாவக முனை ஆய்வு (1-12)" : "Cuspal Sub-Lords (1-12)"}
        </button>
        <button
          type="button"
          onClick={() => setActiveSubTab("significators")}
          className={`px-3 py-1.5 text-xs sm:text-sm font-semibold rounded-md transition-colors whitespace-nowrap ${
            activeSubTab === "significators"
              ? "bg-[#B8860B] text-white"
              : "text-[#475569] hover:bg-[#FAF6EC]"
          }`}
        >
          {language === "ta" ? "கிரக காரகத்துவங்கள்" : "Planetary Significators"}
        </button>
        <button
          type="button"
          onClick={() => setActiveSubTab("house_significators")}
          className={`px-3 py-1.5 text-xs sm:text-sm font-semibold rounded-md transition-colors whitespace-nowrap ${
            activeSubTab === "house_significators"
              ? "bg-[#B8860B] text-white"
              : "text-[#475569] hover:bg-[#FAF6EC]"
          }`}
        >
          {language === "ta" ? "பாவக காரகத்துவங்கள் (A-D)" : "House Significators (A-D)"}
        </button>
        <button
          type="button"
          onClick={() => setActiveSubTab("ruling_planets")}
          className={`px-3 py-1.5 text-xs sm:text-sm font-semibold rounded-md transition-colors whitespace-nowrap ${
            activeSubTab === "ruling_planets"
              ? "bg-[#B8860B] text-white"
              : "text-[#475569] hover:bg-[#FAF6EC]"
          }`}
        >
          {language === "ta" ? "ஆளும் கிரகங்கள் (RPs)" : "Ruling Planets (RPs)"}
        </button>
        <button
          type="button"
          onClick={() => setActiveSubTab("dasa")}
          className={`px-3 py-1.5 text-xs sm:text-sm font-semibold rounded-md transition-colors whitespace-nowrap ${
            activeSubTab === "dasa"
              ? "bg-[#B8860B] text-white"
              : "text-[#475569] hover:bg-[#FAF6EC]"
          }`}
        >
          {language === "ta" ? "5-நிலை தசா-புக்தி" : "5-Level Dasa"}
        </button>
        <button
          type="button"
          onClick={() => setActiveSubTab("events")}
          className={`px-3 py-1.5 text-xs sm:text-sm font-bold rounded-md transition-colors whitespace-nowrap flex items-center gap-1.5 ${
            activeSubTab === "events"
              ? "bg-emerald-600 text-white shadow-xs"
              : "text-[#475569] hover:bg-[#FAF6EC] hover:text-[#0F172A]"
          }`}
        >
          <span>✨</span>
          <span>{language === "ta" ? "KP நிகழ்வு பகுப்பாய்வு" : "KP Event Analysis"}</span>
        </button>
      </div>

      {/* 1. Planetary Sub Lords */}
      {activeSubTab === "planets" && (
        <div className="overflow-x-auto rounded-lg border border-[#E2DCD5] bg-white shadow-xs">
          <table className="w-full text-left text-xs sm:text-sm text-[#1E293B]">
            <thead className="bg-[#FAF7F0] text-[#0F172A] border-b border-[#E2DCD5] uppercase text-[11px] tracking-wider font-semibold">
              <tr>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.planet}</th>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.sign}</th>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.longitude}</th>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">
                  {language === "ta" ? "ராசி நாதன்" : "Sign Lord"}
                </th>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.starLord}</th>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.subLord}</th>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.subSubLord}</th>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.kpNumber}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1EBE4]">
              {kp.planetary_positions.map((p) => {
                const planetLabel = getGrahaName(p.planet, language);
                const rasiLabel = getRasiName(p.sign_index, language);

                return (
                  <tr key={p.planet} className="hover:bg-[#FAF8F5] transition-colors">
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-bold text-[#0F172A]">
                      {planetLabel}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 text-[#334155]">
                      {rasiLabel}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-mono text-xs text-[#64748B]">
                      {formatDms(p.longitude)}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5">
                      {getLordName(p.sign_lord, language)}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5">
                      {getLordName(p.star_lord, language)}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-semibold text-[#B8860B]">
                      {getLordName(p.sub_lord, language)}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 text-[#64748B]">
                      {getLordName(p.sub_sub_lord, language)}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-mono font-bold text-[#784E0E]">
                      {p.kp_number}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* 2. Cuspal Sub Lords */}
      {activeSubTab === "cusps" && (
        <div className="overflow-x-auto rounded-lg border border-[#E2DCD5] bg-white shadow-xs">
          <table className="w-full text-left text-xs sm:text-sm text-[#1E293B]">
            <thead className="bg-[#FAF7F0] text-[#0F172A] border-b border-[#E2DCD5] uppercase text-[11px] tracking-wider font-semibold">
              <tr>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.house}</th>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.cuspDegree}</th>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.sign}</th>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">
                  {language === "ta" ? "ராசி நாதன்" : "Sign Lord"}
                </th>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.starLord}</th>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.subLord}</th>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">
                  {language === "ta" ? "உப-உப நாதன்" : "Sub-Sub Lord"}
                </th>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.promise}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1EBE4]">
              {kp.cuspal_analysis.map((c) => {
                const rasiLabel = getRasiName(c.sign_index, language);

                return (
                  <tr key={`cusp-${c.house}`} className="hover:bg-[#FAF8F5] transition-colors">
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-bold text-[#0F172A]">
                      {language === "ta" ? `${c.house}ம் பாவம்` : `Cusp ${c.house}`}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-mono text-xs text-[#64748B]">
                      {formatDms(c.cusp_degree)}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 text-[#334155]">
                      {rasiLabel}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5">
                      {getLordName(c.sign_lord, language)}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5">
                      {getLordName(c.star_lord, language)}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-semibold text-[#B8860B]">
                      {getLordName(c.sub_lord, language)}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 text-[#64748B]">
                      {c.sub_sub_lord ? getLordName(c.sub_sub_lord, language) : "—"}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold ${
                          c.promise === "Positive"
                            ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                            : c.promise === "Negative"
                            ? "bg-rose-50 text-rose-700 border border-rose-200"
                            : "bg-amber-50 text-amber-700 border border-amber-200"
                        }`}
                      >
                        {c.promise}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* 3. 4-Tier Planetary Significators (Grah Nirdeshan) */}
      {activeSubTab === "significators" && (
        <div className="overflow-x-auto rounded-lg border border-[#E2DCD5] bg-white shadow-xs">
          <table className="w-full text-left text-xs sm:text-sm text-[#1E293B]">
            <thead className="bg-[#FAF7F0] text-[#0F172A] border-b border-[#E2DCD5] uppercase text-[11px] tracking-wider font-semibold">
              <tr>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.planet}</th>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">
                  {language === "ta" ? "குறிக்கும் பாவங்கள்" : "Signified Bhavas"}
                </th>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">
                  {language === "ta" ? "காரகத்துவ வலிமை வரிசை" : "Strength Breakdown"}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1EBE4]">
              {kp.significators.map((s) => {
                const planetLabel = getGrahaName(s.planet, language);

                return (
                  <tr key={`sig-${s.planet}`} className="hover:bg-[#FAF8F5] transition-colors">
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-bold text-[#0F172A]">
                      {planetLabel}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-mono text-sm text-[#B8860B] font-bold">
                      {s.signified_houses.length > 0
                        ? s.signified_houses.join(", ")
                        : "—"}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5">
                      <div className="flex flex-wrap gap-1.5">
                        {s.strength_order.map((entry, idx) => (
                          <span
                            key={idx}
                            className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] bg-[#FAF6EC] border border-[#E2DCD5] text-[#475569]"
                          >
                            <span className="font-semibold text-[#0F172A]">H{entry.house}</span>
                            <span className="text-[#8C6D23]">({entry.type})</span>
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* 4. 4-Tier House Significators (Bhaav Nirdeshan) */}
      {activeSubTab === "house_significators" && (
        <div className="overflow-x-auto rounded-lg border border-[#E2DCD5] bg-white shadow-xs">
          <table className="w-full text-left text-xs sm:text-sm text-[#1E293B]">
            <thead className="bg-[#FAF7F0] text-[#0F172A] border-b border-[#E2DCD5] uppercase text-[11px] tracking-wider font-semibold">
              <tr>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.house}</th>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">
                  {language === "ta" ? "பாவக நாதர்கள்" : "Cusp Lords (Sign/Star/Sub)"}
                </th>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">
                  <span className="text-[#059669]">Level A</span>
                  <span className="block text-[9px] font-normal text-[#64748B]">
                    {language === "ta" ? "அமர்ந்தவர் சாரத்தில்" : "In Occ Star"}
                  </span>
                </th>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">
                  <span className="text-[#2563EB]">Level B</span>
                  <span className="block text-[9px] font-normal text-[#64748B]">
                    {language === "ta" ? "அமர்ந்த கிரகங்கள்" : "Occupants"}
                  </span>
                </th>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">
                  <span className="text-[#D97706]">Level C</span>
                  <span className="block text-[9px] font-normal text-[#64748B]">
                    {language === "ta" ? "அதிபதி சாரத்தில்" : "In Lord Star"}
                  </span>
                </th>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">
                  <span className="text-[#DC2626]">Level D</span>
                  <span className="block text-[9px] font-normal text-[#64748B]">
                    {language === "ta" ? "பாவ அதிபதி" : "Sign Lord"}
                  </span>
                </th>
                <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">
                  {language === "ta" ? "அனைத்து காரகர்கள்" : "All Significators"}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1EBE4]">
              {(kp.house_significators || []).map((hs) => (
                <tr key={`house-sig-${hs.house}`} className="hover:bg-[#FAF8F5] transition-colors">
                  <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-bold text-[#0F172A]">
                    {language === "ta" ? `${hs.house}ம் பாவம்` : `House ${hs.house}`}
                  </td>
                  <td className="px-3 py-2 sm:px-4 sm:py-2.5 text-xs">
                    <span className="font-semibold text-[#334155]">{getLordName(hs.sign_lord, language)}</span>
                    {" / "}
                    <span className="text-[#64748B]">{getLordName(hs.star_lord, language)}</span>
                    {" / "}
                    <span className="font-semibold text-[#B8860B]">{getLordName(hs.sub_lord, language)}</span>
                  </td>
                  <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-medium text-[#059669]">
                    {hs.level_a.length > 0
                      ? hs.level_a.map((p) => getGrahaName(p, language)).join(", ")
                      : "—"}
                  </td>
                  <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-medium text-[#2563EB]">
                    {hs.level_b.length > 0
                      ? hs.level_b.map((p) => getGrahaName(p, language)).join(", ")
                      : "—"}
                  </td>
                  <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-medium text-[#D97706]">
                    {hs.level_c.length > 0
                      ? hs.level_c.map((p) => getGrahaName(p, language)).join(", ")
                      : "—"}
                  </td>
                  <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-medium text-[#DC2626]">
                    {hs.level_d.length > 0
                      ? hs.level_d.map((p) => getGrahaName(p, language)).join(", ")
                      : "—"}
                  </td>
                  <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-semibold text-[#0F172A]">
                    {hs.all_significators.length > 0
                      ? hs.all_significators.map((p) => getGrahaName(p, language)).join(", ")
                      : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* 5. Ruling Planets (RPs) */}
      {activeSubTab === "ruling_planets" && kp.ruling_planets && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {/* Day Lord Card */}
            <div className="p-4 rounded-lg border border-[#E2DCD5] bg-white shadow-xs">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-[#64748B]">
                {language === "ta" ? "கிழமை நாதன்" : "Day Lord"}
              </span>
              <p className="mt-1 text-lg font-bold text-[#B8860B]">
                {getGrahaName(kp.ruling_planets.day_lord, language)}
              </p>
            </div>

            {/* Lagna Rulers Card */}
            <div className="p-4 rounded-lg border border-[#E2DCD5] bg-white shadow-xs">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-[#64748B]">
                {language === "ta" ? "லக்ன அதிபதிகள்" : "Ascendant Lords"}
              </span>
              <div className="mt-2 space-y-1 text-xs">
                <div className="flex justify-between">
                  <span className="text-[#64748B]">{language === "ta" ? "ராசி:" : "Sign:"}</span>
                  <span className="font-semibold text-[#0F172A]">
                    {getGrahaName(kp.ruling_planets.ascendant_sign_lord, language)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#64748B]">{language === "ta" ? "நட்சத்திரம்:" : "Star:"}</span>
                  <span className="font-semibold text-[#0F172A]">
                    {getGrahaName(kp.ruling_planets.ascendant_star_lord, language)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#64748B]">{language === "ta" ? "உப-அதிபதி:" : "Sub:"}</span>
                  <span className="font-bold text-[#B8860B]">
                    {getGrahaName(kp.ruling_planets.ascendant_sub_lord, language)}
                  </span>
                </div>
              </div>
            </div>

            {/* Moon Rulers Card */}
            <div className="p-4 rounded-lg border border-[#E2DCD5] bg-white shadow-xs">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-[#64748B]">
                {language === "ta" ? "சந்திர அதிபதிகள்" : "Moon Lords"}
              </span>
              <div className="mt-2 space-y-1 text-xs">
                <div className="flex justify-between">
                  <span className="text-[#64748B]">{language === "ta" ? "ராசி:" : "Sign:"}</span>
                  <span className="font-semibold text-[#0F172A]">
                    {getGrahaName(kp.ruling_planets.moon_sign_lord, language)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#64748B]">{language === "ta" ? "நட்சத்திரம்:" : "Star:"}</span>
                  <span className="font-semibold text-[#0F172A]">
                    {getGrahaName(kp.ruling_planets.moon_star_lord, language)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#64748B]">{language === "ta" ? "உப-அதிபதி:" : "Sub:"}</span>
                  <span className="font-bold text-[#B8860B]">
                    {getGrahaName(kp.ruling_planets.moon_sub_lord, language)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* RPs Order Table */}
          <div className="rounded-lg border border-[#E2DCD5] bg-white shadow-xs p-4">
            <h4 className="text-xs sm:text-sm font-semibold text-[#0F172A] mb-3">
              {language === "ta" ? "ஆளும் கிரகங்களின் ஒருங்கிணைந்த வரிசை" : "Consolidated Ruling Planets Sequence"}
            </h4>
            <div className="flex flex-wrap gap-2">
              {kp.ruling_planets.details.map((item, idx) => (
                <div
                  key={idx}
                  className="px-3 py-1.5 rounded-md bg-[#FAF6EC] border border-[#E2DCD5] text-xs"
                >
                  <span className="font-bold text-[#0F172A]">{getGrahaName(item.planet, language)}</span>
                  <span className="text-[#64748B] ml-1.5 text-[10px]">({item.role})</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 6. 5-Level KP Vimshottari Timeline */}
      {activeSubTab === "dasa" && kp.dasa_hierarchy && (
        <div className="space-y-4">
          {/* Birth Balance Overview */}
          <div className="rounded-lg border border-[#E2DCD5] bg-[#FAF8F5] p-4 shadow-xs">
            <h4 className="text-xs sm:text-sm font-semibold text-[#0F172A] mb-2">
              {language === "ta" ? "பிறப்பு தசா இருப்பு (5 நிலைகள்)" : "Birth Dasa Balance (5 Levels)"}
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs">
              <div className="p-2.5 rounded bg-white border border-[#E2DCD5]">
                <span className="text-[10px] text-[#64748B] uppercase block">
                  {language === "ta" ? "மகா தசா" : "Mahadasha (L1)"}
                </span>
                <span className="font-bold text-sm text-[#0F172A]">
                  {getGrahaName(kp.dasa_hierarchy.mahadasha_lord, language)}
                </span>
                <span className="text-[10px] text-[#64748B] block mt-0.5">
                  {kp.dasa_hierarchy.mahadasha_balance_years.toFixed(2)}y ({formatDays(kp.dasa_hierarchy.mahadasha_balance_days)})
                </span>
              </div>
              <div className="p-2.5 rounded bg-white border border-[#E2DCD5]">
                <span className="text-[10px] text-[#64748B] uppercase block">
                  {language === "ta" ? "அந்தர்தசா / புக்தி" : "Antardasha (L2)"}
                </span>
                <span className="font-bold text-sm text-[#0F172A]">
                  {getGrahaName(kp.dasa_hierarchy.antardasha_lord, language)}
                </span>
                <span className="text-[10px] text-[#64748B] block mt-0.5">
                  {formatDays(kp.dasa_hierarchy.antardasha_balance_days)}
                </span>
              </div>
              <div className="p-2.5 rounded bg-white border border-[#E2DCD5]">
                <span className="text-[10px] text-[#64748B] uppercase block">
                  {language === "ta" ? "பிரத்யந்தர்தசா / அந்தரம்" : "Pratyantar (L3)"}
                </span>
                <span className="font-bold text-sm text-[#0F172A]">
                  {getGrahaName(kp.dasa_hierarchy.pratyantardasha_lord, language)}
                </span>
                <span className="text-[10px] text-[#64748B] block mt-0.5">
                  {formatDays(kp.dasa_hierarchy.pratyantardasha_balance_days)}
                </span>
              </div>
              <div className="p-2.5 rounded bg-white border border-[#E2DCD5]">
                <span className="text-[10px] text-[#64748B] uppercase block">
                  {language === "ta" ? "சூட்சுமதசா / சூட்சுமம்" : "Sookshma (L4)"}
                </span>
                <span className="font-bold text-sm text-[#0F172A]">
                  {getGrahaName(kp.dasa_hierarchy.sookshmadasha_lord, language)}
                </span>
                <span className="text-[10px] text-[#64748B] block mt-0.5">
                  {formatDays(kp.dasa_hierarchy.sookshmadasha_balance_days)}
                </span>
              </div>
              <div className="p-2.5 rounded bg-white border border-[#E2DCD5]">
                <span className="text-[10px] text-[#64748B] uppercase block">
                  {language === "ta" ? "பிராணதசா / பிராணன்" : "Prana (L5)"}
                </span>
                <span className="font-bold text-sm text-[#0F172A]">
                  {getGrahaName(kp.dasa_hierarchy.pranadasha_lord, language)}
                </span>
                <span className="text-[10px] text-[#64748B] block mt-0.5">
                  {formatDays(kp.dasa_hierarchy.pranadasha_balance_days)}
                </span>
              </div>
            </div>
          </div>

          {/* Active 5-Level Periods Hierarchy Table */}
          <div className="overflow-x-auto rounded-lg border border-[#E2DCD5] bg-white shadow-xs">
            <div className="p-3 bg-[#FAF7F0] border-b border-[#E2DCD5] font-semibold text-xs text-[#0F172A]">
              {language === "ta" ? "பிறப்பு கணத்தில் இயங்கும் 5-நிலை தசா அடுக்கு" : "Active 5-Level Dasa Hierarchy at Birth Moment"}
            </div>
            <table className="w-full text-left text-xs sm:text-sm text-[#1E293B]">
              <thead className="bg-[#FAF7F0] text-[#0F172A] border-b border-[#E2DCD5] uppercase text-[11px] tracking-wider font-semibold">
                <tr>
                  <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">
                    {language === "ta" ? "நிலை" : "Level"}
                  </th>
                  <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">
                    {language === "ta" ? "தசா பெயர்" : "Period Name"}
                  </th>
                  <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">
                    {language === "ta" ? "அதிபதி" : "Lord"}
                  </th>
                  <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">
                    {language === "ta" ? "தொடக்க தேதி" : "Start Date"}
                  </th>
                  <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">
                    {language === "ta" ? "முடிவு தேதி" : "End Date"}
                  </th>
                  <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">
                    {language === "ta" ? "கால அளவு" : "Duration"}
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F1EBE4]">
                {kp.dasa_hierarchy.current_periods.map((p) => (
                  <tr key={`cur-${p.level}`} className="hover:bg-[#FAF8F5] transition-colors">
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-bold text-[#B8860B]">
                      L{p.level}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-medium text-[#0F172A]">
                      {p.level_name} ({p.vedic_name})
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-bold text-[#0F172A]">
                      {getGrahaName(p.lord, language)}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-mono text-xs text-[#64748B]">
                      {formatDate(p.start_date)}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-mono text-xs text-[#64748B]">
                      {formatDate(p.end_date)}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 text-xs text-[#334155]">
                      {formatDays(p.duration_days)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mahadasha Lifetime Sequence */}
          <div className="overflow-x-auto rounded-lg border border-[#E2DCD5] bg-white shadow-xs">
            <div className="p-3 bg-[#FAF7F0] border-b border-[#E2DCD5] font-semibold text-xs text-[#0F172A]">
              {language === "ta" ? "வாழ்நாள் மகா தசா வரிசை (120 ஆண்டுகள்)" : "Lifetime Mahadasha Sequence (120 Years)"}
            </div>
            <table className="w-full text-left text-xs sm:text-sm text-[#1E293B]">
              <thead className="bg-[#FAF7F0] text-[#0F172A] border-b border-[#E2DCD5] uppercase text-[11px] tracking-wider font-semibold">
                <tr>
                  <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">#</th>
                  <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">{t.planet}</th>
                  <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">
                    {language === "ta" ? "தொடக்க தேதி" : "Start Date"}
                  </th>
                  <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">
                    {language === "ta" ? "முடிவு தேதி" : "End Date"}
                  </th>
                  <th scope="col" className="px-3 py-2.5 sm:px-4 sm:py-3">
                    {language === "ta" ? "கால அளவு" : "Duration"}
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F1EBE4]">
                {kp.dasa_hierarchy.mahadashas.map((md, idx) => (
                  <tr key={`md-${idx}`} className="hover:bg-[#FAF8F5] transition-colors">
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-mono text-xs text-[#64748B]">
                      {idx + 1}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-bold text-[#0F172A]">
                      {getGrahaName(md.lord, language)}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-mono text-xs text-[#64748B]">
                      {formatDate(md.start_date)}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 font-mono text-xs text-[#64748B]">
                      {formatDate(md.end_date)}
                    </td>
                    <td className="px-3 py-2 sm:px-4 sm:py-2.5 text-xs text-[#334155]">
                      {formatDays(md.duration_days)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 7. KP Event Analysis */}
      {activeSubTab === "events" && (
        <div id="kp-events" className="scroll-mt-6">
          <KpEventAnalysisSection
            kp={kp}
            dasa={dasa}
            horoscope={horoscope}
            savedHoroscopeId={savedHoroscopeId}
          />
        </div>
      )}
    </div>
  );
}
