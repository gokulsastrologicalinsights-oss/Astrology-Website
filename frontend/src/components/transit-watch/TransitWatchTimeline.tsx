"use client";

import React, { useState, useMemo } from "react";
import { TransitTimelineResponse, TransitIngressEvent } from "@/lib/types";
import { formatDms } from "@/lib/formatters";
import {
  Calendar,
  Clock,
  ArrowRight,
  RotateCw,
  Compass,
  AlertTriangle,
  Info,
  Sparkles,
  Filter,
} from "lucide-react";

interface TransitWatchTimelineProps {
  data: TransitTimelineResponse;
  language?: "en" | "ta";
}

// Visual accent badges per planet
const PLANET_STYLES: Record<string, { bg: string; text: string; border: string }> = {
  Moon: { bg: "bg-slate-50", text: "text-slate-800", border: "border-slate-300" },
  Sun: { bg: "bg-amber-50", text: "text-amber-900", border: "border-amber-300" },
  Jupiter: { bg: "bg-yellow-50", text: "text-yellow-900", border: "border-yellow-300" },
  Saturn: { bg: "bg-blue-50", text: "text-blue-900", border: "border-blue-300" },
  Rahu: { bg: "bg-indigo-50", text: "text-indigo-900", border: "border-indigo-300" },
  Ketu: { bg: "bg-purple-50", text: "text-purple-900", border: "border-purple-300" },
  Mars: { bg: "bg-rose-50", text: "text-rose-900", border: "border-rose-300" },
  Mercury: { bg: "bg-emerald-50", text: "text-emerald-900", border: "border-emerald-300" },
  Venus: { bg: "bg-pink-50", text: "text-pink-900", border: "border-pink-300" },
};

