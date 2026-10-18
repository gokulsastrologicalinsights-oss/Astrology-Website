"use client";

import React from "react";
import { KpCuspDetail } from "@/lib/types";
import { formatDms } from "@/lib/formatters";
import { getRasiName, getLordName } from "@/lib/translations";

interface KpCuspAnalysisTabProps {
  cusps: KpCuspDetail[];
  language: "en" | "ta";
}

export function KpCuspAnalysisTab({ cusps, language }: KpCuspAnalysisTabProps) {
  if (!cusps || cusps.length === 0) {
    return (
      <div className="p-8 text-center bg-white rounded-xl border border-[#E2DCD5] text-[#64748B]">
        {language === "ta" ? "பாவக முனைகள் கிடைக்கவில்லை." : "Cuspal details not available."}
      </div>
    );
  }

  const getPromiseBadge = (promise: string) => {
    switch (promise) {
      case "Positive":
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
            {language === "ta" ? "சாதகம் (Positive)" : "Positive"}
          </span>
        );
      case "Negative":
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200">
            {language === "ta" ? "பாதகம் (Negative)" : "Negative"}
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200">
            {language === "ta" ? "கலப்பு (Mixed)" : "Mixed"}
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Overview Banner */}
      <div className="p-4 rounded-xl bg-[#FAF6EC] border border-[#D8BD80] text-xs text-[#102A4C] leading-relaxed">
        <p className="font-bold text-[#8C6D23] mb-1">
          {language === "ta"
            ? "கே.பி. பாவக முனை உப-அதிபதி தத்துவம் (Cuspal Sub-Lord Principle)"
            : "KP Cuspal Sub-Lord (CSL) Principle:"}
        </p>
        <p>
          {language === "ta"
            ? "ஒரு பாவகத்தின் பலன் நடைபெறுமா என்பதை அந்த பாவகத்தின் உப-அதிபதி (CSL) மற்றும் அவர் நின்ற நட்சத்திராதிபதியின் காரகத்துவங்கள் தீர்மானிக்கின்றன."
            : "In Krishnamurti Paddhati, the Cuspal Sub-Lord (CSL) is the final arbiter of a house's promise. A matter fructifies if the CSL signifies favorable houses without connecting to obstructing houses (6, 8, 12)."}
        </p>
      </div>

      {/* Cusps Table */}
      <div className="overflow-x-auto rounded-xl border border-[#E2DCD5] shadow-xs bg-white">
        <table className="min-w-full divide-y divide-[#E2DCD5] text-xs sm:text-sm">
          <thead className="bg-[#F8FAFC] text-[#475569] font-semibold">
            <tr>
              <th className="px-3 py-3 text-center w-14">
                {language === "ta" ? "பாவகம்" : "Cusp"}
              </th>
              <th className="px-3 py-3 text-left">
                {language === "ta" ? "முனை பாகை" : "Degree (Sign)"}
              </th>
              <th className="px-3 py-3 text-left">
                {language === "ta" ? "ராசி அதிபதி" : "Sign Lord"}
              </th>
              <th className="px-3 py-3 text-left">
                {language === "ta" ? "நட்சத்திர அதிபதி" : "Star Lord"}
              </th>
              <th className="px-3 py-3 text-left">
                <span className="text-[#B8860B] font-bold">
                  {language === "ta" ? "உப-அதிபதி (CSL)" : "Sub-Lord (CSL)"}
                </span>
              </th>
              <th className="px-3 py-3 text-left">
                <span className="text-[#3478F6] font-bold">
                  {language === "ta" ? "உப-உப" : "Sub-Sub"}
                </span>
              </th>
              <th className="px-3 py-3 text-center">
                {language === "ta" ? "பாவக உறுதிப்பாடு" : "Cuspal Promise"}
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#F1F5F9] text-[#1E293B]">
            {cusps.map((c) => {
              const signDeg = c.cusp_degree % 30.0;
              return (
                <tr key={c.house} className="hover:bg-[#FAF6EC]/60 transition-colors">
                  <td className="px-3 py-2.5 text-center font-bold text-[#102A4C]">
                    <span className="w-7 h-7 rounded-full bg-[#FAF2DE] border border-[#D8BD80] text-[#8C6D23] flex items-center justify-center mx-auto text-xs">
                      {c.house}
                    </span>
                  </td>
                  <td className="px-3 py-2.5 whitespace-nowrap font-mono text-xs">
                    {formatDms(signDeg)} in {getRasiName(c.sign_name, language)}
                  </td>
                  <td className="px-3 py-2.5 whitespace-nowrap">
                    {getLordName(c.sign_lord, language)}
                  </td>
                  <td className="px-3 py-2.5 whitespace-nowrap">
                    {getLordName(c.star_lord, language)}
                  </td>
                  <td className="px-3 py-2.5 whitespace-nowrap">
                    <span className="inline-flex items-center px-2 py-0.5 rounded-md font-bold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
                      {getLordName(c.sub_lord, language)}
                    </span>
                  </td>
                  <td className="px-3 py-2.5 whitespace-nowrap">
                    <span className="inline-flex items-center px-2 py-0.5 rounded-md font-semibold bg-[#EBF2FE] text-[#2563EB] border border-[#BFDBFE]">
                      {getLordName(c.sub_sub_lord || "—", language)}
                    </span>
                  </td>
                  <td className="px-3 py-2.5 text-center whitespace-nowrap">
                    {getPromiseBadge(c.promise)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
