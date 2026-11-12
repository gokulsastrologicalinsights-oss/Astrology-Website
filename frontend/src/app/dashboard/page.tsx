"use client";

import React, { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { SavedHoroscopesList } from "@/components/saved/SavedHoroscopesList";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  Compass,
  User,
  Mail,
  Calendar,
  Shield,
  Sparkles,
  Database,
  LogOut,
  Clock,
  Layers,
  ChevronRight,
  Home,
  Cake,
  Flame,
  Heart,
  BookOpen,
  ShieldAlert,
} from "lucide-react";
import { BirthdayReminderModal } from "@/components/birthday/BirthdayReminderModal";
import { DasaCautionReminderModal } from "@/components/caution/DasaCautionReminderModal";

export default function DashboardPage() {
  const router = useRouter();
  const { language, t } = useLanguage();
  const { user, session, isAuthenticated, isLoading, logout } = useAuth();

  const [isBirthdayModalOpen, setIsBirthdayModalOpen] = useState(false);
  const [isCautionModalOpen, setIsCautionModalOpen] = useState(false);
  const [cautionAlertsCount, setCautionAlertsCount] = useState<number>(0);
  const [totalHoroscopesCount, setTotalHoroscopesCount] = useState<number>(0);

  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !user)) {
      router.replace("/login");
    }
  }, [isAuthenticated, user, isLoading, router]);

  // Load real database metrics
  useEffect(() => {
    // Total horoscopes count from Supabase
    fetch("/api/horoscopes?page=1&limit=1", { cache: "no-store" })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data && typeof data.totalCount === "number") {
          setTotalHoroscopesCount(data.totalCount);
        }
      })
      .catch((err) => {
        console.warn("Could not fetch total horoscopes count:", err);
      });
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-[calc(100vh-14rem)] flex items-center justify-center bg-[#E8EEF7]">
        <div className="w-8 h-8 border-4 border-[#3478F6] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  return (
    <div className="w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 sm:py-8 space-y-8">
      {/* Breadcrumb Navigation */}
      <Breadcrumbs
        items={[
          {
            label: language === "ta" ? "டாஷ்போர்டு" : "Dashboard",
          },
        ]}
      />

      {/* Top Welcome & Actions Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-[#DDE5F0]">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="font-serif text-2xl sm:text-3xl font-bold text-[#102A4C]">
              {t.userDashboardTitle || "User Dashboard"}
            </h1>
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#EBF2FE] text-[#3478F6] border border-[#BFDBFE]">
              <Shield className="w-3 h-3 text-[#3478F6]" />
              {user.role === "admin" ? t.roleBadgeAdmin || "Admin" : t.roleBadgeUser || "User"}
            </span>
          </div>
          <p className="mt-1 text-xs sm:text-sm text-[#52667E]">
            {t.userDashboardSubtitle || "Manage your astrological charts and activity."}
          </p>
        </div>

        {/* Quick Section Shortcuts */}
        <div className="flex items-center gap-2.5 flex-wrap">
          <Link
            href="/tools"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold text-white bg-[#102A4C] hover:bg-[#1E3A61] shadow-xs transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5 text-[#3478F6]" />
            <span>{t.navTools || "Astrology Tools"}</span>
          </Link>

          <Link
            href="/horoscopes"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold text-[#102A4C] bg-white hover:bg-slate-50 border border-[#DDE5F0] shadow-xs transition-colors"
          >
            <Database className="w-3.5 h-3.5 text-[#B8862B]" />
            <span>{language === "ta" ? "சேமிக்கப்பட்ட ஜாதகங்கள்" : "Saved Horoscopes"}</span>
            <span className="px-1.5 py-0.2 rounded-full text-[10px] font-extrabold bg-[#FAF2DE] text-[#B8862B] border border-amber-200">
              {totalHoroscopesCount}
            </span>
          </Link>

          <button
            type="button"
            onClick={() => setIsBirthdayModalOpen(true)}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold text-amber-900 bg-amber-50 hover:bg-amber-100 border border-amber-300 shadow-xs transition-colors cursor-pointer"
          >
            <Cake className="w-3.5 h-3.5 text-amber-600" />
            <span>{language === "ta" ? "பிறந்தநாள் நினைவூட்டல்" : "Birthday Wishes"}</span>
          </button>

          <button
            type="button"
            onClick={() => setIsCautionModalOpen(true)}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold text-rose-900 bg-rose-50 hover:bg-rose-100 border border-rose-300 shadow-xs transition-colors cursor-pointer relative"
            title={language === "ta" ? "தசா-புத்தி கண்ட கால எச்சரிக்கை" : "Dasa Caution Alerts"}
          >
            <ShieldAlert className="w-3.5 h-3.5 text-rose-600" />
            <span>{language === "ta" ? "கண்ட கால எச்சரிக்கை" : "Caution Alerts"}</span>
            {cautionAlertsCount > 0 && (
              <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-rose-600 text-white font-extrabold leading-none animate-pulse">
                {cautionAlertsCount}
              </span>
            )}
          </button>

          <button
            type="button"
            onClick={logout}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl border border-[#DDE5F0] bg-white hover:bg-rose-50 text-xs font-semibold text-rose-600 transition-colors cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>{t.navLogout}</span>
          </button>
        </div>
      </div>

      {/* Main Layout: Compact Profile Sidebar & Saved Charts */}
      <div className="flex flex-col lg:flex-row items-start gap-6">
        {/* Left Column: Compact Profile Card */}
        <div className="w-full max-w-sm lg:max-w-none lg:w-[280px] shrink-0 rounded-2xl border border-[#DDE5F0] bg-white p-4.5 sm:p-5 shadow-xs space-y-4">
          <div className="flex items-center gap-3 pb-3.5 border-b border-[#F1F5F9]">
            <div className="w-11 h-11 rounded-full bg-gradient-to-br from-[#102A4C] to-[#1E3A61] flex items-center justify-center text-white font-serif font-bold text-base shadow-2xs shrink-0">
              {user.username?.charAt(0).toUpperCase() || "U"}
            </div>
            <div className="min-w-0">
              <div className="font-bold text-[#102A4C] text-sm truncate">
                {user.displayName || user.username}
              </div>
              <div className="text-xs text-[#52667E] truncate">@{user.username}</div>
            </div>
          </div>

          <div className="space-y-2.5 text-xs">
            <div className="flex items-center gap-2 text-[#334155] min-w-0">
              <Mail className="w-3.5 h-3.5 text-[#94A3B8] shrink-0" />
              <span className="truncate" title={user.email || ""}>
                {user.email || "No email on record"}
              </span>
            </div>

            <div className="flex items-center gap-2 text-[#334155]">
              <Shield className="w-3.5 h-3.5 text-[#94A3B8] shrink-0" />
              <span>
                {language === "ta" ? "பாத்திரம்:" : "Role:"}{" "}
                <strong className="capitalize text-[#102A4C]">{user.role}</strong>
              </span>
            </div>

            {user.createdAt && (
              <div className="flex items-center gap-2 text-[#334155]">
                <Calendar className="w-3.5 h-3.5 text-[#94A3B8] shrink-0" />
                <span>
                  {t.memberSince || "Member since"}: {new Date(user.createdAt).toLocaleDateString()}
                </span>
              </div>
            )}
          </div>

          {/* Quick Tool Links */}
          <div className="pt-3.5 border-t border-[#F1F5F9] space-y-1.5">
            <span className="text-[10px] font-bold uppercase tracking-wider text-[#94A3B8] block mb-1">
              Quick Navigation
            </span>
            <Link
              href="/tools/instant-revelation"
              className="flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-rose-800 bg-rose-50/80 hover:bg-rose-100/90 transition-colors group border border-rose-200/80"
            >
              <div className="flex items-center gap-2 min-w-0">
                <Flame className="w-3.5 h-3.5 text-rose-600 shrink-0 animate-pulse" />
                <span className="truncate">நேரடி வாக்கு பலகை (Instant Reading)</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-rose-400 group-hover:translate-x-0.5 transition-transform shrink-0" />
            </Link>

            <Link
              href="/tools/horoscope"
              className="flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors group"
            >
              <div className="flex items-center gap-2 min-w-0">
                <Compass className="w-3.5 h-3.5 text-[#B8862B] shrink-0" />
                <span className="truncate">Horoscope / KP System</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-[#94A3B8] group-hover:translate-x-0.5 transition-transform shrink-0" />
            </Link>

            <Link
              href="/tools/horoscope-writing"
              className="flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors group"
            >
              <div className="flex items-center gap-2 min-w-0">
                <BookOpen className="w-3.5 h-3.5 text-[#B8862B] shrink-0" />
                <span className="truncate">
                  {language === "ta" ? "பாரம்பரிய தமிழ் ஜாதகக் குறிப்பு" : "Horoscope Writing"}
                </span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-[#94A3B8] group-hover:translate-x-0.5 transition-transform shrink-0" />
            </Link>

            <Link
              href="/tools/numerology"
              className="flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors group"
            >
              <div className="flex items-center gap-2 min-w-0">
                <Sparkles className="w-3.5 h-3.5 text-[#3478F6] shrink-0" />
                <span className="truncate">Numerology System</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-[#94A3B8] group-hover:translate-x-0.5 transition-transform shrink-0" />
            </Link>

            <Link
              href="/tools/advanced-kp"
              className="flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors group"
            >
              <div className="flex items-center gap-2 min-w-0">
                <Layers className="w-3.5 h-3.5 text-[#B8862B] shrink-0" />
                <span className="truncate">Advanced KP &amp; Horary</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-[#94A3B8] group-hover:translate-x-0.5 transition-transform shrink-0" />
            </Link>

            <Link
              href="/tools/kp-events-prediction"
              className="flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors group"
            >
              <div className="flex items-center gap-2 min-w-0">
                <Sparkles className="w-3.5 h-3.5 text-[#B8862B] shrink-0" />
                <span className="truncate">
                  {language === "ta" ? "KP நிகழ்வு கணிப்பு" : "KP Events & Prediction"}
                </span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-[#94A3B8] group-hover:translate-x-0.5 transition-transform shrink-0" />
            </Link>

            <Link
              href="/tools/marriage-prediction"
              className="flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors group"
            >
              <div className="flex items-center gap-2 min-w-0">
                <Heart className="w-3.5 h-3.5 text-rose-600 shrink-0" />
                <span className="truncate">
                  {language === "ta" ? "திருமண கணிப்பு" : "Marriage Prediction"}
                </span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-[#94A3B8] group-hover:translate-x-0.5 transition-transform shrink-0" />
            </Link>

            <Link
              href="/horoscopes"
              className="flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors group"
            >
              <div className="flex items-center gap-2 min-w-0">
                <Database className="w-3.5 h-3.5 text-[#B8862B] shrink-0" />
                <span className="truncate">
                  {language === "ta" ? "சேமிக்கப்பட்ட ஜாதகங்கள்" : "Saved Horoscopes"}
                </span>
              </div>
              <div className="flex items-center gap-1.5 shrink-0">
                <span className="px-1.5 py-0.2 rounded-full text-[10px] font-bold bg-[#FAF2DE] text-[#B8862B] border border-amber-200">
                  {totalHoroscopesCount}
                </span>
                <ChevronRight className="w-3.5 h-3.5 text-[#94A3B8] group-hover:translate-x-0.5 transition-transform" />
              </div>
            </Link>

            <Link
              href="/tools/daily-sastra?tab=vastu"
              className="flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors group"
            >
              <div className="flex items-center gap-2 min-w-0">
                <Home className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                <span className="truncate">
                  {language === "ta" ? "வாஸ்து சாஸ்திரம்" : "Vastu Shastra Assessment"}
                </span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-[#94A3B8] group-hover:translate-x-0.5 transition-transform shrink-0" />
            </Link>

            <Link
              href="/remedies"
              className="flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors group"
            >
              <div className="flex items-center gap-2 min-w-0">
                <Flame className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                <span className="truncate">
                  {language === "ta" ? "பரிகாரங்கள் & ஆலயங்கள்" : "Remedies & Pariharam"}
                </span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-[#94A3B8] group-hover:translate-x-0.5 transition-transform shrink-0" />
            </Link>
          </div>

          {user.role === "admin" && (
            <div className="pt-3.5 border-t border-[#F1F5F9]">
              <Link
                href="/admin"
                className="w-full inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold text-white bg-[#B8862B] hover:bg-[#996515] shadow-xs transition-colors"
              >
                <Shield className="w-3.5 h-3.5" />
                <span>{t.navAdmin || "Open Admin Portal"}</span>
              </Link>
            </div>
          )}
        </div>

        {/* Right Column: Saved Horoscopes Section ONLY */}
        <div className="flex-1 min-w-0 w-full space-y-6">
          <SavedHoroscopesList showHeader={true} showBanner={true} pageSize={10} columns={2} />
        </div>
      </div>

      {/* Birthday Reminder Modal */}
      <BirthdayReminderModal
        isOpen={isBirthdayModalOpen}
        onClose={() => setIsBirthdayModalOpen(false)}
        autoCheckOnLogin={true}
      />

      {/* Dasa Caution Reminder Modal */}
      <DasaCautionReminderModal
        isOpen={isCautionModalOpen}
        onClose={() => setIsCautionModalOpen(false)}
        autoCheckOnLogin={true}
        autoOpenOnLogin={false}
        onAlertsCountChange={setCautionAlertsCount}
      />
    </div>
  );
}
