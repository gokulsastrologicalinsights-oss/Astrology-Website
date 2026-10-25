"use client";

import React, { useState, useEffect, useRef, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { SouthIndianChart } from "@/components/charts/SouthIndianChart";
import { NorthIndianChart } from "@/components/charts/NorthIndianChart";
import {
  VargaD1D9Request,
  VargaD1D9Response,
  VargaPlanetPosition,
  HoroscopeResponse,
  ShodashvargaResponse,
  ShodashvargaChartItem,
  ShodashvargaPlanetEntry,
} from "@/lib/types";
import { calculateVargaD1D9, calculateShodashvarga, downloadShodashvargaPdf, triggerBlobDownload } from "@/lib/api";
import { formatDm } from "@/lib/formatters";
import {
  Compass,
  ArrowLeft,
  Sparkles,
  Layers,
  Calendar,
  Clock,
  MapPin,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  HelpCircle,
  Eye,
  Columns,
  Star,
  Award,
  BookOpen,
  Grid,
  ChevronRight,
  ShieldCheck,
  Flame,
  Info,
  Download,
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

interface VargaMetaDefinition {
  key: string;
  num: number;
  nameEn: string;
  nameTa: string;
  focusEn: string;
  focusTa: string;
  group: "shadvarga" | "saptavarga" | "dasavarga" | "higher";
}

const SHODASHVARGA_LIST: VargaMetaDefinition[] = [
  { key: "D1", num: 1, nameEn: "Rasi", nameTa: "ராசி", focusEn: "Physical Body & General Destiny", focusTa: "உடல் நலம் & பொது விதி", group: "shadvarga" },
  { key: "D2", num: 2, nameEn: "Hora", nameTa: "ஹோரை", focusEn: "Wealth, Speech & Resources", focusTa: "செல்வம், வாக்கு & தனம்", group: "shadvarga" },
  { key: "D3", num: 3, nameEn: "Drekkana", nameTa: "திரேக்காணம்", focusEn: "Siblings, Courage & Vitality", focusTa: "உடன்பிறப்பு & தைரிய வீரியம்", group: "shadvarga" },
  { key: "D4", num: 4, nameEn: "Chaturthamsa", nameTa: "சதுர்த்தாம்சம்", focusEn: "Fixed Assets, Home & Fortune", focusTa: "சொத்து, வீடு & பாக்கியம்", group: "dasavarga" },
  { key: "D7", num: 7, nameEn: "Saptamsa", nameTa: "சப்தாம்சம்", focusEn: "Children, Progeny & Dynasty", focusTa: "புத்திர பாக்கியம் & சந்ததி", group: "saptavarga" },
  { key: "D9", num: 9, nameEn: "Navamsa", nameTa: "நவாம்சம்", focusEn: "Dharma, Spouse & Inner Vitality", focusTa: "தர்மம், களத்திரம் & ஆன்ம பலம்", group: "shadvarga" },
  { key: "D10", num: 10, nameEn: "Dasamsa", nameTa: "தசாம்சம்", focusEn: "Career, Honors & Social Power", focusTa: "தொழில், பதவி & கீர்த்தி", group: "dasavarga" },
  { key: "D12", num: 12, nameEn: "Dwadasamsa", nameTa: "துவாதசாம்சம்", focusEn: "Parents & Ancestral Karma", focusTa: "தாய், தந்தை & பித்ரு கர்மா", group: "shadvarga" },
  { key: "D16", num: 16, nameEn: "Shodasamsa", nameTa: "சோடசாம்சம்", focusEn: "Vehicles, Conveyance & Luxuries", focusTa: "வாகன சுகம் & சொகுசு வாழ்க்கை", group: "dasavarga" },
  { key: "D20", num: 20, nameEn: "Vimsamsa", nameTa: "விம்சாம்சம்", focusEn: "Spiritual Practice, Bhakti & Upasana", focusTa: "ஆன்மீக சாதனை & உபாசனை பலன்", group: "higher" },
  { key: "D24", num: 24, nameEn: "Chaturvimsamsa", nameTa: "சதுர்விம்சாம்சம்", focusEn: "Higher Knowledge & Intellect", focusTa: "உயர்கல்வி, வித்தை & ஞானம்", group: "higher" },
  { key: "D27", num: 27, nameEn: "Saptavimsamsa", nameTa: "சப்தவிம்சாம்சம்", focusEn: "Subtle Strengths & Weaknesses", focusTa: "உள் வலிமை & சகிப்புத்தன்மை", group: "higher" },
  { key: "D30", num: 30, nameEn: "Trimsamsa", nameTa: "திரிம்சாம்சம்", focusEn: "Misfortunes, Evils & Arishta", focusTa: "அரிஷ்டம், தோஷங்கள் & இடர்", group: "shadvarga" },
  { key: "D40", num: 40, nameEn: "Khavedamsa", nameTa: "கவேதாம்சம்", focusEn: "Auspicious & Inauspicious Results", focusTa: "சுபாசுப பலன்கள் & நல்வினை", group: "higher" },
  { key: "D45", num: 45, nameEn: "Akshavedamsa", nameTa: "அக்ஷவேதாம்சம்", focusEn: "All Moral Virtues & Character", focusTa: "சர்வ நன்மைகள் & ஒழுக்க சீலம்", group: "higher" },
  { key: "D60", num: 60, nameEn: "Shashtyamsa", nameTa: "சஷ்டியாம்சம்", focusEn: "Past-Life Karma & Ultimate Decider", focusTa: "பூர்வ ஜென்ம கர்மா & தீர்க்க விபரம்", group: "higher" },
];

const SIGN_SHORT_MAP: Record<number, { en: string; ta: string }> = {
  1: { en: "Ari", ta: "மே" },
  2: { en: "Tau", ta: "ரி" },
  3: { en: "Gem", ta: "மி" },
  4: { en: "Can", ta: "க" },
  5: { en: "Leo", ta: "சி" },
  6: { en: "Vir", ta: "கன்" },
  7: { en: "Lib", ta: "து" },
  8: { en: "Sco", ta: "வி" },
  9: { en: "Sag", ta: "த" },
  10: { en: "Cap", ta: "மக" },
  11: { en: "Aqu", ta: "கு" },
  12: { en: "Pis", ta: "மீ" },
};

function D1D9Content() {
  const searchParams = useSearchParams();
  const savedIdParam = searchParams.get("saved_id");

  const { language } = useLanguage();
  const { session, isAuthenticated } = useAuth();

  // Mode Selection: "saved" | "adhoc"
  const [inputMode, setInputMode] = useState<"saved" | "adhoc">("saved");

  // Saved Horoscopes List & Selected Item
  const [savedHoroscopes, setSavedHoroscopes] = useState<SavedHoroItem[]>([]);
  const [selectedHoroscopeId, setSelectedHoroscopeId] = useState<string>(savedIdParam || "");
  const [loadingSavedList, setLoadingSavedList] = useState<boolean>(false);

  // Ad-hoc Form State
  const [birthDate, setBirthDate] = useState<string>("1990-05-15");
  const [birthTime, setBirthTime] = useState<string>("14:30:00");
  const [timezone, setTimezone] = useState<string>("Asia/Kolkata");
  const [latitude, setLatitude] = useState<number>(13.0827);
  const [longitude, setLongitude] = useState<number>(80.2707);
  const [ayanamsa, setAyanamsa] = useState<number>(0); // 0 = Lahiri, 1 = KP

  // Studio Top Tabs
  const [activeTab, setActiveTab] = useState<"d1_d9" | "shodashvarga" | "matrix" | "d60_deities">("d1_d9");

  // 16-Varga Navigation State
  const [selectedVargaKey, setSelectedVargaKey] = useState<string>("D10");
  const [vargaFilter, setVargaFilter] = useState<"all" | "shadvarga" | "saptavarga" | "dasavarga" | "higher">("all");

  // Chart Rendering Style: South vs North
  const [chartStyle, setChartStyle] = useState<"south" | "north">("south");
  // D1/D9 Comparative View Mode
  const [viewMode, setViewMode] = useState<"side_by_side" | "d1" | "d9">("side_by_side");

  // Calculation Results & State
  const [vargaData, setVargaData] = useState<VargaD1D9Response | null>(null);
  const [shodashvargaData, setShodashvargaData] = useState<ShodashvargaResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Fetch list of saved horoscopes for authenticated user
  useEffect(() => {
    async function fetchSavedList() {
      if (!session?.access_token) return;
      setLoadingSavedList(true);
      try {
        const resp = await fetch("/api/horoscopes?limit=50", {
          headers: {
            Authorization: `Bearer ${session.access_token}`,
          },
        });
        if (resp.ok) {
          const data = await resp.json();
          const items = data.horoscopes || [];
          setSavedHoroscopes(items);
          if (items.length > 0 && !selectedHoroscopeId && !savedIdParam) {
            setSelectedHoroscopeId(items[0].id);
          }
        }
      } catch (err) {
        console.warn("Failed to fetch saved horoscopes:", err);
      } finally {
        setLoadingSavedList(false);
      }
    }

    if (isAuthenticated) {
      fetchSavedList();
    } else {
      setInputMode("adhoc");
    }
  }, [isAuthenticated, session?.access_token]);

  // Handle calculation execution
  const handleCalculate = async () => {
    setLoading(true);
    setErrorMsg(null);

    try {
      const token = session?.access_token;
      let res: VargaD1D9Response;

      if (inputMode === "saved") {
        if (!selectedHoroscopeId) {
          throw new Error("Please select a saved horoscope.");
        }
        res = await calculateVargaD1D9({ saved_horoscope_id: selectedHoroscopeId }, token);
      } else {
        const payload: VargaD1D9Request = {
          birth_date: birthDate,
          birth_time: birthTime,
          timezone,
          latitude,
          longitude,
          ayanamsa,
          house_system: 0,
        };
        res = await calculateVargaD1D9(payload, token);
      }

      setVargaData(res);
      if (res.shodashvarga) {
        setShodashvargaData(res.shodashvarga);
      } else {
        // Fallback fetch if shodashvarga was not included in older snapshot
        const shodashRes = await calculateShodashvarga(
          inputMode === "saved"
            ? { saved_horoscope_id: selectedHoroscopeId }
            : { birth_date: birthDate, birth_time: birthTime, timezone, latitude, longitude, ayanamsa },
          token
        );
        setShodashvargaData(shodashRes);
      }
    } catch (err: any) {
      console.error("Varga calculation failed:", err);
      setErrorMsg(err.message || "Failed to calculate divisional charts.");
    } finally {
      setLoading(false);
    }
  };

  const [downloadingPdf, setDownloadingPdf] = useState(false);

  const handleDownloadShodashvargaPdf = async () => {
    setDownloadingPdf(true);
    try {
      const token = session?.access_token;
      const personName = inputMode === "saved"
        ? (savedHoroscopes.find((h) => h.id === selectedHoroscopeId)?.person_name || "Native")
        : "Native";
      const payload: any = {
        native_name: personName,
        gender: "male",
        language: language === "ta" ? "ta" : "en",
        ayanamsa,
      };

      if (inputMode === "saved" && selectedHoroscopeId) {
        payload.saved_horoscope_id = selectedHoroscopeId;
      } else {
        payload.birth_input = {
          birth_date: birthDate,
          birth_time: birthTime,
          timezone,
          latitude,
          longitude,
        };
      }

      const blob = await downloadShodashvargaPdf(payload, token);
      triggerBlobDownload(blob, `Shodashvarga_Chart_Book_${personName.replace(/\s+/g, "_")}.pdf`);
    } catch (err: any) {
      alert(err?.message || "Failed to download Shodashvarga Chart Book PDF.");
    } finally {
      setDownloadingPdf(false);
    }
  };

  // Auto-calculate if saved_id was provided in URL query param
  const initialCalcRef = useRef(false);
  useEffect(() => {
    if (savedIdParam && session?.access_token && !initialCalcRef.current) {
      initialCalcRef.current = true;
      setInputMode("saved");
      setSelectedHoroscopeId(savedIdParam);
      setLoading(true);
      calculateVargaD1D9({ saved_horoscope_id: savedIdParam }, session.access_token)
        .then((res) => {
          setVargaData(res);
          if (res.shodashvarga) {
            setShodashvargaData(res.shodashvarga);
          }
        })
        .catch((e) => setErrorMsg(e.message))
        .finally(() => setLoading(false));
    }
  }, [savedIdParam, session?.access_token]);

  // Filtered vargas list based on selected classical group
  const filteredVargas = SHODASHVARGA_LIST.filter((v) => {
    if (vargaFilter === "all") return true;
    if (vargaFilter === "shadvarga") return v.group === "shadvarga";
    if (vargaFilter === "saptavarga") return v.group === "shadvarga" || v.group === "saptavarga";
    if (vargaFilter === "dasavarga") return v.group === "shadvarga" || v.group === "saptavarga" || v.group === "dasavarga";
    if (vargaFilter === "higher") return v.group === "higher";
    return true;
  });

  const selectedVargaItem: ShodashvargaChartItem | undefined =
    shodashvargaData?.charts?.[selectedVargaKey];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-8">
      {/* Breadcrumbs */}
      <Breadcrumbs
        items={[
          {
            label: language === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools",
            href: "/tools",
          },
          {
            label: language === "ta" ? "வர்க்க சக்கரங்கள் (D1 - D60)" : "Divisional Charts (D1 - D60)",
          },
        ]}
      />

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-[#DDE5F0] pb-6">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80] mb-2">
            <Compass className="w-3.5 h-3.5 text-[#B8862B]" />
            <span>Classical Shodashvarga Studio (BPHS Ch. 6)</span>
          </div>
          <h1 className="font-serif text-2xl sm:text-3xl lg:text-4xl font-bold text-[#102A4C]">
            {language === "ta"
              ? "16 வர்க்க சக்கரங்கள் & நவாம்ச ஆய்வுக்கூடம்"
              : "Shodashvarga Divisional Charts Studio (D1 to D60)"}
          </h1>
          <p className="text-xs sm:text-sm text-[#52667E] mt-1 max-w-2xl">
            {language === "ta"
              ? "பராசர ஹோரா சாஸ்திர முறைப்படி D1 ராசி முதல் D60 சஷ்டியாம்சம் வரையிலான 16 வர்க்க கட்டங்கள், வர்கோத்தம பலம், தசாம்சம் (தொழில்) மற்றும் 60 சஷ்டியாம்ச கர்மா அதிதேவதைகள்."
              : "Complete 16-divisional Vedic charts per Brihat Parashara Hora Shastra, integer milli-arcsecond precision, D10 Dasamsa career analysis, Varga-Bala matrix, and D60 deity karmic deciders."}
          </p>
        </div>

        <Link
          href="/tools"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#52667E] hover:text-[#102A4C] self-start md:self-center transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>{language === "ta" ? "கருவிகள் அடைவு" : "Back to Tools"}</span>
        </Link>
      </div>

      {/* Controls & Input Card */}
      <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-5">
        <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-4">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-[#B8862B]" />
            <h2 className="text-sm font-bold text-[#102A4C]">
              {language === "ta" ? "ஜாதக தேர்வு / உள்ளீடு" : "Chart Selection & Parameters"}
            </h2>
          </div>

          {/* Mode Switcher */}
          <div className="inline-flex p-1 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] text-xs">
            <button
              type="button"
              onClick={() => setInputMode("saved")}
              disabled={!isAuthenticated}
              className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
                inputMode === "saved"
                  ? "bg-[#102A4C] text-white shadow-2xs"
                  : "text-[#64748B] hover:text-[#102A4C]"
              } ${!isAuthenticated ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
            >
              {language === "ta" ? "சேமித்த ஜாதகம்" : "Saved Horoscope"}
            </button>
            <button
              type="button"
              onClick={() => setInputMode("adhoc")}
              className={`px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer ${
                inputMode === "adhoc"
                  ? "bg-[#102A4C] text-white shadow-2xs"
                  : "text-[#64748B] hover:text-[#102A4C]"
              }`}
            >
              {language === "ta" ? "புதிய உள்ளீடு" : "Custom Birth Details"}
            </button>
          </div>
        </div>

        {/* Saved Horoscope Selector */}
        {inputMode === "saved" && (
          <div className="space-y-3">
            <label className="block text-xs font-semibold text-[#334155]">
              {language === "ta" ? "சேமிக்கப்பட்ட ஜாதகத்தை தேர்ந்தெடுக்கவும்:" : "Select Saved Horoscope:"}
            </label>
            {loadingSavedList ? (
              <div className="text-xs text-[#64748B] flex items-center gap-2">
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-[#B8862B]" />
                <span>Loading your saved charts...</span>
              </div>
            ) : savedHoroscopes.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {savedHoroscopes.map((h) => {
                  const isSelected = selectedHoroscopeId === h.id;
                  return (
                    <div
                      key={h.id}
                      onClick={() => setSelectedHoroscopeId(h.id)}
                      className={`p-3.5 rounded-xl border text-xs cursor-pointer transition-all ${
                        isSelected
                          ? "border-[#B8862B] bg-[#FAF2DE]/50 shadow-xs"
                          : "border-[#E2E8F0] bg-white hover:border-[#CBD5E1]"
                      }`}
                    >
                      <div className="flex items-center justify-between font-bold text-[#102A4C]">
                        <span>{h.person_name}</span>
                        {isSelected && <CheckCircle2 className="w-4 h-4 text-[#B8862B]" />}
                      </div>
                      <div className="text-[11px] text-[#64748B] mt-1 space-y-0.5">
                        <div>
                          {h.birth_date} • {h.birth_time}
                        </div>
                        <div className="truncate text-[#94A3B8]">
                          {h.location_name || `${h.latitude.toFixed(2)}°, ${h.longitude.toFixed(2)}°`}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-amber-50/70 border border-amber-200 text-amber-900 text-xs">
                {language === "ta"
                  ? "சேமிக்கப்பட்ட ஜாதகங்கள் இல்லை. 'புதிய உள்ளீடு' மூலம் கணக்கிடலாம்."
                  : "No saved horoscopes found. Switch to 'Custom Birth Details' to calculate ad-hoc."}
              </div>
            )}
          </div>
        )}

        {/* Ad-hoc Form Inputs */}
        {inputMode === "adhoc" && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
            <div>
              <label className="block font-semibold text-[#334155] mb-1">
                <Calendar className="w-3.5 h-3.5 inline mr-1 text-[#B8862B]" />
                Birth Date (YYYY-MM-DD)
              </label>
              <input
                type="date"
                value={birthDate}
                onChange={(e) => setBirthDate(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] bg-white text-[#102A4C] font-mono focus:outline-hidden focus:border-[#B8862B]"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#334155] mb-1">
                <Clock className="w-3.5 h-3.5 inline mr-1 text-[#B8862B]" />
                Birth Time (HH:MM:SS)
              </label>
              <input
                type="time"
                step="1"
                value={birthTime}
                onChange={(e) => setBirthTime(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] bg-white text-[#102A4C] font-mono focus:outline-hidden focus:border-[#B8862B]"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#334155] mb-1">
                <MapPin className="w-3.5 h-3.5 inline mr-1 text-[#B8862B]" />
                Latitude (° Dec)
              </label>
              <input
                type="number"
                step="any"
                value={latitude}
                onChange={(e) => setLatitude(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] bg-white text-[#102A4C] font-mono focus:outline-hidden focus:border-[#B8862B]"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#334155] mb-1">
                <MapPin className="w-3.5 h-3.5 inline mr-1 text-[#B8862B]" />
                Longitude (° Dec)
              </label>
              <input
                type="number"
                step="any"
                value={longitude}
                onChange={(e) => setLongitude(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] bg-white text-[#102A4C] font-mono focus:outline-hidden focus:border-[#B8862B]"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#334155] mb-1">Timezone</label>
              <input
                type="text"
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                placeholder="Asia/Kolkata"
                className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] bg-white text-[#102A4C] font-mono focus:outline-hidden focus:border-[#B8862B]"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#334155] mb-1">Ayanamsa</label>
              <select
                value={ayanamsa}
                onChange={(e) => setAyanamsa(parseInt(e.target.value, 10))}
                className="w-full px-3 py-2 rounded-xl border border-[#CBD5E1] bg-white text-[#102A4C] font-semibold focus:outline-hidden focus:border-[#B8862B]"
              >
                <option value={0}>Lahiri (Chitra Paksha - Classical)</option>
                <option value={1}>KP (Krishnamurti Ayanamsa)</option>
              </select>
            </div>
          </div>
        )}

        {/* Action Button */}
        <div className="pt-2 flex flex-wrap items-center justify-between gap-3">
          <button
            type="button"
            onClick={handleCalculate}
            disabled={loading || (inputMode === "saved" && !selectedHoroscopeId)}
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-[#B8862B] to-[#9E6E1A] text-white font-bold text-xs shadow-md hover:shadow-lg transition-all cursor-pointer disabled:opacity-50"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>{language === "ta" ? "கணக்கிடப்படுகிறது..." : "Calculating 16 Vargas..."}</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>
                  {language === "ta"
                    ? "16 வர்க்க சக்கரங்களைக் காண்க (D1 - D60)"
                    : "Calculate & Explore 16 Shodashvargas"}
                </span>
              </>
            )}
          </button>

          {errorMsg && (
            <div className="inline-flex items-center gap-1.5 text-xs text-rose-600 bg-rose-50 px-3 py-1.5 rounded-lg border border-rose-200">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}
        </div>
      </div>

      {/* Results Studio Workspace */}
      {vargaData && (
        <div className="space-y-8">
          {/* Main Studio Navigation Tabs & PDF Export Button */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#DDE5F0] pb-2">
            <div className="flex overflow-x-auto gap-2 text-xs sm:text-sm">
              <button
                type="button"
                onClick={() => setActiveTab("d1_d9")}
                className={`flex items-center gap-2 py-3 px-4 font-bold border-b-2 whitespace-nowrap transition-colors cursor-pointer ${
                  activeTab === "d1_d9"
                    ? "border-[#B8862B] text-[#B8862B]"
                    : "border-transparent text-[#64748B] hover:text-[#102A4C]"
                }`}
              >
                <Columns className="w-4 h-4" />
                <span>{language === "ta" ? "D1 & D9 ஒப்பீடு" : "D1 & D9 Comparison"}</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveTab("shodashvarga")}
                className={`flex items-center gap-2 py-3 px-4 font-bold border-b-2 whitespace-nowrap transition-colors cursor-pointer ${
                  activeTab === "shodashvarga"
                    ? "border-[#B8862B] text-[#B8862B]"
                    : "border-transparent text-[#64748B] hover:text-[#102A4C]"
                }`}
              >
                <Grid className="w-4 h-4" />
                <span>{language === "ta" ? "16 வர்க்க சக்கரங்கள்" : "16 Shodashvarga Charts"}</span>
                <span className="px-1.5 py-0.5 rounded-full text-[10px] bg-[#FAF2DE] text-[#8C6D23] font-mono">
                  16
                </span>
              </button>

              <button
                type="button"
                onClick={() => setActiveTab("matrix")}
                className={`flex items-center gap-2 py-3 px-4 font-bold border-b-2 whitespace-nowrap transition-colors cursor-pointer ${
                  activeTab === "matrix"
                    ? "border-[#B8862B] text-[#B8862B]"
                    : "border-transparent text-[#64748B] hover:text-[#102A4C]"
                }`}
              >
                <Award className="w-4 h-4" />
                <span>{language === "ta" ? "16 வர்க்க கிரக அணி (Varga-Bala)" : "16-Varga Planetary Matrix"}</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveTab("d60_deities")}
                className={`flex items-center gap-2 py-3 px-4 font-bold border-b-2 whitespace-nowrap transition-colors cursor-pointer ${
                  activeTab === "d60_deities"
                    ? "border-[#B8862B] text-[#B8862B]"
                    : "border-transparent text-[#64748B] hover:text-[#102A4C]"
                }`}
              >
                <Flame className="w-4 h-4 text-amber-600" />
                <span>{language === "ta" ? "D60 சஷ்டியாம்ச கர்மா தேவதைகள்" : "D60 Karma Deities"}</span>
                <span className="px-1.5 py-0.5 rounded-full text-[10px] bg-amber-100 text-amber-800 font-mono">
                  60
                </span>
              </button>
            </div>

            <button
              type="button"
              onClick={handleDownloadShodashvargaPdf}
              disabled={downloadingPdf}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#8C6D23] hover:bg-[#735118] text-white text-xs font-bold shadow-xs transition-all cursor-pointer shrink-0 self-start sm:self-auto"
            >
              <Download className={`w-3.5 h-3.5 ${downloadingPdf ? "animate-spin" : ""}`} />
              <span>
                {downloadingPdf
                  ? (language === "ta" ? "புத்தகம் தயாராகிறது..." : "Compiling Chart Book...")
                  : (language === "ta" ? "16 வர்க்க கட்ட புத்தகம் PDF" : "Download 16-Varga Book PDF")}
              </span>
            </button>
          </div>

          {/* TAB 1: D1 & D9 COMPARISON */}
          {activeTab === "d1_d9" && (
            <div className="space-y-8">
              {/* Dignity & Summary Metrics Banner */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-4 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-1">
                  <div className="text-[11px] font-bold text-[#8C6D23] uppercase tracking-wider">
                    D1 Rasi Lagna
                  </div>
                  <div className="text-xl font-serif font-bold text-[#102A4C]">
                    {vargaData.ascendant.d1_sign_name}
                  </div>
                  <div className="text-xs text-[#64748B]">
                    {formatDm(vargaData.ascendant.d1_degree_in_sign)} • {vargaData.ascendant.nakshatra_name} (P{vargaData.ascendant.pada})
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-white border border-[#DDE5F0] shadow-2xs space-y-1">
                  <div className="text-[11px] font-bold text-[#8C6D23] uppercase tracking-wider">
                    D9 Navamsa Lagna
                  </div>
                  <div className="text-xl font-serif font-bold text-[#102A4C]">
                    {vargaData.ascendant.d9_sign_name}
                  </div>
                  <div className="text-xs text-[#64748B]">
                    {formatDm(vargaData.ascendant.d9_degree_in_sign)} • Lord: {vargaData.ascendant.d9_sign_lord}
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-[#FAF2DE]/60 border border-[#D8BD80] shadow-2xs space-y-1">
                  <div className="flex items-center justify-between text-[11px] font-bold text-[#8C6D23] uppercase tracking-wider">
                    <span>Vargottama Planets</span>
                    <Award className="w-4 h-4 text-[#B8862B]" />
                  </div>
                  <div className="text-xl font-serif font-bold text-[#8C6D23]">
                    {vargaData.summary.total_vargottama_count} Grahas
                  </div>
                  <div className="text-xs text-[#52667E] truncate">
                    {vargaData.summary.vargottama_planets.length > 0
                      ? vargaData.summary.vargottama_planets.join(", ")
                      : "None"}
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-emerald-50/70 border border-emerald-200 shadow-2xs space-y-1">
                  <div className="flex items-center justify-between text-[11px] font-bold text-emerald-800 uppercase tracking-wider">
                    <span>Pushkara Navamsas</span>
                    <Star className="w-4 h-4 text-emerald-600 fill-emerald-600" />
                  </div>
                  <div className="text-xl font-serif font-bold text-emerald-900">
                    {vargaData.summary.pushkara_navamsa_planets.length} Grahas
                  </div>
                  <div className="text-xs text-emerald-700 truncate">
                    {vargaData.summary.pushkara_navamsa_planets.length > 0
                      ? vargaData.summary.pushkara_navamsa_planets.join(", ")
                      : "None"}
                  </div>
                </div>
              </div>

              {/* Visual Chart Section */}
              <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[#F1F5F9] pb-4">
                  {/* View Mode Switcher */}
                  <div className="flex items-center gap-1.5 p-1 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] text-xs">
                    <button
                      type="button"
                      onClick={() => setViewMode("side_by_side")}
                      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer ${
                        viewMode === "side_by_side"
                          ? "bg-[#102A4C] text-white shadow-2xs"
                          : "text-[#64748B] hover:text-[#102A4C]"
                      }`}
                    >
                      <Columns className="w-3.5 h-3.5" />
                      <span>{language === "ta" ? "ஒப்பீட்டு பார்வை" : "Side-by-Side View"}</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setViewMode("d1")}
                      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer ${
                        viewMode === "d1"
                          ? "bg-[#102A4C] text-white shadow-2xs"
                          : "text-[#64748B] hover:text-[#102A4C]"
                      }`}
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>D1 Rasi</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setViewMode("d9")}
                      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer ${
                        viewMode === "d9"
                          ? "bg-[#102A4C] text-white shadow-2xs"
                          : "text-[#64748B] hover:text-[#102A4C]"
                      }`}
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>D9 Navamsa</span>
                    </button>
                  </div>

                  {/* Chart Style Switcher */}
                  <div className="flex items-center gap-2 text-xs">
                    <span className="text-[#64748B] font-semibold">Style:</span>
                    <div className="inline-flex p-1 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                      <button
                        type="button"
                        onClick={() => setChartStyle("south")}
                        className={`px-3 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                          chartStyle === "south"
                            ? "bg-[#B8862B] text-white shadow-2xs"
                            : "text-[#64748B] hover:text-[#102A4C]"
                        }`}
                      >
                        South Indian
                      </button>
                      <button
                        type="button"
                        onClick={() => setChartStyle("north")}
                        className={`px-3 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                          chartStyle === "north"
                            ? "bg-[#B8862B] text-white shadow-2xs"
                            : "text-[#64748B] hover:text-[#102A4C]"
                        }`}
                      >
                        North Indian
                      </button>
                    </div>
                  </div>
                </div>

                {/* Charts Grid */}
                {viewMode === "side_by_side" ? (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
                    <div className="space-y-3">
                      <div className="text-center">
                        <h3 className="font-serif text-lg font-bold text-[#102A4C]">
                          D1 Rasi Chakra (ராசி கட்டம்)
                        </h3>
                        <p className="text-xs text-[#64748B]">
                          Physical body, birth disposition, and foundational karma
                        </p>
                      </div>
                      <div className="p-4 rounded-2xl bg-[#FAF7F0] border border-[#E8DEC8]">
                        {chartStyle === "south" ? (
                          <SouthIndianChart
                            horoscope={vargaData.d1_chart as unknown as HoroscopeResponse}
                            isSaved={Boolean(savedIdParam || (inputMode === "saved" && selectedHoroscopeId))}
                          />
                        ) : (
                          <NorthIndianChart
                            horoscope={vargaData.d1_chart as unknown as HoroscopeResponse}
                            isSaved={Boolean(savedIdParam || (inputMode === "saved" && selectedHoroscopeId))}
                          />
                        )}
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div className="text-center">
                        <h3 className="font-serif text-lg font-bold text-[#102A4C]">
                          D9 Navamsa Chakra (நவாம்ச கட்டம்)
                        </h3>
                        <p className="text-xs text-[#64748B]">
                          Inner strength, spiritual fruits, and marital destiny
                        </p>
                      </div>
                      <div className="p-4 rounded-2xl bg-[#FAF7F0] border border-[#E8DEC8]">
                        {chartStyle === "south" ? (
                          <SouthIndianChart
                            horoscope={vargaData.d9_chart as unknown as HoroscopeResponse}
                            isSaved={Boolean(savedIdParam || (inputMode === "saved" && selectedHoroscopeId))}
                          />
                        ) : (
                          <NorthIndianChart
                            horoscope={vargaData.d9_chart as unknown as HoroscopeResponse}
                            isSaved={Boolean(savedIdParam || (inputMode === "saved" && selectedHoroscopeId))}
                          />
                        )}
                      </div>
                    </div>
                  </div>
                ) : viewMode === "d1" ? (
                  <div className="max-w-xl mx-auto space-y-3">
                    <div className="text-center">
                      <h3 className="font-serif text-lg font-bold text-[#102A4C]">
                        D1 Rasi Chakra (ராசி கட்டம்)
                      </h3>
                      <p className="text-xs text-[#64748B]">
                        Ascendant: {vargaData.ascendant.d1_sign_name} ({formatDm(vargaData.ascendant.d1_degree_in_sign)})
                      </p>
                    </div>
                    <div className="p-4 rounded-2xl bg-[#FAF7F0] border border-[#E8DEC8]">
                      {chartStyle === "south" ? (
                        <SouthIndianChart
                          horoscope={vargaData.d1_chart as unknown as HoroscopeResponse}
                          isSaved={Boolean(savedIdParam || (inputMode === "saved" && selectedHoroscopeId))}
                        />
                      ) : (
                        <NorthIndianChart
                          horoscope={vargaData.d1_chart as unknown as HoroscopeResponse}
                          isSaved={Boolean(savedIdParam || (inputMode === "saved" && selectedHoroscopeId))}
                        />
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="max-w-xl mx-auto space-y-3">
                    <div className="text-center">
                      <h3 className="font-serif text-lg font-bold text-[#102A4C]">
                        D9 Navamsa Chakra (நவாம்ச கட்டம்)
                      </h3>
                      <p className="text-xs text-[#64748B]">
                        Navamsa Lagna: {vargaData.ascendant.d9_sign_name} ({formatDm(vargaData.ascendant.d9_degree_in_sign)})
                      </p>
                    </div>
                    <div className="p-4 rounded-2xl bg-[#FAF7F0] border border-[#E8DEC8]">
                      {chartStyle === "south" ? (
                        <SouthIndianChart
                          horoscope={vargaData.d9_chart as unknown as HoroscopeResponse}
                          isSaved={Boolean(savedIdParam || (inputMode === "saved" && selectedHoroscopeId))}
                        />
                      ) : (
                        <NorthIndianChart
                          horoscope={vargaData.d9_chart as unknown as HoroscopeResponse}
                          isSaved={Boolean(savedIdParam || (inputMode === "saved" && selectedHoroscopeId))}
                        />
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Detailed Comparative Planetary Table */}
              <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-4">
                <div>
                  <h3 className="font-serif text-lg font-bold text-[#102A4C]">
                    {language === "ta" ? "கிரக நிலைகள் & வர்கோத்தம ஒப்பீடு" : "D1 / D9 Comparative Planetary Analysis"}
                  </h3>
                  <p className="text-xs text-[#64748B]">
                    Rigorous comparison of signs, houses, nakshatras, and classical dignities.
                  </p>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead className="bg-[#FAF7F0] text-[#8C6D23] font-bold uppercase tracking-wider border-b border-[#E8DEC8]">
                      <tr>
                        <th className="py-3 px-3">Planet / Graha</th>
                        <th className="py-3 px-3">Motion</th>
                        <th className="py-3 px-3">D1 Rasi &amp; House</th>
                        <th className="py-3 px-3">D1 Deg in Sign</th>
                        <th className="py-3 px-3">D9 Navamsa &amp; House</th>
                        <th className="py-3 px-3">Nakshatra &amp; Pada</th>
                        <th className="py-3 px-3">Dignities</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#334155]">
                      <tr className="bg-[#FAF2DE]/20 font-semibold">
                        <td className="py-2.5 px-3 flex items-center gap-1.5 text-[#102A4C]">
                          <Compass className="w-3.5 h-3.5 text-[#B8862B]" />
                          <span>Ascendant (Lagna)</span>
                        </td>
                        <td className="py-2.5 px-3 text-[#64748B]">Direct</td>
                        <td className="py-2.5 px-3 text-[#102A4C]">
                          {vargaData.ascendant.d1_sign_name} (H1)
                        </td>
                        <td className="py-2.5 px-3 font-mono">
                          {formatDm(vargaData.ascendant.d1_degree_in_sign)}
                        </td>
                        <td className="py-2.5 px-3 text-[#102A4C]">
                          {vargaData.ascendant.d9_sign_name} (H1)
                        </td>
                        <td className="py-2.5 px-3">
                          {vargaData.ascendant.nakshatra_name} (P{vargaData.ascendant.pada})
                        </td>
                        <td className="py-2.5 px-3">
                          {vargaData.ascendant.is_vargottama && (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
                              <Award className="w-3 h-3 text-[#B8862B]" />
                              Vargottama
                            </span>
                          )}
                        </td>
                      </tr>

                      {vargaData.planets.map((p: VargaPlanetPosition) => (
                        <tr key={p.name} className="hover:bg-[#FAF6EC]/40 transition-colors">
                          <td className="py-2.5 px-3 font-bold text-[#102A4C]">
                            {p.name}
                            <span className="text-[10px] text-[#8C6D23] ml-1.5 font-normal">
                              ({p.d1_sign_name_tamil})
                            </span>
                          </td>
                          <td className="py-2.5 px-3">
                            {p.is_retrograde ? (
                              <span className="inline-flex items-center px-1.5 py-0.5 rounded-sm text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200">
                                Retro (R)
                              </span>
                            ) : (
                              <span className="text-[#94A3B8]">Direct</span>
                            )}
                          </td>
                          <td className="py-2.5 px-3">
                            <span className="font-semibold text-[#102A4C]">{p.d1_sign_name}</span>{" "}
                            <span className="text-[#64748B]">(H{p.d1_house})</span>
                          </td>
                          <td className="py-2.5 px-3 font-mono text-[#475569]">
                            {formatDm(p.d1_degree_in_sign)}
                          </td>
                          <td className="py-2.5 px-3">
                            <span className="font-semibold text-[#102A4C]">{p.d9_sign_name}</span>{" "}
                            <span className="text-[#64748B]">(H{p.d9_house})</span>
                          </td>
                          <td className="py-2.5 px-3">
                            {p.nakshatra_name} (P{p.pada})
                            <span className="text-[10px] text-[#94A3B8] block">
                              Lord: {p.star_lord}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 space-x-1">
                            {p.is_vargottama && (
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
                                <Award className="w-3 h-3 text-[#B8862B]" />
                                Vargottama
                              </span>
                            )}
                            {p.is_pushkara_navamsa && (
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                                <Star className="w-3 h-3 text-emerald-600 fill-emerald-600" />
                                Pushkara
                              </span>
                            )}
                            {!p.is_vargottama && !p.is_pushkara_navamsa && (
                              <span className="text-[#CBD5E1]">—</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Classical Shastra Reference */}
              <div className="p-6 rounded-2xl bg-[#FAF7F0] border border-[#E8DEC8] text-xs text-[#52667E] space-y-3 shadow-2xs">
                <div className="flex items-center gap-2 text-[#8C6D23] font-bold text-sm">
                  <HelpCircle className="w-4 h-4 text-[#B8862B]" />
                  <span>Classical Jyotish Principles &amp; Mathematical Rigor</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
                  <div className="space-y-1">
                    <strong className="text-[#102A4C] block">D9 Navamsa Purpose</strong>
                    <p className="leading-relaxed">
                      Per <em>Brihat Parashara Hora Shastra</em>, D1 represents the physical seed, while D9 Navamsa represents the fruition (Phala), dharma, spousal compatibility, and inner spiritual vitality.
                    </p>
                  </div>

                  <div className="space-y-1">
                    <strong className="text-[#102A4C] block">Vargottama Dignity</strong>
                    <p className="leading-relaxed">
                      Planets occupying identical signs in D1 and D9 attain Vargottama dignity, equivalent to occupying their own moolatrikona sign with heightened auspiciousness.
                    </p>
                  </div>

                  <div className="space-y-1">
                    <strong className="text-[#102A4C] block">Pushkara Navamsas</strong>
                    <p className="leading-relaxed">
                      Per <em>Jataka Parijata</em> Ch. 1, Sloka 58, exactly 24 out of 108 Navamsas are Pushkara (nourishing). All 24 fall strictly within benefic-ruled signs.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: 16 SHODASHVARGA CHARTS */}
          {activeTab === "shodashvarga" && shodashvargaData && (
            <div className="space-y-6">
              {/* Group Filter Chips */}
              <div className="flex flex-wrap items-center justify-between gap-3 bg-white p-4 rounded-2xl border border-[#DDE5F0] shadow-xs">
                <div className="flex items-center gap-2 text-xs font-semibold text-[#52667E]">
                  <span>{language === "ta" ? "பிரிவு வடிகட்டி:" : "Classical Varga Set:"}</span>
                  <div className="inline-flex p-1 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                    {[
                      { id: "all", label: "All 16 (Shodashvarga)" },
                      { id: "shadvarga", label: "Shadvarga (6)" },
                      { id: "saptavarga", label: "Saptavarga (7)" },
                      { id: "dasavarga", label: "Dasavarga (10)" },
                      { id: "higher", label: "High Karma (D20-D60)" },
                    ].map((f) => (
                      <button
                        key={f.id}
                        type="button"
                        onClick={() => setVargaFilter(f.id as any)}
                        className={`px-3 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                          vargaFilter === f.id
                            ? "bg-[#102A4C] text-white shadow-2xs"
                            : "text-[#64748B] hover:text-[#102A4C]"
                        }`}
                      >
                        {f.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Chart Style Switcher */}
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-[#64748B] font-semibold">Style:</span>
                  <div className="inline-flex p-1 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                    <button
                      type="button"
                      onClick={() => setChartStyle("south")}
                      className={`px-3 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                        chartStyle === "south"
                          ? "bg-[#B8862B] text-white shadow-2xs"
                          : "text-[#64748B] hover:text-[#102A4C]"
                      }`}
                    >
                      South Indian
                    </button>
                    <button
                      type="button"
                      onClick={() => setChartStyle("north")}
                      className={`px-3 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                        chartStyle === "north"
                          ? "bg-[#B8862B] text-white shadow-2xs"
                          : "text-[#64748B] hover:text-[#102A4C]"
                      }`}
                    >
                      North Indian
                    </button>
                  </div>
                </div>
              </div>

              {/* 16 Varga Quick Picker Carousel / Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-8 gap-2.5">
                {filteredVargas.map((v) => {
                  const isSelected = selectedVargaKey === v.key;
                  return (
                    <button
                      key={v.key}
                      type="button"
                      onClick={() => setSelectedVargaKey(v.key)}
                      className={`p-3 rounded-xl border text-left transition-all cursor-pointer flex flex-col justify-between ${
                        isSelected
                          ? "border-[#B8862B] bg-gradient-to-br from-[#FAF2DE] to-[#F5E6BE] text-[#102A4C] shadow-sm ring-2 ring-[#B8862B]/30"
                          : "border-[#E2E8F0] bg-white hover:border-[#CBD5E1] text-[#334155]"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-xs font-extrabold text-[#B8862B]">
                          {v.key}
                        </span>
                        <span className="text-[10px] text-[#94A3B8] font-bold">
                          1/{v.num}
                        </span>
                      </div>
                      <div className="mt-1">
                        <div className="font-bold text-xs truncate">
                          {language === "ta" ? v.nameTa : v.nameEn}
                        </div>
                        <div className="text-[10px] text-[#64748B] truncate mt-0.5">
                          {language === "ta" ? v.focusTa : v.focusEn}
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>

              {/* Selected Varga Showcase */}
              {selectedVargaItem && (
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                  {/* Left Column: Visual Chart & Lagna Specs */}
                  <div className="lg:col-span-6 space-y-4">
                    <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-4">
                      {/* Varga Header Banner */}
                      <div className="flex items-start justify-between border-b border-[#F1F5F9] pb-3">
                        <div>
                          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md text-[11px] font-bold bg-[#FAF2DE] text-[#8C6D23]">
                            {selectedVargaItem.division_id} • 1/{selectedVargaItem.division_number}th Division
                          </div>
                          <h3 className="font-serif text-xl font-bold text-[#102A4C] mt-1">
                            {selectedVargaItem.name} Chakra ({selectedVargaItem.name_tamil})
                          </h3>
                          <p className="text-xs text-[#52667E] mt-0.5">
                            {language === "ta" ? selectedVargaItem.significance_tamil : selectedVargaItem.significance}
                          </p>
                        </div>
                        <div className="text-right text-[11px] font-mono text-[#64748B] shrink-0">
                          <div>Span: {selectedVargaItem.span_degrees.toFixed(2)}°</div>
                          <div className="text-[10px] text-[#94A3B8]">per division</div>
                        </div>
                      </div>

                      {/* Lagna Quick Badge */}
                      <div className="flex items-center justify-between p-3 rounded-xl bg-[#FAF7F0] border border-[#E8DEC8] text-xs">
                        <div className="flex items-center gap-2">
                          <Compass className="w-4 h-4 text-[#B8862B]" />
                          <div>
                            <span className="text-[#8C6D23] font-bold">
                              {selectedVargaItem.division_id} Ascendant (Lagna):
                            </span>{" "}
                            <span className="font-bold text-[#102A4C]">
                              {selectedVargaItem.ascendant.sign_name} ({selectedVargaItem.ascendant.sign_name_tamil})
                            </span>
                          </div>
                        </div>
                        <div className="text-[#64748B] font-mono">
                          {formatDm(selectedVargaItem.ascendant.degree_in_sign)} • Lord: {selectedVargaItem.ascendant.sign_lord}
                        </div>
                      </div>

                      {/* Chart Render Canvas */}
                      <div className="p-4 rounded-2xl bg-[#FAF7F0] border border-[#E8DEC8]">
                        {chartStyle === "south" ? (
                          <SouthIndianChart
                            horoscope={selectedVargaItem.chart as unknown as HoroscopeResponse}
                            isSaved={Boolean(savedIdParam || (inputMode === "saved" && selectedHoroscopeId))}
                          />
                        ) : (
                          <NorthIndianChart
                            horoscope={selectedVargaItem.chart as unknown as HoroscopeResponse}
                            isSaved={Boolean(savedIdParam || (inputMode === "saved" && selectedHoroscopeId))}
                          />
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Right Column: Planetary Positions & Dignities in this Division */}
                  <div className="lg:col-span-6 space-y-4">
                    <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-4">
                      <div>
                        <h4 className="font-serif text-base font-bold text-[#102A4C]">
                          Planetary Placements in {selectedVargaItem.division_id} ({selectedVargaItem.name})
                        </h4>
                        <p className="text-xs text-[#64748B]">
                          Whole-sign house placement relative to {selectedVargaItem.division_id} Lagna.
                        </p>
                      </div>

                      <div className="overflow-x-auto">
                        <table className="w-full text-xs text-left">
                          <thead className="bg-[#FAF7F0] text-[#8C6D23] font-bold uppercase tracking-wider border-b border-[#E8DEC8]">
                            <tr>
                              <th className="py-2.5 px-3">Graha</th>
                              <th className="py-2.5 px-3">Sign</th>
                              <th className="py-2.5 px-3">House</th>
                              <th className="py-2.5 px-3">Deg in Sign</th>
                              <th className="py-2.5 px-3">Lord</th>
                              <th className="py-2.5 px-3">Dignity</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#334155]">
                            {/* Ascendant Row */}
                            <tr className="bg-[#FAF2DE]/20 font-semibold">
                              <td className="py-2 px-3 text-[#102A4C] flex items-center gap-1">
                                <Compass className="w-3 h-3 text-[#B8862B]" />
                                Lagna
                              </td>
                              <td className="py-2 px-3">
                                {selectedVargaItem.ascendant.sign_name}
                              </td>
                              <td className="py-2 px-3 text-[#64748B]">H1</td>
                              <td className="py-2 px-3 font-mono">
                                {formatDm(selectedVargaItem.ascendant.degree_in_sign)}
                              </td>
                              <td className="py-2 px-3">{selectedVargaItem.ascendant.sign_lord}</td>
                              <td className="py-2 px-3">
                                {selectedVargaItem.ascendant.is_vargottama && (
                                  <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-sm text-[10px] font-bold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
                                    Vargottama
                                  </span>
                                )}
                              </td>
                            </tr>

                            {/* Planets Rows */}
                            {selectedVargaItem.planets.map((p: ShodashvargaPlanetEntry) => (
                              <tr key={p.name} className="hover:bg-[#FAF6EC]/40 transition-colors">
                                <td className="py-2 px-3 font-bold text-[#102A4C]">
                                  {p.name}
                                  {p.is_retrograde && (
                                    <span className="text-[10px] text-rose-600 font-bold ml-1">
                                      (R)
                                    </span>
                                  )}
                                </td>
                                <td className="py-2 px-3">
                                  <span className="font-semibold">{p.sign_name}</span>{" "}
                                  <span className="text-[10px] text-[#8C6D23]">
                                    ({p.sign_name_tamil})
                                  </span>
                                </td>
                                <td className="py-2 px-3">
                                  <span className="px-1.5 py-0.5 rounded-sm bg-[#F1F5F9] text-[#475569] font-bold text-[10px]">
                                    H{p.house}
                                  </span>
                                </td>
                                <td className="py-2 px-3 font-mono text-[#64748B]">
                                  {formatDm(p.degree_in_sign)}
                                </td>
                                <td className="py-2 px-3">{p.sign_lord}</td>
                                <td className="py-2 px-3 space-x-1">
                                  {p.is_vargottama && (
                                    <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-sm text-[10px] font-bold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
                                      <Award className="w-2.5 h-2.5 text-[#B8862B]" />
                                      Vargottama
                                    </span>
                                  )}
                                  {selectedVargaKey === "D60" && p.shashtyamsa_deity && (
                                    <span
                                      className={`inline-flex items-center px-1.5 py-0.5 rounded-sm text-[10px] font-bold border ${
                                        p.shashtyamsa_nature === "Benefic"
                                          ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                                          : p.shashtyamsa_nature === "Malefic"
                                          ? "bg-rose-50 text-rose-700 border-rose-200"
                                          : "bg-slate-100 text-slate-700 border-slate-200"
                                      }`}
                                    >
                                      {p.shashtyamsa_deity}
                                    </span>
                                  )}
                                  {!p.is_vargottama && selectedVargaKey !== "D60" && (
                                    <span className="text-[#CBD5E1]">—</span>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>

                      {/* Classical Insight for Selected Varga */}
                      <div className="p-4 rounded-xl bg-[#FAF7F0] border border-[#E8DEC8] text-xs text-[#52667E] space-y-1">
                        <div className="flex items-center gap-1.5 font-bold text-[#8C6D23]">
                          <BookOpen className="w-3.5 h-3.5 text-[#B8862B]" />
                          <span>Astrological Significance &amp; Usage</span>
                        </div>
                        <p className="leading-relaxed">
                          {selectedVargaKey === "D10" &&
                            "Dasamsa (D10) is the primary chart for career achievements, professional honors, promotions, business acumen, and public standing. Planets in 1st, 10th, and 9th houses in D10 give supreme career fruits."}
                          {selectedVargaKey === "D7" &&
                            "Saptamsa (D7) is evaluated specifically for progeny, lineage continuation, relationship with children, and the karmic fruits of children's prosperity."}
                          {selectedVargaKey === "D12" &&
                            "Dwadasamsa (D12) reveals parental influences, ancestral heritage, pitru karma, genetic inclinations, and past familial bonds."}
                          {selectedVargaKey === "D60" &&
                            "Shashtyamsa (D60) is the supreme karmic chart possessing highest weight in Shadbala. Per BPHS, every planet must be judged in D60 to finalize its auspicious or inauspicious phala."}
                          {selectedVargaKey === "D2" &&
                            "Hora (D2) divides each sign into Sun (Solar/Pingala - initiative & vitality) and Moon (Lunar/Ida - wealth accumulation & nourishment)."}
                          {selectedVargaKey === "D3" &&
                            "Drekkana (D3) indicates siblings, courage, initiatives, physical vigor, and the 22nd Drekkana (Kharesha) for arishta analysis."}
                          {selectedVargaKey === "D4" &&
                            "Chaturthamsa (D4) reveals luck, fixed real estate, landed properties, mother's happiness, and material fortune."}
                          {selectedVargaKey === "D16" &&
                            "Shodasamsa (D16) evaluates vehicles, comforts of conveyance, mental tranquility, and happiness derived from material conveniences."}
                          {selectedVargaKey === "D20" &&
                            "Vimsamsa (D20) reflects religious devotion, spiritual initiation (Upasana), mantra siddhi, and past spiritual merits."}
                          {selectedVargaKey === "D24" &&
                            "Chaturvimsamsa (D24) governs higher learning, academic honors, retention of knowledge, and intellectual prowess."}
                          {selectedVargaKey === "D27" &&
                            "Saptavimsamsa (D27) reveals internal vitality, subconscious strengths, physical endurance, and latent weaknesses."}
                          {selectedVargaKey === "D30" &&
                            "Trimsamsa (D30) evaluates hidden misfortunes, disease afflictions, moral vulnerabilities, and past unatoned karmic debts."}
                          {selectedVargaKey === "D40" &&
                            "Khavedamsa (D40) governs overall auspicious and inauspicious auspiciousness, maternal ancestral karma, and character."}
                          {selectedVargaKey === "D45" &&
                            "Akshavedamsa (D45) evaluates all matters in life, purity of mind, moral righteousness, and divine protection."}
                          {selectedVargaKey === "D1" &&
                            "Rasi (D1) is the foundational physical manifestation, vitality, and external framework through which all other divisional vargas express."}
                          {selectedVargaKey === "D9" &&
                            "Navamsa (D9) is the celestial mirror revealing inner potential, marital happiness, dharma, and destiny after age 28-32."}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: 16-VARGA PLANETARY MATRIX (VARGA-BALA) */}
          {activeTab === "matrix" && shodashvargaData && (
            <div className="space-y-6">
              <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-[#F1F5F9] pb-4">
                  <div>
                    <h3 className="font-serif text-lg font-bold text-[#102A4C]">
                      {language === "ta"
                        ? "16 வர்க்க கிரக அணி (வர்க்க பலம்)"
                        : "16-Varga Planetary Matrix (Varga-Bala Cross-Tabulation)"}
                    </h3>
                    <p className="text-xs text-[#64748B]">
                      Cross-tabulation of all 9 Grahas and Lagna across all 16 canonical divisions per BPHS Ch. 6.
                    </p>
                  </div>
                  <div className="flex items-center gap-3 text-xs">
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-[#FAF2DE] text-[#8C6D23] font-bold border border-[#D8BD80]">
                      <span className="w-2 h-2 rounded-full bg-[#B8862B]" />
                      Vargottama (D1 Match)
                    </span>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-center border-collapse">
                    <thead>
                      <tr className="bg-[#FAF7F0] text-[#8C6D23] font-bold border-b border-[#E8DEC8]">
                        <th className="py-3 px-3 text-left">Graha / Body</th>
                        {SHODASHVARGA_LIST.map((v) => (
                          <th key={v.key} className="py-3 px-2 font-mono">
                            <div>{v.key}</div>
                            <div className="text-[9px] font-normal text-[#64748B]">{v.num}</div>
                          </th>
                        ))}
                        <th className="py-3 px-3 text-right">Vargottama Dignity</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#334155]">
                      {/* Lagna Row */}
                      {(() => {
                        const lagnaVargas = shodashvargaData.planet_vargas["Lagna"] || {};
                        const d1Sign = lagnaVargas["D1"];
                        let vargottamaMatches = 0;
                        SHODASHVARGA_LIST.forEach((v) => {
                          if (v.key !== "D1" && lagnaVargas[v.key] === d1Sign) {
                            vargottamaMatches++;
                          }
                        });

                        return (
                          <tr className="bg-[#FAF2DE]/30 font-semibold">
                            <td className="py-2.5 px-3 text-left font-bold text-[#102A4C] flex items-center gap-1.5">
                              <Compass className="w-3.5 h-3.5 text-[#B8862B]" />
                              <span>Lagna</span>
                            </td>
                            {SHODASHVARGA_LIST.map((v) => {
                              const sIdx = lagnaVargas[v.key] || 1;
                              const isMatch = v.key !== "D1" && sIdx === d1Sign;
                              const signInfo = SIGN_SHORT_MAP[sIdx] || { en: "---", ta: "-" };
                              return (
                                <td
                                  key={v.key}
                                  className={`py-2 px-1 text-[11px] font-mono ${
                                    isMatch
                                      ? "bg-[#FAF2DE] text-[#8C6D23] font-bold border border-[#D8BD80]"
                                      : "text-[#475569]"
                                  }`}
                                  title={`${v.key}: Sign ${sIdx} (${signInfo.en})`}
                                >
                                  {language === "ta" ? signInfo.ta : signInfo.en}
                                </td>
                              );
                            })}
                            <td className="py-2.5 px-3 text-right font-bold text-[#8C6D23]">
                              {vargottamaMatches > 0 ? `${vargottamaMatches} Vargas` : "—"}
                            </td>
                          </tr>
                        );
                      })()}

                      {/* Planets Rows */}
                      {["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"].map((pName) => {
                        const pVargas = shodashvargaData.planet_vargas[pName] || {};
                        const d1Sign = pVargas["D1"];
                        let vargottamaMatches = 0;
                        SHODASHVARGA_LIST.forEach((v) => {
                          if (v.key !== "D1" && pVargas[v.key] === d1Sign) {
                            vargottamaMatches++;
                          }
                        });

                        return (
                          <tr key={pName} className="hover:bg-[#FAF6EC]/40 transition-colors">
                            <td className="py-2.5 px-3 text-left font-bold text-[#102A4C]">
                              {pName}
                            </td>
                            {SHODASHVARGA_LIST.map((v) => {
                              const sIdx = pVargas[v.key] || 1;
                              const isMatch = v.key !== "D1" && sIdx === d1Sign;
                              const signInfo = SIGN_SHORT_MAP[sIdx] || { en: "---", ta: "-" };
                              return (
                                <td
                                  key={v.key}
                                  className={`py-2 px-1 text-[11px] font-mono ${
                                    isMatch
                                      ? "bg-[#FAF2DE] text-[#8C6D23] font-bold border border-[#D8BD80]"
                                      : "text-[#475569]"
                                  }`}
                                  title={`${v.key}: Sign ${sIdx} (${signInfo.en})`}
                                >
                                  {language === "ta" ? signInfo.ta : signInfo.en}
                                </td>
                              );
                            })}
                            <td className="py-2.5 px-3 text-right font-bold">
                              {vargottamaMatches > 0 ? (
                                <span className="inline-flex items-center gap-1 text-[#8C6D23]">
                                  <Award className="w-3 h-3 text-[#B8862B]" />
                                  {vargottamaMatches} Vargas
                                </span>
                              ) : (
                                <span className="text-[#CBD5E1]">—</span>
                              )}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

                {/* Vaisheshikamsa Classical Benchmark Card */}
                <div className="p-5 rounded-2xl bg-[#FAF7F0] border border-[#E8DEC8] text-xs space-y-3">
                  <div className="flex items-center gap-2 font-bold text-[#8C6D23]">
                    <ShieldCheck className="w-4 h-4 text-[#B8862B]" />
                    <span>Classical Vaisheshikamsa Dignity Scale (BPHS Ch. 6)</span>
                  </div>
                  <p className="text-[#52667E] leading-relaxed">
                    When a planet occupies its own, moolatrikona, exaltation, or identical (Vargottama) sign across multiple divisional charts, it attains celebrated named dignities that multiply its benefic yield:
                  </p>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2 text-[11px]">
                    <div className="p-2 rounded-lg bg-white border border-[#E8DEC8]">
                      <span className="font-bold text-[#102A4C]">2 Vargas:</span> Parijata
                    </div>
                    <div className="p-2 rounded-lg bg-white border border-[#E8DEC8]">
                      <span className="font-bold text-[#102A4C]">3 Vargas:</span> Uttama
                    </div>
                    <div className="p-2 rounded-lg bg-white border border-[#E8DEC8]">
                      <span className="font-bold text-[#102A4C]">4 Vargas:</span> Gopura
                    </div>
                    <div className="p-2 rounded-lg bg-white border border-[#E8DEC8]">
                      <span className="font-bold text-[#102A4C]">5 Vargas:</span> Simhasana
                    </div>
                    <div className="p-2 rounded-lg bg-white border border-[#E8DEC8]">
                      <span className="font-bold text-[#102A4C]">6 Vargas:</span> Paravata
                    </div>
                    <div className="p-2 rounded-lg bg-white border border-[#E8DEC8]">
                      <span className="font-bold text-[#102A4C]">7 Vargas:</span> Devaloka
                    </div>
                    <div className="p-2 rounded-lg bg-white border border-[#E8DEC8]">
                      <span className="font-bold text-[#102A4C]">8 Vargas:</span> Iravata
                    </div>
                    <div className="p-2 rounded-lg bg-white border border-[#E8DEC8]">
                      <span className="font-bold text-[#102A4C]">9 Vargas:</span> Vaishnava
                    </div>
                    <div className="p-2 rounded-lg bg-white border border-[#E8DEC8]">
                      <span className="font-bold text-[#102A4C]">10 Vargas:</span> Saiva
                    </div>
                    <div className="p-2 rounded-lg bg-white border border-[#E8DEC8]">
                      <span className="font-bold text-[#102A4C]">11 Vargas:</span> Bhasvada
                    </div>
                    <div className="p-2 rounded-lg bg-white border border-[#E8DEC8] col-span-2">
                      <span className="font-bold text-[#102A4C]">12-16 Vargas:</span> Vaisheshikamsa
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: D60 SHASHTYAMSA KARMA DEITIES */}
          {activeTab === "d60_deities" && shodashvargaData && (
            <div className="space-y-6">
              {/* Introduction Banner */}
              <div className="p-6 rounded-2xl bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 shadow-xs space-y-2">
                <div className="flex items-center gap-2 text-amber-900 font-bold">
                  <Flame className="w-5 h-5 text-amber-600 fill-amber-600" />
                  <h3 className="font-serif text-lg">
                    {language === "ta"
                      ? "D60 சஷ்டியாம்ச கர்மா அதிதேவதைகள் ஆய்வு"
                      : "D60 Shashtyamsa Karma Deities — The Ultimate Decider"}
                  </h3>
                </div>
                <p className="text-xs text-amber-800 leading-relaxed max-w-4xl">
                  {language === "ta"
                    ? "பிரகத் பராசர ஹோரா சாஸ்திரத்தின்படி, D60 சஷ்டியாம்சமே அனைத்து வர்க்கங்களிலும் அதிமுக்கியமானது. 30 கலைகள் (0° 30') மட்டுமே கொண்ட இந்த நுட்பமான பிரிவில், 60 சாஸ்திர தேவதைகள் ஆளுகை செய்கின்றனர். இரட்டை குழந்தைகள் வெவ்வேறு வாழ்வை அடைவதற்கு D60 தேவதைகளே மூலக் காரணமாக விளங்குகின்றனர்."
                    : "Per Brihat Parashara Hora Shastra Ch. 6, Shashtyamsa (1/60th division, spanning exactly 0°30' of arc) is the supreme decider of past karmic fruits (Prarabdha Karma). Each 30 minutes of arc is ruled by one of the 60 classical deities whose benefic or malefic nature seals the final quality of the planet's results."}
                </p>
              </div>

              {/* Deities Table */}
              {shodashvargaData.charts?.["D60"] && (
                <div className="p-6 rounded-2xl bg-white border border-[#DDE5F0] shadow-xs space-y-4">
                  <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
                    <h4 className="font-serif text-base font-bold text-[#102A4C]">
                      Natal Placements &amp; Corresponding Shashtyamsa Deities
                    </h4>
                    <span className="text-xs text-[#64748B] font-mono">
                      Division Span: 0° 30&apos; 00&quot;
                    </span>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left">
                      <thead className="bg-[#FAF7F0] text-[#8C6D23] font-bold uppercase tracking-wider border-b border-[#E8DEC8]">
                        <tr>
                          <th className="py-3 px-3">Celestial Body</th>
                          <th className="py-3 px-3">D60 Sign &amp; Degree</th>
                          <th className="py-3 px-3">Shashtyamsa Part</th>
                          <th className="py-3 px-3">Deity (Sanskrit)</th>
                          <th className="py-3 px-3">Deity (Tamil)</th>
                          <th className="py-3 px-3">Nature</th>
                          <th className="py-3 px-3">Karmic Significance</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#334155]">
                        {/* Ascendant Lagna */}
                        {(() => {
                          const d60Asc = shodashvargaData.charts["D60"].ascendant;
                          const partNum = Math.floor(d60Asc.degree_in_sign * 2) + 1;
                          const isBenefic = d60Asc.shashtyamsa_nature === "Benefic";
                          const isMalefic = d60Asc.shashtyamsa_nature === "Malefic";

                          return (
                            <tr className="bg-amber-50/40 font-semibold">
                              <td className="py-3 px-3 text-[#102A4C] flex items-center gap-1.5 font-bold">
                                <Compass className="w-4 h-4 text-[#B8862B]" />
                                Ascendant (Lagna)
                              </td>
                              <td className="py-3 px-3">
                                {d60Asc.sign_name} ({formatDm(d60Asc.degree_in_sign)})
                              </td>
                              <td className="py-3 px-3 font-mono font-bold text-[#8C6D23]">
                                #{partNum} / 60
                              </td>
                              <td className="py-3 px-3 font-bold text-[#102A4C]">
                                {d60Asc.shashtyamsa_deity || "—"}
                              </td>
                              <td className="py-3 px-3 font-bold text-[#8C6D23]">
                                {d60Asc.shashtyamsa_deity_tamil || "—"}
                              </td>
                              <td className="py-3 px-3">
                                <span
                                  className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold border ${
                                    isBenefic
                                      ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                                      : isMalefic
                                      ? "bg-rose-50 text-rose-700 border-rose-200"
                                      : "bg-slate-100 text-slate-700 border-slate-200"
                                  }`}
                                >
                                  {d60Asc.shashtyamsa_nature || "Neutral"}
                                </span>
                              </td>
                              <td className="py-3 px-3 text-[#64748B]">
                                Foundation of the entire physical life blueprint and primal soul disposition.
                              </td>
                            </tr>
                          );
                        })()}

                        {/* Planets */}
                        {shodashvargaData.charts["D60"].planets.map((p: ShodashvargaPlanetEntry) => {
                          const partNum = Math.floor(p.degree_in_sign * 2) + 1;
                          const isBenefic = p.shashtyamsa_nature === "Benefic";
                          const isMalefic = p.shashtyamsa_nature === "Malefic";

                          return (
                            <tr key={p.name} className="hover:bg-[#FAF6EC]/40 transition-colors">
                              <td className="py-2.5 px-3 font-bold text-[#102A4C]">
                                {p.name}
                                {p.is_retrograde && (
                                  <span className="text-[10px] text-rose-600 ml-1 font-bold">
                                    (R)
                                  </span>
                                )}
                              </td>
                              <td className="py-2.5 px-3">
                                {p.sign_name} ({formatDm(p.degree_in_sign)})
                              </td>
                              <td className="py-2.5 px-3 font-mono font-bold text-[#8C6D23]">
                                #{partNum} / 60
                              </td>
                              <td className="py-2.5 px-3 font-bold text-[#102A4C]">
                                {p.shashtyamsa_deity || "—"}
                              </td>
                              <td className="py-2.5 px-3 text-[#8C6D23]">
                                {p.shashtyamsa_deity_tamil || "—"}
                              </td>
                              <td className="py-2.5 px-3">
                                <span
                                  className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold border ${
                                    isBenefic
                                      ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                                      : isMalefic
                                      ? "bg-rose-50 text-rose-700 border-rose-200"
                                      : "bg-slate-100 text-slate-700 border-slate-200"
                                  }`}
                                >
                                  {p.shashtyamsa_nature || "Neutral"}
                                </span>
                              </td>
                              <td className="py-2.5 px-3 text-[#64748B]">
                                {isBenefic
                                  ? "Auspicious past-life merit; bestows effortless protection during its Dasha."
                                  : isMalefic
                                  ? "Karmic friction or testing ground; requires focused remedial prayers and conscious dharma."
                                  : "Balanced karmic ledger; depends on planetary dignity in D1 and D9."}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function D1D9Page() {
  return (
    <Suspense
      fallback={
        <div className="min-h-[50vh] flex items-center justify-center">
          <div className="w-8 h-8 border-4 border-[#B8862B] border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <D1D9Content />
    </Suspense>
  );
}
