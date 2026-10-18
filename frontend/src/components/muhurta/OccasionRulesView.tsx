"use client";

import React, { useState, useEffect } from "react";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { getOccasions, addCustomOccasion, updateOccasion } from "@/lib/api";
import { OccasionItem } from "@/lib/types";
import {
  Sliders,
  Plus,
  ShieldCheck,
  ShieldAlert,
  Sparkles,
  CheckCircle2,
  Lock,
  Edit2,
  Trash2,
  X,
  AlertCircle,
  Layers,
  Heart,
  Home,
  Briefcase,
  Car,
  GraduationCap,
  Sparkle,
} from "lucide-react";

export function OccasionRulesView() {
  const { language } = useLanguage();
  const { session, role } = useAuth();
  const isAdmin = role === "admin";

  const [occasions, setOccasions] = useState<OccasionItem[]>([]);
  const [activeCategory, setActiveCategory] = useState<string>("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Edit / Rule Modal
  const [editingOccasion, setEditingOccasion] = useState<OccasionItem | null>(null);
  const [editRules, setEditRules] = useState<Record<string, any>>({});
  const [isSavingEdit, setIsSavingEdit] = useState(false);

  // New Custom Occasion Modal
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newCode, setNewCode] = useState("");
  const [newNameEn, setNewNameEn] = useState("");
  const [newNameTa, setNewNameTa] = useState("");
  const [newCategory, setNewCategory] = useState("custom");
  const [newDescEn, setNewDescEn] = useState("");
  const [newDescTa, setNewDescTa] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  const fetchOccasions = async () => {
    setLoading(true);
    try {
      const data = await getOccasions();
      if (data && data.occasions) {
        setOccasions(data.occasions);
      }
    } catch (err: any) {
      setError(err?.message || "Failed to load occasions.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOccasions();
  }, []);

  const openEditRules = (occ: OccasionItem) => {
    setEditingOccasion(occ);
    setEditRules({
      prohibit_rahu_kalam: occ.rules?.prohibit_rahu_kalam ?? true,
      prohibit_yamagandam: occ.rules?.prohibit_yamagandam ?? true,
      prohibit_varjyam: occ.rules?.prohibit_varjyam ?? true,
      prohibit_dur_muhurta: occ.rules?.prohibit_dur_muhurta ?? true,
      require_lagna_shuddhi: occ.rules?.require_lagna_shuddhi ?? true,
      require_ashtama_shuddhi: occ.rules?.require_ashtama_shuddhi ?? true,
      require_tara_bala: occ.rules?.require_tara_bala ?? true,
      require_chandra_bala: occ.rules?.require_chandra_bala ?? true,
      min_duration_minutes: occ.rules?.min_duration_minutes ?? 45,
    });
  };

  const handleSaveEditedRules = async () => {
    if (!editingOccasion) return;
    const token = session?.access_token || "cookie";
    setIsSavingEdit(true);
    try {
      await updateOccasion(token, editingOccasion.code, {
        rules: editRules,
      });
      await fetchOccasions();
      setEditingOccasion(null);
    } catch (err: any) {
      alert(`Error updating rules: ${err?.message}`);
    } finally {
      setIsSavingEdit(false);
    }
  };

  const handleCreateCustomOccasion = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = session?.access_token || "cookie";
    setIsCreating(true);
    try {
      await addCustomOccasion(token, {
        code: newCode.trim().toLowerCase().replace(/\s+/g, "_"),
        name_en: newNameEn.trim(),
        name_ta: newNameTa.trim() || newNameEn.trim(),
        category: newCategory as any,
        description_en: newDescEn.trim(),
        description_ta: newDescTa.trim(),
        icon: "sparkles",
        rules: {
          prohibit_rahu_kalam: true,
          prohibit_yamagandam: true,
          prohibit_varjyam: true,
          require_lagna_shuddhi: true,
          min_duration_minutes: 45,
        },
      });
      await fetchOccasions();
      setIsAddModalOpen(false);
      setNewCode("");
      setNewNameEn("");
      setNewNameTa("");
      setNewDescEn("");
      setNewDescTa("");
    } catch (err: any) {
      alert(`Error creating occasion: ${err?.message}`);
    } finally {
      setIsCreating(false);
    }
  };

  const categories = [
    { id: "all", en: "All Categories", ta: "அனைத்தும்" },
    { id: "marriage_relationships", en: "Marriage & Relationships", ta: "திருமணம் / உறவுகள்" },
    { id: "family_ceremonies", en: "Family Ceremonies", ta: "குடும்பச் சடங்குகள்" },
    { id: "home_property", en: "Home & Property", ta: "மனை / இல்லம்" },
    { id: "business_professional", en: "Business & Ventures", ta: "வணிகம் / தொழில்" },
    { id: "travel_vehicles", en: "Travel & Vehicles", ta: "பயணம் / வாகனம்" },
    { id: "education_spiritual", en: "Education & Spiritual", ta: "கல்வி / ஆன்மீகம்" },
    { id: "custom", en: "Custom Occasions", ta: "தனிப்பயன் நிகழ்வுகள்" },
  ];

  const filteredOccasions = occasions.filter(
    (o) => activeCategory === "all" || o.category === activeCategory
  );

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white rounded-3xl p-6 sm:p-7 border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-purple-100 text-purple-800">
              <Sliders className="w-5 h-5" />
            </span>
            <h3 className="text-xl font-extrabold text-slate-900">
              {language === "ta" ? "முகூர்த்த விதிமுறை மேலாண்மை" : "Occasion Rules & Configuration"}
            </h3>
          </div>
          <p className="text-xs text-slate-500 mt-1 max-w-xl">
            {language === "ta"
              ? "ஒவ்வொரு சுப நிகழ்விற்கும் அனுமதிக்கப்பட்ட திதிகள், நட்சத்திரங்கள், கிழமைகள், ராகு-எமகண்டக் கட்டுப்பாடுகள் மற்றும் லக்ன சுத்தி விதிகளை நிர்வகிக்கலாம்."
              : "Inspect and customize classical Muhurta rules, Tithi/Nakshatra permissions, Lagna Shuddhi, and Rahu Kalam prohibitions per ceremony."}
          </p>
        </div>

        {/* Admin Action Button */}
        <div>
          {isAdmin ? (
            <button
              type="button"
              onClick={() => setIsAddModalOpen(true)}
              className="px-4 py-2.5 bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-700 hover:to-amber-800 text-white font-bold rounded-2xl shadow-md text-xs flex items-center gap-2 transition-all"
            >
              <Plus className="w-4 h-4" />
              <span>{language === "ta" ? "+ புதிய நிகழ்வைச் சேர்" : "+ Add Custom Occasion"}</span>
            </button>
          ) : (
            <div className="px-3.5 py-2 rounded-xl bg-slate-100 text-slate-500 text-xs flex items-center gap-2 font-medium">
              <Lock className="w-3.5 h-3.5" />
              <span>{language === "ta" ? "நிர்வாகிக்கு மட்டுமே அனுமதி" : "Admin Config Access Only"}</span>
            </div>
          )}
        </div>
      </div>

      {/* Category Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
        {categories.map((cat) => (
          <button
            key={cat.id}
            type="button"
            onClick={() => setActiveCategory(cat.id)}
            className={`px-3.5 py-2 rounded-xl font-semibold whitespace-nowrap transition-all ${
              activeCategory === cat.id
                ? "bg-slate-900 text-white shadow-sm"
                : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
            }`}
          >
            {language === "ta" ? cat.ta : cat.en}
          </button>
        ))}
      </div>

      {/* Occasions Grid */}
      {loading ? (
        <div className="bg-white rounded-3xl p-12 text-center border border-slate-200 text-xs text-slate-500">
          <div className="w-6 h-6 border-2 border-amber-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          <span>{language === "ta" ? "ஏற்றப்படுகிறது..." : "Loading occasion rules..."}</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredOccasions.map((occ) => {
            const rules = occ.rules || {};
            return (
              <div
                key={occ.code}
                className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between space-y-4"
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <span className="text-[10px] font-bold uppercase tracking-wider text-amber-700 bg-amber-50 px-2 py-0.5 rounded-md border border-amber-100">
                        {occ.category.replace("_", " ")}
                      </span>
                      <h4 className="text-base font-extrabold text-slate-900 mt-1.5">
                        {occ.name_en}
                      </h4>
                      <div className="text-xs text-amber-800 font-tamil font-semibold">
                        {occ.name_ta}
                      </div>
                    </div>

                    {isAdmin && (
                      <button
                        type="button"
                        onClick={() => openEditRules(occ)}
                        className="p-1.5 rounded-xl border border-slate-200 hover:bg-slate-100 text-slate-600 transition-colors"
                        title="Configure rules"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>

                  <p className="text-xs text-slate-600 mt-2 line-clamp-2">
                    {occ.description_en || "Traditional Vedic ceremony configuration with standard Lagna rules."}
                  </p>
                </div>

                {/* Rules Summary Tags */}
                <div className="space-y-2 pt-3 border-t border-slate-100 text-[11px]">
                  <div className="flex flex-wrap gap-1.5">
                    {rules.prohibit_rahu_kalam !== false && (
                      <span className="px-2 py-0.5 rounded-md bg-rose-50 text-rose-700 font-medium">
                        🚫 Rahu Kalam Excluded
                      </span>
                    )}
                    {rules.prohibit_varjyam !== false && (
                      <span className="px-2 py-0.5 rounded-md bg-rose-50 text-rose-700 font-medium">
                        🚫 Varjyam Excluded
                      </span>
                    )}
                    {rules.require_lagna_shuddhi !== false && (
                      <span className="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 font-medium">
                        ✓ Lagna Shuddhi
                      </span>
                    )}
                    {rules.require_ashtama_shuddhi !== false && (
                      <span className="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 font-medium">
                        ✓ 8th House Pure
                      </span>
                    )}
                  </div>

                  <div className="text-[11px] text-slate-500 flex items-center justify-between pt-1">
                    <span>
                      Min Duration: <b>{rules.min_duration_minutes || 45} mins</b>
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      code: {occ.code}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Edit Rules Modal (Admin Only) */}
      {editingOccasion && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-white rounded-3xl p-6 sm:p-7 max-w-lg w-full shadow-2xl border border-slate-200 space-y-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-base font-bold text-slate-900">
                  {language === "ta" ? "விதிமுறை கட்டமைப்பு" : "Configure Occasion Rules"}
                </h3>
                <div className="text-xs text-amber-700 font-semibold mt-0.5">
                  {editingOccasion.name_en} ({editingOccasion.name_ta})
                </div>
              </div>
              <button
                type="button"
                onClick={() => setEditingOccasion(null)}
                className="p-1.5 rounded-xl hover:bg-slate-100 text-slate-500"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs max-h-96 overflow-y-auto pr-1">
              {/* Prohibitions */}
              <div className="space-y-2">
                <label className="font-bold text-slate-800 uppercase tracking-wider text-[10px] block">
                  {language === "ta" ? "தடை செய்யப்பட்ட காலங்கள்" : "Inauspicious Period Prohibitions"}
                </label>

                <label className="flex items-center gap-2 p-2.5 rounded-xl bg-slate-50 border border-slate-200 hover:bg-slate-100 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={editRules.prohibit_rahu_kalam}
                    onChange={(e) =>
                      setEditRules({ ...editRules, prohibit_rahu_kalam: e.target.checked })
                    }
                    className="rounded text-amber-600 focus:ring-amber-500"
                  />
                  <span className="text-slate-800 font-medium">Prohibit Rahu Kalam (ராகு காலம் தவிர்த்தல்)</span>
                </label>

                <label className="flex items-center gap-2 p-2.5 rounded-xl bg-slate-50 border border-slate-200 hover:bg-slate-100 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={editRules.prohibit_yamagandam}
                    onChange={(e) =>
                      setEditRules({ ...editRules, prohibit_yamagandam: e.target.checked })
                    }
                    className="rounded text-amber-600 focus:ring-amber-500"
                  />
                  <span className="text-slate-800 font-medium">Prohibit Yamagandam (எமகண்டம் தவிர்த்தல்)</span>
                </label>

                <label className="flex items-center gap-2 p-2.5 rounded-xl bg-slate-50 border border-slate-200 hover:bg-slate-100 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={editRules.prohibit_varjyam}
                    onChange={(e) =>
                      setEditRules({ ...editRules, prohibit_varjyam: e.target.checked })
                    }
                    className="rounded text-amber-600 focus:ring-amber-500"
                  />
                  <span className="text-slate-800 font-medium">Prohibit Varjyam / Tyajyam (வர்ஜியம் தவிர்த்தல்)</span>
                </label>
              </div>

              {/* Lagna & Compatibility */}
              <div className="space-y-2 pt-2 border-t border-slate-100">
                <label className="font-bold text-slate-800 uppercase tracking-wider text-[10px] block">
                  {language === "ta" ? "லக்னம் & கிரக விதிகள்" : "Lagna & Planetary Purity"}
                </label>

                <label className="flex items-center gap-2 p-2.5 rounded-xl bg-slate-50 border border-slate-200 hover:bg-slate-100 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={editRules.require_lagna_shuddhi}
                    onChange={(e) =>
                      setEditRules({ ...editRules, require_lagna_shuddhi: e.target.checked })
                    }
                    className="rounded text-amber-600 focus:ring-amber-500"
                  />
                  <span className="text-slate-800 font-medium">Require Lagna Shuddhi (லக்ன சுத்தி)</span>
                </label>

                <label className="flex items-center gap-2 p-2.5 rounded-xl bg-slate-50 border border-slate-200 hover:bg-slate-100 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={editRules.require_ashtama_shuddhi}
                    onChange={(e) =>
                      setEditRules({ ...editRules, require_ashtama_shuddhi: e.target.checked })
                    }
                    className="rounded text-amber-600 focus:ring-amber-500"
                  />
                  <span className="text-slate-800 font-medium">Require Ashtama Shuddhi (8-ம் இடம் சுத்தி)</span>
                </label>

                <label className="flex items-center gap-2 p-2.5 rounded-xl bg-slate-50 border border-slate-200 hover:bg-slate-100 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={editRules.require_tara_bala}
                    onChange={(e) =>
                      setEditRules({ ...editRules, require_tara_bala: e.target.checked })
                    }
                    className="rounded text-amber-600 focus:ring-amber-500"
                  />
                  <span className="text-slate-800 font-medium">Enforce Tara Bala when birth star provided</span>
                </label>
              </div>

              {/* Minimum Duration */}
              <div className="pt-2 border-t border-slate-100">
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  {language === "ta" ? "குறைந்தபட்ச கால அளவு (நிமிடம்)" : "Minimum Duration (Minutes)"}
                </label>
                <input
                  type="number"
                  min={15}
                  max={240}
                  value={editRules.min_duration_minutes}
                  onChange={(e) =>
                    setEditRules({ ...editRules, min_duration_minutes: Number(e.target.value) })
                  }
                  className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-800"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setEditingOccasion(null)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={isSavingEdit}
                onClick={handleSaveEditedRules}
                className="px-5 py-2 rounded-xl text-xs font-bold bg-slate-900 hover:bg-black text-white shadow-md transition-colors"
              >
                {isSavingEdit ? "Saving..." : "Save Rule Configuration"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Custom Occasion Modal (Admin Only) */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-white rounded-3xl p-6 sm:p-7 max-w-lg w-full shadow-2xl border border-slate-200 space-y-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900">
                {language === "ta" ? "புதிய சுப நிகழ்வைச் சேர்" : "Create New Custom Occasion"}
              </h3>
              <button
                type="button"
                onClick={() => setIsAddModalOpen(false)}
                className="p-1.5 rounded-xl hover:bg-slate-100 text-slate-500"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateCustomOccasion} className="space-y-4 text-xs">
              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  Occasion Code (Unique Identifier)
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. golden_jubilee_celebration"
                  value={newCode}
                  onChange={(e) => setNewCode(e.target.value)}
                  className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-800 font-mono"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                    English Name
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Golden Jubilee"
                    value={newNameEn}
                    onChange={(e) => setNewNameEn(e.target.value)}
                    className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-800"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                    Tamil Name (தமிழ் பெயர்)
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. பொன்விழா"
                    value={newNameTa}
                    onChange={(e) => setNewNameTa(e.target.value)}
                    className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-800 font-tamil"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  Category
                </label>
                <select
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                  className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-800"
                >
                  <option value="marriage_relationships">Marriage & Relationships</option>
                  <option value="family_ceremonies">Family Ceremonies</option>
                  <option value="home_property">Home & Property</option>
                  <option value="business_professional">Business & Professional</option>
                  <option value="travel_vehicles">Travel & Vehicles</option>
                  <option value="education_spiritual">Education & Spiritual</option>
                  <option value="custom">Custom Ceremonies</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  Description
                </label>
                <textarea
                  rows={2}
                  placeholder="Ceremony description and significance..."
                  value={newDescEn}
                  onChange={(e) => setNewDescEn(e.target.value)}
                  className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-800"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setIsAddModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isCreating}
                  className="px-5 py-2 rounded-xl text-xs font-bold bg-amber-600 hover:bg-amber-700 text-white shadow-md transition-colors"
                >
                  {isCreating ? "Creating..." : "Create Occasion"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
