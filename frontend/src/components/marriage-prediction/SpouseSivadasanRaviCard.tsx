"use client";

import React, { useState } from "react";
import { SpousePredictionResponse } from "@/lib/types";
import {
  Briefcase,
  Clock,
  Heart,
  Compass,
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  AlertCircle,
  BookOpen,
  Home,
  Users,
  MapPin,
  Flame,
  Shield,
  Layers,
  Star,
  ChevronDown,
  ChevronUp,
  Award,
} from "lucide-react";

interface SpouseSivadasanRaviCardProps {
  data: SpousePredictionResponse;
  language: "en" | "ta";
}

export function SpouseSivadasanRaviCard({ data, language }: SpouseSivadasanRaviCardProps) {
  const [activeTab, setActiveTab] = useState<"sivadasan_ravi" | "kp_reader4" | "vedic_profile" | "navamsa_d9" | "traits">("sivadasan_ravi");
  const ravi = data.sivadasan_ravi_insights;

  return (
    <div className="space-y-6">
      {/* Overview Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-[#FAF2DE] via-white to-amber-50/40 border border-[#B4872B]/30 shadow-2xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-[#B4872B]/10 text-[#8E6516] border border-[#B4872B]/20">
              <Sparkles className="w-3.5 h-3.5 text-[#B4872B]" />
              {language === "ta" ? "களத்திர பாவ & வாழ்க்கைத் துணை ஜோதிட ஆய்வு" : "Spouse & Partner Nature Astrological Profile"}
            </div>
            <h3 className="text-xl font-black text-[#153F6B] mt-2">
              {language === "ta" ? data.summary_headline_ta : data.summary_headline_en}
            </h3>
            <p className="text-xs sm:text-sm text-slate-600 mt-1 max-w-3xl leading-relaxed">
              {language === "ta" ? data.summary_text_ta : data.summary_text_en}
            </p>
          </div>

          <div className="flex flex-row md:flex-col items-center md:items-end gap-2 shrink-0 bg-white/80 p-3.5 rounded-xl border border-amber-200/60">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
              {language === "ta" ? "லக்னம் & ராசி" : "Lagna & Moon"}
            </span>
            <div className="text-sm font-black text-[#153F6B]">
              {language === "ta"
                ? `${data.ascendant_sign_tamil} லக்னம் / ${data.moon_sign_tamil} ராசி`
                : `${data.ascendant_sign} Asc / ${data.moon_sign} Moon`}
            </div>
            <span className="text-[10px] text-amber-700 font-medium">
              {language === "ta"
                ? `7-ஆம் அதிபதி: ${data.seventh_lord.lord_planet_tamil} (${data.seventh_lord.sign_tamil})`
                : `7th Lord: ${data.seventh_lord.lord_planet} in ${data.seventh_lord.sign}`}
            </span>
          </div>
        </div>
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-2">
        {[
          {
            id: "sivadasan_ravi",
            labelEn: "Sivadasan Ravi Key Rules",
            labelTa: "சித்தயோகி திறவுகோல் விதிகள்",
            icon: BookOpen,
          },
          {
            id: "kp_reader4",
            labelEn: "KP Reader IV (Prof. KSK)",
            labelTa: "கே.பி. ரீடர் 4 (பேரா. கே.எஸ்.கே)",
            icon: Sparkles,
          },
          {
            id: "vedic_profile",
            labelEn: "7th House & Partner Type",
            labelTa: "7-ஆம் பாவம் & துணை குணம்",
            icon: Heart,
          },
          {
            id: "navamsa_d9",
            labelEn: "Navamsa (D9) Inner Nature",
            labelTa: "நவாம்சம் (D9) உள்தன்மை",
            icon: Layers,
          },
          {
            id: "traits",
            labelEn: "Partner Trait Ratings",
            labelTa: "துணை பண்பு மதிப்பீடு",
            icon: Star,
          },
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2.5 text-xs sm:text-sm font-bold rounded-xl transition cursor-pointer ${
                activeTab === tab.id
                  ? "bg-[#153F6B] text-white shadow-sm"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200/80"
              }`}
            >
              <Icon className="w-4 h-4" />
              {language === "ta" ? tab.labelTa : tab.labelEn}
            </button>
          );
        })}
      </div>

      {/* TAB 1: SIVADASAN RAVI SPECIAL TREATISE RULES */}
      {activeTab === "sivadasan_ravi" && ravi && (
        <div className="space-y-6">
          {/* Treatise Credit Banner */}
          <div className="p-4 rounded-xl bg-amber-50/70 border border-amber-200 flex items-start gap-3">
            <BookOpen className="w-5 h-5 text-[#B4872B] shrink-0 mt-0.5" />
            <div className="text-xs">
              <div className="font-bold text-[#153F6B]">
                {language === "ta"
                  ? "திருமண யோக பொருத்த திறவுகோல் - சித்தயோகி சிவதாசன் ரவி"
                  : "Thirumana Yoga Porutha Thiravukol - Siddhayogi Sivadasan Ravi"}
              </div>
              <p className="text-slate-600 mt-0.5 leading-relaxed">
                {language === "ta"
                  ? "மரபு ஜாதகக் கணக்கீடுகளின்படி தனி ஒரு குழந்தையா, கூட்டுக் குடும்பமா, வாழ்க்கைத் துணையின் வீதி அமைப்பு (கிழக்கு-மேற்கு / வடக்கு-தெற்கு), அமையும் திசை, காதல் திருமணம், இரு தார யோகம் மற்றும் 4 திருமணத் தடை விதிகள் ஆகியவற்றின் துல்லிய ஆய்வு."
                  : "Canonical predictions covering single child vs siblings, family size, spouse street orientation (East-West vs North-South), spouse arrival direction, candidate stars, love vs arranged marriage, dual marriage indicators, and the classical 4-point obstruction test."}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* 1. Single Child vs Siblings */}
            <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                  <Users className="w-4 h-4 text-[#B4872B]" />
                  {language === "ta" ? "1. தனி ஒரு குழந்தையா?" : "1. Single Child Indicator"}
                </span>
                <span
                  className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                    ravi.is_single_child
                      ? "bg-amber-100 text-amber-900 border border-amber-300"
                      : "bg-emerald-100 text-emerald-900 border border-emerald-300"
                  }`}
                >
                  {language === "ta" ? ravi.single_child_status_ta : ravi.single_child_status_en}
                </span>
              </div>
              <p className="text-xs text-slate-700 leading-relaxed">
                {language === "ta" ? ravi.single_child_analysis_ta : ravi.single_child_analysis_en}
              </p>
              <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-600">
                <span>{language === "ta" ? "உடன் பிறந்தோர் எண்ணிக்கை மதிப்பீடு:" : "Estimated Siblings:"}</span>
                <span className="font-bold text-[#153F6B]">{ravi.estimated_siblings_count}</span>
              </div>
              <p className="text-[11px] text-slate-500 italic">
                {language === "ta" ? ravi.siblings_analysis_ta : ravi.siblings_analysis_en}
              </p>
            </div>

            {/* 2. Family Size */}
            <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                  <Home className="w-4 h-4 text-[#B4872B]" />
                  {language === "ta" ? "2. குடும்ப அமைப்பு" : "2. Family Size"}
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-50 text-blue-800 border border-blue-200">
                  {language === "ta" ? ravi.family_size_ta : ravi.family_size}
                </span>
              </div>
              <p className="text-xs text-slate-700 leading-relaxed">
                {language === "ta" ? ravi.family_size_analysis_ta : ravi.family_size_analysis_en}
              </p>
            </div>

            {/* 3. Street Orientation */}
            <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                  <Compass className="w-4 h-4 text-[#B4872B]" />
                  {language === "ta" ? "3. துணையின் வீதி அமைப்பு" : "3. Spouse Street Orientation"}
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-purple-50 text-purple-800 border border-purple-200">
                  {language === "ta" ? ravi.street_orientation_ta : ravi.street_orientation_en}
                </span>
              </div>
              <p className="text-xs text-slate-700 leading-relaxed">
                {language === "ta" ? ravi.street_orientation_analysis_ta : ravi.street_orientation_analysis_en}
              </p>
            </div>

            {/* 4. Spouse Direction */}
            <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                  <MapPin className="w-4 h-4 text-[#B4872B]" />
                  {language === "ta" ? "4. துணை அமையும் திசை" : "4. Spouse Arrival Direction"}
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-50 text-amber-900 border border-amber-300 font-semibold">
                  {language === "ta" ? ravi.spouse_direction_ta : ravi.spouse_direction_en}
                </span>
              </div>
              <p className="text-xs text-slate-700 leading-relaxed">
                {language === "ta" ? ravi.spouse_direction_analysis_ta : ravi.spouse_direction_analysis_en}
              </p>
            </div>

            {/* 5. Love Marriage Probability */}
            <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                  <Heart className="w-4 h-4 text-rose-500" />
                  {language === "ta" ? "5. காதல் திருமண வாய்ப்பு" : "5. Love Marriage Probability"}
                </span>
                <span
                  className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                    ravi.love_marriage_probability === "High"
                      ? "bg-rose-100 text-rose-800 border border-rose-300"
                      : ravi.love_marriage_probability === "Moderate"
                      ? "bg-amber-100 text-amber-800 border border-amber-300"
                      : "bg-slate-100 text-slate-700 border border-slate-300"
                  }`}
                >
                  {language === "ta" ? ravi.love_marriage_probability_ta : ravi.love_marriage_probability}
                </span>
              </div>
              <p className="text-xs text-slate-700 leading-relaxed">
                {language === "ta" ? ravi.love_marriage_analysis_ta : ravi.love_marriage_analysis_en}
              </p>
            </div>

            {/* 6. Dual Marriage Risk */}
            <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                  <Shield className="w-4 h-4 text-[#153F6B]" />
                  {language === "ta" ? "6. இரு தார யோக ஆய்வு" : "6. Dual Marriage Assessment"}
                </span>
                <span
                  className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                    ravi.dual_marriage_risk.includes("High")
                      ? "bg-rose-100 text-rose-800 border border-rose-300"
                      : "bg-emerald-100 text-emerald-800 border border-emerald-300"
                  }`}
                >
                  {language === "ta" ? ravi.dual_marriage_risk_ta : ravi.dual_marriage_risk}
                </span>
              </div>
              <p className="text-xs text-slate-700 leading-relaxed">
                {language === "ta" ? ravi.dual_marriage_analysis_ta : ravi.dual_marriage_analysis_en}
              </p>
            </div>
          </div>

          {/* 7. Candidate Nakshatras */}
          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                <Star className="w-4 h-4 text-[#B4872B]" />
                {language === "ta" ? "7. துணையாக வரக்கூடிய உத்தம நட்சத்திரங்கள்" : "7. Candidate Spouse Nakshatras"}
              </span>
              <span className="text-[11px] font-semibold text-slate-500">
                {language === "ta" ? "திரிகோண & அதிபதி நட்சத்திரங்கள்" : "Trinal & Rasi Lord Stars"}
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {(language === "ta" ? ravi.candidate_nakshatras_ta : ravi.candidate_nakshatras_en).map((star, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 rounded-lg text-xs font-bold bg-[#FAF2DE] text-[#8E6516] border border-[#B4872B]/30"
                >
                  {star}
                </span>
              ))}
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              {language === "ta" ? ravi.candidate_nakshatras_analysis_ta : ravi.candidate_nakshatras_analysis_en}
            </p>
          </div>

          {/* 8. 4-Point Permanent Obstruction Test */}
          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-amber-600" />
                <h4 className="font-bold text-sm sm:text-base text-[#153F6B]">
                  {language === "ta"
                    ? "8. திருமணத் தடை - 4 முக்கிய சாஸ்திர விதிகள் ஆய்வு"
                    : "8. 4-Point Classical Marriage Obstruction Test"}
                </h4>
              </div>
              <span
                className={`px-3 py-1 rounded-full text-xs font-bold ${
                  ravi.marriage_obstruction_score === 0
                    ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                    : ravi.marriage_obstruction_score <= 2
                    ? "bg-amber-100 text-amber-800 border border-amber-300"
                    : "bg-rose-100 text-rose-800 border border-rose-300"
                }`}
              >
                {language === "ta" ? ravi.marriage_obstruction_verdict_ta : ravi.marriage_obstruction_verdict}
              </span>
            </div>
            <p className="text-xs text-slate-700 leading-relaxed">
              {language === "ta" ? ravi.marriage_obstruction_analysis_ta : ravi.marriage_obstruction_analysis_en}
            </p>
          </div>

          {/* 9. Sacred Thirumurai & Classical Remedies */}
          {ravi.sacred_remedies_ta && ravi.sacred_remedies_ta.length > 0 && (
            <div className="p-5 rounded-2xl bg-gradient-to-br from-amber-50/60 to-white border border-amber-200 shadow-2xs space-y-3">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-amber-700" />
                <h4 className="font-bold text-sm sm:text-base text-[#153F6B]">
                  {language === "ta"
                    ? "9. சிவதாசன் ரவி பரிந்துரைக்கும் திருமுறைப் பரிகாரங்கள்"
                    : "9. Sacred Thirumurai & Vedic Marriage Remedies"}
                </h4>
              </div>
              <ul className="space-y-2 text-xs text-slate-700">
                {ravi.sacred_remedies_ta.map((remedy, idx) => (
                  <li key={idx} className="flex items-start gap-2 bg-white/80 p-2.5 rounded-lg border border-amber-100">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                    <span className="leading-relaxed">{remedy}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: VEDIC PROFILE & 7TH HOUSE OCCUPANTS/ASPECTS */}
      
      {/* TAB: KP READER 4 STELLAR INSIGHTS */}
      {activeTab === "kp_reader4" && (
        <div className="space-y-6">
          {/* Header Banner */}
          <div className="p-4 rounded-xl bg-blue-50/70 border border-blue-200 flex items-start gap-3">
            <Sparkles className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-bold text-blue-900">
                {language === "ta"
                  ? "கே.பி. ரீடர் 4: திருமணம், இல்லற வாழ்க்கை & குழந்தைப்பேறு (பேரா. கே. எஸ். கிருஷ்ணமூர்த்தி)"
                  : "KP Stellar Reader IV: Marriage, Married Life & Children (Prof. K. S. Krishnamurti)"}
              </h4>
              <p className="text-xs text-blue-700/90 mt-0.5 leading-relaxed">
                {language === "ta"
                  ? "7-ஆம் உப அதிபதி (CSL), 4-ஆம் உப அதிபதி (பணிபுரியும் மனைவி), புனர்பூ தோஷம், மற்றும் செவ்வாய் தோஷ KP தீர்ப்பு."
                  : "7th Cuspal Sub-Lord (CSL) partner appearance, 4th CSL career spouse assessment, Punarphoo delay detection, and authentic Mars Dosha KP override."}
              </p>
            </div>
          </div>

          {data.kp_reader4_insights ? (
            <div className="space-y-6">
              {/* Grid 1: 7th CSL & Partner Appearance */}
              <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <div className="flex items-center gap-2">
                    <Users className="w-4 h-4 text-[#B4872B]" />
                    <span className="font-bold text-sm text-[#153F6B]">
                      {language === "ta" ? "துணையின் உடல் தோற்றம் & குணம் (7-ஆம் CSL)" : "Partner Physical Features & Temperament (7th CSL)"}
                    </span>
                  </div>
                  <span className="text-xs font-black px-2.5 py-1 rounded-full bg-blue-100 text-blue-800">
                    {data.kp_reader4_insights.seventh_csl_planet} in {data.kp_reader4_insights.seventh_csl_sign}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
                    <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                      {language === "ta" ? "உடல் கட்டமைப்பு & உயரம்" : "Stature & Body Frame"}
                    </span>
                    <p className="text-xs sm:text-sm text-slate-800 font-medium">
                      {data.kp_reader4_insights.stature}
                    </p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
                    <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                      {language === "ta" ? "முக அமைப்பு & நிறம்" : "Facial Structure & Complexion"}
                    </span>
                    <p className="text-xs sm:text-sm text-slate-800 font-medium">
                      {data.kp_reader4_insights.complexion_and_face}
                    </p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
                    <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                      {language === "ta" ? "மனோபாவம் & சுபாவம்" : "Mental & Moral Temperament"}
                    </span>
                    <p className="text-xs sm:text-sm text-slate-800 font-medium">
                      {data.kp_reader4_insights.temperament}
                    </p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
                    <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                      {language === "ta" ? "தொழில் & வாழ்க்கை முறை" : "Vocational & Lifestyle Signatures"}
                    </span>
                    <p className="text-xs sm:text-sm text-slate-800 font-medium">
                      {data.kp_reader4_insights.vocational_and_lifestyle_traits}
                    </p>
                  </div>
                </div>

                {data.kp_reader4_insights.cautionary_notes && (
                  <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                    <span>{data.kp_reader4_insights.cautionary_notes}</span>
                  </div>
                )}
              </div>

              {/* Grid 2: Career Wife & Punarphoo & Mars Dosha */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {/* Career Wife Assessment */}
                <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-3">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                    <div className="flex items-center gap-2">
                      <Briefcase className="w-4 h-4 text-[#B4872B]" />
                      <span className="font-bold text-sm text-[#153F6B]">
                        {language === "ta" ? "பணிபுரியும் மனைவி / துணையின் தொழில் (4-ஆம் CSL)" : "Career Spouse Assessment (4th CSL)"}
                      </span>
                    </div>
                    <span
                      className={`text-xs font-black px-2.5 py-0.5 rounded-full ${
                        data.kp_reader4_insights.career_spouse_promised
                          ? "bg-emerald-100 text-emerald-800 border border-emerald-200"
                          : "bg-slate-100 text-slate-700 border border-slate-200"
                      }`}
                    >
                      {data.kp_reader4_insights.career_spouse_promised
                        ? language === "ta"
                          ? "பணிபுரிபவர்"
                          : "Career Spouse"
                        : language === "ta"
                        ? "குடும்ப நிர்வாகி"
                        : "Homemaker"}
                    </span>
                  </div>

                  <div className="text-xs text-slate-700 leading-relaxed space-y-1.5">
                    <div className="font-semibold text-slate-900">
                      {data.kp_reader4_insights.career_spouse_vocation}
                    </div>
                    <p className="text-slate-600">
                      {data.kp_reader4_insights.career_spouse_explanation}
                    </p>
                  </div>
                </div>

                {/* Punarphoo (Saturn-Moon) */}
                <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-3">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-amber-600" />
                      <span className="font-bold text-sm text-[#153F6B]">
                        {language === "ta" ? "புனர்பூ ஆய்வு (சனி-சந்திரன் தொடர்பு)" : "Punarphoo Delay Detection (Saturn-Moon)"}
                      </span>
                    </div>
                    <span
                      className={`text-xs font-black px-2.5 py-0.5 rounded-full ${
                        data.kp_reader4_insights.punarphoo_detected
                          ? "bg-amber-100 text-amber-900 border border-amber-200"
                          : "bg-emerald-100 text-emerald-800 border border-emerald-200"
                      }`}
                    >
                      {data.kp_reader4_insights.punarphoo_detected
                        ? `${data.kp_reader4_insights.punarphoo_severity} Punarphoo`
                        : "No Punarphoo"}
                    </span>
                  </div>

                  <div className="text-xs text-slate-700 leading-relaxed space-y-1.5">
                    <p className="text-slate-600">
                      {data.kp_reader4_insights.punarphoo_advice ||
                        (language === "ta"
                          ? "சனி-சந்திரன் தடையின்றி திருமணம் இயல்பான காலகட்டத்தில் நிறைவேறும்."
                          : "Negotiations proceed normally without Saturn-Moon postponements.")}
                    </p>
                  </div>
                </div>
              </div>

              {/* Grid 3: Mars Dosha & Marriage Promise */}
              <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                  <div className="flex items-center gap-2">
                    <Shield className="w-4 h-4 text-rose-600" />
                    <span className="font-bold text-sm text-[#153F6B]">
                      {language === "ta" ? "செவ்வாய் தோஷம் & KP உப அதிபதி தீர்ப்பு" : "Mars Dosha & KP Cuspal Sub-Lord Override"}
                    </span>
                  </div>
                  <span className="text-xs font-black px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-800">
                    {data.kp_reader4_insights.marriage_promise_verdict}
                  </span>
                </div>

                <div className="space-y-2 text-xs text-slate-700 leading-relaxed">
                  <div className="flex items-start gap-2">
                    <span className="font-bold text-slate-900 shrink-0">
                      {language === "ta" ? "சாஸ்திர நிலை:" : "Shastric Status:"}
                    </span>
                    <span>{data.kp_reader4_insights.mars_dosha_verdict}</span>
                  </div>
                  <div className="flex items-start gap-2 p-3 rounded-xl bg-slate-50 border border-slate-200/60">
                    <span className="font-bold text-blue-950 shrink-0">
                      {language === "ta" ? "KP உப அதிபதி தீர்ப்பு:" : "KP Sub-Lord Ruling:"}
                    </span>
                    <span className="text-blue-900 font-medium">
                      {data.kp_reader4_insights.mars_dosha_kp_ruling}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-6 text-center text-sm text-slate-500 bg-white rounded-2xl border border-slate-200">
              {language === "ta"
                ? "KP ரீடர் 4 தரவு கணக்கிடப்படவில்லை."
                : "KP Reader 4 calculations could not be loaded."}
            </div>
          )}
        </div>
      )}

      {activeTab === "vedic_profile" && (
        <div className="space-y-6">
          {/* 7th House Sign Temperament */}
          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                {language === "ta" ? "7-ஆம் பாவ ராசி & இயல்பு" : "7th House Sign & Baseline Temperament"}
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-[#FAF2DE] text-[#8E6516]">
                {language === "ta" ? data.seventh_sign.sign_tamil : data.seventh_sign.sign} (
                {language === "ta" ? data.seventh_sign.ruler_tamil : data.seventh_sign.ruler})
              </span>
            </div>
            <p className="text-xs text-slate-700 leading-relaxed">
              {language === "ta" ? data.seventh_sign.temperament_ta : data.seventh_sign.temperament_en}
            </p>
            <div className="flex flex-wrap gap-2 pt-2">
              {(language === "ta" ? data.seventh_sign.core_traits_ta : data.seventh_sign.core_traits_en).map((trait, i) => (
                <span key={i} className="px-2.5 py-1 rounded-md text-[11px] font-semibold bg-slate-100 text-slate-700">
                  {trait}
                </span>
              ))}
            </div>
          </div>

          {/* 7th Lord Elemental Analysis */}
          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                {language === "ta" ? "7-ஆம் அதிபதியின் பூத தத்துவம்" : "7th Lord Placement & Elemental Balance"}
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-50 text-blue-800 border border-blue-200">
                {language === "ta" ? data.seventh_lord.element_tamil : data.seventh_lord.element} Element
              </span>
            </div>
            <p className="text-xs text-slate-700 leading-relaxed">
              {language === "ta" ? data.seventh_lord.description_ta : data.seventh_lord.description_en}
            </p>
          </div>

          {/* Planets in 7th or Aspecting */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-3">
              <h4 className="font-bold text-xs uppercase tracking-wider text-slate-600">
                {language === "ta" ? "7-ஆம் வீட்டில் நின்ற கிரகங்கள்" : "Planets Occupying 7th House"}
              </h4>
              {data.planets_in_seventh.length === 0 ? (
                <p className="text-xs text-slate-400 italic">
                  {language === "ta" ? "கிரகங்கள் ஏதுமில்லை (சுத்த களத்திர பாவம்)" : "No planets occupying 7th house."}
                </p>
              ) : (
                data.planets_in_seventh.map((p, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-[#153F6B]">
                        {language === "ta" ? p.planet_tamil : p.planet}
                      </span>
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-amber-100 text-amber-900">
                        {language === "ta" ? p.spouse_type_ta : p.spouse_type_en}
                      </span>
                    </div>
                    <p className="text-slate-600 leading-relaxed">
                      {language === "ta" ? p.influence_type_tamil : p.influence_type}
                    </p>
                  </div>
                ))
              )}
            </div>

            <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-3">
              <h4 className="font-bold text-xs uppercase tracking-wider text-slate-600">
                {language === "ta" ? "7-ஆம் வீட்டைப் பார்க்கும் கிரகங்கள்" : "Planets Aspecting 7th House"}
              </h4>
              {data.aspecting_planets.length === 0 ? (
                <p className="text-xs text-slate-400 italic">
                  {language === "ta" ? "பார்வை செய்யும் கிரகங்கள் ஏதுமில்லை" : "No direct planetary aspects on 7th house."}
                </p>
              ) : (
                data.aspecting_planets.map((p, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-[#153F6B]">
                        {language === "ta" ? p.planet_tamil : p.planet}
                      </span>
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-blue-100 text-blue-900">
                        {language === "ta" ? p.spouse_type_ta : p.spouse_type_en}
                      </span>
                    </div>
                    <p className="text-slate-600 leading-relaxed">
                      {language === "ta" ? p.influence_type_tamil : p.influence_type}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: NAVAMSA (D9) INNER NATURE */}
      {activeTab === "navamsa_d9" && (
        <div className="space-y-4">
          <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Layers className="w-5 h-5 text-[#B4872B]" />
                <h4 className="font-bold text-sm sm:text-base text-[#153F6B]">
                  {language === "ta" ? "நவாம்ச (D9) களத்திர நிலை" : "Navamsa (D9) Spouse Profile"}
                </h4>
              </div>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-[#FAF2DE] text-[#8E6516]">
                {language === "ta" ? data.navamsa_d9.d9_seventh_sign_tamil : data.navamsa_d9.d9_seventh_sign} (
                {language === "ta" ? data.navamsa_d9.d9_seventh_lord_tamil : data.navamsa_d9.d9_seventh_lord})
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2 text-xs">
                <span className="font-bold text-slate-700 block">
                  {language === "ta" ? "உள் குணம் & மனநிலை" : "Inner Nature & Psychological Bond"}
                </span>
                <p className="text-slate-600 leading-relaxed">
                  {language === "ta" ? data.navamsa_d9.inner_nature_ta : data.navamsa_d9.inner_nature_en}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2 text-xs">
                <span className="font-bold text-slate-700 block">
                  {language === "ta" ? "மணவாழ்வு பந்தத்தின் நிலைப்புத்தன்மை" : "Marital Bond Endurance"}
                </span>
                <p className="text-slate-600 leading-relaxed">
                  {language === "ta" ? data.navamsa_d9.marital_bond_ta : data.navamsa_d9.marital_bond_en}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: PARTNER TRAIT SCORES */}
      {activeTab === "traits" && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {[
            {
              titleEn: "Romantic & Affectionate Bond",
              titleTa: "காதல் & அன்புப் பிணைப்பு",
              score: data.trait_scores.romantic_loving_score,
              descEn: data.trait_scores.romantic_loving_analysis_en,
              descTa: data.trait_scores.romantic_loving_analysis_ta,
            },
            {
              titleEn: "Loyalty & Faithfulness",
              titleTa: "விசுவாசம் & குடும்பப் பற்று",
              score: data.trait_scores.loyalty_faithfulness_score,
              descEn: data.trait_scores.loyalty_faithfulness_analysis_en,
              descTa: data.trait_scores.loyalty_faithfulness_analysis_ta,
            },
            {
              titleEn: "Intelligence & Professional Growth",
              titleTa: "புத்தி கூர்மை & பொருளாதார வளர்ச்சி",
              score: data.trait_scores.intelligence_education_score,
              descEn: data.trait_scores.intelligence_education_analysis_en,
              descTa: data.trait_scores.intelligence_education_analysis_ta,
            },
            {
              titleEn: "Physical Charm & Grace",
              titleTa: "உடல் தோற்றம் & கவர்ச்சி",
              score: data.trait_scores.physical_charm_score,
              descEn: data.trait_scores.physical_charm_analysis_en,
              descTa: data.trait_scores.physical_charm_analysis_ta,
            },
          ].map((trait, idx) => (
            <div key={idx} className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs sm:text-sm text-[#153F6B]">
                  {language === "ta" ? trait.titleTa : trait.titleEn}
                </span>
                <span className="font-black text-sm text-[#B4872B]">{trait.score}/100</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-[#B4872B] to-amber-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${trait.score}%` }}
                />
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                {language === "ta" ? trait.descTa : trait.descEn}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
