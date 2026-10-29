"use client";

import React, { useState, useEffect } from "react";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import {
  listSavedMuhurtas,
  updateSavedMuhurta,
  deleteSavedMuhurta,
} from "@/lib/api";
import { SavedMuhurtaItem } from "@/lib/types";
import { MuhurtaReportModal } from "./MuhurtaReportModal";
import {
  Bookmark,
  Search,
  Printer,
  Edit2,
  Trash2,
  Clock,
  MapPin,
  Calendar,
  CheckCircle2,
  AlertTriangle,
  Layers,
  ArrowRightLeft,
  X,
  FileText,
  User,
  Sparkles,
  HelpCircle,
} from "lucide-react";

export function SavedMuhurtasView() {
  const { language } = useLanguage();
  const { session } = useAuth();

  const [savedItems, setSavedItems] = useState<SavedMuhurtaItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [totalCount, setTotalCount] = useState(0);

  // Selected for comparison (array of IDs)
  const [selectedForCompare, setSelectedForCompare] = useState<string[]>([]);
  const [isCompareModalOpen, setIsCompareModalOpen] = useState(false);

  // Edit Modal
  const [editingItem, setEditingItem] = useState<SavedMuhurtaItem | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editClient, setEditClient] = useState("");
  const [editNotes, setEditNotes] = useState("");
  const [isUpdating, setIsUpdating] = useState(false);

  // Report Modal
  const [reportItem, setReportItem] = useState<any | null>(null);
  const [isReportOpen, setIsReportOpen] = useState(false);

  const fetchItems = async () => {
    const token = session?.access_token || "cookie";
    setLoading(true);
    try {
      const res = await listSavedMuhurtas(token, 100, 0, searchQuery || undefined);
      setSavedItems(res.items || []);
      setTotalCount(res.count || 0);
    } catch (err: any) {
      console.error("Failed to fetch saved muhurtas:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, [searchQuery, session]);

  // Handle Edit
  const openEdit = (item: SavedMuhurtaItem) => {
    setEditingItem(item);
    setEditTitle(item.title);
    setEditClient(item.client_name || "");
    setEditNotes(item.notes || "");
  };

  const handleSaveUpdate = async () => {
    if (!editingItem) return;
    const token = session?.access_token || "cookie";
    setIsUpdating(true);
    try {
      await updateSavedMuhurta(token, editingItem.id, {
        title: editTitle,
        client_name: editClient || undefined,
        notes: editNotes || undefined,
      });
      await fetchItems();
      setEditingItem(null);
    } catch (e: any) {
      alert(`Update failed: ${e?.message}`);
    } finally {
      setIsUpdating(false);
    }
  };

  // Handle Delete
  const handleDelete = async (id: string) => {
    if (!confirm(language === "ta" ? "இந்த முகூர்த்தப் பதிவை நீக்க விரும்புகிறீர்களா?" : "Delete this saved Muhurta?")) {
      return;
    }
    const token = session?.access_token || "cookie";
    try {
      await deleteSavedMuhurta(token, id);
      setSavedItems((prev) => prev.filter((i) => i.id !== id));
      setSelectedForCompare((prev) => prev.filter((i) => i !== id));
    } catch (e: any) {
      alert(`Delete failed: ${e?.message}`);
    }
  };

  // Toggle selection for comparison
  const toggleCompare = (id: string) => {
    if (selectedForCompare.includes(id)) {
      setSelectedForCompare(selectedForCompare.filter((i) => i !== id));
    } else {
      if (selectedForCompare.length >= 4) {
        alert("You can compare up to 4 Muhurtas simultaneously.");
        return;
      }
      setSelectedForCompare([...selectedForCompare, id]);
    }
  };

  // Open Report
  const openReport = (item: SavedMuhurtaItem) => {
    const reportData = {
      title: item.title,
      occasion_name: item.occasion_name,
      client_name: item.client_name,
      event_date: item.event_date,
      start_time_local: item.local_start_time,
      end_time_local: item.local_end_time,
      duration_minutes: item.duration_minutes,
      location_name: item.location_name,
      latitude: item.latitude,
      longitude: item.longitude,
      timezone: item.timezone,
      score: item.score,
      status: item.status,
      explanation: item.rule_evaluations?.explanation || "Calculated with classical Vedic rules.",
      tithi: item.panchang_summary?.tithi || { number: 1, name: "Shukla Prathama", paksha: "Shukla" },
      nakshatra: item.panchang_summary?.nakshatra || { number: 1, name: "Ashwini", lord: "Ketu", pada: 1 },
      yoga: item.panchang_summary?.yoga,
      karana: item.panchang_summary?.karana,
      ascendant: item.lagna_summary || { sign_index: 1, sign_name: "Mesha", sign_name_ta: "மேஷம்", degree_in_sign: 15.0 },
      planets: {},
      inauspicious_periods: {
        rahu_kalam: { start_local: "N/A", end_local: "N/A" },
        yamagandam: { start_local: "N/A", end_local: "N/A" },
        varjyam: { start_local: "N/A", end_local: "N/A" },
      },
      auspicious_periods: {
        abhijit: { start_local: "N/A", end_local: "N/A" },
        amrita_kalam: { start_local: "N/A", end_local: "N/A" },
      },
      passed_rules: item.rule_evaluations?.passed || [],
      failed_rules: item.rule_evaluations?.failed || [],
      advisories: item.rule_evaluations?.advisories || [],
      incomplete_checks: item.rule_evaluations?.incomplete || [],
    };
    setReportItem(reportData);
    setIsReportOpen(true);
  };

  // Items chosen for compare
  const compareItems = savedItems.filter((item) =>
    selectedForCompare.includes(item.id)
  );

  return (
    <div className="space-y-6">
      {/* Header & Search Bar */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-amber-100 text-amber-800">
              <Bookmark className="w-5 h-5" />
            </span>
            <h3 className="text-xl font-extrabold text-slate-900">
              {language === "ta" ? "சேமிக்கப்பட்ட முகூர்த்தங்கள்" : "Saved Muhurta Selections"}
            </h3>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            {language === "ta"
              ? "வாடிக்கையாளர்களுக்காகக் கணக்கிடப்பட்டு தொடர் எண்களுடன் பத்திரப்படுத்தப்பட்ட சுப நேரங்கள்."
              : "Sequentially numbered, verified auspicious time windows saved for clients and ceremonies."}
          </p>
        </div>

        {/* Search Input */}
        <div className="relative w-full md:w-72">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
            <Search className="w-4 h-4" />
          </div>
          <input
            type="text"
            placeholder={language === "ta" ? "பெயர் அல்லது நிகழ்வைத் தேடு..." : "Search by title or client..."}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3.5 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-800 focus:ring-2 focus:ring-amber-500"
          />
        </div>
      </div>

      {/* Floating Compare Action Bar if 2+ selected */}
      {selectedForCompare.length >= 2 && (
        <div className="sticky top-20 z-40 bg-gradient-to-r from-slate-900 to-purple-950 text-white rounded-2xl p-4 shadow-xl border border-purple-500/30 flex items-center justify-between gap-4 animate-in fade-in slide-in-from-top-2">
          <div className="flex items-center gap-2 text-xs">
            <ArrowRightLeft className="w-4 h-4 text-amber-400" />
            <span>
              {language === "ta"
                ? `${selectedForCompare.length} முகூர்த்தங்கள் ஒப்பிடத் தேர்ந்தெடுக்கப்பட்டுள்ளன`
                : `${selectedForCompare.length} Muhurtas selected for comparison`}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setSelectedForCompare([])}
              className="px-3 py-1.5 rounded-xl text-xs font-semibold hover:bg-white/10 text-slate-300"
            >
              Clear
            </button>
            <button
              type="button"
              onClick={() => setIsCompareModalOpen(true)}
              className="px-4 py-1.5 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-md flex items-center gap-1.5"
            >
              <Layers className="w-3.5 h-3.5" />
              <span>{language === "ta" ? "ஒப்பீடு காண்க" : "Compare Side-by-Side"}</span>
            </button>
          </div>
        </div>
      )}

      {/* Saved Records List */}
      {loading ? (
        <div className="bg-white rounded-3xl p-12 text-center border border-slate-200 text-xs text-slate-500">
          <div className="w-6 h-6 border-2 border-amber-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          <span>{language === "ta" ? "பதிவுகள் பெறப்படுகின்றன..." : "Loading saved selections..."}</span>
        </div>
      ) : savedItems.length === 0 ? (
        <div className="bg-white rounded-3xl p-12 text-center border border-slate-200">
          <Bookmark className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h4 className="text-base font-bold text-slate-700">
            {language === "ta" ? "சேமிக்கப்பட்ட முகூர்த்தங்கள் எதுவும் இல்லை" : "No saved Muhurtas yet"}
          </h4>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            {language === "ta"
              ? "முகூர்த்தத் தேடலில் பொருத்தமான நேரத்தைத் தேர்வு செய்து 'சேமி' பொத்தானைக் கிளிக் செய்யவும்."
              : "Search for auspicious dates and click 'Save Selection' on any candidate window to preserve it."}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {savedItems.map((item) => {
            const isChecked = selectedForCompare.includes(item.id);

            return (
              <div
                key={item.id}
                className={`bg-white rounded-3xl p-6 border transition-all shadow-sm hover:shadow-md flex flex-col justify-between space-y-4 ${
                  isChecked ? "border-amber-500 ring-2 ring-amber-500/20" : "border-slate-200"
                }`}
              >
                <div>
                  {/* Top Bar: Sequential Number, Compare Checkbox, Status */}
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <div className="flex items-center gap-2">
                      <span className="w-8 h-8 rounded-xl bg-amber-100 text-amber-900 font-extrabold text-xs flex items-center justify-center font-mono">
                        #{item.display_number}
                      </span>
                      <div>
                        <div className="text-xs font-bold text-slate-900 truncate max-w-[150px]">
                          {item.occasion_name}
                        </div>
                        <div className="text-[10px] text-slate-400">
                          {new Date(item.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>

                    <label className="flex items-center gap-1.5 text-[11px] text-slate-600 cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => toggleCompare(item.id)}
                        className="rounded text-amber-600 focus:ring-amber-500"
                      />
                      <span>Compare</span>
                    </label>
                  </div>

                  {/* Title & Client Name */}
                  <div className="mt-3">
                    <h4 className="text-sm font-extrabold text-slate-900">{item.title}</h4>
                    {item.client_name && (
                      <div className="text-xs font-semibold text-purple-700 mt-0.5 flex items-center gap-1">
                        <User className="w-3 h-3" />
                        <span>{item.client_name}</span>
                      </div>
                    )}
                  </div>

                  {/* Date & Time Window */}
                  <div className="mt-3 p-3 rounded-2xl bg-amber-50/60 border border-amber-100 space-y-1 text-xs">
                    <div className="flex items-center justify-between font-bold text-slate-900">
                      <div className="flex items-center gap-1">
                        <Calendar className="w-3.5 h-3.5 text-amber-700" />
                        <span>{item.event_date}</span>
                      </div>
                      <span className="text-amber-800 font-extrabold">{item.score}/100</span>
                    </div>

                    <div className="flex items-center justify-between text-slate-600 text-[11px]">
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3 text-slate-400" />
                        <span>
                          {item.local_start_time} – {item.local_end_time}
                        </span>
                      </div>
                      <span>({item.duration_minutes}m)</span>
                    </div>

                    <div className="text-[10px] text-slate-500 truncate flex items-center gap-1 pt-0.5">
                      <MapPin className="w-3 h-3 text-slate-400 flex-shrink-0" />
                      <span className="truncate">{item.location_name}</span>
                    </div>
                  </div>

                  {/* Panchang Limb Quick Pills */}
                  <div className="grid grid-cols-2 gap-1.5 text-[11px] mt-3">
                    <div className="px-2.5 py-1 rounded-lg bg-slate-50 text-slate-700 truncate">
                      Lagna: <b>{item.lagna_summary?.sign_name || "N/A"}</b>
                    </div>
                    <div className="px-2.5 py-1 rounded-lg bg-slate-50 text-slate-700 truncate">
                      Star: <b>{item.panchang_summary?.nakshatra?.name || "N/A"}</b>
                    </div>
                  </div>

                  {/* User Notes */}
                  {item.notes && (
                    <div className="mt-2.5 p-2 rounded-xl bg-slate-50 text-[11px] text-slate-600 italic">
                      "{item.notes}"
                    </div>
                  )}
                </div>

                {/* Card Action Buttons */}
                <div className="flex items-center justify-between pt-3 border-t border-slate-100 text-xs">
                  <button
                    type="button"
                    onClick={() => openReport(item)}
                    className="px-2.5 py-1.5 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-700 font-semibold flex items-center gap-1 transition-colors"
                  >
                    <Printer className="w-3.5 h-3.5" />
                    <span>Certificate</span>
                  </button>

                  <div className="flex items-center gap-1.5">
                    <button
                      type="button"
                      onClick={() => openEdit(item)}
                      className="p-1.5 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-600"
                      title="Edit notes & client name"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                    </button>
                    <button
                      type="button"
                      onClick={() => handleDelete(item.id)}
                      className="p-1.5 rounded-xl border border-rose-200 hover:bg-rose-50 text-rose-600"
                      title="Delete record"
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

      {/* Side-by-Side Comparison Matrix Modal */}
      {isCompareModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="bg-white rounded-3xl p-6 sm:p-8 max-w-7xl w-full shadow-2xl border border-slate-200 space-y-6 my-8">
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <div className="flex items-center gap-2">
                <span className="p-2 rounded-xl bg-purple-100 text-purple-800">
                  <ArrowRightLeft className="w-5 h-5" />
                </span>
                <div>
                  <h3 className="text-lg font-bold text-slate-900">
                    {language === "ta" ? "முகூர்த்த நேரங்கள் ஒப்பீடு" : "Side-by-Side Muhurta Comparison"}
                  </h3>
                  <div className="text-xs text-slate-500">
                    Comparing {compareItems.length} candidate windows
                  </div>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setIsCompareModalOpen(false)}
                className="p-1.5 rounded-xl hover:bg-slate-100 text-slate-500"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Comparison Matrix Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50">
                    <th className="p-3 font-bold text-slate-500 uppercase tracking-wider text-[10px] w-36">
                      Parameter
                    </th>
                    {compareItems.map((item) => (
                      <th key={item.id} className="p-3 font-bold text-slate-900 min-w-[200px]">
                        <div className="flex items-center gap-1.5">
                          <span className="px-1.5 py-0.5 rounded bg-amber-100 text-amber-900 font-mono text-[10px]">
                            #{item.display_number}
                          </span>
                          <span className="truncate">{item.title}</span>
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  <tr>
                    <td className="p-3 font-semibold text-slate-500">Date & Day</td>
                    {compareItems.map((item) => (
                      <td key={item.id} className="p-3 font-extrabold text-slate-900">
                        {item.event_date}
                      </td>
                    ))}
                  </tr>

                  <tr>
                    <td className="p-3 font-semibold text-slate-500">Time Window</td>
                    {compareItems.map((item) => (
                      <td key={item.id} className="p-3 text-amber-800 font-bold">
                        {item.local_start_time} – {item.local_end_time}
                      </td>
                    ))}
                  </tr>

                  <tr>
                    <td className="p-3 font-semibold text-slate-500">Duration</td>
                    {compareItems.map((item) => (
                      <td key={item.id} className="p-3 text-slate-700">
                        {item.duration_minutes} mins
                      </td>
                    ))}
                  </tr>

                  <tr className="bg-amber-50/40">
                    <td className="p-3 font-semibold text-slate-700">Rule Score</td>
                    {compareItems.map((item) => (
                      <td key={item.id} className="p-3 font-black text-sm text-slate-900">
                        {item.score}/100
                      </td>
                    ))}
                  </tr>

                  <tr>
                    <td className="p-3 font-semibold text-slate-500">Ascendant / Lagna</td>
                    {compareItems.map((item) => (
                      <td key={item.id} className="p-3 font-bold text-purple-900">
                        {item.lagna_summary?.sign_name} ({item.lagna_summary?.sign_name_ta})
                      </td>
                    ))}
                  </tr>

                  <tr>
                    <td className="p-3 font-semibold text-slate-500">Nakshatra</td>
                    {compareItems.map((item) => (
                      <td key={item.id} className="p-3 text-slate-800">
                        {item.panchang_summary?.nakshatra?.name || "N/A"}
                      </td>
                    ))}
                  </tr>

                  <tr>
                    <td className="p-3 font-semibold text-slate-500">Tithi</td>
                    {compareItems.map((item) => (
                      <td key={item.id} className="p-3 text-slate-800">
                        {item.panchang_summary?.tithi?.name || "N/A"}
                      </td>
                    ))}
                  </tr>

                  <tr>
                    <td className="p-3 font-semibold text-slate-500">Location</td>
                    {compareItems.map((item) => (
                      <td key={item.id} className="p-3 text-slate-600 truncate max-w-[200px]">
                        {item.location_name}
                      </td>
                    ))}
                  </tr>

                  <tr>
                    <td className="p-3 font-semibold text-slate-500">Actions</td>
                    {compareItems.map((item) => (
                      <td key={item.id} className="p-3">
                        <button
                          type="button"
                          onClick={() => {
                            setIsCompareModalOpen(false);
                            openReport(item);
                          }}
                          className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-900 text-white hover:bg-black"
                        >
                          Print Report
                        </button>
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Edit Item Modal */}
      {editingItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-white rounded-3xl p-6 sm:p-7 max-w-md w-full shadow-2xl border border-slate-200 space-y-4">
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Edit2 className="w-4 h-4 text-amber-600" />
              <span>Edit Saved Muhurta Details</span>
            </h3>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Display Title
              </label>
              <input
                type="text"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-800"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Client / Family Name
              </label>
              <input
                type="text"
                value={editClient}
                onChange={(e) => setEditClient(e.target.value)}
                className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-800"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Notes
              </label>
              <textarea
                rows={3}
                value={editNotes}
                onChange={(e) => setEditNotes(e.target.value)}
                className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-800"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setEditingItem(null)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={isUpdating}
                onClick={handleSaveUpdate}
                className="px-5 py-2 rounded-xl text-xs font-bold bg-amber-600 hover:bg-amber-700 text-white shadow-md"
              >
                {isUpdating ? "Saving..." : "Save Changes"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Official Certificate Report Modal */}
      {reportItem && (
        <MuhurtaReportModal
          isOpen={isReportOpen}
          onClose={() => setIsReportOpen(false)}
          reportData={reportItem}
        />
      )}
    </div>
  );
}
