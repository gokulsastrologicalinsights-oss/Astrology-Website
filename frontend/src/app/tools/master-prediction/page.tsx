"use client";

import React, { useState, useEffect, useMemo, Suspense } from "react";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  HoroscopeRequest,
  HoroscopeResponse,
  KpMonthlyPredictionResponse,
  LifeRoadmapRequest,
  LifeRoadmapResponse,
  UnifiedMarriageRequest,
  UnifiedMarriageResponse,
  SpousePredictionRequest,
  SpousePredictionResponse,
  DoubleTransitRequest,
  DoubleTransitResponse,
  DoubleTransitWindow,
  AshtakavargaResponse,
  KakshaAlertRequest,
  KakshaAlertsResponse,
  InstantHoraryPredictionRequest,
  InstantHoraryPredictionResponse,
  NakshatraItem,
  SavedHoroscopeItem,
  DomainScorecard,
  RoadmapPeriodItem,
  ScoredMilestone,
} from "@/lib/types";
import {
  calculateHoroscope,
  getKpMonthlyPrediction,
  generateLifeRoadmap,
  predictMarriageEvent,
  predictSpouseEvent,
  calculateDoubleTransit,
  calculateAshtakavarga,
  calculateKakshaAlerts,
  predictInstantHorary,
  fetchNakshatras,
} from "@/lib/api";
import {
  Sparkles,
  Compass,
  Calendar,
  Clock,
  Heart,
  Briefcase,
  Coins,
  Grid,
  Star,
  RefreshCw,
  Plane,
  Baby,
  Activity,
  Home,
  Dice5,
  User,
  Eye,
  Printer,
  CheckCircle2,
  Crown,
  Zap,
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
  { id: 11, name: "Purva Phalguni", name_tamil: "பூரம்", ruling_planet: "Venus", ruling_deity: "Bhaga", functional_nature: "Fierce / Cruel", functional_nature_tamil: "உக்கிர / தீவிர", span_zodiac: "13°20' - 26°40' Leo", gender: "Feminine", result_grade: "HARM", symbol_shape: "Front legs of bed", gaze_direction: "Downward", gaze_direction_tamil: "கீழ் பார்வை" },
  { id: 12, name: "Uttara Phalguni", name_tamil: "உத்திரம்", ruling_planet: "Sun", ruling_deity: "Aryaman", functional_nature: "Fixed / Steady", functional_nature_tamil: "ஸ்திர / நிலையான", span_zodiac: "26°40' Leo - 10°00' Virgo", gender: "Feminine", result_grade: "GOOD", symbol_shape: "Back legs of bed", gaze_direction: "Upward", gaze_direction_tamil: "மேல் பார்வை" },
  { id: 13, name: "Hasta", name_tamil: "அஸ்தம்", ruling_planet: "Moon", ruling_deity: "Savitr", functional_nature: "Light / Swift", functional_nature_tamil: "லகு / சுறுசுறுப்பு", span_zodiac: "10°00' - 23°20' Virgo", gender: "Masculine", result_grade: "GOOD", symbol_shape: "Clenched fist", gaze_direction: "Forward", gaze_direction_tamil: "நேர் பார்வை" },
  { id: 14, name: "Chitra", name_tamil: "சித்திரை", ruling_planet: "Mars", ruling_deity: "Twashtar", functional_nature: "Soft / Gentle", functional_nature_tamil: "மிருதுவான / சாந்த", span_zodiac: "23°20' Virgo - 06°40' Libra", gender: "Feminine", result_grade: "GOOD", symbol_shape: "Pearl / Jewel", gaze_direction: "Forward", gaze_direction_tamil: "நேர் பார்வை" },
  { id: 15, name: "Swati", name_tamil: "சுவாதி", ruling_planet: "Rahu", ruling_deity: "Vayu", functional_nature: "Movable / Ephemeral", functional_nature_tamil: "சர / மாற்றக்கூடிய", span_zodiac: "06°40' - 20°00' Libra", gender: "Feminine", result_grade: "GOOD", symbol_shape: "Shoot of plant", gaze_direction: "Forward", gaze_direction_tamil: "நேர் பார்வை" },
  { id: 16, name: "Vishakha", name_tamil: "விசாகம்", ruling_planet: "Jupiter", ruling_deity: "Indragni", functional_nature: "Mixed / Ordinary", functional_nature_tamil: "மிஸ்ர / கலப்பு", span_zodiac: "20°00' Libra - 03°20' Scorpio", gender: "Feminine", result_grade: "HARM", symbol_shape: "Arch / Potter wheel", gaze_direction: "Downward", gaze_direction_tamil: "கீழ் பார்வை" },
  { id: 17, name: "Anuradha", name_tamil: "அனுஷம்", ruling_planet: "Saturn", ruling_deity: "Mitra", functional_nature: "Soft / Gentle", functional_nature_tamil: "மிருதுவான / சாந்த", span_zodiac: "03°20' - 16°40' Scorpio", gender: "Masculine", result_grade: "GOOD", symbol_shape: "Lotus flower", gaze_direction: "Forward", gaze_direction_tamil: "நேர் பார்வை" },
  { id: 18, name: "Jyeshtha", name_tamil: "கேட்டை", ruling_planet: "Mercury", ruling_deity: "Indra", functional_nature: "Sharp / Dreadful", functional_nature_tamil: "தீட்சண / கொடிய", span_zodiac: "16°40' - 30°00' Scorpio", gender: "Feminine", result_grade: "HARM", symbol_shape: "Umbrella", gaze_direction: "Downward", gaze_direction_tamil: "கீழ் பார்வை" },
  { id: 19, name: "Mula", name_tamil: "மூலம்", ruling_planet: "Ketu", ruling_deity: "Nirriti", functional_nature: "Sharp / Dreadful", functional_nature_tamil: "தீட்சண / கொடிய", span_zodiac: "00°00' - 13°20' Sagittarius", gender: "Hermaphrodite", result_grade: "HARM", symbol_shape: "Roots bundle", gaze_direction: "Downward", gaze_direction_tamil: "கீழ் பார்வை" },
  { id: 20, name: "Purva Ashadha", name_tamil: "பூராடம்", ruling_planet: "Venus", ruling_deity: "Apas", functional_nature: "Fierce / Cruel", functional_nature_tamil: "உக்கிர / தீவிர", span_zodiac: "13°20' - 26°40' Sagittarius", gender: "Feminine", result_grade: "HARM", symbol_shape: "Fan", gaze_direction: "Downward", gaze_direction_tamil: "கீழ் பார்வை" },
  { id: 21, name: "Uttara Ashadha", name_tamil: "உத்திராடம்", ruling_planet: "Sun", ruling_deity: "Vishwadevas", functional_nature: "Fixed / Steady", functional_nature_tamil: "ஸ்திர / நிலையான", span_zodiac: "26°40' Sagittarius - 10°00' Capricorn", gender: "Feminine", result_grade: "GOOD", symbol_shape: "Small cot", gaze_direction: "Upward", gaze_direction_tamil: "மேல் பார்வை" },
  { id: 22, name: "Abhijit", name_tamil: "அபிஜித்", ruling_planet: "Sun / Brahma", ruling_deity: "Brahma / Vishnu", functional_nature: "Fixed / Auspicious", functional_nature_tamil: "சுப / மங்கள நட்சத்திரம்", span_zodiac: "06°40' - 10°53' Capricorn (Intercalary)", gender: "Masculine", result_grade: "GOOD", symbol_shape: "Eagle / Crown", gaze_direction: "Upward", gaze_direction_tamil: "மேல் பார்வை" },
  { id: 23, name: "Shravana", name_tamil: "திருவோணம்", ruling_planet: "Moon", ruling_deity: "Vishnu", functional_nature: "Movable / Ephemeral", functional_nature_tamil: "சர / மாற்றக்கூடிய", span_zodiac: "10°00' - 23°20' Capricorn", gender: "Masculine", result_grade: "GOOD", symbol_shape: "Three footprints", gaze_direction: "Upward", gaze_direction_tamil: "மேல் பார்வை" },
  { id: 24, name: "Dhanishta", name_tamil: "அவிட்டம்", ruling_planet: "Mars", ruling_deity: "Ashta Vasus", functional_nature: "Movable / Ephemeral", functional_nature_tamil: "சர / மாற்றக்கூடிய", span_zodiac: "23°20' Capricorn - 06°40' Aquarius", gender: "Feminine", result_grade: "GOOD", symbol_shape: "Mridangam", gaze_direction: "Upward", gaze_direction_tamil: "மேல் பார்வை" },
  { id: 25, name: "Shatabhisha", name_tamil: "சதயம்", ruling_planet: "Rahu", ruling_deity: "Varuna", functional_nature: "Movable / Ephemeral", functional_nature_tamil: "சர / மாற்றக்கூடிய", span_zodiac: "06°40' - 20°00' Aquarius", gender: "Hermaphrodite", result_grade: "GOOD", symbol_shape: "Circle", gaze_direction: "Upward", gaze_direction_tamil: "மேல் பார்வை" },
  { id: 26, name: "Purva Bhadrapada", name_tamil: "பூரட்டாதி", ruling_planet: "Jupiter", ruling_deity: "Aja Ekapada", functional_nature: "Fierce / Cruel", functional_nature_tamil: "உக்கிர / தீவிர", span_zodiac: "20°00' Aquarius - 03°20' Pisces", gender: "Masculine", result_grade: "HARM", symbol_shape: "Swords", gaze_direction: "Downward", gaze_direction_tamil: "கீழ் பார்வை" },
  { id: 27, name: "Uttara Bhadrapada", name_tamil: "உத்திரட்டாதி", ruling_planet: "Saturn", ruling_deity: "Ahirbudhnya", functional_nature: "Fixed / Steady", functional_nature_tamil: "ஸ்திர / நிலையான", span_zodiac: "03°20' - 16°40' Pisces", gender: "Masculine", result_grade: "GOOD", symbol_shape: "Twin serpents", gaze_direction: "Upward", gaze_direction_tamil: "மேல் பார்வை" },
  { id: 28, name: "Revati", name_tamil: "ரேவதி", ruling_planet: "Mercury", ruling_deity: "Pushan", functional_nature: "Soft / Gentle", functional_nature_tamil: "மிருதுவான / சாந்த", span_zodiac: "16°40' - 30°00' Pisces", gender: "Feminine", result_grade: "GOOD", symbol_shape: "Pair of fish", gaze_direction: "Forward", gaze_direction_tamil: "நேர் பார்வை" },
];

