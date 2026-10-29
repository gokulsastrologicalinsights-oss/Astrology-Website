"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { SavedHoroscopesList } from "@/components/saved/SavedHoroscopesList";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { Plus } from "lucide-react";

export default function SavedHoroscopesPage() {
  const router = useRouter();
  const { language, t } = useLanguage();
  const { user, isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !user)) {
      router.replace("/login");
    }
  }, [isAuthenticated, user, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-[calc(100vh-14rem)] flex items-center justify-center bg-[#F2F3F5]">
        <div className="w-8 h-8 border-4 border-[#153F6B] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  return (
    <div className="w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 sm:py-8 space-y-6">
      {/* Breadcrumbs matching Screenshot 2 */}
      <Breadcrumbs
        items={[
          {
            label: language === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools",
            href: "/tools",
          },
          {
            label: language === "ta" ? "ஜாதகம் (வேத & கே.பி)" : "Horoscope (Vedic & KP)",
          },
        ]}
      />

      {/* Page Header: ஜாதகம் + [+ ஜாதகம் உருவாக்கு] matching Screenshot 2 */}
      <div className="flex items-center justify-between gap-4 pb-4 border-b border-[#D9DEE7]">
        <h1 className="text-xl sm:text-2xl font-bold text-[#183047] font-tamil">
          {language === "ta" ? "ஜாதகம்" : "Horoscopes"}
        </h1>

        <Link
          href="/horoscope"
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white bg-[#153F6B] hover:bg-[#0F3155] shadow-xs transition-colors"
        >
          <Plus className="w-4 h-4 text-white" />
          <span>{language === "ta" ? "ஜாதகம் உருவாக்கு" : "Create Horoscope"}</span>
        </Link>
      </div>

      {/* Main Content: Saved Horoscopes List (Banner, Toolbar, 3-Col Cards) */}
      <SavedHoroscopesList pageSize={12} showHeader={false} showBanner={true} />
    </div>
  );
}
