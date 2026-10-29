"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { SavedHoroscopeItem } from "@/lib/types";
import { formatSerialNumber } from "@/lib/formatters";
import { COMMON_TIMEZONES } from "@/lib/cities";
import { calculateFullHoroscopeSuite } from "@/lib/api";
import { saveActiveCalculation } from "@/lib/storage";
import { prepareCalculationSnapshot } from "@/lib/horoscope-storage-utils";
import { SUPPORTED_COUNTRY_CODES, validateAndNormalizePhone } from "@/lib/phone-utils";
import {
  X,
  Save,
  RotateCw,
  Compass,
  AlertCircle,
  CheckCircle2,
  Calendar,
  Clock,
  MapPin,
  Globe,
  Sliders,
  Layers,
  Sparkles,
  Phone,
  ExternalLink,
} from "lucide-react";

interface SavedHoroscopeEditModalProps {
  horoscope: SavedHoroscopeItem | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function SavedHoroscopeEditModal({
  horoscope,
  isOpen,
  onClose,
  onSuccess,
}: SavedHoroscopeEditModalProps) {
  const router = useRouter();
  const { language, t } = useLanguage();

  // Form states
  const [personName, setPersonName] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [birthTime, setBirthTime] = useState("");
  const [countryCode, setCountryCode] = useState("+91");
  const [customerPhone, setCustomerPhone] = useState("");
  const [timezone, setTimezone] = useState("Asia/Kolkata");
  const [birthplace, setBirthplace] = useState("");
  const [latitude, setLatitude] = useState<number | "">("");
  const [longitude, setLongitude] = useState<number | "">("");
  const [ayanamsaId, setAyanamsaId] = useState<number>(0);
  const [houseSystemId, setHouseSystemId] = useState<number>(2);

  // Status states
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    if (horoscope) {
      setPersonName(horoscope.person_name || "");
      setBirthDate(horoscope.birth_date || "");
      setBirthTime(horoscope.birth_time || "");
      setCountryCode(
        horoscope.customer_country_code || horoscope.country_code || "+91"
      );
      setCustomerPhone(
        horoscope.customer_phone || horoscope.normalized_phone || horoscope.whatsapp_number || ""
      );
      setTimezone(horoscope.timezone || "Asia/Kolkata");
      setBirthplace(horoscope.birthplace || "");
      setLatitude(typeof horoscope.latitude === "number" ? horoscope.latitude : "");
      setLongitude(typeof horoscope.longitude === "number" ? horoscope.longitude : "");
      setAyanamsaId(typeof horoscope.ayanamsa_id === "number" ? horoscope.ayanamsa_id : 0);
      setHouseSystemId(
        typeof horoscope.house_system_id === "number" ? horoscope.house_system_id : 2
      );
      setErrors({});
      setErrorMessage(null);
      setSuccessMessage(null);
    }
  }, [horoscope]);

  if (!isOpen || !horoscope) return null;

  const serialText = formatSerialNumber(horoscope.display_number);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!personName.trim()) {
      newErrors.personName = language === "ta" ? "பெயர் தேவை" : "Birth name is required";
    }

    if (!birthDate) {
      newErrors.birthDate = t.valDateRequired;
    }

    if (!birthTime.trim()) {
      newErrors.birthTime = t.valTimeRequired;
    }

    if (customerPhone.trim()) {
      const pVal = validateAndNormalizePhone(customerPhone, countryCode);
      if (!pVal.isValid) {
        newErrors.customerPhone = pVal.error || "Invalid WhatsApp phone number.";
      }
    }

    if (
      latitude === "" ||
      isNaN(Number(latitude)) ||
      Number(latitude) < -90 ||
      Number(latitude) > 90
    ) {
      newErrors.latitude = t.valLatInvalid;
    }

    if (
      longitude === "" ||
      isNaN(Number(longitude)) ||
      Number(longitude) < -180 ||
      Number(longitude) > 180
    ) {
      newErrors.longitude = t.valLonInvalid;
    }

    if (!timezone.trim()) {
      newErrors.timezone = t.valTzRequired;
    }

    if (!birthplace.trim()) {
      newErrors.birthplace = t.valPlaceRequired;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Save Changes to Existing Record: recalculates and updates in-place without duplicating
  const handleSaveChanges = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setSuccessMessage(null);

    if (!validate()) return;

    setIsSaving(true);
    try {
      const formattedTime =
        birthTime.includes(":") && birthTime.split(":").length === 2
          ? `${birthTime}:00`
          : birthTime;

      // 1. Recalculate astronomical positions with the edited birth details
      const calcResult = await calculateFullHoroscopeSuite({
        fullName: personName.trim(),
        birthDate,
        birthTime: formattedTime,
        isTimeConfirmed: true,
        locationName: birthplace.trim(),
        latitude: Number(latitude),
        longitude: Number(longitude),
        timezone: timezone.trim(),
        ayanamsaId,
        houseSystemId,
        includePanchang: true,
        includeOuterPlanets: true,
      });

      // 2. Prepare snapshot and update existing horoscope record in-place via PUT
      const idempotencyKey =
        (horoscope as any).calculation_result?.idempotency_key ||
        `calc_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
      const compactedSnapshot = prepareCalculationSnapshot(calcResult, idempotencyKey);

      const res = await fetch(`/api/horoscopes/${horoscope.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          person_name: personName.trim(),
          customer_full_name: personName.trim(),
          birth_date: birthDate,
          birth_time: formattedTime,
          timezone: timezone.trim(),
          birthplace: birthplace.trim(),
          latitude: Number(latitude),
          longitude: Number(longitude),
          ayanamsa_id: ayanamsaId,
          house_system_id: houseSystemId,
          customer_phone: customerPhone.trim() || undefined,
          country_code: countryCode,
          customer_id: horoscope.customer_id || undefined,
          calculation_result: compactedSnapshot,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Failed to update horoscope record.");
      }

      // Update client-side active calculation session cache
      saveActiveCalculation({
        ...calcResult,
        savedId: horoscope.id,
        displayNumber: horoscope.display_number,
        isSaved: true,
      });

      setSuccessMessage(
        language === "ta"
          ? "ஜாதக விவரங்கள் மற்றும் கணிப்புகள் வெற்றிகரமாக மாற்றியமைக்கப்பட்டன."
          : "Horoscope details and calculations updated successfully."
      );
      onSuccess();
      setTimeout(() => {
        onClose();
      }, 700);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to save horoscope changes.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs overflow-y-auto">
      <div className="relative w-full max-w-2xl bg-white rounded-2xl border border-[#E2DCD5] shadow-2xl p-6 sm:p-8 my-8 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-[#E2DCD5]">
          <div className="flex items-center gap-3">
            <div className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-mono font-bold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
              <span>{serialText}</span>
            </div>
            <div>
              <h2 className="font-serif text-lg sm:text-xl font-bold text-[#0F172A]">
                {t.editHoroscopeTitle}
              </h2>
              <p className="text-xs text-[#64748B]">
                {t.editHoroscopeSubtitle}
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-[#64748B] hover:text-[#0F172A] hover:bg-[#FAF8F5] transition-colors"
            aria-label="Close dialog"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Notices */}
        {errorMessage && (
          <div className="mt-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {successMessage && (
          <div className="mt-4 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{successMessage}</span>
          </div>
        )}

        {/* Form Body */}
        <form onSubmit={handleSaveChanges} className="mt-6 space-y-4">
          {/* Birth Name */}
          <div>
            <label className="block text-xs font-semibold text-[#334155] mb-1.5">
              {t.fieldName} *
            </label>
            <input
              type="text"
              value={personName}
              onChange={(e) => setPersonName(e.target.value)}
              placeholder={t.fieldNamePlaceholder}
              className={`w-full px-3.5 py-2.5 rounded-xl border text-xs sm:text-sm bg-white focus:outline-hidden focus:ring-2 focus:ring-[#B8860B]/20 transition-all ${
                errors.personName
                  ? "border-rose-400 bg-rose-50/20"
                  : "border-[#CBD5E1] focus:border-[#B8860B]"
              }`}
            />
            {errors.personName && (
              <p className="mt-1 text-[11px] text-rose-600">{errors.personName}</p>
            )}
          </div>

          {/* Customer WhatsApp Phone */}
          <div>
            <label className="block text-xs font-semibold text-[#334155] mb-1.5 flex items-center gap-1.5">
              <Phone className="w-3.5 h-3.5 text-emerald-600" />
              <span>{language === "ta" ? "வாட்ஸ்அப் தொடர்பு எண்" : "Customer WhatsApp Number"}</span>
            </label>
            <div className="flex gap-2">
              <select
                value={countryCode}
                onChange={(e) => {
                  setCountryCode(e.target.value);
                  setErrors((prev) => ({ ...prev, customerPhone: "" }));
                }}
                className="w-28 sm:w-32 px-2.5 py-2.5 rounded-xl border border-[#CBD5E1] bg-white text-xs font-medium text-[#0F172A] focus:border-[#B8860B] focus:ring-2 focus:ring-[#B8860B]/20"
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
                onChange={(e) => {
                  setCustomerPhone(e.target.value);
                  setErrors((prev) => ({ ...prev, customerPhone: "" }));
                }}
                placeholder={countryCode === "+91" ? "98765 43210" : "Phone number"}
                className={`flex-1 px-3.5 py-2.5 rounded-xl border text-xs sm:text-sm bg-white focus:outline-hidden focus:ring-2 focus:ring-[#B8860B]/20 transition-all ${
                  errors.customerPhone
                    ? "border-rose-400 bg-rose-50/20"
                    : "border-[#CBD5E1] focus:border-[#B8860B]"
                }`}
              />
            </div>
            {errors.customerPhone ? (
              <p className="mt-1 text-[11px] text-rose-600">{errors.customerPhone}</p>
            ) : (
              <p className="mt-1 text-[11px] text-[#64748B]">
                {language === "ta"
                  ? "பிறந்தநாள் வாழ்த்துக்கள் & வாட்ஸ்அப் தொடர்புக்கு அவசியமானது."
                  : "Required for birthday reminders and direct WhatsApp contact."}
              </p>
            )}
          </div>

          {/* Date and Time */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-[#334155] mb-1.5 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-[#B8860B]" />
                <span>{t.fieldDate} *</span>
              </label>
              <input
                type="date"
                value={birthDate}
                onChange={(e) => setBirthDate(e.target.value)}
                className={`w-full px-3.5 py-2.5 rounded-xl border text-xs sm:text-sm bg-white focus:outline-hidden focus:ring-2 focus:ring-[#B8860B]/20 transition-all ${
                  errors.birthDate
                    ? "border-rose-400 bg-rose-50/20"
                    : "border-[#CBD5E1] focus:border-[#B8860B]"
                }`}
              />
              {errors.birthDate && (
                <p className="mt-1 text-[11px] text-rose-600">{errors.birthDate}</p>
              )}
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#334155] mb-1.5 flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-[#B8860B]" />
                <span>{language === "ta" ? "பிறந்த நேரம் (24h)" : "Birth Time (24h)"} (HH:MM:SS) *</span>
              </label>
              <input
                type="text"
                value={birthTime}
                onChange={(e) => setBirthTime(e.target.value)}
                placeholder="10:30:00"
                className={`w-full px-3.5 py-2.5 rounded-xl border text-xs sm:text-sm font-mono bg-white focus:outline-hidden focus:ring-2 focus:ring-[#B8860B]/20 transition-all ${
                  errors.birthTime
                    ? "border-rose-400 bg-rose-50/20"
                    : "border-[#CBD5E1] focus:border-[#B8860B]"
                }`}
              />
              {errors.birthTime && (
                <p className="mt-1 text-[11px] text-rose-600">{errors.birthTime}</p>
              )}
            </div>
          </div>

          {/* Timezone and Birthplace */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-[#334155] mb-1.5 flex items-center gap-1.5">
                <Globe className="w-3.5 h-3.5 text-[#B8860B]" />
                <span>{t.fieldTimezone} *</span>
              </label>
              <select
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-[#CBD5E1] text-xs sm:text-sm bg-white focus:outline-hidden focus:border-[#B8860B] focus:ring-2 focus:ring-[#B8860B]/20"
              >
                {COMMON_TIMEZONES.map((tz) => (
                  <option key={tz.value} value={tz.value}>
                    {tz.label} ({tz.offset})
                  </option>
                ))}
                {!COMMON_TIMEZONES.some((tz) => tz.value === timezone) && (
                  <option value={timezone}>{timezone}</option>
                )}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#334155] mb-1.5 flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-[#B8860B]" />
                <span>{t.fieldPlace} *</span>
              </label>
              <input
                type="text"
                value={birthplace}
                onChange={(e) => setBirthplace(e.target.value)}
                placeholder={t.fieldPlacePlaceholder}
                className={`w-full px-3.5 py-2.5 rounded-xl border text-xs sm:text-sm bg-white focus:outline-hidden focus:ring-2 focus:ring-[#B8860B]/20 transition-all ${
                  errors.birthplace
                    ? "border-rose-400 bg-rose-50/20"
                    : "border-[#CBD5E1] focus:border-[#B8860B]"
                }`}
              />
              {errors.birthplace && (
                <p className="mt-1 text-[11px] text-rose-600">{errors.birthplace}</p>
              )}
            </div>
          </div>

          {/* Latitude and Longitude */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-[#334155] mb-1.5">
                {t.fieldLatitude} (-90 to +90) *
              </label>
              <input
                type="number"
                step="0.0001"
                value={latitude}
                onChange={(e) => setLatitude(e.target.value === "" ? "" : Number(e.target.value))}
                placeholder="13.0827"
                className={`w-full px-3.5 py-2.5 rounded-xl border text-xs sm:text-sm font-mono bg-white focus:outline-hidden focus:ring-2 focus:ring-[#B8860B]/20 transition-all ${
                  errors.latitude
                    ? "border-rose-400 bg-rose-50/20"
                    : "border-[#CBD5E1] focus:border-[#B8860B]"
                }`}
              />
              {errors.latitude && (
                <p className="mt-1 text-[11px] text-rose-600">{errors.latitude}</p>
              )}
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#334155] mb-1.5">
                {t.fieldLongitude} (-180 to +180) *
              </label>
              <input
                type="number"
                step="0.0001"
                value={longitude}
                onChange={(e) => setLongitude(e.target.value === "" ? "" : Number(e.target.value))}
                placeholder="80.2707"
                className={`w-full px-3.5 py-2.5 rounded-xl border text-xs sm:text-sm font-mono bg-white focus:outline-hidden focus:ring-2 focus:ring-[#B8860B]/20 transition-all ${
                  errors.longitude
                    ? "border-rose-400 bg-rose-50/20"
                    : "border-[#CBD5E1] focus:border-[#B8860B]"
                }`}
              />
              {errors.longitude && (
                <p className="mt-1 text-[11px] text-rose-600">{errors.longitude}</p>
              )}
            </div>
          </div>

          {/* Ayanamsa and House System */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-[#334155] mb-1.5 flex items-center gap-1.5">
                <Sliders className="w-3.5 h-3.5 text-[#B8860B]" />
                <span>{t.fieldAyanamsa}</span>
              </label>
              <select
                value={ayanamsaId}
                onChange={(e) => setAyanamsaId(Number(e.target.value))}
                className="w-full px-3.5 py-2.5 rounded-xl border border-[#CBD5E1] text-xs sm:text-sm bg-white focus:outline-hidden focus:border-[#B8860B]"
              >
                <option value={0}>Lahiri (Chitrapaksha Standard Vedic)</option>
                <option value={1}>KP (Krishnamurti Paddhati)</option>
                <option value={2}>Raman (Dr. B.V. Raman)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#334155] mb-1.5 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-[#B8860B]" />
                <span>{t.fieldHouseSystem}</span>
              </label>
              <select
                value={houseSystemId}
                onChange={(e) => setHouseSystemId(Number(e.target.value))}
                className="w-full px-3.5 py-2.5 rounded-xl border border-[#CBD5E1] text-xs sm:text-sm bg-white focus:outline-hidden focus:border-[#B8860B]"
              >
                <option value={2}>Placidus (Standard KP)</option>
                <option value={0}>Whole Sign (Rashi-Bhava)</option>
                <option value={1}>Equal House</option>
              </select>
            </div>
          </div>

          {/* Explanatory In-Place Replacement Notice */}
          <div className="p-3.5 rounded-xl bg-amber-50/80 border border-amber-200 text-xs text-amber-900 space-y-1">
            <div className="font-semibold flex items-center gap-1.5">
              <Compass className="w-3.5 h-3.5 text-amber-700" />
              <span>
                {language === "ta"
                  ? "தரவு புதுப்பித்தல் (In-Place Update)"
                  : "In-Place Data Replacement"}
              </span>
            </div>
            <p className="leading-relaxed text-amber-800">
              {language === "ta"
                ? `சேமிக்கும்போது இம்மாற்றங்கள் இந்த ஜாதகத்தின் (${serialText}) முந்தைய தரவை நேரடியாக மாற்றியமைக்கும். புதிய இரட்டை ஜாதகம் (Duplicate) உருவாகாது.`
                : `Saving will replace the calculation and birth data for Horoscope ${serialText} in-place without creating a duplicate record.`}
            </p>
          </div>

          {/* Action Buttons */}
          <div className="pt-4 border-t border-[#E2DCD5] flex flex-col sm:flex-row items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              disabled={isSaving}
              className="w-full sm:w-auto px-4 py-2.5 rounded-xl border border-[#CBD5E1] bg-white hover:bg-[#FAF8F5] text-xs font-semibold text-[#475569] transition-colors cursor-pointer"
            >
              {t.back}
            </button>

            <button
              type="button"
              onClick={() => {
                onClose();
                router.push(`/horoscope?edit_id=${horoscope.id}`);
              }}
              disabled={isSaving}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl border border-[#D9DEE7] bg-white hover:bg-[#F2F3F5] text-xs font-semibold text-[#153F6B] transition-colors cursor-pointer"
              title="Open full interactive form to edit this horoscope"
            >
              <ExternalLink className="w-3.5 h-3.5 text-[#153F6B]" />
              <span>
                {language === "ta" ? "முழு படிவத்தில் திருத்துக" : "Open in Full Form"}
              </span>
            </button>

            <button
              type="submit"
              disabled={isSaving}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-1.5 px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-[#0F172A] hover:bg-[#1E293B] shadow-xs transition-colors cursor-pointer disabled:opacity-50"
            >
              <Save className="w-3.5 h-3.5 text-[#D8BD80]" />
              <span>
                {isSaving
                  ? (language === "ta" ? "கணக்கிட்டுச் சேமிக்கப்படுகிறது..." : "Saving & Recalculating...")
                  : (language === "ta" ? "மாற்றங்களைச் சேமி (Replace Data)" : "Save & Replace Data")}
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