export function TransitWatchTimeline({
  data,
  language = "en",
}: TransitWatchTimelineProps) {
  const [selectedPlanetFilter, setSelectedPlanetFilter] = useState<string>("ALL");
  const [selectedBoundaryFilter, setSelectedBoundaryFilter] = useState<string>("ALL");
  const [motionFilter, setMotionFilter] = useState<"ALL" | "DIRECT" | "RETROGRADE">("ALL");

  // Client-side filtering
  const filteredEvents = useMemo(() => {
    return data.events.filter((ev) => {
      if (selectedPlanetFilter !== "ALL" && ev.planet !== selectedPlanetFilter) {
        return false;
      }
      if (selectedBoundaryFilter === "rashi" && !ev.is_rashi_boundary) {
        return false;
      }
      if (selectedBoundaryFilter === "nakshatra" && !ev.is_nakshatra_boundary) {
        return false;
      }
      if (selectedBoundaryFilter === "sub_lord" && ev.boundary_type !== "sub_lord") {
        return false;
      }
      if (motionFilter === "DIRECT" && ev.is_retrograde) {
        return false;
      }
      if (motionFilter === "RETROGRADE" && !ev.is_retrograde) {
        return false;
      }
      return true;
    });
  }, [data.events, selectedPlanetFilter, selectedBoundaryFilter, motionFilter]);

  // Group events chronologically by local calendar date (YYYY-MM-DD)
  const groupedEvents = useMemo(() => {
    const groups: Record<string, TransitIngressEvent[]> = {};
    for (const ev of filteredEvents) {
      const dateKey = ev.local_datetime.slice(0, 10);
      if (!groups[dateKey]) {
        groups[dateKey] = [];
      }
      groups[dateKey].push(ev);
    }
    return groups;
  }, [filteredEvents]);

  // Planet counts for filter badges
  const planetCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const ev of data.events) {
      counts[ev.planet] = (counts[ev.planet] || 0) + 1;
    }
    return counts;
  }, [data.events]);

  const dateKeys = Object.keys(groupedEvents).sort();

  return (
    <div className="space-y-6">
      {/* 1. Header Summary Banner */}
      <div className="rounded-2xl border border-[#D8BD80] bg-[#FAF6EC] p-4 sm:p-5 shadow-xs space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-[#102A4C]">
          <div className="flex items-center gap-2">
            <Compass className="w-4 h-4 text-[#B8862B]" />
            <span className="font-bold text-[#8C6D23]">
              {language === "ta" ? "கணிப்பு சாளரம்:" : "Calculation Window:"}
            </span>
            <span className="font-mono">
              {data.start_time_local.slice(0, 10)} {data.start_time_local.slice(11, 19)} →{" "}
              {data.end_time_local.slice(0, 10)} {data.end_time_local.slice(11, 19)}
            </span>
            <span className="text-[#64748B]">({data.forecast_days} days)</span>
          </div>

          <div className="flex items-center gap-4 text-[11px]">
            <div>
              <span className="text-[#64748B]">{language === "ta" ? "மண்டலம்:" : "Timezone:"}</span>{" "}
              <span className="font-semibold text-[#102A4C]">{data.timezone}</span>{" "}
              <span className="text-[#8C6D23] font-mono">
                (UTC {data.utc_offset_hours >= 0 ? `+${data.utc_offset_hours}` : data.utc_offset_hours}h)
              </span>
            </div>
            <div>
              <span className="text-[#64748B]">{language === "ta" ? "அயனாம்சம்:" : "Ayanamsa:"}</span>{" "}
              <span className="font-semibold text-[#102A4C]">{data.ayanamsa_name}</span>
            </div>
          </div>
        </div>

        {/* Diagnostic Execution Stats */}
        {data.benchmark_stats && (
          <div className="pt-2.5 border-t border-[#E8DDCA] flex flex-wrap items-center justify-between text-[11px] text-[#64748B]">
            <div>
              <span>{language === "ta" ? "மொத்த நிகழ்வுகள்:" : "Total Ingress Events:"}</span>{" "}
              <span className="font-bold text-[#102A4C]">{data.total_events}</span>
              {filteredEvents.length !== data.total_events && (
                <span className="text-amber-800 ml-1 font-medium">
                  ({filteredEvents.length} matching filters)
                </span>
              )}
            </div>
            <div className="flex items-center gap-3 font-mono text-[10px]">
              <span>Runtime: {data.benchmark_stats.duration_ms} ms</span>
              <span>•</span>
              <span>Evaluations: {data.benchmark_stats.total_evaluations.toLocaleString()}</span>
              <span>•</span>
              <span>Precision: ±0.5s bisection</span>
            </div>
          </div>
        )}
      </div>

      {/* 2. Truncation Alert if max_events reached */}
      {data.truncated && (
        <div className="rounded-xl border border-amber-300 bg-amber-50 p-4 flex items-start gap-3 text-xs text-amber-900">
          <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-bold">
              {language === "ta"
                ? "முடிவுகள் மட்டுப்படுத்தப்பட்டுள்ளன (Truncated)"
                : "Results Capped at Event Limit"}
            </p>
            <p className="text-amber-800 leading-relaxed">
              {language === "ta"
                ? `இந்தக் கால இடைவெளியில் அனுமதிக்கப்பட்ட அதிகபட்ச நிகழ்வுகள் (${data.total_events}) எட்டப்பட்டன. குறுகிய கால அளவை தேர்ந்தெடுக்கவும் அல்லது குறிப்பிட்ட கிரகங்களை வடிகட்டவும்.`
                : `The transit timeline query exceeded the backend limit (${data.total_events} events). Filter for specific planets or select a narrower forecast window to view all individual crossings.`}
            </p>
          </div>
        </div>
      )}

      {/* 3. Interactive Filter Bar */}
      <div className="rounded-2xl border border-[#DDE5F0] bg-white p-4 shadow-xs space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-[#F1F5F9]">
          <div className="flex items-center gap-1.5 text-xs font-bold text-[#102A4C]">
            <Filter className="w-3.5 h-3.5 text-[#B8862B]" />
            <span>{language === "ta" ? "நிகழ்வு வடிகட்டிகள்" : "Timeline Filters"}</span>
          </div>
          {(selectedPlanetFilter !== "ALL" || selectedBoundaryFilter !== "ALL" || motionFilter !== "ALL") && (
            <button
              type="button"
              onClick={() => {
                setSelectedPlanetFilter("ALL");
                setSelectedBoundaryFilter("ALL");
                setMotionFilter("ALL");
              }}
              className="text-[11px] text-[#3478F6] hover:underline font-semibold"
            >
              Reset Filters
            </button>
          )}
        </div>

        {/* Planet Chips */}
        <div className="space-y-1.5">
          <div className="text-[11px] font-semibold text-[#64748B]">
            {language === "ta" ? "கிரகம்:" : "Filter by Planet:"}
          </div>
          <div className="flex flex-wrap items-center gap-1.5">
            <button
              type="button"
              onClick={() => setSelectedPlanetFilter("ALL")}
              className={`px-2.5 py-1 rounded-lg text-xs font-semibold border transition-all ${
                selectedPlanetFilter === "ALL"
                  ? "bg-[#102A4C] text-white border-[#102A4C]"
                  : "bg-[#FAF8F5] text-[#52667E] border-[#DDE5F0] hover:bg-[#F1F5F9]"
              }`}
            >
              All Planets ({data.total_events})
            </button>
            {data.planets_analyzed.map((planet) => {
              const count = planetCounts[planet] || 0;
              const isSelected = selectedPlanetFilter === planet;
              return (
                <button
                  key={planet}
                  type="button"
                  onClick={() => setSelectedPlanetFilter(planet)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-semibold border flex items-center gap-1 transition-all ${
                    isSelected
                      ? "bg-[#B8862B] text-white border-[#B8862B] shadow-2xs"
                      : "bg-[#FAF8F5] text-[#52667E] border-[#DDE5F0] hover:bg-[#F1F5F9]"
                  }`}
                >
                  <span>{planet}</span>
                  <span className={`text-[10px] px-1.5 py-0.2 rounded-full ${isSelected ? "bg-white/20 text-white" : "bg-[#E2E8F0] text-[#64748B]"}`}>
                    {count}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Boundary Type & Motion Filters */}
        <div className="flex flex-wrap items-center gap-4 pt-1 text-xs">
          {/* Boundary Type */}
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] font-semibold text-[#64748B]">Boundary:</span>
            <select
              value={selectedBoundaryFilter}
              onChange={(e) => setSelectedBoundaryFilter(e.target.value)}
              className="px-2.5 py-1 rounded-lg border border-[#DDE5F0] bg-[#FAF8F5] text-xs font-medium text-[#102A4C]"
            >
              <option value="ALL">All Boundaries</option>
              <option value="rashi">Rashi (Sign) Ingress Only</option>
              <option value="nakshatra">Nakshatra (Star) Ingress Only</option>
              <option value="sub_lord">Sub-Lord Boundary Only</option>
            </select>
          </div>

          {/* Motion Filter */}
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] font-semibold text-[#64748B]">Motion:</span>
            <select
              value={motionFilter}
              onChange={(e) => setMotionFilter(e.target.value as "ALL" | "DIRECT" | "RETROGRADE")}
              className="px-2.5 py-1 rounded-lg border border-[#DDE5F0] bg-[#FAF8F5] text-xs font-medium text-[#102A4C]"
            >
              <option value="ALL">All (Direct & Retrograde)</option>
              <option value="DIRECT">Direct Only</option>
              <option value="RETROGRADE">Retrograde Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* 4. Timeline Groups by Date */}
      {filteredEvents.length === 0 ? (
        <div className="rounded-2xl border border-[#DDE5F0] bg-white p-12 text-center space-y-3">
          <div className="w-12 h-12 rounded-2xl bg-[#FAF2DE] text-[#B8862B] border border-[#D8BD80] flex items-center justify-center mx-auto shadow-2xs">
            <Clock className="w-6 h-6" />
          </div>
          <h3 className="font-serif text-lg font-bold text-[#102A4C]">
            {language === "ta" ? "எந்த எல்லை மாற்றமும் காணப்படவில்லை" : "No Boundary Crossings Found"}
          </h3>
          <p className="text-xs sm:text-sm text-[#52667E] max-w-md mx-auto leading-relaxed">
            {language === "ta"
              ? "தேர்ந்தெடுக்கப்பட்ட வடிகட்டிகளில் இந்த கால இடைவெளியில் எந்த கோசார மாற்றங்களும் நிகழவில்லை. கிரகங்கள் தற்போதைய உப-அதிபதி பிரிவில் நீடிக்கின்றன."
              : "No planetary ingress events matched your active filters for this time window. Slow-moving planets may maintain their current KP Sub-Lord division throughout this period."}
          </p>
        </div>
      ) : (
        <div className="space-y-8">
          {dateKeys.map((dateStr) => {
            const dayEvents = groupedEvents[dateStr];
            const parsedDate = new Date(`${dateStr}T12:00:00Z`);
            const dateDisplay = parsedDate.toLocaleDateString(language === "ta" ? "ta-IN" : "en-US", {
              weekday: "long",
              year: "numeric",
              month: "long",
              day: "numeric",
            });

            return (
              <div key={dateStr} className="space-y-4">
                {/* Date Header Anchor */}
                <div className="sticky top-18 z-20 flex items-center gap-3 py-2 bg-[#E8EEF7]/90 backdrop-blur-xs">
                  <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white border border-[#DDE5F0] shadow-xs">
                    <Calendar className="w-3.5 h-3.5 text-[#B8862B]" />
                    <span className="font-serif text-xs sm:text-sm font-bold text-[#102A4C]">
                      {dateDisplay}
                    </span>
                    <span className="text-[11px] font-mono text-[#8C6D23] font-semibold bg-[#FAF2DE] border border-[#D8BD80] px-2 py-0.2 rounded-full">
                      {dayEvents.length} {dayEvents.length === 1 ? "event" : "events"}
                    </span>
                  </div>
                  <div className="h-px flex-1 bg-gradient-to-r from-[#DDE5F0] to-transparent" />
                </div>

                {/* Event Cards under this date */}
                <div className="space-y-3 pl-2 sm:pl-4 border-l-2 border-[#D8BD80]/50 ml-3 sm:ml-4">
                  {dayEvents.map((ev, idx) => {
                    const style = PLANET_STYLES[ev.planet] || {
                      bg: "bg-slate-50",
                      text: "text-slate-800",
                      border: "border-slate-300",
                    };

                    const localTimeStr = ev.local_datetime.slice(11, 19);
                    const utcTimeStr = ev.utc_datetime.slice(11, 19);

                    return (
                      <div
                        key={`${ev.planet}-${ev.jd}-${idx}`}
                        className="relative rounded-2xl border border-[#DDE5F0] bg-white p-4 sm:p-5 shadow-xs hover:shadow-md hover:border-[#B8862B] transition-all group space-y-3"
                      >
                        {/* Connecting timeline dot */}
                        <div className="absolute -left-[19px] sm:-left-[27px] top-6 w-3 h-3 rounded-full bg-white border-2 border-[#B8862B] shadow-xs group-hover:scale-125 transition-transform" />

                        {/* Top Row: Planet & Crossing Badges */}
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <div className="flex items-center gap-2">
                            {/* Planet Badge */}
                            <span
                              className={`px-2.5 py-1 rounded-xl text-xs font-bold border ${style.bg} ${style.text} ${style.border} shadow-2xs flex items-center gap-1.5`}
                            >
                              <Sparkles className="w-3 h-3 text-[#B8862B]" />
                              <span>{ev.planet}</span>
                            </span>

                            {/* Boundary Type Badge */}
                            {ev.is_rashi_boundary && (
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
                                Rashi Ingress
                              </span>
                            )}
                            {ev.is_nakshatra_boundary && !ev.is_rashi_boundary && (
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-800 border border-blue-200">
                                Nakshatra Ingress
                              </span>
                            )}
                            {ev.boundary_type === "sub_lord" && (
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
                                Sub-Lord Shift
                              </span>
                            )}

                            {/* Retrograde / Direct Badge */}
                            {ev.is_retrograde ? (
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-50 text-rose-800 border border-rose-200 flex items-center gap-1">
                                <RotateCw className="w-2.5 h-2.5" />
                                <span>Retrograde ({ev.speed_deg_per_day.toFixed(3)}°/d)</span>
                              </span>
                            ) : (
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200 flex items-center gap-1">
                                <ArrowRight className="w-2.5 h-2.5" />
                                <span>Direct (+{ev.speed_deg_per_day.toFixed(3)}°/d)</span>
                              </span>
                            )}
                          </div>

                          {/* Crossing Timestamps */}
                          <div className="flex items-center gap-2 font-mono text-xs">
                            <span className="px-2 py-0.5 rounded-md bg-[#FAF8F5] border border-[#DDE5F0] text-[#102A4C] font-semibold">
                              {localTimeStr} local
                            </span>
                            <span className="text-[11px] text-[#64748B]">
                              ({utcTimeStr} UTC)
                            </span>
                          </div>
                        </div>

                        {/* Transition Hierarchy Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-2 sm:gap-3 text-xs pt-1">
                          {/* 1. Zodiac Sign Transition */}
                          <div className={`p-2.5 rounded-xl border ${ev.is_rashi_boundary ? "bg-[#FAF6EC] border-[#D8BD80]" : "bg-[#F8FAFC] border-[#E2E8F0]"}`}>
                            <div className="text-[10px] font-semibold text-[#64748B] uppercase tracking-wider mb-1">
                              Rashi (Sign & Lord)
                            </div>
                            <div className="flex items-center justify-between text-[#102A4C] font-medium">
                              <div>
                                <span className="font-bold">{ev.from_sign}</span>
                                <span className="text-[10px] text-[#64748B] block">Lord: {ev.from_sign_lord}</span>
                              </div>
                              <ArrowRight className={`w-3.5 h-3.5 shrink-0 ${ev.is_rashi_boundary ? "text-[#B8862B]" : "text-[#94A3B8]"}`} />
                              <div className="text-right">
                                <span className="font-bold text-[#102A4C]">{ev.to_sign}</span>
                                <span className="text-[10px] text-[#64748B] block">Lord: {ev.to_sign_lord}</span>
                              </div>
                            </div>
                          </div>

                          {/* 2. Nakshatra Transition */}
                          <div className={`p-2.5 rounded-xl border ${ev.is_nakshatra_boundary ? "bg-blue-50/60 border-blue-200" : "bg-[#F8FAFC] border-[#E2E8F0]"}`}>
                            <div className="text-[10px] font-semibold text-[#64748B] uppercase tracking-wider mb-1">
                              Nakshatra (Star & Lord)
                            </div>
                            <div className="flex items-center justify-between text-[#102A4C] font-medium">
                              <div>
                                <span className="font-bold">{ev.from_nakshatra}</span>
                                <span className="text-[10px] text-[#64748B] block">Star: {ev.from_star_lord}</span>
                              </div>
                              <ArrowRight className={`w-3.5 h-3.5 shrink-0 ${ev.is_nakshatra_boundary ? "text-[#3478F6]" : "text-[#94A3B8]"}`} />
                              <div className="text-right">
                                <span className="font-bold text-[#102A4C]">{ev.to_nakshatra}</span>
                                <span className="text-[10px] text-[#64748B] block">Star: {ev.to_star_lord}</span>
                              </div>
                            </div>
                          </div>

                          {/* 3. KP Sub-Lord Transition (Tier 3) */}
                          <div className="p-2.5 rounded-xl border bg-amber-50/40 border-amber-200">
                            <div className="text-[10px] font-semibold text-[#64748B] uppercase tracking-wider mb-1 flex items-center justify-between">
                              <span>KP Sub-Lord (Tier 3)</span>
                              <span className="text-[10px] font-mono text-[#8C6D23]">
                                Div #{ev.from_kp_number} → #{ev.to_kp_number}
                              </span>
                            </div>
                            <div className="flex items-center justify-between text-[#102A4C] font-medium">
                              <div>
                                <span className="font-bold text-[#8C6212]">{ev.from_sub_lord}</span>
                                <span className="text-[10px] text-[#64748B] block">Sub-Lord</span>
                              </div>
                              <ArrowRight className="w-3.5 h-3.5 text-[#B8862B] shrink-0" />
                              <div className="text-right">
                                <span className="font-bold text-[#8C6212]">{ev.to_sub_lord}</span>
                                <span className="text-[10px] text-[#64748B] block">Sub-Lord</span>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Bottom Row: Exact Longitude & Numerical Precision */}
                        <div className="pt-2 border-t border-[#F1F5F9] flex flex-wrap items-center justify-between text-[11px] text-[#64748B]">
                          <div className="flex items-center gap-1.5 font-mono">
                            <Compass className="w-3 h-3 text-[#B8862B]" />
                            <span>Crossing Boundary:</span>
                            <span className="font-semibold text-[#102A4C]">
                              {formatDms(ev.boundary_longitude)}
                            </span>
                            <span className="text-[10px] text-[#94A3B8]">
                              ({ev.boundary_longitude.toFixed(4)}°)
                            </span>
                          </div>
                          <div className="text-[10px] font-mono text-[#64748B]">
                            Bisection precision: ±{ev.calculation_precision_seconds}s temporal
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* 5. Mathematical Transparency & Methodology Note */}
      <div className="rounded-2xl border border-[#DDE5F0] bg-[#FAF8F5] p-5 shadow-xs flex items-start gap-3 text-xs text-[#52667E] leading-relaxed">
        <Info className="w-4 h-4 text-[#B8862B] shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="font-bold text-[#102A4C]">
            {language === "ta" ? "கணித வெளிப்படைத்தன்மை & விதிமுறை" : "Mathematical Transparency & KP Principles"}
          </p>
          <p>
            {language === "ta"
              ? "இந்தக் கோசாரக் காலவரிசை சொந்த XALEN விண்வெளி இயக்கவியல் மற்றும் கிருஷ்ணமூர்த்தி பத்ததியின் 249 உப-அதிபதி (Tier 3 Sub-Lord) துல்லியத்தை மட்டுமே காட்டுகிறது. இது உப-உப அதிபதி (Tier 4) அல்ல. இங்கு காட்டப்படும் நேரங்கள் வானியல் எல்லை மாற்றங்களைக் குறிக்கின்றனவே தவிர, வாழ்க்கையின் நிகழ்வுகளுக்கான உறுதியான உத்தரவாதம் அல்ல."
              : "This timeline computes exact sidereal boundary crossings resolved through Tier 3 (KP Sub-Lord / 249 divisions) using deterministic bracketed bisection on the native XALEN ephemeris engine. It does not compute Tier 4 (Sub-Sub Lord). Ingress timestamps represent exact astronomical boundary transitions, not deterministic predictions of personal life events."}
          </p>
        </div>
      </div>
    </div>
  );
}
