"use client";

import React, { useState } from "react";
import { TransitTimelineRequest } from "@/lib/types";
import {
  Calendar,
  Clock,
  Globe,
  Sliders,
  Sparkles,
  Check,
} from "lucide-react";

export const IANA_TIMEZONES = [
  { label: "India Standard Time (IST, +05:30)", value: "Asia/Kolkata" },
  { label: "Coordinated Universal Time (UTC, +00:00)", value: "UTC" },
  { label: "US Eastern Time (New York, EDT/EST)", value: "America/New_York" },
  { label: "US Pacific Time (Los Angeles, PDT/PST)", value: "America/Los_Angeles" },
  { label: "US Central Time (Chicago, CDT/CST)", value: "America/Chicago" },
  { label: "UK / Greenwich (London, BST/GMT)", value: "Europe/London" },
  { label: "Gulf Standard Time (Dubai, +04:00)", value: "Asia/Dubai" },
  { label: "Singapore / Malaysia (SGT, +08:00)", value: "Asia/Singapore" },
  { label: "Japan Standard Time (Tokyo, JST, +09:00)", value: "Asia/Tokyo" },
  { label: "Australian Eastern (Sydney, AEST/AEDT)", value: "Australia/Sydney" },
];

export const ALL_SUPPORTED_PLANETS = [
  { id: "Moon", label: "Moon (சந்திரன்)", color: "text-slate-700 bg-slate-100 border-slate-300" },
  { id: "Sun", label: "Sun (சூரியன்)", color: "text-amber-800 bg-amber-50 border-amber-300" },
  { id: "Jupiter", label: "Jupiter (குரு)", color: "text-yellow-800 bg-yellow-50 border-yellow-300" },
  { id: "Saturn", label: "Saturn (சனி)", color: "text-blue-900 bg-blue-50 border-blue-300" },
  { id: "Rahu", label: "Rahu (ராகு)", color: "text-indigo-900 bg-indigo-50 border-indigo-300" },
  { id: "Ketu", label: "Ketu (கேது)", color: "text-purple-900 bg-purple-50 border-purple-300" },
  { id: "Mars", label: "Mars (செவ்வாய்)", color: "text-rose-800 bg-rose-50 border-rose-300" },
  { id: "Mercury", label: "Mercury (புதன்)", color: "text-emerald-800 bg-emerald-50 border-emerald-300" },
  { id: "Venus", label: "Venus (சுக்கிரன்)", color: "text-pink-800 bg-pink-50 border-pink-300" },
];

export const DEFAULT_PLANET_SELECTION = ["Moon", "Sun", "Jupiter", "Saturn", "Rahu", "Ketu"];

interface TransitWatchControlsProps {
  initialValues: TransitTimelineRequest;
  onCalculate: (req: TransitTimelineRequest) => void;
  isLoading: boolean;
  language?: "en" | "ta";
}

