"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { SavedHoroscopeItem } from "@/lib/types";
import { formatBirthDate, formatBirthTime, formatSerialNumber, formatDate, formatTime12 } from "@/lib/formatters";
import {
  Calendar,
  Clock,
  MapPin,
  Edit3,
  ExternalLink,
  Info,
  Trash2,
  Eye,
  MessageCircle,
  Sparkles,
  Star,
  Phone,
  Pin,
  Flame,
} from "lucide-react";

interface SavedHoroscopeCardProps {
  horoscope: SavedHoroscopeItem;
  onEdit: (horoscope: SavedHoroscopeItem) => void;
  onDelete?: (id: string) => Promise<void> | void;
  onTogglePin?: (id: string, currentPinned: boolean) => Promise<void> | void;
}

export function SavedHoroscopeCard({
  horoscope,
  onEdit,
  onDelete,
  onTogglePin,
}: SavedHoroscopeCardProps) {
  const { language, t } = useLanguage();
  const { user } = useAuth();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isPinning, setIsPinning] = useState(false);
  const isPinned = !!horoscope.is_pinned;

  const handlePinToggle = async () => {
    if (!onTogglePin || isPinning) return;
    setIsPinning(true);
    try {
      await onTogglePin(horoscope.id, isPinned);
    } finally {
      setIsPinning(false);
    }
  };

  const displayName = horoscope.person_name?.trim() || t.unnamedHoroscope || "Unnamed";
  const initial = displayName.charAt(0).toUpperCase() || "H";
  const idNumber = horoscope.display_number ? formatSerialNumber(horoscope.display_number) : (horoscope.id?.slice(0, 6) || "—");

  const birthDateFormatted = formatBirthDate(horoscope.birth_date, language);
  const birthTimeFormatted = formatBirthTime(horoscope.birth_time);
  const birthplaceText = horoscope.birthplace?.trim() || t.locationUnavailable || "Tamil Nadu";

  // Creation date/time formatted in DD/MM/YYYY
  const createdDateStr = horoscope.created_at ? formatDate(horoscope.created_at) : "";

  const createdTimeStr = horoscope.created_at ? formatTime12(null, horoscope.created_at) : "";

  const isKp = horoscope.ayanamsa_id === 1 || horoscope.ayanamsa_id === 3;
  const ayanamsaLabel =
    horoscope.ayanamsa_id === 1
      ? "KP"
      : horoscope.ayanamsa_id === 2
      ? "Raman"
      : horoscope.ayanamsa_id === 3
      ? "KP New"
      : "Lahiri";
  const typeText = isKp
    ? (language === "ta" ? "கே.பி" : "KP")
    : (language === "ta" ? "வேத" : "Vedic");

  // WhatsApp digits
  const waDigits = (horoscope.whatsapp_number || horoscope.normalized_phone || horoscope.customer_phone || "").replace(/\D/g, "");

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
    <div
      data-testid="saved-horoscope-card"
      className={`rounded-2xl border transition-all flex flex-col justify-between group ${
        isPinned
          ? "border-[#B4872B] bg-gradient-to-b from-[#FFFDF9] via-white to-white p-4 sm:p-5 shadow-sm ring-1 ring-[#B4872B]/35 hover:shadow-md"
          : "border-[#D9DEE7] hover:border-[#B4872B] bg-white p-4 sm:p-5 shadow-xs hover:shadow-md"
      }`}
    >
      <div>
        {/* Top Section: Avatar, ID, Name, Language Badge */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-start gap-3 min-w-0">
            {/* Avatar Circle */}
            <div className="w-11 h-11 rounded-full bg-[#153F6B] text-white flex items-center justify-center font-bold text-base shrink-0 border border-[#B4872B]/30 shadow-2xs">
              {initial}
            </div>

            <div className="min-w-0 space-y-1">
              {/* ID & Name */}
              <div className="flex items-center gap-2 flex-wrap">
                <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-[#FAF2DE] text-[#B4872B] border border-[#D8BD80]">
                  {idNumber}
                </span>
                {isPinned && (
                  <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-300 shadow-2xs">
                    <Pin className="w-2.5 h-2.5 fill-amber-700 text-amber-800 rotate-45" />
                    <span>{language === "ta" ? "முதன்மையானது" : "Pinned"}</span>
                  </span>
                )}
                {(horoscope as any).gender && (
                  <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold border ${
                    (horoscope as any).gender === "female"
                      ? "bg-rose-50 text-rose-700 border-rose-200"
                      : "bg-blue-50 text-blue-700 border-blue-200"
                  }`}>
                    {(horoscope as any).gender === "female"
                      ? (language === "ta" ? "👩 பெண்" : "👩 Female")
                      : (language === "ta" ? "👨 ஆண்" : "👨 Male")}
                  </span>
                )}
                <h3
                  className="font-bold text-sm sm:text-base text-[#183047] truncate"
                  title={displayName}
                >
                  {displayName}
                </h3>
              </div>

              {/* Date & Time */}
              <div className="flex items-center gap-1.5 text-xs text-[#8190A6]">
                <Calendar className="w-3.5 h-3.5 text-[#8190A6] shrink-0" />
                <span className="truncate">
                  {birthDateFormatted} {birthTimeFormatted}
                </span>
              </div>

              {/* Birth Place */}
              <div className="flex items-center gap-1.5 text-xs text-[#8190A6]">
                <MapPin className="w-3.5 h-3.5 text-[#8190A6] shrink-0" />
                <span className="truncate" title={birthplaceText}>
                  {birthplaceText}
                </span>
              </div>
            </div>
          </div>

          {/* Top Right Badges & Pin Toggle */}
          <div className="shrink-0 flex flex-col items-end gap-1">
            {onTogglePin && (
              <button
                type="button"
                onClick={handlePinToggle}
                disabled={isPinning}
                className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold border transition-all cursor-pointer shadow-2xs ${
                  isPinned
                    ? "bg-amber-100 text-amber-900 border-amber-400 hover:bg-amber-200 ring-2 ring-amber-300/40"
                    : "bg-white text-slate-700 border-[#CBD5E1] hover:text-amber-800 hover:border-amber-400 hover:bg-amber-50"
                }`}
                title={
                  isPinned
                    ? t.unpinHoroscope || (language === "ta" ? "பின்னை நீக்கு" : "Unpin from top")
                    : t.pinHoroscope || (language === "ta" ? "மேலே பின் செய்" : "Pin to top")
                }
              >
                <Pin className={`w-3 h-3 ${isPinned ? "fill-amber-600 text-amber-800 rotate-45" : ""}`} />
                <span>
                  {isPinned
                    ? (language === "ta" ? "பின் நீக்கு" : "Unpin")
                    : (language === "ta" ? "பின் செய்" : "Pin")}
                </span>
              </button>
            )}
            <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#F2F3F5] text-[#8190A6] border border-[#D9DEE7]">
              {language === "ta" ? "🌐 TA" : "🌐 EN"}
            </span>

            {/* Vedic or KP Type Badge */}
            <span
              className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                isKp
                  ? "bg-amber-50 text-amber-800 border-amber-300"
                  : "bg-[#EBF2FE] text-[#153F6B] border-[#BFDBFE]"
              }`}
            >
              {typeText} ({ayanamsaLabel})
            </span>
          </div>
        </div>

        {/* WhatsApp Customer Contact Details if present */}
        {waDigits.length >= 7 && (
          <div className="mt-2.5 mb-2 px-2.5 py-1.5 rounded-lg bg-emerald-50/70 border border-emerald-200/80 flex items-center justify-between gap-2 text-xs">
            <div className="flex items-center gap-1.5 text-emerald-800">
              <Phone className="w-3 h-3 text-emerald-600" />
              <span className="font-mono text-[11px] font-semibold">
                {horoscope.normalized_phone || horoscope.customer_phone}
              </span>
            </div>
            <a
              href={`https://wa.me/${waDigits}`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold text-emerald-700 bg-white hover:bg-emerald-100 border border-emerald-300 transition-colors"
              title="Open WhatsApp Chat"
            >
              <MessageCircle className="w-3 h-3 text-emerald-600" />
              <span>Chat</span>
            </a>
          </div>
        )}
      </div>

      {/* Bottom Row: Author/Timestamp + Actions */}
      <div className="mt-3 pt-3 border-t border-[#F2F3F5]">
        {showDeleteConfirm ? (
          <div className="p-2.5 rounded-xl bg-rose-50 border border-rose-200 text-xs flex items-center justify-between gap-2">
            <span className="text-rose-800 font-semibold text-[11px]">
              {language === "ta" ? "நீக்கவா?" : "Delete?"}
            </span>
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={handleDelete}
                disabled={isDeleting}
                className="px-2.5 py-1 rounded bg-rose-600 hover:bg-rose-700 text-white font-bold text-[11px] disabled:opacity-50 cursor-pointer"
              >
                {isDeleting ? "..." : language === "ta" ? "ஆம்" : "Yes"}
              </button>
              <button
                type="button"
                onClick={() => setShowDeleteConfirm(false)}
                disabled={isDeleting}
                className="px-2 py-1 rounded border border-rose-300 bg-white text-rose-800 text-[11px] cursor-pointer"
              >
                {language === "ta" ? "ரத்து" : "Cancel"}
              </button>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-between gap-2">
            {/* Generation Date & Time */}
            <div className="text-[11px] text-[#8190A6] flex items-center gap-1 min-w-0 truncate" title={createdDateStr && createdTimeStr ? `${createdDateStr}, ${createdTimeStr}` : undefined}>
              <Clock className="w-3 h-3 text-[#8190A6] shrink-0" />
              <span className="truncate">
                {createdDateStr && createdTimeStr
                  ? `${createdDateStr}, ${createdTimeStr}`
                  : createdDateStr || createdTimeStr}
              </span>
            </div>

            {/* Actions: Edit, Delete, KP Events, View */}
            <div className="flex items-center gap-1.5 shrink-0">
              {onTogglePin && (
                <button
                  type="button"
                  onClick={handlePinToggle}
                  disabled={isPinning}
                  className={`p-1.5 rounded-lg border transition-all cursor-pointer ${
                    isPinned
                      ? "border-amber-300 bg-amber-100 text-amber-900 hover:bg-amber-200 shadow-2xs"
                      : "border-[#D9DEE7] bg-white hover:bg-amber-50 hover:border-amber-300 text-[#8190A6] hover:text-amber-700"
                  }`}
                  title={
                    isPinned
                      ? t.unpinHoroscope || (language === "ta" ? "பின்னை நீக்கு" : "Unpin from top")
                      : t.pinHoroscope || (language === "ta" ? "மேலே பின் செய்" : "Pin to top")
                  }
                  aria-label={isPinned ? "Unpin horoscope" : "Pin horoscope to top"}
                >
                  <Pin className={`w-3.5 h-3.5 ${isPinned ? "fill-amber-600 text-amber-800 rotate-45" : ""}`} />
                </button>
              )}
              <button
                type="button"
                onClick={() => onEdit(horoscope)}
                className="p-1.5 rounded-lg border border-[#D9DEE7] bg-white hover:bg-[#F2F3F5] text-[#183047] hover:text-[#153F6B] transition-colors cursor-pointer"
                title={t.actionEdit || "Edit"}
                aria-label="Edit horoscope metadata"
              >
                <Edit3 className="w-3.5 h-3.5" />
              </button>

              {onDelete && (
                <button
                  type="button"
                  onClick={() => setShowDeleteConfirm(true)}
                  className="p-1.5 rounded-lg border border-[#D9DEE7] bg-white hover:bg-rose-50 text-[#8190A6] hover:text-rose-600 transition-colors cursor-pointer"
                  title={t.deleteHoroscope || "Delete"}
                  aria-label="Delete horoscope"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              )}

              {/* Dasa Bukthi Palangal Direct Action */}
              <Link
                href={`/horoscope/results?id=${horoscope.id}&tab=dasa-palangal`}
                className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-amber-300 hover:border-[#B4872B] bg-amber-50/80 hover:bg-amber-100 text-xs font-semibold text-[#8C6D23] transition-colors"
                title={language === "ta" ? "தசா புத்தி பலன்கள் (Dasa Bukthi Palangal)" : "Dasa Bukthi Palangal"}
              >
                <Sparkles className="w-3.5 h-3.5 text-[#B4872B]" />
                <span className="hidden sm:inline">{language === "ta" ? "தசா பலன்" : "Dasa Palan"}</span>
              </Link>
              {/* Natchathira Deep Analysis Direct Action */}
              <Link
                href={`/horoscope/results?id=${horoscope.id}&tab=natchathira`}
                className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-indigo-200 hover:border-indigo-400 bg-indigo-50/80 hover:bg-indigo-100 text-xs font-semibold text-indigo-800 transition-colors"
                title={language === "ta" ? "நட்சத்திர ஆய்வு (Nakshatra Deep Analysis)" : "Nakshatra Deep Analysis"}
              >
                <Star className="w-3.5 h-3.5 text-indigo-600 fill-indigo-100" />
                <span className="hidden sm:inline">{language === "ta" ? "நட்சத்திரம்" : "Nakshatra"}</span>
              </Link>

              {/* Instant Revelation Teleprompter Direct Action */}
              <Link
                href={`/tools/instant-revelation?id=${horoscope.id}`}
                className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-amber-400 bg-amber-50 hover:bg-amber-100 text-xs font-semibold text-[#8C6D23] transition-colors"
                title={language === "ta" ? "வாடிக்கையாளர் நேரடி வாக்கு பலகை (Instant Revelation Teleprompter)" : "Instant Revelation Teleprompter"}
              >
                <Flame className="w-3.5 h-3.5 text-[#B4872B] animate-pulse" />
                <span className="hidden sm:inline">{language === "ta" ? "வாக்கு பலகை" : "Revelation"}</span>
              </Link>

              {/* View Action Button matching Screenshot 2 */}
              <Link
                href={`/horoscope/results?id=${horoscope.id}`}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#D9DEE7] hover:border-[#153F6B] bg-white hover:bg-[#EBF2FE] text-xs font-semibold text-[#153F6B] transition-colors"
                title={t.actionOpenHoroscope || "View Horoscope"}
              >
                <Eye className="w-3.5 h-3.5 text-[#153F6B]" />
                <span>{language === "ta" ? "காண்க" : "View"}</span>
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
