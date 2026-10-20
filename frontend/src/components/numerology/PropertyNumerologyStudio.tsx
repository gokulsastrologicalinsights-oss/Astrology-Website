"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { useLanguage } from "@/lib/i18n";
import { analyzePropertyNumerology, saveNumerologyReport } from "@/lib/api";
import {
  PropertyNumerologyResponse,
  PropertyCandidateResult,
  PropertyResidentInput,
} from "@/lib/types";
import {
  Home,
  Building,
  Building2,
  Compass,
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
  Shield,
  MapPin,
} from "lucide-react";

const CATEGORY_OPTIONS = [
  { value: "apartment_flat", labelEn: "Apartment / Flat", labelTa: "அடுக்குமாடி குடியிருப்பு / பிளாட்" },
  { value: "independent_house", labelEn: "Independent House / Villa", labelTa: "தனி வீடு / வில்லா" },
  { value: "commercial_office", labelEn: "Commercial Office / Suite", labelTa: "வணிக அலுவலகம்" },
  { value: "commercial_shop", labelEn: "Retail Shop / Showroom", labelTa: "சில்லறை கடை / வணிக அங்காடி" },
  { value: "plot_land", labelEn: "Plot / Land / Site", labelTa: "மனை / காலி நிலம்" },
  { value: "multi_unit", labelEn: "Multi-Unit / Duplex", labelTa: "பல குடும்பக் கட்டிடம்" },
] as const;

const USAGE_OPTIONS = [
  {
    value: "residential_living",
    labelEn: "Residential & Family Living",
    labelTa: "குடும்ப வாழ்விடம்",
    ruler: "Venus (6), Moon (2), Jupiter (3)",
    desc: "Tranquil family harmony, health, peaceful sleep, and loving domestic life.",
  },
  {
    value: "commercial_business",
    labelEn: "Commercial Office & Business",
    labelTa: "வணிக அலுவலகம்",
    ruler: "Sun (1), Mercury (5), Saturn (8)",
    desc: "Executive deals, commercial revenue, client flow, and enterprise growth.",
  },
  {
    value: "rental_investment",
    labelEn: "Rental & Investment Yield",
    labelTa: "வாடகை முதலீடு",
    ruler: "Saturn (8), Venus (6), Rahu (4)",
    desc: "Consistent rental yield, tenant longevity, and solid capital appreciation.",
  },
  {
    value: "creative_studio",
    labelEn: "Creative Studio & Innovation",
    labelTa: "படைப்பாற்றல் அரங்கம்",
    ruler: "Jupiter (3), Mercury (5), Sun (1)",
    desc: "Artistic production, digital innovation, writing, and expressive flow.",
  },
  {
    value: "spiritual_wellness",
    labelEn: "Spiritual Haven & Wellness",
    labelTa: "ஆன்மீக மையம் & நல்வாழ்வு",
    ruler: "Ketu (7), Mars/Jupiter (9/3), Moon (2)",
    desc: "Meditation sanctuary, yoga healing, deep study, and restful retreat.",
  },
] as const;

const DIRECTION_OPTIONS = [
  { value: "North", label: "North (Kubera / Wealth)" },
  { value: "North-East", label: "North-East (Ishanya / Supreme Grace)" },
  { value: "East", label: "East (Surya / Vitality & Honor)" },
  { value: "South-East", label: "South-East (Agni / Creative Energy)" },
  { value: "South", label: "South (Yama / Order & Rest)" },
  { value: "South-West", label: "South-West (Nairrutya / Master Stability)" },
  { value: "West", label: "West (Varuna / Material Gains)" },
  { value: "North-West", label: "North-West (Vayu / Movement & Transition)" },
];

const SAMPLE_PROPERTIES = [
  { door: "4B", bldg: "Tower 3", floor: "4", name: "Lotus Greens", dir: "North-East", label: "Lotus Greens 4B (NE)" },
  { door: "102", bldg: "Building A", floor: "1", name: "Prestige City", dir: "East", label: "Prestige 102 (East)" },
  { door: "12", bldg: "", floor: "", plot: "42", name: "Vasant Vihar Villa", dir: "North", label: "Vasant Vihar Villa 12 (North)" },
];

