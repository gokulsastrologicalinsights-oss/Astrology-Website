"use client";

import React, { useState, useEffect, useMemo } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  getTamilSastraDailyGuidance,
  getTamilSastraMedicalDeities,
  getTamilSastraLifeWishes,
  getTamilSastraRamayanaParayanam,
  getTamilSastraNavagrahaCatalog,
  getTamilSastraDasaPariharams,
  getTamilSastraVastuTimings,
  getTamilSastraVastuRules,
  getTamilSastraSpecialMuhurtas,
} from "@/lib/api";
import {
  Compass,
  Calendar,
  Sparkles,
  Heart,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Info,
  Flame,
  Search,
  BookOpen,
  Building,
  HelpCircle,
  Home,
  Clock,
  Sun,
  Moon,
  ChevronRight,
  Filter,
  CheckSquare,
} from "lucide-react";

type ActiveTab =
  | "daily"
  | "medical"
  | "wishes"
  | "vastu"
  | "muhurta"
  | "navagraha"
  | "dharma";

export default function DailySastraPage() {
  const { language } = useLanguage();
  const isTa = language === "ta";

  const [activeTab, setActiveTab] = useState<ActiveTab>("daily");

  // Daily guidance state
  const [selectedDate, setSelectedDate] = useState<string>("");
  const [dailyData, setDailyData] = useState<any>(null);
  const [loadingDaily, setLoadingDaily] = useState(false);

  // Initialize date on client mount
  useEffect(() => {
    setSelectedDate(new Date().toISOString().split("T")[0]);
  }, []);

  // Medical deities state
  const [medicalDeities, setMedicalDeities] = useState<any[]>([]);
  const [medicalSearch, setMedicalSearch] = useState("");
  const [medicalCategory, setMedicalCategory] = useState("all");

  // Life wishes & Ramayana
  const [lifeWishes, setLifeWishes] = useState<any[]>([]);
  const [ramayanaGuide, setRamayanaGuide] = useState<any[]>([]);
  const [wishesSearch, setWishesSearch] = useState("");

  // Vastu state
  const [vastuTimings, setVastuTimings] = useState<any[]>([]);
  const [vastuRules, setVastuRules] = useState<any[]>([]);
  const [vastuCategory, setVastuCategory] = useState("all");

  // Navagraha & Special Muhurta
  const [navagrahas, setNavagrahas] = useState<any[]>([]);
  const [dasaPariharams, setDasaPariharams] = useState<any[]>([]);
  const [specialMuhurtas, setSpecialMuhurtas] = useState<any>(null);

  // Load Daily Guidance on date change
  useEffect(() => {
    if (!selectedDate) return;
    async function loadDaily() {
      setLoadingDaily(true);
      try {
        const res = await getTamilSastraDailyGuidance({ date: selectedDate });
        setDailyData(res);
      } catch (err) {
        console.error("Failed to load daily guidance:", err);
      } finally {
        setLoadingDaily(false);
      }
    }
    loadDaily();
  }, [selectedDate]);

  // Load supporting static datasets once
  useEffect(() => {
    async function loadAllDatasets() {
      try {
        const [med, wish, ram, nava, dasa, vTim, vRul, sMuh] = await Promise.all([
          getTamilSastraMedicalDeities(),
          getTamilSastraLifeWishes(),
          getTamilSastraRamayanaParayanam(),
          getTamilSastraNavagrahaCatalog(),
          getTamilSastraDasaPariharams(),
          getTamilSastraVastuTimings(),
          getTamilSastraVastuRules(),
          getTamilSastraSpecialMuhurtas(),
        ]);
        setMedicalDeities(med || []);
        setLifeWishes(wish || []);
        setRamayanaGuide(ram || []);
        setNavagrahas(nava || []);
        setDasaPariharams(dasa || []);
        setVastuTimings(vTim || []);
        setVastuRules(vRul || []);
        setSpecialMuhurtas(sMuh || {});
      } catch (err) {
        console.error("Failed to load Sastra datasets:", err);
      }
    }
    loadAllDatasets();
  }, []);

  // Filtered Medical
  const filteredMedical = useMemo(() => {
    return medicalDeities.filter((item) => {
      const matchCat =
        medicalCategory === "all" || item.category === medicalCategory;
      const q = medicalSearch.toLowerCase();
      const matchSearch =
        !q ||
        item.disease_ta.includes(q) ||
        item.disease_en.toLowerCase().includes(q) ||
        item.deity_ta.includes(q) ||
        item.deity_en.toLowerCase().includes(q);
      return matchCat && matchSearch;
    });
  }, [medicalDeities, medicalSearch, medicalCategory]);

  // Filtered Wishes
  const filteredWishes = useMemo(() => {
    if (!wishesSearch) return lifeWishes;
    const q = wishesSearch.toLowerCase();
    return lifeWishes.filter(
      (w) =>
        w.goal_ta.includes(q) ||
        w.goal_en.toLowerCase().includes(q) ||
        w.deity_ta.includes(q) ||
        w.deity_en.toLowerCase().includes(q)
    );
  }, [lifeWishes, wishesSearch]);

  // Filtered Ramayana
  const filteredRamayana = useMemo(() => {
    if (!wishesSearch) return ramayanaGuide;
    const q = wishesSearch.toLowerCase();
    return ramayanaGuide.filter(
      (r) =>
        r.purpose_ta.includes(q) ||
        r.purpose_en.toLowerCase().includes(q) ||
        r.sarga_title_ta.includes(q) ||
        r.sarga_title_en.toLowerCase().includes(q)
    );
  }, [ramayanaGuide, wishesSearch]);

  // Filtered Vastu Rules
  const filteredVastuRules = useMemo(() => {
    if (vastuCategory === "all") return vastuRules;
    return vastuRules.filter((r) => r.category === vastuCategory);
  }, [vastuRules, vastuCategory]);

  return (
    <div className="min-h-screen bg-[#F4F6F9] py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <Breadcrumbs
          items={[
            { label: isTa ? "முகப்பு" : "Home", href: "/" },
            { label: isTa ? "ஜோதிட கருவிகள்" : "Astrology Tools", href: "/tools" },
            { label: isTa ? "தினசரி சாஸ்திர வழிகாட்டி" : "Daily Sastra Guide" },
          ]}
        />

        {/* Header Banner */}
        <div className="bg-gradient-to-r from-[#1B365D] via-[#2A4D7C] to-[#1B365D] text-white rounded-2xl p-6 sm:p-8 shadow-lg border border-[#B4872B]/30 relative overflow-hidden">
          <div className="absolute right-0 top-0 translate-x-12 -translate-y-12 w-64 h-64 bg-[#B4872B]/10 rounded-full blur-2xl pointer-events-none" />
          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#FAF2DE]/20 text-[#FAF2DE] text-xs font-semibold uppercase tracking-wider mb-3">
                <Sparkles className="w-3.5 h-3.5 text-[#B4872B]" />
                {isTa ? "பஞ்சாங்கம் & தர்ம சாஸ்திரம்" : "Panchangam & Dharma Sastra"}
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
                {isTa
                  ? "தினசரி வாழ்வில் செய்யக்கூடாதவையும் செய்ய வேண்டியவையும்"
                  : "Daily Dharma & Astrology Sastra Guide"}
              </h1>
              <p className="mt-2 text-sm sm:text-base text-gray-200 max-w-3xl leading-relaxed">
                {isTa
                  ? "இந்து மதமும் பாரம்பரிய ஜோதிட சாஸ்திரமும் கூறும் நாள்விழிப்பு, கௌரி பஞ்சாங்கம், வாரசூலம் பரிகாரம், நோய் தீர்க்கும் தெய்வங்கள், வாஸ்து புருஷன் விழிப்பு நேரங்கள் மற்றும் சுபமுகூர்த்த நியதிகள்."
                  : "Authentic classical guidelines covering daily eye-count, Gowri Panchangam, Soolam remedies, medical deity healing, Vastu Purusha awakening, and auspicious life muhurtas."}
              </p>
            </div>
          </div>
        </div>

        {/* Top Navigation Tabs */}
        <div className="bg-white rounded-xl shadow-sm p-2 border border-gray-200 flex flex-wrap gap-2 overflow-x-auto">
          {[
            { id: "daily", labelTa: "🌟 தினசரி வழிகாட்டி", labelEn: "🌟 Daily Guide" },
            { id: "medical", labelTa: "🌿 நோய் தீர்க்கும் தெய்வங்கள் (22)", labelEn: "🌿 Medical Deities (22)" },
            { id: "wishes", labelTa: "🌺 காரிய சித்தி & ராமாயணம்", labelEn: "🌺 Life Goals & Ramayana" },
            { id: "vastu", labelTa: "🏛️ வாஸ்து நாட்கள் & 51 விதிகள்", labelEn: "🏛️ Vastu Days & Rules" },
            { id: "muhurta", labelTa: "⏳ கடன் தீர & சுப முகூர்த்தம்", labelEn: "⏳ Debt & Muhurtas" },
            { id: "navagraha", labelTa: "🪐 நவக்கிரக வழிபாடு & தசா", labelEn: "🪐 Navagraha & Dasa" },
            { id: "dharma", labelTa: "🪔 தீப வழிபாடு & தர்ம நெறி", labelEn: "🪔 Deepam & Daily Dharma" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as ActiveTab)}
              className={`px-4 py-2.5 rounded-lg text-sm font-semibold transition-all whitespace-nowrap flex items-center gap-2 ${
                activeTab === tab.id
                  ? "bg-[#1B365D] text-white shadow-sm"
                  : "text-gray-750 hover:bg-gray-100 hover:text-gray-900"
              }`}
            >
              {isTa ? tab.labelTa : tab.labelEn}
            </button>
          ))}
        </div>

        {/* TAB 1: DAILY GUIDANCE */}
        {activeTab === "daily" && (
          <div className="space-y-6">
            {/* Date Selector & Summary Bar */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-3 w-full md:w-auto">
                <Calendar className="w-5 h-5 text-[#1B365D]" />
                <label className="text-sm font-bold text-gray-700 whitespace-nowrap">
                  {isTa ? "தேதியைத் தேர்ந்தெடுக்கவும்:" : "Select Date:"}
                </label>
                <input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium focus:ring-2 focus:ring-[#1B365D] focus:outline-none"
                />
              </div>

              {dailyData && (
                <div className="flex flex-wrap items-center gap-3 text-sm">
                  <div className="px-3 py-1.5 rounded-lg bg-blue-50 border border-blue-200 text-blue-900 font-semibold flex items-center gap-1.5">
                    <Sun className="w-4 h-4 text-blue-600" />
                    <span>{dailyData.weekday_ta} ({dailyData.weekday_en})</span>
                  </div>
                  <div
                    className={`px-3 py-1.5 rounded-lg font-semibold flex items-center gap-1.5 border ${
                      dailyData.naal_vizhippu_category === "two_eyed"
                        ? "bg-green-50 border-green-200 text-green-900"
                        : dailyData.naal_vizhippu_category === "one_eyed"
                        ? "bg-yellow-50 border-yellow-200 text-yellow-900"
                        : "bg-red-50 border-red-200 text-red-900"
                    }`}
                  >
                    <Sparkles className="w-4 h-4" />
                    <span>{dailyData.naal_vizhippu_ta}</span>
                  </div>
                </div>
              )}
            </div>

            {loadingDaily ? (
              <div className="p-12 text-center bg-white rounded-xl shadow-sm">
                <div className="inline-block w-8 h-8 border-4 border-[#1B365D] border-t-transparent rounded-full animate-spin" />
                <p className="mt-2 text-sm text-gray-500">
                  {isTa ? "சாஸ்திர தகவல்கள் கணிக்கப்படுகின்றன..." : "Loading daily sastra..."}
                </p>
              </div>
            ) : dailyData ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Vaara Soolam & Pariharam */}
                <div className="bg-white rounded-xl p-6 shadow-sm border border-red-100 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <AlertTriangle className="w-5 h-5 text-red-600" />
                      <h3 className="text-base font-bold text-gray-900">
                        {isTa ? "இன்றைய வார சூலம் & பரிகாரம்" : "Today's Vaara Soolam & Pariharam"}
                      </h3>
                    </div>
                    <div className="p-4 rounded-xl bg-red-50/70 border border-red-200 space-y-2">
                      <p className="text-sm text-gray-800">
                        <strong className="text-red-900 font-bold">{isTa ? "சூல திசை:" : "Afflicted Direction:"}</strong>{" "}
                        <span className="text-red-800 font-semibold">{dailyData.vaara_soolam_ta} ({dailyData.vaara_soolam_direction})</span>
                      </p>
                      <p className="text-sm text-gray-800">
                        <strong className="text-gray-900 font-bold">{isTa ? "பரிகார உணவு:" : "Remedy Food:"}</strong>{" "}
                        <span className="text-emerald-800 font-semibold">{dailyData.pariharam_ta}</span>
                      </p>
                      <p className="text-xs text-gray-600 italic mt-2">
                        {isTa
                          ? "குறிப்பு: அவசிய பிரயாணம் ஏற்படின், நாழிகை 10-க்கு மேல் (காலை 10 மணிக்கு மேல்) பரிகாரப் பொருளை உட்கொண்டு புறப்படலாம்."
                          : "Note: If unavoidable, begin travel after 10 Nazhigais (~10 AM) after consuming the remedy."}
                      </p>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-gray-700 mb-2">
                      {isTa ? "சுப ஹோரைகள்" : "Auspicious Horas Today"}
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {dailyData.auspicious_horas_ta?.map((hora: string, idx: number) => (
                        <span
                          key={idx}
                          className="px-2.5 py-1 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs font-medium"
                        >
                          {hora}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Do's & Don'ts */}
                <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 space-y-4">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="w-5 h-5 text-emerald-600" />
                    <h3 className="text-base font-bold text-gray-900">
                      {isTa ? "இன்றைய சாஸ்திர வழிகாட்டுதல்கள்" : "Today's Do's & Don'ts"}
                    </h3>
                  </div>

                  <div className="space-y-2">
                    <h4 className="text-xs font-bold text-emerald-800 uppercase tracking-wider">
                      {isTa ? "செய்யக்கூடியவை (Do's)" : "Recommended"}
                    </h4>
                    <ul className="space-y-1.5">
                      {dailyData.dos_for_today_ta?.map((doItem: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-2 text-xs sm:text-sm text-gray-700">
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
                          <span>{doItem}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="space-y-2 pt-2 border-t border-gray-100">
                    <h4 className="text-xs font-bold text-red-800 uppercase tracking-wider">
                      {isTa ? "தவிர்க்க வேண்டியவை (Don'ts)" : "Avoid"}
                    </h4>
                    <ul className="space-y-1.5">
                      {dailyData.donts_for_today_ta?.map((dontItem: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-2 text-xs sm:text-sm text-gray-700">
                          <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 shrink-0" />
                          <span>{dontItem}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Gowri Panchangam Daytime 8 Slots */}
                <div className="md:col-span-2 bg-white rounded-xl p-6 shadow-sm border border-gray-200 space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <Clock className="w-5 h-5 text-[#B4872B]" />
                      <h3 className="text-base font-bold text-gray-900">
                        {isTa ? "கௌரி பஞ்சாங்கம் (பகல் 8 முகூர்த்தங்கள்)" : "Gowri Panchangam (8 Day Muhurtas)"}
                      </h3>
                    </div>
                    <span className="text-xs text-gray-500">
                      {isTa ? "1 முகூர்த்தம் = 1.30 மணி நேரம் (3.75 நாழிகை)" : "1 Muhurta = 1 hr 30 min (3.75 Nazhigai)"}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
                    {dailyData.gowri_panchangam_day?.map((slot: any) => (
                      <div
                        key={slot.order}
                        className={`p-3 rounded-xl border text-center transition-all ${
                          slot.is_favorable
                            ? slot.name_en === "Amirtham" || slot.name_en === "Labham"
                              ? "bg-emerald-50 border-emerald-300 text-emerald-900 shadow-sm"
                              : "bg-blue-50 border-blue-200 text-blue-900"
                            : "bg-red-50 border-red-200 text-red-900"
                        }`}
                      >
                        <span className="text-[10px] font-bold block opacity-75 uppercase">
                          {isTa ? `பகுதி ${slot.order}` : `Slot ${slot.order}`}
                        </span>
                        <h4 className="text-base font-bold my-1">{slot.name_ta}</h4>
                        <span
                          className={`inline-block text-[10px] px-1.5 py-0.5 rounded font-semibold ${
                            slot.is_favorable
                              ? "bg-emerald-100 text-emerald-800"
                              : "bg-red-100 text-red-800"
                          }`}
                        >
                          {slot.nature}
                        </span>
                        <p className="text-[11px] mt-2 line-clamp-2 leading-tight opacity-90">
                          {slot.description_ta}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Daily Deepam & Eating Wisdom */}
                <div className="md:col-span-2 bg-[#FAF2DE]/50 rounded-xl p-5 border border-[#B4872B]/40 flex flex-col sm:flex-row items-start gap-4">
                  <Flame className="w-8 h-8 text-[#B4872B] shrink-0 mt-1" />
                  <div className="space-y-1.5 text-xs sm:text-sm text-gray-800">
                    <p>
                      <strong className="text-gray-900 font-bold">{isTa ? "தீப வழிபாடு ரகசியம்:" : "Lamp Lighting Wisdom:"}</strong>{" "}
                      {dailyData.deepam_worship_tip_ta}
                    </p>
                    <p>
                      <strong className="text-gray-900 font-bold">{isTa ? "உணவருந்தும் முறை:" : "Dining Dharma:"}</strong>{" "}
                      {dailyData.general_dharma_tip_ta}
                    </p>
                  </div>
                </div>
              </div>
            ) : null}
          </div>
        )}

        {/* TAB 2: MEDICAL ASTROLOGY DEITIES (22) */}
        {activeTab === "medical" && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <h2 className="text-lg font-bold text-gray-900">
                    {isTa ? "எந்தெந்த நோய் தீர எந்தெந்த கடவுளை வணங்க வேண்டும்?" : "Deity Propitiations for 22 Chronic Diseases"}
                  </h2>
                  <p className="text-xs sm:text-sm text-gray-600 mt-1">
                    {isTa
                      ? "சாஸ்திரத்தின்படி உடல் உறுப்புகள் மற்றும் வியாதிகளுக்குரிய அதிதேவதை வழிபாடு மற்றும் பரிகார முறைகள்."
                      : "Presiding divine forms and propitiations for rapid healing and physical recovery."}
                  </p>
                </div>

                <div className="flex flex-col sm:flex-row items-center gap-3">
                  <div className="relative w-full sm:w-64">
                    <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                      type="text"
                      placeholder={isTa ? "நோய் அல்லது கடவுள் தேடுக..." : "Search disease or deity..."}
                      value={medicalSearch}
                      onChange={(e) => setMedicalSearch(e.target.value)}
                      className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#1B365D] focus:outline-none"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Grid of Medical Deities */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredMedical.map((item) => (
                <div
                  key={item.id}
                  className="bg-white rounded-xl p-5 shadow-sm border border-gray-200 hover:border-[#B4872B]/60 transition-all flex flex-col justify-between"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-[#FAF2DE] text-[#B4872B] border border-[#B4872B]/30">
                        #{item.id}
                      </span>
                      <span className="text-xs text-gray-600 uppercase font-semibold">
                        {item.category}
                      </span>
                    </div>

                    <div>
                      <h3 className="text-base font-bold text-gray-900 leading-snug">
                        {item.disease_ta}
                      </h3>
                      <p className="text-xs text-gray-700 mt-0.5">{item.disease_en}</p>
                    </div>

                    <div className="p-3 rounded-lg bg-emerald-50/70 border border-emerald-200 space-y-1">
                      <span className="text-[11px] font-bold text-emerald-800 uppercase block">
                        {isTa ? "வணங்க வேண்டிய தெய்வம்:" : "Worship Deity:"}
                      </span>
                      <h4 className="text-sm font-bold text-emerald-950">
                        {item.deity_ta}
                      </h4>
                      <p className="text-xs text-emerald-700">{item.deity_en}</p>
                    </div>

                    {item.mantra_or_procedure_ta && (
                      <p className="text-xs text-gray-700 leading-relaxed bg-gray-50 p-2.5 rounded-lg border border-gray-200">
                        <strong>{isTa ? "பரிகார முறை:" : "Remedy:"}</strong> {item.mantra_or_procedure_ta}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 3: LIFE WISHES & RAMAYANA */}
        {activeTab === "wishes" && (
          <div className="space-y-8">
            {/* Search */}
            <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200 flex items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-bold text-gray-900">
                  {isTa ? "எந்த காரியம் நடக்க எந்த தெய்வத்தை வணங்க வேண்டும்?" : "Deity Propitiation for 20 Life Goals"}
                </h2>
                <p className="text-xs text-gray-600">
                  {isTa ? "மற்றும் 19 வால்மீகி ராமாயண பாராயண சர்க்கங்கள்" : "And 19 Valmiki Ramayana Parayanam Sargas"}
                </p>
              </div>
              <div className="relative w-64">
                <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder={isTa ? "காரியம் / நோக்கம் தேடுக..." : "Search goal..."}
                  value={wishesSearch}
                  onChange={(e) => setWishesSearch(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#1B365D] focus:outline-none"
                />
              </div>
            </div>

            {/* 20 Life Wishes */}
            <div>
              <h3 className="text-base font-bold text-gray-900 mb-3 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-[#B4872B]" />
                {isTa ? "20 காரிய சித்தி தரும் தெய்வங்கள்" : "20 Life Goals & Deity Propitiations"}
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {filteredWishes.map((w) => (
                  <div
                    key={w.id}
                    className="bg-white rounded-xl p-4 shadow-sm border border-gray-200 space-y-2 hover:border-[#1B365D]/40 transition-all"
                  >
                    <span className="text-[10px] font-bold text-gray-600 block">#{w.id}</span>
                    <h4 className="text-sm font-bold text-[#1B365D] leading-tight">
                      {w.goal_ta}
                    </h4>
                    <p className="text-xs text-gray-700 font-medium">{w.goal_en}</p>
                    <div className="pt-2 border-t border-gray-100 text-xs">
                      <span className="font-bold text-gray-700 block">{isTa ? "தெய்வம்:" : "Deity:"}</span>
                      <p className="font-bold text-emerald-800">{w.deity_ta}</p>
                    </div>
                    {w.temple_sankalpa_ta && (
                      <p className="text-[11px] text-gray-750 bg-gray-50 p-2 rounded">
                        {w.temple_sankalpa_ta}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* 19 Ramayana Parayanams */}
            <div className="pt-6 border-t border-gray-200">
              <h3 className="text-base font-bold text-gray-900 mb-3 flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-[#1B365D]" />
                {isTa ? "வால்மீகி ராமாயண பாராயண கட்டங்கள் (19 காரியங்கள்)" : "Valmiki Ramayana Parayanam Sargas"}
              </h3>
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-x-auto">
                <table className="min-w-full text-left text-xs sm:text-sm">
                  <thead className="bg-[#1B365D] text-white">
                    <tr>
                      <th className="py-3 px-4 font-semibold">{isTa ? "எண்" : "#"}</th>
                      <th className="py-3 px-4 font-semibold">{isTa ? "நிறைவேற வேண்டிய காரியம்" : "Intended Goal"}</th>
                      <th className="py-3 px-4 font-semibold">{isTa ? "காண்டம்" : "Kanda"}</th>
                      <th className="py-3 px-4 font-semibold">{isTa ? "பாராயணக் கட்டம்" : "Sarga / Episode"}</th>
                      <th className="py-3 px-4 font-semibold">{isTa ? "பாராயணம் செய்யும் காலம்" : "Time to Chant"}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {filteredRamayana.map((r) => (
                      <tr key={r.id} className="hover:bg-gray-50">
                        <td className="py-3 px-4 font-bold text-gray-500">{r.id}</td>
                        <td className="py-3 px-4 font-bold text-gray-900">
                          {r.purpose_ta}
                          <span className="block text-xs font-normal text-gray-500">{r.purpose_en}</span>
                        </td>
                        <td className="py-3 px-4 font-semibold text-[#1B365D]">{r.kandam_ta}</td>
                        <td className="py-3 px-4 font-bold text-emerald-800">{r.sarga_title_ta}</td>
                        <td className="py-3 px-4 text-gray-700">{r.recommended_time_ta}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: VASTU SHASTRA */}
        {activeTab === "vastu" && (
          <div className="space-y-8">
            {/* Vastu Purusha 8 Awakening Days */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 space-y-4">
              <div className="flex items-center gap-2">
                <Building className="w-5 h-5 text-[#B4872B]" />
                <h2 className="text-lg font-bold text-gray-900">
                  {isTa ? "வருடத்தின் 8 வாஸ்து புருஷன் விழிப்பு நாட்களும் நேரங்களும்" : "8 Annual Vastu Purusha Awakening Windows"}
                </h2>
              </div>
              <p className="text-xs sm:text-sm text-gray-600 leading-relaxed">
                {isTa
                  ? "வாஸ்து புருஷன் வருடத்தில் 8 குறிப்பிட்ட நாட்களில் மட்டுமே விழித்திருப்பார் (ஒவ்வொரு முறையும் 3 3/4 நாழிகைகள் = 1.30 மணி). அதில் கடைசி 36 நிமிடங்களில் வாஸ்து பூஜை செய்தால் மனை நிலைத்து நிற்கும்."
                  : "Vastu Purusha is active only on 8 specific solar days annually for 90 minutes. Performing puja during the final 36 minutes ensures enduring prosperity."}
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {vastuTimings.map((t, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-xl border border-amber-200 bg-amber-50/40 space-y-2 text-xs"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-sm text-[#1B365D]">
                        {t.tamil_month} {t.solar_day}ம் தேதி
                      </span>
                      <span className="text-[10px] text-gray-700 bg-white px-2 py-0.5 rounded border">
                        {t.gregorian_approx}
                      </span>
                    </div>
                    <p className="text-gray-800">
                      <strong>{isTa ? "விழிப்பு நேரம்:" : "Time:"}</strong> {t.duration_time}
                    </p>
                    <p className="text-emerald-800 font-semibold">
                      <strong>{isTa ? "பூஜை நேரம்:" : "Puja Window:"}</strong> {t.puja_golden_window}
                    </p>
                    <div className="pt-2 border-t border-amber-200/60 font-medium text-gray-700">
                      {t.best_door_facing_ta}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Vastu Rules Checklist */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <CheckSquare className="w-5 h-5 text-emerald-600" />
                  <h3 className="text-base font-bold text-gray-900">
                    {isTa ? "பாரம்பரிய வாஸ்து சாஸ்திர விதிகள் (Checklist)" : "Classical Vastu Shastra Rules"}
                  </h3>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <Filter className="w-3.5 h-3.5 text-gray-500" />
                  <select
                    value={vastuCategory}
                    onChange={(e) => setVastuCategory(e.target.value)}
                    className="px-2.5 py-1.5 border border-gray-300 rounded-lg focus:outline-none text-xs"
                  >
                    <option value="all">{isTa ? "அனைத்து பிரிவுகள்" : "All Categories"}</option>
                    <option value="layout">{isTa ? "அறை அமைப்புகள்" : "Layout"}</option>
                    <option value="water">{isTa ? "நீர் / கிணறு / போரிங்" : "Water & Well"}</option>
                    <option value="toilet">{isTa ? "கழிவறை" : "Toilet"}</option>
                    <option value="wealth">{isTa ? "பணப்பெட்டி / செல்வம்" : "Wealth Safe"}</option>
                    <option value="trees">{isTa ? "மரங்கள்" : "Trees"}</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {filteredVastuRules.map((rule) => (
                  <div
                    key={rule.rule_number}
                    className="p-3.5 rounded-xl border border-gray-100 bg-gray-50/60 space-y-1.5 text-xs sm:text-sm"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-xs text-[#1B365D]">
                        {isTa ? `விதி #${rule.rule_number}` : `Rule #${rule.rule_number}`}
                      </span>
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded font-semibold ${
                          rule.importance === "Mandatory"
                            ? "bg-red-100 text-red-800"
                            : "bg-blue-100 text-blue-800"
                        }`}
                      >
                        {rule.importance}
                      </span>
                    </div>
                    <p className="font-semibold text-gray-900 leading-snug">{rule.rule_ta}</p>
                    <p className="text-xs text-gray-500">{rule.rule_en}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB 5: SPECIAL MUHURTAS & DEBT CLEARANCE */}
        {activeTab === "muhurta" && specialMuhurtas && (
          <div className="space-y-6">
            {/* Kadan Theera Muhurtam */}
            <div className="bg-gradient-to-br from-emerald-50 to-green-100/60 rounded-2xl p-6 border border-emerald-300 shadow-sm space-y-4">
              <div className="flex items-center gap-2">
                <Sparkles className="w-6 h-6 text-emerald-700" />
                <h2 className="text-lg font-bold text-emerald-950">
                  {specialMuhurtas.kadan_theera?.title_ta}
                </h2>
              </div>
              <p className="text-sm text-emerald-900 leading-relaxed font-medium">
                {specialMuhurtas.kadan_theera?.description_ta}
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
                <div className="bg-white/80 p-3 rounded-xl border border-emerald-200">
                  <span className="text-xs font-bold text-gray-500 uppercase block">
                    {isTa ? "நட்சத்திரங்கள்:" : "Nakshatras:"}
                  </span>
                  <p className="font-bold text-emerald-800 mt-0.5">
                    {specialMuhurtas.kadan_theera?.recommended_stars_ta?.join(", ")}
                  </p>
                </div>
                <div className="bg-white/80 p-3 rounded-xl border border-emerald-200">
                  <span className="text-xs font-bold text-gray-500 uppercase block">
                    {isTa ? "கிழமைகள்:" : "Weekdays:"}
                  </span>
                  <p className="font-bold text-emerald-800 mt-0.5">
                    {specialMuhurtas.kadan_theera?.recommended_weekdays_ta?.join(", ")}
                  </p>
                </div>
                <div className="bg-white/80 p-3 rounded-xl border border-emerald-200">
                  <span className="text-xs font-bold text-gray-500 uppercase block">
                    {isTa ? "திதிகள்:" : "Tithis:"}
                  </span>
                  <p className="font-bold text-emerald-800 mt-0.5">
                    {specialMuhurtas.kadan_theera?.recommended_tithis_ta?.join(", ")}
                  </p>
                </div>
              </div>
            </div>

            {/* Pudhu Kanakku & Child Samskaras */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Pudhu Kanakku */}
              <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 space-y-3">
                <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
                  <BookOpen className="w-5 h-5 text-[#1B365D]" />
                  {specialMuhurtas.pudhu_kanakku?.title_ta}
                </h3>
                <p className="text-xs text-gray-600">
                  {specialMuhurtas.pudhu_kanakku?.title_en}
                </p>
                <div className="space-y-2 text-xs sm:text-sm text-gray-700">
                  <p>
                    <strong>{isTa ? "கிழமைகள்:" : "Days:"}</strong>{" "}
                    {specialMuhurtas.pudhu_kanakku?.recommended_weekdays_ta?.join(", ")}
                  </p>
                  <p>
                    <strong>{isTa ? "நட்சத்திரங்கள்:" : "Nakshatras:"}</strong>{" "}
                    {specialMuhurtas.pudhu_kanakku?.recommended_stars_ta?.join(", ")}
                  </p>
                  <div className="p-3 bg-gray-50 rounded-lg border border-gray-100 text-xs">
                    {specialMuhurtas.pudhu_kanakku?.golden_rules_ta?.map((r: string, i: number) => (
                      <p key={i}>• {r}</p>
                    ))}
                  </div>
                </div>
              </div>

              {/* Child Samskaras */}
              <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 space-y-3 text-xs sm:text-sm text-gray-700">
                <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
                  <Heart className="w-5 h-5 text-rose-600" />
                  {isTa ? "குழந்தைகளுக்கான சடங்குகள் முகூர்த்தம்" : "Childhood Samskara Timings"}
                </h3>
                <ul className="space-y-2 divide-y divide-gray-100">
                  <li className="pt-1.5">
                    <strong>{isTa ? "பெயர் சூட்டல் (நாமகரணம்):" : "Naming:"}</strong> பிறந்த 10 அல்லது 12வது நாளில். திங்கள், புதன், வியாழன், வெள்ளி.
                  </li>
                  <li className="pt-1.5">
                    <strong>{isTa ? "பாலூட்டல்:" : "First Milk Feeding:"}</strong> 31 அல்லது 32ம் நாளில் சங்கினால் பாலூட்டல் உத்தமம்.
                  </li>
                  <li className="pt-1.5">
                    <strong>{isTa ? "அன்னப்பிராசனம்:" : "Annaprashana:"}</strong> ஆண் குழந்தைக்கு 6, 8, 10வது மாதம்; பெண் குழந்தைக்கு 7, 9, 11வது மாதம்.
                  </li>
                  <li className="pt-1.5">
                    <strong>{isTa ? "முடி எடுத்தல் (சௌளம்):" : "Tonsure (Chaulam):"}</strong> 3, 5 அல்லது 7வது வயதில் உத்தராயண காலத்தில்.
                  </li>
                  <li className="pt-1.5">
                    <strong>{isTa ? "காது குத்தல்:" : "Ear Piercing:"}</strong> 12, 16ம் நாள் அல்லது 6, 7, 8வது மாதத்தில்.
                  </li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* TAB 6: NAVAGRAHA CATALOG & DASA PARIHARAMS */}
        {activeTab === "navagraha" && (
          <div className="space-y-8">
            {/* Navagraha Matrix Table */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 space-y-4">
              <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <Sun className="w-5 h-5 text-[#B4872B]" />
                {isTa ? "நவக்கிரகங்கள் முழுமையான வழிபாட்டு விவர அட்டவணை" : "Navagraha Comprehensive Attributes"}
              </h2>

              <div className="overflow-x-auto">
                <table className="min-w-full text-left text-xs sm:text-sm">
                  <thead className="bg-[#1B365D] text-white">
                    <tr>
                      <th className="py-2.5 px-3">{isTa ? "கிரகம்" : "Graha"}</th>
                      <th className="py-2.5 px-3">{isTa ? "வஸ்திரம்" : "Color"}</th>
                      <th className="py-2.5 px-3">{isTa ? "தானியம்" : "Grain"}</th>
                      <th className="py-2.5 px-3">{isTa ? "திசை" : "Direction"}</th>
                      <th className="py-2.5 px-3">{isTa ? "ரத்தினம்" : "Gem"}</th>
                      <th className="py-2.5 px-3">{isTa ? "அதிதேவதை" : "Deity"}</th>
                      <th className="py-2.5 px-3">{isTa ? "உலோகம்" : "Metal"}</th>
                      <th className="py-2.5 px-3">{isTa ? "புஷ்பம்" : "Flower"}</th>
                      <th className="py-2.5 px-3">{isTa ? "வாகனம்" : "Vehicle"}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {navagrahas.map((g, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="py-2.5 px-3 font-bold text-[#1B365D]">{g.graha_ta}</td>
                        <td className="py-2.5 px-3">{g.cloth_color_ta}</td>
                        <td className="py-2.5 px-3">{g.grain_ta}</td>
                        <td className="py-2.5 px-3">{g.direction_ta}</td>
                        <td className="py-2.5 px-3 font-semibold text-emerald-800">{g.gemstone_ta}</td>
                        <td className="py-2.5 px-3 font-semibold text-purple-900">{g.adhidevata_ta}</td>
                        <td className="py-2.5 px-3">{g.metal_ta}</td>
                        <td className="py-2.5 px-3">{g.flower_ta}</td>
                        <td className="py-2.5 px-3">{g.vehicle_ta}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Dasa Bhukti Pariharams & Sacred Sthalams */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 space-y-4">
              <h3 className="text-base font-bold text-gray-900">
                {isTa ? "9 கிரகங்களின் தசா-புக்தி பரிகாரங்களும் திருத்தலங்களும்" : "Planetary Dasa Pariharams & Sacred Temples"}
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {dasaPariharams.map((d, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-xl border border-gray-200 bg-gray-50/50 space-y-2 text-xs sm:text-sm"
                  >
                    <span className="font-bold text-[#1B365D] text-base block">
                      {d.graha_ta} தசை பரிகாரம்
                    </span>
                    <p className="text-xs text-gray-600 italic">{d.affliction_triggers_ta}</p>
                    <p className="text-gray-800">
                      <strong>பரிகாரம்:</strong> {d.pariharam_procedure_ta}
                    </p>
                    <p className="text-emerald-800">
                      <strong>தானம்:</strong> {d.donation_items_ta}
                    </p>
                    <div className="pt-2 border-t border-gray-200">
                      <span className="font-bold text-purple-900 text-xs block">முக்கிய தலங்கள்:</span>
                      <p className="text-xs text-gray-700">{d.sacred_temples_ta?.join(", ")}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB 7: DEEPAM & DAILY DHARMA GUIDELINES */}
        {activeTab === "dharma" && specialMuhurtas && (
          <div className="space-y-6">
            {/* Deepam Wicks & Oils */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 space-y-4">
              <div className="flex items-center gap-2">
                <Flame className="w-5 h-5 text-[#B4872B]" />
                <h2 className="text-lg font-bold text-gray-900">
                  {specialMuhurtas.deepam_rules?.title_ta}
                </h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Wicks */}
                <div className="space-y-3">
                  <h3 className="text-sm font-bold text-gray-800 uppercase tracking-wider">
                    {isTa ? "திரிகளின் பலன்கள்" : "Lamp Wicks & Spiritual Boons"}
                  </h3>
                  <div className="space-y-2 text-xs sm:text-sm">
                    {specialMuhurtas.deepam_rules?.wicks_benefits_ta?.map((w: any, idx: number) => (
                      <div key={idx} className="p-2.5 rounded-lg bg-amber-50/60 border border-amber-200/70 flex items-center justify-between">
                        <span className="font-bold text-gray-900">{w.wick}</span>
                        <span className="text-emerald-800 font-semibold">{w.benefit}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Oils */}
                <div className="space-y-3">
                  <h3 className="text-sm font-bold text-gray-800 uppercase tracking-wider">
                    {isTa ? "எண்ணெய்களின் பலன்கள்" : "Lamp Oils & Benefits"}
                  </h3>
                  <div className="space-y-2 text-xs sm:text-sm">
                    {specialMuhurtas.deepam_rules?.oils_benefits_ta?.map((o: any, idx: number) => (
                      <div key={idx} className="p-2.5 rounded-lg bg-orange-50/60 border border-orange-200/70 flex items-center justify-between">
                        <span className="font-bold text-gray-900">{o.oil}</span>
                        <span className="text-emerald-800 font-semibold">{o.benefit}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Temple Pradakshina Counts */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 space-y-4">
              <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
                <Compass className="w-5 h-5 text-[#1B365D]" />
                {specialMuhurtas.temple_pradakshina?.title_ta}
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                {specialMuhurtas.temple_pradakshina?.pradakshina_counts_ta?.map((p: any, idx: number) => (
                  <div key={idx} className="p-3 bg-blue-50/60 rounded-xl border border-blue-200 text-center">
                    <span className="font-bold text-gray-900 block text-sm">{p.deity}</span>
                    <span className="text-xs font-semibold text-[#1B365D] mt-1 block">{p.count}</span>
                  </div>
                ))}
              </div>
              <div className="p-4 bg-gray-50 rounded-xl border border-gray-200 text-xs sm:text-sm text-gray-700 space-y-1.5">
                {specialMuhurtas.temple_pradakshina?.golden_rules_ta?.map((r: string, idx: number) => (
                  <p key={idx}>• {r}</p>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