const TARA_BALA_TYPES = [
  { id: 1, name: "Janma", name_ta: "ஜன்ம தாரை", grade: "HARM", desc_ta: "உடல் நலம், சஞ்சலம், கவனமாக இருக்க வேண்டும்" },
  { id: 2, name: "Sampat", name_ta: "சம்பத்து தாரை", grade: "GOOD", desc_ta: "தன லாபம், சுப காரிய சித்தி, செல்வம் சேரும்" },
  { id: 3, name: "Vipat", name_ta: "விபத்து தாரை", grade: "HARM", desc_ta: "தடைகள், விபத்து, சுப காரியங்களை தவிர்க்கவும்" },
  { id: 4, name: "Kshema", name_ta: "சேம தாரை", grade: "GOOD", desc_ta: "ஆரோக்கியம், குடும்ப நிம்மதி, வெற்றி தரும்" },
  { id: 5, name: "Pratyak", name_ta: "பிரத்யக்கு தாரை", grade: "HARM", desc_ta: "எதிர்ப்பு, மனக்கசப்பு, வழக்கு, காரிய தாமதம்" },
  { id: 6, name: "Sadhana", name_ta: "சாதனை தாரை", grade: "GOOD", desc_ta: "முயற்சி வெற்றி, பதவி உயர்வு, புதிய தொடக்கம்" },
  { id: 7, name: "Naidhana", name_ta: "நைதன தாரை", grade: "HARM", desc_ta: "மரண பயம், கடும் விரயம், முக்கிய முடிவுகள் வேண்டாம்" },
  { id: 8, name: "Mitra", name_ta: "மித்ர தாரை", grade: "GOOD", desc_ta: "நண்பர்கள் ஆதரவு, மகிழ்ச்சி, பொது காரிய சித்தி" },
  { id: 9, name: "Param Mitra", name_ta: "பரம மித்ர தாரை", grade: "GOOD", desc_ta: "பேரதிர்ஷ்டம், மிகச் சிறந்த சுப பலன், ஆன்மீக அருள்" },
];

const DOUBLE_TRANSIT_DOMAINS = [
  { id: "marriage", labelEn: "Marriage & Sacred Union", labelTa: "திருமணம்", house: 7, icon: Heart },
  { id: "career", labelEn: "Career Promotion & Elevation", labelTa: "தொழில் உயர்வு", house: 10, icon: Briefcase },
  { id: "childbirth", labelEn: "Progeny & Childbirth", labelTa: "புத்திர பாக்கியம்", house: 5, icon: Baby },
  { id: "wealth", labelEn: "Major Wealth & Liquid Gain", labelTa: "தன லாபம் & சொத்து", house: 11, icon: Coins },
  { id: "property", labelEn: "Property & Real Estate", labelTa: "பூமி & வீடு சேர்க்கை", house: 4, icon: Home },
  { id: "foreign", labelEn: "Foreign Travel & Relocation", labelTa: "வெளிநாட்டுப் பயணம்", house: 12, icon: Plane },
  { id: "health", labelEn: "Health Recovery & Vitality", labelTa: "ஆரோக்கிய மீட்சி", house: 1, icon: Activity },
];