export function PropertyNumerologyStudio() {
  const { language } = useLanguage();
  const { session, isAuthenticated } = useAuth();

  // Primary Inputs
  const [propertyCategory, setPropertyCategory] = useState<string>("apartment_flat");
  const [tenureType, setTenureType] = useState<"purchased" | "rental">("purchased");
  const [doorFlatNumber, setDoorFlatNumber] = useState("4B");
  const [buildingNumber, setBuildingNumber] = useState("Tower 3");
  const [blockOrWing, setBlockOrWing] = useState("Wing A");
  const [floorNumber, setFloorNumber] = useState("4");
  const [plotNumber, setPlotNumber] = useState("");
  const [buildingName, setBuildingName] = useState("Lotus Greens");
  const [facingDirection, setFacingDirection] = useState("North-East");
  const [propertyUsage, setPropertyUsage] = useState<string>("residential_living");
  const [systemConvention, setSystemConvention] = useState<"pythagorean" | "chaldean">("chaldean");
  const [calculationMode, setCalculationMode] = useState<string>("door_number");

  // Resident Alignment
  const [primaryOwnerName, setPrimaryOwnerName] = useState("Gokul");
  const [primaryBirthDate, setPrimaryBirthDate] = useState("1994-06-15");
  const [coResidents, setCoResidents] = useState<PropertyResidentInput[]>([]);
  const [showAddCoResident, setShowAddCoResident] = useState(false);
  const [newResName, setNewResName] = useState("");
  const [newResDob, setNewResDob] = useState("");
  const [newResRole, setNewResRole] = useState("Spouse");

  // Candidates for Comparison
  const [candidatesList, setCandidatesList] = useState<Array<{ door: string; name: string; floor?: string }>>([
    { door: "102", name: "Skyline Heights", floor: "1" },
    { door: "504", name: "Royal Residency", floor: "5" },
    { door: "701", name: "Grand Vista", floor: "7" },
  ]);
  const [newCandDoor, setNewCandDoor] = useState("");
  const [newCandName, setNewCandName] = useState("");

  // Results & UI State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PropertyNumerologyResponse | null>(null);
  const [expandedCandidate, setExpandedCandidate] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<"composite" | "usage" | "root">("composite");
  const [savedSuccessMsg, setSavedSuccessMsg] = useState<string | null>(null);
  const [savingReport, setSavingReport] = useState(false);
  const [showMethodology, setShowMethodology] = useState(false);
  const [reportLang, setReportLang] = useState<"en" | "ta">("en");

  // Auto-run on mount
  useEffect(() => {
    handleRunStudio();
  }, []);

  const handleRunStudio = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!doorFlatNumber.trim() && !buildingNumber.trim() && !plotNumber.trim() && !buildingName.trim()) {
      setError(language === "ta" ? "குறைந்தது ஒரு சொத்து எண்ணை உள்ளிடுக." : "Please enter at least a door, building, plot, or society name.");
      return;
    }

    setLoading(true);
    setError(null);
    setSavedSuccessMsg(null);

    try {
      const candidatesPayload = candidatesList.map((c) => ({
        door_flat_number: c.door,
        building_name: c.name,
        floor_number: c.floor,
        label: `${c.door} ${c.name}`.trim(),
      }));

      const response = await analyzePropertyNumerology({
        property_category: propertyCategory as any,
        tenure_type: tenureType,
        door_flat_number: doorFlatNumber.trim() || undefined,
        building_number: buildingNumber.trim() || undefined,
        block_or_wing: blockOrWing.trim() || undefined,
        floor_number: floorNumber.trim() || undefined,
        plot_number: plotNumber.trim() || undefined,
        building_name: buildingName.trim() || undefined,
        facing_direction: facingDirection || undefined,
        property_usage: propertyUsage as any,
        system_convention: systemConvention,
        calculation_mode: calculationMode as any,
        primary_birth_date: primaryBirthDate.trim() || undefined,
        primary_owner_name: primaryOwnerName.trim() || undefined,
        co_residents: coResidents,
        candidate_properties: candidatesPayload,
        language: reportLang,
      });

      setResult(response);
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || "Failed to analyze property numerology.");
    } finally {
      setLoading(false);
    }
  };

  // Co-resident management
  const addCoResident = () => {
    if (newResName.trim() && newResDob.trim()) {
      setCoResidents([
        ...coResidents,
        {
          name: newResName.trim(),
          birth_date: newResDob.trim(),
          role: newResRole.trim() || "Resident",
          is_primary: false,
        },
      ]);
      setNewResName("");
      setNewResDob("");
      setShowAddCoResident(false);
    }
  };

  const removeCoResident = (idx: number) => {
    setCoResidents(coResidents.filter((_, i) => i !== idx));
  };

  // Candidate management
  const addCandidate = () => {
    if (newCandDoor.trim() || newCandName.trim()) {
      setCandidatesList([
        ...candidatesList,
        {
          door: newCandDoor.trim(),
          name: newCandName.trim(),
        },
      ]);
      setNewCandDoor("");
      setNewCandName("");
    }
  };

  const removeCandidate = (idx: number) => {
    setCandidatesList(candidatesList.filter((_, i) => i !== idx));
  };

  // Save report to Supabase
  const handleSaveReport = async () => {
    if (!session?.access_token || !result) return;
    setSavingReport(true);
    try {
      await saveNumerologyReport(
        {
          person_name: primaryOwnerName.trim() || result.full_identifier || "Property Analysis",
          birth_date: primaryBirthDate.trim() || "2000-01-01",
          method: "property",
          system_convention: systemConvention,
          calculation_data: {
            property_category: result.property_category,
            tenure_type: result.tenure_type,
            door_flat_number: result.door_flat_number,
            building_number: result.building_number,
            block_or_wing: result.block_or_wing,
            floor_number: result.floor_number,
            plot_number: result.plot_number,
            building_name: result.building_name,
            facing_direction: result.facing_direction,
            full_identifier: result.full_identifier,
            calculation_mode: result.calculation_mode,
            property_usage: result.property_usage,
            primary_analysis: result.primary_analysis,
            combined_analysis: result.combined_analysis,
          },
          interpretation_data: {
            usage_alignment: result.usage_alignment,
            vastu_alignment: result.vastu_alignment,
            resident_alignments: result.resident_alignments,
            overall_household_score: result.overall_household_score,
            disclaimer: result.disclaimer,
          },
        },
        session.access_token
      );
      setSavedSuccessMsg(
        language === "ta"
          ? "சொத்து எண் கணித அறிக்கை வெற்றிகரமாகச் சேமிக்கப்பட்டது!"
          : "Property numerology report saved successfully to your cloud profile!"
      );
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || "Failed to save property report.");
    } finally {
      setSavingReport(false);
    }
  };

  const sortedCandidates = result?.candidates
    ? [...result.candidates].sort((a, b) => {
        if (sortBy === "composite") return b.composite_score - a.composite_score;
        if (sortBy === "usage") return b.usage_score - a.usage_score;
        if (sortBy === "root") return a.root_number - b.root_number;
        return 0;
      })
    : [];

  return (
    <div className="space-y-8 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-emerald-700 via-teal-700 to-emerald-800 p-8 text-white shadow-xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-white/20 backdrop-blur-sm border border-white/30 text-emerald-100">
                <Home className="w-3.5 h-3.5" />
                {language === "ta" ? "மனை, வீடு & சொத்து எண் கணிதம்" : "House, Flat & Property Numerology Studio"}
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-xs bg-black/20 text-emerald-200">
                Phase 6 Production
              </span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
              {language === "ta"
                ? "மனை, பிளாட் & கட்டிட எண் அதிர்வு அரங்கம்"
                : "House, Flat & Architectural Vibration Studio"}
            </h1>
            <p className="mt-2 text-sm sm:text-base text-emerald-100/90 max-w-3xl">
              {language === "ta"
                ? "கதவு எண், மாடி, கட்டிடம் மற்றும் மனை எண்களை தனித்தனியாகவும் ஒருங்கிணைத்தும் ஆராய்ந்து, வாஸ்து திசை மற்றும் குடும்ப பிறந்த எண்களுடன் ஒப்பிடுங்கள்."
                : "Calculate separate and combined vibrations for door/flat number, floor, building shell, and plot, evaluate classical Vastu directional harmony, and align with family astrology."}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={() => setShowMethodology(!showMethodology)}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/20 text-xs font-medium text-white transition-all shadow-sm"
            >
              <HelpCircle className="w-4 h-4" />
              {language === "ta" ? "கணக்கீட்டு விதிகள்" : "Formulas & Rules"}
            </button>
          </div>
        </div>

        <div className="absolute -right-8 -bottom-8 opacity-10 pointer-events-none">
          <Building2 className="w-64 h-64 text-white" />
        </div>
      </div>

      {/* Methodology Collapsible */}
      {showMethodology && (
        <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 dark:bg-emerald-950/20 p-6 space-y-4 text-sm text-foreground">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-base flex items-center gap-2 text-emerald-600 dark:text-emerald-400">
              <Sliders className="w-5 h-5" />
              {language === "ta" ? "சொத்து எண் கணித முறைமை" : "Property Numerology Conventions & Formulas"}
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
              <span className="font-semibold text-primary block mb-1">1. Door / Flat Number (Micro Threshold)</span>
              <p className="text-xs text-muted-foreground">
                In classical property numerology, the door number (e.g. 4B = 4+2 = 6 in Chaldean) governs the immediate intimate daily vibration of the occupants inside the dwelling.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-card border border-border">
              <span className="font-semibold text-primary block mb-1">2. Combined Property Formula</span>
              <p className="text-xs text-muted-foreground">
                Synthesizes all active architectural levels: Door Compound + Floor Compound + Building Compound + Plot Compound into a single master dwelling total.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-card border border-border">
              <span className="font-semibold text-primary block mb-1">3. Vastu Shastra Integration</span>
              <p className="text-xs text-muted-foreground">
                Maps 8 cardinal &amp; intercardinal directions to traditional presiding deities (Kubera, Ishanya, Surya, Agni, Yama, Nirriti, Varuna, Vayu) and elements without mixing formulas.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Configuration & Inputs Form */}
      <form onSubmit={handleRunStudio} className="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Property Type, Numbers & Identifiers */}
          <div className="lg:col-span-7 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                  {language === "ta" ? "சொத்து வகை" : "Property Category"}
                </label>
                <select
                  value={propertyCategory}
                  onChange={(e) => setPropertyCategory(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl border border-input bg-background text-sm font-medium focus:ring-2 focus:ring-emerald-500"
                >
                  {CATEGORY_OPTIONS.map((c) => (
                    <option key={c.value} value={c.value}>
                      {language === "ta" ? c.labelTa : c.labelEn}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                  {language === "ta" ? "உரிமை வகை" : "Tenure Type"}
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setTenureType("purchased")}
                    className={`py-2 px-3 rounded-xl text-xs font-semibold border transition-all ${
                      tenureType === "purchased"
                        ? "bg-emerald-600 text-white border-emerald-600 shadow-sm"
                        : "bg-muted/40 border-border text-foreground hover:bg-muted"
                    }`}
                  >
                    Purchased / Owned
                  </button>
                  <button
                    type="button"
                    onClick={() => setTenureType("rental")}
                    className={`py-2 px-3 rounded-xl text-xs font-semibold border transition-all ${
                      tenureType === "rental"
                        ? "bg-emerald-600 text-white border-emerald-600 shadow-sm"
                        : "bg-muted/40 border-border text-foreground hover:bg-muted"
                    }`}
                  >
                    Rented / Leased
                  </button>
                </div>
              </div>
            </div>

            {/* Micro Numbers Input Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div>
                <label className="text-[11px] font-semibold text-muted-foreground uppercase block mb-1">
                  Door / Flat No.
                </label>
                <input
                  type="text"
                  value={doorFlatNumber}
                  onChange={(e) => setDoorFlatNumber(e.target.value)}
                  placeholder="e.g. 4B, 102"
                  className="w-full px-3 py-2 rounded-xl border border-input bg-background font-mono font-bold text-sm"
                />
              </div>

              <div>
                <label className="text-[11px] font-semibold text-muted-foreground uppercase block mb-1">
                  Floor No.
                </label>
                <input
                  type="text"
                  value={floorNumber}
                  onChange={(e) => setFloorNumber(e.target.value)}
                  placeholder="e.g. 4, 12, G"
                  className="w-full px-3 py-2 rounded-xl border border-input bg-background font-mono font-bold text-sm"
                />
              </div>

              <div>
                <label className="text-[11px] font-semibold text-muted-foreground uppercase block mb-1">
                  Building / Tower
                </label>
                <input
                  type="text"
                  value={buildingNumber}
                  onChange={(e) => setBuildingNumber(e.target.value)}
                  placeholder="e.g. Tower 3"
                  className="w-full px-3 py-2 rounded-xl border border-input bg-background font-mono text-sm"
                />
              </div>

              <div>
                <label className="text-[11px] font-semibold text-muted-foreground uppercase block mb-1">
                  Plot / Site No.
                </label>
                <input
                  type="text"
                  value={plotNumber}
                  onChange={(e) => setPlotNumber(e.target.value)}
                  placeholder="e.g. 42"
                  className="w-full px-3 py-2 rounded-xl border border-input bg-background font-mono text-sm"
                />
              </div>
            </div>

            {/* Building Name & Wing */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="sm:col-span-2">
                <label className="text-[11px] font-semibold text-muted-foreground uppercase block mb-1">
                  Project / Society / Building Name
                </label>
                <input
                  type="text"
                  value={buildingName}
                  onChange={(e) => setBuildingName(e.target.value)}
                  placeholder="e.g. Lotus Greens, Prestige City"
                  className="w-full px-3 py-2 rounded-xl border border-input bg-background text-sm"
                />
              </div>

              <div>
                <label className="text-[11px] font-semibold text-muted-foreground uppercase block mb-1">
                  Block or Wing
                </label>
                <input
                  type="text"
                  value={blockOrWing}
                  onChange={(e) => setBlockOrWing(e.target.value)}
                  placeholder="e.g. Wing A"
                  className="w-full px-3 py-2 rounded-xl border border-input bg-background text-sm"
                />
              </div>
            </div>

            {/* Quick Samples */}
            <div>
              <span className="text-[11px] text-muted-foreground block mb-1">Quick Samples:</span>
              <div className="flex flex-wrap gap-2">
                {SAMPLE_PROPERTIES.map((sp, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => {
                      setDoorFlatNumber(sp.door);
                      setBuildingNumber(sp.bldg);
                      setFloorNumber(sp.floor);
                      setPlotNumber(sp.plot || "");
                      setBuildingName(sp.name);
                      setFacingDirection(sp.dir);
                    }}
                    className="px-2.5 py-1 rounded-lg text-xs bg-muted/60 hover:bg-muted border border-border text-foreground transition-colors"
                  >
                    {sp.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Calculation Mode Selector */}
            <div className="space-y-2 pt-2">
              <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                {language === "ta" ? "முதன்மை கணக்கீட்டு முறை" : "Primary Calculation Mode"}
              </label>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { id: "door_number", label: "Door / Flat No.", sub: "Standard Micro" },
                  { id: "combined_property", label: "Combined Formula", sub: "Door+Floor+Bldg" },
                  { id: "floor_number", label: "Floor Level", sub: "Elevation" },
                  { id: "building_number", label: "Building / Tower", sub: "Macro Shell" },
                  { id: "plot_number", label: "Plot / Cadastral", sub: "Land Grounding" },
                  { id: "full_alphanumeric", label: "Full Identifier", sub: "Name + Number" },
                ].map((mode) => (
                  <button
                    key={mode.id}
                    type="button"
                    onClick={() => setCalculationMode(mode.id)}
                    className={`p-2 rounded-xl text-xs font-medium border text-center transition-all ${
                      calculationMode === mode.id
                        ? "bg-emerald-600 text-white border-emerald-600 shadow-sm"
                        : "bg-muted/40 hover:bg-muted border-border text-foreground"
                    }`}
                  >
                    <span className="font-bold block">{mode.label}</span>
                    <span className="text-[10px] opacity-80">{mode.sub}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column: Vastu Direction, Usage, Resident DOB */}
          <div className="lg:col-span-5 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                  {language === "ta" ? "வாஸ்து திசை" : "Facing Direction (Vastu)"}
                </label>
                <select
                  value={facingDirection}
                  onChange={(e) => setFacingDirection(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl border border-input bg-background text-sm font-medium focus:ring-2 focus:ring-emerald-500"
                >
                  {DIRECTION_OPTIONS.map((d) => (
                    <option key={d.value} value={d.value}>
                      {d.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                  {language === "ta" ? "எண் கணித மரபு" : "Alphabet System"}
                </label>
                <select
                  value={systemConvention}
                  onChange={(e) => setSystemConvention(e.target.value as any)}
                  className="w-full px-3 py-2.5 rounded-xl border border-input bg-background text-sm font-medium focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="chaldean">Chaldean (1-8 Ancient Esoteric)</option>
                  <option value="pythagorean">Pythagorean (1-9 Western Standard)</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                {language === "ta" ? "பயன்பாட்டு நோக்கம்" : "Intended Property Usage"}
              </label>
              <select
                value={propertyUsage}
                onChange={(e) => setPropertyUsage(e.target.value)}
                className="w-full px-3 py-2.5 rounded-xl border border-input bg-background text-sm font-medium focus:ring-2 focus:ring-emerald-500"
              >
                {USAGE_OPTIONS.map((u) => (
                  <option key={u.value} value={u.value}>
                    {language === "ta" ? u.labelTa : u.labelEn}
                  </option>
                ))}
              </select>
            </div>

            {/* Resident / Owner Input */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">
                  Primary Owner / Resident
                </label>
                <input
                  type="text"
                  value={primaryOwnerName}
                  onChange={(e) => setPrimaryOwnerName(e.target.value)}
                  placeholder="e.g. Gokul"
                  className="w-full px-3 py-2 rounded-xl border border-input bg-background text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">
                  Birth Date (YYYY-MM-DD)
                </label>
                <input
                  type="date"
                  value={primaryBirthDate}
                  onChange={(e) => setPrimaryBirthDate(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-input bg-background text-sm"
                />
              </div>
            </div>

            {/* Language & Action */}
            <div className="flex items-center justify-between pt-3">
              <div className="flex items-center gap-3">
                <span className="text-xs text-muted-foreground">Language:</span>
                <button
                  type="button"
                  onClick={() => setReportLang("en")}
                  className={`px-2.5 py-1 rounded-lg text-xs font-medium border ${
                    reportLang === "en" ? "bg-emerald-600 text-white border-emerald-600" : "bg-muted border-border"
                  }`}
                >
                  English
                </button>
                <button
                  type="button"
                  onClick={() => setReportLang("ta")}
                  className={`px-2.5 py-1 rounded-lg text-xs font-medium border ${
                    reportLang === "ta" ? "bg-emerald-600 text-white border-emerald-600" : "bg-muted border-border"
                  }`}
                >
                  தமிழ்
                </button>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm shadow-md transition-all disabled:opacity-50"
              >
                {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                {language === "ta" ? "ஆய்வு செய்க" : "Analyze Property"}
              </button>
            </div>
          </div>
        </div>

        {/* Collapsible Co-Residents / Family Members */}
        <div className="border-t border-border pt-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
              <Users className="w-3.5 h-3.5" />
              {language === "ta" ? "குடும்ப உறுப்பினர்கள் / இணை குடியிருப்பாளர்கள்" : "Family Members & Co-Residents (Optional)"}
              {coResidents.length > 0 && ` (${coResidents.length})`}
            </span>
            <button
              type="button"
              onClick={() => setShowAddCoResident(!showAddCoResident)}
              className="text-xs text-emerald-600 hover:text-emerald-500 font-medium inline-flex items-center gap-1"
            >
              <Plus className="w-3.5 h-3.5" />
              Add Family Member
            </button>
          </div>

          {coResidents.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3">
              {coResidents.map((co, idx) => (
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
                    onClick={() => removeCoResident(idx)}
                    className="text-red-500 hover:text-red-400 ml-1"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          )}

          {showAddCoResident && (
            <div className="p-4 rounded-xl bg-muted/40 border border-border grid grid-cols-1 sm:grid-cols-4 gap-3 items-end">
              <div>
                <label className="text-[11px] text-muted-foreground block mb-1">Name</label>
                <input
                  type="text"
                  value={newResName}
                  onChange={(e) => setNewResName(e.target.value)}
                  placeholder="e.g. Spouse / Child"
                  className="w-full px-3 py-1.5 rounded-lg border border-input bg-background text-xs"
                />
              </div>
              <div>
                <label className="text-[11px] text-muted-foreground block mb-1">Birth Date (YYYY-MM-DD)</label>
                <input
                  type="date"
                  value={newResDob}
                  onChange={(e) => setNewResDob(e.target.value)}
                  className="w-full px-3 py-1.5 rounded-lg border border-input bg-background text-xs"
                />
              </div>
              <div>
                <label className="text-[11px] text-muted-foreground block mb-1">Role / Relationship</label>
                <input
                  type="text"
                  value={newResRole}
                  onChange={(e) => setNewResRole(e.target.value)}
                  placeholder="e.g. Spouse, Child"
                  className="w-full px-3 py-1.5 rounded-lg border border-input bg-background text-xs"
                />
              </div>
              <div>
                <button
                  type="button"
                  onClick={addCoResident}
                  className="w-full px-3 py-2 rounded-lg bg-emerald-600 text-white text-xs font-semibold hover:bg-emerald-500 transition-colors"
                >
                  Confirm Resident
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Candidate Properties for Comparison */}
        <div className="border-t border-border pt-4">
          <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
            {language === "ta" ? "ஒப்பீட்டு சொத்துக்கள் (Flats / Villas for Comparison)" : "Compare Alternative Properties / Units"}
          </label>
          <div className="flex flex-wrap gap-2 mb-3">
            {candidatesList.map((c, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-muted text-xs font-medium border border-border"
              >
                <span className="font-mono font-bold">{c.door}</span>
                <span>{c.name}</span>
                <button
                  type="button"
                  onClick={() => removeCandidate(idx)}
                  className="text-muted-foreground hover:text-red-500"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
          <div className="flex flex-col sm:flex-row gap-2 max-w-xl">
            <input
              type="text"
              value={newCandDoor}
              onChange={(e) => setNewCandDoor(e.target.value)}
              placeholder="Door (e.g. 504)"
              className="w-full sm:w-36 px-3 py-1.5 rounded-lg border border-input bg-background text-xs font-mono"
            />
            <input
              type="text"
              value={newCandName}
              onChange={(e) => setNewCandName(e.target.value)}
              placeholder="Building / Project (e.g. Royal Heights)"
              className="flex-1 px-3 py-1.5 rounded-lg border border-input bg-background text-xs"
            />
            <button
              type="button"
              onClick={addCandidate}
              className="px-3 py-1.5 rounded-lg bg-muted hover:bg-muted/80 text-xs font-medium border border-border inline-flex items-center gap-1"
            >
              <Plus className="w-3 h-3" />
              Add Unit
            </button>
          </div>
        </div>
      </form>

      {/* Error & Success Alerts */}
      {error && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-600 dark:text-red-400 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}
      {savedSuccessMsg && (
        <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-4 text-sm text-emerald-600 dark:text-emerald-400 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
          <span>{savedSuccessMsg}</span>
        </div>
      )}

      {/* Analysis Results View */}
      {result && (
        <div className="space-y-8">
          {/* Section 1: Property Identity & Primary Vibration */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left: Property Decomposition Card */}
            <div className="lg:col-span-5 rounded-2xl border border-border bg-card p-6 space-y-5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                  Dwelling Decomposition
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 capitalize">
                  {result.tenure_type}
                </span>
              </div>

              {/* Graphic Property Nameplate Badge */}
              <div className="p-5 rounded-2xl border-2 border-emerald-700/60 bg-gradient-to-b from-stone-50 to-stone-200 dark:from-stone-900 dark:to-stone-950 text-stone-900 dark:text-white shadow-md space-y-2">
                <div className="flex items-center justify-between border-b border-stone-300 dark:border-stone-800 pb-2">
                  <span className="text-xs font-bold font-mono tracking-wider text-emerald-700 dark:text-emerald-400">
                    {result.building_name || "RESIDENTIAL DWELLING"}
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-stone-300 dark:bg-stone-800">
                    {result.block_or_wing || "MAIN"}
                  </span>
                </div>
                <div className="text-3xl font-extrabold font-mono tracking-wide text-center py-2 text-stone-800 dark:text-stone-100">
                  {result.door_flat_number ? `NO. ${result.door_flat_number}` : result.full_identifier}
                </div>
                {result.floor_number && (
                  <div className="text-[11px] text-center text-muted-foreground">
                    Floor {result.floor_number} • {result.property_category.replace("_", " ").toUpperCase()}
                  </div>
                )}
              </div>

              {/* Component breakdown table */}
              <div className="grid grid-cols-4 gap-2 text-center text-xs">
                <div className="p-2.5 rounded-xl bg-muted/50 border border-border">
                  <span className="text-muted-foreground block text-[10px] uppercase">Door No.</span>
                  <span className="font-bold text-primary text-sm font-mono">{result.door_flat_number || "--"}</span>
                  <span className="text-[9px] text-muted-foreground block font-mono">
                    Root: {result.door_analysis.root_number || "--"}
                  </span>
                </div>
                <div className="p-2.5 rounded-xl bg-muted/50 border border-border">
                  <span className="text-muted-foreground block text-[10px] uppercase">Floor</span>
                  <span className="font-bold text-primary text-sm font-mono">{result.floor_number || "--"}</span>
                  <span className="text-[9px] text-muted-foreground block font-mono">
                    Root: {result.floor_analysis.root_number || "--"}
                  </span>
                </div>
                <div className="p-2.5 rounded-xl bg-muted/50 border border-border">
                  <span className="text-muted-foreground block text-[10px] uppercase">Building</span>
                  <span className="font-bold text-primary text-sm font-mono">{result.building_number || "--"}</span>
                  <span className="text-[9px] text-muted-foreground block font-mono">
                    Root: {result.building_analysis.root_number || "--"}
                  </span>
                </div>
                <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
                  <span className="text-emerald-600 dark:text-emerald-400 block text-[10px] uppercase font-bold">Combined</span>
                  <span className="font-extrabold text-emerald-600 dark:text-emerald-400 text-sm font-mono">
                    {result.combined_analysis.root_number}
                  </span>
                  <span className="text-[9px] text-muted-foreground block font-mono">
                    Sum: {result.combined_analysis.compound_sum}
                  </span>
                </div>
              </div>

              {/* Vastu Orientation Summary Badge */}
              {result.vastu_alignment && (
                <div className="p-4 rounded-xl bg-muted/30 border border-border space-y-2">
                  <div className="flex items-center justify-between text-xs font-semibold">
                    <span className="flex items-center gap-1.5">
                      <Compass className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                      Vastu Facing: {result.vastu_alignment.facing_direction}
                    </span>
                    <span className="font-bold text-emerald-600 dark:text-emerald-400">
                      {result.vastu_alignment.alignment_score}% Match
                    </span>
                  </div>
                  <div className="text-xs text-muted-foreground space-y-1">
                    <p>
                      <strong>Presiding Deity:</strong> {result.vastu_alignment.presiding_deity} ({result.vastu_alignment.sanskrit_name})
                    </p>
                    <p>
                      <strong>Element &amp; Ruler:</strong> {result.vastu_alignment.element} • {result.vastu_alignment.ruling_planet}
                    </p>
                    <p className="text-foreground/80 italic text-[11px] pt-1">
                      {result.vastu_alignment.notes}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Right: Primary Numerical Vibration & Transparent Reduction */}
            <div className="lg:col-span-7 rounded-2xl border border-border bg-card p-6 space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border pb-4">
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                    Active Mode: {result.primary_analysis.component_label}
                  </span>
                  <h3 className="text-2xl font-bold flex items-center gap-2 mt-1">
                    <span className="inline-flex items-center justify-center w-10 h-10 rounded-xl bg-emerald-600 text-white font-extrabold text-xl shadow-md">
                      {result.primary_analysis.root_number}
                    </span>
                    <span>{result.primary_analysis.keyword}</span>
                  </h3>
                </div>

                <div className="text-right">
                  <span className="text-xs text-muted-foreground block">Ruling Celestial Body</span>
                  <span className="font-semibold text-emerald-600 dark:text-emerald-400 text-sm">
                    {result.primary_analysis.ruling_planet}
                  </span>
                </div>
              </div>

              {/* Step-by-Step Reduction Steps */}
              <div className="space-y-2">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block">
                  Transparent Reduction Steps
                </span>
                <div className="p-3.5 rounded-xl bg-muted/50 border border-border font-mono text-xs space-y-1.5">
                  {result.primary_analysis.reduction_steps.map((st, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <span className="text-muted-foreground select-none">[{i + 1}]</span>
                      <span className={i === result.primary_analysis.reduction_steps.length - 1 ? "font-bold text-emerald-600 dark:text-emerald-400" : ""}>
                        {st}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Vibrational Meaning */}
              <div className="space-y-1.5">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block">
                  Dwelling Energy &amp; Architectural Archetype
                </span>
                <p className="text-sm text-foreground/90 leading-relaxed bg-emerald-500/5 dark:bg-emerald-950/20 p-4 rounded-xl border border-emerald-500/20">
                  {result.primary_analysis.vibrational_meaning}
                </p>
              </div>

              {/* All Calculation Modes Side-by-Side */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2">
                {[
                  { label: "Door Only", res: result.door_analysis },
                  { label: "Floor Level", res: result.floor_analysis },
                  { label: "Building Shell", res: result.building_analysis },
                  { label: "Combined Formula", res: result.combined_analysis },
                ].map((item, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-xl border border-border bg-muted/30 text-center space-y-1"
                  >
                    <span className="text-[10px] text-muted-foreground uppercase block font-semibold">
                      {item.label}
                    </span>
                    <span className="text-lg font-bold font-mono">
                      {item.res.root_number || "--"}
                    </span>
                    <span className="text-[10px] text-muted-foreground block font-mono">
                      Sum: {item.res.compound_sum}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Section 2: Usage Harmony & Resident Family Alignment */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Usage Harmony */}
            <div className="lg:col-span-5 rounded-2xl border border-border bg-card p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="font-bold text-base flex items-center gap-2">
                  <Building className="w-4 h-4 text-emerald-500" />
                  Usage Archetype Resonance
                </h4>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-600 border border-emerald-500/20">
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

            {/* Resident & Family Alignment */}
            <div className="lg:col-span-7 rounded-2xl border border-border bg-card p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="font-bold text-base flex items-center gap-2">
                  <Users className="w-4 h-4 text-emerald-500" />
                  Family &amp; Resident Astrological Synergy
                </h4>
                {result.overall_household_score !== null && (
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-600 border border-emerald-500/20">
                    Household Synergy: {result.overall_household_score}%
                  </span>
                )}
              </div>

              {result.resident_alignments.length > 0 ? (
                <div className="space-y-3">
                  {result.resident_alignments.map((resItem, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-xl bg-muted/40 border border-border space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-sm">{resItem.name}</span>
                          <span className="text-[10px] px-2 py-0.5 rounded bg-muted text-muted-foreground">
                            {resItem.role}
                          </span>
                        </div>
                        <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400">
                          {resItem.level} ({resItem.personal_score}%)
                        </span>
                      </div>
                      <div className="flex gap-4 text-xs text-muted-foreground">
                        <span>Psychic Number: <strong>{resItem.psychic_number}</strong></span>
                        <span>Life Path: <strong>{resItem.life_path_number}</strong></span>
                        <span>DOB: <strong className="font-mono">{resItem.birth_date}</strong></span>
                      </div>
                      <p className="text-xs text-foreground/80">
                        {resItem.synthesis}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-muted-foreground p-4 bg-muted/30 rounded-xl">
                  Enter an owner birth date above to view personal and family resonance with this property number.
                </p>
              )}
            </div>
          </div>

          {/* Section 3: Multi-Property Candidate Comparison & Ranking */}
          {sortedCandidates.length > 0 && (
            <div className="rounded-2xl border border-border bg-card p-6 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <h4 className="font-bold text-lg flex items-center gap-2">
                    <Scale className="w-5 h-5 text-emerald-500" />
                    Property Candidate Selection &amp; Ranking
                  </h4>
                  <p className="text-xs text-muted-foreground">
                    Ranked by composite harmony (Resident Astrological Synergy + Usage Archetype Match)
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">Sort By:</span>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as any)}
                    className="px-3 py-1.5 rounded-lg border border-input bg-background text-xs font-medium"
                  >
                    <option value="composite">Composite Harmony</option>
                    <option value="usage">Usage Match</option>
                    <option value="root">Root Number</option>
                  </select>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-border text-muted-foreground uppercase tracking-wider text-[10px]">
                      <th className="py-3 px-3">Rank</th>
                      <th className="py-3 px-3">Property Unit</th>
                      <th className="py-3 px-3">Building / Project</th>
                      <th className="py-3 px-3">Root</th>
                      <th className="py-3 px-3">Sum</th>
                      <th className="py-3 px-3">Ruler</th>
                      <th className="py-3 px-3">Usage Score</th>
                      <th className="py-3 px-3">Owner Synergy</th>
                      <th className="py-3 px-3">Composite</th>
                      <th className="py-3 px-3">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {sortedCandidates.map((cand, idx) => (
                      <React.Fragment key={idx}>
                        <tr className="hover:bg-muted/30 transition-colors">
                          <td className="py-3 px-3 font-bold text-muted-foreground">#{idx + 1}</td>
                          <td className="py-3 px-3 font-mono font-bold text-sm">
                            {cand.door_flat_number || cand.label}
                          </td>
                          <td className="py-3 px-3 text-muted-foreground">
                            {cand.building_name || "--"}
                          </td>
                          <td className="py-3 px-3 font-bold text-primary font-mono text-sm">
                            {cand.root_number}
                          </td>
                          <td className="py-3 px-3 text-muted-foreground font-mono">
                            {cand.compound_sum}
                          </td>
                          <td className="py-3 px-3 text-muted-foreground">
                            {cand.ruling_planet}
                          </td>
                          <td className="py-3 px-3 font-semibold text-emerald-600 dark:text-emerald-400">
                            {cand.usage_score}%
                          </td>
                          <td className="py-3 px-3 font-semibold">
                            {cand.owner_score !== null && cand.owner_score !== undefined ? `${cand.owner_score}%` : "--"}
                          </td>
                          <td className="py-3 px-3 font-extrabold text-sm text-emerald-600 dark:text-emerald-400">
                            {cand.composite_score}%
                          </td>
                          <td className="py-3 px-3">
                            <button
                              type="button"
                              onClick={() =>
                                setExpandedCandidate(
                                  expandedCandidate === cand.label ? null : cand.label
                                )
                              }
                              className="text-xs text-emerald-600 hover:text-emerald-500 font-medium inline-flex items-center gap-1"
                            >
                              {expandedCandidate === cand.label ? (
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

                        {expandedCandidate === cand.label && (
                          <tr className="bg-muted/20">
                            <td colSpan={10} className="p-4 space-y-2 text-xs">
                              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div className="p-3 rounded-lg bg-card border border-border">
                                  <span className="font-semibold block mb-1">Archetype Theme:</span>
                                  <span className="text-muted-foreground">{cand.keyword}</span>
                                </div>
                                <div className="p-3 rounded-lg bg-card border border-border">
                                  <span className="font-semibold block mb-1">Reduction Formula:</span>
                                  <span className="font-mono text-muted-foreground">
                                    {cand.reduction_steps.join(" -> ")}
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
                {language === "ta" ? "அறிக்கையைப் பாதுகாத்தல்" : "Save Property Analysis to Cloud Profile"}
              </span>
              <span className="text-xs text-muted-foreground">
                {isAuthenticated
                  ? "Store this dwelling analysis permanently with your saved profile readings."
                  : "Sign in to save this report to your profile."}
              </span>
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={handleSaveReport}
                disabled={!isAuthenticated || savingReport}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs shadow-sm transition-all disabled:opacity-50"
              >
                {savingReport ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Bookmark className="w-3.5 h-3.5" />}
                {language === "ta" ? "அறிக்கையைச் சேமிக்க" : "Save Report"}
              </button>
            </div>
          </div>

          {/* Legal / Ethical Disclaimer */}
          <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 dark:bg-emerald-950/20 p-4 text-xs text-muted-foreground leading-relaxed flex items-start gap-2.5">
            <Shield className="w-4 h-4 text-emerald-600 dark:text-emerald-400 flex-shrink-0 mt-0.5" />
            <div>
              <strong className="text-foreground block mb-0.5">Disclaimer &amp; Architectural Advisory:</strong>
              {result.disclaimer}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
