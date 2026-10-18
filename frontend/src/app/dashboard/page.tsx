"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { listNumerologyReports, getHealth } from "@/lib/api";
import { SavedNumerologyReportResponse, HealthResponse } from "@/lib/types";
import { SavedHoroscopesList } from "@/components/saved/SavedHoroscopesList";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  Compass,
  User,
  Mail,
  Calendar,
  Shield,
  ArrowRight,
  Sparkles,
  Database,
  LogOut,
  Clock,
  Layers,
  Activity,
  ShieldCheck,
  TrendingUp,
  ExternalLink,
  ChevronRight,
} from "lucide-react";

export default function DashboardPage() {
  const router = useRouter();
  const { language, t } = useLanguage();
  const { user, session, isAuthenticated, isLoading, logout } = useAuth();

  const [numerologyReports, setNumerologyReports] = useState<SavedNumerologyReportResponse[]>([]);
  const [totalNumerologyCount, setTotalNumerologyCount] = useState<number>(0);
  const [totalHoroscopesCount, setTotalHoroscopesCount] = useState<number>(0);
  const [loadingReports, setLoadingReports] = useState(false);
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

    // 2. Total numerology reports from backend
    if (session?.access_token) {
      setLoadingReports(true);
      listNumerologyReports(session.access_token, 10, 0)
        .then((res) => {
          setNumerologyReports(res.reports || []);
          setTotalNumerologyCount(res.count || 0);
        })
        .catch((err) => {
          console.warn("Failed to load numerology reports:", err);
        })
        .finally(() => {
          setLoadingReports(false);
        });
    }

    // 3. Engine health
    getHealth()
      .then((h) => setEngineHealth(h))
      .catch(() => setEngineHealth(null));
  }, [session?.access_token]);

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
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-8">
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
            onClick={logout}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl border border-[#DDE5F0] bg-white hover:bg-rose-50 text-xs font-semibold text-rose-600 transition-colors cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>{t.navLogout}</span>
          </button>
        </div>
      </div>

      {/* Real Statistics Metrics Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Stat 1: Total Saved Horoscopes */}
        <div className="p-5 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-2">
          <div className="flex items-center justify-between text-[#52667E]">
            <span className="text-xs font-semibold">Saved Horoscopes</span>
            <div className="w-8 h-8 rounded-lg bg-[#FAF2DE] text-[#B8862B] flex items-center justify-center">
              <Compass className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-serif font-bold text-[#102A4C]">
            {totalHoroscopesCount}
          </div>
          <div className="text-[11px] text-[#52667E] flex items-center gap-1">
            <span>Stored in Supabase database</span>
          </div>
        </div>

        {/* Stat 2: Total Saved Numerology Reports */}
        <div className="p-5 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-2">
          <div className="flex items-center justify-between text-[#52667E]">
            <span className="text-xs font-semibold">Numerology Reports</span>
            <div className="w-8 h-8 rounded-lg bg-[#EBF2FE] text-[#3478F6] flex items-center justify-center">
              <Sparkles className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-serif font-bold text-[#102A4C]">
            {totalNumerologyCount}
          </div>
          <div className="text-[11px] text-[#52667E] flex items-center gap-1">
            <span>Deterministic readings</span>
          </div>
        </div>

        {/* Stat 3: Astronomical Engine Status */}
        <div className="p-5 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-2">
          <div className="flex items-center justify-between text-[#52667E]">
            <span className="text-xs font-semibold">Ephemeris Engine</span>
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

        {/* Stat 4: Security & Access Level */}
        <div className="p-5 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-2">
          <div className="flex items-center justify-between text-[#52667E]">
            <span className="text-xs font-semibold">Access Level</span>
            <div className="w-8 h-8 rounded-lg bg-[#FAF2DE] text-[#B8862B] flex items-center justify-center">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-serif font-bold capitalize text-[#102A4C]">
            {user.role}
          </div>
          <div className="text-[11px] text-[#52667E]">
            {user.role === "admin" ? "Full administrative authority" : "Standard verified account"}
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
              href="/horoscopes"
              className="flex items-center justify-between p-2 rounded-xl text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors group"
            >
              <div className="flex items-center gap-2">
                <Database className="w-3.5 h-3.5 text-[#B8862B]" />
                <span>{language === "ta" ? "சேமிக்கப்பட்ட ஜாதகங்கள்" : "Saved Horoscopes"}</span>
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

        {/* Right Columns: Saved Sections */}
        <div className="lg:col-span-2 space-y-6">
          {/* Saved Numerology Reports Section */}
          <div className="rounded-2xl border border-[#DDE5F0] bg-white p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#F1F5F9]">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-[#3478F6]" />
                <h2 className="font-serif text-base font-bold text-[#102A4C]">
                  {t.savedNumerologyTitle || "Saved Numerology Reports"}
                </h2>
              </div>
              <Link
                href="/tools/numerology?tab=reports"
                className="text-xs font-semibold text-[#3478F6] hover:underline inline-flex items-center gap-1"
              >
                <span>View All Reports</span>
                <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            {loadingReports ? (
              <div className="py-6 text-center text-xs text-[#52667E]">
                <div className="inline-block animate-spin w-4 h-4 border-2 border-[#3478F6] border-t-transparent rounded-full mb-1" />
                <p>{t.loading}</p>
              </div>
            ) : numerologyReports.length === 0 ? (
              <div className="py-6 px-4 rounded-xl border border-dashed border-[#DDE5F0] bg-[#F8FAFC] text-center">
                <p className="text-xs text-[#52667E]">
                  {t.savedNumerologyEmpty || "No saved numerology reports yet."}
                </p>
                <div className="mt-2.5">
                  <Link
                    href="/numerology/traditional"
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold text-white bg-[#102A4C] hover:bg-[#1E3A61]"
                  >
                    <span>Calculate Numerology</span>
                    <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            ) : (
              <div className="divide-y divide-[#F1F5F9]">
                {numerologyReports.slice(0, 3).map((item) => (
                  <div
                    key={item.id}
                    className="py-2.5 flex items-center justify-between hover:bg-[#F8FAFC] px-2 rounded-lg transition-colors"
                  >
                    <div className="flex items-center gap-2.5">
                      <span className="w-7 h-7 rounded-md bg-[#EBF2FE] border border-[#BFDBFE] text-[#3478F6] font-bold text-xs flex items-center justify-center">
                        #{item.display_number}
                      </span>
                      <div>
                        <div className="font-bold text-xs text-[#102A4C]">
                          {item.person_name}
                        </div>
                        <div className="text-[10px] text-[#64748B]">
                          DOB: {item.birth_date} • {item.method.replace("_", " ").toUpperCase()}
                        </div>
                      </div>
                    </div>

                    <Link
                      href={`/numerology/report/${item.id}`}
                      className="px-2.5 py-1 rounded-lg border border-[#DDE5F0] bg-white hover:bg-[#EBF2FE] text-xs font-semibold text-[#102A4C]"
                    >
                      {t.reopenReport || "Reopen"}
                    </Link>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Saved Horoscopes Section */}
          <div className="rounded-2xl border border-[#DDE5F0] bg-white p-6 shadow-xs">
            <SavedHoroscopesList />
          </div>
        </div>
      </div>
    </div>
  );
}
