"use client";

import React, { useState, useEffect, useMemo } from "react";
import { useLanguage } from "@/lib/i18n";
import {
  NakshatraRitualItem,
  SannuKnowledgeOverviewResponse,
  SannuKarmaDiagnosticResponse,
} from "@/lib/types";
import {
  getSannuRitualsKnowledge,
  getNakshatraRituals,
  analyzeKarmaRituals,
} from "@/lib/api";
import {
  Sparkles,
  BookOpen,
  Flame,
  ShieldAlert,
  Moon,
  Sun,
  Compass,
  AlertTriangle,
  CheckCircle2,
  Search,
  Filter,
  Eye,
  Feather,
  Info,
  Calendar,
  Layers,
  ChevronRight,
  ExternalLink,
  Zap,
} from "lucide-react";

interface SannuRitualsExplorerProps {
  horoscopeId?: string | null;
  chartSnapshot?: Record<string, any> | null;
  initialDiagnostic?: SannuKarmaDiagnosticResponse | null;
}

export function SannuRitualsExplorer({
  horoscopeId,
  chartSnapshot,
  initialDiagnostic,
}: SannuRitualsExplorerProps) {
  const { language } = useLanguage();
  const isTa = language === "ta";

  // Data states
  const [knowledge, setKnowledge] = useState<SannuKnowledgeOverviewResponse | null>(null);
  const [nakshatras, setNakshatras] = useState<NakshatraRitualItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Active view tab inside Sannu module
  const [subTab, setSubTab] = useState<
    "nakshatras" | "karma_blueprint" | "propitiation_vs_empowerment" | "doshas" | "weak_planets" | "diagnostic"
  >(initialDiagnostic ? "diagnostic" : "nakshatras");

  // Nakshatra search & filter
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedElement, setSelectedElement] = useState<string>("all");
  const [selectedPlanet, setSelectedPlanet] = useState<string>("all");
  const [selectedNakshatra, setSelectedNakshatra] = useState<NakshatraRitualItem | null>(null);

  // Weak planet & house explorer states
  const [selectedWeakPlanet, setSelectedWeakPlanet] = useState<string>("sun");
  const [selectedHouse, setSelectedHouse] = useState<number>(1);

  // Personalized diagnostic state
  const [diagnostic, setDiagnostic] = useState<SannuKarmaDiagnosticResponse | null>(initialDiagnostic || null);
  const [loadingDiagnostic, setLoadingDiagnostic] = useState<boolean>(false);
  const [manualLagna, setManualLagna] = useState<string>("Aries");
  const [manualMoonSign, setManualMoonSign] = useState<string>("Aries");
  const [manualNakshatra, setManualNakshatra] = useState<string>("Ashwini");

  // Fetch initial knowledge and nakshatras
  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      try {
        setLoading(true);
        const [knowData, nakData] = await Promise.all([
          getSannuRitualsKnowledge(),
          getNakshatraRituals(),
        ]);
        if (isMounted) {
          setKnowledge(knowData);
          setNakshatras(nakData.items);
          if (nakData.items.length > 0) {
            setSelectedNakshatra(nakData.items[0]);
          }
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err?.message || "Failed to load rituals knowledge base");
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadData();
    return () => {
      isMounted = false;
    };
  }, []);

  // Fetch diagnostic if horoscopeId or chartSnapshot available
  useEffect(() => {
    if (initialDiagnostic) {
      setDiagnostic(initialDiagnostic);
      return;
    }
    if (horoscopeId || chartSnapshot) {
      setLoadingDiagnostic(true);
      analyzeKarmaRituals({
        horoscope_id: horoscopeId || undefined,
        chart_snapshot: chartSnapshot || undefined,
      })
        .then((res) => setDiagnostic(res))
        .catch((err) => console.warn("Failed to load karma diagnostic:", err))
        .finally(() => setLoadingDiagnostic(false));
    }
  }, [horoscopeId, chartSnapshot, initialDiagnostic]);

  const handleManualAnalyze = async () => {
    setLoadingDiagnostic(true);
    try {
      const res = await analyzeKarmaRituals({
        ascendant_sign: manualLagna,
        moon_sign: manualMoonSign,
        moon_nakshatra: manualNakshatra,
      });
      setDiagnostic(res);
      setSubTab("diagnostic");
    } catch (err: any) {
      setError(err?.message || "Diagnostic failed");
    } finally {
      setLoadingDiagnostic(false);
    }
  };

  // Filtered nakshatras
  const filteredNakshatras = useMemo(() => {
    return nakshatras.filter((n) => {
      const q = searchQuery.toLowerCase().trim();
      const matchQuery =
        !q ||
        n.name.toLowerCase().includes(q) ||
        n.name_ta.toLowerCase().includes(q) ||
        n.ruling_deity.toLowerCase().includes(q) ||
        n.symbol.toLowerCase().includes(q);

      const matchElement =
        selectedElement === "all" ||
        n.tattva.toLowerCase().includes(selectedElement.toLowerCase());

      const matchPlanet =
        selectedPlanet === "all" ||
        n.ruling_planet.toLowerCase() === selectedPlanet.toLowerCase();

      return matchQuery && matchElement && matchPlanet;
    });
  }, [nakshatras, searchQuery, selectedElement, selectedPlanet]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 space-y-4">
        <div className="w-10 h-10 border-4 border-amber-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-sm font-medium text-amber-300">
          {isTa ? "வேத சடங்குகள் & பரிகாரங்கள் ஏற்றப்படுகின்றன..." : "Loading Vedic Astrology Rituals & Remedies Knowledge..."}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* ─── Hero Book Banner ──────────────────────────────────────────────── */}
      <div className="relative overflow-hidden rounded-2xl border border-amber-500/30 bg-gradient-to-br from-amber-950/40 via-stone-900 to-amber-900/20 p-6 md:p-8 backdrop-blur-md shadow-2xl">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-3 max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 border border-amber-500/40 text-amber-300 text-xs font-semibold tracking-wider uppercase">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>Sannu Ahmed • Jyotish Sadhak • Seeker of Light</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-yellow-300 to-amber-400">
              {isTa
                ? "வேத ஜோதிட சடங்குகள் & கர்ம பரிகாரங்கள்"
                : "Vedic Astrology Rituals & Remedies: Powerful Protocols"}
            </h2>
            <p className="text-sm text-stone-300 leading-relaxed">
              {isTa
                ? "பிருஹத் பராசர ஹோரா சாஸ்திரம், ஜைமினி சூத்திரங்கள், சம்சுல் மஆரிப், பிகேட்ரிக்ஸ் மற்றும் தந்திர ரகசியங்களின் அடிப்படையில் கர்ம வினைகளைத் தீர்க்கும் முப்பரிமாண ஆன்மீக வழிகாட்டி."
                : "Synthesized from Brihat Parashara Hora Shastra, Jaimini Sutras, Atharvaveda, Shams al-Ma'arif, Picatrix, and Tantric treatises. Decode the soul's threefold karma, 27 Nakshatras sacred geometry, and the soul-body-energy circuit."}
            </p>
            <div className="flex flex-wrap items-center gap-2 pt-1 text-xs text-amber-400/90 font-medium">
              <span className="px-2.5 py-0.5 rounded bg-amber-900/50 border border-amber-700/50">3-Fold Karma</span>
              <span className="px-2.5 py-0.5 rounded bg-amber-900/50 border border-amber-700/50">27 Sacred Yantras</span>
              <span className="px-2.5 py-0.5 rounded bg-amber-900/50 border border-amber-700/50">Vedic Beeja Mantras</span>
              <span className="px-2.5 py-0.5 rounded bg-amber-900/50 border border-amber-700/50">Gandanta & Abhukta Mula Shanti</span>
              <span className="px-2.5 py-0.5 rounded bg-amber-900/50 border border-amber-700/50">Picatrix Safeguards</span>
            </div>
          </div>
          <div className="shrink-0 flex flex-col items-center justify-center p-4 rounded-xl bg-amber-900/30 border border-amber-500/30 text-center min-w-[160px]">
            <Flame className="w-8 h-8 text-amber-400 mb-2 animate-pulse" />
            <span className="text-xs font-semibold text-amber-200 uppercase tracking-wider">
              {isTa ? "ஆன்மீகத் தீர்வு" : "Soul Engineering"}
            </span>
            <span className="text-[11px] text-stone-400 mt-1">
              {isTa ? "விழிப்புணர்வு சடங்கு" : "Conscious Sadhana"}
            </span>
          </div>
        </div>
      </div>

      {/* ─── Navigation Sub-Tabs ───────────────────────────────────────────── */}
      <div className="flex flex-wrap items-center gap-2 p-1.5 rounded-xl bg-stone-900/80 border border-stone-800">
        {[
          { id: "nakshatras", label_en: "27 Nakshatra Rituals", label_ta: "27 நட்சத்திர சடங்குகள்", icon: Moon },
          { id: "karma_blueprint", label_en: "3-Fold Karma Blueprint", label_ta: "முப்பரிமாண கர்மா", icon: Layers },
          { id: "propitiation_vs_empowerment", label_en: "Propitiation vs. Empowerment", label_ta: "சாந்தி vs சக்தி பரிகாரம்", icon: ShieldAlert },
          { id: "doshas", label_en: "Nakshatra Doshas", label_ta: "நட்சத்திர தோஷங்கள்", icon: AlertTriangle },
          { id: "weak_planets", label_en: "Weak Planets & Houses", label_ta: "பலவீன கிரகங்கள் & பாவங்கள்", icon: Eye },
          { id: "diagnostic", label_en: "My Chart Diagnostic", label_ta: "என் ஜாதக கர்ம ஆய்வு", icon: Sparkles },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = subTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setSubTab(tab.id as any)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs md:text-sm font-medium transition-all ${
                isActive
                  ? "bg-amber-500 text-stone-950 font-semibold shadow-md shadow-amber-500/20"
                  : "text-stone-300 hover:text-amber-300 hover:bg-stone-800/60"
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? "text-stone-950" : "text-amber-400"}`} />
              <span>{isTa ? tab.label_ta : tab.label_en}</span>
            </button>
          );
        })}
      </div>

      {/* ─── TAB 1: 27 NAKSHATRA SACRED RITUALS ────────────────────────────── */}
      {subTab === "nakshatras" && (
        <div className="space-y-6">
          {/* Controls: Search and Filters */}
          <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4 p-4 rounded-xl bg-stone-900/60 border border-stone-800">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3.5 top-3 text-stone-400" />
              <input
                type="text"
                placeholder={isTa ? "நட்சத்திரம், அதிபதி, சின்னம் தேடுங்கள்..." : "Search by Nakshatra, Deity, Symbol, or Theme..."}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 text-xs md:text-sm bg-stone-950/80 border border-stone-700 rounded-lg text-stone-200 placeholder-stone-500 focus:outline-none focus:border-amber-500"
              />
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-2">
                <span className="text-xs text-stone-400">{isTa ? "தத்துவம்:" : "Element:"}</span>
                <select
                  value={selectedElement}
                  onChange={(e) => setSelectedElement(e.target.value)}
                  className="px-3 py-1.5 text-xs bg-stone-950 border border-stone-700 rounded-lg text-stone-200 focus:outline-none focus:border-amber-500"
                >
                  <option value="all">{isTa ? "அனைத்து தத்துவங்கள்" : "All Elements"}</option>
                  <option value="Earth">Earth (Prithvi)</option>
                  <option value="Water">Water (Apas)</option>
                  <option value="Fire">Fire (Agni)</option>
                  <option value="Air">Air (Vayu)</option>
                  <option value="Ether">Ether (Akasha)</option>
                </select>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-stone-400">{isTa ? "கிரகம்:" : "Ruler:"}</span>
                <select
                  value={selectedPlanet}
                  onChange={(e) => setSelectedPlanet(e.target.value)}
                  className="px-3 py-1.5 text-xs bg-stone-950 border border-stone-700 rounded-lg text-stone-200 focus:outline-none focus:border-amber-500"
                >
                  <option value="all">{isTa ? "அனைத்து கிரகங்கள்" : "All Planets"}</option>
                  <option value="ketu">Ketu</option>
                  <option value="venus">Venus</option>
                  <option value="sun">Sun</option>
                  <option value="moon">Moon</option>
                  <option value="mars">Mars</option>
                  <option value="rahu">Rahu</option>
                  <option value="jupiter">Jupiter</option>
                  <option value="saturn">Saturn</option>
                  <option value="mercury">Mercury</option>
                </select>
              </div>
            </div>
          </div>

          {/* Grid of Nakshatras & Detail Pane */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* List side */}
            <div className="lg:col-span-5 space-y-3 max-h-[700px] overflow-y-auto pr-1">
              {filteredNakshatras.map((n) => {
                const isSelected = selectedNakshatra?.number === n.number;
                return (
                  <div
                    key={n.number}
                    onClick={() => setSelectedNakshatra(n)}
                    className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                      isSelected
                        ? "bg-amber-500/15 border-amber-500 shadow-md shadow-amber-500/10"
                        : "bg-stone-900/60 border-stone-800 hover:border-amber-500/50 hover:bg-stone-800/40"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-3">
                        <span className="flex items-center justify-center w-7 h-7 rounded-full bg-amber-500/20 text-amber-300 font-bold text-xs border border-amber-500/40">
                          {n.number}
                        </span>
                        <div>
                          <div className="font-semibold text-sm text-stone-100 flex items-center gap-2">
                            <span>{n.name}</span>
                            <span className="text-xs text-amber-400/80 font-normal">({n.name_ta})</span>
                          </div>
                          <div className="text-[11px] text-stone-400">
                            {n.ruling_deity} • {n.ruling_planet.toUpperCase()}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="inline-block px-2 py-0.5 rounded text-[10px] font-medium bg-stone-800 border border-stone-700 text-stone-300">
                          {n.tattva.split(" ")[0]}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
              {filteredNakshatras.length === 0 && (
                <div className="p-8 text-center text-sm text-stone-500 bg-stone-900/40 rounded-xl border border-stone-800">
                  {isTa ? "பொருத்தமான நட்சத்திரங்கள் இல்லை." : "No nakshatras match your search filters."}
                </div>
              )}
            </div>

            {/* Selected Nakshatra Detail Card */}
            <div className="lg:col-span-7">
              {selectedNakshatra ? (
                <div className="p-6 rounded-2xl bg-stone-900/90 border border-amber-500/40 shadow-xl space-y-6 sticky top-6">
                  {/* Title & Metadata */}
                  <div className="flex items-start justify-between border-b border-stone-800 pb-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-amber-500 text-stone-950">
                          #{selectedNakshatra.number}
                        </span>
                        <h3 className="text-xl font-bold text-amber-200">
                          {selectedNakshatra.name} ({selectedNakshatra.name_ta})
                        </h3>
                      </div>
                      <p className="text-xs text-stone-400 mt-1">
                        {isTa ? "அதிபதி:" : "Ruler:"} <span className="text-amber-400 capitalize">{selectedNakshatra.ruling_planet}</span> •{" "}
                        {isTa ? "தெய்வம்:" : "Deity:"} <span className="text-amber-400">{selectedNakshatra.ruling_deity}</span>
                      </p>
                    </div>
                    <div className="text-right text-xs text-stone-400 space-y-0.5">
                      <div>{isTa ? "தத்துவம்:" : "Tattva:"} <span className="text-stone-200 font-medium">{selectedNakshatra.tattva}</span></div>
                      <div>{isTa ? "யோனி மிருகம்:" : "Yoni:"} <span className="text-stone-200 font-medium">{selectedNakshatra.animal_yoni}</span></div>
                    </div>
                  </div>

                  {/* Karmic Theme & Animal Instinct */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-3.5 rounded-xl bg-stone-950/70 border border-stone-800 space-y-1">
                      <div className="text-xs font-semibold text-amber-300 flex items-center gap-1.5">
                        <Compass className="w-3.5 h-3.5 text-amber-400" />
                        <span>{isTa ? "முற்பிறவி கர்ம மையக்கருத்து" : "Past-Life Karmic Theme"}</span>
                      </div>
                      <p className="text-xs text-stone-300 leading-relaxed">
                        {selectedNakshatra.karmic_theme}
                      </p>
                    </div>
                    <div className="p-3.5 rounded-xl bg-stone-950/70 border border-stone-800 space-y-1">
                      <div className="text-xs font-semibold text-amber-300 flex items-center gap-1.5">
                        <Feather className="w-3.5 h-3.5 text-amber-400" />
                        <span>{isTa ? "மிருக யோனி சுபாவம்" : "Yoni Instinct Pattern"}</span>
                      </div>
                      <p className="text-xs text-stone-300 leading-relaxed">
                        {selectedNakshatra.yoni_instinct}
                      </p>
                    </div>
                  </div>

                  {/* Symbol & Esoteric Meaning */}
                  <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/20 space-y-2">
                    <div className="flex items-center justify-between text-xs text-amber-300 font-semibold">
                      <span className="flex items-center gap-1.5">
                        <Eye className="w-3.5 h-3.5 text-amber-400" />
                        {isTa ? "புனித சின்னம்:" : "Sacred Symbol:"} {selectedNakshatra.symbol}
                      </span>
                      <span className="text-[11px] text-amber-400/80">
                        {isTa ? "மரம்:" : "Tree:"} {selectedNakshatra.sacred_tree}
                      </span>
                    </div>
                    <p className="text-xs text-stone-300 leading-relaxed italic">
                      "{selectedNakshatra.esoteric_symbol_meaning}"
                    </p>
                  </div>

                  {/* Sacred Geometry (Rekha) */}
                  <div className="p-4 rounded-xl bg-stone-950/80 border border-stone-800 space-y-2">
                    <div className="text-xs font-semibold text-amber-300 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                      <span>{isTa ? "யந்திர புனித வடிவம் (ரேகை)" : "Sacred Yantric Geometry (Rekha)"}</span>
                    </div>
                    <p className="text-xs text-stone-200 font-mono bg-stone-900/80 p-2.5 rounded-lg border border-stone-800">
                      {selectedNakshatra.sacred_geometry}
                    </p>
                  </div>

                  {/* Sound Remedy (Shabda / Beeja Mantra) */}
                  <div className="p-4 rounded-xl bg-gradient-to-r from-amber-950/40 to-stone-950 border border-amber-500/30 space-y-2 text-center">
                    <div className="text-xs font-semibold text-amber-300 uppercase tracking-wider">
                      {isTa ? "பீஜ ஒலி மந்திரம் (108 முறை ஜபம்)" : "Sacred Sound Code (Shabda Japa)"}
                    </div>
                    <div className="text-lg md:text-xl font-bold text-amber-200 tracking-wide">
                      {selectedNakshatra.sound_mantra}
                    </div>
                    {selectedNakshatra.sound_mantra_bija && (
                      <div className="text-sm font-semibold text-amber-400/90 font-mono">
                        {selectedNakshatra.sound_mantra_bija}
                      </div>
                    )}
                    <div className="text-xs text-stone-400">
                      {selectedNakshatra.sound_mantra_ta}
                    </div>
                  </div>

                  {/* Offerings (Dravya) & Practical Vidhi */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                    <div className="p-3.5 rounded-xl bg-stone-950/70 border border-stone-800 space-y-1">
                      <span className="font-semibold text-amber-300 flex items-center gap-1">
                        <Flame className="w-3.5 h-3.5 text-amber-400" />
                        {isTa ? "பரிகார சமர்ப்பணம் (திரவியம்):" : "Sacred Offerings (Dravya):"}
                      </span>
                      <p className="text-stone-300 leading-relaxed">
                        {selectedNakshatra.offerings_dravya}
                      </p>
                    </div>
                    <div className="p-3.5 rounded-xl bg-stone-950/70 border border-stone-800 space-y-1">
                      <span className="font-semibold text-amber-300 flex items-center gap-1">
                        <BookOpen className="w-3.5 h-3.5 text-amber-400" />
                        {isTa ? "அனுஷ்டான முறை (விதி):" : "Ritual Vidhi (Procedure):"}
                      </span>
                      <p className="text-stone-300 leading-relaxed">
                        {selectedNakshatra.ritual_procedure}
                      </p>
                    </div>
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        </div>
      )}

      {/* ─── TAB 2: 3-FOLD KARMA BLUEPRINT ─────────────────────────────────── */}
      {subTab === "karma_blueprint" && knowledge && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-stone-900/70 border border-stone-800 space-y-6">
            <div className="border-b border-stone-800 pb-4">
              <h3 className="text-xl font-bold text-amber-300">
                {isTa ? "முப்பரிமாண கர்மா கட்டமைப்பு (சஞ்சிதம், பிராரப்தம், கிரியாமாணம்)" : "The Threefold Karma Architecture in Vedic Metaphysics"}
              </h3>
              <p className="text-xs text-stone-400 mt-1">
                From Chapter 1: The Tailor's Workshop of the Soul. Action generates impressions (samskaras) stored in the subtle mind (citta).
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Sanchita */}
              <div className="p-5 rounded-xl bg-stone-950/80 border border-amber-500/20 space-y-3">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-purple-400" />
                  <h4 className="font-bold text-amber-200 text-sm">
                    {knowledge.karma_architecture.sanchita.title_en}
                  </h4>
                </div>
                <p className="text-xs text-stone-300 leading-relaxed">
                  {knowledge.karma_architecture.sanchita.nature}
                </p>
                <div className="p-3 rounded-lg bg-stone-900 text-xs border border-stone-800 text-purple-300 space-y-1">
                  <span className="font-semibold">{isTa ? "கரைக்கும் வழி:" : "Dissolution Path:"}</span>
                  <p className="text-stone-300 text-[11px]">
                    {knowledge.karma_architecture.sanchita.remedial_strategy_en}
                  </p>
                </div>
              </div>

              {/* Prarabdha */}
              <div className="p-5 rounded-xl bg-stone-950/80 border border-amber-500/40 space-y-3">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping" />
                  <h4 className="font-bold text-amber-200 text-sm">
                    {knowledge.karma_architecture.prarabdha.title_en}
                  </h4>
                </div>
                <p className="text-xs text-stone-300 leading-relaxed">
                  {knowledge.karma_architecture.prarabdha.nature}
                </p>
                <div className="p-2.5 rounded-lg bg-amber-950/20 border border-amber-500/20 text-[11px] space-y-1.5">
                  <div>
                    <span className="font-semibold text-amber-300">Acharaniya (Immutable):</span>
                    <span className="text-stone-400"> Parents, birth date, body limbs.</span>
                  </div>
                  <div>
                    <span className="font-semibold text-amber-300">Vasaniya (Modifiable):</span>
                    <span className="text-stone-400"> Diseases, mental habits, mitigated by Graha Shanti.</span>
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-stone-900 text-xs border border-stone-800 text-amber-300 space-y-1">
                  <span className="font-semibold">{isTa ? "தணிக்கும் வழி:" : "Alleviation Path:"}</span>
                  <p className="text-stone-300 text-[11px]">
                    {knowledge.karma_architecture.prarabdha.remedial_strategy_en}
                  </p>
                </div>
              </div>

              {/* Kriyamana */}
              <div className="p-5 rounded-xl bg-stone-950/80 border border-green-500/20 space-y-3">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
                  <h4 className="font-bold text-amber-200 text-sm">
                    {knowledge.karma_architecture.kriyamana.title_en}
                  </h4>
                </div>
                <p className="text-xs text-stone-300 leading-relaxed">
                  {knowledge.karma_architecture.kriyamana.nature}
                </p>
                <div className="p-2.5 rounded-lg bg-emerald-950/20 border border-emerald-500/20 text-[11px] space-y-1">
                  <span className="font-semibold text-emerald-300">Fluid & Volitional:</span>
                  <p className="text-stone-400">Punya seeds from service & japa; Papa seeds from greed & deceit.</p>
                </div>
                <div className="p-3 rounded-lg bg-stone-900 text-xs border border-stone-800 text-emerald-300 space-y-1">
                  <span className="font-semibold">{isTa ? "தடுக்கும் வழி:" : "Prevention Protocol:"}</span>
                  <p className="text-stone-300 text-[11px]">
                    {knowledge.karma_architecture.kriyamana.remedial_strategy_en}
                  </p>
                </div>
              </div>
            </div>

            {/* Soul-Body-Energy Circuit */}
            <div className="p-6 rounded-xl bg-stone-950/90 border border-stone-800 space-y-4">
              <h4 className="text-base font-bold text-amber-300 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-amber-400" />
                <span>The Soul-Body-Energy Circuit (Atma, Prana, Sharira & Breath)</span>
              </h4>
              <p className="text-xs text-stone-300 leading-relaxed">
                Why remedies actually work: they are not magical superstitions but subtle spiritual engineering. 
                Prana flows through 72,000 nadis carrying karmic scent into the physical vessel (Annamaya kosha) 
                and subtle minds (Manomaya / Vijnanamaya koshas). Conscious breath (Pranayama) acts as the bridge.
              </p>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3 pt-2">
                {knowledge.soul_body_circuit.remedial_mechanics.map((m: any, idx: number) => (
                  <div key={idx} className="p-3 rounded-lg bg-stone-900 border border-stone-800 text-center space-y-1">
                    <span className="text-xs font-bold text-amber-400">{m.tool}</span>
                    <p className="text-[10px] text-stone-400 leading-tight">{m.action}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ─── TAB 3: PROPITIATION VS EMPOWERMENT ────────────────────────────── */}
      {subTab === "propitiation_vs_empowerment" && knowledge && (
        <div className="space-y-6">
          {/* Picatrix Alert Banner */}
          <div className="p-5 rounded-xl bg-red-950/30 border border-red-500/40 text-red-200 text-xs md:text-sm flex items-start gap-3.5 shadow-lg">
            <ShieldAlert className="w-6 h-6 text-red-400 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <div className="font-bold text-red-300 uppercase tracking-wider text-xs">
                The Golden Warning (Picatrix & Brihat Parashara Hora Shastra)
              </div>
              <p className="text-stone-300 leading-relaxed font-serif text-sm italic">
                "{knowledge.propitiation_vs_empowerment.core_law}"
              </p>
              <p className="text-xs text-stone-400 pt-1">
                NEVER wear gemstones or perform amplifier rituals for an afflicted, debilitated, combust, or functional malefic planet! 
                Always pacify (Shanti) with Vedic Beeja Mantras, Dana (charity), and fasting first.
              </p>
            </div>
          </div>

          {/* 9 Grahas Vedic Beeja Mantras & Charity Table */}
          <div className="p-6 rounded-2xl bg-stone-900/80 border border-stone-800 space-y-4">
            <h3 className="text-lg font-bold text-amber-300 flex items-center gap-2">
              <Flame className="w-5 h-5 text-amber-400" />
              <span>Vedic Beeja Mantras & Planetary Dana (Charity) Table</span>
            </h3>
            <p className="text-xs text-stone-400">
              Chanted during the planet's Hora or Nakshatra day, mantra resonance multiplies 100 times per the Brihat Tantrasara.
            </p>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border border-stone-800 rounded-lg">
                <thead className="bg-stone-950 text-amber-300 border-b border-stone-800">
                  <tr>
                    <th className="p-3">Graha (Planet)</th>
                    <th className="p-3">Vedic Beeja Mantra</th>
                    <th className="p-3">Karmic Effect</th>
                    <th className="p-3">Prescribed Dana (Charitable Items)</th>
                    <th className="p-3">Spiritual Reason</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-800 text-stone-300">
                  {Object.entries(knowledge.propitiation_vs_empowerment.shanti_karmas.beeja_mantras).map(
                    ([planet, data]: [string, any]) => {
                      const charity = knowledge.propitiation_vs_empowerment.shanti_karmas.charity_items[planet];
                      return (
                        <tr key={planet} className="hover:bg-stone-800/40">
                          <td className="p-3 font-bold text-amber-200 capitalize">{planet}</td>
                          <td className="p-3 font-semibold font-mono text-amber-300">{data.mantra}</td>
                          <td className="p-3 text-stone-400">{data.effect}</td>
                          <td className="p-3 font-medium text-stone-200">{charity?.items}</td>
                          <td className="p-3 text-stone-400 italic">{charity?.spiritual_reason}</td>
                        </tr>
                      );
                    }
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Gemstone Rules & Shams al-Ma'arif Safeguard */}
          <div className="p-6 rounded-2xl bg-stone-900/80 border border-stone-800 space-y-4">
            <div className="flex items-center gap-2 border-b border-stone-800 pb-3">
              <Sparkles className="w-5 h-5 text-amber-400" />
              <h3 className="text-lg font-bold text-amber-300">
                Classical Gemstone Wearing Rules & Strict Safeguards
              </h3>
            </div>
            <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/30 text-xs text-amber-200 space-y-1">
              <span className="font-bold uppercase tracking-wider text-[11px] text-amber-400">
                Shams al-Ma'arif Eclipse Prohibition:
              </span>
              <p className="text-stone-300">
                {knowledge.propitiation_vs_empowerment.empowerment_karmas.lunar_eclipse_warning}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
              {Object.entries(knowledge.propitiation_vs_empowerment.empowerment_karmas.gemstone_rules_and_cautions).map(
                ([planet, gem]: [string, any]) => (
                  <div key={planet} className="p-4 rounded-xl bg-stone-950/90 border border-stone-800 space-y-2 text-xs">
                    <div className="flex items-center justify-between border-b border-stone-800 pb-1.5">
                      <span className="font-bold text-amber-300 capitalize">{planet}</span>
                      <span className="font-semibold text-stone-200">{gem.gem}</span>
                    </div>
                    <div className="text-[11px] text-stone-400">
                      <div>Metal: <span className="text-stone-300 font-medium">{gem.metal}</span></div>
                      <div>Finger: <span className="text-stone-300 font-medium">{gem.finger} Finger</span></div>
                    </div>
                    <div className="p-2 rounded bg-red-950/20 border border-red-500/20 text-red-300 text-[11px]">
                      <span className="font-bold">Caution: </span>{gem.caution}
                    </div>
                  </div>
                )
              )}
            </div>
          </div>
        </div>
      )}

      {/* ─── TAB 4: NAKSHATRA DOSHAS ───────────────────────────────────────── */}
      {subTab === "doshas" && knowledge && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-stone-900/80 border border-stone-800 space-y-6">
            <div className="border-b border-stone-800 pb-3">
              <h3 className="text-xl font-bold text-amber-300">
                {isTa ? "நட்சத்திர தோஷங்கள் & சாந்தி பரிகாரங்கள்" : "Nakshatra Doshas: Sacred Fault Lines & Shantis"}
              </h3>
              <p className="text-xs text-stone-400 mt-1">
                The ancient rishis recognized specific threshold zones where past violent, unfinished, or aborted karmas peak.
              </p>
            </div>

            {/* Gandanta Dosha */}
            <div className="p-5 rounded-xl bg-stone-950/90 border border-amber-500/30 space-y-4">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-amber-400" />
                <h4 className="text-base font-bold text-amber-200">
                  {knowledge.nakshatra_doshas.gandanta.title_en}
                </h4>
              </div>
              <p className="text-xs text-stone-300 leading-relaxed">
                Gandanta literally means "the knot at the end". It occurs at the delicate junction between a watery nakshatra and a fiery nakshatra 
                (spanning the final 3°20' of water and initial 3°20' of fire). Here the emotional karma of the past collides with future transformational fire.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1">
                {knowledge.nakshatra_doshas.gandanta.junctions.map((j: any, idx: number) => (
                  <div key={idx} className="p-3.5 rounded-lg bg-stone-900 border border-stone-800 space-y-1.5 text-xs">
                    <span className="font-bold text-amber-300">{j.water_nakshatra} ➔ {j.fire_nakshatra}</span>
                    <div className="text-[11px] text-stone-400">Span: {j.span}</div>
                    <div className="text-[11px] text-stone-300 font-medium">Deities: {j.shanti_deity}</div>
                    <p className="text-[10px] text-stone-400 italic">{j.remedy}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Abhukta Mula Dosha */}
            <div className="p-5 rounded-xl bg-stone-950/90 border border-red-500/30 space-y-3">
              <div className="flex items-center gap-2">
                <Flame className="w-5 h-5 text-red-400" />
                <h4 className="text-base font-bold text-red-200">
                  {knowledge.nakshatra_doshas.abhukta_mula.title_en}
                </h4>
              </div>
              <p className="text-xs text-stone-300 leading-relaxed">
                The first 00°00' to 13°20' of Mula Nakshatra in Sagittarius is ruled by Goddess Nirriti (Dissolution). 
                Birth here carries the weight of root-level upheaval and deep ancestral curses.
              </p>
              <div className="p-3.5 rounded-lg bg-stone-900 border border-stone-800 space-y-2 text-xs">
                <span className="font-semibold text-amber-300">Mandatory Classical Shanti Vidhi:</span>
                <ul className="list-disc pl-5 space-y-1 text-stone-300 text-xs">
                  {knowledge.nakshatra_doshas.abhukta_mula.mandatory_shanti.map((s: string, idx: number) => (
                    <li key={idx}>{s}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Vishaghati Nakshatras */}
            <div className="p-5 rounded-xl bg-stone-950/90 border border-purple-500/30 space-y-3">
              <div className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-purple-400" />
                <h4 className="text-base font-bold text-purple-200">
                  {knowledge.nakshatra_doshas.vishaghati.title_en}
                </h4>
              </div>
              <p className="text-xs text-stone-300 leading-relaxed">
                Five nakshatras ({knowledge.nakshatra_doshas.vishaghati.vulnerable_nakshatras.join(", ")}) 
                are designated as Vishaghati channels where astral nadis are susceptible to psychic poisoning and ancestral distress.
              </p>
              <p className="text-xs text-stone-400 font-mono bg-stone-900 p-2.5 rounded-lg border border-stone-800">
                Remedy: {knowledge.nakshatra_doshas.vishaghati.shanti_procedure}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ─── TAB 5: WEAK PLANETS & 12 HOUSES ───────────────────────────────── */}
      {subTab === "weak_planets" && knowledge && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-stone-900/80 border border-stone-800 space-y-6">
            <div className="border-b border-stone-800 pb-3">
              <h3 className="text-xl font-bold text-amber-300">
                {isTa ? "பலவீன கிரகங்களின் மன & கர்ம அறிகுறிகள்" : "Psychological & Karmic Symptoms of Weak Planets"}
              </h3>
              <p className="text-xs text-stone-400 mt-1">
                Planetary weakness begins not in external fate, but in internal consciousness frequency before solidifying into life events.
              </p>
            </div>

            {/* Planet Selector */}
            <div className="flex flex-wrap items-center gap-2">
              {Object.keys(knowledge.planetary_weakness_atlas).map((p) => (
                <button
                  key={p}
                  onClick={() => setSelectedWeakPlanet(p)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition-all ${
                    selectedWeakPlanet === p
                      ? "bg-amber-500 text-stone-950 shadow-md shadow-amber-500/20"
                      : "bg-stone-950 border border-stone-800 text-stone-300 hover:border-amber-500/50"
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>

            {/* Selected Weak Planet Card */}
            {knowledge.planetary_weakness_atlas[selectedWeakPlanet] && (
              <div className="p-5 rounded-xl bg-stone-950/90 border border-amber-500/30 space-y-4">
                <div className="border-b border-stone-800 pb-2">
                  <h4 className="text-lg font-bold text-amber-200">
                    {knowledge.planetary_weakness_atlas[selectedWeakPlanet].title_en}
                  </h4>
                  <p className="text-xs text-amber-400/90 font-medium mt-0.5">
                    {knowledge.planetary_weakness_atlas[selectedWeakPlanet].theme}
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  <div className="p-3.5 rounded-lg bg-stone-900 border border-stone-800 space-y-2">
                    <span className="font-bold text-amber-300 flex items-center gap-1.5">
                      <Eye className="w-3.5 h-3.5 text-amber-400" />
                      Psychological Symptoms
                    </span>
                    <ul className="list-disc pl-4 space-y-1 text-stone-300">
                      {knowledge.planetary_weakness_atlas[selectedWeakPlanet].psychological_symptoms.map(
                        (s: string, idx: number) => (
                          <li key={idx}>{s}</li>
                        )
                      )}
                    </ul>
                  </div>

                  <div className="p-3.5 rounded-lg bg-stone-900 border border-stone-800 space-y-2">
                    <span className="font-bold text-amber-300 flex items-center gap-1.5">
                      <Compass className="w-3.5 h-3.5 text-amber-400" />
                      Outer Karmic Symptoms
                    </span>
                    <ul className="list-disc pl-4 space-y-1 text-stone-300">
                      {knowledge.planetary_weakness_atlas[selectedWeakPlanet].karmic_symptoms.map(
                        (s: string, idx: number) => (
                          <li key={idx}>{s}</li>
                        )
                      )}
                    </ul>
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-amber-950/20 border border-amber-500/20 text-xs text-stone-300">
                  <span className="font-bold text-amber-400">Tantric Insight: </span>
                  {knowledge.planetary_weakness_atlas[selectedWeakPlanet].tantric_insight}
                </div>
              </div>
            )}

            {/* 12 Houses Weakness Explorer */}
            <div className="pt-4 border-t border-stone-800 space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-bold text-amber-300">
                  How Different Houses (1st to 12th) Alter Weakness Expression
                </h4>
                <div className="flex items-center gap-1 overflow-x-auto max-w-md">
                  {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((h) => (
                    <button
                      key={h}
                      onClick={() => setSelectedHouse(h)}
                      className={`w-7 h-7 rounded text-xs font-bold transition-all ${
                        selectedHouse === h
                          ? "bg-amber-500 text-stone-950"
                          : "bg-stone-950 text-stone-400 hover:text-stone-100"
                      }`}
                    >
                      {h}
                    </button>
                  ))}
                </div>
              </div>

              {knowledge.house_weakness_manifestation[String(selectedHouse)] && (
                <div className="p-4 rounded-xl bg-stone-950/90 border border-stone-800 space-y-2 text-xs">
                  <div className="font-bold text-amber-200">
                    House {selectedHouse}: {knowledge.house_weakness_manifestation[String(selectedHouse)].bhava_name}
                  </div>
                  <p className="text-stone-300 leading-relaxed">
                    {knowledge.house_weakness_manifestation[String(selectedHouse)].impact_en}
                  </p>
                  <p className="text-stone-400 italic text-[11px]">
                    Tantric Key: {knowledge.house_weakness_manifestation[String(selectedHouse)].tantric_key}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ─── TAB 6: MY CHART KARMA DIAGNOSTIC ──────────────────────────────── */}
      {subTab === "diagnostic" && (
        <div className="space-y-6">
          {/* If diagnostic is already computed */}
          {diagnostic ? (
            <div className="space-y-6">
              {/* Moon Nakshatra Sacred Profile Header */}
              {diagnostic.moon_nakshatra_ritual && (
                <div className="p-6 rounded-2xl bg-gradient-to-r from-amber-950/40 via-stone-900 to-stone-950 border border-amber-500/40 space-y-4 shadow-xl">
                  <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-stone-800 pb-4">
                    <div>
                      <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 text-xs font-semibold mb-1">
                        <Moon className="w-3.5 h-3.5" />
                        <span>Your Karmic Container (Birth Nakshatra)</span>
                      </div>
                      <h3 className="text-2xl font-bold text-amber-200">
                        {diagnostic.moon_nakshatra_ritual.name} ({diagnostic.moon_nakshatra_ritual.name_ta})
                      </h3>
                      <p className="text-xs text-stone-400">
                        Deity: <span className="text-amber-400">{diagnostic.moon_nakshatra_ritual.ruling_deity}</span> •{" "}
                        Yoni: <span className="text-amber-400">{diagnostic.moon_nakshatra_ritual.animal_yoni}</span> •{" "}
                        Element: <span className="text-amber-400">{diagnostic.moon_nakshatra_ritual.tattva}</span>
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-xs font-bold text-amber-400 uppercase tracking-wider">Symbol</div>
                      <div className="text-sm font-semibold text-stone-200">{diagnostic.moon_nakshatra_ritual.symbol}</div>
                    </div>
                  </div>

                  {/* Sacred Geometry & Mantra */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                    <div className="p-3.5 rounded-xl bg-stone-950/80 border border-stone-800 space-y-1.5">
                      <span className="font-semibold text-amber-300 flex items-center gap-1.5">
                        <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                        Sacred Geometry (Rekha)
                      </span>
                      <p className="text-stone-300 font-mono text-xs">
                        {diagnostic.moon_nakshatra_ritual.sacred_geometry}
                      </p>
                    </div>
                    <div className="p-3.5 rounded-xl bg-stone-950/80 border border-stone-800 space-y-1.5 text-center">
                      <span className="font-semibold text-amber-300 uppercase tracking-wider text-[11px]">
                        Prescribed Sound Code (108 Japa)
                      </span>
                      <div className="text-base font-bold text-amber-200">
                        {diagnostic.moon_nakshatra_ritual.sound_mantra}
                      </div>
                      <div className="text-[11px] text-stone-400">
                        {diagnostic.moon_nakshatra_ritual.sound_mantra_ta}
                      </div>
                    </div>
                  </div>

                  {/* Offerings and Procedure */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                    <div className="p-3.5 rounded-xl bg-stone-950/80 border border-stone-800 space-y-1">
                      <span className="font-semibold text-amber-300">Sacred Offerings (Dravya):</span>
                      <p className="text-stone-300">{diagnostic.moon_nakshatra_ritual.offerings_dravya}</p>
                    </div>
                    <div className="p-3.5 rounded-xl bg-stone-950/80 border border-stone-800 space-y-1">
                      <span className="font-semibold text-amber-300">Ritual Vidhi (Procedure):</span>
                      <p className="text-stone-300">{diagnostic.moon_nakshatra_ritual.ritual_procedure}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Detected Nakshatra Doshas */}
              {diagnostic.detected_nakshatra_doshas.length > 0 && (
                <div className="p-6 rounded-2xl bg-red-950/20 border border-red-500/40 space-y-4 shadow-xl">
                  <div className="flex items-center gap-2 text-red-300 font-bold text-base">
                    <AlertTriangle className="w-5 h-5 text-red-400" />
                    <span>Detected Nakshatra Doshas & Required Shantis</span>
                  </div>
                  <div className="space-y-3">
                    {diagnostic.detected_nakshatra_doshas.map((d, idx) => (
                      <div key={idx} className="p-4 rounded-xl bg-stone-950/90 border border-red-500/30 space-y-2 text-xs">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-red-300 text-sm">{d.title_en}</span>
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-red-900/60 text-red-200 border border-red-700">
                            {d.severity}
                          </span>
                        </div>
                        <p className="text-stone-300 leading-relaxed">{d.description_en}</p>
                        <div className="p-2.5 rounded bg-red-950/40 border border-red-700/40 text-amber-200 space-y-1">
                          <span className="font-semibold">Prescribed Shanti Vidhi: </span>
                          <span>{d.shanti_procedure_en}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Threefold Karma Action Blueprint */}
              <div className="p-6 rounded-2xl bg-stone-900/80 border border-stone-800 space-y-4">
                <h4 className="text-base font-bold text-amber-300 flex items-center gap-2">
                  <Layers className="w-4 h-4 text-amber-400" />
                  <span>Your 3-Pronged Karma Action Blueprint</span>
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                  {/* Sanchita */}
                  <div className="p-4 rounded-xl bg-stone-950 border border-stone-800 space-y-2">
                    <span className="font-bold text-purple-300">1. Sanchita (Latent Debt)</span>
                    <p className="text-stone-400 text-[11px]">{diagnostic.threefold_karma_blueprint.sanchita.summary_en}</p>
                    <div className="space-y-1">
                      {diagnostic.threefold_karma_blueprint.sanchita.markers.map((m: any, i: number) => (
                        <div key={i} className="text-stone-300 text-[11px] bg-stone-900 p-1.5 rounded">
                          • {m.factor}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Prarabdha */}
                  <div className="p-4 rounded-xl bg-stone-950 border border-amber-500/30 space-y-2">
                    <span className="font-bold text-amber-300">2. Prarabdha (Active Impact)</span>
                    <p className="text-stone-400 text-[11px]">{diagnostic.threefold_karma_blueprint.prarabdha.summary_en}</p>
                    <div className="space-y-1">
                      {diagnostic.threefold_karma_blueprint.prarabdha.markers.map((m: any, i: number) => (
                        <div key={i} className="text-stone-300 text-[11px] bg-stone-900 p-1.5 rounded">
                          • {m.factor}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Kriyamana */}
                  <div className="p-4 rounded-xl bg-stone-950 border border-emerald-500/30 space-y-2">
                    <span className="font-bold text-emerald-300">3. Kriyamana (Future Prevention)</span>
                    <div className="space-y-1.5">
                      {diagnostic.threefold_karma_blueprint.kriyamana.protocol.map((pr: any, i: number) => (
                        <div key={i} className="text-[11px] bg-stone-900 p-2 rounded border border-stone-800">
                          <div className="font-semibold text-emerald-200">{pr.practice}</div>
                          <div className="text-stone-400 text-[10px]">{pr.cadence}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Propitiation vs Empowerment Status for Chart */}
              <div className="p-6 rounded-2xl bg-stone-900/80 border border-stone-800 space-y-4">
                <h4 className="text-base font-bold text-amber-300 flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 text-amber-400" />
                  <span>Chart Planets: Propitiation vs. Empowerment Classification</span>
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {diagnostic.propitiation_vs_empowerment_status.map((item, idx) => (
                    <div
                      key={idx}
                      className={`p-3.5 rounded-xl border text-xs space-y-1.5 ${
                        item.action_type === "propitiation_only"
                          ? "bg-red-950/20 border-red-500/30"
                          : "bg-emerald-950/20 border-emerald-500/30"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-stone-100 capitalize">{item.graha}</span>
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                            item.action_type === "propitiation_only"
                              ? "bg-red-900/60 text-red-200 border border-red-700"
                              : "bg-emerald-900/60 text-emerald-200 border border-emerald-700"
                          }`}
                        >
                          {item.action_type === "propitiation_only" ? "Propitiate (Shanti)" : "Empower (Shakti)"}
                        </span>
                      </div>
                      <p className="text-[11px] text-stone-300 leading-tight">{item.justification_en}</p>
                      {item.beeja_mantra && (
                        <div className="text-[11px] font-mono text-amber-300 pt-1">
                          Mantra: {item.beeja_mantra.mantra}
                        </div>
                      )}
                      {item.charity_prescribed && (
                        <div className="text-[10px] text-stone-400">
                          Donate: {item.charity_prescribed.items}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            /* Manual Chart Entry Form */
            <div className="p-8 rounded-2xl bg-stone-900/80 border border-stone-800 space-y-6 max-w-xl mx-auto text-center">
              <div className="space-y-2">
                <Sparkles className="w-10 h-10 text-amber-400 mx-auto" />
                <h3 className="text-xl font-bold text-amber-200">
                  {isTa ? "உங்கள் ஜாதக கர்ம ஆய்வு" : "Generate Sannu Ahmed Karma Diagnostic"}
                </h3>
                <p className="text-xs text-stone-400">
                  Select your Ascendant, Moon Sign, and Moon Nakshatra to evaluate your 3-fold karma, 
                  sacred geometry ritual, and nakshatra doshas.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-left">
                <div>
                  <label className="text-xs text-stone-400 mb-1 block">Ascendant (Lagna)</label>
                  <select
                    value={manualLagna}
                    onChange={(e) => setManualLagna(e.target.value)}
                    className="w-full px-3 py-2 text-xs bg-stone-950 border border-stone-700 rounded-lg text-stone-200"
                  >
                    {["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"].map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-xs text-stone-400 mb-1 block">Moon Sign (Rasi)</label>
                  <select
                    value={manualMoonSign}
                    onChange={(e) => setManualMoonSign(e.target.value)}
                    className="w-full px-3 py-2 text-xs bg-stone-950 border border-stone-700 rounded-lg text-stone-200"
                  >
                    {["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"].map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-xs text-stone-400 mb-1 block">Moon Nakshatra</label>
                  <select
                    value={manualNakshatra}
                    onChange={(e) => setManualNakshatra(e.target.value)}
                    className="w-full px-3 py-2 text-xs bg-stone-950 border border-stone-700 rounded-lg text-stone-200"
                  >
                    {nakshatras.map((n) => (
                      <option key={n.number} value={n.name}>{n.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              <button
                onClick={handleManualAnalyze}
                disabled={loadingDiagnostic}
                className="w-full py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-stone-950 font-bold text-sm transition-all shadow-lg shadow-amber-500/20 disabled:opacity-50"
              >
                {loadingDiagnostic ? "Diagnosing Karma & Rituals..." : "Analyze Karma & Sacred Rituals"}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
