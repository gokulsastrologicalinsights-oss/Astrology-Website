"use client";

import React, { useState, useMemo, useRef } from "react";
import { FullHoroscopeResult } from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import { LanguageCode } from "@/lib/translations";
import {
  extractDestinyCardData,
  renderDestinyCardToCanvas,
  downloadDestinyCardPng,
  formatCompactDeg,
  DestinyCardData,
} from "@/lib/destiny-card-utils";
import {
  Download,
  Sparkles,
  ShieldCheck,
  Eye,
  Calendar,
  Compass,
  Moon,
  Clock,
  Sun,
  AlertCircle,
  CheckCircle2,
  Lock,
} from "lucide-react";

interface DestinyCardProps {
  result: FullHoroscopeResult | null;
}

export function DestinyCard({ result }: DestinyCardProps) {
  const { language: globalLang, t } = useLanguage();
  const [cardLang, setCardLang] = useState<LanguageCode>(globalLang);
  const [includeBirthDate, setIncludeBirthDate] = useState<boolean>(false);
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const [exportSuccess, setExportSuccess] = useState<boolean>(false);

  // Synchronize initial language change from global context if user hasn't explicitly set local
  React.useEffect(() => {
    setCardLang(globalLang);
  }, [globalLang]);

  // Extract verified astrological identity
  const cardData = useMemo(() => {
    return extractDestinyCardData(result, includeBirthDate);
  }, [result, includeBirthDate]);

  const handleDownload = async () => {
    if (!cardData || isExporting) return;
    setIsExporting(true);
    setExportSuccess(false);
    try {
      await downloadDestinyCardPng(cardData, cardLang);
      setExportSuccess(true);
      setTimeout(() => setExportSuccess(false), 4000);
    } catch (err) {
      console.error("Failed to export Destiny Card PNG:", err);
    } finally {
      setIsExporting(false);
    }
  };

  // Fallback for missing or unverified calculation data
  if (!result || !cardData) {
    return (
      <div className="p-8 rounded-2xl border border-amber-200/80 bg-gradient-to-b from-amber-50/50 to-orange-50/30 text-center space-y-4 max-w-2xl mx-auto shadow-sm">
        <div className="w-12 h-12 rounded-full bg-amber-100 flex items-center justify-center mx-auto text-amber-700">
          <AlertCircle className="w-6 h-6" />
        </div>
        <div className="space-y-1.5">
          <h3 className="font-serif text-lg font-bold text-amber-950">
            {t.destinyCardMissingData || "Authoritative calculation data is required to generate the Destiny Card."}
          </h3>
          <p className="text-xs text-amber-800/80 max-w-md mx-auto leading-relaxed">
            {cardLang === "ta"
              ? "விதி அட்டை உருவாக்கத்திற்கு லக்னம், சந்திரன், ஜன்ம நட்சத்திரம் மற்றும் விம்சோத்தரி தசா தரவுகள் தேவைப்படுகின்றன. முழுமையான ஜாதகக் கணிப்பை உறுதி செய்யவும்."
              : "The Destiny Card requires verified Ascendant, Moon sign, Nakshatra, and Vimshottari Dasa data from the calculation engine."}
          </p>
        </div>
      </div>
    );
  }

  const isTa = cardLang === "ta";

  return (
    <div className="space-y-6">
      {/* Control Bar: Language, Privacy, and Export Button */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 p-4 rounded-xl bg-white border border-[#E2DCD5] shadow-xs">
        <div className="flex flex-wrap items-center gap-4 text-xs">
          {/* Language Switcher */}
          <div className="flex items-center gap-1.5">
            <span className="font-semibold text-slate-600">
              {t.destinyCardSwitchLang || "Card Language"}:
            </span>
            <div className="inline-flex rounded-lg border border-[#E2DCD5] bg-[#FAF8F5] p-0.5">
              <button
                type="button"
                onClick={() => setCardLang("en")}
                className={`px-2.5 py-1 rounded-md font-semibold transition-all ${
                  cardLang === "en"
                    ? "bg-[#0F172A] text-white shadow-2xs"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                English
              </button>
              <button
                type="button"
                onClick={() => setCardLang("ta")}
                className={`px-2.5 py-1 rounded-md font-semibold transition-all ${
                  cardLang === "ta"
                    ? "bg-[#0F172A] text-white shadow-2xs"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                தமிழ்
              </button>
            </div>
          </div>

          {/* Privacy Toggle: Include Birth Date */}
          <label className="flex items-center gap-2 cursor-pointer select-none text-slate-700 hover:text-slate-900 transition-colors">
            <input
              type="checkbox"
              checked={includeBirthDate}
              onChange={(e) => setIncludeBirthDate(e.target.checked)}
              className="w-4 h-4 rounded text-amber-600 border-slate-300 focus:ring-amber-500"
            />
            <span className="font-medium">
              {t.destinyCardShowDate || "Include Birth Date"}
            </span>
          </label>
        </div>

        {/* Action Button: Download PNG */}
        <div className="flex items-center gap-3">
          {exportSuccess && (
            <span className="text-xs font-semibold text-emerald-600 flex items-center gap-1 animate-fade-in">
              <CheckCircle2 className="w-4 h-4" />
              <span>{isTa ? "பதிவிறக்கம் செய்யப்பட்டது!" : "Downloaded!"}</span>
            </span>
          )}
          <button
            type="button"
            onClick={handleDownload}
            disabled={isExporting}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-750 hover:to-amber-800 text-white font-bold text-xs shadow-sm hover:shadow transition-all disabled:opacity-50 cursor-pointer"
          >
            {isExporting ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>{t.destinyCardGenerating || "Generating Image..."}</span>
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                <span>{t.destinyCardDownload || "Download High-Res PNG"}</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Visual Destiny Card: High-Fidelity Preview Box */}
      <div className="relative max-w-2xl mx-auto rounded-3xl p-1 bg-gradient-to-b from-[#E5A93C] via-[#8C6D23] to-[#5C3D10] shadow-2xl">
        <div className="relative rounded-[22px] bg-gradient-to-b from-[#110501] via-[#1D0A03] to-[#0A0301] p-6 sm:p-10 text-white overflow-hidden border border-[#E5A93C]/40">
          {/* Subtle Radiant Ambient Background Halo */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />

          {/* Card Corner Ornaments */}
          <div className="absolute top-4 left-4 w-6 h-6 border-t-2 border-l-2 border-amber-400/80 rounded-tl pointer-events-none" />
          <div className="absolute top-4 right-4 w-6 h-6 border-t-2 border-r-2 border-amber-400/80 rounded-tr pointer-events-none" />
          <div className="absolute bottom-4 left-4 w-6 h-6 border-b-2 border-l-2 border-amber-400/80 rounded-bl pointer-events-none" />
          <div className="absolute bottom-4 right-4 w-6 h-6 border-b-2 border-r-2 border-amber-400/80 rounded-br pointer-events-none" />

          {/* Header Sacred Symbol & Branding */}
          <div className="text-center relative z-10 space-y-2">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-gradient-to-b from-amber-500/20 to-amber-900/40 border border-amber-400/60 shadow-lg text-amber-300 font-serif text-2xl font-bold mb-1">
              {isTa ? "ௐ" : "ॐ"}
            </div>

            <div>
              <span className="text-[11px] tracking-widest uppercase font-semibold text-amber-400/90 block">
                {isTa ? "கோகுலின் ஜோதிட நுண்ணறிவு" : "GOKUL'S ASTROLOGICAL INSIGHTS"}
              </span>
              <h2 className="font-serif text-2xl sm:text-3xl font-bold tracking-wide text-amber-50">
                {isTa ? "வேத விதி அட்டை" : "VEDIC DESTINY CARD"}
              </h2>
            </div>

            {/* Ornamental Divider */}
            <div className="flex items-center justify-center gap-3 py-1">
              <div className="h-[1px] w-20 sm:w-28 bg-gradient-to-r from-transparent via-amber-400/70 to-transparent" />
              <span className="text-amber-400 text-xs">◆</span>
              <div className="h-[1px] w-20 sm:w-28 bg-gradient-to-r from-transparent via-amber-400/70 to-transparent" />
            </div>

            {/* Person's Name */}
            <div className="pt-1">
              <h3 className="font-serif text-xl sm:text-2xl font-bold text-amber-200">
                {cardData.personName || (isTa ? "வேத சாதகர்" : "Vedic Seeker")}
              </h3>
              {cardData.birthDateDisplay && (
                <p className="text-xs text-amber-100/70 mt-0.5 flex items-center justify-center gap-1">
                  <Calendar className="w-3 h-3 text-amber-400" />
                  <span>
                    {isTa ? "பிறந்த தேதி" : "Date of Birth"}: {cardData.birthDateDisplay}
                  </span>
                </p>
              )}
            </div>
          </div>

          {/* 4 Main Core Identity Pillars (2x2 Grid) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-8 relative z-10">
            {/* 1. Ascendant (Lagna) */}
            <div className="p-4 rounded-xl bg-black/40 border border-amber-500/25 space-y-2 hover:border-amber-500/40 transition-colors">
              <div className="flex items-center justify-between text-xs text-amber-400 font-semibold tracking-wider uppercase">
                <span className="flex items-center gap-1.5">
                  <Compass className="w-4 h-4 text-orange-400" />
                  <span>{isTa ? "லக்னம்" : "Ascendant (Lagna)"}</span>
                </span>
                <span className="text-[11px] font-mono text-amber-200/70">
                  {formatCompactDeg(cardData.ascendantDegree)}
                </span>
              </div>
              <div className="font-serif text-xl font-bold text-white">
                {isTa ? cardData.ascendantSignTa : cardData.ascendantSignEn}
              </div>
              <div className="text-[11px] text-amber-200/80">
                {cardData.ascendantNakshatraEn ? (
                  <span>
                    {isTa ? "நட்சத்திரம்" : "Star"}:{" "}
                    <strong className="text-amber-300">
                      {isTa ? cardData.ascendantNakshatraTa : cardData.ascendantNakshatraEn}
                    </strong>
                    {cardData.ascendantPada ? ` (${isTa ? "பாதம்" : "Pada"} ${cardData.ascendantPada})` : ""}
                  </span>
                ) : (
                  <span>{isTa ? "ஜன்ம உதய லக்னம்" : "Rising Horizon"}</span>
                )}
              </div>
            </div>

            {/* 2. Moon Sign (Rasi) */}
            <div className="p-4 rounded-xl bg-black/40 border border-amber-500/25 space-y-2 hover:border-amber-500/40 transition-colors">
              <div className="flex items-center justify-between text-xs text-amber-400 font-semibold tracking-wider uppercase">
                <span className="flex items-center gap-1.5">
                  <Moon className="w-4 h-4 text-blue-300" />
                  <span>{isTa ? "சந்திர ராசி" : "Moon Sign (Rasi)"}</span>
                </span>
                <span className="text-[11px] font-mono text-amber-200/70">
                  {formatCompactDeg(cardData.moonDegree)}
                </span>
              </div>
              <div className="font-serif text-xl font-bold text-white">
                {isTa ? cardData.moonSignTa : cardData.moonSignEn}
              </div>
              <div className="text-[11px] text-amber-200/80">
                <span>{isTa ? "மனோகாரகன் · மனநிலை" : "Mind & Consciousness"}</span>
              </div>
            </div>

            {/* 3. Birth Star (Nakshatra) & Pada */}
            <div className="p-4 rounded-xl bg-black/40 border border-amber-500/25 space-y-2 hover:border-amber-500/40 transition-colors">
              <div className="flex items-center justify-between text-xs text-amber-400 font-semibold tracking-wider uppercase">
                <span className="flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4 text-amber-400" />
                  <span>{isTa ? "ஜன்ம நட்சத்திரம்" : "Birth Star"}</span>
                </span>
                <span className="text-[11px] font-bold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300">
                  {isTa ? `பாதம் ${cardData.pada}` : `Pada ${cardData.pada}`}
                </span>
              </div>
              <div className="font-serif text-xl font-bold text-white">
                {isTa ? cardData.nakshatraTa : cardData.nakshatraEn}
              </div>
              <div className="text-[11px] text-amber-200/80">
                <span>
                  {isTa ? "நட்சத்திர அதிபதி" : "Star Lord"}:{" "}
                  <strong className="text-amber-300">
                    {isTa ? cardData.starLordTa : cardData.starLordEn}
                  </strong>
                </span>
              </div>
            </div>

            {/* 4. Active Mahadasha */}
            <div className="p-4 rounded-xl bg-black/40 border border-amber-500/25 space-y-2 hover:border-amber-500/40 transition-colors">
              <div className="flex items-center justify-between text-xs text-amber-400 font-semibold tracking-wider uppercase">
                <span className="flex items-center gap-1.5">
                  <Clock className="w-4 h-4 text-emerald-400" />
                  <span>
                    {cardData.isCurrentDasa
                      ? isTa
                        ? "தற்போதைய தசா"
                        : "Active Mahadasha"
                      : isTa
                      ? "ஜன்ம மகா தசா"
                      : "Birth Mahadasha"}
                  </span>
                </span>
              </div>
              <div className="font-serif text-xl font-bold text-white">
                {isTa ? `${cardData.dasaLordTa} தசா` : `${cardData.dasaLordEn} Dasa`}
              </div>
              <div className="text-[11px] text-amber-200/80">
                {cardData.antardashaLordEn ? (
                  <span>
                    {isTa ? "அந்தர்தசா" : "Antardasha"}:{" "}
                    <strong className="text-amber-300">
                      {isTa ? cardData.antardashaLordTa : cardData.antardashaLordEn}
                    </strong>
                  </span>
                ) : (
                  <span>{isTa ? "விம்சோத்தரி தசா இயக்கம்" : "Vimshottari Dasa Cycle"}</span>
                )}
              </div>
            </div>
          </div>

          {/* 5. Secondary Banner: Sun Sign & Ayanamsa */}
          <div className="mt-4 p-3.5 rounded-xl bg-gradient-to-r from-amber-950/40 via-amber-900/30 to-amber-950/40 border border-amber-500/25 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs relative z-10">
            <div className="flex items-center gap-2">
              <Sun className="w-4 h-4 text-amber-400 shrink-0" />
              <div>
                <span className="text-amber-300/80 font-medium">
                  {isTa ? "சூரிய ராசி" : "Sun Sign"}:
                </span>{" "}
                <strong className="text-white">
                  {cardData.sunSignEn
                    ? `${isTa ? cardData.sunSignTa : cardData.sunSignEn}${
                        typeof cardData.sunDegree === "number"
                          ? ` (${formatCompactDeg(cardData.sunDegree)})`
                          : ""
                      }`
                    : "—"}
                </strong>
              </div>
            </div>

            <div className="flex items-center gap-1 text-[11px] text-amber-300/80">
              <span>{isTa ? "அயனாம்சம்" : "Ayanamsa"}:</span>
              <strong className="text-amber-200">{cardData.ayanamsaName}</strong>
            </div>
          </div>

          {/* Sacred Verse Watermark */}
          <div className="mt-6 text-center text-xs italic text-amber-200/60 relative z-10">
            {isTa
              ? "“யாதும் ஊரே யாவரும் கேளிர் · நன்மை தீமை பிறர்தர வாரா”"
              : "“सर्वे भवन्तु सुखिनः सर्वे सन्तु निरामयाः · May cosmic harmony illuminate your path”"}
          </div>

          {/* Card Footer: Verified Calculation & Privacy Badges */}
          <div className="mt-6 pt-4 border-t border-amber-400/20 text-center relative z-10 space-y-1">
            <div className="flex items-center justify-center gap-1.5 text-xs font-semibold text-emerald-400">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>
                {isTa
                  ? "XALEN துல்லிய எபிமெரிஸ் கணிப்பு மூலம் சரிபார்க்கப்பட்டது"
                  : "Verified Calculation · XALEN Astronomical Engine"}
              </span>
            </div>
            <p className="text-[10px] text-amber-200/50 flex items-center justify-center gap-1">
              <Lock className="w-2.5 h-2.5" />
              <span>
                {isTa
                  ? "அதிகாரப்பூர்வ வேத ஜாதக சாரம் · துல்லிய அட்ச/தீர்க்க ரேகைகள் பாதுகாக்கப்பட்டவை"
                  : "Official Vedic Horoscope Essence · Sensitive Coordinates Excluded"}
              </span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
