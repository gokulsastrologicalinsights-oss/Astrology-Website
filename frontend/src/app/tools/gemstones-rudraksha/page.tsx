"use client";

import React, { useState, useEffect, useMemo } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import {
  GemstoneAdvisoryResponse,
  GemstoneRecommendation,
  ProhibitedGemstoneItem,
  RudrakshaItem,
  RudrakshaRecommendationSummary,
} from "@/lib/types";
import { getGemstoneAdvisory, getRudrakshaMatrix, downloadGemstoneRudrakshaPlaybookPdf, triggerBlobDownload } from "@/lib/api";
import {
  Sparkles,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Info,
  CheckCircle2,
  RefreshCw,
  Compass,
  FileText,
  Lock,
  Layers,
  ArrowRight,
  Copy,
  Check,
  Search,
  Filter,
  Scale,
  Heart,
  Flame,
  Award,
  Download,
} from "lucide-react";

const LAGNA_LIST = [
  "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
];

const LAGNA_TAMIL: Record<string, string> = {
  Aries: "மேஷம் (Aries)",
  Taurus: "ரிஷபம் (Taurus)",
  Gemini: "மிதுனம் (Gemini)",
  Cancer: "கடகம் (Cancer)",
  Leo: "சிம்மம் (Leo)",
  Virgo: "கன்னி (Virgo)",
  Libra: "துலாம் (Libra)",
  Scorpio: "விருச்சிகம் (Scorpio)",
  Sagittarius: "தனுசு (Sagittarius)",
  Capricorn: "மகரம் (Capricorn)",
  Aquarius: "கும்பம் (Aquarius)",
  Pisces: "மீனம் (Pisces)",
};

const GRAHA_COLORS: Record<string, { bg: string; border: string; text: string; badge: string }> = {
  sun: { bg: "bg-amber-50", border: "border-amber-300", text: "text-amber-900", badge: "bg-amber-100 text-amber-800" },
  moon: { bg: "bg-slate-50", border: "border-slate-300", text: "text-slate-900", badge: "bg-slate-100 text-slate-800" },
  mars: { bg: "bg-red-50", border: "border-red-300", text: "text-red-900", badge: "bg-red-100 text-red-800" },
  mercury: { bg: "bg-emerald-50", border: "border-emerald-300", text: "text-emerald-900", badge: "bg-emerald-100 text-emerald-800" },
  jupiter: { bg: "bg-yellow-50", border: "border-yellow-300", text: "text-yellow-900", badge: "bg-yellow-100 text-yellow-800" },
  venus: { bg: "bg-purple-50", border: "border-purple-300", text: "text-purple-900", badge: "bg-purple-100 text-purple-800" },
  saturn: { bg: "bg-blue-50", border: "border-blue-300", text: "text-blue-900", badge: "bg-blue-100 text-blue-800" },
  rahu: { bg: "bg-stone-50", border: "border-stone-300", text: "text-stone-900", badge: "bg-stone-100 text-stone-800" },
  ketu: { bg: "bg-orange-50", border: "border-orange-300", text: "text-orange-900", badge: "bg-orange-100 text-orange-800" },
  all: { bg: "bg-indigo-50", border: "border-indigo-300", text: "text-indigo-900", badge: "bg-indigo-100 text-indigo-800" },
};

