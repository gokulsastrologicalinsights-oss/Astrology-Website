"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { formatSerialNumber } from "@/lib/formatters";
import {
  Search,
  X,
  Compass,
  Sparkles,
  Database,
  Calendar,
  Grid3X3,
  Layers,
  Heart,
  FileText,
  Clock,
  ArrowRight,
  Loader2,
} from "lucide-react";

interface FeatureItem {
  id: string;
  titleEn: string;
  titleTa: string;
  categoryEn: string;
  categoryTa: string;
  href: string;
  icon: any;
  color: string;
}

const STATIC_FEATURES: FeatureItem[] = [
  {
    id: "create-horoscope",
    titleEn: "Create Horoscope Form",
    titleTa: "ஜாதகம் கணிக்க",
    categoryEn: "Horoscope / KP System",
    categoryTa: "ஜாதகம் மற்றும் கே.பி. ஜோதிடம்",
    href: "/horoscope",
    icon: Compass,
    color: "text-[#B8862B] bg-[#FAF2DE]",
  },
  {
    id: "saved-horoscopes",
    titleEn: "Saved Horoscopes List",
    titleTa: "சேமிக்கப்பட்ட ஜாதகங்கள்",
    categoryEn: "Horoscope / KP System",
    categoryTa: "ஜாதகம் மற்றும் கே.பி. ஜோதிடம்",
    href: "/tools/horoscope?tab=saved",
    icon: Database,
    color: "text-[#B8862B] bg-[#FAF2DE]",
  },
  {
    id: "kp-astrology",
    titleEn: "KP Astrology & Sub-Lords",
    titleTa: "கே.பி. ஜோதிடம் & உப-அதிபதிகள்",
    categoryEn: "Horoscope / KP System",
    categoryTa: "ஜாதகம் மற்றும் கே.பி. ஜோதிடம்",
    href: "/horoscope/results?tab=kp",
    icon: Layers,
    color: "text-[#B8862B] bg-[#FAF2DE]",
  },
  {
    id: "dasa-timeline",
    titleEn: "Vimshottari Dasa-Bhukti Timeline",
    titleTa: "விம்சோத்தரி தசா-புக்தி காலவரிசை",
    categoryEn: "Horoscope / KP System",
    categoryTa: "ஜாதகம் மற்றும் கே.பி. ஜோதிடம்",
    href: "/horoscope/results?tab=dasa",
    icon: Clock,
    color: "text-[#B8862B] bg-[#FAF2DE]",
  },
  {
    id: "horoscope-analysis",
    titleEn: "Horoscope Planetary Analysis",
    titleTa: "ஜாதக கிரக நிலை பகுப்பாய்வு",
    categoryEn: "Horoscope / KP System",
    categoryTa: "ஜாதகம் மற்றும் கே.பி. ஜோதிடம்",
    href: "/horoscope/results?tab=planets",
    icon: Compass,
    color: "text-[#B8862B] bg-[#FAF2DE]",
  },
  {
    id: "numerology-calc",
    titleEn: "Numerology Core Calculator",
    titleTa: "பாரம்பரிய எண் கணித கால்குலேட்டர்",
    categoryEn: "Numerology",
    categoryTa: "எண் கணிதம்",
    href: "/numerology/traditional",
    icon: Sparkles,
    color: "text-[#3478F6] bg-[#EBF2FE]",
  },
  {
    id: "name-numerology",
    titleEn: "Name Numerology & Spelling Compare",
    titleTa: "பெயர் எண் & மாற்று எழுத்து ஒப்பீடு",
    categoryEn: "Numerology",
    categoryTa: "எண் கணிதம்",
    href: "/tools/numerology?tab=name",
    icon: FileText,
    color: "text-[#3478F6] bg-[#EBF2FE]",
  },
  {
    id: "driver-destiny",
    titleEn: "Birth Number & Life Path Number",
    titleTa: "பிறப்பு எண் & விதி எண்",
    categoryEn: "Numerology",
    categoryTa: "எண் கணிதம்",
    href: "/numerology/traditional",
    icon: Calendar,
    color: "text-[#3478F6] bg-[#EBF2FE]",
  },
  {
    id: "destiny-matrix",
    titleEn: "22 Arcana Destiny Matrix",
    titleTa: "22 ஆர்கானா விதி வரைபடம்",
    categoryEn: "Numerology",
    categoryTa: "எண் கணிதம்",
    href: "/numerology/destiny-matrix",
    icon: Sparkles,
    color: "text-[#3478F6] bg-[#EBF2FE]",
  },
  {
    id: "lo-shu-grid",
    titleEn: "Lo Shu 3x3 Magic Square & Arrows",
    titleTa: "லோ-ஷூ 3x3 கட்டம் & 8 அம்புகள்",
    categoryEn: "Numerology",
    categoryTa: "எண் கணிதம்",
    href: "/numerology/advanced",
    icon: Grid3X3,
    color: "text-[#3478F6] bg-[#EBF2FE]",
  },
  {
    id: "compatibility",
    titleEn: "Numerology Compatibility",
    titleTa: "எண் கணித பொருத்தம்",
    categoryEn: "Numerology",
    categoryTa: "எண் கணிதம்",
    href: "/tools/numerology?tab=compatibility",
    icon: Heart,
    color: "text-[#3478F6] bg-[#EBF2FE]",
  },
];

