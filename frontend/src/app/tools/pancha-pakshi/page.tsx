"use client";

import React, { useState, useEffect, useMemo, useCallback, Suspense } from "react";
import { DateInputDMY } from "@/components/common/DateInputDMY";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  PanchaPakshiResponse,
  AntaraSlot,
  YamamSlot,
  BirdItem,
  SavedHoroscopeItem,
} from "@/lib/types";
import {
  calculatePanchaPakshi,
  getPanchaPakshiBirds,
  downloadPanchaPakshiPdf,
  triggerBlobDownload,
  calculateHoroscope,
} from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import {
  Sparkles,
  Clock,
  Calendar,
  Compass,
  MapPin,
  RefreshCw,
  AlertCircle,
  ShieldAlert,
  ShieldCheck,
  ChevronLeft,
  ChevronRight,
  Flame,
  CheckCircle2,
  XCircle,
  Info,
  Timer,
  Zap,
  Award,
  Sun,
  Moon,
  ArrowRight,
  HelpCircle,
  Download,
  Search,
  FolderOpen,
  User,
  X,
  Database,
  Check,
} from "lucide-react";

interface CityPreset {
  name_en: string;
  name_ta: string;
  lat: number;
  lon: number;
  tz: string;
}

const CITY_PRESETS: CityPreset[] = [
  { name_en: "Chennai", name_ta: "சென்னை", lat: 13.0827, lon: 80.2707, tz: "Asia/Kolkata" },
  { name_en: "Madurai", name_ta: "மதுரை", lat: 9.9252, lon: 78.1198, tz: "Asia/Kolkata" },
  { name_en: "Coimbatore", name_ta: "கோயம்புத்தூர்", lat: 11.0168, lon: 76.9558, tz: "Asia/Kolkata" },
  { name_en: "Tiruchirappalli", name_ta: "திருச்சி", lat: 10.7905, lon: 78.7047, tz: "Asia/Kolkata" },
  { name_en: "Bengaluru", name_ta: "பெங்களூரு", lat: 12.9716, lon: 77.5946, tz: "Asia/Kolkata" },
  { name_en: "Mumbai", name_ta: "மும்பை", lat: 19.0760, lon: 72.8777, tz: "Asia/Kolkata" },
  { name_en: "New Delhi", name_ta: "புது தில்லி", lat: 28.6139, lon: 77.2090, tz: "Asia/Kolkata" },
  { name_en: "Singapore", name_ta: "சிங்கப்பூர்", lat: 1.3521, lon: 103.8198, tz: "Asia/Singapore" },
  { name_en: "London", name_ta: "லண்டன்", lat: 51.5074, lon: -0.1278, tz: "Europe/London" },
  { name_en: "New York", name_ta: "நியூயார்க்", lat: 40.7128, lon: -74.0060, tz: "America/New_York" },
];

const NAKSHATRAS = [
  { index: 1, name_en: "Ashwini", name_ta: "அசுவினி" },
  { index: 2, name_en: "Bharani", name_ta: "பரணி" },
  { index: 3, name_en: "Krittika", name_ta: "கார்த்திகை" },
  { index: 4, name_en: "Rohini", name_ta: "ரோகிணி" },
  { index: 5, name_en: "Mrigashira", name_ta: "மிருகசீரிஷம்" },
  { index: 6, name_en: "Ardra", name_ta: "திருவாதிரை" },
  { index: 7, name_en: "Punarvasu", name_ta: "புனர்பூசம்" },
  { index: 8, name_en: "Pushya", name_ta: "பூசம்" },
  { index: 9, name_en: "Ashlesha", name_ta: "ஆயில்யம்" },
  { index: 10, name_en: "Magha", name_ta: "மகம்" },
  { index: 11, name_en: "Purva Phalguni", name_ta: "பூரம்" },
  { index: 12, name_en: "Uttara Phalguni", name_ta: "உத்திரம்" },
  { index: 13, name_en: "Hasta", name_ta: "அஸ்தம்" },
  { index: 14, name_en: "Chitra", name_ta: "சித்திரை" },
  { index: 15, name_en: "Swati", name_ta: "சுவாதி" },
  { index: 16, name_en: "Vishakha", name_ta: "விசாகம்" },
  { index: 17, name_en: "Anuradha", name_ta: "அனுஷம்" },
  { index: 18, name_en: "Jyeshtha", name_ta: "கேட்டை" },
  { index: 19, name_en: "Moola", name_ta: "மூலம்" },
  { index: 20, name_en: "Purva Ashadha", name_ta: "பூராடம்" },
  { index: 21, name_en: "Uttara Ashadha", name_ta: "உத்திராடம்" },
  { index: 22, name_en: "Shravana", name_ta: "திருவோணம்" },
  { index: 23, name_en: "Dhanishta", name_ta: "அவிட்டம்" },
  { index: 24, name_en: "Shatabhisha", name_ta: "சதயம்" },
  { index: 25, name_en: "Purva Bhadrapada", name_ta: "பூரட்டாதி" },
  { index: 26, name_en: "Uttara Bhadrapada", name_ta: "உத்திரட்டாதி" },
  { index: 27, name_en: "Revati", name_ta: "ரேவதி" },
];

/**
 * Extracts Moon Janma Nakshatra index (1..27) and Paksha ("shukla" | "krishna")
 * from a calculated horoscope snapshot or record.
 */
function extractNakshatraAndPaksha(horo: any): { nakshatra: number; paksha: "shukla" | "krishna" } | null {
  if (!horo) return null;
  const snap = horo.calculation_result?.horoscope || horo.horoscope || horo;
  const planets = snap?.planets || [];
  const moon = Array.isArray(planets) ? planets.find((p: any) => p?.name?.toLowerCase() === "moon") : null;
  const sun = Array.isArray(planets) ? planets.find((p: any) => p?.name?.toLowerCase() === "sun") : null;

  let nakshatraIdx: number | null = null;
  if (moon?.nakshatra?.index && moon.nakshatra.index >= 1 && moon.nakshatra.index <= 27) {
    nakshatraIdx = moon.nakshatra.index;
  } else if (typeof moon?.longitude === "number") {
    nakshatraIdx = Math.floor((((moon.longitude % 360) + 360) % 360) / (360 / 27)) + 1;
  } else if (snap?.panchang?.nakshatra) {
    const rawNak = String(snap.panchang.nakshatra).toLowerCase().trim();
    const found = NAKSHATRAS.find((n) => n.name_en.toLowerCase() === rawNak || n.name_ta === rawNak);
    if (found) nakshatraIdx = found.index;
  }

  let paksha: "shukla" | "krishna" = "shukla";
  const rawPaksha = snap?.panchang?.tithi?.paksha || "";
  if (rawPaksha) {
    if (
      rawPaksha.toLowerCase().includes("krishna") ||
      rawPaksha.includes("தேய்") ||
      rawPaksha.toLowerCase().includes("waning")
    ) {
      paksha = "krishna";
    } else {
      paksha = "shukla";
    }
  } else if (typeof moon?.longitude === "number" && typeof sun?.longitude === "number") {
    const diff = ((moon.longitude - sun.longitude) % 360 + 360) % 360;
    paksha = diff >= 180 ? "krishna" : "shukla";
  }

  if (nakshatraIdx && nakshatraIdx >= 1 && nakshatraIdx <= 27) {
    return { nakshatra: nakshatraIdx, paksha };
  }
  return null;
}

