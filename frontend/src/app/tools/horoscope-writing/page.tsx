"use client";

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { FeatureGuard } from "@/components/auth/FeatureGuard";
import {
  HoroscopeWritingRequest,
  HoroscopeWritingResponse,
  SavedHoroscopeWritingItem,
} from "@/lib/types";
import {
  calculateHoroscopeWriting,
  downloadHoroscopeWritingPdf,
  saveHoroscopeWriting,
  listSavedHoroscopeWritings,
  deleteSavedHoroscopeWriting,
} from "@/lib/api";
import {
  BookOpen,
  Calendar,
  Clock,
  Compass,
  Download,
  Printer,
  Sparkles,
  RefreshCw,
  Edit3,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  Layers,
  ChevronRight,
  User,
  MapPin,
  Save,
  FileText,
  Star,
  Feather,
  Info,
  Trash2,
  Database,
  ExternalLink,
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
  gender?: string;
}

function HoroscopeWritingContent() {
  const searchParams = useSearchParams();
  const savedIdParam = searchParams.get("saved_id");

  const { language } = useLanguage();
  const { session, isAuthenticated } = useAuth();

  // Mode Selection: "saved" | "adhoc" | "saved_writings"
  const [inputMode, setInputMode] = useState<"saved" | "adhoc" | "saved_writings">("saved");

  // Saved Horoscopes List & Selected Item
  const [savedHoroscopes, setSavedHoroscopes] = useState<SavedHoroItem[]>([]);
  const [selectedHoroscopeId, setSelectedHoroscopeId] = useState<string>(savedIdParam || "");
  const [loadingSavedList, setLoadingSavedList] = useState<boolean>(false);

  // Saved Horoscope Writings List (Persistent Documents)
  const [savedWritings, setSavedWritings] = useState<SavedHoroscopeWritingItem[]>([]);
  const [loadingSavedWritings, setLoadingSavedWritings] = useState<boolean>(false);
  const [activeSavedWritingId, setActiveSavedWritingId] = useState<string | null>(null);
  const [writingPersistenceTarget, setWritingPersistenceTarget] = useState<string | null>(null);

  // Ad-hoc Form State
  const [personName, setPersonName] = useState<string>("Native");
  const [gender, setGender] = useState<string>("male");
  const [birthDate, setBirthDate] = useState<string>("1995-05-15");
  const [birthTime, setBirthTime] = useState<string>("14:30:00");
  const [timezone, setTimezone] = useState<string>("Asia/Kolkata");
  const [latitude, setLatitude] = useState<number>(13.0827);
  const [longitude, setLongitude] = useState<number>(80.2707);
  const [birthPlace, setBirthPlace] = useState<string>("Chennai, Tamil Nadu");

  // Options
  const [panchangaSystem, setPanchangaSystem] = useState<string>("thirukanitha");
  const [entranceBasis, setEntranceBasis] = useState<"rasi" | "lagna">("rasi");

  // Calculation Results & State
  const [writingData, setWritingData] = useState<HoroscopeWritingResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [pdfDownloading, setPdfDownloading] = useState<boolean>(false);
  const [savingDoc, setSavingDoc] = useState<boolean>(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Active Booklet Page View Tab: 1 to 6, or "all"
  const [activeTab, setActiveTab] = useState<number | "all">(1);

  // Edit Overrides State (Page 6 Archana Slip)
  const [isEditingOverrides, setIsEditingOverrides] = useState<boolean>(false);
  const [editEntranceDir, setEditEntranceDir] = useState<string>("");
  const [editLuckyDay, setEditLuckyDay] = useState<string>("");
  const [editLuckyColor, setEditLuckyColor] = useState<string>("");
  const [editLuckyGem, setEditLuckyGem] = useState<string>("");
  const [editDeity, setEditDeity] = useState<string>("");

  // Fetch list of saved writings for authenticated user
  const fetchSavedWritingsList = async () => {
    if (!session?.access_token) return;
    setLoadingSavedWritings(true);
    try {
      const resp = await listSavedHoroscopeWritings(session.access_token);
      if (resp && resp.items) {
        setSavedWritings(resp.items);
      }
    } catch (err) {
      console.warn("Failed to fetch saved horoscope writings:", err);
    } finally {
      setLoadingSavedWritings(false);
    }
  };

  // Fetch list of saved horoscopes for authenticated user
  useEffect(() => {
    async function fetchSavedList() {
      if (!session?.access_token) return;
      setLoadingSavedList(true);
      try {
        const resp = await fetch("/api/horoscopes?limit=1000", {
          headers: {
            Authorization: `Bearer ${session.access_token}`,
          },
        });
        if (resp.ok) {
          const data = await resp.json();
          const items: SavedHoroItem[] = data.horoscopes || [];
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
      fetchSavedWritingsList();
    } else {
      setInputMode("adhoc");
    }
  }, [isAuthenticated, session?.access_token]);

  // Selected saved horoscope item
  const activeSavedItem = savedHoroscopes.find((h) => h.id === selectedHoroscopeId);

  // Sync edits when writingData updates
  useEffect(() => {
    if (writingData?.page6_archana_slip) {
      const p6 = writingData.page6_archana_slip;
      setEditEntranceDir(p6.entrance_direction || "");
      setEditLuckyDay(p6.lucky_day || "");
      setEditLuckyColor(p6.lucky_color || "");
      setEditLuckyGem(p6.lucky_gem || "");
      setEditDeity(p6.worship_deity || "");
    }
  }, [writingData]);

  // Calculate Horoscope Writing Booklet
  const handleCalculate = async (overridesToApply?: Record<string, any>) => {
    setLoading(true);
    setErrorMsg(null);
    setSaveSuccessMsg(null);

    try {
      const req: HoroscopeWritingRequest = {
        panchanga_system: panchangaSystem,
        entrance_direction_basis: entranceBasis,
        overrides: overridesToApply || writingData?.overrides || {},
      };

      if (inputMode === "saved") {
        if (!selectedHoroscopeId) {
          throw new Error("தயவுசெய்து ஒரு சேமிக்கப்பட்ட ஜாதகத்தைத் தேர்ந்தெடுக்கவும்.");
        }
        req.saved_horoscope_id = selectedHoroscopeId;
      } else {
        req.person_name = personName.trim() || "Native";
        req.gender = gender;
        req.birth_input = {
          birth_date: birthDate,
          birth_time: birthTime,
          latitude: Number(latitude),
          longitude: Number(longitude),
          timezone: timezone,
        };
      }

      const res = await calculateHoroscopeWriting(req, session?.access_token);
      setWritingData(res);
    } catch (err: any) {
      setErrorMsg(err.message || "ஜாதகக் குறிப்பு கணக்கீட்டில் பிழை ஏற்பட்டது.");
    } finally {
      setLoading(false);
    }
  };

  // Apply Astrologer Overrides
  const handleApplyOverrides = () => {
    const overrides = {
      entrance_direction: editEntranceDir.trim(),
      lucky_day: editLuckyDay.trim(),
      lucky_color: editLuckyColor.trim(),
      lucky_gem: editLuckyGem.trim(),
      worship_deity: editDeity.trim(),
    };
    handleCalculate(overrides);
    setIsEditingOverrides(false);
  };

  // Reset to original calculated values
  const handleResetOverrides = () => {
    if (writingData?.page6_archana_slip) {
      const p6 = writingData.page6_archana_slip;
      setEditEntranceDir(p6.calculated_entrance_direction);
      setEditLuckyDay(p6.calculated_lucky_day);
      setEditLuckyColor(p6.calculated_lucky_color);
      setEditLuckyGem(p6.calculated_lucky_gem);
      setEditDeity(p6.calculated_worship_deity);
    }
    handleCalculate({});
    setIsEditingOverrides(false);
  };

  // Download PDF
  const handleDownloadPdf = async () => {
    if (!writingData) return;
    setPdfDownloading(true);
    setErrorMsg(null);

    try {
      const blob = await downloadHoroscopeWritingPdf(
        {
          precalculated_data: writingData,
        },
        session?.access_token
      );

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const safeName = (writingData.person_details?.name || "Native").replace(/\s+/g, "_");
      const bDate = writingData.person_details?.birth_date || "Horoscope";
      a.download = `Tamil_Horoscope_Writing_${safeName}_${bDate}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setErrorMsg(err.message || "PDF பதிவிறக்கத்தில் பிழை ஏற்பட்டது.");
    } finally {
      setPdfDownloading(false);
    }
  };

  // Save to Database / Persistent Storage
  const handleSaveDocument = async () => {
    if (!writingData) return;
    setSavingDoc(true);
    setSaveSuccessMsg(null);
    setErrorMsg(null);

    try {
      const p = writingData.person_details;
      const res = await saveHoroscopeWriting(
        {
          horoscope_id: inputMode === "saved" ? selectedHoroscopeId : null,
          person_name: p.name,
          birth_date: p.birth_date,
          birth_time: p.birth_time,
          birth_place: birthPlace,
          latitude: p.latitude,
          longitude: p.longitude,
          timezone: p.timezone,
          panchanga_system: panchangaSystem,
          calculated_data: writingData,
          overrides: writingData.overrides,
        },
        session?.access_token
      );
      setWritingPersistenceTarget(res.persistence_target);
      setActiveSavedWritingId(res.id);
      const targetLabel = res.persistence_target === "supabase" ? "Supabase Cloud Database" : "Persistent Local Storage";
      setSaveSuccessMsg(`பாரம்பரிய ஜாதகக் குறிப்பு வெற்றிகரமாகச் சேமிக்கப்பட்டது (${targetLabel})!`);
      fetchSavedWritingsList();
    } catch (err: any) {
      setErrorMsg(err.message || "ஜாதகக் குறிப்பை சேமிப்பதில் பிழை ஏற்பட்டது.");
    } finally {
      setSavingDoc(false);
    }
  };

  // Load a previously saved horoscope writing
  const handleLoadSavedWriting = (item: SavedHoroscopeWritingItem) => {
    setActiveSavedWritingId(item.id);
    setWritingData(item.calculated_data);
    setWritingPersistenceTarget(item.persistence_target || "supabase");
    setPersonName(item.person_name);
    setBirthDate(item.birth_date);
    setBirthTime(item.birth_time);
    setBirthPlace(item.birth_place || "");
    setLatitude(item.latitude);
    setLongitude(item.longitude);
    setTimezone(item.timezone);
    setPanchangaSystem(item.panchanga_system);
    const targetLabel = item.persistence_target === "local_disk" ? "Persistent Local Storage" : "Supabase Cloud DB";
    setSaveSuccessMsg(`சேமிக்கப்பட்ட ஜாதகக் குறிப்பு வெற்றிகரமாக ஏற்றப்பட்டது: ${item.person_name} (${targetLabel})`);
    setActiveTab(1);
  };

  // Delete a saved horoscope writing
  const handleDeleteSavedWriting = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm("இந்த ஜாதகக் குறிப்பை நீக்க விரும்புகிறீர்களா? (Do you want to delete this saved horoscope writing?)")) return;
    try {
      await deleteSavedHoroscopeWriting(id, session?.access_token);
      if (activeSavedWritingId === id) {
        setActiveSavedWritingId(null);
      }
      fetchSavedWritingsList();
      setSaveSuccessMsg("ஜாதகக் குறிப்பு வெற்றிகரமாக நீக்கப்பட்டது.");
    } catch (err: any) {
      setErrorMsg(err.message || "நீக்குவதில் பிழை ஏற்பட்டது.");
    }
  };

  const breadcrumbs = [
    { label: language === "ta" ? "முகப்பு" : "Home", href: "/" },
    { label: language === "ta" ? "கருவிகள்" : "Tools", href: "/tools" },
    {
      label: language === "ta" ? "பாரம்பரிய தமிழ் ஜாதகக் குறிப்பு" : "Horoscope Writing",
      href: "/tools/horoscope-writing",
    },
  ];

  return (
    <div className="min-h-screen bg-[#F8FAFC] pb-16">
      {/* Top Breadcrumb & Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-4">
          <Breadcrumbs items={breadcrumbs} />

          <div className="mt-3 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-[#FAF2DE] border border-[#B4872B]/30 text-[#8B6914] text-xs font-semibold uppercase tracking-wider mb-1.5">
                <BookOpen className="w-3.5 h-3.5" />
                பாரம்பரிய தமிழ் ஜாதகக் குறிப்பு
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold text-[#0F172A]">
                Horoscope Writing (பாரம்பரிய ஜாதக எழுத்து)
              </h1>
              <p className="text-sm text-slate-600 mt-1">
                துல்லியமான திருக்கணித பஞ்சாங்கம், விம்சோத்தரி திசா கணக்கீடு மற்றும் 6-பக்க பாரம்பரிய தமிழ் ஜாதகக் குறிப்பு ஏடு.
              </p>
            </div>

            {writingData && (
              <div className="flex items-center gap-2.5">
                <button
                  type="button"
                  onClick={() => window.print()}
                  className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition shadow-sm"
                >
                  <Printer className="w-4 h-4 text-slate-500" />
                  அச்சு (Print)
                </button>

                <button
                  type="button"
                  onClick={handleDownloadPdf}
                  disabled={pdfDownloading}
                  className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold text-white bg-[#153F6B] hover:bg-[#103052] rounded-lg shadow-sm transition disabled:opacity-50"
                >
                  {pdfDownloading ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Download className="w-4 h-4 text-[#B4872B]" />
                  )}
                  {pdfDownloading ? "PDF தயாராகிறது..." : "PDF பதிவிறக்கம் (6 Pages)"}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 space-y-6">
        {/* Input Configuration Card */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="bg-gradient-to-r from-[#153F6B] to-[#1E293B] text-white px-5 py-3.5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <User className="w-4 h-4 text-[#B4872B]" />
              <h2 className="text-sm font-semibold tracking-wide">
                1. ஜாதகத் தேர்வு அல்லது பிறப்பு விவரங்கள் (Birth Information)
              </h2>
            </div>

            {/* Input Mode Selector */}
            <div className="flex items-center bg-white/10 p-0.5 rounded-lg text-xs">
              <button
                type="button"
                onClick={() => setInputMode("saved")}
                className={`px-3 py-1 rounded-md transition font-medium ${
                  inputMode === "saved"
                    ? "bg-white text-[#153F6B] shadow-xs"
                    : "text-slate-200 hover:text-white"
                }`}
              >
                சேமிக்கப்பட்ட ஜாதகம்
              </button>
              <button
                type="button"
                onClick={() => setInputMode("adhoc")}
                className={`px-3 py-1 rounded-md transition font-medium ${
                  inputMode === "adhoc"
                    ? "bg-white text-[#153F6B] shadow-xs"
                    : "text-slate-200 hover:text-white"
                }`}
              >
                புதிய பிறப்பு விவரம்
              </button>
              {isAuthenticated && (
                <button
                  type="button"
                  onClick={() => setInputMode("saved_writings")}
                  className={`px-3 py-1 rounded-md transition font-medium ${
                    inputMode === "saved_writings"
                      ? "bg-[#B4872B] text-white shadow-xs"
                      : "text-amber-200 hover:text-white"
                  }`}
                >
                  சேமிக்கப்பட்ட குறிப்புகள் ({savedWritings.length})
                </button>
              )}
            </div>
          </div>

          <div className="p-5">
            {inputMode === "saved_writings" ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                  <div className="text-xs text-slate-600">
                    முன்பு கணக்கிட்டுச் சேமிக்கப்பட்ட பாரம்பரிய ஜாதகக் குறிப்புகள் (Persistent Documents).
                  </div>
                  <button
                    type="button"
                    onClick={() => fetchSavedWritingsList()}
                    disabled={loadingSavedWritings}
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-md transition"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${loadingSavedWritings ? "animate-spin" : ""}`} />
                    புதுப்பி (Refresh)
                  </button>
                </div>

                {loadingSavedWritings ? (
                  <div className="flex items-center justify-center gap-2 py-8 text-xs text-slate-500">
                    <RefreshCw className="w-4 h-4 animate-spin text-[#153F6B]" />
                    சேமிக்கப்பட்ட குறிப்புகள் பெறப்படுகின்றன...
                  </div>
                ) : savedWritings.length === 0 ? (
                  <div className="p-6 text-center bg-slate-50 border border-dashed border-slate-200 rounded-xl">
                    <FileText className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                    <p className="text-xs font-semibold text-slate-700">இன்னும் ஜாதகக் குறிப்புகள் சேமிக்கப்படவில்லை</p>
                    <p className="text-xs text-slate-500 mt-1">
                      ஜாதகத்தை கணக்கிட்டு "சேமி (Save)" பொத்தானை அழுத்தினால் இங்கு பாதுகாக்கப்படும்.
                    </p>
                    <button
                      type="button"
                      onClick={() => setInputMode("saved")}
                      className="mt-3 px-3 py-1.5 bg-[#153F6B] text-white text-xs rounded-lg hover:bg-[#103052] transition"
                    >
                      ஜாதகம் கணக்கிட செல்க
                    </button>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {savedWritings.map((doc) => {
                      const isLoaded = activeSavedWritingId === doc.id;
                      const dateStr = new Date(doc.created_at).toLocaleString("ta-IN", {
                        dateStyle: "medium",
                        timeStyle: "short",
                      });
                      return (
                        <div
                          key={doc.id}
                          className={`p-3.5 rounded-xl border transition ${
                            isLoaded
                              ? "border-[#B4872B] bg-[#FFFBF0] shadow-xs"
                              : "border-slate-200 bg-white hover:border-slate-300 shadow-2xs"
                          }`}
                        >
                          <div className="flex items-start justify-between gap-2">
                            <div>
                              <div className="font-semibold text-xs text-[#0F172A] flex items-center gap-1.5">
                                <User className="w-3.5 h-3.5 text-[#B4872B]" />
                                {doc.person_name}
                                {isLoaded && (
                                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 font-semibold">
                                    செயலில்
                                  </span>
                                )}
                              </div>
                              <div className="text-[11px] text-slate-600 mt-1 flex flex-wrap items-center gap-x-3 gap-y-0.5">
                                <span>📅 {doc.birth_date}</span>
                                <span>⏰ {doc.birth_time}</span>
                                {doc.birth_place && <span>📍 {doc.birth_place}</span>}
                              </div>
                            </div>

                            <span
                              className={`text-[10px] px-2 py-0.5 rounded-full font-medium shrink-0 ${
                                doc.persistence_target === "supabase"
                                  ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                                  : "bg-blue-50 text-blue-700 border border-blue-200"
                              }`}
                            >
                              {doc.persistence_target === "supabase" ? "Supabase Cloud" : "Persistent Local"}
                            </span>
                          </div>

                          <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px]">
                            <span className="text-slate-400">சேமிக்கப்பட்டது: {dateStr}</span>
                            <div className="flex items-center gap-1.5">
                              <button
                                type="button"
                                onClick={() => handleLoadSavedWriting(doc)}
                                className="px-2.5 py-1 bg-[#153F6B] hover:bg-[#103052] text-white rounded-md transition font-medium text-[11px] inline-flex items-center gap-1"
                              >
                                <ExternalLink className="w-3 h-3" />
                                பார்க்க (Load)
                              </button>
                              <button
                                type="button"
                                onClick={(e) => handleDeleteSavedWriting(doc.id, e)}
                                title="நீக்கு"
                                className="p-1 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-md transition"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            ) : inputMode === "saved" ? (
              <div className="space-y-4">
                {loadingSavedList ? (
                  <div className="flex items-center gap-2 text-sm text-slate-500 py-3">
                    <RefreshCw className="w-4 h-4 animate-spin text-[#153F6B]" />
                    சேமிக்கப்பட்ட ஜாதகங்கள் பெறப்படுகின்றன...
                  </div>
                ) : savedHoroscopes.length === 0 ? (
                  <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800 flex items-start gap-2.5">
                    <Info className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                    <div>
                      சேமிக்கப்பட்ட ஜாதகங்கள் ஏதுமில்லை. தயவுசெய்து{" "}
                      <button
                        type="button"
                        onClick={() => setInputMode("adhoc")}
                        className="underline font-semibold hover:text-amber-900"
                      >
                        புதிய பிறப்பு விவரம்
                      </button>{" "}
                      வழியாக உருவாக்கவும்.
                    </div>
                  </div>
                ) : (
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                      ஜாதகத்தைத் தேர்ந்தெடுக்கவும்:
                    </label>
                    <select
                      value={selectedHoroscopeId}
                      onChange={(e) => setSelectedHoroscopeId(e.target.value)}
                      className="w-full sm:w-2/3 px-3 py-2 text-sm border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-[#153F6B]/30 focus:border-[#153F6B]"
                    >
                      {savedHoroscopes.map((h) => (
                        <option key={h.id} value={h.id}>
                          {h.person_name} • {h.birth_date} {h.birth_time} ({h.location_name || `${h.latitude}, ${h.longitude}`})
                        </option>
                      ))}
                    </select>

                    {activeSavedItem && (
                      <div className="mt-3 p-3 bg-slate-50 border border-slate-200 rounded-lg grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                        <div>
                          <span className="text-slate-500 block">பெயர்:</span>
                          <span className="font-semibold text-slate-800">{activeSavedItem.person_name}</span>
                        </div>
                        <div>
                          <span className="text-slate-500 block">பிறந்த தேதி & நேரம்:</span>
                          <span className="font-semibold text-slate-800">{activeSavedItem.birth_date} {activeSavedItem.birth_time}</span>
                        </div>
                        <div>
                          <span className="text-slate-500 block">அட்ச / தீர்க்க ரேகை:</span>
                          <span className="font-semibold text-slate-800">{activeSavedItem.latitude.toFixed(2)}°N, {activeSavedItem.longitude.toFixed(2)}°E</span>
                        </div>
                        <div>
                          <span className="text-slate-500 block">நேர மண்டலம்:</span>
                          <span className="font-semibold text-slate-800">{activeSavedItem.timezone}</span>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">ஜாதகர் பெயர்:</label>
                  <input
                    type="text"
                    value={personName}
                    onChange={(e) => setPersonName(e.target.value)}
                    placeholder="Native Name"
                    className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-1 focus:ring-[#153F6B]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">பாலினம்:</label>
                  <select
                    value={gender}
                    onChange={(e) => setGender(e.target.value)}
                    className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg bg-white"
                  >
                    <option value="male">ஆண் (Male)</option>
                    <option value="female">பெண் (Female)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">பிறந்த தேதி:</label>
                  <input
                    type="date"
                    value={birthDate}
                    onChange={(e) => setBirthDate(e.target.value)}
                    className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-1 focus:ring-[#153F6B]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">பிறந்த நேரம் (HH:MM:SS):</label>
                  <input
                    type="time"
                    step="1"
                    value={birthTime}
                    onChange={(e) => setBirthTime(e.target.value)}
                    className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-1 focus:ring-[#153F6B]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">பிறந்த இடம்:</label>
                  <input
                    type="text"
                    value={birthPlace}
                    onChange={(e) => setBirthPlace(e.target.value)}
                    placeholder="Chennai, Tamil Nadu"
                    className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-1 focus:ring-[#153F6B]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">அட்சரேகை (Latitude):</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={latitude}
                    onChange={(e) => setLatitude(parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-1 focus:ring-[#153F6B]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">தீர்க்கரேகை (Longitude):</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={longitude}
                    onChange={(e) => setLongitude(parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-1 focus:ring-[#153F6B]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">நேர மண்டலம்:</label>
                  <input
                    type="text"
                    value={timezone}
                    onChange={(e) => setTimezone(e.target.value)}
                    className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-1 focus:ring-[#153F6B]"
                  />
                </div>
              </div>
            )}

            {/* Panchanga & Calculation Controls */}
            {inputMode !== "saved_writings" && (
              <div className="mt-4 pt-4 border-t border-slate-200 flex flex-wrap items-center justify-between gap-4">
                <div className="flex flex-wrap items-center gap-4 text-xs">
                  <div>
                    <label className="font-semibold text-slate-700 mr-2">பஞ்சாங்க முறை:</label>
                    <select
                      value={panchangaSystem}
                      onChange={(e) => setPanchangaSystem(e.target.value)}
                      className="px-2.5 py-1.5 border border-slate-300 rounded-md bg-white text-xs"
                    >
                      <option value="thirukanitha">திருக்கணிதம் (Drik Siddhanta - Default)</option>
                      <option value="vakkiya">வாக்கிய பஞ்சாங்கம் (Vakkiyam)</option>
                    </select>
                  </div>

                  <div>
                    <label className="font-semibold text-slate-700 mr-2">வாசல் திசை அடிப்படை:</label>
                    <select
                      value={entranceBasis}
                      onChange={(e) => setEntranceBasis(e.target.value as any)}
                      className="px-2.5 py-1.5 border border-slate-300 rounded-md bg-white text-xs"
                    >
                      <option value="rasi">இராசி அடிப்படை (Rasi-based)</option>
                      <option value="lagna">லக்ன அடிப்படை (Lagna-based)</option>
                    </select>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => handleCalculate()}
                  disabled={loading}
                  className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#B4872B] hover:bg-[#996F1D] text-white font-semibold text-xs rounded-lg shadow-sm transition disabled:opacity-50"
                >
                  {loading ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Sparkles className="w-4 h-4 text-amber-100" />
                  )}
                  {loading ? "கணக்கிடப்படுகிறது..." : "ஜாதகக் குறிப்பு உருவாக்குக (Generate)"}
                </button>
              </div>
            )}
          </div>
        </div>

        {errorMsg && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 flex items-center gap-2.5">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-500" />
            <span>{errorMsg}</span>
          </div>
        )}

        {saveSuccessMsg && (
          <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800 flex items-center gap-2.5">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
            <span>{saveSuccessMsg}</span>
          </div>
        )}

        {/* Six-Page Document Preview & Booklet Output */}
        {writingData && (
          <div className="space-y-4">
            {/* Page Tabs Header */}
            <div className="bg-white rounded-xl border border-slate-200 p-2 shadow-xs flex flex-wrap items-center justify-between gap-2">
              <div className="flex flex-wrap items-center gap-1 text-xs font-medium">
                <span className="text-slate-500 px-2 font-semibold">பக்கங்கள்:</span>
                {[
                  { id: 1, label: "பக்கம் 1: ஜனன விவரங்கள்" },
                  { id: 2, label: "பக்கம் 2: தினசுத்திப் படலம்" },
                  { id: 3, label: "பக்கம் 3: உடுமகா திசை" },
                  { id: 4, label: "பக்கம் 4: குறிப்பு" },
                  { id: 5, label: "பக்கம் 5: படுபட்சி பலன்" },
                  { id: 6, label: "பக்கம் 6: அர்ச்சனை பேப்பர்" },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    type="button"
                    onClick={() => setActiveTab(tab.id)}
                    className={`px-3 py-1.5 rounded-lg transition ${
                      activeTab === tab.id
                        ? "bg-[#153F6B] text-white shadow-xs font-semibold"
                        : "text-slate-600 hover:bg-slate-100"
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
                <button
                  type="button"
                  onClick={() => setActiveTab("all")}
                  className={`px-3 py-1.5 rounded-lg transition font-semibold ${
                    activeTab === "all"
                      ? "bg-[#B4872B] text-white shadow-xs"
                      : "text-amber-800 bg-amber-50 hover:bg-amber-100"
                  }`}
                >
                  அனைத்து பக்கங்களும் (View All)
                </button>
              </div>

              <div className="flex items-center gap-2">
                {isAuthenticated && (
                  <button
                    type="button"
                    onClick={handleSaveDocument}
                    disabled={savingDoc}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition shadow-xs disabled:opacity-50"
                  >
                    <Save className="w-3.5 h-3.5 text-slate-500" />
                    {savingDoc ? "சேமிக்கப்படுகிறது..." : "சேமி (Save)"}
                  </button>
                )}
              </div>
            </div>

            {/* Document Render Container */}
            <div className="space-y-6">
              {/* PAGE 1 */}
              {(activeTab === 1 || activeTab === "all") && (
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6 print:border-none print:shadow-none">
                  {/* Traditional Top Invocation */}
                  <div className="text-center space-y-1">
                    <p className="text-xs font-bold text-[#B4872B] tracking-widest">
                      || ஸ்ரீ கணேசாய நம: || ஸ்ரீ குருப்யோ நம: ||
                    </p>
                    <h2 className="text-xl sm:text-2xl font-bold text-[#153F6B]">
                      கோகுலின் பாரம்பரிய ஜோதிடக் குறிப்பு
                    </h2>
                    <p className="text-xs text-slate-500">
                      Gokul&apos;s Astrological Insights • Traditional Tamil Horoscope Booklet
                    </p>
                  </div>

                  {/* Native Particulars Top Box */}
                  <div className="p-3.5 bg-[#FAF2DE]/50 border border-[#B4872B]/40 rounded-lg text-xs grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                    <div>
                      <span className="text-slate-500 block">ஜாதகர் பெயர்:</span>
                      <span className="font-bold text-slate-800">{writingData.person_details?.name}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">பிறந்த தேதி & நேரம்:</span>
                      <span className="font-bold text-slate-800">
                        {writingData.person_details?.birth_date} • {writingData.person_details?.birth_time}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">பிறந்த இடம்:</span>
                      <span className="font-bold text-slate-800">{writingData.person_details?.birth_place}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">பஞ்சாங்கம்:</span>
                      <span className="font-bold text-[#8B6914]">{writingData.page2_dinasuthi?.panchangam}</span>
                    </div>
                  </div>

                  {/* Section Title */}
                  <div className="border-b border-[#B4872B]/40 pb-2 flex items-center justify-between">
                    <div>
                      <h3 className="text-base font-bold text-slate-800">
                        பக்கம் 1: நிகழும் ஆண்டு மற்றும் ஜனன விவரங்கள்
                      </h3>
                      <p className="text-xs text-slate-500">
                        பாரம்பரிய பஞ்சாங்க அங்கங்கள் மற்றும் பிறப்பு நேரக் கணிப்புகள்
                      </p>
                    </div>
                    <span className="text-xs font-bold text-[#B4872B] bg-[#FAF2DE] px-2.5 py-1 rounded-md border border-[#B4872B]/30">
                      Page 1 of 6
                    </span>
                  </div>

                  {/* Page 1 Traditional Table */}
                  <div className="border border-slate-200 rounded-lg overflow-hidden">
                    <table className="w-full text-xs divide-y divide-slate-200">
                      <tbody className="divide-y divide-slate-100">
                        {[
                          ["01", "வருஷம் / மாதம் / தேதி", writingData.page1_birth_details?.tamil_year_month_date],
                          ["02", "கிழமை (வாரம்)", writingData.page1_birth_details?.weekday],
                          ["03", "அயணம்", writingData.page1_birth_details?.ayanam],
                          ["04", "ருது (பருவம்)", writingData.page1_birth_details?.ritu],
                          ["05", "பக்ஷம்", writingData.page1_birth_details?.paksha],
                          ["06", "திதி", writingData.page1_birth_details?.tithi],
                          ["07", "முதல் நாள் நக்ஷத்திரம்", writingData.page1_birth_details?.prev_nakshatra],
                          ["08", "ஜனன நக்ஷத்திரம் (பிறப்பு)", writingData.page1_birth_details?.birth_nakshatra],
                          ["09", "மறுநாள் நக்ஷத்திரம்", writingData.page1_birth_details?.next_nakshatra],
                          ["10", "நாமயோகம்", writingData.page1_birth_details?.nama_yoga],
                          ["11", "கர்ணம்", writingData.page1_birth_details?.karana],
                          ["12", "தியாஜ்ஜியம் (வர்ஜ்யம்)", writingData.page1_birth_details?.tyajyam],
                          ["13", "அகஸ் (பகல் அளவு)", writingData.page1_birth_details?.ahas],
                          ["14", "பிறந்த நேரம்", `${writingData.page1_birth_details?.birth_time} மணி`],
                          ["15", "உதயாதி நாழிகை", `${writingData.page1_birth_details?.udayadhi_nazhigai} (${writingData.page1_birth_details?.udayadhi_hours})`],
                          ["16", "சூரிய உதயம்", `${writingData.page1_birth_details?.sunrise} மணி (அஸ்தமனம்: ${writingData.page1_birth_details?.sunset})`],
                          ["17", "உதய லக்னம்", writingData.page1_birth_details?.udaya_lagna],
                          ["18", "வார யோகம்", writingData.page1_birth_details?.vara_yoga],
                        ].map(([idx, label, val], i) => (
                          <tr key={idx} className={i % 2 === 0 ? "bg-white" : "bg-slate-50/70"}>
                            <td className="w-10 px-3 py-2 text-slate-400 font-mono text-center">{idx}</td>
                            <td className="w-1/3 px-3 py-2 font-semibold text-slate-700">{label}</td>
                            <td className="px-3 py-2 text-slate-900 font-medium">{val}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* PAGE 2 */}
              {(activeTab === 2 || activeTab === "all") && (
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6 print:border-none print:shadow-none">
                  <div className="border-b border-[#B4872B]/40 pb-2 flex items-center justify-between">
                    <div>
                      <h3 className="text-base font-bold text-slate-800">
                        பக்கம் 2: தினசுத்திப் படலம்
                      </h3>
                      <p className="text-xs text-slate-500">
                        பாரம்பரிய பஞ்சாங்க முறை, சகாப்தங்கள் &amp; வானியல் கணக்கீட்டு முறை
                      </p>
                    </div>
                    <span className="text-xs font-bold text-[#B4872B] bg-[#FAF2DE] px-2.5 py-1 rounded-md border border-[#B4872B]/30">
                      Page 2 of 6
                    </span>
                  </div>

                  <div className="border border-slate-200 rounded-lg overflow-hidden">
                    <table className="w-full text-xs divide-y divide-slate-200">
                      <thead>
                        <tr className="bg-slate-50 text-slate-700 font-semibold">
                          <th className="px-4 py-2.5 text-left w-1/2">பாரம்பரிய காலம் / சகாப்தப் பிரிவு</th>
                          <th className="px-4 py-2.5 text-left">கணக்கிடப்பட்ட விவரம்</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {[
                          ["சகாப்தம் (சாலிவாகன சகாப்தம்)", writingData.page2_dinasuthi?.saka_year],
                          ["கலியுகாதி (கலியுக ஆண்டு)", writingData.page2_dinasuthi?.kali_year],
                          ["ஹிஜிரி (இஸ்லாமிய சகாப்தம்)", writingData.page2_dinasuthi?.hijri_year],
                          ["கொல்லம் ஆண்டு (மலையாள வருடம்)", writingData.page2_dinasuthi?.kollam_year],
                          ["ஆங்கில வருஷம்", writingData.page2_dinasuthi?.english_year],
                          ["ஆங்கில தேதி", writingData.page2_dinasuthi?.english_date],
                          ["தமிழ் மாதம் மற்றும் தேதி", writingData.page2_dinasuthi?.tamil_month_date],
                          ["பஞ்சாங்கம்", writingData.page2_dinasuthi?.panchangam],
                          ["கணக்கீட்டு முறை", writingData.page2_dinasuthi?.calculation_method],
                        ].map(([label, val], i) => (
                          <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-slate-50/70"}>
                            <td className="px-4 py-2.5 font-semibold text-slate-700">{label}</td>
                            <td className="px-4 py-2.5 text-slate-900 font-medium">{val}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Notes Card */}
                  <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg text-xs space-y-1.5 text-slate-700">
                    <h4 className="font-bold text-[#153F6B] text-xs">தினசுத்திப் படலக் குறிப்பு விளக்கம்:</h4>
                    <p>• <b>சாலிவாகன சகாப்தம்:</b> கி.பி. 78-இல் தொடங்கப்பட்ட பாரம்பரிய இந்திய வானியல் ஆண்டுக் கணக்கு.</p>
                    <p>• <b>கலியுகாதி:</b> கி.மு. 3102 பிப்ரவரி 18 அன்று துவங்கிய கலியுக ஆண்டுக் கணக்கீடு.</p>
                    <p>• <b>கொல்லம் ஆண்டு:</b> கி.பி. 825-ஆம் ஆண்டு சிம்ம சங்கிராந்தி (ஆவணி 1) அன்று தொடங்கப்பட்ட தென்மண்டல பாரம்பரிய முறை.</p>
                    <p>• <b>திருக்கணித முறை:</b> நவீன வானியல் நுட்பங்களை வேத ஜோதிட சித்தாந்த விதிகளுடன் இணைத்துக் கணக்கிடும் முறைமை.</p>
                  </div>
                </div>
              )}

              {/* PAGE 3 */}
              {(activeTab === 3 || activeTab === "all") && (
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6 print:border-none print:shadow-none">
                  <div className="border-b border-[#B4872B]/40 pb-2 flex items-center justify-between">
                    <div>
                      <h3 className="text-base font-bold text-slate-800">
                        பக்கம் 3: உடுமகா திசை
                      </h3>
                      <p className="text-xs text-slate-500">
                        நட்சத்திர பரம நாழிகை &amp; விம்சோத்தரி மகா திசா-புக்தி கணக்கீட்டுப் படலம்
                      </p>
                    </div>
                    <span className="text-xs font-bold text-[#B4872B] bg-[#FAF2DE] px-2.5 py-1 rounded-md border border-[#B4872B]/30">
                      Page 3 of 6
                    </span>
                  </div>

                  {/* Param Nazhigai & Balance */}
                  <div className="border border-slate-200 rounded-lg overflow-hidden">
                    <table className="w-full text-xs divide-y divide-slate-200">
                      <tbody className="divide-y divide-slate-100">
                        {[
                          ["ஆதிபத்யம் பரம நாழிகை", writingData.page3_udumaka_dasa?.param_nazhigai],
                          ["பாதம் ஒன்றுக்கு", writingData.page3_udumaka_dasa?.pada_duration],
                          ["பிறந்த பாதம்", `${writingData.page3_udumaka_dasa?.birth_pada} ஆம் பாதம்`],
                          ["பிறந்த பாதத்தில் சென்றது", writingData.page3_udumaka_dasa?.pada_sentrathu],
                          ["பிறந்த பாதத்தில் நின்றது", writingData.page3_udumaka_dasa?.pada_nindrathu],
                          ["ஜனன திசை நாயகன்", `${writingData.page3_udumaka_dasa?.dasa_lord} திசை`],
                          ["திசை மொத்த காலம்", writingData.page3_udumaka_dasa?.dasa_full_years],
                          ["திசையில் சென்றது", writingData.page3_udumaka_dasa?.dasa_sentrathu],
                          ["செல் நீக்கி இருப்பு", writingData.page3_udumaka_dasa?.dasa_iruppu],
                        ].map(([label, val], i) => (
                          <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-slate-50/70"}>
                            <td className="w-1/2 px-4 py-2 font-semibold text-slate-700">{label}</td>
                            <td className={`px-4 py-2 font-medium ${label.includes("இருப்பு") ? "text-[#991B1B] font-bold" : "text-slate-900"}`}>
                              {val}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Sequential Dasa Timeline Table */}
                  <div className="space-y-2">
                    <h4 className="font-bold text-slate-800 text-xs">
                      விம்சோத்தரி மகா திசைகளின் வரிசைக் கால அட்டவணை (120 ஆண்டுகள்)
                    </h4>
                    <div className="border border-slate-200 rounded-lg overflow-x-auto">
                      <table className="w-full text-xs divide-y divide-slate-200">
                        <thead className="bg-[#FAF2DE] text-[#8B6914] font-semibold">
                          <tr>
                            <th className="px-3 py-2 text-center w-12">வ.எண்</th>
                            <th className="px-3 py-2 text-left">திசா நாயகன்</th>
                            <th className="px-3 py-2 text-center">மொத்த காலம்</th>
                            <th className="px-3 py-2 text-left">கால இருப்பு / அளவு</th>
                            <th className="px-3 py-2 text-center">ஆரம்ப தேதி</th>
                            <th className="px-3 py-2 text-center">முடிவு தேதி</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 bg-white">
                          {writingData.page3_udumaka_dasa?.dasa_sequence?.map((row) => (
                            <tr key={row.order} className="hover:bg-slate-50">
                              <td className="px-3 py-2 text-center font-mono text-slate-400">{row.order}</td>
                              <td className="px-3 py-2 font-bold text-slate-800">{row.lord_ta} திசை</td>
                              <td className="px-3 py-2 text-center text-slate-600">{row.total_years} ஆ</td>
                              <td className="px-3 py-2 text-slate-700 font-medium">{row.balance_str}</td>
                              <td className="px-3 py-2 text-center text-slate-600 font-mono">{row.start_date}</td>
                              <td className="px-3 py-2 text-center text-slate-600 font-mono">{row.end_date}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {/* PAGE 4 */}
              {(activeTab === 4 || activeTab === "all") && (
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6 print:border-none print:shadow-none">
                  <div className="border-b border-[#B4872B]/40 pb-2 flex items-center justify-between">
                    <div>
                      <h3 className="text-base font-bold text-slate-800">
                        பக்கம் 4: குறிப்பு
                      </h3>
                      <p className="text-xs text-slate-500">
                        ஜனன காலக் குறிப்புகள், பட்சி, மரம், மிருகம் &amp; நாடி-கண அமைப்புகள்
                      </p>
                    </div>
                    <span className="text-xs font-bold text-[#B4872B] bg-[#FAF2DE] px-2.5 py-1 rounded-md border border-[#B4872B]/30">
                      Page 4 of 6
                    </span>
                  </div>

                  <div className="border border-slate-200 rounded-lg overflow-hidden">
                    <table className="w-full text-xs divide-y divide-slate-200">
                      <thead>
                        <tr className="bg-slate-50 text-slate-700 font-semibold">
                          <th className="px-4 py-2.5 text-left w-1/2">சாஸ்திரக் குறிப்புப் பிரிவு</th>
                          <th className="px-4 py-2.5 text-left">ஜாதகருக்குரிய அமைப்புகள்</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {[
                          ["உதயாதி மணி", writingData.page4_kurippu?.udayadhi_mani],
                          ["லக்ன இருப்பு", writingData.page4_kurippu?.lagna_iruppu],
                          ["அகஸ்", writingData.page4_kurippu?.ahas],
                          ["காலம் ஒன்றுக்கு", writingData.page4_kurippu?.kalam_ontrukku],
                          ["காலம் (பகல் / இரவு)", writingData.page4_kurippu?.kalam],
                          ["லக்னம்", `${writingData.page4_kurippu?.lagna} லக்னம்`],
                          ["இராசி", `${writingData.page4_kurippu?.rasi} ராசி`],
                          ["நட்சத்திரம்", writingData.page4_kurippu?.nakshatra],
                          ["நட்சத்திரப் பாதம்", `${writingData.page4_kurippu?.pada} ஆம் பாதம்`],
                          ["மிருகம்", writingData.page4_kurippu?.mrigam],
                          ["பட்சி", writingData.page4_kurippu?.pakshi],
                          ["மரம் (விருட்சம்)", writingData.page4_kurippu?.maram],
                          ["கணம்", writingData.page4_kurippu?.gana],
                          ["ரஜ்ஜு", writingData.page4_kurippu?.rajju],
                          ["நாடி", writingData.page4_kurippu?.nadi],
                        ].map(([label, val], i) => (
                          <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-slate-50/70"}>
                            <td className="px-4 py-2 font-semibold text-slate-700">{label}</td>
                            <td className="px-4 py-2 text-slate-900 font-medium">{val}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900">
                    <b>விளக்கக் குறிப்பு:</b> மேற்கண்ட அம்சங்கள் திருமணப் பொருத்தம், தொழில் தொடக்கம், ஆயுள் பலம் மற்றும் ஆன்மீக பரிகாரக் கிரியைகளுக்கு முதன்மையாகப் பயன்படும் பாரம்பரிய வாழ்வியல் அடையாளங்களாகும்.
                  </div>
                </div>
              )}

              {/* PAGE 5 */}
              {(activeTab === 5 || activeTab === "all") && (
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6 print:border-none print:shadow-none">
                  <div className="border-b border-[#B4872B]/40 pb-2 flex items-center justify-between">
                    <div>
                      <h3 className="text-base font-bold text-slate-800">
                        பக்கம் 5: ஸ்ரீ படுபட்சி பலன்
                      </h3>
                      <p className="text-xs text-slate-500">
                        பஞ்ச பட்சி சாஸ்திரம் • உயிர் பட்சி அவஸ்தைகள் &amp; பலன் வழிகாட்டல்
                      </p>
                    </div>
                    <span className="text-xs font-bold text-[#B4872B] bg-[#FAF2DE] px-2.5 py-1 rounded-md border border-[#B4872B]/30">
                      Page 5 of 6
                    </span>
                  </div>

                  {/* Summary Card */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg space-y-2 text-xs">
                      <div>
                        <span className="text-slate-500 block">ஜென்ம நட்சத்திரம்:</span>
                        <span className="font-bold text-slate-800 text-sm">{writingData.page5_padupakshi?.birth_nakshatra}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">உயிர் பட்சி:</span>
                        <span className="font-bold text-rose-700 text-base">{writingData.page5_padupakshi?.uyir_pakshi}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">பக்ஷம் (பிறப்பு நிலை):</span>
                        <span className="font-semibold text-slate-800">{writingData.page5_padupakshi?.paksha}</span>
                      </div>
                    </div>

                    <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg space-y-2 text-xs">
                      <div>
                        <span className="text-slate-500 block">ஆதிக்க நிலை:</span>
                        <span className="font-bold text-[#153F6B]">{writingData.page5_padupakshi?.dominant_state}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">வளர்பிறை வழிகாட்டல்:</span>
                        <span className="text-slate-700">{writingData.page5_padupakshi?.valarpirai_guidance}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">தேய்பிறை வழிகாட்டல்:</span>
                        <span className="text-slate-700">{writingData.page5_padupakshi?.theypirai_guidance}</span>
                      </div>
                    </div>
                  </div>

                  {/* Pancha Pakshi States Table */}
                  <div className="space-y-2">
                    <h4 className="font-bold text-slate-800 text-xs">
                      பஞ்ச பட்சி சாஸ்திர அவஸ்தைகள் &amp; அவற்றின் பலன்கள்
                    </h4>
                    <div className="border border-slate-200 rounded-lg overflow-hidden">
                      <table className="w-full text-xs divide-y divide-slate-200">
                        <thead className="bg-slate-50 text-slate-700 font-semibold">
                          <tr>
                            <th className="px-3 py-2 text-left w-1/4">அவஸ்தை நிலை</th>
                            <th className="px-3 py-2 text-center w-1/4">ஆற்றல் விகிதம்</th>
                            <th className="px-3 py-2 text-left">செய்யத்தக்க சுப காரியங்கள் &amp; எச்சரிக்கைகள்</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 bg-white">
                          <tr className="hover:bg-slate-50">
                            <td className="px-3 py-2 font-bold text-emerald-700">அரசு (Ruling)</td>
                            <td className="px-3 py-2 text-center font-semibold text-slate-700">100% உச்ச பலம்</td>
                            <td className="px-3 py-2 text-slate-700">முக்கிய முடிவுகள், அரசு வேலை, வழக்கு வெற்றி, ஒப்பந்தங்கள்</td>
                          </tr>
                          <tr className="hover:bg-slate-50">
                            <td className="px-3 py-2 font-bold text-blue-700">ஊண் (Eating)</td>
                            <td className="px-3 py-2 text-center font-semibold text-slate-700">80% உயர்ந்த பலம்</td>
                            <td className="px-3 py-2 text-slate-700">தொழில் தொடக்கம், விருந்து, கல்வி, மங்கல நற்காரியங்கள்</td>
                          </tr>
                          <tr className="hover:bg-slate-50">
                            <td className="px-3 py-2 font-bold text-amber-700">நடை (Walking)</td>
                            <td className="px-3 py-2 text-center font-semibold text-slate-700">50% மத்தியம பலம்</td>
                            <td className="px-3 py-2 text-slate-700">பிரயாணம், பண்டமாற்று, சாதாரண பேச்சுவார்த்தைகள்</td>
                          </tr>
                          <tr className="hover:bg-slate-50">
                            <td className="px-3 py-2 font-bold text-indigo-700">துயில் (Sleeping)</td>
                            <td className="px-3 py-2 text-center font-semibold text-slate-700">20% குறைந்த பலம்</td>
                            <td className="px-3 py-2 text-slate-700">ஓய்வு, தியானம், இறை வழிபாடு; புதிய விவகாரங்களைத் தவிர்க்கவும்</td>
                          </tr>
                          <tr className="hover:bg-slate-50">
                            <td className="px-3 py-2 font-bold text-red-700">சாவு (Dying)</td>
                            <td className="px-3 py-2 text-center font-semibold text-red-600">0% அதம நிலை</td>
                            <td className="px-3 py-2 text-red-600">எந்த ஒரு முக்கிய சுப காரியமும் செய்யலாகாது; அமைதி காக்கவும்</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>

                  <p className="text-xs text-slate-600 leading-relaxed italic">
                    <b>விரிவான வழிகாட்டல்:</b> {writingData.page5_padupakshi?.detailed_guidance}
                  </p>
                </div>
              )}

              {/* PAGE 6 */}
              {(activeTab === 6 || activeTab === "all") && (
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6 print:border-none print:shadow-none">
                  <div className="border-b border-[#B4872B]/40 pb-2 flex items-center justify-between">
                    <div>
                      <h3 className="text-base font-bold text-slate-800">
                        பக்கம் 6: அர்ச்சனை பேப்பரில் பலன்
                      </h3>
                      <p className="text-xs text-slate-500">
                        ஆலய வழிபாடு, சங்கல்ப சுருக்கம் &amp; மங்கல வழிகாட்டல் குறிப்பு
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => setIsEditingOverrides(!isEditingOverrides)}
                        className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-semibold text-[#8B6914] bg-[#FAF2DE] border border-[#B4872B]/40 rounded-lg hover:bg-[#FAF2DE]/80 transition shadow-xs"
                      >
                        <Edit3 className="w-3.5 h-3.5" />
                        {isEditingOverrides ? "திருத்துதலை மூடு" : "பரிந்துரைகளைத் திருத்து (Edit)"}
                      </button>
                      <span className="text-xs font-bold text-[#B4872B] bg-[#FAF2DE] px-2.5 py-1 rounded-md border border-[#B4872B]/30">
                        Page 6 of 6
                      </span>
                    </div>
                  </div>

                  {/* Astrologer Override Edit Form */}
                  {isEditingOverrides && (
                    <div className="p-4 bg-amber-50/70 border border-amber-200 rounded-xl space-y-3 text-xs">
                      <div className="flex items-center justify-between border-b border-amber-200 pb-2">
                        <span className="font-bold text-[#8B6914] flex items-center gap-1.5">
                          <Edit3 className="w-4 h-4" />
                          ஜோதிடர் பரிந்துரைகளைத் திருத்துதல் (Astrologer Custom Overrides):
                        </span>
                        <button
                          type="button"
                          onClick={handleResetOverrides}
                          className="inline-flex items-center gap-1 text-xs font-medium text-amber-800 hover:underline"
                        >
                          <RotateCcw className="w-3 h-3" />
                          கணக்கிடப்பட்ட மதிப்புகளுக்கு மீட்டமை (Reset to Calculated)
                        </button>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                        <div>
                          <label className="block text-slate-700 font-semibold mb-1">வாசல் திசை:</label>
                          <input
                            type="text"
                            value={editEntranceDir}
                            onChange={(e) => setEditEntranceDir(e.target.value)}
                            className="w-full px-2.5 py-1.5 border border-slate-300 rounded-lg bg-white"
                          />
                        </div>

                        <div>
                          <label className="block text-slate-700 font-semibold mb-1">அதிர்ஷ்ட நாள்:</label>
                          <input
                            type="text"
                            value={editLuckyDay}
                            onChange={(e) => setEditLuckyDay(e.target.value)}
                            className="w-full px-2.5 py-1.5 border border-slate-300 rounded-lg bg-white"
                          />
                        </div>

                        <div>
                          <label className="block text-slate-700 font-semibold mb-1">அதிர்ஷ்ட நிறம்:</label>
                          <input
                            type="text"
                            value={editLuckyColor}
                            onChange={(e) => setEditLuckyColor(e.target.value)}
                            className="w-full px-2.5 py-1.5 border border-slate-300 rounded-lg bg-white"
                          />
                        </div>

                        <div>
                          <label className="block text-slate-700 font-semibold mb-1">அதிர்ஷ்ட கல் (ரத்தினம்):</label>
                          <input
                            type="text"
                            value={editLuckyGem}
                            onChange={(e) => setEditLuckyGem(e.target.value)}
                            className="w-full px-2.5 py-1.5 border border-slate-300 rounded-lg bg-white"
                          />
                        </div>

                        <div className="sm:col-span-2">
                          <label className="block text-slate-700 font-semibold mb-1">வணங்க வேண்டிய தெய்வம்:</label>
                          <input
                            type="text"
                            value={editDeity}
                            onChange={(e) => setEditDeity(e.target.value)}
                            className="w-full px-2.5 py-1.5 border border-slate-300 rounded-lg bg-white"
                          />
                        </div>
                      </div>

                      <div className="flex justify-end gap-2 pt-2">
                        <button
                          type="button"
                          onClick={() => setIsEditingOverrides(false)}
                          className="px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-200 rounded-md"
                        >
                          ரத்து
                        </button>
                        <button
                          type="button"
                          onClick={handleApplyOverrides}
                          className="px-4 py-1.5 text-xs font-semibold text-white bg-[#153F6B] hover:bg-[#103052] rounded-md shadow-xs"
                        >
                          மாற்றங்களைச் சேமி &amp; புதுப்பி
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Temple Archana Slip Card */}
                  <div className="border-2 border-[#B4872B]/60 rounded-xl overflow-hidden bg-white shadow-xs">
                    <div className="bg-[#FAF2DE] px-4 py-2.5 border-b border-[#B4872B]/40 text-center">
                      <span className="text-xs font-bold text-[#8B6914] uppercase tracking-wider">
                        ஆலய அர்ச்சனை மற்றும் சங்கல்ப வழிகாட்டல் சீட்டு
                      </span>
                    </div>

                    <table className="w-full text-xs divide-y divide-slate-200">
                      <tbody className="divide-y divide-slate-100">
                        {[
                          ["ஜாதகர் பெயர்", writingData.person_details?.name],
                          ["இராசி", `${writingData.page6_archana_slip?.rasi} ராசி`],
                          ["நட்சத்திரம்", writingData.page6_archana_slip?.nakshatra],
                          ["லக்கனம்", `${writingData.page6_archana_slip?.lagna} லக்னம்`],
                          ["வாசல் திசை (சுப வாசல்)", writingData.page6_archana_slip?.entrance_direction],
                          ["பிறந்த ஆங்கில தேதி", writingData.page6_archana_slip?.birth_date],
                          ["பிறந்த தமிழ் தேதி", writingData.page6_archana_slip?.tamil_date],
                          ["அதிர்ஷ்ட நாள்", writingData.page6_archana_slip?.lucky_day],
                          ["அதிர்ஷ்ட நிறம்", writingData.page6_archana_slip?.lucky_color],
                          ["அதிர்ஷ்ட கல் (ரத்தினம்)", writingData.page6_archana_slip?.lucky_gem],
                          ["வணங்க வேண்டிய தெய்வம்", writingData.page6_archana_slip?.worship_deity],
                        ].map(([label, val], i) => (
                          <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-slate-50/70"}>
                            <td className="w-1/2 px-4 py-2.5 font-semibold text-slate-700">{label}</td>
                            <td className="px-4 py-2.5 text-slate-900 font-bold">{val}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Sacred Kolaru Pathigam Shloka */}
                  <div className="p-4 bg-[#FAF2DE]/50 border border-[#B4872B]/40 rounded-xl text-center space-y-1 text-xs">
                    <p className="font-bold text-[#8B6914] leading-relaxed">
                      வேயுறு தோளிபங்கன் விடமுண்ட கண்டன் மிகநல்ல வீணை தடவி<br />
                      மாசறு திங்கள்கங்கை முடிமே லணிந்தென் உளமே புகுந்த அதனால்<br />
                      ஞாயிறு திங்கள்செவ்வாய் புதன்வியாழன் வெள்ளி சனிபாம்பி ரண்டு முடனே<br />
                      ஆசறு நல்லநல்ல அவைநல்ல நல்ல அடியாரவர்க்கு மிகவே.
                    </p>
                    <p className="text-[11px] text-slate-500 italic mt-1">
                      — திருஞானசம்பந்தர் அருளிய கோளறு திருப்பதிகம்
                    </p>
                  </div>

                  {/* Astrologer Verification Stamp */}
                  <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
                    <div>
                      <span className="font-bold text-[#153F6B] block">சான்றளிக்கப்பட்டது (Verified &amp; Certified):</span>
                      <span className="text-slate-600">
                        பாரம்பரிய தர்ம சாஸ்திர முறைப்படியும் திருக்கணித வானியல் கணிதப்படியும் கணக்கிடப்பட்டுத் தயாரிக்கப்பட்டது.
                      </span>
                    </div>
                    <div className="text-center sm:text-right shrink-0">
                      <span className="font-bold text-slate-800 block">கோகுலின் பாரம்பரிய ஜோதிடக் குறிப்பு</span>
                      <span className="text-[11px] text-[#B4872B]">Gokul&apos;s Astrological Insights</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function HoroscopeWritingPage() {
  return (
    <FeatureGuard permission="tamil_horoscope">
      <Suspense
        fallback={
          <div className="min-h-screen flex items-center justify-center bg-[#F8FAFC]">
            <div className="w-8 h-8 border-4 border-[#153F6B] border-t-transparent rounded-full animate-spin" />
          </div>
        }
      >
        <HoroscopeWritingContent />
      </Suspense>
    </FeatureGuard>
  );
}
