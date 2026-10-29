"use client";

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { FeatureGuard } from "@/components/auth/FeatureGuard";
import {
  KpRequest,
  KpResponse,
  HoraryKpResponse,
  SavedKpChartRecord,
} from "@/lib/types";
import { calculateKp, saveKpChart } from "@/lib/api";
import { KpBirthChartTab } from "@/components/advanced-kp/KpBirthChartTab";
import { KpCuspAnalysisTab } from "@/components/advanced-kp/KpCuspAnalysisTab";
import { KpSignificatorsTab } from "@/components/advanced-kp/KpSignificatorsTab";
import { HoraryPrashnaTab } from "@/components/advanced-kp/HoraryPrashnaTab";
import { KpDasaTimelineTab } from "@/components/advanced-kp/KpDasaTimelineTab";
import { KpReportsExportTab } from "@/components/advanced-kp/KpReportsExportTab";
import { SavedKpRecordsList } from "@/components/advanced-kp/SavedKpRecordsList";
import { SUPPORTED_COUNTRY_CODES, validateAndNormalizePhone } from "@/lib/phone-utils";
import {
  Compass,
  Layers,
  HelpCircle,
  FileText,
  Calendar,
  Save,
  Clock,
  Sparkles,
  BookmarkCheck,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  Phone,
  Users,
} from "lucide-react";

type WorkspaceTab =
  | "birth_chart"
  | "cusp_analysis"
  | "significators"
  | "horary_prashna"
  | "dasa_timeline"
  | "reports"
  | "saved_records";

function AdvancedKpContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialTab = (searchParams.get("tab") as WorkspaceTab) || "birth_chart";

  const { language, t } = useLanguage();
  const { session, isAuthenticated, isLoading } = useAuth();

  const [activeTab, setActiveTab] = useState<WorkspaceTab>(initialTab);

  // Natal Form State
  const [personName, setPersonName] = useState<string>("Sample Client");
  const [birthDate, setBirthDate] = useState<string>("1995-10-24");
  const [birthTime, setBirthTime] = useState<string>("14:30:00");
  const [countryCode, setCountryCode] = useState<string>("+91");
  const [customerPhone, setCustomerPhone] = useState<string>("");
  const [customerId, setCustomerId] = useState<string | null>(null);
  const [savedCustomers, setSavedCustomers] = useState<any[]>([]);
  const [locationName, setLocationName] = useState<string>("Chennai, India");
  const [latitude, setLatitude] = useState<number>(13.0827);
  const [longitude, setLongitude] = useState<number>(80.2707);
  const [timezone, setTimezone] = useState<string>("Asia/Kolkata");
  const [ayanamsa, setAyanamsa] = useState<number>(1); // 1 = KP
  const [houseSystem, setHouseSystem] = useState<number>(2); // 2 = Placidus

  // Calculation & Persistence State
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [natalResult, setNatalResult] = useState<KpResponse | null>(null);
  const [savingNatal, setSavingNatal] = useState<boolean>(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);
  const [refreshSavedCounter, setRefreshSavedCounter] = useState<number>(0);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  // Load existing customers for reuse and deduplication
  useEffect(() => {
    if (isAuthenticated) {
      fetch("/api/customers")
        .then((res) => (res.ok ? res.json() : null))
        .then((data) => {
          if (data?.customers) setSavedCustomers(data.customers);
        })
        .catch((err) => console.warn("Could not load customers for KP:", err));
    }
  }, [isAuthenticated]);

  const handleSelectCustomer = (customer: any) => {
    setPersonName(customer.full_name || "");
    if (customer.birth_date) setBirthDate(customer.birth_date);
    setCountryCode(customer.country_code || "+91");
    setCustomerPhone(customer.phone_number || customer.normalized_phone || "");
    setCustomerId(customer.id);
  };

  // Synchronize URL query parameter with active tab
  const handleTabChange = (tab: WorkspaceTab) => {
    setActiveTab(tab);
    const params = new URLSearchParams(window.location.search);
    params.set("tab", tab);
    window.history.replaceState(null, "", `?${params.toString()}`);
  };

  // Run Natal KP calculation
  const handleCalculateNatal = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setError(null);
    setSaveSuccessMsg(null);
    setLoading(true);

    try {
      const payload: KpRequest = {
        birth_date: birthDate,
        birth_time: birthTime,
        timezone,
        latitude,
        longitude,
        ayanamsa,
        house_system: houseSystem,
      };

      const res = await calculateKp(payload);
      setNatalResult(res);
    } catch (err: any) {
      setError(err?.message || "Failed to calculate Natal KP chart.");
    } finally {
      setLoading(false);
    }
  };

  // Automatically calculate default natal sample on first load if empty
  useEffect(() => {
    if (!natalResult && !loading && isAuthenticated) {
      handleCalculateNatal();
    }
  }, [isAuthenticated]);

  // Save Natal Chart to public.saved_kp_charts with mandatory customer contact validation
  const handleSaveNatal = async () => {
    if (!natalResult || !session?.access_token) return;
    setSavingNatal(true);
    setError(null);
    setSaveSuccessMsg(null);

    const trimmedName = personName.trim();
    if (!trimmedName) {
      setError(
        language === "ta"
          ? "வாடிக்கையாளர் பெயர் தேவை."
          : "Customer Full Name is required to save client horoscope."
      );
      setSavingNatal(false);
      return;
    }

    if (!birthDate) {
      setError(
        language === "ta"
          ? "பிறந்த தேதி தேவை."
          : "Date of Birth is required for client horoscope."
      );
      setSavingNatal(false);
      return;
    }

    const rawPhone = customerPhone.trim();
    let normPhone: string | undefined = undefined;
    let waNum: string | undefined = undefined;

    if (rawPhone) {
      const phoneVal = validateAndNormalizePhone(rawPhone, countryCode);
      if (!phoneVal.isValid) {
        setError(
          phoneVal.error ||
            (language === "ta"
              ? "செல்லுபடியற்ற வாட்ஸ்அப் எண்."
              : "Invalid WhatsApp phone number.")
        );
        setSavingNatal(false);
        return;
      }
      normPhone = phoneVal.normalizedPhone;
      waNum = phoneVal.whatsappNumber;
    }

    try {
      const payload = {
        chart_type: "natal" as const,
        title: trimmedName,
        customer_full_name: trimmedName,
        customer_phone: rawPhone || undefined,
        country_code: countryCode,
        customer_id: customerId || undefined,
        normalized_phone: normPhone,
        whatsapp_number: waNum,
        birth_date: birthDate,
        birth_time: birthTime,
        location_name: locationName,
        latitude,
        longitude,
        timezone,
        ayanamsa_id: ayanamsa,
        house_system_id: houseSystem,
        calculation_result: natalResult,
      };

      const record = await saveKpChart(session.access_token, payload);
      setSaveSuccessMsg(
        language === "ta"
          ? `KP பிறப்பு ஜாதகம் வெற்றிகரமாக சேமிக்கப்பட்டது! வரிசை எண் #${record.display_number}`
          : `Natal KP chart successfully saved! Assigned Record #${record.display_number}`
      );
      setRefreshSavedCounter((c) => c + 1);
    } catch (err: any) {
      setError(err?.message || "Failed to persist Natal KP chart.");
    } finally {
      setSavingNatal(false);
    }
  };

  // Open a saved record from the list
  const handleOpenSavedRecord = (record: SavedKpChartRecord) => {
    if (record.chart_type === "natal" && record.calculation_result) {
      setNatalResult(record.calculation_result as KpResponse);
      setPersonName(record.title || "Saved Chart");
      if (record.birth_date) setBirthDate(record.birth_date);
      if (record.birth_time) setBirthTime(record.birth_time);
      if (record.location_name) setLocationName(record.location_name);
      setLatitude(record.latitude);
      setLongitude(record.longitude);
      setTimezone(record.timezone);
      setAyanamsa(record.ayanamsa_id);
      setActiveTab("birth_chart");
    } else if (record.chart_type === "horary") {
      setActiveTab("horary_prashna");
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-[calc(100vh-14rem)] flex items-center justify-center bg-[#E8EEF7]">
        <div className="w-8 h-8 border-4 border-[#B8862B] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 sm:py-8 space-y-8">
      {/* Breadcrumbs */}
      <Breadcrumbs
        items={[
          {
            label: language === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools",
            href: "/tools",
          },
          {
            label: language === "ta" ? "உயர்நிலை KP முறை" : "Advanced KP System",
          },
        ]}
      />

      {/* Header Banner */}
      <div className="rounded-3xl border border-[#DDE5F0] bg-white p-6 sm:p-8 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-[#B8862B] via-[#E5B558] to-[#3478F6]" />

        <div className="space-y-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
            <Compass className="w-3.5 h-3.5 text-[#B8862B]" />
            <span>Krishnamurti Paddhati Core</span>
          </div>

          <h1 className="font-serif text-2xl sm:text-3xl lg:text-4xl font-bold text-[#102A4C]">
            Advanced KP System | உயர்நிலை கே.பி. முறை
          </h1>

          <p className="text-xs sm:text-sm text-[#52667E] max-w-2xl leading-relaxed">
            {language === "ta"
              ? "துல்லியமான 249 உப-அதிபதி பிரிவுகள், 12 பிளாசிடஸ் பாவக முனைகள், 4-நிலை காரகத்துவங்கள் (A, B, C, D) மற்றும் அங்கீகரிக்கப்பட்ட 1-249 பிரஸ்ன முறை."
              : "Rigorous 249 sub-lord divisions, 12 Placidus cusps, 4-tier significators (A, B, C, D), 5-level Vimshottari timeline, and authentic 1-249 Horary Prashna."}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Link
            href="/tools"
            className="px-4 py-2 rounded-xl text-xs font-semibold text-[#52667E] border border-[#DDE5F0] hover:bg-[#F8FAFC] transition-colors"
          >
            ← {language === "ta" ? "அனைத்து கருவிகள்" : "All Tools"}
          </Link>
        </div>
      </div>

      {/* Workspace Tabs Navigation */}
      <div className="flex border-b border-[#DDE5F0] gap-1.5 overflow-x-auto pb-1 text-xs sm:text-sm font-semibold">
        <button
          type="button"
          onClick={() => handleTabChange("birth_chart")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-t-xl transition-all whitespace-nowrap border-b-2 ${
            activeTab === "birth_chart"
              ? "border-[#B8862B] text-[#B8862B] bg-white font-bold shadow-2xs"
              : "border-transparent text-[#52667E] hover:text-[#102A4C] hover:bg-white/60"
          }`}
        >
          <Compass className="w-4 h-4" />
          <span>{language === "ta" ? "1. KP பிறப்பு ஜாதகம்" : "1. KP Birth Chart"}</span>
        </button>

        <button
          type="button"
          onClick={() => handleTabChange("cusp_analysis")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-t-xl transition-all whitespace-nowrap border-b-2 ${
            activeTab === "cusp_analysis"
              ? "border-[#B8862B] text-[#B8862B] bg-white font-bold shadow-2xs"
              : "border-transparent text-[#52667E] hover:text-[#102A4C] hover:bg-white/60"
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>{language === "ta" ? "2. பாவக முனை & CSL" : "2. Cusp & Sub-Lord Analysis"}</span>
        </button>

        <button
          type="button"
          onClick={() => handleTabChange("significators")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-t-xl transition-all whitespace-nowrap border-b-2 ${
            activeTab === "significators"
              ? "border-[#B8862B] text-[#B8862B] bg-white font-bold shadow-2xs"
              : "border-transparent text-[#52667E] hover:text-[#102A4C] hover:bg-white/60"
          }`}
        >
          <Sparkles className="w-4 h-4" />
          <span>{language === "ta" ? "3. காரகத்துவங்கள் (A-D)" : "3. KP Significators"}</span>
        </button>

        <button
          type="button"
          onClick={() => handleTabChange("horary_prashna")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-t-xl transition-all whitespace-nowrap border-b-2 ${
            activeTab === "horary_prashna"
              ? "border-[#3478F6] text-[#3478F6] bg-white font-bold shadow-2xs"
              : "border-transparent text-[#52667E] hover:text-[#3478F6] hover:bg-white/60"
          }`}
        >
          <HelpCircle className="w-4 h-4" />
          <span>{language === "ta" ? "4. பிரஸ்னம் (1-249)" : "4. Horary Prashna"}</span>
        </button>

        <button
          type="button"
          onClick={() => handleTabChange("dasa_timeline")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-t-xl transition-all whitespace-nowrap border-b-2 ${
            activeTab === "dasa_timeline"
              ? "border-[#B8862B] text-[#B8862B] bg-white font-bold shadow-2xs"
              : "border-transparent text-[#52667E] hover:text-[#102A4C] hover:bg-white/60"
          }`}
        >
          <Clock className="w-4 h-4" />
          <span>{language === "ta" ? "5. 5-நிலை தசா" : "5. Five-Level Dasa"}</span>
        </button>

        <button
          type="button"
          onClick={() => handleTabChange("reports")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-t-xl transition-all whitespace-nowrap border-b-2 ${
            activeTab === "reports"
              ? "border-[#B8862B] text-[#B8862B] bg-white font-bold shadow-2xs"
              : "border-transparent text-[#52667E] hover:text-[#102A4C] hover:bg-white/60"
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>{language === "ta" ? "6. அறிக்கை & ஏற்றுமதி" : "6. Reports & Exports"}</span>
        </button>

        <button
          type="button"
          onClick={() => handleTabChange("saved_records")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-t-xl transition-all whitespace-nowrap border-b-2 ${
            activeTab === "saved_records"
              ? "border-[#102A4C] text-[#102A4C] bg-white font-bold shadow-2xs"
              : "border-transparent text-[#52667E] hover:text-[#102A4C] hover:bg-white/60"
          }`}
        >
          <BookmarkCheck className="w-4 h-4" />
          <span>{language === "ta" ? "சேமிக்கப்பட்ட ஜாதகங்கள்" : "Saved Records"}</span>
        </button>
      </div>

      {/* Notifications */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {saveSuccessMsg && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-700 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{saveSuccessMsg}</span>
        </div>
      )}

      {/* Tab 1: KP Birth Chart & Input Form */}
      {activeTab === "birth_chart" && (
        <div className="space-y-6">
          {/* Natal Inputs Form */}
          <div className="rounded-2xl border border-[#DDE5F0] bg-white p-6 shadow-xs space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-[#F1F5F9]">
              <div className="flex items-center gap-2">
                <Compass className="w-4 h-4 text-[#B8862B]" />
                <h3 className="font-serif text-base font-bold text-[#102A4C]">
                  {language === "ta" ? "பிறப்பு விவரங்கள் மற்றும் அமைப்புகள்" : "Natal Birth Details & Ephemeris Configuration"}
                </h3>
              </div>

              {natalResult && (
                <button
                  type="button"
                  onClick={handleSaveNatal}
                  disabled={savingNatal || !session?.access_token}
                  className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-bold text-white bg-[#102A4C] hover:bg-[#1E3A61] transition-colors disabled:opacity-50"
                  title="Persist to public.saved_kp_charts"
                >
                  <Save className="w-3.5 h-3.5" />
                  <span>
                    {savingNatal
                      ? language === "ta"
                        ? "சேமிக்கப்படுகிறது..."
                        : "Saving..."
                      : language === "ta"
                      ? "KP ஜாதகத்தை சேமி"
                      : "Save Natal KP Chart"}
                  </span>
                </button>
              )}
            </div>

            <form onSubmit={handleCalculateNatal} className="space-y-4">
              {/* Existing Client Selector */}
              {savedCustomers.length > 0 && (
                <div className="p-3 bg-[#FAF8F5] border border-[#E2DCD5] rounded-xl">
                  <div className="flex items-center justify-between mb-1.5">
                    <label htmlFor="kpCustomerSelect" className="text-xs font-bold text-[#102A4C] flex items-center gap-1.5">
                      <Users className="w-3.5 h-3.5 text-[#B8862B]" />
                      <span>{language === "ta" ? "முந்தைய வாடிக்கையாளர் தேர்வு" : "Returning Customer / Saved Client"}</span>
                    </label>
                    {customerId && (
                      <button
                        type="button"
                        onClick={() => {
                          setCustomerId(null);
                          setPersonName("");
                          setCustomerPhone("");
                        }}
                        className="text-[11px] font-semibold text-rose-600 hover:underline"
                      >
                        {language === "ta" ? "புதிய வாடிக்கையாளர் (Reset)" : "Clear / New Customer"}
                      </button>
                    )}
                  </div>
                  <select
                    id="kpCustomerSelect"
                    value={customerId || ""}
                    onChange={(e) => {
                      const val = e.target.value;
                      if (!val) {
                        setCustomerId(null);
                        return;
                      }
                      const found = savedCustomers.find((c) => c.id === val);
                      if (found) {
                        handleSelectCustomer(found);
                      }
                    }}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-[#DDE5F0] bg-white text-[#102A4C] focus:ring-2 focus:ring-[#B8862B]"
                  >
                    <option value="">
                      {language === "ta"
                        ? "-- புதிய வாடிக்கையாளர் (அல்லது பட்டியலிலிருந்து தேர்வு செய்க) --"
                        : "-- Select Saved Customer (or enter new client details) --"}
                    </option>
                    {savedCustomers.map((cust) => (
                      <option key={cust.id} value={cust.id}>
                        {cust.full_name} ({cust.normalized_phone || cust.phone_number}) - DOB: {cust.birth_date || "N/A"}
                      </option>
                    ))}
                  </select>
                  {customerId && (
                    <p className="mt-1.5 text-[11px] text-emerald-700 font-medium flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                      <span>
                        {language === "ta"
                          ? "வாடிக்கையாளர் சுயவிவரம் இணைக்கப்பட்டுள்ளது."
                          : "Authoritative client profile linked. KP horoscope will be saved under this customer."}
                      </span>
                    </p>
                  )}
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="space-y-1">
                  <label className="block text-xs font-bold text-[#52667E]">
                    {language === "ta" ? "வாடிக்கையாளர் முழுப் பெயர்*" : "Customer Full Name*"}
                  </label>
                  <input
                    type="text"
                    required
                    value={personName}
                    onChange={(e) => setPersonName(e.target.value)}
                    placeholder="e.g. John Doe"
                    className="w-full px-3 py-2 text-xs rounded-lg border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] text-[#102A4C]"
                  />
                </div>

                <div className="space-y-1">
                  <label className="block text-xs font-bold text-[#52667E]">
                    {language === "ta" ? "வாட்ஸ்அப் எண் (விருப்பத்தேர்வு)" : "WhatsApp Number (Optional)"}
                  </label>
                  <div className="flex gap-1.5">
                    <select
                      value={countryCode}
                      onChange={(e) => setCountryCode(e.target.value)}
                      className="w-24 px-1.5 py-2 text-xs rounded-lg border border-[#DDE5F0] bg-white text-[#102A4C] focus:ring-2 focus:ring-[#B8862B]"
                    >
                      {SUPPORTED_COUNTRY_CODES.map((item) => (
                        <option key={item.code} value={item.code}>
                          {item.flag} {item.code}
                        </option>
                      ))}
                    </select>
                    <input
                      type="tel"
                      value={customerPhone}
                      onChange={(e) => setCustomerPhone(e.target.value)}
                      placeholder={countryCode === "+91" ? "98765 43210 (Optional)" : "Phone (Optional)"}
                      className="flex-1 px-3 py-2 text-xs rounded-lg border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] text-[#102A4C]"
                    />
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="block text-xs font-bold text-[#52667E]">Birth Date*</label>
                  <input
                    type="date"
                    required
                    value={birthDate}
                    onChange={(e) => setBirthDate(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] text-[#102A4C]"
                  />
                </div>

                <div className="space-y-1">
                  <label className="block text-xs font-bold text-[#52667E]">Birth Time (24h)*</label>
                  <input
                    type="time"
                    step="1"
                    required
                    value={birthTime}
                    onChange={(e) => setBirthTime(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] text-[#102A4C]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                <div className="space-y-1">
                  <label className="block text-xs font-bold text-[#52667E]">Location Name</label>
                  <input
                    type="text"
                    required
                    value={locationName}
                    onChange={(e) => setLocationName(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] text-[#102A4C]"
                  />
                </div>

                <div className="space-y-1">
                  <label className="block text-xs font-bold text-[#52667E]">Latitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    required
                    value={latitude}
                    onChange={(e) => setLatitude(parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] text-[#102A4C]"
                  />
                </div>

                <div className="space-y-1">
                  <label className="block text-xs font-bold text-[#52667E]">Longitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    required
                    value={longitude}
                    onChange={(e) => setLongitude(parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] text-[#102A4C]"
                  />
                </div>

                <div className="space-y-1">
                  <label className="block text-xs font-bold text-[#52667E]">Timezone</label>
                  <input
                    type="text"
                    required
                    value={timezone}
                    onChange={(e) => setTimezone(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] text-[#102A4C]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="block text-xs font-bold text-[#52667E]">Ayanamsa</label>
                  <select
                    value={ayanamsa}
                    onChange={(e) => setAyanamsa(parseInt(e.target.value, 10))}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] text-[#102A4C] bg-white"
                  >
                    <option value={1}>KP Krishnamurti (Standard)</option>
                    <option value={0}>Lahiri (Chitrapaksha)</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="block text-xs font-bold text-[#52667E]">House System</label>
                  <select
                    value={houseSystem}
                    onChange={(e) => setHouseSystem(parseInt(e.target.value, 10))}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-[#DDE5F0] focus:ring-2 focus:ring-[#B8862B] text-[#102A4C] bg-white"
                  >
                    <option value={2}>Placidus (Semi-Arc KP Standard)</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center justify-end pt-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-[#B8862B] hover:bg-[#996515] transition-colors shadow-xs disabled:opacity-50"
                >
                  <Sparkles className="w-4 h-4" />
                  <span>{loading ? "Calculating..." : "Recalculate KP Natal Chart"}</span>
                </button>
              </div>
            </form>
          </div>

          {/* Planetary Table */}
          {natalResult && (
            <KpBirthChartTab
              planets={natalResult.planetary_positions}
              metadata={natalResult.metadata}
              language={language}
            />
          )}
        </div>
      )}

      {/* Tab 2: Cusp and Sub-Lord Analysis */}
      {activeTab === "cusp_analysis" && natalResult && (
        <KpCuspAnalysisTab cusps={natalResult.cuspal_analysis} language={language} />
      )}

      {/* Tab 3: KP Significators */}
      {activeTab === "significators" && natalResult && (
        <KpSignificatorsTab
          houseSignificators={natalResult.house_significators}
          planetSignificators={natalResult.significators}
          language={language}
        />
      )}

      {/* Tab 4: Horary Prashna */}
      {activeTab === "horary_prashna" && (
        <HoraryPrashnaTab
          language={language}
          onSavedRecord={() => setRefreshSavedCounter((c) => c + 1)}
        />
      )}

      {/* Tab 5: Five-Level Vimshottari Dasa */}
      {activeTab === "dasa_timeline" && natalResult && (
        <KpDasaTimelineTab dasaHierarchy={natalResult.dasa_hierarchy} language={language} />
      )}

      {/* Tab 6: Reports & Exports */}
      {activeTab === "reports" && natalResult && (
        <KpReportsExportTab
          data={natalResult}
          chartType="natal"
          title={personName}
          language={language}
        />
      )}

      {/* Tab 7: Saved Records */}
      {activeTab === "saved_records" && (
        <SavedKpRecordsList
          onOpenRecord={handleOpenSavedRecord}
          language={language}
          refreshTrigger={refreshSavedCounter}
        />
      )}
    </div>
  );
}

export default function AdvancedKpPage() {
  return (
    <FeatureGuard permission="kp_astrology">
      <Suspense
        fallback={
          <div className="min-h-[calc(100vh-14rem)] flex items-center justify-center bg-[#E8EEF7]">
            <div className="w-8 h-8 border-4 border-[#B8862B] border-t-transparent rounded-full animate-spin" />
          </div>
        }
      >
        <AdvancedKpContent />
      </Suspense>
    </FeatureGuard>
  );
}
