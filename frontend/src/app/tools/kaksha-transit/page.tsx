"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  KakshaAlertRequest,
  KakshaAlertsResponse,
  KakshaAlertItem,
} from "@/lib/types";
import { calculateKakshaAlerts } from "@/lib/api";
import {
  Grid,
  Sparkles,
  Calendar,
  Clock,
  ShieldCheck,
  AlertTriangle,
  HeartPulse,
  Coins,
  Briefcase,
  Scale,
  RefreshCw,
  ArrowRight,
  Sliders,
  Filter,
  CheckCircle2,
  AlertCircle,
  Eye,
  Search,
  Database,
  User,
} from "lucide-react";

export default function KakshaTransitAlertsPage() {
  const { language } = useLanguage();
  const { session, isAuthenticated } = useAuth();

  // Mode: Saved chart vs manual entry
  const [savedHoroscopes, setSavedHoroscopes] = useState<any[]>([]);
  const [chartSearchQuery, setChartSearchQuery] = useState<string>("");
  const [selectedHoroscopeId, setSelectedHoroscopeId] = useState<string>("");

  // Form State
  const [birthDate, setBirthDate] = useState<string>("1995-10-24");
  const [birthTime, setBirthTime] = useState<string>("14:30:00");
  const [timezone, setTimezone] = useState<string>("Asia/Kolkata");
  const [latitude, setLatitude] = useState<number>(13.0827);
  const [longitude, setLongitude] = useState<number>(80.2707);

  // Alert Filter State
  const [horizonDays, setHorizonDays] = useState<number>(90);
  const [selectedPlanet, setSelectedPlanet] = useState<string>("all");
  const [selectedDomain, setSelectedDomain] = useState<string>("all");

  // Results State
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<KakshaAlertsResponse | null>(null);

  useEffect(() => {
    async function fetchSavedList() {
      if (!session?.access_token) return;
      try {
        const resp = await fetch("/api/horoscopes?limit=1000", {
          headers: { Authorization: `Bearer ${session.access_token}` },
        });
        if (resp.ok) {
          const data = await resp.json();
          const items = data.horoscopes || [];
          setSavedHoroscopes(items);
          if (items.length > 0 && !selectedHoroscopeId) {
            setSelectedHoroscopeId(items[0].id);
            setBirthDate(items[0].birth_date);
            setBirthTime(items[0].birth_time);
            setTimezone(items[0].timezone || "Asia/Kolkata");
            setLatitude(items[0].latitude);
            setLongitude(items[0].longitude);
          }
        }
      } catch (err) {
        console.warn("Could not load saved horoscopes:", err);
      }
    }
    if (isAuthenticated) fetchSavedList();
  }, [isAuthenticated, session?.access_token]);

  const handleSelectSavedChart = (id: string) => {
    setSelectedHoroscopeId(id);
    const found = savedHoroscopes.find((h) => h.id === id);
    if (found) {
      setBirthDate(found.birth_date);
      setBirthTime(found.birth_time);
      setTimezone(found.timezone || "Asia/Kolkata");
      setLatitude(found.latitude);
      setLongitude(found.longitude);
    }
  };

  const handleScanAlerts = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload: KakshaAlertRequest = {
        birth_date: birthDate,
        birth_time: birthTime,
        timezone,
        latitude: Number(latitude),
        longitude: Number(longitude),
        horizon_days: Number(horizonDays),
        planets: ["Saturn", "Jupiter", "Mars"],
        filter_domain: selectedDomain === "all" ? null : selectedDomain,
        ayanamsa: 1,
      };

      const res = await calculateKakshaAlerts(payload);
      setResult(res);
    } catch (err: any) {
      setError(err?.detail || err?.message || "Kaksha alerts calculation failed.");
    } finally {
      setLoading(false);
    }
  };

  const filteredTimeline = result
    ? result.timeline_alerts.filter((item) => {
        if (selectedPlanet !== "all" && item.planet !== selectedPlanet) {
          return false;
        }
        if (selectedDomain !== "all" && !item.life_domains.includes(selectedDomain)) {
          return false;
        }
        return true;
      })
    : [];

  return (
    <div className="min-h-screen bg-[#F8FAFC] pb-24 text-[#0F172A]">
      {/* Top Banner */}
      <div className="bg-linear-to-r from-[#102A4C] via-[#153F6B] to-[#1E4E8C] text-white py-10 px-4 sm:px-6 lg:px-8 border-b border-[#254F7F]">
        <div className="max-w-7xl mx-auto space-y-4">
          <Breadcrumbs
            items={[
              { label: language === "ta" ? "முகப்பு" : "Home", href: "/" },
              { label: language === "ta" ? "கருவிகள்" : "Tools", href: "/tools" },
              { label: language === "ta" ? "அஷ்டகவர்க்கம்" : "Ashtakavarga", href: "/tools/ashtakavarga" },
              { label: language === "ta" ? "கக்ஷா கோச்சார எச்சரிக்கை" : "Kaksha Transit Alerts" },
            ]}
          />

          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pt-2">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-400/20 border border-amber-300/30 text-amber-200 text-xs font-semibold mb-3">
                <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                <span>Accuracy Booster • Parashari 3°45' Sub-Division Engine</span>
              </div>
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-serif font-bold text-white tracking-tight">
                {language === "ta"
                  ? "அஷ்டகவர்க்க கக்ஷா கோச்சார தூண்டுதல் எச்சரிக்கை"
                  : "Ashtakavarga Kaksha Transit Trigger Alert System"}
              </h1>
              <p className="text-sm sm:text-base text-slate-200 mt-2 max-w-3xl leading-relaxed">
                {language === "ta"
                  ? "தினசரி பலனில் ஒரு சம்பவம் கைகூடுவதற்கும் அல்லது தடைபடுவதற்கும், கோச்சார சனி, குரு அல்லது செவ்வாய் உங்கள் ஜாதகத்தில் பிந்து (1) அல்லது பிந்து இல்லாத (0) குறிப்பிட்ட 3° 45' கக்ஷாவைக் கடக்கும் தருணமே காரணியாகும். உடல்நலம், நிதி மற்றும் வழக்குகளுக்கான நிகழ்நேர கோச்சார நாட்காட்டி."
                  : "In daily predictive practice, an event triggers when transit Saturn, Mars, or Jupiter crosses a specific 3°45' Kaksha where the bindu is 1 (auspicious) or 0 (inauspicious). Real-time calendar radar for Health, Finances, Career, and Lawsuits."}
              </p>
            </div>

            <div className="flex items-center gap-3">
              <Link
                href="/tools/birth-time-rectification"
                className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-xs font-medium text-white transition-all flex items-center gap-2"
              >
                <span>BTR Assistant</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
              <Link
                href="/tools/double-transit"
                className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-xs font-medium text-white transition-all flex items-center gap-2"
              >
                <span>Double Transit Radar</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Form & Filters */}
          <div className="lg:col-span-5 space-y-6">
            {/* Saved Horoscope Search & Selector */}
            {savedHoroscopes.length > 0 && (
              <div className="bg-white rounded-2xl p-5 shadow-xs border border-[#E2E8F0] space-y-3">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold text-[#102A4C]">
                    {language === "ta" ? "ஜாதகரைத் தேர்ந்தெடுக்கவும்" : "Select Saved Client Chart"}
                  </label>
                  <span className="text-[11px] font-mono text-[#64748B]">
                    {savedHoroscopes.length} saved
                  </span>
                </div>

                <div className="relative">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                  <input
                    type="text"
                    value={chartSearchQuery}
                    onChange={(e) => setChartSearchQuery(e.target.value)}
                    placeholder="Search by client name, place, date..."
                    className="w-full text-xs pl-9 pr-3 py-2 border border-[#CBD5E1] rounded-xl outline-none focus:ring-2 focus:ring-[#102A4C] bg-[#F8FAFC]"
                  />
                </div>

                <div className="max-h-40 overflow-y-auto space-y-1.5 pt-1">
                  {savedHoroscopes
                    .filter((h) => {
                      if (!chartSearchQuery) return true;
                      const q = chartSearchQuery.toLowerCase();
                      return (
                        (h.person_name && h.person_name.toLowerCase().includes(q)) ||
                        (h.location_name && h.location_name.toLowerCase().includes(q)) ||
                        (h.birth_date && h.birth_date.includes(q))
                      );
                    })
                    .map((h) => {
                      const isSel = h.id === selectedHoroscopeId;
                      return (
                        <div
                          key={h.id}
                          onClick={() => handleSelectSavedChart(h.id)}
                          className={`p-2.5 rounded-xl border text-left cursor-pointer transition-all flex items-center justify-between ${
                            isSel
                              ? "bg-[#FAF7F0] border-[#B4872B] ring-1 ring-[#B4872B]/30"
                              : "hover:bg-slate-50 border-[#E2E8F0]"
                          }`}
                        >
                          <div>
                            <strong className="text-xs text-[#102A4C] block">
                              {h.person_name || "Unnamed"}
                            </strong>
                            <span className="text-[10px] font-mono text-[#64748B]">
                              {h.birth_date} @ {h.birth_time} • {h.location_name || `${h.latitude}, ${h.longitude}`}
                            </span>
                          </div>
                          {isSel && <CheckCircle2 className="w-4 h-4 text-[#B4872B] shrink-0" />}
                        </div>
                      );
                    })}
                </div>
              </div>
            )}

            {/* Birth Details Card */}
            <div className="bg-white rounded-2xl p-6 shadow-xs border border-[#E2E8F0] space-y-4">
              <div className="flex items-center gap-2 pb-3 border-b border-[#F1F5F9]">
                <Clock className="w-5 h-5 text-[#102A4C]" />
                <h3 className="font-serif font-bold text-base text-[#102A4C]">
                  {language === "ta" ? "ஜாதகரின் பிறந்த விவரங்கள்" : "Birth Information"}
                </h3>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-[#475569] mb-1">
                    {language === "ta" ? "பிறந்த தேதி" : "Birth Date"}
                  </label>
                  <input
                    type="date"
                    value={birthDate}
                    onChange={(e) => setBirthDate(e.target.value)}
                    className="w-full text-xs font-mono px-3 py-2 border border-[#CBD5E1] rounded-lg outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-[#475569] mb-1">
                    {language === "ta" ? "பிறந்த நேரம்" : "Birth Time"}
                  </label>
                  <input
                    type="time"
                    step="1"
                    value={birthTime}
                    onChange={(e) => setBirthTime(e.target.value)}
                    className="w-full text-xs font-mono px-3 py-2 border border-[#CBD5E1] rounded-lg outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-[11px] font-semibold text-[#475569] mb-1">Timezone</label>
                  <input
                    type="text"
                    value={timezone}
                    onChange={(e) => setTimezone(e.target.value)}
                    className="w-full text-xs font-mono px-2 py-1.5 border border-[#CBD5E1] rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-[#475569] mb-1">Latitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={latitude}
                    onChange={(e) => setLatitude(parseFloat(e.target.value))}
                    className="w-full text-xs font-mono px-2 py-1.5 border border-[#CBD5E1] rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-[#475569] mb-1">Longitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={longitude}
                    onChange={(e) => setLongitude(parseFloat(e.target.value))}
                    className="w-full text-xs font-mono px-2 py-1.5 border border-[#CBD5E1] rounded-lg"
                  />
                </div>
              </div>

              {/* Forecast Horizon */}
              <div className="pt-3 border-t border-[#F1F5F9] space-y-2">
                <span className="text-xs font-semibold text-[#334155] block">
                  Forecast Window: {horizonDays} Days
                </span>
                <div className="flex items-center gap-1.5">
                  {[30, 60, 90, 180, 365].map((d) => (
                    <button
                      key={d}
                      type="button"
                      onClick={() => setHorizonDays(d)}
                      className={`flex-1 py-1 text-xs font-mono rounded-md transition-colors ${
                        horizonDays === d
                          ? "bg-[#102A4C] text-white font-bold"
                          : "bg-slate-100 hover:bg-slate-200 text-[#475569]"
                      }`}
                    >
                      {d}D
                    </button>
                  ))}
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              {/* Submit Button */}
              <button
                type="button"
                onClick={handleScanAlerts}
                disabled={loading}
                className="w-full py-3.5 px-4 rounded-xl bg-linear-to-r from-[#102A4C] to-[#153F6B] hover:from-[#0B1E38] hover:to-[#102A4C] text-white font-serif font-bold text-sm tracking-wide shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin text-amber-300" />
                    <span>Evaluating 96-Kakshas & Ingress Crossings...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-amber-300" />
                    <span>Calculate Kaksha Transit Triggers</span>
                  </>
                )}
              </button>
            </div>

            {/* Life Domain Advice Cards (when calculated) */}
            {result && (
              <div className="bg-white rounded-2xl p-6 shadow-xs border border-[#E2E8F0] space-y-4">
                <div className="flex items-center gap-2 pb-3 border-b border-[#F1F5F9]">
                  <ShieldCheck className="w-5 h-5 text-emerald-600" />
                  <h3 className="font-serif font-bold text-base text-[#102A4C]">
                    Life Domain Summary Radar
                  </h3>
                </div>

                <div className="space-y-3 text-xs">
                  {/* Health */}
                  <div className="p-3 rounded-xl bg-emerald-50/60 border border-emerald-200 space-y-1">
                    <div className="flex items-center justify-between font-bold text-emerald-900">
                      <span className="flex items-center gap-1.5">
                        <HeartPulse className="w-4 h-4 text-emerald-600" /> Health & Vitality
                      </span>
                      <span className="font-mono text-[11px]">
                        🟢 {result.domain_summaries.health.favorable_windows_count} / 🔴 {result.domain_summaries.health.challenging_windows_count}
                      </span>
                    </div>
                    <p className="text-[#334155] text-[11px] leading-relaxed">
                      {result.domain_summaries.health.key_advice}
                    </p>
                  </div>

                  {/* Finances */}
                  <div className="p-3 rounded-xl bg-amber-50/60 border border-amber-200 space-y-1">
                    <div className="flex items-center justify-between font-bold text-amber-900">
                      <span className="flex items-center gap-1.5">
                        <Coins className="w-4 h-4 text-[#8C6D23]" /> Wealth & Investments
                      </span>
                      <span className="font-mono text-[11px]">
                        🟢 {result.domain_summaries.finances.favorable_windows_count} / 🔴 {result.domain_summaries.finances.challenging_windows_count}
                      </span>
                    </div>
                    <p className="text-[#334155] text-[11px] leading-relaxed">
                      {result.domain_summaries.finances.key_advice}
                    </p>
                  </div>

                  {/* Career */}
                  <div className="p-3 rounded-xl bg-indigo-50/60 border border-indigo-200 space-y-1">
                    <div className="flex items-center justify-between font-bold text-indigo-900">
                      <span className="flex items-center gap-1.5">
                        <Briefcase className="w-4 h-4 text-indigo-600" /> Career & Status
                      </span>
                      <span className="font-mono text-[11px]">
                        🟢 {result.domain_summaries.career.favorable_windows_count} / 🔴 {result.domain_summaries.career.challenging_windows_count}
                      </span>
                    </div>
                    <p className="text-[#334155] text-[11px] leading-relaxed">
                      {result.domain_summaries.career.key_advice}
                    </p>
                  </div>

                  {/* Lawsuits */}
                  <div className="p-3 rounded-xl bg-rose-50/60 border border-rose-200 space-y-1">
                    <div className="flex items-center justify-between font-bold text-rose-900">
                      <span className="flex items-center gap-1.5">
                        <Scale className="w-4 h-4 text-rose-600" /> Lawsuits & Disputes
                      </span>
                      <span className="font-mono text-[11px]">
                        🟢 {result.domain_summaries.lawsuits.favorable_windows_count} / 🔴 {result.domain_summaries.lawsuits.challenging_windows_count}
                      </span>
                    </div>
                    <p className="text-[#334155] text-[11px] leading-relaxed">
                      {result.domain_summaries.lawsuits.key_advice}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right Column: Live Status & Chronological Timeline */}
          <div className="lg:col-span-7 space-y-6">
            {!result ? (
              <div className="bg-white rounded-2xl p-12 text-center border border-[#E2E8F0] shadow-xs space-y-4">
                <div className="w-16 h-16 rounded-2xl bg-amber-50 border border-amber-200 text-[#8C6D23] flex items-center justify-center mx-auto">
                  <Grid className="w-8 h-8" />
                </div>
                <div className="max-w-md mx-auto space-y-2">
                  <h3 className="font-serif font-bold text-lg text-[#102A4C]">
                    {language === "ta" ? "கக்ஷா கோச்சார ஆய்வு தயார்" : "Kaksha Alert Engine Ready"}
                  </h3>
                  <p className="text-xs text-[#64748B] leading-relaxed">
                    {language === "ta"
                      ? "இடதுபுறத்தில் உங்கள் பிறந்த விவரங்களை உள்ளிட்டு ஸ்கேன் செய்யுங்கள். இன்று கோச்சார சனி, குரு மற்றும் செவ்வாய் உங்கள் ஜாதகத்தில் எந்த கக்ஷாவில் (பிந்து 1 அல்லது 0) சஞ்சரிக்கின்றன என்பதை நேரலையாகக் காட்டும்."
                      : "Enter your birth details on the left to activate the real-time Kaksha Trigger Alert engine. It tracks the exact 3°45' Kaksha transits of Saturn, Jupiter, and Mars across your Ashtakavarga matrix."}
                  </p>
                </div>
              </div>
            ) : (
              <>
                {/* Active Right Now Status Cards */}
                <div className="bg-linear-to-br from-[#102A4C] via-[#153F6B] to-[#1A365D] rounded-2xl p-6 text-white shadow-lg border border-amber-400/30 space-y-4">
                  <div className="flex items-center justify-between border-b border-white/10 pb-3">
                    <div>
                      <span className="text-[10px] font-mono uppercase tracking-wider text-amber-300 font-semibold block">
                        Real-Time Live Transit Status
                      </span>
                      <h3 className="text-lg font-serif font-bold text-white">
                        Planets Active In Kakshas Today
                      </h3>
                    </div>
                    <span className="px-2.5 py-1 rounded-full text-xs font-mono bg-white/10 border border-white/20">
                      Lagna: {result.natal_lagna_sign}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    {result.active_now.map((act) => (
                      <div
                        key={act.planet}
                        className={`p-3.5 rounded-xl border transition-all ${
                          act.has_bindu
                            ? "bg-emerald-950/40 border-emerald-400/40"
                            : "bg-rose-950/40 border-rose-400/40"
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1.5">
                          <span className="font-bold text-sm text-white">{act.planet}</span>
                          <span
                            className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-bold ${
                              act.has_bindu
                                ? "bg-emerald-500/30 text-emerald-300 border border-emerald-400/30"
                                : "bg-rose-500/30 text-rose-300 border border-rose-400/30"
                            }`}
                          >
                            {act.has_bindu ? "1 Bindu 🟢" : "0 Bindu 🔴"}
                          </span>
                        </div>
                        <div className="text-xs text-slate-200 font-medium">
                          In {act.current_sign} ({act.current_degree}°)
                        </div>
                        <div className="text-[11px] text-amber-300 font-mono mt-1">
                          Kaksha #{act.kaksha_number} ({act.kaksha_lord})
                        </div>
                        <span className="text-[10px] text-slate-400 block mt-1">
                          House {act.house_from_lagna} • ~{act.days_remaining_in_kaksha} days left
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Timeline Feed & Filters */}
                <div className="bg-white rounded-2xl p-6 shadow-xs border border-[#E2E8F0] space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#F1F5F9]">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-5 h-5 text-[#8C6D23]" />
                      <h3 className="font-serif font-bold text-base text-[#102A4C]">
                        {horizonDays}-Day Kaksha Ingress Trigger Calendar
                      </h3>
                    </div>

                    {/* Filter Pills */}
                    <div className="flex flex-wrap items-center gap-1.5 text-xs">
                      <select
                        value={selectedPlanet}
                        onChange={(e) => setSelectedPlanet(e.target.value)}
                        className="text-xs font-semibold px-2 py-1 rounded-md border border-[#CBD5E1] bg-white text-[#334155]"
                      >
                        <option value="all">All Grahas</option>
                        <option value="Saturn">Saturn</option>
                        <option value="Jupiter">Jupiter</option>
                        <option value="Mars">Mars</option>
                      </select>

                      <select
                        value={selectedDomain}
                        onChange={(e) => setSelectedDomain(e.target.value)}
                        className="text-xs font-semibold px-2 py-1 rounded-md border border-[#CBD5E1] bg-white text-[#334155]"
                      >
                        <option value="all">All Domains</option>
                        <option value="health">Health</option>
                        <option value="finances">Finances</option>
                        <option value="career">Career</option>
                        <option value="lawsuits">Lawsuits</option>
                      </select>
                    </div>
                  </div>

                  {/* Timeline Cards */}
                  <div className="space-y-3">
                    {filteredTimeline.length === 0 ? (
                      <div className="p-8 text-center text-[#64748B] text-xs">
                        No Kaksha triggers match the selected filters.
                      </div>
                    ) : (
                      filteredTimeline.map((item) => {
                        const isAusp = item.has_bindu;
                        return (
                          <div
                            key={item.id}
                            className={`p-4 rounded-xl border transition-all space-y-2 ${
                              isAusp
                                ? "bg-emerald-50/40 border-emerald-200/80 hover:border-emerald-300"
                                : "bg-rose-50/40 border-rose-200/80 hover:border-rose-300"
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <span
                                  className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                                    isAusp
                                      ? "bg-emerald-100 text-emerald-800"
                                      : "bg-rose-100 text-rose-800"
                                  }`}
                                >
                                  {item.alert_badge}
                                </span>
                                <strong className="text-xs text-[#102A4C]">
                                  {item.planet} in {item.sign_name} (Kaksha #{item.kaksha_number}: {item.kaksha_lord})
                                </strong>
                              </div>

                              <span className="text-[11px] font-mono text-[#64748B]">
                                {item.start_date} – {item.end_date} ({item.duration_days}d)
                              </span>
                            </div>

                            <div className="flex flex-wrap items-center gap-2 text-[11px] text-[#64748B]">
                              <span>Span: <strong className="font-mono text-[#102A4C]">{item.kaksha_range}</strong></span>
                              <span>•</span>
                              <span>House from Lagna: <strong className="text-[#102A4C]">{item.house_from_lagna}</strong></span>
                              <span>•</span>
                              <span>Severity: <strong className={isAusp ? "text-emerald-700" : "text-rose-700"}>{item.severity_level}</strong></span>
                            </div>

                            <p className="text-xs text-[#334155] leading-relaxed pt-1 border-t border-slate-200/60">
                              {language === "ta" ? item.guidance_ta : item.guidance}
                            </p>
                          </div>
                        );
                      })
                    )}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
