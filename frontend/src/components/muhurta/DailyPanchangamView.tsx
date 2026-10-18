"use client";

import React, { useState, useEffect } from "react";
import { useLanguage } from "@/lib/i18n";
import { getDailyPanchang } from "@/lib/api";
import {
  Sun,
  Moon,
  Compass,
  Clock,
  Calendar,
  ShieldAlert,
  Sparkles,
  MapPin,
  RefreshCw,
  AlertCircle,
  ShieldCheck,
} from "lucide-react";

export function DailyPanchangamView() {
  const { language } = useLanguage();

  const [dateStr, setDateStr] = useState<string>(() => {
    return new Date().toISOString().split("T")[0];
  });
  const [cityName, setCityName] = useState("Chennai, India");
  const [latitude, setLatitude] = useState(13.0827);
  const [longitude, setLongitude] = useState(80.2707);
  const [timezoneStr, setTimezoneStr] = useState("Asia/Kolkata");

  const [panchangData, setPanchangData] = useState<Record<string, any> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPanchang = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getDailyPanchang({
        date: dateStr,
        latitude,
        longitude,
        timezone: timezoneStr,
        ayanamsa_id: 0,
      });
      setPanchangData(res);
    } catch (err: any) {
      setError(err?.message || "Failed to calculate daily Panchangam.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPanchang();
  }, [dateStr, latitude, longitude, timezoneStr]);

  return (
    <div className="space-y-8">
      {/* Search & Location Bar */}
      <div className="p-5 sm:p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="font-serif text-lg sm:text-xl font-bold text-[#102A4C]">
              {language === "ta" ? "தினசரி பஞ்சாங்கம்" : "Daily Panchangam"}
            </h2>
            <p className="text-xs text-[#52667E]">
              {language === "ta"
                ? "சூரிய உதயம், திதி, நட்சத்திரம் மற்றும் கால அளவுகள்"
                : "Astronomical 5-limbs, sunrise-sunset boundaries, and traditional period timings"}
            </p>
          </div>

          <button
            type="button"
            onClick={fetchPanchang}
            disabled={loading}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#DDE5F0] bg-[#F8FAFC] hover:bg-[#EFF6FF] text-xs font-semibold text-[#102A4C] transition-colors cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-[#3478F6]" : ""}`} />
            <span>{loading ? "Calculating..." : "Refresh"}</span>
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
          <div>
            <label className="block text-[11px] font-bold text-[#52667E] mb-1">
              {language === "ta" ? "தேதி / Date" : "Date"}
            </label>
            <input
              type="date"
              value={dateStr}
              onChange={(e) => setDateStr(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] bg-white text-[#102A4C] font-medium focus:outline-hidden focus:border-[#3478F6]"
            />
          </div>

          <div>
            <label className="block text-[11px] font-bold text-[#52667E] mb-1">
              {language === "ta" ? "நகரம் / Location" : "Location"}
            </label>
            <input
              type="text"
              value={cityName}
              onChange={(e) => setCityName(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] bg-white text-[#102A4C] font-medium focus:outline-hidden focus:border-[#3478F6]"
            />
          </div>

          <div>
            <label className="block text-[11px] font-bold text-[#52667E] mb-1">
              Coordinates (Lat, Lon)
            </label>
            <div className="grid grid-cols-2 gap-1.5">
              <input
                type="number"
                step="0.0001"
                value={latitude}
                onChange={(e) => setLatitude(parseFloat(e.target.value) || 0)}
                className="w-full px-2 py-2 rounded-xl border border-[#DDE5F0] bg-white text-[#102A4C] font-medium text-center focus:outline-hidden focus:border-[#3478F6]"
              />
              <input
                type="number"
                step="0.0001"
                value={longitude}
                onChange={(e) => setLongitude(parseFloat(e.target.value) || 0)}
                className="w-full px-2 py-2 rounded-xl border border-[#DDE5F0] bg-white text-[#102A4C] font-medium text-center focus:outline-hidden focus:border-[#3478F6]"
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-bold text-[#52667E] mb-1">
              Timezone
            </label>
            <input
              type="text"
              value={timezoneStr}
              onChange={(e) => setTimezoneStr(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] bg-white text-[#102A4C] font-medium focus:outline-hidden focus:border-[#3478F6]"
            />
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {loading && (
        <div className="p-12 text-center">
          <div className="w-8 h-8 border-4 border-[#3478F6] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-xs text-[#52667E]">Calculating location-specific astronomical Panchangam...</p>
        </div>
      )}

      {!loading && panchangData && (
        <div className="space-y-8">
          {/* 1. Solar & Astronomical Header Card */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-5 rounded-2xl bg-amber-50/70 border border-amber-200 text-[#102A4C] space-y-1">
              <div className="flex items-center gap-2 text-amber-700 text-xs font-bold uppercase">
                <Sun className="w-4 h-4 text-amber-600" />
                <span>சூரிய உதயம் / Sunrise</span>
              </div>
              <div className="text-2xl font-serif font-bold text-[#102A4C]">
                {panchangData.astronomical.sunrise_local}
              </div>
              <div className="text-[11px] text-[#52667E]">Astronomical Zenith 90° 50&apos;</div>
            </div>

            <div className="p-5 rounded-2xl bg-orange-50/70 border border-orange-200 text-[#102A4C] space-y-1">
              <div className="flex items-center gap-2 text-orange-700 text-xs font-bold uppercase">
                <Sun className="w-4 h-4 text-orange-600" />
                <span>சூரிய அஸ்தமனம் / Sunset</span>
              </div>
              <div className="text-2xl font-serif font-bold text-[#102A4C]">
                {panchangData.astronomical.sunset_local}
              </div>
              <div className="text-[11px] text-[#52667E]">
                Day length: {panchangData.astronomical.day_length_hours} hrs
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-indigo-50/70 border border-indigo-200 text-[#102A4C] space-y-1">
              <div className="flex items-center gap-2 text-indigo-700 text-xs font-bold uppercase">
                <Compass className="w-4 h-4 text-indigo-600" />
                <span>நண்பகல் / Solar Noon</span>
              </div>
              <div className="text-2xl font-serif font-bold text-[#102A4C]">
                {panchangData.astronomical.solar_noon_local}
              </div>
              <div className="text-[11px] text-[#52667E]">Hour Angle 0° Meridian</div>
            </div>

            <div className="p-5 rounded-2xl bg-[#FAF8F5] border border-[#DDE5F0] text-[#102A4C] space-y-1">
              <div className="flex items-center gap-2 text-[#8C6D23] text-xs font-bold uppercase">
                <Calendar className="w-4 h-4 text-[#B8862B]" />
                <span>வாரம் / Weekday</span>
              </div>
              <div className="text-2xl font-serif font-bold text-[#102A4C]">
                {panchangData.vara.name_en}
              </div>
              <div className="text-[11px] text-[#52667E]">
                {panchangData.vara.name_ta} • {panchangData.vara.sanskrit_name}
              </div>
            </div>
          </div>

          {/* 2. Five Limbs Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Tithi Detail */}
            <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-3">
              <div className="flex items-center justify-between pb-3 border-b border-[#F1F5F9]">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-[#FAF2DE] text-[#B8862B] flex items-center justify-center">
                    <Moon className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-[11px] font-bold uppercase tracking-wider text-[#8C6D23]">Limb 1</span>
                    <h3 className="font-serif text-base font-bold text-[#102A4C]">திதி / Tithi</h3>
                  </div>
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
                  {panchangData.tithi.paksha} Paksha
                </span>
              </div>

              <div className="space-y-1.5">
                <div className="text-lg font-bold text-[#102A4C]">
                  {panchangData.tithi.name}
                  {panchangData.tithi.name_ta && (
                    <span className="text-xs font-tamil text-[#52667E] ml-2">({panchangData.tithi.name_ta})</span>
                  )}
                </div>
                <div className="text-xs text-[#52667E] flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4">
                  <div>Starts: <strong className="text-[#102A4C]">{panchangData.tithi.start_time_local}</strong></div>
                  <div>Ends: <strong className="text-[#102A4C]">{panchangData.tithi.end_time_local}</strong></div>
                </div>
              </div>
            </div>

            {/* Nakshatra Detail */}
            <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-3">
              <div className="flex items-center justify-between pb-3 border-b border-[#F1F5F9]">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-[#EBF2FE] text-[#3478F6] flex items-center justify-center">
                    <Sparkles className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-[11px] font-bold uppercase tracking-wider text-[#3478F6]">Limb 2</span>
                    <h3 className="font-serif text-base font-bold text-[#102A4C]">நட்சத்திரம் / Nakshatra</h3>
                  </div>
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-[#EBF2FE] text-[#3478F6] border border-[#BFDBFE]">
                  Pada {panchangData.nakshatra.pada}
                </span>
              </div>

              <div className="space-y-1.5">
                <div className="text-lg font-bold text-[#102A4C]">
                  {panchangData.nakshatra.name}
                  {panchangData.nakshatra.name_ta && (
                    <span className="text-xs font-tamil text-[#52667E] ml-2">({panchangData.nakshatra.name_ta})</span>
                  )}
                </div>
                <div className="text-xs text-[#52667E] flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4">
                  <div>Lord: <strong className="text-[#102A4C]">{panchangData.nakshatra.lord}</strong></div>
                  <div>Ends: <strong className="text-[#102A4C]">{panchangData.nakshatra.end_time_local}</strong></div>
                </div>
              </div>
            </div>

            {/* Yoga Detail */}
            <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-[#52667E]">Limb 3</span>
              <h3 className="font-serif text-base font-bold text-[#102A4C]">யோகம் / Yoga</h3>
              <div className="text-base font-bold text-[#102A4C]">
                {panchangData.yoga.name} (#{panchangData.yoga.number})
              </div>
              <div className="text-xs text-[#52667E]">Combined Solar &amp; Lunar Longitude (13° 20&apos;)</div>
            </div>

            {/* Karana Detail */}
            <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-[#52667E]">Limb 4</span>
              <h3 className="font-serif text-base font-bold text-[#102A4C]">கரணம் / Karana</h3>
              <div className="text-base font-bold text-[#102A4C]">
                {panchangData.karana.name} (#{panchangData.karana.number})
              </div>
              <div className="text-xs text-[#52667E]">Half-Tithi interval (6° arc difference)</div>
            </div>
          </div>

          {/* 3. Prohibited & Auspicious Periods of the Day */}
          <div className="p-6 sm:p-8 rounded-3xl bg-white border border-[#DDE5F0] shadow-xs space-y-6">
            <h3 className="font-serif text-lg font-bold text-[#102A4C] pb-3 border-b border-[#F1F5F9] flex items-center justify-between">
              <span>{language === "ta" ? "சுப மற்றும் அசுப கால அளவுகள்" : "Daytime Auspicious & Prohibited Windows"}</span>
              <span className="text-xs font-normal text-[#52667E]">Proportional to local daylight</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Rahu Kalam */}
              <div className="p-4 rounded-xl bg-rose-50/70 border border-rose-200 space-y-1 text-xs">
                <div className="flex items-center justify-between text-rose-800 font-bold">
                  <span>இராகு காலம் / Rahu Kalam</span>
                  <span className="px-2 py-0.5 rounded-full bg-rose-100 text-[10px]">Avoid</span>
                </div>
                <div className="text-base font-bold text-rose-950 font-serif">
                  {new Date(panchangData.inauspicious_periods.rahu_kalam.start_utc).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} — {new Date(panchangData.inauspicious_periods.rahu_kalam.end_utc).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
                <div className="text-[11px] text-rose-700">
                  Octant #{panchangData.inauspicious_periods.rahu_kalam.part} ({panchangData.inauspicious_periods.rahu_kalam.duration_minutes} min)
                </div>
              </div>

              {/* Yamagandam */}
              <div className="p-4 rounded-xl bg-orange-50/70 border border-orange-200 space-y-1 text-xs">
                <div className="flex items-center justify-between text-orange-800 font-bold">
                  <span>எமகண்டம் / Yamagandam</span>
                  <span className="px-2 py-0.5 rounded-full bg-orange-100 text-[10px]">Avoid</span>
                </div>
                <div className="text-base font-bold text-orange-950 font-serif">
                  {new Date(panchangData.inauspicious_periods.yamagandam.start_utc).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} — {new Date(panchangData.inauspicious_periods.yamagandam.end_utc).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
                <div className="text-[11px] text-orange-700">
                  Octant #{panchangData.inauspicious_periods.yamagandam.part} ({panchangData.inauspicious_periods.yamagandam.duration_minutes} min)
                </div>
              </div>

              {/* Gulikai */}
              <div className="p-4 rounded-xl bg-indigo-50/70 border border-indigo-200 space-y-1 text-xs">
                <div className="flex items-center justify-between text-indigo-800 font-bold">
                  <span>குளிகை காலம் / Gulika Kalam</span>
                  <span className="px-2 py-0.5 rounded-full bg-indigo-100 text-[10px]">Repeats action</span>
                </div>
                <div className="text-base font-bold text-indigo-950 font-serif">
                  {new Date(panchangData.inauspicious_periods.gulikai.start_utc).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} — {new Date(panchangData.inauspicious_periods.gulikai.end_utc).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
                <div className="text-[11px] text-indigo-700">
                  Octant #{panchangData.inauspicious_periods.gulikai.part} ({panchangData.inauspicious_periods.gulikai.duration_minutes} min)
                </div>
              </div>

              {/* Varjyam */}
              <div className="p-4 rounded-xl bg-red-50/70 border border-red-200 space-y-1 text-xs">
                <div className="flex items-center justify-between text-red-800 font-bold">
                  <span>வர்ஜியம் / Tyajyam</span>
                  <span className="px-2 py-0.5 rounded-full bg-red-100 text-[10px]">4 Ghatikas strictly avoided</span>
                </div>
                <div className="text-base font-bold text-red-950 font-serif">
                  {new Date(panchangData.varjyam.start_utc).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} — {new Date(panchangData.varjyam.end_utc).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
                <div className="text-[11px] text-red-700">
                  From {panchangData.varjyam.start_ghatika}th Ghatika of {panchangData.nakshatra.name}
                </div>
              </div>

              {/* Abhijit Muhurta */}
              <div className="p-4 rounded-xl bg-emerald-50/70 border border-emerald-200 space-y-1 text-xs">
                <div className="flex items-center justify-between text-emerald-800 font-bold">
                  <span>அபிஜித் முகூர்த்தம் / Abhijit</span>
                  <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-[10px]">8th Muhurta (Auspicious)</span>
                </div>
                <div className="text-base font-bold text-emerald-950 font-serif">
                  {new Date(panchangData.auspicious_periods.abhijit.start_utc).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} — {new Date(panchangData.auspicious_periods.abhijit.end_utc).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
                <div className="text-[11px] text-emerald-700">
                  {panchangData.auspicious_periods.abhijit.is_dur_muhurta_clash
                    ? "Warning: Clashes with Wednesday Dur Muhurta"
                    : "Potent midday interval that neutralizes minor doshas"}
                </div>
              </div>

              {/* Amrita Kalam */}
              <div className="p-4 rounded-xl bg-teal-50/70 border border-teal-200 space-y-1 text-xs">
                <div className="flex items-center justify-between text-teal-800 font-bold">
                  <span>அமிர்த காலம் / Amrita Kalam</span>
                  <span className="px-2 py-0.5 rounded-full bg-teal-100 text-[10px]">Nectar Window</span>
                </div>
                <div className="text-base font-bold text-teal-950 font-serif">
                  {new Date(panchangData.auspicious_periods.amrita_kalam.start_utc).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} — {new Date(panchangData.auspicious_periods.amrita_kalam.end_utc).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
                <div className="text-[11px] text-teal-700">
                  Benefic 4-ghatika window
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
