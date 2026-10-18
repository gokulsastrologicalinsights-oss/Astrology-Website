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
} from "lucide-react";

interface SavedHoroscopesListProps {
  pageSize?: number;
  showHeader?: boolean;
  title?: string;
}

export function SavedHoroscopesList({
  pageSize = 6,
  showHeader = true,
  title,
}: SavedHoroscopesListProps) {
  const { language, t } = useLanguage();

  // Data states
  const [horoscopes, setHoroscopes] = useState<SavedHoroscopeItem[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(1);
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

  const handleClearSearch = () => {
    setSearchTerm("");
    setDebouncedSearch("");
    setCurrentPage(1);
  };

  // Fetch horoscopes from API
  const fetchHoroscopes = useCallback(
    async (pageToFetch = currentPage, search = debouncedSearch, showRefreshing = false) => {
      if (showRefreshing) {
        setIsRefreshing(true);
      } else {
        setIsLoading(true);
      }
      setErrorMessage(null);

      try {
        const queryParams = new URLSearchParams({
          page: pageToFetch.toString(),
          limit: pageSize.toString(),
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
        setHoroscopes(data.horoscopes || []);
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
    fetchHoroscopes(currentPage, debouncedSearch);
  }, [currentPage, debouncedSearch, fetchHoroscopes]);

  const handleOpenEdit = (item: SavedHoroscopeItem) => {
    setSelectedHoroscope(item);
    setIsEditModalOpen(true);
  };

  const handleCloseEdit = () => {
    setIsEditModalOpen(false);
    setSelectedHoroscope(null);
  };

  const handleEditSuccess = () => {
    fetchHoroscopes(currentPage, debouncedSearch, true);
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
      await fetchHoroscopes(currentPage, debouncedSearch, true);
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

  return (
    <div className="space-y-6">
      {/* 1. Header Toolbar: Title, Total Badge, Search Bar, View Toggle, Refresh */}
      {showHeader && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#E2DCD5]">
          <div className="flex items-center gap-2.5">
            <Database className="w-5 h-5 text-[#B8860B]" />
            <div>
              <h2 className="font-serif text-lg font-bold text-[#0F172A]">
                {title || t.savedHoroscopesTitle}
              </h2>
              <span className="text-xs text-[#64748B]">
                {t.totalHoroscopes.replace("{count}", totalCount.toString())}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2.5 flex-wrap">
            {/* View Mode Toggle */}
            <div className="inline-flex rounded-xl border border-[#CBD5E1] p-0.5 bg-[#FAF8F5]">
              <button
                type="button"
                onClick={() => setViewMode("cards")}
                className={`p-1.5 rounded-lg text-xs font-semibold flex items-center gap-1 transition-all ${
                  viewMode === "cards"
                    ? "bg-white text-[#0F172A] shadow-xs"
                    : "text-[#64748B] hover:text-[#0F172A]"
                }`}
                title="Cards view"
              >
                <LayoutGrid className="w-3.5 h-3.5" />
                <span className="hidden md:inline">{language === "ta" ? "கார்டுகள்" : "Cards"}</span>
              </button>
              <button
                type="button"
                onClick={() => setViewMode("table")}
                className={`p-1.5 rounded-lg text-xs font-semibold flex items-center gap-1 transition-all ${
                  viewMode === "table"
                    ? "bg-white text-[#0F172A] shadow-xs"
                    : "text-[#64748B] hover:text-[#0F172A]"
                }`}
                title="Table view"
              >
                <List className="w-3.5 h-3.5" />
                <span className="hidden md:inline">{language === "ta" ? "அட்டவணை" : "Table"}</span>
              </button>
            </div>

            {/* Search Box */}
            <div className="relative flex-1 sm:w-60">
              <Search className="w-4 h-4 text-[#94A3B8] absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => handleSearchChange(e.target.value)}
                placeholder={t.searchHoroscopesPlaceholder}
                className="w-full pl-9 pr-8 py-2 rounded-xl border border-[#CBD5E1] bg-white text-xs text-[#0F172A] placeholder-[#94A3B8] focus:outline-hidden focus:border-[#B8860B] focus:ring-2 focus:ring-[#B8860B]/20 transition-all"
              />
              {searchTerm && (
                <button
                  type="button"
                  onClick={handleClearSearch}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 p-0.5 rounded text-[#94A3B8] hover:text-[#0F172A]"
                  title={t.clearSearch}
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {/* Refresh Button */}
            <button
              type="button"
              onClick={() => fetchHoroscopes(currentPage, debouncedSearch, true)}
              disabled={isLoading || isRefreshing}
              className="p-2 rounded-xl border border-[#CBD5E1] bg-white hover:bg-[#FAF8F5] text-[#475569] hover:text-[#0F172A] transition-colors cursor-pointer disabled:opacity-50"
              title={language === "ta" ? "புதுப்பி" : "Refresh list"}
              aria-label="Refresh"
            >
              <RefreshCw
                className={`w-4 h-4 ${isRefreshing ? "animate-spin text-[#B8860B]" : ""}`}
              />
            </button>
          </div>
        </div>
      )}

      {/* 2. Loading State */}
      {isLoading && (
        <div className="py-16 text-center space-y-3">
          <div className="inline-block animate-spin w-8 h-8 border-4 border-[#B8860B] border-t-transparent rounded-full" />
          <p className="text-xs text-[#64748B]">{t.loading}</p>
        </div>
      )}

      {/* 3. Error State */}
      {!isLoading && errorMessage && (
        <div className="p-5 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs sm:text-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <button
            type="button"
            onClick={() => fetchHoroscopes(currentPage, debouncedSearch)}
            className="px-3.5 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white font-semibold text-xs transition-colors shrink-0"
          >
            {t.retry}
          </button>
        </div>
      )}

      {/* 4. Empty State: No horoscopes yet */}
      {!isLoading && !errorMessage && horoscopes.length === 0 && !debouncedSearch && (
        <div className="py-12 px-6 rounded-2xl border border-dashed border-[#CBD5E1] bg-[#FAF8F5] text-center">
          <div className="w-14 h-14 mx-auto rounded-full bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center text-[#B8860B] mb-3.5 shadow-2xs">
            <Compass className="w-7 h-7" />
          </div>
          <h3 className="font-serif text-base sm:text-lg font-bold text-[#0F172A]">
            {t.noSavedHoroscopes}
          </h3>
          <p className="mt-1.5 text-xs text-[#64748B] max-w-md mx-auto leading-relaxed">
            {t.noSavedHoroscopesDesc}
          </p>
          <div className="mt-5">
            <Link
              href="/horoscope"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-[#0F172A] hover:bg-[#1E293B] shadow-xs transition-colors"
            >
              <span>{t.calculate}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      )}

      {/* 5. Empty State: Search yielded no matches */}
      {!isLoading && !errorMessage && horoscopes.length === 0 && debouncedSearch && (
        <div className="py-10 px-4 rounded-2xl border border-[#E2DCD5] bg-white text-center">
          <p className="text-xs sm:text-sm text-[#64748B]">
            {t.noSearchResults}
          </p>
          <button
            type="button"
            onClick={handleClearSearch}
            className="mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#CBD5E1] bg-[#FAF8F5] text-xs font-semibold text-[#0F172A] hover:bg-white"
          >
            <span>{t.clearSearch}</span>
          </button>
        </div>
      )}

      {/* 6. List / Cards / Table Rendering */}
      {!isLoading && !errorMessage && horoscopes.length > 0 && (
        <>
          {viewMode === "cards" ? (
            /* Card Grid: Responsive 1 col on mobile, 2 cols on tablet/desktop */
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
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
            /* Table View: Clean responsive data table */
            <div className="rounded-2xl border border-[#E2DCD5] bg-white overflow-hidden shadow-xs">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#FAF8F5] text-[#475569] uppercase font-bold border-b border-[#E2DCD5]">
                    <tr>
                      <th className="px-4 py-3">{language === "ta" ? "ஜாதக எண்" : "Horoscope No."}</th>
                      <th className="px-4 py-3">{language === "ta" ? "பெயர்" : "Subject Name"}</th>
                      <th className="px-4 py-3">{language === "ta" ? "பிறந்த தேதி & நேரம்" : "Birth Date & Time"}</th>
                      <th className="px-4 py-3">{language === "ta" ? "பிறந்த இடம்" : "Birthplace"}</th>
                      <th className="px-4 py-3">{language === "ta" ? "அயனாம்சம்" : "Ayanamsa"}</th>
                      <th className="px-4 py-3">{language === "ta" ? "கணிக்கப்பட்ட நாள்" : "Calculated At"}</th>
                      <th className="px-4 py-3 text-right">{language === "ta" ? "நடவடிக்கை" : "Action"}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#E2DCD5] text-[#334155]">
                    {horoscopes.map((item) => {
                      const seqText = formatHoroscopeSequence(item.display_number, language);
                      const birthDateStr = formatBirthDate(item.birth_date, language);
                      const birthTimeStr = formatBirthTime(item.birth_time);
                      const calcDateStr = item.created_at
                        ? formatBirthDate(item.created_at.split("T")[0], language)
                        : "—";
                      const ayanamsaLabel =
                        item.ayanamsa_id === 1 ? "KP" : item.ayanamsa_id === 2 ? "Raman" : "Lahiri";

                      return (
                        <tr key={item.id} className="hover:bg-[#FAF8F5]/80 transition-colors">
                          <td className="px-4 py-3.5">
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-serif font-bold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
                              {seqText}
                            </span>
                          </td>
                          <td className="px-4 py-3.5 font-bold text-[#0F172A]">
                            {item.person_name?.trim() || t.unnamedHoroscope}
                          </td>
                          <td className="px-4 py-3.5 text-[#475569]">
                            <div>{birthDateStr}</div>
                            <div className="text-[11px] font-mono text-[#64748B]">
                              {birthTimeStr} {item.timezone ? `(${item.timezone})` : ""}
                            </div>
                          </td>
                          <td className="px-4 py-3.5 text-[#475569] max-w-[180px] truncate" title={item.birthplace}>
                            {item.birthplace || t.locationUnavailable}
                          </td>
                          <td className="px-4 py-3.5">
                            <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-[#FAF8F5] border border-[#E2DCD5]">
                              {ayanamsaLabel}
                            </span>
                          </td>
                          <td className="px-4 py-3.5 text-[#64748B] font-mono text-[11px]">
                            {calcDateStr}
                          </td>
                          <td className="px-4 py-3.5 text-right">
                            <div className="inline-flex items-center gap-1.5">
                              <Link
                                href={`/horoscope/results?id=${item.id}`}
                                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#0F172A] hover:bg-[#1E293B] text-white text-[11px] font-semibold transition-colors"
                                title={t.actionOpenHoroscope}
                              >
                                <span>{language === "ta" ? "திறக்க" : "Open"}</span>
                                <ExternalLink className="w-3 h-3 text-[#D8BD80]" />
                              </Link>
                              <button
                                type="button"
                                onClick={() => handleOpenEdit(item)}
                                className="p-1.5 rounded-lg border border-[#CBD5E1] bg-white hover:bg-[#FAF8F5] text-[#475569] hover:text-[#0F172A] transition-colors"
                                title={t.actionEdit}
                              >
                                <Edit3 className="w-3 h-3" />
                              </button>
                              <button
                                type="button"
                                onClick={() => setHoroscopeToDelete(item)}
                                className="p-1.5 rounded-lg border border-transparent hover:border-rose-200 hover:bg-rose-50 text-[#94A3B8] hover:text-rose-600 transition-colors"
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

      {/* 7. Pagination Controls */}
      {!isLoading && !errorMessage && totalPages > 1 && (
        <div className="pt-4 border-t border-[#E2DCD5] flex items-center justify-between gap-3 text-xs">
          <button
            type="button"
            onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
            disabled={currentPage <= 1}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-[#CBD5E1] bg-white hover:bg-[#FAF8F5] text-[#0F172A] font-semibold transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
          >
            <ChevronLeft className="w-4 h-4" />
            <span>{t.prevPage}</span>
          </button>

          <span className="font-medium text-[#64748B]">
            {t.pageIndicator
              .replace("{current}", currentPage.toString())
              .replace("{total}", totalPages.toString())}
          </span>

          <button
            type="button"
            onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
            disabled={currentPage >= totalPages}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-[#CBD5E1] bg-white hover:bg-[#FAF8F5] text-[#0F172A] font-semibold transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
          >
            <span>{t.nextPage}</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Edit Modal */}
      <SavedHoroscopeEditModal
        horoscope={selectedHoroscope}
        isOpen={isEditModalOpen}
        onClose={handleCloseEdit}
        onSuccess={handleEditSuccess}
      />

      {/* Delete Confirmation Modal for Table View */}
      {horoscopeToDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs">
          <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl border border-[#E2DCD5] space-y-4">
            <div className="flex items-center gap-2.5 text-rose-600">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <h4 className="font-bold text-sm text-[#0F172A]">
                {language === "ta" ? "ஜாதகத்தை நீக்கவா?" : "Delete Horoscope?"}
              </h4>
            </div>
            <p className="text-xs text-[#64748B] leading-relaxed">
              {language === "ta"
                ? `"${horoscopeToDelete.person_name || 'ஜாதகம்'}" (${formatHoroscopeSequence(horoscopeToDelete.display_number, 'ta')}) நிரந்தரமாக நீக்கப்படும். இந்த வரிசை எண் மீண்டும் பயன்படுத்தப்படாது.`
                : `"${horoscopeToDelete.person_name || 'Horoscope'}" (${formatHoroscopeSequence(horoscopeToDelete.display_number, 'en')}) will be permanently deleted. This sequential number will remain unused.`}
            </p>
            <div className="flex items-center justify-end gap-2 pt-2 border-t border-[#E2DCD5]">
              <button
                type="button"
                onClick={() => setHoroscopeToDelete(null)}
                disabled={isDeleting}
                className="px-3 py-1.5 rounded-lg border border-[#CBD5E1] bg-white hover:bg-[#FAF8F5] text-xs font-semibold text-[#475569]"
              >
                {language === "ta" ? "ரத்து" : "Cancel"}
              </button>
              <button
                type="button"
                onClick={confirmDeleteAction}
                disabled={isDeleting}
                className="px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold disabled:opacity-50"
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