function PanchaPakshiStudioInner() {
  const { language } = useLanguage();
  const searchParams = useSearchParams();
  const { session, isAuthenticated, isLoading: authLoading } = useAuth();

  // Mode: "saved" (load client chart) | "manual" (direct star & paksha)
  const [inputMode, setInputMode] = useState<"saved" | "manual">("manual");
  const [nativeName, setNativeName] = useState<string>(() => {
    return searchParams?.get("native_name") || searchParams?.get("name") || "Native";
  });

  // Saved horoscopes state
  const [savedHoroscopes, setSavedHoroscopes] = useState<SavedHoroscopeItem[]>([]);
  const [loadingSavedList, setLoadingSavedList] = useState<boolean>(false);
  const [selectedChart, setSelectedChart] = useState<SavedHoroscopeItem | null>(null);
  const [loadingChartDetails, setLoadingChartDetails] = useState<boolean>(false);
  const [chartLoadError, setChartLoadError] = useState<string | null>(null);

  // Search input & manual filter state
  const [chartSearchQuery, setChartSearchQuery] = useState<string>("");
  const [submittedSearchQuery, setSubmittedSearchQuery] = useState<string>("");
  const [showSearchModal, setShowSearchModal] = useState<boolean>(false);

  // Inputs state - safely initialize with fallback from searchParams or defaults
  const [dateStr, setDateStr] = useState<string>(() => {
    const pDate = searchParams?.get("date") || searchParams?.get("target_date");
    if (pDate && !isNaN(Date.parse(pDate))) return pDate.split("T")[0];
    return new Date().toISOString().split("T")[0];
  });
  const [selectedCity, setSelectedCity] = useState<CityPreset>(() => {
    const cityName = searchParams?.get("city") || searchParams?.get("location");
    if (cityName) {
      const found = CITY_PRESETS.find(
        (c) => c.name_en.toLowerCase() === cityName.toLowerCase() || c.name_ta === cityName
      );
      if (found) return found;
    }
    return CITY_PRESETS[0];
  });
  const [latitude, setLatitude] = useState<number>(() => {
    const pLat = searchParams?.get("lat") || searchParams?.get("latitude");
    if (pLat && !isNaN(parseFloat(pLat))) return parseFloat(pLat);
    return CITY_PRESETS[0].lat;
  });
  const [longitude, setLongitude] = useState<number>(() => {
    const pLon = searchParams?.get("lon") || searchParams?.get("longitude");
    if (pLon && !isNaN(parseFloat(pLon))) return parseFloat(pLon);
    return CITY_PRESETS[0].lon;
  });
  const [timezoneStr, setTimezoneStr] = useState<string>(() => {
    return searchParams?.get("tz") || searchParams?.get("timezone") || CITY_PRESETS[0].tz;
  });

  const [birthNakshatra, setBirthNakshatra] = useState<number>(() => {
    const pNak = searchParams?.get("nakshatra") || searchParams?.get("star") || searchParams?.get("birth_nakshatra");
    if (pNak) {
      const parsed = parseInt(pNak, 10);
      if (!isNaN(parsed) && parsed >= 1 && parsed <= 27) return parsed;
      const found = NAKSHATRAS.find(
        (n) => n.name_en.toLowerCase() === pNak.toLowerCase() || n.name_ta === pNak
      );
      if (found) return found.index;
    }
    return 4; // Rohini default
  });
  const [birthPaksha, setBirthPaksha] = useState<"shukla" | "krishna">(() => {
    const pPak = searchParams?.get("paksha") || searchParams?.get("birth_paksha");
    if (pPak && (pPak.toLowerCase().includes("krishna") || pPak.includes("தேய்") || pPak.toLowerCase().includes("waning"))) {
      return "krishna";
    }
    return "shukla";
  });

  // View state
  const [activeTab, setActiveTab] = useState<"timeline" | "golden" | "padupakshi" | "lore">("timeline");
  const [timelineFilter, setTimelineFilter] = useState<"all" | "day" | "night">("all");
  const [selectedAntaraModal, setSelectedAntaraModal] = useState<AntaraSlot | null>(null);

  // Data state
  const [data, setData] = useState<PanchaPakshiResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Live ticking clock
  const [nowTime, setNowTime] = useState<Date>(new Date());
  const [downloadingPdf, setDownloadingPdf] = useState<boolean>(false);

  // Filtered horoscopes for search
  const filteredHoroscopes = useMemo(() => {
    const q = (submittedSearchQuery || chartSearchQuery).trim().toLowerCase();
    if (!q) return savedHoroscopes;

    return savedHoroscopes.filter((item) => {
      const name = (item.person_name || "").toLowerCase();
      const birthDate = (item.birth_date || "").toLowerCase();
      const birthTime = (item.birth_time || "").toLowerCase();
      const place = (item.birthplace || item.location_name || "").toLowerCase();
      const dispNum = item.display_number ? String(item.display_number) : "";
      const phone = (
        item.customer_phone ||
        item.normalized_phone ||
        item.phone_number ||
        item.whatsapp_number ||
        ""
      ).toLowerCase();

      return (
        name.includes(q) ||
        birthDate.includes(q) ||
        birthTime.includes(q) ||
        place.includes(q) ||
        dispNum === q ||
        `#${dispNum}` === q ||
        phone.includes(q)
      );
    });
  }, [savedHoroscopes, chartSearchQuery, submittedSearchQuery]);

  const handleManualSearch = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setSubmittedSearchQuery(chartSearchQuery.trim());
  };

  const handleClearSearch = () => {
    setChartSearchQuery("");
    setSubmittedSearchQuery("");
  };

  // Close modal on Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && showSearchModal) {
        setShowSearchModal(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [showSearchModal]);

  // Fetch saved horoscopes list
  const fetchSavedHoroscopes = useCallback(async () => {
    if (!session?.access_token) return [];
    setLoadingSavedList(true);
    try {
      const resp = await fetch("/api/horoscopes?page=1&limit=1000", {
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${session.access_token}`,
        },
        cache: "no-store",
      });
      if (resp.ok) {
        const resData = await resp.json();
        const items: SavedHoroscopeItem[] = resData.horoscopes || [];
        setSavedHoroscopes(items);
        return items;
      }
    } catch (err) {
      console.warn("Could not load saved horoscopes:", err);
    } finally {
      setLoadingSavedList(false);
    }
    return [];
  }, [session?.access_token]);

  // Handler to select and load a saved chart
  const handleSelectSavedChart = async (chart: SavedHoroscopeItem) => {
    setSelectedChart(chart);
    setLoadingChartDetails(true);
    setChartLoadError(null);
    const resolvedName = chart.person_name?.trim() || "Client";
    setNativeName(resolvedName);
    setShowSearchModal(false);

    try {
      let fullRecord: any = chart;
      // If calculation_result is missing from the list item, fetch the full horoscope record
      if (!chart.calculation_result && session?.access_token) {
        try {
          const resp = await fetch(`/api/horoscopes/${chart.id}`, {
            headers: {
              Accept: "application/json",
              Authorization: `Bearer ${session.access_token}`,
            },
          });
          if (resp.ok) {
            const json = await resp.json();
            if (json.horoscope) {
              fullRecord = json.horoscope;
            }
          }
        } catch (fErr) {
          console.warn("Could not fetch full horoscope snapshot:", fErr);
        }
      }

      // Try extracting nakshatra and paksha
      let extracted = extractNakshatraAndPaksha(fullRecord);

      // If not present in snapshot, calculate on the fly
      if (!extracted && fullRecord.birth_date && fullRecord.latitude && fullRecord.longitude) {
        try {
          let bTime = fullRecord.birth_time || "12:00:00";
          if (bTime.trim().length === 5) bTime += ":00";
          const calcRes = await calculateHoroscope({
            birth_date: fullRecord.birth_date,
            birth_time: bTime,
            latitude: Number(fullRecord.latitude),
            longitude: Number(fullRecord.longitude),
            timezone: fullRecord.timezone || "Asia/Kolkata",
            ayanamsa: fullRecord.ayanamsa_id || 1,
            house_system: fullRecord.house_system_id || 1,
            include_panchang: true,
            include_outer_planets: false,
          });
          extracted = extractNakshatraAndPaksha(calcRes);
        } catch (cErr) {
          console.warn("calculateHoroscope fallback failed:", cErr);
        }
      }

      if (extracted) {
        setBirthNakshatra(extracted.nakshatra);
        setBirthPaksha(extracted.paksha);
      } else {
        setChartLoadError(
          language === "ta"
            ? "ஜாதகரின் நட்சத்திரம் மற்றும் பக்ஷம் தானாக அறிய இயலவில்லை. தயவுசெய்து கீழே நேரடியாக தேர்வு செய்யவும்."
            : "Could not auto-determine birth star/paksha. Please select manually below."
        );
      }

      // Match city preset if close, or adopt latitude/longitude
      if (typeof fullRecord.latitude === "number" && typeof fullRecord.longitude === "number") {
        const matchCity = CITY_PRESETS.find(
          (c) => Math.abs(c.lat - fullRecord.latitude) < 0.25 && Math.abs(c.lon - fullRecord.longitude) < 0.25
        );
        if (matchCity) {
          setSelectedCity(matchCity);
          setLatitude(matchCity.lat);
          setLongitude(matchCity.lon);
          setTimezoneStr(matchCity.tz);
        } else {
          setLatitude(fullRecord.latitude);
          setLongitude(fullRecord.longitude);
          if (fullRecord.timezone) setTimezoneStr(fullRecord.timezone);
        }
      }
    } catch (err: any) {
      console.error("Error loading saved chart for Pancha Pakshi:", err);
      setChartLoadError(err?.message || "Failed to load saved chart particulars.");
    } finally {
      setLoadingChartDetails(false);
    }
  };

  // Initial load of saved horoscopes & auto-open if ?saved_id=... is in URL
  useEffect(() => {
    if (isAuthenticated) {
      fetchSavedHoroscopes().then((items) => {
        const savedIdParam = searchParams?.get("saved_id") || searchParams?.get("id");
        if (savedIdParam && items && items.length > 0) {
          const found = items.find((h) => h.id === savedIdParam);
          if (found) {
            setInputMode("saved");
            handleSelectSavedChart(found);
          }
        }
      });
    }
  }, [isAuthenticated, fetchSavedHoroscopes, searchParams]);

  const handleDownloadPdf = async () => {
    setDownloadingPdf(true);
    try {
      const nakObj = NAKSHATRAS.find((n) => n.index === birthNakshatra);
      const clientName = nativeName?.trim() || selectedChart?.person_name?.trim() || "Native";
      const blob = await downloadPanchaPakshiPdf({
        nakshatra: nakObj?.name_en || "Rohini",
        paksha: birthPaksha,
        target_date: dateStr,
        latitude: latitude,
        longitude: longitude,
        location_name: selectedCity.name_en,
        native_name: clientName,
        language: language === "ta" ? "ta" : "en",
      });
      const safeName = clientName.replace(/[^\w\s-]/g, "").replace(/\s+/g, "_") || "Native";
      triggerBlobDownload(blob, `Agastya_Pancha_Pakshi_24Hr_${safeName}_${dateStr}.pdf`);
    } catch (err: any) {
      alert(err?.message || "Failed to download Pancha Pakshi PDF report.");
    } finally {
      setDownloadingPdf(false);
    }
  };

  useEffect(() => {
    const timer = setInterval(() => {
      setNowTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const handleSelectCity = (city: CityPreset) => {
    setSelectedCity(city);
    setLatitude(city.lat);
    setLongitude(city.lon);
    setTimezoneStr(city.tz);
  };

  const shiftDate = (days: number) => {
    const d = new Date(dateStr);
    d.setDate(d.getDate() + days);
    setDateStr(d.toISOString().split("T")[0]);
  };

  const resetToToday = () => {
    setDateStr(new Date().toISOString().split("T")[0]);
  };

  const fetchBioRhythms = async () => {
    // Defensive parameter sanitization to prevent 422 or empty payload errors
    const validNakshatra = Math.max(1, Math.min(27, parseInt(String(birthNakshatra), 10) || 4));
    const validPaksha: "shukla" | "krishna" = birthPaksha === "krishna" ? "krishna" : "shukla";
    const validDate = dateStr && !isNaN(Date.parse(dateStr))
      ? dateStr.split("T")[0]
      : new Date().toISOString().split("T")[0];
    const validLat = typeof latitude === "number" && !isNaN(latitude) ? latitude : selectedCity.lat;
    const validLon = typeof longitude === "number" && !isNaN(longitude) ? longitude : selectedCity.lon;
    const validTz = timezoneStr || selectedCity.tz || "Asia/Kolkata";

    setLoading(true);
    setError(null);
    try {
      const res = await calculatePanchaPakshi({
        target_date: validDate,
        latitude: validLat,
        longitude: validLon,
        timezone: validTz,
        birth_nakshatra: validNakshatra,
        birth_paksha: validPaksha,
      });
      setData(res);
    } catch (err: any) {
      console.error("Pancha Pakshi calculation error:", err);
      let msg = "";
      if (typeof err?.message === "string" && err.message.trim() && err.message !== "[object Object]") {
        msg = err.message.trim();
      } else if (typeof err?.data?.detail === "string" && err.data.detail.trim() && err.data.detail !== "[object Object]") {
        msg = err.data.detail.trim();
      } else if (Array.isArray(err?.data?.validation_errors) && err.data.validation_errors.length > 0) {
        msg = err.data.validation_errors
          .map((v: any) => `${v.field || ""}: ${v.message || v.type || "Invalid"}`)
          .join("; ");
      } else if (Array.isArray(err?.data?.detail) && err.data.detail.length > 0) {
        msg = err.data.detail
          .map((d: any) => (typeof d === "string" ? d : d.msg || d.message || JSON.stringify(d)))
          .join("; ");
      } else if (typeof err?.data?.error === "string" && err.data.error.trim()) {
        msg = err.data.error.trim();
      } else {
        msg = language === "ta"
          ? "பஞ்ச பட்சி சாஸ்திர கணிப்பில் பிழை ஏற்பட்டது. தயவுசெய்து அளவுருக்களை சரிபார்த்து மீண்டும் முயற்சிக்கவும்."
          : "Failed to calculate Pancha Pakshi bio-rhythms. Please check parameters and try again.";
      }
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBioRhythms();
  }, [dateStr, latitude, longitude, timezoneStr, birthNakshatra, birthPaksha]);

  // Current active sub-period (Antara)
  const currentActiveAntara = useMemo(() => {
    if (!data?.all_antaras || data.all_antaras.length === 0) return null;
    const nowMs = nowTime.getTime();

    for (let i = 0; i < data.all_antaras.length; i++) {
      const slot = data.all_antaras[i];
      const startMs = new Date(slot.start_time_utc).getTime();
      const endMs = new Date(slot.end_time_utc).getTime();

      if (nowMs >= startMs && nowMs < endMs) {
        const totalMs = endMs - startMs;
        const elapsedMs = Math.max(0, nowMs - startMs);
        const remainingMs = Math.max(0, endMs - nowMs);
        const progressPercent = Math.min(100, Math.round((elapsedMs / totalMs) * 100));

        const remMins = Math.floor(remainingMs / 60000);
        const remSecs = Math.floor((remainingMs % 60000) / 1000);

        const nextSlot = i + 1 < data.all_antaras.length ? data.all_antaras[i + 1] : null;

        return {
          slot,
          progressPercent,
          remainingMinutes: remMins,
          remainingSeconds: remSecs,
          nextSlot,
          isToday: dateStr === new Date().toISOString().split("T")[0],
        };
      }
    }
    return null;
  }, [data, nowTime, dateStr]);

  // Filtered Antaras for Timeline Tab
  const filteredAntaras = useMemo(() => {
    if (!data?.all_antaras) return [];
    if (timelineFilter === "day") {
      return data.all_antaras.filter((a) => a.period_type === "day");
    }
    if (timelineFilter === "night") {
      return data.all_antaras.filter((a) => a.period_type === "night");
    }
    return data.all_antaras;
  }, [data, timelineFilter]);

  return (
    <div className="min-h-screen bg-[#F4F6F9] text-[#102A4C]">
      {/* Top Sticky Header & Breadcrumbs */}
      <div className="bg-white border-b border-[#DDE5F0] sticky top-0 z-20 shadow-2xs">
        <div className="w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-4">
          <Breadcrumbs
            items={[
              { label: language === "ta" ? "முகப்பு" : "Home", href: "/" },
              { label: language === "ta" ? "கருவிகள்" : "Tools", href: "/tools" },
              {
                label:
                  language === "ta"
                    ? "பஞ்ச பட்சி சாஸ்திரம் & பயோ-ரிதம் அரங்கம்"
                    : "Pancha Pakshi Bio-Rhythms Studio",
              },
            ]}
          />

          <div className="mt-3 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold uppercase tracking-wider mb-1">
                <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
                <span>{language === "ta" ? "அகத்தியர் சித்த முறை பஞ்ச பட்சி சாஸ்திரம்" : "Sage Agastya's Pancha Pakshi Siddha System"}</span>
              </div>
              <h1 className="font-serif text-2xl sm:text-3xl font-bold text-[#102A4C]">
                {language === "ta"
                  ? "பஞ்ச பட்சி சாஸ்திரம் & பயோ-ரிதம் அரங்கம்"
                  : "Pancha Pakshi Shastra (Five Birds Bio-Rhythms Studio)"}
              </h1>
              <p className="text-xs sm:text-sm text-[#52667E] mt-0.5">
                {language === "ta"
                  ? "வல்லூறு, ஆந்தை, காகம், கோழி, மயில் ஐந்து பட்சிகளின் அரசு, ஊண், நடை, துயில், சாவு அந்தர கால அட்டவணை."
                  : "Daily bio-rhythmic energy transitions across Ruling, Eating, Walking, Sleeping, and Dying phases."}
              </p>
            </div>

            <div className="flex items-center gap-2 flex-wrap">
              <button
                type="button"
                onClick={() => {
                  setInputMode("saved");
                  setShowSearchModal(true);
                }}
                className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-white border border-[#DDE5F0] hover:bg-slate-50 text-[#102A4C] text-xs font-semibold shadow-xs transition-all cursor-pointer"
              >
                <FolderOpen className="w-3.5 h-3.5 text-amber-600" />
                <span>
                  {language === "ta" ? "சேமித்த ஜாதகம் திற" : "Open Saved Chart"}
                </span>
                {savedHoroscopes.length > 0 && (
                  <span className="ml-0.5 px-1.5 py-0.2 rounded-full bg-slate-100 text-[#52667E] text-[10px] font-mono">
                    {savedHoroscopes.length}
                  </span>
                )}
              </button>

              <button
                type="button"
                onClick={handleDownloadPdf}
                disabled={downloadingPdf}
                className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold shadow-xs transition-all cursor-pointer"
              >
                <Download className={`w-3.5 h-3.5 ${downloadingPdf ? "animate-spin" : ""}`} />
                <span>
                  {downloadingPdf
                    ? (language === "ta" ? "தயாராகிறது..." : "Compiling PDF...")
                    : (language === "ta" ? "24-மணி நேர PDF அறிக்கை" : "Download 24-Hr PDF")}
                </span>
              </button>

              <button
                type="button"
                onClick={fetchBioRhythms}
                disabled={loading}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#102A4C] hover:bg-[#16365C] text-white text-xs font-semibold shadow-xs transition-all cursor-pointer"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-amber-300" : ""}`} />
                <span>{loading ? (language === "ta" ? "கணக்கிடுகிறது..." : "Calculating...") : (language === "ta" ? "புதுப்பி" : "Refresh Rhythms")}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 sm:py-8 space-y-8">
        {/* INPUTS & BIRTH BIRD SELECTOR BAR */}
        <div className="p-6 rounded-3xl bg-white border border-[#DDE5F0] shadow-xs space-y-5">
          {/* Top Switcher: Saved Chart vs Manual Selection */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#E2E8F0] gap-3">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-amber-500/10 border border-amber-300 flex items-center justify-center text-amber-800">
                <Sparkles className="w-4 h-4 text-amber-600" />
              </div>
              <div>
                <h2 className="text-sm font-bold text-[#102A4C]">
                  {language === "ta" ? "ஜாதக தேர்வு & பஞ்ச பட்சி அளவுருக்கள்" : "Horoscope & Bio-Rhythm Parameters"}
                </h2>
                <p className="text-[11px] text-[#52667E]">
                  {language === "ta"
                    ? "சேமித்த ஜாதகத்தை திறக்கவும் அல்லது நேரடியாக நட்சத்திரம் & பக்ஷம் தேர்வு செய்யவும்"
                    : "Open a saved client chart with search, or select star and paksha manually"}
                </p>
              </div>
            </div>

            {/* Mode Switcher Tabs */}
            <div className="inline-flex p-1 rounded-xl bg-[#F1F5F9] border border-[#E2E8F0] text-xs self-start sm:self-auto">
              <button
                type="button"
                onClick={() => setInputMode("saved")}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer ${
                  inputMode === "saved"
                    ? "bg-white text-[#102A4C] shadow-2xs"
                    : "text-[#52667E] hover:text-[#102A4C]"
                }`}
              >
                <FolderOpen className="w-3.5 h-3.5 text-amber-600" />
                <span>{language === "ta" ? "சேமித்த ஜாதகம்" : "Saved Chart"}</span>
                {savedHoroscopes.length > 0 && (
                  <span className="px-1.5 py-0.2 rounded-full bg-slate-200 text-[#102A4C] text-[10px] font-mono">
                    {savedHoroscopes.length}
                  </span>
                )}
              </button>
              <button
                type="button"
                onClick={() => setInputMode("manual")}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer ${
                  inputMode === "manual"
                    ? "bg-white text-[#102A4C] shadow-2xs"
                    : "text-[#52667E] hover:text-[#102A4C]"
                }`}
              >
                <Compass className="w-3.5 h-3.5 text-blue-600" />
                <span>{language === "ta" ? "நேரடி தேர்வு" : "Manual Selection"}</span>
              </button>
            </div>
          </div>

          {/* If Saved Chart Mode */}
          {inputMode === "saved" && (
            <div className="space-y-4">
              {/* Search Bar with Manual Search Button */}
              <div className="bg-[#FAF8F5] p-3.5 sm:p-4 rounded-2xl border border-[#E5E0D5] space-y-3">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold text-[#102A4C] flex items-center gap-1.5">
                    <Search className="w-3.5 h-3.5 text-amber-700" />
                    <span>
                      {language === "ta" ? "சேமித்த ஜாதகத்தைத் தேடுக" : "Search Saved Client Charts"}
                    </span>
                  </label>
                  <span className="text-[11px] font-mono text-[#64748B]">
                    {savedHoroscopes.length} {language === "ta" ? "ஜாதகங்கள்" : "saved charts"}
                  </span>
                </div>

                <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
                  <form onSubmit={handleManualSearch} className="flex-1 flex items-center gap-2">
                    <div className="relative flex-1">
                      <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                      <input
                        type="text"
                        value={chartSearchQuery}
                        onChange={(e) => setChartSearchQuery(e.target.value)}
                        placeholder={
                          language === "ta"
                            ? "ஜாதகர் பெயர், ஊர், பிறந்த தேதி (YYYY-MM-DD), எண் மூலம் தேடுக..."
                            : "Search by client name, place, date (YYYY-MM-DD), or chart #..."
                        }
                        className="w-full text-xs pl-9 pr-8 py-2.5 border border-[#CBD5E1] rounded-xl outline-none focus:ring-2 focus:ring-[#102A4C] bg-white text-[#102A4C]"
                      />
                      {chartSearchQuery && (
                        <button
                          type="button"
                          onClick={handleClearSearch}
                          className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-0.5 cursor-pointer"
                          title="Clear"
                        >
                          <X className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>

                    {/* Manual Search Button */}
                    <button
                      type="submit"
                      className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-[#102A4C] hover:bg-[#16365C] text-white text-xs font-semibold shadow-xs transition-all cursor-pointer shrink-0"
                    >
                      <Search className="w-3.5 h-3.5" />
                      <span>{language === "ta" ? "கண்டுபிடி" : "Search"}</span>
                    </button>
                  </form>

                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      type="button"
                      onClick={() => setShowSearchModal(true)}
                      className="inline-flex items-center gap-1.5 px-3 py-2.5 rounded-xl border border-[#CBD5E1] bg-white hover:bg-slate-50 text-xs font-semibold text-[#102A4C] shadow-2xs transition-all cursor-pointer"
                    >
                      <FolderOpen className="w-3.5 h-3.5 text-amber-600" />
                      <span>{language === "ta" ? "அனைத்தையும் காண்க" : "Browse All"}</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => fetchSavedHoroscopes()}
                      disabled={loadingSavedList}
                      title={language === "ta" ? "புதுப்பி" : "Refresh saved charts list"}
                      className="p-2.5 rounded-xl border border-[#CBD5E1] bg-white hover:bg-slate-50 text-slate-600 transition-colors cursor-pointer"
                    >
                      <RefreshCw className={`w-3.5 h-3.5 ${loadingSavedList ? "animate-spin text-amber-600" : ""}`} />
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-between text-[11px] text-[#52667E] px-0.5">
                  <span>
                    {language === "ta"
                      ? `காண்பிக்கப்படுகிறது: ${filteredHoroscopes.length} / ${savedHoroscopes.length}`
                      : `Showing ${filteredHoroscopes.length} of ${savedHoroscopes.length} charts`}
                  </span>
                  {(submittedSearchQuery || chartSearchQuery) && (
                    <button
                      type="button"
                      onClick={handleClearSearch}
                      className="text-amber-700 hover:underline font-medium cursor-pointer"
                    >
                      {language === "ta" ? "அனைத்தையும் காட்டு" : "Show all"}
                    </button>
                  )}
                </div>
              </div>

              {/* Loading chart star/paksha indicator */}
              {loadingChartDetails && (
                <div className="p-3.5 rounded-2xl bg-blue-50 border border-blue-200 text-blue-900 text-xs flex items-center gap-2">
                  <RefreshCw className="w-4 h-4 animate-spin text-blue-600 shrink-0" />
                  <span>
                    {language === "ta"
                      ? "ஜாதகரின் நட்சத்திரம் மற்றும் பக்ஷம் கணக்கிடப்படுகிறது..."
                      : "Deriving birth star and paksha from saved chart..."}
                  </span>
                </div>
              )}

              {/* Chart Load Error Notification */}
              {chartLoadError && (
                <div className="p-3 rounded-2xl bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
                    <span>{chartLoadError}</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => setChartLoadError(null)}
                    className="text-amber-800 hover:text-amber-950 font-bold cursor-pointer"
                  >
                    ✕
                  </button>
                </div>
              )}

              {/* Active Selected Saved Chart Confirmation Card */}
              {selectedChart && (
                <div className="p-4 rounded-2xl bg-[#FAF7F0] border border-amber-300 shadow-2xs space-y-3">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="flex items-start sm:items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-amber-500/15 border border-amber-300 flex items-center justify-center shrink-0 text-amber-800">
                        <User className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-bold text-sm text-[#102A4C]">
                            {selectedChart.person_name || "Client Chart"}
                          </span>
                          {selectedChart.display_number && (
                            <span className="px-1.5 py-0.5 rounded-md bg-amber-100 text-amber-800 text-[10px] font-mono font-bold">
                              #{selectedChart.display_number}
                            </span>
                          )}
                          {selectedChart.is_pinned && <span title="Pinned">📌</span>}
                        </div>
                        <div className="text-[11px] text-[#52667E] flex items-center gap-2 mt-0.5 flex-wrap">
                          <span>📅 {selectedChart.birth_date}</span>
                          <span>• ⏰ {selectedChart.birth_time}</span>
                          <span className="truncate">📍 {selectedChart.birthplace || selectedChart.location_name || `${selectedChart.latitude.toFixed(2)}, ${selectedChart.longitude.toFixed(2)}`}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 self-end sm:self-auto">
                      <button
                        type="button"
                        onClick={() => setShowSearchModal(true)}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-amber-300 bg-white hover:bg-amber-50 text-amber-900 text-xs font-semibold shadow-2xs transition-all cursor-pointer"
                      >
                        <Search className="w-3.5 h-3.5" />
                        <span>{language === "ta" ? "வேறு ஜாதகம் மாற்று" : "Change Chart"}</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setSelectedChart(null);
                          setInputMode("manual");
                        }}
                        className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-slate-500 hover:text-slate-800 text-xs transition-colors cursor-pointer"
                        title="Clear"
                      >
                        <X className="w-3.5 h-3.5" />
                        <span>{language === "ta" ? "நீக்கு" : "Clear"}</span>
                      </button>
                    </div>
                  </div>

                  {/* Derived Pancha Pakshi Particulars */}
                  <div className="pt-3 border-t border-amber-200/70 grid grid-cols-1 sm:grid-cols-3 gap-2.5 text-xs">
                    <div className="p-2.5 rounded-xl bg-white border border-amber-200/60 shadow-2xs">
                      <span className="block text-[10px] font-bold text-[#52667E] uppercase tracking-wider mb-0.5">
                        {language === "ta" ? "ஜென்ம நட்சத்திரம் (Janma Star)" : "Birth Star (Janma Nakshatra)"}
                      </span>
                      <span className="font-bold text-[#102A4C]">
                        #{birthNakshatra} {NAKSHATRAS.find((n) => n.index === birthNakshatra)?.name_en} ({NAKSHATRAS.find((n) => n.index === birthNakshatra)?.name_ta})
                      </span>
                    </div>

                    <div className="p-2.5 rounded-xl bg-white border border-amber-200/60 shadow-2xs">
                      <span className="block text-[10px] font-bold text-[#52667E] uppercase tracking-wider mb-0.5">
                        {language === "ta" ? "பிறந்த பக்ஷம் (Birth Paksha)" : "Birth Paksha"}
                      </span>
                      <span className="font-bold text-[#102A4C]">
                        {birthPaksha === "shukla"
                          ? (language === "ta" ? "வளர்பிறை (சுக்ல)" : "Waxing (Shukla)")
                          : (language === "ta" ? "தேய்பிறை (கிருஷ்ண)" : "Waning (Krishna)")}
                      </span>
                    </div>

                    <div className="p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-950 shadow-2xs">
                      <span className="block text-[10px] font-bold text-emerald-700 uppercase tracking-wider mb-0.5">
                        {language === "ta" ? "ஜென்ம பட்சி (Birth Bird)" : "Birth Bird (Janma Pakshi)"}
                      </span>
                      <span className="font-bold">
                        {data?.birth_bird?.name_ta || data?.birth_bird?.name_en || (language === "ta" ? "கணக்கிடப்படுகிறது..." : "Calculating...")}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Not Authenticated Prompt */}
              {!isAuthenticated && !authLoading && (
                <div className="p-5 rounded-2xl bg-amber-50/70 border border-amber-200 text-amber-900 text-xs flex flex-col sm:flex-row items-center justify-between gap-3">
                  <div>
                    <strong className="font-bold block">
                      {language === "ta"
                        ? "சேமிக்கப்பட்ட ஜாதகங்களைப் பார்க்க உள்நுழையவும்"
                        : "Sign in to access and search your saved client charts"}
                    </strong>
                    <span className="text-amber-800">
                      {language === "ta"
                        ? "உங்கள் கணக்கில் சேமிக்கப்பட்ட ஜாதகங்களிலிருந்து நேரடியாக நட்சத்திரம் & பக்ஷத்தை பெறலாம்."
                        : "Automatically import birth star and paksha directly from your client database."}
                    </span>
                  </div>
                  <Link
                    href="/login?redirect=/tools/pancha-pakshi"
                    className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#102A4C] text-white text-xs font-semibold shrink-0 shadow-xs"
                  >
                    <User className="w-3.5 h-3.5" />
                    <span>{language === "ta" ? "உள்நுழைக" : "Sign In"}</span>
                  </Link>
                </div>
              )}

              {/* Quick Pick Cards (if no chart is selected yet) */}
              {!selectedChart && isAuthenticated && (
                <div>
                  <div className="text-[11px] font-bold text-[#52667E] uppercase tracking-wider mb-2">
                    {language === "ta" ? "விரைவாகத் தேர்வு செய்க (அல்லது மேலே தேடவும்):" : "Quick Select (or search above):"}
                  </div>
                  {loadingSavedList ? (
                    <div className="py-8 text-center text-xs text-[#52667E] flex items-center justify-center gap-2">
                      <RefreshCw className="w-4 h-4 animate-spin text-amber-600" />
                      <span>{language === "ta" ? "ஜாதகங்கள் ஏற்றப்படுகின்றன..." : "Loading saved charts..."}</span>
                    </div>
                  ) : filteredHoroscopes.length === 0 ? (
                    <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center text-xs text-slate-600 space-y-1">
                      <p className="font-semibold">
                        {language === "ta"
                          ? `"${chartSearchQuery}" என்ற பெயரில் ஜாதகங்கள் இல்லை.`
                          : `No saved charts match "${chartSearchQuery}".`}
                      </p>
                      {chartSearchQuery && (
                        <button
                          type="button"
                          onClick={handleClearSearch}
                          className="text-amber-700 font-bold underline cursor-pointer"
                        >
                          {language === "ta" ? "தேடலை அழி" : "Clear Search"}
                        </button>
                      )}
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 max-h-56 overflow-y-auto pr-1">
                      {filteredHoroscopes.slice(0, 12).map((h) => {
                        const isSel = (selectedChart as SavedHoroscopeItem | null)?.id === h.id;
                        return (
                          <div
                            key={h.id}
                            onClick={() => handleSelectSavedChart(h)}
                            className={`p-3 rounded-xl border text-xs cursor-pointer transition-all flex items-center justify-between ${
                              isSel
                                ? "bg-[#FAF7F0] border-amber-500 ring-1 ring-amber-500/30"
                                : "hover:bg-slate-50 border-[#E2E8F0] bg-white"
                            }`}
                          >
                            <div className="min-w-0 pr-2">
                              <div className="font-bold text-[#102A4C] truncate flex items-center gap-1.5">
                                <span>{h.person_name || "Client"}</span>
                                {h.display_number && (
                                  <span className="font-mono text-[10px] text-slate-500">
                                    #{h.display_number}
                                  </span>
                                )}
                                {h.is_pinned && <span title="Pinned">📌</span>}
                              </div>
                              <div className="text-[10px] text-[#64748B] truncate mt-0.5">
                                {h.birth_date} • {h.birthplace || h.location_name || "Location"}
                              </div>
                            </div>
                            <button
                              type="button"
                              className="shrink-0 px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-[#102A4C] hover:text-white text-[#102A4C] text-[11px] font-semibold transition-all cursor-pointer"
                            >
                              {language === "ta" ? "திற" : "Open"}
                            </button>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* If Manual Selection Mode */}
          {inputMode === "manual" && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              {/* Birth Nakshatra */}
              <div>
                <label className="block text-[11px] font-bold text-[#52667E] uppercase tracking-wider mb-1">
                  {language === "ta" ? "பிறந்த நட்சத்திரம் (Janma Star)" : "Birth Star (Janma Nakshatra)"}
                </label>
                <select
                  value={birthNakshatra}
                  onChange={(e) => setBirthNakshatra(parseInt(e.target.value) || 1)}
                  className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] bg-white font-medium text-[#102A4C]"
                >
                  {NAKSHATRAS.map((nak) => (
                    <option key={nak.index} value={nak.index}>
                      #{nak.index} {nak.name_en} ({nak.name_ta})
                    </option>
                  ))}
                </select>
              </div>

              {/* Birth Paksha Toggle */}
              <div>
                <label className="block text-[11px] font-bold text-[#52667E] uppercase tracking-wider mb-1">
                  {language === "ta" ? "பிறந்த பக்ஷம் (Birth Paksha)" : "Birth Paksha"}
                </label>
                <div className="grid grid-cols-2 gap-1.5 p-1 rounded-xl bg-[#F1F5F9] border border-[#E2E8F0]">
                  <button
                    type="button"
                    onClick={() => setBirthPaksha("shukla")}
                    className={`py-1.5 rounded-lg font-bold text-xs transition-all cursor-pointer ${
                      birthPaksha === "shukla"
                        ? "bg-white text-[#102A4C] shadow-2xs"
                        : "text-[#52667E] hover:text-[#102A4C]"
                    }`}
                  >
                    {language === "ta" ? "வளர்பிறை (சுக்ல)" : "Waxing (Shukla)"}
                  </button>
                  <button
                    type="button"
                    onClick={() => setBirthPaksha("krishna")}
                    className={`py-1.5 rounded-lg font-bold text-xs transition-all cursor-pointer ${
                      birthPaksha === "krishna"
                        ? "bg-white text-[#102A4C] shadow-2xs"
                        : "text-[#52667E] hover:text-[#102A4C]"
                    }`}
                  >
                    {language === "ta" ? "தேய்பிறை (கிருஷ்ண)" : "Waning (Krishna)"}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Target Calculation Date & Location (Shared across both modes) */}
          <div className="pt-3 border-t border-[#E2E8F0] grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            {/* Target Date */}
            <div>
              <label className="block text-[11px] font-bold text-[#52667E] uppercase tracking-wider mb-1">
                {language === "ta" ? "கணிப்பு தேதி / Target Date" : "Target Calculation Date"}
              </label>
              <div className="flex items-center gap-1.5">
                <button
                  type="button"
                  onClick={() => shiftDate(-1)}
                  className="p-2 rounded-xl border border-[#DDE5F0] hover:bg-[#F8FAFC] text-[#102A4C] cursor-pointer"
                  title="Previous Day"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <DateInputDMY
                  value={dateStr}
                  onChange={(e) => setDateStr(e.target.value)}
                  className="w-full px-3 py-1.5 rounded-xl border border-[#DDE5F0] bg-white text-xs font-semibold text-[#102A4C]"
                />
                <button
                  type="button"
                  onClick={() => shiftDate(1)}
                  className="p-2 rounded-xl border border-[#DDE5F0] hover:bg-[#F8FAFC] text-[#102A4C] cursor-pointer"
                  title="Next Day"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
                <button
                  type="button"
                  onClick={resetToToday}
                  className="px-2.5 py-1.5 rounded-xl border border-[#DDE5F0] hover:bg-[#F8FAFC] text-[11px] font-semibold text-[#52667E] hover:text-[#102A4C] cursor-pointer shrink-0"
                >
                  {language === "ta" ? "இன்று" : "Today"}
                </button>
              </div>
            </div>

            {/* City Preset */}
            <div>
              <label className="block text-[11px] font-bold text-[#52667E] uppercase tracking-wider mb-1">
                {language === "ta" ? "கணிப்பு நகரம் / Location" : "Target Calculation Location"}
              </label>
              <select
                value={selectedCity.name_en}
                onChange={(e) => {
                  const found = CITY_PRESETS.find((c) => c.name_en === e.target.value);
                  if (found) handleSelectCity(found);
                }}
                className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] bg-white font-medium text-[#102A4C]"
              >
                {CITY_PRESETS.map((c) => (
                  <option key={c.name_en} value={c.name_en}>
                    {language === "ta" ? c.name_ta : c.name_en} ({c.name_en})
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Error Notification */}
        {error && (
          <div className="p-4 sm:p-5 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xs">
            <div className="flex items-start sm:items-center gap-3">
              <AlertCircle className="w-5 h-5 shrink-0 text-rose-600 mt-0.5 sm:mt-0" />
              <div>
                <strong className="font-bold">
                  {language === "ta" ? "கணிப்புப் பிழை: " : "Calculation Error: "}
                </strong>
                <span className="text-rose-700 font-medium">{error}</span>
              </div>
            </div>
            <button
              type="button"
              onClick={fetchBioRhythms}
              disabled={loading}
              className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white font-semibold text-xs transition-colors shrink-0 cursor-pointer self-start sm:self-auto"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
              <span>{language === "ta" ? "மீண்டும் முயற்சி செய்" : "Retry Calculation"}</span>
            </button>
          </div>
        )}

        {/* Loading Spinner */}
        {loading && (
          <div className="p-16 text-center space-y-3">
            <div className="w-10 h-10 border-4 border-[#3478F6] border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-xs font-semibold text-[#52667E]">
              {language === "ta"
                ? "அகத்தியர் முறைப்படி ஜாமங்கள் மற்றும் அந்தரங்கள் கணக்கிடப்படுகின்றன..."
                : "Calculating Agastya Yamams and Antara bio-rhythms..."}
            </p>
          </div>
        )}

        {!loading && data && (
          <div className="space-y-8">
            {/* 1. REAL-TIME ACTIVE BIO-RHYTHM HERO GAUGE */}
            {currentActiveAntara && currentActiveAntara.isToday && (
              <div className="p-6 sm:p-8 rounded-3xl bg-linear-to-r from-[#102A4C] via-[#16365C] to-[#1E4574] text-white shadow-xl relative overflow-hidden">
                <div className="absolute right-0 top-0 bottom-0 opacity-10 pointer-events-none flex items-center pr-8">
                  <span className="text-9xl">{data.birth_bird.symbol}</span>
                </div>

                <div className="relative z-10 space-y-6">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-white/15">
                    <div className="flex items-center gap-4">
                      <div className="w-14 h-14 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 flex items-center justify-center text-3xl shadow-inner">
                        {data.birth_bird.symbol}
                      </div>

                      <div>
                        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/20 border border-emerald-400/40 text-emerald-300 text-[10px] font-bold uppercase tracking-wider mb-1">
                          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                          <span>{language === "ta" ? "தற்போதைய நிகழ்நேர இயக்கம்" : "ACTIVE REAL-TIME STATE"}</span>
                        </div>
                        <h2 className="text-2xl sm:text-3xl font-serif font-bold text-white flex items-center gap-2">
                          <span>{data.birth_bird.name_en}</span>
                          <span className="text-amber-300 text-lg font-tamil">
                            ({data.birth_bird.name_ta})
                          </span>
                        </h2>
                        <div className="text-xs text-white/70">
                          {language === "ta" ? "பூதம்:" : "Element:"} {data.birth_bird.element_ta} ({data.birth_bird.element_en}) • {data.birth_bird.ruling_planet_ta} ({data.birth_bird.ruling_planet})
                        </div>
                      </div>
                    </div>

                    {/* Live Countdown Clock */}
                    <div className="flex items-center gap-4 bg-black/25 px-5 py-3 rounded-2xl border border-white/10 backdrop-blur-md">
                      <Timer className="w-7 h-7 text-amber-300 shrink-0" />
                      <div>
                        <div className="text-[10px] uppercase font-bold text-white/70 tracking-wider">
                          {language === "ta" ? "அந்தர நேரம் முடிவடைய" : "Time Remaining in this Antara"}
                        </div>
                        <div className="text-2xl font-mono font-bold text-amber-300">
                          {currentActiveAntara.remainingMinutes}m {currentActiveAntara.remainingSeconds < 10 ? `0${currentActiveAntara.remainingSeconds}` : currentActiveAntara.remainingSeconds}s
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Active Activity & Power Bar */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs sm:text-sm font-bold">
                      <div className="flex items-center gap-2">
                        <span className="text-white/70">{language === "ta" ? "செயல்பாடு:" : "Activity:"}</span>
                        <span className="text-amber-300 font-serif text-base sm:text-lg">
                          {currentActiveAntara.slot.major_activity_ta}ல் {currentActiveAntara.slot.sub_activity_ta} ({currentActiveAntara.slot.sub_activity_en} in {currentActiveAntara.slot.major_activity_en})
                        </span>
                      </div>
                      <div className="text-amber-300 font-mono text-base font-bold">
                        {currentActiveAntara.slot.power_score}% {language === "ta" ? "ஆற்றல்" : "Power"}
                      </div>
                    </div>

                    <div className="w-full h-3 rounded-full bg-white/10 overflow-hidden">
                      <div
                        className="h-full bg-linear-to-r from-amber-400 to-emerald-400 transition-all duration-1000 rounded-full"
                        style={{ width: `${currentActiveAntara.slot.power_score}%` }}
                      />
                    </div>

                    <div className="flex justify-between text-[11px] text-white/70 font-mono">
                      <span>{currentActiveAntara.slot.start_time_local}</span>
                      <span>{currentActiveAntara.progressPercent}% elapsed</span>
                      <span>{currentActiveAntara.slot.end_time_local}</span>
                    </div>
                  </div>

                  {/* Action Advisory Pills */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs pt-1">
                    <div className="p-4 rounded-2xl bg-white/10 border border-white/15 backdrop-blur-xs space-y-1.5">
                      <div className="flex items-center gap-1.5 text-emerald-300 font-bold uppercase tracking-wider text-[11px]">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                        <span>{language === "ta" ? "இப்போது செய்ய வேண்டியவை / Good To Do" : "Favorable Activities Right Now"}</span>
                      </div>
                      <p className="text-white/90 leading-relaxed">
                        {currentActiveAntara.slot.power_score >= 50
                          ? (language === "ta" ? currentActiveAntara.slot.recommended_ta.join(", ") : currentActiveAntara.slot.recommended_en.join(", "))
                          : (language === "ta" ? "முக்கிய முடிவுகள் எடுக்காமல் அமைதி காக்கவும், தியானம் செய்யலாம்." : "Maintain calm, avoid major signatures or conflicts.")}
                      </p>
                    </div>

                    <div className="p-4 rounded-2xl bg-white/10 border border-white/15 backdrop-blur-xs space-y-1.5">
                      <div className="flex items-center gap-1.5 text-rose-300 font-bold uppercase tracking-wider text-[11px]">
                        <XCircle className="w-4 h-4 text-rose-400" />
                        <span>{language === "ta" ? "இப்போது தவிர்க்க வேண்டியவை / Avoid" : "Activities to Avoid Right Now"}</span>
                      </div>
                      <p className="text-white/90 leading-relaxed">
                        {currentActiveAntara.slot.avoid_ta.length > 0
                          ? (language === "ta" ? currentActiveAntara.slot.avoid_ta.join(", ") : currentActiveAntara.slot.avoid_en.join(", "))
                          : (language === "ta" ? "தவறான பேச்சுவார்த்தைகளைத் தவிர்க்கவும்." : "Avoid unnecessary arguments.")}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Birth Bird Summary Metadata Card */}
            <div className="p-6 rounded-3xl bg-white border border-[#DDE5F0] shadow-xs space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-3 border-b border-[#F1F5F9]">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{data.birth_bird.symbol}</span>
                  <div>
                    <h3 className="font-serif text-lg font-bold text-[#102A4C]">
                      {data.birth_bird.name_en} ({data.birth_bird.name_ta})
                    </h3>
                    <p className="text-xs text-[#52667E]">
                      {language === "ta" ? "உங்களது உயிர் பட்சி (Janma Pakshi)" : "Your Native Birth Bird"} • {data.astronomical.target_paksha_ta} ({data.astronomical.target_paksha.toUpperCase()})
                    </p>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-2 text-xs">
                  <span className="px-3 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 font-bold">
                    {data.total_golden_windows} {language === "ta" ? "தங்கத் தருணங்கள்" : "Golden Windows"}
                  </span>
                  <span className="px-3 py-1 rounded-full bg-rose-50 text-rose-800 border border-rose-200 font-bold">
                    {data.total_padupakshi_windows} {language === "ta" ? "படுபட்சி காலங்கள்" : "Padupakshi Hours"}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3 text-xs">
                <div className="p-3 rounded-xl bg-[#FAF8F5] border border-[#E2E8F0]">
                  <span className="text-[10px] text-[#8C6D23] font-bold uppercase block">பூதம் (Element)</span>
                  <strong className="text-sm text-[#102A4C] block mt-0.5">{data.birth_bird.element_ta}</strong>
                  <span className="text-[10px] text-[#52667E]">{data.birth_bird.element_en}</span>
                </div>

                <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                  <span className="text-[10px] text-[#52667E] font-bold uppercase block">கிரகம் (Graha)</span>
                  <strong className="text-sm text-[#102A4C] block mt-0.5">{data.birth_bird.ruling_planet_ta}</strong>
                  <span className="text-[10px] text-[#52667E]">{data.birth_bird.ruling_planet}</span>
                </div>

                <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                  <span className="text-[10px] text-[#52667E] font-bold uppercase block">திசை (Direction)</span>
                  <strong className="text-sm text-[#102A4C] block mt-0.5">{data.birth_bird.lucky_direction_ta}</strong>
                  <span className="text-[10px] text-[#52667E]">{data.birth_bird.lucky_direction}</span>
                </div>

                <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                  <span className="text-[10px] text-[#52667E] font-bold uppercase block">வண்ணம் (Color)</span>
                  <strong className="text-sm text-[#102A4C] block mt-0.5">{data.birth_bird.lucky_color_ta}</strong>
                  <span className="text-[10px] text-[#52667E]">{data.birth_bird.lucky_color}</span>
                </div>

                <div className="p-3 rounded-xl bg-emerald-50/50 border border-emerald-200">
                  <span className="text-[10px] text-emerald-800 font-bold uppercase block">நட்பு பட்சி (Friend)</span>
                  <strong className="text-sm text-emerald-950 block mt-0.5">{data.birth_bird.friendly_birds_ta.join(", ")}</strong>
                  <span className="text-[10px] text-emerald-700">{data.birth_bird.friendly_birds.join(", ")}</span>
                </div>

                <div className="p-3 rounded-xl bg-rose-50/50 border border-rose-200">
                  <span className="text-[10px] text-rose-800 font-bold uppercase block">பகை பட்சி (Enemy)</span>
                  <strong className="text-sm text-rose-950 block mt-0.5">{data.birth_bird.inimical_birds_ta.join(", ")}</strong>
                  <span className="text-[10px] text-rose-700">{data.birth_bird.inimical_birds.join(", ")}</span>
                </div>
              </div>
            </div>

            {/* Navigation Studio Tabs */}
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-[#DDE5F0] pb-3">
              <div className="flex items-center gap-2">
                {[
                  { id: "timeline", en: "50-Interval Bio-Rhythm Timeline", ta: "முழு நாள் 50 அந்தர கால அட்டவணை", icon: Clock },
                  { id: "golden", en: `Golden Windows (${data.total_golden_windows})`, ta: `தங்க வெற்றித் தருணங்கள் (${data.total_golden_windows})`, icon: Zap },
                  { id: "padupakshi", en: `Padupakshi Hours (${data.total_padupakshi_windows})`, ta: `படுபட்சி எச்சரிக்கை (${data.total_padupakshi_windows})`, icon: ShieldAlert },
                  { id: "lore", en: "Agastya Pancha Pakshi Lore", ta: "அகத்தியர் பட்சி தத்துவங்கள்", icon: Info },
                ].map((tab) => {
                  const Icon = tab.icon;
                  const isActive = activeTab === tab.id;
                  return (
                    <button
                      key={tab.id}
                      type="button"
                      onClick={() => setActiveTab(tab.id as any)}
                      className={`inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all cursor-pointer ${
                        isActive
                          ? "bg-[#102A4C] text-white shadow-xs"
                          : "bg-white text-[#52667E] hover:bg-[#F1F5F9] border border-[#DDE5F0]"
                      }`}
                    >
                      <Icon className={`w-4 h-4 ${isActive ? "text-amber-300" : "text-[#52667E]"}`} />
                      <span>{language === "ta" ? tab.ta : tab.en}</span>
                    </button>
                  );
                })}
              </div>

              {/* Filter for Timeline Tab */}
              {activeTab === "timeline" && (
                <div className="flex items-center gap-1 text-xs">
                  <span className="font-bold text-[#52667E] mr-1">{language === "ta" ? "காட்சி:" : "Filter:"}</span>
                  <button
                    type="button"
                    onClick={() => setTimelineFilter("all")}
                    className={`px-2.5 py-1 rounded-lg font-medium transition-all cursor-pointer ${
                      timelineFilter === "all" ? "bg-[#102A4C] text-white" : "bg-white border text-[#52667E]"
                    }`}
                  >
                    All (50)
                  </button>
                  <button
                    type="button"
                    onClick={() => setTimelineFilter("day")}
                    className={`px-2.5 py-1 rounded-lg font-medium transition-all cursor-pointer ${
                      timelineFilter === "day" ? "bg-amber-600 text-white" : "bg-white border text-amber-700"
                    }`}
                  >
                    Day (25)
                  </button>
                  <button
                    type="button"
                    onClick={() => setTimelineFilter("night")}
                    className={`px-2.5 py-1 rounded-lg font-medium transition-all cursor-pointer ${
                      timelineFilter === "night" ? "bg-indigo-600 text-white" : "bg-white border text-indigo-700"
                    }`}
                  >
                    Night (25)
                  </button>
                </div>
              )}
            </div>

            {/* TAB 1: 50-INTERVAL BIO-RHYTHM TIMELINE */}
            {activeTab === "timeline" && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-3.5">
                  {filteredAntaras.map((antara) => {
                    const isCurrent =
                      currentActiveAntara?.isToday &&
                      currentActiveAntara.slot.global_sub_index === antara.global_sub_index &&
                      currentActiveAntara.slot.period_type === antara.period_type;

                    const isGolden = antara.power_score >= 80;
                    const isDanger = antara.power_score <= 25;

                    return (
                      <div
                        key={`${antara.period_type}-${antara.global_sub_index}`}
                        onClick={() => setSelectedAntaraModal(antara)}
                        className={`p-4 rounded-2xl border transition-all cursor-pointer relative overflow-hidden group hover:shadow-md space-y-2 ${
                          isCurrent
                            ? "bg-amber-50/90 border-amber-400 ring-2 ring-amber-400 shadow-md"
                            : isGolden
                            ? "bg-emerald-50/40 border-emerald-300 hover:border-emerald-400"
                            : isDanger
                            ? "bg-rose-50/40 border-rose-300 hover:border-rose-400"
                            : "bg-white border-[#DDE5F0] hover:border-[#3478F6]/40"
                        }`}
                      >
                        {isCurrent && (
                          <div className="absolute top-0 right-0 bg-amber-500 text-white text-[9px] uppercase font-bold px-2 py-0.5 rounded-bl-lg">
                            ACTIVE
                          </div>
                        )}

                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-mono text-[#52667E]">
                            #{antara.global_sub_index} • {antara.period_type === "day" ? "Day" : "Night"}
                          </span>
                          <span
                            className="text-xs font-bold px-2 py-0.5 rounded-full font-mono"
                            style={{
                              backgroundColor: `${antara.color}15`,
                              color: antara.color,
                            }}
                          >
                            {antara.power_score}%
                          </span>
                        </div>

                        <div>
                          <h4 className="font-serif font-bold text-sm text-[#102A4C] group-hover:text-[#3478F6] transition-colors">
                            {antara.sub_activity_ta} ({antara.sub_activity_en})
                          </h4>
                          <div className="text-[11px] text-[#52667E]">
                            {antara.major_activity_ta}ல் {antara.sub_activity_ta}
                          </div>
                        </div>

                        <div className="pt-2 border-t border-[#F1F5F9] flex items-center justify-between text-[11px] font-mono text-[#102A4C] font-semibold">
                          <span>{antara.start_time_local.slice(0, 5)}</span>
                          <span>—</span>
                          <span>{antara.end_time_local.slice(0, 5)}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* TAB 2: GOLDEN ACTION WINDOWS */}
            {activeTab === "golden" && (
              <div className="p-6 sm:p-8 rounded-3xl bg-white border border-[#DDE5F0] space-y-6">
                <div>
                  <h3 className="font-serif text-xl font-bold text-[#102A4C] flex items-center gap-2">
                    <Zap className="w-5 h-5 text-amber-500" />
                    <span>{language === "ta" ? "தங்க வெற்றித் தருணங்கள் (Golden Victory Windows)" : "Golden Action Windows"}</span>
                  </h3>
                  <p className="text-xs text-[#52667E] mt-0.5">
                    {language === "ta"
                      ? "80% முதல் 100% பிராண சக்தி வாய்ந்த நேரங்கள். முக்கிய ஒப்பந்தங்கள், புதிய துவக்கம் மற்றும் அரச காரியங்களுக்கு உத்தமம்."
                      : "Peak bio-rhythm windows (80% to 100% vitality). Optimal for contracts, major financial moves, and leadership."}
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {data.golden_windows.map((win) => (
                    <div
                      key={`${win.period_type}-${win.global_sub_index}`}
                      className="p-5 rounded-2xl bg-emerald-50/60 border border-emerald-300 space-y-3"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-serif text-base font-bold text-emerald-950">
                          {win.sub_activity_ta} ({win.sub_activity_en})
                        </span>
                        <span className="px-2.5 py-0.5 rounded-full bg-emerald-600 text-white font-mono font-bold text-xs">
                          {win.power_score}%
                        </span>
                      </div>

                      <div className="font-mono text-xs font-bold text-[#102A4C] bg-white/70 p-2 rounded-xl border border-emerald-200">
                        {win.start_time_local} — {win.end_time_local} ({win.duration_minutes} mins)
                      </div>

                      <div className="text-xs text-emerald-900 space-y-1">
                        <div className="font-bold text-[11px] uppercase tracking-wider text-emerald-800">
                          {language === "ta" ? "உத்தம பலன்கள்:" : "Favorable for:"}
                        </div>
                        <ul className="space-y-0.5 pl-2">
                          {(language === "ta" ? win.recommended_ta : win.recommended_en).map((rec, i) => (
                            <li key={i} className="flex items-center gap-1.5">
                              <span className="text-emerald-600 font-bold">✓</span>
                              <span>{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB 3: PADUPAKSHI CAUTION ALERT */}
            {activeTab === "padupakshi" && (
              <div className="p-6 sm:p-8 rounded-3xl bg-white border border-[#DDE5F0] space-y-6">
                <div>
                  <h3 className="font-serif text-xl font-bold text-rose-900 flex items-center gap-2">
                    <ShieldAlert className="w-5 h-5 text-rose-600" />
                    <span>{language === "ta" ? "படுபட்சி எச்சரிக்கை காலங்கள் (Padupakshi Caution Hours)" : "Padupakshi Warning Periods"}</span>
                  </h3>
                  <p className="text-xs text-[#52667E] mt-0.5">
                    {language === "ta"
                      ? "பிராண சக்தி குறைந்த நேரங்கள் (0% முதல் 25%). புதிய காரியங்கள், அறுவை சிகிச்சை, கடன் கொடுத்தல் மற்றும் விவாதங்களைத் தவிர்க்கவும்."
                      : "Critical low-vitality windows (0% to 25% energy). Strictly avoid starting new ventures, high-stakes decisions, or surgery."}
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {data.padupakshi_windows.map((win) => (
                    <div
                      key={`${win.period_type}-${win.global_sub_index}`}
                      className="p-5 rounded-2xl bg-rose-50/60 border border-rose-300 space-y-3"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-serif text-base font-bold text-rose-950">
                          {win.sub_activity_ta} ({win.sub_activity_en})
                        </span>
                        <span className="px-2.5 py-0.5 rounded-full bg-rose-600 text-white font-mono font-bold text-xs">
                          {win.power_score}%
                        </span>
                      </div>

                      <div className="font-mono text-xs font-bold text-[#102A4C] bg-white/70 p-2 rounded-xl border border-rose-200">
                        {win.start_time_local} — {win.end_time_local} ({win.duration_minutes} mins)
                      </div>

                      <div className="text-xs text-rose-900 space-y-1">
                        <div className="font-bold text-[11px] uppercase tracking-wider text-rose-800">
                          {language === "ta" ? "கட்டாயம் தவிர்க்கவும்:" : "Strictly Avoid:"}
                        </div>
                        <p className="text-[11px] text-rose-800 leading-relaxed">
                          {language === "ta"
                            ? "முக்கிய ஆவணக் கையெழுத்து, மருத்துவ சிகிச்சை, பயணம், வாக்குவாதங்கள் தவிர்க்கப்பட வேண்டும்."
                            : "Contract signings, travel, contentious debates, and aggressive confrontations."}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB 4: AGASTYA LORE & PRINCIPLES */}
            {activeTab === "lore" && (
              <div className="p-6 sm:p-8 rounded-3xl bg-white border border-[#DDE5F0] space-y-6">
                <div>
                  <h3 className="font-serif text-xl font-bold text-[#102A4C]">
                    {language === "ta" ? "அகத்தியர் பஞ்ச பட்சி சாஸ்திர தத்துவங்கள்" : "Sage Agastya's Pancha Pakshi Siddha Philosophy"}
                  </h3>
                  <p className="text-xs text-[#52667E] mt-0.5">
                    {language === "ta"
                      ? "ஐந்து பட்சிகள், பஞ்ச பூதங்கள் மற்றும் அன்றாட வாழ்வியல் வழிகாட்டுதல்கள்."
                      : "The biological correspondence between the 5 cosmic birds, 5 elements, and dynamic human energy."}
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs text-[#52667E] leading-relaxed">
                  <div className="p-5 rounded-2xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-3">
                    <h4 className="font-serif font-bold text-sm text-[#102A4C]">
                      {language === "ta" ? "1. பஞ்ச பட்சி சாஸ்திரம் என்றால் என்ன?" : "1. What is Pancha Pakshi Shastra?"}
                    </h4>
                    <p>
                      Conceived by the venerated Tamil Siddha <strong>Sage Agastya</strong>, Pancha Pakshi Shastra assigns every human being one of five sacred birds (Vulture, Owl, Crow, Cock, Peacock) based on the Janma Nakshatra and the Moon&apos;s lunar phase (Shukla / Krishna Paksha).
                    </p>
                    <p>
                      Each bird embodies one of the Five Great Elements (Pancha Bhutas):
                    </p>
                    <ul className="list-disc pl-4 space-y-1">
                      <li><strong>Vulture (வல்லூறு)</strong> — Ether / Space (ஆகாயம்)</li>
                      <li><strong>Owl (ஆந்தை)</strong> — Air (காற்று)</li>
                      <li><strong>Crow (காகம்)</strong> — Fire (நெருப்பு)</li>
                      <li><strong>Cock (கோழி)</strong> — Water (நீர்)</li>
                      <li><strong>Peacock (மயில்)</strong> — Earth (நிலம்)</li>
                    </ul>
                  </div>

                  <div className="p-5 rounded-2xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-3">
                    <h4 className="font-serif font-bold text-sm text-[#102A4C]">
                      {language === "ta" ? "2. ஐந்து தொழில்களின் ஆற்றல் படிநிலை" : "2. Hierarchical Order of the 5 Activities"}
                    </h4>
                    <div className="space-y-2">
                      <div className="p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-between text-emerald-950 font-bold">
                        <span>1. அரசு (Ruling / Arasu)</span>
                        <span>100% Power (Supreme Victory)</span>
                      </div>
                      <div className="p-2.5 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-between text-blue-950 font-bold">
                        <span>2. ஊண் (Eating / Oon)</span>
                        <span>80% Power (Prosperity & Joy)</span>
                      </div>
                      <div className="p-2.5 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-between text-amber-950 font-bold">
                        <span>3. நடை (Walking / Nadai)</span>
                        <span>50% Power (Movement & Commute)</span>
                      </div>
                      <div className="p-2.5 rounded-xl bg-purple-50 border border-purple-200 flex items-center justify-between text-purple-950 font-bold">
                        <span>4. துயில் (Sleeping / Thuyil)</span>
                        <span>20% Power (Rest & Reflection)</span>
                      </div>
                      <div className="p-2.5 rounded-xl bg-rose-50 border border-rose-200 flex items-center justify-between text-rose-950 font-bold">
                        <span>5. சாவு (Dying / Saavu)</span>
                        <span>0% Power (Padupakshi / Prohibited)</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* DETAIL MODAL FOR CLICKED ANTARA SLOT */}
      {selectedAntaraModal && (
        <div
          className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4"
          onClick={() => setSelectedAntaraModal(null)}
        >
          <div
            className="w-full max-w-lg bg-white rounded-3xl p-6 sm:p-8 space-y-5 shadow-2xl border border-[#DDE5F0]"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between pb-4 border-b border-[#F1F5F9]">
              <div>
                <span className="text-[10px] uppercase font-bold text-[#52667E] tracking-wider">
                  Antara #{selectedAntaraModal.global_sub_index} • {selectedAntaraModal.period_type === "day" ? "Daytime" : "Nighttime"}
                </span>
                <h3 className="text-xl font-serif font-bold text-[#102A4C]">
                  {selectedAntaraModal.major_activity_ta}ல் {selectedAntaraModal.sub_activity_ta} ({selectedAntaraModal.sub_activity_en})
                </h3>
              </div>

              <button
                type="button"
                onClick={() => setSelectedAntaraModal(null)}
                className="w-8 h-8 rounded-xl bg-[#F1F5F9] hover:bg-[#E2E8F0] text-[#52667E] flex items-center justify-center font-bold cursor-pointer"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] flex items-center justify-between font-medium">
                <span>{language === "ta" ? "நேர அளவு:" : "Time Window:"}</span>
                <span className="font-mono font-bold text-[#102A4C]">
                  {selectedAntaraModal.start_time_local} — {selectedAntaraModal.end_time_local} ({selectedAntaraModal.duration_minutes} min)
                </span>
              </div>

              <div className="p-3 rounded-xl bg-[#FAF8F5] border border-[#E2E8F0] flex items-center justify-between font-medium">
                <span>{language === "ta" ? "ஆற்றல் நிலை:" : "Vitality Score:"}</span>
                <span className="font-mono font-bold text-base text-amber-700">
                  {selectedAntaraModal.power_score}% ({selectedAntaraModal.rating_label_ta})
                </span>
              </div>

              {selectedAntaraModal.recommended_ta.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-bold text-emerald-800 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    <span>{language === "ta" ? "உத்தம காரியங்கள்" : "Recommended Activities"}</span>
                  </h4>
                  <ul className="space-y-1 pl-2 text-[#52667E]">
                    {(language === "ta" ? selectedAntaraModal.recommended_ta : selectedAntaraModal.recommended_en).map((item, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-emerald-500 font-bold">✓</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {selectedAntaraModal.avoid_ta.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-bold text-rose-800 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                    <XCircle className="w-4 h-4 text-rose-600" />
                    <span>{language === "ta" ? "தவிர்க்க வேண்டியவை" : "Avoid"}</span>
                  </h4>
                  <ul className="space-y-1 pl-2 text-[#52667E]">
                    {(language === "ta" ? selectedAntaraModal.avoid_ta : selectedAntaraModal.avoid_en).map((item, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-rose-500 font-bold">✗</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div className="pt-2">
              <button
                type="button"
                onClick={() => setSelectedAntaraModal(null)}
                className="w-full py-2.5 rounded-xl bg-[#102A4C] hover:bg-[#16365C] text-white font-bold text-xs transition-colors cursor-pointer"
              >
                {language === "ta" ? "மூடு" : "Close"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Saved Chart Search Modal with Manual Search Button */}
      {showSearchModal && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-150"
          onClick={() => setShowSearchModal(false)}
        >
          <div
            className="w-full max-w-2xl bg-white rounded-3xl shadow-2xl border border-[#DDE5F0] overflow-hidden flex flex-col max-h-[90vh]"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="px-5 py-4 bg-[#102A4C] text-white flex items-center justify-between shadow-xs shrink-0">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-white/10 flex items-center justify-center text-amber-300 font-bold">
                  <FolderOpen className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold flex items-center gap-2">
                    <span>
                      {language === "ta"
                        ? "சேமித்த ஜாதகத்தைத் தேடி திறக்கவும்"
                        : "Open Saved Client Chart"}
                    </span>
                    <span className="text-[11px] font-normal px-2 py-0.5 rounded-full bg-white/20">
                      {savedHoroscopes.length} {language === "ta" ? "ஜாதகங்கள்" : "charts"}
                    </span>
                  </h3>
                  <p className="text-xs text-white/80">
                    {language === "ta"
                      ? "ஜாதகரைத் தேர்ந்தெடுத்து பஞ்ச பட்சி கணிப்பை உடனடியாகப் பெறவும்"
                      : "Select a client chart to automatically load birth star, paksha, and rhythms"}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setShowSearchModal(false)}
                className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition cursor-pointer"
                title={language === "ta" ? "மூடு" : "Close"}
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Modal Search Bar with Manual Search Button */}
            <div className="p-4 border-b border-[#DDE5F0] bg-[#FAF8F5]">
              <form onSubmit={handleManualSearch} className="flex items-center gap-2">
                <div className="relative flex-1">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                  <input
                    type="text"
                    autoFocus
                    value={chartSearchQuery}
                    onChange={(e) => setChartSearchQuery(e.target.value)}
                    placeholder={
                      language === "ta"
                        ? "ஜாதகர் பெயர், ஊர், பிறந்த தேதி (YYYY-MM-DD), எண் மூலம் தேடுக..."
                        : "Search by client name, place, date (YYYY-MM-DD), or chart #..."
                    }
                    className="w-full text-xs pl-9 pr-8 py-2.5 border border-[#CBD5E1] rounded-xl outline-none focus:ring-2 focus:ring-[#102A4C] bg-white text-[#102A4C]"
                  />
                  {chartSearchQuery && (
                    <button
                      type="button"
                      onClick={handleClearSearch}
                      className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-0.5 cursor-pointer"
                      title="Clear"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                {/* Manual Search Button */}
                <button
                  type="submit"
                  className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-[#102A4C] hover:bg-[#16365C] text-white text-xs font-semibold shadow-xs transition-all cursor-pointer shrink-0"
                >
                  <Search className="w-3.5 h-3.5" />
                  <span>{language === "ta" ? "கண்டுபிடி" : "Search"}</span>
                </button>

                <button
                  type="button"
                  onClick={() => fetchSavedHoroscopes()}
                  disabled={loadingSavedList}
                  title={language === "ta" ? "புதுப்பி" : "Refresh List"}
                  className="p-2.5 rounded-xl border border-[#CBD5E1] bg-white hover:bg-slate-50 text-slate-600 transition-colors cursor-pointer shrink-0"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${loadingSavedList ? "animate-spin text-amber-600" : ""}`} />
                </button>
              </form>

              <div className="flex items-center justify-between text-[11px] text-[#52667E] mt-2 px-1">
                <span>
                  {language === "ta"
                    ? `காண்பிக்கப்படுகிறது: ${filteredHoroscopes.length} / ${savedHoroscopes.length}`
                    : `Showing ${filteredHoroscopes.length} of ${savedHoroscopes.length} charts`}
                </span>
                {(submittedSearchQuery || chartSearchQuery) && (
                  <button
                    type="button"
                    onClick={handleClearSearch}
                    className="text-amber-700 hover:underline font-medium cursor-pointer"
                  >
                    {language === "ta" ? "அனைத்தையும் காட்டு" : "Show all"}
                  </button>
                )}
              </div>
            </div>

            {/* Modal Charts List */}
            <div className="overflow-y-auto p-4 space-y-2 flex-1 max-h-[55vh]">
              {!isAuthenticated ? (
                <div className="p-6 text-center space-y-3">
                  <p className="text-xs text-[#52667E]">
                    {language === "ta"
                      ? "சேமிக்கப்பட்ட ஜாதகங்களைத் தேட உள்நுழைய வேண்டும்."
                      : "Please sign in to view and search your saved client charts."}
                  </p>
                  <Link
                    href="/login?redirect=/tools/pancha-pakshi"
                    className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#102A4C] text-white text-xs font-semibold shadow-xs"
                  >
                    <User className="w-3.5 h-3.5" />
                    <span>{language === "ta" ? "உள்நுழைக" : "Sign In"}</span>
                  </Link>
                </div>
              ) : loadingSavedList ? (
                <div className="py-12 text-center space-y-2">
                  <RefreshCw className="w-6 h-6 animate-spin text-amber-600 mx-auto" />
                  <p className="text-xs text-[#52667E]">
                    {language === "ta" ? "ஜாதகங்கள் ஏற்றப்படுகின்றன..." : "Loading saved charts..."}
                  </p>
                </div>
              ) : filteredHoroscopes.length === 0 ? (
                <div className="py-12 text-center space-y-2">
                  <Database className="w-8 h-8 text-slate-300 mx-auto" />
                  <p className="text-xs font-semibold text-[#102A4C]">
                    {language === "ta"
                      ? `"${chartSearchQuery}" என்ற பெயரில் ஜாதகங்கள் இல்லை`
                      : `No saved charts found matching "${chartSearchQuery}"`}
                  </p>
                  <p className="text-[11px] text-[#52667E]">
                    {language === "ta"
                      ? "தேடல் சொல்லை மாற்றி அல்லது அழித்து முயற்சிக்கவும்."
                      : "Try a different search term or clear the search filter."}
                  </p>
                  {chartSearchQuery && (
                    <button
                      type="button"
                      onClick={handleClearSearch}
                      className="mt-2 text-xs font-semibold text-amber-700 underline cursor-pointer"
                    >
                      {language === "ta" ? "தேடலை அழி" : "Clear Search"}
                    </button>
                  )}
                </div>
              ) : (
                filteredHoroscopes.map((h) => {
                  const isSelected = selectedChart?.id === h.id;
                  return (
                    <div
                      key={h.id}
                      onClick={() => handleSelectSavedChart(h)}
                      className={`p-3 rounded-2xl border text-left cursor-pointer transition-all flex items-center justify-between gap-3 ${
                        isSelected
                          ? "bg-[#FAF7F0] border-amber-500 ring-2 ring-amber-500/20"
                          : "hover:bg-slate-50 border-[#E2E8F0] bg-white"
                      }`}
                    >
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <strong className="text-xs font-bold text-[#102A4C] truncate">
                            {h.person_name || "Unnamed Chart"}
                          </strong>
                          {h.display_number && (
                            <span className="font-mono text-[10px] font-bold px-1.5 py-0.2 rounded bg-slate-100 text-slate-700 border border-slate-200">
                              #{h.display_number}
                            </span>
                          )}
                          {h.is_pinned && <span title="Pinned">📌</span>}
                        </div>
                        <div className="text-[11px] text-[#52667E] flex items-center gap-2 mt-1 truncate">
                          <span>📅 {h.birth_date}</span>
                          <span>⏰ {h.birth_time}</span>
                          <span className="truncate">📍 {h.birthplace || h.location_name || `${h.latitude}, ${h.longitude}`}</span>
                        </div>
                      </div>

                      <div className="shrink-0 flex items-center gap-2">
                        {isSelected ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 text-[11px] font-bold">
                            <Check className="w-3.5 h-3.5" />
                            <span>{language === "ta" ? "தேர்வு செய்யப்பட்டுள்ளது" : "Active"}</span>
                          </span>
                        ) : (
                          <button
                            type="button"
                            className="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-[#102A4C] hover:text-white text-slate-700 text-xs font-semibold transition-all cursor-pointer"
                          >
                            {language === "ta" ? "திற" : "Open"}
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-3 bg-slate-50 border-t border-[#DDE5F0] flex items-center justify-between text-xs text-[#52667E]">
              <span>
                {language === "ta"
                  ? "விசைப்பலகை: Esc மூடலாம் • Enter தேடலாம்"
                  : "Keyboard: Press Esc to close • Enter to search"}
              </span>
              <button
                type="button"
                onClick={() => setShowSearchModal(false)}
                className="px-3 py-1.5 rounded-lg border border-[#CBD5E1] bg-white hover:bg-slate-100 text-[#102A4C] font-semibold cursor-pointer"
              >
                {language === "ta" ? "மூடு" : "Close"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function PanchaPakshiPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-[#F4F6F9]">
          <div className="w-8 h-8 border-4 border-[#3478F6] border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <PanchaPakshiStudioInner />
    </Suspense>
  );
}
