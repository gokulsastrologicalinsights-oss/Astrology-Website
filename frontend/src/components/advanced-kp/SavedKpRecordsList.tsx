"use client";

import React, { useState, useEffect } from "react";
import { SavedKpChartRecord } from "@/lib/types";
import { listSavedKpCharts, deleteSavedKpChart } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import {
  FolderOpen,
  Trash2,
  Calendar,
  Clock,
  MapPin,
  HelpCircle,
  Compass,
  AlertCircle,
  RefreshCw,
} from "lucide-react";

interface SavedKpRecordsListProps {
  onOpenRecord: (record: SavedKpChartRecord) => void;
  language: "en" | "ta";
  refreshTrigger?: number;
}

export function SavedKpRecordsList({
  onOpenRecord,
  language,
  refreshTrigger,
}: SavedKpRecordsListProps) {
  const { session } = useAuth();
  const [records, setRecords] = useState<SavedKpChartRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>("all");
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchRecords = async () => {
    if (!session?.access_token) return;
    setLoading(true);
    setError(null);
    try {
      const typeParam = filterType === "all" ? undefined : filterType;
      const res = await listSavedKpCharts(session.access_token, typeParam, 50, 0);
      setRecords(res.charts || []);
    } catch (err: any) {
      setError(err?.message || "Failed to load saved KP charts.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, [session?.access_token, filterType, refreshTrigger]);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!session?.access_token) return;
    const confirmMsg =
      language === "ta"
        ? "இந்த சேமிக்கப்பட்ட ஜாதகத்தை நிச்சயமாக நீக்க விரும்புகிறீர்களா? (வரிசை எண் மாறாது)"
        : "Are you sure you want to delete this saved record? (Sequential record numbers will be preserved)";
    if (!window.confirm(confirmMsg)) return;

    setDeletingId(id);
    try {
      await deleteSavedKpChart(session.access_token, id);
      setRecords((prev) => prev.filter((r) => r.id !== id));
    } catch (err: any) {
      alert(err?.message || "Failed to delete chart.");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-4">
      {/* Filter and Refresh Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-xl bg-white border border-[#DDE5F0] shadow-xs">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setFilterType("all")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              filterType === "all"
                ? "bg-[#102A4C] text-white"
                : "bg-white border border-[#DDE5F0] text-[#475569] hover:bg-[#FAF6EC]"
            }`}
          >
            {language === "ta" ? "அனைத்தும்" : "All Records"}
          </button>
          <button
            type="button"
            onClick={() => setFilterType("natal")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              filterType === "natal"
                ? "bg-[#B8862B] text-white"
                : "bg-white border border-[#DDE5F0] text-[#475569] hover:bg-[#FAF6EC]"
            }`}
          >
            {language === "ta" ? "பிறப்பு ஜாதகம் (Natal)" : "Natal KP"}
          </button>
          <button
            type="button"
            onClick={() => setFilterType("horary")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              filterType === "horary"
                ? "bg-[#3478F6] text-white"
                : "bg-white border border-[#DDE5F0] text-[#475569] hover:bg-[#FAF6EC]"
            }`}
          >
            {language === "ta" ? "பிரஸ்னம் (Horary)" : "Horary Prashna"}
          </button>
        </div>

        <button
          type="button"
          onClick={fetchRecords}
          disabled={loading}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-[#52667E] hover:bg-[#F8FAFC] transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          <span>{language === "ta" ? "புதுப்பி" : "Refresh"}</span>
        </button>
      </div>

      {error && (
        <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="p-12 text-center text-xs text-[#52667E] bg-white rounded-xl border border-[#DDE5F0]">
          <div className="inline-block animate-spin w-5 h-5 border-2 border-[#B8862B] border-t-transparent rounded-full mb-2" />
          <p>{language === "ta" ? "சேமிக்கப்பட்ட பதிவுகள் ஏற்றப்படுகின்றன..." : "Loading saved KP charts..."}</p>
        </div>
      ) : records.length === 0 ? (
        <div className="p-10 text-center bg-white rounded-xl border border-dashed border-[#DDE5F0] text-xs text-[#64748B] space-y-2">
          <FolderOpen className="w-8 h-8 text-[#94A3B8] mx-auto" />
          <p>
            {language === "ta"
              ? "சேமிக்கப்பட்ட KP ஜாதகங்கள் எதுவும் இல்லை."
              : "No saved Advanced KP charts found."}
          </p>
          <p className="text-[11px] text-[#94A3B8]">
            {language === "ta"
              ? "பிறப்பு ஜாதகம் அல்லது பிரஸ்னத்தை கணக்கிட்டு 'சேமி' பொத்தானை அழுத்தவும்."
              : "Compute a Natal or Horary Prashna chart and click Save to store records here."}
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-[#DDE5F0] bg-white shadow-xs">
          <table className="min-w-full divide-y divide-[#E2DCD5] text-xs sm:text-sm">
            <thead className="bg-[#F8FAFC] text-[#475569] font-semibold">
              <tr>
                <th className="px-3 py-3 text-center w-14">#</th>
                <th className="px-3 py-3 text-left">
                  {language === "ta" ? "வகை" : "Type"}
                </th>
                <th className="px-3 py-3 text-left">
                  {language === "ta" ? "தலைப்பு / குறிப்பு" : "Title / Label"}
                </th>
                <th className="px-3 py-3 text-left">
                  {language === "ta" ? "தேதி & நேரம்" : "Date & Time"}
                </th>
                <th className="px-3 py-3 text-left">
                  {language === "ta" ? "இடம்" : "Location"}
                </th>
                <th className="px-3 py-3 text-right">
                  {language === "ta" ? "செயல்கள்" : "Actions"}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1F5F9] text-[#1E293B]">
              {records.map((r) => {
                const isHorary = r.chart_type === "horary";
                const dateDisplay = isHorary
                  ? `${r.question_date || ""} ${r.question_time || ""}`
                  : `${r.birth_date || ""} ${r.birth_time || ""}`;

                return (
                  <tr
                    key={r.id}
                    onClick={() => onOpenRecord(r)}
                    className="hover:bg-[#FAF6EC]/60 transition-colors cursor-pointer"
                  >
                    <td className="px-3 py-3 text-center font-bold text-[#102A4C]">
                      <span className="w-7 h-7 rounded-md bg-[#FAF2DE] border border-[#D8BD80] text-[#8C6D23] font-bold text-xs flex items-center justify-center mx-auto">
                        #{r.display_number}
                      </span>
                    </td>
                    <td className="px-3 py-3 whitespace-nowrap">
                      {isHorary ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold bg-[#EBF2FE] text-[#2563EB] border border-[#BFDBFE]">
                          <HelpCircle className="w-3 h-3" />
                          <span>Horary #{r.horary_number}</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
                          <Compass className="w-3 h-3" />
                          <span>Natal KP</span>
                        </span>
                      )}
                    </td>
                    <td className="px-3 py-3 font-semibold text-[#102A4C] whitespace-nowrap">
                      {r.title}
                    </td>
                    <td className="px-3 py-3 whitespace-nowrap text-xs text-[#52667E] font-mono">
                      {dateDisplay || "—"}
                    </td>
                    <td className="px-3 py-3 whitespace-nowrap text-xs text-[#52667E]">
                      {r.location_name}
                    </td>
                    <td className="px-3 py-3 text-right whitespace-nowrap">
                      <div className="flex items-center justify-end gap-1.5" onClick={(e) => e.stopPropagation()}>
                        <button
                          type="button"
                          onClick={() => onOpenRecord(r)}
                          className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-[#102A4C] text-white hover:bg-[#1E3A61] transition-colors"
                        >
                          {language === "ta" ? "திறக்க" : "Open"}
                        </button>
                        <button
                          type="button"
                          disabled={deletingId === r.id}
                          onClick={(e) => handleDelete(r.id, e)}
                          className="p-1 rounded-lg text-rose-600 hover:bg-rose-50 transition-colors"
                          title="Delete saved chart"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
