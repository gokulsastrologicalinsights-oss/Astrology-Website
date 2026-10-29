"use client";

import React, { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { FeatureGuard } from "@/components/auth/FeatureGuard";
import {
  LayoutDashboard,
  Sparkles,
  Sun,
  Calendar as CalendarIcon,
  Sliders,
  Bookmark,
  Settings,
  Compass,
} from "lucide-react";

import { MuhurtaDashboard } from "@/components/muhurta/MuhurtaDashboard";
import { FindAuspiciousDates } from "@/components/muhurta/FindAuspiciousDates";
import { DailyPanchangamView } from "@/components/muhurta/DailyPanchangamView";
import { MuhurtaCalendarView } from "@/components/muhurta/MuhurtaCalendarView";
import { OccasionRulesView } from "@/components/muhurta/OccasionRulesView";
import { SavedMuhurtasView } from "@/components/muhurta/SavedMuhurtasView";
import { CalculationSettingsView } from "@/components/muhurta/CalculationSettingsView";

function MuhurtaContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { language } = useLanguage();
  const { user, isAuthenticated, isLoading } = useAuth();

  const initialTab = searchParams.get("tab") || "dashboard";
  const [activeTab, setActiveTab] = useState<string>(initialTab);

  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !user)) {
      router.replace("/login");
    }
  }, [isAuthenticated, user, isLoading, router]);

  useEffect(() => {
    const tabParam = searchParams.get("tab");
    if (tabParam) {
      setActiveTab(tabParam);
    }
  }, [searchParams]);

  if (isLoading) {
    return (
      <div className="min-h-[calc(100vh-14rem)] flex items-center justify-center bg-[#E8EEF7]">
        <div className="w-8 h-8 border-4 border-amber-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  const handleTabChange = (tab: string, _occasionCode?: string) => {
    setActiveTab(tab);
    router.replace(`/muhurta?tab=${tab}`);
  };

  const tabs = [
    {
      id: "dashboard",
      en: "Dashboard",
      ta: "முகப்பு",
      icon: LayoutDashboard,
    },
    {
      id: "find",
      en: "Find Auspicious Dates",
      ta: "முகூர்த்தம் தேடல்",
      icon: Sparkles,
    },
    {
      id: "panchang",
      en: "Daily Panchangam",
      ta: "தினசரி பஞ்சாங்கம்",
      icon: Sun,
    },
    {
      id: "calendar",
      en: "Muhurta Calendar",
      ta: "முகூர்த்த நாட்காட்டி",
      icon: CalendarIcon,
    },
    {
      id: "rules",
      en: "Occasion Rules",
      ta: "நிகழ்வு விதிமுறைகள்",
      icon: Sliders,
    },
    {
      id: "saved",
      en: "Saved Muhurtas",
      ta: "சேமிக்கப்பட்டவை",
      icon: Bookmark,
    },
    {
      id: "settings",
      en: "Calculation Settings",
      ta: "கணித அமைப்புகள்",
      icon: Settings,
    },
  ];

  return (
    <div className="w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 sm:py-8 space-y-8">
      {/* Breadcrumb Navigation */}
      <Breadcrumbs
        items={[
          {
            label: language === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools",
            href: "/tools",
          },
          {
            label: language === "ta" ? "சுப முகூர்த்தம் (Muhurta)" : "Vedic Muhurta Finder",
          },
        ]}
      />

      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80] mb-2">
            <Compass className="w-3.5 h-3.5 text-[#B8862B]" />
            <span>
              {language === "ta"
                ? "கோகுலின் ஜோதிட நுண்ணறிவு • முகூர்த்த ஆய்வு"
                : "Gokul's Astrological Insights • Muhurta Module"}
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            {language === "ta"
              ? "சுப முகூர்த்த நேரக் கணிப்பான்"
              : "Vedic Muhurta & Panchangam System"}
          </h1>
        </div>

        {/* User Info / Status */}
        <div className="flex items-center gap-2 self-start sm:self-auto">
          <div className="px-3.5 py-1.5 rounded-xl bg-white border border-slate-200 text-xs font-semibold text-slate-700 shadow-sm flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>{user.displayName || user.username}</span>
            <span className="text-slate-400">|</span>
            <span className="capitalize text-amber-700">{user.role}</span>
          </div>
        </div>
      </div>

      {/* Navigation Tab Bar */}
      <div className="bg-white rounded-2xl p-1.5 border border-slate-200 shadow-sm flex items-center gap-1 overflow-x-auto">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => handleTabChange(tab.id)}
              className={`px-4 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 whitespace-nowrap transition-all ${
                isActive
                  ? "bg-gradient-to-r from-amber-600 to-amber-700 text-white shadow-md ring-2 ring-amber-500/20"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100/80"
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{language === "ta" ? tab.ta : tab.en}</span>
            </button>
          );
        })}
      </div>

      {/* Active Tab View Rendering */}
      <div>
        {activeTab === "dashboard" && <MuhurtaDashboard onTabChange={handleTabChange} />}
        {activeTab === "find" && <FindAuspiciousDates />}
        {activeTab === "panchang" && <DailyPanchangamView />}
        {activeTab === "calendar" && <MuhurtaCalendarView />}
        {activeTab === "rules" && <OccasionRulesView />}
        {activeTab === "saved" && <SavedMuhurtasView />}
        {activeTab === "settings" && <CalculationSettingsView />}
      </div>
    </div>
  );
}

export default function MuhurtaPage() {
  return (
    <FeatureGuard permission="panchang_muhurta">
      <React.Suspense
        fallback={
          <div className="min-h-[calc(100vh-14rem)] flex items-center justify-center bg-[#E8EEF7]">
            <div className="w-8 h-8 border-4 border-amber-600 border-t-transparent rounded-full animate-spin" />
          </div>
        }
      >
        <MuhurtaContent />
      </React.Suspense>
    </FeatureGuard>
  );
}
