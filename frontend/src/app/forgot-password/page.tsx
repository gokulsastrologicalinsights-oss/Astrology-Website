"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import {
  Compass,
  Mail,
  AlertCircle,
  CheckCircle2,
  Loader2,
  ArrowLeft,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";

export default function ForgotPasswordPage() {
  const { language, t } = useLanguage();
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;

    setIsLoading(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const response = await fetch("/api/auth/reset-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim() }),
      });

      const data = await response.json();

      if (!response.ok) {
        setErrorMessage(data.error || "Failed to submit request.");
        setIsLoading(false);
        return;
      }

      setSuccessMessage(data.message || t.resetLinkSent);
      setIsLoading(false);
    } catch {
      setErrorMessage(t.connectionError);
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-16rem)] flex items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md mx-auto">
        {/* Brand Card Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-[#B8860B] to-[#784E0E] text-white shadow-md border border-[#D8BD80] mb-4">
            <Compass className="w-7 h-7" />
          </div>
          <h1 className="font-serif text-2xl sm:text-3xl font-bold text-[#0F172A] tracking-tight">
            {t.forgotPasswordTitle}
          </h1>
          <p className="mt-2 text-xs sm:text-sm text-[#475569] leading-relaxed">
            {t.forgotPasswordSubtitle}
          </p>
        </div>

        {/* Form Container */}
        <div className="rounded-2xl border border-[#E2DCD5] bg-white p-6 sm:p-8 shadow-sm">
          {errorMessage && (
            <div className="mb-6 flex items-start gap-3 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs sm:text-sm">
              <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
              <div className="flex-1 font-medium">{errorMessage}</div>
            </div>
          )}

          {successMessage ? (
            <div className="space-y-4">
              <div className="flex items-start gap-3 p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs sm:text-sm">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                <div className="flex-1 font-medium leading-relaxed">
                  {successMessage}
                </div>
              </div>
              <Link
                href="/login"
                className="w-full inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-bold text-sm text-white bg-[#0F172A] hover:bg-[#1E293B] shadow-md transition-all"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>{t.backToLogin}</span>
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-[#0F172A] mb-1.5 uppercase tracking-wider">
                  {t.fieldEmail}
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[#94A3B8]">
                    <Mail className="w-4 h-4" />
                  </div>
                  <input
                    type="email"
                    required
                    disabled={isLoading}
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder={t.fieldEmailPlaceholder}
                    className="w-full pl-10 pr-3.5 py-2.5 rounded-xl border border-[#CBD5E1] bg-[#FAF8F5] text-sm text-[#0F172A] placeholder-[#94A3B8] focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#B8860B] focus:border-[#B8860B] transition-all disabled:opacity-50"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-bold text-sm text-white bg-[#0F172A] hover:bg-[#1E293B] shadow-md transition-all disabled:opacity-60 disabled:cursor-not-allowed group cursor-pointer"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin text-[#D8BD80]" />
                    <span>{t.sendingResetLink}</span>
                  </>
                ) : (
                  <>
                    <span>{t.sendResetLink}</span>
                    <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                  </>
                )}
              </button>

              <div className="pt-4 border-t border-[#E2DCD5] text-center">
                <Link
                  href="/login"
                  className="inline-flex items-center gap-1.5 text-xs font-bold text-[#B8860B] hover:text-[#784E0E] transition-colors"
                >
                  <ArrowLeft className="w-3.5 h-3.5" />
                  <span>{t.backToLogin}</span>
                </Link>
              </div>
            </form>
          )}
        </div>

        {/* Security Notice */}
        <div className="mt-6 text-center flex items-center justify-center gap-2 text-xs text-[#64748B]">
          <ShieldCheck className="w-4 h-4 text-[#B8860B]" />
          <span>
            {language === "ta"
              ? "பாதுகாப்பான கடவுச்சொல் மீட்பு அமைப்பு"
              : "Secure cryptographic password recovery via Supabase"}
          </span>
        </div>
      </div>
    </div>
  );
}