interface SavedHoroscopeResult {
  id: string;
  display_number: number;
  person_name: string;
  birth_date: string;
  birthplace: string;
}

export function HeaderSearch() {
  const router = useRouter();
  const { language, t } = useLanguage();
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [savedResults, setSavedResults] = useState<SavedHoroscopeResult[]>([]);
  const [isSearchingSaved, setIsSearchingSaved] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Filter static features
  const filteredFeatures = query.trim()
    ? STATIC_FEATURES.filter((f) => {
        const q = query.toLowerCase();
        return (
          f.titleEn.toLowerCase().includes(q) ||
          f.titleTa.toLowerCase().includes(q) ||
          f.categoryEn.toLowerCase().includes(q) ||
          f.categoryTa.toLowerCase().includes(q)
        );
      })
    : [];

  // Query saved horoscopes from Supabase when query has 2+ characters
  const fetchSavedHoroscopes = useCallback(async (q: string) => {
    if (!q || q.trim().length < 2) {
      setSavedResults([]);
      setIsSearchingSaved(false);
      return;
    }

    setIsSearchingSaved(true);
    try {
      const res = await fetch(`/api/horoscopes?search=${encodeURIComponent(q)}&limit=4`);
      if (res.ok) {
        const data = await res.json();
        setSavedResults(data.horoscopes || []);
      } else {
        setSavedResults([]);
      }
    } catch {
      setSavedResults([]);
    } finally {
      setIsSearchingSaved(false);
    }
  }, []);

  const handleQueryChange = (val: string) => {
    setQuery(val);
    setIsOpen(true);

    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    searchTimeoutRef.current = setTimeout(() => {
      fetchSavedHoroscopes(val);
    }, 300);
  };

  // Close when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Keyboard shortcut Ctrl+K or / to focus search
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        inputRef.current?.focus();
        setIsOpen(true);
      } else if (e.key === "Escape") {
        setIsOpen(false);
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleSelect = (href: string) => {
    setIsOpen(false);
    setQuery("");
    router.push(href);
  };

  return (
    <div ref={dropdownRef} className="relative w-full max-w-xs sm:max-w-sm md:max-w-md">
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => handleQueryChange(e.target.value)}
          onFocus={() => setIsOpen(true)}
          placeholder={t.searchPlaceholder || "Search tools or saved charts..."}
          className="w-full pl-9 pr-8 py-1.5 rounded-xl border border-[#DDE5F0] bg-[#F8FAFC] focus:bg-white text-xs text-[#102A4C] placeholder:text-[#94A3B8] focus:border-[#3478F6] focus:ring-1 focus:ring-[#3478F6] transition-all"
        />
        <Search className="w-3.5 h-3.5 text-[#94A3B8] absolute left-3 top-2.5 pointer-events-none" />

        {query ? (
          <button
            type="button"
            onClick={() => {
              setQuery("");
              setSavedResults([]);
            }}
            className="absolute right-2.5 top-2 text-[#94A3B8] hover:text-[#102A4C]"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        ) : (
          <kbd className="hidden sm:inline-block absolute right-2.5 top-2 px-1.5 py-0.2 rounded border border-[#DDE5F0] bg-white text-[10px] font-mono text-[#94A3B8]">
            ⌘K
          </kbd>
        )}
      </div>

      {/* Dropdown Results */}
      {isOpen && query.trim().length > 0 && (
        <div className="absolute left-0 right-0 mt-2 bg-white rounded-2xl shadow-xl border border-[#DDE5F0] overflow-hidden z-50 divide-y divide-[#F1F5F9] max-h-96 overflow-y-auto animate-in fade-in duration-150">
          {/* 1. Features Category */}
          {filteredFeatures.length > 0 && (
            <div className="p-2">
              <div className="px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-[#94A3B8]">
                {language === "ta" ? "கருவிகள் & வசதிகள்" : "Astrology Tools & Features"}
              </div>
              <div className="space-y-0.5 mt-1">
                {filteredFeatures.map((item) => {
                  const Icon = item.icon;
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => handleSelect(item.href)}
                      className="w-full flex items-center justify-between p-2 rounded-xl text-left hover:bg-[#F8FAFC] transition-colors group cursor-pointer"
                    >
                      <div className="flex items-center gap-2.5">
                        <div
                          className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${item.color}`}
                        >
                          <Icon className="w-3.5 h-3.5" />
                        </div>
                        <div>
                          <div className="text-xs font-semibold text-[#102A4C] group-hover:text-[#3478F6] transition-colors">
                            {language === "ta" ? item.titleTa : item.titleEn}
                          </div>
                          <div className="text-[10px] text-[#64748B]">
                            {language === "ta" ? item.categoryTa : item.categoryEn}
                          </div>
                        </div>
                      </div>
                      <ArrowRight className="w-3 h-3 text-[#94A3B8] opacity-0 group-hover:opacity-100 transition-opacity" />
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* 2. Saved Horoscopes from Supabase */}
          <div className="p-2 bg-[#FAFBFD]">
            <div className="px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-[#94A3B8] flex items-center justify-between">
              <span>{language === "ta" ? "சேமிக்கப்பட்ட ஜாதகங்கள்" : "Saved Horoscopes"}</span>
              {isSearchingSaved && <Loader2 className="w-3 h-3 text-[#3478F6] animate-spin" />}
            </div>

            {savedResults.length > 0 ? (
              <div className="space-y-0.5 mt-1">
                {savedResults.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => handleSelect(`/horoscope/results?id=${item.id}`)}
                    className="w-full flex items-center justify-between p-2 rounded-xl text-left hover:bg-white transition-colors group cursor-pointer border border-transparent hover:border-[#DDE5F0]"
                  >
                    <div className="flex items-center gap-2.5">
                      <span className="w-7 h-7 rounded-md bg-[#FAF2DE] border border-[#D8BD80] text-[#B8862B] font-mono font-bold text-[11px] flex items-center justify-center shrink-0">
                        #{formatSerialNumber(item.display_number)}
                      </span>
                      <div>
                        <div className="text-xs font-semibold text-[#102A4C] group-hover:text-[#B8862B] transition-colors">
                          {item.person_name}
                        </div>
                        <div className="text-[10px] text-[#64748B]">
                          DOB: {item.birth_date} • {item.birthplace}
                        </div>
                      </div>
                    </div>
                    <ArrowRight className="w-3 h-3 text-[#94A3B8] opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                ))}
              </div>
            ) : query.trim().length >= 2 && !isSearchingSaved ? (
              <div className="px-2 py-2 text-[11px] text-[#94A3B8]">
                {language === "ta"
                  ? "பொருத்தமான சேமிக்கப்பட்ட ஜாதகங்கள் இல்லை"
                  : "No matching saved horoscopes found"}
              </div>
            ) : (
              <div className="px-2 py-2 text-[11px] text-[#94A3B8]">
                {language === "ta"
                  ? "தேட மேலும் எழுத்துக்களை உள்ளிடவும்..."
                  : "Type more characters to search saved charts..."}
              </div>
            )}
          </div>

          {filteredFeatures.length === 0 && savedResults.length === 0 && !isSearchingSaved && (
            <div className="p-4 text-center text-xs text-[#64748B]">
              {language === "ta"
                ? "முடிவுகள் எதுவும் கிடைக்கவில்லை"
                : "No matching tools or horoscopes found."}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
