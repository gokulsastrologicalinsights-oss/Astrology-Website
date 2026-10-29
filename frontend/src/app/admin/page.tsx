"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { getHealth, getNumerologyMetadata, listNumerologyReports } from "@/lib/api";
import { HealthResponse, NumerologyMetadataResponse, SavedNumerologyReportResponse } from "@/lib/types";
import {
  Shield,
  ShieldAlert,
  Users,
  Activity,
  Compass,
  CheckCircle2,
  Lock,
  ArrowLeft,
  RefreshCw,
  Clock,
  Layers,
  Sparkles,
  Eye,
  Database,
  ExternalLink,
  Trash2,
  AlertCircle,
} from "lucide-react";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { TenantUserManager, TenantUser } from "@/components/admin/TenantUserManager";

type AdminUser = TenantUser;

export default function AdminPage() {
  const { language, t } = useLanguage();
  const { user, session, role, isLoading: authLoading } = useAuth();
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [numerologyMeta, setNumerologyMeta] = useState<NumerologyMetadataResponse | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [adminReports, setAdminReports] = useState<SavedNumerologyReportResponse[]>([]);
  const [adminHoroscopes, setAdminHoroscopes] = useState<any[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(true);
  const [loadingReports, setLoadingReports] = useState(false);
  const [loadingHoroscopes, setLoadingHoroscopes] = useState(false);
  const [horoscopeToDelete, setHoroscopeToDelete] = useState<any | null>(null);
  const [isDeletingHoroscope, setIsDeletingHoroscope] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchUsers = async () => {
    setLoadingUsers(true);
    setError(null);
    try {
      const res = await fetch("/api/admin/users");
      if (!res.ok) {
        const data = await res.json();
        setError(data.error || "Failed to retrieve user list.");
        setLoadingUsers(false);
        return;
      }
      const data = await res.json();
      setUsers(data.users || []);
    } catch {
      setError("Network error fetching user administration records.");
    } finally {
      setLoadingUsers(false);
    }
  };

  const fetchReports = async () => {
    if (session?.access_token) {
      setLoadingReports(true);
      try {
        const res = await listNumerologyReports(session.access_token, 50, 0);
        setAdminReports(res.reports || []);
      } catch (e) {
        console.warn("Failed to load admin numerology reports:", e);
      } finally {
        setLoadingReports(false);
      }
    }
  };

  const fetchHoroscopes = async () => {
    setLoadingHoroscopes(true);
    try {
      const res = await fetch("/api/horoscopes?all=true&limit=100", { cache: "no-store" });
      if (res.ok) {
        const data = await res.json();
        setAdminHoroscopes(data.horoscopes || []);
      }
    } catch (e) {
      console.warn("Failed to load admin horoscopes:", e);
    } finally {
      setLoadingHoroscopes(false);
    }
  };

  const handleDeleteHoroscope = async (id: string) => {
    setIsDeletingHoroscope(true);
    try {
      const res = await fetch(`/api/horoscopes/${id}`, {
        method: "DELETE",
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || "Failed to delete horoscope.");
      }
      setHoroscopeToDelete(null);
      await fetchHoroscopes();
    } catch (err: any) {
      alert(err.message || "Failed to delete horoscope.");
    } finally {
      setIsDeletingHoroscope(false);
    }
  };

  useEffect(() => {
    let isMounted = true;
    getHealth()
      .then((res) => {
        if (isMounted) setHealth(res);
      })
      .catch(() => {
        if (isMounted) setHealth(null);
      });

    getNumerologyMetadata()
      .then((meta) => {
        if (isMounted) setNumerologyMeta(meta);
      })
      .catch(() => {
        if (isMounted) setNumerologyMeta(null);
      });

    if (role === "admin") {
      fetchUsers();
      fetchReports();
      fetchHoroscopes();
    }

    return () => {
      isMounted = false;
    };
  }, [role, session?.access_token]);

  if (authLoading) {
    return (
      <div className="w-full px-4 py-16 text-center">
        <div className="inline-block animate-spin w-8 h-8 border-4 border-[#B8860B] border-t-transparent rounded-full mb-4" />
        <p className="text-sm text-[#64748B]">{t.loading}</p>
      </div>
    );
  }

  // Non-admin access prevention view
  if (role !== "admin") {
    return (
      <div className="min-h-[calc(100vh-16rem)] flex items-center justify-center px-4 py-12">
        <div className="max-w-md w-full bg-white rounded-2xl border border-rose-200 p-8 text-center shadow-sm">
          <div className="w-14 h-14 rounded-full bg-rose-100 flex items-center justify-center text-rose-600 mx-auto mb-4">
            <ShieldAlert className="w-8 h-8" />
          </div>
          <h1 className="font-serif text-xl font-bold text-[#0F172A]">
            {language === "ta" ? "அணுகல் மறுக்கப்பட்டது" : "Access Denied"}
          </h1>
          <p className="mt-2 text-xs sm:text-sm text-[#64748B] leading-relaxed">
            {language === "ta"
              ? "இந்த பக்கத்தை அணுக நிர்வாக அனுமதி தேவை. நீங்கள் சாதாரண பயனர் பாத்திரத்துடன் உள்நுழைந்துள்ளீர்கள்."
              : "Administrative privileges are required to view this portal. Your authenticated account possesses standard user permissions."}
          </p>
          <div className="mt-6">
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-[#0F172A] hover:bg-[#1E293B] transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>{language === "ta" ? "பயனர் பலகைக்குத் திரும்புக" : "Return to Dashboard"}</span>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 sm:py-8 space-y-6">
      <Breadcrumbs
        items={[
          {
            label: language === "ta" ? "டாஷ்போர்டு" : "Dashboard",
            href: "/dashboard",
          },
          {
            label: language === "ta" ? "நிர்வாக மையம்" : "Admin Portal",
          },
        ]}
      />

      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-[#DDE5F0]">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="font-serif text-2xl sm:text-3xl font-bold text-[#0F172A]">
              {t.adminDashboardTitle}
            </h1>
            <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold uppercase bg-[#0F172A] text-white shadow-2xs">
              <Shield className="w-3.5 h-3.5 text-[#D8BD80]" />
              {t.roleBadgeAdmin}
            </span>
          </div>
          <p className="mt-1 text-xs sm:text-sm text-[#64748B]">
            {t.adminDashboardSubtitle}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={fetchUsers}
            disabled={loadingUsers}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-[#CBD5E1] bg-white hover:bg-[#FAF8F5] text-xs font-semibold text-[#0F172A] transition-colors cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loadingUsers ? "animate-spin" : ""}`} />
            <span>{language === "ta" ? "புதுப்பி" : "Refresh"}</span>
          </button>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-[#CBD5E1] bg-white hover:bg-[#FAF8F5] text-xs font-semibold text-[#0F172A] transition-colors"
          >
            <span>{t.navDashboard}</span>
          </Link>
        </div>
      </div>

      {/* Telemetry Stats Grid */}
      <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Total Users */}
        <div className="rounded-2xl border border-[#E2DCD5] bg-white p-5 shadow-2xs">
          <div className="flex items-center justify-between text-[#64748B]">
            <span className="text-xs font-semibold uppercase tracking-wider">
              {language === "ta" ? "மொத்த பயனர்கள்" : "Registered Users"}
            </span>
            <Users className="w-4 h-4 text-[#B8860B]" />
          </div>
          <div className="mt-3 text-2xl font-serif font-bold text-[#0F172A]">
            {users.length}
          </div>
          <div className="mt-1 text-[11px] text-[#94A3B8]">
            {users.filter((u) => u.role === "admin").length} Admins •{" "}
            {users.filter((u) => u.role === "user").length} Users
          </div>
        </div>

        {/* Astronomical Engine */}
        <div className="rounded-2xl border border-[#E2DCD5] bg-white p-5 shadow-2xs">
          <div className="flex items-center justify-between text-[#64748B]">
            <span className="text-xs font-semibold uppercase tracking-wider">
              {language === "ta" ? "எஃபிமெரிஸ் இயந்திரம்" : "Ephemeris Engine"}
            </span>
            <Compass className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="mt-3 text-sm font-bold text-[#0F172A] truncate">
            {health?.engine.name || "XALEN Ephemeris"}
          </div>
          <div className="mt-1 text-[11px] text-[#94A3B8]">
            v{health?.engine.version || "0.6.0"} • Deterministic
          </div>
        </div>

        {/* Numerology Engine */}
        <div className="rounded-2xl border border-[#E2DCD5] bg-white p-5 shadow-2xs">
          <div className="flex items-center justify-between text-[#64748B]">
            <span className="text-xs font-semibold uppercase tracking-wider">
              {language === "ta" ? "எண்கணித இயந்திரம்" : "Numerology Engine"}
            </span>
            <Sparkles className="w-4 h-4 text-[#B8860B]" />
          </div>
          <div className="mt-3 text-sm font-bold text-[#0F172A] truncate">
            {numerologyMeta?.service || "Deterministic Engine"}
          </div>
          <div className="mt-1 text-[11px] text-[#94A3B8]">
            v{numerologyMeta?.engine_version || "1.0.0"} • Clean-Room
          </div>
        </div>

        {/* Database Authorization */}
        <div className="rounded-2xl border border-[#E2DCD5] bg-white p-5 shadow-2xs">
          <div className="flex items-center justify-between text-[#64748B]">
            <span className="text-xs font-semibold uppercase tracking-wider">
              {language === "ta" ? "தரவுத்தள பாதுகாப்பு" : "Database Security"}
            </span>
            <Lock className="w-4 h-4 text-[#B8860B]" />
          </div>
          <div className="mt-3 text-sm font-bold text-emerald-700 flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>RLS Active</span>
          </div>
          <div className="mt-1 text-[11px] text-[#94A3B8]">
            Supabase PostgreSQL • Isolated
          </div>
        </div>

        {/* Backend Status */}
        <div className="rounded-2xl border border-[#E2DCD5] bg-white p-5 shadow-2xs">
          <div className="flex items-center justify-between text-[#64748B]">
            <span className="text-xs font-semibold uppercase tracking-wider">
              {language === "ta" ? "சேவையக நிலை" : "FastAPI Status"}
            </span>
            <Activity className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="mt-3 text-sm font-bold text-[#0F172A] capitalize">
            {health?.status || "Connecting..."}
          </div>
          <div className="mt-1 text-[11px] text-[#94A3B8]">
            Zero AI / Pure Algorithmic
          </div>
        </div>
      </div>

      {/* Astrological Rules Engine Administration Banner */}
      <div className="rounded-2xl border border-[#D8BD80] bg-[#FAF8F2] p-5 shadow-2xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white border border-[#D8BD80] flex items-center justify-center text-[#B4872B] shrink-0">
            <Compass className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-[#183047]">
              {language === "ta" ? "ஜோதிட விதிகள் மற்றும் கணிப்புகள் மேலாண்மை" : "Astrological Rules & Predictions Engine"}
            </h3>
            <p className="text-xs text-[#52667E]">
              {language === "ta"
                ? "8 பிரிவுகளில் உள்ள பராசர மற்றும் கே.பி விதிமுறைகளை உருவாக்குதல், திருத்துதல் மற்றும் சோதித்தல்."
                : "Manage, validate, test against saved horoscopes, and version control the shared library of rules."}
            </p>
          </div>
        </div>
        <Link
          href="/admin/rules"
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#B4872B] hover:bg-[#8C6D23] text-white text-xs font-bold transition-colors shadow-2xs shrink-0 self-start sm:self-auto"
        >
          <span>{language === "ta" ? "விதிகள் மையம்" : "Manage Rules Library"}</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </Link>
      </div>

      {/* Astrologer Rental Profiles & Selected Access Management Suite */}
      <TenantUserManager users={users} onRefresh={fetchUsers} />

      {/* Saved Numerology Reports Audit Table */}
      <div className="mt-8 rounded-2xl border border-[#E2DCD5] bg-white overflow-hidden shadow-xs">
        <div className="p-5 border-b border-[#E2DCD5] flex items-center justify-between bg-[#FAF8F5]">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-[#B8860B]" />
            <h2 className="font-serif text-base font-bold text-[#0F172A]">
              {language === "ta" ? "எண்கணித அறிக்கைகள் தணிக்கை" : "Numerology Reports Audit"}
            </h2>
            <span className="ml-2 px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
              {adminReports.length}
            </span>
          </div>
          <button
            type="button"
            onClick={fetchReports}
            disabled={loadingReports}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#CBD5E1] bg-white hover:bg-[#FAF8F5] text-xs font-medium text-[#0F172A] transition-colors cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-3 h-3 ${loadingReports ? "animate-spin" : ""}`} />
            <span>{language === "ta" ? "புதுப்பி" : "Refresh"}</span>
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#FAF8F5] text-[#475569] uppercase font-bold border-b border-[#E2DCD5]">
              <tr>
                <th className="px-5 py-3">#</th>
                <th className="px-5 py-3">{language === "ta" ? "பெயர்" : "Person Name"}</th>
                <th className="px-5 py-3">{language === "ta" ? "முறை" : "Method"}</th>
                <th className="px-5 py-3">{language === "ta" ? "பிறந்த தேதி" : "Birth Date"}</th>
                <th className="px-5 py-3">{language === "ta" ? "மாநாடு / பதிப்பு" : "Convention / Engine"}</th>
                <th className="px-5 py-3">{language === "ta" ? "உருவாக்கிய தேதி" : "Created At"}</th>
                <th className="px-5 py-3 text-right">{language === "ta" ? "நடவடிக்கை" : "Action"}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E2DCD5] text-[#334155]">
              {loadingReports ? (
                <tr>
                  <td colSpan={7} className="px-5 py-8 text-center text-[#94A3B8]">
                    <div className="inline-block animate-spin w-5 h-5 border-2 border-[#B8860B] border-t-transparent rounded-full mb-2" />
                    <div>{language === "ta" ? "அறிக்கைகள் ஏற்றப்படுகின்றன..." : "Loading numerology reports..."}</div>
                  </td>
                </tr>
              ) : adminReports.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-5 py-8 text-center text-[#94A3B8]">
                    {language === "ta" ? "எந்த எண்கணித அறிக்கையும் சேமிக்கப்படவில்லை." : "No saved numerology reports found."}
                  </td>
                </tr>
              ) : (
                adminReports.map((report) => (
                  <tr key={report.id} className="hover:bg-[#FAF8F5]/80 transition-colors">
                    <td className="px-5 py-3.5 font-mono text-[#94A3B8]">
                      #{report.display_number}
                    </td>
                    <td className="px-5 py-3.5 font-bold text-[#0F172A]">
                      {report.person_name}
                    </td>
                    <td className="px-5 py-3.5">
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-[#0F172A] text-white">
                        {report.method.replace("_", " ")}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-[#475569]">
                      {report.birth_date}
                    </td>
                    <td className="px-5 py-3.5 text-[#64748B]">
                      <span className="capitalize">{report.system_convention}</span> • v{report.engine_version}
                    </td>
                    <td className="px-5 py-3.5 text-[#64748B]">
                      {new Date(report.created_at).toLocaleString()}
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <Link
                        href={`/numerology/report/${report.id}`}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded border border-[#CBD5E1] bg-white hover:bg-[#FAF8F5] text-[11px] font-semibold text-[#0F172A] transition-colors"
                      >
                        <Eye className="w-3 h-3 text-[#B8860B]" />
                        <span>{language === "ta" ? "பார்வை" : "View"}</span>
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* All Saved Horoscopes Global Management Table */}
      <div className="mt-8 rounded-2xl border border-[#E2DCD5] bg-white overflow-hidden shadow-xs">
        <div className="p-5 border-b border-[#E2DCD5] flex items-center justify-between bg-[#FAF8F5]">
          <div className="flex items-center gap-2">
            <Compass className="w-4 h-4 text-[#B8860B]" />
            <h2 className="font-serif text-base font-bold text-[#0F172A]">
              {language === "ta" ? "அனைத்து சேமிக்கப்பட்ட ஜாதகங்கள் (உலகளாவிய நிர்வாகம்)" : "All Saved Horoscopes (Global Management)"}
            </h2>
            <span className="ml-2 px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
              {adminHoroscopes.length}
            </span>
          </div>
          <button
            type="button"
            onClick={fetchHoroscopes}
            disabled={loadingHoroscopes}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#CBD5E1] bg-white hover:bg-[#FAF8F5] text-xs font-medium text-[#0F172A] transition-colors cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-3 h-3 ${loadingHoroscopes ? "animate-spin" : ""}`} />
            <span>{language === "ta" ? "புதுப்பி" : "Refresh"}</span>
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#FAF8F5] text-[#475569] uppercase font-bold border-b border-[#E2DCD5]">
              <tr>
                <th className="px-4 py-3">Stable Record UUID</th>
                <th className="px-4 py-3">Owner Account</th>
                <th className="px-4 py-3">Owner Sequence</th>
                <th className="px-4 py-3">Subject Name</th>
                <th className="px-4 py-3">Birth Details</th>
                <th className="px-4 py-3">Birthplace</th>
                <th className="px-4 py-3">Ayanamsa</th>
                <th className="px-4 py-3">Calculated Date</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E2DCD5] text-[#334155]">
              {loadingHoroscopes ? (
                <tr>
                  <td colSpan={9} className="px-5 py-8 text-center text-[#94A3B8]">
                    <div className="inline-block animate-spin w-5 h-5 border-2 border-[#B8860B] border-t-transparent rounded-full mb-2" />
                    <div>{language === "ta" ? "ஜாதகங்கள் ஏற்றப்படுகின்றன..." : "Loading saved horoscopes..."}</div>
                  </td>
                </tr>
              ) : adminHoroscopes.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-5 py-8 text-center text-[#94A3B8]">
                    {language === "ta" ? "சேமிக்கப்பட்ட ஜாதகங்கள் எவையும் இல்லை." : "No saved horoscopes found across system."}
                  </td>
                </tr>
              ) : (
                adminHoroscopes.map((h, index) => {
                  const ayanamsaLabel =
                    h.ayanamsa_id === 1 ? "KP" : h.ayanamsa_id === 2 ? "Raman" : "Lahiri";
                  return (
                    <tr key={h.id} className="hover:bg-[#FAF8F5]/80 transition-colors">
                      <td className="px-4 py-3 font-mono text-[11px] text-[#64748B]">
                        <span title={h.id}>{h.id.substring(0, 8)}...</span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="font-semibold text-[#0F172A]">
                          @{h.owner?.username || "unknown"}
                        </div>
                        {h.owner?.display_name && (
                          <div className="text-[10px] text-[#64748B]">{h.owner.display_name}</div>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
                          Horoscope No. {h.display_number}
                        </span>
                      </td>
                      <td className="px-4 py-3 font-bold text-[#0F172A]">
                        {h.person_name || "Unnamed"}
                      </td>
                      <td className="px-4 py-3 text-[#475569]">
                        <div>{h.birth_date}</div>
                        <div className="text-[10px] font-mono text-[#64748B]">
                          {h.birth_time} {h.timezone ? `(${h.timezone})` : ""}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-[#475569] max-w-[140px] truncate" title={h.birthplace}>
                        {h.birthplace || "—"}
                      </td>
                      <td className="px-4 py-3">
                        <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-[#FAF8F5] border border-[#E2DCD5]">
                          {ayanamsaLabel}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-[#64748B] font-mono text-[10px]">
                        {new Date(h.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="inline-flex items-center gap-1.5">
                          <Link
                            href={`/horoscope/results?id=${h.id}`}
                            className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-[#0F172A] hover:bg-[#1E293B] text-white text-[11px] font-semibold transition-colors"
                            title="Reopen exact snapshot"
                          >
                            <span>Open</span>
                            <ExternalLink className="w-3 h-3 text-[#D8BD80]" />
                          </Link>
                          <button
                            type="button"
                            onClick={() => setHoroscopeToDelete(h)}
                            className="p-1 rounded border border-transparent hover:border-rose-200 hover:bg-rose-50 text-[#94A3B8] hover:text-rose-600 transition-colors cursor-pointer"
                            title="Delete horoscope record"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {horoscopeToDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs">
          <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl border border-[#E2DCD5] space-y-4">
            <div className="flex items-center gap-2.5 text-rose-600">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <h4 className="font-bold text-sm text-[#0F172A]">
                {language === "ta" ? "ஜாதகத்தை நீக்கவா?" : "Delete Horoscope as Admin?"}
              </h4>
            </div>
            <p className="text-xs text-[#64748B] leading-relaxed">
              {language === "ta"
                ? `"${horoscopeToDelete.person_name || 'ஜாதகம்'}" (வரிசை எண் ${horoscopeToDelete.display_number}) நிரந்தரமாக நீக்கப்படும். இந்த வரிசை எண் மீண்டும் பயன்படுத்தப்படாது.`
                : `"${horoscopeToDelete.person_name || 'Horoscope'}" (Horoscope No. ${horoscopeToDelete.display_number}) belonging to @${horoscopeToDelete.owner?.username || 'user'} will be permanently deleted. This sequential number will remain unused.`}
            </p>
            <div className="flex items-center justify-end gap-2 pt-2 border-t border-[#E2DCD5]">
              <button
                type="button"
                onClick={() => setHoroscopeToDelete(null)}
                disabled={isDeletingHoroscope}
                className="px-3 py-1.5 rounded-lg border border-[#CBD5E1] bg-white hover:bg-[#FAF8F5] text-xs font-semibold text-[#475569] cursor-pointer"
              >
                {language === "ta" ? "ரத்து" : "Cancel"}
              </button>
              <button
                type="button"
                onClick={() => handleDeleteHoroscope(horoscopeToDelete.id)}
                disabled={isDeletingHoroscope}
                className="px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold disabled:opacity-50 cursor-pointer"
              >
                {isDeletingHoroscope ? "..." : language === "ta" ? "ஆம், நீக்கு" : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
