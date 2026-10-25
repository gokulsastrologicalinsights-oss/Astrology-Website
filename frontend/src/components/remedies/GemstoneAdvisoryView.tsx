"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import {
  GemstoneAdvisoryResponse,
  GemstoneRecommendation,
  ProhibitedGemstoneItem,
  RemedyAnalysisResponse,
} from "@/lib/types";
import { getGemstoneAdvisory } from "@/lib/api";
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
  ArrowRight,
  Flame,
} from "lucide-react";

interface GemstoneAdvisoryViewProps {
  analysisResult?: RemedyAnalysisResponse | null;
  horoscopeId?: string | null;
}

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

export function GemstoneAdvisoryView({
  analysisResult,
  horoscopeId,
}: GemstoneAdvisoryViewProps) {
  const { language } = useLanguage();
  const isTa = language === "ta";

  // Selected Lagna (defaults to chart's Lagna if available, else Aries)
  const initialLagna = analysisResult?.chart_context?.lagna_sign || "Aries";
  const [selectedLagna, setSelectedLagna] = useState<string>(initialLagna);
  const [advisory, setAdvisory] = useState<GemstoneAdvisoryResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (analysisResult?.chart_context?.lagna_sign) {
      setSelectedLagna(analysisResult.chart_context.lagna_sign);
    }
  }, [analysisResult]);

  useEffect(() => {
    async function fetchAdvisory() {
      setLoading(true);
      setError(null);
      try {
        const res = await getGemstoneAdvisory({
          ascendant_sign: selectedLagna,
          horoscope_id: horoscopeId || undefined,
        });
        setAdvisory(res);
      } catch (err: any) {
        setError(err?.message || "Failed to load gemstone advisory.");
      } finally {
        setLoading(false);
      }
    }
    fetchAdvisory();
  }, [selectedLagna, horoscopeId]);

  return (
    <div className="space-y-6">
      {/* Header & Lagna Selector Bar */}
      <div className="bg-white p-5 rounded-2xl border border-stone-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold text-[#8B6914] uppercase tracking-wider bg-[#FAF2DE] border border-[#B4872B]/30 px-3 py-1 rounded-full">
            {isTa ? "ரத்தின சாஸ்திரம் & பாதுகாப்பு விதி" : "Classical Ratna Shastra & Safety"}
          </span>
          <h2 className="text-xl sm:text-2xl font-bold font-serif text-[#153F6B] mt-1.5">
            {isTa ? "3 தூண் ரத்தின ஆலோசனை & தற்காப்பு விதிகள்" : "3-Pillar Gemstone Prescription & Safety Audit"}
          </h2>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <label className="text-xs font-semibold text-stone-600">
              {isTa ? "லக்னம் தெரிவு:" : "Ascendant (Lagna):"}
            </label>
            <select
              value={selectedLagna}
              onChange={(e) => setSelectedLagna(e.target.value)}
              className="text-sm font-semibold text-[#153F6B] bg-stone-50 border border-stone-300 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#153F6B]/30"
            >
              {LAGNA_LIST.map((sign) => (
                <option key={sign} value={sign}>
                  {isTa ? LAGNA_TAMIL[sign] || sign : sign}
                </option>
              ))}
            </select>
          </div>

          <Link
            href="/tools/gemstones-rudraksha"
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#153F6B] text-white text-xs font-bold hover:bg-[#1E4D7B] transition-colors shadow-sm"
          >
            <Sparkles className="w-3.5 h-3.5 text-[#DDA74F]" />
            <span>{isTa ? "முழுமையான ருத்ராட்ச & ரத்தின மையம்" : "Full Gemstone & Rudraksha Studio"}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {loading && (
        <div className="bg-white rounded-2xl border border-stone-200 p-12 text-center shadow-sm">
          <div className="w-10 h-10 border-4 border-[#153F6B] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-stone-600 font-medium">
            {isTa
              ? "ரத்தின விதிகள் மற்றும் கிரகப் பொருத்தங்கள் சரிபார்க்கப்படுகின்றன..."
              : "Evaluating classical gemstone rules and planetary harmonies..."}
          </p>
        </div>
      )}

      {error && !loading && (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-red-800">
          <p className="font-semibold">{isTa ? "பிழை ஏற்பட்டது" : "Error Occurred"}</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
      )}

      {advisory && !loading && (
        <>
          {/* Mandatory Astrologer Notice */}
          <div className="bg-amber-50 border border-amber-300/80 rounded-2xl p-4 sm:p-5 text-amber-950 flex items-start gap-3.5 shadow-xs">
            <ShieldAlert className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
            <div className="text-xs leading-relaxed">
              <span className="font-bold text-amber-900 block mb-1">
                {isTa ? "முக்கிய பாரம்பரிய ஜோதிட எச்சரிக்கை:" : "Mandatory Astrological Principle:"}
              </span>
              {isTa ? advisory.mandatory_review_notice_ta : advisory.mandatory_review_notice_en}
            </div>
          </div>

          {/* The 3 Pillars of Gemstones */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <GemstoneCard
              rec={advisory.life_stone}
              pillarBadge={isTa ? "தூண் 1: உயிர் ரத்தினம்" : "Pillar 1: Life Stone"}
              pillarColor="from-amber-600 to-amber-800"
              isTa={isTa}
            />
            <GemstoneCard
              rec={advisory.lucky_stone}
              pillarBadge={isTa ? "தூண் 2: புண்ணிய ரத்தினம்" : "Pillar 2: Lucky Stone"}
              pillarColor="from-blue-700 to-indigo-900"
              isTa={isTa}
            />
            <GemstoneCard
              rec={advisory.fortune_stone}
              pillarBadge={isTa ? "தூண் 3: பாக்கிய ரத்தினம்" : "Pillar 3: Fortune Stone"}
              pillarColor="from-emerald-700 to-teal-900"
              isTa={isTa}
            />
          </div>

          {/* Optional 4th Pillar: Secondary Yogakaraka / Dasha Support */}
          {advisory.secondary_support_stone && (
            <div className="bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200/80 rounded-3xl p-6">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <span className="text-2xs font-bold uppercase tracking-wider bg-purple-200 text-purple-900 px-3 py-1 rounded-full">
                    {isTa ? "கூடுதல் ஆதரவு ரத்தினம் (யோககாரகன்)" : "Secondary Support Stone (Yogakaraka)"}
                  </span>
                  <h3 className="text-lg font-bold font-serif text-[#153F6B] mt-2">
                    {isTa ? advisory.secondary_support_stone.primary_gem_ta : advisory.secondary_support_stone.primary_gem_en}{" "}
                    <span className="text-xs font-mono font-normal text-stone-500">
                      ({advisory.secondary_support_stone.primary_gem_sanskrit})
                    </span>
                  </h3>
                  <p className="text-xs text-stone-600 mt-1 max-w-2xl">
                    {isTa ? advisory.secondary_support_stone.governing_purpose_ta : advisory.secondary_support_stone.governing_purpose_en}
                  </p>
                </div>
                <div className="text-xs bg-white p-3 rounded-2xl border border-purple-200 text-purple-950 font-medium shrink-0">
                  <div><strong>{isTa ? "உலோகம்:" : "Metal:"}</strong> {isTa ? advisory.secondary_support_stone.prescribed_metal_ta : advisory.secondary_support_stone.prescribed_metal_en}</div>
                  <div><strong>{isTa ? "விரல்:" : "Finger:"}</strong> {isTa ? advisory.secondary_support_stone.ideal_finger_ta : advisory.secondary_support_stone.ideal_finger_en}</div>
                  <div><strong>{isTa ? "குறைந்தபட்ச எடை:" : "Min Weight:"}</strong> {advisory.secondary_support_stone.minimum_carats} Carats</div>
                </div>
              </div>
            </div>
          )}

          {/* Rudraksha Compatibility Quick Banner */}
          {advisory.recommended_rudraksha && (
            <div className="bg-gradient-to-r from-stone-900 via-[#153F6B] to-stone-900 text-white rounded-3xl p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div className="space-y-1.5">
                <span className="text-2xs font-bold uppercase tracking-wider text-[#F4D068] bg-white/10 px-2.5 py-0.5 rounded-full">
                  {isTa ? "பிரதிகூல சாந்தி: ருத்ராட்ச கவசம்" : "Pratikula Pacification: Rudraksha Shield"}
                </span>
                <h4 className="text-base font-bold font-serif">
                  {isTa
                    ? `${selectedLagna} லக்னத்திற்கு உகந்த ருத்ராட்சம்: ${advisory.recommended_rudraksha.primary_bead.name_ta}`
                    : `Recommended Rudraksha for ${selectedLagna}: ${advisory.recommended_rudraksha.primary_bead.name_en}`}
                </h4>
                <p className="text-xs text-stone-300 max-w-2xl">
                  {isTa
                    ? advisory.recommended_rudraksha.personal_alignment_reason_ta
                    : advisory.recommended_rudraksha.personal_alignment_reason_en}
                </p>
              </div>
              <Link
                href="/tools/gemstones-rudraksha"
                className="px-4 py-2.5 rounded-xl bg-[#FAF2DE] text-[#8B6914] text-xs font-bold hover:bg-white transition-colors shrink-0 flex items-center gap-1.5"
              >
                <span>{isTa ? "1-14 முக அட்டவணை" : "Explore 1-14 Mukhi Matrix"}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          )}

          {/* Prohibited Gemstones Red-Flag Box */}
          {advisory.prohibited_gemstones.length > 0 && (
            <div className="bg-rose-50/70 border border-rose-200 rounded-3xl p-6 shadow-sm space-y-4">
              <div className="flex items-center gap-2.5 text-rose-900">
                <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0" />
                <h3 className="text-lg font-bold font-serif">
                  {isTa
                    ? "கண்டிப்பாக அணியக் கூடாத ரத்தினங்கள் (மறைவு ஸ்தான எச்சரிக்கை)"
                    : "Strictly Prohibited Gemstones (Dusthana & Malefic Lords)"}
                </h3>
              </div>
              <p className="text-xs text-rose-800 leading-relaxed">
                {isTa
                  ? "பாரம்பரிய ஜோதிட விதி (ஜாதக பாரிஜாதம் & மணி மாலை): 6, 8, 12 போன்ற மறைவு ஸ்தான அதிபதிகளின் ரத்தினங்களை ஒருபோதும் அணியக்கூடாது. ரத்தினங்கள் கிரக கதிர்வீச்சை ஈர்க்கும் திறன் கொண்டவை; மறைவு நாதனின் கல்லை அணிவது கடன், நோய், வழக்கு, மன உளைச்சல் மற்றும் விபத்துக்களை பன்மடங்கு அதிகரிக்கும்."
                  : "Classical Jyotish Mandate (Jataka Parijata & Mani Mala): Never wear gemstones for lords of the 6th, 8th, or 12th Dusthana houses. Gemstones amplify incoming cosmic radiation; wearing a stone for an afflicted or malefic house lord magnifies debts, bodily ailments, surgeries, and financial collapse."}
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
                {advisory.prohibited_gemstones.map((pro: ProhibitedGemstoneItem) => (
                  <div
                    key={pro.graha}
                    className="bg-white border border-rose-200 rounded-2xl p-4 text-xs space-y-2 shadow-2xs"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-stone-900 text-sm">
                        {isTa ? pro.graha_name_ta : pro.graha_name_en}
                      </span>
                      <span className="bg-rose-100 text-rose-800 px-2.5 py-0.5 rounded-full font-semibold text-2xs uppercase">
                        {isTa ? "தடை செய்யப்பட்டது" : "Prohibited"}
                      </span>
                    </div>
                    <p className="text-stone-700 font-medium">
                      {isTa ? "ரத்தினம்: " : "Gemstone: "}
                      <span className="font-bold text-rose-950">
                        {isTa ? pro.primary_gem_ta : pro.primary_gem_en}
                      </span>
                    </p>
                    <p className="text-stone-600 leading-relaxed">
                      {isTa ? pro.reason_ta : pro.reason_en}
                    </p>
                    <div className="bg-stone-50 border border-stone-200 p-2.5 rounded-xl text-stone-700">
                      <span className="font-semibold text-emerald-800 block mb-0.5">
                        {isTa ? "சாத்வீக மாற்று வழி:" : "Safe Sattvic Alternative:"}
                      </span>
                      {isTa ? pro.safe_alternative_ta : pro.safe_alternative_en}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Conflicts & Wearing Rules Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Conflicting Combinations */}
            <div className="bg-white rounded-2xl border border-stone-200 p-6 shadow-sm space-y-3">
              <h4 className="text-sm font-bold text-stone-900 uppercase tracking-wider flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                {isTa ? "எதிர் கிரக ரத்தின முரண்பாடுகள்:" : "Conflicting Gemstone Combinations:"}
              </h4>
              <ul className="space-y-2 text-xs text-stone-600">
                {(isTa ? advisory.conflicting_combinations_warning_ta : advisory.conflicting_combinations_warning_en).map(
                  (rule, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-amber-600 font-bold">•</span>
                      <span>{rule}</span>
                    </li>
                  )
                )}
              </ul>
            </div>

            {/* General Wearing Rules */}
            <div className="bg-white rounded-2xl border border-stone-200 p-6 shadow-sm space-y-3">
              <h4 className="text-sm font-bold text-stone-900 uppercase tracking-wider flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                {isTa ? "ரத்தினம் அணியும் நியதிகள்:" : "General Wearing & Cleansing Vidhi:"}
              </h4>
              <ul className="space-y-2 text-xs text-stone-600">
                {(isTa ? advisory.general_wearing_rules_ta : advisory.general_wearing_rules_en).map(
                  (rule, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-emerald-600 font-bold">•</span>
                      <span>{rule}</span>
                    </li>
                  )
                )}
              </ul>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function GemstoneCard({
  rec,
  pillarBadge,
  pillarColor,
  isTa,
}: {
  rec: GemstoneRecommendation;
  pillarBadge: string;
  pillarColor: string;
  isTa: boolean;
}) {
  return (
    <div className="bg-white rounded-3xl border border-stone-200 shadow-sm overflow-hidden flex flex-col justify-between">
      <div>
        {/* Card Header */}
        <div className={`bg-gradient-to-r ${pillarColor} p-5 text-white space-y-1.5`}>
          <span className="text-2xs font-bold uppercase tracking-wider bg-white/20 backdrop-blur-xs px-2.5 py-0.5 rounded-full">
            {pillarBadge}
          </span>
          <h3 className="text-xl font-bold font-serif">
            {isTa ? rec.primary_gem_ta : rec.primary_gem_en}
          </h3>
          <p className="text-xs text-stone-200 italic font-serif">
            {rec.primary_gem_sanskrit}
          </p>
        </div>

        {/* Card Body */}
        <div className="p-5 space-y-4 text-xs">
          {/* Purpose */}
          <p className="text-stone-700 leading-relaxed font-medium">
            {isTa ? rec.governing_purpose_ta : rec.governing_purpose_en}
          </p>

          {/* Astrological Justification */}
          <div className="bg-stone-50 border border-stone-200 p-3 rounded-xl space-y-1">
            <span className="font-semibold text-stone-800 block">
              {isTa ? "ஜோதிட காரணம்:" : "Astrological Justification:"}
            </span>
            <p className="text-stone-600 leading-relaxed">
              {isTa ? rec.astrological_justification_ta : rec.astrological_justification_en}
            </p>
          </div>

          {/* Specifications Grid */}
          <div className="grid grid-cols-2 gap-2 text-2xs pt-1">
            <div className="bg-stone-50 p-2.5 rounded-lg border border-stone-100">
              <span className="text-stone-400 block">{isTa ? "உலோகம்:" : "Metal:"}</span>
              <span className="font-bold text-stone-800">
                {isTa ? rec.prescribed_metal_ta : rec.prescribed_metal_en}
              </span>
            </div>
            <div className="bg-stone-50 p-2.5 rounded-lg border border-stone-100">
              <span className="text-stone-400 block">{isTa ? "விரல்:" : "Finger:"}</span>
              <span className="font-bold text-stone-800">
                {isTa ? rec.ideal_finger_ta : rec.ideal_finger_en}
              </span>
            </div>
            <div className="bg-stone-50 p-2.5 rounded-lg border border-stone-100">
              <span className="text-stone-400 block">{isTa ? "குறைந்தபட்ச எடை:" : "Min Weight:"}</span>
              <span className="font-bold text-stone-800">
                {rec.minimum_rattis ? `${rec.minimum_rattis} Ratti / ` : ""}
                {rec.minimum_carats} Carats
              </span>
            </div>
            <div className="bg-stone-50 p-2.5 rounded-lg border border-stone-100">
              <span className="text-stone-400 block">{isTa ? "அணியும் நாள்:" : "Day & Time:"}</span>
              <span className="font-bold text-stone-800">
                {isTa ? rec.energization_day_ta : rec.energization_day_en}
              </span>
            </div>
          </div>

          {/* Consecration Mantra */}
          <div className="bg-amber-50/70 border border-amber-200 p-3 rounded-xl space-y-1">
            <span className="font-semibold text-amber-900 block flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5 text-amber-700" />
              {isTa ? "பிரதிஷ்டை மூல மந்திரம் (108 முறை):" : "Consecration Mantra (108x):"}
            </span>
            <p className="font-serif font-bold text-amber-950 text-xs">
              {rec.consecration_mantra_sanskrit}
            </p>
            <p className="text-amber-800 text-2xs italic">
              {rec.consecration_mantra_ta}
            </p>
          </div>

          {/* Budget Uparatna Substitutes */}
          <div>
            <span className="font-semibold text-stone-700 block mb-1">
              {isTa ? "எளிய உப-ரத்தின மாற்று (Uparatna):" : "Affordable Semi-Precious Substitutes:"}
            </span>
            <div className="flex flex-wrap gap-1.5">
              {(isTa ? rec.upratna_substitutes_ta : rec.upratna_substitutes_en).map((up, i) => (
                <span
                  key={i}
                  className="bg-stone-100 text-stone-700 px-2 py-0.5 rounded-md text-2xs font-medium"
                >
                  {up}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Footer Conflict Warning */}
      {rec.incompatible_gems_warning_en && (
        <div className="bg-stone-50 border-t border-stone-200 px-5 py-3 text-2xs text-stone-500">
          <span className="font-semibold text-amber-800">
            {isTa ? "முரண்பாடு எச்சரிக்கை: " : "Conflict Note: "}
          </span>
          {isTa ? rec.incompatible_gems_warning_ta : rec.incompatible_gems_warning_en}
        </div>
      )}
    </div>
  );
}
