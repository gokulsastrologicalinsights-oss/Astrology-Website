"use client";

import React, { useState, useEffect, useMemo, useRef, useCallback } from "react";
import {
  HoroscopeResponse,
  DasaResponse,
  KpResponse,
  LiveTransitsResponse,
  PlanetInfo,
  DasaPeriodNode,
} from "@/lib/types";
import { useLanguage } from "@/lib/i18n";
import {
  getRasiName,
  getGrahaName,
  getGrahaShort,
  getNakshatraName,
  getLordName,
} from "@/lib/translations";
import { formatBirthDate, formatBirthTime, formatDms } from "@/lib/formatters";
import { SouthIndianChart } from "@/components/charts/SouthIndianChart";
import { NorthIndianChart } from "@/components/charts/NorthIndianChart";
import { getGrahaDignity } from "@/lib/dignity";
import {
  findActiveHierarchy,
  jdToCalendarDateTime,
  VIMSHOTTARI_YEARS,
} from "@/lib/dasa-helpers";
import {
  buildPlanetContexts,
  calculateBenefitBhavas,
  PlanetContext,
  SIGN_LORDS,
  SIGNS_RULED_BY,
} from "@/lib/benefit-bhavas";
import {
  Clock,
  Play,
  Pause,
  RotateCcw,
  Sparkles,
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  Calendar,
  Compass,
  Copy,
  Check,
  Save,
  Printer,
  FileText,
  AlertTriangle,
  RefreshCw,
  Flame,
  Star,
  Activity,
  Layers,
  Award,
  Radio,
  Gem,
  Heart,
  ChevronRight,
  TrendingUp,
  MapPin,
  Maximize2,
  Minimize2,
} from "lucide-react";

interface AstrologerCockpitProps {
  horoscope: HoroscopeResponse;
  clientInputs: {
    fullName?: string;
    birthDate: string;
    birthTime: string;
    isTimeConfirmed?: boolean;
    locationName?: string;
    latitude?: number;
    longitude?: number;
    gender?: string;
    ayanamsaId?: number;
  };
  dasa?: DasaResponse;
  kp?: KpResponse;
  liveTransitsData?: LiveTransitsResponse | null;
  isLoadingTransits?: boolean;
  fetchLiveTransits?: () => void;
  consultationNotes: string;
  setConsultationNotes: (val: string) => void;
  handleSaveNotes: () => void;
  isSavingNotes: boolean;
  notesSaveStatus: string | null;
  idParam?: string | null;
  systemMode?: "vedic" | "kp";
  setSystemMode?: (mode: "vedic" | "kp") => void;
  chartMode: "south" | "north";
  setChartMode: (mode: "south" | "north") => void;
  d9Horoscope?: HoroscopeResponse | null;
  onNavigateTab?: (tab: string) => void;
}

// Julian Day helper
function dateToJd(isoDateStr: string): number {
  const [y, m, d] = isoDateStr.split("-").map(Number);
  const a = Math.floor((14 - m) / 12);
  const yAdjusted = y + 4800 - a;
  const mAdjusted = m + 12 * a - 3;
  return (
    d +
    Math.floor((153 * mAdjusted + 2) / 5) +
    365 * yAdjusted +
    Math.floor(yAdjusted / 4) -
    Math.floor(yAdjusted / 100) +
    Math.floor(yAdjusted / 400) -
    32045 +
    0.5
  );
}

// Classical deity and remedy affiliations
const PLANETARY_REMEDY_DATA: Record<
  string,
  {
    deityEn: string;
    deityTa: string;
    mantraEn: string;
    mantraTa: string;
    templeEn: string;
    templeTa: string;
    gemEn: string;
    gemTa: string;
    metalEn: string;
    metalTa: string;
  }
> = {
  Sun: {
    deityEn: "Lord Shiva / Surya Narayana",
    deityTa: "சிவபெருமான் / சூரிய நாராயணர்",
    mantraEn: "Om Hram Hreem Hroum Sah Suryaya Namah (Aditya Hridaya Stotram)",
    mantraTa: "ஓம் ஹ்ராம் ஹ்ரீம் ஹ்ரௌம் ஸஹ சூர்யாய நமஹ (ஆதித்ய ஹ்ருதயம்)",
    templeEn: "Suryanar Kovil, Thanjavur (Navagraha Stalam)",
    templeTa: "சூரியனார் கோவில், தஞ்சாவூர் (நவகிரக தலம்)",
    gemEn: "Ruby (Manikkam)",
    gemTa: "மாணிக்கம்",
    metalEn: "Copper / Gold",
    metalTa: "செம்பு / தங்கம்",
  },
  Moon: {
    deityEn: "Goddess Parvati / Chandramouleeswara",
    deityTa: "அம்பாள் பார்வதி / சந்திரமௌலீஸ்வரர்",
    mantraEn: "Om Shram Shreem Shroum Sah Chandraya Namah",
    mantraTa: "ஓம் ச்ராம் ச்ரீம் ச்ரௌம் ஸஹ சந்த்ராய நமஹ",
    templeEn: "Thingalur Kailasanathar Temple, Thanjavur",
    templeTa: "திங்களூர் கைலாசநாதர் கோவில், தஞ்சாவூர்",
    gemEn: "Natural Pearl (Muthu)",
    gemTa: "இயற்கை முத்து",
    metalEn: "Silver",
    metalTa: "வெள்ளி",
  },
  Mars: {
    deityEn: "Lord Murugan / Subrahmanya Swamy",
    deityTa: "முருகப் பெருமான் / செவ்வாய் பகவான்",
    mantraEn: "Om Kram Kreem Kroum Sah Bhaumaya Namah (Kanda Sashti Kavasam)",
    mantraTa: "ஓம் க்ராம் க்ரீம் க்ரௌம் ஸஹ பௌமாய நமஹ (கந்த சஷ்டி கவசம்)",
    templeEn: "Vaitheeswaran Koil, Mayiladuthurai",
    templeTa: "வைத்தீஸ்வரன் கோவில் (செவ்வாய் தலம்), மயிலாடுதுறை",
    gemEn: "Red Coral (Pavazham)",
    gemTa: "சிவப்பு பவளம்",
    metalEn: "Copper / Brass",
    metalTa: "செம்பு / பித்தளை",
  },
  Mercury: {
    deityEn: "Lord Maha Vishnu / Sri Venkatachalapathi",
    deityTa: "மகா விஷ்ணு / திருப்பதி வெங்கடாசலபதி",
    mantraEn: "Om Bram Breem Broum Sah Budhaya Namah (Vishnu Sahasranamam)",
    mantraTa: "ஓம் ப்ராம் ப்ரீம் ப்ரௌம் ஸஹ புதாய நமஹ (விஷ்ணு சகஸ்ரநாமம்)",
    templeEn: "Thiruvenkadu Swetharanyeswarar Temple, Nagapattinam",
    templeTa: "திருவெண்காடு சுவேதாரண்யேஸ்வரர் கோவில்",
    gemEn: "Emerald (Maragatham)",
    gemTa: "மரகதம் (பச்சை)",
    metalEn: "Bronze / Brass",
    metalTa: "வெண்கலம் / பித்தளை",
  },
  Jupiter: {
    deityEn: "Lord Dakshinamurthy / Brihaspati",
    deityTa: "மேதா தட்சிணாமூர்த்தி / குரு பகவான்",
    mantraEn: "Om Gram Greem Groum Sah Gurave Namah (Guru Gayatri)",
    mantraTa: "ஓம் க்ராம் க்ரீம் க்ரௌம் ஸஹ குரவே நமஹ (குரு காயத்ரி)",
    templeEn: "Alangudi Apatsahayeswarar Temple, Kumbakonam",
    templeTa: "ஆலங்குடி ஆபத்சகாயேஸ்வரர் கோவில், கும்பகோணம்",
    gemEn: "Yellow Sapphire (Pushparagam)",
    gemTa: "மஞ்சள் புஷ்பராகம்",
    metalEn: "Gold / Brass",
    metalTa: "தங்கம் / பித்தளை",
  },
  Venus: {
    deityEn: "Goddess Mahalakshmi / Sri Ranganathar",
    deityTa: "ஸ்ரீ மகாலட்சுமி / ஸ்ரீ ரங்கநாதர்",
    mantraEn: "Om Dram Dreem Droum Sah Shukraya Namah (Kanakadhara Stotram)",
    mantraTa: "ஓம் த்ராம் த்ரீம் த்ரௌம் ஸஹ சுக்ராய நமஹ (கனகதாரா ஸ்தோத்திரம்)",
    templeEn: "Kanjanur Agneeswarar Temple, Kumbakonam",
    templeTa: "கஞ்சனூர் அக்னீஸ்வரர் கோவில், கும்பகோணம்",
    gemEn: "Diamond (Vairam) or White Zircon",
    gemTa: "வைரம் அல்லது வெள்ளிக் கற்கள்",
    metalEn: "Silver / White Gold",
    metalTa: "வெள்ளி",
  },
  Saturn: {
    deityEn: "Lord Sastha / Hanuman / Thirunallar Saneeswara",
    deityTa: "ஸ்ரீ தர்ம சாஸ்தா / அனுமன் / சனீஸ்வர பகவான்",
    mantraEn: "Om Pram Preem Proum Sah Shanaischaraya Namah (Hanuman Chalisa)",
    mantraTa: "ஓம் ப்ராம் ப்ரீம் ப்ரௌம் ஸஹ சனைச்சராய நமஹ (அனுமன் சாலிசா)",
    templeEn: "Thirunallar Dharbaranyeswarar Temple, Karaikal",
    templeTa: "திருநள்ளாறு தர்பாரண்யேஸ்வரர் கோவில், காரைக்கால்",
    gemEn: "Blue Sapphire (Neelam) or Amethyst",
    gemTa: "நீலக்கல் அல்லது அமேதிஸ்ட்",
    metalEn: "Iron / Panchaloha",
    metalTa: "இரும்பு / ஐம்பொன்",
  },
  Rahu: {
    deityEn: "Goddess Durga Devi / Rahu Bhagavan",
    deityTa: "துர்க்கை அம்மன் / ராகு பகவான்",
    mantraEn: "Om Bhram Bhreem Bhroum Sah Rahave Namah (Durga Suktam)",
    mantraTa: "ஓம் ப்ராம் ப்ரீம் ப்ரௌம் ஸஹ ராகவே நமஹ (துர்க்கா சூக்தம்)",
    templeEn: "Thirunageswaram Naganathaswamy Temple, Kumbakonam",
    templeTa: "திருநாகேஸ்வரம் நாகநாதசுவாமி கோவில், கும்பகோணம்",
    gemEn: "Hessonite Garnet (Gomedhakam)",
    gemTa: "கோமேதகம்",
    metalEn: "Lead / Silver",
    metalTa: "ஈயம் / வெள்ளி",
  },
  Ketu: {
    deityEn: "Lord Vigneshwara (Ganesha) / Chitragupta",
    deityTa: "விக்னேஸ்வரர் (விநாயகர்) / கேது பகவான்",
    mantraEn: "Om Sram Sreem Sroum Sah Ketave Namah (Ganesha Atharvashirsha)",
    mantraTa: "ஓம் ச்ராம் ச்ரீம் ச்ரௌம் ஸஹ கேதவே நமஹ (விநாயகர் கவசம்)",
    templeEn: "Keezhperumpallam Naganathar Temple, Poompuhar",
    templeTa: "கீழ்ப்பெரும்பள்ளம் நாகநாதர் கோவில், பூம்புகார்",
    gemEn: "Cat's Eye (Vaidooryam)",
    gemTa: "வைடூரியம்",
    metalEn: "Panchaloha / Copper",
    metalTa: "ஐம்பொன்",
  },
};

