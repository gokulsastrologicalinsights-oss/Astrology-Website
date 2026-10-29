"use client";

import React, { useState, useEffect, useMemo, useCallback } from "react";
import Link from "next/link";
import {
  FullHoroscopeResult,
  PredictionCategoryGroup,
  PredictionSubcategory,
  EvaluatedPredictionRule,
} from "@/lib/types";
import {
  getPredictionCategories,
  evaluatePredictionRules,
  saveRuleDefinition,
} from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import {
  Compass,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Sparkles,
  BookOpen,
  Filter,
  Search,
  RefreshCw,
  Layers,
  ChevronDown,
  ChevronUp,
  Info,
  ShieldAlert,
  ArrowRight,
  SlidersHorizontal,
  Plus,
  X,
  Flame,
  Heart,
  Briefcase,
  Crown,
  Star,
  Coins,
  Baby,
  Smile,
  ShieldCheck,
  Check,
  Trash2,
  Play,
  Plane,
  Scale,
  Clock,
} from "lucide-react";

interface AstrologicalPredictionsSectionProps {
  horoscopeResult: FullHoroscopeResult;
  language: "en" | "ta";
}

// Quick filter categories requested by user & extracted from classical documents
const QUICK_FILTER_PILLS = [
  { id: "all", label_en: "All Topics (230+)", label_ta: "அனைத்தும் (230+)", icon: Sparkles },
  { id: "sexuality_intimacy", label_en: "Sexual Topics & Intimacy", label_ta: "தாம்பத்தியம் & காமம்", icon: Flame, isHighlight: true },
  { id: "longevity_death", label_en: "Longevity & Death", label_ta: "ஆயுள் & மரண அமைப்பு", icon: ShieldAlert, isHighlight: true },
  { id: "event_timing", label_en: "Event Timing (KP)", label_ta: "நிகழ்வு காலக் கணிப்பு (KP)", icon: Clock, isHighlight: true },
  { id: "marriage", label_en: "Marriage (General)", label_ta: "திருமணம்", icon: Heart },
  { id: "marriage_timing", label_en: "Marriage Timing (D1/D9/Jaimini)", label_ta: "திருமண கால நிர்ணயம்", icon: Clock, isHighlight: true },
  { id: "first_marriage", label_en: "1st Marriage", label_ta: "முதல் திருமணம்", icon: Heart },
  { id: "second_marriage", label_en: "2nd Marriage", label_ta: "இரண்டாம் திருமணம்", icon: RefreshCw },
  { id: "job", label_en: "Job & Career", label_ta: "வேலை & உத்தியோகம்", icon: Briefcase },
  { id: "lagna", label_en: "Lagna Characters", label_ta: "லக்ன குணநலன்கள்", icon: Crown },
  { id: "star", label_en: "Star Prediction (28 Nakshatras)", label_ta: "நட்சத்திர பலன்கள் (Star Prediction)", icon: Star, isHighlight: true },
  { id: "wealth_yogas", label_en: "Money & Wealth", label_ta: "தனம் & சொத்து", icon: Coins },
  { id: "children_prospects", label_en: "Children & Family", label_ta: "புத்திர பாக்கியம்", icon: Baby },
  { id: "foreign_travel", label_en: "Foreign Travel", label_ta: "வெளிநாட்டுப் பயணம்", icon: Plane },
  { id: "health_vitality", label_en: "Health & Cure", label_ta: "உடல் நலம் & குணம்", icon: ShieldCheck },
  { id: "planetary_debilitation_aspects", label_en: "Debilitation & Aspect Loss", label_ta: "கிரக நீசம் & பார்வை இழப்பு", icon: Compass, isHighlight: true },
  { id: "legal_disputes", label_en: "Litigation & Legal", label_ta: "வழக்கு & வெற்றி", icon: Scale },
];

const LOCAL_STORAGE_CUSTOM_RULES_KEY = "antigravity_custom_astrology_rules";

// Helper to sanitize Dasa data to avoid payload explosion (>1MB) while preserving full 3-level evaluation precision
function sanitizeDasaForEvaluation(dasa: any) {
  if (!dasa) return undefined;
  return {
    balance: dasa.balance,
    current_period_path: dasa.current_period_path,
    current_periods: dasa.current_periods,
    mahadashas: Array.isArray(dasa.mahadashas)
      ? dasa.mahadashas.slice(0, 12).map((m: any) => ({
          lord: m.lord,
          start_date: m.start_date,
          end_date: m.end_date,
          duration_years: m.duration_years,
          bhuktis: Array.isArray(m.bhuktis)
            ? m.bhuktis.map((b: any) => ({
                lord: b.lord,
                start_date: b.start_date,
                end_date: b.end_date,
                antardashas: Array.isArray(b.antardashas)
                  ? b.antardashas.map((a: any) => ({
                      lord: a.lord,
                      start_date: a.start_date,
                      end_date: a.end_date,
                    }))
                  : undefined,
              }))
            : undefined,
        }))
      : undefined,
  };
}