export function TransitWatchControls({
  initialValues,
  onCalculate,
  isLoading,
  language = "en",
}: TransitWatchControlsProps) {
  const [startDate, setStartDate] = useState<string>(initialValues.start_date);
  const [startTime, setStartTime] = useState<string>(initialValues.start_time || "00:00:00");
  const [forecastDays, setForecastDays] = useState<number>(initialValues.forecast_days || 7);
  const [timezone, setTimezone] = useState<string>(initialValues.timezone);
  const [customTimezone, setCustomTimezone] = useState<string>("");
  const [isCustomTz, setIsCustomTz] = useState<boolean>(
    !IANA_TIMEZONES.some((tz) => tz.value === initialValues.timezone)
  );
  const [selectedPlanets, setSelectedPlanets] = useState<string[]>(
    initialValues.planets && initialValues.planets.length > 0
      ? initialValues.planets
      : DEFAULT_PLANET_SELECTION
  );
  const [ayanamsa, setAyanamsa] = useState<number>(initialValues.ayanamsa ?? 0);
  const [validationError, setValidationError] = useState<string | null>(null);

  const togglePlanet = (planetId: string) => {
    if (selectedPlanets.includes(planetId)) {
      if (selectedPlanets.length === 1) {
        setValidationError(
          language === "ta"
            ? "குறைந்தது ஒரு கிரகம் தேர்ந்தெடுக்கப்பட வேண்டும்."
            : "At least one planet must be selected."
        );
        return;
      }
      setValidationError(null);
      setSelectedPlanets(selectedPlanets.filter((p) => p !== planetId));
    } else {
      setValidationError(null);
      setSelectedPlanets([...selectedPlanets, planetId]);
    }
  };

  const handlePresetPlanets = (preset: "default" | "inner" | "all") => {
    setValidationError(null);
    if (preset === "default") {
      setSelectedPlanets(DEFAULT_PLANET_SELECTION);
    } else if (preset === "inner") {
      setSelectedPlanets(["Moon", "Sun", "Mercury", "Venus", "Mars"]);
    } else {
      setSelectedPlanets(ALL_SUPPORTED_PLANETS.map((p) => p.id));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    // Validation
    if (!startDate) {
      setValidationError(language === "ta" ? "துவக்க தேதியை உள்ளிடவும்." : "Please select a start date.");
      return;
    }

    if (forecastDays < 7 || forecastDays > 30) {
      setValidationError(
        language === "ta"
          ? "கால அளவு 7 முதல் 30 நாட்களுக்குள் இருக்க வேண்டும்."
          : "Forecast duration must be between 7 and 30 days."
      );
      return;
    }

    const finalTz = isCustomTz ? customTimezone.trim() : timezone;
    if (!finalTz) {
      setValidationError(language === "ta" ? "நேர மண்டலத்தை உள்ளிடவும்." : "Timezone identifier cannot be empty.");
      return;
    }

    if (selectedPlanets.length === 0) {
      setValidationError(
        language === "ta"
          ? "குறைந்தது ஒரு கிரகம் தேர்ந்தெடுக்கப்பட வேண்டும்."
          : "Please select at least one planet."
      );
      return;
    }

    onCalculate({
      start_date: startDate,
      start_time: startTime || "00:00:00",
      forecast_days: forecastDays,
      timezone: finalTz,
      planets: selectedPlanets,
      ayanamsa,
      max_events: 500,
    });
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-2xl border border-[#DDE5F0] bg-white p-5 sm:p-6 shadow-xs space-y-6"
    >
      <div className="flex items-center justify-between pb-3 border-b border-[#F1F5F9]">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-[#B8862B]" />
          <h2 className="font-serif text-base font-bold text-[#102A4C]">
            {language === "ta" ? "கோசார அமைப்புகள்" : "Transit Forecast Parameters"}
          </h2>
        </div>
        <span className="text-[11px] font-semibold text-[#8C6D23] bg-[#FAF2DE] border border-[#D8BD80] px-2.5 py-0.5 rounded-full">
          KP Tier 3 (Sub-Lord)
        </span>
      </div>

      {validationError && (
        <div className="p-3 text-xs rounded-xl bg-rose-50 border border-rose-200 text-rose-800 font-medium">
          {validationError}
        </div>
      )}

      {/* Grid of Inputs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
        {/* 1. Start Date */}
        <div className="space-y-1.5">
          <label className="font-semibold text-[#334155] flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-[#B8862B]" />
            <span>{language === "ta" ? "துவக்க தேதி" : "Start Date"}</span>
          </label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] bg-[#FAF8F5] text-[#102A4C] text-xs focus:ring-2 focus:ring-[#B8862B] focus:outline-hidden"
            required
          />
        </div>

        {/* 2. Start Time */}
        <div className="space-y-1.5">
          <label className="font-semibold text-[#334155] flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-[#B8862B]" />
            <span>{language === "ta" ? "துவக்க நேரம்" : "Start Time (Local)"}</span>
          </label>
          <input
            type="time"
            step="1"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
            className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] bg-[#FAF8F5] text-[#102A4C] text-xs focus:ring-2 focus:ring-[#B8862B] focus:outline-hidden"
          />
        </div>

        {/* 3. Forecast Duration (7-30 days) */}
        <div className="space-y-1.5">
          <label className="font-semibold text-[#334155] flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-[#B8862B]" />
              <span>{language === "ta" ? "கால அளவு" : "Duration"}</span>
            </span>
            <span className="text-[10px] text-[#64748B] font-mono">7–30 days</span>
          </label>
          <div className="flex items-center gap-1.5">
            {[7, 14, 21, 30].map((days) => (
              <button
                key={days}
                type="button"
                onClick={() => setForecastDays(days)}
                className={`flex-1 py-1.5 px-2 rounded-lg text-xs font-semibold border transition-colors ${
                  forecastDays === days
                    ? "bg-[#B8862B] text-white border-[#B8862B]"
                    : "bg-[#FAF8F5] text-[#334155] border-[#DDE5F0] hover:bg-[#F1F5F9]"
                }`}
              >
                {days}d
              </button>
            ))}
          </div>
        </div>

        {/* 4. Ayanamsa */}
        <div className="space-y-1.5">
          <label className="font-semibold text-[#334155] flex items-center gap-1.5">
            <Globe className="w-3.5 h-3.5 text-[#B8862B]" />
            <span>{language === "ta" ? "அயனாம்சம்" : "Ayanamsa"}</span>
          </label>
          <select
            value={ayanamsa}
            onChange={(e) => setAyanamsa(Number(e.target.value))}
            className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] bg-[#FAF8F5] text-[#102A4C] text-xs focus:ring-2 focus:ring-[#B8862B] focus:outline-hidden"
          >
            <option value={0}>Lahiri (Chitra Paksha) — Canonical</option>
            <option value={1}>KP Krishnamurti (Ayanamsa ID 1)</option>
          </select>
        </div>
      </div>

      {/* Timezone Selector Row */}
      <div className="space-y-1.5 text-xs">
        <div className="flex items-center justify-between">
          <label className="font-semibold text-[#334155] flex items-center gap-1.5">
            <Globe className="w-3.5 h-3.5 text-[#3478F6]" />
            <span>{language === "ta" ? "நேர மண்டலம்" : "Local Timezone (IANA)"}</span>
          </label>
          <button
            type="button"
            onClick={() => setIsCustomTz(!isCustomTz)}
            className="text-[11px] text-[#3478F6] hover:underline font-medium"
          >
            {isCustomTz
              ? language === "ta"
                ? "நிலையான பட்டியலைத் தேர்ந்தெடு"
                : "Choose from standard list"
              : language === "ta"
              ? "தனிப்பயன் மண்டலம் உள்ளிடுக"
              : "Enter custom IANA timezone"}
          </button>
        </div>

        {isCustomTz ? (
          <input
            type="text"
            placeholder="e.g. Europe/Paris or +05:30"
            value={customTimezone}
            onChange={(e) => setCustomTimezone(e.target.value)}
            className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] bg-[#FAF8F5] text-[#102A4C] text-xs font-mono focus:ring-2 focus:ring-[#B8862B] focus:outline-hidden"
          />
        ) : (
          <select
            value={timezone}
            onChange={(e) => setTimezone(e.target.value)}
            className="w-full px-3 py-2 rounded-xl border border-[#DDE5F0] bg-[#FAF8F5] text-[#102A4C] text-xs focus:ring-2 focus:ring-[#B8862B] focus:outline-hidden"
          >
            {IANA_TIMEZONES.map((tz) => (
              <option key={tz.value} value={tz.value}>
                {tz.label} ({tz.value})
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Planet Selection Multi-Select Chips */}
      <div className="space-y-2 text-xs">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <label className="font-semibold text-[#334155] flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-[#B8862B]" />
            <span>{language === "ta" ? "கணக்கிட வேண்டிய கிரகங்கள்" : "Planets to Analyze"}</span>
            <span className="text-[10px] text-[#64748B]">({selectedPlanets.length}/9 selected)</span>
          </label>
          <div className="flex items-center gap-1 text-[11px]">
            <button
              type="button"
              onClick={() => handlePresetPlanets("default")}
              className="px-2 py-0.5 rounded-md bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80] hover:bg-[#F2E5C2] transition-colors"
            >
              KP Default (6)
            </button>
            <button
              type="button"
              onClick={() => handlePresetPlanets("inner")}
              className="px-2 py-0.5 rounded-md bg-[#F1F5F9] text-[#334155] border border-[#E2E8F0] hover:bg-[#E2E8F0] transition-colors"
            >
              Inner Fast (5)
            </button>
            <button
              type="button"
              onClick={() => handlePresetPlanets("all")}
              className="px-2 py-0.5 rounded-md bg-[#F1F5F9] text-[#334155] border border-[#E2E8F0] hover:bg-[#E2E8F0] transition-colors"
            >
              All 9 Grahas
            </button>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 lg:grid-cols-9 gap-1.5">
          {ALL_SUPPORTED_PLANETS.map((planet) => {
            const isSelected = selectedPlanets.includes(planet.id);
            return (
              <button
                key={planet.id}
                type="button"
                onClick={() => togglePlanet(planet.id)}
                className={`py-1.5 px-2 rounded-xl text-[11px] font-semibold border flex items-center justify-center gap-1 transition-all ${
                  isSelected
                    ? "bg-[#102A4C] text-white border-[#102A4C] shadow-2xs"
                    : "bg-[#FAF8F5] text-[#64748B] border-[#E2E8F0] hover:bg-[#F1F5F9]"
                }`}
              >
                {isSelected && <Check className="w-3 h-3 text-[#E5B558]" />}
                <span>{planet.id}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Submit Button */}
      <div className="pt-2 flex items-center justify-end">
        <button
          type="submit"
          disabled={isLoading}
          className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl font-bold text-xs text-white bg-gradient-to-r from-[#B8862B] to-[#996515] hover:from-[#996515] hover:to-[#80500D] shadow-xs hover:shadow-md transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <>
              <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>{language === "ta" ? "கணக்கிடுகிறது..." : "Computing Ingress Timeline..."}</span>
            </>
          ) : (
            <>
              <Sparkles className="w-3.5 h-3.5" />
              <span>{language === "ta" ? "கோசார கணிப்பை இயக்கு" : "Calculate Ingress Timeline"}</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
}
