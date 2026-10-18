"use client";

import React, { useState, useEffect } from "react";
import { useLanguage } from "@/lib/i18n";
import {
  Compass,
  Sliders,
  CheckCircle2,
  MapPin,
  Save,
  RotateCcw,
  Sparkles,
  Info,
  ShieldCheck,
  Cpu,
} from "lucide-react";

export function CalculationSettingsView() {
  const { language } = useLanguage();

  // Settings state persisted in localStorage
  const [ayanamsaId, setAyanamsaId] = useState<number>(0);
  const [tradition, setTradition] = useState<string>("south_indian");
  const [defaultCity, setDefaultCity] = useState<string>("Chennai, Tamil Nadu, India");
  const [defaultLat, setDefaultLat] = useState<number>(13.0827);
  const [defaultLon, setDefaultLon] = useState<number>(80.2707);
  const [defaultTz, setDefaultTz] = useState<string>("Asia/Kolkata");

  // Rule strictness toggles
  const [strictAshtama, setStrictAshtama] = useState<boolean>(true);
  const [rejectSandhi, setRejectSandhi] = useState<boolean>(true);
  const [strictTaraBala, setStrictTaraBala] = useState<boolean>(true);
  const [minSlotDuration, setMinSlotDuration] = useState<number>(45);

  const [savedSuccess, setSavedSuccess] = useState<boolean>(false);

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem("gai_muhurta_settings");
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed.ayanamsaId !== undefined) setAyanamsaId(parsed.ayanamsaId);
        if (parsed.tradition) setTradition(parsed.tradition);
        if (parsed.defaultCity) setDefaultCity(parsed.defaultCity);
        if (parsed.defaultLat !== undefined) setDefaultLat(parsed.defaultLat);
        if (parsed.defaultLon !== undefined) setDefaultLon(parsed.defaultLon);
        if (parsed.defaultTz) setDefaultTz(parsed.defaultTz);
        if (parsed.strictAshtama !== undefined) setStrictAshtama(parsed.strictAshtama);
        if (parsed.rejectSandhi !== undefined) setRejectSandhi(parsed.rejectSandhi);
        if (parsed.strictTaraBala !== undefined) setStrictTaraBala(parsed.strictTaraBala);
        if (parsed.minSlotDuration !== undefined) setMinSlotDuration(parsed.minSlotDuration);
      }
    } catch (e) {
      console.error("Failed to load settings from storage:", e);
    }
  }, []);

  const handleSave = () => {
    try {
      const settings = {
        ayanamsaId,
        tradition,
        defaultCity,
        defaultLat,
        defaultLon,
        defaultTz,
        strictAshtama,
        rejectSandhi,
        strictTaraBala,
        minSlotDuration,
      };
      localStorage.setItem("gai_muhurta_settings", JSON.stringify(settings));
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (e) {
      console.error("Failed to save settings:", e);
    }
  };

  const handleResetDefaults = () => {
    setAyanamsaId(0);
    setTradition("south_indian");
    setDefaultCity("Chennai, Tamil Nadu, India");
    setDefaultLat(13.0827);
    setDefaultLon(80.2707);
    setDefaultTz("Asia/Kolkata");
    setStrictAshtama(true);
    setRejectSandhi(true);
    setStrictTaraBala(true);
    setMinSlotDuration(45);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-white rounded-3xl p-6 sm:p-7 border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-purple-100 text-purple-800">
              <Sliders className="w-5 h-5" />
            </span>
            <h3 className="text-xl font-extrabold text-slate-900">
              {language === "ta" ? "கணித அமைப்புகள் & விதிமுறைகள்" : "Calculation Settings & Ephemeris"}
            </h3>
          </div>
          <p className="text-xs text-slate-500 mt-1 max-w-xl">
            {language === "ta"
              ? "சுவிஸ் எபிமெரிஸ் கணித முறை, அயனாம்சம், இயல்புநிலை இருப்பிடம் மற்றும் முகூர்த்த விதிகளின் கண்டிப்பு நிலைகளை மாற்றியமைக்கலாம்."
              : "Configure default Ayanamsa convention, location coordinates, regional rule profiles, and traditional strictness thresholds."}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleResetDefaults}
            className="px-3.5 py-2 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-600 text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
          <button
            type="button"
            onClick={handleSave}
            className="px-5 py-2 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold shadow-md flex items-center gap-1.5 transition-colors"
          >
            <Save className="w-3.5 h-3.5" />
            <span>{savedSuccess ? "Saved!" : "Save Settings"}</span>
          </button>
        </div>
      </div>

      {savedSuccess && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2 font-medium">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>
            {language === "ta"
              ? "கணித அமைப்புகள் வெற்றிகரமாகச் சேமிக்கப்பட்டன."
              : "Calculation settings saved successfully and will be applied to all future queries."}
          </span>
        </div>
      )}

      {/* Grid: 2 columns */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left Column: Astronomical & Tradition */}
        <div className="space-y-6">
          {/* Card: Engine Provenance */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
            <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-amber-600" />
              <span>{language === "ta" ? "கணித எந்திர விவரங்கள்" : "Ephemeris Engine Provenance"}</span>
            </h4>

            <div className="space-y-2.5 text-xs">
              <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100 flex items-center justify-between">
                <div>
                  <div className="font-bold text-slate-800">Astronomical Engine</div>
                  <div className="text-[11px] text-slate-500">Swiss Ephemeris 2.10 (Meeus Algorithms)</div>
                </div>
                <span className="px-2 py-0.5 rounded-full text-[10px] bg-emerald-100 text-emerald-800 font-bold">
                  Active
                </span>
              </div>

              <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100 flex items-center justify-between">
                <div>
                  <div className="font-bold text-slate-800">Solar Elevation & Zenith</div>
                  <div className="text-[11px] text-slate-500">NOAA standard (90°50' atmospheric refraction)</div>
                </div>
                <span className="px-2 py-0.5 rounded-full text-[10px] bg-blue-100 text-blue-800 font-bold">
                  Sub-second
                </span>
              </div>

              <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100 flex items-center justify-between">
                <div>
                  <div className="font-bold text-slate-800">Tithi/Nakshatra Transition Precision</div>
                  <div className="text-[11px] text-slate-500">24-step binary search root-finding (&lt;0.5ms)</div>
                </div>
                <span className="px-2 py-0.5 rounded-full text-[10px] bg-purple-100 text-purple-800 font-bold">
                  Exact
                </span>
              </div>
            </div>
          </div>

          {/* Card: Ayanamsa & Regional Profile */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
            <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Compass className="w-4 h-4 text-amber-600" />
              <span>{language === "ta" ? "அயனாம்சம் & பாரம்பரியம்" : "Ayanamsa & Regional Profile"}</span>
            </h4>

            <div className="space-y-4 text-xs">
              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  Ayanamsa Convention
                </label>
                <select
                  value={ayanamsaId}
                  onChange={(e) => setAyanamsaId(Number(e.target.value))}
                  className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-800"
                >
                  <option value={0}>Lahiri / Chitra Paksha (Government of India Standard)</option>
                  <option value={1}>Krishnamurti Paddhati (KP System)</option>
                  <option value={2}>B.V. Raman Ayanamsa</option>
                  <option value={3}>Tropical / Sayana (Western)</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  Regional Tradition Profile
                </label>
                <select
                  value={tradition}
                  onChange={(e) => setTradition(e.target.value)}
                  className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-800"
                >
                  <option value="south_indian">South Indian / Tamil Panchangam (Drik & Vakya)</option>
                  <option value="north_indian">North Indian Classical Muhurta</option>
                  <option value="kp_astrology">KP Astrological Sub-Lord Muhurta</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Default Location & Traditional Strictness */}
        <div className="space-y-6">
          {/* Card: Default Event Location */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
            <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <MapPin className="w-4 h-4 text-amber-600" />
              <span>{language === "ta" ? "இயல்புநிலை இடம்" : "Default Geographic Coordinates"}</span>
            </h4>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  Default City Name
                </label>
                <input
                  type="text"
                  value={defaultCity}
                  onChange={(e) => setDefaultCity(e.target.value)}
                  className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-800"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                    Latitude (°N)
                  </label>
                  <input
                    type="number"
                    step="0.0001"
                    value={defaultLat}
                    onChange={(e) => setDefaultLat(Number(e.target.value))}
                    className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-800 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                    Longitude (°E)
                  </label>
                  <input
                    type="number"
                    step="0.0001"
                    value={defaultLon}
                    onChange={(e) => setDefaultLon(Number(e.target.value))}
                    className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-800 font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  Default IANA Timezone Identifier
                </label>
                <input
                  type="text"
                  value={defaultTz}
                  onChange={(e) => setDefaultTz(e.target.value)}
                  className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-800 font-mono"
                />
              </div>
            </div>
          </div>

          {/* Card: Traditional Rule Strictness */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
            <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>{language === "ta" ? "விதிகளின் கண்டிப்பு நிலை" : "Traditional Rule Strictness"}</span>
            </h4>

            <div className="space-y-3 text-xs">
              <label className="flex items-center gap-2.5 p-2.5 rounded-xl bg-slate-50 border border-slate-200 hover:bg-slate-100 cursor-pointer">
                <input
                  type="checkbox"
                  checked={strictAshtama}
                  onChange={(e) => setStrictAshtama(e.target.checked)}
                  className="rounded text-amber-600 focus:ring-amber-500"
                />
                <div>
                  <div className="font-semibold text-slate-800">Strict Ashtama Shuddhi (8th House Purity)</div>
                  <div className="text-[10px] text-slate-500">Rejects any candidate window where 8th house contains any planet.</div>
                </div>
              </label>

              <label className="flex items-center gap-2.5 p-2.5 rounded-xl bg-slate-50 border border-slate-200 hover:bg-slate-100 cursor-pointer">
                <input
                  type="checkbox"
                  checked={rejectSandhi}
                  onChange={(e) => setRejectSandhi(e.target.checked)}
                  className="rounded text-amber-600 focus:ring-amber-500"
                />
                <div>
                  <div className="font-semibold text-slate-800">Reject Sandhi Periods</div>
                  <div className="text-[10px] text-slate-500">Flags first and last 2% of nakshatras and lagna transitions as vulnerable.</div>
                </div>
              </label>

              <label className="flex items-center gap-2.5 p-2.5 rounded-xl bg-slate-50 border border-slate-200 hover:bg-slate-100 cursor-pointer">
                <input
                  type="checkbox"
                  checked={strictTaraBala}
                  onChange={(e) => setStrictTaraBala(e.target.checked)}
                  className="rounded text-amber-600 focus:ring-amber-500"
                />
                <div>
                  <div className="font-semibold text-slate-800">Enforce Navatara Exclusions</div>
                  <div className="text-[10px] text-slate-500">Disqualifies slots with Vipat, Pratyak, or Naidhana taras.</div>
                </div>
              </label>

              <div className="pt-2">
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  Default Minimum Slot Duration (Minutes)
                </label>
                <input
                  type="number"
                  min={15}
                  max={240}
                  value={minSlotDuration}
                  onChange={(e) => setMinSlotDuration(Number(e.target.value))}
                  className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-800"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
