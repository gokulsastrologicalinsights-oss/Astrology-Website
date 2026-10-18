"use client";

import React, { useState, useEffect, useCallback, useRef } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { SavedHoroscopeItem, SavedHoroscopesListResponse } from "@/lib/types";
import { SavedHoroscopeCard } from "./SavedHoroscopeCard";
import { SavedHoroscopeEditModal } from "./SavedHoroscopeEditModal";
import { formatHoroscopeSequence } from "@/lib/horoscope-storage-utils";
import { formatBirthDate, formatBirthTime } from "@/lib/formatters";
import {
  Search,
  RefreshCw,
  Database,
  Compass,
  ArrowRight,
  AlertCircle,
  X,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Sparkles,
  LayoutGrid,
  List,
  Trash2,
  Edit3,
  ExternalLink,
  Calendar,
  Clock,
  MapPin,
  Sliders,
  Download,
  Filter,
  Crown,
} from "lucide-react";

interface SavedHoroscopesListProps {
  pageSize?: number;
  showHeader?: boolean;
  showBanner?: boolean;
  title?: string;
  columns?: 2 | 3;
}

export function SavedHoroscopesList({
  pageSize: initialPageSize = 12,
  showHeader = false,
  showBanner = true,
  title,
  columns = 3,
}: SavedHoroscopesListProps) {
  const { language, t } = useLanguage();

  // Data states
  const [horoscopes, setHoroscopes] = useState<SavedHoroscopeItem[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(initialPageSize);
  const [totalPages, setTotalPages] = useState<number>(1);

  // View mode: cards or table
  const [viewMode, setViewMode] = useState<"cards" | "table">("cards");

  // Search & Filter
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [debouncedSearch, setDebouncedSearch] = useState<string>("");
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Status states
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Modal states
  const [selectedHoroscope, setSelectedHoroscope] = useState<SavedHoroscopeItem | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState<boolean>(false);

  // Delete modal state
  const [horoscopeToDelete, setHoroscopeToDelete] = useState<SavedHoroscopeItem | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  // Debounce search input
  const handleSearchChange = (text: string) => {
    setSearchTerm(text);
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    searchTimeoutRef.current = setTimeout(() => {
      setDebouncedSearch(text.trim());
      setCurrentPage(1); // Reset to page 1 on new search
    }, 350);
  };

  const handleManualSearch = () => {
    setDebouncedSearch(searchTerm.trim());
    setCurrentPage(1);
  };

  const handleClearSearch = () => {
    setSearchTerm("");
    setDebouncedSearch("");
    setCurrentPage(1);
  };

  // Export to CSV
  const handleExportCsv = () => {
    if (horoscopes.length === 0) return;
    const headers = ["Serial", "Name", "Birth Date", "Birth Time", "Birthplace", "Ayanamsa", "Created At"];
    const rows = horoscopes.map((h) => [
      h.display_number,
      `"${(h.person_name || "").replace(/"/g, '""')}"`,
      h.birth_date,
      h.birth_time,
      `"${(h.birthplace || "").replace(/"/g, '""')}"`,
      h.ayanamsa_id === 1 ? "KP" : h.ayanamsa_id === 2 ? "Raman" : "Lahiri",
      h.created_at,
    ]);
    const csvContent =
      "data:text/csv;charset=utf-8," +
      [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute(
      "download",
      `horoscopes_export_${new Date().toISOString().split("T")[0]}.csv`
    );
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Fetch horoscopes from API
  const fetchHoroscopes = useCallback(
    async (pageToFetch = currentPage, search = debouncedSearch, limit = pageSize, showRefreshing = false) => {
      if (showRefreshing) {
        setIsRefreshing(true);
      } else {
        setIsLoading(true);
      }
      setErrorMessage(null);

      try {
        const queryParams = new URLSearchParams({
          page: pageToFetch.toString(),
          limit: limit.toString(),
        });
        if (search) {
          queryParams.set("search", search);
        }

        const res = await fetch(`/api/horoscopes?${queryParams.toString()}`, {
          cache: "no-store",
        });

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.error || "Failed to load saved horoscopes.");
        }

        const data: SavedHoroscopesListResponse = await res.json();
        // Preserve strictly descending order of generation/creation time with stable secondary sort
        const rawList = data.horoscopes || [];
        const sortedList = [...rawList].sort((a, b) => {
          const tA = new Date(a.created_at || 0).getTime();
          const tB = new Date(b.created_at || 0).getTime();
          if (tB !== tA) return tB - tA;
          return (b.display_number || 0) - (a.display_number || 0);
        });
        setHoroscopes(sortedList);
        setTotalCount(data.totalCount || 0);
        setTotalPages(data.totalPages || 1);
        setCurrentPage(data.page || 1);
      } catch (err: any) {
        console.error("Error fetching horoscopes:", err);
        setErrorMessage(
          err.message ||
            (language === "ta"
              ? "சேமிக்கப்பட்ட ஜாதகங்களை ஏற்றுவதில் பிழை ஏற்பட்டது."
              : "An error occurred while loading saved horoscopes.")
        );
      } finally {
        setIsLoading(false);
        setIsRefreshing(false);
      }
    },
    [currentPage, debouncedSearch, language, pageSize]
  );

  useEffect(() => {
    fetchHoroscopes(currentPage, debouncedSearch, pageSize);
  }, [currentPage, debouncedSearch, pageSize, fetchHoroscopes]);

  const handleOpenEdit = (item: SavedHoroscopeItem) => {
    setSelectedHoroscope(item);
    setIsEditModalOpen(true);
  };

  const handleCloseEdit = () => {
    setIsEditModalOpen(false);
    setSelectedHoroscope(null);
  };

  const handleEditSuccess = () => {
    fetchHoroscopes(currentPage, debouncedSearch, pageSize, true);
  };

  const handleDeleteHoroscope = async (id: string) => {
    try {
      const res = await fetch(`/api/horoscopes/${id}`, {
        method: "DELETE",
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.error || "Failed to delete horoscope.");
      }
      // Refresh list
      await fetchHoroscopes(currentPage, debouncedSearch, pageSize, true);
    } catch (err: any) {
      console.error("Error deleting horoscope:", err);
      alert(err.message || "Failed to delete horoscope.");
    }
  };

  const confirmDeleteAction = async () => {
    if (!horoscopeToDelete) return;
    setIsDeleting(true);
    try {
      await handleDeleteHoroscope(horoscopeToDelete.id);
      setHoroscopeToDelete(null);
    } finally {
      setIsDeleting(false);
    }
  };

  // Range text: e.g. "1 to 12 of 693"
  const startItem = totalCount === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  const endItem = Math.min(currentPage * pageSize, totalCount);

  return (
    <div className="space-y-4">
      {/* Optional Section Header */}
      {showHeader && (
        <div className="flex items-center justify-between pb-3 border-b border-[#D9DEE7]">
          <div className="flex items-center gap-2">
            <Database className="w-5 h-5 text-[#B4872B]" />
            <h2 className="font-serif text-base sm:text-lg font-bold text-[#183047]">
              {title || (language === "ta" ? "சேமிக்கப்பட்ட ஜாதகங்கள்" : "Saved Horoscopes")}
            </h2>
          </div>
          <Link
            href="/horoscope"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-white bg-[#153F6B] hover:bg-[#0F3155] shadow-xs transition-colors"
          >
            <Compass className="w-3.5 h-3.5 text-[#B4872B]" />
            <span>{language === "ta" ? "+ புதிய ஜாதகம்" : "+ Create Horoscope"}</span>
          </Link>
        </div>
      )}

      {/* 1. Subscription or Account Status Banner matching Screenshot 2 */}
      {showBanner && (
        <div className="rounded-xl border border-[#D8BD80] bg-[#FAF7F0] p-3.5 sm:p-4 shadow-2xs flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center text-[#B4872B] shrink-0">
              <Crown className="w-4 h-4 text-[#B4872B]" />
            </div>
            <div>
              <div className="text-xs sm:text-sm font-bold text-[#183047] flex items-center gap-1.5">
                <span>{language === "ta" ? "பிரீமியம் அணுகல் செயல்படுகிறது" : "Premium Access Active"}</span>
                <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />
              </div>
              <div className="text-[11px] text-[#8190A6]">
                {language === "ta"
                  ? "வரம்பற்ற துல்லிய ஜாதகக் கணக்கீடுகள் மற்றும் சேமிப்பு இயக்கத்தில் உள்ளது."
                  : "You have unlimited horoscopes creations with permanent sequential serial numbers."}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 2. Compact Search & Pagination Toolbar matching Screenshot 2 */}
      <div className="rounded-xl border border-[#D9DEE7] bg-white p-2.5 sm:p-3 shadow-2xs flex flex-col md:flex-row md:items-center justify-between gap-3">
        {/* Left Side: Search input + கண்டுபிடி Button + Filter */}
        <div className="flex items-center gap-2 flex-1 max-w-md">
          <div className="relative flex-1">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => handleSearchChange(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleManualSearch()}
              placeholder={language === "ta" ? "தேடுக..." : "Search..."}
              className="w-full px-3 py-1.5 text-xs text-[#183047] placeholder-[#8190A6] border border-[#D9DEE7] rounded-lg focus:outline-hidden focus:border-[#153F6B] focus:ring-1 focus:ring-[#153F6B]/20 transition-all bg-white"
            />
            {searchTerm && (
              <button
                type="button"
                onClick={handleClearSearch}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 p-0.5 rounded text-[#8190A6] hover:text-[#183047]"
                title={t.clearSearch}
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          <button
            type="button"
            onClick={handleManualSearch}
            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-[#153F6B] hover:bg-[#0F3155] text-white text-xs font-semibold shadow-2xs transition-colors cursor-pointer shrink-0"
          >
            <Search className="w-3.5 h-3.5" />
            <span>{language === "ta" ? "கண்டுபிடி" : "Search"}</span>
          </button>

          <button
            type="button"
            onClick={() => fetchHoroscopes(currentPage, debouncedSearch, pageSize, true)}
            className="p-1.5 rounded-lg border border-[#D9DEE7] bg-white hover:bg-[#F2F3F5] text-[#183047] transition-colors cursor-pointer shrink-0"
            title={language === "ta" ? "வடிகட்டி / புதுப்பி" : "Filter / Refresh"}
          >
            <Filter className="w-3.5 h-3.5 text-[#8190A6]" />
          </button>
        </div>

        {/* Right Side: Export + Record Counter + Pagination + Page Size */}
        <div className="flex items-center gap-2.5 sm:gap-3 flex-wrap justify-between md:justify-end text-xs text-[#8190A6]">
          {/* Download / Export */}
          <button
            type="button"
            onClick={handleExportCsv}
            disabled={horoscopes.length === 0}
            className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-[#D9DEE7] bg-white hover:bg-[#F2F3F5] text-xs font-semibold text-[#183047] transition-colors cursor-pointer disabled:opacity-40"
            title={language === "ta" ? "தரவிறக்கம்" : "Export CSV"}
          >
            <Download className="w-3.5 h-3.5 text-[#153F6B]" />
            <span>{language === "ta" ? "பதிவிறக்கம்" : "Export"}</span>
          </button>

          {/* Record Counter: 1 to 12 of 693 */}
          <span className="text-xs font-medium text-[#183047] whitespace-nowrap">
            {startItem} to {endItem} of {totalCount}
          </span>

          {/* Pagination Controls << < > >> */}
          <div className="inline-flex items-center gap-1">
            <button
              type="button"
              onClick={() => setCurrentPage(1)}
              disabled={currentPage <= 1}
              className="p-1.5 rounded-lg border border-[#D9DEE7] bg-white hover:bg-[#F2F3F5] text-[#183047] disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer transition-colors"
              title="First Page"
            >
              <ChevronsLeft className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage <= 1}
              className="p-1.5 rounded-lg border border-[#D9DEE7] bg-white hover:bg-[#F2F3F5] text-[#183047] disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer transition-colors"
              title="Previous Page"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage >= totalPages}
              className="p-1.5 rounded-lg border border-[#D9DEE7] bg-white hover:bg-[#F2F3F5] text-[#183047] disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer transition-colors"
              title="Next Page"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={() => setCurrentPage(totalPages)}
              disabled={currentPage >= totalPages}
              className="p-1.5 rounded-lg border border-[#D9DEE7] bg-white hover:bg-[#F2F3F5] text-[#183047] disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer transition-colors"
              title="Last Page"
            >
              <ChevronsRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Page Size Selector */}
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] text-[#8190A6] hidden sm:inline">
              {language === "ta" ? "பக்க அளவு" : "Page Size"}
            </span>
            <select
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setCurrentPage(1);
              }}
              className="px-2 py-1 text-xs border border-[#D9DEE7] rounded-lg bg-white text-[#183047] font-semibold focus:outline-hidden cursor-pointer"
            >
              <option value={6}>6</option>
              <option value={12}>12</option>
              <option value={24}>24</option>
              <option value={48}>48</option>
            </select>
          </div>
        </div>
      </div>

      {/* 3. Loading State */}
      {isLoading && (
        <div className="py-16 text-center space-y-3">
          <div className="inline-block animate-spin w-8 h-8 border-4 border-[#153F6B] border-t-transparent rounded-full" />
          <p className="text-xs text-[#8190A6]">{t.loading}</p>
        </div>
      )}

      {/* 4. Error State */}
      {!isLoading && errorMessage && (
        <div className="p-5 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs sm:text-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <button
            type="button"
            onClick={() => fetchHoroscopes(currentPage, debouncedSearch, pageSize)}
            className="px-3.5 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white font-semibold text-xs transition-colors shrink-0 cursor-pointer"
          >
            {t.retry}
          </button>
        </div>
      )}

      {/* 5. Empty State: No horoscopes yet */}
      {!isLoading && !errorMessage && horoscopes.length === 0 && !debouncedSearch && (
        <div className="py-12 px-6 rounded-2xl border border-dashed border-[#D9DEE7] bg-white text-center">
          <div className="w-14 h-14 mx-auto rounded-full bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center text-[#B4872B] mb-3.5 shadow-2xs">
            <Compass className="w-7 h-7" />
          </div>
          <h3 className="font-serif text-base sm:text-lg font-bold text-[#183047]">
            {t.noSavedHoroscopes}
          </h3>
          <p className="mt-1.5 text-xs text-[#8190A6] max-w-md mx-auto leading-relaxed">
            {t.noSavedHoroscopesDesc}
          </p>
          <div className="mt-5">
            <Link
              href="/horoscope"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-[#153F6B] hover:bg-[#0F3155] shadow-xs transition-colors"
            >
              <span>{language === "ta" ? "+ புதிய ஜாதகம் கணிக்க" : "+ Calculate Horoscope"}</span>
              <ArrowRight className="w-3.5 h-3.5 text-[#B4872B]" />
            </Link>
          </div>
        </div>
      )}

      {/* 6. Empty State: Search yielded no matches */}
      {!isLoading && !errorMessage && horoscopes.length === 0 && debouncedSearch && (
        <div className="py-10 px-4 rounded-2xl border border-[#D9DEE7] bg-white text-center">
          <p className="text-xs sm:text-sm text-[#8190A6]">{t.noSearchResults}</p>
          <button
            type="button"
            onClick={handleClearSearch}
            className="mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#D9DEE7] bg-[#F2F3F5] text-xs font-semibold text-[#183047] hover:bg-white cursor-pointer"
          >
            <span>{t.clearSearch}</span>
          </button>
        </div>
      )}

      {/* 7. 3-Column Responsive Cards Grid matching Screenshot 2 */}
      {!isLoading && !errorMessage && horoscopes.length > 0 && (
        <>
          {viewMode === "cards" ? (
            <div
              className={
                columns === 2
                  ? "grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-5"
                  : "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5"
              }
            >
              {horoscopes.map((item) => (
                <SavedHoroscopeCard
                  key={item.id}
                  horoscope={item}
                  onEdit={handleOpenEdit}
                  onDelete={handleDeleteHoroscope}
                />
              ))}
            </div>
          ) : (
            /* Table View: Clean data table */
            <div className="rounded-2xl border border-[#D9DEE7] bg-white overflow-hidden shadow-xs">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#FAF7F0] text-[#183047] uppercase font-bold border-b border-[#D9DEE7]">
                    <tr>
                      <th className="px-4 py-3">{language === "ta" ? "ஜாதக எண்" : "Horoscope No."}</th>
                      <th className="px-4 py-3">{language === "ta" ? "பெயர்" : "Subject Name"}</th>
                      <th className="px-4 py-3">{language === "ta" ? "வகை" : "Type"}</th>
                      <th className="px-4 py-3">{language === "ta" ? "பிறந்த தேதி & நேரம்" : "Birth Date & Time"}</th>
                      <th className="px-4 py-3">{language === "ta" ? "பிறந்த இடம்" : "Birthplace"}</th>
                      <th className="px-4 py-3">{language === "ta" ? "உருவாக்கிய நேரம்" : "Generated"}</th>
                      <th className="px-4 py-3 text-right">{language === "ta" ? "நடவடிக்கை" : "Action"}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#D9DEE7] text-[#183047]">
                    {horoscopes.map((item) => {
                      const seqText = formatHoroscopeSequence(item.display_number, language);
                      const birthDateStr = formatBirthDate(item.birth_date, language);
                      const birthTimeStr = formatBirthTime(item.birth_time);
                      const isKp = item.ayanamsa_id === 1 || item.ayanamsa_id === 3;
                      const ayanamsaLabel =
                        item.ayanamsa_id === 1 ? "KP" : item.ayanamsa_id === 2 ? "Raman" : item.ayanamsa_id === 3 ? "KP New" : "Lahiri";
                      const typeLabel = isKp
                        ? (language === "ta" ? "கே.பி" : "KP")
                        : (language === "ta" ? "வேத" : "Vedic");
                      const genDateStr = item.created_at
                        ? new Date(item.created_at).toLocaleDateString(language === "ta" ? "ta-IN" : "en-US", {
                            year: "numeric",
                            month: "short",
                            day: "numeric",
                          })
                        : "";
                      const genTimeStr = item.created_at
                        ? new Date(item.created_at).toLocaleTimeString(language === "ta" ? "ta-IN" : "en-US", {
                            hour: "2-digit",
                            minute: "2-digit",
                          })
                        : "";

                      return (
                        <tr key={item.id} className="hover:bg-[#FAF7F0]/60 transition-colors">
                          <td className="px-4 py-3.5">
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-[#FAF2DE] text-[#B4872B] border border-[#D8BD80]">
                              {seqText}
                            </span>
                          </td>
                          <td className="px-4 py-3.5 font-bold text-[#183047]">
                            {item.person_name?.trim() || t.unnamedHoroscope}
                          </td>
                          <td className="px-4 py-3.5">
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                                isKp
                                  ? "bg-amber-50 text-amber-800 border-amber-300"
                                  : "bg-[#EBF2FE] text-[#153F6B] border-[#BFDBFE]"
                              }`}
                            >
                              {typeLabel} ({ayanamsaLabel})
                            </span>
                          </td>
                          <td className="px-4 py-3.5 text-[#52667E]">
                            <div>{birthDateStr}</div>
                            <div className="text-[11px] font-mono text-[#8190A6]">
                              {birthTimeStr} {item.timezone ? `(${item.timezone})` : ""}
                            </div>
                          </td>
                          <td className="px-4 py-3.5 text-[#52667E] max-w-[180px] truncate" title={item.birthplace}>
                            {item.birthplace || t.locationUnavailable}
                          </td>
                          <td className="px-4 py-3.5 text-[#52667E] whitespace-nowrap text-[11px]">
                            <div>{genDateStr}</div>
                            <div className="text-[10px] text-[#8190A6]">{genTimeStr}</div>
                          </td>
                          <td className="px-4 py-3.5 text-right">
                            <div className="inline-flex items-center gap-1.5">
                              <Link
                                href={`/horoscope/results?id=${item.id}`}
                                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#153F6B] hover:bg-[#0F3155] text-white text-[11px] font-semibold transition-colors"
                              >
                                <span>{language === "ta" ? "காண்க" : "View"}</span>
                                <ExternalLink className="w-3 h-3 text-[#B4872B]" />
                              </Link>
                              <button
                                type="button"
                                onClick={() => handleOpenEdit(item)}
                                className="p-1.5 rounded-lg border border-[#D9DEE7] bg-white hover:bg-[#F2F3F5] text-[#183047] transition-colors"
                                title={t.actionEdit}
                              >
                                <Edit3 className="w-3 h-3" />
                              </button>
                              <button
                                type="button"
                                onClick={() => setHoroscopeToDelete(item)}
                                className="p-1.5 rounded-lg border border-transparent hover:border-rose-200 hover:bg-rose-50 text-[#8190A6] hover:text-rose-600 transition-colors"
                                title={t.deleteHoroscope || "Delete"}
                              >
                                <Trash2 className="w-3 h-3" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {/* Edit Modal */}
      <SavedHoroscopeEditModal
        horoscope={selectedHoroscope}
        isOpen={isEditModalOpen}
        onClose={handleCloseEdit}
        onSuccess={handleEditSuccess}
      />

      {/* Delete Confirmation Modal */}
      {horoscopeToDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs">
          <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl border border-[#D9DEE7] space-y-4">
            <div className="flex items-center gap-2.5 text-rose-600">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <h4 className="font-bold text-sm text-[#183047]">
                {language === "ta" ? "ஜாதகத்தை நீக்கவா?" : "Delete Horoscope?"}
              </h4>
            </div>
            <p className="text-xs text-[#8190A6] leading-relaxed">
              {language === "ta"
                ? `"${horoscopeToDelete.person_name || "ஜாதகம்"}" (${formatHoroscopeSequence(horoscopeToDelete.display_number, "ta")}) நிரந்தரமாக நீக்கப்படும்.`
                : `"${horoscopeToDelete.person_name || "Horoscope"}" (${formatHoroscopeSequence(horoscopeToDelete.display_number, "en")}) will be permanently deleted.`}
            </p>
            <div className="flex items-center justify-end gap-2 pt-2 border-t border-[#D9DEE7]">
              <button
                type="button"
                onClick={() => setHoroscopeToDelete(null)}
                disabled={isDeleting}
                className="px-3 py-1.5 rounded-lg border border-[#D9DEE7] bg-white hover:bg-[#F2F3F5] text-xs font-semibold text-[#183047] cursor-pointer"
              >
                {language === "ta" ? "ரத்து" : "Cancel"}
              </button>
              <button
                type="button"
                onClick={confirmDeleteAction}
                disabled={isDeleting}
                className="px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold disabled:opacity-50 cursor-pointer"
              >
                {isDeleting ? "..." : language === "ta" ? "ஆம், நீக்கு" : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
