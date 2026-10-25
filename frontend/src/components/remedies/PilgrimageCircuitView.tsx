"use client";

import React, { useState, useEffect } from "react";
import { useLanguage } from "@/lib/i18n";
import {
  PilgrimageCircuitResponse,
  PilgrimageDayPlan,
  PilgrimageTempleStop,
  RemedyAnalysisResponse,
} from "@/lib/types";
import {
  getPilgrimageCircuits,
  getPersonalizedPilgrimageCircuit,
} from "@/lib/api";
import {
  MapPin,
  Clock,
  Compass,
  Sparkles,
  Calendar,
  AlertTriangle,
  ExternalLink,
  Printer,
  ShieldCheck,
  ChevronRight,
  Info,
  Car,
  Flame,
  CheckCircle2,
} from "lucide-react";

interface PilgrimageCircuitViewProps {
  analysisResult?: RemedyAnalysisResponse | null;
  horoscopeId?: string | null;
}

const GRAHA_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  sun: { bg: "bg-amber-100", text: "text-amber-800", border: "border-amber-300" },
  moon: { bg: "bg-slate-100", text: "text-slate-800", border: "border-slate-300" },
  mars: { bg: "bg-rose-100", text: "text-rose-800", border: "border-rose-300" },
  mercury: { bg: "bg-emerald-100", text: "text-emerald-800", border: "border-emerald-300" },
  jupiter: { bg: "bg-yellow-100", text: "text-yellow-800", border: "border-yellow-300" },
  venus: { bg: "bg-pink-100", text: "text-pink-800", border: "border-pink-300" },
  saturn: { bg: "bg-indigo-100", text: "text-indigo-800", border: "border-indigo-300" },
  rahu: { bg: "bg-purple-100", text: "text-purple-800", border: "border-purple-300" },
  ketu: { bg: "bg-orange-100", text: "text-orange-800", border: "border-orange-300" },
};

