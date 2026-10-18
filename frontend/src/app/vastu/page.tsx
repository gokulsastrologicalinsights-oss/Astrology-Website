"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import {
  evaluateVastuLayout,
  getVastuDirections,
  saveVastuReport,
  listVastuReports,
  deleteVastuReport,
} from "@/lib/api";
import {
  VastuEvaluationRequest,
  VastuEvaluationResponse,
  DirectionMetadata,
  PadaDeityMetadata,
  SavedVastuReportResponse,
} from "@/lib/types";
import { VastuMandala } from "@/components/vastu/VastuMandala";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  Compass,
  Home,
  Building,
  MapPin,
  Factory,
  ShieldAlert,
  Sparkles,
  CheckCircle,
  AlertTriangle,
  Save,
  Trash2,
  ExternalLink,
  BookOpen,
  Layers,
  ArrowRight,
  Info,
  RotateCw,
} from "lucide-react";

export default function VastuPage() {
  const router = useRouter();
  const { user, session, isAuthenticated } = useAuth();

  // Active Tab
  const [activeTab, setActiveTab] = useState<"evaluate" | "mandala" | "reference" | "saved">("evaluate");

  // Reference data loaded from backend
  const [directions16, setDirections16] = useState<DirectionMetadata[]>([]);
  const [padas32, setPadas32] = useState<PadaDeityMetadata[]>([]);
  const [loadingMetadata, setLoadingMetadata] = useState(false);

  // Form Inputs
  const [propertyName, setPropertyName] = useState("My Residence");
  const [propertyType, setPropertyType] = useState<"residential" | "commercial" | "plot" | "industrial">("residential");
  const [facingDirection, setFacingDirection] = useState("E");
  const [facingDegrees, setFacingDegrees] = useState<string>("");

  // Residential Placements
  const [mainEntranceDir, setMainEntranceDir] = useState("E");
  const [kitchenDir, setKitchenDir] = useState("SE");
  const [masterBedDir, setMasterBedDir] = useState("SW");
  const [poojaDir, setPoojaDir] = useState("NE");
  const [toiletDirs, setToiletDirs] = useState<string[]>(["WNW"]);
  const [brahmasthanStatus, setBrahmasthanStatus] = useState<"clear" | "partially_obstructed" | "heavily_obstructed">("clear");
  const [plotShape, setPlotShape] = useState<"square" | "rectangular" | "gaumukhi" | "shermukhi" | "triangular" | "irregular">("square");

  // Commercial / Plot / Industrial Placements
  const [ownerCabinDir, setOwnerCabinDir] = useState("SW");
  const [accountsDir, setAccountsDir] = useState("N");
  const [conferenceDir, setConferenceDir] = useState("NW");
  const [slopeDir, setSlopeDir] = useState("NE");
  const [heavyMachineryDir, setHeavyMachineryDir] = useState("SW");
  const [boilerFurnaceDir, setBoilerFurnaceDir] = useState("SE");

  // Astro-Vastu Inputs
  const [includeAstro, setIncludeAstro] = useState(false);
  const [birthDate, setBirthDate] = useState("");
  const [birthTime, setBirthTime] = useState("");
  const [timezone, setTimezone] = useState("Asia/Kolkata");
  const [latitude, setLatitude] = useState("13.0827");
  const [longitude, setLongitude] = useState("80.2707");

  // Evaluation Output State
  const [evalResult, setEvalResult] = useState<VastuEvaluationResponse | null>(null);
  const [evaluating, setEvaluating] = useState(false);
  const [evalError, setEvalError] = useState<string | null>(null);

  // Persistence State
  const [saving, setSaving] = useState(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);
  const [savedReports, setSavedReports] = useState<SavedVastuReportResponse[]>([]);
  const [loadingReports, setLoadingReports] = useState(false);

  // Load directions & padas metadata once on mount
  useEffect(() => {
    setLoadingMetadata(true);
    getVastuDirections()
      .then((data) => {
        setDirections16(data.directions_16);
        setPadas32(data.padas_32);
      })
      .catch((err) => {
        console.warn("Failed to load Vastu metadata:", err);
      })
      .finally(() => setLoadingMetadata(false));
  }, []);

  // Load saved reports if user is authenticated
  useEffect(() => {
    if (session?.access_token && activeTab === "saved") {
      fetchSavedReports();
    }
  }, [session?.access_token, activeTab]);

  const fetchSavedReports = async () => {
    if (!session?.access_token) return;
    setLoadingReports(true);
    try {
      const res = await listVastuReports(session.access_token, 50, 0);
      setSavedReports(res.reports || []);
    } catch (err) {
      console.warn("Failed to load saved reports:", err);
    } finally {
      setLoadingReports(false);
    }
  };

  const handleEvaluate = async (e: React.FormEvent) => {
    e.preventDefault();
    setEvaluating(true);
    setEvalError(null);
    setSaveSuccessMsg(null);

    const reqPayload: VastuEvaluationRequest = {
      property_name: propertyName.trim() || "Untitled Property",
      property_type: propertyType,
      facing_direction: facingDirection,
      facing_degrees: facingDegrees ? parseFloat(facingDegrees) : undefined,
      placements: {
        main_entrance_direction: mainEntranceDir || undefined,
        kitchen_direction: propertyType === "residential" ? kitchenDir : undefined,
        master_bedroom_direction: propertyType === "residential" ? masterBedDir : undefined,
        pooja_room_direction: propertyType === "residential" ? poojaDir : undefined,
        toilet_directions: propertyType === "residential" ? toiletDirs : undefined,
        brahmasthan_status: brahmasthanStatus,
        plot_shape: plotShape,
        slope_direction: propertyType === "plot" ? slopeDir : undefined,
        owner_cabin_direction: propertyType === "commercial" ? ownerCabinDir : undefined,
        accounts_cash_direction: propertyType === "commercial" ? accountsDir : undefined,
        conference_room_direction: propertyType === "commercial" ? conferenceDir : undefined,
        heavy_machinery_direction: propertyType === "industrial" ? heavyMachineryDir : undefined,
        boiler_furnace_direction: propertyType === "industrial" ? boilerFurnaceDir : undefined,
      },
      birth_date: includeAstro && birthDate ? birthDate : undefined,
      birth_time: includeAstro && birthTime ? birthTime : undefined,
      timezone: includeAstro ? timezone : undefined,
      latitude: includeAstro && latitude ? parseFloat(latitude) : undefined,
      longitude: includeAstro && longitude ? parseFloat(longitude) : undefined,
    };

    try {
      const result = await evaluateVastuLayout(reqPayload);
      setEvalResult(result);
    } catch (err: any) {
      setEvalError(err?.message || "Evaluation failed. Please review input directions.");
    } finally {
      setEvaluating(false);
    }
  };

  const handleSaveReport = async () => {
    if (!isAuthenticated || !session?.access_token) {
      router.push("/login");
      return;
    }
    if (!evalResult) return;

    setSaving(true);
    setSaveSuccessMsg(null);
    try {
      const saved = await saveVastuReport(session.access_token, {
        property_name: evalResult.property_name,
        property_type: evalResult.property_type as any,
        facing_direction: evalResult.facing_direction,
        facing_degrees: evalResult.facing_degrees || null,
        birth_date: birthDate || null,
        evaluation_data: evalResult as any,
      });
      setSaveSuccessMsg(`Assessment saved successfully as VASTU-#${saved.display_number}!`);
      fetchSavedReports();
    } catch (err: any) {
      alert("Failed to save report: " + (err?.message || "Unknown error"));
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteReport = async (id: string) => {
    if (!session?.access_token) return;
    if (!confirm("Are you sure you want to delete this saved Vastu assessment?")) return;
    try {
      await deleteVastuReport(session.access_token, id);
      setSavedReports((prev) => prev.filter((r) => r.id !== id));
    } catch (err: any) {
      alert("Failed to delete report: " + err.message);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-8">
      {/* Breadcrumbs */}
      <Breadcrumbs
        items={[
          { label: "Home", href: "/" },
          { label: "Dashboard", href: "/dashboard" },
          { label: "Vastu Shastra" },
        ]}
      />

      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-8 sm:p-10 shadow-xl border border-slate-800">
        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 border border-amber-400/30 text-amber-300 text-xs font-semibold uppercase tracking-wider">
            <span>🕉️</span> Classical Vastu Vidya · Mayamata & Manasara
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
            Vastu Shastra Architectural Assessment
          </h1>
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            Evaluate directional alignments, room placements, and spatial harmony according to classical
            Vedic architectural principles. Deterministic scoring normalized across assessable zones with
            remedial recommendations.
          </p>
        </div>
      </div>

      {/* Main Tabs Navigation */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 pb-2">
        <button
          onClick={() => setActiveTab("evaluate")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all ${
            activeTab === "evaluate"
              ? "bg-[#3478F6] text-white shadow-sm"
              : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
          }`}
        >
          <Compass className="w-4 h-4" />
          <span>Layout Evaluator</span>
        </button>

        <button
          onClick={() => setActiveTab("mandala")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all ${
            activeTab === "mandala"
              ? "bg-[#3478F6] text-white shadow-sm"
              : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>Vastu Mandala</span>
        </button>

        <button
          onClick={() => setActiveTab("reference")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all ${
            activeTab === "reference"
              ? "bg-[#3478F6] text-white shadow-sm"
              : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
          }`}
        >
          <BookOpen className="w-4 h-4" />
          <span>16 Directions & 32 Padas</span>
        </button>

        <button
          onClick={() => setActiveTab("saved")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all ${
            activeTab === "saved"
              ? "bg-[#3478F6] text-white shadow-sm"
              : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
          }`}
        >
          <Save className="w-4 h-4" />
          <span>Saved Assessments {savedReports.length > 0 && `(${savedReports.length})`}</span>
        </button>
      </div>

      {/* TAB 1: LAYOUT EVALUATION */}
      {activeTab === "evaluate" && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Input Form Column */}
          <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 space-y-6">
            <div className="border-b border-slate-100 pb-4">
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <span>🏠</span> Property Layout Specifications
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Select your property type and enter room or functional zone orientations.
              </p>
            </div>

            <form onSubmit={handleEvaluate} className="space-y-5 text-sm">
              {/* Property Name */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Property Name / Label
                </label>
                <input
                  type="text"
                  value={propertyName}
                  onChange={(e) => setPropertyName(e.target.value)}
                  placeholder="e.g. My Residence, Palm Grove Villa"
                  className="w-full px-3.5 py-2 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-slate-800"
                  required
                />
              </div>

              {/* Property Type Selector */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Property Classification
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { id: "residential", label: "Residential", icon: Home },
                    { id: "commercial", label: "Commercial", icon: Building },
                    { id: "plot", label: "Vacant Plot", icon: MapPin },
                    { id: "industrial", label: "Industrial", icon: Factory },
                  ].map((pt) => {
                    const Icon = pt.icon;
                    const isSelected = propertyType === pt.id;
                    return (
                      <button
                        type="button"
                        key={pt.id}
                        onClick={() => setPropertyType(pt.id as any)}
                        className={`flex items-center gap-2 px-3 py-2 rounded-xl border text-xs font-medium transition-all ${
                          isSelected
                            ? "bg-blue-50/80 border-blue-500 text-blue-800 font-semibold"
                            : "border-slate-200 text-slate-600 hover:bg-slate-50"
                        }`}
                      >
                        <Icon className={`w-3.5 h-3.5 ${isSelected ? "text-blue-600" : "text-slate-400"}`} />
                        <span>{pt.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Facing Orientation & Compass Degrees */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Main Facing Direction
                  </label>
                  <select
                    value={facingDirection}
                    onChange={(e) => setFacingDirection(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-slate-800 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-xs"
                  >
                    {directions16.map((d) => (
                      <option key={d.code} value={d.code}>
                        {d.code} ({d.english_name} · {d.center_degree}°)
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Compass Azimuth (Optional)
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="359.9"
                    step="0.1"
                    value={facingDegrees}
                    onChange={(e) => setFacingDegrees(e.target.value)}
                    placeholder="e.g. 88.5°"
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-slate-800 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-xs"
                  />
                </div>
              </div>

              {/* Residential-Specific Room Inputs */}
              {propertyType === "residential" && (
                <div className="space-y-4 pt-3 border-t border-slate-100">
                  <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                    Residential Room Placements
                  </h3>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-[11px] font-medium text-slate-600 mb-1">
                        Main Entrance (門)
                      </label>
                      <select
                        value={mainEntranceDir}
                        onChange={(e) => setMainEntranceDir(e.target.value)}
                        className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs"
                      >
                        {directions16.map((d) => (
                          <option key={`me-${d.code}`} value={d.code}>{d.code} - {d.english_name}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-medium text-slate-600 mb-1">
                        Kitchen (廚房)
                      </label>
                      <select
                        value={kitchenDir}
                        onChange={(e) => setKitchenDir(e.target.value)}
                        className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs"
                      >
                        {directions16.map((d) => (
                          <option key={`k-${d.code}`} value={d.code}>{d.code} - {d.english_name}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-medium text-slate-600 mb-1">
                        Master Bedroom (主臥)
                      </label>
                      <select
                        value={masterBedDir}
                        onChange={(e) => setMasterBedDir(e.target.value)}
                        className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs"
                      >
                        {directions16.map((d) => (
                          <option key={`mb-${d.code}`} value={d.code}>{d.code} - {d.english_name}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-medium text-slate-600 mb-1">
                        Pooja / Altar (神壇)
                      </label>
                      <select
                        value={poojaDir}
                        onChange={(e) => setPoojaDir(e.target.value)}
                        className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs"
                      >
                        {directions16.map((d) => (
                          <option key={`pj-${d.code}`} value={d.code}>{d.code} - {d.english_name}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-[11px] font-medium text-slate-600 mb-1">
                      Toilet Zone (廁所)
                    </label>
                    <select
                      value={toiletDirs[0] || "WNW"}
                      onChange={(e) => setToiletDirs([e.target.value])}
                      className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs"
                    >
                      {directions16.map((d) => (
                        <option key={`t-${d.code}`} value={d.code}>{d.code} - {d.english_name}</option>
                      ))}
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-[11px] font-medium text-slate-600 mb-1">
                        Central Brahmasthan
                      </label>
                      <select
                        value={brahmasthanStatus}
                        onChange={(e) => setBrahmasthanStatus(e.target.value as any)}
                        className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs"
                      >
                        <option value="clear">Clear & Open (開闊潔淨)</option>
                        <option value="partially_obstructed">Light Furniture (局部陳設)</option>
                        <option value="heavily_obstructed">Pillars/Stairs (重度阻斷)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-medium text-slate-600 mb-1">
                        Plot Shape
                      </label>
                      <select
                        value={plotShape}
                        onChange={(e) => setPlotShape(e.target.value as any)}
                        className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs"
                      >
                        <option value="square">Square (正方大吉)</option>
                        <option value="rectangular">Rectangular (長方吉)</option>
                        <option value="gaumukhi">Gaumukhi (牛面吉)</option>
                        <option value="shermukhi">Shermukhi (獅面)</option>
                        <option value="irregular">Irregular/Cut (不規則缺角)</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {/* Commercial Inputs */}
              {propertyType === "commercial" && (
                <div className="space-y-4 pt-3 border-t border-slate-100">
                  <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                    Commercial Placements
                  </h3>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-[11px] font-medium text-slate-600 mb-1">
                        Executive / Owner Cabin
                      </label>
                      <select
                        value={ownerCabinDir}
                        onChange={(e) => setOwnerCabinDir(e.target.value)}
                        className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs"
                      >
                        {directions16.map((d) => (
                          <option key={`oc-${d.code}`} value={d.code}>{d.code} - {d.english_name}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-medium text-slate-600 mb-1">
                        Accounts & Cash Counter
                      </label>
                      <select
                        value={accountsDir}
                        onChange={(e) => setAccountsDir(e.target.value)}
                        className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs"
                      >
                        {directions16.map((d) => (
                          <option key={`acc-${d.code}`} value={d.code}>{d.code} - {d.english_name}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {/* Plot Inputs */}
              {propertyType === "plot" && (
                <div className="space-y-4 pt-3 border-t border-slate-100">
                  <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                    Plot Geometry & Terrain
                  </h3>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-[11px] font-medium text-slate-600 mb-1">
                        Downward Slope Direction
                      </label>
                      <select
                        value={slopeDir}
                        onChange={(e) => setSlopeDir(e.target.value)}
                        className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs"
                      >
                        {directions16.map((d) => (
                          <option key={`sl-${d.code}`} value={d.code}>{d.code} - {d.english_name}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-medium text-slate-600 mb-1">
                        Plot Shape
                      </label>
                      <select
                        value={plotShape}
                        onChange={(e) => setPlotShape(e.target.value as any)}
                        className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs"
                      >
                        <option value="square">Square</option>
                        <option value="rectangular">Rectangular</option>
                        <option value="gaumukhi">Gaumukhi (Cow-faced)</option>
                        <option value="shermukhi">Sher-mukhi (Lion-faced)</option>
                        <option value="irregular">Irregular / Cut</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {/* Industrial Inputs */}
              {propertyType === "industrial" && (
                <div className="space-y-4 pt-3 border-t border-slate-100">
                  <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                    Industrial & Plant Equipment
                  </h3>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-[11px] font-medium text-slate-600 mb-1">
                        Heavy Machinery Plant
                      </label>
                      <select
                        value={heavyMachineryDir}
                        onChange={(e) => setHeavyMachineryDir(e.target.value)}
                        className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs"
                      >
                        {directions16.map((d) => (
                          <option key={`hm-${d.code}`} value={d.code}>{d.code} - {d.english_name}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-medium text-slate-600 mb-1">
                        Boiler / Furnace / Transformer
                      </label>
                      <select
                        value={boilerFurnaceDir}
                        onChange={(e) => setBoilerFurnaceDir(e.target.value)}
                        className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs"
                      >
                        {directions16.map((d) => (
                          <option key={`bf-${d.code}`} value={d.code}>{d.code} - {d.english_name}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {/* Optional Astro-Vastu Linkage Toggle */}
              <div className="pt-3 border-t border-slate-100">
                <label className="flex items-center gap-2 cursor-pointer text-xs font-medium text-slate-700">
                  <input
                    type="checkbox"
                    checked={includeAstro}
                    onChange={(e) => setIncludeAstro(e.target.checked)}
                    className="rounded text-blue-600 focus:ring-blue-500"
                  />
                  <span>Include Astro-Vastu Synthesis (Native XALEN Ephemeris)</span>
                </label>

                {includeAstro && (
                  <div className="mt-3 p-3 bg-slate-50 border border-slate-200/80 rounded-xl space-y-3 text-xs">
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="block text-[10px] text-slate-500 mb-0.5">Birth Date</label>
                        <input
                          type="date"
                          value={birthDate}
                          onChange={(e) => setBirthDate(e.target.value)}
                          className="w-full px-2 py-1.5 border rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-[10px] text-slate-500 mb-0.5">Birth Time (24h)</label>
                        <input
                          type="time"
                          value={birthTime}
                          onChange={(e) => setBirthTime(e.target.value)}
                          className="w-full px-2 py-1.5 border rounded-lg"
                        />
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={evaluating}
                className="w-full py-3 px-4 bg-[#3478F6] hover:bg-blue-600 text-white font-semibold rounded-xl shadow-sm transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {evaluating ? (
                  <>
                    <RotateCw className="w-4 h-4 animate-spin" />
                    <span>Evaluating Vastu Alignments...</span>
                  </>
                ) : (
                  <>
                    <Compass className="w-4 h-4" />
                    <span>Execute Vastu Assessment</span>
                  </>
                )}
              </button>

              {evalError && (
                <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-xs flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                  <span>{evalError}</span>
                </div>
              )}
            </form>
          </div>

          {/* Results Column */}
          <div className="lg:col-span-7 space-y-6">
            {evalResult ? (
              <>
                {/* Score Header Card */}
                <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
                    <div>
                      <span className="text-xs uppercase tracking-wider font-semibold text-slate-400">
                        {evalResult.property_type} Assessment
                      </span>
                      <h3 className="text-xl font-extrabold text-slate-900 mt-0.5">
                        {evalResult.property_name}
                      </h3>
                      <p className="text-xs text-slate-500 mt-0.5">
                        Facing: <span className="font-semibold text-slate-700">{evalResult.facing_direction}</span>
                        {evalResult.facing_degrees != null && ` (${evalResult.facing_degrees}°)`} · Engine v{evalResult.engine_version}
                      </p>
                    </div>

                    {/* Action buttons */}
                    <div className="flex items-center gap-2">
                      <button
                        onClick={handleSaveReport}
                        disabled={saving}
                        className="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-xl shadow-sm flex items-center gap-1.5 transition-all disabled:opacity-50"
                      >
                        <Save className="w-3.5 h-3.5" />
                        <span>{saving ? "Saving..." : "Save Assessment"}</span>
                      </button>
                    </div>
                  </div>

                  {saveSuccessMsg && (
                    <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs flex items-center gap-2 font-medium">
                      <CheckCircle className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                      <span>{saveSuccessMsg}</span>
                    </div>
                  )}

                  {/* Compliance Score Gauge */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-center bg-slate-50 p-4 rounded-xl border border-slate-200/80">
                    <div className="text-center sm:text-left">
                      <span className="text-xs text-slate-500 font-medium">Normalized Compliance</span>
                      <div className="text-3xl font-black text-slate-900 mt-0.5">
                        {evalResult.compliance_score != null ? (
                          <>
                            <span className={evalResult.compliance_score >= 70 ? "text-emerald-600" : evalResult.compliance_score >= 50 ? "text-amber-600" : "text-rose-600"}>
                              {evalResult.compliance_score}
                            </span>
                            <span className="text-slate-400 text-lg font-normal"> / 100</span>
                          </>
                        ) : (
                          <span className="text-slate-400 text-lg">Unassessed</span>
                        )}
                      </div>
                    </div>

                    <div className="sm:col-span-2 space-y-1.5">
                      <div className="flex justify-between text-xs font-medium">
                        <span className="text-slate-700">{evalResult.score_grade}</span>
                        <span className="text-slate-500">
                          {evalResult.factors_assessed} of {evalResult.factors_total} factors assessed
                        </span>
                      </div>
                      <div className="w-full bg-slate-200 h-2.5 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${
                            (evalResult.compliance_score || 0) >= 70
                              ? "bg-emerald-500"
                              : (evalResult.compliance_score || 0) >= 50
                              ? "bg-amber-500"
                              : "bg-rose-500"
                          }`}
                          style={{ width: `${evalResult.compliance_score || 0}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Doshas Alert Banner (if any) */}
                {evalResult.doshas.length > 0 && (
                  <div className="bg-rose-50 border border-rose-200/90 rounded-2xl p-5 space-y-3">
                    <div className="flex items-center gap-2 text-rose-800 font-bold text-sm">
                      <ShieldAlert className="w-4 h-4 text-rose-600 flex-shrink-0" />
                      <span>Classical Vastu Doshas Identified ({evalResult.doshas.length})</span>
                    </div>

                    <div className="space-y-3">
                      {evalResult.doshas.map((d) => (
                        <div key={d.dosha_code} className="bg-white p-3.5 rounded-xl border border-rose-200 shadow-xs space-y-1.5 text-xs">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-rose-900">{d.dosha_name}</span>
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-rose-100 text-rose-800">
                              {d.severity}
                            </span>
                          </div>
                          <p className="text-slate-600">{d.traditional_impact}</p>
                          <div className="pt-1.5 border-t border-slate-100">
                            <span className="font-semibold text-slate-700">Classical Remedies:</span>
                            <ul className="list-disc list-inside mt-0.5 space-y-0.5 text-slate-600">
                              {d.remedies.map((rem, i) => (
                                <li key={i}>{rem}</li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Astro-Vastu Synthesis Card */}
                {evalResult.astro_overlay && (
                  <div className="bg-indigo-50/80 border border-indigo-200 rounded-2xl p-5 space-y-3 text-xs">
                    <div className="flex items-center justify-between text-indigo-900 font-bold text-sm">
                      <div className="flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-indigo-600" />
                        <span>Astro-Vastu Birth Alignment</span>
                      </div>
                      <span className="text-[10px] font-normal text-indigo-600">
                        {evalResult.astro_overlay.calculation_source}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-3 bg-white p-3 rounded-xl border border-indigo-100">
                      <div>
                        <span className="text-slate-500 font-medium">Ascendant (Lagna):</span>
                        <p className="font-bold text-slate-800 text-sm">{evalResult.astro_overlay.lagna_sign}</p>
                      </div>
                      <div>
                        <span className="text-slate-500 font-medium">Lagna Lord:</span>
                        <p className="font-bold text-slate-800 text-sm">{evalResult.astro_overlay.lagna_ruler}</p>
                      </div>
                    </div>

                    <div className="space-y-1 text-slate-700">
                      <p>
                        <span className="font-semibold">Favorable Cardinal Zones:</span>{" "}
                        {evalResult.astro_overlay.favorable_directions.join(", ")}
                      </p>
                      <ul className="list-disc list-inside text-slate-600 space-y-0.5">
                        {evalResult.astro_overlay.planetary_zone_notes.map((note, idx) => (
                          <li key={idx}>{note}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Factor-by-Factor Evaluation Table */}
                <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 space-y-4">
                  <h3 className="text-base font-bold text-slate-900">
                    Detailed Factor Findings & Classical Citations
                  </h3>

                  <div className="space-y-3 text-xs">
                    {evalResult.factor_results.map((f) => (
                      <div
                        key={f.factor_key}
                        className="p-3.5 rounded-xl border border-slate-200/80 hover:border-slate-300 transition-all space-y-2"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-800 text-sm">{f.factor_name}</span>
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                              f.severity === "ideal"
                                ? "bg-emerald-100 text-emerald-800"
                                : f.severity === "acceptable"
                                ? "bg-blue-100 text-blue-800"
                                : f.severity === "moderate_defect"
                                ? "bg-amber-100 text-amber-800"
                                : f.severity === "severe_defect"
                                ? "bg-rose-100 text-rose-800"
                                : "bg-slate-100 text-slate-600"
                            }`}
                          >
                            {f.severity.replace("_", " ")}
                          </span>
                        </div>

                        <div className="text-slate-600 space-y-1">
                          <p>{f.explanation}</p>
                          <p className="text-[11px] text-slate-400 italic">
                            Rule: {f.traditional_rule} ({f.rule_source})
                          </p>
                        </div>

                        {f.remedy && (
                          <div className="p-2 bg-amber-50/70 border border-amber-200/60 rounded-lg text-amber-900 text-[11px]">
                            <span className="font-semibold">Remedy:</span> {f.remedy}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Disclaimer */}
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-slate-500 text-xs leading-relaxed flex items-start gap-2.5">
                  <Info className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
                  <p>{evalResult.disclaimer}</p>
                </div>
              </>
            ) : (
              /* Placeholder State */
              <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-12 text-center space-y-4">
                <div className="w-16 h-16 mx-auto rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center text-2xl">
                  🧭
                </div>
                <h3 className="text-lg font-bold text-slate-800">
                  Ready for Assessment
                </h3>
                <p className="text-xs text-slate-500 max-w-md mx-auto">
                  Configure your property classification and room orientations on the left, then click
                  &quot;Execute Vastu Assessment&quot; to inspect compliance scores, classical Doshas, and traditional remedies.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: VASTU MANDALA */}
      {activeTab === "mandala" && (
        <div className="space-y-6">
          <VastuMandala
            directions={directions16}
            padas={padas32}
            highlightDirection={facingDirection}
            favorableDirections={evalResult?.astro_overlay?.favorable_directions || []}
          />
        </div>
      )}

      {/* TAB 3: 16 DIRECTIONS & 32 PADAS REFERENCE */}
      {activeTab === "reference" && (
        <div className="space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6">
            <h3 className="text-lg font-bold text-slate-900 mb-1">
              Standardized 16-Direction Reference Guide
            </h3>
            <p className="text-xs text-slate-500 mb-6">
              Traversed strictly clockwise in 22.5° sectors with governing Vedic deities, elements, and colors.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {directions16.map((d) => (
                <div
                  key={d.code}
                  className="p-4 rounded-xl border border-slate-200/80 bg-slate-50/50 space-y-2 text-xs"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-extrabold text-sm text-slate-800">{d.code} · {d.english_name}</span>
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-blue-100 text-blue-800">
                      {d.center_degree}°
                    </span>
                  </div>
                  <p className="text-slate-500 font-medium">{d.sanskrit_name}</p>
                  <p className="text-slate-600">
                    <span className="font-semibold">Deity:</span> {d.deity}
                  </p>
                  <p className="text-slate-600">
                    <span className="font-semibold">Element:</span> {d.element}
                  </p>
                  <p className="text-slate-500 text-[11px] leading-relaxed pt-1 border-t border-slate-200">
                    {d.traditional_significance}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: SAVED ASSESSMENTS */}
      {activeTab === "saved" && (
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 space-y-6">
          <div className="border-b border-slate-100 pb-4">
            <h3 className="text-lg font-bold text-slate-900">
              Saved Vastu Assessments History
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Sequential property evaluations saved under your authenticated account.
            </p>
          </div>

          {!isAuthenticated ? (
            <div className="p-8 text-center space-y-3">
              <p className="text-slate-500 text-xs">Please log in to inspect your saved Vastu assessments.</p>
              <Link
                href="/login"
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-xl text-xs font-semibold"
              >
                Log In
              </Link>
            </div>
          ) : loadingReports ? (
            <div className="p-8 text-center text-slate-400 text-xs">Loading saved reports...</div>
          ) : savedReports.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-xs">
              No saved Vastu assessments found. Evaluate a layout and click &quot;Save Assessment&quot; to track property history.
            </div>
          ) : (
            <div className="space-y-3">
              {savedReports.map((r) => (
                <div
                  key={r.id}
                  className="p-4 rounded-xl border border-slate-200/80 hover:border-slate-300 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded font-bold text-[10px]">
                        VASTU-#{r.display_number}
                      </span>
                      <span className="font-bold text-slate-900 text-sm">{r.property_name}</span>
                      <span className="text-slate-400 uppercase text-[10px]">({r.property_type})</span>
                    </div>
                    <p className="text-slate-500 text-[11px]">
                      Facing: {r.facing_direction} · Score:{" "}
                      <span className="font-bold text-slate-800">{r.compliance_score} / 100</span> · Saved on{" "}
                      {new Date(r.created_at).toLocaleDateString()}
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <Link
                      href={`/vastu/report/${r.id}`}
                      className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-lg flex items-center gap-1 transition-all"
                    >
                      <span>View Report</span>
                      <ExternalLink className="w-3 h-3" />
                    </Link>

                    <button
                      onClick={() => handleDeleteReport(r.id)}
                      className="p-1.5 text-slate-400 hover:text-rose-600 transition-all"
                      title="Delete assessment"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
