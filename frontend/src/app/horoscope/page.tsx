"use client";

import React, { useState, useEffect, useRef, useCallback, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { getMetadata, calculateFullHoroscopeSuite, ApiError } from "@/lib/api";
import { searchLocations, LocationSearchResult } from "@/lib/geocoding";
import { saveActiveCalculation, clearActiveCalculation } from "@/lib/storage";
import {
  AyanamsaOption,
  HouseSystemOption,
  MetadataResponse,
} from "@/lib/types";
import { COMMON_TIMEZONES } from "@/lib/cities";
import { prepareCalculationSnapshot } from "@/lib/horoscope-storage-utils";
import { SUPPORTED_COUNTRY_CODES, validateAndNormalizePhone } from "@/lib/phone-utils";
import { parse12HourTimeTo24, parse24To12 } from "@/lib/formatters";
import Link from "next/link";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { useAuth } from "@/lib/auth-context";
import {
  Compass,
  MapPin,
  User,
  Sliders,
  AlertCircle,
  Loader2,
  Search,
  ArrowLeft,
  Phone,
  Users,
  CheckCircle2,
  Edit3,
  RotateCcw,
} from "lucide-react";

function HoroscopeFormContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const editId = searchParams.get("edit_id");
  const { language, t } = useLanguage();
  const { isAuthenticated } = useAuth();

  // Edit Mode state
  const [isEditMode, setIsEditMode] = useState<boolean>(false);
  const [editingDisplayNumber, setEditingDisplayNumber] = useState<number | null>(null);
  const [isLoadingEditData, setIsLoadingEditData] = useState<boolean>(false);
  const [editLoadError, setEditLoadError] = useState<string | null>(null);

  // Customer & Form Fields
  const [fullName, setFullName] = useState("");
  const [gender, setGender] = useState<"male" | "female">("male");
  const [birthDate, setBirthDate] = useState("");
  const [countryCode, setCountryCode] = useState("+91");
  const [customerPhone, setCustomerPhone] = useState("");
  const [customerId, setCustomerId] = useState<string | null>(null);

  // Existing Customers Reuse & Autocomplete
  const [savedCustomers, setSavedCustomers] = useState<any[]>([]);
  const [customerSearch, setCustomerSearch] = useState("");
  const [showCustomerDropdown, setShowCustomerDropdown] = useState(false);

  const [birthTime12, setBirthTime12] = useState("");
  const [birthPeriod, setBirthPeriod] = useState<"AM" | "PM">("AM");
  const [isTimeConfirmed, setIsTimeConfirmed] = useState(true);

  // Location Fields
  const [locationQuery, setLocationQuery] = useState("");
  const [locationResults, setLocationResults] = useState<LocationSearchResult[]>([]);
  const [isSearchingLocation, setIsSearchingLocation] = useState(false);
  const [latitude, setLatitude] = useState<number | "">("");
  const [longitude, setLongitude] = useState<number | "">("");
  const [timezone, setTimezone] = useState<string>(() => {
    if (typeof window !== "undefined") {
      try {
        return Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Kolkata";
      } catch {
        return "Asia/Kolkata";
      }
    }
    return "Asia/Kolkata";
  });
  const [showLocationDropdown, setShowLocationDropdown] = useState(false);

  // Calculation Options
  const [ayanamsas, setAyanamsas] = useState<AyanamsaOption[]>([
    { id: 0, name: "Lahiri", description: "Chitrapaksha Lahiri (Standard Vedic)", is_default: true },
    { id: 1, name: "KP", description: "Krishnamurti Paddhati", is_default: false },
    { id: 2, name: "Raman", description: "Dr. B.V. Raman", is_default: false },
  ]);
  const [selectedAyanamsa, setSelectedAyanamsa] = useState(0);

  const [houseSystems, setHouseSystems] = useState<HouseSystemOption[]>([
    { id: 0, name: "WholeSign", description: "Whole Sign (Rashi-Bhava) — Standard Vedic", is_default: true },
    { id: 2, name: "Placidus", description: "Placidus semi-arc (Standard KP)", is_default: false },
    { id: 1, name: "Equal", description: "Equal House from Ascendant", is_default: false },
  ]);
  const [selectedHouseSystem, setSelectedHouseSystem] = useState(0);

  const [includePanchang, setIncludePanchang] = useState(true);
  const [includeOuterPlanets, setIncludeOuterPlanets] = useState(true);

  // Form State & Errors
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [calculationError, setCalculationError] = useState<string | null>(null);

  const formRef = useRef<HTMLFormElement | null>(null);
  const locationSearchTimeout = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (isEditMode && editingDisplayNumber) {
      document.title = `${language === "ta" ? `ஜாதக எண் ${editingDisplayNumber} திருத்துதல்` : `Edit Horoscope No. ${editingDisplayNumber}`} | ${t.brandName}`;
    } else {
      document.title = `${t.formTitle} | ${t.brandName}`;
    }
  }, [isEditMode, editingDisplayNumber, language, t.formTitle, t.brandName]);

  // Helper to ensure the detail form page is 100% clean and fresh for new horoscope generation
  const resetFormToCleanState = useCallback(() => {
    setFullName("");
    setGender("male");
    setBirthDate("");
    setCountryCode("+91");
    setCustomerPhone("");
    setCustomerId(null);
    setCustomerSearch("");
    setShowCustomerDropdown(false);
    setBirthTime12("");
    setBirthPeriod("AM");
    setIsTimeConfirmed(true);
    setLocationQuery("");
    setLocationResults([]);
    setIsSearchingLocation(false);
    setLatitude("");
    setLongitude("");
    setTimezone(() => {
      if (typeof window !== "undefined") {
        try {
          return Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Kolkata";
        } catch {
          return "Asia/Kolkata";
        }
      }
      return "Asia/Kolkata";
    });
    setSelectedAyanamsa(0);
    setSelectedHouseSystem(0);
    setIncludePanchang(true);
    setIncludeOuterPlanets(true);
    setErrors({});
    setCalculationError(null);
    setIsEditMode(false);
    setEditingDisplayNumber(null);
    setEditLoadError(null);
    clearActiveCalculation();

    // Reset native DOM form controls directly to eliminate browser autofill and bfcache restoration
    if (formRef.current) {
      try {
        formRef.current.reset();
        const inputs = formRef.current.querySelectorAll("input");
        inputs.forEach((input) => {
          if (input.type !== "checkbox" && input.type !== "submit" && input.type !== "button") {
            input.value = "";
          }
        });
      } catch {
        // Safe fallback
      }
    }
  }, []);

  // Manual reset that also cleans URL query parameter if present
  const handleManualClear = useCallback(() => {
    resetFormToCleanState();
    if (editId) {
      router.replace("/horoscope");
    }
  }, [editId, resetFormToCleanState, router]);

  // Enforce 100% fresh, blank form state whenever opening this page for new horoscope creation
  useEffect(() => {
    if (!editId) {
      resetFormToCleanState();
    }
  }, [editId, resetFormToCleanState]);

  // Listen to browser pageshow events (e.g. Back/Forward navigation or bfcache restoration)
  useEffect(() => {
    const handlePageShow = (e: PageTransitionEvent) => {
      if (!editId || e.persisted) {
        if (!editId) {
          resetFormToCleanState();
        }
      }
    };

    window.addEventListener("pageshow", handlePageShow);
    return () => {
      window.removeEventListener("pageshow", handlePageShow);
    };
  }, [editId, resetFormToCleanState]);

  // Load existing horoscope details ONLY if edit_id is explicitly present in query parameters
  useEffect(() => {
    if (!editId) {
      return;
    }

    setIsEditMode(true);
    setIsLoadingEditData(true);
    setEditLoadError(null);

    fetch(`/api/horoscopes/${editId}`, { cache: "no-store" })
      .then(async (res) => {
        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.error || "Failed to load horoscope for editing.");
        }
        return res.json();
      })
      .then((data) => {
        const item = data.horoscope;
        if (!item) return;

        setFullName(item.person_name || "");
        const savedGender =
          (item as any).gender ||
          item.calculation_result?.clientInputs?.gender ||
          item.calculation_result?.customer?.gender ||
          item.calculation_result?.horoscope?.request?.gender ||
          "male";
        setGender(savedGender === "female" ? "female" : "male");
        setBirthDate(item.birth_date || "");
        setCountryCode(item.customer_country_code || item.country_code || "+91");
        setCustomerPhone(
          item.customer_phone || item.normalized_phone || item.whatsapp_number || ""
        );
        setCustomerId(item.customer_id || null);

        if (item.birth_time) {
          const parsed = parse24To12(item.birth_time);
          setBirthTime12(parsed.time12);
          setBirthPeriod(parsed.period);
        }

        setLocationQuery(item.birthplace || "");
        setLatitude(typeof item.latitude === "number" ? item.latitude : "");
        setLongitude(typeof item.longitude === "number" ? item.longitude : "");
        setTimezone(item.timezone || "Asia/Kolkata");
        if (typeof item.ayanamsa_id === "number") {
          setSelectedAyanamsa(item.ayanamsa_id);
        }
        if (typeof item.house_system_id === "number") {
          setSelectedHouseSystem(item.house_system_id);
        }
        setEditingDisplayNumber(item.display_number || null);
      })
      .catch((err) => {
        console.error("Error loading horoscope for editing:", err);
        setEditLoadError(err.message || "Failed to load horoscope for editing.");
      })
      .finally(() => {
        setIsLoadingEditData(false);
      });
  }, [editId]);

  // Fetch backend metadata options on mount
  useEffect(() => {
    getMetadata()
      .then((data: MetadataResponse) => {
        if (data.supported_ayanamsas && data.supported_ayanamsas.length > 0) {
          setAyanamsas(data.supported_ayanamsas);
          const defaultAya = data.supported_ayanamsas.find((a) => a.is_default);
          if (defaultAya) setSelectedAyanamsa(defaultAya.id);
        }
        if (data.supported_house_systems && data.supported_house_systems.length > 0) {
          setHouseSystems(data.supported_house_systems);
          const defaultHs = data.supported_house_systems.find((h) => h.is_default);
          if (defaultHs) setSelectedHouseSystem(defaultHs.id);
        }
      })
      .catch((err) => {
        console.warn("Could not load backend metadata options:", err);
      });

    // Fetch existing customers to enable automatic profile reuse
    if (isAuthenticated) {
      fetch("/api/customers")
        .then((res) => (res.ok ? res.json() : null))
        .then((data) => {
          if (data?.customers) {
            setSavedCustomers(data.customers);
          }
        })
        .catch((err) => console.warn("Could not load existing customers:", err));
    }
  }, [isAuthenticated]);

  // Handle selecting an existing customer
  const handleSelectCustomer = (customer: any) => {
    setFullName(customer.full_name || "");
    if (customer.gender) {
      setGender(customer.gender === "female" ? "female" : "male");
    }
    setBirthDate(customer.birth_date || "");
    setCountryCode(customer.country_code || "+91");
    setCustomerPhone(customer.phone_number || customer.normalized_phone || "");
    setCustomerId(customer.id);
    if (customer.birth_time) {
      const parsed = parse24To12(customer.birth_time);
      setBirthTime12(parsed.time12);
      setBirthPeriod(parsed.period);
    }
    setShowCustomerDropdown(false);
    setErrors((prev) => ({
      ...prev,
      fullName: "",
      birthDate: "",
      customerPhone: "",
      birthTime: "",
    }));
  };

  // Handle location search input with debounce
  const handleLocationQueryChange = (text: string) => {
    setLocationQuery(text);
    setErrors((prev) => ({ ...prev, location: "" }));

    if (locationSearchTimeout.current) {
      clearTimeout(locationSearchTimeout.current);
    }

    if (text.trim().length < 2) {
      setLocationResults([]);
      setShowLocationDropdown(false);
      return;
    }

    setIsSearchingLocation(true);
    locationSearchTimeout.current = setTimeout(async () => {
      try {
        const results = await searchLocations(text);
        setLocationResults(results);
        setShowLocationDropdown(true);
      } catch (err) {
        console.error("Geocoding failed:", err);
      } finally {
        setIsSearchingLocation(false);
      }
    }, 350);
  };

  const handleSelectLocation = (loc: LocationSearchResult) => {
    setLocationQuery(loc.displayName);
    setLatitude(loc.latitude);
    setLongitude(loc.longitude);
    if (loc.estimatedTimezone) {
      setTimezone(loc.estimatedTimezone);
    }
    setShowLocationDropdown(false);
    setErrors((prev) => ({ ...prev, location: "", latitude: "", longitude: "" }));
  };

  // Form Validation
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // 1. Mandatory Customer Full Name
    if (!fullName.trim()) {
      newErrors.fullName =
        language === "ta"
          ? "வாடிக்கையாளர் முழுப் பெயர் தேவை."
          : "Customer Full Name is required.";
    }

    // 2. Mandatory Date of Birth
    if (!birthDate) {
      newErrors.birthDate =
        language === "ta" ? "பிறந்த தேதி தேவை." : t.valDateRequired;
    }

    // 3. Optional Customer WhatsApp Number
    if (customerPhone.trim()) {
      const pVal = validateAndNormalizePhone(customerPhone, countryCode);
      if (!pVal.isValid) {
        newErrors.customerPhone =
          pVal.error ||
          (language === "ta"
            ? "செல்லுபடியற்ற வாட்ஸ்அப் எண்."
            : "Invalid WhatsApp phone number.");
      }
    }

    if (isTimeConfirmed) {
      if (!birthTime12.trim()) {
        newErrors.birthTime =
          language === "ta"
            ? "சரியான பிறந்த நேரத்தை உள்ளிடவும் (எ.கா: 10:30)."
            : t.valTimeRequired;
      } else {
        const parsed = parse12HourTimeTo24(birthTime12, birthPeriod);
        if (!parsed.isValid) {
          newErrors.birthTime =
            language === "ta"
              ? parsed.errorTa || "செல்லுபடியற்ற பிறந்த நேரம் (01:00 முதல் 12:59 வரை இருக்க வேண்டும்)."
              : parsed.errorEn || "Please enter a valid 12-hour birth time (01:00 to 12:59) with AM or PM.";
        }
      }
    }

    if (latitude === "" || isNaN(Number(latitude)) || Number(latitude) < -90 || Number(latitude) > 90) {
      newErrors.latitude = t.valLatInvalid;
    }

    if (longitude === "" || isNaN(Number(longitude)) || Number(longitude) < -180 || Number(longitude) > 180) {
      newErrors.longitude = t.valLonInvalid;
    }

    if (!timezone.trim()) {
      newErrors.timezone = t.valTzRequired;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle Submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setCalculationError(null);

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    // If time is unconfirmed, standard astronomical default is 12:00:00 PM local
    let formattedTime = "12:00:00";
    if (isTimeConfirmed) {
      const parsed = parse12HourTimeTo24(birthTime12, birthPeriod);
      if (!parsed.isValid || !parsed.time24) {
        setErrors((prev) => ({
          ...prev,
          birthTime:
            language === "ta"
              ? parsed.errorTa || "செல்லுபடியற்ற பிறந்த நேரம்."
              : parsed.errorEn || "Please enter a valid 12-hour birth time.",
        }));
        setIsSubmitting(false);
        return;
      }
      formattedTime = parsed.time24;
    }

    try {
      const fullResult = await calculateFullHoroscopeSuite({
        fullName: fullName.trim() || undefined,
        gender,
        birthDate,
        birthTime: formattedTime,
        isTimeConfirmed,
        locationName: locationQuery.trim() || `Coordinates: ${latitude}, ${longitude}`,
        latitude: Number(latitude),
        longitude: Number(longitude),
        timezone: timezone.trim(),
        ayanamsaId: selectedAyanamsa,
        houseSystemId: selectedHouseSystem,
        includePanchang,
        includeOuterPlanets,
      });

      // Saving Workflow: If editing an existing horoscope, update it in-place via PUT
      // (replacing the data without creating duplicate records).
      // If creating fresh, insert a new record via POST.
      let savedId: string | undefined = undefined;
      let displayNumber: number | undefined = undefined;
      let isSaved = false;
      let saveErrorMsg: string | undefined = undefined;

      const idempotencyKey = `calc_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

      if (isEditMode && editId) {
        try {
          const compactedSnapshot = prepareCalculationSnapshot(fullResult, idempotencyKey);
          const updateRes = await fetch(`/api/horoscopes/${editId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              person_name: fullName.trim(),
              customer_full_name: fullName.trim(),
              gender,
              birth_date: birthDate,
              birth_time: formattedTime,
              customer_phone: customerPhone.trim(),
              country_code: countryCode,
              customer_id: customerId || undefined,
              timezone: timezone.trim(),
              birthplace: locationQuery.trim() || `Coordinates: ${latitude}, ${longitude}`,
              latitude: Number(latitude),
              longitude: Number(longitude),
              ayanamsa_id: selectedAyanamsa,
              house_system_id: selectedHouseSystem,
              calculation_result: compactedSnapshot,
            }),
          });

          if (updateRes.ok) {
            const updateData = await updateRes.json();
            savedId = updateData.horoscope?.id || editId;
            displayNumber = updateData.horoscope?.display_number || editingDisplayNumber || undefined;
            isSaved = true;
          } else {
            const errData = await updateRes.json().catch(() => ({}));
            saveErrorMsg = errData.error || "Failed to update horoscope record.";
          }
        } catch (updateErr: any) {
          console.error("Failed to update existing horoscope in-place:", updateErr);
          saveErrorMsg = updateErr?.message || "Network error during horoscope update.";
        }
      } else {
        try {
          const compactedSnapshot = prepareCalculationSnapshot(fullResult, idempotencyKey);
          const saveRes = await fetch("/api/horoscopes", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              idempotency_key: idempotencyKey,
              person_name: fullName.trim(),
              customer_full_name: fullName.trim(),
              gender,
              birth_date: birthDate,
              customer_phone: customerPhone.trim(),
              country_code: countryCode,
              customer_id: customerId || undefined,
              birth_time: formattedTime,
              timezone: timezone.trim(),
              birthplace: locationQuery.trim() || `Coordinates: ${latitude}, ${longitude}`,
              latitude: Number(latitude),
              longitude: Number(longitude),
              ayanamsa_id: selectedAyanamsa,
              house_system_id: selectedHouseSystem,
              calculation_result: compactedSnapshot,
            }),
          });

          if (saveRes.ok) {
            const saveData = await saveRes.json();
            if (saveData.horoscope) {
              savedId = saveData.horoscope.id;
              displayNumber = saveData.horoscope.display_number;
              isSaved = true;
            }
          } else {
            const errData = await saveRes.json().catch(() => ({}));
            // If 401 unauthorized, user is simply an unauthenticated guest; don't report error
            if (saveRes.status === 401) {
              saveErrorMsg = undefined;
            } else {
              saveErrorMsg = errData.error || "Automatic save failed.";
            }
          }
        } catch (saveErr: any) {
          console.warn("Auto-save attempt failed:", saveErr);
          saveErrorMsg = saveErr?.message || "Network error during automatic save.";
        }
      }

      const finalResult = {
        ...fullResult,
        savedId: savedId || (isEditMode && editId ? editId : undefined),
        displayNumber: displayNumber || (isEditMode && editingDisplayNumber ? editingDisplayNumber : undefined),
        isSaved,
        saveError: saveErrorMsg,
        idempotencyKey,
      };

      // Save to client-side session cache safely without URL exposure
      saveActiveCalculation(finalResult);

      // Navigate to results
      const destId = savedId || (isEditMode && editId ? editId : undefined);
      if (destId) {
        router.push(`/horoscope/results?id=${destId}`);
      } else {
        router.push("/horoscope/results");
      }
    } catch (err: unknown) {
      console.error("Calculation failure:", err);
      if (err instanceof ApiError) {
        if (err.data?.validation_errors && err.data.validation_errors.length > 0) {
          const detailStr = err.data.validation_errors
            .map((v) => `${v.field}: ${v.message}`)
            .join(" | ");
          setCalculationError(`${err.message} (${detailStr})`);
        } else {
          setCalculationError(err.message);
        }
      } else {
        setCalculationError(
          language === "ta"
            ? "கணக்கீட்டு சேவையகத்தை இணைக்க முடியவில்லை. தயவுசெய்து backend இயங்குகிறதா என சரிபார்க்கவும்."
            : "Failed to connect to backend engine. Please check if the backend service is running."
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoadingEditData) {
    return (
      <div className="min-h-[calc(100vh-14rem)] flex flex-col items-center justify-center p-8 space-y-4 bg-[#FAF8F5]">
        <Loader2 className="w-8 h-8 animate-spin text-[#B8860B]" />
        <p className="text-sm font-semibold text-[#102A4C]">
          {language === "ta"
            ? "ஜாதக விவரங்கள் ஏற்றப்படுகின்றன..."
            : "Loading horoscope details for editing..."}
        </p>
      </div>
    );
  }

  if (editLoadError) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center space-y-4">
        <AlertCircle className="w-10 h-10 text-rose-600 mx-auto" />
        <h2 className="text-lg font-bold text-slate-800">
          {language === "ta" ? "ஜாதகத்தை ஏற்ற முடியவில்லை" : "Could not load horoscope"}
        </h2>
        <p className="text-sm text-slate-600">{editLoadError}</p>
        <Link
          href="/horoscopes"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[#102A4C] text-white text-xs font-semibold hover:bg-[#1E3A61]"
        >
          {language === "ta" ? "எனது ஜாதகங்கள்" : "Back to My Horoscopes"}
        </Link>
      </div>
    );
  }

  return (
    <div className="w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 sm:py-8 space-y-8">
      {/* Navigation Breadcrumbs & Back Link */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <Breadcrumbs
          items={[
            {
              label: language === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools",
              href: "/tools",
            },
            {
              label: language === "ta" ? "எனது ஜாதகங்கள்" : "My Horoscopes",
              href: "/horoscopes",
            },
            ...(isEditMode
              ? [
                  {
                    label:
                      language === "ta"
                        ? `ஜாதக எண் ${editingDisplayNumber || ""} திருத்துதல்`
                        : `Edit Horoscope No. ${editingDisplayNumber || ""}`,
                  },
                ]
              : [
                  {
                    label: language === "ta" ? "ஜாதகம் கணிக்க" : "Create Horoscope",
                  },
                ]),
          ]}
        />

        <Link
          href={isEditMode && editId ? `/horoscope/results?id=${editId}` : "/tools/horoscope"}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#52667E] hover:text-[#102A4C] transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>
            {isEditMode
              ? (language === "ta" ? "ஜாதக முடிவுகளுக்குத் திரும்பு" : "Return to Horoscope View")
              : (language === "ta" ? "ஜாதகக் கருவிகள் அடைவு" : "Back to Horoscope / KP Tools")}
          </span>
        </Link>
      </div>

      {/* Edit Mode Notification Banner */}
      {isEditMode && (
        <div className="p-4 rounded-xl bg-amber-50 border border-amber-300 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-amber-900 shadow-2xs">
          <div className="flex items-start sm:items-center gap-3">
            <Edit3 className="w-5 h-5 text-amber-700 shrink-0 mt-0.5 sm:mt-0" />
            <div>
              <div className="font-bold text-sm">
                {language === "ta"
                  ? `ஜாதக எண் ${editingDisplayNumber || ""} (${fullName || "—"}) திருத்துதல்`
                  : `Editing Horoscope No. ${editingDisplayNumber || ""} (${fullName || "Unnamed"})`}
              </div>
              <p className="text-xs text-amber-800/90 mt-0.5 leading-relaxed">
                {language === "ta"
                  ? "நீங்கள் செய்யும் மாற்றங்கள் இந்த ஜாதகத்தின் முந்தைய தரவை நேரடியாக மாற்றியமைக்கும் (Replace). புதிய இரட்டை ஜாதகம் (Duplicate) உருவாகாது."
                  : "Any edits you make will replace this horoscope's data in-place without creating a duplicate record."}
              </p>
            </div>
          </div>
          {editId && (
            <Link
              href={`/horoscope/results?id=${editId}`}
              className="px-3 py-1.5 rounded-lg border border-amber-400 bg-white hover:bg-amber-100 text-amber-900 text-xs font-semibold shrink-0 transition-colors"
            >
              {language === "ta" ? "ரத்து / பின்செல்க" : "Cancel & View"}
            </Link>
          )}
        </div>
      )}

      {/* Page Header */}
      <div className="text-center max-w-2xl mx-auto mb-10">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#FAF2DE] border border-[#D8BD80] text-xs font-semibold text-[#8C6D23] mb-3">
          <Compass className="w-3.5 h-3.5" />
          <span>
            {isEditMode
              ? (language === "ta" ? `ஜாதக எண் ${editingDisplayNumber || ""} திருத்துதல்` : `Edit Horoscope No. ${editingDisplayNumber || ""}`)
              : (language === "ta" ? "ஜாதகக் கணிப்பு படிவம்" : "Horoscope Input Form")}
          </span>
        </div>
        <h1 className="font-serif text-2xl sm:text-3xl md:text-4xl font-bold text-[#0F172A]">
          {isEditMode
            ? (language === "ta" ? `ஜாதகத்தைத் திருத்துக (எண் ${editingDisplayNumber || ""})` : `Edit Horoscope (No. ${editingDisplayNumber || ""})`)
            : t.formTitle}
        </h1>
        <p className="mt-2 text-xs sm:text-sm text-[#64748B]">
          {isEditMode
            ? (language === "ta"
                ? "பிறப்பு விவரங்கள் அல்லது அமைப்புகளை மாற்றி புதிய கணிப்புகளை இந்த ஜாதகத்தில் சேமிக்கலாம்."
                : "Modify birth information or calculation parameters to replace this horoscope's data.")
            : t.formSubtitle}
        </p>
      </div>

      {/* Global Error Notice if calculation failed */}
      {calculationError && (
        <div className="mb-8 p-4 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div className="flex-1">
            <h4 className="font-bold text-rose-900">{t.error}</h4>
            <p className="text-xs mt-1 leading-relaxed">{calculationError}</p>
          </div>
        </div>
      )}

      {/* Main Form Card */}
      <form
        ref={formRef}
        onSubmit={handleSubmit}
        className="bg-white rounded-xl border border-[#E2DCD5] shadow-xs p-6 sm:p-8 space-y-8"
        noValidate
        autoComplete="off"
      >
        {/* SECTION 1: Personal & Time */}
        <div className="space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-[#E2DCD5]">
            <div className="flex items-center gap-2">
              <User className="w-4 h-4 text-[#B8860B]" />
              <h3 className="font-serif text-sm font-bold uppercase tracking-wider text-[#0F172A]">
                {t.sectionPersonal}
              </h3>
            </div>
            <button
              type="button"
              onClick={handleManualClear}
              className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
              title="Reset all fields to clean empty form"
            >
              <RotateCcw className="w-3.5 h-3.5 text-slate-400" />
              <span>
                {isEditMode
                  ? (language === "ta" ? "புதிய படிவத்திற்கு மாறுக (Start Clean Form)" : "Start Clean New Form")
                  : (language === "ta" ? "படிவத்தை சுத்தப்படுத்துக (Clear All)" : "Clear Form")}
              </span>
            </button>
          </div>

          {/* Existing Client Selector */}
          {savedCustomers.length > 0 && (
            <div className="p-3 bg-[#FAF8F5] border border-[#E2DCD5] rounded-lg">
              <div className="flex items-center justify-between mb-1.5">
                <label htmlFor="customerSelect" className="text-xs font-bold text-[#102A4C] flex items-center gap-1.5">
                  <Users className="w-3.5 h-3.5 text-[#B8860B]" />
                  <span>{language === "ta" ? "முந்தைய வாடிக்கையாளர் தேர்வு" : "Returning Customer / Existing Client"}</span>
                </label>
                {customerId && (
                  <button
                    type="button"
                    onClick={() => {
                      setCustomerId(null);
                      setFullName("");
                      setBirthDate("");
                      setCustomerPhone("");
                      setBirthTime12("");
                      setBirthPeriod("AM");
                    }}
                    className="text-[11px] font-semibold text-rose-600 hover:underline cursor-pointer"
                  >
                    {language === "ta" ? "புதிய வாடிக்கையாளர் (Reset)" : "Clear / New Customer"}
                  </button>
                )}
              </div>
              <select
                id="customerSelect"
                name="customer_select_clean"
                autoComplete="off"
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
                className="w-full px-3 py-2 text-xs rounded-lg border border-[#D8BD80] bg-white text-[#0F172A] focus:ring-1 focus:ring-[#B8860B]"
              >
                <option value="">
                  {language === "ta"
                    ? "-- புதிய வாடிக்கையாளர் (அல்லது பட்டியலிலிருந்து தேர்வு செய்க) --"
                    : "-- Select Saved Customer (or enter new details below) --"}
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
                      : "Authoritative client profile linked. Horoscope will be saved under this customer."}
                  </span>
                </p>
              )}
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Customer Full Name */}
            <div>
              <label htmlFor="fullName" className="block text-xs font-semibold text-[#334155] mb-1">
                {language === "ta" ? "வாடிக்கையாளர் முழுப் பெயர்" : "Customer Full Name"}{" "}
                <span className="text-rose-600">*</span>
              </label>
              <input
                id="fullName"
                name="person_full_name_clean"
                type="text"
                required
                autoComplete="off"
                autoCorrect="off"
                spellCheck={false}
                data-form-type="other"
                data-lpignore="true"
                value={fullName}
                onChange={(e) => {
                  setFullName(e.target.value);
                  setErrors((prev) => ({ ...prev, fullName: "" }));
                }}
                placeholder={t.fieldNamePlaceholder}
                className={`w-full px-3.5 py-2.5 rounded-lg border text-sm text-[#0F172A] bg-[#FFFDF9] placeholder:text-[#94A3B8] focus:ring-1 ${
                  errors.fullName
                    ? "border-rose-500 focus:border-rose-500 focus:ring-rose-500"
                    : "border-[#D8BD80]/80 focus:border-[#B8860B] focus:ring-[#B8860B]"
                }`}
              />
              {errors.fullName && (
                <p className="mt-1 text-xs text-rose-600">{errors.fullName}</p>
              )}
            </div>

            {/* Gender Selection */}
            <div>
              <label className="block text-xs font-semibold text-[#334155] mb-1">
                {language === "ta" ? "பாலினம் (Gender)" : "Gender"}{" "}
                <span className="text-rose-600">*</span>
              </label>
              <div className="grid grid-cols-2 gap-2 h-[42px]">
                <button
                  type="button"
                  onClick={() => setGender("male")}
                  className={`flex items-center justify-center gap-2 px-3 py-2 rounded-lg border text-xs font-bold transition-all cursor-pointer ${
                    gender === "male"
                      ? "bg-[#102A4C] text-white border-[#102A4C] shadow-sm ring-2 ring-[#B8860B]/40"
                      : "bg-[#FFFDF9] text-[#334155] border-[#D8BD80]/80 hover:bg-[#F5F2EB]"
                  }`}
                >
                  <span className="text-sm">👨</span>
                  <span>{language === "ta" ? "ஆண் (Male)" : "Male"}</span>
                </button>
                <button
                  type="button"
                  onClick={() => setGender("female")}
                  className={`flex items-center justify-center gap-2 px-3 py-2 rounded-lg border text-xs font-bold transition-all cursor-pointer ${
                    gender === "female"
                      ? "bg-[#881337] text-white border-[#881337] shadow-sm ring-2 ring-[#B8860B]/40"
                      : "bg-[#FFFDF9] text-[#334155] border-[#D8BD80]/80 hover:bg-[#F5F2EB]"
                  }`}
                >
                  <span className="text-sm">👩</span>
                  <span>{language === "ta" ? "பெண் (Female)" : "Female"}</span>
                </button>
              </div>
            </div>


            {/* Customer WhatsApp Number & Country Code (Optional) */}
            <div>
              <label htmlFor="customerPhone" className="block text-xs font-semibold text-[#334155] mb-1">
                {language === "ta" ? "வாட்ஸ்அப் எண் (விருப்பத்தேர்வு)" : "Customer WhatsApp Number (Optional)"}
              </label>
              <div className="flex gap-2">
                <select
                  id="countryCode"
                  name="country_code_clean"
                  autoComplete="off"
                  value={countryCode}
                  onChange={(e) => {
                    setCountryCode(e.target.value);
                    setErrors((prev) => ({ ...prev, customerPhone: "" }));
                  }}
                  className="w-28 sm:w-32 px-2 py-2.5 rounded-lg border border-[#D8BD80]/80 bg-[#FFFDF9] text-xs font-medium text-[#0F172A] focus:border-[#B8860B] focus:ring-1 focus:ring-[#B8860B]"
                >
                  {SUPPORTED_COUNTRY_CODES.map((item) => (
                    <option key={item.code} value={item.code}>
                      {item.flag} {item.code}
                    </option>
                  ))}
                </select>
                <div className="flex-1 relative">
                  <input
                    id="customerPhone"
                    name="customer_phone_clean"
                    type="tel"
                    autoComplete="off"
                    autoCorrect="off"
                    spellCheck={false}
                    data-form-type="other"
                    data-lpignore="true"
                    value={customerPhone}
                    onChange={(e) => {
                      setCustomerPhone(e.target.value);
                      setErrors((prev) => ({ ...prev, customerPhone: "" }));
                    }}
                    placeholder={countryCode === "+91" ? "98765 43210 (Optional)" : "Phone number (Optional)"}
                    className={`w-full px-3.5 py-2.5 rounded-lg border text-sm text-[#0F172A] bg-[#FFFDF9] focus:ring-1 ${
                      errors.customerPhone
                        ? "border-rose-500 focus:border-rose-500 focus:ring-rose-500"
                        : "border-[#D8BD80]/80 focus:border-[#B8860B] focus:ring-[#B8860B]"
                    }`}
                  />
                </div>
              </div>
              {errors.customerPhone ? (
                <p className="mt-1 text-xs text-rose-600">{errors.customerPhone}</p>
              ) : (
                <p className="mt-1 text-[11px] text-[#64748B]">
                  {language === "ta"
                    ? "விருப்பத்தேர்வு: பிறந்தநாள் வாழ்த்துக்கள் & வாட்ஸ்அப் தொடர்புக்கு பயன்படுத்தப்படுகிறது."
                    : "Optional: Used for birthday reminders and WhatsApp wishes."}
                </p>
              )}
            </div>

            {/* Birth Date */}
            <div>
              <label htmlFor="birthDate" className="block text-xs font-semibold text-[#334155] mb-1">
                {t.fieldDate} <span className="text-rose-600">*</span>
              </label>
              <input
                id="birthDate"
                name="birth_date_clean"
                type="date"
                required
                autoComplete="off"
                data-form-type="other"
                data-lpignore="true"
                value={birthDate}
                onChange={(e) => {
                  setBirthDate(e.target.value);
                  setErrors((prev) => ({ ...prev, birthDate: "" }));
                }}
                className={`w-full px-3.5 py-2.5 rounded-lg border text-sm text-[#0F172A] bg-[#FFFDF9] focus:ring-1 ${
                  errors.birthDate
                    ? "border-rose-500 focus:border-rose-500 focus:ring-rose-500"
                    : "border-[#D8BD80]/80 focus:border-[#B8860B] focus:ring-[#B8860B]"
                }`}
              />
              {errors.birthDate && (
                <p className="mt-1 text-xs text-rose-600">{errors.birthDate}</p>
              )}
            </div>

            {/* Birth Time (12 hrs with AM or PM drop down) */}
            <div>
              <label htmlFor="birthTime12" className="block text-xs font-semibold text-[#334155] mb-1">
                {t.fieldTime} {isTimeConfirmed && <span className="text-rose-600">*</span>}
              </label>
              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <input
                    id="birthTime12"
                    name="birth_time_clean"
                    type="text"
                    autoComplete="off"
                    autoCorrect="off"
                    spellCheck={false}
                    data-form-type="other"
                    data-lpignore="true"
                    disabled={!isTimeConfirmed}
                    value={birthTime12}
                    onChange={(e) => {
                      let val = e.target.value;
                      if (/pm/i.test(val)) {
                        setBirthPeriod("PM");
                        val = val.replace(/pm/gi, "").trim();
                      } else if (/am/i.test(val)) {
                        setBirthPeriod("AM");
                        val = val.replace(/am/gi, "").trim();
                      }
                      setBirthTime12(val);
                      setErrors((prev) => ({ ...prev, birthTime: "" }));
                    }}
                    placeholder={language === "ta" ? "10:30 அல்லது 10:30:00" : "10:30 or 10:30:00"}
                    className={`w-full px-3.5 py-2.5 rounded-lg border text-sm font-mono text-[#0F172A] bg-[#FFFDF9] disabled:bg-[#F1EBE4] disabled:text-[#94A3B8] focus:ring-1 ${
                      errors.birthTime
                        ? "border-rose-500 focus:border-rose-500 focus:ring-rose-500"
                        : "border-[#D8BD80]/80 focus:border-[#B8860B] focus:ring-[#B8860B]"
                    }`}
                  />
                </div>
                <select
                  id="birthPeriod"
                  name="birth_period_clean"
                  autoComplete="off"
                  disabled={!isTimeConfirmed}
                  value={birthPeriod}
                  onChange={(e) => {
                    setBirthPeriod(e.target.value as "AM" | "PM");
                    setErrors((prev) => ({ ...prev, birthTime: "" }));
                  }}
                  className="w-24 sm:w-28 px-3 py-2.5 rounded-lg border border-[#D8BD80]/80 bg-[#FFFDF9] text-sm font-semibold text-[#0F172A] disabled:bg-[#F1EBE4] disabled:text-[#94A3B8] focus:border-[#B8860B] focus:ring-1 focus:ring-[#B8860B]"
                >
                  <option value="AM">AM</option>
                  <option value="PM">PM</option>
                </select>
              </div>
              {errors.birthTime ? (
                <p className="mt-1 text-xs text-rose-600">{errors.birthTime}</p>
              ) : (
                <p className="mt-1 text-[11px] text-[#64748B]">
                  {language === "ta"
                    ? "12 மணி நேர வடிவம் (எ.கா: 10:30 அல்லது 10:30:00) மற்றும் AM / PM தேர்ந்தெடுக்கவும்."
                    : "12-hour format (e.g. 10:30 or 10:30:00) with AM / PM dropdown."}
                </p>
              )}
            </div>

            {/* Time Confirmation Toggle */}
            <div className="flex flex-col justify-center sm:col-span-2 pt-1">
              <label className="flex items-center gap-2 text-xs font-medium text-[#334155] cursor-pointer">
                <input
                  type="checkbox"
                  checked={isTimeConfirmed}
                  onChange={(e) => setIsTimeConfirmed(e.target.checked)}
                  className="w-4 h-4 rounded text-[#B8860B] border-[#D8BD80] focus:ring-[#B8860B]"
                />
                <span>{t.fieldTimeConfirmed}</span>
              </label>

              {!isTimeConfirmed && (
                <div className="mt-2 p-2.5 rounded bg-[#FAF6EC] border border-[#E8DEC8] text-[11px] text-[#784E0E] leading-relaxed">
                  {t.fieldTimeUnknownNotice}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* SECTION 2: Location & Coordinates */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-[#E2DCD5]">
            <MapPin className="w-4 h-4 text-[#B8860B]" />
            <h3 className="font-serif text-sm font-bold uppercase tracking-wider text-[#0F172A]">
              {t.sectionLocation}
            </h3>
          </div>

          {/* Place Search */}
          <div className="relative">
            <label htmlFor="placeSearch" className="block text-xs font-semibold text-[#334155] mb-1">
              {t.fieldPlace} <span className="text-rose-600">*</span>
            </label>
            <div className="relative">
              <input
                id="placeSearch"
                name="place_search_clean"
                type="text"
                autoComplete="off"
                autoCorrect="off"
                spellCheck={false}
                data-form-type="other"
                data-lpignore="true"
                value={locationQuery}
                onChange={(e) => handleLocationQueryChange(e.target.value)}
                onFocus={() => {
                  if (locationResults.length > 0) setShowLocationDropdown(true);
                }}
                placeholder={t.fieldPlacePlaceholder}
                className="w-full pl-9 pr-4 py-2.5 rounded-lg border border-[#D8BD80]/80 bg-[#FFFDF9] text-sm text-[#0F172A] placeholder:text-[#94A3B8] focus:border-[#B8860B] focus:ring-1 focus:ring-[#B8860B]"
              />
              <Search className="w-4 h-4 text-[#94A3B8] absolute left-3 top-3.5" />
              {isSearchingLocation && (
                <Loader2 className="w-4 h-4 text-[#B8860B] animate-spin absolute right-3 top-3.5" />
              )}
            </div>

            {/* Dropdown Results */}
            {showLocationDropdown && locationResults.length > 0 && (
              <div className="absolute z-30 w-full mt-1 bg-white border border-[#D8BD80] rounded-lg shadow-lg max-h-60 overflow-y-auto divide-y divide-[#F1EBE4]">
                {locationResults.map((loc, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSelectLocation(loc)}
                    className="w-full text-left px-3.5 py-2.5 text-xs hover:bg-[#FAF6EC] flex items-center justify-between"
                  >
                    <div>
                      <span className="font-semibold text-[#0F172A]">
                        {loc.shortName}
                      </span>
                      <span className="text-[#64748B] ml-1.5 truncate block sm:inline">
                        {loc.displayName}
                      </span>
                    </div>
                    <div className="text-[10px] font-mono text-[#8C6D23] shrink-0 ml-2">
                      {loc.latitude.toFixed(2)}°, {loc.longitude.toFixed(2)}°
                    </div>
                  </button>
                ))}
                {locationResults.some((l) => l.provider === "osm-nominatim") && (
                  <div className="px-3.5 py-1.5 text-[10px] text-[#64748B] bg-[#FAF8F5] border-t border-[#F1EBE4] flex items-center justify-between">
                    <span>Location data</span>
                    <a
                      href="https://www.openstreetmap.org/copyright"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[#8C6D23] hover:underline"
                    >
                      © OpenStreetMap contributors
                    </a>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Coordinates and Timezone */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Latitude */}
            <div>
              <label htmlFor="latitude" className="block text-xs font-semibold text-[#334155] mb-1">
                {t.fieldLatitude} (-90 to +90) <span className="text-rose-600">*</span>
              </label>
              <input
                id="latitude"
                name="latitude_clean"
                type="number"
                step="0.0001"
                min="-90"
                max="90"
                required
                autoComplete="off"
                data-form-type="other"
                data-lpignore="true"
                value={latitude}
                onChange={(e) => {
                  setLatitude(e.target.value === "" ? "" : parseFloat(e.target.value));
                  setErrors((prev) => ({ ...prev, latitude: "" }));
                }}
                placeholder="e.g. 13.0827"
                className={`w-full px-3 py-2 rounded-lg border font-mono text-xs text-[#0F172A] bg-[#FFFDF9] ${
                  errors.latitude
                    ? "border-rose-500"
                    : "border-[#D8BD80]/80 focus:border-[#B8860B]"
                }`}
              />
              {errors.latitude && (
                <p className="mt-1 text-xs text-rose-600">{errors.latitude}</p>
              )}
            </div>

            {/* Longitude */}
            <div>
              <label htmlFor="longitude" className="block text-xs font-semibold text-[#334155] mb-1">
                {t.fieldLongitude} (-180 to +180) <span className="text-rose-600">*</span>
              </label>
              <input
                id="longitude"
                name="longitude_clean"
                type="number"
                step="0.0001"
                min="-180"
                max="180"
                required
                autoComplete="off"
                data-form-type="other"
                data-lpignore="true"
                value={longitude}
                onChange={(e) => {
                  setLongitude(e.target.value === "" ? "" : parseFloat(e.target.value));
                  setErrors((prev) => ({ ...prev, longitude: "" }));
                }}
                placeholder="e.g. 80.2707"
                className={`w-full px-3 py-2 rounded-lg border font-mono text-xs text-[#0F172A] bg-[#FFFDF9] ${
                  errors.longitude
                    ? "border-rose-500"
                    : "border-[#D8BD80]/80 focus:border-[#B8860B]"
                }`}
              />
              {errors.longitude && (
                <p className="mt-1 text-xs text-rose-600">{errors.longitude}</p>
              )}
            </div>

            {/* Timezone */}
            <div>
              <label htmlFor="timezone" className="block text-xs font-semibold text-[#334155] mb-1">
                {t.fieldTimezone} <span className="text-rose-600">*</span>
              </label>
              <select
                id="timezone"
                name="timezone_clean"
                autoComplete="off"
                value={timezone}
                onChange={(e) => {
                  setTimezone(e.target.value);
                  setErrors((prev) => ({ ...prev, timezone: "" }));
                }}
                className="w-full px-3 py-2 rounded-lg border border-[#D8BD80]/80 bg-[#FFFDF9] text-xs text-[#0F172A] focus:border-[#B8860B]"
              >
                {COMMON_TIMEZONES.map((tz) => (
                  <option key={tz.value} value={tz.value}>
                    {tz.label} ({tz.offset})
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* SECTION 3: Astronomical Settings */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-[#E2DCD5]">
            <Sliders className="w-4 h-4 text-[#B8860B]" />
            <h3 className="font-serif text-sm font-bold uppercase tracking-wider text-[#0F172A]">
              {t.sectionCalculations}
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Ayanamsa */}
            <div>
              <label htmlFor="ayanamsa" className="block text-xs font-semibold text-[#334155] mb-1">
                {t.fieldAyanamsa}
              </label>
              <select
                id="ayanamsa"
                name="ayanamsa_clean"
                autoComplete="off"
                value={selectedAyanamsa}
                onChange={(e) => setSelectedAyanamsa(parseInt(e.target.value, 10))}
                className="w-full px-3 py-2.5 rounded-lg border border-[#D8BD80]/80 bg-[#FFFDF9] text-xs text-[#0F172A] focus:border-[#B8860B]"
              >
                {ayanamsas.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.name} — {a.description}
                  </option>
                ))}
              </select>
            </div>

            {/* House System */}
            <div>
              <label htmlFor="houseSystem" className="block text-xs font-semibold text-[#334155] mb-1">
                {t.fieldHouseSystem}
              </label>
              <select
                id="houseSystem"
                name="house_system_clean"
                autoComplete="off"
                value={selectedHouseSystem}
                onChange={(e) => setSelectedHouseSystem(parseInt(e.target.value, 10))}
                className="w-full px-3 py-2.5 rounded-lg border border-[#D8BD80]/80 bg-[#FFFDF9] text-xs text-[#0F172A] focus:border-[#B8860B]"
              >
                {houseSystems.map((h) => (
                  <option key={h.id} value={h.id}>
                    {h.name} — {h.description}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Options Toggles */}
          <div className="pt-2 flex flex-col sm:flex-row gap-4">
            <label className="flex items-center gap-2 text-xs text-[#334155] cursor-pointer">
              <input
                type="checkbox"
                checked={includePanchang}
                onChange={(e) => setIncludePanchang(e.target.checked)}
                className="w-4 h-4 rounded text-[#B8860B] border-[#D8BD80] focus:ring-[#B8860B]"
              />
              <span>{t.fieldIncludePanchang}</span>
            </label>

            <label className="flex items-center gap-2 text-xs text-[#334155] cursor-pointer">
              <input
                type="checkbox"
                checked={includeOuterPlanets}
                onChange={(e) => setIncludeOuterPlanets(e.target.checked)}
                className="w-4 h-4 rounded text-[#B8860B] border-[#D8BD80] focus:ring-[#B8860B]"
              />
              <span>{t.fieldIncludeOuterPlanets}</span>
            </label>
          </div>
        </div>

        {/* Submit Button */}
        <div className="pt-4 border-t border-[#E8DEC8]">
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3.5 px-6 rounded-lg text-sm font-bold text-white bg-[#0F172A] hover:bg-[#1E293B] shadow-md transition-all flex items-center justify-center gap-2 disabled:opacity-75 disabled:cursor-not-allowed cursor-pointer"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-[#D8BD80]" />
                <span>
                  {isEditMode
                    ? (language === "ta" ? "கணக்கிட்டுப் புதுப்பிக்கப்படுகிறது..." : "Updating & Recalculating...")
                    : t.calculating}
                </span>
              </>
            ) : (
              <>
                {isEditMode ? (
                  <CheckCircle2 className="w-4 h-4 text-[#D8BD80]" />
                ) : (
                  <Compass className="w-4 h-4 text-[#D8BD80]" />
                )}
                <span>
                  {isEditMode
                    ? (language === "ta"
                        ? "ஜாதகத்தைப் புதுப்பித்துக் கணக்கிடுக (Replace Data)"
                        : "Update Horoscope (Replace Data)")
                    : t.submitButton}
                </span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

export default function HoroscopeFormPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-[calc(100vh-14rem)] flex items-center justify-center bg-[#FAF8F5]">
          <div className="w-8 h-8 border-4 border-[#B8860B] border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <HoroscopeFormContent />
    </Suspense>
  );
}
