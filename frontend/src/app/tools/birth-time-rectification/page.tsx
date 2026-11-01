"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  BtrRequest,
  BtrResponse,
  BtrLifeEventInput,
  BtrCandidateDetail,
} from "@/lib/types";
import { rectifyBirthTime, getBtrEventTemplates } from "@/lib/api";
import {
  Clock,
  Sparkles,
  Calendar,
  AlertCircle,
  CheckCircle2,
  HelpCircle,
  Layers,
  ArrowRight,
  TrendingUp,
  Activity,
  Award,
  ShieldCheck,
  RefreshCw,
  Plus,
  Trash2,
  Sliders,
  ChevronDown,
  Compass,
  Search,
  User,
  Database,
} from "lucide-react";

interface SavedHoroItem {
  id: string;
  person_name: string;
  birth_date: string;
  birth_time: string;
  timezone: string;
  latitude: number;
  longitude: number;
  location_name?: string;
  display_number?: number;
}

const CANONICAL_TEMPLATES = [
  {
    id: "first_job",
    label: "First Job / Major Promotion",
    primary_house: 10,
    secondary_houses: [2, 6, 11],
    default_offset_years: 23,
  },
  {
    id: "marriage",
    label: "Marriage / Sacred Union",
    primary_house: 7,
    secondary_houses: [2, 11],
    default_offset_years: 27,
  },
  {
    id: "childbirth",
    label: "Childbirth / Progeny",
    primary_house: 5,
    secondary_houses: [2, 11],
    default_offset_years: 29,
  },
  {
    id: "property_vehicle",
    label: "Property / Vehicle Purchase",
    primary_house: 4,
    secondary_houses: [11, 12],
    default_offset_years: 28,
  },
  {
    id: "relocation_foreign",
    label: "Foreign Move / Relocation",
    primary_house: 12,
    secondary_houses: [3, 9],
    default_offset_years: 25,
  },
  {
    id: "accident_surgery",
    label: "Major Accident / Surgery",
    primary_house: 8,
    secondary_houses: [6, 12],
    default_offset_years: 24,
  },
  {
    id: "education_degree",
    label: "Higher Education Degree",
    primary_house: 9,
    secondary_houses: [4, 11],
    default_offset_years: 22,
  },
  {
    id: "lawsuit_dispute",
    label: "Lawsuit Victory / Decree",
    primary_house: 6,
    secondary_houses: [1, 11],
    default_offset_years: 31,
  },
];

