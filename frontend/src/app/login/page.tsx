"use client";

import React, { useState, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import {
  Compass,
  Lock,
  User,
  Eye,
  EyeOff,
  AlertCircle,
  Info,
  Loader2,
  ArrowRight,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectParam = searchParams.get("redirect");
  const isExpired =
    searchParams.get("expired") === "true" ||
    searchParams.get("error") === "session_expired";
  const isUnauthorized = searchParams.get("error") === "unauthorized";

  const { language, t } = useLanguage();
  const { refreshUser } = useAuth();

  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isLoading) return;

    if (!identifier.trim() || !password) {
      setErrorMessage(
        language === "ta"
          ? "பயனர் பெயர் மற்றும் கடவுச்சொல்லை உள்ளிடவும்."
          : "Please enter both username and password."
      );
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ identifier: identifier.trim(), password }),
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 401) {
          setErrorMessage(
            language === "ta"
              ? "தவறான பயனர் பெயர் அல்லது கடவுச்சொல். தயவுசெய்து சரிபார்க்கவும்."
              : "Invalid username or password. Please verify your credentials."
          );
        } else if (response.status >= 500) {
          setErrorMessage(
            data.error ||
              (language === "ta"
                ? "சேவையகத்துடன் இணைக்க முடியவில்லை. தயவுசெய்து சிறிது நேரம் கழித்து முயற்சிக்கவும்."
                : "Unable to connect to authentication server. Please check your connection.")
          );
        } else {
          setErrorMessage(
            data.error ||
              (language === "ta"
                ? "தவறான பயனர் பெயர் அல்லது கடவுச்சொல்."
                : "Invalid username or password.")
          );
        }
        setIsLoading(false);
        return;
      }

      // Successful login - refresh auth context and redirect to target or dashboard
      await refreshUser();
      const target =
        redirectParam && !redirectParam.startsWith("/login")
          ? redirectParam
          : data.redirect || "/dashboard";
      router.push(target);
      router.refresh();
    } catch {
      setErrorMessage(
        language === "ta"
          ? "நெட்வொர்க் பிழை ஏற்பட்டது. இணைய இணைப்பை சரிபார்க்கவும்."
          : "Network connection error. Please verify your network and try again."
      );
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto">
      {/* Brand Header */}
      <div className="text-center mb-8">
        <div className="relative inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-[#B8860B] via-[#996515] to-[#593E10] text-white shadow-lg border border-[#D8BD80] mb-4">
          <Compass className="w-8 h-8" />
          <Sparkles className="w-4 h-4 text-amber-200 absolute -top-1 -right-1" />
        </div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#FAF2DE] border border-[#D8BD80] text-[11px] font-semibold text-[#8C6D23] mb-3 shadow-2xs">
          <span>
            {language === "ta"
              ? "துல்லிய வேத & கே.பி வானியல் தளம்"
              : "Precision Vedic & KP Astronomical System"}
          </span>
        </div>
        <h1 className="font-serif text-2xl sm:text-3xl font-bold text-[#0F172A] tracking-tight">
          {t.brandName}
        </h1>
        <p className="mt-2 text-xs sm:text-sm text-[#475569] leading-relaxed">
          {language === "ta"
            ? "பாதுகாப்பான உள்நுழைவு போர்ட்டல் • உங்கள் கணக்கில் உள்நுழையவும்"
            : "Secure Access Gateway • Sign in to access the portal"}
        </p>
      </div>

      {/* Main Authentication Box */}
      <div className="rounded-2xl border border-[#E2DCD5] bg-white p-6 sm:p-8 shadow-sm">
        {/* Session Expired Notice */}
        {isExpired && !errorMessage && (
          <div className="mb-6 flex items-start gap-3 p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs sm:text-sm">
            <Info className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div className="flex-1 font-medium">
              {language === "ta"
                ? "உங்கள் அமர்வு காலாவதியானது. தொடர மீண்டும் உள்நுழையவும்."
                : "Your session has expired. Please log in again to continue."}
            </div>
          </div>
        )}

        {/* Unauthorized Route Notice */}
        {isUnauthorized && !errorMessage && (
          <div className="mb-6 flex items-start gap-3 p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs sm:text-sm">
            <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div className="flex-1 font-medium">
              {language === "ta"
                ? "அணுகல் கட்டுப்படுத்தப்பட்டது. நிர்வாகி அனுமதி தேவை."
                : "Access restricted. Administrative privileges are required."}
            </div>
          </div>
        )}

        {/* Error Alert Box */}
        {errorMessage && (
          <div className="mb-6 flex items-start gap-3 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs sm:text-sm animate-fadeIn">
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
            <div className="flex-1 font-medium">{errorMessage}</div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Username Input */}
          <div>
            <label
              htmlFor="login-username"
              className="block text-xs font-bold text-[#0F172A] mb-1.5 uppercase tracking-wider"
            >
              {language === "ta" ? "பயனர் பெயர்" : "Username"}
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[#94A3B8]">
                <User className="w-4 h-4" />
              </div>
              <input
                id="login-username"
                type="text"
                autoComplete="username"
                required
                disabled={isLoading}
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder={
                  language === "ta"
                    ? "பயனர் பெயரை உள்ளிடவும் (எ.கா. Gokul Murugan)"
                    : "Enter your username (e.g. Gokul Murugan)"
                }
                className="w-full pl-10 pr-3.5 py-2.5 rounded-xl border border-[#CBD5E1] bg-[#FAF8F5] text-sm text-[#0F172A] placeholder-[#94A3B8] focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#B8860B] focus:border-[#B8860B] transition-all disabled:opacity-50"
              />
            </div>
          </div>

          {/* Password Input with Show/Hide */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label
                htmlFor="login-password"
                className="block text-xs font-bold text-[#0F172A] uppercase tracking-wider"
              >
                {t.fieldPassword}
              </label>
              <Link
                href="/forgot-password"
                className="text-xs text-[#B8860B] hover:text-[#784E0E] font-medium transition-colors"
              >
                {t.forgotPasswordLink}
              </Link>
            </div>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[#94A3B8]">
                <Lock className="w-4 h-4" />
              </div>
              <input
                id="login-password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
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
                aria-label={showPassword ? t.hidePassword : t.showPassword}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-[#94A3B8] hover:text-[#0F172A] transition-colors cursor-pointer"
              >
                {showPassword ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>

          {/* Sign In Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-bold text-sm text-white bg-[#0F172A] hover:bg-[#1E293B] shadow-md transition-all disabled:opacity-60 disabled:cursor-not-allowed group cursor-pointer focus:outline-none focus:ring-2 focus:ring-[#B8860B]"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-[#D8BD80]" />
                <span>{t.signingIn}</span>
              </>
            ) : (
              <>
                <span>{t.signInButton}</span>
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
              </>
            )}
          </button>
        </form>

        {/* Register Navigation Link */}
        <div className="mt-6 pt-6 border-t border-[#E2DCD5] text-center text-xs sm:text-sm text-[#64748B]">
          <span>{t.dontHaveAccount} </span>
          <Link
            href="/register"
            className="font-bold text-[#B8860B] hover:text-[#784E0E] underline underline-offset-2 transition-colors"
          >
            {t.registerLink}
          </Link>
        </div>
      </div>

      {/* Security Assurance Tag */}
      <div className="mt-6 text-center flex items-center justify-center gap-2 text-xs text-[#64748B]">
        <ShieldCheck className="w-4 h-4 text-[#B8860B]" />
        <span>
          {language === "ta"
            ? "சுபபேஸ் அத்தண்டிகேஷன் மற்றும் வரிசை-நிலை பாதுகாப்பு (RLS)"
            : "Protected by Supabase Auth and Row-Level Security (RLS)"}
        </span>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <div className="min-h-[calc(100vh-14rem)] flex items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
      <Suspense
        fallback={
          <div className="flex items-center justify-center p-12">
            <Loader2 className="w-8 h-8 animate-spin text-[#B8860B]" />
          </div>
        }
      >
        <LoginForm />
      </Suspense>
    </div>
  );
}
