"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import {
  Compass,
  Lock,
  Eye,
  EyeOff,
  AlertCircle,
  CheckCircle2,
  Loader2,
  ArrowRight,
  ShieldAlert,
} from "lucide-react";

export default function UpdatePasswordPage() {
  const router = useRouter();
  const { language, t } = useLanguage();
  const { user, mustChangePassword, refreshUser } = useAuth();

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setSuccessMessage(null);

    if (password !== confirmPassword) {
      setErrorMessage(t.passwordMismatch);
      return;
    }

    if (password.length < 8) {
      setErrorMessage(t.passwordRequirements);
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch("/api/auth/update-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });

      const data = await response.json();

      if (!response.ok) {
        setErrorMessage(data.error || "Failed to update password.");
        setIsLoading(false);
        return;
      }

      setSuccessMessage(data.message || t.passwordUpdatedSuccess);
      await refreshUser();
      setIsLoading(false);

      setTimeout(() => {
        router.push(data.redirect || (user?.role === "admin" ? "/admin" : "/dashboard"));
        router.refresh();
      }, 1500);
    } catch {
      setErrorMessage(t.connectionError);
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-16rem)] flex items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-[#B8860B] to-[#784E0E] text-white shadow-md border border-[#D8BD80] mb-4">
            <Compass className="w-7 h-7" />
          </div>
          <h1 className="font-serif text-2xl sm:text-3xl font-bold text-[#0F172A] tracking-tight">
            {t.updatePasswordTitle}
          </h1>
          <p className="mt-2 text-xs sm:text-sm text-[#475569] leading-relaxed">
            {t.updatePasswordSubtitle}
          </p>
        </div>

        {/* First-login requirement banner if mustChangePassword */}
        {mustChangePassword && (
          <div className="mb-6 flex items-start gap-3 p-4 rounded-xl bg-amber-50 border border-amber-300 text-amber-900 text-xs sm:text-sm">
            <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div className="flex-1 font-medium leading-relaxed">
              {t.firstLoginNotice}
            </div>
          </div>
        )}

        {/* Form Container */}
        <div className="rounded-2xl border border-[#E2DCD5] bg-white p-6 sm:p-8 shadow-sm">
          {errorMessage && (
            <div className="mb-6 flex items-start gap-3 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs sm:text-sm">
              <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
              <div className="flex-1 font-medium">{errorMessage}</div>
            </div>
          )}

          {successMessage && (
            <div className="mb-6 flex items-start gap-3 p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs sm:text-sm">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
              <div className="flex-1 font-medium">{successMessage}</div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-[#0F172A] mb-1.5 uppercase tracking-wider">
                {t.fieldNewPassword}
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[#94A3B8]">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  disabled={isLoading}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={t.fieldPasswordPlaceholder}
                  className="w-full pl-10 pr-10 py-2.5 rounded-xl border border-[#CBD5E1] bg-[#FAF8F5] text-sm text-[#0F172A] placeholder-[#94A3B8] focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#B8860B] focus:border-[#B8860B] transition-all disabled:opacity-50"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={isLoading}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-[#94A3B8] hover:text-[#0F172A] transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              <p className="mt-1 text-[11px] text-[#64748B]">
                {t.passwordRequirements}
              </p>
            </div>

            <div>
              <label className="block text-xs font-bold text-[#0F172A] mb-1.5 uppercase tracking-wider">
                {t.fieldConfirmPassword}
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[#94A3B8]">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  disabled={isLoading}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder={t.fieldConfirmPasswordPlaceholder}
                  className="w-full pl-10 pr-3.5 py-2.5 rounded-xl border border-[#CBD5E1] bg-[#FAF8F5] text-sm text-[#0F172A] placeholder-[#94A3B8] focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#B8860B] focus:border-[#B8860B] transition-all disabled:opacity-50"
                />
              </div>
            </div>

            <div className="pt-2">
              <button
                type="submit"
                disabled={isLoading}
                className="w-full inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-bold text-sm text-white bg-[#0F172A] hover:bg-[#1E293B] shadow-md transition-all disabled:opacity-60 disabled:cursor-not-allowed group cursor-pointer"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin text-[#D8BD80]" />
                    <span>{t.updatingPassword}</span>
                  </>
                ) : (
                  <>
                    <span>{t.updatePasswordButton}</span>
                    <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
