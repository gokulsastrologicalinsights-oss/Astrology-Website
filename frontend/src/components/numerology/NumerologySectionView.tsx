"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { listNumerologyReports } from "@/lib/api";
import { SavedNumerologyReportResponse } from "@/lib/types";
import {
  Compass,
  Sparkles,
  ArrowLeft,
  ArrowRight,
  Database,
  Calendar,
  Grid3X3,
  FileText,
  Clock,
  Heart,
  Eye,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  ShieldCheck,
  Plus,
  Trash2,
  RefreshCw,
  Layers,
} from "lucide-react";

// Client-side helper calculation functions for instant name comparison
const PYTHAGOREAN_MAP: Record<string, number> = {
  A: 1, B: 2, C: 3, D: 4, E: 5, F: 6, G: 7, H: 8, I: 9,
  J: 1, K: 2, L: 3, M: 4, N: 5, O: 6, P: 7, Q: 8, R: 9,
  S: 1, T: 2, U: 3, V: 4, W: 5, X: 6, Y: 7, Z: 8,
};

const CHALDEAN_MAP: Record<string, number> = {
  A: 1, I: 1, J: 1, Q: 1, Y: 1,
  B: 2, K: 2, R: 2,
  C: 3, G: 3, L: 3, S: 3,
  D: 4, M: 4, T: 4,
  E: 5, H: 5, N: 5, X: 5,
  U: 6, V: 6, W: 6,
  O: 7, Z: 7,
  F: 8, P: 8,
};

const VOWELS = new Set(["A", "E", "I", "O", "U"]);

function reduceNumber(val: number, preserveMaster: boolean = true): number {
  if (val <= 0) return 0;
  while (val > 9) {
    if (preserveMaster && (val === 11 || val === 22 || val === 33)) break;
    val = val
      .toString()
      .split("")
      .reduce((acc, digit) => acc + parseInt(digit, 10), 0);
  }
  return val;
}

function calculateNameVibration(name: string, convention: "pythagorean" | "chaldean") {
  const clean = name.toUpperCase().replace(/[^A-Z]/g, "");
  const map = convention === "chaldean" ? CHALDEAN_MAP : PYTHAGOREAN_MAP;

  let totalSum = 0;
  let vowelSum = 0;
  let consonantSum = 0;

  for (const char of clean) {
    const val = map[char] || 0;
    totalSum += val;
    if (VOWELS.has(char)) {
      vowelSum += val;
    } else {
      consonantSum += val;
    }
  }

  return {
    cleanName: clean,
    expression: reduceNumber(totalSum, true),
    rawExpressionSum: totalSum,
    soulUrge: reduceNumber(vowelSum, true),
    personality: reduceNumber(consonantSum, true),
    letterCount: clean.length,
  };
}

