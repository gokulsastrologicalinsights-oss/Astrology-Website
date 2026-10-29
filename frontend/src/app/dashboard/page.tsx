"use client";

import React, { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { getHealth } from "@/lib/api";
import { HealthResponse } from "@/lib/types";
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
  Activity,
  ShieldCheck,
  ChevronRight,
  Home,
  Cake,
  Flame,
  Heart,
  BookOpen,
} from "lucide-react";
import { BirthdayReminderModal } from "@/components/birthday/BirthdayReminderModal";

export default function DashboardPage() {
  const router = useRouter();
  const { language, t } = useLanguage();
  const { user, session, isAuthenticated, isLoading, logout } = useAuth();

  const [isBirthdayModalOpen, setIsBirthdayModalOpen] = useState(false);
  const [totalHoroscopesCount, setTotalHoroscopesCount] = useState<number>(0);
  const [engineHealth, setEngineHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !user)) {
      router.replace("/login");
    }
  }, [isAuthenticated, user, isLoading, router]);

  // Load real database metrics
  useEffect(() => {
    // 1. Total horoscopes count from Supabase
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

    // 2. Engine health
    getHealth()
      .then((h) => setEngineHealth(h))
      .catch(() => setEngineHealth(null));
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
            href="/horoscope"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold text-[#102A4C] bg-white hover:bg-slate-50 border border-[#DDE5F0] shadow-xs transition-colors"
          >
            <Compass className="w-3.5 h-3.5 text-[#B8862B]" />
            <span>{language === "ta" ? "ஜாதகம் கணிக்க" : "New Horoscope"}</span>
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
            onClick={logout}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl border border-[#DDE5F0] bg-white hover:bg-rose-50 text-xs font-semibold text-rose-600 transition-colors cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>{t.navLogout}</span>
          </button>
        </div>
      </div>

      {/* Real Statistics Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Stat 1: Total Saved Horoscopes */}
        <div className="p-5 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-2">
          <div className="flex items-center justify-between text-[#52667E]">
            <span className="text-xs font-semibold">
              {language === "ta" ? "சேமிக்கப்பட்ட ஜாதகங்கள்" : "Saved Horoscopes"}
            </span>
            <div className="w-8 h-8 rounded-lg bg-[#FAF2DE] text-[#B8862B] flex items-center justify-center">
              <Compass className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-serif font-bold text-[#102A4C]">
            {totalHoroscopesCount}
          </div>
          <div className="text-[11px] text-[#52667E] flex items-center gap-1">
            <span>{language === "ta" ? "Supabase தரவுத்தளத்தில் சேமிக்கப்பட்டது" : "Stored in Supabase database"}</span>
          </div>
        </div>

        {/* Stat 2: Astronomical Engine Status */}
        <div className="p-5 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-2">
          <div className="flex items-center justify-between text-[#52667E]">
            <span className="text-xs font-semibold">
              {language === "ta" ? "எஃபிமெரிஸ் என்ஜின்" : "Ephemeris Engine"}
            </span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-serif font-bold text-emerald-700">
            {engineHealth?.status === "healthy" ? "Online" : "Connecting"}
          </div>
          <div className="text-[11px] text-[#52667E] truncate">
            {engineHealth?.engine ? `${engineHealth.engine.name} v${engineHealth.engine.version}` : "XALEN Ephemeris Core"}
          </div>
        </div>

        {/* Stat 3: Security & Access Level */}
        <div className="p-5 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-2">
          <div className="flex items-center justify-between text-[#52667E]">
            <span className="text-xs font-semibold">
              {language === "ta" ? "அணுகல் நிலை" : "Access Level"}
            </span>
            <div className="w-8 h-8 rounded-lg bg-[#FAF2DE] text-[#B8862B] flex items-center justify-center">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-serif font-bold capitalize text-[#102A4C]">
            {user.role}
          </div>
          <div className="text-[11px] text-[#52667E]">
            {user.role === "admin"
              ? (language === "ta" ? "முழு நிர்வாக அதிகாரம்" : "Full administrative authority")
              : (language === "ta" ? "சரிபார்க்கப்பட்ட பயனர் கணக்கு" : "Standard verified account")}
          </div>
        </div>
      </div>

      {/* Main Grid: Profile Info & Saved Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Profile Card */}
        <div className="rounded-2xl border border-[#DDE5F0] bg-white p-6 shadow-xs space-y-5">
          <div className="flex items-center gap-3 pb-4 border-b border-[#F1F5F9]">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#102A4C] to-[#1E3A61] flex items-center justify-center text-white font-serif font-bold text-lg shadow-2xs">
              {user.username?.charAt(0).toUpperCase() || "U"}
            </div>
            <div>
              <div className="font-bold text-[#102A4C] text-base">
                {user.displayName || user.username}
              </div>
              <div className="text-xs text-[#52667E]">@{user.username}</div>
            </div>
          </div>

          <div className="space-y-3.5 text-xs">
            <div className="flex items-center gap-2.5 text-[#334155]">
              <Mail className="w-4 h-4 text-[#94A3B8]" />
              <span className="truncate">{user.email || "No email on record"}</span>
            </div>

            <div className="flex items-center gap-2.5 text-[#334155]">
              <Shield className="w-4 h-4 text-[#94A3B8]" />
              <span>
                {language === "ta" ? "பாத்திரம்:" : "Role:"}{" "}
                <strong className="capitalize text-[#102A4C]">{user.role}</strong>
              </span>
            </div>

            {user.createdAt && (
              <div className="flex items-center gap-2.5 text-[#334155]">
                <Calendar className="w-4 h-4 text-[#94A3B8]" />
                <span>
                  {t.memberSince || "Member since"}: {new Date(user.createdAt).toLocaleDateString()}
                </span>
              </div>
            )}
          </div>

          {/* Quick Tool Links */}
          <div className="pt-4 border-t border-[#F1F5F9] space-y-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-[#94A3B8] block">
              Quick Navigation
            </span>
            <Link
              href="/tools/horoscope"
              className="flex items-center justify-between p-2 rounded-xl text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors group"
            >
              <div className="flex items-center gap-2">
                <Compass className="w-3.5 h-3.5 text-[#B8862B]" />
                <span>Horoscope / KP System</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-[#94A3B8] group-hover:translate-x-0.5 transition-transform" />
            </Link>

            <Link
              href="/tools/horoscope-writing"
              className="flex items-center justify-between p-2 rounded-xl text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors group"
            >
              <div className="flex items-center gap-2">
                <BookOpen className="w-3.5 h-3.5 text-[#B8862B]" />
                <span>{language === "ta" ? "பாரம்பரிய தமிழ் ஜாதகக் குறிப்பு" : "Horoscope Writing"}</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-[#94A3B8] group-hover:translate-x-0.5 transition-transform" />
            </Link>

            <Link
              href="/tools/numerology"
              className="flex items-center justify-between p-2 rounded-xl text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors group"
            >
              <div className="flex items-center gap-2">
                <Sparkles className="w-3.5 h-3.5 text-[#3478F6]" />
                <span>Numerology System</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-[#94A3B8] group-hover:translate-x-0.5 transition-transform" />
            </Link>

            <Link
              href="/tools/advanced-kp"
              className="flex items-center justify-between p-2 rounded-xl text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors group"
            >
              <div className="flex items-center gap-2">
                <Layers className="w-3.5 h-3.5 text-[#B8862B]" />
                <span>Advanced KP &amp; Horary</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-[#94A3B8] group-hover:translate-x-0.5 transition-transform" />
            </Link>

            <Link
              href="/tools/kp-events-prediction"
              className="flex items-center justify-between p-2 rounded-xl text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors group"
            >
              <div className="flex items-center gap-2">
                <Sparkles className="w-3.5 h-3.5 text-[#B8862B]" />
                <span>{language === "ta" ? "KP நிகழ்வு கணிப்பு" : "KP Events & Prediction"}</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-[#94A3B8] group-hover:translate-x-0.5 transition-transform" />
            </Link>

            <Link
              href="/tools/marriage-prediction"
              className="flex items-center justify-between p-2 rounded-xl text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors group"
            >
              <div className="flex items-center gap-2">
                <Heart className="w-3.5 h-3.5 text-rose-600" />
                <span>{language === "ta" ? "திருமண கணிப்பு" : "Marriage Prediction"}</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-[#94A3B8] group-hover:translate-x-0.5 transition-transform" />
            </Link>

            <Link
              href="/horoscopes"
              className="flex items-center justify-between p-2 rounded-xl text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors group"
            >
              <div className="flex items-center gap-2">
                <Database className="w-3.5 h-3.5 text-[#B8862B]" />
                <span>{language === "ta" ? "சேமிக்கப்பட்ட ஜாதகங்கள்" : "Saved Horoscopes"}</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-[#94A3B8] group-hover:translate-x-0.5 transition-transform" />
            </Link>

            <Link
              href="/vastu"
              className="flex items-center justify-between p-2 rounded-xl text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors group"
            >
              <div className="flex items-center gap-2">
                <Home className="w-3.5 h-3.5 text-blue-600" />
                <span>{language === "ta" ? "வாஸ்து சாஸ்திரம்" : "Vastu Shastra Assessment"}</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-[#94A3B8] group-hover:translate-x-0.5 transition-transform" />
            </Link>

            <Link
              href="/remedies"
              className="flex items-center justify-between p-2 rounded-xl text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors group"
            >
              <div className="flex items-center gap-2">
                <Flame className="w-3.5 h-3.5 text-amber-600" />
                <span>{language === "ta" ? "பரிகாரங்கள் & ஆலயங்கள்" : "Remedies & Pariharam"}</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-[#94A3B8] group-hover:translate-x-0.5 transition-transform" />
            </Link>
          </div>

          {user.role === "admin" && (
            <div className="pt-4 border-t border-[#F1F5F9]">
              <Link
                href="/admin"
                className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold text-white bg-[#B8862B] hover:bg-[#996515] shadow-xs transition-colors"
              >
                <Shield className="w-4 h-4" />
                <span>{t.navAdmin || "Open Admin Portal"}</span>
              </Link>
            </div>
          )}
        </div>

        {/* Right Column: Saved Horoscopes Section ONLY */}
        <div className="lg:col-span-2 space-y-6">
          <SavedHoroscopesList showHeader={true} showBanner={true} pageSize={10} columns={2} />
        </div>
      </div>

      {/* Birthday Reminder Modal */}
      <BirthdayReminderModal
        isOpen={isBirthdayModalOpen}
        onClose={() => setIsBirthdayModalOpen(false)}
      />
    </div>
  );
}
