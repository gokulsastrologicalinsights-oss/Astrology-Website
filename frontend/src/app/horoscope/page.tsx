"use client";

import React, { useState, useRef, Suspense } from "react";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { calculateFullHoroscopeSuite, ApiError } from "@/lib/api";
import { searchLocations, LocationSearchResult } from "@/lib/geocoding";
import { saveActiveCalculation } from "@/lib/storage";
import { AyanamsaOption } from "@/lib/types";
import { parse12HourTimeTo24 } from "@/lib/formatters";
import { DateInputDMY } from "@/components/common/DateInputDMY";
import { Compass, AlertCircle, Loader2, Search } from "lucide-react";

function HoroscopeFormContent() {
  const { language, t } = useLanguage();
  const router = useRouter();

  const [ayanamsas, setAyanamsas] = useState<AyanamsaOption[]>([
    { id: 0, name: "Lahiri (Chitrapaksha)", description: "Standard Government of India", is_default: true },
    { id: 1, name: "KP (Krishnamurti)", description: "Krishnamurti Paddhati", is_default: false },
    { id: 2, name: "Raman", description: "B.V. Raman Ayanamsa", is_default: false },
    { id: 3, name: "True Chitrapaksha", description: "True Spica 180°", is_default: false },
  ]);

  // Five-input form state
  const [fullName, setFullName] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [birthTime12, setBirthTime12] = useState("");
  const [birthPeriod, setBirthPeriod] = useState<"AM" | "PM">("AM");
  const [locationQuery, setLocationQuery] = useState("");
  const [gender, setGender] = useState<"male" | "female">("male");
  const [maritalStatus, setMaritalStatus] = useState<string>("unmarried");
  const [selectedAyanamsa, setSelectedAyanamsa] = useState<number>(0);

  // Internally resolved location coordinates & timezone
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

  const [locationResults, setLocationResults] = useState<LocationSearchResult[]>([]);
  const [isSearchingLocation, setIsSearchingLocation] = useState(false);
  const [showLocationDropdown, setShowLocationDropdown] = useState(false);

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [calculationError, setCalculationError] = useState<string | null>(null);

  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const handleLocationQueryChange = (val: string) => {
    setLocationQuery(val);
    setLatitude("");
    setLongitude("");
    setErrors((prev) => ({ ...prev, location: "" }));

    if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);

    if (val.trim().length < 2) {
      setLocationResults([]);
      setShowLocationDropdown(false);
      return;
    }

    searchTimeoutRef.current = setTimeout(async () => {
      setIsSearchingLocation(true);
      try {
        const results = await searchLocations(val);
        setLocationResults(results);
        setShowLocationDropdown(results.length > 0);
      } catch {
        setLocationResults([]);
      } finally {
        setIsSearchingLocation(false);
      }
    }, 350);
  };

  const handleSelectLocation = (loc: LocationSearchResult) => {
    setLocationQuery(loc.displayName);
    setLatitude(Number(loc.latitude.toFixed(4)));
    setLongitude(Number(loc.longitude.toFixed(4)));
    setShowLocationDropdown(false);
    setErrors((prev) => ({ ...prev, location: "" }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setCalculationError(null);

    const newErrors: Record<string, string> = {};
    if (!fullName.trim()) {
      newErrors.fullName =
        language === "ta" ? "பெயரை உள்ளிடவும்." : "Please enter a name.";
    }
    if (!birthDate) {
      newErrors.birthDate =
        language === "ta" ? "பிறந்த தேதியை உள்ளிடவும்." : "Please enter birth date.";
    }

    const parsedTime = parse12HourTimeTo24(birthTime12, birthPeriod);
    if (!parsedTime.isValid || !parsedTime.time24) {
      newErrors.birthTime =
        language === "ta"
          ? parsedTime.errorTa || "செல்லுபடியற்ற பிறந்த நேரம்."
          : parsedTime.errorEn || "Please enter a valid 12-hour birth time.";
    }

    if (latitude === "" || longitude === "") {
      newErrors.location =
        language === "ta"
          ? "பட்டியலிலிருந்து பிறந்த இடத்தைத் தேர்ந்தெடுக்கவும்."
          : "Please select a birthplace from the suggestions.";
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsSubmitting(true);
    try {
      const fullResult = await calculateFullHoroscopeSuite({
        fullName: fullName.trim(),
        birthDate,
        birthTime: parsedTime.time24!,
        isTimeConfirmed: true,
        locationName: locationQuery.trim(),
        latitude: Number(latitude),
        longitude: Number(longitude),
        timezone: timezone.trim(),
        ayanamsaId: selectedAyanamsa,
        houseSystemId: 2,
        includePanchang: true,
        includeOuterPlanets: false,
        gender,
        maritalStatus,
      });

      saveActiveCalculation(fullResult);

      router.push("/horoscope/results");
    } catch (err) {
      const msg =
        err instanceof ApiError
          ? err.message
          : err instanceof Error
          ? err.message
          : language === "ta"
          ? "ஜாதகம் கணக்கிடுவதில் பிழை ஏற்பட்டது."
          : "An error occurred while calculating the horoscope.";
      setCalculationError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-[650px] mx-auto px-4 py-6 sm:py-10">
      <div className="text-center mb-5">
        <h1 className="font-serif text-xl sm:text-2xl font-bold text-[#0F172A]">
          {language === "ta" ? "ஜாதகக் கணிப்பு" : t.formTitle}
        </h1>
        <p className="mt-1 text-xs text-[#64748B]">
          {language === "ta"
            ? "பிறப்பு விவரங்களை உள்ளிட்டு ஜாதகத்தைக் கணக்கிடவும்."
            : "Enter birth details to calculate the horoscope."}
        </p>
      </div>

      {calculationError && (
        <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-start gap-2.5">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
          <p className="leading-relaxed">{calculationError}</p>
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        className="bg-white rounded-xl border border-[#E2DCD5] shadow-sm p-5 sm:p-6 space-y-4"
        noValidate
        autoComplete="off"
      >
        {/* 1. Name */}
        <div>
          <label htmlFor="fullName" className="block text-xs font-semibold text-[#334155] mb-1">
            {language === "ta" ? "பெயர்" : "Name"} <span className="text-rose-600">*</span>
          </label>
          <input
            id="fullName"
            name="person_full_name_clean"
            type="text"
            required
            autoComplete="off"
            value={fullName}
            onChange={(e) => {
              setFullName(e.target.value);
              setErrors((prev) => ({ ...prev, fullName: "" }));
            }}
            placeholder={t.fieldNamePlaceholder}
            className={`w-full h-11 px-3.5 rounded-lg border text-sm text-[#0F172A] bg-[#FFFDF9] placeholder:text-[#94A3B8] focus:ring-1 ${
              errors.fullName
                ? "border-rose-500 focus:border-rose-500 focus:ring-rose-500"
                : "border-[#D8BD80]/80 focus:border-[#B8860B] focus:ring-[#B8860B]"
            }`}
          />
          {errors.fullName && <p className="mt-1 text-xs text-rose-600">{errors.fullName}</p>}
        </div>

        {/* 2. DOB & 3. TOB */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label htmlFor="birthDate" className="block text-xs font-semibold text-[#334155] mb-1">
              {language === "ta" ? "பிறந்த தேதி" : "Date of Birth"}{" "}
              <span className="text-rose-600">*</span>
            </label>
            <DateInputDMY
              id="birthDate"
              name="birth_date_clean"
              required
              autoComplete="off"
              language={language}
              value={birthDate}
              onChange={(e) => {
                setBirthDate(e.target.value);
                setErrors((prev) => ({ ...prev, birthDate: "" }));
              }}
              className={`w-full h-11 px-3.5 rounded-lg border text-sm text-[#0F172A] bg-[#FFFDF9] focus:ring-1 ${
                errors.birthDate
                  ? "border-rose-500 focus:border-rose-500 focus:ring-rose-500"
                  : "border-[#D8BD80]/80 focus:border-[#B8860B] focus:ring-[#B8860B]"
              }`}
            />
            {errors.birthDate && <p className="mt-1 text-xs text-rose-600">{errors.birthDate}</p>}
          </div>

          <div>
            <label htmlFor="birthTime12" className="block text-xs font-semibold text-[#334155] mb-1">
              {language === "ta" ? "பிறந்த நேரம்" : "Time of Birth"}{" "}
              <span className="text-rose-600">*</span>
            </label>
            <div className="flex gap-2">
              <input
                id="birthTime12"
                name="birth_time_clean"
                type="text"
                autoComplete="off"
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
                placeholder={language === "ta" ? "10:30" : "10:30"}
                className={`flex-1 h-11 px-3.5 rounded-lg border text-sm font-mono text-[#0F172A] bg-[#FFFDF9] focus:ring-1 ${
                  errors.birthTime
                    ? "border-rose-500 focus:border-rose-500 focus:ring-rose-500"
                    : "border-[#D8BD80]/80 focus:border-[#B8860B] focus:ring-[#B8860B]"
                }`}
              />
              <select
                id="birthPeriod"
                name="birth_period_clean"
                autoComplete="off"
                value={birthPeriod}
                onChange={(e) => {
                  setBirthPeriod(e.target.value as "AM" | "PM");
                  setErrors((prev) => ({ ...prev, birthTime: "" }));
                }}
                className="w-20 h-11 px-2.5 rounded-lg border border-[#D8BD80]/80 bg-[#FFFDF9] text-sm font-semibold text-[#0F172A] focus:border-[#B8860B] focus:ring-1 focus:ring-[#B8860B]"
              >
                <option value="AM">AM</option>
                <option value="PM">PM</option>
              </select>
            </div>
            {errors.birthTime && <p className="mt-1 text-xs text-rose-600">{errors.birthTime}</p>}
          </div>
        </div>

        {/* 4. Place of Birth */}
        <div className="relative">
          <label htmlFor="placeSearch" className="block text-xs font-semibold text-[#334155] mb-1">
            {language === "ta" ? "பிறந்த இடம்" : "Place of Birth"}{" "}
            <span className="text-rose-600">*</span>
          </label>
          <div className="relative">
            <input
              id="placeSearch"
              name="place_search_clean"
              type="text"
              autoComplete="off"
              value={locationQuery}
              onChange={(e) => handleLocationQueryChange(e.target.value)}
              onFocus={() => {
                if (locationResults.length > 0) setShowLocationDropdown(true);
              }}
              placeholder={t.fieldPlacePlaceholder}
              className={`w-full h-11 pl-9 pr-9 rounded-lg border bg-[#FFFDF9] text-sm text-[#0F172A] placeholder:text-[#94A3B8] focus:ring-1 ${
                errors.location
                  ? "border-rose-500 focus:border-rose-500 focus:ring-rose-500"
                  : "border-[#D8BD80]/80 focus:border-[#B8860B] focus:ring-[#B8860B]"
              }`}
            />
            <Search className="w-4 h-4 text-[#94A3B8] absolute left-3 top-3.5" />
            {isSearchingLocation && (
              <Loader2 className="w-4 h-4 text-[#B8860B] animate-spin absolute right-3 top-3.5" />
            )}
          </div>
          {errors.location && <p className="mt-1 text-xs text-rose-600">{errors.location}</p>}

          {showLocationDropdown && locationResults.length > 0 && (
            <div className="absolute z-30 w-full mt-1 bg-white border border-[#D8BD80] rounded-lg shadow-lg max-h-56 overflow-y-auto divide-y divide-[#F1EBE4]">
              {locationResults.map((loc, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSelectLocation(loc)}
                  className="w-full text-left px-3.5 py-2.5 text-xs hover:bg-[#FAF6EC] flex items-center justify-between cursor-pointer"
                >
                  <div className="truncate pr-2">
                    <span className="font-semibold text-[#0F172A]">{loc.shortName}</span>
                    <span className="text-[#64748B] ml-1.5">{loc.displayName}</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* 5. Gender & Marital Status */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label htmlFor="gender" className="block text-xs font-semibold text-[#334155] mb-1">
              {language === "ta" ? "பாலினம்" : "Gender"}
            </label>
            <select
              id="gender"
              name="gender_clean"
              autoComplete="off"
              value={gender}
              onChange={(e) => setGender(e.target.value as "male" | "female")}
              className="w-full h-11 px-3 rounded-lg border border-[#D8BD80]/80 bg-[#FFFDF9] text-sm text-[#0F172A] focus:border-[#B8860B] focus:ring-1 focus:ring-[#B8860B]"
            >
              <option value="male">{language === "ta" ? "ஆண்" : "Male"}</option>
              <option value="female">{language === "ta" ? "பெண்" : "Female"}</option>
            </select>
          </div>

          <div>
            <label htmlFor="maritalStatus" className="block text-xs font-semibold text-[#334155] mb-1">
              {language === "ta" ? "திருமண நிலை" : "Marital Status"}
            </label>
            <select
              id="maritalStatus"
              name="marital_status_clean"
              autoComplete="off"
              value={maritalStatus}
              onChange={(e) => setMaritalStatus(e.target.value)}
              className="w-full h-11 px-3 rounded-lg border border-[#D8BD80]/80 bg-[#FFFDF9] text-sm text-[#0F172A] focus:border-[#B8860B] focus:ring-1 focus:ring-[#B8860B]"
            >
              <option value="unmarried">{language === "ta" ? "திருமணமாகாதவர்" : "Unmarried"}</option>
              <option value="married">{language === "ta" ? "திருமணமானவர்" : "Married"}</option>
              <option value="divorced">{language === "ta" ? "விவாகரத்தானவர்" : "Divorced"}</option>
              <option value="widowed">{language === "ta" ? "விதவை / விதவர்" : "Widowed"}</option>
            </select>
          </div>
        </div>

        {/* 6. Ayanamsa System */}
        <div>
          <label htmlFor="ayanamsa" className="block text-xs font-semibold text-[#334155] mb-1">
            {language === "ta" ? "அயனாம்ச முறை" : "Ayanamsa System"}
          </label>
          <select
            id="ayanamsa"
            name="ayanamsa_clean"
            autoComplete="off"
            value={selectedAyanamsa}
            onChange={(e) => setSelectedAyanamsa(parseInt(e.target.value, 10))}
            className="w-full h-11 px-3 rounded-lg border border-[#D8BD80]/80 bg-[#FFFDF9] text-sm text-[#0F172A] focus:border-[#B8860B] focus:ring-1 focus:ring-[#B8860B]"
          >
            {ayanamsas.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name} — {a.description}
              </option>
            ))}
          </select>
        </div>

        {/* Submit Button */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full h-11 px-6 rounded-lg text-sm font-bold text-white bg-[#102A4C] hover:bg-[#1E3A61] shadow-sm transition-all flex items-center justify-center gap-2 disabled:opacity-75 disabled:cursor-not-allowed cursor-pointer"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-[#D8BD80]" />
                <span>{t.calculating}</span>
              </>
            ) : (
              <>
                <Compass className="w-4 h-4 text-[#D8BD80]" />
                <span>{language === "ta" ? "ஜாதகம் கணக்கிடுக" : t.submitButton}</span>
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
