"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { useLanguage } from "@/lib/i18n";
import { analyzeVehicleNumerology, saveNumerologyReport } from "@/lib/api";
import {
  VehicleNumerologyResponse,
  VehicleCandidateResult,
  VehicleOwnerInput,
} from "@/lib/types";
import {
  Car,
  Truck,
  Shield,
  Sparkles,
  Users,
  User,
  Plus,
  Trash2,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Bookmark,
  Scale,
  Award,
  Layers,
  ShieldCheck,
  Zap,
  Flame,
  BarChart3,
  Sliders,
  Compass,
} from "lucide-react";

const USAGE_OPTIONS = [
  {
    value: "personal",
    labelEn: "Personal & Commute",
    labelTa: "தனிநபர் & அன்றாடப் பயணம்",
    ruler: "Sun (1), Venus (6), Mercury (5)",
    desc: "Leadership presence, driving comfort, agility, and aesthetic pride.",
    icon: Car,
  },
  {
    value: "family",
    labelEn: "Family & Household",
    labelTa: "குடும்பம் & சுற்றுப்பயணம்",
    ruler: "Moon (2), Jupiter (3), Venus (6)",
    desc: "Passenger harmony, peaceful journeys, safety mindfulness, and shared comfort.",
    icon: Users,
  },
  {
    value: "commercial",
    labelEn: "Commercial & Taxi",
    labelTa: "வணிகம் & வாடகை ஊர்தி",
    ruler: "Mercury (5), Sun (1), Saturn (8)",
    desc: "Punctuality, active client transit, rapid turnaround, and revenue generation.",
    icon: Compass,
  },
  {
    value: "fleet",
    labelEn: "Heavy Fleet & Transport",
    labelTa: "சரக்கு & கனரகப் போக்குவரத்து",
    ruler: "Saturn (8), Mars (9), Sun (1)",
    desc: "Mechanical durability, long-haul stamina, multi-driver discipline, and payload endurance.",
    icon: Truck,
  },
] as const;

const SAMPLE_PLATES = [
  { plate: "TN 09 AB 1234", label: "Tamil Nadu Standard" },
  { plate: "MH 12 CD 5678", label: "Maharashtra Classic" },
  { plate: "DL 3C AB 1234", label: "Delhi Alphanumeric RTO" },
  { plate: "KA 01 MG 9999", label: "Karnataka VIP Quad" },
  { plate: "22 BH 1234 AA", label: "Bharat (BH) Series" },
];

