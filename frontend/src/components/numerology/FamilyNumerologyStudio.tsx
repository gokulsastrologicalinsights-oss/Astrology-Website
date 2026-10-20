"use client";

import React, { useState } from "react";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { analyzeFamilyNumerology, saveNumerologyReport, exportNumerologyPdf } from "@/lib/api";
import {
  FamilyNumerologyRequest,
  FamilyNumerologyResponse,
  FamilyMemberInput,
} from "@/lib/types";
import {
  Users,
  Baby,
  Sparkles,
  Heart,
  Save,
  Download,
  Loader2,
  Plus,
  Trash2,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  ShieldCheck,
  Flame,
  Droplets,
  Wind,
  Layers,
  Compass,
  ArrowRight,
  BookOpen,
} from "lucide-react";

interface MemberFormState {
  id: string;
  name: string;
  role: string;
  birth_date: string;
}

export function FamilyNumerologyStudio() {
  const { language } = useLanguage();
  const { session, isAuthenticated } = useAuth();

  // General configuration
  const [familyName, setFamilyName] = useState<string>("Sundaram Family");
  const [convention, setConvention] = useState<"pythagorean" | "chaldean">("pythagorean");
  const [reportLang, setReportLang] = useState<"en" | "ta">("en");

  // Multi-member list
  const [members, setMembers] = useState<MemberFormState[]>([
    { id: "1", name: "Sundaram", role: "father", birth_date: "1984-05-12" },
    { id: "2", name: "Lakshmi", role: "mother", birth_date: "1987-08-22" },
    { id: "3", name: "Ananya", role: "child", birth_date: "2018-11-04" },
  ]);

  // Baby Name Studio inputs
  const [babyCandidatesText, setBabyCandidatesText] = useState<string>("Aarav, Advik, Kavin");
  const [babyDob, setBabyDob] = useState<string>("");
  const [babySurname, setBabySurname] = useState<string>("Sundaram");
  const [targetRoot, setTargetRoot] = useState<string>("");
  const [generateSuggestions, setGenerateSuggestions] = useState<boolean>(true);

  // Computation state
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<FamilyNumerologyResponse | null>(null);

  // Persistence & PDF export
  const [saving, setSaving] = useState<boolean>(false);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [pdfDownloading, setPdfDownloading] = useState<boolean>(false);

  // Member management handlers
  const handleAddMember = () => {
    if (members.length >= 10) return;
    const nextId = String(Date.now());
    setMembers((prev) => [
      ...prev,
      { id: nextId, name: "", role: "child", birth_date: "" },
    ]);
  };

  const handleRemoveMember = (id: string) => {
    if (members.length <= 1) return;
    setMembers((prev) => prev.filter((m) => m.id !== id));
  };

  const handleUpdateMember = (id: string, field: keyof MemberFormState, value: string) => {
    setMembers((prev) =>
      prev.map((m) => (m.id === id ? { ...m, [field]: value } : m))
    );
  };

  const handleReset = () => {
    setFamilyName("Sundaram Family");
    setMembers([
      { id: "1", name: "Sundaram", role: "father", birth_date: "1984-05-12" },
      { id: "2", name: "Lakshmi", role: "mother", birth_date: "1987-08-22" },
      { id: "3", name: "Ananya", role: "child", birth_date: "2018-11-04" },
    ]);
    setBabyCandidatesText("Aarav, Advik, Kavin");
    setBabyDob("");
    setBabySurname("Sundaram");
    setTargetRoot("");
    setGenerateSuggestions(true);
    setResult(null);
    setError(null);
    setSaveSuccess(null);
    setSaveError(null);
  };

  const handleAnalyze = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (members.length === 0) {
      setError(language === "ta" ? "குறைந்தது ஒரு குடும்ப உறுப்பினரைச் சேர்க்கவும்." : "Please add at least one family member.");
      return;
    }

    setLoading(true);
    setError(null);
    setSaveSuccess(null);
    setSaveError(null);

    const candidateList = babyCandidatesText
      .split(/[,;\n]+/)
      .map((s) => s.trim())
      .filter(Boolean);

    const payload: FamilyNumerologyRequest = {
      family_name: familyName.trim() || undefined,
      members: members.map((m) => ({
        id: m.id,
        name: m.name.trim() || undefined,
        role: m.role,
        birth_date: m.birth_date.trim() || undefined,
      })),
      candidate_names: candidateList.length > 0 ? candidateList : undefined,
      baby_dob: babyDob.trim() || undefined,
      surname: babySurname.trim() || undefined,
      target_root: targetRoot ? parseInt(targetRoot, 10) : undefined,
      system_convention: convention,
      generate_suggestions: generateSuggestions,
      language: reportLang,
    };

    try {
      const res = await analyzeFamilyNumerology(payload, session?.access_token);
      setResult(res);
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || "Failed to analyze family numerology.");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveReport = async () => {
    if (!result) return;
    if (!isAuthenticated || !session?.access_token) {
      setSaveError(
        language === "ta"
          ? "அறிக்கையைச் சேமிக்க உள்நுழையவும்."
          : "Please log in to save this numerology report."
      );
      return;
    }

    setSaving(true);
    setSaveSuccess(null);
    setSaveError(null);

    try {
      await saveNumerologyReport(
        {
          person_name: result.family_name || familyName,
          birth_date: members[0]?.birth_date || "2026-01-01",
          method: "family" as any,
          system_convention: result.system_convention,
          calculation_data: result as any,
          interpretation_data: {
            overall_harmony_score: result.overall_family_harmony_score,
            overall_harmony_level: result.overall_family_harmony_level,
            synthesis: result.overall_synthesis,
            family_strengths: result.family_strengths,
            family_challenges: result.family_challenges,
            reflection_questions: result.reflection_questions,
          },
        },
        session.access_token
      );
      setSaveSuccess(
        language === "ta"
          ? "குடும்ப எண் கணித அறிக்கை வெற்றிகரமாகச் சேமிக்கப்பட்டது!"
          : "Family numerology report saved successfully!"
      );
    } catch (err: any) {
      setSaveError(err?.data?.detail || err?.message || "Failed to save report.");
    } finally {
      setSaving(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!result) return;
    setPdfDownloading(true);
    try {
      const blob = await exportNumerologyPdf(
        {
          person_name: result.family_name || familyName,
          birth_date: members[0]?.birth_date || "2026-01-01",
          method: "family",
          system_convention: result.system_convention,
          language: reportLang,
          calculation_data: result as any,
          interpretation_data: {
            overall_harmony_score: result.overall_family_harmony_score,
            overall_harmony_level: result.overall_family_harmony_level,
            synthesis: result.overall_synthesis,
            family_strengths: result.family_strengths,
            family_challenges: result.family_challenges,
          },
        },
        session?.access_token
      );
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `Family_Numerology_${result.family_name.replace(/\s+/g, "_")}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || "Failed to generate PDF.");
    } finally {
      setPdfDownloading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Title & Introduction */}
      <div className="bg-gradient-to-r from-amber-900/30 via-slate-900 to-indigo-950/40 p-6 md:p-8 rounded-2xl border border-amber-500/20 shadow-xl backdrop-blur-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <span className="p-2.5 bg-amber-500/10 rounded-xl border border-amber-500/30 text-amber-400">
                <Users className="w-6 h-6" />
              </span>
              <h1 className="text-2xl md:text-3xl font-bold text-white tracking-wide">
                {language === "ta" ? "குடும்ப & குழந்தை எண் கணித ஆய்வுக்கூடம்" : "Family & Baby Numerology Studio"}
              </h1>
            </div>
            <p className="mt-2 text-slate-300 text-sm md:text-base max-w-3xl leading-relaxed">
              {language === "ta"
                ? "பல தலைமுறை குடும்ப உறுப்பினர்களின் அதிர்வுகள், தாய்-தந்தை-குழந்தை இணக்கம், மற்றும் குழந்தைக்கான உன்னத பெயர் பரிந்துரைகளை ஒருங்கிணைக்கும் துல்லியமான எண் கணித ஆய்வு மையம்."
                : "Multi-generational family vibrational grid, parent-child nurturing harmony, and baby name numerology with deterministic Pythagorean & Chaldean phonetic scoring."}
            </p>
          </div>

          {/* System & Language controls */}
          <div className="flex flex-wrap items-center gap-3 bg-slate-900/80 p-2 rounded-xl border border-slate-700/60 self-start md:self-auto">
            <div>
              <label className="block text-[10px] uppercase font-semibold text-slate-400 mb-1">
                {language === "ta" ? "அமைப்பு" : "Convention"}
              </label>
              <select
                value={convention}
                onChange={(e) => setConvention(e.target.value as any)}
                className="bg-slate-800 text-xs text-amber-300 font-medium px-2.5 py-1.5 rounded-lg border border-slate-700 focus:outline-none focus:border-amber-500"
              >
                <option value="pythagorean">Pythagorean (1-9)</option>
                <option value="chaldean">Chaldean (1-8)</option>
              </select>
            </div>

            <div>
              <label className="block text-[10px] uppercase font-semibold text-slate-400 mb-1">
                {language === "ta" ? "மொழி" : "Report Lang"}
              </label>
              <select
                value={reportLang}
                onChange={(e) => setReportLang(e.target.value as any)}
                className="bg-slate-800 text-xs text-amber-300 font-medium px-2.5 py-1.5 rounded-lg border border-slate-700 focus:outline-none focus:border-amber-500"
              >
                <option value="en">English</option>
                <option value="ta">தமிழ் (Tamil)</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Main Studio Input Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Family Members & Setup (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-6 shadow-lg">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Users className="w-5 h-5 text-amber-400" />
                <h2 className="text-lg font-bold text-white">
                  {language === "ta" ? "1. குடும்ப உறுப்பினர்களின் விவரங்கள்" : "1. Family Group Profiles"}
                </h2>
              </div>
              <span className="text-xs text-slate-400 bg-slate-800 px-2.5 py-1 rounded-full border border-slate-700">
                {members.length} {language === "ta" ? "உறுப்பினர்கள்" : "Members"}
              </span>
            </div>

            {/* Family Name Input */}
            <div className="mb-5">
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                {language === "ta" ? "குடும்பத்தின் பெயர் / அடையாளம்" : "Family Group Identifier"}
              </label>
              <input
                type="text"
                value={familyName}
                onChange={(e) => setFamilyName(e.target.value)}
                placeholder="e.g., Sundaram Family"
                className="w-full bg-slate-950/80 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
              />
            </div>

            {/* Members Repeater List */}
            <div className="space-y-3">
              {members.map((m, idx) => (
                <div
                  key={m.id}
                  className="p-3.5 bg-slate-950/60 rounded-xl border border-slate-800/80 flex flex-col sm:flex-row items-start sm:items-center gap-3 hover:border-slate-700 transition"
                >
                  <div className="flex items-center justify-between w-full sm:w-auto gap-2">
                    <span className="w-6 h-6 rounded-full bg-amber-500/10 text-amber-400 flex items-center justify-center text-xs font-bold shrink-0">
                      {idx + 1}
                    </span>
                    <select
                      value={m.role}
                      onChange={(e) => handleUpdateMember(m.id, "role", e.target.value)}
                      className="bg-slate-900 text-xs text-amber-300 font-medium px-2 py-1.5 rounded-lg border border-slate-700 focus:outline-none focus:border-amber-500 shrink-0"
                    >
                      <option value="father">Father / தந்தை</option>
                      <option value="mother">Mother / தாய்</option>
                      <option value="parent">Parent / பெற்றோர்</option>
                      <option value="child">Child / குழந்தை</option>
                      <option value="baby">Baby / பச்சிளங்குழந்தை</option>
                      <option value="grandfather">Grandfather / தாத்தா</option>
                      <option value="grandmother">Grandmother / பாட்டி</option>
                      <option value="sibling">Sibling / உடன்பிறப்பு</option>
                      <option value="other">Household / உறுப்பினர்</option>
                    </select>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 flex-1 w-full">
                    <input
                      type="text"
                      placeholder="Name / பெயர்"
                      value={m.name}
                      onChange={(e) => handleUpdateMember(m.id, "name", e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
                    />
                    <input
                      type="date"
                      value={m.birth_date}
                      onChange={(e) => handleUpdateMember(m.id, "birth_date", e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                    />
                  </div>

                  {members.length > 1 && (
                    <button
                      type="button"
                      onClick={() => handleRemoveMember(m.id)}
                      className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition self-end sm:self-auto"
                      title="Remove Member"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>

            {/* Add Member CTA */}
            {members.length < 10 && (
              <button
                type="button"
                onClick={handleAddMember}
                className="mt-4 w-full py-2.5 px-4 bg-slate-800/70 hover:bg-slate-800 border border-dashed border-slate-700 hover:border-amber-500/50 rounded-xl text-xs font-semibold text-slate-300 hover:text-amber-300 flex items-center justify-center gap-2 transition"
              >
                <Plus className="w-4 h-4" />
                {language === "ta" ? "+ குடும்ப உறுப்பினரைச் சேர்" : "+ Add Another Member"}
              </button>
            )}
          </div>
        </div>

        {/* Right Column: Baby Name Studio & Variations (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-6 shadow-lg">
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-800">
              <Baby className="w-5 h-5 text-amber-400" />
              <h2 className="text-lg font-bold text-white">
                {language === "ta" ? "2. குழந்தை பெயர் ஆய்வு" : "2. Baby Name Resonance"}
              </h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  {language === "ta" ? "பரிசீலனைக்குரிய பெயர்கள் (கமாவால் பிரிக்கவும்)" : "Candidate Names (comma separated)"}
                </label>
                <textarea
                  rows={2}
                  value={babyCandidatesText}
                  onChange={(e) => setBabyCandidatesText(e.target.value)}
                  placeholder="e.g., Aarav, Advik, Kavin"
                  className="w-full bg-slate-950/80 border border-slate-700 rounded-xl p-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    {language === "ta" ? "குழந்தையின் பிறந்த தேதி (விருப்பத்தேர்வு)" : "Baby DOB (Optional)"}
                  </label>
                  <input
                    type="date"
                    value={babyDob}
                    onChange={(e) => setBabyDob(e.target.value)}
                    className="w-full bg-slate-950/80 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    {language === "ta" ? "குடும்பப் பெயர் / இனிஷியல்" : "Surname / Family Name"}
                  </label>
                  <input
                    type="text"
                    value={babySurname}
                    onChange={(e) => setBabySurname(e.target.value)}
                    placeholder="e.g., Sundaram"
                    className="w-full bg-slate-950/80 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    {language === "ta" ? "இலக்கு அதிர்வு எண் (1-9)" : "Target Root Number (1-9)"}
                  </label>
                  <select
                    value={targetRoot}
                    onChange={(e) => setTargetRoot(e.target.value)}
                    className="w-full bg-slate-950/80 border border-slate-700 rounded-xl px-3 py-2 text-xs text-amber-300 focus:outline-none focus:border-amber-500"
                  >
                    <option value="">Any Harmonious (ஏதேனும்)</option>
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((n) => (
                      <option key={n} value={n}>
                        Root {n}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex items-center gap-2 pt-5">
                  <input
                    type="checkbox"
                    id="auto-variations-toggle"
                    checked={generateSuggestions}
                    onChange={(e) => setGenerateSuggestions(e.target.checked)}
                    className="w-4 h-4 rounded text-amber-500 bg-slate-950 border-slate-700 focus:ring-0"
                  />
                  <label htmlFor="auto-variations-toggle" className="text-xs text-slate-300 cursor-pointer">
                    {language === "ta" ? "எழுத்து மாறுபாடுகள் பரிந்துரை" : "Auto Spelling Variations"}
                  </label>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="mt-6 pt-4 border-t border-slate-800 flex items-center gap-3">
              <button
                type="button"
                onClick={() => handleAnalyze()}
                disabled={loading}
                className="flex-1 py-3 px-4 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-950 font-bold rounded-xl shadow-lg flex items-center justify-center gap-2 transition disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>{language === "ta" ? "கணக்கிடுகிறது..." : "Analyzing Vibrations..."}</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>{language === "ta" ? "குடும்ப எண் கணித ஆய்வு" : "Analyze Family Numerology"}</span>
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={handleReset}
                disabled={loading}
                className="px-3.5 py-3 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold transition"
                title="Reset Inputs"
              >
                Reset
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl flex items-center gap-3 text-red-300 text-sm">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Result Presentation */}
      {result && (
        <div className="space-y-8 pt-4">
          {/* Executive Header Banner */}
          <div className="bg-gradient-to-br from-slate-900 via-indigo-950/40 to-slate-900 border border-amber-500/30 rounded-2xl p-6 md:p-8 shadow-2xl relative overflow-hidden">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div>
                <span className="text-xs uppercase tracking-widest font-bold text-amber-400">
                  {language === "ta" ? "முழுமையான குடும்ப ஆய்வு அறிக்கை" : "Family Vibrational Synthesis"}
                </span>
                <h2 className="text-2xl md:text-3xl font-extrabold text-white mt-1">
                  {result.family_name}
                </h2>
                <p className="mt-2 text-sm text-slate-300 max-w-3xl leading-relaxed">
                  {result.overall_synthesis}
                </p>
              </div>

              {/* Score pill */}
              <div className="flex flex-col items-center justify-center bg-slate-950/80 px-6 py-4 rounded-2xl border border-amber-500/30 shadow-inner text-center shrink-0">
                <span className="text-xs font-semibold text-slate-400 uppercase">
                  {language === "ta" ? "குடும்ப ஒற்றுமை" : "Family Harmony"}
                </span>
                <div className="text-3xl md:text-4xl font-black text-amber-400 mt-1">
                  {result.overall_family_harmony_score}%
                </div>
                <span className="text-[11px] font-bold text-emerald-400 mt-1 px-2.5 py-0.5 bg-emerald-500/10 rounded-full border border-emerald-500/20">
                  {result.overall_family_harmony_level}
                </span>
              </div>
            </div>

            {/* Quick Summary Cards (6 KPIs) */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mt-6 pt-6 border-t border-slate-800">
              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800 text-center">
                <span className="text-[10px] text-slate-400 uppercase font-bold">Members</span>
                <div className="text-lg font-extrabold text-white mt-0.5">
                  {result.members_evaluated.length}
                </div>
                <span className="text-[9px] text-slate-500">Profiled</span>
              </div>

              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800 text-center">
                <span className="text-[10px] text-slate-400 uppercase font-bold">Dominant</span>
                <div className="text-lg font-extrabold text-amber-400 mt-0.5">
                  {result.dominant_vibrations.length > 0 ? result.dominant_vibrations.join(", ") : "Balanced"}
                </div>
                <span className="text-[9px] text-slate-500">Core Roots</span>
              </div>

              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800 text-center">
                <span className="text-[10px] text-slate-400 uppercase font-bold">Leading Element</span>
                <div className="text-lg font-extrabold text-indigo-400 mt-0.5">
                  {result.elemental_balance?.dominant_element || "Balanced"}
                </div>
                <span className="text-[9px] text-slate-500">Element Matrix</span>
              </div>

              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800 text-center">
                <span className="text-[10px] text-slate-400 uppercase font-bold">Baby Names</span>
                <div className="text-lg font-extrabold text-emerald-400 mt-0.5">
                  {result.baby_name_candidates.length}
                </div>
                <span className="text-[9px] text-slate-500">Ranked</span>
              </div>

              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800 text-center">
                <span className="text-[10px] text-slate-400 uppercase font-bold">Pairs</span>
                <div className="text-lg font-extrabold text-purple-400 mt-0.5">
                  {result.pairwise_comparisons.length}
                </div>
                <span className="text-[9px] text-slate-500">Synergy Links</span>
              </div>

              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800 text-center">
                <span className="text-[10px] text-slate-400 uppercase font-bold">Missing</span>
                <div className="text-lg font-extrabold text-rose-400 mt-0.5">
                  {result.missing_vibrations.length > 0 ? result.missing_vibrations.join(", ") : "None"}
                </div>
                <span className="text-[9px] text-slate-500">Vibrational Gaps</span>
              </div>
            </div>

            {/* Action Bar (Save & PDF) */}
            <div className="mt-6 flex flex-wrap items-center gap-3 justify-end">
              <button
                type="button"
                onClick={handleSaveReport}
                disabled={saving}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl text-xs font-semibold text-white flex items-center gap-2 transition disabled:opacity-50"
              >
                {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4 text-amber-400" />}
                <span>{language === "ta" ? "அறிக்கையைச் சேமி" : "Save Report"}</span>
              </button>

              <button
                type="button"
                onClick={handleDownloadPdf}
                disabled={pdfDownloading}
                className="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold rounded-xl text-xs flex items-center gap-2 transition disabled:opacity-50"
              >
                {pdfDownloading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
                <span>{language === "ta" ? "PDF பதிவிறக்கம்" : "Download PDF Report"}</span>
              </button>
            </div>

            {saveSuccess && (
              <div className="mt-4 p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-xs text-emerald-300 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>{saveSuccess}</span>
              </div>
            )}
            {saveError && (
              <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-xl text-xs text-red-300 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{saveError}</span>
              </div>
            )}
          </div>

          {/* Section 1: Member Profiles Cards */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
              <Users className="w-5 h-5 text-amber-400" />
              <h3 className="text-lg font-bold text-white">
                {language === "ta" ? "குடும்ப உறுப்பினர்களின் அதிர்வு நிலைகள்" : "Individual Member Vibrational Profiles"}
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {result.members_evaluated.map((m) => (
                <div
                  key={m.id}
                  className="bg-slate-900/90 rounded-2xl border border-slate-800 p-5 shadow-lg relative flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs uppercase font-bold text-amber-400 tracking-wider">
                        {m.role}
                      </span>
                      <span className="text-[11px] font-semibold text-slate-400 bg-slate-800 px-2.5 py-0.5 rounded-full border border-slate-700">
                        {m.element}
                      </span>
                    </div>

                    <h4 className="text-lg font-bold text-white">{m.name}</h4>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {m.birth_date ? `DOB: ${m.birth_date}` : "DOB not provided"}
                    </p>

                    <div className="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-slate-800 text-center">
                      <div className="bg-slate-950/70 p-2 rounded-xl">
                        <span className="text-[10px] text-slate-400 block font-semibold">Mulank</span>
                        <span className="text-base font-bold text-amber-400">
                          {m.birth_psychic_number ?? "-"}
                        </span>
                      </div>
                      <div className="bg-slate-950/70 p-2 rounded-xl">
                        <span className="text-[10px] text-slate-400 block font-semibold">Bhagyank</span>
                        <span className="text-base font-bold text-indigo-400">
                          {m.life_path_number ?? "-"}
                        </span>
                      </div>
                      <div className="bg-slate-950/70 p-2 rounded-xl">
                        <span className="text-[10px] text-slate-400 block font-semibold">Name</span>
                        <span className="text-base font-bold text-emerald-400">
                          {m.expression_number ?? "-"}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-800/80">
                    <div className="text-[11px] text-slate-300 font-medium">
                      <span className="text-amber-400 font-semibold">{m.life_path_planet || m.birth_psychic_planet || "Cosmic"}</span> • {m.archetype}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Section 2: Baby Name Candidate Rankings (if any) */}
          {result.baby_name_candidates.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
                <Baby className="w-5 h-5 text-amber-400" />
                <h3 className="text-lg font-bold text-white">
                  {language === "ta" ? "குழந்தை பெயர் வேட்பாளர்கள் & தரவரிசை" : "Baby Name Candidates & Vibrational Rankings"}
                </h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {result.baby_name_candidates.map((cand, idx) => (
                  <div
                    key={`${cand.name}-${idx}`}
                    className="p-5 bg-slate-900/90 rounded-2xl border border-slate-800 shadow-lg flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="w-6 h-6 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center text-xs font-bold">
                            #{idx + 1}
                          </span>
                          <h4 className="text-lg font-bold text-white">{cand.name}</h4>
                        </div>
                        <span
                          className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${
                            cand.is_generated
                              ? "bg-purple-500/10 text-purple-300 border-purple-500/20"
                              : "bg-blue-500/10 text-blue-300 border-blue-500/20"
                          }`}
                        >
                          {cand.variation_type}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 gap-2 mt-3 text-xs">
                        <div className="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/80">
                          <span className="text-[10px] text-slate-400 block">Pythagorean</span>
                          <span className="font-bold text-amber-300">
                            Root {cand.pythagorean_expression} (Sum {cand.pythagorean_compound})
                          </span>
                        </div>
                        <div className="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/80">
                          <span className="text-[10px] text-slate-400 block">Chaldean</span>
                          <span className="font-bold text-indigo-300">
                            Root {cand.chaldean_expression} (Sum {cand.chaldean_compound})
                          </span>
                        </div>
                      </div>

                      <div className="grid grid-cols-4 gap-1.5 mt-2 text-center text-[10px]">
                        <div className="bg-slate-950/40 p-1.5 rounded-lg border border-slate-800/60">
                          <span className="text-slate-400 block">DOB</span>
                          <span className="font-bold text-slate-200">{cand.dob_harmony_score}%</span>
                        </div>
                        <div className="bg-slate-950/40 p-1.5 rounded-lg border border-slate-800/60">
                          <span className="text-slate-400 block">Parents</span>
                          <span className="font-bold text-slate-200">{cand.parent_harmony_score}%</span>
                        </div>
                        <div className="bg-slate-950/40 p-1.5 rounded-lg border border-slate-800/60">
                          <span className="text-slate-400 block">Phonetic</span>
                          <span className="font-bold text-slate-200">{cand.pronunciation_score}%</span>
                        </div>
                        <div className="bg-slate-950/40 p-1.5 rounded-lg border border-slate-800/60">
                          <span className="text-slate-400 block">Simplicity</span>
                          <span className="font-bold text-slate-200">{cand.simplicity_score}%</span>
                        </div>
                      </div>

                      <p className="mt-3 text-xs text-slate-300 leading-relaxed">
                        {cand.vibrational_synthesis}
                      </p>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between">
                      <span className="text-xs text-slate-400">
                        Planet: <strong className="text-white">{cand.ruling_planet}</strong>
                      </span>
                      <div className="flex items-center gap-1.5">
                        <span className="text-xs text-slate-400">Composite:</span>
                        <span className="text-base font-extrabold text-amber-400">
                          {cand.composite_score}/100
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Section 3: Pairwise Harmonization Dynamics */}
          {result.pairwise_comparisons.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
                <Heart className="w-5 h-5 text-amber-400" />
                <h3 className="text-lg font-bold text-white">
                  {language === "ta" ? "உறுப்பினர்களிடையேயான நல்லிணக்க உறவுகள்" : "Family Pairwise Compatibility Dynamics"}
                </h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {result.pairwise_comparisons.map((pair, idx) => (
                  <div
                    key={idx}
                    className="p-5 bg-slate-900/90 rounded-2xl border border-slate-800 shadow-lg space-y-3"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-base font-bold text-white">
                          {pair.person_a_name} ↔ {pair.person_b_name}
                        </h4>
                        <span className="text-xs text-slate-400 capitalize">
                          {pair.relationship_type}
                        </span>
                      </div>
                      <div className="text-right">
                        <span className="text-base font-extrabold text-amber-400">
                          {pair.composite_harmony_score}%
                        </span>
                        <span className="block text-[10px] font-semibold text-emerald-400">
                          {pair.harmony_level}
                        </span>
                      </div>
                    </div>

                    <div className="text-xs text-indigo-300 font-medium bg-indigo-950/30 p-2 rounded-xl border border-indigo-900/40">
                      {pair.planetary_dynamic}
                    </div>

                    {pair.shared_strengths.length > 0 && (
                      <div>
                        <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wide">
                          Shared Nurturing Strength:
                        </span>
                        <p className="text-xs text-slate-300 mt-0.5">{pair.shared_strengths[0]}</p>
                      </div>
                    )}

                    {pair.nurturing_prompt && (
                      <div className="bg-amber-500/10 p-3 rounded-xl border border-amber-500/20">
                        <span className="text-[10px] font-bold text-amber-300 uppercase tracking-wide flex items-center gap-1">
                          <Sparkles className="w-3 h-3" />
                          Mindful Dialogue Prompt:
                        </span>
                        <p className="text-xs text-amber-100/90 mt-1 italic">
                          "{pair.nurturing_prompt}"
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Section 4: 1-9 Distribution Grid & Elemental Balance */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
              <Compass className="w-5 h-5 text-amber-400" />
              <h3 className="text-lg font-bold text-white">
                {language === "ta" ? "1–9 அதிர்வுப் பகிர்வு & பஞ்சபூத சமநிலை" : "1–9 Vibration Distribution & Elemental Matrix"}
              </h3>
            </div>

            <div className="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-9 gap-2">
              {result.number_distribution.map((item) => (
                <div
                  key={item.number}
                  className={`p-3 rounded-xl border text-center transition ${
                    item.count > 0
                      ? "bg-slate-900 border-amber-500/30 shadow-md"
                      : "bg-slate-950/40 border-slate-800/60 opacity-60"
                  }`}
                >
                  <span className="text-xl font-black text-amber-400 block">{item.number}</span>
                  <span className="text-[11px] font-bold text-white block mt-0.5">
                    {item.count} {item.count === 1 ? "time" : "times"}
                  </span>
                  <span className="text-[9px] text-slate-400 block">{item.ruling_planet}</span>
                  <span className="text-[9px] text-indigo-300 block">{item.element}</span>
                </div>
              ))}
            </div>

            {/* Elemental Balance Bars */}
            {result.elemental_balance && (
              <div className="bg-slate-900/80 p-5 rounded-2xl border border-slate-800 grid grid-cols-2 sm:grid-cols-4 gap-4 text-center mt-3">
                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 flex items-center justify-center gap-3">
                  <Flame className="w-5 h-5 text-red-400" />
                  <div className="text-left">
                    <span className="text-[10px] text-slate-400 uppercase font-bold block">Fire / நெருப்பு</span>
                    <span className="text-base font-extrabold text-white">{result.elemental_balance.Fire || 0}</span>
                  </div>
                </div>

                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 flex items-center justify-center gap-3">
                  <Droplets className="w-5 h-5 text-blue-400" />
                  <div className="text-left">
                    <span className="text-[10px] text-slate-400 uppercase font-bold block">Water / நீர்</span>
                    <span className="text-base font-extrabold text-white">{result.elemental_balance.Water || 0}</span>
                  </div>
                </div>

                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 flex items-center justify-center gap-3">
                  <Wind className="w-5 h-5 text-teal-400" />
                  <div className="text-left">
                    <span className="text-[10px] text-slate-400 uppercase font-bold block">Air / காற்று</span>
                    <span className="text-base font-extrabold text-white">{result.elemental_balance.Air || 0}</span>
                  </div>
                </div>

                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 flex items-center justify-center gap-3">
                  <Layers className="w-5 h-5 text-amber-400" />
                  <div className="text-left">
                    <span className="text-[10px] text-slate-400 uppercase font-bold block">Earth / பூமி</span>
                    <span className="text-base font-extrabold text-white">{result.elemental_balance.Earth || 0}</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Section 5: Strengths, Challenges & Reflection Prompts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-6 shadow-lg space-y-4">
              <h4 className="text-base font-bold text-white flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                {language === "ta" ? "குடும்பத்தின் முதன்மை பலங்கள்" : "Collective Strengths & Synergies"}
              </h4>
              <ul className="space-y-2 text-xs text-slate-300">
                {result.family_strengths.map((str, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-emerald-400 font-bold">•</span>
                    <span>{str}</span>
                  </li>
                ))}
              </ul>

              {result.family_challenges.length > 0 && (
                <div className="pt-3 border-t border-slate-800">
                  <h4 className="text-base font-bold text-white flex items-center gap-2 mb-2">
                    <AlertCircle className="w-4 h-4 text-amber-400" />
                    {language === "ta" ? "வளர்ச்சிப் பகுதிகள் & சவால்கள்" : "Growth Edges & Vibrational Gaps"}
                  </h4>
                  <ul className="space-y-2 text-xs text-slate-300">
                    {result.family_challenges.map((cha, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-amber-400 font-bold">•</span>
                        <span>{cha}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-6 shadow-lg space-y-4">
              <h4 className="text-base font-bold text-white flex items-center gap-2">
                <HelpCircle className="w-4 h-4 text-indigo-400" />
                {language === "ta" ? "குடும்ப உரையாடலுக்கான சிந்தனை வினாக்கள்" : "Mindful Family Reflection Prompts"}
              </h4>
              <div className="space-y-3">
                {result.reflection_questions.map((q, i) => (
                  <div key={i} className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 text-xs text-slate-200">
                    <span className="text-amber-400 font-bold mr-1.5">{i + 1}.</span>
                    {q}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Ethical Disclaimer */}
          <div className="bg-slate-900/60 rounded-xl border border-slate-800 p-4 text-xs text-slate-400 flex items-start gap-3">
            <ShieldCheck className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            <p className="leading-relaxed">{result.disclaimer}</p>
          </div>
        </div>
      )}
    </div>
  );
}