export function AstrologicalPredictionsSection({
  horoscopeResult,
  language,
}: AstrologicalPredictionsSectionProps) {
  const { session } = useAuth();

  // Categories state
  const [categoryGroups, setCategoryGroups] = useState<PredictionCategoryGroup[]>([]);
  const [isLoadingCategories, setIsLoadingCategories] = useState<boolean>(true);
  const [categoriesError, setCategoriesError] = useState<string | null>(null);

  // Native Gender Detection & Filter State
  const nativeGender: "male" | "female" = useMemo(() => {
    const g =
      (horoscopeResult.clientInputs as any)?.gender ||
      (horoscopeResult.horoscope as any)?.request?.gender ||
      (horoscopeResult as any)?.gender ||
      "male";
    return String(g).toLowerCase() === "female" ? "female" : "male";
  }, [horoscopeResult]);

  const [selectedGenderFilter, setSelectedGenderFilter] = useState<"chart" | "male" | "female" | "all">("chart");

  const activeGender = useMemo(() => {
    if (selectedGenderFilter === "chart") return nativeGender;
    return selectedGenderFilter;
  }, [selectedGenderFilter, nativeGender]);

  // Filter & Selection state
  const [activeCategoryFilter, setActiveCategoryFilter] = useState<string>("sexuality_intimacy");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [chartScope, setChartScope] = useState<"d1" | "d9" | "both">("both");
  const [astrologySystem, setAstrologySystem] = useState<"all" | "vedic" | "kp">("all");
  const [showOnlyMatched, setShowOnlyMatched] = useState<boolean>(true);

  // Evaluation state
  const [isEvaluating, setIsEvaluating] = useState<boolean>(false);
  const [evaluationError, setEvaluationError] = useState<string | null>(null);
  const [evaluationResults, setEvaluationResults] = useState<EvaluatedPredictionRule[] | null>(null);
  const [evaluatedAt, setEvaluatedAt] = useState<string | null>(null);
  const [lastEvaluatedKey, setLastEvaluatedKey] = useState<string | null>(null);

  // Expanded rule card IDs for detailed rationale
  const [expandedRuleIds, setExpandedRuleIds] = useState<Set<string>>(new Set());

  // Custom User-Defined Rules (Stored in localStorage + passed to evaluate)
  const [customRules, setCustomRules] = useState<any[]>(() => {
    if (typeof window !== "undefined") {
      try {
        const stored = localStorage.getItem(LOCAL_STORAGE_CUSTOM_RULES_KEY);
        return stored ? JSON.parse(stored) : [];
      } catch {
        return [];
      }
    }
    return [];
  });

  // Modal State for Manual Condition Builder
  const [isAddRuleModalOpen, setIsAddRuleModalOpen] = useState<boolean>(false);
  const [isManageCustomModalOpen, setIsManageCustomModalOpen] = useState<boolean>(false);
  const [newRuleNameEn, setNewRuleNameEn] = useState<string>("");
  const [newRuleNameTa, setNewRuleNameTa] = useState<string>("");
  const [newRuleCategory, setNewRuleCategory] = useState<string>("sexuality_intimacy");
  const [newRuleSystem, setNewRuleSystem] = useState<"vedic" | "kp" | "combined">("vedic");
  const [newRuleScope, setNewRuleScope] = useState<string>("d1");
  const [newRuleSeverity, setNewRuleSeverity] = useState<string>("favorable");
  const [newLogicalOperator, setNewLogicalOperator] = useState<"NONE" | "AND" | "OR" | "NOT">("NONE");

  // Condition 1 parameters
  const [newConditionType, setNewConditionType] = useState<string>("planet_conjunction");
  const [condPlanet1, setCondPlanet1] = useState<string>("Venus");
  const [condPlanet2, setCondPlanet2] = useState<string>("Rahu");
  const [condHouse, setCondHouse] = useState<number>(7);
  const [condPlacedInHouse, setCondPlacedInHouse] = useState<number>(7);
  const [condSign, setCondSign] = useState<number>(1);
  const [condNakshatra, setCondNakshatra] = useState<string>("Rohini");
  const [condMaxOrb, setCondMaxOrb] = useState<number>(8.0);
  const [condDasaLevel, setCondDasaLevel] = useState<string>("mahadasha");
  const [condDasaLord, setCondDasaLord] = useState<string>("Jupiter");
  const [condCusp, setCondCusp] = useState<number>(7);
  const [condSubLord, setCondSubLord] = useState<string>("Venus");
  const [condHouse2, setCondHouse2] = useState<number>(11);

  // Condition 2 parameters (for AND / OR compound conditions)
  const [cond2Type, setCond2Type] = useState<string>("planet_house");
  const [cond2Planet1, setCond2Planet1] = useState<string>("Mars");
  const [cond2Planet2, setCond2Planet2] = useState<string>("Saturn");
  const [cond2House, setCond2House] = useState<number>(7);
  const [cond2PlacedInHouse, setCond2PlacedInHouse] = useState<number>(10);
  const [cond2Sign, setCond2Sign] = useState<number>(1);
  const [cond2Nakshatra, setCond2Nakshatra] = useState<string>("Ashwini");
  const [cond2MaxOrb, setCond2MaxOrb] = useState<number>(8.0);
  const [cond2DasaLevel, setCond2DasaLevel] = useState<string>("bhukti");
  const [cond2DasaLord, setCond2DasaLord] = useState<string>("Venus");
  const [cond2Cusp, setCond2Cusp] = useState<number>(7);
  const [cond2SubLord, setCond2SubLord] = useState<string>("Mars");
  const [cond2House2, setCond2House2] = useState<number>(11);

  // Descriptions & Reasons
  const [newInterpretationEn, setNewInterpretationEn] = useState<string>("");
  const [newInterpretationTa, setNewInterpretationTa] = useState<string>("");
  const [newPrincipleEn, setNewPrincipleEn] = useState<string>("");
  const [newPrincipleTa, setNewPrincipleTa] = useState<string>("");
  const [newSourceRef, setNewSourceRef] = useState<string>("Classical Traditional Jyotish");

  // Test inside modal state
  const [isTestingNewRule, setIsTestingNewRule] = useState<boolean>(false);
  const [testResultFeedback, setTestResultFeedback] = useState<{ matched: boolean; message: string } | null>(null);

  // Generate unique chart signature for cache/re-evaluation detection
  const chartIdentityKey = useMemo(() => {
    const hid = horoscopeResult.savedId || "adhoc";
    const dt = horoscopeResult.clientInputs?.birthDate || horoscopeResult.horoscope?.metadata?.birth_utc_iso || "";
    const tm = horoscopeResult.clientInputs?.birthTime || "";
    const aya = horoscopeResult.horoscope?.metadata?.ayanamsa_id ?? 0;
    return `${hid}-${dt}-${tm}-aya${aya}-${customRules.length}`;
  }, [horoscopeResult, customRules.length]);

  // Load category library on mount
  useEffect(() => {
    let isMounted = true;
    async function loadCategories() {
      setIsLoadingCategories(true);
      setCategoriesError(null);
      try {
        const groups = await getPredictionCategories();
        if (isMounted) {
          setCategoryGroups(groups);
        }
      } catch (err: unknown) {
        if (isMounted) {
          const msg = err instanceof Error ? err.message : String(err);
          setCategoriesError(msg);
        }
      } finally {
        if (isMounted) setIsLoadingCategories(false);
      }
    }
    loadCategories();
    return () => {
      isMounted = false;
    };
  }, []);

  // Evaluator execution
  const executeEvaluation = useCallback(
    async (categorySlugToQuery: string) => {
      setIsEvaluating(true);
      setEvaluationError(null);

      try {
        const payload = {
          horoscope: horoscopeResult.horoscope,
          saved_horoscope_id: horoscopeResult.savedId,
          category_slug: categorySlugToQuery === "all" ? undefined : categorySlugToQuery,
          chart_scope: chartScope,
          astrology_system: astrologySystem,
          language: language,
          gender: activeGender === "all" ? "all" : activeGender,
          dasa: sanitizeDasaForEvaluation(horoscopeResult.dasa),
          kp: horoscopeResult.kp as any,
          custom_rules:
            customRules.length > 0
              ? customRules.filter((r) => r.is_enabled !== false)
              : undefined,
        };

        const resp = await evaluatePredictionRules(payload);
        setEvaluationResults(resp.results);
        setEvaluatedAt(new Date().toLocaleTimeString());
        setLastEvaluatedKey(`${chartIdentityKey}-${categorySlugToQuery}`);

        // Auto-expand matched rules
        const matchedIds = new Set<string>();
        resp.results.forEach((r) => {
          if (r.matched) matchedIds.add(r.rule_id);
        });
        setExpandedRuleIds(matchedIds);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        setEvaluationError(msg);
      } finally {
        setIsEvaluating(false);
      }
    },
    [
      horoscopeResult,
      chartScope,
      astrologySystem,
      language,
      chartIdentityKey,
      customRules,
      activeGender,
    ]
  );

  // Auto-run evaluation on mount or when chart or active filter changes
  useEffect(() => {
    executeEvaluation(activeCategoryFilter);
  }, [activeCategoryFilter, chartScope, astrologySystem, chartIdentityKey, activeGender, executeEvaluation]);

  // Toggle card expansion
  const toggleExpand = (ruleId: string) => {
    setExpandedRuleIds((prev) => {
      const next = new Set(prev);
      if (next.has(ruleId)) {
        next.delete(ruleId);
      } else {
        next.add(ruleId);
      }
      return next;
    });
  };

  // Filtered displayed rules with search
  const displayedRules = useMemo(() => {
    if (!evaluationResults) return [];
    let list = evaluationResults;

    if (showOnlyMatched) {
      list = list.filter((r) => r.matched);
    }

    // Strict gender filtering
    if (activeGender === "male") {
      list = list.filter((r) => r.applicable_gender !== "female");
    } else if (activeGender === "female") {
      list = list.filter((r) => r.applicable_gender !== "male");
    }

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      list = list.filter(
        (r) =>
          r.name_en?.toLowerCase().includes(q) ||
          r.name_ta?.toLowerCase().includes(q) ||
          r.interpretation_en?.toLowerCase().includes(q) ||
          r.interpretation_ta?.toLowerCase().includes(q) ||
          r.astrological_principle_en?.toLowerCase().includes(q) ||
          r.astrological_principle_ta?.toLowerCase().includes(q) ||
          r.rule_id?.toLowerCase().includes(q) ||
          r.chart_evidence.some((ev) => ev.toLowerCase().includes(q))
      );
    }

    return list;
  }, [evaluationResults, showOnlyMatched, searchQuery, activeGender]);

  const matchedCount = useMemo(() => {
    return evaluationResults ? evaluationResults.filter((r) => r.matched).length : 0;
  }, [evaluationResults]);

  // Helper to build leaf condition node
  const buildLeafNode = (
    type: string,
    p1: string,
    p2: string,
    h1: number,
    h2: number,
    sign: number,
    nak: string,
    orb: number,
    scope: string,
    dasaLvl: string,
    dasaLrd: string,
    cusp: number,
    subLrd: string
  ) => {
    switch (type) {
      case "planet_conjunction":
        return {
          condition_type: "planet_conjunction",
          planets: [p1, p2],
          same_sign_only: true,
          orb_degrees: Number(orb) || 8.0,
          chart: scope,
        };
      case "planet_house":
        return {
          condition_type: "planet_house",
          planet: p1,
          house: Number(h1),
          chart: scope,
        };
      case "planet_sign":
        return {
          condition_type: "planet_sign",
          planet: p1,
          sign: Number(sign),
          chart: scope,
        };
      case "house_lord_placement":
        return {
          condition_type: "house_lord_placement",
          house: Number(h1),
          placed_in_house: Number(h2),
          chart: scope,
        };
      case "planet_aspect":
        return {
          condition_type: "planet_aspect",
          aspecting_planet: p1,
          target_type: "house",
          target_value: Number(h1),
          chart: scope,
        };
      case "planet_nakshatra":
        return {
          condition_type: "planet_nakshatra",
          planet: p1,
          nakshatra: nak,
          chart: scope,
        };
      case "lagna_sign":
        return {
          condition_type: "lagna_sign",
          sign: Number(sign),
          chart: scope,
        };
      case "dasa_active":
        return {
          condition_type: "dasa_active",
          level: dasaLvl,
          lord: dasaLrd,
        };
      case "kp_sub_lord":
        return {
          condition_type: "kp_sub_lord",
          cusp: Number(cusp),
          sub_lord: subLrd,
        };
      case "kp_significator":
        return {
          condition_type: "kp_significator",
          planet: p1,
          house: Number(h1),
        };
      case "mutual_exchange":
        return {
          condition_type: "mutual_exchange",
          house1: Number(h1),
          house2: Number(h2),
          chart: scope,
        };
      default:
        return {
          condition_type: "planet_house",
          planet: p1,
          house: Number(h1),
          chart: scope,
        };
    }
  };

  // Build declarative Condition Tree with logical operators (AND, OR, NOT)
  const buildCurrentConditionTree = () => {
    const cond1 = buildLeafNode(
      newConditionType,
      condPlanet1,
      condPlanet2,
      condHouse,
      condPlacedInHouse,
      condSign,
      condNakshatra,
      condMaxOrb,
      newRuleScope,
      condDasaLevel,
      condDasaLord,
      condCusp,
      condSubLord
    );

    if (newLogicalOperator === "NONE") {
      return cond1;
    }

    if (newLogicalOperator === "NOT") {
      return {
        condition_type: "compound",
        operator: "NOT",
        conditions: [cond1],
      };
    }

    const cond2 = buildLeafNode(
      cond2Type,
      cond2Planet1,
      cond2Planet2,
      cond2House,
      cond2PlacedInHouse,
      cond2Sign,
      cond2Nakshatra,
      cond2MaxOrb,
      newRuleScope,
      cond2DasaLevel,
      cond2DasaLord,
      cond2Cusp,
      cond2SubLord
    );

    return {
      condition_type: "compound",
      operator: newLogicalOperator,
      conditions: [cond1, cond2],
    };
  };

  // Test proposed new condition against the currently open chart inside modal
  const handleTestProposedCondition = async () => {
    setIsTestingNewRule(true);
    setTestResultFeedback(null);
    try {
      const tempRule = {
        rule_id: `CUSTOM-TEST-${Date.now()}`,
        version: 1,
        name_en: newRuleNameEn || "Custom Proposed Rule",
        name_ta: newRuleNameTa || "முன்மொழியப்பட்ட தனிப்பயன் விதி",
        category_slug: newRuleCategory,
        subcategory: newRuleCategory,
        astrology_system: newRuleSystem,
        chart_scope: newRuleScope,
        calculation_mode: "thirukanitha",
        condition_tree: buildCurrentConditionTree(),
        interpretation_en: newInterpretationEn || "Evaluation of custom astrological condition.",
        interpretation_ta: newInterpretationTa || "தனிப்பயன் ஜோதிட விதியின் ஆய்வு.",
        astrological_principle_en: newPrincipleEn || "Custom astrological principle.",
        astrological_principle_ta: newPrincipleTa || "தனிப்பயன் ஜோதிட விதி விளக்கம்.",
        source_reference: newSourceRef,
        severity: newRuleSeverity,
        is_enabled: true,
      };

      const testPayload = {
        horoscope: horoscopeResult.horoscope,
        saved_horoscope_id: horoscopeResult.savedId,
        custom_rules: [tempRule],
        category_slug: newRuleCategory,
        chart_scope: newRuleScope,
        language: language,
      };

      const resp = await evaluatePredictionRules(testPayload);
      const testMatch = resp.results.find((r) => r.rule_id === tempRule.rule_id);

      if (testMatch && testMatch.matched) {
        setTestResultFeedback({
          matched: true,
          message:
            language === "ta"
              ? `பொருந்தியது! இந்த ஜாதகத்தில் சான்றுகள் காணப்படுகின்றன: ${testMatch.chart_evidence.join(", ")}`
              : `MATCHED! Chart evidence found: ${testMatch.chart_evidence.join("; ")}`,
        });
      } else {
        setTestResultFeedback({
          matched: false,
          message:
            language === "ta"
              ? "இந்த திறக்கப்பட்ட ஜாதகத்தில் இந்த விதி பொருந்தவில்லை (காரணம்: நிபந்தனைகள் பூர்த்தியாகவில்லை)."
              : "Does NOT match this open chart (conditions not met by active planetary coordinates).",
        });
      }
    } catch (err: any) {
      setTestResultFeedback({
        matched: false,
        message: `Test evaluation error: ${err?.message || String(err)}`,
      });
    } finally {
      setIsTestingNewRule(false);
    }
  };

  // Save new custom condition
  const handleSaveCustomCondition = async () => {
    if (!newRuleNameEn.trim()) {
      alert("Please enter a rule name in English.");
      return;
    }

    const uniqueId = `CUSTOM-${Date.now().toString(36).toUpperCase()}`;
    const newRuleDef = {
      rule_id: uniqueId,
      version: 1,
      name_en: newRuleNameEn.trim(),
      name_ta: newRuleNameTa.trim() || newRuleNameEn.trim(),
      category_slug: newRuleCategory,
      subcategory: newRuleCategory,
      astrology_system: newRuleSystem,
      chart_scope: newRuleScope,
      calculation_mode: "thirukanitha",
      condition_tree: buildCurrentConditionTree(),
      interpretation_en: newInterpretationEn.trim() || `${newRuleNameEn.trim()} manifests significant astrological influence in the horoscope.`,
      interpretation_ta: newInterpretationTa.trim() || `${newRuleNameTa.trim() || newRuleNameEn.trim()} ஜாதகத்தில் குறிப்பிடத்தக்க பலனை ஏற்படுத்துகிறது.`,
      astrological_principle_en: newPrincipleEn.trim() || "Classical principle linking planetary dignity, house rulership, and astrological aspects.",
      astrological_principle_ta: newPrincipleTa.trim() || "பாரம்பரிய ஜோதிட விதிமுறைகளின்படி கிரக சேர்க்கை மற்றும் பாவக பலன்களின் தொடர்பு.",
      source_reference: newSourceRef.trim() || "User-Defined Astrological Canon",
      severity: newRuleSeverity,
      is_enabled: true,
    };

    const updated = [...customRules, newRuleDef];
    setCustomRules(updated);
    if (typeof window !== "undefined") {
      try {
        localStorage.setItem(LOCAL_STORAGE_CUSTOM_RULES_KEY, JSON.stringify(updated));
      } catch (e) {
        console.error("Failed to save custom rule to localStorage", e);
      }
    }

    // Attempt server sync if session token exists
    if (session?.access_token) {
      try {
        await saveRuleDefinition(newRuleDef, session.access_token);
      } catch {
        // LocalStorage copy suffices
      }
    }

    setIsAddRuleModalOpen(false);
    // Reset form
    setNewRuleNameEn("");
    setNewRuleNameTa("");
    setNewInterpretationEn("");
    setNewInterpretationTa("");
    setNewPrincipleEn("");
    setNewPrincipleTa("");
    setTestResultFeedback(null);

    // Switch to category and re-evaluate
    setActiveCategoryFilter(newRuleCategory);
  };

  // Toggle custom condition active state
  const handleToggleCustomRule = (ruleId: string) => {
    const updated = customRules.map((r) =>
      r.rule_id === ruleId ? { ...r, is_enabled: r.is_enabled === false ? true : false } : r
    );
    setCustomRules(updated);
    if (typeof window !== "undefined") {
      try {
        localStorage.setItem(LOCAL_STORAGE_CUSTOM_RULES_KEY, JSON.stringify(updated));
      } catch {}
    }
  };

  // Delete custom condition
  const handleDeleteCustomRule = (ruleId: string) => {
    const updated = customRules.filter((r) => r.rule_id !== ruleId);
    setCustomRules(updated);
    if (typeof window !== "undefined") {
      try {
        localStorage.setItem(LOCAL_STORAGE_CUSTOM_RULES_KEY, JSON.stringify(updated));
      } catch {}
    }
  };

  const planetOptions = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
  const nakshatraOptions = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
  ];
  const rashiOptions = [
    { num: 1, name: "Mesha (Aries)" },
    { num: 2, name: "Vrishabha (Taurus)" },
    { num: 3, name: "Mithuna (Gemini)" },
    { num: 4, name: "Kataka (Cancer)" },
    { num: 5, name: "Simha (Leo)" },
    { num: 6, name: "Kanya (Virgo)" },
    { num: 7, name: "Thula (Libra)" },
    { num: 8, name: "Vrishchika (Scorpio)" },
    { num: 9, name: "Dhanus (Sagittarius)" },
    { num: 10, name: "Makara (Capricorn)" },
    { num: 11, name: "Kumbha (Aquarius)" },
    { num: 12, name: "Meena (Pisces)" },
  ];
  const dasaLevelOptions = [
    { id: "mahadasha", label: "Mahadasha (மகா தசை)" },
    { id: "bhukti", label: "Bhukti / Antardasha (புக்தி)" },
    { id: "antar", label: "Anthara (அந்தரம்)" },
    { id: "any", label: "Any Active Level (ஏதேனும் ஒன்று)" },
  ];

  return (
    <section className="bg-white rounded-xl border border-[#D9DEE7] p-4 sm:p-6 shadow-2xs space-y-6">
      {/* 1. Header with Badge & Add Condition Button */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#F2F3F5] pb-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2 flex-wrap">
            <div className="w-8 h-8 rounded-lg bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center text-[#B4872B] shrink-0">
              <Compass className="w-4 h-4" />
            </div>
            <h3 className="font-serif text-base sm:text-lg font-bold text-[#183047]">
              {language === "ta"
                ? "ஜோதிட விதிகள் மற்றும் பலன்கள் (கணிப்பு இயந்திரம்)"
                : "Astrological Conditions & Prediction Engine"}
            </h3>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
              70+ {language === "ta" ? "விதிகள்" : "Classical Rules"}
            </span>
          </div>
          <p className="text-xs text-[#52667E] max-w-3xl">
            {language === "ta"
              ? "சுக்கிரன்+ராகு, செவ்வாய் சேர்க்கை, லக்ன குணங்கள், நட்சத்திர பலன்கள், உத்தியோகம் மற்றும் திருமண விதிகள் போன்ற 70+ பாரம்பரிய விதிகளின்படி இந்த ஜாதகத்தை தானாக ஆராய்ந்து சான்றுகளுடன் பலன்களைப் பெறும் பகுதி."
              : "Deterministic evaluation of active chart against 70+ classical rules across Marriage, 1st/2nd Marriage, Sexuality, Career, Lagna, and Stars with full textual evidence and reasons."}
          </p>
        </div>

        {/* Action Controls: Refresh & Manual Add Button */}
        <div className="flex items-center gap-2 self-start md:self-center flex-wrap">
          <button
            type="button"
            onClick={() => executeEvaluation(activeCategoryFilter)}
            disabled={isEvaluating}
            title={language === "ta" ? "மறுபரிசீலனை செய்" : "Re-evaluate"}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-[#F2F3F5] hover:bg-[#E2E8F0] border border-[#D9DEE7] text-xs font-semibold text-[#153F6B] transition-colors cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isEvaluating ? "animate-spin" : ""}`} />
            <span className="hidden sm:inline">
              {language === "ta" ? "புதுப்பி" : "Refresh"}
            </span>
          </button>

          <button
            type="button"
            onClick={() => setIsAddRuleModalOpen(true)}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-[#B4872B] hover:bg-[#8C6D23] text-white font-bold text-xs shadow-2xs transition-colors cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>{language === "ta" ? "புதிய விதியைச் சேர்" : "+ Add Condition"}</span>
          </button>
        </div>
      </div>

      {/* 2. Top-Level Filter Pills (Direct One-Click Category Filter) */}
      <div className="space-y-3 bg-[#F8FAFC] rounded-xl p-3.5 sm:p-4 border border-[#E2E8F0]">
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-1.5 text-xs font-bold text-[#183047]">
            <Filter className="w-3.5 h-3.5 text-[#B4872B]" />
            <span>{language === "ta" ? "வடிகட்டும் தலைப்புகள் (தேர்வு செய்க):" : "Filter Categories (Click to Evaluate):"}</span>
          </div>
          {customRules.length > 0 && (
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-semibold text-[#8C6D23] bg-[#FAF2DE] px-2 py-0.5 rounded-full border border-[#D8BD80]">
                {customRules.filter((r) => r.is_enabled !== false).length} / {customRules.length}{" "}
                {language === "ta" ? "தனிப்பயன் விதிகள் பயன்பாட்டில் உள்ளன" : "custom conditions active"}
              </span>
              <button
                type="button"
                onClick={() => setIsManageCustomModalOpen(true)}
                className="text-[11px] font-bold text-[#153F6B] hover:text-[#0E2845] underline cursor-pointer"
              >
                {language === "ta" ? "விதிகள் மேலாண்மை" : "Manage Rules"}
              </button>
            </div>
          )}
        </div>

        {/* Quick Filter Pill Buttons */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-thin">
          {QUICK_FILTER_PILLS.map((pill) => {
            const isSelected = activeCategoryFilter === pill.id;
            const Icon = pill.icon;
            return (
              <button
                key={pill.id}
                type="button"
                onClick={() => setActiveCategoryFilter(pill.id)}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap transition-all cursor-pointer border ${
                  isSelected
                    ? pill.isHighlight
                      ? "bg-rose-700 text-white border-rose-800 shadow-sm"
                      : "bg-[#153F6B] text-white border-[#153F6B] shadow-sm"
                    : pill.isHighlight
                    ? "bg-rose-50 text-rose-800 border-rose-200 hover:bg-rose-100"
                    : "bg-white text-[#52667E] border-[#D9DEE7] hover:bg-[#F2F3F5] hover:text-[#183047]"
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isSelected ? "text-white" : pill.isHighlight ? "text-rose-600" : "text-[#B4872B]"}`} />
                <span>{language === "ta" ? pill.label_ta : pill.label_en}</span>
              </button>
            );
          })}
        </div>

        {/* Secondary Row: More Specific Categories Dropdown, Search, and Options */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2 border-t border-[#E2E8F0] items-center">
          {/* Detailed Subcategory Selector Dropdown */}
          <div className="space-y-1">
            <label className="text-[10px] font-bold text-[#8190A6] uppercase tracking-wider block">
              {language === "ta" ? "கூடுதல் தலைப்புகள் (67+ பிரிவுகள்):" : "More Classical Topics (67+):"}
            </label>
            <select
              value={activeCategoryFilter}
              onChange={(e) => setActiveCategoryFilter(e.target.value)}
              className="w-full text-xs rounded-lg border border-[#D9DEE7] bg-white p-2 text-[#183047] font-semibold focus:ring-1 focus:ring-[#B4872B] focus:border-[#B4872B]"
            >
              <option value="all">
                {language === "ta" ? "🌟 அனைத்து பிரிவுகள் (All 70+ Rules)" : "🌟 All Categories (All 70+ Rules)"}
              </option>
              {categoryGroups.map((group) => (
                <optgroup
                  key={group.group_code}
                  label={language === "ta" ? group.group_name_ta : group.group_name_en}
                >
                  {group.subcategories.map((sub) => (
                    <option key={sub.slug} value={sub.slug}>
                      {language === "ta" ? sub.name_ta : sub.name_en}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
          </div>

          {/* Keyword Search */}
          <div className="space-y-1">
            <label className="text-[10px] font-bold text-[#8190A6] uppercase tracking-wider block">
              {language === "ta" ? "விதிகள் அல்லது கிரகங்களை தேடு:" : "Search Conditions / Planets:"}
            </label>
            <div className="relative">
              <input
                type="text"
                placeholder={
                  language === "ta"
                    ? "சுக்கிரன், ராகு, செவ்வாய், திருமணம்..."
                    : "Search Venus, Rahu, Mars, 7th lord..."
                }
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg border border-[#D9DEE7] bg-white text-[#183047] placeholder-[#8190A6] focus:ring-1 focus:ring-[#B4872B] focus:border-[#B4872B]"
              />
              <Search className="w-3.5 h-3.5 text-[#8190A6] absolute left-2.5 top-2.5" />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery("")}
                  className="absolute right-2.5 top-2 text-[10px] text-[#8190A6] hover:text-[#183047]"
                >
                  Clear
                </button>
              )}
            </div>
          </div>

          {/* Scope & Matched Only Checkbox */}
          <div className="flex items-center justify-between gap-2 pt-2 md:pt-4">
            <div className="inline-flex rounded-lg bg-white border border-[#D9DEE7] p-0.5">
              {(["both", "d1", "d9"] as const).map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => setChartScope(s)}
                  className={`px-2 py-1 rounded text-[11px] font-bold uppercase transition-colors ${
                    chartScope === s
                      ? "bg-[#FAF2DE] text-[#8C6D23]"
                      : "text-[#52667E] hover:text-[#183047]"
                  }`}
                >
                  {s === "both" ? "D1+D9" : s}
                </button>
              ))}
            </div>

            <label className="inline-flex items-center gap-1.5 text-xs text-[#183047] cursor-pointer">
              <input
                type="checkbox"
                checked={showOnlyMatched}
                onChange={(e) => setShowOnlyMatched(e.target.checked)}
                className="rounded border-[#D9DEE7] text-[#B4872B] focus:ring-[#B4872B]"
              />
              <span className="font-bold text-[11px]">
                {language === "ta" ? "பொருந்தியவை மட்டும்" : "Matched only"}
              </span>
            </label>
          </div>
        </div>
      </div>

      {/* 3. Evaluation Status, Counts & Error Banner */}
      {evaluationError && (
        <div className="p-3.5 rounded-lg border border-rose-300 bg-rose-50 flex items-start gap-3 text-xs text-rose-800">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold">Evaluation Error</span>
            <p>{evaluationError}</p>
          </div>
        </div>
      )}

      {evaluationResults && !isEvaluating && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-3 rounded-lg bg-[#FAF8F2] border border-[#D8BD80]/50 text-xs text-[#8C6D23]">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="font-bold text-sm text-[#183047]">
              {matchedCount} {language === "ta" ? "ஜோதிட விதிகள் இந்த ஜாதகத்தில் பொருந்தியுள்ளன" : "Conditions Matched in This Horoscope"}
            </span>
            <span className="text-[#8190A6]">
              ({evaluationResults.length} {language === "ta" ? "விதிகள் சோதிக்கப்பட்டன" : "evaluated"})
            </span>
          </div>
          {evaluatedAt && (
            <span className="text-[#8190A6] text-[11px] font-mono">
              {language === "ta" ? "கணிக்கப்பட்ட நேரம்:" : "Evaluated at:"} {evaluatedAt}
            </span>
          )}
        </div>
      )}

      {/* Sexuality & Intimacy Dedicated Gender Filter Banner */}
      {activeCategoryFilter === "sexuality_intimacy" && (
        <div className="p-3.5 sm:p-4 rounded-xl bg-gradient-to-r from-rose-50 via-amber-50 to-orange-50 border border-rose-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs shadow-2xs">
          <div className="flex items-start sm:items-center gap-2.5">
            <span className="p-2 rounded-lg bg-[#881337] text-white shrink-0 shadow-xs">
              <Flame className="w-4 h-4" />
            </span>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h4 className="font-bold text-[#881337] text-sm">
                  {language === "ta" ? "தாம்பத்தியம் & காமம் - பாலின அடிப்படையிலான ஜோதிட விதிகள்" : "Sexuality & Intimacy - Classical Gender-Filtered Rules"}
                </h4>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                  nativeGender === "female"
                    ? "bg-rose-100 text-rose-800 border-rose-300"
                    : "bg-blue-100 text-blue-800 border-blue-300"
                }`}>
                  {nativeGender === "female"
                    ? (language === "ta" ? "👩 ஜாதகர்: பெண் (Stri Jataka)" : "👩 Native: Female (Stri Jataka)")
                    : (language === "ta" ? "👨 ஜாதகர்: ஆண் (Purusha)" : "👨 Native: Male (Purusha)")}
                </span>
              </div>
              <p className="text-slate-600 text-xs mt-0.5">
                {language === "ta"
                  ? `இந்த ஜாதகரின் பாலினத்திற்குரிய (${nativeGender === "female" ? "பெண் / ஸ்திரீ" : "ஆண்"}) விதிகள் மட்டுமே துல்லியமாக சோதிக்கப்பட்டு காட்டப்படுகின்றன. எதிர் பாலின விதிகள் விலக்கப்பட்டுள்ளன.`
                  : `Rules are strictly matched for this native's gender (${nativeGender === "female" ? "Female / Stri Jataka" : "Male / Purusha"}). Opposite gender rules are excluded.`}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-1.5 self-end sm:self-auto shrink-0">
            <span className="text-[11px] font-bold text-slate-700">
              {language === "ta" ? "வடிகட்டி:" : "Filter:"}
            </span>
            <div className="inline-flex rounded-lg bg-white border border-[#D9DEE7] p-0.5 shadow-2xs">
              <button
                type="button"
                onClick={() => setSelectedGenderFilter("chart")}
                className={`px-2.5 py-1 rounded text-xs font-bold transition-all cursor-pointer ${
                  selectedGenderFilter === "chart"
                    ? (nativeGender === "female" ? "bg-rose-600 text-white" : "bg-[#102A4C] text-white")
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                {nativeGender === "female" ? "👩 பெண் (Chart)" : "👨 ஆண் (Chart)"}
              </button>
              <button
                type="button"
                onClick={() => setSelectedGenderFilter("male")}
                className={`px-2 py-1 rounded text-xs font-bold transition-all cursor-pointer ${
                  selectedGenderFilter === "male"
                    ? "bg-blue-600 text-white"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                👨 {language === "ta" ? "ஆண்" : "Male"}
              </button>
              <button
                type="button"
                onClick={() => setSelectedGenderFilter("female")}
                className={`px-2 py-1 rounded text-xs font-bold transition-all cursor-pointer ${
                  selectedGenderFilter === "female"
                    ? "bg-rose-600 text-white"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                👩 {language === "ta" ? "பெண்" : "Female"}
              </button>
              <button
                type="button"
                onClick={() => setSelectedGenderFilter("all")}
                className={`px-2 py-1 rounded text-xs font-bold transition-all cursor-pointer ${
                  selectedGenderFilter === "all"
                    ? "bg-slate-700 text-white"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                👥 {language === "ta" ? "அனைத்தும்" : "All"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Star Prediction Dedicated Banner */}
      {activeCategoryFilter === "star" && (
        <div className="p-4 rounded-xl bg-gradient-to-r from-blue-50 via-indigo-50 to-amber-50 border border-blue-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div className="flex items-start gap-2.5">
            <span className="p-2 rounded-lg bg-[#153F6B] text-[#F3E5AB] shrink-0">
              <Star className="w-4 h-4" />
            </span>
            <div>
              <h4 className="font-bold text-[#0F2942] text-sm">
                {language === "ta" ? "28 நட்சத்திர சாஸ்திர பலன்கள் (The Real Secrets of Vedic Astrology)" : "28 Nakshatras - Star Prediction & Shastra Secrets"}
              </h4>
              <p className="text-slate-600 mt-0.5 leading-relaxed">
                {language === "ta"
                  ? "சந்திரன் நின்ற நட்சத்திரம், லக்ன நட்சத்திரம், 4 பாத நயங்கள், குடும்ப தோஷங்கள் மற்றும் பரிகாரங்கள் உள்ளிட்ட 120+ சாஸ்திர விதிகள் இந்த ஜாதகத்தில் துல்லியமாக சோதிக்கப்படுகின்றன."
                  : "Deterministic evaluation of Moon Star, Ascendant Star, Pada nuances, family doshas, and classical remedies across all 28 Nakshatras."}
              </p>
            </div>
          </div>
          <Link
            href="/tools/nakshatras"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-[#153F6B] text-white font-bold whitespace-nowrap shadow-xs hover:bg-[#103052] transition-colors shrink-0"
          >
            <span>{language === "ta" ? "28 நட்சத்திர கருவிக்குச் செல்க" : "Open 28 Nakshatras Portal"}</span>
            <ArrowRight className="w-3.5 h-3.5 text-[#F3E5AB]" />
          </Link>
        </div>
      )}

      {/* 4. Results Display List / Empty States */}
      {isEvaluating ? (
        <div className="py-12 flex flex-col items-center justify-center space-y-3 text-center">
          <RefreshCw className="w-7 h-7 text-[#B4872B] animate-spin" />
          <p className="text-xs font-semibold text-[#183047]">
            {language === "ta"
              ? "ஜாதக அமைப்புகள், ராசி மற்றும் நவாம்ச நிலைகள் சோதிக்கப்படுகின்றன..."
              : "Evaluating astrological conditions against chart evidence..."}
          </p>
        </div>
      ) : displayedRules.length === 0 ? (
        <div className="py-10 text-center space-y-2 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0] p-6">
          <Info className="w-6 h-6 text-[#8190A6] mx-auto" />
          <h4 className="font-bold text-xs sm:text-sm text-[#183047]">
            {language === "ta"
              ? "இந்த பிரிவில் விதிகள் பொருந்தவில்லை"
              : "No Rules Matched for This Selection"}
          </h4>
          <p className="text-xs text-[#8190A6] max-w-md mx-auto">
            {language === "ta"
              ? "தற்போதைய ஜாதக அமைப்புகளுக்கு இந்த குறிப்பிட்ட நிபந்தனைகள் பூர்த்தியாகவில்லை."
              : "The planetary configurations in this horoscope do not meet the classical criteria for the selected category."}
          </p>
          {showOnlyMatched && evaluationResults && evaluationResults.length > 0 && (
            <button
              type="button"
              onClick={() => setShowOnlyMatched(false)}
              className="text-xs font-bold text-[#153F6B] hover:underline cursor-pointer pt-2"
            >
              {language === "ta"
                ? "பொருந்தாத விதிகளையும் காரணங்களுடன் காண்க"
                : "Show non-matching rules to review reasons"}
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {displayedRules.map((rule) => {
            const isExpanded = expandedRuleIds.has(rule.rule_id);
            const isCustom = rule.rule_id.startsWith("CUSTOM-");
            const severityColor =
              rule.severity === "favorable"
                ? "bg-emerald-50 text-emerald-800 border-emerald-300"
                : rule.severity === "unfavorable"
                ? "bg-rose-50 text-rose-800 border-rose-300"
                : rule.severity === "mixed"
                ? "bg-purple-50 text-purple-800 border-purple-300"
                : "bg-blue-50 text-blue-800 border-blue-300";

            return (
              <div
                key={rule.rule_id}
                className={`rounded-xl border transition-all ${
                  rule.matched
                    ? "bg-white border-[#D9DEE7] shadow-sm hover:border-[#B4872B]"
                    : "bg-[#F8FAFC] border-[#E2E8F0] opacity-80"
                }`}
              >
                {/* Rule Card Header */}
                <div
                  onClick={() => toggleExpand(rule.rule_id)}
                  className="p-3.5 sm:p-4 flex items-start justify-between gap-3 cursor-pointer select-none"
                >
                  <div className="space-y-2 flex-1">
                    {/* Badges Row */}
                    <div className="flex items-center gap-2 flex-wrap text-[10px]">
                      {rule.matched ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold border border-emerald-300 shadow-2xs">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                          <span>{language === "ta" ? "✓ பொருந்திய விதி" : "✓ Matched Condition"}</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-gray-100 text-gray-700 font-medium">
                          <span>{language === "ta" ? "பொருந்தவில்லை" : "Not Matched"}</span>
                        </span>
                      )}

                      <span className="font-mono font-bold text-[#8190A6]">
                        {rule.rule_id}
                      </span>

                      {isCustom && (
                        <span className="px-2 py-0.5 rounded font-bold bg-[#FAF2DE] text-[#8C6D23] border border-[#D8BD80]">
                          {language === "ta" ? "தனிப்பயன் விதி" : "Custom Added"}
                        </span>
                      )}

                      <span className="px-2 py-0.5 rounded font-semibold bg-[#F2F3F5] text-[#153F6B] border border-[#D9DEE7]">
                        {rule.astrology_system.toUpperCase()}
                      </span>
                      <span className="px-2 py-0.5 rounded font-semibold bg-[#F2F3F5] text-[#52667E] border border-[#D9DEE7] uppercase">
                        {rule.chart_scope}
                      </span>
                      <span className={`px-2 py-0.5 rounded font-bold border ${severityColor}`}>
                        {rule.severity.toUpperCase()}
                      </span>

                      {/* Rule Gender Badge */}
                      {rule.applicable_gender && rule.applicable_gender !== "both" ? (
                        <span
                          className={`px-2 py-0.5 rounded font-bold border ${
                            rule.applicable_gender === "female"
                              ? "bg-rose-50 text-rose-800 border-rose-300"
                              : "bg-blue-50 text-blue-800 border-blue-300"
                          }`}
                        >
                          {rule.applicable_gender === "female"
                            ? (language === "ta" ? "👩 பெண் மட்டும் (ஸ்திரீ)" : "👩 Female Only")
                            : (language === "ta" ? "👨 ஆண் மட்டும்" : "👨 Male Only")}
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded font-medium bg-slate-100 text-slate-700 border border-slate-200">
                          {language === "ta" ? "👥 பொதுவானது" : "👥 Both"}
                        </span>
                      )}
                    </div>

                    {/* Rule Title */}
                    <h4 className="text-sm sm:text-base font-bold text-[#183047] flex items-center gap-2">
                      <span>{language === "ta" && rule.name_ta ? rule.name_ta : rule.name_en}</span>
                    </h4>

                    {/* Primary Prediction / Description */}
                    <div className="bg-[#F8FAFC] rounded-lg p-3 border border-[#E2E8F0] space-y-1">
                      <div className="flex items-center gap-1.5 text-[11px] font-bold text-[#153F6B] uppercase tracking-wider">
                        <Sparkles className="w-3.5 h-3.5 text-[#B4872B]" />
                        <span>{language === "ta" ? "பலன் மற்றும் விளக்கம் (Prediction):" : "Prediction Description:"}</span>
                      </div>
                      <p className="text-xs sm:text-sm text-[#183047] font-medium leading-relaxed">
                        {language === "ta" && rule.interpretation_ta
                          ? rule.interpretation_ta
                          : rule.interpretation_en}
                      </p>
                    </div>

                    {/* Astrological Reason Box */}
                    <div className="bg-[#FAF8F2] rounded-lg p-3 border border-[#D8BD80]/50 space-y-1">
                      <div className="flex items-center gap-1.5 text-[11px] font-bold text-[#8C6D23] uppercase tracking-wider">
                        <Compass className="w-3.5 h-3.5 text-[#B4872B]" />
                        <span>{language === "ta" ? "ஜோதிடக் காரணம் & மூல விதிமுறை (Astrological Reason):" : "Astrological Reason & Principle:"}</span>
                      </div>
                      <p className="text-xs text-[#52667E] leading-relaxed">
                        {language === "ta" && rule.astrological_principle_ta
                          ? rule.astrological_principle_ta
                          : rule.astrological_principle_en}
                      </p>
                    </div>
                  </div>

                  {/* Expand / Collapse Chevron */}
                  <div className="pt-1 text-[#8190A6]">
                    {isExpanded ? (
                      <ChevronUp className="w-5 h-5 text-[#183047]" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-[#8190A6]" />
                    )}
                  </div>
                </div>

                {/* Collapsible Details Drawer */}
                {isExpanded && (
                  <div className="p-3.5 sm:p-4 border-t border-[#F2F3F5] bg-white space-y-3.5 text-xs">
                    {/* Exact Chart Evidence */}
                    <div className="space-y-1.5 bg-[#F2F3F5]/60 p-3 rounded-lg border border-[#D9DEE7]">
                      <div className="flex items-center gap-1.5 text-[11px] font-bold text-[#153F6B] uppercase tracking-wider">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                        <span>{language === "ta" ? "ஜாதகத்தில் அமைந்த கிரக சான்றுகள் (Chart Evidence):" : "Exact Chart Evidence Found:"}</span>
                      </div>
                      {rule.chart_evidence.length > 0 ? (
                        <ul className="space-y-1 pl-4 list-disc text-xs text-[#183047] font-mono">
                          {rule.chart_evidence.map((ev, idx) => (
                            <li key={idx} className="font-semibold text-[11px]">
                              {ev}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-[#8190A6] italic text-[11px]">
                          {rule.unevaluable_reason || "No matching chart evidence found for this placement."}
                        </p>
                      )}
                    </div>

                    {/* Source Reference & Limitations */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pt-2 border-t border-[#D9DEE7]/70 text-[11px] text-[#8190A6]">
                      {rule.source_reference && (
                        <div className="flex items-center gap-1.5">
                          <BookOpen className="w-3.5 h-3.5 text-[#B4872B] shrink-0" />
                          <span>
                            <strong className="text-[#52667E]">{language === "ta" ? "நூல் ஆதாரம்:" : "Classical Source:"}</strong>{" "}
                            {rule.source_reference}
                          </span>
                        </div>
                      )}
                      {(rule.limitations_en || rule.limitations_ta) && (
                        <div className="flex items-center gap-1.5 text-[#8C6D23]">
                          <ShieldAlert className="w-3.5 h-3.5 shrink-0" />
                          <span>
                            <strong className="text-[#8C6D23]">{language === "ta" ? "குறிப்பு:" : "Notice:"}</strong>{" "}
                            {language === "ta" && rule.limitations_ta
                              ? rule.limitations_ta
                              : rule.limitations_en}
                          </span>
                        </div>
                      )}
                      {isCustom && (
                        <div className="flex items-center gap-2 ml-auto">
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleToggleCustomRule(rule.rule_id);
                            }}
                            className={`inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded cursor-pointer border ${
                              customRules.find((r) => r.rule_id === rule.rule_id)?.is_enabled !== false
                                ? "bg-emerald-50 text-emerald-700 border-emerald-300 hover:bg-emerald-100"
                                : "bg-gray-100 text-gray-500 border-gray-300 hover:bg-gray-200"
                            }`}
                          >
                            <span>
                              {customRules.find((r) => r.rule_id === rule.rule_id)?.is_enabled !== false
                                ? language === "ta"
                                  ? "இயக்கத்தில் உள்ளது"
                                  : "Enabled"
                                : language === "ta"
                                ? "முடக்கப்பட்டுள்ளது"
                                : "Disabled"}
                            </span>
                          </button>

                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteCustomRule(rule.rule_id);
                            }}
                            className="inline-flex items-center gap-1 text-rose-600 hover:text-rose-800 font-semibold cursor-pointer"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                            <span>{language === "ta" ? "விதியை நீக்கு" : "Delete Rule"}</span>
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* 5. Modal Dialog: Add Condition Manually */}
      {isAddRuleModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto border border-[#D9DEE7] shadow-2xl p-5 sm:p-6 space-y-4">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-[#F2F3F5] pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-[#FAF2DE] text-[#B4872B] flex items-center justify-center">
                  <Plus className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="font-bold text-sm sm:text-base text-[#183047]">
                    {language === "ta" ? "புதிய ஜோதிட விதியைச் சேர்க்கவும்" : "Add New Astrological Condition"}
                  </h4>
                  <p className="text-[11px] text-[#8190A6]">
                    {language === "ta"
                      ? "சுக்கிரன்+ராகு சேர்க்கை, பாவக அதிபதிகள் நிலை போன்ற புதிய விதிகளை நீங்களே உருவாக்கலாம்."
                      : "Define custom conditions (e.g. Venus+Rahu, planet in house, aspects) to evaluate on this chart."}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => {
                  setIsAddRuleModalOpen(false);
                  setTestResultFeedback(null);
                }}
                className="text-[#8190A6] hover:text-[#183047] p-1 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Form */}
            <div className="space-y-4 text-xs">
              {/* Row 1: Rule Name */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-[#183047] block">
                    {language === "ta" ? "விதியின் பெயர் (English)" : "Rule Name (English) *"}
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Venus-Rahu Passion Arousal Yoga"
                    value={newRuleNameEn}
                    onChange={(e) => setNewRuleNameEn(e.target.value)}
                    className="w-full rounded-lg border border-[#D9DEE7] p-2 text-xs text-[#183047] focus:ring-1 focus:ring-[#B4872B]"
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-[#183047] block">
                    {language === "ta" ? "விதியின் பெயர் (தமிழ்)" : "Rule Name (Tamil)"}
                  </label>
                  <input
                    type="text"
                    placeholder="உதா: சுக்கிரன்-ராகு அதீத காம யோகம்"
                    value={newRuleNameTa}
                    onChange={(e) => setNewRuleNameTa(e.target.value)}
                    className="w-full rounded-lg border border-[#D9DEE7] p-2 text-xs text-[#183047] focus:ring-1 focus:ring-[#B4872B]"
                  />
                </div>
              </div>

              {/* Row 2: Category, System, Scope, Severity */}
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-[#183047] block">
                    {language === "ta" ? "பிரிவு (Category)" : "Category"}
                  </label>
                  <select
                    value={newRuleCategory}
                    onChange={(e) => setNewRuleCategory(e.target.value)}
                    className="w-full rounded-lg border border-[#D9DEE7] p-2 text-xs text-[#183047] font-semibold"
                  >
                    <option value="sexuality_intimacy">🔥 Sexual Topics & Intimacy</option>
                    <option value="marriage_prospects">💍 Marriage Prospects</option>
                    <option value="first_marriage">🌸 1st Marriage</option>
                    <option value="second_marriage">🔄 2nd Marriage</option>
                    <option value="job_prospects">💼 Job & Career</option>
                    <option value="lagna_characteristics">👑 Lagna Characters</option>
                    <option value="nakshatra_characteristics">✨ Star Characteristics</option>
                    <option value="wealth_yogas">💰 Money & Wealth</option>
                    <option value="children_prospects">👶 Children & Family</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="font-bold text-[#183047] block">
                    {language === "ta" ? "ஜோதிட முறை (System)" : "Astrology System"}
                  </label>
                  <select
                    value={newRuleSystem}
                    onChange={(e) => setNewRuleSystem(e.target.value as any)}
                    className="w-full rounded-lg border border-[#D9DEE7] p-2 text-xs text-[#183047] font-semibold"
                  >
                    <option value="vedic">Vedic (வேத ஜோதிடம்)</option>
                    <option value="kp">KP System (கிருஷ்ணமூர்த்தி பத்ததி)</option>
                    <option value="combined">Both / Combined (இரு முறைகளும்)</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="font-bold text-[#183047] block">
                    {language === "ta" ? "சக்கரம் (Scope)" : "Chart Scope"}
                  </label>
                  <select
                    value={newRuleScope}
                    onChange={(e) => setNewRuleScope(e.target.value)}
                    className="w-full rounded-lg border border-[#D9DEE7] p-2 text-xs text-[#183047] font-semibold"
                  >
                    <option value="d1">D1 (Rasi Chart)</option>
                    <option value="d9">D9 (Navamsa Chart)</option>
                    <option value="both">Both D1 & D9</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="font-bold text-[#183047] block">
                    {language === "ta" ? "தன்மை (Nature)" : "Severity / Nature"}
                  </label>
                  <select
                    value={newRuleSeverity}
                    onChange={(e) => setNewRuleSeverity(e.target.value)}
                    className="w-full rounded-lg border border-[#D9DEE7] p-2 text-xs text-[#183047] font-semibold"
                  >
                    <option value="favorable">Favorable (சுபம்)</option>
                    <option value="unfavorable">Unfavorable (சவால்)</option>
                    <option value="neutral">Neutral (சமநிலை)</option>
                    <option value="mixed">Mixed (கலப்பு)</option>
                  </select>
                </div>
              </div>

              {/* Row 3: Condition Builder & Logical Operators */}
              <div className="space-y-3 bg-[#F8FAFC] p-3.5 rounded-xl border border-[#E2E8F0]">
                {/* Logical Operator Header */}
                <div className="flex items-center justify-between gap-2 pb-2.5 border-b border-[#E2E8F0] flex-wrap">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-xs text-[#183047]">
                      {language === "ta" ? "தர்க்க இயக்கி (Logical Operator):" : "Logical Operator:"}
                    </span>
                    <select
                      value={newLogicalOperator}
                      onChange={(e) => setNewLogicalOperator(e.target.value as any)}
                      className="rounded-lg border border-[#B4872B] px-2 py-1 text-xs font-bold bg-white text-[#B4872B]"
                    >
                      <option value="NONE">Single Condition (ஒரே நிபந்தனை)</option>
                      <option value="AND">AND (மற்றும் — இரு நிபந்தனைகளும் பொருந்த வேண்டும்)</option>
                      <option value="OR">OR (அல்லது — ஏதேனும் ஒன்று பொருந்தினால் போதும்)</option>
                      <option value="NOT">NOT (இல்லை — நிபந்தனை அமையாத போது மட்டுமே)</option>
                    </select>
                  </div>
                  <span className="text-[10px] text-[#8190A6]">
                    {newLogicalOperator === "NONE" && (language === "ta" ? "ஒற்றை நிபந்தனை ஆய்வு" : "Evaluating 1 condition")}
                    {newLogicalOperator === "AND" && (language === "ta" ? "Condition 1 AND Condition 2 இரண்டும் பூர்த்தியாக வேண்டும்" : "Requires both Cond 1 & Cond 2")}
                    {newLogicalOperator === "OR" && (language === "ta" ? "Condition 1 அல்லது Condition 2 ஏதேனும் ஒன்று பூர்த்தியானால் போதும்" : "Matches if Cond 1 OR Cond 2 met")}
                    {newLogicalOperator === "NOT" && (language === "ta" ? "Condition 1 ஜாதகத்தில் அமையாத போது விதி பொருந்தும்" : "Inverts Cond 1 (true when unmet)")}
                  </span>
                </div>

                {/* Condition 1 */}
                <div className="space-y-2 pt-1">
                  <label className="font-bold text-[#183047] block flex items-center justify-between">
                    <span>
                      {newLogicalOperator !== "NONE"
                        ? language === "ta"
                          ? "முதன்மை நிபந்தனை 1 (Condition 1):"
                          : "Primary Condition (Condition 1):"
                        : language === "ta"
                        ? "நிபந்தனை வகை (Condition Logic):"
                        : "Condition Type:"}
                    </span>
                  </label>
                  <select
                    value={newConditionType}
                    onChange={(e) => setNewConditionType(e.target.value)}
                    className="w-full rounded-lg border border-[#D9DEE7] p-2 text-xs text-[#183047] font-bold bg-white"
                  >
                    <option value="planet_conjunction">இரண்டு கிரகங்கள் சேர்க்கை (Planet Conjunction, e.g. Venus + Mars)</option>
                    <option value="planet_house">ஒரு கிரகம் குறிப்பிட்ட பாவத்தில் (Planet in House, e.g. Saturn in 7th)</option>
                    <option value="planet_sign">ஒரு கிரகம் குறிப்பிட்ட ராசியில் (Planet in Sign, e.g. Venus in Aries)</option>
                    <option value="house_lord_placement">பாவாதிபதி அமர்ந்த இடம் (House Lord in House, e.g. 7th Lord in 10th)</option>
                    <option value="planet_aspect">கிரகப் பார்வை (Planet Aspecting House, e.g. Mars aspects 10th)</option>
                    <option value="planet_nakshatra">கிரகம் நின்ற நட்சத்திரம் (Planet in Nakshatra, e.g. Moon in Rohini)</option>
                    <option value="lagna_sign">லக்னம் அமைந்த ராசி (Ascendant Sign, e.g. Taurus, Libra)</option>
                    <option value="dasa_active">தசா-புக்தி அதிபதி நிலை (Active Dasa-Bhukti Lord)</option>
                    <option value="kp_sub_lord">KP பாவ உப அதிபதி (KP Cusp Sub-Lord)</option>
                    <option value="kp_significator">KP பாவ காரகர் (KP Planet Signifies House)</option>
                    <option value="mutual_exchange">பரிவர்த்தனை யோகம் (Mutual Exchange of Lords / Parivartana)</option>
                  </select>

                  {/* Condition 1 Dynamic Parameters */}
                  <div className="pt-1">
                    {newConditionType === "planet_conjunction" && (
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                        <div>
                          <label className="text-[10px] font-bold text-[#8190A6]">Planet 1</label>
                          <select
                            value={condPlanet1}
                            onChange={(e) => setCondPlanet1(e.target.value)}
                            className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                          >
                            {planetOptions.map((p) => (
                              <option key={p} value={p}>{p}</option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="text-[10px] font-bold text-[#8190A6]">Planet 2</label>
                          <select
                            value={condPlanet2}
                            onChange={(e) => setCondPlanet2(e.target.value)}
                            className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                          >
                            {planetOptions.map((p) => (
                              <option key={p} value={p}>{p}</option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="text-[10px] font-bold text-[#8190A6]">Max Orb (Degrees)</label>
                          <input
                            type="number"
                            value={condMaxOrb}
                            onChange={(e) => setCondMaxOrb(Number(e.target.value))}
                            step="0.5"
                            className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                          />
                        </div>
                      </div>
                    )}

                    {newConditionType === "planet_house" && (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        <div>
                          <label className="text-[10px] font-bold text-[#8190A6]">Planet</label>
                          <select
                            value={condPlanet1}
                            onChange={(e) => setCondPlanet1(e.target.value)}
                            className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                          >
                            {planetOptions.map((p) => (
                              <option key={p} value={p}>{p}</option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="text-[10px] font-bold text-[#8190A6]">House (1 - 12)</label>
                          <input
                            type="number"
                            min="1"
                            max="12"
                            value={condHouse}
                            onChange={(e) => setCondHouse(Number(e.target.value))}
                            className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                          />
                        </div>
                      </div>
                    )}

                    {newConditionType === "planet_sign" && (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        <div>
                          <label className="text-[10px] font-bold text-[#8190A6]">Planet</label>
                          <select
                            value={condPlanet1}
                            onChange={(e) => setCondPlanet1(e.target.value)}
                            className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                          >
                            {planetOptions.map((p) => (
                              <option key={p} value={p}>{p}</option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="text-[10px] font-bold text-[#8190A6]">Zodiac Sign</label>
                          <select
                            value={condSign}
                            onChange={(e) => setCondSign(Number(e.target.value))}
                            className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                          >
                            {rashiOptions.map((r) => (
                              <option key={r.num} value={r.num}>{r.num} - {r.name}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                    )}

                    {newConditionType === "house_lord_placement" && (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        <div>
                          <label className="text-[10px] font-bold text-[#8190A6]">Lord of House (1 - 12)</label>
                          <input
                            type="number"
                            min="1"
                            max="12"
                            value={condHouse}
                            onChange={(e) => setCondHouse(Number(e.target.value))}
                            className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                          />
                        </div>
                        <div>
                          <label className="text-[10px] font-bold text-[#8190A6]">Placed in House (1 - 12)</label>
                          <input
                            type="number"
                            min="1"
                            max="12"
                            value={condPlacedInHouse}
                            onChange={(e) => setCondPlacedInHouse(Number(e.target.value))}
                            className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                          />
                        </div>
                      </div>
                    )}

                    {newConditionType === "planet_aspect" && (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        <div>
                          <label className="text-[10px] font-bold text-[#8190A6]">Aspecting Planet</label>
                          <select
                            value={condPlanet1}
                            onChange={(e) => setCondPlanet1(e.target.value)}
                            className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                          >
                            {planetOptions.map((p) => (
                              <option key={p} value={p}>{p}</option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="text-[10px] font-bold text-[#8190A6]">Target House (1 - 12)</label>
                          <input
                            type="number"
                            min="1"
                            max="12"
                            value={condHouse}
                            onChange={(e) => setCondHouse(Number(e.target.value))}
                            className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                          />
                        </div>
                      </div>
                    )}

                    {newConditionType === "planet_nakshatra" && (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        <div>
                          <label className="text-[10px] font-bold text-[#8190A6]">Planet</label>
                          <select
                            value={condPlanet1}
                            onChange={(e) => setCondPlanet1(e.target.value)}
                            className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                          >
                            {planetOptions.map((p) => (
                              <option key={p} value={p}>{p}</option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="text-[10px] font-bold text-[#8190A6]">Nakshatra</label>
                          <select
                            value={condNakshatra}
                            onChange={(e) => setCondNakshatra(e.target.value)}
                            className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                          >
                            {nakshatraOptions.map((n) => (
                              <option key={n} value={n}>{n}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                    )}

                    {newConditionType === "lagna_sign" && (
                      <div>
                        <label className="text-[10px] font-bold text-[#8190A6]">Ascendant (Lagna) Sign</label>
                        <select
                          value={condSign}
                          onChange={(e) => setCondSign(Number(e.target.value))}
                          className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                        >
                          {rashiOptions.map((r) => (
                            <option key={r.num} value={r.num}>{r.num} - {r.name}</option>
                          ))}
                        </select>
                      </div>
                    )}

                    {newConditionType === "dasa_active" && (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        <div>
                          <label className="text-[10px] font-bold text-[#8190A6]">Dasa Level</label>
                          <select
                            value={condDasaLevel}
                            onChange={(e) => setCondDasaLevel(e.target.value)}
                            className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                          >
                            {dasaLevelOptions.map((d) => (
                              <option key={d.id} value={d.id}>{d.label}</option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="text-[10px] font-bold text-[#8190A6]">Ruling Lord</label>
                          <select
                            value={condDasaLord}
                            onChange={(e) => setCondDasaLord(e.target.value)}
                            className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                          >
                            {planetOptions.map((p) => (
                              <option key={p} value={p}>{p}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                    )}

                    {newConditionType === "kp_sub_lord" && (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        <div>
                          <label className="text-[10px] font-bold text-[#8190A6]">KP Cusp (1 - 12)</label>
                          <input
                            type="number"
                            min="1"
                            max="12"
                            value={condCusp}
                            onChange={(e) => setCondCusp(Number(e.target.value))}
                            className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                          />
                        </div>
                        <div>
                          <label className="text-[10px] font-bold text-[#8190A6]">Sub-Lord Planet</label>
                          <select
                            value={condSubLord}
                            onChange={(e) => setCondSubLord(e.target.value)}
                            className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                          >
                            {planetOptions.map((p) => (
                              <option key={p} value={p}>{p}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                    )}

                    {newConditionType === "kp_significator" && (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        <div>
                          <label className="text-[10px] font-bold text-[#8190A6]">Planet</label>
                          <select
                            value={condPlanet1}
                            onChange={(e) => setCondPlanet1(e.target.value)}
                            className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                          >
                            {planetOptions.map((p) => (
                              <option key={p} value={p}>{p}</option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="text-[10px] font-bold text-[#8190A6]">Signified House (1 - 12)</label>
                          <input
                            type="number"
                            min="1"
                            max="12"
                            value={condHouse}
                            onChange={(e) => setCondHouse(Number(e.target.value))}
                            className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                          />
                        </div>
                      </div>
                    )}

                    {newConditionType === "mutual_exchange" && (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        <div>
                          <label className="text-[10px] font-bold text-[#8190A6]">House 1 Lord</label>
                          <input
                            type="number"
                            min="1"
                            max="12"
                            value={condHouse}
                            onChange={(e) => setCondHouse(Number(e.target.value))}
                            className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                          />
                        </div>
                        <div>
                          <label className="text-[10px] font-bold text-[#8190A6]">House 2 Lord (Parivartana)</label>
                          <input
                            type="number"
                            min="1"
                            max="12"
                            value={condPlacedInHouse}
                            onChange={(e) => setCondPlacedInHouse(Number(e.target.value))}
                            className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Condition 2 (Shown when AND or OR is selected) */}
                {(newLogicalOperator === "AND" || newLogicalOperator === "OR") && (
                  <div className="space-y-2 pt-3 border-t border-[#E2E8F0]">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-[#153F6B]">
                      <span className="bg-[#153F6B] text-white px-2 py-0.5 rounded text-[10px]">
                        {newLogicalOperator}
                      </span>
                      <span>
                        {language === "ta" ? "இரண்டாம் நிபந்தனை 2 (Condition 2):" : "Secondary Condition (Condition 2):"}
                      </span>
                    </div>

                    <select
                      value={cond2Type}
                      onChange={(e) => setCond2Type(e.target.value)}
                      className="w-full rounded-lg border border-[#D9DEE7] p-2 text-xs text-[#183047] font-bold bg-white"
                    >
                      <option value="planet_house">ஒரு கிரகம் குறிப்பிட்ட பாவத்தில் (Planet in House, e.g. Mars in 7th)</option>
                      <option value="planet_sign">ஒரு கிரகம் குறிப்பிட்ட ராசியில் (Planet in Sign, e.g. Mars in Taurus)</option>
                      <option value="planet_conjunction">இரண்டு கிரகங்கள் சேர்க்கை (Planet Conjunction, e.g. Saturn + Rahu)</option>
                      <option value="house_lord_placement">பாவாதிபதி அமர்ந்த இடம் (House Lord in House, e.g. 5th Lord in 6th)</option>
                      <option value="planet_aspect">கிரகப் பார்வை (Planet Aspecting House, e.g. Jupiter aspects 7th)</option>
                      <option value="planet_nakshatra">கிரகம் நின்ற நட்சத்திரம் (Planet in Nakshatra)</option>
                      <option value="lagna_sign">லக்னம் அமைந்த ராசி (Ascendant Sign)</option>
                      <option value="dasa_active">தசா-புக்தி அதிபதி நிலை (Active Dasa-Bhukti Lord)</option>
                      <option value="kp_sub_lord">KP பாவ உப அதிபதி (KP Cusp Sub-Lord)</option>
                      <option value="kp_significator">KP பாவ காரகர் (KP Planet Signifies House)</option>
                      <option value="mutual_exchange">பரிவர்த்தனை யோகம் (Mutual Exchange of Lords)</option>
                    </select>

                    {/* Condition 2 Dynamic Parameters */}
                    <div className="pt-1">
                      {cond2Type === "planet_conjunction" && (
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                          <div>
                            <label className="text-[10px] font-bold text-[#8190A6]">Planet 1</label>
                            <select
                              value={cond2Planet1}
                              onChange={(e) => setCond2Planet1(e.target.value)}
                              className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                            >
                              {planetOptions.map((p) => (
                                <option key={p} value={p}>{p}</option>
                              ))}
                            </select>
                          </div>
                          <div>
                            <label className="text-[10px] font-bold text-[#8190A6]">Planet 2</label>
                            <select
                              value={cond2Planet2}
                              onChange={(e) => setCond2Planet2(e.target.value)}
                              className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                            >
                              {planetOptions.map((p) => (
                                <option key={p} value={p}>{p}</option>
                              ))}
                            </select>
                          </div>
                          <div>
                            <label className="text-[10px] font-bold text-[#8190A6]">Max Orb (Deg)</label>
                            <input
                              type="number"
                              value={cond2MaxOrb}
                              onChange={(e) => setCond2MaxOrb(Number(e.target.value))}
                              step="0.5"
                              className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                            />
                          </div>
                        </div>
                      )}

                      {cond2Type === "planet_house" && (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          <div>
                            <label className="text-[10px] font-bold text-[#8190A6]">Planet</label>
                            <select
                              value={cond2Planet1}
                              onChange={(e) => setCond2Planet1(e.target.value)}
                              className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                            >
                              {planetOptions.map((p) => (
                                <option key={p} value={p}>{p}</option>
                              ))}
                            </select>
                          </div>
                          <div>
                            <label className="text-[10px] font-bold text-[#8190A6]">House (1 - 12)</label>
                            <input
                              type="number"
                              min="1"
                              max="12"
                              value={cond2House}
                              onChange={(e) => setCond2House(Number(e.target.value))}
                              className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                            />
                          </div>
                        </div>
                      )}

                      {cond2Type === "planet_sign" && (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          <div>
                            <label className="text-[10px] font-bold text-[#8190A6]">Planet</label>
                            <select
                              value={cond2Planet1}
                              onChange={(e) => setCond2Planet1(e.target.value)}
                              className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                            >
                              {planetOptions.map((p) => (
                                <option key={p} value={p}>{p}</option>
                              ))}
                            </select>
                          </div>
                          <div>
                            <label className="text-[10px] font-bold text-[#8190A6]">Zodiac Sign</label>
                            <select
                              value={cond2Sign}
                              onChange={(e) => setCond2Sign(Number(e.target.value))}
                              className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                            >
                              {rashiOptions.map((r) => (
                                <option key={r.num} value={r.num}>{r.num} - {r.name}</option>
                              ))}
                            </select>
                          </div>
                        </div>
                      )}

                      {cond2Type === "house_lord_placement" && (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          <div>
                            <label className="text-[10px] font-bold text-[#8190A6]">Lord of House (1 - 12)</label>
                            <input
                              type="number"
                              min="1"
                              max="12"
                              value={cond2House}
                              onChange={(e) => setCond2House(Number(e.target.value))}
                              className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                            />
                          </div>
                          <div>
                            <label className="text-[10px] font-bold text-[#8190A6]">Placed in House (1 - 12)</label>
                            <input
                              type="number"
                              min="1"
                              max="12"
                              value={cond2PlacedInHouse}
                              onChange={(e) => setCond2PlacedInHouse(Number(e.target.value))}
                              className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                            />
                          </div>
                        </div>
                      )}

                      {cond2Type === "planet_aspect" && (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          <div>
                            <label className="text-[10px] font-bold text-[#8190A6]">Aspecting Planet</label>
                            <select
                              value={cond2Planet1}
                              onChange={(e) => setCond2Planet1(e.target.value)}
                              className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                            >
                              {planetOptions.map((p) => (
                                <option key={p} value={p}>{p}</option>
                              ))}
                            </select>
                          </div>
                          <div>
                            <label className="text-[10px] font-bold text-[#8190A6]">Target House (1 - 12)</label>
                            <input
                              type="number"
                              min="1"
                              max="12"
                              value={cond2House}
                              onChange={(e) => setCond2House(Number(e.target.value))}
                              className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                            />
                          </div>
                        </div>
                      )}

                      {cond2Type === "planet_nakshatra" && (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          <div>
                            <label className="text-[10px] font-bold text-[#8190A6]">Planet</label>
                            <select
                              value={cond2Planet1}
                              onChange={(e) => setCond2Planet1(e.target.value)}
                              className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                            >
                              {planetOptions.map((p) => (
                                <option key={p} value={p}>{p}</option>
                              ))}
                            </select>
                          </div>
                          <div>
                            <label className="text-[10px] font-bold text-[#8190A6]">Nakshatra</label>
                            <select
                              value={cond2Nakshatra}
                              onChange={(e) => setCond2Nakshatra(e.target.value)}
                              className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                            >
                              {nakshatraOptions.map((n) => (
                                <option key={n} value={n}>{n}</option>
                              ))}
                            </select>
                          </div>
                        </div>
                      )}

                      {cond2Type === "lagna_sign" && (
                        <div>
                          <label className="text-[10px] font-bold text-[#8190A6]">Ascendant (Lagna) Sign</label>
                          <select
                            value={cond2Sign}
                            onChange={(e) => setCond2Sign(Number(e.target.value))}
                            className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                          >
                            {rashiOptions.map((r) => (
                              <option key={r.num} value={r.num}>{r.num} - {r.name}</option>
                            ))}
                          </select>
                        </div>
                      )}

                      {cond2Type === "dasa_active" && (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          <div>
                            <label className="text-[10px] font-bold text-[#8190A6]">Dasa Level</label>
                            <select
                              value={cond2DasaLevel}
                              onChange={(e) => setCond2DasaLevel(e.target.value)}
                              className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                            >
                              {dasaLevelOptions.map((d) => (
                                <option key={d.id} value={d.id}>{d.label}</option>
                              ))}
                            </select>
                          </div>
                          <div>
                            <label className="text-[10px] font-bold text-[#8190A6]">Ruling Lord</label>
                            <select
                              value={cond2DasaLord}
                              onChange={(e) => setCond2DasaLord(e.target.value)}
                              className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                            >
                              {planetOptions.map((p) => (
                                <option key={p} value={p}>{p}</option>
                              ))}
                            </select>
                          </div>
                        </div>
                      )}

                      {cond2Type === "kp_sub_lord" && (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          <div>
                            <label className="text-[10px] font-bold text-[#8190A6]">KP Cusp (1 - 12)</label>
                            <input
                              type="number"
                              min="1"
                              max="12"
                              value={cond2Cusp}
                              onChange={(e) => setCond2Cusp(Number(e.target.value))}
                              className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                            />
                          </div>
                          <div>
                            <label className="text-[10px] font-bold text-[#8190A6]">Sub-Lord Planet</label>
                            <select
                              value={cond2SubLord}
                              onChange={(e) => setCond2SubLord(e.target.value)}
                              className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                            >
                              {planetOptions.map((p) => (
                                <option key={p} value={p}>{p}</option>
                              ))}
                            </select>
                          </div>
                        </div>
                      )}

                      {cond2Type === "kp_significator" && (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          <div>
                            <label className="text-[10px] font-bold text-[#8190A6]">Planet</label>
                            <select
                              value={cond2Planet1}
                              onChange={(e) => setCond2Planet1(e.target.value)}
                              className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                            >
                              {planetOptions.map((p) => (
                                <option key={p} value={p}>{p}</option>
                              ))}
                            </select>
                          </div>
                          <div>
                            <label className="text-[10px] font-bold text-[#8190A6]">Signified House (1 - 12)</label>
                            <input
                              type="number"
                              min="1"
                              max="12"
                              value={cond2House}
                              onChange={(e) => setCond2House(Number(e.target.value))}
                              className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                            />
                          </div>
                        </div>
                      )}

                      {cond2Type === "mutual_exchange" && (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          <div>
                            <label className="text-[10px] font-bold text-[#8190A6]">House 1 Lord</label>
                            <input
                              type="number"
                              min="1"
                              max="12"
                              value={cond2House}
                              onChange={(e) => setCond2House(Number(e.target.value))}
                              className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                            />
                          </div>
                          <div>
                            <label className="text-[10px] font-bold text-[#8190A6]">House 2 Lord</label>
                            <input
                              type="number"
                              min="1"
                              max="12"
                              value={cond2PlacedInHouse}
                              onChange={(e) => setCond2PlacedInHouse(Number(e.target.value))}
                              className="w-full rounded border border-[#D9DEE7] p-1.5 text-xs bg-white"
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* NOT Operator Explanatory Note */}
                {newLogicalOperator === "NOT" && (
                  <div className="bg-amber-50 p-2.5 rounded-lg border border-amber-200 text-[11px] text-amber-800 flex items-center gap-1.5">
                    <AlertCircle className="w-4 h-4 shrink-0 text-amber-600" />
                    <span>
                      {language === "ta"
                        ? "குறிப்பு: மேலே குறிப்பிட்டுள்ள முதன்மை நிபந்தனை 1 ஜாதகத்தில் இல்லாத போது மட்டுமே இந்த விதி பூர்த்தியாகும்."
                        : "Note: Inversion active. This rule evaluates to TRUE only when Primary Condition 1 is NOT met in the chart."}
                    </span>
                  </div>
                )}
              </div>

              {/* Row 4: Descriptions, Principles & References */}
              <div className="space-y-3">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="font-bold text-[#183047] block">
                      {language === "ta" ? "பலன் மற்றும் விளக்கம் (English)" : "Prediction Description (English)"}
                    </label>
                    <textarea
                      rows={2}
                      placeholder="e.g. When Venus conjoins Rahu, it magnifies passionate desires and aesthetic attraction..."
                      value={newInterpretationEn}
                      onChange={(e) => setNewInterpretationEn(e.target.value)}
                      className="w-full rounded-lg border border-[#D9DEE7] p-2 text-xs text-[#183047]"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="font-bold text-[#183047] block">
                      {language === "ta" ? "பலன் மற்றும் விளக்கம் (தமிழ்)" : "Prediction Description (Tamil)"}
                    </label>
                    <textarea
                      rows={2}
                      placeholder="உதா: சுக்கிரன்-ராகு சேர்க்கை தீவிர காமக் கவர்ச்சியையும் காதல் நாட்டத்தையும் தரும்..."
                      value={newInterpretationTa}
                      onChange={(e) => setNewInterpretationTa(e.target.value)}
                      className="w-full rounded-lg border border-[#D9DEE7] p-2 text-xs text-[#183047]"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="font-bold text-[#183047] block">
                      {language === "ta" ? "ஜோதிடக் காரணம் (English Principle)" : "Astrological Principle (English)"}
                    </label>
                    <textarea
                      rows={2}
                      placeholder="e.g. Rahu amplifies the sensory qualities of Shukra, encouraging boundary-pushing romantic expression..."
                      value={newPrincipleEn}
                      onChange={(e) => setNewPrincipleEn(e.target.value)}
                      className="w-full rounded-lg border border-[#D9DEE7] p-2 text-xs text-[#183047]"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="font-bold text-[#183047] block">
                      {language === "ta" ? "ஜோதிடக் காரணம் (தமிழ் விளக்கம்)" : "Astrological Principle (Tamil)"}
                    </label>
                    <textarea
                      rows={2}
                      placeholder="உதா: சுக்கிரனின் காரகத்துவங்களான காமம், இன்பங்களை ராகு பலமடங்கு பெருக்குகிறார்..."
                      value={newPrincipleTa}
                      onChange={(e) => setNewPrincipleTa(e.target.value)}
                      className="w-full rounded-lg border border-[#D9DEE7] p-2 text-xs text-[#183047]"
                    />
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="font-bold text-[#183047] block">
                    {language === "ta" ? "நூல் மேற்கோள் (Classical Source / Author)" : "Classical Source Reference"}
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Jataka Tatva, Brihat Jataka, BPHS, KP Reader"
                    value={newSourceRef}
                    onChange={(e) => setNewSourceRef(e.target.value)}
                    className="w-full rounded-lg border border-[#D9DEE7] p-2 text-xs text-[#183047]"
                  />
                </div>
              </div>

              {/* Live Test Feedback Banner */}
              {testResultFeedback && (
                <div
                  className={`p-3 rounded-lg border text-xs font-semibold flex items-start gap-2 ${
                    testResultFeedback.matched
                      ? "bg-emerald-50 text-emerald-800 border-emerald-300"
                      : "bg-amber-50 text-amber-800 border-amber-300"
                  }`}
                >
                  {testResultFeedback.matched ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                  )}
                  <span>{testResultFeedback.message}</span>
                </div>
              )}

              {/* Modal Action Buttons */}
              <div className="flex items-center justify-between gap-2 pt-3 border-t border-[#F2F3F5] flex-wrap">
                <button
                  type="button"
                  onClick={handleTestProposedCondition}
                  disabled={isTestingNewRule}
                  className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-[#F2F3F5] hover:bg-[#E2E8F0] text-[#153F6B] font-bold text-xs border border-[#D9DEE7] cursor-pointer"
                >
                  <Play className={`w-3.5 h-3.5 ${isTestingNewRule ? "animate-spin" : ""}`} />
                  <span>{language === "ta" ? "இந்த ஜாதகத்தில் சோதித்துப் பார்" : "Test on Open Chart"}</span>
                </button>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      setIsAddRuleModalOpen(false);
                      setTestResultFeedback(null);
                    }}
                    className="px-3 py-2 rounded-lg text-xs font-semibold text-[#8190A6] hover:text-[#183047]"
                  >
                    {language === "ta" ? "ரத்து" : "Cancel"}
                  </button>

                  <button
                    type="button"
                    onClick={handleSaveCustomCondition}
                    className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-[#B4872B] hover:bg-[#8C6D23] text-white font-bold text-xs shadow-2xs cursor-pointer"
                  >
                    <Check className="w-4 h-4" />
                    <span>{language === "ta" ? "விதியைச் சேமி" : "Save Condition"}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 6. Modal Dialog: Manage All Custom Rules */}
      {isManageCustomModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[85vh] overflow-y-auto border border-[#D9DEE7] shadow-2xl p-5 sm:p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-[#F2F3F5] pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-[#FAF2DE] text-[#B4872B] flex items-center justify-center">
                  <Filter className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="font-bold text-sm sm:text-base text-[#183047]">
                    {language === "ta" ? "தனிப்பயன் விதிகள் மேலாண்மை" : "Manage Custom Rules"}
                  </h4>
                  <p className="text-[11px] text-[#8190A6]">
                    {language === "ta"
                      ? "நீங்கள் உருவாக்கிய விதிகளை இயக்கலாம், முடக்கலாம் அல்லது நீக்கலாம்."
                      : "Enable, disable, or delete custom astrological rules stored in your profile."}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setIsManageCustomModalOpen(false)}
                className="text-[#8190A6] hover:text-[#183047] p-1 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3">
              {customRules.length === 0 ? (
                <div className="text-center py-8 text-xs text-[#8190A6]">
                  {language === "ta"
                    ? "தற்போது தனிப்பயன் விதிகள் ஏதுமில்லை. '+ புதிய விதியைச் சேர்' பட்டனை அழுத்தவும்."
                    : "No custom rules created yet. Click '+ Add Condition' to build one."}
                </div>
              ) : (
                <div className="space-y-2">
                  {customRules.map((cr) => {
                    const isEnabled = cr.is_enabled !== false;
                    return (
                      <div
                        key={cr.rule_id}
                        className={`p-3 rounded-xl border flex items-center justify-between gap-3 transition-colors ${
                          isEnabled
                            ? "bg-[#F8FAFC] border-[#E2E8F0]"
                            : "bg-gray-50 border-gray-200 opacity-60"
                        }`}
                      >
                        <div className="space-y-0.5">
                          <div className="font-bold text-xs text-[#183047]">
                            {language === "ta" && cr.name_ta ? cr.name_ta : cr.name_en}
                          </div>
                          <div className="flex items-center gap-2 text-[10px] text-[#8190A6]">
                            <span className="uppercase font-semibold tracking-wider text-[#B4872B]">
                              {cr.astrology_system || "vedic"}
                            </span>
                            <span>•</span>
                            <span className="uppercase font-semibold text-[#153F6B]">
                              {cr.chart_scope || "d1"}
                            </span>
                            <span>•</span>
                            <span>{cr.category_slug}</span>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 shrink-0">
                          <button
                            type="button"
                            onClick={() => handleToggleCustomRule(cr.rule_id)}
                            className={`px-2.5 py-1 rounded text-xs font-bold border transition-colors cursor-pointer ${
                              isEnabled
                                ? "bg-emerald-50 text-emerald-700 border-emerald-300 hover:bg-emerald-100"
                                : "bg-gray-200 text-gray-600 border-gray-300 hover:bg-gray-300"
                            }`}
                          >
                            {isEnabled
                              ? language === "ta"
                                ? "இயக்கத்தில் உள்ளது"
                                : "Enabled"
                              : language === "ta"
                              ? "முடக்கப்பட்டுள்ளது"
                              : "Disabled"}
                          </button>

                          <button
                            type="button"
                            onClick={() => handleDeleteCustomRule(cr.rule_id)}
                            className="p-1.5 rounded text-rose-600 hover:text-rose-800 hover:bg-rose-50 transition-colors cursor-pointer"
                            title={language === "ta" ? "விதியை நீக்கு" : "Delete"}
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            <div className="flex justify-end pt-3 border-t border-[#F2F3F5]">
              <button
                type="button"
                onClick={() => setIsManageCustomModalOpen(false)}
                className="px-4 py-2 rounded-lg bg-[#153F6B] hover:bg-[#0E2845] text-white font-bold text-xs cursor-pointer"
              >
                {language === "ta" ? "முடிந்தது" : "Done"}
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
