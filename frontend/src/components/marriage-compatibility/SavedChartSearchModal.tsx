"use client";

import React, { useState, useMemo, useEffect, useRef } from "react";
import { SavedHoroscopeItem } from "@/lib/types";
import {
  Search,
  X,
  Calendar,
  Clock,
  MapPin,
  Globe,
  User,
  Phone,
  CheckCircle2,
  RefreshCw,
  Sparkles,
} from "lucide-react";

interface SavedChartSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (item: SavedHoroscopeItem) => void;
  savedHoroscopes: SavedHoroscopeItem[];
  loading?: boolean;
  onRefresh?: () => void;
  partnerType: "groom" | "bride";
  language: "en" | "ta";
}

export function SavedChartSearchModal({
  isOpen,
  onClose,
  onSelect,
  savedHoroscopes,
  loading = false,
  onRefresh,
  partnerType,
  language,
}: SavedChartSearchModalProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const isGroom = partnerType === "groom";
  const themeColor = isGroom ? "#153F6B" : "#B4872B";
  const themeHover = isGroom ? "#1E4E8C" : "#996F1D";
  const themeLightBg = isGroom ? "bg-blue-50 text-[#153F6B]" : "bg-amber-50 text-[#996F1D]";

  // Focus search input when modal opens
  useEffect(() => {
    if (isOpen) {
      setSearchQuery("");
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  }, [isOpen]);

  // Handle escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  // Client-side filtering across name, date, time, place, chart #, and phone
  const filteredHoroscopes = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return savedHoroscopes;

    return savedHoroscopes.filter((item) => {
      const name = (item.person_name || "").toLowerCase();
      const birthDate = (item.birth_date || "").toLowerCase();
      const birthTime = (item.birth_time || "").toLowerCase();
      const place = (item.birthplace || item.location_name || "").toLowerCase();
      const dispNum = item.display_number ? String(item.display_number) : "";
      const phone = (
        item.customer_phone ||
        item.normalized_phone ||
        item.phone_number ||
        item.whatsapp_number ||
        ""
      ).toLowerCase();

      return (
        name.includes(q) ||
        birthDate.includes(q) ||
        birthTime.includes(q) ||
        place.includes(q) ||
        dispNum === q ||
        `#${dispNum}` === q ||
        phone.includes(q)
      );
    });
  }, [savedHoroscopes, searchQuery]);

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-150"
    >
      <div
        className="w-full max-w-2xl bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div
          className="px-5 py-4 text-white flex items-center justify-between shadow-sm shrink-0"
          style={{ backgroundColor: themeColor }}
        >
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-white/15 flex items-center justify-center font-bold text-sm">
              {isGroom ? "♂" : "♀"}
            </div>
            <div>
              <h3 className="text-base font-bold flex items-center gap-2">
                <span>
                  {isGroom
                    ? language === "ta"
                      ? "மணமகன் ஜாதகங்களைத் தேடுக"
                      : "Search Saved Charts for Groom"
                    : language === "ta"
                      ? "மணமகள் ஜாதகங்களைத் தேடுக"
                      : "Search Saved Charts for Bride"}
                </span>
                <span className="text-[11px] font-normal px-2 py-0.5 rounded-full bg-white/20">
                  {savedHoroscopes.length} {language === "ta" ? "ஜாதகங்கள்" : "charts"}
                </span>
              </h3>
              <p className="text-xs text-white/80">
                {language === "ta"
                  ? "ஜாதகத்தைத் தேர்வுசெய்து விவரங்களை உடனடியாகப் பெறவும்"
                  : "Search & select a saved chart to load full birth particulars"}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition cursor-pointer"
            aria-label="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Search controls */}
        <div className="p-4 bg-slate-50 border-b border-slate-200 space-y-3 shrink-0">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                ref={inputRef}
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={
                  language === "ta"
                    ? "பெயர், பிறந்த தேதி (YYYY-MM-DD), ஊர் அல்லது ஜாதக எண் (#) மூலம் தேடுக..."
                    : "Search by customer name, birth date (YYYY-MM-DD), place, or chart #..."
                }
                className="w-full pl-9 pr-8 py-2 text-xs sm:text-sm rounded-xl border border-slate-300 bg-white text-slate-800 placeholder:text-slate-400 focus:border-[#153F6B] focus:ring-1 focus:ring-[#153F6B] shadow-2xs"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery("")}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-0.5"
                  title={language === "ta" ? "நீக்குக" : "Clear"}
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {/* Refresh button */}
            {onRefresh && (
              <button
                type="button"
                onClick={onRefresh}
                disabled={loading}
                className="px-3 py-2 rounded-xl bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 text-xs font-semibold flex items-center gap-1.5 transition shadow-2xs"
                title={language === "ta" ? "புதுப்பிக்க" : "Refresh saved charts"}
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-blue-600" : ""}`} />
                <span className="hidden sm:inline">{language === "ta" ? "புதுப்பி" : "Refresh"}</span>
              </button>
            )}
          </div>

          <div className="flex items-center justify-between text-xs text-slate-500 px-1">
            <span>
              {searchQuery
                ? language === "ta"
                  ? `"${searchQuery}" க்கான முடிவுகள்: ${filteredHoroscopes.length} ஜாதகம்`
                  : `Results for "${searchQuery}": ${filteredHoroscopes.length} chart(s)`
                : language === "ta"
                  ? `மொத்தம் ${savedHoroscopes.length} சேமிக்கப்பட்ட ஜாதகங்கள் உள்ளன`
                  : `Showing ${savedHoroscopes.length} total saved charts`}
            </span>
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery("")}
                className="text-blue-700 hover:underline font-semibold cursor-pointer"
              >
                {language === "ta" ? "அனைத்தையும் காட்டு" : "Show all charts"}
              </button>
            )}
          </div>
        </div>

        {/* Results List */}
        <div className="p-4 overflow-y-auto flex-1 space-y-2.5 min-h-[220px]">
          {loading ? (
            <div className="py-12 flex flex-col items-center justify-center gap-2 text-slate-500 text-xs">
              <RefreshCw className="w-5 h-5 animate-spin text-blue-600" />
              <span>
                {language === "ta"
                  ? "சேமிக்கப்பட்ட ஜாதகங்கள் ஏற்றப்படுகின்றன..."
                  : "Loading your saved horoscopes..."}
              </span>
            </div>
          ) : savedHoroscopes.length === 0 ? (
            <div className="p-6 rounded-xl bg-amber-50 border border-amber-200 text-center text-amber-900 text-xs space-y-2">
              <p className="font-bold text-sm">
                {language === "ta"
                  ? "சேமிக்கப்பட்ட ஜாதகங்கள் எதுவும் கிடைக்கவில்லை."
                  : "No saved customer horoscopes found in your account."}
              </p>
              <p className="text-slate-600">
                {language === "ta"
                  ? "ஜாதகப் பக்கத்தில் புதிய ஜாதகங்களை உருவாக்கிய பிறகு இங்கு தானாகவே தோன்றும்."
                  : "Generate and save charts in the Horoscope tool, or switch to Direct Input mode."}
              </p>
            </div>
          ) : filteredHoroscopes.length === 0 ? (
            <div className="py-10 text-center text-slate-500 text-xs space-y-2">
              <p className="font-semibold text-slate-700 text-sm">
                {language === "ta"
                  ? `"${searchQuery}" என்ற தேடலுக்கு பொருத்தமான ஜாதகங்கள் இல்லை.`
                  : `No saved charts match "${searchQuery}".`}
              </p>
              <p className="text-slate-500">
                {language === "ta"
                  ? "பெயர், பிறந்த தேதி அல்லது ஜாதக எண் மூலம் மீண்டும் தேடவும்."
                  : "Try searching with a different name, date of birth (YYYY-MM-DD), or chart number."}
              </p>
              <button
                type="button"
                onClick={() => setSearchQuery("")}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 text-[#153F6B] font-semibold text-xs border border-blue-200 hover:bg-blue-100 transition cursor-pointer"
              >
                {language === "ta" ? "தேடலை நீக்கி அனைத்தையும் காட்டு" : "Clear Search & Show All"}
              </button>
            </div>
          ) : (
            filteredHoroscopes.map((h) => {
              const dispNum = h.display_number ? `#${h.display_number}` : null;
              const phone =
                h.customer_phone || h.normalized_phone || h.phone_number || h.whatsapp_number;

              return (
                <div
                  key={h.id}
                  className="rounded-xl border border-slate-200 bg-white hover:bg-slate-50/80 p-3 sm:p-3.5 transition flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-2xs hover:shadow-sm"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <div className="flex items-center gap-1.5 font-bold text-slate-900 text-sm">
                        <User className="w-3.5 h-3.5 text-slate-500" />
                        <span>{h.person_name || "Horoscope"}</span>
                      </div>
                      {dispNum && (
                        <span className="text-[11px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                          {dispNum}
                        </span>
                      )}
                      {phone && (
                        <span className="inline-flex items-center gap-1 text-[11px] text-slate-500 font-mono">
                          <Phone className="w-3 h-3 text-slate-400" />
                          {phone}
                        </span>
                      )}
                    </div>

                    <div className="text-xs text-slate-600 flex flex-wrap gap-x-3.5 gap-y-1 pt-0.5">
                      <span className="inline-flex items-center gap-1">
                        <Calendar className="w-3 h-3 text-slate-400" />
                        {h.birth_date}
                      </span>
                      <span className="inline-flex items-center gap-1">
                        <Clock className="w-3 h-3 text-slate-400" />
                        {h.birth_time || "N/A"}
                      </span>
                      <span className="inline-flex items-center gap-1">
                        <MapPin className="w-3 h-3 text-slate-400" />
                        {h.birthplace || h.location_name || "Location"}
                        {h.latitude !== undefined && h.longitude !== undefined && (
                          <span className="text-slate-400 text-[11px]">
                            ({Number(h.latitude).toFixed(2)}°, {Number(h.longitude).toFixed(2)}°)
                          </span>
                        )}
                      </span>
                      {h.timezone && (
                        <span className="inline-flex items-center gap-1 text-slate-400 text-[11px]">
                          <Globe className="w-3 h-3" />
                          {h.timezone}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Get Data action button */}
                  <div className="self-end sm:self-center shrink-0">
                    <button
                      type="button"
                      onClick={() => {
                        onSelect(h);
                        onClose();
                      }}
                      className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-white font-semibold text-xs shadow-2xs hover:shadow-xs transition cursor-pointer"
                      style={{ backgroundColor: themeColor }}
                      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = themeHover)}
                      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = themeColor)}
                      title={language === "ta" ? "இந்த ஜாதகத்தின் விவரங்களைப் பெறுக" : "Get data from this saved chart"}
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>{language === "ta" ? "விவரங்களைப் பெறுக" : "Get Data"}</span>
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="px-5 py-3 bg-slate-100 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500 shrink-0">
          <span className="flex items-center gap-1">
            <Sparkles className="w-3.5 h-3.5 text-amber-500" />
            {language === "ta"
              ? "தேர்ந்தெடுக்கப்பட்டவுடன் பிறப்பு விவரங்கள் படிவத்தில் தானாக நிரப்பப்படும்"
              : "Selecting a chart automatically loads birth date, time, location & coordinates"}
          </span>
          <button
            type="button"
            onClick={onClose}
            className="px-3 py-1.5 rounded-lg bg-white border border-slate-300 text-slate-700 font-semibold hover:bg-slate-50 transition cursor-pointer"
          >
            {language === "ta" ? "மூடுக" : "Close"}
          </button>
        </div>
      </div>
    </div>
  );
}
