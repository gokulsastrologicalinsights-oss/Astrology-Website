"use client";

import React, { useState } from "react";
import { useLanguage } from "@/lib/i18n";
import {
  MODULE_REGISTRY,
  PLAN_PRESETS,
  PermissionKey,
  UserPermissions,
  UserSubscription,
  BASIC_PLAN_PERMISSIONS,
  PRO_PLAN_PERMISSIONS,
  TAMIL_SPECIALIST_PERMISSIONS,
} from "@/lib/permissions";
import {
  Users,
  UserPlus,
  Shield,
  Key,
  Calendar,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  Sparkles,
  Edit2,
  PauseCircle,
  PlayCircle,
  Trash2,
  Lock,
  Search,
  Check,
  X,
  RefreshCw,
  Eye,
  EyeOff,
} from "lucide-react";

export interface TenantUser {
  id: string;
  username: string;
  display_name: string | null;
  email: string | null;
  role: "admin" | "user";
  must_change_password: boolean;
  created_at: string;
  updated_at?: string;
  last_sign_in_at?: string | null;
  subscription?: UserSubscription;
  permissions?: UserPermissions;
}

interface TenantUserManagerProps {
  users: TenantUser[];
  onRefresh: () => Promise<void>;
}

export function TenantUserManager({ users, onRefresh }: TenantUserManagerProps) {
  const { language } = useLanguage();
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStatus, setFilterStatus] = useState<"all" | "active" | "suspended" | "expired">("all");

  // Modal States
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<TenantUser | null>(null);
  const [resetPwdUser, setResetPwdUser] = useState<TenantUser | null>(null);
  const [deletingUser, setDeletingUser] = useState<TenantUser | null>(null);

  // Form States for Creation / Edit
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    displayName: "",
    password: "",
    role: "user" as "admin" | "user",
    tier: "basic" as "basic" | "pro" | "enterprise" | "custom",
    status: "active" as "active" | "suspended" | "expired",
    validityDuration: "30", // in days, or "unlimited"
    customValidUntil: "",
    maxPdfMonthly: 30,
    permissions: { ...BASIC_PLAN_PERMISSIONS } as UserPermissions,
  });

  const [formError, setFormError] = useState<string | null>(null);
  const [formLoading, setFormLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [newPasswordInput, setNewPasswordInput] = useState("");

  // Quick Plan Preset Selection
  const applyPreset = (presetKey: string) => {
    if (presetKey === "basic") {
      setFormData((prev) => ({
        ...prev,
        tier: "basic",
        maxPdfMonthly: 30,
        permissions: { ...BASIC_PLAN_PERMISSIONS },
      }));
    } else if (presetKey === "tamil_specialist") {
      setFormData((prev) => ({
        ...prev,
        tier: "pro",
        maxPdfMonthly: 100,
        permissions: { ...TAMIL_SPECIALIST_PERMISSIONS },
      }));
    } else if (presetKey === "pro") {
      setFormData((prev) => ({
        ...prev,
        tier: "pro",
        maxPdfMonthly: 9999,
        permissions: { ...PRO_PLAN_PERMISSIONS },
      }));
    }
  };

  const generateRandomPassword = () => {
    const chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789!@#$%";
    let pwd = "";
    for (let i = 0; i < 12; i++) {
      pwd += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    setFormData((prev) => ({ ...prev, password: pwd }));
    setShowPassword(true);
  };

  const openCreateModal = () => {
    setFormData({
      username: "",
      email: "",
      displayName: "",
      password: "",
      role: "user",
      tier: "basic",
      status: "active",
      validityDuration: "30",
      customValidUntil: "",
      maxPdfMonthly: 30,
      permissions: { ...BASIC_PLAN_PERMISSIONS },
    });
    setFormError(null);
    setIsAddModalOpen(true);
  };

  const openEditModal = (u: TenantUser) => {
    setEditingUser(u);
    const sub = u.subscription;
    const perms = u.permissions || (sub?.tier === "pro" ? PRO_PLAN_PERMISSIONS : BASIC_PLAN_PERMISSIONS);
    setFormData({
      username: u.username,
      email: u.email || "",
      displayName: u.display_name || "",
      password: "",
      role: u.role,
      tier: (sub?.tier as any) || "basic",
      status: (sub?.status as any) || "active",
      validityDuration: "custom",
      customValidUntil: sub?.validUntil ? new Date(sub.validUntil).toISOString().split("T")[0] : "",
      maxPdfMonthly: sub?.maxPdfMonthly || 30,
      permissions: { ...perms },
    });
    setFormError(null);
  };

  // Submit Create
  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormLoading(true);
    setFormError(null);

    try {
      let validUntil: string | null = null;
      if (formData.validityDuration !== "unlimited") {
        const days = parseInt(formData.validityDuration, 10);
        if (!isNaN(days) && days > 0) {
          const d = new Date();
          d.setDate(d.getDate() + days);
          validUntil = d.toISOString();
        }
      }

      const res = await fetch("/api/admin/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: formData.username,
          email: formData.email,
          password: formData.password,
          displayName: formData.displayName,
          role: formData.role,
          tier: formData.tier,
          validUntil,
          status: formData.status,
          permissions: formData.permissions,
          maxPdfMonthly: formData.maxPdfMonthly,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Failed to create account.");
      }

      setIsAddModalOpen(false);
      await onRefresh();
    } catch (err: any) {
      setFormError(err.message || "Failed to create user.");
    } finally {
      setFormLoading(false);
    }
  };

  // Submit Edit
  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingUser) return;
    setFormLoading(true);
    setFormError(null);

    try {
      let validUntil: string | null = null;
      if (formData.customValidUntil) {
        validUntil = new Date(formData.customValidUntil).toISOString();
      }

      const res = await fetch("/api/admin/users", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userId: editingUser.id,
          displayName: formData.displayName,
          role: formData.role,
          tier: formData.tier,
          status: formData.status,
          validUntil,
          permissions: formData.permissions,
          maxPdfMonthly: formData.maxPdfMonthly,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Failed to update account.");
      }

      setEditingUser(null);
      await onRefresh();
    } catch (err: any) {
      setFormError(err.message || "Failed to update user.");
    } finally {
      setFormLoading(false);
    }
  };

  // Quick Action: Extend Validity (+30 days or +365 days)
  const handleQuickExtend = async (u: TenantUser, daysToAdd: number) => {
    try {
      let baseDate = new Date();
      if (u.subscription?.validUntil) {
        const cur = new Date(u.subscription.validUntil);
        if (cur.getTime() > baseDate.getTime()) {
          baseDate = cur;
        }
      }
      baseDate.setDate(baseDate.getDate() + daysToAdd);

      const res = await fetch("/api/admin/users", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userId: u.id,
          validUntil: baseDate.toISOString(),
          status: "active",
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Failed to extend subscription.");
      }
      await onRefresh();
    } catch (err: any) {
      alert(err.message);
    }
  };

  // Quick Action: Toggle Pause / Resume
  const handleToggleStatus = async (u: TenantUser) => {
    const newStatus = u.subscription?.status === "suspended" ? "active" : "suspended";
    try {
      const res = await fetch("/api/admin/users", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userId: u.id,
          status: newStatus,
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Failed to toggle status.");
      }
      await onRefresh();
    } catch (err: any) {
      alert(err.message);
    }
  };

  // Quick Action: Reset Password Submit
  const handleResetPasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resetPwdUser || newPasswordInput.length < 8) return;
    setFormLoading(true);
    setFormError(null);

    try {
      const res = await fetch("/api/admin/users", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userId: resetPwdUser.id,
          newPassword: newPasswordInput,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Failed to reset password.");
      }

      setResetPwdUser(null);
      setNewPasswordInput("");
      alert("Password updated successfully.");
    } catch (err: any) {
      setFormError(err.message || "Failed to reset password.");
    } finally {
      setFormLoading(false);
    }
  };

  // Delete User Submit
  const handleDeleteSubmit = async () => {
    if (!deletingUser) return;
    setFormLoading(true);
    try {
      const res = await fetch("/api/admin/users", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userId: deletingUser.id }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Failed to delete account.");
      }

      setDeletingUser(null);
      await onRefresh();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setFormLoading(false);
    }
  };

  // Filtered Users
  const filteredUsers = users.filter((u) => {
    const q = searchQuery.toLowerCase();
    const matchesSearch =
      u.username.toLowerCase().includes(q) ||
      (u.display_name && u.display_name.toLowerCase().includes(q)) ||
      (u.email && u.email.toLowerCase().includes(q));

    if (!matchesSearch) return false;

    const status = u.subscription?.status || "active";
    if (filterStatus === "active") return status === "active";
    if (filterStatus === "suspended") return status === "suspended";
    if (filterStatus === "expired") return status === "expired";
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Top Action Header */}
      <div className="rounded-2xl border border-[#D8BD80] bg-[#FAF8F5] p-5 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-600/10 text-amber-700 font-bold">
                <Users className="h-5 w-5" />
              </div>
              <h2 className="font-serif text-lg font-bold text-[#0F172A]">
                {language === "ta"
                  ? "வாடகை ஜோதிடர்கள் & அனுமதி மேலாண்மை"
                  : "Astrologer Rental Accounts & Selected Access"}
              </h2>
            </div>
            <p className="mt-1 text-xs text-[#64748B]">
              {language === "ta"
                ? "புதிய ஜோதிடர்களுக்கு கணக்கு உருவாக்குதல், தேவையான பகுதிகளை மட்டும் திறந்துவிடுதல் (Selected Access) மற்றும் சந்தா காலாவதி கட்டுப்பாடு."
                : "Create tenant profiles, configure modular feature permissions (Parashari, KP, Tamil Booklet, Porutham), and monitor subscription renewals."}
            </p>
          </div>

          <button
            type="button"
            onClick={openCreateModal}
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-amber-600 px-4 py-2.5 text-xs font-bold text-white shadow-md shadow-amber-600/20 transition hover:bg-amber-500 cursor-pointer self-start md:self-auto"
          >
            <UserPlus className="h-4 w-4" />
            <span>
              {language === "ta"
                ? "+ புதிய ஜோதிடர் கணக்கு உருவாக்கு"
                : "+ Add Astrologer Profile"}
            </span>
          </button>
        </div>

        {/* Search & Filter Bar */}
        <div className="mt-4 flex flex-col sm:flex-row items-center gap-3 pt-4 border-t border-[#E2DCD5]">
          <div className="relative flex-1 w-full">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-[#94A3B8]" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={
                language === "ta"
                  ? "பெயர், பயனர் பெயர் அல்லது மின்னஞ்சல் மூலம் தேடுக..."
                  : "Search astrologers by name, username, or email..."
              }
              className="w-full rounded-xl border border-[#CBD5E1] bg-white pl-9 pr-4 py-2 text-xs text-[#0F172A] placeholder-[#94A3B8] focus:border-amber-600 focus:outline-none"
            />
          </div>

          <div className="flex items-center gap-1.5 self-start sm:self-auto">
            {(["all", "active", "suspended", "expired"] as const).map((st) => (
              <button
                key={st}
                type="button"
                onClick={() => setFilterStatus(st)}
                className={`rounded-lg px-3 py-1.5 text-xs font-semibold capitalize transition ${
                  filterStatus === st
                    ? "bg-[#0F172A] text-white"
                    : "bg-white border border-[#CBD5E1] text-[#64748B] hover:bg-[#FAF8F5]"
                }`}
              >
                {st}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="rounded-2xl border border-[#E2DCD5] bg-white overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#FAF8F5] text-[#475569] uppercase font-bold border-b border-[#E2DCD5]">
              <tr>
                <th className="px-5 py-3">Astrologer / Studio</th>
                <th className="px-5 py-3">Plan & Status</th>
                <th className="px-5 py-3">Validity & Expiry</th>
                <th className="px-5 py-3">Selected Access (Modules)</th>
                <th className="px-5 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E2DCD5] text-[#334155]">
              {filteredUsers.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-5 py-10 text-center text-[#94A3B8]">
                    No astrologer accounts matched your search.
                  </td>
                </tr>
              ) : (
                filteredUsers.map((u) => {
                  const sub = u.subscription;
                  const perms = u.permissions || (sub?.tier === "pro" ? PRO_PLAN_PERMISSIONS : BASIC_PLAN_PERMISSIONS);
                  const activeModulesCount = Object.values(perms).filter(Boolean).length;
                  const isAdmin = u.role === "admin";

                  // Expiry calculations
                  let expiryLabel = "Lifetime / Indefinite";
                  let isExpired = false;
                  if (sub?.validUntil && !isAdmin) {
                    const expDate = new Date(sub.validUntil);
                    const diffDays = Math.ceil((expDate.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
                    if (diffDays < 0) {
                      isExpired = true;
                      expiryLabel = `Expired ${Math.abs(diffDays)}d ago`;
                    } else {
                      expiryLabel = `Expires in ${diffDays} days (${expDate.toLocaleDateString()})`;
                    }
                  }

                  const status = isAdmin ? "active" : isExpired ? "expired" : sub?.status || "active";

                  return (
                    <tr key={u.id} className="hover:bg-[#FAF8F5]/80 transition">
                      {/* Astrologer Column */}
                      <td className="px-5 py-3.5">
                        <div className="font-bold text-[#0F172A] text-sm flex items-center gap-1.5">
                          {u.display_name || u.username}
                          {isAdmin && (
                            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-[#0F172A] text-white">
                              ADMIN
                            </span>
                          )}
                        </div>
                        <div className="text-[11px] text-[#64748B] font-mono">@{u.username}</div>
                        {u.email && <div className="text-[11px] text-[#94A3B8]">{u.email}</div>}
                      </td>

                      {/* Plan & Status */}
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-1.5">
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-amber-500/10 text-amber-800 border border-amber-500/20">
                            {isAdmin ? "Enterprise" : sub?.tier || "Basic"}
                          </span>
                        </div>
                        <div className="mt-1 flex items-center gap-1">
                          {status === "active" && (
                            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700">
                              <CheckCircle2 className="h-3 w-3 text-emerald-600" />
                              Active
                            </span>
                          )}
                          {status === "suspended" && (
                            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-700">
                              <PauseCircle className="h-3 w-3 text-amber-600" />
                              Suspended
                            </span>
                          )}
                          {status === "expired" && (
                            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-rose-700">
                              <XCircle className="h-3 w-3 text-rose-600" />
                              Expired
                            </span>
                          )}
                        </div>
                      </td>

                      {/* Validity & Expiry */}
                      <td className="px-5 py-3.5">
                        <div className={`font-medium ${isExpired ? "text-rose-600 font-bold" : "text-[#475569]"}`}>
                          {expiryLabel}
                        </div>
                        {!isAdmin && (
                          <div className="mt-1 flex items-center gap-1.5">
                            <button
                              type="button"
                              onClick={() => handleQuickExtend(u, 30)}
                              className="px-2 py-0.5 rounded border border-[#CBD5E1] bg-white hover:bg-emerald-50 text-[10px] font-bold text-emerald-700 transition"
                              title="Extend subscription by 30 days"
                            >
                              +30 Days
                            </button>
                            <button
                              type="button"
                              onClick={() => handleQuickExtend(u, 365)}
                              className="px-2 py-0.5 rounded border border-[#CBD5E1] bg-white hover:bg-emerald-50 text-[10px] font-bold text-emerald-700 transition"
                              title="Extend subscription by 1 year"
                            >
                              +1 Year
                            </button>
                          </div>
                        )}
                      </td>

                      {/* Selected Access Chips */}
                      <td className="px-5 py-3.5">
                        <div className="text-[11px] font-bold text-[#0F172A] mb-1">
                          {activeModulesCount} of 10 Modules Unlocked
                        </div>
                        <div className="flex flex-wrap gap-1 max-w-sm">
                          {MODULE_REGISTRY.map((m) => {
                            const isAllowed = isAdmin || Boolean(perms[m.key]);
                            return (
                              <span
                                key={m.key}
                                className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                                  isAllowed
                                    ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                                    : "bg-neutral-100 text-neutral-400 line-through opacity-60"
                                }`}
                                title={isAllowed ? `Active: ${m.nameEn}` : `Locked: ${m.nameEn}`}
                              >
                                {m.key === "tamil_horoscope"
                                  ? "Tamil PDF"
                                  : m.key === "kp_astrology"
                                  ? "KP 249"
                                  : m.key === "marriage_matching"
                                  ? "Porutham"
                                  : m.key === "panchang_muhurta"
                                  ? "Panchang"
                                  : m.key === "pdf_export"
                                  ? "PDF Export"
                                  : m.nameEn.split(" ")[0]}
                              </span>
                            );
                          })}
                        </div>
                      </td>

                      {/* Action Buttons */}
                      <td className="px-5 py-3.5 text-right">
                        <div className="inline-flex items-center gap-1.5">
                          <button
                            type="button"
                            onClick={() => openEditModal(u)}
                            className="inline-flex items-center gap-1 rounded-lg border border-[#CBD5E1] bg-white px-2.5 py-1 text-[11px] font-semibold text-[#0F172A] hover:bg-[#FAF8F5] transition"
                            title="Edit Selected Access & Plan"
                          >
                            <Edit2 className="h-3 w-3 text-amber-700" />
                            <span>Edit Access</span>
                          </button>

                          {!isAdmin && (
                            <>
                              <button
                                type="button"
                                onClick={() => handleToggleStatus(u)}
                                className={`p-1 rounded-lg border transition ${
                                  sub?.status === "suspended"
                                    ? "border-emerald-300 bg-emerald-50 text-emerald-700 hover:bg-emerald-100"
                                    : "border-amber-300 bg-amber-50 text-amber-700 hover:bg-amber-100"
                                }`}
                                title={sub?.status === "suspended" ? "Resume Account" : "Pause / Suspend Account"}
                              >
                                {sub?.status === "suspended" ? (
                                  <PlayCircle className="h-3.5 w-3.5" />
                                ) : (
                                  <PauseCircle className="h-3.5 w-3.5" />
                                )}
                              </button>

                              <button
                                type="button"
                                onClick={() => {
                                  setResetPwdUser(u);
                                  setNewPasswordInput("");
                                }}
                                className="p-1 rounded-lg border border-[#CBD5E1] bg-white text-[#64748B] hover:text-[#0F172A] hover:bg-[#FAF8F5] transition"
                                title="Reset User Password"
                              >
                                <Key className="h-3.5 w-3.5" />
                              </button>

                              <button
                                type="button"
                                onClick={() => setDeletingUser(u)}
                                className="p-1 rounded-lg border border-transparent text-[#94A3B8] hover:text-rose-600 hover:bg-rose-50 transition"
                                title="Delete Astrologer Profile"
                              >
                                <Trash2 className="h-3.5 w-3.5" />
                              </button>
                            </>
                          )}
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

      {/* CREATE MODAL */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs overflow-y-auto">
          <div className="w-full max-w-2xl rounded-2xl bg-white p-6 shadow-2xl border border-[#E2DCD5] space-y-5 my-8">
            <div className="flex items-center justify-between border-b border-[#E2DCD5] pb-4">
              <div className="flex items-center gap-2">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-500/10 text-amber-700">
                  <UserPlus className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="font-serif text-lg font-bold text-[#0F172A]">
                    {language === "ta"
                      ? "புதிய ஜோதிடர் கணக்கு உருவாக்கு"
                      : "Create Astrologer Rental Profile"}
                  </h3>
                  <p className="text-xs text-[#64748B]">
                    Enter client details, assign an access plan, and configure enabled modules.
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setIsAddModalOpen(false)}
                className="rounded-lg p-1 text-[#94A3B8] hover:bg-neutral-100 hover:text-[#0F172A]"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {formError && (
              <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs font-medium text-rose-800">
                {formError}
              </div>
            )}

            <form onSubmit={handleCreateSubmit} className="space-y-4">
              {/* Profile Credentials */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-[#334155] mb-1">
                    Astrologer / Studio Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.displayName}
                    onChange={(e) => setFormData({ ...formData, displayName: e.target.value })}
                    placeholder="e.g. Guruji Shanmugam"
                    className="w-full rounded-xl border border-[#CBD5E1] px-3 py-2 text-xs text-[#0F172A] focus:border-amber-600 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#334155] mb-1">
                    Username (Login ID) *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.username}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        username: e.target.value.toLowerCase().replace(/\s+/g, "_"),
                      })
                    }
                    placeholder="e.g. shanmugam_astro"
                    className="w-full rounded-xl border border-[#CBD5E1] px-3 py-2 text-xs font-mono text-[#0F172A] focus:border-amber-600 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#334155] mb-1">
                    Client Email Address *
                  </label>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="e.g. astrologer@example.com"
                    className="w-full rounded-xl border border-[#CBD5E1] px-3 py-2 text-xs text-[#0F172A] focus:border-amber-600 focus:outline-none"
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="text-xs font-bold text-[#334155]">Initial Password *</label>
                    <button
                      type="button"
                      onClick={generateRandomPassword}
                      className="text-[10px] font-bold text-amber-700 hover:underline cursor-pointer"
                    >
                      ⚡ Auto-Generate
                    </button>
                  </div>
                  <div className="relative">
                    <input
                      type={showPassword ? "text" : "password"}
                      required
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      placeholder="At least 8 characters"
                      className="w-full rounded-xl border border-[#CBD5E1] px-3 py-2 pr-9 text-xs text-[#0F172A] focus:border-amber-600 focus:outline-none font-mono"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-2.5 top-2.5 text-[#94A3B8] hover:text-[#0F172A]"
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
              </div>

              {/* Preset Plan Shortcuts */}
              <div className="rounded-xl border border-[#E2DCD5] bg-[#FAF8F5] p-3 space-y-2">
                <label className="block text-xs font-bold text-[#334155]">
                  1-Click Rental Plan Presets:
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  <button
                    type="button"
                    onClick={() => applyPreset("basic")}
                    className={`rounded-xl border p-2.5 text-left transition ${
                      formData.tier === "basic" && !formData.permissions.kp_astrology
                        ? "border-amber-600 bg-amber-500/10 text-amber-900"
                        : "border-[#CBD5E1] bg-white text-[#475569] hover:bg-[#FAF8F5]"
                    }`}
                  >
                    <div className="text-xs font-bold">🟡 Basic Plan (₹999/mo)</div>
                    <div className="text-[10px] text-[#64748B] mt-0.5">Vedic + Porutham + Panchang</div>
                  </button>

                  <button
                    type="button"
                    onClick={() => applyPreset("tamil_specialist")}
                    className={`rounded-xl border p-2.5 text-left transition ${
                      formData.permissions.tamil_horoscope && !formData.permissions.kp_astrology
                        ? "border-amber-600 bg-amber-500/10 text-amber-900"
                        : "border-[#CBD5E1] bg-white text-[#475569] hover:bg-[#FAF8F5]"
                    }`}
                  >
                    <div className="text-xs font-bold">🔵 Tamil Specialist (₹1,999/mo)</div>
                    <div className="text-[10px] text-[#64748B] mt-0.5">Vedic + Tamil 6-Page Booklet + CRM</div>
                  </button>

                  <button
                    type="button"
                    onClick={() => applyPreset("pro")}
                    className={`rounded-xl border p-2.5 text-left transition ${
                      formData.permissions.kp_astrology && formData.permissions.tamil_horoscope
                        ? "border-amber-600 bg-amber-500/10 text-amber-900"
                        : "border-[#CBD5E1] bg-white text-[#475569] hover:bg-[#FAF8F5]"
                    }`}
                  >
                    <div className="text-xs font-bold">🟣 Pro Studio (₹2,999/mo)</div>
                    <div className="text-[10px] text-[#64748B] mt-0.5">All 10 Modules Unlocked</div>
                  </button>
                </div>
              </div>

              {/* Validity & Quota */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-[#334155] mb-1">
                    Rental Duration / Validity
                  </label>
                  <select
                    value={formData.validityDuration}
                    onChange={(e) => setFormData({ ...formData, validityDuration: e.target.value })}
                    className="w-full rounded-xl border border-[#CBD5E1] px-3 py-2 text-xs text-[#0F172A] bg-white focus:border-amber-600 focus:outline-none"
                  >
                    <option value="30">1 Month (+30 Days)</option>
                    <option value="90">3 Months (+90 Days)</option>
                    <option value="180">6 Months (+180 Days)</option>
                    <option value="365">1 Year (+365 Days)</option>
                    <option value="unlimited">Lifetime / Indefinite</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#334155] mb-1">
                    Monthly PDF Limit
                  </label>
                  <input
                    type="number"
                    min="5"
                    max="99999"
                    value={formData.maxPdfMonthly}
                    onChange={(e) =>
                      setFormData({ ...formData, maxPdfMonthly: parseInt(e.target.value, 10) || 30 })
                    }
                    className="w-full rounded-xl border border-[#CBD5E1] px-3 py-2 text-xs text-[#0F172A] focus:border-amber-600 focus:outline-none"
                  />
                </div>
              </div>

              {/* Granular Module Checkboxes */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-xs font-bold text-[#0F172A]">
                    {language === "ta"
                      ? "தேர்ந்தெடுக்கப்பட்ட அணுகல் (Selected Module Access):"
                      : "Selected Module Access Checklist:"}
                  </label>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() =>
                        setFormData({
                          ...formData,
                          permissions: { ...PRO_PLAN_PERMISSIONS },
                        })
                      }
                      className="text-[11px] font-semibold text-amber-700 hover:underline cursor-pointer"
                    >
                      Select All
                    </button>
                    <span className="text-neutral-300">|</span>
                    <button
                      type="button"
                      onClick={() =>
                        setFormData({
                          ...formData,
                          permissions: {
                            ...Object.keys(BASIC_PLAN_PERMISSIONS).reduce((acc, k) => {
                              acc[k as PermissionKey] = false;
                              return acc;
                            }, {} as UserPermissions),
                          },
                        })
                      }
                      className="text-[11px] font-semibold text-[#64748B] hover:underline cursor-pointer"
                    >
                      Deselect All
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-56 overflow-y-auto p-1 border border-[#E2DCD5] rounded-xl bg-white">
                  {MODULE_REGISTRY.map((mod) => {
                    const isChecked = Boolean(formData.permissions[mod.key]);
                    return (
                      <label
                        key={mod.key}
                        className={`flex items-start gap-2.5 p-2 rounded-lg border cursor-pointer transition ${
                          isChecked
                            ? "border-emerald-300 bg-emerald-50/50"
                            : "border-neutral-200 bg-white hover:bg-[#FAF8F5]"
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              permissions: {
                                ...formData.permissions,
                                [mod.key]: e.target.checked,
                              },
                            })
                          }
                          className="mt-0.5 rounded text-amber-600 focus:ring-amber-500"
                        />
                        <div className="flex-1 min-w-0">
                          <div className="text-xs font-bold text-[#0F172A] truncate">
                            {language === "ta" ? mod.nameTa : mod.nameEn}
                          </div>
                          <div className="text-[10px] text-[#64748B] line-clamp-1">
                            {mod.descriptionEn}
                          </div>
                        </div>
                      </label>
                    );
                  })}
                </div>
              </div>

              {/* Form Buttons */}
              <div className="flex items-center justify-end gap-2 pt-4 border-t border-[#E2DCD5]">
                <button
                  type="button"
                  onClick={() => setIsAddModalOpen(false)}
                  disabled={formLoading}
                  className="rounded-xl border border-[#CBD5E1] bg-white px-4 py-2 text-xs font-semibold text-[#475569] hover:bg-[#FAF8F5]"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={formLoading}
                  className="rounded-xl bg-amber-600 px-5 py-2 text-xs font-bold text-white shadow-md shadow-amber-600/20 hover:bg-amber-500 disabled:opacity-50"
                >
                  {formLoading ? "Creating Profile..." : "Create & Provision Account"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* EDIT MODAL */}
      {editingUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs overflow-y-auto">
          <div className="w-full max-w-2xl rounded-2xl bg-white p-6 shadow-2xl border border-[#E2DCD5] space-y-5 my-8">
            <div className="flex items-center justify-between border-b border-[#E2DCD5] pb-4">
              <div className="flex items-center gap-2">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-500/10 text-amber-700">
                  <Edit2 className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="font-serif text-lg font-bold text-[#0F172A]">
                    Edit Selected Access & Validity: @{editingUser.username}
                  </h3>
                  <p className="text-xs text-[#64748B]">
                    Instantly enable/disable modules or adjust subscription expiration.
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setEditingUser(null)}
                className="rounded-lg p-1 text-[#94A3B8] hover:bg-neutral-100 hover:text-[#0F172A]"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {formError && (
              <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs font-medium text-rose-800">
                {formError}
              </div>
            )}

            <form onSubmit={handleEditSubmit} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-bold text-[#334155] mb-1">Display Name</label>
                  <input
                    type="text"
                    value={formData.displayName}
                    onChange={(e) => setFormData({ ...formData, displayName: e.target.value })}
                    className="w-full rounded-xl border border-[#CBD5E1] px-3 py-2 text-xs text-[#0F172A] focus:border-amber-600 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#334155] mb-1">Account Status</label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
                    className="w-full rounded-xl border border-[#CBD5E1] px-3 py-2 text-xs text-[#0F172A] bg-white focus:border-amber-600 focus:outline-none"
                  >
                    <option value="active">🟢 Active (Access Enabled)</option>
                    <option value="suspended">🟡 Suspended (Paused)</option>
                    <option value="expired">🔴 Expired</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#334155] mb-1">Plan Tier</label>
                  <select
                    value={formData.tier}
                    onChange={(e) => setFormData({ ...formData, tier: e.target.value as any })}
                    className="w-full rounded-xl border border-[#CBD5E1] px-3 py-2 text-xs text-[#0F172A] bg-white focus:border-amber-600 focus:outline-none"
                  >
                    <option value="basic">Basic Astrologer</option>
                    <option value="pro">Pro Studio</option>
                    <option value="enterprise">Enterprise / White-Label</option>
                    <option value="custom">Custom</option>
                  </select>
                </div>
              </div>

              {/* Expiry Date */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-[#334155] mb-1">
                    Subscription Valid Until (Date)
                  </label>
                  <input
                    type="date"
                    value={formData.customValidUntil}
                    onChange={(e) => setFormData({ ...formData, customValidUntil: e.target.value })}
                    className="w-full rounded-xl border border-[#CBD5E1] px-3 py-2 text-xs text-[#0F172A] focus:border-amber-600 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#334155] mb-1">
                    Monthly PDF Quota
                  </label>
                  <input
                    type="number"
                    value={formData.maxPdfMonthly}
                    onChange={(e) =>
                      setFormData({ ...formData, maxPdfMonthly: parseInt(e.target.value, 10) || 30 })
                    }
                    className="w-full rounded-xl border border-[#CBD5E1] px-3 py-2 text-xs text-[#0F172A] focus:border-amber-600 focus:outline-none"
                  />
                </div>
              </div>

              {/* Granular Module Checkboxes */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-xs font-bold text-[#0F172A]">
                    Enabled Modules for this Astrologer:
                  </label>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() =>
                        setFormData({
                          ...formData,
                          permissions: { ...PRO_PLAN_PERMISSIONS },
                        })
                      }
                      className="text-[11px] font-semibold text-amber-700 hover:underline cursor-pointer"
                    >
                      Select All
                    </button>
                    <span className="text-neutral-300">|</span>
                    <button
                      type="button"
                      onClick={() =>
                        setFormData({
                          ...formData,
                          permissions: { ...BASIC_PLAN_PERMISSIONS },
                        })
                      }
                      className="text-[11px] font-semibold text-[#64748B] hover:underline cursor-pointer"
                    >
                      Reset to Basic
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-60 overflow-y-auto p-1 border border-[#E2DCD5] rounded-xl bg-white">
                  {MODULE_REGISTRY.map((mod) => {
                    const isChecked = Boolean(formData.permissions[mod.key]);
                    return (
                      <label
                        key={mod.key}
                        className={`flex items-start gap-2.5 p-2 rounded-lg border cursor-pointer transition ${
                          isChecked
                            ? "border-emerald-300 bg-emerald-50/50"
                            : "border-neutral-200 bg-white hover:bg-[#FAF8F5]"
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              permissions: {
                                ...formData.permissions,
                                [mod.key]: e.target.checked,
                              },
                            })
                          }
                          className="mt-0.5 rounded text-amber-600 focus:ring-amber-500"
                        />
                        <div className="flex-1 min-w-0">
                          <div className="text-xs font-bold text-[#0F172A] truncate">
                            {language === "ta" ? mod.nameTa : mod.nameEn}
                          </div>
                          <div className="text-[10px] text-[#64748B] line-clamp-1">
                            {mod.descriptionEn}
                          </div>
                        </div>
                      </label>
                    );
                  })}
                </div>
              </div>

              {/* Form Buttons */}
              <div className="flex items-center justify-end gap-2 pt-4 border-t border-[#E2DCD5]">
                <button
                  type="button"
                  onClick={() => setEditingUser(null)}
                  disabled={formLoading}
                  className="rounded-xl border border-[#CBD5E1] bg-white px-4 py-2 text-xs font-semibold text-[#475569] hover:bg-[#FAF8F5]"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={formLoading}
                  className="rounded-xl bg-amber-600 px-5 py-2 text-xs font-bold text-white shadow-md shadow-amber-600/20 hover:bg-amber-500 disabled:opacity-50"
                >
                  {formLoading ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* RESET PASSWORD MODAL */}
      {resetPwdUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
          <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl border border-[#E2DCD5] space-y-4">
            <div className="flex items-center gap-2 text-amber-700">
              <Key className="h-5 w-5" />
              <h4 className="font-bold text-sm text-[#0F172A]">
                Reset Password for @{resetPwdUser.username}
              </h4>
            </div>

            <form onSubmit={handleResetPasswordSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-[#475569] mb-1">
                  New Temporary Password
                </label>
                <input
                  type="text"
                  required
                  value={newPasswordInput}
                  onChange={(e) => setNewPasswordInput(e.target.value)}
                  placeholder="Min 8 characters"
                  className="w-full rounded-xl border border-[#CBD5E1] px-3 py-2 text-xs font-mono text-[#0F172A] focus:border-amber-600 focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-[#E2DCD5]">
                <button
                  type="button"
                  onClick={() => setResetPwdUser(null)}
                  className="px-3 py-1.5 rounded-lg border border-[#CBD5E1] bg-white text-xs font-semibold text-[#475569] hover:bg-[#FAF8F5]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={newPasswordInput.length < 8 || formLoading}
                  className="px-3 py-1.5 rounded-lg bg-amber-600 text-white text-xs font-bold hover:bg-amber-500 disabled:opacity-50 shadow-xs"
                >
                  Update Password
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* DELETE MODAL */}
      {deletingUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
          <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl border border-[#E2DCD5] space-y-4">
            <div className="flex items-center gap-2 text-rose-600">
              <AlertTriangle className="h-5 w-5 shrink-0" />
              <h4 className="font-bold text-sm text-[#0F172A]">Delete Astrologer Profile?</h4>
            </div>
            <p className="text-xs text-[#64748B] leading-relaxed">
              Are you sure you want to permanently delete the profile for{" "}
              <strong>@{deletingUser.username}</strong> ({deletingUser.display_name})? Their login
              and access will be immediately terminated.
            </p>
            <div className="flex items-center justify-end gap-2 pt-2 border-t border-[#E2DCD5]">
              <button
                type="button"
                onClick={() => setDeletingUser(null)}
                className="px-3 py-1.5 rounded-lg border border-[#CBD5E1] bg-white text-xs font-semibold text-[#475569] hover:bg-[#FAF8F5]"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleDeleteSubmit}
                disabled={formLoading}
                className="px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold shadow-xs disabled:opacity-50"
              >
                {formLoading ? "Deleting..." : "Confirm Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