export function NumerologySectionView() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialTab =
    (searchParams.get("tab") as "overview" | "name" | "compatibility" | "reports") ||
    "overview";

  const { language, t } = useLanguage();
  const { user, session, isAuthenticated, isLoading } = useAuth();

  const [activeTab, setActiveTab] = useState<"overview" | "name" | "compatibility" | "reports">(
    initialTab
  );

  // Saved reports state
  const [savedReports, setSavedReports] = useState<SavedNumerologyReportResponse[]>([]);
  const [loadingReports, setLoadingReports] = useState(false);

  // Name Spelling Comparator state
  const [primaryName, setPrimaryName] = useState("Gokul");
  const [alternativeSpellings, setAlternativeSpellings] = useState<string[]>([
    "Gokull",
    "Gokhul",
  ]);
  const [spellingConvention, setSpellingConvention] = useState<"pythagorean" | "chaldean">("pythagorean");

  // Compatibility Checker state
  const [partner1Name, setPartner1Name] = useState("Partner 1");
  const [partner1Dob, setPartner1Dob] = useState("1995-05-14");
  const [partner2Name, setPartner2Name] = useState("Partner 2");
  const [partner2Dob, setPartner2Dob] = useState("1996-09-22");
  const [compatibilityResult, setCompatibilityResult] = useState<any | null>(null);

  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !user)) {
      router.replace("/login");
    }
  }, [isAuthenticated, user, isLoading, router]);

  useEffect(() => {
    const tabParam = searchParams.get("tab");
    if (tabParam && ["overview", "name", "compatibility", "reports"].includes(tabParam)) {
      setActiveTab(tabParam as any);
    }
  }, [searchParams]);

  // Load saved reports
  useEffect(() => {
    if (isAuthenticated && session?.access_token) {
      setLoadingReports(true);
      listNumerologyReports(session.access_token, 20, 0)
        .then((res) => {
          setSavedReports(res.reports || []);
        })
        .catch((err) => {
          console.warn("Failed to load saved numerology reports:", err);
        })
        .finally(() => {
          setLoadingReports(false);
        });
    }
  }, [isAuthenticated, session?.access_token]);

  // Handle compatibility calculation
  const handleCalculateCompatibility = () => {
    if (!partner1Dob || !partner2Dob) return;

    const calcLifePath = (dob: string) => {
      const nums = dob.replace(/\D/g, "").split("").map((d) => parseInt(d, 10));
      const sum = nums.reduce((a, b) => a + b, 0);
      return reduceNumber(sum, true);
    };

    const lp1 = calcLifePath(partner1Dob);
    const lp2 = calcLifePath(partner2Dob);
    const jointPurpose = reduceNumber(lp1 + lp2, true);

    const calcDay = (dob: string) => {
      const day = parseInt(dob.split("-")[2], 10);
      return reduceNumber(day, true);
    };

    const bday1 = calcDay(partner1Dob);
    const bday2 = calcDay(partner2Dob);
    const romanticVibration = reduceNumber(bday1 + bday2, true);

    setCompatibilityResult({
      lp1,
      lp2,
      jointPurpose,
      bday1,
      bday2,
      romanticVibration,
      harmonyScore: Math.min(95, 60 + ((lp1 * lp2) % 35)),
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-[calc(100vh-14rem)] flex items-center justify-center bg-[#E8EEF7]">
        <div className="w-8 h-8 border-4 border-[#3478F6] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  const numerologyCards = [
    {
      id: "card-calc",
      titleEn: "Numerology Calculator",
      titleTa: "எண் கணித கால்குலேட்டர்",
      descEn:
        "Accepts full name and birth date to compute deterministic Life Path, Birthday, Attitude, and Personal Year numbers with Pythagorean or Chaldean systems.",
      descTa:
        "முழு பெயர் மற்றும் பிறந்த தேதியை அடிப்படையாகக் கொண்டு ஆயுள் பாதை, பிறந்த எண், மற்றும் நடப்பு ஆண்டு அதிர்வுகளை துல்லியமாகக் கணக்கிடுங்கள்.",
      icon: Sparkles,
      href: "/numerology/traditional",
      ctaEn: "Open Core Calculator",
      ctaTa: "கால்குலேட்டரைத் திறக்க",
      badge: "Core Numbers",
      color: "text-[#3478F6] bg-[#EBF2FE] border-[#BFDBFE]",
    },
    {
      id: "card-name",
      titleEn: "Name Numerology & Spellings",
      titleTa: "பெயர் எண் & மாற்று எழுத்து ஒப்பீடு",
      descEn:
        "Calculate the Expression/Destiny number from your name. Compare alternative spellings side-by-side to evaluate vowel harmonies and consonant balance.",
      descTa:
        "பெயரின் அதிர்வு எண்ணைக் கணக்கிடுங்கள். பல்வேறு மாற்று எழுத்துப்பிழைகளை அருகருகே ஒப்பிட்டு சிறந்த கூட்டு எண்ணைக் கண்டறியுங்கள்.",
      icon: FileText,
      action: () => setActiveTab("name"),
      ctaEn: "Compare Spellings",
      ctaTa: "பெயர்களை ஒப்பிடுக",
      badge: "Spelling Analyzer",
      color: "text-[#3478F6] bg-[#EBF2FE] border-[#BFDBFE]",
    },
    {
      id: "card-birth-lifepath",
      titleEn: "Birth & Life Path Numbers",
      titleTa: "பிறப்பு எண் & விதி எண்",
      descEn:
        "Derive Driver/Moolank (day of birth) and Destiny/Bhagyank (sum of full date). Preserves master numbers (11, 22, 33) under strict reduction standards.",
      descTa:
        "பிறந்த தேதியின் மூலம் மூல எண் (Driver) மற்றும் முழு பிறந்த தேதியின் கூட்டுத்தொகை மூலம் விதி எண் (Destiny) ஆகியவற்றை அறியுங்கள்.",
      icon: Calendar,
      href: "/numerology/traditional",
      ctaEn: "Derive Driver & Destiny",
      ctaTa: "விதி எண்ணைக் கணக்கிடுக",
      badge: "Moolank & Bhagyank",
      color: "text-[#3478F6] bg-[#EBF2FE] border-[#BFDBFE]",
    },
    {
      id: "card-soul-personality",
      titleEn: "Soul Urge & Personality",
      titleTa: "ஆத்ம எண் & ஆளுமை எண்",
      descEn:
        "Calculate Soul Urge / Heart's Desire from vowels and outer Personality number from consonants. Identifies hidden passions and karmic lessons.",
      descTa:
        "உயிர் எழுத்துக்களின் மூலம் ஆத்ம விருப்ப எண் மற்றும் மெய் எழுத்துக்களின் மூலம் வெளி ஆளுமை எண்ணைக் கணக்கிட்டு பண்புகளை அறியுங்கள்.",
      icon: Compass,
      href: "/numerology/traditional",
      ctaEn: "Analyze Soul & Personality",
      ctaTa: "ஆத்ம எண்ணை அறிய",
      badge: "Vowels & Consonants",
      color: "text-[#3478F6] bg-[#EBF2FE] border-[#BFDBFE]",
    },
    {
      id: "card-compatibility",
      titleEn: "Numerology Compatibility",
      titleTa: "எண் கணித பொருத்தம்",
      descEn:
        "Synthesize two birth dates and names to evaluate relationship purpose, shared financial energy, romantic harmony, and joint karmic lessons.",
      descTa:
        "இரு நபர்களின் பிறந்த தேதிகள் மற்றும் பெயர்களை ஒப்பிட்டு உறவு நோக்கம், நிதி அதிர்வுகள் மற்றும் இணக்க நிலையை அறியுங்கள்.",
      icon: Heart,
      action: () => setActiveTab("compatibility"),
      ctaEn: "Check Compatibility",
      ctaTa: "பொருத்தத்தை சரிபார்க்க",
      badge: "Couples Synthesis",
      color: "text-[#3478F6] bg-[#EBF2FE] border-[#BFDBFE]",
    },
    {
      id: "card-reports",
      titleEn: "Numerology Reports & Matrix",
      titleTa: "அறிக்கைகள் & விதி வரைபடம்",
      descEn:
        "Reopen saved numerology readings, print reports, or explore the 22 Major Arcana Destiny Matrix and Yuan 3x3 Lo Shu Magic Square with 8 Arrows.",
      descTa:
        "சேமிக்கப்பட்ட அறிக்கைகளைத் திறக்கவும், அச்சிடவும் அல்லது 22 ஆர்கானா விதி வரைபடம் மற்றும் லோ-ஷூ 3x3 கட்டத்தை ஆராயவும்.",
      icon: Database,
      action: () => setActiveTab("reports"),
      ctaEn: "Browse Reports & Matrix",
      ctaTa: "அறிக்கைகளை அணுகுக",
      badge: "Saved Readings",
      color: "text-[#3478F6] bg-[#EBF2FE] border-[#BFDBFE]",
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-8">
      {/* 1. Breadcrumb Navigation & Back Action */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <Breadcrumbs
          items={[
            {
              label: language === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools",
              href: "/tools",
            },
            {
              label: language === "ta" ? "எண் கணிதம்" : "Numerology",
            },
          ]}
        />

        <Link
          href="/tools"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#52667E] hover:text-[#102A4C] transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>
            {language === "ta" ? "ஜோதிடக் கருவிகள் முதன்மைப் பக்கம்" : "Back to Astrology Tools"}
          </span>
        </Link>
      </div>

      {/* 2. Page Title Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-[#DDE5F0]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2 h-2 rounded-full bg-[#3478F6]" />
            <span className="text-xs font-bold uppercase tracking-wider text-[#3478F6]">
              Vibrational Blueprint &amp; Metaphysical Science
            </span>
          </div>
          <h1 className="font-serif text-2xl sm:text-3xl lg:text-4xl font-bold text-[#102A4C]">
            Numerology | எண் கணிதம்
          </h1>
          <p className="mt-1 text-xs sm:text-sm text-[#52667E]">
            {language === "ta"
              ? "பாரம்பரிய பித்தகோரியன்/கால்டியன் முறைகள், மாற்று பெயர் எழுத்து ஒப்பீடு, விதி அணி மற்றும் லோ-ஷூ கட்டம்."
              : "Calculate core numbers, compare alternative spellings, analyze couples compatibility, and inspect Destiny Matrices."}
          </p>
        </div>

        {/* Local Internal Tabs */}
        <div className="flex items-center gap-1 p-1 rounded-xl bg-white border border-[#DDE5F0] shadow-2xs shrink-0 overflow-x-auto">
          <button
            type="button"
            onClick={() => setActiveTab("overview")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer whitespace-nowrap ${
              activeTab === "overview"
                ? "bg-[#102A4C] text-white shadow-xs"
                : "text-[#52667E] hover:text-[#102A4C]"
            }`}
          >
            {language === "ta" ? "அனைத்து அம்சங்கள்" : "Overview"}
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("name")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer whitespace-nowrap ${
              activeTab === "name"
                ? "bg-[#102A4C] text-white shadow-xs"
                : "text-[#52667E] hover:text-[#102A4C]"
            }`}
          >
            {language === "ta" ? "பெயர் ஒப்பீடு" : "Name Comparator"}
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("compatibility")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer whitespace-nowrap ${
              activeTab === "compatibility"
                ? "bg-[#102A4C] text-white shadow-xs"
                : "text-[#52667E] hover:text-[#102A4C]"
            }`}
          >
            {language === "ta" ? "பொருத்தம்" : "Compatibility"}
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("reports")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer whitespace-nowrap ${
              activeTab === "reports"
                ? "bg-[#102A4C] text-white shadow-xs"
                : "text-[#52667E] hover:text-[#102A4C]"
            }`}
          >
            {language === "ta" ? "சேமித்த அறிக்கைகள்" : "Saved Reports"}
          </button>
        </div>
      </div>

      {/* 3. Tab Content */}

      {/* TAB 1: OVERVIEW (The 6 Cards) */}
      {activeTab === "overview" && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {numerologyCards.map((card) => {
              const Icon = card.icon;

              const content = (
                <div className="flex flex-col justify-between h-full space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div
                        className={`w-12 h-12 rounded-xl flex items-center justify-center shadow-2xs border ${card.color}`}
                      >
                        <Icon className="w-6 h-6" />
                      </div>
                      <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-[#F8FAFC] text-[#52667E] border border-[#E2E8F0]">
                        {card.badge}
                      </span>
                    </div>

                    <div>
                      <h3 className="font-serif text-lg font-bold text-[#102A4C] group-hover:text-[#3478F6] transition-colors">
                        {language === "ta" ? card.titleTa : card.titleEn}
                      </h3>
                      <p className="text-[11px] font-tamil text-[#3478F6] font-medium">
                        {language === "ta" ? card.titleEn : card.titleTa}
                      </p>
                    </div>

                    <p className="text-xs text-[#52667E] leading-relaxed">
                      {language === "ta" ? card.descTa : card.descEn}
                    </p>
                  </div>

                  <div className="pt-4 border-t border-[#F1F5F9] flex items-center justify-between text-xs font-bold text-[#3478F6]">
                    <span>{language === "ta" ? card.ctaTa : card.ctaEn}</span>
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              );

              if (card.href) {
                return (
                  <Link
                    key={card.id}
                    href={card.href}
                    className="p-6 rounded-2xl bg-white border border-[#DDE5F0] hover:border-[#3478F6] shadow-xs hover:shadow-md transition-all group block"
                  >
                    {content}
                  </Link>
                );
              }

              return (
                <button
                  key={card.id}
                  type="button"
                  onClick={card.action}
                  className="p-6 rounded-2xl bg-white border border-[#DDE5F0] hover:border-[#3478F6] shadow-xs hover:shadow-md transition-all group block text-left w-full cursor-pointer"
                >
                  {content}
                </button>
              );
            })}
          </div>

          {/* Direct Method Shortcuts */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Link
              href="/numerology/traditional"
              className="p-5 rounded-2xl bg-white border border-[#DDE5F0] hover:border-[#3478F6] shadow-xs hover:shadow-sm transition-all flex items-center gap-3.5 group"
            >
              <div className="w-10 h-10 rounded-xl bg-[#EBF2FE] text-[#3478F6] flex items-center justify-center shrink-0">
                <Compass className="w-5 h-5 group-hover:rotate-12 transition-transform" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-[#102A4C]">Traditional Calculator</h4>
                <p className="text-[11px] text-[#52667E]">Pythagorean &amp; Chaldean core numbers</p>
              </div>
            </Link>

            <Link
              href="/numerology/destiny-matrix"
              className="p-5 rounded-2xl bg-white border border-[#DDE5F0] hover:border-[#3478F6] shadow-xs hover:shadow-sm transition-all flex items-center gap-3.5 group"
            >
              <div className="w-10 h-10 rounded-xl bg-[#FAF2DE] text-[#B8862B] flex items-center justify-center shrink-0">
                <Sparkles className="w-5 h-5 group-hover:scale-105 transition-transform" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-[#102A4C]">Destiny Matrix</h4>
                <p className="text-[11px] text-[#52667E]">22 Major Arcana octagram geometry</p>
              </div>
            </Link>

            <Link
              href="/numerology/advanced"
              className="p-5 rounded-2xl bg-white border border-[#DDE5F0] hover:border-[#3478F6] shadow-xs hover:shadow-sm transition-all flex items-center gap-3.5 group"
            >
              <div className="w-10 h-10 rounded-xl bg-[#F0FDF4] text-emerald-600 flex items-center justify-center shrink-0">
                <Grid3X3 className="w-5 h-5 group-hover:scale-105 transition-transform" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-[#102A4C]">Advanced Yuan Matrix</h4>
                <p className="text-[11px] text-[#52667E]">Lo Shu 3x3 Magic Square &amp; Pinnacles</p>
              </div>
            </Link>
          </div>
        </div>
      )}

      {/* TAB 2: NAME SPELLING COMPARATOR */}
      {activeTab === "name" && (
        <div className="space-y-6">
          <div className="p-6 sm:p-8 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-6">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <FileText className="w-4 h-4 text-[#3478F6]" />
                <h2 className="text-lg font-bold text-[#102A4C]">
                  {language === "ta"
                    ? "பெயர் எண் மற்றும் மாற்று எழுத்து ஒப்பீடு"
                    : "Name Numerology & Alternative Spelling Comparison"}
                </h2>
              </div>
              <p className="text-xs text-[#52667E]">
                {language === "ta"
                  ? "பல்வேறு மாற்று எழுத்துப்பிழைகளை உள்ளிட்டு அவற்றின் பித்தகோரியன் மற்றும் கால்டியன் கூட்டு எண்களை அருகருகே ஒப்பிடுங்கள்."
                  : "Enter different name spellings to compare their total expression number, vowels (Soul Urge), and consonants (Personality)."}
              </p>
            </div>

            {/* Inputs & Settings */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pb-4 border-b border-[#F1F5F9]">
              <div className="sm:col-span-2">
                <label className="block text-xs font-semibold text-[#334155] mb-1">
                  Primary Name / பிறந்த பெயர்
                </label>
                <input
                  type="text"
                  value={primaryName}
                  onChange={(e) => setPrimaryName(e.target.value)}
                  placeholder="e.g. Gokul"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-[#DDE5F0] text-sm text-[#102A4C] focus:border-[#3478F6] focus:ring-1 focus:ring-[#3478F6]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#334155] mb-1">
                  Numerology Convention
                </label>
                <select
                  value={spellingConvention}
                  onChange={(e) => setSpellingConvention(e.target.value as any)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-[#DDE5F0] text-xs text-[#102A4C] focus:border-[#3478F6]"
                >
                  <option value="pythagorean">Pythagorean (Western 1-9)</option>
                  <option value="chaldean">Chaldean (Ancient 1-8)</option>
                </select>
              </div>
            </div>

            {/* Alternative Spellings Input Rows */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-[#102A4C]">
                  Alternative Spellings to Compare:
                </span>
                {alternativeSpellings.length < 4 && (
                  <button
                    type="button"
                    onClick={() =>
                      setAlternativeSpellings([...alternativeSpellings, ""])
                    }
                    className="inline-flex items-center gap-1 text-xs font-semibold text-[#3478F6] hover:underline cursor-pointer"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Add Spelling</span>
                  </button>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {alternativeSpellings.map((spelling, idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <input
                      type="text"
                      value={spelling}
                      onChange={(e) => {
                        const updated = [...alternativeSpellings];
                        updated[idx] = e.target.value;
                        setAlternativeSpellings(updated);
                      }}
                      placeholder={`Alternative #${idx + 1} (e.g. ${primaryName + "l"})`}
                      className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] text-xs text-[#102A4C] focus:border-[#3478F6]"
                    />
                    <button
                      type="button"
                      onClick={() => {
                        const updated = alternativeSpellings.filter(
                          (_, i) => i !== idx
                        );
                        setAlternativeSpellings(updated);
                      }}
                      className="p-2 text-rose-500 hover:text-rose-700 hover:bg-rose-50 rounded-lg cursor-pointer"
                      title="Remove"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Comparison Results Table */}
            <div className="pt-4 border-t border-[#F1F5F9]">
              <h3 className="text-xs font-bold uppercase tracking-wider text-[#94A3B8] mb-3">
                Side-by-Side Vibrational Analysis ({spellingConvention.toUpperCase()})
              </h3>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border border-[#DDE5F0] rounded-xl overflow-hidden">
                  <thead className="bg-[#F8FAFC] text-[#52667E] border-b border-[#DDE5F0]">
                    <tr>
                      <th className="py-2.5 px-3 font-semibold">Spelling</th>
                      <th className="py-2.5 px-3 font-semibold text-center">Name Number</th>
                      <th className="py-2.5 px-3 font-semibold text-center">Soul Urge (Vowels)</th>
                      <th className="py-2.5 px-3 font-semibold text-center">Personality (Consonants)</th>
                      <th className="py-2.5 px-3 font-semibold text-center">Letters</th>
                      <th className="py-2.5 px-3 font-semibold">Vibrational Synthesis</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#F1F5F9]">
                    {[primaryName, ...alternativeSpellings.filter((s) => s.trim())].map(
                      (nameStr, idx) => {
                        const calc = calculateNameVibration(
                          nameStr || "Unnamed",
                          spellingConvention
                        );
                        const isPrimary = idx === 0;

                        return (
                          <tr
                            key={idx}
                            className={
                              isPrimary
                                ? "bg-[#EBF2FE]/30 font-semibold text-[#102A4C]"
                                : "hover:bg-[#F8FAFC]"
                            }
                          >
                            <td className="py-3 px-3">
                              <div className="flex items-center gap-2">
                                <span>{calc.cleanName || nameStr}</span>
                                {isPrimary && (
                                  <span className="px-1.5 py-0.2 rounded text-[9px] font-bold bg-[#3478F6] text-white">
                                    Primary
                                  </span>
                                )}
                              </div>
                            </td>
                            <td className="py-3 px-3 text-center">
                              <span className="inline-flex items-center justify-center w-7 h-7 rounded-lg bg-[#EBF2FE] border border-[#BFDBFE] text-[#3478F6] font-bold text-xs">
                                {calc.expression}
                              </span>
                            </td>
                            <td className="py-3 px-3 text-center font-mono">
                              {calc.soulUrge}
                            </td>
                            <td className="py-3 px-3 text-center font-mono">
                              {calc.personality}
                            </td>
                            <td className="py-3 px-3 text-center text-[#52667E]">
                              {calc.letterCount}
                            </td>
                            <td className="py-3 px-3 text-[11px] text-[#52667E]">
                              {calc.expression === 1 && "Leadership, pioneering initiative, dynamic drive."}
                              {calc.expression === 2 && "Cooperation, diplomacy, sensitivity, peace."}
                              {calc.expression === 3 && "Creative expression, joy, communication, inspiration."}
                              {calc.expression === 4 && "Stability, disciplined structure, methodical work."}
                              {calc.expression === 5 && "Freedom, versatility, adventure, adaptability."}
                              {calc.expression === 6 && "Nurturing, responsibility, harmonious home."}
                              {calc.expression === 7 && "Analysis, analytical intellect, metaphysical inquiry."}
                              {calc.expression === 8 && "Material mastery, executive authority, abundance."}
                              {calc.expression === 9 && "Universal compassion, humanitarian vision."}
                              {calc.expression === 11 && "Master Intuition (11/2) — Spiritual illumination."}
                              {calc.expression === 22 && "Master Builder (22/4) — Transforming vision into reality."}
                              {calc.expression === 33 && "Master Teacher (33/6) — Selfless devotion and service."}
                            </td>
                          </tr>
                        );
                      }
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: COMPATIBILITY ANALYZER */}
      {activeTab === "compatibility" && (
        <div className="space-y-6">
          <div className="p-6 sm:p-8 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-6">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Heart className="w-4 h-4 text-rose-500" />
                <h2 className="text-lg font-bold text-[#102A4C]">
                  {language === "ta"
                    ? "எண் கணித பொருத்தம் & கூட்டாண்மை பகுப்பாய்வு"
                    : "Numerology Compatibility & Partnership Analysis"}
                </h2>
              </div>
              <p className="text-xs text-[#52667E]">
                {language === "ta"
                  ? "இரு நபர்களின் பிறந்த தேதிகளை அடிப்படையாகக் கொண்டு கூட்டாண்மை நோக்கம் மற்றும் காதல் இணக்கத்தை அறியுங்கள்."
                  : "Calculate relationship purpose and vibrational resonance between two birth dates."}
              </p>
            </div>

            {/* Two Partner Inputs */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-4 rounded-xl bg-[#F8FAFC] border border-[#DDE5F0]">
              {/* Partner 1 */}
              <div className="space-y-3">
                <div className="text-xs font-bold text-[#102A4C] flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#3478F6]" />
                  <span>First Individual / முதல் நபர்</span>
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-[#52667E] mb-1">
                    Name
                  </label>
                  <input
                    type="text"
                    value={partner1Name}
                    onChange={(e) => setPartner1Name(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-[#DDE5F0] text-xs text-[#102A4C] bg-white"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-[#52667E] mb-1">
                    Date of Birth
                  </label>
                  <input
                    type="date"
                    value={partner1Dob}
                    onChange={(e) => setPartner1Dob(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-[#DDE5F0] text-xs text-[#102A4C] bg-white"
                  />
                </div>
              </div>

              {/* Partner 2 */}
              <div className="space-y-3">
                <div className="text-xs font-bold text-[#102A4C] flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-rose-500" />
                  <span>Second Individual / இரண்டாம் நபர்</span>
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-[#52667E] mb-1">
                    Name
                  </label>
                  <input
                    type="text"
                    value={partner2Name}
                    onChange={(e) => setPartner2Name(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-[#DDE5F0] text-xs text-[#102A4C] bg-white"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-[#52667E] mb-1">
                    Date of Birth
                  </label>
                  <input
                    type="date"
                    value={partner2Dob}
                    onChange={(e) => setPartner2Dob(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-[#DDE5F0] text-xs text-[#102A4C] bg-white"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-center">
              <button
                type="button"
                onClick={handleCalculateCompatibility}
                className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl text-xs font-bold text-white bg-[#102A4C] hover:bg-[#1E3A61] shadow-xs cursor-pointer transition-colors"
              >
                <Heart className="w-4 h-4 text-rose-400" />
                <span>Calculate Vibrational Compatibility</span>
              </button>
            </div>

            {/* Results Display */}
            {compatibilityResult && (
              <div className="p-6 rounded-xl border border-[#DDE5F0] bg-[#FAFBFD] space-y-4 animate-in fade-in duration-200">
                <div className="flex items-center justify-between pb-3 border-b border-[#DDE5F0]">
                  <h3 className="font-serif text-base font-bold text-[#102A4C]">
                    Compatibility Blueprint: {partner1Name} &amp; {partner2Name}
                  </h3>
                  <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    {compatibilityResult.harmonyScore}% Harmonic Resonance
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                  <div className="p-3 rounded-lg bg-white border border-[#DDE5F0]">
                    <span className="text-[10px] text-[#52667E] block">{partner1Name} Life Path</span>
                    <strong className="text-lg font-bold text-[#3478F6]">
                      {compatibilityResult.lp1}
                    </strong>
                  </div>

                  <div className="p-3 rounded-lg bg-white border border-[#DDE5F0]">
                    <span className="text-[10px] text-[#52667E] block">{partner2Name} Life Path</span>
                    <strong className="text-lg font-bold text-[#3478F6]">
                      {compatibilityResult.lp2}
                    </strong>
                  </div>

                  <div className="p-3 rounded-lg bg-white border border-[#DDE5F0]">
                    <span className="text-[10px] text-[#52667E] block">Joint Relationship Purpose</span>
                    <strong className="text-lg font-bold text-[#B8862B]">
                      {compatibilityResult.jointPurpose}
                    </strong>
                  </div>

                  <div className="p-3 rounded-lg bg-white border border-[#DDE5F0]">
                    <span className="text-[10px] text-[#52667E] block">Emotional Resonance</span>
                    <strong className="text-lg font-bold text-rose-600">
                      {compatibilityResult.romanticVibration}
                    </strong>
                  </div>
                </div>

                {/* Disclaimer */}
                <div className="p-3 rounded-lg bg-[#FAF8F5] border border-[#E2DCD5] text-[11px] text-[#64748B] flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                  <p>
                    <strong>Metaphysical Notice:</strong> Numerology compatibility is a philosophical reflection of vibrational tendencies and archetypal resonances. It is provided for personal reflection and does not constitute a scientifically established or deterministically binding guarantee.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 4: SAVED REPORTS */}
      {activeTab === "reports" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-[#DDE5F0] bg-white p-6 sm:p-8 shadow-xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#DDE5F0]">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-[#EBF2FE] border border-[#BFDBFE] flex items-center justify-center text-[#3478F6] shadow-2xs">
                  <Database className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="font-serif text-lg font-bold text-[#102A4C]">
                    {t.savedNumerologyTitle || "Saved Numerology Reports"}
                  </h2>
                  <p className="text-xs text-[#52667E]">
                    {t.savedNumerologySubtitle || "Auto-saved numerology calculations and readings."}
                  </p>
                </div>
              </div>

              <Link
                href="/numerology/traditional"
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-bold text-white bg-[#102A4C] hover:bg-[#1E3A61]"
              >
                <span>Calculate New Report</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {loadingReports ? (
              <div className="py-12 text-center">
                <div className="inline-block animate-spin w-6 h-6 border-3 border-[#3478F6] border-t-transparent rounded-full mb-2" />
                <p className="text-xs text-[#52667E]">{t.loading}</p>
              </div>
            ) : savedReports.length === 0 ? (
              <div className="mt-6 py-8 px-6 rounded-xl border border-dashed border-[#DDE5F0] bg-[#F8FAFC] text-center">
                <Clock className="w-8 h-8 mx-auto text-[#94A3B8] mb-2" />
                <h3 className="font-serif text-sm font-bold text-[#102A4C]">
                  {language === "ta" ? "அறிக்கைகள் இல்லை" : "No Saved Reports Yet"}
                </h3>
                <p className="mt-1 text-xs text-[#52667E] max-w-md mx-auto">
                  {t.savedNumerologyEmpty}
                </p>
              </div>
            ) : (
              <div className="mt-6 divide-y divide-[#F1F5F9]">
                {savedReports.map((report) => (
                  <div
                    key={report.id}
                    className="py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-[#F8FAFC] px-2 rounded-xl transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <span className="w-8 h-8 rounded-lg bg-[#EBF2FE] border border-[#BFDBFE] text-[#3478F6] font-bold text-xs flex items-center justify-center">
                        #{report.display_number}
                      </span>
                      <div>
                        <div className="font-bold text-xs text-[#102A4C] flex items-center gap-2">
                          <span>{report.person_name}</span>
                          <span className="text-[10px] font-semibold uppercase px-2 py-0.2 rounded-full bg-[#F8FAFC] text-[#52667E] border border-[#DDE5F0]">
                            {report.method.replace("_", " ")}
                          </span>
                        </div>
                        <div className="text-[11px] text-[#64748B] flex items-center gap-3 mt-0.5">
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3 h-3 text-[#94A3B8]" />
                            DOB: {report.birth_date}
                          </span>
                          <span>•</span>
                          <span>
                            Saved: {new Date(report.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <Link
                        href={`/numerology/report/${report.id}`}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#DDE5F0] bg-white hover:bg-[#EBF2FE] hover:border-[#BFDBFE] text-xs font-semibold text-[#102A4C] shadow-2xs transition-colors"
                      >
                        <Eye className="w-3.5 h-3.5 text-[#3478F6]" />
                        <span>{t.reopenReport}</span>
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