function MasterPredictionContent() {
  const router = useRouter();
  const { language } = useLanguage();
  const isTa = language === "ta";
  const { session, isAuthenticated, isLoading: authLoading, user } = useAuth();

  // Authentication check
  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !user)) {
      router.replace("/login");
    }
  }, [isAuthenticated, user, authLoading, router]);

  // Mode: Saved chart vs manual entry
  const [chartMode, setChartMode] = useState<"saved" | "manual">("saved");
  const [savedHoroscopes, setSavedHoroscopes] = useState<SavedHoroscopeItem[]>([]);
  const [selectedHoroscopeId, setSelectedHoroscopeId] = useState<string>("");

  // Manual chart input state
  const [manualName, setManualName] = useState<string>("Senthil Kumar");
  const [manualDate, setManualDate] = useState<string>("1992-06-18");
  const [manualTime, setManualTime] = useState<string>("10:35:00");
  const [manualLat, setManualLat] = useState<string>("13.0827");
  const [manualLon, setManualLon] = useState<string>("80.2707");
  const [manualTz, setManualTz] = useState<string>("Asia/Kolkata");
  const [manualPlace, setManualPlace] = useState<string>("Chennai, Tamil Nadu, India");

  // Navigation Tabs
  const [activeTab, setActiveTab] = useState<
    "overview" | "kp-monthly" | "roadmap" | "marriage" | "double-transit" | "ashtakavarga" | "nakshatra" | "horary"
  >("overview");

  // Engine Calculation States
  const [isCalculating, setIsCalculating] = useState(false);
  const [progressStep, setProgressStep] = useState<string>("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Results State Containers
  const [horoData, setHoroData] = useState<HoroscopeResponse | null>(null);
  const [kpMonthlyData, setKpMonthlyData] = useState<KpMonthlyPredictionResponse | null>(null);
  const [roadmapData, setRoadmapData] = useState<LifeRoadmapResponse | null>(null);
  const [marriageData, setMarriageData] = useState<UnifiedMarriageResponse | null>(null);
  const [spouseData, setSpouseData] = useState<SpousePredictionResponse | null>(null);
  const [doubleTransitData, setDoubleTransitData] = useState<DoubleTransitResponse | null>(null);
  const [ashtakavargaData, setAshtakavargaData] = useState<AshtakavargaResponse | null>(null);
  const [kakshaData, setKakshaData] = useState<KakshaAlertsResponse | null>(null);
  const [nakshatrasList, setNakshatrasList] = useState<NakshatraItem[]>(CANONICAL_28_NAKSHATRAS as NakshatraItem[]);

  // Horary Interactive Dock State
  const [horaryNumber, setHoraryNumber] = useState<number>(108);
  const [horaryTopic, setHoraryTopic] = useState<string>("job");
  const [horaryQuery, setHoraryQuery] = useState<string>("");
  const [horaryLoading, setHoraryLoading] = useState<boolean>(false);
  const [horaryResult, setHoraryResult] = useState<InstantHoraryPredictionResponse | null>(null);

  // Double Transit Selected Domain
  const [selectedDtDomain, setSelectedDtDomain] = useState<string>("marriage");

  // Roadmap Selected Horizon
  const [roadmapHorizon, setRoadmapHorizon] = useState<number>(3);
  const [roadmapDomainFilter, setRoadmapDomainFilter] = useState<string>("all");

  // KP Monthly Selected Month & Year
  const currentDate = new Date();
  const [kpYear, setKpYear] = useState<number>(currentDate.getFullYear());
  const [kpMonth, setKpMonth] = useState<number>(currentDate.getMonth() + 1);

  // Load Saved Horoscopes and Nakshatras on mount
  useEffect(() => {
    async function initData() {
      if (!session?.access_token) return;
      try {
        const resp = await fetch("/api/horoscopes?limit=1000", {
          headers: { Authorization: `Bearer ${session.access_token}` },
        });
        if (resp.ok) {
          const data = await resp.json();
          const items: SavedHoroscopeItem[] = data.horoscopes || [];
          setSavedHoroscopes(items);
          if (items.length > 0 && !selectedHoroscopeId) {
            setSelectedHoroscopeId(items[0].id);
            setManualName(items[0].person_name || "Client");
            setManualDate(items[0].birth_date);
            setManualTime(items[0].birth_time);
            setManualLat(String(items[0].latitude));
            setManualLon(String(items[0].longitude));
            setManualTz(items[0].timezone || "Asia/Kolkata");
            setManualPlace(items[0].birthplace || "Chennai");
          }
        }
      } catch (err) {
        console.warn("Could not load saved horoscopes:", err);
      }

      try {
        const nList = await fetchNakshatras();
        if (nList && nList.length >= 27) {
          setNakshatrasList(nList);
        }
      } catch {
        // Fallback already assigned
      }
    }
    if (isAuthenticated) {
      initData();
    }
  }, [isAuthenticated, session?.access_token]);

  // Handle Saved Horoscope Select
  const handleSelectSavedChart = (id: string) => {
    setSelectedHoroscopeId(id);
    const found = savedHoroscopes.find((h) => h.id === id);
    if (found) {
      setManualName(found.person_name || "Client");
      setManualDate(found.birth_date);
      setManualTime(found.birth_time);
      setManualLat(String(found.latitude));
      setManualLon(String(found.longitude));
      setManualTz(found.timezone || "Asia/Kolkata");
      setManualPlace(found.birthplace || "Chennai");
    }
  };

  // Run Master Orchestration (All 8 Engines in Parallel)
  const handleRunMasterPrediction = async () => {
    setIsCalculating(true);
    setErrorMsg(null);
    setProgressStep(isTa ? "அனைத்து 8 ஜோதிட இயந்திரங்களையும் இயக்குகிறது..." : "Initializing all 8 Predictive Engines in parallel...");

    const token = session?.access_token;
    const bDate = manualDate.trim();
    const bTime = manualTime.trim();
    const lat = parseFloat(manualLat) || 13.0827;
    const lon = parseFloat(manualLon) || 80.2707;
    const tz = manualTz.trim() || "Asia/Kolkata";
    const name = manualName.trim() || "Client";

    try {
      // 1. Horoscope Calculation Payload
      const horoReq: HoroscopeRequest = {
        birth_date: bDate,
        birth_time: bTime,
        latitude: lat,
        longitude: lon,
        timezone: tz,
        ayanamsa: 1, // KP
        house_system: 1, // Placidus
        include_panchang: true,
        include_outer_planets: true,
        include_ashtakavarga: true,
        include_vedic_yogas: true,
        include_doshas: true,
      };

      // 2. KP Monthly Payload
      const kpReq: any = {
        year: kpYear,
        month: kpMonth,
        ayanamsa_id: 1,
        birth: {
          birth_date: bDate,
          birth_time: bTime,
          latitude: lat,
          longitude: lon,
          timezone: tz,
          name,
        },
      };

      // 3. Life Roadmap Payload
      const roadmapReq: LifeRoadmapRequest = {
        horizon_years: roadmapHorizon,
        start_date: new Date().toISOString().split("T")[0],
        filter_domain: roadmapDomainFilter === "all" ? undefined : roadmapDomainFilter,
        birth_date: bDate,
        birth_time: bTime,
        timezone: tz,
        latitude: lat,
        longitude: lon,
        place_name: manualPlace,
        customer_name: name,
      };

      // 4. Marriage Payload
      const marriageReq: UnifiedMarriageRequest = {
        birth: {
          birth_date: bDate,
          birth_time: bTime,
          timezone: tz,
          latitude: lat,
          longitude: lon,
        },
        birth_time_uncertainty_seconds: 60,
      };

      // 5. Spouse Payload
      const spouseReq: SpousePredictionRequest = {
        birth: {
          birth_date: bDate,
          birth_time: bTime,
          timezone: tz,
          latitude: lat,
          longitude: lon,
        },
      };

      // 6. Double Transit Payload
      const dtReq: DoubleTransitRequest = {
        birth_date: bDate,
        birth_time: bTime,
        timezone: tz,
        latitude: lat,
        longitude: lon,
        domain: selectedDtDomain,
        forecast_years: 3,
        include_rahu: true,
        ayanamsa: 1,
      };

      // 7. Ashtakavarga Payload
      const avReq = {
        birth_date: bDate,
        birth_time: bTime,
        timezone: tz,
        latitude: lat,
        longitude: lon,
        ayanamsa: 1,
      };

      // 8. Kaksha Alerts Payload
      const kakshaReq: KakshaAlertRequest = {
        birth_date: bDate,
        birth_time: bTime,
        timezone: tz,
        latitude: lat,
        longitude: lon,
        horizon_days: 90,
      };

      // Execute in Parallel with Promise.allSettled for maximum fault tolerance
      const [
        horoSettled,
        kpSettled,
        roadmapSettled,
        marriageSettled,
        spouseSettled,
        dtSettled,
        avSettled,
        kakshaSettled,
      ] = await Promise.allSettled([
        calculateHoroscope(horoReq),
        getKpMonthlyPrediction(kpReq, token),
        generateLifeRoadmap(roadmapReq, token),
        predictMarriageEvent(marriageReq, token),
        predictSpouseEvent(spouseReq, token),
        calculateDoubleTransit(dtReq),
        calculateAshtakavarga(avReq),
        calculateKakshaAlerts(kakshaReq),
      ]);

      if (horoSettled.status === "fulfilled") setHoroData(horoSettled.value);
      if (kpSettled.status === "fulfilled") setKpMonthlyData(kpSettled.value);
      if (roadmapSettled.status === "fulfilled") setRoadmapData(roadmapSettled.value);
      if (marriageSettled.status === "fulfilled") setMarriageData(marriageSettled.value);
      if (spouseSettled.status === "fulfilled") setSpouseData(spouseSettled.value);
      if (dtSettled.status === "fulfilled") setDoubleTransitData(dtSettled.value);
      if (avSettled.status === "fulfilled") setAshtakavargaData(avSettled.value);
      if (kakshaSettled.status === "fulfilled") setKakshaData(kakshaSettled.value);

      // Check failures
      const failureCount = [
        horoSettled,
        kpSettled,
        roadmapSettled,
        marriageSettled,
        dtSettled,
        avSettled,
      ].filter((s) => s.status === "rejected").length;

      if (failureCount > 3) {
        setErrorMsg(
          isTa
            ? "சில கணிப்பு இயந்திரங்கள் பதிலளிக்கவில்லை. பிறந்த நேர விவரங்களை சரிபார்க்கவும்."
            : "Some prediction modules failed to calculate. Please check birth data and coordinates."
        );
      }
    } catch (err: any) {
      console.error("Master prediction failed:", err);
      setErrorMsg(err?.message || "Failed to execute Master Prediction synthesis.");
    } finally {
      setIsCalculating(false);
      setProgressStep("");
    }
  };

  // Run Horary Query inside Dock
  const handleRunHorary = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setHoraryLoading(true);
    try {
      const now = new Date();
      const payload: InstantHoraryPredictionRequest = {
        horary_number: horaryNumber,
        question_topic: horaryTopic,
        question_text: horaryQuery.trim() || undefined,
        question_date: now.toISOString().split("T")[0],
        question_time: now.toTimeString().split(" ")[0],
        timezone: manualTz || "Asia/Kolkata",
        latitude: parseFloat(manualLat) || 13.0827,
        longitude: parseFloat(manualLon) || 80.2707,
      };
      const res = await predictInstantHorary(payload);
      setHoraryResult(res);
    } catch (err: any) {
      console.warn("Horary error:", err);
    } finally {
      setHoraryLoading(false);
    }
  };

  const handleRandomSeed = () => {
    const rnd = Math.floor(Math.random() * 249) + 1;
    setHoraryNumber(rnd);
  };

  // Native Details Extraction from Horoscope or Inputs
  const nativeSummary = useMemo(() => {
    if (!horoData) return null;
    const p = horoData.planets || [];
    const moon = p.find((x) => x.name.toLowerCase() === "moon");
    const lagna = horoData.ascendant;

    return {
      lagnaRasi: lagna?.sign_name || "Aries",
      moonRasi: moon?.sign_name || "Moon Sign",
      moonNakshatra: typeof moon?.nakshatra === "object" ? moon.nakshatra.name : String(moon?.nakshatra || "Nakshatra"),
      moonPada: typeof moon?.nakshatra === "object" ? moon.nakshatra.pada : 1,
    };
  }, [horoData]);

  // Native's Matching Nakshatra from 28 Canonical
  const nativeNakshatraShastra = useMemo(() => {
    const starName = nativeSummary?.moonNakshatra || "Rohini";
    const found = nakshatrasList.find(
      (n) => n.name.toLowerCase() === starName.toLowerCase()
    );
    return found || nakshatrasList[3]; // default Rohini
  }, [nativeSummary, nakshatrasList]);

  return (
    <div className="w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 sm:py-8 space-y-6">
      {/* Breadcrumbs Navigation */}
      <Breadcrumbs
        items={[
          {
            label: isTa ? "ஜோதிடக் கருவிகள்" : "Astrology Tools",
            href: "/tools",
          },
          {
            label: isTa ? "மகா முழுமை கணிப்பு (Master Prediction)" : "Master Prediction Suite",
          },
        ]}
      />

      {/* ========================================================================= */}
      {/* MASTER HERO HEADER                                                        */}
      {/* ========================================================================= */}
      <div className="rounded-3xl border border-[#D8BD80] bg-gradient-to-br from-[#102A4C] via-[#153F6B] to-[#0A1A2E] text-white p-6 sm:p-8 shadow-xl relative overflow-hidden">
        {/* Decorative Golden Ambient Glows */}
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-80 h-80 rounded-full bg-[#B8862B]/20 blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/3 -mb-16 w-72 h-72 rounded-full bg-blue-500/10 blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div className="space-y-2 max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-[#FAF2DE]/20 text-[#F5E1A4] border border-[#D8BD80]/40 backdrop-blur-md uppercase tracking-wider">
              <Crown className="w-4 h-4 text-amber-300" />
              <span>{isTa ? "அனைத்தும் ஒருங்கிணைந்த மகா ஜோதிட அரங்கம்" : "All-In-One Unified Astrologer Suite"}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold font-serif tracking-tight text-[#FFF8E7]">
              {isTa ? "மகா முழுமை கணிப்பு (Master Prediction)" : "Master Prediction Console"}
            </h1>
            <p className="text-xs sm:text-sm text-slate-200/90 leading-relaxed">
              {isTa
                ? "ஒரு ஜாதகத்தைத் திறந்ததும் KP நிகழ்வு கணிப்பு, 1-5 ஆண்டு காலவரிசை, திருமண ஆய்வு, அஷ்டகவர்க்கம், இரட்டை கோச்சாரம், கக்ஷா, 28 நட்சத்திர ரகசியம் மற்றும் 1-249 பிரஸ்னம் அத்தனையும் ஒரே பக்கத்தில் வழங்கும் முழுமையான கணிப்பு இயந்திரம்."
                : "Open any horoscope once to instantly unlock KP Monthly Predictive Timing, 1-5 Year Life Roadmap, Marriage & Spouse Engine, Double Transit (Jupiter & Saturn), Ashtakavarga & Kaksha, 28 Nakshatra Shastra, and Instant 1-249 Horary — all calculated synchronously in one unified screen."}
            </p>
          </div>

          {/* Quick Action Buttons */}
          <div className="flex flex-wrap items-center gap-3 shrink-0">
            <button
              onClick={() => window.print()}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold bg-white/10 hover:bg-white/20 text-white border border-white/20 backdrop-blur-md transition-all cursor-pointer"
            >
              <Printer className="w-4 h-4 text-amber-300" />
              <span>{isTa ? "அறிக்கை அச்சிடு" : "Print Dossier"}</span>
            </button>
            <button
              onClick={handleRunMasterPrediction}
              disabled={isCalculating}
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-bold bg-gradient-to-r from-[#D4AF37] via-[#B8862B] to-[#996515] hover:brightness-110 text-slate-950 shadow-lg shadow-amber-900/30 transition-all cursor-pointer disabled:opacity-50"
            >
              {isCalculating ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>{progressStep || (isTa ? "கணிக்கப்படுகிறது..." : "Synthesizing...")}</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>{isTa ? "மகா கணிப்பை இயக்கு" : "Run Master Prediction"}</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* ===================================================================== */}
        {/* CHART SELECTOR / INPUT DOCK (Inside Hero for Quick Toggle)            */}
        {/* ===================================================================== */}
        <div className="mt-6 pt-6 border-t border-white/10 grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
          {/* Mode Switcher */}
          <div className="md:col-span-3 flex items-center p-1 rounded-xl bg-black/30 border border-white/10 text-xs">
            <button
              type="button"
              onClick={() => setChartMode("saved")}
              className={`flex-1 py-1.5 px-3 rounded-lg font-bold text-center transition-all ${
                chartMode === "saved"
                  ? "bg-[#D8BD80] text-slate-950 shadow-xs"
                  : "text-slate-300 hover:text-white"
              }`}
            >
              {isTa ? "சேமித்த ஜாதகம்" : "Saved Chart"}
            </button>
            <button
              type="button"
              onClick={() => setChartMode("manual")}
              className={`flex-1 py-1.5 px-3 rounded-lg font-bold text-center transition-all ${
                chartMode === "manual"
                  ? "bg-[#D8BD80] text-slate-950 shadow-xs"
                  : "text-slate-300 hover:text-white"
              }`}
            >
              {isTa ? "நேரடி உள்ளீடு" : "Manual Input"}
            </button>
          </div>

          {/* Selector controls based on mode */}
          {chartMode === "saved" ? (
            <div className="md:col-span-9 flex flex-col sm:flex-row items-center gap-3">
              <div className="w-full sm:w-1/2 relative">
                <select
                  value={selectedHoroscopeId}
                  onChange={(e) => handleSelectSavedChart(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-900/80 border border-amber-500/40 text-amber-200 text-xs focus:ring-2 focus:ring-amber-400 focus:outline-hidden"
                >
                  {savedHoroscopes.map((h) => (
                    <option key={h.id} value={h.id} className="bg-slate-900 text-white">
                      {h.person_name} • {h.birth_date} ({h.birthplace || "Chennai"})
                    </option>
                  ))}
                </select>
              </div>

              {/* Active Chart Quick Info Chips */}
              <div className="w-full sm:w-1/2 flex items-center justify-between sm:justify-end gap-2 text-[11px] text-amber-200/90 font-mono">
                <span className="px-2.5 py-1 rounded-lg bg-white/5 border border-white/10">
                  📅 {manualDate}
                </span>
                <span className="px-2.5 py-1 rounded-lg bg-white/5 border border-white/10">
                  ⏰ {manualTime}
                </span>
                <span className="px-2.5 py-1 rounded-lg bg-white/5 border border-white/10 truncate max-w-[140px]">
                  📍 {manualPlace.split(",")[0]}
                </span>
              </div>
            </div>
          ) : (
            <div className="md:col-span-9 grid grid-cols-2 sm:grid-cols-4 gap-2">
              <input
                type="text"
                placeholder="Native Name"
                value={manualName}
                onChange={(e) => setManualName(e.target.value)}
                className="px-2.5 py-1.5 rounded-lg bg-slate-900/80 border border-white/20 text-xs text-white"
              />
              <input
                type="date"
                value={manualDate}
                onChange={(e) => setManualDate(e.target.value)}
                className="px-2.5 py-1.5 rounded-lg bg-slate-900/80 border border-white/20 text-xs text-white"
              />
              <input
                type="time"
                step="1"
                value={manualTime}
                onChange={(e) => setManualTime(e.target.value)}
                className="px-2.5 py-1.5 rounded-lg bg-slate-900/80 border border-white/20 text-xs text-white"
              />
              <input
                type="text"
                placeholder="City / Place"
                value={manualPlace}
                onChange={(e) => setManualPlace(e.target.value)}
                className="px-2.5 py-1.5 rounded-lg bg-slate-900/80 border border-white/20 text-xs text-white"
              />
            </div>
          )}
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-xs text-rose-800 flex items-center gap-3">
          <span>{errorMsg}</span>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MASTER EXECUTIVE SNAPSHOT (Live Metrics Dashboard)                        */}
      {/* ========================================================================= */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1: Native Vital Signatures */}
        <div className="rounded-2xl border border-[#DDE5F0] bg-white p-4 sm:p-5 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
              {isTa ? "ஜன்ம அடையாளங்கள்" : "Vedic Birth Signs"}
            </span>
            <span className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-700 flex items-center justify-center">
              <Compass className="w-4 h-4" />
            </span>
          </div>
          <div>
            <div className="text-lg font-bold text-[#102A4C]">
              {nativeSummary ? `${nativeSummary.lagnaRasi} Lagna` : `${manualName || "Native"}`}
            </div>
            <div className="text-xs text-slate-600 mt-0.5">
              {nativeSummary
                ? `${nativeSummary.moonRasi} • ${nativeSummary.moonNakshatra} (${nativeSummary.moonPada})`
                : `${manualDate} @ ${manualTime}`}
            </div>
          </div>
          <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px]">
            <span className="text-slate-500">{isTa ? "நிலை" : "Status"}:</span>
            <span className="font-bold text-indigo-700">
              {nativeSummary ? "Horoscope Loaded" : "Pending Run"}
            </span>
          </div>
        </div>

        {/* KPI 2: KP Guaranteed Monthly Signal */}
        <div className="rounded-2xl border border-amber-200 bg-amber-50/50 p-4 sm:p-5 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-amber-800 uppercase tracking-wider">
              {isTa ? "KP நடப்பு மாத பலன்" : "KP Guaranteed Event"}
            </span>
            <span className="w-8 h-8 rounded-lg bg-amber-100 text-amber-800 flex items-center justify-center">
              <Sparkles className="w-4 h-4" />
            </span>
          </div>
          <div>
            <div className="text-lg font-bold text-amber-950">
              {kpMonthlyData?.guaranteed_events?.[0]?.title_ta ||
                kpMonthlyData?.guaranteed_events?.[0]?.title_en ||
                (isTa ? "100% உறுதி நிகழ்வு" : "High-Certainty Window")}
            </div>
            <div className="text-xs text-amber-800 line-clamp-1 mt-0.5">
              {kpMonthlyData?.month_label_ta || `${kpMonth}/${kpYear}`} •{" "}
              {kpMonthlyData?.guaranteed_events?.length || 0} {isTa ? "நிகழ்வுகள் தயார்" : "Events Evaluated"}
            </div>
          </div>
          <div className="pt-2 border-t border-amber-200/60 flex items-center justify-between text-[11px]">
            <span className="text-amber-700">{isTa ? "சூரியன் நிலை" : "Transit Sun"}:</span>
            <span className="font-bold text-amber-900">
              {kpMonthlyData?.transit_sun?.start_sign_ta || "Active Trigger"}
            </span>
          </div>
        </div>

        {/* KPI 3: Double Transit Window */}
        <div className="rounded-2xl border border-blue-200 bg-blue-50/50 p-4 sm:p-5 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-blue-800 uppercase tracking-wider">
              {isTa ? "குரு-சனி இரட்டை கோச்சாரம்" : "Double Transit Radar"}
            </span>
            <span className="w-8 h-8 rounded-lg bg-blue-100 text-blue-800 flex items-center justify-center">
              <Clock className="w-4 h-4" />
            </span>
          </div>
          <div>
            <div className="text-lg font-bold text-blue-950">
              {doubleTransitData?.windows?.[0]
                ? `${doubleTransitData.windows[0].start_date.slice(0, 7)} to ${doubleTransitData.windows[0].end_date.slice(0, 7)}`
                : (isTa ? "சுப இணைவு காலம்" : "Upcoming Trigger")}
            </div>
            <div className="text-xs text-blue-800 line-clamp-1 mt-0.5">
              {doubleTransitData?.domain?.name_ta || doubleTransitData?.domain?.name_en || "Marriage & Career"} • House {doubleTransitData?.target_house || 7}
            </div>
          </div>
          <div className="pt-2 border-t border-blue-200/60 flex items-center justify-between text-[11px]">
            <span className="text-blue-700">{isTa ? "ஆசிர்வதிக்கும் கிரகங்கள்" : "Grahas"}:</span>
            <span className="font-bold text-blue-900">Jupiter (Guru) + Saturn (Shani)</span>
          </div>
        </div>

        {/* KPI 4: Marriage & Roadmap Status */}
        <div className="rounded-2xl border border-rose-200 bg-rose-50/50 p-4 sm:p-5 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-rose-800 uppercase tracking-wider">
              {isTa ? "திருமண பிராப்த நிலை" : "Marriage Engine"}
            </span>
            <span className="w-8 h-8 rounded-lg bg-rose-100 text-rose-800 flex items-center justify-center">
              <Heart className="w-4 h-4" />
            </span>
          </div>
          <div>
            <div className="text-lg font-bold text-rose-950">
              {marriageData?.final_verdict === "EVENT_INDICATED"
                ? (isTa ? "திருமண பிராப்தம் உறுதி" : "Promised & Favorable")
                : marriageData?.final_verdict === "EVENT_NOT_INDICATED"
                ? (isTa ? "காரிய தடை / மறுப்பு" : "Event Not Indicated")
                : (isTa ? "7-ம் பாவக ஆய்வு தயார்" : "CSL Analysis Ready")}
            </div>
            <div className="text-xs text-rose-800 line-clamp-1 mt-0.5">
              {marriageData?.timing?.best_window
                ? `${isTa ? "சுப காலம்" : "Window"}: ${marriageData.timing.best_window.start_date} ~ ${marriageData.timing.best_window.end_date}`
                : (isTa ? "தசா-புத்தி ஆய்வு" : "DBA Alignment")}
            </div>
          </div>
          <div className="pt-2 border-t border-rose-200/60 flex items-center justify-between text-[11px]">
            <span className="text-rose-700">{isTa ? "துணைவர் திசை" : "Spouse"}:</span>
            <span className="font-bold text-rose-900">
              {spouseData?.sivadasan_ravi_insights?.street_orientation_ta || spouseData?.sivadasan_ravi_insights?.street_orientation_en || "Favorable Direction"}
            </span>
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* UNIFIED WORKSTATION NAVIGATION TABS                                       */}
      {/* ========================================================================= */}
      <div className="rounded-2xl border border-[#DDE5F0] bg-white p-2 shadow-xs">
        <div className="flex items-center gap-1 overflow-x-auto no-scrollbar py-1">
          {[
            { id: "overview", labelTa: "முழுமை மேலோட்டம்", labelEn: "Master Overview", icon: Eye },
            { id: "kp-monthly", labelTa: "KP நடப்பு பலன்", labelEn: "KP Monthly Timing", icon: Sparkles },
            { id: "roadmap", labelTa: "1-5 ஆண்டு காலவரிசை", labelEn: "Life Roadmap", icon: Calendar },
            { id: "marriage", labelTa: "திருமண கணிப்பு", labelEn: "Marriage & Spouse", icon: Heart },
            { id: "double-transit", labelTa: "இரட்டை கோச்சாரம்", labelEn: "Double Transit", icon: Clock },
            { id: "ashtakavarga", labelTa: "அஷ்டகவர்க்கம் & கக்ஷா", labelEn: "Ashtakavarga & Kaksha", icon: Grid },
            { id: "nakshatra", labelTa: "28 நட்சத்திர சாஸ்திரம்", labelEn: "28 Nakshatras", icon: Star },
            { id: "horary", labelTa: "1-249 உடனடி பிரஸ்னம்", labelEn: "Instant Horary", icon: Zap },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id as any)}
                className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold shrink-0 transition-all cursor-pointer ${
                  isActive
                    ? "bg-[#153F6B] text-white shadow-md shadow-blue-950/20"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-[#D4AF37]" : "text-slate-400"}`} />
                <span>{isTa ? tab.labelTa : tab.labelEn}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* ========================================================================= */}
      {/* TAB CONTENT 1: MASTER OVERVIEW & SYNTHESIS REPORT                         */}
      {/* ========================================================================= */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          <div className="rounded-3xl border border-[#D8BD80]/50 bg-gradient-to-br from-amber-50/50 via-white to-orange-50/30 p-6 sm:p-8 shadow-sm space-y-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-[#E8DFC8] pb-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl bg-[#B8862B] text-white flex items-center justify-center font-bold text-lg shadow-md">
                  👑
                </div>
                <div>
                  <h2 className="text-xl font-bold font-serif text-[#102A4C]">
                    {isTa ? "ஜோதிட மகா தீர்ப்பு சுருக்கம் (Executive Predictive Verdict)" : "Executive Astrological Verdict & Timing"}
                  </h2>
                  <p className="text-xs text-[#64748B]">
                    {isTa
                      ? "8 ஜோதிட விதிகளின் இணைவு மூலம் பெறப்பட்ட உடனடி பலன்கள்."
                      : "Multi-layered astrological convergence across KP, Parashara, and Jaimini systems."}
                  </p>
                </div>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
                {nativeSummary ? `${nativeSummary.lagnaRasi} Lagna` : "Astrology Ready"}
              </span>
            </div>

            {/* Core Pillars Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {/* Pillar 1: KP Monthly Focus */}
              <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-3">
                <div className="flex items-center gap-2 text-amber-700 font-bold text-xs uppercase tracking-wide">
                  <Sparkles className="w-4 h-4" />
                  <span>{isTa ? "நடப்பு மாத முக்கிய நிகழ்வு" : "KP Monthly Guaranteed"}</span>
                </div>
                <p className="text-sm font-semibold text-slate-800">
                  {kpMonthlyData?.guaranteed_events?.[0]?.title_ta ||
                    kpMonthlyData?.guaranteed_events?.[0]?.title_en ||
                    (isTa ? "நிகழ்வு கணக்கிட 'மகா கணிப்பை இயக்கு' பொத்தானை அழுத்தவும்." : "Click 'Run Master Prediction' to populate guaranteed events.")}
                </p>
                <p className="text-xs text-slate-500 leading-relaxed">
                  {kpMonthlyData?.guaranteed_events?.[0]?.summary_verdict_ta ||
                    kpMonthlyData?.guaranteed_events?.[0]?.detailed_analysis_ta ||
                    (isTa ? "உப-நட்சத்திர நாதன் மற்றும் கோச்சார சூரியன் வாயிலாக தீர்மானிக்கப்படும் நிகழ்வு." : "Pinpointed through Cuspal Sub-Lord and Transit Sun trigger.")}
                </p>
              </div>

              {/* Pillar 2: Marriage & Relations */}
              <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-3">
                <div className="flex items-center gap-2 text-rose-700 font-bold text-xs uppercase tracking-wide">
                  <Heart className="w-4 h-4" />
                  <span>{isTa ? "திருமண பிராப்தம் & துணைவர்" : "Marriage & Spouse"}</span>
                </div>
                <p className="text-sm font-semibold text-slate-800">
                  {marriageData?.final_verdict === "EVENT_INDICATED"
                    ? (isTa ? "திருமணம் 100% உறுதியானது (7-ம் பாவக சுப தொடர்பு)" : "Marriage Promised (Houses 2, 7, 11 signified)")
                    : marriageData?.final_verdict === "EVENT_NOT_INDICATED"
                    ? (isTa ? "தாமத திருமணம் (சனி/ராகு பார்வை தாக்கம்)" : "Delayed Marriage (Saturn/Rahu influence)")
                    : (isTa ? "7-ம் பாவகம் தயார் நிலையில் உள்ளது" : "7th House readiness confirmed")}
                </p>
                <p className="text-xs text-slate-500 leading-relaxed">
                  {spouseData
                    ? `${isTa ? "துணைவரின் திசை" : "Direction"}: ${spouseData.sivadasan_ravi_insights?.street_orientation_ta || spouseData.sivadasan_ravi_insights?.street_orientation_en || "East/North"}. ${spouseData.summary_headline_ta || spouseData.summary_headline_en || "Service/Business"}`
                    : (isTa ? "துணைவர் திசை மற்றும் குணம் சிவநேசன் ரவி விதிகளின்படி கணிக்கப்படுகிறது." : "Spouse direction and traits derived via classical Sivadasan Ravi rules.")}
                </p>
              </div>

              {/* Pillar 3: Life Roadmap Peak */}
              <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-3">
                <div className="flex items-center gap-2 text-indigo-700 font-bold text-xs uppercase tracking-wide">
                  <Calendar className="w-4 h-4" />
                  <span>{isTa ? "1-5 ஆண்டு வாழ்க்கை உச்சம்" : "Multi-Year Peak"}</span>
                </div>
                <p className="text-sm font-semibold text-slate-800">
                  {roadmapData?.domain_scorecards?.[0]
                    ? `${roadmapData.domain_scorecards[0].domain_name_ta || roadmapData.domain_scorecards[0].domain_name}: ${roadmapData.domain_scorecards[0].summary_label}`
                    : (isTa ? "தொழில், தனம், திருமணம், பயணம், ஆரோக்கியம்" : "Career, Finance, Marriage, Travel, Health")}
                </p>
                <p className="text-xs text-slate-500 leading-relaxed">
                  {roadmapData?.chronological_periods?.[0]
                    ? `${roadmapData.chronological_periods[0].start_display} ~ ${roadmapData.chronological_periods[0].end_display}: ${roadmapData.chronological_periods[0].mahadasha_lord} Dasa`
                    : (isTa ? "தசா-புத்தி மற்றும் தசாநாதனின் சர்வ பலன்களைக் கொண்டு கணக்கிடப்பட்ட காலவரிசை." : "Evaluated across progressive DBA periods.")}
                </p>
              </div>

              {/* Pillar 4: Double Transit Timing */}
              <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-3">
                <div className="flex items-center gap-2 text-blue-700 font-bold text-xs uppercase tracking-wide">
                  <Clock className="w-4 h-4" />
                  <span>{isTa ? "குரு-சனி இரட்டை கோச்சாரம்" : "Double Transit Confirmation"}</span>
                </div>
                <p className="text-sm font-semibold text-slate-800">
                  {doubleTransitData?.windows?.[0]
                    ? `${doubleTransitData.windows[0].start_date} ~ ${doubleTransitData.windows[0].end_date}`
                    : (isTa ? "இரு பெரும் கிரகங்களின் இணைவு பார்வை" : "Jupiter & Saturn simultaneous aspect")}
                </p>
                <p className="text-xs text-slate-500 leading-relaxed">
                  {isTa
                    ? "B.V. ராமன் விதிப்படி சுப காரியங்கள் கைகூடும் காலம் சனியும் குருவும் இணைந்தே தருகின்றன."
                    : "Classical rule: Major karma sanctions require simultaneous Jupiter and Saturn sanction."}
                </p>
              </div>

              {/* Pillar 5: Ashtakavarga SAV Power */}
              <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-3">
                <div className="flex items-center gap-2 text-purple-700 font-bold text-xs uppercase tracking-wide">
                  <Grid className="w-4 h-4" />
                  <span>{isTa ? "சர்வ அஷ்டகவர்க்க பலம் (SAV)" : "Sarvashtakavarga Strength"}</span>
                </div>
                <p className="text-sm font-semibold text-slate-800">
                  {ashtakavargaData?.sarvashtakavarga
                    ? `SAV Total: ${ashtakavargaData.sarvashtakavarga.total_bindus} Bindus`
                    : (isTa ? "12 ராசிகளின் பரல் கூட்டமைப்பு" : "Bindu distribution across 12 signs")}
                </p>
                <p className="text-xs text-slate-500 leading-relaxed">
                  {isTa
                    ? "28 பரல்களுக்கு மேல் பெற்ற பாவகங்கள் மிகச் சிறந்த யோக பலனையும், குறைந்தவை பரிகாரத் தேவையையும் குறிக்கின்றன."
                    : "Signs with >28 bindus deliver effortless raja yoga; <28 indicate karmic rectification zones."}
                </p>
              </div>

              {/* Pillar 6: 28 Nakshatras & Abhijit */}
              <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-3">
                <div className="flex items-center gap-2 text-teal-700 font-bold text-xs uppercase tracking-wide">
                  <Star className="w-4 h-4" />
                  <span>{isTa ? "ஜன்ம நட்சத்திர சாஸ்திரம் & அபிஜித்" : "Janma Nakshatra & Abhijit"}</span>
                </div>
                <p className="text-sm font-semibold text-slate-800">
                  {nativeNakshatraShastra.name_tamil} ({nativeNakshatraShastra.name})
                </p>
                <p className="text-xs text-slate-500 leading-relaxed">
                  {nativeNakshatraShastra.ruling_deity} • {nativeNakshatraShastra.functional_nature_tamil} • {nativeNakshatraShastra.gaze_direction_tamil}. {isTa ? "அபிஜித் நட்சத்திர தொடர்புடன் கூடியது." : "Includes 28th intercalary Abhijit sync."}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB CONTENT 2: KP MONTHLY & PERIOD TIMING                                */}
      {/* ========================================================================= */}
      {activeTab === "kp-monthly" && (
        <div className="space-y-6">
          <div className="rounded-3xl border border-amber-300 bg-white p-6 sm:p-8 shadow-sm space-y-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
              <div>
                <h3 className="text-lg font-bold font-serif text-[#102A4C] flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-amber-600" />
                  <span>{isTa ? "KP நடப்பு காலக்கட்ட பலன் & நிகழ்வு கணிப்பான்" : "KP Monthly Predictive Event Timing"}</span>
                </h3>
                <p className="text-xs text-slate-500">
                  {isTa
                    ? "தசா-புத்தி-அந்தரம், பாவ உப-நட்சத்திர நாதன் (CSL) மற்றும் கோச்சார சூரியன் மூலம் 100% உறுதி பலன்கள்."
                    : "Pinpoint guaranteed and favorable monthly events via Cuspal Sub-Lord (CSL) and transit Sun."}
                </p>
              </div>

              {/* Month / Year Selector inside card */}
              <div className="flex items-center gap-2">
                <select
                  value={kpMonth}
                  onChange={(e) => setKpMonth(Number(e.target.value))}
                  className="px-3 py-1.5 rounded-xl border border-slate-200 text-xs font-bold text-slate-800 bg-slate-50"
                >
                  {[
                    "ஜனவரி (Jan)", "பிப்ரவரி (Feb)", "மார்ச் (Mar)", "ஏப்ரல் (Apr)",
                    "மே (May)", "ஜூன் (Jun)", "ஜூலை (Jul)", "ஆகஸ்ட் (Aug)",
                    "செப்டம்பர் (Sep)", "அக்டோபர் (Oct)", "நவம்பர் (Nov)", "டிசம்பர் (Dec)",
                  ].map((m, idx) => (
                    <option key={idx} value={idx + 1}>{m}</option>
                  ))}
                </select>
                <select
                  value={kpYear}
                  onChange={(e) => setKpYear(Number(e.target.value))}
                  className="px-3 py-1.5 rounded-xl border border-slate-200 text-xs font-bold text-slate-800 bg-slate-50"
                >
                  {[2024, 2025, 2026, 2027, 2028, 2029, 2030].map((y) => (
                    <option key={y} value={y}>{y}</option>
                  ))}
                </select>
                <button
                  type="button"
                  onClick={handleRunMasterPrediction}
                  className="px-3 py-1.5 rounded-xl bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold cursor-pointer"
                >
                  {isTa ? "புதுப்பி" : "Refresh"}
                </button>
              </div>
            </div>

            {/* Guaranteed Events List */}
            <div className="space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-amber-800 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>{isTa ? "100% கண்டிப்பாக நடந்து தீரும் நிகழ்வுகள் (Guaranteed Events)" : "Guaranteed Life Events"}</span>
              </h4>

              {kpMonthlyData?.guaranteed_events && kpMonthlyData.guaranteed_events.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {kpMonthlyData.guaranteed_events.map((ev, i) => (
                    <div
                      key={i}
                      className="p-4 rounded-2xl bg-gradient-to-br from-amber-50/70 via-white to-amber-50/30 border border-amber-300 shadow-xs space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold font-serif text-slate-900">
                          {isTa ? ev.title_ta : ev.title_en}
                        </span>
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                          {isTa ? "100% உறுதி" : "Guaranteed"}
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 leading-relaxed">
                        {ev.summary_verdict_ta || ev.detailed_analysis_ta}
                      </p>
                      <div className="pt-2 border-t border-amber-100 flex items-center justify-between text-[11px] text-slate-500">
                        <span>{isTa ? "காரக பாவகங்கள்" : "Signified Houses"}:</span>
                        <span className="font-mono font-bold text-amber-800">
                          {ev.primary_houses?.join(", ") || "Active"}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-6 rounded-2xl bg-slate-50 border border-dashed border-slate-200 text-center text-xs text-slate-500">
                  {isTa
                    ? "இந்த மாதத்திற்கான KP பலன்களைக் கணக்கிட மேலே உள்ள 'மகா கணிப்பை இயக்கு' பொத்தானை அழுத்தவும்."
                    : "No specific guaranteed event recorded for this month. Click 'Run Master Prediction' to fetch fresh calculations."}
                </div>
              )}
            </div>

            {/* Favorable & Opportunity Signals */}
            {kpMonthlyData?.favorable_events && kpMonthlyData.favorable_events.length > 0 && (
              <div className="space-y-4 pt-4 border-t border-slate-100">
                <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-800 flex items-center gap-2">
                  <Star className="w-4 h-4 text-emerald-600" />
                  <span>{isTa ? "சுப நிகழ்வுகள் & வாய்ப்புகள் (Favorable Opportunities)" : "Favorable Opportunities"}</span>
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {kpMonthlyData.favorable_events.map((ev, i) => (
                    <div key={i} className="p-4 rounded-2xl bg-emerald-50/50 border border-emerald-200 space-y-2">
                      <div className="text-xs font-bold text-emerald-950">
                        {isTa ? ev.title_ta : ev.title_en}
                      </div>
                      <p className="text-xs text-emerald-900/80">
                        {ev.summary_verdict_ta || ev.detailed_analysis_ta}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB CONTENT 3: MULTI-YEAR LIFE ROADMAP (1-5 YEARS)                       */}
      {/* ========================================================================= */}
      {activeTab === "roadmap" && (
        <div className="space-y-6">
          <div className="rounded-3xl border border-emerald-300 bg-white p-6 sm:p-8 shadow-sm space-y-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
              <div>
                <h3 className="text-lg font-bold font-serif text-[#102A4C] flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-emerald-600" />
                  <span>{isTa ? "வாழ்க்கை காலவரிசை கணிப்பு (Multi-Year Life Roadmap)" : "Multi-Year Life Roadmap (1-5 Years)"}</span>
                </h3>
                <p className="text-xs text-slate-500">
                  {isTa
                    ? "அனைத்து 5 முக்கிய வாழ்க்கை துறைகளிலும் அடுத்த 1 முதல் 5 ஆண்டுகளுக்கான முழு காலவரிசை வரைபடம்."
                    : "Automated multi-year timeline evaluating Career, Relationships, Finance, Relocation, and Health."}
                </p>
              </div>

              {/* Horizon & Domain Filter */}
              <div className="flex items-center gap-2">
                <select
                  value={roadmapHorizon}
                  onChange={(e) => setRoadmapHorizon(Number(e.target.value))}
                  className="px-3 py-1.5 rounded-xl border border-slate-200 text-xs font-bold text-slate-800 bg-slate-50"
                >
                  <option value={1}>{isTa ? "1 வருடம் (1 Year)" : "1 Year"}</option>
                  <option value={3}>{isTa ? "3 வருடங்கள் (3 Years)" : "3 Years"}</option>
                  <option value={5}>{isTa ? "5 வருடங்கள் (5 Years)" : "5 Years"}</option>
                </select>
                <select
                  value={roadmapDomainFilter}
                  onChange={(e) => setRoadmapDomainFilter(e.target.value)}
                  className="px-3 py-1.5 rounded-xl border border-slate-200 text-xs font-bold text-slate-800 bg-slate-50"
                >
                  <option value="all">{isTa ? "அனைத்து துறைகள் (All)" : "All Domains"}</option>
                  <option value="career">{isTa ? "தொழில் (Career)" : "Career"}</option>
                  <option value="marriage">{isTa ? "திருமணம் (Relationships)" : "Relationships"}</option>
                  <option value="finance">{isTa ? "தனம் (Finance)" : "Finance"}</option>
                  <option value="travel">{isTa ? "பயணம் (Relocation)" : "Relocation"}</option>
                  <option value="health">{isTa ? "ஆரோக்கியம் (Health)" : "Health"}</option>
                </select>
              </div>
            </div>

            {/* Scorecards Across Domains */}
            {roadmapData?.domain_scorecards && roadmapData.domain_scorecards.length > 0 && (
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                {roadmapData.domain_scorecards.map((sc: DomainScorecard) => (
                  <div
                    key={sc.domain_id}
                    className="p-3.5 rounded-2xl border border-slate-200 bg-slate-50/70 text-center space-y-1.5"
                  >
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                      {sc.domain_name_ta || sc.domain_name}
                    </span>
                    <div className="text-sm font-bold font-serif text-[#102A4C]">
                      {sc.summary_label}
                    </div>
                    <span className={`inline-block px-2 py-0.5 rounded-md text-[10px] font-bold ${
                      sc.status_color === "green"
                        ? "bg-emerald-100 text-emerald-800"
                        : sc.status_color === "orange"
                        ? "bg-amber-100 text-amber-800"
                        : "bg-rose-100 text-rose-800"
                    }`}>
                      {sc.status_color.toUpperCase()}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {/* Chronological Milestones */}
            <div className="space-y-4 pt-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600">
                {isTa ? "முக்கிய கால மைல்கற்கள் (Chronological Periods)" : "Key Timing Periods"}
              </h4>

              {roadmapData?.chronological_periods && roadmapData.chronological_periods.length > 0 ? (
                <div className="space-y-3">
                  {roadmapData.chronological_periods.slice(0, 8).map((p: RoadmapPeriodItem, idx: number) => (
                    <div
                      key={idx}
                      className="p-4 rounded-2xl border border-slate-200 bg-white hover:border-emerald-300 transition-all space-y-2"
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-50 text-emerald-800 border border-emerald-200 font-mono">
                            {p.start_display} ~ {p.end_display}
                          </span>
                          <span className="text-xs font-bold text-slate-800">
                            {p.mahadasha_lord} - {p.bhukti_lord}
                          </span>
                        </div>
                        <span className={`text-[11px] font-bold px-2 py-0.5 rounded ${
                          p.primary_status === "green"
                            ? "bg-emerald-100 text-emerald-800"
                            : p.primary_status === "orange"
                            ? "bg-amber-100 text-amber-800"
                            : "bg-slate-100 text-slate-700"
                        }`}>
                          {p.primary_status.toUpperCase()}
                        </span>
                      </div>

                      {p.all_milestones && p.all_milestones.length > 0 && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 pt-2 border-t border-slate-100">
                          {p.all_milestones.slice(0, 4).map((m: ScoredMilestone, mIdx: number) => (
                            <div key={mIdx} className="text-xs text-slate-600 flex items-start gap-1.5">
                              <span className="text-emerald-600 shrink-0 font-bold">•</span>
                              <span>
                                <strong className="text-slate-800">{m.domain_name.toUpperCase()}:</strong> {m.event_name}
                              </span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-6 rounded-2xl bg-slate-50 border border-dashed border-slate-200 text-center text-xs text-slate-500">
                  {isTa
                    ? "வாழ்க்கை காலவரிசை தகவல்களைப் பெற 'மகா கணிப்பை இயக்கு' பொத்தானை அழுத்தவும்."
                    : "Roadmap timeline pending. Click 'Run Master Prediction' to compute."}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB CONTENT 4: MARRIAGE & SPOUSE PREDICTION                              */}
      {/* ========================================================================= */}
      {activeTab === "marriage" && (
        <div className="space-y-6">
          <div className="rounded-3xl border border-rose-300 bg-white p-6 sm:p-8 shadow-sm space-y-6">
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <div>
                <h3 className="text-lg font-bold font-serif text-[#102A4C] flex items-center gap-2">
                  <Heart className="w-5 h-5 text-rose-600" />
                  <span>{isTa ? "திருமண கணிப்பு & களத்திர ஆய்வு (Marriage & Spouse)" : "Marriage & Spouse Prediction Engine"}</span>
                </h3>
                <p className="text-xs text-slate-500">
                  {isTa
                    ? "7-ம் பாவ உப-அதிபதி (CSL), விவாக பிராப்த காலம் மற்றும் சிவநேசன் ரவி விதிகளின்படி துணைவர் இயல்புகள்."
                    : "7th Cuspal Sub-Lord analysis, marriage timing windows, and Sivadasan Ravi spouse traits."}
                </p>
              </div>

              {marriageData?.final_verdict && (
                <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                  marriageData.final_verdict === "EVENT_INDICATED"
                    ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                    : "bg-amber-100 text-amber-800 border border-amber-300"
                }`}>
                  {marriageData.final_verdict}
                </span>
              )}
            </div>

            {/* Core Marriage Verdict & Windows */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {/* Marriage Timing Windows */}
              <div className="p-5 rounded-2xl bg-rose-50/50 border border-rose-200 space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-rose-800 flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-rose-600" />
                  <span>{isTa ? "திருமண யோக விண்டோ (Timing Window)" : "Prime Marriage Window"}</span>
                </h4>
                {marriageData?.timing?.best_window ? (
                  <div className="p-3 rounded-xl bg-white border border-rose-100 flex items-center justify-between text-xs">
                    <span className="font-mono font-bold text-rose-950">
                      {marriageData.timing.best_window.start_date} ~ {marriageData.timing.best_window.end_date}
                    </span>
                    <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-rose-100 text-rose-800">
                      Score: {marriageData.timing.best_window.confidence_score}%
                    </span>
                  </div>
                ) : (
                  <p className="text-xs text-slate-600">
                    {marriageData?.kp_promise?.explanation || (isTa ? "7-ம் பாவக உப-அதிபதி தொடர்பு உறுதி செய்யப்பட்டுள்ளது." : "CSL signifies favorable marriage houses.")}
                  </p>
                )}
              </div>

              {/* Sivadasan Ravi Spouse Characteristics */}
              <div className="p-5 rounded-2xl bg-indigo-50/50 border border-indigo-200 space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-800 flex items-center gap-2">
                  <User className="w-4 h-4 text-indigo-600" />
                  <span>{isTa ? "துணைவரின் குணாதிசயங்கள் & திசை (Spouse Profile)" : "Spouse Direction & Traits"}</span>
                </h4>
                {spouseData ? (
                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between py-1 border-b border-indigo-100">
                      <span className="text-indigo-900/70">{isTa ? "துணைவர் வரும் திசை" : "Direction"}:</span>
                      <span className="font-bold text-indigo-950">
                        {spouseData.sivadasan_ravi_insights?.street_orientation_ta || spouseData.sivadasan_ravi_insights?.street_orientation_en || "East / North"}
                      </span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-indigo-100">
                      <span className="text-indigo-900/70">{isTa ? "குடும்ப அளவு" : "Family"}:</span>
                      <span className="font-bold text-indigo-950">
                        {spouseData.sivadasan_ravi_insights?.family_size_ta || spouseData.sivadasan_ravi_insights?.family_size || "Auspicious Family"}
                      </span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-indigo-100">
                      <span className="text-indigo-900/70">{isTa ? "ராசி லக்கினம்" : "7th Sign"}:</span>
                      <span className="font-bold text-indigo-950">
                        {spouseData.seventh_sign?.sign_tamil || spouseData.seventh_sign?.sign}
                      </span>
                    </div>
                    <div className="flex justify-between py-1">
                      <span className="text-indigo-900/70">{isTa ? "சுபாவம் & குணம்" : "Nature"}:</span>
                      <span className="font-bold text-indigo-950">
                        {spouseData.seventh_sign?.temperament_ta || "Auspicious"}
                      </span>
                    </div>
                  </div>
                ) : (
                  <p className="text-xs text-slate-600">
                    {isTa ? "துணைவர் விபரங்கள் தயாராக உள்ளன." : "Spouse traits will populate upon Master Prediction execution."}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB CONTENT 5: DOUBLE TRANSIT TIMING (GURU & SHANI)                     */}
      {/* ========================================================================= */}
      {activeTab === "double-transit" && (
        <div className="space-y-6">
          <div className="rounded-3xl border border-blue-300 bg-white p-6 sm:p-8 shadow-sm space-y-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
              <div>
                <h3 className="text-lg font-bold font-serif text-[#102A4C] flex items-center gap-2">
                  <Clock className="w-5 h-5 text-blue-600" />
                  <span>{isTa ? "குரு & சனி இரட்டை கோச்சாரம் (Double Transit Timing)" : "Jupiter & Saturn Double Transit Radar"}</span>
                </h3>
                <p className="text-xs text-slate-500">
                  {isTa
                    ? "B.V. ராமன் & K.N. ராவ் விதி: கர்ம காரகன் சனியும் ஜீவ காரகன் குருவும் ஒரே நேரத்தில் பாவகத்தை ஆசீர்வதிக்கும் காலம்."
                    : "Simultaneous activation of houses by Jupiter and Saturn to sanction major life milestones."}
                </p>
              </div>

              {/* Domain Switcher */}
              <select
                value={selectedDtDomain}
                onChange={(e) => setSelectedDtDomain(e.target.value)}
                className="px-3 py-1.5 rounded-xl border border-slate-200 text-xs font-bold text-slate-800 bg-slate-50"
              >
                {DOUBLE_TRANSIT_DOMAINS.map((d) => (
                  <option key={d.id} value={d.id}>
                    {isTa ? `${d.labelTa} (${d.house}-ம் பாவம்)` : `${d.labelEn} (House ${d.house})`}
                  </option>
                ))}
              </select>
            </div>

            {/* Active Double Transit Windows */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-blue-800">
                {isTa ? "உறுதிப்படுத்தப்பட்ட இணைவு விண்டோக்கள் (Active Windows)" : "Confirmed Transit Windows"}
              </h4>

              {doubleTransitData?.windows && doubleTransitData.windows.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {doubleTransitData.windows.map((w: DoubleTransitWindow, idx: number) => (
                    <div
                      key={idx}
                      className="p-5 rounded-2xl bg-gradient-to-br from-blue-50/70 via-white to-blue-50/30 border border-blue-200 shadow-xs space-y-3"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-blue-950 font-serif">
                          Transit Window #{idx + 1}
                        </span>
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-blue-800 font-mono">
                          {w.start_date} ~ {w.end_date}
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 leading-relaxed">
                        {isTa
                          ? `குரு (${w.jupiter_transit_sign}) மற்றும் சனி (${w.saturn_transit_sign}) இருவரும் ஒரே நேரத்தில் இலக்கு பாவகத்தை ஆசீர்வதிக்கின்றனர்.`
                          : `Simultaneous activation: Jupiter in ${w.jupiter_transit_sign} and Saturn in ${w.saturn_transit_sign}.`}
                      </p>
                      <div className="pt-2 border-t border-blue-100 flex items-center justify-between text-[11px] text-blue-900 font-bold">
                        <span>{isTa ? "கால அளவு" : "Duration"}:</span>
                        <span>{w.duration_months} {isTa ? "மாதங்கள்" : "Months"}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-6 rounded-2xl bg-slate-50 border border-dashed border-slate-200 text-center text-xs text-slate-500">
                  {isTa
                    ? "இரட்டை கோச்சார விண்டோக்களை அறிய 'மகா கணிப்பை இயக்கு' பொத்தானை அழுத்தவும்."
                    : "No double transit window returned yet. Click 'Run Master Prediction' to calculate."}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB CONTENT 6: ASHTAKAVARGA & KAKSHA TRANSIT                             */}
      {/* ========================================================================= */}
      {activeTab === "ashtakavarga" && (
        <div className="space-y-6">
          <div className="rounded-3xl border border-purple-300 bg-white p-6 sm:p-8 shadow-sm space-y-6">
            <div className="border-b border-slate-100 pb-4">
              <h3 className="text-lg font-bold font-serif text-[#102A4C] flex items-center gap-2">
                <Grid className="w-5 h-5 text-purple-600" />
                <span>{isTa ? "அஷ்டகவர்க்கம் & கக்ஷா கோச்சார ஆய்வு" : "Ashtakavarga & Kaksha Micro-Transit"}</span>
              </h3>
              <p className="text-xs text-slate-500">
                {isTa
                  ? "சர்வ அஷ்டகவர்க்கம் (SAV) பரல்கள் மற்றும் ஒவ்வொரு ராசியின் 8 கக்ஷா (3°45') பாகங்களில் சுப பரல் உள்ள கோச்சார தினங்கள்."
                  : "Sarvashtakavarga bindu distribution and 3°45' Kaksha transit benefic windows."}
              </p>
            </div>

            {/* SAV 12 Rasis Matrix */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-purple-800">
                {isTa ? "சர்வ அஷ்டகவர்க்க கூட்டுத்தொகை (SAV Matrix - 12 Rasis)" : "Sarvashtakavarga (SAV) Matrix"}
              </h4>

              {ashtakavargaData?.sarvashtakavarga ? (
                <div className="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-6 gap-3">
                  {[
                    "Aries", "Taurus", "Gemini", "Cancer",
                    "Leo", "Virgo", "Libra", "Scorpio",
                    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
                  ].map((signName, idx) => {
                    const bindusMap: Record<string, number> = ashtakavargaData.sarvashtakavarga?.sign_bindus || {};
                    const points = bindusMap[signName] ?? 28;
                    const isStrong = points >= 28;
                    return (
                      <div
                        key={idx}
                        className={`p-3 rounded-2xl border text-center space-y-1 transition-all ${
                          isStrong
                            ? "bg-purple-50/70 border-purple-200 text-purple-950"
                            : "bg-slate-50 border-slate-200 text-slate-700"
                        }`}
                      >
                        <span className="text-[11px] font-bold block">{signName}</span>
                        <div className="text-xl font-bold font-serif">
                          {points} <span className="text-[10px] font-sans font-normal text-slate-500">பரல்</span>
                        </div>
                        <span className={`inline-block px-1.5 py-0.2 rounded text-[9px] font-bold ${
                          isStrong ? "bg-purple-200 text-purple-900" : "bg-slate-200 text-slate-600"
                        }`}>
                          {isStrong ? (isTa ? "சுப பலம்" : "Strong") : (isTa ? "சுமாரான" : "Weak")}
                        </span>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="p-6 rounded-2xl bg-slate-50 border border-dashed border-slate-200 text-center text-xs text-slate-500">
                  {isTa ? "அஷ்டகவர்க்க பரல்களைப் பெற 'மகா கணிப்பை இயக்கு' பொத்தானை அழுத்தவும்." : "Ashtakavarga data pending calculation."}
                </div>
              )}
            </div>

            {/* Kaksha Micro-Transit Benefic Windows */}
            {kakshaData?.timeline_alerts && kakshaData.timeline_alerts.length > 0 && (
              <div className="space-y-3 pt-4 border-t border-slate-100">
                <h4 className="text-xs font-bold uppercase tracking-wider text-teal-800">
                  {isTa ? "கக்ஷா கோச்சார சுப தினங்கள் (Kaksha Benefic Windows - 3°45')" : "Upcoming Kaksha Benefic Windows"}
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {kakshaData.timeline_alerts.slice(0, 4).map((alert, aIdx) => (
                    <div key={aIdx} className="p-3.5 rounded-xl bg-teal-50/50 border border-teal-200 text-xs space-y-1">
                      <div className="flex items-center justify-between font-bold text-teal-950">
                        <span>{alert.planet} in Kaksha {alert.kaksha_lord}</span>
                        <span className="px-2 py-0.5 rounded-full text-[10px] bg-teal-100 text-teal-800 font-mono">
                          {alert.start_date} ~ {alert.end_date}
                        </span>
                      </div>
                      <p className="text-[11px] text-teal-800">
                        {isTa
                          ? `சுப பரல் உள்ள கக்ஷா. இந்த நாட்களில் தொடங்கும் காரியங்கள் நிச்சயம் வெற்றியடையும்.`
                          : `Benefic Kaksha transit active with bindu score. Auspicious for progressive endeavors.`}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB CONTENT 7: 28 NAKSHATRAS SHASTRA PORTAL                               */}
      {/* ========================================================================= */}
      {activeTab === "nakshatra" && (
        <div className="space-y-6">
          <div className="rounded-3xl border border-teal-300 bg-white p-6 sm:p-8 shadow-sm space-y-6">
            <div className="border-b border-slate-100 pb-4">
              <h3 className="text-lg font-bold font-serif text-[#102A4C] flex items-center gap-2">
                <Star className="w-5 h-5 text-teal-600" />
                <span>{isTa ? "28 நட்சத்திர சாஸ்திர அரங்கம் & தாராபலம்" : "28 Nakshatra Shastra & Tara Bala Portal"}</span>
              </h3>
              <p className="text-xs text-slate-500">
                {isTa
                  ? "28-வது நட்சத்திரமான அபிஜித் (Abhijit) உள்ளிட்ட முழுமையான சாஸ்திர ரகசியங்கள் மற்றும் ஜன்ம தாராபல அட்டவணை."
                  : "Complete 28-Nakshatra esoteric portal with intercalary Abhijit sync and Tara Bala dynamics."}
              </p>
            </div>

            {/* Native Star Deep Dossier */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-teal-50/70 via-white to-amber-50/30 border border-teal-200 shadow-xs space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-teal-100 pb-3">
                <div className="flex items-center gap-2">
                  <span className="text-xl">🌟</span>
                  <span className="text-base font-bold text-teal-950 font-serif">
                    {nativeNakshatraShastra.name_tamil} ({nativeNakshatraShastra.name})
                  </span>
                </div>
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-teal-100 text-teal-900 border border-teal-300">
                  {nativeNakshatraShastra.span_zodiac}
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="p-3 rounded-xl bg-white border border-slate-100 space-y-0.5">
                  <span className="text-[10px] text-slate-400 font-bold uppercase">{isTa ? "அதிபதி" : "Planet"}</span>
                  <div className="font-bold text-slate-800">{nativeNakshatraShastra.ruling_planet}</div>
                </div>
                <div className="p-3 rounded-xl bg-white border border-slate-100 space-y-0.5">
                  <span className="text-[10px] text-slate-400 font-bold uppercase">{isTa ? "தேவதை" : "Deity"}</span>
                  <div className="font-bold text-slate-800">{nativeNakshatraShastra.ruling_deity}</div>
                </div>
                <div className="p-3 rounded-xl bg-white border border-slate-100 space-y-0.5">
                  <span className="text-[10px] text-slate-400 font-bold uppercase">{isTa ? "குணம்" : "Nature"}</span>
                  <div className="font-bold text-slate-800">{nativeNakshatraShastra.functional_nature_tamil}</div>
                </div>
                <div className="p-3 rounded-xl bg-white border border-slate-100 space-y-0.5">
                  <span className="text-[10px] text-slate-400 font-bold uppercase">{isTa ? "பார்வை" : "Gaze"}</span>
                  <div className="font-bold text-slate-800">{nativeNakshatraShastra.gaze_direction_tamil}</div>
                </div>
              </div>

              {/* Abhijit Intercalary Star Callout */}
              <div className="p-4 rounded-xl bg-amber-50/80 border border-amber-300 text-xs space-y-1">
                <div className="font-bold text-amber-950 flex items-center gap-1.5">
                  <Crown className="w-4 h-4 text-amber-600" />
                  <span>28-வது அபிஜித் நட்சத்திர ரகசியம் (Abhijit Intercalary Star)</span>
                </div>
                <p className="text-[11px] text-amber-900 leading-relaxed">
                  {isTa
                    ? "மகர ராசியில் 06°40' முதல் 10°53' வரை உள்ள பகுதி அபிஜித் நட்சத்திரமாகும். இது சர்வ தோஷங்களை நீக்கும் சர்வார்த்த சித்த யோகத்திற்குரிய மகா சுப நட்சத்திரமாகும்."
                    : "Spans 06°40' to 10°53' Capricorn. The timeless 28th intercalary nakshatra that neutralizes planetary afflictions in classical Sarvatobhadra Chakra."}
                </p>
              </div>
            </div>

            {/* 9 Tara Bala Breakdown */}
            <div className="space-y-3 pt-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600">
                {isTa ? "நவ தாரா பலன்கள் (9 Tara Bala Evaluation)" : "9 Tara Bala Matrix"}
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {TARA_BALA_TYPES.map((tb) => (
                  <div
                    key={tb.id}
                    className={`p-3.5 rounded-xl border space-y-1 ${
                      tb.grade === "GOOD"
                        ? "bg-emerald-50/50 border-emerald-200 text-emerald-950"
                        : "bg-rose-50/50 border-rose-200 text-rose-950"
                    }`}
                  >
                    <div className="flex items-center justify-between text-xs font-bold">
                      <span>{tb.id}. {isTa ? tb.name_ta : tb.name}</span>
                      <span className={`px-1.5 py-0.2 rounded text-[9px] ${
                        tb.grade === "GOOD" ? "bg-emerald-200 text-emerald-900" : "bg-rose-200 text-rose-900"
                      }`}>
                        {tb.grade === "GOOD" ? (isTa ? "சுபம்" : "Benefic") : (isTa ? "அசுபம்" : "Malefic")}
                      </span>
                    </div>
                    <p className="text-[11px] opacity-80 leading-tight">
                      {tb.desc_ta}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB CONTENT 8: INSTANT KP HORARY (1-249) QUICK DOCK                       */}
      {/* ========================================================================= */}
      {activeTab === "horary" && (
        <div className="space-y-6">
          <div className="rounded-3xl border border-[#D8BD80] bg-white p-6 sm:p-8 shadow-sm space-y-6">
            <div className="border-b border-slate-100 pb-4">
              <h3 className="text-lg font-bold font-serif text-[#102A4C] flex items-center gap-2">
                <Zap className="w-5 h-5 text-amber-600" />
                <span>{isTa ? "கே.பி. உடனடி பிரஸ்னம் (1-249 நிகழ்வு கணிப்பாளர்)" : "Instant KP Horary / Prashna Predictor (1-249)"}</span>
              </h3>
              <p className="text-xs text-slate-500">
                {isTa
                  ? "வாடிக்கையாளர் கேட்கும் உடனடி கேள்விகளுக்கு (விசா, வேலை, நீதிமன்றம், திருமணம்) 1-249 எண் மூலம் உடனடி காரிய சித்தி தீர்ப்பு."
                  : "Resolve real-time queries (Visa, Job, Marriage, Court Case, Health) instantly without losing the birth chart view."}
              </p>
            </div>

            {/* Quick Query Form */}
            <form onSubmit={handleRunHorary} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
                {/* Number Input & Random Seed */}
                <div className="md:col-span-4 p-4 rounded-2xl bg-amber-50/60 border border-amber-200 space-y-2">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-bold text-amber-950">
                      {isTa ? "பிரஸ்ன எண் (1 முதல் 249)*" : "Horary Seed Number (1-249)*"}
                    </label>
                    <button
                      type="button"
                      onClick={handleRandomSeed}
                      className="px-2.5 py-1 rounded-lg bg-white border border-amber-300 text-amber-800 text-[11px] font-bold hover:bg-amber-100 flex items-center gap-1 cursor-pointer"
                    >
                      <Dice5 className="w-3 h-3" />
                      <span>{isTa ? "ரேண்டம்" : "Random"}</span>
                    </button>
                  </div>
                  <div className="flex items-center gap-3">
                    <input
                      type="number"
                      min={1}
                      max={249}
                      value={horaryNumber}
                      onChange={(e) => setHoraryNumber(Number(e.target.value) || 1)}
                      className="w-20 px-3 py-1.5 text-center text-xl font-bold font-serif text-slate-900 rounded-xl border border-amber-300 bg-white"
                    />
                    <input
                      type="range"
                      min={1}
                      max={249}
                      value={horaryNumber}
                      onChange={(e) => setHoraryNumber(Number(e.target.value) || 1)}
                      className="flex-1 accent-amber-600 cursor-pointer"
                    />
                  </div>
                </div>

                {/* Topic Selector */}
                <div className="md:col-span-4 space-y-1.5">
                  <label className="text-xs font-bold text-slate-700">
                    {isTa ? "கேள்வித் துறை (Topic)*" : "Question Topic*"}
                  </label>
                  <select
                    value={horaryTopic}
                    onChange={(e) => setHoraryTopic(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-bold text-slate-800 bg-slate-50 focus:ring-2 focus:ring-amber-500"
                  >
                    <option value="job">{isTa ? "வேலை / தொழில் உயர்வு (Job & Career)" : "Job & Career"}</option>
                    <option value="visa">{isTa ? "விசா அனுமதி & வெளிநாடு (Visa & Relocation)" : "Visa & Travel"}</option>
                    <option value="marriage">{isTa ? "திருமண காரிய சித்தி (Marriage Timing)" : "Marriage Timing"}</option>
                    <option value="court_case">{isTa ? "நீதிமன்ற வழக்கு வெற்றி (Court Case)" : "Court Case Victory"}</option>
                    <option value="recovery">{isTa ? "உடல் நலம் & நோய் குணமாகுதல் (Health Recovery)" : "Health Recovery"}</option>
                    <option value="property">{isTa ? "சொத்து & பூமி சேர்க்கை (Property Purchase)" : "Property"}</option>
                    <option value="financial_gain">{isTa ? "தன லாபம் (Financial Gain)" : "Financial Gain"}</option>
                  </select>
                </div>

                {/* Submit Action */}
                <div className="md:col-span-4 flex items-end">
                  <button
                    type="submit"
                    disabled={horaryLoading}
                    className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-950 font-bold text-xs flex items-center justify-center gap-2 shadow-md cursor-pointer disabled:opacity-50"
                  >
                    {horaryLoading ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        <span>{isTa ? "தீர்ப்பு கணிக்கப்படுகிறது..." : "Resolving Query..."}</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4" />
                        <span>{isTa ? "உடனடி தீர்ப்பு காண்க" : "Reveal Horary Verdict"}</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </form>

            {/* Instant Horary Verdict Card */}
            {horaryResult && (
              <div
                className={`p-6 rounded-3xl border-2 space-y-4 transition-all ${
                  horaryResult.outcome === "YES"
                    ? "bg-emerald-50/70 border-emerald-300"
                    : horaryResult.outcome === "DELAYED"
                    ? "bg-amber-50/70 border-amber-300"
                    : "bg-rose-50/70 border-rose-300"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="w-10 h-10 rounded-xl bg-white border border-slate-200 text-amber-800 font-bold font-serif text-lg flex items-center justify-center shadow-xs">
                      #{horaryResult.horary_number}
                    </span>
                    <div>
                      <h4 className="text-base font-bold font-serif text-slate-900">
                        {isTa ? "காரிய சித்தி தீர்ப்பு" : "Event Verdict"}
                      </h4>
                      <p className="text-xs text-slate-600">
                        {horaryResult.question_text || horaryTopic}
                      </p>
                    </div>
                  </div>

                  <span className={`px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider ${
                    horaryResult.outcome === "YES"
                      ? "bg-emerald-200 text-emerald-950"
                      : horaryResult.outcome === "DELAYED"
                      ? "bg-amber-200 text-amber-950"
                      : "bg-rose-200 text-rose-950"
                  }`}>
                    {horaryResult.outcome === "YES"
                      ? (isTa ? "வெற்றி / காரிய சித்தி (YES)" : "CONFIRMED (YES)")
                      : horaryResult.outcome === "DELAYED"
                      ? (isTa ? "தாமத வெற்றி (DELAYED)" : "DELAYED SUCCESS")
                      : (isTa ? "தோல்வி / தடைகள் (NO)" : "UNFAVORABLE (NO)")}
                  </span>
                </div>

                <p className="text-xs text-slate-700 leading-relaxed">
                  {horaryResult.explanation?.summary_ta || horaryResult.explanation?.summary_en}
                </p>

                {/* Sub-Lord & Timing Indicators */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-3 border-t border-black/5 text-[11px]">
                  <div className="p-2 rounded-lg bg-white/70">
                    <span className="text-slate-400 block">{isTa ? "உப-அதிபதி" : "Sub-Lord"}</span>
                    <span className="font-bold text-slate-800">{horaryResult.cusp_sub_lord}</span>
                  </div>
                  <div className="p-2 rounded-lg bg-white/70">
                    <span className="text-slate-400 block">{isTa ? "நட்சத்திர நாதன்" : "Star Lord"}</span>
                    <span className="font-bold text-slate-800">{horaryResult.cusp_star_lord}</span>
                  </div>
                  <div className="p-2 rounded-lg bg-white/70">
                    <span className="text-slate-400 block">{isTa ? "ஆளும் கிரகங்கள்" : "Ruling Planets"}</span>
                    <span className="font-bold text-slate-800">
                      {horaryResult.ruling_planets ? horaryResult.ruling_planets.slice(0, 3).join(", ") : "Aligned"}
                    </span>
                  </div>
                  <div className="p-2 rounded-lg bg-white/70">
                    <span className="text-slate-400 block">{isTa ? "நிகழும் காலம்" : "Timing"}</span>
                    <span className="font-bold text-emerald-800">
                      {horaryResult.timing ? `${horaryResult.timing.start_date} ~ ${horaryResult.timing.end_date}` : "Active Month"}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default function MasterPredictionPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-[calc(100vh-14rem)] flex items-center justify-center bg-[#F2F3F5]">
          <div className="w-8 h-8 border-4 border-[#153F6B] border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <MasterPredictionContent />
    </Suspense>
  );
}
