"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  SavedMarriageReportSummary,
  SavedMarriageReportDetail,
  UpdateMarriageReportMetadataRequest,
} from "@/lib/types";
import {
  listSavedMarriageCompatibilityReports,
  getSavedMarriageCompatibilityReport,
  updateSavedMarriageCompatibilityReportMetadata,
  deleteSavedMarriageCompatibilityReport,
} from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import {
  FolderOpen,
  Trash2,
  Edit2,
  Calendar,
  HeartHandshake,
  CheckCircle2,
  AlertTriangle,
  ShieldAlert,
  HelpCircle,
  AlertCircle,
  RefreshCw,
  Clock,
  User,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Lock,
  X,
  Save,
} from "lucide-react";

interface SavedMarriageReportsListProps {
  onOpenReport: (report: SavedMarriageReportDetail) => void;
  language: "en" | "ta";
  refreshTrigger?: number;
}

export function SavedMarriageReportsList({
  onOpenReport,
  language,
  refreshTrigger,
}: SavedMarriageReportsListProps) {
  const { session, isAuthenticated, isLoading: authLoading } = useAuth();
  const [reports, setReports] = useState<SavedMarriageReportSummary[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const limit = 10;

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Opening / Action states
  const [openingId, setOpeningId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  // Edit Metadata Modal State
  const [editingReport, setEditingReport] = useState<SavedMarriageReportSummary | null>(null);
  const [editTitle, setEditTitle] = useState<string>("");
  const [editGroomName, setEditGroomName] = useState<string>("");
  const [editBrideName, setEditBrideName] = useState<string>("");
  const [savingMetadata, setSavingMetadata] = useState<boolean>(false);
  const [editError, setEditError] = useState<string | null>(null);

  const fetchReports = useCallback(async () => {
    if (!session?.access_token) return;
    setLoading(true);
    setError(null);
    try {
      const offset = (page - 1) * limit;
      const res = await listSavedMarriageCompatibilityReports(
        { limit, offset },
        session.access_token
      );
      setReports(res.reports || []);
      setTotalCount(res.total_count || 0);
    } catch (err: any) {
      console.error("Failed to load saved compatibility reports:", err);
      setError(err?.message || "Failed to load saved reports. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [session?.access_token, page]);

  useEffect(() => {
    if (isAuthenticated && session?.access_token) {
      fetchReports();
    } else if (!authLoading && !isAuthenticated) {
      setLoading(false);
    }
  }, [isAuthenticated, session?.access_token, authLoading, fetchReports, refreshTrigger]);

  const handleOpen = async (summary: SavedMarriageReportSummary) => {
    if (!session?.access_token) return;
    setOpeningId(summary.id);
    try {
      const detail = await getSavedMarriageCompatibilityReport(
        summary.id,
        session.access_token
      );
      onOpenReport(detail);
    } catch (err: any) {
      alert(err?.message || "Failed to load full report snapshot.");
    } finally {
      setOpeningId(null);
    }
  };

  const handleDelete = async (summary: SavedMarriageReportSummary, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!session?.access_token) return;

    const confirmPrompt =
      language === "ta"
        ? `அறிக்கை #${summary.display_number} (${summary.title}) நீக்கப்பட வேண்டுமா? வரலாற்று முடிவு நிரந்தரமாக அழிக்கப்படும்.`
        : `Are you sure you want to delete Report #${summary.display_number} (${summary.title})? The stored snapshot will be permanently removed.`;

    if (!window.confirm(confirmPrompt)) return;

    setDeletingId(summary.id);
    try {
      await deleteSavedMarriageCompatibilityReport(summary.id, session.access_token);
      setReports((prev) => prev.filter((r) => r.id !== summary.id));
      setTotalCount((prev) => Math.max(0, prev - 1));
    } catch (err: any) {
      alert(err?.message || "Failed to delete report.");
    } finally {
      setDeletingId(null);
    }
  };

  const handleStartEdit = (summary: SavedMarriageReportSummary, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingReport(summary);
    setEditTitle(summary.title);
    setEditGroomName(summary.groom_name);
    setEditBrideName(summary.bride_name);
    setEditError(null);
  };

  const handleSaveMetadata = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingReport || !session?.access_token) return;

    const trimmedTitle = editTitle.trim();
    const trimmedGroom = editGroomName.trim();
    const trimmedBride = editBrideName.trim();

    if (!trimmedTitle || !trimmedGroom || !trimmedBride) {
      setEditError(
        language === "ta"
          ? "தலைப்பு மற்றும் பெயர்கள் காலியாக இருக்க முடியாது."
          : "Title, Groom name, and Bride name cannot be empty."
      );
      return;
    }

    setSavingMetadata(true);
    setEditError(null);
    try {
      const payload: UpdateMarriageReportMetadataRequest = {
        title: trimmedTitle,
        groom_name: trimmedGroom,
        bride_name: trimmedBride,
      };
      const updated = await updateSavedMarriageCompatibilityReportMetadata(
        editingReport.id,
        payload,
        session.access_token
      );

      // Update in local list
      setReports((prev) =>
        prev.map((r) =>
          r.id === editingReport.id
            ? {
                ...r,
                title: updated.title,
                groom_name: updated.groom_name,
                bride_name: updated.bride_name,
                updated_at: updated.updated_at,
              }
            : r
        )
      );
      setEditingReport(null);
    } catch (err: any) {
      setEditError(err?.message || "Failed to update report metadata.");
    } finally {
      setSavingMetadata(false);
    }
  };

  const getVerdictBadge = (outcome: string) => {
    switch (outcome) {
      case "FAVOURABLE_UNDER_SELECTED_RULES":
        return {
          bg: "bg-emerald-50 text-emerald-800 border-emerald-200",
          icon: CheckCircle2,
          label: language === "ta" ? "பொருத்தம் சாதகமானது" : "Favourable Match",
        };
      case "MIXED_OR_CONDITIONAL":
        return {
          bg: "bg-amber-50 text-amber-800 border-amber-200",
          icon: AlertTriangle,
          label: language === "ta" ? "மிதமான / நிபந்தனை" : "Conditional / Mixed",
        };
      case "UNFAVOURABLE_UNDER_SELECTED_RULES":
        return {
          bg: "bg-rose-50 text-rose-800 border-rose-200",
          icon: ShieldAlert,
          label: language === "ta" ? "பொருத்தம் சாதகமற்றது" : "Unfavourable Match",
        };
      default:
        return {
          bg: "bg-slate-50 text-slate-800 border-slate-200",
          icon: HelpCircle,
          label: language === "ta" ? "முடிவற்றது" : "Indeterminate",
        };
    }
  };

  // 1. Unauthenticated State
  if (!authLoading && !isAuthenticated) {
    return (
      <div className="p-8 sm:p-12 text-center bg-white rounded-2xl border border-slate-200 shadow-sm max-w-xl mx-auto space-y-4">
        <div className="w-14 h-14 rounded-full bg-slate-100 flex items-center justify-center mx-auto text-slate-500">
          <Lock className="w-7 h-7" />
        </div>
        <h3 className="text-xl font-bold text-[#153F6B]">
          {language === "ta" ? "உள்நுழைவு தேவை" : "Authentication Required"}
        </h3>
        <p className="text-sm text-slate-600">
          {language === "ta"
            ? "உங்கள் சேமிக்கப்பட்ட திருமணப் பொருத்த அறிக்கைகளை அணுக அல்லது புதிய அறிக்கையைச் சேமிக்க தயவுசெய்து உள்நுழையவும்."
            : "Please sign in to access your saved marriage compatibility reports and review historical calculation snapshots."}
        </p>
        <div className="pt-2">
          <Link
            href="/login"
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-[#153F6B] text-white font-semibold text-sm hover:bg-[#1E5692] transition-colors shadow-sm"
          >
            <span>{language === "ta" ? "உள்நுழைக" : "Sign In"}</span>
          </Link>
        </div>
      </div>
    );
  }

  // 2. Loading State
  if (loading && reports.length === 0) {
    return (
      <div className="p-12 text-center bg-white rounded-2xl border border-slate-200 shadow-sm space-y-3">
        <RefreshCw className="w-8 h-8 text-[#153F6B] animate-spin mx-auto" />
        <p className="text-sm text-slate-600 font-medium">
          {language === "ta" ? "சேமிக்கப்பட்ட அறிக்கைகள் ஏற்றப்படுகின்றன..." : "Loading saved compatibility reports..."}
        </p>
      </div>
    );
  }

  // 3. Error State
  if (error) {
    return (
      <div className="p-6 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 space-y-3">
        <div className="flex items-center gap-2 font-bold text-sm">
          <AlertCircle className="w-5 h-5 text-rose-600" />
          <span>{language === "ta" ? "அறிக்கைகளை ஏற்றுவதில் பிழை" : "Error Loading Reports"}</span>
        </div>
        <p className="text-xs text-rose-700">{error}</p>
        <button
          onClick={fetchReports}
          className="px-4 py-1.5 rounded-lg bg-rose-600 text-white text-xs font-semibold hover:bg-rose-700 transition"
        >
          {language === "ta" ? "மீண்டும் முயற்சி செய்" : "Retry"}
        </button>
      </div>
    );
  }

  // 4. Empty State
  if (reports.length === 0) {
    return (
      <div className="p-12 text-center bg-white rounded-2xl border border-slate-200 shadow-sm space-y-4 max-w-xl mx-auto">
        <div className="w-14 h-14 rounded-full bg-slate-100 flex items-center justify-center mx-auto text-[#153F6B]">
          <HeartHandshake className="w-7 h-7" />
        </div>
        <h3 className="text-lg font-bold text-[#153F6B]">
          {language === "ta" ? "சேமிக்கப்பட்ட அறிக்கைகள் எதுவும் இல்லை" : "No Saved Compatibility Reports"}
        </h3>
        <p className="text-sm text-slate-600">
          {language === "ta"
            ? "நீங்கள் இதுவரை எந்த திருமணப் பொருத்த அறிக்கையையும் சேமிக்கவில்லை. பொருத்தத்தை கணித்த பிறகு 'சேமி' பொத்தானைக் கிளிக் செய்யவும்."
            : "You have not saved any marriage compatibility reports yet. Run an analysis and click 'Save Report' to preserve historical snapshots here."}
        </p>
      </div>
    );
  }

  const totalPages = Math.ceil(totalCount / limit) || 1;

  return (
    <div className="space-y-6">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-2xl bg-white border border-slate-200 shadow-xs">
        <div>
          <h2 className="text-lg font-bold text-[#153F6B] flex items-center gap-2">
            <HeartHandshake className="w-5 h-5 text-[#B4872B]" />
            <span>{language === "ta" ? "சேமிக்கப்பட்ட பொருத்த அறிக்கைகள்" : "Saved Compatibility Reports"}</span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            {language === "ta"
              ? `மொத்தம் ${totalCount} அறிக்கைகள் கண்டறியப்பட்டன (புதியவை முதலில்)`
              : `Total ${totalCount} saved reports (ordered newest first)`}
          </p>
        </div>

        <button
          type="button"
          onClick={fetchReports}
          disabled={loading}
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          <span>{language === "ta" ? "புதுப்பி" : "Refresh"}</span>
        </button>
      </div>

      {/* Reports Grid / Cards List */}
      <div className="grid grid-cols-1 gap-4">
        {reports.map((report) => {
          const badge = getVerdictBadge(report.overall_outcome);
          const BadgeIcon = badge.icon;
          const isOpening = openingId === report.id;
          const isDeleting = deletingId === report.id;

          return (
            <div
              key={report.id}
              className="bg-white rounded-2xl border border-slate-200 shadow-xs hover:shadow-md transition-all p-5 sm:p-6 flex flex-col md:flex-row md:items-center justify-between gap-5"
            >
              {/* Left Details */}
              <div className="space-y-3 flex-1 min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-[#153F6B] text-white">
                    #{report.display_number}
                  </span>
                  <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${badge.bg}`}>
                    <BadgeIcon className="w-3.5 h-3.5" />
                    <span>{badge.label}</span>
                  </span>
                  <span className="text-xs text-slate-400 flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5" />
                    <span>{new Date(report.created_at).toLocaleDateString(language === "ta" ? "ta-IN" : "en-US", {
                      year: "numeric",
                      month: "short",
                      day: "numeric",
                    })}</span>
                  </span>
                </div>

                <div>
                  <h3 className="text-base sm:text-lg font-bold text-[#153F6B] truncate">
                    {report.title}
                  </h3>
                  <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-600 mt-1">
                    <span className="font-semibold text-slate-800">
                      {language === "ta" ? "மணமகன்:" : "Groom:"} {report.groom_name} ({report.groom_birth_date})
                    </span>
                    <span className="text-slate-300">•</span>
                    <span className="font-semibold text-slate-800">
                      {language === "ta" ? "மணமகள்:" : "Bride:"} {report.bride_name} ({report.bride_birth_date})
                    </span>
                  </div>
                </div>

                {/* Score Indicators Pill Bar */}
                <div className="flex flex-wrap items-center gap-2 pt-1">
                  {report.porutham_score !== null && report.porutham_score !== undefined && (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-50 border border-slate-200 text-xs font-medium text-slate-700">
                      <span className="text-slate-400">{language === "ta" ? "பொருத்தம்:" : "Porutham:"}</span>
                      <strong className="text-[#153F6B]">{report.porutham_score} / 10</strong>
                    </span>
                  )}
                  {report.ashtakoota_points !== null && report.ashtakoota_points !== undefined && (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-50 border border-slate-200 text-xs font-medium text-slate-700">
                      <span className="text-slate-400">{language === "ta" ? "அஷ்டகூடம்:" : "Ashtakoota:"}</span>
                      <strong className="text-[#B4872B]">{report.ashtakoota_points} / 36</strong>
                    </span>
                  )}
                  {report.samadosham_status && (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-50 border border-slate-200 text-xs font-medium text-slate-700">
                      <span className="text-slate-400">{language === "ta" ? "தோஷம்:" : "Dosha:"}</span>
                      <span>{report.samadosham_status}</span>
                    </span>
                  )}
                </div>
              </div>

              {/* Right Action Buttons */}
              <div className="flex items-center gap-2.5 pt-3 md:pt-0 border-t md:border-t-0 border-slate-100 shrink-0">
                <button
                  type="button"
                  onClick={() => handleOpen(report)}
                  disabled={isOpening}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-[#153F6B] to-[#1E5692] text-white text-xs font-bold shadow-sm hover:from-[#1E5692] hover:to-[#153F6B] disabled:opacity-50 transition"
                  title="Open calculation snapshot"
                >
                  {isOpening ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <FolderOpen className="w-4 h-4" />
                  )}
                  <span>{language === "ta" ? "திறக்க" : "Open Report"}</span>
                </button>

                <button
                  type="button"
                  onClick={(e) => handleStartEdit(report, e)}
                  className="p-2 rounded-xl border border-slate-200 text-slate-600 hover:text-[#153F6B] hover:bg-slate-50 transition"
                  title="Edit metadata (title, names)"
                >
                  <Edit2 className="w-4 h-4" />
                </button>

                <button
                  type="button"
                  onClick={(e) => handleDelete(report, e)}
                  disabled={isDeleting}
                  className="p-2 rounded-xl border border-slate-200 text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition disabled:opacity-50"
                  title="Delete report"
                >
                  {isDeleting ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Trash2 className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-4 px-2">
          <button
            type="button"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700 disabled:opacity-40 hover:bg-slate-50 transition"
          >
            <ChevronLeft className="w-4 h-4" />
            <span>{language === "ta" ? "முந்தையது" : "Previous"}</span>
          </button>

          <span className="text-xs text-slate-500 font-medium">
            {language === "ta"
              ? `பக்கம் ${page} / ${totalPages}`
              : `Page ${page} of ${totalPages}`}
          </span>

          <button
            type="button"
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700 disabled:opacity-40 hover:bg-slate-50 transition"
          >
            <span>{language === "ta" ? "அடுத்தது" : "Next"}</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Edit Metadata Modal Dialog */}
      {editingReport && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xl max-w-md w-full p-6 space-y-5 animate-scaleUp">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <Edit2 className="w-5 h-5 text-[#153F6B]" />
                <h3 className="font-bold text-[#153F6B] text-base">
                  {language === "ta" ? "அறிக்கைத் தலைப்பைத் திருத்து" : "Edit Report Metadata"}
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setEditingReport(null)}
                className="text-slate-400 hover:text-slate-600 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveMetadata} className="space-y-4">
              {editError && (
                <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs">
                  {editError}
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  {language === "ta" ? "அறிக்கை தலைப்பு" : "Report Title"} *
                </label>
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-[#153F6B] focus:border-[#153F6B]"
                  placeholder="e.g. Karthik & Revathi Match"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  {language === "ta" ? "மணமகன் பெயர்" : "Groom Name"} *
                </label>
                <input
                  type="text"
                  value={editGroomName}
                  onChange={(e) => setEditGroomName(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-[#153F6B] focus:border-[#153F6B]"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  {language === "ta" ? "மணமகள் பெயர்" : "Bride Name"} *
                </label>
                <input
                  type="text"
                  value={editBrideName}
                  onChange={(e) => setEditBrideName(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-[#153F6B] focus:border-[#153F6B]"
                  required
                />
              </div>

              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-500">
                <span className="font-semibold text-slate-700">
                  {language === "ta" ? "பாதுகாக்கப்பட்ட கணக்கீட்டு விபரம்:" : "Immutable Calculation Notice:"}
                </span>{" "}
                {language === "ta"
                  ? "பிறப்பு விவரங்கள், அட்சரேகை/தீர்க்கரேகை மற்றும் கணிப்பு முடிவுகள் மாறாது; மாற்ற முடியாது."
                  : "Calculation parameters, scores, and birth particulars are strictly immutable to protect historical integrity."}
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setEditingReport(null)}
                  disabled={savingMetadata}
                  className="px-4 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-50 transition"
                >
                  {language === "ta" ? "ரத்து" : "Cancel"}
                </button>

                <button
                  type="submit"
                  disabled={savingMetadata}
                  className="inline-flex items-center gap-1.5 px-5 py-2 rounded-xl bg-[#153F6B] text-white text-xs font-bold hover:bg-[#1E5692] disabled:opacity-50 transition"
                >
                  {savingMetadata ? (
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Save className="w-3.5 h-3.5" />
                  )}
                  <span>{language === "ta" ? "சேமி" : "Save Changes"}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
