"use client";

import React, { useState, useEffect, useMemo, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  fetchNakshatras,
  fetchFunctionalNatures,
  checkActivitySuitability as fetchActivityCheck,
  checkPadaDosha as fetchPadaDosha,
} from "@/lib/api";
import {
  NakshatraItem,
  FunctionalNatureGroup,
  ActivityCheckResult,
  PadaDoshaResult,
} from "@/lib/types";
import {
  Star,
  Search,
  Filter,
  CheckCircle2,
  AlertTriangle,
  Info,
  Shield,
  Compass,
  ArrowRight,
  BookOpen,
  Sparkles,
  Calendar,
  X,
  ExternalLink,
  Layers,
  ChevronRight,
} from "lucide-react";

// Canonical fallback data for all 28 Nakshatras (including Abhijit)
const CANONICAL_28_NAKSHATRAS: Partial<NakshatraItem>[] = [
  { id: 1, name: "Ashwini", name_tamil: "அஸ்வினி", ruling_planet: "Ketu", ruling_deity: "Ashwini Kumaras", functional_nature: "Light / Swift", functional_nature_tamil: "லகு / சுறுசுறுப்பு", span_zodiac: "00°00' - 13°20' Aries", gender: "Masculine", result_grade: "GOOD", symbol_shape: "Horse head", gaze_direction: "Forward", gaze_direction_tamil: "நேர் பார்வை" },
  { id: 2, name: "Bharani", name_tamil: "பரணி", ruling_planet: "Venus", ruling_deity: "Yama", functional_nature: "Fierce / Cruel", functional_nature_tamil: "உக்கிர / தீவிர", span_zodiac: "13°20' - 26°40' Aries", gender: "Feminine", result_grade: "HARM", symbol_shape: "Yoni / Triangle", gaze_direction: "Downward", gaze_direction_tamil: "கீழ் பார்வை" },
  { id: 3, name: "Krittika", name_tamil: "கார்த்திகை", ruling_planet: "Sun", ruling_deity: "Agni", functional_nature: "Mixed / Ordinary", functional_nature_tamil: "மிஸ்ர / கலப்பு", span_zodiac: "26°40' Aries - 10°00' Taurus", gender: "Feminine", result_grade: "HARM", symbol_shape: "Razor / Flame", gaze_direction: "Downward", gaze_direction_tamil: "கீழ் பார்வை" },
  { id: 4, name: "Rohini", name_tamil: "ரோகிணி", ruling_planet: "Moon", ruling_deity: "Brahma / Prajapati", functional_nature: "Fixed / Steady", functional_nature_tamil: "ஸ்திர / நிலையான", span_zodiac: "10°00' - 23°20' Taurus", gender: "Feminine", result_grade: "GOOD", symbol_shape: "Chariot / Cart", gaze_direction: "Upward", gaze_direction_tamil: "மேல் பார்வை" },
  { id: 5, name: "Mrigashira", name_tamil: "மிருகசீரிஷம்", ruling_planet: "Mars", ruling_deity: "Soma / Moon God", functional_nature: "Soft / Gentle", functional_nature_tamil: "மிருதுவான / சாந்த", span_zodiac: "23°20' Taurus - 06°40' Gemini", gender: "Hermaphrodite", result_grade: "GOOD", symbol_shape: "Deer head", gaze_direction: "Forward", gaze_direction_tamil: "நேர் பார்வை" },
  { id: 6, name: "Ardra", name_tamil: "திருவாதிரை", ruling_planet: "Rahu", ruling_deity: "Rudra", functional_nature: "Sharp / Dreadful", functional_nature_tamil: "தீட்சண / கொடிய", span_zodiac: "06°40' - 20°00' Gemini", gender: "Feminine", result_grade: "HARM", symbol_shape: "Teardrop / Diamond", gaze_direction: "Upward", gaze_direction_tamil: "மேல் பார்வை" },
  { id: 7, name: "Punarvasu", name_tamil: "புனர்பூசம்", ruling_planet: "Jupiter", ruling_deity: "Aditi", functional_nature: "Movable / Ephemeral", functional_nature_tamil: "சர / மாற்றக்கூடிய", span_zodiac: "20°00' Gemini - 03°20' Cancer", gender: "Masculine", result_grade: "GOOD", symbol_shape: "Bow and Quiver", gaze_direction: "Forward", gaze_direction_tamil: "நேர் பார்வை" },
  { id: 8, name: "Pushya", name_tamil: "பூசம்", ruling_planet: "Saturn", ruling_deity: "Brihaspati", functional_nature: "Light / Swift", functional_nature_tamil: "லகு / சுறுசுறுப்பு", span_zodiac: "03°20' - 16°40' Cancer", gender: "Masculine", result_grade: "GOOD", symbol_shape: "Cow udder / Lotus", gaze_direction: "Upward", gaze_direction_tamil: "மேல் பார்வை" },
  { id: 9, name: "Ashlesha", name_tamil: "ஆயில்யம்", ruling_planet: "Mercury", ruling_deity: "Sarpas / Nagas", functional_nature: "Sharp / Dreadful", functional_nature_tamil: "தீட்சண / கொடிய", span_zodiac: "16°40' - 30°00' Cancer", gender: "Feminine", result_grade: "HARM", symbol_shape: "Coiled serpent", gaze_direction: "Downward", gaze_direction_tamil: "கீழ் பார்வை" },
  { id: 10, name: "Magha", name_tamil: "மகம்", ruling_planet: "Ketu", ruling_deity: "Pitrus", functional_nature: "Fierce / Cruel", functional_nature_tamil: "உக்கிர / தீவிர", span_zodiac: "00°00' - 13°20' Leo", gender: "Feminine", result_grade: "HARM", symbol_shape: "Royal Throne", gaze_direction: "Downward", gaze_direction_tamil: "கீழ் பார்வை" },
  { id: 11, name: "Purva Phalguni", name_tamil: "பூரம்", ruling_planet: "Venus", ruling_deity: "Bhaga", functional_nature: "Fierce / Cruel", functional_nature_tamil: "உக்கிர / தீவிர", span_zodiac: "13°20' - 26°40' Leo", gender: "Feminine", result_grade: "HARM", symbol_shape: "Front legs of bed", gaze_direction: "Upward", gaze_direction_tamil: "மேல் பார்வை" },
  { id: 12, name: "Uttara Phalguni", name_tamil: "உத்திரம்", ruling_planet: "Sun", ruling_deity: "Aryaman", functional_nature: "Fixed / Steady", functional_nature_tamil: "ஸ்திர / நிலையான", span_zodiac: "26°40' Leo - 10°00' Virgo", gender: "Masculine", result_grade: "GOOD", symbol_shape: "Back legs of bed", gaze_direction: "Upward", gaze_direction_tamil: "மேல் பார்வை" },
  { id: 13, name: "Hasta", name_tamil: "அஸ்தம்", ruling_planet: "Moon", ruling_deity: "Savitar", functional_nature: "Light / Swift", functional_nature_tamil: "லகு / சுறுசுறுப்பு", span_zodiac: "10°00' - 23°20' Virgo", gender: "Masculine", result_grade: "GOOD", symbol_shape: "Open Hand / Palm", gaze_direction: "Forward", gaze_direction_tamil: "நேர் பார்வை" },
  { id: 14, name: "Chitra", name_tamil: "சித்திரை", ruling_planet: "Mars", ruling_deity: "Vishwakarma / Tvashtar", functional_nature: "Soft / Gentle", functional_nature_tamil: "மிருதுவான / சாந்த", span_zodiac: "23°20' Virgo - 06°40' Libra", gender: "Feminine", result_grade: "GOOD", symbol_shape: "Bright Jewel / Pearl", gaze_direction: "Forward", gaze_direction_tamil: "நேர் பார்வை" },
  { id: 15, name: "Swati", name_tamil: "சுவாதி", ruling_planet: "Rahu", ruling_deity: "Vayu", functional_nature: "Movable / Ephemeral", functional_nature_tamil: "சர / மாற்றக்கூடிய", span_zodiac: "06°40' - 20°00' Libra", gender: "Feminine", result_grade: "GOOD", symbol_shape: "Young shoot blowing in wind", gaze_direction: "Forward", gaze_direction_tamil: "நேர் பார்வை" },
  { id: 16, name: "Vishakha", name_tamil: "விசாகம்", ruling_planet: "Jupiter", ruling_deity: "Indragni", functional_nature: "Mixed / Ordinary", functional_nature_tamil: "மிஸ்ர / கலப்பு", span_zodiac: "20°00' Libra - 03°20' Scorpio", gender: "Feminine", result_grade: "HARM", symbol_shape: "Triumphal Arch / Potter's wheel", gaze_direction: "Downward", gaze_direction_tamil: "கீழ் பார்வை" },
  { id: 17, name: "Anuradha", name_tamil: "அனுஷம்", ruling_planet: "Saturn", ruling_deity: "Mitra", functional_nature: "Soft / Gentle", functional_nature_tamil: "மிருதுவான / சாந்த", span_zodiac: "03°20' - 16°40' Scorpio", gender: "Masculine", result_grade: "GOOD", symbol_shape: "Lotus flower / Staff", gaze_direction: "Forward", gaze_direction_tamil: "நேர் பார்வை" },
  { id: 18, name: "Jyeshtha", name_tamil: "கேட்டை", ruling_planet: "Mercury", ruling_deity: "Indra", functional_nature: "Sharp / Dreadful", functional_nature_tamil: "தீட்சண / கொடிய", span_zodiac: "16°40' - 30°00' Scorpio", gender: "Feminine", result_grade: "HARM", symbol_shape: "Circular Amulet / Umbrella", gaze_direction: "Forward", gaze_direction_tamil: "நேர் பார்வை" },
  { id: 19, name: "Mula", name_tamil: "மூலம்", ruling_planet: "Ketu", ruling_deity: "Nirriti", functional_nature: "Sharp / Dreadful", functional_nature_tamil: "தீட்சண / கொடிய", span_zodiac: "00°00' - 13°20' Sagittarius", gender: "Hermaphrodite", result_grade: "HARM", symbol_shape: "Tied bunch of roots", gaze_direction: "Downward", gaze_direction_tamil: "கீழ் பார்வை" },
  { id: 20, name: "Purva Ashadha", name_tamil: "பூராடம்", ruling_planet: "Venus", ruling_deity: "Apas (Water God)", functional_nature: "Fierce / Cruel", functional_nature_tamil: "உக்கிர / தீவிர", span_zodiac: "13°20' - 26°40' Sagittarius", gender: "Feminine", result_grade: "HARM", symbol_shape: "Winnowing basket / Fan", gaze_direction: "Downward", gaze_direction_tamil: "கீழ் பார்வை" },
  { id: 21, name: "Uttara Ashadha", name_tamil: "உத்திராடம்", ruling_planet: "Sun", ruling_deity: "Vishwadevas", functional_nature: "Fixed / Steady", functional_nature_tamil: "ஸ்திர / நிலையான", span_zodiac: "26°40' Sagittarius - 10°00' Capricorn", gender: "Feminine", result_grade: "GOOD", symbol_shape: "Elephant tusk / Small cot", gaze_direction: "Upward", gaze_direction_tamil: "மேல் பார்வை" },
  { id: 22, name: "Abhijit", name_tamil: "அபிஜித்", ruling_planet: "Sun / Brahma", ruling_deity: "Brahma", functional_nature: "Fixed / Auspicious", functional_nature_tamil: "சுப / மங்கள நட்சத்திரம்", span_zodiac: "06°40' - 10°53' Capricorn (Intercalary)", gender: "Masculine", result_grade: "GOOD", symbol_shape: "Eagle / Crown", gaze_direction: "Upward", gaze_direction_tamil: "மேல் பார்வை" },
  { id: 23, name: "Shravana", name_tamil: "திருவோணம்", ruling_planet: "Moon", ruling_deity: "Vishnu", functional_nature: "Movable / Ephemeral", functional_nature_tamil: "சர / மாற்றக்கூடிய", span_zodiac: "10°00' - 23°20' Capricorn", gender: "Masculine", result_grade: "GOOD", symbol_shape: "Three footprints / Ear", gaze_direction: "Upward", gaze_direction_tamil: "மேல் பார்வை" },
  { id: 24, name: "Dhanishta", name_tamil: "அவிட்டம்", ruling_planet: "Mars", ruling_deity: "Ashta Vasus", functional_nature: "Movable / Ephemeral", functional_nature_tamil: "சர / மாற்றக்கூடிய", span_zodiac: "23°20' Capricorn - 06°40' Aquarius", gender: "Feminine", result_grade: "GOOD", symbol_shape: "Mridangam / Flute", gaze_direction: "Upward", gaze_direction_tamil: "மேல் பார்வை" },
  { id: 25, name: "Shatabhisha", name_tamil: "சதயம்", ruling_planet: "Rahu", ruling_deity: "Varuna", functional_nature: "Movable / Ephemeral", functional_nature_tamil: "சர / மாற்றக்கூடிய", span_zodiac: "06°40' - 20°00' Aquarius", gender: "Hermaphrodite", result_grade: "GOOD", symbol_shape: "Empty circle / 100 physicians", gaze_direction: "Upward", gaze_direction_tamil: "மேல் பார்வை" },
  { id: 26, name: "Purva Bhadrapada", name_tamil: "பூரட்டாதி", ruling_planet: "Jupiter", ruling_deity: "Aja Ekapada", functional_nature: "Fierce / Cruel", functional_nature_tamil: "உக்கிர / தீவிர", span_zodiac: "20°00' Aquarius - 03°20' Pisces", gender: "Masculine", result_grade: "HARM", symbol_shape: "Front of funeral cot / Swords", gaze_direction: "Downward", gaze_direction_tamil: "கீழ் பார்வை" },
  { id: 27, name: "Uttara Bhadrapada", name_tamil: "உத்திரட்டாதி", ruling_planet: "Saturn", ruling_deity: "Ahirbudhnya", functional_nature: "Fixed / Steady", functional_nature_tamil: "ஸ்திர / நிலையான", span_zodiac: "03°20' - 16°40' Pisces", gender: "Masculine", result_grade: "GOOD", symbol_shape: "Back of funeral cot / Twin serpents", gaze_direction: "Upward", gaze_direction_tamil: "மேல் பார்வை" },
  { id: 28, name: "Revati", name_tamil: "ரேவதி", ruling_planet: "Mercury", ruling_deity: "Pushan", functional_nature: "Soft / Gentle", functional_nature_tamil: "மிருதுவான / சாந்த", span_zodiac: "16°40' - 30°00' Pisces", gender: "Feminine", result_grade: "GOOD", symbol_shape: "Pair of fish / Drum", gaze_direction: "Forward", gaze_direction_tamil: "நேர் பார்வை" },
];