export default function GemstoneRudrakshaStudioPage() {
  const { language } = useLanguage();
  const isTa = language === "ta";

  const [selectedLagna, setSelectedLagna] = useState<string>("Leo");
  const [bodyWeight, setBodyWeight] = useState<number>(68);
  const [activeTab, setActiveTab] = useState<"anukula" | "gemstones" | "prohibitions" | "rudraksha">("gemstones");
  const [advisory, setAdvisory] = useState<GemstoneAdvisoryResponse | null>(null);
  const [rudrakshaCatalog, setRudrakshaCatalog] = useState<RudrakshaItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [copiedMantra, setCopiedMantra] = useState<string | null>(null);
  const [downloadingPdf, setDownloadingPdf] = useState<boolean>(false);

  const handleDownloadPdf = async () => {
    setDownloadingPdf(true);
    try {
      const blob = await downloadGemstoneRudrakshaPlaybookPdf({
        ascendant_sign: selectedLagna,
        native_name: "Native",
        body_weight_kg: bodyWeight,
        language: isTa ? "ta" : "en",
      });
      triggerBlobDownload(blob, `Gemstone_Rudraksha_Playbook_${selectedLagna}.pdf`);
    } catch (err: any) {
      alert(err?.message || "Failed to download Gemstone & Rudraksha Playbook PDF.");
    } finally {
      setDownloadingPdf(false);
    }
  };

  // Rudraksha catalog filters
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedGrahaFilter, setSelectedGrahaFilter] = useState<string>("all");

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError(null);
      try {
        const advRes = await getGemstoneAdvisory({
          ascendant_sign: selectedLagna,
          body_weight_kg: bodyWeight,
        });
        setAdvisory(advRes);

        if (advRes.rudraksha_catalog && advRes.rudraksha_catalog.length > 0) {
          setRudrakshaCatalog(advRes.rudraksha_catalog);
        } else {
          const catRes = await getRudrakshaMatrix();
          setRudrakshaCatalog(catRes.items || []);
        }
      } catch (err: any) {
        setError(err?.message || "Failed to load gemstone & rudraksha data.");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [selectedLagna, bodyWeight]);

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedMantra(id);
    setTimeout(() => setCopiedMantra(null), 2500);
  };

  const filteredRudraksha = useMemo(() => {
    return rudrakshaCatalog.filter((item) => {
      const matchesSearch =
        item.name_en.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.name_ta.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.ruling_deity_en.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.astrological_benefits_en.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesGraha =
        selectedGrahaFilter === "all" || item.ruling_graha === selectedGrahaFilter;

      return matchesSearch && matchesGraha;
    });
  }, [rudrakshaCatalog, searchQuery, selectedGrahaFilter]);

  return (
    <div className="min-h-screen bg-[#FDFBF7] py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Navigation Breadcrumb */}
        <div className="flex items-center gap-2 text-sm text-[#735118]">
          <Link href="/tools" className="hover:underline flex items-center gap-1">
            <Compass className="w-4 h-4" />
            {isTa ? "ஜோதிடக் கருவிகள்" : "Astrological Tools"}
          </Link>
          <span>/</span>
          <span className="font-semibold text-[#8B6914]">
            {isTa ? "ரத்தினம் & ருத்ராட்ச ஆலோசனை" : "Gemstone & Rudraksha Studio"}
          </span>
        </div>

        {/* Studio Header & Lagna Selector Bar */}
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-stone-200/80 shadow-md">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#FAF2DE] border border-[#B4872B]/30 text-xs font-bold text-[#8B6914] uppercase tracking-wider">
                <Sparkles className="w-3.5 h-3.5" />
                {isTa ? "பாரம்பரிய ரத்தின & ருத்ராட்ச சாஸ்திரம்" : "Classical Ratna & Rudraksha Shastra"}
              </div>
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold font-serif text-[#153F6B]">
                {isTa
                  ? "ரத்தினம் & ருத்ராட்ச பரிந்துரை மையம்"
                  : "Remedial Gemstone & Rudraksha Recommendation Engine"}
              </h1>
              <p className="text-sm sm:text-base text-stone-600 max-w-3xl">
                {isTa
                  ? "அனுகூல ரத்தின முறை, பிரதிகூல சாந்தி முறை, 1 முதல் 14 முக ருத்ராட்சப் பொருத்தம், மற்றும் உடல் எடையிலான சரியான ரட்டி/காரட் அளவீடு."
                  : "Authentic Anukula vs Pratikula evaluation, Yogakaraka support stones, 1-to-14 Mukhi Rudraksha compatibility matrix, and body-weight proportional weight formulas."}
              </p>
            </div>

            {/* Quick Selectors */}
            <div className="flex flex-wrap items-center gap-4 bg-stone-50 p-4 rounded-2xl border border-stone-200">
              <div>
                <label className="block text-xs font-bold text-stone-600 uppercase mb-1">
                  {isTa ? "லக்னம் (Ascendant)" : "Ascendant (Lagna)"}
                </label>
                <select
                  value={selectedLagna}
                  onChange={(e) => setSelectedLagna(e.target.value)}
                  className="bg-white border border-stone-300 rounded-xl px-3 py-2 text-sm font-semibold text-[#153F6B] focus:ring-2 focus:ring-[#8B6914] outline-none"
                >
                  {LAGNA_LIST.map((sign) => (
                    <option key={sign} value={sign}>
                      {isTa ? LAGNA_TAMIL[sign] || sign : sign}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-stone-600 uppercase mb-1 flex items-center gap-1">
                  <Scale className="w-3.5 h-3.5 text-[#8B6914]" />
                  {isTa ? "உடல் எடை (Body Weight)" : "Body Weight (kg)"}
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    min={35}
                    max={150}
                    value={bodyWeight}
                    onChange={(e) => setBodyWeight(Number(e.target.value))}
                    className="w-20 bg-white border border-stone-300 rounded-xl px-2.5 py-2 text-sm font-semibold text-center text-[#153F6B] focus:ring-2 focus:ring-[#8B6914] outline-none"
                  />
                  <span className="text-xs font-bold text-stone-500">kg</span>
                </div>
              </div>

              <div>
                <button
                  type="button"
                  onClick={handleDownloadPdf}
                  disabled={downloadingPdf}
                  className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#8B6914] hover:bg-[#735118] text-white text-xs font-bold shadow-xs transition-all cursor-pointer mt-4"
                >
                  <Download className={`w-4 h-4 ${downloadingPdf ? "animate-spin" : ""}`} />
                  <span>
                    {downloadingPdf
                      ? (isTa ? "தயாராகிறது..." : "Compiling Playbook...")
                      : (isTa ? "பரிந்துரை கையேடு PDF" : "Download Playbook PDF")}
                  </span>
                </button>
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-6 pt-6 border-t border-stone-100">
            <button
              onClick={() => setActiveTab("gemstones")}
              className={`flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-sm font-bold transition-all ${
                activeTab === "gemstones"
                  ? "bg-[#153F6B] text-white shadow"
                  : "bg-stone-50 text-stone-700 hover:bg-stone-100"
              }`}
            >
              <Sparkles className="w-4 h-4 text-[#DDA74F]" />
              <span>{isTa ? "சுப ரத்தினங்கள் (3+1 தூண்கள்)" : "Auspicious Gemstones (3+1)"}</span>
            </button>

            <button
              onClick={() => setActiveTab("anukula")}
              className={`flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-sm font-bold transition-all ${
                activeTab === "anukula"
                  ? "bg-[#153F6B] text-white shadow"
                  : "bg-stone-50 text-stone-700 hover:bg-stone-100"
              }`}
            >
              <Layers className="w-4 h-4 text-[#DDA74F]" />
              <span>{isTa ? "அனுகூல vs பிரதிகூல விதி" : "Anukula vs Pratikula"}</span>
            </button>

            <button
              onClick={() => setActiveTab("prohibitions")}
              className={`flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-sm font-bold transition-all ${
                activeTab === "prohibitions"
                  ? "bg-[#153F6B] text-white shadow"
                  : "bg-stone-50 text-stone-700 hover:bg-stone-100"
              }`}
            >
              <ShieldAlert className="w-4 h-4 text-rose-500" />
              <span>{isTa ? "கண்டிப்பான தடைகள்" : "Strict Prohibitions"}</span>
            </button>

            <button
              onClick={() => setActiveTab("rudraksha")}
              className={`flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-sm font-bold transition-all ${
                activeTab === "rudraksha"
                  ? "bg-[#153F6B] text-white shadow"
                  : "bg-stone-50 text-stone-700 hover:bg-stone-100"
              }`}
            >
              <Flame className="w-4 h-4 text-amber-500" />
              <span>{isTa ? "1-14 முக ருத்ராட்ச மையம்" : "1-to-14 Mukhi Rudraksha"}</span>
            </button>
          </div>
        </div>

        {/* Loading Spinner */}
        {loading && (
          <div className="bg-white rounded-3xl p-12 text-center border border-stone-200">
            <RefreshCw className="w-8 h-8 text-[#8B6914] animate-spin mx-auto mb-3" />
            <p className="text-stone-600 font-medium">
              {isTa ? "ரத்தின மற்றும் ருத்ராட்ச தரவுகள் கணக்கிடப்படுகின்றன..." : "Auditing classical gemological & rudraksha canons..."}
            </p>
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <div className="bg-rose-50 border border-rose-200 text-rose-800 p-4 rounded-2xl flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
            <p className="text-sm font-medium">{error}</p>
          </div>
        )}

        {/* Tab 1: Auspicious Gemstones (3 Pillars + Secondary Support) */}
        {!loading && advisory && activeTab === "gemstones" && (
          <div className="space-y-6">
            {/* Body Weight Calculation Note */}
            <div className="bg-gradient-to-r from-amber-500/10 via-amber-400/5 to-transparent border-l-4 border-amber-600 p-4 rounded-r-2xl flex items-start gap-3">
              <Scale className="w-5 h-5 text-amber-700 flex-shrink-0 mt-0.5" />
              <div className="text-sm">
                <span className="font-bold text-amber-900">
                  {isTa ? "ஆயுர்வேத/ஜோதிட எடை விதி:" : "Ayurvedic & Jyotish Weight Formula:"}
                </span>{" "}
                <span className="text-amber-800">
                  {isTa
                    ? `உங்கள் உடல் எடை ${bodyWeight} கிலோவிற்கு, குறைந்தபட்சம் ${(bodyWeight / 10).toFixed(1)} ரட்டி (சுமார் ${((bodyWeight / 10) * 0.91).toFixed(2)} காரட்) எடையுள்ள ரத்தினம் உகந்தது.`
                    : `For body weight of ${bodyWeight} kg, the classical formula (1 Ratti per 10 kg) mandates at least ${(bodyWeight / 10).toFixed(1)} Rattis (approx ${((bodyWeight / 10) * 0.91).toFixed(2)} Carats / ${Math.round((bodyWeight / 10) * 0.91 * 200)} mg).`}
                </span>
              </div>
            </div>

            {/* Gemstone Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Pillar 1: Life Stone */}
              <GemstoneCard
                rec={advisory.life_stone}
                badgeText={isTa ? "1-ஆம் அதிபதி (உயிர் பலம்)" : "1st Lord (Vitality)"}
                isTa={isTa}
                onCopyMantra={copyToClipboard}
                copiedMantraId={copiedMantra}
              />

              {/* Pillar 2: Lucky Stone */}
              <GemstoneCard
                rec={advisory.lucky_stone}
                badgeText={isTa ? "5-ஆம் அதிபதி (புண்ணியம்)" : "5th Lord (Punya)"}
                isTa={isTa}
                onCopyMantra={copyToClipboard}
                copiedMantraId={copiedMantra}
              />

              {/* Pillar 3: Fortune Stone */}
              <GemstoneCard
                rec={advisory.fortune_stone}
                badgeText={isTa ? "9-ஆம் அதிபதி (பாக்கியம்)" : "9th Lord (Bhagya)"}
                isTa={isTa}
                onCopyMantra={copyToClipboard}
                copiedMantraId={copiedMantra}
              />

              {/* Pillar 4: Secondary Support Stone (Yogakaraka or Dasha Lord) */}
              {advisory.secondary_support_stone ? (
                <GemstoneCard
                  rec={advisory.secondary_support_stone}
                  badgeText={isTa ? "யோககாரகன் / தசா நாதன்" : "Yogakaraka Support"}
                  isTa={isTa}
                  onCopyMantra={copyToClipboard}
                  copiedMantraId={copiedMantra}
                  isSecondary
                />
              ) : (
                <div className="bg-white p-6 rounded-3xl border border-dashed border-stone-300 flex flex-col items-center justify-center text-center text-stone-500 space-y-3">
                  <Award className="w-10 h-10 text-stone-400" />
                  <h4 className="font-bold text-stone-700">
                    {isTa ? "மூன்று தூண் போதுமானது" : "3-Pillars Are Fully Sufficient"}
                  </h4>
                  <p className="text-xs text-stone-500 max-w-sm">
                    {isTa
                      ? `${selectedLagna} லக்னத்திற்கு தனிப்பட்ட யோககாரகன் இல்லாததால், மேற்கண்ட 3 முதன்மை ரத்தினங்களே முழுமையான நன்மைகளை வழங்கும்.`
                      : `For ${selectedLagna} Lagna, the primary 3-pillar trio provides comprehensive planetary alignment without requiring an additional stone.`}
                  </p>
                </div>
              )}
            </div>

            {/* General Wearing Mandate */}
            <div className="bg-stone-50 border border-stone-200 rounded-3xl p-6">
              <h3 className="text-base font-bold text-[#153F6B] flex items-center gap-2 mb-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                {isTa ? "ரத்தினம் அணியும் பொதுவான நெறிமுறைகள்" : "General Classical Wearing Protocols"}
              </h3>
              <ul className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-stone-700">
                {(isTa ? advisory.general_wearing_rules_ta : advisory.general_wearing_rules_en).map((rule, idx) => (
                  <li key={idx} className="flex items-start gap-2 bg-white p-3 rounded-xl border border-stone-150">
                    <span className="w-5 h-5 rounded-full bg-[#FAF2DE] text-[#8B6914] text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                      {idx + 1}
                    </span>
                    <span>{rule}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Tab 2: Anukula vs Pratikula Doctrine Matrix */}
        {!loading && advisory && activeTab === "anukula" && (
          <div className="space-y-6">
            <div className="bg-white p-6 sm:p-8 rounded-3xl border border-stone-200 shadow-sm space-y-6">
              <div>
                <span className="text-xs font-bold text-[#8B6914] uppercase tracking-wider bg-[#FAF2DE] px-3 py-1 rounded-full">
                  {isTa ? "வேத ஜோதிட அடிப்படை தத்துவம்" : "Foundational Shastric Principle"}
                </span>
                <h2 className="text-xl sm:text-2xl font-bold font-serif text-[#153F6B] mt-2">
                  {isTa ? "அனுகூல ரத்தின முறை vs பிரதிகூல சாந்தி முறை" : "Anukula (Amplification) vs Pratikula (Pacification)"}
                </h2>
                <p className="text-sm text-stone-500 mt-1">
                  {isTa ? "பிருஹத் சம்ஹிதை மற்றும் கருட புராணத்தின் அதிகாரப்பூர்வ விதி" : "Authorized by Brihat Samhita (Ch. 80), Garuda Purana & Mani Mala"}
                </p>
              </div>

              {/* Comparison Hero Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Anukula Card */}
                <div className="bg-emerald-50/70 border border-emerald-200 rounded-2xl p-5 space-y-3">
                  <div className="flex items-center gap-2 text-emerald-800 font-bold text-base">
                    <Sparkles className="w-5 h-5 text-emerald-600" />
                    <span>{isTa ? "அனுகூல வாதம் (சுப கிரக வலுவூட்டல்)" : "Anukula Vada (Benefic Strengthening)"}</span>
                  </div>
                  <p className="text-xs text-emerald-950 leading-relaxed">
                    {isTa
                      ? "ரத்தினங்கள் வானியல் மின்காந்த கதிர்வீச்சை ஈர்த்து உடலின் ஆரா மண்டலத்திற்குள் பாய்ச்சும் பெருக்கிகள் (Amplifiers). அவை சுப கிரகங்களின் நற்கதிர்களை உடலில் அதிகப்படுத்த மட்டுமே பயன்பட வேண்டும்."
                      : "Gemstones act as cosmic crystalline prisms that capture and transmit planetary radiation into your bio-magnetic aura. They ALWAYS amplify planetary potency and cannot appease hostile forces."}
                  </p>
                  <div className="bg-white/80 p-3 rounded-xl border border-emerald-150 text-xs text-emerald-900 font-medium">
                    <strong className="block text-emerald-950 font-bold mb-1">
                      {isTa ? "பரிந்துரைக்கப்படும் நிலை:" : "Strict Prescription:"}
                    </strong>
                    {isTa
                      ? "லக்னாதிபதி, 5-ஆம் அதிபதி, 9-ஆம் அதிபதி மற்றும் யோககாரகர்கள் மட்டுமே ரத்தினம் அணிய தகுதியானவர்கள்."
                      : "Strictly limited to the 1st Lord (Lagna), 5th Lord (Punya), 9th Lord (Bhagya), and undisputed Yogakarakas."}
                  </div>
                </div>

                {/* Pratikula Card */}
                <div className="bg-amber-50/70 border border-amber-200 rounded-2xl p-5 space-y-3">
                  <div className="flex items-center gap-2 text-amber-800 font-bold text-base">
                    <Flame className="w-5 h-5 text-amber-600" />
                    <span>{isTa ? "பிரதிகூல சாந்தி (பாப கிரக அமைதிப்படுத்துதல்)" : "Pratikula Shanti (Malefic Pacification)"}</span>
                  </div>
                  <p className="text-xs text-amber-950 leading-relaxed">
                    {isTa
                      ? "பாதக, மாரக அல்லது மறைவு ஸ்தான கிரகங்களுக்கு ஒருபோதும் ரத்தினங்களை அணியக்கூடாது; ஏனெனில் ரத்தினம் அவற்றின் தீய கதிர்வீச்சையும் பெருக்கிவிடும்! அவற்றுக்கு அமைதிப்படுத்தும் பரிகாரங்கள் மட்டுமே தேவை."
                      : "Malefic, afflicted, or Dusthana planets (6th, 8th, 12th lords) must NEVER be energized with gemstones. Doing so magnifies disease, litigation, and distress. They must be pacified through bio-calming remedies."}
                  </p>
                  <div className="bg-white/80 p-3 rounded-xl border border-amber-150 text-xs text-amber-900 font-medium">
                    <strong className="block text-amber-950 font-bold mb-1">
                      {isTa ? "பரிந்துரைக்கப்படும் பரிகாரங்கள்:" : "Authorized Non-Amplifying Remedies:"}
                    </strong>
                    {isTa
                      ? "உகந்த ருத்ராட்ச மணிகள், மூல மந்திர ஜெபம், தானங்கள் மற்றும் நவதிருப்பதி/நவக்கிரக கோவில் அர்ச்சனை."
                      : "Authentic Rudraksha Beads, Moola Mantra Japa (108x), Daana (charity), and Sthala Yatra worship."}
                  </div>
                </div>
              </div>

              {/* Core Philosophy Text */}
              <div className="bg-stone-50 p-5 rounded-2xl border border-stone-200 text-sm text-stone-700 leading-relaxed">
                <p>
                  {isTa
                    ? advisory.anukula_vs_pratikula_doctrine_ta?.core_principle
                    : advisory.anukula_vs_pratikula_doctrine_en?.core_principle}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Strict Prohibitions & Incompatible Gemstones */}
        {!loading && advisory && activeTab === "prohibitions" && (
          <div className="space-y-6">
            {/* Prohibited Dusthana Cards */}
            <div className="bg-white p-6 sm:p-8 rounded-3xl border border-stone-200 shadow-sm space-y-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-rose-100 text-rose-700 flex items-center justify-center flex-shrink-0">
                  <ShieldAlert className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-xl font-bold font-serif text-[#153F6B]">
                    {isTa ? "மறைவு ஸ்தானங்களால் தடை செய்யப்பட்ட ரத்தினங்கள்" : "Strictly Prohibited Gemstones (Dusthana Rulers)"}
                  </h3>
                  <p className="text-xs text-stone-500">
                    {isTa
                      ? `${selectedLagna} லக்னத்திற்கு 6, 8, 12-ஆம் வீடுகளை ஆட்சி செய்வதால் இவற்றை அணிவது கடுமையான தோஷங்களை ஏற்படுத்தும்.`
                      : `Planets ruling the 6th (debts/disease), 8th (obstacles), and 12th (losses) for ${selectedLagna} Lagna.`}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {advisory.prohibited_gemstones.map((item, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-2xl border border-rose-200 bg-rose-50/50 space-y-3"
                  >
                    <div className="flex items-center justify-between">
                      <div className="font-bold text-rose-950 text-sm">
                        {isTa ? item.primary_gem_ta : item.primary_gem_en}
                      </div>
                      <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-rose-200 text-rose-800">
                        {isTa ? item.graha_name_ta : item.graha_name_en}
                      </span>
                    </div>

                    <p className="text-xs text-rose-900 leading-relaxed">
                      {isTa ? item.reason_ta : item.reason_en}
                    </p>

                    <div className="bg-white/80 p-2.5 rounded-xl border border-rose-150 text-xs text-rose-800">
                      <strong className="block text-rose-950 font-semibold mb-0.5">
                        {isTa ? "பாதுகாப்பான மாற்று வழி:" : "Safe Classical Alternative:"}
                      </strong>
                      {isTa ? item.safe_alternative_ta : item.safe_alternative_en}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Incompatible Conflict Matrix */}
            <div className="bg-white p-6 sm:p-8 rounded-3xl border border-stone-200 shadow-sm space-y-4">
              <h3 className="text-lg font-bold font-serif text-[#153F6B] flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-amber-600" />
                {isTa ? "பகை கிரக ரத்தின முரண்பாடுகள் (ஒன்றாக அணியக் கூடாதவை)" : "Planetary Conflict Guard (Never Combine)"}
              </h3>
              <ul className="space-y-2 text-sm text-stone-700">
                {(isTa ? advisory.conflicting_combinations_warning_ta : advisory.conflicting_combinations_warning_en).map((warn, idx) => (
                  <li key={idx} className="flex items-start gap-2 bg-amber-50/60 p-3 rounded-xl border border-amber-200/60">
                    <span className="text-amber-700 font-bold">•</span>
                    <span>{warn}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Tab 4: 1-to-14 Mukhi Rudraksha Compatibility Studio */}
        {!loading && advisory && activeTab === "rudraksha" && (
          <div className="space-y-8">
            {/* Personalized Rudraksha Recommendation Hero */}
            {advisory.recommended_rudraksha && (
              <div className="bg-gradient-to-br from-[#153F6B] via-[#1E4D7B] to-[#122E4E] text-white p-6 sm:p-8 rounded-3xl shadow-lg space-y-6">
                <div>
                  <span className="text-xs font-bold text-[#F4D068] uppercase tracking-wider bg-white/10 px-3 py-1 rounded-full">
                    {isTa ? "தனிப்பயன் ருத்ராட்ச பொருத்தம்" : "Personalized Astrological Prescription"}
                  </span>
                  <h3 className="text-xl sm:text-2xl font-bold font-serif mt-2">
                    {isTa
                      ? `${selectedLagna} லக்னத்திற்கான பிரத்யேக ருத்ராட்சப் பரிந்துரை`
                      : `Recommended Rudraksha Combination for ${selectedLagna} Lagna`}
                  </h3>
                  <p className="text-sm text-blue-100 max-w-2xl mt-1">
                    {isTa
                      ? advisory.recommended_rudraksha.personal_alignment_reason_ta
                      : advisory.recommended_rudraksha.personal_alignment_reason_en}
                  </p>
                </div>

                {/* Recommended Beads Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Primary Bead */}
                  <div className="bg-white/10 backdrop-blur-sm p-4 rounded-2xl border border-white/15 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-[#F4D068] uppercase">
                        {isTa ? "முதன்மை ருத்ராட்சம்" : "Primary Prescription"}
                      </span>
                      <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full font-bold">
                        {advisory.recommended_rudraksha.primary_bead.mukhi} Mukhi
                      </span>
                    </div>
                    <h4 className="font-bold text-base">
                      {isTa
                        ? advisory.recommended_rudraksha.primary_bead.name_ta
                        : advisory.recommended_rudraksha.primary_bead.name_en}
                    </h4>
                    <p className="text-xs text-blue-100">
                      <strong>{isTa ? "அதிபதி:" : "Deity:"}</strong>{" "}
                      {isTa
                        ? advisory.recommended_rudraksha.primary_bead.ruling_deity_ta
                        : advisory.recommended_rudraksha.primary_bead.ruling_deity_en}
                    </p>
                    <div className="text-xs bg-black/20 p-2 rounded-lg font-mono text-[#F4D068]">
                      {advisory.recommended_rudraksha.primary_bead.beeja_mantra_sanskrit}
                    </div>
                  </div>

                  {/* Secondary Bead */}
                  {advisory.recommended_rudraksha.secondary_bead && (
                    <div className="bg-white/10 backdrop-blur-sm p-4 rounded-2xl border border-white/15 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-[#F4D068] uppercase">
                          {isTa ? "துணை ருத்ராட்சம்" : "Secondary Support"}
                        </span>
                        <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full font-bold">
                          {advisory.recommended_rudraksha.secondary_bead.mukhi} Mukhi
                        </span>
                      </div>
                      <h4 className="font-bold text-base">
                        {isTa
                          ? advisory.recommended_rudraksha.secondary_bead.name_ta
                          : advisory.recommended_rudraksha.secondary_bead.name_en}
                      </h4>
                      <p className="text-xs text-blue-100">
                        <strong>{isTa ? "அதிபதி:" : "Deity:"}</strong>{" "}
                        {isTa
                          ? advisory.recommended_rudraksha.secondary_bead.ruling_deity_ta
                          : advisory.recommended_rudraksha.secondary_bead.ruling_deity_en}
                      </p>
                      <div className="text-xs bg-black/20 p-2 rounded-lg font-mono text-[#F4D068]">
                        {advisory.recommended_rudraksha.secondary_bead.beeja_mantra_sanskrit}
                      </div>
                    </div>
                  )}

                  {/* Universal Bead */}
                  <div className="bg-white/10 backdrop-blur-sm p-4 rounded-2xl border border-white/15 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-[#F4D068] uppercase">
                        {isTa ? "பொதுக் கவசம்" : "Universal Shield"}
                      </span>
                      <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full font-bold">
                        5 Mukhi
                      </span>
                    </div>
                    <h4 className="font-bold text-base">
                      {isTa
                        ? advisory.recommended_rudraksha.universal_bead.name_ta
                        : advisory.recommended_rudraksha.universal_bead.name_en}
                    </h4>
                    <p className="text-xs text-blue-100">
                      <strong>{isTa ? "அதிபதி:" : "Deity:"}</strong>{" "}
                      {isTa
                        ? advisory.recommended_rudraksha.universal_bead.ruling_deity_ta
                        : advisory.recommended_rudraksha.universal_bead.ruling_deity_en}
                    </p>
                    <div className="text-xs bg-black/20 p-2 rounded-lg font-mono text-[#F4D068]">
                      {advisory.recommended_rudraksha.universal_bead.beeja_mantra_sanskrit}
                    </div>
                  </div>
                </div>

                {/* Wearing Instructions */}
                <div className="border-t border-white/15 pt-4">
                  <h5 className="text-xs font-bold text-[#F4D068] uppercase tracking-wider mb-2">
                    {isTa ? "ருத்ராட்சம் அணியும் முறை & தூய்மை விதி" : "Prana Pratishtha & Wearing Protocols"}
                  </h5>
                  <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-blue-100">
                    {(isTa
                      ? advisory.recommended_rudraksha.wearing_instructions_ta
                      : advisory.recommended_rudraksha.wearing_instructions_en
                    ).map((ins, idx) => (
                      <li key={idx} className="flex items-start gap-1.5">
                        <span className="text-[#F4D068] font-bold">✓</span>
                        <span>{ins}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Complete 1-to-14 Mukhi Catalogue */}
            <div className="bg-white p-6 sm:p-8 rounded-3xl border border-stone-200 shadow-sm space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <h3 className="text-xl font-bold font-serif text-[#153F6B]">
                    {isTa ? "1 முதல் 14 முக ருத்ராட்ச விரிவான அட்டவணை" : "Complete 1-to-14 Mukhi Rudraksha Catalogue"}
                  </h3>
                  <p className="text-xs text-stone-500">
                    {isTa
                      ? "சிவபுராணம் மற்றும் தேவி பாகவதத்தின்படி அனைத்து மணிகளின் தாத்பரியம் மற்றும் தோஷ நிவர்த்தி."
                      : "Classical database based on Shiva Purana, Padma Purana, and Shrimad Devi Bhagavatam."}
                  </p>
                </div>

                {/* Search & Filters */}
                <div className="flex flex-wrap items-center gap-3">
                  <div className="relative">
                    <Search className="w-4 h-4 text-stone-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                      type="text"
                      placeholder={isTa ? "தேடுக..." : "Search beads, deities..."}
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-9 pr-3 py-1.5 bg-stone-50 border border-stone-300 rounded-xl text-xs text-stone-800 outline-none focus:ring-2 focus:ring-[#8B6914]"
                    />
                  </div>

                  <select
                    value={selectedGrahaFilter}
                    onChange={(e) => setSelectedGrahaFilter(e.target.value)}
                    className="py-1.5 px-3 bg-stone-50 border border-stone-300 rounded-xl text-xs font-semibold text-stone-700 outline-none focus:ring-2 focus:ring-[#8B6914]"
                  >
                    <option value="all">{isTa ? "அனைத்து கிரகங்களும்" : "All Grahas"}</option>
                    <option value="sun">{isTa ? "சூரியன் (Sun)" : "Sun"}</option>
                    <option value="moon">{isTa ? "சந்திரன் (Moon)" : "Moon"}</option>
                    <option value="mars">{isTa ? "செவ்வாய் (Mars)" : "Mars"}</option>
                    <option value="mercury">{isTa ? "புதன் (Mercury)" : "Mercury"}</option>
                    <option value="jupiter">{isTa ? "குரு (Jupiter)" : "Jupiter"}</option>
                    <option value="venus">{isTa ? "சுக்கிரன் (Venus)" : "Venus"}</option>
                    <option value="saturn">{isTa ? "சனி (Saturn)" : "Saturn"}</option>
                    <option value="rahu">{isTa ? "ராகு (Rahu)" : "Rahu"}</option>
                    <option value="ketu">{isTa ? "கேது (Ketu)" : "Ketu"}</option>
                  </select>
                </div>
              </div>

              {/* Catalogue Cards Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredRudraksha.map((bead) => (
                  <RudrakshaCard
                    key={bead.name_en}
                    bead={bead}
                    isTa={isTa}
                    onCopyMantra={copyToClipboard}
                    copiedMantraId={copiedMantra}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Sub-Component: Gemstone Recommendation Card ─────────────────────────────

interface GemstoneCardProps {
  rec: GemstoneRecommendation;
  badgeText: string;
  isTa: boolean;
  onCopyMantra: (text: string, id: string) => void;
  copiedMantraId: string | null;
  isSecondary?: boolean;
}

function GemstoneCard({
  rec,
  badgeText,
  isTa,
  onCopyMantra,
  copiedMantraId,
  isSecondary = false,
}: GemstoneCardProps) {
  const colorTheme = GRAHA_COLORS[rec.graha] || GRAHA_COLORS.sun;

  return (
    <div
      className={`rounded-3xl border ${colorTheme.border} ${colorTheme.bg} p-6 shadow-sm flex flex-col justify-between space-y-5 transition-all hover:shadow-md`}
    >
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between gap-2">
          <span
            className={`text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider ${colorTheme.badge}`}
          >
            {badgeText}
          </span>
          <span className="text-xs font-semibold text-stone-500">
            {isTa ? rec.graha_name_ta : rec.graha_name_en}
          </span>
        </div>

        <div>
          <h3 className="text-xl font-bold font-serif text-[#153F6B]">
            {isTa ? rec.primary_gem_ta : rec.primary_gem_en}
          </h3>
          <p className="text-xs font-mono text-[#8B6914] mt-0.5">
            {rec.primary_gem_sanskrit}
          </p>
          <p className="text-xs text-stone-600 mt-2 leading-relaxed">
            {isTa ? rec.governing_purpose_ta : rec.governing_purpose_en}
          </p>
        </div>

        {/* Specifications Grid */}
        <div className="grid grid-cols-2 gap-3 text-xs bg-white/80 p-4 rounded-2xl border border-stone-200/80">
          <div>
            <span className="text-stone-500 block">{isTa ? "பரிந்துரை உலோகம்:" : "Prescribed Metal:"}</span>
            <strong className="text-stone-800">
              {isTa ? rec.prescribed_metal_ta : rec.prescribed_metal_en}
            </strong>
          </div>
          <div>
            <span className="text-stone-500 block">{isTa ? "அணியும் விரல்:" : "Ideal Finger:"}</span>
            <strong className="text-stone-800">
              {isTa ? rec.ideal_finger_ta : rec.ideal_finger_en}
            </strong>
          </div>
          <div>
            <span className="text-stone-500 block">{isTa ? "குறைந்தபட்ச எடை:" : "Min. Weight:"}</span>
            <strong className="text-stone-800">
              {rec.minimum_rattis ? `${rec.minimum_rattis} Ratti / ` : ""}
              {rec.minimum_carats} Carats
            </strong>
          </div>
          <div>
            <span className="text-stone-500 block">{isTa ? "சுப தினம்/ஓரை:" : "Auspicious Day/Hora:"}</span>
            <strong className="text-stone-800 line-clamp-1">
              {isTa ? rec.energization_day_ta : rec.energization_day_en}
            </strong>
          </div>
        </div>

        {/* Weight Formula Note */}
        {rec.weight_guideline_formula_en && (
          <div className="text-[11px] text-stone-500 bg-white/50 p-2.5 rounded-xl border border-stone-150">
            <span className="font-semibold text-stone-700">
              {isTa ? "எடை விதி:" : "Weight Formula:"}
            </span>{" "}
            {isTa ? rec.weight_guideline_formula_ta : rec.weight_guideline_formula_en}
          </div>
        )}

        {/* Affordable Uparatna */}
        {rec.upratna_substitutes_en.length > 0 && (
          <div className="text-xs">
            <span className="font-bold text-stone-600 block mb-1">
              {isTa ? "மலிவான மாற்று கற்கள் (உபரத்தினங்கள்):" : "Affordable Substitutes (Uparatna):"}
            </span>
            <div className="flex flex-wrap gap-1.5">
              {(isTa ? rec.upratna_substitutes_ta : rec.upratna_substitutes_en).map((sub, i) => (
                <span
                  key={i}
                  className="bg-white/90 border border-stone-200 px-2.5 py-0.5 rounded-lg text-stone-700 text-[11px]"
                >
                  {sub}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Consecration Mantra */}
        <div className="bg-stone-900 text-stone-100 p-4 rounded-2xl space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-[#DDA74F] uppercase tracking-wider">
              {isTa ? "பிரதிஷ்டை மூல மந்திரம் (108 முறை)" : "Consecration Mantra (108x)"}
            </span>
            <button
              onClick={() =>
                onCopyMantra(
                  `${rec.consecration_mantra_sanskrit}\n${rec.consecration_mantra_ta}`,
                  rec.category_code
                )
              }
              className="text-stone-400 hover:text-white p-1 rounded-md transition-colors"
              title="Copy Mantra"
            >
              {copiedMantraId === rec.category_code ? (
                <Check className="w-3.5 h-3.5 text-emerald-400" />
              ) : (
                <Copy className="w-3.5 h-3.5" />
              )}
            </button>
          </div>
          <p className="text-xs font-mono text-amber-200 leading-relaxed">
            {rec.consecration_mantra_sanskrit}
          </p>
          <p className="text-[11px] text-stone-300 font-sans">
            {rec.consecration_mantra_ta}
          </p>
        </div>
      </div>

      {/* Cleansing Vidhi */}
      <div className="border-t border-stone-200/60 pt-3 text-[11px] text-stone-600">
        <strong className="text-stone-800 block mb-0.5">
          {isTa ? "சுத்திகரிப்பு விதி:" : "Cleansing Vidhi:"}
        </strong>
        {isTa ? rec.cleansing_vidhi_ta : rec.cleansing_vidhi_en}
      </div>
    </div>
  );
}

// ─── Sub-Component: Rudraksha Item Card ──────────────────────────────────────

interface RudrakshaCardProps {
  bead: RudrakshaItem;
  isTa: boolean;
  onCopyMantra: (text: string, id: string) => void;
  copiedMantraId: string | null;
}

function RudrakshaCard({ bead, isTa, onCopyMantra, copiedMantraId }: RudrakshaCardProps) {
  const colorTheme = GRAHA_COLORS[bead.ruling_graha] || GRAHA_COLORS.jupiter;

  return (
    <div className="bg-stone-50/70 border border-stone-200 rounded-2xl p-5 flex flex-col justify-between space-y-4 hover:shadow-md transition-all">
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-[#FAF2DE] text-[#8B6914]">
            {bead.mukhi > 0 ? `${bead.mukhi} Mukhi` : "Special Bead"}
          </span>
          <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${colorTheme.badge}`}>
            {isTa ? bead.ruling_graha_ta : bead.ruling_graha_en}
          </span>
        </div>

        <div>
          <h4 className="font-bold text-base text-[#153F6B]">
            {isTa ? bead.name_ta : bead.name_en}
          </h4>
          <p className="text-xs text-stone-500 font-medium">
            <strong>{isTa ? "தெய்வம்:" : "Deity:"}</strong>{" "}
            {isTa ? bead.ruling_deity_ta : bead.ruling_deity_en}
          </p>
          <p className="text-xs text-stone-500">
            <strong>{isTa ? "சக்கரம்:" : "Chakra:"}</strong>{" "}
            {isTa ? bead.chakra_ta : bead.chakra_en}
          </p>
        </div>

        <p className="text-xs text-stone-600 leading-relaxed">
          {isTa ? bead.astrological_benefits_ta : bead.astrological_benefits_en}
        </p>

        {/* Doshas Mitigated */}
        {bead.doshas_mitigated_en.length > 0 && (
          <div className="space-y-1">
            <span className="text-[11px] font-bold text-stone-600 block">
              {isTa ? "நிவர்த்தியாகும் தோஷங்கள்:" : "Mitigates Doshas:"}
            </span>
            <div className="flex flex-wrap gap-1">
              {(isTa ? bead.doshas_mitigated_ta : bead.doshas_mitigated_en).map((dosha, i) => (
                <span
                  key={i}
                  className="bg-white border border-stone-200 px-2 py-0.5 rounded-md text-[10px] text-stone-700"
                >
                  {dosha}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Beeja Mantra */}
        <div className="bg-stone-900 text-stone-100 p-3 rounded-xl space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold text-[#DDA74F] uppercase">
              {isTa ? "பீஜ மந்திரம்" : "Beeja Mantra"}
            </span>
            <button
              onClick={() => onCopyMantra(bead.beeja_mantra_sanskrit, `rudra-${bead.mukhi}`)}
              className="text-stone-400 hover:text-white p-0.5"
            >
              {copiedMantraId === `rudra-${bead.mukhi}` ? (
                <Check className="w-3 h-3 text-emerald-400" />
              ) : (
                <Copy className="w-3 h-3" />
              )}
            </button>
          </div>
          <p className="text-xs font-mono text-amber-200">
            {bead.beeja_mantra_sanskrit}
          </p>
        </div>
      </div>

      <div className="border-t border-stone-200 pt-2 text-[11px] text-stone-500">
        <strong>{isTa ? "அணியும் விதி:" : "Protocol:"}</strong>{" "}
        {isTa ? bead.wearing_protocol_ta : bead.wearing_protocol_en}
      </div>
    </div>
  );
}
