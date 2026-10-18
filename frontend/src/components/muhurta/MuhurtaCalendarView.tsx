"use client";

import React, { useState, useEffect } from "react";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { getOccasions, findMuhurtas, getDailyPanchang, saveMuhurtaSelection } from "@/lib/api";
import {
  OccasionItem,
  CandidateSlot,
  FindMuhurtaResponse,
  SaveMuhurtaRequest,
} from "@/lib/types";
import { MuhurtaReportModal } from "./MuhurtaReportModal";
import {
  Calendar as CalendarIcon,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Clock,
  MapPin,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  Bookmark,
  Printer,
  Compass,
  Sun,
  Moon,
  Info,
} from "lucide-react";

export function MuhurtaCalendarView() {
  const { language } = useLanguage();
  const { session } = useAuth();

  // Current calendar view year & month (1-indexed month)
  const today = new Date();
  const [currentYear, setCurrentYear] = useState<number>(today.getFullYear());
  const [currentMonth, setCurrentMonth] = useState<number>(today.getMonth() + 1); // 1-12
  const [selectedDateStr, setSelectedDateStr] = useState<string>(
    today.toISOString().split("T")[0]
  );

  // Occasions
  const [occasions, setOccasions] = useState<OccasionItem[]>([]);
  const [selectedOccasion, setSelectedOccasion] = useState<string>("marriage");

  // Location
  const [cityName, setCityName] = useState("Chennai, India");
  const [latitude, setLatitude] = useState(13.0827);
  const [longitude, setLongitude] = useState(80.2707);
  const [timezoneStr, setTimezoneStr] = useState("Asia/Kolkata");

  // Calendar search results
  const [monthData, setMonthData] = useState<FindMuhurtaResponse | null>(null);
  const [loadingMonth, setLoadingMonth] = useState(false);

  // Selected date's full Panchang
  const [datePanchang, setDatePanchang] = useState<Record<string, any> | null>(null);
  const [loadingPanchang, setLoadingPanchang] = useState(false);

  // Report Modal
  const [reportCandidate, setReportCandidate] = useState<any | null>(null);
  const [isReportOpen, setIsReportOpen] = useState(false);

  // Save state
  const [savedSuccessMap, setSavedSuccessMap] = useState<Record<string, number>>({});
  const [savingId, setSavingId] = useState<string | null>(null);

  // Fetch occasions on mount
  useEffect(() => {
    getOccasions()
      .then((data) => {
        if (data && data.occasions) setOccasions(data.occasions);
      })
      .catch((e) => console.error(e));
  }, []);

  // Fetch month data when year, month, occasion, or location changes
  useEffect(() => {
    const startStr = `${currentYear}-${String(currentMonth).padStart(2, "0")}-01`;
    const lastDay = new Date(currentYear, currentMonth, 0).getDate();
    const endStr = `${currentYear}-${String(currentMonth).padStart(2, "0")}-${String(
      lastDay
    ).padStart(2, "0")}`;

    setLoadingMonth(true);
    findMuhurtas({
      occasion_code: selectedOccasion,
      start_date: startStr,
      end_date: endStr,
      latitude,
      longitude,
      location_name: cityName,
      timezone: timezoneStr,
      preferred_time_range: "all_day",
      limit: 150,
    })
      .then((res) => setMonthData(res))
      .catch((e) => console.error("Error fetching month data:", e))
      .finally(() => setLoadingMonth(false));
  }, [currentYear, currentMonth, selectedOccasion, latitude, longitude, timezoneStr]);

  // Fetch Panchang for selected date
  useEffect(() => {
    if (!selectedDateStr) return;
    setLoadingPanchang(true);
    getDailyPanchang({
      date: selectedDateStr,
      latitude,
      longitude,
      timezone: timezoneStr,
      ayanamsa_id: 0,
    })
      .then((res) => setDatePanchang(res))
      .catch((e) => console.error("Error fetching date panchang:", e))
      .finally(() => setLoadingPanchang(false));
  }, [selectedDateStr, latitude, longitude, timezoneStr]);

  // Calendar math
  const daysInMonth = new Date(currentYear, currentMonth, 0).getDate();
  const firstDayWeekday = new Date(currentYear, currentMonth - 1, 1).getDay(); // 0 = Sun
  const monthName = new Date(currentYear, currentMonth - 1, 1).toLocaleString(
    language === "ta" ? "ta-IN" : "en-US",
    { month: "long" }
  );

  const prevMonth = () => {
    if (currentMonth === 1) {
      setCurrentMonth(12);
      setCurrentYear((y) => y - 1);
    } else {
      setCurrentMonth((m) => m - 1);
    }
  };

  const nextMonth = () => {
    if (currentMonth === 12) {
      setCurrentMonth(1);
      setCurrentYear((y) => y + 1);
    } else {
      setCurrentMonth((m) => m + 1);
    }
  };

  // Candidates on selected date
  const selectedDateCandidates =
    monthData?.candidates.filter((c) => c.event_date === selectedDateStr) || [];

  // Save handler
  const handleSaveSlot = async (slot: CandidateSlot) => {
    const token = session?.access_token || "cookie";
    setSavingId(slot.id);
    try {
      const payload: SaveMuhurtaRequest = {
        title: `${monthData?.occasion.name_en || "Muhurta"} - ${slot.event_date}`,
        occasion_code: selectedOccasion,
        occasion_name: monthData?.occasion.name_en || selectedOccasion,
        event_date: slot.event_date,
        start_time: slot.start_time_utc,
        end_time: slot.end_time_utc,
        local_start_time: slot.start_time_local,
        local_end_time: slot.end_time_local,
        duration_minutes: slot.duration_minutes,
        location_name: cityName,
        latitude,
        longitude,
        timezone: timezoneStr,
        ayanamsa_id: 0,
        tradition: "south_indian",
        score: slot.score,
        status: slot.status,
        panchang_summary: {
          tithi: slot.tithi,
          nakshatra: slot.nakshatra,
          yoga: slot.yoga,
          karana: slot.karana,
          weekday: slot.weekday,
        },
        lagna_summary: slot.ascendant,
        rule_evaluations: {
          passed: slot.passed_rules,
          failed: slot.failed_rules,
          advisories: slot.advisories,
        },
      };
      const res = await saveMuhurtaSelection(token, payload);
      setSavedSuccessMap((prev) => ({ ...prev, [slot.id]: res.record.display_number }));
    } catch (e: any) {
      alert(`Save failed: ${e?.message}`);
    } finally {
      setSavingId(null);
    }
  };

  const openReport = (cand: CandidateSlot) => {
    setReportCandidate({
      title: `${monthData?.occasion.name_en || "Muhurta"} Certificate`,
      occasion_name: monthData?.occasion.name_en || selectedOccasion,
      event_date: cand.event_date,
      start_time_local: cand.start_time_local,
      end_time_local: cand.end_time_local,
      duration_minutes: cand.duration_minutes,
      location_name: cityName,
      latitude,
      longitude,
      timezone: timezoneStr,
      score: cand.score,
      status: cand.status,
      explanation: cand.explanation,
      tithi: cand.tithi,
      nakshatra: cand.nakshatra,
      yoga: cand.yoga,
      karana: cand.karana,
      ascendant: cand.ascendant,
      planets: cand.planets,
      inauspicious_periods: cand.inauspicious_periods,
      auspicious_periods: cand.auspicious_periods,
      passed_rules: cand.passed_rules,
      failed_rules: cand.failed_rules,
      advisories: cand.advisories,
      incomplete_checks: cand.incomplete_checks,
    });
    setIsReportOpen(true);
  };

  return (
    <div className="space-y-6">
      {/* Top Filter and Navigation Bar */}
      <div className="bg-white rounded-3xl p-5 sm:p-6 border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Occasion & Location Selectors */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          <div>
            <label className="block text-[11px] font-semibold text-slate-500 mb-1">
              {language === "ta" ? "நிகழ்வு வகை" : "Occasion"}
            </label>
            <select
              value={selectedOccasion}
              onChange={(e) => setSelectedOccasion(e.target.value)}
              className="px-3 py-2 text-xs font-semibold bg-slate-50 border border-slate-200 rounded-xl text-slate-800"
            >
              {occasions.map((o) => (
                <option key={o.code} value={o.code}>
                  {o.name_en} ({o.name_ta})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-500 mb-1">
              {language === "ta" ? "இடம்" : "Location"}
            </label>
            <div className="px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-700 flex items-center gap-1.5 font-medium">
              <MapPin className="w-3.5 h-3.5 text-amber-600" />
              <span>{cityName}</span>
            </div>
          </div>
        </div>

        {/* Month Navigator */}
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={prevMonth}
            className="p-2 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-700 transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <div className="text-center min-w-[150px]">
            <h3 className="text-base font-extrabold text-slate-900 capitalize">
              {monthName} {currentYear}
            </h3>
            {loadingMonth && (
              <span className="text-[10px] text-amber-600 animate-pulse font-medium">
                {language === "ta" ? "கணக்கிடப்படுகிறது..." : "Calculating..."}
              </span>
            )}
          </div>
          <button
            type="button"
            onClick={nextMonth}
            className="p-2 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-700 transition-colors"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Calendar Legend */}
      <div className="flex flex-wrap items-center justify-center gap-4 text-xs text-slate-600">
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-emerald-500 ring-2 ring-emerald-200" />
          <span>{language === "ta" ? "முழு சுப முகூர்த்தம்" : "Auspicious Slots"}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-amber-500 ring-2 ring-amber-200" />
          <span>{language === "ta" ? "எச்சரிக்கையுடன்" : "With Advisories"}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-rose-400 ring-2 ring-rose-200" />
          <span>{language === "ta" ? "தடைபட்டவை" : "Restricted"}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-slate-300" />
          <span>{language === "ta" ? "சுப நேரம் இல்லை" : "No Viable Slots"}</span>
        </div>
      </div>

      {/* Two Column Layout: Monthly Grid on Left, Selected Date Details on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Calendar Grid (8 cols) */}
        <div className="lg:col-span-8 bg-white rounded-3xl p-6 border border-slate-200 shadow-sm">
          {/* Weekday Headers */}
          <div className="grid grid-cols-7 gap-2 text-center text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
            <div>{language === "ta" ? "ஞாயிறு" : "Sun"}</div>
            <div>{language === "ta" ? "திங்கள்" : "Mon"}</div>
            <div>{language === "ta" ? "செவ்வாய்" : "Tue"}</div>
            <div>{language === "ta" ? "புதன்" : "Wed"}</div>
            <div>{language === "ta" ? "வியாழன்" : "Thu"}</div>
            <div>{language === "ta" ? "வெள்ளி" : "Fri"}</div>
            <div>{language === "ta" ? "சனி" : "Sat"}</div>
          </div>

          {/* Days Grid */}
          <div className="grid grid-cols-7 gap-2">
            {/* Empty slots before first day */}
            {Array.from({ length: firstDayWeekday }).map((_, i) => (
              <div key={`empty-${i}`} className="h-20 sm:h-24 rounded-2xl bg-slate-50/40" />
            ))}

            {/* Days of the month */}
            {Array.from({ length: daysInMonth }).map((_, i) => {
              const dayNum = i + 1;
              const dateStr = `${currentYear}-${String(currentMonth).padStart(2, "0")}-${String(
                dayNum
              ).padStart(2, "0")}`;
              const isSelected = selectedDateStr === dateStr;
              const isToday =
                today.toISOString().split("T")[0] === dateStr;

              const summary = monthData?.calendar_summary?.[dateStr];
              const badge = summary?.badge;
              const slotCount = summary?.total_slots || 0;

              return (
                <button
                  key={dayNum}
                  type="button"
                  onClick={() => setSelectedDateStr(dateStr)}
                  className={`h-20 sm:h-24 p-2 rounded-2xl border text-left flex flex-col justify-between transition-all relative ${
                    isSelected
                      ? "border-amber-500 bg-amber-50/60 ring-2 ring-amber-500/20 shadow-sm"
                      : "border-slate-100 hover:border-slate-300 hover:bg-slate-50/50"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span
                      className={`text-xs sm:text-sm font-extrabold ${
                        isToday
                          ? "w-6 h-6 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs"
                          : isSelected
                          ? "text-amber-800"
                          : "text-slate-800"
                      }`}
                    >
                      {dayNum}
                    </span>

                    {/* Status Badge Indicator */}
                    {badge === "auspicious" && (
                      <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 ring-2 ring-emerald-200" />
                    )}
                    {badge === "moderate" && (
                      <span className="w-2.5 h-2.5 rounded-full bg-amber-500 ring-2 ring-amber-200" />
                    )}
                    {badge === "restricted" && (
                      <span className="w-2.5 h-2.5 rounded-full bg-rose-400 ring-2 ring-rose-200" />
                    )}
                  </div>

                  {/* Cell Footer Info */}
                  <div className="space-y-0.5">
                    {summary ? (
                      <>
                        <div className="text-[10px] text-slate-500 font-medium truncate">
                          {summary.tithi || ""}
                        </div>
                        <div className="text-[10px] text-amber-700 font-bold truncate">
                          {slotCount > 0 ? `${slotCount} ${language === "ta" ? "நேரம்" : "slots"}` : ""}
                        </div>
                      </>
                    ) : (
                      <div className="text-[10px] text-slate-300">-</div>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Selected Date Inspector Panel (4 cols) */}
        <div className="lg:col-span-4 bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-5">
          {/* Header */}
          <div className="border-b border-slate-100 pb-3 flex items-center justify-between">
            <div>
              <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                {language === "ta" ? "தேர்ந்தெடுக்கப்பட்ட தேதி" : "Selected Date"}
              </div>
              <h4 className="text-lg font-black text-slate-900 mt-0.5">{selectedDateStr}</h4>
            </div>
            <div className="text-xs font-semibold px-2.5 py-1 rounded-xl bg-purple-50 text-purple-800">
              {datePanchang?.vara?.name || ""}
            </div>
          </div>

          {/* Daily Panchang Quick Summary */}
          {loadingPanchang ? (
            <div className="p-8 text-center text-xs text-slate-400">
              <div className="w-5 h-5 border-2 border-amber-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
              <span>{language === "ta" ? "பஞ்சாங்கம் பெறப்படுகிறது..." : "Loading Panchang..."}</span>
            </div>
          ) : datePanchang ? (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                  <span className="text-[10px] text-slate-400 block font-bold">
                    {language === "ta" ? "திதி" : "Tithi"}
                  </span>
                  <span className="font-bold text-slate-800">
                    {datePanchang.tithi?.name}
                  </span>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                  <span className="text-[10px] text-slate-400 block font-bold">
                    {language === "ta" ? "நட்சத்திரம்" : "Nakshatra"}
                  </span>
                  <span className="font-bold text-slate-800">
                    {datePanchang.nakshatra?.name}
                  </span>
                </div>
              </div>

              {/* Sun & Moon Timings */}
              <div className="p-2.5 rounded-xl bg-amber-50/60 border border-amber-100 text-xs flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <Sun className="w-3.5 h-3.5 text-amber-600" />
                  <span className="text-slate-700">
                    {datePanchang.solar?.sunrise} – {datePanchang.solar?.sunset}
                  </span>
                </div>
                <div className="text-slate-500 font-mono text-[11px]">
                  Rahu: {datePanchang.inauspicious_periods?.rahu_kalam?.start}
                </div>
              </div>
            </div>
          ) : null}

          {/* Candidate Slots for this date */}
          <div className="space-y-3 pt-2">
            <h5 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center justify-between">
              <span>{language === "ta" ? "முகூர்த்த நேரங்கள்" : "Candidate Windows"}</span>
              <span className="text-amber-700 font-mono font-bold">
                {selectedDateCandidates.length}
              </span>
            </h5>

            {selectedDateCandidates.length === 0 ? (
              <div className="p-5 rounded-2xl bg-slate-50 text-center text-xs text-slate-500">
                {language === "ta"
                  ? "இந்த தேதியில் தேர்ந்தெடுக்கப்பட்ட நிகழ்விற்கு ஏற்ற சுப முகூர்த்தம் அமையவில்லை."
                  : "No auspicious slots found for this occasion on this date."}
              </div>
            ) : (
              <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1">
                {selectedDateCandidates.map((slot) => {
                  const isSaved = savedSuccessMap[slot.id] !== undefined;
                  const isSaving = savingId === slot.id;

                  return (
                    <div
                      key={slot.id}
                      className="p-3 rounded-2xl border border-slate-200 hover:border-amber-300 bg-white transition-all space-y-2 text-xs"
                    >
                      <div className="flex items-center justify-between">
                        <div className="font-bold text-slate-900 flex items-center gap-1">
                          <Clock className="w-3.5 h-3.5 text-amber-600" />
                          <span>
                            {slot.start_time_local} – {slot.end_time_local}
                          </span>
                        </div>
                        <span className="text-xs font-extrabold text-amber-700">
                          {slot.score}/100
                        </span>
                      </div>

                      <div className="text-[11px] text-slate-600 flex items-center justify-between">
                        <span>Lagna: <b>{slot.ascendant.sign_name}</b></span>
                        <span className="text-slate-400">({slot.duration_minutes}m)</span>
                      </div>

                      <div className="flex items-center justify-end gap-2 pt-1 border-t border-slate-100">
                        <button
                          type="button"
                          onClick={() => openReport(slot)}
                          className="px-2 py-1 rounded-lg text-[10px] font-semibold border border-slate-200 hover:bg-slate-50 text-slate-700 flex items-center gap-1"
                        >
                          <Printer className="w-3 h-3" />
                          <span>{language === "ta" ? "அறிக்கை" : "Report"}</span>
                        </button>
                        <button
                          type="button"
                          disabled={isSaved || isSaving}
                          onClick={() => handleSaveSlot(slot)}
                          className={`px-2.5 py-1 rounded-lg text-[10px] font-bold flex items-center gap-1 ${
                            isSaved
                              ? "bg-emerald-100 text-emerald-800"
                              : "bg-slate-900 text-white hover:bg-black"
                          }`}
                        >
                          <Bookmark className="w-3 h-3" />
                          <span>
                            {isSaved
                              ? `#${savedSuccessMap[slot.id]}`
                              : language === "ta" ? "சேமி" : "Save"}
                          </span>
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Official Certificate Report Modal */}
      {reportCandidate && (
        <MuhurtaReportModal
          isOpen={isReportOpen}
          onClose={() => setIsReportOpen(false)}
          reportData={reportCandidate}
        />
      )}
    </div>
  );
}