const PREDEFINED_ACTIVITIES = [
  { id: "marriage", labelEn: "Marriage & Wedding (விவாக சுபகாரியம்)", labelTa: "திருமணம் & மாங்கல்ய தாரணம்", defaultKey: "marriage" },
  { id: "house_construction", labelEn: "House Foundation & Building (கட்டடம் & வாஸ்து)", labelTa: "அடிக்கல் நாட்டுதல் & புதுமனை புகுவிழா", defaultKey: "laying foundations" },
  { id: "business", labelEn: "New Business & Commerce (தொழில் துவக்கம்)", labelTa: "புதிய தொழில் & வியாபார தொடக்கம்", defaultKey: "starting business" },
  { id: "travel", labelEn: "Travel & Long Journeys (பிரயாணம் & வெளிநாடு)", labelTa: "நீண்ட தூர பிரயாணம்", defaultKey: "travel" },
  { id: "medical", labelEn: "Surgery & Medical Treatment (மருத்துவ சிகிச்சை)", labelTa: "மருத்துவ சிகிச்சை & அறுவை சிகிச்சை", defaultKey: "medical treatments" },
  { id: "learning", labelEn: "Education & Vidyarambham (கல்வி & வித்யாரம்பம்)", labelTa: "கல்வி துவக்கம் & உபதேசம் பெறுதல்", defaultKey: "commencing education" },
  { id: "property", labelEn: "Buying Land & Property (நிலம்/வீடு வாங்குதல்)", labelTa: "நிலம் & மனை வாங்குதல்", defaultKey: "buying land" },
  { id: "jewelry", labelEn: "Wearing New Ornaments & Apparel (ஆடை/ஆபரணம்)", labelTa: "புதிய ஆடை & தங்க ஆபரணம் அணிதல்", defaultKey: "wearing new apparel" },
];

function NakshatrasContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { language } = useLanguage();
  const isTa = language === "ta";
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();

  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !user)) {
      router.replace("/login");
    }
  }, [isAuthenticated, user, authLoading, router]);

  const [activeTab, setActiveTab] = useState<"catalog" | "activity" | "pada" | "natures">("catalog");
  const [nakshatrasList, setNakshatrasList] = useState<NakshatraItem[]>(CANONICAL_28_NAKSHATRAS as NakshatraItem[]);
  const [loadingList, setLoadingList] = useState(false);
  const [selectedNakshatra, setSelectedNakshatra] = useState<NakshatraItem | null>(null);

  // Search & Filter state
  const [searchTerm, setSearchTerm] = useState("");
  const [natureFilter, setNatureFilter] = useState("all");
  const [directionFilter, setDirectionFilter] = useState("all");

  // Activity Checker State
  const [checkActivity, setCheckActivity] = useState("marriage");
  const [checkNakshatra, setCheckNakshatra] = useState("Rohini");
  const [activityChecking, setActivityChecking] = useState(false);
  const [activityResult, setActivityResult] = useState<ActivityCheckResult | null>(null);

  // Pada Dosha Checker State
  const [padaNakshatra, setPadaNakshatra] = useState("Mula");
  const [padaNumber, setPadaNumber] = useState<number>(1);
  const [padaChecking, setPadaChecking] = useState(false);
  const [padaResult, setPadaResult] = useState<PadaDoshaResult | null>(null);

  // Load full catalog from backend on mount
  useEffect(() => {
    let mounted = true;
    async function loadCatalog() {
      setLoadingList(true);
      try {
        const data = await fetchNakshatras();
        if (mounted && Array.isArray(data) && data.length > 0) {
          setNakshatrasList(data);
        }
      } catch (err) {
        console.warn("Using canonical client fallback for 28 Nakshatras:", err);
      } finally {
        if (mounted) setLoadingList(false);
      }
    }
    loadCatalog();
    return () => {
      mounted = false;
    };
  }, []);

  // Pre-select Nakshatra from query params if passed (?star=Rohini or ?star=அஸ்வினி)
  useEffect(() => {
    const starParam = searchParams.get("star");
    if (starParam) {
      const found = nakshatrasList.find(
        (n) =>
          n.name.toLowerCase() === starParam.toLowerCase() ||
          n.name_tamil === starParam ||
          String(n.id) === starParam
      );
      if (found) {
        setSelectedNakshatra(found);
        setCheckNakshatra(found.name);
        setPadaNakshatra(found.name);
      }
    }
    const tabParam = searchParams.get("tab");
    if (tabParam && ["catalog", "activity", "pada", "natures"].includes(tabParam)) {
      setActiveTab(tabParam as any);
    }
  }, [searchParams, nakshatrasList]);

  // Filtered catalog
  const filteredNakshatras = useMemo(() => {
    return nakshatrasList.filter((item) => {
      const q = searchTerm.toLowerCase().trim();
      const matchSearch =
        !q ||
        item.name.toLowerCase().includes(q) ||
        (item.name_tamil && item.name_tamil.includes(q)) ||
        (item.ruling_deity && item.ruling_deity.toLowerCase().includes(q)) ||
        (item.ruling_planet && item.ruling_planet.toLowerCase().includes(q)) ||
        (item.symbol_shape && item.symbol_shape.toLowerCase().includes(q));

      const matchNature =
        natureFilter === "all" ||
        item.functional_nature.toLowerCase().includes(natureFilter.toLowerCase());

      const matchDirection =
        directionFilter === "all" ||
        item.gaze_direction?.toLowerCase() === directionFilter.toLowerCase();

      return matchSearch && matchNature && matchDirection;
    });
  }, [nakshatrasList, searchTerm, natureFilter, directionFilter]);

  // Handle Activity Check submit
  const handleCheckActivity = async (e: React.FormEvent) => {
    e.preventDefault();
    setActivityChecking(true);
    try {
      const selected = PREDEFINED_ACTIVITIES.find((a) => a.id === checkActivity);
      const activityQuery = selected ? selected.defaultKey : checkActivity;
      const res = await fetchActivityCheck(activityQuery, checkNakshatra);
      setActivityResult(res);
    } catch (err) {
      // Deterministic client fallback calculation
      const targetStar = nakshatrasList.find(
        (n) => n.name.toLowerCase() === checkNakshatra.toLowerCase()
      );
      const isGood = targetStar?.result_grade === "GOOD";
      setActivityResult({
        suitable: isGood,
        verdict: isGood ? "AUSPICIOUS" : "DISCOURAGED",
        reason: `${checkNakshatra} possesses ${targetStar?.functional_nature || "unique"} nature. ${
          isGood
            ? "Favorable for constructive undertakings."
            : "Requires careful Muhurta mitigation or alternative lunar star."
        }`,
        nakshatra_nature: targetStar?.functional_nature || "Standard",
        nakshatra_nature_tamil: targetStar?.functional_nature_tamil || "சாதாரண",
        direction: targetStar?.gaze_direction || "Forward",
      });
    } finally {
      setActivityChecking(false);
    }
  };

  // Handle Pada Dosha Check submit
  const handleCheckPada = async (e: React.FormEvent) => {
    e.preventDefault();
    setPadaChecking(true);
    try {
      const res = await fetchPadaDosha(padaNakshatra, padaNumber);
      setPadaResult(res);
    } catch (err) {
      // Fallback response
      const isGandanta =
        (padaNakshatra === "Mula" && padaNumber === 1) ||
        (padaNakshatra === "Ashlesha" && padaNumber === 4) ||
        (padaNakshatra === "Jyeshtha" && padaNumber === 4);

      setPadaResult({
        has_dosha: isGandanta,
        dosha_status: isGandanta ? "Nakshatra Gandanta Dosha" : "Neutral / Shanti",
        dosha_affects: isGandanta ? "Early developmental stress / Family harmony" : "None noted",
        remedy: isGandanta
          ? "Shanti Homa on 27th day, Gau Daanam, Rudrabhishekam."
          : "General Kuladeivam prayer and ghee lamp worship.",
        traits: `Traits for ${padaNakshatra} Pada ${padaNumber}`,
      });
    } finally {
      setPadaChecking(false);
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-[#153F6B] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="w-full px-4 sm:px-6 lg:px-8 py-6 space-y-6 max-w-7xl mx-auto">
      {/* Breadcrumbs */}
      <Breadcrumbs
        items={[
          { label: isTa ? "முகப்பு" : "Home", href: "/home" },
          { label: isTa ? "ஜோதிடக் கருவிகள்" : "Astrology Tools", href: "/tools" },
          { label: isTa ? "28 நட்சத்திர சாஸ்திர அரங்கம்" : "28 Nakshatras Portal" },
        ]}
      />

      {/* Hero Banner */}
      <div className="bg-gradient-to-r from-[#102A4C] via-[#153F6B] to-[#1C538C] rounded-2xl p-6 sm:p-8 text-white shadow-md relative overflow-hidden">
        <div className="relative z-10 max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-white/10 text-[#F3E5AB] backdrop-blur-xs border border-white/15">
            <Star className="w-3.5 h-3.5 fill-[#F3E5AB]" />
            <span>{isTa ? "28 நட்சத்திர சாஸ்திர ரகசியங்கள்" : "Classical 28 Nakshatras Shastra"}</span>
          </div>
          <h1 className="font-serif text-2xl sm:text-4xl font-bold tracking-tight text-white">
            {isTa
              ? "28 நட்சத்திர சாஸ்திர அரங்கம் & சுபகாரிய வழிகாட்டி"
              : "28 Nakshatras - Secrets & Shastra Portal"}
          </h1>
          <p className="text-xs sm:text-sm text-blue-100/90 leading-relaxed">
            {isTa
              ? "27 நட்சத்திரங்கள் மற்றும் மங்கள அபிஜித் உள்ளிட்ட 28 விண்மீன்களின் முழுமையான தத்துவங்கள், 4 பாத குணங்கள், தோஷ பரிகாரங்கள் மற்றும் தேர்தல் சுப முகூர்த்த வழிகாட்டி."
              : "Comprehensive classical treatises covering all 28 stellar constellations (27 Nakshatras + Abhijit), 4-pada nuances, Gandanta doshas, and electional transit suitability."}
          </p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white rounded-xl shadow-xs border border-[#E2E8F0] p-1.5 flex flex-wrap gap-1.5">
        {[
          { id: "catalog", labelTa: "🌟 28 நட்சத்திரங்கள் (Catalog)", labelEn: "🌟 28 Nakshatras Catalog" },
          { id: "activity", labelTa: "🎯 சுபகாரிய தேர்தல் தேர்வு", labelEn: "🎯 Activity Election Checker" },
          { id: "pada", labelTa: "⚖️ பாத தோஷ ஆய்வு", labelEn: "⚖️ Pada Dosha Diagnostic" },
          { id: "natures", labelTa: "📜 7 குண நயங்கள் (Functional Natures)", labelEn: "📜 7 Functional Natures" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-4 py-2.5 rounded-lg text-xs sm:text-sm font-semibold transition-all flex items-center gap-2 ${
              activeTab === tab.id
                ? "bg-[#153F6B] text-white shadow-xs"
                : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
            }`}
          >
            {isTa ? tab.labelTa : tab.labelEn}
          </button>
        ))}
      </div>

      {/* TAB 1: 28 NAKSHATRAS CATALOG */}
      {activeTab === "catalog" && (
        <div className="space-y-4">
          {/* Filter Bar */}
          <div className="bg-white p-4 rounded-xl border border-[#E2E8F0] shadow-xs flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder={isTa ? "நட்சத்திரப் பெயர், அதிபதி, தெய்வம் மூலம் தேடுக..." : "Search by Nakshatra, deity, ruler, symbol..."}
                className="w-full pl-9 pr-4 py-2 text-xs sm:text-sm border border-[#CBD5E1] rounded-lg focus:outline-hidden focus:ring-2 focus:ring-[#153F6B] bg-slate-50/50"
              />
            </div>
            <div className="flex flex-wrap gap-2">
              <select
                value={natureFilter}
                onChange={(e) => setNatureFilter(e.target.value)}
                className="text-xs border border-[#CBD5E1] rounded-lg px-3 py-2 bg-white text-slate-700"
              >
                <option value="all">{isTa ? "அனைத்து குணங்கள் (All Natures)" : "All Functional Natures"}</option>
                <option value="fixed">{isTa ? "ஸ்திர / நிலையான (Fixed)" : "Fixed / Steady"}</option>
                <option value="soft">{isTa ? "மிருதுவான / சாந்த (Soft)" : "Soft / Gentle"}</option>
                <option value="swift">{isTa ? "லகு / சுறுசுறுப்பு (Swift)" : "Light / Swift"}</option>
                <option value="sharp">{isTa ? "தீட்சண / கொடிய (Sharp)" : "Sharp / Dreadful"}</option>
                <option value="movable">{isTa ? "சர / மாற்றக்கூடிய (Movable)" : "Movable / Ephemeral"}</option>
                <option value="cruel">{isTa ? "உக்கிர / தீவிர (Cruel)" : "Fierce / Cruel"}</option>
                <option value="mixed">{isTa ? "மிஸ்ர / கலப்பு (Mixed)" : "Mixed / Ordinary"}</option>
              </select>

              <select
                value={directionFilter}
                onChange={(e) => setDirectionFilter(e.target.value)}
                className="text-xs border border-[#CBD5E1] rounded-lg px-3 py-2 bg-white text-slate-700"
              >
                <option value="all">{isTa ? "அனைத்துப் பார்வைகள் (All Gaze)" : "All Gaze Directions"}</option>
                <option value="upward">{isTa ? "மேல் பார்வை (Upward)" : "Upward"}</option>
                <option value="downward">{isTa ? "கீழ் பார்வை (Downward)" : "Downward"}</option>
                <option value="forward">{isTa ? "நேர் பார்வை (Forward)" : "Forward"}</option>
              </select>
            </div>
          </div>

          {/* Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredNakshatras.map((n) => {
              const isAbhijit = n.id === 22;
              return (
                <div
                  key={n.id}
                  onClick={() => setSelectedNakshatra(n)}
                  className={`bg-white rounded-xl p-4 border transition-all cursor-pointer hover:shadow-md hover:border-[#153F6B] flex flex-col justify-between space-y-3 relative group ${
                    isAbhijit ? "border-amber-300 bg-amber-50/20" : "border-[#E2E8F0]"
                  }`}
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-[#153F6B] text-[#F3E5AB] font-bold text-xs">
                        {n.id}
                      </span>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          n.result_grade === "GOOD"
                            ? "bg-emerald-100 text-emerald-800"
                            : n.result_grade === "HARM"
                            ? "bg-rose-100 text-rose-800"
                            : "bg-slate-100 text-slate-800"
                        }`}
                      >
                        {n.result_grade || "SHASTRA"}
                      </span>
                    </div>

                    <div>
                      <h3 className="font-bold text-base text-[#0F2942] group-hover:text-[#153F6B] transition-colors">
                        {isTa ? n.name_tamil : n.name}
                      </h3>
                      <p className="text-xs text-slate-500 font-medium">
                        {isTa ? n.name : n.name_tamil}
                      </p>
                    </div>

                    <div className="space-y-1 text-xs text-slate-600 border-t border-slate-100 pt-2">
                      <div className="flex justify-between">
                        <span className="text-slate-400">{isTa ? "அதிபதி:" : "Ruler:"}</span>
                        <span className="font-semibold text-slate-800">{n.ruling_planet}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">{isTa ? "தெய்வம்:" : "Deity:"}</span>
                        <span className="font-semibold text-slate-800 truncate max-w-[130px]">{n.ruling_deity}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">{isTa ? "குணம்:" : "Nature:"}</span>
                        <span className="font-semibold text-[#153F6B] truncate max-w-[130px]">
                          {isTa ? n.functional_nature_tamil : n.functional_nature}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">{isTa ? "பார்வை:" : "Gaze:"}</span>
                        <span className="text-slate-700">{isTa ? n.gaze_direction_tamil : n.gaze_direction}</span>
                      </div>
                    </div>
                  </div>

                  <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-[#153F6B] font-semibold">
                    <span>{isTa ? "முழு பலன் பார்க்க" : "View Shastra Details"}</span>
                    <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              );
            })}
          </div>

          {filteredNakshatras.length === 0 && (
            <div className="text-center py-12 bg-white rounded-xl border border-slate-200">
              <Info className="w-8 h-8 text-slate-400 mx-auto mb-2" />
              <p className="text-sm font-semibold text-slate-700">
                {isTa ? "நட்சத்திரங்கள் எதுவும் பொருந்தவில்லை." : "No Nakshatras match your search query."}
              </p>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: ACTIVITY ELECTION CHECKER */}
      {activeTab === "activity" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-xl border border-[#E2E8F0] shadow-xs space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
              <Compass className="w-5 h-5 text-[#153F6B]" />
              <h2 className="font-bold text-base text-[#0F2942]">
                {isTa ? "சுபகாரிய தேர்தல் சோதனை" : "Electional Suitability Check"}
              </h2>
            </div>

            <form onSubmit={handleCheckActivity} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  {isTa ? "செயல்பாடு / சுபகாரியம்:" : "Select Activity / Enterprise:"}
                </label>
                <select
                  value={checkActivity}
                  onChange={(e) => setCheckActivity(e.target.value)}
                  className="w-full text-xs sm:text-sm border border-[#CBD5E1] rounded-lg p-2.5 bg-white text-slate-800"
                >
                  {PREDEFINED_ACTIVITIES.map((act) => (
                    <option key={act.id} value={act.id}>
                      {isTa ? act.labelTa : act.labelEn}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  {isTa ? "நட்சத்திரம் (Nakshatra):" : "Select Nakshatra:"}
                </label>
                <select
                  value={checkNakshatra}
                  onChange={(e) => setCheckNakshatra(e.target.value)}
                  className="w-full text-xs sm:text-sm border border-[#CBD5E1] rounded-lg p-2.5 bg-white text-slate-800"
                >
                  {nakshatrasList.map((n) => (
                    <option key={n.id} value={n.name}>
                      {n.id}. {isTa ? n.name_tamil : n.name} ({n.name})
                    </option>
                  ))}
                </select>
              </div>

              <button
                type="submit"
                disabled={activityChecking}
                className="w-full py-2.5 px-4 bg-[#153F6B] text-white rounded-lg font-bold text-xs sm:text-sm hover:bg-[#102A4C] transition-colors shadow-xs flex items-center justify-center gap-2"
              >
                {activityChecking ? (
                  <span>{isTa ? "சாஸ்திர விதிகள் சோதிக்கப்படுகின்றன..." : "Evaluating Shastra Rules..."}</span>
                ) : (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-[#F3E5AB]" />
                    <span>{isTa ? "சுப முகூர்த்த தகுதியை சரிபார்" : "Evaluate Auspiciousness"}</span>
                  </>
                )}
              </button>
            </form>
          </div>

          <div className="lg:col-span-2">
            {activityResult ? (
              <div className="bg-white p-6 rounded-xl border border-[#E2E8F0] shadow-xs space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <div>
                    <h3 className="text-base font-bold text-[#0F2942]">
                      {isTa ? "சாஸ்திர தேர்தல் தீர்ப்பு" : "Canonical Shastra Verdict"}
                    </h3>
                    <p className="text-xs text-slate-500">
                      {checkNakshatra} • {checkActivity}
                    </p>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-bold ${
                      activityResult.suitable
                        ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                        : "bg-rose-100 text-rose-800 border border-rose-300"
                    }`}
                  >
                    {activityResult.suitable ? (isTa ? "சுபமானது (Auspicious)" : "Auspicious") : (isTa ? "தவிர்க்கவும் (Inauspicious)" : "Avoid / Discouraged")}
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                  <div className="text-xs font-bold text-slate-700">
                    {isTa ? "விளக்கம் & காரணக் குறிப்பு:" : "Classical Rationale:"}
                  </div>
                  <p className="text-xs sm:text-sm text-slate-700 leading-relaxed">
                    {activityResult.reason}
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div className="p-3 bg-blue-50/50 rounded-lg border border-blue-100">
                    <span className="text-slate-500 block">{isTa ? "நட்சத்திர குணம்:" : "Functional Nature:"}</span>
                    <span className="font-bold text-[#153F6B] text-sm">
                      {isTa ? activityResult.nakshatra_nature_tamil || activityResult.nakshatra_nature : activityResult.nakshatra_nature}
                    </span>
                  </div>
                  <div className="p-3 bg-blue-50/50 rounded-lg border border-blue-100">
                    <span className="text-slate-500 block">{isTa ? "பார்வை திசை:" : "Gaze Direction:"}</span>
                    <span className="font-bold text-[#153F6B] text-sm">{activityResult.direction}</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-full min-h-[220px] bg-slate-50/50 rounded-xl border border-dashed border-slate-300 flex flex-col items-center justify-center p-6 text-center text-slate-500">
                <Compass className="w-8 h-8 text-slate-400 mb-2" />
                <p className="text-xs sm:text-sm font-semibold text-slate-700">
                  {isTa ? "செயல்பாடு மற்றும் நட்சத்திரத்தை தேர்வு செய்து சரிபார்க்கவும்." : "Select an enterprise activity and Nakshatra to evaluate Muhurta suitability."}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 3: PADA DOSHA DIAGNOSTIC */}
      {activeTab === "pada" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-xl border border-[#E2E8F0] shadow-xs space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
              <Shield className="w-5 h-5 text-[#153F6B]" />
              <h2 className="font-bold text-base text-[#0F2942]">
                {isTa ? "பாத தோஷ ஆய்வு & பரிகாரம்" : "Pada Dosha Diagnostic"}
              </h2>
            </div>

            <form onSubmit={handleCheckPada} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  {isTa ? "நட்சத்திரம் (Nakshatra):" : "Select Nakshatra:"}
                </label>
                <select
                  value={padaNakshatra}
                  onChange={(e) => setPadaNakshatra(e.target.value)}
                  className="w-full text-xs sm:text-sm border border-[#CBD5E1] rounded-lg p-2.5 bg-white text-slate-800"
                >
                  {nakshatrasList.map((n) => (
                    <option key={n.id} value={n.name}>
                      {n.id}. {isTa ? n.name_tamil : n.name} ({n.name})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  {isTa ? "பாத எண் (Pada Quarter 1-4):" : "Select Pada Quarter (1-4):"}
                </label>
                <div className="grid grid-cols-4 gap-2">
                  {[1, 2, 3, 4].map((p) => (
                    <button
                      key={p}
                      type="button"
                      onClick={() => setPadaNumber(p)}
                      className={`py-2 rounded-lg text-xs font-bold transition-all ${
                        padaNumber === p
                          ? "bg-[#153F6B] text-white shadow-xs"
                          : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                      }`}
                    >
                      {isTa ? `${p}-ம் பாதம்` : `Pada ${p}`}
                    </button>
                  ))}
                </div>
              </div>

              <button
                type="submit"
                disabled={padaChecking}
                className="w-full py-2.5 px-4 bg-[#153F6B] text-white rounded-lg font-bold text-xs sm:text-sm hover:bg-[#102A4C] transition-colors shadow-xs flex items-center justify-center gap-2"
              >
                {padaChecking ? (
                  <span>{isTa ? "ஆய்வு செய்யப்படுகிறது..." : "Diagnosing..."}</span>
                ) : (
                  <>
                    <Shield className="w-4 h-4 text-[#F3E5AB]" />
                    <span>{isTa ? "பாத தோஷங்களை கண்டறி" : "Diagnose Pada Dosha"}</span>
                  </>
                )}
              </button>
            </form>
          </div>

          <div className="lg:col-span-2">
            {padaResult ? (
              <div className="bg-white p-6 rounded-xl border border-[#E2E8F0] shadow-xs space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <div>
                    <h3 className="text-base font-bold text-[#0F2942]">
                      {isTa ? "பாத தோஷ ஆய்வு முடிவு" : "Pada Diagnostic Result"}
                    </h3>
                    <p className="text-xs text-slate-500">
                      {padaNakshatra} • {isTa ? `${padaNumber}-ம் பாதம்` : `Pada ${padaNumber}`}
                    </p>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-bold ${
                      padaResult.has_dosha
                        ? "bg-amber-100 text-amber-900 border border-amber-300"
                        : "bg-emerald-100 text-emerald-800 border border-emerald-300"
                    }`}
                  >
                    {padaResult.has_dosha ? (isTa ? "தோஷம் உண்டு (Dosha Present)" : "Dosha Present") : (isTa ? "தோஷம் இல்லை (Clean / Auspicious)" : "Clean")}
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="p-3.5 bg-slate-50 rounded-lg border border-slate-200">
                    <span className="text-xs font-bold text-slate-500 block mb-1">
                      {isTa ? "தோஷ வகை / நிலை:" : "Dosha Status:"}
                    </span>
                    <span className="text-sm font-semibold text-slate-800">
                      {padaResult.dosha_status || "None"}
                    </span>
                  </div>
                  <div className="p-3.5 bg-slate-50 rounded-lg border border-slate-200">
                    <span className="text-xs font-bold text-slate-500 block mb-1">
                      {isTa ? "பாதிப்புக்குரிய அமைப்பு:" : "Affected Sphere:"}
                    </span>
                    <span className="text-sm font-semibold text-slate-800">
                      {padaResult.dosha_affects || "None"}
                    </span>
                  </div>
                </div>

                {padaResult.remedy && (
                  <div className="p-4 rounded-xl bg-amber-50/60 border border-amber-200 space-y-1">
                    <div className="text-xs font-bold text-amber-900 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-amber-700" />
                      <span>{isTa ? "சாஸ்திர பரிகாரம் & சாந்தி முறை:" : "Prescribed Classical Remedy:"}</span>
                    </div>
                    <p className="text-xs sm:text-sm text-amber-950 leading-relaxed">
                      {padaResult.remedy}
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="h-full min-h-[220px] bg-slate-50/50 rounded-xl border border-dashed border-slate-300 flex flex-col items-center justify-center p-6 text-center text-slate-500">
                <Shield className="w-8 h-8 text-slate-400 mb-2" />
                <p className="text-xs sm:text-sm font-semibold text-slate-700">
                  {isTa ? "நட்சத்திரம் மற்றும் பாதத்தை தேர்வு செய்து தோஷ நிலையை அறியவும்." : "Select a Nakshatra and Pada quarter to diagnose doshas and remedies."}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 4: 7 FUNCTIONAL NATURES GUIDE */}
      {activeTab === "natures" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            {
              id: "fixed",
              nameEn: "Fixed / Steady (Sthira / Dhruva)",
              nameTa: "ஸ்திர / நிலையான நட்சத்திரங்கள்",
              stars: "Rohini (4), Uttara Phalguni (12), Uttara Ashadha (21), Uttara Bhadrapada (27)",
              actionsEn: "Laying foundations, building homes, planting trees, deity installation, entering permanent relationships.",
              actionsTa: "அடிக்கல் நாட்டுதல், புதுமனை புகுவிழா, மரம் நடுதல், கோவில் அமைத்தல், நிலையான ஒப்பந்தங்கள்.",
              badgeColor: "bg-emerald-100 text-emerald-800 border-emerald-300",
            },
            {
              id: "soft",
              nameEn: "Soft / Gentle (Mridu)",
              nameTa: "மிருதுவான / சாந்த நட்சத்திரங்கள்",
              stars: "Mrigashira (5), Chitra (14), Anuradha (17), Revati (28)",
              actionsEn: "Fine arts, learning, romance, wearing new clothes/ornaments, marriage celebrations, peaceful travels.",
              actionsTa: "நுண்கலைகள், நட்பு, ஆடை ஆபரணம் அணிதல், திருமணம், மங்கள சடங்குகள், சுப பிரயாணங்கள்.",
              badgeColor: "bg-indigo-100 text-indigo-800 border-indigo-300",
            },
            {
              id: "swift",
              nameEn: "Light / Swift (Kshipra / Laghu)",
              nameTa: "லகு / சுறுசுறுப்பு நட்சத்திரங்கள்",
              stars: "Ashwini (1), Pushya (8), Hasta (13)",
              actionsEn: "Medical treatments, sports, short journeys, starting industries, trade, giving or taking loans.",
              actionsTa: "மருத்துவ சிகிச்சை, விளையாட்டு, குறுகிய பயணம், தொழிற்சாலை தொடக்கம், வர்த்தக விற்பனை, கடன் விவகாரங்கள்.",
              badgeColor: "bg-amber-100 text-amber-800 border-amber-300",
            },
            {
              id: "sharp",
              nameEn: "Sharp / Dreadful (Tikshna / Daruna)",
              nameTa: "தீட்சண / கொடிய நட்சத்திரங்கள்",
              stars: "Ardra (6), Ashlesha (9), Jyeshtha (18), Mula (19)",
              actionsEn: "Warfare, crisis management, demolition, exorcism, breaking harmful alliances, court litigation.",
              actionsTa: "போர் வெற்றி, ஆபத்துகளை சமாளித்தல், பழையவற்றை தகர்த்தல், தீய சக்திகளை முறியடித்தல், வழக்கு விவகாரங்கள்.",
              badgeColor: "bg-rose-100 text-rose-800 border-rose-300",
            },
            {
              id: "movable",
              nameEn: "Movable / Ephemeral (Chara)",
              nameTa: "சர / மாற்றக்கூடிய நட்சத்திரங்கள்",
              stars: "Punarvasu (7), Swati (15), Shravana (23), Dhanishta (24), Shatabhisha (25)",
              actionsEn: "Travel, buying vehicles, changing residence, machinery repairs, dynamic commercial activities.",
              actionsTa: "வாகனம் வாங்குதல், வீடு மாறுதல், இயந்திர பழுது நீக்குதல், சுப பிரயாணங்கள்.",
              badgeColor: "bg-cyan-100 text-cyan-800 border-cyan-300",
            },
            {
              id: "cruel",
              nameEn: "Fierce / Cruel (Ugra)",
              nameTa: "உக்கிர / தீவிர நட்சத்திரங்கள்",
              stars: "Bharani (2), Magha (10), Purva Phalguni (11), Purva Ashadha (20), Purva Bhadrapada (26)",
              actionsEn: "Demolition, handling weapons, surgery, research into poisonous substances, boundary disputes.",
              actionsTa: "எதிரிகளை முறியடித்தல், அறுவை சிகிச்சை, எல்லை தகராறு தீர்வு, கடுமையான ஆயுத பிரயோகம்.",
              badgeColor: "bg-red-100 text-red-800 border-red-300",
            },
            {
              id: "mixed",
              nameEn: "Mixed / Ordinary (Misra)",
              nameTa: "மிஸ்ர / கலப்பு நட்சத்திரங்கள்",
              stars: "Krittika (3), Vishakha (16)",
              actionsEn: "Furnaces, welding, fire rituals, starting routine daily tasks, short-lived works.",
              actionsTa: "அக்னி காரியங்கள், ஹோமம், பட்டறை வேலைகள், குறுகிய கால நுகர்வு வேலைகள்.",
              badgeColor: "bg-purple-100 text-purple-800 border-purple-300",
            },
          ].map((item) => (
            <div key={item.id} className="bg-white p-5 rounded-xl border border-[#E2E8F0] shadow-xs space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-sm text-[#0F2942]">
                  {isTa ? item.nameTa : item.nameEn}
                </h3>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${item.badgeColor}`}>
                  {item.id.toUpperCase()}
                </span>
              </div>
              <p className="text-xs text-[#153F6B] font-semibold">{item.stars}</p>
              <div className="pt-2 border-t border-slate-100 text-xs text-slate-600 leading-relaxed">
                <strong>{isTa ? "சுபமான காரியங்கள்:" : "Suitable Actions:"} </strong>
                {isTa ? item.actionsTa : item.actionsEn}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* DETAIL MODAL FOR SELECTED NAKSHATRA */}
      {selectedNakshatra && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 shadow-xl space-y-4 relative">
            <button
              onClick={() => setSelectedNakshatra(null)}
              className="absolute top-4 right-4 p-1.5 rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-100"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="space-y-1">
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-[#153F6B] text-[#F3E5AB]">
                <span>{selectedNakshatra.id}. {selectedNakshatra.name}</span>
                <span>•</span>
                <span>{selectedNakshatra.name_tamil}</span>
              </div>
              <h2 className="font-bold text-xl text-[#0F2942]">
                {isTa ? `${selectedNakshatra.name_tamil} நட்சத்திர சாஸ்திர விபரங்கள்` : `${selectedNakshatra.name} Full Shastra Profile`}
              </h2>
              <p className="text-xs text-slate-500 font-medium">
                {selectedNakshatra.span_zodiac}
              </p>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-400 block">{isTa ? "அதிபதி கிரகம்" : "Ruler"}</span>
                <span className="font-bold text-slate-800">{selectedNakshatra.ruling_planet}</span>
              </div>
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-400 block">{isTa ? "அதிதேவதை" : "Deity"}</span>
                <span className="font-bold text-slate-800 truncate">{selectedNakshatra.ruling_deity}</span>
              </div>
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-400 block">{isTa ? "வடிவம் / சின்னம்" : "Symbol"}</span>
                <span className="font-bold text-slate-800 truncate">{selectedNakshatra.symbol_shape}</span>
              </div>
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-400 block">{isTa ? "குண நயம்" : "Nature"}</span>
                <span className="font-bold text-[#153F6B] truncate">
                  {isTa ? selectedNakshatra.functional_nature_tamil : selectedNakshatra.functional_nature}
                </span>
              </div>
            </div>

            {selectedNakshatra.padas && selectedNakshatra.padas.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-700">
                  {isTa ? "4 பாதங்களின் நுணுக்கங்கள் & தோஷங்கள்:" : "4 Padas Nuances & Diagnostics:"}
                </h4>
                <div className="space-y-2">
                  {selectedNakshatra.padas.map((p) => (
                    <div key={p.pada_number} className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-[#153F6B]">
                          {isTa ? `${p.pada_number}-ம் பாதம்` : `Pada ${p.pada_number}`} ({p.degree_range})
                        </span>
                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                            p.dosha_status === "CLEAN"
                              ? "bg-emerald-100 text-emerald-800"
                              : "bg-amber-100 text-amber-800"
                          }`}
                        >
                          {p.dosha_status}
                        </span>
                      </div>
                      <p className="text-slate-600">{p.traits}</p>
                      {p.remedy && (
                        <p className="text-amber-800 font-medium">
                          <strong>{isTa ? "பரிகாரம்:" : "Remedy:"} </strong>{p.remedy}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex justify-end pt-2 border-t border-slate-100">
              <button
                onClick={() => setSelectedNakshatra(null)}
                className="px-4 py-2 bg-[#153F6B] text-white text-xs font-bold rounded-lg hover:bg-[#102A4C]"
              >
                {isTa ? "மூடுக" : "Close"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function NakshatrasPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-[60vh] flex items-center justify-center">
          <div className="w-8 h-8 border-4 border-[#153F6B] border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <NakshatrasContent />
    </Suspense>
  );
}