export function AstrologerCockpit({
  horoscope,
  clientInputs,
  dasa,
  kp,
  liveTransitsData,
  isLoadingTransits,
  fetchLiveTransits,
  consultationNotes,
  setConsultationNotes,
  handleSaveNotes,
  isSavingNotes,
  notesSaveStatus,
  idParam,
  systemMode = "vedic",
  setSystemMode,
  chartMode,
  setChartMode,
  d9Horoscope,
  onNavigateTab,
}: AstrologerCockpitProps) {
  const { language } = useLanguage();

  // Consultation Stopwatch state
  const [stopwatchSeconds, setStopwatchSeconds] = useState<number>(0);
  const [isTimerRunning, setIsTimerRunning] = useState<boolean>(true);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (isTimerRunning) {
      timerRef.current = setInterval(() => {
        setStopwatchSeconds((prev) => prev + 1);
      }, 1000);
    } else if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isTimerRunning]);

  const formatTimer = (totalSeconds: number) => {
    const hrs = Math.floor(totalSeconds / 3600);
    const mins = Math.floor((totalSeconds % 3600) / 60);
    const secs = totalSeconds % 60;
    if (hrs > 0) {
      return `${hrs.toString().padStart(2, "0")}:${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
    }
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const handleResetTimer = () => {
    setStopwatchSeconds(0);
    setIsTimerRunning(false);
  };

  // Dual Chart View Configuration
  // "d1_d9" = Rasi + Navamsa | "d1_transits" = Rasi + Live Transits
  const [dualViewMode, setDualViewMode] = useState<"d1_d9" | "d1_transits">("d1_d9");

  // Time Machine date selection (defaults to today)
  const todayIso = useMemo(() => new Date().toISOString().split("T")[0], []);
  const [activeDate, setActiveDate] = useState<string>(todayIso);

  // Auto-fetch transits if not loaded
  useEffect(() => {
    if (!liveTransitsData && !isLoadingTransits && fetchLiveTransits) {
      fetchLiveTransits();
    }
  }, [liveTransitsData, isLoadingTransits, fetchLiveTransits]);

  // Derived Client Age
  const clientAge = useMemo(() => {
    if (!clientInputs.birthDate) return null;
    const [by, bm, bd] = clientInputs.birthDate.split("-").map(Number);
    const [ty, tm, td] = activeDate.split("-").map(Number);
    let years = ty - by;
    let months = tm - bm;
    let days = td - bd;
    if (days < 0) {
      months -= 1;
      days += 30;
    }
    if (months < 0) {
      years -= 1;
      months += 12;
    }
    return { years, months, days };
  }, [clientInputs.birthDate, activeDate]);

  // Planet Contexts & Functional House Significations
  const planetContexts = useMemo(() => {
    if (!horoscope) return null;
    return buildPlanetContexts(horoscope.planets, horoscope.ascendant, horoscope.houses);
  }, [horoscope]);

  // Active Dasa Hierarchy Calculation
  const activeHierarchy = useMemo(() => {
    if (!dasa?.dasa_tree || dasa.dasa_tree.length === 0 || !activeDate) return null;
    const tJd = dateToJd(activeDate);
    const tzHours = (horoscope.metadata?.coordinates?.longitude || 80.2707) / 15.0;
    return findActiveHierarchy(
      dasa.dasa_tree,
      tJd,
      tzHours,
      clientInputs.birthDate
    );
  }, [dasa, activeDate, horoscope.metadata, clientInputs.birthDate]);

  // Active Mahadasha & Antardasha Progress Metrics
  const dasaProgress = useMemo(() => {
    if (!activeHierarchy?.antardasha) return null;
    const currentJd = dateToJd(activeDate);
    const startJd = activeHierarchy.antardasha.start_jd;
    const endJd = activeHierarchy.antardasha.end_jd;
    const totalDays = Math.max(1, endJd - startJd);
    const elapsedDays = Math.max(0, Math.min(totalDays, currentJd - startJd));
    const percentage = Math.round((elapsedDays / totalDays) * 100);
    const remainingDays = Math.max(0, Math.round(endJd - currentJd));
    return {
      percentage,
      remainingDays,
      totalDays: Math.round(totalDays),
    };
  }, [activeHierarchy, activeDate]);

  // Next Upcoming Bhukti
  const nextBhukti = useMemo(() => {
    if (!dasa?.dasa_tree || !activeHierarchy?.mahadasha || !activeHierarchy?.antardasha) return null;
    const currentMaha = dasa.dasa_tree.find(
      (m) => m.lord === activeHierarchy.mahadasha?.lord
    );
    if (!currentMaha?.sub_periods) return null;
    const curIdx = currentMaha.sub_periods.findIndex(
      (b: DasaPeriodNode) => b.lord === activeHierarchy.antardasha?.lord
    );
    if (curIdx >= 0 && curIdx < currentMaha.sub_periods.length - 1) {
      return currentMaha.sub_periods[curIdx + 1];
    }
    // Else next Mahadasha's first Bhukti
    const mahaIdx = dasa.dasa_tree.findIndex((m) => m.lord === currentMaha.lord);
    if (mahaIdx >= 0 && mahaIdx < dasa.dasa_tree.length - 1) {
      const nextM = dasa.dasa_tree[mahaIdx + 1];
      if (nextM.sub_periods && nextM.sub_periods.length > 0) {
        return nextM.sub_periods[0];
      }
    }
    return null;
  }, [dasa, activeHierarchy]);

  // Planetary Strengths, Dignities & Vargottama Evaluation
  const planetaryMatrix = useMemo(() => {
    if (!horoscope?.planets) return [];
    const lagnaSign = horoscope.ascendant.sign_index;
    const moon = horoscope.planets.find((p) => p.name === "Moon");
    const moonSign = moon ? moon.sign_index : lagnaSign;

    return horoscope.planets.map((planet) => {
      const houseFromLagna = ((planet.sign_index - lagnaSign + 12) % 12) + 1;
      const houseFromMoon = ((planet.sign_index - moonSign + 12) % 12) + 1;
      const dignity = getGrahaDignity(
        planet.name,
        planet.sign_index,
        planet.degree_in_sign,
        houseFromLagna
      );

      // Check Vargottama (same sign in D1 and D9)
      const d9Planet = d9Horoscope?.planets.find((dp) => dp.name === planet.name);
      const isVargottama = d9Planet && d9Planet.sign_index === planet.sign_index;

      // Shadbala lookup
      const shadbalaInfo = (horoscope as any).shadbala?.planets?.find(
        (sp: any) => sp.planet?.toLowerCase() === planet.name.toLowerCase()
      );

      // Benefit Bhavas context
      const ctx = planetContexts?.[planet.name];

      return {
        ...planet,
        houseFromLagna,
        houseFromMoon,
        dignity,
        isVargottama,
        shadbalaInfo,
        ctx,
      };
    });
  }, [horoscope, d9Horoscope, planetContexts]);

  // Gochara (Transit) Radar: Saturn & Jupiter relative to Natal Moon
  const gocharaRadar = useMemo(() => {
    const moon = horoscope.planets.find((p) => p.name === "Moon");
    if (!moon || !liveTransitsData?.planets) return null;

    const moonSign = moon.sign_index;
    const transitSaturn = liveTransitsData.planets.find((p) => p.name === "Saturn");
    const transitJupiter = liveTransitsData.planets.find((p) => p.name === "Jupiter");
    const transitRahu = liveTransitsData.planets.find((p) => p.name === "Rahu");
    const transitKetu = liveTransitsData.planets.find((p) => p.name === "Ketu");

    let saturnTransitTitleEn = "Favorable Transit (Subha Gochara)";
    let saturnTransitTitleTa = "சுப கோசாரம் (நன்மை)";
    let saturnBadgeColor = "bg-emerald-50 text-emerald-800 border-emerald-200";

    let saturnDiff = 0;
    if (transitSaturn) {
      saturnDiff = ((transitSaturn.sign_index - moonSign + 12) % 12) + 1;
      if (saturnDiff === 12) {
        saturnTransitTitleEn = "Sade Sati - 1st Phase (Viraya Sani)";
        saturnTransitTitleTa = "ஏழரைச் சனி - விரையச் சனி (1-ம் சுற்று)";
        saturnBadgeColor = "bg-amber-50 text-amber-800 border-amber-200";
      } else if (saturnDiff === 1) {
        saturnTransitTitleEn = "Sade Sati - Peak Phase (Janma Sani)";
        saturnTransitTitleTa = "ஏழரைச் சனி - ஜென்மச் சனி (உச்ச தாக்கம்)";
        saturnBadgeColor = "bg-rose-50 text-rose-800 border-rose-300";
      } else if (saturnDiff === 2) {
        saturnTransitTitleEn = "Sade Sati - Final Phase (Paadha Sani)";
        saturnTransitTitleTa = "ஏழரைச் சனி - பாதச் சனி (முடிவுக்கட்டம்)";
        saturnBadgeColor = "bg-amber-50 text-amber-800 border-amber-200";
      } else if (saturnDiff === 8) {
        saturnTransitTitleEn = "Ashtama Shani (Major Transformation)";
        saturnTransitTitleTa = "அஷ்டமச் சனி (கவனம் மற்றும் விழிப்புணர்வு)";
        saturnBadgeColor = "bg-red-50 text-red-800 border-red-300";
      } else if (saturnDiff === 4) {
        saturnTransitTitleEn = "Ardhashtama Shani (4th House Transit)";
        saturnTransitTitleTa = "அர்த்தாஷ்டமச் சனி (4-ம் இடச் சனி)";
        saturnBadgeColor = "bg-orange-50 text-orange-800 border-orange-200";
      } else if ([3, 6, 11].includes(saturnDiff)) {
        saturnTransitTitleEn = `Upachaya Shani in House ${saturnDiff} (Victor / Gains)`;
        saturnTransitTitleTa = `${saturnDiff}-ம் இடத்து உபஜெயச் சனி (வெற்றி & தனலாபம்)`;
        saturnBadgeColor = "bg-emerald-50 text-emerald-800 border-emerald-200";
      } else {
        saturnTransitTitleEn = `Shani in House ${saturnDiff} from Moon`;
        saturnTransitTitleTa = `சந்திரனிலிருந்து ${saturnDiff}-ம் வீட்டில் சனி`;
        saturnBadgeColor = "bg-slate-50 text-slate-700 border-slate-200";
      }
    }

    let jupiterTransitTitleEn = "Internal Growth Period";
    let jupiterTransitTitleTa = "சுய விழிப்புணர்வு காலம்";
    let isGuruBalam = false;
    let jupiterDiff = 0;
    if (transitJupiter) {
      jupiterDiff = ((transitJupiter.sign_index - moonSign + 12) % 12) + 1;
      if ([2, 5, 7, 9, 11].includes(jupiterDiff)) {
        isGuruBalam = true;
        jupiterTransitTitleEn = `Guru Balan Active (${jupiterDiff}th from Moon - Auspicious)`;
        jupiterTransitTitleTa = `குரு பலம் உண்டு (${jupiterDiff}-ம் இடத்து சுப குரு)`;
      } else {
        jupiterTransitTitleEn = `Jupiter in House ${jupiterDiff} from Moon`;
        jupiterTransitTitleTa = `சந்திரனிலிருந்து ${jupiterDiff}-ம் வீட்டில் குரு`;
      }
    }

    return {
      saturnDiff,
      saturnTransitTitleEn,
      saturnTransitTitleTa,
      saturnBadgeColor,
      jupiterDiff,
      isGuruBalam,
      jupiterTransitTitleEn,
      jupiterTransitTitleTa,
      transitSaturn,
      transitJupiter,
      transitRahu,
      transitKetu,
    };
  }, [horoscope, liveTransitsData]);

  // Sarvashtakavarga (SAV) points mapping by house
  const savByHouse = useMemo(() => {
    const bindus = horoscope.ashtakavarga?.sarvashtakavarga?.house_bindus;
    if (!bindus) return null;
    const res: Record<number, number> = {};
    for (let h = 1; h <= 12; h++) {
      res[h] = bindus[h.toString()] ?? bindus[`H${h}`] ?? 28;
    }
    return res;
  }, [horoscope.ashtakavarga]);

  // Active Dasa Lords' live transits
  const dasaLordsTransits = useMemo(() => {
    if (!liveTransitsData?.planets) return null;
    const mahaLord = activeHierarchy?.mahadasha?.lord;
    const bhuktiLord = activeHierarchy?.antardasha?.lord;
    const tMaha = liveTransitsData.planets.find(
      (p) => p.name.toLowerCase() === mahaLord?.toLowerCase()
    );
    const tBhukti = liveTransitsData.planets.find(
      (p) => p.name.toLowerCase() === bhuktiLord?.toLowerCase()
    );
    return { tMaha, tBhukti, mahaLord, bhuktiLord };
  }, [activeHierarchy, liveTransitsData]);

  // Consultation Topics Checklist State
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const toggleTopic = (topic: string) => {
    setSelectedTopics((prev) =>
      prev.includes(topic) ? prev.filter((t) => t !== topic) : [...prev, topic]
    );
  };

  const consultationTopics = [
    { id: "career", labelEn: "Career & Job (10H)", labelTa: "தொழில் & வேலை (10-ம் இடம்)" },
    { id: "marriage", labelEn: "Marriage & Love (7H)", labelTa: "திருமணம் & தாம்பத்யம் (7-ம் இடம்)" },
    { id: "finance", labelEn: "Wealth & Finance (2H/11H)", labelTa: "தன லாபம் & பொருளாதாரம் (2/11)" },
    { id: "health", labelEn: "Health & Vitality (1H/6H)", labelTa: "உடல் நலம் & ஆயுள் (1/6)" },
    { id: "children", labelEn: "Children / Progeny (5H)", labelTa: "புத்திர பாக்கியம் (5-ம் இடம்)" },
    { id: "foreign", labelEn: "Foreign Travel (9H/12H)", labelTa: "வெளிநாட்டு பயணம் (9/12)" },
    { id: "legal", labelEn: "Litigation & Property (4H/6H)", labelTa: "நிலம் & வழக்குகள் (4/6)" },
  ];

  // Quick Snippet Inserters into Astrologer Notes
  const handleInsertSnippet = (snippetText: string) => {
    const updated = consultationNotes
      ? `${consultationNotes}\n\n${snippetText}`
      : snippetText;
    setConsultationNotes(updated);
  };

  // WhatsApp / Client Takeaways Formatter & Copy
  const [copiedTakeaways, setCopiedTakeaways] = useState<boolean>(false);
  const handleCopyClientTakeaways = () => {
    const clientName = clientInputs.fullName || (language === "ta" ? "அன்பார்ந்த வாடிக்கையாளர்" : "Valued Client");
    const lagnaStr = `${horoscope.ascendant.sign_name_tamil || horoscope.ascendant.sign_name} லக்னம் (${formatDms(horoscope.ascendant.degree_in_sign)})`;
    const moon = horoscope.planets.find((p) => p.name === "Moon");
    const rasiStr = moon
      ? `${moon.sign_name_tamil || moon.sign_name} ராசி, ${getNakshatraName(moon.nakshatra?.name || "", language === "ta" ? "ta" : "en")} பாதம் ${moon.nakshatra?.pada || 1}`
      : "-";

    const mahaLord = activeHierarchy?.mahadasha?.lord
      ? getGrahaName(activeHierarchy.mahadasha.lord, language === "ta" ? "ta" : "en")
      : "-";
    const bhuktiLord = activeHierarchy?.antardasha?.lord
      ? getGrahaName(activeHierarchy.antardasha.lord, language === "ta" ? "ta" : "en")
      : "-";

    const saturnStatus = language === "ta"
      ? gocharaRadar?.saturnTransitTitleTa || "-"
      : gocharaRadar?.saturnTransitTitleEn || "-";

    const guruStatus = language === "ta"
      ? gocharaRadar?.jupiterTransitTitleTa || "-"
      : gocharaRadar?.jupiterTransitTitleEn || "-";

    const remedyData = activeHierarchy?.mahadasha?.lord
      ? PLANETARY_REMEDY_DATA[activeHierarchy.mahadasha.lord]
      : null;

    let text = "";
    if (language === "ta") {
      text = `🌟 *ஜோதிட ஆலோசனைச் சுருக்கம் (Consultation Summary)* 🌟\n\n` +
        `👤 *வாடிக்கையாளர்:* ${clientName}\n` +
        `🪐 *அடிப்படை அமைப்புகள்:* ${lagnaStr} | ${rasiStr}\n\n` +
        `⏳ *நடப்பு தசா - புக்தி:* ${mahaLord} மகா தசா - ${bhuktiLord} புக்தி\n` +
        `🪐 *முக்கிய கோசார நிலவரம்:* ${saturnStatus} | ${guruStatus}\n\n` +
        `📋 *ஆலோசனை முக்கிய குறிப்புகள்:*\n${consultationNotes ? consultationNotes : "ஆலோசனை நிறைவடைந்தது."}\n\n` +
        (remedyData
          ? `🪔 *பரிந்துரைக்கப்பட்ட பரிகாரங்கள்:*\n` +
            `• தெய்வம்: ${remedyData.deityTa}\n` +
            `• மந்திரம்: ${remedyData.mantraTa}\n` +
            `• பரிகாரத் தலம்: ${remedyData.templeTa}\n` +
            `• ரத்தினம்: ${remedyData.gemTa}\n\n`
          : "") +
        `நன்றி! வாழ்க வளமுடன். 🙏`;
    } else {
      text = `🌟 *Astrological Consultation Takeaways* 🌟\n\n` +
        `👤 *Client:* ${clientName}\n` +
        `🪐 *Core Blueprint:* ${horoscope.ascendant.sign_name} Ascendant | ${moon?.sign_name || "-"} Moon Sign (${moon?.nakshatra?.name || "-"} P-${moon?.nakshatra?.pada || 1})\n\n` +
        `⏳ *Running Period:* ${mahaLord} Mahadasha - ${bhuktiLord} Bhukti\n` +
        `🪐 *Major Transits:* ${saturnStatus} | ${guruStatus}\n\n` +
        `📋 *Consultation Insights & Action Points:*\n${consultationNotes ? consultationNotes : "Consultation completed successfully."}\n\n` +
        (remedyData
          ? `🪔 *Prescribed Remedies:*\n` +
            `• Presiding Deity: ${remedyData.deityEn}\n` +
            `• Sacred Mantra: ${remedyData.mantraEn}\n` +
            `• Pilgrimage Temple: ${remedyData.templeEn}\n` +
            `• Auspicious Gemstone: ${remedyData.gemEn}\n\n`
          : "") +
        `Wishing you divine peace, prosperity, and success! 🙏`;
    }

    navigator.clipboard.writeText(text);
    setCopiedTakeaways(true);
    setTimeout(() => setCopiedTakeaways(false), 3000);
  };

  // Print Cockpit View
  const handlePrintCockpit = () => {
    window.print();
  };

  // Primary active Dasa Lord Remedy
  const activeRemedy = activeHierarchy?.mahadasha?.lord
    ? PLANETARY_REMEDY_DATA[activeHierarchy.mahadasha.lord]
    : null;

  return (
    <div className="space-y-4 print:space-y-2">
      {/* 1. HUD COMMAND BAR: CLIENT IDENTITY + STOPWATCH + CONTROLS */}
      <div className="bg-white rounded-2xl border border-[#D9DEE7] p-4 sm:p-5 shadow-xs">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 border-b border-[#F2F3F5] pb-4">
          {/* Client Bio & Identity Badges */}
          <div className="space-y-1.5">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-black uppercase tracking-wider px-2 py-0.5 rounded-md bg-[#153F6B] text-white">
                {language === "ta" ? "ஜோதிடர் காக்பிட்" : "Astrologer Cockpit"}
              </span>
              <h2 className="text-xl sm:text-2xl font-black text-[#183047] tracking-tight">
                {clientInputs.fullName || (language === "ta" ? "பெயர் குறிப்பிடப்படவில்லை" : "Unnamed Client")}
              </h2>
              {clientInputs.gender && (
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-[#F2F3F5] text-[#52667E] border border-[#D9DEE7]">
                  {clientInputs.gender === "female"
                    ? language === "ta" ? "பெண்" : "Female"
                    : clientInputs.gender === "male"
                    ? language === "ta" ? "ஆண்" : "Male"
                    : clientInputs.gender}
                </span>
              )}
              {clientAge && (
                <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
                  {clientAge.years} {language === "ta" ? "ஆண்டுகள்" : "yrs"} {clientAge.months} {language === "ta" ? "மாதங்கள்" : "mos"}
                </span>
              )}
            </div>

            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-[#52667E]">
              <span className="inline-flex items-center gap-1 font-medium">
                <Calendar className="w-3.5 h-3.5 text-[#B4872B]" />
                {formatBirthDate(clientInputs.birthDate, language)}
              </span>
              <span className="inline-flex items-center gap-1 font-medium">
                <Clock className="w-3.5 h-3.5 text-[#B4872B]" />
                {formatBirthTime(clientInputs.birthTime)}
              </span>
              {clientInputs.locationName && (
                <span className="inline-flex items-center gap-1 font-medium truncate max-w-xs">
                  <MapPin className="w-3.5 h-3.5 text-[#B4872B]" />
                  {clientInputs.locationName}
                </span>
              )}
              <span className="text-[11px] text-[#8190A6]">
                {horoscope.metadata?.ayanamsa_name || "Lahiri"} Ayanamsa
              </span>
            </div>
          </div>

          {/* Consultation Timer & Real-time Action Buttons */}
          <div className="flex flex-wrap items-center gap-2.5">
            {/* Live Consultation Stopwatch */}
            <div className="flex items-center gap-2 bg-[#F2F3F5]/60 border border-[#D9DEE7] px-3 py-1.5 rounded-xl">
              <Clock
                className={`w-4 h-4 ${
                  stopwatchSeconds > 2700
                    ? "text-rose-600 animate-pulse"
                    : stopwatchSeconds > 1800
                    ? "text-amber-600"
                    : "text-[#153F6B]"
                }`}
              />
              <div className="flex flex-col">
                <span className="text-[9px] font-bold uppercase tracking-wider text-[#8190A6]">
                  {language === "ta" ? "ஆலோசனை நேரம்" : "Call Timer"}
                </span>
                <span
                  className={`text-sm font-black font-mono tracking-wider ${
                    stopwatchSeconds > 2700
                      ? "text-rose-600"
                      : stopwatchSeconds > 1800
                      ? "text-amber-600"
                      : "text-[#183047]"
                  }`}
                >
                  {formatTimer(stopwatchSeconds)}
                </span>
              </div>
              <div className="flex items-center gap-1 ml-1">
                <button
                  type="button"
                  onClick={() => setIsTimerRunning(!isTimerRunning)}
                  title={isTimerRunning ? "Pause timer" : "Resume timer"}
                  className="p-1 rounded-md hover:bg-white text-[#52667E] hover:text-[#153F6B] transition-colors"
                >
                  {isTimerRunning ? (
                    <Pause className="w-3.5 h-3.5" />
                  ) : (
                    <Play className="w-3.5 h-3.5 text-emerald-600" />
                  )}
                </button>
                <button
                  type="button"
                  onClick={handleResetTimer}
                  title="Reset timer"
                  className="p-1 rounded-md hover:bg-white text-[#52667E] hover:text-[#153F6B] transition-colors"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            {/* Chart Style Switcher (South / North) */}
            <div className="inline-flex rounded-xl bg-[#F2F3F5] p-1 border border-[#D9DEE7]">
              <button
                type="button"
                onClick={() => setChartMode("south")}
                className={`px-3 py-1 text-xs font-bold rounded-lg transition-all cursor-pointer ${
                  chartMode === "south"
                    ? "bg-[#153F6B] text-white shadow-2xs"
                    : "text-[#52667E] hover:text-[#153F6B]"
                }`}
              >
                {language === "ta" ? "தெற்கு" : "South"}
              </button>
              <button
                type="button"
                onClick={() => setChartMode("north")}
                className={`px-3 py-1 text-xs font-bold rounded-lg transition-all cursor-pointer ${
                  chartMode === "north"
                    ? "bg-[#153F6B] text-white shadow-2xs"
                    : "text-[#52667E] hover:text-[#153F6B]"
                }`}
              >
                {language === "ta" ? "வடக்கு" : "North"}
              </button>
            </div>

            {/* WhatsApp Takeaways Copy */}
            <button
              type="button"
              onClick={handleCopyClientTakeaways}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-2xs transition-all cursor-pointer"
              title="Copy consultation takeaways to paste in WhatsApp"
            >
              {copiedTakeaways ? (
                <>
                  <Check className="w-3.5 h-3.5" />
                  <span>{language === "ta" ? "நகலெடுக்கப்பட்டது!" : "Copied!"}</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>{language === "ta" ? "வாட்ஸ்அப் சுருக்கம்" : "Copy WhatsApp"}</span>
                </>
              )}
            </button>

            {/* Print Sheet */}
            <button
              type="button"
              onClick={handlePrintCockpit}
              className="inline-flex items-center gap-1 px-3 py-2 rounded-xl bg-white hover:bg-[#F2F3F5] border border-[#D9DEE7] text-[#183047] text-xs font-bold transition-all cursor-pointer"
              title="Print single-sheet consultation report"
            >
              <Printer className="w-3.5 h-3.5 text-[#52667E]" />
              <span className="hidden sm:inline">{language === "ta" ? "அச்சிடுக" : "Print"}</span>
            </button>
          </div>
        </div>

        {/* Essential Astrological Pillars Strip (Lagna, Rasi, Nakshatra, Sun, Tithi) */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 pt-3.5">
          {/* 1. Lagna */}
          <div className="p-2.5 rounded-xl bg-[#F2F3F5]/60 border border-[#D9DEE7] flex flex-col justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider text-[#8190A6]">
              {language === "ta" ? "லக்னம் (Ascendant)" : "Ascendant (Lagna)"}
            </span>
            <div className="font-bold text-xs sm:text-sm text-[#153F6B] truncate">
              {horoscope.ascendant.sign_name_tamil || horoscope.ascendant.sign_name}
            </div>
            <span className="text-[10px] font-mono text-[#52667E]">
              {formatDms(horoscope.ascendant.degree_in_sign)} • {getNakshatraName(horoscope.ascendant.nakshatra?.name || "", language)}
            </span>
          </div>

          {/* 2. Janma Rasi (Moon) */}
          {(() => {
            const moon = horoscope.planets.find((p) => p.name === "Moon");
            return (
              <div className="p-2.5 rounded-xl bg-[#F2F3F5]/60 border border-[#D9DEE7] flex flex-col justify-between">
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#8190A6]">
                  {language === "ta" ? "ராசி (Moon Sign)" : "Moon Sign (Rasi)"}
                </span>
                <div className="font-bold text-xs sm:text-sm text-[#153F6B] truncate">
                  {moon?.sign_name_tamil || moon?.sign_name || "-"}
                </div>
                <span className="text-[10px] font-mono text-[#52667E]">
                  {moon ? formatDms(moon.degree_in_sign) : "-"}
                </span>
              </div>
            );
          })()}

          {/* 3. Janma Nakshatra & Pada */}
          {(() => {
            const moon = horoscope.planets.find((p) => p.name === "Moon");
            return (
              <div className="p-2.5 rounded-xl bg-[#F2F3F5]/60 border border-[#D9DEE7] flex flex-col justify-between">
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#8190A6]">
                  {language === "ta" ? "நட்சத்திரம் (Star)" : "Birth Star"}
                </span>
                <div className="font-bold text-xs sm:text-sm text-[#183047] truncate">
                  {moon?.nakshatra ? getNakshatraName(moon.nakshatra.name, language) : "-"}
                </div>
                <span className="text-[10px] font-semibold text-[#B4872B]">
                  {language === "ta" ? "பாதம்" : "Pada"} {moon?.nakshatra?.pada || 1} • {getLordName(moon?.nakshatra?.lord || "", language)}
                </span>
              </div>
            );
          })()}

          {/* 4. Sun Sign */}
          {(() => {
            const sun = horoscope.planets.find((p) => p.name === "Sun");
            return (
              <div className="p-2.5 rounded-xl bg-[#F2F3F5]/60 border border-[#D9DEE7] flex flex-col justify-between">
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#8190A6]">
                  {language === "ta" ? "சூரிய ராசி" : "Sun Sign"}
                </span>
                <div className="font-bold text-xs sm:text-sm text-[#183047] truncate">
                  {sun?.sign_name_tamil || sun?.sign_name || "-"}
                </div>
                <span className="text-[10px] font-mono text-[#52667E]">
                  {sun ? formatDms(sun.degree_in_sign) : "-"}
                </span>
              </div>
            );
          })()}

          {/* 5. Tithi & Yoga */}
          <div className="p-2.5 rounded-xl bg-[#F2F3F5]/60 border border-[#D9DEE7] flex flex-col justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider text-[#8190A6]">
              {language === "ta" ? "திதி & யோகம்" : "Tithi & Yoga"}
            </span>
            <div className="font-bold text-xs sm:text-sm text-[#183047] truncate">
              {horoscope.panchang?.tithi?.name || "Tithi"}
            </div>
            <span className="text-[10px] text-[#52667E] truncate">
              {horoscope.panchang?.yoga?.name || "-"}
            </span>
          </div>

          {/* 6. Current Gochara Moon */}
          {(() => {
            const tMoon = liveTransitsData?.planets?.find((p) => p.name === "Moon");
            return (
              <div className="p-2.5 rounded-xl bg-[#FAF2DE]/50 border border-[#B4872B]/30 flex flex-col justify-between">
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#B4872B] flex items-center gap-1">
                  <Radio className="w-3 h-3 text-[#B4872B] animate-pulse" />
                  {language === "ta" ? "இன்றைய சந்திரன்" : "Live Moon (Transit)"}
                </span>
                <div className="font-bold text-xs sm:text-sm text-[#183047] truncate">
                  {tMoon ? (language === "ta" ? tMoon.sign_name_tamil : tMoon.sign_name) : "Calculating..."}
                </div>
                <span className="text-[10px] text-[#52667E] truncate">
                  {tMoon?.nakshatra?.name || "-"} ({tMoon ? formatDms(tMoon.degree_in_sign) : "-"})
                </span>
              </div>
            );
          })()}
        </div>
      </div>

      {/* 2. DASA-BHUKTI COMMAND STRIP & TIME MACHINE */}
      <div className="bg-white rounded-2xl border border-[#D9DEE7] p-4 sm:p-5 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-[#F2F3F5] pb-3 mb-4">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-[#153F6B]/10 flex items-center justify-center text-[#153F6B]">
              <Compass className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-sm sm:text-base text-[#183047] flex items-center gap-2">
                <span>{language === "ta" ? "நடப்பு தசா-புக்தி கட்டளை மையம்" : "Dasa-Bhukti Command Center"}</span>
                {activeDate === todayIso ? (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                    {language === "ta" ? "இன்றைய நிலை" : "Live Today"}
                  </span>
                ) : (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-purple-100 text-purple-800">
                    {language === "ta" ? "தேர்ந்தெடுக்கப்பட்ட தேதி" : "Time Machine"}
                  </span>
                )}
              </h3>
            </div>
          </div>

          {/* Time Machine Quick Date Picker */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-[#52667E] hidden sm:inline">
              {language === "ta" ? "தேதி மாற்றி:" : "Date Anchor:"}
            </span>
            <input
              type="date"
              value={activeDate}
              onChange={(e) => setActiveDate(e.target.value)}
              className="text-xs px-2.5 py-1.5 rounded-lg border border-[#D9DEE7] bg-[#F2F3F5]/40 text-[#183047] font-semibold focus:outline-none focus:ring-1 focus:ring-[#153F6B]"
            />
            {activeDate !== todayIso && (
              <button
                type="button"
                onClick={() => setActiveDate(todayIso)}
                className="text-xs font-bold text-[#153F6B] hover:underline cursor-pointer"
              >
                {language === "ta" ? "இன்று" : "Today"}
              </button>
            )}
          </div>
        </div>

        {/* 4-Tier Hierarchy Cards */}
        {activeHierarchy?.mahadasha ? (
          <div className="space-y-3.5">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {/* Mahadasha */}
              <div className="p-3.5 rounded-xl bg-[#153F6B]/5 border border-[#153F6B]/20 relative overflow-hidden">
                <div className="flex items-center justify-between text-[11px] font-bold text-[#153F6B] uppercase mb-1">
                  <span>{language === "ta" ? "1. மகா தசா" : "1. Mahadasha"}</span>
                  <span className="font-mono text-[10px]">
                    {VIMSHOTTARI_YEARS[activeHierarchy.mahadasha.lord || ""] || 0} {language === "ta" ? "ஆண்டுகள்" : "yrs"}
                  </span>
                </div>
                <div className="text-base sm:text-lg font-black text-[#153F6B]">
                  {getGrahaName(activeHierarchy.mahadasha.lord || "", language)}
                </div>
                <div className="text-[11px] text-[#52667E] mt-1 flex items-center justify-between">
                  <span>{activeHierarchy.mahadasha.start_date_iso || "-"}</span>
                  <span>→</span>
                  <span>{activeHierarchy.mahadasha.end_date_iso || "-"}</span>
                </div>
                {/* Transit Position of Maha Lord */}
                {dasaLordsTransits?.tMaha && (
                  <div className="text-[10px] font-semibold text-[#B4872B] mt-2 pt-1 border-t border-[#D9DEE7]/50 flex items-center gap-1">
                    <Radio className="w-2.5 h-2.5 animate-pulse" />
                    <span>
                      {language === "ta" ? "கோசாரம்:" : "Transit:"} {language === "ta" ? dasaLordsTransits.tMaha.sign_name_tamil : dasaLordsTransits.tMaha.sign_name}
                    </span>
                  </div>
                )}
              </div>

              {/* Antardasha (Bhukti) with Progress Bar */}
              <div className="p-3.5 rounded-xl bg-[#B4872B]/10 border border-[#B4872B]/30 relative overflow-hidden">
                <div className="flex items-center justify-between text-[11px] font-bold text-[#8C6212] uppercase mb-1">
                  <span>{language === "ta" ? "2. அந்தர்தசா (புக்தி)" : "2. Antardasha (Bhukti)"}</span>
                  {dasaProgress && (
                    <span className="font-mono text-[10px] text-[#8C6212] font-bold">
                      {dasaProgress.percentage}% {language === "ta" ? "நிறைவு" : "done"}
                    </span>
                  )}
                </div>
                <div className="text-base sm:text-lg font-black text-[#8C6212]">
                  {getGrahaName(activeHierarchy.antardasha?.lord || "", language)}
                </div>
                <div className="text-[11px] text-[#52667E] mt-1 flex items-center justify-between">
                  <span>{activeHierarchy.antardasha?.start_date_iso || "-"}</span>
                  <span>→</span>
                  <span>{activeHierarchy.antardasha?.end_date_iso || "-"}</span>
                </div>

                {/* Progress bar */}
                {dasaProgress && (
                  <div className="w-full bg-[#D9DEE7] h-1.5 rounded-full mt-2.5 overflow-hidden">
                    <div
                      className="bg-[#B4872B] h-full rounded-full transition-all duration-500"
                      style={{ width: `${dasaProgress.percentage}%` }}
                    />
                  </div>
                )}

                {/* Days remaining */}
                {dasaProgress && (
                  <div className="text-[10px] text-[#8C6212] font-semibold mt-1.5 flex items-center justify-between">
                    <span>
                      {language === "ta" ? "மீதமுள்ளவை:" : "Remaining:"} {dasaProgress.remainingDays} {language === "ta" ? "நாட்கள்" : "days"}
                    </span>
                    {dasaLordsTransits?.tBhukti && (
                      <span className="text-[#52667E]">
                        {language === "ta" ? dasaLordsTransits.tBhukti.sign_name_tamil : dasaLordsTransits.tBhukti.sign_name}
                      </span>
                    )}
                  </div>
                )}
              </div>

              {/* Pratyantardasha (Antharam) */}
              <div className="p-3.5 rounded-xl bg-[#F2F3F5]/60 border border-[#D9DEE7]">
                <div className="text-[11px] font-bold text-[#52667E] uppercase mb-1">
                  {language === "ta" ? "3. பிரத்யந்தர்தசா" : "3. Pratyantardasha"}
                </div>
                <div className="text-base font-black text-[#183047]">
                  {activeHierarchy.pratyantardasha?.lord
                    ? getGrahaName(activeHierarchy.pratyantardasha.lord, language)
                    : "-"}
                </div>
                <div className="text-[11px] text-[#52667E] mt-1 flex items-center justify-between">
                  <span>{activeHierarchy.pratyantardasha?.start_date_iso || "-"}</span>
                  <span>→</span>
                  <span>{activeHierarchy.pratyantardasha?.end_date_iso || "-"}</span>
                </div>
              </div>

              {/* Sookshma Dasa */}
              <div className="p-3.5 rounded-xl bg-[#F2F3F5]/60 border border-[#D9DEE7]">
                <div className="text-[11px] font-bold text-[#52667E] uppercase mb-1">
                  {language === "ta" ? "4. சூட்சும தசா" : "4. Sookshmadasha"}
                </div>
                <div className="text-base font-black text-[#183047]">
                  {activeHierarchy.sookshmadasha?.lord
                    ? getGrahaName(activeHierarchy.sookshmadasha.lord, language)
                    : "-"}
                </div>
                <div className="text-[11px] text-[#52667E] mt-1 flex items-center justify-between">
                  <span>{activeHierarchy.sookshmadasha?.start_date_iso || "-"}</span>
                  <span>→</span>
                  <span>{activeHierarchy.sookshmadasha?.end_date_iso || "-"}</span>
                </div>
              </div>
            </div>

            {/* Next Upcoming Bhukti Alert */}
            {nextBhukti && (
              <div className="p-2.5 rounded-xl bg-purple-50/70 border border-purple-200 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-purple-700 shrink-0" />
                  <span className="font-semibold text-purple-900">
                    {language === "ta" ? "அடுத்த வரவிருக்கும் புக்தி:" : "Next Upcoming Bhukti:"}{" "}
                    <span className="font-black">
                      {getGrahaName(nextBhukti.lord || "", language)}
                    </span>{" "}
                    ({language === "ta" ? "தொடங்கும் தேதி:" : "Starts on:"}{" "}
                    <span className="font-mono">{nextBhukti.start_date_iso}</span>)
                  </span>
                </div>
                <span className="text-[11px] font-bold text-purple-700 bg-purple-100/80 px-2 py-0.5 rounded-md self-start sm:self-auto">
                  {nextBhukti.end_date_iso ? `${language === "ta" ? "முடிவு:" : "Until:"} ${nextBhukti.end_date_iso}` : ""}
                </span>
              </div>
            )}
          </div>
        ) : (
          <div className="text-xs text-[#8190A6] italic py-2">
            {language === "ta" ? "தசா தகவல்கள் கிடைக்கவில்லை." : "Dasa calculations not available."}
          </div>
        )}
      </div>

      {/* 3. DUAL SYNCHRONIZED CHARTS & SAV POINTS STRIP */}
      <div className="bg-white rounded-2xl border border-[#D9DEE7] p-4 sm:p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#F2F3F5] pb-3 mb-4">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-[#153F6B]/10 flex items-center justify-center text-[#153F6B]">
              <Layers className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-sm sm:text-base text-[#183047]">
                {language === "ta" ? "இரட்டைக் கட்டங்கள் (Dual Synchronized Charts)" : "Dual Synchronized Charts"}
              </h3>
              <p className="text-xs text-[#8190A6]">
                {language === "ta"
                  ? "ராசி (D1) உடன் நவாம்சம் (D9) அல்லது இன்றைய நேரலை கோசாரத்தை அருகருகே ஒப்பிடுக."
                  : "Compare Rasi (D1) with Navamsa (D9) or Live Transits (Gochara) side-by-side."}
              </p>
            </div>
          </div>

          {/* Dual Chart Toggle */}
          <div className="inline-flex rounded-xl bg-[#F2F3F5] p-1 border border-[#D9DEE7]">
            <button
              type="button"
              onClick={() => setDualViewMode("d1_d9")}
              className={`px-3 py-1.5 text-xs font-bold rounded-lg transition-all cursor-pointer ${
                dualViewMode === "d1_d9"
                  ? "bg-[#153F6B] text-white shadow-2xs"
                  : "text-[#52667E] hover:text-[#153F6B]"
              }`}
            >
              {language === "ta" ? "ராசி + நவாம்சம் (D1 & D9)" : "Rasi + Navamsa (D1 & D9)"}
            </button>
            <button
              type="button"
              onClick={() => setDualViewMode("d1_transits")}
              className={`px-3 py-1.5 text-xs font-bold rounded-lg transition-all cursor-pointer ${
                dualViewMode === "d1_transits"
                  ? "bg-[#153F6B] text-white shadow-2xs"
                  : "text-[#52667E] hover:text-[#153F6B]"
              }`}
            >
              {language === "ta" ? "ராசி + நேரலைக் கோசாரம்" : "Rasi + Live Transits"}
            </button>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* Chart 1: Rasi (D1) */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-bold text-[#153F6B]">
              <span>{language === "ta" ? "ராசிக் கட்டம் (D1 - ஜென்ம ஜாதகம்)" : "Rasi Chart (D1 - Natal)"}</span>
              <span className="text-[11px] text-[#8190A6]">
                {chartMode === "south" ? (language === "ta" ? "தென்னிந்திய முறை" : "South Indian") : (language === "ta" ? "வட இந்திய முறை" : "North Indian")}
              </span>
            </div>
            <div className="rounded-xl border border-[#D9DEE7] p-2 bg-[#F2F3F5]/30">
              {chartMode === "south" ? (
                <SouthIndianChart
                  horoscope={horoscope}
                  centerLabel={language === "ta" ? "ராசி" : "Rasi"}
                  highlightLagnaBlue
                />
              ) : (
                <NorthIndianChart
                  horoscope={horoscope}
                  highlightLagnaBlue
                />
              )}
            </div>
          </div>

          {/* Chart 2: Navamsa (D9) OR Live Transits */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-bold text-[#153F6B]">
              <span>
                {dualViewMode === "d1_d9"
                  ? language === "ta" ? "நவாம்சக் கட்டம் (D9 - பலம் & களத்திரம்)" : "Navamsa Chart (D9 - Strength)"
                  : language === "ta" ? "நேரலைக் கோசாரக் கட்டம் (Live Transits)" : "Live Gochara Transits"}
              </span>
              <span className="text-[11px] text-[#8190A6]">
                {dualViewMode === "d1_d9"
                  ? language === "ta" ? "பாகை விபரம் D9" : "Harmonic 9"
                  : liveTransitsData ? liveTransitsData.calculated_at?.split("T")[0] : "Today"}
              </span>
            </div>
            <div className="rounded-xl border border-[#D9DEE7] p-2 bg-[#F2F3F5]/30">
              {dualViewMode === "d1_d9" ? (
                d9Horoscope ? (
                  chartMode === "south" ? (
                    <SouthIndianChart
                      horoscope={d9Horoscope}
                      centerLabel={language === "ta" ? "நவாம்சம்" : "Navamsa"}
                    />
                  ) : (
                    <NorthIndianChart
                      horoscope={d9Horoscope}
                    />
                  )
                ) : (
                  <div className="h-64 flex items-center justify-center text-xs text-[#8190A6]">
                    {language === "ta" ? "நவாம்ச கணக்கீடு தயாராகிறது..." : "Calculating Navamsa..."}
                  </div>
                )
              ) : (
                /* Live Transits Chart */
                liveTransitsData ? (
                  chartMode === "south" ? (
                    <SouthIndianChart
                      horoscope={horoscope}
                      transitPlanets={liveTransitsData.planets}
                      showTransits={true}
                      centerLabel={language === "ta" ? "கோசாரம்" : "Transit"}
                    />
                  ) : (
                    <NorthIndianChart
                      horoscope={horoscope}
                      transitPlanets={liveTransitsData.planets}
                      showTransits={true}
                    />
                  )
                ) : (
                  <div className="h-64 flex flex-col items-center justify-center gap-2 text-xs text-[#8190A6]">
                    <RefreshCw className="w-5 h-5 animate-spin text-[#153F6B]" />
                    <span>{language === "ta" ? "கோசாரக் கணக்கீடு பெறப்படுகிறது..." : "Loading live planetary transits..."}</span>
                  </div>
                )
              )}
            </div>
          </div>
        </div>

        {/* Sarvashtakavarga (SAV) House Points Strip */}
        {savByHouse && (
          <div className="mt-4 pt-3 border-t border-[#F2F3F5]">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-[#183047] flex items-center gap-1.5">
                <Award className="w-3.5 h-3.5 text-[#B4872B]" />
                {language === "ta" ? "சர்வ அஷ்டகவர்க்க பிந்துக்கள் (SAV Points by House):" : "Sarvashtakavarga (SAV) Points by House:"}
              </span>
              <span className="text-[10px] text-[#8190A6]">
                {language === "ta" ? "சராசரி: 28 பிந்துக்கள் (>28 பலம், <25 பலவீனம்)" : "Standard Average: 28 bindus (>28 Strong, <25 Deficit)"}
              </span>
            </div>
            <div className="grid grid-cols-6 sm:grid-cols-12 gap-1.5 text-center">
              {Array.from({ length: 12 }, (_, i) => i + 1).map((houseNum) => {
                const pts = savByHouse[houseNum] || 0;
                const isStrong = pts >= 28;
                const isWeak = pts < 25;
                return (
                  <div
                    key={houseNum}
                    className={`py-1.5 px-1 rounded-lg border text-xs font-mono transition-all ${
                      isStrong
                        ? "bg-emerald-50 text-emerald-800 border-emerald-200 font-black"
                        : isWeak
                        ? "bg-rose-50 text-rose-800 border-rose-200 font-bold"
                        : "bg-[#F2F3F5]/60 text-[#183047] border-[#D9DEE7] font-semibold"
                    }`}
                  >
                    <div className="text-[9px] uppercase tracking-wider text-[#8190A6]">
                      {language === "ta" ? `${houseNum}ம்` : `H${houseNum}`}
                    </div>
                    <div className="text-xs font-bold">{pts}</div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* 4. PLANETARY POWER & DIGNITY HIGH-DENSITY MATRIX */}
      <div className="bg-white rounded-2xl border border-[#D9DEE7] p-4 sm:p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#F2F3F5] pb-3 mb-3">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-[#153F6B]/10 flex items-center justify-center text-[#153F6B]">
              <Star className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-sm sm:text-base text-[#183047]">
                {language === "ta" ? "நவகிரக வலிமை & அந்தஸ்து அட்டவணை" : "Planetary Power & Dignity Matrix"}
              </h3>
              <p className="text-xs text-[#8190A6]">
                {language === "ta"
                  ? "ஒரே பார்வையில் கிரகம், பாகை, நட்சத்திரம், லக்ன/சந்திர பாவ நிலை, ஷட்பல விகிதம் & வர்கோத்தமம்."
                  : "Single unified matrix for degrees, Nakshatra, dignities, Shadbala ratio, and Vargottama."}
              </p>
            </div>
          </div>
        </div>

        {/* Compact Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-[#D9DEE7] text-[10px] font-bold uppercase tracking-wider text-[#8190A6] bg-[#F2F3F5]/50">
                <th className="py-2.5 px-3">{language === "ta" ? "கிரகம்" : "Graha"}</th>
                <th className="py-2.5 px-2">{language === "ta" ? "ராசி" : "Sign"}</th>
                <th className="py-2.5 px-2 font-mono">{language === "ta" ? "பாகை" : "Degree"}</th>
                <th className="py-2.5 px-2">{language === "ta" ? "நட்சத்திரம் (பாதம்)" : "Nakshatra (Pada)"}</th>
                <th className="py-2.5 px-2 text-center">{language === "ta" ? "லக்ன பாவம்" : "House (Lag)"}</th>
                <th className="py-2.5 px-2 text-center">{language === "ta" ? "சந்திர பாவம்" : "House (Moo)"}</th>
                <th className="py-2.5 px-2">{language === "ta" ? "நிலை / அந்தஸ்து" : "Dignity"}</th>
                <th className="py-2.5 px-2 text-center">{language === "ta" ? "வர்கோத்தமம்" : "Vargottama"}</th>
                <th className="py-2.5 px-2 text-center">{language === "ta" ? "ஷட்பலம்" : "Shadbala"}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F2F3F5]">
              {planetaryMatrix.map((p) => {
                return (
                  <tr key={p.name} className="hover:bg-[#F2F3F5]/40 transition-colors">
                    {/* Graha Name with Retrogression / Combustion */}
                    <td className="py-2.5 px-3 font-bold text-[#183047] flex items-center gap-1.5 whitespace-nowrap">
                      <span>{getGrahaName(p.name, language)}</span>
                      {p.is_retrograde && (
                        <span
                          className="text-[9px] px-1 py-0.2 rounded font-black bg-purple-100 text-purple-800"
                          title="Retrograde (வக்ரம்)"
                        >
                          ℞
                        </span>
                      )}
                      {(p as any).is_combust && (
                        <span
                          className="text-[9px] px-1 py-0.2 rounded font-black bg-rose-100 text-rose-800 flex items-center gap-0.5"
                          title="Combust (அஸ்தங்கம்)"
                        >
                          <Flame className="w-2.5 h-2.5" />
                        </span>
                      )}
                    </td>

                    {/* Sign Name */}
                    <td className="py-2.5 px-2 text-[#52667E] whitespace-nowrap">
                      {language === "ta" ? p.sign_name_tamil : p.sign_name}
                    </td>

                    {/* Degree DMS */}
                    <td className="py-2.5 px-2 font-mono text-[#183047] whitespace-nowrap">
                      {formatDms(p.degree_in_sign)}
                    </td>

                    {/* Nakshatra & Pada */}
                    <td className="py-2.5 px-2 text-[#52667E] whitespace-nowrap">
                      {p.nakshatra ? (
                        <span>
                          {getNakshatraName(p.nakshatra.name, language)}{" "}
                          <span className="text-[10px] text-[#B4872B] font-semibold">
                            P-{p.nakshatra.pada}
                          </span>
                        </span>
                      ) : (
                        "-"
                      )}
                    </td>

                    {/* House from Lagna */}
                    <td className="py-2.5 px-2 text-center font-bold text-[#153F6B]">
                      {p.houseFromLagna}
                    </td>

                    {/* House from Moon */}
                    <td className="py-2.5 px-2 text-center text-[#52667E]">
                      {p.houseFromMoon}
                    </td>

                    {/* Dignity Badge */}
                    <td className="py-2.5 px-2 whitespace-nowrap">
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded-full font-bold border ${p.dignity.badgeBgClass} ${p.dignity.badgeBorderClass}`}
                      >
                        {language === "ta" ? p.dignity.labelTa : p.dignity.labelEn}
                      </span>
                    </td>

                    {/* Vargottama */}
                    <td className="py-2.5 px-2 text-center">
                      {p.isVargottama ? (
                        <span className="inline-flex items-center gap-0.5 text-[10px] font-bold text-amber-700 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded-full">
                          <Star className="w-2.5 h-2.5 fill-amber-500 text-amber-500" />
                          <span>{language === "ta" ? "ஆம்" : "Yes"}</span>
                        </span>
                      ) : (
                        <span className="text-[#8190A6] text-[10px]">-</span>
                      )}
                    </td>

                    {/* Shadbala */}
                    <td className="py-2.5 px-2 text-center whitespace-nowrap">
                      {p.shadbalaInfo ? (
                        <span
                          className={`text-[10px] font-bold px-1.5 py-0.5 rounded-md ${
                            p.shadbalaInfo.is_strong
                              ? "bg-emerald-50 text-emerald-800"
                              : "bg-rose-50 text-rose-800"
                          }`}
                        >
                          {p.shadbalaInfo.ratio.toFixed(2)}x
                        </span>
                      ) : (
                        <span className="text-[#8190A6] text-[10px]">-</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* 5. CONSULTATION INTELLIGENCE: YOGAS, TRANSIT RADAR & REMEDIES */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Card A: Key Yogas & Doshas */}
        <div className="bg-white rounded-2xl border border-[#D9DEE7] p-4 sm:p-5 shadow-xs flex flex-col justify-between space-y-3">
          <div className="space-y-2.5">
            <div className="flex items-center justify-between border-b border-[#F2F3F5] pb-2.5">
              <span className="text-xs font-bold text-[#153F6B] flex items-center gap-1.5">
                <Sparkles className="w-4 h-4 text-[#B4872B]" />
                {language === "ta" ? "யோகங்கள் & தோஷங்கள்" : "Key Yogas & Doshas"}
              </span>
              <span className="text-[10px] font-semibold text-[#8190A6]">
                {horoscope.vedic_yogas?.yogas?.length || 0} {language === "ta" ? "யோகங்கள்" : "Yogas"}
              </span>
            </div>

            {/* Kuja / Manglik Dosha status */}
            {horoscope.doshas?.kuja_dosha && (
              <div
                className={`p-2.5 rounded-xl border text-xs flex items-center justify-between ${
                  horoscope.doshas.kuja_dosha.is_present && !horoscope.doshas.kuja_dosha.is_cancelled
                    ? "bg-rose-50 border-rose-200 text-rose-900"
                    : "bg-emerald-50 border-emerald-200 text-emerald-900"
                }`}
              >
                <div>
                  <span className="font-bold">
                    {language === "ta" ? "செவ்வாய் தோஷம்:" : "Kuja / Manglik Dosha:"}
                  </span>{" "}
                  <span>
                    {horoscope.doshas.kuja_dosha.is_cancelled
                      ? language === "ta" ? "நிவர்த்தி (Cancelled)" : "Cancelled"
                      : horoscope.doshas.kuja_dosha.is_present
                      ? (horoscope.doshas.kuja_dosha.severity || (language === "ta" ? "உண்டு" : "Present"))
                      : language === "ta" ? "இல்லை (None)" : "None"}
                  </span>
                </div>
                {horoscope.doshas.kuja_dosha.is_cancelled && (
                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800">
                    Bhanga
                  </span>
                )}
              </div>
            )}

            {/* Kaal Sarp Dosha status */}
            {horoscope.doshas?.kaal_sarp_dosha && (
              <div
                className={`p-2.5 rounded-xl border text-xs flex items-center justify-between ${
                  horoscope.doshas.kaal_sarp_dosha.is_present
                    ? "bg-amber-50 border-amber-200 text-amber-900"
                    : "bg-[#F2F3F5]/60 border-[#D9DEE7] text-[#52667E]"
                }`}
              >
                <span className="font-bold">
                  {language === "ta" ? "கால சர்ப்ப தோஷம்:" : "Kaal Sarp Dosha:"}
                </span>
                <span>
                  {horoscope.doshas.kaal_sarp_dosha.is_present
                    ? horoscope.doshas.kaal_sarp_dosha.subtype_name || horoscope.doshas.kaal_sarp_dosha.dosha_type || (language === "ta" ? "உண்டு" : "Present")
                    : language === "ta" ? "இல்லை" : "None"}
                </span>
              </div>
            )}

            {/* Top Active Yogas */}
            <div className="space-y-1.5 pt-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#8190A6]">
                {language === "ta" ? "முக்கிய யோகங்கள்:" : "Prominent Yogas:"}
              </span>
              {horoscope.vedic_yogas?.yogas && horoscope.vedic_yogas.yogas.length > 0 ? (
                <div className="space-y-1">
                  {horoscope.vedic_yogas.yogas.slice(0, 4).map((y) => (
                    <div
                      key={y.id}
                      className="p-1.5 rounded-lg bg-[#F2F3F5]/50 border border-[#D9DEE7]/70 text-xs font-semibold text-[#183047] flex items-center justify-between"
                    >
                      <span>{language === "ta" ? y.name_tamil : y.name}</span>
                      <span className="text-[10px] text-[#B4872B] font-bold">
                        {y.category || "Yoga"}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-xs text-[#8190A6] italic">
                  {language === "ta" ? "யோகங்கள் கணக்கிடப்படவில்லை" : "No prominent yogas identified."}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Card B: Live Gochara Radar (Saturn, Jupiter, Rahu) */}
        <div className="bg-white rounded-2xl border border-[#D9DEE7] p-4 sm:p-5 shadow-xs flex flex-col justify-between space-y-3">
          <div className="space-y-2.5">
            <div className="flex items-center justify-between border-b border-[#F2F3F5] pb-2.5">
              <span className="text-xs font-bold text-[#153F6B] flex items-center gap-1.5">
                <Radio className="w-4 h-4 text-[#B4872B] animate-pulse" />
                {language === "ta" ? "நேரலைக் கோசார ரேடார்" : "Live Gochara Radar"}
              </span>
              <span className="text-[10px] font-semibold text-[#8190A6]">
                {liveTransitsData ? liveTransitsData.calculated_at?.split("T")[0] : "Today"}
              </span>
            </div>

            {/* Saturn Transit Status */}
            {gocharaRadar && (
              <div className={`p-2.5 rounded-xl border text-xs space-y-1 ${gocharaRadar.saturnBadgeColor}`}>
                <div className="font-bold flex items-center justify-between">
                  <span>{language === "ta" ? "சனி கோசாரம் (Shani):" : "Saturn Transit (Shani):"}</span>
                  <span className="font-mono text-[10px]">
                    {language === "ta" ? `சந்திரனிலிருந்து ${gocharaRadar.saturnDiff}ம் வீடு` : `H${gocharaRadar.saturnDiff} from Moon`}
                  </span>
                </div>
                <div className="text-[11px] font-semibold">
                  {language === "ta" ? gocharaRadar.saturnTransitTitleTa : gocharaRadar.saturnTransitTitleEn}
                </div>
              </div>
            )}

            {/* Jupiter Transit Status */}
            {gocharaRadar && (
              <div
                className={`p-2.5 rounded-xl border text-xs space-y-1 ${
                  gocharaRadar.isGuruBalam
                    ? "bg-emerald-50 text-emerald-900 border-emerald-200"
                    : "bg-[#F2F3F5]/60 text-[#52667E] border-[#D9DEE7]"
                }`}
              >
                <div className="font-bold flex items-center justify-between">
                  <span>{language === "ta" ? "குரு கோசாரம் (Guru):" : "Jupiter Transit (Guru):"}</span>
                  <span className="font-mono text-[10px]">
                    {language === "ta" ? `சந்திரனிலிருந்து ${gocharaRadar.jupiterDiff}ம் வீடு` : `H${gocharaRadar.jupiterDiff} from Moon`}
                  </span>
                </div>
                <div className="text-[11px] font-semibold">
                  {language === "ta" ? gocharaRadar.jupiterTransitTitleTa : gocharaRadar.jupiterTransitTitleEn}
                </div>
              </div>
            )}

            {/* Rahu / Ketu Axis */}
            {gocharaRadar?.transitRahu && gocharaRadar?.transitKetu && (
              <div className="p-2.5 rounded-xl bg-[#F2F3F5]/60 border border-[#D9DEE7] text-xs space-y-1 text-[#183047]">
                <div className="font-bold text-[11px] text-[#52667E]">
                  {language === "ta" ? "ராகு - கேது அச்சு:" : "Rahu - Ketu Transit Axis:"}
                </div>
                <div className="text-[11px] font-semibold">
                  {language === "ta"
                    ? `ராகு: ${gocharaRadar.transitRahu.sign_name_tamil} | கேது: ${gocharaRadar.transitKetu.sign_name_tamil}`
                    : `Rahu in ${gocharaRadar.transitRahu.sign_name} | Ketu in ${gocharaRadar.transitKetu.sign_name}`}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Card C: Prescribed Remedies for Running Dasa */}
        <div className="bg-white rounded-2xl border border-[#D9DEE7] p-4 sm:p-5 shadow-xs flex flex-col justify-between space-y-3">
          <div className="space-y-2.5">
            <div className="flex items-center justify-between border-b border-[#F2F3F5] pb-2.5">
              <span className="text-xs font-bold text-[#153F6B] flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-[#B4872B]" />
                {language === "ta" ? "நடப்பு தசா பரிகாரங்கள்" : "Prescribed Dasa Remedies"}
              </span>
              {activeHierarchy?.mahadasha?.lord && (
                <span className="text-[10px] font-black px-2 py-0.5 rounded-md bg-[#153F6B] text-white">
                  {getGrahaName(activeHierarchy.mahadasha.lord, language)}
                </span>
              )}
            </div>

            {activeRemedy ? (
              <div className="space-y-2 text-xs">
                {/* Deity & Temple */}
                <div className="p-2.5 rounded-xl bg-[#FAF2DE]/50 border border-[#B4872B]/30 space-y-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[#8C6212]">
                    {language === "ta" ? "அதிதேவதை & நவகிரக தலம்:" : "Presiding Deity & Temple:"}
                  </span>
                  <div className="font-bold text-[#183047]">
                    {language === "ta" ? activeRemedy.deityTa : activeRemedy.deityEn}
                  </div>
                  <div className="text-[11px] text-[#52667E]">
                    📍 {language === "ta" ? activeRemedy.templeTa : activeRemedy.templeEn}
                  </div>
                </div>

                {/* Mantra */}
                <div className="p-2 rounded-lg bg-[#F2F3F5]/60 border border-[#D9DEE7] text-[11px]">
                  <span className="font-bold text-[#153F6B] block">
                    {language === "ta" ? "தினம் சொல்ல வேண்டிய மந்திரம்:" : "Daily Recitation Mantra:"}
                  </span>
                  <span className="italic text-[#52667E]">
                    {language === "ta" ? activeRemedy.mantraTa : activeRemedy.mantraEn}
                  </span>
                </div>

                {/* Gemstone & Metal */}
                <div className="flex items-center justify-between p-2 rounded-lg bg-[#F2F3F5]/60 border border-[#D9DEE7] text-xs">
                  <span className="font-bold text-[#183047] flex items-center gap-1">
                    <Gem className="w-3.5 h-3.5 text-[#B4872B]" />
                    {language === "ta" ? "ரத்தினம்:" : "Gem:"}{" "}
                    <span className="font-normal">{language === "ta" ? activeRemedy.gemTa : activeRemedy.gemEn}</span>
                  </span>
                  <span className="text-[#52667E] text-[11px]">
                    {language === "ta" ? activeRemedy.metalTa : activeRemedy.metalEn}
                  </span>
                </div>
              </div>
            ) : (
              <div className="text-xs text-[#8190A6] italic py-2">
                {language === "ta" ? "பரிகார தகவல்கள் கிடைக்கவில்லை." : "Remedy details not loaded."}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 6. ASTROLOGER'S INTERACTIVE SCRATCHPAD & CLIENT TAKEAWAYS */}
      <div className="bg-white rounded-2xl border border-[#D9DEE7] p-4 sm:p-5 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#F2F3F5] pb-3">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-[#153F6B]/10 flex items-center justify-center text-[#153F6B]">
              <FileText className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-sm sm:text-base text-[#183047]">
                {language === "ta" ? "ஜோதிடர் நேரடி ஆலோசனைக் குறிப்பேடு" : "Astrologer's Live Consultation Scratchpad"}
              </h3>
              <p className="text-xs text-[#8190A6]">
                {language === "ta"
                  ? "வாடிக்கையாளருக்கான கணிப்புகள், பரிகாரங்கள் மற்றும் பதில்களை இங்கே உடனுக்குடன் குறித்துக் கொள்ளுங்கள் (தானாகச் சேமிக்கப்படும்)."
                  : "Draft direct consultation remarks, client questions, and custom remedies (auto-saved locally)."}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleSaveNotes}
              disabled={isSavingNotes}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-[#153F6B] hover:bg-[#0F3155] text-white text-xs font-bold shadow-2xs transition-colors cursor-pointer disabled:opacity-50"
            >
              {isSavingNotes ? (
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Save className="w-3.5 h-3.5" />
              )}
              <span>{language === "ta" ? "குறிப்புகளைச் சேமிக்க" : "Save Notes"}</span>
            </button>
          </div>
        </div>

        {/* Save confirmation toast */}
        {notesSaveStatus && (
          <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold flex items-center gap-2">
            <Check className="w-4 h-4 text-emerald-600" />
            <span>{notesSaveStatus}</span>
          </div>
        )}

        {/* Consultation Inquiry Focus Chips */}
        <div className="space-y-1.5">
          <span className="text-[10px] font-bold uppercase tracking-wider text-[#8190A6]">
            {language === "ta" ? "ஆலோசனை தலைப்புகள் / முக்கிய கேள்விகள்:" : "Consultation Inquiry Tags:"}
          </span>
          <div className="flex flex-wrap gap-1.5">
            {consultationTopics.map((top) => {
              const isSelected = selectedTopics.includes(top.id);
              return (
                <button
                  key={top.id}
                  type="button"
                  onClick={() => toggleTopic(top.id)}
                  className={`text-xs px-2.5 py-1 rounded-full font-semibold border transition-all cursor-pointer ${
                    isSelected
                      ? "bg-[#153F6B] text-white border-[#153F6B]"
                      : "bg-[#F2F3F5] text-[#52667E] border-[#D9DEE7] hover:border-[#153F6B] hover:text-[#153F6B]"
                  }`}
                >
                  {language === "ta" ? top.labelTa : top.labelEn}
                </button>
              );
            })}
          </div>
        </div>

        {/* Quick Snippet Inserters */}
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <span className="text-[10px] font-bold uppercase tracking-wider text-[#8190A6]">
            {language === "ta" ? "விரைவுச் சேர்க்கை:" : "Insert Snippet:"}
          </span>
          <button
            type="button"
            onClick={() =>
              handleInsertSnippet(
                language === "ta"
                  ? `⏳ *நடப்பு தசா கணிப்பு:*\n• மகா தசா: ${getGrahaName(activeHierarchy?.mahadasha?.lord || "", "ta")}\n• புக்தி: ${getGrahaName(activeHierarchy?.antardasha?.lord || "", "ta")}\n• பலன்:`
                  : `⏳ *Current Dasa Assessment:*\n• Mahadasha: ${activeHierarchy?.mahadasha?.lord || "-"}\n• Bhukti: ${activeHierarchy?.antardasha?.lord || "-"}\n• Analysis:`
              )
            }
            className="text-xs px-2 py-0.5 rounded-md bg-[#F2F3F5] hover:bg-white border border-[#D9DEE7] text-[#183047] font-semibold cursor-pointer"
          >
            + {language === "ta" ? "தசா ஆய்வு" : "Dasa Insight"}
          </button>
          <button
            type="button"
            onClick={() =>
              handleInsertSnippet(
                language === "ta"
                  ? `🪐 *கோசார தாக்கம்:*\n• சனி: ${gocharaRadar?.saturnTransitTitleTa || "-"}\n• குரு: ${gocharaRadar?.jupiterTransitTitleTa || "-"}`
                  : `🪐 *Transit Impact:*\n• Saturn: ${gocharaRadar?.saturnTransitTitleEn || "-"}\n• Jupiter: ${gocharaRadar?.jupiterTransitTitleEn || "-"}`
              )
            }
            className="text-xs px-2 py-0.5 rounded-md bg-[#F2F3F5] hover:bg-white border border-[#D9DEE7] text-[#183047] font-semibold cursor-pointer"
          >
            + {language === "ta" ? "கோசார பலன்" : "Transit Impact"}
          </button>
          <button
            type="button"
            onClick={() =>
              handleInsertSnippet(
                language === "ta"
                  ? `🪔 *பரிந்துரைக்கப்பட்ட பரிகாரங்கள்:*\n• கோவில்: ${activeRemedy?.templeTa || "-"}\n• மந்திரம்: ${activeRemedy?.mantraTa || "-"}\n• ரத்தினம்: ${activeRemedy?.gemTa || "-"}`
                  : `🪔 *Prescribed Remedies:*\n• Temple: ${activeRemedy?.templeEn || "-"}\n• Mantra: ${activeRemedy?.mantraEn || "-"}\n• Gemstone: ${activeRemedy?.gemEn || "-"}`
              )
            }
            className="text-xs px-2 py-0.5 rounded-md bg-[#F2F3F5] hover:bg-white border border-[#D9DEE7] text-[#183047] font-semibold cursor-pointer"
          >
            + {language === "ta" ? "பரிகாரங்கள்" : "Remedies"}
          </button>
          <button
            type="button"
            onClick={() =>
              handleInsertSnippet(
                language === "ta"
                  ? `⭐ *சாதகமான காலம் / சுப முகூர்த்தம்:*\n• காலம்:`
                  : `⭐ *Favorable Window / Auspicious Timing:*\n• Window:`
              )
            }
            className="text-xs px-2 py-0.5 rounded-md bg-[#F2F3F5] hover:bg-white border border-[#D9DEE7] text-[#183047] font-semibold cursor-pointer"
          >
            + {language === "ta" ? "சாதகமான காலம்" : "Favorable Timing"}
          </button>
        </div>

        {/* Text Area */}
        <textarea
          rows={7}
          value={consultationNotes}
          onChange={(e) => setConsultationNotes(e.target.value)}
          placeholder={
            language === "ta"
              ? "வாடிக்கையாளரின் கேள்விகள், தசா-புக்தி பலன்கள், தொழில்/திருமண வழிகாட்டல் அல்லது பரிகாரங்கள் குறித்த ஆலோசனைக் குறிப்புகளை இங்கே பதிவு செய்யவும்..."
              : "Type active consultation findings, client queries, job/marriage guidance, and prescribed remedies here..."
          }
          className="w-full text-xs sm:text-sm p-3.5 rounded-xl border border-[#D9DEE7] bg-[#F2F3F5]/30 text-[#183047] focus:outline-none focus:ring-1 focus:ring-[#153F6B] focus:border-[#153F6B] font-sans leading-relaxed"
        />
      </div>
    </div>
  );
}