export function VehicleNumberStudio() {
  const { language } = useLanguage();
  const { session, isAuthenticated } = useAuth();

  // Primary Inputs
  const [registrationNumber, setRegistrationNumber] = useState("TN 09 AB 1234");
  const [systemConvention, setSystemConvention] = useState<"pythagorean" | "chaldean">("chaldean");
  const [calculationMode, setCalculationMode] = useState<"digits_only" | "numeric_all" | "full_alphanumeric">("digits_only");
  const [vehicleUsage, setVehicleUsage] = useState<"personal" | "family" | "commercial" | "fleet">("personal");
  const [primaryBirthDate, setPrimaryBirthDate] = useState("1994-06-15");
  const [primaryOwnerName, setPrimaryOwnerName] = useState("Gokul");
  const [reportLang, setReportLang] = useState<"en" | "ta">("en");

  // Co-Owners / Co-Drivers
  const [coOwners, setCoOwners] = useState<VehicleOwnerInput[]>([]);
  const [showAddCoOwner, setShowAddCoOwner] = useState(false);
  const [newCoName, setNewCoName] = useState("");
  const [newCoDob, setNewCoDob] = useState("");
  const [newCoRole, setNewCoRole] = useState("Co-Driver");

  // Candidate Plates
  const [candidatePlates, setCandidatePlates] = useState<string[]>([
    "TN 09 AB 9999",
    "MH 12 CD 0007",
    "DL 3C AB 1221",
  ]);
  const [newCandidateInput, setNewCandidateInput] = useState("");

  // Results & UI State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<VehicleNumerologyResponse | null>(null);
  const [expandedCandidate, setExpandedCandidate] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<"composite" | "vanity" | "root">("composite");
  const [savedSuccessMsg, setSavedSuccessMsg] = useState<string | null>(null);
  const [savingReport, setSavingReport] = useState(false);
  const [showMethodology, setShowMethodology] = useState(false);

  // Auto-run on mount for instant visual preview
  useEffect(() => {
    handleRunStudio();
  }, []);

  const handleRunStudio = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!registrationNumber.trim()) {
      setError(language === "ta" ? "வாகன பதிவு எண்ணை உள்ளிடுக." : "Please enter a valid registration number.");
      return;
    }

    setLoading(true);
    setError(null);
    setSavedSuccessMsg(null);

    try {
      const response = await analyzeVehicleNumerology({
        registration_number: registrationNumber.trim(),
        system_convention: systemConvention,
        calculation_mode: calculationMode,
        vehicle_usage: vehicleUsage,
        primary_birth_date: primaryBirthDate.trim() || undefined,
        primary_owner_name: primaryOwnerName.trim() || undefined,
        co_owners: coOwners,
        candidate_numbers: candidatePlates.filter((c) => c.trim()),
        language: reportLang,
      });

      setResult(response);
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || "Failed to analyze vehicle registration number.");
    } finally {
      setLoading(false);
    }
  };

  // Co-driver management
  const addCoOwner = () => {
    if (newCoName.trim() && newCoDob.trim()) {
      setCoOwners([
        ...coOwners,
        {
          name: newCoName.trim(),
          birth_date: newCoDob.trim(),
          role: newCoRole.trim() || "Co-Driver",
          is_primary: false,
        },
      ]);
      setNewCoName("");
      setNewCoDob("");
      setShowAddCoOwner(false);
    }
  };

  const removeCoOwner = (idx: number) => {
    setCoOwners(coOwners.filter((_, i) => i !== idx));
  };

  // Candidate management
  const addCandidate = () => {
    if (newCandidateInput.trim() && !candidatePlates.includes(newCandidateInput.trim())) {
      setCandidatePlates([...candidatePlates, newCandidateInput.trim()]);
      setNewCandidateInput("");
    }
  };

  const removeCandidate = (plate: string) => {
    setCandidatePlates(candidatePlates.filter((c) => c !== plate));
  };

  // Save report to Supabase
  const handleSaveReport = async () => {
    if (!session?.access_token || !result) return;
    setSavingReport(true);
    try {
      await saveNumerologyReport(
        {
          person_name: primaryOwnerName.trim() || result.formatted_registration,
          birth_date: primaryBirthDate.trim() || "2000-01-01",
          method: "vehicle",
          system_convention: systemConvention,
          calculation_data: {
            raw_input: result.raw_input,
            formatted_registration: result.formatted_registration,
            state_code: result.state_code,
            state_name: result.state_name,
            rto_code: result.rto_code,
            series_letters: result.series_letters,
            numeric_digits: result.numeric_digits,
            calculation_mode: result.calculation_mode,
            vehicle_usage: result.vehicle_usage,
            primary_analysis: result.primary_analysis,
            vanity_score: result.vanity_score,
            patterns: result.patterns,
          },
          interpretation_data: {
            usage_alignment: result.usage_alignment,
            owner_alignments: result.owner_alignments,
            overall_owner_score: result.overall_owner_score,
            disclaimer: result.disclaimer,
          },
        },
        session.access_token
      );
      setSavedSuccessMsg(
        language === "ta"
          ? "வாகன எண் அறிக்கை வெற்றிகரமாகச் சேமிக்கப்பட்டது!"
          : "Vehicle numerology report saved successfully to your cloud profile!"
      );
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || "Failed to save vehicle report.");
    } finally {
      setSavingReport(false);
    }
  };

  // Candidate sorting
  const sortedCandidates = result?.candidates
    ? [...result.candidates].sort((a, b) => {
        if (sortBy === "composite") return b.composite_score - a.composite_score;
        if (sortBy === "vanity") return b.vanity_score - a.vanity_score;
        if (sortBy === "root") return a.root_number - b.root_number;
        return 0;
      })
    : [];

  return (
    <div className="space-y-8 w-full py-6">
      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-amber-600 via-orange-600 to-amber-700 p-8 text-white shadow-xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-white/20 backdrop-blur-sm border border-white/30 text-amber-100">
                <Car className="w-3.5 h-3.5" />
                {language === "ta" ? "வாகன & சொத்து எண் கணிதம்" : "Vehicle & Asset Registration Numerology"}
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-xs bg-black/20 text-amber-200">
                Phase 5 Production
              </span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
              {language === "ta"
                ? "வாகன எண் அதிர்வு & உரிமைப் பொருத்தம்"
                : "Vehicle Plate Vibration & Driver Resonance Studio"}
            </h1>
            <p className="mt-2 text-sm sm:text-base text-amber-100/90 max-w-3xl">
              {language === "ta"
                ? "இந்திய மோட்டார் வாகனப் பதிவு எண்களைப் பிரித்து ஆராய்ந்து, ஓட்டுநர் பிறந்த தேதியுடன் பாரம்பரிய கிரகப் பொருத்தத்தைக் காண்க."
                : "Analyze Indian motor vehicle registration plates (TN, MH, DL, KA, BH series) across numeric and full alphanumeric traditions, evaluate VIP vanity patterns, and align with driver astrology."}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={() => setShowMethodology(!showMethodology)}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/20 text-xs font-medium text-white transition-all shadow-sm"
            >
              <HelpCircle className="w-4 h-4" />
              {language === "ta" ? "விதிகள் & கணக்கீட்டு முறை" : "Calculation Methods"}
            </button>
          </div>
        </div>

        <div className="absolute -right-8 -bottom-8 opacity-10 pointer-events-none">
          <Car className="w-64 h-64 text-white" />
        </div>
      </div>

      {/* Methodology Collapsible */}
      {showMethodology && (
        <div className="rounded-2xl border border-amber-500/20 bg-amber-500/5 dark:bg-amber-950/20 p-6 space-y-4 text-sm text-foreground">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-base flex items-center gap-2 text-amber-600 dark:text-amber-400">
              <Sliders className="w-5 h-5" />
              {language === "ta" ? "வாகன எண் கணித மரபு விதிகள்" : "Vehicle Numerology Conventions & Plate Rules"}
            </h3>
            <button
              onClick={() => setShowMethodology(false)}
              className="text-xs text-muted-foreground hover:text-foreground"
            >
              Close
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-card border border-border">
              <span className="font-semibold text-primary block mb-1">1. Numeric Digits Only (Standard)</span>
              <p className="text-xs text-muted-foreground">
                In classical Indian vehicle numerology, the vehicle is primarily known by its 4-digit unique registration number (e.g. 1234 in TN 09 AB 1234 = 1+2+3+4 = 10 -&gt; 1).
              </p>
            </div>
            <div className="p-4 rounded-xl bg-card border border-border">
              <span className="font-semibold text-primary block mb-1">2. Numeric All (RTO + Digits)</span>
              <p className="text-xs text-muted-foreground">
                Sums the district RTO numeric code with the vehicle number (e.g. 09 + 1234 = 19 -&gt; 1) to incorporate the vehicle's geographic origin.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-card border border-border">
              <span className="font-semibold text-primary block mb-1">3. Full Alphanumeric Plate</span>
              <p className="text-xs text-muted-foreground">
                Converts state code and series letters via Chaldean (1-8) or Pythagorean (1-9) mappings combined with digits for full vehicle vibrational synthesis.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Main Form & Configuration */}
      <form onSubmit={handleRunStudio} className="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left: Plate Number & Calculation Mode */}
          <div className="lg:col-span-6 space-y-4">
            <div>
              <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                {language === "ta" ? "வாகன பதிவு எண்" : "Registration Plate Number"}
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={registrationNumber}
                  onChange={(e) => setRegistrationNumber(e.target.value.toUpperCase())}
                  placeholder="e.g. TN 09 AB 1234"
                  className="w-full px-4 py-3 rounded-xl border border-input bg-background text-foreground text-lg font-mono font-bold tracking-wider uppercase focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
                <span className="absolute right-3 top-3.5 text-xs text-muted-foreground font-sans">
                  India / Global
                </span>
              </div>
            </div>

            {/* Quick Plate Samples */}
            <div>
              <span className="text-xs text-muted-foreground block mb-1.5">
                {language === "ta" ? "விரைவு மாதிரி எண்கள்:" : "Quick Samples:"}
              </span>
              <div className="flex flex-wrap gap-2">
                {SAMPLE_PLATES.map((sp) => (
                  <button
                    key={sp.plate}
                    type="button"
                    onClick={() => setRegistrationNumber(sp.plate)}
                    className="px-2.5 py-1 rounded-lg text-xs bg-muted/70 hover:bg-muted border border-border font-mono transition-colors"
                  >
                    {sp.plate}
                  </button>
                ))}
              </div>
            </div>

            {/* Calculation Mode Selector */}
            <div className="space-y-2 pt-2">
              <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                {language === "ta" ? "கணக்கீட்டு முறை" : "Calculation Mode"}
              </label>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => setCalculationMode("digits_only")}
                  className={`p-2.5 rounded-xl text-xs font-medium border text-center transition-all ${
                    calculationMode === "digits_only"
                      ? "bg-amber-600 text-white border-amber-600 shadow-sm"
                      : "bg-muted/40 hover:bg-muted border-border text-foreground"
                  }`}
                >
                  <span className="font-bold block">Digits Only</span>
                  <span className="text-[10px] opacity-80">e.g. 1234</span>
                </button>
                <button
                  type="button"
                  onClick={() => setCalculationMode("numeric_all")}
                  className={`p-2.5 rounded-xl text-xs font-medium border text-center transition-all ${
                    calculationMode === "numeric_all"
                      ? "bg-amber-600 text-white border-amber-600 shadow-sm"
                      : "bg-muted/40 hover:bg-muted border-border text-foreground"
                  }`}
                >
                  <span className="font-bold block">Numeric All</span>
                  <span className="text-[10px] opacity-80">RTO + Digits</span>
                </button>
                <button
                  type="button"
                  onClick={() => setCalculationMode("full_alphanumeric")}
                  className={`p-2.5 rounded-xl text-xs font-medium border text-center transition-all ${
                    calculationMode === "full_alphanumeric"
                      ? "bg-amber-600 text-white border-amber-600 shadow-sm"
                      : "bg-muted/40 hover:bg-muted border-border text-foreground"
                  }`}
                >
                  <span className="font-bold block">Full Plate</span>
                  <span className="text-[10px] opacity-80">State+RTO+Series</span>
                </button>
              </div>
            </div>
          </div>

          {/* Right: Convention, Vehicle Use, Primary Driver */}
          <div className="lg:col-span-6 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                  {language === "ta" ? "எண் கணித மரபு" : "Alphabet System"}
                </label>
                <select
                  value={systemConvention}
                  onChange={(e) => setSystemConvention(e.target.value as any)}
                  className="w-full px-3 py-2.5 rounded-xl border border-input bg-background text-sm font-medium focus:ring-2 focus:ring-amber-500"
                >
                  <option value="chaldean">Chaldean (1-8 Ancient Vedic)</option>
                  <option value="pythagorean">Pythagorean (1-9 Western Standard)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                  {language === "ta" ? "வாகன பயன்பாட்டு வகை" : "Vehicle Usage"}
                </label>
                <select
                  value={vehicleUsage}
                  onChange={(e) => setVehicleUsage(e.target.value as any)}
                  className="w-full px-3 py-2.5 rounded-xl border border-input bg-background text-sm font-medium focus:ring-2 focus:ring-amber-500"
                >
                  {USAGE_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {language === "ta" ? opt.labelTa : opt.labelEn}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                  {language === "ta" ? "உரிமையாளர் பெயர்" : "Primary Owner Name"}
                </label>
                <input
                  type="text"
                  value={primaryOwnerName}
                  onChange={(e) => setPrimaryOwnerName(e.target.value)}
                  placeholder="e.g. Gokul"
                  className="w-full px-3 py-2.5 rounded-xl border border-input bg-background text-sm focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                  {language === "ta" ? "பிறந்த தேதி (YYYY-MM-DD)" : "Owner Birth Date (DOB)"}
                </label>
                <input
                  type="date"
                  value={primaryBirthDate}
                  onChange={(e) => setPrimaryBirthDate(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl border border-input bg-background text-sm focus:ring-2 focus:ring-amber-500"
                />
              </div>
            </div>

            {/* Language & Action */}
            <div className="flex items-center justify-between pt-2">
              <div className="flex items-center gap-3">
                <span className="text-xs text-muted-foreground">Language:</span>
                <button
                  type="button"
                  onClick={() => setReportLang("en")}
                  className={`px-2.5 py-1 rounded-lg text-xs font-medium border ${
                    reportLang === "en" ? "bg-amber-600 text-white border-amber-600" : "bg-muted border-border"
                  }`}
                >
                  English
                </button>
                <button
                  type="button"
                  onClick={() => setReportLang("ta")}
                  className={`px-2.5 py-1 rounded-lg text-xs font-medium border ${
                    reportLang === "ta" ? "bg-amber-600 text-white border-amber-600" : "bg-muted border-border"
                  }`}
                >
                  தமிழ்
                </button>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-semibold text-sm shadow-md transition-all disabled:opacity-50"
              >
                {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                {language === "ta" ? "ஆய்வு செய்க" : "Analyze Plate"}
              </button>
            </div>
          </div>
        </div>

        {/* Collapsible Co-Drivers / Co-Owners */}
        <div className="border-t border-border pt-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
              <Users className="w-3.5 h-3.5" />
              {language === "ta" ? "கூடுதல் ஓட்டுநர்கள் / குடும்பத்தினர்" : "Co-Drivers / Family Users (Optional)"}
              {coOwners.length > 0 && ` (${coOwners.length})`}
            </span>
            <button
              type="button"
              onClick={() => setShowAddCoOwner(!showAddCoOwner)}
              className="text-xs text-amber-600 hover:text-amber-500 font-medium inline-flex items-center gap-1"
            >
              <Plus className="w-3.5 h-3.5" />
              {language === "ta" ? "ஓட்டுநர் சேர்க்க" : "Add Co-Driver"}
            </button>
          </div>

          {coOwners.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3">
              {coOwners.map((co, idx) => (
                <div
                  key={idx}
                  className="inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-muted text-xs border border-border"
                >
                  <User className="w-3 h-3 text-muted-foreground" />
                  <span className="font-semibold">{co.name}</span>
                  <span className="text-muted-foreground font-mono">({co.birth_date})</span>
                  <span className="text-muted-foreground">[{co.role}]</span>
                  <button
                    type="button"
                    onClick={() => removeCoOwner(idx)}
                    className="text-red-500 hover:text-red-400 ml-1"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          )}

          {showAddCoOwner && (
            <div className="p-4 rounded-xl bg-muted/40 border border-border grid grid-cols-1 sm:grid-cols-4 gap-3 items-end">
              <div>
                <label className="text-[11px] text-muted-foreground block mb-1">Name</label>
                <input
                  type="text"
                  value={newCoName}
                  onChange={(e) => setNewCoName(e.target.value)}
                  placeholder="e.g. Spouse / Driver"
                  className="w-full px-3 py-1.5 rounded-lg border border-input bg-background text-xs"
                />
              </div>
              <div>
                <label className="text-[11px] text-muted-foreground block mb-1">Birth Date (YYYY-MM-DD)</label>
                <input
                  type="date"
                  value={newCoDob}
                  onChange={(e) => setNewCoDob(e.target.value)}
                  className="w-full px-3 py-1.5 rounded-lg border border-input bg-background text-xs"
                />
              </div>
              <div>
                <label className="text-[11px] text-muted-foreground block mb-1">Role</label>
                <input
                  type="text"
                  value={newCoRole}
                  onChange={(e) => setNewCoRole(e.target.value)}
                  placeholder="e.g. Co-Driver"
                  className="w-full px-3 py-1.5 rounded-lg border border-input bg-background text-xs"
                />
              </div>
              <div>
                <button
                  type="button"
                  onClick={addCoOwner}
                  className="w-full px-3 py-2 rounded-lg bg-amber-600 text-white text-xs font-semibold hover:bg-amber-500 transition-colors"
                >
                  Confirm Driver
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Candidate Numbers for Comparison */}
        <div className="border-t border-border pt-4">
          <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
            {language === "ta" ? "ஒப்பீட்டு வாகன எண்கள் (Fancy / Auction Candidates)" : "Compare Alternative Plates (Fancy / Auction Selection)"}
          </label>
          <div className="flex flex-wrap gap-2 mb-3">
            {candidatePlates.map((c) => (
              <span
                key={c}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-muted text-xs font-mono font-bold border border-border"
              >
                {c}
                <button
                  type="button"
                  onClick={() => removeCandidate(c)}
                  className="text-muted-foreground hover:text-red-500"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
          <div className="flex gap-2 max-w-md">
            <input
              type="text"
              value={newCandidateInput}
              onChange={(e) => setNewCandidateInput(e.target.value.toUpperCase())}
              placeholder="e.g. KA 01 MG 9999"
              className="flex-1 px-3 py-1.5 rounded-lg border border-input bg-background text-xs font-mono uppercase"
            />
            <button
              type="button"
              onClick={addCandidate}
              className="px-3 py-1.5 rounded-lg bg-muted hover:bg-muted/80 text-xs font-medium border border-border inline-flex items-center gap-1"
            >
              <Plus className="w-3 h-3" />
              Add Candidate
            </button>
          </div>
        </div>
      </form>

      {/* Error Banner */}
      {error && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-600 dark:text-red-400 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Save Report Banner */}
      {savedSuccessMsg && (
        <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-4 text-sm text-emerald-600 dark:text-emerald-400 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
          <span>{savedSuccessMsg}</span>
        </div>
      )}

      {/* Analysis Results View */}
      {result && (
        <div className="space-y-8">
          {/* Section 1: Plate Classification & Primary Vibrational Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left: Plate Structure Breakdown Badge */}
            <div className="lg:col-span-5 rounded-2xl border border-border bg-card p-6 space-y-5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                  Plate Decomposition
                </span>
                <span
                  className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                    result.is_valid_indian_format
                      ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20"
                      : "bg-amber-500/10 text-amber-600 border border-amber-500/20"
                  }`}
                >
                  {result.plate_classification}
                </span>
              </div>

              {/* Graphic License Plate Badge */}
              <div className="p-4 rounded-xl border-2 border-slate-700 bg-gradient-to-b from-white to-slate-100 dark:from-slate-900 dark:to-slate-950 text-slate-900 dark:text-white shadow-md flex items-center justify-between gap-4 font-mono font-extrabold tracking-widest text-2xl sm:text-3xl">
                <div className="flex flex-col items-center justify-center border-r-2 border-slate-300 dark:border-slate-700 pr-3">
                  <span className="text-[10px] font-sans font-bold text-blue-600">IND</span>
                  <span className="text-xs">🇮🇳</span>
                </div>
                <div className="flex-1 text-center">
                  {result.formatted_registration}
                </div>
              </div>

              {/* Component breakdown table */}
              <div className="grid grid-cols-4 gap-2 text-center text-xs">
                <div className="p-2.5 rounded-xl bg-muted/50 border border-border">
                  <span className="text-muted-foreground block text-[10px] uppercase">State</span>
                  <span className="font-bold text-primary text-sm font-mono">{result.state_code || "--"}</span>
                  <span className="text-[9px] text-muted-foreground block truncate">{result.state_name || "N/A"}</span>
                </div>
                <div className="p-2.5 rounded-xl bg-muted/50 border border-border">
                  <span className="text-muted-foreground block text-[10px] uppercase">RTO Code</span>
                  <span className="font-bold text-primary text-sm font-mono">{result.rto_code || "--"}</span>
                  <span className="text-[9px] text-muted-foreground block">District</span>
                </div>
                <div className="p-2.5 rounded-xl bg-muted/50 border border-border">
                  <span className="text-muted-foreground block text-[10px] uppercase">Series</span>
                  <span className="font-bold text-primary text-sm font-mono">{result.series_letters || "--"}</span>
                  <span className="text-[9px] text-muted-foreground block">Running</span>
                </div>
                <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20">
                  <span className="text-amber-600 dark:text-amber-400 block text-[10px] uppercase font-bold">Number</span>
                  <span className="font-extrabold text-amber-600 dark:text-amber-400 text-sm font-mono">{result.numeric_digits}</span>
                  <span className="text-[9px] text-muted-foreground block">Primary Digits</span>
                </div>
              </div>

              {/* Vanity Score Bar */}
              <div className="p-4 rounded-xl bg-muted/30 border border-border space-y-2">
                <div className="flex items-center justify-between text-xs font-semibold">
                  <span className="flex items-center gap-1.5">
                    <Award className="w-3.5 h-3.5 text-amber-500" />
                    Vanity / Memorability Rating
                  </span>
                  <span className="font-bold text-amber-600 dark:text-amber-400">
                    {result.vanity_score}/100
                  </span>
                </div>
                <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
                  <div
                    className="h-2 rounded-full bg-gradient-to-r from-amber-500 to-orange-500 transition-all duration-500"
                    style={{ width: `${result.vanity_score}%` }}
                  />
                </div>
                <div className="flex items-center justify-between text-[11px] text-muted-foreground">
                  <span>{result.patterns.pattern_classification}</span>
                  <span className="flex gap-1">
                    {result.patterns.pattern_tags.map((tag, i) => (
                      <span key={i} className="px-1.5 py-0.5 rounded bg-muted text-[10px]">
                        {tag}
                      </span>
                    ))}
                  </span>
                </div>
              </div>
            </div>

            {/* Right: Primary Numerical Vibration & Transparent Reduction */}
            <div className="lg:col-span-7 rounded-2xl border border-border bg-card p-6 space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border pb-4">
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                    Active Mode: {result.primary_analysis.mode_label}
                  </span>
                  <h3 className="text-2xl font-bold flex items-center gap-2 mt-1">
                    <span className="inline-flex items-center justify-center w-10 h-10 rounded-xl bg-amber-600 text-white font-extrabold text-xl shadow-md">
                      {result.primary_analysis.root_number}
                    </span>
                    <span>{result.primary_analysis.keyword}</span>
                  </h3>
                </div>

                <div className="text-right">
                  <span className="text-xs text-muted-foreground block">Ruling Planet</span>
                  <span className="font-semibold text-amber-600 dark:text-amber-400 text-sm">
                    {result.primary_analysis.ruling_planet}
                  </span>
                </div>
              </div>

              {/* Transparent Reduction Steps */}
              <div className="space-y-2">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block">
                  Step-by-Step Reduction Formula
                </span>
                <div className="p-3.5 rounded-xl bg-muted/50 border border-border font-mono text-xs space-y-1.5">
                  {result.primary_analysis.reduction_steps.map((st, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <span className="text-muted-foreground select-none">[{i + 1}]</span>
                      <span className={i === result.primary_analysis.reduction_steps.length - 1 ? "font-bold text-amber-600 dark:text-amber-400" : ""}>
                        {st}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Vibrational Meaning */}
              <div className="space-y-1.5">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block">
                  Vibrational & Journey Archetype
                </span>
                <p className="text-sm text-foreground/90 leading-relaxed bg-amber-500/5 dark:bg-amber-950/20 p-4 rounded-xl border border-amber-500/20">
                  {result.primary_analysis.vibrational_meaning}
                </p>
              </div>

              {/* 3 Modes Side-by-Side Comparison */}
              <div className="grid grid-cols-3 gap-3 pt-2">
                <div className={`p-3 rounded-xl border text-center transition-all ${
                  result.calculation_mode === "digits_only" ? "border-amber-600 bg-amber-500/10" : "border-border bg-muted/30"
                }`}>
                  <span className="text-[10px] text-muted-foreground uppercase block font-semibold">Digits Only</span>
                  <span className="text-lg font-bold font-mono">{result.digits_only_analysis.root_number}</span>
                  <span className="text-[10px] text-muted-foreground block font-mono">Sum: {result.digits_only_analysis.compound_sum}</span>
                </div>
                <div className={`p-3 rounded-xl border text-center transition-all ${
                  result.calculation_mode === "numeric_all" ? "border-amber-600 bg-amber-500/10" : "border-border bg-muted/30"
                }`}>
                  <span className="text-[10px] text-muted-foreground uppercase block font-semibold">Numeric All</span>
                  <span className="text-lg font-bold font-mono">{result.numeric_all_analysis.root_number}</span>
                  <span className="text-[10px] text-muted-foreground block font-mono">Sum: {result.numeric_all_analysis.compound_sum}</span>
                </div>
                <div className={`p-3 rounded-xl border text-center transition-all ${
                  result.calculation_mode === "full_alphanumeric" ? "border-amber-600 bg-amber-500/10" : "border-border bg-muted/30"
                }`}>
                  <span className="text-[10px] text-muted-foreground uppercase block font-semibold">Full Plate</span>
                  <span className="text-lg font-bold font-mono">{result.full_alphanumeric_analysis.root_number}</span>
                  <span className="text-[10px] text-muted-foreground block font-mono">Sum: {result.full_alphanumeric_analysis.compound_sum}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Section 2: Usage Harmony & Driver Alignment */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Vehicle Usage Alignment */}
            <div className="lg:col-span-5 rounded-2xl border border-border bg-card p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="font-bold text-base flex items-center gap-2">
                  <Car className="w-4 h-4 text-amber-500" />
                  Vehicle Usage Compatibility
                </h4>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/10 text-amber-600 border border-amber-500/20">
                  {result.usage_alignment.score}% Match
                </span>
              </div>

              <div className="p-4 rounded-xl bg-muted/40 border border-border space-y-2">
                <span className="font-semibold text-sm block">{result.usage_alignment.usage_name}</span>
                <span className="text-xs text-muted-foreground block">
                  <strong>Planetary Archetypes:</strong> {result.usage_alignment.planetary_rulers}
                </span>
                <span className="text-xs text-muted-foreground block">
                  <strong>Resonant Numbers:</strong> {result.usage_alignment.primary_numbers.join(", ")}
                </span>
                <p className="text-xs text-foreground/80 mt-2">
                  {result.usage_alignment.description}
                </p>
              </div>
            </div>

            {/* Owner & Driver Alignments */}
            <div className="lg:col-span-7 rounded-2xl border border-border bg-card p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="font-bold text-base flex items-center gap-2">
                  <User className="w-4 h-4 text-amber-500" />
                  Driver & Owner Astrology Compatibility
                </h4>
                {result.overall_owner_score !== null && (
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-600 border border-emerald-500/20">
                    Overall Synergy: {result.overall_owner_score}%
                  </span>
                )}
              </div>

              {result.owner_alignments.length > 0 ? (
                <div className="space-y-3">
                  {result.owner_alignments.map((owner, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-xl bg-muted/40 border border-border space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-sm">{owner.name}</span>
                          <span className="text-[10px] px-2 py-0.5 rounded bg-muted text-muted-foreground">
                            {owner.role}
                          </span>
                        </div>
                        <span className="text-xs font-bold text-amber-600 dark:text-amber-400">
                          {owner.level} ({owner.personal_score}%)
                        </span>
                      </div>
                      <div className="flex gap-4 text-xs text-muted-foreground">
                        <span>Psychic Number: <strong>{owner.psychic_number}</strong></span>
                        <span>Life Path: <strong>{owner.life_path_number}</strong></span>
                        <span>DOB: <strong className="font-mono">{owner.birth_date}</strong></span>
                      </div>
                      <p className="text-xs text-foreground/80">
                        {owner.synthesis}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-muted-foreground p-4 bg-muted/30 rounded-xl">
                  Enter an owner birth date above to view personal planetary compatibility with this vehicle registration.
                </p>
              )}
            </div>
          </div>

          {/* Section 3: Candidate Plates Comparison & Ranking */}
          {sortedCandidates.length > 0 && (
            <div className="rounded-2xl border border-border bg-card p-6 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <h4 className="font-bold text-lg flex items-center gap-2">
                    <Scale className="w-5 h-5 text-amber-500" />
                    Alternative Candidate Plates Ranking (SIM / VIP Auction)
                  </h4>
                  <p className="text-xs text-muted-foreground">
                    Ranked by composite score (Vanity / Memorability + Usage Alignment + Owner Resonance)
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">Sort By:</span>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as any)}
                    className="px-3 py-1.5 rounded-lg border border-input bg-background text-xs font-medium"
                  >
                    <option value="composite">Composite Score</option>
                    <option value="vanity">Vanity Rating</option>
                    <option value="root">Root Number</option>
                  </select>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-border text-muted-foreground uppercase tracking-wider text-[10px]">
                      <th className="py-3 px-3">Rank</th>
                      <th className="py-3 px-3">Plate Number</th>
                      <th className="py-3 px-3">Type</th>
                      <th className="py-3 px-3">Root</th>
                      <th className="py-3 px-3">Sum</th>
                      <th className="py-3 px-3">Vanity</th>
                      <th className="py-3 px-3">Owner Score</th>
                      <th className="py-3 px-3">Composite</th>
                      <th className="py-3 px-3">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {sortedCandidates.map((cand, idx) => (
                      <React.Fragment key={cand.raw_input}>
                        <tr className="hover:bg-muted/30 transition-colors">
                          <td className="py-3 px-3 font-bold text-muted-foreground">
                            #{idx + 1}
                          </td>
                          <td className="py-3 px-3 font-mono font-bold text-sm">
                            {cand.normalized_registration}
                          </td>
                          <td className="py-3 px-3 text-muted-foreground">
                            {cand.plate_classification}
                          </td>
                          <td className="py-3 px-3 font-bold text-primary font-mono text-sm">
                            {cand.root_number}
                          </td>
                          <td className="py-3 px-3 text-muted-foreground font-mono">
                            {cand.compound_sum}
                          </td>
                          <td className="py-3 px-3 font-semibold text-amber-600 dark:text-amber-400">
                            {cand.vanity_score}%
                          </td>
                          <td className="py-3 px-3 font-semibold">
                            {cand.owner_score !== null ? `${cand.owner_score}%` : "--"}
                          </td>
                          <td className="py-3 px-3 font-extrabold text-sm text-emerald-600 dark:text-emerald-400">
                            {cand.composite_score}%
                          </td>
                          <td className="py-3 px-3">
                            <button
                              type="button"
                              onClick={() =>
                                setExpandedCandidate(
                                  expandedCandidate === cand.raw_input ? null : cand.raw_input
                                )
                              }
                              className="text-xs text-amber-600 hover:text-amber-500 font-medium inline-flex items-center gap-1"
                            >
                              {expandedCandidate === cand.raw_input ? (
                                <>
                                  Hide <ChevronUp className="w-3.5 h-3.5" />
                                </>
                              ) : (
                                <>
                                  Details <ChevronDown className="w-3.5 h-3.5" />
                                </>
                              )}
                            </button>
                          </td>
                        </tr>

                        {expandedCandidate === cand.raw_input && (
                          <tr className="bg-muted/20">
                            <td colSpan={9} className="p-4 space-y-2 text-xs">
                              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                                <div className="p-3 rounded-lg bg-card border border-border">
                                  <span className="font-semibold block mb-1">Patterns Detected:</span>
                                  <span className="text-muted-foreground">
                                    {cand.patterns.details}
                                  </span>
                                </div>
                                <div className="p-3 rounded-lg bg-card border border-border">
                                  <span className="font-semibold block mb-1">Reduction Steps:</span>
                                  <span className="font-mono text-muted-foreground">
                                    {cand.reduction_steps.join(" -> ")}
                                  </span>
                                </div>
                                <div className="p-3 rounded-lg bg-card border border-border">
                                  <span className="font-semibold block mb-1">Usage Match:</span>
                                  <span className="text-muted-foreground">
                                    Score: {cand.usage_score ?? "--"}%
                                  </span>
                                </div>
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Section 4: Persistence Actions & Disclaimer */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-6 rounded-2xl border border-border bg-card">
            <div>
              <span className="text-sm font-semibold block">
                {language === "ta" ? "அறிக்கையைப் பாதுகாத்தல்" : "Save Analysis to Profile"}
              </span>
              <span className="text-xs text-muted-foreground">
                {isAuthenticated
                  ? "Store this vehicle analysis report permanently with your saved charts."
                  : "Sign in to save this report to your profile."}
              </span>
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={handleSaveReport}
                disabled={!isAuthenticated || savingReport}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-semibold text-xs shadow-sm transition-all disabled:opacity-50"
              >
                {savingReport ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Bookmark className="w-3.5 h-3.5" />}
                {language === "ta" ? "அறிக்கையைச் சேமிக்க" : "Save Report"}
              </button>
            </div>
          </div>

          {/* Legal / Ethical Disclaimer */}
          <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 dark:bg-amber-950/20 p-4 text-xs text-muted-foreground leading-relaxed flex items-start gap-2.5">
            <Shield className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
            <div>
              <strong className="text-foreground block mb-0.5">Disclaimer & Advisory Notice:</strong>
              {result.disclaimer}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
