"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { SavedHoroscopeItem } from "@/lib/types";
import {
  formatBirthDate,
  formatBirthTime,
} from "@/lib/formatters";
import { formatHoroscopeSequence } from "@/lib/horoscope-storage-utils";
import {
  Calendar,
  Clock,
  MapPin,
  Edit3,
  ExternalLink,
  Info,
  Trash2,
  Sliders,
  Check,
  X,
  Sparkles,
} from "lucide-react";

interface SavedHoroscopeCardProps {
  horoscope: SavedHoroscopeItem;
  onEdit: (horoscope: SavedHoroscopeItem) => void;
  onDelete?: (id: string) => Promise<void> | void;
}

export function SavedHoroscopeCard({
  horoscope,
  onEdit,
  onDelete,
}: SavedHoroscopeCardProps) {
  const { language, t } = useLanguage();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const sequenceText = formatHoroscopeSequence(horoscope.display_number, language);
  const birthDateFormatted = formatBirthDate(horoscope.birth_date, language);
  const birthTimeFormatted = formatBirthTime(horoscope.birth_time);
  const calculatedDateFormatted = horoscope.created_at
    ? formatBirthDate(horoscope.created_at.split("T")[0], language)
    : "—";
  const birthplaceText = horoscope.birthplace?.trim() || t.locationUnavailable;
  const displayName = horoscope.person_name?.trim() || t.unnamedHoroscope;

  const ayanamsaName =
    horoscope.ayanamsa_id === 1
      ? "KP"
      : horoscope.ayanamsa_id === 2
      ? "Raman"
      : "Lahiri";

  // Check if record was edited after creation
  const isEdited =
    horoscope.updated_at &&
    horoscope.created_at &&
    new Date(horoscope.updated_at).getTime() - new Date(horoscope.created_at).getTime() > 1000;

  const handleDelete = async () => {
    if (!onDelete) return;
    setIsDeleting(true);
    try {
      await onDelete(horoscope.id);
    } finally {
      setIsDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  return (
    <div className="relative rounded-2xl border border-[#E2DCD5] bg-white p-5 sm:p-6 shadow-xs hover:shadow-md transition-all duration-200 flex flex-col justify-between group">
      <div>
        {/* 1. Top Area: Sequential Number Badge conforming to specification */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-serif font-bold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
            <span>{sequenceText}</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[11px] font-mono text-[#64748B] px-2 py-0.5 rounded bg-[#FAF8F5] border border-[#E2DCD5]">
              {ayanamsaName}
            </span>

            {isEdited && (
              <span
                className="inline-flex items-center gap-1 text-[11px] font-medium text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full"
                title={t.editedWithoutRecalcNotice}
              >
                <Info className="w-3 h-3 text-amber-600 shrink-0" />
                <span>{t.editedWithoutRecalcBadge}</span>
              </span>
            )}
          </div>
        </div>

        {/* 2. Subject's Name: Main Heading */}
        <h3
          className="font-serif text-xl sm:text-2xl font-bold text-[#0F172A] tracking-tight leading-snug truncate mb-4"
          title={displayName}
        >
          {displayName}
        </h3>

        {/* 3. Core Birth Details & Metadata */}
        <div className="space-y-2 text-xs sm:text-sm text-[#334155] border-t border-[#F1ECE4] pt-3.5 mb-5">
          <div className="flex items-baseline gap-2">
            <span className="text-[#64748B] font-medium min-w-[80px] flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-[#B8860B] shrink-0" />
              <span>{t.birthDateLabel}:</span>
            </span>
            <span className="font-semibold text-[#0F172A]">
              {birthDateFormatted}
            </span>
          </div>

          <div className="flex items-baseline gap-2">
            <span className="text-[#64748B] font-medium min-w-[80px] flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-[#B8860B] shrink-0" />
              <span>{t.birthTimeLabel}:</span>
            </span>
            <span className="font-semibold text-[#0F172A] font-mono">
              {birthTimeFormatted}
            </span>
            {horoscope.timezone && (
              <span className="text-[11px] text-[#64748B] truncate">
                ({horoscope.timezone})
              </span>
            )}
          </div>

          <div className="flex items-baseline gap-2">
            <span className="text-[#64748B] font-medium min-w-[80px] flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-[#B8860B] shrink-0" />
              <span>{t.birthPlaceLabel}:</span>
            </span>
            <span className="font-medium text-[#0F172A] truncate" title={birthplaceText}>
              {birthplaceText}
            </span>
          </div>

          <div className="flex items-baseline gap-2 text-xs text-[#64748B] pt-1 border-t border-[#F1ECE4]/60">
            <span className="min-w-[80px] flex items-center gap-1.5">
              <Sliders className="w-3 h-3 text-[#94A3B8] shrink-0" />
              <span>{language === "ta" ? "கணிக்கப்பட்ட நாள்:" : "Calculated:"}</span>
            </span>
            <span className="font-mono text-[11px] text-[#475569]">
              {calculatedDateFormatted}
            </span>
          </div>
        </div>
      </div>

      {/* 4. Action Buttons */}
      <div className="pt-4 border-t border-[#F1ECE4]">
        {showDeleteConfirm ? (
          <div className="p-2.5 rounded-xl bg-rose-50 border border-rose-200 text-xs flex items-center justify-between gap-2">
            <span className="text-rose-800 font-semibold text-[11px]">
              {language === "ta" ? "நீக்கவா? உறுதிப்படுத்தவும்." : "Confirm deletion?"}
            </span>
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={handleDelete}
                disabled={isDeleting}
                className="px-2.5 py-1 rounded bg-rose-600 hover:bg-rose-700 text-white font-bold text-[11px] disabled:opacity-50 cursor-pointer"
              >
                {isDeleting ? "..." : language === "ta" ? "ஆம், நீக்கு" : "Delete"}
              </button>
              <button
                type="button"
                onClick={() => setShowDeleteConfirm(false)}
                disabled={isDeleting}
                className="px-2 py-1 rounded border border-rose-300 bg-white hover:bg-rose-100 text-rose-800 text-[11px] cursor-pointer"
              >
                {language === "ta" ? "ரத்து" : "Cancel"}
              </button>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => onEdit(horoscope)}
              className="inline-flex items-center justify-center gap-1 px-3 py-2 rounded-xl border border-[#CBD5E1] bg-white hover:bg-[#FAF8F5] text-xs font-semibold text-[#0F172A] shadow-2xs hover:border-[#94A3B8] transition-all cursor-pointer"
              title={t.actionEdit}
            >
              <Edit3 className="w-3.5 h-3.5 text-[#64748B]" />
              <span className="hidden sm:inline">{t.actionEdit}</span>
            </button>

            {onDelete && (
              <button
                type="button"
                onClick={() => setShowDeleteConfirm(true)}
                className="p-2 rounded-xl border border-transparent hover:border-rose-200 hover:bg-rose-50 text-[#94A3B8] hover:text-rose-600 transition-colors cursor-pointer"
                title={t.deleteHoroscope || "Delete"}
                aria-label="Delete horoscope"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            )}

            <Link
              href={`/horoscope/results?id=${horoscope.id}&tab=kp#kp-events`}
              className="inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl border border-amber-300 bg-amber-50/90 hover:bg-amber-100 text-xs font-semibold text-amber-900 shadow-2xs hover:border-amber-400 transition-all cursor-pointer"
              title={language === "ta" ? "கே.பி. நிகழ்வுகள்" : "KP Events"}
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-600" />
              <span>{language === "ta" ? "KP நிகழ்வுகள்" : "KP Events"}</span>
            </Link>

            <Link
              href={`/horoscope/results?id=${horoscope.id}`}
              className="flex-1 inline-flex items-center justify-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold text-white bg-[#0F172A] hover:bg-[#1E293B] shadow-xs transition-all"
            >
              <span>{t.actionOpenHoroscope}</span>
              <ExternalLink className="w-3.5 h-3.5 text-[#D8BD80]" />
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
