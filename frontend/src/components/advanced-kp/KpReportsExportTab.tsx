"use client";

import React from "react";
import { KpResponse, HoraryKpResponse } from "@/lib/types";
import { Printer, Download, FileText, CheckCircle } from "lucide-react";
import { formatDms } from "@/lib/formatters";

interface KpReportsExportTabProps {
  data: KpResponse | HoraryKpResponse | null;
  chartType: "natal" | "horary";
  title?: string;
  language: "en" | "ta";
}

export function KpReportsExportTab({
  data,
  chartType,
  title,
  language,
}: KpReportsExportTabProps) {
  if (!data) {
    return (
      <div className="p-8 text-center bg-white rounded-xl border border-[#E2DCD5] text-[#64748B]">
        {language === "ta"
          ? "அறிக்கையை உருவாக்க முதலில் ஒரு ஜாதகத்தை கணக்கிடவும்."
          : "Please run a calculation to generate report and export options."}
      </div>
    );
  }

  const handlePrint = () => {
    window.print();
  };

  const handleExportJson = () => {
    const jsonStr = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `KP_Report_${chartType}_${new Date().toISOString().split("T")[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleExportCsv = () => {
    const rows = [
      ["Type", "Entity", "Degree", "Sign", "SignLord", "StarLord", "SubLord", "SubSubLord", "KP_Number_or_Promise"],
    ];

    // Planets
    data.planetary_positions.forEach((p) => {
      rows.push([
        "Planet",
        p.planet,
        p.longitude.toFixed(4),
        p.sign_name,
        p.sign_lord,
        p.star_lord,
        p.sub_lord,
        p.sub_sub_lord,
        `#${p.kp_number}`,
      ]);
    });

    // Cusps
    data.cuspal_analysis.forEach((c) => {
      rows.push([
        "Cusp",
        `House ${c.house}`,
        c.cusp_degree.toFixed(4),
        c.sign_name,
        c.sign_lord,
        c.star_lord,
        c.sub_lord,
        c.sub_sub_lord || "",
        c.promise,
      ]);
    });

    const csvContent =
      "data:text/csv;charset=utf-8," +
      rows.map((e) => e.map((val) => `"${val}"`).join(",")).join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute(
      "download",
      `KP_Planets_Cusps_${chartType}_${new Date().toISOString().split("T")[0]}.csv`
    );
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Export Action Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-xl bg-white border border-[#DDE5F0] shadow-xs">
        <div>
          <h3 className="font-serif text-base font-bold text-[#102A4C]">
            {language === "ta" ? "அறிக்கை & ஏற்றுமதி கருவிகள்" : "Detailed Report & Export Tools"}
          </h3>
          <p className="text-xs text-[#52667E]">
            Print-friendly verification report with certified ephemeris metadata and settings.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={handleExportCsv}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold bg-white border border-[#DDE5F0] text-[#102A4C] hover:bg-[#FAF6EC] transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-emerald-600" />
            <span>Export CSV</span>
          </button>

          <button
            type="button"
            onClick={handleExportJson}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold bg-white border border-[#DDE5F0] text-[#102A4C] hover:bg-[#FAF6EC] transition-colors"
          >
            <FileText className="w-3.5 h-3.5 text-[#3478F6]" />
            <span>Export JSON</span>
          </button>

          <button
            type="button"
            onClick={handlePrint}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-bold text-white bg-[#B8862B] hover:bg-[#996515] transition-colors shadow-2xs"
          >
            <Printer className="w-3.5 h-3.5" />
            <span>Print Report / PDF</span>
          </button>
        </div>
      </div>

      {/* Printable Report Preview */}
      <div className="p-8 rounded-2xl border border-[#DDE5F0] bg-white shadow-sm space-y-6 print:border-none print:shadow-none print:p-0">
        {/* Report Header */}
        <div className="border-b-2 border-[#102A4C] pb-4 flex items-start justify-between">
          <div>
            <h2 className="font-serif text-2xl font-bold text-[#102A4C]">
              Gokul&apos;s Astrological Insights
            </h2>
            <div className="text-sm font-semibold text-[#B8862B] mt-0.5">
              Advanced Krishnamurti Paddhati (KP) Astrology Report
            </div>
            <div className="text-xs text-[#64748B] mt-1">
              Title: <strong>{title || (chartType === "horary" ? "Horary Prashna Analysis" : "Natal KP Chart")}</strong>
            </div>
          </div>
          <div className="text-right text-xs text-[#52667E] space-y-0.5">
            <div>Generated: {new Date().toLocaleDateString()}</div>
            <div>Engine: <strong>{data.metadata.engine}</strong></div>
            <div>Ayanamsa: <strong>{data.metadata.ayanamsa_name} ({data.metadata.ayanamsa_deg.toFixed(4)}°)</strong></div>
            <div>House System: <strong>{data.metadata.house_system_name}</strong></div>
          </div>
        </div>

        {/* Location & Time Coordinates */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] text-xs">
          <div>
            <span className="text-[#64748B] block">Latitude:</span>
            <strong className="text-[#102A4C]">{data.metadata.coordinates?.latitude ?? "—"}°</strong>
          </div>
          <div>
            <span className="text-[#64748B] block">Longitude:</span>
            <strong className="text-[#102A4C]">{data.metadata.coordinates?.longitude ?? "—"}°</strong>
          </div>
          <div>
            <span className="text-[#64748B] block">Timezone:</span>
            <strong className="text-[#102A4C]">{data.metadata.local_timezone}</strong>
          </div>
          <div>
            <span className="text-[#64748B] block">Julian Day (UT1):</span>
            <strong className="text-[#102A4C] font-mono">{data.metadata.julian_day_ut1.toFixed(4)}</strong>
          </div>
        </div>

        {/* 9 Grahas Table */}
        <div className="space-y-2">
          <h4 className="font-serif text-sm font-bold text-[#102A4C] uppercase tracking-wider">
            Planetary Positions (9 Grahas - Sidereal KP Subdivision)
          </h4>
          <div className="overflow-x-auto rounded-lg border border-[#E2DCD5]">
            <table className="min-w-full divide-y divide-[#E2DCD5] text-xs">
              <thead className="bg-[#F8FAFC] font-semibold text-[#475569]">
                <tr>
                  <th className="px-2.5 py-2 text-left">Planet</th>
                  <th className="px-2.5 py-2 text-left">Sign</th>
                  <th className="px-2.5 py-2 text-left">Longitude</th>
                  <th className="px-2.5 py-2 text-left">Sign Lord</th>
                  <th className="px-2.5 py-2 text-left">Star Lord</th>
                  <th className="px-2.5 py-2 text-left">Sub-Lord</th>
                  <th className="px-2.5 py-2 text-left">Sub-Sub</th>
                  <th className="px-2.5 py-2 text-center">KP #</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F1F5F9]">
                {data.planetary_positions.map((p) => (
                  <tr key={p.planet}>
                    <td className="px-2.5 py-1.5 font-bold text-[#102A4C]">{p.planet}</td>
                    <td className="px-2.5 py-1.5">{p.sign_name}</td>
                    <td className="px-2.5 py-1.5 font-mono">{formatDms(p.longitude % 30.0)}</td>
                    <td className="px-2.5 py-1.5">{p.sign_lord}</td>
                    <td className="px-2.5 py-1.5">{p.star_lord}</td>
                    <td className="px-2.5 py-1.5 font-bold text-[#8C6D23]">{p.sub_lord}</td>
                    <td className="px-2.5 py-1.5 text-blue-700">{p.sub_sub_lord}</td>
                    <td className="px-2.5 py-1.5 text-center font-bold text-emerald-700">#{p.kp_number}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* 12 Cusps Table */}
        <div className="space-y-2">
          <h4 className="font-serif text-sm font-bold text-[#102A4C] uppercase tracking-wider">
            12 Placidus House Cusps &amp; Cuspal Sub-Lord Arbiter
          </h4>
          <div className="overflow-x-auto rounded-lg border border-[#E2DCD5]">
            <table className="min-w-full divide-y divide-[#E2DCD5] text-xs">
              <thead className="bg-[#F8FAFC] font-semibold text-[#475569]">
                <tr>
                  <th className="px-2.5 py-2 text-center w-12">Cusp</th>
                  <th className="px-2.5 py-2 text-left">Sign</th>
                  <th className="px-2.5 py-2 text-left">Degree</th>
                  <th className="px-2.5 py-2 text-left">Sign Lord</th>
                  <th className="px-2.5 py-2 text-left">Star Lord</th>
                  <th className="px-2.5 py-2 text-left">Sub-Lord (CSL)</th>
                  <th className="px-2.5 py-2 text-center">Promise</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F1F5F9]">
                {data.cuspal_analysis.map((c) => (
                  <tr key={c.house}>
                    <td className="px-2.5 py-1.5 text-center font-bold">{c.house}</td>
                    <td className="px-2.5 py-1.5">{c.sign_name}</td>
                    <td className="px-2.5 py-1.5 font-mono">{formatDms(c.cusp_degree % 30.0)}</td>
                    <td className="px-2.5 py-1.5">{c.sign_lord}</td>
                    <td className="px-2.5 py-1.5">{c.star_lord}</td>
                    <td className="px-2.5 py-1.5 font-bold text-[#8C6D23]">{c.sub_lord}</td>
                    <td className="px-2.5 py-1.5 text-center font-bold text-xs">{c.promise}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Engine Footnotes */}
        <div className="pt-4 border-t border-[#F1F5F9] text-[11px] text-[#64748B] space-y-1">
          {data.metadata.notes?.map((n, i) => (
            <div key={i} className="flex items-start gap-1.5">
              <CheckCircle className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
              <span>{n}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
