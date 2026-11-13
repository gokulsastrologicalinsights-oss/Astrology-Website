"use client";

import React, { useState, Suspense } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter, useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import {
  Lock,
  User,
  Eye,
  EyeOff,
  AlertCircle,
  Info,
  Loader2,
  Globe,
  Home,
  HelpCircle,
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

  const { language, toggleLanguage, t } = useLanguage();
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
    <div className="w-full min-h-screen flex flex-col lg:flex-row bg-[#08182B]">
      {/* =========================================
          LEFT SIDE: BRANDING & RESIZED CENTER LOGO
          ========================================= */}
      <div className="w-full lg:w-1/2 min-h-[440px] lg:min-h-screen bg-gradient-to-b from-[#08182B] via-[#0B213A] to-[#061220] flex flex-col items-center justify-center p-8 sm:p-12 lg:p-16 relative overflow-hidden select-none border-b lg:border-b-0 lg:border-r border-[#1B3554]/50">
        {/* Subtle background celestial glows & stars */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_45%,rgba(216,189,128,0.12),transparent_70%)] pointer-events-none" />
        <div className="absolute top-12 left-12 w-2 h-2 rounded-full bg-amber-300/40 animate-pulse pointer-events-none" />
        <div className="absolute top-1/4 right-16 w-1.5 h-1.5 rounded-full bg-blue-300/40 pointer-events-none" />
        <div className="absolute bottom-20 left-20 w-2 h-2 rounded-full bg-amber-200/30 pointer-events-none" />

        {/* Content Container */}
        <div className="relative z-10 flex flex-col items-center text-center max-w-lg my-auto">
          {/* Main Brand Title */}
          <h1 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-bold text-white tracking-tight leading-tight">
            {language === "ta" ? "கோகுலின் ஜோதிட நுண்ணறிவுகள்" : "Gokul's Astrological Insights"}
          </h1>

          {/* Golden Divider Accent Line */}
          <div className="w-16 sm:w-20 h-1 bg-[#D4AF37] rounded-full my-3.5 shadow-[0_0_12px_rgba(212,175,55,0.6)]" />

          {/* Subtitle */}
          <p className="text-xs sm:text-sm lg:text-base text-slate-300 font-light tracking-wide max-w-md">
            {language === "ta"
              ? "துல்லியமான AI வேத & கே.பி ஜோதிடக் கணிப்புகள்"
              : "Instant, AI Powered Vedic Astrology Predictions"}
          </p>

          {/* Resized Centered Logo with Astrology Artwork Frame */}
          <div className="mt-8 sm:mt-12 relative flex items-center justify-center">
            {/* Outer Subtle Orbit / Glow Rings */}
            <div className="absolute -inset-6 rounded-full border border-amber-400/15 animate-[spin_60s_linear_infinite] pointer-events-none hidden sm:block" />
            <div className="absolute -inset-12 rounded-full border border-amber-300/10 pointer-events-none hidden sm:block" />

            {/* Astrology Sun Accent on Top */}
            <div className="absolute -top-7 z-20 flex items-center justify-center w-11 h-11 rounded-full bg-gradient-to-tr from-amber-500 to-yellow-300 shadow-[0_0_20px_rgba(245,158,11,0.6)] text-amber-950 border border-amber-200">
              <Sparkles className="w-5 h-5 text-amber-950" />
            </div>

            {/* Centered Logo Container */}
            <div className="relative w-56 h-56 sm:w-64 sm:h-64 lg:w-72 lg:h-72 rounded-full p-2.5 bg-gradient-to-b from-[#183556] to-[#0A1A2E] border-2 border-amber-400/50 shadow-[0_0_40px_rgba(212,175,55,0.25)] flex items-center justify-center overflow-hidden group hover:scale-[1.02] transition-transform duration-500">
              <div className="relative w-full h-full rounded-full overflow-hidden bg-[#071322]">
                <Image
                  src="/logo.png"
                  alt="Gokul's Astrological Insights Logo"
                  fill
                  priority
                  sizes="(max-width: 640px) 224px, (max-width: 1024px) 256px, 288px"
                  className="object-contain p-2"
                />
              </div>
            </div>

            {/* Zodiac Constellation Emblems (Visual touch matching reference artwork) */}
            <div className="absolute -left-6 bottom-8 hidden sm:flex items-center justify-center px-3 py-1 rounded-full bg-[#0C243F]/90 border border-amber-400/30 text-amber-300 text-[11px] font-medium shadow-md backdrop-blur-xs">
              ♌ Leo
            </div>
            <div className="absolute -right-6 bottom-8 hidden sm:flex items-center justify-center px-3 py-1 rounded-full bg-[#0C243F]/90 border border-amber-400/30 text-amber-300 text-[11px] font-medium shadow-md backdrop-blur-xs">
              ♏ Scorpio
            </div>
          </div>
        </div>
      </div>

      {/* =========================================
          RIGHT SIDE: LOGIN DETAILS FORM CARD
          ========================================= */}
      <div className="w-full lg:w-1/2 min-h-screen bg-[#F8FAFC] flex flex-col justify-between p-6 sm:p-10 lg:p-14 relative">
        {/* Top bar with language switcher */}
        <div className="w-full flex justify-end mb-4">
          <button
            type="button"
            onClick={toggleLanguage}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold text-slate-600 bg-white border border-slate-200 hover:bg-slate-50 hover:text-slate-900 shadow-2xs transition-colors cursor-pointer"
            aria-label="Toggle language"
          >
            <Globe className="w-3.5 h-3.5 text-amber-600" />
            <span>{language === "ta" ? "English" : "தமிழ்"}</span>
          </button>
        </div>

        {/* Center: Floating Login Card */}
        <div className="w-full max-w-[400px] mx-auto my-auto">
          <div className="bg-white rounded-2xl sm:rounded-3xl border border-slate-200/80 shadow-[0_15px_40px_rgba(15,23,42,0.06)] p-7 sm:p-9">
            {/* Card Header: Mini Logo + Brand */}
            <div className="flex items-center justify-center gap-2.5 mb-7">
              <div className="relative w-8 h-8 rounded-full overflow-hidden border border-amber-400/60 shadow-xs bg-[#090d2e] shrink-0">
                <Image
                  src="/logo.png"
                  alt="Logo"
                  width={32}
                  height={32}
                  className="w-full h-full object-cover"
                />
              </div>
              <span className="font-serif text-lg font-bold text-[#0D2238] tracking-tight">
                {language === "ta" ? "கோகுல் ஜோதிடம்" : "VedicSage.ai"}
              </span>
            </div>

            {/* Session Expired Notice */}
            {isExpired && !errorMessage && (
              <div className="mb-5 flex items-start gap-2.5 p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs">
                <Info className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                <div className="flex-1 font-medium">
                  {language === "ta"
                    ? "உங்கள் அமர்வு காலாவதியானது. தொடர மீண்டும் உள்நுழையவும்."
                    : "Your session has expired. Please log in again to continue."}
                </div>
              </div>
            )}

            {/* Unauthorized Notice */}
            {isUnauthorized && !errorMessage && (
              <div className="mb-5 flex items-start gap-2.5 p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs">
                <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                <div className="flex-1 font-medium">
                  {language === "ta"
                    ? "அணுகல் கட்டுப்படுத்தப்பட்டது. நிர்வாகி அனுமதி தேவை."
                    : "Access restricted. Administrative privileges are required."}
                </div>
              </div>
            )}

            {/* Error Message Notice */}
            {errorMessage && (
              <div className="mb-5 flex items-start gap-2.5 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs animate-fadeIn">
                <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                <div className="flex-1 font-medium">{errorMessage}</div>
              </div>
            )}

            {/* The Login Form */}
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Field 1: Mobile Number ( Username ) */}
              <div>
                <label
                  htmlFor="login-username"
                  className="block text-xs font-semibold text-slate-700 mb-1.5"
                >
                  {language === "ta"
                    ? "கைபேசி எண் ( பயனர் பெயர் )"
                    : "Mobile Number ( Username )"}
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
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
                        ? "பயனர் பெயரை உள்ளிடவும்"
                        : "Enter your username"
                    }
                    className="w-full pl-10 pr-3.5 py-2.5 rounded-xl border border-slate-300 bg-white text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0D2238]/10 focus:border-[#0D2238] transition-all disabled:opacity-50"
                  />
                </div>
              </div>

              {/* Field 2: Password */}
              <div>
                <label
                  htmlFor="login-password"
                  className="block text-xs font-semibold text-slate-700 mb-1.5"
                >
                  {language === "ta" ? "கடவுச்சொல்" : "Password"}
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
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
                    placeholder={
                      language === "ta"
                        ? "கடவுச்சொல்லை உள்ளிடவும்"
                        : "Enter your password"
                    }
                    className="w-full pl-10 pr-10 py-2.5 rounded-xl border border-slate-300 bg-white text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0D2238]/10 focus:border-[#0D2238] transition-all disabled:opacity-50"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    disabled={isLoading}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-700 transition-colors cursor-pointer"
                  >
                    {showPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Login Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full inline-flex items-center justify-center gap-2 py-3 px-6 rounded-xl font-bold text-xs tracking-wider uppercase text-white bg-[#0D2238] hover:bg-[#153354] active:scale-[0.99] shadow-md transition-all disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer focus:outline-none focus:ring-2 focus:ring-[#0D2238]/20"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin text-amber-300" />
                    <span>{language === "ta" ? "உள்நுழைகிறது..." : "LOGGING IN..."}</span>
                  </>
                ) : (
                  <span>{language === "ta" ? "உள்நுழைக" : "LOGIN"}</span>
                )}
              </button>
            </form>

            {/* Sign Up Navigation Link */}
            <div className="mt-6 text-center text-xs text-slate-500">
              <span>{language === "ta" ? "புதியவரா? " : "New here? "}</span>
              <Link
                href="/register"
                className="font-medium text-[#0D2238] hover:underline transition-colors"
              >
                {language === "ta" ? "இலவச கணக்கை உருவாக்குங்கள்" : "Create free account"}
              </Link>
            </div>
          </div>

          {/* Footer Sub-Links below the card */}
          <div className="mt-6 flex items-center justify-between text-xs text-slate-500 px-2">
            <Link
              href="/forgot-password"
              className="inline-flex items-center gap-1 hover:text-[#0D2238] transition-colors"
            >
              <HelpCircle className="w-3.5 h-3.5 text-slate-400" />
              <span>{language === "ta" ? "கடவுச்சொல் மறந்துவிட்டதா?" : "Forgot Password?"}</span>
            </Link>

            <Link
              href="/"
              className="inline-flex items-center gap-1 hover:text-[#0D2238] transition-colors"
            >
              <Home className="w-3.5 h-3.5 text-slate-400" />
              <span>{language === "ta" ? "முகப்புக்கு செல்க" : "Continue to homepage"}</span>
            </Link>
          </div>
        </div>

        {/* Bottom copyright / security tag */}
        <div className="w-full text-center text-[11px] text-slate-400 mt-6">
          © {new Date().getFullYear()} {t.brandName}. All rights reserved.
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-[#08182B]">
          <Loader2 className="w-8 h-8 animate-spin text-amber-400" />
        </div>
      }
    >
      <LoginForm />
    </Suspense>
  );
}