export function PilgrimageCircuitView({
  analysisResult,
  horoscopeId,
}: PilgrimageCircuitViewProps) {
  const { language } = useLanguage();
  const isTa = language === "ta";

  const [circuits, setCircuits] = useState<PilgrimageCircuitResponse[]>([]);
  const [selectedCircuitId, setSelectedCircuitId] = useState<string>("2_day_comprehensive");
  const [personalizedCircuit, setPersonalizedCircuit] = useState<PilgrimageCircuitResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError(null);
      try {
        const stdCircuits = await getPilgrimageCircuits();
        setCircuits(stdCircuits);

        // If active chart analysis is available, also fetch personalized chart priorities
        if (analysisResult || horoscopeId) {
          try {
            const pCircuit = await getPersonalizedPilgrimageCircuit({
              horoscope_id: horoscopeId || undefined,
              chart_snapshot: analysisResult ? {
                horoscope: {
                  planets: (analysisResult.chart_context?.debilitated_planets || []).map(p => ({ name: p, is_debilitated: true })),
                  doshas: { manglik: analysisResult.chart_context?.kuja_dosha_status === "present" },
                },
                running_mahadasha: analysisResult.chart_context?.running_mahadasha,
                running_bhukti: analysisResult.chart_context?.running_bhukti,
              } : undefined,
              circuit_type: "2_day",
            });
            setPersonalizedCircuit(pCircuit);
            setSelectedCircuitId("personalized");
          } catch (pErr) {
            console.warn("Could not load personalized circuit, using standard", pErr);
          }
        }
      } catch (err: any) {
        setError(err?.message || "Failed to load pilgrimage circuits.");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [analysisResult, horoscopeId]);

  const activeCircuit =
    selectedCircuitId === "personalized" && personalizedCircuit
      ? personalizedCircuit
      : circuits.find((c) => c.circuit_id === selectedCircuitId) || circuits[0];

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="bg-white rounded-2xl border border-stone-200 p-12 text-center shadow-sm">
        <div className="w-10 h-10 border-4 border-[#153F6B] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-stone-600 font-medium">
          {isTa
            ? "காவிரி டெல்டா நவக்கிரக யாத்திரை விவரங்கள் பெறப்படுகின்றன..."
            : "Loading Kaveri Delta Navagraha Pilgrimage Circuits..."}
        </p>
      </div>
    );
  }

  if (error || !activeCircuit) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-red-800">
        <p className="font-semibold">{isTa ? "பிழை ஏற்பட்டது" : "Error Occurred"}</p>
        <p className="text-sm mt-1">{error || "No circuits available."}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Circuit Selector Bar */}
      <div className="bg-white p-4 rounded-2xl border border-stone-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-2">
          {personalizedCircuit && (
            <button
              onClick={() => setSelectedCircuitId("personalized")}
              className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all flex items-center gap-2 ${
                selectedCircuitId === "personalized"
                  ? "bg-[#8B6914] text-white shadow-sm"
                  : "bg-stone-100 text-stone-700 hover:bg-stone-200"
              }`}
            >
              <Sparkles className="w-4 h-4 text-amber-300" />
              {isTa ? "ஜாதக முன்னுரிமை யாத்திரை" : "Chart Priority Circuit"}
            </button>
          )}
          <button
            onClick={() => setSelectedCircuitId("2_day_comprehensive")}
            className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
              selectedCircuitId === "2_day_comprehensive"
                ? "bg-[#153F6B] text-white shadow-sm"
                : "bg-stone-100 text-stone-700 hover:bg-stone-200"
            }`}
          >
            {isTa ? "2-நாள் முழுமையான ஆன்மீக யாத்திரை" : "2-Day Comprehensive"}
          </button>
          <button
            onClick={() => setSelectedCircuitId("1_day_express")}
            className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
              selectedCircuitId === "1_day_express"
                ? "bg-[#153F6B] text-white shadow-sm"
                : "bg-stone-100 text-stone-700 hover:bg-stone-200"
            }`}
          >
            {isTa ? "1-நாள் விரைவு யாத்திரை (எக்ஸ்பிரஸ்)" : "1-Day Express Circuit"}
          </button>
        </div>

        <button
          onClick={handlePrint}
          className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-stone-700 bg-stone-100 hover:bg-stone-200 rounded-xl transition"
        >
          <Printer className="w-4 h-4 text-stone-600" />
          {isTa ? "யாத்திரை அட்டவணையை அச்சிடுக" : "Print Itinerary"}
        </button>
      </div>

      {/* Hero Overview Card */}
      <div className="bg-gradient-to-br from-[#153F6B] to-[#0D2644] text-white rounded-3xl p-6 sm:p-8 shadow-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 bg-amber-400/20 text-amber-200 border border-amber-300/30 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider">
              <Compass className="w-3.5 h-3.5" />
              {isTa ? "காவிரி டெல்டா புனித ஸ்தலங்கள்" : "Kaveri Delta Sacred Sthalams"}
            </div>
            <h2 className="text-2xl sm:text-3xl font-bold font-serif">
              {isTa ? activeCircuit.title_ta : activeCircuit.title_en}
            </h2>
            <p className="text-stone-300 text-sm max-w-2xl leading-relaxed">
              {isTa ? activeCircuit.summary_ta : activeCircuit.summary_en}
            </p>
          </div>

          <div className="grid grid-cols-3 gap-3 bg-white/10 backdrop-blur-sm border border-white/15 p-4 rounded-2xl text-center">
            <div>
              <p className="text-xs text-stone-300">{isTa ? "மொத்த ஆலயங்கள்" : "Temples"}</p>
              <p className="text-xl sm:text-2xl font-bold text-amber-300">{activeCircuit.total_temples}</p>
            </div>
            <div className="border-x border-white/15 px-3">
              <p className="text-xs text-stone-300">{isTa ? "பயண தூரம்" : "Distance"}</p>
              <p className="text-xl sm:text-2xl font-bold text-amber-300">{activeCircuit.total_distance_km} km</p>
            </div>
            <div>
              <p className="text-xs text-stone-300">{isTa ? "மைய நகரம்" : "Hub"}</p>
              <p className="text-sm sm:text-base font-bold text-white mt-1">
                {isTa ? activeCircuit.base_hub_ta : activeCircuit.base_hub_en}
              </p>
            </div>
          </div>
        </div>

        {/* Rahu Kalam & Customs Banner */}
        <div className="mt-6 pt-6 border-t border-white/15 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-stone-200">
          <div className="flex items-start gap-2.5">
            <Clock className="w-4 h-4 text-amber-300 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-amber-200">
                {isTa ? "ராகு கால வழிகாட்டுதல்: " : "Rahu Kalam Guidance: "}
              </span>
              {isTa ? activeCircuit.rahu_kalam_guidelines_ta : activeCircuit.rahu_kalam_guidelines_en}
            </div>
          </div>
          <div className="flex items-start gap-2.5">
            <ShieldCheck className="w-4 h-4 text-emerald-300 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-emerald-200">
                {isTa ? "பாரம்பரிய ஆடை & நடைமுறைகள்: " : "Dress Code & Sanctum Customs: "}
              </span>
              {isTa ? activeCircuit.dress_code_and_customs_ta : activeCircuit.dress_code_and_customs_en}
            </div>
          </div>
        </div>
      </div>

      {/* Day by Day Plans */}
      <div className="space-y-8">
        {activeCircuit.day_plans.map((dayPlan: PilgrimageDayPlan) => (
          <div
            key={dayPlan.day_number}
            className="bg-white rounded-3xl border border-stone-200 shadow-sm overflow-hidden"
          >
            {/* Day Header */}
            <div className="bg-stone-50 border-b border-stone-200 px-6 py-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-[#8B6914] bg-[#FAF2DE] border border-[#B4872B]/30 px-2.5 py-0.5 rounded-full">
                  {isTa ? `நாள் ${dayPlan.day_number}` : `Day ${dayPlan.day_number}`}
                </span>
                <h3 className="text-xl font-bold font-serif text-[#153F6B] mt-1">
                  {isTa ? dayPlan.title_ta : dayPlan.title_en}
                </h3>
              </div>
              <div className="flex items-center gap-4 text-xs text-stone-600">
                <div className="flex items-center gap-1.5 bg-white border border-stone-200 px-3 py-1.5 rounded-xl">
                  <Clock className="w-4 h-4 text-[#8B6914]" />
                  <span>
                    {isTa ? "புறப்பாடு: " : "Start: "}
                    <strong>{dayPlan.recommended_start_time}</strong>
                  </span>
                </div>
                <div className="flex items-center gap-1.5 bg-white border border-stone-200 px-3 py-1.5 rounded-xl">
                  <Car className="w-4 h-4 text-[#153F6B]" />
                  <span>
                    <strong>{dayPlan.total_distance_km} km</strong> (~{dayPlan.estimated_travel_time_hours} hrs)
                  </span>
                </div>
              </div>
            </div>

            {/* Temple Stops Timeline */}
            <div className="p-6 divide-y divide-stone-100">
              {dayPlan.temple_stops.map((stop: PilgrimageTempleStop) => {
                const colors = GRAHA_COLORS[stop.graha] || {
                  bg: "bg-stone-100",
                  text: "text-stone-800",
                  border: "border-stone-300",
                };

                return (
                  <div
                    key={stop.code}
                    className={`py-6 first:pt-2 last:pb-2 transition-colors ${
                      stop.is_chart_priority ? "bg-amber-50/50 -mx-6 px-6 rounded-2xl my-2 border border-amber-200" : ""
                    }`}
                  >
                    <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
                      {/* Left: Stop Number & Badges */}
                      <div className="space-y-3 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="w-7 h-7 rounded-full bg-[#153F6B] text-white flex items-center justify-center text-xs font-bold shadow-sm">
                            #{stop.order_in_day}
                          </span>
                          <span
                            className={`px-3 py-0.5 rounded-full text-xs font-semibold border ${colors.bg} ${colors.text} ${colors.border}`}
                          >
                            {isTa ? stop.graha_name_ta : stop.graha_name_en}
                          </span>
                          <div className="inline-flex items-center gap-1 text-xs text-stone-600 font-medium bg-stone-100 px-2.5 py-0.5 rounded-full">
                            <Clock className="w-3.5 h-3.5 text-stone-500" />
                            {isTa ? stop.visiting_time_window_ta : stop.visiting_time_window_en}
                          </div>

                          {stop.is_chart_priority && (
                            <span className="inline-flex items-center gap-1 text-xs font-bold text-amber-900 bg-amber-200 border border-amber-300 px-2.5 py-0.5 rounded-full animate-pulse">
                              <Sparkles className="w-3.5 h-3.5 text-amber-800" />
                              {isTa ? "ஜாதக முக்கியத்துவம் (Priority)" : "Chart Priority Sthalam"}
                            </span>
                          )}
                        </div>

                        {/* Title & Deity */}
                        <div>
                          <h4 className="text-lg font-bold text-stone-900 font-serif">
                            {isTa ? stop.name_ta : stop.name_en}
                          </h4>
                          <p className="text-xs text-stone-600 mt-0.5">
                            {isTa ? "மூலவர்: " : "Presiding Deity: "}
                            <span className="font-semibold text-stone-800">
                              {isTa ? stop.presiding_deity_ta : stop.presiding_deity_en}
                            </span>
                          </p>
                          <p className="text-xs text-stone-500 flex items-center gap-1 mt-0.5">
                            <MapPin className="w-3.5 h-3.5 text-stone-400" />
                            {isTa ? `${stop.place_name_ta}, ${stop.district_ta}` : `${stop.place_name_en}, ${stop.district_en}`}
                          </p>
                        </div>

                        {/* Astrological Chart Priority Reason */}
                        {stop.is_chart_priority && (
                          <div className="bg-amber-100/70 border border-amber-300 rounded-xl p-3 text-xs text-amber-950">
                            <div className="flex items-start gap-2">
                              <Sparkles className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
                              <div>
                                <span className="font-bold">
                                  {isTa ? "ஜாதக காரணம்: " : "Astrological Reason: "}
                                </span>
                                {isTa ? stop.chart_priority_reason_ta : stop.chart_priority_reason_en}
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Special Ritual & Darshan Timing */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                          <div className="bg-stone-50 border border-stone-200/80 p-3 rounded-xl text-xs space-y-1">
                            <span className="font-semibold text-[#8B6914] flex items-center gap-1">
                              <Flame className="w-3.5 h-3.5" />
                              {isTa ? "சிறப்பு பரிகாரம் & வழிபாடு:" : "Special Pariharam & Ritual:"}
                            </span>
                            <p className="text-stone-700 leading-relaxed">
                              {isTa ? stop.special_ritual_ta : stop.special_ritual_en}
                            </p>
                          </div>

                          <div className="bg-stone-50 border border-stone-200/80 p-3 rounded-xl text-xs space-y-1">
                            <span className="font-semibold text-[#153F6B] flex items-center gap-1">
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              {isTa ? "பரிந்துரைக்கப்படும் சமர்ப்பணம்:" : "Prescribed Offerings:"}
                            </span>
                            <p className="text-stone-700 leading-relaxed">
                              {isTa ? stop.remedy_offerings_ta : stop.remedy_offerings_en}
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Right: Map & Distance */}
                      <div className="lg:text-right shrink-0 flex flex-row lg:flex-col items-center lg:items-end justify-between gap-3 pt-2 lg:pt-0">
                        {stop.distance_from_previous_km > 0 && (
                          <div className="text-xs text-stone-500 bg-stone-100 px-2.5 py-1 rounded-lg">
                            {isTa ? "முந்தைய இடத்திலிருந்து:" : "From previous:"}{" "}
                            <strong className="text-stone-800">{stop.distance_from_previous_km} km</strong> (~{stop.driving_minutes_from_previous}m)
                          </div>
                        )}
                        <a
                          href={`https://www.google.com/maps/search/?api=1&query=${stop.latitude},${stop.longitude}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#153F6B] bg-[#EBF2FE] hover:bg-[#D5E5FD] px-3 py-1.5 rounded-xl transition"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                          {isTa ? "கூகுள் மேப் வழிகாட்டல்" : "View on Google Maps"}
                        </a>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Day Tips Footer */}
            {dayPlan.practical_tips_en.length > 0 && (
              <div className="bg-stone-50 border-t border-stone-200 px-6 py-4">
                <p className="text-xs font-bold text-stone-700 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <Info className="w-4 h-4 text-[#8B6914]" />
                  {isTa ? "இன்றைய பயண குறிப்புகள்:" : "Practical Travel Advice for this Day:"}
                </p>
                <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-stone-600">
                  {(isTa ? dayPlan.practical_tips_ta : dayPlan.practical_tips_en).map((tip, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="text-[#8B6914] font-bold">•</span>
                      <span>{tip}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
