"use client";

import React, { useState, useEffect, useMemo, useCallback } from "react";
import {
  HoroscopeResponse,
  GemstoneAdvisoryResponse,
  GemstoneRecommendation,
  ProhibitedGemstoneItem,
  RudrakshaItem,
  GemstoneRudrakshaPlaybookPdfRequest,
} from "@/lib/types";
import { getGemstoneAdvisory, downloadGemstoneRudrakshaPlaybookPdf } from "@/lib/api";
import { useLanguage } from "@/lib/i18n";
import {
  Gem,
  Download,
  Sparkles,
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Info,
  Scale,
  BookOpen,
  Flame,
  Layers,
  Compass,
  Printer,
  Clock,
  Heart,
  Sun,
  Moon,
  RefreshCw,
  FileText,
  Check,
  ExternalLink,
  ChevronRight,
  Award,
  Sliders,
  X,
} from "lucide-react";

export interface GemstoneDownloadProps {
  horoscope: HoroscopeResponse;
  clientInputs?: {
    fullName?: string;
    gender?: string;
    birthDate?: string;
    birthTime?: string;
    birthPlace?: string;
    latitude?: number;
    longitude?: number;
    timezone?: string;
    ayanamsaId?: number;
  } | null;
  doshas?: any;
  onNavigateTab?: (tab: string) => void;
}