export default function BirthTimeRectificationPage() {
  const { language } = useLanguage();
  const { session, isAuthenticated } = useAuth();

  // Mode: Saved chart vs manual entry
  const [inputMode, setInputMode] = useState<"saved" | "manual">("manual");
  const [savedHoroscopes, setSavedHoroscopes] = useState<SavedHoroItem[]>([]);
  const [loadingSavedList, setLoadingSavedList] = useState<boolean>(false);
  const [chartSearchQuery, setChartSearchQuery] = useState<string>("");
  const [selectedHoroscopeId, setSelectedHoroscopeId] = useState<string>("");

  // Form State
  const [personName, setPersonName] = useState<string>("Sample Client");
  const [birthDate, setBirthDate] = useState<string>("1995-10-24");
  const [birthTime, setBirthTime] = useState<string>("14:30:00");
  const [timezone, setTimezone] = useState<string>("Asia/Kolkata");
  const [latitude, setLatitude] = useState<number>(13.0827);
  const [longitude, setLongitude] = useState<number>(80.2707);
  const [locationName, setLocationName] = useState<string>("Chennai, India");

  // Rectification Scan Settings
  const [windowMinutes, setWindowMinutes] = useState<number>(30.0);
  const [stepMinutes, setStepMinutes] = useState<number>(1.0);
  const [refineSeconds, setRefineSeconds] = useState<boolean>(true);
  const [useRulingPlanets, setUseRulingPlanets] = useState<boolean>(true);
  const [siblingsCount, setSiblingsCount] = useState<number | "">("");

  // Events State
  const [events, setEvents] = useState<BtrLifeEventInput[]>([
    {
      label: "First Job Offer",
      event_date: "2018-06-15",
      primary_house: 10,
      secondary_houses: [2, 6, 11],
    },
    {
      label: "Marriage",
      event_date: "2022-11-20",
      primary_house: 7,
      secondary_houses: [2, 11],
    },
    {
      label: "Home / Flat Purchase",
      event_date: "2024-03-10",
      primary_house: 4,
      secondary_houses: [11, 12],
    },
  ]);

  // Loading & Results
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BtrResponse | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<BtrCandidateDetail | null>(null);
  const [candidateFilterQuery, setCandidateFilterQuery] = useState<string>("");

  // Fetch saved horoscopes if authenticated
  useEffect(() => {
    async function fetchSavedList() {
      if (!session?.access_token) return;
      setLoadingSavedList(true);
      try {
        const resp = await fetch("/api/horoscopes?limit=1000", {
          headers: {
            Authorization: `Bearer ${session.access_token}`,
          },
        });
        if (resp.ok) {
          const data = await resp.json();
          const items = data.horoscopes || [];
          setSavedHoroscopes(items);
          if (items.length > 0 && !selectedHoroscopeId) {
            setInputMode("saved");
            setSelectedHoroscopeId(items[0].id);
            applySelectedChart(items[0]);
          }
        }
      } catch (err) {
        console.warn("Could not load saved horoscopes:", err);
      } finally {
        setLoadingSavedList(false);
      }
    }

    if (isAuthenticated) {
      fetchSavedList();
    }
  }, [isAuthenticated, session?.access_token]);

  const applySelectedChart = (item: SavedHoroItem) => {
    setPersonName(item.person_name || "Client");
    setBirthDate(item.birth_date);
    setBirthTime(item.birth_time);
    setTimezone(item.timezone || "Asia/Kolkata");
    setLatitude(item.latitude);
    setLongitude(item.longitude);
    setLocationName(item.location_name || "");

    // Adjust event dates if they predate the selected birth date
    const birthYear = parseInt(item.birth_date.slice(0, 4), 10) || 1995;
    const adjustedEvents = events.map((ev, idx) => {
      const evYear = parseInt(ev.event_date.slice(0, 4), 10) || 2020;
      if (evYear <= birthYear) {
        const offset = CANONICAL_TEMPLATES[idx]?.default_offset_years || 25;
        return {
          ...ev,
          event_date: `${birthYear + offset}-05-15`,
        };
      }
      return ev;
    });
    setEvents(adjustedEvents);
  };

  const handleSelectSavedChart = (id: string) => {
    setSelectedHoroscopeId(id);
    const found = savedHoroscopes.find((h) => h.id === id);
    if (found) {
      applySelectedChart(found);
    }
  };

  // Quick Add Event Helper
  const addEventFromTemplate = (template: (typeof CANONICAL_TEMPLATES)[0]) => {
    const birthYear = parseInt(birthDate.slice(0, 4), 10) || 1995;
    const estYear = birthYear + template.default_offset_years;
    const newEv: BtrLifeEventInput = {
      label: template.label,
      event_date: `${estYear}-05-15`,
      primary_house: template.primary_house,
      secondary_houses: template.secondary_houses,
    };
    setEvents([...events, newEv]);
  };

  const removeEvent = (index: number) => {
    setEvents(events.filter((_, i) => i !== index));
  };

  const updateEvent = (index: number, field: keyof BtrLifeEventInput, value: any) => {
    const updated = [...events];
    updated[index] = { ...updated[index], [field]: value };
    setEvents(updated);
  };

  const handleRunRectification = async () => {
    if (events.length === 0) {
      setError(
        language === "ta"
          ? "குறைந்தது ஒரு கடந்த கால நிகழ்வை உள்ளிடவும்."
          : "Please enter at least 1 known life event (3-5 recommended)."
      );
      return;
    }

    // Client-side date check
    for (const ev of events) {
      if (ev.event_date <= birthDate) {
        setError(
          language === "ta"
            ? `நிகழ்வு '${ev.label}' பிறந்த தேதிக்கு (${birthDate}) பின்னரே இருக்க வேண்டும்.`
            : `Event '${ev.label}' date (${ev.event_date}) must be after the birth date (${birthDate}).`
        );
        return;
      }
    }

    setLoading(true);
    setError(null);

    try {
      const payload: BtrRequest = {
        birth_date: birthDate,
        birth_time: birthTime,
        timezone,
        latitude: Number(latitude),
        longitude: Number(longitude),
        events,
        window_minutes: Number(windowMinutes),
        step_minutes: Number(stepMinutes),
        refine_seconds: refineSeconds,
        use_ruling_planets: useRulingPlanets,
        siblings_count: siblingsCount === "" ? null : Number(siblingsCount),
        ayanamsa: 1, // KP
      };

      const res = await rectifyBirthTime(payload);
      setResult(res);
      setSelectedCandidate(res.best_candidate);
    } catch (err: any) {
      console.error("Rectification error:", err);
      setError(err?.detail || err?.message || "Birth time rectification failed.");
    } finally {
      setLoading(false);
    }
  };

  const filteredSavedCharts = savedHoroscopes.filter((h) => {
    if (!chartSearchQuery) return true;
    const q = chartSearchQuery.toLowerCase();
    return (
      (h.person_name && h.person_name.toLowerCase().includes(q)) ||
      (h.location_name && h.location_name.toLowerCase().includes(q)) ||
      (h.birth_date && h.birth_date.includes(q))
    );
  });

  const filteredCandidates = result
    ? result.top_candidates.filter((c) => {
        if (!candidateFilterQuery) return true;
        const q = candidateFilterQuery.toLowerCase();
        return (
          c.time_str.toLowerCase().includes(q) ||
          c.lsl.toLowerCase().includes(q) ||
          c.d9_sign.toLowerCase().includes(q) ||
          c.d60_sign.toLowerCase().includes(q)
        );
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
              { label: language === "ta" ? "உயர்நிலை கே.பி" : "Advanced KP", href: "/tools/advanced-kp" },
              { label: language === "ta" ? "பிறந்த நேர திருத்தம்" : "Birth Time Rectification" },
            ]}
          />

          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pt-2">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-400/20 border border-amber-300/30 text-amber-200 text-xs font-semibold mb-3">
                <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                <span>Accuracy Booster • KP & Parashari Engine</span>
              </div>
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-serif font-bold text-white tracking-tight">
                {language === "ta" ? "பிறந்த நேர திருத்த உதவியாளர் (BTR)" : "Birth Time Rectification (BTR) Assistant"}
              </h1>
              <p className="text-sm sm:text-base text-slate-200 mt-2 max-w-3xl leading-relaxed">
                {language === "ta"
                  ? "வெறும் 3 நிமிட பிழை கூட கே.பி உப-அதிபதிகள் (KP Sub-Lords), நவாம்சம் (D9) மற்றும் ஷஷ்டியாம்சம் (D60) லக்னங்களை முற்றிலும் மாற்றிவிடும். கடந்த கால முக்கிய வாழ்க்கை நிகழ்வுகளைக் கொண்டு வினாடித் துல்லியத்தில் சரியான பிறந்த நேரத்தைக் கண்டறியுங்கள்."
                  : "Even a 3-minute error shifts the KP sub-lords, D9 Navamsha lagna, and D60 Shashtiamsha. Cross-check your known life events against Dasa-Bhukti-Antara and KP Ruling Planets down to the exact second."}
              </p>
            </div>

            <div className="flex items-center gap-3">
              <Link
                href="/tools/double-transit"
                className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-xs font-medium text-white transition-all flex items-center gap-2"
              >
                <span>Double Transit Radar</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
              <Link
                href="/tools/kaksha-transit"
                className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-xs font-medium text-white transition-all flex items-center gap-2"
              >
                <span>Kaksha Alerts</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Form & Life Events */}
          <div className="lg:col-span-5 space-y-6">
            {/* Input Mode Selector */}
            {savedHoroscopes.length > 0 && (
              <div className="bg-white rounded-2xl p-4 shadow-xs border border-[#E2E8F0] flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setInputMode("saved")}
                  className={`flex-1 py-2 text-xs font-bold rounded-xl transition-all flex items-center justify-center gap-2 ${
                    inputMode === "saved"
                      ? "bg-[#102A4C] text-white shadow-xs"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  }`}
                >
                  <Database className="w-3.5 h-3.5" />
                  <span>{language === "ta" ? "சேமிக்கப்பட்ட ஜாதகம்" : "Saved Horoscope"}</span>
                </button>
                <button
                  type="button"
                  onClick={() => setInputMode("manual")}
                  className={`flex-1 py-2 text-xs font-bold rounded-xl transition-all flex items-center justify-center gap-2 ${
                    inputMode === "manual"
                      ? "bg-[#102A4C] text-white shadow-xs"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  }`}
                >
                  <User className="w-3.5 h-3.5" />
                  <span>{language === "ta" ? "புதிய உள்ளீடு" : "Manual Entry"}</span>
                </button>
              </div>
            )}

            {/* Saved Horoscope Search & Selector */}
            {inputMode === "saved" && savedHoroscopes.length > 0 && (
              <div className="bg-white rounded-2xl p-5 shadow-xs border border-[#E2E8F0] space-y-3">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold text-[#102A4C]">
                    {language === "ta" ? "ஜாதகரைத் தேர்ந்தெடுக்கவும்" : "Select Client Chart"}
                  </label>
                  <span className="text-[11px] font-mono text-[#64748B]">
                    {savedHoroscopes.length} saved
                  </span>
                </div>

                {/* Search Bar for Saved Charts */}
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

                <div className="max-h-44 overflow-y-auto space-y-1.5 pt-1">
                  {filteredSavedCharts.length === 0 ? (
                    <div className="p-3 text-center text-xs text-slate-400">
                      No saved horoscopes match &ldquo;{chartSearchQuery}&rdquo;
                    </div>
                  ) : (
                    filteredSavedCharts.map((h) => {
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
                    })
                  )}
                </div>
              </div>
            )}

            {/* Birth Details Card */}
            <div className="bg-white rounded-2xl p-6 shadow-xs border border-[#E2E8F0] space-y-4">
              <div className="flex items-center gap-2 pb-3 border-b border-[#F1F5F9]">
                <Clock className="w-5 h-5 text-[#102A4C]" />
                <h3 className="font-serif font-bold text-base text-[#102A4C]">
                  {language === "ta" ? "பதிவு செய்யப்பட்ட பிறந்த விவரங்கள்" : "Recorded Birth Information"}
                </h3>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#475569] mb-1">
                  {language === "ta" ? "பெயர்" : "Client / Profile Name"}
                </label>
                <input
                  type="text"
                  value={personName}
                  onChange={(e) => setPersonName(e.target.value)}
                  className="w-full text-xs font-medium px-3 py-2 border border-[#CBD5E1] rounded-lg outline-none"
                />
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
                    className="w-full text-xs font-mono px-3 py-2 border border-[#CBD5E1] rounded-lg focus:ring-2 focus:ring-[#102A4C] outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-[#475569] mb-1">
                    {language === "ta" ? "பதிவான நேரம் (தோராயமாக)" : "Approximate Time"}
                  </label>
                  <input
                    type="time"
                    step="1"
                    value={birthTime}
                    onChange={(e) => setBirthTime(e.target.value)}
                    className="w-full text-xs font-mono px-3 py-2 border border-[#CBD5E1] rounded-lg focus:ring-2 focus:ring-[#102A4C] outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="col-span-1">
                  <label className="block text-[11px] font-semibold text-[#475569] mb-1">Timezone</label>
                  <input
                    type="text"
                    value={timezone}
                    onChange={(e) => setTimezone(e.target.value)}
                    className="w-full text-xs font-mono px-2.5 py-2 border border-[#CBD5E1] rounded-lg"
                  />
                </div>
                <div className="col-span-1">
                  <label className="block text-[11px] font-semibold text-[#475569] mb-1">Latitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={latitude}
                    onChange={(e) => setLatitude(parseFloat(e.target.value))}
                    className="w-full text-xs font-mono px-2.5 py-2 border border-[#CBD5E1] rounded-lg"
                  />
                </div>
                <div className="col-span-1">
                  <label className="block text-[11px] font-semibold text-[#475569] mb-1">Longitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={longitude}
                    onChange={(e) => setLongitude(parseFloat(e.target.value))}
                    className="w-full text-xs font-mono px-2.5 py-2 border border-[#CBD5E1] rounded-lg"
                  />
                </div>
              </div>

              {/* Scan Tuning Options */}
              <div className="pt-3 border-t border-[#F1F5F9] space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-[#334155] flex items-center gap-1.5">
                    <Sliders className="w-3.5 h-3.5 text-[#102A4C]" />
                    <span>Search Window: ±{windowMinutes} mins</span>
                  </span>
                  <span className="text-xs font-mono text-[#64748B]">
                    {Math.round(windowMinutes * 2)} min span
                  </span>
                </div>
                <input
                  type="range"
                  min="5"
                  max="120"
                  step="5"
                  value={windowMinutes}
                  onChange={(e) => setWindowMinutes(parseFloat(e.target.value))}
                  className="w-full accent-[#102A4C]"
                />

                <div className="flex items-center justify-between text-xs pt-1">
                  <label className="flex items-center gap-2 cursor-pointer text-[#334155]">
                    <input
                      type="checkbox"
                      checked={refineSeconds}
                      onChange={(e) => setRefineSeconds(e.target.checked)}
                      className="rounded accent-[#102A4C]"
                    />
                    <span>Refine down to exact second</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer text-[#334155]">
                    <input
                      type="checkbox"
                      checked={useRulingPlanets}
                      onChange={(e) => setUseRulingPlanets(e.target.checked)}
                      className="rounded accent-[#102A4C]"
                    />
                    <span>KP Ruling Planets test</span>
                  </label>
                </div>
              </div>
            </div>

            {/* Life Events Input Card */}
            <div className="bg-white rounded-2xl p-6 shadow-xs border border-[#E2E8F0] space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-[#F1F5F9]">
                <div className="flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-[#8C6D23]" />
                  <h3 className="font-serif font-bold text-base text-[#102A4C]">
                    {language === "ta" ? "கடந்த கால வாழ்க்கை நிகழ்வுகள்" : "Known Life Events (3–5 recommended)"}
                  </h3>
                </div>
                <span className="px-2 py-0.5 rounded-full text-xs font-mono bg-amber-100 text-amber-800">
                  {events.length} entered
                </span>
              </div>

              {/* Quick Preset Buttons */}
              <div>
                <p className="text-xs text-[#64748B] mb-2 font-medium">
                  {language === "ta" ? "விரைவு நிகழ்வு வார்ப்புருக்கள்:" : "Quick Preset Templates:"}
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {CANONICAL_TEMPLATES.map((tmpl) => (
                    <button
                      key={tmpl.id}
                      type="button"
                      onClick={() => addEventFromTemplate(tmpl)}
                      className="px-2.5 py-1 text-[11px] rounded-lg bg-[#FAF7F0] hover:bg-[#F3EDE0] border border-[#E8DEC8] text-[#8C6D23] font-medium transition-colors flex items-center gap-1"
                    >
                      <Plus className="w-3 h-3" />
                      <span>{tmpl.label.split("/")[0]}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Event List */}
              <div className="space-y-3 pt-2">
                {events.map((ev, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-2 relative group hover:border-[#CBD5E1] transition-all"
                  >
                    <button
                      type="button"
                      onClick={() => removeEvent(idx)}
                      className="absolute top-2 right-2 p-1 text-slate-400 hover:text-rose-600 rounded-md transition-colors"
                      title="Remove event"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>

                    <div className="grid grid-cols-1 sm:grid-cols-12 gap-2.5 items-center pr-6">
                      <div className="sm:col-span-6">
                        <label className="block text-[10px] font-semibold text-[#64748B] uppercase">Event Description</label>
                        <input
                          type="text"
                          value={ev.label}
                          onChange={(e) => updateEvent(idx, "label", e.target.value)}
                          placeholder="e.g. Marriage, First Job"
                          className="w-full text-xs font-medium px-2.5 py-1.5 border border-[#CBD5E1] rounded-md bg-white outline-none"
                        />
                      </div>
                      <div className="sm:col-span-6">
                        <label className="block text-[10px] font-semibold text-[#64748B] uppercase">Event Date</label>
                        <input
                          type="date"
                          value={ev.event_date}
                          onChange={(e) => updateEvent(idx, "event_date", e.target.value)}
                          className="w-full text-xs font-mono px-2.5 py-1.5 border border-[#CBD5E1] rounded-md bg-white outline-none"
                        />
                      </div>
                    </div>

                    <div className="flex items-center gap-3 text-xs pt-1">
                      <div className="flex items-center gap-1.5">
                        <span className="text-[11px] text-[#64748B]">Primary House:</span>
                        <select
                          value={ev.primary_house}
                          onChange={(e) => updateEvent(idx, "primary_house", parseInt(e.target.value, 10))}
                          className="text-xs font-mono font-bold text-[#102A4C] border border-[#CBD5E1] rounded px-1.5 py-0.5 bg-white"
                        >
                          {Array.from({ length: 12 }, (_, i) => i + 1).map((h) => (
                            <option key={h} value={h}>House {h}</option>
                          ))}
                        </select>
                      </div>
                      <span className="text-[11px] text-[#94A3B8]">
                        Secondary: [{ev.secondary_houses.join(", ")}]
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Error Message */}
              {error && (
                <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              {/* Action Button */}
              <button
                type="button"
                onClick={handleRunRectification}
                disabled={loading}
                className="w-full py-3.5 px-4 rounded-xl bg-linear-to-r from-[#102A4C] to-[#153F6B] hover:from-[#0B1E38] hover:to-[#102A4C] text-white font-serif font-bold text-sm tracking-wide shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin text-amber-300" />
                    <span>Cross-Checking Dasa & KP Ruling Planets...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-amber-300" />
                    <span>Run High-Precision Rectification Scan</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Right Column: Rectification Results Dashboard */}
          <div className="lg:col-span-7 space-y-6">
            {!result ? (
              <div className="bg-white rounded-2xl p-12 text-center border border-[#E2E8F0] shadow-xs space-y-4">
                <div className="w-16 h-16 rounded-2xl bg-amber-50 border border-amber-200 text-[#8C6D23] flex items-center justify-center mx-auto">
                  <Clock className="w-8 h-8" />
                </div>
                <div className="max-w-md mx-auto space-y-2">
                  <h3 className="font-serif font-bold text-lg text-[#102A4C]">
                    {language === "ta" ? "பிறந்த நேர திருத்த பரிசோதனை தயார்" : "Ready for Rectification"}
                  </h3>
                  <p className="text-xs text-[#64748B] leading-relaxed">
                    {language === "ta"
                      ? "இடதுபுறத்தில் உங்கள் தோராயமான பிறந்த நேரம் மற்றும் 3-5 கடந்த கால நிகழ்வுகளை உள்ளிட்டு 'Run High-Precision Rectification Scan' பொத்தானைக் கிளிக் செய்யவும். இயந்திரம் ஒவ்வொரு வினாடியையும் சோதித்து சரியான நேரத்தைக் கணக்கிடும்."
                      : "Enter your approximate birth time and 3–5 dated life milestones on the left, then click 'Run High-Precision Rectification Scan'. The engine will simulate candidate birth moments down to the second, scoring each against the Lagna sub-lord and Vimshottari dasha running at each milestone."}
                  </p>
                </div>
              </div>
            ) : (
              <>
                {/* Hero Rectified Birth Time Card */}
                <div className="bg-linear-to-br from-[#102A4C] via-[#153F6B] to-[#1A365D] rounded-2xl p-6 sm:p-8 text-white shadow-lg border border-amber-400/30 space-y-6">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-5">
                    <div>
                      <span className="text-[11px] font-mono uppercase tracking-wider text-amber-300 font-semibold block">
                        Rectification Completed
                      </span>
                      <h2 className="text-xl sm:text-2xl font-serif font-bold text-white mt-1">
                        Exact Rectified Birth Time
                      </h2>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-400/30 text-emerald-300 font-mono text-xs font-bold flex items-center gap-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                        <span>{result.best_candidate.confidence_percentage}% Confidence</span>
                      </span>
                    </div>
                  </div>

                  {/* Big Digital Clock Display */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 items-center text-center sm:text-left">
                    <div>
                      <span className="text-xs text-slate-300 block mb-1">Rectified Local Clock:</span>
                      <div className="text-3xl sm:text-4xl font-mono font-extrabold text-amber-300 tracking-wider">
                        {result.rectified_time}
                      </div>
                      <span className="text-[11px] text-slate-300 font-mono mt-1 block">
                        Shift: {result.offset_formatted}
                      </span>
                    </div>

                    <div>
                      <span className="text-xs text-slate-300 block mb-1">Lagna Sub-Lord (LSL):</span>
                      <div className="text-2xl sm:text-3xl font-serif font-bold text-white">
                        {result.rectified_lsl}
                      </div>
                      <span className="text-[11px] text-emerald-300 mt-1 block">
                        Signifies {result.best_candidate.events.filter(e => e.lsl_hit).length}/{result.best_candidate.events.length} milestone houses
                      </span>
                    </div>

                    <div>
                      <span className="text-xs text-slate-300 block mb-1">Posterior Mass Band:</span>
                      <div className="text-sm font-mono font-bold text-slate-100">
                        {result.credible_interval.start_time} – {result.credible_interval.end_time}
                      </div>
                      <span className="text-[11px] text-slate-300 mt-1 block">
                        {result.credible_interval.posterior_mass_percentage}% mass within {result.credible_interval.spread_minutes}m spread
                      </span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-200 bg-white/5 p-3.5 rounded-xl border border-white/10 leading-relaxed font-sans">
                    {result.astrological_verdict}
                  </p>
                </div>

                {/* Varga Shift Comparison: D1 Sub-Lord, D9 Navamsha, D60 Shashtiamsha */}
                <div className="bg-white rounded-2xl p-6 shadow-xs border border-[#E2E8F0] space-y-4">
                  <div className="flex items-center justify-between pb-3 border-b border-[#F1F5F9]">
                    <div className="flex items-center gap-2">
                      <Layers className="w-5 h-5 text-[#102A4C]" />
                      <h3 className="font-serif font-bold text-base text-[#102A4C]">
                        Critical Lagna Shift Breakdown (Approx vs Rectified)
                      </h3>
                    </div>
                    <span className="text-xs text-[#64748B]">Impact on Key Vargas</span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    {/* KP Lagna Sub-Lord */}
                    <div className={`p-4 rounded-xl border ${result.shift_comparison.lsl_changed ? "bg-amber-50/60 border-amber-300" : "bg-slate-50 border-slate-200"}`}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-bold text-[#102A4C]">KP Lagna Sub-Lord</span>
                        {result.shift_comparison.lsl_changed && (
                          <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-200 text-amber-900">
                            SHIFTED
                          </span>
                        )}
                      </div>
                      <div className="space-y-1 text-xs">
                        <div className="flex justify-between text-[#64748B]">
                          <span>Recorded:</span>
                          <span className="font-mono font-semibold">{result.shift_comparison.approx_lsl}</span>
                        </div>
                        <div className="flex justify-between text-[#102A4C] font-bold">
                          <span>Rectified:</span>
                          <span className="font-mono text-amber-800">{result.shift_comparison.rectified_lsl}</span>
                        </div>
                      </div>
                    </div>

                    {/* D9 Navamsha Lagna */}
                    <div className={`p-4 rounded-xl border ${result.shift_comparison.d9_changed ? "bg-indigo-50/60 border-indigo-300" : "bg-slate-50 border-slate-200"}`}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-bold text-[#102A4C]">D9 Navamsha Lagna</span>
                        {result.shift_comparison.d9_changed && (
                          <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-indigo-200 text-indigo-900">
                            SHIFTED
                          </span>
                        )}
                      </div>
                      <div className="space-y-1 text-xs">
                        <div className="flex justify-between text-[#64748B]">
                          <span>Recorded:</span>
                          <span className="font-semibold">{result.shift_comparison.approx_d9.sign_name}</span>
                        </div>
                        <div className="flex justify-between text-[#102A4C] font-bold">
                          <span>Rectified:</span>
                          <span className="text-indigo-900">{result.shift_comparison.rectified_d9.sign_name}</span>
                        </div>
                        <span className="text-[10px] text-slate-500 block">
                          {result.shift_comparison.rectified_d9.division_specific}
                        </span>
                      </div>
                    </div>

                    {/* D60 Shashtiamsha Lagna */}
                    <div className={`p-4 rounded-xl border ${result.shift_comparison.d60_changed ? "bg-rose-50/60 border-rose-300" : "bg-slate-50 border-slate-200"}`}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-bold text-[#102A4C]">D60 Shashtiamsha</span>
                        {result.shift_comparison.d60_changed && (
                          <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-rose-200 text-rose-900">
                            SHIFTED
                          </span>
                        )}
                      </div>
                      <div className="space-y-1 text-xs">
                        <div className="flex justify-between text-[#64748B]">
                          <span>Recorded:</span>
                          <span className="font-semibold">{result.shift_comparison.approx_d60.sign_name}</span>
                        </div>
                        <div className="flex justify-between text-[#102A4C] font-bold">
                          <span>Rectified:</span>
                          <span className="text-rose-900">{result.shift_comparison.rectified_d60.sign_name}</span>
                        </div>
                        <span className="text-[10px] text-slate-500 block truncate" title={result.shift_comparison.rectified_d60.division_specific || ""}>
                          {result.shift_comparison.rectified_d60.division_specific}
                        </span>
                      </div>
                    </div>
                  </div>

                  <p className="text-xs text-[#475569] leading-relaxed bg-[#F8FAFC] p-3 rounded-lg border border-[#E2E8F0]">
                    {result.shift_comparison.explanation}
                  </p>
                </div>

                {/* Event-by-Event Verification Breakdown */}
                <div className="bg-white rounded-2xl p-6 shadow-xs border border-[#E2E8F0] space-y-4">
                  <div className="flex items-center justify-between pb-3 border-b border-[#F1F5F9]">
                    <div className="flex items-center gap-2">
                      <ShieldCheck className="w-5 h-5 text-emerald-600" />
                      <h3 className="font-serif font-bold text-base text-[#102A4C]">
                        Milestone Verification Against Rectified Time
                      </h3>
                    </div>
                    {result.transit_confirmation && (
                      <span className="text-xs font-mono text-[#64748B]">
                        Transit Match: {result.transit_confirmation.match_percentage}%
                      </span>
                    )}
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left border-collapse">
                      <thead>
                        <tr className="bg-[#FAF7F0] text-[#8C6D23] font-bold border-b border-[#E8DEC8]">
                          <th className="py-2.5 px-3">Event Milestone</th>
                          <th className="py-2.5 px-2">Date</th>
                          <th className="py-2.5 px-2">Houses</th>
                          <th className="py-2.5 px-2">LSL Match</th>
                          <th className="py-2.5 px-2">MD Lord</th>
                          <th className="py-2.5 px-2">AD Lord</th>
                          <th className="py-2.5 px-2">PD Lord</th>
                          <th className="py-2.5 px-2 text-center">Dasa Hit</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#334155]">
                        {result.best_candidate.events.map((es, idx) => (
                          <tr key={idx} className="hover:bg-[#FAF6EC]/40 transition-colors">
                            <td className="py-2.5 px-3 font-semibold text-[#102A4C]">{es.label}</td>
                            <td className="py-2.5 px-2 font-mono text-[#64748B]">{es.event_date}</td>
                            <td className="py-2.5 px-2 font-mono">
                              House {es.primary_house}
                              {es.secondary_houses.length > 0 && ` (${es.secondary_houses.join(",")})`}
                            </td>
                            <td className="py-2.5 px-2">
                              {es.lsl_hit ? (
                                <span className="inline-flex items-center gap-1 text-emerald-700 font-bold">
                                  <CheckCircle2 className="w-3.5 h-3.5" /> Hit (+{es.lsl_score})
                                </span>
                              ) : (
                                <span className="text-slate-400">Miss</span>
                              )}
                            </td>
                            <td className="py-2.5 px-2 font-serif font-bold text-[#102A4C]">{es.mahadasha_lord}</td>
                            <td className="py-2.5 px-2 font-serif text-[#102A4C]">{es.antardasha_lord}</td>
                            <td className="py-2.5 px-2 font-serif text-[#64748B]">{es.pratyantardasha_lord}</td>
                            <td className="py-2.5 px-2 text-center">
                              {es.dasha_hit ? (
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                                  Confirmed
                                </span>
                              ) : (
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800">
                                  Partial
                                </span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Top Candidates Ranked Grid with Filter */}
                <div className="bg-white rounded-2xl p-6 shadow-xs border border-[#E2E8F0] space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#F1F5F9]">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="w-5 h-5 text-[#102A4C]" />
                      <h3 className="font-serif font-bold text-base text-[#102A4C]">
                        Top Scored Candidate Times ({result.total_candidates_evaluated} Tested)
                      </h3>
                    </div>

                    {/* Candidate Search / Filter */}
                    <div className="relative">
                      <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                      <input
                        type="text"
                        value={candidateFilterQuery}
                        onChange={(e) => setCandidateFilterQuery(e.target.value)}
                        placeholder="Filter by LSL, time, D9..."
                        className="text-xs pl-8 pr-2.5 py-1 border border-[#CBD5E1] rounded-lg outline-none bg-[#F8FAFC]"
                      />
                    </div>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left border-collapse">
                      <thead>
                        <tr className="bg-[#FAF7F0] text-[#8C6D23] font-bold border-b border-[#E8DEC8]">
                          <th className="py-2.5 px-3">#</th>
                          <th className="py-2.5 px-2">Local Time</th>
                          <th className="py-2.5 px-2">Offset</th>
                          <th className="py-2.5 px-2">LSL</th>
                          <th className="py-2.5 px-2">D9</th>
                          <th className="py-2.5 px-2">D60</th>
                          <th className="py-2.5 px-2">LSL Pts</th>
                          <th className="py-2.5 px-2">Dasa Pts</th>
                          <th className="py-2.5 px-2 text-right">Confidence</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#334155]">
                        {filteredCandidates.length === 0 ? (
                          <tr>
                            <td colSpan={9} className="py-6 text-center text-[#64748B]">
                              No candidates match &ldquo;{candidateFilterQuery}&rdquo;
                            </td>
                          </tr>
                        ) : (
                          filteredCandidates.map((cand, idx) => (
                            <tr
                              key={idx}
                              onClick={() => setSelectedCandidate(cand)}
                              className={`cursor-pointer transition-colors ${
                                selectedCandidate?.time_str === cand.time_str
                                  ? "bg-amber-100/60 font-semibold"
                                  : "hover:bg-[#FAF6EC]/30"
                              }`}
                            >
                              <td className="py-2.5 px-3 text-[#64748B]">#{idx + 1}</td>
                              <td className="py-2.5 px-2 font-mono font-bold text-[#102A4C]">{cand.time_str}</td>
                              <td className="py-2.5 px-2 font-mono text-slate-600">{cand.offset_formatted}</td>
                              <td className="py-2.5 px-2 font-serif text-[#102A4C]">{cand.lsl}</td>
                              <td className="py-2.5 px-2 text-slate-600">{cand.d9_sign}</td>
                              <td className="py-2.5 px-2 text-slate-600">{cand.d60_sign}</td>
                              <td className="py-2.5 px-2 font-mono">{cand.lsl_score}</td>
                              <td className="py-2.5 px-2 font-mono">{cand.dasha_score}</td>
                              <td className="py-2.5 px-2 text-right font-mono font-bold text-emerald-700">
                                {cand.confidence_percentage}%
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
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
