"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  HoraryTopicInfo,
  InstantHoraryPredictionRequest,
  InstantHoraryPredictionResponse,
} from "@/lib/types";
import { getHoraryPredictionTopics, predictInstantHorary } from "@/lib/api";
import { formatDms } from "@/lib/formatters";
import {
  Sparkles,
  HelpCircle,
  Clock,
  MapPin,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Calendar,
  Compass,
  ArrowRight,
  RotateCcw,
  Dice5,
  Plane,
  Briefcase,
  Scale,
  Heart,
  Home,
  Baby,
  Coins,
  Activity,
  GraduationCap,
  Award,
  TrendingUp,
  Search,
  Copy,
  Printer,
  ChevronDown,
  ChevronUp,
  Share2,
} from "lucide-react";

// Preset Quick Seed numbers for convenient 1-click selection
const QUICK_SEEDS = [1, 27, 54, 77, 108, 145, 189, 204, 249];

export default function InstantKPHoraryPredictorPage() {
  const { language, t } = useLanguage();
  const { isAuthenticated } = useAuth();

  // Topics from API
  const [topics, setTopics] = useState<HoraryTopicInfo[]>([]);
  const [selectedTopicId, setSelectedTopicId] = useState<string>("visa");

  // Form State
  const [horaryNumber, setHoraryNumber] = useState<number>(145);
  const [customQuestion, setCustomQuestion] = useState<string>("Will I get this visa?");
  const [questionDate, setQuestionDate] = useState<string>("");
  const [questionTime, setQuestionTime] = useState<string>("");
  const [locationName, setLocationName] = useState<string>("Chennai, India");
  const [latitude, setLatitude] = useState<number>(13.0827);
  const [longitude, setLongitude] = useState<number>(80.2707);
  const [timezone, setTimezone] = useState<string>("Asia/Kolkata");
  const [ayanamsa, setAyanamsa] = useState<number>(1); // 1 = KP

  // UI state
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<InstantHoraryPredictionResponse | null>(null);
  const [activeLangTab, setActiveLangTab] = useState<"en" | "ta">(language);
  const [showFullChart, setShowFullChart] = useState<boolean>(false);
  const [copiedSummary, setCopiedSummary] = useState<boolean>(false);

  // Sync active language tab when global language changes
  useEffect(() => {
    setActiveLangTab(language);
  }, [language]);

  // Load topics & initialize current moment on mount
  useEffect(() => {
    handleSetCurrentMoment();
    getHoraryPredictionTopics()
      .then((data) => {
        if (data && data.length > 0) {
          setTopics(data);
        }
      })
      .catch((err) => {
        console.warn("Could not load topics dynamically, using fallbacks:", err);
      });
  }, []);

  const handleSetCurrentMoment = () => {
    const now = new Date();
    const yyyy = now.getFullYear();
    const mm = String(now.getMonth() + 1).padStart(2, "0");
    const dd = String(now.getDate()).padStart(2, "0");
    const hh = String(now.getHours()).padStart(2, "0");
    const min = String(now.getMinutes()).padStart(2, "0");
    const ss = String(now.getSeconds()).padStart(2, "0");

    setQuestionDate(`${yyyy}-${mm}-${dd}`);
    setQuestionTime(`${hh}:${min}:${ss}`);
  };

  const handleRandomSeed = () => {
    const rand = Math.floor(Math.random() * 249) + 1;
    setHoraryNumber(rand);
  };

  const handleSelectTopic = (topic: HoraryTopicInfo) => {
    setSelectedTopicId(topic.id);
    setCustomQuestion(
      language === "ta" ? topic.sample_query_ta : topic.sample_query_en
    );
  };

  const handlePredict = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setError(null);

    if (horaryNumber < 1 || horaryNumber > 249) {
      setError(
        language === "ta"
          ? "பிரஸ்ன எண் 1 முதல் 249-க்குள் இருக்க வேண்டும்."
          : "Horary seed number must be between 1 and 249."
      );
      return;
    }

    setLoading(true);
    try {
      const payload: InstantHoraryPredictionRequest = {
        horary_number: horaryNumber,
        question_topic: selectedTopicId,
        question_text: customQuestion.trim() || undefined,
        question_date: questionDate || undefined,
        question_time: questionTime || undefined,
        timezone,
        latitude,
        longitude,
        location_name: locationName,
        ayanamsa,
      };

      const res = await predictInstantHorary(payload);
      setResult(res);
      // Auto-scroll to results card
      setTimeout(() => {
        const el = document.getElementById("instant-verdict-card");
        if (el) el.scrollIntoView({ behavior: "smooth" });
      }, 100);
    } catch (err: any) {
      setError(err?.message || "Failed to compute Horary prediction.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopySummary = () => {
    if (!result) return;
    const isTa = activeLangTab === "ta";
    const text = isTa
      ? `🔮 கே.பி. பிரஸ்ன முடிவு #${result.horary_number}
கேள்வி: ${result.question_text}
தீர்ப்பு: ${result.outcome_label_ta} (நம்பகத்தன்மை: ${result.confidence_score}%)
காரிய சித்தி காலம்: ${result.timing.summary_ta}
ஆளும் கிரகங்கள்: ${result.ruling_planets.join(", ")}
விளக்கம்: ${result.explanation.summary_ta}`
      : `🔮 KP Horary Prediction #${result.horary_number}
Question: ${result.question_text}
Verdict: ${result.outcome_label_en} (${result.confidence_score}% Confidence)
Timing of Fructification: ${result.timing.summary_en}
Ruling Planets: ${result.ruling_planets.join(", ")}
Explanation: ${result.explanation.summary_en}`;

    navigator.clipboard.writeText(text);
    setCopiedSummary(true);
    setTimeout(() => setCopiedSummary(false), 2500);
  };

  const getTopicIcon = (id: string) => {
    switch (id) {
      case "visa":
        return Plane;
      case "job":
        return Briefcase;
      case "court_case":
        return Scale;
      case "marriage":
        return Heart;
      case "property":
        return Home;
      case "childbirth":
        return Baby;
      case "financial_gain":
        return Coins;
      case "recovery":
        return Activity;
      case "higher_education":
        return GraduationCap;
      case "competitive_exam":
        return Award;
      case "business":
        return TrendingUp;
      default:
        return Search;
    }
  };

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
            label:
              language === "ta"
                ? "உடனடி கே.பி. பிரஸ்னம் (1-249)"
                : "Instant KP Horary Predictor (1-249)",
          },
        ]}
      />

      {/* Page Title & Mission Header */}
      <div className="rounded-2xl border border-[#DDE5F0] bg-white p-6 sm:p-8 shadow-xs">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-[#F1F5F9] pb-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center text-[#B8862B] shadow-inner shrink-0">
              <Sparkles className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#EBF2FE] text-[#153F6B] border border-[#BFDBFE] uppercase tracking-wider mb-1">
                Feature 3 • Real-Time Event Predictor
              </div>
              <h1 className="font-serif text-xl sm:text-2xl font-bold text-[#102A4C]">
                {language === "ta"
                  ? "கே.பி. உடனடி பிரஸ்னம் (1 – 249) தானியங்கி நிகழ்வு கணிப்பாளர்"
                  : "Instant KP Horary / Prashna (1–249) Automated Event Predictor"}
              </h1>
              <p className="text-xs sm:text-sm text-[#52667E] mt-0.5">
                {language === "ta"
                  ? "விசா அனுமதி, நேர்காணல் வெற்றி, நீதிமன்ற வழக்கு சாதகம், திருமணம், மற்றும் சொத்து தொடர்பான அவசர கேள்விகளுக்கு வினாடி நேரத்தில் துல்லியமான தீர்ப்பு."
                  : "Instant deterministic real-time question resolution for Visa, Job Interviews, Court Cases, Marriage, Property, and Financial Gains."}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleSetCurrentMoment}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#FAF6EC] text-[#8C6D23] border border-[#D8BD80] hover:bg-[#F3E8CD] transition-colors"
            >
              <Clock className="w-3.5 h-3.5" />
              <span>{language === "ta" ? "தற்போதைய நேரம்" : "Use Current Time"}</span>
            </button>
            <button
              type="button"
              onClick={handleRandomSeed}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#EBF2FE] text-[#153F6B] border border-[#BFDBFE] hover:bg-[#DBEAFE] transition-colors"
              title="Pick a random seed number between 1 and 249"
            >
              <Dice5 className="w-3.5 h-3.5" />
              <span>{language === "ta" ? "ரேண்டம் எண்" : "Random Seed"}</span>
            </button>
          </div>
        </div>

        {/* Input Form */}
        <form onSubmit={handlePredict} className="space-y-6 pt-6">
          {/* Section 1: Seed Number Selection (1 to 249) */}
          <div className="p-5 rounded-2xl bg-gradient-to-br from-[#FAF8F5] to-[#F3EDE2]/60 border border-[#E8DFC8] space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <label className="block text-xs font-bold text-[#102A4C] uppercase tracking-wider">
                  {language === "ta"
                    ? "1. பிரஸ்ன எண் தேர்வு (1 முதல் 249)*"
                    : "1. Select Querent Horary Seed Number (1 to 249)*"}
                </label>
                <p className="text-[11px] text-[#64748B]">
                  {language === "ta"
                    ? "கேட்பவர் உள்ளுணர்வோடு கூறிய எண். இது லக்னத்தை துல்லியமாக நிர்ணயிக்கும்."
                    : "Querent's intuitive number between 1 and 249 fixes Cusp 1 at the exact sub-lord midpoint."}
                </p>
              </div>

              {/* Number Display Box */}
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1">
                  <span className="text-xs text-[#8C6D23] font-bold">#</span>
                  <input
                    type="number"
                    min={1}
                    max={249}
                    required
                    value={horaryNumber}
                    onChange={(e) => setHoraryNumber(parseInt(e.target.value, 10) || 1)}
                    className="w-20 px-2 py-1.5 text-center text-xl font-bold font-serif text-[#102A4C] rounded-xl border border-[#D8BD80] bg-white focus:ring-2 focus:ring-[#B8862B] focus:outline-hidden"
                  />
                </div>
              </div>
            </div>

            {/* Slider */}
            <div className="space-y-2">
              <input
                type="range"
                min={1}
                max={249}
                value={horaryNumber}
                onChange={(e) => setHoraryNumber(parseInt(e.target.value, 10) || 1)}
                className="w-full accent-[#B8862B] cursor-pointer h-2 bg-[#E2DCD5] rounded-lg"
              />
              <div className="flex justify-between text-[10px] text-[#8C6D23] font-semibold px-0.5">
                <span>#1 (Aries / Ketu)</span>
                <span>#77 (Cancer / Sat)</span>
                <span>#145 (Libra / Ven)</span>
                <span>#204 (Sag / Ketu)</span>
                <span>#249 (Pisces / Rahu)</span>
              </div>
            </div>

            {/* Quick Seeds */}
            <div className="flex flex-wrap items-center gap-2 pt-1">
              <span className="text-[11px] font-semibold text-[#64748B]">
                {language === "ta" ? "விரைவு எண்கள்:" : "Quick Seeds:"}
              </span>
              {QUICK_SEEDS.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => setHoraryNumber(s)}
                  className={`px-2.5 py-1 text-xs font-bold rounded-lg transition-colors ${
                    horaryNumber === s
                      ? "bg-[#B8862B] text-white shadow-xs"
                      : "bg-white text-[#52667E] border border-[#DDE5F0] hover:border-[#B8862B]"
                  }`}
                >
                  #{s}
                </button>
              ))}
            </div>
          </div>

          {/* Section 2: Question Topic / One-Click Question Cards */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <label className="block text-xs font-bold text-[#102A4C] uppercase tracking-wider">
                  {language === "ta"
                    ? "2. கேள்வி தலைப்பு & காரக பாவகங்கள்*"
                    : "2. Query Topic & Governing Cusps*"}
                </label>
                <p className="text-[11px] text-[#64748B]">
                  {language === "ta"
                    ? "கீழ்க்கண்ட பொதுவான கேள்விகளில் ஒன்றை அழுத்தவும் அல்லது சொந்த கேள்வியை உள்ளிடவும்."
                    : "Click a standard quick question card or select topic to auto-assign primary and supporting cusps."}
                </p>
              </div>
            </div>

            {/* One-Click Presets Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {(topics.length > 0
                ? topics
                : [
                    {
                      id: "visa",
                      name_en: "Visa & Foreign Travel",
                      name_ta: "விசா & வெளிநாட்டுப் பயணம்",
                      sample_query_en: "Will I get this visa?",
                      sample_query_ta: "விசா அனுமதி கிடைக்குமா?",
                      category: "Travel",
                      primary_cusp: 12,
                      supporting_houses: [3, 9, 12],
                      denying_houses: [2, 11],
                    },
                    {
                      id: "job",
                      name_en: "Job Interview & Career",
                      name_ta: "வேலை நேர்காணல் & புதிய வேலை",
                      sample_query_en: "Will my job interview succeed?",
                      sample_query_ta: "நேர்காணலில் வெற்றி கிடைக்குமா?",
                      category: "Career",
                      primary_cusp: 6,
                      supporting_houses: [2, 6, 10, 11],
                      denying_houses: [1, 5, 9],
                    },
                    {
                      id: "court_case",
                      name_en: "Court Case & Settlement",
                      name_ta: "நீதிமன்ற வழக்கு & சட்ட தீர்வு",
                      sample_query_en: "Will this court case settle in my favor?",
                      sample_query_ta: "நீதிமன்ற வழக்கு எனக்கு சாதகமாக தீருமா?",
                      category: "Legal",
                      primary_cusp: 6,
                      supporting_houses: [1, 6, 11],
                      denying_houses: [5, 8, 12],
                    },
                    {
                      id: "marriage",
                      name_en: "Marriage Proposal",
                      name_ta: "திருமண உறுதி & வரன் அமைதல்",
                      sample_query_en: "Will this marriage proposal finalize?",
                      sample_query_ta: "இந்த வரன் திருமணமாக கைகூடுமா?",
                      category: "Relationship",
                      primary_cusp: 7,
                      supporting_houses: [2, 7, 11],
                      denying_houses: [1, 6, 10],
                    },
                    {
                      id: "property",
                      name_en: "Property Purchase",
                      name_ta: "சொத்து & வீடு வாங்குதல்",
                      sample_query_en: "Will I be able to purchase this property?",
                      sample_query_ta: "இந்த சொத்தை வாங்க முடியுமா?",
                      category: "Property",
                      primary_cusp: 4,
                      supporting_houses: [4, 11, 12],
                      denying_houses: [3, 10],
                    },
                    {
                      id: "childbirth",
                      name_en: "Childbirth & Progeny",
                      name_ta: "குழந்தைப் பேறு & புத்திர பாக்கியம்",
                      sample_query_en: "Will we be blessed with a child?",
                      sample_query_ta: "புத்திர பாக்கியம் கைகூடுமா?",
                      category: "Family",
                      primary_cusp: 5,
                      supporting_houses: [2, 5, 11],
                      denying_houses: [1, 4, 10],
                    },
                    {
                      id: "financial_gain",
                      name_en: "Financial Gain / Recovery",
                      name_ta: "பண வரவு & நிதி ஆதாயம்",
                      sample_query_en: "Will I receive money / financial gain?",
                      sample_query_ta: "எதிர்பார்த்த பணம் கைக்கு வருமா?",
                      category: "Finance",
                      primary_cusp: 11,
                      supporting_houses: [2, 6, 11],
                      denying_houses: [5, 8, 12],
                    },
                    {
                      id: "recovery",
                      name_en: "Health Recovery",
                      name_ta: "உடல் நலம் & நோய் குணமாகுதல்",
                      sample_query_en: "Will the illness be cured quickly?",
                      sample_query_ta: "நோய் விரைவில் குணமாகுமா?",
                      category: "Health",
                      primary_cusp: 11,
                      supporting_houses: [1, 5, 11],
                      denying_houses: [6, 8, 12],
                    },
                  ]
              ).map((topic) => {
                const IconComp = getTopicIcon(topic.id);
                const isSelected = selectedTopicId === topic.id;
                return (
                  <button
                    key={topic.id}
                    type="button"
                    onClick={() => handleSelectTopic(topic as HoraryTopicInfo)}
                    className={`flex items-start gap-3 p-3.5 rounded-xl border text-left transition-all ${
                      isSelected
                        ? "bg-[#FAF2DE] border-[#B8862B] ring-2 ring-[#B8862B]/30 shadow-xs"
                        : "bg-white border-[#DDE5F0] hover:border-[#B8862B]/50 hover:bg-[#FBFBFA]"
                    }`}
                  >
                    <div
                      className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                        isSelected
                          ? "bg-[#B8862B] text-white"
                          : "bg-[#F1F5F9] text-[#52667E]"
                      }`}
                    >
                      <IconComp className="w-4 h-4" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center justify-between gap-1">
                        <span className="text-xs font-bold text-[#102A4C] truncate">
                          {language === "ta" ? topic.name_ta : topic.name_en}
                        </span>
                        <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-white border border-[#DDE5F0] text-[#8C6D23]">
                          Cusp {topic.primary_cusp}
                        </span>
                      </div>
                      <p className="text-[11px] text-[#64748B] line-clamp-1 mt-0.5">
                        {language === "ta" ? topic.sample_query_ta : topic.sample_query_en}
                      </p>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Custom Question Text Input */}
            <div className="pt-2">
              <label className="block text-xs font-bold text-[#52667E] mb-1">
                {language === "ta"
                  ? "கேட்பவரின் குறிப்பிட்ட கேள்வி (Querent Question)"
                  : "Querent Exact Question / Consultation Label"}
              </label>
              <input
                type="text"
                required
                value={customQuestion}
                onChange={(e) => setCustomQuestion(e.target.value)}
                placeholder={
                  language === "ta"
                    ? "எ.கா: எனக்கு விசா அனுமதி கிடைக்குமா? அல்லது இந்த நேர்காணலில் வேலை கிடைக்குமா?"
                    : "e.g., Will I get this visa approval? / Will my job interview succeed?"
                }
                className="w-full px-3.5 py-2.5 text-sm rounded-xl border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] focus:outline-hidden text-[#102A4C]"
              />
            </div>
          </div>

          {/* Section 3: Moment & Coordinates */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
            <div className="space-y-1">
              <label className="block text-xs font-bold text-[#52667E]">
                {language === "ta" ? "கேள்வி தேதி*" : "Question Date*"}
              </label>
              <input
                type="date"
                required
                value={questionDate}
                onChange={(e) => setQuestionDate(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-lg border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] text-[#102A4C] bg-white"
              />
            </div>

            <div className="space-y-1">
              <label className="block text-xs font-bold text-[#52667E]">
                {language === "ta" ? "கேள்வி நேரம்*" : "Question Time*"}
              </label>
              <input
                type="time"
                step="1"
                required
                value={questionTime}
                onChange={(e) => setQuestionTime(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-lg border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] text-[#102A4C] bg-white"
              />
            </div>

            <div className="space-y-1">
              <label className="block text-xs font-bold text-[#52667E]">
                {language === "ta" ? "இடம் (City)*" : "Location Name*"}
              </label>
              <input
                type="text"
                required
                value={locationName}
                onChange={(e) => setLocationName(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-lg border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] text-[#102A4C] bg-white"
              />
            </div>

            <div className="space-y-1">
              <label className="block text-xs font-bold text-[#52667E]">
                {language === "ta" ? "நேர மண்டலம்*" : "Timezone*"}
              </label>
              <input
                type="text"
                required
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-lg border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] text-[#102A4C] bg-white"
              />
            </div>
          </div>

          {error && (
            <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-center gap-2">
              <XCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Predict Action Button */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center gap-2 px-8 py-3 rounded-xl text-base font-bold text-white bg-gradient-to-r from-[#B8862B] to-[#996515] hover:from-[#996515] hover:to-[#805010] shadow-md hover:shadow-lg transition-all disabled:opacity-50"
            >
              <Sparkles className="w-5 h-5" />
              <span>
                {loading
                  ? language === "ta"
                    ? "கணக்கிடப்படுகிறது..."
                    : "Computing Horary Verdict..."
                  : language === "ta"
                  ? "உடனடி பிரஸ்ன பலன் காண்க"
                  : "Reveal Instant Event Verdict"}
              </span>
            </button>
          </div>
        </form>
      </div>

      {/* ========================================================================= */}
      {/* RESULT SECTION: Immediate Verdict Card (Hero Component)                  */}
      {/* ========================================================================= */}
      {result && (
        <div id="instant-verdict-card" className="space-y-6 pt-2">
          {/* Main Hero Card */}
          <div
            className={`rounded-3xl border-2 p-6 sm:p-8 shadow-md space-y-6 transition-all ${
              result.outcome === "YES"
                ? "bg-gradient-to-br from-emerald-50/70 via-white to-amber-50/50 border-emerald-300"
                : result.outcome === "DELAYED"
                ? "bg-gradient-to-br from-amber-50/80 via-white to-yellow-50/40 border-amber-300"
                : "bg-gradient-to-br from-rose-50/70 via-white to-orange-50/40 border-rose-300"
            }`}
          >
            {/* Top Toolbar: Record Badge & Copy/Share */}
            <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-[#E2E8F0]/70">
              <div className="flex items-center gap-2.5">
                <span className="w-10 h-10 rounded-xl bg-white border border-[#DDE5F0] text-[#B8862B] font-serif font-extrabold text-lg flex items-center justify-center shadow-xs">
                  #{result.horary_number}
                </span>
                <div>
                  <h3 className="font-serif text-lg sm:text-xl font-bold text-[#102A4C]">
                    {result.question_text}
                  </h3>
                  <div className="text-xs text-[#52667E] flex flex-wrap items-center gap-2 mt-0.5">
                    <Clock className="w-3.5 h-3.5 text-[#B8862B]" />
                    <span>{new Date(result.query_timestamp).toLocaleString()}</span>
                    <span>•</span>
                    <MapPin className="w-3.5 h-3.5 text-[#B8862B]" />
                    <span>{result.location_name}</span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleCopySummary}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white border border-[#DDE5F0] text-[#1E293B] hover:bg-[#F8FAFC] transition-colors shadow-xs"
                >
                  <Copy className="w-3.5 h-3.5 text-[#B8862B]" />
                  <span>
                    {copiedSummary
                      ? language === "ta"
                        ? "நகலெடுக்கப்பட்டது!"
                        : "Copied!"
                      : language === "ta"
                      ? "நகலெடு"
                      : "Copy Verdict"}
                  </span>
                </button>

                <button
                  type="button"
                  onClick={() => window.print()}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white border border-[#DDE5F0] text-[#1E293B] hover:bg-[#F8FAFC] transition-colors shadow-xs"
                >
                  <Printer className="w-3.5 h-3.5 text-[#102A4C]" />
                  <span>{language === "ta" ? "அச்சிடு" : "Print"}</span>
                </button>
              </div>
            </div>

            {/* Verdict Hero Banner */}
            <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-6 p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs">
              <div className="flex items-center gap-4">
                <div
                  className={`w-16 h-16 rounded-2xl flex items-center justify-center shrink-0 shadow-inner ${
                    result.outcome === "YES"
                      ? "bg-emerald-100 text-emerald-700 border-2 border-emerald-300"
                      : result.outcome === "DELAYED"
                      ? "bg-amber-100 text-amber-700 border-2 border-amber-300"
                      : "bg-rose-100 text-rose-700 border-2 border-rose-300"
                  }`}
                >
                  {result.outcome === "YES" && <CheckCircle2 className="w-9 h-9" />}
                  {result.outcome === "DELAYED" && <AlertTriangle className="w-9 h-9" />}
                  {result.outcome === "NO" && <XCircle className="w-9 h-9" />}
                </div>

                <div>
                  <div className="text-xs uppercase font-extrabold tracking-wider text-[#64748B]">
                    {language === "ta" ? "தானியங்கி பிரஸ்ன தீர்ப்பு" : "Automated Horary Verdict"}
                  </div>
                  <div className="text-2xl sm:text-3xl font-extrabold font-serif tracking-tight mt-0.5">
                    {activeLangTab === "ta" ? result.outcome_label_ta : result.outcome_label_en}
                  </div>
                  <div className="text-xs text-[#52667E] mt-1">
                    {activeLangTab === "ta"
                      ? result.explanation.summary_ta
                      : result.explanation.summary_en}
                  </div>
                </div>
              </div>

              {/* Confidence Score Pill */}
              <div className="flex flex-col items-end justify-center border-t md:border-t-0 md:border-l border-[#F1F5F9] pt-4 md:pt-0 md:pl-6 shrink-0">
                <div className="text-xs text-[#64748B] font-semibold uppercase">
                  {language === "ta" ? "ஜோதிட நம்பகத்தன்மை" : "Astrological Certainty"}
                </div>
                <div className="flex items-baseline gap-1 mt-0.5">
                  <span className="text-3xl font-bold font-mono text-[#102A4C]">
                    {result.confidence_score}%
                  </span>
                </div>
                <div className="w-32 bg-gray-200 h-2 rounded-full overflow-hidden mt-1.5">
                  <div
                    className={`h-full ${
                      result.outcome === "YES"
                        ? "bg-emerald-500"
                        : result.outcome === "DELAYED"
                        ? "bg-amber-500"
                        : "bg-rose-500"
                    }`}
                    style={{ width: `${result.confidence_score}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Timing of Fructification Card */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-[#FAF6EC] to-[#F5ECE0] border border-[#D8BD80] shadow-xs space-y-4">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-[#8C6D23] text-white flex items-center justify-center">
                  <Calendar className="w-4 h-4" />
                </div>
                <h4 className="font-serif text-base font-bold text-[#102A4C]">
                  {language === "ta"
                    ? "காரிய சித்தி காலம் (Timing of Fructification)"
                    : "Timing of Fructification (Dasha & Moon Transit Trigger)"}
                </h4>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* 1. Operating Dasha Window */}
                <div className="p-4 rounded-xl bg-white border border-[#E8DFC8] space-y-2">
                  <div className="text-xs font-bold text-[#8C6D23] uppercase tracking-wider flex items-center justify-between">
                    <span>
                      {language === "ta"
                        ? "1. இயங்கும் தசா - புக்தி - அந்தரம்"
                        : "1. Operating Dasha Window"}
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#FAF2DE] text-[#8C6D23] font-mono">
                      Vimshottari
                    </span>
                  </div>
                  <div className="text-sm font-bold text-[#102A4C]">
                    {result.timing.dasha_mahadasha} Dasa • {result.timing.dasha_bhukti} Bhukti •{" "}
                    {result.timing.dasha_antara} Antara
                  </div>
                  <div className="text-xs text-[#52667E] flex items-center gap-1 font-mono">
                    <Clock className="w-3.5 h-3.5 text-[#8C6D23]" />
                    <span>
                      {result.timing.dasha_window_start} &rarr; {result.timing.dasha_window_end}
                    </span>
                  </div>
                </div>

                {/* 2. Moon Transit Window */}
                <div className="p-4 rounded-xl bg-white border border-[#E8DFC8] space-y-2">
                  <div className="text-xs font-bold text-[#2563EB] uppercase tracking-wider flex items-center justify-between">
                    <span>
                      {language === "ta"
                        ? "2. சந்திரன் பெயர்ச்சி வாயில் (Moon Transit)"
                        : "2. Moon Transit Trigger Window"}
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 font-mono">
                      Exact Trigger
                    </span>
                  </div>
                  <div className="text-sm font-bold text-[#102A4C]">
                    {activeLangTab === "ta"
                      ? `${result.timing.moon_transit_star_ta} (${result.timing.moon_transit_sign_ta})`
                      : `${result.timing.moon_transit_star} (${result.timing.moon_transit_sign})`}
                    <span className="text-xs text-[#64748B] font-normal ml-1">
                      [Lord: {result.timing.moon_transit_lord}]
                    </span>
                  </div>
                  <div className="text-xs text-[#1E293B] font-mono flex items-center gap-1">
                    <Sparkles className="w-3.5 h-3.5 text-[#B8862B]" />
                    <span>
                      {result.timing.moon_transit_start} &rarr; {result.timing.moon_transit_end}
                    </span>
                  </div>
                </div>
              </div>

              {/* Timing Narrative Box */}
              <div className="p-3.5 rounded-xl bg-white/90 border border-[#E8DFC8] text-xs text-[#102A4C] leading-relaxed">
                <strong>{language === "ta" ? "விளக்கம்: " : "Astrological Summary: "}</strong>
                {activeLangTab === "ta" ? result.timing.summary_ta : result.timing.summary_en}
              </div>
            </div>

            {/* KP Cuspal Sub-Lord & Ruling Planets Breakdown Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Box A: Primary Cusp & Sub-Lord Details */}
              <div className="p-5 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-3">
                <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-2.5">
                  <div className="text-xs font-bold text-[#102A4C] uppercase tracking-wider">
                    {language === "ta"
                      ? "முதன்மை பாவகம் & CSL தொடர்பு"
                      : "Primary Cusp & CSL Connection"}
                  </div>
                  <span className="text-xs font-bold text-[#B8862B]">
                    Cusp {result.primary_cusp}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="p-2 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                    <div className="text-[10px] text-[#64748B] uppercase">Primary Cusp Sub-Lord</div>
                    <div className="font-bold text-[#102A4C] text-sm mt-0.5">
                      {activeLangTab === "ta" ? result.cusp_sub_lord_ta : result.cusp_sub_lord}
                    </div>
                  </div>

                  <div className="p-2 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                    <div className="text-[10px] text-[#64748B] uppercase">Constellation (Star) Lord</div>
                    <div className="font-bold text-[#102A4C] text-sm mt-0.5">
                      {activeLangTab === "ta" ? result.cusp_star_lord_ta : result.cusp_star_lord}
                    </div>
                  </div>
                </div>

                {/* Supporting vs Denying Matrix */}
                <div className="space-y-2 pt-1 text-xs">
                  <div className="flex items-center justify-between p-2 rounded-lg bg-emerald-50/70 border border-emerald-200">
                    <span className="text-[#065F46] font-semibold">
                      {language === "ta" ? "ஆதரவு பாவகங்கள்:" : "Supporting Houses:"}
                    </span>
                    <span className="font-mono font-bold text-emerald-800">
                      {result.supporting_houses.join(", ")} (Hits: {result.supporting_hits.join(", ") || "None"})
                    </span>
                  </div>

                  <div className="flex items-center justify-between p-2 rounded-lg bg-rose-50/70 border border-rose-200">
                    <span className="text-[#991B1B] font-semibold">
                      {language === "ta" ? "மறுக்கும் பாவகங்கள்:" : "Denying Houses:"}
                    </span>
                    <span className="font-mono font-bold text-rose-800">
                      {result.denying_houses.join(", ")} (Hits: {result.denying_hits.join(", ") || "None"})
                    </span>
                  </div>
                </div>

                <div className="text-[11px] text-[#64748B]">
                  {result.is_csl_retrograde
                    ? "⚠️ CSL is retrograde: delay or additional effort indicated."
                    : "✅ CSL is direct: natural planetary momentum."}
                </div>
              </div>

              {/* Box B: Ruling Planets Confirmation */}
              <div className="p-5 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-3">
                <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-2.5">
                  <div className="text-xs font-bold text-[#102A4C] uppercase tracking-wider">
                    {language === "ta"
                      ? "கேள்வி நேர ஆளும் கிரகங்கள் (RPs)"
                      : "Ruling Planets Validation (RPs)"}
                  </div>
                  <span
                    className={`text-[11px] px-2 py-0.5 rounded-full font-bold ${
                      result.rp_agreement
                        ? "bg-emerald-100 text-emerald-800"
                        : "bg-amber-100 text-amber-800"
                    }`}
                  >
                    {result.rp_agreement
                      ? language === "ta"
                        ? "உறுதி செய்யப்பட்டது"
                        : "RP Confirmed"
                      : language === "ta"
                      ? "மிதமான உடன்பாடு"
                      : "Partial RP"}
                  </span>
                </div>

                <div className="space-y-1.5">
                  <div className="text-[11px] text-[#64748B]">
                    {language === "ta"
                      ? "கேள்வி கேட்ட வினாடியில் பிரபஞ்சத்தை இயக்கிய ஆளும் கிரகங்கள்:"
                      : "Planets governing the exact query moment at this latitude:"}
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {result.ruling_planets.map((p, idx) => {
                      const isMatching = result.rp_matching_planets.includes(p);
                      return (
                        <span
                          key={idx}
                          className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-bold border ${
                            isMatching
                              ? "bg-[#FAF2DE] border-[#B8862B] text-[#8C6D23] shadow-xs ring-1 ring-[#B8862B]"
                              : "bg-[#F8FAFC] border-[#E2E8F0] text-[#475569]"
                          }`}
                        >
                          <span>{p}</span>
                          {isMatching && <CheckCircle2 className="w-3 h-3 text-[#B8862B]" />}
                        </span>
                      );
                    })}
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] text-xs text-[#52667E] leading-relaxed">
                  {activeLangTab === "ta"
                    ? result.explanation.ruling_planets_ta
                    : result.explanation.ruling_planets_en}
                </div>
              </div>
            </div>

            {/* Dual-Language Detailed Astrological Explanation */}
            <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#F1F5F9] pb-3">
                <div className="flex items-center gap-2">
                  <HelpCircle className="w-5 h-5 text-[#B8862B]" />
                  <h4 className="font-serif text-base font-bold text-[#102A4C]">
                    {language === "ta"
                      ? "முழுமையான கே.பி. ஜோதிட விளக்கம்"
                      : "Transparent KP Astrological Explanation"}
                  </h4>
                </div>

                {/* English vs Tamil Toggle */}
                <div className="inline-flex rounded-xl bg-[#F1F5F9] p-1 border border-[#E2E8F0]">
                  <button
                    type="button"
                    onClick={() => setActiveLangTab("en")}
                    className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                      activeLangTab === "en"
                        ? "bg-white text-[#102A4C] shadow-xs"
                        : "text-[#64748B] hover:text-[#102A4C]"
                    }`}
                  >
                    English
                  </button>
                  <button
                    type="button"
                    onClick={() => setActiveLangTab("ta")}
                    className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                      activeLangTab === "ta"
                        ? "bg-white text-[#102A4C] shadow-xs"
                        : "text-[#64748B] hover:text-[#102A4C]"
                    }`}
                  >
                    தமிழ் (Tamil)
                  </button>
                </div>
              </div>

              {/* Content Body */}
              <div className="space-y-4 text-xs sm:text-sm text-[#1E293B] leading-relaxed">
                <div className="p-3.5 rounded-xl bg-[#FAF8F5] border border-[#E8DFC8]">
                  <h5 className="font-bold text-[#8C6D23] mb-1">
                    {activeLangTab === "ta"
                      ? "1. முதன்மை பாவகம் & லக்ன நிர்ணயம்:"
                      : "1. Primary Cusp & Ascendant Fixation:"}
                  </h5>
                  <p>
                    {activeLangTab === "ta"
                      ? result.explanation.primary_cusp_analysis_ta
                      : result.explanation.primary_cusp_analysis_en}
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-[#FAF8F5] border border-[#E8DFC8]">
                  <h5 className="font-bold text-[#8C6D23] mb-1">
                    {activeLangTab === "ta"
                      ? "2. உப-அதிபதி (CSL) பாவகத் தொடர்புகள்:"
                      : "2. Cuspal Sub-Lord (CSL) Significations:"}
                  </h5>
                  <p>
                    {activeLangTab === "ta"
                      ? result.explanation.csl_connection_ta
                      : result.explanation.csl_connection_en}
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-[#FAF8F5] border border-[#E8DFC8]">
                  <h5 className="font-bold text-[#8C6D23] mb-1">
                    {activeLangTab === "ta"
                      ? "3. காரிய சித்தி கால நிர்ணய நியதி:"
                      : "3. Timing of Fructification Logic:"}
                  </h5>
                  <p>
                    {activeLangTab === "ta"
                      ? result.explanation.timing_explanation_ta
                      : result.explanation.timing_explanation_en}
                  </p>
                </div>
              </div>
            </div>

            {/* Collapsible Deep Chart View */}
            <div className="pt-2">
              <button
                type="button"
                onClick={() => setShowFullChart(!showFullChart)}
                className="w-full flex items-center justify-between p-4 rounded-xl bg-white border border-[#DDE5F0] hover:bg-[#F8FAFC] text-xs font-bold text-[#102A4C] transition-colors"
              >
                <span>
                  {showFullChart
                    ? language === "ta"
                      ? "முழு பிரஸ்ன ஜாதக அட்டவணையை மறை"
                      : "Hide Full Horary Chart Tables"
                    : language === "ta"
                    ? "முழு பிரஸ்ன ஜாதக அட்டவணையைக் காண்க (12 பாவகங்கள் & கிரகங்கள்)"
                    : "Inspect Full Horary Chart Tables (12 Placidus Cusps & Planets)"}
                </span>
                {showFullChart ? (
                  <ChevronUp className="w-4 h-4 text-[#64748B]" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-[#64748B]" />
                )}
              </button>

              {showFullChart && (
                <div className="mt-4 p-5 rounded-2xl bg-white border border-[#DDE5F0] space-y-6">
                  {/* Cusps Table */}
                  <div className="space-y-2">
                    <h5 className="text-xs font-bold text-[#102A4C] uppercase tracking-wider">
                      {language === "ta" ? "12 பிளாசிடஸ் பாவக முனைகள்" : "12 Placidus House Cusps"}
                    </h5>
                    <div className="overflow-x-auto">
                      <table className="w-full text-xs text-left border-collapse">
                        <thead>
                          <tr className="bg-[#F8FAFC] text-[#64748B] border-b border-[#E2E8F0]">
                            <th className="p-2">Cusp</th>
                            <th className="p-2">Sign</th>
                            <th className="p-2">Degree</th>
                            <th className="p-2">Sign Lord</th>
                            <th className="p-2">Star Lord</th>
                            <th className="p-2 font-bold text-[#8C6D23]">Sub-Lord (CSL)</th>
                          </tr>
                        </thead>
                        <tbody>
                          {result.cuspal_analysis.map((c) => (
                            <tr
                              key={c.house}
                              className={`border-b border-[#F1F5F9] ${
                                c.house === result.primary_cusp ? "bg-[#FAF2DE]/60 font-bold" : ""
                              }`}
                            >
                              <td className="p-2 font-mono">
                                #{c.house}{" "}
                                {c.house === result.primary_cusp && (
                                  <span className="text-[10px] text-[#8C6D23] font-bold">
                                    [PRIMARY]
                                  </span>
                                )}
                              </td>
                              <td className="p-2">{c.sign_name}</td>
                              <td className="p-2 font-mono">{formatDms(c.cusp_degree % 30.0)}</td>
                              <td className="p-2">{c.sign_lord}</td>
                              <td className="p-2">{c.star_lord}</td>
                              <td className="p-2 font-bold text-[#8C6D23]">{c.sub_lord}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Planets Table */}
                  <div className="space-y-2">
                    <h5 className="text-xs font-bold text-[#102A4C] uppercase tracking-wider">
                      {language === "ta" ? "கேள்வி நேர கிரக நிலைகள்" : "Planetary Positions at Question Moment"}
                    </h5>
                    <div className="overflow-x-auto">
                      <table className="w-full text-xs text-left border-collapse">
                        <thead>
                          <tr className="bg-[#F8FAFC] text-[#64748B] border-b border-[#E2E8F0]">
                            <th className="p-2">Planet</th>
                            <th className="p-2">Sign</th>
                            <th className="p-2">Longitude</th>
                            <th className="p-2">Star Lord</th>
                            <th className="p-2">Sub-Lord</th>
                            <th className="p-2 font-mono">KP Sub #</th>
                          </tr>
                        </thead>
                        <tbody>
                          {result.planetary_positions.map((p) => (
                            <tr key={p.planet} className="border-b border-[#F1F5F9]">
                              <td className="p-2 font-bold text-[#102A4C]">{p.planet}</td>
                              <td className="p-2">{p.sign_name}</td>
                              <td className="p-2 font-mono">{formatDms(p.longitude % 30.0)}</td>
                              <td className="p-2">{p.star_lord}</td>
                              <td className="p-2 font-semibold text-[#8C6D23]">{p.sub_lord}</td>
                              <td className="p-2 font-mono text-[#64748B]">#{p.kp_number}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
