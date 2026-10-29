"use client";

import React from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { useLanguage } from "@/lib/i18n";
import { PermissionKey, MODULE_REGISTRY } from "@/lib/permissions";
import { Lock, ShieldAlert, ArrowLeft, Mail, AlertTriangle, Sparkles } from "lucide-react";

interface FeatureGuardProps {
  permission: PermissionKey;
  moduleName?: string;
  children: React.ReactNode;
}

export function FeatureGuard({ permission, moduleName, children }: FeatureGuardProps) {
  const { user, role, isLoading, hasPermission, isSubscriptionActive } = useAuth();
  const { language } = useLanguage();

  if (isLoading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-amber-600 border-t-transparent" />
      </div>
    );
  }

  // Admin always has full access
  if (role === "admin") {
    return <>{children}</>;
  }

  const moduleDef = MODULE_REGISTRY.find((m) => m.key === permission);
  const title =
    moduleName ||
    (language === "ta" ? moduleDef?.nameTa : moduleDef?.nameEn) ||
    permission;

  // 1. Subscription Expired or Suspended
  if (!isSubscriptionActive) {
    const isSuspended = user?.subscription?.status === "suspended";
    return (
      <div className="mx-auto my-12 max-w-2xl px-4">
        <div className="rounded-2xl border border-red-500/30 bg-gradient-to-b from-red-950/20 to-neutral-900/40 p-8 text-center shadow-2xl backdrop-blur-md">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-500/10 text-red-400 ring-8 ring-red-500/5">
            <AlertTriangle className="h-8 w-8" />
          </div>

          <h2 className="mb-2 text-2xl font-bold text-neutral-100">
            {isSuspended
              ? language === "ta"
                ? "கணக்கு தற்காலிகமாக முடக்கப்பட்டுள்ளது"
                : "Account Temporarily Suspended"
              : language === "ta"
              ? "சந்தா காலம் முடிவடைந்தது"
              : "Subscription Expired"}
          </h2>

          <p className="mb-6 text-sm leading-relaxed text-neutral-300">
            {isSuspended
              ? language === "ta"
                ? "உங்கள் கணக்கு நிர்வாகியால் தற்காலிகமாக இடைநிறுத்தப்பட்டுள்ளது. மீண்டும் செயல்படுத்த அட்மினைத் தொடர்பு கொள்ளவும்."
                : "Your account access has been paused by the system administrator. Please reach out to reactivate your subscription."
              : language === "ta"
              ? `உங்கள் மாதாந்திர/வருடாந்திர சந்தா காலம் முடிவடைந்துவிட்டது (${
                  user?.subscription?.validUntil
                    ? new Date(user.subscription.validUntil).toLocaleDateString()
                    : ""
                }). இந்த மென்பொருளைத் தொடர்ந்து பயன்படுத்த உங்கள் சந்தாவைப் புதுப்பிக்கவும்.`
              : `Your active access plan expired on ${
                  user?.subscription?.validUntil
                    ? new Date(user.subscription.validUntil).toLocaleDateString()
                    : "the scheduled date"
                }. Please renew your rental subscription with the administrator to restore full uninterrupted access.`}
          </p>

          <div className="flex flex-wrap items-center justify-center gap-3">
            <Link
              href="/"
              className="inline-flex items-center gap-2 rounded-xl border border-neutral-700 bg-neutral-800/80 px-4 py-2.5 text-sm font-medium text-neutral-200 transition hover:bg-neutral-700"
            >
              <ArrowLeft className="h-4 w-4" />
              {language === "ta" ? "முகப்புக்குச் செல்க" : "Return to Home"}
            </Link>

            <a
              href="mailto:admin@gokul-astrology.local?subject=Subscription%20Renewal%20Request"
              className="inline-flex items-center gap-2 rounded-xl bg-amber-600 px-5 py-2.5 text-sm font-semibold text-neutral-950 transition hover:bg-amber-500 shadow-lg shadow-amber-600/20"
            >
              <Mail className="h-4 w-4" />
              {language === "ta" ? "நிர்வாகியைத் தொடர்பு கொள்ள" : "Contact Administrator"}
            </a>
          </div>
        </div>
      </div>
    );
  }

  // 2. Specific Module Locked
  if (!hasPermission(permission)) {
    return (
      <div className="mx-auto my-12 max-w-2xl px-4">
        <div className="rounded-2xl border border-amber-500/30 bg-gradient-to-b from-amber-950/20 via-neutral-900/60 to-neutral-900/40 p-8 text-center shadow-2xl backdrop-blur-md">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-amber-500/10 text-amber-400 ring-8 ring-amber-500/5">
            <Lock className="h-8 w-8" />
          </div>

          <div className="mb-2 inline-flex items-center gap-1.5 rounded-full border border-amber-500/20 bg-amber-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-amber-400">
            <Sparkles className="h-3 w-3" />
            {language === "ta" ? "தேர்ந்தெடுக்கப்பட்ட அனுமதி தேவை" : "Plan Upgrade Required"}
          </div>

          <h2 className="mb-2 text-2xl font-bold text-neutral-100">{title}</h2>

          <p className="mb-6 text-sm leading-relaxed text-neutral-300">
            {language === "ta"
              ? `இந்த "${title}" அம்சம் உங்கள் தற்போதைய சந்தா திட்டத்தில் (${
                  user?.subscription?.tier?.toUpperCase() || "BASIC"
                }) சேர்க்கப்படவில்லை. இந்த வசதியை உங்கள் கணக்கில் திறந்துவிட (Enable) நிர்வாகியைத் தொடர்பு கொள்ளவும்.`
              : `The module "${title}" is not unlocked in your current subscription tier (${
                  user?.subscription?.tier?.toUpperCase() || "BASIC"
                }). To enable this high-precision engine for your practice, contact your platform administrator.`}
          </p>

          <div className="mb-6 rounded-xl border border-neutral-800 bg-neutral-950/50 p-4 text-left">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-neutral-400">
              {language === "ta" ? "இந்த அம்சத்தில் கிடைக்கும் வசதிகள்:" : "Included with this module:"}
            </h4>
            <p className="mt-1 text-xs text-neutral-300">
              {language === "ta" ? moduleDef?.descriptionTa : moduleDef?.descriptionEn}
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3">
            <Link
              href="/"
              className="inline-flex items-center gap-2 rounded-xl border border-neutral-700 bg-neutral-800/80 px-4 py-2.5 text-sm font-medium text-neutral-200 transition hover:bg-neutral-700"
            >
              <ArrowLeft className="h-4 w-4" />
              {language === "ta" ? "முகப்புக்குச் செல்க" : "Return to Home"}
            </Link>

            <a
              href={`mailto:admin@gokul-astrology.local?subject=Access%20Request%20for%20${encodeURIComponent(
                title
              )}`}
              className="inline-flex items-center gap-2 rounded-xl bg-amber-600 px-5 py-2.5 text-sm font-semibold text-neutral-950 transition hover:bg-amber-500 shadow-lg shadow-amber-600/20"
            >
              <ShieldAlert className="h-4 w-4" />
              {language === "ta" ? "அனுமதி கோரிக்கை விடுக்க" : "Request Module Unlock"}
            </a>
          </div>
        </div>
      </div>
    );
  }

  // Access Granted!
  return <>{children}</>;
}
