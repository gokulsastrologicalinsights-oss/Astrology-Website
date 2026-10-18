"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { SavedHoroscopesList } from "@/components/saved/SavedHoroscopesList";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { Compass, Sparkles, Plus, ArrowLeft } from "lucide-react";

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
      <div className="min-h-[calc(100vh-14rem)] flex items-center justify-center bg-[#FAF8F5]">
        <div className="w-8 h-8 border-4 border-[#B8860B] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-8">
      {/* Breadcrumbs */}
      <Breadcrumbs
        items={[
          {
            label: language === "ta" ? "டாஷ்போர்டு" : "Dashboard",
            href: "/dashboard",
          },
          {
            label: language === "ta" ? "சேமிக்கப்பட்ட ஜாதகங்கள்" : "Saved Horoscopes",
          },
        ]}
      />

      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-[#E2DCD5]">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center text-[#B8860B]">
              <Compass className="w-5 h-5" />
            </div>
            <div>
              <h1 className="font-serif text-2xl sm:text-3xl font-bold text-[#0F172A]">
                {language === "ta" ? "சேமிக்கப்பட்ட ஜாதகங்கள்" : "Saved Horoscopes"}
              </h1>
              <p className="mt-1 text-xs sm:text-sm text-[#64748B]">
                {language === "ta"
                  ? "தானாகச் சேமிக்கப்பட்ட அனைத்து ஜாதகக் கணக்கீடுகளையும் மீண்டும் திறக்கலாம்."
                  : "Access and reopen all automatically saved horoscope calculations."}
              </p>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2.5">
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-[#475569] bg-white hover:bg-[#FAF8F5] border border-[#CBD5E1] shadow-2xs transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>{language === "ta" ? "டாஷ்போர்டு" : "Dashboard"}</span>
          </Link>

          <Link
            href="/horoscope"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white bg-[#0F172A] hover:bg-[#1E293B] shadow-xs transition-colors"
          >
            <Plus className="w-3.5 h-3.5 text-[#D8BD80]" />
            <span>{language === "ta" ? "புதிய ஜாதகம் கணிக்க" : "New Horoscope"}</span>
          </Link>
        </div>
      </div>

      {/* Main Content: Saved Horoscopes List */}
      <div className="rounded-2xl border border-[#E2DCD5] bg-white p-6 shadow-xs">
        <SavedHoroscopesList pageSize={8} />
      </div>
    </div>
  );
}
