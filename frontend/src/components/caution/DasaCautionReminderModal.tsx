"use client";

import React, { useState, useEffect, useCallback, useMemo } from "react";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import {
  ShieldAlert,
  AlertTriangle,
  Calendar,
  Phone,
  MessageCircle,
  CheckCircle2,
  X,
  Clock,
  Sparkles,
  Edit2,
  Check,
  Eye,
  EyeOff,
  Copy,
  ExternalLink,
  Flame,
  Search,
  Filter,
  Layers,
  ChevronDown,
  ChevronUp,
  RefreshCw,
} from "lucide-react";
import { DasaCautionItem, CautionSeverity } from "@/lib/dasa-caution-service";
import { SUPPORTED_COUNTRY_CODES, validateAndNormalizePhone } from "@/lib/phone-utils";

interface DasaCautionReminderModalProps {
  isOpen?: boolean;
  onClose?: () => void;
  autoCheckOnLogin?: boolean;
  onAlertsCountChange?: (count: number) => void;
}

export function DasaCautionReminderModal({
  isOpen: controlledIsOpen,
  onClose: controlledOnClose,
  autoCheckOnLogin = false,
  onAlertsCountChange,
}: DasaCautionReminderModalProps) {
  const { language } = useLanguage();
  const { isAuthenticated, role } = useAuth();
  const isTa = language === "ta";

  const [internalIsOpen, setInternalIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [alerts, setAlerts] = useState<DasaCautionItem[]>([]);
  const [todayKolkata, setTodayKolkata] = useState<string>("");
  const [markingId, setMarkingId] = useState<string | null>(null);

  // Filter tabs: "active" | "upcoming" | "all"
  const [filterTab, setFilterTab] = useState<"active" | "upcoming" | "all">("active");
  const [searchTerm, setSearchTerm] = useState<string>("");

  // Advisory language: Default to Tamil
  const [messageLang, setMessageLang] = useState<"ta" | "en">("ta");
  const [previewId, setPreviewId] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Inline Contact Edit State
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editCountryCode, setEditCountryCode] = useState<string>("+91");
  const [editPhone, setEditPhone] = useState<string>("");
  const [isSavingContact, setIsSavingContact] = useState<boolean>(false);
  const [contactSaveError, setContactSaveError] = useState<string | null>(null);

  // Modal open is true if explicitly controlled open OR internally auto-opened on login
  const isOpen = controlledIsOpen !== undefined ? (controlledIsOpen || internalIsOpen) : internalIsOpen;

  const handleClose = () => {
    if (todayKolkata) {
      sessionStorage.setItem(`dasa_caution_dismissed_${todayKolkata}`, "true");
    }
    setInternalIsOpen(false);
    if (controlledOnClose) {
      controlledOnClose();
    }
  };

  const fetchAlerts = useCallback(
    async (isAuto = false, forceFresh = false) => {
      if (!isAuthenticated) return;
      setLoading(true);
      setFetchError(null);
      try {
        const url = `/api/customers/dasa-cautions?lang=${messageLang}${forceFresh ? "&fresh=true" : ""}`;
        const res = await fetch(url);
        if (res.ok) {
          const data = await res.json();
          const items: DasaCautionItem[] = data.alerts || [];
          setAlerts(items);
          setTodayKolkata(data.todayKolkata || "");

          if (data.queryError) {
            console.warn("Dasa caution query notice:", data.queryError);
          }

          if (onAlertsCountChange) {
            onAlertsCountChange(data.activeCount !== undefined ? data.activeCount : items.length);
          }

          if (isAuto && items.length > 0) {
            // Check if already dismissed today in this session
            const sessionKey = `dasa_caution_dismissed_${data.todayKolkata}`;
            const alreadyDismissed = sessionStorage.getItem(sessionKey);
            if (!alreadyDismissed) {
              setInternalIsOpen(true);
            }
          }
        } else {
          const errData = await res.json().catch(() => ({}));
          const errMsg = errData.error || (isTa ? "எச்சரிக்கை பட்டியலை ஏற்றுவதில் பிழை ஏற்பட்டது." : "Failed to load caution alerts.");
          setFetchError(errMsg);
        }
      } catch (err: any) {
        console.warn("Could not load Dasa caution reminders:", err);
        setFetchError(err?.message || (isTa ? "இணைப்பு பிழை ஏற்பட்டது." : "Network connection error."));
      } finally {
        setLoading(false);
      }
    },
    [isAuthenticated, messageLang, onAlertsCountChange, isTa]
  );

  // Initial check on login
  useEffect(() => {
    if (autoCheckOnLogin && isAuthenticated) {
      fetchAlerts(true);
    }
  }, [autoCheckOnLogin, isAuthenticated, fetchAlerts]);

  // Fetch when opened explicitly
  useEffect(() => {
    if (isOpen) {
      fetchAlerts(false);
    }
  }, [isOpen, fetchAlerts]);

  // Manual mark as sent action
  const handleMarkAlertSent = async (item: DasaCautionItem) => {
    setMarkingId(item.id);
    try {
      const res = await fetch("/api/customers/dasa-cautions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          horoscope_id: item.horoscopeId,
          customer_id: item.customerId,
          dasa_lord: item.mahadashaLord,
          bhukti_lord: item.antardashaLord,
          andhar_lord: item.andharLord,
          period_start: item.startDateIso,
          period_end: item.endDateIso,
          severity: item.severity,
        }),
      });
      if (res.ok) {
        const nowIso = new Date().toISOString();
        setAlerts((prev) =>
          prev.map((a) =>
            a.id === item.id ? { ...a, alertSent: true, alertSentAt: nowIso } : a
          )
        );
      }
    } catch (err) {
      console.warn("Could not mark caution alert as sent:", err);
    } finally {
      setMarkingId(null);
    }
  };

  // Copy message
  const handleCopyMessage = (item: DasaCautionItem) => {
    const text = messageLang === "ta" ? item.messageTextTa : item.messageTextEn;
    navigator.clipboard.writeText(text);
    setCopiedId(item.id);
    setTimeout(() => setCopiedId(null), 2500);
  };

  // Inline Save Contact
  const handleSaveContact = async (item: DasaCautionItem) => {
    if (!editPhone.trim()) {
      setContactSaveError(isTa ? "தொலைபேசி எண் தேவை." : "Phone number is required.");
      return;
    }
    setIsSavingContact(true);
    setContactSaveError(null);
    try {
      const custId = item.customerId || item.horoscopeId;
      const res = await fetch(`/api/customers/${custId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phoneNumber: editPhone.trim(),
          countryCode: editCountryCode,
          fullName: item.fullName,
          birthDate: item.birthDate,
          horoscopeId: item.horoscopeId,
        }),
      });
      if (res.ok) {
        const resJson = await res.json().catch(() => ({}));
        const updatedCust = resJson.customer;
        const norm = validateAndNormalizePhone(editPhone.trim(), editCountryCode);

        // Optimistically update the alerts in local React state immediately so WhatsApp button transforms instantly
        setAlerts((prev) =>
          prev.map((a) => {
            if (a.id === item.id || a.horoscopeId === item.horoscopeId || (a.customerId && a.customerId === updatedCust?.id)) {
              const updatedWhatsapp = norm.whatsappNumber || (updatedCust?.whatsapp_number ?? null);
              const updatedNormPhone = norm.normalizedPhone || (updatedCust?.normalized_phone ?? null);
              const updatedNational = norm.nationalNumber || editPhone.trim();
              const hasPhone = norm.isValid;

              const clean = updatedWhatsapp ? updatedWhatsapp.replace(/\D/g, "") : "";
              const wLinkTa = clean && clean.length >= 7
                ? `https://api.whatsapp.com/send/?phone=${clean}&text=${encodeURIComponent(a.messageTextTa)}`
                : "";
              const wLinkEn = clean && clean.length >= 7
                ? `https://api.whatsapp.com/send/?phone=${clean}&text=${encodeURIComponent(a.messageTextEn)}`
                : "";

              return {
                ...a,
                customerId: updatedCust?.id || a.customerId,
                countryCode: editCountryCode,
                phoneNumber: updatedNational,
                normalizedPhone: updatedNormPhone || undefined,
                whatsappNumber: updatedWhatsapp || undefined,
                hasValidPhone: hasPhone,
                whatsappLinkTa: wLinkTa,
                whatsappLinkEn: wLinkEn,
              };
            }
            return a;
          })
        );

        setEditingId(null);
        await fetchAlerts(false, true);
      } else {
        const data = await res.json().catch(() => ({}));
        setContactSaveError(data?.error || `Failed to update phone number (HTTP ${res.status}).`);
      }
    } catch (err: any) {
      setContactSaveError(err?.message || "Failed to save phone number.");
    } finally {
      setIsSavingContact(false);
    }
  };

  // Filtered and searched list
  const filteredAlerts = useMemo(() => {
    let result = alerts;

    if (filterTab === "active") {
      result = result.filter((a) => a.isActiveNow);
    } else if (filterTab === "upcoming") {
      result = result.filter((a) => a.isUpcoming);
    }

    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      result = result.filter(
        (a) =>
          a.fullName.toLowerCase().includes(term) ||
          a.mahadashaLord.toLowerCase().includes(term) ||
          a.antardashaLord.toLowerCase().includes(term) ||
          a.andharLord.toLowerCase().includes(term) ||
          a.mahadashaLordTa.includes(term) ||
          a.antardashaLordTa.includes(term) ||
          a.andharLordTa.includes(term) ||
          (a.phoneNumber && a.phoneNumber.includes(term))
      );
    }

    return result;
  }, [alerts, filterTab, searchTerm]);

  const activeCount = alerts.filter((a) => a.isActiveNow).length;
  const upcomingCount = alerts.filter((a) => a.isUpcoming).length;
  const criticalCount = alerts.filter((a) => a.severity === "critical").length;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="relative w-full max-w-4xl max-h-[92vh] bg-white rounded-3xl shadow-2xl border border-rose-200 flex flex-col overflow-hidden">
        {/* Header Section */}
        <div className="px-5 sm:px-6 py-4 bg-gradient-to-r from-rose-900 via-rose-800 to-amber-950 text-white flex items-center justify-between border-b border-rose-700/50">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl bg-white/10 border border-white/20 flex items-center justify-center shadow-inner">
              <ShieldAlert className="w-6 h-6 text-rose-300" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-serif text-lg sm:text-xl font-bold tracking-tight">
                  {isTa
                    ? "தசா-புத்தி கண்ட கால எச்சரிக்கை"
                    : "Dasa-Bhukti Caution Reminders"}
                </h2>
                {criticalCount > 0 && (
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-rose-500 text-white border border-rose-400 animate-pulse">
                    {criticalCount} {isTa ? "கண்டம்" : "Critical"}
                  </span>
                )}
              </div>
              <p className="text-xs text-rose-200/90 mt-0.5">
                {isTa
                  ? `இன்றைய கணிப்பு (${todayKolkata || "Asia/Kolkata"}): சாதகமற்ற மற்றும் பரிகாரம் தேவைப்படும் தசா-புக்திகள்`
                  : `Today's Scan (${todayKolkata}): Challenging Dasa-Bhuktis requiring vigilance & remedies`}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Language Switcher for messages */}
            <div className="flex items-center rounded-xl bg-white/10 p-0.5 border border-white/20 text-xs">
              <button
                type="button"
                onClick={() => setMessageLang("ta")}
                className={`px-2.5 py-1 rounded-lg font-bold transition-all ${
                  messageLang === "ta"
                    ? "bg-white text-rose-950 shadow-xs"
                    : "text-rose-100 hover:text-white"
                }`}
              >
                தமிழ்
              </button>
              <button
                type="button"
                onClick={() => setMessageLang("en")}
                className={`px-2.5 py-1 rounded-lg font-bold transition-all ${
                  messageLang === "en"
                    ? "bg-white text-rose-950 shadow-xs"
                    : "text-rose-100 hover:text-white"
                }`}
              >
                EN
              </button>
            </div>

            <button
              type="button"
              onClick={() => fetchAlerts(false, true)}
              title={isTa ? "மீண்டும் கணிக்க (Refresh)" : "Refresh & Re-scan"}
              className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 text-rose-100 hover:text-white flex items-center justify-center transition-colors cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            </button>

            <button
              type="button"
              onClick={handleClose}
              className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 text-rose-100 hover:text-white flex items-center justify-center transition-colors cursor-pointer"
              aria-label="Close"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Toolbar & Filter Tabs */}
        <div className="px-5 sm:px-6 py-3 bg-[#FFFBF8] border-b border-[#F2E8DF] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          {/* Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
            <button
              type="button"
              onClick={() => setFilterTab("active")}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-colors inline-flex items-center gap-1.5 cursor-pointer whitespace-nowrap ${
                filterTab === "active"
                  ? "bg-rose-600 text-white shadow-xs"
                  : "bg-white text-slate-700 border border-slate-200 hover:bg-rose-50"
              }`}
            >
              <Flame className="w-3.5 h-3.5" />
              <span>{isTa ? "தற்போது நடப்பில் உள்ளவை" : "Active Now"}</span>
              <span className={`px-1.5 py-0.2 rounded-full text-[10px] ${filterTab === "active" ? "bg-rose-800 text-rose-100" : "bg-slate-100 text-slate-700"}`}>
                {activeCount}
              </span>
            </button>

            <button
              type="button"
              onClick={() => setFilterTab("upcoming")}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-colors inline-flex items-center gap-1.5 cursor-pointer whitespace-nowrap ${
                filterTab === "upcoming"
                  ? "bg-amber-600 text-white shadow-xs"
                  : "bg-white text-slate-700 border border-slate-200 hover:bg-amber-50"
              }`}
            >
              <Clock className="w-3.5 h-3.5" />
              <span>{isTa ? "அடுத்து வரும் 60 நாட்கள்" : "Upcoming (60 Days)"}</span>
              <span className={`px-1.5 py-0.2 rounded-full text-[10px] ${filterTab === "upcoming" ? "bg-amber-800 text-amber-100" : "bg-slate-100 text-slate-700"}`}>
                {upcomingCount}
              </span>
            </button>

            <button
              type="button"
              onClick={() => setFilterTab("all")}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-colors inline-flex items-center gap-1.5 cursor-pointer whitespace-nowrap ${
                filterTab === "all"
                  ? "bg-slate-800 text-white shadow-xs"
                  : "bg-white text-slate-700 border border-slate-200 hover:bg-slate-100"
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>{isTa ? "அனைத்தும்" : "All Flagged"}</span>
              <span className={`px-1.5 py-0.2 rounded-full text-[10px] ${filterTab === "all" ? "bg-slate-900 text-slate-200" : "bg-slate-100 text-slate-700"}`}>
                {alerts.length}
              </span>
            </button>
          </div>

          {/* Search Box */}
          <div className="relative w-full sm:w-64">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder={isTa ? "பெயர் அல்லது தசா தேடுக..." : "Search name or Dasa..."}
              className="w-full pl-8 pr-3 py-1.5 text-xs bg-white rounded-xl border border-slate-200 focus:outline-hidden focus:ring-1 focus:ring-rose-500 text-slate-800"
            />
          </div>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 bg-slate-50/50">
          {loading ? (
            <div className="py-20 flex flex-col items-center justify-center gap-3">
              <div className="w-8 h-8 border-3 border-rose-600 border-t-transparent rounded-full animate-spin" />
              <p className="text-xs text-slate-500 font-medium">
                {isTa
                  ? "சேமிக்கப்பட்ட ஜாதகங்களின் தசா-புக்தி பலன்கள் கணிக்கப்படுகின்றன..."
                  : "Analyzing saved charts for adverse Dasa-Bhuktis..."}
              </p>
            </div>
          ) : fetchError ? (
            <div className="py-16 text-center space-y-3 bg-white rounded-2xl border border-rose-200 p-8">
              <div className="w-12 h-12 mx-auto rounded-full bg-rose-50 text-rose-600 flex items-center justify-center">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-slate-800 text-sm sm:text-base">
                {isTa ? "தகவல் பெறுவதில் தாமதம் / பிழை" : "Unable to Load Caution Alerts"}
              </h3>
              <p className="text-xs text-slate-500 max-w-md mx-auto">
                {fetchError}
              </p>
              <button
                type="button"
                onClick={() => fetchAlerts(false, true)}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 shadow-xs transition-colors cursor-pointer"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>{isTa ? "மீண்டும் முயற்சிக்கவும் (Retry)" : "Retry Now"}</span>
              </button>
            </div>
          ) : filteredAlerts.length === 0 ? (
            <div className="py-16 text-center space-y-3 bg-white rounded-2xl border border-dashed border-slate-200 p-8">
              {searchTerm.trim() ? (
                <>
                  <div className="w-12 h-12 mx-auto rounded-full bg-slate-100 text-slate-500 flex items-center justify-center">
                    <Search className="w-6 h-6" />
                  </div>
                  <h3 className="font-bold text-slate-800 text-sm sm:text-base">
                    {isTa
                      ? `"${searchTerm}" என்ற பெயரில் எச்சரிக்கைகள் ஏதுமில்லை`
                      : `No caution alerts found matching "${searchTerm}"`}
                  </h3>
                  <button
                    type="button"
                    onClick={() => setSearchTerm("")}
                    className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 cursor-pointer"
                  >
                    {isTa ? "தேடலை நீக்குக (Clear Search)" : "Clear Search"}
                  </button>
                </>
              ) : filterTab === "upcoming" && upcomingCount === 0 ? (
                <>
                  <div className="w-12 h-12 mx-auto rounded-full bg-amber-50 text-amber-600 flex items-center justify-center">
                    <Clock className="w-6 h-6" />
                  </div>
                  <h3 className="font-bold text-slate-800 text-sm sm:text-base">
                    {isTa ? "அடுத்த 60 நாட்களில் தொடங்கும் கண்ட காலங்கள் ஏதுமில்லை" : "No Critical Periods Entering in Next 60 Days"}
                  </h3>
                  <p className="text-xs text-slate-500 max-w-md mx-auto">
                    {isTa
                      ? `தற்போது நடப்பில் உள்ள கண்ட காலங்களைக் காண 'தற்போது நடப்பில் உள்ளவை' (${activeCount}) தாவலைத் தேர்ந்தெடுக்கவும்.`
                      : `Switch to 'Active Now' (${activeCount}) tab to view clients currently in adverse periods.`}
                  </p>
                  {activeCount > 0 && (
                    <button
                      type="button"
                      onClick={() => setFilterTab("active")}
                      className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-rose-600 hover:bg-rose-700 text-white shadow-xs transition-colors cursor-pointer"
                    >
                      <Flame className="w-3.5 h-3.5" />
                      <span>{isTa ? `நடப்பில் உள்ளவை காண (${activeCount})` : `View Active Now (${activeCount})`}</span>
                    </button>
                  )}
                </>
              ) : (
                <>
                  <div className="w-12 h-12 mx-auto rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center">
                    <CheckCircle2 className="w-6 h-6" />
                  </div>
                  <h3 className="font-bold text-slate-800 text-sm sm:text-base">
                    {isTa ? "கண்ட கால எச்சரிக்கைகள் ஏதுமில்லை!" : "No Critical Caution Periods Found!"}
                  </h3>
                  <p className="text-xs text-slate-500 max-w-md mx-auto">
                    {isTa
                      ? "தற்போது உங்களுடைய சேமிக்கப்பட்ட ஜாதகங்களில் தீவிர மாரக/சடாஷ்டக தோஷங்கள் உள்ள நபர்கள் எவருமில்லை. அனைவரும் சீரான காலத்தில் உள்ளனர்."
                      : "None of your saved clients are currently traversing severe Maraka or Shadashtaka periods. All charts are operating in balanced or favorable windows."}
                  </p>
                  <button
                    type="button"
                    onClick={() => fetchAlerts(false, true)}
                    className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 transition-colors cursor-pointer"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    <span>{isTa ? "மீண்டும் சரிபார்க்க (Re-scan)" : "Re-scan Now"}</span>
                  </button>
                </>
              )}
            </div>
          ) : (
            filteredAlerts.map((item) => {
              const waLink = messageLang === "ta" ? item.whatsappLinkTa : item.whatsappLinkEn;
              const isMarkingThis = markingId === item.id;
              const isCritical = item.severity === "critical";

              return (
                <div
                  key={item.id}
                  className={`rounded-2xl border bg-white p-4 sm:p-5 shadow-xs transition-all hover:shadow-md ${
                    isCritical
                      ? "border-rose-300 ring-1 ring-rose-200/50"
                      : "border-amber-200 hover:border-amber-300"
                  }`}
                >
                  {/* Top Row: Client Info, Period, Severity Badge */}
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                    <div className="flex items-start gap-3 min-w-0">
                      {/* Avatar */}
                      <div
                        className={`w-11 h-11 rounded-2xl flex items-center justify-center text-white font-serif font-bold text-base shrink-0 shadow-xs ${
                          isCritical
                            ? "bg-gradient-to-br from-rose-700 to-rose-900"
                            : "bg-gradient-to-br from-amber-600 to-amber-800"
                        }`}
                      >
                        {item.fullName.charAt(0).toUpperCase() || "C"}
                      </div>

                      <div className="min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h4 className="font-bold text-sm sm:text-base text-slate-900 truncate">
                            {item.fullName}
                          </h4>
                          {/* Active / Upcoming Pill */}
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                              item.isActiveNow
                                ? "bg-rose-100 text-rose-800 border border-rose-300"
                                : "bg-amber-100 text-amber-800 border border-amber-300"
                            }`}
                          >
                            {item.isActiveNow
                              ? isTa
                                ? "தற்போது நடப்பில்"
                                : "Active Now"
                              : isTa
                              ? "வரவிருப்பது"
                              : "Upcoming"}
                          </span>

                          {/* Severity Badge */}
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                              isCritical
                                ? "bg-rose-600 text-white shadow-2xs"
                                : "bg-amber-500 text-white"
                            }`}
                          >
                            {isCritical
                              ? isTa
                                ? "🔴 கண்ட காலம்"
                                : "🔴 High Caution"
                              : isTa
                              ? "🟡 எச்சரிக்கை தேவை"
                              : "🟡 Moderate Caution"}
                          </span>

                          {/* Domain Pill (Relationships / Family / Health / Finance / Career) */}
                          {item.primaryRiskDomain === "relationships" && (
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-rose-100 text-rose-900 border border-rose-300">
                              {isTa ? "💍 திருமண & களத்திர உறவு விழிப்புணர்வு" : "💍 Marriage & Relationship Harmony Alert"}
                            </span>
                          )}
                          {item.primaryRiskDomain === "family_discord" && (
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-purple-100 text-purple-900 border border-purple-300">
                              {isTa ? "👨‍👩‍👧 குடும்ப விழிப்புணர்வு / பிரிவு தவிர்த்தல்" : "👨‍👩‍👧 Family Harmony & Conflict Alert"}
                            </span>
                          )}
                        </div>

                        {/* Contact details & helpline */}
                        <div className="mt-1 flex items-center gap-2.5 text-xs text-slate-500 flex-wrap">
                          {item.hasValidPhone ? (
                            <span className="flex items-center gap-1 font-mono font-semibold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">
                              <Phone className="w-3 h-3 text-emerald-600" />
                              {item.normalizedPhone || item.phoneNumber}
                            </span>
                          ) : (
                            <span className="flex items-center gap-1 text-amber-800 bg-amber-50 px-2 py-0.5 rounded-md border border-amber-200 text-[11px]">
                              <AlertTriangle className="w-3 h-3 text-amber-600" />
                              {isTa ? "எண் இல்லை" : "No WhatsApp phone"}
                            </span>
                          )}

                          <button
                            type="button"
                            onClick={() => {
                              setEditingId(editingId === item.id ? null : item.id);
                              setEditPhone(item.phoneNumber || "");
                              setEditCountryCode(item.countryCode || "+91");
                            }}
                            className="text-[11px] text-[#3478F6] hover:underline flex items-center gap-0.5 cursor-pointer font-medium"
                          >
                            <Edit2 className="w-3 h-3" />
                            <span>
                              {item.hasValidPhone
                                ? isTa
                                  ? "எண் மாற்று"
                                  : "Edit Phone"
                                : isTa
                                ? "+ எண் சேர்"
                                : "+ Add Phone"}
                            </span>
                          </button>

                          <a
                            href="tel:+919444559071"
                            title="Astrologer Consultation Helpline"
                            className="inline-flex items-center gap-1 text-[11px] font-semibold text-rose-800 bg-rose-50 hover:bg-rose-100 px-2 py-0.5 rounded-md border border-rose-200 transition-colors"
                          >
                            <Phone className="w-2.5 h-2.5 text-rose-600" />
                            <span>9444 55 9071</span>
                          </a>
                        </div>
                      </div>
                    </div>

                    {/* 3-Tier Period Lord Badge & Exact Anthara Window */}
                    <div className="shrink-0 text-left sm:text-right bg-rose-50/50 sm:bg-transparent p-2.5 sm:p-0 rounded-xl sm:rounded-none border sm:border-0 border-rose-100">
                      <div className="text-xs font-bold text-slate-900 flex items-center sm:justify-end gap-1.5 flex-wrap">
                        <Sparkles className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                        <span>
                          {isTa
                            ? `${item.mahadashaLordTa} தசா › ${item.antardashaLordTa} புக்தி › `
                            : `${item.mahadashaLord} Dasa › ${item.antardashaLord} Bhukti › `}
                        </span>
                        <span className="text-rose-700 bg-rose-100/90 px-1.5 py-0.5 rounded font-extrabold text-[11px]">
                          {isTa ? `${item.andharLordTa} அந்தரம்` : `${item.andharLord} Anthara`}
                        </span>
                      </div>
                      <div className="text-[11px] text-rose-950 font-bold font-mono mt-1">
                        {item.startDateFormatted} — {item.endDateFormatted}
                      </div>
                      <div className="text-[10px] text-rose-700 font-semibold mt-0.5">
                        {isTa
                          ? `அந்தர காலம் மட்டும்: ${item.durationFormatted}`
                          : `Anthara Period Alone: ${item.durationFormatted}`}
                      </div>
                      {item.bhuktiStartDateFormatted && (
                        <div className="text-[10px] text-slate-400 mt-0.5">
                          {isTa
                            ? `(புக்தி: ${item.bhuktiStartDateFormatted} – ${item.bhuktiEndDateFormatted})`
                            : `(Bhukti: ${item.bhuktiStartDateFormatted} – ${item.bhuktiEndDateFormatted})`}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Progress Bar (Antharam progress if active) */}
                  {item.isActiveNow && (
                    <div className="mt-3 space-y-1">
                      <div className="flex justify-between text-[10px] text-slate-500 font-medium">
                        <span>
                          {isTa
                            ? `${item.andharLordTa} அந்தர கால முன்னேற்றம் (${item.startDateFormatted} – ${item.endDateFormatted})`
                            : `${item.andharLord} Anthara Progress (${item.startDateFormatted} – ${item.endDateFormatted})`}
                        </span>
                        <span>{item.progressPercent}%</span>
                      </div>
                      <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${
                            isCritical ? "bg-rose-600" : "bg-amber-500"
                          }`}
                          style={{ width: `${item.progressPercent}%` }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Astrological Vulnerability & Reason Breakdown */}
                  <div className="mt-3.5 p-3 rounded-xl bg-rose-50/60 border border-rose-200/80 text-xs space-y-2">
                    <div className="flex items-center gap-2 font-bold text-rose-950 text-[11px]">
                      <AlertTriangle className="w-3.5 h-3.5 text-rose-700 shrink-0" />
                      <span>
                        {isTa ? "கவனப் பகுதி:" : "Focus Domain:"}{" "}
                        <strong className="text-rose-800">
                          {isTa ? item.riskDomainLabelTa : item.riskDomainLabelEn}
                        </strong>
                      </span>
                    </div>

                    <ul className="space-y-1 text-slate-700 text-[11px]">
                      {(isTa ? item.reasonsTa : item.reasonsEn).map((reason, idx) => (
                        <li key={idx} className="flex items-start gap-1.5">
                          <span className="text-rose-600 font-bold">•</span>
                          <span>{reason}</span>
                        </li>
                      ))}
                      <li className="flex items-start gap-1.5 text-rose-900 font-semibold pt-1 border-t border-rose-200/60">
                        <span className="text-rose-600 font-bold">⛔</span>
                        <span>
                          {isTa ? "தவிர்க்க வேண்டியவை:" : "Avoid:"}{" "}
                          <span className="font-normal">
                            {isTa ? item.avoidNotesTa : item.avoidNotesEn}
                          </span>
                        </span>
                      </li>
                    </ul>

                    {/* Gochara Transit Confirmation Badge & Reason */}
                    {item.transitConfirmed && (
                      <div className="pt-2 border-t border-rose-200/60 text-[11px] text-indigo-950 bg-indigo-50/70 p-2 rounded-lg space-y-1">
                        <div className="font-extrabold text-indigo-900 flex items-center gap-1.5">
                          <span>🪐</span>
                          <span>
                            {isTa
                              ? "கோச்சார கிரக நிலைகள் உறுதிப்படுத்துகின்றன (Transit Confirmed):"
                              : "Live Planetary Transits Confirm This Risk (Gochara Check):"}
                          </span>
                        </div>
                        <p className="text-slate-800 text-[11px] leading-relaxed">
                          {isTa ? item.transitInfluenceSummaryTa : item.transitInfluenceSummaryEn}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Recommended Remedies Grid */}
                  <div className="mt-3 p-3 rounded-xl bg-amber-50/50 border border-amber-200 text-xs space-y-1.5">
                    <div className="font-bold text-amber-950 flex items-center gap-1.5 text-[11px]">
                      <Sparkles className="w-3.5 h-3.5 text-amber-700" />
                      <span>{isTa ? "பரிந்துரைக்கப்படும் பரிகாரங்கள்:" : "Prescribed Vedic Remedies:"}</span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] text-slate-700">
                      <div>
                        <strong className="text-amber-900">{isTa ? "தெய்வம்:" : "Deity:"}</strong>{" "}
                        {isTa ? item.remedyDeityTa : item.remedyDeityEn}
                      </div>
                      <div>
                        <strong className="text-amber-900">{isTa ? "பாராயணம்:" : "Mantra:"}</strong>{" "}
                        {isTa ? item.remedyMantraTa : item.remedyMantraEn}
                      </div>
                      <div>
                        <strong className="text-amber-900">{isTa ? "தானம்:" : "Charity:"}</strong>{" "}
                        {isTa ? item.remedyCharityTa : item.remedyCharityEn}
                      </div>
                      <div>
                        <strong className="text-amber-900">{isTa ? "வழிபாடு:" : "Practice:"}</strong>{" "}
                        {isTa ? item.generalRemedyTa : item.generalRemedyEn}
                      </div>
                    </div>
                  </div>

                  {/* Inline Contact Edit Form */}
                  {editingId === item.id && (
                    <div className="mt-3 p-3 bg-white rounded-xl border border-amber-400 shadow-xs space-y-2.5 animate-in fade-in duration-150">
                      <div className="text-xs font-semibold text-slate-900 flex items-center gap-1.5">
                        <Phone className="w-3.5 h-3.5 text-amber-700" />
                        <span>
                          {isTa
                            ? "வாட்ஸ்அப் எண் சேர்க்க / புதுப்பிக்க:"
                            : "Add or Update WhatsApp Number:"}
                        </span>
                      </div>
                      <div className="flex flex-wrap sm:flex-nowrap gap-2">
                        <select
                          value={editCountryCode}
                          onChange={(e) => setEditCountryCode(e.target.value)}
                          className="w-28 px-2 py-1.5 text-xs rounded-lg border border-slate-300 bg-white text-slate-900"
                        >
                          {SUPPORTED_COUNTRY_CODES.map((c) => (
                            <option key={c.code} value={c.code}>
                              {c.flag} {c.code}
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
                          className="flex-1 px-3 py-1.5 text-xs rounded-lg border border-slate-300 text-slate-900 focus:ring-1 focus:ring-rose-500"
                        />
                        <button
                          type="button"
                          onClick={() => handleSaveContact(item)}
                          disabled={isSavingContact}
                          className="px-3.5 py-1.5 bg-rose-900 hover:bg-rose-950 text-white text-xs font-semibold rounded-lg transition-colors disabled:opacity-50 inline-flex items-center gap-1"
                        >
                          <Check className="w-3 h-3" />
                          <span>
                            {isSavingContact
                              ? "Saving..."
                              : isTa
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
                          className="px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium rounded-lg"
                        >
                          {isTa ? "ரத்து" : "Cancel"}
                        </button>
                      </div>
                      {contactSaveError && (
                        <p className="text-[11px] text-rose-600 font-medium">
                          {contactSaveError}
                        </p>
                      )}
                    </div>
                  )}

                  {/* Message Preview Box */}
                  {previewId === item.id && (
                    <div className="mt-3 p-3.5 bg-slate-50 rounded-xl border border-slate-200 space-y-2 text-xs shadow-inner animate-in fade-in duration-150">
                      <div className="flex items-center justify-between text-[11px] font-bold text-slate-800 border-b border-slate-200 pb-1.5">
                        <span className="flex items-center gap-1.5">
                          <MessageCircle className="w-3.5 h-3.5 text-rose-700" />
                          <span>
                            {isTa ? "எச்சரிக்கை செய்தி முன்னோட்டம்:" : "WhatsApp Message Preview:"}
                          </span>
                        </span>
                        <button
                          type="button"
                          onClick={() => handleCopyMessage(item)}
                          className="inline-flex items-center gap-1 text-[11px] font-semibold text-slate-800 hover:text-rose-700 px-2.5 py-1 rounded-lg bg-white hover:bg-rose-50 border border-slate-200 transition-colors"
                        >
                          {copiedId === item.id ? (
                            <>
                              <Check className="w-3 h-3 text-emerald-600" />
                              <span className="text-emerald-700 font-bold">
                                {isTa ? "நகலெடுக்கப்பட்டது!" : "Copied!"}
                              </span>
                            </>
                          ) : (
                            <>
                              <Copy className="w-3 h-3 text-rose-700" />
                              <span>{isTa ? "செய்தி நகலெடு" : "Copy Text"}</span>
                            </>
                          )}
                        </button>
                      </div>

                      <div className="bg-white p-3 rounded-lg border border-slate-200 text-xs font-sans text-slate-800 whitespace-pre-wrap leading-relaxed max-h-56 overflow-y-auto">
                        {messageLang === "ta" ? item.messageTextTa : item.messageTextEn}
                      </div>
                    </div>
                  )}

                  {/* Bottom Action Row */}
                  <div className="mt-4 pt-3 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => setPreviewId(previewId === item.id ? null : item.id)}
                        className="text-xs text-slate-600 hover:text-rose-700 font-semibold inline-flex items-center gap-1 px-2.5 py-1 rounded-lg hover:bg-rose-50 border border-slate-200 transition-colors cursor-pointer"
                      >
                        {previewId === item.id ? (
                          <>
                            <EyeOff className="w-3.5 h-3.5" />
                            <span>{isTa ? "செய்தி மறை" : "Hide Preview"}</span>
                          </>
                        ) : (
                          <>
                            <Eye className="w-3.5 h-3.5" />
                            <span>{isTa ? "செய்தி காண்" : "Preview Message"}</span>
                          </>
                        )}
                      </button>

                      {/* View Horoscope Link */}
                      <a
                        href={`/horoscope/results?id=${item.horoscopeId}&tab=dasa-palangal`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-slate-600 hover:text-[#3478F6] font-semibold inline-flex items-center gap-1 px-2.5 py-1 rounded-lg hover:bg-blue-50 border border-slate-200 transition-colors"
                        title="Open Dasa Palangal in new tab"
                      >
                        <ExternalLink className="w-3 h-3" />
                        <span>{isTa ? "ஜாதக பலன்" : "View Dasa"}</span>
                      </a>
                    </div>

                    <div className="flex items-center gap-2 flex-wrap">
                      {/* WhatsApp 1-Click Button */}
                      {item.hasValidPhone && waLink ? (
                        <a
                          href={waLink}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-xs transition-colors"
                        >
                          <MessageCircle className="w-3.5 h-3.5" />
                          <span>
                            {isTa ? "வாட்ஸ்அப் எச்சரிக்கை அனுப்பு" : "Send WhatsApp Alert"}
                          </span>
                        </a>
                      ) : (
                        <button
                          type="button"
                          onClick={() => {
                            setEditingId(item.id);
                            setEditPhone(item.phoneNumber || "");
                          }}
                          className="inline-flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl border border-slate-300 transition-colors"
                        >
                          <Phone className="w-3.5 h-3.5 text-amber-600" />
                          <span>{isTa ? "எண் சேர்த்து அனுப்பு" : "Add Phone to Send"}</span>
                        </button>
                      )}

                      {/* Mark as Sent Toggle Button */}
                      <button
                        type="button"
                        onClick={() => handleMarkAlertSent(item)}
                        disabled={isMarkingThis}
                        className={`inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-colors cursor-pointer border ${
                          item.alertSent
                            ? "bg-emerald-50 text-emerald-800 border-emerald-300 hover:bg-emerald-100"
                            : "bg-white text-slate-700 border-slate-300 hover:bg-slate-50"
                        }`}
                      >
                        {item.alertSent ? (
                          <>
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                            <span>
                              {isTa
                                ? "அனுப்பப்பட்டது ✓"
                                : "Alerted ✓"}
                            </span>
                          </>
                        ) : (
                          <>
                            <Clock className="w-3.5 h-3.5 text-slate-400" />
                            <span>
                              {isMarkingThis
                                ? "..."
                                : isTa
                                ? "அனுப்பியதாகக் குறி"
                                : "Mark as Sent"}
                            </span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-5 sm:px-6 py-3.5 bg-white border-t border-slate-200 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
            <span>
              {isTa
                ? "தினசரி தானியங்கி கண்ட கால ஸ்கேனர்"
                : "Daily Automatic Dasa Caution Scanner"}
            </span>
          </div>

          <div className="flex items-center gap-3">
            <a
              href="tel:+919444559071"
              className="inline-flex items-center gap-1 font-semibold text-rose-800 bg-rose-50 px-2.5 py-1 rounded-lg border border-rose-200 hover:bg-rose-100 transition-colors"
            >
              <Phone className="w-3 h-3 text-rose-600" />
              <span>{isTa ? "ஆலோசனைகளுக்கு: 9444 55 9071" : "Consultation: 9444 55 9071"}</span>
            </a>

            <button
              type="button"
              onClick={handleClose}
              className="px-4 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold transition-colors cursor-pointer"
            >
              {isTa ? "மூடுக" : "Dismiss for Today"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
