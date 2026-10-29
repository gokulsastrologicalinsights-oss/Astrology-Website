"use client";

import React, { useState, useEffect, useMemo } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  getPredictionCategories,
  listRuleDefinitions,
  saveRuleDefinition,
  validateRuleDefinition,
  testRuleDefinition,
  toggleRuleStatus,
} from "@/lib/api";
import {
  PredictionCategoryGroup,
  PredictionSubcategory,
} from "@/lib/types";
import {
  Shield,
  ShieldAlert,
  Compass,
  CheckCircle2,
  AlertCircle,
  Plus,
  Edit3,
  Search,
  Filter,
  RefreshCw,
  ArrowLeft,
  Sliders,
  BookOpen,
  Code2,
  Play,
  Save,
  Trash2,
  Check,
  X,
} from "lucide-react";

export default function AdminRulesPage() {
  const { language } = useLanguage();
  const { user, session, role, isLoading: authLoading } = useAuth();

  const [categories, setCategories] = useState<PredictionCategoryGroup[]>([]);
  const [rules, setRules] = useState<any[]>([]);
  const [loadingRules, setLoadingRules] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Filters
  const [selectedGroup, setSelectedGroup] = useState<string>("all");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Editor Modal / Drawer state
  const [isEditorOpen, setIsEditorOpen] = useState<boolean>(false);
  const [editingRuleId, setEditingRuleId] = useState<string | null>(null);
  const [ruleIdInput, setRuleIdInput] = useState<string>("");
  const [nameEn, setNameEn] = useState<string>("");
  const [nameTa, setNameTa] = useState<string>("");
  const [categorySlug, setCategorySlug] = useState<string>("marriage_prospects");
  const [subcategory, setSubcategory] = useState<string>("");
  const [astrologySystem, setAstrologySystem] = useState<string>("vedic");
  const [chartScope, setChartScope] = useState<string>("d1");
  const [calculationMode, setCalculationMode] = useState<string>("thirukanitha");
  const [severity, setSeverity] = useState<string>("neutral");
  const [conditionTreeJson, setConditionTreeJson] = useState<string>(
    JSON.stringify(
      {
        condition_type: "planet_house",
        planet: "Jupiter",
        house: 7,
        chart: "d1",
      },
      null,
      2
    )
  );
  const [interpretationEn, setInterpretationEn] = useState<string>("");
  const [interpretationTa, setInterpretationTa] = useState<string>("");
  const [principleEn, setPrincipleEn] = useState<string>("");
  const [principleTa, setPrincipleTa] = useState<string>("");
  const [sourceReference, setSourceReference] = useState<string>("");
  const [limitationsEn, setLimitationsEn] = useState<string>("");
  const [limitationsTa, setLimitationsTa] = useState<string>("");
  const [isEnabled, setIsEnabled] = useState<boolean>(true);
  const [isDraft, setIsDraft] = useState<boolean>(false);

  // Validation & Test state
  const [isValidating, setIsValidating] = useState<boolean>(false);
  const [validationResult, setValidationResult] = useState<{
    is_valid: boolean;
    errors: string[];
  } | null>(null);
  const [isTesting, setIsTesting] = useState<boolean>(false);
  const [testResult, setTestResult] = useState<any | null>(null);
  const [savedHoroscopes, setSavedHoroscopes] = useState<any[]>([]);
  const [selectedHoroscopeId, setSelectedHoroscopeId] = useState<string>("");

  const isAdmin = role === "admin";

  // Fetch initial data
  const loadData = async () => {
    if (!session?.access_token) return;
    setLoadingRules(true);
    setErrorMessage(null);
    try {
      const [cats, ruleList] = await Promise.all([
        getPredictionCategories(),
        listRuleDefinitions(undefined, session.access_token),
      ]);
      setCategories(cats);
      setRules(ruleList);
    } catch (err: any) {
      setErrorMessage(err?.message || "Failed to load rules or categories.");
    } finally {
      setLoadingRules(false);
    }
  };

  useEffect(() => {
    if (isAdmin && session?.access_token) {
      loadData();
      // Load saved horoscopes for test-run dropdown
      fetch("/api/horoscopes?limit=50")
        .then((r) => r.json())
        .then((d) => {
          if (d.horoscopes) {
            setSavedHoroscopes(d.horoscopes);
            if (d.horoscopes.length > 0) {
              setSelectedHoroscopeId(d.horoscopes[0].id);
            }
          }
        })
        .catch(() => {});
    }
  }, [isAdmin, session?.access_token]);

  // Subcategories lookup
  const subcategoriesList = useMemo(() => {
    const list: PredictionSubcategory[] = [];
    categories.forEach((g) => {
      g.subcategories.forEach((s) => list.push(s));
    });
    return list;
  }, [categories]);

  // Filtered rules
  const filteredRules = useMemo(() => {
    return rules.filter((r) => {
      if (selectedCategory !== "all" && r.category_slug !== selectedCategory) {
        return false;
      }
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        const matchName =
          r.name_en.toLowerCase().includes(q) ||
          (r.name_ta && r.name_ta.toLowerCase().includes(q)) ||
          r.rule_id.toLowerCase().includes(q);
        if (!matchName) return false;
      }
      return true;
    });
  }, [rules, selectedCategory, searchQuery]);

  // Open editor for new rule
  const handleOpenCreate = () => {
    setEditingRuleId(null);
    setRuleIdInput(`RULE-CUSTOM-${Math.floor(100 + Math.random() * 900)}`);
    setNameEn("");
    setNameTa("");
    setCategorySlug("marriage_prospects");
    setSubcategory("first_marriage");
    setAstrologySystem("vedic");
    setChartScope("d1");
    setCalculationMode("thirukanitha");
    setSeverity("favorable");
    setConditionTreeJson(
      JSON.stringify(
        {
          condition_type: "planet_house",
          planet: "Jupiter",
          house: 7,
          chart: "d1",
        },
        null,
        2
      )
    );
    setInterpretationEn("");
    setInterpretationTa("");
    setPrincipleEn("");
    setPrincipleTa("");
    setSourceReference("");
    setLimitationsEn("");
    setLimitationsTa("");
    setIsEnabled(true);
    setIsDraft(false);
    setValidationResult(null);
    setTestResult(null);
    setIsEditorOpen(true);
  };

  // Open editor to edit existing rule
  const handleOpenEdit = (rule: any) => {
    setEditingRuleId(rule.rule_id);
    setRuleIdInput(rule.rule_id);
    setNameEn(rule.name_en);
    setNameTa(rule.name_ta || "");
    setCategorySlug(rule.category_slug);
    setSubcategory(rule.subcategory || "");
    setAstrologySystem(rule.astrology_system || "vedic");
    setChartScope(rule.chart_scope || "d1");
    setCalculationMode(rule.calculation_mode || "thirukanitha");
    setSeverity(rule.severity || "neutral");
    setConditionTreeJson(JSON.stringify(rule.condition_tree || {}, null, 2));
    setInterpretationEn(rule.interpretation_en);
    setInterpretationTa(rule.interpretation_ta || "");
    setPrincipleEn(rule.astrological_principle_en);
    setPrincipleTa(rule.astrological_principle_ta || "");
    setSourceReference(rule.source_reference || "");
    setLimitationsEn(rule.limitations_en || "");
    setLimitationsTa(rule.limitations_ta || "");
    setIsEnabled(rule.is_enabled ?? true);
    setIsDraft(rule.is_draft ?? false);
    setValidationResult(null);
    setTestResult(null);
    setIsEditorOpen(true);
  };

  // Toggle status
  const handleToggleStatus = async (ruleId: string, currentStatus: boolean) => {
    if (!session?.access_token) return;
    try {
      await toggleRuleStatus(ruleId, !currentStatus, session.access_token);
      setRules((prev) =>
        prev.map((r) => (r.rule_id === ruleId ? { ...r, is_enabled: !currentStatus } : r))
      );
      setSuccessMessage(`Rule ${ruleId} status updated successfully.`);
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      setErrorMessage(err?.message || "Failed to toggle rule status.");
    }
  };

  // Validate AST
  const handleValidateAst = async () => {
    setIsValidating(true);
    setValidationResult(null);
    try {
      const parsedAst = JSON.parse(conditionTreeJson);
      const rulePayload = {
        rule_id: ruleIdInput,
        name_en: nameEn,
        category_slug: categorySlug,
        subcategory,
        interpretation_en: interpretationEn,
        astrological_principle_en: principleEn,
        condition_tree: parsedAst,
      };
      const res = await validateRuleDefinition(rulePayload);
      setValidationResult(res);
    } catch (jsonErr: any) {
      setValidationResult({
        is_valid: false,
        errors: [`JSON Syntax Error: ${jsonErr.message}`],
      });
    } finally {
      setIsValidating(false);
    }
  };

  // Test Run
  const handleTestRun = async () => {
    if (!selectedHoroscopeId) {
      alert("Please select a saved horoscope to test against.");
      return;
    }
    setIsTesting(true);
    setTestResult(null);
    try {
      const parsedAst = JSON.parse(conditionTreeJson);
      const rulePayload = {
        rule_id: ruleIdInput,
        name_en: nameEn,
        name_ta: nameTa,
        category_slug: categorySlug,
        subcategory,
        astrology_system: astrologySystem,
        chart_scope: chartScope,
        calculation_mode: calculationMode,
        severity,
        interpretation_en: interpretationEn,
        interpretation_ta: interpretationTa,
        astrological_principle_en: principleEn,
        astrological_principle_ta: principleTa,
        source_reference: sourceReference,
        limitations_en: limitationsEn,
        limitations_ta: limitationsTa,
        condition_tree: parsedAst,
      };

      const res = await testRuleDefinition(
        {
          rule: rulePayload,
          saved_horoscope_id: selectedHoroscopeId,
          language: language,
        },
        session?.access_token
      );
      setTestResult(res);
    } catch (err: any) {
      setTestResult({ error: err?.message || "Test run failed." });
    } finally {
      setIsTesting(false);
    }
  };

  // Save rule
  const handleSaveRule = async (saveAsDraft: boolean = false) => {
    setErrorMessage(null);
    try {
      const parsedAst = JSON.parse(conditionTreeJson);
      const rulePayload = {
        rule_id: ruleIdInput.trim(),
        name_en: nameEn.trim(),
        name_ta: nameTa.trim(),
        category_slug: categorySlug,
        subcategory: subcategory || undefined,
        astrology_system: astrologySystem,
        chart_scope: chartScope,
        calculation_mode: calculationMode,
        severity,
        condition_tree: parsedAst,
        interpretation_en: interpretationEn.trim(),
        interpretation_ta: interpretationTa.trim(),
        astrological_principle_en: principleEn.trim(),
        astrological_principle_ta: principleTa.trim(),
        source_reference: sourceReference.trim() || undefined,
        limitations_en: limitationsEn.trim() || undefined,
        limitations_ta: limitationsTa.trim() || undefined,
        is_enabled: isEnabled,
        is_draft: saveAsDraft,
      };

      await saveRuleDefinition(rulePayload, session?.access_token);
      setSuccessMessage(
        `Rule '${ruleIdInput}' successfully ${editingRuleId ? "updated" : "created"}!`
      );
      setIsEditorOpen(false);
      loadData();
      setTimeout(() => setSuccessMessage(null), 4000);
    } catch (err: any) {
      setErrorMessage(err?.message || "Failed to save rule.");
    }
  };

  // Preset Template loader
  const applyPresetTemplate = (preset: string) => {
    if (preset === "conjunction") {
      setConditionTreeJson(
        JSON.stringify(
          {
            condition_type: "planet_conjunction",
            planets: ["Venus", "Rahu"],
            same_sign_only: true,
            orb_degrees: 8.0,
            chart: "d1",
          },
          null,
          2
        )
      );
    } else if (preset === "house_lord") {
      setConditionTreeJson(
        JSON.stringify(
          {
            condition_type: "house_lord_placement",
            house: 10,
            placed_in_house: 1,
            chart: "d1",
          },
          null,
          2
        )
      );
    } else if (preset === "aspect") {
      setConditionTreeJson(
        JSON.stringify(
          {
            condition_type: "planet_aspect",
            aspecting_planet: "Jupiter",
            target_type: "house",
            target_value: 2,
            aspect_type: "any",
            chart: "d1",
          },
          null,
          2
        )
      );
    } else if (preset === "compound_and") {
      setConditionTreeJson(
        JSON.stringify(
          {
            condition_type: "compound",
            operator: "AND",
            conditions: [
              {
                condition_type: "planet_house",
                planet: "Sun",
                house: 10,
                chart: "d1",
              },
              {
                condition_type: "house_lord_placement",
                house: 10,
                placed_in_house: [1, 9, 10, 11],
                chart: "d1",
              },
            ],
          },
          null,
          2
        )
      );
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-[50vh] flex items-center justify-center">
        <RefreshCw className="w-6 h-6 animate-spin text-[#B4872B]" />
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="p-6 rounded-xl border border-rose-300 bg-rose-50 text-center space-y-3">
          <ShieldAlert className="w-10 h-10 text-rose-600 mx-auto" />
          <h2 className="text-lg font-bold text-rose-900">Access Denied</h2>
          <p className="text-xs text-rose-700">
            Administrative role is required to modify the shared astrological rules library.
          </p>
          <Link
            href="/admin"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-rose-700 text-white text-xs font-bold"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Return to Admin Dashboard</span>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 sm:py-8 space-y-6">
      <Breadcrumbs
        items={[
          {
            label: language === "ta" ? "டாஷ்போர்டு" : "Dashboard",
            href: "/dashboard",
          },
          {
            label: language === "ta" ? "நிர்வாக மையம்" : "Admin Portal",
            href: "/admin",
          },
          {
            label: language === "ta" ? "ஜோதிட விதிகள்" : "Astrological Rules",
          },
        ]}
      />

      {/* Header */}
      <div className="bg-white rounded-xl border border-[#D9DEE7] p-5 shadow-2xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-[#FAF2DE] text-[#B4872B] border border-[#D8BD80]">
              <Shield className="w-4 h-4" />
            </span>
            <h1 className="font-serif text-lg sm:text-xl font-bold text-[#183047]">
              Astrological Rules Management
            </h1>
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-[#153F6B] text-white">
              Admin Authorized
            </span>
          </div>
          <p className="text-xs text-[#52667E]">
            Create, edit, validate, and version deterministic condition trees across 8 classical categories.
          </p>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <Link
            href="/admin"
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg border border-[#D9DEE7] bg-white text-xs font-semibold text-[#52667E] hover:bg-[#F2F3F5] transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Admin Overview</span>
          </Link>
          <button
            type="button"
            onClick={handleOpenCreate}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-[#B4872B] hover:bg-[#8C6D23] text-white text-xs font-bold shadow-2xs transition-colors cursor-pointer"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Create New Rule</span>
          </button>
        </div>
      </div>

      {/* Feedback Messages */}
      {successMessage && (
        <div className="p-3.5 rounded-lg border border-emerald-300 bg-emerald-50 text-xs font-semibold text-emerald-800 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}
      {errorMessage && (
        <div className="p-3.5 rounded-lg border border-rose-300 bg-rose-50 text-xs font-semibold text-rose-800 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Filter Bar */}
      <div className="bg-white rounded-xl border border-[#D9DEE7] p-4 shadow-2xs flex flex-col md:flex-row items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-3 w-full md:w-auto flex-wrap">
          {/* Category Filter */}
          <div className="flex items-center gap-1.5">
            <span className="text-[#8190A6] font-semibold">Category:</span>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="rounded-lg border border-[#D9DEE7] p-1.5 text-xs text-[#183047] bg-white focus:ring-1 focus:ring-[#B4872B]"
            >
              <option value="all">All Categories ({rules.length})</option>
              {subcategoriesList.map((s) => (
                <option key={s.slug} value={s.slug}>
                  {s.name_en}
                </option>
              ))}
            </select>
          </div>

          {/* Search Box */}
          <div className="relative flex-1 md:w-64">
            <input
              type="text"
              placeholder="Search rule ID, title..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-7 pr-3 py-1.5 rounded-lg border border-[#D9DEE7] text-xs text-[#183047] focus:ring-1 focus:ring-[#B4872B]"
            />
            <Search className="w-3.5 h-3.5 text-[#8190A6] absolute left-2 top-2" />
          </div>
        </div>

        <div className="text-xs text-[#8190A6]">
          Showing <strong>{filteredRules.length}</strong> of {rules.length} rules
        </div>
      </div>

      {/* Rules Table */}
      <div className="bg-white rounded-xl border border-[#D9DEE7] shadow-2xs overflow-hidden">
        {loadingRules ? (
          <div className="py-12 text-center text-xs text-[#8190A6] space-y-2">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto text-[#B4872B]" />
            <p>Loading rules library...</p>
          </div>
        ) : filteredRules.length === 0 ? (
          <div className="py-12 text-center text-xs text-[#8190A6]">
            No rules matching the current filters.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-[#FAF8F2] text-[#8C6D23] font-bold border-b border-[#E2E8F0] uppercase tracking-wider text-[11px]">
                <tr>
                  <th className="p-3">Rule ID & Ver</th>
                  <th className="p-3">Rule Title</th>
                  <th className="p-3">Category</th>
                  <th className="p-3">System / Scope</th>
                  <th className="p-3">Severity</th>
                  <th className="p-3">Status</th>
                  <th className="p-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F2F3F5]">
                {filteredRules.map((rule) => {
                  return (
                    <tr key={rule.rule_id} className="hover:bg-[#FAF8F2]/40 transition-colors">
                      <td className="p-3 font-mono font-bold text-[#153F6B]">
                        {rule.rule_id} <span className="text-[10px] text-[#8190A6]">v{rule.version}</span>
                      </td>
                      <td className="p-3">
                        <div className="font-bold text-[#183047]">{rule.name_en}</div>
                        {rule.name_ta && (
                          <div className="text-[11px] text-[#8190A6]">{rule.name_ta}</div>
                        )}
                      </td>
                      <td className="p-3 text-[#52667E] capitalize">
                        {rule.category_slug.replace(/_/g, " ")}
                      </td>
                      <td className="p-3">
                        <div className="flex items-center gap-1 flex-wrap">
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-[#F2F3F5] text-[#153F6B] border border-[#D9DEE7] uppercase">
                            {rule.astrology_system}
                          </span>
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-[#F2F3F5] text-[#52667E] border border-[#D9DEE7] uppercase">
                            {rule.chart_scope}
                          </span>
                        </div>
                      </td>
                      <td className="p-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${
                            rule.severity === "favorable"
                              ? "bg-emerald-50 text-emerald-800 border-emerald-300"
                              : rule.severity === "unfavorable"
                              ? "bg-rose-50 text-rose-800 border-rose-300"
                              : "bg-blue-50 text-blue-800 border-blue-300"
                          }`}
                        >
                          {rule.severity}
                        </span>
                      </td>
                      <td className="p-3">
                        <button
                          type="button"
                          onClick={() => handleToggleStatus(rule.rule_id, rule.is_enabled)}
                          className={`px-2.5 py-1 rounded text-[10px] font-bold transition-colors cursor-pointer ${
                            rule.is_enabled
                              ? "bg-emerald-100 text-emerald-800 hover:bg-emerald-200"
                              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                          }`}
                        >
                          {rule.is_enabled ? "Active" : "Disabled"}
                        </button>
                      </td>
                      <td className="p-3 text-right">
                        <button
                          type="button"
                          onClick={() => handleOpenEdit(rule)}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-[#FAF2DE] text-[#8C6D23] font-bold text-[11px] border border-[#D8BD80] hover:bg-[#FAF8F2] transition-colors cursor-pointer"
                        >
                          <Edit3 className="w-3 h-3" />
                          <span>Edit</span>
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Editor Modal */}
      {isEditorOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white rounded-xl border border-[#D9DEE7] shadow-xl w-full max-w-5xl max-h-[90vh] overflow-y-auto p-5 sm:p-6 space-y-5">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-[#F2F3F5] pb-3">
              <div className="flex items-center gap-2">
                <Compass className="w-5 h-5 text-[#B4872B]" />
                <h3 className="font-bold text-base text-[#183047]">
                  {editingRuleId ? `Edit Rule: ${editingRuleId}` : "Create New Astrological Rule"}
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setIsEditorOpen(false)}
                className="text-[#8190A6] hover:text-[#183047] p-1 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Form Fields */}
            <div className="space-y-4 text-xs">
              {/* Row 1: ID, Category, Subcategory */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-[#52667E]">Rule ID</label>
                  <input
                    type="text"
                    value={ruleIdInput}
                    disabled={!!editingRuleId}
                    onChange={(e) => setRuleIdInput(e.target.value)}
                    className="w-full p-2 rounded-lg border border-[#D9DEE7] font-mono text-xs disabled:bg-gray-100"
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-[#52667E]">Category</label>
                  <select
                    value={categorySlug}
                    onChange={(e) => setCategorySlug(e.target.value)}
                    className="w-full p-2 rounded-lg border border-[#D9DEE7] bg-white text-xs"
                  >
                    {subcategoriesList.map((s) => (
                      <option key={s.slug} value={s.slug}>
                        {s.name_en}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-[#52667E]">Subcategory (Optional)</label>
                  <input
                    type="text"
                    value={subcategory}
                    onChange={(e) => setSubcategory(e.target.value)}
                    placeholder="e.g. first_marriage"
                    className="w-full p-2 rounded-lg border border-[#D9DEE7] text-xs"
                  />
                </div>
              </div>

              {/* Row 2: Names EN & TA */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-[#52667E]">Rule Name (English)</label>
                  <input
                    type="text"
                    value={nameEn}
                    onChange={(e) => setNameEn(e.target.value)}
                    placeholder="e.g. 7th Lord in 7th House"
                    className="w-full p-2 rounded-lg border border-[#D9DEE7] text-xs"
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-[#52667E]">Rule Name (Tamil)</label>
                  <input
                    type="text"
                    value={nameTa}
                    onChange={(e) => setNameTa(e.target.value)}
                    placeholder="e.g. 7-ஆம் அதிபதி 7-ல் ஆட்சி"
                    className="w-full p-2 rounded-lg border border-[#D9DEE7] text-xs"
                  />
                </div>
              </div>

              {/* Row 3: System, Scope, Severity */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-[#52667E]">Astrology System</label>
                  <select
                    value={astrologySystem}
                    onChange={(e) => setAstrologySystem(e.target.value)}
                    className="w-full p-2 rounded-lg border border-[#D9DEE7] bg-white text-xs"
                  >
                    <option value="vedic">Vedic (Parashari)</option>
                    <option value="kp">KP (Krishnamurti)</option>
                    <option value="combined">Combined (Vedic + KP)</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-[#52667E]">Chart Scope</label>
                  <select
                    value={chartScope}
                    onChange={(e) => setChartScope(e.target.value)}
                    className="w-full p-2 rounded-lg border border-[#D9DEE7] bg-white text-xs"
                  >
                    <option value="d1">D1 Only (Rasi)</option>
                    <option value="d9">D9 Only (Navamsa)</option>
                    <option value="both">Both (D1 + D9 Independently)</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-[#52667E]">Severity / Auspiciousness</label>
                  <select
                    value={severity}
                    onChange={(e) => setSeverity(e.target.value)}
                    className="w-full p-2 rounded-lg border border-[#D9DEE7] bg-white text-xs"
                  >
                    <option value="favorable">Favorable</option>
                    <option value="neutral">Neutral</option>
                    <option value="unfavorable">Unfavorable</option>
                    <option value="mixed">Mixed</option>
                    <option value="info">Informational</option>
                  </select>
                </div>
              </div>

              {/* Condition Tree Editor & Presets */}
              <div className="space-y-2 bg-[#F8FAFC] p-3.5 rounded-lg border border-[#E2E8F0]">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center gap-1.5 font-bold text-[#183047]">
                    <Code2 className="w-4 h-4 text-[#B4872B]" />
                    <span>Declarative Condition Tree (JSON AST)</span>
                  </div>
                  {/* Preset Pills */}
                  <div className="flex items-center gap-1 flex-wrap">
                    <span className="text-[10px] text-[#8190A6]">Presets:</span>
                    <button
                      type="button"
                      onClick={() => applyPresetTemplate("conjunction")}
                      className="px-2 py-0.5 rounded bg-white border border-[#D9DEE7] text-[10px] font-semibold hover:bg-gray-50"
                    >
                      Conjunction
                    </button>
                    <button
                      type="button"
                      onClick={() => applyPresetTemplate("house_lord")}
                      className="px-2 py-0.5 rounded bg-white border border-[#D9DEE7] text-[10px] font-semibold hover:bg-gray-50"
                    >
                      House Lord
                    </button>
                    <button
                      type="button"
                      onClick={() => applyPresetTemplate("aspect")}
                      className="px-2 py-0.5 rounded bg-white border border-[#D9DEE7] text-[10px] font-semibold hover:bg-gray-50"
                    >
                      Aspect
                    </button>
                    <button
                      type="button"
                      onClick={() => applyPresetTemplate("compound_and")}
                      className="px-2 py-0.5 rounded bg-white border border-[#D9DEE7] text-[10px] font-semibold hover:bg-gray-50"
                    >
                      AND Tree
                    </button>
                  </div>
                </div>

                <textarea
                  rows={7}
                  value={conditionTreeJson}
                  onChange={(e) => setConditionTreeJson(e.target.value)}
                  className="w-full p-2.5 rounded-lg border border-[#D9DEE7] font-mono text-[11px] bg-white text-[#183047] focus:ring-1 focus:ring-[#B4872B]"
                />

                <div className="flex items-center justify-between gap-2 flex-wrap pt-1">
                  <button
                    type="button"
                    onClick={handleValidateAst}
                    disabled={isValidating}
                    className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-[#153F6B] text-white font-bold text-[11px] hover:bg-[#183047] cursor-pointer"
                  >
                    <CheckCircle2 className="w-3 h-3" />
                    <span>{isValidating ? "Validating..." : "Validate AST"}</span>
                  </button>

                  {validationResult && (
                    <div
                      className={`px-2.5 py-1 rounded text-[11px] font-semibold border ${
                        validationResult.is_valid
                          ? "bg-emerald-50 text-emerald-800 border-emerald-300"
                          : "bg-rose-50 text-rose-800 border-rose-300"
                      }`}
                    >
                      {validationResult.is_valid
                        ? "AST Structure Valid!"
                        : `Validation Failed: ${validationResult.errors.join("; ")}`}
                    </div>
                  )}
                </div>
              </div>

              {/* Live Test Against Saved Chart Section */}
              <div className="space-y-2 bg-[#FAF8F2] p-3.5 rounded-lg border border-[#D8BD80]/50">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center gap-1.5 font-bold text-[#8C6D23]">
                    <Play className="w-4 h-4" />
                    <span>Test Against Opened / Saved Horoscope</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <select
                      value={selectedHoroscopeId}
                      onChange={(e) => setSelectedHoroscopeId(e.target.value)}
                      className="p-1 rounded border border-[#D9DEE7] bg-white text-[11px] max-w-xs"
                    >
                      {savedHoroscopes.map((h) => (
                        <option key={h.id} value={h.id}>
                          {h.person_name} ({h.birth_date})
                        </option>
                      ))}
                    </select>
                    <button
                      type="button"
                      onClick={handleTestRun}
                      disabled={isTesting || !selectedHoroscopeId}
                      className="px-3 py-1 rounded bg-[#B4872B] hover:bg-[#8C6D23] text-white font-bold text-[11px] cursor-pointer disabled:opacity-50"
                    >
                      {isTesting ? "Evaluating..." : "Run Test"}
                    </button>
                  </div>
                </div>

                {testResult && (
                  <div className="p-2.5 rounded bg-white border border-[#D9DEE7] text-[11px] space-y-1">
                    {testResult.error ? (
                      <span className="text-rose-600 font-bold">
                        Error: {testResult.error}
                      </span>
                    ) : (
                      <>
                        <div className="flex items-center gap-2">
                          <span className="font-bold">Result:</span>
                          <span
                            className={`font-bold ${
                              testResult.matched ? "text-emerald-600" : "text-gray-500"
                            }`}
                          >
                            {testResult.matched ? "MATCHED (TRUE)" : "NOT MATCHED (FALSE)"}
                          </span>
                        </div>
                        {testResult.chart_evidence?.length > 0 && (
                          <div>
                            <span className="font-bold">Evidence:</span>{" "}
                            {testResult.chart_evidence.join(" | ")}
                          </div>
                        )}
                        {testResult.match_reasons?.length > 0 && (
                          <div>
                            <span className="font-bold">Reasoning:</span>{" "}
                            {testResult.match_reasons.join(" | ")}
                          </div>
                        )}
                      </>
                    )}
                  </div>
                )}
              </div>

              {/* Interpretations EN & TA */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-[#52667E]">Interpretation (English)</label>
                  <textarea
                    rows={3}
                    value={interpretationEn}
                    onChange={(e) => setInterpretationEn(e.target.value)}
                    placeholder="Classical meaning and behavioral indications..."
                    className="w-full p-2 rounded-lg border border-[#D9DEE7] text-xs"
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-[#52667E]">Interpretation (Tamil)</label>
                  <textarea
                    rows={3}
                    value={interpretationTa}
                    onChange={(e) => setInterpretationTa(e.target.value)}
                    placeholder="தமிழில் விளக்கம்..."
                    className="w-full p-2 rounded-lg border border-[#D9DEE7] text-xs"
                  />
                </div>
              </div>

              {/* Astrological Principles EN & TA */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-[#52667E]">Astrological Principle (English)</label>
                  <textarea
                    rows={2}
                    value={principleEn}
                    onChange={(e) => setPrincipleEn(e.target.value)}
                    placeholder="Bhavat Bhava, Sthana-Bala, Drishti rule..."
                    className="w-full p-2 rounded-lg border border-[#D9DEE7] text-xs"
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-[#52667E]">Astrological Principle (Tamil)</label>
                  <textarea
                    rows={2}
                    value={principleTa}
                    onChange={(e) => setPrincipleTa(e.target.value)}
                    placeholder="சாஸ்திர தத்துவம்..."
                    className="w-full p-2 rounded-lg border border-[#D9DEE7] text-xs"
                  />
                </div>
              </div>

              {/* References & Limitations */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-[#52667E]">Classical Source Reference</label>
                  <input
                    type="text"
                    value={sourceReference}
                    onChange={(e) => setSourceReference(e.target.value)}
                    placeholder="e.g. BPHS Ch. 24, Sloka 70"
                    className="w-full p-2 rounded-lg border border-[#D9DEE7] text-xs"
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-[#52667E]">Limitations / Counter-Factors</label>
                  <input
                    type="text"
                    value={limitationsEn}
                    onChange={(e) => setLimitationsEn(e.target.value)}
                    placeholder="e.g. Combust planets or malefic aspects modify outcome"
                    className="w-full p-2 rounded-lg border border-[#D9DEE7] text-xs"
                  />
                </div>
              </div>
            </div>

            {/* Modal Actions */}
            <div className="flex items-center justify-between border-t border-[#F2F3F5] pt-3 flex-wrap gap-2">
              <button
                type="button"
                onClick={() => setIsEditorOpen(false)}
                className="px-4 py-2 rounded-lg border border-[#D9DEE7] text-xs font-semibold text-[#52667E] hover:bg-gray-50"
              >
                Cancel
              </button>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => handleSaveRule(true)}
                  className="px-3.5 py-2 rounded-lg bg-gray-100 border border-[#D9DEE7] text-xs font-semibold text-[#183047] hover:bg-gray-200 cursor-pointer"
                >
                  Save as Draft
                </button>
                <button
                  type="button"
                  onClick={() => handleSaveRule(false)}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-[#B4872B] hover:bg-[#8C6D23] text-white font-bold text-xs shadow-2xs transition-colors cursor-pointer"
                >
                  <Save className="w-3.5 h-3.5" />
                  <span>{editingRuleId ? "Update & Increment Version" : "Save & Publish Rule"}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
