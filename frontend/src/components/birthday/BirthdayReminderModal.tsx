"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import {
  Cake,
  Gift,
  Calendar,
  Phone,
  MessageCircle,
  CheckCircle2,
  AlertTriangle,
  X,
  ExternalLink,
  Clock,
  Sparkles,
  Edit2,
  Check,
  Eye,
  EyeOff,
  Copy,
} from "lucide-react";
import {
  SUPPORTED_COUNTRY_CODES,
  generateWhatsAppBirthdayLink,
  getBirthdayWishMessageText,
} from "@/lib/phone-utils";

export interface BirthdayCelebrant {
  id: string;
  fullName: string;
  birthDate: string;
  countryCode?: string;
  phoneNumber?: string;
  normalizedPhone?: string;
  whatsappNumber?: string;
  displayPhone?: string;
  whatsappLink?: string;
  hasValidPhone: boolean;
  warningMessage?: string | null;
  wishSent: boolean;
  wishSentAt?: string | null;
}

interface BirthdayReminderModalProps {
  isOpen?: boolean;
  onClose?: () => void;
  // If true, automatically queries on mount when authenticated and opens if celebrants exist
  autoCheckOnLogin?: boolean;
}

export function BirthdayReminderModal({
  isOpen: controlledIsOpen,
  onClose: controlledOnClose,
  autoCheckOnLogin = false,
}: BirthdayReminderModalProps) {
  const { language } = useLanguage();
  const { isAuthenticated, role } = useAuth();
  const isAdmin = role === "admin";

  const [internalIsOpen, setInternalIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [celebrants, setCelebrants] = useState<BirthdayCelebrant[]>([]);
  const [todayKolkata, setTodayKolkata] = useState<string>("");
  const [markingId, setMarkingId] = useState<string | null>(null);

  // Wish Language: Default to Tamil as requested
  const [wishLang, setWishLang] = useState<"ta" | "en">("ta");
  const [previewId, setPreviewId] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // State for inline "Add Number / Update Contact"
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editCountryCode, setEditCountryCode] = useState<string>("+91");
  const [editPhone, setEditPhone] = useState<string>("");
  const [isSavingContact, setIsSavingContact] = useState<boolean>(false);
  const [contactSaveError, setContactSaveError] = useState<string | null>(null);

  const isOpen = controlledIsOpen !== undefined ? controlledIsOpen : internalIsOpen;
  const handleClose = () => {
    if (controlledOnClose) {
      controlledOnClose();
    } else {
      setInternalIsOpen(false);
    }
  };

  const fetchBirthdays = useCallback(async (isAuto = false) => {
    if (!isAuthenticated) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/customers/birthdays?lang=${wishLang}`);
      if (res.ok) {
        const data = await res.json();
        setCelebrants(data.celebrants || []);
        setTodayKolkata(data.todayKolkata || "");

        if (isAuto && data.celebrants && data.celebrants.length > 0) {
          // Check if already dismissed today in this session
          const sessionKey = `birthday_dismissed_${data.todayKolkata}`;
          const alreadyDismissed = sessionStorage.getItem(sessionKey);
          if (!alreadyDismissed) {
            setInternalIsOpen(true);
          }
        }
      }
    } catch (err) {
      console.warn("Could not load birthday reminders:", err);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, wishLang]);

  // Initial check on login
  useEffect(() => {
    if (autoCheckOnLogin && isAuthenticated) {
      fetchBirthdays(true);
    }
  }, [autoCheckOnLogin, isAuthenticated, fetchBirthdays]);

  // Fetch when opened explicitly
  useEffect(() => {
    if (isOpen) {
      fetchBirthdays(false);
    }
  }, [isOpen, fetchBirthdays]);

  // Manual action: mark wish as sent
  const handleMarkWishSent = async (customerId: string) => {
    setMarkingId(customerId);
    try {
      const res = await fetch("/api/customers/birthdays", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ customer_id: customerId }),
      });
      if (res.ok) {
        const nowIso = new Date().toISOString();
        setCelebrants((prev) =>
          prev.map((c) =>
            c.id === customerId ? { ...c, wishSent: true, wishSentAt: nowIso } : c
          )
        );
      }
    } catch (err) {
      console.error("Failed to mark birthday wish as sent:", err);
    } finally {
      setMarkingId(null);
    }
  };

  // Inline save action for adding or updating contact
  const handleSaveContact = async (celebrant: BirthdayCelebrant) => {
    if (!editPhone.trim()) {
      setContactSaveError(language === "ta" ? "வாட்ஸ்அப் எண் தேவை." : "WhatsApp number is required.");
      return;
    }
    setIsSavingContact(true);
    setContactSaveError(null);
    try {
      const res = await fetch(`/api/customers/${encodeURIComponent(celebrant.id)}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          full_name: celebrant.fullName,
          birth_date: celebrant.birthDate,
          country_code: editCountryCode,
          phone_number: editPhone.trim(),
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Failed to update customer contact.");
      }
      const updatedCust = data.customer;
      const newWaLink = generateWhatsAppBirthdayLink(
        updatedCust.whatsapp_number,
        updatedCust.full_name,
        wishLang
      );
      setCelebrants((prev) =>
        prev.map((c) =>
          c.id === celebrant.id
            ? {
                ...c,
                countryCode: updatedCust.country_code,
                phoneNumber: updatedCust.phone_number,
                normalizedPhone: updatedCust.normalized_phone,
                whatsappNumber: updatedCust.whatsapp_number,
                hasValidPhone: true,
                whatsappLink: newWaLink,
                warningMessage: null,
              }
            : c
        )
      );
      setEditingId(null);
      setEditPhone("");
    } catch (err: any) {
      setContactSaveError(err.message || "Failed to save phone number.");
    } finally {
      setIsSavingContact(false);
    }
  };

  const handleCopyWish = (celebrant: BirthdayCelebrant) => {
    const text = getBirthdayWishMessageText(celebrant.fullName, wishLang);
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      navigator.clipboard.writeText(text);
      setCopiedId(celebrant.id);
      setTimeout(() => setCopiedId(null), 2500);
    }
  };

  const handleDismiss = () => {
    if (todayKolkata) {
      sessionStorage.setItem(`birthday_dismissed_${todayKolkata}`, "true");
    }
    handleClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl border border-[#E2DCD5] shadow-2xl max-w-2xl w-full max-h-[90vh] flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header Banner */}
        <div className="relative bg-gradient-to-r from-[#102A4C] via-[#1E3A61] to-[#B8862B] p-5 sm:p-6 text-white flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 flex items-center justify-center shrink-0">
              <Cake className="w-6 h-6 text-[#F9D776]" />
            </div>
            <div>
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-white/15 text-white/90 border border-white/20 mb-1">
                <Sparkles className="w-3 h-3 text-[#F9D776]" />
                <span>Asia/Kolkata (IST) Today: {todayKolkata || "Today"}</span>
              </div>
              <h2 className="font-serif text-lg sm:text-xl font-bold tracking-tight">
                {language === "ta"
                  ? "வாடிக்கையாளர் பிறந்தநாள் நினைவூட்டல்கள்"
                  : "Customer Birthday Reminders"}
              </h2>
              <p className="text-xs text-white/80 mt-0.5">
                {language === "ta"
                  ? "இன்றைய பிறந்தநாள் கொண்டாடும் வாடிக்கையாளர்களுக்கு வாட்ஸ்அப் மூலம் வாழ்த்து அனுப்புங்கள்."
                  : "Celebrate with your clients by sending personalized WhatsApp birthday blessings."}
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={handleDismiss}
            className="p-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-white/90 transition-colors"
            aria-label="Close dialog"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Celebrants Body */}
        <div className="p-5 sm:p-6 overflow-y-auto space-y-4 flex-1">
          {loading ? (
            <div className="py-12 flex flex-col items-center justify-center text-[#64748B] text-xs gap-3">
              <div className="w-8 h-8 border-3 border-[#B8862B] border-t-transparent rounded-full animate-spin" />
              <span>Checking birthday records in Asia/Kolkata timezone...</span>
            </div>
          ) : celebrants.length === 0 ? (
            <div className="py-12 text-center text-[#64748B] space-y-2">
              <Gift className="w-10 h-10 text-[#CBD5E1] mx-auto" />
              <h4 className="font-serif font-bold text-sm text-[#0F172A]">
                {language === "ta"
                  ? "இன்று பிறந்தநாள் எதுவும் இல்லை"
                  : "No Client Birthdays Today"}
              </h4>
              <p className="text-xs max-w-sm mx-auto">
                {language === "ta"
                  ? "இன்றைய தேதியில் எந்த வாடிக்கையாளருக்கும் பிறந்தநாள் பதிவு செய்யப்படவில்லை."
                  : "None of your saved clients have a birthday matching today's date in Asia/Kolkata."}
              </p>
            </div>
          ) : (
            <div className="space-y-3.5">
              <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-[#64748B] px-1 bg-amber-50/60 p-2.5 rounded-xl border border-amber-200/70">
                <div className="flex items-center gap-2">
                  <span>
                    {language === "ta" ? "கொண்டாட்டக்காரர்கள்:" : "Celebrants found:"}{" "}
                    <strong className="text-[#0F172A]">{celebrants.length}</strong>
                  </span>
                  <span className="text-[11px] text-amber-700 bg-amber-100/70 border border-amber-200 px-2 py-0.5 rounded-md font-medium hidden sm:inline">
                    {language === "ta" ? "வாட்ஸ்அப் லிங்க் அனுப்பியதும் குறிக்கவும்" : "Manual Status Confirmation"}
                  </span>
                </div>

                {/* Wish Language Selector */}
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-semibold text-[#334155]">
                    {language === "ta" ? "வாழ்த்து மொழி:" : "Wish Language:"}
                  </span>
                  <div className="inline-flex rounded-lg border border-[#CBD5E1] p-0.5 bg-white shadow-xs">
                    <button
                      type="button"
                      onClick={() => setWishLang("ta")}
                      className={`px-2.5 py-0.5 rounded-md text-[11px] font-semibold transition-all ${
                        wishLang === "ta"
                          ? "bg-[#102A4C] text-white shadow-xs"
                          : "text-[#64748B] hover:text-[#0F172A]"
                      }`}
                    >
                      தமிழ்
                    </button>
                    <button
                      type="button"
                      onClick={() => setWishLang("en")}
                      className={`px-2.5 py-0.5 rounded-md text-[11px] font-semibold transition-all ${
                        wishLang === "en"
                          ? "bg-[#102A4C] text-white shadow-xs"
                          : "text-[#64748B] hover:text-[#0F172A]"
                      }`}
                    >
                      English
                    </button>
                  </div>
                </div>
              </div>

              {celebrants.map((celebrant) => {
                const activeWaLink =
                  celebrant.hasValidPhone && celebrant.whatsappNumber
                    ? generateWhatsAppBirthdayLink(
                        celebrant.whatsappNumber,
                        celebrant.fullName,
                        wishLang
                      )
                    : celebrant.whatsappLink;

                return (
                  <div
                    key={celebrant.id}
                    className="p-4 rounded-xl border border-[#E2DCD5] bg-[#FAF8F5] hover:bg-white transition-all space-y-3"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div>
                        <h4 className="font-serif font-bold text-base text-[#0F172A]">
                          {celebrant.fullName}
                        </h4>
                        <div className="flex items-center gap-3 text-xs text-[#64748B] mt-1 flex-wrap">
                          <span className="flex items-center gap-1 font-mono">
                            <Calendar className="w-3.5 h-3.5 text-[#B8860B]" />
                            <span>DOB: {celebrant.birthDate}</span>
                          </span>

                          {celebrant.normalizedPhone ? (
                            <span className="flex items-center gap-1 font-mono text-emerald-800 font-semibold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                              <Phone className="w-3 h-3 text-emerald-600" />
                              <span>{celebrant.normalizedPhone}</span>
                            </span>
                          ) : (
                            <span className="text-amber-800 bg-amber-50 px-2 py-0.5 rounded border border-amber-200 text-[11px] font-medium flex items-center gap-1">
                              <AlertTriangle className="w-3 h-3 text-amber-600 shrink-0" />
                              <span>{language === "ta" ? "வாட்ஸ்அப் எண் சேர்க்கப்படவில்லை" : "WhatsApp number not added."}</span>
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Wish Status Badge */}
                      <div>
                        {celebrant.wishSent ? (
                          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                            <span>
                              {language === "ta"
                                ? "வாழ்த்து அனுப்பப்பட்டது"
                                : "Wish Sent"}
                            </span>
                          </div>
                        ) : (
                          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-900 border border-amber-300">
                            <Clock className="w-3.5 h-3.5 text-amber-700" />
                            <span>
                              {language === "ta"
                                ? "வாழ்த்து அனுப்பப்படவில்லை"
                                : "Pending Wish"}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Warning if no valid phone */}
                    {!celebrant.hasValidPhone && (
                      <div className="p-2.5 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                        <span>
                          {celebrant.warningMessage ||
                            (language === "ta"
                              ? "வாட்ஸ்அப் எண் சேர்க்கப்படவில்லை."
                              : "WhatsApp number not added.")}
                        </span>
                      </div>
                    )}

                    {/* Action Controls */}
                    <div className="space-y-3 pt-2 border-t border-[#E8DEC8]">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          {/* 1. WhatsApp Click-to-Chat Button */}
                          {celebrant.hasValidPhone && activeWaLink ? (
                            <a
                              href={activeWaLink}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white bg-[#25D366] hover:bg-[#1EBE5D] shadow-xs transition-colors"
                              title="Opens WhatsApp with prefilled personalized message. Opening WhatsApp does not mark wish as sent."
                            >
                              <MessageCircle className="w-4 h-4" />
                              <span>
                                {language === "ta"
                                  ? "வாட்ஸ்அப் வாழ்த்து அனுப்பு"
                                  : "Send Birthday Wish via WhatsApp"}
                              </span>
                              <ExternalLink className="w-3.5 h-3.5 opacity-80" />
                            </a>
                          ) : (
                            /* Optional "Add Number" or "Update Contact" Action */
                            <button
                              type="button"
                              onClick={() => {
                                if (editingId === celebrant.id) {
                                  setEditingId(null);
                                } else {
                                  setEditingId(celebrant.id);
                                  setEditPhone(celebrant.phoneNumber || "");
                                  setEditCountryCode(celebrant.countryCode || "+91");
                                  setContactSaveError(null);
                                }
                              }}
                              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold text-amber-900 bg-amber-100 hover:bg-amber-200 border border-amber-300 transition-colors"
                            >
                              <Edit2 className="w-3.5 h-3.5 text-amber-800" />
                              <span>
                                {language === "ta"
                                  ? "எண்ணைச் சேர்க்கவும்"
                                  : "Add Number / Update Contact"}
                              </span>
                            </button>
                          )}

                          {/* Preview Message Toggle */}
                          <button
                            type="button"
                            onClick={() =>
                              setPreviewId(previewId === celebrant.id ? null : celebrant.id)
                            }
                            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold text-[#102A4C] bg-white hover:bg-[#F1ECE4] border border-[#CBD5E1] transition-colors"
                            title={language === "ta" ? "வாழ்த்துச் செய்தியைக் காண்க" : "Preview birthday message"}
                          >
                            {previewId === celebrant.id ? (
                              <>
                                <EyeOff className="w-3.5 h-3.5 text-[#64748B]" />
                                <span>{language === "ta" ? "மறை" : "Hide"}</span>
                              </>
                            ) : (
                              <>
                                <Eye className="w-3.5 h-3.5 text-[#B8860B]" />
                                <span>{language === "ta" ? "செய்தி" : "Preview"}</span>
                              </>
                            )}
                          </button>
                        </div>

                        {/* 2. Manual status update confirmation */}
                        <div>
                          {celebrant.wishSent ? (
                            <span className="text-[11px] text-[#64748B]">
                              Confirmed by admin
                              {celebrant.wishSentAt
                                ? ` on ${new Date(celebrant.wishSentAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`
                                : ""}
                            </span>
                          ) : (
                            <button
                              type="button"
                              onClick={() => handleMarkWishSent(celebrant.id)}
                              disabled={markingId === celebrant.id}
                              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold text-[#102A4C] bg-white hover:bg-[#F1ECE4] border border-[#CBD5E1] transition-colors disabled:opacity-50"
                            >
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                              <span>
                                {markingId === celebrant.id
                                  ? "Saving..."
                                  : language === "ta"
                                  ? "வாழ்த்தியதாகக் குறிக்கவும்"
                                  : "Mark Wish as Sent"}
                              </span>
                            </button>
                          )}
                        </div>
                      </div>

                      {/* Preview Box */}
                      {previewId === celebrant.id && (
                        <div className="p-3.5 bg-[#FFFDF9] rounded-xl border border-[#E2DCD5] space-y-2 text-xs shadow-inner animate-in fade-in duration-150">
                          <div className="flex items-center justify-between text-[11px] font-bold text-[#102A4C] border-b border-[#E8DEC8] pb-1.5">
                            <span className="flex items-center gap-1.5">
                              <Sparkles className="w-3.5 h-3.5 text-[#B8860B]" />
                              <span>
                                {language === "ta"
                                  ? "வாழ்த்து செய்தி முன்னோட்டம்:"
                                  : "Birthday Message Preview:"}
                              </span>
                            </span>
                            <button
                              type="button"
                              onClick={() => handleCopyWish(celebrant)}
                              className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#102A4C] hover:text-[#B8860B] px-2.5 py-1 rounded-lg bg-amber-50 hover:bg-amber-100 border border-amber-200 transition-colors"
                            >
                              {copiedId === celebrant.id ? (
                                <>
                                  <Check className="w-3 h-3 text-emerald-600" />
                                  <span className="text-emerald-700 font-bold">
                                    {language === "ta" ? "நகலெடுக்கப்பட்டது!" : "Copied!"}
                                  </span>
                                </>
                              ) : (
                                <>
                                  <Copy className="w-3 h-3 text-[#B8860B]" />
                                  <span>{language === "ta" ? "நகலெடு" : "Copy Message"}</span>
                                </>
                              )}
                            </button>
                          </div>
                          <div className="bg-white p-3 rounded-lg border border-[#E8DEC8] text-xs font-sans text-[#334155] whitespace-pre-wrap leading-relaxed max-h-56 overflow-y-auto">
                            {getBirthdayWishMessageText(celebrant.fullName, wishLang)}
                          </div>
                        </div>
                      )}

                    {/* 3. Inline Contact Update Form when expanded */}
                    {editingId === celebrant.id && (
                      <div className="p-3 bg-white rounded-xl border border-[#D8BD80] shadow-xs space-y-2.5 animate-in fade-in duration-150">
                        <div className="text-xs font-semibold text-[#0F172A] flex items-center gap-1.5">
                          <Phone className="w-3.5 h-3.5 text-[#B8860B]" />
                          <span>
                            {language === "ta"
                              ? "வாட்ஸ்அப் எண் சேர்க்க / புதுப்பிக்க:"
                              : "Add or Update WhatsApp Number:"}
                          </span>
                        </div>
                        <div className="flex flex-wrap sm:flex-nowrap gap-2">
                          <select
                            value={editCountryCode}
                            onChange={(e) => setEditCountryCode(e.target.value)}
                            className="w-28 px-2 py-1.5 text-xs rounded-lg border border-[#CBD5E1] bg-white text-[#0F172A]"
                          >
                            {SUPPORTED_COUNTRY_CODES.map((item) => (
                              <option key={item.code} value={item.code}>
                                {item.flag} {item.code}
                              </option>
                            ))}
                          </select>
                          <input
                            type="tel"
                            value={editPhone}
                            onChange={(e) => {
                              setEditPhone(e.target.value);
                              setContactSaveError(null);
                            }}
                            placeholder="e.g. 98765 43210"
                            className="flex-1 px-3 py-1.5 text-xs rounded-lg border border-[#CBD5E1] text-[#0F172A] focus:ring-1 focus:ring-[#B8860B]"
                          />
                          <button
                            type="button"
                            onClick={() => handleSaveContact(celebrant)}
                            disabled={isSavingContact}
                            className="px-3.5 py-1.5 bg-[#102A4C] hover:bg-[#1E3A61] text-white text-xs font-semibold rounded-lg transition-colors disabled:opacity-50 inline-flex items-center gap-1"
                          >
                            <Check className="w-3 h-3" />
                            <span>
                              {isSavingContact
                                ? "Saving..."
                                : language === "ta"
                                ? "சேமி"
                                : "Save Number"}
                            </span>
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              setEditingId(null);
                              setContactSaveError(null);
                            }}
                            className="px-2.5 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-medium rounded-lg transition-colors"
                          >
                            {language === "ta" ? "ரத்து" : "Cancel"}
                          </button>
                        </div>
                        {contactSaveError && (
                          <p className="text-xs text-rose-600 font-medium">{contactSaveError}</p>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 bg-[#FAF8F5] border-t border-[#E2DCD5] flex items-center justify-between">
          <p className="text-[11px] text-[#64748B]">
            {language === "ta"
              ? "குறிப்பு: வாட்ஸ்அப் திறப்பது தானாக வாழ்த்து அனுப்பப்பட்டதாகக் குறிக்காது."
              : "Note: Opening WhatsApp does not automatically mark wish as sent."}
          </p>

          <button
            type="button"
            onClick={handleDismiss}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-[#0F172A] bg-white border border-[#CBD5E1] hover:bg-[#F1ECE4] transition-colors"
          >
            {language === "ta" ? "மூடு" : "Close"}
          </button>
        </div>
      </div>
    </div>
  );
}