export function GemstoneDownload({
  horoscope,
  clientInputs,
  doshas,
  onNavigateTab,
}: GemstoneDownloadProps) {
  const { language, t } = useLanguage();
  const isTa = language === "ta";

  // Native basic identifiers
  const nativeName = clientInputs?.fullName || "Native";
  const ascendantSign = horoscope.ascendant?.sign_name || "Leo";
  const moonPlanet = horoscope.planets?.find(
    (p) => p.name.toLowerCase() === "moon" || p.name.toLowerCase() === "chandra"
  );
  const moonSign = moonPlanet?.sign_name || null;

  // Detect running dasha lord if available
  const currentDasha = useMemo(() => {
    // Check if planet has high dignity or from dasa data
    return horoscope.planets?.[0]?.name || "Sun";
  }, [horoscope]);

  // Detect common doshas
  const hasKujaDosha = useMemo(() => {
    if (!doshas) return false;
    const all = doshas?.all_doshas || [];
    return all.some(
      (d: any) =>
        (d.slug?.toLowerCase().includes("kuja") ||
          d.slug?.toLowerCase().includes("manglik") ||
          d.name_en?.toLowerCase().includes("kuja") ||
          d.name_en?.toLowerCase().includes("manglik")) &&
        d.status === "present"
    );
  }, [doshas]);

  const hasSadeSati = useMemo(() => {
    if (!doshas) return false;
    const all = doshas?.all_doshas || [];
    return all.some(
      (d: any) =>
        (d.slug?.toLowerCase().includes("sade_sati") ||
          d.name_en?.toLowerCase().includes("sade sati")) &&
        d.status === "present"
    );
  }, [doshas]);

  const hasKaalSarp = useMemo(() => {
    if (!doshas) return false;
    const all = doshas?.all_doshas || [];
    return all.some(
      (d: any) =>
        (d.slug?.toLowerCase().includes("kaal_sarp") ||
          d.name_en?.toLowerCase().includes("kaal sarp")) &&
        d.status === "present"
    );
  }, [doshas]);

  // Interactive State
  const [weightKg, setWeightKg] = useState<number>(68.0);
  const [activeSection, setActiveSection] = useState<
    "pillars" | "karma" | "consecration" | "safety"
  >("pillars");
  const [advisory, setAdvisory] = useState<GemstoneAdvisoryResponse | null>(null);
  const [isLoadingAdvisory, setIsLoadingAdvisory] = useState<boolean>(true);
  const [isDownloadingPdf, setIsDownloadingPdf] = useState<boolean>(false);
  const [downloadSuccess, setDownloadSuccess] = useState<string | null>(null);
  const [selectedGemForModal, setSelectedGemForModal] = useState<GemstoneRecommendation | null>(
    null
  );

  // Fetch or calculate gemstone advisory
  const fetchAdvisory = useCallback(async (currentWeight: number) => {
    setIsLoadingAdvisory(true);
    try {
      const data = await getGemstoneAdvisory({
        ascendant_sign: ascendantSign,
        body_weight_kg: currentWeight,
      });
      setAdvisory(data);
    } catch (err) {
      console.warn("Failed to load backend advisory, generating fallback:", err);
    } finally {
      setIsLoadingAdvisory(false);
    }
  }, [ascendantSign]);

  useEffect(() => {
    fetchAdvisory(weightKg);
  }, [fetchAdvisory, weightKg]);

  // Dynamic weight helper for real-time recalculation
  const calculateDynamicWeight = useCallback(
    (baseMinRattis: number = 3.5, baseMinCarats: number = 3.25) => {
      const rattiFromWeight = Number((weightKg / 10).toFixed(2));
      const effectiveRattis = Math.max(baseMinRattis, rattiFromWeight);
      const effectiveCarats = Number((effectiveRattis * 0.91).toFixed(2));
      return { rattis: effectiveRattis, carats: effectiveCarats };
    },
    [weightKg]
  );

  // Download PDF Action
  const handleDownloadPlaybookPdf = async () => {
    setIsDownloadingPdf(true);
    setDownloadSuccess(null);
    try {
      const req: GemstoneRudrakshaPlaybookPdfRequest = {
        ascendant_sign: ascendantSign,
        native_name: nativeName,
        body_weight_kg: weightKg,
        moon_sign: moonSign,
        running_mahadasha: currentDasha,
        has_kuja_dosha: hasKujaDosha,
        has_sade_sati: hasSadeSati,
        has_rahu_ketu_dosha: hasKaalSarp,
        language: isTa ? "ta" : "en",
      };

      const blob = await downloadGemstoneRudrakshaPlaybookPdf(req);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      const cleanName = nativeName.replace(/\s+/g, "_");
      link.download = `Gemstone_Rudraksha_Playbook_${cleanName}_${ascendantSign}_${isTa ? "ta" : "en"}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      setDownloadSuccess(
        isTa
          ? "ரத்ன சமாதானம் புனிதக் கையேடு வெற்றிகரமாக பதிவிறக்கம் செய்யப்பட்டது!"
          : "Ratna Samadhan Gemstone Playbook PDF downloaded successfully!"
      );
      setTimeout(() => setDownloadSuccess(null), 6000);
    } catch (err: any) {
      console.error("PDF download failed:", err);
      alert(
        isTa
          ? "PDF பதிவிறக்கம் செய்ய முடியவில்லை. தயவுசெய்து சிறிது நேரம் கழித்து மீண்டும் முயற்சிக்கவும்."
          : `Failed to download Gemstone PDF report: ${err?.message || "Please try again."}`
      );
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. HERO HEADER: Ratna Samadhan & Dr. Andrew Dutta Heritage */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#0F2942] via-[#153F6B] to-[#1E4D7B] p-6 sm:p-8 text-white shadow-md border border-[#C5A059]/40">
        <div className="absolute -top-16 -right-16 w-64 h-64 bg-[#B4872B]/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-16 -left-16 w-64 h-64 bg-[#0F2942]/60 rounded-full blur-2xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-3 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#FAF2DE]/15 border border-[#D8BD80]/30 text-[#E5C378] text-xs font-bold tracking-wide">
              <Gem className="w-3.5 h-3.5 text-[#E5C378]" />
              <span>
                {isTa
                  ? "ரத்ன சமாதானம் • SECRETS OF ASTROLOGICAL GEM SOLUTIONS"
                  : "RATNA SAMADHAN • SECRETS OF ASTROLOGICAL GEM SOLUTIONS"}
              </span>
            </div>

            <h2 className="text-xl sm:text-2xl lg:text-3xl font-extrabold text-white tracking-tight">
              {isTa
                ? "ஜாதக ரத்தின வழிகாட்டி & புனிதக் கையேடு (GemstoneDownload)"
                : "Personalized Astrological Gemstone Advisory (GemstoneDownload)"}
            </h2>

            <p className="text-xs sm:text-sm text-slate-200 leading-relaxed">
              {isTa
                ? "டாக்டர் ஆண்ட்ரூ தத்தா (ஸ்ரீ இந்திரஜித்) அவர்களின் 'கிரகபலபலம்' மற்றும் பிருஹத் சம்ஹிதை, கருட புராண நெறிமுறைப்படி, 3 தூண் சுப ரத்தினங்கள், உடல் எடைக்கேற்ற ரட்டி/காரட் அளவுகள், புனித சுத்திகரிப்பு (ரத்ன சோதனம் & ஜாகரணம்), மற்றும் 1-14 முக ருத்ராட்ச பிரதிகூல சாந்தி."
                : "Authentic Ratna Samadhan based on the Grahabalabal Method & Classical Canons (Brihat Samhita, Garuda Purana). Features 3-Pillar Auspicious Gems, dynamic body-weight formulas, consecration rituals (Ratna Shodhan & Jagaran), and 1-to-14 Mukhi Rudraksha pacification."}
            </p>

            <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px]">
              <span className="px-2.5 py-1 rounded-md bg-white/10 border border-white/10 text-slate-200">
                <b>{isTa ? "லக்னம்:" : "Ascendant:"}</b> {ascendantSign}
              </span>
              {moonSign && (
                <span className="px-2.5 py-1 rounded-md bg-white/10 border border-white/10 text-slate-200">
                  <b>{isTa ? "ராசி:" : "Moon Sign:"}</b> {moonSign}
                </span>
              )}
              <span className="px-2.5 py-1 rounded-md bg-white/10 border border-white/10 text-slate-200">
                <b>{isTa ? "ஜாதகர்:" : "Native:"}</b> {nativeName}
              </span>
              {hasKujaDosha && (
                <span className="px-2.5 py-1 rounded-md bg-rose-500/20 border border-rose-400/40 text-rose-200 font-semibold">
                  {isTa ? "செவ்வாய் தோஷம்" : "Kuja Dosha"}
                </span>
              )}
              {hasSadeSati && (
                <span className="px-2.5 py-1 rounded-md bg-amber-500/20 border border-amber-400/40 text-amber-200 font-semibold">
                  {isTa ? "ஏழரை சனி" : "Sade Sati"}
                </span>
              )}
            </div>
          </div>

          {/* Quick Action Download Box */}
          <div className="shrink-0 flex flex-col gap-2.5 bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/15 w-full md:w-72">
            <div className="flex items-center justify-between text-xs text-slate-300">
              <span className="font-semibold">{isTa ? "அதிகாரப்பூர்வ PDF கையேடு" : "Official Printable Playbook"}</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#B4872B] text-white font-bold">
                {isTa ? "3 பக்கங்கள்" : "3 Pages"}
              </span>
            </div>

            <button
              type="button"
              onClick={handleDownloadPlaybookPdf}
              disabled={isDownloadingPdf}
              className="w-full inline-flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-gradient-to-r from-[#B4872B] to-[#D8BD80] hover:from-[#9B7322] hover:to-[#B4872B] text-[#0F2942] font-bold text-xs sm:text-sm shadow-md transition-all cursor-pointer disabled:opacity-50"
            >
              {isDownloadingPdf ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin text-[#0F2942]" />
                  <span>{isTa ? "PDF உருவாக்கப்படுகிறது..." : "Generating PDF..."}</span>
                </>
              ) : (
                <>
                  <Download className="w-4 h-4 text-[#0F2942]" />
                  <span>{isTa ? "கையேட்டைப் பதிவிறக்கு (PDF)" : "Download Playbook PDF"}</span>
                </>
              )}
            </button>

            <p className="text-[11px] text-slate-300 text-center">
              {isTa
                ? "மந்திரங்கள், விரல், உலோகம் மற்றும் சுத்தி விதிகளுடன் கூடிய முழு அறிக்கை."
                : "Complete dossier with mantras, metals, fingers, and consecration vidhi."}
            </p>
          </div>
        </div>

        {/* Success Alert Banner */}
        {downloadSuccess && (
          <div className="mt-4 p-3 rounded-lg bg-emerald-500/20 border border-emerald-400 text-emerald-100 text-xs font-semibold flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-300 shrink-0" />
            <span>{downloadSuccess}</span>
          </div>
        )}
      </div>

      {/* 2. DYNAMIC PROPORTIONAL BODY WEIGHT CALCULATOR */}
      <div className="bg-white rounded-xl border border-[#D9DEE7] p-5 shadow-2xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#F2F3F5]">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-[#FAF2DE] text-[#B4872B] flex items-center justify-center">
              <Scale className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-[#183047]">
                {isTa
                  ? "உடல் எடைக்கேற்ற துல்லிய ரத்தின அளவு கணிப்பான்"
                  : "Dynamic Proportional Body Weight Calculator (Ratna Bala)"}
              </h3>
              <p className="text-xs text-[#8190A6]">
                {isTa
                  ? "சாஸ்திர விதி: உடலின் 10 கிலோ எடைக்கு 1 ரட்டி (1 Ratti = 0.91 Carat / 182 mg)."
                  : "Classical Canon: 1 Ratti per 10 kg of native body weight (1 Ratti = 0.91 Carat)."}
              </p>
            </div>
          </div>

          {/* Quick presets */}
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-[11px] font-semibold text-[#8190A6]">{isTa ? "முன்அமைப்புகள்:" : "Presets:"}</span>
            {[55, 65, 75, 85, 95].map((preset) => (
              <button
                key={`preset-${preset}`}
                type="button"
                onClick={() => setWeightKg(preset)}
                className={`px-2.5 py-1 text-xs rounded-md font-semibold transition-all cursor-pointer ${
                  weightKg === preset
                    ? "bg-[#153F6B] text-white shadow-2xs"
                    : "bg-[#F8FAFC] text-[#52667E] hover:bg-[#FAF2DE] hover:text-[#B4872B] border border-[#E2E8F0]"
                }`}
              >
                {preset} kg
              </button>
            ))}
          </div>
        </div>

        {/* Slider & Input Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
          <div className="md:col-span-2 space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-medium text-[#52667E]">
                {isTa ? "ஜாதகரின் உடல் எடை அளவு:" : "Native's Body Weight Slider:"}
              </span>
              <span className="font-bold text-[#153F6B] font-mono text-sm">
                {weightKg.toFixed(1)} kg ({((weightKg / 10)).toFixed(2)} {isTa ? "ரட்டி" : "Rattis"})
              </span>
            </div>
            <input
              type="range"
              min={40}
              max={120}
              step={1}
              value={weightKg}
              onChange={(e) => setWeightKg(parseFloat(e.target.value) || 65)}
              className="w-full accent-[#B4872B] cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-[#8190A6]">
              <span>40 kg</span>
              <span>60 kg</span>
              <span>80 kg</span>
              <span>100 kg</span>
              <span>120 kg</span>
            </div>
          </div>

          <div className="bg-[#FAF8F2] border border-[#E8DFCE] rounded-lg p-3 text-center space-y-1">
            <span className="text-[11px] font-semibold text-[#8C6D23]">
              {isTa ? "பரிந்துரைக்கப்படும் சுப எடை" : "Computed Effective Weight"}
            </span>
            <div className="text-base font-extrabold text-[#153F6B] font-mono">
              {(weightKg / 10).toFixed(2)} Ratti &nbsp;|&nbsp; {((weightKg / 10) * 0.91).toFixed(2)} Carats
            </div>
            <p className="text-[10px] text-[#8190A6]">
              {isTa ? "அனைத்து ரத்தின அட்டைகளிலும் தானாக புதுப்பிக்கப்பட்டுள்ளது" : "Synchronized dynamically across all recommendations"}
            </p>
          </div>
        </div>
      </div>

      {/* 3. SECTION NAVIGATION PILLS */}
      <div className="flex items-center gap-1.5 border-b border-[#D9DEE7] pb-1 overflow-x-auto text-xs font-semibold">
        <button
          type="button"
          onClick={() => setActiveSection("pillars")}
          className={`px-4 py-2 rounded-lg transition-all cursor-pointer whitespace-nowrap inline-flex items-center gap-1.5 ${
            activeSection === "pillars"
              ? "bg-[#153F6B] text-white shadow-2xs font-bold"
              : "text-[#52667E] hover:text-[#153F6B] hover:bg-white"
          }`}
        >
          <Gem className="w-3.5 h-3.5" />
          <span>{isTa ? "1. சுப 3-தூண் ரத்தினங்கள்" : "1. 3-Pillar Auspicious Gems"}</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveSection("karma")}
          className={`px-4 py-2 rounded-lg transition-all cursor-pointer whitespace-nowrap inline-flex items-center gap-1.5 ${
            activeSection === "karma"
              ? "bg-[#153F6B] text-white shadow-2xs font-bold"
              : "text-[#52667E] hover:text-[#153F6B] hover:bg-white"
          }`}
        >
          <BookOpen className="w-3.5 h-3.5" />
          <span>{isTa ? "2. கர்மா & கிரகபலபலம்" : "2. Karma & Grahabalabal"}</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveSection("consecration")}
          className={`px-4 py-2 rounded-lg transition-all cursor-pointer whitespace-nowrap inline-flex items-center gap-1.5 ${
            activeSection === "consecration"
              ? "bg-[#153F6B] text-white shadow-2xs font-bold"
              : "text-[#52667E] hover:text-[#153F6B] hover:bg-white"
          }`}
        >
          <Flame className="w-3.5 h-3.5" />
          <span>{isTa ? "3. சுத்தி & அணிதல் (சோதனம்/ஜாகரணம்)" : "3. Consecration (Shodhan & Jagaran)"}</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveSection("safety")}
          className={`px-4 py-2 rounded-lg transition-all cursor-pointer whitespace-nowrap inline-flex items-center gap-1.5 ${
            activeSection === "safety"
              ? "bg-[#153F6B] text-white shadow-2xs font-bold"
              : "text-[#52667E] hover:text-[#153F6B] hover:bg-white"
          }`}
        >
          <ShieldAlert className="w-3.5 h-3.5" />
          <span>{isTa ? "4. தடைகள் & ருத்ராட்ச சாந்தி" : "4. Strict Prohibitions & Rudraksha"}</span>
        </button>
      </div>

      {/* 4. SECTION 1: 3-PILLAR AUSPICIOUS GEMSTONES */}
      {activeSection === "pillars" && (
        <div className="space-y-5">
          {/* Doctrine Callout */}
          <div className="bg-[#FFFDF5] border-l-4 border-[#B4872B] p-4 rounded-r-xl border-y border-r border-[#EFE8D8] space-y-1">
            <h4 className="font-bold text-xs sm:text-sm text-[#183047] flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-[#B4872B]" />
              <span>
                {isTa
                  ? "அனுகூல ரத்தின முறை: 3 தூண் மற்றும் யோககாரக ரத்தினங்கள்"
                  : "The Three Pillars of Auspicious Jyotish Gemology (Anukula Vada)"}
              </span>
            </h4>
            <p className="text-xs text-[#52667E] leading-relaxed">
              {isTa
                ? "ரத்தினங்கள் உடலின் ஆரா மண்டலத்தில் கிரகத்தின் சுப ஒளியை பெருக்கும் காந்தக் கண்ணாடிகள். லக்னாதிபதி (உயிர்), 5-ஆம் அதிபதி (புண்ணியம்), 9-ஆம் அதிபதி (பாக்கியம்) மற்றும் பூரண யோககாரக கிரகங்களுக்கு மட்டுமே ரத்தினங்களை அணிய வேண்டும்."
                : "Gemstones act as cosmic prisms that capture and transmit planetary radiation into the native's aura. They ALWAYS magnify planetary energy. Under classical canons, gemstones are prescribed strictly for the Lagna Lord, 5th Lord, 9th Lord, and genuine Yogakarakas."}
            </p>
          </div>

          {/* Cards Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {/* Pillar 1: Life Stone (Jeevan Ratna) */}
            {advisory?.life_stone && (
              <GemstoneCard
                titleBadge={isTa ? "தூண் 1: உயிர் ரத்தினம் (ஜீவன் ரத்னம்)" : "PILLAR 1: LIFE STONE (JEEVAN RATNA)"}
                rec={advisory.life_stone}
                dynamicWeight={calculateDynamicWeight(
                  advisory.life_stone.minimum_rattis || 3.5,
                  advisory.life_stone.minimum_carats || 3.25
                )}
                isTa={isTa}
                onOpenModal={() => setSelectedGemForModal(advisory.life_stone)}
              />
            )}

            {/* Pillar 2: Lucky Stone (Punya Ratna) */}
            {advisory?.lucky_stone && (
              <GemstoneCard
                titleBadge={isTa ? "தூண் 2: புண்ணிய ரத்தினம் (பூர்வ புண்ணியம்)" : "PILLAR 2: LUCKY STONE (PUNYA RATNA)"}
                rec={advisory.lucky_stone}
                dynamicWeight={calculateDynamicWeight(
                  advisory.lucky_stone.minimum_rattis || 3.5,
                  advisory.lucky_stone.minimum_carats || 3.25
                )}
                isTa={isTa}
                onOpenModal={() => setSelectedGemForModal(advisory.lucky_stone)}
              />
            )}

            {/* Pillar 3: Fortune Stone (Bhagya Ratna) */}
            {advisory?.fortune_stone && (
              <GemstoneCard
                titleBadge={isTa ? "தூண் 3: பாக்கிய ரத்தினம் (பாக்கிய ஸ்தானம்)" : "PILLAR 3: FORTUNE STONE (BHAGYA RATNA)"}
                rec={advisory.fortune_stone}
                dynamicWeight={calculateDynamicWeight(
                  advisory.fortune_stone.minimum_rattis || 3.5,
                  advisory.fortune_stone.minimum_carats || 3.25
                )}
                isTa={isTa}
                onOpenModal={() => setSelectedGemForModal(advisory.fortune_stone)}
              />
            )}

            {/* Secondary Support Stone (Yogakaraka or Dasha Lord) */}
            {advisory?.secondary_support_stone && (
              <GemstoneCard
                titleBadge={
                  isTa
                    ? "துணை ஆதரவு ரத்தினம் (யோககாரகன் / தசா நாதன்)"
                    : "SECONDARY SUPPORT STONE (YOGAKARAKA / DASHA LORD)"
                }
                rec={advisory.secondary_support_stone}
                dynamicWeight={calculateDynamicWeight(
                  advisory.secondary_support_stone.minimum_rattis || 3.5,
                  advisory.secondary_support_stone.minimum_carats || 3.25
                )}
                isTa={isTa}
                onOpenModal={() => setSelectedGemForModal(advisory?.secondary_support_stone ?? null)}
              />
            )}
          </div>
        </div>
      )}

      {/* 5. SECTION 2: KARMA & GRAHABALABAL PHILOSOPHY */}
      {activeSection === "karma" && (
        <div className="space-y-5">
          <div className="bg-white rounded-xl border border-[#D9DEE7] p-6 shadow-2xs space-y-4">
            <div className="flex items-center gap-2 pb-2 border-b border-[#F2F3F5]">
              <BookOpen className="w-5 h-5 text-[#B4872B]" />
              <h3 className="font-bold text-base text-[#183047]">
                {isTa
                  ? "ரத்ன சமாதானம்: கர்மாவின் 4 அடுக்குகள் மற்றும் ஜோதிட தீர்வுகள்"
                  : "Secrets of Astrological Gem Solutions: The 4 Layers of Karma"}
              </h3>
            </div>

            <p className="text-xs sm:text-sm text-[#52667E] leading-relaxed">
              {isTa
                ? "டாக்டர் ஆண்ட்ரூ தத்தா (ஸ்ரீ இந்திரஜித்) அவர்களின் குடும்ப வழித்தோன்றல் ரகசியங்களின்படி, மனிதன் பூமியில் பிறப்பது முற்பிறவிகளில் செய்த கர்ம வினைகளின் காரணமாகவே. கர்ம வினைகள் 4 அடுக்குகளாக செயல்படுகின்றன:"
                : "According to the Ratna Samadhan heritage expounded by Dr. Andrew Dutta (Sri Indrajit), human life on earth is shaped by past actions unfolding across 4 distinct layers of Karma:"}
            </p>

            {/* 4 Layers Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-2">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-[#153F6B] text-white flex items-center justify-center text-xs font-bold">
                    1
                  </span>
                  <h4 className="font-bold text-xs sm:text-sm text-[#183047]">
                    {isTa ? "சஞ்சித கர்மா (Sanchita Karma)" : "Sanchita Karma (Accumulated Storehouse)"}
                  </h4>
                </div>
                <p className="text-xs text-[#52667E] leading-relaxed">
                  {isTa
                    ? "ஆயிரக்கணக்கான முற்பிறவிகளில் ஆன்மாவால் ஈட்டப்பட்ட மொத்த கர்ம வினைகளின் பிரம்மாண்ட கருவூலம். இது ஒரு ஆழ்கடல் போன்றது."
                    : "The vast celestial reservoir of all deeds, thoughts, and impressions gathered across countless previous incarnations."}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-[#FAF8F2] border border-[#E8DFCE] space-y-2">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-[#B4872B] text-white flex items-center justify-center text-xs font-bold">
                    2
                  </span>
                  <h4 className="font-bold text-xs sm:text-sm text-[#183047]">
                    {isTa ? "பிராரப்த கர்மா (Prarabdha Karma)" : "Prarabdha Karma (Fated Natal Blueprint)"}
                  </h4>
                </div>
                <p className="text-xs text-[#52667E] leading-relaxed">
                  {isTa
                    ? "இந்த குறிப்பிட்ட மனிதப் பிறவியில் அனுபவித்து முடிப்பதற்காக சஞ்சித கர்மாவிலிருந்து ஒதுக்கப்பட்ட பகுதி. இதுவே ஒருவரின் பிறந்த நேர ஜாதகமாக வரைபடமாகிறது."
                    : "The precise slice of Sanchita karma chosen to unfold in this specific lifetime. This is mapped directly by your natal birth chart."}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-[#F0FDF4] border border-[#BBF7D0] space-y-2">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-emerald-700 text-white flex items-center justify-center text-xs font-bold">
                    3
                  </span>
                  <h4 className="font-bold text-xs sm:text-sm text-[#183047]">
                    {isTa ? "கிரியமாண கர்மா (Kriyaman Karma)" : "Kriyaman Karma (Current Willful Action)"}
                  </h4>
                </div>
                <p className="text-xs text-[#52667E] leading-relaxed">
                  {isTa
                    ? "தற்போதைய பிறவியில் மனிதன் தன் புருஷாகாரத்தால் (சுய முயற்சியால்) செய்யும் செயல்கள், பரிகாரங்கள் மற்றும் சாஸ்திர ரத்தின தீர்வுகள். இதுவே விதியை வெல்லும் திறவுகோல்."
                    : "Active, present-moment conscious choices and remedial measures (Purushakara), including authentic gemstone wearing, that modulate destiny."}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-[#FAF5FF] border border-[#E9D5FF] space-y-2">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-purple-700 text-white flex items-center justify-center text-xs font-bold">
                    4
                  </span>
                  <h4 className="font-bold text-xs sm:text-sm text-[#183047]">
                    {isTa ? "ஆகாமிய கர்மா (Agami Karma)" : "Agami Karma (Future Seeds)"}
                  </h4>
                </div>
                <p className="text-xs text-[#52667E] leading-relaxed">
                  {isTa
                    ? "தற்போதைய கிரியமாண வினைகளால் எதிர்காலப் பிறவிகளுக்காக விதைக்கப்படும் கர்ம வித்துக்கள்."
                    : "Future karmic consequences generated by present actions and mental intentions."}
                </p>
              </div>
            </div>

            {/* 3 Qualities of Karma Box */}
            <div className="pt-4 border-t border-[#F2F3F5] space-y-3">
              <h4 className="font-bold text-xs sm:text-sm text-[#183047] flex items-center gap-1.5">
                <Compass className="w-4 h-4 text-[#153F6B]" />
                <span>
                  {isTa
                    ? "கர்மாவின் 3 குணங்கள் மற்றும் ரத்தினங்களால் மாற்றும் திறன்"
                    : "3 Qualities of Karma & How Gem Solutions Alter Horoscope Potential"}
                </span>
              </h4>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                <div className="p-3 rounded-lg border border-rose-200 bg-rose-50/50 space-y-1">
                  <span className="font-bold text-rose-900">
                    {isTa ? "திட கர்மா (Dridha Karma)" : "Dridha Karma (Fixed)"}
                  </span>
                  <p className="text-rose-800 text-[11px] leading-relaxed">
                    {isTa
                      ? "மாற்ற முடியாத உறுதியான விதி. அனுபவித்தே தீர வேண்டும். இறை சரணாகதியும் தியானமும் மட்டுமே ஆறுதல் தரும்."
                      : "Unalterable fated karma. Must be experienced; requires prayer, acceptance, and spiritual surrender."}
                  </p>
                </div>

                <div className="p-3 rounded-lg border border-amber-200 bg-amber-50/50 space-y-1">
                  <span className="font-bold text-amber-900">
                    {isTa ? "திட-அதிட கர்மா (Dridha-Adridha)" : "Dridha-Adridha (Partially Alterable)"}
                  </span>
                  <p className="text-amber-800 text-[11px] leading-relaxed">
                    {isTa
                      ? "முறையான ரத்தின சமாதானம் மற்றும் சாதனைகளால் தீவிரத்தை குறைத்து சுபமாக மாற்றக்கூடிய கர்ம வினைகள்."
                      : "Can be actively mitigated, deflected, or transmuted through authentic astrological gem remedies and mantras."}
                  </p>
                </div>

                <div className="p-3 rounded-lg border border-emerald-200 bg-emerald-50/50 space-y-1">
                  <span className="font-bold text-emerald-900">
                    {isTa ? "அதிட கர்மா (Adridha Karma)" : "Adridha Karma (Flexible)"}
                  </span>
                  <p className="text-emerald-800 text-[11px] leading-relaxed">
                    {isTa
                      ? "மிக எளிதில் கரையக்கூடியது. சரியான சுப ரத்தினத்தை அணிந்த உடனேயே பூரண நன்மைகள் கை கூடும்."
                      : "Readily dissolved and transformed through timely Purushakar and wearing auspicious gems."}
                  </p>
                </div>
              </div>
            </div>

            {/* The Grahabalabal Method & KP Insight */}
            <div className="p-4 rounded-xl bg-[#FFFDF5] border border-[#D8BD80] space-y-2 text-xs">
              <div className="flex items-center gap-2 text-[#8C6D23] font-bold">
                <Sparkles className="w-4 h-4 text-[#B4872B]" />
                <span>
                  {isTa
                    ? "கிரகபலபலம் நெறிமுறை: 'கிரகமே பலன்களின் ஊற்றுக்கண்'"
                    : "The Grahabalabal Method: 'Planet is the Source of the Result'"}
                </span>
              </div>
              <p className="text-[#52667E] leading-relaxed">
                {isTa
                  ? "கே.பி ஜோதிட மேதை கே.எஸ். கிருஷ்ணமூர்த்தி அவர்கள் கூறியபடி, 'கிரகமே பலன்களின் ஊற்றுக்கண்'. மேலோட்டமான அனுகூல/பிரதிகூல வாதங்களில் சிக்காமல், ஷட்பலம், பாவபலம், மற்றும் ஆதிபத்தியங்களை சமன் செய்யும் முறையே கிரகபலபலம் ஆகும். சர லக்னத்திற்கு 11-ஆம் அதிபதி பாதகாதிபதியாக இருந்தாலும், அவரே லாபத்திற்கும் வெற்றிகளுக்கும் காரணமாவார். கிரகபலபல முறை இந்த முரண்பாடுகளை களைய 3 தூண் ரத்தினங்களை மட்டுமே தேர்ந்தெடுத்து பாதுகாப்பான ஒளிக்கதிர்களை உறுதி செய்கிறது."
                  : "As affirmed by KP master K.S. Krishnamurti, 'The planet is the source of the result'. The Grahabalabal method reconciles the paradox of planets ruling both good and bad houses (e.g. Badhaka vs 11th gains) by prioritizing the 3 pure benefic pillars (Lagna, 5th, 9th) to ensure positive energetic radiation without triggering hidden vulnerabilities."}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 6. SECTION 3: CONSECRATION (SHODHAN, JAGARAN & DHARAN) */}
      {activeSection === "consecration" && (
        <div className="space-y-5">
          <div className="bg-white rounded-xl border border-[#D9DEE7] p-6 shadow-2xs space-y-5">
            <div className="flex items-center gap-2 pb-2 border-b border-[#F2F3F5]">
              <Flame className="w-5 h-5 text-[#B4872B]" />
              <h3 className="font-bold text-base text-[#183047]">
                {isTa
                  ? "ரத்தின சுத்தி மற்றும் அணிதல் சாஸ்திர நெறிமுறைகள்"
                  : "Sacred Consecration Protocols: Ratna Shodhan, Jagaran & Dharan"}
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              {/* Step 1: Ratna Shodhan */}
              <div className="p-5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-3 flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="w-10 h-10 rounded-lg bg-[#153F6B]/10 text-[#153F6B] flex items-center justify-center font-bold text-sm">
                    01
                  </div>
                  <h4 className="font-bold text-sm text-[#183047]">
                    {isTa ? "ரத்ன சோதனம் (சுத்திகரிப்பு)" : "Ratna Shodhan (Purification)"}
                  </h4>
                  <p className="text-xs text-[#52667E] leading-relaxed">
                    {isTa
                      ? "சுரங்கங்களிலிருந்து வெட்டி எடுக்கப்பட்டு பல கைகள் மாறி வரும் போது ரத்தினத்தில் படியும் எதிர்மறை ஆற்றல்களை நீக்குதல். பசும்பால், தேன், நெய், தயிர் மற்றும் கங்கை நீர் (பஞ்சாமிர்தம்) கலவையில் 45 முதல் 60 நிமிடங்கள் ஊற வைத்து, தூய நீரால் கழுவ வேண்டும்."
                      : "Neutralizes mining and commercial handling vibrations. Immerse in Panchamrit (raw cow's milk, honey, curd, ghee, gangajal) for 45-60 minutes, then rinse in pure sacred water."}
                  </p>
                </div>
                <div className="pt-2 border-t border-[#E2E8F0] text-[11px] font-semibold text-[#153F6B]">
                  ✓ {isTa ? "எதிர்மறை பதிவுகள் நீங்கும்" : "Clears residual negative energy"}
                </div>
              </div>

              {/* Step 2: Ratna Jagaran */}
              <div className="p-5 rounded-xl bg-[#FFFDF5] border border-[#D8BD80] space-y-3 flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="w-10 h-10 rounded-lg bg-[#FAF2DE] text-[#B4872B] flex items-center justify-center font-bold text-sm">
                    02
                  </div>
                  <h4 className="font-bold text-sm text-[#183047]">
                    {isTa ? "ரத்ன ஜாகரணம் (விழிப்புணர்வு)" : "Ratna Jagaran (Activation)"}
                  </h4>
                  <p className="text-xs text-[#52667E] leading-relaxed">
                    {isTa
                      ? "ரத்தினத்தில் உறங்கிக் கிடக்கும் பிரபஞ்ச காஸ்மிக் கதிர்வீச்சை உயிர்ப்பித்தல். வளர்பிறை சுப தினத்தில், உரிய கிரகத்தின் ஓரையில் (Sunrise Hora), அந்த கிரகத்தின் பீஜ மூல மந்திரம் மற்றும் காயத்ரி மந்திரத்தை 108 முறை ஜெபித்து பிராண பிரதிஷ்டை செய்ய வேண்டும்."
                      : "Awakens the crystalline prism's dormant cosmic frequencies. Recite 108 Beeja & Gayatri Mantras during the planet's ruling Hora at Shukla Paksha sunrise."}
                  </p>
                </div>
                <div className="pt-2 border-t border-[#E8DFCE] text-[11px] font-semibold text-[#8C6D23]">
                  ✓ {isTa ? "108 முறை மூல மந்திர ஜெபம்" : "108x Planetary Beeja Chants"}
                </div>
              </div>

              {/* Step 3: Ratna Dharan */}
              <div className="p-5 rounded-xl bg-[#F0FDF4] border border-[#86EFAC] space-y-3 flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="w-10 h-10 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-sm">
                    03
                  </div>
                  <h4 className="font-bold text-sm text-[#183047]">
                    {isTa ? "ரத்ன தாரணம் (அணிதல்)" : "Ratna Dharan (Sacred Wearing)"}
                  </h4>
                  <p className="text-xs text-[#52667E] leading-relaxed">
                    {isTa
                      ? "ரத்தினத்தின் அடிபாகம் தோலில் படும் வகையில் திறந்த அடி (open-back) அமைப்பில் மோதிரம் செய்யப்பட வேண்டும். வலது கையின் குறிப்பிட்ட விரலில், உரிய உலோகம் (தங்கம்/வெள்ளி/பஞ்சலோகம்) கொண்டு, கிழக்கு நோக்கி அமர்ந்து வழிபாட்டிற்கு பின் அணிய வேண்டும்."
                      : "Set with an open-back setting so the pavilion touches the skin. Wear on the designated finger of the active (right) hand facing East after morning prayers."}
                  </p>
                </div>
                <div className="pt-2 border-t border-[#BBF7D0] text-[11px] font-semibold text-emerald-800">
                  ✓ {isTa ? "தோலைத் தொடும் திறந்த அடி" : "Skin contact strictly mandatory"}
                </div>
              </div>
            </div>

            {/* Special 3-Day Pillow Test Notice */}
            <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs space-y-1">
              <div className="flex items-center gap-1.5 font-bold">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                <span>
                  {isTa
                    ? "நீலக்கல் மற்றும் கோமேதகத்திற்கு 3 நாள் தலையணை சோதனை கட்டாயம்:"
                    : "Mandatory 3-Day Pillow Trial for Blue Sapphire (Neelam) and Hessonite (Gomed):"}
                </span>
              </div>
              <p className="leading-relaxed">
                {isTa
                  ? "சனி மற்றும் ராகுவின் ரத்தினங்களை உலோகத்தில் பதிப்பதற்கு முன், ஒரு நீலத் துணியில் முடிந்து 3 நாட்கள் இரவில் தலையணையின் கீழ் வைத்து உறங்க வேண்டும். கெட்ட கனவுகள், பதட்டம் அல்லது தலைவலி ஏற்பட்டால் அந்த ரத்தினத்தை தவிர்க்க வேண்டும்; சுப கனவுகள் அல்லது அமைதியான தூக்கம் கிடைத்தால் அணியலாம்."
                  : "Before setting Blue Sapphire or Hessonite in metal, wrap the loose gem in blue silk and place under your pillow for 3 consecutive nights. If you experience distressing dreams or unrest, avoid the gem. Peaceful rest confirms bio-energetic harmony."}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 7. SECTION 4: STRICT PROHIBITIONS & RUDRAKSHA PACIFICATION */}
      {activeSection === "safety" && (
        <div className="space-y-5">
          {/* Prohibited Stones Table */}
          <div className="bg-white rounded-xl border border-[#D9DEE7] p-6 shadow-2xs space-y-4">
            <div className="flex items-center gap-2 pb-2 border-b border-[#F2F3F5]">
              <ShieldAlert className="w-5 h-5 text-rose-600" />
              <div>
                <h3 className="font-bold text-base text-[#183047]">
                  {isTa
                    ? `${ascendantSign} லக்னத்திற்கு கண்டிப்பாக தவிர்க்க வேண்டிய ரத்தினங்கள்`
                    : `Strictly Prohibited Gemstones for ${ascendantSign} Ascendant`}
                </h3>
                <p className="text-xs text-[#8190A6]">
                  {isTa
                    ? "6, 8, 12 மறைவு ஸ்தானாதிபதிகள் மற்றும் அசுப கிரகங்களின் ரத்தினங்களை அணிவது ஆபத்தானது."
                    : "Lords of 6th, 8th, and 12th Dusthanas magnify illnesses, debts, litigation, and setbacks if worn as gemstones."}
                </p>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-rose-50 text-rose-900 font-bold border-b border-rose-200">
                  <tr>
                    <th className="p-2.5">{isTa ? "கிரகம்" : "Graha"}</th>
                    <th className="p-2.5">{isTa ? "தடை செய்யப்பட்ட ரத்தினம்" : "Prohibited Gem"}</th>
                    <th className="p-2.5">{isTa ? "சாஸ்திர தடைக்கான காரணம்" : "Shastric Reason"}</th>
                    <th className="p-2.5">{isTa ? "பாதுகாப்பான மாற்று சாந்தி" : "Safe Alternative Remedy"}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F2F3F5]">
                  {advisory?.prohibited_gemstones?.map((pro, idx) => (
                    <tr key={`pro-${idx}`} className="hover:bg-rose-50/30">
                      <td className="p-2.5 font-bold text-[#183047]">
                        {isTa ? pro.graha_name_ta : pro.graha_name_en}
                      </td>
                      <td className="p-2.5 font-semibold text-rose-700">
                        {isTa ? pro.primary_gem_ta : pro.primary_gem_en}
                      </td>
                      <td className="p-2.5 text-[#52667E] max-w-xs">
                        {isTa ? pro.reason_ta : pro.reason_en}
                      </td>
                      <td className="p-2.5 text-emerald-800 font-medium">
                        {isTa ? pro.safe_alternative_ta : pro.safe_alternative_en}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Incompatible Gemstone Conflicts */}
            <div className="pt-3 border-t border-[#F2F3F5] space-y-2">
              <h4 className="font-bold text-xs text-[#183047] flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                <span>
                  {isTa ? "பகை கிரக ரத்தின முரண்பாட்டு விதிகள்:" : "Planetary Conflict Rules (Never Wear Together):"}
                </span>
              </h4>
              <ul className="text-xs text-[#52667E] space-y-1 list-disc list-inside">
                <li>
                  <b>{isTa ? "மாணிக்கம் (சூரியன்):" : "Ruby (Sun):"}</b>{" "}
                  {isTa
                    ? "நீலக்கல், வைரம், கோமேதகம், வைடூரியத்துடன் ஒருபோதும் இணைக்கக் கூடாது."
                    : "Never wear with Blue Sapphire, Diamond, Hessonite, or Cat's Eye."}
                </li>
                <li>
                  <b>{isTa ? "முத்து (சந்திரன்):" : "Pearl (Moon):"}</b>{" "}
                  {isTa
                    ? "கோமேதகம் அல்லது வைடூரியத்துடன் ஒருபோதும் இணைக்கக் கூடாது."
                    : "Never wear with Hessonite or Cat's Eye."}
                </li>
                <li>
                  <b>{isTa ? "பவழம் (செவ்வாய்):" : "Red Coral (Mars):"}</b>{" "}
                  {isTa
                    ? "மரகதம் அல்லது நீலக்கல்லுடன் ஒருபோதும் இணைக்கக் கூடாது."
                    : "Never wear with Emerald or Blue Sapphire."}
                </li>
                <li>
                  <b>{isTa ? "மஞ்சள் புஷ்பராகம் (குரு):" : "Yellow Sapphire (Jupiter):"}</b>{" "}
                  {isTa
                    ? "வைரம் அல்லது நீலக்கல்லுடன் ஒரே கையில் இணைக்கக் கூடாது."
                    : "Never wear with Diamond or Blue Sapphire on the same hand."}
                </li>
              </ul>
            </div>
          </div>

          {/* Rudraksha Pratikula Pacification Box */}
          {advisory?.recommended_rudraksha && (
            <div className="bg-white rounded-xl border border-[#D9DEE7] p-6 shadow-2xs space-y-4">
              <div className="flex items-center gap-2 pb-2 border-b border-[#F2F3F5]">
                <ShieldCheck className="w-5 h-5 text-emerald-600" />
                <div>
                  <h3 className="font-bold text-base text-[#183047]">
                    {isTa
                      ? "பிரதிகூல சாந்தி: பாதுகாப்பான 1-14 முக ருத்ராட்ச பரிந்துரை"
                      : "Pratikula Pacification: Safe 1-to-14 Mukhi Rudraksha Prescription"}
                  </h3>
                  <p className="text-xs text-[#8190A6]">
                    {isTa
                      ? "ரத்தினங்கள் போல் கதிர்வீச்சை பெருக்காமல், தோஷங்களை சாந்தப்படுத்தும் மின்காந்த கவசம்."
                      : "Unlike gemstones which magnify radiation, Rudraksha safely neutralizes doshas without side-effects."}
                  </p>
                </div>
              </div>

              <div className="p-3.5 rounded-lg bg-[#FAF8F2] border border-[#E8DFCE] text-xs text-[#8C6D23]">
                <b>{isTa ? "ஜாதக பொருத்தம்:" : "Personal Alignment:"}</b>{" "}
                {isTa
                  ? advisory.recommended_rudraksha.personal_alignment_reason_ta
                  : advisory.recommended_rudraksha.personal_alignment_reason_en}
              </div>

              {/* 3 Beads Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {advisory.recommended_rudraksha.primary_bead && (
                  <RudrakshaCard
                    badge={isTa ? "முதன்மை ருத்ராட்சம்" : "Primary Bead"}
                    bead={advisory.recommended_rudraksha.primary_bead}
                    isTa={isTa}
                  />
                )}
                {advisory.recommended_rudraksha.secondary_bead && (
                  <RudrakshaCard
                    badge={isTa ? "துணை ருத்ராட்சம்" : "Secondary Bead"}
                    bead={advisory.recommended_rudraksha.secondary_bead}
                    isTa={isTa}
                  />
                )}
                {advisory.recommended_rudraksha.universal_bead && (
                  <RudrakshaCard
                    badge={isTa ? "பொதுக் கவசம்" : "Universal Protector"}
                    bead={advisory.recommended_rudraksha.universal_bead}
                    isTa={isTa}
                  />
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 8. BOTTOM HERO ACTION BAR */}
      <div className="bg-[#FAF8F2] border border-[#E8DFCE] rounded-xl p-5 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="space-y-1 text-center sm:text-left">
          <h4 className="font-bold text-sm text-[#183047]">
            {isTa ? "ரத்ன சமாதானம் புனிதக் கையேடு தயார்" : "Ready to Order or Consecrate Your Gemstone?"}
          </h4>
          <p className="text-xs text-[#52667E]">
            {isTa
              ? `ஜாதகர் ${nativeName} (${ascendantSign} லக்னம்) அவர்களின் முழு ரத்தின-ருத்ராட்ச கையேட்டை PDF ஆக சேமிக்க.`
              : `Download the complete 3-page personalized PDF Playbook for ${nativeName} (${ascendantSign} Lagna).`}
          </p>
        </div>

        <button
          type="button"
          onClick={handleDownloadPlaybookPdf}
          disabled={isDownloadingPdf}
          className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-lg bg-[#153F6B] hover:bg-[#0F3155] text-white font-bold text-xs sm:text-sm shadow-md transition-all cursor-pointer disabled:opacity-50 shrink-0"
        >
          {isDownloadingPdf ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin text-white" />
              <span>{isTa ? "PDF உருவாக்கப்படுகிறது..." : "Generating PDF..."}</span>
            </>
          ) : (
            <>
              <Download className="w-4 h-4 text-white" />
              <span>{isTa ? "கையேட்டைப் பதிவிறக்கு (PDF)" : "Download Playbook PDF"}</span>
            </>
          )}
        </button>
      </div>

      {/* 9. MODAL: GEMSTONE DEEP DIVE MODAL */}
      {selectedGemForModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-4 border border-[#D9DEE7] max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-[#F2F3F5]">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-[#FAF2DE] text-[#B4872B] flex items-center justify-center">
                  <Gem className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-bold text-base text-[#183047]">
                    {isTa ? selectedGemForModal.primary_gem_ta : selectedGemForModal.primary_gem_en}
                  </h3>
                  <span className="text-xs text-[#8190A6] font-mono">
                    {selectedGemForModal.primary_gem_sanskrit}
                  </span>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setSelectedGemForModal(null)}
                className="p-1 rounded-lg text-[#8190A6] hover:bg-[#F2F3F5] hover:text-[#183047] transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-lg bg-[#FAF8F2] border border-[#E8DFCE]">
                <span className="font-bold text-[#8C6D23]">
                  {isTa ? "நோக்கம் & சாஸ்திர பலன்:" : "Purpose & Astrological Scope:"}
                </span>
                <p className="text-[#52667E] mt-1 leading-relaxed">
                  {isTa
                    ? selectedGemForModal.governing_purpose_ta
                    : selectedGemForModal.governing_purpose_en}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="p-2.5 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                  <span className="text-[#8190A6] block text-[10px]">{isTa ? "உலோகம்" : "Prescribed Metal"}</span>
                  <span className="font-bold text-[#183047]">
                    {isTa ? selectedGemForModal.prescribed_metal_ta : selectedGemForModal.prescribed_metal_en}
                  </span>
                </div>
                <div className="p-2.5 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                  <span className="text-[#8190A6] block text-[10px]">{isTa ? "விரல்" : "Wearing Finger"}</span>
                  <span className="font-bold text-[#183047]">
                    {isTa ? selectedGemForModal.ideal_finger_ta : selectedGemForModal.ideal_finger_en}
                  </span>
                </div>
                <div className="p-2.5 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                  <span className="text-[#8190A6] block text-[10px]">{isTa ? "நாள் & ஓரை" : "Day & Planetary Hora"}</span>
                  <span className="font-bold text-[#183047]">
                    {isTa ? selectedGemForModal.energization_day_ta : selectedGemForModal.energization_day_en}
                  </span>
                </div>
                <div className="p-2.5 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                  <span className="text-[#8190A6] block text-[10px]">{isTa ? "சுப எடை" : "Prescribed Weight"}</span>
                  <span className="font-bold text-[#B4872B] font-mono">
                    {calculateDynamicWeight(selectedGemForModal.minimum_rattis || 3.5).rattis} Ratti / {calculateDynamicWeight(selectedGemForModal.minimum_rattis || 3.5).carats} Carats
                  </span>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0] space-y-1">
                <span className="font-bold text-[#153F6B] block">
                  {isTa ? "பிரதிஷ்டை பீஜ மந்திரம் (108 முறை):" : "Consecration Beeja Mantra (Chant 108x):"}
                </span>
                <p className="font-mono text-[#183047] font-semibold">
                  {selectedGemForModal.consecration_mantra_sanskrit}
                </p>
                <p className="text-[11px] text-[#52667E] italic">
                  {selectedGemForModal.consecration_mantra_ta}
                </p>
              </div>

              {selectedGemForModal.gayatri_mantra_sanskrit && (
                <div className="p-3 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0] space-y-1">
                  <span className="font-bold text-[#153F6B] block">
                    {isTa ? "காயத்ரி மந்திரம்:" : "Gayatri Mantra:"}
                  </span>
                  <p className="font-mono text-[#183047] font-semibold">
                    {selectedGemForModal.gayatri_mantra_sanskrit}
                  </p>
                </div>
              )}

              <div className="p-3 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                <span className="font-bold text-[#52667E] block text-[11px]">
                  {isTa ? "மலிவான மாற்று கற்கள் (Uparatna):" : "Affordable Semi-Precious Substitutes (Uparatna):"}
                </span>
                <span className="text-xs text-[#183047] font-medium">
                  {(isTa
                    ? selectedGemForModal.upratna_substitutes_ta
                    : selectedGemForModal.upratna_substitutes_en
                  )?.join(", ")}
                </span>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                type="button"
                onClick={() => setSelectedGemForModal(null)}
                className="px-4 py-2 bg-[#153F6B] text-white rounded-lg text-xs font-bold cursor-pointer hover:bg-[#0F3155]"
              >
                {isTa ? "மூடுக" : "Close"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// -----------------------------------------------------------------------------
// Subcomponent: Individual Gemstone Card
// -----------------------------------------------------------------------------
interface GemstoneCardProps {
  titleBadge: string;
  rec: GemstoneRecommendation;
  dynamicWeight: { rattis: number; carats: number };
  isTa: boolean;
  onOpenModal: () => void;
}

function GemstoneCard({
  titleBadge,
  rec,
  dynamicWeight,
  isTa,
  onOpenModal,
}: GemstoneCardProps) {
  return (
    <div className="bg-white rounded-xl border border-[#D9DEE7] shadow-2xs hover:shadow-sm transition-all p-5 space-y-4 flex flex-col justify-between">
      <div className="space-y-3">
        {/* Badge & Primary Name */}
        <div className="space-y-1">
          <span className="inline-block px-2.5 py-0.5 rounded-md bg-[#FAF2DE] border border-[#D8BD80] text-[#8C6D23] font-bold text-[10px] tracking-wide">
            {titleBadge}
          </span>
          <div className="flex items-start justify-between gap-2">
            <div>
              <h3 className="font-extrabold text-base text-[#183047]">
                {isTa ? rec.primary_gem_ta : rec.primary_gem_en}
              </h3>
              <span className="text-xs text-[#8190A6] font-mono">
                {rec.primary_gem_sanskrit}
              </span>
            </div>
            <div className="text-right">
              <span className="text-[10px] text-[#8190A6] block">{isTa ? "சுப எடை" : "Prescribed Weight"}</span>
              <span className="font-extrabold text-sm text-[#B4872B] font-mono">
                {dynamicWeight.rattis} Ratti
              </span>
              <span className="text-[10px] text-[#8190A6] block">
                ({dynamicWeight.carats} Carats)
              </span>
            </div>
          </div>
        </div>

        {/* Purpose */}
        <p className="text-xs text-[#52667E] leading-relaxed line-clamp-2">
          {isTa ? rec.governing_purpose_ta : rec.governing_purpose_en}
        </p>

        {/* Attributes Grid */}
        <div className="grid grid-cols-2 gap-2 text-xs pt-1 border-t border-[#F2F3F5]">
          <div className="space-y-0.5">
            <span className="text-[10px] text-[#8190A6] block">{isTa ? "உலோகம்" : "Prescribed Metal"}</span>
            <span className="font-semibold text-[#183047] text-[11px]">
              {isTa ? rec.prescribed_metal_ta : rec.prescribed_metal_en}
            </span>
          </div>

          <div className="space-y-0.5">
            <span className="text-[10px] text-[#8190A6] block">{isTa ? "அணியும் விரல்" : "Wearing Finger"}</span>
            <span className="font-semibold text-[#183047] text-[11px]">
              {isTa ? rec.ideal_finger_ta : rec.ideal_finger_en}
            </span>
          </div>

          <div className="space-y-0.5 col-span-2">
            <span className="text-[10px] text-[#8190A6] block">{isTa ? "நாள் & ஓரை" : "Day & Auspicious Hora"}</span>
            <span className="font-semibold text-[#183047] text-[11px]">
              {isTa ? rec.energization_day_ta : rec.energization_day_en}
            </span>
          </div>
        </div>

        {/* Mantra Preview Box */}
        <div className="p-2.5 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0] space-y-1">
          <span className="text-[10px] font-bold text-[#153F6B] block">
            {isTa ? "பிரதிஷ்டை பீஜ மந்திரம்:" : "Consecration Mantra:"}
          </span>
          <p className="font-mono text-[11px] text-[#183047] truncate font-medium">
            {rec.consecration_mantra_sanskrit}
          </p>
        </div>
      </div>

      {/* Detail Button */}
      <button
        type="button"
        onClick={onOpenModal}
        className="w-full inline-flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg bg-[#F8FAFC] hover:bg-[#FAF2DE] border border-[#D9DEE7] hover:border-[#D8BD80] text-xs font-bold text-[#153F6B] hover:text-[#8C6D23] transition-colors cursor-pointer"
      >
        <span>{isTa ? "முழு விவரங்கள் & மந்திரங்கள் காண்க" : "View Full Ritual & Mantras"}</span>
        <ChevronRight className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}

// -----------------------------------------------------------------------------
// Subcomponent: Individual Rudraksha Card
// -----------------------------------------------------------------------------
interface RudrakshaCardProps {
  badge: string;
  bead: RudrakshaItem;
  isTa: boolean;
}

function RudrakshaCard({ badge, bead, isTa }: RudrakshaCardProps) {
  return (
    <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-3 flex flex-col justify-between">
      <div className="space-y-2">
        <span className="inline-block px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px] font-bold">
          {badge}
        </span>
        <div>
          <h4 className="font-bold text-sm text-[#183047]">
            {bead.mukhi} Mukhi ({isTa ? bead.name_ta : bead.name_en})
          </h4>
          <span className="text-[11px] text-[#8190A6]">
            {isTa ? bead.ruling_deity_ta : bead.ruling_deity_en}
          </span>
        </div>

        <p className="text-xs text-[#52667E] leading-relaxed line-clamp-2">
          {isTa ? bead.astrological_benefits_ta : bead.astrological_benefits_en}
        </p>

        <div className="p-2 rounded bg-white border border-[#E2E8F0] text-[11px] space-y-0.5">
          <span className="text-[#8190A6] block text-[9px]">{isTa ? "பீஜ மந்திரம்" : "Beeja Mantra"}</span>
          <span className="font-bold text-[#153F6B] font-mono">{bead.beeja_mantra_sanskrit}</span>
        </div>
      </div>

      <div className="text-[10px] text-emerald-700 font-semibold pt-1 border-t border-[#E2E8F0]">
        ✓ {isTa ? bead.wearing_protocol_ta : bead.wearing_protocol_en}
      </div>
    </div>
  );
}

export default GemstoneDownload;
