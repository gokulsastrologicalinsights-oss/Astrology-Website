"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { SavedHoroscopesList } from "@/components/saved/SavedHoroscopesList";
import { Plus } from "lucide-react";

function HoroscopeToolsContent() {
  const router = useRouter();
  const { language } = useLanguage();
  const { user, isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !user)) {
      router.replace("/login");
    }
  }, [isAuthenticated, user, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-[calc(100vh-14rem)] flex items-center justify-center bg-[#E8EEF7]">
        <div className="w-8 h-8 border-4 border-[#B8862B] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-8">
      {/* 1. Breadcrumbs */}
      <Breadcrumbs
        items={[
          {
            label: language === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools",
            href: "/tools",
          },
          {
            label: language === "ta" ? "எனது ஜாதகங்கள்" : "My Horoscopes",
          },
        ]}
      />

      {/* 2. Top Section: Page Heading & Primary Create New Horoscope Button */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-[#DDE5F0]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2 h-2 rounded-full bg-[#B8862B]" />
            <span className="text-xs font-bold uppercase tracking-wider text-[#B8862B]">
              Vedic &amp; KP Astrological Engine
            </span>
          </div>
          <h1 className="font-serif text-2xl sm:text-3xl lg:text-4xl font-bold text-[#102A4C]">
            {language === "ta" ? "எனது ஜாதகங்கள்" : "My Horoscopes"}
          </h1>
          <p className="mt-1 text-xs sm:text-sm text-[#52667E]">
            {language === "ta"
              ? "சேமிக்கப்பட்ட வேத மற்றும் கே.பி. ஜாதகங்களின் பட்டியல் மற்றும் கணிப்பு விவரங்கள்."
              : "Access and manage your saved Vedic and KP horoscopes with stored calculation snapshots."}
          </p>
        </div>

        <Link
          href="/horoscope"
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold text-white bg-[#102A4C] hover:bg-[#1E3A61] shadow-xs transition-colors shrink-0"
        >
          <Plus className="w-4 h-4 text-[#B8862B]" />
          <span>{language === "ta" ? "+ புதிய ஜாதகம்" : "+ Create New Horoscope"}</span>
        </Link>
      </div>

      {/* 3. Main Section: Saved Horoscopes List ONLY */}
      <SavedHoroscopesList showHeader={false} showBanner={false} pageSize={12} />
    </div>
  );
}

export default function HoroscopeToolsPage() {
  return (
    <React.Suspense
      fallback={
        <div className="min-h-[calc(100vh-14rem)] flex items-center justify-center bg-[#E8EEF7]">
          <div className="w-8 h-8 border-4 border-[#B8862B] border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <HoroscopeToolsContent />
    </React.Suspense>
  );
}
